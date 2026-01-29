---
name: e2e-testing
description: End-to-end testing with Playwright. Use when writing Playwright tests, page objects, test fixtures, configuring playwright.config.ts, setting up CI pipelines for E2E tests, or debugging test failures.
---

# Playwright E2E Testing

Apply Playwright best practices when writing or reviewing end-to-end tests.

## Key Standards

- **Locators**: `getByRole` first, then `getByText`/`getByLabel`, `getByTestId` as last resort. Never use CSS selectors or XPath.
- **Waiting**: Use web-first assertions (`await expect(locator).toBeVisible()`). Never use `page.waitForTimeout()`.
- **Page Objects**: Encapsulate page interactions in POM classes. Use as fixtures, not instantiated in tests.
- **Test Isolation**: Each test gets a fresh browser context. No test depends on another test's state.
- **Auth**: Use setup projects with `storageState` for authentication. Authenticate via API, not UI.
- **Data**: Seed test data via API calls, not UI interactions. Use factory functions with faker-js.
- **Network**: Mock external APIs with `page.route()`. Test error scenarios and loading states.
- **Visual Testing**: Use `toHaveScreenshot()` with masking for dynamic content.
- **Accessibility**: Integrate `@axe-core/playwright` for automated WCAG checks.
- **CI**: Shard tests across machines, use blob reporter, merge reports, enable traces on first retry.

## When writing tests, follow these principles

1. Use `getByRole` as the primary locator strategy
2. Never use `page.waitForTimeout()` -- always use web-first assertions
3. Each test must create its own data via API and clean up after itself
4. Use fixtures for reusable setup/teardown instead of `beforeEach`/`afterEach`
5. Tag tests with `@smoke`, `@regression`, `@critical` for selective CI runs
6. Set `retries: 2` in CI, `0` locally. Fix flaky tests -- do not rely on retries.
7. Use Trace Viewer for debugging CI failures, not screenshots

## Detailed reference

For complete patterns, code examples, and configurations, see [reference.md](reference.md).
