# Lightweight Distributed AI Assistant

轻量化分布式AI助手架构 - 适合小型设备运行的分布式计算系统

## 特性

- **极简本地根节点**：内存占用 < 50MB（实测37.8MB）
- **无需Docker**：纯Python实现
- **多云支持**：Oracle Cloud、GitHub Actions、Google Cloud Run
- **适合小型设备**：1核/921MB即可运行
- **完全免费**：充分利用免费云资源

## 快速开始

### 本地运行

```bash
cd src/lightweight-root
pip3 install -r requirements.txt
python3 main.py
```

### 测试API

```bash
curl -X POST http://localhost:5000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"test","payload":{"message":"hello"}}'
```

## 架构

- **本地根节点**：Python + Flask + SQLite
- **云端从节点**：Docker容器（Oracle Cloud/GitHub Actions/Cloud Run）
- **统一接口**：抽象适配器模式

## 文档

- [快速启动](src/lightweight-root/QUICKSTART.md)
- [生产部署](docs/deployment/PRODUCTION_DEPLOYMENT.md)
- [架构设计](docs/architecture/)
- [云平台调研](research/free-cloud-platforms.md)

## 性能指标

- 内存占用：37.8MB
- CPU占用：1.3%（空闲）
- 启动时间：~2秒
- API响应：< 500ms

## 许可证

MIT License

## 项目状态

✅ 完成并测试通过

---

**从单机助手到分布式协作系统的进化** 🍉
