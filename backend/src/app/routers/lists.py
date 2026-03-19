"""List API endpoints: CRUD + reorder for lists on a board."""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from app.logging import get_logger
from app.models import List

log = get_logger(module="routers.lists")

router = APIRouter(tags=["lists"])


# ── Request models ──────────────────────────────────────────────────────


class CreateListRequest(BaseModel):
    """Request body for creating a new list."""

    title: str
    board_id: str


class UpdateListRequest(BaseModel):
    """Request body for updating a list's title."""

    title: str


class ReorderListsRequest(BaseModel):
    """Request body for reordering lists on a board."""

    list_ids: list[str]


# ── Endpoints ───────────────────────────────────────────────────────────


@router.post("/lists", status_code=201)
async def create_list(body: CreateListRequest, request: Request) -> dict:
    """Create a new list with auto-assigned position."""
    db = request.app.state.db
    existing_lists = await db.get_lists_by_board(body.board_id)
    position = len(existing_lists)
    lst = List(title=body.title, board_id=body.board_id, position=position)
    created = await db.create_list(lst)
    log.info("list_created", list_id=created.id, board_id=body.board_id, position=position)
    return created.model_dump()


@router.put("/lists/reorder")
async def reorder_lists(body: ReorderListsRequest, request: Request) -> list[dict]:
    """Reorder lists on a board by updating positions to match the submitted order."""
    db = request.app.state.db
    if not body.list_ids:
        return []
    for index, list_id in enumerate(body.list_ids):
        await db.update_list(list_id=list_id, position=index)
    first_list = await db.get_list(body.list_ids[0])
    if first_list is None:
        return []
    reordered = await db.get_lists_by_board(first_list.board_id)
    log.info("lists_reordered", list_ids=body.list_ids, board_id=first_list.board_id)
    return [lst.model_dump() for lst in reordered]


@router.put("/lists/{list_id}")
async def update_list(list_id: str, body: UpdateListRequest, request: Request) -> dict:
    """Update a list's title."""
    db = request.app.state.db
    updated = await db.update_list(list_id=list_id, title=body.title)
    if updated is None:
        raise HTTPException(status_code=404, detail="List not found")
    log.info("list_updated", list_id=list_id)
    return updated.model_dump()


@router.delete("/lists/{list_id}", status_code=204)
async def delete_list(list_id: str, request: Request) -> Response:
    """Delete a list and all its cards (CASCADE)."""
    db = request.app.state.db
    deleted = await db.delete_list(list_id=list_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="List not found")
    log.info("list_deleted", list_id=list_id)
    return Response(status_code=204)
