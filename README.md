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

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status": "ok", "version": "0.1.0"}` |

### Board

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/board` | Returns the board with all lists and cards in a nested JSON structure |
| `PUT` | `/api/board` | Updates the board title — accepts `{"title": "..."}`, returns the updated board |

### Lists

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/lists` | Create a new list |
| `PUT` | `/api/lists/reorder` | Reorder lists on a board |
| `PUT` | `/api/lists/{id}` | Update a list's title |
| `DELETE` | `/api/lists/{id}` | Delete a list and its cards |

**POST /api/lists** — Create a new list with auto-assigned position.
- Request: `{ "title": "string", "board_id": "string" }`
- Response: `201` with the created list object (`id`, `title`, `board_id`, `position`)

**PUT /api/lists/{id}** — Update a list's title.
- Request: `{ "title": "string" }`
- Response: `200` with the updated list object, or `404` if not found

**DELETE /api/lists/{id}** — Delete a list and all its cards (CASCADE).
- Response: `204` No Content, or `404` if not found

**PUT /api/lists/reorder** — Reorder lists on a board.
- Request: `{ "list_ids": ["string"] }` (ordered array of list IDs)
- Response: `200` with the reordered list of lists

## Getting Started

```bash
make install    # Install all dependencies (backend + frontend)
make dev        # Start backend (port 8000) and frontend (port 3000)
make test       # Run all tests
make lint       # Run all linters
```
