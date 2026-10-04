"use client";

import { ScissorsIcon, LayersIcon, WaveformIcon } from "./icons";

// Mock clip data — width % across the track
const VIDEO_CLIPS = [
  { id: "v1", label: "Intro", start: 0, width: 22, tone: "from-ink-500 to-ink-700" },
  { id: "v2", label: "Runway A", start: 23, width: 30, tone: "from-zinc-600 to-ink-600" },
  { id: "v3", label: "B-Roll", start: 54, width: 18, tone: "from-ink-600 to-ink-800" },
  { id: "v4", label: "Outro", start: 73, width: 25, tone: "from-zinc-700 to-ink-700" },
];

const AUDIO_CLIPS = [
  { id: "a1", start: 4, width: 44 },
  { id: "a2", start: 50, width: 46 },
];

const TICKS = Array.from({ length: 13 });

export default function Timeline() {
  return (
    <div className="flex h-56 flex-col border-t border-ink-700 bg-ink-900">
      {/* Toolbar */}
      <div className="flex h-11 items-center justify-between border-b border-ink-700 px-4">
        <div className="flex items-center gap-1">
          <ToolButton Icon={ScissorsIcon} label="Split" />
          <ToolButton Icon={LayersIcon} label="Layer" />
          <ToolButton Icon={WaveformIcon} label="Audio" />
        </div>
        <div className="flex items-center gap-4">
          <p className="label">Timeline</p>
          <div className="flex items-center gap-2">
            <span className="label normal-case tracking-normal">Zoom</span>
            <div className="h-1 w-24 bg-ink-700">
              <div className="h-full w-1/2 bg-zinc-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Ruler */}
      <div className="relative flex h-6 items-end border-b border-ink-700 px-[120px] pr-4">
        {TICKS.map((_, i) => (
          <div key={i} className="flex flex-1 items-end justify-start">
            <span className="label normal-case tracking-normal text-[9px] text-slate-fog">
              {String(i * 3).padStart(2, "0")}s
            </span>
          </div>
        ))}
      </div>

      {/* Tracks */}
      <div className="relative flex-1 overflow-x-auto">
        {/* Playhead */}
        <div className="pointer-events-none absolute left-[33%] top-0 z-20 h-full w-px bg-white/70 shadow-glow">
          <div className="absolute -left-[5px] top-0 h-2.5 w-2.5 rotate-45 bg-white" />
        </div>

        {/* Video track */}
        <Track label="Video" Icon={LayersIcon}>
          {VIDEO_CLIPS.map((c) => (
            <button
              key={c.id}
              className={`group absolute top-1.5 h-[44px] overflow-hidden border border-ink-600 bg-gradient-to-b ${c.tone} transition-all duration-300 hover:border-white/40 hover:shadow-glow`}
              style={{ left: `${c.start}%`, width: `${c.width}%` }}
            >
              <span className="absolute inset-x-0 top-0 h-px bg-white/10" />
              <span className="absolute left-2 top-1.5 text-[10px] uppercase tracking-wider text-white/80 group-hover:text-white">
                {c.label}
              </span>
              {/* trim handles */}
              <span className="absolute inset-y-0 left-0 w-1 bg-white/0 group-hover:bg-white/40" />
              <span className="absolute inset-y-0 right-0 w-1 bg-white/0 group-hover:bg-white/40" />
            </button>
          ))}
        </Track>

        {/* Audio track */}
        <Track label="Audio" Icon={WaveformIcon}>
          {AUDIO_CLIPS.map((c) => (
            <div
              key={c.id}
              className="group absolute top-1.5 flex h-[40px] items-center gap-[2px] overflow-hidden border border-ink-600 bg-ink-800 px-2 transition-all duration-300 hover:border-white/30 hover:shadow-glow"
              style={{ left: `${c.start}%`, width: `${c.width}%` }}
            >
              {Array.from({ length: 60 }).map((_, i) => (
                <span
                  key={i}
                  className="w-[2px] shrink-0 bg-zinc-500/60 group-hover:bg-zinc-300/70"
                  style={{ height: `${10 + Math.abs(Math.sin(i * 0.7)) * 24}px` }}
                />
              ))}
            </div>
          ))}
        </Track>
      </div>
    </div>
  );
}

function Track({
  label,
  Icon,
  children,
}: {
  label: string;
  Icon: (p: { className?: string }) => JSX.Element;
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex h-[58px] border-b border-ink-800">
      {/* Track header */}
      <div className="sticky left-0 z-10 flex w-[120px] shrink-0 items-center gap-2 border-r border-ink-700 bg-ink-900 px-4">
        <Icon className="h-3.5 w-3.5 text-slate-fog" />
        <span className="label">{label}</span>
      </div>
      {/* Lane */}
      <div className="relative flex-1 bg-[linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] [background-size:8.33%_100%]">
        {children}
      </div>
    </div>
  );
}

function ToolButton({
  Icon,
  label,
}: {
  Icon: (p: { className?: string }) => JSX.Element;
  label: string;
}) {
  return (
    <button
      className="group flex items-center gap-2 px-3 py-1.5 text-slate-mist transition-all duration-300 hover:bg-ink-850 hover:text-white"
      title={label}
    >
      <Icon className="h-3.5 w-3.5" />
      <span className="hidden text-[11px] uppercase tracking-wider lg:inline">
        {label}
      </span>
    </button>
  );
}
