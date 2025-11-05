-- ClickHouse Data Quality Reporting Schema
-- This script creates tables for storing data quality check results
-- Optimized for analytics and dashboard creation in Superset

-- Create database for data quality reports
CREATE DATABASE IF NOT EXISTS common;
USE common;

-- Main table for data quality scan results
CREATE TABLE IF NOT EXISTS data_quality_scans (
    scan_id String,
    data_source String,
    scan_timestamp DateTime64(3),
    total_checks UInt32,
    checks_passed UInt32,
    checks_failed UInt32,
    checks_warned UInt32,
    scan_result Int8,
    scan_duration_ms UInt32 DEFAULT 0,
    environment String DEFAULT 'production',
    created_at DateTime64(3) DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(scan_timestamp))
ORDER BY (data_source, scan_timestamp)
SETTINGS index_granularity = 8192;

-- Detailed table for individual check results
CREATE TABLE IF NOT EXISTS data_quality_checks (
    check_id String,
    scan_id String,
    data_source String,
    table_name String,
    check_name String,
    check_type String,
    check_result Enum8('PASS' = 1, 'FAIL' = 2, 'WARN' = 3, 'ERROR' = 4),
    check_value Nullable(Float64),
    expected_value Nullable(Float64),
    threshold_value Nullable(Float64),
    check_details String,
    check_category String DEFAULT 'general',
    severity Enum8('LOW' = 1, 'MEDIUM' = 2, 'HIGH' = 3, 'CRITICAL' = 4) DEFAULT 'MEDIUM',
    scan_timestamp DateTime64(3),
    created_at DateTime64(3) DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(scan_timestamp))
ORDER BY (data_source, table_name, scan_timestamp, check_name)
SETTINGS index_granularity = 8192;

-- Table for tracking data quality trends and metrics
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metric_id String,
    data_source String,
    table_name String,
    metric_name String,
    metric_value Float64,
    metric_unit String DEFAULT '',
    metric_category String DEFAULT 'quality',
    scan_timestamp DateTime64(3),
    created_at DateTime64(3) DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(scan_timestamp))
ORDER BY (data_source, table_name, metric_name, scan_timestamp)
SETTINGS index_granularity = 8192;

-- Table for storing scan logs and error details
CREATE TABLE IF NOT EXISTS data_quality_logs (
    log_id String,
    scan_id String,
    data_source String,
    log_level Enum8('DEBUG' = 1, 'INFO' = 2, 'WARN' = 3, 'ERROR' = 4),
    log_message String,
    log_details String DEFAULT '',
    scan_timestamp DateTime64(3),
    created_at DateTime64(3) DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(scan_timestamp))
ORDER BY (data_source, scan_timestamp, log_level)
SETTINGS index_granularity = 8192;

-- Daily summary table
CREATE TABLE IF NOT EXISTS data_quality_daily_summary
(
    data_source String,
    scan_date Date,
    total_scans UInt32,
    total_checks UInt32,
    total_passed UInt32,
    total_failed UInt32,
    total_warned UInt32,
    avg_pass_rate Float64,
    first_scan_time DateTime64(3),
    last_scan_time DateTime64(3)
)
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(scan_date)
ORDER BY (data_source, scan_date);

-- Materialized view to populate daily summary
CREATE MATERIALIZED VIEW IF NOT EXISTS data_quality_daily_summary_mv
TO data_quality_daily_summary
AS 
WITH aggregated AS (
    SELECT
        data_source,
        toDate(scan_timestamp) as scan_date,
        count() as total_scans,
        sum(total_checks) as total_checks,
        sum(checks_passed) as total_passed,
        sum(checks_failed) as total_failed,
        sum(checks_warned) as total_warned,
        min(scan_timestamp) as first_scan_time,
        max(scan_timestamp) as last_scan_time
    FROM data_quality_scans
    GROUP BY data_source, toDate(scan_timestamp)
)
SELECT
    data_source,
    scan_date,
    total_scans,
    total_checks,
    total_passed,
    total_failed,
    total_warned,
    if(total_checks > 0, (total_passed * 100.0 / total_checks), 0) as avg_pass_rate,
    first_scan_time,
    last_scan_time
FROM aggregated;

-- Hourly trends table
CREATE TABLE IF NOT EXISTS data_quality_hourly_trends
(
    data_source String,
    scan_date Date,
    scan_hour UInt8,
    scan_count UInt32,
    total_checks UInt32,
    total_passed UInt32,
    total_failed UInt32,
    total_warned UInt32,
    pass_rate Float64
)
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(scan_date)
ORDER BY (data_source, scan_date, scan_hour);

-- Materialized view to populate hourly trends
CREATE MATERIALIZED VIEW IF NOT EXISTS data_quality_hourly_trends_mv
TO data_quality_hourly_trends
AS 
WITH aggregated AS (
    SELECT
        data_source,
        toDate(scan_timestamp) as scan_date,
        toHour(scan_timestamp) as scan_hour,
        count() as scan_count,
        sum(total_checks) as total_checks,
        sum(checks_passed) as total_passed,
        sum(checks_failed) as total_failed,
        sum(checks_warned) as total_warned
    FROM data_quality_scans
    GROUP BY data_source, toDate(scan_timestamp), toHour(scan_timestamp)
)
SELECT
    data_source,
    scan_date,
    scan_hour,
    scan_count,
    total_checks,
    total_passed,
    total_failed,
    total_warned,
    if(total_checks > 0, (total_passed * 100.0 / total_checks), 0) as pass_rate
FROM aggregated;

-- View for latest data quality status per data source
CREATE VIEW IF NOT EXISTS data_quality_latest_status AS
SELECT 
    s.data_source,
    s.scan_timestamp as last_scan_time,
    s.total_checks,
    s.checks_passed,
    s.checks_failed,
    s.checks_warned,
    round(s.checks_passed * 100.0 / nullIf(s.total_checks, 0), 2) as pass_rate_percent,
    CASE 
        WHEN s.checks_failed = 0 THEN 'HEALTHY'
        WHEN s.checks_failed <= s.total_checks * 0.1 THEN 'WARNING'
        ELSE 'CRITICAL'
    END as health_status,
    dateDiff('hour', s.scan_timestamp, now()) as hours_since_last_scan
FROM data_quality_scans s
INNER JOIN (
    SELECT data_source, max(scan_timestamp) as max_timestamp
    FROM data_quality_scans
    GROUP BY data_source
) latest ON s.data_source = latest.data_source AND s.scan_timestamp = latest.max_timestamp;

-- View for failed checks analysis
CREATE VIEW IF NOT EXISTS data_quality_failed_checks AS
SELECT 
    c.data_source,
    c.table_name,
    c.check_name,
    c.check_type,
    c.check_details,
    c.scan_timestamp,
    count(*) OVER (PARTITION BY c.data_source, c.table_name, c.check_name ORDER BY c.scan_timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as failure_streak
FROM data_quality_checks c
WHERE c.check_result = 'FAIL'
ORDER BY c.data_source, c.table_name, c.scan_timestamp DESC;

-- Create indexes for better query performance
-- Note: ClickHouse uses ORDER BY for primary indexing, but we can create additional indexes

-- Insert sample data for testing (optional)
-- Uncomment and modify as needed
-- INSERT INTO data_quality_scans VALUES 
--     ('scan_001', 'postgresql', '2024-01-15 10:00:00', 10, 8, 2, 0, 0, 1500, 'production', now64()),
--     ('scan_002', 'clickhouse', '2024-01-15 10:05:00', 5, 3, 2, 0, 0, 800, 'production', now64());
-- 
-- INSERT INTO data_quality_checks VALUES 
--     ('check_001', 'scan_001', 'postgresql', 'users', 'row_count_check', 'volume', 'PASS', 1000, 100, 100, 'Table has sufficient data', 'volume', 'LOW', '2024-01-15 10:00:00', now64()),
--     ('check_002', 'scan_001', 'postgresql', 'users', 'null_check_email', 'completeness', 'FAIL', 5, 0, 0, 'Found 5 null email addresses', 'completeness', 'HIGH', '2024-01-15 10:00:00', now64());

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT ON data_quality.* TO superset_user;
-- GRANT INSERT ON data_quality.* TO dq_writer;
