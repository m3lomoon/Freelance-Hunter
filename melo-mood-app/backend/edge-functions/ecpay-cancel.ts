/* POST with the user's session → stops the ECPay recurring order. Access continues until
   current_period_end; nothing further is charged. */
import { createClient } from "npm:@supabase/supabase-js@2";
import { cors, json, periodAction } from "./_shared/ecpay.ts";

const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method" }, 405);
  const jwt = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
  const { data: { user } } = await admin.auth.getUser(jwt);
  if (!user) return json({ error: "login required" }, 401);

  const { data: sub } = await admin.from("subscriptions").select("*").eq("user_id", user.id).maybeSingle();
  if (!sub || sub.status === "canceled") return json({ ok: true, status: sub?.status ?? "none", until: sub?.current_period_end ?? null });
  // store subscriptions can only be cancelled in the store; Apple and Google require it
  if (sub.source === "apple") return json({ error: "store", message: "請到 iPhone「設定 → Apple ID → 訂閱」取消" }, 409);
  if (sub.source === "google") return json({ error: "store", message: "請到 Google Play「付款和訂閱 → 訂閱」取消" }, 409);

  const r = await periodAction(sub.merchant_trade_no, "Cancel");
  if (!r.ok) return json({ error: "ecpay", message: r.rtnMsg ?? "綠界沒有回應，請稍後再試" }, 502);
  const now = new Date().toISOString();
  await admin.from("subscriptions").update({ status: "canceled", canceled_at: now, updated_at: now }).eq("user_id", user.id);
  return json({ ok: true, status: "canceled", until: sub.current_period_end });
});
