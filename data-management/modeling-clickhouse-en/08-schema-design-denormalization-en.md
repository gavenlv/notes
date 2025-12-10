# 8. Schema Design and Denormalization Strategies

## 8.1 Schema Design Principles for Analytical Databases

### 8.1.1 Columnar Storage Optimization
ClickHouse's columnar storage architecture requires specific schema design considerations:

```sql
-- Optimized schema for analytical queries
CREATE TABLE optimized_schema (
    -- Primary key columns (used for sorting and indexing)
    event_date Date,
    user_id UInt64,
    event_timestamp DateTime64(3),
    
    -- Low-cardinality dimensions (use LowCardinality type)
    event_type LowCardinality(String),
    country LowCardinality(String),
    device_type LowCardinality(String),
    
    -- High-cardinality dimensions
    session_id String,
    ip_address String,
    
    -- Metrics (numerical values for aggregation)
    amount Decimal(10,2),
    quantity UInt32,
    duration Float64,
    
    -- Flags and status indicators
    is_premium Bool,
    status_code UInt8,
    
    -- Arrays for multi-valued attributes
    tags Array(String),
    categories Array(LowCardinality(String)),
    
    -- JSON for flexible schema
    metadata String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp)
SETTINGS index_granularity = 8192;
```

### 8.1.2 Data Type Selection Guidelines

#### Numeric Types
```sql
-- Choose appropriate numeric types based on value ranges
CREATE TABLE numeric_types_example (
    -- Small integers: use UInt8/UInt16 for small ranges
    age UInt8,                    -- 0-255
    status_code UInt16,           -- 0-65535
    
    -- Medium integers: UInt32 for most use cases
    user_id UInt32,               -- Up to 4 billion
    product_id UInt32,
    
    -- Large integers: UInt64 for very large values
    transaction_id UInt64,        -- For extremely large datasets
    
    -- Decimal types for financial data
    amount Decimal(15,2),         -- High precision financial data
    price Decimal(10,4),          -- Currency with 4 decimal places
    
    -- Floating point for scientific data
    temperature Float32,          -- Single precision
    latitude Float64,             -- Double precision for coordinates
    
    -- Fixed precision for performance
    ratio FixedString(8)          -- Fixed length ratios
);
```

#### String Types
```sql
-- String type optimization strategies
CREATE TABLE string_types_example (
    -- LowCardinality for enum-like strings
    event_type LowCardinality(String),    -- 'click', 'view', 'purchase'
    country_code LowCardinality(String),  -- 'US', 'CN', 'EU'
    
    -- Regular strings for high-cardinality data
    email String,                         -- High cardinality
    product_name String,                  -- Unique product names
    
    -- FixedString for known-length data
    user_hash FixedString(32),            -- MD5 hashes
    uuid FixedString(36),                 -- UUID strings
    
    -- Enum for truly fixed sets
    priority Enum8('low' = 1, 'medium' = 2, 'high' = 3)
);
```

## 8.2 Denormalization Strategies

### 8.2.1 When to Denormalize

#### ✅ Benefits of Denormalization
- **Improved query performance**: Fewer joins needed
- **Simplified query logic**: Direct access to related data
- **Better compression**: Related data stored together
- **Optimized for analytical workloads**: Columnar storage benefits

#### ❌ When to Avoid Denormalization
- **Frequent updates**: Denormalized data requires multiple updates
- **Large dimension tables**: Can significantly increase storage
- **Complex many-to-many relationships**: Difficult to maintain consistency

### 8.2.2 Denormalization Patterns

#### Pattern 1: Flattened Dimensions
```sql
-- Before normalization (requires joins)
CREATE TABLE events_normalized (
    event_id UInt64,
    user_id UInt64,
    product_id UInt64,
    event_type String,
    event_timestamp DateTime
);

CREATE TABLE users (
    user_id UInt64,
    user_name String,
    country String,
    registration_date Date
);

CREATE TABLE products (
    product_id UInt64,
    product_name String,
    category String,
    price Decimal(10,2)
);

-- After denormalization (no joins needed)
CREATE TABLE events_denormalized (
    event_id UInt64,
    
    -- User dimensions
    user_id UInt64,
    user_name String,
    user_country LowCardinality(String),
    user_registration_date Date,
    
    -- Product dimensions
    product_id UInt64,
    product_name String,
    product_category LowCardinality(String),
    product_price Decimal(10,2),
    
    -- Event data
    event_type LowCardinality(String),
    event_timestamp DateTime,
    amount Decimal(10,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_timestamp)
ORDER BY (event_timestamp, user_id, event_type);
```

#### Pattern 2: Nested Data Structures
```sql
-- Using nested data for hierarchical relationships
CREATE TABLE user_sessions_nested (
    session_id String,
    user_id UInt64,
    start_time DateTime,
    end_time DateTime,
    
    -- Nested structure for page views
    page_views Nested(
        page_url String,
        view_time DateTime,
        duration UInt32,
        referrer String
    ),
    
    -- Nested structure for products viewed
    products_viewed Nested(
        product_id UInt64,
        product_name String,
        view_count UInt32,
        last_viewed DateTime
    )
) ENGINE = MergeTree()
ORDER BY (user_id, start_time);

-- Querying nested data
SELECT
    session_id,
    user_id,
    arrayLength(page_views) as page_view_count,
    sum(arraySum(products_viewed.view_count)) as total_product_views
FROM user_sessions_nested
ARRAY JOIN page_views, products_viewed
WHERE start_time >= '2024-01-01'
GROUP BY session_id, user_id;
```

#### Pattern 3: Materialized Pre-aggregations
```sql
-- Pre-aggregated denormalized views
CREATE MATERIALIZED VIEW daily_user_metrics
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, country, device_type)
AS SELECT
    toDate(event_timestamp) as event_date,
    user_id,
    user_country,
    device_type,
    
    -- Count metrics
    count() as event_count,
    countIf(event_type = 'purchase') as purchase_count,
    
    -- Sum metrics
    sum(amount) as total_amount,
    sumIf(amount, event_type = 'purchase') as purchase_amount,
    
    -- Unique counts
    uniq(session_id) as unique_sessions,
    uniqIf(product_id, event_type = 'view') as unique_products_viewed
FROM events_denormalized
GROUP BY event_date, user_id, user_country, device_type;
```

## 8.3 Schema Evolution and Migration

### 8.3.1 Adding New Columns
```sql
-- Safe schema evolution by adding nullable columns
ALTER TABLE events_denormalized 
ADD COLUMN IF NOT EXISTS marketing_channel LowCardinality(String) DEFAULT '';

ALTER TABLE events_denormalized 
ADD COLUMN IF NOT EXISTS campaign_id UInt64 DEFAULT 0;

-- For more complex migrations, create new table and copy data
CREATE TABLE events_denormalized_v2 (
    -- Existing columns
    event_id UInt64,
    user_id UInt64,
    -- ... other existing columns
    
    -- New columns
    marketing_channel LowCardinality(String),
    campaign_id UInt64,
    utm_parameters String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_timestamp)
ORDER BY (event_timestamp, user_id, event_type);

-- Copy data with new columns populated
INSERT INTO events_denormalized_v2
SELECT
    event_id,
    user_id,
    -- ... existing columns
    
    -- New columns with default values
    '' as marketing_channel,
    0 as campaign_id,
    '' as utm_parameters
FROM events_denormalized;
```

### 8.3.2 Handling Schema Changes in ETL
```python
# Python example for schema evolution in ETL
class SchemaEvolutionManager:
    def __init__(self, target_table):
        self.target_table = target_table
        self.current_schema = self.get_current_schema()
    
    def adapt_data_for_schema(self, data_batch):
        """Adapt incoming data to match current table schema"""
        adapted_batch = []
        
        for record in data_batch:
            adapted_record = {}
            
            # Map existing fields
            for field in self.current_schema['fields']:
                field_name = field['name']
                
                if field_name in record:
                    # Field exists in incoming data
                    adapted_record[field_name] = record[field_name]
                else:
                    # Field doesn't exist, use default
                    adapted_record[field_name] = field.get('default', None)
            
            adapted_batch.append(adapted_record)
        
        return adapted_batch
    
    def get_current_schema(self):
        """Retrieve current table schema from metadata"""
        # Implementation to get schema from ClickHouse system tables
        # or from a schema registry
        pass

# Usage in ETL pipeline
schema_manager = SchemaEvolutionManager('events_denormalized')

# Process incoming data
raw_data = get_raw_events()
adapted_data = schema_manager.adapt_data_for_schema(raw_data)

# Insert adapted data
insert_into_clickhouse(adapted_data)
```

## 8.4 Partitioning and Sorting Strategies

### 8.4.1 Effective Partitioning
```sql
-- Date-based partitioning (most common)
PARTITION BY toYYYYMM(event_date)

-- Multi-level partitioning for large datasets
PARTITION BY (toYYYYMM(event_date), event_type)

-- Custom partitioning for business logic
PARTITION BY 
    CASE 
        WHEN user_id % 100 = 0 THEN 'shard_0'
        WHEN user_id % 100 = 1 THEN 'shard_1'
        -- ... up to shard_99
        ELSE 'other'
    END

-- Partition by predefined ranges
PARTITION BY 
    CASE 
        WHEN amount < 10 THEN 'small'
        WHEN amount < 100 THEN 'medium'
        WHEN amount < 1000 THEN 'large'
        ELSE 'xlarge'
    END
```

### 8.4.2 Optimal Sorting Keys
```sql
-- Good: Columns frequently used in WHERE clauses
ORDER BY (event_date, user_id, event_type)

-- Better: Consider data distribution and query patterns
ORDER BY (event_date, event_type, user_id)  -- If queries often filter by event_type

-- Advanced: Composite keys for specific use cases
ORDER BY ( 
    toStartOfHour(event_timestamp),  -- Hourly aggregations
    user_id,
    event_type
)

-- For time-series analysis
ORDER BY (device_id, event_timestamp)
```

## 8.5 Indexing and Compression

### 8.5.1 Primary Key Design
```sql
-- Primary key automatically creates sparse index
CREATE TABLE optimized_indexing (
    event_date Date,
    user_id UInt64,
    event_type LowCardinality(String),
    event_timestamp DateTime,
    -- ... other columns
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp)  -- Primary key
SETTINGS 
    index_granularity = 8192,          -- Adjust based on data size
    index_granularity_bytes = 10485760; -- 10MB per granule

-- The primary key enables efficient range queries
EXPLAIN SYNTAX
SELECT * FROM optimized_indexing
WHERE event_date = '2024-01-01'
  AND user_id = 12345
  AND event_type = 'purchase';
```

### 8.5.2 Compression Strategies
```sql
-- Column-level compression settings
CREATE TABLE compressed_table (
    -- High compression for repetitive data
    event_type LowCardinality(String) CODEC(ZSTD(1)),
    country LowCardinality(String) CODEC(ZSTD(3)),
    
    -- Delta encoding for sequential data
    user_id UInt64 CODEC(Delta, ZSTD),
    event_timestamp DateTime64 CODEC(DoubleDelta, ZSTD),
    
    -- Gorilla encoding for metrics
    temperature Float64 CODEC(Gorilla, ZSTD),
    pressure Float64 CODEC(Gorilla, ZSTD),
    
    -- Default compression for other columns
    metadata String CODEC(ZSTD(5))
) ENGINE = MergeTree()
ORDER BY (event_timestamp, user_id);

-- Table-level compression settings
ALTER TABLE compressed_table MODIFY SETTING
    min_compress_block_size = 65536,
    max_compress_block_size = 1048576,
    compress_block_size_delta = 16384;
```

## 8.6 Real-world Schema Design Examples

### 8.6.1 E-commerce Analytics Schema
```sql
-- Comprehensive e-commerce schema with denormalization
CREATE TABLE ecommerce_events (
    -- Event identification
    event_id UInt64,
    event_timestamp DateTime64(3),
    event_date Date,
    
    -- User information (denormalized)
    user_id UInt64,
    user_email String,
    user_country LowCardinality(String),
    user_age_group LowCardinality(String),
    user_segment LowCardinality(String),
    user_registration_date Date,
    
    -- Session context
    session_id String,
    device_type LowCardinality(String),
    browser LowCardinality(String),
    os LowCardinality(String),
    
    -- Product information (denormalized)
    product_id UInt64,
    product_name String,
    product_category LowCardinality(String),
    product_brand LowCardinality(String),
    product_price Decimal(10,2),
    
    -- Event details
    event_type LowCardinality(String),  -- 'view', 'add_to_cart', 'purchase'
    page_url String,
    referrer String,
    
    -- Transaction details
    quantity UInt32,
    amount Decimal(10,2),
    currency LowCardinality(String),
    
    -- Marketing context
    campaign_id UInt64,
    marketing_channel LowCardinality(String),
    utm_source LowCardinality(String),
    utm_medium LowCardinality(String),
    utm_campaign LowCardinality(String),
    
    -- Technical metadata
    ip_address String,
    user_agent String,
    
    -- Arrays for multi-value attributes
    product_tags Array(LowCardinality(String)),
    viewed_products Array(UInt64)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp)
SETTINGS index_granularity = 8192;
```

### 8.6.2 IoT Device Monitoring Schema
```sql
-- IoT schema optimized for time-series data
CREATE TABLE iot_device_metrics (
    -- Device identification
    device_id UInt64,
    device_type LowCardinality(String),
    device_location String,
    
    -- Time dimensions
    metric_timestamp DateTime64(3),
    metric_date Date,
    
    -- Metric values
    temperature Nullable(Float64),
    humidity Nullable(Float64),
    pressure Nullable(Float64),
    voltage Nullable(Float64),
    current Nullable(Float64),
    
    -- Status information
    device_status LowCardinality(String),
    battery_level UInt8,
    signal_strength UInt8,
    
    -- Environmental context
    weather_condition LowCardinality(String),
    ambient_temperature Nullable(Float64),
    
    -- Technical metadata
    firmware_version String,
    last_maintenance_date Date,
    
    -- Arrays for multiple sensor readings
    sensor_readings Array(Float64),
    alert_codes Array(UInt16)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(metric_date)
ORDER BY (device_id, metric_timestamp)
SETTINGS 
    index_granularity = 4096,  -- Smaller granules for time-series
    storage_policy = 'tsdb';   -- Custom storage policy for time-series
```

## 8.7 Performance Monitoring and Optimization

### 8.7.1 Schema Performance Metrics
```sql
-- Monitor table performance
SELECT
    database,
    table,
    formatReadableSize(total_bytes) as total_size,
    formatReadableSize(primary_key_bytes_in_memory) as index_size,
    rows,
    partitions,
    formatReadableSize(bytes_on_disk) as disk_size
FROM system.parts
WHERE active = 1
AND database = currentDatabase()
ORDER BY total_bytes DESC;

-- Analyze query performance
SELECT
    query,
    query_duration_ms,
    read_rows,
    read_bytes,
    result_rows,
    result_bytes
FROM system.query_log
WHERE event_date = today()
AND query LIKE '%SELECT%'
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### 8.7.2 Continuous Schema Optimization
```sql
-- Regular maintenance operations
-- Optimize table to merge parts
OPTIMIZE TABLE ecommerce_events FINAL;

-- Update table settings based on usage patterns
ALTER TABLE ecommerce_events MODIFY SETTING
    index_granularity = 16384,  -- Adjust based on query patterns
    min_compress_block_size = 131072;

-- Add projections for common query patterns
ALTER TABLE ecommerce_events ADD PROJECTION user_behavior_projection (
    SELECT
        user_id,
        event_date,
        event_type,
        count(),
        sum(amount)
    GROUP BY user_id, event_date, event_type
);
```

## 8.8 Summary

Effective schema design and denormalization are critical for achieving optimal performance in ClickHouse. Key principles include:

1. **Columnar optimization**: Choose appropriate data types and compression
2. **Strategic denormalization**: Balance query performance with update complexity
3. **Proper partitioning**: Align with query patterns and data distribution
4. **Optimal sorting**: Design primary keys based on common query filters
5. **Continuous evolution**: Plan for schema changes and migrations

By following these patterns, you can create schemas that leverage ClickHouse's strengths while providing excellent query performance for analytical workloads.