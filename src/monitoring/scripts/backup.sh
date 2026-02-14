#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
BACKUP_ROOT="${1:-$ROOT_DIR/backups}"
KEEP_DAYS="${KEEP_DAYS:-14}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUT_DIR="$BACKUP_ROOT/$TIMESTAMP"

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker 未安装" >&2
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

PROJECT_NAME="${COMPOSE_PROJECT_NAME:-$(basename "$ROOT_DIR")}" 
mkdir -p "$OUT_DIR"

backup_volume() {
  volume_name="$1"
  archive_name="$2"

  if docker volume inspect "$volume_name" >/dev/null 2>&1; then
    echo "[INFO] 备份 volume: $volume_name"
    docker run --rm \
      -v "$volume_name:/from:ro" \
      -v "$OUT_DIR:/to" \
      alpine:3.20 \
      sh -c "cd /from && tar -czf /to/$archive_name ."
  else
    echo "[WARN] volume 不存在，跳过: $volume_name"
  fi
}

echo "[1/4] 备份配置文件..."
tar -czf "$OUT_DIR/configs.tar.gz" \
  -C "$ROOT_DIR" \
  docker-compose.yml prometheus grafana alertmanager exporters scripts README.md

echo "[2/4] 导出 compose 解析结果..."
sh -c "$COMPOSE_CMD -f '$ROOT_DIR/docker-compose.yml' config" > "$OUT_DIR/compose.resolved.yml"

echo "[3/4] 备份持久化数据卷..."
backup_volume "${PROJECT_NAME}_prometheus-data" "prometheus-data.tar.gz"
backup_volume "${PROJECT_NAME}_grafana-data" "grafana-data.tar.gz"
backup_volume "${PROJECT_NAME}_alertmanager-data" "alertmanager-data.tar.gz"

echo "[4/4] 清理过期备份 (>${KEEP_DAYS} 天)..."
find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime "+$KEEP_DAYS" -exec rm -rf {} +

echo "备份完成: $OUT_DIR"
