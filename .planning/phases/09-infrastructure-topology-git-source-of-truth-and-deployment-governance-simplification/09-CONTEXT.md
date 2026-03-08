---
phase: 9
slug: infrastructure-topology-git-source-of-truth-and-deployment-governance-simplification
created: 2026-03-08
status: ready
source_prd: /Users/IAn/Downloads/PLAN.md
source_codebase_map:
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/ARCHITECTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/INTEGRATIONS.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/STRUCTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/CONCERNS.md
depends_on:
  - phase: 8
    reason: "Phase 8 completed portfolio reorganization and surfaced the remaining source-of-truth and repo-governance questions."
requirements:
  - INF-01
  - INF-02
  - INF-03
  - INF-04
  - INF-05
  - VAL-05
---

# Phase 9 Context

## Objective

Define the long-term infrastructure model for AI-Enterprise, with special focus on:

- whether GitHub is required or optional
- whether a Tailscale-reachable self-hosted Git server is acceptable
- which systems are source of truth versus deploy targets
- the simplest top-level repo and folder hierarchy that still supports rollback, traceability, and live governance

## Why This Phase Exists

Phase 8 finished the portfolio reorganization and remote-surface hardening work, but it did not settle the final operating model for source control and deployment governance.

The open decision is not "GitHub or no GitHub" in isolation. The real decision is:

1. what is the canonical source of truth for code
2. where that Git remote should live
3. which live surfaces deserve their own repos
4. how shallow the top-level hierarchy can stay without losing operator clarity or deploy safety

## Locked Decisions

### Source Of Truth

- Git is required as the canonical source of truth for code and infrastructure definitions.
- GitHub is optional. A self-hosted Git remote reachable over Tailscale is acceptable if it preserves:
  - clone/push/pull reliability
  - SSH access control
  - backup and disaster recovery
  - rollback by commit
  - source-to-live traceability
- cPanel and SSH hosts are deploy targets, not the primary source of truth.
- Emergency live hotfixes are allowed only if they are immediately backported into Git.

### Simplicity

- Keep the repo topology shallow and top-level.
- Avoid repo-per-app sprawl.
- Only independently deployed live surfaces should get separate repos by default.
- Placeholder apps, archive contexts, and non-independent modules stay inside the main AI-Enterprise repo unless they graduate into real deploy boundaries.

### Current Operating Truth

- The Lavprishjemmeside workflow already assumes Git-backed remote repos and Git SHA rollback.
- `lavprishjemmeside.dk`, `ljdesignstudio.dk`, and `reporting.theartisan.dk` behave like independent live surfaces.
- The current local `IAn` repo does not have a configured origin, and GitHub SSH auth is currently missing on this workstation.
- AI-Enterprise itself is governed locally today, but its long-term source-of-truth and remote strategy are not yet locked.

## Scope

This phase may change:

- `/Users/IAn/Agent/AI-Enterprise/.planning/*`
- `/Users/IAn/Agent/AI-Enterprise/docs/*`
- `/Users/IAn/Agent/AI-Enterprise/scripts/*`
- `/Users/IAn/Agent/AI-Enterprise/ops/*`
- Git/repo governance docs and manifests

This phase should prefer planning artifacts, manifests, and validation scripts over application-code churn.

## Desired End State

1. There is a documented recommendation for GitHub-backed versus self-hosted Git over Tailscale.
2. AI-Enterprise has a canonical repo topology and top-level folder hierarchy.
3. Live cPanel surfaces are explicitly classified as deploy targets, not source-of-truth stores.
4. The chosen model has validation steps for Git remote health, SSH connectivity, and rollback.
5. The result is simple enough to operate overnight without hidden repo sprawl.

## Planning Constraints

- Do not assume GitHub is mandatory.
- Do not treat Tailscale as a substitute for Git; it is a transport and access layer.
- Preserve the Phase 8 operating model for `IAn Agency -> Programs`.
- Favor the smallest number of repos that still respects real deploy boundaries.
- Keep top-level structure operator-readable before optimizing for theoretical scale.
