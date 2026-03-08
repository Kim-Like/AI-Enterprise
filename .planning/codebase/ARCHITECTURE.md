# Architecture

**Analysis Date:** 2026-03-08

## Pattern Overview

**Overall:** Service-centric control-plane monolith with a bundled SPA and embedded portfolio-program adapters

**Key Characteristics:**
- Single FastAPI application booted from `backend/main.py`
- SQLite-backed orchestration and registry state in `father.db`
- React SPA built from `frontend/` and served from `backend/static/ui/`
- Agent behavior loaded from filesystem canonical files under `father/`, `engineer/`, and `masters/`
- Managed program payloads live beside the control plane in `programs/`, with some directly integrated and others only cataloged

## Layers

**HTTP Route Layer:**
- Purpose: Define API surfaces and mount the SPA/static routes
- Contains: Thin route modules in `backend/routes/`
- Depends on: Service layer, auth helpers, request models
- Used by: Browser clients, tests, and local tooling

**Service / Domain Layer:**
- Purpose: Aggregate runtime state, execute orchestration logic, manage registries, and handle program-specific operations
- Contains: Large service modules in `backend/system/` such as `chat_service.py`, `control_ui_service.py`, `workspace_service.py`, and `program_registry.py`
- Depends on: DB layer, filesystem canonical files, env config, and external systems
- Used by: Route layer and startup bootstrapping

**Agent Runtime Layer:**
- Purpose: Load canonical files, resolve models/providers, and execute agent workflows
- Contains: `backend/agent/` including `base_agent.py`, `identity_loader.py`, provider integrations, and ownership rules
- Depends on: Filesystem agent packets, config, DB-backed state, and local CLI/provider access
- Used by: Chat, tasks, orchestration, and specialist routing

**Persistence / Registry Layer:**
- Purpose: Store tasks, threads, registries, execution history, and error records
- Contains: `backend/db/`, `father.db`, and seeded config assets like `backend/db/schema.sql` and `backend/config/*.json`
- Depends on: SQLite and filesystem-managed config files
- Used by: Startup sync, services, and tests

**Frontend Presentation Layer:**
- Purpose: Render the control UI and orchestrate calls into `/api/*`
- Contains: `frontend/src/api/`, `frontend/src/pages/`, `frontend/src/components/`, and `frontend/src/types/`
- Depends on: Browser runtime, routed backend APIs, and generated static output
- Used by: Operators using the control-plane UI

**Identity / Prompt Content Layer:**
- Purpose: Define agent identity, role boundaries, memory, and architecture context
- Contains: Markdown canonical files in `father/`, `engineer/`, and `masters/*/tasks/*`
- Depends on: Filesystem only
- Used by: Agent runtime, control UI audits, and orchestration logic

**Managed Program Boundary:**
- Purpose: Represent or control downstream applications owned by the system
- Contains: `programs/*`
- Depends on: Per-program stack and external infra
- Used by: Registry sync, workspace operations, and some runtime adapters

## Data Flow

**Application Bootstrap:**

1. `backend/main.py` creates the FastAPI app and DB client
2. `backend/config.py` loads `.env` and establishes project paths
3. Startup mutates runtime state through `backend/system/brain_files.py`, `backend/system/specialist_schema.py`, `backend/system/program_registry.py`, `backend/system/application_registry.py`, and `backend/system/specialist_service.py`
4. Route modules are mounted under `/api`
5. Static frontend assets are mounted from `backend/static/`
6. HTML routes fall back to the SPA entrypoint

**Control UI Request:**

1. A page in `frontend/src/App.tsx` renders inside `WorkspaceShell`
2. The page uses API helpers from `frontend/src/api/`
3. The backend route module in `backend/routes/` validates and forwards the request
4. A service module in `backend/system/` aggregates DB, filesystem, and registry state
5. JSON is returned to the SPA for rendering

**Chat / Orchestration Execution:**

1. A browser action or API client calls `/api/chat/*`, `/api/tasks/*`, or `/api/orchestration/*`
2. Services persist thread/task state in `father.db`
3. Agent runtime loads canonical files through `backend/agent/identity_loader.py`
4. Provider routing resolves model runtime and invokes local Claude tooling where needed
5. Results are written back to the DB and surfaced to the UI

**Workspace / Program Operation:**

1. A route in `backend/routes/workspace.py` or a program-specific route such as `backend/routes/samlino.py` is called
2. The service layer resolves ownership, registry metadata, and allowed operations
3. The backend interacts with local files, SQLite, or remote SSH-backed systems
4. Results are normalized and returned to the caller

**State Management:**
- Persistent state is primarily SQLite-backed through `father.db`
- Agent definitions and durable context are file-backed Markdown
- Program and application metadata are part DB seed data, part JSON config, and part filesystem discovery
- The frontend itself is largely stateless beyond browser storage of admin/autonomy headers

## Key Abstractions

**Agent Identity Packet:**
- Purpose: Define role, memory, tools, and architecture context for an agent
- Examples: `father/soul.md`, `engineer/tools.md`, `masters/artisan-master/ARCHITECTURE.md`
- Pattern: Filesystem-loaded canonical packet

**Registry Record:**
- Purpose: Describe programs, applications, datastores, and ownership
- Examples: rows seeded from `backend/db/schema.sql`, mirrored by `backend/system/program_registry.py` and `backend/system/application_registry.py`
- Pattern: DB-backed metadata registry synchronized at startup

**Control UI Aggregate Model:**
- Purpose: Combine disparate runtime and config sources into UI-ready payloads
- Examples: `backend/system/control_ui_service.py`
- Pattern: Service-level read models over DB + filesystem + runtime checks

**Task / Thread Record:**
- Purpose: Track orchestration work, chat state, and specialist activity
- Examples: task and chat tables in `father.db`, used by `backend/system/chat_service.py` and `backend/routes/tasks.py`
- Pattern: Durable workflow record with runtime backfill and enrichment

## Entry Points

**Backend App:**
- Location: `backend/main.py`
- Triggers: `uvicorn backend.main:app`, tests, or local server scripts
- Responsibilities: Startup sync, middleware, route registration, static mount

**Frontend App:**
- Location: `frontend/src/main.tsx`
- Triggers: Vite dev/build pipeline and browser load
- Responsibilities: Boot React app and route into `frontend/src/App.tsx`

**Production Launcher:**
- Location: `scripts/run_prod.sh`
- Triggers: systemd, launchd, or direct shell invocation
- Responsibilities: Activate venv and launch Uvicorn

**Managed Program Catalog:**
- Location: `backend/config/application_catalog.json`
- Triggers: startup sync and registry-driven discovery
- Responsibilities: Seed known application boundaries and entrypoints

## Error Handling

**Strategy:** Route-layer exceptions and runtime failures bubble into FastAPI handlers and `ErrorCaptureMiddleware`, with additional warnings logged during boot-time sync.

**Patterns:**
- Routes often let service exceptions surface as HTTP errors or captured runtime errors
- Startup catches and downgrades some failures to warnings rather than aborting boot
- Frontend wraps fetch failures into `ApiError` in `frontend/src/api/client.ts`

## Cross-Cutting Concerns

**Logging:**
- Python logging plus DB-backed error capture through `backend/middleware/error_capture.py`

**Validation:**
- Pydantic request models at API boundaries
- Additional policy validation in service code, for example orchestration boundary checks

**Authentication:**
- Shared header auth through `backend/security/admin_auth.py`
- No user/session/RBAC system was found for the control plane

**Clean-Slate Boundary To Preserve:**
- Keep the control plane (`backend/`, `frontend/`, agent packets, registry/persistence) distinct from managed portfolio payload (`programs/`)
- Preserve the current API, route, registry, and canonical-file contracts unless intentionally versioned during a rebuild

---

*Architecture analysis: 2026-03-08*
*Update when major patterns change*
