// @vitest-environment jsdom
// @ts-nocheck — Intentional: tests reference exports that don't exist yet (TDD fail-first)
/**
 * TRE-40: Fail-first tests for board display components.
 *
 * These tests verify that the Board, BoardList, BoardCard, and EmptyBoard
 * components are exported correctly and render the expected DOM structure.
 *
 * All tests are expected to FAIL until the implementation is written.
 */
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import * as BoardModule from "@/components/Board";
import * as BoardListModule from "@/components/BoardList";
import * as BoardCardModule from "@/components/BoardCard";
import * as EmptyBoardModule from "@/components/EmptyBoard";

// ── Test Data ──────────────────────────────────────────────────────────────

const mockBoardData = {
  id: "b1",
  title: "My Board",
  lists: [
    {
      id: "l1",
      title: "To Do",
      position: 0,
      cards: [
        { id: "c1", title: "Task 1", position: 0 },
        { id: "c2", title: "Task 2", position: 1 },
      ],
    },
    {
      id: "l2",
      title: "In Progress",
      position: 1,
      cards: [{ id: "c3", title: "Task 3", position: 0 }],
    },
    {
      id: "l3",
      title: "Done",
      position: 2,
      cards: [],
    },
  ],
};

// ── Component Export Tests ─────────────────────────────────────────────────

describe("Board component exports", () => {
  it("Board is exported as a function component", () => {
    expect(
      BoardModule.Board,
      "Board.tsx should export a named 'Board' component",
    ).toBeDefined();
    expect(
      typeof BoardModule.Board,
      "Board should be a function component",
    ).toBe("function");
  });

  it("BoardList is exported as a function component", () => {
    expect(
      BoardListModule.BoardList,
      "BoardList.tsx should export a named 'BoardList' component",
    ).toBeDefined();
    expect(
      typeof BoardListModule.BoardList,
      "BoardList should be a function component",
    ).toBe("function");
  });

  it("BoardCard is exported as a function component", () => {
    expect(
      BoardCardModule.BoardCard,
      "BoardCard.tsx should export a named 'BoardCard' component",
    ).toBeDefined();
    expect(
      typeof BoardCardModule.BoardCard,
      "BoardCard should be a function component",
    ).toBe("function");
  });

  it("EmptyBoard is exported as a function component", () => {
    expect(
      EmptyBoardModule.EmptyBoard,
      "EmptyBoard.tsx should export a named 'EmptyBoard' component",
    ).toBeDefined();
    expect(
      typeof EmptyBoardModule.EmptyBoard,
      "EmptyBoard should be a function component",
    ).toBe("function");
  });
});

// ── Board Component Rendering Tests ───────────────────────────────────────

describe("Board component rendering", () => {
  it("renders board title", () => {
    const Board = BoardModule.Board;
    expect(Board, "Board component must be exported before rendering tests can run").toBeDefined();

    render(React.createElement(Board, { board: mockBoardData }));

    expect(
      screen.getByText("My Board"),
      "Board should display the board title",
    ).toBeDefined();
  });

  it("renders a scrollable container for lists", () => {
    const Board = BoardModule.Board;
    expect(Board, "Board component must be exported before rendering tests can run").toBeDefined();

    const { container } = render(
      React.createElement(Board, { board: mockBoardData }),
    );

    // The board should have a horizontally scrollable container
    const scrollContainer = container.querySelector(
      "[data-testid='board-lists-container']",
    );
    expect(
      scrollContainer,
      "Board should render a lists container with data-testid='board-lists-container'",
    ).not.toBeNull();
  });

  it("renders a BoardList for each list in the board", () => {
    const Board = BoardModule.Board;
    expect(Board, "Board component must be exported before rendering tests can run").toBeDefined();

    render(React.createElement(Board, { board: mockBoardData }));

    // All three list titles should be rendered
    expect(
      screen.getByText("To Do"),
      "Board should render the 'To Do' list",
    ).toBeDefined();
    expect(
      screen.getByText("In Progress"),
      "Board should render the 'In Progress' list",
    ).toBeDefined();
    expect(
      screen.getByText("Done"),
      "Board should render the 'Done' list",
    ).toBeDefined();
  });
});

// ── BoardList Component Rendering Tests ───────────────────────────────────

describe("BoardList component rendering", () => {
  it("renders list title", () => {
    const BoardList = BoardListModule.BoardList;
    expect(BoardList, "BoardList component must be exported before rendering tests can run").toBeDefined();

    render(
      React.createElement(BoardList, {
        list: mockBoardData.lists[0],
      }),
    );

    expect(
      screen.getByText("To Do"),
      "BoardList should display the list title",
    ).toBeDefined();
  });

  it("renders a BoardCard for each card in the list", () => {
    const BoardList = BoardListModule.BoardList;
    expect(BoardList, "BoardList component must be exported before rendering tests can run").toBeDefined();

    render(
      React.createElement(BoardList, {
        list: mockBoardData.lists[0],
      }),
    );

    // The "To Do" list has 2 cards
    expect(
      screen.getByText("Task 1"),
      "BoardList should render the first card",
    ).toBeDefined();
    expect(
      screen.getByText("Task 2"),
      "BoardList should render the second card",
    ).toBeDefined();
  });

  it("renders cards ordered by position", () => {
    const BoardList = BoardListModule.BoardList;
    expect(BoardList, "BoardList component must be exported before rendering tests can run").toBeDefined();

    const unorderedList = {
      id: "l1",
      title: "Test List",
      position: 0,
      cards: [
        { id: "c3", title: "Third", position: 2 },
        { id: "c1", title: "First", position: 0 },
        { id: "c2", title: "Second", position: 1 },
      ],
    };

    const { container } = render(
      React.createElement(BoardList, { list: unorderedList }),
    );

    // Get all card elements and verify order
    const cardElements = container.querySelectorAll(
      "[data-testid='board-card']",
    );
    expect(
      cardElements.length,
      "BoardList should render 3 cards",
    ).toBe(3);

    // Cards should appear in position order: First, Second, Third
    expect(
      cardElements[0]?.textContent,
      "First card by position should be 'First'",
    ).toContain("First");
    expect(
      cardElements[1]?.textContent,
      "Second card by position should be 'Second'",
    ).toContain("Second");
    expect(
      cardElements[2]?.textContent,
      "Third card by position should be 'Third'",
    ).toContain("Third");
  });
});

// ── BoardCard Component Rendering Tests ───────────────────────────────────

describe("BoardCard component rendering", () => {
  it("renders card title", () => {
    const BoardCard = BoardCardModule.BoardCard;
    expect(BoardCard, "BoardCard component must be exported before rendering tests can run").toBeDefined();

    render(
      React.createElement(BoardCard, {
        card: { id: "c1", title: "Fix bug", position: 0 },
      }),
    );

    expect(
      screen.getByText("Fix bug"),
      "BoardCard should display the card title",
    ).toBeDefined();
  });

  it("renders with data-testid attribute", () => {
    const BoardCard = BoardCardModule.BoardCard;
    expect(BoardCard, "BoardCard component must be exported before rendering tests can run").toBeDefined();

    const { container } = render(
      React.createElement(BoardCard, {
        card: { id: "c1", title: "Fix bug", position: 0 },
      }),
    );

    const cardEl = container.querySelector("[data-testid='board-card']");
    expect(
      cardEl,
      "BoardCard should render with data-testid='board-card'",
    ).not.toBeNull();
  });
});

// ── EmptyBoard Component Rendering Tests ──────────────────────────────────

describe("EmptyBoard component rendering", () => {
  it("renders empty state message", () => {
    const EmptyBoard = EmptyBoardModule.EmptyBoard;
    expect(EmptyBoard, "EmptyBoard component must be exported before rendering tests can run").toBeDefined();

    render(React.createElement(EmptyBoard));

    // Should contain some prompt about creating a list
    const body = document.body.textContent || "";
    expect(
      body.toLowerCase(),
      "EmptyBoard should contain text about creating a list",
    ).toContain("list");
  });

  it("contains call-to-action text encouraging list creation", () => {
    const EmptyBoard = EmptyBoardModule.EmptyBoard;
    expect(EmptyBoard, "EmptyBoard component must be exported before rendering tests can run").toBeDefined();

    render(React.createElement(EmptyBoard));

    // Should contain encouraging text about getting started or creating first list
    const body = document.body.textContent || "";
    const hasCtaText =
      body.toLowerCase().includes("create") ||
      body.toLowerCase().includes("add") ||
      body.toLowerCase().includes("get started");
    expect(
      hasCtaText,
      "EmptyBoard should contain call-to-action text (create/add/get started)",
    ).toBe(true);
  });
});
