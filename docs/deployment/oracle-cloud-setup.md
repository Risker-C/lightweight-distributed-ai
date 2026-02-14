# Oracle Cloud Always Free 申请与配置指南

## 1. Always Free 资源说明

Oracle Cloud Always Free（长期免费）常用资源：

- ARM 实例总额度：4 OCPU + 24 GB RAM（Ampere A1）
- Block Volume：200 GB
- 每月出站流量：10 TB

> 推荐用于 Worker：创建 2~4 台 ARM VM，每台 1 OCPU / 6 GB。

---

## 2. 申请账号（新用户）

### 2.1 准备材料

- 可用邮箱（建议 Gmail/企业邮箱）
- 手机号（短信验证）
- 可用信用卡（身份验证）

### 2.2 注册流程

1. 打开：<https://www.oracle.com/cloud/free/>
2. 点击 `Start for free`
3. 填写国家/姓名/邮箱/密码
4. 验证邮箱
5. 完成信用卡验证
6. 登录 OCI Console

### 2.3 常见审核问题

- 地址信息必须真实、完整
- 同一人/卡多次注册容易触发风控
- 建议使用稳定网络环境提交

---

## 3. 创建 ARM 实例（Worker 主机）

### 3.1 建议规划

- `ai-worker-1`：1 OCPU / 6 GB
- `ai-worker-2`：1 OCPU / 6 GB
- `ai-worker-3`：1 OCPU / 6 GB
- `ai-worker-4`：1 OCPU / 6 GB（可选）

### 3.2 创建步骤

1. OCI Console -> `Compute` -> `Instances` -> `Create instance`
2. Image 选择 Ubuntu 22.04
3. Shape 选择 `VM.Standard.A1.Flex`
4. 设置 OCPU=1、Memory=6GB
5. 网络选择 Public Subnet，分配公网 IP
6. 上传你的 SSH 公钥
7. 启动盘 40~50GB
8. 点击创建

### 3.3 SSH 连接

```bash
chmod 400 ~/.ssh/oracle_worker.key
ssh -i ~/.ssh/oracle_worker.key ubuntu@<public-ip>
```

---

## 4. 网络与安全配置

## 4.1 安全列表（Security List）放行

至少放行端口：

- `22/tcp`：SSH
- `80/tcp`：HTTP（可选）
- `443/tcp`：HTTPS（可选）
- `8000/tcp`：Coolify 控制台（可改）
- `3001/tcp`：Worker API

> 建议把来源地址限制为你的固定 IP 或根节点 IP，避免 `0.0.0.0/0` 全开放。

### 4.2 实例内防火墙（Ubuntu）

如果使用 UFW：

```bash
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3001/tcp
sudo ufw enable
sudo ufw status
```

---

## 5. 实例初始化建议

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git unzip jq ca-certificates
```

配置时区：

```bash
sudo timedatectl set-timezone Asia/Shanghai
```

---

## 6. 容量与区域问题处理

### 6.1 Out of capacity

Oracle 免费 ARM 在部分区域经常紧张，建议：

- 更换 Region（如东京/首尔/新加坡）
- 更换 AD（Availability Domain）
- 错峰重试（整点前后）

### 6.2 先用少量实例上线

可以先 2 台 Worker 启动，再逐步扩容到 3~4 台。

---

## 7. 运维建议

- 为每个实例记录：公网 IP、私网 IP、用途、密钥路径
- 不要复用 root 账户，统一使用 `ubuntu` + SSH Key
- 定期更新系统补丁
- 打开 OCI 监控告警（CPU、内存、网络）

---

## 8. 验证清单

- [ ] 能 SSH 连接每台 VM
- [ ] 安全列表已放行 8000/3001（按需）
- [ ] UFW/iptables 未拦截业务端口
- [ ] 每台实例可执行 `curl` / `docker` 命令

---

## 9. 下一步

完成云主机准备后，继续：

- Coolify 部署：`coolify-setup.md`
- Worker 镜像制作：`docker-worker-guide.md`
- 根节点与 E2E：`LIGHTWEIGHT_DEPLOYMENT_GUIDE.md`
