#!/usr/bin/env bash
set -euo pipefail

# =====================
# Nomad TLS 证书生成脚本
# 输出：
# - nomad-agent-ca.pem / nomad-agent-ca-key.pem
# - server.pem / server-key.pem
# - client.pem / client-key.pem
# - cli.pem / cli-key.pem
# =====================

OUT_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
mkdir -p "${OUT_DIR}"

DAYS_CA="${DAYS_CA:-3650}"
DAYS_CERT="${DAYS_CERT:-825}"

# 根据环境覆盖 SAN（生产建议包含全部 Server/Client IP 和域名）
SERVER_SANS="${SERVER_SANS:-DNS:localhost,IP:127.0.0.1,DNS:nomad.service.consul}"
CLIENT_SANS="${CLIENT_SANS:-DNS:localhost,IP:127.0.0.1}"
CLI_SANS="${CLI_SANS:-DNS:localhost,IP:127.0.0.1}"

CA_KEY="${OUT_DIR}/nomad-agent-ca-key.pem"
CA_CERT="${OUT_DIR}/nomad-agent-ca.pem"

create_ca() {
  echo "[INFO] Generating CA..."
  openssl genrsa -out "${CA_KEY}" 4096
  openssl req -x509 -new -nodes -key "${CA_KEY}" -sha256 -days "${DAYS_CA}" \
    -subj "/CN=nomad-agent-ca" \
    -out "${CA_CERT}"
}

gen_cert() {
  local name="$1"
  local cn="$2"
  local sans="$3"
  local eku="$4"

  local key="${OUT_DIR}/${name}-key.pem"
  local csr="${OUT_DIR}/${name}.csr"
  local crt="${OUT_DIR}/${name}.pem"
  local ext="${OUT_DIR}/${name}.ext"

  openssl genrsa -out "${key}" 4096
  openssl req -new -key "${key}" -subj "/CN=${cn}" -out "${csr}"

  cat > "${ext}" <<EOF
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = ${eku}
subjectAltName = ${sans}
EOF

  openssl x509 -req -in "${csr}" -CA "${CA_CERT}" -CAkey "${CA_KEY}" -CAcreateserial \
    -out "${crt}" -days "${DAYS_CERT}" -sha256 -extfile "${ext}"

  rm -f "${csr}" "${ext}"
}

if [[ ! -f "${CA_CERT}" || ! -f "${CA_KEY}" ]]; then
  create_ca
else
  echo "[INFO] Existing CA found, reusing: ${CA_CERT}"
fi

echo "[INFO] Generating server/client/cli certificates..."
gen_cert "server" "server.global.nomad" "${SERVER_SANS}" "serverAuth,clientAuth"
gen_cert "client" "client.global.nomad" "${CLIENT_SANS}" "clientAuth,serverAuth"
gen_cert "cli"    "cli.global.nomad"    "${CLI_SANS}"    "clientAuth"

chmod 600 "${OUT_DIR}"/*-key.pem

cat <<MSG
[OK] Certificates generated in: ${OUT_DIR}
- ${CA_CERT}
- ${OUT_DIR}/server.pem
- ${OUT_DIR}/client.pem
- ${OUT_DIR}/cli.pem
MSG
