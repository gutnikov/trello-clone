# Doc Impact Analysis: TRE-40

## Overview

TRE-40 introduces the board route and read-only display components — the first frontend UI layer for the Trello clone. This includes four React components (`Board`, `BoardList`, `BoardCard`, `EmptyBoard`), a `/board` route using TanStack Router, an API proxy in `server.js` for production SSR, and SSR-aware API base URL resolution.

---

## Impacted Documents

### 1. `docs/agents/implementation.md` — Frontend Component & Route Patterns

- **Impact:** HIGH — Update required
- **Reason:** TRE-40 creates the first frontend components and route. Future agents building UI features need to know the component structure pattern, the route creation pattern, and the SSR/API proxy architecture.
- **Action:** Add sections documenting:
  - Frontend component pattern: named exports, TypeScript interfaces for props, `data-testid` attributes, Tailwind CSS classes
  - Route creation pattern: `createFileRoute` with `useBoard()` hook, loading/error/empty states
  - SSR + API proxy: `server.js` proxies `/api/*` to backend, `api.ts` uses `getApiBase()` for SSR vs client URL resolution
  - Router SSR integration: `QueryClient` creation in `router.tsx` with `setupRouterSsrQueryIntegration`

### 2. `docs/agents/design-feedback-loop.md` — Frontend Component Test Patterns

- **Impact:** MEDIUM — Update required
- **Reason:** TRE-40 adds the first frontend component tests (`frontend/tests/board-components.test.tsx`) using `@testing-library/react`. The design feedback loop agent doc should reference this as the canonical pattern for future component test scaffolds.
- **Action:** Add a subsection documenting:
  - Component test pattern using `@testing-library/react` with `render`, `screen`, and `within`
  - E2E test pattern with API-based data seeding and cleanup (`frontend/e2e/board.spec.ts`)

### 3. `docs/agents/implementation.md` — Pre-commit Hooks

- **Impact:** LOW — Minor update
- **Reason:** TRE-40 adds `mypy` and `tsc --noEmit` pre-commit hooks. Agents should know these run automatically on commit.
- **Action:** Mention the pre-commit type-checking hooks under the existing Style section.

---

## Documents NOT Impacted

| Document | Reason |
|---|---|
| `CLAUDE.md` | No structural changes to the project map |
| `docs/conventions/golden-principles.md` | No new conventions introduced |
| `docs/guides/workflow-customization.md` | Orca workflow unchanged |
| `docs/agents/scoping.md` | Scoping process unchanged |
| `docs/agents/planning.md` | Planning process unchanged |
| `docs/agents/validation.md` | Validation process unchanged |
| `docs/agents/docs-update.md` | Docs process unchanged |
| `docs/architecture/` | No new architectural decisions — components follow standard React patterns, SSR proxy is standard infrastructure |
| `docs/runbooks/deploy-prod.md` | API proxy is transparent to deployment — same Docker Compose setup |
| `README.md` | No new API endpoints or configuration changes |

---

## Summary

| Document | Impact Level | Action |
|---|---|---|
| `docs/agents/implementation.md` | High | **Update** — add frontend component pattern, route pattern, SSR/API proxy, pre-commit hooks |
| `docs/agents/design-feedback-loop.md` | Medium | **Update** — add frontend component test pattern and E2E data seeding pattern |
