# Doris高可用集群部署指南

本目录包含Doris高可用集群的部署配置文件和脚本，用于部署一个包含3个FE Follower节点和3个BE节点的高可用集群。

## 目录结构

```
ha-cluster/
├── docker-compose.yml          # Docker Compose配置文件
├── init-sql/
│   └── init-cluster.sql        # 集群初始化SQL脚本
├── fe-follower-1.conf          # FE Follower节点1配置
├── fe-follower-2.conf          # FE Follower节点2配置
├── fe-follower-3.conf          # FE Follower节点3配置
├── be-1.conf                   # BE节点1配置
├── be-2.conf                   # BE节点2配置
├── be-3.conf                   # BE节点3配置
└── README.md                   # 本文件
```

## 集群架构

本高可用集群包含以下组件：

- 3个FE Follower节点：
  - fe-follower-1 (端口: 8030, 9030, 9010)
  - fe-follower-2 (端口: 8031, 9031, 9011)
  - fe-follower-3 (端口: 8032, 9032, 9012)

- 3个BE节点：
  - be-1 (端口: 8040, 9000, 9050)
  - be-2 (端口: 8041, 9001, 9051)
  - be-3 (端口: 8042, 9002, 9052)

## 快速开始

### 1. 前置条件

- Docker和Docker Compose已安装
- 至少8GB可用内存
- 至少50GB可用磁盘空间
- 确保以下端口未被占用：
  - FE端口: 8030-8032, 9030-9032, 9010-9012
  - BE端口: 8040-8042, 9000-9002, 9050-9052

### 2. 创建必要的目录

```bash
# 创建FE节点数据目录
mkdir -p fe-follower-1/{conf,doris-meta,log}
mkdir -p fe-follower-2/{conf,doris-meta,log}
mkdir -p fe-follower-3/{conf,doris-meta,log}

# 创建BE节点数据目录
mkdir -p be-1/{conf,storage,log}
mkdir -p be-2/{conf,storage,log}
mkdir -p be-3/{conf,storage,log}

# 创建初始化SQL目录
mkdir -p init-sql
```

### 3. 复制配置文件

```bash
# 复制FE配置文件
cp fe-follower-1.conf fe-follower-1/conf/fe.conf
cp fe-follower-2.conf fe-follower-2/conf/fe.conf
cp fe-follower-3.conf fe-follower-3/conf/fe.conf

# 复制BE配置文件
cp be-1.conf be-1/conf/be.conf
cp be-2.conf be-2/conf/be.conf
cp be-3.conf be-3/conf/be.conf
```

### 4. 启动集群

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 验证集群状态

```bash
# 连接到FE Follower节点1
mysql -h 127.0.0.1 -P 9030 -uroot

# 查看FE节点状态
SHOW FRONTENDS;

# 查看BE节点状态
SHOW BACKENDS;

# 查看数据库
SHOW DATABASES;
```

## 配置说明

### FE节点配置

每个FE Follower节点的配置文件主要包含以下关键配置：

- `priority_networks`: 指定网络范围
- `frontend_address`: 节点主机名
- `meta_dir`: 元数据存储目录
- `cluster_id`: 集群ID，所有FE节点必须相同
- `http_port`: HTTP端口
- `query_port`: MySQL协议端口
- `edit_log_port`: FE节点间通信端口

### BE节点配置

每个BE节点的配置文件主要包含以下关键配置：

- `priority_networks`: 指定网络范围
- `be_ip`: 节点主机名
- `storage_root_path`: 存储根目录
- `be_port`: BE Thrift端口
- `webserver_port`: BE HTTP端口
- `heartbeat_service_port`: BE心跳端口

### 网络配置

集群使用Docker自定义网络`doris-ha-net`，子网为`172.20.0.0/16`，确保容器间可以正常通信。

## 高可用特性

### FE高可用

- 3个FE Follower节点组成高可用集群
- 通过Raft协议选举Leader节点
- Leader节点负责处理元数据变更
- Follower节点同步元数据并参与选举
- 当Leader节点故障时，自动选举新的Leader

### BE高可用

- 多个BE节点提供数据存储和计算能力
- 数据副本分布在不同的BE节点
- 当某个BE节点故障时，查询可以路由到其他节点
- 支持节点故障后的自动恢复

## 连接信息

### FE节点连接信息

- FE Follower节点1:
  - MySQL协议: `mysql -h 127.0.0.1 -P 9030 -uroot`
  - Web UI: http://127.0.0.1:8030

- FE Follower节点2:
  - MySQL协议: `mysql -h 127.0.0.1 -P 9031 -uroot`
  - Web UI: http://127.0.0.1:8031

- FE Follower节点3:
  - MySQL协议: `mysql -h 127.0.0.1 -P 9032 -uroot`
  - Web UI: http://127.0.0.1:8032

### BE节点连接信息

- BE节点1:
  - HTTP: http://127.0.0.1:8040
  - Thrift: 127.0.0.1:9000
  - 心跳: 127.0.0.1:9050

- BE节点2:
  - HTTP: http://127.0.0.1:8041
  - Thrift: 127.0.0.1:9001
  - 心跳: 127.0.0.1:9051

- BE节点3:
  - HTTP: http://127.0.0.1:8042
  - Thrift: 127.0.0.1:9002
  - 心跳: 127.0.0.1:9052

## 常见操作

### 添加新的BE节点

1. 准备新的BE节点配置文件
2. 启动新的BE节点
3. 连接到FE Leader节点
4. 执行命令添加BE节点:
   ```sql
   ALTER SYSTEM ADD BACKEND "new-be-host:9050";
   ```

### 添加新的FE Follower节点

1. 准备新的FE节点配置文件
2. 启动新的FE节点
3. 连接到FE Leader节点
4. 执行命令添加FE节点:
   ```sql
   ALTER SYSTEM ADD FOLLOWER "new-fe-host:9010";
   ```

### 移除BE节点

1. 连接到FE Leader节点
2. 执行命令移除BE节点:
   ```sql
   ALTER SYSTEM DECOMMISSION BACKEND "be-host:9050";
   ```

### 移除FE节点

1. 连接到FE Leader节点
2. 执行命令移除FE节点:
   ```sql
   ALTER SYSTEM DECOMMISSION FOLLOWER "fe-host:9010";
   ```

## 故障恢复

### FE节点故障

- 当FE Leader节点故障时，集群会自动从Follower节点中选举新的Leader
- 选举过程通常在几秒到几十秒内完成
- 选举期间集群可能无法处理元数据变更操作
- 查询操作仍然可用

### BE节点故障

- 当BE节点故障时，集群会自动检测到节点不可用
- 查询会自动路由到其他健康的BE节点
- 如果数据副本不足，可能影响查询结果
- 节点恢复后会自动加入集群

## 监控和维护

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fe-follower-1
docker-compose logs -f be-1
```

### 集群状态检查

```sql
-- 查看FE节点状态
SHOW FRONTENDS;

-- 查看BE节点状态
SHOW BACKENDS;

-- 查看集群信息
SHOW PROC '/clusters';
```

### 数据备份

```sql
-- 创建备份
BACKUP DATABASE demo TO 'backup_label'
PROPERTIES
(
    "type" = "full",
    "timeout" = "3600"
);

-- 查看备份任务
SHOW BACKUP;

-- 恢复数据
RESTORE DATABASE demo FROM 'backup_label'
PROPERTIES
(
    "backup_timestamp" = "2023-11-20-10-30-00",
    "timeout" = "3600"
);
```

## 性能调优

### FE节点调优

- 调整JVM内存大小：修改`JAVA_OPTS`参数
- 调整最大连接数：修改`max_connection`参数
- 优化元数据存储：使用SSD存储元数据

### BE节点调优

- 调整内存限制：修改`mem_limit`参数
- 优化存储配置：使用高性能存储设备
- 调整并发参数：修改`max_scan_thread_num`等参数

## 安全配置

### 启用SSL/TLS

1. 生成SSL证书
2. 修改FE和BE配置文件，设置`enable_ssl = true`
3. 配置证书路径和密码

### 用户权限管理

```sql
-- 创建用户
CREATE USER 'username'@'%' IDENTIFIED BY 'password';

-- 授权
GRANT SELECT_PRIV ON database.* TO 'username'@'%';

-- 查看权限
SHOW GRANTS FOR 'username'@'%';
```

## 扩展阅读

- [Doris官方文档](https://doris.apache.org/docs/)
- [Doris高可用部署指南](https://doris.apache.org/docs/admin-manual/cluster-management/ha-deployment/)
- [Doris集群管理](https://doris.apache.org/docs/admin-manual/cluster-management/)

## 常见问题

### Q: 如何确定FE Leader节点？

A: 执行`SHOW FRONTENDS;`命令，Role为FOLLOWER且IsMaster为true的节点是Leader节点。

### Q: BE节点一直显示false怎么办？

A: 检查BE节点日志，确认网络连接是否正常，检查防火墙设置。

### Q: 如何扩容集群？

A: 按照常见操作中的步骤添加新的FE或BE节点。

### Q: 如何升级集群？

A: 按照官方升级文档，逐个升级FE和BE节点。