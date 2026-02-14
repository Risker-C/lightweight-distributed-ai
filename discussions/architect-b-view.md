# 架构专家B视角：分布式 AI 助手系统设计（边缘极简 + 云端重计算）

## 0. 约束与目标（从“算力不对称”出发）
- **本地根节点**：1 vCPU / 921MB RAM / 无 Docker。结论：本地不适合承载任何“常驻重服务”（向量库、消息队列、模型推理、复杂编排）。
- **云端从节点**：可 Docker 部署。结论：把“重计算 + 复杂依赖 + 可扩缩”尽量放云端。
- **系统目标**：
  - 低资源根节点也能稳定运行（极简、可恢复、可升级）
  - 云端弹性扩展（按需用 CPU/GPU、可做多租户隔离）
  - 端到端可观测、可回放、可审计（尤其是工具调用/文件操作）

我的核心观点：**把“控制平面”尽量上移到云端**，本地根节点更像“边缘代理/入口”，只负责：会话入口、最小状态、权限边界、离线降级。

---

## 1. 总体方案（Cloud-control / Edge-agent 反转控制）
### 1.1 逻辑角色
- **Edge Root（本地根节点）**：
  - 运行一个单进程（建议 Go 或 Python+uvicorn，但 Go 更省内存）的 `edge-gateway`
  - 提供本地入口：CLI/HTTP（可选 Web UI，但不建议常驻前端）
  - 维护最小配置与凭据：`config.yaml` + `sqlite`（仅存会话元信息、缓存、审计索引）
  - 对外只做“向云端发起的长连接”（WebSocket/gRPC stream），避免入站端口/内网穿透复杂度
  - 本地工具执行（访问本地文件、局域网设备）只在 root 上执行，云端通过“受控 RPC”调用

- **Cloud Control Plane（云端控制平面）**：
  - 负责：编排、队列、路由、插件目录、作业状态机、限流、审计、观测
  - 负责把一次对话拆成多个 job（LLM 推理、检索、工具调用、总结）并分配给 Worker

- **Cloud Workers（云端从节点/执行平面）**：
  - 全 Docker 化：`llm-worker`、`embed-worker`、`retrieval-worker`、`web-worker`、`tool-sandbox-worker`
  - 支持水平扩展，按标签调度（cpu/gpu、region、cost-tier）

### 1.2 连接模型（强烈建议“云端为中心”）
- Root 通过 **outbound-only** 方式连接云端：
  - WebSocket（最简单、穿透性最好）或 gRPC streaming（类型安全更好）
  - 心跳 + 断线重连 + 会话续传 token
- 云端不需要主动连回本地（避免 NAT、端口暴露、安全审计复杂）

---

## 2. 数据流（一次请求的拆分与调度）
1) 用户在本地 root 发起请求（文本/语音/文件引用）
2) root 进行轻量预处理：
   - 解析意图（规则/小模型可选，但建议直接交给云端）
   - 打包上下文（本地文件仅传“引用/摘要/哈希”，不直接外发内容，除非用户允许）
3) root 将 `ConversationEvent` 推送到云端控制平面
4) 云端控制平面生成 `Plan`：
   - LLM 推理 job（可能需要 GPU）
   - 检索 job（向量检索、知识库、网页）
   - 工具调用 job（如果需要访问本地文件/设备，则转成 `edge-tool-call`）
5) 云端 workers 执行并回传增量结果（streaming tokens / partial results）
6) 如果需要本地工具：云端发 `ToolCallRequest` 给 root，root 在本地执行并回传 `ToolCallResult`
7) 云端汇总，输出最终回答回 root

关键点：**云端才是编排与状态机中心**；root 只需要保持与云端的“会话通道”和“本地工具能力”。

---

## 3. 协议与可维护性（Versioned Capability Contract）
### 3.1 统一消息模型（建议 JSON-RPC 2.0 风格 + 版本字段）
- `message_type`: `event | job | tool_call | tool_result | log | metrics`
- `schema_version`: 例如 `v1`
- `capabilities`: root/worker 启动时上报：
  - root：`fs.read`, `fs.write`, `shell.exec`, `lan.http`, `device.control`...
  - worker：`llm.gpu`, `embed.cpu`, `web.fetch`, `retrieval.vector`...

好处：
- 云端可根据 capability 自动路由
- 插件升级/回滚可控，避免“隐式依赖”

### 3.2 插件体系（可选，但推荐）
- 云端维护插件 registry（Docker image + manifest）
- root 只支持少量内置工具（文件、shell、局域网 HTTP），并通过 manifest 声明参数/权限

---

## 4. 性能视角：把瓶颈从“root 常驻”迁走
### 4.1 root 的内存预算
- 目标：root 常驻 RSS < 200MB（给 OS/缓存留余量）
- 避免：
  - 本地向量数据库常驻（容易爆内存/IO 抖动）
  - 本地多进程 worker
  - 大量 Python 依赖常驻（若必须 Python，尽量单进程 + uvloop + 精简依赖）

### 4.2 云端异构算力
- LLM 推理：GPU worker（按需扩缩，支持 spot 实例）
- Embedding/检索：CPU worker（批处理、缓存）
- Web 抓取：隔离 worker（防止 SSRF/不可信内容影响核心服务）

### 4.3 缓存策略（“云端大缓存 + root 小缓存”）
- 云端：
  - prompt/response cache（基于 hash + policy）
  - embedding cache（高收益）
- root：
  - 最近会话摘要（sqlite）
  - 允许用户设置“敏感不上传”时，仅保留本地摘要

---

## 5. 成本视角：按需启停、分层服务、托管优先
### 5.1 控制平面尽量用托管（若允许）
- 优先选择托管队列/DB：
  - 队列：SQS / PubSub / RabbitMQ 托管版
  - DB：Postgres 托管版（作业状态、审计、用户配置）
- 若必须自建：单个 Docker Compose 起 `postgres + nats`（比 Kafka 便宜/轻量）

### 5.2 Worker 资源分层
- `tier-0`：CPU-only（检索、工具、结构化处理）
- `tier-1`：小 GPU（轻量模型、实时对话）
- `tier-2`：大 GPU（复杂推理、长上下文）
- 调度策略：默认走便宜层，置信度不足或任务标记再升级

### 5.3 计费/配额
- 每个 job 带 cost 标签（token、GPU 秒、外部 API 次数）
- 云端控制平面做限流与预算保护，root 仅展示提示

---

## 6. 安全与合规视角：边界清晰、最小外泄
### 6.1 权限边界
- root 的本地工具必须显式授权（allowlist）：
  - 文件路径白名单
  - shell 命令白名单/模板化
  - 局域网目标白名单（IP/域名）
- 云端请求本地工具调用必须带：
  - `request_id`、`user_confirmation`（可配置自动确认）
  - 参数签名（HMAC/mTLS）

### 6.2 连接安全
- root ↔ 云端：mTLS 或基于设备证书的双向认证
- 所有 tool_result 记录审计（本地 + 云端摘要），便于追踪

### 6.3 数据策略
- 默认：本地文件不上传正文，只上传摘要/哈希/结构化结果
- 用户可临时授权“上传片段”以换取更好回答

---

## 7. 可靠性视角：断网可用、重试幂等、状态机可回放
### 7.1 断网降级
- root 支持离线模式：
  - 基础 FAQ/规则回复
  - 本地工具（文件检索、简单自动化）
- 云端不可用时：请求排队（sqlite）+ 指数退避重连

### 7.2 幂等与重试
- 每个 job/tool_call 有 `idempotency_key`
- root 执行工具时写入本地审计表：避免断线重传导致重复执行危险命令

### 7.3 可回放
- 云端保存：事件流（event sourcing 轻量版）+ 关键快照
- 便于问题定位与模型输出对比

---

## 8. 可部署形态（落地建议）
### 8.1 Root（无 Docker）
- 一个静态二进制 `edge-gateway`（Go）或一个 Python venv（但要控制依赖）
- systemd service（如果有），否则用简单守护脚本
- 本地存储：`~/.assistant/` 下的 `config.yaml` + `state.db`

### 8.2 Cloud（Docker）
- 镜像建议：
  - `control-plane`（API + orchestrator）
  - `router`（可选，做流量入口）
  - `worker-llm`、`worker-embed`、`worker-web`、`worker-retrieval`
- 运行方式：
  - 起步：单机 Docker Compose
  - 进阶：Kubernetes（需要时再上，避免过早复杂化）

---

## 9. 备选方案对比（我偏好的理由）
### 方案A：本地 root 做控制平面（传统）
- 优点：本地可控、隐私强
- 缺点：1核/921MB 很难跑编排/队列/检索/观测；升级维护成本高；扩展到多云端节点复杂

### 方案B：云端控制平面 + 本地 root 做边缘代理（推荐）
- 优点：
  - root 轻量稳定；云端扩缩灵活
  - 调度/配额/审计集中，便于运维
  - root 只做敏感工具与入口，安全边界清晰
- 缺点：
  - 云端依赖增强；需要做好断网降级与隐私策略

我推荐方案B，并用“默认不上传正文 + 明确授权”的策略弥补隐私顾虑。

---

## 10. 最小可行版本（MVP）建议
- Root：WebSocket 客户端 + 本地工具执行器 + sqlite 审计
- 云端：
  - 一个 `control-plane`（HTTP + WS）
  - 一个 `worker-llm`（可先用 CPU 模型或调用外部 API）
- 先跑通：对话 → 云端推理 → 需要本地文件时触发 tool_call → root 执行 → 回传 → 汇总

---

## 11. 我希望主方案里明确的“决策点”（给架构总监）
- 控制平面是否允许使用托管 DB/队列（显著影响成本与复杂度）
- root 是否必须提供 Web UI（若必须，建议静态页面 + 反向代理，不引入重框架）
- 本地数据外发默认策略（摘要/片段/全量）与用户确认机制
