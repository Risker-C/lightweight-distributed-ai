# Docker镜像构建配置说明

## ⚠️ 需要配置GitHub Secrets

GitHub Actions需要Docker Hub的登录凭证才能推送镜像。

### 配置步骤：

1. **访问GitHub仓库设置**
   - 打开：https://github.com/Risker-C/lightweight-distributed-ai/settings/secrets/actions
   
2. **添加两个Secrets**
   
   点击 "New repository secret"，添加：
   
   **Secret 1:**
   - Name: `DOCKER_USERNAME`
   - Value: 您的Docker Hub用户名（如 `riskerc`）
   
   **Secret 2:**
   - Name: `DOCKER_PASSWORD`
   - Value: 您的Docker Hub密码或Access Token（推荐使用Token）

3. **获取Docker Hub Access Token（推荐）**
   - 访问：https://hub.docker.com/settings/security
   - 点击 "New Access Token"
   - 描述：GitHub Actions
   - 权限：Read, Write, Delete
   - 生成后复制Token（只显示一次！）
   - 将Token作为 `DOCKER_PASSWORD` 的值

4. **重新运行GitHub Actions**
   - 访问：https://github.com/Risker-C/lightweight-distributed-ai/actions
   - 找到失败的 "Build and Push Docker Image" 工作流
   - 点击 "Re-run all jobs"

---

## 🚀 配置完成后

GitHub Actions会自动：
1. 构建Docker镜像（支持amd64和arm64）
2. 推送到Docker Hub
3. 标记为 `latest` 和版本号

**镜像地址：** `docker.io/riskerc/lightweight-ai-worker:latest`

---

## 📦 手动构建（备选方案）

如果不想配置GitHub Actions，可以在本地构建：

```bash
cd /root/.openclaw/workspace/distributed-ai-assistant-project/src/lightweight-root

# 登录Docker Hub
docker login

# 构建镜像
docker build -t riskerc/lightweight-ai-worker:latest .

# 推送镜像
docker push riskerc/lightweight-ai-worker:latest
```

---

Master，请按照上述步骤配置GitHub Secrets，然后镜像就会自动构建并推送！🍉
