# Coolify 部署指南（Worker 节点）

## 1. 目标

在每台 Oracle Worker VM 上安装 Coolify，并用它部署 Worker 容器服务。

---

## 2. 环境准备

每台 Worker VM 先执行：

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ca-certificates
```

确保已安装 Docker（若未安装）：

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
docker version
```

---

## 3. 安装 Coolify

> 官方一键安装脚本可能随版本更新，请以官网文档为准。

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

安装完成后，默认访问：

- `http://<worker-ip>:8000`

首次登录后务必修改管理员密码。

---

## 4. 创建 Worker 应用

### 4.1 在 Coolify 创建 Project

- Project Name: `distributed-ai-assistant`
- Environment: `production`

### 4.2 新建 Resource（Docker Compose 或 Docker Image）

推荐用 Docker Image（简单稳定）：

- Image: `<your-registry>/ai-worker:<tag>`
- Port: `3001`

### 4.3 环境变量配置（关键）

```env
WORKER_ID=worker-1
WORKER_PORT=3001
ROOT_NODE_URL=http://<root-node-ip>:3000
ROOT_NODE_SECRET=please-change-to-a-strong-random-secret

OPENAI_API_KEY=
ANTHROPIC_API_KEY=

ENABLE_WEB_SEARCH=true
ENABLE_CODE_EXEC=true
ENABLE_FILE_TOOLS=true
LOG_LEVEL=info
```

### 4.4 健康检查

路径建议：

- `/health`

间隔建议：

- interval: 20s
- timeout: 5s
- retries: 3

---

## 5. Docker Compose 模板（可直接粘贴）

```yaml
version: "3.8"

services:
  worker:
    image: <your-registry>/ai-worker:latest
    restart: unless-stopped
    ports:
      - "3001:3001"
    environment:
      - WORKER_ID=worker-1
      - WORKER_PORT=3001
      - ROOT_NODE_URL=http://<root-node-ip>:3000
      - ROOT_NODE_SECRET=${ROOT_NODE_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ENABLE_WEB_SEARCH=true
      - ENABLE_CODE_EXEC=true
      - ENABLE_FILE_TOOLS=true
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3001/health"]
      interval: 20s
      timeout: 5s
      retries: 3
```

---

## 6. 多 Worker 复制部署

对 `worker-2/worker-3/...` 重复部署时，仅修改：

- `WORKER_ID`
- 实例 IP / 域名

其余配置保持一致。

---

## 7. 发布与回滚策略

### 7.1 发布

- 使用版本标签：`v1.0.0`, `v1.0.1`，避免一直 `latest`
- 在 Coolify 更新镜像标签并部署

### 7.2 回滚

- 若新版本异常，切回上一个稳定标签重新 Deploy

---

## 8. 运维建议

- 开启自动重启（`restart: unless-stopped`）
- 收敛日志（避免无限增长）
- 给每个 Worker 单独监控（CPU/内存/健康检查失败次数）

---

## 9. 故障排查

### 9.1 Coolify 页面无法访问

- 检查 Oracle 安全组是否放行 `8000`
- 检查实例防火墙是否放行 `8000`
- `docker ps` 查看 Coolify 容器状态

### 9.2 Worker 启动失败

- 查看部署日志
- 检查镜像地址和 tag 是否存在
- 检查必填环境变量是否缺失

### 9.3 Worker 健康检查失败

- 确认服务监听 `0.0.0.0:3001`
- 确认 `/health` 路径存在并返回 200

---

## 10. 完成标志

- [ ] Coolify 可以访问
- [ ] Worker 容器状态为 running + healthy
- [ ] 根节点 `GET /api/workers` 能看到该 Worker

下一步请进行：

- 根节点部署与 E2E：`LIGHTWEIGHT_DEPLOYMENT_GUIDE.md`
