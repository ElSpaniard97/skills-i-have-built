---
name: mission-control-dashboard-variant-rollout
description: Safely roll out a major Mission Control dashboard redesign as an optional view mode (modern/classic) without breaking existing data flow or APIs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mission-control, dashboard, ui-redesign, zustand, rollout]
    project: hermes-mission-control
---

# Mission Control Dashboard Variant Rollout

## When to use
Use this when introducing a large visual/dashboard overhaul in `hermes-mission-control` while preserving current behavior and minimizing risk.

## Core approach
1. **Do not replace the existing dashboard outright.**
2. Add a **persisted view mode toggle** in Zustand (`modern | classic`).
3. Keep **existing data-loading logic** in `src/components/dashboard/dashboard.tsx`.
4. Implement new UI as a **presentation layer** consuming existing `DashboardData`.
5. Gate render with a mode switch and validate with `pnpm typecheck` + `pnpm lint`.

## Implementation steps

### 1) Add persisted view mode in store
- File: `src/store/index.ts`
- Add type:
  - `export type DashboardViewMode = 'modern' | 'classic'`
- Add store fields:
  - `dashboardViewMode: DashboardViewMode`
  - `setDashboardViewMode: (mode: DashboardViewMode) => void`
- Persist to localStorage key:
  - `mc-dashboard-view-mode`

### 2) Create classic dashboard component
- File: `src/components/dashboard/classic/classic-command-bridge.tsx`
- Input: `{ data: DashboardData }`
- Build visual sections (header, left ops, center HUD, right logs/warnings/api, bottom command console).
- Reuse existing `DashboardData` values and derive missing display-only metrics.

### 3) Wire render switch in existing dashboard
- File: `src/components/dashboard/dashboard.tsx`
- Keep existing fetch/poll/state logic untouched.
- Add toggle buttons for `Modern` / `Classic`.
- Render:
  - `dashboardViewMode === 'classic' ? <ClassicCommandBridge data={dashboardData} /> : <WidgetGrid data={dashboardData} />`

### 4) Validate
Run in repo root:
- `pnpm typecheck`
- `pnpm lint`

## Pitfalls
- **Do not duplicate backend fetching** in the new classic component. Use `DashboardData` only.
- `CurrentUser` uses `display_name`, not `name`.
- `patch` tool may report unrelated `tsc` noise; trust explicit project commands (`pnpm typecheck`, `pnpm lint`) for real verification.
- Avoid accidental regressions by keeping mode default to `modern` unless explicitly requested.

## Verification checklist
- Mode toggle appears and persists after refresh.
- Modern dashboard still works unchanged.
- Classic dashboard renders with live Mission Control data.
- Command console buttons route to existing panels/actions.
- Typecheck passes; lint has no new errors.

## Deployment Reference

See `references/deployment-pitfalls.md` for the full deployment and systemd guide, including Node version gotchas and the better-sqlite3 native addon rebuild procedure.
