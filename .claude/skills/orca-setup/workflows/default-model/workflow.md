---
name: default-model
description: Configure the default AI model for OpenCode
dependencies: []
docs:
  - docs/agents/implementation.md
---

# Setup: Default Model

## Detect

Check for existing model configuration:

1. Read `opencode.json` at the project root — look for a `model` key
2. If `opencode.json` has a `model` value set, report "configured" and show the current model
3. If `opencode.json` exists but has no `model` key, or doesn't exist at all, report "not configured"

## Propose

List available models by running:

```bash
opencode models
```

Present the models grouped by provider. Highlight the recommended defaults:

| Alias | Full Model ID | Best For |
|-------|--------------|----------|
| `anthropic/claude-opus-4-6` | `anthropic/claude-opus-4-6` | Complex reasoning, architecture |
| `anthropic/claude-sonnet-4-6` | `anthropic/claude-sonnet-4-6` | Balanced speed and quality |
| `anthropic/claude-haiku-4-5` | `anthropic/claude-haiku-4-5-20251001` | Fast, lightweight tasks |

If `opencode models` is not available, fall back to asking the user to specify a `provider/model` string manually.

Present the proposal and ask the user which model they'd like as their default. Wait for approval before proceeding.

## Configure

1. If `opencode.json` doesn't exist, create it:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "<provider/model>"
}
```

2. If `opencode.json` already exists, add or update the `model` key with the chosen value. Preserve all existing configuration (lsp, plugins, etc.).

3. Optionally, if the user wants per-agent models, configure the `agent` section:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "<provider/model>",
  "agent": {
    "build": { "model": "<provider/model>" },
    "plan": { "model": "<provider/model>" }
  }
}
```

Only add the `agent` section if the user explicitly asks for per-agent model overrides.

## Verify

1. Confirm `opencode.json` is valid JSON: `python3 -c "import json; json.load(open('opencode.json'))"`
2. Confirm the `model` key is present and matches the chosen value
3. Run `opencode models` and confirm the selected model appears in the list

## Docs Update

Update `docs/agents/implementation.md` — add or update the Default Model section:

```markdown
### Default Model
- Model: `<provider/model>`
- Config: `opencode.json`
```

## Definition of Done

- [ ] `opencode.json` exists with a valid `model` key
- [ ] The model value matches what the user selected
- [ ] `opencode.json` is valid JSON
- [ ] Selected model appears in `opencode models` output
- [ ] `docs/agents/implementation.md` has default model info
