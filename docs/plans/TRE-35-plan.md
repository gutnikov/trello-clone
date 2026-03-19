# Implementation Plan: TRE-35

## Overview

Set up the foundational API infrastructure by creating the router package, adding CORS middleware and database lifespan management to the FastAPI app, and establishing shared pytest fixtures for all future API test modules. This work modifies one existing file (`main.py`) and creates two new files (`routers/__init__.py`, `tests/conftest.py`). All changes follow existing project conventions (Python 3.12, FastAPI, structlog, strict mypy, pytest-asyncio auto mode, ruff).

## Steps

### Step 1: Create the router package init file

- **Files:** `backend/src/app/routers/__init__.py` (new)
- **Changes:** Create the `routers/` directory and an empty `__init__.py` file. This establishes the package that future endpoint sub-issues will populate with individual router modules (e.g., `boards.py`, `lists.py`, `cards.py`). The file should contain only a module docstring for consistency with the project's convention of documenting file purpose.
- **Depends on:** None

### Step 2: Modify `main.py` — add CORS middleware

- **Files:** `backend/src/app/main.py` (modify)
- **Changes:**
  - Import `CORSMiddleware` from `fastapi.middleware.cors`.
  - Import `os` (for reading environment variables).
  - After the `FastAPI()` instantiation (currently line 8), add CORS middleware configuration:
    - Read allowed origins from `CORS_ORIGINS` environment variable (comma-separated string, e.g., `"http://localhost:3000,http://localhost:5173"`).
    - Default to `["*"]` when the environment variable is not set (dev mode — allow all origins).
    - Set `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
  - Use `app.add_middleware(CORSMiddleware, ...)` to register.
  - Log the configured origins at startup for observability.
- **Depends on:** Step 1 (routers package should exist before wiring the app, though CORS itself has no direct dependency)

### Step 3: Modify `main.py` — add lifespan context manager with DB lifecycle

- **Files:** `backend/src/app/main.py` (modify)
- **Changes:**
  - Import `contextlib.asynccontextmanager` and `collections.abc.AsyncIterator`.
  - Import `Database` from `app.database`.
  - Define an async lifespan context manager function `lifespan(app: FastAPI) -> AsyncIterator[None]`:
    - **Startup phase:**
      1. Read the database path from `DB_PATH` environment variable, defaulting to `"data/trello.db"`.
      2. Create a `Database(db_path)` instance.
      3. Call `await db.connect()`.
      4. Call `await db.init_schema()`.
      5. Call `await db.seed_default_board()`.
      6. Store the database instance on `app.state.db = db`.
      7. Log `"app_startup_complete"` with the db_path.
    - **Yield** — the app runs while the context manager is held open.
    - **Shutdown phase:**
      1. Call `await app.state.db.close()`.
      2. Log `"app_shutdown_complete"`.
  - Pass the lifespan to the `FastAPI()` constructor: `FastAPI(title="Trello Clone API", version="0.1.0", lifespan=lifespan)`.
  - Remove the module-level `setup_logging()` / `log = get_logger()` calls and move `setup_logging()` into the lifespan startup phase (before DB operations) so logging is configured before any structured log events fire. Alternatively, keep `setup_logging()` at module level since it's idempotent and logging setup should happen at import time for the `/health` endpoint to work even before lifespan runs — this is the preferred approach to maintain the existing behavior.
  - The `/health` endpoint remains unchanged.
- **Depends on:** Step 2 (CORS should be added first to keep the diff clean, though there's no functional dependency)

### Step 4: Create shared test fixtures in `conftest.py`

- **Files:** `backend/tests/conftest.py` (new)
- **Changes:**
  - Add a module docstring explaining this provides shared fixtures for all API test modules.
  - Import `collections.abc.AsyncIterator`.
  - Import `pytest`, `httpx.ASGITransport`, `httpx.AsyncClient`.
  - Import `Database` from `app.database`.
  - Import `app` from `app.main`.
  - Define fixture `db` (scope: function, async):
    1. Create `Database(":memory:")`.
    2. `await db.connect()`.
    3. `await db.init_schema()`.
    4. `await db.seed_default_board()` — seed the default board so tests start with a known state.
    5. `yield db`.
    6. `await db.close()`.
    - Use `# type: ignore[misc]` on the yield line for mypy compatibility with async generator fixtures (matching existing pattern in `test_database.py:22`).
  - Define fixture `client` (scope: function, async, depends on `db`):
    1. Set `app.state.db = db` — wire the test database into the app's state so route handlers can access it.
    2. Create `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")`.
    3. `yield client`.
    4. `await client.aclose()`.
    - Use `# type: ignore[misc]` on the yield line.
  - All fixtures should have return type annotations and docstrings.
  - The `db` fixture in `conftest.py` seeds the default board (unlike the inline fixture in `test_database.py` which does not seed). This is intentional — API tests need a board to exist for list/card operations. The existing `test_database.py` fixture remains as-is since those tests specifically test seed behavior and need an unseeded database.
- **Depends on:** Steps 2-3 (the app must have lifespan and `app.state.db` pattern established so the test fixture can mirror it)

## Risk Factors

- **Circular import between `conftest.py` and `main.py`** — Importing `app` from `app.main` in conftest triggers module-level code (`setup_logging()`, `FastAPI()` instantiation). The lifespan does NOT run at import time (it only runs when the ASGI server starts), so this is safe. However, if the lifespan is changed to run at module level in the future, this would break. Mitigation: the lifespan is explicitly an async context manager passed to FastAPI, which only executes during server startup or test client creation — this is the standard FastAPI testing pattern.

- **Test isolation with shared `app` instance** — The `client` fixture sets `app.state.db` on every test function, which mutates the global `app` object. Since pytest-asyncio runs tests sequentially by default and the fixture is function-scoped, this is safe. Mitigation: if parallel test execution is added later, the test setup will need to create a new `FastAPI` app instance per test or use proper locking.

- **`httpx.ASGITransport` vs deprecated `app` parameter** — `httpx` 0.27+ requires `ASGITransport` instead of passing `app` directly to `AsyncClient`. The project pins `httpx>=0.27.0`, so `ASGITransport` is available and is the correct approach. Mitigation: already using the supported API.

- **CORS `allow_origins=["*"]` in production** — The default of allowing all origins is appropriate for dev but insecure for production. Mitigation: the `CORS_ORIGINS` environment variable provides the override mechanism. This should be documented and set in production deployment configs.

- **Existing `test_database.py` fixture duplication** — After creating `conftest.py` with a `db` fixture, `test_database.py` will have its own local `db` fixture that shadows the conftest one. This is intentional and correct — pytest resolves fixtures from the most local scope first, so `test_database.py` continues to use its unseeded fixture while new API test modules use the seeded conftest fixture. No changes to `test_database.py` are needed.
