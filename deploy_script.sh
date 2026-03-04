#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKERS_HELM_DIR="${SCRIPT_DIR}/calculator/workers/helm"
TEMPORAL_SERVER_CHART_DIR="${SCRIPT_DIR}/temporal_server/helm"
TRIGGER_SERVER_CHART_DIR="${SCRIPT_DIR}/trigger_server/helm"
ROOT_DOCKERFILE="${SCRIPT_DIR}/Dockerfile"
TEMPORAL_SERVER_DOCKERFILE="${SCRIPT_DIR}/temporal_server/Dockerfile"
TRIGGER_SERVER_DOCKERFILE="${SCRIPT_DIR}/trigger_server/Dockerfile"

if [[ ! -f "${ROOT_DOCKERFILE}" ]]; then
  echo "Root Dockerfile not found: ${ROOT_DOCKERFILE}" >&2
  exit 1
fi

if [[ ! -f "${TEMPORAL_SERVER_DOCKERFILE}" ]]; then
  echo "Temporal server Dockerfile not found: ${TEMPORAL_SERVER_DOCKERFILE}" >&2
  exit 1
fi

if [[ ! -f "${TRIGGER_SERVER_DOCKERFILE}" ]]; then
  echo "Trigger server Dockerfile not found: ${TRIGGER_SERVER_DOCKERFILE}" >&2
  exit 1
fi

if [[ ! -d "${WORKERS_HELM_DIR}" ]]; then
  echo "Workers helm directory not found: ${WORKERS_HELM_DIR}" >&2
  exit 1
fi

if [[ ! -d "${TEMPORAL_SERVER_CHART_DIR}" ]]; then
  echo "Temporal server helm directory not found: ${TEMPORAL_SERVER_CHART_DIR}" >&2
  exit 1
fi

if [[ ! -d "${TRIGGER_SERVER_CHART_DIR}" ]]; then
  echo "Trigger server helm directory not found: ${TRIGGER_SERVER_CHART_DIR}" >&2
  exit 1
fi

if ! command -v minikube >/dev/null 2>&1; then
  echo "minikube command not found in PATH" >&2
  exit 1
fi

echo "Switching Docker daemon to Minikube"
eval "$(minikube docker-env)"

echo "Building calculator worker image from ${SCRIPT_DIR}"
docker build -t calculator-worker:latest "${SCRIPT_DIR}"

echo "Building temporal server image from ${SCRIPT_DIR}/temporal_server"
docker build -t temporal-server:latest "${SCRIPT_DIR}/temporal_server"

echo "Building trigger server image from ${SCRIPT_DIR}"
docker build -f "${TRIGGER_SERVER_DOCKERFILE}" -t trigger-server:latest "${SCRIPT_DIR}"

echo "Deploying temporal-server from ${TEMPORAL_SERVER_CHART_DIR}"
helm upgrade --install temporal-server "${TEMPORAL_SERVER_CHART_DIR}"

echo "Deploying trigger-server from ${TRIGGER_SERVER_CHART_DIR}"
helm upgrade --install trigger-server "${TRIGGER_SERVER_CHART_DIR}"

for chart_dir in "${WORKERS_HELM_DIR}"/*; do
  [[ -d "${chart_dir}" ]] || continue
  worker_name="$(basename "${chart_dir}")"
  release_name="${worker_name}-worker"
  echo "Deploying ${release_name} from ${chart_dir}"
  helm upgrade --install "${release_name}" "${chart_dir}"
done

echo "Images built, temporal/trigger servers deployed, and all calculator workers deployed/upgraded."
