# Phase 5: Orchestration And Control API Normalization - Research

**Researched:** 2026-03-08
**Domain:** Control-plane route normalization, specialist projection, and orchestration flow/run services
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- The clean target should expose the normalized control-plane routes named in the master PRD.
- Required source route and payload behavior must remain traceable through aliases or explicit versioning.
- Phase 5 should rebuild agents, programs, reporting, and agent-config/context payloads on the clean backend.
- The target's existing orchestration schema should be used rather than replaced.
- Specialist projection into `specialist_agents` is part of Phase 5.
- All new writes must use the Phase 4 hardened auth model.

### Claude's Discretion
- Exact module split between query helpers, control-ui aggregation, and orchestration services
- Which legacy route aliases remain live in Phase 5
- Exact seeded-test strategy for flows and specialists

### Deferred Ideas (OUT OF SCOPE)
- Frontend implementation
- Full live cutover validation

</user_constraints>

<research_summary>
## Summary

Phase 5 is where the clean target stops being only a duplicated database and file tree and starts behaving like a control plane again. The source system already shows the right high-level pattern: a thin route layer over control-ui and orchestration services, with run state stored in normalized SQLite tables and agent identity/readiness derived from canonical files plus `specialist_agents`. The clean target already has most of the schema needed, but it is still missing the service layer and the `specialist_agents` projection that make those tables useful.

The cleanest path is a two-step rebuild. First, project the duplicated specialists into `specialist_agents` and rebuild the operator-facing read APIs for agents, programs, configs, and reporting. Second, port the orchestration flow/run service layer and expose both normalized control-ui run endpoints and the compatibility orchestration write routes the source system relies on. This sequencing keeps read-only UI surfaces from depending on half-built orchestration writes, while ensuring the run-state endpoints are backed by real specialist ownership data.

**Primary recommendation:** use the source control-ui and orchestration services as query/behavior references, but rebuild them as smaller clean-target modules with explicit route contracts and pytest-backed compatibility assertions.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | source current | route and payload layer | already the clean backend runtime |
| sqlite3 | stdlib | run-state and registry persistence | schema already duplicated |
| pytest | source current | contract and seeded-run verification | already the project test stack |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| JSON catalogs | checked in | application registry sync and payload lookup | continue using for registry-backed endpoints |
| filesystem packet loading | stdlib/pathlib | agent config and context-file health | for agent roster/config payloads |
| markdown compatibility docs | n/a | route alias/version traceability | update during this phase |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| porting source orchestration service semantics | inventing a new orchestration API | faster to code in isolation, but breaks traceability and later validation |
| specialist projection into DB | reading specialist folders ad hoc on every request | avoids sync work, but makes queries and orchestration writes inconsistent |
| alias-backed compatibility | replacing all old routes immediately | cleaner on paper, but breaks the source contract map too early |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: DB Projection for Specialists, Filesystem for Context Detail
**What:** sync specialist identities into `specialist_agents`, but read canonical file health/details from the duplicated packet directories when building config payloads.
**When to use:** for agents, configs, floor/roster, and orchestration assignment checks.
**Why:** DB rows give queryability; files remain the source of context truth.

### Pattern 2: Normalized Endpoint + Compatibility Alias
**What:** add the final route shape from the PRD, while keeping selected source-compatible aliases that call the same service functions.
**When to use:** where the source frontend and docs still reference older paths like `/api/control-ui/floor` or `/api/control-ui/report/state`.
**Why:** lets the clean target move forward without losing contract traceability.

### Pattern 3: Thin Route, Query/Service Layer Below
**What:** route files should stay declarative while aggregation and orchestration logic live in `api/system/*`.
**When to use:** for both control-ui and orchestration routes.
**Why:** source already proved this pattern, and the clean target needs smaller, testable slices.

### Pattern 4: Seeded Run-State Tests
**What:** create flows, steps, and runs in isolated test DBs to verify list/detail/trigger behavior.
**When to use:** for orchestration overview, run detail, queue, trigger, and retry contracts.
**Why:** these APIs are only meaningful if they are exercised against real DB rows, not empty-route smoke tests.

### Anti-Patterns to Avoid
- **Rebuilding the entire source `control_ui_service.py` monolith unchanged**
- **Creating orchestration routes before specialists are synced**
- **Normalizing routes without documenting old-to-new mappings**
- **Returning run-state contracts that only work when tables are empty**

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| route payloads from scratch with guessed fields | new ad hoc DTOs | source payload builders as contract references | keeps UI/API drift low |
| orchestration persistence redesign | new tables or event bus | existing duplicated schema and source query semantics | lower risk and already mapped to requirements |
| specialist ownership inference per request | repeated directory scans and regexes | specialist sync + ownership rules | stable IDs and queryable assignments |
| compatibility tracking in memory | undocumented route drift | updated `docs/api-compatibility.md` + tests | later phases need traceable contracts |

**Key insight:** Phase 5 should convert duplicated structure into queryable behavior, not start another architecture rewrite.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Building control-ui routes before `specialist_agents` exists
**What goes wrong:** agent/program payloads look empty or misleading because specialists never appear in the DB.
**Why it happens:** the duplicated file tree is mistaken for a complete runtime projection.
**How to avoid:** sync specialists as part of Phase 5, then build the read surfaces against those rows.
**Warning signs:** programs report zero active specialists despite duplicated task packets.

### Pitfall 2: Treating legacy route names as obsolete before the new frontend exists
**What goes wrong:** contract traceability is lost and future verification cannot prove equivalence.
**Why it happens:** normalization is interpreted as immediate deletion.
**How to avoid:** keep compatibility aliases or explicit mappings for the source surface until the rebuilt frontend lands.
**Warning signs:** `api-compatibility.md` says deferred or replaced, but no alias or version note exists in code/tests.

### Pitfall 3: Porting orchestration writes without read visibility
**What goes wrong:** flows can be created or triggered, but there is no trustworthy overview or run detail surface for operators.
**Why it happens:** write routes feel more “functional” than reporting routes.
**How to avoid:** deliver overview/list/detail/trigger together as a cohesive contract.
**Warning signs:** tests can create a run, but nothing exposes queue depth or step state.

### Pitfall 4: Returning empty-green payloads
**What goes wrong:** routes technically respond, but do not reflect real routing ownership or live DB state.
**Why it happens:** placeholder payloads are used to unblock the frontend.
**How to avoid:** seed/derive from actual registry, specialist, and orchestration rows in tests.
**Warning signs:** response structures are stable, but all counters stay zero regardless of inserted test data.

</common_pitfalls>

<open_questions>
## Open Questions

1. **How much of the source `control_ui_service.py` should be ported verbatim?**
   - What we know: it contains the right payload contracts but is much larger than Phase 5 needs.
   - Recommendation: port only the slices backing the PRD routes and compatibility aliases.

2. **Should the normalized `/api/control-ui/agents` replace `/api/control-ui/floor` immediately?**
   - What we know: the PRD prefers `/agents`, but the source frontend still uses `/floor`.
   - Recommendation: implement `/agents` as canonical and keep `/floor` as an alias in Phase 5.

3. **How should manual trigger work in the clean target?**
   - What we know: source writes use `/api/orchestration/flows/{flow_id}/run` and run-context patch/retrigger routes.
   - Recommendation: expose `POST /api/control-ui/orchestration/trigger` as the normalized entry point while retaining source orchestration write routes for compatibility.

## Validation Architecture

Phase 5 validation should prove:

- specialists are projected into `specialist_agents` from duplicated agent/task packets
- normalized control-ui routes for agents, programs, reporting, and configs exist and return real data
- selected legacy control-ui aliases remain mapped intentionally
- orchestration flow list/detail/trigger/context/retrigger routes work against the duplicated schema
- normalized orchestration overview/run routes surface queue depth, run detail, and step timeline
- source-to-target route mappings are updated in docs and tests

<sources>
## Sources

### Primary (HIGH confidence)
- `/Users/IAn/Downloads/PLAN.md`
- `README/organization.md`
- source `backend/routes/control_ui.py`
- source `backend/routes/orchestration.py`
- source `backend/routes/applications.py`
- source `backend/system/control_ui_service.py`
- source `backend/system/orchestration_service.py`
- source `backend/system/specialist_service.py`
- target `AI-Enterprise/api/db/schema.sql`

### Secondary (MEDIUM confidence)
- `AI-Enterprise/docs/api-compatibility.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`

### Tertiary (LOW confidence - needs validation)
- exact minimum alias set needed by the eventual rebuilt frontend versus historical source docs

</sources>

<metadata>
## Metadata

**Research scope:**
- control-ui read payloads
- orchestration flow/run services
- specialist projection
- route compatibility/aliasing

**Confidence breakdown:**
- schema support: HIGH
- source contract visibility: HIGH
- specialist sync dependency: HIGH
- minimal alias set: MEDIUM

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
</metadata>

---

*Phase: 05-orchestration-and-control-api-normalization*
*Research completed: 2026-03-08*
*Ready for planning: yes*
