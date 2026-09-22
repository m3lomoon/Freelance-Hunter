/* ECPay 全方位金流 (AIO) helpers — shared by checkout, notify and cancel.
   Credentials come from env; with ECPAY_ENV=stage and no credentials set it falls back to
   ECPay's public test merchant so the whole flow can be exercised with test cards. */

export const ECPAY_ENV = (Deno.env.get("ECPAY_ENV") ?? "stage") as "stage" | "prod";
const TEST = { merchantId: "3002607", hashKey: "pwFHCqoQZGmho4w6", hashIV: "EkRm7iFT261dpevs" };

export const merchant = {
  id: Deno.env.get("ECPAY_MERCHANT_ID") ?? (ECPAY_ENV === "stage" ? TEST.merchantId : ""),
  hashKey: Deno.env.get("ECPAY_HASH_KEY") ?? (ECPAY_ENV === "stage" ? TEST.hashKey : ""),
  hashIV: Deno.env.get("ECPAY_HASH_IV") ?? (ECPAY_ENV === "stage" ? TEST.hashIV : ""),
};

const host = ECPAY_ENV === "prod" ? "https://payment.ecpay.com.tw" : "https://payment-stage.ecpay.com.tw";
export const CHECKOUT_URL = `${host}/Cashier/AioCheckOut/V5`;
export const PERIOD_ACTION_URL = `${host}/Cashier/CreditCardPeriodAction`;

/* ECPay's CheckMacValue: sort keys case-insensitively, wrap in HashKey/HashIV, encode the way
   .NET HttpUtility.UrlEncode does (space → '+', leaves - _ . ! * ( ) alone), lowercase, SHA-256,
   uppercase hex. encodeURIComponent already leaves - _ . ! * ( ) unencoded; it additionally
   leaves ~ and ' which .NET encodes, so those are patched by hand. */
export function dotnetUrlEncode(s: string): string {
  return encodeURIComponent(s).replace(/%20/g, "+").replace(/~/g, "%7e").replace(/'/g, "%27");
}

export async function checkMacValue(params: Record<string, string | number>, hashKey = merchant.hashKey, hashIV = merchant.hashIV): Promise<string> {
  const body = Object.keys(params)
    .filter((k) => k !== "CheckMacValue")
    .sort((a, b) => a.toLowerCase() < b.toLowerCase() ? -1 : a.toLowerCase() > b.toLowerCase() ? 1 : 0)
    .map((k) => `${k}=${params[k]}`)
    .join("&");
  const raw = dotnetUrlEncode(`HashKey=${hashKey}&${body}&HashIV=${hashIV}`).toLowerCase();
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(raw));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
}

/* constant-time compare so a forged callback can't learn the MAC byte by byte */
export function sameMac(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

export async function verifyMac(fields: Record<string, string>): Promise<boolean> {
  const got = (fields.CheckMacValue ?? "").toUpperCase();
  return got.length > 0 && sameMac(got, await checkMacValue(fields));
}

/* yyyy/MM/dd HH:mm:ss in Taiwan time, which is what MerchantTradeDate expects */
export function taipeiNow(d = new Date()): string {
  const t = new Date(d.getTime() + 8 * 3600_000);
  const p = (n: number) => String(n).padStart(2, "0");
  return `${t.getUTCFullYear()}/${p(t.getUTCMonth() + 1)}/${p(t.getUTCDate())} ${p(t.getUTCHours())}:${p(t.getUTCMinutes())}:${p(t.getUTCSeconds())}`;
}

export const PLANS = {
  glow_m: { name: "Melo Mood Glow 月繳", amount: 290, periodType: "M", frequency: 1, execTimes: 99, tier: "glow", months: 1 },
  glow_y: { name: "Melo Mood Glow 年繳", amount: 2490, periodType: "Y", frequency: 1, execTimes: 9, tier: "glow", months: 12 },
  muse_m: { name: "Melo Mood Muse 月繳", amount: 790, periodType: "M", frequency: 1, execTimes: 99, tier: "muse", months: 1 },
} as const;
export type PlanKey = keyof typeof PLANS;

/* recurring-order control (Cancel / ReAuth). ECPay answers in query-string form. */
export async function periodAction(tradeNo: string, action: "Cancel" | "ReAuth") {
  const p: Record<string, string> = {
    MerchantID: merchant.id, MerchantTradeNo: tradeNo, Action: action,
    TimeStamp: String(Math.floor(Date.now() / 1000)),
  };
  p.CheckMacValue = await checkMacValue(p);
  const res = await fetch(PERIOD_ACTION_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(p),
  });
  const raw = await res.text();
  const out = Object.fromEntries(new URLSearchParams(raw));
  return { ok: out.RtnCode === "1", rtnCode: out.RtnCode, rtnMsg: out.RtnMsg, raw };
}

export function addMonths(d: Date, n: number): Date {
  const x = new Date(d);
  x.setUTCMonth(x.getUTCMonth() + n);
  return x;
}

export const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
export const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });
