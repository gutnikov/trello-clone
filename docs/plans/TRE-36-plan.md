# Implementation Plan: TRE-36

## Overview

Implement the board API router with two endpoints (`GET /api/board` and `PUT /api/board`) that expose the existing database layer through a REST interface. The GET endpoint returns a nested JSON response containing the single board with all its lists and their cards, ordered by position. The PUT endpoint updates the board title with validation. This requires creating Pydantic response/request schemas in the new router file, implementing the two route handlers, registering the router in `main.py`, and writing integration tests using the existing shared test fixtures from `conftest.py`. All database methods needed already exist — no changes to the persistence layer are required.

## Steps

### Step 1: Define Pydantic response and request schemas in the board router file

- **Files:** `backend/src/app/routers/boards.py` (new)
- **Changes:**
  - Create the file with a module docstring explaining it provides the board API endpoints.
  - Define `CardResponse(BaseModel)` with fields: `id: str`, `title: str`, `position: int`. This is the API response representation of a card (no `list_id` — the nesting makes it implicit).
  - Define `ListWithCards(BaseModel)` with fields: `id: str`, `title: str`, `position: int`, `cards: list[CardResponse]`. This embeds cards within each list for the nested response.
  - Define `BoardDetailResponse(BaseModel)` with fields: `id: str`, `title: str`, `lists: list[ListWithCards]`. This is the top-level nested response for `GET /api/board`.
  - Define `BoardUpdateRequest(BaseModel)` with field: `title: str = Field(min_length=1)`. This validates the PUT body — the `min_length=1` constraint matches the existing `Board` model and ensures empty titles return 422.
  - Define `BoardResponse(BaseModel)` with fields: `id: str`, `title: str`. This is the flat response for `PUT /api/board`.
  - All schemas should use `model_config = ConfigDict(frozen=True)` consistent with the existing domain models in `backend/src/app/models.py`.
- **Depends on:** None

### Step 2: Implement the GET /api/board endpoint

- **Files:** `backend/src/app/routers/boards.py` (modify — same file from Step 1)
- **Changes:**
  - Create `router = APIRouter(tags=["boards"])` at module level. Do NOT set a prefix on the router itself — the prefix `/api` will be set during registration in `main.py`.
  - Import `APIRouter`, `HTTPException`, `Request` from `fastapi`, and `Database` from `app.database`.
  - Implement `async def get_board(request: Request) -> BoardDetailResponse`:
    - Access the database via `db: Database = request.app.state.db`.
    - Call `boards = await db.list_boards()` to get all boards; take the first one (the default board). If no boards exist, raise `HTTPException(status_code=404, detail="No board found")`.
    - Call `lists = await db.get_lists_by_board(board.id)` to get lists ordered by position.
    - For each list, call `cards = await db.get_cards_by_list(lst.id)` to get cards ordered by position.
    - Construct and return the nested `BoardDetailResponse` with `ListWithCards` and `CardResponse` objects.
  - Decorate with `@router.get("/board", response_model=BoardDetailResponse)`.
- **Depends on:** Step 1

### Step 3: Implement the PUT /api/board endpoint

- **Files:** `backend/src/app/routers/boards.py` (modify — same file)
- **Changes:**
  - Implement `async def update_board(request: Request, body: BoardUpdateRequest) -> BoardResponse`:
    - Access the database via `db: Database = request.app.state.db`.
    - Call `boards = await db.list_boards()` to get the default board. If no boards exist, raise `HTTPException(status_code=404, detail="No board found")`.
    - Call `updated = await db.update_board(board.id, body.title)`.
    - If `updated` is `None`, raise `HTTPException(status_code=404, detail="Board not found")` (defensive — shouldn't happen if `list_boards` returned results).
    - Return `BoardResponse(id=updated.id, title=updated.title)`.
  - Decorate with `@router.put("/board", response_model=BoardResponse)`.
  - FastAPI's request body validation will automatically return 422 for empty `title` thanks to the `min_length=1` constraint on `BoardUpdateRequest`.
  - Add structlog logging: `log.info("board_updated", board_id=board.id, new_title=body.title)` after successful update.
- **Depends on:** Step 1

### Step 4: Register the board router in main.py

- **Files:** `backend/src/app/main.py` (modify)
- **Changes:**
  - Add import: `from app.routers.boards import router as boards_router`.
  - Add router registration after the CORS middleware block and before the `/health` endpoint: `app.include_router(boards_router, prefix="/api")`.
  - This makes the endpoints available at `GET /api/board` and `PUT /api/board`.
  - Log the router registration for observability: `log.info("router_registered", router="boards", prefix="/api")`.
- **Depends on:** Steps 2, 3

### Step 5: Write integration tests for the board API

- **Files:** `backend/tests/test_api_boards.py` (new)
- **Changes:**
  - Add a module docstring referencing the TRE-36 feedback loop plan.
  - Import `httpx`, `pytest` and the domain models (`Board`, `List`, `Card`) from `app.models`, and `Database` from `app.database`.
  - Use the shared `client` and `db` fixtures from `conftest.py` — do NOT create local fixtures.
  - Create test class `TestGetBoard`:
    - `test_get_board_returns_200_with_nested_structure(client, db)`: Verify `GET /api/board` returns 200, response body has `id`, `title`, and `lists` keys, and `lists` is a list.
    - `test_get_board_includes_lists_and_cards_in_order(client, db)`: Seed two lists with different positions and multiple cards per list with different positions. Verify the response returns lists in position order and cards within each list in position order.
  - Create test class `TestPutBoard`:
    - `test_put_board_updates_title(client, db)`: Send `PUT /api/board` with `{"title": "New Title"}`, verify 200 response with updated title. Then `GET /api/board` and verify the title persisted.
    - `test_put_board_empty_title_returns_422(client)`: Send `PUT /api/board` with `{"title": ""}`, verify 422 response.
  - All test functions are `async def` with full type annotations and descriptive docstrings, matching the pattern in existing test files (`test_database.py`, `test_main.py`).
  - Use explicit assert messages for clear failure diagnostics.
- **Depends on:** Step 4

## Risk Factors

- **`app.state.db` is typed as `Any`** — Starlette's `State` object uses `Any` for attribute access. Route handlers accessing `request.app.state.db` won't get type checking on the returned `Database` instance. Mitigation: add a local type annotation `db: Database = request.app.state.db` in each handler for IDE/mypy benefit, and add `# type: ignore[attr-defined]` if mypy strict mode flags the state access.

- **N+1 query pattern in GET /api/board** — The nested response requires one query for the board, one for lists, and one per list for cards. For a single-board Trello clone with modest list/card counts, this is acceptable. Mitigation: if performance becomes a concern in the future, a single JOIN query could replace the per-list card queries. This is out of scope for TRE-36.

- **First router registration sets a pattern** — This is the first router in the codebase. The prefix strategy (`/api` on `include_router`, no prefix on the router itself) and the DB access pattern (`request.app.state.db`) will be followed by future routers (lists, cards). If the pattern is wrong, it creates tech debt. Mitigation: the plan uses standard FastAPI idioms; the prefix-at-registration pattern is the recommended approach from FastAPI docs.

- **Empty `routers/__init__.py` already exists** — The `__init__.py` in `routers/` already exists with a docstring from TRE-35. No changes needed, but verify the import `from app.routers.boards import router` works with the existing package structure.

- **PUT endpoint assumes a single default board** — Both endpoints use `list_boards()[0]` to find the default board rather than accepting a board ID in the URL path. This matches the issue requirement ("Return the single board") but would need refactoring if multi-board support is added later. Mitigation: the current single-board design is intentional per the scope.
