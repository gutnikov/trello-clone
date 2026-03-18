<!-- Project customize blocks for validation.md -->

### Required Checks

1. **Linting (backend):** `cd backend && uv run ruff check src/ tests/`
2. **Formatting (backend):** `cd backend && uv run ruff format --check src/ tests/`
3. **Linting (frontend):** `cd frontend && pnpm biome lint ./src`
4. **Formatting (frontend):** `cd frontend && pnpm biome format ./src`
5. **Type checking (backend):** `cd backend && uv run python -m mypy src/`
6. **Type checking (frontend):** `cd frontend && pnpm exec tsc --noEmit`
7. **Unit tests (backend):** `cd backend && uv run python -m pytest tests/ -v`
8. **Unit tests (frontend):** `cd frontend && pnpm vitest run`
9. **Pre-commit hooks:** `cd backend && uv run pre-commit install` (install), `cd backend && uv run pre-commit run --all-files` (run all)
