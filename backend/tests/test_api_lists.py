"""Tests for the List API endpoints.

Verifies CRUD + reorder operations on lists:
- POST /api/lists creates a list with correct auto-assigned position
- PUT /api/lists/{id} updates a list's title
- PUT /api/lists/{id} returns 404 for non-existent list
- DELETE /api/lists/{id} removes list and its cards (CASCADE)
- DELETE /api/lists/{id} returns 404 for non-existent list
- PUT /api/lists/reorder updates list positions correctly

These tests correspond to the feedback loop plan in docs/feedback-loops/TRE-37-feedback.md.
Uses shared ``db`` and ``client`` fixtures from conftest.py.
"""

import httpx

from app.database import Database
from app.models import Card, List


class TestCreateList:
    """Tests for POST /api/lists — create a new list."""

    async def test_create_list_with_correct_position(
        self, client: httpx.AsyncClient, db: Database
    ) -> None:
        """POST /api/lists creates a list with auto-assigned position.

        First list gets position 0, second list gets position 1.
        Response includes id, title, board_id, and position fields.
        """
        boards = await db.list_boards()
        board_id = boards[0].id

        # Create first list — should get position 0
        response = await client.post(
            "/api/lists",
            json={"title": "Todo", "board_id": board_id},
        )
        assert response.status_code == 201, (
            f"POST /api/lists should return 201 Created, got {response.status_code}"
        )
        data = response.json()
        assert data["title"] == "Todo", f"Expected title 'Todo', got {data.get('title')!r}"
        assert data["board_id"] == board_id, (
            f"Expected board_id '{board_id}', got {data.get('board_id')!r}"
        )
        assert data["position"] == 0, (
            f"First list should have position 0, got {data.get('position')!r}"
        )
        assert "id" in data, "Response should include 'id' field"

        # Create second list — should get position 1
        response2 = await client.post(
            "/api/lists",
            json={"title": "Doing", "board_id": board_id},
        )
        assert response2.status_code == 201, (
            f"Second POST /api/lists should return 201 Created, got {response2.status_code}"
        )
        data2 = response2.json()
        assert data2["position"] == 1, (
            f"Second list should have position 1, got {data2.get('position')!r}"
        )


class TestUpdateList:
    """Tests for PUT /api/lists/{id} — update list title."""

    async def test_update_list_title(self, client: httpx.AsyncClient, db: Database) -> None:
        """PUT /api/lists/{id} updates the list title and returns the updated list.

        The list ID and board_id remain unchanged after the update.
        """
        boards = await db.list_boards()
        board_id = boards[0].id
        lst = await db.create_list(List(title="Original", board_id=board_id, position=0))

        response = await client.put(
            f"/api/lists/{lst.id}",
            json={"title": "Updated"},
        )
        assert response.status_code == 200, (
            f"PUT /api/lists/{{id}} should return 200, got {response.status_code}"
        )
        data = response.json()
        assert data["title"] == "Updated", (
            f"Expected updated title 'Updated', got {data.get('title')!r}"
        )
        assert data["id"] == lst.id, (
            f"List ID should remain unchanged: expected {lst.id!r}, got {data.get('id')!r}"
        )
        assert data["board_id"] == board_id, (
            f"board_id should remain unchanged: expected {board_id!r}, got {data.get('board_id')!r}"
        )

    async def test_update_list_returns_404_for_nonexistent(self, client: httpx.AsyncClient) -> None:
        """PUT /api/lists/{id} returns 404 with a JSON detail message for a non-existent list."""
        response = await client.put(
            "/api/lists/nonexistent-uuid",
            json={"title": "X"},
        )
        assert response.status_code == 404, (
            f"PUT /api/lists/nonexistent-uuid should return 404, got {response.status_code}"
        )
        data = response.json()
        assert "detail" in data, (
            "404 response should include a 'detail' field with an error message"
        )
        assert data["detail"] == "List not found", (
            f"Expected detail 'List not found', got {data['detail']!r}"
        )


class TestDeleteList:
    """Tests for DELETE /api/lists/{id} — delete list and CASCADE to cards."""

    async def test_delete_list_removes_list_and_cards(
        self, client: httpx.AsyncClient, db: Database
    ) -> None:
        """DELETE /api/lists/{id} returns 204, removes the list and its cards via CASCADE.

        After deletion, both db.get_list(list_id) and db.get_card(card_id)
        return None.
        """
        boards = await db.list_boards()
        board_id = boards[0].id
        lst = await db.create_list(List(title="To Delete", board_id=board_id, position=0))
        card = await db.create_card(Card(title="Card on deleted list", list_id=lst.id, position=0))

        response = await client.delete(f"/api/lists/{lst.id}")
        assert response.status_code == 204, (
            f"DELETE /api/lists/{{id}} should return 204 No Content, got {response.status_code}"
        )

        # Verify list is gone
        deleted_list = await db.get_list(lst.id)
        assert deleted_list is None, (
            f"List should be deleted from database, but get_list returned {deleted_list!r}"
        )

        # Verify card is gone (CASCADE delete)
        deleted_card = await db.get_card(card.id)
        assert deleted_card is None, (
            f"Card should be CASCADE-deleted, but get_card returned {deleted_card!r}"
        )

    async def test_delete_list_returns_404_for_nonexistent(self, client: httpx.AsyncClient) -> None:
        """DELETE /api/lists/{id} returns 404 for a non-existent list."""
        response = await client.delete("/api/lists/nonexistent-uuid")
        assert response.status_code == 404, (
            f"DELETE /api/lists/nonexistent-uuid should return 404, got {response.status_code}"
        )
        data = response.json()
        assert data["detail"] == "List not found", (
            f"Expected detail 'List not found', got {data.get('detail')!r}"
        )


class TestReorderLists:
    """Tests for PUT /api/lists/reorder — reorder lists on a board."""

    async def test_reorder_lists_updates_positions(
        self, client: httpx.AsyncClient, db: Database
    ) -> None:
        """PUT /api/lists/reorder updates positions to match submitted list_ids order.

        Creates 3 lists (positions 0, 1, 2), reorders them, and verifies
        the new positions are persisted correctly.
        """
        boards = await db.list_boards()
        board_id = boards[0].id

        lst_0 = await db.create_list(List(title="List A", board_id=board_id, position=0))
        lst_1 = await db.create_list(List(title="List B", board_id=board_id, position=1))
        lst_2 = await db.create_list(List(title="List C", board_id=board_id, position=2))

        # Reorder: C, A, B
        response = await client.put(
            "/api/lists/reorder",
            json={"list_ids": [lst_2.id, lst_0.id, lst_1.id]},
        )
        assert response.status_code == 200, (
            f"PUT /api/lists/reorder should return 200, got {response.status_code}"
        )

        # Verify positions are persisted correctly via database
        reordered = await db.get_lists_by_board(board_id)
        reordered_ids = [lst.id for lst in reordered]
        expected_order = [lst_2.id, lst_0.id, lst_1.id]
        assert reordered_ids == expected_order, (
            f"Lists should be reordered to {expected_order}, but got {reordered_ids}"
        )

        # Verify positions are sequential 0, 1, 2
        positions = [lst.position for lst in reordered]
        assert positions == [0, 1, 2], (
            f"Positions should be [0, 1, 2] after reorder, got {positions}"
        )
