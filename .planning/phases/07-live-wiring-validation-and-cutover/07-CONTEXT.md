---
phase: 7
slug: live-wiring-validation-and-cutover
created: 2026-03-08
status: ready
source_prd: /Users/IAn/Downloads/PLAN.md
source_codebase_map:
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/ARCHITECTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/CONCERNS.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/TESTING.md
depends_on:
  - phase: 6
    reason: "Phase 6 completed the mission-control frontend and route-level live wiring."
requirements:
  - UI-03
  - VAL-02
  - VAL-03
---

# Phase 7 Context

## Objective

Take the clean AI-Enterprise duplicate from “feature complete” to “operationally ready” by serving the built frontend from the clean backend, proving end-to-end routing across the hierarchy, and codifying one-command validation/cutover steps.

## Why This Phase Exists

Phase 6 completed the frontend rebuild, but the clean target still relies on ad hoc local serving for the dashboard and manual sequencing for frontend-versus-backend verification. The final phase must remove that operational ambiguity and replace it with repeatable delivery and validation.

## Current Verified Baseline

- Clean backend exists in `/Users/IAn/Agent/AI-Enterprise/api`
- Clean frontend exists in `/Users/IAn/Agent/AI-Enterprise/src`
- Frontend route/data tests pass
- Frontend production build passes
- Backend API contract suite passed earlier, but only when `node_modules` was not present inside the clean target
- The clean backend does not yet serve the built SPA from `/`

## Remaining Gaps To Close

- The dashboard should be reachable from the clean backend itself, not only from an ad hoc static file server.
- The overnight success criterion `IAn -> Program Master -> Specialist -> Engineer` needs a single end-to-end proof in the duplicated runtime.
- Validation should be reproducible with one command that handles the frontend dependency/worktree constraint safely.
- Cutover guidance should live in the clean project rather than in conversational context only.

## Scope

This phase may change:

- `/Users/IAn/Agent/AI-Enterprise/api/app.py`
- `/Users/IAn/Agent/AI-Enterprise/tests/api/*`
- `/Users/IAn/Agent/AI-Enterprise/scripts/*`
- `/Users/IAn/Agent/AI-Enterprise/docs/*`

This phase should not rebuild or redesign the frontend visuals.

## Success Criteria

Phase 7 is successful when:

1. The built mission-control frontend is served from the clean backend with SPA fallback behavior.
2. A duplicated-system test proves an `IAn -> Program Master -> Specialist -> Engineer` execution chain.
3. A single validation entrypoint proves frontend build/tests, backend tests, and bundle/security checks without leaving `node_modules` in the target root.
