---
name: type-checker
description: Configure static type checking
dependencies: [package-management]
docs:
  - docs/agents/validation.md
  - docs/agents/implementation.md
---

# Setup: Type Checker

## Detect

Check for existing type checking configuration:

- Python: `pyproject.toml` (look for `[tool.mypy]`), `mypy.ini`, `pyrightconfig.json`
- TypeScript: `tsconfig.json` (type checking is built-in via `tsc --noEmit`)
- Go: built into `go build` / `go vet` — no separate config needed
- Rust: built into `cargo check` — no separate config needed

If Go or Rust, report "configured" (built-in). If TypeScript with `tsconfig.json`, report "configured." If Python with mypy/pyright config, report "configured."

## Propose

Only needed for Python (if not already configured):

| Tool | Config | Why |
|------|--------|-----|
| mypy (strict) | `pyproject.toml [tool.mypy]` | Industry standard, strict mode catches more bugs |

For Go, Rust, TypeScript: explain that type checking is built-in and no additional setup is needed.

Present proposal and wait for approval.

## Configure

For Python, add to `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

Install: `pip install mypy`

For other languages: no configuration needed — built-in tooling.

## Verify

Run the type checker:
```bash
# Python
python3 -m mypy src/
# TypeScript
npx tsc --noEmit
# Go
go vet ./...
# Rust
cargo check
```

Must complete without configuration errors and exit 0. Type errors in existing code are acceptable for now.

## Docs Update

Update `docs/agents/validation.md` — add type checking to the "Required Checks" `<!-- CUSTOMIZE -->` section:

```markdown
3. **Type checking:** `<exact type check command>`
```

Update `docs/agents/implementation.md` — add type check command to Build & Run section.

## Definition of Done

- [ ] Type checker is available (installed or built-in)
- [ ] Config exists (if applicable — Python needs one, Go/Rust/TS don't)
- [ ] Type checker runs on project source and exits 0 (without configuration errors)
- [ ] `docs/agents/validation.md` has exact type check command
- [ ] `docs/agents/implementation.md` has type check info
