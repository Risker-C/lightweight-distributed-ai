# 部署测试环境检查报告

- 检查时间：2026-02-14 14:28:31 CST (+0800)
- 主机：`ryder`
- 目的：验证部署测试所需基础环境（Docker、系统资源、网络、端口）

## 1) Docker 检查

### 结果
- Docker **未安装**（`docker`/`dockerd` 命令不存在）
- Docker 服务单元不存在（`docker.service` not found）

### 关键输出
```bash
$ docker --version
/bin/sh: 3: docker: not found

$ docker info
/bin/sh: 6: docker: not found

$ command -v docker
# (无输出)

$ command -v dockerd
# (无输出)

$ systemctl status docker --no-pager -l
Unit docker.service could not be found.
```

## 2) 系统资源检查

### CPU
```bash
$ nproc
1
```
- 可用 CPU 核心数：**1 核**

### 内存
```bash
$ free -h
               total        used        free      shared  buff/cache   available
Mem:           921Mi       592Mi        74Mi       0.0Ki       254Mi       175Mi
Swap:          2.5Gi       359Mi       2.1Gi
```
- 物理内存总量：**921Mi**
- 当前可用内存：**175Mi**（偏低）
- 已启用交换分区：**2.5Gi**

### 磁盘
```bash
$ df -h
Filesystem      Size  Used Avail Use% Mounted on
tmpfs            93M  1.1M   92M   2% /run
/dev/sda1        20G   16G  3.4G  83% /
tmpfs           461M     0  461M   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      105M  6.1M   99M   6% /boot/efi
tmpfs            93M  4.0K   93M   1% /run/user/0
```
- 根分区 `/`：**20G 总量，已用 16G，剩余 3.4G（83%）**

## 3) 网络配置与连通性

### 基础网络配置
```bash
$ hostname -I
38.148.249.237

$ ip -brief addr
lo    UNKNOWN 127.0.0.1/8 ::1/128
ens3  UP      38.148.249.237/24 fe80::289:23ff:fecf:50da/64

$ ip route
default via 38.148.249.1 dev ens3 proto static
38.148.249.0/24 dev ens3 proto kernel scope link src 38.148.249.237
38.148.249.1 dev ens3 proto static scope link
```
- 网卡 `ens3` 状态：**UP**
- 默认网关：**38.148.249.1**

### DNS 与外网连通性
```bash
$ cat /etc/resolv.conf
nameserver 127.0.0.53
options edns0 trust-ad
search .

$ getent hosts www.baidu.com
103.235.46.115  www.wshifen.com www.baidu.com www.a.shifen.com
103.235.46.102  www.wshifen.com www.baidu.com www.a.shifen.com
```
- DNS 解析：**正常**

```bash
$ ping -c 2 -W 2 38.148.249.1
2 packets transmitted, 2 received, 0% packet loss

$ ping -c 2 -W 2 8.8.8.8
2 packets transmitted, 2 received, 0% packet loss

$ curl -I -m 8 https://www.baidu.com
HTTP/1.1 200 OK

$ curl -I -m 8 https://example.com
HTTP/2 200
```
- 网关连通：**正常**
- 公网 IP 连通：**正常**
- HTTPS 出口访问：**正常**

## 4) 必要端口占用检查

检查端口：`4646, 8500, 8080, 9090, 3000`

| 端口 | 状态 | 详情 |
|---|---|---|
| 4646 | 可用（FREE） | 无监听进程 |
| 8500 | 可用（FREE） | 无监听进程 |
| 8080 | 已占用（IN_USE） | `nginx` 正在监听 `0.0.0.0:8080` |
| 9090 | 可用（FREE） | 无监听进程 |
| 3000 | 可用（FREE） | 无监听进程 |

关键输出：
```bash
8080 IN_USE LISTEN 0 511 0.0.0.0:8080 0.0.0.0:* users:(("nginx",pid=835889,fd=12),("nginx",pid=835886,fd=12))
```

## 5) 结论与建议

### 总体结论
- 网络基础能力（路由、DNS、外网访问）正常。
- 目标端口中除 `8080` 外均可用。
- **当前环境不满足 Docker 部署测试前提**（Docker 未安装）。

### 风险提示
- 可用内存较低（`available=175Mi`），部署测试时可能出现 OOM 或性能瓶颈。
- 根分区使用率较高（83%），建议预留更多空间用于镜像、日志与构建缓存。

### 建议动作
1. 安装并启动 Docker（建议同时安装 Docker Compose 插件）。
2. 如测试服务需使用 `8080`，请先停用/迁移现有 `nginx` 监听或调整服务端口。
3. 在正式压测前，建议将可用内存与磁盘余量提升到更安全水平。
