# 第2章代码示例：Apache Doris 安装与环境配置

本章包含Apache Doris安装与环境配置相关的代码示例和配置文件，帮助读者快速搭建Doris环境。

## 📁 文件结构

```
chapter2/
├── README.md                    # 本文件，章节代码说明
├── docker/                      # Docker部署示例
│   ├── docker-compose.yml       # Docker Compose部署配置
│   ├── single-node/             # 单节点Docker部署
│   │   └── docker-compose.yml   # 单节点配置
│   └── ha-cluster/              # 高可用集群部署
│       └── docker-compose.yml   # 高可用集群配置
├── binary/                      # 二进制部署示例
│   ├── fe.conf                  # FE配置文件
│   ├── be.conf                  # BE配置文件
│   ├── install.sh               # 安装脚本
│   └── start-cluster.sh         # 集群启动脚本
├── ha-cluster/                  # 高可用集群部署
│   ├── fe1.conf                 # FE1配置
│   ├── fe2.conf                 # FE2配置
│   ├── fe3.conf                 # FE3配置
│   ├── be1.conf                 # BE1配置
│   ├── be2.conf                 # BE2配置
│   ├── be3.conf                 # BE3配置
│   └── deploy.sh                # 部署脚本
├── nginx/                       # 负载均衡配置
│   └── nginx.conf               # Nginx配置文件
└── monitoring/                  # 监控配置
    ├── prometheus.yml           # Prometheus配置
    └── grafana/                 # Grafana仪表盘
        └── doris-dashboard.json # Doris监控仪表盘
```

## 🚀 快速开始

### 1. Docker单节点部署

```bash
# 进入docker/single-node目录
cd docker/single-node

# 启动Doris集群
docker-compose up -d

# 查看服务状态
docker-compose ps

# 连接Doris
mysql -h 127.0.0.1 -P 9030 -uroot
```

### 2. 二进制部署

```bash
# 进入binary目录
cd binary

# 修改配置文件（根据实际环境调整IP等参数）
vim fe.conf
vim be.conf

# 执行安装脚本
chmod +x install.sh
./install.sh

# 启动集群
chmod +x start-cluster.sh
./start-cluster.sh
```

### 3. 高可用集群部署

```bash
# 进入ha-cluster目录
cd ha-cluster

# 修改配置文件（根据实际环境调整IP等参数）
vim fe1.conf
vim fe2.conf
vim fe3.conf
vim be1.conf
vim be2.conf
vim be3.conf

# 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

## 📝 代码说明

### Docker部署

`docker/` 目录包含Docker部署相关的配置文件：

1. **单节点部署** (`docker/single-node/`)
   - 1个FE节点和1个BE节点的最小化部署
   - 适合快速体验和开发测试

2. **高可用集群部署** (`docker/ha-cluster/`)
   - 3个FE节点和3个BE节点的高可用部署
   - 包含Nginx负载均衡配置

### 二进制部署

`binary/` 目录包含二进制部署所需的配置和脚本：

1. **配置文件**
   - `fe.conf`：FE节点配置
   - `be.conf`：BE节点配置

2. **部署脚本**
   - `install.sh`：自动化安装脚本
   - `start-cluster.sh`：集群启动脚本

### 高可用集群

`ha-cluster/` 目录包含高可用集群的详细配置：

1. **FE配置**
   - `fe1.conf`：第一个FE节点配置
   - `fe2.conf`：第二个FE节点配置
   - `fe3.conf`：第三个FE节点配置

2. **BE配置**
   - `be1.conf`：第一个BE节点配置
   - `be2.conf`：第二个BE节点配置
   - `be3.conf`：第三个BE节点配置

3. **部署脚本**
   - `deploy.sh`：高可用集群部署脚本

### 负载均衡

`nginx/` 目录包含Nginx负载均衡配置：

- `nginx.conf`：Nginx配置文件，配置FE节点的负载均衡

### 监控配置

`monitoring/` 目录包含监控相关的配置：

1. **Prometheus配置**
   - `prometheus.yml`：Prometheus配置文件

2. **Grafana仪表盘**
   - `grafana/doris-dashboard.json`：Doris监控仪表盘配置

## 🔧 环境要求

- Docker 20.0+
- Docker Compose 2.0+
- MySQL客户端 5.7+
- Linux系统（CentOS 7.x/8.x、Ubuntu 18.04/20.04）
- JDK 1.8+

## 📖 学习建议

1. 先尝试Docker单节点部署，快速体验Doris
2. 然后尝试二进制部署，了解Doris的组件结构
3. 最后尝试高可用集群部署，掌握生产环境部署方法
4. 配置监控系统，了解Doris的运行状态
5. 结合章节文档，理解每个配置项的作用

## ❓ 常见问题

### Q: Docker启动失败怎么办？
A: 检查端口是否被占用，确保Docker服务正常运行。

### Q: 二进制部署时FE启动失败？
A: 检查Java环境是否正确配置，检查元数据目录权限。

### Q: 高可用集群中FE节点无法加入集群？
A: 检查网络连通性，确认FE配置中的helper参数正确。

### Q: BE节点状态为dead？
A: 检查BE进程状态，查看BE日志，确认与FE的网络连通性。

---

> 返回章节文档：[第2章：Apache Doris 安装与环境配置](../../2-安装与环境配置.md)