# 快速启动指南

## 1. 安装依赖

```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project/src/lightweight-root
pip3 install -r requirements.txt
```

## 2. 配置

### 方式A：使用环境变量
```bash
cp .env.example .env
nano .env  # 编辑配置
```

### 方式B：使用配置文件
```bash
cp config.example.json config.json
nano config.json  # 编辑配置
```

## 3. 运行

### 开发模式
```bash
python3 main.py
```

### 生产模式（systemd）
```bash
# 复制服务文件
sudo cp ../../deployment/lightweight-root.service /etc/systemd/system/

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable lightweight-root
sudo systemctl start lightweight-root

# 查看状态
sudo systemctl status lightweight-root

# 查看日志
sudo journalctl -u lightweight-root -f
```

## 4. 测试

```bash
# 创建任务
curl -X POST http://localhost:5000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"test","payload":{"message":"hello"}}'

# 查询任务
curl http://localhost:5000/jobs/<job_id>
```

## 5. 停止服务

```bash
sudo systemctl stop lightweight-root
```

## 配置说明

### GitHub Actions
1. 在GitHub创建仓库
2. 添加workflow文件（.github/workflows/worker.yml）
3. 生成Personal Access Token
4. 填入配置

### Oracle Cloud
1. 注册Oracle Cloud Always Free账号
2. 创建Compartment
3. 配置VCN和Subnet
4. 获取OCID信息
5. 填入配置

详细配置请参考：`docs/deployment/`
