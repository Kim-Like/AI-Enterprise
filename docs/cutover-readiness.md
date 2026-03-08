# AI-Enterprise Cutover Readiness

## Goal

Run the clean AI-Enterprise duplicate from its own backend entrypoint, validate frontend and backend health in one pass, and leave the worktree in the contract-safe state expected by the duplicate.

## Canonical Local Dashboard URL

- Backend-served dashboard: `http://127.0.0.1:8001/`

## Launch Sequence

1. Validate the full stack:

```bash
cd /Users/IAn/Agent/AI-Enterprise
bash scripts/validate_ai_enterprise.sh
```

2. Start the clean backend and dashboard:

```bash
cd /Users/IAn/Agent/AI-Enterprise
bash scripts/serve_ai_enterprise.sh
```

3. Open the dashboard:

```text
http://127.0.0.1:8001/
```

## What The Validation Script Proves

- frontend unit and route tests pass
- production frontend build succeeds
- no browser-persistent secret storage or forbidden bundle strings are present
- backend API and duplication tests pass
- `node_modules` is parked outside `AI-Enterprise` after validation so the clean-target duplication contract remains true at rest
- remote cPanel config files are checked for secret-bearing directives
- Git governance and repo-topology policy are checked before remote runtime validation
- live remote portfolio health endpoints are revalidated

## Expected Environment

- Python dependencies from `requirements.txt` installed
- Node/npm available
- frontend dependencies may be parked at `/Users/IAn/Agent/node_modules.ai-enterprise-temp`; the validation script restores and re-parks them automatically
- `DASHBOARD_ADMIN_KEY` and `IAN_AUTONOMY_KEY` can be supplied for live usage, but tests seed their own values
- remote validation will auto-load cPanel SSH settings from `AI-Enterprise/.env.local`, `AI-Enterprise/.env`, or the source `IAn/.env` when available

## Operational Checks

- `/` loads the backend-served SPA
- `/programs`, `/orchestration`, `/agents/configs`, `/report`, `/secrets`, and `/settings` deep-link directly
- `/api/*` routes still behave like API routes and are not intercepted by SPA fallback
- end-to-end cutover test proves `father -> artisan-master-owned governor -> artisan specialist -> engineer specialist`

## Failure Notes

- If `dist/index.html` is missing, run the validation script or `npm run build` first.
- If frontend tooling is unavailable, confirm dependencies exist either in `AI-Enterprise/node_modules` or `/Users/IAn/Agent/node_modules.ai-enterprise-temp`.
- If backend tests fail because `node_modules` exists in the target root, rerun `bash scripts/validate_ai_enterprise.sh`; it re-parks dependencies before the Python suite.
- If remote checks skip, provide the cPanel SSH variables in `AI-Enterprise/.env.local` or reuse the source-system `.env`.
