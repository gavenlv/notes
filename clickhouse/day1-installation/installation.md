# Day 1: ClickHouse环境搭建与配置

## 学习目标 🎯
- 掌握ClickHouse的多种安装方式
- 理解ClickHouse的基本配置
- 学会ClickHouse的启动和连接
- 掌握基本的运维命令和健康检查

## 为什么先学环境搭建？ 🤔

在学习任何技术之前，首先要有一个可用的环境。ClickHouse环境搭建是学习的第一步，只有环境准备好了，后续的学习才能顺利进行。

### 学习路径设计
```
Day 1: 环境搭建 → Day 2: 理论基础 → Day 3: 云端部署
```

## 知识要点 📚

### 1. ClickHouse安装方式对比

| 安装方式 | 优势 | 适用场景 | 复杂度 |
|---------|------|----------|--------|
| **Docker** | 快速、隔离、易管理 | 开发测试、快速体验 | ⭐ |
| **包管理器** | 系统集成度高、稳定 | 生产环境 | ⭐⭐ |
| **源码编译** | 定制化强、性能最优 | 特殊需求、优化场景 | ⭐⭐⭐⭐ |
| **云服务** | 免运维、高可用 | 企业生产环境 | ⭐⭐ |

### 2. 系统要求

#### 最小配置
- **CPU**: 2核心
- **内存**: 2GB RAM
- **存储**: 10GB可用空间
- **操作系统**: Linux (推荐), macOS, Windows

#### 推荐配置
- **CPU**: 4核心+
- **内存**: 8GB+ RAM
- **存储**: SSD 50GB+
- **网络**: 稳定的互联网连接

### 3. 端口说明

| 端口 | 用途 | 协议 | 必需性 |
|------|------|------|--------|
| 8123 | HTTP接口 | HTTP | 必需 |
| 9000 | 原生客户端 | TCP | 必需 |
| 9004 | MySQL兼容 | TCP | 可选 |
| 9005 | PostgreSQL兼容 | TCP | 可选 |
| 2181 | ZooKeeper | TCP | 集群必需 |

## 实践操作 🛠️

### 方案一：Docker快速安装 (推荐新手)

#### 1.1 安装Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# macOS (使用Homebrew)
brew install docker
```

#### 1.2 运行ClickHouse Docker容器
```bash
# 执行Docker安装脚本
chmod +x day1/code/docker-install.sh
./day1/code/docker-install.sh
```

**脚本功能:**
- 自动拉取最新稳定版镜像
- 配置数据持久化
- 设置网络和端口映射
- 启动健康检查
- 创建默认用户和数据库

#### 1.3 验证安装
```bash
# 检查容器状态
docker ps | grep clickhouse

# 连接测试
docker exec -it clickhouse-server clickhouse-client

# 执行测试查询
echo "SELECT version()" | docker exec -i clickhouse-server clickhouse-client
```

### 方案二：原生安装 (推荐生产环境)

#### 2.1 自动安装脚本
```bash
# 执行原生安装脚本
chmod +x day1/code/install-native.sh
./day1/code/install-native.sh
```

**脚本特性:**
- 自动检测操作系统类型
- 支持Ubuntu/Debian、CentOS/RHEL、macOS
- 自动配置软件源
- 安装最新稳定版
- 配置自启动服务
- 执行安装后验证

#### 2.2 手动安装步骤

**Ubuntu/Debian:**
```bash
# 添加官方源
sudo apt-get install -y apt-transport-https ca-certificates dirmngr
GNUPGHOME=$(mktemp -d)
sudo GNUPGHOME="$GNUPGHOME" gpg --no-default-keyring --keyring /usr/share/keyrings/clickhouse-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8919F6BD2B48D754

echo "deb [signed-by=/usr/share/keyrings/clickhouse-keyring.gpg] https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list

# 安装
sudo apt-get update
sudo apt-get install -y clickhouse-server clickhouse-client

# 启动服务
sudo systemctl enable clickhouse-server
sudo systemctl start clickhouse-server
```

**CentOS/RHEL:**
```bash
# 添加官方源
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://packages.clickhouse.com/rpm/clickhouse.repo

# 安装
sudo yum install -y clickhouse-server clickhouse-client

# 启动服务
sudo systemctl enable clickhouse-server
sudo systemctl start clickhouse-server
```

**macOS:**
```bash
# 使用Homebrew
brew install clickhouse

# 启动服务
brew services start clickhouse
```

### 方案三：Windows安装

#### 3.1 WSL2方式 (推荐)
```powershell
# 启用WSL2
wsl --install -d Ubuntu-20.04

# 在WSL2中按Linux方式安装
wsl
sudo apt update
sudo apt install -y clickhouse-server clickhouse-client
```

#### 3.2 Docker Desktop方式
```powershell
# 安装Docker Desktop for Windows
# 然后按Docker方式安装ClickHouse
```

## 配置文件详解 ⚙️

### 主配置文件: config.xml

查看配置模板:
```bash
cat day1/configs/config.xml
```

**重要配置项:**
- `<http_port>8123</http_port>` - HTTP端口
- `<tcp_port>9000</tcp_port>` - 原生客户端端口
- `<data_path>/var/lib/clickhouse/</data_path>` - 数据目录
- `<log_path>/var/log/clickhouse-server/</log_path>` - 日志目录

### 用户配置文件: users.xml

查看用户配置:
```bash
cat day1/configs/users.xml
```

**安全配置:**
- 默认用户设置
- 密码和网络限制
- 查询限制和配额
- 权限控制

## 连接和测试 🔗

### 1. 命令行客户端连接
```bash
# 本地连接
clickhouse-client

# 指定主机和端口
clickhouse-client --host=localhost --port=9000

# 带用户名密码
clickhouse-client --user=default --password=''
```

### 2. HTTP接口连接
```bash
# 基本查询
curl 'http://localhost:8123/' --data-binary "SELECT version()"

# 带认证
curl 'http://localhost:8123/?user=default' --data-binary "SELECT version()"

# JSON格式输出
curl 'http://localhost:8123/?query=SELECT%20version()&default_format=JSON'
```

### 3. 第三方客户端
- **DBeaver**: 通用数据库客户端
- **DataGrip**: JetBrains IDE
- **Tabix**: Web界面客户端
- **Grafana**: 监控和可视化

## 快速体验 🚀

运行快速开始示例:
```bash
clickhouse-client < day1/examples/quick-start.sql
```

**示例内容包括:**
- 数据库和表创建
- 数据插入和查询
- 基本聚合分析
- 函数使用示例
- 数据导入导出

## 性能测试 📊

### 基准测试脚本
```bash
# 执行性能测试
chmod +x day1/code/benchmark.sh
./day1/code/benchmark.sh
```

**测试项目:**
- 基础查询性能
- 大数据量插入
- 复杂聚合查询
- 并发查询测试
- 内存和CPU使用率

### 预期性能指标
- **简单查询**: < 10ms
- **聚合查询**: < 100ms
- **大表扫描**: 根据数据量而定
- **插入速度**: > 100MB/s (取决于硬件)

## 健康检查和监控 🔍

### 系统状态检查
```bash
# 执行健康检查脚本
chmod +x day1/code/check-config.sh
./day1/code/check-config.sh
```

**检查项目:**
- 服务运行状态
- 端口监听情况
- 配置文件语法
- 磁盘空间和权限
- 日志文件检查

### 监控SQL命令
```sql
-- 检查系统信息
SELECT * FROM system.build_options;

-- 查看数据库列表
SHOW DATABASES;

-- 检查表信息
SELECT * FROM system.tables LIMIT 5;

-- 监控查询执行
SELECT * FROM system.processes;

-- 查看系统指标
SELECT * FROM system.metrics LIMIT 10;
```

## 故障排除 🔧

### 常见问题

#### 1. 服务启动失败
```bash
# 检查服务状态
sudo systemctl status clickhouse-server

# 查看详细日志
sudo journalctl -u clickhouse-server -f

# 检查配置文件
sudo clickhouse-server --config-file=/etc/clickhouse-server/config.xml --daemon
```

#### 2. 连接被拒绝
- 检查防火墙设置
- 验证端口配置
- 确认服务运行状态
- 检查网络配置

#### 3. 权限问题
```bash
# 检查文件权限
ls -la /etc/clickhouse-server/
ls -la /var/lib/clickhouse/

# 修复权限
sudo chown -R clickhouse:clickhouse /var/lib/clickhouse/
sudo chown -R clickhouse:clickhouse /var/log/clickhouse-server/
```

#### 4. 性能问题
- 检查系统资源使用
- 优化配置参数
- 调整查询限制
- 监控慢查询日志

### 日志分析
```bash
# 主日志文件
sudo tail -f /var/log/clickhouse-server/clickhouse-server.log

# 错误日志
sudo tail -f /var/log/clickhouse-server/clickhouse-server.err.log

# 查询日志
sudo tail -f /var/log/clickhouse-server/query_log.log
```

## 安全配置 🔒

### 1. 网络安全
```xml
<!-- 限制访问IP -->
<listen_host>127.0.0.1</listen_host>

<!-- 配置SSL -->
<https_port>8443</https_port>
```

### 2. 用户管理
```sql
-- 创建新用户
CREATE USER new_user IDENTIFIED BY 'password';

-- 授权
GRANT SELECT ON database.* TO new_user;

-- 查看用户权限
SHOW GRANTS FOR new_user;
```

### 3. 查询限制
```xml
<profiles>
    <default>
        <max_memory_usage>10000000000</max_memory_usage>
        <max_execution_time>60</max_execution_time>
    </default>
</profiles>
```

## 维护操作 🔧

### 1. 备份策略
```bash
# 数据目录备份
sudo rsync -av /var/lib/clickhouse/ /backup/clickhouse/

# 配置文件备份
sudo cp -r /etc/clickhouse-server/ /backup/config/
```

### 2. 日志轮转
```bash
# 配置logrotate
sudo nano /etc/logrotate.d/clickhouse-server
```

### 3. 更新升级
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade clickhouse-server clickhouse-client

# CentOS/RHEL
sudo yum update clickhouse-server clickhouse-client
```

## 下一步学习 📖

完成环境搭建后，建议：

1. **熟悉基本操作**: 连接、查询、插入数据
2. **了解配置选项**: 调整性能参数
3. **练习SQL语法**: 准备Day 2的理论学习
4. **监控系统状态**: 养成运维好习惯

## 总结 📋

今天我们完成了：
- ✅ ClickHouse多种安装方式
- ✅ 基本配置和连接方法
- ✅ 性能测试和健康检查
- ✅ 故障排除和安全配置
- ✅ 维护操作和最佳实践

**下一步**: Day 2 - ClickHouse核心概念和架构原理

---
*学习进度: Day 1/14 完成* 🎉 