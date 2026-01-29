# Playwright End-to-End Testing: Golden Standards and Best Practices (2025-2026)

A comprehensive reference for building scalable, maintainable, and reliable E2E test suites with Playwright. This document is intended to serve as instructions for an AI coding assistant when writing or reviewing Playwright tests.

---

## Table of Contents

1. [Project Structure and Configuration](#1-project-structure-and-configuration)
2. [Page Object Model (POM) Pattern](#2-page-object-model-pom-pattern)
3. [Test Organization and Naming Conventions](#3-test-organization-and-naming-conventions)
4. [Locator Best Practices](#4-locator-best-practices)
5. [Waiting Strategies and Auto-Waiting](#5-waiting-strategies-and-auto-waiting)
6. [Network Mocking and API Interception](#6-network-mocking-and-api-interception)
7. [Authentication Handling](#7-authentication-handling)
8. [Visual Regression Testing](#8-visual-regression-testing)
9. [Accessibility Testing](#9-accessibility-testing)
10. [Cross-Browser Testing Strategies](#10-cross-browser-testing-strategies)
11. [CI/CD Integration](#11-cicd-integration)
12. [Parallelization and Sharding](#12-parallelization-and-sharding)
13. [Fixtures and Test Isolation](#13-fixtures-and-test-isolation)
14. [Reporting and Debugging](#14-reporting-and-debugging)
15. [Mobile and Responsive Testing](#15-mobile-and-responsive-testing)
16. [Performance Testing Considerations](#16-performance-testing-considerations)
17. [Flaky Test Prevention and Retry Strategies](#17-flaky-test-prevention-and-retry-strategies)
18. [Data Management and Test Data Factories](#18-data-management-and-test-data-factories)

---

## 1. Project Structure and Configuration

### Recommended Directory Layout

```
project-root/
├── e2e/
│   ├── tests/                    # Test spec files, grouped by feature
│   │   ├── auth/
│   │   │   ├── login.spec.ts
│   │   │   └── registration.spec.ts
│   │   ├── dashboard/
│   │   │   └── dashboard.spec.ts
│   │   └── settings/
│   │       └── profile.spec.ts
│   ├── pages/                    # Page Object Model classes
│   │   ├── LoginPage.ts
│   │   ├── DashboardPage.ts
│   │   └── BasePage.ts
│   ├── fixtures/                 # Custom test fixtures
│   │   └── test-setup.ts
│   ├── utils/                    # Shared helpers and utilities
│   │   ├── api-helpers.ts
│   │   └── date-utils.ts
│   ├── data/                     # Test data (JSON, CSV, factories)
│   │   ├── users.json
│   │   └── factories/
│   │       └── user-factory.ts
│   └── global-setup.ts          # Global setup (if using setup projects)
├── playwright.config.ts          # Central Playwright configuration
└── tsconfig.json
```

### Key Structural Rules

- **Group tests by feature or domain**, not by test type. For example, `tests/auth/`, `tests/dashboard/`, `tests/settings/`.
- **Separate test logic from page interactions** -- tests go in `tests/`, page objects go in `pages/`.
- **Keep utilities, fixtures, and test data in dedicated directories** so they are easy to find and reuse.
- **Use a single `playwright.config.ts`** at the project root as the central configuration hub.

### Configuration Best Practices

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI
    ? [['blob'], ['github']]
    : [['html', { open: 'never' }]],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },

  projects: [
    { name: 'setup', testMatch: /global-setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },
  ],
});
```

### Configuration Rules

- **Set `fullyParallel: true`** to maximize test distribution across workers and shards.
- **Set `forbidOnly: !!process.env.CI`** to prevent `.only` from accidentally shipping to CI.
- **Set `workers: 1` in CI** for stability; use sharding for parallelism across machines.
- **Set `retries: 2` in CI, `0` locally** to catch flaky tests in pipelines without masking local failures.
- **Use environment variables** for `baseURL`, credentials, and environment-specific settings. Never hardcode secrets.
- **Enable trace, screenshot, and video only on failure or first retry** to save storage and CI time.
- **Use `defineConfig()`** for full type-safety and autocomplete.

---

## 2. Page Object Model (POM) Pattern

### Core Principles

The POM encapsulates page-specific locators and interactions in dedicated classes, separating "how to interact with the UI" from "what the test verifies."

### Implementation Pattern

```typescript
// pages/LoginPage.ts
import { type Locator, type Page } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

```typescript
// tests/auth/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/LoginPage';

test.describe('Login', () => {
  test('should login with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'wrong');
    await expect(loginPage.errorMessage).toBeVisible();
  });
});
```

### POM Rules

- **One class per page or significant component.** A `LoginPage` handles login. A `DashboardPage` handles the dashboard. Do not combine them.
- **Define locators in the constructor** using user-facing selectors (`getByRole`, `getByLabel`, `getByText`). This makes them easy to find and update.
- **Methods should represent user actions**, not DOM operations. Name them `login()`, `createProject()`, `searchFor()` -- not `clickButton()` or `fillInput()`.
- **Do NOT put assertions in page objects.** Page objects encapsulate interactions; tests contain assertions. This keeps page objects reusable across tests with different expected outcomes.
- **Avoid inheritance hierarchies.** Do not create deep `BasePage > AuthenticatedPage > DashboardPage` chains. Use composition -- pass shared components as constructor arguments if needed.
- **Avoid bloated page objects.** If a page object grows beyond ~15 methods, split it into component objects (e.g., `HeaderComponent`, `SidebarComponent`).
- **Page objects can be used as fixtures** for cleaner injection (see Fixtures section).

### Using POM as Fixtures

```typescript
// fixtures/test-setup.ts
import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

type MyFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
};

export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
});

export { expect } from '@playwright/test';
```

---

## 3. Test Organization and Naming Conventions

### File Naming

- **Test files:** `kebab-case.spec.ts` -- e.g., `login.spec.ts`, `create-board.spec.ts`, `user-profile.spec.ts`
- **Page objects:** `PascalCase.ts` -- e.g., `LoginPage.ts`, `DashboardPage.ts`
- **Utilities:** `kebab-case.ts` -- e.g., `api-helpers.ts`, `date-utils.ts`
- **Fixtures:** `kebab-case.ts` -- e.g., `test-setup.ts`, `auth-fixtures.ts`

### Test Naming

Write test titles as behavior descriptions from the user's perspective:

```typescript
// GOOD: Describes user-visible behavior
test('should display error message when login fails', async ({ page }) => {});
test('should redirect to dashboard after successful login', async ({ page }) => {});
test('should allow user to create a new board', async ({ page }) => {});

// BAD: Describes implementation details
test('test login button click handler', async ({ page }) => {});
test('verify DOM element exists', async ({ page }) => {});
```

### Describe Block Organization

```typescript
test.describe('Board Management', () => {
  test.describe('Creating boards', () => {
    test('should create a new board with a title', async ({ page }) => {});
    test('should show validation error for empty title', async ({ page }) => {});
  });

  test.describe('Editing boards', () => {
    test('should rename an existing board', async ({ page }) => {});
    test('should change board background color', async ({ page }) => {});
  });
});
```

### Tags and Annotations

Use tags to categorize tests for selective execution:

```typescript
test('should load dashboard @smoke', async ({ page }) => {});
test('should export report @slow', async ({ page }) => {});

// Or use the structured tag syntax:
test('should process payment', { tag: ['@critical', '@payments'] }, async ({ page }) => {});

// Run tagged tests:
// npx playwright test --grep @smoke
// npx playwright test --grep @critical
```

Recommended tag taxonomy:
- `@smoke` -- fast, critical-path tests run on every PR
- `@regression` -- full regression suite, run nightly or before releases
- `@slow` -- tests known to be slow (triples timeout automatically with `test.slow()`)
- `@critical` -- business-critical paths that must never break
- `@visual` or `@vrt` -- visual regression tests

### Annotations

```typescript
test.skip('should handle edge case', async ({ page }) => {
  // Skip: not implemented yet
});

test.fixme('should handle concurrent edits', async ({ page }) => {
  // Known broken, don't waste CI time running it
});

test('should process large file', async ({ page }) => {
  test.slow(); // Triple the timeout for this test
});

// Add metadata annotations for reporting:
test('should display user profile', {
  annotation: { type: 'issue', description: 'https://github.com/org/repo/issues/123' },
}, async ({ page }) => {});
```

### Structural Rules

- **Group tests by feature**, not by test type. All board-related tests go in `tests/boards/`, not in separate `tests/smoke/` and `tests/regression/` folders.
- **Use tags** (not folder structure) to control which tests run in different contexts (smoke vs. regression).
- **Use `test.step()`** to break complex tests into readable named steps.
- **Avoid conditional logic in tests.** Tests should be deterministic. If you find yourself writing `if/else` in a test, split it into separate tests.
- **Keep tests focused.** Each test should verify one behavior. If a test title contains "and", consider splitting it.

---

## 4. Locator Best Practices

### Priority Hierarchy (Most to Least Preferred)

1. **`page.getByRole()`** -- always try first. Mirrors how users and assistive technologies perceive the page.
2. **`page.getByLabel()`** -- for form controls with associated labels.
3. **`page.getByPlaceholder()`** -- for inputs identified by placeholder text.
4. **`page.getByText()`** -- for elements identified by their visible text content.
5. **`page.getByAltText()`** -- for images and elements with alt text.
6. **`page.getByTitle()`** -- for elements with title attributes.
7. **`page.getByTestId()`** -- fallback when semantic locators are insufficient.

### Examples

```typescript
// BEST: Role-based (mirrors accessibility tree)
page.getByRole('button', { name: 'Submit' });
page.getByRole('heading', { name: 'Welcome' });
page.getByRole('link', { name: 'Sign up' });
page.getByRole('textbox', { name: 'Search' });
page.getByRole('checkbox', { name: 'Remember me' });
page.getByRole('navigation');
page.getByRole('dialog');

// GOOD: Label-based for form controls
page.getByLabel('Email address');
page.getByLabel('Password');
page.getByPlaceholder('Search...');

// GOOD: Text-based for content
page.getByText('Welcome back');
page.getByText(/total: \$\d+/i);  // Regex for dynamic text

// ACCEPTABLE: Test IDs as fallback
page.getByTestId('board-card-42');
page.getByTestId('dropdown-menu');

// BAD: Implementation-coupled selectors (avoid these)
page.locator('.btn-primary');           // CSS class
page.locator('#submit-btn');            // ID (fragile)
page.locator('div > span:nth-child(2)'); // Structure-dependent
page.locator('xpath=//div[@class="x"]'); // XPath (never use)
```

### Chaining and Filtering

```typescript
// Narrow scope by chaining
const productCard = page.getByRole('listitem').filter({ hasText: 'Laptop' });
await productCard.getByRole('button', { name: 'Add to cart' }).click();

// Filter by nested locator
page.getByRole('row').filter({
  has: page.getByRole('cell', { name: 'Active' })
});

// Use .nth() only as last resort
page.getByRole('listitem').nth(0);
```

### data-testid Guidelines

When you must use `data-testid`:
- **Use descriptive, semantic names:** `data-testid="submit-registration-form"` not `data-testid="btn1"`.
- **Use kebab-case:** `data-testid="user-profile-card"`.
- **Only add them when semantic locators genuinely cannot work** (e.g., multiple identical buttons differentiated only by context, or custom canvas/chart elements).
- **Configure custom test ID attribute** in `playwright.config.ts` if your app uses a different convention:

```typescript
use: {
  testIdAttribute: 'data-test',
}
```

### Locator Rules

- **Never use CSS classes, XPath, or deeply nested selectors.** They are brittle and coupled to implementation.
- **Prefer exact matches** where possible: `getByRole('button', { name: 'Submit', exact: true })`.
- **Use `getByRole` first** for every element. Only fall back to other locators if role-based selection is ambiguous.
- **Use web-first assertions** with locators:

```typescript
// CORRECT: Auto-waits and retries
await expect(page.getByRole('alert')).toBeVisible();
await expect(page.getByRole('heading')).toHaveText('Dashboard');

// WRONG: Does not auto-wait, produces flaky tests
expect(await page.getByRole('alert').isVisible()).toBe(true);
```

---

## 5. Waiting Strategies and Auto-Waiting

### Core Principle: Let Playwright Wait for You

Playwright has built-in auto-waiting on every action. When you call `click()`, `fill()`, `check()`, etc., Playwright automatically waits for the element to be:
- Attached to the DOM
- Visible
- Stable (not animating)
- Enabled
- Receiving events (not obscured by other elements)

### Rules

- **Never use `page.waitForTimeout()`** (fixed sleeps). This is the primary cause of flaky and slow tests. There is almost always a better wait condition.
- **Never use manual boolean checks** like `expect(await locator.isVisible()).toBe(true)`. Use web-first assertions instead.
- **Use web-first assertions** -- they auto-retry until the condition is met or timeout expires:

```typescript
// These all auto-wait and retry:
await expect(page.getByRole('heading')).toBeVisible();
await expect(page.getByRole('heading')).toHaveText('Dashboard');
await expect(page.getByRole('list')).toHaveCount(5);
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('My App');
```

- **Use `waitForResponse` or `waitForRequest`** when you need to synchronize with network activity:

```typescript
const responsePromise = page.waitForResponse('**/api/boards');
await page.getByRole('button', { name: 'Load boards' }).click();
const response = await responsePromise;
expect(response.status()).toBe(200);
```

- **Use `waitForLoadState`** only when navigating and you need to ensure a specific load state:

```typescript
await page.goto('/dashboard');
await page.waitForLoadState('networkidle'); // Use sparingly
```

- **Use `locator.waitFor()`** when you need to wait for an element's state without performing an action:

```typescript
await page.getByTestId('loading-spinner').waitFor({ state: 'hidden' });
```

### Anti-Patterns to Avoid

```typescript
// BAD: Fixed sleep
await page.waitForTimeout(3000);

// BAD: Manual polling
while (!(await element.isVisible())) {
  await page.waitForTimeout(100);
}

// BAD: Manual boolean assertion (no auto-wait)
expect(await page.getByText('Success').isVisible()).toBe(true);

// GOOD: Web-first assertion (auto-waits)
await expect(page.getByText('Success')).toBeVisible();
```

---

## 6. Network Mocking and API Interception

### When to Mock

- **Mock external/third-party APIs** you do not control (payment gateways, email services, etc.).
- **Mock error scenarios** (500 errors, timeouts, malformed responses) that are hard to trigger against real servers.
- **Mock data for deterministic tests** when the server data is volatile.
- **Do NOT mock your own application's API** for happy-path E2E tests -- the point of E2E is to test the full stack.

### Basic API Mocking

```typescript
// Mock a specific endpoint
await page.route('**/api/boards', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([
      { id: 1, title: 'Board 1' },
      { id: 2, title: 'Board 2' },
    ]),
  });
});

await page.goto('/dashboard');
```

### Error Scenario Testing

```typescript
await page.route('**/api/boards', async (route) => {
  await route.fulfill({ status: 500, body: 'Internal Server Error' });
});

await page.goto('/dashboard');
await expect(page.getByText('Something went wrong')).toBeVisible();
```

### Request Modification

```typescript
// Add auth header to all API requests
await page.route('**/api/**', async (route) => {
  const headers = {
    ...route.request().headers(),
    'Authorization': 'Bearer test-token',
  };
  await route.continue({ headers });
});
```

### Request Interception for Assertions

```typescript
// Verify the app sends the correct payload
const requestPromise = page.waitForRequest('**/api/boards');
await page.getByRole('button', { name: 'Create board' }).click();
const request = await requestPromise;
expect(request.postDataJSON()).toEqual({ title: 'New Board' });
```

### Blocking Resources

```typescript
// Block images and stylesheets for faster tests
await page.route('**/*.{png,jpg,jpeg,svg,css}', (route) => route.abort());
```

### Rules

- **Register routes BEFORE navigation** (`page.goto`) to ensure early requests are intercepted.
- **Use precise URL patterns.** Avoid overly broad wildcards like `**/*`. Match specific endpoints.
- **Use `context.route()`** for mocks that should apply to all pages in a context. Use `page.route()` for page-specific mocks.
- **Store mock data in separate files** (`data/mocks/boards.json`) to keep tests clean.
- **Do not use MSW (Mock Service Worker) alongside Playwright route mocking** -- MSW's service worker intercepts requests before Playwright can see them.

---

## 7. Authentication Handling

### Recommended Approach: Setup Projects with storageState

The modern best practice is to use **project dependencies** to run authentication once, save the session state, and reuse it across all tests.

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    // Setup project: runs first, performs login
    {
      name: 'setup',
      testMatch: /global-setup\.ts/,
    },
    // Test projects: depend on setup, reuse auth state
    {
      name: 'chromium',
      use: {
        storageState: '.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

```typescript
// e2e/global-setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = '.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL('/dashboard');

  // Save signed-in state
  await page.context().storageState({ path: authFile });
});
```

### API-Based Authentication (Faster)

When possible, authenticate via API instead of UI to save time:

```typescript
setup('authenticate via API', async ({ request }) => {
  const response = await request.post('/api/auth/login', {
    data: { email: 'user@example.com', password: 'password123' },
  });
  expect(response.ok()).toBeTruthy();

  // Save the storage state including cookies from the API response
  await request.storageState({ path: '.auth/user.json' });
});
```

### Multiple Roles

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /global-setup\.ts/ },
    {
      name: 'admin-tests',
      use: { storageState: '.auth/admin.json' },
      dependencies: ['setup'],
    },
    {
      name: 'user-tests',
      use: { storageState: '.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
});
```

```typescript
// global-setup.ts
setup('authenticate as admin', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('admin@example.com');
  await page.getByLabel('Password').fill('admin-pass');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.context().storageState({ path: '.auth/admin.json' });
});

setup('authenticate as user', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('user-pass');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.context().storageState({ path: '.auth/user.json' });
});
```

### Unauthenticated Tests

```typescript
// For tests that should NOT be authenticated:
test.use({ storageState: { cookies: [], origins: [] } });

test('should show login page for unauthenticated users', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveURL('/login');
});
```

### Rules

- **Always use project dependencies** over the legacy `globalSetup` file. Project dependencies produce traces, appear in HTML reports, and support fixtures.
- **Prefer API-based authentication** over UI login flows for speed.
- **Add `.auth/` to `.gitignore`** -- never commit auth state files.
- **Do not log in during every test.** Authenticate once, reuse the session.
- **Use separate storage state files per role** for multi-role testing.

---

## 8. Visual Regression Testing

### Built-in Screenshot Comparison

```typescript
// Full page screenshot comparison
test('should match homepage screenshot', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png');
});

// Element-level screenshot comparison
test('should match header screenshot', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('banner')).toHaveScreenshot('header.png');
});
```

### Handling Dynamic Content

```typescript
test('should match dashboard screenshot', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard.png', {
    // Mask dynamic elements
    mask: [
      page.getByTestId('timestamp'),
      page.getByTestId('avatar'),
      page.getByTestId('random-ad'),
    ],
    // Allow slight pixel differences (anti-aliasing, font rendering)
    maxDiffPixelRatio: 0.01,
  });
});
```

### Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,   // Allow 1% pixel difference
      // OR use absolute pixel count:
      // maxDiffPixels: 100,
      animations: 'disabled',    // Disable CSS animations
      caret: 'hide',             // Hide text cursor
    },
    toMatchSnapshot: {
      maxDiffPixelRatio: 0.01,
    },
  },
  use: {
    // Apply custom stylesheet to hide volatile content during screenshots
    // contextOptions: { reducedMotion: 'reduce' },
  },
});
```

### Rules

- **Run visual tests on a single, controlled environment** (ideally Docker in CI). Screenshot rendering differs across OS, GPU, and font installations.
- **Mask dynamic content** (timestamps, avatars, ads, animations) that changes between runs.
- **Disable animations** with `animations: 'disabled'` to avoid capturing mid-animation frames.
- **Test components, not full pages** when possible -- smaller screenshots produce fewer false positives.
- **Update baselines deliberately:** run `npx playwright test --update-snapshots` only after visually verifying the changes are intentional. Review diffs before committing.
- **Commit baseline screenshots to version control** so the team shares a single source of truth.
- **Use `maxDiffPixelRatio`** rather than `maxDiffPixels` for resolution-independent tolerance.
- **Consider pairing with Storybook** for component-level visual tests with controlled, deterministic data.

---

## 9. Accessibility Testing

### Setup with axe-core

```bash
npm install @axe-core/playwright --save-dev
```

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('should have no accessibility violations on homepage', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('should have no violations on login form', async ({ page }) => {
    await page.goto('/login');

    const results = await new AxeBuilder({ page })
      .include('#login-form')           // Scope to specific area
      .exclude('.third-party-widget')    // Exclude elements you don't control
      .analyze();

    expect(results.violations).toEqual([]);
  });
});
```

### Creating a Reusable Accessibility Fixture

```typescript
// fixtures/test-setup.ts
import { test as base, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

export const test = base.extend({
  makeAxeBuilder: async ({ page }, use) => {
    await use(() =>
      new AxeBuilder({ page }).withTags([
        'wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa',
      ])
    );
  },
});

// Usage in tests:
test('dashboard should be accessible', async ({ page, makeAxeBuilder }) => {
  await page.goto('/dashboard');
  const results = await makeAxeBuilder().analyze();
  expect(results.violations).toEqual([]);
});
```

### Rules

- **Test accessibility on every critical page** -- at minimum, test the pages in your `@smoke` suite.
- **Focus on WCAG 2.1 Level A and AA** using `.withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])`.
- **Use `.exclude()`** for third-party widgets you do not control, but document why they are excluded.
- **Automated tests catch ~30-50% of accessibility issues.** They are a complement to manual testing, not a replacement. Automated tools find missing labels, poor contrast, and duplicate IDs. They cannot test keyboard navigation flow, screen reader comprehension, or cognitive load.
- **Generate HTML reports** using `axe-html-reporter` for human-readable violation summaries.
- **Run accessibility tests in CI** and fail the build on violations (or use `skipFailures` to introduce gradually on legacy apps).
- **Use `getByRole` locators in your functional tests** -- this inherently validates that elements have correct ARIA roles.

---

## 10. Cross-Browser Testing Strategies

### Supported Browsers

Playwright supports three browser engines:
- **Chromium** (Chrome, Edge)
- **Firefox**
- **WebKit** (Safari)

### Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

### Strategies

- **Run all browsers in CI, primarily develop against Chromium locally.** Chromium is the fastest and most commonly used, so it is the best default for local development. Run Firefox and WebKit in CI to catch cross-browser issues.
- **Use device profiles** for consistent viewport, user-agent, and DPR settings across browsers.
- **Same test code across all browsers** -- do not write browser-specific test logic. If a feature behaves differently across browsers, fix the application, not the test.
- **Use `test.skip()` with browser conditions** only for known browser-specific limitations:

```typescript
test('should use clipboard API', async ({ page, browserName }) => {
  test.skip(browserName === 'firefox', 'Clipboard API not supported in Firefox automation');
  // ...
});
```

- **Prioritize based on your user base.** If 90% of your users are on Chrome, run Chromium on every PR, and run Firefox/WebKit nightly or on merge to main.

---

## 11. CI/CD Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
    timeout-minutes: 30
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shardIndex: [1, 2, 3, 4]
        shardTotal: [4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}

      - name: Upload blob report
        if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v4
        with:
          name: blob-report-${{ matrix.shardIndex }}
          path: blob-report
          retention-days: 1

  merge-reports:
    if: ${{ !cancelled() }}
    needs: [e2e-tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci

      - name: Download blob reports
        uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true

      - name: Merge reports
        run: npx playwright merge-reports --reporter html ./all-blob-reports

      - name: Upload HTML report
        uses: actions/upload-artifact@v4
        with:
          name: html-report
          path: playwright-report
          retention-days: 14
```

### CI Rules

- **Run tests on every PR and every push to main.**
- **Use `fail-fast: false`** so all shards complete even if one fails -- you want the full picture.
- **Use the `blob` reporter in CI** for mergeable reports across shards.
- **Upload reports as artifacts** with appropriate retention (1 day for blobs, 14 days for HTML).
- **Install browser dependencies** with `npx playwright install --with-deps`.
- **Set a job timeout** (e.g., 30 minutes) to prevent hung tests from consuming CI resources.
- **Use `!cancelled()`** instead of `always()` for upload steps -- this ensures reports are uploaded even on failure, but not on manual cancellation.
- **Cache npm dependencies** to speed up the install step.
- **Use Docker image `mcr.microsoft.com/playwright:v1.xx.x-jammy`** for consistent, pre-built browser environments (especially important for visual regression tests).

---

## 12. Parallelization and Sharding

### Parallelization (Within a Machine)

- **`fullyParallel: true`** runs tests from the same file in parallel (default is to run files in parallel but tests within a file serially).
- **`workers`** controls how many parallel worker processes run on a single machine.

```typescript
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 1 : undefined,  // 1 worker in CI, auto-detect locally
});
```

### Sharding (Across Machines)

Sharding splits the test suite across multiple CI machines:

```bash
# Machine 1: npx playwright test --shard=1/4
# Machine 2: npx playwright test --shard=2/4
# Machine 3: npx playwright test --shard=3/4
# Machine 4: npx playwright test --shard=4/4
```

### Rules

- **In CI, set `workers: 1` and use sharding for parallelism.** This avoids resource contention on CI machines while still achieving parallelism across machines.
- **Locally, let Playwright auto-detect workers** (leave `workers` undefined or set to `'50%'`).
- **Enable `fullyParallel: true`** for balanced test distribution across shards.
- **Tests MUST be independent** for parallelization to work. No test should depend on state from another test.
- **Start with 4 shards** and adjust based on suite size and CI budget. Monitor shard execution times -- if one shard consistently takes longer, rebalance.
- **Merge shard reports** after all shards complete to get a unified test report.
- **Use `test.describe.configure({ mode: 'serial' })`** only when tests genuinely must run in order (e.g., a create-then-edit-then-delete flow). Avoid serial mode by default.

---

## 13. Fixtures and Test Isolation

### Built-in Fixtures

Playwright provides these built-in fixtures:
- `page` -- an isolated page instance for each test
- `context` -- an isolated browser context for each test
- `browser` -- shared browser instance (for performance)
- `request` -- an API request context for each test

### Custom Fixtures

```typescript
import { test as base } from '@playwright/test';

type MyFixtures = {
  todoPage: TodoPage;
  authenticatedPage: Page;
};

export const test = base.extend<MyFixtures>({
  // Fixture that provides a TodoPage
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await use(todoPage);
    // Cleanup happens after use() returns
  },

  // Fixture that provides an already-authenticated page
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: '.auth/user.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});
```

### Worker-Scoped Fixtures

For expensive resources shared across tests in the same worker:

```typescript
type WorkerFixtures = {
  dbConnection: DatabaseConnection;
};

export const test = base.extend<{}, WorkerFixtures>({
  dbConnection: [async ({}, use) => {
    const db = await createConnection();
    await use(db);
    await db.close();
  }, { scope: 'worker' }],
});
```

### Test Isolation Rules

- **Each test gets a fresh browser context** with its own cookies, local storage, and session storage. This is Playwright's default -- do not fight it.
- **Never share state between tests.** If test B depends on test A creating data, both tests are fragile. Each test should set up its own preconditions.
- **Use `beforeEach` for per-test setup** (e.g., seeding data via API), not `beforeAll`. `beforeAll` runs once for the worker, which can create shared state.
- **Use fixtures for reusable setup/teardown** instead of `beforeEach`/`afterEach` hooks. Fixtures are composable, lazily initialized, and automatically cleaned up.
- **Box frequently used fixtures** to reduce noise in reports:

```typescript
export const test = base.extend({
  todoPage: [async ({ page }, use) => {
    await use(new TodoPage(page));
  }, { box: true }],  // Won't show as a separate step in reports
});
```

---

## 14. Reporting and Debugging

### Reporters Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  reporter: process.env.CI
    ? [
        ['blob'],                    // For merging sharded reports
        ['github'],                  // Annotations in GitHub PR
        ['junit', { outputFile: 'results/junit.xml' }],  // For CI dashboards
      ]
    : [
        ['html', { open: 'never' }], // Local HTML report
        ['list'],                    // Console output
      ],
});
```

### Trace Viewer

The Trace Viewer is the most powerful debugging tool for CI failures. It captures:
- Screenshots at every step
- DOM snapshots
- Network requests and responses
- Console logs
- Action timeline

```typescript
// Enable traces on first retry (recommended default)
use: {
  trace: 'on-first-retry',
}

// For debugging, temporarily enable on all tests:
use: {
  trace: 'on',
}
```

To view traces locally:

```bash
npx playwright show-trace trace.zip
```

Or upload to `trace.playwright.dev` in a browser.

### Debugging Locally

```bash
# Run with Playwright Inspector (step-through debugger)
npx playwright test --debug

# Run with UI Mode (interactive test explorer)
npx playwright test --ui

# Run a specific test in debug mode
npx playwright test login.spec.ts:15 --debug

# Run in headed mode to see the browser
npx playwright test --headed
```

### Programmatic Debugging

```typescript
test('debug this test', async ({ page }) => {
  await page.goto('/');
  await page.pause();  // Opens Inspector at this point
  // Continue debugging interactively...
});
```

### Rules

- **Use `trace: 'on-first-retry'`** as the default. This captures traces only when tests fail and retry, balancing storage cost with debugging value.
- **Use `screenshot: 'only-on-failure'`** and `video: 'on-first-retry'`** for the same reason.
- **For CI failures, use the Trace Viewer** -- it is far more useful than screenshots or videos alone.
- **Use UI Mode locally** for interactive test development and debugging.
- **Use `--debug` flag** for step-through debugging with the Playwright Inspector.
- **Use the `github` reporter in GitHub Actions** for inline PR annotations showing which tests failed and why.
- **Use JUnit reporter** for integration with CI dashboards (Jenkins, Azure DevOps, etc.).
- **Track test health over time** -- identify tests with high flaky rates and prioritize fixing them.

---

## 15. Mobile and Responsive Testing

### Device Emulation

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'Desktop Chrome', use: { ...devices['Desktop Chrome'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 7'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 14'] } },
    { name: 'Tablet', use: { ...devices['iPad Pro 11'] } },
  ],
});
```

### Custom Viewport Testing

```typescript
test.describe('Responsive behavior', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should show mobile menu', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
    await expect(page.getByRole('navigation')).toBeHidden();
  });
});
```

### Touch and Gesture Testing

```typescript
// Device profiles include hasTouch: true
test('should handle swipe gesture', async ({ page }) => {
  await page.goto('/carousel');
  const carousel = page.getByTestId('carousel');

  // Simulate swipe
  await carousel.evaluate((el) => {
    el.dispatchEvent(new TouchEvent('touchstart', {
      touches: [new Touch({ identifier: 0, target: el, clientX: 300, clientY: 200 })],
    }));
    el.dispatchEvent(new TouchEvent('touchend', {
      changedTouches: [new Touch({ identifier: 0, target: el, clientX: 50, clientY: 200 })],
    }));
  });
});

// Or use locator.tap() for touch interactions
await page.getByRole('button', { name: 'Submit' }).tap();
```

### Network Condition Simulation

```typescript
// Simulate slow network
const context = await browser.newContext({
  offline: false,
});
const page = await context.newPage();

// Throttle using CDP (Chromium only)
const client = await page.context().newCDPSession(page);
await client.send('Network.emulateNetworkConditions', {
  offline: false,
  downloadThroughput: (1.5 * 1024 * 1024) / 8, // 1.5 Mbps
  uploadThroughput: (750 * 1024) / 8,            // 750 Kbps
  latency: 40,
});
```

### Rules

- **Test at least three breakpoints:** mobile (375px), tablet (768px), desktop (1280px+).
- **Use Playwright's built-in device profiles** (`devices['iPhone 14']`, `devices['Pixel 7']`) for realistic user-agent, viewport, DPR, and touch settings.
- **Use `locator.tap()`** instead of `locator.click()` for touch-specific interactions.
- **Playwright emulates mobile browsers, it does not test on real devices.** Emulation covers viewport, user-agent, and touch events. For native mobile app testing, use other tools.
- **Tag mobile tests** with `@mobile` and consider running them in a separate CI project to avoid slowing down the primary suite.

---

## 16. Performance Testing Considerations

### What Playwright Can Measure

Playwright is not a performance testing tool, but it can capture useful performance metrics as part of E2E tests:

```typescript
test('should load dashboard within performance budget', async ({ page }) => {
  await page.goto('/dashboard');

  // Capture Web Vitals
  const performanceMetrics = await page.evaluate(() => {
    return JSON.stringify(performance.getEntriesByType('navigation'));
  });

  const metrics = JSON.parse(performanceMetrics);
  const navigationEntry = metrics[0];

  // Assert on performance budgets
  expect(navigationEntry.domContentLoadedEventEnd).toBeLessThan(3000);
  expect(navigationEntry.loadEventEnd).toBeLessThan(5000);
});
```

### Network Request Monitoring

```typescript
test('should not make excessive API calls', async ({ page }) => {
  const apiCalls: string[] = [];

  page.on('request', (request) => {
    if (request.url().includes('/api/')) {
      apiCalls.push(request.url());
    }
  });

  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');

  // Assert reasonable number of API calls
  expect(apiCalls.length).toBeLessThan(20);
});
```

### Bundle Size Monitoring

```typescript
test('should not load excessively large resources', async ({ page }) => {
  const largeResources: { url: string; size: number }[] = [];

  page.on('response', async (response) => {
    const size = (await response.body()).length;
    if (size > 500_000) {  // > 500KB
      largeResources.push({ url: response.url(), size });
    }
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  expect(largeResources).toEqual([]);
});
```

### Rules

- **Playwright is not a substitute for dedicated performance tools** (Lighthouse, k6, WebPageTest). Use it for lightweight performance smoke tests.
- **Set performance budgets** for critical pages (e.g., dashboard must load in < 3s).
- **Monitor resource count and size** to catch performance regressions (e.g., accidentally importing a large library).
- **Run performance-sensitive tests in a consistent environment** (same CI machine type, same network conditions) for meaningful comparisons.
- **Use `page.waitForLoadState('networkidle')` sparingly** -- it is useful for performance measurements but can slow tests.

---

## 17. Flaky Test Prevention and Retry Strategies

### Built-in Anti-Flake Mechanisms

Playwright addresses flakiness through:
1. **Auto-waiting:** every action waits for the element to be actionable.
2. **Web-first assertions:** `expect(locator).toBeVisible()` retries until timeout.
3. **Test isolation:** each test gets a fresh browser context.
4. **Out-of-process execution:** tests run outside the browser process, avoiding in-process timing issues.

### Retry Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,  // Retry twice in CI, never locally
});

// Per-test retry override
test.describe.configure({ retries: 3 });
```

### Common Causes of Flakiness and Solutions

| Cause | Solution |
|-------|----------|
| Fixed timeouts (`waitForTimeout`) | Replace with web-first assertions or `waitFor` |
| Race conditions with network | Use `waitForResponse` or `waitForRequest` |
| Animations causing click misses | Disable animations or wait for stability |
| Shared state between tests | Ensure full test isolation |
| Non-deterministic data | Use seeded/controlled test data |
| Time-dependent behavior | Mock dates/times with `page.clock` |
| Third-party scripts (ads, analytics) | Block them with `page.route` |
| Element not in viewport | Playwright auto-scrolls, but ensure layout is stable |

### Identifying Flaky Tests

```bash
# Run tests multiple times to detect flakiness
npx playwright test --repeat-each=5

# Run only previously failed tests
npx playwright test --last-failed
```

### Rules

- **Fix flaky tests; do not just add retries.** Retries mask problems. Use them as a safety net in CI while you investigate root causes.
- **A test that fails on retry and passes is marked "flaky" in the HTML report.** Monitor these and fix them.
- **Never use `page.waitForTimeout()`** in production tests. If you find yourself needing it, there is a better wait condition.
- **Run `--repeat-each=5` periodically** to proactively detect flaky tests before they erode team confidence.
- **Use `test.slow()`** for genuinely slow tests instead of increasing the global timeout.
- **Use `page.clock`** to mock time-dependent behavior (e.g., countdowns, session expiry).
- **Block third-party scripts** that introduce non-deterministic behavior.

---

## 18. Data Management and Test Data Factories

### Principles

1. **Each test creates the data it needs.** Never depend on shared or pre-existing data.
2. **Use API calls to seed data, not UI interactions.** API seeding is faster and more reliable.
3. **Clean up after tests** when data persists in a shared environment.

### Test Data Factory Pattern

```typescript
// data/factories/user-factory.ts
import { faker } from '@faker-js/faker';

interface UserData {
  email: string;
  password: string;
  name: string;
}

export function createUserData(overrides: Partial<UserData> = {}): UserData {
  return {
    email: faker.internet.email(),
    password: faker.internet.password({ length: 12 }),
    name: faker.person.fullName(),
    ...overrides,
  };
}

// Usage in tests:
test('should register a new user', async ({ page }) => {
  const user = createUserData({ name: 'Test User' });

  await page.goto('/register');
  await page.getByLabel('Name').fill(user.name);
  await page.getByLabel('Email').fill(user.email);
  await page.getByLabel('Password').fill(user.password);
  await page.getByRole('button', { name: 'Register' }).click();

  await expect(page.getByText(`Welcome, ${user.name}`)).toBeVisible();
});
```

### API-Based Data Seeding

```typescript
// data/factories/board-factory.ts
import { APIRequestContext } from '@playwright/test';

export async function createBoard(
  request: APIRequestContext,
  data: { title: string; description?: string }
) {
  const response = await request.post('/api/boards', { data });
  expect(response.ok()).toBeTruthy();
  return response.json();
}

export async function deleteBoard(request: APIRequestContext, boardId: string) {
  await request.delete(`/api/boards/${boardId}`);
}
```

```typescript
// In tests:
test('should display board details', async ({ page, request }) => {
  // Seed data via API
  const board = await createBoard(request, { title: 'Test Board' });

  // Test the UI
  await page.goto(`/boards/${board.id}`);
  await expect(page.getByRole('heading', { name: 'Test Board' })).toBeVisible();

  // Cleanup
  await deleteBoard(request, board.id);
});
```

### Data Seeding via Fixtures

```typescript
// fixtures/test-setup.ts
import { test as base } from '@playwright/test';
import { createBoard, deleteBoard } from '../data/factories/board-factory';

type MyFixtures = {
  testBoard: { id: string; title: string };
};

export const test = base.extend<MyFixtures>({
  testBoard: async ({ request }, use) => {
    // Setup: create board
    const board = await createBoard(request, { title: `Board ${Date.now()}` });
    // Provide to test
    await use(board);
    // Teardown: delete board
    await deleteBoard(request, board.id);
  },
});

// Usage:
test('should rename a board', async ({ page, testBoard }) => {
  await page.goto(`/boards/${testBoard.id}`);
  // testBoard is automatically created before and deleted after this test
});
```

### Data-Driven Testing

```typescript
// data/login-scenarios.json
[
  { "email": "admin@test.com", "password": "admin123", "expectedRole": "admin" },
  { "email": "user@test.com", "password": "user123", "expectedRole": "user" }
]
```

```typescript
import scenarios from '../data/login-scenarios.json';

for (const scenario of scenarios) {
  test(`should login as ${scenario.expectedRole}`, async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(scenario.email);
    await page.getByLabel('Password').fill(scenario.password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByTestId('user-role')).toHaveText(scenario.expectedRole);
  });
}
```

### Rules

- **Never rely on pre-existing database state.** Tests must work on a fresh environment.
- **Use `faker-js`** for generating unique, realistic test data. This prevents collisions in parallel test runs.
- **Seed data via API, not UI.** UI-based data setup is slow and fragile.
- **Use fixtures for data lifecycle management.** The fixture pattern (create in setup, use, delete in teardown) ensures cleanup happens even if the test fails.
- **Separate data definitions from test logic.** Store factories in `data/factories/`, mock data in `data/mocks/`.
- **Use unique identifiers** (timestamps, UUIDs) in generated data names to prevent collisions during parallel execution.
- **Keep mock data minimal and focused.** Only include the fields the test actually needs.

---

## Quick Reference: The Non-Negotiables

These rules should be enforced in every Playwright test without exception:

1. **Use `getByRole` as the primary locator strategy.** Fall back to `getByText`, `getByLabel`, or `getByTestId` only when necessary.
2. **Never use `page.waitForTimeout()`.** Always use web-first assertions or specific wait conditions.
3. **Never use CSS class selectors or XPath.** They are brittle and coupled to implementation.
4. **Each test must be independent.** No test should depend on another test's state or execution order.
5. **Use web-first assertions** (`await expect(locator).toBeVisible()`) instead of manual checks (`expect(await locator.isVisible()).toBe(true)`).
6. **Authenticate once via setup project**, reuse via `storageState`. Do not log in during every test.
7. **Seed test data via API**, not via UI interactions.
8. **Enable traces on first retry** (`trace: 'on-first-retry'`) for debugging CI failures.
9. **Set `forbidOnly: !!process.env.CI`** to prevent `.only()` from reaching CI.
10. **Fix flaky tests.** Do not rely on retries as a permanent solution.

---

## Sources

- [Playwright Official Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Official Docs: Locators](https://playwright.dev/docs/locators)
- [Playwright Official Docs: Page Object Models](https://playwright.dev/docs/pom)
- [Playwright Official Docs: Test Fixtures](https://playwright.dev/docs/test-fixtures)
- [Playwright Official Docs: Authentication](https://playwright.dev/docs/auth)
- [Playwright Official Docs: Network Mocking](https://playwright.dev/docs/network)
- [Playwright Official Docs: Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [Playwright Official Docs: Accessibility Testing](https://playwright.dev/docs/accessibility-testing)
- [Playwright Official Docs: Sharding](https://playwright.dev/docs/test-sharding)
- [Playwright Official Docs: CI Integration](https://playwright.dev/docs/ci)
- [Playwright Official Docs: Trace Viewer](https://playwright.dev/docs/trace-viewer-intro)
- [Playwright Official Docs: Global Setup and Teardown](https://playwright.dev/docs/test-global-setup-teardown)
- [Playwright Official Docs: Annotations](https://playwright.dev/docs/test-annotations)
- [BrowserStack: 15 Best Practices for Playwright Testing in 2026](https://www.browserstack.com/guide/playwright-best-practices)
- [BrowserStack: Page Object Model with Playwright](https://www.browserstack.com/guide/page-object-model-with-playwright)
- [BrowserStack: How to Mock API with Playwright](https://www.browserstack.com/guide/how-to-mock-api-with-playwright)
- [Better Stack: 9 Playwright Best Practices](https://betterstack.com/community/guides/testing/playwright-best-practices/)
- [DeviQA: Guide to Playwright E2E Testing in 2026](https://www.deviqa.com/blog/guide-to-playwright-end-to-end-testing-in-2025/)
- [DEV Community: Organizing Playwright Tests Effectively](https://dev.to/playwright/organizing-playwright-tests-effectively-2hi0)
- [DEV Community: A Better Global Setup with Project Dependencies](https://dev.to/playwright/a-better-global-setup-in-playwright-reusing-login-with-project-dependencies-14)
- [DEV Community: How We Automate Accessibility Testing with Playwright and Axe](https://dev.to/subito/how-we-automate-accessibility-testing-with-playwright-and-axe-3ok5)
- [Momentic: Playwright Locators Guide](https://momentic.ai/blog/playwright-locators-guide)
- [Momentic: The Definitive Guide to Playwright Test Data Management](https://momentic.ai/resources/the-definitive-guide-to-playwright-test-data-management-strategies)
- [Momentic: Playwright Trace Viewer Guide](https://momentic.ai/blog/the-ultimate-guide-to-playwright-trace-viewer-master-time-travel-debugging)
- [Kyrre Gjerstad: CI/CD Best Practices for Playwright](https://www.kyrre.dev/blog/playwright-ci-cd)
- [Currents: Playwright Parallelization](https://docs.currents.dev/guides/ci-optimization/playwright-parallelization)
- [PlaywrightSolutions: Creating a DataFactory for Test Data](https://playwrightsolutions.com/the-definitive-guide-to-api-testcreating-a-datafactory-to-manage-test-data/)
- [Strapi: Data-Driven Testing with Playwright](https://strapi.io/blog/data-driven-testing-with-playwright)
- [ThinksyS: Cross-Browser Testing with Playwright 2025](https://thinksys.com/qa-testing/cross-browser-testing-with-playwright/)
- [Alphabin: Playwright for Mobile Web Testing](https://www.alphabin.co/blog/using-playwright-for-mobile-web-testing)
- [Codoid: Playwright Visual Testing Guide](https://codoid.com/automation-testing/playwright-visual-testing-a-comprehensive-guide-to-ui-regression/)
- [CSS-Tricks: Automated Visual Regression Testing with Playwright](https://css-tricks.com/automated-visual-regression-testing-with-playwright/)
