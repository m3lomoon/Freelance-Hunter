"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import VideoPlayer from "@/components/VideoPlayer";
import Timeline from "@/components/Timeline";
import PromptPanel from "@/components/PromptPanel";
import { ChevronIcon } from "@/components/icons";

export default function StudioPage() {
  const [panelOpen, setPanelOpen] = useState(true);

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-ink-950 text-zinc-300">
      {/* Left navigation */}
      <Sidebar />

      {/* Center column */}
      <section className="flex min-w-0 flex-1 flex-col">
        {/* Top bar */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-ink-700 bg-ink-900 px-6">
          <div className="flex items-center gap-3">
            <span className="label">Project</span>
            <ChevronIcon className="h-3 w-3 text-slate-fog" />
            <h1 className="text-sm font-medium tracking-wide text-white">
              Nocturne / Reel 01
            </h1>
            <span className="ml-2 border border-ink-700 px-2 py-0.5 text-[10px] uppercase tracking-wider text-slate-fog">
              Draft
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button className="btn-ghost hidden sm:flex">Share</button>
            <button
              onClick={() => setPanelOpen((o) => !o)}
              className="btn-ghost lg:hidden"
            >
              {panelOpen ? "Hide AI" : "AI Panel"}
            </button>
            <button className="btn-primary">Export</button>
          </div>
        </header>

        {/* Player + timeline stacked; prompt panel sits to the right on large screens */}
        <div className="flex min-h-0 flex-1">
          <div className="flex min-w-0 flex-1 flex-col">
            <VideoPlayer />
            <Timeline />
          </div>

          {/* Right panel — inline on large screens */}
          <div className="hidden lg:block">
            <PromptPanel />
          </div>
        </div>
      </section>

      {/* Right panel — overlay drawer on smaller screens */}
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
    </main>
  );
}
