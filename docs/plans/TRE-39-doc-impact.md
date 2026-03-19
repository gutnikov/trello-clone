# Doc Impact Analysis: TRE-39

## Overview

TRE-39 introduces the frontend data layer — an API client module (`frontend/src/lib/api.ts`) and a React Query state management layer (`frontend/src/lib/board-store.ts`). This is the first frontend state management code in the project, adding TanStack React Query as a dependency with optimistic updates for all CRUD operations.

---

## Impacted Documents

### 1. `docs/architecture/adr-002-tanstack-query-state-management.md` — New ADR

- **Impact:** HIGH — New ADR required
- **Reason:** TRE-39 introduces the first client-side state management approach. The choice of TanStack React Query over alternatives (Redux, Zustand, plain useState) is an architectural decision that future agents need to understand and follow.
- **Action:** Create ADR-002 documenting:
  - Decision to use TanStack React Query for server state management
  - Single `["board"]` query key strategy (single-board paradigm)
  - Optimistic update pattern (onMutate → cancel → snapshot → rollback on error → invalidate on settle)
  - API client as a separate module from the React Query hooks

### 2. `docs/agents/implementation.md` — Frontend Data Layer Pattern

- **Impact:** HIGH — Update required
- **Reason:** The implementation agent context doc has no frontend data layer documentation. With `api.ts` and `board-store.ts` as the canonical patterns, future agents building UI components need to know how to use these hooks and how to add new mutations.
- **Action:** Add a "Frontend Data Layer" section documenting:
  - API client structure (`frontend/src/lib/api.ts`): typed functions, error handling, request/response types
  - Board store structure (`frontend/src/lib/board-store.ts`): query hook, mutation hooks, optimistic update pattern
  - How to add a new mutation hook following the existing pattern
  - The `@tanstack/react-query` dependency and QueryClient setup

### 3. `README.md` — Tech Stack Update

- **Impact:** LOW — Minor update
- **Reason:** The tech stack table lists Frontend as "Astro, React, TypeScript" but does not mention TanStack React Query, which is now a core frontend dependency for state management.
- **Action:** Add TanStack React Query to the Frontend row in the tech stack table.

### 4. `docs/agents/design-feedback-loop.md` — Frontend API Test Patterns

- **Impact:** LOW — Minor update
- **Reason:** TRE-39 adds the first frontend API client tests (`frontend/tests/api.test.ts`) using vitest with fetch mocking. The design feedback loop agent doc should reference this as the canonical pattern for future frontend API test scaffolds.
- **Action:** Add a note under the "Unit Tests (Frontend)" section referencing `frontend/tests/api.test.ts` as the canonical frontend API test pattern.

---

## Documents NOT Impacted

| Document | Reason |
|---|---|
| `CLAUDE.md` | No structural changes to the project map; `frontend/src/lib/` is under the existing `frontend/` structure |
| `docs/conventions/golden-principles.md` | No new conventions introduced |
| `docs/guides/workflow-customization.md` | Orca workflow unchanged |
| `docs/agents/scoping.md` | Scoping process unchanged |
| `docs/agents/planning.md` | Planning process unchanged |
| `docs/agents/validation.md` | Validation process unchanged |
| `docs/agents/docs-update.md` | Docs process unchanged |
| `docs/runbooks/deploy-prod.md` | No operational changes — frontend build process unchanged |

---

## Summary

| Document | Impact Level | Action |
|---|---|---|
| `docs/architecture/adr-002-tanstack-query-state-management.md` | High | **Create** — new ADR for frontend state management decision |
| `docs/agents/implementation.md` | High | **Update** — add frontend data layer pattern documentation |
| `README.md` | Low | **Update** — add TanStack React Query to tech stack |
| `docs/agents/design-feedback-loop.md` | Low | **Update** — reference frontend API test pattern |
