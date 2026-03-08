---
phase: 3
slug: program-and-agent-duplication
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 3 - Validation Strategy

> Validation contract for duplicating agents and program payloads into the clean target root.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + pytest |
| **Config file** | `AI-Enterprise/.gitignore`, duplication manifests in `AI-Enterprise/docs` |
| **Quick run command** | `test -d /Users/IAn/Agent/AI-Enterprise/agents && test -d /Users/IAn/Agent/AI-Enterprise/programs && test -f /Users/IAn/Agent/AI-Enterprise/tests/test_agent_hierarchy.py && test -f /Users/IAn/Agent/AI-Enterprise/tests/test_program_payloads.py` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/test_agent_hierarchy.py tests/test_program_payloads.py -q` |
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
| 3-01-01 | 01 | 1 | AGT-01 | structure | `test -d /Users/IAn/Agent/AI-Enterprise/agents/IAn && test -d /Users/IAn/Agent/AI-Enterprise/agents/Engineer && test -f /Users/IAn/Agent/AI-Enterprise/docs/agent-hierarchy.md` | yes | green |
| 3-01-02 | 01 | 1 | AGT-02 | packets | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/test_agent_hierarchy.py -q` | yes | green |
| 3-01-03 | 01 | 1 | AGT-01 | hygiene | `test -f /Users/IAn/Agent/AI-Enterprise/.gitignore && test ! -e /Users/IAn/Agent/AI-Enterprise/.pytest_cache` | yes | green |
| 3-02-01 | 02 | 2 | DUP-03 | payloads | `test -d /Users/IAn/Agent/AI-Enterprise/programs/artisan && test -d /Users/IAn/Agent/AI-Enterprise/programs/samlino && test -f /Users/IAn/Agent/AI-Enterprise/docs/program-payloads.md` | yes | green |
| 3-02-02 | 02 | 2 | AGT-02 | exclusions | `find /Users/IAn/Agent/AI-Enterprise/programs \\( -name .git -o -name node_modules -o -name venv -o -name .venv -o -name __pycache__ -o -name .pytest_cache \\) | grep -q . && exit 1 || exit 0` | yes | green |
| 3-02-03 | 02 | 2 | DUP-03 | tests | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/test_program_payloads.py -q` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Phase 3 starts from an existing target root but no agent/program duplication trees yet.

---

## Manual-Only Verifications

- Sanity check that copied placeholder programs remain placeholders rather than being silently expanded.
- Confirm manifests accurately describe explicit exclusions.

---

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers missing target-root artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
