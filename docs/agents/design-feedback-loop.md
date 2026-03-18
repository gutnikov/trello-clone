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

### Staging
- **Available:** yes (Docker Compose based, needs deployment target customization)
