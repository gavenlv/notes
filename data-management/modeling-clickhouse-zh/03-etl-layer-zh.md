# 3. ETL层职责与扫描逻辑

## 3.1 ETL层核心职责

ETL（Extract, Transform, Load）层在现代数据架构中承担着关键的数据预处理和转换任务。合理的扫描逻辑划分对整体系统性能至关重要。

### 3.1.1 主要职责
- **数据抽取**: 从各种数据源获取数据
- **数据转换**: 清洗、格式化、标准化数据
- **数据加载**: 将处理后的数据加载到目标系统
- **数据质量**: 确保数据的准确性和一致性

## 3.2 Flink在ETL中的扫描逻辑

### 3.2.1 流式数据处理

Flink作为流处理引擎，适合处理实时数据流，其扫描逻辑设计如下：

```java
// 示例：Flink流式ETL作业
DataStream<RawData> rawStream = env
    .addSource(new KafkaSource<>("topic"))
    .map(new DataParser())           // 数据解析
    .filter(new DataValidator())     // 数据验证
    .keyBy(RawData::getUserId)       // 按用户分组
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
    .aggregate(new UserBehaviorAggregator())  // 用户行为聚合
    .map(new DataEnricher())         // 数据丰富
    .addSink(new ClickHouseSink());  // 写入ClickHouse
```

### 3.2.2 扫描逻辑划分

**应在Flink中处理的扫描逻辑**:
- 实时数据流处理
- 窗口聚合计算
- 数据格式转换
- 基础数据清洗
- 实时数据去重

**不应在Flink中处理的扫描逻辑**:
- 复杂的历史数据分析
- 大规模数据关联查询
- 多维度的数据聚合

## 3.3 BigQuery在ETL中的扫描逻辑

### 3.3.1 批处理ETL

BigQuery适合处理大规模批处理任务，其扫描逻辑设计如下：

```sql
-- 示例：BigQuery批处理ETL作业
CREATE OR REPLACE TABLE `project.dataset.cleaned_data` AS
SELECT 
    user_id,
    event_type,
    event_timestamp,
    -- 数据清洗和转换
    TRIM(event_data) as cleaned_data,
    CAST(amount AS NUMERIC) as numeric_amount,
    -- 基础聚合
    COUNT(*) OVER (PARTITION BY user_id) as user_event_count,
    -- 时间窗口计算
    TIMESTAMP_DIFF(event_timestamp, LAG(event_timestamp) 
        OVER (PARTITION BY user_id ORDER BY event_timestamp), SECOND) as time_diff
FROM `project.dataset.raw_data`
WHERE event_timestamp >= TIMESTAMP('2024-01-01')
  AND event_type IN ('click', 'view', 'purchase')
  AND amount IS NOT NULL;
```

### 3.3.2 扫描逻辑划分

**应在BigQuery中处理的扫描逻辑**:
- 大规模数据批量处理
- 复杂的数据转换逻辑
- 历史数据回溯分析
- 数据质量检查和修复
- 预聚合和汇总计算

**不应在BigQuery中处理的扫描逻辑**:
- 实时数据流处理
- 高频的交互式查询
- 需要低延迟的实时分析

## 3.4 ETL层扫描逻辑最佳实践

### 3.4.1 数据预处理策略

#### 数据清洗规则
```python
# 示例：数据清洗函数
def clean_and_transform_data(raw_data):
    # 1. 去除无效数据
    if not is_valid_data(raw_data):
        return None
    
    # 2. 格式标准化
    standardized_data = standardize_format(raw_data)
    
    # 3. 数据类型转换
    converted_data = convert_data_types(standardized_data)
    
    # 4. 数据丰富
    enriched_data = enrich_with_reference_data(converted_data)
    
    return enriched_data
```

#### 数据质量检查
```sql
-- 示例：数据质量SQL检查
WITH data_quality_checks AS (
    SELECT
        COUNT(*) as total_records,
        COUNT(DISTINCT user_id) as unique_users,
        SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) as null_amounts,
        SUM(CASE WHEN event_timestamp > CURRENT_TIMESTAMP() THEN 1 ELSE 0 END) as future_timestamps
    FROM raw_data
)
SELECT
    total_records,
    unique_users,
    -- 计算数据质量指标
    ROUND((total_records - null_amounts) * 100.0 / total_records, 2) as data_completeness_rate,
    ROUND((total_records - future_timestamps) * 100.0 / total_records, 2) as data_validity_rate
FROM data_quality_checks;
```

### 3.4.2 性能优化策略

#### Flink优化
```java
// Flink性能优化配置
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 设置并行度
env.setParallelism(4);

// 启用检查点
env.enableCheckpointing(60000);

// 状态后端配置
env.setStateBackend(new FsStateBackend("hdfs://checkpoints"));

// 内存配置
env.getConfig().setTaskManagerMemory(2048);
```

#### BigQuery优化
```sql
-- BigQuery查询优化
-- 使用分区表
CREATE TABLE partitioned_data
PARTITION BY DATE(event_timestamp)
AS SELECT * FROM raw_data;

-- 使用集群字段
CREATE TABLE clustered_data
CLUSTER BY user_id, event_type
AS SELECT * FROM raw_data;

-- 避免全表扫描
SELECT * FROM partitioned_data
WHERE event_timestamp >= '2024-01-01'
  AND event_timestamp < '2024-02-01';
```

## 3.5 与ClickHouse的协同工作

### 3.5.1 数据流向设计

```
数据源 → Flink(实时ETL) → ClickHouse(实时分析)
数据源 → BigQuery(批处理ETL) → ClickHouse(历史分析)
```

### 3.5.2 数据格式约定

ETL层应输出ClickHouse友好的数据格式：
- 使用合适的数值类型
- 避免复杂的嵌套结构
- 提供明确的时间戳字段
- 包含必要的数据分区字段

## 3.6 监控和运维

### 3.6.1 关键监控指标
- **数据处理吞吐量**: 记录/秒
- **数据处理延迟**: 端到端延迟
- **数据质量指标**: 完整性、准确性
- **系统资源使用**: CPU、内存、网络

### 3.6.2 告警策略
- 数据流中断告警
- 数据处理延迟告警
- 数据质量异常告警
- 系统资源告警

## 3.7 总结

ETL层是数据架构中的关键环节，主要负责数据的预处理和转换。合理的扫描逻辑划分可以显著提升整体系统的性能和可靠性。Flink适合处理实时数据流，而BigQuery适合处理大规模批处理任务。下一章将详细讨论ClickHouse层的职责和扫描逻辑。