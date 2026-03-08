---
phase: 1
slug: planning-and-contract-freeze
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 1 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + `gsd-tools` parsing |
| **Config file** | `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md` |
| **Quick run command** | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 1 >/dev/null && test -f .planning/PROJECT.md && test -f .planning/phases/01-planning-and-contract-freeze/01-CONTEXT.md && test -f .planning/phases/01-planning-and-contract-freeze/01-SOURCE-TRACEABILITY.md` |
| **Full suite command** | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 1 >/dev/null && python3 - <<'PY'\nfrom pathlib import Path\nimport re\nrequired = [\n    Path('.planning/codebase/STACK.md'),\n    Path('.planning/codebase/INTEGRATIONS.md'),\n    Path('.planning/codebase/ARCHITECTURE.md'),\n    Path('.planning/codebase/STRUCTURE.md'),\n    Path('.planning/codebase/CONVENTIONS.md'),\n    Path('.planning/codebase/TESTING.md'),\n    Path('.planning/codebase/CONCERNS.md'),\n    Path('.planning/phases/01-planning-and-contract-freeze/01-CONTEXT.md'),\n    Path('.planning/phases/01-planning-and-contract-freeze/01-SOURCE-TRACEABILITY.md'),\n    Path('.planning/phases/01-planning-and-contract-freeze/01-RESEARCH.md'),\n    Path('.planning/phases/01-planning-and-contract-freeze/01-VALIDATION.md'),\n    Path('.planning/phases/01-planning-and-contract-freeze/01-01-PLAN.md'),\n    Path('.planning/phases/01-planning-and-contract-freeze/01-02-PLAN.md'),\n]\nassert all(p.exists() for p in required)\ntext='\\n'.join(p.read_text() for p in Path('.planning').rglob('*.md'))\nfor token in ['AUD-01', 'AUD-02', 'AUD-03', '/Users/IAn/Agent/AI-Enterprise']:\n    assert token in text\npatterns = [\n    re.compile(r'sk-[A-Za-z0-9]{32,}'),\n    re.compile(r'ghp_[A-Za-z0-9]{36}'),\n    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),\n    re.compile(r'-----BEGIN [A-Z0-9 ]+PRIVATE KEY-----'),\n]\nassert not any(p.search(text) for p in patterns)\nPY` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quick command
- **After every plan wave:** Run the full suite command
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | AUD-01 | contract | `test -f .planning/codebase/STACK.md && test -f .planning/codebase/INTEGRATIONS.md && test -f .planning/codebase/ARCHITECTURE.md && test -f .planning/codebase/STRUCTURE.md && test -f .planning/codebase/CONVENTIONS.md && test -f .planning/codebase/TESTING.md && test -f .planning/codebase/CONCERNS.md` | yes | green |
| 1-01-02 | 01 | 1 | AUD-02 | docs | `grep -q "Exclude" .planning/PROJECT.md && grep -q "Exclude" .planning/phases/01-planning-and-contract-freeze/01-CONTEXT.md` | yes | green |
| 1-01-03 | 01 | 1 | AUD-03 | inventory | `grep -q "## Programs" .planning/phases/01-planning-and-contract-freeze/01-SOURCE-TRACEABILITY.md && grep -q "## Datastores" .planning/phases/01-planning-and-contract-freeze/01-SOURCE-TRACEABILITY.md && grep -q "## External Connections" .planning/phases/01-planning-and-contract-freeze/01-SOURCE-TRACEABILITY.md` | yes | green |
| 1-02-01 | 02 | 2 | AUD-01 | docs | `test -f .planning/phases/01-planning-and-contract-freeze/01-RESEARCH.md && test -f .planning/phases/01-planning-and-contract-freeze/01-VALIDATION.md` | yes | green |
| 1-02-02 | 02 | 2 | AUD-03 | traceability | `grep -q "AUD-01" .planning/phases/01-planning-and-contract-freeze/01-01-PLAN.md && grep -q "01-SOURCE-TRACEABILITY.md" .planning/phases/01-planning-and-contract-freeze/01-01-PLAN.md && grep -q "AUD-03" .planning/phases/01-planning-and-contract-freeze/01-02-PLAN.md` | yes | green |
| 1-02-03 | 02 | 2 | AUD-02 | security | `python3 - <<'PY'\nfrom pathlib import Path\nimport re\ntext='\\n'.join(p.read_text() for p in Path('.planning').rglob('*.md'))\npatterns = [\n    re.compile(r'sk-[A-Za-z0-9]{32,}'),\n    re.compile(r'ghp_[A-Za-z0-9]{36}'),\n    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),\n    re.compile(r'-----BEGIN [A-Z0-9 ]+PRIVATE KEY-----'),\n]\nassert not any(p.search(text) for p in patterns)\nPY` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors listed for Phase 1 have automated verification.

---

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
