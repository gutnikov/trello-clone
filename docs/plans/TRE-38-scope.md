# Scope Report: TRE-38

## Summary
This issue implements the card API router with four endpoints (POST create, PUT update title, DELETE remove, PUT move/reorder) and registers it in `main.py`. It also requires a comprehensive test file covering all seven specified test cases. The database layer (`Database` class) already has all necessary CRUD methods (`create_card`, `get_card`, `update_card`, `delete_card`, `get_cards_by_list`), the `Card` model is defined, and test fixtures (`db`, `client`) are available in `conftest.py`. The work is a single cohesive API feature within the routing subsystem.

## Affected Files
- `backend/src/app/routers/cards.py` — **NEW** — FastAPI APIRouter with 4 endpoints: POST `/api/cards` (create card with auto-assigned position), PUT `/api/cards/{id}` (update title), DELETE `/api/cards/{id}` (remove card), PUT `/api/cards/{id}/move` (move card between lists and/or reorder within list, updating positions of affected cards in both source and target lists)
- `backend/src/app/main.py` — **MODIFY** — add `from app.routers.cards import router as cards_router` import and `app.include_router(cards_router, prefix="/api")` registration (~2 lines)
- `backend/tests/test_api_cards.py` — **NEW** — 7 test cases: POST creates card in list, PUT updates title, PUT returns 404 for missing card, DELETE removes card, DELETE returns 404 for missing card, PUT move between lists, PUT move reorder within same list

## Subsystems Involved
- **API routing layer** — creating the card router module with endpoint handlers, request/response schemas, and position management logic; registering the router in the FastAPI app

## Scope Score: 6/10
- Files: 1pt (3 files affected)
- Subsystems: 1pt (1 subsystem — API/routing layer; tests are verification of the same subsystem)
- LOC estimate: 2pt (~150-200 lines total — router ~80 lines including move/reorder logic, tests ~120 lines for 7 test cases, main.py ~2 lines)
- Migration: 0pt (no schema or data migration; cards table already exists)
- API surface: 2pt (4 new public REST endpoints being added)
- **Total: 6/10**

## Decision: ATOMIC
The issue is a single cohesive feature: CRUD + move endpoints for cards. All three affected files serve the same purpose (exposing card operations via REST API). The database layer already provides all necessary methods (`create_card`, `get_card`, `get_cards_by_list`, `update_card`, `delete_card`), the `Card` model exists with proper validation, and test fixtures are in place. The move endpoint has moderate complexity (reordering positions in source/target lists), but this is contained within a single handler function. Decomposing into sub-issues (e.g., "basic CRUD" vs "move endpoint") would create artificial boundaries and excessive overhead for what is a tightly coupled set of related endpoints sharing the same router, models, and database methods.
