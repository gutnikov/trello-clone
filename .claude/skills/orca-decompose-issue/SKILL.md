---
name: orca-decompose-issue
description: >
  Break a large Linear issue into smaller sub-issues by writing `.orca/decomposition.json`.
  Use when the Scoping Agent has calculated a scope_score > 6 and the issue needs to be
  split before planning can begin. Do NOT use for atomic issues (scope_score <= 6).
  Do NOT use for implementation planning — decomposition is purely about splitting work
  into independently shippable pieces.
---

# Decompose Issue

Split an oversized Linear issue into smaller, independently implementable sub-issues by writing `.orca/decomposition.json`. The orchestrator reads this file and handles all Linear API calls — creating child issues, setting parent relationships, and wiring up blocking relations.

## Why This Matters

Agents fail at oversized tasks. Decomposition is the engineering response to complexity — not a sign of failure. Each sub-issue becomes its own orca pipeline run: Scoping → Planning → Design Feedback Loop → Implementing → Validating → Docs → Review → Done.

## Prerequisites

- The scope report must exist at `docs/plans/{issue.identifier}-scope.md`
- The scope report's decision must be `NEEDS_DECOMPOSITION` (scope_score > 6)

## Step 1: Read the Scope Report

Read `docs/plans/{issue.identifier}-scope.md`. Extract:
- The affected files and which subsystems they belong to
- The estimated LOC breakdown per area
- The decision section, which may already suggest a split strategy

## Step 2: Find the Natural Seams

A good decomposition splits where the code already separates. Prefer the first strategy that fits:

**By subsystem** (best when work crosses module boundaries):
- One sub-issue per subsystem touched
- Each sub-issue changes files within a single subsystem
- Example: "Add user avatar — API layer" and "Add user avatar — UI layer"

**By layer** (best for vertical slices through one subsystem):
- Data layer (schema, migration)
- Business logic
- API / interface
- Consumer / UI

**By phase** (best for sequential foundation-then-feature work):
- Foundational change first (new abstraction, new table)
- Feature built on the foundation second

These strategies can combine — a subsystem split where one subsystem also needs a phase split is fine.

### What makes a valid sub-issue

- Independently implementable and testable on its own
- Estimated scope_score ≤ 6
- Clear about what files it touches and why
- If it depends on a sibling, the dependency is explicit

### When to stop and escalate

If you can't find a clean split — the changes are deeply entangled, or every decomposition leaves sub-issues with scope_score > 6 — write `.orca/needs-human` instead. A bad decomposition is worse than no decomposition.

## Step 3: Write `.orca/decomposition.json`

This is the only output that matters. The orchestrator reads this file and creates all sub-issues in Linear automatically — you never call the Linear API yourself.

### Schema

```json
{
  "sub_issues": [
    {
      "key": "db-schema",
      "title": "PRJ-42: Add avatar column to users table",
      "description": "Sub-issue of PRJ-42: Add user avatars\n\n## What This Implements\nAdd the `avatar_url` column to the users table with a migration.\n\n## Affected Files\n- `db/migrations/003_add_avatar.py` — new migration\n- `src/models/user.py` — add field\n\n## Estimated Scope Score: 3/10",
      "priority": 2
    },
    {
      "key": "api",
      "title": "PRJ-42: Avatar upload API endpoint",
      "description": "Sub-issue of PRJ-42: Add user avatars\n\n## What This Implements\nPOST /users/:id/avatar endpoint for uploading and storing avatar images.\n\n## Affected Files\n- `src/api/users.py` — new endpoint\n- `src/services/storage.py` — upload helper\n\n## Estimated Scope Score: 4/10",
      "priority": 3,
      "depends_on": ["db-schema"]
    }
  ]
}
```

### Field reference

**Top-level:**
| Field | Required | Description |
|-------|----------|-------------|
| `sub_issues` | yes | Array of child issues to create |

**Each sub-issue:**
| Field | Required | Description |
|-------|----------|-------------|
| `title` | yes | Prefixed with parent identifier (e.g., `PRJ-42: ...`) |
| `description` | no | Markdown body — use the template from Step 2's output |
| `priority` | no | Linear priority 0–4 (inherits from parent if omitted) |
| `key` | no* | Lowercase identifier for dependency references (`^[a-z][a-z0-9_-]{0,49}$`) |
| `depends_on` | no | Array of sibling `key` values that must complete first |

*`key` is required only when another sub-issue references it in `depends_on`.

### Validation rules

The orchestrator validates the file before creating anything. If validation fails, no sub-issues are created. The rules:

- **Flat only** — sub-issues cannot contain nested `sub_issues`
- **Unique keys** — no duplicate `key` values
- **Valid references** — every entry in `depends_on` must match an existing `key`
- **No cycles** — the dependency graph must be a DAG
- **Key format** — lowercase, starts with a letter, max 50 characters

### What the orchestrator does with this file

1. Creates each sub-issue in the **Scoping** state with a parent relationship to the current issue
2. Creates **blocking relations**: each child blocks the parent, and dependencies block their dependents
3. If the parent has a `yolo` label, propagates it to children
4. Parent stays in its current state — the orchestrator manages its lifecycle from here

## Sub-Issue Description Template

Use this structure for each sub-issue's `description` field:

```
Sub-issue of {parent.identifier}: {parent.title}

## What This Implements
One paragraph describing exactly what this sub-issue delivers.

## Affected Files
- `path/to/file.ext` — why it changes

## Estimated Scope Score: X/10
- Files: X pt
- Subsystems: X pt
- LOC: X pt
- Migration: X pt
- API surface: X pt

## Dependencies
- Depends on: {sibling key or "none"}
```

## Guidelines

- **Aim for 2–4 sub-issues.** More than 5 usually means the original issue was unclear, not complex — escalate with `.orca/needs-human` instead of over-splitting.
- **Check for existing work first.** Read the Linear issue's linked issues and comments. Don't create sub-issues for work that's already tracked elsewhere.
- **Title prefix is important.** Starting each title with the parent identifier (e.g., `PRJ-42:`) makes the relationship visible in Linear's UI without opening the issue.
- **Dependencies should be minimal.** If every sub-issue depends on the previous one, you've created a serial chain, not a decomposition. Parallel-safe splits let orca dispatch multiple agents concurrently.
