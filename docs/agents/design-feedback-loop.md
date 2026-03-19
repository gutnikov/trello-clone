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

### Frontend API Client Tests
- **Canonical example:** `frontend/tests/api.test.ts` — demonstrates testing the API client module (`frontend/src/lib/api.ts`) using vitest with `globalThis.fetch` mocked via `vi.fn()`.
- **Pattern:** Mock `fetch` to return controlled `Response` objects, then assert the API function returns the correct typed result or throws on error responses. Each API function gets its own `describe` block.
- **Board store tests:** `frontend/tests/board-store.test.ts` — tests React Query hooks by wrapping them in a `QueryClientProvider` and asserting on query/mutation behavior.

### Frontend Component Tests
- **Canonical example:** `frontend/tests/board-components.test.tsx` — demonstrates testing React display components using `@testing-library/react` with `vitest` and `jsdom`.
- **Pattern:** Use `render()` to mount the component, `screen.getByText()` / `screen.getByTestId()` to find elements, and `within()` for scoped queries inside specific containers. Each component gets its own `describe` block covering export verification and rendering behavior.
- **Props setup:** Construct typed props objects with test data (board with lists, list with cards, etc.) and pass them directly to the component under test.
- **Position ordering:** Test that items render in `position` order by verifying DOM node order via `getAllByTestId()`.

### E2E Tests
- Location: `frontend/e2e/`
- Framework: Playwright
- Config: `frontend/playwright.config.ts`
- Naming: `*.spec.ts`
- Run locally: `cd frontend && pnpm e2e` (auto-starts dev server)
- Run against staging: `cd frontend && BASE_URL=http://2.56.122.47:400N pnpm e2e`
- Headed mode: `cd frontend && pnpm e2e:headed`
- **E2E data seeding pattern:** `frontend/e2e/board.spec.ts` demonstrates seeding test data via the API before assertions and cleaning up afterward. Use `page.request.post("/api/...")` to create lists/cards, wrap assertions in `try/finally` to ensure cleanup via `page.request.delete(...)`, and use `timeout` options on `toBeVisible()` for SSR data loading.

### Shared Test Fixtures
- **Location:** `backend/tests/conftest.py`
- **Available fixtures:** `db` (in-memory Database with schema + seeded default board), `client` (httpx AsyncClient wired to the test app)
- When writing test scaffolds for API endpoint tests, use the `db` and `client` fixtures from conftest rather than creating new fixture setup. Tests can simply declare `db: Database` or `client: httpx.AsyncClient` as parameters.
- **Canonical API test example:** `backend/tests/test_api_cards.py` — demonstrates class-based test organization (one class per endpoint group), async helper functions for creating prerequisite data via the `db` fixture, and HTTP assertions against the `client` fixture.

### API Endpoint Test Patterns
The canonical pattern for API integration tests is established in `backend/tests/test_api_boards.py`. Follow this pattern for new endpoint tests:

- **Fixtures:** Use the `client` fixture (`httpx.AsyncClient`) for HTTP requests and `db` fixture (`Database`) for test data setup. Both come from `conftest.py`.
- **Test class grouping:** Group tests by endpoint (e.g., `TestGetBoard`, `TestPutBoard`, `TestBoardRouterRegistration`).
- **Test coverage per endpoint:**
  - HTTP status code (200, 404, 422)
  - Response JSON structure (required keys, correct types)
  - Field values and ordering (e.g., lists/cards sorted by position)
  - Validation error responses (empty/missing required fields return 422)
  - Persistence verification (PUT followed by GET to confirm update)
  - Router registration (endpoint reachable at `/api/...` prefix, not at bare path)
- **Test data setup:** The `db` fixture provides a seeded default board. Create additional test data directly via `db.create_list()` / `db.create_card()` within the test method — no extra fixtures needed.
- **Assertion messages:** Include descriptive assertion messages to make failures easy to diagnose.

#### List API Endpoint Tests
- **Reference:** `backend/tests/test_api_lists.py` — extends the canonical pattern for list CRUD and reorder endpoints.
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
