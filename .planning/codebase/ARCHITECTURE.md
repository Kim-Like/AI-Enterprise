# Architecture

**Analysis Date:** 2026-03-08

## System Shape

AI-Enterprise is a single-repo control plane that serves a compiled React dashboard from a FastAPI backend while also owning agent packets, registry state, autonomy policy, and a portfolio of managed program payloads.

Canonical runtime entrypoints:
- `api/app.py`
- `api/bootstrap.py`
- `src/main.tsx`
- `scripts/serve_ai_enterprise.sh`
- `ops/systemd/ai-enterprise-api.service`
- `ops/systemd/ai-enterprise-autonomy.service`

## Primary Layers

**HTTP/API layer**
- Route modules live in `api/routes/`
- Main surfaces: health, meta, control-ui, orchestration, secrets, applications, autonomy, datastores, settings
- Routes are intentionally thin and delegate to `api/system/*`

**Domain/service layer**
- Core aggregation and behavior live in `api/system/`
- Important modules:
  - `control_ui_service.py`
  - `orchestration_service.py`
  - `program_registry.py`
  - `application_registry.py`
  - `connection_status.py`
  - `autonomy_service.py`

**Persistence and registry layer**
- Local SQLite via `api/db/client.py`
- Schema and seed tables in `api/db/schema.sql`
- Startup sync writes program registry, application registry, specialists, and autonomy topology into the DB

**Agent filesystem layer**
- Canonical agent packets live in `agents/`
- The API reads those files for coverage, context health, hierarchy, and routing support
- Agent identity loading is handled through `api/agent/`

**Frontend presentation layer**
- SPA source lives in `src/`
- Build output goes to `dist/`
- FastAPI serves `dist/index.html` and `dist/assets/*`
- Unknown HTML routes fall back to the SPA shell

**Autonomy and governance layer**
- Repo topology and deploy policy live in `ops/repository-topology.json`
- Autonomous repo provisioning and execution logic live in `api/system/autonomy_service.py`
- Host rollout is defined by docs plus systemd units

**Portfolio payload layer**
- Managed program material lives in `programs/`
- Some payloads are documentation/archive only, some are embedded references, and some point to independent live surfaces
- The portfolio is governed by registry metadata, not by importing every payload into the main runtime

## Startup Flow

1. `create_app()` in `api/app.py` calls `build_runtime()` from `api/bootstrap.py`
2. Settings are loaded from `.env`-style config via `api/config.py`
3. `DatabaseClient` initializes schema from `api/db/schema.sql`
4. `run_startup()` synchronizes:
   - program registry
   - application registry
   - specialist rows
   - autonomy topology state
5. FastAPI routers are mounted
6. `dist/` assets are mounted under `/assets`
7. top-level dashboard routes return `dist/index.html`

This means boot is not passive; it actively reconciles runtime state on every start.

## Request/Data Flow

**Dashboard read flow**
1. React route renders in `src/App.tsx`
2. Component calls `requestJson()` from `src/lib/api/client.ts`
3. Route in `api/routes/control_ui.py` validates auth
4. Service in `api/system/control_ui_service.py` combines DB, registry, and agent filesystem data
5. JSON returns to the SPA

**Autonomy/governance flow**
1. Request hits `api/routes/autonomy.py`
2. `api/system/autonomy_service.py` validates policy against `ops/repository-topology.json`
3. Service reads local Git state and optional GitHub provider state
4. Audit rows and sync rows are written into SQLite

**Secrets/connection flow**
1. Request hits `api/routes/secrets.py`
2. `api/system/connection_status.py` combines env presence, datastore verification, and optional live checks
3. Response returns redacted secret presence plus connection health

## Boundaries

**Canonical code boundary**
- Control plane: `api/`, `src/`, `agents/`, `ops/`, `scripts/`, `tests/`, `docs/`
- Managed payloads: `programs/`

**Operational boundary**
- GitHub/Git: code source of truth
- cPanel/SSH: deploy target and live remote check surface
- Tailscale host: planned always-on autonomy executor

**Brownfield carryover boundary**
- Some catalogs and shell helpers still reference legacy source-project locations
- Those references are compatibility/drift artifacts, not the intended long-term architecture

## Architectural Drift To Track

- `api/config/application_catalog.json` still contains some path metadata from the pre-duplication source layout
- `scripts/_cpanel_common.sh` and `scripts/_git_governance_common.sh` still allow fallback to archived `IAn` env files
- Portfolio payloads remain heterogeneous by design, so the registry layer is the normalizer rather than the payload directories themselves
