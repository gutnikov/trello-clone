# Feedback Loop Plan: TRE-40

## Overview

Verification strategy for the board route and read-only display components. This issue creates:
- `frontend/src/routes/board.tsx` — `/board` route using TanStack Router
- `frontend/src/components/Board.tsx` — Main board layout with horizontal scroll
- `frontend/src/components/BoardList.tsx` — List column with title and cards
- `frontend/src/components/BoardCard.tsx` — Card displaying title
- `frontend/src/components/EmptyBoard.tsx` — Empty state when no lists exist
- `frontend/src/styles.css` (modification) — Board layout styles

Tests verify that components export correctly, render the expected DOM structure, and the `/board` route is accessible.

---

## 1. Unit Tests — Component Exports (`frontend/tests/board-components.test.tsx`)

These tests verify that all board display components are exported as valid React components from their respective modules.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `Board is exported as a function component` | `Board.tsx` exports a default or named `Board` component |
| `BoardList is exported as a function component` | `BoardList.tsx` exports a default or named `BoardList` component |
| `BoardCard is exported as a function component` | `BoardCard.tsx` exports a default or named `BoardCard` component |
| `EmptyBoard is exported as a function component` | `EmptyBoard.tsx` exports a default or named `EmptyBoard` component |

### Run Command

```bash
cd frontend && pnpm vitest run tests/board-components.test.tsx
```

---

## 2. Unit Tests — Component Rendering (`frontend/tests/board-components.test.tsx`)

These tests verify the rendering behavior of each component using `@testing-library/react` with jsdom.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `Board renders board title` | Given board data with title "My Board", renders the title text |
| `Board renders lists horizontally in a scrollable container` | Given board data with lists, renders a container with `overflow-x: auto` or equivalent class |
| `Board renders BoardList for each list` | Given board data with 3 lists, renders 3 list columns |
| `BoardList renders list title` | Given a list with title "To Do", renders "To Do" text |
| `BoardList renders BoardCard for each card` | Given a list with 2 cards, renders 2 card elements |
| `BoardList renders cards ordered by position` | Given cards with positions [2, 0, 1], renders them in position order |
| `BoardCard renders card title` | Given a card with title "Fix bug", renders "Fix bug" text |
| `EmptyBoard renders empty state message` | When no lists exist, renders a prompt to create the first list |
| `EmptyBoard contains call-to-action text` | Renders text encouraging user to create a list |

### Run Command

```bash
cd frontend && pnpm vitest run tests/board-components.test.tsx
```

---

## 3. E2E Tests — Board Route (`frontend/e2e/board.spec.ts`)

These tests verify the `/board` route is accessible and renders board data correctly.

### Test Cases

| Test Name | Expected Behavior |
|---|---|
| `board page loads at /board` | Navigating to `/board` does not return a 404 |
| `board page displays board title` | The board title is visible on the page |
| `board page displays lists when board has lists` | List titles are visible on the board |
| `board page displays cards within lists` | Card titles are visible within their parent lists |
| `board page shows empty state when no lists exist` | When board has no lists, empty state message is shown |

### Run Command

```bash
cd frontend && pnpm e2e e2e/board.spec.ts
```

---

## 4. Non-Regression Tests

Verify existing tests still pass after adding new test files.

### Test Suites

| Suite | File | Expected |
|---|---|---|
| Smoke | `tests/smoke.test.ts` | 1 test passes |
| API Client | `tests/api.test.ts` | All tests pass |
| Board Store | `tests/board-store.test.ts` | All tests pass |

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
| Unit tests — component exports | 2 | 4 export verification tests for all components |
| Unit tests — component rendering | 2 | 9 rendering behavior tests covering all components |
| E2E tests — route accessibility | 2 | 5 tests covering route, board display, and empty state |
| Non-regression | 1 | Full existing test suite re-run |
| Static analysis | 1 | Biome linting on all new/modified files |

**Total feedback_completeness_score: 8/10**

The score of 8 exceeds the minimum threshold of 6. This is a UI layer with visual components, so E2E tests are included.
