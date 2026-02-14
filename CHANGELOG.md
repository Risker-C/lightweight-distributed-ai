# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-14

### Added

#### Core Features
- Lightweight root node implementation (Python + Flask + SQLite)
- Multi-cloud backend adapters (Oracle Cloud, GitHub Actions, Cloud Run)
- REST API for job management
- Automatic task scheduler
- SQLite-based state management

#### Documentation
- Complete deployment guides
- Architecture discussion documents
- Cloud platform research report
- Quick start guide
- Production deployment guide
- Oracle Cloud setup guide
- Coolify deployment guide
- Docker worker guide

#### Deployment
- systemd service configuration
- Configuration examples (.env and JSON)
- Docker examples
- GitHub Actions workflow examples

#### Testing
- Local deployment tests
- API functionality verification
- Performance benchmarks

### Performance
- Memory usage: 37.8MB (target: <50MB) ✅
- CPU usage: 1.3% (idle)
- Startup time: ~2 seconds
- API response: <500ms

### Highlights
- Works on 1 core / 921MB devices
- No Docker required for root node
- Complete free cloud resources utilization
- Production-ready configuration

---

## Project Timeline

- **2026-02-14 13:21**: Project kickoff
- **2026-02-14 14:35**: Phase 1 complete (heavy architecture)
- **2026-02-14 15:32**: Architecture refactoring started
- **2026-02-14 18:17**: Lightweight implementation complete
- **2026-02-14 18:41**: Local deployment tested
- **2026-02-14 19:48**: GitHub repository published

Total development time: ~5 hours
