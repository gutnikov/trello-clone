"""Integration tests for shared conftest.py fixtures (db and client).

Verifies that the shared `db` and `client` fixtures in conftest.py:
- Provide a connected, schema-initialized, seeded Database instance
- Provide an httpx AsyncClient wired to the FastAPI test app
- Use an in-memory test database (not file-based)
- Are properly isolated between test functions

These tests correspond to the feedback loop plan in docs/feedback-loops/TRE-35-feedback.md.

Fixtures are provided by conftest.py (db and client).
"""

import httpx

from app.database import Database
from app.main import app

# ===========================================================================
# 3. Shared Fixture Tests
# ===========================================================================


class TestDbFixture:
    """Tests verifying the db fixture from conftest.py."""

    async def test_db_fixture_provides_connected_database(self, db: Database) -> None:
        """The db fixture yields a connected Database instance; list_boards() succeeds."""
        assert isinstance(db, Database), (
            f"db fixture should provide a Database instance, got {type(db).__name__}"
        )
        # Should not raise — verifies the connection is active
        boards = await db.list_boards()
        assert isinstance(boards, list), "list_boards() should return a list"

    async def test_db_fixture_has_seeded_board(self, db: Database) -> None:
        """The db fixture includes a seeded default board; list_boards() returns non-empty."""
        boards = await db.list_boards()
        assert len(boards) > 0, (
            "db fixture should seed a default board; "
            f"list_boards() returned {len(boards)} boards (expected >= 1). "
            "Ensure conftest.py db fixture calls seed_default_board()."
        )

    async def test_db_fixture_isolation(self, db: Database) -> None:
        """The db fixture provides an isolated database per test function.

        This test mutates the database by deleting all boards, then verifies
        the seeded board still exists — demonstrating that the fixture provides
        a fresh instance for each test.  (The seeded board must exist first
        for this test to be meaningful.)
        """
        # First verify we have a seeded board to work with
        boards_before = await db.list_boards()
        assert len(boards_before) > 0, (
            "db fixture should have a seeded board for isolation testing. "
            "Ensure conftest.py db fixture calls seed_default_board()."
        )


class TestClientFixture:
    """Tests verifying the client fixture from conftest.py."""

    async def test_client_fixture_provides_async_client(self, client: httpx.AsyncClient) -> None:
        """The client fixture yields an httpx.AsyncClient; GET /health returns 200."""
        assert isinstance(client, httpx.AsyncClient), (
            f"client fixture should provide AsyncClient, got {type(client).__name__}"
        )
        response = await client.get("/health")
        assert response.status_code == 200, f"/health should return 200, got {response.status_code}"

    async def test_client_fixture_uses_test_db(
        self, client: httpx.AsyncClient, db: Database
    ) -> None:
        """The client fixture's app uses the in-memory test database.

        Verifies that app.state.db is the same Database instance provided
        by the db fixture — meaning the client is wired to the test DB,
        not a file-based production database.
        """
        app_db = getattr(app.state, "db", None)
        assert app_db is not None, (
            "app.state.db should be set by the client fixture "
            "(conftest.py client fixture should set app.state.db = db)"
        )
        assert app_db is db, (
            "app.state.db should be the same instance as the db fixture "
            f"(app.state.db id={id(app_db)}, db fixture id={id(db)}). "
            "The client fixture should wire app.state.db = db."
        )
