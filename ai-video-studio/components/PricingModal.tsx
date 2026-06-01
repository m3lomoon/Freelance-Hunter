"use client";

import { PLANS, Plan } from "@/lib/plans";
import { SparkIcon } from "./icons";

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.4}
      className="h-4 w-4">
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}
      className="h-3 w-3 shrink-0 mt-0.5 text-white">
      <path d="M20 6L9 17l-5-5" />
    </svg>
  );
}

export default function PricingModal({
  onClose,
  onSelectPlan,
  currentCredits,
}: {
  onClose: () => void;
  onSelectPlan: (plan: Plan) => void;
  currentCredits: number;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto p-4 py-10">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/85 backdrop-blur-sm"
        onClick={onClose}
      />

      <div className="relative w-full max-w-5xl">
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute right-0 top-0 flex items-center gap-2 border border-ink-700 bg-ink-900 p-2 text-slate-fog transition-all hover:border-zinc-500 hover:text-white"
        >
          <CloseIcon />
        </button>

        {/* Header */}
        <div className="mb-10 text-center">
          <p className="label mb-3 tracking-editorial">點數方案 · TWD</p>
          <h2 className="text-3xl font-semibold tracking-tight text-white">
            選擇適合你的方案
          </h2>
          <p className="mt-2 text-sm text-slate-mist">
            不到一千元，擁有你的專屬 AI 視覺團隊
          </p>
          {currentCredits > 0 && (
            <p className="mt-3 inline-flex items-center gap-2 border border-ink-700 bg-ink-900 px-4 py-1.5 text-xs text-zinc-400">
              <SparkIcon className="h-3 w-3" />
              目前剩餘 <strong className="text-white">{currentCredits.toLocaleString()}</strong> 點
            </p>
          )}
        </div>

        {/* Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          {PLANS.map((plan) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              onSelect={() => onSelectPlan(plan)}
            />
          ))}
        </div>

        {/* Footer notes */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-[11px] text-slate-fog">
          <span>✓ 信用卡 · LINE Pay</span>
          <span>✓ SSL 加密付款</span>
          <span>✓ 企業方案可開統一編號發票</span>
          <span>✓ 7 天退款保障</span>
        </div>
      </div>
    </div>
  );
}

function PlanCard({ plan, onSelect }: { plan: Plan; onSelect: () => void }) {
  return (
    <div
      className={`relative flex flex-col border transition-all duration-300 ${
        plan.highlight
          ? "border-white bg-ink-800 shadow-glow-strong"
          : "border-ink-700 bg-ink-900 hover:border-zinc-500 hover:shadow-glow"
      }`}
    >
      {/* Most popular badge */}
      {plan.badge && (
        <div className="absolute -top-3.5 left-0 right-0 flex justify-center">
          <span className="bg-white px-4 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-black">
            {plan.badge}
          </span>
        </div>
      )}

      <div className="flex flex-1 flex-col p-6 pt-7">
        {/* Name */}
        <div className="mb-5">
          <p className="label mb-1">{plan.nameEn}</p>
          <h3 className="text-xl font-medium text-white">{plan.name}</h3>
        </div>

        {/* Price */}
        <div className="mb-5 border-b border-ink-700 pb-5">
          <div className="flex items-baseline gap-1">
            <span className="text-sm text-slate-fog">NT$</span>
            <span className="text-4xl font-bold tabular-nums text-white">
              {plan.price.toLocaleString()}
            </span>
            {plan.originalPrice && (
              <span className="ml-1 text-sm text-slate-fog line-through">
                {plan.originalPrice.toLocaleString()}
              </span>
            )}
          </div>
          <p className="mt-0.5 text-[12px] text-slate-mist">{plan.period}</p>
        </div>

        {/* Credits highlight */}
        <div
          className={`mb-5 flex items-center gap-2.5 border px-4 py-3 ${
            plan.highlight
              ? "border-white/20 bg-white/5"
              : "border-ink-700 bg-ink-850"
          }`}
        >
          <SparkIcon className="h-4 w-4 shrink-0 text-white animate-pulseGlow" />
          <div>
            <p className="text-sm font-semibold text-white">{plan.creditLabel}</p>
            <p className="text-[10px] text-slate-fog">{plan.validity}</p>
          </div>
        </div>

        {/* Feature list */}
        <ul className="mb-8 flex-1 space-y-2.5">
          {plan.features.map((f) => (
            <li key={f} className="flex items-start gap-2 text-[13px] text-zinc-400">
              <CheckIcon />
              <span>{f}</span>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <button
          onClick={onSelect}
          className={`w-full py-3.5 text-[12px] font-medium uppercase tracking-wider transition-all duration-300 active:scale-[0.98] ${
            plan.highlight
              ? "bg-white text-black hover:shadow-glow-strong"
              : "border border-ink-700 text-zinc-300 hover:border-white hover:text-white hover:shadow-glow"
          }`}
        >
          {plan.cta}
        </button>
      </div>
    </div>
  );
}
