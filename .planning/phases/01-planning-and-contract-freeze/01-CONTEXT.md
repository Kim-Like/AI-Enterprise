# Phase 1: Planning And Contract Freeze - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning
**Source:** Master PRD (`/Users/IAn/Downloads/PLAN.md`) + `.planning/codebase/*`

<domain>
## Phase Boundary

Turn the AI-Enterprise master plan and source codebase map into a GSD-ready execution baseline for duplicating the brownfield IAn system. This phase locks scope, contracts, exclusions, and execution structure. It does not begin duplicating live backend/frontend/program code into AI-Enterprise yet.

</domain>

<decisions>
## Implementation Decisions

### Source of truth
- The brownfield source system is `/Users/IAn/Agent/IAn`
- The AI-Enterprise master PRD is `/Users/IAn/Downloads/PLAN.md`
- The codebase map in `.planning/codebase/` is the canonical reference for stack, integrations, architecture, structure, conventions, testing, and concerns
- The target duplication root is locked to `/Users/IAn/Agent/AI-Enterprise`

### Duplication boundary
- Duplicate only first-party programs, agents, API/runtime behavior, registries, and operator workflows
- Exclude vendor trees, build output, logs, backups, nested VCS metadata, and duplicate incubators as first-party duplication targets
- Treat `backend/static/ui/` as generated output, not source of truth
- Freeze source traceability in a dedicated matrix so later phases can point back to exact source entities

### Contract preservation
- Preserve registry IDs, application IDs, master ownership, canonical agent file naming, and required API compatibility mappings
- Treat current source-system route payloads and `father.db` schema as compatibility inputs for planning

### Planning workflow
- Use GSD planning artifacts so the project can run through an uninterrupted overnight execution sequence
- Build the roadmap around duplication and hardening, not around new product scope
- Use Phase 1 to remove ambiguity before implementation phases begin

### Claude's Discretion
- Exact plan split and wave boundaries inside Phase 1
- Which codebase-map findings are elevated into must-haves vs supporting context
- How many execution plans Phase 1 should contain so long as they are actionable and verifiable

</decisions>

<specifics>
## Specific Ideas

- The PRD already defines the target file outputs, design system, API normalization, secrets model, hierarchy, and execution checklist
- The codebase map already identifies the highest-risk source issues: weak auth, browser-stored secrets, side-effectful GETs, startup mutation, and mixed platform/payload boundaries
- Planning should be optimized for a long uninterrupted workflow, which means minimal remaining discovery and strong dependency ordering

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/codebase/STACK.md`: exact source stack and sub-stack inventory
- `.planning/codebase/INTEGRATIONS.md`: external systems, auth patterns, and configured-vs-live caveats
- `.planning/codebase/ARCHITECTURE.md`: control-plane layering and preserved contracts
- `.planning/codebase/STRUCTURE.md`: filesystem and duplication boundaries
- `.planning/codebase/CONCERNS.md`: security, auth, side-effect, and migration risks to front-load into planning

### Established Patterns
- `backend/routes/*` are thin and `backend/system/*` is heavy service logic
- Agent behavior is encoded through canonical Markdown packets, not only runtime code
- The source repo mixes platform and portfolio payload, so planning must keep those boundaries explicit

### Integration Points
- The rebuild must preserve or intentionally version the current control-plane API surfaces consumed by `frontend/src/api/*`
- The rebuild must preserve role ownership and canonical IDs used across `backend/system/program_registry.py`, `backend/system/application_registry.py`, and `backend/agent/ownership_rules.py`
- The rebuild must account for current external dependencies declared in registry data and env names

</code_context>

<deferred>
## Deferred Ideas

- Actual code duplication into AI-Enterprise target directories belongs to Phase 2 onward
- Frontend implementation work belongs primarily to Phase 6
- Full live cutover validation belongs to Phase 7

</deferred>

---

*Phase: 01-planning-and-contract-freeze*
*Context gathered: 2026-03-08*
