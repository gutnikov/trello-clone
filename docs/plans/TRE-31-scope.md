# Scope Report: TRE-31

## Summary
This issue introduces the foundational data layer for the Trello clone backend: three Pydantic models (Board, List, Card) with position/ordering fields, a SQLite persistence layer using aiosqlite for async CRUD operations, schema initialization on first run, a default board seed, and corresponding unit tests. The backend currently has a minimal FastAPI scaffold with only a health endpoint, structured logging, and a smoke test — no models or database code exists yet. All files are new or minor modifications to an existing config file, and the work is contained entirely within the `backend/` directory.

## Affected Files
- `backend/src/app/models.py` (new) — Pydantic models for Board (id, title), List (id, title, board_id, position), Card (id, title, list_id, position)
- `backend/src/app/database.py` (new) — SQLite persistence layer with async support via aiosqlite; schema initialization (CREATE TABLE), CRUD operations for all three entities, and default board seeding on first startup
- `backend/pyproject.toml` (modify) — Add `aiosqlite` to the project dependencies list
- `backend/tests/test_models.py` (new) — Unit tests for Pydantic model validation, defaults, and constraints
- `backend/tests/test_database.py` (new) — Unit tests for database CRUD operations (create, read, update, delete) for Board, List, and Card, plus schema initialization and default seed verification

## Subsystems Involved
- **Data Models** — New Pydantic model definitions for the core domain entities (Board, List, Card); no existing model layer exists
- **Persistence/Database** — New SQLite database layer with async support; includes schema management and CRUD operations; no existing database infrastructure in the project

## Scope Score: 6/10
- Files: 2pt (5 files affected)
- Subsystems: 2pt (2 subsystems: data models + persistence)
- LOC estimate: 2pt (~200-250 lines across all files)
- Migration: +0pt (greenfield schema initialization, no existing data to migrate)
- API surface: +0pt (no public REST API endpoints added or modified; internal persistence layer only)
- **Total: 6/10**

## Decision: ATOMIC
The scope score of 6 is at the atomic threshold. The work is well-defined with clear boundaries: three straightforward Pydantic models, a single-file database module with standard CRUD patterns, a minor dependency addition, and two test files. All changes are confined to the `backend/` directory within two closely related subsystems (models and persistence). There are no migrations, no API surface changes, and no cross-cutting concerns. The issue description is specific enough to implement without ambiguity. Decomposition would add overhead without meaningful benefit at this scope level.
