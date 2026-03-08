# Codebase Structure

**Analysis Date:** 2026-03-08

## Canonical Root Layout

```text
AI-Enterprise/
|-- .planning/        # GSD project state and codebase map
|-- agents/           # IAn, Engineer, program masters, specialists
|-- api/              # FastAPI app, routes, services, DB, auth
|-- dist/             # Built frontend bundle served by the API
|-- docs/             # Architecture, security, governance, rollout docs
|-- ops/              # Repository topology and systemd units
|-- programs/         # Managed program payloads and archive/context material
|-- scripts/          # Validation, remote checks, launchers, provisioning
|-- src/              # React/TypeScript mission-control SPA source
|-- tests/            # Python contract and phase tests
|-- PLAN.md           # Product/master plan
|-- SECRETS-MANIFEST.md
|-- requirements.txt
|-- package.json
|-- tsconfig.json
`-- vite.config.ts
```

## Canonical Source Directories

**`api/`**
- Purpose: backend runtime and all server-side contracts
- Important subdirs: `routes/`, `system/`, `db/`, `security/`, `agent/`
- Entry files: `api/app.py`, `api/bootstrap.py`, `api/config.py`

**`src/`**
- Purpose: source of truth for the mission-control SPA
- Important subdirs: `components/`, `lib/`, `styles/`, `test/`
- Entry files: `src/main.tsx`, `src/App.tsx`

**`agents/`**
- Purpose: canonical identity/context packets for IAn, Engineer, masters, and specialists
- Used by the runtime for hierarchy, coverage, and token estimates

**`tests/`**
- Purpose: backend/API contracts, security, live-cutover, phase-specific regression checks
- Important subdir: `tests/api/`

**`docs/`**
- Purpose: operational and architectural truth outside code
- Key docs: security model, infrastructure topology, repository governance, cPanel runtime contract, autonomy executor host

**`ops/`**
- Purpose: machine-readable infra policy and service definitions
- Key files: `ops/repository-topology.json`, `ops/systemd/*`

## Generated Or Runtime Directories

**`dist/`**
- Generated frontend output
- Served directly by FastAPI
- Not source of truth for UI implementation

**SQLite files**
- `ai_enterprise.db`, `ai_enterprise.db-wal`, `ai_enterprise.db-shm`
- Runtime state only
- Ignored by Git

**`.planning/`**
- Project planning state is now correctly local to `AI-Enterprise`
- This is the live GSD root, not the archived source project

## Managed Payload Directories

**`programs/`**
- Purpose: governed portfolio payloads, archive-carried contexts, and migration-hold material
- Important top-level branches:
  - `programs/artisan/`
  - `programs/baltzer/`
  - `programs/ian-agency/`
  - `programs/lavprishjemmeside/`
  - `programs/personal-assistant/`

Important nuance:
- `programs/ian-agency/contexts/samlino/seo-agent-playground` is partially embedded into the control plane as mapped context and runtime reference material
- not every directory under `programs/` is part of the main runtime

## Top-Level Operational Files

- `.env.example`: canonical env-name contract
- `PLAN.md`: product/master plan for the clean build
- `SECRETS-MANIFEST.md`: secret inventory without values
- `requirements.txt`: Python dependency entrypoint
- `package.json`: frontend dependency/build entrypoint

## Structure Drift And Oddities

- `api/config/application_catalog.json` still describes some `backend/*` and `backend/static/*` locations from the original source project
- `scripts/_cpanel_common.sh` and `scripts/_git_governance_common.sh` still fall back to `../IAn/.env*` if repo-local env files are missing
- The repo intentionally mixes source, docs, policy, generated bundle, and runtime database files at the top level, but generated/runtime files are ignored by Git

## External Workspace Expectations

The repo itself is canonical, but `ops/repository-topology.json` expects the wider workspace to provide:
- `/Users/IAn/Agent/AI-Enterprise` as the main repo
- `/Users/IAn/Agent/sites` for independent live-surface clones
- `/Users/IAn/Agent/archive` for non-live material

Those sibling paths are part of the operational model, not part of the codebase root itself.
