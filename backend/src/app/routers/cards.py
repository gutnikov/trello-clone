"""Card API router: CRUD operations and move/reorder.

Endpoints:
- POST   /cards          — Create a new card (auto-assign position)
- PUT    /cards/{id}     — Update card title
- DELETE /cards/{id}     — Delete a card
- PUT    /cards/{id}/move — Move card to different list and/or reorder
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.responses import Response

from app.database import Database
from app.logging import get_logger
from app.models import Card

log = get_logger(module="cards_router")

router = APIRouter(tags=["cards"])


# ── Request Schemas ─────────────────────────────────────────────────────


class CreateCardRequest(BaseModel):
    """Request body for creating a card."""

    title: str = Field(min_length=1)
    list_id: str


class UpdateCardRequest(BaseModel):
    """Request body for updating a card's title."""

    title: str = Field(min_length=1)


class MoveCardRequest(BaseModel):
    """Request body for moving/reordering a card."""

    list_id: str
    position: int


# ── Helpers ─────────────────────────────────────────────────────────────


def _get_db(request: Request) -> Database:
    """Retrieve the Database instance from app state."""
    return request.app.state.db  # type: ignore[no-any-return]


# ── Endpoints ───────────────────────────────────────────────────────────


@router.post("/cards", status_code=201)
async def create_card(body: CreateCardRequest, request: Request) -> dict[str, object]:
    """Create a new card in the specified list with auto-assigned position."""
    db = _get_db(request)
    existing_cards = await db.get_cards_by_list(body.list_id)
    position = len(existing_cards)
    card = Card(title=body.title, list_id=body.list_id, position=position)
    await db.create_card(card)
    log.info("card_created", card_id=card.id, list_id=body.list_id, position=position)
    return card.model_dump()


@router.put("/cards/{card_id}")
async def update_card(card_id: str, body: UpdateCardRequest, request: Request) -> dict[str, object]:
    """Update a card's title."""
    db = _get_db(request)
    updated = await db.update_card(card_id, title=body.title)
    if updated is None:
        raise HTTPException(status_code=404, detail="Card not found")
    log.info("card_updated", card_id=card_id)
    return updated.model_dump()


@router.delete("/cards/{card_id}", status_code=204, response_class=Response)
async def delete_card(card_id: str, request: Request) -> Response:
    """Delete a card by ID."""
    db = _get_db(request)
    deleted = await db.delete_card(card_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Card not found")
    log.info("card_deleted", card_id=card_id)
    return Response(status_code=204)


@router.put("/cards/{card_id}/move")
async def move_card(card_id: str, body: MoveCardRequest, request: Request) -> dict[str, object]:
    """Move a card to a different list and/or reorder within a list."""
    db = _get_db(request)

    # Fetch current card
    card = await db.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")

    source_list_id = card.list_id
    target_list_id = body.list_id
    target_position = body.position

    if source_list_id == target_list_id:
        # Reorder within the same list
        cards = await db.get_cards_by_list(source_list_id)
        # Remove the moving card from the list
        remaining = [c for c in cards if c.id != card_id]
        # Insert at the target position
        remaining.insert(target_position, card)
        # Reassign positions sequentially
        for idx, c in enumerate(remaining):
            if c.position != idx or (
                c.id == card_id and (c.list_id != target_list_id or c.position != idx)
            ):
                await db.update_card(c.id, position=idx, list_id=target_list_id)
    else:
        # Move between lists
        # Update source list: remove card and reassign positions
        source_cards = await db.get_cards_by_list(source_list_id)
        source_remaining = [c for c in source_cards if c.id != card_id]
        for idx, c in enumerate(source_remaining):
            if c.position != idx:
                await db.update_card(c.id, position=idx)

        # Update target list: insert card and reassign positions
        target_cards = await db.get_cards_by_list(target_list_id)
        target_cards.insert(target_position, card)
        for idx, c in enumerate(target_cards):
            if c.id == card_id:
                await db.update_card(c.id, list_id=target_list_id, position=idx)
            elif c.position != idx:
                await db.update_card(c.id, position=idx)

    # Fetch the final state of the moved card
    updated = await db.get_card(card_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Card not found")

    log.info(
        "card_moved",
        card_id=card_id,
        source_list_id=source_list_id,
        target_list_id=target_list_id,
        new_position=target_position,
    )
    return updated.model_dump()
