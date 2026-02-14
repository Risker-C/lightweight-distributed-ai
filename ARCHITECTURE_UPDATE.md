# 架构更新 - 支持Docker镜像部署

## Master的重要指正

**核心观点**：
- 类似 Cloud Run 的平台提供免费资源
- 可通过Docker镜像部署服务
- **从节点应该支持Docker镜像部署**

## 架构调整

### 本地根节点（轻量化）
- 无需Docker
- Python + Flask + SQLite
- 内存 < 50MB

### 从节点（云端执行）
需要支持两种模式：

1. **Docker镜像部署模式**
   - Cloud Run
   - Railway
   - Fly.io
   - Render
   - 其他容器平台

2. **脚本执行模式**
   - GitHub Actions
   - 其他CI/CD平台

## 实施方案

从节点统一接口，支持：
- 提交Docker镜像任务
- 提交脚本任务
- 统一的状态查询
- 统一的结果获取

---

*更新时间：2026-02-14 17:39 GMT+8*
