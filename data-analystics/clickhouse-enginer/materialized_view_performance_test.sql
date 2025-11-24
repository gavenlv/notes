-- ClickHouse物化视图写入性能测试脚本
-- 本脚本用于测试物化视图对写入性能的影响，并提供基准测试

-- ================================
-- 1. 环境准备
-- ================================

-- 设置测试参数
SET insert_deduplicate = 0;
SET insert_quorum = 1;
SET max_insert_block_size = 1048576;
SET max_threads = 8;

-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS mv_performance_test;
USE mv_performance_test;

-- ================================
-- 2. 基准测试：无物化视图
-- ================================

-- 创建源表（无物化视图）
CREATE TABLE source_no_mv (
    id UInt64,
    timestamp DateTime,
    user_id UInt64,
    event_type String,
    value Float64,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, user_id, event_type);

-- 插入测试数据（1亿行）
INSERT INTO source_no_mv
SELECT 
    number AS id,
    now() - INTERVAL (number % 86400) SECOND AS timestamp,
    number % 100000 AS user_id,
    arrayJoin(['click', 'view', 'purchase', 'login', 'logout']) AS event_type,
    randCanonical() AS value,
    toString(number % 1000) AS properties
FROM numbers(100000000);

-- 记录基准测试结果
SELECT 
    'No Materialized View' AS test_scenario,
    query_duration_ms AS insert_duration_ms,
    read_rows,
    written_rows,
    memory_usage AS memory_usage_bytes,
    formatReadableSize(memory_usage) AS memory_usage_readable
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE 'INSERT INTO source_no_mv%'
ORDER BY query_start_time DESC
LIMIT 1;

-- ================================
-- 3. 测试1：单个简单物化视图
-- ================================

-- 创建源表
CREATE TABLE source_1_mv (
    id UInt64,
    timestamp DateTime,
    user_id UInt64,
    event_type String,
    value Float64,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, user_id, event_type);

-- 创建目标表
CREATE TABLE target_1_simple (
    id UInt64,
    timestamp DateTime,
    user_id UInt64,
    event_type String,
    value Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, user_id, event_type);

-- 创建简单物化视图
CREATE MATERIALIZED VIEW mv_1_simple TO target_1_simple AS
SELECT id, timestamp, user_id, event_type, value
FROM source_1_mv;

-- 插入测试数据（1亿行）
INSERT INTO source_1_mv
SELECT 
    number AS id,
    now() - INTERVAL (number % 86400) SECOND AS timestamp,
    number % 100000 AS user_id,
    arrayJoin(['click', 'view', 'purchase', 'login', 'logout']) AS event_type,
    randCanonical() AS value,
    toString(number % 1000) AS properties
FROM numbers(100000000);

-- 记录测试结果
SELECT 
    '1 Simple Materialized View' AS test_scenario,
    query_duration_ms AS insert_duration_ms,
    read_rows,
    written_rows,
    memory_usage AS memory_usage_bytes,
    formatReadableSize(memory_usage) AS memory_usage_readable
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE 'INSERT INTO source_1_mv%'
ORDER BY query_start_time DESC
LIMIT 1;

-- 比较性能差异
WITH base_performance AS (
    SELECT query_duration_ms AS base_duration
    FROM system.query_log
    WHERE event_date = today()
      AND type = 'QueryFinish'
      AND query LIKE 'INSERT INTO source_no_mv%'
      AND query_start_time = (
          SELECT min(query_start_time)
          FROM system.query_log
          WHERE event_date = today()
            AND type = 'QueryFinish'
            AND query LIKE 'INSERT INTO source_no_mv%'
      )
),
test1_performance AS (
    SELECT query_duration_ms AS test1_duration
    FROM system.query_log
    WHERE event_date = today()
      AND type = 'QueryFinish'
      AND query LIKE 'INSERT INTO source_1_mv%'
      AND query_start_time = (
          SELECT min(query_start_time)
          FROM system.query_log
          WHERE event_date = today()
            AND type = 'QueryFinish'
            AND query LIKE 'INSERT INTO source_1_mv%'
      )
)
SELECT 
    '1 Simple MV vs No MV' AS comparison,
    base_duration,
    test1_duration,
    round(test1_duration * 100.0 / base_duration - 100, 2) AS performance_impact_percent
FROM base_performance, test1_performance;

-- ================================
-- 4. 测试2：单个复杂物化视图
-- ================================

-- 创建源表
CREATE TABLE source_complex_mv (
    id UInt64,
    timestamp DateTime,
    user_id UInt64,
    event_type String,
    value Float64,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, user_id, event_type);

-- 创建目标表
CREATE TABLE target_complex (
    date Date,
    event_type String,
    user_group String,
    total_value Float64,
    event_count UInt64,
    unique_users AggregateFunction(uniq, UInt64),
    max_value Float64,
    min_value Float64,
    avg_value Float64
) ENGINE = AggregatingMergeTree()
PARTITION BY (date, event_type)
ORDER BY (date, event_type, user_group);

-- 创建复杂物化视图
CREATE MATERIALIZED VIEW mv_complex TO target_complex AS
SELECT 
    toDate(timestamp) AS date,
    event_type,
    CASE WHEN user_id % 1000 < 500 THEN 'group_a' ELSE 'group_b' END AS user_group,
    sum(value) AS total_value,
    count() AS event_count,
    uniqState(user_id) AS unique_users,
    max(value) AS max_value,
    min(value) AS min_value,
    avg(value) AS avg_value
FROM source_complex_mv
GROUP BY date, event_type, user_group;

-- 插入测试数据（1亿行）
INSERT INTO source_complex_mv
SELECT 
    number AS id,
    now() - INTERVAL (number % 86400) SECOND AS timestamp,
    number % 100000 AS user_id,
    arrayJoin(['click', 'view', 'purchase', 'login', 'logout']) AS event_type,
    randCanonical() AS value,
    toString(number % 1000) AS properties
FROM numbers(100000000);

-- 记录测试结果
SELECT 
    '1 Complex Materialized View' AS test_scenario,
    query_duration_ms AS insert_duration_ms,
    read_rows,
    written_rows,
    memory_usage AS memory_usage_bytes,
    formatReadableSize(memory_usage) AS memory_usage_readable
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE 'INSERT INTO source_complex_mv%'
ORDER BY query_start_time DESC
LIMIT 1;

-- ================================
-- 5. 测试3：多个物化视图
-- ================================

-- 创建源表
CREATE TABLE source_multiple_mvs (
    id UInt64,
    timestamp DateTime,
    user_id UInt64,
    event_type String,
    value Float64,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, user_id, event_type);

-- 创建目标表1：基本事件记录
CREATE TABLE target_basic_events (
    id UInt64,
    timestamp DateTime,
    user_id UInt64,
    event_type String,
    value Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, user_id);

-- 创建目标表2：日统计
CREATE TABLE target_daily_stats (
    date Date,
    event_type String,
    event_count UInt64,
    total_value Float64
) ENGINE = SummingMergeTree(event_count, total_value)
PARTITION BY (date, event_type)
ORDER BY (date, event_type);

-- 创建目标表3：用户统计
CREATE TABLE target_user_stats (
    user_id UInt64,
    last_active Date,
    total_events UInt64,
    total_value Float64
) ENGINE = ReplacingMergeTree(last_active)
ORDER BY user_id;

-- 创建目标表4：事件类型分布
CREATE TABLE target_event_distribution (
    event_type String,
    hour DateTime,
    event_count UInt64,
    unique_users AggregateFunction(uniq, UInt64)
) ENGINE = AggregatingMergeTree()
ORDER BY (event_type, hour);

-- 创建多个物化视图
CREATE MATERIALIZED VIEW mv_basic_events TO target_basic_events AS
SELECT id, timestamp, user_id, event_type, value
FROM source_multiple_mvs;

CREATE MATERIALIZED VIEW mv_daily_stats TO target_daily_stats AS
SELECT 
    toDate(timestamp) AS date,
    event_type,
    count() AS event_count,
    sum(value) AS total_value
FROM source_multiple_mvs
GROUP BY date, event_type;

CREATE MATERIALIZED VIEW mv_user_stats TO target_user_stats AS
SELECT 
    user_id,
    toDate(max(timestamp)) AS last_active,
    count() AS total_events,
    sum(value) AS total_value
FROM source_multiple_mvs
GROUP BY user_id;

CREATE MATERIALIZED VIEW mv_event_distribution TO target_event_distribution AS
SELECT 
    event_type,
    toStartOfHour(timestamp) AS hour,
    count() AS event_count,
    uniqState(user_id) AS unique_users
FROM source_multiple_mvs
GROUP BY event_type, hour;

-- 插入测试数据（1亿行）
INSERT INTO source_multiple_mvs
SELECT 
    number AS id,
    now() - INTERVAL (number % 86400) SECOND AS timestamp,
    number % 100000 AS user_id,
    arrayJoin(['click', 'view', 'purchase', 'login', 'logout']) AS event_type,
    randCanonical() AS value,
    toString(number % 1000) AS properties
FROM numbers(100000000);

-- 记录测试结果
SELECT 
    '4 Multiple Materialized Views' AS test_scenario,
    query_duration_ms AS insert_duration_ms,
    read_rows,
    written_rows,
    memory_usage AS memory_usage_bytes,
    formatReadableSize(memory_usage) AS memory_usage_readable
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE 'INSERT INTO source_multiple_mvs%'
ORDER BY query_start_time DESC
LIMIT 1;

-- ================================
-- 6. 综合性能比较
-- ================================

-- 创建综合性能比较表
CREATE TABLE performance_comparison (
    scenario String,
    insert_duration_ms UInt64,
    read_rows UInt64,
    written_rows UInt64,
    memory_usage_bytes UInt64,
    performance_impact_percent Float64
) ENGINE = MergeTree()
ORDER BY scenario;

-- 填充性能比较数据
INSERT INTO performance_comparison VALUES
(
    'No Materialized View',
    (SELECT query_duration_ms FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_no_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT read_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_no_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT written_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_no_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT memory_usage FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_no_mv%' ORDER BY query_start_time DESC LIMIT 1),
    0
),
(
    '1 Simple MV',
    (SELECT query_duration_ms FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_1_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT read_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_1_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT written_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_1_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT memory_usage FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_1_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (
        SELECT round(t1.query_duration_ms * 100.0 / t0.query_duration_ms - 100, 2)
        FROM system.query_log t0, system.query_log t1
        WHERE t0.event_date = today() AND t0.type = 'QueryFinish' AND t0.query LIKE 'INSERT INTO source_no_mv%'
          AND t1.event_date = today() AND t1.type = 'QueryFinish' AND t1.query LIKE 'INSERT INTO source_1_mv%'
        ORDER BY t0.query_start_time DESC, t1.query_start_time DESC
        LIMIT 1
    )
),
(
    '1 Complex MV',
    (SELECT query_duration_ms FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_complex_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT read_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_complex_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT written_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_complex_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT memory_usage FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_complex_mv%' ORDER BY query_start_time DESC LIMIT 1),
    (
        SELECT round(t1.query_duration_ms * 100.0 / t0.query_duration_ms - 100, 2)
        FROM system.query_log t0, system.query_log t1
        WHERE t0.event_date = today() AND t0.type = 'QueryFinish' AND t0.query LIKE 'INSERT INTO source_no_mv%'
          AND t1.event_date = today() AND t1.type = 'QueryFinish' AND t1.query LIKE 'INSERT INTO source_complex_mv%'
        ORDER BY t0.query_start_time DESC, t1.query_start_time DESC
        LIMIT 1
    )
),
(
    '4 Multiple MVs',
    (SELECT query_duration_ms FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_multiple_mvs%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT read_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_multiple_mvs%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT written_rows FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_multiple_mvs%' ORDER BY query_start_time DESC LIMIT 1),
    (SELECT memory_usage FROM system.query_log WHERE event_date = today() AND type = 'QueryFinish' AND query LIKE 'INSERT INTO source_multiple_mvs%' ORDER BY query_start_time DESC LIMIT 1),
    (
        SELECT round(t1.query_duration_ms * 100.0 / t0.query_duration_ms - 100, 2)
        FROM system.query_log t0, system.query_log t1
        WHERE t0.event_date = today() AND t0.type = 'QueryFinish' AND t0.query LIKE 'INSERT INTO source_no_mv%'
          AND t1.event_date = today() AND t1.type = 'QueryFinish' AND t1.query LIKE 'INSERT INTO source_multiple_mvs%'
        ORDER BY t0.query_start_time DESC, t1.query_start_time DESC
        LIMIT 1
    )
);

-- 查看性能比较结果
SELECT 
    scenario,
    insert_duration_ms,
    formatReadableSize(memory_usage_bytes) AS memory_usage,
    performance_impact_percent
FROM performance_comparison
ORDER BY performance_impact_percent;

-- ================================
-- 7. 资源使用分析
-- ================================

-- 创建资源使用分析表
CREATE TABLE resource_usage_analysis (
    scenario String,
    metric_name String,
    metric_value Float64,
    readable_value String
) ENGINE = MergeTree()
ORDER BY (scenario, metric_name);

-- 插入资源使用数据
INSERT INTO resource_usage_analysis
WITH all_queries AS (
    SELECT 
        CASE 
            WHEN query LIKE 'INSERT INTO source_no_mv%' THEN 'No MV'
            WHEN query LIKE 'INSERT INTO source_1_mv%' THEN '1 Simple MV'
            WHEN query LIKE 'INSERT INTO source_complex_mv%' THEN '1 Complex MV'
            WHEN query LIKE 'INSERT INTO source_multiple_mvs%' THEN '4 Multiple MVs'
        END AS scenario,
        read_rows,
        read_bytes,
        written_rows,
        written_bytes,
        memory_usage,
        peak_memory_usage,
        query_duration_ms
    FROM system.query_log
    WHERE event_date = today()
      AND type = 'QueryFinish'
      AND query LIKE 'INSERT INTO source_%'
)
SELECT 
    scenario,
    'Read Rows' AS metric_name,
    read_rows AS metric_value,
    formatReadableQuantity(read_rows) AS readable_value
FROM all_queries
GROUP BY scenario, read_rows

UNION ALL

SELECT 
    scenario,
    'Read Bytes' AS metric_name,
    read_bytes AS metric_value,
    formatReadableSize(read_bytes) AS readable_value
FROM all_queries
GROUP BY scenario, read_bytes

UNION ALL

SELECT 
    scenario,
    'Written Rows' AS metric_name,
    written_rows AS metric_value,
    formatReadableQuantity(written_rows) AS readable_value
FROM all_queries
GROUP BY scenario, written_rows

UNION ALL

SELECT 
    scenario,
    'Written Bytes' AS metric_name,
    written_bytes AS metric_value,
    formatReadableSize(written_bytes) AS readable_value
FROM all_queries
GROUP BY scenario, written_bytes

UNION ALL

SELECT 
    scenario,
    'Memory Usage' AS metric_name,
    memory_usage AS metric_value,
    formatReadableSize(memory_usage) AS readable_value
FROM all_queries
GROUP BY scenario, memory_usage

UNION ALL

SELECT 
    scenario,
    'Peak Memory Usage' AS metric_name,
    peak_memory_usage AS metric_value,
    formatReadableSize(peak_memory_usage) AS readable_value
FROM all_queries
GROUP BY scenario, peak_memory_usage

UNION ALL

SELECT 
    scenario,
    'Insert Duration (ms)' AS metric_name,
    query_duration_ms AS metric_value,
    toString(query_duration_ms) AS readable_value
FROM all_queries
GROUP BY scenario, query_duration_ms;

-- 查看资源使用分析结果
SELECT 
    scenario,
    metric_name,
    readable_value
FROM resource_usage_analysis
ORDER BY scenario, metric_name;

-- ================================
-- 8. 物化视图状态检查
-- ================================

-- 检查物化视图状态
SELECT 
    database,
    name AS view_name,
    create_table_query,
    as_select_query,
    target_database,
    target_table,
    is_populate
FROM system.tables
WHERE engine = 'MaterializedView'
  AND database = 'mv_performance_test'
ORDER BY name;

-- 检查目标表状态
SELECT 
    table,
    count() AS part_count,
    sum(rows) AS total_rows,
    sum(data_uncompressed_bytes) AS uncompressed_bytes,
    sum(data_compressed_bytes) AS compressed_bytes,
    formatReadableSize(sum(data_compressed_bytes)) AS compressed_size
FROM system.parts
WHERE database = 'mv_performance_test'
  AND active = 1
GROUP BY table
ORDER BY total_rows DESC;

-- ================================
-- 9. 写入放大效应分析
-- ================================

-- 创建写入放大分析表
CREATE TABLE write_amplification_analysis (
    scenario String,
    source_rows UInt64,
    target_rows UInt64,
    amplification_factor Float64
) ENGINE = MergeTree()
ORDER BY scenario;

-- 计算写入放大效应
INSERT INTO write_amplification_analysis
WITH source_rows AS (
    SELECT count() AS row_count FROM source_no_mv
),
target_rows_1mv AS (
    SELECT sum(rows) AS total_rows 
    FROM system.parts 
    WHERE database = 'mv_performance_test' 
      AND table = 'target_1_simple'
      AND active = 1
),
target_rows_complex AS (
    SELECT sum(rows) AS total_rows 
    FROM system.parts 
    WHERE database = 'mv_performance_test' 
      AND table = 'target_complex'
      AND active = 1
),
target_rows_multiple AS (
    SELECT sum(rows) AS total_rows 
    FROM system.parts 
    WHERE database = 'mv_performance_test' 
      AND table IN ('target_basic_events', 'target_daily_stats', 'target_user_stats', 'target_event_distribution')
      AND active = 1
)
SELECT 
    '1 Simple MV' AS scenario,
    (SELECT row_count FROM source_rows) AS source_rows,
    (SELECT total_rows FROM target_rows_1mv) AS target_rows,
    (SELECT total_rows * 1.0 / row_count FROM target_rows_1mv, source_rows) AS amplification_factor

UNION ALL

SELECT 
    '1 Complex MV' AS scenario,
    (SELECT row_count FROM source_rows) AS source_rows,
    (SELECT total_rows FROM target_rows_complex) AS target_rows,
    (SELECT total_rows * 1.0 / row_count FROM target_rows_complex, source_rows) AS amplification_factor

UNION ALL

SELECT 
    '4 Multiple MVs' AS scenario,
    (SELECT row_count FROM source_rows) AS source_rows,
    (SELECT total_rows FROM target_rows_multiple) AS target_rows,
    (SELECT total_rows * 1.0 / row_count FROM target_rows_multiple, source_rows) AS amplification_factor;

-- 查看写入放大效应分析结果
SELECT 
    scenario,
    formatReadableQuantity(source_rows) AS source_rows,
    formatReadableQuantity(target_rows) AS target_rows,
    round(amplification_factor, 2) AS amplification_factor
FROM write_amplification_analysis
ORDER BY amplification_factor;

-- ================================
-- 10. 清理测试环境
-- ================================

-- 取消注释以下内容以清理测试环境
/*
DROP DATABASE IF EXISTS mv_performance_test;
*/

-- ================================
-- 11. 测试报告生成
-- ================================

-- 生成综合测试报告
WITH performance_data AS (
    SELECT 
        scenario,
        insert_duration_ms,
        performance_impact_percent
    FROM performance_comparison
),
resource_data AS (
    SELECT 
        scenario,
        readable_value AS memory_usage
    FROM resource_usage_analysis
    WHERE metric_name = 'Memory Usage'
),
amplification_data AS (
    SELECT 
        scenario,
        amplification_factor
    FROM write_amplification_analysis
)
SELECT 
    p.scenario,
    formatReadableTimeSpan(p.insert_duration_ms / 1000) AS insert_duration,
    round(p.performance_impact_percent, 2) AS performance_impact_percent,
    r.memory_usage,
    round(a.amplification_factor, 2) AS write_amplification_factor
FROM performance_data p
LEFT JOIN resource_data r ON p.scenario = r.scenario
LEFT JOIN amplification_data a ON p.scenario = a.scenario
ORDER BY performance_impact_percent;

-- 生成优化建议
WITH max_impact AS (
    SELECT max(performance_impact_percent) AS max_impact
    FROM performance_comparison
)
SELECT 
    CASE 
        WHEN max_impact > 200 THEN 'High: Consider reducing the number or complexity of materialized views'
        WHEN max_impact > 100 THEN 'Medium: Optimize materialized views for better performance'
        WHEN max_impact > 50 THEN 'Low: Materialized views have acceptable impact on write performance'
        ELSE 'Minimal: Materialized views have negligible impact on write performance'
    END AS performance_recommendation
FROM max_impact;