---
phase: 10
slug: autonomy-infrastructure-and-repo-provisioning
created: 2026-03-08
status: ready
source_prd: /Users/IAn/Downloads/PLAN.md
source_codebase_map:
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/ARCHITECTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/INTEGRATIONS.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/STRUCTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/CONCERNS.md
depends_on:
  - phase: 9
    reason: "Phase 9 locked the Git topology and validation model; Phase 10 builds the non-human execution and provisioning layer on top of it."
requirements:
  - AUT-01
  - AUT-02
  - AUT-03
  - AUT-04
  - AUT-05
  - VAL-06
---

# Phase 10 Context

## Objective

Make AI-Enterprise operationally autonomous for routine repo provisioning, execution, and deployment governance so IAn and Engineer do not depend on ad hoc human actions like manually creating remotes before a push.

## Why This Phase Exists

Phase 9 established the repo topology and Git governance model, but the execution path still depends on an operator for provider-side setup. The clean system now has:

- a canonical `AI-Enterprise` GitHub repo
- validated Git governance for the main repo
- topology manifests and bootstrap scripts

The missing layer is autonomy:

1. an always-on executor host
2. a non-human control identity with provisioning authority
3. an automated repo/bootstrap flow for governed surfaces
4. safety rails so autonomy does not become uncontrolled writes

## Locked Decisions

### Control-Plane Direction

- The autonomy system should prefer a Tailscale-hosted, always-on execution environment rather than a laptop-bound workflow.
- Git remains the canonical source of truth.
- cPanel remains a deployment target, not an authoring surface.
- Routine repo provisioning should be automatable from AI-Enterprise itself.

### Provider Strategy

- Tailscale-first autonomy is the preferred direction for maximum control.
- GitHub may remain the public or collaboration-facing remote.
- If GitHub is used for autonomous provisioning, a non-human control identity is required. Personal interactive credentials are not an acceptable long-term control plane.

### Safety And Scope

- Autonomous creation should cover missing governed Git remotes, bootstrap pushes, topology updates, and validation.
- Destructive or high-risk actions should remain guarded: repo deletion, billing, DNS ownership changes, and root-secret rotation.
- Every autonomous action must leave an audit trail and support rollback-safe failure handling.

### Integration Points Already Present

- `/Users/IAn/Agent/AI-Enterprise/ops/repository-topology.json` already classifies governed repo surfaces.
- `/Users/IAn/Agent/AI-Enterprise/scripts/bootstrap_primary_remote.sh` already bootstraps local repos against a remote.
- `/Users/IAn/Agent/AI-Enterprise/scripts/validate_git_governance.sh` and `validate_ai_enterprise.sh` already provide validation hooks.

## Scope

This phase may change:

- `/Users/IAn/Agent/AI-Enterprise/.planning/*`
- `/Users/IAn/Agent/AI-Enterprise/scripts/*`
- `/Users/IAn/Agent/AI-Enterprise/docs/*`
- `/Users/IAn/Agent/AI-Enterprise/ops/*`
- `/Users/IAn/Agent/AI-Enterprise/api/*`
- `/Users/IAn/Agent/AI-Enterprise/agents/*`
- `/Users/IAn/Agent/AI-Enterprise/.env.example`

This phase should prefer autonomy scaffolding, provisioning services, host bootstrap docs, and validation over unrelated application feature work.

## Desired End State

1. A non-human autonomy host exists in the architecture and is documented concretely.
2. Missing governed repos can be provisioned and bootstrapped without a human creating them first.
3. IAn and Engineer have a defined execution path on that host for scheduled or event-driven work.
4. Secrets and service credentials are server-side and separable from operator laptop state.
5. Autonomy remains auditable, bounded, and rollback-safe.

## Planning Constraints

- Keep top-level hierarchy shallow and operator-readable.
- Avoid turning autonomy into a broad platform rewrite.
- Favor extending the existing topology manifest and validation scripts over parallel systems.
- Keep the implementation practical for the current portfolio: `AI-Enterprise`, `lavprishjemmeside.dk`, `ljdesignstudio.dk`, and `reporting.theartisan.dk`.
- Do not require a human to manually create each remote as part of the steady-state workflow.
