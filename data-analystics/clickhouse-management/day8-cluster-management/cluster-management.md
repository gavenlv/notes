# Day 8: ClickHouse 集群管理和分布式全攻略

## 学习目标 🎯
- 掌握ClickHouse分布式架构设计原理
- 学会集群配置和节点管理
- 理解分片(Shard)和副本(Replica)机制
- 掌握分布式表的创建和使用
- 学会集群监控和故障处理
- 了解数据迁移和扩容策略

## 为什么Day 8学集群管理和分布式？ 🤔

经过前7天的学习：
- ✅ Day 1: 环境搭建 - 单节点基础
- ✅ Day 2: 理论基础 - 架构原理
- ✅ Day 3: 云端部署 - 生产环境
- ✅ Day 4: SQL语法 - 基础操作
- ✅ Day 5: 表引擎 - 存储机制
- ✅ Day 6: 查询优化 - 性能调优
- ✅ Day 7: 数据导入导出 - 数据流转

现在学习**集群管理和分布式**，这是ClickHouse生产环境的核心技能！

### 学习路径回顾
```
Day 1: 环境搭建 ✅ → Day 2: 理论基础 ✅ → Day 3: 云端部署 ✅ → Day 4: SQL语法 ✅ → Day 5: 表引擎 ✅ → Day 6: 查询优化 ✅ → Day 7: 数据导入导出 ✅ → Day 8: 集群管理和分布式
```

## 知识要点 📚

### 1. ClickHouse分布式架构概览

#### 1.1 分布式架构核心概念

ClickHouse采用**Shared Nothing**架构，每个节点都是独立的，通过网络协调工作。

#### 1.2 核心组件说明

| 组件 | 作用 | 特点 | 数量建议 |
|------|------|------|----------|
| **Shard (分片)** | 数据水平分割 | 提高并行处理能力 | 根据数据量决定 |
| **Replica (副本)** | 数据冗余备份 | 提高可用性和读性能 | 每个分片2-3个副本 |
| **ZooKeeper** | 分布式协调 | 管理元数据和副本同步 | 3或5个节点 |
| **Load Balancer** | 负载均衡 | 分发客户端请求 | 2个节点(主备) |

#### 1.3 分布式优势

**水平扩展能力**：
- 📈 **性能线性增长**：增加节点直接提升处理能力
- 🔄 **负载分散**：查询和写入压力分布到多个节点
- 💾 **存储扩展**：突破单机存储限制

**高可用性**：
- 🛡️ **故障容错**：单节点故障不影响整体服务
- 🔄 **自动故障转移**：副本自动接管故障节点工作
- ⚡ **读写分离**：副本可以分担读查询压力

### 2. 集群配置详解

#### 2.1 配置文件结构

ClickHouse集群配置主要在`config.xml`中的`<remote_servers>`部分：

```xml
<!-- /etc/clickhouse-server/config.xml -->
<clickhouse>
    <!-- ZooKeeper配置 -->
    <zookeeper>
        <node index="1">
            <host>zk1.example.com</host>
            <port>2181</port>
        </node>
        <node index="2">
            <host>zk2.example.com</host>
            <port>2181</port>
        </node>
        <node index="3">
            <host>zk3.example.com</host>
            <port>2181</port>
        </node>
    </zookeeper>

    <!-- 集群配置 -->
    <remote_servers>
        <production_cluster>
            <!-- 第一个分片 -->
            <shard>
                <weight>1</weight>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>ch1.example.com</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
                <replica>
                    <host>ch2.example.com</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
            </shard>
            
            <!-- 第二个分片 -->
            <shard>
                <weight>1</weight>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>ch3.example.com</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
                <replica>
                    <host>ch4.example.com</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
            </shard>
        </production_cluster>
    </remote_servers>

    <!-- 宏定义 -->
    <macros>
        <cluster>production_cluster</cluster>
        <shard>01</shard>
        <replica>replica1</replica>
    </macros>

    <!-- 分布式DDL配置 -->
    <distributed_ddl>
        <path>/clickhouse/task_queue/ddl</path>
    </distributed_ddl>
</clickhouse>
```

#### 2.2 配置参数详解

**集群配置参数**：

```xml
<!-- 分片权重配置 -->
<weight>1</weight>
<!-- 权重决定数据分布比例，权重越高分配的数据越多 -->

<!-- 内部复制开关 -->
<internal_replication>true</internal_replication>
<!-- true: ClickHouse自动处理副本同步 -->
<!-- false: 需要手动向每个副本写入数据 -->

<!-- 连接参数 -->
<host>ch1.example.com</host>     <!-- 节点主机名或IP -->
<port>9000</port>                <!-- ClickHouse原生协议端口 -->
<user>default</user>             <!-- 连接用户名 -->
<password></password>            <!-- 连接密码 -->
<secure>0</secure>               <!-- 是否使用SSL -->
<compression>true</compression>   <!-- 是否启用压缩 -->
```

### 3. 分布式表管理

#### 3.1 分布式表类型

ClickHouse中有两种分布式表：

1. **本地表 (Local Table)**：存储在单个节点上的实际数据表
2. **分布式表 (Distributed Table)**：跨多个节点的逻辑视图表

#### 3.2 创建分布式表

**步骤1：在每个节点创建本地表**

```sql
-- 在所有节点上执行
CREATE TABLE user_analytics_local ON CLUSTER production_cluster (
    user_id UInt32,
    event_date Date,
    page_views UInt32,
    session_duration UInt32,
    country String,
    device_type String,
    revenue Decimal(10, 2)
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/user_analytics', '{replica}')
PARTITION BY toYYYYMM(event_date)
ORDER BY (user_id, event_date)
SETTINGS index_granularity = 8192;
```

**步骤2：创建分布式表**

```sql
-- 在所有节点上执行
CREATE TABLE user_analytics_distributed ON CLUSTER production_cluster AS user_analytics_local
ENGINE = Distributed(production_cluster, default, user_analytics_local, rand());
```

#### 3.3 分布式表引擎参数

```sql
ENGINE = Distributed(cluster_name, database, table, sharding_key[, policy_name])
```

| 参数 | 说明 | 示例 |
|------|------|------|
| `cluster_name` | 集群名称 | `production_cluster` |
| `database` | 数据库名 | `default` |
| `table` | 本地表名 | `user_analytics_local` |
| `sharding_key` | 分片键 | `rand()`, `user_id`, `cityHash64(user_id)` |
| `policy_name` | 分片策略(可选) | `round_robin` |

#### 3.4 分片键选择策略

**常用分片键**：

```sql
-- 1. 随机分片 - 数据均匀分布
ENGINE = Distributed(cluster, db, table, rand())

-- 2. 用户ID分片 - 相同用户数据在同一分片
ENGINE = Distributed(cluster, db, table, user_id)

-- 3. 哈希分片 - 更均匀的分布
ENGINE = Distributed(cluster, db, table, cityHash64(user_id))

-- 4. 时间分片 - 按时间范围分片
ENGINE = Distributed(cluster, db, table, toYYYYMM(event_date))

-- 5. 地理分片 - 按地区分片
ENGINE = Distributed(cluster, db, table, cityHash64(country))
```

**分片键选择原则**：

1. **数据分布均匀**：避免热点分片
2. **查询局部性**：相关数据尽量在同一分片
3. **扩展友好**：便于后续扩容
4. **业务逻辑**：符合业务查询模式

### 4. 副本管理

#### 4.1 ReplicatedMergeTree引擎

ReplicatedMergeTree是ClickHouse的核心复制引擎：

```sql
CREATE TABLE replicated_table (
    id UInt32,
    name String,
    timestamp DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/replicated_table', '{replica}')
ORDER BY id
PARTITION BY toYYYYMM(timestamp);
```

**路径参数说明**：
- `/clickhouse/tables/{shard}/replicated_table`：ZooKeeper中的表路径
- `{replica}`：副本标识符，来自宏配置

#### 4.2 副本状态监控

```sql
-- 查看副本状态
SELECT 
    database,
    table,
    replica_name,
    is_leader,
    is_readonly,
    absolute_delay,
    queue_size,
    inserts_in_queue,
    merges_in_queue
FROM system.replicas
WHERE database = 'default'
  AND table = 'user_analytics_local';

-- 查看副本队列
SELECT 
    database,
    table,
    replica_name,
    position,
    node_name,
    type,
    create_time,
    required_quorum,
    source_replica,
    is_currently_executing
FROM system.replication_queue
WHERE database = 'default'
  AND table = 'user_analytics_local'
ORDER BY create_time;
```

#### 4.3 副本故障恢复

**手动同步副本**：

```sql
-- 强制同步特定副本
SYSTEM SYNC REPLICA user_analytics_local;

-- 重启副本队列
SYSTEM RESTART REPLICA user_analytics_local;

-- 删除损坏的副本
SYSTEM DROP REPLICA 'replica_name' FROM TABLE user_analytics_local;
```

### 5. 分布式查询优化

#### 5.1 分布式查询优化技巧

**1. 合理使用GLOBAL关键字**

```sql
-- 不推荐：子查询在每个分片执行
SELECT user_id, revenue
FROM user_analytics_distributed 
WHERE user_id IN (
    SELECT user_id 
    FROM user_profiles_distributed 
    WHERE country = 'China'
);

-- 推荐：使用GLOBAL优化
SELECT user_id, revenue
FROM user_analytics_distributed 
WHERE user_id IN GLOBAL (
    SELECT user_id 
    FROM user_profiles_distributed 
    WHERE country = 'China'
);
```

**2. 利用分片键优化查询**

```sql
-- 优化前：全分片扫描
SELECT sum(revenue) 
FROM user_analytics_distributed 
WHERE event_date = '2024-01-01';

-- 优化后：指定分片键条件
SELECT sum(revenue) 
FROM user_analytics_distributed 
WHERE event_date = '2024-01-01'
  AND user_id BETWEEN 1000 AND 2000;  -- 分片键条件
```

**3. 预聚合和物化视图**

```sql
-- 创建预聚合表
CREATE TABLE user_analytics_daily_local ON CLUSTER production_cluster (
    event_date Date,
    country String,
    device_type String,
    total_users UInt32,
    total_revenue Decimal(12, 2)
) ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/{shard}/user_analytics_daily', '{replica}')
ORDER BY (event_date, country, device_type)
PARTITION BY toYYYYMM(event_date);

-- 创建物化视图
CREATE MATERIALIZED VIEW user_analytics_daily_mv ON CLUSTER production_cluster
TO user_analytics_daily_local AS
SELECT 
    event_date,
    country,
    device_type,
    count() as total_users,
    sum(revenue) as total_revenue
FROM user_analytics_local
GROUP BY event_date, country, device_type;
```

#### 5.2 查询性能监控

```sql
-- 查看当前查询
SELECT 
    query_id,
    user,
    query,
    elapsed,
    read_rows,
    read_bytes,
    written_rows,
    memory_usage
FROM system.processes 
WHERE query NOT LIKE '%system.processes%'
ORDER BY elapsed DESC;

-- 查看查询日志
SELECT 
    event_date,
    query_start_time,
    query_duration_ms,
    read_rows,
    read_bytes,
    result_rows,
    result_bytes,
    memory_usage,
    query
FROM system.query_log 
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query_duration_ms > 1000  -- 查询时间超过1秒
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### 6. 集群运维管理

#### 6.1 集群健康检查

**基础连通性检查**：

```sql
-- 检查集群节点状态
SELECT 
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    is_local,
    user,
    errors_count,
    slowdowns_count,
    estimated_recovery_time
FROM system.clusters 
WHERE cluster = 'production_cluster';

-- 检查分布式表状态
SELECT 
    database,
    table,
    engine,
    is_temporary,
    data_paths,
    metadata_path,
    dependencies_database,
    dependencies_table
FROM system.tables 
WHERE engine LIKE '%Distributed%';
```

**ZooKeeper连接检查**：

```sql
-- 检查ZooKeeper连接
SELECT 
    name,
    value,
    changed
FROM system.zookeeper 
WHERE path = '/';

-- 检查分布式DDL队列
SELECT 
    entry,
    host,
    port,
    status,
    exception,
    query
FROM system.distributed_ddl_queue
ORDER BY entry DESC
LIMIT 10;
```

#### 6.2 集群扩容策略

**水平扩容步骤**：

1. **准备新节点**
```bash
# 安装ClickHouse
sudo apt-get install clickhouse-server clickhouse-client

# 配置集群信息
sudo vim /etc/clickhouse-server/config.xml
```

2. **更新集群配置**
```xml
<!-- 添加新的分片 -->
<shard>
    <weight>1</weight>
    <internal_replication>true</internal_replication>
    <replica>
        <host>ch5.example.com</host>
        <port>9000</port>
    </replica>
    <replica>
        <host>ch6.example.com</host>
        <port>9000</port>
    </replica>
</shard>
```

3. **重新加载配置**
```sql
-- 重新加载配置
SYSTEM RELOAD CONFIG;

-- 验证新节点
SELECT * FROM system.clusters WHERE cluster = 'production_cluster';
```

#### 6.3 数据迁移和重平衡

**手动数据迁移**：

```sql
-- 1. 创建临时分布式表（包含新分片）
CREATE TABLE user_analytics_new_distributed AS user_analytics_local
ENGINE = Distributed(production_cluster_new, default, user_analytics_local, cityHash64(user_id));

-- 2. 数据重新分布
INSERT INTO user_analytics_new_distributed 
SELECT * FROM user_analytics_distributed;

-- 3. 验证数据一致性
SELECT 
    count() as total_rows,
    sum(revenue) as total_revenue
FROM user_analytics_distributed
UNION ALL
SELECT 
    count() as total_rows,
    sum(revenue) as total_revenue  
FROM user_analytics_new_distributed;

-- 4. 切换表名
RENAME TABLE user_analytics_distributed TO user_analytics_old_distributed;
RENAME TABLE user_analytics_new_distributed TO user_analytics_distributed;
```

### 7. 监控和告警

#### 7.1 关键监控指标

**集群级别监控**：

```sql
-- 集群节点状态监控
CREATE VIEW cluster_health AS
SELECT 
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    errors_count,
    slowdowns_count,
    CASE 
        WHEN errors_count = 0 THEN 'Healthy'
        WHEN errors_count < 10 THEN 'Warning'
        ELSE 'Critical'
    END as health_status
FROM system.clusters;

-- 副本延迟监控  
CREATE VIEW replica_lag AS
SELECT 
    database,
    table,
    replica_name,
    absolute_delay,
    queue_size,
    CASE 
        WHEN absolute_delay < 60 THEN 'OK'
        WHEN absolute_delay < 300 THEN 'Warning'
        ELSE 'Critical'
    END as lag_status
FROM system.replicas;
```

**性能监控**：

```sql
-- 查询性能监控
SELECT 
    toStartOfHour(event_time) as hour,
    count() as query_count,
    avg(query_duration_ms) as avg_duration,
    quantile(0.95)(query_duration_ms) as p95_duration,
    sum(read_bytes) as total_read_bytes
FROM system.query_log 
WHERE event_date = today()
  AND type = 'QueryFinish'
GROUP BY hour
ORDER BY hour;

-- 资源使用监控
SELECT 
    hostName() as host,
    uptime() as uptime_seconds,
    formatReadableSize(total_memory) as total_memory,
    formatReadableSize(free_memory) as free_memory,
    round(free_memory / total_memory * 100, 2) as memory_usage_percent
FROM system.asynchronous_metrics
WHERE metric LIKE '%Memory%';
```

### 8. 最佳实践总结

#### 8.1 集群设计原则

**硬件配置建议**：

| 组件 | CPU | 内存 | 存储 | 网络 |
|------|-----|------|------|------|
| **ClickHouse节点** | 16+ cores | 64GB+ | SSD RAID10 | 10Gbps |
| **ZooKeeper节点** | 4+ cores | 8GB+ | SSD | 1Gbps |
| **负载均衡器** | 8+ cores | 16GB+ | SSD | 10Gbps |

**集群规模建议**：

- **小型集群**：3个分片，每分片2个副本 (6个ClickHouse节点)
- **中型集群**：6个分片，每分片2个副本 (12个ClickHouse节点)  
- **大型集群**：12+个分片，每分片2-3个副本 (24+个ClickHouse节点)

#### 8.2 运维最佳实践

**配置管理**：
- ✅ 使用配置管理工具(Ansible/Puppet)统一配置
- ✅ 版本控制所有配置文件
- ✅ 定期备份配置和元数据
- ✅ 测试环境验证配置变更

**监控告警**：
- ✅ 部署完整的监控体系(Prometheus + Grafana)
- ✅ 设置合理的告警阈值
- ✅ 建立故障响应流程
- ✅ 定期演练故障恢复

**数据管理**：
- ✅ 合理设计分片键，避免热点
- ✅ 定期清理过期数据
- ✅ 监控数据倾斜情况
- ✅ 制定扩容计划

**安全管理**：
- ✅ 启用用户认证和权限控制
- ✅ 使用SSL/TLS加密传输
- ✅ 定期更新系统和软件
- ✅ 网络隔离和防火墙配置

#### 8.3 性能优化建议

**查询优化**：
- 🚀 使用合适的分片键进行查询过滤
- 🚀 利用GLOBAL关键字优化分布式JOIN
- 🚀 创建预聚合表和物化视图
- 🚀 避免跨分片的复杂查询

**写入优化**：
- 🚀 批量写入而非单条插入
- 🚀 使用异步写入模式
- 🚀 合理设置批次大小
- 🚀 避免写入热点分片

**存储优化**：
- 🚀 选择合适的压缩算法
- 🚀 定期执行OPTIMIZE操作
- 🚀 合理设置分区策略
- 🚀 监控磁盘使用情况

## 实践练习 🛠️

### 练习1：搭建本地集群

使用Docker Compose搭建本地测试集群：

```yaml
# docker-compose.yml
version: '3.8'
services:
  zookeeper:
    image: zookeeper:3.7
    hostname: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOO_MY_ID: 1
      ZOO_SERVERS: server.1=0.0.0.0:2888:3888;2181

  clickhouse-01:
    image: clickhouse/clickhouse-server:latest
    hostname: clickhouse-01
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - ./config/clickhouse-01:/etc/clickhouse-server/
    depends_on:
      - zookeeper

  clickhouse-02:
    image: clickhouse/clickhouse-server:latest
    hostname: clickhouse-02
    ports:
      - "8124:8123"
      - "9001:9000"
    volumes:
      - ./config/clickhouse-02:/etc/clickhouse-server/
    depends_on:
      - zookeeper
```

### 练习2：分布式表操作

运行day8的示例文件：
```bash
clickhouse-client < day8/examples/cluster-demo.sql
```

### 练习3：故障模拟和恢复

```sql
-- 模拟节点故障
-- 停止一个副本节点，观察集群行为

-- 检查副本状态
SELECT * FROM system.replicas;

-- 重启节点后检查恢复情况
SYSTEM SYNC REPLICA user_analytics_local;
```

## 常见问题 ❓

### Q1: 如何选择合适的分片数量？
**A**: 分片数量选择原则：
- 根据数据量：每个分片建议存储100GB-1TB数据
- 考虑查询并发：分片数 ≈ CPU核心数 / 2
- 预留扩展空间：初期可以少一些，后续扩容
- 避免过度分片：太多分片会增加协调开销

### Q2: 副本同步延迟高怎么处理？
**A**: 延迟优化方法：
- 检查网络带宽和延迟
- 调整max_replica_delay_for_distributed_queries参数
- 优化ZooKeeper性能
- 使用SSD存储加速同步

### Q3: 如何处理数据倾斜问题？
**A**: 数据倾斜解决方案：
- 重新选择分片键，使用哈希函数
- 调整分片权重配置
- 实施数据重平衡
- 监控各分片的数据分布情况

### Q4: 集群扩容时如何保证服务不中断？
**A**: 无中断扩容策略：
- 使用滚动升级方式
- 先添加副本节点，再添加分片
- 利用负载均衡器进行流量控制
- 分批迁移数据，验证后切换

## 今日总结 📋

今天我们全面学习了：
- ✅ ClickHouse分布式架构和核心概念
- ✅ 集群配置和节点管理
- ✅ 分布式表的创建和使用
- ✅ 副本管理和故障恢复
- ✅ 分布式查询优化技巧
- ✅ 集群运维和监控告警

**下一步**: Day 9 - 监控和运维，深入学习ClickHouse的监控体系

---
*学习进度: Day 8/14 完成* 🎉 