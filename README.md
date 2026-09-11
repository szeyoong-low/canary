# <img src="frontend/public/favicon.svg" height="32" align="top"> Canary crystallises chaos into charts
**[Canary](https://canary.markets)** is an agentic analyst who uncovers business stories hidden in data. You can interact with it just like how you would prepare a report or write scripts on a Jupyter Notebook.

<table>
    <tr>
        <td width="500" align="center"><img src="public/landing-page.png" alt="Landing page for unauthenticated users" width="500"/></td>
        <td width="500" align="center"><img src="public/report-page-top.png" alt="Report page (top)" width="500"/></td>
    </tr>
<table>

> **Disclaimer:** This project is still in development. The user experience and functionality may differ from what is described in documentation.

## Architecture
<div align="center">
    <img src="public/infrastructure.png" width=800>
    <p>
        <a href="https://lucid.app/lucidchart/c42a4a91-df21-4cbd-8531-80d03def2023/edit?viewport_loc=-2084%2C-780%2C3105%2C1505%2C0_0&invitationId=inv_acd69b55-1da8-4e08-a279-c3a66c4b2fc0">
            Architecture diagram on Lucidchart
        </a>
    </p>
</div>



Check out [the project wiki](https://github.com/szeyoong-low/canary/wiki) for deep dives on my design process.

## Tech stack 
| Layer | Choice |
|---|---|
| Frontend | React (Compiler), TypeScript, Vite, React Router, Apache ECharts, Zod, OpenAPI Fetch, Tailwind CSS, Base UI |
| Backend | FastAPI, Python 3.12, httpx, Pydantic, OpenAPI TypeScript |
| Data sources | Financial Modelling Prep |
| Data pipeline | Polars |
| Database | PostgreSQL, SQLAlchemy, asyncpg, Alembic, dbeaver, AWS boto3 SDK |
| Authentication | Auth0, pyjwt |
| AI agent | LangGraph, OpenRouter |
| Deployment | AWS, Cloudflare Workers, Terraform, Docker |
| DevOps | Git, GitHub Actions, npm, uv, Ruff, ESLint, Prettier, Lefthook |
| Testing | pytest asyncio, unittest mock, Postman |
| Coding agent | Claude Code (Skills, MCP) |
| Design & diagramming | Figma, Mermaid, Lucidchart |