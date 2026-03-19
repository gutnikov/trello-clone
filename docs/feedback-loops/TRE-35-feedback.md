# Feedback Loop Plan: TRE-35

## Overview

Verification strategy for the API scaffolding layer: router package creation, CORS middleware configuration, database lifespan management in `main.py`, and shared test fixtures in `conftest.py`. This issue establishes infrastructure that subsequent endpoint issues depend on, so verification focuses on correctness of app startup/shutdown lifecycle, CORS behavior, fixture availability, and non-regression of existing tests.

---

## 1. Unit Tests — CORS Middleware (`backend/tests/test_main.py`)

These tests verify that CORS middleware is correctly configured and responds with appropriate headers.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_cors_allows_any_origin_by_default` | A request with `Origin: http://example.com` receives `Access-Control-Allow-Origin: *` in the response (default dev config) |
| `test_cors_preflight_returns_200` | An `OPTIONS` request to `/health` with CORS headers returns 200 with `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers` |
| `test_cors_configured_origins_respected` | When `CORS_ORIGINS` env var is set to `http://localhost:3000`, only that origin is reflected in the response header (requires monkeypatching the env var and recreating the app, or testing via the env var mechanism) |

### Run Command

```bash
cd backend && uv run pytest tests/test_main.py -v -k cors
```

---

## 2. Unit Tests — Lifespan Lifecycle (`backend/tests/test_main.py`)

These tests verify the database lifespan context manager connects, initializes, seeds, and closes correctly.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_app_state_has_db_after_startup` | After the test client is created (which triggers lifespan), `app.state.db` is a `Database` instance |
| `test_lifespan_seeds_default_board` | After startup, querying the database via `app.state.db.list_boards()` returns at least one board |
| `test_health_endpoint_still_works` | `GET /health` returns `{"status": "ok", "version": "0.1.0"}` with status 200 — confirms existing functionality is preserved |

### Run Command

```bash
cd backend && uv run pytest tests/test_main.py -v -k lifespan
```

---

## 3. Integration Tests — Shared Fixtures (`backend/tests/test_conftest_fixtures.py`)

These tests verify that the shared `db` and `client` fixtures in `conftest.py` work correctly and are available to test modules.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_db_fixture_provides_connected_database` | The `db` fixture yields a `Database` instance; calling `db.list_boards()` succeeds without error |
| `test_db_fixture_has_seeded_board` | The `db` fixture includes a seeded default board; `db.list_boards()` returns a non-empty list |
| `test_client_fixture_provides_async_client` | The `client` fixture yields an `httpx.AsyncClient`; calling `client.get("/health")` returns status 200 |
| `test_client_fixture_uses_test_db` | The `client` fixture's app uses the in-memory test database, not a file-based database; `client.get` requests hit the test DB |
| `test_db_fixture_isolation` | Two test functions using the `db` fixture get independent database instances (mutations in one don't affect the other) |

### Run Command

```bash
cd backend && uv run pytest tests/test_conftest_fixtures.py -v
```

---

## 4. Non-Regression — Existing Tests

Verify that existing tests continue to pass after the changes to `main.py` and the addition of `conftest.py`.

### Test Cases

| Suite | Expected Behavior |
|---|---|
| `tests/test_smoke.py` | `test_smoke` still passes (trivial assert) |
| `tests/test_models.py` | All 12 model tests still pass (no changes to models) |
| `tests/test_database.py` | All 23 database CRUD tests still pass; the local `db` fixture in `test_database.py` takes precedence over the `conftest.py` `db` fixture (pytest local scope resolution) |

### Run Command

```bash
cd backend && uv run pytest -v
```

---

## 5. Static Analysis

### Type Checking

```bash
cd backend && uv run mypy src/app/main.py src/app/routers/__init__.py --strict
```

Verifies:
- The lifespan context manager has correct type annotations (`AsyncIterator[None]`)
- `app.state.db` access is properly typed (note: `app.state` is `Any` in Starlette, so this may need `# type: ignore` comments)
- CORS middleware configuration uses correct types
- All new code in `main.py` has full type annotations

### Linting

```bash
cd backend && uv run ruff check src/app/main.py src/app/routers/__init__.py tests/conftest.py
```

Verifies:
- Import ordering follows project conventions
- Line length <= 100 characters
- No unused imports or variables
- Async patterns are correct (ASYNC rules)

---

## 6. Observability Hooks

The lifespan and CORS changes include structured logging via `structlog` for runtime observability:

| Event | Log Level | Fields | Purpose |
|---|---|---|---|
| `cors_configured` | `info` | `allowed_origins` | Confirms CORS middleware is active and shows configured origins |
| `app_startup_complete` | `info` | `db_path` | Confirms lifespan startup completed: DB connected, schema initialized, board seeded |
| `app_shutdown_complete` | `info` | — | Confirms lifespan shutdown completed: DB connection closed |

These events complement the existing database-level logging (`database_connected`, `schema_initialized`, `default_board_seeded` from `database.py`) to provide a complete startup audit trail:

```
database_connected → schema_initialized → default_board_seeded → app_startup_complete
```

And on shutdown:
```
database_closed → app_shutdown_complete
```

---

## 7. Runtime Validation

- **CORS origins parsing:** If `CORS_ORIGINS` env var is set but contains invalid values (empty string, whitespace), the middleware should still function with sensible defaults. The implementation should strip whitespace from parsed origins.
- **Lifespan error handling:** If database connection fails during startup (e.g., invalid path, permissions), the exception should propagate and prevent the app from starting, rather than silently continuing with no database.
- **`app.state.db` availability:** Route handlers accessing `app.state.db` should get a connected `Database` instance. If accessed before lifespan runs (which shouldn't happen in normal FastAPI flow), they'd get an `AttributeError` — this is acceptable as it indicates a configuration error.
- **Fixture cleanup:** The `conftest.py` fixtures use try/finally or yield patterns to ensure database connections are always closed, even if a test fails.

---

## Feedback Completeness Score

| Dimension | Score (0-2) | Justification |
|---|---|---|
| Unit tests — CORS | 2 | 3 test cases covering default config, preflight, and env-configured origins |
| Unit tests — lifespan | 1 | 3 test cases covering DB availability, seed state, and health endpoint non-regression |
| Integration tests — fixtures | 2 | 5 test cases verifying both fixtures work, are isolated, and use test DB |
| Non-regression | 1 | Full existing test suite re-run to verify no breakage |
| Static analysis | 1 | mypy strict + ruff linting on all new/modified files |
| Observability | 1 | 3 structured log events for startup/shutdown audit trail |
| Runtime validation | 1 | CORS parsing robustness, lifespan error propagation, fixture cleanup |

**Total feedback_completeness_score: 9/10**

The score of 9 exceeds the minimum threshold of 6. The high score reflects that this issue is foundational infrastructure where thorough verification is critical — downstream endpoint issues depend on CORS, lifespan, and test fixtures all working correctly. E2e tests are not applicable since there are no user-facing endpoints added by this issue (the `/health` endpoint already exists).
