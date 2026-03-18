---
name: deploy-prod
description: Configure production deployment strategy (manual vs auto-on-merge) and deployment targets
dependencies: [ci, staging]
docs:
  - docs/agents/validation.md
  - docs/agents/docs-update.md
---

# Setup: Production Deployment

This workflow depends on ci and staging. If the project is a library with no deployable artifact (determined by local-environment), skip this workflow — note "skipped — library project."

## Detect

Scan for existing production deployment configuration:

- **Deploy workflows:** CI jobs with "deploy", "release", "prod", "production" in filenames or job names that target a non-staging environment
- **Release configs:** `release.config.js`, `.releaserc`, `semantic-release` in package.json, `goreleaser.yml`
- **Platform prod configs:** production-specific Dockerfiles, Kubernetes manifests with `production` namespace/overlay, Helm values-prod files, Terraform workspaces for prod
- **Environment files:** `.env.production`, `PRODUCTION_URL` or `PROD_URL` in any env/CI config
- **Deploy protection:** GitHub environment protection rules, required reviewers, deployment gates in CI
- **GitOps:** ArgoCD Application targeting production, Flux kustomization for prod

Report "configured" if a working production deploy pipeline already exists. Report "not configured" otherwise.

## Propose

Ask the user two questions:

### 1. Deployment trigger

| Option | When It Deploys | Best For |
|--------|----------------|----------|
| **Manual only** | Human clicks "Run workflow" or approves a deploy gate | High-risk services, regulated environments, teams wanting explicit control |
| **Auto on merge to main** | Every merge to main triggers a production deploy | Fast-moving teams, trunk-based development, services with good test coverage |
| **Auto with approval gate** | Merge to main triggers deploy, but pauses for manual approval before applying | Balance of speed and safety — deploy is queued automatically but requires a human click |
| **Release-based** | Deploy triggers on GitHub Release / git tag (`v*`) | Libraries, mobile apps, versioned APIs, teams that batch changes |

### 2. Deployment targets

Ask the user where production lives:

| Target | Examples |
|--------|---------|
| **Cloud platform** | Vercel, Netlify, Render, Railway, Fly.io, Heroku |
| **Container orchestration** | Kubernetes (EKS/GKE/AKS), Docker Swarm, Nomad |
| **Serverless** | AWS Lambda, Google Cloud Functions, Cloudflare Workers |
| **VM/bare metal** | EC2, Droplets, GCE — deploy via SSH/rsync/Ansible |
| **PaaS** | Google App Engine, Azure App Service, Elastic Beanstalk |
| **Custom/other** | User describes their setup |

The proposal must include:
- Which trigger strategy and why it fits
- Which deployment target and how deploys reach it
- What CI workflow(s) will be created or modified
- What rollback looks like (how to revert a bad deploy)
- What secrets/credentials are needed (document, don't create)

Present the proposal and wait for user approval.

## Configure

Based on the chosen trigger and target:

### 1. Create or update deploy workflow

Create `.github/workflows/deploy-prod.yml` (or equivalent for the project's CI platform):

**Manual only:**
```yaml
on:
  workflow_dispatch:
    inputs:
      ref:
        description: 'Git ref to deploy'
        required: true
        default: 'main'
```

**Auto on merge:**
```yaml
on:
  push:
    branches: [main]
```

**Auto with approval gate:**
```yaml
on:
  push:
    branches: [main]
# Uses GitHub Environment with required reviewers
```

**Release-based:**
```yaml
on:
  release:
    types: [published]
```

### 2. Add environment protection (if supported)

- For GitHub: document that a `production` environment should be created in repo settings with required reviewers (if approval gate chosen)
- For GitLab: add `when: manual` to the deploy job (if manual/approval gate chosen)

### 3. Create rollback mechanism

Add a rollback workflow or document the rollback procedure:
- Container-based: redeploy previous image tag
- Platform-based: platform rollback command (e.g., `fly releases rollback`, `vercel rollback`)
- Release-based: create a patch release from the previous tag

### 4. Add deployment status notification (optional)

If the project uses Slack, Discord, or similar — add a deploy notification step to the workflow.

## Verify

1. Validate CI workflow YAML is well-formed (run `actionlint` if available)
2. Confirm all referenced secrets/variables are documented
3. If manual trigger: do a dry-run `workflow_dispatch` or confirm the workflow is visible in the Actions tab
4. If auto trigger: confirm the workflow would trigger on the correct events (check `on:` block)
5. Verify rollback procedure is documented or rollback workflow exists

## Docs Update

Update `docs/agents/validation.md` — add a "Production Deployment" section after the Staging Environment section:

```markdown
### Production Deployment
- **Trigger:** <manual / auto-on-merge / approval-gate / release-based>
- **Target:** <platform/infrastructure description>
- **Deploy workflow:** `<path to workflow file>`
- **Rollback:** `<rollback command or workflow path>`
- **Required secrets:** <list of secrets that must be configured>
- **Production URL:** <URL or how to find it>
```

Update `docs/agents/docs-update.md` — add deployment info to the Docs Structure table:

```markdown
| `docs/runbooks/` | Operational procedures, **deploy & rollback runbooks** | New features requiring ops support, deploy changes |
```

Create `docs/runbooks/deploy-prod.md` with:
- Step-by-step deploy procedure (even if automated — document what happens)
- Rollback procedure
- How to verify a deploy succeeded
- Who to contact if a deploy fails
- Links to monitoring dashboards (reference staging workflow's monitoring if applicable)

## Definition of Done

- [ ] Production deploy workflow file exists and is valid YAML
- [ ] Deploy trigger matches the user's chosen strategy
- [ ] Deploy targets the correct production environment
- [ ] Rollback mechanism is documented or automated
- [ ] All required secrets/variables are documented
- [ ] Environment protection rules are documented (if approval gate chosen)
- [ ] `docs/agents/validation.md` has production deployment info
- [ ] `docs/runbooks/deploy-prod.md` exists with deploy and rollback procedures
- [ ] OR: documented as "skipped — library project" with justification
