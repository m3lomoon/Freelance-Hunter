# NOIR — AI Video Studio

An avant-garde, monochrome dark-mode MVP for an AI video generation platform.
Built with **Next.js 14 (App Router)**, **React 18**, **TypeScript**, and **Tailwind CSS**.

## Aesthetic

"Spiritual Baddie" high-end fashion — deep blacks, slate grays, sharp edges,
editorial micro-typography, and subtle white glow on hover. No rounded blobs,
no color clutter. Pure monochrome.

## Layout

```
┌────────────┬──────────────────────────────────┬──────────────┐
│  Sidebar   │  Top bar (project · export)       │  AI Prompt   │
│            ├──────────────────────────────────┤  Panel       │
│  Projects  │                                   │              │
│  Templates │        Video Player (mock)        │  Prompt      │
│  Settings  │                                   │  Model       │
│            ├──────────────────────────────────┤  Ratio       │
│  Recent    │   Timeline (video + audio)        │  Style       │
│            │                                   │  Sliders     │
└────────────┴──────────────────────────────────┴──────────────┘
```

- **Left sidebar** — Projects / Templates / Settings nav + recent projects.
- **Center** — mocked video player with play transport, plus a horizontal
  video/audio timeline editor (draggable-looking clips, waveform, playhead).
- **Right panel** — AI prompt textarea, model/ratio/style selectors, and
  duration/guidance sliders with custom diamond thumbs.

Fully responsive: the right panel collapses into an overlay drawer below `lg`,
and the sidebar condenses to icons below `md`.

## Run

```bash
npm install
npm run dev
# open http://localhost:3000
```

## Structure

```
app/
  layout.tsx        Root layout + Inter font
  page.tsx          Studio shell (assembles all panels)
  globals.css       Tailwind + design tokens (glow, sliders, scrollbars)
components/
  Sidebar.tsx       Left navigation
  VideoPlayer.tsx   Mocked player stage
  Timeline.tsx      Video/audio timeline editor
  PromptPanel.tsx   AI inputs + parameter tweaks
  icons.tsx         Inline stroked SVG icon set
```
