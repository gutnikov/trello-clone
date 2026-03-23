# Product Requirements Document — Phase 5

## Trello Clone: Search, Filter & Polish

---

| Field | Detail |
|---|---|
| **Version** | 1.0 |
| **Date** | March 23, 2026 |
| **Author** | Product Management |
| **Status** | Draft |
| **Target Release** | Sprint 14–17 (8 weeks) |
| **Dependency** | Phase 4 (Collaboration & Users) complete |

---

## 1. Overview

Phase 5 is about making the product usable at scale. As users accumulate dozens of boards, hundreds of cards, and multiple collaborators, they need powerful ways to find things (search), narrow their view (filter), move faster (keyboard shortcuts), and stay informed (notifications). This phase polishes the product into something that feels professional and production-ready.

### 1.1 Objectives

- Deliver a global search experience that finds cards, boards, and comments across the entire workspace.
- Provide per-board filtering so users can focus on what matters (their cards, overdue items, specific labels).
- Implement keyboard shortcuts for power users to operate the board without a mouse.
- Build a notification system (in-app and email) so users never miss important updates.
- Add board-level settings and permission controls to round out the admin experience.

### 1.2 Success Metrics

| Metric | Target |
|---|---|
| Users who use board filters at least once per week | ≥ 40% of active users |
| Keyboard shortcut adoption (at least one shortcut used) | ≥ 20% of active users within 1 month |
| Notification click-through rate (in-app) | ≥ 30% |
| Email notification open rate | ≥ 25% |

### 1.3 Scope

**In scope:** Global search (cards, boards, comments), board-level card filtering (by label, member, due date), keyboard shortcuts, in-app notification center, email notifications (configurable), board settings panel, member permission refinements (Admin, Member, Observer roles).

**Out of scope:** Saved/pinned filters, advanced query syntax (e.g., `label:red AND due:week`), push notifications (mobile), audit logs (Phase 7), custom fields (Phase 6).

---

## 2. User Stories

### 2.1 Global Search

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P5-01 | As a user, I want to search across all my boards to find a specific card, board, or comment. | 1. Search icon/bar accessible from the top navigation (visible on all pages). 2. Results grouped by type: Boards, Cards, Comments. 3. Card results show title, parent board, parent list, and matching text snippet. 4. Board results show title and background thumbnail. 5. Comment results show snippet, parent card title, and author. | Must Have |
| P5-02 | As a user, I want search results to appear as I type so I can find things quickly. | 1. Results begin appearing after 2+ characters typed. 2. Debounced (300ms) to avoid excessive API calls. 3. Results update incrementally as query changes. 4. "No results found" message when empty. | Must Have |
| P5-03 | As a user, I want to click a search result and navigate directly to it. | 1. Clicking a board result navigates to the board. 2. Clicking a card result navigates to the board with the card detail modal open. 3. Clicking a comment result navigates to the card containing the comment. 4. Search closes on navigation. | Must Have |
| P5-04 | As a user, I want recent searches remembered so I can quickly re-run them. | 1. Last 5 search queries stored locally. 2. Shown as suggestions when the search bar is focused with no input. 3. Clearable individually or all at once. | Should Have |

### 2.2 Board-Level Filtering

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P5-05 | As a user, I want to filter cards on the current board by label so I can focus on a specific category. | 1. Filter bar below the board header with a "Labels" dropdown. 2. Multi-select: choose one or more labels. 3. Non-matching cards are dimmed (reduced opacity) rather than hidden, to preserve spatial context. 4. Clearing the filter restores all cards. | Must Have |
| P5-06 | As a user, I want to filter cards by assigned member so I can see only my tasks or a specific colleague's tasks. | 1. "Members" dropdown in the filter bar. 2. Multi-select. 3. Includes a "No members" option to find unassigned cards. 4. "Cards assigned to me" is a one-click shortcut. | Must Have |
| P5-07 | As a user, I want to filter cards by due date status so I can focus on urgent work. | 1. "Due Date" dropdown with options: Overdue, Due in the next day, Due in the next week, No due date. 2. Multi-select. 3. Combinable with label and member filters (AND logic between filter types). | Must Have |
| P5-08 | As a user, I want to combine multiple filters (label + member + due date) to narrow my view precisely. | 1. All active filters shown as removable chips in the filter bar. 2. Logic: AND between filter types (e.g., label:Red AND member:Alice), OR within a filter type (e.g., label:Red OR label:Blue). 3. Card count shown: "Showing X of Y cards." | Must Have |
| P5-09 | As a user, I want to clear all filters with one click. | 1. "Clear Filters" button visible when any filter is active. 2. Resets all filter dropdowns and restores full board view. | Must Have |

### 2.3 Keyboard Shortcuts

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P5-10 | As a power user, I want keyboard shortcuts for common actions so I can work faster. | 1. Shortcuts work when no text input is focused. 2. Shortcut overlay accessible via `?` key. 3. See shortcut map below. | Must Have |
| P5-11 | As a user, I want to see a keyboard shortcut reference so I can learn the available shortcuts. | 1. `?` opens a modal listing all shortcuts grouped by category. 2. Modal closable via Escape or clicking outside. | Must Have |

**Keyboard Shortcut Map:**

| Shortcut | Action |
|---|---|
| `N` | Create new card (focuses the quick-add input on the first list) |
| `B` | Open board switcher (search across boards) |
| `/` | Focus global search |
| `F` | Open filter menu |
| `Q` | Toggle "show only my cards" filter |
| `D` | Open due date picker on focused card |
| `L` | Open label picker on focused card |
| `M` | Open member picker on focused card |
| `E` | Quick edit card title (on hover/focus) |
| `Enter` | Open card detail (on focused card) |
| `Escape` | Close any open modal or panel |
| `←` `→` | Navigate between lists |
| `↑` `↓` | Navigate between cards within a list |
| `Space` | Toggle self-assignment on focused card |
| `C` | Archive focused card |
| `?` | Show shortcuts reference |

### 2.4 Notifications

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P5-12 | As a user, I want to receive in-app notifications when relevant events happen on boards I'm a member of. | 1. Bell icon in top navigation with unread count badge. 2. Notification panel opens as a dropdown or drawer. 3. Notifications grouped by board. 4. Each notification is clickable and navigates to the relevant card/board. | Must Have |
| P5-13 | As a user, I want to be notified when someone assigns me to a card, mentions me in a comment, or a card I'm on is moved or has a due date approaching. | Triggering events: 1. Assigned to a card. 2. Comment added to a card I'm assigned to. 3. Card I'm assigned to is moved to a different list. 4. Due date within 24 hours on a card I'm assigned to. 5. Due date passed (overdue) on a card I'm assigned to. 6. Invited to a board. | Must Have |
| P5-14 | As a user, I want to receive email notifications for important events so I stay informed even when not in the app. | 1. Email sent for the same triggering events as in-app notifications. 2. Emails are batched (digest every 15 minutes) to avoid spam. 3. Each email includes a direct link to the relevant card. | Should Have |
| P5-15 | As a user, I want to configure my notification preferences so I only receive what I care about. | 1. Settings page with toggles per notification type (per channel: in-app, email). 2. "Mute board" option to suppress all notifications from a specific board. 3. Default: all notifications on. | Should Have |
| P5-16 | As a user, I want to mark notifications as read individually or all at once. | 1. "Mark as read" on individual notifications. 2. "Mark all as read" button at the top of the notification panel. 3. Read notifications are visually distinct (dimmed). | Must Have |

### 2.5 Board Settings & Permissions

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P5-17 | As a board admin, I want a dedicated board settings panel to manage board properties and permissions. | 1. Settings accessible from board menu (⋯ in header). 2. Sections: General (title, description, background), Members, Permissions, Danger Zone (archive, delete). | Must Have |
| P5-18 | As a board admin, I want to add an Observer role so stakeholders can view a board without editing. | 1. Observer role: can view board, cards, comments. Cannot create, edit, move, or delete any content. 2. Assignable in member management. 3. Observer sees a "View Only" badge on the board. | Should Have |
| P5-19 | As a board admin, I want to control whether Members can invite other people to the board. | 1. Toggle in board settings: "Allow members to invite" (default: on). 2. When off, only admins see the Invite button. | Should Have |
| P5-20 | As a board admin, I want to add a board description so members understand the board's purpose. | 1. Description field in board settings (plain text, max 500 characters). 2. Description visible in an info tooltip or expandable section on the board header. | Should Have |

---

## 3. Functional Requirements

### 3.1 Search Architecture

**Approach:** Full-text search across cards, boards, and comments. Search results are weighted by relevance (titles weighted higher than body content).

```
Search Index Fields:
- Cards: title, description (weighted: title higher, description lower)
- Boards: title (weighted high)
- Comments: body (weighted lower), with parent card title for context
```

- **API**: `GET /api/search?q=<query>&type=<boards|cards|comments|all>`
- **Results**: Return max 20 results per type, sorted by relevance.
- **Access control**: Results filtered to boards the requesting user is a member of.

### 3.2 Data Model Extensions

```
Notification
├── id: UUID
├── user_id: FK → User (recipient)
├── type: enum (assigned_to_card, comment_added, card_moved, due_date_approaching, due_date_overdue, board_invitation)
├── board_id: FK → Board
├── card_id: FK → Card (nullable)
├── actor_id: FK → User (who triggered it)
├── data: jsonb (contextual details)
├── is_read: boolean (default false)
├── created_at: timestamp

NotificationPreference
├── user_id: FK → User
├── type: enum (matches Notification.type)
├── in_app: boolean (default true)
├── email: boolean (default true)

Board (extended)
├── description: text (nullable, max 500)
├── allow_member_invite: boolean (default true)

BoardMember (extended)
├── role: enum (admin, member, observer)  -- observer added
```

### 3.3 API Endpoints (New)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/search` | Global search (query param: q, type) |
| GET | `/api/notifications` | List notifications (paginated, filterable) |
| PATCH | `/api/notifications/:id/read` | Mark notification as read |
| POST | `/api/notifications/read-all` | Mark all as read |
| GET | `/api/users/me/notification-preferences` | Get preferences |
| PATCH | `/api/users/me/notification-preferences` | Update preferences |
| PATCH | `/api/boards/:id/settings` | Update board settings (description, permissions) |

### 3.4 Notification Delivery Pipeline

1. **Event occurs** (e.g., card assigned) → application publishes event to internal message bus.
2. **Notification service** consumes event, determines recipients (card members, board members based on event type), checks user preferences.
3. **In-app**: Notification record created in database; pushed via existing WebSocket channel to online users.
4. **Email**: Event queued in email buffer. Buffer flushes every 15 minutes as a digest email (or immediately for high-priority events like board invitations).
5. **Email service**: Transactional email provider.

### 3.5 Filter Implementation

- Filters are client-side only (no API call needed). Cards are already loaded with the board.
- Filter state stored in URL query params for shareability: `/board/:id?label=red,blue&member=userId&due=overdue`.
- Non-matching cards dimmed to 30% opacity (not removed from DOM) to preserve board layout context.

---

---

## 4. UX & Design Notes

- **Global search**: Command-palette style overlay (similar to Cmd+K in modern apps). Appears centered, above the board. Results grouped with section headers.
- **Filter bar**: Horizontal bar between board header and lists. Compact by default (icon buttons), expands to show active filter chips. Subtle background color change when filters are active.
- **Notification panel**: Right-aligned dropdown (max 400px wide, max 500px tall, scrollable). Each notification: avatar + description + relative timestamp + unread dot.
- **Keyboard shortcuts modal**: Two-column grid, shortcuts on the left, descriptions on the right. Grouped by category (Navigation, Cards, Board).
- **Board settings**: Full-page drawer from the right. Tab navigation: General, Members, Permissions.
- **Dimmed cards**: Filtered-out cards show at 30% opacity with no pointer events (not clickable). A tooltip on hover says "Hidden by filter."

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Full-text search performance degrades at scale | High | Monitor query times; plan migration to a dedicated search engine if needed. |
| Notification spam overwhelms users | Medium | Default to 15-minute email digest; provide granular per-type and per-board mute controls. |
| Keyboard shortcuts conflict with browser or assistive technology | Medium | Test against screen readers; use only single-key shortcuts (no Ctrl/Cmd combos); disable when input focused. |
| Filter-by-URL enables leaking board structure via shared links | Low | Filters only affect the current user's view; filter params are ignored if the user doesn't have board access. |
| Email deliverability issues | Medium | Use reputable transactional email provider; authenticate domain; monitor bounce rates. |

---

## 6. Release Checklist

- [ ] Global search (cards, boards, comments) with instant results
- [ ] Search results navigation (click-to-navigate)
- [ ] Recent searches (local storage)
- [ ] Board-level filter: by label (multi-select)
- [ ] Board-level filter: by member (multi-select + "assigned to me" shortcut)
- [ ] Board-level filter: by due date status (overdue, upcoming, no date)
- [ ] Combined filters with AND/OR logic and chip display
- [ ] Filter state reflected in URL query params
- [ ] Non-matching cards dimmed (not hidden)
- [ ] Full keyboard shortcut map implemented
- [ ] Keyboard shortcut reference modal (`?`)
- [ ] In-app notification center with unread badge
- [ ] All notification trigger events wired up
- [ ] Notification click-to-navigate
- [ ] Mark as read (individual + bulk)
- [ ] Email notification digest (15-minute batching)
- [ ] Notification preference settings (per type, per channel)
- [ ] Board mute option
- [ ] Board settings panel (description, background, permissions)
- [ ] Observer role implemented and enforced
- [ ] "Allow members to invite" toggle
- [ ] Search index setup
- [ ] Email domain authentication
- [ ] Accessibility audit: notifications, filters, shortcuts
