# Engineer Agent - Tools

## Core Runtime

- Python virtualenv in `.venv`
- FastAPI + Uvicorn
- pytest
- sqlite3 CLI

## Control-Plane APIs

- `/health`
- `/api/execute`
- `/api/tasks`
- `/api/system-map`
- `/api/datastores/verify`
- `/api/programs/artisan-wordpress/inventory`
- `/api/programs/artisan-wordpress/ssh-check`
- `/api/programs/artisan-wordpress/ops-action`

## Claude Model and Context Control APIs

- `GET /api/models/catalog?agent_id={agent_id}`
- `PATCH /api/models/agents/{agent_id}` (admin)
- `PATCH /api/chat/threads/{thread_id}/model`
- `GET /api/chat/threads/{thread_id}/context-usage`
- `POST /api/chat/threads/{thread_id}/context-refresh`

## Operations Utilities

- `rg`, `curl`, `lsof`, `git`, `jq`
- local log files under `/tmp` when needed

## Integration Surfaces

- WordPress/cPanel MySQL
- WordPress controlled SSH ops (`cpanel_ssh_ops`)
- Artisan reporting cPanel MySQL (`ARTISAN_REPORTING_DB_*`)
- migration-hold datastore replacement work for Baltzer TCG
- Shopify
- Brevo
- Billy API

## Security/Quality Constraints

- explicit CORS origins only
- no secrets in committed markdown/code
- preserve deterministic ownership and queue contracts

## Orchestration vNext Interfaces

- `POST /api/tasks/{task_id}/delegate` (v1 compatible, v2 mission envelope supported)
- `POST /api/tasks/{task_id}/result` (structured specialist result packet)
- `POST /api/tasks/{task_id}/escalate` (blocked-task escalation protocol)
- Escalation payload schema: `backend/config/schemas/specialist_escalation_tool.schema.json`
- `specialist_invocations` as mandatory telemetry ledger for route/delegate/compress/result/escalate/tool/chat scopes
- `task_result_packets` for structured result persistence
- `task_escalations` for blocked-task lifecycle and engineer takeover
- `chat_thread_carryovers` for thread continuation packets

## Autonomy Authorization

- Write-capable specialist tool execution accepts:
- `X-Admin-Key` (operator path)
- `X-Autonomy-Key` (autonomous runtime path)
- Respect write gates:
- global `ENABLE_SPECIALIST_TOOL_WRITES=1`
- specialist `allow_write_tools=1`
- binding `writes_enabled=1`

## Model Policy Hard Rules

- `model_policy_engineer_only_opus=1` must remain enabled.
- `model_profile_haiku_30_enabled=0` must remain disabled unless an explicit migration decision is approved.
