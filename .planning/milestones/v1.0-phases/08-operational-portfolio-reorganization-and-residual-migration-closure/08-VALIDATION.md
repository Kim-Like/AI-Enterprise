---
phase: 8
slug: operational-portfolio-reorganization-and-residual-migration-closure
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 8 - Validation Strategy

> Validation contract for reorganizing AI-Enterprise into the final operating model while closing residual migration and deployment gaps.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + sqlite3 checks + ripgrep policy scans + pytest + remote curl/ssh validation |
| **Config file** | `AI-Enterprise/api/config/*`, `AI-Enterprise/api/system/*`, `AI-Enterprise/scripts/*`, `.planning/phases/08-*/` |
| **Quick run command** | `cd /Users/IAn/Agent && sqlite3 AI-Enterprise/ai_enterprise.db \"select count(*) from program_registry;\" && rg -n \"supabase|SUPABASE\" AI-Enterprise --glob '!**/node_modules/**' --glob '!**/dist/**'` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && pytest -q && bash scripts/validate_ai_enterprise.sh` plus targeted remote `ssh`/`curl` checks |
| **Estimated runtime** | ~2-5 minutes depending on remote checks |

## Sampling Rate

- After every metadata or hierarchy mutation: run the quick command
- After every plan wave: run the relevant pytest/shell checks plus the remote surface checks impacted by that wave
- Before closing the phase: full suite plus remote verification must be green
- Max feedback latency: 5 minutes

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 8-01-01 | 01 | 1 | ORG-01 | hierarchy metadata | `sqlite3 /Users/IAn/Agent/AI-Enterprise/ai_enterprise.db \"select count(*) from program_registry;\"` | yes | pending |
| 8-01-02 | 01 | 1 | ORG-02 | program tree audit | `find /Users/IAn/Agent/AI-Enterprise/programs -maxdepth 3 -type d | sort` | yes | pending |
| 8-01-03 | 01 | 1 | MIG-01 | Samlino carryover coverage | `find /Users/IAn/Agent/AI-Enterprise/programs/samlino/seo-agent-playground -maxdepth 2 -type d | sort` | yes | pending |
| 8-02-01 | 02 | 2 | MIG-02 | Supabase removal scan | `cd /Users/IAn/Agent && rg -n \"supabase|SUPABASE\" AI-Enterprise --glob '!**/node_modules/**' --glob '!**/dist/**'` | yes | pending |
| 8-02-02 | 02 | 2 | SEC-04 | deployment hardening policy | `cd /Users/IAn/Agent && rg -n \"Passenger|SetEnv|ghp_|re_\" IAn/scripts AI-Enterprise/scripts AI-Enterprise/docs --glob '!**/node_modules/**'` | yes | pending |
| 8-02-03 | 02 | 2 | VAL-04 | remote surface re-verification | `curl -fsS https://api.lavprishjemmeside.dk/health && curl -fsS https://api.ljdesignstudio.dk/health && curl -fsS https://reporting.theartisan.dk/health` | yes | pending |

*Status: pending, green, red, flaky*

## Wave 0 Requirements

Phase 8 begins with:

- a working AI-Enterprise dashboard and backend
- verified live remote CMS/reporting surfaces
- residual Supabase references still present in the clean target
- residual portfolio organization drift in the clean target
- at least one remote deployment surface with secret-bearing config

## Manual-Only Verifications

- Review the AI-Enterprise dashboard programs view to confirm the operator-facing hierarchy matches the requested model.
- Review that `Lavprishjemmeside` communicates its parent/client-site relationship clearly rather than as an SSH placeholder.
- Review that Samlino modules are classified intentionally rather than left half-present.
- Review that secret hardening changes do not break the live cPanel APIs.

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers the current baseline and required new artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 5 minutes
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
