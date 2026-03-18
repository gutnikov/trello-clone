# Docs Agent Context

## Documentation Responsibilities

The Docs Agent updates all harness artifacts after implementation is complete. It reads the doc impact checklist from `docs/plans/{issue.identifier}-doc-impact.md` and ensures every item is addressed.

## Docs Structure

| Directory | Contents | When to Update |
|---|---|---|
| `docs/architecture/` | ADRs | New architectural decisions, pattern changes |
| `docs/conventions/` | Golden principles, coding standards | New conventions established |
| `docs/agents/` | Agent context docs | New subsystems, changed conventions, new tools |
| `docs/guides/` | Setup and workflow references | Changed setup process, new workflows |
| `docs/runbooks/` | Operational procedures | New features requiring ops support |
| `docs/specs/` | Feature specifications | Spec updates based on implementation learnings |

## Validation Rules

After updating docs, verify:
1. All items in the doc impact checklist are addressed
2. All internal links (`docs/path/to/file.md`) point to files that exist
3. All code references (`src/path/to/file.ext:123`) point to actual code
4. No TODO/FIXME left in doc updates

## PR Creation

After docs are validated, create a PR using the `create-pr` skill:
1. Ensure all changes (code + tests + docs) are committed
2. Push the branch
3. Create PR with description referencing the Linear issue
4. Transition issue to "Review" state

## What This Agent Must NOT Do

- Do NOT modify application code or test files
- Do NOT create docs for features that weren't implemented
- Do NOT remove existing documentation without explicit justification
