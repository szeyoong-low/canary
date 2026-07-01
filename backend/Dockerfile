# Official Python Docker image
# Slim strips out extras (e.g. docs, dev headers) to keep the image small
FROM python:3.12-slim

# Run all commands from this directory instead of filesystem root
WORKDIR /app

# Copies the uv binary directly from uv's official image instead of pip installing
COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /usr/local/bin/uv

# Build command
# Dependencies are installed before source code is copied
# Docker caches each instruction as a layer, so a code-only change won't
# re-download packages
COPY pyproject.toml uv.lock ./
# frozen: Sync without updating the `uv.lock` file, ensures reproducibility
RUN uv sync --frozen --no-dev

# Copy all other files from current directory on host machine to
# working directory in container
COPY . .

# Default for local runs
ENV PORT=8000
# Python reads PORT from environment directly, avoiding shell quoting issues
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request, os; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', '8000') + '/health')"
# Start command
# Host: listen on all network interfaces (https://dev.to/engrmark/what-is-host0000-goa)
# Shell form (not array form) so $PORT expands at runtime from the environment
# Railway injects $PORT at runtime
CMD uv run fastapi run main.py --host 0.0.0.0 --port $PORT
