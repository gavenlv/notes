-- ClickHouse Day 13: 生产环境最佳实践示例
-- 演示性能优化、表设计、查询调优等最佳实践

-- =====================================
-- 1. 表设计最佳实践
-- =====================================

-- 创建演示数据库
CREATE DATABASE IF NOT EXISTS best_practices_demo;
USE best_practices_demo;

-- 好的表设计示例：电商订单表
CREATE TABLE orders_optimized (
    -- 主键设计：高基数列在前
    user_id UInt64,           -- 高基数，查询频繁
    order_date Date,          -- 时间列，用于分区
    order_id UInt64,          -- 订单ID
    
    -- 业务字段
    product_id UInt32,        -- 商品ID
    category_id UInt16,       -- 分类ID (使用较小的数据类型)
    quantity UInt16,          -- 数量
    price Decimal64(2),       -- 价格 (固定精度)
    discount_rate Float32,    -- 折扣率
    
    -- 状态字段使用枚举
    status Enum8('pending' = 1, 'paid' = 2, 'shipped' = 3, 'delivered' = 4, 'cancelled' = 5),
    
    -- 时间戳
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
    
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)  -- 按月分区
ORDER BY (user_id, order_date, order_id)  -- 排序键优化
SETTINGS index_granularity = 8192;

-- 添加跳数索引
ALTER TABLE orders_optimized ADD INDEX idx_category category_id TYPE set(100) GRANULARITY 4;
ALTER TABLE orders_optimized ADD INDEX idx_price price TYPE minmax GRANULARITY 4;
ALTER TABLE orders_optimized ADD INDEX idx_status status TYPE set(10) GRANULARITY 4;

-- 对比：不好的表设计
CREATE TABLE orders_bad_design (
    order_id String,          -- 应该用数字类型
    order_time DateTime,      -- 时间列在前不利于索引
    status String,            -- 应该用枚举
    user_name String,         -- 应该用ID关联
    product_name String,      -- 应该用ID关联
    price String,             -- 应该用数值类型
    metadata String           -- 非结构化数据
) ENGINE = MergeTree()
ORDER BY order_time;  -- 排序键不优化

-- =====================================
-- 2. 分区策略最佳实践
-- =====================================

-- 按时间分区（推荐）
CREATE TABLE events_time_partitioned (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)  -- 按月分区
ORDER BY (user_id, event_time);

-- 多级分区（适用于大数据量）
CREATE TABLE sales_multi_partitioned (
    sale_date Date,
    region String,
    store_id UInt32,
    product_id UInt64,
    amount Decimal64(2)
) ENGINE = MergeTree()
PARTITION BY (toYear(sale_date), region)  -- 按年份和地区分区
ORDER BY (store_id, sale_date);

-- 自定义分区函数
CREATE TABLE logs_custom_partitioned (
    log_time DateTime,
    level String,
    message String,
    source String
) ENGINE = MergeTree()
PARTITION BY toStartOfWeek(log_time)  -- 按周分区
ORDER BY (source, log_time);

-- =====================================
-- 3. 索引优化最佳实践
-- =====================================

-- 创建测试表用于索引演示
CREATE TABLE products_with_indexes (
    product_id UInt64,
    category_id UInt32,
    brand_id UInt32,
    name String,
    description String,
    price Decimal64(2),
    rating Float32,
    tags Array(String),
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY (category_id, brand_id, product_id);

-- 添加不同类型的跳数索引
-- 1. 集合索引 - 适用于低基数列
ALTER TABLE products_with_indexes ADD INDEX idx_category category_id TYPE set(1000) GRANULARITY 4;

-- 2. 最小最大索引 - 适用于数值范围查询
ALTER TABLE products_with_indexes ADD INDEX idx_price price TYPE minmax GRANULARITY 4;

-- 3. 布隆过滤器索引 - 适用于字符串等值查询
ALTER TABLE products_with_indexes ADD INDEX idx_name_bloom name TYPE bloom_filter() GRANULARITY 4;

-- 4. N-gram布隆过滤器 - 适用于模糊搜索
ALTER TABLE products_with_indexes ADD INDEX idx_description_ngram description TYPE ngrambf_v1(3, 256, 2, 0) GRANULARITY 4;

-- 5. 令牌布隆过滤器 - 适用于分词搜索
ALTER TABLE products_with_indexes ADD INDEX idx_tags_token tags TYPE tokenbf_v1(256, 2, 0) GRANULARITY 4;

-- =====================================
-- 4. 查询优化最佳实践
-- =====================================

-- 插入测试数据
INSERT INTO orders_optimized
SELECT 
    number % 100000 + 1 as user_id,
    today() - INTERVAL (number % 365) DAY as order_date,
    number as order_id,
    number % 10000 + 1 as product_id,
    number % 100 + 1 as category_id,
    (number % 10) + 1 as quantity,
    round((number % 1000) + 10.99, 2) as price,
    (number % 100) / 100.0 as discount_rate,
    (['pending', 'paid', 'shipped', 'delivered', 'cancelled'])[number % 5 + 1] as status,
    now() - INTERVAL (number % 86400) SECOND as created_at,
    now() - INTERVAL (number % 43200) SECOND as updated_at
FROM numbers(1000000);

-- 优化前的查询（低效）
-- 避免在WHERE子句中使用函数
-- 错误示例：
-- SELECT count() FROM orders_optimized WHERE toYYYYMM(order_date) = 202401;

-- 优化后的查询（高效）
-- 使用范围查询替代函数
SELECT count() 
FROM orders_optimized 
WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';

-- 利用主键索引的查询优化
-- 好的查询：按排序键顺序查询
SELECT user_id, sum(price * quantity) as total_amount
FROM orders_optimized 
WHERE user_id BETWEEN 1000 AND 2000
    AND order_date >= '2024-01-01'
GROUP BY user_id
ORDER BY total_amount DESC;

-- 使用PREWHERE优化查询
-- PREWHERE在读取所有列之前先过滤数据
SELECT user_id, order_id, price, quantity
FROM orders_optimized 
PREWHERE status = 'paid'  -- 先过滤状态
WHERE price > 100         -- 再过滤价格
    AND order_date >= today() - 30;

-- =====================================
-- 5. 聚合查询优化
-- =====================================

-- 使用物化视图预计算聚合
CREATE MATERIALIZED VIEW orders_daily_stats
ENGINE = SummingMergeTree()
ORDER BY (order_date, category_id)
AS SELECT 
    order_date,
    category_id,
    count() as order_count,
    sum(price * quantity) as total_amount,
    uniq(user_id) as unique_users
FROM orders_optimized
GROUP BY order_date, category_id;

-- 使用AggregatingMergeTree进行复杂聚合
CREATE TABLE orders_aggregated (
    order_date Date,
    category_id UInt16,
    order_count AggregateFunction(count),
    total_amount AggregateFunction(sum, Decimal64(2)),
    unique_users AggregateFunction(uniq, UInt64),
    avg_price AggregateFunction(avg, Decimal64(2))
) ENGINE = AggregatingMergeTree()
ORDER BY (order_date, category_id);

-- 插入聚合数据
INSERT INTO orders_aggregated
SELECT 
    order_date,
    category_id,
    countState() as order_count,
    sumState(price * quantity) as total_amount,
    uniqState(user_id) as unique_users,
    avgState(price) as avg_price
FROM orders_optimized
GROUP BY order_date, category_id;

-- 查询聚合数据
SELECT 
    order_date,
    category_id,
    countMerge(order_count) as total_orders,
    sumMerge(total_amount) as revenue,
    uniqMerge(unique_users) as customers,
    avgMerge(avg_price) as average_price
FROM orders_aggregated
WHERE order_date >= today() - 30
GROUP BY order_date, category_id
ORDER BY order_date DESC, revenue DESC;

-- =====================================
-- 6. JOIN优化最佳实践
-- =====================================

-- 创建用户表
CREATE TABLE users_optimized (
    user_id UInt64,
    username String,
    email String,
    registration_date Date,
    user_type Enum8('free' = 1, 'premium' = 2, 'enterprise' = 3),
    region String
) ENGINE = MergeTree()
ORDER BY user_id;

-- 插入用户数据
INSERT INTO users_optimized
SELECT 
    number as user_id,
    concat('user_', toString(number)) as username,
    concat('user_', toString(number), '@example.com') as email,
    today() - INTERVAL (number % 1000) DAY as registration_date,
    (['free', 'premium', 'enterprise'])[number % 3 + 1] as user_type,
    (['US', 'EU', 'ASIA'])[number % 3 + 1] as region
FROM numbers(100000);

-- 使用字典替代JOIN（推荐）
CREATE DICTIONARY user_dict (
    user_id UInt64,
    username String,
    user_type String,
    region String
) PRIMARY KEY user_id
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 TABLE 'users_optimized' DB 'best_practices_demo'))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED());

-- 使用字典的查询（高效）
SELECT 
    user_id,
    dictGet('user_dict', 'username', user_id) as username,
    dictGet('user_dict', 'user_type', user_id) as user_type,
    sum(price * quantity) as total_spent
FROM orders_optimized
WHERE order_date >= today() - 30
GROUP BY user_id
ORDER BY total_spent DESC
LIMIT 10;

-- 传统JOIN查询（对比）
SELECT 
    o.user_id,
    u.username,
    u.user_type,
    sum(o.price * o.quantity) as total_spent
FROM orders_optimized o
GLOBAL JOIN users_optimized u ON o.user_id = u.user_id
WHERE o.order_date >= today() - 30
GROUP BY o.user_id, u.username, u.user_type
ORDER BY total_spent DESC
LIMIT 10;

-- =====================================
-- 7. 数据类型优化示例
-- =====================================

-- 优化前：使用不当的数据类型
CREATE TABLE events_unoptimized (
    event_id String,          -- 应该用数字
    timestamp String,         -- 应该用DateTime
    user_id String,          -- 应该用数字
    event_type String,       -- 应该用枚举
    status String,           -- 应该用枚举
    amount String,           -- 应该用数值
    metadata String          -- JSON数据
) ENGINE = MergeTree()
ORDER BY event_id;

-- 优化后：使用合适的数据类型
CREATE TABLE events_optimized (
    event_id UInt64,                    -- 数字类型
    timestamp DateTime,                 -- 时间类型
    user_id UInt64,                    -- 数字类型
    event_type LowCardinality(String), -- 低基数字符串
    status Enum8('active' = 1, 'inactive' = 2, 'pending' = 3),  -- 枚举
    amount Decimal64(2),               -- 精确数值
    metadata JSON                      -- 结构化JSON (ClickHouse 21.12+)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp);

-- =====================================
-- 8. 性能监控查询
-- =====================================

-- 监控慢查询
CREATE VIEW slow_queries_monitor AS
SELECT 
    query_id,
    user,
    query_duration_ms,
    read_rows,
    formatReadableSize(read_bytes) as read_bytes,
    formatReadableSize(memory_usage) as memory_usage,
    substring(query, 1, 200) as query_preview
FROM system.query_log
WHERE event_date >= today() - 1
    AND type = 'QueryFinish'
    AND query_duration_ms > 10000  -- 超过10秒的查询
ORDER BY query_duration_ms DESC;

-- 监控表大小和增长
CREATE VIEW table_size_monitor AS
SELECT 
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as size_on_disk,
    formatReadableSize(sum(bytes)) as uncompressed_size,
    sum(rows) as total_rows,
    count() as parts_count,
    max(modification_time) as last_modified
FROM system.parts
WHERE active = 1
    AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;

-- 监控分区状态
CREATE VIEW partition_monitor AS
SELECT 
    database,
    table,
    partition,
    formatReadableSize(sum(bytes_on_disk)) as partition_size,
    sum(rows) as partition_rows,
    count() as parts_in_partition,
    min(min_date) as min_date,
    max(max_date) as max_date,
    max(modification_time) as last_modified
FROM system.parts
WHERE active = 1
    AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
GROUP BY database, table, partition
HAVING count() > 1
ORDER BY sum(bytes_on_disk) DESC;

-- 监控内存使用
CREATE VIEW memory_usage_monitor AS
SELECT 
    query_id,
    user,
    formatReadableSize(memory_usage) as current_memory,
    formatReadableSize(peak_memory_usage) as peak_memory,
    elapsed,
    substring(query, 1, 100) as query_preview
FROM system.processes
WHERE query != ''
ORDER BY memory_usage DESC;

-- =====================================
-- 9. 数据质量检查
-- =====================================

-- 检查重复数据
SELECT 
    user_id,
    order_date,
    order_id,
    count() as duplicate_count
FROM orders_optimized
GROUP BY user_id, order_date, order_id
HAVING count() > 1
ORDER BY duplicate_count DESC;

-- 检查数据完整性
SELECT 
    'orders_optimized' as table_name,
    count() as total_rows,
    count(DISTINCT user_id) as unique_users,
    count(DISTINCT order_id) as unique_orders,
    countIf(price <= 0) as invalid_prices,
    countIf(quantity <= 0) as invalid_quantities,
    countIf(user_id = 0) as missing_user_ids
FROM orders_optimized;

-- 检查数据分布
SELECT 
    status,
    count() as order_count,
    round(count() * 100.0 / (SELECT count() FROM orders_optimized), 2) as percentage
FROM orders_optimized
GROUP BY status
ORDER BY order_count DESC;

-- =====================================
-- 10. 优化建议查询
-- =====================================

-- 查找需要优化的表（分区过多）
SELECT 
    database,
    table,
    count() as partition_count,
    formatReadableSize(sum(bytes_on_disk)) as total_size
FROM system.parts
WHERE active = 1
    AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
GROUP BY database, table
HAVING count() > 100  -- 分区数超过100
ORDER BY count() DESC;

-- 查找小分区（需要合并）
SELECT 
    database,
    table,
    partition,
    formatReadableSize(sum(bytes_on_disk)) as partition_size,
    count() as parts_count
FROM system.parts
WHERE active = 1
    AND bytes_on_disk < 1048576  -- 小于1MB的部分
GROUP BY database, table, partition
HAVING count() > 1
ORDER BY sum(bytes_on_disk);

-- 查找缺少索引的大表
SELECT 
    t.database,
    t.table,
    formatReadableSize(p.total_bytes) as table_size,
    t.sorting_key,
    'Consider adding skip indexes' as recommendation
FROM system.tables t
JOIN (
    SELECT 
        database,
        table,
        sum(bytes_on_disk) as total_bytes
    FROM system.parts
    WHERE active = 1
    GROUP BY database, table
    HAVING sum(bytes_on_disk) > 1073741824  -- 大于1GB
) p ON t.database = p.database AND t.table = p.table
LEFT JOIN system.data_skipping_indices i ON t.database = i.database AND t.table = i.table
WHERE t.engine LIKE '%MergeTree%'
    AND i.name IS NULL
    AND t.database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
ORDER BY p.total_bytes DESC;

-- =====================================
-- 11. 清理和维护
-- =====================================

-- 优化表（合并分区）
-- OPTIMIZE TABLE orders_optimized;

-- 清理过期数据
-- ALTER TABLE orders_optimized DELETE WHERE order_date < today() - 365;

-- 重建统计信息
-- ANALYZE TABLE orders_optimized;

-- 检查表一致性
-- CHECK TABLE orders_optimized;

-- =====================================
-- 12. 性能测试查询
-- =====================================

-- 测试查询性能
SELECT 'Performance Test Results' as test_name;

-- 测试1：简单聚合查询
SELECT 
    'Simple Aggregation' as test_type,
    count() as total_orders,
    sum(price * quantity) as total_revenue,
    avg(price) as avg_price
FROM orders_optimized
WHERE order_date >= today() - 30;

-- 测试2：复杂分组查询
SELECT 
    'Complex Grouping' as test_type,
    category_id,
    status,
    count() as order_count,
    avg(price * quantity) as avg_order_value,
    uniq(user_id) as unique_customers
FROM orders_optimized
WHERE order_date >= today() - 30
GROUP BY category_id, status
ORDER BY order_count DESC
LIMIT 20;

-- 测试3：时间序列查询
SELECT 
    'Time Series' as test_type,
    toStartOfDay(order_date) as day,
    count() as daily_orders,
    sum(price * quantity) as daily_revenue
FROM orders_optimized
WHERE order_date >= today() - 30
GROUP BY day
ORDER BY day;

-- 查看查询执行计划
EXPLAIN SYNTAX SELECT user_id, sum(price * quantity) 
FROM orders_optimized 
WHERE order_date >= today() - 7 
GROUP BY user_id;

-- 查看查询管道
EXPLAIN PIPELINE SELECT user_id, sum(price * quantity) 
FROM orders_optimized 
WHERE order_date >= today() - 7 
GROUP BY user_id;

-- =====================================
-- 总结和最佳实践清单
-- =====================================

SELECT '=== ClickHouse 最佳实践总结 ===' as summary;

SELECT '表设计最佳实践:' as category, practice FROM (
    SELECT '1. 选择合适的数据类型' as practice
    UNION ALL SELECT '2. 优化主键和排序键设计'
    UNION ALL SELECT '3. 合理设计分区策略'
    UNION ALL SELECT '4. 添加适当的跳数索引'
    UNION ALL SELECT '5. 使用枚举替代字符串'
);

SELECT '查询优化最佳实践:' as category, practice FROM (
    SELECT '1. 避免在WHERE中使用函数' as practice
    UNION ALL SELECT '2. 使用PREWHERE预过滤'
    UNION ALL SELECT '3. 利用主键索引顺序'
    UNION ALL SELECT '4. 使用字典替代JOIN'
    UNION ALL SELECT '5. 合理使用物化视图'
);

SELECT '运维监控最佳实践:' as category, practice FROM (
    SELECT '1. 定期监控慢查询' as practice
    UNION ALL SELECT '2. 监控表大小和增长'
    UNION ALL SELECT '3. 检查分区状态'
    UNION ALL SELECT '4. 监控内存使用'
    UNION ALL SELECT '5. 定期优化和清理'
);

-- 清理演示数据（可选）
-- DROP DATABASE IF EXISTS best_practices_demo; 