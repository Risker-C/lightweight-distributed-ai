#!/bin/bash
# Koyeb部署脚本

set -e

IMAGE="docker.io/riskerc/lightweight-ai-worker:latest"
SERVICE_NAME="lightweight-worker"
INSTANCE_TYPE="nano"
REGION="fra"

echo "🚀 开始部署到Koyeb..."

# 检查是否已安装koyeb CLI
if ! command -v koyeb &> /dev/null; then
    echo "📥 安装Koyeb CLI..."
    curl -fsSL https://cli.koyeb.com/install.sh | sh
fi

# 检查是否已登录
if ! koyeb whoami &> /dev/null; then
    echo "🔐 请登录Koyeb..."
    koyeb login
fi

# 获取配置
read -p "根节点URL (如 http://YOUR_IP:5000): " ROOT_NODE_URL
read -p "Worker名称 [koyeb-worker-1]: " WORKER_NAME
WORKER_NAME=${WORKER_NAME:-koyeb-worker-1}

# 部署服务
echo "📦 部署服务: $SERVICE_NAME"
koyeb service create $SERVICE_NAME \
  --docker $IMAGE \
  --ports 8080:http \
  --routes /:8080 \
  --env PORT=8080 \
  --env ROOT_NODE_URL=$ROOT_NODE_URL \
  --env WORKER_NAME=$WORKER_NAME \
  --env PYTHONUNBUFFERED=1 \
  --instance-type $INSTANCE_TYPE \
  --regions $REGION \
  --checks http:8080:/health

echo "⏳ 等待部署完成..."
sleep 10

# 获取服务信息
echo "📊 服务状态:"
koyeb service get $SERVICE_NAME

# 获取URL
SERVICE_URL=$(koyeb service get $SERVICE_NAME -o json | jq -r '.app_domain' 2>/dev/null || echo "")
if [ -n "$SERVICE_URL" ]; then
    echo "✅ 部署完成！"
    echo "🌐 服务URL: https://$SERVICE_URL"
    echo "🔍 测试健康检查: curl https://$SERVICE_URL/health"
else
    echo "⚠️  无法获取服务URL，请手动检查"
fi

echo "📝 查看日志: koyeb service logs $SERVICE_NAME"
