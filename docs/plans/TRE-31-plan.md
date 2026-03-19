# Implementation Plan: TRE-31

## Overview

Introduce the core data layer for the Trello clone backend: three Pydantic models (Board, List, Card) with position/ordering fields and a SQLite persistence layer built on `aiosqlite`. The work adds two new source modules (`models.py`, `database.py`), one dependency change (`pyproject.toml`), and two test files. All changes are confined to `backend/` and follow existing project conventions (Python 3.12, FastAPI, structlog, strict mypy, ruff, pytest-asyncio).

## Steps

### Step 1: Add `aiosqlite` dependency to `backend/pyproject.toml`

- **Files:** `backend/pyproject.toml`
- **Changes:** Add `"aiosqlite>=0.20.0"` to the `dependencies` list (line 6-10). This must be a runtime dependency, not a dev dependency, because the persistence layer is part of the application.
- **Depends on:** None

### Step 2: Define Pydantic models in `backend/src/app/models.py`

- **Files:** `backend/src/app/models.py` (new)
- **Changes:**
  - Import `pydantic.BaseModel` and `uuid` (Pydantic ships with FastAPI, no new dependency needed).
  - Define `Board` model with fields:
    - `id: str` — UUID string, default generated via `uuid.uuid4()`
    - `title: str` — board title, non-empty
  - Define `List` model with fields:
    - `id: str` — UUID string, default generated
    - `title: str` — list title, non-empty
    - `board_id: str` — foreign key reference to Board
    - `position: int` — ordering field, default `0`
  - Define `Card` model with fields:
    - `id: str` — UUID string, default generated
    - `title: str` — card title, non-empty
    - `list_id: str` — foreign key reference to List
    - `position: int` — ordering field, default `0`
  - Use `pydantic.Field` for constraints (e.g., `min_length=1` on title fields).
  - All models should use `model_config = ConfigDict(frozen=True)` to enforce immutability (changes produce new instances).
- **Depends on:** Step 1 (Pydantic is already available via FastAPI, but the dependency step should be first to keep ordering clean)

### Step 3: Implement SQLite persistence layer in `backend/src/app/database.py`

- **Files:** `backend/src/app/database.py` (new)
- **Changes:**
  - Import `aiosqlite`, `pathlib.Path`, models from `app.models`, and `structlog` logger from `app.logging`.
  - Define a `Database` class that encapsulates all persistence operations:
    - `__init__(self, db_path: str | Path)` — store the database file path (default: `data/trello.db` relative to project root, or configurable).
    - `async connect(self) -> None` — open the aiosqlite connection, enable WAL mode, enable foreign keys.
    - `async close(self) -> None` — close the connection.
    - `async init_schema(self) -> None` — execute `CREATE TABLE IF NOT EXISTS` for `boards`, `lists`, `cards` tables with appropriate columns, types, and foreign key constraints. Use `TEXT` for UUIDs, `INTEGER` for position, and `FOREIGN KEY` references.
    - `async seed_default_board(self) -> Board` — check if any board exists; if not, insert a default board (title: "My Board") and return it. Log the seed action.
  - CRUD methods for Board:
    - `async create_board(self, board: Board) -> Board`
    - `async get_board(self, board_id: str) -> Board | None`
    - `async list_boards(self) -> list[Board]`
    - `async update_board(self, board_id: str, title: str) -> Board | None`
    - `async delete_board(self, board_id: str) -> bool`
  - CRUD methods for List:
    - `async create_list(self, lst: List) -> List`
    - `async get_list(self, list_id: str) -> List | None`
    - `async get_lists_by_board(self, board_id: str) -> list[List]` — ordered by position
    - `async update_list(self, list_id: str, title: str | None = None, position: int | None = None) -> List | None`
    - `async delete_list(self, list_id: str) -> bool`
  - CRUD methods for Card:
    - `async create_card(self, card: Card) -> Card`
    - `async get_card(self, card_id: str) -> Card | None`
    - `async get_cards_by_list(self, list_id: str) -> list[Card]` — ordered by position
    - `async update_card(self, card_id: str, title: str | None = None, position: int | None = None, list_id: str | None = None) -> Card | None`
    - `async delete_card(self, card_id: str) -> bool`
  - All CRUD methods should use parameterized queries (never string interpolation) to prevent SQL injection.
  - Add structured logging (via `app.logging.get_logger()`) for connection lifecycle events, schema initialization, and seed operations.
  - Use `aiosqlite.Connection` type hints properly for mypy strict mode.
- **Depends on:** Step 2 (models must exist to type CRUD methods)

### Step 4: Write unit tests for models in `backend/tests/test_models.py`

- **Files:** `backend/tests/test_models.py` (new)
- **Changes:**
  - Test Board creation with valid title; verify `id` is auto-generated UUID.
  - Test Board creation with explicit id.
  - Test Board rejects empty title (validation error).
  - Test List creation with valid fields; verify position defaults to 0.
  - Test List creation with explicit position.
  - Test List rejects empty title.
  - Test Card creation with valid fields; verify position defaults to 0.
  - Test Card creation with explicit position.
  - Test Card rejects empty title.
  - Test model immutability (frozen config — assignment raises error).
- **Depends on:** Step 2 (models must be defined)

### Step 5: Write unit tests for database CRUD in `backend/tests/test_database.py`

- **Files:** `backend/tests/test_database.py` (new)
- **Changes:**
  - Use `pytest-asyncio` and an in-memory SQLite database (`:memory:`) for fast, isolated tests.
  - Create a `db` fixture that initializes a `Database` instance with `:memory:`, calls `connect()` and `init_schema()`, yields it, then calls `close()`.
  - Test `init_schema` creates the three tables (query `sqlite_master`).
  - Test `seed_default_board` creates a board when none exist.
  - Test `seed_default_board` is idempotent (calling twice returns the same board, doesn't create duplicates).
  - Test Board CRUD: create, get, list, update, delete.
  - Test List CRUD: create, get by id, get by board (ordered by position), update title, update position, delete.
  - Test Card CRUD: create, get by id, get by list (ordered by position), update title, update position, update list_id (move card), delete.
  - Test cascade or referential integrity: deleting a board should handle associated lists/cards (decide on CASCADE vs. application-level enforcement — recommend CASCADE for simplicity in v0).
  - Test get returns None for non-existent id.
  - Test delete returns False for non-existent id.
- **Depends on:** Step 3 (database module must exist), Step 4 (model tests should pass first to confirm models work)

## Risk Factors

- **aiosqlite version compatibility** — Pin `>=0.20.0` to ensure Python 3.12 support. Mitigation: the library is mature and well-maintained; lock file (`uv.lock`) will pin the exact version after install.
- **mypy strict mode with aiosqlite** — `aiosqlite` may not have complete type stubs. Mitigation: use inline `# type: ignore` comments sparingly where needed, or add `aiosqlite` to mypy's `[[tool.mypy.overrides]]` with `ignore_missing_imports = true`.
- **SQLite foreign key enforcement** — SQLite does not enforce foreign keys by default. Mitigation: execute `PRAGMA foreign_keys = ON` on every connection open (included in Step 3's `connect()` method).
- **Position field conflicts** — No uniqueness constraint on position within a list/board, allowing duplicate positions. Mitigation: acceptable for v0; the API layer (future issue) will manage position rebalancing. Document this as a known limitation.
- **Naming collision with `List`** — Python's built-in `list` type conflicts with the `List` model name. Mitigation: use `from __future__ import annotations` to defer evaluation, and use `list[...]` (lowercase) for Python's built-in type in type hints. Consider naming the model `TaskList` instead if the collision proves problematic for imports throughout the codebase.
