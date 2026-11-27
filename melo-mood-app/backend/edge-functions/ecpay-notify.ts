/* ECPay server-to-server callbacks, used as both ReturnURL (first authorization) and
   PeriodReturnURL (every renewal). Deployed with JWT verification OFF: ECPay can't send a
   Supabase token, so the CheckMacValue signature is the authentication. Must answer "1|OK". */
import { createClient } from "npm:@supabase/supabase-js@2";
import { ECPAY_ENV, PLANS, type PlanKey, addMonths, merchant, periodAction, verifyMac } from "./_shared/ecpay.ts";

const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const ack = () => new Response("1|OK", { headers: { "Content-Type": "text/plain" } });

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("0|method", { status: 405 });
  const form = await req.formData().catch(() => null);
  if (!form) return new Response("0|bad request", { status: 400 });
  const f: Record<string, string> = {};
  for (const [k, v] of form.entries()) f[k] = String(v);

  const tradeNo = f.MerchantTradeNo ?? null;
  const kind = f.TradeNo ? "first" : "period";          // only the first authorization carries TradeNo
  const amount = Number(f.TradeAmt ?? f.Amount);
  const valid = f.MerchantID === merchant.id && await verifyMac(f);
  const dedupe = valid ? `${tradeNo}:${kind}:${f.Gwsr || f.TradeNo || `${f.ProcessDate}/${f.TotalSuccessTimes}`}:${f.RtnCode}` : null;

  const { error: logErr } = await admin.from("payment_events").insert({
    merchant_trade_no: tradeNo, kind: valid ? kind : "rejected", rtn_code: f.RtnCode ?? null, rtn_msg: f.RtnMsg ?? null,
    amount: Number.isFinite(amount) ? amount : null, raw: f, dedupe,
  });
  if (!valid) return new Response("0|CheckMacValue Error", { status: 400 });
  if (logErr?.code === "23505") return ack();           // a retry of a callback we already processed

  const { data: co } = await admin.from("checkouts").select("user_id, plan, amount").eq("merchant_trade_no", tradeNo).maybeSingle();
  const plan = co && PLANS[co.plan as PlanKey];
  if (!co || !plan) return ack();                       // not one of ours; logged, stop the retries
  if (ECPAY_ENV === "prod" && f.SimulatePaid === "1") return ack();   // back-office "simulate" never grants in prod

  const { data: cur } = await admin.from("subscriptions")
    .select("merchant_trade_no, status, source, current_period_end").eq("user_id", co.user_id).maybeSingle();
  const isCurrent = cur?.merchant_trade_no === tradeNo;
  const now = new Date();

  if (f.RtnCode !== "1") {
    if (kind === "period" && isCurrent) {
      await admin.from("subscriptions").update({ status: "past_due", updated_at: now.toISOString() }).eq("user_id", co.user_id);
    }
    return ack();
  }
  if (amount !== co.amount) return ack();               // paid amount differs from what we priced: never grant
  if (kind === "period" && !isCurrent) return ack();    // renewal of an order the user already replaced; logged

  // a new order replacing another live ECPay order (e.g. Glow → Muse): stop the old one so they aren't billed twice
  if (kind === "first" && cur && !isCurrent && cur.source === "ecpay" && cur.merchant_trade_no && cur.status !== "canceled") {
    await periodAction(cur.merchant_trade_no, "Cancel").catch(() => null);
  }

  const prevEnd = isCurrent && cur?.current_period_end ? new Date(cur.current_period_end) : null;
  const base = prevEnd && prevEnd > now ? prevEnd : now;   // renewals extend from the old end, no drift
  await admin.from("subscriptions").upsert({
    user_id: co.user_id, tier: plan.tier, plan: co.plan, status: "active", source: "ecpay",
    merchant_trade_no: tradeNo, current_period_end: addMonths(base, plan.months).toISOString(),
    canceled_at: null, updated_at: now.toISOString(),
  });
  return ack();
});
