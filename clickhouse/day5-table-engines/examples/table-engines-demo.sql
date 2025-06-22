-- ClickHouse表引擎深度演示
-- Day 5 学习示例

-- 创建演示数据库
CREATE DATABASE IF NOT EXISTS table_engines_demo;
USE table_engines_demo;

-- =====================================================
-- 1. MergeTree基础引擎演示
-- =====================================================

SELECT '=== 1. MergeTree基础引擎演示 ===' as section;

-- 创建基础MergeTree表
DROP TABLE IF EXISTS web_analytics;
CREATE TABLE web_analytics (
    user_id UInt32,
    event_time DateTime,
    event_type LowCardinality(String),
    page_url String,
    session_id String,
    country LowCardinality(String),
    device_type LowCardinality(String),
    revenue Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (user_id, event_time)        -- 排序键
PARTITION BY toYYYYMM(event_time)      -- 按月分区
PRIMARY KEY (user_id)                  -- 主键（稀疏索引）
SAMPLE BY user_id                      -- 采样键
TTL event_time + INTERVAL 1 YEAR;     -- 数据过期时间

-- 插入测试数据
INSERT INTO web_analytics VALUES
(1001, '2024-01-15 10:30:00', 'page_view', '/home', 'sess_001', 'CN', 'mobile', 0.00),
(1001, '2024-01-15 10:31:00', 'click', '/product/123', 'sess_001', 'CN', 'mobile', 99.99),
(1002, '2024-01-15 11:00:00', 'page_view', '/category', 'sess_002', 'US', 'desktop', 0.00),
(1002, '2024-01-15 11:05:00', 'purchase', '/checkout', 'sess_002', 'US', 'desktop', 299.99),
(1003, '2024-02-01 14:20:00', 'page_view', '/about', 'sess_003', 'UK', 'tablet', 0.00),
(1003, '2024-02-01 14:25:00', 'signup', '/register', 'sess_003', 'UK', 'tablet', 0.00);

-- 查看表结构和数据
DESCRIBE web_analytics;
SELECT * FROM web_analytics ORDER BY user_id, event_time;

-- 查看分区信息
SELECT 
    partition,
    rows,
    bytes_on_disk,
    primary_key_bytes_in_memory
FROM system.parts 
WHERE table = 'web_analytics' AND active = 1;

-- =====================================================
-- 2. ReplacingMergeTree去重引擎演示
-- =====================================================

SELECT '=== 2. ReplacingMergeTree去重引擎演示 ===' as section;

-- 创建去重表
DROP TABLE IF EXISTS user_profiles;
CREATE TABLE user_profiles (
    user_id UInt32,
    name String,
    email String,
    last_login DateTime,
    version UInt64  -- 版本号，用于选择最新记录
) ENGINE = ReplacingMergeTree(version)  -- 指定版本列
ORDER BY user_id
PARTITION BY user_id % 10;

-- 插入重复数据进行测试
INSERT INTO user_profiles VALUES
(1001, '张三', 'zhang@old.com', '2024-01-01 10:00:00', 1),
(1002, '李四', 'li@example.com', '2024-01-01 12:00:00', 1),
(1003, '王五', 'wang@example.com', '2024-01-01 14:00:00', 1);

-- 更新用户信息（通过插入新版本）
INSERT INTO user_profiles VALUES
(1001, '张三', 'zhang@new.com', '2024-01-02 11:00:00', 2),  -- 更新邮箱
(1002, '李四新', 'li@new.com', '2024-01-02 13:00:00', 2);   -- 更新姓名和邮箱

-- 再次更新
INSERT INTO user_profiles VALUES
(1001, '张三最新', 'zhang@latest.com', '2024-01-03 10:00:00', 3);

-- 查看去重前的所有数据
SELECT '去重前的数据:' as status;
SELECT * FROM user_profiles ORDER BY user_id, version;

-- 强制合并以触发去重
OPTIMIZE TABLE user_profiles FINAL;

-- 查看去重后的结果
SELECT '去重后的数据:' as status;
SELECT * FROM user_profiles FINAL ORDER BY user_id;

-- =====================================================
-- 3. SummingMergeTree聚合引擎演示
-- =====================================================

SELECT '=== 3. SummingMergeTree聚合引擎演示 ===' as section;

-- 创建求和聚合表
DROP TABLE IF EXISTS daily_metrics;
CREATE TABLE daily_metrics (
    date Date,
    country LowCardinality(String),
    event_type LowCardinality(String),
    page_views UInt64,
    unique_users UInt64,
    total_revenue Decimal(15, 2)
) ENGINE = SummingMergeTree((page_views, unique_users, total_revenue))  -- 指定求和列
ORDER BY (date, country, event_type)
PARTITION BY toYYYYMM(date);

-- 插入需要聚合的数据
INSERT INTO daily_metrics VALUES
('2024-01-01', 'CN', 'page_view', 1000, 800, 0.00),
('2024-01-01', 'CN', 'page_view', 500, 400, 0.00),   -- 会与上一条聚合
('2024-01-01', 'CN', 'page_view', 300, 200, 0.00),   -- 会与前两条聚合
('2024-01-01', 'US', 'page_view', 800, 600, 0.00),
('2024-01-01', 'CN', 'purchase', 50, 45, 2999.95),
('2024-01-01', 'CN', 'purchase', 30, 28, 1899.97),   -- 会与上一条聚合
('2024-01-01', 'US', 'purchase', 20, 18, 1199.98);

-- 查看聚合前的数据
SELECT '聚合前的数据:' as status;
SELECT * FROM daily_metrics ORDER BY date, country, event_type;

-- 触发聚合
OPTIMIZE TABLE daily_metrics FINAL;

-- 查看聚合后的结果
SELECT '聚合后的数据:' as status;
SELECT * FROM daily_metrics FINAL ORDER BY date, country, event_type;

-- =====================================================
-- 4. AggregatingMergeTree预聚合引擎演示
-- =====================================================

SELECT '=== 4. AggregatingMergeTree预聚合引擎演示 ===' as section;

-- 首先创建原始事件表用于演示
DROP TABLE IF EXISTS raw_events;
CREATE TABLE raw_events (
    user_id UInt32,
    event_time DateTime,
    session_duration UInt32,
    page_views UInt32,
    country LowCardinality(String)
) ENGINE = MergeTree()
ORDER BY (event_time, user_id)
PARTITION BY toYYYYMM(event_time);

-- 插入原始事件数据
INSERT INTO raw_events VALUES
(1001, '2024-01-01 10:00:00', 300, 5, 'CN'),
(1002, '2024-01-01 10:30:00', 450, 8, 'CN'),
(1003, '2024-01-01 11:00:00', 200, 3, 'US'),
(1001, '2024-01-01 15:00:00', 600, 12, 'CN'),
(1004, '2024-01-01 16:00:00', 180, 2, 'UK'),
(1002, '2024-01-02 09:00:00', 520, 9, 'CN'),
(1005, '2024-01-02 10:00:00', 350, 6, 'US');

-- 创建预聚合表
DROP TABLE IF EXISTS user_analytics_agg;
CREATE TABLE user_analytics_agg (
    date Date,
    country LowCardinality(String),
    unique_users AggregateFunction(uniq, UInt32),        -- 去重状态
    avg_session_time AggregateFunction(avg, UInt32),     -- 平均值状态
    total_page_views SimpleAggregateFunction(sum, UInt64) -- 简单聚合
) ENGINE = AggregatingMergeTree()
ORDER BY (date, country)
PARTITION BY toYYYYMM(date);

-- 使用聚合状态插入数据
INSERT INTO user_analytics_agg 
SELECT 
    toDate(event_time) as date,
    country,
    uniqState(user_id) as unique_users,
    avgState(session_duration) as avg_session_time,
    sum(page_views) as total_page_views
FROM raw_events 
GROUP BY date, country;

-- 查询聚合结果
SELECT 
    date,
    country,
    uniqMerge(unique_users) as unique_users,
    round(avgMerge(avg_session_time), 2) as avg_session_time,
    sum(total_page_views) as total_page_views
FROM user_analytics_agg 
GROUP BY date, country
ORDER BY date, country;

-- =====================================================
-- 5. CollapsingMergeTree状态折叠引擎演示
-- =====================================================

SELECT '=== 5. CollapsingMergeTree状态折叠引擎演示 ===' as section;

-- 创建状态折叠表
DROP TABLE IF EXISTS user_balance;
CREATE TABLE user_balance (
    user_id UInt32,
    balance Decimal(10, 2),
    update_time DateTime,
    sign Int8  -- 符号列：1表示插入，-1表示删除
) ENGINE = CollapsingMergeTree(sign)
ORDER BY (user_id, update_time)
PARTITION BY toYYYYMM(update_time);

-- 模拟账户余额变更
-- 1. 初始余额
INSERT INTO user_balance VALUES
(1001, 1000.00, '2024-01-01 10:00:00', 1),
(1002, 2000.00, '2024-01-01 10:00:00', 1),
(1003, 500.00, '2024-01-01 10:00:00', 1);

-- 2. 余额变更（先删除旧记录，再插入新记录）
INSERT INTO user_balance VALUES
(1001, 1000.00, '2024-01-01 10:00:00', -1),  -- 删除旧记录
(1001, 1500.00, '2024-01-01 11:00:00', 1);   -- 插入新记录

-- 3. 另一用户的余额变更
INSERT INTO user_balance VALUES
(1002, 2000.00, '2024-01-01 10:00:00', -1),  -- 删除旧记录
(1002, 1800.00, '2024-01-01 12:00:00', 1);   -- 插入新记录

-- 查看所有变更记录
SELECT '所有余额变更记录:' as status;
SELECT * FROM user_balance ORDER BY user_id, update_time, sign;

-- 查询最终状态
SELECT '当前用户余额:' as status;
SELECT 
    user_id,
    sum(balance * sign) as current_balance,
    sum(sign) as record_status  -- 应该为1表示有效记录
FROM user_balance 
GROUP BY user_id
HAVING sum(sign) > 0  -- 确保记录没有被完全删除
ORDER BY user_id;

-- =====================================================
-- 6. VersionedCollapsingMergeTree版本折叠引擎演示
-- =====================================================

SELECT '=== 6. VersionedCollapsingMergeTree版本折叠引擎演示 ===' as section;

-- 创建版本折叠表
DROP TABLE IF EXISTS user_balance_v2;
CREATE TABLE user_balance_v2 (
    user_id UInt32,
    balance Decimal(10, 2),
    update_time DateTime,
    version UInt64,  -- 版本列
    sign Int8        -- 符号列
) ENGINE = VersionedCollapsingMergeTree(sign, version)
ORDER BY (user_id, version)
PARTITION BY toYYYYMM(update_time);

-- 版本化的状态变更（支持乱序写入）
INSERT INTO user_balance_v2 VALUES
(1001, 1000.00, '2024-01-01 10:00:00', 1, 1),   -- 版本1，余额1000
(1001, 1500.00, '2024-01-01 11:00:00', 2, 1),   -- 版本2，余额1500
(1001, 1000.00, '2024-01-01 10:00:00', 1, -1),  -- 删除版本1（乱序写入）
(1002, 2000.00, '2024-01-01 10:00:00', 1, 1),   -- 用户1002版本1
(1001, 1800.00, '2024-01-01 12:00:00', 3, 1),   -- 版本3，余额1800
(1001, 1500.00, '2024-01-01 11:00:00', 2, -1);  -- 删除版本2

-- 查看所有版本记录
SELECT '所有版本记录:' as status;
SELECT * FROM user_balance_v2 ORDER BY user_id, version, sign;

-- 查询当前状态（最新版本）
SELECT '当前用户余额（最新版本）:' as status;
SELECT 
    user_id,
    argMax(balance, version) as current_balance,
    max(version) as latest_version
FROM user_balance_v2 
WHERE sign = 1
GROUP BY user_id
ORDER BY user_id;

-- =====================================================
-- 7. 不同日志引擎对比演示
-- =====================================================

SELECT '=== 7. 日志引擎对比演示 ===' as section;

-- TinyLog引擎 - 最简单
DROP TABLE IF EXISTS tiny_log_demo;
CREATE TABLE tiny_log_demo (
    id UInt32,
    message String,
    timestamp DateTime
) ENGINE = TinyLog;

-- Log引擎 - 支持并发读取
DROP TABLE IF EXISTS log_demo;
CREATE TABLE log_demo (
    id UInt32,
    message String,
    timestamp DateTime
) ENGINE = Log;

-- StripeLog引擎 - 条带化存储
DROP TABLE IF EXISTS stripe_log_demo;
CREATE TABLE stripe_log_demo (
    id UInt32,
    level String,
    message String,
    timestamp DateTime
) ENGINE = StripeLog;

-- 插入相同的测试数据
INSERT INTO tiny_log_demo VALUES
(1, 'Application started', '2024-01-01 10:00:00'),
(2, 'User login: admin', '2024-01-01 10:01:00'),
(3, 'Database connection established', '2024-01-01 10:02:00');

INSERT INTO log_demo VALUES
(1, 'Application started', '2024-01-01 10:00:00'),
(2, 'User login: admin', '2024-01-01 10:01:00'),
(3, 'Database connection established', '2024-01-01 10:02:00');

INSERT INTO stripe_log_demo VALUES
(1, 'INFO', 'Application started', '2024-01-01 10:00:00'),
(2, 'INFO', 'User login: admin', '2024-01-01 10:01:00'),
(3, 'INFO', 'Database connection established', '2024-01-01 10:02:00');

-- 查询日志数据
SELECT 'TinyLog数据:' as engine_type;
SELECT * FROM tiny_log_demo;

SELECT 'Log数据:' as engine_type;
SELECT * FROM log_demo;

SELECT 'StripeLog数据:' as engine_type;
SELECT * FROM stripe_log_demo;

-- =====================================================
-- 8. Memory引擎演示
-- =====================================================

SELECT '=== 8. Memory引擎演示 ===' as section;

-- 创建内存表
DROP TABLE IF EXISTS session_cache;
CREATE TABLE session_cache (
    session_id String,
    user_id UInt32,
    last_activity DateTime,
    data String
) ENGINE = Memory;

-- 插入会话数据
INSERT INTO session_cache VALUES
('sess_001', 1001, now(), '{"page": "/home", "referrer": "google"}'),
('sess_002', 1002, now(), '{"page": "/product", "referrer": "direct"}'),
('sess_003', 1003, now(), '{"page": "/checkout", "referrer": "/cart"}');

-- 查询内存表数据
SELECT * FROM session_cache ORDER BY user_id;

-- =====================================================
-- 9. 表引擎性能对比分析
-- =====================================================

SELECT '=== 9. 表引擎性能对比分析 ===' as section;

-- 查看不同表的存储统计
SELECT 
    table,
    engine,
    total_rows,
    total_bytes,
    round(total_bytes / total_rows, 2) as bytes_per_row
FROM system.tables 
WHERE database = 'table_engines_demo'
  AND total_rows > 0
ORDER BY total_bytes DESC;

-- 查看分区信息（仅MergeTree系列）
SELECT 
    table,
    count() as partition_count,
    sum(rows) as total_rows,
    sum(bytes_on_disk) as total_bytes_on_disk
FROM system.parts 
WHERE database = 'table_engines_demo' 
  AND active = 1
GROUP BY table
ORDER BY total_bytes_on_disk DESC;

-- =====================================================
-- 10. 清理演示数据
-- =====================================================

SELECT '=== 演示完成，清理数据 ===' as section;

-- 删除所有演示表
DROP TABLE IF EXISTS web_analytics;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS daily_metrics;
DROP TABLE IF EXISTS raw_events;
DROP TABLE IF EXISTS user_analytics_agg;
DROP TABLE IF EXISTS user_balance;
DROP TABLE IF EXISTS user_balance_v2;
DROP TABLE IF EXISTS tiny_log_demo;
DROP TABLE IF EXISTS log_demo;
DROP TABLE IF EXISTS stripe_log_demo;
DROP TABLE IF EXISTS session_cache;

-- 删除演示数据库
DROP DATABASE IF EXISTS table_engines_demo;

SELECT '✅ Day 5 表引擎演示完成！' as completion_message;
SELECT '🎯 关键收获：不同表引擎适用不同场景，MergeTree系列是核心' as key_takeaway; 