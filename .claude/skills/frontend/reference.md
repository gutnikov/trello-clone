# Golden Standards & Best Practices: Modern Frontend Development (2025-2026)

## React + TypeScript + TanStack + Tailwind CSS

This document serves as a comprehensive reference for AI coding assistants and developers building modern frontend applications. It covers established patterns, conventions, and best practices current as of 2025-2026.

---

## Table of Contents

1. [React Best Practices](#1-react-best-practices)
2. [TypeScript Strict Mode & Advanced Patterns](#2-typescript-strict-mode--advanced-patterns)
3. [TanStack Query (React Query)](#3-tanstack-query-react-query)
4. [TanStack Router](#4-tanstack-router)
5. [TanStack Table](#5-tanstack-table)
6. [TanStack Form](#6-tanstack-form)
7. [Tailwind CSS v4](#7-tailwind-css-v4)
8. [State Management](#8-state-management)
9. [Component Architecture & Composition](#9-component-architecture--composition)
10. [Error Boundaries & Error Handling](#10-error-boundaries--error-handling)
11. [Performance Optimization](#11-performance-optimization)
12. [Testing (Vitest + React Testing Library)](#12-testing-vitest--react-testing-library)
13. [Accessibility (a11y)](#13-accessibility-a11y)
14. [Project Structure](#14-project-structure)
15. [Code Quality (ESLint, Prettier, TypeScript Config)](#15-code-quality-eslint-prettier-typescript-config)

---

## 1. React Best Practices

### Functional Components Are the Standard

- **Always use functional components.** Class components are legacy. All new code must use function components with hooks.
- Keep components small and focused -- ideally one concern per component.
- Use PascalCase for component names, camelCase for variables and functions.

### React 19 Features to Leverage

- **React Compiler**: React 19+ includes an automatic compiler that memoizes components and values transparently. You write standard React code; the compiler inserts optimizations. Early adopters report 25-40% fewer re-renders without code changes. This means you can remove many manual `React.memo`, `useMemo`, and `useCallback` calls -- but only after confirming the compiler is active in your build.

- **`use()` hook**: Read promises and context directly in render. Unlike other hooks, `use()` can be called conditionally (e.g., after early returns). Use it to read async resources with Suspense.

- **`useActionState` hook**: Replaces `useFormState` for form handling with clearer semantics and better TypeScript support. Manages pending states, error handling, and form data in one hook.

- **`useOptimistic` hook**: Show users instant feedback while mutations are in flight. Automatically reverts on failure.

- **`useEffectEvent` (React 19.2+)**: Extract "event" logic out of `useEffect` to prevent unnecessary effect re-runs. For example, changing a theme should not cause a chat connection to reconnect.

- **Concurrent Rendering**: Enabled by default. React can interrupt and pause rendering to keep the UI responsive. Automatic batching extends to promises, `setTimeout`, and native event handlers.

- **Server Components**: For frameworks like Next.js or TanStack Start. Keep data fetching on the server, reduce client bundle size.

### Rules of Hooks

- **Never** call hooks inside loops, conditions, or nested functions.
- Always call hooks at the top level of your React function.
- Custom hooks must start with `use`.

### Custom Hooks

- Extract reusable stateful logic into custom hooks.
- If logic repeats across components, it belongs in a custom hook.
- Name hooks descriptively: `useUserPermissions`, `useDebouncedSearch`, `useLocalStorage`.

### Component Guidelines

```typescript
// GOOD: Small, focused component with clear props
interface UserAvatarProps {
  user: User;
  size?: 'sm' | 'md' | 'lg';
}

function UserAvatar({ user, size = 'md' }: UserAvatarProps) {
  return (
    <img
      src={user.avatarUrl}
      alt={`${user.name}'s avatar`}
      className={avatarSizes[size]}
    />
  );
}

// BAD: God component doing too many things
function UserPage() {
  // 200 lines of mixed concerns...
}
```

### Key Principles

- Prefer composition over inheritance.
- Lift state up only when necessary; keep state as local as possible.
- Use `children` prop for flexible component composition.
- Avoid deeply nested ternary expressions in JSX -- extract into variables or components.
- Avoid `any` in TypeScript -- always type your props.

---

## 2. TypeScript Strict Mode & Advanced Patterns

### Strict `tsconfig.json`

Always enable strict mode. This is non-negotiable for production code:

```jsonc
{
  "compilerOptions": {
    "strict": true,                    // Enables all strict checks
    "noImplicitAny": true,             // No implicit `any` types
    "strictNullChecks": true,          // null/undefined are distinct types
    "strictFunctionTypes": true,       // Strict function type checking
    "strictBindCallApply": true,       // Strict bind/call/apply
    "strictPropertyInitialization": true,
    "noImplicitReturns": true,         // Every code path must return
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,  // Array/object indexing returns T | undefined
    "forceConsistentCasingInFileNames": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "jsx": "react-jsx",
    "resolveJsonModule": true,
    "isolatedModules": true
  }
}
```

### Never Use `any`

```typescript
// BAD
function processData(data: any) { ... }

// GOOD: Use `unknown` and narrow
function processData(data: unknown) {
  if (isValidPayload(data)) {
    // data is now narrowed to ValidPayload
  }
}
```

### Discriminated Unions

Use discriminated unions for complex state modeling. Always include exhaustive checking:

```typescript
// Define a discriminated union with a common literal-type property
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

// Exhaustive switch with `never` check
function renderState<T>(state: RequestState<T>) {
  switch (state.status) {
    case 'idle':
      return <Placeholder />;
    case 'loading':
      return <Spinner />;
    case 'success':
      return <DataView data={state.data} />;
    case 'error':
      return <ErrorMessage error={state.error} />;
    default: {
      const _exhaustive: never = state;
      return _exhaustive;
    }
  }
}
```

### Utility Types

Use built-in utility types instead of rewriting boilerplate:

```typescript
// Pick only what you need
type UserSummary = Pick<User, 'id' | 'name' | 'email'>;

// Make all properties optional for updates
type UserUpdate = Partial<User>;

// Make all properties required
type CompleteUser = Required<User>;

// Omit sensitive fields
type PublicUser = Omit<User, 'password' | 'ssn'>;

// Record for dictionaries
type UserMap = Record<string, User>;

// Readonly for immutable data
type FrozenConfig = Readonly<AppConfig>;

// Extract and Exclude for union manipulation
type SuccessStates = Extract<RequestState<unknown>, { status: 'success' | 'idle' }>;
```

### Component Props Patterns

```typescript
// Polymorphic component with `as` prop
type BoxProps<C extends React.ElementType> = {
  as?: C;
  children: React.ReactNode;
} & Omit<React.ComponentPropsWithoutRef<C>, 'as' | 'children'>;

// Props extending native HTML elements
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  isLoading?: boolean;
}

// Children render prop pattern (typed)
interface DataListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
}
```

### Zod for Runtime Validation

Pair TypeScript with Zod for runtime validation that stays in sync with your types:

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(['admin', 'editor', 'viewer']),
});

type User = z.infer<typeof UserSchema>;

// Use z.discriminatedUnion for efficient runtime discrimination
const EventSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('click'), x: z.number(), y: z.number() }),
  z.object({ type: z.literal('keypress'), key: z.string() }),
]);
```

---

## 3. TanStack Query (React Query)

### Core Principles

- TanStack Query v5 requires React 18+.
- Use a single object parameter for all hooks (overloads were removed in v5).
- **Separate server state from client state.** TanStack Query handles server state; use Zustand/Jotai/Context for client-only state.

### Query Options Factory

Use `queryOptions` for type-safe, reusable query definitions:

```typescript
import { queryOptions, useQuery, useSuspenseQuery } from '@tanstack/react-query';

// Define reusable query options
const userQueries = {
  all: () => queryOptions({
    queryKey: ['users'],
    queryFn: () => api.users.list(),
  }),
  detail: (userId: string) => queryOptions({
    queryKey: ['users', userId],
    queryFn: () => api.users.getById(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  }),
  byOrg: (orgId: string) => queryOptions({
    queryKey: ['users', { orgId }],
    queryFn: () => api.users.listByOrg(orgId),
  }),
};

// Use in components
function UserProfile({ userId }: { userId: string }) {
  const { data } = useSuspenseQuery(userQueries.detail(userId));
  // data is typed as User, never undefined (thanks to Suspense)
}
```

### Caching Best Practices

- `gcTime` (formerly `cacheTime`): Controls when unused queries are garbage-collected. Default is 5 minutes.
- `staleTime`: How long data is considered fresh. Default is 0 (always stale). Set to `Infinity` for rarely-changing data.
- Multiple components requesting the same query key result in only one network call.
- Use `placeholderData` (with the identity function or `keepPreviousData`) instead of the removed `keepPreviousData` option.

### Mutations

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UserUpdate) => api.users.update(data),
    onSuccess: (updatedUser) => {
      // Prefer invalidation over direct cache updates
      queryClient.invalidateQueries({ queryKey: ['users'] });

      // OR: Direct cache update (use immutably!)
      queryClient.setQueryData(
        ['users', updatedUser.id],
        updatedUser // Never mutate cache data in place
      );
    },
  });
}
```

**Prefer invalidation over direct cache updates** for most cases. Direct updates duplicate backend logic and are error-prone for sorted/filtered lists.

### Optimistic Updates

Two approaches:

**Approach 1: Via `variables` (simpler, for single-location updates)**

```typescript
const mutation = useMutation({
  mutationFn: updateTodo,
});

// In JSX, use mutation.variables for optimistic display
<li style={{ opacity: mutation.isPending ? 0.5 : 1 }}>
  {mutation.isPending ? mutation.variables.title : todo.title}
</li>
```

**Approach 2: Via cache `onMutate` (for multi-location updates)**

```typescript
useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    await queryClient.cancelQueries({ queryKey: ['todos'] });
    const previousTodos = queryClient.getQueryData(['todos']);
    queryClient.setQueryData(['todos'], (old) =>
      old.map(t => t.id === newTodo.id ? { ...t, ...newTodo } : t)
    );
    return { previousTodos }; // Snapshot for rollback
  },
  onError: (_err, _newTodo, context) => {
    queryClient.setQueryData(['todos'], context?.previousTodos);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] });
  },
});
```

**When NOT to use optimistic updates:**
- When the mutation can realistically fail (rollback UX is jarring).
- When the UI closes/navigates on submit (hard to undo).
- Reserve for interactions where instant feedback is critical.

### Suspense Integration

```typescript
// Preferred: useSuspenseQuery guarantees data is defined
const { data } = useSuspenseQuery(userQueries.detail(userId));
// data: User (not User | undefined)

// Note: `enabled` is not available on useSuspenseQuery
// For dependent queries with Suspense, queries run serially automatically
```

### Rules

- `onSuccess`, `onError`, `onSettled` callbacks were **removed from `useQuery`** in v5. They remain on `useMutation`.
- Always update cache immutably with `setQueryData`.
- Use `useMutationState` to share mutation state across components.

---

## 4. TanStack Router

### Core Philosophy

TanStack Router provides fully inferred type safety -- no manual type assertions, no angle brackets. Every path, param, and search param is type-checked.

### Use File-Based Routing

File-based routing is the recommended approach. The TanStack Router Bundler Plugin or Router CLI manages route paths automatically, enabling full type inference:

```
src/
  routes/
    __root.tsx          # Root layout
    index.tsx           # / route
    about.tsx           # /about route
    users/
      index.tsx         # /users route
      $userId.tsx       # /users/:userId route
      $userId.edit.tsx  # /users/:userId/edit route
```

### Type-Safe Navigation

```typescript
// Links are fully type-checked
<Link to="/users/$userId" params={{ userId: '123' }} />

// Search params are type-safe
<Link
  to="/users"
  search={{ page: 1, sort: 'name' }}
/>

// navigate() is also type-safe
const navigate = useNavigate();
navigate({ to: '/users/$userId', params: { userId } });
```

### Type-Safe Hooks with `from`

```typescript
// In a route-specific component, pass `from` for full type safety
function UserPage() {
  const { userId } = useParams({ from: '/users/$userId' });
  const { page, sort } = useSearch({ from: '/users' });
  const data = useLoaderData({ from: '/users/$userId' });
}
```

### Shared Components with `strict: false`

```typescript
// For components shared across multiple routes
function Breadcrumbs() {
  const search = useSearch({ strict: false });
  // search is typed as union of all possible search params
}
```

### Search Params as First-Class Citizens

Search params are deeply typed and support complex data structures. They work like `useState` in the URL:

```typescript
// In route definition
export const Route = createFileRoute('/users/')({
  validateSearch: (search: Record<string, unknown>) => ({
    page: Number(search.page) || 1,
    filter: (search.filter as string) || '',
    sort: (search.sort as 'name' | 'date') || 'name',
  }),
});
```

### Router Context for Dependency Injection

```typescript
// Create root route with typed context
const rootRoute = createRootRouteWithContext<{
  queryClient: QueryClient;
  auth: AuthState;
}>()({
  component: RootLayout,
});

// Access in any route
export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: '/login' });
    }
  },
  loader: ({ context }) =>
    context.queryClient.ensureQueryData(dashboardQueries.stats()),
});
```

### Anti-Patterns to Avoid

- **Never** use JSX-based route definitions -- TypeScript cannot infer types from JSX routes.
- **Never** define all routes in a single nested object tree -- it doesn't scale and hinders code-splitting.
- Use `getRouteApi` for code-split components to avoid importing the full route path.

---

## 5. TanStack Table

### Core Concept

TanStack Table is a **headless** table library. It provides the logic (sorting, filtering, pagination); you provide all the markup and styling. This gives complete control over rendering.

### Critical: Stable Data References

```typescript
// BAD: Data redefined every render -> infinite re-render loop
function MyTable() {
  const data = fetchedData.map(transform); // New array every render!
  const table = useReactTable({ data, columns });
}

// GOOD: Stable reference with useMemo or useState
function MyTable() {
  const [data, setData] = useState<User[]>([]);
  const columns = useMemo(() => columnDefs, []);
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });
}
```

### Column Definitions

```typescript
const columns = useMemo<ColumnDef<User>[]>(() => [
  {
    accessorKey: 'name',
    header: 'Name',
    cell: (info) => info.getValue(),
  },
  {
    // Deep accessor with dot notation
    accessorKey: 'address.city',
    header: 'City',
  },
  {
    // Accessor function for computed values
    accessorFn: (row) => `${row.firstName} ${row.lastName}`,
    id: 'fullName',
    header: 'Full Name',
  },
], []);
```

### Avoid Prop Drilling with Context

```typescript
// Provide table instance via context
const TableContext = createContext<Table<User> | null>(null);

function useTableContext() {
  const ctx = useContext(TableContext);
  if (!ctx) throw new Error('useTableContext must be used within TableProvider');
  return ctx;
}

function TableProvider({ children, data }: { children: ReactNode; data: User[] }) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() });
  return <TableContext.Provider value={table}>{children}</TableContext.Provider>;
}
```

### Combine with TanStack Query

Use TanStack Query for fetching and TanStack Table for display. Keep server state (pagination, sorting, filtering) in URL search params for shareable/bookmarkable URLs.

### Performance

- Memoize `data` and `columns` with `useMemo`.
- Use row virtualization (`@tanstack/react-virtual`) for large datasets (1000+ rows).
- Import only the row models you need (tree-shakeable).

---

## 6. TanStack Form

### Core Concepts

TanStack Form is a headless, type-safe form library with performance optimized via signals (`@tanstack/store`). Each field only re-renders when its own value changes.

### Basic Usage

```typescript
import { useForm } from '@tanstack/react-form';

function CreateUserForm() {
  const form = useForm({
    defaultValues: {
      name: '',
      email: '',
    },
    onSubmit: async ({ value }) => {
      await api.users.create(value);
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.Field
        name="name"
        validators={{
          onChange: ({ value }) =>
            value.length < 2 ? 'Name must be at least 2 characters' : undefined,
        }}
      >
        {(field) => (
          <div>
            <label htmlFor={field.name}>Name</label>
            <input
              id={field.name}
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
              aria-invalid={field.state.meta.errors.length > 0}
            />
            {field.state.meta.errors.map((error) => (
              <p key={error} role="alert">{error}</p>
            ))}
          </div>
        )}
      </form.Field>
    </form>
  );
}
```

### Schema-Based Validation with Zod

```typescript
import { zodValidator } from '@tanstack/zod-form-adapter';

const form = useForm({
  defaultValues: { name: '', email: '' },
  validatorAdapter: zodValidator(),
  onSubmit: async ({ value }) => { /* ... */ },
});

// Field-level Zod validation
<form.Field
  name="email"
  validators={{
    onChange: z.string().email('Invalid email'),
  }}
/>
```

### Validation Strategies

- **`onChange`**: Validates on every keystroke. Best for real-time feedback.
- **`onBlur`**: Validates when the field loses focus. Good default for most fields.
- **`onSubmit`**: Validates only on form submission. Least intrusive.
- **Mix strategies per field**: Use `onBlur` for most fields, `onChange` for critical fields, and async validators with `onChangeAsyncDebounceMs` for server-side checks.

### Best Practices

- Use `onBlur` validation by default; use `onChange` only where instant feedback matters.
- Use async validation with debouncing (`onChangeAsyncDebounceMs: 500`) for server-side checks (e.g., username availability).
- Use dot notation for nested fields: `user.address.city`.
- Add `aria-invalid` to form controls and `role="alert"` to error messages for accessibility.
- TanStack Form works with any UI library: Tailwind, ShadCN, Material UI, or plain HTML.

---

## 7. Tailwind CSS v4

### CSS-First Configuration

Tailwind CSS v4 eliminates `tailwind.config.js` in favor of CSS-first configuration:

```css
/* app.css */
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-secondary: #64748b;
  --color-danger: #ef4444;
  --color-success: #22c55e;

  --spacing-page: 1.5rem;
  --font-sans: 'Inter', sans-serif;
  --radius-default: 0.5rem;
}
```

### `@theme` vs `:root`

- **`@theme`**: Defines design tokens that generate utility classes. `--color-primary` creates `bg-primary`, `text-primary`, etc.
- **`:root`**: Plain CSS variables that do NOT generate utility classes. Use for non-utility values.

### Setup

One line of CSS, zero configuration:

```css
@import "tailwindcss";
```

No `@tailwind base/components/utilities` directives. No config file required. Template paths are auto-detected. Lightning CSS handles vendor prefixing and syntax transforms.

### Custom Utilities

```css
@utility scrollbar-hidden {
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
```

### Best Practices

1. **Use semantic token names**: `bg-primary`, `text-danger`, `p-page` -- not `bg-blue-500`.
2. **Extract reusable patterns**: Use `@apply` for repeated combinations, but prefer component extraction:

```typescript
// Prefer: Component extraction
function Button({ variant, children }: ButtonProps) {
  return (
    <button className={cn(
      'rounded-default px-4 py-2 font-medium transition-colors',
      variant === 'primary' && 'bg-primary text-white hover:bg-primary-hover',
      variant === 'secondary' && 'bg-secondary text-white',
    )}>
      {children}
    </button>
  );
}

// Acceptable: @apply for highly repeated utility combinations
/* In CSS */
@layer components {
  .btn-base {
    @apply rounded-default px-4 py-2 font-medium transition-colors;
  }
}
```

3. **Use `cn()` (clsx + tailwind-merge)** for conditional class composition:

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

4. **Install `prettier-plugin-tailwindcss`** for automatic class sorting.
5. **Dark mode**: Use the `dark:` variant with class-based toggling.
6. **Responsive design**: Mobile-first with `sm:`, `md:`, `lg:`, `xl:` breakpoints.
7. **Keep token files platform-agnostic**: Don't couple design tokens to Tailwind-specific naming.

### Performance

Tailwind v4 engine: full builds up to 5x faster, incremental builds 100x+ faster. Uses cascade layers, `@property`, and `color-mix()`.

---

## 8. State Management

### Decision Framework

| Use Case | Recommended Tool |
|---|---|
| Server state (API data) | TanStack Query -- always |
| Simple component state | `useState` / `useReducer` |
| Shared state (2-3 components) | Lift state up, or Context API |
| Global app state | Zustand |
| Fine-grained reactive state | Jotai |
| Complex state machines | XState |
| URL state | TanStack Router search params |

### The 80/20 Rule

TanStack Query eliminates roughly 80% of state management concerns. Most "state" in a typical app is actually server state (cached API responses). Once you separate server state, your client state needs shrink dramatically.

### Zustand (Recommended for Global State)

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AppState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        sidebarOpen: true,
        theme: 'light',
        toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
        setTheme: (theme) => set({ theme }),
      }),
      { name: 'app-store' }
    )
  )
);

// Use selectors for performance -- only re-render when selected value changes
function Sidebar() {
  const isOpen = useAppStore((s) => s.sidebarOpen);
  // ...
}
```

### Jotai (For Fine-Grained Reactivity)

```typescript
import { atom, useAtom } from 'jotai';

// Primitive atom
const countAtom = atom(0);

// Derived atom (computed)
const doubleCountAtom = atom((get) => get(countAtom) * 2);

// Async atom
const userAtom = atom(async () => {
  const response = await fetch('/api/user');
  return response.json();
});

// Components subscribe only to atoms they use
function Counter() {
  const [count, setCount] = useAtom(countAtom);
  // Only re-renders when countAtom changes
}
```

### Best Practices

- **Start simple, scale up**: `useState` -> Context -> Zustand/Jotai.
- **Never use Zustand/Jotai/Redux for server state.** That is TanStack Query's job.
- **Keep state as local as possible.** Only lift to global store when truly needed.
- **Use URL state (search params)** for anything that should be shareable/bookmarkable: filters, pagination, sort order, active tabs.
- You can use Zustand and Jotai together: Zustand for global app state, Jotai for component-scoped shared state.

---

## 9. Component Architecture & Composition

### Compound Components

Use compound components for related UI elements that share implicit state:

```typescript
// Usage: Clean, expressive API
<Accordion>
  <Accordion.Item>
    <Accordion.Trigger>Section 1</Accordion.Trigger>
    <Accordion.Content>Content here...</Accordion.Content>
  </Accordion.Item>
</Accordion>

// Implementation: Context-based (preferred)
const AccordionContext = createContext<AccordionContextType | null>(null);

function Accordion({ children }: { children: ReactNode }) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());
  return (
    <AccordionContext.Provider value={{ openItems, toggle }}>
      <div role="region">{children}</div>
    </AccordionContext.Provider>
  );
}

Accordion.Item = AccordionItem;
Accordion.Trigger = AccordionTrigger;
Accordion.Content = AccordionContent;
```

### Custom Hook Pattern

Extract all stateful logic into hooks. Components should be thin rendering layers:

```typescript
// Hook handles all logic
function useUserList(filters: UserFilters) {
  const query = useSuspenseQuery(userQueries.list(filters));
  const deleteMutation = useDeleteUser();

  const sortedUsers = useMemo(
    () => query.data.sort(sortByName),
    [query.data]
  );

  return { users: sortedUsers, deleteUser: deleteMutation.mutate };
}

// Component only renders
function UserList({ filters }: { filters: UserFilters }) {
  const { users, deleteUser } = useUserList(filters);
  return (
    <ul>
      {users.map(user => (
        <UserRow key={user.id} user={user} onDelete={deleteUser} />
      ))}
    </ul>
  );
}
```

### Container/Presentational Split

- **Container components**: Handle data fetching, state, and logic. Use hooks.
- **Presentational components**: Pure rendering. Receive data via props. Easy to test and reuse.

### Composition vs. Configuration

- **Compose** when you need arbitrary JSX and flexible rendering.
- **Configure** when the UI is data-driven and predictable (e.g., form fields from a schema, table columns).

### Props Getters Pattern

Provide functions that return preconfigured prop objects:

```typescript
function useToggle() {
  const [on, setOn] = useState(false);

  const getTogglerProps = (props?: ButtonHTMLAttributes<HTMLButtonElement>) => ({
    'aria-pressed': on,
    onClick: () => setOn(prev => !prev),
    ...props,
  });

  return { on, getTogglerProps };
}
```

---

## 10. Error Boundaries & Error Handling

### Error Boundary Setup

Use the `react-error-boundary` library (functional component based):

```typescript
import { ErrorBoundary, FallbackProps } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert" className="p-4 rounded-default bg-danger/10 text-danger">
      <h2 className="font-bold">Something went wrong</h2>
      <p className="text-sm">{error.message}</p>
      <button onClick={resetErrorBoundary} className="mt-2 btn-base">
        Try again
      </button>
    </div>
  );
}

// Place boundaries strategically around failure-prone areas
function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <Layout>
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <Dashboard />
        </ErrorBoundary>
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <Sidebar />
        </ErrorBoundary>
      </Layout>
    </ErrorBoundary>
  );
}
```

### React 19 Error Hooks

```typescript
// In createRoot or hydrateRoot
createRoot(document.getElementById('root')!, {
  onUncaughtError: (error, errorInfo) => {
    // Errors not caught by any error boundary
    reportToSentry(error, errorInfo);
  },
  onCaughtError: (error, errorInfo) => {
    // Errors caught by an error boundary
    reportToSentry(error, errorInfo);
  },
}).render(<App />);
```

### What Error Boundaries Do NOT Catch

- Event handlers (use `try-catch`).
- Async code (`setTimeout`, promises -- use `try-catch`).
- Server-side errors.
- Errors in the boundary itself.

### Layered Error Handling Strategy

```typescript
// 1. Error boundaries for rendering errors (automatic)
// 2. try-catch for event handlers
async function handleSubmit() {
  try {
    await submitForm(data);
  } catch (error) {
    setError(error instanceof Error ? error.message : 'Unknown error');
  }
}

// 3. TanStack Query for data fetching errors
const { data, error, isError } = useQuery({ ... });

// 4. Global error logging
// Use onUncaughtError/onCaughtError + Sentry/Datadog/LogRocket
```

### Best Practices

- **Place boundaries strategically** -- not one giant boundary, but granular boundaries around independent sections.
- **Always provide a meaningful fallback** with a retry option.
- **Log all errors** to a monitoring service (Sentry, Datadog, LogRocket).
- **Test your error boundaries** by intentionally breaking components.
- For data fetching errors, TanStack Query's `isError`/`error` states provide built-in handling.

---

## 11. Performance Optimization

### Priority Order (High Impact First)

1. **React Compiler** (if available): Automatic memoization. Delivers 60-80% of potential improvements with zero effort.
2. **Code splitting / lazy loading**: Reduce initial bundle by 20-70%.
3. **Proper state architecture**: Keep state local, use TanStack Query for server state.
4. **Image optimization**: Next/Image, lazy loading, proper formats (WebP/AVIF).
5. **Manual memoization**: `useMemo`, `useCallback`, `React.memo` for confirmed bottlenecks.

### Code Splitting

```typescript
import { lazy, Suspense } from 'react';

const AdminPanel = lazy(() => import('./features/admin/AdminPanel'));
const SettingsPage = lazy(() => import('./features/settings/SettingsPage'));

// With TanStack Router, code splitting is built into file-based routing
// Each route component is automatically lazy-loaded
```

### Memoization Rules

```typescript
// USE useMemo for expensive computations
const sortedItems = useMemo(
  () => items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// USE useCallback for stable function references passed to memoized children
const handleDelete = useCallback(
  (id: string) => deleteMutation.mutate(id),
  [deleteMutation.mutate]
);

// USE React.memo for components that re-render often with same props
const ExpensiveRow = memo(function ExpensiveRow({ data }: RowProps) {
  return <ComplexVisualization data={data} />;
});

// DON'T memoize everything -- profile first!
// The cost of memoization (storing + comparing) can exceed the cost of re-rendering
```

### Virtualization

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
            }}
          >
            {items[virtualItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Additional Guidelines

- **Debounce** search inputs, window resize handlers, and scroll handlers.
- **Avoid anonymous functions in JSX** when passing to memoized children.
- **Split Context providers** into smaller, specific providers to limit re-render scope.
- **Memoize Context values** with `useMemo` to prevent all consumers from re-rendering.
- **Profile with React DevTools Profiler** before optimizing -- find bottlenecks, don't guess.

---

## 12. Testing (Vitest + React Testing Library)

### Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: true,
  },
});
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

### Core Principles

1. **Test behavior, not implementation.** Focus on what users see and do.
2. **Use accessible queries.** Prefer `getByRole`, `getByLabelText`, `getByText` over `getByTestId`.
3. **Prefer `userEvent` over `fireEvent`.** `userEvent` simulates real user interactions.

### Query Priority (Most to Least Preferred)

1. `getByRole` -- accessible to everyone
2. `getByLabelText` -- good for form fields
3. `getByPlaceholderText` -- when label is not available
4. `getByText` -- for non-interactive elements
5. `getByDisplayValue` -- for filled form elements
6. `getByAltText` -- for images
7. `getByTitle` -- rarely used
8. `getByTestId` -- last resort only

### Writing Tests

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

describe('LoginForm', () => {
  it('submits with valid credentials', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    });
  });

  it('shows validation error for invalid email', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);

    await user.type(screen.getByLabelText(/email/i), 'invalid');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByRole('alert')).toHaveTextContent(/valid email/i);
  });
});
```

### Testing Async Components

```typescript
it('loads and displays user data', async () => {
  render(<UserProfile userId="123" />, { wrapper: createTestWrapper() });

  // Use findBy for async content (includes waitFor internally)
  const heading = await screen.findByRole('heading', { name: /john doe/i });
  expect(heading).toBeInTheDocument();
});
```

### Test Utilities

```typescript
// Create a wrapper with providers for testing
function createTestWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}
```

### Best Practices Summary

- Each test should verify a single behavior.
- Mock only what is necessary to isolate the unit under test.
- Extract common setup into helper functions/fixtures.
- Use `vi.fn()` for mock functions, `vi.mock()` for module mocking.
- Prefer integration tests (rendering full component trees) over unit tests of individual functions.
- Use `screen.debug()` to inspect rendered output when debugging.

---

## 13. Accessibility (a11y)

### Semantic HTML First

- Use `<button>` for buttons, not `<div onClick>`.
- Use `<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, `<article>` for page structure.
- Use `<ul>/<ol>/<li>` for lists.
- Use `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>` for tabular data.
- Use `<form>`, `<label>`, `<fieldset>`, `<legend>` for forms.

### ARIA Attributes

```typescript
// Icon-only button
<button aria-label="Close dialog" onClick={onClose}>
  <XIcon />
</button>

// Modal/dialog
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Delete</h2>
  ...
</div>

// Toggle button
<button aria-pressed={isActive} onClick={toggle}>
  Dark Mode
</button>

// Expandable section
<button aria-expanded={isOpen} aria-controls="panel-1" onClick={toggle}>
  Details
</button>
<div id="panel-1" hidden={!isOpen}>
  Panel content
</div>

// Live region for dynamic updates
<div role="status" aria-live="polite">
  {statusMessage}
</div>

// Error message association
<input
  id="email"
  aria-invalid={!!error}
  aria-describedby={error ? 'email-error' : undefined}
/>
{error && <p id="email-error" role="alert">{error}</p>}
```

### Keyboard Navigation

- All interactive elements must be reachable via Tab.
- Custom components must handle Enter, Space, Escape, and Arrow keys as appropriate.
- **Never remove focus outlines** unless replacing with a clearly visible alternative.
- Trap focus inside modals/dialogs.
- Return focus to the trigger element when a modal closes.

### Color & Visual

- Minimum contrast ratio: **4.5:1** for normal text, **3:1** for large text (WCAG AA).
- Never convey information by color alone -- always pair with text, icons, or patterns.
- Respect `prefers-reduced-motion` for animations.
- Respect `prefers-color-scheme` for dark mode.

### Forms

- Every input must have an associated `<label>`.
- Group related inputs with `<fieldset>` and `<legend>`.
- Associate error messages with `aria-describedby`.
- Use `aria-required="true"` for required fields (or HTML `required` attribute).

### Testing Accessibility

- **ESLint**: `eslint-plugin-jsx-a11y` for static analysis.
- **Browser**: Axe DevTools extension for runtime audits.
- **Unit tests**: `vitest-axe` or `jest-axe` for automated a11y assertions.
- **Manual**: Test with keyboard-only navigation and a screen reader (VoiceOver on macOS, NVDA on Windows).
- **Storybook**: `addon-a11y` for interactive component testing.

### Legal Requirements

The European Accessibility Act (EAA) requires WCAG compliance for digital products as of June 2025. ADA compliance is enforced in the US. Accessibility is a legal requirement, not optional.

---

## 14. Project Structure

### Feature-Based Architecture (2025 Standard)

```
src/
├── app/                    # App-level setup
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   ├── router.tsx          # Router configuration
│   └── providers.tsx       # Global providers (QueryClient, etc.)
│
├── features/               # Feature modules (business domains)
│   ├── auth/
│   │   ├── components/     # Feature-specific components
│   │   ├── hooks/          # Feature-specific hooks
│   │   ├── api/            # API calls and query definitions
│   │   ├── types.ts        # Feature types
│   │   ├── utils.ts        # Feature utilities
│   │   └── index.ts        # Public API (barrel export)
│   ├── users/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── types.ts
│   │   └── index.ts
│   ├── dashboard/
│   └── settings/
│
├── shared/                  # Shared/reusable code
│   ├── components/          # Generic UI components (Button, Modal, etc.)
│   ├── hooks/               # Generic hooks (useDebounce, useLocalStorage)
│   ├── utils/               # Pure utility functions
│   ├── types/               # Shared TypeScript types
│   └── lib/                 # Third-party library wrappers
│
├── routes/                  # TanStack Router file-based routes
│   ├── __root.tsx
│   ├── index.tsx
│   └── users/
│       ├── index.tsx
│       └── $userId.tsx
│
├── assets/                  # Static assets (images, fonts)
├── styles/                  # Global CSS, Tailwind theme
│   └── app.css
└── test/                    # Test setup and utilities
    ├── setup.ts
    └── utils.tsx
```

### Key Principles

1. **Features are self-contained modules.** Each feature folder contains everything related to that business domain.
2. **Public API via `index.ts`**: Each feature exports only what other features need. Internal implementation is hidden.
3. **Shared code is truly shared.** Only put code in `shared/` if it is used by 2+ features.
4. **Avoid deep nesting.** Maximum 3-4 levels deep.
5. **Colocation**: Keep related code together. Tests next to source files (`UserList.tsx` / `UserList.test.tsx`).

### Naming Conventions

- **PascalCase**: Components (`UserProfile.tsx`), types (`UserProfile`)
- **camelCase**: Hooks (`useUserProfile.ts`), utilities (`formatDate.ts`), variables
- **kebab-case**: CSS files, route files (when not using PascalCase components)
- **UPPER_SNAKE_CASE**: Constants (`MAX_RETRY_COUNT`)

### Feature Module Public API

```typescript
// features/users/index.ts
// Only export what other features need
export { UserList } from './components/UserList';
export { UserAvatar } from './components/UserAvatar';
export { useUser } from './hooks/useUser';
export type { User, UserRole } from './types';
```

---

## 15. Code Quality (ESLint, Prettier, TypeScript Config)

### ESLint Flat Config (2025)

```javascript
// eslint.config.mjs
import eslint from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';
import prettierRecommended from 'eslint-plugin-prettier/recommended';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import reactHooks from 'eslint-plugin-react-hooks';

export default defineConfig(
  // Global ignores
  { ignores: ['dist/', 'node_modules/', '**/*.d.ts', 'coverage/', '.vinxi/'] },

  // Base configs
  eslint.configs.recommended,
  prettierRecommended,

  // TypeScript files
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
    ],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'jsx-a11y': jsxA11y,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
    },
  },

  // JavaScript files (disable type-checked rules)
  {
    files: ['**/*.{js,mjs}'],
    extends: [tseslint.configs.disableTypeChecked],
  }
);
```

### Prettier Configuration

```javascript
// prettier.config.js
export default {
  semi: true,
  singleQuote: true,
  trailingComma: 'all',
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  bracketSpacing: true,
  arrowParens: 'always',
  endOfLine: 'lf',
  plugins: ['prettier-plugin-tailwindcss'],
};
```

### TypeScript Configuration

See Section 2 for the full strict `tsconfig.json`. Key flags:

- `"strict": true` -- enables all strict checks.
- `"noUncheckedIndexedAccess": true` -- array/object indexing returns `T | undefined`.
- `"moduleResolution": "bundler"` -- modern resolution for Vite/esbuild.
- `"isolatedModules": true` -- required for Vite/esbuild.

### Pre-Commit Hooks

Use `husky` + `lint-staged` for pre-commit quality gates:

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,css}": ["prettier --write"]
  }
}
```

### Recommended Configuration Tiers

- **`recommended`**: Drop-in correctness rules. Good starting point.
- **`strict`**: Recommended + opinionated rules that catch more bugs.
- **`strict-type-checked`**: Strict + rules that use TypeScript's type checker. **Use this if your team is proficient in TypeScript.**
- **`stylistic`**: Consistent code style (naming conventions, type annotations style).

### Best Practices

1. **Use flat config** (`eslint.config.mjs`). Legacy `.eslintrc` is deprecated.
2. **Let Prettier handle all formatting.** Never use ESLint for formatting rules.
3. **Enable `projectService: true`** for full type-aware linting.
4. **Use `tseslint.configs.disableTypeChecked`** for plain `.js` files.
5. **Add `eslint-plugin-jsx-a11y`** for accessibility linting.
6. **Add `eslint-plugin-react-hooks`** to enforce Rules of Hooks.
7. **Sort Tailwind classes** with `prettier-plugin-tailwindcss`.
8. **Enforce via CI**: Run `tsc --noEmit`, `eslint .`, and `prettier --check .` in your CI pipeline.

---

## Summary: Quick Reference Decision Table

| Decision | Recommendation |
|---|---|
| Components | Functional components only, with hooks |
| Typing | TypeScript strict mode, Zod for runtime validation |
| Data fetching | TanStack Query v5 (`useSuspenseQuery` preferred) |
| Routing | TanStack Router (file-based, type-safe) |
| Tables | TanStack Table (headless, memoize data/columns) |
| Forms | TanStack Form + Zod validation |
| Styling | Tailwind CSS v4 with `@theme` design tokens |
| Server state | TanStack Query (never use Redux/Zustand for this) |
| Client state | Zustand for global, Jotai for atomic, URL for shareable |
| Error handling | `react-error-boundary` + try-catch + monitoring |
| Performance | React Compiler first, then code-split, then manual memo |
| Testing | Vitest + React Testing Library, test behavior not implementation |
| Accessibility | Semantic HTML, ARIA, keyboard nav, color contrast, automated testing |
| Project structure | Feature-based folders with public API barrel exports |
| Linting | ESLint flat config + typescript-eslint strict + Prettier |

---

*Last updated: January 2025. Based on React 19.2, TanStack Query v5, TanStack Router v1, TanStack Table v8, TanStack Form v1, Tailwind CSS v4, TypeScript 5.x, ESLint 9.x flat config.*
