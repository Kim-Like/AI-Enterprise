# Technology Stack

**Analysis Date:** 2026-03-08

## Languages

**Primary:**
- Python 3.x - Control-plane backend, agent runtime, registry sync, and persistence access in `backend/`
- TypeScript 5.x - Control-plane frontend in `frontend/src/`

**Secondary:**
- JavaScript - Build config and managed program runtimes such as `frontend/vite.config.ts`, `programs/artisan/reporting.theartisan.dk/app.js`, and `scripts/*.sh`
- SQL - SQLite schema and data bootstrapping in `backend/db/schema.sql`
- Markdown - Agent canonical files under `father/`, `engineer/`, `masters/`, and operational docs under `README/`
- PHP - Managed WordPress payload under `programs/artisan/the-artisan-wp/`

## Runtime

**Environment:**
- Python virtualenv runtime - App boot uses `.venv` through `scripts/run_prod.sh`
- Node.js runtime - Required for `frontend/` and several managed programs; no repo-pinned Node version file was found
- Browser runtime - React SPA served from `backend/static/ui/`

**Package Manager:**
- pip via `requirements.txt` - Backend dependency entrypoint; versions are mostly unpinned
- npm - Frontend and managed program package manager
- Lockfiles: `frontend/package-lock.json` and several nested `package-lock.json` files under `programs/`

## Frameworks

**Core:**
- FastAPI - HTTP server and route composition in `backend/main.py`
- Uvicorn - ASGI runtime launched by `scripts/run_prod.sh`
- Pydantic 2.x - Request and response models in backend routes
- React 18.3 - SPA shell and routed pages in `frontend/src/`
- React Router 6.30 - Frontend route handling in `frontend/src/App.tsx`
- Tailwind CSS 3.4 - Utility styling in `frontend/tailwind.config.js` and `frontend/src/styles/`

**Testing:**
- pytest - Root test runner configured by `pytest.ini`
- FastAPI `TestClient` - Backend integration-style API tests under `tests/`
- Managed-program local test stacks also exist, for example Node test scripts in `programs/artisan/reporting.theartisan.dk/package.json` and Vitest in `programs/baltzer/TCG-index/package.json`

**Build/Dev:**
- Vite 5.4 - Frontend bundling in `frontend/vite.config.ts`
- TypeScript 5.7 - Control-plane compile/typecheck in `frontend/package.json` and `frontend/tsconfig.json`
- PostCSS + Autoprefixer - CSS pipeline in `frontend/postcss.config.js`

## Key Dependencies

**Critical:**
- `fastapi` - API routing, dependency injection, and response handling from `requirements.txt`
- `uvicorn[standard]` - Production/dev server process from `requirements.txt`
- `pydantic>=2.0` - Request model validation from `requirements.txt`
- `python-dotenv` - Root `.env` loading in `backend/config.py`
- `react` / `react-dom` - SPA rendering in `frontend/package.json`
- `react-router-dom` - Client routing in `frontend/package.json`
- `typescript` - Strict frontend typing in `frontend/package.json`
- `vite` - Frontend build pipeline in `frontend/package.json`
- `tailwindcss` - Frontend design-token and utility system in `frontend/package.json`

**Infrastructure:**
- SQLite - Control-plane state store at `father.db`, initialized by `backend/db/client.py`
- JSON config catalogs - Runtime metadata in `backend/config/application_catalog.json`, `backend/config/stack_profiles.json`, and related files
- Markdown agent packets - Canonical agent behavior loaded from `father/`, `engineer/`, and `masters/`

## Configuration

**Environment:**
- Root configuration is file-based through `.env` and `.env.example`, loaded by `backend/config.py`
- Required config categories include server boot (`HOST`, `PORT`, `DB_PATH`), write auth (`DASHBOARD_ADMIN_KEY`, `IAN_AUTONOMY_*`), model selection (`DEFAULT_MODEL_PROVIDER`, `DEFAULT_MODEL`, `CLAUDE_*`), and portfolio integrations (database, SSH, Billy, Supabase, Shopify)
- Frontend does not use a separate build-time env layer for the control plane; it relies on same-origin API calls from `frontend/src/api/client.ts`

**Build:**
- `frontend/vite.config.ts` - Frontend build output targets `backend/static/ui`
- `frontend/tsconfig.json` - Strict TypeScript settings for the control-plane SPA
- `frontend/tailwind.config.js` and `frontend/postcss.config.js` - Styling pipeline
- `backend/db/schema.sql` - Database schema and seeded registry data

## Platform Requirements

**Development:**
- macOS or Linux-like shell environment
- Python virtualenv with dependencies from `requirements.txt`
- Node/npm for `frontend/` and managed-program builds
- Optional local access to Claude CLI and remote SSH-backed integrations for full feature coverage

**Production:**
- Long-running Python process managed through `deploy/systemd/ian-father-agent.service` or `deploy/launchd/com.ian.father-agent.plist.example`
- Built frontend assets served from `backend/static/ui/`
- SQLite write access for `father.db`, plus optional external connectivity for cPanel, Billy, Supabase, and Shopify-backed programs

## Managed Program Sub-Stacks

- `programs/artisan/reporting.theartisan.dk/` - Node + Express + EJS + MySQL (`express`, `ejs`, `mysql2`)
- `programs/artisan/the-artisan-wp/` - WordPress/PHP/WooCommerce payload controlled through the control plane
- `programs/baltzer/TCG-index/` - React + Vite + Supabase + Vitest local app stack
- `programs/samlino/seo-agent-playground/` - React + Vite frontend with Python runtime sidecars and local SQLite

---

*Stack analysis: 2026-03-08*
*Update after major dependency changes*
