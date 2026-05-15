# ADR-006 — React TypeScript without compiler or framework mode

## Decision
Use the standard Vite React + TypeScript template. Do not use the React Compiler
variant or React Router v7 framework mode.

## Context
The Vite CLI offers three React variants: TypeScript, TypeScript + React Compiler,
and React Router v7. The frontend is a SPA that communicates with a separate
FastAPI backend over HTTP.

## Reasoning
### React Router v7 ruled out
React Router v7 in the Vite CLI is a full-stack meta-framework (the successor to
Remix), not just a router library. It includes server-side rendering and server
data loaders, which would blur the frontend/backend separation established in
ADR-001 and conflicts with the plan in ADR-002 to add React Router as a library
in Phase 2.

### React Compiler deferred
The React Compiler (shipped with React 19) automatically inserts memoisation at
build time, removing the need to write `useMemo`, `useCallback`, and `memo`
manually. For a learning project, this abstracts away React's rendering model
before it has been understood. Plain TypeScript keeps that model visible, which
is the better choice at this stage. The compiler can be enabled later as a
one-line config change.

## Consequences
- Re-render optimisation is manual. Components are wrapped in `memo`,
  values in `useMemo`, and callbacks in `useCallback` when needed.
- React Router is added as a library (`react-router-dom`) in Phase 2, not as
  a framework.

## Trade-offs accepted
More boilerplate for memoisation compared to the compiler variant. Acceptable
given the learning objective of understanding React's rendering model.

## Revisit if
The project grows to a point where manual memoisation becomes a maintenance
burden. Enabling the React Compiler at that point is low-risk.
