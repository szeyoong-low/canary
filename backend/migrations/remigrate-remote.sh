#!/bin/sh

# Unwinds the remote database to REVISION, then re-applies every revision above
# it. For when a migration has been edited in place. Alembic keys on the revision
# id, which does not change when the file's contents do, so an edited revision is
# only re-run by removing it and putting it back.
#
# Usage:
#   MIGRATE_ENVIRONMENT=<env> ./migrations/remigrate-remote.sh <revision>

set -euo pipefail

revision="${1:?usage: remigrate-remote.sh <revision>}"
cluster="cluster-$MIGRATE_ENVIRONMENT"
service="backend-$MIGRATE_ENVIRONMENT"

echo "About to unwind $service down to $revision and re-apply to head."
echo "Every table created above $revision will be DROPPED, with its rows."
printf 'Type the environment name to continue: '
read -r confirmation

if [ "$confirmation" != "$MIGRATE_ENVIRONMENT" ]; then
  echo "Aborted." >&2
  exit 1
fi

network="$(aws ecs describe-services \
  --cluster "$cluster" \
  --services "$service" \
  --query 'services[0].networkConfiguration' \
  --output json)"

# The entrypoint runs `alembic upgrade head` before this command, which is a
# no-op while the revisions are already applied. The downgrade therefore has to
# come first here, and the upgrade after it re-runs the edited files.
#
# `sh -c` because containerOverrides takes an argv, not a shell line, and the
# two commands must share one container so the gap between them is as short as
# possible: the application role is dropped by the downgrade and only recreated
# by the upgrade, and the service cannot authenticate in between.
#
overrides="$(jq --null-input --arg revision "$revision" '{
  containerOverrides: [{
    name: "backend",
    command: [
      "sh", "-c",
      "uv run alembic downgrade \($revision) && uv run alembic upgrade head"
    ]
  }]
}')"

task="$(aws ecs run-task \
  --cluster "$cluster" \
  --task-definition "$service" \
  --launch-type FARGATE \
  --started-by admin-running-remigrate \
  --network-configuration "$network" \
  --overrides "$overrides" \
  --query 'tasks[0].taskArn' \
  --output text)"

echo "Started $task"

# Tail in the background, then block on the task itself. Tailing alone would
# leave the shell waiting on a stream that never ends, and would exit 0 however
# the migration went.
aws logs tail "/ecs/$service" --follow &
tail_pid="$!"

aws ecs wait tasks-stopped --cluster "$cluster" --tasks "$task"
kill "$tail_pid" 2>/dev/null || true

# The container's exit code is the migration's. A non-zero one here means the
# database is in whatever state the failed revision left it, which is worth
# saying out loud rather than leaving to the log.
code="$(aws ecs describe-tasks \
  --cluster "$cluster" \
  --tasks "$task" \
  --query 'tasks[0].containers[0].exitCode' \
  --output text)"

if [ "$code" != "0" ]; then
  echo "Migration task exited $code. The schema may be partially unwound." >&2
  exit 1
fi

echo "Done. Schema is at head."
