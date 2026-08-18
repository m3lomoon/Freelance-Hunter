"use client";

import { useState } from "react";
import { SparkIcon } from "./icons";

const MODELS = ["Noir Diffusion v3", "Kinetic XL", "Mono Motion"];
const RATIOS = ["9:16", "1:1", "16:9", "2.39:1"];
const STYLES = ["Editorial", "Cinematic", "Brutalist", "Ethereal", "Noir"];

export default function PromptPanel() {
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState(MODELS[0]);
  const [ratio, setRatio] = useState("9:16");
  const [style, setStyle] = useState("Editorial");
  const [duration, setDuration] = useState(5);
  const [guidance, setGuidance] = useState(7.5);

  return (
    <aside className="flex h-full w-full flex-col border-l border-ink-700 bg-ink-900 lg:w-[340px]">
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b border-ink-700 px-6">
        <div className="flex items-center gap-2">
          <SparkIcon className="h-4 w-4 text-white animate-pulseGlow" />
          <p className="text-sm font-medium tracking-wider text-white">
            Generate
          </p>
        </div>
        <span className="label">AI</span>
      </div>

      <div className="flex-1 space-y-7 overflow-y-auto px-6 py-6">
        {/* Prompt */}
        <Field label="Prompt">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={5}
            placeholder="A lone figure walking through fog-lit marble corridors, silk drapery in slow motion, monochrome, 35mm grain…"
            className="w-full resize-none border border-ink-700 bg-ink-850 p-3 text-[13px] leading-relaxed text-zinc-200 placeholder:text-slate-fog/60 transition-all duration-300 focus:border-zinc-500 focus:shadow-glow focus:outline-none"
          />
          <div className="mt-2 flex flex-wrap gap-1.5">
            {["+ Slow motion", "+ Film grain", "+ Low key"].map((chip) => (
              <button
                key={chip}
                onClick={() => setPrompt((p) => (p ? p + ", " : "") + chip.slice(2))}
                className="border border-ink-700 px-2 py-1 text-[10px] uppercase tracking-wider text-slate-fog transition-all duration-300 hover:border-zinc-500 hover:text-white"
              >
                {chip}
              </button>
            ))}
          </div>
        </Field>

        {/* Model */}
        <Field label="Model">
          <Segmented options={MODELS} value={model} onChange={setModel} stack />
        </Field>

        {/* Aspect ratio */}
        <Field label="Aspect Ratio">
          <div className="grid grid-cols-4 gap-1.5">
            {RATIOS.map((r) => (
              <button
                key={r}
                onClick={() => setRatio(r)}
                className={`border py-2 text-[11px] tracking-wider transition-all duration-300 ${
                  ratio === r
                    ? "border-white bg-white text-black"
                    : "border-ink-700 text-slate-mist hover:border-zinc-500 hover:text-white"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </Field>

        {/* Style */}
        <Field label="Style Preset">
          <div className="flex flex-wrap gap-1.5">
            {STYLES.map((s) => (
              <button
                key={s}
                onClick={() => setStyle(s)}
                className={`border px-3 py-1.5 text-[11px] uppercase tracking-wider transition-all duration-300 ${
                  style === s
                    ? "border-white bg-white text-black"
                    : "border-ink-700 text-slate-mist hover:border-zinc-500 hover:text-white"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </Field>

        {/* Duration slider */}
        <Slider
          label="Duration"
          value={duration}
          min={1}
          max={15}
          step={1}
          unit="s"
          onChange={setDuration}
        />

        {/* Guidance slider */}
        <Slider
          label="Guidance"
          value={guidance}
          min={1}
          max={20}
          step={0.5}
          onChange={setGuidance}
        />
      </div>

      {/* Generate CTA */}
      <div className="border-t border-ink-700 p-5">
        <div className="mb-3 flex items-center justify-between">
          <span className="label">Est. cost</span>
          <span className="text-xs text-zinc-300">
            {(duration * 1.5).toFixed(0)} credits
          </span>
        </div>
        <button className="btn-primary w-full py-3">
          <SparkIcon className="h-4 w-4" />
          Generate Video
        </button>
      </div>
    </aside>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <p className="label mb-2.5">{label}</p>
      {children}
    </div>
  );
}

function Segmented({
  options,
  value,
  onChange,
  stack,
}: {
  options: string[];
  value: string;
  onChange: (v: string) => void;
  stack?: boolean;
}) {
  return (
    <div className={stack ? "flex flex-col gap-1.5" : "flex gap-1.5"}>
      {options.map((o) => (
        <button
          key={o}
          onClick={() => onChange(o)}
          className={`flex items-center justify-between border px-3 py-2 text-[12px] tracking-wide transition-all duration-300 ${
            value === o
              ? "border-zinc-500 bg-ink-800 text-white shadow-inset"
              : "border-ink-700 text-slate-mist hover:border-zinc-600 hover:text-white"
          }`}
        >
          {o}
          {value === o && (
            <span className="h-1.5 w-1.5 rounded-full bg-white animate-pulseGlow" />
          )}
        </button>
      ))}
    </div>
  );
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  unit = "",
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit?: string;
  onChange: (v: number) => void;
}) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div>
      <div className="mb-2.5 flex items-center justify-between">
        <p className="label">{label}</p>
        <span className="text-xs text-zinc-300">
          {value}
          {unit}
        </span>
      </div>
      <div className="relative flex h-4 items-center">
        <div className="absolute h-px w-full bg-ink-600" />
        <div
          className="absolute h-px bg-white"
          style={{ width: `${pct}%` }}
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="slider-thumb absolute h-4 w-full cursor-pointer appearance-none bg-transparent"
          style={{
            // custom thumb via accent fallback
          }}
        />
        <div
          className="pointer-events-none absolute h-3 w-3 -translate-x-1/2 rotate-45 border border-white bg-black shadow-glow"
          style={{ left: `${pct}%` }}
        />
      </div>
    </div>
  );
}
