# Execution Gateway

轻量级统一执行网关（Node.js），用于提交和管理以下执行后端：

- Nomad
- GitHub Actions
- Cloud Run Jobs

## 功能

- 统一任务 API：提交 / 查询状态 / 拉取日志 / 取消任务
- Bearer Token 认证
- TLS（HTTPS）支持
- 上游调用重试（指数退避）
- 结构化日志（stdout + 可选文件）

---

## 目录结构

```text
src/execution-gateway/
├── index.js
├── api/
│   ├── handlers.js
│   └── router.js
├── nomad/
│   └── client.js
├── providers/
│   ├── githubActions.js
│   └── cloudRun.js
├── services/
│   └── taskService.js
├── lib/
│   ├── auth.js
│   ├── config.js
│   ├── errors.js
│   ├── http.js
│   ├── logger.js
│   ├── retry.js
│   └── taskStore.js
├── tests/
│   ├── api.test.js
│   └── taskService.test.js
├── config.yaml
├── Dockerfile
└── docker-compose.yml
```

---

## 快速开始

### 1) 本地运行

```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project/src/execution-gateway
node index.js
```

默认读取 `./config.yaml`。

### 2) 运行测试

```bash
npm test
```

---

## API 说明

> 所有请求都需要 Header：

```http
Authorization: Bearer <token>
Content-Type: application/json
```

### POST `/v1/tasks/submit`

提交任务。

示例（Nomad）：

```bash
curl -X POST http://localhost:8080/v1/tasks/submit \
  -H 'Authorization: Bearer dev-token-123' \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "nomad",
    "task": {
      "job_id": "demo-job-1",
      "image": "busybox:latest",
      "command": "echo",
      "args": ["hello"]
    }
  }'
```

示例（GitHub Actions）：

```json
{
  "provider": "github_actions",
  "task": {
    "workflow_id": "deploy.yml",
    "ref": "main",
    "inputs": {
      "env": "prod"
    }
  }
}
```

示例（Cloud Run）：

```json
{
  "provider": "cloud_run",
  "task": {
    "project": "my-project",
    "region": "asia-east1",
    "job": "my-job"
  }
}
```

### GET `/v1/tasks/{id}/status`

查询任务状态。

### GET `/v1/tasks/{id}/logs`

查询任务日志。

### DELETE `/v1/tasks/{id}`

取消任务。

---

## 配置

编辑 `config.yaml`：

- `server`: 监听地址和超时
- `tls`: 是否启用 HTTPS 及证书路径
- `auth`: Bearer Token 列表
- `retry`: 重试策略
- `providers`: 各执行后端配置

> 注意：当前 YAML 解析器是轻量实现，建议使用简单 key/value 的 YAML 格式（与示例一致）。

---

## TLS 启用

1. 将证书放到：
   - `certs/server.crt`
   - `certs/server.key`
2. 在 `config.yaml` 设置：

```yaml
tls:
  enabled: true
  cert_file: ./certs/server.crt
  key_file: ./certs/server.key
```

---

## Docker

### 构建

```bash
docker build -t execution-gateway:local .
```

### 运行

```bash
docker run --rm -p 8080:8080 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  execution-gateway:local
```

### Docker Compose（含 Nomad dev）

```bash
docker compose up --build
```

---

## 设计说明

- 统一入口 API + Provider 抽象层
- Task 元数据保存在内存（`TaskStore`），适合轻量网关
- 生产环境可替换为 Redis/PostgreSQL 持久化
- 错误通过统一 `GatewayError` 返回规范 JSON
