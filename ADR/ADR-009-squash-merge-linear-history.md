# ADR-009 — Squash merge for linear history

## Decision
Merge all pull requests into `main` via squash merge. Rebase merge and merge
commits are disabled by the "Require linear history" branch protection rule.

## Context

### Linear history
We use GitHub's "Require linear history" branch protection rule to disables merge
commits on `main`. This keeps `git log` readable as a sequential list of meaningful
changes rather than a tangle of merge commits. There are two strategies that
satisfy linear history: squash merge and rebase merge. A choice between them is needed.

## Reasoning
### Squash merge over rebase merge
Rebase merge preserves every individual commit from the feature branch,
replaying them one-by-one on top of `main`. This is valuable when branch
commits are well-structured and tell a coherent story worth keeping in the
permanent record.

In practice — especially on a solo learning project — feature branches
accumulate WIP commits ("fix", "try this", "revert", "oops") that carry no
long-term value. Rebase merge would surface these on `main` permanently.

Squash merge collapses the entire feature branch into a single commit on
`main`. The branch history is discarded; the author writes one meaningful
commit message at merge time. The result is a `main` history that reads as a
clean, one-entry-per-feature changelog.

### Commit message discipline
The value of squash merge depends on the quality of the message written at
merge time. The auto-generated "Merge pull request #N" default is not
sufficient. Each squash commit message should summarise what changed and why,
following the same standard as any well-written git commit.

## Consequences
- Feature branches can be committed to freely without concern for commit
  quality — they are never exposed on `main`.
- One meaningful commit message must be written per pull request at merge time.
- `git log` on `main` is a clean, linear changelog with one entry per feature.
- The "Require linear history" rule on GitHub disables the regular merge button;
  only "Squash and merge" and "Rebase and merge" are available. "Squash and
  merge" should always be chosen.

## Trade-offs accepted
Individual feature branch commits are not preserved in `main`'s history. If
the reasoning behind a specific intermediate change is ever needed, it must be
recovered from the pull request itself (GitHub retains the branch and PR
discussion after merge).

## Revisit if
A second developer joins and pair code review benefits from seeing granular
commit history on `main`. At that point, rebase merge is the alternative
without sacrificing linearity.
