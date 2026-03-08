# Coding Conventions

**Analysis Date:** 2026-03-08

## Repo-Level Conventions

- Python backend code lives under `api/`
- React/TypeScript frontend code lives under `src/`
- Agent identity packets live under `agents/`
- Managed payloads live under `programs/`
- Top-level plans and operational docs live under `docs/`, `.planning/`, and root Markdown files

## Naming Patterns

**Python**
- Modules use `snake_case.py`
- Route handlers typically use `get_*`, `post_*`, `patch_*`
- Service helpers and local variables use `snake_case`
- Constants use `UPPER_SNAKE_CASE`

**TypeScript / React**
- Components use `PascalCase.tsx`
- Utility modules use lower-case or domain-style names such as `client.ts` and `control-session.tsx`
- Types and prop shapes use `PascalCase`
- Local variables and helpers use `camelCase`

**Agent packets**
- Canonical filenames are fixed:
  - `soul.md`
  - `user.md`
  - `agents.md`
  - `skills.md`
  - `tools.md`
  - `heartbeat.md`
  - `ARCHITECTURE.md`
  - `memory.md`

## Backend Conventions

- Route modules in `api/routes/` are intentionally thin
- Business logic lives in `api/system/*`
- Request models are Pydantic classes near the route definitions
- App/runtime boot is centralized through `api/app.py` and `api/bootstrap.py`
- Request handlers typically read shared dependencies from `request.app.state`

Common pattern:
1. authorize in route
2. parse request payload
3. delegate to service layer
4. return dict payloads

## Frontend Conventions

- Function components only
- React Router drives all page routing from `src/App.tsx`
- Same-origin fetch wrappers live in `src/lib/api/client.ts`
- Operator auth headers are composed by `src/lib/control-session.tsx`
- Styling uses CSS variables and authored CSS, not Tailwind, in the main control-plane app

## Typing And Validation

- TypeScript runs in strict mode via `tsconfig.json`
- Python code is annotated, but response payloads are often plain `dict[str, object]`
- Pydantic is used for API request validation
- Frontend validation is light and mostly inline rather than schema-library driven

## Error Handling

- Backend uses `HTTPException` at route and service boundaries
- Auth helpers centralize `401` and `503` write-access failures in `api/security/admin_auth.py`
- Frontend wraps failed requests in `ApiError`
- SPA fallback behavior for unknown HTML routes is handled in `api/app.py`

## Tooling And Enforcement

- No repo-wide ESLint, Prettier, Ruff, or MyPy config is currently enforcing style
- Conventions are enforced by example, tests, and validation scripts
- Canonical validation entrypoint is `scripts/validate_ai_enterprise.sh`

## Cross-Cutting Naming Drift

- `father`, `IAn`, and `ian-master` still coexist as compatibility names
- The runtime normalizes some of that naming inside service code rather than eliminating it everywhere
- This is a real naming convention wrinkle and should be treated as deliberate compatibility, not accidental style freedom

## Security-Conscious Conventions

- No client-side persistence of admin/autonomy keys
- No `localStorage`/`sessionStorage` auth pattern in the main app
- Secrets should appear only in env files and redacted status surfaces
- cPanel and Git/GitHub are treated as operational boundaries, not ad hoc source locations
