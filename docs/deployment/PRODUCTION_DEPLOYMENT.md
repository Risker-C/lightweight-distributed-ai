# 生产部署完整指南

## 系统要求

- Linux系统
- Python 3.8+
- systemd（用于服务管理）
- 最低1核CPU、512MB内存

---

## 部署步骤

### 1. 准备环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install -y python3 python3-pip

# 安装依赖
cd /root/.openclaw/workspace/distributed-ai-assistant-project/src/lightweight-root
pip3 install -r requirements.txt
```

### 2. 配置服务

#### 创建配置文件

```bash
# 复制示例配置
cp config.example.json config.json

# 编辑配置
nano config.json
```

**需要配置的项目**：
- GitHub仓库和Token
- Oracle Cloud凭证（可选）
- Cloud Run项目（可选）

#### 安装systemd服务

```bash
# 复制服务文件
sudo cp ../../deployment/lightweight-root.service /etc/systemd/system/

# 重载systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable lightweight-root

# 启动服务
sudo systemctl start lightweight-root
```

### 3. 验证部署

```bash
# 检查服务状态
sudo systemctl status lightweight-root

# 查看日志
sudo journalctl -u lightweight-root -f

# 测试API
curl http://localhost:5000/jobs -X POST \
  -H "Content-Type: application/json" \
  -d '{"type":"test"}'
```

---

## 配置GitHub Actions

### 1. 创建GitHub仓库

```bash
# 在GitHub上创建新仓库
# 例如：your-username/ai-worker
```

### 2. 添加Workflow

```bash
# 在仓库中创建.github/workflows/worker.yml
# 内容参考：examples/github-workflow-example.yml
```

### 3. 生成Token

1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 创建新token，权限：`repo`, `workflow`
3. 复制token到配置文件

### 4. 测试

```bash
# 提交任务
curl -X POST http://localhost:5000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "github_test",
    "backend": "github_actions",
    "payload": {"message": "test"}
  }'

# 查询状态
curl http://localhost:5000/jobs/<job_id>
```

---

## 配置Oracle Cloud（可选）

### 1. 注册账号

访问：https://www.oracle.com/cloud/free/

### 2. 创建资源

1. 创建Compartment
2. 创建VCN和Subnet
3. 配置安全规则

### 3. 获取配置信息

- Compartment OCID
- Subnet OCID
- Region
- OCIR Repository

### 4. 配置CLI

```bash
# 安装OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# 配置
oci setup config
```

---

## 监控和维护

### 查看日志

```bash
# 实时日志
sudo journalctl -u lightweight-root -f

# 最近日志
sudo journalctl -u lightweight-root -n 100

# 错误日志
sudo journalctl -u lightweight-root -p err
```

### 重启服务

```bash
sudo systemctl restart lightweight-root
```

### 停止服务

```bash
sudo systemctl stop lightweight-root
```

### 更新代码

```bash
# 停止服务
sudo systemctl stop lightweight-root

# 更新代码
cd /root/.openclaw/workspace/distributed-ai-assistant-project/src/lightweight-root
git pull  # 如果使用git

# 重启服务
sudo systemctl start lightweight-root
```

---

## 故障排查

### 服务无法启动

```bash
# 检查日志
sudo journalctl -u lightweight-root -n 50

# 检查配置
python3 -c "from config import load_config; print(load_config())"
```

### API无响应

```bash
# 检查端口
sudo netstat -tlnp | grep 5000

# 检查进程
ps aux | grep main.py
```

### 内存不足

```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head
```

---

## 安全建议

1. **使用防火墙**
```bash
sudo ufw allow 5000/tcp
sudo ufw enable
```

2. **定期更新**
```bash
sudo apt update && sudo apt upgrade -y
```

3. **备份配置**
```bash
cp config.json config.json.backup
```

4. **日志轮转**
```bash
# systemd自动处理日志轮转
# 可配置保留时间
sudo journalctl --vacuum-time=7d
```

---

**部署完成后，系统将在后台持续运行，自动处理任务调度和云端分发。**
