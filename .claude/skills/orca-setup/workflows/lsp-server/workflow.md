---
name: lsp-server
description: Configure LSP server for code intelligence
dependencies: [package-management]
docs:
  - docs/agents/implementation.md
---

# Setup: LSP Server

## Detect

Check for existing LSP configuration:

- `opencode.json` — look for an `lsp` section
- `.vscode/settings.json` — check for language server settings
- Run `which pyright`, `which gopls`, `which rust-analyzer`, `which typescript-language-server` to check if LSP binaries are installed

If `opencode.json` already has an `lsp` section with entries for the detected language(s), report "configured." Otherwise report "not configured."

## Propose

Based on detected language(s), propose the appropriate LSP server:

| Language | LSP Server | Install Command |
|----------|-----------|-----------------|
| Python | pyright | `npm install -g pyright` or `pip install pyright` |
| TypeScript/JS | typescript-language-server | `npm install -g typescript-language-server typescript` |
| Go | gopls | `go install golang.org/x/tools/gopls@latest` |
| Rust | rust-analyzer | `rustup component add rust-analyzer` |

For other languages, research the recommended LSP server.

Present the proposal to the user and wait for approval before proceeding.

## Configure

1. Install the LSP server binary using the approved install command
2. Create or update `opencode.json` at the project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": {
    "<language>": {
      "command": ["<lsp-binary>", "--stdio"],
      "extensions": [".<ext>"]
    }
  }
}
```

For multi-language projects, add an entry per language.

## Verify

1. Confirm the LSP binary is on PATH: `<lsp-binary> --version` — must exit 0
2. Validate `opencode.json` is well-formed JSON
3. Test that the LSP server starts: run it in stdio mode and confirm it accepts an initialize request against a sample project file

## Docs Update

Update `docs/agents/implementation.md` — add LSP server info to the Coding Conventions section if not already present:

```markdown
### LSP
- Server: <lsp-server-name>
- Config: `opencode.json`
```

## Definition of Done

- [ ] LSP binary is installed and on PATH (`<binary> --version` exits 0)
- [ ] `opencode.json` exists with valid LSP configuration for detected language(s)
- [ ] LSP server starts and accepts an initialize request
- [ ] `docs/agents/implementation.md` has LSP server info
