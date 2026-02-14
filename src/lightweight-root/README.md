# Lightweight Root Node

轻量化分布式AI助手根节点

## 特性

- **极简设计**：内存占用 < 50MB
- **无需Docker**：纯Python实现
- **多云支持**：Oracle Cloud、GitHub Actions、Cloud Run
- **适合小型设备**：1核/921MB即可运行

## 安装

```bash
pip install -r requirements.txt
```

## 配置

创建 `config.json`:

```json
{
  "oracle_cloud": {
    "compartment_id": "ocid1.compartment...",
    "ocir_repository": "namespace/repo",
    "subnet_id": "ocid1.subnet...",
    "region": "us-ashburn-1"
  },
  "github_actions": {
    "repository": "owner/repo",
    "workflow": "worker.yml",
    "token": "ghp_...",
    "ref": "main"
  }
}
```

或使用环境变量。

## 运行

```bash
python main.py
```

## API

### 创建任务
```bash
curl -X POST http://localhost:5000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type": "inference", "payload": {"model": "gpt-4"}, "backend": "oracle_cloud"}'
```

### 查询状态
```bash
curl http://localhost:5000/jobs/<job_id>
```

### 获取结果
```bash
curl http://localhost:5000/jobs/<job_id>/result
```

## 架构

- `main.py` - 主程序入口
- `api.py` - Flask REST API
- `scheduler.py` - 任务调度器
- `db.py` - SQLite数据库
- `config.py` - 配置管理
- `backends/` - 云平台适配器
  - `base.py` - 基类
  - `oracle_cloud.py` - Oracle Cloud
  - `github_actions.py` - GitHub Actions
  - `cloud_run.py` - Google Cloud Run
