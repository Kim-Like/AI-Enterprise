# Lavprishjemmeside Master - Tools

## Domain Tooling
- Core codebase at `ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/lavprishjemmeside.dk`
- Companion domain repo at `ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/ljdesignstudio.dk`
- SEO/Ads modules run from CMS repo and DB-backed config (no local module folders)
- Subscription ops scope is repo + database driven (no local module folder)
- MySQL on cPanel as primary datastore

## Control Plane and Operations
- Queue/error management through `/api/tasks` and `/api/errors`
- Datastore status via `/api/datastores/verify`
- System mapping via `/api/system-map`

## Guardrails
- Preserve Git as code source of truth and MySQL as app-data source of truth; no uncontrolled schema drift or live-only code changes.
- Maintain deterministic ownership and handoff contracts.

## Delegation vNext Interfaces
- `POST /api/tasks/{task_id}/delegate` for specialist assignment with structured mission payloads.
- `POST /api/tasks/{task_id}/result` for structured specialist completion packets.
- `POST /api/tasks/{task_id}/escalate` for blocked-task escalation with engineer takeover.
- `specialist_invocations` as mandatory decision telemetry.
- `task_result_packets` and `task_escalations` as lifecycle evidence stores.


## Warn-Only Contract Governance
- Contract enforcement is permanent warn-only (`ORCH_CONTRACT_MODE=warn_only`).
- Use `backend/system/orchestration_policy.py` helpers for boundary, warning, and observability logic.
- Include boundary/model/warning metadata in telemetry decision envelopes.
- Never reject tasks solely because optional orchestration contract fields are absent.

## Model and Context Control Interfaces

- `GET /api/models/catalog?agent_id={agent_id}`
- `PATCH /api/models/agents/{agent_id}` (admin)
- `PATCH /api/chat/threads/{thread_id}/model`
- `GET /api/chat/threads/{thread_id}/context-usage`
- `POST /api/chat/threads/{thread_id}/context-refresh`

Policy reminders:

- `opus_46` is engineer-only.
- `haiku_30` is disabled.
- fallback profile is `sonnet_46`.
