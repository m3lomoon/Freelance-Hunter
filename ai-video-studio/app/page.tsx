"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import VideoPlayer from "@/components/VideoPlayer";
import Timeline from "@/components/Timeline";
import PromptPanel from "@/components/PromptPanel";
import PricingModal from "@/components/PricingModal";
import CheckoutModal from "@/components/CheckoutModal";
import SuccessToast from "@/components/SuccessToast";
import { ChevronIcon, SparkIcon } from "@/components/icons";
import { Plan } from "@/lib/plans";

type Modal = "none" | "pricing" | "checkout";

export default function StudioPage() {
  const [panelOpen, setPanelOpen] = useState(true);
  const [modal, setModal] = useState<Modal>("none");
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [credits, setCredits] = useState(120);          // mock starting balance
  const [showSuccess, setShowSuccess] = useState(false);
  const [lastPurchasedCredits, setLastPurchasedCredits] = useState(0);

  const openPricing = () => setModal("pricing");

  const handleSelectPlan = (plan: Plan) => {
    setSelectedPlan(plan);
    setModal("checkout");
  };

  const handlePaymentSuccess = (earned: number) => {
    setCredits((c) => c + earned);
    setLastPurchasedCredits(earned);
    setModal("none");
    setShowSuccess(true);
  };

  const creditsLow = credits < 200;

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-ink-950 text-zinc-300">
      {/* ── Left navigation ─────────────────────────────────── */}
      <Sidebar />

      {/* ── Center column ───────────────────────────────────── */}
      <section className="flex min-w-0 flex-1 flex-col">

        {/* Top bar */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-ink-700 bg-ink-900 px-6">
          {/* Breadcrumb */}
          <div className="flex items-center gap-3">
            <span className="label">專案</span>
            <ChevronIcon className="h-3 w-3 text-slate-fog" />
            <h1 className="text-sm font-medium tracking-wide text-white">
              Nocturne / Reel 01
            </h1>
            <span className="ml-2 border border-ink-700 px-2 py-0.5 text-[10px] uppercase tracking-wider text-slate-fog">
              草稿
            </span>
          </div>

          {/* Right cluster */}
          <div className="flex items-center gap-3">
            {/* Credits badge */}
            <button
              onClick={openPricing}
              className={`group flex items-center gap-2 border px-3 py-1.5 text-[12px] transition-all duration-300 ${
                creditsLow
                  ? "border-amber-700/60 bg-amber-950/30 text-amber-400 hover:border-amber-500 hover:shadow-glow"
                  : "border-ink-700 bg-ink-850 text-zinc-300 hover:border-zinc-500 hover:text-white hover:shadow-glow"
              }`}
              title="購買點數"
            >
              <SparkIcon
                className={`h-3.5 w-3.5 ${creditsLow ? "animate-pulseGlow text-amber-400" : "text-slate-fog group-hover:text-white"}`}
              />
              <span className="tabular-nums">
                {credits.toLocaleString()}
              </span>
              <span className="text-[10px] text-slate-fog">點</span>
              {creditsLow && (
                <span className="border border-amber-700/60 bg-amber-950/40 px-1.5 py-px text-[9px] uppercase tracking-wider text-amber-400">
                  補充
                </span>
              )}
            </button>

            <button className="hidden items-center gap-2 border border-ink-700 bg-ink-850 px-4 py-2 text-xs uppercase tracking-wider text-zinc-400 transition-all duration-300 hover:border-zinc-500 hover:text-white hover:shadow-glow sm:flex">
              分享
            </button>

            <button
              onClick={() => setPanelOpen((o) => !o)}
              className="flex items-center gap-2 border border-ink-700 bg-ink-850 px-3 py-2 text-xs uppercase tracking-wider text-zinc-400 transition-all hover:border-zinc-500 hover:text-white lg:hidden"
            >
              {panelOpen ? "隱藏 AI" : "AI 面板"}
            </button>

            <button
              onClick={openPricing}
              className="flex items-center justify-center gap-2 bg-white px-4 py-2 text-xs font-medium uppercase tracking-wider text-black transition-all duration-300 hover:shadow-glow-strong active:scale-[0.98]"
            >
              購買點數
            </button>
          </div>
        </header>

        {/* Main content area */}
        <div className="flex min-h-0 flex-1">
          <div className="flex min-w-0 flex-1 flex-col">
            <VideoPlayer />
            <Timeline />
          </div>

          {/* Right prompt panel — desktop */}
          <div className="hidden lg:block">
            <PromptPanel />
          </div>
        </div>
      </section>

      {/* ── Right panel overlay — mobile ──────────────────────── */}
      {panelOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setPanelOpen(false)}
          />
          <div className="absolute right-0 top-0 h-full w-[88%] max-w-sm">
            <PromptPanel />
          </div>
        </div>
      )}

      {/* ── Modals ─────────────────────────────────────────────── */}
      {modal === "pricing" && (
        <PricingModal
          onClose={() => setModal("none")}
          onSelectPlan={handleSelectPlan}
          currentCredits={credits}
        />
      )}

      {modal === "checkout" && selectedPlan && (
        <CheckoutModal
          plan={selectedPlan}
          onClose={() => setModal("none")}
          onBack={() => setModal("pricing")}
          onSuccess={handlePaymentSuccess}
        />
      )}

      {/* ── Success toast ──────────────────────────────────────── */}
      {showSuccess && (
        <SuccessToast
          credits={lastPurchasedCredits}
          onDone={() => setShowSuccess(false)}
        />
      )}
    </main>
  );
}
