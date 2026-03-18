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
10. **E2E tests:** `cd frontend && pnpm e2e` (Playwright, or `BASE_URL=... pnpm e2e` against staging)

### CI
- **Platform:** GitHub Actions on self-hosted runners
- **Host:** `deploy@2.56.122.47` (Ubuntu 22.04, 8 cores, 16GB RAM)
- **Runners:** 4 parallel (`trello-clone-runner`, `-2`, `-3`, `-4`)
- **Workflow:** `.github/workflows/ci.yml`
- **Trigger:** push to main, PRs to main
- **Lint job:** runs pre-commit (ruff + biome), mypy, tsc
- **Test job:** runs pytest + vitest

### Staging Environment
- **Host:** `deploy@2.56.122.47`
- **Approach:** Per-PR Docker Compose stacks with isolated project names
- **Port scheme:** PR #N -> frontend `:400N`, backend `:900N`
- **Deploy workflow:** `.github/workflows/deploy-staging.yml`
- **Cleanup workflow:** `.github/workflows/cleanup-staging.yml`
- **Docker Compose:** `docker-compose.staging.yml`
- **Logs:** `docker compose -p preview-pr-{N} logs`
- **E2E against staging:** `cd frontend && BASE_URL=http://2.56.122.47:400N pnpm e2e` (runs automatically after deploy)

### Production Deployment
- **Host:** `deploy@2.56.122.47`
- **Trigger:** auto-on-merge to main
- **Deploy workflow:** `.github/workflows/deploy-prod.yml`
- **Ports:** frontend `:3999`, backend `:8999`
- **Rollback:** `ssh deploy@2.56.122.47 "cd /home/deploy/production && git checkout <prev-sha> && docker compose -p production up -d --build --wait"`
- **Health check:** `curl http://2.56.122.47:8999/health`
