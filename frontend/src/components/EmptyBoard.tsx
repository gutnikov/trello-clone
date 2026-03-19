export function EmptyBoard() {
  return (
    <div
      data-testid="empty-board"
      className="flex flex-col items-center justify-center px-4 py-20 text-center"
    >
      <h2 className="mb-2 text-xl font-semibold text-foreground">No lists yet</h2>
      <p className="max-w-sm text-muted-foreground">
        Create your first list to get started organizing your tasks.
      </p>
    </div>
  );
}
