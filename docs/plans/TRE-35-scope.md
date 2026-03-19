# Scope Report: TRE-35

## Summary
This issue sets up foundational API infrastructure: a router package init, CORS middleware and database lifespan management in the FastAPI app, and shared pytest fixtures (in-memory DB + httpx AsyncClient) for all future API test modules. The work is well-scoped, with clear requirements touching only 3 files across 2 subsystems, and estimated at under 80 lines of new/modified code.

## Affected Files
- `backend/src/app/routers/__init__.py` — **NEW** — empty router package init file to establish the routers module
- `backend/src/app/main.py` — **MODIFY** — add CORS middleware (allow all origins for dev, configurable for prod), add lifespan async context manager (connect DB, init schema, seed default board on startup; close DB on shutdown), expose `app.state.db`
- `backend/tests/conftest.py` — **NEW** — shared pytest fixtures: in-memory `Database` instance with schema+seed, httpx `AsyncClient` wired to the FastAPI test app, `db` and `client` fixtures available to all test modules

## Subsystems Involved
- **FastAPI application layer** — adding middleware configuration and lifespan lifecycle hooks to `main.py`
- **Test infrastructure** — creating shared conftest.py with reusable async fixtures for API integration testing

## Scope Score: 4/10
- Files: 1pt (3 files affected)
- Subsystems: 2pt (2 subsystems: app layer + test infra)
- LOC estimate: 1pt (~60-80 lines total — CORS config ~10 lines, lifespan context manager ~15 lines, conftest fixtures ~30 lines, router __init__.py ~1 line)
- Migration: 0pt (no schema or data migration)
- API surface: 0pt (no new public endpoints; CORS is middleware configuration, not an API surface change)
- **Total: 4/10**

## Decision: ATOMIC
The issue is well-defined with 3 files, 2 subsystems, and under 100 lines of code. All three deliverables are tightly coupled (the conftest depends on the lifespan/DB patterns established in main.py, and the router init is a prerequisite for future endpoint sub-issues). Decomposing further would create unnecessary overhead for what is fundamentally a single coherent scaffolding task. The existing `Database` class, models, and test patterns provide clear templates to follow.
