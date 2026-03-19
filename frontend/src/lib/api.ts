/**
 * API client module for the Trello clone backend.
 *
 * Wraps all backend endpoints with typed functions.
 * All endpoints are under the /api prefix.
 */

// ── Types ──────────────────────────────────────────────────────────────────

export interface Card {
  id: string;
  title: string;
  list_id: string;
  position: number;
}

export interface List {
  id: string;
  title: string;
  board_id: string;
  position: number;
  cards: Card[];
}

export interface Board {
  id: string;
  title: string;
}

export interface BoardDetailResponse {
  id: string;
  title: string;
  lists: List[];
}

// ── Request Types ──────────────────────────────────────────────────────────

export interface UpdateBoardRequest {
  title: string;
}

export interface CreateListRequest {
  title: string;
  board_id: string;
}

export interface UpdateListRequest {
  title: string;
}

export interface ReorderListsRequest {
  list_ids: string[];
}

export interface CreateCardRequest {
  title: string;
  list_id: string;
}

export interface UpdateCardRequest {
  title: string;
}

export interface MoveCardRequest {
  list_id: string;
  position: number;
}

// ── Error Handling ─────────────────────────────────────────────────────────

interface ApiErrorResponse {
  detail: string;
}

const API_BASE = "/api";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorBody = (await response.json()) as ApiErrorResponse;
    throw new Error(errorBody.detail);
  }
  return response.json() as Promise<T>;
}

// ── API Functions ──────────────────────────────────────────────────────────

/** GET /api/board — Fetch full board with nested lists and cards */
export async function getBoard(): Promise<BoardDetailResponse> {
  const response = await fetch(`${API_BASE}/board`, { method: "GET" });
  return handleResponse<BoardDetailResponse>(response);
}

/** PUT /api/board — Update board title */
export async function updateBoard(data: UpdateBoardRequest): Promise<Board> {
  const response = await fetch(`${API_BASE}/board`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Board>(response);
}

/** POST /api/lists — Create a new list */
export async function createList(data: CreateListRequest): Promise<List> {
  const response = await fetch(`${API_BASE}/lists`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<List>(response);
}

/** PUT /api/lists/{id} — Update a list */
export async function updateList(id: string, data: UpdateListRequest): Promise<List> {
  const response = await fetch(`${API_BASE}/lists/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<List>(response);
}

/** DELETE /api/lists/{id} — Delete a list */
export async function deleteList(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/lists/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const errorBody = (await response.json()) as ApiErrorResponse;
    throw new Error(errorBody.detail);
  }
}

/** PUT /api/lists/reorder — Reorder lists */
export async function reorderLists(data: ReorderListsRequest): Promise<List[]> {
  const response = await fetch(`${API_BASE}/lists/reorder`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<List[]>(response);
}

/** POST /api/cards — Create a new card */
export async function createCard(data: CreateCardRequest): Promise<Card> {
  const response = await fetch(`${API_BASE}/cards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Card>(response);
}

/** PUT /api/cards/{id} — Update a card */
export async function updateCard(id: string, data: UpdateCardRequest): Promise<Card> {
  const response = await fetch(`${API_BASE}/cards/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Card>(response);
}

/** DELETE /api/cards/{id} — Delete a card */
export async function deleteCard(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/cards/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const errorBody = (await response.json()) as ApiErrorResponse;
    throw new Error(errorBody.detail);
  }
}

/** PUT /api/cards/{id}/move — Move a card to a different list/position */
export async function moveCard(id: string, data: MoveCardRequest): Promise<Card> {
  const response = await fetch(`${API_BASE}/cards/${id}/move`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Card>(response);
}
