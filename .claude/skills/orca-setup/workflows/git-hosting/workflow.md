---
name: git-hosting
description: Detect git hosting platform and configure CLI tools
dependencies: [package-management]
docs:
  - docs/agents/implementation.md
---

# Setup: Git Hosting

## Detect

Parse `git remote get-url origin` to identify the hosting platform:

- URL contains `github.com` → GitHub
- URL contains `gitlab.com` → GitLab
- Other → ask user to specify (self-hosted instances require user confirmation)

Check if the corresponding CLI is installed and authenticated:
- GitHub: `gh auth status` exits 0
- GitLab: `glab auth status` exits 0

Report "configured" if host is detected, CLI is installed, and CLI is authenticated. Report "not configured" otherwise.

## Propose

Present detected host and CLI status to the user:

> Detected: GitHub (from git@github.com:owner/repo.git)
> CLI: gh is installed and authenticated
>
> Is this correct?

If CLI is missing, propose installing it:

| Host | CLI | Install |
|------|-----|---------|
| GitHub | gh | `brew install gh` (macOS) / `apt install gh` (Linux) / see https://cli.github.com |
| GitLab | glab | `brew install glab` (macOS) / `apt install glab` (Linux) / see https://gitlab.com/gitlab-org/cli |

If CLI is installed but not authenticated, propose authenticating:
- GitHub: `gh auth login`
- GitLab: `glab auth login`

Wait for user approval before proceeding.

## Configure

1. Install CLI if not present (using approved method)
2. Authenticate if not already authenticated

## Verify

Full round-trip PR/MR test:

1. Confirm CLI is authenticated: `gh auth status` / `glab auth status` — must exit 0
2. Create a test branch: `git checkout -b orca-setup-test-$(date +%s)`
3. Create an empty commit: `git commit --allow-empty -m "orca setup test"`
4. Push the branch: `git push -u origin HEAD`
5. Create a PR/MR:
   - GitHub: `gh pr create --title "Orca setup test" --body "Automated test — will be deleted" --head <branch>`
   - GitLab: `glab mr create --title "Orca setup test" --description "Automated test — will be deleted" --source-branch <branch>`
6. Verify PR/MR exists:
   - GitHub: `gh pr view <branch> --json url` exits 0
   - GitLab: `glab mr view <branch>` exits 0
7. Close and clean up:
   - GitHub: `gh pr close <branch> --delete-branch`
   - GitLab: `glab mr close <branch>` then `git push origin --delete <branch>`
8. Delete local test branch: `git checkout main && git branch -D <branch>`

All steps must succeed. Clean up automatically regardless of where a failure occurs (use try/finally pattern).

## Docs Update

Add a "Git Hosting" section to `docs/agents/implementation.md`:

```markdown
### Git Hosting
- **Host:** GitHub / GitLab
- **Repo:** owner/repo (from git remote)
- **CLI:** gh / glab
- **Create PR:** `gh pr create --title {title} --body {body} --head {branch}` / `glab mr create --title {title} --description {body} --source-branch {branch}`
- **Check CI:** `gh pr checks {branch} --json state` / `glab ci status --branch {branch} --output json`
- **PR status:** `gh pr view {branch} --json state,mergeable` / `glab mr view {branch} --json state`
```

## Definition of Done

- [ ] Git host detected from remote URL
- [ ] CLI tool (`gh` or `glab`) is installed and on PATH
- [ ] CLI tool is authenticated (`auth status` exits 0)
- [ ] Round-trip PR/MR test passed (create, verify, close, cleanup)
- [ ] `docs/agents/implementation.md` has Git Hosting section with exact CLI commands
