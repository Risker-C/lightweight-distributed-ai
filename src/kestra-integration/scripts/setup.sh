#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
KESTRA_URL="${KESTRA_URL:-http://localhost:8080}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd docker
require_cmd curl

echo "[1/4] Starting Kestra + Postgres + Nomad..."
cd "$ROOT_DIR"
docker compose up -d

echo "[2/4] Waiting for Kestra API..."
MAX_TRIES=60
i=1
while [ "$i" -le "$MAX_TRIES" ]; do
  if curl -fsS "$KESTRA_URL/api/v1/health" >/dev/null 2>&1; then
    echo "Kestra is ready"
    break
  fi
  sleep 3
  i=$((i + 1))
done

if [ "$i" -gt "$MAX_TRIES" ]; then
  echo "Kestra startup timeout" >&2
  exit 1
fi

upload_flow() {
  flow_file="$1"
  echo "Importing flow: $flow_file"

  code="$(curl -sS -o /tmp/kestra-flow-upload.out -w '%{http_code}' \
    -X POST "$KESTRA_URL/api/v1/flows" \
    -H 'Content-Type: application/x-yaml' \
    --data-binary "@$flow_file")"

  if [ "$code" -ge 200 ] && [ "$code" -lt 300 ]; then
    return 0
  fi

  code="$(curl -sS -o /tmp/kestra-flow-upload.out -w '%{http_code}' \
    -X PUT "$KESTRA_URL/api/v1/flows" \
    -H 'Content-Type: application/x-yaml' \
    --data-binary "@$flow_file")"

  if [ "$code" -ge 200 ] && [ "$code" -lt 300 ]; then
    return 0
  fi

  echo "Failed to upload flow ($flow_file), HTTP $code" >&2
  cat /tmp/kestra-flow-upload.out >&2 || true
  exit 1
}

echo "[3/4] Importing Kestra flows..."
upload_flow "$ROOT_DIR/flows/nomad-job-flow.yml"
upload_flow "$ROOT_DIR/flows/parallel-tasks-flow.yml"
upload_flow "$ROOT_DIR/flows/dag-workflow.yml"

echo "[4/4] Setup complete"
echo "Kestra UI: http://localhost:8080"
echo "Nomad UI:  http://localhost:4646"
