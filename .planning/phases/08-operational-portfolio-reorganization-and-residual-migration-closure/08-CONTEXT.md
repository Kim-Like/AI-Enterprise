---
phase: 8
slug: operational-portfolio-reorganization-and-residual-migration-closure
created: 2026-03-08
status: ready
source_prd: /Users/IAn/Downloads/PLAN.md
source_codebase_map:
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/ARCHITECTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/STRUCTURE.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/INTEGRATIONS.md
  - /Users/IAn/Agent/AI-Enterprise/.planning/codebase/CONCERNS.md
depends_on:
  - phase: 7
    reason: "Phase 7 completed live wiring and operational validation, which exposed the residual closure work."
requirements:
  - ORG-01
  - ORG-02
  - MIG-01
  - MIG-02
  - SEC-04
  - VAL-04
verification_inputs:
  - /Users/IAn/Agent/AI-Enterprise/.planning/phases/07-live-wiring-validation-and-cutover/07-UAT.md
---

# Phase 8 Context

## Objective

Take AI-Enterprise from "cutover-ready duplicate" to "operationally organized portfolio authority" by restructuring the top-level program model, carrying forward missing operational context, removing residual Supabase drift, and hardening remote cPanel deployment surfaces.

## Why This Phase Exists

Phase 7 proved that the clean dashboard, orchestration chain, and validation tooling work. The follow-up verification also proved that several source-truth and operating-model gaps remain:

- the requested portfolio structure is not yet reflected in AI-Enterprise
- the Samlino duplicate omitted subprojects that still matter as mapped operational context
- Supabase dependencies remain in duplicated runtime and registry metadata
- cPanel deployment config for at least one live API surface still embeds sensitive runtime values

These are no longer planning assumptions. They are verified closure items that must be resolved before AI-Enterprise can be treated as the final governing dashboard.

## Locked Decisions

### Operating Model

- AI-Enterprise is governed by `IAn Agency` as the main agent program.
- Top-level portfolio programs for the operational dashboard are:
  - `Lavprishjemmeside`
  - `Artisan`
  - `Baltzer Games`
  - `Personal assistance`
- `Lavprishjemmeside` is the parent that governs client sites.
- `Lavprishjemmeside` must explicitly distinguish:
  - `CMS`
  - `client-sites`
  - `lavprishjemmeside.dk`
  - `ljdesignstudio.dk`

### Verification Truths

- Shared cPanel SSH access on `cp10.nordicway.dk:33` is working with the existing key.
- `https://api.lavprishjemmeside.dk/health` and `https://api.ljdesignstudio.dk/health` are live and DB-backed.
- `https://theartisan.dk` is live and `https://reporting.theartisan.dk/health` reports healthy MySQL state.
- The Lavprishjemmeside source system already has a template/client workflow in `IAn/scripts/lavpris/ssh_client_install.sh`.
- The personal assistant skeleton exists in the clean target.

### Verified Gaps

- `AI-visibility`, `seo-auditor`, and `samlino-mind-map` exist in the source Samlino tree but not in the clean target.
- Supabase remains in the clean target registry and duplicated Baltzer/Samlino code paths.
- The clean target program tree still reflects duplication-era grouping, not the requested operating model.
- Remote deployment config still embeds secret values in at least one cPanel API surface and must be hardened.

## Scope

This phase may change:

- `/Users/IAn/Agent/AI-Enterprise/programs/*`
- `/Users/IAn/Agent/AI-Enterprise/agents/*`
- `/Users/IAn/Agent/AI-Enterprise/api/config/*`
- `/Users/IAn/Agent/AI-Enterprise/api/system/*`
- `/Users/IAn/Agent/AI-Enterprise/api/db/*`
- `/Users/IAn/Agent/AI-Enterprise/docs/*`
- `/Users/IAn/Agent/AI-Enterprise/scripts/*`
- `/Users/IAn/Agent/AI-Enterprise/.planning/*`

This phase may also touch remote deployment scripts and runbooks, but it must not make destructive live-host changes without explicit verification criteria and rollback coverage.

## Desired End State

1. AI-Enterprise exposes the intended portfolio shape clearly in filesystem, registry, and dashboard data.
2. Samlino context is either duplicated into AI-Enterprise or explicitly archived with traceable references so it is no longer ambiguous.
3. Supabase is no longer part of the live AI-Enterprise operational surface.
4. Remote deployment/config handling for cPanel-backed APIs is safe and verifiable.
5. A post-change verification pass proves the live cPanel surfaces and local dashboard still work after reorganization.

## Planning Constraints

- Preserve stable program IDs and ownership semantics where possible; if labels change, add compatibility mapping rather than silent breaks.
- Do not lose remote-first program truth while reorganizing local directories.
- No secret values may be copied into planning docs, summary files, or tests.
- Treat the Phase 7 UAT as the authoritative evidence set for this phase boundary.
