# ADR-008 — GitHub Flow branch strategy

## Decision
Use [GitHub Flow](): short-lived feature branches merged into `main` via pull
request. No permanent `dev` branch.

## Context
The repository has a single developer. The goals are a clean, linear git
history, mandatory CI and deployment gates before merging, and no unnecessary
process overhead.

## Reasoning
### GitHub Flow over GitFlow
GitFlow uses a permanent `dev` branch as a staging ground: features merge into
`dev`, then `dev` merges into `main` for a release. This means two pull
requests per feature and additional bookkeeping designed for teams coordinating
parallel work. For a solo developer it adds ceremony with no benefit.

GitHub Flow removes the intermediate branch. A feature branch is cut from
`main`, developed, and merged back via a single pull request once CI passes
and the deployment is healthy.

### Vercel PR previews as staging
The reason teams reach for a `dev` branch is often to have a stable staging
environment. Vercel automatically deploys every pull request to a unique
preview URL (e.g. `https://canary-abc123-team.vercel.app`). This covers the
same need without a permanent branch.

## Consequences

### Branch protections on `main`
The following rules must be enabled in GitHub (Settings → Branches):
- Require a pull request before merging (no direct pushes)
- Require status checks to pass (CI + deployment)
- Require linear history

### CORSMiddleware regex for Vercel preview URLs
Dropping `dev` means Vercel preview URLs are the only staging environment.
These URLs are unique per pull request (e.g. `https://canary-abc123.vercel.app`)
so they cannot be enumerated in the `ALLOWED_ORIGINS` list. Instead,
`CORSMiddleware` is configured with `allow_origin_regex` to match the
predictable Vercel subdomain pattern:

```
https://canary-.*\.vercel\.app
```

The `ALLOWED_ORIGINS` variable continues to hold the explicit whitelist for
`localhost:5030` (dev) and the stable production Vercel URL (once known).

### CI pipeline
A GitHub Actions workflow must run on every pull request and report a status
check. It runs:
- **Frontend:** TypeScript compiler check and ESLint
- **Backend:** Ruff lint and format check

Merging to `main` is blocked until this check passes.

### Healthy deployment
Vercel and Railway both integrate with GitHub Actions — once connected, a
successful deployment becomes a reportable status check that can be required
before merge.

### Code scanning
GitHub CodeQL and Dependabot are enabled on the repository to surface security
vulnerabilities in code and dependencies respectively.

## Trade-offs accepted
No permanent staging URL. A pull request preview URL must be shared manually
for review. Acceptable for a solo-developer project with no external reviewers.

## Revisit if
A second developer joins and parallel feature work requires a dedicated staging
environment. At that point, introduce a `dev` branch and configure a Railway
staging service to deploy from it.

## Additional information - industry standard version control systems
GitFlow (2010, Vincent Driessen) — main + develop + feature/release/hotfix branches. Was the dominant model for most of the 2010s. Now considered overkill
for most teams, but still appropriate for versioned software with scheduled releases (mobile apps, open-source libraries with semver).

GitHub Flow — what we're using. main + short-lived feature branches + PRs. Designed for continuous deployment where main is always in a releasable state.
Widely used by web and SaaS teams.

Trunk-Based Development — everyone commits directly to main (the "trunk"), with feature flags hiding unfinished work. No long-lived branches at all. Used
internally at Google and Meta. Maximises integration speed and minimises merge conflicts. Requires strong CI discipline and feature flagging
infrastructure.

GitLab Flow — GitHub Flow with added environment branches (staging, production). A middle ground when you need promotion gates between environments.

The current industry trend for web products is moving towards trunk-based development or GitHub Flow. GitFlow has largely fallen out of favour for
anything doing continuous deployment — the release branch ceremony doesn't make sense when you're shipping multiple times a day.
