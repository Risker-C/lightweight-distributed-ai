# Docker Worker 镜像制作指南

## 1. 目标

构建适用于 Oracle ARM（可兼容 AMD64）的 Worker 镜像，并推送到镜像仓库供 Coolify 拉取部署。

---

## 2. 推荐目录结构

```text
worker/
  ├─ Dockerfile
  ├─ .dockerignore
  ├─ package.json
  ├─ package-lock.json
  ├─ src/
  └─ config/
```

---

## 3. Dockerfile（生产推荐）

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS runtime
WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

COPY --from=deps /app/node_modules ./node_modules
COPY src ./src
COPY config ./config
COPY package*.json ./

ENV NODE_ENV=production
ENV WORKER_PORT=3001

EXPOSE 3001

HEALTHCHECK --interval=20s --timeout=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3001/health || exit 1

USER app
CMD ["node", "src/server.js"]
```

---

## 4. .dockerignore（建议）

```gitignore
node_modules
.git
.github
.vscode
.idea
coverage
tests
*.log
.env
.env.*
Dockerfile*
```

---

## 5. 本地构建与运行

```bash
cd worker

docker build -t ai-worker:local .

docker run --rm -p 3001:3001 \
  -e WORKER_ID=worker-local \
  -e ROOT_NODE_URL=http://host.docker.internal:3000 \
  -e ROOT_NODE_SECRET=please-change \
  ai-worker:local
```

健康检查：

```bash
curl http://127.0.0.1:3001/health
```

---

## 6. 多架构构建（ARM64 + AMD64）

> Oracle 免费实例通常是 ARM64，必须确保镜像支持 `linux/arm64`。

```bash
# 1) 初始化 buildx
docker buildx create --name multiarch --use

docker buildx inspect --bootstrap

# 2) 多架构构建并推送
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <your-registry>/ai-worker:v1.0.0 \
  -t <your-registry>/ai-worker:latest \
  --push .
```

验证镜像架构：

```bash
docker buildx imagetools inspect <your-registry>/ai-worker:v1.0.0
```

---

## 7. 推送到镜像仓库

### 7.1 Docker Hub 示例

```bash
docker login

docker tag ai-worker:local <dockerhub-user>/ai-worker:v1.0.0
docker push <dockerhub-user>/ai-worker:v1.0.0
```

### 7.2 标签策略建议

- 稳定版本：`v1.0.0`
- 灰度版本：`v1.0.0-rc.1`
- 永久追踪：`latest`（仅用于测试/演示）

生产优先使用固定版本标签。

---

## 8. CI 自动构建（GitHub Actions 示例）

创建 `.github/workflows/worker-image.yml`：

```yaml
name: build-worker-image

on:
  push:
    branches: ["main"]
    tags: ["v*"]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: ./worker
          push: true
          platforms: linux/amd64,linux/arm64
          tags: |
            <dockerhub-user>/ai-worker:latest
            <dockerhub-user>/ai-worker:${{ github.sha }}
```

---

## 9. 镜像优化建议

- 使用多阶段构建，避免 dev 依赖进入生产镜像
- 尽量使用 Alpine/Distroless
- 严格 `.dockerignore`
- 仅复制运行时必需文件
- 使用非 root 用户
- 打开 healthcheck

---

## 10. 安全建议

- 不在镜像中写死 API Key
- 运行时通过环境变量注入
- 使用只读文件系统（按需）
- 设置资源限制（CPU/内存）

运行示例：

```bash
docker run -d --name worker \
  --memory=2g --cpus=1 \
  -p 3001:3001 \
  -e WORKER_ID=worker-1 \
  -e ROOT_NODE_URL=http://<root-node-ip>:3000 \
  -e ROOT_NODE_SECRET=please-change \
  <your-registry>/ai-worker:v1.0.0
```

---

## 11. 常见问题

### Q1：Oracle 上拉镜像报 `exec format error`

镜像只构建了 AMD64，未包含 ARM64。请用 buildx 多架构构建。

### Q2：容器不断重启

- 先看日志：`docker logs <container>`
- 检查环境变量是否缺失
- 检查健康检查路径是否存在

### Q3：镜像体积过大

- 检查是否把 `node_modules`、测试目录打进了镜像
- 合并 RUN 层并清理缓存

---

## 12. 与 Coolify 联动

在 Coolify 中直接填写：

- Image: `<your-registry>/ai-worker:v1.0.0`
- Port: `3001`
- Env: 按 `coolify-setup.md` 填写

部署后检查：

```bash
curl http://<worker-ip>:3001/health
```

可返回 200 即表示镜像与服务运行正常。
