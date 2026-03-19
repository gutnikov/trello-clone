interface BoardCardProps {
  card: {
    id: string;
    title: string;
    position: number;
  };
}

export function BoardCard({ card }: BoardCardProps) {
  return (
    <div
      data-testid="board-card"
      className="rounded-lg border border-border bg-card px-3 py-2 text-sm text-card-foreground shadow-sm"
    >
      {card.title}
    </div>
  );
}
