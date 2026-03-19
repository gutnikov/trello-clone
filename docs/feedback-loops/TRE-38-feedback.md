# Feedback Loop Plan: TRE-38

## Overview

Verification strategy for the card API router: four endpoints (create, update title, delete, move/reorder), router registration in `main.py`, and comprehensive test coverage. The card router is the first router in the project, so verification must also confirm the router registration pattern works correctly with the existing app infrastructure (lifespan, CORS, test fixtures).

---

## 1. Unit Tests — Card CRUD Endpoints (`backend/tests/test_api_cards.py`)

These tests verify each card endpoint works correctly through HTTP requests.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_create_card` | POST `/api/cards` with `{"title": "Test Card", "list_id": "<valid_list_id>"}` returns 201 with JSON body containing `id` (UUID string), `title` matching input, `list_id` matching input, and `position` of 0 (auto-assigned as first card in list) |
| `test_create_card_auto_position` | POST `/api/cards` twice to the same list; second card gets `position: 1` (auto-incremented) |
| `test_update_card_title` | Create a card via DB fixture, PUT `/api/cards/{id}` with `{"title": "Updated"}` returns 200 with JSON body showing updated title |
| `test_update_card_not_found` | PUT `/api/cards/nonexistent-uuid` with `{"title": "X"}` returns 404 with `{"detail": "Card not found"}` |
| `test_delete_card` | Create a card via DB fixture, DELETE `/api/cards/{id}` returns 204 with no response body. Verify card is gone by querying DB directly |
| `test_delete_card_not_found` | DELETE `/api/cards/nonexistent-uuid` returns 404 with `{"detail": "Card not found"}` |
| `test_move_card_between_lists` | Create two lists and a card in list 1. PUT `/api/cards/{id}/move` with `{"list_id": "<list2_id>", "position": 0}` returns 200. Response shows card has `list_id` of list 2 and `position` of 0 |
| `test_reorder_card_within_list` | Create a list with 3 cards (positions 0, 1, 2). Move card at position 2 to position 0 via PUT `/api/cards/{id}/move`. Response shows card at position 0. Verify via DB that other cards shifted: former position 0 → 1, former position 1 → 2 |

### Run Command

```bash
cd backend && uv run pytest tests/test_api_cards.py -v
```

---

## 2. Integration Tests — Router Registration (`backend/tests/test_api_cards.py`)

These tests implicitly verify that the router is correctly registered in `main.py` by confirming HTTP requests reach the card endpoints. If the router is not registered or the prefix is wrong, all endpoint tests will fail with 404.

### Verification Points

| Check | How Verified |
|---|---|
| Router registered with correct prefix `/api` | All tests use `/api/cards` URLs; a missing registration produces 404 for all requests |
| Router tags set correctly | Verified via OpenAPI schema (optional — can check `app.openapi()` in a test) |
| No conflict with existing `/health` endpoint | Health endpoint continues to work (covered by non-regression tests below) |
| DB dependency accessible in route handlers | All endpoint tests exercise `request.app.state.db`; failures indicate wiring issues |

---

## 3. Non-Regression Tests

Verify that existing tests continue to pass after adding the card router and modifying `main.py`.

### Test Suites

| Suite | File | Expected |
|---|---|---|
| Smoke | `tests/test_smoke.py` | 1 test passes |
| Models | `tests/test_models.py` | All model tests pass (no changes to models) |
| Database | `tests/test_database.py` | All DB CRUD tests pass (no changes to database layer) |
| Main | `tests/test_main.py` | CORS and lifespan tests pass (main.py modified only to add import + include_router) |
| Conftest fixtures | `tests/test_conftest_fixtures.py` | Fixture tests pass (conftest.py unchanged) |

### Run Command

```bash
cd backend && uv run pytest -v
```

---

## 4. Static Analysis

### Type Checking

```bash
cd backend && uv run mypy src/app/routers/cards.py src/app/main.py --strict
```

Verifies:
- Request schema models have correct type annotations
- Route handler signatures have return type annotations
- `_get_db` helper returns properly typed `Database`
- `request.app.state.db` access is handled (may need `# type: ignore` for `Any` state)
- All new code passes strict mypy

### Linting

```bash
cd backend && uv run ruff check src/app/routers/cards.py src/app/main.py tests/test_api_cards.py
```

Verifies:
- Import ordering follows project conventions (isort-compatible `I` rules)
- Line length <= 100 characters
- No unused imports or variables
- Async patterns correct (ASYNC rules)
- No security issues (B rules for bandit-like checks)

---

## 5. Observability Hooks

The card router should include structured logging via `structlog` for runtime observability:

| Event | Log Level | Fields | Purpose |
|---|---|---|---|
| `card_created` | `info` | `card_id`, `list_id`, `position` | Audit trail for card creation, confirms auto-position assignment |
| `card_updated` | `info` | `card_id` | Audit trail for title updates |
| `card_deleted` | `info` | `card_id` | Audit trail for card deletion |
| `card_moved` | `info` | `card_id`, `source_list_id`, `target_list_id`, `new_position` | Audit trail for move operations, critical for debugging reorder issues |

These events complement the existing database-level logging and the app startup/shutdown events from `main.py`.

---

## 6. Runtime Validation

- **Request body validation:** FastAPI + Pydantic automatically validates request bodies against the schema models. Invalid requests (missing `title`, empty `title`, missing `list_id`) return 422 Unprocessable Entity with detailed error messages. This is tested implicitly — no custom validation code needed.

- **Path parameter validation:** FastAPI validates `card_id` as a string path parameter. Non-string values are rejected by the framework.

- **Position bounds:** The move endpoint accepts any integer position. If `position` exceeds the number of cards in the target list, the card is placed at the end (the reorder logic handles this by clamping or allowing sparse positions). The implementation should handle edge cases:
  - `position < 0` — treat as 0 (or reject with 422)
  - `position > len(cards)` — place at end
  - `position == current_position` and same list — no-op (return current card)

- **Foreign key integrity:** SQLite enforces `FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE`. Creating a card with a non-existent `list_id` will raise an IntegrityError. The router should catch this and return an appropriate error (400 or 422) rather than letting it bubble up as 500. This is a nice-to-have for v0; the minimum viable behavior is to let the 500 propagate.

- **Concurrent access:** SQLite serializes writes via file-level locking. The move endpoint performs multiple `update_card` calls sequentially. Between updates, another request could read an inconsistent state. This is acceptable for v0 with SQLite but should be noted for future migration to PostgreSQL where explicit transactions would be needed.

---

## 7. Edge Case Coverage

| Edge Case | Expected Behavior | Tested By |
|---|---|---|
| Create card in empty list | Position auto-assigned to 0 | `test_create_card` |
| Create second card in list | Position auto-assigned to 1 | `test_create_card_auto_position` |
| Update with same title | Returns 200 with unchanged card | Implicitly covered |
| Delete already-deleted card | Returns 404 | `test_delete_card_not_found` |
| Move card to same position in same list | Returns 200 (no-op or idempotent) | Could be additional test |
| Move card to non-existent list | Returns 500 (FK violation) or 400 if validated | Not in initial test set — future improvement |

---

## Feedback Completeness Score

| Dimension | Score (0-2) | Justification |
|---|---|---|
| Unit tests — CRUD endpoints | 2 | 8 test cases covering all 4 endpoints including happy paths and error cases |
| Integration tests — router registration | 1 | Implicitly verified through all endpoint tests; explicit registration check via test URL routing |
| Non-regression | 1 | Full existing test suite re-run to verify no breakage from main.py modification |
| Static analysis | 1 | mypy strict + ruff linting on all new/modified files |
| Observability | 1 | 4 structured log events covering all card operations |
| Runtime validation | 1 | Pydantic schema validation, FK integrity handling, position edge cases documented |
| Edge case coverage | 1 | Position auto-assignment, concurrent access, bounds handling documented |

**Total feedback_completeness_score: 8/10**

The score of 8 exceeds the minimum threshold of 6. The high score reflects that this is the first router in the project, establishing patterns for future endpoint implementations. E2e browser tests are not applicable since these are pure API endpoints with no frontend component. The move/reorder logic warrants thorough testing due to its multi-card update complexity.
