---
phase: 05-orchestration-and-control-api-normalization
plan: 01
subsystem: control-ui
tags: [agents, programs, reporting, compatibility]
requires: []
provides:
  - "Projected duplicated specialists into runtime `specialist_agents` rows"
  - "Added normalized control-ui read routes for agents, programs, reporting, and config coverage"
  - "Established compatibility aliases over the new control-plane payload layer"
affects: [phase-5, backend, control-ui, registry]
tech-stack:
  added: [control-ui aggregation service, specialist projection runtime]
  patterns: [registry-backed payloads, alias compatibility, auth-protected operator reads]
key-files:
  created:
    - /Users/IAn/Agent/AI-Enterprise/.planning/phases/05-orchestration-and-control-api-normalization/05-01-SUMMARY.md
  modified:
    - /Users/IAn/Agent/AI-Enterprise/api/bootstrap.py
    - /Users/IAn/Agent/AI-Enterprise/api/system/application_registry.py
    - /Users/IAn/Agent/AI-Enterprise/api/system/control_ui_service.py
    - /Users/IAn/Agent/AI-Enterprise/api/system/specialist_service.py
    - /Users/IAn/Agent/AI-Enterprise/api/routes/applications.py
    - /Users/IAn/Agent/AI-Enterprise/api/routes/control_ui.py
    - /Users/IAn/Agent/AI-Enterprise/api/app.py
    - /Users/IAn/Agent/AI-Enterprise/docs/api-compatibility.md
    - /Users/IAn/Agent/AI-Enterprise/tests/api/test_control_ui_contracts.py
key-decisions:
  - "Specialist state is projected into the clean runtime during bootstrap instead of being inferred ad hoc from folders."
  - "Normalized read routes and legacy aliases share the same payload builders so frontend rebuild work targets one backend contract."
  - "Operator-facing read routes remain protected by the Phase 4 write-authorization model."
patterns-established:
  - "Registry and filesystem aggregation into explicit control-ui DTOs"
  - "Compatibility aliasing without reviving the legacy frontend"
requirements-completed: []
duration: 35min
completed: 2026-03-08
---

# Phase 5 Plan 01: Normalize control-plane APIs Summary

**Completed the control-plane read layer: specialist projection, normalized agent/program/report payloads, and compatibility aliases are now backed by the clean duplicate runtime instead of placeholders.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-03-08T03:10:00Z
- **Completed:** 2026-03-08T03:45:00Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments
- Added specialist projection during bootstrap so `specialist_agents` is populated from the duplicated hierarchy and application registry.
- Implemented normalized control-ui read routes for agent rosters, canonical file coverage, programs, application detail, and loss-pending reporting.
- Preserved selected legacy route aliases such as `/api/control-ui/floor`, `/api/control-ui/agents/configs*`, and `/api/control-ui/report/state`.
- Added application list/detail/rescan routes backed by the duplicated registry and specialist sync.
- Added contract tests proving the payloads are real and registry-backed.

## Task Commits

No task commits were created.

The repository still has no coherent baseline commit, so execution tracking remains in summaries, validation artifacts, roadmap state, and tests instead of partial git history.

## Verification

- `tests/api/test_control_ui_contracts.py`: pass

## Self-Check

PASSED - the clean target now exposes real control-plane read APIs for the frontend rebuild and keeps compatibility aliases traceable.

---
*Phase: 05-orchestration-and-control-api-normalization*
*Completed: 2026-03-08*
