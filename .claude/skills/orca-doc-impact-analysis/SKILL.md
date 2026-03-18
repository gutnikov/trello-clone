---
name: orca-doc-impact-analysis
description: >
  Determine which documentation files need updating based on planned or completed code changes.
  Use during Planning state (to predict doc impacts before implementation) and during Docs state
  (to verify doc impacts after implementation). Also use when asked "what docs need updating" or
  "what documentation is affected by this change". Do NOT use for actually writing or updating docs
  — this skill only produces the checklist. Do NOT use for scope analysis (use orca-scope-analysis).
---

# Doc Impact Analysis

Analyze code changes (planned or implemented) and produce a checklist of documentation that needs creating or updating. This checklist becomes the Docs Agent's work queue.

## Why This Matters

Documentation drift is invisible until it causes an agent failure. The doc impact checklist ensures every implementation is accompanied by harness updates — so future agents working in the same codebase have accurate context. Agent context docs (`docs/agents/`) are the highest-value updates because they directly improve future agent performance.

## Step 1: Read the Code Changes

**During Planning state:** Read `docs/plans/{issue.identifier}-plan.md` to understand what will change.

**During Docs state:** Run `git diff main...HEAD` to see actual changes. Also read the plan to compare prediction vs. reality — implementations sometimes diverge from plans, and the checklist should reflect what was actually built.

## Step 2: Check Each Doc Category

For each category, evaluate whether the changes trigger an update. Check `docs/agents/docs-update.md` for any project-specific documentation rules before applying the defaults below.

### Architecture Decision Records (`docs/architecture/`)

**Triggers:**
- New technology, framework, or library added
- Architectural pattern established or changed
- Significant tradeoff made (choosing approach A over B)
- Service boundary introduced or moved
- Data model decision with long-term implications

ADRs document *decisions*, not features. If a feature is implemented in the obvious way with no significant tradeoffs, no ADR is needed.

### API Documentation

**Triggers:**
- New or changed REST endpoints (signatures, responses)
- New or changed GraphQL types, queries, mutations
- New or changed event schemas (queue messages, webhooks)
- Changes to public SDK or library interfaces

### Agent Context Docs (`docs/agents/`)

**Triggers:**
- New coding convention established (error handling pattern, naming convention)
- Build or test commands change
- New subsystem or module introduced (update `scoping.md` boundaries)
- Test framework, locations, or naming conventions change (update `design-feedback-loop.md`)
- Validation commands or criteria change (update `validation.md`)
- Documentation structure or update rules change (update `docs-update.md`)

### Golden Principles (`docs/conventions/golden-principles.md`)

**Triggers:**
- New rule that agents should follow in future issues
- Existing principle violated by this change (principle needs revision)
- Pattern identified as "always do this" or "never do this"

### Runbooks (`docs/runbooks/`)

**Triggers:**
- New feature requiring operational procedures (enable/disable, monitor, rollback)
- Background job or scheduled task added
- New infrastructure dependency (cache, queue, external API)
- Existing operational procedure changed

### Setup / Workflow Guides (`docs/guides/`)

**Triggers:**
- Development environment setup process changes
- New environment variables or secrets required
- Development workflow changes (new commands, new steps)

### Specs (`docs/specs/`)

**Triggers:**
- Implementation diverged from spec significantly
- New constraints or behaviors discovered during implementation
- Acceptance criteria revised

## Step 3: Write the Checklist

Save to `docs/plans/{issue.identifier}-doc-impact.md`:

```markdown
# Doc Impact: {issue.identifier}

## Summary
One paragraph: what changed and the overall doc impact.

## Checklist

- [ ] `docs/architecture/adr-NNN-{title}.md` — CREATE: {why this decision needs recording}
- [ ] `docs/agents/implementation.md` — UPDATE: {what convention changed}
- [ ] `docs/runbooks/{feature-name}.md` — CREATE: {what operational procedure is needed}

## No Impact

The following categories were checked and require no update:
- API docs — no public interface changes
- Specs — implementation matches spec
- Guides — setup process unchanged
```

Each checklist item specifies:
1. The exact file path
2. CREATE or UPDATE
3. A one-sentence reason explaining what needs changing and why

## Guidelines

- **When in doubt, add it.** It's better to check and find no update needed than to miss a required doc update.
- **Document "No Impact" explicitly.** The Docs Agent needs to know you checked a category and found nothing — otherwise it can't tell if you forgot.
- **The checklist is a living document.** During Docs state, the Docs Agent may add items discovered from the actual git diff that weren't predicted during Planning.
- **Agent context docs are the priority.** These directly affect how future agents operate. A stale `scoping.md` with wrong subsystem boundaries causes bad scope scores on every subsequent issue.
