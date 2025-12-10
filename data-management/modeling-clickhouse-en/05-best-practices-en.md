# 5. Best Practices for ETL and ClickHouse Responsibility Division

## 5.1 Core Division Principles

Proper responsibility division is key to building an efficient data architecture. The following principles guide the allocation of scan logic between the ETL layer and the ClickHouse layer:

### 5.1.1 Data Preprocessing Priority Principle
- **ETL Layer**: Responsible for data cleaning, format conversion, basic validation
- **ClickHouse Layer**: Focuses on data analysis and query optimization

### 5.1.2 Computational Complexity Principle
- **Simple Calculations**: Completed in the ETL layer
- **Complex Calculations**: Leverage ClickHouse's computational capabilities

### 5.1.3 Real-time Requirements Principle
- **Real-time Processing**: Flink stream processing
- **Near Real-time**: ClickHouse materialized views
- **Batch Processing**: BigQuery batch ETL

## 5.2 Specific Responsibility Division Guidelines

### 5.2.1 Data Cleaning and Transformation

#### ETL Layer Responsibilities
```python
# Data processing that should be completed in the ETL layer
def etl_data_processing(raw_data):
    # 1. Data format validation
    if not validate_data_format(raw_data):
        return None
    
    # 2. Data type conversion
    converted_data = convert_data_types(raw_data)
    
    # 3. Data standardization
    standardized_data = standardize_data(converted_data)
    
    # 4. Basic data cleaning
    cleaned_data = basic_data_cleaning(standardized_data)
    
    return cleaned_data
```

#### ClickHouse Layer Responsibilities
```sql
-- Complex transformations to avoid in ClickHouse layer
-- Not recommended: Complex data transformations during queries
SELECT
    jsonExtractString(event_data, 'user.name') as user_name,  -- Complex JSON parsing
    parseDateTimeBestEffort(event_time_str) as event_time,    -- Time format parsing
    multiIf(amount > 100, 'high', amount > 50, 'medium', 'low') as amount_level  -- Complex conditional logic
FROM raw_events;
```

### 5.2.2 Data Aggregation Calculations

#### ETL Layer Pre-aggregation
```sql
-- Pre-aggregation in BigQuery
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

#### ClickHouse Layer Aggregation Optimization
```sql
-- Leveraging ClickHouse's aggregation capabilities
-- Create materialized views for real-time aggregation
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

-- Query materialized views
SELECT
    event_date,
    event_type,
    countMerge(count_state) as total_count,
    sumMerge(sum_state) as total_amount,
    uniqMerge(unique_users_state) as unique_users
FROM realtime_aggregates
WHERE event_date = '2024-01-15';
```

## 5.3 Performance Optimization Strategies

### 5.3.1 Data Loading Optimization

#### ETL Layer Data Partitioning
```python
# Flink data partitioning strategy
stream.keyBy(lambda event: event["user_id"] % 10)  # Hash partition by user ID
stream.window(TumblingProcessingTimeWindows.of(Time.minutes(5)))  # Time window
```

#### ClickHouse Data Partitioning
```sql
-- ClickHouse table partitioning design
CREATE TABLE events (
    event_date Date,
    event_timestamp DateTime64(3),
    user_id UInt64,
    event_type LowCardinality(String),
    amount Decimal(10,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)  -- Monthly partitioning
ORDER BY (event_date, user_id, event_type)  -- Sorting key
SETTINGS index_granularity = 8192;  -- Index granularity
```

### 5.3.2 Query Performance Optimization

#### Avoid Complex Calculations in ClickHouse
```sql
-- Not recommended: Complex data transformations in ClickHouse
SELECT
    arrayJoin(splitByChar(',', tags)) as tag,  -- Array expansion
    count() as count
FROM events
WHERE event_date >= '2024-01-01'
GROUP BY tag;

-- Recommended: Preprocess tag data in ETL layer
-- ETL layer expands tag arrays into multiple rows
-- ClickHouse performs simple counting queries
```

#### Leverage ClickHouse's Vectorized Execution
```sql
-- ClickHouse-optimized aggregation queries
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

## 5.4 Data Quality Assurance

### 5.4.1 ETL Layer Data Quality Checks
```python
# Data quality validation function
def validate_data_quality(data):
    checks = [
        # Completeness checks
        lambda d: all(key in d for key in required_fields),
        # Validity checks
        lambda d: is_valid_timestamp(d['event_timestamp']),
        lambda d: 0 <= d['amount'] <= 1000000,
        # Consistency checks
        lambda d: d['event_type'] in valid_event_types,
    ]
    
    return all(check(data) for check in checks)
```

### 5.4.2 ClickHouse Layer Data Monitoring
```sql
-- Data quality monitoring queries
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

## 5.5 Fault Tolerance and Recovery Strategies

### 5.5.1 ETL Layer Fault Tolerance
```java
// Flink checkpointing and state management
env.enableCheckpointing(60000);  // 60-second checkpoint interval
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
```

### 5.5.2 ClickHouse Data Backup
```sql
-- ClickHouse data backup strategies
-- Use ALTER TABLE FREEZE for snapshot backups
ALTER TABLE events FREEZE;

-- Use INSERT INTO for data migration
INSERT INTO backup_events
SELECT * FROM events
WHERE event_date >= '2024-01-01';
```

## 5.6 Monitoring and Alerting

### 5.6.1 Key Monitoring Metrics

#### ETL Layer Monitoring
- **Data Processing Latency**: End-to-end latency statistics
- **Data Throughput**: Records/second processing capacity
- **Error Rate**: Data processing failure ratio
- **Resource Usage**: CPU, memory, network utilization

#### ClickHouse Layer Monitoring
- **Query Response Time**: P50/P95/P99 latency
- **Query Throughput**: QPS (Queries Per Second)
- **Data Compression Rate**: Storage efficiency metrics
- **System Resources**: Disk I/O, memory usage

### 5.6.2 Alerting Strategies
```yaml
# Monitoring alert configuration example
alerts:
  - name: "etl_processing_delay"
    condition: "processing_delay > 300"  # Delay exceeds 5 minutes
    severity: "warning"
    
  - name: "clickhouse_query_timeout"
    condition: "query_timeout_rate > 0.05"  # Query timeout rate exceeds 5%
    severity: "critical"
    
  - name: "data_quality_anomaly"
    condition: "data_completeness_rate < 0.95"  # Data completeness below 95%
    severity: "warning"
```

## 5.7 Summary

Proper division of responsibilities between ETL and ClickHouse is crucial for building an efficient data architecture. By following principles such as data preprocessing priority, computational complexity grading, and real-time requirements, the advantages of each technical component can be fully utilized to improve overall system performance. The next chapter will demonstrate the practical application of these principles through real-world case studies.