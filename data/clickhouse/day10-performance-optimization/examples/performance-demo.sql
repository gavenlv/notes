-- ClickHouse Day 10: 性能优化示例
-- 演示各种查询优化技巧和性能测试方法

-- =====================================
-- 1. 查询分析和优化示例
-- =====================================

-- 创建测试表
DROP TABLE IF EXISTS events_perf_test;
CREATE TABLE events_perf_test (
    event_id UInt64,
    user_id UInt64,
    event_type LowCardinality(String),
    event_time DateTime,
    event_date Date MATERIALIZED toDate(event_time),
    url String,
    session_id String,
    properties String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type)
SETTINGS index_granularity = 8192;

-- 添加跳数索引
ALTER TABLE events_perf_test ADD INDEX idx_event_type event_type TYPE set(100) GRANULARITY 4;
ALTER TABLE events_perf_test ADD INDEX idx_url_bloom url TYPE bloom_filter() GRANULARITY 1;
ALTER TABLE events_perf_test ADD INDEX idx_session_minmax session_id TYPE minmax GRANULARITY 1;

-- 插入测试数据（100万条记录）
INSERT INTO events_perf_test (event_id, user_id, event_type, event_time, url, session_id, properties)
SELECT 
    number as event_id,
    number % 10000 as user_id,
    ['click', 'view', 'purchase', 'signup', 'logout'][number % 5 + 1] as event_type,
    now() - (number % (30 * 24 * 3600)) as event_time,
    concat('https://example.com/page/', toString(number % 100)) as url,
    concat('session_', toString(number % 1000)) as session_id,
    concat('{"key": "value_', toString(number % 50), '"}') as properties
FROM numbers(1000000);

-- =====================================
-- 2. 查询优化示例
-- =====================================

-- 示例1: PREWHERE vs WHERE
-- 低效查询
SELECT count() 
FROM events_perf_test 
WHERE event_date >= '2024-01-01' AND user_id = 1234;

-- 优化后的查询
SELECT count() 
FROM events_perf_test 
PREWHERE event_date >= '2024-01-01' 
WHERE user_id = 1234;

-- 查看执行计划对比
EXPLAIN PIPELINE 
SELECT count() 
FROM events_perf_test 
WHERE event_date >= '2024-01-01' AND user_id = 1234;

EXPLAIN PIPELINE 
SELECT count() 
FROM events_perf_test 
PREWHERE event_date >= '2024-01-01' 
WHERE user_id = 1234;

-- 示例2: 避免 SELECT *
-- 低效查询
SELECT * FROM events_perf_test WHERE event_type = 'click' LIMIT 10;

-- 优化后的查询
SELECT event_id, user_id, event_type, event_time 
FROM events_perf_test 
WHERE event_type = 'click' 
LIMIT 10;

-- 示例3: 聚合函数优化
-- 精确计算（较慢）
SELECT uniq(user_id) as unique_users 
FROM events_perf_test 
WHERE event_date >= today() - 7;

-- 近似计算（较快）
SELECT uniqHLL12(user_id) as unique_users_approx 
FROM events_perf_test 
WHERE event_date >= today() - 7;

-- 对比两种方法的性能
SELECT 
    'exact' as method,
    uniq(user_id) as result,
    now() as end_time
FROM events_perf_test 
WHERE event_date >= today() - 7

UNION ALL

SELECT 
    'approximate' as method,
    uniqHLL12(user_id) as result,
    now() as end_time
FROM events_perf_test 
WHERE event_date >= today() - 7;

-- =====================================
-- 3. 索引使用示例
-- =====================================

-- 测试跳数索引效果
-- 使用索引的查询
SELECT count() FROM events_perf_test WHERE event_type = 'click';

-- Bloom Filter 索引测试
SELECT count() FROM events_perf_test WHERE url = 'https://example.com/page/1';

-- 查看索引使用情况
SELECT 
    table,
    name,
    type,
    granularity
FROM system.data_skipping_indices 
WHERE table = 'events_perf_test';

-- =====================================
-- 4. 分区裁剪示例
-- =====================================

-- 好的查询 - 使用分区键
SELECT count() 
FROM events_perf_test 
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
AND event_type = 'purchase';

-- 不好的查询 - 没有使用分区键
SELECT count() 
FROM events_perf_test 
WHERE event_time >= '2024-01-01 00:00:00'
AND event_type = 'purchase';

-- 查看分区信息
SELECT 
    partition,
    rows,
    bytes_on_disk,
    formatReadableSize(bytes_on_disk) as size
FROM system.parts 
WHERE table = 'events_perf_test' AND active = 1
ORDER BY partition;

-- =====================================
-- 5. JOIN 优化示例
-- =====================================

-- 创建用户维度表
DROP TABLE IF EXISTS users_dim;
CREATE TABLE users_dim (
    user_id UInt64,
    user_name String,
    user_type String,
    registration_date Date
) ENGINE = MergeTree()
ORDER BY user_id;

-- 插入用户数据
INSERT INTO users_dim 
SELECT 
    number as user_id,
    concat('user_', toString(number)) as user_name,
    ['premium', 'basic', 'trial'][number % 3 + 1] as user_type,
    today() - (number % 365) as registration_date
FROM numbers(10000);

-- JOIN 优化示例
-- 小表在右边
SELECT 
    e.event_type,
    u.user_type,
    count() as event_count
FROM events_perf_test e
INNER JOIN users_dim u ON e.user_id = u.user_id
WHERE e.event_date >= today() - 7
GROUP BY e.event_type, u.user_type
ORDER BY event_count DESC;

-- =====================================
-- 6. 性能监控查询
-- =====================================

-- 查看慢查询
SELECT 
    left(query, 100) as query_snippet,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage,
    formatReadableSize(memory_usage) as memory_readable
FROM system.query_log 
WHERE type = 'QueryFinish' 
AND query_duration_ms > 1000
AND event_time >= now() - 3600
ORDER BY query_duration_ms DESC
LIMIT 10;

-- 查看表的统计信息
SELECT 
    table,
    sum(rows) as total_rows,
    sum(bytes_on_disk) as total_bytes,
    formatReadableSize(sum(bytes_on_disk)) as size_readable,
    avg(bytes_on_disk / rows) as avg_row_size
FROM system.parts 
WHERE active = 1 AND table LIKE '%perf_test%'
GROUP BY table;

-- 查看分区统计
SELECT 
    table,
    partition,
    count() as parts_count,
    sum(rows) as partition_rows,
    formatReadableSize(sum(bytes_on_disk)) as partition_size
FROM system.parts 
WHERE table = 'events_perf_test' AND active = 1
GROUP BY table, partition
ORDER BY partition DESC;

-- =====================================
-- 7. 内存使用分析
-- =====================================

-- 查看当前运行的查询内存使用
SELECT 
    query_id,
    left(query, 80) as query_snippet,
    memory_usage,
    formatReadableSize(memory_usage) as memory_readable,
    peak_memory_usage,
    formatReadableSize(peak_memory_usage) as peak_memory_readable,
    elapsed as seconds_elapsed
FROM system.processes
WHERE memory_usage > 0
ORDER BY memory_usage DESC;

-- 查看系统内存事件
SELECT 
    event,
    value
FROM system.events
WHERE event LIKE '%Memory%' AND value > 0
ORDER BY value DESC;

-- =====================================
-- 8. 性能基准测试
-- =====================================

-- 测试批量插入性能
CREATE TABLE insert_perf_test AS events_perf_test;

-- 记录插入开始时间并执行插入
INSERT INTO insert_perf_test 
SELECT 
    number + 1000000 as event_id,
    number % 10000 as user_id,
    ['click', 'view', 'purchase'][number % 3 + 1] as event_type,
    now() - (number % (7 * 24 * 3600)) as event_time,
    concat('https://test.com/page/', toString(number % 100)) as url,
    concat('session_', toString(number % 500)) as session_id,
    concat('{"test": "value_', toString(number % 25), '"}') as properties
FROM numbers(100000);

-- 查看最近的插入性能
SELECT 
    query,
    query_duration_ms,
    written_rows,
    written_bytes,
    formatReadableSize(written_bytes) as written_size,
    written_rows / (query_duration_ms / 1000) as rows_per_second
FROM system.query_log
WHERE query LIKE 'INSERT INTO insert_perf_test%'
AND type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 1;

-- =====================================
-- 9. 查询缓存测试
-- =====================================

-- 第一次执行（冷缓存）
SELECT count(*) FROM events_perf_test WHERE event_type = 'click';

-- 第二次执行（热缓存）
SELECT count(*) FROM events_perf_test WHERE event_type = 'click';

-- 对比执行时间
SELECT 
    left(query, 50) as query_snippet,
    query_duration_ms,
    read_rows,
    read_bytes,
    event_time
FROM system.query_log
WHERE query LIKE 'SELECT count(*) FROM events_perf_test WHERE event_type = ''click'''
AND type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 2;

-- =====================================
-- 10. 数据压缩测试
-- =====================================

-- 创建不同压缩算法的表进行对比
CREATE TABLE compression_test_lz4 (
    id UInt64,
    data String CODEC(LZ4),
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY id;

CREATE TABLE compression_test_zstd (
    id UInt64,
    data String CODEC(ZSTD),
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY id;

-- 插入相同数据
INSERT INTO compression_test_lz4 
SELECT number, concat('data_', toString(number % 1000)), now() 
FROM numbers(100000);

INSERT INTO compression_test_zstd 
SELECT number, concat('data_', toString(number % 1000)), now() 
FROM numbers(100000);

-- 比较压缩效果
SELECT 
    table,
    formatReadableSize(sum(bytes_on_disk)) as compressed_size,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed_size,
    sum(data_uncompressed_bytes) / sum(bytes_on_disk) as compression_ratio
FROM system.parts 
WHERE table LIKE 'compression_test_%' AND active = 1
GROUP BY table;

-- =====================================
-- 11. 清理测试表
-- =====================================

-- 清理测试表（可选）
-- DROP TABLE IF EXISTS events_perf_test;
-- DROP TABLE IF EXISTS users_dim;
-- DROP TABLE IF EXISTS insert_perf_test;
-- DROP TABLE IF EXISTS compression_test_lz4;
-- DROP TABLE IF EXISTS compression_test_zstd;

-- =====================================
-- 12. 性能优化总结查询
-- =====================================

-- 查看当前数据库的整体统计
SELECT 
    'Tables' as metric,
    toString(count()) as value
FROM system.tables 
WHERE database = currentDatabase()

UNION ALL

SELECT 
    'Total Rows' as metric,
    toString(sum(total_rows)) as value
FROM system.tables 
WHERE database = currentDatabase()

UNION ALL

SELECT 
    'Total Size' as metric,
    formatReadableSize(sum(total_bytes)) as value
FROM system.tables 
WHERE database = currentDatabase();

-- 显示数据库中最大的表
SELECT 
    table,
    formatReadableSize(total_bytes) as size,
    total_rows,
    engine
FROM system.tables 
WHERE database = currentDatabase()
ORDER BY total_bytes DESC
LIMIT 5; 