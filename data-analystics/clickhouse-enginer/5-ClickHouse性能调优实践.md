# ClickHouse性能调优实践

ClickHouse作为一个高性能的列式数据库，虽然默认配置已经具有出色的性能，但在实际应用中，通过合理的调优可以进一步提升系统性能。本章详细介绍ClickHouse的各种性能调优技巧和最佳实践。

## 1. 查询性能优化

### 1.1 查询计划分析

ClickHouse提供了强大的查询分析工具，可以帮助理解查询执行过程：

```sql
-- 分析查询执行计划
EXPLAIN 
    SELECT 
        region,
        sum(amount) AS total_revenue,
        count() AS order_count
    FROM sales
    WHERE date >= '2023-01-01'
    GROUP BY region;

-- 分析查询性能
EXPLAIN PIPELINE
    SELECT 
        region,
        sum(amount) AS total_revenue,
        count() AS order_count
    FROM sales
    WHERE date >= '2023-01-01'
    GROUP BY region;

-- 分析查询估算
EXPLAIN ESTIMATE
    SELECT 
        region,
        sum(amount) AS total_revenue,
        count() AS order_count
    FROM sales
    WHERE date >= '2023-01-01'
    GROUP BY region;
```

### 1.2 查询设置优化

通过调整查询设置，可以显著改善查询性能：

```sql
-- 启用并行查询处理
SET max_threads = 8;
SET max_block_size = 65536;
SET max_bytes_before_external_group_by = 10000000000;

-- 优化JOIN操作
SET join_algorithm = 'hash';
SET join_use_nulls = 0;
SET max_bytes_in_join = 10000000000;
SET max_rows_in_join = 1000000;

-- 优化子查询
SET distributed_product_mode = 'global';
SET parallel_replicas_count = 2;
SET parallel_replicas_offset = 0;

-- 优化聚合操作
SET aggregation_memory_efficient_merge_threads = 8;
SET aggregation_memory_efficient_merge_threads_const = 1;
SET max_bytes_before_external_group_by = 10737418240;

-- 限制查询资源使用
SET max_execution_time = 300;
SET max_memory_usage = 10000000000;
SET max_result_bytes = 1000000000;
SET max_result_rows = 1000000;
```

### 1.3 查询重写技巧

通过重写查询语句，可以提高执行效率：

```sql
-- 原始查询：低效
SELECT 
    (SELECT count(*) FROM events WHERE event_type = 'page_view' AND user_id = e.user_id) AS page_views,
    (SELECT count(*) FROM events WHERE event_type = 'click' AND user_id = e.user_id) AS clicks,
    (SELECT count(*) FROM events WHERE event_type = 'purchase' AND user_id = e.user_id) AS purchases
FROM (SELECT DISTINCT user_id FROM events WHERE event_date = today()) e;

-- 优化后的查询：高效
SELECT 
    user_id,
    sumIf(event_type = 'page_view', 1) AS page_views,
    sumIf(event_type = 'click', 1) AS clicks,
    sumIf(event_type = 'purchase', 1) AS purchases
FROM events
WHERE event_date = today()
GROUP BY user_id;

-- 原始查询：使用IN
SELECT 
    product_id,
    product_name
FROM products
WHERE category IN (SELECT category FROM categories WHERE is_active = 1);

-- 优化后的查询：使用JOIN
SELECT 
    p.product_id,
    p.product_name
FROM products p
JOIN categories c ON p.category = c.category
WHERE c.is_active = 1;
```

## 2. 表设计优化

### 2.1 分区策略优化

合理的分区策略是提高查询性能的关键：

```sql
-- 按月分区：适用于中等数据量
CREATE TABLE sales_monthly (
    order_id UInt64,
    customer_id UInt64,
    order_date Date,
    amount Decimal(10, 2),
    region String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)  -- 按月分区
ORDER BY (order_date, customer_id);

-- 按日分区：适用于大数据量
CREATE TABLE events_daily (
    event_id UInt64,
    user_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)  -- 按日分区
ORDER BY (user_id, event_time);

-- 复合分区：适用于复杂场景
CREATE TABLE iot_measurements (
    device_id String,
    sensor_type String,
    measurement_time DateTime,
    value Float64
) ENGINE = MergeTree()
PARTITION BY (toYYYYMM(measurement_time), device_type)  -- 复合分区
ORDER BY (device_id, sensor_type, measurement_time);
```

### 2.2 排序键设计

排序键对查询性能有重要影响：

```sql
-- 单列排序键：简单场景
CREATE TABLE simple_events (
    user_id UInt64,
    event_id UInt64,
    event_time DateTime,
    event_type String
) ENGINE = MergeTree()
ORDER BY user_id;  -- 单列排序键

-- 复合排序键：常见场景
CREATE TABLE user_events (
    user_id UInt64,
    event_id UInt64,
    event_time DateTime,
    event_type String
) ENGINE = MergeTree()
ORDER BY (user_id, event_time, event_type);  -- 复合排序键

-- 带前缀的排序键：优化特定查询
CREATE TABLE sales_optimized (
    customer_id UInt64,
    order_date Date,
    order_time DateTime,
    product_id UInt64,
    amount Decimal(10, 2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (customer_id, order_date, order_time, product_id);  -- 带前缀的排序键
```

### 2.3 主键优化

主键与排序键的关系和优化：

```sql
-- 主键与排序键相同：默认情况
CREATE TABLE events_v1 (
    event_id UInt64,
    user_id UInt64,
    event_time DateTime,
    event_type String
) ENGINE = MergeTree()
ORDER BY (user_id, event_time)
PRIMARY KEY (user_id, event_time);  -- 与排序键相同

-- 主键是排序键的前缀：优化存储
CREATE TABLE events_v2 (
    event_id UInt64,
    user_id UInt64,
    event_time DateTime,
    event_type String
) ENGINE = MergeTree()
ORDER BY (user_id, event_time, event_type)
PRIMARY KEY (user_id, event_time);  -- 排序键的前缀
```

### 2.4 抽样键设计

抽样键可以提高大数据表的查询效率：

```sql
-- 基于时间戳的抽样
CREATE TABLE web_logs (
    timestamp DateTime,
    url String,
    user_id UInt64,
    ip_address String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, url, user_id)
SAMPLE BY intHash64(user_id);  -- 基于用户ID的抽样

-- 复合抽样键
CREATE TABLE sensor_data (
    device_id String,
    measurement_time DateTime,
    value Float64,
    quality UInt8
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(measurement_time)
ORDER BY (device_id, measurement_time)
SAMPLE BY (device_id, intHash64(measurement_time));  -- 复合抽样键
```

## 3. 存储优化

### 3.1 编压缩优化

选择合适的编压缩算法可以显著减少存储空间：

```sql
-- 使用LZ4压缩：平衡速度和压缩率
CREATE TABLE events_lz4 (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
SETTINGS compression = {'event_type': 'LZ4', 'properties': 'LZ4HC(9)'};

-- 使用ZSTD压缩：高压缩率
CREATE TABLE events_zstd (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
SETTINGS compression = {'event_type': 'ZSTD(10)', 'properties': 'ZSTD(12)'};

-- 自定义压缩策略
CREATE TABLE events_custom (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String,
    user_id UInt64
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
SETTINGS compression = {
    'event_id': 'NONE',          -- 不压缩ID列
    'event_time': 'Delta,ZSTD',  -- 先使用Delta编码，再使用ZSTD
    'event_type': 'LZ4',         -- 低基数列使用LZ4
    'properties': 'ZSTD(12)',    -- 高基数列使用高压缩率ZSTD
    'user_id': 'ZSTD'            -- 用户ID使用标准ZSTD
};
```

### 3.2 索引优化

ClickHouse支持多种索引类型：

```sql
-- 跳过索引：跳过不满足条件的数据块
CREATE TABLE events_skip_index (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    user_id UInt64
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
INDEX idx_event_type event_type TYPE minmax GRANULARITY 3  -- 最小值/最大值索引
INDEX idx_user_id user_id TYPE set(0) GRANULARITY 1       -- 集合索引
INDEX idx_event_type_bloom event_type TYPE bloom_filter GRANULARITY 1;  -- 布隆过滤器索引

-- 条件跳过索引：基于条件跳过数据块
CREATE TABLE events_conditional_index (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    user_id UInt64,
    value Float64
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
INDEX idx_high_value value > 1000 TYPE minmax GRANULARITY 1  -- 条件索引
INDEX idx_recent_event event_time > (now() - INTERVAL 1 DAY) TYPE minmax GRANULARITY 1;  -- 时间条件索引

-- 令牌索引：用于文本搜索
CREATE TABLE pages (
    url String,
    title String,
    content String,
    crawl_time DateTime
) ENGINE = MergeTree()
ORDER BY (crawl_time, url)
INDEX idx_title_tokens title TYPE tokenbf_v1(256, 2, 0) GRANULARITY 1  -- 令牌布隆过滤器
INDEX idx_content_tokens content TYPE tokenbf_v1(256, 4, 0) GRANULARITY 4;  -- 更精细的令牌索引
```

### 3.3 存储引擎选择

根据场景选择合适的存储引擎：

```sql
-- MergeTree：通用分析场景
CREATE TABLE sales (
    order_id UInt64,
    customer_id UInt64,
    order_date Date,
    amount Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (order_date, order_id);

-- ReplacingMergeTree：需要去重的场景
CREATE TABLE user_status (
    user_id UInt64,
    status String,
    update_time DateTime,
    version UInt64
) ENGINE = ReplacingMergeTree(version)
ORDER BY user_id;

-- SummingMergeTree：预聚合场景
CREATE TABLE daily_counters (
    date Date,
    counter_name String,
    value UInt64
) ENGINE = SummingMergeTree(value)
ORDER BY (date, counter_name);

-- AggregatingMergeTree：复杂聚合场景
CREATE TABLE user_behavior_daily (
    date Date,
    activity_type String,
    unique_users AggregateFunction(uniq, UInt64),
    page_views AggregateFunction(sum, UInt64)
) ENGINE = AggregatingMergeTree()
ORDER BY (date, activity_type);
```

## 4. 写入性能优化

### 4.1 批量插入优化

批量插入是提高写入性能的关键：

```sql
-- 小批量插入：不推荐
INSERT INTO events (event_id, user_id, event_time, event_type) 
VALUES (1, 100, now(), 'page_view');

-- 大批量插入：推荐
INSERT INTO events (event_id, user_id, event_time, event_type) 
VALUES (1, 100, now(), 'page_view'),
       (2, 101, now(), 'click'),
       (3, 102, now(), 'purchase');

-- 从文件批量插入：更高效
INSERT INTO events FORMAT CSV
event_id,user_id,event_time,event_type
1,100,"2023-01-01 10:00:00",page_view
2,101,"2023-01-01 10:00:01",click
3,102,"2023-01-01 10:00:02",purchase
;

-- 设置批量插入大小
SET max_insert_block_size = 1048576;  -- 块大小
SET max_threads = 8;                  -- 线程数
SET max_bytes_before_external_sort = 10737418240;  -- 外部排序阈值
```

### 4.2 异步插入配置

配置异步插入可以提高写入吞吐量：

```xml
<!-- config.xml中的异步插入配置 -->
<async_insert>
    <!-- 启用异步插入 -->
    <enable>1</enable>
    
    <!-- 数据堆积时间阈值，超过则强制插入 -->
    <max_data_size>1000000</max_data_size>
    
    <!-- 时间阈值，超过则强制插入 -->
    <busy_timeout_ms>1000</busy_timeout_ms>
    
    <!-- 异步插入队列最大大小 -->
    <max_size>10000</max_size>
</async_insert>
```

### 4.3 缓冲表优化

使用缓冲表提高写入性能：

```sql
-- 创建缓冲表
CREATE TABLE sales_buffer (
    order_id UInt64,
    customer_id UInt64,
    order_date Date,
    amount Decimal(10, 2)
) ENGINE = Buffer(default, sales, 16, 10, 100, 10000, 1000000, 10000000);

-- 缓冲表参数解释
-- 16: 最小层数
-- 10: 最大层数
-- 100: 最小时间（秒）
-- 10000: 最大时间（秒）
-- 1000000: 最小行数
-- 10000000: 最大行数

-- 创建目标表
CREATE TABLE sales (
    order_id UInt64,
    customer_id UInt64,
    order_date Date,
    amount Decimal(10, 2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_date, order_id);
```

### 4.4 插入性能监控

监控插入性能：

```sql
-- 查看插入性能
SELECT 
    query_id,
    event_time,
    query_duration_ms,
    read_rows,
    written_rows,
    read_bytes,
    written_bytes
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE 'INSERT INTO%'
ORDER BY query_duration_ms DESC
LIMIT 10;

-- 查看插入队列状态
SELECT 
    database,
    table,
    min_age,
    max_age,
    max_bytes,
    max_rows,
    actual_bytes,
    actual_rows
FROM system.buffer_tables
ORDER BY actual_rows DESC;
```

## 5. 合并与TTL优化

### 5.1 合并策略优化

控制合并过程可以优化性能：

```sql
-- 设置合并参数
ALTER TABLE events 
MODIFY SETTING 
    min_bytes_for_wide_part = 100000000,      -- 使用宽格式的最小字节大小
    max_bytes_for_wide_part = 1073741824,      -- 使用宽格式的最大字节大小
    min_rows_for_wide_part = 1048576,          -- 使用宽格式的最小行数
    max_rows_for_wide_part = 10485760,         -- 使用宽格式的最大行数
    merge_max_block_size = 8192,                -- 合并块大小
    merge_min_bytes_for_consecutive_read = 10485760,  -- 连续读取的最小字节数
    parts_to_delay_insert = 150,                -- 延迟插入的部件数阈值
    parts_to_throw_insert = 300,               -- 抛出异常的部件数阈值
    max_parts_to_merge_at_once = 10;            -- 一次合并的最大部件数

-- 手动触发合并
OPTIMIZE TABLE events FINAL;                   -- 立即合并所有部件
OPTIMIZE TABLE events PARTITION '202301';       -- 合并特定分区
OPTIMIZE TABLE DEDUPLICATE;                    -- 去重合并

-- 查看待合并的部件
SELECT 
    partition,
    count() AS part_count,
    sum(rows) AS total_rows,
    sum(data_uncompressed_bytes) AS uncompressed_bytes,
    sum(data_compressed_bytes) AS compressed_bytes
FROM system.parts
WHERE table = 'events'
  AND active = 1
GROUP BY partition
ORDER BY partition;
```

### 5.2 TTL策略优化

合理设置TTL可以自动管理数据生命周期：

```sql
-- 基本TTL：按时间删除数据
CREATE TABLE events_with_ttl (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
TTL event_time + INTERVAL 90 DAY;  -- 90天后删除数据

-- 复杂TTL：条件删除
CREATE TABLE events_complex_ttl (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String,
    is_important Boolean
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
TTL 
    event_time + INTERVAL 30 DAY DELETE WHERE event_type = 'page_view',
    event_time + INTERVAL 90 DAY DELETE WHERE event_type = 'click',
    event_time + INTERVAL 180 DAY DELETE WHERE event_type = 'purchase',
    event_time + INTERVAL 365 DAY DELETE WHERE is_important = 0,
    event_time + INTERVAL 3 YEAR;  -- 默认删除时间

-- TTL移动到冷存储
CREATE TABLE events_cold_storage (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
TTL 
    event_time + INTERVAL 30 DAY TO DISK 'cold',
    event_time + INTERVAL 90 DAY DELETE;

-- TTL重新压缩
CREATE TABLE events_recompress (
    event_id UInt64,
    event_time DateTime,
    event_type String,
    properties String
) ENGINE = MergeTree()
ORDER BY (event_time, event_id)
TTL 
    event_time + INTERVAL 7 DAY RECOMPRESS CODEC (ZSTD(6)),
    event_time + INTERVAL 30 DAY RECOMPRESS CODEC (ZSTD(12));

-- 设置TTL运行间隔
SET merge_with_ttl_timeout = 3600;  -- TTL检查间隔（秒）
```

### 5.3 后台任务优化

控制后台任务可以避免资源竞争：

```xml
<!-- config.xml中的后台任务配置 -->
<background_executor_pool>
    <!-- 后台任务大小 -->
    <size>16</size>
    
    <!-- 任务最大执行时间 -->
    <task_max_execution_time_ms>600000</task_max_execution_time_ms>
</background_executor_pool>

<background_schedule_pool>
    <!-- 调度任务池大小 -->
    <size>8</size>
</background_schedule_pool>
```

## 6. 内存管理优化

### 6.1 查询内存控制

控制查询内存使用可以避免系统内存耗尽：

```sql
-- 查询级别内存设置
SET max_memory_usage = 10000000000;        -- 10GB
SET max_memory_usage_for_user = 0;         -- 0表示无限制
SET max_memory_usage_for_all_queries = 0; -- 0表示无限制

-- 聚合内存设置
SET max_bytes_before_external_group_by = 5000000000;  -- 5GB
SET max_bytes_before_external_sort = 5000000000;      -- 5GB

-- JOIN内存设置
SET max_bytes_in_join = 5000000000;          -- 5GB
SET max_rows_in_join = 10000000;             -- 1000万行

-- 表函数内存设置
SET max_bytes_in_external_tables = 5000000000; -- 5GB
SET max_rows_in_external_tables = 10000000;    -- 1000万行

-- 监控内存使用
SELECT 
    query_id,
    initial_user,
    query,
    memory_usage,
    peak_memory_usage,
    read_rows,
    result_rows
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND memory_usage > 0
ORDER BY memory_usage DESC
LIMIT 10;
```

### 6.2 系统内存优化

系统级别的内存优化：

```xml
<!-- config.xml中的内存配置 -->
<max_memory_usage>10000000000</max_memory_usage>          <!-- 10GB -->
<max_memory_usage_for_user>0</max_memory_usage_for_user>  <!-- 0表示无限制 -->
<max_memory_usage_for_all_queries>0</max_memory_usage_for_all_queries>

<max_bytes_before_external_group_by>5000000000</max_bytes_before_external_group_by>  <!-- 5GB -->
<max_bytes_before_external_sort>5000000000</max_bytes_before_external_sort>          <!-- 5GB -->

<max_bytes_in_join>5000000000</max_bytes_in_join>            <!-- 5GB -->
<max_rows_in_join>10000000</max_rows_in_join>               <!-- 1000万行 -->

<max_bytes_in_external_tables>5000000000</max_bytes_in_external_tables>  <!-- 5GB -->
<max_rows_in_external_tables>10000000</max_rows_in_external_tables>     <!-- 1000万行 -->
```

## 7. 分布式查询优化

### 7.1 分布式聚合优化

优化分布式聚合可以提高查询性能：

```sql
-- 分布式聚合设置
SET distributed_aggregation_memory_efficient = 1;          -- 内存高效聚合
SET distributed_aggregation_memory_efficient_merge_threads = 4;  -- 聚合合并线程数

-- 两阶段聚合
SELECT 
    region,
    sum(total_amount) AS total_revenue
FROM (
    SELECT 
        region,
        sum(amount) AS total_amount
    FROM distributed_sales
    WHERE date >= '2023-01-01'
    GROUP BY region, date
)
GROUP BY region;

-- 远程聚合
SELECT 
    region,
    sum(total_amount) AS total_revenue
FROM remote('ch1.example.com,ch2.example.com', default, local_sales)
WHERE date >= '2023-01-01'
GROUP BY region;
```

### 7.2 分布式JOIN优化

优化分布式JOIN操作：

```sql
-- 分布式JOIN设置
SET distributed_product_mode = 'global';   -- 全局JOIN
SET prefer_localhost_replica = 1;         -- 优先使用本地副本
SET use_compact_format_in_distributed_participants = 1;  -- 使用紧凑格式

-- 同分片JOIN（推荐）
CREATE TABLE orders (
    order_id UInt64,
    customer_id UInt64,
    order_date Date,
    amount Decimal(10, 2)
) ENGINE = Distributed('cluster', 'default', 'local_orders', cityHash64(customer_id));

CREATE TABLE customers (
    customer_id UInt64,
    name String,
    region String
) ENGINE = Distributed('cluster', 'default', 'local_customers', cityHash64(customer_id));

-- 同分片JOIN
SELECT 
    o.order_id,
    c.name,
    o.amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
```

### 7.3 分布式查询调优

分布式查询通用调优：

```sql
-- 分布式查询设置
SET max_distributed_connections = 1024;           -- 最大连接数
SET connect_timeout = 10;                         -- 连接超时
SET receive_timeout = 300;                        -- 接收超时
SET send_timeout = 300;                           -- 发送超时

-- 复制查询
SET parallel_replicas_count = 2;                  -- 并行副本数
SET parallel_replicas_offset = 0;                 -- 副本偏移

-- 分布式DDL
SET distributed_ddl_task_timeout = 180;           -- DDL任务超时

-- 查询路由
SET optimize_skip_unused_shards = 1;              -- 跳过未使用的分片
SET force_optimize_skip_unused_shards = 1;        -- 强制跳过未使用的分片
```

## 8. 系统配置优化

### 8.1 服务器配置

服务器级别的性能优化：

```xml
<!-- config.xml中的服务器配置 -->
<!-- 线程配置 -->
<max_threads>8</max_threads>
<max_background_threads>8</max_background_threads>
<background_fetches_pool_size>8</background_fetches_pool_size>
<background_merges_mutations_concurrency_mutex>4</background_merges_mutations_concurrency_mutex>

<!-- 内存配置 -->
<max_memory_usage>10000000000</max_memory_usage>
<mark_cache_size>10737418240</mark_cache_size>
<uncompressed_cache_size>8589934592</uncompressed_cache_size>

<!-- 文件系统配置 -->
<max_open_files>262144</max_open_files>
<max_table_size_to_drop>0</max_table_size_to_drop>
<max_partition_size_to_drop>50000000000</max_partition_size_to_drop>

<!-- 网络配置 -->
<tcp_port>9000</tcp_port>
<http_port>8123</http_port>
<interserver_http_port>9009</interserver_http_port>
<max_connections>4096</max_connections>
<keep_alive_timeout>3</keep_alive_timeout>
```

### 8.2 内核参数调优

操作系统内核参数调优：

```bash
# /etc/sysctl.conf

# 网络参数
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# 文件描述符限制
fs.file-max = 2097152

# 虚拟内存参数
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# 透明大页面
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

### 8.3 磁盘I/O优化

磁盘I/O优化：

```xml
<!-- config.xml中的磁盘配置 -->
<storage_configuration>
    <disks>
        <default>
            <path>/var/lib/clickhouse/</path>
            <keep_free_space_bytes>10737418240</keep_free_space_bytes>
        </default>
        
        <!-- 不同类型的磁盘 -->
        <fast_disk>
            <path>/mnt/ssd/clickhouse/</path>
            <keep_free_space_bytes>10737418240</keep_free_space_bytes>
        </fast_disk>
        
        <cold_disk>
            <path>/mnt/hdd/clickhouse/</path>
            <keep_free_space_bytes>10737418240</keep_free_space_bytes>
        </cold_disk>
    </disks>
    
    <policies>
        <default>
            <volumes>
                <default>
                    <disk>default</disk>
                </default>
            </volumes>
        </default>
        
        <hot_cold_policy>
            <volumes>
                <hot>
                    <disk>fast_disk</disk>
                </hot>
                <cold>
                    <disk>cold_disk</disk>
                    <max_data_part_size_bytes>1073741824</max_data_part_size_bytes>
                </cold>
            </volumes>
            <move_factor>0.1</move_factor>
        </hot_cold_policy>
    </policies>
</storage_configuration>
```

## 9. 性能监控与分析

### 9.1 查询性能监控

监控查询性能：

```sql
-- 查询统计
SELECT 
    type,
    count() AS query_count,
    avg(query_duration_ms) AS avg_duration,
    max(query_duration_ms) AS max_duration,
    sum(read_rows) AS total_read_rows,
    sum(read_bytes) AS total_read_bytes,
    sum(result_rows) AS total_result_rows,
    sum(result_bytes) AS total_result_bytes
FROM system.query_log
WHERE event_date = today()
  AND type IN ('QueryStart', 'QueryFinish')
GROUP BY type;

-- 慢查询
SELECT 
    query_id,
    query_duration_ms,
    query,
    read_rows,
    written_rows,
    read_bytes,
    written_bytes,
    memory_usage
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query_duration_ms > 5000
ORDER BY query_duration_ms DESC
LIMIT 10;

-- 错误查询
SELECT 
    query_id,
    query_duration_ms,
    exception,
    exception_code,
    stack_trace
FROM system.query_log
WHERE event_date = today()
  AND type = 'Exception'
ORDER BY event_time DESC
LIMIT 10;
```

### 9.2 表性能监控

监控表性能：

```sql
-- 表大小统计
SELECT 
    database,
    table,
    engine,
    sum(rows) AS total_rows,
    sum(data_uncompressed_bytes) / 1024 / 1024 / 1024 AS uncompressed_gb,
    sum(data_compressed_bytes) / 1024 / 1024 / 1024 AS compressed_gb,
    1 - sum(data_compressed_bytes) / sum(data_uncompressed_bytes) AS compression_ratio
FROM system.parts
WHERE active = 1
GROUP BY database, table, engine
ORDER BY uncompressed_gb DESC;

-- 表部件统计
SELECT 
    database,
    table,
    partition,
    count() AS part_count,
    sum(rows) AS total_rows,
    sum(data_uncompressed_bytes) / 1024 / 1024 AS uncompressed_mb,
    sum(data_compressed_bytes) / 1024 / 1024 AS compressed_mb
FROM system.parts
WHERE active = 1
GROUP BY database, table, partition
ORDER BY part_count DESC;

-- 表查询热度
SELECT 
    table,
    count() AS query_count,
    avg(query_duration_ms) AS avg_duration,
    sum(read_rows) AS total_read_rows,
    sum(read_bytes) AS total_read_bytes
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND table != ''
GROUP BY table
ORDER BY query_count DESC;
```

### 9.3 系统性能监控

监控系统性能：

```sql
-- CPU使用情况
SELECT 
    hostname,
    uptime(),
    formatReadableSize(os_memory_total) AS total_memory,
    formatReadableSize(os_memory_free) AS free_memory,
    formatReadableSize(system.cpu_usage_user) AS cpu_user,
    formatReadableSize(system.cpu_usage_system) AS cpu_system
FROM system.metrics
WHERE metric LIKE '%cpu%' OR metric LIKE '%memory%';

-- 磁盘使用情况
SELECT 
    name,
    path,
    formatReadableSize(free_space) AS free_space,
    formatReadableSize(total_space) AS total_space,
    formatReadableSize(keep_free_space) AS keep_free_space
FROM system.disks;

-- 缓存使用情况
SELECT 
    formatReadableSize(mark_cache_size) AS mark_cache_size,
    formatReadableSize(uncompressed_cache_size) AS uncompressed_cache_size,
    mark_cache_hits / (mark_cache_hits + mark_cache_misses) AS mark_cache_hit_rate,
    uncompressed_cache_hits / (uncompressed_cache_hits + uncompressed_cache_misses) AS uncompressed_cache_hit_rate
FROM system.metrics
WHERE metric IN ('MarkCacheBytes', 'UncompressedCacheBytes');
```

## 10. 常见性能问题诊断

### 10.1 查询慢诊断

诊断查询慢的原因：

```sql
-- 查看查询执行计划
EXPLAIN PIPELINE SELECT 
    region,
    sum(amount) AS total_amount
FROM sales
WHERE date >= '2023-01-01'
GROUP BY region;

-- 查看查询资源使用
SELECT 
    query_id,
    thread_id,
    elapsed_ns,
    read_rows,
    read_bytes,
    written_rows,
    written_bytes,
    memory_usage,
    peak_memory_usage
FROM system.query_thread_log
WHERE event_date = today()
  AND query_id = 'query_id_here'
ORDER BY elapsed_ns DESC;
```

### 10.2 写入慢诊断

诊断写入慢的原因：

```sql
-- 查看插入性能
SELECT 
    query_id,
    query_duration_ms,
    written_rows,
    written_bytes,
    result_rows,
    result_bytes
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE 'INSERT INTO%'
ORDER BY query_duration_ms DESC;

-- 查看合并情况
SELECT 
    database,
    table,
    count() AS parts_count,
    sum(rows) AS total_rows,
    sum(data_uncompressed_bytes) AS uncompressed_bytes,
    sum(data_compressed_bytes) AS compressed_bytes
FROM system.parts
WHERE active = 1
GROUP BY database, table
HAVING parts_count > 50
ORDER BY parts_count DESC;
```

### 10.3 内存使用诊断

诊断内存使用问题：

```sql
-- 查看内存使用情况
SELECT 
    query_id,
    initial_user,
    query,
    memory_usage,
    peak_memory_usage,
    read_rows,
    written_rows
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND memory_usage > 1000000000  -- 大于1GB
ORDER BY memory_usage DESC;

-- 查看服务器内存使用
SELECT 
    metric,
    value,
    formatReadableSize(value) AS readable_value
FROM system.asynchronous_metrics
WHERE metric LIKE '%Memory%'
ORDER BY value DESC;
```

## 11. 性能测试与基准

### 11.1 查询性能测试

```sql
-- 创建测试表
CREATE TABLE test_table (
    id UInt64,
    date Date,
    user_id UInt64,
    event_type String,
    value Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id, event_type);

-- 生成测试数据
INSERT INTO test_table
SELECT 
    number AS id,
    toDate('2020-01-01') + intDiv(number, 1000000) AS date,
    number % 1000000 AS user_id,
    ['click', 'view', 'purchase', 'login'][number % 4 + 1] AS event_type,
    rand() AS value
FROM numbers(100000000);

-- 测试查询
SELECT 
    event_type,
    count() AS event_count,
    avg(value) AS avg_value
FROM test_table
WHERE date BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY event_type
ORDER BY event_count DESC;
```

### 11.2 写入性能测试

```sql
-- 批量写入测试
SET max_insert_block_size = 1048576;
SET max_threads = 8;

INSERT INTO test_table
SELECT 
    number AS id,
    toDate('2020-01-01') + intDiv(number, 1000000) AS date,
    number % 1000000 AS user_id,
    ['click', 'view', 'purchase', 'login'][number % 4 + 1] AS event_type,
    rand() AS value
FROM numbers(10000000);

-- 测试写入速度
SELECT 
    query_duration_ms,
    written_rows,
    written_rows / (query_duration_ms / 1000) AS rows_per_second
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE 'INSERT INTO test_table%'
ORDER BY query_duration_ms DESC
LIMIT 1;
```

## 12. 总结

ClickHouse性能调优是一个综合性的过程，涉及查询优化、表设计、存储配置、系统设置等多个方面。通过合理的调优，可以显著提高系统性能，满足大规模数据分析需求。

关键调优要点：

1. **查询优化**：合理使用查询设置，重写低效查询
2. **表设计**：优化分区策略、排序键和主键设计
3. **存储优化**：选择合适的编压缩算法和索引策略
4. **写入优化**：使用批量插入和缓冲表提高写入性能
5. **合并优化**：控制合并过程，避免资源竞争
6. **内存管理**：合理设置内存限制，避免内存耗尽
7. **分布式优化**：优化分布式查询和JOIN操作
8. **系统配置**：调整服务器和系统参数，提高整体性能
9. **监控分析**：持续监控性能指标，及时发现和解决问题

通过掌握这些调优技巧和最佳实践，您可以构建高性能、高稳定性的ClickHouse分析系统，满足各种复杂的数据分析需求。