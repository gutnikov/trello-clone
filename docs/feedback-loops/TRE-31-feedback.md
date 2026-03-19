# Feedback Loop Plan: TRE-31

## Overview

Verification strategy for the backend data models and persistence layer. Covers unit tests for Pydantic models, unit tests for database CRUD operations, runtime validation via structured logging, and observability hooks for production monitoring.

---

## 1. Unit Tests — Models (`backend/tests/test_models.py`)

These tests verify Pydantic model validation, defaults, constraints, and immutability.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_board_creation_defaults` | Board created with only `title` has auto-generated UUID `id` |
| `test_board_creation_explicit_id` | Board created with explicit `id` and `title` preserves both |
| `test_board_rejects_empty_title` | `ValidationError` raised when `title` is empty string |
| `test_board_immutable` | Assigning to `board.title` raises `ValidationError` (frozen model) |
| `test_list_creation_defaults` | List created with `title` and `board_id` has `position=0` and auto UUID |
| `test_list_creation_explicit_position` | List with explicit `position=5` preserves the value |
| `test_list_rejects_empty_title` | `ValidationError` raised when `title` is empty string |
| `test_list_immutable` | Assigning to `lst.position` raises `ValidationError` |
| `test_card_creation_defaults` | Card created with `title` and `list_id` has `position=0` and auto UUID |
| `test_card_creation_explicit_position` | Card with explicit `position=3` preserves the value |
| `test_card_rejects_empty_title` | `ValidationError` raised when `title` is empty string |
| `test_card_immutable` | Assigning to `card.title` raises `ValidationError` |

### Run Command

```bash
cd backend && uv run pytest tests/test_models.py -v
```

---

## 2. Unit Tests — Database CRUD (`backend/tests/test_database.py`)

These tests verify the SQLite persistence layer using in-memory databases for isolation and speed.

### Fixture

```python
@pytest.fixture
async def db():
    database = Database(":memory:")
    await database.connect()
    await database.init_schema()
    yield database
    await database.close()
```

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `test_schema_creates_tables` | After `init_schema`, querying `sqlite_master` returns `boards`, `lists`, `cards` tables |
| `test_seed_default_board_creates_board` | `seed_default_board` inserts one board titled "My Board" when DB is empty |
| `test_seed_default_board_idempotent` | Calling `seed_default_board` twice returns same board; `list_boards` returns exactly 1 |
| `test_create_board` | `create_board` inserts a board; `get_board` retrieves it with matching fields |
| `test_get_board_not_found` | `get_board` with non-existent ID returns `None` |
| `test_list_boards` | After creating 3 boards, `list_boards` returns all 3 |
| `test_update_board` | `update_board` changes title; subsequent `get_board` reflects the change |
| `test_update_board_not_found` | `update_board` with non-existent ID returns `None` |
| `test_delete_board` | `delete_board` returns `True`; subsequent `get_board` returns `None` |
| `test_delete_board_not_found` | `delete_board` with non-existent ID returns `False` |
| `test_create_list` | `create_list` inserts a list; `get_list` retrieves it |
| `test_get_lists_by_board_ordered` | Lists for a board are returned ordered by `position` |
| `test_update_list_title` | `update_list` with new title updates the record |
| `test_update_list_position` | `update_list` with new position updates the record |
| `test_delete_list` | `delete_list` returns `True`; subsequent `get_list` returns `None` |
| `test_create_card` | `create_card` inserts a card; `get_card` retrieves it |
| `test_get_cards_by_list_ordered` | Cards for a list are returned ordered by `position` |
| `test_update_card_title` | `update_card` with new title updates the record |
| `test_update_card_position` | `update_card` with new position updates the record |
| `test_update_card_move_to_list` | `update_card` with new `list_id` moves card between lists |
| `test_delete_card` | `delete_card` returns `True`; subsequent `get_card` returns `None` |
| `test_delete_board_cascades` | Deleting a board also removes its lists and cards (CASCADE) |
| `test_delete_list_cascades_cards` | Deleting a list also removes its cards (CASCADE) |

### Run Command

```bash
cd backend && uv run pytest tests/test_database.py -v
```

---

## 3. Full Test Suite

Run all tests to verify no regressions against the existing smoke test:

```bash
cd backend && uv run pytest -v
```

---

## 4. Static Analysis

### Type Checking

```bash
cd backend && uv run mypy src/app/models.py src/app/database.py --strict
```

Verifies:
- All functions have type annotations
- No `Any` types leak through
- aiosqlite usage is type-safe (or explicitly ignored where stubs are incomplete)

### Linting

```bash
cd backend && uv run ruff check src/app/models.py src/app/database.py
```

Verifies:
- Code follows project style (line length 100, Python 3.12 target)
- No import ordering issues
- No unused imports or variables

---

## 5. Observability Hooks

The persistence layer includes structured logging via `structlog` for runtime observability:

| Event | Log Level | Fields | Purpose |
|---|---|---|---|
| `database_connected` | `info` | `db_path` | Confirms DB connection established |
| `database_closed` | `info` | `db_path` | Confirms DB connection closed |
| `schema_initialized` | `info` | `tables_created` | Confirms tables exist after init |
| `default_board_seeded` | `info` | `board_id`, `board_title` | Confirms default board created on first run |
| `default_board_exists` | `debug` | `board_id` | Default board already present, seed skipped |
| CRUD operations | `debug` | `entity_type`, `entity_id`, `operation` | Trace individual persistence operations |

These log events allow operators to:
- Verify the database initializes correctly on first deployment
- Trace data operations in development/staging
- Debug persistence issues without adding ad-hoc print statements

---

## 6. Runtime Validation

- **Schema verification:** `init_schema()` uses `CREATE TABLE IF NOT EXISTS`, making it safe to call on every startup without data loss. The method should query `sqlite_master` after creation and log the result to confirm tables exist.
- **Foreign key enforcement:** `PRAGMA foreign_keys = ON` is executed on every connection open. This prevents orphaned records at the database level.
- **Seed idempotency:** `seed_default_board()` checks for existing boards before inserting, preventing duplicate default boards across restarts.
- **Parameterized queries:** All SQL uses `?` placeholders, preventing SQL injection at the boundary between application code and database.

---

## Feedback Completeness Score

| Dimension | Score (0-2) | Justification |
|---|---|---|
| Unit tests — models | 2 | 12 test cases covering creation, defaults, validation errors, and immutability |
| Unit tests — persistence | 2 | 23 test cases covering full CRUD for all 3 entities plus schema, seed, cascade |
| Static analysis | 1 | mypy strict + ruff linting verify type safety and style |
| Observability | 1 | Structured logging for lifecycle events and CRUD operations |
| Runtime validation | 1 | Schema verification, FK enforcement, seed idempotency, parameterized queries |
| Integration tests | 0 | Not applicable — no API endpoints yet; persistence is tested in isolation |
| E2e tests | 0 | Not applicable — no user-facing interface in this issue |

**Total feedback_completeness_score: 7/10**

The score of 7 exceeds the minimum threshold of 6. Integration and e2e tests are not applicable because this issue only introduces the internal persistence layer with no API surface. Those verification layers will be added when the API endpoints issue (future) is implemented.
