# Product Requirements Document — Phase 3

## Trello Clone: Multi-Board & Navigation

---

| Field | Detail |
|---|---|
| **Version** | 1.0 |
| **Date** | March 23, 2026 |
| **Author** | Product Management |
| **Status** | Draft |
| **Target Release** | Sprint 7–9 (6 weeks) |
| **Dependency** | Phase 2 (Card Detail & Richness) complete |

---

## 1. Overview

Phase 3 expands the product from a single-board tool into a multi-board workspace. Users can create and manage multiple boards, navigate between them via a home dashboard and sidebar, personalize boards with backgrounds and favorites, and archive items they no longer need. This phase transforms the product from "a board" into "a workspace."

### 1.1 Objectives

- Enable users to manage multiple projects simultaneously within a single application.
- Provide clear, intuitive navigation between boards via a home view and persistent sidebar.
- Introduce board personalization (backgrounds, colors) to help users visually distinguish projects.
- Add archive/restore flows as a non-destructive alternative to permanent deletion.

### 1.2 Success Metrics

| Metric | Target |
|---|---|
| Average boards per active user (after 2 weeks) | ≥ 3 |
| Navigation from home to board | < 2 clicks |
| Users who star at least one board | ≥ 60% |
| Archive used instead of delete | ≥ 40% of removal actions |

### 1.3 Scope

**In scope:** Home dashboard, board list/grid view, sidebar navigation, board backgrounds (solid colors + image presets), board starring/favorites, board archiving and restoring, list archiving and restoring, card archiving and restoring, recently viewed boards.

**Out of scope:** Authentication (Phase 4), workspaces/teams (Phase 7), board templates (Phase 6), search (Phase 5).

---

## 2. User Stories

### 2.1 Home Dashboard

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P3-01 | As a user, I want a home page that shows all my boards so I can quickly find and access any project. | 1. Home view displays all boards as cards in a grid layout. 2. Each card shows the board title and background color/image. 3. Card count or last-updated timestamp shown per board. | Must Have |
| P3-02 | As a user, I want to create a new board directly from the home page. | 1. "Create new board" card is always visible in the grid. 2. Clicking it opens a creation dialog with title input and background selector. 3. New board appears in the grid immediately after creation. | Must Have |
| P3-03 | As a user, I want to see my starred boards in a separate section at the top of the home page so I can quickly access favorites. | 1. "Starred Boards" section appears above "All Boards" when at least one board is starred. 2. Section collapses if empty. 3. Order within the section is user-defined (drag to reorder). | Must Have |
| P3-04 | As a user, I want to see recently viewed boards so I can resume work quickly. | 1. "Recently Viewed" section shows last 5 boards visited, ordered by recency. 2. Updated automatically on board open. | Should Have |

### 2.2 Sidebar Navigation

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P3-05 | As a user, I want a persistent sidebar that lets me navigate between boards without returning to the home page. | 1. Sidebar visible on board view, collapsible via toggle. 2. Lists starred boards at the top, then all boards alphabetically. 3. Clicking a board name navigates to it. | Must Have |
| P3-06 | As a user, I want the sidebar to show which board I'm currently viewing. | 1. Active board is highlighted in the sidebar. 2. Visual indicator (bold text or colored bar). | Must Have |
| P3-07 | As a user, I want to collapse and expand the sidebar so I can maximize board space when needed. | 1. Toggle button (hamburger or chevron) at the top of the sidebar. 2. Collapsed state persists across navigation. 3. On mobile, sidebar is off-canvas and slides in/out. | Must Have |

### 2.3 Board Personalization

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P3-08 | As a user, I want to set a background color for my board so I can visually distinguish projects. | 1. Palette of 9 solid background colors available in board settings. 2. Background fills the entire board area behind lists. 3. List and card colors remain readable against all backgrounds. | Must Have |
| P3-09 | As a user, I want to choose from preset background images for my board. | 1. Library of 6–10 curated background images. 2. Image covers the board area (CSS cover). 3. Semi-transparent overlay on the image to ensure list readability. | Should Have |
| P3-10 | As a user, I want to star/unstar a board to mark it as a favorite. | 1. Star icon on board header and on board card (home view). 2. Toggling updates starred section on home page and sidebar in real time. | Must Have |

### 2.4 Archiving & Restoring

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P3-11 | As a user, I want to archive a card instead of deleting it so I can restore it later if needed. | 1. "Archive" option in card detail and card context menu. 2. Archived cards are removed from the board view but not deleted. 3. Archived cards accessible via a board-level "Archived Items" panel. | Must Have |
| P3-12 | As a user, I want to restore an archived card to its original list (or choose a different list). | 1. "Restore" button in the archived items panel. 2. Card returns to the bottom of its original list (or user selects a list if the original was deleted). | Must Have |
| P3-13 | As a user, I want to archive a list so I can remove it from view without losing its cards. | 1. "Archive this list" option in list menu. 2. All cards within the list are archived with it. 3. Archived list appears in the archived items panel. | Must Have |
| P3-14 | As a user, I want to restore an archived list with all its cards. | 1. Restoring a list restores all its cards in their original order. 2. List appears at the rightmost position on the board. | Must Have |
| P3-15 | As a user, I want to archive a board so I can declutter my home page without losing data. | 1. "Archive Board" in board settings. 2. Board disappears from home and sidebar. 3. Accessible via "View Archived Boards" link on home page. | Must Have |
| P3-16 | As a user, I want to restore or permanently delete an archived board. | 1. Archived boards panel on home page. 2. "Restore" brings board back to home. 3. "Delete Permanently" requires confirmation and cascades all data. | Must Have |
| P3-17 | As a user, I want to permanently delete an archived card or list. | 1. "Delete" option in the archived items panel (not available on active items directly). 2. Confirmation dialog. 3. Permanent and irreversible. | Should Have |

---

## 3. Functional Requirements

### 3.1 Data Model Extensions

```
Board (extended)
├── background_type: enum (color, image)
├── background_value: string (hex color or image key/URL)
├── is_starred: boolean (default false)
├── starred_position: float (nullable, for ordering starred boards)
├── is_archived: boolean (default false)
├── archived_at: timestamp (nullable)
├── last_viewed_at: timestamp

Card (extended)
├── is_archived: boolean (default false)
├── archived_at: timestamp (nullable)

List (extended)
├── is_archived: boolean (default false)
├── archived_at: timestamp (nullable)
```

### 3.2 API Endpoints (New & Modified)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/boards` | List all boards (with filters: starred, archived, recent) |
| PATCH | `/api/boards/:id` | Extended: background, is_starred, starred_position, is_archived |
| GET | `/api/boards/:id/archive` | List archived cards and lists for a board |
| PATCH | `/api/cards/:id/archive` | Archive a card |
| PATCH | `/api/cards/:id/restore` | Restore an archived card |
| PATCH | `/api/lists/:id/archive` | Archive a list (cascades to cards) |
| PATCH | `/api/lists/:id/restore` | Restore a list (cascades to cards) |

### 3.3 Routing

| Route | View |
|---|---|
| `/` | Home dashboard |
| `/board/:id` | Board view |
| `/board/:id/card/:cardId` | Board view with card detail modal open |
| `/archived` | Archived boards list |

### 3.4 Background Images

- Ship 8–10 curated, royalty-free images (compressed JPEG, max 500 KB each).
- Serve via CDN with aggressive caching.
- Apply an overlay on images to maintain text readability.
- Board header text switches to white on dark backgrounds, dark on light backgrounds (calculate contrast ratio).

---

---

## 4. UX & Design Notes

- **Home dashboard grid**: 3–4 columns on desktop, 2 on tablet, 1 on mobile. Board cards have a 16:9 aspect ratio showing background + title.
- **Sidebar width**: ~260px expanded, ~48px collapsed (showing only icons).
- **Board background**: when using a solid color, lists appear on a slightly lighter/darker tint. When using an image, lists have a subtle `backdrop-filter: blur(4px)` or white semi-transparent background.
- **Archived items panel**: slides in from the right edge of the board (drawer pattern). Shows cards and lists in separate tabs.
- **Transition animations**: board-to-board navigation uses a subtle fade. Sidebar toggle uses a slide animation.

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Too many boards make the home page overwhelming | Medium | Default sort by recent activity; provide a search/filter mechanism (delivered in Phase 5). |
| Background images increase page weight | Low | Compress aggressively, lazy-load on home grid, preload only on hover. |
| Archive model complicates queries | Medium | Add database index on is_archived; ensure all list/card queries filter by default. |
| No auth — "all boards" belongs to no one | Low | Scope to session/local storage for now; document Phase 4 dependency. |

---

## 6. Release Checklist

- [ ] Home dashboard with board grid (starred, recent, all sections)
- [ ] Board creation from home page with background picker
- [ ] Sidebar navigation with active board highlight and collapse toggle
- [ ] 9 solid background colors functional
- [ ] 8–10 preset background images with readability overlay
- [ ] Board starring with persistent ordering
- [ ] Recently viewed tracking (auto-updated)
- [ ] Card archive and restore
- [ ] List archive and restore (with card cascade)
- [ ] Board archive, restore, and permanent delete
- [ ] Archived items panel on board view
- [ ] Archived boards panel on home page
- [ ] Routing: `/`, `/board/:id`, `/board/:id/card/:cardId`, `/archived`
- [ ] Mobile-responsive sidebar and home grid
