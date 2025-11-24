-- ClickHouse 数据迁移演示
-- 场景：从3分片2副本集群迁移到1分片2副本集群
-- 日期：2024-03-01

-- ==================== 第一部分：环境准备 ====================

-- 1. 检查源集群状态
SELECT 
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    is_local
FROM system.clusters 
WHERE cluster = 'cluster_3s_2r'
ORDER BY shard_num, replica_num;

-- 2. 检查目标集群状态
SELECT 
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    is_local
FROM system.clusters 
WHERE cluster = 'cluster_1s_2r'
ORDER BY shard_num, replica_num;

-- 3. 查看源集群数据分布
SELECT 
    hostName() as host,
    database,
    table,
    count(*) as parts,
    sum(rows) as total_rows,
    formatReadableSize(sum(bytes_on_disk)) as total_size
FROM cluster('cluster_3s_2r', system.parts)
WHERE active = 1
  AND database NOT IN ('system', 'information_schema')
GROUP BY hostName(), database, table
ORDER BY sum(bytes_on_disk) DESC;

-- 4. 检查副本同步状态
SELECT 
    database,
    table,
    is_leader,
    total_replicas,
    active_replicas,
    absolute_delay,
    queue_size,
    log_max_index,
    log_pointer,
    total_replicas - active_replicas as lagging_replicas
FROM cluster('cluster_3s_2r', system.replicas)
WHERE absolute_delay > 0 OR queue_size > 0
ORDER BY absolute_delay DESC, queue_size DESC;

-- ==================== 第二部分：创建测试数据 ====================

-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS migration_test ON CLUSTER cluster_3s_2r;

-- 创建分布式表示例1：用户行为事件表
CREATE TABLE migration_test.user_events_local ON CLUSTER cluster_3s_2r
(
    event_id UInt64,
    user_id UInt32,
    event_type String,
    event_time DateTime,
    event_date Date DEFAULT toDate(event_time),
    properties Map(String, String),
    session_id String,
    page_url String,
    referrer String,
    user_agent String,
    ip String,
    country String,
    city String
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{cluster}-{shard}/user_events', '{replica}')
PARTITION BY toYYYYMM(event_date)
ORDER BY (user_id, event_time, event_id)
SAMPLE BY intHash32(user_id)
TTL event_date + INTERVAL 2 YEAR DELETE
SETTINGS index_granularity = 8192;

-- 创建分布式表
CREATE TABLE migration_test.user_events ON CLUSTER cluster_3s_2r AS migration_test.user_events_local
ENGINE = Distributed(cluster_3s_2r, migration_test, user_events_local, rand());

-- 创建测试表2：电商订单表
CREATE TABLE migration_test.orders_local ON CLUSTER cluster_3s_2r
(
    order_id UInt64,
    customer_id UInt32,
    order_date Date,
    order_time DateTime,
    status Enum8('pending' = 1, 'processing' = 2, 'shipped' = 3, 'delivered' = 4, 'cancelled' = 5),
    total_amount Decimal(10,2),
    currency FixedString(3),
    items Array(Tuple(product_id UInt32, quantity UInt16, price Decimal(8,2))),
    shipping_address String,
    payment_method String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{cluster}-{shard}/orders', '{replica}')
PARTITION BY toYYYYMM(order_date)
ORDER BY (customer_id, order_date, order_id)
SETTINGS index_granularity = 8192;

CREATE TABLE migration_test.orders ON CLUSTER cluster_3s_2r AS migration_test.orders_local
ENGINE = Distributed(cluster_3s_2r, migration_test, orders_local, intHash32(customer_id));

-- 创建测试表3：产品目录表
CREATE TABLE migration_test.products_local ON CLUSTER cluster_3s_2r
(
    product_id UInt32,
    name String,
    category String,
    subcategory String,
    brand String,
    price Decimal(8,2),
    cost Decimal(8,2),
    description String,
    attributes Map(String, String),
    is_active Bool DEFAULT true,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{cluster}-{shard}/products', '{replica}')
ORDER BY product_id
SETTINGS index_granularity = 8192;

CREATE TABLE migration_test.products ON CLUSTER cluster_3s_2r AS migration_test.products_local
ENGINE = Distributed(cluster_3s_2r, migration_test, products_local, rand());

-- ==================== 第三部分：插入测试数据 ====================

-- 插入用户行为数据
INSERT INTO migration_test.user_events 
SELECT 
    number as event_id,
    number % 100000 as user_id,
    arrayElement(['click', 'view', 'purchase', 'add_to_cart', 'remove_from_cart'], number % 5 + 1) as event_type,
    now() - INTERVAL (number % 86400) SECOND as event_time,
    today() - INTERVAL (number % 30) DAY as event_date,
    map('key1', toString(number), 'key2', toString(number * 2)) as properties,
    concat('session_', toString(number % 10000)) as session_id,
    concat('https://example.com/page/', toString(number % 1000)) as page_url,
    concat('https://referrer.com/page/', toString(number % 500)) as referrer,
    'Mozilla/5.0 (compatible; Bot)' as user_agent,
    concat('192.168.', toString(number % 256), '.', toString((number * 7) % 256)) as ip,
    arrayElement(['US', 'CN', 'UK', 'DE', 'FR'], number % 5 + 1) as country,
    arrayElement(['New York', 'Beijing', 'London', 'Berlin', 'Paris'], number % 5 + 1) as city
FROM numbers(1000000);

-- 插入订单数据
INSERT INTO migration_test.orders
SELECT 
    number as order_id,
    number % 50000 as customer_id,
    today() - INTERVAL (number % 365) DAY as order_date,
    now() - INTERVAL (number % 86400) SECOND as order_time,
    arrayElement(['pending', 'processing', 'shipped', 'delivered', 'cancelled'], number % 5 + 1) as status,
    round((number % 1000 + 10) * 1.5, 2) as total_amount,
    'USD' as currency,
    [(number % 100 + 1, number % 10 + 1, round((number % 50 + 5) * 1.2, 2))] as items,
    concat('Address ', toString(number % 10000)) as shipping_address,
    arrayElement(['credit_card', 'paypal', 'bank_transfer'], number % 3 + 1) as payment_method,
    now() - INTERVAL (number % 86400) SECOND as created_at,
    now() - INTERVAL (number % 43200) SECOND as updated_at
FROM numbers(500000);

-- 插入产品数据
INSERT INTO migration_test.products
SELECT 
    number as product_id,
    concat('Product ', toString(number)) as name,
    arrayElement(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], number % 5 + 1) as category,
    concat('Subcategory ', toString(number % 20)) as subcategory,
    concat('Brand ', toString(number % 100)) as brand,
    round((number % 500 + 10) * 1.5, 2) as price,
    round((number % 500 + 10) * 0.7, 2) as cost,
    concat('Description for product ', toString(number)) as description,
    map('color', arrayElement(['red', 'blue', 'green', 'black', 'white'], number % 5 + 1),
        'size', arrayElement(['S', 'M', 'L', 'XL'], number % 4 + 1)) as attributes,
    if(number % 10 = 0, false, true) as is_active,
    now() - INTERVAL (number % 86400) SECOND as created_at,
    now() - INTERVAL (number % 43200) SECOND as updated_at
FROM numbers(10000);

-- ==================== 第四部分：迁移前数据统计 ====================

-- 统计源集群数据
SELECT 
    '源集群数据统计' as info,
    database,
    table,
    sum(rows) as total_rows,
    formatReadableSize(sum(bytes_on_disk)) as total_size,
    count(*) as total_parts,
    countDistinct(partition) as partitions
FROM cluster('cluster_3s_2r', system.parts)
WHERE active = 1 
  AND database = 'migration_test'
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;

-- 检查数据分布均匀性
SELECT 
    '数据分布检查' as info,
    hostName() as host,
    database,
    table,
    sum(rows) as rows_per_host,
    formatReadableSize(sum(bytes_on_disk)) as size_per_host
FROM cluster('cluster_3s_2r', system.parts)
WHERE active = 1 
  AND database = 'migration_test'
GROUP BY hostName(), database, table
ORDER BY database, table, hostName();

-- 业务数据验证查询
SELECT 
    '用户事件数据验证' as check_type,
    count(*) as total_events,
    countDistinct(user_id) as unique_users,
    min(event_date) as min_date,
    max(event_date) as max_date,
    countDistinct(event_type) as event_types
FROM migration_test.user_events;

SELECT 
    '订单数据验证' as check_type,
    count(*) as total_orders,
    countDistinct(customer_id) as unique_customers,
    sum(total_amount) as total_revenue,
    min(order_date) as min_date,
    max(order_date) as max_date,
    countDistinct(status) as order_statuses
FROM migration_test.orders;

SELECT 
    '产品数据验证' as check_type,
    count(*) as total_products,
    countDistinct(category) as categories,
    countDistinct(brand) as brands,
    sum(if(is_active, 1, 0)) as active_products,
    avg(price) as avg_price
FROM migration_test.products;

-- ==================== 第五部分：目标集群表创建 ====================

-- 注意：这些命令需要在目标集群上执行

-- 创建目标数据库
-- CREATE DATABASE IF NOT EXISTS migration_test ON CLUSTER cluster_1s_2r;

-- 创建目标表（1分片2副本）
-- CREATE TABLE migration_test.user_events_local ON CLUSTER cluster_1s_2r
-- (
--     event_id UInt64,
--     user_id UInt32,
--     event_type String,
--     event_time DateTime,
--     event_date Date DEFAULT toDate(event_time),
--     properties Map(String, String),
--     session_id String,
--     page_url String,
--     referrer String,
--     user_agent String,
--     ip String,
--     country String,
--     city String
-- )
-- ENGINE = ReplicatedMergeTree('/clickhouse/tables/{cluster}-{shard}/user_events', '{replica}')
-- PARTITION BY toYYYYMM(event_date)
-- ORDER BY (user_id, event_time, event_id)
-- SAMPLE BY intHash32(user_id)
-- TTL event_date + INTERVAL 2 YEAR DELETE
-- SETTINGS index_granularity = 8192;

-- CREATE TABLE migration_test.user_events ON CLUSTER cluster_1s_2r AS migration_test.user_events_local
-- ENGINE = Distributed(cluster_1s_2r, migration_test, user_events_local, rand());

-- ==================== 第六部分：数据迁移 ====================

-- 使用INSERT INTO ... SELECT进行数据迁移
-- 注意：这些命令需要在目标集群上执行

-- 迁移用户事件数据
-- INSERT INTO migration_test.user_events 
-- SELECT * FROM remote('cluster_3s_2r', migration_test.user_events);

-- 迁移订单数据
-- INSERT INTO migration_test.orders 
-- SELECT * FROM remote('cluster_3s_2r', migration_test.orders);

-- 迁移产品数据  
-- INSERT INTO migration_test.products 
-- SELECT * FROM remote('cluster_3s_2r', migration_test.products);

-- ==================== 第七部分：数据校验查询 ====================

-- 行数对比校验
WITH source_counts AS (
    SELECT 
        database,
        table,
        sum(rows) as source_rows
    FROM remote('cluster_3s_2r', system.parts)
    WHERE active = 1 AND database = 'migration_test'
    GROUP BY database, table
),
target_counts AS (
    SELECT 
        database,
        table,
        sum(rows) as target_rows
    FROM system.parts
    WHERE active = 1 AND database = 'migration_test'
    GROUP BY database, table
)
SELECT 
    '行数校验' as validation_type,
    s.database,
    s.table,
    s.source_rows,
    t.target_rows,
    s.source_rows - t.target_rows as difference,
    if(s.source_rows = t.target_rows, 'PASS', 'FAIL') as status
FROM source_counts s
FULL OUTER JOIN target_counts t ON s.database = t.database AND s.table = t.table
ORDER BY database, table;

-- 业务指标对比校验
SELECT 
    '用户事件业务校验' as validation_type,
    'source' as cluster_type,
    count(*) as total_events,
    countDistinct(user_id) as unique_users,
    countDistinct(event_type) as event_types,
    toYYYYMM(min(event_date)) as min_month,
    toYYYYMM(max(event_date)) as max_month
FROM remote('cluster_3s_2r', migration_test.user_events)

UNION ALL

SELECT 
    '用户事件业务校验' as validation_type,
    'target' as cluster_type,
    count(*) as total_events,
    countDistinct(user_id) as unique_users,
    countDistinct(event_type) as event_types,
    toYYYYMM(min(event_date)) as min_month,
    toYYYYMM(max(event_date)) as max_month
FROM migration_test.user_events;

-- 订单数据业务校验
SELECT 
    '订单业务校验' as validation_type,
    'source' as cluster_type,
    count(*) as total_orders,
    countDistinct(customer_id) as unique_customers,
    round(sum(total_amount), 2) as total_revenue,
    round(avg(total_amount), 2) as avg_order_value
FROM remote('cluster_3s_2r', migration_test.orders)

UNION ALL

SELECT 
    '订单业务校验' as validation_type,
    'target' as cluster_type,
    count(*) as total_orders,
    countDistinct(customer_id) as unique_customers,
    round(sum(total_amount), 2) as total_revenue,
    round(avg(total_amount), 2) as avg_order_value
FROM migration_test.orders;

-- 产品数据业务校验
SELECT 
    '产品业务校验' as validation_type,
    'source' as cluster_type,
    count(*) as total_products,
    countDistinct(category) as categories,
    countDistinct(brand) as brands,
    sum(if(is_active, 1, 0)) as active_products,
    round(avg(price), 2) as avg_price
FROM remote('cluster_3s_2r', migration_test.products)

UNION ALL

SELECT 
    '产品业务校验' as validation_type,
    'target' as cluster_type,
    count(*) as total_products,
    countDistinct(category) as categories,
    countDistinct(brand) as brands,
    sum(if(is_active, 1, 0)) as active_products,
    round(avg(price), 2) as avg_price
FROM migration_test.products;

-- ==================== 第八部分：性能对比测试 ====================

-- 查询性能测试1：用户行为分析
SELECT 
    '性能测试1' as test_name,
    event_type,
    count(*) as event_count,
    countDistinct(user_id) as unique_users,
    round(count(*) * 100.0 / (SELECT count(*) FROM migration_test.user_events), 2) as percentage
FROM migration_test.user_events
GROUP BY event_type
ORDER BY event_count DESC;

-- 查询性能测试2：月度订单分析
SELECT 
    '性能测试2' as test_name,
    toYYYYMM(order_date) as order_month,
    count(*) as orders,
    countDistinct(customer_id) as customers,
    sum(total_amount) as revenue,
    round(avg(total_amount), 2) as avg_order_value
FROM migration_test.orders
WHERE order_date >= today() - INTERVAL 12 MONTH
GROUP BY toYYYYMM(order_date)
ORDER BY order_month DESC;

-- 查询性能测试3：复杂JOIN查询
SELECT 
    '性能测试3' as test_name,
    p.category,
    count(DISTINCT o.order_id) as orders,
    sum(item.quantity * item.price) as revenue
FROM migration_test.orders o
ARRAY JOIN o.items as item
JOIN migration_test.products p ON item.product_id = p.product_id
WHERE o.order_date >= today() - INTERVAL 30 DAY
GROUP BY p.category
ORDER BY revenue DESC;

-- ==================== 第九部分：清理和优化 ====================

-- 优化目标表
-- OPTIMIZE TABLE migration_test.user_events_local ON CLUSTER cluster_1s_2r FINAL;
-- OPTIMIZE TABLE migration_test.orders_local ON CLUSTER cluster_1s_2r FINAL;
-- OPTIMIZE TABLE migration_test.products_local ON CLUSTER cluster_1s_2r FINAL;

-- 检查最终状态
SELECT 
    '最终状态检查' as info,
    database,
    table,
    sum(rows) as total_rows,
    formatReadableSize(sum(bytes_on_disk)) as total_size,
    count(*) as total_parts,
    min(min_date) as data_min_date,
    max(max_date) as data_max_date
FROM system.parts
WHERE active = 1 
  AND database = 'migration_test'
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;

-- 检查副本状态
SELECT 
    '副本状态检查' as info,
    database,
    table,
    is_leader,
    total_replicas,
    active_replicas,
    absolute_delay,
    queue_size
FROM system.replicas
WHERE database = 'migration_test'
ORDER BY database, table;

-- ==================== 第十部分：监控查询 ====================

-- 系统资源监控
SELECT 
    '系统监控' as info,
    formatReadableSize(free_space) as free_space,
    formatReadableSize(total_space) as total_space,
    round(free_space * 100.0 / total_space, 2) as free_percent
FROM system.disks
WHERE name = 'default';

-- 查询性能监控
SELECT 
    '查询性能监控' as info,
    count(*) as query_count,
    round(avg(query_duration_ms), 2) as avg_duration_ms,
    round(avg(read_rows), 2) as avg_read_rows,
    formatReadableSize(round(avg(read_bytes), 2)) as avg_read_bytes
FROM system.query_log
WHERE event_date = today()
  AND query_duration_ms > 1000
  AND type = 'QueryFinish';

-- 表大小变化监控
SELECT 
    '表大小监控' as info,
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as current_size,
    count(*) as parts_count,
    sum(rows) as total_rows
FROM system.parts
WHERE active = 1
  AND database = 'migration_test'
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;

-- 完成迁移演示 