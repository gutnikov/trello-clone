# Validation Agent Context

## CI-Based Validation

The Validation Agent does NOT run checks locally. Instead, it uses the `check-ci` skill to push the branch, create a draft PR, and poll CI status for results.

### CI Pipeline Requirements

The CI pipeline must include these jobs (configured via `/orca setup ci`):

<!-- CUSTOMIZE: ci-checks -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

### Validation Flow

1. Agent uses `check-ci` skill
2. Skill pushes branch, creates draft PR, polls CI
3. If all CI jobs pass → PR URL written, agent signals done
4. If any CI job fails → validation report written, agent bounces back to Implementing

### Staging Environment

<!-- CUSTOMIZE: staging-env -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

### Production Deployment

<!-- CUSTOMIZE: production-deploy -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

### Validation Report

The `check-ci` skill writes `.orca/validation-report.md` with CI results:

```
# Validation Report: {issue.identifier}

## Summary
PASS / FAIL / ERROR — N of M CI checks passed

## CI Results
- lint: PASS/FAIL
- test: PASS/FAIL
- e2e: PASS/FAIL
- build: PASS/FAIL

## Failures Requiring Fix
- [ ] {job}: {failure summary from CI logs}
```

The Implementation Agent reads this report when bounced back to fix issues.

### What This Agent Must NOT Do

- Do NOT run tests, lint, or type checks locally — CI is the source of truth
- Do NOT modify source code or test files
- Do NOT merge or approve the PR
- If CI infrastructure is broken (not a test failure), signal needs-human
