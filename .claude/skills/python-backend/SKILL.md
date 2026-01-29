---
name: python-backend
description: Python backend API development best practices. Use when writing Python backend code, FastAPI endpoints, SQLAlchemy models, Pydantic schemas, async patterns, or configuring Python tooling (ruff, mypy, uv, Docker).
---

# Python Backend API Development

Apply modern Python backend best practices when writing or reviewing code.

## Key Standards

- **Framework**: FastAPI with async endpoints, Pydantic v2 models, and `Annotated` dependencies
- **Type Safety**: Full type hints everywhere, strict mypy, Pydantic for validation
- **Database**: SQLAlchemy 2.0 async with `Mapped`/`mapped_column`, Alembic migrations
- **Auth**: JWT with RS256, short-lived access tokens, refresh token rotation
- **Async**: Use `async def` for I/O-bound routes, `asyncio.gather()` for concurrent ops, never block the event loop
- **Testing**: pytest + pytest-asyncio, factory fixtures, dependency overrides
- **Logging**: structlog with JSON in production, OpenTelemetry trace correlation
- **Code Quality**: Ruff for linting/formatting, Mypy strict mode, pre-commit hooks
- **Package Manager**: uv (preferred) or Poetry
- **Docker**: Multi-stage builds, slim images, non-root user, health checks

## When writing code, follow these principles

1. Use `Annotated` type aliases for reusable dependency declarations
2. Separate Pydantic schemas: Create, Update, Response (never expose ORM models directly)
3. Keep routes thin -- business logic goes in service functions
4. Handle errors with custom exception classes and global exception handlers
5. Use `yield` dependencies for resources needing cleanup (DB sessions)
6. Never run blocking code in async routes -- use `asyncio.to_thread()` if needed
7. Configure structured logging with request correlation IDs

## Detailed reference

For complete patterns, code examples, and configurations, see [reference.md](reference.md).
