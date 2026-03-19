# Doc Impact Analysis: TRE-37

## Summary

TRE-37 adds the first API router module (`lists.py`) with four CRUD + reorder endpoints and registers it in `main.py`. This is the first concrete router in the `routers/` package established by TRE-35. The primary doc impact is updating agent context docs to reflect the new router pattern so that subsequent endpoint issues (boards, cards) follow the same conventions.

---

## Checklist

- [x] `docs/agents/implementation.md` — UPDATE: Document the router implementation pattern established by `lists.py` — Pydantic request models defined in the router file, `request.app.state.db` for database access, route ordering requirement for parameterized vs. static paths, structured logging per endpoint, and `app.include_router(router, prefix="/api")` registration pattern in `main.py`. Future endpoint agents (boards router, cards router) should follow this template.

- [x] `docs/agents/design-feedback-loop.md` — UPDATE: Add `lists.py` router as a reference pattern for API endpoint test scaffolds. Future Design Feedback Loop Agents writing tests for board or card endpoints should reference `test_api_lists.py` as the canonical example of how to use the `db` and `client` fixtures to test CRUD endpoints with position management, 404 handling, and CASCADE delete verification.

- [x] `README.md` — UPDATE: Add API endpoint documentation section listing the four list endpoints (`POST /api/lists`, `PUT /api/lists/{id}`, `DELETE /api/lists/{id}`, `PUT /api/lists/reorder`) with their request/response schemas. This is the first set of business endpoints beyond `/health`.

---

## No Impact

The following categories were checked and require no update:

- `docs/architecture/` — No new architectural decisions. The router pattern is standard FastAPI and does not warrant an ADR. The database layer, model structure, and test infrastructure were all established in prior issues.
- `docs/conventions/golden-principles.md` — No new conventions introduced. The router follows existing principles (one responsibility per file, validate at boundaries, TDD).
- `docs/guides/workflow-customization.md` — Orca workflow unchanged.
- `docs/agents/scoping.md` — Scoping process and subsystem boundaries unchanged.
- `docs/agents/planning.md` — Planning process unchanged.
- `docs/agents/validation.md` — Validation process unchanged.
- `docs/agents/docs-update.md` — Documentation update process unchanged.
- `docs/runbooks/` — No operational procedures changed; list endpoints don't introduce new operational concerns beyond what the app already has.
- `docs/specs/` — No specs directory exists; implementation matches issue specification exactly.
- `deploy/` — No deployment configuration changes needed; the router is automatically included via `main.py` registration.

---

## Summary Table

| Document | Impact Level | Action |
|---|---|---|
| `docs/agents/implementation.md` | Medium | **Update** — document router pattern for future endpoint agents |
| `docs/agents/design-feedback-loop.md` | Low | **Update** — reference `test_api_lists.py` as canonical test pattern |
| `README.md` | Low | **Update** — add list API endpoint documentation |
