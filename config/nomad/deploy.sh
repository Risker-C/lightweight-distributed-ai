#!/usr/bin/env bash
set -euo pipefail

# =====================
# Nomad 一键部署脚本
# 用法:
#   ./deploy.sh server
#   ./deploy.sh client-warm
#   ./deploy.sh client-batch
#   ./deploy.sh client-special
# =====================

ROLE="${1:-}"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="/etc/nomad.d"
TLS_DIR="${BASE_DIR}/tls"
ACL_DIR="${BASE_DIR}/acl-policies"

usage() {
  echo "Usage: $0 {server|client-warm|client-batch|client-special}"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "[ERROR] command not found: $1"; exit 1; }
}

if [[ -z "${ROLE}" ]]; then
  usage
  exit 1
fi

case "${ROLE}" in
  server)
    SRC_CONFIG="${BASE_DIR}/server.hcl"
    ;;
  client-warm)
    SRC_CONFIG="${BASE_DIR}/client-warm.hcl"
    ;;
  client-batch)
    SRC_CONFIG="${BASE_DIR}/client-batch.hcl"
    ;;
  client-special)
    SRC_CONFIG="${BASE_DIR}/client-special.hcl"
    ;;
  *)
    usage
    exit 1
    ;;
esac

require_cmd nomad
require_cmd openssl
require_cmd systemctl

if [[ ! -f "${SRC_CONFIG}" ]]; then
  echo "[ERROR] config file not found: ${SRC_CONFIG}"
  exit 1
fi

if [[ ! -f "${TLS_DIR}/nomad-agent-ca.pem" || ! -f "${TLS_DIR}/server.pem" || ! -f "${TLS_DIR}/client.pem" ]]; then
  echo "[INFO] TLS artifacts missing, generating certificates..."
  bash "${TLS_DIR}/generate-certs.sh" "${TLS_DIR}"
fi

echo "[INFO] Preparing target directories..."
sudo mkdir -p "${TARGET_DIR}" "${TARGET_DIR}/tls" "${TARGET_DIR}/acl-policies"

echo "[INFO] Deploying Nomad config for role: ${ROLE}"
sudo cp "${SRC_CONFIG}" "${TARGET_DIR}/nomad.hcl"

echo "[INFO] Deploying TLS files..."
sudo cp "${TLS_DIR}"/*.pem "${TARGET_DIR}/tls/"

# ACL 策略文件放到目标机，便于后续 bootstrap
sudo cp "${ACL_DIR}"/*.hcl "${TARGET_DIR}/acl-policies/"
sudo cp "${ACL_DIR}/bootstrap-acl.sh" "${TARGET_DIR}/acl-policies/"

# 安全权限
sudo chmod 600 "${TARGET_DIR}/tls"/*-key.pem
sudo chmod 644 "${TARGET_DIR}/tls"/*.pem || true
sudo chmod +x "${TARGET_DIR}/acl-policies/bootstrap-acl.sh"

if id nomad >/dev/null 2>&1; then
  sudo chown -R nomad:nomad "${TARGET_DIR}"
fi

echo "[INFO] Validating Nomad configuration..."
sudo nomad agent -validate -config="${TARGET_DIR}"

echo "[INFO] Restarting Nomad service..."
sudo systemctl daemon-reload
sudo systemctl enable nomad
sudo systemctl restart nomad
sudo systemctl --no-pager --full status nomad | sed -n '1,20p'

cat <<EOF

[OK] Nomad deployment complete (${ROLE})

Recommended CLI environment:
  export NOMAD_ADDR=https://127.0.0.1:4646
  export NOMAD_CACERT=${TARGET_DIR}/tls/nomad-agent-ca.pem
  export NOMAD_CLIENT_CERT=${TARGET_DIR}/tls/cli.pem
  export NOMAD_CLIENT_KEY=${TARGET_DIR}/tls/cli-key.pem

If this is the first server node, bootstrap ACL:
  nomad acl bootstrap
  export NOMAD_TOKEN=<bootstrap_secret_id>
  bash ${TARGET_DIR}/acl-policies/bootstrap-acl.sh

EOF
