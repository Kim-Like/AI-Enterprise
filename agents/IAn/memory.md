# Father Memory

Snapshot date: `2026-03-01`

## System Identity

- IAn is the single Father orchestrator.
- Canonical root: `/Users/IAn/Agent/IAn`.

## Current Orchestration State

- Consolidation into `programs/` is complete.
- Registry model is active in SQLite.
- Objective intake path is stable at `POST /api/execute`.
- Task context contract includes explicit program scope metadata.

## Active Governance Decisions

1. Hybrid datastore architecture is mandatory.
2. Father may only delegate to owned masters/programs.
3. Unowned or unroutable objectives must be logged.
4. Engineer owns platform-level reliability and integration remediation.

## Known Runtime Notes

- Planner can fall back to deterministic routing if runtime planner is unavailable.
- Datastore verification may report `missing_env` until external credentials are configured.

## Current Priority Sequence

1. Stabilize integration env configuration.
2. Maintain deterministic queue quality.
3. Advance domain implementations through master ownership.

## 2026-02-28 Capability Audit Update

- Completed full scan of `father/`, `engineer/`, and `masters/` markdown assets.
- Upgraded root orchestration docs (`skill.md`, `tool.md`, `SPAWN_RULES.md`) for Father, Engineer, and all Masters.
- Upgraded all task-agent `skill.md` and `tool.md` files with domain-specific capabilities, guardrails, and verification discipline.

## 2026-02-28 Orchestration vNext Update

- Delegation pipeline supports v2 mission envelopes with correlation IDs and model-tier receipts.
- Structured specialist lifecycle endpoints are active:
- `POST /api/tasks/{task_id}/result`
- `POST /api/tasks/{task_id}/escalate`
- Route/delegate/compress/escalate decisions are auditable in `specialist_invocations`.
- Stack coherence is contract-first using `backend/config/stack_profiles.json` while preserving multi-stack app flexibility.
- Engineer remains escalation lead; Father preserves strict layer discipline and ownership boundaries.

## 2026-02-28 Orchestrator Hardening v2 (Warn-Only)

- Father emits mission envelopes with `mission_id`, `boundary_set_id`, `boundary_plan`, and `observability_tags` into queued task context.
- Boundary overlap decisions are deterministic and surfaced as warnings (no hard contract block).
- Correlation continuity is explicit (`correlation_id`) for downstream master/specialist orchestration.
- Warn-only telemetry and decision envelopes are persisted in `specialist_invocations`.

## 2026-03-01 Claude Control and Context Continuity

- Model catalog and thread model controls are now part of standard ops and workspace context.
- Context usage and guided context refresh APIs are part of expected chat orchestration flow.
- Policy lock remains active: `opus_46` engineer-only, `haiku_30` disabled, fallback `sonnet_46`.
- Context continuation packets are persisted in `chat_thread_carryovers` and linked through thread lineage.

## 2026-03-01 Samlino v3 Control-Plane Rewrite

- Samlino runtime moved to control-plane-native route/service modules with no standalone backend dependency.
- Samlino specialist topology expanded to full SEO workflow specialists under `samlino-master`.
- Samlino datastore contract now points to local SQLite `programs/ian-agency/contexts/samlino/seo-agent-playground/data/samlino.db`.

## 2026-03-01 Kanban Governance v1

- Kanban lifecycle mapping is status/stage-first: planning, assigned, in_progress, blocked, completed, closed.
- Task versions (`v1`, `v1.1`, `v2`) are board metadata and do not replace status/execution_stage truth.
- Every stage transition must use guarded API contracts and produce audit trail entries.
- Archived duplicate tasks are excluded from default dashboards and Kanban views.
- WIP thresholds are warn-only and must trigger prioritization/rebalancing actions instead of hard blocking.
