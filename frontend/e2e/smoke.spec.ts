import { expect, test } from "@playwright/test";

test("homepage loads and shows heading", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /organize your work/i })).toBeVisible();
});

test("homepage shows feature cards", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Kanban Boards")).toBeVisible();
  await expect(page.getByText("Real-time Updates")).toBeVisible();
});

test("navigation to about page works", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "About", exact: true }).click();
  await expect(page).toHaveURL(/\/about/);
  await expect(page.getByRole("heading", { name: /about/i })).toBeVisible();
});
