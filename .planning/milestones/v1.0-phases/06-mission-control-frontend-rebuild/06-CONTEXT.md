---
phase: 6
slug: mission-control-frontend-rebuild
created: 2026-03-08
status: ready
source_prd: /Users/IAn/Downloads/PLAN.md
source_codebase_map:
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/STACK.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/ARCHITECTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/CONCERNS.md
depends_on:
  - phase: 5
    reason: "Phase 5 normalized the backend contracts the frontend must consume."
requirements:
  - UI-01
  - UI-02
---

# Phase 6 Context

## Objective

Rebuild the operator frontend from scratch inside `/Users/IAn/Agent/AI-Enterprise` as a clean mission-control application that consumes the normalized backend created in Phase 5.

## Why This Phase Exists

The source repo has a working React frontend, but it is tightly coupled to legacy route naming, compiled bundle drift, and browser-stored control headers. The clean target needs a deliberately rebuilt UI that preserves operator workflows without inheriting those structural weaknesses.

## Brownfield Source Reference

- Source frontend stack: React 18 + TypeScript + Vite + React Router in `/Users/IAn/Agent/IAn/frontend`
- Source route file: `/Users/IAn/Agent/IAn/frontend/src/App.tsx`
- Source shell layout: `/Users/IAn/Agent/IAn/frontend/src/components/layout/WorkspaceShell.tsx`
- Source backend-served bundle: `/Users/IAn/Agent/IAn/backend/static/ui`
- Brownfield mapping authority: `.planning/codebase/*`

## Clean Target Scope

Build these new frontend artifacts in `/Users/IAn/Agent/AI-Enterprise`:

- `package.json`
- `index.html`
- `tsconfig*.json`
- `vite.config.ts`
- `src/App.tsx`
- `src/main.tsx`
- `src/styles/tokens.css`
- `src/components/shell/*`
- `src/components/shared/*`
- `src/components/floor/*`
- `src/components/programs/*`
- `src/components/orchestration/*`
- `src/components/configs/*`
- `src/components/report/*`
- `src/components/secrets/*`
- `src/components/settings/*`
- `src/lib/api/*`
- `src/test/*`

## Route Contract To Implement

Required clean routes:

- `/`
- `/programs`
- `/orchestration`
- `/agents/configs`
- `/report`
- `/secrets`
- `/settings`

Allowed compatibility redirect:

- `/orchestration-center` -> `/orchestration`

Explicitly not in v1 frontend scope for this phase:

- `/agents/:id/chat`
- `/agents/:id/activity`

Those source routes are brownfield references only and should not block the mission-control rebuild.

## Backend Contracts Available After Phase 5

The frontend should target these clean backend endpoints:

- `GET /api/control-ui/shell/hud`
- `GET /api/control-ui/agents`
- `GET /api/control-ui/agents/{id}/context-files`
- `GET /api/control-ui/programs/overview`
- `GET /api/control-ui/programs/applications/{id}`
- `GET /api/control-ui/orchestration/overview`
- `GET /api/control-ui/orchestration/runs`
- `GET /api/control-ui/orchestration/runs/{id}`
- `POST /api/control-ui/orchestration/trigger`
- `GET /api/control-ui/reporting/agent-coverage`
- `GET /api/control-ui/reporting/loss-pending`
- `GET /api/control-ui/secrets/status`
- `POST /api/control-ui/secrets/test/{key_name}`
- `GET /api/settings`
- `PUT /api/settings`

## Design Contract

This phase must implement the design language from `/Users/IAn/Downloads/PLAN.md`:

- warm dark terminal palette
- amber phosphor glow as the primary accent
- IBM Plex Mono for display/data
- DM Sans for body and labels
- scanlines, noise, glass panels, and restrained motion
- zero purple SaaS styling
- dense but readable operational surfaces

## Security Contract

- Do not store admin or autonomy keys in `localStorage`
- Do not persist provider secrets in the browser
- Frontend auth entry may exist only as in-memory session state for the current tab
- `/secrets` must display status/test results, never raw secret values

## Success Criteria

Phase 6 is successful when:

1. The new frontend exists as a standalone buildable app in `AI-Enterprise`
2. The required routes render with the planned design system
3. The UI consumes the clean Phase 5 backend contracts
4. No legacy compiled bundle or browser-persisted secret pattern is reintroduced
