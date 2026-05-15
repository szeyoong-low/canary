# ADR-007 — FastAPI CORSMiddleware to handle browser Same-Origin Policy

## Decision
Handle cross-origin requests by configuring `CORSMiddleware` on the FastAPI
backend, rather than using Vite's `server.proxy` to work around the browser's
same-origin policy.

## Context
The browser's same-origin policy blocks requests between different origins (different port = different origin) unless the server explicitly opts in with CORS headers. You'd get a blocked request in the browser console.
In development the frontend runs on port 5030 and the backend on port 8000;
in production they are on entirely different domains (Vercel and Railway).
A mechanism is needed to allow the frontend to call the backend in both
environments.

## Reasoning
### Why not the Vite proxy
The Vite proxy sidesteps this entirely in development by intercepting requests on the dev server. The browser makes a request to `localhost:5030/api/...` (same origin, no CORS check), and Vite's dev server forwards it to `localhost:8000` server-side., so the browser never makes a cross-origin request
(server-to-server requests aren't subject to CORS). This has two drawbacks:

1. **Dev-only.** The Vite dev server does not exist in production. A second
   mechanism (CORSMiddleware) would be needed for production anyway, meaning
   two configs to maintain instead of one.
2. **Misleading.** The dev environment does not reflect production behaviour.
   Cross-origin requests that would be blocked in production appear to work
   fine in dev, masking configuration gaps until deployment.

### Why CORSMiddleware
`CORSMiddleware` is a standard ASGI middleware that adds the HTTP headers
(`Access-Control-Allow-Origin`, etc.) that tell the browser to permit the
cross-origin request. It works identically in dev and production — one config,
no environment-specific surprises.

It also makes CORS explicit and visible, which is educationally valuable.

### Environment variable for allowed origins
Allowed origins differ between environments (localhost in dev, Vercel domain
in production). These are stored in an `ALLOWED_ORIGINS` environment variable
read at startup, keeping secrets and environment-specific values out of source
code.

## Consequences
Before deploying to production, `ALLOWED_ORIGINS` must be updated in the
Railway environment to include the Vercel frontend domain and remove
`http://localhost:5030`.

The frontend cannot use relative paths (e.g. `fetch('/api/test')`) because
requests go directly to the backend, not through a proxy. The backend base URL
is stored in a `VITE_API_BASE_URL` environment variable and used to construct
absolute URLs in frontend fetch calls.

## Trade-offs accepted
Slightly more setup than the proxy (two environment variable files instead of
none). The benefit of a unified, honest config outweighs this.

## Revisit if
Highly unlikely. CORSMiddleware is the standard FastAPI solution and has no
meaningful drawbacks at this scale.
