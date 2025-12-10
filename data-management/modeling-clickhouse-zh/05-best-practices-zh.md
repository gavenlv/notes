# 5. ETL与ClickHouse职责划分最佳实践

## 5.1 核心划分原则

合理的职责划分是构建高效数据架构的关键。以下原则指导ETL层与ClickHouse层之间的扫描逻辑分配：

### 5.1.1 数据预处理优先原则
- **ETL层**: 负责数据清洗、格式转换、基础验证
- **ClickHouse层**: 专注于数据分析和查询优化

### 5.1.2 计算复杂度原则
- **简单计算**: 在ETL层完成
- **复杂计算**: 在ClickHouse层利用其计算能力

### 5.1.3 实时性要求原则
- **实时处理**: Flink流处理
- **准实时**: ClickHouse物化视图
- **批处理**: BigQuery批量ETL

## 5.2 具体职责划分指南

### 5.2.1 数据清洗和转换

#### ETL层职责
```python
# 应在ETL层完成的数据处理
def etl_data_processing(raw_data):
    # 1. 数据格式验证
    if not validate_data_format(raw_data):
        return None
    
    # 2. 数据类型转换
    converted_data = convert_data_types(raw_data)
    
    # 3. 数据标准化
    standardized_data = standardize_data(converted_data)
    
    # 4. 基础数据清洗
    cleaned_data = basic_data_cleaning(standardized_data)
    
    return cleaned_data
```

#### ClickHouse层职责
```sql
-- 应在ClickHouse层避免的复杂转换
-- 不推荐：在查询时进行复杂的数据转换
SELECT
    jsonExtractString(event_data, 'user.name') as user_name,  -- 复杂JSON解析
    parseDateTimeBestEffort(event_time_str) as event_time,    -- 时间格式解析
    multiIf(amount > 100, 'high', amount > 50, 'medium', 'low') as amount_level  -- 复杂条件判断
FROM raw_events;
```

### 5.2.2 数据聚合计算

#### ETL层预聚合
```sql
-- 在BigQuery中进行的预聚合
CREATE TABLE pre_aggregated_data AS
SELECT
    event_date,
    user_id,
    event_type,
    COUNT(*) as event_count,
    SUM(amount) as total_amount
FROM raw_events
GROUP BY event_date, user_id, event_type;
```

#### ClickHouse层聚合优化
```sql
-- 在ClickHouse中利用其聚合能力
-- 创建物化视图进行实时聚合
CREATE MATERIALIZED VIEW realtime_aggregates
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_type)
AS SELECT
    event_date,
    event_type,
    countState() as count_state,
    sumState(amount) as sum_state,
    uniqState(user_id) as unique_users_state
FROM events
GROUP BY event_date, event_type;

-- 查询物化视图
SELECT
    event_date,
    event_type,
    countMerge(count_state) as total_count,
    sumMerge(sum_state) as total_amount,
    uniqMerge(unique_users_state) as unique_users
FROM realtime_aggregates
WHERE event_date = '2024-01-15';
```

## 5.3 性能优化策略

### 5.3.1 数据加载优化

#### ETL层数据分区
```python
# Flink数据分区策略
stream.keyBy(lambda event: event["user_id"] % 10)  # 按用户ID哈希分区
stream.window(TumblingProcessingTimeWindows.of(Time.minutes(5)))  # 时间窗口
```

#### ClickHouse数据分区
```sql
-- ClickHouse表分区设计
CREATE TABLE events (
    event_date Date,
    event_timestamp DateTime64(3),
    user_id UInt64,
    event_type LowCardinality(String),
    amount Decimal(10,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)  -- 按月分区
ORDER BY (event_date, user_id, event_type)  -- 排序键
SETTINGS index_granularity = 8192;  -- 索引粒度
```

### 5.3.2 查询性能优化

#### 避免在ClickHouse中进行复杂计算
```sql
-- 不推荐：在ClickHouse中进行复杂的数据转换
SELECT
    arrayJoin(splitByChar(',', tags)) as tag,  -- 数组展开
    count() as count
FROM events
WHERE event_date >= '2024-01-01'
GROUP BY tag;

-- 推荐：在ETL层预处理标签数据
-- ETL层将标签数组展开为多行
-- ClickHouse直接进行简单的计数查询
```

#### 利用ClickHouse的向量化执行
```sql
-- ClickHouse优化的聚合查询
SELECT
    event_type,
    count(),
    sum(amount),
    avg(amount),
    quantile(0.5)(amount) as median_amount
FROM events
WHERE event_date >= '2024-01-01'
GROUP BY event_type
ORDER BY sum(amount) DESC;
```

## 5.4 数据质量保证

### 5.4.1 ETL层数据质量检查
```python
# 数据质量验证函数
def validate_data_quality(data):
    checks = [
        # 完整性检查
        lambda d: all(key in d for key in required_fields),
        # 有效性检查
        lambda d: is_valid_timestamp(d['event_timestamp']),
        lambda d: 0 <= d['amount'] <= 1000000,
        # 一致性检查
        lambda d: d['event_type'] in valid_event_types,
    ]
    
    return all(check(data) for check in checks)
```

### 5.4.2 ClickHouse层数据监控
```sql
-- 数据质量监控查询
SELECT
    event_date,
    count() as total_records,
    countIf(amount IS NULL) as null_amounts,
    countIf(event_timestamp > now()) as future_timestamps,
    countIf(event_type NOT IN ('view', 'click', 'purchase')) as invalid_types,
    round((count() - countIf(amount IS NULL)) * 100.0 / count(), 2) as completeness_rate
FROM events
WHERE event_date >= today() - 7
GROUP BY event_date
ORDER BY event_date DESC;
```

## 5.5 容错和恢复策略

### 5.5.1 ETL层容错
```java
// Flink检查点和状态管理
env.enableCheckpointing(60000);  // 60秒检查点间隔
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
```

### 5.5.2 ClickHouse数据备份
```sql
-- ClickHouse数据备份策略
-- 使用ALTER TABLE FREEZE进行快照备份
ALTER TABLE events FREEZE;

-- 使用INSERT INTO进行数据迁移
INSERT INTO backup_events
SELECT * FROM events
WHERE event_date >= '2024-01-01';
```

## 5.6 监控和告警

### 5.6.1 关键监控指标

#### ETL层监控
- **数据处理延迟**: 端到端延迟统计
- **数据吞吐量**: 记录/秒处理能力
- **错误率**: 数据处理失败比例
- **资源使用**: CPU、内存、网络使用情况

#### ClickHouse层监控
- **查询响应时间**: P50/P95/P99延迟
- **查询吞吐量**: QPS（每秒查询数）
- **数据压缩率**: 存储效率指标
- **系统资源**: 磁盘IO、内存使用

### 5.6.2 告警策略
```yaml
# 监控告警配置示例
alerts:
  - name: "etl_processing_delay"
    condition: "processing_delay > 300"  # 延迟超过5分钟
    severity: "warning"
    
  - name: "clickhouse_query_timeout"
    condition: "query_timeout_rate > 0.05"  # 查询超时率超过5%
    severity: "critical"
    
  - name: "data_quality_anomaly"
    condition: "data_completeness_rate < 0.95"  # 数据完整性低于95%
    severity: "warning"
```

## 5.7 总结

合理的ETL与ClickHouse职责划分是构建高效数据架构的关键。通过遵循数据预处理优先、计算复杂度分级和实时性要求等原则，可以充分发挥各技术组件的优势，提升整体系统性能。下一章将通过实际案例展示这些原则的具体应用。