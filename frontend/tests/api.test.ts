/**
 * TRE-39: Fail-first tests for frontend API client module (src/lib/api.ts)
 *
 * These tests verify that the API client exports typed functions for every
 * backend endpoint and that each function calls fetch with the correct
 * HTTP method, URL, headers, and body.
 *
 * All tests are expected to FAIL until the implementation is written.
 */
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import * as api from "@/lib/api";

// ── Helpers ────────────────────────────────────────────────────────────────

/** Create a mock fetch that returns a successful JSON response */
function mockFetch(body: unknown, status = 200) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  });
}

// ── Function Export Tests ──────────────────────────────────────────────────

describe("API client function exports", () => {
  it("exports getBoard as a function", () => {
    expect(api.getBoard).toBeDefined();
    expect(typeof api.getBoard).toBe("function");
  });

  it("exports updateBoard as a function", () => {
    expect(api.updateBoard).toBeDefined();
    expect(typeof api.updateBoard).toBe("function");
  });

  it("exports createList as a function", () => {
    expect(api.createList).toBeDefined();
    expect(typeof api.createList).toBe("function");
  });

  it("exports updateList as a function", () => {
    expect(api.updateList).toBeDefined();
    expect(typeof api.updateList).toBe("function");
  });

  it("exports deleteList as a function", () => {
    expect(api.deleteList).toBeDefined();
    expect(typeof api.deleteList).toBe("function");
  });

  it("exports reorderLists as a function", () => {
    expect(api.reorderLists).toBeDefined();
    expect(typeof api.reorderLists).toBe("function");
  });

  it("exports createCard as a function", () => {
    expect(api.createCard).toBeDefined();
    expect(typeof api.createCard).toBe("function");
  });

  it("exports updateCard as a function", () => {
    expect(api.updateCard).toBeDefined();
    expect(typeof api.updateCard).toBe("function");
  });

  it("exports deleteCard as a function", () => {
    expect(api.deleteCard).toBeDefined();
    expect(typeof api.deleteCard).toBe("function");
  });

  it("exports moveCard as a function", () => {
    expect(api.moveCard).toBeDefined();
    expect(typeof api.moveCard).toBe("function");
  });
});

// ── Fetch Behavior Tests ───────────────────────────────────────────────────

describe("API client fetch behavior", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    globalThis.fetch = mockFetch({});
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("getBoard calls GET /api/board", async () => {
    const boardResponse = { id: "b1", title: "My Board", lists: [] };
    globalThis.fetch = mockFetch(boardResponse);

    expect(api.getBoard, "getBoard must be exported as a function").toBeTypeOf("function");

    await api.getBoard();

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/board"),
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("getBoard returns typed BoardDetailResponse", async () => {
    const boardResponse = {
      id: "b1",
      title: "My Board",
      lists: [
        {
          id: "l1",
          title: "Todo",
          position: 0,
          cards: [{ id: "c1", title: "Task 1", position: 0 }],
        },
      ],
    };
    globalThis.fetch = mockFetch(boardResponse);

    expect(api.getBoard, "getBoard must be exported as a function").toBeTypeOf("function");

    const result = await api.getBoard();

    expect(result, "getBoard should return the parsed board response").toEqual(boardResponse);
    expect(result.id).toBe("b1");
    expect(result.title).toBe("My Board");
    expect(result.lists).toHaveLength(1);
    expect(result.lists[0].cards).toHaveLength(1);
  });

  it("updateBoard calls PUT /api/board with JSON body", async () => {
    const updated = { id: "b1", title: "Updated Board" };
    globalThis.fetch = mockFetch(updated);

    expect(api.updateBoard, "updateBoard must be exported as a function").toBeTypeOf("function");

    await api.updateBoard({ title: "Updated Board" });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/board"),
      expect.objectContaining({
        method: "PUT",
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
        body: JSON.stringify({ title: "Updated Board" }),
      }),
    );
  });

  it("createList calls POST /api/lists with JSON body", async () => {
    const created = { id: "l1", title: "New List", board_id: "b1", position: 0 };
    globalThis.fetch = mockFetch(created, 201);

    expect(api.createList, "createList must be exported as a function").toBeTypeOf("function");

    await api.createList({ title: "New List", board_id: "b1" });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/lists"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ title: "New List", board_id: "b1" }),
      }),
    );
  });

  it("updateList calls PUT /api/lists/{id} with JSON body", async () => {
    const updated = { id: "l1", title: "Renamed", board_id: "b1", position: 0 };
    globalThis.fetch = mockFetch(updated);

    expect(api.updateList, "updateList must be exported as a function").toBeTypeOf("function");

    await api.updateList("l1", { title: "Renamed" });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/lists/l1"),
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ title: "Renamed" }),
      }),
    );
  });

  it("deleteList calls DELETE /api/lists/{id}", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, status: 204 });

    expect(api.deleteList, "deleteList must be exported as a function").toBeTypeOf("function");

    await api.deleteList("l1");

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/lists/l1"),
      expect.objectContaining({ method: "DELETE" }),
    );
  });

  it("reorderLists calls PUT /api/lists/reorder with list_ids", async () => {
    const reordered = [
      { id: "l2", title: "B", board_id: "b1", position: 0 },
      { id: "l1", title: "A", board_id: "b1", position: 1 },
    ];
    globalThis.fetch = mockFetch(reordered);

    expect(api.reorderLists, "reorderLists must be exported as a function").toBeTypeOf("function");

    await api.reorderLists({ list_ids: ["l2", "l1"] });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/lists/reorder"),
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ list_ids: ["l2", "l1"] }),
      }),
    );
  });

  it("createCard calls POST /api/cards with JSON body", async () => {
    const created = { id: "c1", title: "New Card", list_id: "l1", position: 0 };
    globalThis.fetch = mockFetch(created, 201);

    expect(api.createCard, "createCard must be exported as a function").toBeTypeOf("function");

    await api.createCard({ title: "New Card", list_id: "l1" });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/cards"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ title: "New Card", list_id: "l1" }),
      }),
    );
  });

  it("updateCard calls PUT /api/cards/{id} with JSON body", async () => {
    const updated = { id: "c1", title: "Updated", list_id: "l1", position: 0 };
    globalThis.fetch = mockFetch(updated);

    expect(api.updateCard, "updateCard must be exported as a function").toBeTypeOf("function");

    await api.updateCard("c1", { title: "Updated" });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/cards/c1"),
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ title: "Updated" }),
      }),
    );
  });

  it("deleteCard calls DELETE /api/cards/{id}", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, status: 204 });

    expect(api.deleteCard, "deleteCard must be exported as a function").toBeTypeOf("function");

    await api.deleteCard("c1");

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/cards/c1"),
      expect.objectContaining({ method: "DELETE" }),
    );
  });

  it("moveCard calls PUT /api/cards/{id}/move with JSON body", async () => {
    const moved = { id: "c1", title: "Task", list_id: "l2", position: 0 };
    globalThis.fetch = mockFetch(moved);

    expect(api.moveCard, "moveCard must be exported as a function").toBeTypeOf("function");

    await api.moveCard("c1", { list_id: "l2", position: 0 });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/cards/c1/move"),
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ list_id: "l2", position: 0 }),
      }),
    );
  });

  it("throws on non-OK response with detail message", async () => {
    globalThis.fetch = mockFetch({ detail: "Not found" }, 404);

    expect(api.getBoard, "getBoard must be exported as a function").toBeTypeOf("function");

    await expect(api.getBoard()).rejects.toThrow("Not found");
  });
});
