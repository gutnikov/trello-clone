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

### Staging
- **Available:** yes (per-PR Docker Compose preview deploys on `2.56.122.47`)
