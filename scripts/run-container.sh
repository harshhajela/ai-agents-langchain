#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME=${IMAGE_NAME:-ai-agents-backend}
IMAGE_TAG=${IMAGE_TAG:-latest}
ENV_FILE=${ENV_FILE:-.env}
PORT=${PORT:-8000}

if [ ! -f "$ENV_FILE" ]; then
  echo "Env file $ENV_FILE not found. Generate one with scripts/write-env-file.sh or provide --env-file manually."
  exit 1
fi

echo "Running ${IMAGE_NAME}:${IMAGE_TAG} on port ${PORT} using env file ${ENV_FILE}"
docker run --rm -p ${PORT}:8000 --env-file "$ENV_FILE" "${IMAGE_NAME}:${IMAGE_TAG}"

