# ClickHouse集群监控实践案例与最佳实践

## 1. 生产环境监控实践案例

### 1.1 大型电商平台监控案例

**业务背景**：
- 日订单量：1000万+
- 数据量：10TB+/天
- 集群规模：20节点，5分片4副本
- 查询QPS：5000+

**监控架构**：
```yaml
监控体系组成：
- Prometheus: 3节点集群
- Grafana: 2节点负载均衡
- Alertmanager: 高可用配置
- Consul: 服务发现
- ClickHouse Exporter: 每节点部署
```

**关键监控指标**：
```sql
-- 核心业务指标
SELECT 
    toStartOfMinute(event_time) as minute,
    countIf(query LIKE '%SELECT%orders%') as order_queries,
    countIf(query LIKE '%INSERT%orders%') as order_inserts,
    avgIf(query_duration_ms, query LIKE '%SELECT%orders%') as avg_order_query_time,
    quantile(0.95)(If(query_duration_ms, query LIKE '%SELECT%orders%')) as p95_order_query_time
FROM clusterAllReplicas('production', system.query_log)
WHERE event_date = today()
  AND type = 'QueryFinish'
GROUP BY minute
ORDER BY minute DESC;
```

**告警策略**：
- 订单查询P95 > 2秒：Warning级别
- 订单插入失败率 > 1%：Critical级别
- 副本延迟 > 5分钟：Warning级别
- 节点宕机：Critical级别

### 1.2 实时数据分析平台案例

**业务特点**：
- 实时数据流处理
- 复杂聚合查询
- 高并发读写
- 数据时效性要求高

**监控重点**：
```sql
-- 实时数据处理监控
SELECT 
    toStartOfMinute(now()) as current_minute,
    count() as active_queries,
    sum(read_rows) as rows_processed_per_second,
    avg(query_duration_ms) as avg_query_time,
    countIf(query_duration_ms > 10000) as slow_queries
FROM clusterAllReplicas('realtime', system.processes)
WHERE query != ''
GROUP BY current_minute;

-- 数据新鲜度监控
SELECT 
    database,
    table,
    max(modification_time) as latest_data_time,
    now() - max(modification_time) as data_freshness
FROM clusterAllReplicas('realtime', system.parts)
WHERE active = 1
GROUP BY database, table
HAVING data_freshness > INTERVAL 5 MINUTE
ORDER BY data_freshness DESC;
```

## 2. 性能优化监控实践

### 2.1 查询性能瓶颈识别

**慢查询分析**：
```sql
-- 识别慢查询模式
SELECT 
    normalizeQuery(query) as query_pattern,
    count() as execution_count,
    avg(query_duration_ms) as avg_duration,
    max(query_duration_ms) as max_duration,
    sum(read_rows) as total_rows_read,
    sum(read_bytes) as total_bytes_read,
    sum(memory_usage) as total_memory_used,
    groupArray(DISTINCT user) as users,
    min(query_start_time) as first_seen,
    max(query_start_time) as last_seen
FROM clusterAllReplicas('production', system.query_log)
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
  AND query_duration_ms > 5000
GROUP BY query_pattern
HAVING execution_count > 10
ORDER BY avg_duration DESC
LIMIT 20;

-- 查询资源消耗分析
SELECT 
    user,
    count() as query_count,
    sum(read_rows) as total_rows_read,
    formatReadableSize(sum(read_bytes)) as total_data_read,
    formatReadableSize(sum(memory_usage)) as total_memory_used,
    round(sum(read_bytes) * 100.0 / (SELECT sum(read_bytes) FROM system.query_log 
                                   WHERE event_date >= today() - 1 AND type = 'QueryFinish'), 2) as data_percentage
FROM clusterAllReplicas('production', system.query_log)
WHERE event_date >= today() - 1
  AND type = 'QueryFinish'
GROUP BY user
ORDER BY total_data_read DESC;
```

**索引使用分析**：
```sql
-- 索引效率监控
SELECT 
    database,
    table,
    sum(rows) as total_rows,
    sum(primary_key_bytes_in_memory) as index_size,
    round(sum(primary_key_bytes_in_memory) * 100.0 / sum(bytes), 2) as index_overhead_percent,
    avg(granularity) as avg_granularity
FROM clusterAllReplicas('production', system.parts)
WHERE active = 1
GROUP BY database, table
HAVING index_overhead_percent > 10
ORDER BY index_overhead_percent DESC;
```

### 2.2 内存优化监控

**内存使用分析**：
```sql
-- 内存使用趋势
SELECT 
    toStartOfMinute(event_time) as minute,
    avg(MemoryTracking) as avg_memory_usage,
    max(MemoryTracking) as peak_memory_usage,
    avg(MemoryUsage) as system_memory_usage
FROM clusterAllReplicas('production', system.metric_log)
WHERE event_date = today()
  AND metric IN ('MemoryTracking', 'MemoryUsage')
GROUP BY minute
ORDER BY minute DESC
LIMIT 60;

-- 内存分配模式分析
SELECT 
    toStartOfHour(event_time) as hour,
    count() as allocations,
    sum(bytes_allocated) as total_allocated,
    sum(bytes_freed) as total_freed,
    sum(bytes_allocated) - sum(bytes_freed) as net_allocated,
    avg(alloc_size) as avg_allocation_size
FROM clusterAllReplicas('production', system.part_log)
WHERE event_date >= today() - 1
  AND event_type = 'NewPart'
GROUP BY hour
ORDER BY hour DESC;
```

## 3. 容量规划与资源管理

### 3.1 存储容量预测

```sql
-- 数据增长趋势分析
WITH daily_stats AS (
    SELECT 
        event_date,
        database,
        sum(rows) as daily_rows,
        sum(bytes) as daily_bytes
    FROM clusterAllReplicas('production', system.parts)
    WHERE active = 1
      AND event_date >= today() - 30
    GROUP BY event_date, database
)
SELECT 
    database,
    avg(daily_rows) as avg_daily_rows,
    avg(daily_bytes) as avg_daily_bytes,
    stddevPop(daily_rows) as rows_stddev,
    stddevPop(daily_bytes) as bytes_stddev,
    
    -- 预测30天后的数据量
    avg(daily_rows) * 30 as predicted_rows_30d,
    avg(daily_bytes) * 30 as predicted_bytes_30d,
    
    -- 考虑标准差的安全边界
    (avg(daily_rows) + 2 * stddevPop(daily_rows)) * 30 as safe_predicted_rows_30d,
    (avg(daily_bytes) + 2 * stddevPop(daily_bytes)) * 30 as safe_predicted_bytes_30d
FROM daily_stats
GROUP BY database
ORDER BY avg_daily_bytes DESC;

-- 表级别容量预测
SELECT 
    database,
    table,
    count() as part_count,
    sum(rows) as total_rows,
    formatReadableSize(sum(bytes)) as total_size,
    
    -- 数据压缩率
    round(sum(data_uncompressed_bytes) * 100.0 / sum(data_compressed_bytes), 2) as compression_ratio,
    
    -- 分区策略分析
    uniq(partition) as partition_count,
    avg(rows) as avg_partition_rows,
    
    -- 增长趋势
    dateDiff('day', min(min_date), max(max_date)) as data_age_days,
    sum(rows) / greatest(dateDiff('day', min(min_date), max(max_date)), 1) as avg_daily_growth
FROM clusterAllReplicas('production', system.parts)
WHERE active = 1
GROUP BY database, table
ORDER BY total_rows DESC
LIMIT 50;
```

### 3.2 资源使用效率监控

```sql
-- CPU使用效率
SELECT 
    toStartOfHour(event_time) as hour,
    shard_num,
    avg(CPUUsage) as avg_cpu_usage,
    max(CPUUsage) as peak_cpu_usage,
    
    -- 查询效率指标
    sum(Query) as total_queries,
    sum(SelectQuery) as select_queries,
    round(sum(SelectQuery) * 100.0 / sum(Query), 2) as select_query_ratio,
    
    -- 资源利用率
    round(avg(CPUUsage) * 100.0 / 100, 2) as cpu_utilization_percent
FROM clusterAllReplicas('production', system.metric_log)
WHERE event_date = today()
  AND metric IN ('CPUUsage', 'Query', 'SelectQuery')
GROUP BY hour, shard_num
ORDER BY hour DESC, shard_num;

-- 磁盘IO效率
SELECT 
    toStartOfHour(event_time) as hour,
    shard_num,
    
    -- 读写统计
    sum(Read) as total_reads,
    sum(Write) as total_writes,
    
    -- IO吞吐量
    formatReadableSize(sum(ReadBytes)) as total_read_bytes,
    formatReadableSize(sum(WriteBytes)) as total_write_bytes,
    
    -- IO效率指标
    round(avg(ReadBytes) / avg(Read), 2) as avg_read_size_bytes,
    round(avg(WriteBytes) / avg(Write), 2) as avg_write_size_bytes,
    
    -- 缓存命中率
    round(sum(MarkCacheHits) * 100.0 / (sum(MarkCacheHits) + sum(MarkCacheMisses)), 2) as mark_cache_hit_rate
FROM clusterAllReplicas('production', system.metric_log)
WHERE event_date = today()
  AND metric IN ('Read', 'Write', 'ReadBytes', 'WriteBytes', 'MarkCacheHits', 'MarkCacheMisses')
GROUP BY hour, shard_num
ORDER BY hour DESC, shard_num;
```

## 4. 高可用性监控实践

### 4.1 副本健康状态监控

```sql
-- 副本健康度评分
WITH replica_health AS (
    SELECT 
        database,
        table,
        replica_name,
        shard_num,
        
        -- 健康度指标
        CASE WHEN is_active = 1 THEN 1 ELSE 0 END as active_score,
        CASE WHEN is_readonly = 0 THEN 1 ELSE 0 END as writable_score,
        CASE WHEN is_session_expired = 0 THEN 1 ELSE 0 END as session_score,
        CASE WHEN replica_delay = 0 THEN 1 
             WHEN replica_delay < 60 THEN 0.8
             WHEN replica_delay < 300 THEN 0.5
             ELSE 0.2 END as sync_score,
        
        -- 队列状态
        CASE WHEN queue_size = 0 THEN 1
             WHEN queue_size < 100 THEN 0.8
             WHEN queue_size < 1000 THEN 0.5
             ELSE 0.2 END as queue_score
    FROM clusterAllReplicas('production', system.replicas)
    WHERE is_active = 1
)
SELECT 
    database,
    table,
    replica_name,
    shard_num,
    
    -- 综合健康度评分 (0-1)
    round((active_score + writable_score + session_score + sync_score + queue_score) / 5.0, 2) as health_score,
    
    -- 详细评分
    active_score,
    writable_score,
    session_score,
    sync_score,
    queue_score,
    
    -- 健康状态
    CASE 
        WHEN health_score >= 0.8 THEN 'HEALTHY'
        WHEN health_score >= 0.6 THEN 'DEGRADED'
        ELSE 'UNHEALTHY'
    END as health_status
FROM replica_health
ORDER BY health_score ASC, database, table
LIMIT 50;
```

### 4.2 故障切换监控

```sql
-- 故障切换历史分析
SELECT 
    toStartOfHour(event_time) as hour,
    database,
    table,
    
    -- 故障统计
    countIf(type = 'LeaderElection') as leader_elections,
    countIf(type = 'ReplicaRecovery') as replica_recoveries,
    countIf(type = 'PartitionMove') as partition_moves,
    
    -- 故障影响
    sum(affected_rows) as total_affected_rows,
    avg(duration_ms) as avg_recovery_time,
    
    -- 成功率
    round(countIf(success = 1) * 100.0 / count(), 2) as success_rate
FROM clusterAllReplicas('production', system.replication_log)
WHERE event_date >= today() - 7
  AND type IN ('LeaderElection', 'ReplicaRecovery', 'PartitionMove')
GROUP BY hour, database, table
ORDER BY hour DESC, leader_elections DESC;
```

## 5. 安全监控实践

### 5.1 访问安全监控

```sql
-- 用户访问行为分析
SELECT 
    user,
    
    -- 访问统计
    count() as total_queries,
    countDistinct(initial_address) as unique_ips,
    
    -- 时间分布
    min(query_start_time) as first_access,
    max(query_start_time) as last_access,
    
    -- 查询类型分析
    countIf(query LIKE '%SELECT%') as select_queries,
    countIf(query LIKE '%INSERT%') as insert_queries,
    countIf(query LIKE '%ALTER%') as alter_queries,
    countIf(query LIKE '%DROP%') as drop_queries,
    
    -- 权限使用
    countIf(query LIKE '%GRANT%') as grant_queries,
    countIf(query LIKE '%REVOKE%') as revoke_queries,
    
    -- 异常行为检测
    countIf(query_duration_ms > 30000) as long_running_queries,
    countIf(read_rows > 1000000) as large_read_queries,
    countIf(memory_usage > 1000000000) as high_memory_queries
FROM clusterAllReplicas('production', system.query_log)
WHERE event_date = today()
  AND type = 'QueryFinish'
GROUP BY user
HAVING total_queries > 10
ORDER BY total_queries DESC;

-- IP访问模式分析
SELECT 
    initial_address as ip_address,
    
    -- 访问统计
    count() as total_requests,
    uniq(user) as unique_users,
    
    -- 时间模式
    min(query_start_time) as first_request,
    max(query_start_time) as last_request,
    
    -- 请求频率
    count() / greatest(dateDiff('minute', min(query_start_time), max(query_start_time)), 1) as requests_per_minute,
    
    -- 异常检测
    countIf(query_duration_ms > 10000) as slow_requests,
    countIf(result_rows = 0) as empty_results,
    countIf(exception != '') as failed_requests
FROM clusterAllReplicas('production', system.query_log)
WHERE event_date = today()
  AND type = 'QueryFinish'
GROUP BY ip_address
HAVING total_requests > 100
ORDER BY requests_per_minute DESC;
```

### 5.2 数据安全监控

```sql
-- 数据变更监控
SELECT 
    toStartOfHour(event_time) as hour,
    database,
    table,
    user,
    
    -- 变更统计
    countIf(type = 'Insert') as insert_operations,
    countIf(type = 'Delete') as delete_operations,
    countIf(type = 'Update') as update_operations,
    
    -- 影响范围
    sum(affected_rows) as total_affected_rows,
    
    -- 变更模式
    uniq(initial_address) as source_ips,
    
    -- 风险评估
    CASE 
        WHEN delete_operations > 0 THEN 'HIGH_RISK'
        WHEN update_operations > 1000 THEN 'MEDIUM_RISK'
        ELSE 'LOW_RISK'
    END as risk_level
FROM clusterAllReplicas('production', system.query_log)
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query_type IN ('Insert', 'Delete', 'Update')
GROUP BY hour, database, table, user
ORDER BY hour DESC, total_affected_rows DESC;
```

## 6. 监控报表与告警优化

### 6.1 自定义监控报表

```sql
-- 每日健康报告
SELECT 
    'ClickHouse集群健康报告' as report_title,
    today() as report_date,
    
    -- 集群概览
    (SELECT count() FROM system.clusters WHERE cluster = 'production') as total_nodes,
    (SELECT count() FROM system.clusters WHERE cluster = 'production' AND is_active = 1) as active_nodes,
    (SELECT count() FROM system.replicas WHERE is_active = 1) as total_replicas,
    (SELECT count() FROM system.replicas WHERE is_active = 1 AND replica_delay = 0) as synced_replicas,
    
    -- 性能指标
    (SELECT round(avg(query_duration_ms), 2) FROM system.query_log 
     WHERE event_date = today() AND type = 'QueryFinish') as avg_query_time_ms,
    (SELECT count() FROM system.query_log 
     WHERE event_date = today() AND type = 'QueryFinish') as total_queries,
    
    -- 资源使用
    (SELECT formatReadableSize(sum(bytes_on_disk)) FROM system.parts WHERE active = 1) as total_data_size,
    (SELECT round(avg(MemoryUsage), 2) FROM system.asynchronous_metrics 
     WHERE metric = 'MemoryUsage') as avg_memory_usage_percent,
    
    -- 错误统计
    (SELECT count() FROM system.query_log 
     WHERE event_date = today() AND type = 'ExceptionWhileProcessing') as total_errors,
    
    -- 健康评分
    CASE 
        WHEN active_nodes = total_nodes AND synced_replicas = total_replicas THEN 'EXCELLENT'
        WHEN active_nodes >= total_nodes * 0.9 AND synced_replicas >= total_replicas * 0.9 THEN 'GOOD'
        WHEN active_nodes >= total_nodes * 0.8 THEN 'FAIR'
        ELSE 'POOR'
    END as overall_health;
```

### 6.2 告警优化策略

**告警收敛策略**：
```yaml
alert_rules:
  - name: "clickhouse-cluster-health"
    rules:
      # 基础告警
      - alert: "NodeDown"
        expr: "up{job='clickhouse'} == 0"
        for: "2m"
        labels:
          severity: "critical"
        annotations:
          summary: "ClickHouse节点 {{ $labels.instance }} 宕机"
      
      # 性能告警（带收敛）
      - alert: "QueryPerformanceDegraded"
        expr: |
          (
            quantile_over_time(0.95, clickhouse_query_duration_seconds[5m]) > 10
            and
            rate(clickhouse_query_total[5m]) > 10
          )
        for: "5m"
        labels:
          severity: "warning"
        annotations:
          summary: "查询性能下降，P95响应时间 {{ $value }} 秒"
      
      # 资源告警（分级）
      - alert: "MemoryUsageHigh"
        expr: "clickhouse_memory_usage_ratio > 0.8"
        for: "5m"
        labels:
          severity: "warning"
      
      - alert: "MemoryUsageCritical"
        expr: "clickhouse_memory_usage_ratio > 0.9"
        for: "2m"
        labels:
          severity: "critical"
```

**告警路由策略**：
```yaml
route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 1h
  
  routes:
    - match:
        severity: critical
      receiver: 'pager-duty'
      group_wait: 5s
      
    - match:
        severity: warning
      receiver: 'slack'
      group_wait: 30s
      
    - match_re:
        alertname: '.*[Pp]erformance.*'
      receiver: 'performance-team'
```

## 7. 总结与最佳实践

### 7.1 监控体系成熟度模型

| 成熟度等级 | 监控能力 | 告警策略 | 自动化程度 |
|-----------|----------|----------|------------|
| **基础级** | 基础指标监控 | 简单阈值告警 | 手动处理 |
| **标准级** | 多层监控体系 | 分级告警策略 | 半自动化 |
| **高级级** | 预测性监控 | 智能告警收敛 | 全自动化 |
| **专家级** | AIOps监控 | 自愈系统 | 智能化运维 |

### 7.2 持续改进流程

1. **监控指标评审**：每月审查监控指标的有效性
2. **告警优化**：基于误报率调整告警阈值
3. **性能基准**：建立性能基准并定期测试
4. **容量规划**：基于历史数据预测未来需求
5. **故障演练**：定期进行故障恢复演练

通过实施这些最佳实践，可以建立健壮、高效的ClickHouse集群监控体系，确保业务连续性和数据可靠性。