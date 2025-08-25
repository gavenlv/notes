# BigQuery 成本优化 / BigQuery Cost Optimization

## 中文版

### 成本结构理解

BigQuery 的成本主要由两部分组成：
- **存储成本**：按数据存储量收费
- **查询成本**：按处理的数据量收费

### 存储成本优化

#### 1. 数据生命周期管理

```sql
-- 设置表的过期时间
CREATE TABLE `project.dataset.table_name`
(
  id INT64,
  data STRING,
  created_at TIMESTAMP
)
PARTITION BY DATE(created_at)
OPTIONS(
  expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
);
```

#### 2. 分区表优化

```sql
-- 删除旧分区以节省存储成本
DELETE FROM `project.dataset.events`
WHERE _PARTITIONTIME < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY);
```

#### 3. 数据压缩和格式优化

```sql
-- 使用优化的数据格式
CREATE TABLE `project.dataset.optimized_table`
PARTITION BY DATE(created_at)
CLUSTER BY user_id
AS SELECT * FROM source_table;
```

### 查询成本优化

#### 1. 减少扫描的数据量

```sql
-- 使用分区列过滤
SELECT user_id, event_type
FROM `project.dataset.events`
WHERE _PARTITIONTIME >= TIMESTAMP('2023-01-01')
  AND created_at >= TIMESTAMP('2023-01-01')
  AND user_id = '12345';

-- 避免全表扫描
-- 错误示例：SELECT * FROM large_table WHERE user_id = '12345';
```

#### 2. 选择特定列

```sql
-- 只选择需要的列
SELECT user_id, event_type, created_at
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01');

-- 避免 SELECT *
-- 错误示例：SELECT * FROM large_table;
```

#### 3. 使用聚簇表

```sql
-- 创建聚簇表以提高查询效率
CREATE TABLE `project.dataset.clustered_events`
PARTITION BY DATE(created_at)
CLUSTER BY user_id, event_type
AS SELECT * FROM source_events;
```

### 高级优化技术

#### 1. 物化视图

```sql
-- 创建物化视图以缓存常用查询结果
CREATE MATERIALIZED VIEW `project.dataset.daily_user_stats`
AS SELECT 
  DATE(created_at) as date,
  user_id,
  COUNT(*) as event_count,
  COUNT(DISTINCT event_type) as event_types
FROM `project.dataset.events`
GROUP BY DATE(created_at), user_id;
```

#### 2. 查询缓存

```sql
-- 启用查询缓存（默认启用）
-- 重复执行相同查询会使用缓存结果
SELECT user_id, COUNT(*) as event_count
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01')
GROUP BY user_id;
```

#### 3. 数据采样

```sql
-- 使用数据采样进行探索性分析
SELECT user_id, event_type
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01')
TABLESAMPLE SYSTEM (10 PERCENT);
```

### 成本监控和分析

#### 1. 查询成本分析

```sql
-- 查看查询成本统计
SELECT 
  creation_time,
  query,
  total_bytes_processed,
  total_slot_ms,
  state,
  -- 估算成本（基于处理的数据量）
  total_bytes_processed / POWER(2, 40) * 5 as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY total_bytes_processed DESC;
```

#### 2. 存储成本分析

```sql
-- 查看表存储信息
SELECT 
  table_schema,
  table_name,
  total_rows,
  total_logical_bytes,
  total_physical_bytes,
  -- 存储成本估算
  total_physical_bytes / POWER(2, 30) * 0.02 as storage_cost_usd_per_month
FROM `project.dataset.INFORMATION_SCHEMA.TABLES`
ORDER BY total_physical_bytes DESC;
```

### 最佳实践总结

#### 1. 查询优化
- 始终使用分区列进行过滤
- 只选择需要的列
- 使用聚簇表提高查询效率
- 利用查询缓存
- 避免 CROSS JOIN

#### 2. 存储优化
- 设置适当的表过期时间
- 定期清理旧分区
- 使用合适的数据类型
- 考虑数据压缩

#### 3. 监控和告警
- 设置成本预算告警
- 定期审查高成本查询
- 监控存储增长趋势
- 使用成本分析工具

---

## English Version

### Understanding Cost Structure

BigQuery costs consist of two main components:
- **Storage Costs**: Charged based on data storage volume
- **Query Costs**: Charged based on data processing volume

### Storage Cost Optimization

#### 1. Data Lifecycle Management

```sql
-- Set table expiration time
CREATE TABLE `project.dataset.table_name`
(
  id INT64,
  data STRING,
  created_at TIMESTAMP
)
PARTITION BY DATE(created_at)
OPTIONS(
  expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
);
```

#### 2. Partitioned Table Optimization

```sql
-- Delete old partitions to save storage costs
DELETE FROM `project.dataset.events`
WHERE _PARTITIONTIME < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY);
```

#### 3. Data Compression and Format Optimization

```sql
-- Use optimized data formats
CREATE TABLE `project.dataset.optimized_table`
PARTITION BY DATE(created_at)
CLUSTER BY user_id
AS SELECT * FROM source_table;
```

### Query Cost Optimization

#### 1. Reduce Scanned Data Volume

```sql
-- Use partition columns for filtering
SELECT user_id, event_type
FROM `project.dataset.events`
WHERE _PARTITIONTIME >= TIMESTAMP('2023-01-01')
  AND created_at >= TIMESTAMP('2023-01-01')
  AND user_id = '12345';

-- Avoid full table scans
-- Bad example: SELECT * FROM large_table WHERE user_id = '12345';
```

#### 2. Select Specific Columns

```sql
-- Only select needed columns
SELECT user_id, event_type, created_at
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01');

-- Avoid SELECT *
-- Bad example: SELECT * FROM large_table;
```

#### 3. Use Clustered Tables

```sql
-- Create clustered tables to improve query efficiency
CREATE TABLE `project.dataset.clustered_events`
PARTITION BY DATE(created_at)
CLUSTER BY user_id, event_type
AS SELECT * FROM source_events;
```

### Advanced Optimization Techniques

#### 1. Materialized Views

```sql
-- Create materialized views to cache common query results
CREATE MATERIALIZED VIEW `project.dataset.daily_user_stats`
AS SELECT 
  DATE(created_at) as date,
  user_id,
  COUNT(*) as event_count,
  COUNT(DISTINCT event_type) as event_types
FROM `project.dataset.events`
GROUP BY DATE(created_at), user_id;
```

#### 2. Query Caching

```sql
-- Enable query caching (enabled by default)
-- Repeated execution of identical queries uses cached results
SELECT user_id, COUNT(*) as event_count
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01')
GROUP BY user_id;
```

#### 3. Data Sampling

```sql
-- Use data sampling for exploratory analysis
SELECT user_id, event_type
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01')
TABLESAMPLE SYSTEM (10 PERCENT);
```

### Cost Monitoring and Analysis

#### 1. Query Cost Analysis

```sql
-- View query cost statistics
SELECT 
  creation_time,
  query,
  total_bytes_processed,
  total_slot_ms,
  state,
  -- Estimate cost (based on processed data volume)
  total_bytes_processed / POWER(2, 40) * 5 as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY total_bytes_processed DESC;
```

#### 2. Storage Cost Analysis

```sql
-- View table storage information
SELECT 
  table_schema,
  table_name,
  total_rows,
  total_logical_bytes,
  total_physical_bytes,
  -- Storage cost estimation
  total_physical_bytes / POWER(2, 30) * 0.02 as storage_cost_usd_per_month
FROM `project.dataset.INFORMATION_SCHEMA.TABLES`
ORDER BY total_physical_bytes DESC;
```

### Best Practices Summary

#### 1. Query Optimization
- Always use partition columns for filtering
- Only select needed columns
- Use clustered tables to improve query efficiency
- Leverage query caching
- Avoid CROSS JOIN

#### 2. Storage Optimization
- Set appropriate table expiration times
- Regularly clean up old partitions
- Use appropriate data types
- Consider data compression

#### 3. Monitoring and Alerts
- Set up cost budget alerts
- Regularly review high-cost queries
- Monitor storage growth trends
- Use cost analysis tools