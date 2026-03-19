# Feedback Loop Plan: TRE-37

## Overview

Verification strategy for the list API router: four CRUD + reorder endpoints (`POST /api/lists`, `PUT /api/lists/{id}`, `DELETE /api/lists/{id}`, `PUT /api/lists/reorder`). Tests exercise all endpoints through the httpx test client, verifying correct HTTP status codes, response payloads, position auto-assignment, CASCADE deletion, and reorder persistence. Observability is provided through structured logging on each endpoint.

---

## Feedback Completeness Score: 8/10

| Method | Score | Notes |
|--------|-------|-------|
| Unit tests | 3 | 6 test cases covering all 4 endpoints plus error paths |
| Integration tests | 2 | Tests exercise full HTTP→router→database→response stack |
| E2E tests | 0 | N/A — backend-only API endpoints; no user-facing frontend component in this issue |
| Observability | 2 | 4 structured log events covering all endpoint operations |
| Runtime validation | 1 | Health check non-regression + test suite re-run |
| **Total** | **8** | |

---

## 1. Unit Tests — List API Endpoints (`backend/tests/test_api_lists.py`)

These tests use the shared `db` and `client` fixtures from `backend/tests/conftest.py`. The `db` fixture provides an in-memory SQLite database with schema initialized and default board seeded. The `client` fixture provides an httpx AsyncClient wired to the FastAPI test app.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_create_list_with_correct_position` | `POST /api/lists` with `{"title": "Todo", "board_id": "<seeded_board_id>"}` returns 201 with the created list containing `position: 0`. A second POST returns `position: 1`. Response body includes `id`, `title`, `board_id`, and `position` fields. |
| `test_update_list_title` | Create a list via `db.create_list(...)`, then `PUT /api/lists/{id}` with `{"title": "Updated"}` returns 200 with `title: "Updated"`. The list ID and board_id remain unchanged. |
| `test_update_list_returns_404_for_nonexistent` | `PUT /api/lists/nonexistent-uuid` with `{"title": "X"}` returns 404 with a JSON detail message. |
| `test_delete_list_removes_list_and_cards` | Create a list via `db.create_list(...)` and a card on it via `db.create_card(...)`. `DELETE /api/lists/{list_id}` returns 204 (no content body). Subsequently, `db.get_list(list_id)` returns `None` and `db.get_card(card_id)` returns `None` (CASCADE delete verified). |
| `test_delete_list_returns_404_for_nonexistent` | `DELETE /api/lists/nonexistent-uuid` returns 404. |
| `test_reorder_lists_updates_positions` | Create 3 lists with positions 0, 1, 2. `PUT /api/lists/reorder` with `{"list_ids": [id_2, id_0, id_1]}` returns 200. The response contains lists ordered by their new positions. Verify via `db.get_lists_by_board()` that positions are persisted as 0, 1, 2 matching the submitted order. |

### Run Command

```bash
cd backend && uv run python -m pytest tests/test_api_lists.py -v
```

---

## 2. Integration Tests — Router↔Database Stack

The unit tests above are inherently integration tests because they exercise the full HTTP request/response cycle through FastAPI's ASGI transport into the actual database layer (in-memory SQLite). Each test verifies:

- HTTP request parsing (Pydantic request model validation)
- Router handler logic (position computation, error handling)
- Database CRUD operations (via `Database` methods)
- HTTP response serialization (JSON response with correct status code)

### Additional Integration Verification

| Scenario | What It Verifies |
|---|---|
| Route ordering (`/lists/reorder` before `/lists/{id}`) | The reorder endpoint is reachable and doesn't get captured by the `{id}` parameter route |
| CASCADE delete | SQLite foreign key enforcement is active in the test database; deleting a list cascades to its cards |
| Position auto-assignment | The create endpoint queries existing lists and computes the next position, testing the full database round-trip |

These are implicitly covered by the unit test cases above rather than requiring separate test functions.

### Run Command

```bash
cd backend && uv run python -m pytest tests/test_api_lists.py -v
```

---

## 3. E2E Tests

**N/A** — This issue adds backend API endpoints only. There is no frontend component, no user-facing UI, and no browser interaction. E2E testing will become relevant when the frontend consumes these endpoints (a separate issue). While staging is available per `docs/agents/design-feedback-loop.md`, there are no user flows to test against it for this backend-only change.

---

## 4. Observability

The list router includes structured logging via `structlog` for runtime observability. Each endpoint logs a structured event on successful operation.

### Logs

| Event | Log Level | Fields | Purpose |
|---|---|---|---|
| `list_created` | `info` | `list_id`, `board_id`, `position` | Confirms a new list was created with its assigned position |
| `list_updated` | `info` | `list_id` | Confirms a list title was updated |
| `list_deleted` | `info` | `list_id` | Confirms a list was deleted (CASCADE includes cards) |
| `lists_reordered` | `info` | `board_id`, `count` | Confirms lists were reordered on a board, with count of lists affected |

These events complement the existing database-level logging (`database_connected`, `schema_initialized`) and the app-level logging (`app_startup_complete`). Together they provide a request-level audit trail for list operations.

### Metrics

N/A — The project does not have a metrics collection framework (no Prometheus, StatsD, or similar). Adding metrics infrastructure is out of scope for this issue.

### Traces

N/A — The project does not use distributed tracing. Single-process SQLite backend does not benefit from trace spans at this stage.

---

## 5. Runtime Validation

### Non-Regression

After implementing the list router, verify that existing tests continue to pass:

```bash
cd backend && uv run python -m pytest -v
```

This confirms that:
- Router registration in `main.py` doesn't break the `/health` endpoint
- The shared `conftest.py` fixtures still work for all existing test modules
- No import errors introduced by the new router module

### Static Analysis

```bash
cd backend && uv run ruff check src/app/routers/lists.py src/app/main.py tests/test_api_lists.py
cd backend && uv run mypy src/app/routers/lists.py src/app/main.py --strict
```

Verifies:
- Import ordering and linting compliance
- Type annotations are complete and correct
- No unused imports or variables
- Async patterns follow project conventions

---

## Summary

The feedback loop is dominated by unit/integration tests since this is a thin routing layer over an already-tested database layer. The six test cases cover all four endpoints, both success and error paths, position auto-assignment logic, CASCADE delete behavior, and reorder persistence. Observability via structured logging provides production-level audit trails without requiring additional infrastructure. The feedback_completeness_score of 8 exceeds the minimum threshold of 6.
