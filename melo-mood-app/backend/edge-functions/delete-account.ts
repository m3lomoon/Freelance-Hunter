/* Supabase Edge Function · delete-account — an account made in the app
   can be deleted in the app.
   POST {confirm:"DELETE", storeAck?:true}  → {ok:true}
   Order matters: nothing is deleted while the card is still being billed.
     1. an active ECPay recurring order is cancelled first; if ECPay does not confirm, we stop (502)
     2. an active App Store / Google Play plan cannot be cancelled from here; the user must say they
        know (storeAck) before the account goes, otherwise 409 store_active
     3. the voice clone is deleted at ElevenLabs together with every clip made in it
     4. the auth user is deleted; subscriptions, checkouts, voice_clones and usage_monthly cascade
   payment_events keeps ECPay's raw callbacks (order number, amount, time) for bookkeeping; they carry no email.
   secrets: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ELEVENLABS_API_KEY (if a clone exists), ECPAY_* (if ECPay) */
import { admin, caller, cors, json } from "./_shared/tier.ts";
import { forget } from "./_shared/eleven.ts";
import { periodAction } from "./_shared/ecpay.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method" }, 405);
  const user = await caller(req);
  if (!user) return json({ error: "login_required" }, 401);
  const b = await req.json().catch(() => ({}));
  if (b.confirm !== "DELETE") return json({ error: "confirm_required" }, 400);

  const { data: sub } = await admin.from("subscriptions").select("*").eq("user_id", user.id).maybeSingle();
  const live = !!sub && sub.status !== "canceled" && (!sub.current_period_end || new Date(sub.current_period_end).getTime() > Date.now());

  if (sub && sub.source === "ecpay" && sub.status === "active" && sub.merchant_trade_no) {
    const r = await periodAction(sub.merchant_trade_no, "Cancel");
    if (!r.ok) return json({ error: "ecpay", message: r.rtnMsg ?? "綠界沒有回應，請稍後再試" }, 502);
    // recorded at once: if a later step fails, a retry must not ask ECPay to cancel the same order twice
    const now = new Date().toISOString();
    await admin.from("subscriptions").update({ status: "canceled", canceled_at: now, updated_at: now }).eq("user_id", user.id);
  } else if (live && sub!.source !== "ecpay" && b.storeAck !== true) {
    return json({ error: "store_active", source: sub!.source, until: sub!.current_period_end }, 409);
  }

  const { data: clone } = await admin.from("voice_clones").select("voice_id").eq("user_id", user.id).maybeSingle();
  if (clone) {
    const key = Deno.env.get("ELEVENLABS_API_KEY") ?? "";
    if (!key) return json({ error: "not_configured" }, 503);   // never orphan a voice we cannot delete
    await forget(clone.voice_id, key);
  }

  const { error } = await admin.auth.admin.deleteUser(user.id);
  if (error) return json({ error: "delete_failed" }, 500);
  return json({ ok: true });
});
