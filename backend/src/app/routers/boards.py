"""Board API endpoints for the Trello Clone.

Provides GET /board (nested response) and PUT /board (update title).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.database import Database
from app.logging import get_logger

log = get_logger(module="routers.boards")

router = APIRouter(tags=["boards"])


# ── Response / Request Schemas ──────────────────────────────────────────


class CardResponse(BaseModel):
    """API response representation of a card within a list."""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    position: int


class ListWithCards(BaseModel):
    """A list with its nested cards for the board detail response."""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    position: int
    cards: list[CardResponse]


class BoardDetailResponse(BaseModel):
    """Top-level nested board response for GET /api/board."""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    lists: list[ListWithCards]


class BoardUpdateRequest(BaseModel):
    """Request body for PUT /api/board."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1)


class BoardResponse(BaseModel):
    """Flat board response for PUT /api/board."""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str


# ── Endpoints ───────────────────────────────────────────────────────────


@router.get("/board", response_model=BoardDetailResponse)
async def get_board(request: Request) -> BoardDetailResponse:
    """Return the single board with all lists and cards in a nested response."""
    db: Database = request.app.state.db

    boards = await db.list_boards()
    if not boards:
        raise HTTPException(status_code=404, detail="No board found")

    board = boards[0]
    lists = await db.get_lists_by_board(board.id)

    lists_with_cards: list[ListWithCards] = []
    for lst in lists:
        cards = await db.get_cards_by_list(lst.id)
        lists_with_cards.append(
            ListWithCards(
                id=lst.id,
                title=lst.title,
                position=lst.position,
                cards=[CardResponse(id=c.id, title=c.title, position=c.position) for c in cards],
            )
        )

    return BoardDetailResponse(
        id=board.id,
        title=board.title,
        lists=lists_with_cards,
    )


@router.put("/board", response_model=BoardResponse)
async def update_board(request: Request, body: BoardUpdateRequest) -> BoardResponse:
    """Update the board title."""
    db: Database = request.app.state.db

    boards = await db.list_boards()
    if not boards:
        raise HTTPException(status_code=404, detail="No board found")

    board = boards[0]
    updated = await db.update_board(board.id, body.title)
    if updated is None:
        raise HTTPException(status_code=404, detail="Board not found")

    log.info("board_updated", board_id=board.id, new_title=body.title)
    return BoardResponse(id=updated.id, title=updated.title)
