# Feedback Loop Plan: TRE-39

## Overview

Verification strategy for the frontend API client and state management layer. This issue creates two new modules: `frontend/src/lib/api.ts` (typed fetch wrappers for all backend endpoints) and `frontend/src/lib/board-store.ts` (React Query hooks with optimistic updates). Tests verify that the API client correctly calls endpoints with proper HTTP methods, URLs, headers, and body serialization, and that the React Query hooks expose the expected interface.

---

## 1. Unit Tests — API Client (`frontend/tests/api.test.ts`)

These tests verify the API client module exports typed functions for every backend endpoint and that each function calls `fetch` with the correct method, URL, headers, and body.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `exports getBoard function` | `api.ts` exports a `getBoard` function |
| `getBoard calls GET /api/board` | `getBoard()` calls `fetch` with `GET` method and `/api/board` URL |
| `getBoard returns typed BoardDetailResponse` | `getBoard()` returns a promise resolving to `{ id, title, lists: [{ id, title, position, cards }] }` |
| `exports updateBoard function` | `api.ts` exports an `updateBoard` function |
| `updateBoard calls PUT /api/board` | `updateBoard({ title })` calls `fetch` with `PUT` method, `/api/board` URL, and JSON body |
| `exports createList function` | `api.ts` exports a `createList` function |
| `createList calls POST /api/lists` | `createList({ title, board_id })` calls `fetch` with `POST` method and `/api/lists` URL |
| `exports updateList function` | `api.ts` exports an `updateList` function |
| `updateList calls PUT /api/lists/{id}` | `updateList(id, { title })` calls `fetch` with `PUT` method and `/api/lists/{id}` URL |
| `exports deleteList function` | `api.ts` exports a `deleteList` function |
| `deleteList calls DELETE /api/lists/{id}` | `deleteList(id)` calls `fetch` with `DELETE` method and `/api/lists/{id}` URL |
| `exports reorderLists function` | `api.ts` exports a `reorderLists` function |
| `reorderLists calls PUT /api/lists/reorder` | `reorderLists({ list_ids })` calls `fetch` with `PUT` method and `/api/lists/reorder` URL |
| `exports createCard function` | `api.ts` exports a `createCard` function |
| `createCard calls POST /api/cards` | `createCard({ title, list_id })` calls `fetch` with `POST` method and `/api/cards` URL |
| `exports updateCard function` | `api.ts` exports an `updateCard` function |
| `updateCard calls PUT /api/cards/{id}` | `updateCard(id, { title })` calls `fetch` with `PUT` method and `/api/cards/{id}` URL |
| `exports deleteCard function` | `api.ts` exports a `deleteCard` function |
| `deleteCard calls DELETE /api/cards/{id}` | `deleteCard(id)` calls `fetch` with `DELETE` method and `/api/cards/{id}` URL |
| `exports moveCard function` | `api.ts` exports a `moveCard` function |
| `moveCard calls PUT /api/cards/{id}/move` | `moveCard(id, { list_id, position })` calls `fetch` with `PUT` method and `/api/cards/{id}/move` URL |
| `throws on error response` | When fetch returns a non-OK status, the function throws with the `detail` message from the error response |

### Run Command

```bash
cd frontend && pnpm vitest run tests/api.test.ts
```

---

## 2. Unit Tests — TypeScript Types (`frontend/tests/api.test.ts`)

These tests verify that the module exports the expected TypeScript types.

### Type Verification

| Type Name | Expected Fields |
|---|---|
| `Board` | `{ id: string, title: string }` |
| `List` | `{ id: string, title: string, board_id: string, position: number }` |
| `Card` | `{ id: string, title: string, list_id: string, position: number }` |
| `BoardDetailResponse` | `{ id: string, title: string, lists: ListWithCards[] }` |
| `ListWithCards` | `{ id: string, title: string, position: number, cards: CardResponse[] }` |
| `CardResponse` | `{ id: string, title: string, position: number }` |

---

## 3. Unit Tests — Board Store / React Query Hooks (`frontend/tests/board-store.test.ts`)

These tests verify the React Query hooks module exports the expected hooks and that they function correctly.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `exports useBoard hook` | `board-store.ts` exports a `useBoard` function |
| `useBoard returns query result with data/isLoading/isError` | `useBoard()` returns an object with `data`, `isLoading`, `isError` properties |
| `exports useUpdateBoard mutation hook` | `board-store.ts` exports a `useUpdateBoard` function |
| `exports useCreateList mutation hook` | `board-store.ts` exports a `useCreateList` function |
| `exports useUpdateList mutation hook` | `board-store.ts` exports a `useUpdateList` function |
| `exports useDeleteList mutation hook` | `board-store.ts` exports a `useDeleteList` function |
| `exports useReorderLists mutation hook` | `board-store.ts` exports a `useReorderLists` function |
| `exports useCreateCard mutation hook` | `board-store.ts` exports a `useCreateCard` function |
| `exports useUpdateCard mutation hook` | `board-store.ts` exports a `useUpdateCard` function |
| `exports useDeleteCard mutation hook` | `board-store.ts` exports a `useDeleteCard` function |
| `exports useMoveCard mutation hook` | `board-store.ts` exports a `useMoveCard` function |
| `useBoard calls getBoard on mount` | When rendered, `useBoard` triggers a fetch to GET /api/board |
| `mutation hooks return mutate function` | Each mutation hook returns an object with a `mutate` or `mutateAsync` function |

### Run Command

```bash
cd frontend && pnpm vitest run tests/board-store.test.ts
```

---

## 4. Non-Regression Tests

Verify existing tests still pass after adding new test files.

### Test Suites

| Suite | File | Expected |
|---|---|---|
| Smoke | `tests/smoke.test.ts` | 1 test passes |

### Run Command

```bash
cd frontend && pnpm vitest run
```

---

## 5. Static Analysis

### Linting

```bash
cd frontend && pnpm lint
```

---

## Feedback Completeness Score

| Dimension | Score (0-2) | Justification |
|---|---|---|
| Unit tests — API client | 2 | 21 test cases covering all 10 endpoints, error handling, and type exports |
| Unit tests — state management | 2 | 13 test cases covering all hooks and their interfaces |
| Type verification | 1 | Types checked at compile-time via TypeScript strict mode |
| Non-regression | 1 | Full existing test suite re-run |
| Static analysis | 1 | Biome linting on all new/modified files |

**Total feedback_completeness_score: 7/10**

The score of 7 exceeds the minimum threshold of 6. E2E tests are not applicable as this is a data layer with no visual components.
