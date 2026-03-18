---
name: orca-design-feedback-loop
description: >
  Design the full verification strategy (tests + observability) for a feature and produce a
  feedback loop plan. Use when the Planning Agent needs to define how a feature will be verified
  before implementation begins. Also use when asked to design a testing strategy or observability
  plan for a change. Do NOT use for writing actual test code (that's the Design Feedback Loop
  Agent's job using the plan this skill produces). Do NOT use for scope analysis (use
  scope-analysis instead).
---

# Design Feedback Loop

Design the verification strategy for a feature: what tests are needed at each level, what observability to add, and how to confirm correctness in production. The output is a plan that the Design Feedback Loop Agent uses to write fail-first test scaffolds.

## Why This Matters

This plan is the contract between the Planning Agent and the Design Feedback Loop Agent. If the plan is vague ("add unit tests"), the test scaffolds will be vague too, and bugs will slip through. Specific test case names with clear expectations produce useful tests.

A feedback_completeness_score below 6 blocks the pipeline — the feature isn't safe to implement without adequate verification coverage.

## Step 1: Understand What's Being Built

Read the implementation plan at `docs/plans/{issue.identifier}-plan.md`. Identify:
- What new behavior is being introduced
- Which files and functions are changing or being created
- What the acceptance criteria are

## Step 1.5: Check E2E Capabilities

Read `docs/agents/design-feedback-loop.md` — look for the "E2E Capabilities" section. If it exists and shows `Available: yes` and `Staging: yes`, e2e infrastructure is ready. Note this for Step 8.

If the section is absent or still contains the `<!-- CUSTOMIZE -->` placeholder, e2e infrastructure is not set up — e2e tests remain optional in scoring.

## Step 2: Study Existing Test Patterns

Before designing new tests, look at how the project already tests things:

1. Read `docs/agents/design-feedback-loop.md` for project-specific conventions (framework, file layout, naming)
2. Look at a few existing test files to understand the patterns in use — imports, fixtures, assertion style, directory structure

Test case names in the plan should match the conventions you find. If the project uses pytest, name tests `test_function_scenario`. If it uses jest, name them `describe/it` blocks. The Design Feedback Loop Agent will use these names directly.

## Step 3: Design Unit Tests

For each function, class, or module being created or modified, specify:

- What behavior to test (pure logic, transformations, validation, error handling)
- What inputs produce what expected outputs
- What edge cases exist (empty input, boundary values, concurrent access)

Be specific — name each test case and describe what it verifies:

```
### {Module or Function Name}
- `test_parse_config_returns_defaults_for_empty_input` — verifies fallback behavior
- `test_parse_config_raises_on_missing_required_field` — verifies validation
- `test_parse_config_expands_env_vars` — verifies $VAR substitution
```

## Step 4: Design Integration Tests

For each boundary between components (service-to-service, code-to-database, code-to-external-API):

- What two components interact and what's the contract between them
- What infrastructure the test needs (test DB, mock service, fixture data)
- What failure modes to test (timeout, invalid response, connection refused)

If the feature doesn't cross component boundaries, note that integration tests are N/A and why.

## Step 5: Design E2E Tests

For each user-facing behavior being introduced or changed:

- What is the user action sequence (navigate, fill form, submit, verify result)
- What does the user see on success and on failure
- What browser/environment conditions matter (if applicable)

If the feature has no user-facing component (internal service, background job, CLI tool), note E2E as N/A.

## Step 6: Design Observability

Consider what the team needs to know when this feature runs in production:

- **Logs**: What events to log, with what structured fields, at what level
- **Metrics**: What counters, histograms, or gauges help monitor the feature's health
- **Traces**: What spans to add for distributed tracing (if the project uses tracing)

Not every feature needs all three. A small internal utility might only need error logging. A new API endpoint probably needs all three. Match the observability depth to the feature's production impact.

If the project doesn't have observability infrastructure set up, note this and skip.

## Step 7: Design Runtime Validation

What checks can verify the feature works correctly after deployment?

- Smoke tests run post-deploy
- Synthetic checks (periodic automated requests)
- Health check endpoints or metrics

This is often N/A for small features or projects without deployment infrastructure. Note why if skipping.

## Step 8: Calculate Feedback Completeness Score

| Method | Points | Criteria for "defined" |
|--------|--------|----------------------|
| Unit tests | 3 | Specific test cases named with what each verifies |
| Integration tests | 2 | Specific test cases with infrastructure requirements |
| E2E tests | 2 | Specific user flows with expected outcomes |
| Observability | 2 | Specific log events, metrics, or trace spans identified |
| Runtime validation | 1 | Specific post-deploy checks described |
| **Maximum** | **10** | |

A method scored 0 can be either "not defined" or "N/A with justification." Both are valid, but the total must reach at least 6.

**Mandatory e2e rule:** If ALL of the following are true, e2e tests are mandatory — scoring 0 for e2e blocks the pipeline regardless of total score:

1. The "E2E Capabilities" section in `docs/agents/design-feedback-loop.md` shows `Available: yes` and `Staging: yes`
2. The implementation plan's "User-Facing" field is "yes"

If e2e is mandatory but you cannot define meaningful e2e tests, do not save the plan. Instead, document why e2e tests cannot be defined and let the Planning Agent decide whether to escalate via `needs-human`.

**If score < 6:** Don't save. Add more coverage until the threshold is met. If you genuinely can't reach 6 (e.g., a trivial config change), document why and let the Planning Agent decide whether to escalate.

## Step 9: Save the Plan

Save to `docs/feedback-loops/{issue.identifier}-feedback.md`:

```markdown
# Feedback Loop Plan: {issue.identifier}

## Feedback Completeness Score: X/10

| Method | Score | Notes |
|--------|-------|-------|
| Unit tests | 3 | {N test cases defined} |
| Integration tests | 2 | {N test cases defined} |
| E2E tests | 0 | N/A — {reason} |
| Observability | 2 | {what's covered} |
| Runtime validation | 1 | {what's covered} |
| **Total** | **X** | |

## Unit Tests

### {Module or Function Name}
- `test_case_name` — what it verifies
- `test_case_name` — what it verifies

## Integration Tests

### {Boundary}
- `test_case_name` — what it verifies, infrastructure needed

## E2E Tests

{Test cases or "N/A — {reason}"}

## Observability

### Logs
- {event} at {level} with fields: {field_list}

### Metrics
- `{metric_name}` ({type}) — what it measures

### Traces
- {span description, or "N/A"}

## Runtime Validation

{Checks or "N/A — {reason}"}
```

## Guidelines

- **Name test cases concretely.** The Design Feedback Loop Agent reads this plan and creates test files from it. `test_handles_edge_cases` tells it nothing. `test_parse_raises_value_error_for_negative_timeout` tells it exactly what to write.
- **Match the project's conventions.** Use the test framework, directory layout, and naming patterns already established in the codebase.
- **"N/A" is valid but must be justified.** Skipping a verification method is fine when it genuinely doesn't apply — just say why so reviewers know it was a conscious choice, not an oversight.
- **Observability scales with production impact.** A new public API endpoint needs metrics and logging. A refactored internal helper probably doesn't.
