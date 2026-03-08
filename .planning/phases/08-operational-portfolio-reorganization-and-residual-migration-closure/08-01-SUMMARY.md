---
phase: 08-operational-portfolio-reorganization-and-residual-migration-closure
plan: 01
subsystem: portfolio
tags: [registry, control-ui, frontend, docs, hierarchy]
requires:
  - phase: 07-live-wiring-validation-and-cutover
    provides: live dashboard, remote verification evidence, cutover baseline
provides:
  - explicit IAn Agency portfolio presentation layer
  - lavprishjemmeside cms and client-site structure contract
  - samlino context carryover under ian-agency
  - baltzer tcg migration-hold contract
affects: [phase-08-02, programs-overview, registry-sync, frontend-programs-map]
tech-stack:
  added: [no new libraries]
  patterns: [stable runtime ids with presentation metadata, migration-hold contract, archive-mapped context]
key-files:
  created:
    - /Users/IAn/Agent/AI-Enterprise/programs/baltzer/TCG-index/MIGRATION-HOLD.md
  modified:
    - /Users/IAn/Agent/AI-Enterprise/api/system/control_ui_service.py
    - /Users/IAn/Agent/AI-Enterprise/api/system/program_registry.py
    - /Users/IAn/Agent/AI-Enterprise/api/config/application_catalog.json
    - /Users/IAn/Agent/AI-Enterprise/src/components/programs/ProgramsMap.tsx
    - /Users/IAn/Agent/AI-Enterprise/docs/program-payloads.md
key-decisions:
  - "Keep program and application IDs stable while changing presentation labels and hierarchy."
  - "Model Lavprishjemmeside as remote-first CMS governance plus governed client-sites instead of fake local payloads."
  - "Demote Baltzer TCG into an explicit migration-hold contract instead of pretending it remains live."
patterns-established:
  - "Programs overview payload now carries agency metadata, lane descriptions, summaries, and structure badges."
  - "Archive-mapped context is kept under programs/ian-agency/contexts rather than top-level client program lanes."
requirements-completed: [ORG-01, ORG-02, MIG-01]
duration: 32min
completed: 2026-03-08
---

# Phase 8 Plan 01 Summary

**Explicit IAn Agency portfolio lanes, Lavprishjemmeside governance structure, and a demoted Baltzer TCG migration-hold contract**

## Performance

- **Duration:** 32 min
- **Started:** 2026-03-08T13:05:00Z
- **Completed:** 2026-03-08T13:36:38Z
- **Tasks:** 3
- **Files modified:** 20+

## Accomplishments

- Added a real portfolio presentation layer to the control-ui programs overview, including `IAn Agency`, top-level program lane labels, domain descriptions, and program structure badges.
- Made `Lavprishjemmeside` explicit as `cms/` plus governed `client-sites/` and documented the requested parent/client relationship.
- Rehomed Samlino under `programs/ian-agency/contexts/` and closed the missing-context ambiguity with archive-mapped coverage.
- Demoted `baltzer-tcg-index` to a migration-hold contract so the dashboard no longer treats that workload as live.

## Task Commits

No git commits were created. The repository still lacks a coherent baseline history, so task-atomic commits remain disabled for this milestone.

## Files Created/Modified

- `/Users/IAn/Agent/AI-Enterprise/api/system/control_ui_service.py` - agency/lane metadata and richer programs overview payload
- `/Users/IAn/Agent/AI-Enterprise/api/system/program_registry.py` - updated program/data-store truth for the reorganized portfolio
- `/Users/IAn/Agent/AI-Enterprise/api/config/application_catalog.json` - refreshed application notes and migration-hold wiring
- `/Users/IAn/Agent/AI-Enterprise/src/components/programs/ProgramsMap.tsx` - programs route now renders agency card, lane descriptions, and structure badges
- `/Users/IAn/Agent/AI-Enterprise/docs/program-payloads.md` - updated duplication manifest for Lavprishjemmeside and Baltzer TCG
- `/Users/IAn/Agent/AI-Enterprise/programs/baltzer/TCG-index/MIGRATION-HOLD.md` - explicit demotion contract and replacement path

## Decisions Made

- Preserved runtime IDs and ownership joins while adding a presentation layer for operator-facing hierarchy.
- Treated Samlino as `IAn Agency` context, not a top-level client program.
- Represented the unverified Baltzer TCG workload as `planned` and migration-held rather than carrying false live status.

## Deviations from Plan

### Auto-fixed Issues

**1. Verification command adjustment for Samlino path**
- **Found during:** Task 3
- **Issue:** The original plan verification still referenced the old `programs/samlino/...` location after the clean-target move.
- **Fix:** Verified the new canonical path at `programs/ian-agency/contexts/samlino/seo-agent-playground` and kept the registry/catalog aligned to that path.
- **Verification:** directory audit plus backend contract tests

## Issues Encountered

- The frontend route test could not run directly because `node_modules` were parked outside the clean target. This is expected and is handled by the full validation script in Plan 08-02.

## User Setup Required

None.

## Next Phase Readiness

- The portfolio hierarchy is now stable enough for deployment hardening and remote verification.
- Remaining work is concentrated in remote config enforcement, full validation wiring, and final Phase 8 closeout.

---
*Phase: 08-operational-portfolio-reorganization-and-residual-migration-closure*
*Completed: 2026-03-08*
