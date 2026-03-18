# Implementation Agent Context

## Coding Conventions

<!-- CUSTOMIZE: dev-tooling -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

## Implementation Workflow

1. Read the implementation plan from `docs/plans/{issue.identifier}-plan.md`
2. Read the existing fail-first tests created by the Design Feedback Loop Agent
3. Implement code to make tests pass, one test at a time
4. Run the full test suite after each change
5. Commit working code frequently (after each test passes)

## What This Agent Must NOT Do

- Do NOT modify test expectations to make tests pass
- Do NOT skip or delete failing tests
- Do NOT add features not described in the implementation plan
- Do NOT refactor code unrelated to the current issue
- If stuck after 3 attempts at making a test pass, escalate by adding the "needs-human" label to the Linear issue

## Commit Convention

<!-- CUSTOMIZE: commit-format -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

## Git Hosting

<!-- CUSTOMIZE: git-hosting -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->
