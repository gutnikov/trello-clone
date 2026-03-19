"""Data models for the Trello clone backend.

Defines Board, List, and Card Pydantic models with validation and immutability.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


def _uuid4_str() -> str:
    """Generate a UUID v4 string."""
    return str(uuid.uuid4())


class Board(BaseModel):
    """A Trello-style board containing lists."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=_uuid4_str)
    title: str = Field(min_length=1)


class List(BaseModel):
    """A list within a board, containing cards. Ordered by position."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=_uuid4_str)
    title: str = Field(min_length=1)
    board_id: str
    position: int = 0


class Card(BaseModel):
    """A card within a list. Ordered by position."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=_uuid4_str)
    title: str = Field(min_length=1)
    list_id: str
    position: int = 0
