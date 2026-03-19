"""Tests for Card API endpoints: CRUD operations and move/reorder.

Verifies that:
- POST /api/cards creates a card in the specified list with auto-assigned position
- PUT /api/cards/{id} updates a card's title
- PUT /api/cards/{id} returns 404 for non-existent card
- DELETE /api/cards/{id} removes a card
- DELETE /api/cards/{id} returns 404 for non-existent card
- PUT /api/cards/{id}/move moves a card between lists
- PUT /api/cards/{id}/move reorders cards within the same list

These tests correspond to the feedback loop plan in docs/feedback-loops/TRE-38-feedback.md.
"""

import uuid

import httpx
import pytest

from app.database import Database
from app.models import Board, Card, List


# ===========================================================================
# Helpers
# ===========================================================================


async def _create_board_and_list(db: Database) -> tuple[Board, List]:
    """Create a board and a list for card tests. Returns (board, list)."""
    board = Board(title="Test Board")
    await db.create_board(board)
    lst = List(title="Test List", board_id=board.id, position=0)
    await db.create_list(lst)
    return board, lst


async def _create_two_lists(db: Database) -> tuple[Board, List, List]:
    """Create a board with two lists for move tests. Returns (board, list1, list2)."""
    board = Board(title="Test Board")
    await db.create_board(board)
    lst1 = List(title="To Do", board_id=board.id, position=0)
    lst2 = List(title="Done", board_id=board.id, position=1)
    await db.create_list(lst1)
    await db.create_list(lst2)
    return board, lst1, lst2


# ===========================================================================
# 1. Create Card Tests
# ===========================================================================


class TestCreateCard:
    """Tests for POST /api/cards endpoint."""

    async def test_create_card(self, client: httpx.AsyncClient, db: Database) -> None:
        """POST /api/cards with valid title and list_id returns 201 with created card.

        The response should contain an auto-generated id (UUID string), the submitted
        title, the submitted list_id, and position 0 (first card in list).
        """
        _board, lst = await _create_board_and_list(db)

        response = await client.post(
            "/api/cards",
            json={"title": "Test Card", "list_id": lst.id},
        )

        assert response.status_code == 201, (
            f"POST /api/cards should return 201 Created, got {response.status_code}"
        )
        data = response.json()
        assert "id" in data, "Response should contain card id"
        assert data["title"] == "Test Card", (
            f"Response title should match input, got {data.get('title')!r}"
        )
        assert data["list_id"] == lst.id, (
            f"Response list_id should match input, got {data.get('list_id')!r}"
        )
        assert data["position"] == 0, (
            f"First card in list should get position 0, got {data.get('position')!r}"
        )

    async def test_create_card_auto_position(self, client: httpx.AsyncClient, db: Database) -> None:
        """POST /api/cards twice to the same list; second card gets position 1.

        Auto-position assignment should increment based on existing cards in the list.
        """
        _board, lst = await _create_board_and_list(db)

        # Create first card
        response1 = await client.post(
            "/api/cards",
            json={"title": "First Card", "list_id": lst.id},
        )
        assert response1.status_code == 201, (
            f"First POST /api/cards should return 201, got {response1.status_code}"
        )
        data1 = response1.json()
        assert data1["position"] == 0, (
            f"First card should get position 0, got {data1.get('position')!r}"
        )

        # Create second card
        response2 = await client.post(
            "/api/cards",
            json={"title": "Second Card", "list_id": lst.id},
        )
        assert response2.status_code == 201, (
            f"Second POST /api/cards should return 201, got {response2.status_code}"
        )
        data2 = response2.json()
        assert data2["position"] == 1, (
            f"Second card should get position 1 (auto-incremented), got {data2.get('position')!r}"
        )


# ===========================================================================
# 2. Update Card Tests
# ===========================================================================


class TestUpdateCard:
    """Tests for PUT /api/cards/{id} endpoint."""

    async def test_update_card_title(self, client: httpx.AsyncClient, db: Database) -> None:
        """PUT /api/cards/{id} with new title returns 200 with updated card."""
        _board, lst = await _create_board_and_list(db)
        card = Card(title="Original Title", list_id=lst.id, position=0)
        await db.create_card(card)

        response = await client.put(
            f"/api/cards/{card.id}",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200, (
            f"PUT /api/cards/{{id}} should return 200, got {response.status_code}"
        )
        data = response.json()
        assert data["title"] == "Updated Title", (
            f"Card title should be updated to 'Updated Title', got {data.get('title')!r}"
        )
        assert data["id"] == card.id, "Card id should remain unchanged"

    async def test_update_card_not_found(self, client: httpx.AsyncClient) -> None:
        """PUT /api/cards/{id} with non-existent id returns 404."""
        fake_id = str(uuid.uuid4())
        response = await client.put(
            f"/api/cards/{fake_id}",
            json={"title": "Does Not Matter"},
        )

        assert response.status_code == 404, (
            f"PUT /api/cards/{{id}} for non-existent card should return 404, "
            f"got {response.status_code}"
        )
        data = response.json()
        assert data["detail"] == "Card not found", (
            f"404 response detail should be 'Card not found', got {data.get('detail')!r}"
        )


# ===========================================================================
# 3. Delete Card Tests
# ===========================================================================


class TestDeleteCard:
    """Tests for DELETE /api/cards/{id} endpoint."""

    async def test_delete_card(self, client: httpx.AsyncClient, db: Database) -> None:
        """DELETE /api/cards/{id} removes the card and returns 204 with no body."""
        _board, lst = await _create_board_and_list(db)
        card = Card(title="To Delete", list_id=lst.id, position=0)
        await db.create_card(card)

        response = await client.delete(f"/api/cards/{card.id}")

        assert response.status_code == 204, (
            f"DELETE /api/cards/{{id}} should return 204 No Content, got {response.status_code}"
        )
        assert response.content == b"", "DELETE /api/cards/{id} should return empty body with 204"

        # Verify card is actually gone from the database
        deleted_card = await db.get_card(card.id)
        assert deleted_card is None, "Card should be removed from the database after DELETE"

    async def test_delete_card_not_found(self, client: httpx.AsyncClient) -> None:
        """DELETE /api/cards/{id} with non-existent id returns 404."""
        fake_id = str(uuid.uuid4())
        response = await client.delete(f"/api/cards/{fake_id}")

        assert response.status_code == 404, (
            f"DELETE /api/cards/{{id}} for non-existent card should return 404, "
            f"got {response.status_code}"
        )
        data = response.json()
        assert data["detail"] == "Card not found", (
            f"404 response detail should be 'Card not found', got {data.get('detail')!r}"
        )


# ===========================================================================
# 4. Move Card Tests
# ===========================================================================


class TestMoveCard:
    """Tests for PUT /api/cards/{id}/move endpoint."""

    async def test_move_card_between_lists(self, client: httpx.AsyncClient, db: Database) -> None:
        """PUT /api/cards/{id}/move moves a card from one list to another.

        Create two lists and a card in list 1. Move the card to list 2 at
        position 0. The response should show the card with the new list_id
        and position.
        """
        _board, lst1, lst2 = await _create_two_lists(db)
        card = Card(title="Moving Card", list_id=lst1.id, position=0)
        await db.create_card(card)

        response = await client.put(
            f"/api/cards/{card.id}/move",
            json={"list_id": lst2.id, "position": 0},
        )

        assert response.status_code == 200, (
            f"PUT /api/cards/{{id}}/move should return 200, got {response.status_code}"
        )
        data = response.json()
        assert data["list_id"] == lst2.id, (
            f"Card should be moved to list 2, got list_id={data.get('list_id')!r}"
        )
        assert data["position"] == 0, (
            f"Card should be at position 0 in target list, got {data.get('position')!r}"
        )

    async def test_reorder_card_within_list(self, client: httpx.AsyncClient, db: Database) -> None:
        """PUT /api/cards/{id}/move reorders cards within the same list.

        Create a list with 3 cards at positions 0, 1, 2. Move the card at
        position 2 to position 0. The response should show the moved card at
        position 0, and the other cards should be shifted: former pos 0 -> 1,
        former pos 1 -> 2.
        """
        _board, lst = await _create_board_and_list(db)
        card_a = Card(title="Card A", list_id=lst.id, position=0)
        card_b = Card(title="Card B", list_id=lst.id, position=1)
        card_c = Card(title="Card C", list_id=lst.id, position=2)
        await db.create_card(card_a)
        await db.create_card(card_b)
        await db.create_card(card_c)

        # Move card_c (position 2) to position 0
        response = await client.put(
            f"/api/cards/{card_c.id}/move",
            json={"list_id": lst.id, "position": 0},
        )

        assert response.status_code == 200, (
            f"PUT /api/cards/{{id}}/move should return 200, got {response.status_code}"
        )
        data = response.json()
        assert data["position"] == 0, (
            f"Moved card should be at position 0, got {data.get('position')!r}"
        )

        # Verify other cards were reordered in the database
        cards = await db.get_cards_by_list(lst.id)
        card_positions = {c.id: c.position for c in cards}

        assert card_positions[card_c.id] == 0, (
            f"Card C should now be at position 0, got {card_positions[card_c.id]}"
        )
        assert card_positions[card_a.id] == 1, (
            f"Card A should now be at position 1 (shifted), got {card_positions[card_a.id]}"
        )
        assert card_positions[card_b.id] == 2, (
            f"Card B should now be at position 2 (shifted), got {card_positions[card_b.id]}"
        )

    async def test_move_card_not_found(self, client: httpx.AsyncClient, db: Database) -> None:
        """PUT /api/cards/{id}/move with non-existent id returns 404."""
        _board, lst = await _create_board_and_list(db)
        fake_id = str(uuid.uuid4())

        response = await client.put(
            f"/api/cards/{fake_id}/move",
            json={"list_id": lst.id, "position": 0},
        )

        assert response.status_code == 404, (
            f"PUT /api/cards/{{id}}/move for non-existent card should return 404, "
            f"got {response.status_code}"
        )
        data = response.json()
        assert data["detail"] == "Card not found", (
            f"404 response detail should be 'Card not found', got {data.get('detail')!r}"
        )
