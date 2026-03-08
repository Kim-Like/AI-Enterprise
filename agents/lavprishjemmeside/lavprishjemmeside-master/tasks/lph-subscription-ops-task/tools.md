# LPH Subscription Ops Task - Tools

## Primary Tooling
- Client subscription scope under `ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/ljdesignstudio.dk` with DB-backed configuration.
- MySQL-backed reporting queries with safe aggregation boundaries.
- Task queue context contracts for dependencies and handoff sequencing.

## Control Plane and Verification
- FastAPI endpoints: `/api/tasks`, `/api/errors`, `/api/system-map`, `/api/datastores/verify`.
- Runtime health checks: `/health` and `/api/meta/runtime`.
- Local/Tailscale access: `http://localhost:8001` and `http://100.96.78.62:8001`.

## Security and Reliability Guardrails
- Never hardcode secrets; rely on `.env` and environment injection.
- Validate queue context keys: `program_id`, `scope_path`, `acceptance_criteria`, `dependencies`, `constraints`, `handoff_to`.
- Escalate cross-domain security/reliability incidents to Engineer with error-log traceability.
