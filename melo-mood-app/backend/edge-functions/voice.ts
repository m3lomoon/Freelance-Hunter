/* Supabase Edge Function · voice — real voices for Glow and Muse, on our ElevenLabs account.
   POST json {op:"status"}                          → {tier, clone, usage, caps}
   POST json {op:"speak", text, voice, speed}       → {url}  (signed, 1 h)   Glow+: melo|deep, Muse: clone
   POST form {op:"clone", consent:"yes", sample}    → {ok}   Muse: replaces any earlier clone
   POST json {op:"unclone"}                         → {ok}   deletes the clone at ElevenLabs too
   One sentence in one voice at one speed is synthesized once, ever, and shared through `tts_lines`;
   only cache misses count against the monthly cap. The voice sample itself is never stored.
   secrets: ELEVENLABS_API_KEY (+ SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY); optional BETA_TIER */
import { CAPS, RANK, admin, bump, caller, cors, json, tierOf, usage } from "./_shared/tier.ts";
import { ELEVEN, forget } from "./_shared/eleven.ts";

const MODEL = "eleven_multilingual_v2";
const VOICES: Record<string, string> = {
  melo: Deno.env.get("VOICE_MELO") ?? "cVpaMfwbISlOywwtDanV",
  deep: Deno.env.get("VOICE_DEEP") ?? "kbrsaic1zriFXx1pgRYN",
};
const MAX_TEXT = 600;
const MAX_SAMPLE = 10 * 1024 * 1024;

async function sha256(s: string) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method" }, 405);
  const user = await caller(req);
  if (!user) return json({ error: "login_required" }, 401);
  const key = Deno.env.get("ELEVENLABS_API_KEY") ?? "";

  const isForm = (req.headers.get("content-type") ?? "").includes("multipart/form-data");
  const form = isForm ? await req.formData() : null;
  const body = isForm ? {} : await req.json().catch(() => ({}));
  const op = String(form ? form.get("op") : body.op);
  const tier = await tierOf(user.id);

  if (op === "status") {
    const { data: clone } = await admin.from("voice_clones").select("voice_id").eq("user_id", user.id).maybeSingle();
    return json({ tier, clone: !!clone, usage: await usage(user.id), caps: CAPS[tier], configured: !!key });
  }
  if (!key) return json({ error: "not_configured" }, 503);

  if (op === "speak") {
    const text = String(body.text ?? "").trim();
    const speed = Math.min(1.2, Math.max(0.7, Number(body.speed) || 0.9));
    if (!text || text.length > MAX_TEXT) return json({ error: "bad_text" }, 400);
    let voiceId = VOICES[String(body.voice)];
    if (body.voice === "clone") {
      if (RANK[tier] < RANK.muse) return json({ error: "upgrade_required", need: "muse" }, 402);
      const { data: clone } = await admin.from("voice_clones").select("voice_id").eq("user_id", user.id).maybeSingle();
      if (!clone) return json({ error: "no_clone" }, 404);
      voiceId = clone.voice_id;
    } else if (RANK[tier] < RANK.glow) return json({ error: "upgrade_required", need: "glow" }, 402);
    if (!voiceId) return json({ error: "unknown_voice" }, 400);

    const hash = await sha256(`${MODEL}|${speed.toFixed(2)}|${text}`);
    const { data: hit } = await admin.from("tts_lines").select("audio_path").eq("voice_id", voiceId).eq("text_hash", hash).maybeSingle();
    let path = hit?.audio_path as string | undefined;
    if (!path) {
      const used = await usage(user.id);
      if (used.ttsChars + text.length > CAPS[tier].ttsChars) return json({ error: "quota", usage: used, caps: CAPS[tier] }, 429);
      const r = await fetch(`${ELEVEN}/text-to-speech/${voiceId}?output_format=mp3_44100_64`, {
        method: "POST",
        headers: { "xi-api-key": key, "content-type": "application/json" },
        body: JSON.stringify({ text, model_id: MODEL, voice_settings: { stability: 0.6, similarity_boost: 0.8, style: 0.15, speed } }),
      });
      if (!r.ok) return json({ error: "tts_failed", status: r.status }, 502);
      path = `${voiceId}/${hash}.mp3`;
      const up = await admin.storage.from("tts").upload(path, await r.blob(), { contentType: "audio/mpeg", upsert: true });
      if (up.error) return json({ error: "store_failed" }, 500);
      await admin.from("tts_lines").upsert({ voice_id: voiceId, text_hash: hash, audio_path: path, chars: text.length });
      await bump(user.id, text.length, 0);
    }
    const { data: signed } = await admin.storage.from("tts").createSignedUrl(path, 3600);
    if (!signed) return json({ error: "sign_failed" }, 500);
    return json({ url: signed.signedUrl });
  }

  if (op === "clone") {
    if (RANK[tier] < RANK.muse) return json({ error: "upgrade_required", need: "muse" }, 402);
    if (form?.get("consent") !== "yes") return json({ error: "consent_required" }, 400);
    const sample = form?.get("sample");
    if (!(sample instanceof File) || sample.size < 1000 || sample.size > MAX_SAMPLE) return json({ error: "bad_sample" }, 400);
    const { data: old } = await admin.from("voice_clones").select("voice_id").eq("user_id", user.id).maybeSingle();
    const fd = new FormData();
    fd.append("name", `melomood-${user.id.slice(0, 8)}`);
    fd.append("files", sample, sample.name || "sample.webm");
    fd.append("remove_background_noise", "true");
    const r = await fetch(`${ELEVEN}/voices/add`, { method: "POST", headers: { "xi-api-key": key }, body: fd });
    if (!r.ok) return json({ error: "clone_failed", status: r.status }, 502);
    const { voice_id } = await r.json();
    await admin.from("voice_clones").upsert({ user_id: user.id, voice_id, consent_at: new Date().toISOString() });
    // each account keeps one voice: drop the previous clone once the new one is saved
    if (old?.voice_id && old.voice_id !== voice_id) await forget(old.voice_id, key);
    return json({ ok: true });
  }

  if (op === "unclone") {
    const { data: old } = await admin.from("voice_clones").select("voice_id").eq("user_id", user.id).maybeSingle();
    if (old) {
      await forget(old.voice_id, key);
      await admin.from("voice_clones").delete().eq("user_id", user.id);
    }
    return json({ ok: true });
  }

  return json({ error: "unknown_op" }, 400);
});
