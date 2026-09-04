# Contributing

## Local dev

Run each server in a separate terminal.

The backend will not start without a database, so bring that up first.

```bash
# Database (from /database)
# Holds until Postgres accepts connections, not merely until the container starts.
# Idempotent, unlike `docker run` (need to run `docker start` subsequently)
docker compose up --wait --detach # http://localhost:5432

# Backend (from /backend)
uv run fastapi dev # http://localhost:8000

# Frontend (from /frontend)
npm run dev # http://localhost:5030

# Backend Docker test
docker build -t canary-backend .
docker run -p 8000:8000 canary-backend
```

Data persists across restarts in a named volume. Use `docker compose down --volumes` to drop the existing local database.