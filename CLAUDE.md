# CLAUDE.md

## About this project
Canary is a full-stack agentic financial terminal. Users ask free-text questions;
an AI agent fetches data, transforms it, and returns an interactive chart with
concise insights synthesised by a LLM.

## Key references
- Architecture + file structure: `ARCHITECTURE.md`
- Decision rationale: `ADR/`

## Phases
1. Basic full stack app deployed to production. Able to fetch financial data
   from an external API, transform it, and chart a computed metric (e.g.
   Capex to revenue ratio).
2. Agentic workflow that takes a free-text query and uses a data pipeline to
   dynamically generate the answer.
3. Add authentication, so that users can save their charts.

Afterwards, expand the variety of analysis that can be performed, and allow more
data sources to be incorporated.

## Way of working — read before answering any prompt
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
  decisions like I'm a **first-timer** but **be concise**. Highlight the tradeoffs
  involved, and whether this decision will need to change down the line. I want
  a full understanding of the solution's rationale before any code is written.
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
- Details like version numbers change constantly. I expect you to flag potential
  discrepancies (e.g. outdated version numbers, shell scripts not matching docs,
  dependency names different from examples in documentation) so that I can cross
  check them online.

## Progress checklist
### Phase 1
#### Goal
Basic full stack app deployed to production. Able to fetch financial data from
an external API, transform it, and chart a computed metric (e.g. Capex to
revenue ratio).

#### Learning objectives
REST API design, data pipelines, charting

#### Milestones
- [ ] Frontend and backend are deployed, Git CI/CD pipeline in place
- [ ] Claude Code integrated into workflow
- [ ] A single backend endpoint `api/test` that accepts a JSON query, fetches data
      from `yfinance`, cleans it, and returns it as a chart config JSON
- [ ] A single page on the frontend that only displays a chart with the processed
      data

#### Done when
User loads the page and gets a comparison of the Big 5 hyperscalers' Capex to
revenue ratio.

### Phase 2
#### Goal
Replace the hardcoded `api/test` endpoint with a LangGraph data pipeline that plans
and calls tools to build the chart and generate the insights.

#### Learning objectives
Agent orchestration, tool use, SSE streaming, API endpoint design.

#### Milestones
- [ ] Planner node with an LLM that parses the query and creates a plan
- [ ] Research node that uses python functions as tools to fetch data with
      extracted parameters
- [ ] Transformer node uses python functions to clean and normalise raw
      API data
- [ ] Visualiser node outputs a JSON chart config compatible with frontend charting
      component
- [ ] Storyteller node streams a brief insight about the data over SSE
- [ ] Agent pipeline set up
- [ ] Chart and insight panel are displayed at a URL with search parameters
      embedded, without any full-page refresh occurring
- [ ] (Stretch goal) Cache API and LLM calls
- [ ] (Stretch goal) Support multiple types of analysis on different endpoints

#### Done when
User enters a free text query about the year-on-year change in Q1 revenue of the
biggest US airlines, and gets a bar chart comparison and a quick analysis streamed
in real time.

### Phase 3
#### Goal
Allow users to save their charts under their own accounts.

#### Learning objectives
Database integration, auth patterns

#### Milestones
- [ ] Users must sign in to use the service, all paths protected by middleware
- [ ] Users' charts are saved to a PostgreSQL database as a JSON blob
- [ ] Sidebar and personal homepage show all of their past charts
- [ ] (Stretch goal) Users can share charts publicly
- [ ] (Stretch goal) Non-authenticated users can see sample charts on the landing
      page
- [ ] (Stretch goal) Dark mode toggle
- [ ] (Stretch goal) Mobile support

#### Done when
Users have a personal dashboard of chart previews and sidebar that they can
click through to see charts they created in the past.