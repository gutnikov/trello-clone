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
- Location: `e2e/`
- Framework: agent-browser (shell scripts)
- Run locally: `./e2e/smoke.sh http://localhost:3000`
- Run against staging: `./e2e/smoke.sh http://2.56.122.47:400N`

### E2E Capabilities
- **Available:** yes
- **Framework:** agent-browser (CLI browser automation)
- **Staging:** yes (per-PR preview deploys on `2.56.122.47`)
- **Run locally:** `./e2e/smoke.sh`
- **Run against staging:** `./e2e/smoke.sh $PREVIEW_URL`
