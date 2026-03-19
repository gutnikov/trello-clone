# trello-clone

A Trello-style kanban board application.

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | Astro, React, TypeScript          |
| Backend  | FastAPI, Python 3.12+             |
| Database | SQLite (via aiosqlite)            |
| Logging  | structlog (JSON to stdout)        |

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Comma-separated list of allowed CORS origins | `*` (all origins, for development) |
| `DB_PATH` | Path to the SQLite database file | `data/trello.db` |

Set `CORS_ORIGINS` to your frontend domain in production (e.g., `https://app.example.com`).

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/cards` | Create a new card |
| `PUT` | `/api/cards/{id}` | Update card title |
| `DELETE` | `/api/cards/{id}` | Delete a card |
| `PUT` | `/api/cards/{id}/move` | Move/reorder a card |

This section will grow as boards and lists routers are added.

## Getting Started

```bash
make install    # Install all dependencies (backend + frontend)
make dev        # Start backend (port 8000) and frontend (port 3000)
make test       # Run all tests
make lint       # Run all linters
```