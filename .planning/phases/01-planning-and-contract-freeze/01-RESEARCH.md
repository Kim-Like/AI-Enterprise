# Phase 1: Planning And Contract Freeze - Research

**Researched:** 2026-03-08
**Domain:** Brownfield codebase duplication planning and contract freeze
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- The brownfield source system is `/Users/IAn/Agent/IAn`
- The AI-Enterprise master PRD is `/Users/IAn/Downloads/PLAN.md`
- The codebase map in `.planning/codebase/` is the canonical reference for stack, integrations, architecture, structure, conventions, testing, and concerns
- Duplicate only first-party programs, agents, API/runtime behavior, registries, and operator workflows
- Exclude vendor trees, build output, logs, backups, nested VCS metadata, and duplicate incubators as first-party duplication targets
- Treat `backend/static/ui/` as generated output, not source of truth
- Preserve registry IDs, application IDs, master ownership, canonical agent file naming, and required API compatibility mappings
- Treat current source-system route payloads and `father.db` schema as compatibility inputs for planning
- Use GSD planning artifacts so the project can run through an uninterrupted overnight execution sequence
- Build the roadmap around duplication and hardening, not around new product scope
- Use Phase 1 to remove ambiguity before implementation phases begin

### Claude's Discretion
- Exact plan split and wave boundaries inside Phase 1
- Which codebase-map findings are elevated into must-haves vs supporting context
- How many execution plans Phase 1 should contain so long as they are actionable and verifiable

### Deferred Ideas (OUT OF SCOPE)
- Actual code duplication into AI-Enterprise target directories belongs to Phase 2 onward
- Frontend implementation work belongs primarily to Phase 6
- Full live cutover validation belongs to Phase 7

</user_constraints>

<research_summary>
## Summary

Phase 1 is not a technology-selection phase. The main problem is brownfield contract extraction: the source system already exists, already runs, and already encodes program ownership, agent hierarchy, route contracts, persistence, and integration expectations. The correct expert approach is to freeze those truths before any duplication work starts, so later implementation phases are driven by traceable source behavior rather than memory or aspirational redesign.

The mapped codebase shows that the source repo mixes platform code, portfolio payload, runtime state, generated assets, and security debt in one workspace. That means the first planning phase must make three things explicit: what is first-party duplication scope, which contracts are preserved or intentionally versioned, and which source problems are treated as migration risks rather than copied forward. The best planning baseline is therefore: master PRD + codebase map + GSD requirements/roadmap/state + a phase-specific context file.

**Primary recommendation:** Use Phase 1 to lock the source-system contract and execution structure, not to start implementation. Every later phase should consume the codebase map and this phase's planning artifacts as authoritative inputs.
</research_summary>

<standard_stack>
## Standard Stack

The established tools and artifacts for this phase are process-oriented rather than library-selection oriented.

### Core
| Library / Artifact | Version | Purpose | Why Standard |
|--------------------|---------|---------|--------------|
| `.planning/codebase/*.md` | current | Brownfield source overview | Prevents planning from drifting away from the real repo |
| `.planning/PROJECT.md` | current | Project identity and scope | Standard GSD project anchor |
| `.planning/REQUIREMENTS.md` | current | Checkable duplication requirements | Enables roadmap traceability |
| `.planning/ROADMAP.md` | current | Phase sequencing | Required for `gsd-plan-phase` and execution ordering |
| `.planning/STATE.md` | current | Session continuity and focus | Enables uninterrupted workflow across long sessions |

### Supporting
| Library / Artifact | Version | Purpose | When to Use |
|--------------------|---------|---------|-------------|
| `/Users/IAn/Downloads/PLAN.md` | current | Master AI-Enterprise PRD | Use as target-state truth and duplication brief |
| `node $HOME/.codex/get-shit-done/bin/gsd-tools.cjs` | current | GSD phase and roadmap parsing | Use to verify scaffold validity |
| `pytest` and shell verification commands | current | Phase validation checks | Use for artifact and contract verification, not product behavior yet |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| GSD scaffold + codebase map | Freeform planning docs | Faster initially, but poor traceability and weaker overnight continuity |
| Source-contract freeze first | Immediate code duplication | Higher risk of copying drift, security debt, or wrong boundaries |
| Evidence-driven exclusions | Manual judgment during implementation | More interruptions and more scope churn mid-execution |

**Installation:**
```bash
# No new libraries are required for Phase 1 planning.
# Existing repo tooling plus GSD templates are sufficient.
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Structure
```text
.planning/
|-- PROJECT.md
|-- REQUIREMENTS.md
|-- ROADMAP.md
|-- STATE.md
|-- codebase/
|   |-- STACK.md
|   |-- INTEGRATIONS.md
|   |-- ARCHITECTURE.md
|   |-- STRUCTURE.md
|   |-- CONVENTIONS.md
|   |-- TESTING.md
|   `-- CONCERNS.md
`-- phases/
    `-- 01-planning-and-contract-freeze/
        |-- 01-CONTEXT.md
        |-- 01-RESEARCH.md
        |-- 01-VALIDATION.md
        |-- 01-01-PLAN.md
        `-- 01-02-PLAN.md
```

### Pattern 1: Contract-First Brownfield Duplication
**What:** Lock source-system facts, exclusions, and preserved contracts before any duplication work.
**When to use:** When the source system is live and already encodes operational truth.
**Example:**
```markdown
- Source repo: `/Users/IAn/Agent/IAn`
- Preserve: registry IDs, canonical agent file contract, API compatibility mappings
- Exclude: vendor/build output, duplicate incubators, nested VCS metadata
```

### Pattern 2: Platform vs Portfolio Boundary
**What:** Separate the control plane from managed program payload during planning.
**When to use:** When one repo contains both orchestration infrastructure and downstream application code.
**Example:**
```markdown
Control plane:
- `backend/`
- `frontend/`
- `father/`, `engineer/`, `masters/`

Managed portfolio payload:
- `programs/*`
```

### Pattern 3: Traceability-Driven Phase Planning
**What:** Every phase requirement, roadmap entry, context decision, validation rule, and plan file must line up.
**When to use:** When execution will continue across long sessions and should not re-open settled scope.
**Example:**
```markdown
Requirement: AUD-01
Phase: 1
Plan coverage: `01-01-PLAN.md`
Validation: `01-VALIDATION.md`
```

### Anti-Patterns to Avoid
- **Planning directly against raw repo memory:** This bypasses the codebase map and reintroduces discovery churn.
- **Treating configured integrations as live:** The mapped source system explicitly distinguishes env presence from authenticated connectivity.
- **Copying security debt as part of duplication:** Weak auth, browser-side secrets, and side-effectful GETs should be migration risks, not preserved patterns.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

Problems that look simple but already have a better solution in the current workflow:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Brownfield inventory | Ad-hoc file-by-file notes | `.planning/codebase/*.md` | The map already captures the source repo in structured form |
| Phase sequencing | Loose task list in one big plan | GSD `ROADMAP.md` + phase directories | Execution and verification depend on phase structure |
| Requirement coverage | Narrative-only PRD mapping | `REQUIREMENTS.md` traceability table | Prevents gaps between plan intent and execution |
| Overnight continuity | Human memory or chat scrollback | `STATE.md` + phase docs | Long sessions need resumable project memory |

**Key insight:** The hard part is preserving live source-system truth, not inventing more planning formats.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Letting source-of-truth drift during planning
**What goes wrong:** Requirements, roadmap, and later plans stop matching the mapped repo or PRD.
**Why it happens:** Brownfield details are remembered loosely instead of tied to concrete artifacts.
**How to avoid:** Reference `.planning/codebase/*.md` and `/Users/IAn/Downloads/PLAN.md` directly in every planning artifact.
**Warning signs:** Requirement IDs stop mapping cleanly to roadmap phases or plan files.

### Pitfall 2: Under-scoping exclusions
**What goes wrong:** Vendor trees, generated UI output, duplicate incubators, or nested repos get treated as first-party duplication work.
**Why it happens:** Everything under one workspace looks equally important during fast-moving planning.
**How to avoid:** Keep the exclusion boundary explicit in project, requirements, roadmap, and phase context.
**Warning signs:** Plan files mention `node_modules`, build output, or vendor/plugin trees as duplication targets.

### Pitfall 3: Deferring security debt until late phases
**What goes wrong:** The rebuild quietly inherits browser-side secret storage, weak write auth, or unsafe read/write boundaries.
**Why it happens:** Duplication is framed as structure-only instead of behavior-plus-security.
**How to avoid:** Carry security findings from `.planning/codebase/CONCERNS.md` into roadmap requirements and phase gating.
**Warning signs:** Phase 2 or 3 plans copy auth or settings behavior without an explicit hardening boundary.
</common_pitfalls>

<code_examples>
## Code Examples

Verified local patterns from the source repo and planning scaffold:

### Preserved Source Contract Input
```markdown
# Source contract inputs used by planning
@.planning/codebase/ARCHITECTURE.md
@.planning/codebase/INTEGRATIONS.md
@.planning/codebase/CONCERNS.md
@/Users/IAn/Downloads/PLAN.md
```

### GSD Traceability Pattern
```markdown
| Requirement | Phase | Status |
|-------------|-------|--------|
| AUD-01 | Phase 1 | Pending |
| AUD-02 | Phase 1 | Pending |
| AUD-03 | Phase 1 | Pending |
```

### Compatibility-Preserving Boundary Rule
```markdown
Preserve:
- registry IDs
- canonical agent file names
- source-system API compatibility mappings

Exclude:
- vendor trees
- generated assets as source-of-truth
- duplicate incubators
```
</code_examples>

<sota_updates>
## State of the Art (2024-2025)

For this phase, the relevant current practice is process-focused:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Plan from memory and raw repo browsing | Use structured codebase maps before roadmap/phase planning | Modern AI-assisted brownfield workflows | Reduces drift and repeated discovery |
| Treat config-presence as integration health | Separate configured from live-authenticated status | Current ops/security practice | Prevents false confidence in cutover readiness |
| Let frontend carry operator secrets | Keep secrets server-side and expose status only | Current security baseline | Changes rebuild scope and acceptance criteria |

**New tools/patterns to consider:**
- Structured codebase maps as first-class planning input
- Validation contracts per phase, not only ad-hoc testing at execution time

**Deprecated/outdated:**
- Browser-stored operational secrets
- Side-effectful GET endpoints treated as harmless reads
</sota_updates>

<open_questions>
## Open Questions

1. **What is the exact target repo layout for AI-Enterprise?**
   - What we know: The master PRD defines the target structure and output files.
   - What's unclear: No longer open - the planning scaffold now locks the target root to `/Users/IAn/Agent/AI-Enterprise`.
   - Recommendation: Keep Phase 2 duplication logic path-parameterized, but treat `/Users/IAn/Agent/AI-Enterprise` as the default execution target.

2. **How much managed-program payload should be duplicated from local snapshots versus refreshed from remote sources?**
   - What we know: The source repo contains live local snapshots plus remote references and auth gaps.
   - What's unclear: Whether duplication should prefer the audited local payload or attempt remote sync during initial duplication.
   - Recommendation: Use local audited first-party snapshots as the duplication baseline and treat remote validation as a separate connection-hardening concern.
</open_questions>

## Validation Architecture

Phase 1 validation should prove planning integrity, not product runtime behavior:

- Verify GSD scaffold integrity with `gsd-tools` roadmap parsing and phase init.
- Verify all required planning artifacts exist: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `01-CONTEXT.md`, `01-RESEARCH.md`, `01-VALIDATION.md`, and Phase 1 plan files.
- Verify traceability: every Phase 1 requirement ID appears in roadmap and at least one Phase 1 plan file.
- Verify exclusions and contract-preservation rules are present in project, requirements, roadmap, context, and plans.
- Verify no secret values appear in generated planning docs.

<sources>
## Sources

### Primary (HIGH confidence)
- Local master PRD: `/Users/IAn/Downloads/PLAN.md`
- Local codebase map: `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONCERNS.md`
- Local brownfield repo docs and config via `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and `CLAUDE.md`

### Secondary (MEDIUM confidence)
- None used; this research was anchored to local repo truth and the master project plan

### Tertiary (LOW confidence - needs validation)
- None
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: Brownfield duplication planning for the IAn control plane
- Ecosystem: GSD planning workflow, mapped source repo, AI-Enterprise PRD
- Patterns: contract freeze, scope exclusion, platform/payload separation, traceability
- Pitfalls: source drift, under-scoped exclusions, copied security debt

**Confidence breakdown:**
- Standard stack: HIGH - based on local planning tooling and artifacts
- Architecture: HIGH - derived from mapped local source repo
- Pitfalls: HIGH - grounded in `.planning/codebase/CONCERNS.md`
- Code examples: HIGH - drawn from current local planning artifacts

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
</metadata>

---

*Phase: 01-planning-and-contract-freeze*
*Research completed: 2026-03-08*
*Ready for planning: yes*
