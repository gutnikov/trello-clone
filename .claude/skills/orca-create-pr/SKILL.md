---
name: orca-create-pr
description: >
  Create or finalize a pull request for the current issue's changes. Handles both new PRs and
  converting existing draft PRs to ready for review. Use when the Docs Agent has completed
  documentation updates.
---

# Create PR

Push the current branch and open a pull request that gives reviewers full context: what changed, why, how it was verified, and what docs were updated. Then write the PR URL to `.orca/pr-url` so the orchestrator can track it.

## Prerequisites

Before creating the PR, confirm all of these:

1. `validate-docs` returned PASS for this issue
2. `.orca/validation-report.md` shows all checks passing
3. All code, test, and doc changes are committed (`git status` should be clean)
4. `.orca/` is in `.gitignore` — it contains orchestrator state that shouldn't be in the PR

If any prerequisite isn't met, fix it first. Don't create a PR with failing checks or uncommitted changes.

## Host Detection

Read the "Git Hosting" section from `docs/agents/implementation.md` to determine which CLI to use:

- If **Host: GitHub** → use `gh` commands throughout this skill
- If **Host: GitLab** → use `glab` commands: `glab mr create` instead of `gh pr create`, `glab mr view` instead of `gh pr view`
- If no Git Hosting section exists → fall back to `gh` (backward compatibility)

The commands below show GitHub syntax. For GitLab equivalents:

| GitHub | GitLab |
|--------|--------|
| `gh pr create --title ... --body ...` | `glab mr create --title ... --description ...` |
| `gh pr view --json url` | `glab mr view --json web_url` |
| `gh pr close` | `glab mr close` |

## Step 1: Check for Existing PR

A PR may already exist for this branch (e.g., from a previous attempt). Check before creating a duplicate:

```bash
gh pr view --json url 2>/dev/null
```

If a PR exists, check whether it is a draft:

```bash
# Check if PR is a draft
IS_DRAFT=$(gh pr view --json isDraft --jq '.isDraft' 2>/dev/null)
if [ "$IS_DRAFT" = "true" ]; then
  # Convert draft to ready
  gh pr ready
fi
```

Then continue to the **Updating an Existing PR** section below.

## Step 2: Push the Branch

```bash
git push -u origin HEAD
```

If rejected due to upstream changes:

```bash
git fetch origin
git rebase origin/main
git push -u origin HEAD
```

If the rebase has conflicts you can't safely resolve, signal for human help (`touch .orca/needs-human`) and stop.

## Step 3: Gather Context

Read these files to build the PR description:

| File | What to extract |
|------|-----------------|
| `docs/plans/{issue.identifier}-plan.md` | Summary of what was implemented |
| `docs/plans/{issue.identifier}-scope.md` | Scope score, affected files, subsystems |
| `docs/plans/{issue.identifier}-doc-impact.md` | Which docs were updated |
| `.orca/validation-report.md` | Test/lint/type-check/build results |

Also run `git diff main...HEAD --stat` to get the actual file change summary.

Not all files may exist (e.g., a small issue may skip doc-impact). Use what's available.

## Step 4: Create the PR

The PR title must include the issue identifier so Linear links it automatically:

```bash
gh pr create \
  --title "{issue.identifier}: {issue.title}" \
  --body "$(cat <<'EOF'
## Summary

Resolves {issue.identifier}: {issue.title}

{One paragraph: what was built, why it matters, any key decisions.}

## Changes

{Bullet list of key changes — be specific about what each file modification does, not just "added feature X".}

- `path/to/file.ext` — what changed and why

## Verification

{From .orca/validation-report.md — report the final state of each check.}

- Tests: PASS
- Lint: PASS
- Type check: PASS

## Documentation

{From doc-impact checklist — list what was updated.}

- `docs/path/to/file.md` — what was updated

## Scope

scope_score: {score}/10 | Files: {N} | Subsystems: {N}
EOF
)"
```

If `gh` is not available or not authenticated, write the PR description to `.orca/pr-description.md` and signal `touch .orca/needs-human` so a human can create it manually.

## Updating an Existing PR

If a PR already exists (draft or ready), push any new commits and update the description:

```bash
git push origin HEAD
gh pr edit --body "$(cat <<'EOF'
[updated PR body with doc changes appended]
EOF
)"
```

Then skip to Step 5 to write signal files.

## Step 5: Write the Signal Files

The orchestrator watches for these files to know the PR is ready:

```bash
# Write the PR URL so the orchestrator can track it
echo "https://github.com/org/repo/pull/123" > .orca/pr-url

# Signal completion
touch .orca/done
```

Both files are required. The orchestrator advances the issue to "Review" state when it sees `.orca/done`, and uses `.orca/pr-url` to link the PR in Linear.

## After the PR Is Created

The agent's work is done. A human reviewer takes it from here. Do not merge or approve the PR — that's outside the agent's mandate.

## Edge Cases

- **PR already exists:** Use the existing URL. Don't create a duplicate.
- **`gh` not installed:** Write the description to `.orca/pr-description.md` and escalate.
- **Push rejected after rebase:** Escalate with `.orca/needs-human`. Never force-push.
- **Missing context files:** Write the PR with whatever information is available. A PR with a partial description is better than no PR.
