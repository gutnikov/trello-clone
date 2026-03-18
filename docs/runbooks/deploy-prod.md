# Production Deployment Runbook

## Overview

Production runs on `deploy@2.56.122.47` via Docker Compose.

| Service  | Port | URL                          |
|----------|------|------------------------------|
| Frontend | 3999 | http://2.56.122.47:3999      |
| Backend  | 8999 | http://2.56.122.47:8999      |

## Automatic Deploy

Every merge to `main` triggers `.github/workflows/deploy-prod.yml`:

1. Syncs code to `/home/deploy/production/`
2. Rebuilds and restarts the `production` Docker Compose stack
3. Runs a health check against the backend `/health` endpoint

## Manual Deploy

```bash
ssh deploy@2.56.122.47
cd /home/deploy/production
git pull origin main
BACKEND_PORT=8999 FRONTEND_PORT=3999 docker compose -f docker-compose.staging.yml -p production up -d --build --wait
curl http://localhost:8999/health
```

## Rollback

```bash
ssh deploy@2.56.122.47
cd /home/deploy/production
git log --oneline -5            # Find the commit to roll back to
git checkout <previous-sha>
BACKEND_PORT=8999 FRONTEND_PORT=3999 docker compose -f docker-compose.staging.yml -p production up -d --build --wait
curl http://localhost:8999/health
```

## Verify Deploy Succeeded

```bash
# Health check
curl http://2.56.122.47:8999/health
# Expected: {"status":"ok"}

# Container status
ssh deploy@2.56.122.47 "docker compose -p production ps"

# Logs
ssh deploy@2.56.122.47 "docker compose -p production logs --tail 50"
```

## Staging (PR Previews)

Each PR gets an isolated preview environment:

- **Frontend:** `http://2.56.122.47:400{PR_NUMBER}`
- **Backend:** `http://2.56.122.47:900{PR_NUMBER}`

Preview environments are created by `.github/workflows/deploy-staging.yml` and torn down by `.github/workflows/cleanup-staging.yml` when the PR is closed.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Health check fails after deploy | Check logs: `docker compose -p production logs backend` |
| Port conflict | Verify no other service uses 3999/8999: `ss -tlnp \| grep -E '3999\|8999'` |
| Disk full | Prune Docker: `docker system prune -af --volumes` |
| Runner offline | Check systemd: `systemctl --user status actions.runner.*trello*` |

## Contact

If a deploy fails, check the GitHub Actions run log first, then SSH to the host and inspect Docker logs.
