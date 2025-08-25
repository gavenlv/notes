# BigQuery 最佳实践 / BigQuery Best Practices

## 中文版

### 表设计和数据建模

#### 分区策略
```sql
-- 推荐：使用日期列进行分区
CREATE TABLE `project.dataset.table_name`
PARTITION BY DATE(created_at)
AS SELECT * FROM source_table;
```

#### 聚簇策略
```sql
-- 在分区内按常用查询列进行聚簇
CREATE TABLE `project.dataset.table_name`
PARTITION BY DATE(created_at)
CLUSTER BY user_id, event_type
AS SELECT * FROM source_table;
```

### 查询优化

#### SELECT 语句优化
```sql
-- 只选择需要的列
SELECT user_id, event_type, created_at
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01');
```

#### WHERE 子句优化
```sql
-- 使用分区列进行过滤
SELECT *
FROM `project.dataset.events`
WHERE _PARTITIONTIME >= TIMESTAMP('2023-01-01')
  AND created_at >= TIMESTAMP('2023-01-01');
```

### 数据加载最佳实践

#### 批量加载
```sql
LOAD DATA INTO `project.dataset.table_name`
FROM FILES(
  format = 'CSV',
  uris = ['gs://bucket/path/to/data/*.csv'],
  skip_leading_rows = 1
);
```

### 性能监控

#### 查询性能分析
```sql
-- 使用EXPLAIN查看查询计划
EXPLAIN SELECT user_id, COUNT(*) as event_count
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01')
GROUP BY user_id;
```

---

## English Version

### Table Design and Data Modeling

#### Partitioning Strategy
```sql
-- Recommended: Use date columns for partitioning
CREATE TABLE `project.dataset.table_name`
PARTITION BY DATE(created_at)
AS SELECT * FROM source_table;
```

#### Clustering Strategy
```sql
-- Cluster by commonly queried columns within partitions
CREATE TABLE `project.dataset.table_name`
PARTITION BY DATE(created_at)
CLUSTER BY user_id, event_type
AS SELECT * FROM source_table;
```

### Query Optimization

#### SELECT Statement Optimization
```sql
-- Only select needed columns
SELECT user_id, event_type, created_at
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01');
```

#### WHERE Clause Optimization
```sql
-- Use partition columns for filtering
SELECT *
FROM `project.dataset.events`
WHERE _PARTITIONTIME >= TIMESTAMP('2023-01-01')
  AND created_at >= TIMESTAMP('2023-01-01');
```

### Data Loading Best Practices

#### Batch Loading
```sql
LOAD DATA INTO `project.dataset.table_name`
FROM FILES(
  format = 'CSV',
  uris = ['gs://bucket/path/to/data/*.csv'],
  skip_leading_rows = 1
);
```

### Performance Monitoring

#### Query Performance Analysis
```sql
-- Use EXPLAIN to view query plans
EXPLAIN SELECT user_id, COUNT(*) as event_count
FROM `project.dataset.events`
WHERE created_at >= TIMESTAMP('2023-01-01')
GROUP BY user_id;
```