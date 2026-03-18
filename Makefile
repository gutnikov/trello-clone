.PHONY: install dev dev-backend dev-frontend lint lint-fix type-check test

# Install all dependencies
install:
	cd backend && uv sync --all-extras
	cd frontend && pnpm install

# Start both backend and frontend dev servers
dev:
	@echo "Starting backend on :8000 and frontend on :3000..."
	@$(MAKE) dev-backend & $(MAKE) dev-frontend & wait

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && pnpm dev

# Lint and format
lint:
	cd backend && uv run ruff check src/ tests/
	cd backend && uv run ruff format --check src/ tests/
	cd frontend && pnpm biome check ./src

lint-fix:
	cd backend && uv run ruff check --fix src/ tests/
	cd backend && uv run ruff format src/ tests/
	cd frontend && pnpm biome check --fix ./src

# Type checking
type-check:
	cd backend && uv run python -m mypy src/
	cd frontend && pnpm exec tsc --noEmit

# Run all tests
test:
	cd backend && uv run python -m pytest tests/ -v
	cd frontend && pnpm vitest run
