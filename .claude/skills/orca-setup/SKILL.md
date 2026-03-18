---
name: orca-setup
description: >
  Set up and manage project validation infrastructure. Use `/orca` to see status
  of all setup workflows, or `/orca setup-<name>` to run a specific one.
  User-invocable only — not used by pipeline agents.
---

# Orca Setup Skill

Set up validation infrastructure for this project. Each setup phase is a separate workflow that can be run independently and re-run at any time.

## Invocation

### `/orca` — Status overview

1. Run the project scan (see below)
2. Discover all workflows by reading `workflows/*/workflow.md` frontmatter
3. For each workflow, run its Detect phase silently
4. Display a status table:

| Workflow | Status | Dependencies |
|----------|--------|-------------|
| package-management | configured | — |
| linter | not configured | met |
| ci | not configured | not met (linter, type-checker) |

Status values: `configured`, `not configured`, `outdated`

### `/orca setup-<name>` — Run a specific workflow

1. Run the project scan
2. Find the matching workflow — the `<name>` maps to the workflow directory name (e.g., `/orca setup-linter` runs `workflows/linter/workflow.md`)
3. **Check dependencies** — for each workflow listed in the `dependencies` frontmatter field, run its Detect phase. If any reports "not configured," refuse:
   > Cannot run setup-linter: package-management is not configured. Run `/orca setup-package-management` first.
4. Run the workflow's own Detect phase — if already configured, inform the user and ask if they want to re-run
5. Execute the workflow phases in order: Propose → Configure → Verify → Docs Update → DoD Check
6. If Verify or DoD Check fails, report the error — the workflow is not complete

### `/orca setup-all` — Run all unconfigured workflows

1. Topologically sort workflows by dependencies
2. Run each in order, skipping those where Detect reports "configured" and DoD passes
3. Stop on first failure

## Project Scan

Before dispatching to any workflow, perform a lightweight scan of the project:

- **Language(s):** Detect from config files (`pyproject.toml` → Python, `package.json` → JS/TS, `go.mod` → Go, `Cargo.toml` → Rust, `*.csproj`/`*.sln` → C#/.NET, `pom.xml`/`build.gradle` → Java/Kotlin). Confirm by checking file extensions in `src/` or project root.
- **Package manager:** `pip`/`npm`/`pnpm`/`yarn`/`cargo`/`go mod`/etc.
- **App type:** web app, API service, CLI tool, or library — inferred from project structure (presence of `server`/`app`/`api` directories, HTTP framework deps, `main` entry points, or pure library structure).
- **Runtime version:** from config files (`python_requires`, `engines.node`, `go` directive) or version managers (`.python-version`, `.nvmrc`, `rust-toolchain.toml`).

Pass this context to the workflow being executed.

## Common Rules

All workflows follow these rules:

1. **Detect before proposing** — never install something already configured. The Detect phase must report one of: "not configured", "configured", or "configured but outdated".
2. **Propose before acting** — always explain what you'll do and wait for user approval before making changes.
3. **Verify concretely** — the tool must actually run successfully. Not "config looks valid" but "ran the tool and it exited 0." If verification fails, report the error.
4. **Update docs after verify** — every workflow that affects agent behavior must update the relevant `docs/agents/*.md` files. Never skip doc updates.
5. **Check DoD last** — after Docs Update, verify all Definition of Done items pass. If any fail, the workflow is not complete.
6. **Be interactive** — ask the user when there are meaningful choices. Don't assume defaults without presenting them.
7. **Be idempotent** — re-running a workflow on an already-configured project should detect existing state and either skip or offer to update/reconfigure.

## Workflow File Format

Each workflow lives at `workflows/<name>/workflow.md` with this structure:

```
---
name: <directory-name>
description: <one-line description>
dependencies: [<list of workflow names>]
docs:
  - <list of doc files this workflow updates>
---

# Setup: <Display Name>

## Detect
[Check if already configured. Report: not configured / configured / outdated]

## Propose
[Present options based on project scan context. Wait for approval.]

## Configure
[Step-by-step setup instructions]

## Verify
[Concrete verification — run the tool, confirm success]

## Docs Update
[Update docs/agents/*.md with exact commands and config]

## Definition of Done
[Checklist — all items must be true for workflow to be complete]
```
