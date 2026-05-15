# ADR-005 — uv for Python dependency management

## Decision
Use uv to manage Python dependencies instead of plain pip or Poetry.

## Context
The backend is a Python 3.12 FastAPI project. Dependencies need to be
declared, locked, and reproducibly installed both locally and on Railway.

## Reasoning
Plain pip with requirements.txt has two problems: pip freeze captures
transitive dependencies alongside direct ones (making the file hard to
maintain), and there is no cryptographic lock — version ranges can resolve
differently across machines or deploys.

uv solves both. It keeps pyproject.toml as the human-maintained list of
direct dependencies, and generates uv.lock as a fully pinned, reproducible
lock file. It is a drop-in replacement for pip, pip-tools, and virtualenv,
written in Rust, and is significantly faster than pip or Poetry. FastAPI's
official documentation now recommends uv, and Railway has native uv support.

## Consequences
- pyproject.toml declares direct dependencies only.
- uv.lock must be committed to the repository so Railway and CI reproduce the
  exact same environment.
- Developers install uv once (curl -LsSf https://astral.sh/uv/install.sh | sh)
  and then use `uv add`, `uv run`, and `uv sync` instead of pip.

## Trade-offs accepted
uv was released in 2024 and is newer than pip or Poetry. Community answers
for edge cases may be thinner. This is not a concern at this project's scale.

## Revisit if
uv introduces a breaking change or the project grows to need features Poetry
provides (e.g. monorepo workspace management beyond uv's capabilities).
