/* Who is calling and what their plan allows — shared by the voice and ai functions.
   The plan is read from `subscriptions` with the service role; nothing the client sends
   can raise it. BETA_TIER (glow|muse) is an opt-in switch for a demo period: every signed-in
   account is treated as at least that tier, still under the same monthly caps. */
import { createClient, type User } from "npm:@supabase/supabase-js@2";

export const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

export type Tier = "free" | "glow" | "muse";
export const RANK: Record<Tier, number> = { free: 0, glow: 1, muse: 2 };

// fair-use caps per calendar month; cache hits never count toward tts_chars
export const CAPS: Record<Tier, { ttsChars: number; aiCalls: number }> = {
  free: { ttsChars: 0, aiCalls: 0 },
  glow: { ttsChars: 60_000, aiCalls: 0 },
  muse: { ttsChars: 150_000, aiCalls: 60 },
};

export const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
export const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "content-type": "application/json" } });

export async function caller(req: Request): Promise<User | null> {
  const jwt = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
  if (!jwt) return null;
  const { data: { user } } = await admin.auth.getUser(jwt);
  return user ?? null;
}

export async function tierOf(userId: string): Promise<Tier> {
  const { data: sub } = await admin.from("subscriptions")
    .select("tier,status,current_period_end").eq("user_id", userId).maybeSingle();
  let tier: Tier = "free";
  if (sub) {
    const inPeriod = !sub.current_period_end || new Date(sub.current_period_end).getTime() > Date.now();
    // canceled and past-due plans keep access until the paid period ends
    if (sub.status === "active" || inPeriod) tier = sub.tier as Tier;
  }
  const beta = (Deno.env.get("BETA_TIER") ?? "") as Tier;
  if (beta in RANK && RANK[beta] > RANK[tier]) tier = beta;
  return tier;
}

export const monthKey = () =>
  new Date(Date.now() + 8 * 3600_000).toISOString().slice(0, 7);   // Asia/Taipei

export async function usage(userId: string) {
  const { data } = await admin.from("usage_monthly").select("tts_chars,ai_calls")
    .eq("user_id", userId).eq("month", monthKey()).maybeSingle();
  return { ttsChars: data?.tts_chars ?? 0, aiCalls: data?.ai_calls ?? 0 };
}

export async function bump(userId: string, chars: number, calls: number) {
  await admin.rpc("bump_usage", { p_user: userId, p_month: monthKey(), p_chars: chars, p_calls: calls });
}
