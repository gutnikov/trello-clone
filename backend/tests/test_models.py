"""Unit tests for Pydantic data models (Board, List, Card).

Verifies model creation, defaults, validation constraints, and immutability.
These tests correspond to the feedback loop plan in docs/feedback-loops/TRE-31-feedback.md.
"""

import uuid

import pytest
from pydantic import ValidationError

from app.models import Board, Card, List


class TestBoard:
    """Tests for the Board model."""

    def test_board_creation_defaults(self) -> None:
        """Board created with only `title` has auto-generated UUID `id`."""
        board = Board(title="Test Board")
        # id should be a non-empty, valid UUID v4 string
        assert board.id, "Board id should not be empty"
        try:
            parsed = uuid.UUID(board.id)
        except ValueError:
            pytest.fail(f"Board id {board.id!r} is not a valid UUID string")
        assert parsed.version == 4, "Board id should be a UUID v4"
        assert board.title == "Test Board"

    def test_board_creation_explicit_id(self) -> None:
        """Board created with explicit `id` and `title` preserves both."""
        explicit_id = str(uuid.uuid4())
        board = Board(id=explicit_id, title="My Board")
        assert board.id == explicit_id, "Board should preserve explicit id"
        assert board.title == "My Board", "Board should preserve explicit title"

    def test_board_rejects_empty_title(self) -> None:
        """ValidationError raised when `title` is empty string."""
        with pytest.raises(ValidationError, match="title"):
            Board(title="")

    def test_board_immutable(self) -> None:
        """Assigning to `board.title` raises ValidationError (frozen model)."""
        board = Board(title="Immutable Board")
        with pytest.raises(ValidationError):
            board.title = "Changed"  # type: ignore[misc]


class TestList:
    """Tests for the List model."""

    def test_list_creation_defaults(self) -> None:
        """List created with `title` and `board_id` has `position=0` and auto UUID."""
        board_id = str(uuid.uuid4())
        lst = List(title="To Do", board_id=board_id)
        # id should be a non-empty, valid UUID v4 string
        assert lst.id, "List id should not be empty"
        try:
            parsed = uuid.UUID(lst.id)
        except ValueError:
            pytest.fail(f"List id {lst.id!r} is not a valid UUID string")
        assert parsed.version == 4, "List id should be a UUID v4"
        assert lst.title == "To Do"
        assert lst.board_id == board_id
        assert lst.position == 0, "List position should default to 0"

    def test_list_creation_explicit_position(self) -> None:
        """List with explicit `position=5` preserves the value."""
        board_id = str(uuid.uuid4())
        lst = List(title="Done", board_id=board_id, position=5)
        assert lst.position == 5, "List should preserve explicit position"

    def test_list_rejects_empty_title(self) -> None:
        """ValidationError raised when `title` is empty string."""
        board_id = str(uuid.uuid4())
        with pytest.raises(ValidationError, match="title"):
            List(title="", board_id=board_id)

    def test_list_immutable(self) -> None:
        """Assigning to `lst.position` raises ValidationError (frozen model)."""
        board_id = str(uuid.uuid4())
        lst = List(title="In Progress", board_id=board_id)
        with pytest.raises(ValidationError):
            lst.position = 99  # type: ignore[misc]


class TestCard:
    """Tests for the Card model."""

    def test_card_creation_defaults(self) -> None:
        """Card created with `title` and `list_id` has `position=0` and auto UUID."""
        list_id = str(uuid.uuid4())
        card = Card(title="My Task", list_id=list_id)
        # id should be a non-empty, valid UUID v4 string
        assert card.id, "Card id should not be empty"
        try:
            parsed = uuid.UUID(card.id)
        except ValueError:
            pytest.fail(f"Card id {card.id!r} is not a valid UUID string")
        assert parsed.version == 4, "Card id should be a UUID v4"
        assert card.title == "My Task"
        assert card.list_id == list_id
        assert card.position == 0, "Card position should default to 0"

    def test_card_creation_explicit_position(self) -> None:
        """Card with explicit `position=3` preserves the value."""
        list_id = str(uuid.uuid4())
        card = Card(title="Another Task", list_id=list_id, position=3)
        assert card.position == 3, "Card should preserve explicit position"

    def test_card_rejects_empty_title(self) -> None:
        """ValidationError raised when `title` is empty string."""
        list_id = str(uuid.uuid4())
        with pytest.raises(ValidationError, match="title"):
            Card(title="", list_id=list_id)

    def test_card_immutable(self) -> None:
        """Assigning to `card.title` raises ValidationError (frozen model)."""
        list_id = str(uuid.uuid4())
        card = Card(title="Frozen Card", list_id=list_id)
        with pytest.raises(ValidationError):
            card.title = "Changed"  # type: ignore[misc]
