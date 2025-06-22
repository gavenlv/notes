-- Day 7: ClickHouse 数据导入导出示例
-- ===============================================

-- 1. 基础表结构创建
-- ===============================================

-- 用户分析表
CREATE DATABASE IF NOT EXISTS analytics;
USE analytics;

DROP TABLE IF EXISTS user_analytics;
CREATE TABLE user_analytics (
    user_id UInt32,
    event_date Date,
    page_views UInt32,
    session_duration UInt32,
    country String,
    device_type String,
    revenue Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (user_id, event_date)
PARTITION BY toYYYYMM(event_date);

-- 2. CSV格式数据导入演示
-- ===============================================

-- 直接INSERT CSV数据
INSERT INTO user_analytics FORMAT CSV
1001,"2024-01-01",25,1800,"China","mobile",99.99
1002,"2024-01-01",15,1200,"USA","desktop",149.99
1003,"2024-01-01",30,2100,"Japan","tablet",75.50
1004,"2024-01-01",18,900,"Germany","mobile",125.00
1005,"2024-01-01",22,1650,"UK","desktop",89.99

-- 验证导入数据
SELECT 'CSV导入验证' as test_type, count() as row_count FROM user_analytics;
SELECT * FROM user_analytics ORDER BY user_id LIMIT 5;

-- 3. JSON格式数据导入演示
-- ===============================================

-- JSONEachRow格式导入
INSERT INTO user_analytics FORMAT JSONEachRow
{"user_id": 2001, "event_date": "2024-01-02", "page_views": 28, "session_duration": 1950, "country": "China", "device_type": "mobile", "revenue": 199.99}
{"user_id": 2002, "event_date": "2024-01-02", "page_views": 12, "session_duration": 850, "country": "USA", "device_type": "desktop", "revenue": 79.99}
{"user_id": 2003, "event_date": "2024-01-02", "page_views": 35, "session_duration": 2400, "country": "Japan", "device_type": "tablet", "revenue": 299.99}

-- 验证JSON导入
SELECT 'JSON导入验证' as test_type, count() as row_count FROM user_analytics WHERE event_date = '2024-01-02';

-- 4. 批量数据生成演示
-- ===============================================

-- 生成大量测试数据
INSERT INTO user_analytics 
SELECT 
    number % 10000 + 3000 as user_id,
    toDate('2024-01-03') + toIntervalDay(number % 30) as event_date,
    (number % 50) + 1 as page_views,
    (number % 3600) + 300 as session_duration,
    ['China', 'USA', 'Japan', 'Germany', 'UK', 'France', 'Canada', 'Australia'][number % 8 + 1] as country,
    ['mobile', 'desktop', 'tablet'][number % 3 + 1] as device_type,
    round((number % 500) * 0.99 + 10, 2) as revenue
FROM numbers(50000);

-- 数据统计
SELECT '批量数据统计' as test_type, count() as total_rows FROM user_analytics;
SELECT 
    country,
    device_type,
    count() as user_count,
    round(avg(revenue), 2) as avg_revenue,
    sum(revenue) as total_revenue
FROM user_analytics 
GROUP BY country, device_type
ORDER BY user_count DESC
LIMIT 10;

-- 5. 数据导出演示
-- ===============================================

-- 导出为不同格式（示例，实际需要文件路径）

-- CSV导出示例
SELECT 'CSV导出示例' as demo_type;
SELECT * FROM user_analytics 
WHERE country = 'China' AND event_date >= '2024-01-01'
ORDER BY user_id, event_date
LIMIT 10
FORMAT CSV;

-- JSON导出示例
SELECT 'JSON导出示例' as demo_type;
SELECT * FROM user_analytics 
WHERE device_type = 'mobile' AND revenue > 100
ORDER BY revenue DESC
LIMIT 5
FORMAT JSONEachRow;

-- TSV导出示例
SELECT 'TSV导出示例' as demo_type;
SELECT 
    country,
    device_type,
    count() as users,
    round(avg(revenue), 2) as avg_revenue
FROM user_analytics 
GROUP BY country, device_type
ORDER BY users DESC
LIMIT 10
FORMAT TSV;

-- 6. 数据聚合和分析演示
-- ===============================================

-- 创建聚合表
DROP TABLE IF EXISTS daily_summary;
CREATE TABLE daily_summary (
    event_date Date,
    country String,
    device_type String,
    total_users UInt32,
    total_page_views UInt32,
    avg_session_duration UInt32,
    total_revenue Decimal(12, 2)
) ENGINE = SummingMergeTree((total_users, total_page_views, avg_session_duration, total_revenue))
ORDER BY (event_date, country, device_type)
PARTITION BY toYYYYMM(event_date);

-- 数据聚合导入
INSERT INTO daily_summary
SELECT 
    event_date,
    country,
    device_type,
    count() as total_users,
    sum(page_views) as total_page_views,
    round(avg(session_duration)) as avg_session_duration,
    sum(revenue) as total_revenue
FROM user_analytics
GROUP BY event_date, country, device_type;

-- 查看聚合结果
SELECT 'Daily Summary' as report_type;
SELECT * FROM daily_summary 
ORDER BY event_date DESC, total_revenue DESC
LIMIT 15;

-- 7. 实时数据流模拟
-- ===============================================

-- 创建Buffer表模拟实时写入
DROP TABLE IF EXISTS analytics_buffer;
CREATE TABLE analytics_buffer AS user_analytics
ENGINE = Buffer(analytics, user_analytics, 16, 10, 100, 10000, 1000000, 10000000, 100000000);

-- 模拟实时数据写入
INSERT INTO analytics_buffer 
SELECT 
    number + 100000 as user_id,
    today() as event_date,
    (number % 20) + 5 as page_views,
    (number % 1800) + 600 as session_duration,
    ['China', 'USA', 'Japan'][number % 3 + 1] as country,
    ['mobile', 'desktop'][number % 2 + 1] as device_type,
    round((number % 200) + 50, 2) as revenue
FROM numbers(1000);

-- 实时数据监控
SELECT 'Real-time Buffer Stats' as stats_type;
SELECT 
    device_type,
    count() as event_count,
    uniq(user_id) as unique_users,
    round(avg(revenue), 2) as avg_revenue,
    sum(revenue) as total_revenue
FROM analytics_buffer 
WHERE event_date = today()
GROUP BY device_type;

-- 8. 数据质量检查演示
-- ===============================================

-- 数据质量报告
SELECT 'Data Quality Report' as report_type;
SELECT 
    count() as total_rows,
    count(DISTINCT user_id) as unique_users,
    count(DISTINCT event_date) as date_range,
    min(event_date) as min_date,
    max(event_date) as max_date,
    countIf(user_id <= 0) as invalid_user_ids,
    countIf(page_views <= 0) as invalid_page_views,
    countIf(revenue < 0) as negative_revenue,
    countIf(country = '') as empty_countries,
    round(avg(revenue), 2) as avg_revenue,
    round(avg(page_views), 2) as avg_page_views
FROM user_analytics;

-- 异常数据检测
SELECT 'Anomaly Detection' as analysis_type;
SELECT 
    country,
    device_type,
    count() as records,
    min(revenue) as min_revenue,
    max(revenue) as max_revenue,
    round(avg(revenue), 2) as avg_revenue,
    round(stddevPop(revenue), 2) as revenue_stddev
FROM user_analytics 
GROUP BY country, device_type
HAVING count() > 100
ORDER BY revenue_stddev DESC
LIMIT 10;

-- 9. 性能测试
-- ===============================================

-- 查询性能测试
SELECT 'Performance Test' as test_type, now() as start_time;

-- 大数据量聚合查询
SELECT 
    country,
    toYYYYMM(event_date) as year_month,
    count() as user_count,
    sum(page_views) as total_page_views,
    round(avg(session_duration), 0) as avg_session_duration,
    sum(revenue) as total_revenue
FROM user_analytics 
WHERE event_date >= '2024-01-01'
GROUP BY country, toYYYYMM(event_date)
ORDER BY total_revenue DESC;

-- 复杂分析查询
WITH user_segments AS (
    SELECT 
        user_id,
        sum(revenue) as total_spent,
        avg(page_views) as avg_page_views,
        CASE 
            WHEN sum(revenue) >= 500 THEN 'VIP'
            WHEN sum(revenue) >= 200 THEN 'Premium'
            WHEN sum(revenue) >= 50 THEN 'Regular'
            ELSE 'Basic'
        END as user_segment
    FROM user_analytics
    GROUP BY user_id
)
SELECT 
    user_segment,
    count() as user_count,
    round(avg(total_spent), 2) as avg_total_spent,
    round(avg(avg_page_views), 2) as avg_page_views_per_user
FROM user_segments
GROUP BY user_segment
ORDER BY avg_total_spent DESC;

-- 10. 清理和优化
-- ===============================================

-- 表优化
OPTIMIZE TABLE user_analytics FINAL;
OPTIMIZE TABLE daily_summary FINAL;

-- 查看表信息
SELECT 'Table Information' as info_type;
SELECT 
    table,
    sum(rows) as total_rows,
    formatReadableSize(sum(data_compressed_bytes)) as compressed_size,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed_size,
    round(sum(data_compressed_bytes) / sum(data_uncompressed_bytes), 3) as compression_ratio
FROM system.parts 
WHERE database = 'analytics'
  AND table IN ('user_analytics', 'daily_summary')
  AND active
GROUP BY table;

-- 最终统计
SELECT '=== Day 7 Demo Completed ===' as completion_status;
SELECT 
    'Total Records' as metric,
    count() as value
FROM user_analytics
UNION ALL
SELECT 
    'Date Range' as metric,
    toString(max(event_date) - min(event_date) + 1) as value
FROM user_analytics
UNION ALL
SELECT 
    'Countries' as metric,
    toString(count(DISTINCT country)) as value
FROM user_analytics
UNION ALL
SELECT 
    'Device Types' as metric,
    toString(count(DISTINCT device_type)) as value
FROM user_analytics
UNION ALL
SELECT 
    'Total Revenue' as metric,
    toString(round(sum(revenue), 2)) as value
FROM user_analytics;

-- 演示完成提示
SELECT 
    '🎉 Day 7 数据导入导出演示完成！' as message,
    '📊 已创建' || toString(count()) || '条测试记录' as summary
FROM user_analytics; 