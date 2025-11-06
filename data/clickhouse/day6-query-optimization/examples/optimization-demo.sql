-- ClickHouse查询优化与索引实战演示
-- Day 6 学习示例

-- 创建演示数据库
CREATE DATABASE IF NOT EXISTS optimization_demo;
USE optimization_demo;

-- =====================================================
-- 1. 索引机制演示
-- =====================================================

SELECT '=== 1. 稀疏索引机制演示 ===' as section;

-- 创建基础表来演示索引原理
DROP TABLE IF EXISTS user_behavior;
CREATE TABLE user_behavior (
    user_id UInt32,
    event_time DateTime,
    event_type LowCardinality(String),
    page_url String,
    session_id String,
    ip_address IPv4,
    user_agent String
) ENGINE = MergeTree()
ORDER BY (user_id, event_time)        -- 排序键
PRIMARY KEY (user_id, event_time)     -- 主键索引（稀疏索引）
PARTITION BY toYYYYMM(event_time)      -- 分区索引
SAMPLE BY user_id                      -- 采样键
SETTINGS index_granularity = 8192;    -- 索引粒度设置

-- 插入测试数据（模拟用户行为数据）
INSERT INTO user_behavior 
SELECT 
    number % 10000 + 1 as user_id,
    toDateTime('2024-01-01 00:00:00') + toIntervalSecond(number * 60) as event_time,
    ['page_view', 'click', 'purchase', 'logout'][number % 4 + 1] as event_type,
    concat('/page/', toString(number % 100)) as page_url,
    concat('session_', toString((number % 10000) % 500)) as session_id,
    toIPv4(toString((number % 256) + 1) || '.168.1.' || toString((number % 100) + 1)) as ip_address,
    'Mozilla/5.0 (compatible; ClickHouse-Demo)' as user_agent
FROM numbers(100000);

-- 查看表的分区和索引信息
SELECT '表的分区信息:' as info_type;
SELECT 
    partition,
    rows,
    bytes_on_disk,
    primary_key_bytes_in_memory,
    marks
FROM system.parts 
WHERE table = 'user_behavior' AND active = 1
ORDER BY partition;

-- 查看索引标记数量
SELECT '索引标记统计:' as info_type;
SELECT 
    table,
    sum(marks) as total_marks,
    sum(rows) as total_rows,
    round(sum(rows) / sum(marks), 2) as avg_rows_per_mark
FROM system.parts 
WHERE table = 'user_behavior' AND active = 1
GROUP BY table;

-- =====================================================
-- 2. 主键索引查询优化演示
-- =====================================================

SELECT '=== 2. 主键索引查询优化演示 ===' as section;

-- ✅ 高效查询 - 利用主键索引
SELECT '高效查询 - 利用主键索引:' as query_type;
SELECT count() 
FROM user_behavior 
WHERE user_id = 5000 
  AND event_time >= '2024-01-01 10:00:00' 
  AND event_time < '2024-01-01 11:00:00';

-- ✅ 范围查询 - 利用主键前缀
SELECT '范围查询 - 利用主键前缀:' as query_type;
SELECT count() 
FROM user_behavior 
WHERE user_id BETWEEN 1000 AND 2000 
  AND event_time >= '2024-01-01 00:00:00';

-- ❌ 低效查询 - 跳过主键第一列
SELECT '低效查询 - 跳过主键第一列:' as query_type;
SELECT count() 
FROM user_behavior 
WHERE event_time >= '2024-01-01 10:00:00' 
  AND event_time < '2024-01-01 11:00:00'
  AND event_type = 'purchase';

-- ❌ 破坏索引的函数查询
SELECT '破坏索引的函数查询:' as query_type;
SELECT count() 
FROM user_behavior 
WHERE toHour(event_time) = 10;

-- ✅ 改进的范围查询
SELECT '改进的范围查询:' as query_type;
SELECT count() 
FROM user_behavior 
WHERE event_time >= '2024-01-01 10:00:00' 
  AND event_time < '2024-01-01 11:00:00';

-- =====================================================
-- 3. 跳数索引实战演示
-- =====================================================

SELECT '=== 3. 跳数索引实战演示 ===' as section;

-- 创建带跳数索引的表
DROP TABLE IF EXISTS ecommerce_events;
CREATE TABLE ecommerce_events (
    event_id UInt64,
    user_id UInt32,
    event_time DateTime,
    event_type LowCardinality(String),
    product_id Nullable(UInt32),
    category_id UInt32,
    price Decimal(10, 2),
    session_id String,
    user_agent String,
    ip_address IPv4
) ENGINE = MergeTree()
ORDER BY (user_id, event_time)
PARTITION BY toYYYYMM(event_time)
PRIMARY KEY (user_id, event_time)

-- 添加各种类型的跳数索引
INDEX idx_time_minmax event_time TYPE minmax GRANULARITY 4
INDEX idx_category_set category_id TYPE set(1000) GRANULARITY 4
INDEX idx_session_bloom session_id TYPE bloom_filter() GRANULARITY 4
INDEX idx_ua_ngram user_agent TYPE ngrambf_v1(4, 1024, 3, 0) GRANULARITY 4
INDEX idx_price_minmax price TYPE minmax GRANULARITY 4;

-- 插入测试数据
INSERT INTO ecommerce_events 
SELECT 
    number as event_id,
    (number % 50000) + 1 as user_id,
    toDateTime('2024-01-01 00:00:00') + toIntervalSecond(number * 30) as event_time,
    ['page_view', 'add_to_cart', 'purchase', 'logout', 'search'][number % 5 + 1] as event_type,
    if(number % 5 = 2, (number % 1000) + 1, NULL) as product_id,
    (number % 50) + 1 as category_id,
    round((number % 500 + 10) * 1.99, 2) as price,
    concat('session_', toString(number % 10000)) as session_id,
    ['Mozilla/5.0', 'Chrome/91.0', 'Safari/14.0', 'Edge/91.0'][number % 4 + 1] as user_agent,
    toIPv4(toString((number % 256) + 1) || '.168.' || toString((number % 256) + 1) || '.' || toString((number % 256) + 1)) as ip_address
FROM numbers(200000);

-- 测试MinMax索引效果
SELECT 'MinMax索引测试 - 时间范围查询:' as test_type;
SELECT count() 
FROM ecommerce_events 
WHERE event_time >= '2024-01-02 00:00:00' 
  AND event_time < '2024-01-03 00:00:00';

SELECT 'MinMax索引测试 - 价格范围查询:' as test_type;
SELECT count() 
FROM ecommerce_events 
WHERE price >= 100.00 AND price <= 200.00;

-- 测试Set索引效果
SELECT 'Set索引测试 - IN查询:' as test_type;
SELECT count() 
FROM ecommerce_events 
WHERE category_id IN (1, 5, 10, 15, 20);

-- 测试Bloom Filter索引效果
SELECT 'Bloom Filter索引测试 - 等值查询:' as test_type;
SELECT count() 
FROM ecommerce_events 
WHERE session_id = 'session_12345';

-- 测试N-gram索引效果
SELECT 'N-gram索引测试 - 模糊匹配:' as test_type;
SELECT count() 
FROM ecommerce_events 
WHERE user_agent LIKE '%Chrome%';

-- =====================================================
-- 4. 查询执行计划分析
-- =====================================================

SELECT '=== 4. 查询执行计划分析 ===' as section;

-- 查看查询执行计划
SELECT 'EXPLAIN PLAN 示例:' as demo_type;
EXPLAIN PLAN 
SELECT 
    user_id,
    count() as event_count,
    uniq(session_id) as session_count,
    sum(price) as total_spent
FROM ecommerce_events 
WHERE event_time >= '2024-01-01 10:00:00' 
  AND event_time < '2024-01-01 12:00:00'
  AND event_type = 'purchase'
GROUP BY user_id 
ORDER BY total_spent DESC 
LIMIT 10;

-- 查看详细执行管道
SELECT 'EXPLAIN PIPELINE 示例:' as demo_type;
EXPLAIN PIPELINE 
SELECT user_id, count() 
FROM ecommerce_events 
WHERE user_id BETWEEN 1000 AND 2000 
GROUP BY user_id;

-- =====================================================
-- 5. 查询优化对比演示
-- =====================================================

SELECT '=== 5. 查询优化对比演示 ===' as section;

-- 创建预聚合表用于优化对比
DROP TABLE IF EXISTS daily_user_stats;
CREATE TABLE daily_user_stats (
    date Date,
    user_id UInt32,
    event_count UInt64,
    session_count UInt64,
    total_spent Decimal(15, 2)
) ENGINE = SummingMergeTree((event_count, session_count, total_spent))
ORDER BY (date, user_id)
PARTITION BY toYYYYMM(date);

-- 插入预聚合数据
INSERT INTO daily_user_stats 
SELECT 
    toDate(event_time) as date,
    user_id,
    count() as event_count,
    uniq(session_id) as session_count,
    sum(if(event_type = 'purchase', price, 0)) as total_spent
FROM ecommerce_events 
GROUP BY date, user_id;

-- ❌ 未优化的复杂查询
SELECT '未优化的复杂聚合查询:' as optimization_demo;
SELECT 
    user_id,
    count() as total_events,
    uniq(session_id) as total_sessions,
    sum(if(event_type = 'purchase', price, 0)) as total_spent
FROM ecommerce_events 
WHERE event_time >= '2024-01-01' 
  AND event_time < '2024-01-08'
GROUP BY user_id
HAVING total_events > 50
ORDER BY total_spent DESC
LIMIT 20;

-- ✅ 优化后的查询（使用预聚合表）
SELECT '优化后的聚合查询（预聚合表）:' as optimization_demo;
SELECT 
    user_id,
    sum(event_count) as total_events,
    sum(session_count) as total_sessions,
    sum(total_spent) as total_spent
FROM daily_user_stats 
WHERE date >= '2024-01-01' 
  AND date < '2024-01-08'
GROUP BY user_id
HAVING total_events > 50
ORDER BY total_spent DESC
LIMIT 20;

-- =====================================================
-- 6. JOIN优化演示
-- =====================================================

SELECT '=== 6. JOIN优化演示 ===' as section;

-- 创建用户维度表
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id UInt32,
    name String,
    email String,
    registration_date Date,
    country LowCardinality(String),
    age_group LowCardinality(String)
) ENGINE = MergeTree()
ORDER BY user_id;

-- 插入用户数据
INSERT INTO users 
SELECT 
    number + 1 as user_id,
    concat('User_', toString(number + 1)) as name,
    concat('user', toString(number + 1), '@example.com') as email,
    toDate('2023-01-01') + toIntervalDay(number % 365) as registration_date,
    ['China', 'USA', 'Japan', 'Germany', 'UK'][number % 5 + 1] as country,
    ['18-25', '26-35', '36-45', '46-55', '55+'][number % 5 + 1] as age_group
FROM numbers(50000);

-- ✅ 优化的JOIN查询
SELECT 'ANY LEFT JOIN 优化查询:' as join_demo;
SELECT 
    u.country,
    u.age_group,
    count() as events,
    uniq(e.user_id) as active_users,
    sum(e.price) as revenue
FROM ecommerce_events e
ANY LEFT JOIN users u ON e.user_id = u.user_id
WHERE e.event_time >= '2024-01-01'
  AND e.event_type = 'purchase'
  AND u.country = 'China'
GROUP BY u.country, u.age_group
ORDER BY revenue DESC
LIMIT 10;

-- 创建字典优化小表JOIN
DROP DICTIONARY IF EXISTS user_dict;
CREATE DICTIONARY user_dict (
    user_id UInt32,
    country String,
    age_group String
) PRIMARY KEY user_id
SOURCE(CLICKHOUSE(TABLE 'users'))
LAYOUT(HASHED())
LIFETIME(3600);

-- ✅ 使用字典的优化查询
SELECT '字典优化查询:' as join_demo;
SELECT 
    dictGet('user_dict', 'country', user_id) as country,
    dictGet('user_dict', 'age_group', user_id) as age_group,
    count() as events,
    sum(price) as revenue
FROM ecommerce_events 
WHERE event_time >= '2024-01-01'
  AND event_type = 'purchase'
  AND dictGet('user_dict', 'country', user_id) = 'China'
GROUP BY country, age_group
ORDER BY revenue DESC
LIMIT 10;

-- =====================================================
-- 7. 采样查询演示
-- =====================================================

SELECT '=== 7. 采样查询演示 ===' as section;

-- ✅ 使用采样加速大数据集分析
SELECT '采样查询 - 10%采样率:' as sampling_demo;
SELECT 
    toStartOfDay(event_time) as date,
    event_type,
    count() * 10 as estimated_events,  -- 乘以采样率倒数
    uniq(user_id) * 10 as estimated_users,
    sum(price) * 10 as estimated_revenue
FROM ecommerce_events SAMPLE 0.1      -- 10%采样
WHERE event_time >= '2024-01-01'
  AND event_time < '2024-01-08'
GROUP BY date, event_type
ORDER BY date, event_type;

-- 对比完整查询结果
SELECT '完整查询结果:' as sampling_demo;
SELECT 
    toStartOfDay(event_time) as date,
    event_type,
    count() as actual_events,
    uniq(user_id) as actual_users,
    sum(price) as actual_revenue
FROM ecommerce_events 
WHERE event_time >= '2024-01-01'
  AND event_time < '2024-01-08'
GROUP BY date, event_type
ORDER BY date, event_type;

-- =====================================================
-- 8. 性能监控查询演示
-- =====================================================

SELECT '=== 8. 性能监控查询演示 ===' as section;

-- 执行一些查询以产生日志数据
SELECT count() FROM ecommerce_events WHERE user_id < 1000;
SELECT avg(price) FROM ecommerce_events WHERE event_type = 'purchase';
SELECT uniq(user_id) FROM ecommerce_events WHERE event_time >= today();

-- 查询性能监控
SELECT '最近的查询性能统计:' as monitoring_demo;
SELECT 
    substring(query, 1, 60) as query_preview,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage,
    query_start_time
FROM system.query_log 
WHERE type = 'QueryFinish'
  AND query LIKE '%ecommerce_events%'
  AND query_start_time >= now() - INTERVAL 10 MINUTE
ORDER BY query_start_time DESC 
LIMIT 5;

-- 表读取统计
SELECT '表读取统计:' as monitoring_demo;
SELECT 
    table,
    sum(read_rows) as total_rows_read,
    sum(read_bytes) as total_bytes_read,
    count() as query_count,
    avg(query_duration_ms) as avg_duration_ms
FROM system.query_log 
WHERE type = 'QueryFinish'
  AND database = 'optimization_demo'
  AND query_start_time >= now() - INTERVAL 10 MINUTE
GROUP BY table
ORDER BY total_bytes_read DESC;

-- =====================================================
-- 9. 物化视图优化演示
-- =====================================================

SELECT '=== 9. 物化视图优化演示 ===' as section;

-- 创建实时聚合物化视图
DROP TABLE IF EXISTS hourly_stats;
CREATE TABLE hourly_stats (
    hour DateTime,
    event_type LowCardinality(String),
    event_count UInt64,
    unique_users UInt64,
    total_revenue Decimal(15, 2)
) ENGINE = SummingMergeTree((event_count, unique_users, total_revenue))
ORDER BY (hour, event_type);

-- 创建物化视图
DROP VIEW IF EXISTS hourly_stats_mv;
CREATE MATERIALIZED VIEW hourly_stats_mv TO hourly_stats AS
SELECT 
    toStartOfHour(event_time) as hour,
    event_type,
    count() as event_count,
    uniq(user_id) as unique_users,
    sum(if(event_type = 'purchase', price, 0)) as total_revenue
FROM ecommerce_events
GROUP BY hour, event_type;

-- 插入新数据触发物化视图
INSERT INTO ecommerce_events 
SELECT 
    number + 200000 as event_id,
    (number % 50000) + 1 as user_id,
    now() - toIntervalSecond(number * 60) as event_time,
    ['page_view', 'purchase'][number % 2 + 1] as event_type,
    NULL as product_id,
    (number % 50) + 1 as category_id,
    round((number % 100 + 10) * 2.99, 2) as price,
    concat('session_new_', toString(number)) as session_id,
    'Mozilla/5.0 (New Session)' as user_agent,
    toIPv4('192.168.1.1') as ip_address
FROM numbers(1000);

-- 查询物化视图结果
SELECT '物化视图实时聚合结果:' as mv_demo;
SELECT 
    hour,
    event_type,
    sum(event_count) as total_events,
    sum(unique_users) as total_users,
    sum(total_revenue) as total_revenue
FROM hourly_stats 
WHERE hour >= now() - INTERVAL 2 HOUR
GROUP BY hour, event_type
ORDER BY hour DESC, event_type;

-- =====================================================
-- 10. 清理演示数据
-- =====================================================

SELECT '=== 演示完成，清理数据 ===' as section;

-- 删除物化视图和表
DROP VIEW IF EXISTS hourly_stats_mv;
DROP TABLE IF EXISTS hourly_stats;
DROP DICTIONARY IF EXISTS user_dict;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS daily_user_stats;
DROP TABLE IF EXISTS ecommerce_events;
DROP TABLE IF EXISTS user_behavior;

-- 删除演示数据库
DROP DATABASE IF EXISTS optimization_demo;

SELECT '✅ Day 6 查询优化演示完成！' as completion_message;
SELECT '🎯 关键收获：合理设计索引、优化查询模式、使用预聚合技术是性能优化的核心' as key_takeaway;
SELECT '📊 监控建议：定期检查system.query_log，分析慢查询，持续优化' as monitoring_tip; 