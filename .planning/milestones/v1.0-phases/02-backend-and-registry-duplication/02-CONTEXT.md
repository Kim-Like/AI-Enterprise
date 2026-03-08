# Phase 2: Backend And Registry Duplication - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning
**Source:** Phase 1 packet + source backend/runtime files

<domain>
## Phase Boundary

Create the clean AI-Enterprise backend foundation in `/Users/IAn/Agent/AI-Enterprise` by duplicating the source runtime, persistence, registry metadata, and compatibility-critical IDs from `/Users/IAn/Agent/IAn` without carrying forward the legacy frontend, generated assets, or broad startup side effects.

</domain>

<decisions>
## Implementation Decisions

### Target root and package shape
- The clean duplicate root remains locked to `/Users/IAn/Agent/AI-Enterprise`.
- The clean backend should live under `AI-Enterprise/api/` rather than copying the source `backend/` layout wholesale.
- The target backend should preserve source behavior and IDs while adopting a cleaner package boundary for future frontend and API work.

### Runtime foundation
- Duplicate the source FastAPI application-factory pattern, but move startup mutations out of `create_app()` into explicit bootstrap helpers.
- Preserve the SQLite/WAL runtime and schema-based bootstrap approach from `backend/db/client.py` and `backend/db/schema.sql`.
- Duplicate only the minimum route slice needed to prove runtime viability in this phase: `/health`, `/api/meta/runtime`, and foundational control-plane hooks required by later phases.

### Registry and ownership contracts
- Preserve `program_registry`, `application_registry`, `data_store_registry`, and master ownership semantics from the source system.
- Preserve canonical program IDs, application IDs, and master IDs exactly.
- Port ownership/routing rules as source-compatible logic, not as reinterpreted business rules.

### Scope exclusions
- Do not duplicate the source frontend, `backend/static/ui/`, generated assets, or any Vite/Tailwind build output in this phase.
- Do not duplicate portfolio program payloads or agent markdown packets yet; those belong to Phase 3.
- Do not port chat, orchestration, secrets-panel, or reporting surfaces beyond what is required for backend foundation and compatibility mapping.

### Startup safety
- Treat `migrate_brain_files`, `ensure_specialist_schema`, `sync_registry`, `sync_application_registry`, `sync_specialists`, `backfill_workspace_attribution`, and boundary-matrix validation as isolated startup steps, not unconditional import-time behavior.
- The clean build must make it obvious which startup steps are safe in local development and which mutate runtime state.

### Claude's Discretion
- Exact module boundaries inside `AI-Enterprise/api/`
- Whether compatibility mapping lives in code, docs, or test fixtures so long as it is traceable
- Test file layout and fixture structure for the new backend foundation

</decisions>

<specifics>
## Specific Ideas

- Use the source files `backend/config.py`, `backend/db/client.py`, `backend/db/schema.sql`, `backend/routes/health.py`, `backend/routes/meta.py`, `backend/system/program_registry.py`, `backend/system/application_registry.py`, `backend/agent/ownership_rules.py`, and `backend/agent/identity_loader.py` as the main duplication references.
- Do not reproduce the source app's SPA mounting or static asset coupling in this phase.
- Use Phase 2 to establish the new backend spine that later phases can attach agents, programs, orchestration, and frontend routes onto.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/config.py`: source env loading and root path conventions
- `backend/db/client.py`: SQLite client, WAL setup, and migration hook pattern
- `backend/db/schema.sql`: source system-of-record tables for orchestration, registries, and execution history
- `backend/routes/health.py` and `backend/routes/meta.py`: minimal runtime diagnostics route shape
- `backend/system/program_registry.py` and `backend/system/application_registry.py`: canonical registry data and sync logic
- `backend/agent/ownership_rules.py`: canonical master/program ownership and routing hints
- `backend/agent/identity_loader.py`: canonical agent file loading contract

### Established Patterns
- The source backend uses thin route modules with heavier `backend/system/*` services.
- Runtime state and registry truth are bootstrapped from SQLite plus JSON catalogs.
- The source app currently mixes backend bootstrap and side-effectful sync calls inside `create_app()`.

### Integration Points
- Phase 2 outputs must support later duplication of Phase 3 agents and programs without changing IDs.
- The clean backend must keep compatibility with the source route inventory tracked in `.planning/codebase/ARCHITECTURE.md` and `01-SOURCE-TRACEABILITY.md`.
- `.env.example` in the new root must preserve required env names from the source system while removing browser-side secret exposure patterns.

</code_context>

<deferred>
## Deferred Ideas

- Full control-ui endpoint normalization belongs mostly to Phase 5
- Full agent packet duplication belongs to Phase 3
- Frontend rebuild belongs to Phase 6
- End-to-end live routing validation belongs to Phase 7

</deferred>

---

*Phase: 02-backend-and-registry-duplication*
*Context gathered: 2026-03-08*
