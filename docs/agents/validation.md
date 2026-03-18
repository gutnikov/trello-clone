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

### CI
- Platform: GitHub Actions
- Workflow: `.github/workflows/ci.yml`
- Trigger: push to main, PRs to main
- Lint job: runs pre-commit (ruff + biome), mypy, tsc
- Test job: runs pytest + vitest

### Staging Environment
- **Approach:** Docker Compose staging
- **URL source:** `.orca/staging-url` (written by deploy-staging CI job, needs customization)
- **Deploy workflow:** `.github/workflows/deploy-staging.yml`
- **Cleanup workflow:** `.github/workflows/cleanup-staging.yml`
- **Docker Compose:** `docker-compose.staging.yml`
- **Logs:** `docker compose -f docker-compose.staging.yml logs`
- **E2E against staging:** not yet configured
