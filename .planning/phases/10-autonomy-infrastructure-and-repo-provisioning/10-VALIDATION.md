---
phase: 10
slug: autonomy-infrastructure-and-repo-provisioning
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 10 - Validation Strategy

> Validation contract for adding always-on autonomy, governed repo provisioning, and rollback-safe safety rails to AI-Enterprise.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + shell validation + existing AI-Enterprise validation scripts |
| **Config file** | `AI-Enterprise/ops/repository-topology.json`, `AI-Enterprise/scripts/*`, `AI-Enterprise/api/*`, `AI-Enterprise/docs/*` |
| **Quick run command** | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=. pytest -q tests/test_phase10_contracts.py tests/api/test_autonomy_api.py` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && bash scripts/validate_autonomy.sh && bash scripts/validate_ai_enterprise.sh` |
| **Estimated runtime** | ~90-240 seconds |

## Sampling Rate

- After every task commit: run `PYTHONPATH=. pytest -q tests/test_phase10_contracts.py tests/api/test_autonomy_api.py`
- After every plan wave: run `bash scripts/validate_autonomy.sh && bash scripts/validate_ai_enterprise.sh`
- Before `$gsd-verify-work`: full suite must be green
- Max feedback latency: 300 seconds

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | AUT-01, AUT-05 | manifest/provider contract | `PYTHONPATH=. pytest -q tests/test_phase10_contracts.py -k topology` | ✅ | green |
| 10-01-02 | 01 | 1 | AUT-01, AUT-03, AUT-04 | provisioning dry-run and bootstrap preflight | `PYTHONPATH=. pytest -q tests/test_phase10_contracts.py -k provisioning` | ✅ | green |
| 10-01-03 | 01 | 1 | AUT-04 | policy and kill-switch contract | `PYTHONPATH=. pytest -q tests/api/test_autonomy_api.py -k policy` | ✅ | green |
| 10-02-01 | 02 | 2 | AUT-02 | executor-host bootstrap and scheduled execution contract | `PYTHONPATH=. pytest -q tests/test_phase10_contracts.py -k executor && PYTHONPATH=. pytest -q tests/api/test_autonomy_api.py -k executor` | ✅ | green |
| 10-02-02 | 02 | 2 | AUT-03, AUT-04, AUT-05 | credential, audit, and sync validation | `PYTHONPATH=. pytest -q tests/api/test_autonomy_api.py -k audit && PYTHONPATH=. pytest -q tests/api/test_autonomy_api.py -k sync` | ✅ | green |
| 10-02-03 | 02 | 2 | VAL-06 | full autonomy validation chain | `bash scripts/validate_autonomy.sh && bash scripts/validate_ai_enterprise.sh` | ✅ | green |

*Status: pending, green, red, flaky*

## Wave 0 Requirements

- `tests/test_phase10_contracts.py` — contract tests for topology, provisioning, and executor metadata
- `tests/api/test_autonomy_api.py` — API/service tests for policy, executor auth, audit, sync, and kill-switch enforcement
- `scripts/validate_autonomy.sh` — canonical autonomy validation entrypoint

Existing infrastructure already covers pytest, shell validation, and the top-level validation chain.

## Manual-Only Verifications

- Review that autonomous provisioning is limited to additive or reversible actions by default.
- Review that destructive actions remain admin-only or disabled by policy.
- Review that the executor-host bootstrap docs are sufficient to stand up a new host without laptop-only assumptions.

## Validation Sign-Off

- [x] All tasks have automated verification or explicit Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers the new autonomy-specific test and script surface
- [x] No watch-mode flags
- [x] Feedback latency < 300s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
