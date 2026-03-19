# Doc Impact Analysis: TRE-31

## Overview

TRE-31 introduces the first data models and persistence layer to the backend. Since this is greenfield infrastructure with no prior database or model documentation, the documentation impact is primarily additive — new docs rather than updates to existing ones.

---

## Impacted Documents

### 1. `CLAUDE.md` — Project Structure Section

- **Impact:** LOW — Minor update
- **Reason:** The Project Structure section (lines 75-101) may need to reflect the new `models.py` and `database.py` files if the team wants the map to reference the data layer. However, CLAUDE.md is meant to be a high-level map (Principle 1: under 120 lines), so individual source files should NOT be listed. No change needed unless the team decides to add a "Backend Architecture" subsection.
- **Action:** No change required. The existing structure already covers `backend/` implicitly.

### 2. `docs/architecture/` — New ADR Recommended

- **Impact:** MEDIUM — New ADR recommended
- **Reason:** This issue makes two architectural decisions that should be documented per Principle 6 (Document Decisions, Not Descriptions):
  1. **SQLite with aiosqlite** as the persistence backend (vs. PostgreSQL, in-memory stores, etc.)
  2. **Pydantic models separate from ORM** — the models are pure Pydantic, not SQLAlchemy/ORM models; the database layer manually maps between models and SQL.
- **Action:** The Docs Agent should create `docs/architecture/adr-001-sqlite-persistence.md` documenting:
  - Why SQLite was chosen for v0 (simplicity, zero-config, single-board scope)
  - Why Pydantic models are decoupled from the database layer (flexibility, testability)
  - Trade-offs acknowledged (no concurrent write scaling, no migration framework yet)

### 3. `docs/agents/implementation.md` — Backend Patterns

- **Impact:** LOW — Optional update
- **Reason:** The implementation agent context doc may benefit from noting the database module pattern (class-based Database with async connect/close lifecycle) so future implementation agents follow the same pattern when adding new entities or CRUD operations.
- **Action:** If the doc is currently a placeholder, defer to when more patterns are established. If it has content, add a note about the `Database` class pattern.

### 4. `docs/runbooks/deploy-prod.md` — Database File Location

- **Impact:** LOW — Future concern
- **Reason:** The persistence layer introduces a SQLite database file that needs to be persisted across deployments. The deploy runbook should eventually document where the `.db` file lives and how it's backed up. However, this is a v0 concern — the current Dockerfile and deploy config don't reference a database yet.
- **Action:** Defer to the deployment/infrastructure issue. Flag for future update.

### 5. `README.md` — Dependencies Section

- **Impact:** LOW — Minor update
- **Reason:** The README should reflect that `aiosqlite` is now a runtime dependency, and that the backend uses SQLite for persistence. This helps new contributors understand the tech stack.
- **Action:** The Docs Agent should add a brief mention of SQLite/aiosqlite to any "Tech Stack" or "Dependencies" section in the README.

---

## Documents NOT Impacted

| Document | Reason |
|---|---|
| `docs/conventions/golden-principles.md` | No new conventions introduced |
| `docs/guides/workflow-customization.md` | Orca workflow unchanged |
| `docs/agents/scoping.md` | Scoping process unchanged |
| `docs/agents/planning.md` | Planning process unchanged |
| `docs/agents/design-feedback-loop.md` | DFL process unchanged |
| `docs/agents/validation.md` | Validation process unchanged |
| `docs/agents/docs-update.md` | Docs process unchanged |
| `frontend/` docs | No frontend changes |

---

## Summary

| Document | Impact Level | Action |
|---|---|---|
| `CLAUDE.md` | None | No change needed |
| `docs/architecture/adr-001-sqlite-persistence.md` | Medium | **Create new ADR** — SQLite choice and model/DB separation |
| `docs/agents/implementation.md` | Low | Optional — note Database class pattern |
| `docs/runbooks/deploy-prod.md` | Low | Defer — flag for infrastructure issue |
| `README.md` | Low | Add aiosqlite/SQLite to tech stack description |
