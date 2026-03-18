import { expect, test } from "@playwright/test";

test("homepage loads and shows Hello World", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /hello world/i })).toBeVisible();
});

test("homepage button triggers alert with 42", async ({ page }) => {
  await page.goto("/");

  // Register a dialog handler that auto-accepts before clicking.
  // alert() blocks JS execution, so the click won't resolve until the dialog is dismissed.
  let dialogMessage = "";
  page.on("dialog", async (dialog) => {
    dialogMessage = dialog.message();
    await dialog.accept();
  });

  await page.getByRole("button", { name: /the answer/i }).click();
  expect(dialogMessage).toBe("42");
});

test("navigation to about page works", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "About", exact: true }).click();
  await expect(page).toHaveURL(/\/about/);
  await expect(page.getByRole("heading", { name: /about/i })).toBeVisible();
});
