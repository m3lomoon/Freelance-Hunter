// Supabase Edge Function · generate-script
// POST { goal, minutes, tone, kind: "manifest" | "sleep" }
// Reads the caller's profile + last 5 journal entries, asks Claude for a
// personalised script, stores it in `scripts`, returns { id, lines }.
//
// deploy: supabase functions deploy generate-script --no-verify-jwt=false
// secrets: ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

import Anthropic from "npm:@anthropic-ai/sdk";
import { createClient } from "npm:@supabase/supabase-js@2";

const TONES: Record<string, string> = {
  gentle: "溫柔：像深夜的朋友，慢慢說",
  firm: "堅定：像教練，短、直接、有力",
  baddie: "Baddie：高街潮流 × 5D 意識，自信帶點壞，偶爾夾一句英文",
};
const GOALS: Record<string, string> = {
  wealth: "財富自由（收入、版稅、被動現金流）",
  music: "音樂與舞台（作品、演出、被對的人聽見）",
  love: "愛與關係",
  health: "身體與能量（睡眠、運動、無糖飲食）",
  confidence: "自信與魅力",
  creative: "創作靈感（點子、專案、一人公司）",
};

const SYSTEM = `你是 Melo Mood 的顯化腳本作者。使用者會用「自己複製的聲音」把這段腳本唸給自己聽，所以一律用第一人稱現在式、繁體中文（台灣口語），句子短，適合朗讀。
輸出格式：每行一句，不要編號、不要標題、不要 markdown、不要引號。
結構：
1. 開場呼吸（2 到 3 句，叫使用者的名字）
2. 肯定語（依長度 8 到 28 句，可重複並漸進加強）
3. 一段具體視覺化畫面（以「想像」開頭，2 到 3 句）
4. 收尾（2 句）
睡前版本改為：身體掃描 → 10 到 1 倒數 → 目標暗示 → 「現在，你可以睡了」。
從使用者最近的日記裡挑一到兩個具體細節放進腳本，讓它像只為她寫的。不做醫療宣稱。`;

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });
  const auth = req.headers.get("Authorization") ?? "";
  const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
    global: { headers: { Authorization: auth } },
  });
  const { data: { user } } = await supabase.auth.getUser(auth.replace("Bearer ", ""));
  if (!user) return Response.json({ error: "unauthorized" }, { status: 401 });

  const { goal, minutes = 7, tone = "gentle", kind = "manifest" } = await req.json();

  const [{ data: profile }, { data: entries }] = await Promise.all([
    supabase.from("profiles").select("name, goals, tone, plan").eq("id", user.id).single(),
    supabase.from("journal_entries").select("entry_date, mood, gratitude, note").eq("user_id", user.id)
      .order("entry_date", { ascending: false }).limit(5),
  ]);
  if (!profile) return Response.json({ error: "no profile" }, { status: 400 });
  if (profile.plan === "free") return Response.json({ error: "upgrade_required" }, { status: 402 });

  const journal = (entries ?? [])
    .map((e) => `${e.entry_date} 心情 ${e.mood}/5 感謝：${e.gratitude.join("、")} 筆記：${e.note}`)
    .join("\n") || "（還沒有日記）";

  const client = new Anthropic();
  const response = await client.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 4000,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
    messages: [{
      role: "user",
      content: `使用者：${profile.name}\n版本：${kind === "sleep" ? "睡前催眠" : "日間顯化"}\n目標：${GOALS[goal] ?? goal}\n語氣：${TONES[tone] ?? tone}\n長度：約 ${minutes} 分鐘朗讀量\n最近的日記：\n${journal}`,
    }],
  });

  if (response.stop_reason === "refusal") {
    return Response.json({ error: "refused", detail: response.stop_details?.explanation }, { status: 422 });
  }
  const text = response.content.filter((b) => b.type === "text").map((b) => b.text).join("\n");
  const lines = text.split(/\n+/).map((s) => s.trim()).filter(Boolean).map((t, i, a) => ({
    t,
    kind: i === 0 || i === a.length - 1 ? "open" : /^想像/.test(t) ? "vision" : "aff",
    pause: kind === "sleep" ? 3000 : 1300,
  }));

  const { data: script } = await supabase.from("scripts")
    .insert({ user_id: user.id, kind, goal, tone, minutes, lines, source: "claude" })
    .select("id").single();

  return Response.json({ id: script?.id, lines });
});
