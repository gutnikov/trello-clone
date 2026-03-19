"""Integration tests for the board API endpoints (GET /api/board, PUT /api/board).

Tests verify the nested board response structure, list/card ordering,
board title updates, input validation, and router registration at the /api prefix.
"""

from __future__ import annotations

import httpx

from app.database import Database
from app.models import Card, List


class TestGetBoard:
    """Tests for GET /api/board — nested board retrieval."""

    async def test_get_board_returns_200_with_nested_structure(
        self, client: httpx.AsyncClient, db: Database
    ) -> None:
        """GET /api/board returns 200 with id, title, and lists keys."""
        response = await client.get("/api/board")

        assert response.status_code == 200, (
            f"Expected 200 for GET /api/board, got {response.status_code}"
        )
        data = response.json()
        assert "id" in data, "Response missing 'id' key"
        assert "title" in data, "Response missing 'title' key"
        assert "lists" in data, "Response missing 'lists' key"
        assert isinstance(data["id"], str), "Board 'id' should be a string"
        assert isinstance(data["title"], str), "Board 'title' should be a string"
        assert isinstance(data["lists"], list), "Board 'lists' should be a list"
        assert data["title"] == "My Board", (
            f"Expected seeded board title 'My Board', got '{data['title']}'"
        )

    async def test_get_board_includes_lists_and_cards_in_order(
        self, client: httpx.AsyncClient, db: Database
    ) -> None:
        """GET /api/board returns lists and cards sorted by position."""
        # Seed two lists with intentionally reversed positions
        boards = await db.list_boards()
        board_id = boards[0].id

        await db.create_list(List(title="List B", board_id=board_id, position=1))
        list_a = await db.create_list(List(title="List A", board_id=board_id, position=0))

        # Seed three cards on list_a with non-sequential positions
        await db.create_card(Card(title="Card 3", list_id=list_a.id, position=2))
        await db.create_card(Card(title="Card 1", list_id=list_a.id, position=0))
        await db.create_card(Card(title="Card 2", list_id=list_a.id, position=1))

        response = await client.get("/api/board")
        assert response.status_code == 200, (
            f"Expected 200 for GET /api/board, got {response.status_code}"
        )

        data = response.json()
        lists = data["lists"]
        assert len(lists) >= 2, f"Expected at least 2 lists, got {len(lists)}"

        # Verify lists are ordered by position (ascending)
        for i in range(len(lists) - 1):
            assert lists[i]["position"] < lists[i + 1]["position"], (
                f"Lists not ordered by position: list at index {i} has position "
                f"{lists[i]['position']} >= position {lists[i + 1]['position']} at index {i + 1}"
            )

        # Find list_a in the response and verify its cards are ordered by position
        list_a_data = next((lst for lst in lists if lst["id"] == list_a.id), None)
        assert list_a_data is not None, f"List A (id={list_a.id}) not found in response"
        cards = list_a_data["cards"]
        assert len(cards) == 3, f"Expected 3 cards in List A, got {len(cards)}"
        for i in range(len(cards) - 1):
            assert cards[i]["position"] < cards[i + 1]["position"], (
                f"Cards not ordered by position: card at index {i} has position "
                f"{cards[i]['position']} >= position {cards[i + 1]['position']} at index {i + 1}"
            )

    async def test_get_board_empty_lists_returns_empty_cards(
        self, client: httpx.AsyncClient, db: Database
    ) -> None:
        """When a list has no cards, its 'cards' field is an empty list, not null or absent."""
        boards = await db.list_boards()
        board_id = boards[0].id

        await db.create_list(List(title="Empty List", board_id=board_id, position=0))

        response = await client.get("/api/board")
        assert response.status_code == 200, (
            f"Expected 200 for GET /api/board, got {response.status_code}"
        )

        data = response.json()
        lists = data["lists"]
        assert len(lists) >= 1, "Expected at least 1 list in the response"

        # Find the empty list and verify its cards array
        for lst in lists:
            assert "cards" in lst, f"List '{lst.get('title', 'unknown')}' is missing 'cards' key"
            assert isinstance(lst["cards"], list), (
                f"List '{lst.get('title', 'unknown')}' 'cards' should be a list, "
                f"got {type(lst['cards']).__name__}"
            )

        # Specifically check the list we created has an empty cards array
        empty_list = next((lst for lst in lists if lst.get("title") == "Empty List"), None)
        assert empty_list is not None, "Empty List not found in response"
        assert empty_list["cards"] == [], (
            f"Expected empty cards list for 'Empty List', got {empty_list['cards']}"
        )


class TestPutBoard:
    """Tests for PUT /api/board — update board title."""

    async def test_put_board_updates_title(self, client: httpx.AsyncClient, db: Database) -> None:
        """PUT /api/board with valid title returns 200 and persists the update."""
        boards = await db.list_boards()
        board_id = boards[0].id

        response = await client.put(
            "/api/board",
            json={"title": "New Title"},
        )

        assert response.status_code == 200, (
            f"Expected 200 for PUT /api/board, got {response.status_code}"
        )
        data = response.json()
        assert data["id"] == board_id, f"Expected board id '{board_id}', got '{data.get('id')}'"
        assert data["title"] == "New Title", (
            f"Expected title 'New Title', got '{data.get('title')}'"
        )

        # Verify persistence via subsequent GET
        get_response = await client.get("/api/board")
        assert get_response.status_code == 200, (
            f"Expected 200 for GET /api/board after update, got {get_response.status_code}"
        )
        get_data = get_response.json()
        assert get_data["title"] == "New Title", (
            f"GET /api/board did not reflect updated title: got '{get_data.get('title')}'"
        )

    async def test_put_board_empty_title_returns_422(self, client: httpx.AsyncClient) -> None:
        """PUT /api/board with empty title returns 422 due to min_length=1 validation."""
        response = await client.put(
            "/api/board",
            json={"title": ""},
        )

        assert response.status_code == 422, (
            f"Expected 422 for empty title, got {response.status_code}"
        )
        data = response.json()
        assert "detail" in data, "Expected validation error 'detail' in 422 response body"

    async def test_put_board_missing_title_returns_422(self, client: httpx.AsyncClient) -> None:
        """PUT /api/board with missing title field returns 422."""
        response = await client.put(
            "/api/board",
            json={},
        )

        assert response.status_code == 422, (
            f"Expected 422 for missing title, got {response.status_code}"
        )
        data = response.json()
        assert "detail" in data, "Expected validation error 'detail' in 422 response body"


class TestBoardRouterRegistration:
    """Tests for board router registration in main.py."""

    async def test_board_endpoints_registered_at_api_prefix(
        self, client: httpx.AsyncClient
    ) -> None:
        """GET /api/board returns 200 (not 404); GET /board returns 404."""
        # The /api/board endpoint should exist
        api_response = await client.get("/api/board")
        assert api_response.status_code != 404, (
            "GET /api/board returned 404 — board router not registered at /api prefix"
        )
        assert api_response.status_code == 200, (
            f"Expected 200 for GET /api/board, got {api_response.status_code}"
        )

        # The /board endpoint (without prefix) should NOT exist
        bare_response = await client.get("/board")
        assert bare_response.status_code == 404, (
            f"Expected 404 for GET /board (no /api prefix), got {bare_response.status_code}"
        )
