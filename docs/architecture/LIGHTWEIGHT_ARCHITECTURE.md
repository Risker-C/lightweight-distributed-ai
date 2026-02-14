# LIGHTWEIGHT ARCHITECTURE - 小型设备可运行的分布式重构方案

## 1. 目标与约束

### 1.1 现状问题
当前架构依赖 Nomad/Consul/Kestra/PostgreSQL/Docker，资源门槛高（16GB RAM + 8核CPU），无法在以下设备运行：
- CPU: 1核
- RAM: 921MB
- Disk: 3.4GB 可用
- 无 Docker

### 1.2 重构目标
1. 在小型设备运行根节点（Root Node）
2. 根节点仅负责协调、调度、状态管理
3. 重任务全部转发到云端执行（GitHub Actions 为主，Cloud Run 为辅）
4. 根节点内存占用 < 100MB

### 1.3 设计原则
- 极简优先：能删就删，保留最小闭环
- 云端优先：本地只做轻任务与控制平面
- 单机稳定优先：避免多进程和复杂依赖
- 可观测优先：即使轻量，也要可追踪

---

## 2. 总体架构

```text
+--------------------------------------------------------------+
|                    Tiny Device (Root Node)                  |
|                                                              |
|  +-------------------+    +------------------------------+   |
|  | Flask API         |    | Scheduler + Dispatcher       |   |
|  | - submit task     |--->| - classify task              |   |
|  | - query status    |    | - route local/cloud          |   |
|  | - callback        |<---| - retry/backoff              |   |
|  +-------------------+    +------------------------------+   |
|            |                           |                     |
|            v                           v                     |
|      +-----------+              +-----------+                |
|      | SQLite    |              | Local     |                |
|      | state DB  |              | worker x1 |                |
|      +-----------+              +-----------+                |
+--------------------------------------------------------------+
                 |                         |
                 | REST/API               | REST/API
                 v                         v
      +----------------------+    +----------------------+
      | GitHub Actions       |    | Cloud Run Jobs/HTTP  |
      | (primary executor)   |    | (optional executor)  |
      +----------------------+    +----------------------+
```

### 架构结论
- 删除：Nomad、Consul、Kestra、PostgreSQL、Docker 依赖
- 保留并简化：Execution Gateway（作为统一执行路由层）
- 新核心：`Python + Flask + SQLite + in-process queue`

---

## 3. 根节点（Root Node）极简设计

## 3.1 进程模型
单进程（推荐）+ 单本地 worker 线程：
- 主线程：Flask API
- 后台线程A：调度器（扫描待执行任务）
- 后台线程B：分发器（路由到本地或云）
- 后台线程C：回收器（同步云任务状态）

说明：避免多进程可显著降低内存占用和运维复杂度。

## 3.2 组件职责
1. API 层（Flask）
   - 接收任务提交
   - 提供任务查询/取消
   - 提供云端回调入口（可选）

2. Scheduler（轻量调度器）
   - 每 1~3 秒扫描 SQLite 中 `PENDING` 任务
   - 依据任务标签与资源策略进行分类

3. Dispatcher（简化 Execution Gateway）
   - `local`：推入本地执行队列
   - `github_actions`：调用 GitHub Workflow Dispatch
   - `cloud_run`：调用 Cloud Run Job/HTTP API

4. State Store（SQLite）
   - 持久化任务状态、重试次数、执行日志摘要
   - 使用 WAL 模式，提高并发读写稳定性

5. Local Worker（仅轻任务）
   - 串行执行（并发=1）
   - 单任务内存限制目标 < 50MB

## 3.3 资源预算（目标）

| 模块 | 预估内存 |
|------|----------|
| Python runtime + Flask | 30-45MB |
| Scheduler + Dispatcher + Queue | 8-15MB |
| SQLite page cache | 5-12MB |
| Local worker（空闲） | 5-10MB |
| 缓冲与波动余量 | 10-15MB |
| **总计** | **58-97MB** |

满足目标：根节点常态 < 100MB。

---

## 4. 任务执行层设计

## 4.1 任务分级策略

### L0: 本地轻任务（允许本地执行）
满足全部条件才允许本地：
- 预计内存 < 50MB
- 预计执行时长 < 60s
- 无外部重依赖（如浏览器、容器、GPU）

示例：
- 文本规则检查
- 小文件转换
- 轻量状态同步

### L1/L2: 云端任务（默认）
任一条件成立即路由云端：
- 预计内存 >= 50MB
- 执行时长 >= 60s
- 需要依赖安装/编译/网络密集
- 需要并行扩展

示例：
- 构建、测试、打包
- 大模型推理或数据处理
- 多步骤流水线任务

## 4.2 云执行后端优先级
1. GitHub Actions（默认主后端）
   - 优点：免费额度可用、成熟日志、易审计
   - 方式：`workflow_dispatch` + run_id 追踪

2. Cloud Run（补充后端）
   - 用于 HTTP 任务或短时弹性任务
   - 在 Actions 队列拥堵或需快速 API 响应时启用

## 4.3 路由策略（建议）
```text
if task.class == "light" and local_queue_depth < 3:
    route = "local"
else:
    route = "github_actions"

if github_actions_rate_limited or task.requires_http_runtime:
    route = "cloud_run"
```

---

## 5. 简化版 Execution Gateway 设计

## 5.1 Gateway 职责（保留概念，最小实现）
- 接收统一任务格式
- 标准化执行后端调用
- 写入统一状态机
- 处理重试、超时、失败归档

## 5.2 最小 API 设计

### 提交任务
`POST /api/v1/tasks`
```json
{
  "task_type": "build",
  "payload": {"repo": "org/repo", "ref": "main"},
  "priority": 5,
  "constraints": {"max_mem_mb": 256, "max_duration_s": 1200}
}
```

### 查询任务
`GET /api/v1/tasks/{task_id}`

### 取消任务
`POST /api/v1/tasks/{task_id}/cancel`

### 云回调（可选）
`POST /api/v1/callbacks/github`

## 5.3 任务状态机
`PENDING -> DISPATCHING -> RUNNING -> SUCCESS | FAILED | TIMEOUT | CANCELED`

失败重试：
- 最大重试次数：3
- 退避策略：5s, 20s, 60s
- 仅对可重试错误（网络、429、5xx）生效

---

## 6. SQLite 状态存储设计

## 6.1 表结构（核心）

### tasks
- id (TEXT, PK)
- task_type (TEXT)
- route_target (TEXT: local/github_actions/cloud_run)
- status (TEXT)
- priority (INTEGER)
- payload_json (TEXT)
- retry_count (INTEGER)
- max_retries (INTEGER)
- created_at (INTEGER)
- updated_at (INTEGER)

### executions
- id (TEXT, PK)
- task_id (TEXT, FK)
- backend (TEXT)
- backend_ref (TEXT)  // run_id / job_id
- started_at (INTEGER)
- finished_at (INTEGER)
- exit_code (INTEGER)
- log_summary (TEXT)

### events
- id (INTEGER, PK AUTOINCREMENT)
- task_id (TEXT)
- level (TEXT)
- message (TEXT)
- ts (INTEGER)

## 6.2 SQLite 参数建议
- `PRAGMA journal_mode=WAL;`
- `PRAGMA synchronous=NORMAL;`
- `PRAGMA temp_store=MEMORY;`
- `PRAGMA busy_timeout=3000;`

说明：在低资源设备上，WAL + 合理超时可提高稳定性。

---

## 7. 关键运行策略

## 7.1 CPU 与并发控制
- 本地 worker 并发固定为 1
- 调度扫描间隔 1~3 秒，不做高频轮询
- 回收器轮询云任务状态间隔 10~20 秒

## 7.2 内存保护
- 任务提交时执行静态资源评估
- 本地执行前二次校验（超过阈值直接改派云端）
- 队列长度保护：本地待执行队列上限 20

## 7.3 磁盘保护（3.4GB 可用）
- SQLite 文件目标 < 300MB
- 日志只保留摘要，完整日志保留在 GitHub Actions
- 自动清理策略：保留 7~14 天任务明细

---

## 8. 安全与凭据管理（轻量版）

- GitHub Token、Cloud Run 凭据通过环境变量注入
- 本地仅保存最小必要配置，不落盘明文密钥
- 回调接口使用 HMAC 签名校验
- API 可选启用简单 token 鉴权（Header: `Authorization: Bearer ...`）

---

## 9. 部署方案（无 Docker）

## 9.1 运行依赖
- Python 3.11+
- Flask
- requests
- sqlite3（Python 内置）

## 9.2 启动方式
- 推荐：`systemd` 守护进程
- 备选：`nohup` + 日志重定向

示例命令：
```bash
python -m venv .venv
source .venv/bin/activate
pip install flask requests
python root_node.py
```

## 9.3 systemd（建议）
- 自动重启：`Restart=always`
- 内存保护：`MemoryMax=150M`（保护上限，不等于常态）
- 文件句柄限制：`LimitNOFILE=4096`

---

## 10. 从原架构迁移（删减清单）

## 10.1 删除组件
- Nomad Server/Client
- Consul
- Kestra
- PostgreSQL
- Docker/Compose 运行路径（根节点侧）

## 10.2 保留并重写
- Execution Gateway -> Python 轻量路由器
- Task API -> Flask 统一入口
- 状态管理 -> SQLite 单文件数据库

## 10.3 兼容策略
- 保留任务 ID 与基础状态字段语义
- 旧任务类型映射到新路由策略（local/github_actions/cloud_run）

---

## 11. 可落地实施计划（建议 4 阶段）

### Phase A（0.5天）
- 建立 Flask + SQLite 最小骨架
- 完成任务提交/查询 API

### Phase B（1天）
- 实现 Scheduler + Dispatcher + Local Worker
- 打通本地轻任务闭环

### Phase C（1天）
- 接入 GitHub Actions workflow_dispatch
- 完成 run_id 追踪与状态回写

### Phase D（0.5天）
- 加入清理策略、重试机制、基本鉴权
- systemd 部署与资源压测

---

## 12. 验收标准

### 功能验收
- 可提交任务并返回 task_id
- 轻任务可在本地完成
- 重任务可自动转发到 GitHub Actions
- 可查询完整状态流转

### 性能验收
- 根节点空闲内存 < 80MB
- 根节点峰值内存 < 100MB（常规负载）
- API P95 响应 < 200ms（本地查询接口）

### 稳定性验收
- 连续运行 72 小时无崩溃
- 云端偶发失败可自动重试并收敛
- SQLite 无锁死、无明显膨胀失控

---

## 13. 最终结论

该重构方案将系统从“重编排平台”调整为“轻协调根节点 + 云执行后端”模式：
- 在 1核/921MB/无Docker 的设备上可落地运行
- 根节点专注控制平面，资源占用可控
- 重计算与复杂依赖外移到 GitHub Actions/Cloud Run
- 显著降低部署与维护复杂度，同时保留分布式执行能力

这是当前硬件条件下最稳妥、可维护、可持续演进的最小架构方案。
