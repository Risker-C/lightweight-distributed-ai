# Koyeb & Railway Docker镜像部署指南

**轻量化分布式AI助手 - Docker镜像部署完整教程**

---

## 📦 Docker镜像信息

- **镜像名称**: `riskerc/lightweight-ai-worker`
- **最新版本**: `v1.0.0`
- **镜像大小**: ~150MB
- **内存占用**: 37.8MB（运行时）
- **端口**: 8080

---

## 🔨 步骤一：构建Docker镜像

### 1. 准备代码

```bash
git clone https://github.com/Risker-C/lightweight-distributed-ai.git
cd lightweight-distributed-ai/src/lightweight-root
```

### 2. 构建镜像

```bash
# 构建镜像
docker build -t riskerc/lightweight-ai-worker:latest \
             -t riskerc/lightweight-ai-worker:v1.0.0 .

# 查看镜像
docker images | grep lightweight-ai-worker
```

### 3. 推送到Docker Hub

```bash
# 登录Docker Hub
docker login

# 推送镜像
docker push riskerc/lightweight-ai-worker:latest
docker push riskerc/lightweight-ai-worker:v1.0.0
```

**镜像地址**: `docker.io/riskerc/lightweight-ai-worker:latest`

---

## 🚀 步骤二：Koyeb镜像部署（推荐）

### 优势
- ✅ 完全免费，无需信用卡
- ✅ Always-on，不会休眠
- ✅ 512MB内存
- ✅ 直接使用Docker镜像

### 部署步骤

#### 1. 注册Koyeb
- 访问: https://www.koyeb.com/
- 点击 Sign Up 注册
- 无需信用卡

#### 2. 创建服务

**Web控制台：**
1. 登录Koyeb → Create Service
2. 选择 **Docker**
3. 镜像地址: `docker.io/riskerc/lightweight-ai-worker:latest`
4. 环境变量:
   ```
   PORT=8080
   ROOT_NODE_URL=http://YOUR_IP:5000
   WORKER_NAME=koyeb-worker-1
   ```
5. 实例: Nano (512MB) - 免费
6. 区域: fra (法兰克福) 或 sin (新加坡)
7. 健康检查: `/health`
8. Deploy

**CLI方式：**
```bash
# 安装CLI
curl -fsSL https://cli.koyeb.com/install.sh | sh

# 登录
koyeb login

# 部署
koyeb service create lightweight-worker \
  --docker docker.io/riskerc/lightweight-ai-worker:latest \
  --ports 8080:http \
  --routes /:8080 \
  --env PORT=8080 \
  --env ROOT_NODE_URL=http://YOUR_IP:5000 \
  --instance-type nano \
  --regions fra \
  --checks http:8080:/health
```

#### 3. 验证

```bash
curl https://lightweight-worker-xxx.koyeb.app/health
```

---

## 🚂 步骤三：Railway镜像部署

### 部署步骤

#### 1. 注册Railway
- 访问: https://railway.app/
- GitHub登录
- 获得$5免费额度

#### 2. 创建项目

**Web控制台：**
1. New Project → Deploy Docker Image
2. 镜像: `docker.io/riskerc/lightweight-ai-worker:latest`
3. 环境变量:
   ```
   PORT=8080
   ROOT_NODE_URL=http://YOUR_IP:5000
   WORKER_NAME=railway-worker-1
   ```
4. Settings → Networking → Generate Domain

**CLI方式：**
```bash
npm install -g @railway/cli
railway login
railway init
railway up --image docker.io/riskerc/lightweight-ai-worker:latest
```

#### 3. 验证

```bash
curl https://your-project.railway.app/health
```

---

## 🌐 步骤四：配置根节点

### 1. 启动根节点

```bash
cd src/lightweight-root
pip install -r requirements.txt
python main.py
```

### 2. 配置Worker

创建 `config.json`:

```json
{
  "workers": [
    {
      "name": "koyeb-worker-1",
      "url": "https://lightweight-worker-xxx.koyeb.app",
      "platform": "koyeb"
    },
    {
      "name": "railway-worker-1",
      "url": "https://your-project.railway.app",
      "platform": "railway"
    }
  ]
}
```

### 3. 测试

```bash
# 提交任务
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{"type":"compute","payload":{"operation":"factorial","number":10000}}'

# 查看Worker
curl http://localhost:5000/api/workers
```

---

## 📊 平台对比

| 特性 | Koyeb | Railway |
|------|-------|---------|
| 免费额度 | 1个Web服务 | $5/月 |
| 内存 | 512MB | 按量计费 |
| 休眠 | Never | Never |
| 信用卡 | 不需要 | 不需要 |
| 存储 | 临时 | 支持Volume |

**推荐**: 单Worker用Koyeb，多Worker用Koyeb+Railway

---

## ⚠️ 注意事项

### 网络配置

本地根节点需要公网访问，使用内网穿透：

**Ngrok:**
```bash
ngrok http 5000
# 获得 https://abc123.ngrok.io
# 配置为 ROOT_NODE_URL
```

**Cloudflare Tunnel:**
```bash
cloudflared tunnel --url http://localhost:5000
```

### 环境变量

| 变量 | 必需 | 默认 | 说明 |
|------|------|------|------|
| PORT | 否 | 8080 | Worker端口 |
| ROOT_NODE_URL | 是 | - | 根节点地址 |
| WORKER_NAME | 否 | hostname | Worker名称 |

---

## 🎯 检查清单

- [ ] 构建Docker镜像
- [ ] 推送到Docker Hub
- [ ] 注册Koyeb/Railway
- [ ] 部署Worker
- [ ] 配置根节点
- [ ] 测试连接
- [ ] 提交任务
- [ ] 监控状态

---

## 🎉 成功标志

✅ Worker健康检查返回200
✅ 内存占用 < 50MB
✅ 根节点看到Worker在线
✅ 分布式任务成功执行

---

**相关资源:**
- 项目: https://github.com/Risker-C/lightweight-distributed-ai
- Koyeb: https://www.koyeb.com/docs
- Railway: https://docs.railway.app
