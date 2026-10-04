"use client";

import { useState } from "react";
import {
  ProjectsIcon,
  TemplatesIcon,
  SettingsIcon,
} from "./icons";

const NAV = [
  { id: "projects", label: "Projects", Icon: ProjectsIcon },
  { id: "templates", label: "Templates", Icon: TemplatesIcon },
  { id: "settings", label: "Settings", Icon: SettingsIcon },
];

const RECENT = [
  { name: "Nocturne / Reel 01", meta: "00:42 · 9:16" },
  { name: "Atelier Campaign", meta: "01:18 · 16:9" },
  { name: "Silk & Static", meta: "00:30 · 1:1" },
];

export default function Sidebar() {
  const [active, setActive] = useState("projects");

  return (
    <aside className="flex h-full w-[68px] flex-col border-r border-ink-700 bg-ink-900 md:w-64">
      {/* Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-ink-700 px-4 md:px-6">
        <div className="flex h-7 w-7 items-center justify-center bg-white">
          <span className="text-sm font-bold text-black">N</span>
        </div>
        <div className="hidden md:block">
          <p className="text-sm font-semibold tracking-editorial text-white">
            NOIR
          </p>
          <p className="label -mt-0.5">Video Studio</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 p-2 md:p-4">
        <p className="label mb-2 hidden px-2 md:block">Workspace</p>
        {NAV.map(({ id, label, Icon }) => {
          const isActive = active === id;
          return (
            <button
              key={id}
              onClick={() => setActive(id)}
              className={`group flex items-center gap-3 px-3 py-2.5 text-sm transition-all duration-300
                ${
                  isActive
                    ? "bg-ink-800 text-white shadow-inset"
                    : "text-slate-mist hover:bg-ink-850 hover:text-white"
                }`}
            >
              <Icon
                className={`h-4 w-4 shrink-0 transition-colors ${
                  isActive ? "text-white" : "text-slate-fog group-hover:text-white"
                }`}
              />
              <span className="hidden md:inline">{label}</span>
              {isActive && (
                <span className="ml-auto hidden h-1 w-1 rounded-full bg-white animate-pulseGlow md:block" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Recent projects */}
      <div className="hidden flex-1 overflow-y-auto px-4 py-2 md:block">
        <p className="label mb-3 px-2">Recent</p>
        <ul className="space-y-1">
          {RECENT.map((p) => (
            <li key={p.name}>
              <button className="group w-full px-2 py-2 text-left transition-colors hover:bg-ink-850">
                <p className="truncate text-[13px] text-zinc-300 group-hover:text-white">
                  {p.name}
                </p>
                <p className="label mt-0.5 normal-case tracking-normal text-slate-fog">
                  {p.meta}
                </p>
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Account footer */}
      <div className="mt-auto border-t border-ink-700 p-3 md:p-4">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 shrink-0 bg-gradient-to-br from-ink-500 to-ink-700 ring-1 ring-ink-600" />
          <div className="hidden md:block">
            <p className="text-xs text-zinc-300">studio@noir.ai</p>
            <p className="label normal-case tracking-normal">Pro · 4K</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
