---
name: orca-validate-docs
description: >
  Verify documentation coverage and freshness after the Docs Agent has made updates. Use when
  the Docs Agent needs to validate its work before creating a PR. Also use when asked to check
  whether documentation is complete, consistent, or up-to-date. Produces a PASS or FAIL result
  with specific failure details. Do NOT use for writing or updating docs — this skill only
  validates existing docs. Do NOT use for code validation (use the test suite and linter for that).
---

# Validate Docs

Verify that all documentation required for a completed implementation has been created or updated, that internal links are valid, code references point to real files, and no outstanding TODOs remain. Produces a PASS or FAIL result.

## Why This Matters

Documentation that references nonexistent files or stale code paths actively misleads future agents. A passing validation means the harness is in better shape than before. A failing validation means the Docs Agent has more work to do — don't create the PR until it passes.

## Step 1: Check the Doc Impact Checklist

Read `docs/plans/{issue.identifier}-doc-impact.md`.

For each item marked complete (`- [x]`):
- Verify the file exists
- Verify the file was actually modified (check `git diff` or file contents)

For each item still unchecked (`- [ ]`):
- This is a failure — the item was identified as needed but not completed

## Step 2: Validate Internal Links

For each doc file created or updated in this issue, scan for internal references:

- Markdown links: `[text](docs/path/to/file.md)` or `[text](../path/to/file.md)`
- Bare path references: `` `docs/architecture/adr-001.md` ``

For each reference, resolve the path relative to the repo root and check the file exists.

**Skip:** External URLs (`http://`, `https://`), anchor links (`#section-name`), and paths inside `<!-- CUSTOMIZE: ... -->` blocks (template placeholders).

## Step 3: Validate Code References

For each doc file created or updated, scan for code path references:

- File paths: `` `src/path/to/file.ext` `` or `` `src/path/to/file.ext:123` ``

For each reference, check the file exists. If a line number is specified, check the file has at least that many lines.

**Skip:** Paths inside `<!-- CUSTOMIZE: ... -->` blocks and generic placeholders like `src/your-module/file.ext`.

## Step 4: Check for TODO/FIXME

Scan all doc files created or updated in this issue for:
- `TODO`, `FIXME`, `PLACEHOLDER`
- `<!-- TODO:`, `<!-- FIXME:`

Any occurrence is a failure. The Docs Agent should resolve these before the PR is created.

**Exception:** If `docs/agents/docs-update.md` designates certain placeholder patterns as acceptable (e.g., `<!-- CUSTOMIZE: ... -->` in template files), those are exempt.

## Step 5: Produce the Validation Report

**On PASS:**

```markdown
## Doc Validation: PASS

All checks passed for issue {issue.identifier}.

- Checklist items: N/N completed
- Internal links checked: N (all valid)
- Code references checked: N (all valid)
- TODO/FIXME remaining: 0

Docs are ready. Proceed to PR creation.
```

**On FAIL:**

```markdown
## Doc Validation: FAIL

Issue {issue.identifier} has N validation failure(s).

### Failures

#### Incomplete checklist items
- [ ] `docs/architecture/adr-005.md` — marked required, not created

#### Broken internal links
- `docs/agents/implementation.md` line 42: references `docs/guides/setup.md` which does not exist

#### Invalid code references
- `docs/runbooks/feature-x.md` line 18: references `src/services/feature_x.py` which does not exist

#### Outstanding TODO/FIXME
- `docs/conventions/golden-principles.md` line 73: contains "TODO: add example"

### Required Actions
1. Create `docs/architecture/adr-005.md`
2. Fix broken link in `docs/agents/implementation.md`
3. Fix code reference in `docs/runbooks/feature-x.md`
4. Resolve TODO at `docs/conventions/golden-principles.md:73`
```

## Guidelines

- **Run this after the Docs Agent believes it's done** — this is a final gate, not a progress check.
- **A FAIL is not an error** — it's the correct outcome when doc work is incomplete. Fix the failures and run again.
- **When uncertain whether a reference is a real path or a template placeholder**, flag it. Stricter is better — a false positive is easy to dismiss, a missed broken link misleads future agents.
