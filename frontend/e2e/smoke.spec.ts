import { expect, test } from "@playwright/test";

test("homepage loads and shows title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/TanStack/);
});

test("homepage has interactive elements", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("nav")).toBeVisible();
  await expect(page.getByRole("link", { name: /about/i })).toBeVisible();
});

test("navigation to about page works", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: /about/i }).click();
  await expect(page).toHaveURL(/\/about/);
});
