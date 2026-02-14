#!/usr/bin/env bash
set -euo pipefail

# 说明：
# 1) 先在首个 Server 上执行：nomad acl bootstrap
# 2) 将得到的 Secret ID 导出为 NOMAD_TOKEN
# 3) 再运行本脚本创建策略

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

: "${NOMAD_ADDR:=https://127.0.0.1:4646}"
: "${NOMAD_CACERT:=/etc/nomad.d/tls/nomad-agent-ca.pem}"
: "${NOMAD_CLIENT_CERT:=/etc/nomad.d/tls/cli.pem}"
: "${NOMAD_CLIENT_KEY:=/etc/nomad.d/tls/cli-key.pem}"

if [[ -z "${NOMAD_TOKEN:-}" ]]; then
  echo "[ERROR] NOMAD_TOKEN 未设置，请先执行 nomad acl bootstrap 并导出管理 token"
  exit 1
fi

nomad acl policy apply anonymous "${BASE_DIR}/anonymous.hcl"
nomad acl policy apply readonly  "${BASE_DIR}/readonly.hcl"
nomad acl policy apply deployer  "${BASE_DIR}/deployer.hcl"
nomad acl policy apply ops-admin "${BASE_DIR}/ops-admin.hcl"

echo "[OK] ACL policies applied."
