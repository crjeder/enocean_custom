#!/usr/bin/env bash
# Run the Docker-based integration test suite.
# Requires Docker with Linux containers (WSL2 on Windows).
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose -f docker-compose.test.yml up \
  --build \
  --abort-on-container-exit \
  --exit-code-from test-runner

docker compose -f docker-compose.test.yml down --volumes
