#!/bin/sh

# Brings the schema up to date, then hands the container over to whatever the
# image's CMD is. Splitting the two means the server stays overridable: a one-off
# migration task can run this same image with the command replaced.

# `-e` aborts on first failure (including failed migrations)
# `-u` catches a mistyped variable name rather than treating it as empty.
set -eu

echo "Running migrations..."
uv run alembic upgrade head
echo "Starting server..."

# exec: Tells the shell to swap itself out and run a new program in its exact
# place instead of starting a child process. This will be CMD.
# "$@": Expands to all the arguments passed to the script, cleanly wrapped in
# quotes to preserve spaces and special characters
exec "$@"
