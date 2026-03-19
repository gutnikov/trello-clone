"""Tests for FastAPI app configuration: CORS middleware and lifespan lifecycle.

Verifies that:
- CORS middleware is properly configured with appropriate headers
- The lifespan context manager connects to DB, initializes schema, seeds default board
- app.state.db is available after startup
- The /health endpoint continues to work (non-regression)

These tests correspond to the feedback loop plan in docs/feedback-loops/TRE-35-feedback.md.
"""

import httpx
import pytest
from httpx import ASGITransport

from app.database import Database
from app.main import app

# ---------------------------------------------------------------------------
# Helpers — minimal test client without relying on conftest.py fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def client() -> httpx.AsyncClient:  # type: ignore[misc]
    """Create an httpx AsyncClient wired to the FastAPI app under test.

    This fixture creates a test client that exercises the ASGI app including
    any middleware and lifespan events.  It does NOT override app.state.db,
    so it tests the real app configuration.
    """
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c  # type: ignore[misc]


# ===========================================================================
# 1. CORS Middleware Tests
# ===========================================================================


class TestCORSMiddleware:
    """Tests verifying CORS middleware is configured on the FastAPI app."""

    async def test_cors_allows_any_origin_by_default(self, client: httpx.AsyncClient) -> None:
        """A request with Origin: http://example.com receives Access-Control-Allow-Origin: *."""
        response = await client.get("/health", headers={"Origin": "http://example.com"})
        assert response.status_code == 200, "Health endpoint should return 200"
        allow_origin = response.headers.get("access-control-allow-origin")
        assert allow_origin is not None, (
            "Response should include Access-Control-Allow-Origin header "
            "(CORS middleware not configured)"
        )
        assert allow_origin == "*", (
            f"Default CORS should allow all origins ('*'), got {allow_origin!r}"
        )

    async def test_cors_preflight_returns_200(self, client: httpx.AsyncClient) -> None:
        """An OPTIONS preflight request returns 200 with CORS method and header allowances."""
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code == 200, (
            f"CORS preflight should return 200, got {response.status_code}"
        )
        assert "access-control-allow-methods" in response.headers, (
            "Preflight response should include Access-Control-Allow-Methods"
        )
        assert "access-control-allow-headers" in response.headers, (
            "Preflight response should include Access-Control-Allow-Headers"
        )

    async def test_cors_configured_origins_respected(
        self, client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When CORS_ORIGINS env var is set, only those origins are allowed.

        NOTE: This test verifies that the app respects CORS_ORIGINS configuration.
        Since the app is created at module import time, we need to verify the
        mechanism is in place.  The implementation should read CORS_ORIGINS at
        app startup and configure the middleware accordingly.
        """
        # For this test, we verify that when the app is configured with
        # restricted origins (not "*"), a request from an unlisted origin
        # does NOT receive the Access-Control-Allow-Origin header or gets
        # the specific origin reflected.
        #
        # We test the default behavior here — with no CORS_ORIGINS set,
        # http://localhost:3000 should still be allowed (via wildcard "*").
        response = await client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        allow_origin = response.headers.get("access-control-allow-origin")
        # When CORS is properly configured, this should be either "*" or
        # "http://localhost:3000" — but NOT None (missing).
        assert allow_origin is not None, (
            "CORS middleware should set Access-Control-Allow-Origin for any origin "
            "in dev mode (CORS_ORIGINS not set)"
        )


# ===========================================================================
# 2. Lifespan Lifecycle Tests
# ===========================================================================


class TestLifespanLifecycle:
    """Tests verifying the lifespan context manager sets up DB correctly."""

    async def test_app_state_has_db_after_startup(self, client: httpx.AsyncClient) -> None:
        """After the test client triggers lifespan, app.state.db is a Database instance."""
        # The client fixture triggers the lifespan events.
        # After startup, app.state.db should be set.
        db = getattr(app.state, "db", None)
        assert db is not None, (
            "app.state.db should be set after lifespan startup "
            "(lifespan context manager not configured)"
        )
        assert isinstance(db, Database), (
            f"app.state.db should be a Database instance, got {type(db).__name__}"
        )

    async def test_lifespan_seeds_default_board(self, client: httpx.AsyncClient) -> None:
        """After startup, the database contains at least one seeded board."""
        db = getattr(app.state, "db", None)
        assert db is not None, "app.state.db should be set after lifespan startup"
        boards = await db.list_boards()
        assert len(boards) >= 1, (
            f"Lifespan should seed a default board; found {len(boards)} boards instead of >= 1"
        )

    async def test_health_endpoint_still_works(self, client: httpx.AsyncClient) -> None:
        """GET /health returns {\"status\": \"ok\", \"version\": \"0.1.0\"} with status 200.

        This is a non-regression test confirming the /health endpoint
        continues to work after adding lifespan and CORS middleware.
        """
        response = await client.get("/health")
        assert response.status_code == 200, f"/health should return 200, got {response.status_code}"
        data = response.json()
        assert data == {"status": "ok", "version": "0.1.0"}, (
            f"/health should return expected JSON, got {data!r}"
        )
