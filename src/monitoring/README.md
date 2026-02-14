# Nomad + Kestra + Gateway 生产级监控体系

本目录提供一套可直接落地的监控栈：
- 指标采集：Prometheus
- 可视化：Grafana
- 告警路由：Alertmanager
- 基础指标：Node Exporter + cAdvisor
- Nomad指标：Nomad原生指标 + Nomad Exporter

所有配置均位于当前目录，可一键部署、备份、恢复。

## 目录结构

```text
monitoring/
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml
│   ├── rules/
│   └── targets/
├── grafana/
│   ├── dashboards/
│   ├── datasources/
│   └── provisioning/
├── alertmanager/
│   ├── alertmanager.yml
│   └── templates/
├── exporters/
│   ├── nomad-exporter.yml
│   └── node-exporter.yml
├── scripts/
│   ├── deploy.sh
│   └── backup.sh
└── README.md
```

## 监控覆盖说明

### 1) Nomad 集群健康状态
- `up{job="nomad"}`：Nomad端点可用性
- `nomad_nomad_raft_leader`：Leader是否存在
- `nomad_nomad_blocked_evals`：调度阻塞评估
- `nomad:alloc_failed_rate_5m`：任务分配失败速率

### 2) 任务执行成功率
- Nomad：`nomad:task_success_rate_15m`
- Kestra：`kestra:workflow_success_rate_15m`

### 3) 资源使用情况
- 主机CPU/内存/磁盘：Node Exporter
- 容器资源：cAdvisor

### 4) Gateway API 延迟
- `gateway:request_p95_seconds`（P95）
- `gateway:error_rate_5m`（5xx错误率）

### 5) Kestra 工作流状态
- `kestra_execution_total{state=...}`
- `kestra:workflow_failure_rate_15m`
- `kestra_queue_size` / `kestra_executor_queued_tasks`

## 部署步骤

1. 进入目录：
```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project/src/monitoring
```

2. 修改抓取目标（按你实际地址）：
- `prometheus/targets/nomad.yml`
- `prometheus/targets/gateway.yml`
- `prometheus/targets/kestra.yml`
- `prometheus/targets/nodes.yml`

3. 启动：
```bash
./scripts/deploy.sh
```

4. 访问：
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- Grafana: `http://localhost:3000`（默认 `admin / admin123!`）

## 告警配置

- 主配置：`alertmanager/alertmanager.yml`
- 模板：`alertmanager/templates/default.tmpl`
- 规则：`prometheus/rules/*.yml`

默认将告警发往：
- `http://host.docker.internal:5001/alerts`
- `http://host.docker.internal:5001/alerts/critical`

如需接入企业微信/飞书/Slack/PagerDuty，请修改 Alertmanager receiver。

## 备份

执行：
```bash
./scripts/backup.sh
```

默认行为：
- 打包所有配置文件
- 导出 compose 最终配置
- 备份 `prometheus-data` / `grafana-data` / `alertmanager-data` 数据卷
- 默认保留 14 天（可设置 `KEEP_DAYS`）

示例：
```bash
KEEP_DAYS=30 ./scripts/backup.sh /data/monitoring-backups
```

## 生产建议

- 将 Grafana 默认密码改为强密码
- 将 Alertmanager webhook 切换到真实告警通道
- 给 Prometheus 增加远程存储（如 Thanos/Mimir/VictoriaMetrics）
- 给关键告警配置值班策略与升级链路
- 在 Nomad/Kestra/Gateway 启用统一 `env/cluster/service` 标签，便于跨系统排障
