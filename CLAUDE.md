# CLAUDE.md — orca-harness-template

## Overview

A template for orca-orchestrated AI development. Issues move through a 10-state Linear pipeline; each state dispatches a specialized agent. Fork this repo, customize `docs/agents/`, and run `orca WORKFLOW.md`.

## Orca Pipeline

```
Backlog → Todo → Scoping → Planning → Design Feedback Loop → Implementing → Validating → Docs → Review → Done
```

Each state transition dispatches an agent. Agents communicate via canonical artifact files.

## Agent Roles

| Role | Triggered by State | What It Does |
|---|---|---|
| Scoping Agent | Scoping | Calculates scope_score, decomposes oversized issues |
| Planning Agent | Planning | Creates implementation plan, feedback loop, doc impact list |
| Design Feedback Loop Agent | Design Feedback Loop | Writes fail-first test scaffolds (TDD) |
| Implementation Agent | Implementing | Writes code to make tests pass |
| Validation Agent | Validating | Pushes branch, triggers CI, reports results |
| Docs Agent | Docs | Updates documentation, creates PR |

## Skills

| Skill | Used By | Purpose |
|---|---|---|
| `orca-scope-analysis` | Scoping Agent | Calculate scope_score and identify affected files |
| `orca-decompose-issue` | Scoping Agent | Produce `.orca/decomposition.json` for orchestrator-managed sub-issue creation |
| `orca-design-feedback-loop` | Planning Agent | Design verification strategy (tests + observability) |
| `orca-doc-impact-analysis` | Planning Agent | Identify which docs need updating |
| `orca-validate-docs` | Docs Agent | Check doc completeness before PR |
| `orca-create-pr` | Docs Agent | Open PR with checklist and labels |
| `check-ci` | Validation Agent | Push branch, create draft PR, poll CI status, write validation report |

## Setup

After running `orca init`, use `/orca-setup` to set up validation infrastructure. Run `/orca-setup` to see available setup workflows and their status, or `/orca-setup setup-<name>` to run a specific one.

## Customization

1. Fork this repo
2. Run `orca init` to scaffold and connect Linear
3. Use `/orca-setup` to configure validation infrastructure (linter, type checker, pre-commit hooks, CI, tests, staging)
4. Customize `docs/agents/*.md` with your project's conventions
5. Update `WORKFLOW.md`: set project_slug, hooks, concurrency
6. Run `orca WORKFLOW.md`

See `docs/guides/workflow-customization.md` for full details.

## Key Conventions

- Agent separation of concerns: each agent modifies only files within its mandate
- Canonical artifact paths use `{issue.identifier}` as namespace
- TDD enforced: Design Feedback Loop Agent writes failing tests; Implementation Agent makes them pass
- Docs are mandatory deliverables; PR creation blocked until validate-docs returns PASS
- CLAUDE.md stays under 120 lines — it's a map, not a manual
- See `docs/conventions/golden-principles.md` for all 12 principles

## Documentation Map

- `WORKFLOW.md` — Orca orchestration config and agent prompt templates
- `docs/agents/` — Per-agent context docs (customize these for your project)
- `docs/architecture/` — Architecture Decision Records (ADRs)
- `docs/conventions/` — Golden principles and coding standards
- `docs/guides/` — Setup and workflow references
- `docs/feedback-loops/` — Per-issue feedback loop plans
- `docs/plans/` — Per-issue scope and implementation plans
- `docs/runbooks/` — Operational runbooks

## Project Structure

```
CLAUDE.md                       # This file — the agent's map
WORKFLOW.md                     # Orca orchestration config
docs/
  agents/                       # Agent context docs (customize these)
    scoping.md
    planning.md
    design-feedback-loop.md
    implementation.md
    validation.md
    docs-update.md
  architecture/                 # ADRs
  conventions/                  # Golden principles
  feedback-loops/               # {id}-feedback.md files
  guides/                       # workflow-customization.md
  plans/                        # {id}-scope.md, {id}-plan.md files
  runbooks/                     # Operational runbooks
.claude/
  agents/                       # Agent role prompts
    orca-scoping-agent.md
    orca-planning-agent.md
    orca-design-feedback-loop-agent.md
    orca-implementation-agent.md
    orca-validation-agent.md
    orca-docs-agent.md
  skills/                       # Agent skills
```
