# ARCHITECTURE.md
Deep-dive reference for architecture, file structure, and system design.
For quick-reference instructions see `CLAUDE.md`.
For decision rationale see `ADR/`.

## Tech stack overview
This is a full-stack web application with an AI agent orchestration layer.
 
| Layer | Choice |
|---|---|
| Frontend | React, Vite, React Router, Recharts, Tailwind CSS |
| Backend | FastAPI |
| Agent orchestration | LangGraph |
| Data source/services | yfinance, LLM API (TBC) |
| Data engineering | pandas/polar (TBC) |
| Cache | Upstash Redis (TBC) |
| Database | PostgreSQL via Supabase/Railway/Neon (TBC) |
| Auth | Clerk (TBC) |
| Deployment | Vercel (frontend), Railway Docker (backend) |
| Design | Figma |
| Planning | Notion |
