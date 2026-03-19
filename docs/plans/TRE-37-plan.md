# Implementation Plan: TRE-37

## Overview

Implement a FastAPI list router with four endpoints (create, update title, delete, reorder) that delegate to the existing `Database` CRUD methods. The router module defines Pydantic request models, retrieves `request.app.state.db` to access the database, and returns appropriate HTTP status codes. Registration in `main.py` adds two lines. Tests use the shared `db` and `client` fixtures from `conftest.py` to exercise all six specified scenarios.

## Steps

### Step 1: Create the list router module

- **Files:** `backend/src/app/routers/lists.py` (new)
- **Changes:**
  - Define Pydantic request models:
    - `CreateListRequest` with fields `title: str` and `board_id: str`
    - `UpdateListRequest` with field `title: str`
    - `ReorderListsRequest` with field `list_ids: list[str]`
  - Create `router = APIRouter(tags=["lists"])` (no prefix — the prefix is applied during registration in `main.py`)
  - Import `get_logger` from `app.logging` and create a module-level logger
  - Implement four endpoints:

  **`POST /lists`** — Create a new list
  1. Extract `db` from `request.app.state.db`
  2. Compute the next available position by calling `db.get_lists_by_board(body.board_id)` and setting `position = len(existing_lists)`
  3. Construct a `List` model instance with `title=body.title`, `board_id=body.board_id`, `position=position`
  4. Call `db.create_list(lst)` and return the created list with `status_code=201`
  5. Log `list_created` with list_id, board_id, position

  **`PUT /lists/{id}`** — Update list title
  1. Extract `db` from `request.app.state.db`
  2. Call `db.update_list(list_id=id, title=body.title)`
  3. If result is `None`, raise `HTTPException(status_code=404, detail="List not found")`
  4. Return the updated list
  5. Log `list_updated` with list_id

  **`DELETE /lists/{id}`** — Delete list (CASCADE handles cards)
  1. Extract `db` from `request.app.state.db`
  2. Call `db.delete_list(list_id=id)`
  3. If result is `False`, raise `HTTPException(status_code=404, detail="List not found")`
  4. Return `Response(status_code=204)` (no content)
  5. Log `list_deleted` with list_id

  **`PUT /lists/reorder`** — Reorder lists on a board
  1. Extract `db` from `request.app.state.db`
  2. Iterate over `body.list_ids` with `enumerate()` to get `(index, list_id)` pairs
  3. For each pair, call `db.update_list(list_id=list_id, position=index)`
  4. After updating all positions, determine the board_id from the first list (call `db.get_list(body.list_ids[0])` to get the board_id) and return the reordered lists via `db.get_lists_by_board(board_id)`
  5. Log `lists_reordered` with list_ids and board_id

  **IMPORTANT routing order:** The `PUT /lists/reorder` route must be defined *before* `PUT /lists/{id}` in the file, otherwise FastAPI will match "reorder" as a path parameter `{id}`. This is critical for correct URL resolution.

- **Depends on:** None (uses existing `Database` methods and `List` model)

### Step 2: Register the list router in main.py

- **Files:** `backend/src/app/main.py` (modify)
- **Changes:**
  - Add import: `from app.routers.lists import router as lists_router`
  - Add registration: `app.include_router(lists_router, prefix="/api")` — place this after the CORS middleware setup and before the `/health` endpoint definition
  - This follows the pattern described in `routers/__init__.py` docstring and matches the `prefix="/api"` convention specified in the issue
- **Depends on:** Step 1 (the router module must exist)

### Step 3: Create list API tests

- **Files:** `backend/tests/test_api_lists.py` (new)
- **Changes:**
  - Import `pytest`, `httpx`, `Database` from `app.database`, `Card` from `app.models`
  - Use the shared `client` and `db` fixtures from `conftest.py` (function-scoped, in-memory DB with seeded default board)
  - Implement six test cases:

  **`test_create_list_with_correct_position`**
  - Use `db.list_boards()` to get the seeded board's ID
  - POST `/api/lists` with `{"title": "Todo", "board_id": board_id}`
  - Assert status 201, response contains `title: "Todo"`, `board_id: board_id`, `position: 0`
  - POST another list and assert `position: 1`

  **`test_update_list_title`**
  - Create a list via `db.create_list(...)` directly
  - PUT `/api/lists/{list_id}` with `{"title": "Updated Title"}`
  - Assert status 200, response contains `title: "Updated Title"`

  **`test_update_list_returns_404_for_nonexistent`**
  - PUT `/api/lists/nonexistent-id` with `{"title": "X"}`
  - Assert status 404

  **`test_delete_list_removes_list_and_cards`**
  - Create a list via `db.create_list(...)`
  - Create a card on that list via `db.create_card(...)`
  - DELETE `/api/lists/{list_id}`
  - Assert status 204
  - Verify list is gone: `db.get_list(list_id)` returns `None`
  - Verify card is gone: `db.get_card(card_id)` returns `None` (CASCADE delete)

  **`test_delete_list_returns_404_for_nonexistent`**
  - DELETE `/api/lists/nonexistent-id`
  - Assert status 404

  **`test_reorder_lists_updates_positions`**
  - Create two or three lists via `db.create_list(...)` with positions 0, 1, 2
  - PUT `/api/lists/reorder` with `{"list_ids": [id_2, id_0, id_1]}` (reversed/shuffled order)
  - Assert status 200
  - Verify the response contains lists in the new order with positions 0, 1, 2 matching the submitted order
  - Optionally verify via `db.get_lists_by_board()` that the positions are persisted correctly

- **Depends on:** Steps 1-2 (router must be registered for the test client to hit the endpoints)

## Risk Factors

- **Route ordering for `/lists/reorder` vs `/lists/{id}`** — If the reorder endpoint is defined after the parameterized update endpoint, FastAPI will interpret "reorder" as a list ID and route to the update handler. Mitigation: define the `PUT /lists/reorder` route before `PUT /lists/{id}` in the router file. This is a well-known FastAPI pattern.

- **Position auto-assignment race condition** — The create endpoint computes position by counting existing lists. If two concurrent requests create lists simultaneously, they could get the same position. Mitigation: SQLite serializes writes via WAL mode, and the app is single-process for now. This is acceptable for the current scale; a future issue can add database-level position management if needed.

- **Reorder endpoint with invalid list IDs** — If `list_ids` contains IDs that don't exist, `db.update_list()` returns `None` but the endpoint silently continues. Mitigation: the current issue scope doesn't require validation of list IDs in the reorder body. The endpoint updates what it can and returns the result. This matches the pragmatic approach of the existing codebase. Validation can be added as a follow-up if needed.

- **Reorder endpoint with empty `list_ids`** — If the array is empty, the endpoint would attempt `db.get_list(body.list_ids[0])` and raise an `IndexError`. Mitigation: the implementation should handle the empty case by returning an empty list or a 400 error. The plan recommends returning an empty list `[]` for simplicity.

- **CASCADE delete verification in tests** — The test for delete-with-cards relies on SQLite's `PRAGMA foreign_keys=ON` being enabled in the test database. The `conftest.py` `db` fixture calls `db.connect()` which enables foreign keys. This is already handled by the existing infrastructure.
