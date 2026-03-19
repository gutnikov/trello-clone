# Scope Report: TRE-36

## Summary

This issue implements the board router with two API endpoints: `GET /api/board` (returns the single board with nested lists and cards) and `PUT /api/board` (updates the board title). The database layer already provides all necessary CRUD methods (`list_boards`, `get_board`, `update_board`, `get_lists_by_board`, `get_cards_by_list`), so the work is confined to creating the router, adding Pydantic response schemas for the nested structure, registering the router in `main.py`, and writing tests. No schema migrations or database changes are required.

## Affected Files

- `backend/src/app/routers/boards.py` (new) — Board router with `GET /api/board` and `PUT /api/board` endpoints; also defines nested Pydantic response schemas (`CardResponse`, `ListWithCards`, `BoardDetailResponse`, `BoardUpdateRequest`)
- `backend/src/app/main.py` (modify) — Add `include_router()` call to register the board router with prefix `/api`
- `backend/tests/test_api_boards.py` (new) — Integration tests for both endpoints: nested response structure, ordering, title update, and validation error on empty title

## Subsystems Involved

- **FastAPI app layer** — New router module, response schemas, router registration in the application entry point, and HTTP integration tests

## Scope Score: 6/10

- Files: 1pt (3 files affected)
- Subsystems: 1pt (1 subsystem — FastAPI app layer only; database layer is untouched)
- LOC estimate: 2pt (~150-190 lines across router, schemas, registration, and tests)
- Migration: 0pt (no schema or data migration needed)
- API surface: 2pt (2 new public API endpoints)
- **Total: 6/10**

## Decision: ATOMIC

The issue is well-scoped and self-contained. All database methods needed already exist. The work involves creating a single router file with two straightforward endpoints, adding a few lines to register it in `main.py`, and writing ~4 test cases. The three affected files are all within the same subsystem (FastAPI app layer) with clear, non-overlapping responsibilities. There are no cross-cutting concerns, no migrations, and no ambiguity in the requirements. A scope score of 6 is at the atomic threshold and does not warrant decomposition.
