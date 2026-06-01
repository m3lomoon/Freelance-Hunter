"use client";

import { useEffect, useState } from "react";

export default function SuccessToast({
  credits,
  onDone,
}: {
  credits: number;
  onDone: () => void;
}) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => {
      setVisible(false);
      setTimeout(onDone, 400);
    }, 4000);
    return () => clearTimeout(t);
  }, [onDone]);

  return (
    <div
      className={`fixed bottom-6 right-6 z-[60] flex items-start gap-4 border border-white/20 bg-ink-800 p-5 shadow-glow-strong transition-all duration-500 ${
        visible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
      }`}
    >
      {/* Animated checkmark */}
      <div className="flex h-10 w-10 shrink-0 items-center justify-center border border-white/20 bg-white">
        <svg viewBox="0 0 24 24" fill="none" stroke="black" strokeWidth={2.5}
          className="h-5 w-5">
          <path d="M20 6L9 17l-5-5" />
        </svg>
      </div>
      <div>
        <p className="text-sm font-semibold text-white">付款成功！</p>
        <p className="mt-0.5 text-[12px] text-zinc-400">
          已新增{" "}
          <strong className="text-white">{credits.toLocaleString()} 點</strong>{" "}
          至你的帳戶
        </p>
        <p className="mt-2 text-[11px] text-slate-fog">
          收據已寄至你的登記信箱
        </p>
      </div>
      <button
        onClick={() => { setVisible(false); setTimeout(onDone, 400); }}
        className="ml-auto text-slate-fog transition-colors hover:text-white"
        aria-label="關閉"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth={1.5} className="h-4 w-4">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
