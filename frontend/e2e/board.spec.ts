/**
 * TRE-40: E2E tests for /board route and read-only display components.
 *
 * These tests verify that the /board route is accessible and renders
 * board data correctly, including lists, cards, and empty state.
 *
 * Tests that require lists/cards seed their own data via the API
 * and clean up afterwards to maintain test isolation.
 */
import { expect, test } from "@playwright/test";

test.describe("Board page", () => {
  test("board page loads at /board", async ({ page }) => {
    const response = await page.goto("/board");

    // The route should not return a 404
    expect(response?.status(), "Board page should not return 404").not.toBe(404);
  });

  test("board page displays board title", async ({ page }) => {
    await page.goto("/board");

    // The board title should be visible somewhere on the page
    const heading = page.getByRole("heading");
    await expect(
      heading.first(),
      "Board page should display a heading with the board title",
    ).toBeVisible();
  });

  test("board page displays lists when board has lists", async ({ page }) => {
    // Seed a list via the API so the board has data to display
    const boardRes = await page.request.get("/api/board");
    const board = await boardRes.json();
    const listRes = await page.request.post("/api/lists", {
      data: { title: "E2E Test List", board_id: board.id },
    });
    const list = await listRes.json();

    try {
      await page.goto("/board");

      // Wait for board data to load — look for any list column element
      const listColumn = page.locator("[data-testid='board-list']");
      await expect(
        listColumn.first(),
        "Board page should display at least one list when the board has lists",
      ).toBeVisible({ timeout: 10000 });
    } finally {
      // Clean up: delete the test list
      await page.request.delete(`/api/lists/${list.id}`);
    }
  });

  test("board page displays cards within lists", async ({ page }) => {
    // Seed a list and card via the API so the board has data to display
    const boardRes = await page.request.get("/api/board");
    const board = await boardRes.json();
    const listRes = await page.request.post("/api/lists", {
      data: { title: "E2E Test List for Cards", board_id: board.id },
    });
    const list = await listRes.json();
    const cardRes = await page.request.post("/api/cards", {
      data: { title: "E2E Test Card", list_id: list.id },
    });
    const card = await cardRes.json();

    try {
      await page.goto("/board");

      // Wait for board data to load — look for card elements inside lists
      const cardElement = page.locator("[data-testid='board-card']");
      await expect(
        cardElement.first(),
        "Board page should display cards within lists",
      ).toBeVisible({ timeout: 10000 });
    } finally {
      // Clean up: delete the test card and list
      await page.request.delete(`/api/cards/${card.id}`);
      await page.request.delete(`/api/lists/${list.id}`);
    }
  });

  test("board page shows empty state when no lists exist", async ({ page }) => {
    // This test assumes the board starts empty or can be made empty
    // The empty state component should show a message about creating lists
    await page.goto("/board");

    // If the board has no lists, it should show the empty state
    // We check for the presence of either lists or the empty state message
    const hasLists = await page
      .locator("[data-testid='board-list']")
      .first()
      .isVisible()
      .catch(() => false);

    if (!hasLists) {
      // Should show empty state when no lists exist
      const emptyState = page.locator("[data-testid='empty-board']");
      await expect(
        emptyState,
        "Board page should show empty state when no lists exist",
      ).toBeVisible({ timeout: 5000 });
    }
  });
});
