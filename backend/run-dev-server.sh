#!/bin/bash
docker compose up --wait --detach && uv run fastapi dev