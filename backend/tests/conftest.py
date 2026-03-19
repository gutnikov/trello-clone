"""Shared pytest fixtures for all API test modules.

Provides:
- ``db``: An in-memory Database instance with schema initialized and default
  board seeded.  Function-scoped for test isolation.
- ``client``: An httpx AsyncClient wired to the FastAPI test app with the
  test database injected into ``app.state.db``.
"""

from collections.abc import AsyncIterator

import httpx
import pytest
from httpx import ASGITransport

from app.database import Database
from app.main import app


@pytest.fixture
async def db() -> AsyncIterator[Database]:
    """Create an in-memory Database with schema and default board seeded.

    Yields a connected, schema-initialized, seeded Database instance.
    Each test function gets a fresh, isolated database.
    """
    database = Database(":memory:")
    await database.connect()
    await database.init_schema()
    await database.seed_default_board()
    yield database
    await database.close()


@pytest.fixture(autouse=True)
async def _wire_app_db(db: Database) -> AsyncIterator[None]:
    """Wire the test database into the FastAPI app state.

    This autouse fixture ensures ``app.state.db`` is set to the test database
    for every test function, enabling route handlers and lifespan-dependent
    tests to access the database instance.
    """
    app.state.db = db
    yield
    # Clean up app state to avoid leaking between test modules
    if hasattr(app.state, "db"):
        del app.state.db


@pytest.fixture
async def client(db: Database) -> AsyncIterator[httpx.AsyncClient]:
    """Create an httpx AsyncClient wired to the FastAPI test app.

    Sets ``app.state.db`` to the test database before creating the client,
    so route handlers can access the in-memory test database.
    """
    app.state.db = db
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
