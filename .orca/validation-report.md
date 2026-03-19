# Validation Report — TRE-35

## CI Result: FAIL

**PR:** https://github.com/gutnikov/trello-clone/pull/5
**Branch:** TRE-35
**CI Workflow Runs:**
- CI: https://github.com/gutnikov/trello-clone/actions/runs/23285069007
- Deploy Staging: https://github.com/gutnikov/trello-clone/actions/runs/23285069003

## Job Results

| Job | Status | Duration |
|-----|--------|----------|
| Lint & Format | FAIL | 10s |
| Test | PASS | 13s |
| Deploy PR Preview | FAIL | 14s |
| E2E Tests | SKIPPED | (depends on deploy) |

## Failure Details

### 1. Lint & Format — FAIL (blocking)

**Step:** Run pre-commit
**Error:** `ruff` hook found 1 auto-fixable lint error and modified files:

```
ruff (legacy alias)......................................................Failed
- hook id: ruff
- files were modified by this hook

Found 1 error (1 fixed, 0 remaining).
```

**Root cause:** There is a ruff lint violation in the backend code that ruff can auto-fix. When pre-commit runs ruff with `--fix`, it modifies files, which causes the hook to fail (signaling the file was dirty).

**Fix required:** Run `cd backend && uv run ruff check src/ tests/ --fix` locally, then commit the fixed files. Alternatively, run `cd backend && uv run pre-commit run --all-files` to identify and fix the exact file/issue.

### 2. Deploy PR Preview — FAIL (non-blocking for CI, but informational)

**Step:** Deploy preview stack
**Error:** Backend container exited with code 3:

```
Container preview-pr-5-backend-1 Error dependency backend failed to start
dependency failed to start: container preview-pr-5-backend-1 exited (3)
```

**Root cause:** The backend Docker container fails to start. This could be related to the lifespan changes (DB initialization at startup) or a missing dependency in the production Docker image (e.g., `aiosqlite` or `httpx` not in non-dev dependencies). The Dockerfile uses `uv sync --no-dev --no-install-project`, so only production dependencies are installed.

**Fix required:** Check that all runtime dependencies (especially `aiosqlite`) are listed as non-dev dependencies in `backend/pyproject.toml`. Also verify the backend starts correctly with the new lifespan manager when no DB file path is configured.

## Summary

Two fixes needed before CI will pass:
1. **Fix ruff lint violation** — run ruff check/fix and commit
2. **Fix Docker startup** — ensure production dependencies are complete and lifespan works in containerized environment
