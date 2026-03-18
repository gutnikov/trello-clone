---
name: linter
description: Configure code linting and formatting
dependencies: [package-management]
docs:
  - docs/agents/validation.md
  - docs/agents/implementation.md
---

# Setup: Code Linter

## Detect

Check for existing linter configuration:

- Python: `ruff.toml`, `pyproject.toml` (look for `[tool.ruff]`), `.flake8`
- TypeScript/JS: `.eslintrc.*`, `eslint.config.*`, `biome.json`
- Go: `.golangci.yml`, `.golangci.yaml`
- Rust: clippy is built-in — check `Cargo.toml` for `[lints]`

Also check `.pre-commit-config.yaml` for linter hooks.

Report "configured" if a linter config exists. Report "not configured" otherwise.

## Propose

| Language | Linter | Why |
|----------|--------|-----|
| Python | ruff | Fast, replaces flake8 + isort + pyupgrade, includes formatter |
| TypeScript/JS | biome (or eslint + prettier) | biome is faster single-tool; eslint + prettier if team prefers |
| Go | golangci-lint | Meta-linter that runs multiple Go linters |
| Rust | clippy | Built into toolchain, no extra install |

Present the proposal with the specific config you'll create. Wait for approval.

## Configure

1. Install the linter if not already present
2. Create the config file with sensible defaults (follow the language community's recommended rules)
3. If `.pre-commit-config.yaml` exists, add the linter as a hook

Example for Python (ruff in pyproject.toml):
```toml
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM"]
```

## Verify

Run the linter on the project source:
```bash
# Python example
ruff check src/ tests/
ruff format --check src/ tests/
```

Must complete without configuration errors and exit 0. Code warnings are acceptable — the goal is confirming the linter runs.

## Docs Update

Update `docs/agents/validation.md` — replace the linting/formatting entries in the "Required Checks" `<!-- CUSTOMIZE -->` section:

```markdown
1. **Linting:** `<exact lint command>`
2. **Formatting:** `<exact format check command>`
```

Update `docs/agents/implementation.md` — add to the Coding Conventions `<!-- CUSTOMIZE -->` section:

```markdown
### Style
- Run `<exact lint command>` before committing
- Run `<exact format command>` before committing
- Follow existing patterns in the codebase
```

## Definition of Done

- [ ] Linter binary is installed and on PATH
- [ ] Config file exists with rules appropriate for the project
- [ ] Linter runs on project source and exits 0 (warnings acceptable, errors not)
- [ ] Format check runs on project source and exits 0
- [ ] `docs/agents/validation.md` has exact lint and format commands
- [ ] `docs/agents/implementation.md` has lint/format instructions in coding conventions
