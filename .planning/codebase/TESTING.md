# Testing Patterns

**Analysis Date:** 2026-03-08

## Test Framework

**Runner:**
- `pytest` from `requirements.txt`
- Root config in `pytest.ini`

**Assertion Library:**
- Built-in Python `assert`
- FastAPI `TestClient` for HTTP assertions

**Run Commands:**
```bash
pytest -q                                  # Run all root tests
pytest -q tests/test_control_ui_v21.py     # Run one file
pytest -q tests/test_db.py::test_*         # Run selected tests
```

## Test File Organization

**Location:**
- Root tests live in `tests/`
- Naming pattern is `test_*.py`

**Naming:**
- API and UI contract tests: `tests/test_control_ui_v21.py`, `tests/test_workspace_ui_routes.py`
- Runtime/service tests: `tests/test_specialists_runtime.py`, `tests/test_chat_v2.py`
- DB/bootstrap tests: `tests/test_db.py`

**Structure:**
```text
tests/
|-- test_chat_v2.py
|-- test_control_ui_v21.py
|-- test_db.py
|-- test_specialists_runtime.py
`-- ...
```

## Test Structure

**Suite Organization:**
```python
client = TestClient(create_app())

def test_example_behavior():
    response = client.get("/api/...")
    assert response.status_code == 200
```

**Patterns:**
- Many files create a module-level `TestClient(create_app())`
- Tests are plain `def test_*` functions rather than class-based suites
- Arrange/act/assert is used informally, not through a strict fixture framework
- `monkeypatch` is used where env or runtime behavior must be altered

## Mocking

**Framework:**
- pytest `monkeypatch`
- Direct patching/substitution of env vars and service behaviors

**Patterns:**
```python
def test_something(monkeypatch):
    monkeypatch.setenv("KEY", "value")
    response = client.get("/api/...")
    assert response.status_code == 200
```

**What to Mock:**
- Environment variables
- External or expensive runtime behavior
- Some service-layer functions when isolating a route or policy edge case

**What NOT to Mock:**
- Much of the SQLite-backed control-plane logic currently runs against the app's real startup path
- The codebase favors integration-style tests over pure unit isolation

## Fixtures and Factories

**Test Data:**
- Most data setup is inline inside each test file
- There is no strong shared `tests/fixtures/` or `tests/factories/` convention in the root suite

**Location:**
- Inline helper functions and temporary data inside test modules
- Some tests use real repo paths and clean them up afterward rather than using isolated fixture directories

## Coverage

**Requirements:**
- No explicit coverage threshold was found
- No coverage plugin or CI enforcement was found at the root

**Configuration:**
- `pytest.ini` only points test discovery at `tests/`
- Coverage is observational rather than enforced

**View Coverage:**
```bash
pytest -q
```

## Test Types

**Unit Tests:**
- Limited number of pure unit-style tests
- Most so-called unit coverage is still close to real DB/app boot behavior

**Integration Tests:**
- Dominant pattern in the root suite
- Tests commonly exercise `create_app()`, route handlers, DB interactions, and service behavior together

**E2E Tests:**
- No root frontend E2E framework such as Playwright was found for the control plane
- No frontend component/unit test setup was found in `frontend/`

## Common Patterns

**Async Testing:**
- Root tests are mostly synchronous through `TestClient`, even when underlying app code is async

**Error Testing:**
```python
response = client.post("/api/...", json={})
assert response.status_code == 401
```

**Snapshot Testing:**
- Not used in the root control-plane codebase

## Coverage Signals From Audit

- 15 root test files and 66 `test_*` functions were found under `tests/`
- Strongest coverage areas:
  - backend/API contracts
  - orchestration and specialist runtime behavior
  - auth and policy edges
  - DB bootstrap and schema behavior
- Weakest or missing areas:
  - frontend unit/component behavior
  - frontend route rendering
  - security-hardening regression tests
  - full external integration validation

## Risks In Current Test Design

- Tests are not fully hermetic because `create_app()` performs startup sync and DB/filesystem mutation on import/startup
- Some tests write to real repo paths, which raises the risk of local-state coupling
- Managed programs have their own local test stacks, but those are not part of a unified repository-wide test contract

---

*Testing analysis: 2026-03-08*
*Update when test patterns change*
