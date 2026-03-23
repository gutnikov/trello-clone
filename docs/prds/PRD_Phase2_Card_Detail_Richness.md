# Product Requirements Document — Phase 2

## Trello Clone: Card Detail & Richness

---

| Field | Detail |
|---|---|
| **Version** | 1.0 |
| **Date** | March 23, 2026 |
| **Author** | Product Management |
| **Status** | Draft |
| **Target Release** | Sprint 4–6 (6 weeks) |
| **Dependency** | Phase 1 (Core Board Experience) complete |

---

## 1. Overview

Phase 2 transforms the card from a simple title/description sticky note into a rich, actionable task object. Labels, due dates, checklists, comments, and file attachments turn the board into a lightweight project tracker. The card detail modal — established in Phase 1 — becomes the primary workspace for this phase.

### 1.1 Objectives

- Make each card a self-contained unit of work with enough metadata to replace a simple task tracker.
- Introduce visual scanning aids (labels, due-date badges) on the board view so users can assess status at a glance.
- Lay the groundwork for collaboration (comments, activity) even before multi-user auth exists in Phase 4.

### 1.2 Success Metrics

| Metric | Target |
|---|---|
| Average metadata fields used per card (labels, due date, checklist) | ≥ 1.5 after 1 week of use |
| Checklist completion drives card movement (cards with 100% checklist move to "Done") | Trackable correlation |

### 1.3 Scope

**In scope:** Labels (create, assign, color), due dates (set, display, overdue indicator), checklists (add, check/uncheck, progress bar), comments (add, edit, delete), file attachments (upload, preview, delete), card cover image, activity log per card.

**Out of scope:** Assignees/members (Phase 4), notifications (Phase 5), custom fields (Phase 6), recurring due dates.

---

## 2. User Stories

### 2.1 Labels

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P2-01 | As a user, I want to create labels with a name and color so I can categorize cards by type, priority, or any custom dimension. | 1. Label manager accessible from card detail sidebar. 2. Predefined palette of 10 colors. 3. Label name is optional (color-only labels are valid). 4. Labels are board-scoped (shared across all cards on a board). | Must Have |
| P2-02 | As a user, I want to assign one or more labels to a card so I can visually tag it. | 1. Labels selectable via checkbox list in card detail. 2. Assigned labels appear as colored chips on the card front (board view). 3. Clicking a chip on the board opens the label picker. | Must Have |
| P2-03 | As a user, I want to edit or delete a label so I can refine my categorization over time. | 1. Editing a label updates it everywhere it's assigned. 2. Deleting a label removes it from all cards with confirmation. | Must Have |
| P2-04 | As a user, I want to toggle between showing label names and showing color-only chips on the board so I can save space. | 1. Clicking any label chip on the board toggles all labels between expanded (name + color) and compact (color-only). 2. Preference persists per session. | Should Have |

### 2.2 Due Dates

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P2-05 | As a user, I want to set a due date on a card so I can track deadlines. | 1. Date picker accessible from card detail sidebar. 2. Optional time component (defaults to end of day). 3. Due date badge appears on card front. | Must Have |
| P2-06 | As a user, I want to see visual indicators when a card is due soon or overdue. | 1. Due within 24 hours: yellow badge. 2. Overdue: red badge. 3. Completed (manually marked): green badge with strikethrough. 4. Badge colors update in real-time without refresh. | Must Have |
| P2-07 | As a user, I want to mark a due date as complete without moving the card so I can track deadline adherence separately from workflow stage. | 1. Checkbox on the due date badge (both board view and card detail). 2. Toggling complete/incomplete updates badge color immediately. | Should Have |
| P2-08 | As a user, I want to remove a due date from a card. | 1. "Remove" option in the date picker. 2. Badge disappears from card front. | Must Have |

### 2.3 Checklists

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P2-09 | As a user, I want to add one or more named checklists to a card so I can break work into subtasks. | 1. "Add Checklist" button in card detail. 2. Each checklist has an editable title (default: "Checklist"). 3. Multiple checklists per card supported. | Must Have |
| P2-10 | As a user, I want to add, check/uncheck, rename, and delete checklist items. | 1. Items added via text input at the bottom of the checklist. 2. Checkbox toggles complete state. 3. Completed items show strikethrough. 4. Items can be renamed inline and deleted via context menu. | Must Have |
| P2-11 | As a user, I want to see a progress bar on the card front showing checklist completion. | 1. Progress bar shows percentage and fraction (e.g., "3/5"). 2. Bar fills with a green gradient. 3. Multiple checklists aggregate into one bar on the card front. | Must Have |
| P2-12 | As a user, I want to reorder checklist items by dragging so I can prioritize subtasks. | 1. Drag handle on each item. 2. Items reorderable within a checklist. 3. Moving items between checklists is not required in this phase. | Should Have |
| P2-13 | As a user, I want to delete an entire checklist from a card. | 1. Delete action on the checklist header. 2. Confirmation dialog. 3. All items removed. | Must Have |

### 2.4 Comments & Activity

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P2-14 | As a user, I want to add a comment to a card so I can capture notes, decisions, or context. | 1. Comment input at the bottom of the card detail. 2. Supports plain text (markdown rendering deferred to future phase). 3. Comments display author name (placeholder "You" until auth exists) and timestamp. | Must Have |
| P2-15 | As a user, I want to edit or delete my comments. | 1. Edit and Delete options on each comment (only for comments by current session). 2. Edited comments show "(edited)" indicator. | Must Have |
| P2-16 | As a user, I want to see an activity log on each card showing what changed and when. | 1. Activity section below comments. 2. Tracks: card created, card moved (list change), label added/removed, due date set/changed/removed, checklist item completed, attachment added/removed. 3. Entries show timestamp and description. | Should Have |

### 2.5 Attachments

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P2-17 | As a user, I want to upload file attachments to a card so I can keep relevant documents with the task. | 1. Upload via file picker or drag-and-drop onto card detail. 2. Accepted file types: images (png, jpg, gif, webp), PDFs, documents (docx, xlsx, pptx), and text files. 3. Max file size: 10 MB. 4. Upload progress indicator shown. | Must Have |
| P2-18 | As a user, I want to preview image attachments inline and download any attachment. | 1. Image attachments show a thumbnail preview in the card detail. 2. All attachments have a download link. 3. PDF and document files show an icon + filename. | Must Have |
| P2-19 | As a user, I want to set an image attachment as the card cover so I can visually distinguish cards on the board. | 1. "Make Cover" option on image attachments. 2. Cover image displays above the card title on the board view. 3. Covers can be removed. | Should Have |
| P2-20 | As a user, I want to delete an attachment from a card. | 1. Delete option per attachment. 2. Confirmation dialog. 3. File removed from storage. | Must Have |

---

## 3. Functional Requirements

### 3.1 Data Model Extensions

```
Label
├── id: UUID
├── board_id: FK → Board
├── name: string (nullable)
├── color: string (hex, from predefined palette)

CardLabel (join table)
├── card_id: FK → Card
├── label_id: FK → Label

Card (extended)
├── due_date: timestamp (nullable)
├── due_complete: boolean (default false)
├── cover_image_url: string (nullable)

Checklist
├── id: UUID
├── card_id: FK → Card
├── title: string
├── position: float

ChecklistItem
├── id: UUID
├── checklist_id: FK → Checklist
├── text: string
├── is_checked: boolean
├── position: float

Comment
├── id: UUID
├── card_id: FK → Card
├── author_name: string (placeholder until auth)
├── body: text
├── created_at: timestamp
├── updated_at: timestamp

Attachment
├── id: UUID
├── card_id: FK → Card
├── filename: string
├── file_url: string
├── file_type: string (MIME)
├── file_size: integer (bytes)
├── created_at: timestamp

Activity
├── id: UUID
├── card_id: FK → Card
├── action: enum (created, moved, label_added, label_removed, due_date_set, due_date_removed, checklist_completed, attachment_added, attachment_removed)
├── detail: jsonb (contextual data)
├── created_at: timestamp
```

### 3.2 API Endpoints (New)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/boards/:id/labels` | List all labels for a board |
| POST | `/api/boards/:id/labels` | Create label |
| PATCH | `/api/labels/:id` | Update label |
| DELETE | `/api/labels/:id` | Delete label |
| POST | `/api/cards/:id/labels` | Assign label to card |
| DELETE | `/api/cards/:id/labels/:labelId` | Remove label from card |
| POST | `/api/cards/:id/checklists` | Create checklist |
| PATCH | `/api/checklists/:id` | Update checklist (title, position) |
| DELETE | `/api/checklists/:id` | Delete checklist |
| POST | `/api/checklists/:id/items` | Add checklist item |
| PATCH | `/api/checklist-items/:id` | Update item (text, is_checked, position) |
| DELETE | `/api/checklist-items/:id` | Delete item |
| GET | `/api/cards/:id/comments` | List comments |
| POST | `/api/cards/:id/comments` | Add comment |
| PATCH | `/api/comments/:id` | Edit comment |
| DELETE | `/api/comments/:id` | Delete comment |
| POST | `/api/cards/:id/attachments` | Upload attachment (multipart) |
| DELETE | `/api/attachments/:id` | Delete attachment |
| GET | `/api/cards/:id/activity` | Get activity log |

### 3.3 File Storage

- Use object storage (S3-compatible) for attachments.
- Generate pre-signed URLs for downloads (expiry: 1 hour).
- Thumbnails for images generated server-side on upload (max 300px wide).
- Enforce 10 MB per-file limit at both client and server.

---

---

## 4. UX & Design Notes

- **Card detail modal layout:** Left column (wide): title, description, checklists, comments, activity. Right sidebar (narrow): labels, due date, attachments, actions (Move, Copy, Delete).
- **Label colors** (predefined palette): green, yellow, orange, red, purple, blue, sky, lime, pink, black.
- **Due date badge** on card front: compact format, e.g., "Mar 25" or "Tomorrow". Color indicates status.
- **Checklist progress bar** on card front only appears when at least one checklist exists.
- **Activity log** is collapsed by default with a "Show Activity" toggle to avoid overwhelming the detail view.
- **Attachment drag-and-drop zone** highlights the entire card detail area when a file is dragged over the browser window.

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Large file uploads fail on slow connections | Medium | Implement resumable/chunked uploads; show progress with retry option. |
| Activity log grows unbounded | Low | Paginate activity (load last 20, "Show More" button). Archive old entries after 90 days in future phase. |
| Comments without auth have no real identity | Low | Store session-scoped identifier; document this as a placeholder for Phase 4 user model. |

---

## 6. Release Checklist

- [ ] Label CRUD and assignment to cards
- [ ] Labels visible as colored chips on board view (with name toggle)
- [ ] Due date picker with overdue/upcoming visual indicators
- [ ] Due date completion toggle
- [ ] Checklist CRUD with progress bar on card front
- [ ] Checklist item drag reorder
- [ ] Comment add/edit/delete with timestamps
- [ ] Activity log tracking major card events
- [ ] File attachment upload, preview, download, and delete
- [ ] Card cover image from attachment
- [ ] Card detail modal layout (content + sidebar)
- [ ] Server-side file validation and storage integration
- [ ] Cascade delete verified for all child entities
