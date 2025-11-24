-- ClickHouse高级特性示例代码
-- 本文件包含ClickHouse引擎系列、物化视图、投影、分布式和性能优化的实际示例

-- ================================
-- 1. MergeTree系列引擎示例
-- ================================

-- 1.1 基础MergeTree表
CREATE TABLE events (
    event_id UInt64,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    page_url String,
    referrer String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type)
SETTINGS index_granularity = 8192;

-- 插入示例数据
INSERT INTO events VALUES
    (1, '2023-01-01 08:00:00', 1001, 'page_view', '/home', '', 'device=mobile,os=ios'),
    (2, '2023-01-01 08:01:00', 1001, 'click', '/products/123', '/home', 'element=button,page=product'),
    (3, '2023-01-01 08:02:00', 1002, 'page_view', '/home', '', 'device=desktop,os=windows'),
    (4, '2023-01-01 08:03:00', 1001, 'page_view', '/products/123', '/home', 'device=mobile,os=ios'),
    (5, '2023-01-01 08:04:00', 1002, 'click', '/cart', '/products/123', 'element=button,page=cart'),
    (6, '2023-01-01 08:05:00', 1003, 'page_view', '/products/456', '', 'device=mobile,os=android'),
    (7, '2023-01-01 08:06:00', 1003, 'add_to_cart', '/cart', '/products/456', 'product_id=456,quantity=1'),
    (8, '2023-01-01 08:07:00', 1003, 'checkout', '/checkout', '/cart', 'items=1,total=99.99');

-- 1.2 ReplacingMergeTree示例 - 用户状态表
CREATE TABLE user_status (
    user_id UInt64,
    status String,
    update_time DateTime,
    version UInt64
) ENGINE = ReplacingMergeTree(version)
PARTITION BY toYYYYMM(update_time)
ORDER BY user_id;

-- 插入用户状态数据
INSERT INTO user_status VALUES
    (1001, 'active', '2023-01-01 08:00:00', 1672567200),
    (1002, 'inactive', '2023-01-01 09:00:00', 1672570800),
    (1003, 'active', '2023-01-01 10:00:00', 1672574400);

-- 更新用户状态
INSERT INTO user_status VALUES
    (1001, 'premium', '2023-01-02 08:00:00', 1672653600),  -- 更新用户1001状态
    (1002, 'active', '2023-01-02 09:00:00', 1672657200);  -- 更新用户1002状态

-- 手动触发合并
OPTIMIZE TABLE user_status FINAL;

-- 1.3 SummingMergeTree示例 - 每日计数器
CREATE TABLE daily_counters (
    date Date,
    counter_name String,
    value UInt64
) ENGINE = SummingMergeTree(value)
PARTITION BY toYYYYMM(date)
ORDER BY (date, counter_name);

-- 插入计数器数据
INSERT INTO daily_counters VALUES
    ('2023-01-01', 'page_views', 1000),
    ('2023-01-01', 'page_views', 1500),
    ('2023-01-01', 'clicks', 300),
    ('2023-01-01', 'clicks', 200),
    ('2023-01-01', 'signups', 50),
    ('2023-01-01', 'signups', 30);

-- 再次插入相同计数器的值
INSERT INTO daily_counters VALUES
    ('2023-01-01', 'page_views', 500),
    ('2023-01-01', 'clicks', 100),
    ('2023-01-02', 'page_views', 2000),
    ('2023-01-02', 'clicks', 400);

-- 触发合并
OPTIMIZE TABLE daily_counters FINAL;

-- 查看合并后的结果
SELECT date, counter_name, value FROM daily_counters ORDER BY date, counter_name;

-- 1.4 AggregatingMergeTree示例 - 用户行为预聚合
CREATE TABLE user_behavior_daily (
    date Date,
    user_group String,
    page_views AggregateFunction(sum, UInt64),
    unique_users AggregateFunction(uniq, UInt64),
    avg_session_duration AggregateFunction(avg, UInt64)
) ENGINE = AggregatingMergeTree()
PARTITION BY date
ORDER BY (date, user_group);

-- 插入预聚合数据
INSERT INTO user_behavior_daily SELECT
    toDate(event_time) AS date,
    CASE WHEN user_id % 1000 < 500 THEN 'group_a' ELSE 'group_b' END AS user_group,
    sumState(toUInt64(1)) AS page_views,
    uniqState(user_id) AS unique_users,
    avgState(toUInt32(dateDiff('second', event_time, lead(event_time) OVER (PARTITION BY user_id ORDER BY event_time)))) AS avg_session_duration
FROM events
WHERE event_time >= '2023-01-01' AND event_time < '2023-01-02'
GROUP BY date, user_group;

-- 查询聚合结果
SELECT 
    date,
    user_group,
    sumMerge(page_views) AS total_page_views,
    uniqMerge(unique_users) AS total_unique_users,
    avgMerge(avg_session_duration) AS avg_session_duration
FROM user_behavior_daily
WHERE date = '2023-01-01'
GROUP BY date, user_group;

-- ================================
-- 2. 物化视图示例
-- ================================

-- 2.1 创建源表
CREATE TABLE sales (
    order_id UInt64,
    customer_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, product_id);

-- 创建目标表
CREATE TABLE sales_daily_summary (
    date Date,
    product_id UInt64,
    region String,
    channel String,
    total_amount Decimal(15, 2),
    order_count UInt64
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, product_id, region, channel);

-- 创建物化视图
CREATE MATERIALIZED VIEW sales_daily_mv TO sales_daily_summary AS
SELECT 
    toDate(order_time) AS date,
    product_id,
    region,
    channel,
    sum(amount) AS total_amount,
    count() AS order_count
FROM sales
GROUP BY date, product_id, region, channel;

-- 插入销售数据
INSERT INTO sales VALUES
    (1, 1001, 101, '2023-01-01 09:00:00', 199.99, 'North', 'Online'),
    (2, 1002, 102, '2023-01-01 10:00:00', 299.99, 'South', 'Offline'),
    (3, 1001, 103, '2023-01-01 11:00:00', 149.99, 'North', 'Online'),
    (4, 1003, 101, '2023-01-01 12:00:00', 199.99, 'East', 'Online'),
    (5, 1004, 104, '2023-01-02 09:00:00', 399.99, 'West', 'Offline'),
    (6, 1002, 105, '2023-01-02 10:00:00', 249.99, 'South', 'Online'),
    (7, 1005, 101, '2023-01-02 11:00:00', 199.99, 'North', 'Online'),
    (8, 1001, 106, '2023-01-02 12:00:00', 349.99, 'North', 'Offline');

-- 查看物化视图结果
SELECT 
    date, 
    product_id, 
    region, 
    channel, 
    total_amount, 
    order_count 
FROM sales_daily_summary 
ORDER BY date, product_id, region, channel;

-- 2.2 多级物化视图 - 分钟级到小时级到日级
-- 分钟级表
CREATE TABLE sales_minute_summary (
    minute DateTime,
    product_id UInt64,
    total_amount Decimal(15, 2),
    order_count UInt64
) ENGINE = SummingMergeTree()
ORDER BY (minute, product_id);

-- 分钟级物化视图
CREATE MATERIALIZED VIEW sales_minute_mv TO sales_minute_summary AS
SELECT 
    toStartOfMinute(order_time) AS minute,
    product_id,
    sum(amount) AS total_amount,
    count() AS order_count
FROM sales
GROUP BY minute, product_id;

-- 小时级表
CREATE TABLE sales_hourly_summary (
    hour DateTime,
    product_id UInt64,
    total_amount Decimal(15, 2),
    order_count UInt64
) ENGINE = SummingMergeTree()
ORDER BY (hour, product_id);

-- 小时级物化视图
CREATE MATERIALIZED VIEW sales_hourly_mv TO sales_hourly_summary AS
SELECT 
    toStartOfHour(minute) AS hour,
    product_id,
    sum(total_amount) AS total_amount,
    sum(order_count) AS order_count
FROM sales_minute_summary
GROUP BY hour, product_id;

-- 日级表
CREATE TABLE sales_daily_v2_summary (
    date Date,
    product_id UInt64,
    total_amount Decimal(15, 2),
    order_count UInt64
) ENGINE = SummingMergeTree()
ORDER BY (date, product_id);

-- 日级物化视图
CREATE MATERIALIZED VIEW sales_daily_v2_mv TO sales_daily_v2_summary AS
SELECT 
    toDate(hour) AS date,
    product_id,
    sum(total_amount) AS total_amount,
    sum(order_count) AS order_count
FROM sales_hourly_summary
GROUP BY date, product_id;

-- ================================
-- 3. 投影(Projection)示例
-- ================================

-- 3.1 创建带投影的表
CREATE TABLE sales_with_projections (
    order_id UInt64,
    customer_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, product_id)
-- 聚合投影
PROJECTION daily_summary (
    SELECT 
        toDate(order_time) AS date,
        product_id,
        region,
        channel,
        sum(amount) AS total_amount,
        count() AS order_count
    GROUP BY date, product_id, region, channel
)
-- 筛选投影
PROJECTION recent_orders (
    SELECT 
        order_id,
        customer_id,
        product_id,
        order_time,
        amount,
        region,
        channel
    WHERE order_time >= today() - INTERVAL 30 DAY
)
-- 排序投影
PROJECTION product_summary (
    SELECT 
        product_id,
        order_time,
        amount,
        region,
        channel
    ORDER BY (product_id, order_time DESC)
);

-- 插入数据
INSERT INTO sales_with_projections SELECT * FROM sales;

-- 使用聚合投影的查询
SELECT 
    date,
    product_id,
    region,
    channel,
    sum(amount) AS total_amount,
    count() AS order_count
FROM sales_with_projections
WHERE date >= '2023-01-01'
GROUP BY date, product_id, region, channel;

-- 使用筛选投影的查询
SELECT *
FROM sales_with_projections
WHERE order_time >= today() - INTERVAL 30 DAY
  AND region = 'North';

-- 使用排序投影的查询
SELECT *
FROM sales_with_projections
WHERE product_id = 101
ORDER BY order_time DESC
LIMIT 100;

-- ================================
-- 4. 分布式引擎示例
-- ================================

-- 注意：以下示例需要在集群环境中运行，这里仅提供语法示例

-- 4.1 创建本地表
CREATE TABLE local_sales ON CLUSTER 'cluster_name' (
    order_id UInt64,
    customer_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, product_id);

-- 4.2 创建分布式表
CREATE TABLE sales_dist ON CLUSTER 'cluster_name' (
    order_id UInt64,
    customer_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = Distributed('cluster_name', 'default', 'local_sales', cityHash64(order_id));

-- 4.3 创建副本表
CREATE TABLE local_sales_replicated ON CLUSTER 'cluster_name' (
    order_id UInt64,
    customer_id UInt64,
    product_id UInt64,
    order_time DateTime,
    amount Decimal(10, 2),
    region String,
    channel String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/sales', '{replica}')
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_time, product_id);

-- ================================
-- 5. 性能优化示例
-- ================================

-- 5.1 索引优化示例
CREATE TABLE events_with_indexes (
    event_id UInt64,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    page_url String,
    referrer String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type)
-- 跳过索引
INDEX idx_event_type event_type TYPE minmax GRANULARITY 1
INDEX idx_user_id user_id TYPE set(1000) GRANULARITY 1
INDEX idx_event_type_bloom event_type TYPE bloom_filter GRANULARITY 1
-- 条件索引
INDEX idx_high_value parseJSONBestEffort(properties)['value'] > 1000 TYPE minmax GRANULARITY 1
INDEX idx_recent_event event_time > (now() - INTERVAL 1 DAY) TYPE minmax GRANULARITY 1;

-- 5.2 压缩优化示例
CREATE TABLE events_with_compression (
    event_id UInt64,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    page_url String,
    referrer String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type)
SETTINGS compression = {
    'event_id': 'NONE',                 -- ID列不压缩
    'event_time': 'Delta,ZSTD',         -- 时间列先Delta编码再压缩
    'event_type': 'LZ4',                -- 低基数列使用LZ4
    'page_url': 'ZSTD(10)',             -- URL列使用高压缩率ZSTD
    'properties': 'ZSTD(12)',           -- 属性列使用最高压缩率ZSTD
    'user_id': 'ZSTD'                   -- 用户ID使用标准ZSTD
};

-- 5.3 TTL优化示例
CREATE TABLE events_with_ttl (
    event_id UInt64,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    page_url String,
    referrer String,
    properties String,
    is_important Boolean DEFAULT 0
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type)
TTL 
    event_time + INTERVAL 30 DAY DELETE WHERE event_type = 'page_view',
    event_time + INTERVAL 60 DAY DELETE WHERE event_type = 'click',
    event_time + INTERVAL 90 DAY DELETE WHERE event_type = 'purchase',
    event_time + INTERVAL 180 DAY DELETE WHERE is_important = 0,
    event_time + INTERVAL 3 YEAR
SETTINGS
    merge_with_ttl_timeout = 3600;  -- 每小时检查一次TTL

-- 5.4 抽样优化示例
CREATE TABLE events_with_sampling (
    event_id UInt64,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    page_url String,
    referrer String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type)
SAMPLE BY intHash64(user_id);  -- 基于用户ID的抽样

-- 使用抽样查询
SELECT 
    event_type,
    count() * 10 AS estimated_count,  -- 假设抽样比例为10%
    uniqExact(user_id) * 10 AS estimated_unique_users
FROM events_with_sampling
SAMPLE 0.1  -- 抽样10%的数据
WHERE event_time >= '2023-01-01'
GROUP BY event_type;

-- ================================
-- 6. 高级查询示例
-- ================================

-- 6.1 窗口函数
SELECT 
    user_id,
    event_time,
    event_type,
    -- 用户事件序号
    row_number() OVER (PARTITION BY user_id ORDER BY event_time) AS event_seq,
    -- 会话序号（会话间隔30分钟）
    sumIf(toUInt32(event_time > (lag(event_time, 1, event_time) OVER (PARTITION BY user_id ORDER BY event_time) + INTERVAL 30 MINUTE)), 
         1, 0) OVER (PARTITION BY user_id ORDER BY event_time) AS session_indicator,
    -- 同一类型事件的间隔时间
    event_time - lag(event_time, 1) OVER (PARTITION BY user_id, event_type ORDER BY event_time) AS time_since_last_same_event
FROM events
WHERE event_time >= '2023-01-01'
ORDER BY user_id, event_time;

-- 6.2 时间序列分析
SELECT 
    toDate(event_time) AS date,
    event_type,
    count() AS event_count,
    -- 7日移动平均
    avg(count) OVER (PARTITION BY event_type ORDER BY toDate(event_time) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d,
    -- 28日移动平均
    avg(count) OVER (PARTITION BY event_type ORDER BY toDate(event_time) ROWS BETWEEN 27 PRECEDING AND CURRENT ROW) AS moving_avg_28d,
    -- 同比增长率
    (count() - lag(count, 7) OVER (PARTITION BY event_type ORDER BY toDate(event_time))) / 
    lag(count, 7) OVER (PARTITION BY event_type ORDER BY toDate(event_time)) * 100 AS yoy_growth_percent
FROM events
WHERE event_time >= '2023-01-01'
GROUP BY date, event_type
ORDER BY event_type, date;

-- 6.3 漏斗分析
-- 创建用户会话表
CREATE TABLE user_sessions AS
SELECT 
    user_id,
    min(event_time) AS session_start,
    max(event_time) AS session_end,
    dateDiff('second', min(event_time), max(event_time)) AS session_duration_seconds,
    countIf(event_type = 'page_view') AS page_views,
    countIf(event_type = 'click') AS clicks,
    countIf(event_type = 'add_to_cart') AS add_to_cart,
    countIf(event_type = 'checkout') AS checkout,
    countIf(event_type = 'purchase') AS purchase
FROM events
WHERE event_time >= '2023-01-01'
GROUP BY user_id;

-- 漏斗分析
WITH funnel_stages AS (
    SELECT 
        SUM(page_views) AS page_views,
        SUM(clicks) AS clicks,
        SUM(add_to_cart) AS add_to_cart,
        SUM(checkout) AS checkout,
        SUM(purchase) AS purchase
    FROM user_sessions
),
total_users AS (
    SELECT count() AS total_users FROM user_sessions
)
SELECT 
    'Page Views' AS stage,
    page_views AS users,
    page_views * 100.0 / total_users AS conversion_rate
FROM funnel_stages, total_users

UNION ALL

SELECT 
    'Clicks' AS stage,
    clicks AS users,
    clicks * 100.0 / page_views AS conversion_rate
FROM funnel_stages

UNION ALL

SELECT 
    'Add to Cart' AS stage,
    add_to_cart AS users,
    add_to_cart * 100.0 / clicks AS conversion_rate
FROM funnel_stages

UNION ALL

SELECT 
    'Checkout' AS stage,
    checkout AS users,
    checkout * 100.0 / add_to_cart AS conversion_rate
FROM funnel_stages

UNION ALL

SELECT 
    'Purchase' AS stage,
    purchase AS users,
    purchase * 100.0 / checkout AS conversion_rate
FROM funnel_stages;

-- 6.4 用户留存分析
-- 创建用户首次活跃日期表
CREATE TABLE user_first_active AS
SELECT 
    user_id,
    toDate(min(event_time)) AS first_active_date
FROM events
GROUP BY user_id;

-- 计算用户留存率
WITH active_users AS (
    SELECT 
        ufa.first_active_date AS cohort,
        toDate(e.event_time) AS activity_date,
        dateDiff('day', ufa.first_active_date, toDate(e.event_time)) AS day_number,
        uniqExact(e.user_id) AS active_users
    FROM user_first_active ufa
    JOIN events e ON ufa.user_id = e.user_id
    WHERE e.event_time >= '2023-01-01'
    GROUP BY cohort, activity_date, day_number
),
cohort_sizes AS (
    SELECT 
        first_active_date AS cohort,
        uniqExact(user_id) AS cohort_size
    FROM events
    WHERE event_time >= '2023-01-01'
    GROUP BY first_active_date
)
SELECT 
    cohort,
    day_number,
    cohort_size,
    active_users,
    active_users * 100.0 / cohort_size AS retention_rate
FROM active_users a
JOIN cohort_sizes c ON a.cohort = c.cohort
WHERE day_number BETWEEN 0 AND 30
ORDER BY cohort, day_number;

-- 6.5 高级JSON处理
-- 假设properties列包含JSON格式的数据
-- 提取JSON属性
SELECT 
    event_type,
    -- 提取简单属性
    JSONExtractString(properties, 'device') AS device,
    JSONExtractInt(properties, 'screen_width') AS screen_width,
    JSONExtractFloat(properties, 'value') AS value,
    -- 提取嵌套属性
    JSONExtractString(properties, 'location.country') AS country,
    JSONExtractString(properties, 'location.city') AS city,
    -- 检查属性是否存在
    JSONHas(properties, 'source') AS has_source,
    -- 提取数组属性
    JSONExtractArrayRaw(properties, 'tags') AS tags_array
FROM events
WHERE event_time >= '2023-01-01'
  AND JSONHas(properties, 'device')
  AND JSONHas(properties, 'location.country');

-- 6.6 高级时间函数
SELECT 
    toDate(event_time) AS date,
    -- 获取日期的各种部分
    toYear(event_time) AS year,
    toQuarter(event_time) AS quarter,
    toMonth(event_time) AS month,
    toDayOfMonth(event_time) AS day,
    toDayOfWeek(event_time) AS day_of_week,
    toDayOfYear(event_time) AS day_of_year,
    toISOWeek(event_time) AS iso_week,
    -- 日期计算
    addDays(toDate(event_time), 7) AS next_week,
    addMonths(toDate(event_time), 1) AS next_month,
    dateDiff('day', toDate(event_time), today()) AS days_since,
    -- 时间序列分组
    toStartOfDay(event_time) AS day_start,
    toStartOfWeek(event_time) AS week_start,
    toStartOfMonth(event_time) AS month_start,
    toStartOfQuarter(event_time) AS quarter_start,
    toStartOfYear(event_time) AS year_start,
    -- 时间间隔
    toDateTime(toDate(event_time)) AS date_only,
    timeSlot(event_time, 1800) AS 30min_slot,  -- 30分钟时间槽
    toTime(event_time) AS time_only
FROM events
WHERE event_time >= '2023-01-01'
LIMIT 10;

-- ================================
-- 7. 清理示例表
-- ================================

-- 删除创建的示例表（可选）
-- DROP TABLE IF EXISTS events;
-- DROP TABLE IF EXISTS user_status;
-- DROP TABLE IF EXISTS daily_counters;
-- DROP TABLE IF EXISTS user_behavior_daily;
-- DROP TABLE IF EXISTS sales;
-- DROP TABLE IF EXISTS sales_daily_summary;
-- DROP TABLE IF EXISTS sales_daily_mv;
-- DROP TABLE IF EXISTS sales_minute_summary;
-- DROP TABLE IF EXISTS sales_minute_mv;
-- DROP TABLE IF EXISTS sales_hourly_summary;
-- DROP TABLE IF EXISTS sales_hourly_mv;
-- DROP TABLE IF EXISTS sales_daily_v2_summary;
-- DROP TABLE IF EXISTS sales_daily_v2_mv;
-- DROP TABLE IF EXISTS sales_with_projections;
-- DROP TABLE IF EXISTS events_with_indexes;
-- DROP TABLE IF EXISTS events_with_compression;
-- DROP TABLE IF EXISTS events_with_ttl;
-- DROP TABLE IF EXISTS events_with_sampling;
-- DROP TABLE IF EXISTS user_sessions;
-- DROP TABLE IF EXISTS user_first_active;