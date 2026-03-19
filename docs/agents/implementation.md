<!-- Project customize blocks for implementation.md -->

### Build & Run
- `make install` — install all dependencies (backend + frontend)
- `make dev` — start both backend (port 8000) and frontend (port 3000) dev servers
- `make dev-backend` — start only the backend dev server
- `make dev-frontend` — start only the frontend dev server
- `make lint` — run all linters
- `make lint-fix` — auto-fix lint issues
- `make type-check` — run type checkers
- `make test` — run all tests

### Style
- **Backend (Python):** Run `cd backend && uv run ruff check src/ tests/` and `cd backend && uv run ruff format src/ tests/` before committing
- **Frontend (TypeScript):** Run `cd frontend && pnpm biome check --fix ./src` before committing
- Follow existing patterns in the codebase

### Task Management
- **Tracker:** Linear
- **Project:** TRE
- **Active states:** Scoping, Planning, Design Feedback Loop, Implementing, Validating, Docs, Review
- **Terminal states:** Done, Closed, Cancelled
- **API endpoint:** https://api.linear.app/graphql

### Git Hosting
- **Host:** GitHub
- **Repo:** gutnikov/trello-clone
- **CLI:** gh
- **Create PR:** `gh pr create --title {title} --body {body} --head {branch}`
- **Check CI:** `gh pr checks {branch} --json state`
- **PR status:** `gh pr view {branch} --json state,mergeable`

### LSP
- **Python:** pyright (`opencode.json`)
- **TypeScript:** typescript-language-server (`opencode.json`)
- Config: `opencode.json`

### Default Model
- Model: `anthropic/claude-opus-4-6`
- Config: `opencode.json`

### Logging
- Library: structlog
- Config: `backend/src/app/logging.py`
- Import: `from app.logging import get_logger, setup_logging`
- Format: JSON to stdout

### Database
- **Engine:** SQLite via `aiosqlite`
- **Module:** `backend/src/app/database.py` — `Database` class with async lifecycle
- **Models:** `backend/src/app/models.py` — frozen Pydantic `BaseModel` subclasses (no ORM)
- **Pattern:** The `Database` class owns the connection and provides async CRUD methods. Call `connect()` → `init_schema()` → `seed_default_board()` on startup; `close()` on shutdown.
- **Adding entities:** Define a Pydantic model in `models.py`, add `CREATE TABLE` SQL to `init_schema()`, then add CRUD methods to `Database` following the existing Board/List/Card pattern.
- **ADR:** See `docs/architecture/adr-001-sqlite-persistence.md` for rationale.

### App Configuration
- **CORS:** Configured in `backend/src/app/main.py` via `CORSMiddleware`. Defaults to allow all origins (`*`) for dev. Set `CORS_ORIGINS` env var (comma-separated) for production.
- **Lifespan:** The `lifespan` async context manager in `main.py` connects to the database, initializes the schema, seeds the default board on startup, and closes the DB on shutdown. The `Database` instance is available at `app.state.db`.
- **Router package:** `backend/src/app/routers/__init__.py` is the router package. Add new endpoint modules (e.g., `boards.py`, `cards.py`) here and register them in `main.py`.

### Router Implementation Pattern

The `lists.py` router (`backend/src/app/routers/lists.py`) establishes the canonical pattern for API endpoint modules. Future routers (boards, cards) should follow this template:

1. **Pydantic request models** — Define request body schemas (e.g., `CreateListRequest`, `UpdateListRequest`) as `BaseModel` subclasses directly in the router file. These validate input at the boundary.
2. **Database access** — Access the database via `request.app.state.db` (the `Database` instance injected during app lifespan). Do not import or instantiate the database directly.
3. **Route ordering** — Define static path routes (e.g., `PUT /lists/reorder`) **before** parameterized path routes (e.g., `PUT /lists/{list_id}`). FastAPI matches routes in definition order, so `/lists/reorder` must come before `/lists/{list_id}` to avoid `"reorder"` being captured as a `list_id` parameter.
4. **Structured logging** — Use `from app.logging import get_logger` with a `module` parameter (e.g., `get_logger(module="routers.lists")`). Log one event per endpoint action (e.g., `list_created`, `list_updated`, `list_deleted`).
5. **Return types** — Return `dict[str, Any]` (via `model.model_dump()`) for single-entity responses, `list[dict[str, Any]]` for collections. Use `Response(status_code=204)` for delete endpoints.
6. **Error handling** — Raise `HTTPException(status_code=404, detail="<Entity> not found")` when a requested resource does not exist.
7. **Router registration** — Import the router in `backend/src/app/main.py` and register it with `app.include_router(router, prefix="/api")`. See `main.py:54` for the lists router registration.

### API Router Pattern
The canonical pattern for implementing API routers is established in `backend/src/app/routers/boards.py`. Follow this pattern for new routers:

- **Database access:** Route handlers obtain the database via `db: Database = request.app.state.db` (from the `Request` object, not dependency injection).
- **Response/request schemas:** Define Pydantic `BaseModel` subclasses in the same router file alongside the endpoints. Use `ConfigDict(frozen=True)` on all schemas. Use `Field(min_length=1)` or similar validators for request body validation.
- **Router declaration:** Use `APIRouter(tags=["..."])` with no prefix on the router itself. The prefix (`/api`) is set at registration in `main.py` via `app.include_router(router, prefix="/api")`.
- **Response models:** Set `response_model=` on each route decorator for automatic response validation and OpenAPI docs.
- **Logging:** Include structlog logging in each handler for observability (e.g., `log.info("board_updated", board_id=board.id)`).
- **Registration:** Import the router in `main.py` and register with `app.include_router(router, prefix="/api")`. See `backend/src/app/main.py:54` for the existing registration pattern.

### Shared Test Fixtures
- **Location:** `backend/tests/conftest.py`
- **`db` fixture:** Provides an in-memory `Database` instance with schema initialized and the default board seeded. Function-scoped for test isolation. Use this fixture in API endpoint tests rather than creating ad-hoc database setup.
- **`client` fixture:** Provides an `httpx.AsyncClient` wired to the FastAPI test app via `ASGITransport`, with the test database injected into `app.state.db`. Use this for testing route handlers.
- **`_wire_app_db` fixture (autouse):** Automatically sets `app.state.db` to the test database for every test function.
- **Important:** The `test_database.py` file has its own local `db` fixture that does **not** seed the default board. This is intentional — those tests need unseeded state. Pytest resolves fixtures from the most local scope first, so `test_database.py` uses its own fixture while other test modules use the conftest one.
- **Pattern:** New API endpoint test modules should depend on `db` and `client` from conftest rather than duplicating fixture setup.
