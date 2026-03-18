---
name: task-management
description: Configure task tracker backend (Linear or Jira)
dependencies: []
docs:
  - docs/agents/implementation.md
---

# Setup: Task Management

## Detect

Read `WORKFLOW.md` front matter for the `tracker:` section:

```yaml
tracker:
  kind: linear   # or jira
  api_key: $LINEAR_API_KEY   # or $JIRA_API_TOKEN
  project_slug: my-project   # Linear team key or Jira project key
  endpoint: https://api.linear.app/graphql  # or https://myco.atlassian.net
```

Report status:
- **configured** if `tracker.kind` is set and `tracker.api_key` resolves to a non-empty value
- **not configured** if `tracker.kind` is empty or missing

## Propose

If not configured, ask the user to choose a tracker:

> Which task tracker does this project use?
>
> 1. **Linear** — GraphQL API
> 2. **Jira Cloud** — REST API v3
>
> Choose [1/2]:

Present the required configuration for the chosen tracker.

## Configure

### Linear

Collect:
1. **API key:** Personal API key from Linear Settings → API → Personal API keys. Store as `$LINEAR_API_KEY` environment variable.
2. **Team key:** The URL slug for the Linear team (e.g., `my-project` from `linear.app/my-project/...`)
3. **Endpoint:** Default `https://api.linear.app/graphql` (only change for self-hosted)

### Jira Cloud

Collect:
1. **Instance URL:** e.g., `https://mycompany.atlassian.net`
2. **Email:** The Atlassian account email for API authentication
3. **API token:** From https://id.atlassian.com/manage-profile/security/api-tokens. Store as environment variable.
4. **Project key:** The Jira project key (e.g., `PROJ` from `PROJ-123` issue keys)

The setup workflow base64-encodes `email:token` and stores the result as `$JIRA_API_TOKEN`.

Write the `tracker:` section to `WORKFLOW.md`:

```yaml
# Linear example:
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: my-project

# Jira example:
tracker:
  kind: jira
  api_key: $JIRA_API_TOKEN
  project_slug: PROJ
  endpoint: https://mycompany.atlassian.net
```

## Verify

Round-trip API test to confirm credentials and project access:

### Linear
1. `python3 -c "..."` — call `get_team_id()` with the configured credentials
2. Verify a team ID is returned (non-empty string)
3. Fetch one issue (limit 1) to confirm read access

### Jira
1. `GET /rest/api/3/project/{key}` — verify project exists and is accessible
2. `GET /rest/api/3/search?jql=project={key}&maxResults=1` — verify issue read access
3. Both must return HTTP 200

All steps must succeed. Report the project name and issue count on success.

## Docs Update

Add a "Task Management" section to `docs/agents/implementation.md`:

```markdown
### Task Management
- **Tracker:** Linear / Jira Cloud
- **Project:** {project_slug}
- **Active states:** {active_states list}
- **Terminal states:** {terminal_states list}
- **API endpoint:** {endpoint}
```

## Definition of Done

- [ ] `tracker.kind` is set in WORKFLOW.md (`linear` or `jira`)
- [ ] `tracker.api_key` resolves to a non-empty value from environment
- [ ] `tracker.project_slug` is set and valid
- [ ] `tracker.endpoint` is set (Jira only — must not be the Linear default)
- [ ] Round-trip API test passed (project lookup + issue fetch)
- [ ] `docs/agents/implementation.md` has Task Management section
