# Workflow Customization Guide

How to adapt the orca harness template for your project.

## Quick Start

1. Fork this repo
2. Customize `docs/agents/*.md` with your project's conventions
3. Update `WORKFLOW.md` config: project_slug, hooks, concurrency
4. Run `orca` and choose 'Initialize a new project' (or set up Linear states manually)
5. Run `orca WORKFLOW.md`

## Customizing Agent Context Docs

Each file in `docs/agents/` tells a specific agent about your project. These are the most important files to customize:

| File | What to customize |
|---|---|
| `scoping.md` | Your project's subsystem boundaries, scope thresholds |
| `planning.md` | Plan formats, project-specific planning rules |
| `design.md` | Test framework, test file locations, naming conventions |
| `implementation.md` | Language, framework, build commands, coding standards |
| `validation.md` | Which checks to run, exact commands, acceptance criteria |
| `docs-update.md` | Which docs exist, when each should be updated |

## Customizing Linear States

The template uses 10 Linear states:

```
Backlog → Todo → Scoping → Planning → Design Feedback Loop → Implementing → Validating → Docs → Review → Done
```

`orca init` creates all 10 states automatically. Todo is used for human-input questions (not in `active_states` — the orchestrator does not dispatch agents for it). Manual setup is only needed if customizing state names.

To use different state names, update `WORKFLOW.md`:

1. Change `active_states` and `terminal_states` in the YAML config
2. Update the `{% if issue.state == "..." %}` conditionals in the prompt template
3. State names must match your Linear workflow exactly (case-sensitive)

## Customizing Execution Modes

Two modes are supported, controlled via Linear labels:

- **review** (default): Agent pauses for human approval at Planning → Design Feedback Loop transition
- **autonomous**: Agent drives through without pausing

To change the default, modify the mode detection line in WORKFLOW.md:
```jinja2
{% set mode = "autonomous" if "autonomous" in issue.labels else "review" %}
```

## Tuning Concurrency

In `WORKFLOW.md` config:

```yaml
agent:
  max_concurrent_agents: 5        # total agents running at once
  max_concurrent_agents_by_state:
    Scoping: 3                    # limit scoping agents
    Implementing: 3               # limit implementation agents
```

Reduce concurrency for resource-intensive states. Increase for lightweight states like Scoping.

## Adding New Agent Types

To add a new agent role:

1. Create a role prompt: `.claude/agents/{name}-agent.md`
2. Create a context doc: `docs/agents/{name}.md`
3. Add a new Linear state (or reuse an existing one)
4. Add a `{% elif issue.state == "New State" %}` block in WORKFLOW.md
5. Update `active_states` in WORKFLOW.md config

## Customizing Hooks

```yaml
hooks:
  after_create: "git clone $REPO_URL ."          # clone repo into workspace
  before_run: "npm install"                       # install deps before agent starts
  after_run: "npm test"                           # run after agent finishes
  before_remove: "git push origin HEAD"           # push before cleanup
  timeout_ms: 120000                              # 2 min timeout for hooks
```

Common patterns:
- **Python:** `before_run: "pip install -e '.[dev]'"`
- **Node.js:** `before_run: "npm ci"`
- **Monorepo:** `after_create: "git clone $REPO_URL . && cd packages/api"`
