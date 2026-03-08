# Technology Stack

**Analysis Date:** 2026-03-08

## Canonical Runtime

- Canonical repo root: `AI-Enterprise/`
- Backend runtime: Python FastAPI app in `api/`
- Frontend runtime: React 18 + TypeScript SPA in `src/`
- Delivery model: frontend is built into `dist/` and served by `api/app.py`
- Local launcher: `scripts/serve_ai_enterprise.sh`
- Production host model: systemd services in `ops/systemd/`

## Languages

**Primary**
- Python: API routes, startup/bootstrap, registry sync, autonomy runtime, SQLite access
- TypeScript: mission-control SPA, route components, API client, operator session state

**Secondary**
- SQL: schema bootstrap in `api/db/schema.sql`
- Bash: validation, remote checks, Git governance, autonomy executor launch
- JSON: application catalog, topology manifest, runtime config
- CSS: design tokens and app styles in `src/styles/`
- Markdown: planning, agent canonical files, operational docs

## Backend Stack

- FastAPI in `api/app.py`
- Uvicorn as the ASGI server via `python3 -m uvicorn api.app:create_app --factory`
- Pydantic v2 request models across route modules
- `python-dotenv`-driven settings load in `api/config.py`
- SQLite with WAL-backed schema bootstrap via `api/db/client.py`

Backend dependency entrypoint:
- `requirements.txt`

Important backend modules:
- `api/bootstrap.py`
- `api/routes/`
- `api/system/`
- `api/security/admin_auth.py`
- `api/db/schema.sql`

## Frontend Stack

- React 18
- React Router 6
- Vite 5
- TypeScript 5.7
- Vitest + Testing Library
- `@fontsource/dm-sans` and `@fontsource/ibm-plex-mono`

The live frontend does **not** use Tailwind. The control-plane UI is styled with plain CSS in:
- `src/styles/tokens.css`
- `src/styles/app.css`

Frontend dependency and build entrypoints:
- `package.json`
- `vite.config.ts`
- `tsconfig.json`
- `src/main.tsx`
- `src/App.tsx`

## Storage And State

- Primary runtime store: local SQLite database at `ai_enterprise.db` via `DB_PATH`
- Schema bootstrap: `api/db/schema.sql`
- Registry/state sync on startup: `api/bootstrap.py`
- Agent identity/state content: filesystem canonical files under `agents/`
- Built frontend output: `dist/`

## Auth And Operator Session

- Server auth model: shared headers `X-Admin-Key` and `X-Autonomy-Key`
- Enforcement: `api/security/admin_auth.py`
- Frontend session storage: in-memory React context only in `src/lib/control-session.tsx`
- Browser `localStorage` and `sessionStorage` use is treated as forbidden by `scripts/validate_ai_enterprise.sh`

## External And Portfolio Sub-Stacks

The control plane manages or inventories downstream stacks that are not part of the main runtime:
- Node/Express/EJS payloads under `programs/artisan/` and `programs/baltzer/`
- WordPress/PHP payload under `programs/artisan/the-artisan-wp`
- Shopify-backed operational surface declared in the registry
- Samlino archive/context workspace under `programs/ian-agency/contexts/samlino/`

Some portfolio payloads still use Tailwind or different local stacks, but that is payload-specific and not part of the main mission-control frontend.

## Build And Validation Commands

```bash
npm run test -- --run
npm run build
python3 -m pytest -p no:cacheprovider tests/api tests/test_agent_hierarchy.py tests/test_program_payloads.py tests/test_phase10_contracts.py -q
bash scripts/validate_ai_enterprise.sh
bash scripts/serve_ai_enterprise.sh
```

## Drift Notes

- Older codebase-map docs that describe `backend/`, `frontend/`, Tailwind, or browser-persisted keys are stale.
- `api/config/application_catalog.json` still carries some brownfield-era path metadata for `ian-mission-control`.
- The canonical control-plane stack is now `api/` + `src/` + `dist/`, not the original source-project layout.
