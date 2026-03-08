# Codebase Structure

**Analysis Date:** 2026-03-08

## Directory Layout

```text
IAn/
|-- backend/            # FastAPI app, routes, services, DB, auth, static hosting
|-- frontend/           # React/Vite control-plane SPA source
|-- father/             # Father agent canonical files
|-- engineer/           # Engineer agent canonical files and specialist tasks
|-- masters/            # Program masters and specialist task folders
|-- programs/           # Managed portfolio applications and placeholders
|-- tests/              # Root pytest suite
|-- scripts/            # Runbooks, bootstrap, and operational scripts
|-- deploy/             # systemd/launchd deployment examples
|-- README/             # Product and operational documentation
|-- ops/                # Operational support material
|-- .planning/codebase/ # Generated codebase map documents
|-- father.db           # Primary SQLite runtime state
|-- requirements.txt    # Python dependency entrypoint
|-- pytest.ini          # Pytest configuration
|-- .env.example        # Environment-variable names and examples
`-- .gitignore          # Current ignore rules
```

## Directory Purposes

**`backend/`:**
- Purpose: Control-plane backend implementation
- Contains: `agent/`, `routes/`, `system/`, `db/`, `security/`, `middleware/`, `config/`, and `static/`
- Key files: `backend/main.py`, `backend/config.py`, `backend/db/schema.sql`
- Subdirectories:
  - `backend/routes/` - HTTP endpoints
  - `backend/system/` - domain and orchestration services
  - `backend/agent/` - agent runtime and identity loading
  - `backend/static/ui/` - compiled frontend bundle served to operators

**`frontend/`:**
- Purpose: Source of truth for the control-plane SPA
- Contains: `src/`, Vite config, Tailwind config, TS config, and npm manifest
- Key files: `frontend/package.json`, `frontend/src/App.tsx`, `frontend/vite.config.ts`
- Subdirectories:
  - `frontend/src/api/` - frontend API clients
  - `frontend/src/pages/` - routed screens
  - `frontend/src/components/` - reusable UI
  - `frontend/src/types/` - shared TS types

**`father/`, `engineer/`, `masters/`:**
- Purpose: Canonical agent identity packets and task-specialist definitions
- Contains: `soul.md`, `user.md`, `agents.md`, `skills.md`, `tools.md`, `heartbeat.md`, `ARCHITECTURE.md`, `memory.md` in varying completeness
- Key files: `father/ARCHITECTURE.md`, `engineer/tools.md`, `masters/*/tasks/*/skills.md`
- Subdirectories:
  - `engineer/tasks/` - engineer specialists
  - `masters/*/tasks/` - program specialists

**`programs/`:**
- Purpose: Managed portfolio applications and placeholder program roots
- Contains: real apps, placeholders, incubators, and program-specific runtimes
- Key files: `programs/artisan/reporting.theartisan.dk/app.js`, `programs/baltzer/TCG-index/package.json`, `programs/samlino/seo-agent-playground/package.json`
- Subdirectories:
  - `programs/samlino/seo-agent-playground/runtime/` is partially embedded into the control plane because backend runtime modules load from it directly

**`tests/`:**
- Purpose: Root backend/API contract tests
- Contains: `test_*.py` files
- Key files: `tests/test_control_ui_v21.py`, `tests/test_chat_v2.py`, `tests/test_specialists_runtime.py`

**`README/`, `scripts/`, `deploy/`, `ops/`:**
- Purpose: Documentation, operations scripts, deployment files, and support artifacts
- Key files: `README/Introduction.md`, `scripts/run_prod.sh`, `deploy/systemd/ian-father-agent.service`

## Key File Locations

**Entry Points:**
- `backend/main.py`: FastAPI startup and route/static registration
- `frontend/src/main.tsx`: React frontend bootstrap
- `scripts/run_prod.sh`: Production backend launcher

**Configuration:**
- `.env.example`: Root env template
- `backend/config.py`: Runtime env loading and path constants
- `backend/config/application_catalog.json`: Cataloged application metadata
- `frontend/vite.config.ts`: Frontend build output configuration
- `frontend/tsconfig.json`: Frontend compiler rules

**Core Logic:**
- `backend/routes/`: HTTP endpoints
- `backend/system/`: service layer and orchestration logic
- `backend/agent/`: agent runtime and ownership rules
- `backend/db/`: DB client and schema

**Testing:**
- `tests/`: Root pytest suite
- `programs/artisan/reporting.theartisan.dk/tests/`: Managed-program Node tests

**Documentation:**
- `README/`: Human-facing repository documentation
- `father/`, `engineer/`, `masters/`: Agent-facing Markdown docs
- `.planning/codebase/`: Generated map output

## Naming Conventions

**Files:**
- `snake_case.py` for most Python backend modules
- `PascalCase.tsx` for React pages/components such as `FloorPage.tsx` and `WorkspaceShell.tsx`
- `test_*.py` for root pytest files
- Canonical agent files use fixed names like `soul.md`, `skills.md`, and `ARCHITECTURE.md`

**Directories:**
- Lowercase domain directories at the top level
- Program roots grouped by client/domain under `programs/`
- Specialist folders use task-oriented names under `engineer/tasks/` and `masters/*/tasks/`

**Special Patterns:**
- `backend/routes/*` mirrors API domain groupings
- `backend/system/*` holds the corresponding service logic
- `frontend/src/api/*` mirrors backend API surfaces used by the SPA

## Where to Add New Code

**New Backend Feature:**
- Primary code: `backend/routes/` plus `backend/system/`
- Tests: `tests/`
- Config if needed: `backend/config/` or `.env.example`

**New Frontend Screen:**
- Implementation: `frontend/src/pages/`
- Shared UI: `frontend/src/components/`
- API client: `frontend/src/api/`
- Types: `frontend/src/types/`

**New Agent or Specialist:**
- Canonical files: `father/`, `engineer/`, or `masters/<program-master>/tasks/<task>/`
- Runtime support: `backend/agent/` and `backend/system/specialist_service.py`

**New Managed Program Registration:**
- Payload: `programs/<client>/<app>/`
- Catalog/registry metadata: `backend/config/application_catalog.json` and registry sync logic

## Special Directories

**`backend/static/ui/`:**
- Purpose: Generated frontend build output currently served by FastAPI
- Source: Built from `frontend/`
- Committed: Yes in the current tree, but it should not be treated as the source of truth

**`father.db`:**
- Purpose: Primary runtime database
- Source: Created/managed by app startup and `backend/db/client.py`
- Committed: Ignored by `.gitignore`

**`logs/` and `backups/`:**
- Purpose: Operational artifacts and local state history
- Source: Runtime processes and manual operations
- Committed: Not part of first-party source-of-truth mapping

**`.planning/codebase/`:**
- Purpose: Generated codebase reference documents
- Source: `gsd-map-codebase` workflow
- Committed: Intended to be committed as docs once verified

---

*Structure analysis: 2026-03-08*
*Update when directory structure changes*
