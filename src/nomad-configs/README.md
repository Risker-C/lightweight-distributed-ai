# Nomad 生产级集群配置

本目录提供完整的 Nomad 生产部署配置，包含：
- 3 节点 Server 高可用配置（Raft）
- Client 资源池（warm / batch / special）
- TLS 双向认证证书生成
- ACL 权限策略与初始化脚本
- 一键部署脚本

## 目录结构

```text
nomad-config/
├── server.hcl
├── client-warm.hcl
├── client-batch.hcl
├── client-special.hcl
├── deploy.sh
├── acl-policies/
│   ├── anonymous.hcl
│   ├── readonly.hcl
│   ├── deployer.hcl
│   ├── ops-admin.hcl
│   └── bootstrap-acl.sh
└── tls/
    └── generate-certs.sh
```

## 部署前准备

1. 安装 Nomad（建议 1.6+）
2. 每台机器配置时间同步（NTP）
3. 开放端口：
   - `4646` HTTP API
   - `4647` RPC
   - `4648` Serf
4. 根据实际环境修改以下字段：
   - 所有配置中的 `name`
   - `advertise` 网卡名（默认 `eth0`）
   - Server/Client 的 `servers` 或 `retry_join` IP 列表

## 1) Server（3节点 HA）

在 3 台 Server 机器分别部署（每台 `name` 唯一）：

```bash
cd /root/.openclaw/workspace/nomad-config
bash deploy.sh server
```

> `server.hcl` 中 `bootstrap_expect = 3`，确保 3 台都启动后完成选主。

## 2) Client 资源池部署

### Warm 池（长稳态服务）

```bash
bash deploy.sh client-warm
```

### Batch 池（离线/短作业）

```bash
bash deploy.sh client-batch
```

### Special 池（关键任务/高优先级）

```bash
bash deploy.sh client-special
```

## 3) TLS 配置说明

证书由 `tls/generate-certs.sh` 生成，默认输出在 `tls/` 目录。

手动生成：

```bash
bash tls/generate-certs.sh tls
```

生产建议：
- 将 `SERVER_SANS` 包含全部 Server IP/域名
- CA 私钥离线保存
- 证书定期轮换（例如 6~12 个月）

示例：

```bash
SERVER_SANS="DNS:nomad.service.consul,IP:10.10.10.11,IP:10.10.10.12,IP:10.10.10.13" \
bash tls/generate-certs.sh tls
```

## 4) ACL 初始化

在首台 Server 执行：

```bash
export NOMAD_ADDR=https://127.0.0.1:4646
export NOMAD_CACERT=/etc/nomad.d/tls/nomad-agent-ca.pem
export NOMAD_CLIENT_CERT=/etc/nomad.d/tls/cli.pem
export NOMAD_CLIENT_KEY=/etc/nomad.d/tls/cli-key.pem

nomad acl bootstrap
# 记下 Secret ID
export NOMAD_TOKEN=<bootstrap_secret_id>

bash /etc/nomad.d/acl-policies/bootstrap-acl.sh
```

策略说明：
- `anonymous.hcl`：匿名最小可观测权限
- `readonly.hcl`：只读审计
- `deployer.hcl`：CI/CD 发布权限
- `ops-admin.hcl`：运维管理员权限

## 5) 资源池与调度策略

通过 `node_class` + `meta.pool` 实现池化：
- `warm`：在线服务（稳定优先）
- `batch`：离线任务（吞吐优先）
- `special`：关键任务（优先级最高）

作业约束示例（投递到 warm 池）：

```hcl
constraint {
  attribute = "${meta.pool}"
  value     = "warm"
}
```

关键业务建议：
- 提升 `priority`（例如 `80~100`）
- 使用 `spread` 按 `node.datacenter`/`node.unique.id` 分散副本
- 搭配 `update` 的分批发布与健康检查

## 6) 重试与恢复策略

已在集群配置中体现：
- Server `server_join.retry_join` + `retry_interval`
- Server `rejoin_after_leave = true`
- Client 各池独立 GC 与 `max_kill_timeout`

建议在 Job 规范中同时启用：

```hcl
restart {
  attempts = 5
  interval = "30m"
  delay    = "15s"
  mode     = "delay"
}

reschedule {
  attempts      = 10
  interval      = "1h"
  delay         = "30s"
  delay_function = "exponential"
  max_delay     = "10m"
  unlimited     = false
}
```

## 7) 常见检查

```bash
nomad server members
nomad node status
nomad acl policy list
nomad status
```

如果 API 连接失败，优先检查：
1. 证书 SAN 是否包含访问地址
2. 防火墙与安全组端口是否放通
3. `advertise` 网卡名是否正确
4. 节点时间是否同步
