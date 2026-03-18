<!-- Project customize blocks for implementation.md -->

### Build & Run
- `make install` — install all dependencies (backend + frontend)
- `make dev` — start both backend (port 8000) and frontend (port 3000) dev servers
- `make dev-backend` — start only the backend dev server
- `make dev-frontend` — start only the frontend dev server
- `make lint` — run all linters
- `make lint-fix` — auto-fix lint issues
- `make type-check` — run type checkers
- `make test` — run all tests

### Style
- **Backend (Python):** Run `cd backend && uv run ruff check src/ tests/` and `cd backend && uv run ruff format src/ tests/` before committing
- **Frontend (TypeScript):** Run `cd frontend && pnpm biome check --fix ./src` before committing
- Follow existing patterns in the codebase

### Task Management
- **Tracker:** Linear
- **Project:** TRE
- **Active states:** Scoping, Planning, Design Feedback Loop, Implementing, Validating, Docs, Review
- **Terminal states:** Done, Closed, Cancelled
- **API endpoint:** https://api.linear.app/graphql
