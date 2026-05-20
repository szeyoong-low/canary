Here's the current state of the project:

- Backend (main.py): FastAPI skeleton with CORS middleware and a / health check. No business logic.
- Frontend (App.tsx): Vite + React boilerplate. No app content.
- Infrastructure: Deployed to Railway (backend) and Vercel (frontend) with CI/CD in place.

---
Next milestone

The roadmap calls for two things to be built together:

1. POST /api/test — fetches capex and revenue from yfinance for the Big 5 hyperscalers (AAPL, MSFT, GOOGL, AMZN, META), computes the ratio, and returns a
chart config JSON
2. A single frontend page — calls the endpoint on load and renders a chart from the response

---
Suggested approach

Backend

yfinance exposes a Ticker object with .financials (income statement) and .cashflow (cash flow statement). Capex lives in the cash flow as Capital
Expenditure and revenue in the income statement as Total Revenue. A thin pandas transformation computes the ratio across years.

The endpoint returns a chart config JSON — a plain data structure the frontend can directly feed to the charting library. For example:

```json
{
    "title": "Capex/Revenue Ratio — Big 5 Hyperscalers",
    "xAxis": ["2021", "2022", "2023", "2024"],
    "series": [
        { "name": "Apple",     "data": [0.05, 0.06, 0.05, 0.04] },
        { "name": "Microsoft", "data": [0.09, 0.10, 0.11, 0.12] }
    ]
}
```

This shape is deliberately charting-library-agnostic for now, so we can switch libraries later.

Frontend — charting library decision (ADR needed)

The architecture doc lists two candidates: Recharts and Apache ECharts. This is the main architectural decision before writing any frontend code.


| | Recharts | Apache ECharts (via echarts-for-react) |
|---|---|---|
| API style | Declarative JSX components | Config object passed as prop |
| Learning  | Low — feels like React | Medium — separate config vocabulary |
| Chart variety | Good for standard charts | Much wider (heatmaps, candlesticks, etc) |
| Bundle size | ~150 kB | ~1 MB (tree-shakeable) |
| Community | React-first, well maintained | Backed by Apache, very mature |

For Phase 1 (a single line/bar chart), Recharts is the better starting point — smaller, simpler, and you'll understand every line. ECharts becomes worth
it once you need exotic chart types in Phase 2+. That said, if Phase 2 ends up needing things like candlestick charts, switching later is non-trivial.
Worth deciding consciously.

Sources:
- Recharts docs (https://recharts.org/en-US/)
- echarts-for-react (https://github.com/hustcc/echarts-for-react)
- yfinance financials (https://ranaroussi.github.io/yfinance/reference/yfinance.Ticker.html)

---
Proposed sequence (one file at a time)

1. Add yfinance and pandas to backend dependencies (pyproject.toml)
2. Write the POST /api/test endpoint in main.py
3. Pick a charting library and install it on the frontend
4. Replace App.tsx boilerplate with the chart page

Before I write anything: which charting library do you want to go with? And does this plan look right to you?