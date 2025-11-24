-- ClickHouse 基础查询示例
-- 适用于 Day 1-2 的学习

-- ==============================================
-- 1. 系统查询 - 了解ClickHouse环境
-- ==============================================

-- 查看版本信息
SELECT version();

-- 查看当前时间
SELECT now();

-- 查看时区
SELECT timezone();

-- 查看可用数据库
SHOW DATABASES;

-- 查看系统表
SELECT database, name, engine 
FROM system.tables 
WHERE database = 'system' 
LIMIT 10;

-- ==============================================
-- 2. 数据库和表操作
-- ==============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS tutorial;

-- 切换到数据库
USE tutorial;

-- 创建第一个表 - 用户事件表
CREATE TABLE user_events (
    event_time DateTime,
    user_id UInt32,
    event_type String,
    page_url String,
    user_agent String,
    ip String,
    created_date Date DEFAULT toDate(event_time)
) ENGINE = MergeTree()
ORDER BY (created_date, user_id, event_time);

-- 查看表结构
DESCRIBE user_events;

-- 查看表的创建语句
SHOW CREATE TABLE user_events;

-- ==============================================
-- 3. 插入数据
-- ==============================================

-- 插入单条数据
INSERT INTO user_events VALUES 
    ('2024-01-15 10:30:00', 1001, 'page_view', '/home', 'Mozilla/5.0', '192.168.1.100', '2024-01-15');

-- 插入多条数据
INSERT INTO user_events (event_time, user_id, event_type, page_url, user_agent, ip) VALUES 
    ('2024-01-15 10:31:00', 1001, 'click', '/products', 'Mozilla/5.0', '192.168.1.100'),
    ('2024-01-15 10:32:00', 1002, 'page_view', '/home', 'Chrome/91.0', '192.168.1.101'),
    ('2024-01-15 10:33:00', 1003, 'login', '/login', 'Safari/14.0', '192.168.1.102'),
    ('2024-01-15 10:34:00', 1001, 'purchase', '/checkout', 'Mozilla/5.0', '192.168.1.100');

-- 使用生成函数插入大量测试数据
INSERT INTO user_events (event_time, user_id, event_type, page_url, user_agent, ip)
SELECT 
    now() - number * 60 as event_time,  -- 每条记录间隔1分钟
    number % 1000 + 1 as user_id,       -- 用户ID 1-1000
    ['page_view', 'click', 'login', 'logout', 'purchase'][number % 5 + 1] as event_type,
    ['/home', '/products', '/about', '/contact', '/checkout'][number % 5 + 1] as page_url,
    ['Mozilla/5.0', 'Chrome/91.0', 'Safari/14.0', 'Edge/91.0'][number % 4 + 1] as user_agent,
    '192.168.1.' || toString(number % 255 + 1) as ip
FROM numbers(10000);  -- 生成10000条记录

-- ==============================================
-- 4. 基础查询
-- ==============================================

-- 查看总记录数
SELECT COUNT(*) FROM user_events;

-- 查看最新的10条记录
SELECT * FROM user_events 
ORDER BY event_time DESC 
LIMIT 10;

-- 按事件类型统计
SELECT 
    event_type,
    COUNT(*) as count
FROM user_events 
GROUP BY event_type 
ORDER BY count DESC;

-- 按日期统计
SELECT 
    created_date,
    COUNT(*) as daily_events
FROM user_events 
GROUP BY created_date 
ORDER BY created_date;

-- 最活跃的用户
SELECT 
    user_id,
    COUNT(*) as event_count
FROM user_events 
GROUP BY user_id 
ORDER BY event_count DESC 
LIMIT 10;

-- ==============================================
-- 5. 时间相关查询
-- ==============================================

-- 按小时统计事件
SELECT 
    toStartOfHour(event_time) as hour,
    COUNT(*) as events_per_hour
FROM user_events 
WHERE event_time >= now() - INTERVAL 24 HOUR
GROUP BY hour 
ORDER BY hour;

-- 查看最近1小时的事件
SELECT 
    event_time,
    user_id,
    event_type,
    page_url
FROM user_events 
WHERE event_time >= now() - INTERVAL 1 HOUR
ORDER BY event_time DESC;

-- ==============================================
-- 6. 聚合函数示例
-- ==============================================

-- 基本聚合
SELECT 
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    MIN(event_time) as first_event,
    MAX(event_time) as last_event
FROM user_events;

-- 条件聚合
SELECT 
    event_type,
    COUNT(*) as total,
    COUNT(DISTINCT user_id) as unique_users,
    MIN(event_time) as first_time,
    MAX(event_time) as last_time
FROM user_events 
GROUP BY event_type;

-- ==============================================
-- 7. 字符串函数示例
-- ==============================================

-- 提取域名信息
SELECT 
    user_agent,
    -- 提取浏览器信息
    CASE 
        WHEN user_agent LIKE '%Chrome%' THEN 'Chrome'
        WHEN user_agent LIKE '%Firefox%' THEN 'Firefox'
        WHEN user_agent LIKE '%Safari%' THEN 'Safari'
        WHEN user_agent LIKE '%Edge%' THEN 'Edge'
        ELSE 'Other'
    END as browser,
    COUNT(*) as count
FROM user_events 
GROUP BY user_agent, browser
ORDER BY count DESC;

-- 字符串操作
SELECT 
    page_url,
    length(page_url) as url_length,
    upper(page_url) as upper_url,
    lower(page_url) as lower_url
FROM user_events 
WHERE page_url != ''
LIMIT 5;

-- ==============================================
-- 8. 数组和高级数据类型
-- ==============================================

-- 创建包含数组的表
CREATE TABLE user_tags (
    user_id UInt32,
    tags Array(String),
    preferences Map(String, String),
    metadata JSON
) ENGINE = MergeTree()
ORDER BY user_id;

-- 插入包含数组的数据
INSERT INTO user_tags VALUES 
    (1001, ['tech', 'gaming', 'music'], map('theme', 'dark', 'language', 'en'), '{"age": 25, "location": "Beijing"}'),
    (1002, ['sports', 'travel'], map('theme', 'light', 'language', 'zh'), '{"age": 30, "location": "Shanghai"}'),
    (1003, ['food', 'cooking', 'travel'], map('theme', 'auto', 'language', 'en'), '{"age": 28, "location": "Guangzhou"}');

-- 查询数组数据
SELECT 
    user_id,
    tags,
    arrayStringConcat(tags, ', ') as tags_str,
    length(tags) as tag_count,
    has(tags, 'tech') as has_tech_tag
FROM user_tags;

-- 数组展开
SELECT 
    user_id,
    tag
FROM user_tags
ARRAY JOIN tags as tag;

-- ==============================================
-- 9. 子查询和WITH子句
-- ==============================================

-- 使用WITH子句
WITH active_users AS (
    SELECT user_id, COUNT(*) as event_count
    FROM user_events 
    WHERE event_time >= now() - INTERVAL 24 HOUR
    GROUP BY user_id
    HAVING event_count > 5
)
SELECT 
    au.user_id,
    au.event_count,
    ue.event_type,
    COUNT(*) as type_count
FROM active_users au
JOIN user_events ue ON au.user_id = ue.user_id
WHERE ue.event_time >= now() - INTERVAL 24 HOUR
GROUP BY au.user_id, au.event_count, ue.event_type
ORDER BY au.event_count DESC, type_count DESC;

-- 子查询示例
SELECT 
    event_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM user_events), 2) as percentage
FROM user_events 
GROUP BY event_type
ORDER BY count DESC;

-- ==============================================
-- 10. 系统监控查询
-- ==============================================

-- 查看当前查询
SELECT 
    query_id,
    user,
    query,
    elapsed,
    memory_usage
FROM system.processes 
WHERE query != '';

-- 查看表信息
SELECT 
    database,
    table,
    formatReadableSize(total_bytes) as size,
    total_rows,
    total_parts
FROM system.parts 
WHERE database = 'tutorial'
ORDER BY total_bytes DESC;

-- 查看最近的查询日志
SELECT 
    type,
    event_time,
    query,
    exception,
    memory_usage,
    query_duration_ms
FROM system.query_log 
WHERE event_time >= now() - INTERVAL 1 HOUR
ORDER BY event_time DESC
LIMIT 10;

-- ==============================================
-- 11. 清理操作
-- ==============================================

-- 删除特定数据 (注意：ClickHouse的DELETE操作是异步的)
-- ALTER TABLE user_events DELETE WHERE user_id = 1001;

-- 删除表
-- DROP TABLE user_tags;

-- 删除数据库
-- DROP DATABASE tutorial;

-- ==============================================
-- 练习题
-- ==============================================

-- 1. 查询每个用户的第一次和最后一次访问时间
-- 2. 统计每个页面的访问次数和独立访客数
-- 3. 找出连续访问时间超过10分钟的用户会话
-- 4. 计算每小时的转化率 (purchase事件占比)
-- 5. 分析用户行为路径 (从page_view到purchase的路径)

-- 提示：这些练习题的答案在 code/examples/advanced-queries.sql 中 