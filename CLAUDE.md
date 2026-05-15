# CLAUDE.md

## About this project
Canary is a full-stack agentic financial terminal. Users ask free-text questions;
an AI agent fetches data, transforms it, and returns an interactive chart with
concise insights synthesised by a LLM.

## Phases
1. Basic full stack app deployed to production. Able to fetch financial data
   from an external API, transform it, and chart a computed metric (e.g.
   Capex to revenue ratio).
2. Agentic workflow that takes a free-text query and uses a data pipeline to
   dynamically generate the answer.
3. Add authentication, so that users can save their charts.

Afterwards, expand the variety of analysis that can be performed, and allow more
data sources to be incorporated.

## Way of working — read before answering my prompts
The highest priority of this project is learning. I want to be capable of making
architectural decisions and reason about them. I would like the pace to be
manageable so that I can stay in control. Treat me as a rookie in web development
and agentic engineering, but also treat me as the person with the final say over
every detail in this project.

- My aim is to build a minimum viable product while making good design choices
  that scale well. Everything else is secondary.
- I will break work down into bite-sized chunks. Only work on these atomic
  pieces, **do not do more than asked for**.
- However, you are more than welcome to **challenge my decisions**
  constructively and suggest **potential improvements** and **next steps**.
- Instead of giving you objectives to fulfil (e.g. Build this feature), I will
  pose **questions** (e.g. How can this be built?)
- Start off by **suggesting an approach**, and always explain your architectural
  decisions like I'm a **first-timer** but **be concise**. I want to have a full
  understanding of the solution's rationale before any code is written.
- Give me **sources** where I can read more about these architectural details.
- Wait for my **explicit go ahead** before writing code. For any significant
  tradeoffs, draft an architectural decision rational markdown file
  (e.g. `ADR-001-spa-over-mpa.md`) in the `ADR/` directory. **Do not** update
  `ARCHITECTURE.md`, I will do it myself.
- Make **as few changes as possible**. Explain what every change does and why
  **before** creating it. **One file at a time.** Wait for approval before
  moving to the next step.
- Prefer **simple, readable, and maintanable over clever**. No unnecessary
  abstractions, we can always refactor later.
- If a problem has a well-documented solution or design pattern regarded
  by industry as **best practice**, use it. If a library or external service can
  solve it, use it. I want to focus on building the interesting parts rather
  than reinventing the wheel. If there are real concerns about maintainability,
  we can refactor this later on.
- **Comment** every non-obvious line.
- If a task touches multiple concerns, **split** it into sequential steps.
- **Never run destructive commands** (e.g. drop tables, delete files, reset DBs)
  without explicit confirmation.
- Explain error messages before fixing them — **teach, don't just patch**. Let
  me try to debug first, don't give me the solution.
- Make sure you give me a heads up before **copying** or lightly adapting code
  from a single source. I may need to give acknowledgements as this is a
  portfolio project.

## Progress checklist
### Phase 1

**Goal:** Basic full stack app deployed to production.
          Able to fetch financial data from an external API, transform it, and
          chart a computed metric (e.g. Capex to revenue ratio).

**Done when:** User loads the page and gets a comparison of the Big 5
               hyperscalers' Capex to revenue ratio.

Details to follow.

## Local dev

```bash
# backend

# frontend
cd frontend && npm run dev    # http://localhost:5173, proxied to :8000
```

## Key references
- Architecture + file structure: `ARCHITECTURE.md`
- Decision rationale: `ADR/`