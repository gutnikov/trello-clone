# Project Initialization Specification

## Trello Clone: Repository & Development Environment Setup

---

| Field | Detail |
|---|---|
| **Version** | 1.0 |
| **Date** | March 23, 2026 |
| **Author** | Product Management |
| **Status** | Draft |
| **Scope** | Monorepo setup, toolchain configuration, local dev environment, CI/CD pipeline |

---

## 1. Overview

This document specifies how to initialize the Trello Clone project from zero — repository structure, toolchains, local development environment, testing setup, code quality gates, and CI/CD pipeline. The goal is that a new developer can clone the repo, run one command, and have the full stack running locally within 5 minutes.

Every technical choice made here must support the requirements outlined in PRD Phases 1–5 without requiring a re-architecture later.

---

## 2. Monorepo Structure

A single repository containing both the backend and frontend as top-level packages, with shared configuration at the root.

```
trello-clone/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Main CI pipeline
│       └── e2e.yml                 # Playwright E2E (runs after CI passes)
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Settings / env var loading
│   │   ├── database.py             # SQLAlchemy engine & session
│   │   ├── models/                 # SQLAlchemy models (one file per domain)
│   │   │   ├── __init__.py
│   │   │   ├── board.py
│   │   │   ├── list.py
│   │   │   ├── card.py
│   │   │   └── ...
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── board.py
│   │   │   └── ...
│   │   ├── routers/                # FastAPI routers (one file per domain)
│   │   │   ├── __init__.py
│   │   │   ├── boards.py
│   │   │   └── ...
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   └── ...
│   │   └── utils/                  # Shared helpers
│   │       └── __init__.py
│   ├── migrations/                 # Alembic migrations
│   │   ├── env.py
│   │   ├── alembic.ini
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py             # Fixtures (test DB, test client)
│   │   ├── test_boards.py
│   │   └── ...
│   ├── pyproject.toml              # uv project config, dependencies, ruff config
│   └── uv.lock
├── frontend/
│   ├── app/                        # TanStack Start app directory
│   │   ├── routes/
│   │   │   ├── __root.tsx
│   │   │   ├── index.tsx           # Home dashboard
│   │   │   └── board/
│   │   │       └── $boardId.tsx    # Board view
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components
│   │   │   └── ...                 # App-specific components
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   └── types/
│   ├── tests/
│   │   ├── unit/                   # Vitest unit tests
│   │   └── ...
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   ├── biome.json                  # Biome config (lint + format)
│   └── app.config.ts               # TanStack Start config
├── e2e/
│   ├── tests/
│   │   ├── board.spec.ts
│   │   └── ...
│   ├── playwright.config.ts
│   └── package.json
├── docker-compose.yml              # Local dev: Postgres + Redis (future)
├── .env.example                    # Documented env var template
├── .gitignore
├── .pre-commit-config.yaml         # Pre-commit hook configuration
├── Makefile                        # Convenience commands
└── README.md
```

### 2.1 Key Structural Decisions

- **Backend and frontend are sibling directories**, not nested. Each has its own dependency management and can be built/tested independently.
- **`e2e/` is a separate package** because Playwright tests span both stacks and should not be coupled to either one's build.
- **`Makefile` at the root** provides unified commands (`make dev`, `make test`, `make lint`) that delegate to the appropriate tool in each package.
- **No shared code package between frontend and backend.** TypeScript and Python have no shared runtime. API contract alignment is enforced by Pydantic schemas (backend) generating or informing TypeScript types (frontend).

---

## 3. Backend Stack

### 3.1 Runtime & Package Management

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| uv | Latest | Package management, virtual environment, script running |

**Initialization:**

```bash
cd backend
uv init
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic pydantic pydantic-settings
uv add --dev pytest pytest-asyncio httpx ruff mypy
```

### 3.2 Framework: FastAPI

- **Entry point:** `app/main.py` creates the FastAPI application instance, registers routers, configures CORS middleware, and sets up lifespan events (DB connection pool startup/shutdown).
- **Routers:** One file per domain (`boards.py`, `lists.py`, `cards.py`, etc.). Routers are prefixed: `/api/boards`, `/api/lists`, etc.
- **Dependency injection:** Use FastAPI's `Depends()` for database sessions, auth (Phase 4), and shared services.
- **CORS:** Allow `http://localhost:3000` (frontend dev server) in development. Configurable via env var for production.

### 3.3 Database: SQLAlchemy + Alembic

- **SQLAlchemy 2.0** style with async engine (`create_async_engine`) and `asyncpg` driver.
- **Session management:** `async_sessionmaker` with `AsyncSession`. Sessions injected via FastAPI dependency.
- **Models:** Declarative base, one file per domain entity. All models inherit from a shared `Base` class with common columns (`id` as UUID, `created_at`, `updated_at`).
- **Alembic:** Configured with async support. `env.py` imports all models to ensure autogenerate detects schema changes. Migration files stored in `backend/migrations/versions/`.

**Initial migration covers Phase 1 models:** Board, List, Card.

### 3.4 Configuration: Pydantic Settings

All configuration loaded via `pydantic-settings` from environment variables with sensible defaults for local development:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/trello_clone
CORS_ORIGINS=http://localhost:3000
ENV=development
LOG_LEVEL=info
```

### 3.5 Testing: pytest

- **pytest-asyncio** for testing async FastAPI endpoints.
- **httpx** `AsyncClient` as the test HTTP client (replaces `TestClient` for async support).
- **Test database:** A separate `trello_clone_test` Postgres database, created/dropped per test session. Migrations run before each session.
- **Fixtures in `conftest.py`:** `db_session` (scoped per test, rolled back after each), `client` (async HTTP client pointed at the test app).
- **Naming convention:** `test_<domain>_<action>.py` → e.g., `test_boards_create.py` or grouped as `test_boards.py`.

### 3.6 Linting & Formatting: Ruff

Configured in `backend/pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM", "TCH"]
ignore = []

[tool.ruff.format]
quote-style = "double"
```

### 3.7 Type Checking: mypy

Configured in `backend/pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]
```

---

## 4. Frontend Stack

### 4.1 Runtime & Package Management

| Tool | Version | Purpose |
|---|---|---|
| Node.js | 20 LTS | Runtime |
| pnpm | Latest | Package management |
| TypeScript | 5.x | Language |

### 4.2 Framework: TanStack Start

- **TanStack Start** as the full-stack React framework (file-based routing, SSR-ready).
- **Routing:** File-based routes under `app/routes/`. Key routes from Phase 1–3: `/` (home), `/board/$boardId` (board view), `/board/$boardId/card/$cardId` (card detail — handled as modal over board route).
- **Data fetching:** TanStack Router loaders for initial data, TanStack Query for mutations and cache management.

**Initialization:**

```bash
cd frontend
pnpm create @tanstack/start
pnpm add @tanstack/react-query
```

### 4.3 UI: shadcn/ui + Theme

- **shadcn/ui** installed via CLI, components committed to `app/components/ui/`.
- **Custom theme** applied from the provided tweakcn URL:

```bash
pnpm dlx shadcn@latest add https://tweakcn.com/r/themes/cmdght103000n04lh3e2ae93r
```

- Components are added on demand as needed per phase (e.g., `dialog`, `dropdown-menu`, `popover`, `calendar`, `checkbox` will be pulled in as features require them).

### 4.4 Testing: Vitest

- **Vitest** as the unit test runner (fast, native ESM, compatible with TanStack Start's Vite setup).
- **Testing Library** (`@testing-library/react`) for component tests.
- **Test location:** `frontend/tests/unit/` mirroring the component/hook structure.
- **Coverage:** Configured but not gated in CI initially. Target: 60% coverage before Phase 3 ships.

```bash
pnpm add -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

### 4.5 Linting & Formatting: Biome

Configured in `frontend/biome.json`:

```json
{
  "$schema": "https://biomejs.dev/schemas/2.0.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": { "recommended": true }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  }
}
```

### 4.6 Type Checking

- `tsc --noEmit` runs as part of the pre-commit hook and CI pipeline.
- `tsconfig.json` uses `"strict": true`.

---

## 5. End-to-End Tests: Playwright

- **Separate `e2e/` package** at the monorepo root.
- **Playwright** tests run against the full local stack (frontend + backend + Postgres via Docker Compose).
- **Config:** Headless Chromium by default. CI runs against Chromium only; developers can run all browsers locally.
- **Test structure:** One spec file per major user flow, aligned to PRD user stories (e.g., `board-crud.spec.ts`, `card-drag-drop.spec.ts`, `labels-and-dates.spec.ts`).
- **Setup:** Playwright's `globalSetup` starts Docker Compose, seeds the test database, and waits for both servers to be healthy.

```bash
cd e2e
pnpm add -D @playwright/test
npx playwright install chromium
```

**`playwright.config.ts` key settings:**

```
webServer: [
  { command: 'cd ../backend && uv run uvicorn app.main:app --port 8000', port: 8000 },
  { command: 'cd ../frontend && pnpm dev --port 3000', port: 3000 },
]
```

---

## 6. Docker Compose (Local Development)

`docker-compose.yml` at the monorepo root provides infrastructure services only. The application servers (FastAPI, TanStack Start) run natively on the host for fast iteration with hot reload.

```yaml
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: trello_clone
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  postgres-test:
    image: postgres:16-alpine
    ports:
      - "5433:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: trello_clone_test

volumes:
  pgdata:
```

**Key decisions:**
- **Two Postgres containers** — one for dev (`5432`), one for tests (`5433`). Tests can destroy and recreate their database without affecting the dev environment.
- **No containerized app servers** — running FastAPI and TanStack Start inside Docker slows down hot reload and complicates debugging. Docker is only for stateful services.
- **Redis** will be added in Phase 4 when WebSocket pub/sub is needed.

---

## 7. Environment Variable Management

### 7.1 `.env.example` (committed to repo)

```env
# ─── Database ───
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/trello_clone
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/trello_clone_test

# ─── Backend ───
ENV=development
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000
SECRET_KEY=change-me-in-production

# ─── Frontend ───
VITE_API_BASE_URL=http://localhost:8000

# ─── Auth (Phase 4 — leave blank until needed) ───
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# ─── File Storage (Phase 2 — leave blank until needed) ───
S3_BUCKET=
S3_REGION=
S3_ACCESS_KEY=
S3_SECRET_KEY=

# ─── Email (Phase 5 — leave blank until needed) ───
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=
```

### 7.2 Rules

- `.env` is in `.gitignore` — never committed.
- `.env.example` is committed and kept up to date. Every env var used anywhere in the codebase must have an entry here.
- Backend loads env vars via `pydantic-settings` with validation at startup — the app crashes immediately with a clear message if a required var is missing.
- Frontend env vars are prefixed with `VITE_` and accessed via `import.meta.env`.

---

## 8. Pre-Commit Hooks

Managed via the `pre-commit` framework. Configured in `.pre-commit-config.yaml` at the monorepo root.

### 8.1 Hook Configuration

```yaml
repos:
  # ─── General ───
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: no-commit-to-branch
        args: ['--branch', 'main']

  # ─── Backend (Python) ───
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format (backend)
        entry: bash -c 'cd backend && uv run ruff format --check .'
        language: system
        files: ^backend/.*\.py$
        pass_filenames: false

      - id: ruff-lint
        name: ruff lint (backend)
        entry: bash -c 'cd backend && uv run ruff check .'
        language: system
        files: ^backend/.*\.py$
        pass_filenames: false

      - id: mypy-backend
        name: mypy (backend)
        entry: bash -c 'cd backend && uv run mypy app/'
        language: system
        files: ^backend/.*\.py$
        pass_filenames: false

  # ─── Frontend (TypeScript) ───
  - repo: local
    hooks:
      - id: biome-check
        name: biome check (frontend)
        entry: bash -c 'cd frontend && pnpm biome check --no-errors-on-unmatched .'
        language: system
        files: ^frontend/.*\.(ts|tsx|js|jsx)$
        pass_filenames: false

      - id: tsc-frontend
        name: tsc --noEmit (frontend)
        entry: bash -c 'cd frontend && pnpm tsc --noEmit'
        language: system
        files: ^frontend/.*\.(ts|tsx)$
        pass_filenames: false
```

### 8.2 Setup

Developers install hooks after cloning:

```bash
pip install pre-commit
pre-commit install
```

This is documented in the README as part of the "Getting Started" instructions.

---

## 9. CI/CD Pipeline (GitHub Actions)

All CI/CD jobs run on a **self-hosted external action runner** at `2.56.122.47`, accessed via SSH as the `deploy` user. GitHub Actions workflows use `runs-on: self-hosted` and the runner agent is pre-installed on the server.

### 9.1 Runner Setup (One-Time)

The external server must be configured as a self-hosted GitHub Actions runner:

1. SSH into the runner: `ssh deploy@2.56.122.47`
2. Install the GitHub Actions runner agent following GitHub's documentation (Settings → Actions → Runners → Add runner).
3. Install runner prerequisites: Python 3.12, uv, Node.js 20, pnpm, Docker, Playwright system dependencies.
4. Register the runner with labels: `self-hosted`, `linux`, `trello-clone`.
5. Configure the runner as a systemd service so it survives reboots.

### 9.2 Main CI (`ci.yml`)

Triggered on every push and pull request to `main`.

**Jobs:**

| Job | Steps | Runs on |
|---|---|---|
| **backend-lint** | Ruff format check → Ruff lint → mypy | `self-hosted` |
| **backend-test** | Start Postgres (Docker) → Run Alembic migrations → pytest with coverage | `self-hosted` |
| **frontend-lint** | Biome check → tsc --noEmit | `self-hosted` |
| **frontend-test** | Vitest with coverage | `self-hosted` |

All four jobs run in parallel. PR merge is blocked if any job fails.

**Database for CI tests:** The runner starts a Postgres Docker container (`postgres:16-alpine`) at the beginning of the test job and tears it down after. This keeps test isolation clean without needing a persistent database on the runner.

### 9.3 E2E Pipeline (`e2e.yml`)

Triggered after `ci.yml` succeeds (using `workflow_run` trigger), or manually via `workflow_dispatch`.

**Steps (all on `self-hosted`):**

1. Start Postgres via Docker on the runner.
2. Install backend dependencies, run migrations, start FastAPI server.
3. Install frontend dependencies, build, start preview server.
4. Run Playwright tests (Chromium, headless).
5. Upload Playwright HTML report as artifact (available for 14 days).

E2E is intentionally separated from the main CI to keep PR feedback fast. The main CI pipeline should complete in under 3 minutes. E2E runs as a follow-up and is expected to take 5–10 minutes.

### 9.4 Runner Security Considerations

- The `deploy` user on `2.56.122.47` should have limited permissions — no root access, only what's needed to run builds and Docker.
- GitHub Actions secrets (database credentials, API keys) are stored in GitHub's encrypted secrets, never on the runner filesystem.
- The runner workspace is cleaned between jobs (`clean: true` on checkout) to prevent state leakage between PRs.
- SSH access to the runner is key-based only (no password auth). Key rotation recommended every 90 days.

### 9.5 Branch Protection Rules

| Rule | Setting |
|---|---|
| Required status checks | `backend-lint`, `backend-test`, `frontend-lint`, `frontend-test` |
| Require PR before merge to `main` | Yes |
| Require at least 1 approval | Yes (can be relaxed for solo phase) |
| Require branch up to date | Yes |
| E2E required for merge? | No (advisory only, to avoid blocking PRs on slow E2E runs) |

---

## 10. Makefile (Developer Convenience)

Root-level `Makefile` providing unified commands:

```makefile
# ─── Local Infrastructure ───
up:                  # Start Postgres containers
	docker compose up -d

down:                # Stop and remove containers
	docker compose down

reset-db:            # Drop and recreate dev database, re-run migrations
	docker compose down -v
	docker compose up -d
	sleep 2
	cd backend && uv run alembic upgrade head

# ─── Backend ───
be-install:          # Install backend dependencies
	cd backend && uv sync

be-dev:              # Run backend dev server with hot reload
	cd backend && uv run uvicorn app.main:app --reload --port 8000

be-lint:             # Run ruff lint + format check + mypy
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app/

be-test:             # Run backend unit tests
	cd backend && uv run pytest -v

be-migrate:          # Run pending Alembic migrations
	cd backend && uv run alembic upgrade head

be-migration:        # Generate a new migration (usage: make be-migration msg="add labels table")
	cd backend && uv run alembic revision --autogenerate -m "$(msg)"

# ─── Frontend ───
fe-install:          # Install frontend dependencies
	cd frontend && pnpm install

fe-dev:              # Run frontend dev server
	cd frontend && pnpm dev --port 3000

fe-lint:             # Run biome check + tsc
	cd frontend && pnpm biome check . && pnpm tsc --noEmit

fe-test:             # Run frontend unit tests
	cd frontend && pnpm vitest run

# ─── Full Stack ───
install:             # Install all dependencies
	make be-install && make fe-install

dev:                 # Start everything (requires Docker running)
	make up
	make be-dev & make fe-dev

lint:                # Lint both stacks
	make be-lint && make fe-lint

test:                # Run all unit tests
	make be-test && make fe-test

# ─── E2E ───
e2e:                 # Run Playwright E2E tests
	cd e2e && pnpm playwright test

e2e-ui:              # Run Playwright with UI mode
	cd e2e && pnpm playwright test --ui
```

---

## 11. Getting Started (README Template)

The README should walk a new developer through setup in this order:

1. **Prerequisites:** Python 3.12, uv, Node.js 20, pnpm, Docker.
2. **Clone & install:** `git clone ... && make install`
3. **Environment:** `cp .env.example .env` (defaults work for local dev).
4. **Start infrastructure:** `make up`
5. **Run migrations:** `make be-migrate`
6. **Start dev servers:** `make dev` (opens backend on `:8000`, frontend on `:3000`).
7. **Install pre-commit hooks:** `pre-commit install`
8. **Run tests:** `make test`
9. **Run E2E:** `make e2e`

Target: zero-to-running in under 5 minutes on a machine with prerequisites installed.

---

## 12. Decisions Deferred to Future Phases

| Decision | Deferred To | Rationale |
|---|---|---|
| Redis for WebSocket pub/sub | Phase 4 | Not needed until real-time collaboration. Add to Docker Compose at that point. |
| S3-compatible object storage | Phase 2 | Not needed until file attachments. Use MinIO in Docker Compose for local dev. |
| Email service (SMTP / transactional provider) | Phase 5 | Not needed until notifications. Use Mailpit in Docker Compose for local dev. |
| Production deployment (Docker images, hosting) | Post-Phase 5 | Focus on development velocity first. |
| API documentation (OpenAPI) | Phase 1 | FastAPI auto-generates OpenAPI spec at `/docs`. No additional tooling needed initially. |
