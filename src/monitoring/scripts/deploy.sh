#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker 未安装，请先安装 Docker / Docker Compose" >&2
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "[ERROR] 未找到 docker compose 命令" >&2
  exit 1
fi

http_ok() {
  url="$1"
  if command -v curl >/dev/null 2>&1; then
    curl -fsS "$url" >/dev/null 2>&1
    return $?
  fi
  if command -v wget >/dev/null 2>&1; then
    wget -q -O - "$url" >/dev/null 2>&1
    return $?
  fi
  echo "[ERROR] curl/wget 均不可用，无法做健康检查" >&2
  return 1
}

wait_for() {
  name="$1"
  url="$2"
  retries="${3:-30}"

  i=1
  while [ "$i" -le "$retries" ]; do
    if http_ok "$url"; then
      echo "[OK] $name 已就绪"
      return 0
    fi
    echo "[WAIT] $name 未就绪，重试 ${i}/${retries} ..."
    i=$((i + 1))
    sleep 2
  done

  echo "[ERROR] $name 启动超时" >&2
  return 1
}

cd "$ROOT_DIR"

echo "[1/5] 校验 Compose 配置..."
sh -c "$COMPOSE_CMD -f '$COMPOSE_FILE' config >/dev/null"

echo "[2/5] 拉取镜像..."
sh -c "$COMPOSE_CMD -f '$COMPOSE_FILE' pull"

echo "[3/5] 启动监控栈..."
sh -c "$COMPOSE_CMD -f '$COMPOSE_FILE' up -d --remove-orphans"

echo "[4/5] 检查核心服务健康状态..."
wait_for "Prometheus" "http://localhost:9090/-/healthy"
wait_for "Alertmanager" "http://localhost:9093/-/healthy"
wait_for "Grafana" "http://localhost:3000/api/health"

echo "[5/5] 当前服务状态"
sh -c "$COMPOSE_CMD -f '$COMPOSE_FILE' ps"

echo "\n部署完成："
echo "- Prometheus:  http://localhost:9090"
echo "- Alertmanager: http://localhost:9093"
echo "- Grafana:     http://localhost:3000 (默认 admin / admin123!)"
