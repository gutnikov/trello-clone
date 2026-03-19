# ADR-001: SQLite Persistence with Decoupled Pydantic Models

**Date:** 2026-03-19
**Status:** Accepted

## Context

TRE-31 introduces the first persistence layer for the Trello clone backend. The application needs to store Board, List, and Card entities with positional ordering. Key forces at play:

- The v0 scope is a single-board application — no multi-tenant or high-concurrency requirements yet.
- The team wants zero-config local development (no external database server).
- The backend uses FastAPI with async request handling, so the persistence layer must support async operations.
- Data models need to be usable independently of the storage mechanism for testing and future flexibility.

## Decision

### 1. SQLite via aiosqlite as the persistence backend

We chose SQLite (via the `aiosqlite` library) for the v0 data store. The database file lives at `data/trello.db` by default and is configurable via the `Database` constructor. WAL mode and foreign key enforcement are enabled on every connection (`backend/src/app/database.py:31-32`).

### 2. Pydantic models decoupled from the database layer

Data models (`Board`, `List`, `Card`) are defined as pure frozen Pydantic `BaseModel` subclasses in `backend/src/app/models.py`. They have no awareness of SQLite or any ORM. The `Database` class in `backend/src/app/database.py` manually maps between Pydantic models and SQL rows.

### 3. Schema initialization and default board seeding

Tables are created via `Database.init_schema()` using `CREATE TABLE IF NOT EXISTS`, making it idempotent. A default board is seeded via `Database.seed_default_board()`, which is also idempotent (skips if any board exists).

## Consequences

### Positive
- Zero external dependencies for storage — no database server to install or configure
- Async-compatible via `aiosqlite`, integrating cleanly with FastAPI's async handlers
- Pydantic models can be tested in isolation without any database
- Schema is self-initializing — no migration tool needed for v0
- WAL mode provides reasonable read concurrency for the single-board use case

### Negative
- SQLite does not support concurrent writes from multiple processes — will need migration if the application scales beyond a single instance
- No migration framework — schema changes require manual `ALTER TABLE` or a future adoption of Alembic or similar
- Manual SQL-to-model mapping in the `Database` class is repetitive and must be maintained in sync with models

### Neutral
- The `data/` directory must be persisted across deployments (relevant for Docker volumes and production deploy)
- Foreign keys with `ON DELETE CASCADE` handle referential integrity automatically

## Alternatives Considered

- **PostgreSQL:** Rejected for v0 — adds operational complexity (server management, connection pooling) that is unnecessary for a single-board MVP. Can be adopted later without changing the Pydantic models.
- **SQLAlchemy ORM:** Rejected — introduces a heavy abstraction layer not justified at this scale. The current manual mapping is ~100 lines and easy to understand. ORM would also couple models to the database layer, reducing testability.
- **In-memory dict store:** Rejected — no persistence across restarts, no relational integrity guarantees. Would need to be replaced immediately for any production use.
