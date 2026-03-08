# Coding Conventions

**Analysis Date:** 2026-03-08

## Naming Patterns

**Files:**
- Python backend modules use `snake_case.py`, for example `backend/system/chat_service.py`
- React pages and components use `PascalCase.tsx`, for example `frontend/src/pages/FloorPage.tsx` and `frontend/src/components/layout/WorkspaceShell.tsx`
- Root tests use `test_*.py` in `tests/`
- Agent canonical files use fixed names rather than stylistic freedom: `soul.md`, `user.md`, `agents.md`, `skills.md`, `tools.md`, `heartbeat.md`, `ARCHITECTURE.md`, `memory.md`

**Functions:**
- Backend route handlers frequently use HTTP verb prefixes such as `get_*`, `post_*`, and `patch_*` in `backend/routes/`
- Python service helpers use `snake_case`
- Frontend helpers use `camelCase`, while React components use `PascalCase`

**Variables:**
- Python constants are typically `UPPER_SNAKE_CASE`, for example values in `backend/config.py`
- Python local variables and function names are `snake_case`
- TypeScript variables and helpers are `camelCase`

**Types:**
- Pydantic models and TypeScript types/interfaces are `PascalCase`
- There is no `I` prefix convention for interfaces in the frontend

## Code Style

**Formatting:**
- Python follows conventional 4-space formatting with module docstrings and type hints, as seen in `backend/main.py` and `backend/routes/chat.py`
- Frontend TypeScript uses semicolons, double quotes, and strict compiler checks from `frontend/tsconfig.json`
- Utility-first Tailwind classes are mixed with CSS variable layers in `frontend/src/styles/`

**Linting:**
- There is no repo-wide lint/format configuration enforcing one standard across Python and TypeScript
- The root control-plane frontend package does not expose a `lint` script in `frontend/package.json`
- Some managed programs do have their own lint/test scripts, but those are local to each payload

## Import Organization

**Order:**
1. Python standard library imports
2. Third-party packages
3. Local `backend.*` imports
4. Relative imports where needed

**Grouping:**
- Python files generally use blank lines between import groups
- Frontend files usually import React/router packages first, then local modules

**Path Aliases:**
- No frontend path alias like `@/` was found in the control-plane app
- Imports are relative or package-based

## Error Handling

**Patterns:**
- Backend routes usually validate at the boundary, then delegate to services and raise/propagate `HTTPException` or runtime errors
- Shared write auth helpers live in `backend/security/admin_auth.py`
- Frontend fetch failures are normalized into `ApiError` in `frontend/src/api/client.ts`

**Error Types:**
- Route-level validation errors are handled near API boundaries
- Service-layer failures often bubble upward and are captured by `ErrorCaptureMiddleware`
- Startup sync code sometimes catches exceptions and logs warnings instead of failing hard

## Logging

**Framework:**
- Python `logging` is the primary logging mechanism
- Error capture is augmented by `backend/middleware/error_capture.py` and DB-backed error storage

**Patterns:**
- Logging is more common at service boundaries and startup than in utility code
- Frontend uses very light custom error wrapping rather than a dedicated logging framework

## Comments

**When to Comment:**
- Python modules often begin with short docstrings such as `\"\"\"FastAPI entry point.\"\"\"`
- Comments are used sparingly; most intent is carried by function and module names
- Markdown canonical files carry much of the higher-level behavioral documentation outside code

**JSDoc/TSDoc:**
- Not used consistently in the control-plane frontend

**TODO Comments:**
- No strong repository-wide TODO annotation convention was found

## Function Design

**Size:**
- Route handlers tend to stay relatively thin
- Service functions and service modules can become very large, especially in `backend/system/`

**Parameters:**
- Backend APIs prefer typed request models at the boundary
- Frontend helpers generally take small explicit argument lists

**Return Values:**
- Python code commonly returns dictionaries/JSON-ready structures from services
- Frontend request helpers return typed promises and throw on non-OK responses

## Module Design

**Exports:**
- Python modules export functions and constants directly
- Frontend React files mostly use named exports, with `App.tsx` as a clear default-export exception

**Barrel Files:**
- The control-plane frontend does not rely heavily on barrel exports
- Directory structure itself is used as the main organization mechanism

## Repository-Specific Conventions To Preserve

- Keep route modules in `backend/routes/` thin and push aggregation logic into `backend/system/`
- Keep agent identity data in canonical Markdown files rather than embedding it in Python
- Preserve the current alias normalization rule where legacy `ian` and `ian-master` inputs may resolve to `father`, but document and isolate that behavior because it is a naming inconsistency
- Treat `frontend/` as the only source of truth for UI code even though generated output also exists in `backend/static/ui/`

---

*Convention analysis: 2026-03-08*
*Update when patterns change*
