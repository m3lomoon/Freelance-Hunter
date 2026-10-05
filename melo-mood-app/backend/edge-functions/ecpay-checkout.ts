/* POST {plan, returnTo} with the user's session → the signed ECPay form the browser submits.
   The price comes from PLANS on the server, never from the request. */
import { createClient } from "npm:@supabase/supabase-js@2";
import { CHECKOUT_URL, PLANS, type PlanKey, checkMacValue, cors, json, merchant, taipeiNow } from "./_shared/ecpay.ts";

const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
// where ECPay's "back to store" button may send people; anything else falls back to the first
const ORIGINS = (Deno.env.get("APP_ORIGINS") ?? "https://m3lomoon.github.io,http://localhost:8080")
  .split(",").map((s) => s.trim()).filter(Boolean);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method" }, 405);
  if (!merchant.id || !merchant.hashKey || !merchant.hashIV) return json({ error: "payments not configured" }, 503);

  const jwt = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
  const { data: { user } } = await admin.auth.getUser(jwt);
  if (!user) return json({ error: "login required" }, 401);

  const body = await req.json().catch(() => ({}));
  const key = body.plan as PlanKey;
  const plan = PLANS[key];
  if (!plan) return json({ error: "unknown plan" }, 400);
  const rt = typeof body.returnTo === "string" ? body.returnTo : "";
  const back = ORIGINS.some((o) => rt === o || rt.startsWith(o + "/")) ? rt : ORIGINS[0];

  // ≤20 alphanumerics, unique per attempt
  const rnd = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
  const tradeNo = ("MM" + Date.now().toString(36) + rnd).toUpperCase().slice(0, 20);
  const { error } = await admin.from("checkouts").insert({ merchant_trade_no: tradeNo, user_id: user.id, plan: key, amount: plan.amount });
  if (error) return json({ error: "could not start checkout" }, 500);

  const notify = `${Deno.env.get("SUPABASE_URL")}/functions/v1/ecpay-notify`;
  const fields: Record<string, string> = {
    MerchantID: merchant.id,
    MerchantTradeNo: tradeNo,
    MerchantTradeDate: taipeiNow(),
    PaymentType: "aio",
    TotalAmount: String(plan.amount),
    TradeDesc: "MeloMood",
    ItemName: plan.name,
    ReturnURL: notify,
    ChoosePayment: "Credit",
    EncryptType: "1",
    PeriodAmount: String(plan.amount),
    PeriodType: plan.periodType,
    Frequency: String(plan.frequency),
    ExecTimes: String(plan.execTimes),
    PeriodReturnURL: notify,
    ClientBackURL: back,
  };
  fields.CheckMacValue = await checkMacValue(fields);
  return json({ action: CHECKOUT_URL, fields });
});
