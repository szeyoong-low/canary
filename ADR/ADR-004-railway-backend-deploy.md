# ADR-004 — Railway for backend deployment

## Decision
Deploy the FastAPI backend on Railway rather than Render.

## Context
Both are PaaS providers that run Docker containers with minimal configuration.
The backend needs to serve REST and SSE, and will gain a co-located database
instance in Phase 3. The project is a learning build with fast iterations and
frequent deploys.

## Reasoning
### CLI-first workflow
Railway's CLI (`railway up`, `railway logs`, `railway shell`) covers the full
deploy-debug loop without leaving the terminal.
This fits naturally alongside a Claude Code workflow where everything happens in
the terminal. Render's CLI is thinner and most operations push toward the web
dashboard.

### Co-located services
Railway provisions databases like Postgres and Redis as first-class services
within the same project. Environment variables (`DATABASE_URL`, `REDIS_URL`)
are automatically injected into the backend container — no manual
copy-pasting of connection strings between dashboards. When Phase 3 adds
these services, it's one command or click away.

### No cold starts
Railway keeps containers warm continuously. Render's free
tier spins services down after 15 minutes of inactivity, adding a ~30 second
cold-start penalty on the first request — unacceptable for an SSE streaming
endpoint where the connection needs to open immediately.

## Trade-offs accepted
### Cost
Railway's free trial is time-limited; after that it's pay-as-you-go
(typically $2–5/month at low traffic). Render's free tier runs indefinitely at
no cost. This is acceptable for a learning project where the monthly cost is
negligible, but Render would be the better choice under a hard zero-budget
constraint.

### Track record
Render has a longer operational history and a slightly stronger
uptime reputation. Not a meaningful concern for a learning project.

## Revisit if
May need to revisit when real users come on after public release.