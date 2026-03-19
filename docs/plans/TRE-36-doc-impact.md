# Doc Impact Analysis: TRE-36

## Overview

TRE-36 adds the first API router to the codebase (`GET /api/board` and `PUT /api/board`). The documentation impact is focused on recording the API surface, updating agent context docs with the router pattern and response schema conventions, and ensuring the README reflects the new endpoints. No architectural decisions warrant a new ADR — the router follows standard FastAPI patterns.

---

## Impacted Documents

### 1. `docs/agents/implementation.md` — Router Pattern and DB Access Convention

- **Impact:** MEDIUM — Update recommended
- **Reason:** TRE-36 establishes the canonical router implementation pattern: database access via `request.app.state.db`, response schemas defined in the router file, router registration with `/api` prefix in `main.py`. Future implementation agents (TRE-37 lists, TRE-38 cards) need to follow this exact pattern. The implementation agent context doc should document it explicitly.
- **Action:** Add a section documenting:
  - Route handlers access the database via `db: Database = request.app.state.db`
  - Response/request Pydantic schemas are defined in the router file alongside the endpoints
  - Routers use `APIRouter(tags=["..."])` with no prefix; the prefix `/api` is set at registration in `main.py`
  - `response_model` is set on each route decorator for automatic response validation
  - Structlog logging is included in each handler for observability

### 2. `docs/agents/design-feedback-loop.md` — API Test Patterns

- **Impact:** MEDIUM — Update recommended
- **Reason:** TRE-36 establishes the pattern for API endpoint integration tests: use `client` fixture from `conftest.py`, test HTTP status codes + response body structure, verify persistence via follow-up GET requests, test validation by sending invalid payloads. The Design Feedback Loop Agent should know this pattern to write correct test scaffolds for future endpoint issues.
- **Action:** Add a section documenting:
  - API tests use the shared `client` fixture (httpx AsyncClient) and `db` fixture from `conftest.py`
  - Test classes are grouped by endpoint (e.g., `TestGetBoard`, `TestPutBoard`)
  - Tests verify: HTTP status code, response JSON structure, field values, ordering, and validation error responses (422)
  - The `db` fixture provides a seeded default board; tests can add lists/cards directly via `db.create_list()` / `db.create_card()` for test data setup

### 3. `README.md` — API Endpoints Documentation

- **Impact:** LOW — Minor update
- **Reason:** TRE-36 adds the first user-facing API endpoints. The README should document available endpoints for contributors and users.
- **Action:** Add an "API Endpoints" section documenting:
  - `GET /api/board` — Returns the board with nested lists and cards
  - `PUT /api/board` — Updates the board title (accepts `{"title": "..."}`)
  - `GET /health` — Health check (already exists, but group it with the new endpoints for completeness)

### 4. `docs/agents/scoping.md` — Reference File for Scope Estimation

- **Impact:** LOW — Optional update
- **Reason:** Now that `backend/src/app/routers/boards.py` exists as a concrete example, the scoping agent can reference its line count and complexity when estimating scope for similar router issues (TRE-37, TRE-38).
- **Action:** Optionally add a note that a single-entity router with 2 endpoints + schemas is approximately 60-80 lines and scores ~6 on the scope scale.

---

## Documents NOT Impacted

| Document | Reason |
|---|---|
| `CLAUDE.md` | No structural changes to the project map; `routers/boards.py` falls under the existing `backend/` structure |
| `docs/conventions/golden-principles.md` | No new conventions introduced; router patterns follow existing FastAPI standards |
| `docs/guides/workflow-customization.md` | Orca workflow unchanged |
| `docs/agents/validation.md` | Validation process unchanged |
| `docs/agents/docs-update.md` | Docs process unchanged |
| `docs/architecture/` | No architectural decisions — using standard FastAPI routers, not introducing a new pattern |
| `docs/runbooks/` | No operational procedures changed |
| `deploy/` configs | No deployment changes; endpoints are available on the existing server |
| `frontend/` docs | No frontend changes |
| `backend/src/app/models.py` | Domain models unchanged; new schemas are response-only and live in the router file |

---

## Summary

| Document | Impact Level | Action |
|---|---|---|
| `docs/agents/implementation.md` | Medium | **Update** — document router pattern, DB access, schema conventions |
| `docs/agents/design-feedback-loop.md` | Medium | **Update** — document API test patterns and fixture usage |
| `README.md` | Low | Add API endpoints documentation section |
| `docs/agents/scoping.md` | Low | Optional — add router scope reference data |
