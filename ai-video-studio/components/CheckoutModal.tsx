"use client";

import { useState } from "react";
import { Plan } from "@/lib/plans";

type PayMethod = "credit" | "linepay";

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}
      className="h-3 w-3">
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );
}

function ChevronLeftIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}
      className="h-3.5 w-3.5">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  );
}

export default function CheckoutModal({
  plan,
  onClose,
  onBack,
  onSuccess,
}: {
  plan: Plan;
  onClose: () => void;
  onBack: () => void;
  onSuccess: (credits: number) => void;
}) {
  const [method, setMethod] = useState<PayMethod>("credit");
  const [taxId, setTaxId] = useState("");
  const [cardName, setCardName] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [expiry, setExpiry] = useState("");
  const [cvv, setCvv] = useState("");
  const [processing, setProcessing] = useState(false);
  const [taxIdError, setTaxIdError] = useState("");

  const formatCardNumber = (v: string) =>
    v.replace(/\D/g, "").slice(0, 16).replace(/(.{4})/g, "$1 ").trim();

  const formatExpiry = (v: string) => {
    const d = v.replace(/\D/g, "").slice(0, 4);
    return d.length >= 2 ? d.slice(0, 2) + "/" + d.slice(2) : d;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (plan.requiresTaxId && taxId.length !== 8) {
      setTaxIdError("統一編號須為 8 碼數字");
      return;
    }

    setTaxIdError("");
    setProcessing(true);
    setTimeout(() => {
      setProcessing(false);
      onSuccess(plan.credits);
    }, 2200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/85 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-md border border-ink-700 bg-ink-900 shadow-glow">
        {/* Header — plan summary */}
        <div className="flex items-start justify-between border-b border-ink-700 p-6">
          <div>
            <p className="label mb-1">確認訂單</p>
            <p className="text-base font-medium text-white">{plan.name}</p>
            <p className="mt-1 text-[12px] text-slate-mist">
              {plan.creditLabel} · {plan.validity}
            </p>
          </div>
          <div className="text-right">
            <p className="label mb-1">應付金額</p>
            <p className="text-2xl font-bold tabular-nums text-white">
              NT${plan.price.toLocaleString()}
            </p>
            <p className="text-[11px] text-slate-fog">{plan.period}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 p-6">
          {/* Payment method selector */}
          <div>
            <p className="label mb-3">付款方式</p>
            <div className="grid grid-cols-2 gap-2">
              <MethodBtn
                active={method === "credit"}
                onClick={() => setMethod("credit")}
                label="信用卡"
                sub="Visa · Mastercard · JCB"
              />
              <MethodBtn
                active={method === "linepay"}
                onClick={() => setMethod("linepay")}
                label="LINE Pay"
                sub="綁定 LINE 帳號付款"
                iconNode={<LinepayBadge size="sm" />}
              />
            </div>
          </div>

          {/* Credit card form */}
          {method === "credit" && (
            <div className="space-y-3">
              <Field
                label="持卡人姓名"
                placeholder="姓名同信用卡正面"
                value={cardName}
                onChange={setCardName}
                required
              />
              <Field
                label="卡號"
                placeholder="0000 0000 0000 0000"
                value={cardNumber}
                onChange={(v) => setCardNumber(formatCardNumber(v))}
                maxLength={19}
                inputMode="numeric"
                required
              />
              <div className="grid grid-cols-2 gap-3">
                <Field
                  label="有效期限"
                  placeholder="MM / YY"
                  value={expiry}
                  onChange={(v) => setExpiry(formatExpiry(v))}
                  maxLength={5}
                  inputMode="numeric"
                  required
                />
                <Field
                  label="安全碼 CVV"
                  placeholder="···"
                  value={cvv}
                  onChange={(v) => setCvv(v.replace(/\D/g, "").slice(0, 4))}
                  maxLength={4}
                  type="password"
                  inputMode="numeric"
                  required
                />
              </div>
            </div>
          )}

          {/* LINE Pay placeholder */}
          {method === "linepay" && (
            <div className="flex flex-col items-center gap-5 border border-ink-700 bg-ink-850 px-6 py-8">
              <LinepayBadge size="lg" />
              <p className="text-center text-[13px] leading-relaxed text-zinc-400">
                點擊確認後將跳轉至 LINE Pay 安全付款頁面完成結帳
              </p>
            </div>
          )}

          {/* 統一編號 — enterprise only */}
          {plan.requiresTaxId && (
            <div>
              <Field
                label="統一編號（公司行號必填）"
                placeholder="例：12345678"
                value={taxId}
                onChange={(v) => {
                  setTaxId(v.replace(/\D/g, "").slice(0, 8));
                  setTaxIdError("");
                }}
                maxLength={8}
                inputMode="numeric"
                required
                error={taxIdError}
              />
              <p className="mt-1.5 text-[11px] text-slate-fog">
                發票將開立三聯式電子發票，3 個工作天內寄送至登記信箱
              </p>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={processing}
            className="relative w-full overflow-hidden bg-white py-4 text-[13px] font-semibold uppercase tracking-wider text-black transition-all duration-300 hover:shadow-glow-strong active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {processing && (
              <span className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-black/10 to-transparent" />
            )}
            {processing
              ? "處理中，請稍候…"
              : method === "linepay"
              ? "前往 LINE Pay 付款"
              : `確認付款 NT$${plan.price.toLocaleString()}`}
          </button>

          {/* Footer links */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={onBack}
              className="flex items-center gap-1 text-[12px] text-slate-fog transition-colors hover:text-white"
            >
              <ChevronLeftIcon />
              返回方案選擇
            </button>
            <span className="flex items-center gap-1.5 text-[11px] text-slate-fog">
              <LockIcon />
              SSL 256-bit 加密
            </span>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function MethodBtn({
  active, onClick, label, sub, iconNode,
}: {
  active: boolean; onClick: () => void; label: string; sub: string;
  iconNode?: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-start gap-3 border p-3.5 text-left transition-all duration-300 ${
        active
          ? "border-white bg-ink-800 shadow-glow"
          : "border-ink-700 bg-ink-900 hover:border-zinc-600"
      }`}
    >
      {/* Radio dot */}
      <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center border border-ink-600">
        {active && <span className="h-2 w-2 bg-white" />}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <span className="text-[13px] font-medium text-white">{label}</span>
          {iconNode}
        </div>
        <span className="text-[10px] text-slate-fog">{sub}</span>
      </div>
    </button>
  );
}

function Field({
  label, placeholder, value, onChange, maxLength, type, inputMode, required, error,
}: {
  label: string; placeholder: string; value: string;
  onChange: (v: string) => void; maxLength?: number; type?: string;
  inputMode?: React.InputHTMLAttributes<HTMLInputElement>["inputMode"];
  required?: boolean; error?: string;
}) {
  return (
    <div>
      <label className="label mb-1.5 block">{label}</label>
      <input
        type={type ?? "text"}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={maxLength}
        inputMode={inputMode}
        required={required}
        className={`w-full border bg-ink-850 px-3 py-2.5 text-[13px] text-zinc-200 placeholder:text-slate-fog/50 transition-all duration-300 focus:outline-none focus:shadow-glow ${
          error ? "border-red-700 focus:border-red-500" : "border-ink-700 focus:border-zinc-500"
        }`}
      />
      {error && <p className="mt-1 text-[11px] text-red-400">{error}</p>}
    </div>
  );
}

function LinepayBadge({ size }: { size: "sm" | "lg" }) {
  return (
    <div
      className={`flex shrink-0 items-center justify-center bg-[#00B900] font-bold text-white ${
        size === "lg" ? "h-12 w-28 text-[15px]" : "h-5 w-14 text-[9px]"
      }`}
    >
      LINE Pay
    </div>
  );
}
