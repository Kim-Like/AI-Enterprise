---
phase: 6
slug: mission-control-frontend-rebuild
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 6 - Validation Strategy

> Validation contract for rebuilding the AI-Enterprise mission-control frontend against the clean Phase 5 backend.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + Vitest + Vite build |
| **Config file** | `AI-Enterprise/package.json`, `AI-Enterprise/vite.config.ts`, `AI-Enterprise/src/test/*` |
| **Quick run command** | `cd /Users/IAn/Agent/AI-Enterprise && test -f package.json && test -f src/App.tsx && test -f src/styles/tokens.css` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && npm run test -- --run && npm run build` |
| **Estimated runtime** | ~30-60 seconds after dependencies are installed |

## Sampling Rate

- After every task batch: run the quick command
- After every plan wave: run the full suite command
- Before closing the phase: full suite must be green
- Max feedback latency: 60 seconds

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 6-01-01 | 01 | 1 | UI-02 | toolchain scaffold | `cd /Users/IAn/Agent/AI-Enterprise && test -f package.json && test -f vite.config.ts && test -f src/main.tsx` | yes | green |
| 6-01-02 | 01 | 1 | UI-02 | shell render smoke | `cd /Users/IAn/Agent/AI-Enterprise && npm run test -- --run src/test/app-shell.test.tsx` | yes | green |
| 6-01-03 | 01 | 1 | UI-02 | build viability | `cd /Users/IAn/Agent/AI-Enterprise && npm run build` | yes | green |
| 6-02-01 | 02 | 2 | UI-01 | route surface rendering | `cd /Users/IAn/Agent/AI-Enterprise && npm run test -- --run src/test/routes.test.tsx -t routes` | yes | green |
| 6-02-02 | 02 | 2 | UI-01 | live API wiring | `cd /Users/IAn/Agent/AI-Enterprise && npm run test -- --run src/test/routes.test.tsx -t data` | yes | green |
| 6-02-03 | 02 | 2 | UI-02 | final frontend build | `cd /Users/IAn/Agent/AI-Enterprise && npm run test -- --run && npm run build` | yes | green |

*Status: pending, green, red, flaky*

## Wave 0 Requirements

Phase 6 begins with:

- normalized backend APIs completed in Phase 5
- no clean frontend scaffold yet in `AI-Enterprise`
- no accepted browser-side secret persistence model beyond in-memory session state

## Manual-Only Verifications

- Review typography and palette against the PRD rather than settling for default Vite styling.
- Review desktop and mobile shells for density and spacing discipline.
- Review that `/orchestration-center` redirects cleanly to `/orchestration`.
- Review that the frontend does not use `localStorage` or bundle raw provider/admin secrets.

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers the current baseline and required new artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
