---
phase: 8
slug: operational-portfolio-reorganization-and-residual-migration-closure
created: 2026-03-08
status: complete
---

# Phase 8 Research

**Researched:** 2026-03-08
**Domain:** Portfolio information architecture, residual source-context carryover, datastore decommissioning, and remote deployment hardening
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md and verification)

### Locked Decisions
- AI-Enterprise is governed by `IAn Agency`.
- The primary top-level programs for the operational dashboard are `Lavprishjemmeside`, `Artisan`, `Baltzer Games`, and `Personal assistance`.
- `Lavprishjemmeside` must explicitly model `CMS` and `client-sites`, with `lavprishjemmeside.dk` and `ljdesignstudio.dk` represented as governed client surfaces.
- Missing Samlino operational context cannot remain implicit or lost.
- Supabase should not remain part of the live AI-Enterprise operational surface.
- Remote cPanel deployment surfaces must not expose secret values in deployment config.

### Verified Baseline
- Shared SSH access to `cp10.nordicway.dk:33` is working.
- `api.lavprishjemmeside.dk`, `api.ljdesignstudio.dk`, and `reporting.theartisan.dk` are live and DB-backed.
- The template/client install model for Lavprishjemmeside already exists in `IAn/scripts/lavpris/ssh_client_install.sh`.
- Phase 7 UAT documented the remaining gaps and root causes.

### Deferred Ideas
- Expanding AI-Enterprise to net-new portfolio programs beyond the current source baseline.
- Replacing cPanel as hosting in this phase.
- Rebuilding the mission-control frontend again; Phase 8 should preserve the Phase 6/7 UI unless organization-driven data changes require narrow updates.

</user_constraints>

<research_summary>
## Summary

Phase 8 is not a feature-add phase. It is a truth-alignment phase. The clean duplicate works, but it still mixes two models:

1. a source-faithful duplication layout built for speed and traceability
2. the intended operating model where AI-Enterprise is the authoritative dashboard for a clearly governed client/program portfolio

The shortest safe path is to split the work into two tracks that still land in one phase:

- **Structure track:** reorganize portfolio metadata, folder layout, and registry projection so the clean target expresses the right programs and parent/child relationships without breaking stable IDs or live routes.
- **Closure track:** remove or demote residual brownfield dependencies and risks, specifically missing Samlino context, residual Supabase references, and secret-bearing remote deployment config.

The most important planning decision is to treat remote-first programs and archived/incubator contexts differently:

- `lavprishjemmeside.dk` and `ljdesignstudio.dk` are **remote-first live operational surfaces** and should stay remote-first, but the clean target must represent them explicitly as governed assets in the program tree and registry.
- `AI-visibility`, `seo-auditor`, and `samlino-mind-map` are **mapped context assets** whose status must be made explicit: either promoted into the clean target as operational modules or archived as non-operational context with registry coverage.

**Primary recommendation:** keep runtime IDs stable, introduce an explicit portfolio structure layer in the registry and filesystem, then execute residual migration closure and security hardening as deliberate artifacts rather than as side effects of directory moves.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Layer | Current Standard | Role In Phase 8 |
|-------|-------------------|-----------------|
| SQLite registry | `AI-Enterprise/ai_enterprise.db` | program/application/datastore truth and migration-safe renaming/mapping |
| JSON config catalogs | `AI-Enterprise/api/config/*.json` | canonical seed/update source for program/application presentation |
| Filesystem manifests | `AI-Enterprise/programs/*`, `AI-Enterprise/agents/*` | operator-visible portfolio shape and duplicated payload context |
| Bash/SSH automation | `IAn/scripts/lavpris/*`, `AI-Enterprise/scripts/*` | remote cPanel validation and deployment hardening |

### Supporting
| Tool | Purpose | Why It Matters |
|------|---------|----------------|
| Phase 7 UAT | authoritative evidence source | turns verified gaps into explicit planning truths |
| codebase map docs | brownfield structure and concern baseline | prevents rediscovery and keeps planning anchored |
| pytest + shell validation | regression and contract checks | proves reorganization does not break the working dashboard |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stable ID plus label/hierarchy remapping | renaming IDs and folders wholesale | cleaner superficially, but risks breaking orchestration ownership and registry joins |
| explicit archive/ops classification for Samlino | copying every Samlino subtree blindly | faster initially, but recreates brownfield sprawl |
| separate security-only hotfix phase | folding hardening into Phase 8 | another phase isolates risk better, but leaves known deployment exposure unowned longer |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Stable Runtime IDs, Explicit Portfolio Presentation Layer
**What:** preserve existing `program_id`, `application_id`, and owner IDs where they drive runtime behavior, but add explicit hierarchy/grouping fields and filesystem layout for operator clarity.
**When to use:** for `Lavprishjemmeside`, `Artisan`, `Baltzer`, `Personal assistance`, and any program move that should not break orchestration or registry lookups.
**Why:** operational reorganization should not silently rewrite runtime identity.

### Pattern 2: Remote-First Asset Modeling
**What:** represent remote-first client surfaces as first-class portfolio entries with source contract, live URL, health, and ownership, without pretending they are fully local payload duplicates.
**When to use:** for `lavprishjemmeside.dk`, `ljdesignstudio.dk`, and other SSH/cPanel-first properties.
**Why:** the current placeholder approach is too weak for the operator model, but forcing a fake local payload would be dishonest.

### Pattern 3: Context-Carryover Classification
**What:** classify carryover artifacts as `operational module`, `archive context`, or `sandbox reference`.
**When to use:** for Samlino subprojects and any residual brownfield module whose relationship to live operations is ambiguous.
**Why:** Phase 7 proved ambiguity is itself a defect.

### Pattern 4: Security Closure Through Deployment Contract Checks
**What:** pair secret relocation work with automated checks that fail when deployment config embeds live values.
**When to use:** for cPanel API subdomains and any generated `.htaccess`/Passenger setup.
**Why:** hardening without a detector will drift back immediately.

### Anti-Patterns to Avoid
- Moving directories without updating registry/catalog/ownership projections together
- Treating remote-first programs as “not real” because they are not fully local
- Deleting Supabase references from docs only while leaving live runtime/client code intact
- Solving the organization problem with naming only, while leaving the dashboard data model unchanged

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| portfolio hierarchy | ad hoc folder conventions only | registry + filesystem + docs kept in sync | dashboard and runtime need a shared truth |
| Samlino carryover | blanket copy or blanket delete | explicit module classification with traceable evidence | preserves meaning and reduces sprawl |
| Supabase removal | comment-only deprecation | code-path removal plus datastore registry updates | ensures the operational surface is actually clean |
| cPanel hardening | one-off host edits with no local trace | scripts/runbooks/tests that define the safe deployment contract | keeps the clean target reproducible |

**Key insight:** Phase 8 should not just “tidy folders.” It needs to make the operational model machine-readable and verifiable.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Breaking live ownership while reorganizing programs
**What goes wrong:** dashboard or orchestration lookups fail because IDs changed with the folder move.
**How to avoid:** keep runtime IDs stable and add mapping/presentation layers instead of destructive renames first.

### Pitfall 2: Copying missing Samlino subprojects without deciding their status
**What goes wrong:** AI-Enterprise regains brownfield sprawl and unclear scope.
**How to avoid:** classify each missing Samlino subtree before duplication: operational, archived context, or sandbox.

### Pitfall 3: Declaring Supabase removed while runtime still imports it
**What goes wrong:** operators believe the migration is complete, but live surfaces still depend on an undeclared backend.
**How to avoid:** pair registry cleanup with code search, test gates, and runtime replacement decisions.

### Pitfall 4: Fixing remote secrets manually but not the provisioning path
**What goes wrong:** the next deployment or bootstrap script reintroduces the same exposure.
**How to avoid:** update the provisioning/deploy contract and add a detector for secret-bearing config.

</common_pitfalls>

<recommended_phase_split>
## Recommended Phase Split

### Plan 08-01: Reorganize portfolio structure and carry over missing context
- define the target portfolio tree and program grouping model
- update registry/catalog/docs to represent `IAn Agency` and the requested top-level programs
- model `Lavprishjemmeside` as `CMS` plus governed `client-sites`
- classify and carry forward missing Samlino operational context

### Plan 08-02: Close residual runtime and deployment gaps
- remove or demote Supabase from the live AI-Enterprise surface
- harden cPanel deployment/config handling for remote APIs
- add verification coverage for remote surfaces, datastores, and post-reorganization registry state

This split keeps information architecture and portfolio truth stable before touching migration/security closure.
</recommended_phase_split>

## Validation Architecture

Phase 8 validation should prove:

- the program/application hierarchy shown by AI-Enterprise matches the requested operating model
- `Lavprishjemmeside` explicitly represents both CMS governance and client-site surfaces
- missing Samlino modules are no longer ambiguous: each is duplicated or explicitly archived with traceability
- `rg` across AI-Enterprise no longer finds live Supabase runtime usage in operational paths
- registry/datastore metadata no longer treats Supabase as part of the live AI-Enterprise operational surface
- remote cPanel deployment config no longer embeds raw secret values
- `api.lavprishjemmeside.dk`, `api.ljdesignstudio.dk`, `theartisan.dk`, and `reporting.theartisan.dk` still pass post-change verification

<sources>
## Sources

### Primary (HIGH confidence)
- `/Users/IAn/Agent/AI-Enterprise/.planning/phases/08-operational-portfolio-reorganization-and-residual-migration-closure/08-CONTEXT.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/phases/07-live-wiring-validation-and-cutover/07-UAT.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/codebase/STRUCTURE.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/codebase/INTEGRATIONS.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/codebase/CONCERNS.md`
- `/Users/IAn/Agent/IAn/scripts/lavpris/ssh_client_install.sh`
- `AI-Enterprise/api/system/program_registry.py`
- `AI-Enterprise/api/db/schema.sql`

### Secondary (MEDIUM confidence)
- `AI-Enterprise/programs/lavprishjemmeside/README.md`
- `AI-Enterprise/api/config/application_catalog.json`
- `AI-Enterprise/docs/program-payloads.md`
- source and target Samlino directory trees under `programs/samlino/seo-agent-playground`

</sources>

<metadata>
## Metadata

**Research scope:**
- portfolio structure
- remote-first program modeling
- Samlino carryover coverage
- Supabase removal
- cPanel deployment hardening

**Confidence breakdown:**
- verification evidence: HIGH
- source/target structure comparison: HIGH
- remote-host behavior: HIGH
- exact implementation details for replacement datastore paths: MEDIUM

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
</metadata>

---

*Phase: 08-operational-portfolio-reorganization-and-residual-migration-closure*
*Research completed: 2026-03-08*
*Ready for planning: yes*
