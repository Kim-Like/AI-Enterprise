---
phase: 5
slug: orchestration-and-control-api-normalization
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 5 - Validation Strategy

> Validation contract for rebuilding normalized control-plane and orchestration APIs in `AI-Enterprise`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + pytest |
| **Config file** | `AI-Enterprise/docs/api-compatibility.md`, target route modules in `api/routes/` |
| **Quick run command** | `test -f /Users/IAn/Agent/AI-Enterprise/api/routes/control_ui.py && test -f /Users/IAn/Agent/AI-Enterprise/api/routes/orchestration.py && test -f /Users/IAn/Agent/AI-Enterprise/tests/api/test_control_ui_contracts.py && test -f /Users/IAn/Agent/AI-Enterprise/tests/api/test_orchestration_contracts.py` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_runtime_foundation.py tests/api/test_registry_contracts.py tests/api/test_security_auth.py tests/api/test_connection_status.py tests/api/test_control_ui_contracts.py tests/api/test_orchestration_contracts.py -q` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quick command
- **After every plan wave:** Run the full suite command
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 5-01-01 | 01 | 1 | AGT-03 | specialist sync | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_control_ui_contracts.py -q -k specialist` | yes | green |
| 5-01-02 | 01 | 1 | API-01 | control-ui read routes | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_control_ui_contracts.py -q -k routes` | yes | green |
| 5-01-03 | 01 | 1 | API-01 | compatibility mapping | `test -f /Users/IAn/Agent/AI-Enterprise/docs/api-compatibility.md && grep -q \"/api/control-ui/agents\" /Users/IAn/Agent/AI-Enterprise/docs/api-compatibility.md` | yes | green |
| 5-02-01 | 02 | 2 | AGT-03 | orchestration service | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_orchestration_contracts.py -q -k flow` | yes | green |
| 5-02-02 | 02 | 2 | API-01 | normalized orchestration routes | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_orchestration_contracts.py -q -k control_ui` | yes | green |
| 5-02-03 | 02 | 2 | AGT-03 | run-state visibility | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_orchestration_contracts.py -q -k retrigger` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Phase 5 starts from a clean target with duplicated schema, registries, agents, programs, and security routes, but without control-ui aggregation or orchestration service routes implemented.

---

## Manual-Only Verifications

- Review that legacy route aliases and new normalized routes call the same underlying payload/service logic where intended.
- Review that orchestration `partial` or empty states are honest when no runs exist yet.
- Review that the route map in `docs/api-compatibility.md` matches the actual code.

---

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers the current baseline and new route/service artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 20s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
