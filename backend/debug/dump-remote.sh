#!/bin/bash

# Runs the dump as a one-off task in a remote environment and prints what it
# wrote to the log.
#
# The database is not reachable from here: it sits in private subnets with
# `publicly_accessible = false`. So the dump runs inside the VPC, on the same
# task definition the service runs, and the rows come back through the
# container's log stream.
#
# Usage: DUMP_ENVIRONMENT=development ./debug/dump-remote.sh

set -euo pipefail

# `:?` aborts with this message rather than letting `-u` report a bare
# "unbound variable" from wherever the name is first read.
environment="${DUMP_ENVIRONMENT:?must name the environment to dump, e.g. development}"

cluster="cluster-$environment"
service="backend-$environment"
log_group="/ecs/$service"

# The container name inside the task definition, which is also the log stream
# prefix the task definition sets. Both appear in the stream name below.
container="backend"

# The task has to land in the same subnets and security groups as the service,
# because the database's security group admits that group and nothing else.
network="$(aws ecs describe-services \
  --cluster "$cluster" \
  --services "$service" \
  --query 'services[0].networkConfiguration' \
  --output json)"

# Replaces the image's CMD, so the container runs the dump instead of the
# server. The image's ENTRYPOINT still runs first and migrates: harmless here,
# because this task definition names the image the service is already running,
# so there is nothing left to apply.
#
# `PYTHONPATH=/` puts the repository root on the import path, which is what makes
# the `backend.debug` package importable.
overrides="$(jq --null-input --arg container "$container" '{
  containerOverrides: [{
    name: $container,
    command: ["uv", "run", "python", "-m", "backend.debug"],
    environment: [{name: "PYTHONPATH", value: "/"}]
  }]
}')"

echo "Starting dump task in $environment..." >&2

task_arn="$(aws ecs run-task \
  --cluster "$cluster" \
  --task-definition "$service" \
  --launch-type FARGATE \
  --started-by admin-running-dump \
  --network-configuration "$network" \
  --overrides "$overrides" \
  --query 'tasks[0].taskArn' \
  --output text)"

# The ARN ends in the task id, which is the last segment of both the ARN and the
# log stream name.
task_id="${task_arn##*/}"

# The prefix and the container name are both `backend`, which is why the stream
# name has it twice.
stream="$container/$container/$task_id"

echo "Task $task_id started. Log stream: $log_group $stream" >&2

# Waits rather than following the log, so this exits on its own once the dump is
# done instead of leaving a `--follow` to be interrupted by hand.
aws ecs wait tasks-stopped --cluster "$cluster" --tasks "$task_arn"

exit_code="$(aws ecs describe-tasks \
  --cluster "$cluster" \
  --tasks "$task_arn" \
  --query "tasks[0].containers[?name=='$container'].exitCode | [0]" \
  --output text)"

# Only this task's stream, so the running service's own logs are not mixed in.
# `--since` covers the task's whole life rather than the default ten minutes.
aws logs tail "$log_group" --log-stream-names "$stream" --since 1h --format short

if [[ "$exit_code" != "0" ]]; then
  echo "Dump task exited with $exit_code." >&2
  exit 1
fi