-- ClickHouse 2副本集群监控SQL查询 - treasurycluster
-- 集群名称: treasurycluster
-- 副本数量: 2

-- ===========================================
-- 1. 集群健康状态监控
-- ===========================================

-- 1.1 集群节点状态检查
SELECT 
    shard_num,
    host_name,
    host_address,
    is_active,
    errors_count,
    slowdowns_count,
    estimated_recovery_time,
    replica_is_readonly,
    replica_is_session_expired
FROM system.clusters
WHERE cluster = 'treasurycluster'
ORDER BY shard_num, host_name;

-- 1.2 副本同步状态监控
SELECT 
    database,
    table,
    replica_name,
    is_leader,
    is_readonly,
    is_session_expired,
    future_parts,
    parts_to_check,
    queue_size,
    inserts_in_queue,
    merges_in_queue,
    log_max_index,
    log_pointer,
    total_replicas,
    active_replicas,
    replica_delay,
    CASE 
        WHEN replica_delay = 0 THEN 'SYNCED'
        WHEN replica_delay < 30 THEN 'MINOR_DELAY'
        WHEN replica_delay < 60 THEN 'MODERATE_DELAY'
        ELSE 'MAJOR_DELAY'
    END as delay_status
FROM system.replicas
WHERE is_active = 1
ORDER BY replica_delay DESC;

-- 1.3 副本延迟详细分析
SELECT 
    database,
    table,
    replica_name,
    replica_delay,
    queue_size,
    last_queue_update,
    dateDiff('second', last_queue_update, now()) as seconds_since_last_update
FROM system.replicas
WHERE is_active = 1 AND replica_delay > 0
ORDER BY replica_delay DESC
LIMIT 10;

-- ===========================================
-- 2. 性能监控
-- ===========================================

-- 2.1 查询性能统计（最近1小时）
SELECT 
    toStartOfMinute(query_start_time) as time_window,
    count() as query_count,
    round(avg(query_duration_ms), 2) as avg_duration_ms,
    round(quantile(0.95)(query_duration_ms), 2) as p95_duration_ms,
    round(quantile(0.99)(query_duration_ms), 2) as p99_duration_ms,
    sum(read_rows) as total_rows_read,
    sum(read_bytes) as total_bytes_read,
    sum(result_rows) as total_rows_returned,
    formatReadableSize(sum(memory_usage)) as total_memory_used
FROM clusterAllReplicas('treasurycluster', system.query_log)
WHERE event_time >= now() - INTERVAL 1 HOUR
  AND type = 'QueryFinish'
GROUP BY time_window
ORDER BY time_window DESC
LIMIT 60;

-- 2.2 慢查询分析（最近24小时）
SELECT 
    user,
    initial_address,
    normalizeQuery(query) as query_pattern,
    count() as execution_count,
    round(avg(query_duration_ms), 2) as avg_duration_ms,
    round(max(query_duration_ms), 2) as max_duration_ms,
    sum(read_rows) as total_rows_read,
    formatReadableSize(sum(read_bytes)) as total_data_read,
    min(query_start_time) as first_seen,
    max(query_start_time) as last_seen
FROM clusterAllReplicas('treasurycluster', system.query_log)
WHERE event_time >= now() - INTERVAL 24 HOUR
  AND type = 'QueryFinish'
  AND query_duration_ms > 10000  -- 超过10秒的查询
GROUP BY user, initial_address, query_pattern
HAVING execution_count > 1
ORDER BY avg_duration_ms DESC
LIMIT 20;

-- 2.3 查询失败分析
SELECT 
    toStartOfHour(event_time) as hour,
    user,
    initial_address,
    exception,
    count() as failure_count,
    substring(query, 1, 200) as query_preview
FROM clusterAllReplicas('treasurycluster', system.query_log)
WHERE event_time >= today()
  AND type = 'ExceptionWhileProcessing'
GROUP BY hour, user, initial_address, exception, query_preview
ORDER BY hour DESC, failure_count DESC
LIMIT 20;

-- ===========================================
-- 3. 资源使用监控
-- ===========================================

-- 3.1 内存使用监控
SELECT 
    metric,
    value,
    formatReadableSize(value) as readable_size,
    description
FROM system.asynchronous_metrics
WHERE metric LIKE '%Memory%'
ORDER BY value DESC
LIMIT 15;

-- 3.2 磁盘使用分析
SELECT 
    database,
    table,
    count() as part_count,
    sum(rows) as total_rows,
    formatReadableSize(sum(bytes)) as total_size,
    formatReadableSize(sum(primary_key_bytes_in_memory)) as index_size,
    round(sum(data_uncompressed_bytes) * 100.0 / sum(data_compressed_bytes), 2) as compression_ratio,
    min(min_date) as oldest_data,
    max(max_date) as newest_data
FROM system.parts 
WHERE active = 1
  AND database NOT IN ('system')
GROUP BY database, table
ORDER BY total_size DESC
LIMIT 20;

-- 3.3 表级别存储分析
SELECT 
    database,
    table,
    engine,
    formatReadableSize(total_bytes) as table_size,
    total_rows,
    partition_key,
    sorting_key,
    metadata_modification_time
FROM system.tables
WHERE database NOT IN ('system')
ORDER BY total_bytes DESC
LIMIT 15;

-- ===========================================
-- 4. 数据分布和一致性监控
-- ===========================================

-- 4.1 副本间数据一致性检查
WITH replica_stats AS (
    SELECT 
        database,
        table,
        replica_name,
        sum(rows) as total_rows,
        sum(bytes) as total_bytes
    FROM clusterAllReplicas('treasurycluster', system.parts)
    WHERE active = 1
    GROUP BY database, table, replica_name
)
SELECT 
    database,
    table,
    count(DISTINCT replica_name) as replica_count,
    max(total_rows) - min(total_rows) as row_difference,
    formatReadableSize(max(total_bytes) - min(total_bytes)) as size_difference,
    CASE 
        WHEN max(total_rows) - min(total_rows) = 0 THEN 'CONSISTENT'
        WHEN max(total_rows) - min(total_rows) < 100 THEN 'MINOR_DIFF'
        ELSE 'INCONSISTENT'
    END as consistency_status
FROM replica_stats
GROUP BY database, table
HAVING replica_count = 2  -- 2副本集群
ORDER BY row_difference DESC
LIMIT 10;

-- 4.2 数据增长趋势分析
SELECT 
    toDate(event_date) as date,
    database,
    table,
    sum(rows) as daily_rows,
    formatReadableSize(sum(bytes)) as daily_size,
    sum(rows) - lag(sum(rows)) OVER (PARTITION BY database, table ORDER BY event_date) as row_growth,
    round((sum(rows) - lag(sum(rows)) OVER (PARTITION BY database, table ORDER BY event_date)) * 100.0 / 
          lag(sum(rows)) OVER (PARTITION BY database, table ORDER BY event_date), 2) as growth_percentage
FROM clusterAllReplicas('treasurycluster', system.parts)
WHERE active = 1
  AND event_date >= today() - INTERVAL 7 DAY
  AND database NOT IN ('system')
GROUP BY date, database, table
ORDER BY date DESC, daily_size DESC
LIMIT 30;

-- ===========================================
-- 5. 系统级监控
-- ===========================================

-- 5.1 后台任务监控
SELECT 
    database,
    table,
    type,
    elapsed,
    progress,
    is_ready,
    num_parts,
    source_part_names,
    result_part_name,
    partition_id,
    create_time
FROM clusterAllReplicas('treasurycluster', system.merges)
WHERE database NOT IN ('system')
ORDER BY elapsed DESC
LIMIT 10;

-- 5.2 突变操作监控
SELECT 
    database,
    table,
    command,
    create_time,
    block_numbers.number,
    parts_to_do,
    is_done
FROM clusterAllReplicas('treasurycluster', system.mutations)
WHERE database NOT IN ('system')
  AND is_done = 0
ORDER BY create_time DESC
LIMIT 10;

-- 5.3 ZooKeeper状态检查
SELECT 
    name,
    value,
    data_length,
    num_children,
    ctime,
    mtime,
    version
FROM system.zookeeper
WHERE path = '/clickhouse'
LIMIT 20;

-- ===========================================
-- 6. 实时监控视图
-- ===========================================

-- 6.1 创建实时监控视图
CREATE VIEW IF NOT EXISTS treasurycluster_realtime_monitor AS
SELECT 
    now() as check_time,
    
    -- 集群状态
    (SELECT count() FROM system.clusters WHERE cluster = 'treasurycluster' AND is_active = 1) as active_nodes,
    (SELECT count() FROM system.clusters WHERE cluster = 'treasurycluster') as total_nodes,
    
    -- 副本状态
    (SELECT count() FROM system.replicas WHERE replica_delay = 0 AND is_active = 1) as synced_replicas,
    (SELECT count() FROM system.replicas WHERE replica_delay > 0 AND replica_delay <= 60 AND is_active = 1) as minor_delay_replicas,
    (SELECT count() FROM system.replicas WHERE replica_delay > 60 AND is_active = 1) as major_delay_replicas,
    
    -- 内存使用
    (SELECT value FROM system.asynchronous_metrics WHERE metric = 'MemoryTracking') as memory_used,
    (SELECT value FROM system.asynchronous_metrics WHERE metric = 'MemoryLimit') as memory_limit,
    
    -- 查询统计（最近5分钟）
    (SELECT count() FROM system.query_log WHERE event_time >= now() - INTERVAL 5 MINUTE AND type = 'QueryFinish') as queries_5min,
    (SELECT count() FROM system.query_log WHERE event_time >= now() - INTERVAL 5 MINUTE AND type = 'ExceptionWhileProcessing') as failed_queries_5min,
    
    -- 数据统计
    (SELECT sum(rows) FROM system.parts WHERE active = 1) as total_rows,
    (SELECT sum(bytes) FROM system.parts WHERE active = 1) as total_bytes;

-- 6.2 查看实时监控状态
SELECT * FROM treasurycluster_realtime_monitor;

-- ===========================================
-- 7. 健康度评分
-- ===========================================

-- 7.1 集群健康度综合评分
WITH health_metrics AS (
    SELECT
        -- 节点可用性 (权重: 30%)
        (SELECT countIf(is_active = 1) * 100.0 / count() FROM system.clusters WHERE cluster = 'treasurycluster') as node_availability,
        
        -- 副本同步率 (权重: 25%)
        (SELECT countIf(replica_delay = 0) * 100.0 / count() FROM system.replicas WHERE is_active = 1) as replica_sync_rate,
        
        -- 查询成功率 (权重: 20%)
        (SELECT countIf(type = 'QueryFinish') * 100.0 / count() FROM system.query_log 
         WHERE event_time >= now() - INTERVAL 1 HOUR) as query_success_rate,
        
        -- 内存使用率 (权重: 15%)
        100 - (SELECT value * 100.0 / (SELECT value FROM system.asynchronous_metrics WHERE metric = 'MemoryLimit') 
               FROM system.asynchronous_metrics WHERE metric = 'MemoryTracking') as memory_availability,
        
        -- 错误率 (权重: 10%)
        (SELECT 100 - countIf(type = 'ExceptionWhileProcessing') * 100.0 / count() FROM system.query_log 
         WHERE event_time >= now() - INTERVAL 1 HOUR) as error_free_rate
)
SELECT
    round((node_availability * 0.3 + replica_sync_rate * 0.25 + query_success_rate * 0.2 + 
           memory_availability * 0.15 + error_free_rate * 0.1), 2) as overall_health_score,
    
    node_availability,
    replica_sync_rate,
    query_success_rate,
    memory_availability,
    error_free_rate,
    
    CASE
        WHEN overall_health_score >= 95 THEN 'EXCELLENT'
        WHEN overall_health_score >= 85 THEN 'GOOD'
        WHEN overall_health_score >= 75 THEN 'FAIR'
        ELSE 'POOR'
    END as health_status
FROM health_metrics;