import { expect, test } from "@playwright/test";

test("homepage loads and shows Hello World", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /hello world/i })).toBeVisible();
});

test("homepage button triggers alert with 42", async ({ page }) => {
  await page.goto("/");
  const dialogPromise = page.waitForEvent("dialog");
  await page.getByRole("button", { name: /the answer/i }).click();
  const dialog = await dialogPromise;
  expect(dialog.message()).toBe("42");
  await dialog.accept();
});

test("navigation to about page works", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "About", exact: true }).click();
  await expect(page).toHaveURL(/\/about/);
  await expect(page.getByRole("heading", { name: /about/i })).toBeVisible();
});
