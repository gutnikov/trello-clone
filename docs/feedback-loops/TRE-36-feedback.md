# Feedback Loop Plan: TRE-36

## Overview

Verification strategy for the board API endpoints: `GET /api/board` (nested board response with lists and cards) and `PUT /api/board` (update board title). This is the first router in the codebase, so verification also covers router registration correctness and the database access pattern from route handlers. Tests use the shared `db` and `client` fixtures from `backend/tests/conftest.py`.

---

## 1. Integration Tests — GET /api/board (`backend/tests/test_api_boards.py`)

These tests verify the nested board retrieval endpoint returns the correct structure with lists and cards ordered by position.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_get_board_returns_200_with_nested_structure` | `GET /api/board` returns 200; response body contains `id` (str), `title` (str), and `lists` (list) keys. The seeded default board ("My Board") is returned. |
| `test_get_board_includes_lists_and_cards_in_order` | After seeding 2 lists (positions 1, 0) and 3 cards (positions 2, 0, 1) across those lists, `GET /api/board` returns lists sorted by position (0 before 1) and cards within each list sorted by position (0 before 1 before 2). Verify by checking `lists[0].position < lists[1].position` and `cards[i].position < cards[i+1].position` within each list. |
| `test_get_board_empty_lists_returns_empty_cards` | When a board has lists but no cards, the `cards` array in each list object is an empty list `[]`, not absent or null. |

### Run Command

```bash
cd backend && uv run pytest tests/test_api_boards.py -v -k "TestGetBoard"
```

---

## 2. Integration Tests — PUT /api/board (`backend/tests/test_api_boards.py`)

These tests verify the board title update endpoint validates input, persists changes, and returns the updated board.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_put_board_updates_title` | `PUT /api/board` with body `{"title": "New Title"}` returns 200; response body contains `id` matching the default board's ID and `title` equal to `"New Title"`. A subsequent `GET /api/board` returns the updated title, confirming persistence. |
| `test_put_board_empty_title_returns_422` | `PUT /api/board` with body `{"title": ""}` returns 422 (Unprocessable Entity) due to the `min_length=1` validation on `BoardUpdateRequest.title`. The response body contains a validation error detail. |
| `test_put_board_missing_title_returns_422` | `PUT /api/board` with body `{}` (no `title` field) returns 422 with a validation error indicating `title` is required. |

### Run Command

```bash
cd backend && uv run pytest tests/test_api_boards.py -v -k "TestPutBoard"
```

---

## 3. Integration Tests — Router Registration (`backend/tests/test_api_boards.py`)

These tests verify the board router is correctly registered in `main.py` and accessible at the expected URL paths.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_board_endpoints_registered_at_api_prefix` | `GET /api/board` returns 200 (not 404), confirming the router is registered with the `/api` prefix. `GET /board` (without prefix) returns 404, confirming the prefix is required. |

### Run Command

```bash
cd backend && uv run pytest tests/test_api_boards.py -v -k "test_board_endpoints_registered"
```

---

## 4. Non-Regression — Existing Tests

Verify that adding the board router and modifying `main.py` does not break existing functionality.

### Test Cases

| Suite | Expected Behavior |
|---|---|
| `tests/test_smoke.py` | `test_smoke` still passes |
| `tests/test_models.py` | All model tests still pass (no model changes) |
| `tests/test_database.py` | All database CRUD tests still pass (no database changes) |
| `tests/test_main.py` | CORS and lifespan tests still pass; the new `include_router` call doesn't interfere with middleware or lifecycle |
| `tests/test_conftest_fixtures.py` | Shared fixture tests still pass |

### Run Command

```bash
cd backend && uv run pytest -v
```

---

## 5. Static Analysis

### Type Checking

```bash
cd backend && uv run mypy src/app/routers/boards.py src/app/main.py --strict
```

Verifies:
- All Pydantic response/request schemas have correct field type annotations
- Route handler functions have full parameter and return type annotations
- `request.app.state.db` access is properly annotated with local `db: Database` variable
- `BoardUpdateRequest` field validation uses `Field(min_length=1)` correctly
- Import paths resolve correctly (`from app.routers.boards import router`)

### Linting

```bash
cd backend && uv run ruff check src/app/routers/boards.py src/app/main.py tests/test_api_boards.py
```

Verifies:
- Import ordering follows isort conventions (I rules)
- Line length <= 100 characters
- No unused imports or variables
- Async patterns are correct (ASYNC rules)
- Naming conventions followed (N rules)

---

## 6. Observability Hooks

The board router includes structured logging via `structlog` for runtime observability:

| Event | Log Level | Fields | Purpose |
|---|---|---|---|
| `board_fetched` | `info` | `board_id` | Confirms GET /api/board successfully retrieved the board and nested data |
| `board_updated` | `info` | `board_id`, `new_title` | Confirms PUT /api/board successfully updated the board title |
| `router_registered` | `info` | `router="boards"`, `prefix="/api"` | Logged in `main.py` at startup to confirm the board router was registered |

These events extend the existing startup audit trail:

```
database_connected → schema_initialized → seed_default_board → router_registered(boards) → app_startup_complete
```

And during request handling:
```
board_fetched(board_id=...)   [on GET /api/board]
board_updated(board_id=..., new_title=...)   [on PUT /api/board]
```

---

## 7. Runtime Validation

- **Board existence check:** Both endpoints verify that at least one board exists via `list_boards()` before proceeding. If no board is found (e.g., seed failed), they return 404 with a clear error message rather than crashing on index access.
- **Empty title rejection:** The `BoardUpdateRequest` schema uses `Field(min_length=1)` which causes FastAPI to return 422 automatically for empty or missing title fields. This matches the `Board` domain model's `min_length=1` constraint, ensuring API-level and persistence-level validation are consistent.
- **Response model enforcement:** Using `response_model=BoardDetailResponse` and `response_model=BoardResponse` on the route decorators ensures FastAPI validates the response structure at runtime, catching any mismatch between the handler return value and the declared schema.
- **Position ordering guarantee:** The database methods `get_lists_by_board` and `get_cards_by_list` include `ORDER BY position` clauses. The router trusts this ordering and does not re-sort. Tests verify the ordering is correct end-to-end.

---

## 8. Manual Verification (Optional)

For local development verification beyond automated tests:

```bash
# Start the server
cd backend && uv run uvicorn app.main:app --reload

# Test GET
curl -s http://localhost:8000/api/board | python -m json.tool

# Test PUT
curl -s -X PUT http://localhost:8000/api/board -H "Content-Type: application/json" -d '{"title": "Updated Board"}' | python -m json.tool

# Test validation (should return 422)
curl -s -X PUT http://localhost:8000/api/board -H "Content-Type: application/json" -d '{"title": ""}' | python -m json.tool
```

---

## Feedback Completeness Score

| Dimension | Score (0-2) | Justification |
|---|---|---|
| Integration tests — GET endpoint | 2 | 3 test cases covering basic structure, ordering correctness, and empty-cards edge case |
| Integration tests — PUT endpoint | 2 | 3 test cases covering successful update, empty title rejection, and missing title rejection |
| Integration tests — registration | 1 | 1 test case confirming router is mounted at `/api` prefix |
| Non-regression | 1 | Full existing test suite re-run to verify no breakage from `main.py` modification |
| Static analysis | 1 | mypy strict + ruff linting on all new/modified files |
| Observability | 1 | 3 structured log events for request handling and router registration |
| Runtime validation | 1 | Board existence checks, schema validation, response model enforcement |

**Total feedback_completeness_score: 9/10**

The score of 9 exceeds the minimum threshold of 6. The high score reflects that this is the first API router in the codebase, establishing patterns for all subsequent endpoint implementations. Thorough verification ensures the DB access pattern, response schema approach, and test structure are correct before they're replicated in TRE-37 (lists) and TRE-38 (cards). E2e browser tests are not applicable since these are pure JSON API endpoints with no frontend component yet.
