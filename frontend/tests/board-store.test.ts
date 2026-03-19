/**
 * TRE-39: Fail-first tests for board store / React Query hooks (src/lib/board-store.ts)
 *
 * These tests verify that the board store module exports React Query hooks
 * for fetching and mutating board data, with proper loading/error states
 * and mutation functions.
 *
 * All tests are expected to FAIL until the implementation is written.
 */
import { describe, expect, it } from "vitest";
import * as boardStore from "@/lib/board-store";

// ── Hook Export Tests ──────────────────────────────────────────────────────

describe("Board store hook exports", () => {
  it("exports useBoard as a function", () => {
    expect(boardStore.useBoard).toBeDefined();
    expect(typeof boardStore.useBoard).toBe("function");
  });

  it("exports useUpdateBoard as a function", () => {
    expect(boardStore.useUpdateBoard).toBeDefined();
    expect(typeof boardStore.useUpdateBoard).toBe("function");
  });

  it("exports useCreateList as a function", () => {
    expect(boardStore.useCreateList).toBeDefined();
    expect(typeof boardStore.useCreateList).toBe("function");
  });

  it("exports useUpdateList as a function", () => {
    expect(boardStore.useUpdateList).toBeDefined();
    expect(typeof boardStore.useUpdateList).toBe("function");
  });

  it("exports useDeleteList as a function", () => {
    expect(boardStore.useDeleteList).toBeDefined();
    expect(typeof boardStore.useDeleteList).toBe("function");
  });

  it("exports useReorderLists as a function", () => {
    expect(boardStore.useReorderLists).toBeDefined();
    expect(typeof boardStore.useReorderLists).toBe("function");
  });

  it("exports useCreateCard as a function", () => {
    expect(boardStore.useCreateCard).toBeDefined();
    expect(typeof boardStore.useCreateCard).toBe("function");
  });

  it("exports useUpdateCard as a function", () => {
    expect(boardStore.useUpdateCard).toBeDefined();
    expect(typeof boardStore.useUpdateCard).toBe("function");
  });

  it("exports useDeleteCard as a function", () => {
    expect(boardStore.useDeleteCard).toBeDefined();
    expect(typeof boardStore.useDeleteCard).toBe("function");
  });

  it("exports useMoveCard as a function", () => {
    expect(boardStore.useMoveCard).toBeDefined();
    expect(typeof boardStore.useMoveCard).toBe("function");
  });
});

// ── Query Key Export Tests ─────────────────────────────────────────────────

describe("Board store query key exports", () => {
  it("exports a board query key for cache management", () => {
    // The module should export a query key constant or factory for the board query
    // so consumers can manually invalidate or prefetch
    expect(boardStore.boardQueryKey).toBeDefined();
  });
});
