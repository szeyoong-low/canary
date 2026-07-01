# Contributing

## Local dev

Run each server in a separate terminal.

```bash
# Backend (from /backend)
uv run fastapi dev   # http://localhost:8000

# Backend Docker test
docker build -t canary-backend .
docker run -p 8000:8000 canary-backend

# Frontend (from /frontend)
npm run dev          # http://localhost:5030
```