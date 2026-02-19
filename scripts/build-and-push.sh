#!/bin/bash
# Docker镜像构建和推送脚本

set -e

# 配置
IMAGE_NAME="riskerc/lightweight-ai-worker"
VERSION="v1.0.0"

echo "🔨 开始构建Docker镜像..."

# 进入项目目录
cd "$(dirname "$0")/../src/lightweight-root"

# 构建镜像
echo "📦 构建镜像: $IMAGE_NAME:$VERSION"
docker build -t $IMAGE_NAME:latest \
             -t $IMAGE_NAME:$VERSION \
             --platform linux/amd64,linux/arm64 \
             .

echo "✅ 镜像构建完成"

# 显示镜像信息
docker images | grep lightweight-ai-worker

# 推送到Docker Hub
read -p "是否推送到Docker Hub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🚀 推送镜像到Docker Hub..."
    docker push $IMAGE_NAME:latest
    docker push $IMAGE_NAME:$VERSION
    echo "✅ 推送完成"
    echo "📍 镜像地址: docker.io/$IMAGE_NAME:latest"
fi

echo "🎉 完成！"
