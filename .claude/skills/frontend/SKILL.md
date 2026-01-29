---
name: frontend
description: Frontend development with React, TypeScript, TanStack tools, and Tailwind CSS. Use when writing React components, hooks, TanStack Query/Router/Table/Form code, Tailwind styles, or configuring frontend tooling (ESLint, Prettier, tsconfig).
---

# Frontend Development Standards

Apply modern frontend best practices when writing or reviewing code.

## Key Standards

- **React**: Functional components only, React 19 features (Compiler, `use()`, `useActionState`), custom hooks for all logic
- **TypeScript**: Strict mode, discriminated unions with exhaustive checks, Zod for runtime validation
- **TanStack Query**: `queryOptions` factory pattern, proper cache invalidation, optimistic updates, `useSuspenseQuery`
- **TanStack Router**: File-based routing, type-safe search params, `from` parameter for typed hooks
- **TanStack Table**: Stable data references (critical), memoized columns, headless architecture
- **TanStack Form**: Schema-based Zod validation, proper validation strategies
- **Tailwind CSS v4**: `@theme` for design tokens, utility composition, `cn()` helper, Prettier plugin for class sorting
- **State Management**: TanStack Query for server state, Zustand for global client state, URL for shareable state
- **Testing**: Vitest + React Testing Library, test behavior not implementation, `getByRole` first
- **Accessibility**: Semantic HTML, ARIA attributes, keyboard navigation, 4.5:1 contrast ratio

## When writing code, follow these principles

1. Extract stateful logic into custom hooks -- components should be thin rendering layers
2. Use `queryOptions()` factories for query key management and reuse
3. Never use Redux/Zustand for server state -- that is TanStack Query's job
4. Use feature-based folder structure with barrel exports as public API
5. Place error boundaries strategically around independent sections
6. Use `userEvent` over `fireEvent` in tests
7. Every interactive element must be keyboard accessible

## Detailed reference

For complete patterns, code examples, and configurations, see [reference.md](reference.md).
