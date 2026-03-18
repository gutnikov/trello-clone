---
name: ci
description: Configure CI pipeline for linting and testing
dependencies: [linter, type-checker, unit-testing, pre-commit, git-hosting]
docs:
  - docs/agents/validation.md
---

# Setup: CI Workflow

## Detect

Check for existing CI configuration:

- `.github/workflows/*.yml` → GitHub Actions
- `.gitlab-ci.yml` → GitLab CI
- `Jenkinsfile` → Jenkins
- `.circleci/config.yml` → CircleCI

Report "configured" if a CI workflow exists that runs linting and tests. Report "not configured" otherwise.

## Propose

If no CI exists, propose a workflow for the detected CI platform (default to GitHub Actions):

- **Lint job:** runs the linter, formatter check, and type checker (using commands from those workflows), with pre-commit hooks
- **Test job:** runs the unit test suite
- **deploy-preview job** — deploys the PR to a preview environment (runs after lint+test pass):
```yaml
deploy-preview:
  runs-on: ubuntu-latest
  needs: [lint, test]
  # CUSTOMIZE: Deploy PR to preview environment
  # Example for Vercel:
  # steps:
  #   - uses: actions/checkout@v4
  #   - run: vercel deploy --token=${{ secrets.VERCEL_TOKEN }} > preview-url.txt
  #   - id: preview
  #     run: echo "url=$(cat preview-url.txt)" >> $GITHUB_OUTPUT
  outputs:
    preview-url: ${{ steps.preview.outputs.url }}
```
- **e2e job** — runs E2E tests AFTER the preview deployment is live:
```yaml
e2e:
  runs-on: ubuntu-latest
  needs: [deploy-preview]
  # CUSTOMIZE: E2E tests against the preview deployment
  # Example for Playwright:
  # steps:
  #   - uses: actions/checkout@v4
  #   - run: npx playwright install --with-deps
  #   - run: BASE_URL=${{ needs.deploy-preview.outputs.preview-url }} npx playwright test
```
- **Trigger:** on push to main + PRs to main

Present the exact workflow YAML and wait for approval.

## Configure

Create the CI workflow file (e.g., `.github/workflows/ci.yml`) using the exact commands established by the linter, type-checker, unit-testing, and pre-commit workflows. Fill in actual commands — do not use placeholders.

If pre-commit hooks are configured, add a pre-commit validation step:

```yaml
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

## Verify

1. Validate the CI workflow YAML is well-formed (run `actionlint` if available)
2. Push a test branch or trigger the CI run
3. Confirm the CI run completes and all jobs pass

The CI must actually run and succeed — not just have valid YAML.

## Docs Update

Update `docs/agents/validation.md` — note CI platform and workflow location:

```markdown
### CI
- Platform: <GitHub Actions / GitLab CI / etc.>
- Workflow: `<path to workflow file>`
- Trigger: push to main, PRs to main
- E2E job runs end-to-end tests after preview deployment (if configured)
```

## Definition of Done

- [ ] CI workflow file exists and is valid YAML
- [ ] CI run triggered and all jobs pass
- [ ] Lint job runs linter, formatter, and type checker
- [ ] Test job runs unit tests
- [ ] Pre-commit hooks are included in CI (if configured)
- [ ] Preview deploy job deploys PR to preview environment (if configured)
- [ ] E2E job runs end-to-end tests against preview deployment (if configured)
- [ ] `docs/agents/validation.md` has CI info
