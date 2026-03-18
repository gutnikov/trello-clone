# Planning Agent Context

## Implementation Plan Format

All implementation plans must be saved to `docs/plans/{issue.identifier}-plan.md` and follow this structure:

```
# Implementation Plan: {issue.identifier}

## Goal
One sentence describing what this implements.

## User-Facing
yes / no — Does this issue introduce or change behavior visible to end users?

## Files to Change
- `path/to/file.ext` — what changes and why

## Steps
1. Step description (specific, actionable)
2. Step description
...

## Risks
- Risk description and mitigation

## Dependencies
- Any blockers or ordering constraints
```

## Feedback Loop Plan Format

All feedback loop plans must be saved to `docs/feedback-loops/{issue.identifier}-feedback.md`:

```
# Feedback Loop Plan: {issue.identifier}

## Unit Tests
- What to test, which modules, expected behavior

## Integration Tests
- Which service boundaries to test

## E2E Tests
- User flows to validate (describe headless browser scenarios if applicable)

## Observability
- Logs: what events to log, structured fields
- Metrics: what to measure
- Traces: what spans to add

## Runtime Validation
- Synthetic checks or smoke tests for production
```

## Doc Impact Checklist Format

Save to `docs/plans/{issue.identifier}-doc-impact.md`:

```
# Doc Impact: {issue.identifier}

## Docs to Update
- [ ] `docs/architecture/adr-NNN.md` — new ADR needed because...
- [ ] `docs/agents/implementation.md` — new convention added
- [ ] `docs/conventions/golden-principles.md` — new principle needed

## Docs to Create
- [ ] `docs/runbooks/feature-name.md` — operational runbook for new feature
```

<!-- CUSTOMIZE: planning-conventions -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->
