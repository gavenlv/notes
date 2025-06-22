-- Day 8: ClickHouse 集群管理和分布式示例
-- =============================================

-- 1. 集群状态检查
-- =============================================

-- 检查集群配置
SELECT 'Cluster Configuration Check' as demo_section;
SELECT 
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    is_local,
    user,
    errors_count,
    slowdowns_count
FROM system.clusters 
ORDER BY cluster, shard_num, replica_num;

-- 检查当前节点信息
SELECT 'Current Node Information' as demo_section;
SELECT 
    hostName() as hostname,
    version() as clickhouse_version,
    uptime() as uptime_seconds,
    formatReadableSize(total_memory) as total_memory
FROM system.one;

-- 2. 分布式表创建演示
-- =============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS cluster_demo;
USE cluster_demo;

-- 创建本地表（模拟集群环境，在单机上演示）
DROP TABLE IF EXISTS user_events_local;
CREATE TABLE user_events_local (
    user_id UInt32,
    event_date Date,
    event_type String,
    page_url String,
    session_id String,
    country String,
    device_type String,
    revenue Decimal(10, 2),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (user_id, event_date, created_at)
SETTINGS index_granularity = 8192;

-- 创建分布式表（单机模拟）
DROP TABLE IF EXISTS user_events_distributed;
CREATE TABLE user_events_distributed AS user_events_local
ENGINE = Distributed('default', 'cluster_demo', 'user_events_local', cityHash64(user_id));

-- 验证表创建
SELECT 'Table Creation Verification' as demo_section;
SELECT 
    database,
    name,
    engine,
    partition_key,
    sorting_key,
    primary_key
FROM system.tables 
WHERE database = 'cluster_demo'
ORDER BY name;

-- 3. 数据插入和分布演示
-- =============================================

-- 插入测试数据
SELECT 'Data Insertion Demo' as demo_section;
INSERT INTO user_events_local VALUES
(1001, '2024-01-01', 'page_view', '/home', 'sess_001', 'China', 'mobile', 0.00, '2024-01-01 10:00:00'),
(1002, '2024-01-01', 'purchase', '/product/123', 'sess_002', 'USA', 'desktop', 99.99, '2024-01-01 10:05:00'),
(1003, '2024-01-01', 'page_view', '/category', 'sess_003', 'Japan', 'tablet', 0.00, '2024-01-01 10:10:00'),
(1004, '2024-01-01', 'purchase', '/product/456', 'sess_004', 'Germany', 'mobile', 149.99, '2024-01-01 10:15:00'),
(1005, '2024-01-01', 'page_view', '/search', 'sess_005', 'UK', 'desktop', 0.00, '2024-01-01 10:20:00');

-- 通过分布式表插入数据
INSERT INTO user_events_distributed VALUES
(2001, '2024-01-02', 'page_view', '/home', 'sess_101', 'France', 'mobile', 0.00, '2024-01-02 10:00:00'),
(2002, '2024-01-02', 'purchase', '/product/789', 'sess_102', 'Canada', 'desktop', 199.99, '2024-01-02 10:05:00'),
(2003, '2024-01-02', 'page_view', '/about', 'sess_103', 'Australia', 'tablet', 0.00, '2024-01-02 10:10:00');

-- 生成大量测试数据
INSERT INTO user_events_local 
SELECT 
    number % 1000 + 3000 as user_id,
    toDate('2024-01-03') + toIntervalDay(number % 7) as event_date,
    ['page_view', 'purchase', 'add_to_cart', 'checkout'][number % 4 + 1] as event_type,
    ['/home', '/product', '/category', '/search', '/checkout'][number % 5 + 1] as page_url,
    'sess_' || toString(number + 1000) as session_id,
    ['China', 'USA', 'Japan', 'Germany', 'UK', 'France', 'Canada'][number % 7 + 1] as country,
    ['mobile', 'desktop', 'tablet'][number % 3 + 1] as device_type,
    CASE 
        WHEN event_type = 'purchase' THEN round((number % 200) + 50, 2)
        ELSE 0.00 
    END as revenue,
    toDateTime('2024-01-03 10:00:00') + toIntervalSecond(number * 10) as created_at
FROM numbers(10000);

-- 验证数据插入
SELECT 'Data Verification' as demo_section;
SELECT 
    'Local Table' as table_type,
    count() as total_records,
    count(DISTINCT user_id) as unique_users,
    sum(revenue) as total_revenue
FROM user_events_local
UNION ALL
SELECT 
    'Distributed Table' as table_type,
    count() as total_records,
    count(DISTINCT user_id) as unique_users,
    sum(revenue) as total_revenue
FROM user_events_distributed;

-- 4. 分片键效果演示
-- =============================================

-- 不同分片键的数据分布对比
SELECT 'Sharding Key Comparison' as demo_section;

-- 模拟不同分片键的哈希分布
SELECT 
    'Random Sharding' as sharding_method,
    rand() % 4 as shard_id,
    count() as record_count
FROM user_events_local 
GROUP BY shard_id
ORDER BY shard_id

UNION ALL

SELECT 
    'User ID Sharding' as sharding_method,
    user_id % 4 as shard_id,
    count() as record_count
FROM user_events_local 
GROUP BY shard_id
ORDER BY shard_id

UNION ALL

SELECT 
    'Hash Sharding' as sharding_method,
    cityHash64(user_id) % 4 as shard_id,
    count() as record_count
FROM user_events_local 
GROUP BY shard_id
ORDER BY shard_id;

-- 5. 分布式查询优化演示
-- =============================================

-- 创建用户画像表用于JOIN演示
DROP TABLE IF EXISTS user_profiles_local;
CREATE TABLE user_profiles_local (
    user_id UInt32,
    username String,
    email String,
    age UInt8,
    country String,
    registration_date Date,
    is_premium UInt8
) ENGINE = MergeTree()
ORDER BY user_id;

-- 插入用户画像数据
INSERT INTO user_profiles_local 
SELECT 
    number + 1000 as user_id,
    'user_' || toString(number + 1000) as username,
    'user' || toString(number + 1000) || '@example.com' as email,
    (number % 50) + 18 as age,
    ['China', 'USA', 'Japan', 'Germany', 'UK', 'France', 'Canada'][number % 7 + 1] as country,
    toDate('2023-01-01') + toIntervalDay(number % 365) as registration_date,
    number % 10 = 0 as is_premium
FROM numbers(5000);

-- 创建用户画像分布式表
DROP TABLE IF EXISTS user_profiles_distributed;
CREATE TABLE user_profiles_distributed AS user_profiles_local
ENGINE = Distributed('default', 'cluster_demo', 'user_profiles_local', cityHash64(user_id));

-- 分布式JOIN查询演示
SELECT 'Distributed JOIN Demo' as demo_section;

-- 普通JOIN（可能性能较差）
SELECT 
    'Regular JOIN' as join_type,
    count() as result_count,
    sum(e.revenue) as total_revenue
FROM user_events_distributed e
JOIN user_profiles_distributed p ON e.user_id = p.user_id
WHERE e.event_date >= '2024-01-01'
  AND p.is_premium = 1;

-- 使用GLOBAL优化的JOIN
SELECT 
    'GLOBAL JOIN' as join_type,
    count() as result_count,
    sum(e.revenue) as total_revenue
FROM user_events_distributed e
JOIN GLOBAL user_profiles_distributed p ON e.user_id = p.user_id
WHERE e.event_date >= '2024-01-01'
  AND p.is_premium = 1;

-- 6. 聚合查询性能对比
-- =============================================

-- 创建预聚合表
DROP TABLE IF EXISTS daily_analytics_local;
CREATE TABLE daily_analytics_local (
    event_date Date,
    country String,
    device_type String,
    event_type String,
    total_events UInt32,
    unique_users UInt32,
    total_revenue Decimal(12, 2)
) ENGINE = SummingMergeTree((total_events, unique_users, total_revenue))
ORDER BY (event_date, country, device_type, event_type)
PARTITION BY toYYYYMM(event_date);

-- 创建物化视图进行实时聚合
CREATE MATERIALIZED VIEW daily_analytics_mv TO daily_analytics_local AS
SELECT 
    event_date,
    country,
    device_type,
    event_type,
    count() as total_events,
    uniq(user_id) as unique_users,
    sum(revenue) as total_revenue
FROM user_events_local
GROUP BY event_date, country, device_type, event_type;

-- 触发物化视图计算（插入新数据）
INSERT INTO user_events_local VALUES
(9001, '2024-01-10', 'purchase', '/product/premium', 'sess_9001', 'China', 'mobile', 299.99, '2024-01-10 15:00:00'),
(9002, '2024-01-10', 'purchase', '/product/standard', 'sess_9002', 'USA', 'desktop', 199.99, '2024-01-10 15:05:00');

-- 查看聚合结果
SELECT 'Pre-aggregated Analytics' as demo_section;
SELECT * FROM daily_analytics_local 
WHERE event_date = '2024-01-10'
ORDER BY total_revenue DESC;

-- 7. 系统表监控演示
-- =============================================

-- 查看表的存储信息
SELECT 'Table Storage Information' as demo_section;
SELECT 
    database,
    table,
    sum(rows) as total_rows,
    formatReadableSize(sum(data_compressed_bytes)) as compressed_size,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed_size,
    round(sum(data_compressed_bytes) / sum(data_uncompressed_bytes), 3) as compression_ratio
FROM system.parts 
WHERE database = 'cluster_demo'
  AND active = 1
GROUP BY database, table
ORDER BY total_rows DESC;

-- 查看分区信息
SELECT 'Partition Information' as demo_section;
SELECT 
    table,
    partition,
    rows,
    formatReadableSize(bytes_on_disk) as size_on_disk,
    min_date,
    max_date
FROM system.parts 
WHERE database = 'cluster_demo'
  AND table = 'user_events_local'
  AND active = 1
ORDER BY partition;

-- 查看查询统计
SELECT 'Query Statistics' as demo_section;
SELECT 
    type,
    count() as query_count,
    avg(query_duration_ms) as avg_duration_ms,
    quantile(0.95)(query_duration_ms) as p95_duration_ms,
    sum(read_rows) as total_read_rows,
    formatReadableSize(sum(read_bytes)) as total_read_bytes
FROM system.query_log 
WHERE event_date = today()
  AND type IN ('QueryStart', 'QueryFinish')
  AND query NOT LIKE '%system.%'
GROUP BY type;

-- 8. 模拟集群故障和恢复
-- =============================================

-- 创建副本表（模拟环境）
DROP TABLE IF EXISTS user_events_replica;
CREATE TABLE user_events_replica AS user_events_local
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (user_id, event_date, created_at);

-- 同步数据到副本
INSERT INTO user_events_replica SELECT * FROM user_events_local;

-- 验证副本数据一致性
SELECT 'Replica Consistency Check' as demo_section;
SELECT 
    'Primary' as replica_type,
    count() as record_count,
    sum(revenue) as total_revenue,
    max(created_at) as last_update
FROM user_events_local
UNION ALL
SELECT 
    'Replica' as replica_type,
    count() as record_count,
    sum(revenue) as total_revenue,
    max(created_at) as last_update
FROM user_events_replica;

-- 9. 性能基准测试
-- =============================================

-- 大数据量查询测试
SELECT 'Performance Benchmark' as demo_section;

-- 简单聚合查询
SELECT 
    'Simple Aggregation' as query_type,
    count() as record_count,
    now() as query_time
FROM user_events_local;

-- 复杂分组聚合查询
SELECT 
    'Complex Aggregation' as query_type,
    count() as group_count,
    now() as query_time
FROM (
    SELECT 
        country,
        device_type,
        toYYYYMM(event_date) as month,
        count() as events,
        sum(revenue) as revenue,
        uniq(user_id) as unique_users
    FROM user_events_local 
    GROUP BY country, device_type, month
    HAVING events > 10
);

-- 10. 清理和总结
-- =============================================

-- 表优化
OPTIMIZE TABLE user_events_local FINAL;
OPTIMIZE TABLE daily_analytics_local FINAL;

-- 最终统计报告
SELECT '=== Day 8 Cluster Demo Summary ===' as summary_section;

SELECT 
    'Tables Created' as metric,
    toString(count()) as value
FROM system.tables 
WHERE database = 'cluster_demo'

UNION ALL

SELECT 
    'Total Records' as metric,
    toString(sum(total_rows)) as value
FROM system.tables 
WHERE database = 'cluster_demo'
  AND engine LIKE '%MergeTree%'

UNION ALL

SELECT 
    'Storage Used' as metric,
    formatReadableSize(sum(total_bytes)) as value
FROM system.tables 
WHERE database = 'cluster_demo'
  AND engine LIKE '%MergeTree%'

UNION ALL

SELECT 
    'Countries Covered' as metric,
    toString(uniq(country)) as value
FROM user_events_local

UNION ALL

SELECT 
    'Device Types' as metric,
    toString(uniq(device_type)) as value
FROM user_events_local;

-- 演示完成提示
SELECT 
    '🎉 Day 8 集群管理和分布式演示完成！' as message,
    '📊 已演示分布式表、分片策略、查询优化等核心概念' as summary;

-- 注意：此演示在单机环境中模拟分布式概念
-- 生产环境中需要真实的多节点集群配置 