#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME=${IMAGE_NAME:-ai-agents-backend}
IMAGE_TAG=${IMAGE_TAG:-latest}

echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
echo "Built ${IMAGE_NAME}:${IMAGE_TAG}"

