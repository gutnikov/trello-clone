---
name: orca-scope-analysis
description: >
  Analyze codebase impact for a Linear issue and calculate a scope_score (1-10) to determine
  if the issue is atomic or needs decomposition. Use when the Scoping Agent needs to evaluate
  an issue in the "Scoping" Linear state. Also use when asked to assess the complexity or
  blast radius of a proposed change. Do NOT use for implementation planning or test design
  (use design-feedback-loop for that). Do NOT use when decomposing issues into sub-issues
  (use decompose-issue after this skill produces a score > 6).
---

# Scope Analysis

Analyze the codebase impact of a Linear issue and calculate a scope_score (1-10) that determines whether the issue is atomic (implementable as-is) or needs decomposition.

## Why This Matters

Agents that attempt oversized changes make more errors, produce harder-to-review PRs, and are more likely to stall. A scope_score above 6 signals the issue should be decomposed before any planning or implementation begins. This isn't a judgment — it's a routing decision.

## Step 1: Read the Issue

Read the issue title, description, and any linked specs or plans. Identify:
- What behavior is being added, changed, or removed
- Any explicit acceptance criteria or test requirements
- Any dependencies or blockers mentioned

## Step 2: Identify Affected Files

Search the codebase for files that would need modification. Use Grep, Glob, and Read tools — don't guess from memory.

Look for:
- Symbols, patterns, or paths mentioned in the issue
- Imports and call sites of functions being changed
- Type definitions, config files, migration files
- Test files that would need updating

List each affected file with a one-line reason for the change.

## Step 3: Identify Affected Subsystems

Read `docs/agents/scoping.md` for this project's subsystem boundaries. If it hasn't been customized, infer subsystems from the directory structure (e.g., `src/api/`, `src/services/`, `src/db/` each count as one subsystem).

Count how many subsystems the change crosses.

## Step 4: Estimate Lines of Code

Estimate the total lines of new + modified code needed. Be conservative — estimates should reflect actual implementation work. Consider:
- New functions, classes, or modules
- Existing functions to modify
- Test code (even though it's written later by the Design Feedback Loop Agent)
- Config or migration files

## Step 5: Check for Migrations and API Changes

**Migrations:** Does this issue require a database migration, schema change, or data transform? (New tables, columns, indexes, enum changes, data transformations.)

**API surface:** Does this issue change any public interface? (REST endpoints, GraphQL types, exported functions/classes, environment variables, config schemas.)

## Step 6: Calculate the Score

Apply the additive scoring formula:

| Dimension | Threshold | Points |
|-----------|-----------|--------|
| Files affected | 1-3 files | 1 pt |
| Files affected | 4-7 files | 2 pt |
| Files affected | 8+ files | 3 pt |
| Subsystems crossed | 1 subsystem | 0 pt |
| Subsystems crossed | 2 subsystems | 1 pt |
| Subsystems crossed | 3+ subsystems | 2 pt |
| Estimated LOC | < 100 LOC | 0 pt |
| Estimated LOC | 100-300 LOC | 1 pt |
| Estimated LOC | 300+ LOC | 2 pt |
| Migration needed | yes | +2 pt |
| API surface change | yes | +1 pt |

**Maximum possible score: 10**

Check `docs/agents/scoping.md` for project-specific overrides to these thresholds before applying the defaults.

## Step 7: Make the Decision

| Score | Decision | What happens next |
|-------|----------|-------------------|
| 1-6 | ATOMIC | Write scope report, signal `.orca/done` |
| 7-10 | NEEDS_DECOMPOSITION | Write scope report, then use the `orca-decompose-issue` skill to produce `.orca/decomposition.json` |

## Step 8: Write the Scope Report

Save to `docs/plans/{issue.identifier}-scope.md`:

```markdown
# Scope Report: {issue.identifier}

## Summary
One paragraph describing the scope of this issue.

## Affected Files
- `path/to/file.ext` — reason for change

## Subsystems Involved
- Subsystem name — what changes

## Scope Score: X/10

| Dimension | Value | Points |
|-----------|-------|--------|
| Files affected | N files | X pt |
| Subsystems crossed | N subsystems | X pt |
| Estimated LOC | ~N lines | X pt |
| Migration needed | yes/no | X pt |
| API surface change | yes/no | X pt |
| **Total** | | **X/10** |

## Decision: ATOMIC / NEEDS_DECOMPOSITION
Reasoning for the decision. If NEEDS_DECOMPOSITION, describe the proposed split strategy.
```

## Guidelines

- **Base analysis on actual codebase evidence.** Use search tools to find affected files — don't estimate from issue text alone.
- **When ambiguous, estimate conservatively.** A higher score leads to decomposition, which is safe. An underestimate leads to an agent attempting work that's too large, which causes failures.
- **A high score is not a failure.** It's a signal to decompose, which is the correct engineering response to complexity.
