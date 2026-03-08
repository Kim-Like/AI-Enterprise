---
phase: 7
slug: live-wiring-validation-and-cutover
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 7 - Validation Strategy

> Validation contract for AI-Enterprise live delivery, end-to-end routing proof, and cutover readiness.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + pytest + frontend build/test + scripted validation |
| **Config file** | `AI-Enterprise/package.json`, `AI-Enterprise/tests/api/*`, `AI-Enterprise/scripts/validate_ai_enterprise.sh` |
| **Quick run command** | `cd /Users/IAn/Agent/AI-Enterprise && test -f api/app.py && test -f dist/index.html && test -f scripts/validate_ai_enterprise.sh` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && bash scripts/validate_ai_enterprise.sh` |
| **Estimated runtime** | ~60-120 seconds |

## Sampling Rate

- After every task batch: run the quick command
- After every plan wave: run the targeted command for that plan
- Before closing the phase: run the full suite command
- Max feedback latency: 60 seconds

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 7-01-01 | 01 | 1 | UI-03 | backend SPA delivery | `cd /Users/IAn/Agent/AI-Enterprise && npm run build && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_frontend_delivery.py -q` | yes | green |
| 7-01-02 | 01 | 1 | VAL-02 | end-to-end routing proof | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_live_cutover.py -q` | yes | green |
| 7-02-01 | 02 | 2 | VAL-03 | validation automation | `cd /Users/IAn/Agent/AI-Enterprise && bash scripts/validate_ai_enterprise.sh` | yes | green |
| 7-02-02 | 02 | 2 | VAL-03 | cutover docs present | `cd /Users/IAn/Agent/AI-Enterprise && test -f docs/cutover-readiness.md && test -f scripts/serve_ai_enterprise.sh` | yes | green |

*Status: pending, green, red, flaky*

## Wave 0 Requirements

Phase 7 begins with:

- frontend routes already live-wired in Phase 6
- no backend-served SPA delivery in the clean target
- no single validation command covering frontend plus backend constraints

## Manual-Only Verifications

- Review the backend-served root page in a browser and confirm the dashboard loads without a separate static file server.
- Review the cutover runbook for exact launch order and absolute paths.
- Review that the validation script does not leave `node_modules` inside the clean target after completion.

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers the current baseline and required new artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
