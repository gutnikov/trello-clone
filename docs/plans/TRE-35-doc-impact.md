# Doc Impact Analysis: TRE-35

## Overview

TRE-35 adds CORS middleware, database lifespan management, and shared test fixtures to the FastAPI application. These are infrastructure changes that affect how the app starts up, how cross-origin requests are handled, and how tests are structured. The documentation impact is modest — primarily updating the implementation agent context doc and potentially the README.

---

## Impacted Documents

### 1. `docs/agents/implementation.md` — Testing Patterns

- **Impact:** MEDIUM — Update recommended
- **Reason:** The new `conftest.py` establishes the canonical testing pattern for all future API endpoint tests. The implementation agent context doc should reference the shared `db` and `client` fixtures so that agents implementing endpoint sub-issues (TRE-36, TRE-37, etc.) use them correctly rather than creating ad-hoc fixtures.
- **Action:** Add a section documenting:
  - The `db` fixture provides an in-memory database with schema and seeded default board
  - The `client` fixture provides an `httpx.AsyncClient` wired to the test app with the test DB
  - Tests should use these fixtures rather than creating their own database/client setup
  - The `test_database.py` local fixture is an intentional exception (it needs unseeded state)

### 2. `docs/agents/design-feedback-loop.md` — Test Fixture Awareness

- **Impact:** LOW — Optional update
- **Reason:** The Design Feedback Loop Agent writes failing test scaffolds. It should know that `conftest.py` provides `db` and `client` fixtures so it writes tests that depend on them rather than duplicating fixture setup.
- **Action:** Add a note that shared fixtures exist in `backend/tests/conftest.py` and should be used for API endpoint tests.

### 3. `README.md` — Environment Variables

- **Impact:** LOW — Minor update
- **Reason:** TRE-35 introduces two environment variables (`CORS_ORIGINS`, `DB_PATH`) that configure runtime behavior. These should be documented for contributors and operators.
- **Action:** Add a brief "Configuration" or "Environment Variables" subsection documenting:
  - `CORS_ORIGINS` — comma-separated allowed origins (default: all origins for dev)
  - `DB_PATH` — path to SQLite database file (default: `data/trello.db`)

### 4. `deploy/` configs — CORS production origins

- **Impact:** LOW — Future concern
- **Reason:** The staging/production deployment configs should set `CORS_ORIGINS` to the actual frontend domain rather than allowing all origins. However, the frontend URL isn't known yet.
- **Action:** Defer to the deployment issue. Flag that `CORS_ORIGINS` must be set in production environment.

---

## Documents NOT Impacted

| Document | Reason |
|---|---|
| `CLAUDE.md` | No structural changes to the project map; `main.py` and `conftest.py` are covered by existing `backend/` references |
| `docs/conventions/golden-principles.md` | No new conventions introduced |
| `docs/guides/workflow-customization.md` | Orca workflow unchanged |
| `docs/agents/scoping.md` | Scoping process unchanged |
| `docs/agents/planning.md` | Planning process unchanged |
| `docs/agents/validation.md` | Validation process unchanged |
| `docs/agents/docs-update.md` | Docs process unchanged |
| `docs/architecture/` | No new architectural decisions — CORS and lifespan are standard FastAPI patterns, not architectural choices. The SQLite decision is already covered by TRE-31's ADR recommendation. |
| `docs/runbooks/` | No operational procedures changed |
| `frontend/` docs | No frontend changes |

---

## Summary

| Document | Impact Level | Action |
|---|---|---|
| `docs/agents/implementation.md` | Medium | **Update** — document shared test fixtures pattern |
| `docs/agents/design-feedback-loop.md` | Low | Optional — note conftest fixtures exist |
| `README.md` | Low | Add `CORS_ORIGINS` and `DB_PATH` environment variable documentation |
| `deploy/` configs | Low | Defer — flag `CORS_ORIGINS` for production setup |
