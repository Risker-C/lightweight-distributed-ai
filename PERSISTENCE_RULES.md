# 项目持久化配置

## 项目根目录
`/root/.openclaw/workspace/distributed-ai-assistant-project/`

## 自动持久化规则

所有开发产出必须保存到项目目录：

### 文档类
- 架构设计 → `docs/architecture/`
- 安全配置 → `docs/security/`
- 部署指南 → `docs/deployment/`
- API文档 → `docs/api/`

### 代码类
- Execution Gateway → `src/execution-gateway/`
- Nomad配置 → `src/nomad-configs/`
- Kestra集成 → `src/kestra-integration/`
- 监控系统 → `src/monitoring/`

### 配置类
- Nomad配置文件 → `config/nomad/`
- Kestra配置文件 → `config/kestra/`
- 安全配置 → `config/security/`
- 监控配置 → `config/monitoring/`

### 部署类
- Docker Compose → `deploy/docker-compose/`
- 部署脚本 → `deploy/scripts/`
- 基础设施代码 → `deploy/terraform/`

### 测试类
- 单元测试 → `tests/unit/`
- 集成测试 → `tests/integration/`
- 端到端测试 → `tests/e2e/`

### 日志类
- 开发日志 → `logs/development.log`
- 协调日志 → `logs/coordination.log`
- 进度日志 → `logs/progress.log`

## 专业Agents产出规则

每个专业agent必须：
1. 将所有产出保存到对应目录
2. 创建README.md说明文档
3. 完成后更新进度日志
4. 关键里程碑立即报告

---
*创建时间：2026-02-14 13:31 GMT+8*
