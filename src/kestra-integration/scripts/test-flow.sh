#!/usr/bin/env sh
set -eu

KESTRA_URL="${KESTRA_URL:-http://localhost:8080}"
NAMESPACE="company.team.nomad"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd curl

extract_execution_id() {
  # Extract first JSON id field without jq
  echo "$1" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -n 1
}

trigger_flow() {
  flow_id="$1"
  payload="$2"

  response="$(curl -fsS -X POST \
    "$KESTRA_URL/api/v1/executions/$NAMESPACE/$flow_id" \
    -H 'Content-Type: application/json' \
    -d "$payload")"

  execution_id="$(extract_execution_id "$response")"
  if [ -z "$execution_id" ]; then
    echo "Failed to parse execution id for flow $flow_id" >&2
    echo "$response" >&2
    exit 1
  fi

  echo "$execution_id"
}

wait_execution() {
  execution_id="$1"
  max_tries="${2:-80}"
  i=1

  while [ "$i" -le "$max_tries" ]; do
    response="$(curl -fsS "$KESTRA_URL/api/v1/executions/$execution_id")"

    if echo "$response" | grep -q '"state":"SUCCESS"'; then
      echo "Execution $execution_id SUCCESS"
      return 0
    fi

    if echo "$response" | grep -Eq '"state":"(FAILED|KILLED|WARNING)"'; then
      echo "Execution $execution_id ended with failure-like state" >&2
      echo "$response" >&2
      return 1
    fi

    sleep 3
    i=$((i + 1))
  done

  echo "Execution $execution_id timeout" >&2
  return 1
}

echo "Triggering nomad-job-flow..."
exec1="$(trigger_flow "nomad-job-flow" '{"job_name":"test-basic-flow"}')"
echo "Execution ID: $exec1"
wait_execution "$exec1"

echo "Triggering parallel-tasks-flow..."
exec2="$(trigger_flow "parallel-tasks-flow" '{}')"
echo "Execution ID: $exec2"
wait_execution "$exec2"

echo "Triggering dag-workflow..."
exec3="$(trigger_flow "dag-workflow" '{}')"
echo "Execution ID: $exec3"
wait_execution "$exec3"

echo "All test flows completed successfully."
