import { createFileRoute } from "@tanstack/react-router";
import { Board } from "@/components/Board";
import { EmptyBoard } from "@/components/EmptyBoard";
import { useBoard } from "@/lib/board-store";

export const Route = createFileRoute("/board")({ component: BoardPage });

function BoardPage() {
  const { data: board, isLoading, error } = useBoard();

  if (isLoading) {
    return (
      <main className="flex min-h-[calc(100dvh-4rem)] items-center justify-center">
        <p className="text-muted-foreground">Loading board...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-[calc(100dvh-4rem)] items-center justify-center">
        <p className="text-destructive">Failed to load board.</p>
      </main>
    );
  }

  if (!board) {
    return null;
  }

  if (board.lists.length === 0) {
    return (
      <main className="min-h-[calc(100dvh-4rem)]">
        <h1 className="px-6 py-4 text-2xl font-bold text-foreground">{board.title}</h1>
        <EmptyBoard />
      </main>
    );
  }

  return (
    <main className="min-h-[calc(100dvh-4rem)]">
      <Board board={board} />
    </main>
  );
}
