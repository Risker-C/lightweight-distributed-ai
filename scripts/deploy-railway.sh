#!/bin/bash
# Railway部署脚本

set -e

IMAGE="docker.io/riskerc/lightweight-ai-worker:latest"

echo "🚂 开始部署到Railway..."

# 检查是否已安装railway CLI
if ! command -v railway &> /dev/null; then
    echo "📥 安装Railway CLI..."
    npm install -g @railway/cli
fi

# 检查是否已登录
if ! railway whoami &> /dev/null; then
    echo "🔐 请登录Railway..."
    railway login
fi

# 获取配置
read -p "根节点URL (如 http://YOUR_IP:5000): " ROOT_NODE_URL
read -p "Worker名称 [railway-worker-1]: " WORKER_NAME
WORKER_NAME=${WORKER_NAME:-railway-worker-1}

# 初始化项目
echo "📦 初始化Railway项目..."
railway init

# 设置环境变量
echo "⚙️  配置环境变量..."
railway variables set PORT=8080
railway variables set ROOT_NODE_URL=$ROOT_NODE_URL
railway variables set WORKER_NAME=$WORKER_NAME
railway variables set PYTHONUNBUFFERED=1

# 部署
echo "🚀 开始部署..."
railway up

echo "⏳ 等待部署完成..."
sleep 15

# 获取服务信息
echo "📊 服务状态:"
railway status

echo "✅ 部署完成！"
echo "📝 查看日志: railway logs"
echo "🌐 获取URL: railway domain"
