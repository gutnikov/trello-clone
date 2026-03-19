"""Data models for the Trello clone backend.

Stub module — implementation pending (TRE-31).
Models are importable but not yet implemented with correct behavior.
"""

from pydantic import BaseModel


class Board(BaseModel):
    """Board model stub — fields and validation not yet implemented."""

    id: str = ""
    title: str = ""


class List(BaseModel):
    """List model stub — fields and validation not yet implemented."""

    id: str = ""
    title: str = ""
    board_id: str = ""
    position: int = -1


class Card(BaseModel):
    """Card model stub — fields and validation not yet implemented."""

    id: str = ""
    title: str = ""
    list_id: str = ""
    position: int = -1
