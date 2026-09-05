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

## Migrations
```bash
# Auto-generate migration file
uv run alembic revision --autogenerate -m "<title>"

# Preview raw SQL DDL
uv run alembic upgrade base:head --sql

# Test migrations
uv run alembic upgrade head && \
uv run alembic downgrade base && \
uv run alembic upgrade head

docker compose exec postgres psql -U canary_admin -d canary -c '\d app_user'
```

## The application role

The backend does not connect as the owner. Migrations run as `canary_admin`, requests are served as `canary_app`.

On RDS `canary_app` authenticates with a short-lived IAM token and never has a password. There is no IAM locally, so it needs one set out of band.

Run this **after** `alembic upgrade head`, which is what creates the role:

```bash
# From /backend, with DATABASE_APP_USERNAME and DATABASE_APP_PASSWORD set in .env
set -a && . ./.env && set +a

docker compose exec -T postgres \
  psql -U "$DATABASE_USERNAME" -d "$DATABASE_NAME" \
  -v role="$DATABASE_APP_USERNAME" -v pw="$DATABASE_APP_PASSWORD" <<'SQL'
ALTER ROLE :"role" WITH PASSWORD :'pw';
SQL
```

`:"role"` interpolates a quoted identifier and `:'pw'` a quoted string literal, so
psql escapes both. Building the statement by string concatenation instead would
break on any password containing a quote — which the RDS-generated ones do.

`ALTER ROLE` is idempotent, so re-run it whenever the password in `.env` changes.

Two rules this schema relies on that nothing enforces yet:

- **Adding a column to a soft-deletable table means `CREATE OR REPLACE VIEW`** for its `_live` view, so the new column is invisible to every read path until the view is replaced.

- **Adding a table means granting on it.** `canary_app` is given rights explicitly, so a new table is unreachable until a migration grants on it.