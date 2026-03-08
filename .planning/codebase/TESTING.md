# Testing Patterns

**Analysis Date:** 2026-03-08

## Test Stack

**Backend**
- `pytest`
- FastAPI `TestClient`
- SQLite-backed app creation through `create_app()`

**Frontend**
- Vitest
- React Testing Library
- `@testing-library/user-event`
- `jsdom`

## Test Locations

**Python tests**
- `tests/api/test_autonomy_api.py`
- `tests/api/test_connection_status.py`
- `tests/api/test_control_ui_contracts.py`
- `tests/api/test_frontend_delivery.py`
- `tests/api/test_live_cutover.py`
- `tests/api/test_orchestration_contracts.py`
- `tests/api/test_registry_contracts.py`
- `tests/api/test_runtime_foundation.py`
- `tests/api/test_security_auth.py`
- `tests/test_agent_hierarchy.py`
- `tests/test_phase8_contracts.py`
- `tests/test_phase9_contracts.py`
- `tests/test_phase10_contracts.py`
- `tests/test_program_payloads.py`

**Frontend tests**
- `src/test/app-shell.test.tsx`
- `src/test/routes.test.tsx`

## Coverage Shape

- Backend coverage is strongest around API contracts, startup/bootstrap, security, registry sync, autonomy, and cutover checks
- Frontend coverage is thin but targeted at route rendering, shell navigation, and in-memory session handling
- There is no broad unit-test layer for every service module

## Common Test Patterns

**Backend**
- Build an app with `create_app(db_path_override=...)`
- Use temp SQLite databases per test or per file
- Assert route availability, JSON payload shape, and startup side effects
- Use `monkeypatch` for env overrides and auth scenarios

**Frontend**
- Render `AppRoutes` in `MemoryRouter`
- Wrap with `ControlSessionProvider`
- Mock `fetch` at the browser boundary
- Assert route rendering, redirects, and session/auth UX behavior

## Main Validation Commands

```bash
npm run test -- --run
npm run build
python3 -m pytest -p no:cacheprovider tests/api tests/test_agent_hierarchy.py tests/test_program_payloads.py tests/test_phase10_contracts.py -q
bash scripts/validate_ai_enterprise.sh
```

`scripts/validate_ai_enterprise.sh` is the real integration gate. It runs frontend tests, build, backend tests, autonomy validation, Git governance validation, and remote portfolio checks.

## Gaps

- No repo-local CI workflow currently enforces the validation script on push
- No explicit coverage threshold or coverage report config
- No lint/type-only gate beyond what TypeScript and the existing scripts naturally catch
- Large service modules are mostly protected by contract tests rather than fine-grained unit tests

## Risk Notes

- Some tests exercise real startup synchronization, which means boot behavior is covered but not fully isolated
- Validation still depends on environment and remote reachability for the deepest operational checks
- The suite is strong for regression on contracts, but weaker for localizing failures inside large service files
