# Product Requirements Document — Phase 4

## Trello Clone: Collaboration & Users

---

| Field | Detail |
|---|---|
| **Version** | 1.0 |
| **Date** | March 23, 2026 |
| **Author** | Product Management |
| **Status** | Draft |
| **Target Release** | Sprint 10–13 (8 weeks) |
| **Dependency** | Phase 3 (Multi-Board & Navigation) complete |

---

## 1. Overview

Phase 4 introduces the user identity layer and real-time collaboration — the features that turn this from a single-player tool into a shared workspace. Users can sign up, log in, invite others to boards, assign members to cards, and see changes from collaborators in real time. This is the highest-complexity phase and the one that unlocks the product's core value proposition as a team tool.

### 1.1 Objectives

- Establish a user identity model with secure authentication (email/password + OAuth).
- Enable board-level collaboration with invitations and membership roles.
- Allow card-level member assignment so teams can distribute work.
- Deliver real-time synchronization so collaborators see each other's changes instantly.
- Retrofit all existing data (boards, cards, comments, activity) with user ownership.

### 1.2 Success Metrics

| Metric | Target |
|---|---|
| Account creation to first board shared | < 5 minutes |
| Boards with ≥ 2 members (after 2 weeks) | ≥ 30% of all boards |
| OAuth sign-up conversion (click → account created) | ≥ 70% |

### 1.3 Scope

**In scope:** User registration (email/password), OAuth login (Google, GitHub), user profile (name, avatar, email), board membership (invite via email, roles: Admin / Member), card member assignment, real-time updates via WebSocket, user presence on board, activity feed with real user identity, session management, password reset.

**Out of scope:** Workspace/team-level organization (Phase 7), granular permissions beyond Admin/Member (Phase 7), notifications (Phase 5), SSO/SAML (Phase 7).

---

## 2. User Stories

### 2.1 Authentication

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P4-01 | As a visitor, I want to create an account with email and password so I can start using the app. | 1. Registration form: name, email, password, confirm password. 2. Email validation (format + uniqueness). 3. Password requirements: ≥ 8 characters, at least one letter and one number. 4. Account created → redirected to home dashboard. | Must Have |
| P4-02 | As a visitor, I want to sign up / log in with Google or GitHub so I can get started without creating a new password. | 1. "Continue with Google" and "Continue with GitHub" buttons on auth pages. 2. OAuth flow creates account on first use, logs in on subsequent uses. 3. Profile name and avatar auto-populated from OAuth provider. | Must Have |
| P4-03 | As a user, I want to log in with my email and password. | 1. Login form with email + password. 2. "Incorrect email or password" message on failure (no indication of which field is wrong). 3. Successful login redirects to home dashboard. | Must Have |
| P4-04 | As a user, I want to reset my password if I forget it. | 1. "Forgot password?" link on login page. 2. Enter email → receive reset link (valid for 1 hour). 3. Reset page: new password + confirm. 4. After reset, user is logged in automatically. | Must Have |
| P4-05 | As a user, I want to log out from any device. | 1. Logout option in user menu (top-right avatar). 2. Session invalidated server-side. 3. Redirect to login page. | Must Have |

### 2.2 User Profile

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P4-06 | As a user, I want to view and edit my profile (name, avatar) so my collaborators can identify me. | 1. Profile page accessible from user menu. 2. Name is editable. 3. Avatar: upload custom image or use initials-based fallback. 4. Email is displayed but not editable (change email is a future feature). | Must Have |
| P4-07 | As a user, I want my avatar and name shown on cards I'm assigned to and on comments I write. | 1. Avatar displayed as a circular thumbnail (24–32px). 2. Comments retroactively show real identity (replace "You" placeholder from Phase 2). | Must Have |

### 2.3 Board Membership & Invitations

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P4-08 | As a board admin, I want to invite people to my board via email so they can collaborate. | 1. "Invite" button on board header opens invite dialog. 2. Enter one or more email addresses. 3. If the email belongs to an existing user, they're added immediately and see the board on their home page. 4. If the email is unregistered, an invitation email is sent with a sign-up link that auto-joins the board. | Must Have |
| P4-09 | As a board admin, I want to set a member's role to Admin or Member so I can control who can manage the board. | 1. Admin can: rename board, change background, archive/delete board, manage members, remove other members. 2. Member can: create/edit/move/archive cards and lists, add comments, upload attachments. 3. Role selectable in member management panel. | Must Have |
| P4-10 | As a board admin, I want to remove a member from the board. | 1. Remove option in member management panel. 2. Removed member loses access immediately. 3. Their cards, comments, and activity entries remain attributed to them. | Must Have |
| P4-11 | As a user, I want to leave a board I no longer want to be part of. | 1. "Leave Board" option in board menu. 2. Confirmation dialog. 3. If the user is the last admin, they must assign another admin first or delete the board. | Must Have |
| P4-12 | As a user, I want to see all members of a board so I know who I'm collaborating with. | 1. Member avatars displayed in board header (max 5 visible + "+N" overflow). 2. Clicking opens a full member list with roles. | Must Have |

### 2.4 Card Member Assignment

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P4-13 | As a user, I want to assign one or more board members to a card so we know who is responsible. | 1. "Members" option in card detail sidebar. 2. Dropdown shows board members with checkboxes. 3. Assigned members' avatars appear on the card front (board view). | Must Have |
| P4-14 | As a user, I want to remove a member from a card. | 1. Uncheck in the members dropdown. 2. Avatar removed from card front. | Must Have |
| P4-15 | As a user, I want to quickly assign myself to a card. | 1. "Join" button in card detail (adds current user). 2. Pressing spacebar on a focused card adds/removes self (keyboard shortcut). | Should Have |

### 2.5 Real-Time Collaboration

| ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| P4-16 | As a user, I want to see changes made by other board members in real time without refreshing. | 1. Card creation, editing, movement, and deletion by others reflected within 500ms. 2. List creation, editing, and reordering by others reflected in real time. 3. Label, due date, checklist, and comment changes by others reflected in real time. | Must Have |
| P4-17 | As a user, I want to see who else is currently viewing the same board (presence). | 1. Avatars of online board members shown in the board header with a green dot. 2. Users who leave or go idle (>5 minutes) are removed from presence. | Should Have |
| P4-18 | As a user, I want to see when someone else is currently editing a card I'm also viewing. | 1. If two users have the same card detail open, a banner shows "X is also editing this card." 2. No conflict resolution needed — last-write-wins with real-time sync. | Should Have |
| P4-19 | As a user, I want the app to automatically reconnect if my connection drops. | 1. WebSocket auto-reconnects with exponential backoff (1s, 2s, 4s, max 30s). 2. On reconnect, client fetches latest board state to reconcile. 3. "Reconnecting…" banner shown during disconnection. | Must Have |

---

## 3. Functional Requirements

### 3.1 Data Model Extensions

```
User
├── id: UUID
├── email: string (unique)
├── password_hash: string (nullable for OAuth-only users)
├── name: string
├── avatar_url: string (nullable)
├── auth_provider: enum (local, google, github)
├── auth_provider_id: string (nullable)
├── created_at: timestamp

Board (extended)
├── owner_id: FK → User (creator)

BoardMember
├── board_id: FK → Board
├── user_id: FK → User
├── role: enum (admin, member)
├── joined_at: timestamp

CardMember (join table)
├── card_id: FK → Card
├── user_id: FK → User

Comment (extended)
├── user_id: FK → User (replaces author_name)

Activity (extended)
├── user_id: FK → User

Session
├── id: UUID
├── user_id: FK → User
├── token_hash: string
├── expires_at: timestamp
├── created_at: timestamp

PasswordReset
├── id: UUID
├── user_id: FK → User
├── token_hash: string
├── expires_at: timestamp
├── used: boolean
```

### 3.2 API Endpoints (New)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account (email/password) |
| POST | `/api/auth/login` | Log in |
| POST | `/api/auth/logout` | Log out (invalidate session) |
| GET | `/api/auth/oauth/:provider` | Initiate OAuth flow |
| GET | `/api/auth/oauth/:provider/callback` | OAuth callback |
| POST | `/api/auth/forgot-password` | Send reset email |
| POST | `/api/auth/reset-password` | Reset password with token |
| GET | `/api/users/me` | Get current user profile |
| PATCH | `/api/users/me` | Update profile (name, avatar) |
| GET | `/api/boards/:id/members` | List board members |
| POST | `/api/boards/:id/members` | Invite member (by email) |
| PATCH | `/api/boards/:id/members/:userId` | Update member role |
| DELETE | `/api/boards/:id/members/:userId` | Remove member |
| POST | `/api/cards/:id/members` | Assign member to card |
| DELETE | `/api/cards/:id/members/:userId` | Remove member from card |

### 3.3 WebSocket Architecture

- **Channel model**: One channel per board. Users subscribe when opening a board, unsubscribe when navigating away.
- **Event types**: `card:created`, `card:updated`, `card:moved`, `card:deleted`, `list:created`, `list:updated`, `list:moved`, `list:deleted`, `member:joined`, `member:left`, `presence:update`.
- **Payload**: Each event includes the full updated entity (not a diff) for simplicity.
- **Auth**: WebSocket connections authenticated via the same session token.

### 3.4 Security Requirements

| Area | Requirement |
|---|---|
| Passwords | Hashed with a strong, slow hashing algorithm. Never stored in plain text. |
| Sessions | HTTP-only, Secure cookies. Token rotation on sensitive actions. |
| OAuth | CSRF protection on OAuth flows. Tokens stored server-side only. |
| Authorization | Every API endpoint checks board membership. Card/list endpoints verify the user is a member of the parent board. |
| Rate limiting | Auth endpoints rate-limited per IP. API rate-limited per user. |
| Input | All user input sanitized. Comments rendered as plain text (no HTML injection). |

---

---

## 4. UX & Design Notes

- **Auth pages**: Clean, centered card layout. Social login buttons above the divider, email/password form below.
- **Board header**: Shows member avatars on the right side. Invite button prominent (blue, labeled "Invite").
- **Card front avatars**: Small (24px) circles in the bottom-right of the card. Max 3 visible + "+N".
- **Presence indicators**: Green dot (online), gray dot (offline/idle). Shown on board header avatars.
- **Reconnection banner**: Fixed at the top of the viewport, yellow background, "Reconnecting…" with a spinner.
- **Member management panel**: Drawer from the right. Shows avatar, name, email, role dropdown, and remove button.

---

## 5. Migration Plan

Transitioning from the unauthenticated Phase 1–3 world to authenticated Phase 4:

1. Existing data in development/staging environments can be wiped (acceptable for pre-launch).
2. If preserving data is required (e.g., beta users), create a migration that assigns all existing boards to a default "demo" user account, and existing comments/activity to a "Legacy User" attribution.
3. On first login, allow users to "claim" boards via a one-time board transfer flow (enter a board ID or use a link).

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| WebSocket scaling under load | High | Start with single-server; benchmark at 500 connections; add Redis pub/sub adapter before public launch. |
| OAuth provider downtime blocks login | Medium | Always offer email/password as fallback. Cache OAuth tokens appropriately. |
| Conflict when two users edit the same card field simultaneously | Medium | Last-write-wins with real-time sync means the latest save prevails. Show "X is also editing" warning. Full CRDT-based conflict resolution deferred to future phase. |
| Invitation abuse (spam invites to non-users) | Low | Rate-limit invitations (20 per board per hour). Include unsubscribe link in invitation emails. |
| Migration complexity from unauthenticated data | Medium | Prefer clean-slate for launch; document migration path for beta retention scenarios. |

---

## 7. Release Checklist

- [ ] User registration (email/password) with validation
- [ ] Login / logout with session management
- [ ] Google OAuth flow (sign up + login)
- [ ] GitHub OAuth flow (sign up + login)
- [ ] Password reset via email
- [ ] User profile view and edit (name, avatar)
- [ ] Board membership model with Admin/Member roles
- [ ] Invite members via email (existing + new users)
- [ ] Member management panel (role change, remove)
- [ ] Leave board flow with last-admin guard
- [ ] Card member assignment (assign, remove, self-join)
- [ ] Member avatars on card fronts and board header
- [ ] WebSocket real-time sync for all board events
- [ ] User presence on board (online/idle indicators)
- [ ] "Also editing" indicator on card detail
- [ ] Auto-reconnect with state reconciliation
- [ ] Authorization middleware on all API endpoints
- [ ] Rate limiting on auth and API endpoints
- [ ] Security audit: password hashing, session cookies, CSRF, input sanitization
- [ ] Comments and activity retroactively linked to user identities
