# ADR-002: TanStack React Query for Frontend State Management

**Date:** 2026-03-19
**Status:** Accepted

## Context

TRE-39 introduces the first frontend data layer for the Trello clone. The application needs to fetch board data from the backend API and keep the UI in sync with server state during CRUD operations on boards, lists, and cards. Key forces at play:

- The backend follows a single-board paradigm — `GET /api/board` returns the entire board with nested lists and cards in one response.
- Users expect immediate visual feedback when creating, editing, deleting, or reordering items (no loading spinners for every action).
- The frontend uses React with TanStack Router, so the state management solution must integrate cleanly with React's component model.
- The data is primarily server-owned — the frontend does not generate complex derived state; it mirrors what the backend stores.

## Decision

### 1. TanStack React Query (`@tanstack/react-query`) for server state management

We chose TanStack React Query as the data-fetching and caching layer. It manages the full lifecycle of server state: fetching, caching, background refetching, and cache invalidation. The library is configured in `frontend/src/routes/__root.tsx` and hooks are defined in `frontend/src/lib/board-store.ts`.

### 2. Separate API client module

All backend API calls are defined in `frontend/src/lib/api.ts` as plain async functions with full TypeScript types. The React Query hooks in `board-store.ts` consume these functions as `queryFn` / `mutationFn` callbacks. This separation allows the API client to be tested independently of React and reused in non-React contexts (e.g., scripts, SSR).

### 3. Single query key for the board

All board data (including nested lists and cards) is cached under a single query key `["board"]` (`boardQueryKey` in `board-store.ts:14`). This matches the backend's single-board paradigm where `GET /api/board` returns the complete board state. Mutations invalidate this single key on settlement, triggering a full refetch.

### 4. Optimistic updates with rollback

Every mutation hook (create, update, delete, reorder, move) implements the standard React Query optimistic update pattern:

1. `onMutate`: Cancel in-flight queries, snapshot current cache, apply the optimistic change
2. `onError`: Roll back to the snapshot if the mutation fails
3. `onSettled`: Invalidate the query to refetch authoritative server state

This provides instant UI feedback while ensuring eventual consistency with the server. The pattern is implemented consistently across all 9 mutation hooks in `board-store.ts`.

## Consequences

### Positive
- Instant UI feedback for all CRUD operations — no loading state between user action and visual update
- Automatic cache invalidation ensures the UI never drifts from server state for long
- Built-in loading and error states exposed via `useBoard()` hook reduce boilerplate in components
- API client is testable independently of React Query (pure async functions with fetch)
- TypeScript types for all request/response shapes catch API contract mismatches at compile time

### Negative
- Optimistic updates add complexity to each mutation hook (~30 lines per hook for the onMutate/onError/onSettled pattern)
- The single query key strategy means every mutation triggers a full board refetch on settlement — acceptable for the single-board paradigm but would need refinement for multi-board or large datasets
- Temporary IDs (`temp-${Date.now()}`) used in optimistic creates could cause brief UI flicker when the server response replaces them

### Neutral
- TanStack React Query is already in the TanStack ecosystem alongside TanStack Router, maintaining consistency in the dependency tree
- The `@tanstack/react-query` package adds ~13KB gzipped to the frontend bundle

## Alternatives Considered

- **Redux Toolkit + RTK Query:** Rejected — introduces Redux as a global state container, which is heavyweight for an application where all state is server-owned. RTK Query provides similar data-fetching capabilities but requires significantly more boilerplate (slices, store setup, middleware).
- **Zustand:** Rejected — excellent for client-side state but lacks built-in server state management (fetching, caching, background refetching, cache invalidation). Would need to manually implement what React Query provides out of the box.
- **Plain React state (`useState` + `useEffect`):** Rejected — requires manual implementation of caching, deduplication, background refetching, loading/error states, and optimistic updates. Error-prone and produces significantly more code for the same result.
- **SWR:** Viable alternative with similar API, but TanStack React Query has richer mutation support (optimistic updates, cache manipulation) and aligns with the existing TanStack Router dependency.
