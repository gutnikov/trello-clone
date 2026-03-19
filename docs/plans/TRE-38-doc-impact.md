# Doc Impact Analysis: TRE-38

## Overview

TRE-38 adds the card API router — the first router module in the project — with four endpoints (create, update, delete, move) and registers it in `main.py`. Documentation impact is low-to-medium: the existing agent context docs already describe the router pattern and test fixtures, so the main additions are documenting the new card API endpoints and the router implementation pattern now that a concrete example exists.

---

## Impacted Documents

### 1. `docs/agents/implementation.md` — Router Pattern Documentation

- **Impact:** MEDIUM — Update recommended
- **Reason:** TRE-38 creates the first router module in the project. The implementation agent context doc (`docs/agents/implementation.md:59`) mentions the router package but has no concrete example of how to structure a router module. Now that `cards.py` exists, the doc should reference it as the canonical pattern for future routers (boards, lists).
- **Action:** Add a subsection under "App Configuration" or as a new section documenting:
  - Router module structure: `APIRouter` with tags, request schema models, `_get_db` helper pattern
  - Registration pattern: `from app.routers.cards import router as cards_router` + `app.include_router(cards_router, prefix="/api")`
  - How request body schemas relate to domain models (separate mutable Pydantic models vs frozen domain models)
  - Reference `backend/src/app/routers/cards.py` as the canonical example

### 2. `README.md` — API Endpoints

- **Impact:** LOW — Minor update
- **Reason:** The README describes the tech stack and configuration but has no mention of available API endpoints. With four new card endpoints, the README should list them for contributor orientation.
- **Action:** Add an "API Endpoints" section (or brief table) documenting:
  - `POST /api/cards` — Create a card
  - `PUT /api/cards/{id}` — Update card title
  - `DELETE /api/cards/{id}` — Delete a card
  - `PUT /api/cards/{id}/move` — Move/reorder a card
  - `GET /health` — Health check (already exists)
  - Note: this section will grow as boards and lists routers are added

### 3. `docs/agents/design-feedback-loop.md` — API Test Pattern

- **Impact:** LOW — Optional update
- **Reason:** The design feedback loop agent doc (`docs/agents/design-feedback-loop.md:26-27`) already mentions shared test fixtures. With `test_api_cards.py` as the first API endpoint test file, the doc could reference it as a pattern for writing failing test scaffolds for future endpoint issues.
- **Action:** Optionally add a note referencing `backend/tests/test_api_cards.py` as the canonical API endpoint test pattern — class-based organization, use of `db` and `client` fixtures, creating prerequisite data via `db` fixture methods before HTTP requests.

---

## Documents NOT Impacted

| Document | Reason |
|---|---|
| `CLAUDE.md` | No structural changes to the project map; `routers/cards.py` is under the existing `backend/` structure already referenced |
| `docs/conventions/golden-principles.md` | No new conventions introduced — the router follows standard FastAPI patterns |
| `docs/guides/workflow-customization.md` | Orca workflow unchanged |
| `docs/agents/scoping.md` | Scoping process unchanged |
| `docs/agents/planning.md` | Planning process unchanged |
| `docs/agents/validation.md` | Validation process unchanged |
| `docs/agents/docs-update.md` | Docs process unchanged |
| `docs/architecture/` | No new architectural decisions — the card router follows the standard FastAPI APIRouter pattern, not an architectural choice. SQLite persistence is already covered by ADR-001. |
| `docs/runbooks/` | No operational procedures changed |
| `backend/src/app/models.py` | Card model already exists and is unchanged |
| `backend/src/app/database.py` | All card CRUD methods already exist and are unchanged |
| `backend/tests/conftest.py` | Shared fixtures already exist and are unchanged |
| `frontend/` docs | No frontend changes |

---

## Summary

| Document | Impact Level | Action |
|---|---|---|
| `docs/agents/implementation.md` | Medium | **Update** — document the router module pattern and registration using `cards.py` as canonical example |
| `README.md` | Low | Add API endpoints section listing the four card endpoints |
| `docs/agents/design-feedback-loop.md` | Low | Optional — reference `test_api_cards.py` as canonical API test pattern |
