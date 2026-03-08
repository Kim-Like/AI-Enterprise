# Engineer Architecture Notes

## Mission

Engineer owns platform reliability, integration integrity, and cross-domain delivery quality for the IAn control plane.

## System Layers

1. API Layer
- FastAPI routes for health, tasks, settings, errors, agents, execute, models, chat, and workspace.

2. Orchestration Data Layer
- SQLite `father.db` with WAL mode.
- Queue, registry, and telemetry tables as control-plane source of truth.

3. Agent Layer
- Father -> Masters -> Specialists.
- Engineer is escalation lead and platform authority.

4. Program Layer
- Consolidated domain codebases in `programs/`.

5. Integration Layer
- WordPress/cPanel MySQL, Shopify, Brevo, Billy API, and datastore exit work.

## Critical Data Contracts

- `task_queue.context` includes:
- `program_id`
- `scope_path`
- `acceptance_criteria`
- `dependencies`
- `constraints`
- `handoff_to`

- specialist returns are structured through:
- `POST /api/tasks/{task_id}/result`
- `POST /api/tasks/{task_id}/escalate`

## Claude Control and Context Architecture

- Profile config source: `backend/config/claude_model_profiles.json`
- Policy logic: `backend/system/model_policy.py`
- Per-agent catalog: `GET /api/models/catalog?agent_id={agent_id}`
- Agent default mutation: `PATCH /api/models/agents/{agent_id}` (admin key)
- Thread controls:
- `PATCH /api/chat/threads/{thread_id}/model`
- `GET /api/chat/threads/{thread_id}/context-usage`
- `POST /api/chat/threads/{thread_id}/context-refresh`

Policy constraints:

- `opus_46` is engineer-only
- `haiku_30` is disabled
- fallback profile is `sonnet_46`

## Ownership Model

- Program ownership defined in `agent_program_assignments`.
- Father must not enqueue tasks without valid ownership.

## Core Engineer Sub-Personas

- `platform-reliability-task`
- `integration-architecture-task`
- `data-observability-task`
