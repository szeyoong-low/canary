# Product roadmap

## Phase 1
### Goal
Basic full stack app deployed to production. Able to fetch financial data from
an external API, transform it, and chart a computed metric (e.g. Capex to
revenue ratio).

### Learning objectives
REST API design, data pipelines, charting

### Milestones
- [x] Frontend and backend are deployed, Git CI/CD pipeline in place
- [ ] Design and document backend API endpoints
- [ ] A single backend endpoint that accepts a JSON query, fetches data, cleans
      it, and returns it as a chart config JSON
- [ ] A single page on the frontend that displays a chart with the processed
      data

### Done when
User loads the page and gets a comparison of the Big 5 hyperscalers' capex-to-revenue
ratio.

## Phase 2
### Goal
Use a LangGraph data pipeline to plan and call tools (e.g. backend API calls)
to build the chart and generate the insights.

### Learning objectives
Agent orchestration, tool use, SSE streaming, API endpoint design.

### Milestones
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

### Done when
User enters a free text query about the capex-to-revenue ratio of several companies,
and gets a bar chart comparison and a quick analysis streamed in real time.

## Phase 3
### Goal
Allow users to save their charts under their own accounts.

### Learning objectives
Database integration, auth patterns

### Milestones
- [ ] Users must sign in to use the service, all paths protected by middleware
- [ ] Users' charts are saved to a PostgreSQL database as JSON blobs
- [ ] Sidebar and personal homepage show all of their past charts

### Done when
Users have a personal dashboard of chart previews and sidebar that they can
click through to see charts they created in the past.

## Phase 4
### Goal
Post-launch: Enhance the user experience, optimise performance, security improvements.

###
- [ ] Users can share charts publicly
- [ ] Non-authenticated users can see sample charts on the landing page
- [ ] Cache API and LLM calls
- [ ] Support more types of analysis on more endpoints
- [ ] Integrate more APIs: prediction markets, patents, scientific journals
- [ ] Dark mode toggle
- [ ] Mobile support
- [ ] Native apps for mobile and PC
- [ ] Enchanced search experience, with live suggestions and ticker icons
- [ ] Fine tune planner API to handle queries beyond the types of analysis supported
- [ ] Rate limiting
- [ ] Allow raw data to be viewed and downloaded