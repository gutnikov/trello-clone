import { BoardList } from "@/components/BoardList";

interface CardData {
  id: string;
  title: string;
  position: number;
}

interface ListData {
  id: string;
  title: string;
  position: number;
  cards: CardData[];
}

interface BoardProps {
  board: {
    id: string;
    title: string;
    lists: ListData[];
  };
}

export function Board({ board }: BoardProps) {
  return (
    <div className="flex h-full flex-col">
      <h1 className="px-6 py-4 text-2xl font-bold text-foreground">
        {board.title}
      </h1>
      <div
        data-testid="board-lists-container"
        className="flex flex-1 gap-4 overflow-x-auto px-6 pb-6"
      >
        {board.lists.map((list) => (
          <BoardList key={list.id} list={list} />
        ))}
      </div>
    </div>
  );
}
