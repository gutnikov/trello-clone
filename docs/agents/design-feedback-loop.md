<!-- Project customize blocks for design-feedback-loop.md -->

### Unit Tests (Backend)
- Location: `backend/tests/`
- Framework: pytest + pytest-asyncio
- Naming: `test_*.py`
- Run: `cd backend && uv run python -m pytest tests/ -v`

### Unit Tests (Frontend)
- Location: `frontend/tests/`
- Framework: vitest
- Naming: `*.test.ts` / `*.test.tsx`
- Run: `cd frontend && pnpm vitest run`

### E2E Tests
- Location: `frontend/e2e/`
- Framework: Playwright
- Config: `frontend/playwright.config.ts`
- Naming: `*.spec.ts`
- Run locally: `cd frontend && pnpm e2e` (auto-starts dev server)
- Run against staging: `cd frontend && BASE_URL=http://2.56.122.47:400N pnpm e2e`
- Headed mode: `cd frontend && pnpm e2e:headed`

### Shared Test Fixtures
- **Location:** `backend/tests/conftest.py`
- **Available fixtures:** `db` (in-memory Database with schema + seeded default board), `client` (httpx AsyncClient wired to the test app)
- When writing test scaffolds for API endpoint tests, use the `db` and `client` fixtures from conftest rather than creating new fixture setup. Tests can simply declare `db: Database` or `client: httpx.AsyncClient` as parameters.

### Canonical API Endpoint Test Pattern
- **Reference:** `backend/tests/test_api_lists.py` — the canonical example for API endpoint test scaffolds.
- **Structure:** Organize tests into classes by operation (e.g., `TestCreateList`, `TestUpdateList`, `TestDeleteList`, `TestReorderLists`). Each class groups related test cases for a single endpoint.
- **Patterns to follow:**
  - Use `db` fixture to set up preconditions (create boards, lists, cards) via `Database` methods before calling the API.
  - Use `client` fixture (`httpx.AsyncClient`) to make HTTP requests against the test app.
  - Test auto-assigned position management (verify sequential positions on creation).
  - Test 404 handling for non-existent resources with both status code and `detail` message assertions.
  - Test CASCADE delete behavior by verifying child entities (e.g., cards) are removed when a parent (e.g., list) is deleted.
  - Include descriptive assertion messages explaining expected vs. actual values.

### Staging
- **Available:** yes (per-PR Docker Compose preview deploys on `2.56.122.47`)
