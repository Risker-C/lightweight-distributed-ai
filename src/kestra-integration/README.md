# Kestra + Nomad 集成方案

本目录提供一个完整的 Kestra 与 Nomad 集成模板，用于实现：
- 工作流编排（Kestra）
- 任务调度与执行（Nomad）
- 任务状态监控
- 失败重试
- 并行执行
- DAG 依赖编排

---

## 目录结构

```text
kestra-integration/
├── docker-compose.yml
├── README.md
├── config/
│   ├── application.yml
│   └── database.yml
├── flows/
│   ├── nomad-job-flow.yml
│   ├── parallel-tasks-flow.yml
│   └── dag-workflow.yml
├── plugins/
│   └── nomad-plugin.js
└── scripts/
    ├── setup.sh
    └── test-flow.sh
```

---

## 架构说明

- **Kestra**：流程编排引擎，提供 API/UI
- **PostgreSQL**：Kestra 的 repository/queue 元数据存储
- **Nomad (dev mode)**：作业调度与执行
- **Nomad Plugin (Node.js)**：封装 Nomad API（提交、查询、监控、停止）

数据流：
1. Kestra flow 通过 HTTP API 提交 Job 到 Nomad
2. Kestra 轮询 Nomad allocation 状态
3. 根据状态成功/失败推进后续流程
4. 并行流与 DAG 流复用基础 Job flow

---

## 快速开始

### 1) 启动环境并导入流程

```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project/src/kestra-integration
./scripts/setup.sh
```

启动后访问：
- Kestra UI: http://localhost:8080
- Nomad UI: http://localhost:4646

### 2) 测试流程

```bash
./scripts/test-flow.sh
```

该脚本会依次触发：
- `nomad-job-flow`
- `parallel-tasks-flow`
- `dag-workflow`

---

## 核心能力映射

### 1. Nomad API 调用
- `flows/nomad-job-flow.yml` 使用 `io.kestra.plugin.core.http.Request` 调用：
  - `POST /v1/jobs`（提交作业）
  - `GET /v1/job/{job}/summary`（查询摘要）
- `plugins/nomad-plugin.js` 提供可复用 API 封装

### 2. 任务状态监控
- `nomad-job-flow.yml` 中 `monitor_nomad_job` 使用轮询 `/v1/job/{job}/allocations`
- 检测 `running/complete` 判定成功，`failed/lost` 判定失败

### 3. 失败重试
- 在提交、监控、摘要查询和 Subflow 调用中均配置 `retry`
- 采用常量间隔重试（`type: constant`）

### 4. 并行执行
- `parallel-tasks-flow.yml` 使用 `io.kestra.plugin.core.flow.Parallel`
- 并行触发多个基础 Nomad 子流程

### 5. DAG 依赖
- `dag-workflow.yml` 使用 `io.kestra.plugin.core.flow.Dag`
- 通过 `dependsOn` 构建阶段依赖（prep -> feature/train + quality -> package）

---

## Nomad 自定义插件（Node）

`plugins/nomad-plugin.js` 支持：

```bash
node plugins/nomad-plugin.js submit <job-id>
node plugins/nomad-plugin.js monitor <job-id>
node plugins/nomad-plugin.js summary <job-id>
node plugins/nomad-plugin.js stop <job-id>
```

可选环境变量：
- `NOMAD_ADDR`（默认 `http://localhost:4646`）
- `NOMAD_TOKEN`（ACL 场景）

---

## 生产化建议

1. 将 Nomad 从 dev 模式切换为 server/client 集群模式
2. 为 Kestra 开启认证和 RBAC
3. 配置 TLS（Kestra API / Nomad API）
4. 使用 Nomad ACL Token 与 Kestra Secret 管理凭证
5. 将流程发布接入 CI/CD（flow lint + API import + smoke tests）

