# Aveyo Dashboard — Project Instructions

## What This Is
A mobile-first PWA command center for Quentin Spencer, a PM at Aveyo Solar. Single HTML file (`aveyo-dashboard.html`) with embedded fonts, CSS, and vanilla JS. No frameworks, no build step. Deployed via GitHub Pages.

## Architecture
- **Single file:** `aveyo-dashboard.html` (~450KB) — everything is here
- **Backend:** Flask on VPS at 187.124.240.101 (aveyo.aiwhileyousleeping.com) — handles AI calls, Google Drive, Podio writes
- **Data source:** Podio API (OAuth2) — 6 apps: Projects (29839792), SOW (29839685), Support Tickets (29840119), Pre-Install (29839773), Change Orders (29841104), Roof Work (29839741)
- **Service worker:** `sw.js` for offline caching

## Design System — Battlefront 2015 (LOCKED)
- Black backgrounds (#000 / #0a0a0a)
- PPTelegraf font — bold, industrial, all-caps labels, wide letter-spacing
- #ADD8E6 accent (light blue) — active states, positive indicators
- Zero border-radius — sharp edges everywhere
- NO emojis — ever
- 1px horizontal rules for separators
- Three-color status: #ADD8E6 (good), #FFFFFF (neutral), #E88B8B (urgent)

## Coding Conventions
- Vanilla JS only — no React, no Vue, no libraries
- DOM manipulation and string concatenation for rendering
- Lazy load tab data on first tap, cache per session
- All tab queue functions follow pattern: `loadXxx()` fetches, `renderXxx()` renders
- Filter chips at top of each queue tab
- Age timers on queue items (blue < threshold, white mid, red overdue)

## Key Documents
- `MISSION.md` — full product spec, tab details, data architecture, success metrics
- `DESIGN-SPEC.md` — UX patterns, layout specs, tab-by-tab implementation details

## Rules
- Never remove working features — add new tabs alongside existing ones
- Build each tab one at a time, perfect it before moving on
- Keep the single-file architecture — do not split into multiple files
- Preserve existing Home, Projects, Action, and Knowledge tabs
- Every queue tab needs: filter chips, sorted list, status badges, age timers, tap-to-detail

## Current Progress
See `PROGRESS.md` in the memory directory for live status of what's built and what's next.
