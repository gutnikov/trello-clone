"""Unit tests for SQLite persistence layer (Database CRUD operations).

Verifies schema creation, seed logic, and full CRUD for Board, List, and Card entities.
Uses in-memory SQLite for isolation and speed.
These tests correspond to the feedback loop plan in docs/feedback-loops/TRE-31-feedback.md.
"""

import uuid

import pytest

from app.database import Database
from app.models import Board, Card, List


@pytest.fixture
async def db() -> Database:  # type: ignore[misc]
    """Create an in-memory Database instance with schema initialized."""
    database = Database(":memory:")
    await database.connect()
    await database.init_schema()
    yield database  # type: ignore[misc]
    await database.close()


class TestSchema:
    """Tests for schema initialization."""

    async def test_schema_creates_tables(self, db: Database) -> None:
        """After init_schema, querying sqlite_master returns boards, lists, cards tables."""
        # The db fixture already called init_schema; we verify the tables exist.
        # We need to access the internal connection to query sqlite_master.
        assert db._conn is not None, "Database connection should be established"
        cursor = await db._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        rows = await cursor.fetchall()
        table_names = sorted(row[0] for row in rows)
        assert "boards" in table_names, "boards table should exist"
        assert "cards" in table_names, "cards table should exist"
        assert "lists" in table_names, "lists table should exist"


class TestSeedDefaultBoard:
    """Tests for default board seeding."""

    async def test_seed_default_board_creates_board(self, db: Database) -> None:
        """seed_default_board inserts one board titled 'My Board' when DB is empty."""
        board = await db.seed_default_board()
        assert board.title == "My Board", "Default board should be titled 'My Board'"
        assert board.id is not None, "Default board should have an id"
        # Verify it's in the database
        boards = await db.list_boards()
        assert len(boards) == 1, "Should have exactly one board after seeding"

    async def test_seed_default_board_idempotent(self, db: Database) -> None:
        """Calling seed_default_board twice returns same board; list_boards returns exactly 1."""
        board1 = await db.seed_default_board()
        board2 = await db.seed_default_board()
        assert board1.id == board2.id, "Seed should return the same board on second call"
        boards = await db.list_boards()
        assert len(boards) == 1, "Should still have exactly one board after double seed"


class TestBoardCRUD:
    """Tests for Board CRUD operations."""

    async def test_create_board(self, db: Database) -> None:
        """create_board inserts a board; get_board retrieves it with matching fields."""
        board = Board(title="Project Alpha")
        created = await db.create_board(board)
        assert created.id == board.id, "Created board should have the same id"
        assert created.title == "Project Alpha"

        retrieved = await db.get_board(board.id)
        assert retrieved is not None, "get_board should find the created board"
        assert retrieved.id == board.id
        assert retrieved.title == "Project Alpha"

    async def test_get_board_not_found(self, db: Database) -> None:
        """get_board with non-existent ID returns None."""
        result = await db.get_board(str(uuid.uuid4()))
        assert result is None, "get_board should return None for non-existent ID"

    async def test_list_boards(self, db: Database) -> None:
        """After creating 3 boards, list_boards returns all 3."""
        for i in range(3):
            await db.create_board(Board(title=f"Board {i}"))
        boards = await db.list_boards()
        assert len(boards) == 3, "list_boards should return all 3 created boards"

    async def test_update_board(self, db: Database) -> None:
        """update_board changes title; subsequent get_board reflects the change."""
        board = Board(title="Old Title")
        await db.create_board(board)
        updated = await db.update_board(board.id, title="New Title")
        assert updated is not None, "update_board should return the updated board"
        assert updated.title == "New Title", "Title should be updated"

        retrieved = await db.get_board(board.id)
        assert retrieved is not None
        assert retrieved.title == "New Title"

    async def test_update_board_not_found(self, db: Database) -> None:
        """update_board with non-existent ID returns None."""
        result = await db.update_board(str(uuid.uuid4()), title="Nope")
        assert result is None, "update_board should return None for non-existent ID"

    async def test_delete_board(self, db: Database) -> None:
        """delete_board returns True; subsequent get_board returns None."""
        board = Board(title="To Delete")
        await db.create_board(board)
        deleted = await db.delete_board(board.id)
        assert deleted is True, "delete_board should return True for existing board"

        retrieved = await db.get_board(board.id)
        assert retrieved is None, "get_board should return None after deletion"

    async def test_delete_board_not_found(self, db: Database) -> None:
        """delete_board with non-existent ID returns False."""
        result = await db.delete_board(str(uuid.uuid4()))
        assert result is False, "delete_board should return False for non-existent ID"


class TestListCRUD:
    """Tests for List CRUD operations."""

    async def test_create_list(self, db: Database) -> None:
        """create_list inserts a list; get_list retrieves it."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="To Do", board_id=board.id)
        created = await db.create_list(lst)
        assert created.id == lst.id
        assert created.title == "To Do"

        retrieved = await db.get_list(lst.id)
        assert retrieved is not None, "get_list should find the created list"
        assert retrieved.title == "To Do"
        assert retrieved.board_id == board.id

    async def test_get_lists_by_board_ordered(self, db: Database) -> None:
        """Lists for a board are returned ordered by position."""
        board = Board(title="Board")
        await db.create_board(board)
        # Create lists out of order
        await db.create_list(List(title="Third", board_id=board.id, position=2))
        await db.create_list(List(title="First", board_id=board.id, position=0))
        await db.create_list(List(title="Second", board_id=board.id, position=1))

        lists = await db.get_lists_by_board(board.id)
        assert len(lists) == 3, "Should have 3 lists"
        assert lists[0].title == "First", "Lists should be ordered by position"
        assert lists[1].title == "Second"
        assert lists[2].title == "Third"

    async def test_update_list_title(self, db: Database) -> None:
        """update_list with new title updates the record."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="Old Title", board_id=board.id)
        await db.create_list(lst)

        updated = await db.update_list(lst.id, title="New Title")
        assert updated is not None
        assert updated.title == "New Title", "Title should be updated"

    async def test_update_list_position(self, db: Database) -> None:
        """update_list with new position updates the record."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="Movable", board_id=board.id, position=0)
        await db.create_list(lst)

        updated = await db.update_list(lst.id, position=5)
        assert updated is not None
        assert updated.position == 5, "Position should be updated"

    async def test_delete_list(self, db: Database) -> None:
        """delete_list returns True; subsequent get_list returns None."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="To Delete", board_id=board.id)
        await db.create_list(lst)

        deleted = await db.delete_list(lst.id)
        assert deleted is True, "delete_list should return True for existing list"

        retrieved = await db.get_list(lst.id)
        assert retrieved is None, "get_list should return None after deletion"


class TestCardCRUD:
    """Tests for Card CRUD operations."""

    async def test_create_card(self, db: Database) -> None:
        """create_card inserts a card; get_card retrieves it."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="To Do", board_id=board.id)
        await db.create_list(lst)
        card = Card(title="My Task", list_id=lst.id)
        created = await db.create_card(card)
        assert created.id == card.id
        assert created.title == "My Task"

        retrieved = await db.get_card(card.id)
        assert retrieved is not None, "get_card should find the created card"
        assert retrieved.title == "My Task"
        assert retrieved.list_id == lst.id

    async def test_get_cards_by_list_ordered(self, db: Database) -> None:
        """Cards for a list are returned ordered by position."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="To Do", board_id=board.id)
        await db.create_list(lst)
        # Create cards out of order
        await db.create_card(Card(title="Third", list_id=lst.id, position=2))
        await db.create_card(Card(title="First", list_id=lst.id, position=0))
        await db.create_card(Card(title="Second", list_id=lst.id, position=1))

        cards = await db.get_cards_by_list(lst.id)
        assert len(cards) == 3, "Should have 3 cards"
        assert cards[0].title == "First", "Cards should be ordered by position"
        assert cards[1].title == "Second"
        assert cards[2].title == "Third"

    async def test_update_card_title(self, db: Database) -> None:
        """update_card with new title updates the record."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="To Do", board_id=board.id)
        await db.create_list(lst)
        card = Card(title="Old Title", list_id=lst.id)
        await db.create_card(card)

        updated = await db.update_card(card.id, title="New Title")
        assert updated is not None
        assert updated.title == "New Title", "Card title should be updated"

    async def test_update_card_position(self, db: Database) -> None:
        """update_card with new position updates the record."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="To Do", board_id=board.id)
        await db.create_list(lst)
        card = Card(title="Movable", list_id=lst.id, position=0)
        await db.create_card(card)

        updated = await db.update_card(card.id, position=7)
        assert updated is not None
        assert updated.position == 7, "Card position should be updated"

    async def test_update_card_move_to_list(self, db: Database) -> None:
        """update_card with new list_id moves card between lists."""
        board = Board(title="Board")
        await db.create_board(board)
        lst1 = List(title="To Do", board_id=board.id, position=0)
        lst2 = List(title="Done", board_id=board.id, position=1)
        await db.create_list(lst1)
        await db.create_list(lst2)
        card = Card(title="Moving Card", list_id=lst1.id)
        await db.create_card(card)

        updated = await db.update_card(card.id, list_id=lst2.id)
        assert updated is not None
        assert updated.list_id == lst2.id, "Card should be moved to the new list"

        # Verify the card is no longer in the old list
        old_list_cards = await db.get_cards_by_list(lst1.id)
        assert len(old_list_cards) == 0, "Old list should have no cards"
        new_list_cards = await db.get_cards_by_list(lst2.id)
        assert len(new_list_cards) == 1, "New list should have the moved card"

    async def test_delete_card(self, db: Database) -> None:
        """delete_card returns True; subsequent get_card returns None."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="To Do", board_id=board.id)
        await db.create_list(lst)
        card = Card(title="To Delete", list_id=lst.id)
        await db.create_card(card)

        deleted = await db.delete_card(card.id)
        assert deleted is True, "delete_card should return True for existing card"

        retrieved = await db.get_card(card.id)
        assert retrieved is None, "get_card should return None after deletion"


class TestCascadeDelete:
    """Tests for cascade/referential integrity behavior."""

    async def test_delete_board_cascades(self, db: Database) -> None:
        """Deleting a board also removes its lists and cards (CASCADE)."""
        board = Board(title="Cascade Board")
        await db.create_board(board)
        lst = List(title="Cascade List", board_id=board.id)
        await db.create_list(lst)
        card = Card(title="Cascade Card", list_id=lst.id)
        await db.create_card(card)

        deleted = await db.delete_board(board.id)
        assert deleted is True

        # Lists and cards should also be gone
        assert await db.get_list(lst.id) is None, "List should be deleted with board"
        assert await db.get_card(card.id) is None, "Card should be deleted with board"

    async def test_delete_list_cascades_cards(self, db: Database) -> None:
        """Deleting a list also removes its cards (CASCADE)."""
        board = Board(title="Board")
        await db.create_board(board)
        lst = List(title="Cascade List", board_id=board.id)
        await db.create_list(lst)
        card = Card(title="Cascade Card", list_id=lst.id)
        await db.create_card(card)

        deleted = await db.delete_list(lst.id)
        assert deleted is True

        # Card should be gone, but board should remain
        assert await db.get_card(card.id) is None, "Card should be deleted with list"
        assert await db.get_board(board.id) is not None, "Board should still exist"
