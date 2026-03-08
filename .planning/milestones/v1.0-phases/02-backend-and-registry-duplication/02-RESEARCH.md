# Phase 2: Backend And Registry Duplication - Research

**Researched:** 2026-03-08
**Domain:** Clean-slate FastAPI backend duplication with SQLite registry bootstrap
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- The clean duplicate root remains locked to `/Users/IAn/Agent/AI-Enterprise`.
- The clean backend should live under `AI-Enterprise/api/` rather than copying the source `backend/` layout wholesale.
- Duplicate the source FastAPI application-factory pattern, but move startup mutations out of `create_app()` into explicit bootstrap helpers.
- Preserve the SQLite/WAL runtime and schema-based bootstrap approach from `backend/db/client.py` and `backend/db/schema.sql`.
- Preserve `program_registry`, `application_registry`, `data_store_registry`, and master ownership semantics from the source system.
- Preserve canonical program IDs, application IDs, and master IDs exactly.
- Do not duplicate the source frontend, `backend/static/ui/`, generated assets, or any Vite/Tailwind build output in this phase.
- Do not duplicate portfolio program payloads or agent markdown packets yet; those belong to Phase 3.

### Claude's Discretion
- Exact module boundaries inside `AI-Enterprise/api/`
- Whether compatibility mapping lives in code, docs, or test fixtures so long as it is traceable
- Test file layout and fixture structure for the new backend foundation

### Deferred Ideas (OUT OF SCOPE)
- Full control-ui endpoint normalization belongs mostly to Phase 5
- Full agent packet duplication belongs to Phase 3
- Frontend rebuild belongs to Phase 6
- End-to-end live routing validation belongs to Phase 7

</user_constraints>

<research_summary>
## Summary

Phase 2 is a backend extraction problem, not a full-app clone. The source codebase already proves the right runtime primitives: FastAPI application factory, SQLite with WAL mode, schema bootstrapping, JSON-backed registry catalogs, and thin route modules backed by service code. The clean build should preserve those primitives while removing the biggest current risk: side-effectful startup behavior embedded directly inside `backend/main.py`.

The standard approach for this kind of brownfield duplication is to stand up a new minimal backend spine first, prove it boots cleanly, then port registry and compatibility contracts before moving on to higher-level orchestration and UI work. That means Phase 2 should produce a clean `AI-Enterprise/api/` package, a runtime config module, a database client plus schema, explicit bootstrap services, minimal health/meta routes, and registry sync logic wired behind startup boundaries.

**Primary recommendation:** Build the clean backend as a small, testable application core under `AI-Enterprise/api/`, keep source IDs and registry semantics intact, and isolate all source startup mutations behind explicit bootstrap helpers before duplicating any higher-level feature surface.
</research_summary>

<standard_stack>
## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | source current | HTTP runtime and app factory | Already proven in source and fits clean API package split |
| Uvicorn | source current | Local/dev ASGI serving | Matches source runtime and keeps boot path simple |
| sqlite3 | stdlib | Runtime persistence | Source schema and WAL model already depend on it |
| Pydantic | source current | Request/response validation | Already part of source dependency set |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | source current | Local env loading | Keep for parity with source `.env` behavior |
| pytest | source current | Backend foundation verification | Use immediately in Phase 2 for boot and registry tests |
| httpx | source current | API test client support | Use for route-level tests when needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SQLite bootstrap client | SQLAlchemy/Alembic | More abstraction, but unnecessary churn for a direct duplication phase |
| `api/` package | copy `backend/` as-is | Faster short term, but carries forward the legacy package boundary the clean build is trying to remove |
| implicit startup sync in `create_app()` | explicit bootstrap service | Slightly more code, but much safer and easier to test |

**Installation:**
```bash
pip install -r requirements.txt
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Structure
```text
AI-Enterprise/
├── api/
│   ├── app.py              # FastAPI app factory
│   ├── config.py           # env + path loading
│   ├── bootstrap.py        # explicit startup pipeline
│   ├── db/
│   │   ├── client.py
│   │   └── schema.sql
│   ├── routes/
│   │   ├── health.py
│   │   └── meta.py
│   ├── system/
│   │   ├── program_registry.py
│   │   └── application_registry.py
│   ├── agent/
│   │   ├── identity_loader.py
│   │   └── ownership_rules.py
│   └── security/
│       └── admin_auth.py
└── tests/
    └── api/
```

### Pattern 1: Explicit Bootstrap Pipeline
**What:** Keep app creation separate from runtime mutations like schema initialization, registry sync, and specialist sync.
**When to use:** Always in the clean build, especially where source code currently mutates on startup.
**Example:**
```python
def create_app() -> FastAPI:
    app = FastAPI(title="AI-Enterprise")
    app.state.runtime = build_runtime()
    register_routes(app)
    return app

def startup(app: FastAPI) -> None:
    runtime = app.state.runtime
    bootstrap_database(runtime.db)
    sync_registries(runtime.db, runtime.paths)
```

### Pattern 2: Catalog-Backed Registry Sync
**What:** Keep registry truth in versioned catalog/config files, then sync into SQLite.
**When to use:** For program, application, datastore, and ownership metadata that later phases will consume.
**Example:**
```python
catalog = load_catalog(paths.application_catalog)
for item in catalog:
    db.execute("INSERT ... ON CONFLICT(id) DO UPDATE SET ...", to_row(item))
```

### Pattern 3: Thin Route, Heavy Service
**What:** Routes should translate HTTP to service calls; registry/control logic stays in `api/system/*`.
**When to use:** For all duplicated endpoints in the clean backend.
**Example:**
```python
@router.get("/meta/runtime")
def get_runtime_meta(request: Request):
    return build_runtime_meta_payload(request.app)
```

### Anti-Patterns to Avoid
- **Startup work hidden in imports or app factory:** makes tests flaky and boot behavior opaque.
- **Copying source static UI coupling into backend foundation:** drags frontend concerns into a backend-only phase.
- **Reinventing IDs or ownership rules:** breaks traceability and later program/agent duplication.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DB access layer | new ORM abstraction | source-style SQLite client | source schema and sync code already assume direct SQL |
| env/config bootstrap | custom config framework | `python-dotenv` + simple config module | faster and closer to the source system |
| route compatibility tracking | manual memory-based notes | checked-in compatibility mapping doc/test fixture | later phases need traceable source-to-target contracts |
| startup orchestration | implicit side effects | explicit bootstrap module | easier to test and reason about |

**Key insight:** Phase 2 is about preserving proven runtime behavior with cleaner boundaries, not introducing a new backend architecture for its own sake.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Carrying source startup side effects forward unchanged
**What goes wrong:** app creation mutates the DB, syncs registries, and touches workspace state before tests or alternate runtimes can control it.
**Why it happens:** the source `backend/main.py` bundles bootstrap and HTTP wiring together.
**How to avoid:** separate runtime bootstrap into explicit functions and call them intentionally.
**Warning signs:** importing the app creates files, mutates DB contents, or warns about missing portfolio state.

### Pitfall 2: Leaking source paths into the clean target
**What goes wrong:** target code still points at `/Users/IAn/Agent/IAn` instead of its own root, making duplication false and fragile.
**Why it happens:** copied config or registry code assumes the source `PROJECT_ROOT`.
**How to avoid:** centralize root-path resolution in target config and test it against `/Users/IAn/Agent/AI-Enterprise`.
**Warning signs:** tests or runtime payloads return source repo paths from the target app.

### Pitfall 3: Copying generated or phase-later surfaces into Phase 2
**What goes wrong:** backend foundation becomes noisy with static assets, SPA routes, or unrelated feature modules.
**Why it happens:** bulk copying is faster than selective duplication.
**How to avoid:** duplicate only the planned foundation slice and verify excluded paths stay absent.
**Warning signs:** `AI-Enterprise/api/` contains UI assets, frontend bundles, or broad feature routes not referenced in Phase 2 plans.
</common_pitfalls>

<code_examples>
## Code Examples

Verified patterns from the source codebase:

### SQLite bootstrap
```python
with self._connect() as conn:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    if self.schema_path and Path(self.schema_path).exists():
        conn.executescript(Path(self.schema_path).read_text())
```
Source: `backend/db/client.py`

### Minimal health route
```python
@router.get("/health")
def health(request: Request):
    db = request.app.state.db
    count_row = db.fetch_one("SELECT COUNT(*) AS count FROM master_agents")
    return {"status": "ok", "db": "connected", "agents": count_row["count"] if count_row else 0}
```
Source: `backend/routes/health.py`

### Runtime meta route
```python
@router.get("/meta/runtime")
def get_runtime_meta(request: Request):
    app = request.app
    return {"status": "ok", "runtime_id": getattr(app.state, "runtime_id", "unknown")}
```
Source pattern: `backend/routes/meta.py`
</code_examples>

<sota_updates>
## State of the Art (2024-2025)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| monolithic app startup | explicit lifecycle/bootstrap modules | current backend best practice | lowers side effects and improves testability |
| backend serving SPA by default | API-first backend plus separate frontend app | already common by 2024 | aligns with the clean-slate frontend rebuild in later phases |
| ad hoc runtime metadata | structured health/meta endpoints | standard current ops practice | makes deployment and cutover checks easier |

**New tools/patterns to consider:**
- explicit startup modules rather than hidden app-factory side effects
- route and contract verification via tests instead of manual spot-checks

**Deprecated/outdated:**
- tying generated frontend bundles directly to the backend foundation in a duplication phase
- path resolution that assumes the original source repo is still the active runtime root
</sota_updates>

<open_questions>
## Open Questions

1. **How much of the control-ui route surface belongs in Phase 2 versus Phase 5?**
   - What we know: health/meta and foundational control-plane hooks are enough to prove backend runtime viability.
   - What's unclear: whether to carry one minimal control-ui overview endpoint into Phase 2.
   - Recommendation: keep Phase 2 to health/meta plus registry/control primitives; leave route normalization breadth to Phase 5.

2. **Should the clean backend duplicate all source schema tables immediately?**
   - What we know: later phases depend on registry, agents, tasking, and execution-history tables already defined in the source schema.
   - What's unclear: whether a trimmed schema would save effort now.
   - Recommendation: copy the full source schema first, then isolate usage through tests; schema drift is riskier than over-including at this stage.

3. **When should git task commits start?**
   - What we know: the current repo has no baseline commit and the worktree is fully untracked.
   - What's unclear: whether the user wants the initial baseline captured before implementation commits.
   - Recommendation: continue execution without atomic commits until a coherent baseline policy is established, but keep summaries and roadmap state accurate.
</open_questions>

## Validation Architecture

Phase 2 validation should prove duplicated backend viability and contract preservation:

- Verify `/Users/IAn/Agent/AI-Enterprise` exists and contains the planned `api/`, `tests/`, and manifest files.
- Verify the target app imports and `create_app()` registers `/health` and `/api/meta/runtime`.
- Verify the target DB bootstrap creates the source-critical tables: `master_agents`, `program_registry`, `data_store_registry`, and `application_registry`.
- Verify registry sync preserves canonical source IDs for programs and applications.
- Verify excluded assets stay excluded: no copied frontend bundle, no `backend/static/ui/`, no vendor trees, no nested `.git`.

<sources>
## Sources

### Primary (HIGH confidence)
- `.planning/codebase/ARCHITECTURE.md` - source backend boundaries and route surfaces
- `.planning/codebase/STRUCTURE.md` - source filesystem boundaries and exclusion rules
- `.planning/codebase/CONCERNS.md` - startup side effects and security risks to avoid copying forward
- `backend/main.py` - source app factory and startup side effects
- `backend/config.py` - source config contract
- `backend/db/client.py` and `backend/db/schema.sql` - runtime persistence foundation
- `backend/system/program_registry.py` and `backend/system/application_registry.py` - registry truth and sync logic
- `backend/agent/ownership_rules.py` and `backend/agent/identity_loader.py` - ownership and identity contracts

### Secondary (MEDIUM confidence)
- `.env.example` - source env naming baseline
- `requirements.txt` - current backend dependency floor

### Tertiary (LOW confidence - needs validation)
- None
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: FastAPI + SQLite backend duplication
- Ecosystem: source runtime config, DB bootstrap, registries, ownership rules
- Patterns: explicit bootstrap, thin routes, catalog-backed registries
- Pitfalls: startup mutations, path bleed, over-copying

**Confidence breakdown:**
- Standard stack: HIGH - directly confirmed in source dependencies
- Architecture: HIGH - directly confirmed in source backend files
- Pitfalls: HIGH - directly confirmed by source startup and codebase concerns
- Code examples: HIGH - taken from local source files

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
</metadata>

---

*Phase: 02-backend-and-registry-duplication*
*Research completed: 2026-03-08*
*Ready for planning: yes*
