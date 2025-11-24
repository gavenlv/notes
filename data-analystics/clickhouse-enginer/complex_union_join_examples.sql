-- ClickHouse复杂UNION和JOIN的物化视图示例
-- 本文件包含了各种复杂场景下的实际应用示例

-- ================================
-- 1. 复杂UNION操作示例
-- ================================

-- 1.1 基础数据表
CREATE TABLE web_events (
    event_id UUID,
    user_id UInt64,
    event_time DateTime,
    page_url String,
    event_type String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id);

CREATE TABLE app_events (
    event_id UUID,
    user_id UInt64,
    event_time DateTime,
    screen_name String,
    event_type String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id);

CREATE TABLE offline_events (
    event_id UUID,
    user_id UInt64,
    event_time DateTime,
    store_id UInt32,
    event_type String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);

-- 1.2 多源数据UNION物化视图
CREATE TABLE unified_events (
    event_id UUID,
    user_id UInt64,
    event_time DateTime,
    page_url String,
    screen_name String,
    store_id UInt32,
    event_type String,
    properties String,
    source_type String
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, source_type);

CREATE MATERIALIZED VIEW all_sources_events_mv TO unified_events AS
SELECT 
    event_id,
    user_id,
    event_time,
    page_url,
    '' AS screen_name,
    0 AS store_id,
    event_type,
    properties,
    'web' AS source_type
FROM web_events

UNION ALL

SELECT 
    event_id,
    user_id,
    event_time,
    '' AS page_url,
    screen_name,
    0 AS store_id,
    event_type,
    properties,
    'app' AS source_type
FROM app_events

UNION ALL

SELECT 
    event_id,
    user_id,
    event_time,
    '' AS page_url,
    '' AS screen_name,
    store_id,
    event_type,
    properties,
    'offline' AS source_type
FROM offline_events;

-- 1.3 条件过滤的UNION物化视图
CREATE TABLE filtered_events (
    event_id UUID,
    user_id UInt64,
    event_time DateTime,
    event_type String,
    source_type String,
    is_premium_user UInt8
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type);

-- 创建用户表
CREATE TABLE users (
    user_id UInt64,
    username String,
    is_premium UInt8 DEFAULT 0,
    registration_date Date
) ENGINE = MergeTree()
ORDER BY user_id;

CREATE MATERIALIZED VIEW filtered_events_mv TO filtered_events AS
SELECT 
    event_id,
    user_id,
    event_time,
    event_type,
    'web' AS source_type,
    u.is_premium
FROM web_events e
JOIN users u ON e.user_id = u.user_id
WHERE e.event_time >= today() - INTERVAL 30 DAY
  AND (u.is_premium = 1 OR e.event_type IN ('purchase', 'checkout'))

UNION ALL

SELECT 
    event_id,
    user_id,
    event_time,
    event_type,
    'app' AS source_type,
    u.is_premium
FROM app_events e
JOIN users u ON e.user_id = u.user_id
WHERE e.event_time >= today() - INTERVAL 30 DAY
  AND (u.is_premium = 1 OR e.event_type IN ('purchase', 'checkout'));

-- 1.4 聚合UNION物化视图
CREATE TABLE daily_source_metrics (
    date Date,
    source_type String,
    event_type String,
    event_count UInt64,
    unique_users AggregateFunction(uniq, UInt64)
) ENGINE = AggregatingMergeTree()
PARTITION BY (date, source_type)
ORDER BY (date, source_type, event_type);

CREATE MATERIALIZED VIEW web_daily_metrics_mv TO daily_source_metrics AS
SELECT
    toDate(event_time) AS date,
    'web' AS source_type,
    event_type,
    count() AS event_count,
    uniqState(user_id) AS unique_users
FROM web_events
GROUP BY date, source_type, event_type;

CREATE MATERIALIZED VIEW app_daily_metrics_mv TO daily_source_metrics AS
SELECT
    toDate(event_time) AS date,
    'app' AS source_type,
    event_type,
    count() AS event_count,
    uniqState(user_id) AS unique_users
FROM app_events
GROUP BY date, source_type, event_type;

CREATE MATERIALIZED VIEW offline_daily_metrics_mv TO daily_source_metrics AS
SELECT
    toDate(event_time) AS date,
    'offline' AS source_type,
    event_type,
    count() AS event_count,
    uniqState(user_id) AS unique_users
FROM offline_events
GROUP BY date, source_type, event_type;

-- ================================
-- 2. 复杂JOIN操作示例
-- ================================

-- 2.1 基础表结构
CREATE TABLE customers (
    customer_id UInt64,
    name String,
    email String,
    country String,
    registration_date Date,
    segment String
) ENGINE = MergeTree()
ORDER BY customer_id;

CREATE TABLE products (
    product_id UInt64,
    name String,
    category String,
    brand String,
    price Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY product_id;

CREATE TABLE orders (
    order_id UInt64,
    customer_id UInt64,
    order_date Date,
    order_time DateTime,
    status String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_date, customer_id);

CREATE TABLE order_items (
    item_id UInt64,
    order_id UInt64,
    product_id UInt64,
    quantity UInt32,
    unit_price Decimal(10, 2),
    total_price Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY order_id;

-- 2.2 多表JOIN物化视图
CREATE TABLE order_fact (
    order_id UInt64,
    order_date Date,
    order_time DateTime,
    customer_id UInt64,
    customer_name String,
    customer_segment String,
    customer_country String,
    product_id UInt64,
    product_name String,
    product_category String,
    product_brand String,
    quantity UInt32,
    unit_price Decimal(10, 2),
    total_price Decimal(10, 2),
    order_status String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_date, customer_id, product_id);

CREATE MATERIALIZED VIEW order_fact_mv TO order_fact AS
SELECT 
    o.order_id,
    o.order_date,
    o.order_time,
    o.customer_id,
    c.name AS customer_name,
    c.segment AS customer_segment,
    c.country AS customer_country,
    oi.product_id,
    p.name AS product_name,
    p.category AS product_category,
    p.brand AS product_brand,
    oi.quantity,
    oi.unit_price,
    oi.total_price,
    o.status AS order_status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- 2.3 聚合JOIN物化视图
CREATE TABLE daily_sales_by_customer_category (
    date Date,
    customer_segment String,
    product_category String,
    total_quantity UInt32,
    total_revenue Decimal(15, 2),
    order_count UInt32,
    unique_customers AggregateFunction(uniq, UInt64)
) ENGINE = AggregatingMergeTree()
PARTITION BY (date, customer_segment)
ORDER BY (date, customer_segment, product_category);

CREATE MATERIALIZED VIEW daily_sales_category_mv TO daily_sales_by_customer_category AS
SELECT 
    order_date AS date,
    customer_segment,
    product_category,
    sum(quantity) AS total_quantity,
    sum(total_price) AS total_revenue,
    count(DISTINCT order_id) AS order_count,
    uniqState(customer_id) AS unique_customers
FROM order_fact
WHERE order_status IN ('completed', 'shipped')
GROUP BY date, customer_segment, product_category;

-- 2.4 时间序列JOIN物化视图
CREATE TABLE product_daily_metrics (
    date Date,
    product_id UInt64,
    product_name String,
    product_category String,
    total_sales UInt32,
    total_revenue Decimal(15, 2),
    view_count UInt32,
    conversion_rate Float64
) ENGINE = AggregatingMergeTree()
PARTITION BY (date, product_category)
ORDER BY (date, product_id);

-- 创建产品浏览表
CREATE TABLE product_views (
    view_id UUID,
    product_id UInt64,
    user_id UInt64,
    view_time DateTime
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(view_time)
ORDER BY (product_id, view_time);

CREATE MATERIALIZED VIEW product_daily_metrics_mv TO product_daily_metrics AS
WITH sales_data AS (
    SELECT 
        order_date AS date,
        product_id,
        sum(quantity) AS total_sales,
        sum(total_price) AS total_revenue
    FROM order_fact
    WHERE order_status IN ('completed', 'shipped')
    GROUP BY date, product_id
),
view_data AS (
    SELECT 
        toDate(view_time) AS date,
        product_id,
        count() AS view_count
    FROM product_views
    GROUP BY date, product_id
)
SELECT 
    s.date,
    s.product_id,
    p.name AS product_name,
    p.category AS product_category,
    s.total_sales,
    s.total_revenue,
    v.view_count,
    s.total_sales * 100.0 / v.view_count AS conversion_rate
FROM sales_data s
JOIN view_data v ON s.date = v.date AND s.product_id = v.product_id
JOIN products p ON s.product_id = p.product_id
WHERE v.view_count > 0;

-- ================================
-- 3. 复杂查询优化示例
-- ================================

-- 3.1 分层物化视图
-- 第1层：原始数据层（events, customers, products等）

-- 第2层：基础聚合层
CREATE TABLE user_daily_activity (
    user_id UInt64,
    date Date,
    page_views UInt32,
    session_duration UInt32,
    unique_pages UInt32
) ENGINE = ReplacingMergeTree(date)
PARTITION BY (toYYYYMM(date), user_id % 100)
ORDER BY (user_id, date);

CREATE MATERIALIZED VIEW user_daily_activity_mv TO user_daily_activity AS
SELECT 
    user_id,
    toDate(event_time) AS date,
    countIf(event_type = 'page_view') AS page_views,
    sumIf(session_duration, session_duration > 0) AS session_duration,
    uniqExact(page_url) AS unique_pages
FROM unified_events
WHERE source_type = 'web'
GROUP BY user_id, date;

-- 第3层：业务指标层
CREATE TABLE user_segment_daily_metrics (
    date Date,
    user_segment String,
    active_users UInt32,
    total_page_views UInt32,
    avg_session_duration UInt32
) ENGINE = ReplacingMergeTree(date, user_segment)
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_segment);

-- 创建用户信息表
CREATE TABLE user_info (
    user_id UInt64,
    segment String,
    registration_date Date
) ENGINE = MergeTree()
ORDER BY user_id;

CREATE MATERIALIZED VIEW user_segment_daily_metrics_mv TO user_segment_daily_metrics AS
SELECT 
    a.date,
    u.segment AS user_segment,
    count() AS active_users,
    sum(page_views) AS total_page_views,
    avg(session_duration) AS avg_session_duration
FROM user_daily_activity a
JOIN user_info u ON a.user_id = u.user_id
GROUP BY date, user_segment;

-- 3.2 条件物化视图
-- 根据不同用户价值创建不同的物化视图
CREATE TABLE premium_user_events (
    event_id UUID,
    user_id UInt64,
    event_time DateTime,
    event_type String,
    properties String,
    customer_value UInt8
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type);

CREATE TABLE regular_user_events (
    event_id UUID,
    user_id UInt64,
    event_time DateTime,
    event_type String,
    properties String,
    customer_value UInt8
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type);

CREATE MATERIALIZED VIEW premium_events_mv TO premium_user_events AS
SELECT 
    event_id,
    user_id,
    event_time,
    event_type,
    properties,
    2 AS customer_value
FROM unified_events
WHERE user_id IN (
    SELECT user_id FROM user_info WHERE segment IN ('premium', 'vip')
);

CREATE MATERIALIZED VIEW regular_events_mv TO regular_user_events AS
SELECT 
    event_id,
    user_id,
    event_time,
    event_type,
    properties,
    1 AS customer_value
FROM unified_events
WHERE user_id IN (
    SELECT user_id FROM user_info WHERE segment IN ('free', 'basic')
);

-- 3.3 时间窗口物化视图
-- 实时指标（5分钟窗口）
CREATE TABLE real_time_metrics (
    window_start DateTime,
    window_end DateTime,
    metric_type String,
    source_type String,
    value UInt64,
    unique_users UInt64
) ENGINE = SummingMergeTree(value, unique_users)
ORDER BY (window_start, metric_type, source_type);

CREATE MATERIALIZED VIEW real_time_metrics_mv TO real_time_metrics AS
SELECT 
    toStartOfFiveMinutes(event_time) AS window_start,
    toStartOfFiveMinutes(event_time) + INTERVAL 5 MINUTE AS window_end,
    event_type AS metric_type,
    source_type,
    count() AS value,
    uniqExact(user_id) AS unique_users
FROM unified_events
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY window_start, metric_type, source_type;

-- 小时级指标
CREATE TABLE hourly_metrics (
    hour DateTime,
    metric_type String,
    source_type String,
    value UInt64,
    unique_users UInt64
) ENGINE = SummingMergeTree(value, unique_users)
ORDER BY (hour, metric_type, source_type);

CREATE MATERIALIZED VIEW hourly_metrics_mv TO hourly_metrics AS
SELECT 
    toStartOfHour(event_time) AS hour,
    event_type AS metric_type,
    source_type,
    count() AS value,
    uniqExact(user_id) AS unique_users
FROM unified_events
GROUP BY hour, metric_type, source_type;

-- ================================
-- 4. 故障排除示例
-- ================================

-- 4.1 数据一致性检查
-- 检查物化视图与源表的数据一致性
WITH source_data AS (
    SELECT 
        toDate(event_time) AS date,
        source_type,
        count() AS source_count
    FROM web_events
    WHERE event_time >= today() - INTERVAL 1 DAY
    GROUP BY date, source_type
),
view_data AS (
    SELECT 
        date,
        source_type,
        sum(value) AS view_count
    FROM daily_source_metrics
    WHERE date >= today() - INTERVAL 1 DAY
  AND source_type = 'web'
    GROUP BY date, source_type
)
SELECT 
    COALESCE(s.date, v.date) AS date,
    COALESCE(s.source_type, v.source_type) AS source_type,
    s.source_count,
    v.view_count,
    s.source_count - v.view_count AS diff
FROM source_data s
FULL OUTER JOIN view_data v ON s.date = v.date AND s.source_type = v.source_type
WHERE s.source_count != v.view_count OR v.view_count IS NULL OR s.source_count IS NULL
ORDER BY date;

-- 4.2 性能监控查询
-- 监控物化视图的执行性能
SELECT 
    query_id,
    query_duration_ms,
    read_rows,
    read_bytes,
    written_rows,
    memory_usage,
    substring(query, 1, 50) AS query_preview
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query LIKE '%MATERIALIZED%'
ORDER BY query_duration_ms DESC
LIMIT 10;

-- 4.3 物化视图状态查询
-- 查看物化视图的基本信息
SELECT 
    database,
    name AS view_name,
    create_table_query,
    as_select_query,
    target_database,
    target_table,
    is_populate
FROM system.tables
WHERE engine = 'MaterializedView'
ORDER BY database, name;

-- 4.4 重建物化视图示例
-- 重建物化视图以解决数据不一致问题

-- 1. 删除物化视图
DROP VIEW IF EXISTS complex_mv_name;

-- 2. 手动填充目标表
INSERT INTO target_table_name 
SELECT ... FROM source_table_name WHERE conditions;

-- 3. 重新创建物化视图
CREATE MATERIALIZED VIEW complex_mv_name TO target_table_name AS 
SELECT ... FROM source_table_name WHERE conditions;

-- ================================
-- 5. 实际应用案例
-- ================================

-- 5.1 用户行为漏斗分析
CREATE TABLE user_funnel (
    date Date,
    step_num UInt8,
    step_name String,
    total_users UInt32,
    conversion_rate Float64
) ENGINE = ReplacingMergeTree(date, step_num)
PARTITION BY (toYYYYMM(date))
ORDER BY (date, step_num);

CREATE MATERIALIZED VIEW user_funnel_mv TO user_funnel AS
WITH user_steps AS (
    SELECT 
        user_id,
        toDate(event_time) AS date,
        row_number() OVER (PARTITION BY user_id, toDate(event_time) ORDER BY event_time) AS step_num,
        event_type AS step_name
    FROM (
        SELECT DISTINCT 
            user_id, 
            toDate(event_time) AS date, 
            event_type
        FROM unified_events
        WHERE event_type IN ('visit', 'search', 'add_to_cart', 'checkout', 'purchase')
    )
)
SELECT 
    date,
    step_num,
    step_name,
    count() AS total_users,
    count() * 100.0 / lag(count(), 1, count()) OVER (PARTITION BY date ORDER BY step_num) AS conversion_rate
FROM user_steps
GROUP BY date, step_num, step_name
ORDER BY date, step_num;

-- 5.2 用户留存分析
CREATE TABLE user_retention (
    cohort_date Date,
    activity_date Date,
    day_number UInt16,
    cohort_size UInt32,
    active_users UInt32,
    retention_rate Float64
) ENGINE = ReplacingMergeTree(cohort_date, activity_date, day_number)
PARTITION BY (toYYYYMM(cohort_date))
ORDER BY (cohort_date, activity_date, day_number);

CREATE MATERIALIZED VIEW user_retention_mv TO user_retention AS
WITH user_activity AS (
    SELECT 
        user_id,
        toDate(min(event_time)) AS cohort_date,
        toDate(event_time) AS activity_date,
        dateDiff('day', min(event_time), event_time) AS day_number
    FROM unified_events
    GROUP BY user_id, toDate(event_time)
),
cohort_sizes AS (
    SELECT 
        cohort_date,
        count() AS cohort_size
    FROM (
        SELECT user_id, toDate(min(event_time)) AS cohort_date
        FROM unified_events
        GROUP BY user_id
    )
    GROUP BY cohort_date
)
SELECT 
    ua.cohort_date,
    ua.activity_date,
    ua.day_number,
    cs.cohort_size,
    count() AS active_users,
    count() * 100.0 / cs.cohort_size AS retention_rate
FROM user_activity ua
JOIN cohort_sizes cs ON ua.cohort_date = cs.cohort_date
WHERE ua.day_number BETWEEN 0 AND 30
GROUP BY ua.cohort_date, ua.activity_date, ua.day_number, cs.cohort_size
ORDER BY ua.cohort_date, ua.activity_date;

-- 5.3 销售趋势分析
CREATE TABLE sales_trends (
    date Date,
    period_type String,
    period_value String,
    region String,
    product_category String,
    total_revenue Decimal(15, 2),
    order_count UInt32,
    unique_customers UInt32,
    avg_order_value Decimal(10, 2),
    growth_rate Float64
) ENGINE = ReplacingMergeTree(date, period_type, period_value)
PARTITION BY toYYYYMM(date)
ORDER BY (date, period_type, period_value);

CREATE MATERIALIZED VIEW sales_trends_mv TO sales_trends AS
WITH weekly_data AS (
    SELECT 
        toStartOfWeek(order_date) AS week_start,
        toYYYYMMDD(order_date) AS date,
        customer_country AS region,
        product_category,
        sum(total_price) AS total_revenue,
        count(DISTINCT order_id) AS order_count,
        uniqExact(customer_id) AS unique_customers,
        avg(total_price) AS avg_order_value
    FROM order_fact
    WHERE order_status IN ('completed', 'shipped')
    GROUP BY week_start, date, region, product_category
),
growth_data AS (
    SELECT 
        date,
        region,
        product_category,
        total_revenue,
        lag(total_revenue, 7) OVER (PARTITION BY region, product_category ORDER BY date) AS prev_week_revenue
    FROM weekly_data
)
SELECT 
    date,
    'weekly' AS period_type,
    toYYYYMMDD(toStartOfWeek(date)) AS period_value,
    region,
    product_category,
    total_revenue,
    order_count,
    unique_customers,
    avg_order_value,
    CASE 
        WHEN prev_week_revenue > 0 THEN (total_revenue - prev_week_revenue) / prev_week_revenue * 100
        ELSE 0 
    END AS growth_rate
FROM growth_data
ORDER BY date, region, product_category;

-- ================================
-- 6. 清理示例
-- ================================

-- 删除创建的示例表（可选）
/*
DROP TABLE IF EXISTS unified_events;
DROP TABLE IF EXISTS filtered_events;
DROP TABLE IF EXISTS daily_source_metrics;
DROP TABLE IF EXISTS order_fact;
DROP TABLE IF EXISTS daily_sales_by_customer_category;
DROP TABLE IF EXISTS product_daily_metrics;
DROP TABLE IF EXISTS user_daily_activity;
DROP TABLE IF EXISTS user_segment_daily_metrics;
DROP TABLE IF EXISTS premium_user_events;
DROP TABLE IF EXISTS regular_user_events;
DROP TABLE IF EXISTS real_time_metrics;
DROP TABLE IF EXISTS hourly_metrics;
DROP TABLE IF EXISTS user_funnel;
DROP TABLE IF EXISTS user_retention;
DROP TABLE IF EXISTS sales_trends;
DROP TABLE IF EXISTS web_events;
DROP TABLE IF EXISTS app_events;
DROP TABLE IF EXISTS offline_events;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS product_views;
DROP TABLE IF EXISTS user_info;
*/