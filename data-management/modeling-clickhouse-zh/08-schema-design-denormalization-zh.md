# 8. 模式设计与反规范化策略

## 8.1 分析型数据库的模式设计原则

### 8.1.1 列式存储优化
ClickHouse的列式存储架构需要特定的模式设计考虑：

```sql
-- 为分析查询优化的模式设计
CREATE TABLE optimized_schema (
    -- 主键列（用于排序和索引）
    event_date Date,
    user_id UInt64,
    event_timestamp DateTime64(3),
    
    -- 低基数维度（使用LowCardinality类型）
    event_type LowCardinality(String),
    country LowCardinality(String),
    device_type LowCardinality(String),
    
    -- 高基数维度
    session_id String,
    ip_address String,
    
    -- 指标（用于聚合的数值）
    amount Decimal(10,2),
    quantity UInt32,
    duration Float64,
    
    -- 标志和状态指示器
    is_premium Bool,
    status_code UInt8,
    
    -- 多值属性的数组
    tags Array(String),
    categories Array(LowCardinality(String)),
    
    -- 灵活模式的JSON
    metadata String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp)
SETTINGS index_granularity = 8192;
```

### 8.1.2 数据类型选择指南

#### 数值类型
```sql
-- 根据值范围选择合适的数值类型
CREATE TABLE numeric_types_example (
    -- 小整数：对小范围使用UInt8/UInt16
    age UInt8,                    -- 0-255
    status_code UInt16,           -- 0-65535
    
    -- 中等整数：大多数用例使用UInt32
    user_id UInt32,               -- 最多40亿
    product_id UInt32,
    
    -- 大整数：非常大的值使用UInt64
    transaction_id UInt64,        -- 用于极大数据集
    
    -- 金融数据的Decimal类型
    amount Decimal(15,2),         -- 高精度金融数据
    price Decimal(10,4),          -- 4位小数的货币
    
    -- 科学数据的浮点数
    temperature Float32,          -- 单精度
    latitude Float64,             -- 坐标的双精度
    
    -- 性能优化的固定精度
    ratio FixedString(8)          -- 固定长度比率
);
```

#### 字符串类型
```sql
-- 字符串类型优化策略
CREATE TABLE string_types_example (
    -- 枚举类字符串使用LowCardinality
    event_type LowCardinality(String),    -- 'click', 'view', 'purchase'
    country_code LowCardinality(String),  -- 'US', 'CN', 'EU'
    
    -- 高基数数据使用常规字符串
    email String,                         -- 高基数
    product_name String,                  -- 唯一产品名称
    
    -- 已知长度数据使用FixedString
    user_hash FixedString(32),            -- MD5哈希
    uuid FixedString(36),                 -- UUID字符串
    
    -- 真正固定集合使用Enum
    priority Enum8('low' = 1, 'medium' = 2, 'high' = 3)
);
```

## 8.2 反规范化策略

### 8.2.1 何时进行反规范化

#### ✅ 反规范化的好处
- **改进查询性能**：减少连接需求
- **简化查询逻辑**：直接访问相关数据
- **更好的压缩**：相关数据存储在一起
- **分析工作负载优化**：列式存储优势

#### ❌ 何时避免反规范化
- **频繁更新**：反规范化数据需要多次更新
- **大维度表**：可能显著增加存储
- **复杂多对多关系**：难以维护一致性

### 8.2.2 反规范化模式

#### 模式1：扁平化维度
```sql
-- 规范化前（需要连接）
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

-- 反规范化后（无需连接）
CREATE TABLE events_denormalized (
    event_id UInt64,
    
    -- 用户维度
    user_id UInt64,
    user_name String,
    user_country LowCardinality(String),
    user_registration_date Date,
    
    -- 产品维度
    product_id UInt64,
    product_name String,
    product_category LowCardinality(String),
    product_price Decimal(10,2),
    
    -- 事件数据
    event_type LowCardinality(String),
    event_timestamp DateTime,
    amount Decimal(10,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_timestamp)
ORDER BY (event_timestamp, user_id, event_type);
```

#### 模式2：嵌套数据结构
```sql
-- 使用嵌套数据进行层次关系
CREATE TABLE user_sessions_nested (
    session_id String,
    user_id UInt64,
    start_time DateTime,
    end_time DateTime,
    
    -- 页面浏览的嵌套结构
    page_views Nested(
        page_url String,
        view_time DateTime,
        duration UInt32,
        referrer String
    ),
    
    -- 查看产品的嵌套结构
    products_viewed Nested(
        product_id UInt64,
        product_name String,
        view_count UInt32,
        last_viewed DateTime
    )
) ENGINE = MergeTree()
ORDER BY (user_id, start_time);

-- 查询嵌套数据
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

#### 模式3：物化预聚合
```sql
-- 预聚合的反规范化视图
CREATE MATERIALIZED VIEW daily_user_metrics
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, country, device_type)
AS SELECT
    toDate(event_timestamp) as event_date,
    user_id,
    user_country,
    device_type,
    
    -- 计数指标
    count() as event_count,
    countIf(event_type = 'purchase') as purchase_count,
    
    -- 求和指标
    sum(amount) as total_amount,
    sumIf(amount, event_type = 'purchase') as purchase_amount,
    
    -- 唯一计数
    uniq(session_id) as unique_sessions,
    uniqIf(product_id, event_type = 'view') as unique_products_viewed
FROM events_denormalized
GROUP BY event_date, user_id, user_country, device_type;
```

## 8.3 模式演进和迁移

### 8.3.1 添加新列
```sql
-- 通过添加可空列进行安全模式演进
ALTER TABLE events_denormalized 
ADD COLUMN IF NOT EXISTS marketing_channel LowCardinality(String) DEFAULT '';

ALTER TABLE events_denormalized 
ADD COLUMN IF NOT EXISTS campaign_id UInt64 DEFAULT 0;

-- 对于更复杂的迁移，创建新表并复制数据
CREATE TABLE events_denormalized_v2 (
    -- 现有列
    event_id UInt64,
    user_id UInt64,
    -- ... 其他现有列
    
    -- 新列
    marketing_channel LowCardinality(String),
    campaign_id UInt64,
    utm_parameters String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_timestamp)
ORDER BY (event_timestamp, user_id, event_type);

-- 复制数据并填充新列
INSERT INTO events_denormalized_v2
SELECT
    event_id,
    user_id,
    -- ... 现有列
    
    -- 带默认值的新列
    '' as marketing_channel,
    0 as campaign_id,
    '' as utm_parameters
FROM events_denormalized;
```

### 8.3.2 ETL中的模式变更处理
```python
# ETL中模式演进的Python示例
class SchemaEvolutionManager:
    def __init__(self, target_table):
        self.target_table = target_table
        self.current_schema = self.get_current_schema()
    
    def adapt_data_for_schema(self, data_batch):
        """使传入数据适应当前表模式"""
        adapted_batch = []
        
        for record in data_batch:
            adapted_record = {}
            
            # 映射现有字段
            for field in self.current_schema['fields']:
                field_name = field['name']
                
                if field_name in record:
                    # 传入数据中存在字段
                    adapted_record[field_name] = record[field_name]
                else:
                    # 字段不存在，使用默认值
                    adapted_record[field_name] = field.get('default', None)
            
            adapted_batch.append(adapted_record)
        
        return adapted_batch
    
    def get_current_schema(self):
        """从元数据检索当前表模式"""
        # 从ClickHouse系统表或模式注册表获取模式的实现
        pass

# ETL管道中的使用
schema_manager = SchemaEvolutionManager('events_denormalized')

# 处理传入数据
raw_data = get_raw_events()
adapted_data = schema_manager.adapt_data_for_schema(raw_data)

# 插入适配的数据
insert_into_clickhouse(adapted_data)
```

## 8.4 分区和排序策略

### 8.4.1 有效的分区
```sql
-- 基于日期的分区（最常见）
PARTITION BY toYYYYMM(event_date)

-- 大数据集的多级分区
PARTITION BY (toYYYYMM(event_date), event_type)

-- 业务逻辑的自定义分区
PARTITION BY 
    CASE 
        WHEN user_id % 100 = 0 THEN 'shard_0'
        WHEN user_id % 100 = 1 THEN 'shard_1'
        -- ... 最多到shard_99
        ELSE 'other'
    END

-- 预定义范围的分区
PARTITION BY 
    CASE 
        WHEN amount < 10 THEN 'small'
        WHEN amount < 100 THEN 'medium'
        WHEN amount < 1000 THEN 'large'
        ELSE 'xlarge'
    END
```

### 8.4.2 最优排序键
```sql
-- 良好：WHERE子句中频繁使用的列
ORDER BY (event_date, user_id, event_type)

-- 更好：考虑数据分布和查询模式
ORDER BY (event_date, event_type, user_id)  -- 如果查询经常按event_type过滤

-- 高级：特定用例的复合键
ORDER BY ( 
    toStartOfHour(event_timestamp),  -- 小时聚合
    user_id,
    event_type
)

-- 时间序列分析
ORDER BY (device_id, event_timestamp)
```

## 8.5 索引和压缩

### 8.5.1 主键设计
```sql
-- 主键自动创建稀疏索引
CREATE TABLE optimized_indexing (
    event_date Date,
    user_id UInt64,
    event_type LowCardinality(String),
    event_timestamp DateTime,
    -- ... 其他列
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp)  -- 主键
SETTINGS 
    index_granularity = 8192,          -- 根据数据大小调整
    index_granularity_bytes = 10485760; -- 每个颗粒10MB

-- 主键支持高效的范围查询
EXPLAIN SYNTAX
SELECT * FROM optimized_indexing
WHERE event_date = '2024-01-01'
  AND user_id = 12345
  AND event_type = 'purchase';
```

### 8.5.2 压缩策略
```sql
-- 列级压缩设置
CREATE TABLE compressed_table (
    -- 重复数据的高压缩
    event_type LowCardinality(String) CODEC(ZSTD(1)),
    country LowCardinality(String) CODEC(ZSTD(3)),
    
    -- 顺序数据的Delta编码
    user_id UInt64 CODEC(Delta, ZSTD),
    event_timestamp DateTime64 CODEC(DoubleDelta, ZSTD),
    
    -- 指标的Gorilla编码
    temperature Float64 CODEC(Gorilla, ZSTD),
    pressure Float64 CODEC(Gorilla, ZSTD),
    
    -- 其他列的默认压缩
    metadata String CODEC(ZSTD(5))
) ENGINE = MergeTree()
ORDER BY (event_timestamp, user_id);

-- 表级压缩设置
ALTER TABLE compressed_table MODIFY SETTING
    min_compress_block_size = 65536,
    max_compress_block_size = 1048576,
    compress_block_size_delta = 16384;
```

## 8.6 实际模式设计示例

### 8.6.1 电商分析模式
```sql
-- 具有反规范化的全面电商模式
CREATE TABLE ecommerce_events (
    -- 事件标识
    event_id UInt64,
    event_timestamp DateTime64(3),
    event_date Date,
    
    -- 用户信息（反规范化）
    user_id UInt64,
    user_email String,
    user_country LowCardinality(String),
    user_age_group LowCardinality(String),
    user_segment LowCardinality(String),
    user_registration_date Date,
    
    -- 会话上下文
    session_id String,
    device_type LowCardinality(String),
    browser LowCardinality(String),
    os LowCardinality(String),
    
    -- 产品信息（反规范化）
    product_id UInt64,
    product_name String,
    product_category LowCardinality(String),
    product_brand LowCardinality(String),
    product_price Decimal(10,2),
    
    -- 事件详情
    event_type LowCardinality(String),  -- 'view', 'add_to_cart', 'purchase'
    page_url String,
    referrer String,
    
    -- 交易详情
    quantity UInt32,
    amount Decimal(10,2),
    currency LowCardinality(String),
    
    -- 营销上下文
    campaign_id UInt64,
    marketing_channel LowCardinality(String),
    utm_source LowCardinality(String),
    utm_medium LowCardinality(String),
    utm_campaign LowCardinality(String),
    
    -- 技术元数据
    ip_address String,
    user_agent String,
    
    -- 多值属性的数组
    product_tags Array(LowCardinality(String)),
    viewed_products Array(UInt64)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp)
SETTINGS index_granularity = 8192;
```

### 8.6.2 IoT设备监控模式
```sql
-- 为时间序列数据优化的IoT模式
CREATE TABLE iot_device_metrics (
    -- 设备标识
    device_id UInt64,
    device_type LowCardinality(String),
    device_location String,
    
    -- 时间维度
    metric_timestamp DateTime64(3),
    metric_date Date,
    
    -- 指标值
    temperature Nullable(Float64),
    humidity Nullable(Float64),
    pressure Nullable(Float64),
    voltage Nullable(Float64),
    current Nullable(Float64),
    
    -- 状态信息
    device_status LowCardinality(String),
    battery_level UInt8,
    signal_strength UInt8,
    
    -- 环境上下文
    weather_condition LowCardinality(String),
    ambient_temperature Nullable(Float64),
    
    -- 技术元数据
    firmware_version String,
    last_maintenance_date Date,
    
    -- 多个传感器读数的数组
    sensor_readings Array(Float64),
    alert_codes Array(UInt16)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(metric_date)
ORDER BY (device_id, metric_timestamp)
SETTINGS 
    index_granularity = 4096,  -- 时间序列的较小颗粒
    storage_policy = 'tsdb';   -- 时间序列的自定义存储策略
```

## 8.7 性能监控和优化

### 8.7.1 模式性能指标
```sql
-- 监控表性能
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

-- 分析查询性能
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

### 8.7.2 持续模式优化
```sql
-- 定期维护操作
-- 优化表以合并部分
OPTIMIZE TABLE ecommerce_events FINAL;

-- 根据使用模式更新表设置
ALTER TABLE ecommerce_events MODIFY SETTING
    index_granularity = 16384,  -- 根据查询模式调整
    min_compress_block_size = 131072;

-- 为常见查询模式添加投影
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

## 8.8 总结

有效的模式设计和反规范化对于在ClickHouse中实现最佳性能至关重要。关键原则包括：

1. **列式优化**：选择适当的数据类型和压缩
2. **战略性反规范化**：平衡查询性能和更新复杂性
3. **适当分区**：与查询模式和数据分布对齐
4. **最优排序**：基于常见查询过滤器设计主键
5. **持续演进**：规划模式变更和迁移

通过遵循这些模式，您可以创建利用ClickHouse优势的模式，同时为分析工作负载提供出色的查询性能。