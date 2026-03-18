---
name: staging
description: Configure staging environment for PR-based deployments
dependencies: [local-environment, ci]
docs:
  - docs/agents/validation.md
  - docs/agents/design-feedback-loop.md
---

# Setup: Staging Environment

This workflow depends on local-environment and ci. If the project is a library with no deployable artifact (determined by local-environment), skip this workflow — note "skipped — library project."

## Detect

Scan for existing staging infrastructure:

- **Deploy configs:** Kubernetes manifests (`k8s/`, `deploy/`), Helm charts (`charts/`), Terraform/Pulumi (`infra/`, `terraform/`, `pulumi/`), `docker-compose.staging.yml`, `fly.toml`, `render.yaml`, Vercel/Netlify project configs
- **CI deploy jobs:** GitHub Actions workflows with "deploy", "staging", "preview" in filenames or job names
- **Platform files:** `vercel.json`, `netlify.toml`, `Procfile`, `app.yaml` (GCP), Dockerfiles with staging variants
- **Environment patterns:** `.env.staging`, `STAGING_URL` in any env file, preview URL patterns in CI outputs
- **PR-based preview configs:** ArgoCD ApplicationSets, Vercel preview deploy settings, namespace-per-PR patterns

Report "configured" if a working staging deploy pipeline already exists. Report "not configured" otherwise.

## Propose

Based on app type:

| App Type | Staging Approach | How |
|----------|-----------------|-----|
| Static/SSR web app (Next.js, Vite, etc.) | Vercel/Netlify preview deploys | Platform-native PR previews |
| Containerized API service | Namespace-per-PR on K8s, or Cloud Run revision per PR | CI builds image, deploys to isolated namespace/revision |
| Docker Compose app (no K8s) | Single staging server, branch-based deploy | CI pushes image, SSH/webhook triggers redeploy |
| Serverless (Lambda, Cloud Functions) | Stage-per-PR or aliased deployments | Framework CLI deploy (SST, Serverless, SAM) |
| Heroku/Fly/Railway/Render | Platform review apps | Platform-native PR-based environments |

The proposal must include:
- Which approach and why it fits this project
- What CI workflow will be created (deploy + teardown)
- What teardown/cleanup looks like (delete preview env on PR close)
- Where the staging URL will be written (`.orca/staging-url`)

Present the proposal and wait for user approval.

## Configure

1. **Create deploy workflow** — `.github/workflows/deploy-staging.yml` (or equivalent) that:
   - Triggers on PR open/synchronize
   - Builds the app
   - Deploys to a PR-specific staging environment
   - Writes the staging URL to a PR comment and to `.orca/staging-url` in the workspace
2. **Create teardown workflow** — cleanup job triggered on PR close/merge that destroys the preview environment
3. **Create/update environment config** — staging-specific env vars, secrets references (document which secrets need to be set, don't create actual secrets)

## Verify

1. Validate CI workflow YAML is well-formed (run `actionlint` if available)
2. Confirm all referenced secrets/variables are documented
3. If possible, do a dry-run deploy or confirm the deploy target is reachable

## Docs Update

Update `docs/agents/validation.md` — replace the `<!-- CUSTOMIZE -->` placeholder in the "Staging Environment" section:

```markdown
### Staging Environment
- **URL source:** `.orca/staging-url` (written by deploy-staging CI job)
- **Logs:** <how to access staging logs>
- **Metrics:** <how to access staging metrics, or "not configured">
- **E2E against staging:** <exact staging e2e command, or "not yet configured">
```

Update `docs/agents/design-feedback-loop.md` — update the staging fields in the "E2E Capabilities" section:

```markdown
- **Staging:** yes
```

## Definition of Done

- [ ] Deploy workflow file exists and is valid YAML
- [ ] Teardown workflow file exists and is valid YAML
- [ ] All required secrets/variables are documented
- [ ] Deploy target is reachable (or dry-run succeeds)
- [ ] `docs/agents/validation.md` has staging environment info
- [ ] `docs/agents/design-feedback-loop.md` has staging capability noted
- [ ] OR: documented as "skipped — library project" with justification
