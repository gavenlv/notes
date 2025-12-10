# 4. ClickHouse层职责与扫描逻辑

## 4.1 ClickHouse层核心职责

ClickHouse作为分析型数据库，主要负责高效的数据存储、快速查询和复杂分析计算。合理的扫描逻辑设计对查询性能至关重要。

### 4.1.1 主要职责
- **数据存储**: 高效的列式存储和数据压缩
- **快速查询**: 支持复杂的分析查询
- **数据聚合**: 实时和批量的数据聚合计算
- **查询优化**: 自动的查询优化和执行计划

## 4.2 ClickHouse扫描逻辑设计

### 4.2.1 数据存储策略

#### 表引擎选择
```sql
-- 示例：MergeTree系列表引擎
CREATE TABLE user_events (
    event_date Date,
    event_timestamp DateTime,
    user_id UInt64,
    event_type String,
    event_data String,
    amount Decimal(10,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type)
SETTINGS index_granularity = 8192;
```

#### 数据分区设计
```sql
-- 按时间分区
PARTITION BY toYYYYMM(event_date)

-- 按业务维度分区
PARTITION BY user_id % 10

-- 组合分区策略
PARTITION BY (toYYYYMM(event_date), event_type)
```

### 4.2.2 查询优化策略

#### 索引设计
```sql
-- 主键索引
ORDER BY (event_date, user_id, event_type)

-- 跳数索引
ALTER TABLE user_events ADD INDEX event_type_index event_type TYPE bloom_filter GRANULARITY 1;

-- 投影（Projection）
ALTER TABLE user_events ADD PROJECTION daily_stats (
    SELECT 
        event_date,
        event_type,
        count(),
        sum(amount)
    GROUP BY event_date, event_type
);
```

## 4.3 扫描逻辑划分原则

### 4.3.1 应在ClickHouse中处理的扫描逻辑

#### 复杂聚合查询
```sql
-- 多维度聚合
SELECT
    event_date,
    event_type,
    user_id,
    count() as event_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount,
    quantile(0.5)(amount) as median_amount
FROM user_events
WHERE event_date >= '2024-01-01'
GROUP BY event_date, event_type, user_id
HAVING event_count > 10
ORDER BY total_amount DESC
LIMIT 100;
```

#### 窗口函数分析
```sql
-- 用户行为序列分析
SELECT
    user_id,
    event_timestamp,
    event_type,
    LAG(event_timestamp) OVER (PARTITION BY user_id ORDER BY event_timestamp) as prev_timestamp,
    LEAD(event_timestamp) OVER (PARTITION BY user_id ORDER BY event_timestamp) as next_timestamp,
    runningAccumulate(sum(amount)) OVER (PARTITION BY user_id ORDER BY event_timestamp) as running_total
FROM user_events
WHERE event_date = '2024-01-15';
```

#### 关联查询优化
```sql
-- 使用JOIN进行数据关联
SELECT
    u.user_id,
    u.event_type,
    u.amount,
    p.product_name,
    c.category_name
FROM user_events u
JOIN products p ON u.product_id = p.id
JOIN categories c ON p.category_id = c.id
WHERE u.event_date = '2024-01-15'
  AND u.amount > 100;
```

### 4.3.2 不应在ClickHouse中处理的扫描逻辑

#### 复杂的数据转换
- 应在ETL层完成的数据格式转换
- 复杂的数据清洗和修复逻辑
- 需要多步处理的数据标准化

#### 实时数据流处理
- 高频率的实时数据更新
- 需要严格事务保证的数据操作
- 实时数据去重和排序

## 4.4 ClickHouse与ETL层的协同

### 4.4.1 数据加载策略

#### 批量插入优化
```sql
-- 使用批量插入提高性能
INSERT INTO user_events VALUES
('2024-01-15', '2024-01-15 10:00:00', 12345, 'purchase', '{}', 99.99),
('2024-01-15', '2024-01-15 10:01:00', 12345, 'view', '{}', 0.00),
('2024-01-15', '2024-01-15 10:02:00', 67890, 'purchase', '{}', 149.99);

-- 使用INSERT SELECT进行数据迁移
INSERT INTO user_events
SELECT
    event_date,
    event_timestamp,
    user_id,
    event_type,
    event_data,
    amount
FROM external_table;
```

#### 数据更新策略
```sql
-- 使用ReplacingMergeTree处理数据更新
CREATE TABLE user_events_replacing (
    event_date Date,
    event_timestamp DateTime,
    user_id UInt64,
    event_type String,
    event_data String,
    amount Decimal(10,2),
    version UInt32
) ENGINE = ReplacingMergeTree(version)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp);
```

### 4.4.2 查询性能优化

#### 物化视图
```sql
-- 创建物化视图预聚合数据
CREATE MATERIALIZED VIEW user_daily_stats
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type)
AS SELECT
    event_date,
    user_id,
    event_type,
    count() as event_count,
    sum(amount) as total_amount
FROM user_events
GROUP BY event_date, user_id, event_type;
```

#### 查询缓存
```sql
-- 启用查询结果缓存
SET use_uncompressed_cache = 1;
SET max_threads = 16;
SET max_memory_usage = 10000000000;
```

## 4.5 实际应用案例

### 4.5.1 用户行为分析

```sql
-- 用户漏斗分析
WITH funnel_steps AS (
    SELECT
        user_id,
        minIf(event_timestamp, event_type = 'view') as view_time,
        minIf(event_timestamp, event_type = 'add_to_cart') as cart_time,
        minIf(event_timestamp, event_type = 'purchase') as purchase_time
    FROM user_events
    WHERE event_date >= '2024-01-01'
    GROUP BY user_id
)
SELECT
    countIf(view_time IS NOT NULL) as viewed,
    countIf(cart_time IS NOT NULL AND cart_time > view_time) as added_to_cart,
    countIf(purchase_time IS NOT NULL AND purchase_time > cart_time) as purchased,
    round(added_to_cart * 100.0 / viewed, 2) as cart_conversion_rate,
    round(purchased * 100.0 / added_to_cart, 2) as purchase_conversion_rate
FROM funnel_steps;
```

### 4.5.2 实时监控仪表板

```sql
-- 实时业务指标
SELECT
    event_type,
    count() as event_count,
    sum(amount) as total_revenue,
    avg(amount) as avg_order_value,
    countDistinct(user_id) as unique_users
FROM user_events
WHERE event_timestamp >= now() - INTERVAL 1 HOUR
GROUP BY event_type
ORDER BY total_revenue DESC;
```

## 4.6 性能监控和优化

### 4.6.1 关键性能指标
- **查询响应时间**: P50, P95, P99延迟
- **查询吞吐量**: QPS（每秒查询数）
- **数据压缩率**: 原始数据与存储数据的比例
- **资源使用率**: CPU、内存、磁盘IO

### 4.6.2 优化建议
- 合理设计数据分区策略
- 使用合适的索引类型
- 避免全表扫描的查询模式
- 定期进行表维护和优化

## 4.7 总结

ClickHouse层主要负责高效的数据存储和快速的分析查询。合理的扫描逻辑划分应该将复杂的聚合计算、窗口函数分析和多维度查询放在ClickHouse层处理，而将数据预处理和实时流处理放在ETL层。下一章将讨论ETL层与ClickHouse层之间的职责划分最佳实践。