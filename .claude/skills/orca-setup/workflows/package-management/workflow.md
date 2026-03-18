---
name: package-management
description: Detect project language(s) and package manager
dependencies: []
docs: []
---

# Setup: Package Management

## Detect

Examine the project root for language-specific config files and source directories:

- `pyproject.toml`, `setup.py`, `setup.cfg` → Python
- `package.json` → JavaScript/TypeScript
- `go.mod` → Go
- `Cargo.toml` → Rust
- `*.csproj`, `*.sln` → C#/.NET
- `pom.xml`, `build.gradle` → Java/Kotlin

Also check file extensions in the `src/` directory (or project root) to confirm.

If multiple languages are detected (monorepo), identify the primary language and list secondary ones.

Report "configured" if at least one language config file exists. Report "not configured" if no recognizable language config files are found.

## Propose

Present detected language(s), package manager, and runtime version to the user for confirmation:

> Detected: Python 3.12 with pip (from pyproject.toml)
>
> Is this correct? If not, please clarify your project's language and package manager.

If no language was detected, ask the user to specify.

## Configure

No configuration needed — this workflow detects and confirms, it doesn't install anything.

If no language config file exists (e.g., bare project), propose creating the appropriate one:
- Python: `pyproject.toml` with `[project]` section
- TypeScript/JS: `package.json` with basic fields
- Go: `go mod init`
- Rust: `cargo init`

## Verify

Confirm the package manager is functional:

```bash
# Python
pip --version
# Node.js
npm --version  # or pnpm/yarn
# Go
go version
# Rust
cargo --version
```

The command must exit 0.

## Docs Update

No docs to update — this is a foundational detection workflow that other workflows build on.

## Definition of Done

- [ ] At least one language config file exists in the project root
- [ ] Package manager binary is available and exits 0 when queried for version
- [ ] Language, package manager, and runtime version are confirmed with the user
