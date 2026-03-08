# Phase 5: Orchestration And Control API Normalization - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning
**Source:** Master PRD + Phase 4 security baseline + source control-ui/orchestration services

<domain>
## Phase Boundary

Rebuild the clean target's operator-facing API surface so AI-Enterprise exposes normalized control-plane endpoints for agents, programs, reporting, secrets, and orchestration while preserving the source system's required route and payload behavior. This phase converts the duplicated schema and registries into live read/write backend surfaces that later frontend work can bind to directly.

</domain>

<decisions>
## Implementation Decisions

### API normalization
- The clean target should expose the normalized control-plane routes named in the master PRD, even if selected legacy routes remain as compatibility aliases during transition.
- Phase 5 must keep source route behavior traceable; aliasing or explicit versioning is acceptable, silent drift is not.
- Secrets routes implemented in Phase 4 become part of the normalized control-plane surface rather than a temporary side path.

### Control-plane read surfaces
- Phase 5 should rebuild agents, programs, reporting, and agent-config/context payloads on the clean backend.
- The source `backend/system/control_ui_service.py` is a reference for payload shape, not a mandate to duplicate one monolithic service file unchanged.
- Agent/config/reporting payloads should use duplicated agent packets, registry tables, and specialist rows in the target DB.

### Orchestration runtime surfaces
- The clean target already has the orchestration schema; Phase 5 should port the flow/run service layer rather than inventing a new persistence model.
- Specialist projection into `specialist_agents` is part of Phase 5 because orchestration flows and control-plane agent views depend on it.
- Run-state routes must surface queue, run detail, step timeline, and a manual trigger path with observable status.

### Security boundary
- All new control-plane writes must use the Phase 4 hardened auth model.
- Read surfaces that expose operational state may use admin or autonomy authorization where appropriate, but settings-grade sensitivity stays admin-only.

### Claude's Discretion
- Exact module split between query helpers, control-ui aggregation, and orchestration services
- Which legacy route aliases remain live in Phase 5 versus being documented-only compatibility mappings
- Exact test fixture strategy for seeded flows, specialists, and run-state assertions

</decisions>

<specifics>
## Specific Ideas

- Port a minimal `specialist_service` slice that can sync duplicated specialist packets into `specialist_agents`.
- Add `api/routes/control_ui.py` for normalized agent/program/reporting surfaces and compatibility aliases.
- Add `api/routes/orchestration.py` for flow/run operations plus the normalized `/api/control-ui/orchestration/*` contract.
- Extend `api/system/application_registry.py` with fetch/query helpers needed by the new endpoints.
- Add contract tests for control-ui reads and orchestration writes/run-state detail.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- Source `backend/routes/control_ui.py` and `backend/system/control_ui_service.py`
- Source `backend/routes/orchestration.py` and `backend/system/orchestration_service.py`
- Source `backend/system/specialist_service.py` for specialist sync into `specialist_agents`
- Target `AI-Enterprise/api/db/schema.sql` already includes `specialist_agents`, `task_queue`, `chat_threads`, `orchestration_flows`, `orchestration_flow_steps`, and run tables

### Established Patterns
- The source runtime uses thin route modules over service/query functions.
- Control-ui payloads are aggregated from DB tables plus agent file health.
- Orchestration flow execution uses locked pipeline semantics with step/task/run linkage already represented in the duplicated schema.

### Integration Points
- Phase 6 frontend routes `/`, `/programs`, `/orchestration`, `/agents/configs`, and `/report` depend directly on Phase 5 payloads.
- Phase 7 end-to-end validation depends on Phase 5 providing observable run-state and manual trigger behavior.
- Phase 4 security routes and auth helpers are the mandatory gate for all new operational endpoints.

</code_context>

<deferred>
## Deferred Ideas

- Mission-control UI rendering belongs to Phase 6.
- Full live cutover and end-to-end operator validation belong to Phase 7.

</deferred>

---

*Phase: 05-orchestration-and-control-api-normalization*
*Context gathered: 2026-03-08*
