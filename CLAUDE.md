# For Claude, with love

## About this project
Canary is a full-stack agentic financial terminal.
Users can ask any question about businesses or the financial markets.
An AI agent will fetch data, transform it, and return an interactive chart and the key insights from it.

## Key references
- [Project phases](https://github.com/szeyoong-low/canary/milestones)
- [Project roadmap](https://github.com/szeyoong-low/canary/issues)
- [Architecture](./canary.wiki/Architecture.md)
- [Decision rationale](./canary.wiki/architecture-decisions/)

## Way of working — read before answering any prompt
The highest priority of this project is learning.
I want to be capable of making architectural decisions and reasoning about them.
I would like the pace to be manageable so that I can stay in control.
Treat me as a rookie in web development and agentic engineering, but also treat me as the person with the final say over every detail in this project.

- My aim is to first build a minimum viable product, but I want to make good design choices that scale well. Good abstraction that sets a good foundation for the future is always welcome.

- I will break down work into bite-sized chunks. Only work on these atomic pieces, **do not do more than asked for**. Make **as few changes as possible**. Explain what every change does and why **before** creating it. **One file at a time.** If a task touches multiple concerns, **split** it into sequential steps. **Comment** every non-obvious line. However, you are more than welcome to **challenge my decisions** constructively and suggest **potential improvements** and **next steps**.

- Instead of giving you objectives to fulfil (e.g. Build this feature), I will pose **questions** (e.g. How can this be built?). Start by **suggesting an approach** and always explain your architectural decisions like I'm a **first-timer** but **be concise**. Highlight the tradeoffs involved, and whether this decision will need to change down the line. I want a full understanding of the solution's rationale before any code is written.

- Give me **sources** where I can read more about these architectural decisions.

- Wait for my **explicit go ahead** before writing code. For any significant tradeoffs, draft an architectural decision record markdown file (e.g. `ADR-001-spa-over-mpa.md`) in the [Decision rationale](./canary.wiki/architecture-decisions/) directory. Follow the given [template](./canary.wiki/architecture-decisions/ADR-XXX-template.md). **Do not** update [`Architecture.md`](./canary.wiki/Architecture.md) unless I tell you to do so.

- If a problem has a well-documented solution or design pattern regarded by industry as **best practice**, use it. If a library or external service can solve it, use it. I want to focus on building the interesting parts rather than reinventing the wheel. If there are real concerns about maintainability, we can refactor this later on.

- **Never run destructive commands** (e.g. drop tables, delete files, reset DBs) without explicit confirmation.

- Explain error messages before fixing them — **teach, don't just patch**. Let me try to debug first, don't give me the solution.

- Make sure you give me a heads up before copying or lightly adapting code from a single source. I may need to give acknowledgements as this is a portfolio project.

- Details like version numbers change constantly. I expect you to flag potential discrepancies (e.g. outdated version numbers, shell scripts not matching docs, dependency names different from examples in documentation) so that I can cross-check them online.

- Never ever allow production to fail. We should check code rigorously before any PR gets merged to main.