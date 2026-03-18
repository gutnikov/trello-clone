---
name: local-environment
description: Configure local development environment
dependencies: [package-management]
docs:
  - docs/agents/implementation.md
---

# Setup: Local Test Environment

## Detect

Check for existing local dev environment setup:

- `docker-compose.yml` or `compose.yml`
- `Dockerfile`
- `Makefile` with `dev`, `up`, or `serve` targets
- `scripts/dev.sh` or similar
- `package.json` scripts: `dev`, `start`, `serve`
- `.env.example`

Report "configured" if a working local dev setup exists. Report "not configured" otherwise.

## Propose

Analyze what the application needs:

1. **Service with dependencies** (DB, cache, queue, etc.): propose `docker-compose.yml` for dependencies + a dev server script
2. **Standalone service** (no external deps): propose a run script or Makefile target
3. **Library** (no runnable app): the test suite is the test environment — note this and skip

Present the specific files you'll create and wait for approval.

## Configure

Create the approved files. For a typical service with dependencies:

1. `docker-compose.yml` — with only the service dependencies (not the app itself)
2. `scripts/dev.sh` or Makefile target — starts dependencies, then starts the app
3. `.env.example` — template for required environment variables

## Verify

1. Start the local environment using the created scripts
2. Confirm the app responds (health check endpoint, port open, or process running)
3. Shut down the environment cleanly

## Docs Update

Update `docs/agents/implementation.md` — add to the Build & Run section in the `<!-- CUSTOMIZE -->` area:

```markdown
### Build & Run
- `<install command>` — install dependencies
- `<local env start command>` — start dev environment
```

## Definition of Done

- [ ] Local dev environment start command works and app responds
- [ ] Environment shuts down cleanly
- [ ] `docs/agents/implementation.md` has start/stop commands
- [ ] OR: documented as "skipped — library project" with justification
