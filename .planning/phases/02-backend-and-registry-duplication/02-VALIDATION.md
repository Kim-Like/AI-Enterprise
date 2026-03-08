---
phase: 2
slug: backend-and-registry-duplication
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 2 - Validation Strategy

> Validation contract for duplicating the clean backend/runtime foundation into `AI-Enterprise`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + pytest |
| **Config file** | `AI-Enterprise/.env.example`, `AI-Enterprise/requirements.txt` |
| **Quick run command** | `test -d /Users/IAn/Agent/AI-Enterprise && test -f /Users/IAn/Agent/AI-Enterprise/api/app.py && test -f /Users/IAn/Agent/AI-Enterprise/api/db/schema.sql && test -f /Users/IAn/Agent/AI-Enterprise/tests/api/test_runtime_foundation.py` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest tests/api/test_runtime_foundation.py tests/api/test_registry_contracts.py -q` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quick command
- **After every plan wave:** Run the full suite command
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 1 | DUP-01 | structure | `test -d /Users/IAn/Agent/AI-Enterprise && test -f /Users/IAn/Agent/AI-Enterprise/requirements.txt && test -f /Users/IAn/Agent/AI-Enterprise/.env.example` | yes | green |
| 2-01-02 | 01 | 1 | API-03 | runtime | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 - <<'PY'\nfrom api.app import create_app\napp = create_app()\npaths = {getattr(route, 'path', '') for route in app.routes}\nassert '/health' in paths\nassert '/api/meta/runtime' in paths\nPY` | yes | green |
| 2-01-03 | 01 | 1 | API-03 | tests | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest tests/api/test_runtime_foundation.py -q` | yes | green |
| 2-02-01 | 02 | 2 | DUP-02 | registry | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest tests/api/test_registry_contracts.py -q` | yes | green |
| 2-02-02 | 02 | 2 | API-02 | contracts | `test -f /Users/IAn/Agent/AI-Enterprise/docs/api-compatibility.md && grep -q "ian-control-plane" /Users/IAn/Agent/AI-Enterprise/docs/api-compatibility.md` | yes | green |
| 2-02-03 | 02 | 2 | DUP-01 | exclusions | `test ! -e /Users/IAn/Agent/AI-Enterprise/backend/static/ui && test ! -e /Users/IAn/Agent/AI-Enterprise/frontend && test ! -e /Users/IAn/Agent/AI-Enterprise/node_modules` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

The target project may not exist yet, so validation starts with structure assertions and grows into runtime + registry tests.

---

## Manual-Only Verifications

- Review that copied env names preserve source contracts without carrying secret values.
- Review that startup/bootstrap code makes side effects explicit rather than hidden in imports.

---

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers missing target-root artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
