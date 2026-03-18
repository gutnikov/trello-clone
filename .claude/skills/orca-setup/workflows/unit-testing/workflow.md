---
name: unit-testing
description: Configure unit test framework and create smoke test
dependencies: [package-management]
docs:
  - docs/agents/validation.md
  - docs/agents/design-feedback-loop.md
---

# Setup: Unit Test Framework

## Detect

Check for existing test setup:

- Python: `pyproject.toml` (look for `[tool.pytest]`), `pytest.ini`, `tests/` directory
- TypeScript/JS: `jest.config.*`, `vitest.config.*`, `__tests__/` directory
- Go: `*_test.go` files (built-in `testing` package)
- Rust: `#[test]` in source files (built-in)

Report "configured" if a test framework is configured and a test directory exists with at least one test file. Report "not configured" otherwise.

## Propose

| Language | Framework | Install |
|----------|-----------|---------|
| Python | pytest + pytest-asyncio | `pip install pytest pytest-asyncio` |
| TypeScript/JS | vitest | `npm install -D vitest` |
| Go | built-in `testing` | none |
| Rust | built-in `#[test]` | none |

Also propose creating a test directory and a single smoke test. Present and wait for approval.

## Configure

1. Install the framework
2. Add test config to the project config file
3. Create the test directory structure
4. Create a single smoke test:

Python example (`tests/test_smoke.py`):
```python
def test_smoke():
    """Verify test framework is working."""
    assert True
```

## Verify

Run the test suite:
```bash
# Python
python3 -m pytest tests/ -v
# TypeScript
npx vitest run
# Go
go test ./...
# Rust
cargo test
```

The smoke test must pass and exit 0.

## Docs Update

Update `docs/agents/validation.md` — add unit test command to the "Required Checks" `<!-- CUSTOMIZE -->` section:

```markdown
4. **Unit tests:** `<exact test command>`
```

Update `docs/agents/design-feedback-loop.md` — replace the `<!-- CUSTOMIZE -->` placeholder in the "Test Structure" section:

```markdown
### Unit Tests
- Location: `<test directory>`
- Framework: <framework name>
- Naming: `<naming convention>`
- Run: `<exact test command>`
```

## Definition of Done

- [ ] Test framework is installed (or built-in)
- [ ] Test config exists in project config file
- [ ] Test directory exists with correct structure
- [ ] Smoke test exists, runs, and passes
- [ ] `docs/agents/validation.md` has exact test command
- [ ] `docs/agents/design-feedback-loop.md` has test structure info
