# Father Agent - Tools

## Control Plane Interfaces

- FastAPI APIs: `/api/execute`, `/api/tasks`, `/api/errors`, `/api/agents`, `/api/system-map`, `/api/datastores/verify`
- Workspace APIs: `/api/workspace/system-overview`, `/api/workspace/agents/{agent_id}/context`, `/api/chat/*`
- SQLite orchestration DB `father.db` in WAL mode for queue/error/history state

## Prompt and Runtime Tooling

- Claude runtime subprocess tooling (`CLAUDE_BINARY`, model profile settings)
- Prompt assets registry (`prompt_assets_registry`) synchronized from father/engineer/master/task markdown assets
- Runtime diagnostics via `/api/meta/runtime` and engineer console views

## Claude Model and Context APIs

- `GET /api/models/catalog?agent_id={agent_id}`
- `PATCH /api/models/agents/{agent_id}` (admin key)
- `PATCH /api/chat/threads/{thread_id}/model`
- `GET /api/chat/threads/{thread_id}/context-usage`
- `POST /api/chat/threads/{thread_id}/context-refresh`

## Operational Tooling

- Server run command: `python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001`
- Health checks: `/health` and `/api/meta/runtime`
- Access paths: `http://localhost:8001` and Tailscale `http://100.96.78.62:8001`

## Governance Constraints

- Canonical root: `/Users/IAn/Agent/IAn`
- `father.db` is orchestration-only; business data stays in app-native datastores
- Never bypass ownership mapping or queue context contract keys

## vNext Governance Surfaces

- Delegation contracts:
- `POST /api/tasks/{task_id}/delegate`
- `POST /api/tasks/{task_id}/result`
- `POST /api/tasks/{task_id}/escalate`
- Stack coherence registry: `backend/config/stack_profiles.json`
- Escalation and result ledgers:
- `task_escalations`
- `task_result_packets`
- Decision telemetry ledger:
- `specialist_invocations` with route/delegate/compress/escalate/chat scope tagging

## Warn-Only Contract Governance

- Global mode: `ORCH_CONTRACT_MODE=warn_only`.
- Boundary source of truth: `backend/config/orchestrator_boundary_matrix.json`.
- Shared helper module: `backend/system/orchestration_policy.py`.
- Warning outputs are expected in API responses and persisted in telemetry decision payloads.
- Missing contract fields should never block delegation by themselves.
- Triaging key: use `correlation_id` across `task_queue`, `task_result_packets`, `task_escalations`, and `specialist_invocations`.

## Claude Policy Constraints

- `opus_46` is restricted to `engineer` identity.
- `haiku_30` remains disabled by policy.
- Denied profile requests must degrade gracefully to `sonnet_46` with warning telemetry.
