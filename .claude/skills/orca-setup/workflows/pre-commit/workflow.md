---
name: pre-commit
description: Configure pre-commit hooks for linting and formatting
dependencies: [linter, type-checker]
docs:
  - docs/agents/validation.md
---

# Setup: Pre-commit Hooks

## Detect

Check for existing pre-commit configuration:

- `.pre-commit-config.yaml` — the standard config file
- `package.json` scripts with `precommit`, `pre-commit`, or `prepare` (husky)
- `.husky/pre-commit` — husky hook
- `.lefthook.yml` — lefthook config
- `git config --get core.hooksPath` — custom hooks path

Also check if `pre-commit` (Python) or `husky` (JS) is installed:
- `which pre-commit` or check `pyproject.toml` dev dependencies
- `npx husky --version` or check `package.json` devDependencies

Report "configured" if a pre-commit setup already runs the linter and formatter. Report "not configured" otherwise.

## Propose

| Ecosystem | Tool | Why |
|-----------|------|-----|
| Python | pre-commit | Language-agnostic, config-driven, widely adopted |
| JavaScript/TypeScript | husky + lint-staged | Native npm ecosystem, runs only on staged files |
| Go | pre-commit or lefthook | Both work well; pre-commit has more hooks available |
| Rust | pre-commit or cargo-husky | pre-commit is more flexible |

The hooks should run the tools already configured by the linter and type-checker workflows:
1. **Formatter** — auto-fix on commit (e.g., `ruff format`, `biome format`, `gofmt`)
2. **Linter** — with auto-fix where safe (e.g., `ruff check --fix`, `biome lint --fix`)
3. **Type checker** — block commit on type errors (optional, can be slow)

Present the exact config and wait for approval.

## Configure

**Python (pre-commit):**

1. Install: `pip install pre-commit`
2. Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0  # use latest
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

3. Install the hooks: `pre-commit install`

**JavaScript/TypeScript (husky + lint-staged):**

1. Install: `npm install -D husky lint-staged`
2. Initialize: `npx husky init`
3. Add lint-staged config to `package.json`
4. Update `.husky/pre-commit`: `npx lint-staged`

## Verify

1. Stage a file with a known lint violation
2. Attempt to commit — the hook should catch it and either auto-fix or block
3. Fix the violation and commit again — should succeed
4. Run `pre-commit run --all-files` (if using pre-commit) to confirm all hooks pass on the full codebase — must exit 0

## Docs Update

Update `docs/agents/validation.md` — add pre-commit hooks to the "Required Checks" `<!-- CUSTOMIZE -->` section:

```markdown
5. **Pre-commit hooks:** `<exact install command>` (e.g., `pre-commit install`)
```

## Definition of Done

- [ ] Pre-commit tool is installed
- [ ] Config file exists with linter and formatter hooks
- [ ] Hooks are installed in the git repo (`pre-commit install` or equivalent)
- [ ] `pre-commit run --all-files` (or equivalent) exits 0
- [ ] `docs/agents/validation.md` has pre-commit install command
