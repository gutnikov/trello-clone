# Product Requirements Document — Phase 1

## Trello Clone: Core Board Experience

---

| Field | Detail |
|---|---|
| **Version** | 1.0 |
| **Date** | March 23, 2026 |
| **Author** | Product Management |
| **Status** | Draft |
| **Target Release** | Sprint 1–3 (6 weeks) |

---

## 1. Overview

Phase 1 delivers the foundational Kanban board experience — the minimum product surface that feels genuinely usable. A single user can create a board, organize lists (columns), and manage cards within those lists. The defining interaction — drag-and-drop reordering — must be present from day one; without it the product has no identity.

### 1.1 Objectives

- Deliver a functional single-user Kanban board that can be used for personal task management.
- Establish the core data model (Board → List → Card) that all future phases build upon.
- Nail the drag-and-drop interaction so it feels fast, smooth, and reliable.
- Ship a deployable product that can be demo'd and tested with real users.

### 1.2 Success Metrics

| Metric | Target |
|---|---|
| User can complete a basic "create board → add 3 lists → add 5 cards → reorder" flow without errors | 100% of test sessions |

### 1.3 Scope

**In scope:** Board CRUD, List CRUD, Card CRUD, drag-and-drop (within list & across lists), basic card editing (title + description), responsive layout.

**Out of scope:** Authentication, multiple boards, labels, due dates, comments, attachments, collaboration, search.

---

## 2. User Stories

### 2.1 Board Management

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P1-01 | As a user, I want to create a new board with a title so I can start organizing my work. | 1. User can enter a board name and confirm creation. 2. Board renders immediately with an empty state prompt. 3. Title is editable inline after creation. | Must Have |
| P1-02 | As a user, I want to edit the board title so I can rename it as my project evolves. | 1. Clicking the title enters inline edit mode. 2. Pressing Enter or clicking away saves the change. 3. Pressing Escape reverts to the previous title. | Must Have |
| P1-03 | As a user, I want to delete a board so I can remove projects I no longer need. | 1. Delete action requires confirmation dialog. 2. All associated lists and cards are removed. 3. User is redirected to an empty/landing state. | Must Have |

### 2.2 List Management

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P1-04 | As a user, I want to add a new list to my board so I can define workflow stages (e.g., To Do, In Progress, Done). | 1. "Add a list" button is always visible at the end of the list row. 2. User types a title and confirms. 3. New list appears at the rightmost position. | Must Have |
| P1-05 | As a user, I want to rename a list so I can update my workflow stages. | 1. Clicking the list title enters inline edit mode. 2. Save on Enter/blur, cancel on Escape. | Must Have |
| P1-06 | As a user, I want to delete a list so I can remove stages I no longer need. | 1. Accessible via a list menu (⋯). 2. Confirmation dialog warns that all cards in the list will be deleted. 3. Remaining lists reflow without gaps. | Must Have |
| P1-07 | As a user, I want to reorder lists by dragging them horizontally so I can rearrange my workflow. | 1. Drag handle or header initiates horizontal drag. 2. Visual placeholder indicates drop position. 3. Order persists after page refresh. | Must Have |

### 2.3 Card Management

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P1-08 | As a user, I want to add a card to a list so I can capture a task or idea. | 1. "Add a card" button at the bottom of each list. 2. Quick-add: user types title and presses Enter. 3. Card appears at the bottom of the list. | Must Have |
| P1-09 | As a user, I want to edit a card's title and description so I can provide more detail. | 1. Clicking a card opens a detail view/modal. 2. Title is inline-editable. 3. Description supports plain text with basic markdown preview. 4. Changes auto-save or save on blur. | Must Have |
| P1-10 | As a user, I want to delete a card so I can remove tasks that are no longer relevant. | 1. Delete option available in card detail view and via card context menu. 2. Confirmation required. 3. List reflows smoothly. | Must Have |
| P1-11 | As a user, I want to drag a card within a list to reorder it so I can prioritize tasks. | 1. Dragging a card vertically within the same list reorders it. 2. Visual drop indicator shows target position. 3. New order persists on refresh. | Must Have |
| P1-12 | As a user, I want to drag a card from one list to another so I can move tasks across workflow stages. | 1. Card can be dragged from any list and dropped into any other list. 2. Card snaps into the position where it was dropped. 3. Source and target list card counts update. | Must Have |

---

## 3. Functional Requirements

### 3.1 Data Model

```
Board
├── id: UUID
├── title: string
├── created_at: timestamp
├── updated_at: timestamp
└── lists: List[]

List
├── id: UUID
├── board_id: FK → Board
├── title: string
├── position: float (fractional indexing for reorder without full re-index)
└── cards: Card[]

Card
├── id: UUID
├── list_id: FK → List
├── title: string
├── description: text (nullable)
├── position: float
├── created_at: timestamp
└── updated_at: timestamp
```

**Position strategy:** Use fractional indexing (e.g., midpoint between neighbors). This avoids rewriting every sibling's position on each drag. Periodic re-balancing job recommended.

### 3.2 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/boards` | Create board |
| GET | `/api/boards/:id` | Get board with all lists and cards |
| PATCH | `/api/boards/:id` | Update board title |
| DELETE | `/api/boards/:id` | Delete board (cascade) |
| POST | `/api/boards/:id/lists` | Create list |
| PATCH | `/api/lists/:id` | Update list (title, position) |
| DELETE | `/api/lists/:id` | Delete list (cascade) |
| POST | `/api/lists/:id/cards` | Create card |
| PATCH | `/api/cards/:id` | Update card (title, description, position, list_id) |
| DELETE | `/api/cards/:id` | Delete card |
| PATCH | `/api/cards/:id/move` | Move card (update list_id + position atomically) |

### 3.3 Drag-and-Drop Requirements

- Must support both pointer (mouse) and touch interactions.
- Visual feedback: dragged item shows elevated shadow; placeholder shows target slot.
- Optimistic UI update — reorder locally first, persist to API in background; rollback on failure.
- Horizontal scrolling of lists should auto-trigger when dragging near board edges.

---

---

## 4. UX & Design Notes

- **Board view** fills the viewport. Lists are arranged in a horizontal scrollable row.
- **Empty state** when a board has no lists: centered prompt — "Add your first list to get started."
- **Card quick-add** keeps the input open after adding, so users can rapidly add multiple cards.
- **Card detail modal** overlays the board (URL should update to `/board/:id/card/:cardId` for deep-linking readiness, even if routing is minimal in Phase 1).
- **List width** fixed at ~272px (matching Trello's pattern) to keep cards scannable.

---

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Drag-and-drop performance degrades with many cards | High | Virtualize long card lists; benchmark with 200+ cards early. |
| Fractional position values lose precision over time | Medium | Implement a background re-balancing job that normalizes positions periodically. |
| No auth means data is unprotected | Low (Phase 1 only) | Use browser-local or session-scoped data for demos; document this as a Phase 4 dependency. |

---

## 6. Dependencies & Assumptions

- No authentication exists — Phase 1 operates as a single-user local or session-scoped experience.
- The data model must be designed with multi-user in mind (user_id FK on Board) even if not enforced yet.
- Phase 2 (Card Detail & Richness) builds directly on the card modal established here.

---

## 7. Release Checklist

- [ ] Board CRUD fully functional
- [ ] List CRUD with horizontal drag reorder
- [ ] Card CRUD with vertical drag reorder within and across lists
- [ ] Card detail modal with title + description editing
- [ ] Optimistic drag-and-drop with API persistence
- [ ] Responsive layout tested on mobile viewports
- [ ] Keyboard accessibility for core flows
- [ ] API documented (OpenAPI spec)
