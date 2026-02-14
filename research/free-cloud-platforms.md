# 云平台深度调研报告

## 核心发现：Oracle Cloud Always Free 最适合！

### 🏆 推荐平台排序

#### 1. Oracle Cloud Always Free（强烈推荐）
- **免费额度**：永久免费
  - 2个AMD小VM
  - Arm Ampere（最高4 VM、24 GB内存）
  - 500 GB Docker容器镜像仓库
  - Kubernetes Engine 4500小时/月

- **Docker部署**：
  - 直接在VM安装Docker/Docker Compose
  - 支持Kubernetes部署
  - 可自建registry

- **API/CLI**：完整OCI CLI、Terraform、SDK

- **作为从节点可行性**：⭐⭐⭐⭐⭐ 极高
  - 完整root访问
  - 持久化存储
  - 支持Docker Swarm/K8s集群
  - 可长期稳定运行
  - 适合AI分布式任务

#### 2. Koyeb（良好）
- 免费：1个Web Service（0.1 vCPU、512 MB RAM）
- 无sleep，always-on
- 适合轻量级worker

#### 3. Fly.io（中等）
- 免费额度有限
- 全球边缘部署
- 持续运行可能超额

#### 4. Render（不推荐）
- 空闲15分钟后sleep
- 不适合always-on从节点

#### 5. Google Cloud Run（不适合）
- Serverless，scale-to-zero
- 不适合持久进程

---

## 💡 最佳方案

**Oracle VM + Coolify/CapRover**
- 在Oracle免费VM上部署自托管PaaS
- 完全免费、always-on、无sleep
- GUI + CLI管理Docker镜像
- 多个Oracle VM可组成集群
- 可行性：⭐⭐⭐⭐⭐ 极高

---

## 关键优势

### Oracle Cloud Always Free
1. **真正的永久免费**（非试用）
2. **完整VM控制**（非受限容器）
3. **支持集群部署**
4. **适合AI工作负载**
5. **全球多区域**

### 与其他平台对比
- Railway：无永久免费
- AWS/Azure：仅12个月试用
- Cloud Run：不适合长运行进程
- Oracle：永久免费 + 完整控制

---

*调研完成时间：2026-02-14 17:55 GMT+8*  
*数据来源：官方文档、GitHub Awesome列表、HostAdvice*
