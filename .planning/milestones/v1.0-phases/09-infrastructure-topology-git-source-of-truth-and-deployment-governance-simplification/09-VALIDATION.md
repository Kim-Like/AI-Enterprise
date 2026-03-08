---
phase: 9
slug: infrastructure-topology-git-source-of-truth-and-deployment-governance-simplification
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 9 - Validation Strategy

> Validation contract for locking AI-Enterprise infrastructure topology, Git source-of-truth, and deploy governance without creating repo sprawl.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + ripgrep policy scans + git/ssh probes + existing AI-Enterprise validation scripts |
| **Config file** | `.planning/phases/09-*/`, `AI-Enterprise/docs/*`, `AI-Enterprise/ops/*`, `AI-Enterprise/scripts/*` |
| **Quick run command** | `cd /Users/IAn/Agent && test -f IAn/.planning/phases/09-infrastructure-topology-git-source-of-truth-and-deployment-governance-simplification/09-RESEARCH.md && rg -n \"source of truth|Tailscale|GitHub|cPanel|nested repos|repo\" IAn/.planning/phases/09-infrastructure-topology-git-source-of-truth-and-deployment-governance-simplification/*.md` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && bash scripts/check_remote_config_contract.sh && bash scripts/verify_remote_portfolio.sh` plus targeted `git ls-remote` / `ssh -T` checks for the chosen remote model |
| **Estimated runtime** | ~60-180 seconds depending on remote checks |

## Sampling Rate

- After every planning-doc change: run the quick command
- After every plan wave in execution: run the full suite command plus the wave-specific Git remote checks
- Before `$gsd-verify-work`: full suite must be green
- Max feedback latency: 300 seconds

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 9-01-01 | 01 | 1 | INF-01 | policy/doc contract | `rg -n \"Git is the canonical source of truth|deploy targets\" /Users/IAn/Agent/AI-Enterprise/docs /Users/IAn/Agent/AI-Enterprise/.planning/phases/09-*` | yes | pending |
| 9-01-02 | 01 | 1 | INF-02 | topology comparison | `rg -n \"GitHub|Tailscale|mirror|self-hosted\" /Users/IAn/Agent/AI-Enterprise/docs /Users/IAn/Agent/AI-Enterprise/.planning/phases/09-*` | yes | pending |
| 9-01-03 | 01 | 1 | INF-03, INF-04, INF-05 | repo classification and layout audit | `rg -n \"independent repo|embedded|archive|no nested repos|top-level\" /Users/IAn/Agent/AI-Enterprise/docs /Users/IAn/Agent/AI-Enterprise/ops /Users/IAn/Agent/AI-Enterprise/.planning/phases/09-*` | yes | pending |
| 9-02-01 | 02 | 2 | VAL-05 | Git remote health | `git ls-remote <configured-primary-remote> HEAD` | no | pending |
| 9-02-02 | 02 | 2 | VAL-05 | SSH path health | `ssh -T <configured-git-host> -o ConnectTimeout=5` | no | pending |
| 9-02-03 | 02 | 2 | INF-01, VAL-05 | deploy-target validation | `cd /Users/IAn/Agent/AI-Enterprise && bash scripts/check_remote_config_contract.sh && bash scripts/verify_remote_portfolio.sh` | yes | pending |

*Status: pending, green, red, flaky*

## Wave 0 Requirements

- Existing infrastructure covers the planning phase itself.
- Execution phase must add:
  - a canonical repo topology manifest
  - at least one Git remote validation script
  - at least one deploy provenance or rollback verification script

## Manual-Only Verifications

- Review that the final repo topology is still shallow enough to understand from the top-level directory tree alone.
- Review that no independent live site is nested as a working tree inside `AI-Enterprise`.
- Review that the selected remote model can be explained in one sentence: "Git is source of truth; {self-hosted Git over Tailscale or GitHub} is the remote; cPanel is deploy target."

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers the current baseline and required new artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 300s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
