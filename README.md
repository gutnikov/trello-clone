# trello-clone

A Trello-style kanban board application.

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | Astro, React, TypeScript          |
| Backend  | FastAPI, Python 3.12+             |
| Database | SQLite (via aiosqlite)            |
| Logging  | structlog (JSON to stdout)        |

## Getting Started

```bash
make install    # Install all dependencies (backend + frontend)
make dev        # Start backend (port 8000) and frontend (port 3000)
make test       # Run all tests
make lint       # Run all linters
```