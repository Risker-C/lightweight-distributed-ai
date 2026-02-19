# 快速部署指南 - 5分钟上手

## 🎯 最快部署路径（推荐Koyeb）

### 方式一：使用现成镜像（最快）

**1. 注册Koyeb（1分钟）**
- 打开 https://www.koyeb.com/
- 点击 Sign Up → 用GitHub登录
- 无需信用卡

**2. 部署镜像（2分钟）**
- 登录后点击 "Create Service"
- 选择 "Docker"
- 镜像地址填入：`docker.io/riskerc/lightweight-ai-worker:latest`
- 点击下一步

**3. 配置环境变量（1分钟）**
添加以下变量：
```
PORT=8080
ROOT_NODE_URL=http://YOUR_IP:5000
WORKER_NAME=koyeb-worker-1
```

**4. 选择配置（30秒）**
- Instance type: Nano (免费)
- Region: fra 或 sin
- Health check: /health
- 点击 Deploy

**5. 完成！**
- 等待1-2分钟部署完成
- 获取服务URL（如 https://xxx.koyeb.app）
- 测试：`curl https://xxx.koyeb.app/health`

---

## 🔧 方式二：自己构建镜像

**前提：有Docker环境**

```bash
# 1. Clone项目
git clone https://github.com/Risker-C/lightweight-distributed-ai.git
cd lightweight-distributed-ai

# 2. 构建镜像
cd src/lightweight-root
docker build -t YOUR_USERNAME/lightweight-worker:latest .

# 3. 推送到Docker Hub
docker login
docker push YOUR_USERNAME/lightweight-worker:latest

# 4. 在Koyeb部署
# 使用你自己的镜像地址：docker.io/YOUR_USERNAME/lightweight-worker:latest
```

---

## 🌐 配置本地根节点

**1. 如果本地没有公网IP，使用Ngrok：**
```bash
# 安装ngrok
brew install ngrok  # macOS
# 或从 https://ngrok.com/download 下载

# 启动
ngrok http 5000

# 获得URL（如 https://abc123.ngrok.io）
# 这个URL就是 ROOT_NODE_URL
```

**2. 启动根节点：**
```bash
cd src/lightweight-root
pip install -r requirements.txt
python main.py
```

**3. 测试连接：**
```bash
# 查看Worker状态
curl http://localhost:5000/api/workers

# 提交测试任务
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{"type":"compute","payload":{"number":100}}'
```

---

## ⚡ 一键部署脚本

我已经为您准备了自动化脚本：

**构建镜像：**
```bash
chmod +x scripts/build-and-push.sh
./scripts/build-and-push.sh
```

**部署到Koyeb：**
```bash
chmod +x scripts/deploy-koyeb.sh
./scripts/deploy-koyeb.sh
```

**部署到Railway：**
```bash
chmod +x scripts/deploy-railway.sh
./scripts/deploy-railway.sh
```

---

## 📊 成功标志

✅ Worker健康检查返回200  
✅ 内存占用 < 50MB  
✅ 根节点显示Worker在线  
✅ 测试任务成功执行  

---

## 🆘 遇到问题？

**Worker无法连接根节点：**
- 检查ROOT_NODE_URL是否正确
- 确保根节点有公网访问（用ngrok）
- 检查防火墙是否开放5000端口

**健康检查失败：**
- 等待1-2分钟，镜像可能还在启动
- 查看日志：`koyeb service logs lightweight-worker`

**内存不足：**
- 我们的Worker只需37.8MB，512MB完全足够
- 如果真的超了，检查是否有内存泄漏

---

Master，这是最精简的部署指南！您现在可以：

1. **立即部署**：直接用现成镜像 `docker.io/riskerc/lightweight-ai-worker:latest`
2. **或者等我**：我可以帮您一步步完成部署

您想现在就开始部署吗？🍉
