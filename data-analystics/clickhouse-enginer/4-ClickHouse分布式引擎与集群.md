# ClickHouse分布式引擎与集群

ClickHouse的分布式能力是其最强大的特性之一，通过分布式引擎和集群架构，可以实现水平扩展、高可用和负载均衡。本章详细介绍ClickHouse的分布式引擎、集群管理和分布式查询优化。

## 1. 分布式架构概述

### 1.1 ClickHouse集群架构

ClickHouse集群由多个分片(Shard)和副本(Replica)组成：

- **分片(Shard)**：数据水平分割，每个分片存储部分数据
- **副本(Replica)**：数据冗余备份，提供高可用性
- **ZooKeeper**：协调服务，管理集群状态和副本同步

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    分片1         │    │    分片2         │    │    分片3         │
│ ┌─────┐ ┌─────┐ │    │ ┌─────┐ ┌─────┐ │    │ ┌─────┐ ┌─────┐ │
│ │R1.1 │ │R1.2 │ │    │ │R2.1 │ │R2.2 │ │    │ │R3.1 │ │R3.2 │ │
│ └─────┘ └─────┘ │    │ └─────┘ └─────┘ │    │ └─────┘ └─────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 分片与副本的选择

**何时使用分片：**
- 数据量超过单个节点的存储容量
- 查询负载超过单个节点的处理能力
- 需要提高并行处理能力

**何时使用副本：**
- 需要高可用性
- 提高查询吞吐量（副本可以分担读取负载）
- 数据安全备份

### 1.3 分布式DML操作

- **INSERT**：可以分布式插入到各个分片
- **SELECT**：可以分布式查询所有分片
- **UPDATE/DELETE**：ClickHouse不支持标准的UPDATE/DELETE，但有替代方案
- **ALTER**：分布式ALTER操作需要特殊处理

## 2. Distributed引擎详解

### 2.1 基本语法

```sql
CREATE TABLE table_name (
    column1 Type1,
    column2 Type2,
    ...
) ENGINE = Distributed(cluster_name, database_name, table_name[, sharding_key])
```

参数说明：
- **cluster_name**：集群名称，定义在配置文件中
- **database_name**：远程数据库名称
- **table_name**：远程表名称
- **sharding_key**：分片键，决定数据分布到哪个分片

### 2.2 创建分布式表示例

```sql
-- 本地表
CREATE TABLE local_sales ON CLUSTER 'cluster_name' (
    order_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, product_id);

-- 分布式表
CREATE TABLE sales ON CLUSTER 'cluster_name' (
    order_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = Distributed('cluster_name', 'default', 'local_sales', cityHash64(order_id));
```

### 2.3 分片键选择

分片键决定了数据如何分布到不同分片：

```sql
-- 使用用户ID哈希分片
CREATE TABLE user_events_dist ON CLUSTER 'cluster_name' (
    user_id UInt64,
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = Distributed('cluster_name', 'default', 'user_events_local', cityHash64(user_id));

-- 使用日期和用户ID组合分片
CREATE TABLE user_events_dist_v2 ON CLUSTER 'cluster_name' (
    user_id UInt64,
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = Distributed('cluster_name', 'default', 'user_events_local', 
                       cityHash64(toYYYYMM(event_time), user_id));

-- 使用随机分片
CREATE TABLE user_events_dist_random ON CLUSTER 'cluster_name' (
    user_id UInt64,
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = Distributed('cluster_name', 'default', 'user_events_local', rand());
```

### 2.4 分片键设计原则

1. **均匀分布**：确保数据均匀分布到各个分片
2. **查询局部性**：相关数据尽量分布到同一分片
3. **稳定性**：避免频繁的数据迁移
4. **性能考虑**：分片键计算不应成为瓶颈

## 3. 集群配置与管理

### 3.1 集群配置文件

ClickHouse集群通过配置文件定义，通常在config.xml中指定：

```xml
<!-- config.xml -->
<remote_servers>
    <cluster_name>
        <!-- 分片1 -->
        <shard>
            <replica>
                <host>ch1.example.com</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>ch2.example.com</host>
                <port>9000</port>
            </replica>
        </shard>
        
        <!-- 分片2 -->
        <shard>
            <replica>
                <host>ch3.example.com</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>ch4.example.com</host>
                <port>9000</port>
            </replica>
        </shard>
        
        <!-- 分片3 -->
        <shard>
            <replica>
                <host>ch5.example.com</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>ch6.example.com</host>
                <port>9000</port>
            </replica>
        </shard>
    </cluster_name>
</remote_servers>
```

### 3.2 分片内部负载均衡

```xml
<remote_servers>
    <cluster_name>
        <shard>
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
    </cluster_name>
</remote_servers>
```

### 3.3 ZooKeeper配置

ZooKeeper是ClickHouse集群的关键组件：

```xml
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
```

### 3.4 宏定义

宏定义简化集群配置：

```xml
<macros>
    <shard>01</shard>
    <replica>ch1.example.com</replica>
</macros>
```

## 4. 副本表引擎

### 4.1 ReplicatedMergeTree

ReplicatedMergeTree是MergeTree的副本版本：

```sql
CREATE TABLE local_sales_replicated ON CLUSTER 'cluster_name' (
    order_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/sales', '{replica}')
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, product_id);
```

参数说明：
- **zoo_path**：ZooKeeper中的路径
- **replica_name**：副本名称，通常使用主机名

### 4.2 其他副本引擎

```sql
-- ReplicatedReplacingMergeTree
CREATE TABLE user_status_replicated ON CLUSTER 'cluster_name' (
    user_id UInt64,
    status String,
    update_time DateTime,
    version UInt64
) ENGINE = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/user_status', '{replica}', version)
ORDER BY user_id;

-- ReplicatedSummingMergeTree
CREATE TABLE daily_stats_replicated ON CLUSTER 'cluster_name' (
    date Date,
    metric_name String,
    value UInt64
) ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/{shard}/daily_stats', '{replica}', value)
ORDER BY (date, metric_name);

-- ReplicatedAggregatingMergeTree
CREATE TABLE user_activity_agg_replicated ON CLUSTER 'cluster_name' (
    date Date,
    activity_type String,
    users AggregateFunction(uniq, UInt64),
    page_views AggregateFunction(sum, UInt64)
) ENGINE = ReplicatedAggregatingMergeTree('/clickhouse/tables/{shard}/user_activity_agg', '{replica}')
ORDER BY (date, activity_type);
```

## 5. 分布式DML操作

### 5.1 分布式INSERT

```sql
-- 直接插入分布式表（数据会自动分布到各个分片）
INSERT INTO sales (order_id, product_id, order_time, amount, region, channel) VALUES
    (1, 1001, '2023-01-01 10:00:00', 100.00, 'North', 'Online'),
    (2, 1002, '2023-01-01 10:01:00', 200.00, 'South', 'Offline'),
    (3, 1003, '2023-01-01 10:02:00', 150.00, 'East', 'Online');

-- 批量插入
INSERT INTO sales FORMAT CSV
order_id,product_id,order_time,amount,region,channel
4,1004,"2023-01-01 10:03:00",120.00,West,Online
5,1005,"2023-01-01 10:04:00",80.00,North,Offline
6,1006,"2023-01-01 10:05:00",90.00,South,Online
;
```

### 5.2 分布式SELECT

```sql
-- 基本查询
SELECT 
    region,
    channel,
    count() AS order_count,
    sum(amount) AS total_amount
FROM sales
WHERE order_time >= '2023-01-01'
GROUP BY region, channel
ORDER BY total_amount DESC;

-- 带子查询的分布式查询
SELECT 
    product_id,
    sum(total_amount) AS product_revenue
FROM (
    SELECT 
        product_id,
        sum(amount) AS total_amount
    FROM sales
    WHERE order_time >= '2023-01-01'
    GROUP BY order_id, product_id, amount
)
GROUP BY product_id
ORDER BY product_revenue DESC
LIMIT 10;
```

### 5.3 分布式ALTER

```sql
-- 添加列
ALTER TABLE sales ON CLUSTER 'cluster_name' ADD COLUMN customer_id UInt64;

-- 修改列类型
ALTER TABLE sales ON CLUSTER 'cluster_name' MODIFY COLUMN amount Decimal(12, 2);

-- 删除列
ALTER TABLE sales ON CLUSTER 'cluster_name' DROP COLUMN channel;

-- 添加索引
ALTER TABLE sales ON CLUSTER 'cluster_name' ADD INDEX idx_region_bloom region TYPE bloom_filter GRANULARITY 1;
```

### 5.4 分布式删除操作

ClickHouse不支持标准的DELETE，但可以通过ALTER TABLE删除分区：

```sql
-- 删除分区
ALTER TABLE local_sales ON CLUSTER 'cluster_name' DROP PARTITION '202301';

-- 删除特定数据（通过创建新表）
CREATE TABLE sales_temp AS sales;

INSERT INTO sales_temp SELECT * FROM sales WHERE region != 'Deleted';

RENAME TABLE sales TO sales_old, sales_temp TO sales;

DROP TABLE sales_old;
```

## 6. 分布式查询优化

### 6.1 分布式查询执行流程

1. **查询解析**：解析SQL语句
2. **查询优化**：生成执行计划
3. **子查询分发**：将子查询分发到各个分片
4. **并行执行**：各分片并行执行子查询
5. **结果汇总**：收集并汇总各分片的结果
6. **最终计算**：执行最后的聚合和排序

### 6.2 查询优化设置

```sql
-- 启用分布式聚合
SET distributed_aggregation_memory_efficient = 1;

-- 启用分布式产品模式
SET distributed_product_mode = 'global';

-- 设置并行副本处理
SET parallel_replicas_count = 2;
SET parallel_replicas_offset = 0;

-- 设置查询超时
SET max_execution_time = 60;

-- 设置内存限制
SET max_memory_usage = 10000000000;
```

### 6.3 分布式JOIN优化

```sql
-- 本地表JOIN（推荐）
CREATE TABLE orders ON CLUSTER 'cluster_name' (
    order_id UInt64,
    customer_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2)
) ENGINE = Distributed('cluster_name', 'default', 'local_orders', cityHash64(order_id));

CREATE TABLE customers ON CLUSTER 'cluster_name' (
    customer_id UInt64,
    name String,
    region String,
    register_time DateTime
) ENGINE = Distributed('cluster_name', 'default', 'local_customers', cityHash64(customer_id));

-- 同分片JOIN（效率高）
SELECT 
    o.order_id,
    c.name,
    o.amount,
    o.order_time
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_time >= '2023-01-01';

-- 全局JOIN（跨分片，效率低）
SELECT 
    o.order_id,
    c.name,
    o.amount,
    o.order_time
FROM orders o
GLOBAL JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_time >= '2023-01-01';
```

### 6.4 分布式子查询优化

```sql
-- 低效的分布式子查询
SELECT 
    order_id,
    amount
FROM sales
WHERE product_id IN (
    SELECT product_id 
    FROM products 
    WHERE category = 'Electronics'
);

-- 优化的分布式子查询
SELECT 
    s.order_id,
    s.amount
FROM sales s
GLOBAL JOIN (
    SELECT product_id 
    FROM products 
    WHERE category = 'Electronics'
) p ON s.product_id = p.product_id;
```

## 7. 集群监控与维护

### 7.1 集群状态监控

```sql
-- 查看集群配置
SELECT * FROM system.clusters;

-- 查看副本状态
SELECT 
    database,
    table,
    replica_name,
    is_leader,
    is_readonly,
    absolute_delay,
    queue_size
FROM system.replicas;

-- 查看分片状态
SELECT 
    shard_num,
    replica_num,
    host_name,
    port,
    user,
    errors_count
FROM system.clusters
WHERE cluster = 'cluster_name';

-- 查看分布式表状态
SELECT 
    cluster,
    database,
    table,
    shard,
    replica_num,
    host_name,
    port,
    errors_count
FROM system.parts
WHERE database = 'default' AND table LIKE '%_dist';
```

### 7.2 副本同步监控

```sql
-- 查看ZooKeeper队列
SELECT 
    database,
    table,
    log_pointer,
    log_max_index,
    queue_size
FROM system.replica_queue
ORDER BY database, table;

-- 查看副本延迟
SELECT 
    database,
    table,
    replica_name,
    is_leader,
    absolute_delay,
    expected_delay,
    queue_size
FROM system.replicas
WHERE absolute_delay > 0;
```

### 7.3 分片数据分布

```sql
-- 查看分片数据分布
SELECT 
    shard_num,
    count() AS parts_count,
    sum(rows) AS total_rows,
    sum(data_compressed_bytes) AS compressed_size,
    sum(data_uncompressed_bytes) AS uncompressed_size
FROM system.parts
WHERE database = 'default' AND table = 'local_sales'
GROUP BY shard_num
ORDER BY shard_num;

-- 查看分片查询负载
SELECT 
    shard_num,
    host_name,
    query_duration_ms,
    read_rows,
    read_bytes
FROM system.query_log
WHERE event_date = today()
  AND table = 'sales'
  AND type = 'QueryFinish'
GROUP BY shard_num, host_name
ORDER BY shard_num;
```

### 7.4 集群维护操作

```sql
-- 重置ZooKeeper会话
SYSTEM RESTART REPLICA database.table;

-- 重建副本
SYSTEM SYNC REPLICA database.table;

-- 合并所有分区
OPTIMIZE TABLE local_sales ON CLUSTER 'cluster_name' FINAL;

-- 检查表完整性
CHECK TABLE local_sales ON CLUSTER 'cluster_name';
```

## 8. 高级分布式特性

### 8.1 分布式字典

```sql
-- 创建分布式字典
CREATE DICTIONARY products_dict ON CLUSTER 'cluster_name' (
    product_id UInt64,
    product_name String,
    category String,
    price Decimal(10, 2)
) PRIMARY KEY product_id
SOURCE(CLICKHOUSE(HOST 'ch1.example.com' PORT 9000 USER 'default' PASSWORD '' DB 'default' TABLE 'products'))
LIFETIME(60)
LAYOUT(HASHED());

-- 使用字典
SELECT 
    s.product_id,
    dictGet('products_dict', 'product_name', s.product_id) AS product_name,
    dictGet('products_dict', 'category', s.product_id) AS category,
    s.amount
FROM sales s
WHERE s.order_time >= '2023-01-01';
```

### 8.2 分布式表函数

```sql
-- cluster函数：在集群上执行查询
SELECT 
    hostName(),
    count() AS table_count
FROM cluster('cluster_name', system, tables)
WHERE database = 'default';

-- remote函数：在远程服务器上执行查询
SELECT 
    hostName(),
    count() AS table_count
FROM remote('ch1.example.com', system, tables)
WHERE database = 'default';

-- remoteSecure函数：安全连接远程服务器
SELECT 
    hostName(),
    count() AS table_count
FROM remoteSecure('ch1.example.com', system, tables, 'default', '', '')
WHERE database = 'default';
```

### 8.3 分布式DDL执行

```sql
-- 在集群上创建表
CREATE TABLE new_table ON CLUSTER 'cluster_name' (
    id UInt64,
    name String,
    value Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY id;

-- 在集群上执行查询
EXISTS TABLE new_table ON CLUSTER 'cluster_name';

-- 在集群上删除表
DROP TABLE new_table ON CLUSTER 'cluster_name';
```

### 8.4 分布式查询调度

```sql
-- 设置查询优先级
SET priority = 10;

-- 设置查询超时
SET max_execution_time = 120;

-- 设置分布式表超时
SET distributed_connections_pool_size = 10;

-- 设置远程查询超时
SET connect_timeout = 10;
SET receive_timeout = 300;
```

## 9. 高可用与故障处理

### 9.1 节点故障处理

```sql
-- 手动标记节点为只读
ALTER TABLE local_sales ON CLUSTER 'cluster_name' MODIFY SETTING readonly = 1;

-- 从集群中移除故障节点
ALTER TABLE sales ON CLUSTER 'cluster_name' DETACH PARTITION '202301';

-- 添加新节点
ALTER TABLE sales ON CLUSTER 'cluster_name' ATTACH PARTITION '202301';
```

### 9.2 数据恢复

```sql
-- 从副本恢复数据
CREATE TABLE local_sales_recovery ON CLUSTER 'cluster_name' AS local_sales;
INSERT INTO local_sales_recovery SELECT * FROM remote('ch2.example.com', default, local_sales);

-- 从备份恢复
ATTACH TABLE local_sales_backup 'local_sales_backup' ON CLUSTER 'cluster_name';
RENAME TABLE local_sales_backup TO local_sales ON CLUSTER 'cluster_name';
```

### 9.3 数据重新分布

```sql
-- 创建新的分片表
CREATE TABLE local_sales_new_shard ON CLUSTER 'cluster_name' (
    order_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, product_id);

-- 重新分布数据
INSERT INTO local_sales_new_shard SELECT * FROM local_sales;

-- 切换到新表
RENAME TABLE local_sales TO local_sales_old, local_sales_new_shard TO local_sales;
```

## 10. 性能调优最佳实践

### 10.1 分片策略优化

1. **分片键选择**：使用高基数字段，确保数据均匀分布
2. **分片数量**：根据数据量和查询负载确定合适分片数
3. **分片扩容**：预先规划分片扩容策略
4. **热点数据**：识别和处理热点数据分片

### 10.2 副本策略优化

1. **副本数量**：通常2-3个副本即可满足高可用需求
2. **副本分布**：将副本分布在不同机架或可用区
3. **副本同步**：监控副本延迟，及时处理同步问题
4. **故障转移**：设计合理的故障转移机制

### 10.3 查询优化

1. **查询局部性**：尽量让查询在单个分片内完成
2. **分布式聚合**：合理使用分布式聚合设置
3. **并行处理**：增加并行副本数提高查询吞吐量
4. **查询缓存**：使用查询缓存减少重复计算

### 10.4 网络优化

1. **网络带宽**：确保足够的网络带宽支持分布式查询
2. **网络延迟**：降低节点间网络延迟
3. **压缩传输**：启用数据压缩减少网络传输量
4. **连接池**：合理配置连接池避免连接竞争

## 11. 实际应用案例

### 11.1 电商数据分析平台

```sql
-- 用户行为表
CREATE TABLE user_events_local ON CLUSTER 'analytics_cluster' (
    event_id UUID,
    user_id UInt64,
    session_id String,
    event_type String,
    event_time DateTime,
    page_url String,
    referrer String,
    device_type String,
    properties String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/user_events', '{replica}')
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time, event_type);

-- 用户行为分布式表
CREATE TABLE user_events ON CLUSTER 'analytics_cluster' AS user_events_local
ENGINE = Distributed('analytics_cluster', 'analytics', 'user_events_local', cityHash64(user_id));

-- 产品表
CREATE TABLE products_local ON CLUSTER 'analytics_cluster' (
    product_id UInt64,
    product_name String,
    category String,
    brand String,
    price Decimal(10, 2)
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/products', '{replica}')
ORDER BY product_id;

-- 产品分布式表
CREATE TABLE products ON CLUSTER 'analytics_cluster' AS products_local
ENGINE = Distributed('analytics_cluster', 'analytics', 'products_local', cityHash64(product_id));

-- 订单表
CREATE TABLE orders_local ON CLUSTER 'analytics_cluster' (
    order_id UInt64,
    user_id UInt64,
    product_id UInt64,
    order_time DateTime,
    quantity UInt32,
    unit_price Decimal(10, 2),
    total_amount Decimal(10, 2),
    status String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/orders', '{replica}')
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, order_id);

-- 订单分布式表
CREATE TABLE orders ON CLUSTER 'analytics_cluster' AS orders_local
ENGINE = Distributed('analytics_cluster', 'analytics', 'orders_local', cityHash64(user_id));

-- 实时用户行为分析
CREATE MATERIALIZED VIEW user_activity_realtime_mv TO user_activity_realtime AS
SELECT 
    toDate(event_time) AS date,
    event_type,
    device_type,
    uniqExact(user_id) AS unique_users,
    count() AS event_count
FROM user_events
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY date, event_type, device_type;

-- 产品销售分析
CREATE MATERIALIZED VIEW product_sales_daily_mv TO product_sales_daily AS
SELECT 
    toDate(order_time) AS date,
    product_id,
    dictGet('products_dict', 'product_name', product_id) AS product_name,
    dictGet('products_dict', 'category', product_id) AS category,
    sum(quantity) AS total_quantity,
    sum(total_amount) AS total_revenue,
    count() AS order_count
FROM orders
WHERE status = 'completed'
GROUP BY date, product_id;
```

### 11.2 IoT数据处理平台

```sql
-- IoT设备表
CREATE TABLE iot_devices_local ON CLUSTER 'iot_cluster' (
    device_id String,
    device_type String,
    location String,
    install_date Date,
    properties String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/iot_devices', '{replica}')
ORDER BY device_id;

-- IoT设备分布式表
CREATE TABLE iot_devices ON CLUSTER 'iot_cluster' AS iot_devices_local
ENGINE = Distributed('iot_cluster', 'iot', 'iot_devices_local', cityHash64(device_id));

-- 传感器数据表
CREATE TABLE sensor_data_local ON CLUSTER 'iot_cluster' (
    device_id String,
    sensor_type String,
    measurement_time DateTime,
    value Float64,
    quality UInt8
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/sensor_data', '{replica}')
PARTITION BY toYYYYMM(measurement_time)
ORDER BY (device_id, sensor_type, measurement_time)
TTL measurement_time + INTERVAL 90 DAY;

-- 传感器数据分布式表
CREATE TABLE sensor_data ON CLUSTER 'iot_cluster' AS sensor_data_local
ENGINE = Distributed('iot_cluster', 'iot', 'sensor_data_local', cityHash64(device_id));

-- 设备状态表
CREATE TABLE device_status_local ON CLUSTER 'iot_cluster' (
    device_id String,
    status String,
    status_time DateTime,
    details String
) ENGINE = ReplacingMergeTree(status_time)
PARTITION BY toYYYYMM(status_time)
ORDER BY (device_id, status_time);

-- 设备状态分布式表
CREATE TABLE device_status ON CLUSTER 'iot_cluster' AS device_status_local
ENGINE = Distributed('iot_cluster', 'iot', 'device_status_local', cityHash64(device_id));

-- 实时监控视图
CREATE MATERIALIZED VIEW device_monitoring_realtime_mv TO device_monitoring_realtime AS
SELECT 
    device_id,
    dictGet('iot_devices_dict', 'device_type', device_id) AS device_type,
    dictGet('iot_devices_dict', 'location', device_id) AS location,
    avgIf(value, quality >= 8) AS avg_value,
    min(value) AS min_value,
    max(value) AS max_value,
    count() AS measurement_count
FROM sensor_data
WHERE measurement_time >= now() - INTERVAL 1 HOUR
GROUP BY device_id;

-- 设备异常检测
CREATE MATERIALIZED VIEW device_anomalies_mv TO device_anomalies AS
SELECT 
    device_id,
    sensor_type,
    measurement_time,
    value,
    -- 简单的异常检测：值偏离历史均值3个标准差
    (value - (SELECT avg(value) FROM sensor_data s2 
              WHERE s2.device_id = sensor_data.device_id 
                AND s2.sensor_type = sensor_data.sensor_type
                AND s2.measurement_time >= sensor_data.measurement_time - INTERVAL 7 DAY)) /
    (SELECT stddevPop(value) FROM sensor_data s2 
     WHERE s2.device_id = sensor_data.device_id 
       AND s2.sensor_type = sensor_data.sensor_type
       AND s2.measurement_time >= sensor_data.measurement_time - INTERVAL 7 DAY) AS z_score
FROM sensor_data
WHERE quality >= 8
HAVING abs(z_score) > 3;
```

## 12. 总结

ClickHouse的分布式引擎和集群管理功能使其能够处理大规模数据分析场景。通过合理设计分片策略、配置副本机制、优化查询性能，可以构建高性能、高可用的分析型数据库系统。

关键要点：
1. **分片设计**：选择合适的分片键，确保数据均匀分布
2. **副本管理**：合理配置副本，提供高可用性和负载均衡
3. **查询优化**：理解分布式查询执行流程，优化查询性能
4. **监控维护**：定期监控集群状态，及时处理故障
5. **扩展规划**：预先规划集群扩容策略

通过掌握这些技术和最佳实践，您可以构建稳定、高效的ClickHouse分布式集群，满足大规模数据分析需求。在下一节中，我们将介绍ClickHouse性能调优的高级技巧，帮助您进一步提升系统性能。