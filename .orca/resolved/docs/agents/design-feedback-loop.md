# Design Feedback Loop Agent Context (Test Scaffolding)

## Testing Philosophy

This agent writes **fail-first tests** (TDD). Tests are written BEFORE implementation code exists. They MUST fail when first created — this verifies they actually test something.

## Test Structure

<!-- CUSTOMIZE: test-framework -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

## E2E Capabilities

<!-- CUSTOMIZE: e2e-testing -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

## Fail-First Verification

After writing each test file, run the test suite and verify:
1. New tests are discovered by the test runner
2. New tests FAIL (not error — they should fail with assertion errors, not import errors)
3. The failure message clearly describes what's expected

If tests pass immediately, something is wrong — the test likely doesn't test real behavior.

## What This Agent Must NOT Do

- Do NOT write implementation code
- Do NOT create stubs or mock implementations that make tests pass
- Do NOT modify existing passing tests
- Only create test files and test fixtures/helpers
