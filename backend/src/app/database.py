"""SQLite persistence layer for the Trello clone backend.

Provides async CRUD operations for Board, List, and Card entities
using aiosqlite with WAL mode and foreign key enforcement.
"""

from __future__ import annotations

from pathlib import Path

import aiosqlite

from app.logging import get_logger
from app.models import Board, Card, List

log = get_logger(module="database")


class Database:
    """Async SQLite persistence layer for boards, lists, and cards."""

    _conn: aiosqlite.Connection | None

    def __init__(self, db_path: str | Path = "data/trello.db") -> None:
        self.db_path = str(db_path)
        self._conn = None

    async def connect(self) -> None:
        """Open database connection, enable WAL mode and foreign keys."""
        self._conn = await aiosqlite.connect(self.db_path)
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        log.info("database_connected", db_path=self.db_path)

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
            log.info("database_closed")

    async def init_schema(self) -> None:
        """Create tables if they don't exist."""
        assert self._conn is not None, "Database not connected"
        await self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS boards (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS lists (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                board_id TEXT NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                list_id TEXT NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE
            );
            """
        )
        await self._conn.commit()
        log.info("schema_initialized")

    async def seed_default_board(self) -> Board:
        """Seed a default board if none exist. Idempotent."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute("SELECT id, title FROM boards LIMIT 1")
        row = await cursor.fetchone()
        if row is not None:
            log.info("seed_default_board_skipped", reason="board_exists")
            return Board(id=row[0], title=row[1])
        board = Board(title="My Board")
        await self._conn.execute(
            "INSERT INTO boards (id, title) VALUES (?, ?)",
            (board.id, board.title),
        )
        await self._conn.commit()
        log.info("seed_default_board_created", board_id=board.id)
        return board

    # ── Board CRUD ──────────────────────────────────────────────────────

    async def create_board(self, board: Board) -> Board:
        """Insert a board into the database."""
        assert self._conn is not None, "Database not connected"
        await self._conn.execute(
            "INSERT INTO boards (id, title) VALUES (?, ?)",
            (board.id, board.title),
        )
        await self._conn.commit()
        return board

    async def get_board(self, board_id: str) -> Board | None:
        """Retrieve a board by ID, or None if not found."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute("SELECT id, title FROM boards WHERE id = ?", (board_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        return Board(id=row[0], title=row[1])

    async def list_boards(self) -> list[Board]:
        """Return all boards."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute("SELECT id, title FROM boards")
        rows = await cursor.fetchall()
        return [Board(id=row[0], title=row[1]) for row in rows]

    async def update_board(self, board_id: str, title: str) -> Board | None:
        """Update a board's title. Returns updated board or None if not found."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute(
            "UPDATE boards SET title = ? WHERE id = ?", (title, board_id)
        )
        await self._conn.commit()
        if cursor.rowcount == 0:
            return None
        return await self.get_board(board_id)

    async def delete_board(self, board_id: str) -> bool:
        """Delete a board by ID. Returns True if deleted, False if not found."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        await self._conn.commit()
        return cursor.rowcount > 0

    # ── List CRUD ───────────────────────────────────────────────────────

    async def create_list(self, lst: List) -> List:
        """Insert a list into the database."""
        assert self._conn is not None, "Database not connected"
        await self._conn.execute(
            "INSERT INTO lists (id, title, board_id, position) VALUES (?, ?, ?, ?)",
            (lst.id, lst.title, lst.board_id, lst.position),
        )
        await self._conn.commit()
        return lst

    async def get_list(self, list_id: str) -> List | None:
        """Retrieve a list by ID, or None if not found."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute(
            "SELECT id, title, board_id, position FROM lists WHERE id = ?", (list_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return List(id=row[0], title=row[1], board_id=row[2], position=row[3])

    async def get_lists_by_board(self, board_id: str) -> list[List]:
        """Return all lists for a board, ordered by position."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute(
            "SELECT id, title, board_id, position FROM lists WHERE board_id = ? ORDER BY position",
            (board_id,),
        )
        rows = await cursor.fetchall()
        return [List(id=row[0], title=row[1], board_id=row[2], position=row[3]) for row in rows]

    async def update_list(
        self, list_id: str, title: str | None = None, position: int | None = None
    ) -> List | None:
        """Update a list's title and/or position. Returns updated list or None."""
        assert self._conn is not None, "Database not connected"
        updates: list[str] = []
        params: list[str | int] = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if position is not None:
            updates.append("position = ?")
            params.append(position)
        if not updates:
            return await self.get_list(list_id)
        params.append(list_id)
        query = f"UPDATE lists SET {', '.join(updates)} WHERE id = ?"  # noqa: S608
        cursor = await self._conn.execute(query, params)
        await self._conn.commit()
        if cursor.rowcount == 0:
            return None
        return await self.get_list(list_id)

    async def delete_list(self, list_id: str) -> bool:
        """Delete a list by ID. Returns True if deleted, False if not found."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute("DELETE FROM lists WHERE id = ?", (list_id,))
        await self._conn.commit()
        return cursor.rowcount > 0

    # ── Card CRUD ───────────────────────────────────────────────────────

    async def create_card(self, card: Card) -> Card:
        """Insert a card into the database."""
        assert self._conn is not None, "Database not connected"
        await self._conn.execute(
            "INSERT INTO cards (id, title, list_id, position) VALUES (?, ?, ?, ?)",
            (card.id, card.title, card.list_id, card.position),
        )
        await self._conn.commit()
        return card

    async def get_card(self, card_id: str) -> Card | None:
        """Retrieve a card by ID, or None if not found."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute(
            "SELECT id, title, list_id, position FROM cards WHERE id = ?", (card_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Card(id=row[0], title=row[1], list_id=row[2], position=row[3])

    async def get_cards_by_list(self, list_id: str) -> list[Card]:
        """Return all cards for a list, ordered by position."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute(
            "SELECT id, title, list_id, position FROM cards WHERE list_id = ? ORDER BY position",
            (list_id,),
        )
        rows = await cursor.fetchall()
        return [Card(id=row[0], title=row[1], list_id=row[2], position=row[3]) for row in rows]

    async def update_card(
        self,
        card_id: str,
        title: str | None = None,
        position: int | None = None,
        list_id: str | None = None,
    ) -> Card | None:
        """Update a card's title, position, and/or list_id. Returns updated card or None."""
        assert self._conn is not None, "Database not connected"
        updates: list[str] = []
        params: list[str | int] = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if position is not None:
            updates.append("position = ?")
            params.append(position)
        if list_id is not None:
            updates.append("list_id = ?")
            params.append(list_id)
        if not updates:
            return await self.get_card(card_id)
        params.append(card_id)
        query = f"UPDATE cards SET {', '.join(updates)} WHERE id = ?"  # noqa: S608
        cursor = await self._conn.execute(query, params)
        await self._conn.commit()
        if cursor.rowcount == 0:
            return None
        return await self.get_card(card_id)

    async def delete_card(self, card_id: str) -> bool:
        """Delete a card by ID. Returns True if deleted, False if not found."""
        assert self._conn is not None, "Database not connected"
        cursor = await self._conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        await self._conn.commit()
        return cursor.rowcount > 0
