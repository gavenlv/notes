# 3. ETL Layer Responsibilities & Scan Logic

## 3.1 Core Responsibilities of ETL Layer

The ETL (Extract, Transform, Load) layer plays a critical role in modern data architecture, handling key data preprocessing and transformation tasks. Proper division of scan logic is crucial for overall system performance.

### 3.1.1 Main Responsibilities
- **Data Extraction**: Retrieve data from various data sources
- **Data Transformation**: Clean, format, and standardize data
- **Data Loading**: Load processed data into target systems
- **Data Quality**: Ensure data accuracy and consistency

## 3.2 Flink Scan Logic in ETL

### 3.2.1 Stream Data Processing

Flink, as a stream processing engine, is suitable for handling real-time data streams. Its scan logic design is as follows:

```java
// Example: Flink streaming ETL job
DataStream<RawData> rawStream = env
    .addSource(new KafkaSource<>("topic"))
    .map(new DataParser())           // Data parsing
    .filter(new DataValidator())     // Data validation
    .keyBy(RawData::getUserId)       // Group by user
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
    .aggregate(new UserBehaviorAggregator())  // User behavior aggregation
    .map(new DataEnricher())         // Data enrichment
    .addSink(new ClickHouseSink());  // Write to ClickHouse
```

### 3.2.2 Scan Logic Division

**Scan logic that should be handled in Flink**:
- Real-time data stream processing
- Window aggregation calculations
- Data format conversion
- Basic data cleaning
- Real-time data deduplication

**Scan logic that should NOT be handled in Flink**:
- Complex historical data analysis
- Large-scale data join queries
- Multi-dimensional data aggregation

## 3.3 BigQuery Scan Logic in ETL

### 3.3.1 Batch Processing ETL

BigQuery is suitable for handling large-scale batch processing tasks. Its scan logic design is as follows:

```sql
-- Example: BigQuery batch ETL job
CREATE OR REPLACE TABLE `project.dataset.cleaned_data` AS
SELECT 
    user_id,
    event_type,
    event_timestamp,
    -- Data cleaning and transformation
    TRIM(event_data) as cleaned_data,
    CAST(amount AS NUMERIC) as numeric_amount,
    -- Basic aggregation
    COUNT(*) OVER (PARTITION BY user_id) as user_event_count,
    -- Time window calculation
    TIMESTAMP_DIFF(event_timestamp, LAG(event_timestamp) 
        OVER (PARTITION BY user_id ORDER BY event_timestamp), SECOND) as time_diff
FROM `project.dataset.raw_data`
WHERE event_timestamp >= TIMESTAMP('2024-01-01')
  AND event_type IN ('click', 'view', 'purchase')
  AND amount IS NOT NULL;
```

### 3.3.2 Scan Logic Division

**Scan logic that should be handled in BigQuery**:
- Large-scale data batch processing
- Complex data transformation logic
- Historical data retrospective analysis
- Data quality checking and repair
- Pre-aggregation and summary calculations

**Scan logic that should NOT be handled in BigQuery**:
- Real-time data stream processing
- High-frequency interactive queries
- Real-time analysis requiring low latency

## 3.4 Best Practices for ETL Layer Scan Logic

### 3.4.1 Data Preprocessing Strategies

#### Data Cleaning Rules
```python
# Example: Data cleaning function
def clean_and_transform_data(raw_data):
    # 1. Remove invalid data
    if not is_valid_data(raw_data):
        return None
    
    # 2. Format standardization
    standardized_data = standardize_format(raw_data)
    
    # 3. Data type conversion
    converted_data = convert_data_types(standardized_data)
    
    # 4. Data enrichment
    enriched_data = enrich_with_reference_data(converted_data)
    
    return enriched_data
```

#### Data Quality Checks
```sql
-- Example: SQL data quality checks
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
    -- Calculate data quality metrics
    ROUND((total_records - null_amounts) * 100.0 / total_records, 2) as data_completeness_rate,
    ROUND((total_records - future_timestamps) * 100.0 / total_records, 2) as data_validity_rate
FROM data_quality_checks;
```

### 3.4.2 Performance Optimization Strategies

#### Flink Optimization
```java
// Flink performance optimization configuration
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// Set parallelism
env.setParallelism(4);

// Enable checkpointing
env.enableCheckpointing(60000);

// State backend configuration
env.setStateBackend(new FsStateBackend("hdfs://checkpoints"));

// Memory configuration
env.getConfig().setTaskManagerMemory(2048);
```

#### BigQuery Optimization
```sql
-- BigQuery query optimization
-- Use partitioned tables
CREATE TABLE partitioned_data
PARTITION BY DATE(event_timestamp)
AS SELECT * FROM raw_data;

-- Use clustering fields
CREATE TABLE clustered_data
CLUSTER BY user_id, event_type
AS SELECT * FROM raw_data;

-- Avoid full table scans
SELECT * FROM partitioned_data
WHERE event_timestamp >= '2024-01-01'
  AND event_timestamp < '2024-02-01';
```

## 3.5 Collaboration with ClickHouse

### 3.5.1 Data Flow Design

```
Data Sources → Flink(Real-time ETL) → ClickHouse(Real-time Analysis)
Data Sources → BigQuery(Batch ETL) → ClickHouse(Historical Analysis)
```

### 3.5.2 Data Format Conventions

The ETL layer should output ClickHouse-friendly data formats:
- Use appropriate numeric types
- Avoid complex nested structures
- Provide clear timestamp fields
- Include necessary data partitioning fields

## 3.6 Monitoring and Operations

### 3.6.1 Key Monitoring Metrics
- **Data processing throughput**: Records/second
- **Data processing latency**: End-to-end latency
- **Data quality metrics**: Completeness, accuracy
- **System resource usage**: CPU, memory, network

### 3.6.2 Alerting Strategies
- Data flow interruption alerts
- Data processing latency alerts
- Data quality anomaly alerts
- System resource alerts

## 3.7 Summary

The ETL layer is a critical component in data architecture, primarily responsible for data preprocessing and transformation. Proper division of scan logic can significantly improve the performance and reliability of the overall system. Flink is suitable for real-time data stream processing, while BigQuery is suitable for large-scale batch processing tasks. The next chapter will discuss the responsibilities and scan logic of the ClickHouse layer in detail.