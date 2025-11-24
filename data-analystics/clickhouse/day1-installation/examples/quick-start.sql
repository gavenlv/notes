-- ClickHouse 快速开始示例
-- 5分钟体验ClickHouse的核心功能

-- ==============================================
-- Step 1: 验证连接和查看系统信息
-- ==============================================

-- 基础连接测试
SELECT 'Hello ClickHouse!' as greeting;

-- 查看版本和系统信息
SELECT version() as version, now() as current_time, timezone() as timezone;

-- 查看系统资源
SELECT 
    formatReadableSize(total_bytes) as used_space,
    formatReadableQuantity(total_rows) as total_rows
FROM system.parts;

-- ==============================================
-- Step 2: 创建你的第一个数据库和表
-- ==============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS quickstart;

-- 使用数据库
USE quickstart;

-- 创建网站访问日志表
CREATE TABLE website_visits (
    visit_time DateTime,
    user_id UInt32,
    page_path String,
    referrer String,
    user_agent String,
    country String,
    device_type Enum8('desktop' = 1, 'mobile' = 2, 'tablet' = 3),
    session_duration UInt32,
    page_views UInt16,
    is_bounce Boolean
) ENGINE = MergeTree()
ORDER BY (visit_time, user_id);

-- ==============================================
-- Step 3: 插入示例数据
-- ==============================================

-- 插入一些示例访问记录
INSERT INTO website_visits VALUES
    ('2024-01-15 10:00:00', 1001, '/home', 'https://google.com', 'Mozilla/5.0 Chrome', 'China', 'desktop', 120, 3, false),
    ('2024-01-15 10:05:00', 1002, '/products', 'https://facebook.com', 'Mozilla/5.0 Safari', 'USA', 'mobile', 45, 1, true),
    ('2024-01-15 10:10:00', 1003, '/about', '', 'Mozilla/5.0 Firefox', 'Germany', 'desktop', 200, 5, false),
    ('2024-01-15 10:15:00', 1001, '/contact', '/home', 'Mozilla/5.0 Chrome', 'China', 'desktop', 180, 4, false),
    ('2024-01-15 10:20:00', 1004, '/home', 'https://twitter.com', 'Edge/91.0', 'Japan', 'tablet', 90, 2, false);

-- 使用生成函数插入更多测试数据
INSERT INTO website_visits
SELECT 
    now() - number * 60 as visit_time,
    number % 1000 + 1 as user_id,
    ['/home', '/products', '/about', '/contact', '/blog', '/pricing'][number % 6 + 1] as page_path,
    if(number % 3 = 0, '', ['https://google.com', 'https://facebook.com', 'https://twitter.com'][number % 3 + 1]) as referrer,
    ['Mozilla/5.0 Chrome', 'Mozilla/5.0 Safari', 'Mozilla/5.0 Firefox', 'Edge/91.0'][number % 4 + 1] as user_agent,
    ['China', 'USA', 'Germany', 'Japan', 'UK', 'France'][number % 6 + 1] as country,
    ['desktop', 'mobile', 'tablet'][number % 3 + 1] as device_type,
    30 + number % 300 as session_duration,
    1 + number % 10 as page_views,
    number % 5 = 0 as is_bounce
FROM numbers(1000);

-- ==============================================
-- Step 4: 体验ClickHouse的查询威力
-- ==============================================

-- 查看数据概况
SELECT 
    COUNT(*) as total_visits,
    COUNT(DISTINCT user_id) as unique_visitors,
    MIN(visit_time) as first_visit,
    MAX(visit_time) as last_visit
FROM website_visits;

-- 最受欢迎的页面
SELECT 
    page_path,
    COUNT(*) as visits,
    COUNT(DISTINCT user_id) as unique_visitors,
    ROUND(AVG(session_duration), 2) as avg_duration,
    ROUND(AVG(page_views), 2) as avg_page_views,
    ROUND(SUM(is_bounce) * 100.0 / COUNT(*), 2) as bounce_rate
FROM website_visits 
GROUP BY page_path 
ORDER BY visits DESC;

-- 设备类型分析
SELECT 
    device_type,
    COUNT(*) as visits,
    COUNT(DISTINCT user_id) as unique_users,
    ROUND(AVG(session_duration), 2) as avg_duration,
    ROUND(SUM(is_bounce) * 100.0 / COUNT(*), 2) as bounce_rate
FROM website_visits 
GROUP BY device_type 
ORDER BY visits DESC;

-- 国家/地区分析
SELECT 
    country,
    COUNT(*) as visits,
    COUNT(DISTINCT user_id) as unique_visitors,
    ROUND(AVG(session_duration), 2) as avg_duration
FROM website_visits 
GROUP BY country 
ORDER BY visits DESC 
LIMIT 10;

-- 流量来源分析
SELECT 
    CASE 
        WHEN referrer = '' THEN 'Direct'
        WHEN referrer LIKE '%google%' THEN 'Google'
        WHEN referrer LIKE '%facebook%' THEN 'Facebook'
        WHEN referrer LIKE '%twitter%' THEN 'Twitter'
        ELSE 'Other'
    END as traffic_source,
    COUNT(*) as visits,
    COUNT(DISTINCT user_id) as unique_visitors,
    ROUND(AVG(session_duration), 2) as avg_duration,
    ROUND(SUM(is_bounce) * 100.0 / COUNT(*), 2) as bounce_rate
FROM website_visits 
GROUP BY traffic_source 
ORDER BY visits DESC;

-- ==============================================
-- Step 5: 时间序列分析
-- ==============================================

-- 每小时访问量趋势
SELECT 
    toStartOfHour(visit_time) as hour,
    COUNT(*) as visits,
    COUNT(DISTINCT user_id) as unique_visitors,
    ROUND(AVG(session_duration), 2) as avg_duration
FROM website_visits 
WHERE visit_time >= now() - INTERVAL 24 HOUR
GROUP BY hour 
ORDER BY hour;

-- 每天访问量（如果有多天数据）
SELECT 
    toDate(visit_time) as date,
    COUNT(*) as visits,
    COUNT(DISTINCT user_id) as unique_visitors,
    ROUND(AVG(session_duration), 2) as avg_duration
FROM website_visits 
GROUP BY date 
ORDER BY date;

-- ==============================================
-- Step 6: 高级分析示例
-- ==============================================

-- 用户行为分析 - 找出最活跃的用户
SELECT 
    user_id,
    COUNT(*) as total_visits,
    SUM(page_views) as total_page_views,
    SUM(session_duration) as total_time_spent,
    ROUND(AVG(session_duration), 2) as avg_session_duration,
    countIf(is_bounce) as bounced_sessions,
    ROUND(countIf(is_bounce) * 100.0 / COUNT(*), 2) as bounce_rate
FROM website_visits 
GROUP BY user_id 
HAVING total_visits > 3
ORDER BY total_visits DESC, total_time_spent DESC
LIMIT 10;

-- 页面漏斗分析
WITH page_funnel AS (
    SELECT 
        user_id,
        hasAny(arrayMap(x -> x = '/home', groupArray(page_path))) as visited_home,
        hasAny(arrayMap(x -> x = '/products', groupArray(page_path))) as visited_products,
        hasAny(arrayMap(x -> x = '/contact', groupArray(page_path))) as visited_contact
    FROM website_visits 
    GROUP BY user_id
)
SELECT 
    countIf(visited_home) as step1_home,
    countIf(visited_home AND visited_products) as step2_products,
    countIf(visited_home AND visited_products AND visited_contact) as step3_contact,
    ROUND(countIf(visited_home AND visited_products) * 100.0 / countIf(visited_home), 2) as conversion_home_to_products,
    ROUND(countIf(visited_home AND visited_products AND visited_contact) * 100.0 / countIf(visited_home AND visited_products), 2) as conversion_products_to_contact
FROM page_funnel;

-- ==============================================
-- Step 7: 窗口函数示例
-- ==============================================

-- 用户访问序列分析
SELECT 
    user_id,
    visit_time,
    page_path,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY visit_time) as visit_sequence,
    LAG(page_path) OVER (PARTITION BY user_id ORDER BY visit_time) as previous_page,
    session_duration,
    SUM(session_duration) OVER (PARTITION BY user_id ORDER BY visit_time) as cumulative_time
FROM website_visits 
WHERE user_id IN (1001, 1002, 1003)
ORDER BY user_id, visit_time;

-- ==============================================
-- Step 8: ClickHouse特有功能展示
-- ==============================================

-- 数组操作示例
SELECT 
    user_id,
    groupArray(page_path) as visited_pages,
    arrayStringConcat(groupArray(page_path), ' -> ') as user_journey,
    length(groupArray(page_path)) as total_pages_visited,
    arrayUniq(groupArray(page_path)) as unique_pages_visited
FROM website_visits 
GROUP BY user_id 
HAVING total_pages_visited > 2
ORDER BY total_pages_visited DESC
LIMIT 10;

-- 近似计算（用于大数据集）
SELECT 
    country,
    uniq(user_id) as exact_unique_users,
    uniqHLL12(user_id) as approx_unique_users,
    ABS(uniq(user_id) - uniqHLL12(user_id)) as difference
FROM website_visits 
GROUP BY country 
ORDER BY exact_unique_users DESC;

-- ==============================================
-- Step 9: 系统表查询
-- ==============================================

-- 查看表的详细信息
SELECT 
    database,
    table,
    formatReadableSize(total_bytes) as size,
    total_rows,
    total_parts,
    engine
FROM system.parts 
WHERE database = 'quickstart';

-- 查看最近的查询性能
SELECT 
    type,
    query_duration_ms,
    memory_usage,
    read_rows,
    result_rows,
    query
FROM system.query_log 
WHERE event_time >= now() - INTERVAL 10 MINUTE
  AND type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 5;

-- ==============================================
-- Step 10: 清理（可选）
-- ==============================================

-- 如果需要清理数据，取消注释以下命令
-- DROP TABLE website_visits;
-- DROP DATABASE quickstart;

-- ==============================================
-- 🎉 恭喜！你已经完成了ClickHouse快速开始教程
-- ==============================================

SELECT 
    '🎉 恭喜！' as message,
    '你已经学会了ClickHouse的基础操作!' as achievement,
    '继续学习 notes/week1/day3-basic-sql.md' as next_step; 