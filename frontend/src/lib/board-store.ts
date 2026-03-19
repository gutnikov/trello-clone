/**
 * Board store module — React Query hooks for board data.
 *
 * Provides query and mutation hooks for all board, list, and card operations
 * with optimistic updates and automatic cache invalidation.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { BoardDetailResponse } from "@/lib/api";
import * as api from "@/lib/api";

// ── Query Keys ─────────────────────────────────────────────────────────────

export const boardQueryKey = ["board"] as const;

// ── Query Hook ─────────────────────────────────────────────────────────────

/** Fetches the full board with nested lists and cards. */
export function useBoard() {
  return useQuery({
    queryKey: boardQueryKey,
    queryFn: api.getBoard,
  });
}

// ── Board Mutations ────────────────────────────────────────────────────────

/** Updates the board title with optimistic update. */
export function useUpdateBoard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: api.UpdateBoardRequest) => api.updateBoard(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          title: data.title,
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

// ── List Mutations ─────────────────────────────────────────────────────────

/** Creates a new list with optimistic update. */
export function useCreateList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: api.CreateListRequest) => api.createList(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          lists: [
            ...previous.lists,
            {
              id: `temp-${Date.now()}`,
              title: data.title,
              board_id: data.board_id,
              position: previous.lists.length,
              cards: [],
            },
          ],
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

/** Updates a list with optimistic update. */
export function useUpdateList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: api.UpdateListRequest }) =>
      api.updateList(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          lists: previous.lists.map((list) =>
            list.id === id ? { ...list, title: data.title } : list,
          ),
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

/** Deletes a list with optimistic update. */
export function useDeleteList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.deleteList(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          lists: previous.lists.filter((list) => list.id !== id),
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

/** Reorders lists with optimistic update. */
export function useReorderLists() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: api.ReorderListsRequest) => api.reorderLists(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        const listMap = new Map(previous.lists.map((l) => [l.id, l]));
        const reordered = data.list_ids
          .map((id, i) => {
            const list = listMap.get(id);
            return list ? { ...list, position: i } : undefined;
          })
          .filter((l): l is api.List => l !== undefined);
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          lists: reordered,
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

// ── Card Mutations ─────────────────────────────────────────────────────────

/** Creates a new card with optimistic update. */
export function useCreateCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: api.CreateCardRequest) => api.createCard(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          lists: previous.lists.map((list) =>
            list.id === data.list_id
              ? {
                  ...list,
                  cards: [
                    ...list.cards,
                    {
                      id: `temp-${Date.now()}`,
                      title: data.title,
                      list_id: data.list_id,
                      position: list.cards.length,
                    },
                  ],
                }
              : list,
          ),
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

/** Updates a card with optimistic update. */
export function useUpdateCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: api.UpdateCardRequest }) =>
      api.updateCard(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          lists: previous.lists.map((list) => ({
            ...list,
            cards: list.cards.map((card) =>
              card.id === id ? { ...card, title: data.title } : card,
            ),
          })),
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

/** Deletes a card with optimistic update. */
export function useDeleteCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.deleteCard(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
          ...previous,
          lists: previous.lists.map((list) => ({
            ...list,
            cards: list.cards.filter((card) => card.id !== id),
          })),
        });
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}

/** Moves a card to a different list/position with optimistic update. */
export function useMoveCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: api.MoveCardRequest }) => api.moveCard(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: boardQueryKey });
      const previous = queryClient.getQueryData<BoardDetailResponse>(boardQueryKey);
      if (previous) {
        // Find the card being moved
        const allCards = previous.lists.flatMap((list) => list.cards);
        const foundCard = allCards.find((c) => c.id === id);
        if (foundCard) {
          const movedCard: api.Card = {
            ...foundCard,
            list_id: data.list_id,
            position: data.position,
          };
          // Remove card from all lists, then insert into target list
          const listsWithoutCard = previous.lists.map((list) => ({
            ...list,
            cards: list.cards.filter((c) => c.id !== id),
          }));
          const listsWithCard = listsWithoutCard.map((list) =>
            list.id === data.list_id
              ? {
                  ...list,
                  cards: [
                    ...list.cards.slice(0, data.position),
                    movedCard,
                    ...list.cards.slice(data.position),
                  ],
                }
              : list,
          );
          queryClient.setQueryData<BoardDetailResponse>(boardQueryKey, {
            ...previous,
            lists: listsWithCard,
          });
        }
      }
      return { previous };
    },
    onError: (_err, _data, context) => {
      if (context?.previous) {
        queryClient.setQueryData(boardQueryKey, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: boardQueryKey });
    },
  });
}
