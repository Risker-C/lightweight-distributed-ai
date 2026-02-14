# 轻量级部署指南（主指南）

> 目标：基于 Oracle Cloud Always Free + Coolify + Docker，部署一个“本地根节点 + 云端 Worker 节点”的分布式 AI 助手系统。

## 1. 架构与部署目标

### 1.1 推荐架构

- 本地 Root Node（根节点）
  - 负责：路由、会话、负载均衡、故障转移
- Oracle Cloud Worker Nodes（2~4 个）
  - 负责：模型调用、工具执行、任务处理
- Coolify（部署控制面）
  - 负责：Worker 容器化部署与运维

```text
Client (Web/IM/Bot)
       |
       v
Root Node (Local / VPS)
       |
  -------------------------
  |          |            |
Worker-1   Worker-2    Worker-3 ...
(Oracle)   (Oracle)    (Oracle)
```

### 1.2 本指南覆盖内容

1. Oracle Cloud Always Free 申请与实例准备（详见 `oracle-cloud-setup.md`）
2. Coolify 部署与 Worker 上线（详见 `coolify-setup.md`）
3. 本地根节点部署（本文件）
4. Worker Docker 镜像制作（详见 `docker-worker-guide.md`）
5. 端到端集成测试（本文件）

---

## 2. 前置条件

- 一张可用信用卡（Oracle 仅身份验证，Always Free 资源不扣费）
- 本地机器（Linux/macOS/WSL）
  - Docker / Docker Compose
  - Git
  - Node.js 18+
- 已准备 API Key（按需）
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - 其他工具 API Key（可选）

---

## 3. 快速部署总流程

1. 申请 Oracle 账号并创建 2~4 台 ARM 实例
2. 每台实例安装 Coolify，部署 Worker 服务
3. 本地部署 Root Node，配置 Worker 列表
4. 完成健康检查、负载测试、故障切换测试

---

## 4. 本地根节点部署步骤

> 以下步骤假设你的项目根目录为：
> `/root/.openclaw/workspace/distributed-ai-assistant-project`

### 4.1 目录与配置文件

```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project
mkdir -p runtime/root-node logs data
```

创建环境变量文件 `runtime/root-node/.env`：

```env
# 基础服务
NODE_ENV=production
ROOT_NODE_PORT=3000
ROOT_NODE_HOST=0.0.0.0

# 鉴权
ROOT_NODE_SECRET=please-change-to-a-strong-random-secret

# Worker 列表（逗号分隔）
WORKERS=http://<worker1-ip>:3001,http://<worker2-ip>:3001,http://<worker3-ip>:3001

# 健康检查与负载
HEALTH_CHECK_INTERVAL_MS=10000
WORKER_TIMEOUT_MS=30000
LOAD_BALANCE_STRATEGY=least-connections

# LLM Keys（按需）
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# 日志
LOG_LEVEL=info
LOG_DIR=./logs

# 数据
DATA_DIR=./data
```

### 4.2 Docker Compose 方式（推荐）

创建 `runtime/root-node/docker-compose.yml`：

```yaml
version: "3.8"

services:
  root-node:
    image: node:20-alpine
    container_name: root-node
    working_dir: /app
    restart: unless-stopped
    ports:
      - "3000:3000"
    env_file:
      - ./.env
    volumes:
      - ../../:/app
      - ../../logs:/app/logs
      - ../../data:/app/data
    command: sh -c "npm ci && npm run start:root"
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 20s
      timeout: 5s
      retries: 5
```

启动：

```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project/runtime/root-node
docker compose up -d
```

查看日志：

```bash
docker compose logs -f root-node
```

### 4.3 源码直跑方式（可选）

```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project
npm ci
export $(grep -v '^#' runtime/root-node/.env | xargs)
npm run start:root
```

生产建议使用 PM2：

```bash
npm i -g pm2
pm2 start "npm run start:root" --name root-node
pm2 save
pm2 startup
```

### 4.4 根节点连通性验证

```bash
curl http://127.0.0.1:3000/health
curl http://127.0.0.1:3000/api/workers
```

预期：

- `/health` 返回 `healthy`
- `/api/workers` 显示已注册的 Worker 及状态

---

## 5. Worker 节点接入规范（摘要）

每个 Worker 必须至少配置：

```env
WORKER_ID=worker-1
WORKER_PORT=3001
ROOT_NODE_URL=http://<root-node-ip>:3000
ROOT_NODE_SECRET=please-change-to-a-strong-random-secret
```

可选能力开关：

```env
ENABLE_WEB_SEARCH=true
ENABLE_CODE_EXEC=true
ENABLE_FILE_TOOLS=true
```

---

## 6. 端到端集成测试（E2E）

> 本节为上线前必须执行的测试清单。

### 6.1 测试目标

- 验证根节点与 Worker 全链路可用
- 验证负载均衡是否生效
- 验证单 Worker 故障时系统可自动降级
- 验证恢复后可重新纳入集群

### 6.2 基础健康测试

```bash
# Root
curl -s http://<root-node-ip>:3000/health

# Workers
curl -s http://<worker1-ip>:3001/health
curl -s http://<worker2-ip>:3001/health
curl -s http://<worker3-ip>:3001/health
```

通过标准：

- 所有节点返回 HTTP 200
- 健康状态字段为 `healthy`

### 6.3 对话能力测试

```bash
curl -X POST http://<root-node-ip>:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "e2e-session-1",
    "message": "请回复：系统联通正常"
  }'
```

通过标准：

- 返回非空 `response`
- 返回 `worker_id`
- 延迟在可接受范围（如 < 10s，依模型而定）

### 6.4 多轮上下文测试

```bash
curl -X POST http://<root-node-ip>:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"ctx-1","message":"我叫小李"}'

curl -X POST http://<root-node-ip>:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"ctx-1","message":"我叫什么？"}'
```

通过标准：

- 第二轮能正确提取上下文（"小李"）

### 6.5 负载均衡测试

示例（并发 20，100 请求）：

```bash
# request.json
cat > /tmp/request.json << 'EOF'
{"session_id":"load-test","message":"hello"}
EOF

ab -n 100 -c 20 -p /tmp/request.json -T application/json \
  http://<root-node-ip>:3000/api/chat
```

通过标准：

- 失败请求数为 0（或极低）
- 多 Worker 均有请求命中（查看 root metrics）

### 6.6 故障切换测试

1) 手动停止一个 Worker：

```bash
# 在 worker-2 机器
cd <worker-deploy-dir>
docker compose stop worker
```

2) 继续压测或发请求，观察系统是否可用。

3) 恢复 Worker：

```bash
docker compose start worker
```

通过标准：

- Worker 停止期间，系统整体服务不中断
- Worker 恢复后能重新注册并接收流量

### 6.7 自动化 E2E 脚本模板

创建 `tests/e2e.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_URL=${ROOT_URL:-http://127.0.0.1:3000}

echo "[1/4] health"
curl -fsS "$ROOT_URL/health" >/dev/null

echo "[2/4] workers"
curl -fsS "$ROOT_URL/api/workers" >/dev/null

echo "[3/4] chat"
curl -fsS -X POST "$ROOT_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"e2e-auto","message":"ping"}' >/dev/null

echo "[4/4] metrics"
curl -fsS "$ROOT_URL/api/metrics" >/dev/null

echo "E2E OK"
```

执行：

```bash
chmod +x tests/e2e.sh
ROOT_URL=http://<root-node-ip>:3000 tests/e2e.sh
```

---

## 7. 上线检查清单

- [ ] Oracle 实例安全组端口已最小化暴露
- [ ] 所有默认密码已替换
- [ ] `ROOT_NODE_SECRET` 使用高强度随机值
- [ ] API Key 未写入仓库
- [ ] Root/Worker 健康检查通过
- [ ] 负载与故障切换测试通过
- [ ] 日志与告警链路可用

---

## 8. 常见问题

### Q1：Root 能启动，但 Worker 全部离线

- 检查 Worker 端 `ROOT_NODE_URL` 是否可达
- 检查 `ROOT_NODE_SECRET` 是否一致
- 检查防火墙 / 安全列表是否放行 3001

### Q2：请求偶发超时

- 提高 `WORKER_TIMEOUT_MS`
- 减少单 Worker 并发
- 检查模型 API 限流

### Q3：负载不均匀

- 将策略改为 `least-connections`
- 检查某个 Worker 是否性能异常（CPU/内存）

---

## 9. 关联文档

- Oracle 设置：`oracle-cloud-setup.md`
- Coolify 部署：`coolify-setup.md`
- Docker Worker 镜像：`docker-worker-guide.md`
