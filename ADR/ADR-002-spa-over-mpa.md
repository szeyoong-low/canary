# ADR-002 — Single page app with query parameters encoded in URL

## Decision
Build the frontend as a Single Page Application (SPA) using React Router v6.
Encode chart query parameters in the URL as search parameters rather than
holding them in React component state.

## Context
- The core UI is a persistent dashboard — sidebar, chart panel, and insight panel
update in place without full page reloads.
- Chart queries should be shareable and bookmarkable.

## Reasoning
### SPA over MPA
The interaction model is a dashboard, not a content site.
A multi-page app (server-rendered per route) would require a full page reload
on every query, losing the highly responsive feel of a native app.
React Router v6 gives client-side navigation with a persistent layout shell.

### URL-encoded state over React state
Storing data about the chart as URL search params (e.g. `/terminal?tickers=NVDA,AMD&metric=price&years=5`) means:
- Charts are bookmarkable and shareable via URL.
- The browser back/forward buttons work correctly — pressing back restores
  the previous query.
- On hard refresh, the query is not lost.
- Deep linking works out of the box.

React Router's `useSearchParams` hook reads and writes search params. On form
submit, call `setSearchParams(newParams)` instead of `setState`. On mount, read
params to pre-fill the form. The URL is the single source of truth for query
state.

## Consequences
- The `AppShell` component renders once and never unmounts; only the `<Outlet />`
  content swaps between routes.
- Do not add React Router until Phase 2 — Phase 1 is a single view with no
  routing needed. Use plain React state for the form in Phase 1, then migrate
  to `useSearchParams` when routing is introduced.
- In Phase 3, auth state is managed by Clerk, not the URL.

## Revisit if
SEO becomes a requirement (e.g. public-facing chart pages that need to be
indexed). At that point, consider server-side rendering with Next.js and
migrate the routing layer.