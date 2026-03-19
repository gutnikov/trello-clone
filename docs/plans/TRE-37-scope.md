# Scope Report: TRE-37

## Summary
This issue implements the list API router with four CRUD + reorder endpoints for the Trello clone backend. The database layer (`Database` class) already provides all required CRUD methods (`create_list`, `get_list`, `update_list`, `delete_list`, `get_lists_by_board`), so the work is a thin routing layer that delegates to existing persistence methods plus a test module exercising the endpoints. The test infrastructure (conftest.py with `db` and `client` fixtures) is already in place.

## Affected Files
- `backend/src/app/routers/lists.py` — **NEW** — FastAPI router with 4 endpoints: POST /api/lists (create), PUT /api/lists/{id} (update title), DELETE /api/lists/{id} (delete), PUT /api/lists/reorder (reorder positions). Each endpoint accesses `request.app.state.db` for database operations.
- `backend/src/app/main.py` — **MODIFY** — Add `from app.routers.lists import router as lists_router` and `app.include_router(lists_router, prefix="/api")` (~2 lines added)
- `backend/tests/test_api_lists.py` — **NEW** — 6 test cases using the existing `client` and `db` fixtures from conftest.py: create list with correct position, update title, update 404, delete list and cards, delete 404, reorder positions

## Subsystems Involved
- **FastAPI routing layer** — New router module with endpoint definitions, request/response models, and HTTP status code handling
- **Test infrastructure** — New test module leveraging existing shared fixtures (in-memory DB + httpx AsyncClient)

## Scope Score: 6/10
- Files: 1pt (3 files affected)
- Subsystems: 2pt (2 subsystems: routing layer + test suite)
- LOC estimate: 1pt (~100-130 lines total — router ~60-70 lines for 4 endpoints with Pydantic request models, main.py ~2 lines, tests ~60-80 lines for 6 test cases)
- Migration: 0pt (no schema changes; all tables and CRUD methods already exist in database.py)
- API surface: 2pt (4 new public HTTP endpoints exposed)
- **Total: 6/10**

## Decision: ATOMIC
The scope score of 6 is at the atomic threshold. Key factors supporting an atomic decision:
1. **Database layer is complete** — All five list CRUD methods (`create_list`, `get_list`, `update_list`, `delete_list`, `get_lists_by_board`) already exist in `database.py` with full implementation
2. **Test infrastructure exists** — The `conftest.py` provides `db` (in-memory Database) and `client` (httpx AsyncClient) fixtures ready to use
3. **Clear specification** — The issue explicitly defines all 4 endpoints with their request/response schemas, status codes, and all 6 test cases
4. **Single responsibility** — All changes serve one purpose: exposing list operations via HTTP. The reorder endpoint is slightly more complex (iterating list_ids to update positions) but uses existing `update_list` method
5. **Established patterns** — The router registration pattern in `main.py`, Pydantic models in `models.py`, and test patterns in existing test files provide clear templates to follow
