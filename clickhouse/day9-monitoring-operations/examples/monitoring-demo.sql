-- Day 9: ClickHouse 监控和运维示例
-- =============================================

-- 1. 系统监控基础查询
-- =============================================

-- 检查ClickHouse版本和基本信息
SELECT 'Basic System Information' as demo_section;
SELECT 
    version() as clickhouse_version,
    hostName() as hostname,
    uptime() as uptime_seconds,
    formatReadableSize(total_memory) as total_memory
FROM system.one
CROSS JOIN (
    SELECT value as total_memory 
    FROM system.asynchronous_metrics 
    WHERE metric = 'MemoryTotal'
);

-- 检查当前运行的查询
SELECT 'Current Running Queries' as demo_section;
SELECT 
    query_id,
    user,
    elapsed,
    formatReadableSize(memory_usage) as memory_used,
    formatReadableSize(read_bytes) as bytes_read,
    read_rows,
    substring(query, 1, 100) as query_preview
FROM system.processes 
WHERE query != ''
ORDER BY elapsed DESC;

-- 2. 查询性能监控
-- =============================================

-- 创建监控数据库
CREATE DATABASE IF NOT EXISTS monitoring;
USE monitoring;

-- 创建查询性能汇总表
DROP TABLE IF EXISTS query_performance_summary;
CREATE TABLE query_performance_summary (
    date Date,
    hour UInt8,
    query_count UInt32,
    avg_duration_ms Float64,
    p50_duration_ms Float64,
    p95_duration_ms Float64,
    p99_duration_ms Float64,
    total_read_rows UInt64,
    total_read_bytes UInt64,
    error_count UInt32
) ENGINE = MergeTree()
ORDER BY (date, hour)
PARTITION BY toYYYYMM(date);

-- 插入历史性能数据汇总
INSERT INTO query_performance_summary
SELECT 
    toDate(event_time) as date,
    toHour(event_time) as hour,
    count() as query_count,
    avg(query_duration_ms) as avg_duration_ms,
    quantile(0.5)(query_duration_ms) as p50_duration_ms,
    quantile(0.95)(query_duration_ms) as p95_duration_ms,
    quantile(0.99)(query_duration_ms) as p99_duration_ms,
    sum(read_rows) as total_read_rows,
    sum(read_bytes) as total_read_bytes,
    countIf(type = 'ExceptionWhileProcessing') as error_count
FROM system.query_log 
WHERE event_date >= today() - 7
  AND type IN ('QueryFinish', 'ExceptionWhileProcessing')
GROUP BY date, hour
ORDER BY date DESC, hour DESC;

-- 查看性能汇总数据
SELECT 'Query Performance Summary (Last 24 Hours)' as demo_section;
SELECT 
    hour,
    query_count,
    round(avg_duration_ms, 2) as avg_duration_ms,
    round(p95_duration_ms, 2) as p95_duration_ms,
    formatReadableSize(total_read_bytes) as total_bytes_read,
    error_count,
    round(error_count * 100.0 / query_count, 2) as error_rate_percent
FROM query_performance_summary 
WHERE date = today()
ORDER BY hour DESC
LIMIT 24;

-- 3. 慢查询分析
-- =============================================

-- 创建慢查询分析表
DROP TABLE IF EXISTS slow_query_analysis;
CREATE TABLE slow_query_analysis (
    query_date Date,
    normalized_query String,
    execution_count UInt32,
    avg_duration_ms Float64,
    max_duration_ms UInt64,
    avg_memory_usage UInt64,
    avg_read_rows UInt64,
    total_read_bytes UInt64
) ENGINE = MergeTree()
ORDER BY (query_date, avg_duration_ms)
PARTITION BY toYYYYMM(query_date);

-- 分析慢查询模式
INSERT INTO slow_query_analysis
SELECT 
    toDate(event_time) as query_date,
    normalizeQuery(query) as normalized_query,
    count() as execution_count,
    avg(query_duration_ms) as avg_duration_ms,
    max(query_duration_ms) as max_duration_ms,
    avg(memory_usage) as avg_memory_usage,
    avg(read_rows) as avg_read_rows,
    sum(read_bytes) as total_read_bytes
FROM system.query_log 
WHERE event_date >= today() - 3
  AND type = 'QueryFinish'
  AND query_duration_ms > 5000  -- 慢查询阈值5秒
  AND query NOT LIKE '%system.%'  -- 排除系统查询
GROUP BY query_date, normalized_query
HAVING execution_count >= 2  -- 至少执行2次
ORDER BY avg_duration_ms DESC;

-- 查看TOP慢查询
SELECT 'Top Slow Queries Analysis' as demo_section;
SELECT 
    normalized_query,
    execution_count,
    round(avg_duration_ms, 2) as avg_duration_ms,
    max_duration_ms,
    formatReadableSize(avg_memory_usage) as avg_memory_used,
    formatReadableSize(total_read_bytes) as total_bytes_read
FROM slow_query_analysis 
WHERE query_date >= today() - 1
ORDER BY avg_duration_ms DESC
LIMIT 10;

-- 4. 用户行为分析
-- =============================================

-- 创建用户活动统计表
DROP TABLE IF EXISTS user_activity_stats;
CREATE TABLE user_activity_stats (
    date Date,
    user String,
    query_count UInt32,
    avg_duration_ms Float64,
    total_read_rows UInt64,
    total_read_bytes UInt64,
    error_count UInt32,
    unique_queries UInt32
) ENGINE = MergeTree()
ORDER BY (date, user)
PARTITION BY toYYYYMM(date);

-- 统计用户活动数据
INSERT INTO user_activity_stats
SELECT 
    toDate(event_time) as date,
    user,
    count() as query_count,
    avg(query_duration_ms) as avg_duration_ms,
    sum(read_rows) as total_read_rows,
    sum(read_bytes) as total_read_bytes,
    countIf(type = 'ExceptionWhileProcessing') as error_count,
    uniq(normalizeQuery(query)) as unique_queries
FROM system.query_log 
WHERE event_date >= today() - 7
  AND user != ''
GROUP BY date, user;

-- 用户活动分析
SELECT 'User Activity Analysis (Today)' as demo_section;
SELECT 
    user,
    query_count,
    round(avg_duration_ms, 2) as avg_duration_ms,
    formatReadableSize(total_read_bytes) as data_processed,
    error_count,
    round(error_count * 100.0 / query_count, 2) as error_rate_percent,
    unique_queries
FROM user_activity_stats 
WHERE date = today()
ORDER BY query_count DESC
LIMIT 10;

-- 5. 系统资源监控
-- =============================================

-- 创建系统资源监控表
DROP TABLE IF EXISTS system_resource_monitoring;
CREATE TABLE system_resource_monitoring (
    timestamp DateTime,
    cpu_usage_percent Float64,
    memory_usage_percent Float64,
    disk_usage_percent Float64,
    active_queries UInt32,
    total_connections UInt32
) ENGINE = MergeTree()
ORDER BY timestamp
PARTITION BY toYYYYMM(timestamp);

-- 模拟系统资源数据插入（实际环境中这些数据来自metric_log）
INSERT INTO system_resource_monitoring
SELECT 
    toDateTime(toUnixTimestamp(now()) - number * 60) as timestamp,
    rand() % 30 + 20 as cpu_usage_percent,  -- 模拟CPU使用率 20-50%
    rand() % 40 + 30 as memory_usage_percent,  -- 模拟内存使用率 30-70%
    rand() % 20 + 60 as disk_usage_percent,  -- 模拟磁盘使用率 60-80%
    rand() % 10 + 1 as active_queries,  -- 模拟活跃查询数 1-10
    rand() % 50 + 10 as total_connections  -- 模拟连接数 10-60
FROM numbers(1440)  -- 最近24小时，每分钟一个数据点
WHERE timestamp >= now() - INTERVAL 24 HOUR;

-- 资源使用趋势分析
SELECT 'System Resource Trends (Last 6 Hours)' as demo_section;
SELECT 
    toStartOfHour(timestamp) as hour,
    round(avg(cpu_usage_percent), 2) as avg_cpu_percent,
    round(avg(memory_usage_percent), 2) as avg_memory_percent,
    round(avg(disk_usage_percent), 2) as avg_disk_percent,
    round(avg(active_queries), 2) as avg_active_queries,
    round(avg(total_connections), 2) as avg_connections
FROM system_resource_monitoring 
WHERE timestamp >= now() - INTERVAL 6 HOUR
GROUP BY hour
ORDER BY hour DESC;

-- 6. 错误监控和分析
-- =============================================

-- 创建错误监控表
DROP TABLE IF EXISTS error_monitoring;
CREATE TABLE error_monitoring (
    error_date Date,
    error_hour UInt8,
    error_type String,
    error_count UInt32,
    affected_users Array(String),
    sample_queries Array(String)
) ENGINE = MergeTree()
ORDER BY (error_date, error_hour, error_type)
PARTITION BY toYYYYMM(error_date);

-- 插入错误监控数据
INSERT INTO error_monitoring
SELECT 
    toDate(event_time) as error_date,
    toHour(event_time) as error_hour,
    if(exception != '', exception, 'Unknown Error') as error_type,
    count() as error_count,
    groupUniqArray(user) as affected_users,
    groupArray(substring(query, 1, 200)) as sample_queries
FROM system.query_log 
WHERE event_date >= today() - 3
  AND type IN ('ExceptionBeforeStart', 'ExceptionWhileProcessing')
GROUP BY error_date, error_hour, error_type
ORDER BY error_date DESC, error_hour DESC;

-- 错误统计分析
SELECT 'Error Analysis (Last 24 Hours)' as demo_section;
SELECT 
    error_hour,
    error_type,
    error_count,
    length(affected_users) as unique_users_affected,
    if(length(sample_queries) > 0, sample_queries[1], '') as sample_query
FROM error_monitoring 
WHERE error_date = today()
ORDER BY error_count DESC
LIMIT 15;

-- 7. 表和数据库存储分析
-- =============================================

-- 数据库存储统计
SELECT 'Database Storage Analysis' as demo_section;
SELECT 
    database,
    count() as table_count,
    sum(rows) as total_rows,
    formatReadableSize(sum(data_compressed_bytes)) as compressed_size,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed_size,
    round(sum(data_compressed_bytes) / sum(data_uncompressed_bytes), 3) as compression_ratio,
    formatReadableSize(sum(primary_key_bytes_in_memory)) as index_size
FROM system.parts 
WHERE active = 1
GROUP BY database
ORDER BY sum(data_compressed_bytes) DESC;

-- 分区存储分析
SELECT 'Partition Storage Analysis' as demo_section;
SELECT 
    database,
    table,
    partition,
    rows,
    formatReadableSize(data_compressed_bytes) as compressed_size,
    round(compression_ratio, 3) as compression_ratio,
    modification_time
FROM system.parts 
WHERE active = 1
  AND database NOT IN ('system', '_temporary_and_external_tables')
ORDER BY data_compressed_bytes DESC
LIMIT 20;

-- 8. 查询模式分析
-- =============================================

-- 创建查询模式分析表
DROP TABLE IF EXISTS query_pattern_analysis;
CREATE TABLE query_pattern_analysis (
    analysis_date Date,
    query_pattern String,
    execution_count UInt32,
    avg_duration_ms Float64,
    total_data_processed UInt64,
    peak_hour UInt8
) ENGINE = MergeTree()
ORDER BY (analysis_date, execution_count)
PARTITION BY toYYYYMM(analysis_date);

-- 分析查询模式
INSERT INTO query_pattern_analysis
SELECT 
    toDate(event_time) as analysis_date,
    CASE 
        WHEN query LIKE 'SELECT%FROM%WHERE%' THEN 'Filtered SELECT'
        WHEN query LIKE 'SELECT%FROM%GROUP BY%' THEN 'Aggregation Query'
        WHEN query LIKE 'SELECT%FROM%ORDER BY%' THEN 'Sorted Query'
        WHEN query LIKE 'INSERT%' THEN 'Data Insert'
        WHEN query LIKE 'CREATE%' THEN 'DDL Operation'
        WHEN query LIKE 'ALTER%' THEN 'Table Modification'
        ELSE 'Other Queries'
    END as query_pattern,
    count() as execution_count,
    avg(query_duration_ms) as avg_duration_ms,
    sum(read_bytes) as total_data_processed,
    argMax(toHour(event_time), count()) as peak_hour
FROM system.query_log 
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
  AND query NOT LIKE '%system.%'
GROUP BY analysis_date, query_pattern
ORDER BY analysis_date DESC, execution_count DESC;

-- 查询模式统计
SELECT 'Query Pattern Analysis (Last 3 Days)' as demo_section;
SELECT 
    query_pattern,
    sum(execution_count) as total_executions,
    round(avg(avg_duration_ms), 2) as avg_duration_ms,
    formatReadableSize(sum(total_data_processed)) as total_data_processed,
    argMax(peak_hour, sum(execution_count)) as most_active_hour
FROM query_pattern_analysis 
WHERE analysis_date >= today() - 3
GROUP BY query_pattern
ORDER BY total_executions DESC;

-- 9. 性能基准测试
-- =============================================

-- 创建性能测试表
DROP TABLE IF EXISTS performance_benchmark;
CREATE TABLE performance_benchmark (
    test_id UInt32,
    test_name String,
    test_query String,
    execution_time_ms UInt64,
    rows_processed UInt64,
    bytes_processed UInt64,
    memory_used UInt64,
    test_timestamp DateTime
) ENGINE = MergeTree()
ORDER BY test_timestamp;

-- 插入基准测试数据
INSERT INTO performance_benchmark VALUES
(1, 'Simple Aggregation', 'SELECT count() FROM numbers(1000000)', 0, 0, 0, 0, now()),
(2, 'Complex JOIN', 'SELECT * FROM numbers(100000) n1 JOIN numbers(100000) n2 ON n1.number = n2.number', 0, 0, 0, 0, now()),
(3, 'GROUP BY Query', 'SELECT number % 1000, count() FROM numbers(1000000) GROUP BY number % 1000', 0, 0, 0, 0, now());

-- 执行基准测试查询并记录性能
SELECT 'Performance Benchmark Tests' as demo_section;

-- 测试1: 简单聚合
SET max_execution_time = 300;
SELECT 
    '简单聚合测试' as test_name,
    count() as result_count,
    'SELECT count() FROM numbers(1000000)' as test_query
FROM numbers(1000000);

-- 测试2: 复杂分组
SELECT 
    '复杂分组测试' as test_name,
    count() as group_count,
    'SELECT number % 1000, count() FROM numbers(1000000) GROUP BY number % 1000' as test_query
FROM (
    SELECT number % 1000 as group_key, count() as cnt
    FROM numbers(1000000) 
    GROUP BY number % 1000
);

-- 测试3: 数据处理性能
SELECT 
    '数据处理测试' as test_name,
    count() as processed_rows,
    'Complex calculation on large dataset' as test_query
FROM (
    SELECT 
        number,
        sqrt(number) as sqrt_val,
        sin(number / 1000.0) as sin_val,
        toString(number) as str_val
    FROM numbers(500000)
    WHERE number % 7 = 0
);

-- 10. 监控告警模拟
-- =============================================

-- 创建告警规则表
DROP TABLE IF EXISTS alert_rules;
CREATE TABLE alert_rules (
    rule_id UInt32,
    rule_name String,
    metric_query String,
    threshold_value Float64,
    operator String,
    severity String,
    description String,
    is_active UInt8
) ENGINE = Memory;

-- 插入告警规则
INSERT INTO alert_rules VALUES
(1, 'High Query Duration', 'SELECT quantile(0.95)(query_duration_ms) FROM system.query_log WHERE event_time >= now() - 300', 10000, '>', 'warning', '95%查询时间超过10秒', 1),
(2, 'High Error Rate', 'SELECT countIf(type = ''ExceptionWhileProcessing'') * 100.0 / count() FROM system.query_log WHERE event_time >= now() - 300', 5, '>', 'critical', '错误率超过5%', 1),
(3, 'Low Query Count', 'SELECT count() FROM system.query_log WHERE event_time >= now() - 300', 10, '<', 'warning', '查询数量异常偏低', 1),
(4, 'High Memory Usage', 'SELECT avg(memory_usage) FROM system.processes', 1000000000, '>', 'warning', '平均内存使用超过1GB', 1);

-- 执行告警检查
SELECT 'Alert Rules Evaluation' as demo_section;
SELECT 
    rule_name,
    threshold_value,
    operator,
    severity,
    CASE 
        WHEN rule_name = 'High Query Duration' THEN (
            SELECT quantile(0.95)(query_duration_ms) 
            FROM system.query_log 
            WHERE event_time >= now() - 300 
              AND type = 'QueryFinish'
        )
        WHEN rule_name = 'High Error Rate' THEN (
            SELECT if(count() > 0, countIf(type = 'ExceptionWhileProcessing') * 100.0 / count(), 0)
            FROM system.query_log 
            WHERE event_time >= now() - 300
        )
        WHEN rule_name = 'Low Query Count' THEN (
            SELECT count() 
            FROM system.query_log 
            WHERE event_time >= now() - 300
        )
        ELSE 0
    END as current_value,
    CASE 
        WHEN rule_name = 'High Query Duration' AND (
            SELECT quantile(0.95)(query_duration_ms) 
            FROM system.query_log 
            WHERE event_time >= now() - 300 AND type = 'QueryFinish'
        ) > threshold_value THEN 'ALERT'
        WHEN rule_name = 'High Error Rate' AND (
            SELECT if(count() > 0, countIf(type = 'ExceptionWhileProcessing') * 100.0 / count(), 0)
            FROM system.query_log 
            WHERE event_time >= now() - 300
        ) > threshold_value THEN 'ALERT'
        WHEN rule_name = 'Low Query Count' AND (
            SELECT count() 
            FROM system.query_log 
            WHERE event_time >= now() - 300
        ) < threshold_value THEN 'ALERT'
        ELSE 'OK'
    END as alert_status
FROM alert_rules 
WHERE is_active = 1;

-- 11. 清理和优化
-- =============================================

-- 表优化
OPTIMIZE TABLE query_performance_summary FINAL;
OPTIMIZE TABLE slow_query_analysis FINAL;
OPTIMIZE TABLE user_activity_stats FINAL;
OPTIMIZE TABLE system_resource_monitoring FINAL;

-- 统计信息更新
SELECT 'Monitoring Tables Summary' as demo_section;
SELECT 
    'monitoring' as database,
    name as table_name,
    total_rows,
    formatReadableSize(total_bytes) as size_on_disk
FROM system.tables 
WHERE database = 'monitoring'
  AND engine LIKE '%MergeTree%'
ORDER BY total_rows DESC;

-- 最终监控报告
SELECT '=== Day 9 Monitoring Demo Summary ===' as summary_section;

SELECT 
    'Monitoring Tables Created' as metric,
    toString(count()) as value
FROM system.tables 
WHERE database = 'monitoring'

UNION ALL

SELECT 
    'Performance Records Analyzed' as metric,
    toString(sum(total_rows)) as value
FROM system.tables 
WHERE database = 'monitoring'
  AND name LIKE '%performance%'

UNION ALL

SELECT 
    'Alert Rules Configured' as metric,
    toString(count()) as value
FROM alert_rules

UNION ALL

SELECT 
    'Recent Queries Monitored' as metric,
    toString(count()) as value
FROM system.query_log 
WHERE event_date = today()

UNION ALL

SELECT 
    'System Uptime' as metric,
    toString(uptime()) || ' seconds' as value
FROM system.one;

-- 演示完成提示
SELECT 
    '🎉 Day 9 监控和运维演示完成！' as message,
    '📊 已创建完整的监控体系和分析报告' as summary;

-- 注意：此演示展示了监控和运维的核心概念和实践
-- 生产环境中需要结合Prometheus、Grafana等外部监控工具 