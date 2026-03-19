"""SQLite persistence layer for the Trello clone backend.

Stub module — implementation pending (TRE-31).
Methods are importable but not yet implemented with correct behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import aiosqlite

from app.models import Board, Card, List


class Database:
    """SQLite persistence layer stub — not yet implemented."""

    _conn: aiosqlite.Connection | None

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = db_path
        self._conn = None

    async def connect(self) -> None:
        """Open database connection — stub, does nothing."""

    async def close(self) -> None:
        """Close database connection — stub, does nothing."""

    async def init_schema(self) -> None:
        """Initialize database schema — stub, does nothing."""

    async def seed_default_board(self) -> Board:
        """Seed default board — stub, returns empty board."""
        return Board()

    async def create_board(self, board: Board) -> Board:
        """Create a board — stub, returns empty board."""
        return Board()

    async def get_board(self, board_id: str) -> Board | None:
        """Get a board by ID — stub, returns None."""
        return None

    async def list_boards(self) -> list[Board]:
        """List all boards — stub, returns empty list."""
        return []

    async def update_board(self, board_id: str, title: str) -> Board | None:
        """Update a board — stub, returns None."""
        return None

    async def delete_board(self, board_id: str) -> bool:
        """Delete a board — stub, returns False."""
        return False

    async def create_list(self, lst: List) -> List:
        """Create a list — stub, returns empty list model."""
        return List()

    async def get_list(self, list_id: str) -> List | None:
        """Get a list by ID — stub, returns None."""
        return None

    async def get_lists_by_board(self, board_id: str) -> list[List]:
        """Get lists by board — stub, returns empty list."""
        return []

    async def update_list(
        self, list_id: str, title: str | None = None, position: int | None = None
    ) -> List | None:
        """Update a list — stub, returns None."""
        return None

    async def delete_list(self, list_id: str) -> bool:
        """Delete a list — stub, returns False."""
        return False

    async def create_card(self, card: Card) -> Card:
        """Create a card — stub, returns empty card model."""
        return Card()

    async def get_card(self, card_id: str) -> Card | None:
        """Get a card by ID — stub, returns None."""
        return None

    async def get_cards_by_list(self, list_id: str) -> list[Card]:
        """Get cards by list — stub, returns empty list."""
        return []

    async def update_card(
        self,
        card_id: str,
        title: str | None = None,
        position: int | None = None,
        list_id: str | None = None,
    ) -> Card | None:
        """Update a card — stub, returns None."""
        return None

    async def delete_card(self, card_id: str) -> bool:
        """Delete a card — stub, returns False."""
        return False
