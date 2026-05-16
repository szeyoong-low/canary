# Contributing

## Local dev

Run each server in a separate terminal.

```bash
# Backend — from /backend
uv run fastapi dev   # http://localhost:8000

# Frontend — from /frontend
npm run dev          # http://localhost:5030
```

## Environment variables

The frontend and backend follow different conventions.

### Backend — gitignored `.env`

The backend's `.env` is **not committed**. It will accumulate secrets (API
keys, database URLs, etc.) over time, so it is excluded unconditionally from
the start.

In production, variables are set directly in the Railway dashboard — no `.env`
file is deployed.

### Frontend — committed `.env.development`

The frontend follows Vite's named environment file convention. Files are
committed if they contain no secrets; files with a `.local` suffix are never
committed.

| File | Committed | Purpose |
|---|---|---|
| `.env.development` | Yes, if no secrets | Shared dev defaults (e.g. backend URL) |
| `.env.*.local` | No | Personal overrides, may contain secrets |

The `VITE_` prefix is required on any variable that needs to be readable in
browser code (e.g. `VITE_API_BASE_URL`). Variables without this prefix are
stripped from the bundle at build time.

In production, variables are set in the Vercel dashboard and injected at build
time.
