-- Trino Iceberg 查询示例
-- 本示例演示如何在 Trino 中查询 Iceberg 表

-- 1. 创建 Iceberg Catalog
CREATE SCHEMA IF NOT EXISTS iceberg.tutorial;

-- 2. 创建示例表
CREATE TABLE IF NOT EXISTS iceberg.tutorial.web_events (
    event_id VARCHAR,
    user_id BIGINT,
    event_type VARCHAR,
    page_url VARCHAR,
    referrer VARCHAR,
    user_agent VARCHAR,
    ip_address VARCHAR,
    event_time TIMESTAMP(6),
    processing_time TIMESTAMP(6)
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['DATE(event_time)'],
    location = 'hdfs://namenode:9000/warehouse/tutorial/web_events'
);

-- 3. 插入示例数据
INSERT INTO iceberg.tutorial.web_events
VALUES
    ('evt001', 1001, 'page_view', 'https://example.com/home', 'https://google.com', 'Mozilla/5.0...', '192.168.1.1', TIMESTAMP '2023-06-01 10:00:00', CURRENT_TIMESTAMP),
    ('evt002', 1002, 'click', 'https://example.com/product/123', '', 'Mozilla/5.0...', '192.168.1.2', TIMESTAMP '2023-06-01 10:05:00', CURRENT_TIMESTAMP),
    ('evt003', 1001, 'purchase', 'https://example.com/checkout', 'https://example.com/cart', 'Mozilla/5.0...', '192.168.1.1', TIMESTAMP '2023-06-01 10:15:00', CURRENT_TIMESTAMP);

-- 4. 基础查询
-- 查询所有事件
SELECT * FROM iceberg.tutorial.web_events;

-- 按事件类型统计
SELECT event_type, COUNT(*) as event_count
FROM iceberg.tutorial.web_events
GROUP BY event_type;

-- 5. 时间旅行查询
-- 查询表在特定时间点的数据
SELECT * FROM iceberg.tutorial.web_events FOR TIMESTAMP AS OF TIMESTAMP '2023-06-01 11:00:00';

-- 6. 分区裁剪查询
-- 利用分区字段优化查询
SELECT *
FROM iceberg.tutorial.web_events
WHERE DATE(event_time) = DATE '2023-06-01';

-- 7. 谓词下推优化
-- 利用谓词下推减少数据扫描
SELECT user_id, event_type, event_time
FROM iceberg.tutorial.web_events
WHERE event_type = 'page_view' AND event_time >= TIMESTAMP '2023-06-01 09:00:00';

-- 8. 列裁剪优化
-- 只选择需要的列减少I/O
SELECT event_id, user_id, event_type
FROM iceberg.tutorial.web_events
WHERE event_time BETWEEN TIMESTAMP '2023-06-01 00:00:00' AND TIMESTAMP '2023-06-01 23:59:59';

-- 9. 复杂分析查询
-- 用户会话分析
WITH user_sessions AS (
    SELECT 
        user_id,
        event_time,
        LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) as prev_event_time
    FROM iceberg.tutorial.web_events
)
SELECT 
    user_id,
    COUNT(*) as total_events,
    COUNT(CASE WHEN prev_event_time IS NULL OR event_time - prev_event_time > INTERVAL '30' MINUTE THEN 1 END) as session_count
FROM user_sessions
GROUP BY user_id;

-- 10. 性能优化查询
-- 使用统计信息优化查询计划
ANALYZE iceberg.tutorial.web_events;

-- 查看表统计信息
SHOW STATS FOR iceberg.tutorial.web_events;

-- 11. 元数据查询
-- 查询表的分区信息
SELECT * FROM iceberg.tutorial.web_events.partitions;

-- 查询表的文件信息
SELECT 
    record_count,
    file_path,
    file_size_in_bytes
FROM iceberg.tutorial.web_events.files;

-- 12. Schema 演化示例
-- 添加新列
ALTER TABLE iceberg.tutorial.web_events ADD COLUMN session_id VARCHAR;

-- 修改列名
ALTER TABLE iceberg.tutorial.web_events RENAME COLUMN ip_address TO client_ip;

-- 13. 删除数据
-- 删除特定条件的数据
DELETE FROM iceberg.tutorial.web_events
WHERE event_type = 'test_event';

-- 14. 更新数据
-- 更新特定记录
UPDATE iceberg.tutorial.web_events
SET referrer = 'https://direct-visit.com'
WHERE referrer = '';

-- 15. 查看表历史
-- 查询表的历史版本
SELECT * FROM iceberg.tutorial.web_events.history;

-- 16. 快照查询
-- 查询当前快照信息
SELECT * FROM iceberg.tutorial.web_events.snapshots;