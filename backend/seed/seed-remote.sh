#!/bin/bash

set -euo pipefail

network="$(aws ecs describe-services \
  --cluster "cluster-$SEED_ENVIRONMENT" \
  --services "backend-$SEED_ENVIRONMENT" \
  --query 'services[0].networkConfiguration' \
  --output json)"

# jq builds the JSON so that the subject is escaped as a JSON string rather than
# pasted into one. Single quotes still protect the program from the shell, and
# `--arg` is what carries a value across that boundary.
overrides="$(jq --null-input --arg subject "$SEED_ADMIN_SUBJECT" '{
  containerOverrides: [{
    name: "backend",
    command: ["uv", "run", "python", "-m", "backend.seed"],
    environment: [
      {name: "PYTHONPATH", value: "/"},
      {name: "SEED_ADMIN_SUBJECT", value: $subject}
    ]
  }]
}')"

aws ecs run-task \
  --cluster "cluster-$SEED_ENVIRONMENT" \
  --task-definition "backend-$SEED_ENVIRONMENT" \
  --launch-type FARGATE \
  --started-by admin-running-seed \
  --network-configuration "$network" \
  --overrides "$overrides"

aws logs tail "/ecs/backend-$SEED_ENVIRONMENT" --follow
