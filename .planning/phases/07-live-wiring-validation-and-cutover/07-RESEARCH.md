---
phase: 7
slug: live-wiring-validation-and-cutover
created: 2026-03-08
status: complete
---

# Phase 7 Research

## Brownfield And Clean-State Facts That Matter

- The original source backend serves its UI bundle directly from FastAPI and falls back to `index.html` for operator routes.
- The clean target frontend is already buildable and route-complete, but the clean backend currently exposes only API routes.
- The clean target backend test `test_phase_2_exclusions_are_not_present` still asserts that `node_modules` should not remain in `AI-Enterprise` at rest.
- The clean orchestration service only allows active specialists as flow steps, but flow owners may still be `father`, `engineer`, or a master agent.

## Clean-Build Implications

- The operational dashboard should move from an ad hoc static server to backend-served `dist/` delivery so the clean target has a canonical front page.
- End-to-end routing proof should model hierarchy using:
  - flow owner `father`
  - a program-governor specialist owned by a Program Master
  - a task specialist owned by the same Program Master
  - an Engineer-owned specialist for technical completion
- Full validation needs a scripted sequence because frontend tooling temporarily requires `node_modules` in the project root while backend policy asserts it should not remain there.

## Recommended Phase Split

Plan `07-01`:

- add backend SPA delivery
- add end-to-end routing proof tests
- verify frontend delivery and orchestration chain

Plan `07-02`:

- codify a single validation command
- add cutover readiness documentation and launch instructions
- run the full validation sequence and close the milestone

## Risks To Control

- Catch-all SPA routing must not swallow `/api/*`, `/health`, docs, or asset failures.
- Validation automation must always park `node_modules` back outside the target root before backend tests run.
- End-to-end routing proof must use the duplicated hierarchy, not a fake one-off flow that bypasses program ownership.
