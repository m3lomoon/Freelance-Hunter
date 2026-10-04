"use client";

import { useState } from "react";
import { PlayIcon } from "./icons";

export default function VideoPlayer() {
  const [playing, setPlaying] = useState(false);

  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-6 md:px-10 md:py-8">
      {/* Stage */}
      <div className="group relative aspect-video w-full max-w-4xl overflow-hidden border border-ink-700 bg-ink-900 shadow-glow transition-all duration-500 hover:shadow-glow-strong">
        {/* Grain / vignette */}
        <div className="absolute inset-0 bg-grain [background-size:18px_18px] opacity-60" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_30%,rgba(0,0,0,0.7)_100%)]" />

        {/* Placeholder mock content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-5">
          <button
            onClick={() => setPlaying((p) => !p)}
            className="flex h-16 w-16 items-center justify-center rounded-full border border-white/20 bg-black/40 backdrop-blur-sm transition-all duration-300 hover:border-white/60 hover:bg-black/60 hover:shadow-glow-strong"
            aria-label={playing ? "Pause" : "Play"}
          >
            {playing ? (
              <span className="flex gap-1">
                <span className="h-5 w-1.5 bg-white" />
                <span className="h-5 w-1.5 bg-white" />
              </span>
            ) : (
              <PlayIcon className="h-6 w-6 translate-x-0.5 text-white" />
            )}
          </button>
          <p className="label">
            {playing ? "Rendering Preview" : "Untitled Composition"}
          </p>
        </div>

        {/* Corner registration marks — editorial detail */}
        {["left-3 top-3", "right-3 top-3", "left-3 bottom-3", "right-3 bottom-3"].map(
          (pos) => (
            <span
              key={pos}
              className={`absolute ${pos} h-3 w-3 border-white/15 ${
                pos.includes("left") ? "border-l" : "border-r"
              } ${pos.includes("top") ? "border-t" : "border-b"}`}
            />
          )
        )}

        {/* Resolution badge */}
        <div className="absolute right-3 top-1/2 hidden -translate-y-1/2 rotate-90 md:block">
          <p className="label text-white/30">3840 × 2160</p>
        </div>
      </div>

      {/* Transport bar */}
      <div className="mt-5 flex w-full max-w-4xl items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="h-1.5 w-1.5 rounded-full bg-white animate-pulseGlow" />
          <p className="label">
            {playing ? "Playing" : "Paused"} · 00:00 / 00:42
          </p>
        </div>
        <div className="flex items-center gap-2">
          {["0.5×", "1×", "2×"].map((s, i) => (
            <button
              key={s}
              className={`px-2.5 py-1 text-[11px] tracking-wider transition-all duration-300 ${
                i === 1
                  ? "bg-white text-black"
                  : "text-slate-fog hover:text-white"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
