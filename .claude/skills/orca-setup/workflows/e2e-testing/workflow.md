---
name: e2e-testing
description: Configure E2E test framework with staging support
dependencies: [unit-testing, staging]
docs:
  - docs/agents/validation.md
  - docs/agents/design-feedback-loop.md
---

# Setup: E2E Test Framework

This workflow depends on unit-testing and staging. If the project is a library (no local test environment), E2E reduces to integration tests within the unit test framework — no separate tool needed.

## Detect

Check for existing E2E/integration test setup:

- `playwright.config.*`, `cypress.config.*`
- E2E test directories: `e2e/`, `tests/e2e/`, `tests/integration/`
- Integration test files in the existing test directory

Report "configured" if E2E or integration tests are already configured. Report "not configured" otherwise.

## Propose

Based on app type:

| App Type | E2E Approach | Tool |
|----------|-------------|------|
| Web app with UI | Browser-based E2E | Playwright |
| API service | HTTP integration tests | pytest + httpx / supertest / etc. |
| CLI tool | Shell integration tests | bats or shell scripts |
| Library | Integration tests in unit framework | Same as unit-testing |

If a staging environment was configured, also propose a **staging e2e mode**:
- E2E tests accept a `BASE_URL` environment variable (defaulting to `http://localhost:<port>` for local runs)
- A CI step in the deploy-staging workflow runs e2e tests against the staging URL after deployment succeeds
- This staging e2e run is the authoritative validation — local e2e is for fast iteration

Present the proposal and wait for approval.

## Configure

1. Install the E2E framework (if separate from unit test framework)
2. Create config file
3. Create a single smoke E2E test that verifies the happy path
4. Configure the e2e framework to read `BASE_URL` from the environment, defaulting to localhost
5. Add an e2e step to the deploy-staging workflow (`.github/workflows/deploy-staging.yml`) that runs after deploy completes, passing the staging URL as `BASE_URL`

## Verify

1. Start the local environment
2. Run the smoke E2E test locally — must pass and exit 0
3. If staging is configured, verify the CI e2e step is properly added to the deploy workflow
4. Shut down

## Docs Update

Update `docs/agents/validation.md` — add e2e command to the "Required Checks" `<!-- CUSTOMIZE -->` section:

```markdown
6. **Integration/E2E tests:** `<exact e2e command>`
```

Update `docs/agents/design-feedback-loop.md` — replace the `<!-- CUSTOMIZE -->` placeholder in the "E2E Capabilities" section:

```markdown
### E2E Capabilities
- **Available:** yes
- **Framework:** <framework name>
- **Staging:** yes / no
- **Run locally:** `<local e2e command>`
- **Run against staging:** `<staging e2e command with BASE_URL>`
```

Also update the "Test Structure" section with integration/E2E test info:

```markdown
### Integration Tests
- Location: `<integration test directory>`
- Framework: <framework>
- Run: `<exact integration test command>`

### E2E Tests
- Location: `<e2e test directory>`
- Framework: <framework>
- Run: `<exact e2e command>`
```

## Definition of Done

- [ ] E2E framework is installed (or using unit test framework for integration tests)
- [ ] E2E config file exists
- [ ] Smoke E2E test exists, runs locally, and passes
- [ ] E2E tests accept `BASE_URL` env var for staging support
- [ ] CI e2e step added to deploy-staging workflow (if staging configured)
- [ ] `docs/agents/validation.md` has e2e test command
- [ ] `docs/agents/design-feedback-loop.md` has E2E Capabilities and Test Structure info
- [ ] OR: documented as "skipped — using integration tests in unit framework" with justification
