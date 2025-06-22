-- ClickHouse Day 14: 项目实战 SQL 示例
-- 实时数据分析平台完整实现

-- ================================
-- 1. 数据库和用户设置
-- ================================

-- 创建项目数据库
CREATE DATABASE IF NOT EXISTS analytics ON CLUSTER '{cluster}';
USE analytics;

-- 创建专用用户
CREATE USER IF NOT EXISTS analytics_user ON CLUSTER '{cluster}' 
IDENTIFIED WITH plaintext_password BY 'Analytics@2024';

-- 授权
GRANT ALL ON analytics.* TO analytics_user ON CLUSTER '{cluster}';

-- ================================
-- 2. 核心数据表设计
-- ================================

-- 用户行为事件表 (本地表)
CREATE TABLE user_events_local ON CLUSTER '{cluster}'
(
    event_time DateTime64(3) COMMENT '事件时间',
    user_id UInt64 COMMENT '用户ID',
    session_id String COMMENT '会话ID',
    event_type LowCardinality(String) COMMENT '事件类型',
    page_url String COMMENT '页面URL',
    referrer String COMMENT '来源页面',
    user_agent String COMMENT '用户代理',
    ip_address IPv4 COMMENT 'IP地址',
    country LowCardinality(String) COMMENT '国家',
    city LowCardinality(String) COMMENT '城市',
    device_type LowCardinality(String) COMMENT '设备类型',
    browser LowCardinality(String) COMMENT '浏览器',
    os LowCardinality(String) COMMENT '操作系统',
    screen_resolution String COMMENT '屏幕分辨率',
    custom_properties Map(String, String) COMMENT '自定义属性',
    created_at DateTime DEFAULT now() COMMENT '创建时间'
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/user_events_local', '{replica}')
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id, event_type)
SETTINGS 
    index_granularity = 8192,
    ttl_only_drop_parts = 1;

-- 添加索引优化查询
ALTER TABLE user_events_local ADD INDEX idx_user_time (user_id, event_time) TYPE minmax GRANULARITY 1;
ALTER TABLE user_events_local ADD INDEX idx_country_device (country, device_type) TYPE set(100) GRANULARITY 1;
ALTER TABLE user_events_local ADD INDEX idx_page_url (page_url) TYPE bloom_filter(0.01) GRANULARITY 1;

-- 设置TTL策略
ALTER TABLE user_events_local MODIFY TTL 
    event_time + INTERVAL 7 DAY TO DISK 'cold',
    event_time + INTERVAL 30 DAY TO VOLUME 'archive',
    event_time + INTERVAL 365 DAY DELETE;

-- 分布式表
CREATE TABLE user_events ON CLUSTER '{cluster}' AS user_events_local
ENGINE = Distributed('{cluster}', analytics, user_events_local, rand());

-- 应用性能指标表 (本地表)
CREATE TABLE app_metrics_local ON CLUSTER '{cluster}'
(
    timestamp DateTime64(3) COMMENT '时间戳',
    service_name LowCardinality(String) COMMENT '服务名称',
    instance_id String COMMENT '实例ID',
    metric_name LowCardinality(String) COMMENT '指标名称',
    metric_value Float64 COMMENT '指标值',
    tags Map(String, String) COMMENT '标签',
    host_name LowCardinality(String) COMMENT '主机名',
    environment LowCardinality(String) COMMENT '环境',
    created_at DateTime DEFAULT now() COMMENT '创建时间'
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/app_metrics_local', '{replica}')
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, service_name, metric_name)
TTL timestamp + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;

-- 分布式表
CREATE TABLE app_metrics ON CLUSTER '{cluster}' AS app_metrics_local
ENGINE = Distributed('{cluster}', analytics, app_metrics_local, rand());

-- 错误日志表 (本地表)
CREATE TABLE error_logs_local ON CLUSTER '{cluster}'
(
    timestamp DateTime64(3) COMMENT '时间戳',
    level LowCardinality(String) COMMENT '日志级别',
    service_name LowCardinality(String) COMMENT '服务名称',
    message String COMMENT '错误信息',
    stack_trace String COMMENT '堆栈跟踪',
    user_id UInt64 COMMENT '用户ID',
    session_id String COMMENT '会话ID',
    request_id String COMMENT '请求ID',
    host_name LowCardinality(String) COMMENT '主机名',
    environment LowCardinality(String) COMMENT '环境',
    tags Map(String, String) COMMENT '标签',
    created_at DateTime DEFAULT now() COMMENT '创建时间'
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/error_logs_local', '{replica}')
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, level, service_name)
TTL timestamp + INTERVAL 30 DAY
SETTINGS index_granularity = 8192;

-- 分布式表
CREATE TABLE error_logs ON CLUSTER '{cluster}' AS error_logs_local
ENGINE = Distributed('{cluster}', analytics, error_logs_local, rand());

-- ================================
-- 3. 数据接入层 (Kafka集成)
-- ================================

-- Kafka引擎表用于实时数据接入
CREATE TABLE user_events_kafka ON CLUSTER '{cluster}'
(
    event_time DateTime64(3),
    user_id UInt64,
    session_id String,
    event_type String,
    page_url String,
    referrer String,
    user_agent String,
    ip_address String,
    screen_resolution String,
    custom_properties String
)
ENGINE = Kafka
SETTINGS 
    kafka_broker_list = 'kafka1:9092,kafka2:9092,kafka3:9092',
    kafka_topic_list = 'user-events',
    kafka_group_name = 'clickhouse-consumer-group',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 3,
    kafka_max_block_size = 1048576,
    kafka_skip_broken_messages = 1000;

-- 物化视图实现数据转换和存储
CREATE MATERIALIZED VIEW user_events_mv ON CLUSTER '{cluster}'
TO user_events_local
AS SELECT
    event_time,
    user_id,
    session_id,
    event_type,
    page_url,
    referrer,
    user_agent,
    IPv4StringToNum(ip_address) as ip_address,
    geoToCountry(IPv4StringToNum(ip_address)) as country,
    geoToCity(IPv4StringToNum(ip_address)) as city,
    multiIf(
        match(user_agent, '(?i)mobile|android|iphone'), 'mobile',
        match(user_agent, '(?i)tablet|ipad'), 'tablet',
        'desktop'
    ) as device_type,
    multiIf(
        match(user_agent, '(?i)chrome'), 'Chrome',
        match(user_agent, '(?i)firefox'), 'Firefox',
        match(user_agent, '(?i)safari'), 'Safari',
        match(user_agent, '(?i)edge'), 'Edge',
        'Other'
    ) as browser,
    multiIf(
        match(user_agent, '(?i)windows'), 'Windows',
        match(user_agent, '(?i)mac'), 'macOS',
        match(user_agent, '(?i)linux'), 'Linux',
        match(user_agent, '(?i)android'), 'Android',
        match(user_agent, '(?i)ios'), 'iOS',
        'Other'
    ) as os,
    screen_resolution,
    JSONExtractKeysAndValues(custom_properties, 'String') as custom_properties
FROM user_events_kafka;

-- ================================
-- 4. 预聚合表设计
-- ================================

-- 用户行为小时级聚合表
CREATE TABLE user_events_hourly_local ON CLUSTER '{cluster}'
(
    event_hour DateTime COMMENT '事件小时',
    event_type LowCardinality(String) COMMENT '事件类型',
    country LowCardinality(String) COMMENT '国家',
    device_type LowCardinality(String) COMMENT '设备类型',
    total_events UInt64 COMMENT '总事件数',
    unique_users UInt64 COMMENT '独立用户数',
    unique_sessions UInt64 COMMENT '独立会话数',
    avg_session_duration Float64 COMMENT '平均会话时长',
    bounce_rate Float64 COMMENT '跳出率'
)
ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/{shard}/user_events_hourly_local', '{replica}')
PARTITION BY toYYYYMM(event_hour)
ORDER BY (event_hour, event_type, country, device_type)
SETTINGS index_granularity = 8192;

-- 分布式表
CREATE TABLE user_events_hourly ON CLUSTER '{cluster}' AS user_events_hourly_local
ENGINE = Distributed('{cluster}', analytics, user_events_hourly_local, rand());

-- 小时级聚合物化视图
CREATE MATERIALIZED VIEW user_events_hourly_mv ON CLUSTER '{cluster}'
TO user_events_hourly_local
AS SELECT
    toStartOfHour(event_time) as event_hour,
    event_type,
    country,
    device_type,
    count() as total_events,
    uniq(user_id) as unique_users,
    uniq(session_id) as unique_sessions,
    avg(assumeNotNull(session_duration)) as avg_session_duration,
    countIf(page_views = 1) / count() as bounce_rate
FROM (
    SELECT
        event_time,
        event_type,
        country,
        device_type,
        user_id,
        session_id,
        count() OVER (PARTITION BY session_id) as page_views,
        max(event_time) OVER (PARTITION BY session_id) - 
        min(event_time) OVER (PARTITION BY session_id) as session_duration
    FROM user_events_local
    WHERE event_time >= now() - INTERVAL 2 HOUR
)
GROUP BY event_hour, event_type, country, device_type;

-- 日级用户行为汇总表
CREATE TABLE user_behavior_daily_local ON CLUSTER '{cluster}'
(
    date Date COMMENT '日期',
    user_id UInt64 COMMENT '用户ID',
    first_visit_time DateTime COMMENT '首次访问时间',
    last_visit_time DateTime COMMENT '最后访问时间',
    total_sessions UInt32 COMMENT '总会话数',
    total_page_views UInt32 COMMENT '总页面浏览数',
    total_events UInt32 COMMENT '总事件数',
    unique_pages UInt32 COMMENT '独立页面数',
    avg_session_duration Float64 COMMENT '平均会话时长',
    countries Array(String) COMMENT '访问国家列表',
    devices Array(String) COMMENT '使用设备列表'
)
ENGINE = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/user_behavior_daily_local', '{replica}')
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id)
SETTINGS index_granularity = 8192;

-- 分布式表
CREATE TABLE user_behavior_daily ON CLUSTER '{cluster}' AS user_behavior_daily_local
ENGINE = Distributed('{cluster}', analytics, user_behavior_daily_local, rand());

-- ================================
-- 5. 实时监控查询
-- ================================

-- 实时流量监控
SELECT
    toStartOfMinute(event_time) as minute,
    count() as events,
    uniq(user_id) as users,
    uniq(session_id) as sessions,
    round(avg(assumeNotNull(session_duration)), 2) as avg_session_duration
FROM (
    SELECT
        event_time,
        user_id,
        session_id,
        max(event_time) OVER (PARTITION BY session_id) - 
        min(event_time) OVER (PARTITION BY session_id) as session_duration
    FROM user_events
    WHERE event_time >= now() - INTERVAL 1 HOUR
)
GROUP BY minute
ORDER BY minute DESC
LIMIT 60;

-- 实时错误监控
SELECT
    service_name,
    level,
    count() as error_count,
    count(DISTINCT user_id) as affected_users,
    count(DISTINCT session_id) as affected_sessions,
    max(timestamp) as last_error,
    groupArray(message) as recent_messages
FROM error_logs
WHERE timestamp >= now() - INTERVAL 5 MINUTE
    AND level IN ('ERROR', 'FATAL')
GROUP BY service_name, level
HAVING error_count > 5
ORDER BY error_count DESC;

-- 实时性能监控
SELECT
    service_name,
    metric_name,
    round(avg(metric_value), 2) as avg_value,
    round(quantile(0.50)(metric_value), 2) as p50,
    round(quantile(0.95)(metric_value), 2) as p95,
    round(quantile(0.99)(metric_value), 2) as p99,
    round(max(metric_value), 2) as max_value,
    count() as sample_count
FROM app_metrics
WHERE timestamp >= now() - INTERVAL 5 MINUTE
    AND metric_name IN ('response_time', 'cpu_usage', 'memory_usage', 'disk_io')
GROUP BY service_name, metric_name
ORDER BY service_name, metric_name;

-- ================================
-- 6. 用户行为分析查询
-- ================================

-- 用户漏斗分析
WITH funnel_steps AS (
    SELECT
        user_id,
        session_id,
        event_time,
        event_type,
        multiIf(
            event_type = 'page_view', 1,
            event_type = 'product_view', 2,
            event_type = 'add_to_cart', 3,
            event_type = 'checkout_start', 4,
            event_type = 'payment', 5,
            event_type = 'purchase', 6,
            0
        ) as step_number
    FROM user_events
    WHERE event_time >= today() - INTERVAL 7 DAY
        AND event_type IN ('page_view', 'product_view', 'add_to_cart', 'checkout_start', 'payment', 'purchase')
        AND step_number > 0
),
funnel_data AS (
    SELECT
        step_number,
        event_type,
        count(DISTINCT session_id) as sessions,
        count(DISTINCT user_id) as users
    FROM funnel_steps
    GROUP BY step_number, event_type
)
SELECT
    step_number,
    event_type,
    sessions,
    users,
    round(sessions / first_value(sessions) OVER (ORDER BY step_number) * 100, 2) as session_conversion_rate,
    round(users / first_value(users) OVER (ORDER BY step_number) * 100, 2) as user_conversion_rate,
    round(sessions / lag(sessions) OVER (ORDER BY step_number) * 100, 2) as step_conversion_rate
FROM funnel_data
ORDER BY step_number;

-- 用户留存分析
WITH user_cohorts AS (
    SELECT
        user_id,
        toMonday(min(event_time)) as cohort_week,
        min(event_time) as first_event_time
    FROM user_events
    WHERE event_time >= today() - INTERVAL 12 WEEK
    GROUP BY user_id
),
user_activities AS (
    SELECT
        uc.user_id,
        uc.cohort_week,
        toMonday(ue.event_time) as activity_week,
        dateDiff('week', uc.cohort_week, toMonday(ue.event_time)) as week_number
    FROM user_cohorts uc
    JOIN user_events ue ON uc.user_id = ue.user_id
    WHERE ue.event_time >= uc.first_event_time
        AND ue.event_time <= today()
),
retention_data AS (
    SELECT
        cohort_week,
        week_number,
        count(DISTINCT user_id) as retained_users
    FROM user_activities
    GROUP BY cohort_week, week_number
),
cohort_sizes AS (
    SELECT
        cohort_week,
        count(DISTINCT user_id) as cohort_size
    FROM user_cohorts
    GROUP BY cohort_week
)
SELECT
    rd.cohort_week,
    rd.week_number,
    cs.cohort_size,
    rd.retained_users,
    round(rd.retained_users / cs.cohort_size * 100, 2) as retention_rate
FROM retention_data rd
JOIN cohort_sizes cs ON rd.cohort_week = cs.cohort_week
WHERE cs.cohort_size >= 100  -- 只分析有足够样本的群组
ORDER BY rd.cohort_week DESC, rd.week_number;

-- 用户路径分析
WITH user_paths AS (
    SELECT
        session_id,
        user_id,
        page_url,
        event_time,
        row_number() OVER (PARTITION BY session_id ORDER BY event_time) as step_order,
        lead(page_url) OVER (PARTITION BY session_id ORDER BY event_time) as next_page
    FROM user_events
    WHERE event_time >= today() - INTERVAL 1 DAY
        AND event_type = 'page_view'
        AND page_url != ''
),
path_transitions AS (
    SELECT
        page_url as from_page,
        next_page as to_page,
        count() as transition_count,
        count(DISTINCT session_id) as unique_sessions
    FROM user_paths
    WHERE next_page IS NOT NULL
    GROUP BY from_page, to_page
)
SELECT
    from_page,
    to_page,
    transition_count,
    unique_sessions,
    round(transition_count / sum(transition_count) OVER (PARTITION BY from_page) * 100, 2) as transition_rate
FROM path_transitions
WHERE transition_count >= 10
ORDER BY from_page, transition_count DESC;

-- ================================
-- 7. 异常检测查询
-- ================================

-- 异常流量检测
WITH hourly_traffic AS (
    SELECT
        toStartOfHour(event_time) as hour,
        count() as events,
        uniq(user_id) as users
    FROM user_events
    WHERE event_time >= now() - INTERVAL 7 DAY
    GROUP BY hour
),
traffic_stats AS (
    SELECT
        hour,
        events,
        users,
        avg(events) OVER (ORDER BY hour ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) as avg_events_24h,
        stddevPop(events) OVER (ORDER BY hour ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) as stddev_events_24h,
        avg(users) OVER (ORDER BY hour ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) as avg_users_24h,
        stddevPop(users) OVER (ORDER BY hour ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) as stddev_users_24h
    FROM hourly_traffic
    ORDER BY hour
)
SELECT
    hour,
    events,
    users,
    round(avg_events_24h, 0) as expected_events,
    round(avg_users_24h, 0) as expected_users,
    round((events - avg_events_24h) / nullIf(stddev_events_24h, 0), 2) as events_z_score,
    round((users - avg_users_24h) / nullIf(stddev_users_24h, 0), 2) as users_z_score,
    multiIf(
        abs(events_z_score) > 3, 'CRITICAL',
        abs(events_z_score) > 2, 'WARNING',
        'NORMAL'
    ) as events_status,
    multiIf(
        abs(users_z_score) > 3, 'CRITICAL',
        abs(users_z_score) > 2, 'WARNING',
        'NORMAL'
    ) as users_status
FROM traffic_stats
WHERE hour >= now() - INTERVAL 24 HOUR
    AND (abs(events_z_score) > 2 OR abs(users_z_score) > 2)
ORDER BY hour DESC;

-- 应用性能异常检测
WITH metric_stats AS (
    SELECT
        service_name,
        metric_name,
        timestamp,
        metric_value,
        avg(metric_value) OVER (
            PARTITION BY service_name, metric_name 
            ORDER BY timestamp 
            ROWS BETWEEN 100 PRECEDING AND 1 PRECEDING
        ) as moving_avg,
        stddevPop(metric_value) OVER (
            PARTITION BY service_name, metric_name 
            ORDER BY timestamp 
            ROWS BETWEEN 100 PRECEDING AND 1 PRECEDING
        ) as moving_stddev
    FROM app_metrics
    WHERE timestamp >= now() - INTERVAL 2 HOUR
        AND metric_name IN ('response_time', 'error_rate', 'cpu_usage', 'memory_usage')
)
SELECT
    service_name,
    metric_name,
    timestamp,
    round(metric_value, 2) as current_value,
    round(moving_avg, 2) as expected_value,
    round((metric_value - moving_avg) / nullIf(moving_stddev, 0), 2) as z_score,
    multiIf(
        abs(z_score) > 3, 'CRITICAL',
        abs(z_score) > 2, 'WARNING',
        'NORMAL'
    ) as status
FROM metric_stats
WHERE abs(z_score) > 2
    AND moving_stddev > 0
ORDER BY timestamp DESC, abs(z_score) DESC;

-- ================================
-- 8. 数据质量检查
-- ================================

-- 数据完整性检查
SELECT
    'user_events' as table_name,
    count() as total_records,
    countIf(user_id = 0 OR user_id IS NULL) as invalid_user_ids,
    countIf(session_id = '' OR session_id IS NULL) as invalid_session_ids,
    countIf(event_time < '2020-01-01' OR event_time > now() + INTERVAL 1 HOUR) as invalid_timestamps,
    countIf(event_type = '' OR event_type IS NULL) as invalid_event_types,
    round(countIf(user_id = 0 OR user_id IS NULL) / count() * 100, 2) as invalid_user_rate,
    round(countIf(session_id = '' OR session_id IS NULL) / count() * 100, 2) as invalid_session_rate
FROM user_events
WHERE event_time >= today() - INTERVAL 1 DAY

UNION ALL

SELECT
    'app_metrics' as table_name,
    count() as total_records,
    countIf(service_name = '' OR service_name IS NULL) as invalid_service_names,
    countIf(metric_name = '' OR metric_name IS NULL) as invalid_metric_names,
    countIf(metric_value IS NULL OR isNaN(metric_value) OR isInfinite(metric_value)) as invalid_metric_values,
    countIf(timestamp < now() - INTERVAL 7 DAY OR timestamp > now() + INTERVAL 1 HOUR) as invalid_timestamps,
    0 as invalid_event_types,
    round(countIf(service_name = '' OR service_name IS NULL) / count() * 100, 2) as invalid_service_rate,
    round(countIf(metric_value IS NULL OR isNaN(metric_value)) / count() * 100, 2) as invalid_metric_rate
FROM app_metrics
WHERE timestamp >= today() - INTERVAL 1 DAY;

-- 重复数据检查
SELECT
    'user_events_duplicates' as check_type,
    count() as total_records,
    count() - count(DISTINCT (user_id, session_id, event_time, event_type)) as duplicate_records,
    round((count() - count(DISTINCT (user_id, session_id, event_time, event_type))) / count() * 100, 2) as duplicate_rate
FROM user_events
WHERE event_time >= today() - INTERVAL 1 DAY;

-- 数据分布检查
SELECT
    'user_events_distribution' as check_type,
    country,
    device_type,
    count() as event_count,
    round(count() / sum(count()) OVER () * 100, 2) as percentage
FROM user_events
WHERE event_time >= today() - INTERVAL 1 DAY
GROUP BY country, device_type
ORDER BY event_count DESC
LIMIT 20;

-- ================================
-- 9. 性能测试查询
-- ================================

-- 查询性能基准测试
SELECT
    'large_aggregation_test' as test_name,
    count() as processed_records,
    uniq(user_id) as unique_users,
    uniq(session_id) as unique_sessions,
    now() as test_end_time
FROM user_events
WHERE event_time >= today() - INTERVAL 30 DAY;

-- 复杂JOIN性能测试
SELECT
    'join_performance_test' as test_name,
    count() as result_count,
    avg(ue.user_id) as avg_user_id,
    now() as test_end_time
FROM user_events ue
JOIN (
    SELECT DISTINCT user_id
    FROM user_events
    WHERE event_time >= today() - INTERVAL 7 DAY
        AND event_type = 'purchase'
) buyers ON ue.user_id = buyers.user_id
WHERE ue.event_time >= today() - INTERVAL 7 DAY;

-- 窗口函数性能测试
SELECT
    'window_function_test' as test_name,
    count() as processed_records,
    avg(session_rank) as avg_session_rank,
    now() as test_end_time
FROM (
    SELECT
        user_id,
        session_id,
        row_number() OVER (PARTITION BY user_id ORDER BY min(event_time)) as session_rank
    FROM user_events
    WHERE event_time >= today() - INTERVAL 7 DAY
    GROUP BY user_id, session_id
) ranked_sessions;

-- ================================
-- 10. 系统监控查询
-- ================================

-- 集群状态检查
SELECT
    hostname() as node,
    database,
    table,
    partition,
    active,
    is_leader,
    absolute_delay,
    log_max_index - log_pointer as replication_lag
FROM system.replicas
WHERE database = 'analytics'
ORDER BY absolute_delay DESC;

-- 查询性能统计
SELECT
    query_kind,
    type,
    count() as query_count,
    round(avg(query_duration_ms), 2) as avg_duration_ms,
    round(quantile(0.95)(query_duration_ms), 2) as p95_duration_ms,
    round(avg(read_rows), 0) as avg_read_rows,
    round(avg(read_bytes / 1024 / 1024), 2) as avg_read_mb
FROM system.query_log
WHERE event_time >= now() - INTERVAL 1 HOUR
    AND type = 'QueryFinish'
    AND query NOT LIKE '%system.%'
GROUP BY query_kind, type
ORDER BY avg_duration_ms DESC;

-- 存储使用情况
SELECT
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as disk_size,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed_size,
    round(sum(bytes_on_disk) / sum(data_uncompressed_bytes), 2) as compression_ratio,
    sum(rows) as total_rows,
    count() as partitions
FROM system.parts
WHERE database = 'analytics'
    AND active = 1
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;

-- ================================
-- 11. 告警规则定义
-- ================================

-- 创建告警表
CREATE TABLE alerts_local ON CLUSTER '{cluster}'
(
    alert_time DateTime COMMENT '告警时间',
    alert_type LowCardinality(String) COMMENT '告警类型',
    severity LowCardinality(String) COMMENT '严重程度',
    service_name LowCardinality(String) COMMENT '服务名称',
    message String COMMENT '告警信息',
    tags Map(String, String) COMMENT '标签',
    resolved UInt8 DEFAULT 0 COMMENT '是否已解决',
    resolved_time DateTime COMMENT '解决时间'
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/alerts_local', '{replica}')
PARTITION BY toYYYYMMDD(alert_time)
ORDER BY (alert_time, alert_type, service_name)
SETTINGS index_granularity = 8192;

-- 分布式表
CREATE TABLE alerts ON CLUSTER '{cluster}' AS alerts_local
ENGINE = Distributed('{cluster}', analytics, alerts_local, rand());

-- 高错误率告警
INSERT INTO alerts
SELECT
    now() as alert_time,
    'high_error_rate' as alert_type,
    'CRITICAL' as severity,
    service_name,
    concat('High error rate detected: ', toString(round(error_rate, 2)), '% (', toString(error_count), ' errors in last 5 minutes)') as message,
    map('error_count', toString(error_count), 'total_logs', toString(total_logs), 'threshold', '5.0') as tags
FROM (
    SELECT
        service_name,
        countIf(level IN ('ERROR', 'FATAL')) as error_count,
        count() as total_logs,
        (error_count / total_logs) * 100 as error_rate
    FROM error_logs
    WHERE timestamp >= now() - INTERVAL 5 MINUTE
    GROUP BY service_name
    HAVING error_rate > 5 AND total_logs > 10
);

-- 性能异常告警
INSERT INTO alerts
SELECT
    now() as alert_time,
    'performance_anomaly' as alert_type,
    multiIf(avg_response_time > 5000, 'CRITICAL', 'WARNING') as severity,
    service_name,
    concat('High response time detected: ', toString(round(avg_response_time, 2)), 'ms (threshold: 1000ms)') as message,
    map('avg_response_time', toString(avg_response_time), 'p95_response_time', toString(p95_response_time), 'threshold', '1000') as tags
FROM (
    SELECT
        service_name,
        avg(metric_value) as avg_response_time,
        quantile(0.95)(metric_value) as p95_response_time
    FROM app_metrics
    WHERE timestamp >= now() - INTERVAL 5 MINUTE
        AND metric_name = 'response_time'
    GROUP BY service_name
    HAVING avg_response_time > 1000
);

-- ================================
-- 12. 数据清理和维护
-- ================================

-- 清理过期告警
DELETE FROM alerts_local
WHERE alert_time < now() - INTERVAL 30 DAY
    AND resolved = 1;

-- 优化表结构
OPTIMIZE TABLE user_events_local ON CLUSTER '{cluster}' FINAL;
OPTIMIZE TABLE app_metrics_local ON CLUSTER '{cluster}' FINAL;
OPTIMIZE TABLE error_logs_local ON CLUSTER '{cluster}' FINAL;

-- 检查表完整性
CHECK TABLE user_events_local ON CLUSTER '{cluster}';
CHECK TABLE app_metrics_local ON CLUSTER '{cluster}';
CHECK TABLE error_logs_local ON CLUSTER '{cluster}';

-- ================================
-- 13. 示例数据生成 (用于测试)
-- ================================

-- 生成测试用户事件数据
INSERT INTO user_events_local
SELECT
    now() - INTERVAL (rand() % 86400) SECOND as event_time,
    rand() % 100000 + 1 as user_id,
    concat('session_', toString(rand() % 10000)) as session_id,
    ['page_view', 'click', 'scroll', 'form_submit', 'purchase'][rand() % 5 + 1] as event_type,
    concat('/page/', toString(rand() % 100 + 1)) as page_url,
    if(rand() % 3 = 0, '', concat('https://referrer', toString(rand() % 10 + 1), '.com')) as referrer,
    concat('Mozilla/5.0 (', ['Windows NT 10.0', 'Macintosh', 'X11; Linux x86_64'][rand() % 3 + 1], ') Browser/1.0') as user_agent,
    IPv4NumToString(rand() % 4294967295) as ip_address,
    ['US', 'CN', 'UK', 'DE', 'JP', 'FR', 'CA', 'AU'][rand() % 8 + 1] as country,
    ['New York', 'Beijing', 'London', 'Tokyo', 'Paris'][rand() % 5 + 1] as city,
    ['desktop', 'mobile', 'tablet'][rand() % 3 + 1] as device_type,
    ['Chrome', 'Firefox', 'Safari', 'Edge'][rand() % 4 + 1] as browser,
    ['Windows', 'macOS', 'Linux', 'iOS', 'Android'][rand() % 5 + 1] as os,
    concat(toString((rand() % 3 + 1) * 1920), 'x', toString((rand() % 3 + 1) * 1080)) as screen_resolution,
    map('campaign', concat('campaign_', toString(rand() % 10 + 1)), 'source', ['google', 'facebook', 'twitter'][rand() % 3 + 1]) as custom_properties
FROM numbers(100000);

-- 生成测试应用指标数据
INSERT INTO app_metrics_local
SELECT
    now() - INTERVAL (rand() % 3600) SECOND as timestamp,
    ['web-service', 'api-service', 'auth-service', 'payment-service'][rand() % 4 + 1] as service_name,
    concat('instance-', toString(rand() % 5 + 1)) as instance_id,
    ['response_time', 'cpu_usage', 'memory_usage', 'disk_io', 'network_io'][rand() % 5 + 1] as metric_name,
    rand() % 1000 + (rand() % 100) / 100.0 as metric_value,
    map('environment', 'production', 'region', ['us-east-1', 'us-west-2', 'eu-west-1'][rand() % 3 + 1]) as tags,
    concat('host-', toString(rand() % 10 + 1)) as host_name,
    'production' as environment
FROM numbers(50000);

-- 生成测试错误日志数据
INSERT INTO error_logs_local
SELECT
    now() - INTERVAL (rand() % 3600) SECOND as timestamp,
    ['ERROR', 'WARN', 'FATAL'][rand() % 3 + 1] as level,
    ['web-service', 'api-service', 'auth-service'][rand() % 3 + 1] as service_name,
    concat('Error message ', toString(rand() % 1000)) as message,
    concat('Stack trace line ', toString(rand() % 50)) as stack_trace,
    rand() % 100000 + 1 as user_id,
    concat('session_', toString(rand() % 10000)) as session_id,
    concat('req_', toString(rand() % 100000)) as request_id,
    concat('host-', toString(rand() % 10 + 1)) as host_name,
    'production' as environment,
    map('error_code', toString(rand() % 500 + 400), 'module', ['auth', 'payment', 'user'][rand() % 3 + 1]) as tags
FROM numbers(1000);

-- ================================
-- 项目总结查询
-- ================================

-- 项目整体数据统计
SELECT
    'Project Summary' as report_type,
    formatReadableQuantity(count()) as total_events,
    formatReadableQuantity(uniq(user_id)) as unique_users,
    formatReadableQuantity(uniq(session_id)) as unique_sessions,
    round(avg(assumeNotNull(session_duration)), 2) as avg_session_duration_minutes,
    min(event_time) as earliest_event,
    max(event_time) as latest_event,
    dateDiff('day', min(event_time), max(event_time)) as data_span_days
FROM (
    SELECT
        event_time,
        user_id,
        session_id,
        (max(event_time) OVER (PARTITION BY session_id) - 
         min(event_time) OVER (PARTITION BY session_id)) / 60 as session_duration
    FROM user_events
    WHERE event_time >= today() - INTERVAL 30 DAY
);

-- 系统性能总结
SELECT
    'System Performance Summary' as report_type,
    round(avg(query_duration_ms), 2) as avg_query_duration_ms,
    round(quantile(0.95)(query_duration_ms), 2) as p95_query_duration_ms,
    formatReadableSize(avg(read_bytes)) as avg_read_bytes,
    formatReadableQuantity(avg(read_rows)) as avg_read_rows,
    count() as total_queries
FROM system.query_log
WHERE event_time >= today() - INTERVAL 1 DAY
    AND type = 'QueryFinish'
    AND query NOT LIKE '%system.%';

-- 数据质量总结
SELECT
    'Data Quality Summary' as report_type,
    round((1 - countIf(user_id = 0 OR user_id IS NULL) / count()) * 100, 2) as user_id_quality_score,
    round((1 - countIf(session_id = '' OR session_id IS NULL) / count()) * 100, 2) as session_id_quality_score,
    round((1 - countIf(event_type = '' OR event_type IS NULL) / count()) * 100, 2) as event_type_quality_score,
    round((count() - count(DISTINCT (user_id, session_id, event_time, event_type))) / count() * 100, 2) as duplicate_rate,
    count() as total_records_analyzed
FROM user_events
WHERE event_time >= today() - INTERVAL 7 DAY; 