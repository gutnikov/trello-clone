import { BoardCard } from "@/components/BoardCard";

interface CardData {
  id: string;
  title: string;
  position: number;
}

interface BoardListProps {
  list: {
    id: string;
    title: string;
    position: number;
    cards: CardData[];
  };
}

export function BoardList({ list }: BoardListProps) {
  const sortedCards = [...list.cards].sort((a, b) => a.position - b.position);

  return (
    <div
      data-testid="board-list"
      className="flex w-72 shrink-0 flex-col rounded-xl bg-muted/60 p-3"
    >
      <h3 className="mb-3 px-1 text-sm font-semibold text-foreground">{list.title}</h3>
      <div className="flex flex-col gap-2">
        {sortedCards.map((card) => (
          <BoardCard key={card.id} card={card} />
        ))}
      </div>
    </div>
  );
}
