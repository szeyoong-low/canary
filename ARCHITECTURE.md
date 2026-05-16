# ARCHITECTURE.md
Deep-dive reference for architecture, file structure, and system design.
For quick-reference instructions see `CLAUDE.md`.
For decision rationale see `ADR/`.

## Tech stack overview
This is a full-stack web application with an AI agent orchestration layer.
 
| Layer | Choice |
|---|---|
| Frontend | React(TypeScript), Vite, React Router, Recharts/Apache ECharts,
             Tailwind CSS |
| Backend | FastAPI, Python 3.12, Postman |
| Agent orchestration | LangGraph |
| Data source/services | yfinance, LLM API (TBC) |
| Data engineering | pandas/polar (TBC) |
| Cache | Upstash Redis (TBC) |
| Database | PostgreSQL via Supabase/Railway/Neon (TBC) |
| Auth | Clerk/Auth.js/BetterAuth (TBC) |
| Deployment | Vercel (frontend), Railway (backend), Docker |
| Package manager | npm (frontend), uv (backend) |
| CI/CD | Git |
| Design | Figma |
| Planning | Notion |