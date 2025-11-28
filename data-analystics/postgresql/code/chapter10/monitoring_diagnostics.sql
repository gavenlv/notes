-- ================================================
-- PostgreSQL第10章：监控和诊断
-- ================================================
-- 本文件演示PostgreSQL的系统监控和性能诊断

-- ================================================
-- 1. 系统性能监控
-- ================================================

-- 1.1 数据库整体状态监控
CREATE OR REPLACE FUNCTION get_database_status()
RETURNS TABLE(
    metric_name VARCHAR(100),
    current_value TEXT,
    status VARCHAR(20),
    threshold_value TEXT
) AS $$
DECLARE
    db_size NUMERIC;
    connection_count INTEGER;
    active_connections INTEGER;
    cache_hit_ratio NUMERIC;
    xact_commit_rate NUMERIC;
BEGIN
    -- 获取数据库大小
    SELECT pg_database_size(current_database()) / 1024.0 / 1024.0 / 1024.0 INTO db_size;
    
    -- 获取连接数
    SELECT COUNT(*) INTO connection_count FROM pg_stat_activity;
    SELECT COUNT(*) INTO active_connections FROM pg_stat_activity WHERE state = 'active';
    
    -- 获取缓存命中率
    SELECT COALESCE(SUM(blks_hit) * 100.0 / (SUM(blks_hit) + SUM(blks_read)), 0) 
    INTO cache_hit_ratio FROM pg_stat_database;
    
    -- 获取事务提交率
    SELECT COALESCE(SUM(xact_commit) * 100.0 / (SUM(xact_commit) + SUM(xact_rollback)), 0)
    INTO xact_commit_rate FROM pg_stat_database;
    
    RETURN QUERY VALUES
        ('Database Size', 
         db_size::TEXT || ' GB',
         CASE WHEN db_size < 100 THEN 'GOOD' WHEN db_size < 500 THEN 'WARNING' ELSE 'CRITICAL' END,
         '100 GB'),
        ('Total Connections',
         connection_count::TEXT,
         CASE WHEN connection_count < 100 THEN 'GOOD' WHEN connection_count < 200 ELSE 'WARNING' END,
         '100'),
        ('Active Connections',
         active_connections::TEXT,
         CASE WHEN active_connections < 50 THEN 'GOOD' WHEN active_connections < 100 ELSE 'WARNING' END,
         '50'),
        ('Cache Hit Ratio',
         cache_hit_ratio::TEXT || '%',
         CASE WHEN cache_hit_ratio > 95 THEN 'GOOD' WHEN cache_hit_ratio > 90 ELSE 'WARNING' ELSE 'CRITICAL' END,
         '95%'),
        ('Transaction Commit Rate',
         xact_commit_rate::TEXT || '%',
         CASE WHEN xact_commit_rate > 99 THEN 'GOOD' WHEN xact_commit_rate > 95 ELSE 'WARNING' ELSE 'CRITICAL' END,
         '99%');
END;
$$ LANGUAGE plpgsql;

-- 测试数据库状态监控
SELECT * FROM get_database_status();

-- 1.2 系统资源使用监控
CREATE OR REPLACE FUNCTION monitor_system_resources()
RETURNS TABLE(
    resource_type VARCHAR(50),
    usage_percentage NUMERIC,
    available_units TEXT,
    alert_level VARCHAR(20)
) AS $$
DECLARE
    cpu_usage NUMERIC;
    memory_usage NUMERIC;
    disk_usage NUMERIC;
    network_io NUMERIC;
BEGIN
    -- 模拟系统资源监控
    cpu_usage := (random() * 80 + 10)::NUMERIC(5,2); -- 10-90%
    memory_usage := (random() * 70 + 20)::NUMERIC(5,2); -- 20-90%
    disk_usage := (random() * 60 + 10)::NUMERIC(5,2); -- 10-70%
    network_io := (random() * 500 + 50)::NUMERIC(8,2); -- MB/s
    
    RETURN QUERY VALUES
        ('CPU Usage',
         cpu_usage,
         'CPU cores',
         CASE WHEN cpu_usage > 90 THEN 'CRITICAL' WHEN cpu_usage > 75 THEN 'WARNING' ELSE 'NORMAL' END),
        ('Memory Usage',
         memory_usage,
         'RAM GB',
         CASE WHEN memory_usage > 90 THEN 'CRITICAL' WHEN memory_usage > 80 ELSE 'WARNING' ELSE 'NORMAL' END),
        ('Disk Usage',
         disk_usage,
         'Storage GB',
         CASE WHEN disk_usage > 85 THEN 'CRITICAL' WHEN disk_usage > 70 THEN 'WARNING' ELSE 'NORMAL' END),
        ('Network I/O',
         network_io,
         'MB/s',
         CASE WHEN network_io > 800 THEN 'HIGH' WHEN network_io > 400 ELSE 'NORMAL' END);
END;
$$ LANGUAGE plpgsql;

SELECT * FROM monitor_system_resources();

-- 1.3 数据库连接监控
CREATE OR REPLACE FUNCTION monitor_connections()
RETURNS TABLE(
    client_ip VARCHAR(50),
    user_name VARCHAR(100),
    application_name VARCHAR(200),
    state VARCHAR(20),
    query_start TIMESTAMP,
    query_duration INTEGER,
    blocked_by INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(client_addr::VARCHAR, 'local')::VARCHAR(50),
        usename::VARCHAR(100),
        COALESCE(application_name, 'Unknown')::VARCHAR(200),
        state::VARCHAR(20),
        query_start::TIMESTAMP,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - query_start))::INTEGER,
        blocked_by
    FROM pg_stat_activity
    WHERE state != 'idle'
    ORDER BY query_start
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- 测试连接监控
SELECT * FROM monitor_connections();

-- ================================================
-- 2. 慢查询分析
-- ================================================

-- 2.1 慢查询检测（需要pg_stat_statements扩展）
CREATE OR REPLACE FUNCTION analyze_slow_queries(
    min_execution_time INTEGER DEFAULT 1000, -- 毫秒
    limit_count INTEGER DEFAULT 20
)
RETURNS TABLE(
    query_text TEXT,
    total_calls INTEGER,
    total_time NUMERIC,
    avg_time NUMERIC,
    min_time NUMERIC,
    max_time NUMERIC,
    stddev_time NUMERIC,
    cache_hit_ratio NUMERIC
) AS $$
BEGIN
    -- 确保pg_stat_statements扩展已启用
    -- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    
    RETURN QUERY
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        min_time,
        max_time,
        stddev_time,
        CASE 
            WHEN calls > 0 THEN 
                (total_time - (mean_time * calls)) * 100.0 / NULLIF(total_time, 0)
            ELSE 0 
        END as cache_hit_ratio
    FROM pg_stat_statements
    WHERE mean_time >= min_execution_time
    ORDER BY total_time DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- 2.2 查询执行计划分析
CREATE OR REPLACE FUNCTION analyze_query_plan(
    query_text TEXT,
    analyze_mode VARCHAR(20) DEFAULT 'analyze' -- 'explain' or 'analyze'
)
RETURNS TABLE(
    plan_node TEXT,
    node_type VARCHAR(50),
    estimated_cost NUMERIC,
    estimated_rows INTEGER,
    actual_time NUMERIC,
    actual_rows INTEGER,
    loop_count INTEGER
) AS $$
DECLARE
    plan_result TEXT;
BEGIN
    -- 这里需要实际执行EXPLAIN命令
    -- 在实际环境中，需要使用动态SQL执行EXPLAIN
    
    -- 模拟执行计划分析结果
    RETURN QUERY VALUES
        ('Root', 
         'Aggregate', 
         1000.50,
         1500,
         50.25,
         1500,
         1),
        ('Child 1',
         'Hash Join',
         800.25,
         2000,
         35.10,
         2000,
         1),
        ('Child 2',
         'Index Scan',
         200.75,
         5000,
         15.15,
         2000,
         1),
        ('Child 3',
         'Seq Scan',
         150.00,
         5000,
         20.10,
         5000,
         1);
END;
$$ LANGUAGE plpgsql;

-- 2.3 查询性能趋势分析
CREATE OR REPLACE FUNCTION analyze_query_trends(
    days_back INTEGER DEFAULT 7
)
RETURNS TABLE(
    query_pattern TEXT,
    execution_count BIGINT,
    avg_execution_time NUMERIC,
    performance_change NUMERIC,
    trend_direction VARCHAR(20)
) AS $$
BEGIN
    -- 模拟查询趋势分析
    RETURN QUERY VALUES
        ('SELECT * FROM orders WHERE status = $1',
         10000,
         45.5,
         -12.3,
         'IMPROVING'),
        ('INSERT INTO users (name, email) VALUES ($1, $2)',
         5000,
         25.8,
         5.7,
         'DEGRADING'),
        ('UPDATE products SET price = $1 WHERE id = $2',
         3000,
         15.2,
         -8.4,
         'IMPROVING'),
        ('SELECT count(*) FROM events WHERE date >= $1',
         8000,
         120.75,
         15.6,
         'DEGRADING');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM analyze_query_trends(7);

-- ================================================
-- 3. 锁监控和死锁处理
-- ================================================

-- 3.1 当前锁状态监控
CREATE OR REPLACE FUNCTION monitor_locks()
RETURNS TABLE(
    lock_type VARCHAR(50),
    relation_name VARCHAR(200),
    lock_mode VARCHAR(50),
    waiting_transaction BIGINT,
    granted_transaction BIGINT,
    wait_duration INTEGER,
    blocking_query TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.locktype::VARCHAR(50),
        COALESCE(c.relname, 'Unknown')::VARCHAR(200),
        l.mode::VARCHAR(50),
        l.pid::BIGINT as waiting_transaction,
        a.pid::BIGINT as granted_transaction,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.query_start))::INTEGER as wait_duration,
        LEFT(a.query, 100)::TEXT as blocking_query
    FROM pg_locks l
    LEFT JOIN pg_class c ON l.relation = c.oid
    LEFT JOIN pg_stat_activity a ON a.pid = l.pid
    WHERE NOT l.granted
    ORDER BY wait_duration DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- 测试锁监控
SELECT * FROM monitor_locks();

-- 3.2 死锁检测和分析
CREATE OR REPLACE FUNCTION detect_deadlocks()
RETURNS TABLE(
    deadlock_id INTEGER,
    transaction_1 BIGINT,
    transaction_2 BIGINT,
    deadlock_table VARCHAR(200),
    blocking_resource VARCHAR(100),
    detection_time TIMESTAMP,
    resolution_action VARCHAR(50)
) AS $$
DECLARE
    deadlock_pattern TEXT[] := ARRAY[
        'Transaction A locked table users, waiting for table orders',
        'Transaction B locked table orders, waiting for table users'
    ];
    i INTEGER;
BEGIN
    -- 模拟死锁检测结果
    FOR i IN 1..2 LOOP
        RETURN QUERY SELECT 
            i,
            1000 + i,
            2000 + i,
            'user_orders'::VARCHAR(200),
            'table_' || i::TEXT::VARCHAR(100),
            CURRENT_TIMESTAMP - (i || ' minutes')::INTERVAL,
            'ROLLBACK_TRANSACTION_' || i::TEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM detect_deadlocks();

-- 3.3 锁等待分析
CREATE OR REPLACE FUNCTION analyze_lock_waits()
RETURNS TABLE(
    waiting_transaction BIGINT,
    waiting_query TEXT,
    blocking_transaction BIGINT,
    blocking_query TEXT,
    wait_duration INTEGER,
    lock_type VARCHAR(50),
    severity VARCHAR(20)
) AS $$
BEGIN
    -- 模拟锁等待分析
    RETURN QUERY VALUES
        (12345,
         'UPDATE users SET last_login = NOW() WHERE id = 1001',
         12344,
         'ALTER TABLE users ADD COLUMN new_field VARCHAR(100)',
         45,
         'AccessShareLock',
         'MEDIUM'),
        (12347,
         'SELECT * FROM orders WHERE user_id = 2001',
         12346,
         'VACUUM FULL orders',
         120,
         'AccessShareLock',
         'HIGH'),
        (12348,
         'DELETE FROM sessions WHERE expired = true',
         12349,
         'CREATE INDEX idx_sessions_user_id ON sessions(user_id)',
         15,
         'AccessExclusiveLock',
         'LOW');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM analyze_lock_waits();

-- ================================================
-- 4. 表和索引监控
-- ================================================

-- 4.1 表大小和增长监控
CREATE OR REPLACE FUNCTION monitor_table_sizes()
RETURNS TABLE(
    table_name VARCHAR(200),
    table_size_mb NUMERIC,
    index_size_mb NUMERIC,
    total_size_mb NUMERIC,
    row_count BIGINT,
    growth_rate NUMERIC,
    last_vacuum TIMESTAMP,
    last_analyze TIMESTAMP
) AS $$
DECLARE
    table_rec RECORD;
BEGIN
    FOR table_rec IN 
        SELECT 
            schemaname || '.' || tablename as table_name,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 20
    LOOP
        RETURN QUERY
        SELECT 
            table_rec.table_name,
            (random() * 500 + 10)::NUMERIC(10,2),
            (random() * 100 + 5)::NUMERIC(10,2),
            (random() * 600 + 15)::NUMERIC(10,2),
            (random() * 100000 + 1000)::BIGINT,
            (random() * 20 - 10)::NUMERIC(5,2), -- -10% to +10%
            CURRENT_TIMESTAMP - (random() * 24 * 7)::INTERVAL, -- Within last week
            CURRENT_TIMESTAMP - (random() * 24 * 7)::INTERVAL;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM monitor_table_sizes();

-- 4.2 索引使用情况分析
CREATE OR REPLACE FUNCTION analyze_index_usage()
RETURNS TABLE(
    index_name VARCHAR(200),
    table_name VARCHAR(200),
    index_size_mb NUMERIC,
    index_scans BIGINT,
    index_tuples_read BIGINT,
    index_tuples_fetched BIGINT,
    usage_efficiency NUMERIC,
    recommendation VARCHAR(100)
) AS $$
DECLARE
    index_rec RECORD;
BEGIN
    -- 模拟索引使用分析
    FOR index_rec IN 
        SELECT 
            indexname,
            tablename,
            indexsize
        FROM pg_stat_user_indexes 
        ORDER BY idx_scan DESC
        LIMIT 20
    LOOP
        RETURN QUERY
        SELECT 
            index_rec.indexname::VARCHAR(200),
            index_rec.tablename::VARCHAR(200),
            (random() * 50 + 1)::NUMERIC(8,2),
            (random() * 10000 + 100)::BIGINT,
            (random() * 100000 + 1000)::BIGINT,
            (random() * 50000 + 500)::BIGINT,
            (random() * 100)::NUMERIC(5,2),
            CASE 
                WHEN random() < 0.1 THEN 'Consider dropping - rarely used'
                WHEN random() < 0.3 THEN 'Medium usage - monitor'
                ELSE 'Well used - keep'
            END::VARCHAR(100);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM analyze_index_usage();

-- 4.3 表膨胀分析
CREATE OR REPLACE FUNCTION analyze_table_bloat()
RETURNS TABLE(
    table_name VARCHAR(200),
    actual_size_mb NUMERIC,
    expected_size_mb NUMERIC,
    bloat_size_mb NUMERIC,
    bloat_percentage NUMERIC,
    dead_rows INTEGER,
    vacuum_needed BOOLEAN,
    priority VARCHAR(20)
) AS $$
DECLARE
    table_rec RECORD;
BEGIN
    FOR table_rec IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        LIMIT 20
    LOOP
        RETURN QUERY
        SELECT 
            table_rec.tablename::VARCHAR(200),
            (random() * 500 + 100)::NUMERIC(10,2),
            (random() * 400 + 80)::NUMERIC(10,2),
            (random() * 100 + 1)::NUMERIC(10,2),
            (random() * 30 + 5)::NUMERIC(5,2),
            (random() * 10000 + 100)::INTEGER,
            random() < 0.5,
            CASE 
                WHEN random() > 0.8 THEN 'HIGH'
                WHEN random() > 0.5 THEN 'MEDIUM'
                ELSE 'LOW'
            END::VARCHAR(20);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM analyze_table_bloat();

-- ================================================
-- 5. 数据库健康检查
-- ================================================

-- 5.1 综合健康检查
CREATE OR REPLACE FUNCTION comprehensive_health_check()
RETURNS TABLE(
    health_category VARCHAR(100),
    check_item VARCHAR(200),
    status VARCHAR(20),
    details TEXT,
    recommendations TEXT
) AS $$
DECLARE
    db_size NUMERIC;
    connection_utilization NUMERIC;
    cache_hit_ratio NUMERIC;
    replication_lag INTEGER;
BEGIN
    -- 获取关键指标
    SELECT pg_database_size(current_database()) / 1024.0 / 1024.0 / 1024.0 INTO db_size;
    SELECT COUNT(*) * 100.0 / current_setting('max_connections')::NUMERIC INTO connection_utilization;
    
    -- 模拟其他指标
    cache_hit_ratio := (random() * 20 + 80)::NUMERIC(5,2); -- 80-100%
    replication_lag := (random() * 60)::INTEGER; -- 0-60秒
    
    RETURN QUERY VALUES
        ('Performance',
         'Cache Hit Ratio',
         CASE WHEN cache_hit_ratio > 95 THEN 'GOOD' WHEN cache_hit_ratio > 90 THEN 'WARNING' ELSE 'CRITICAL' END,
         cache_hit_ratio::TEXT || '%',
         CASE WHEN cache_hit_ratio <= 95 THEN 'Increase shared_buffers or optimize queries' ELSE 'Cache performance is optimal' END),
        ('Connections',
         'Connection Utilization',
         CASE WHEN connection_utilization < 50 THEN 'GOOD' WHEN connection_utilization < 80 ELSE 'WARNING' ELSE 'CRITICAL' END,
         connection_utilization::TEXT || '%',
         CASE WHEN connection_utilization > 80 THEN 'Consider connection pooling or increase max_connections' ELSE 'Connection usage is normal' END),
        ('Storage',
         'Database Size',
         CASE WHEN db_size < 100 THEN 'GOOD' WHEN db_size < 500 ELSE 'WARNING' END,
         db_size::TEXT || ' GB',
         CASE WHEN db_size > 100 THEN 'Monitor storage usage and consider archiving old data' ELSE 'Storage usage is normal' END),
        ('Replication',
         'Replication Lag',
         CASE WHEN replication_lag < 10 THEN 'GOOD' WHEN replication_lag < 30 ELSE 'WARNING' ELSE 'CRITICAL' END,
         replication_lag::TEXT || ' seconds',
         CASE WHEN replication_lag > 30 THEN 'Check network and replica performance' ELSE 'Replication is healthy' END),
        ('Maintenance',
         'Autovacuum Status',
         CASE WHEN random() < 0.9 THEN 'GOOD' ELSE 'WARNING' END,
         'Autovacuum running',
         'Regular maintenance appears to be running');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM comprehensive_health_check();

-- 5.2 数据库活动监控
CREATE OR REPLACE FUNCTION monitor_database_activity()
RETURNS TABLE(
    activity_type VARCHAR(50),
    metric_name VARCHAR(100),
    current_rate NUMERIC,
    baseline_rate NUMERIC,
    deviation_percentage NUMERIC,
    alert_level VARCHAR(20)
) AS $$
BEGIN
    -- 模拟数据库活动监控
    RETURN QUERY VALUES
        ('Transactions',
         'Transactions per second',
         250.5,
         200.0,
         25.3,
         'NORMAL'),
        ('Queries',
         'Queries per second',
         1500.0,
         1200.0,
         25.0,
         'NORMAL'),
        ('Connections',
         'New connections per minute',
         45.0,
         30.0,
         50.0,
         'HIGH'),
        ('Writes',
         'Writes per second',
         75.5,
         60.0,
         25.8,
         'NORMAL'),
        ('Reads',
         'Reads per second',
         1200.0,
         1500.0,
         -20.0,
         'LOW');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM monitor_database_activity();

-- ================================================
-- 6. 性能基线和告警
-- ================================================

-- 6.1 性能基线管理
CREATE TABLE performance_baselines (
    baseline_id SERIAL PRIMARY KEY,
    metric_name VARCHAR(200),
    metric_value NUMERIC,
    measurement_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    workload_type VARCHAR(50),
    environment VARCHAR(50),
    notes TEXT
);

-- 创建基线数据
INSERT INTO performance_baselines (metric_name, metric_value, workload_type, environment) VALUES
    ('avg_query_response_time', 50.0, 'normal', 'production'),
    ('transactions_per_second', 200.0, 'normal', 'production'),
    ('cache_hit_ratio', 95.0, 'normal', 'production'),
    ('connection_count', 80, 'normal', 'production'),
    ('cpu_usage_percent', 45.0, 'normal', 'production');

-- 6.2 告警规则定义
CREATE TABLE alert_rules (
    rule_id SERIAL PRIMARY KEY,
    metric_name VARCHAR(200),
    warning_threshold NUMERIC,
    critical_threshold NUMERIC,
    comparison_type VARCHAR(20), -- 'greater', 'less', 'percent_deviation'
    duration_minutes INTEGER,
    enabled BOOLEAN DEFAULT TRUE,
    notification_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO alert_rules (metric_name, warning_threshold, critical_threshold, comparison_type, duration_minutes) VALUES
    ('avg_query_response_time', 100.0, 200.0, 'greater', 5),
    ('cache_hit_ratio', 90.0, 85.0, 'less', 10),
    ('connection_count', 150, 200, 'greater', 2),
    ('replication_lag', 30.0, 60.0, 'greater', 5);

-- 6.3 告警检查函数
CREATE OR REPLACE FUNCTION check_alerts()
RETURNS TABLE(
    rule_id INTEGER,
    metric_name VARCHAR(200),
    current_value NUMERIC,
    threshold_value NUMERIC,
    alert_level VARCHAR(20),
    triggered_at TIMESTAMP,
    status VARCHAR(20)
) AS $$
DECLARE
    rule_rec RECORD;
    current_value NUMERIC;
BEGIN
    -- 检查告警规则
    FOR rule_rec IN 
        SELECT * FROM alert_rules WHERE enabled = TRUE
    LOOP
        -- 模拟当前值获取
        CASE rule_rec.metric_name
            WHEN 'avg_query_response_time' THEN current_value := (random() * 300 + 20)::NUMERIC(8,2);
            WHEN 'cache_hit_ratio' THEN current_value := (random() * 20 + 80)::NUMERIC(5,2);
            WHEN 'connection_count' THEN current_value := (random() * 250 + 10)::NUMERIC(8,2);
            WHEN 'replication_lag' THEN current_value := (random() * 100 + 5)::NUMERIC(8,2);
        END CASE;
        
        -- 判断告警级别
        IF (rule_rec.comparison_type = 'greater' AND current_value >= rule_rec.critical_threshold) OR
           (rule_rec.comparison_type = 'less' AND current_value <= rule_rec.critical_threshold) THEN
            RETURN QUERY SELECT 
                rule_rec.rule_id,
                rule_rec.metric_name,
                current_value,
                rule_rec.critical_threshold,
                'CRITICAL'::VARCHAR(20),
                CURRENT_TIMESTAMP,
                'ACTIVE'::VARCHAR(20);
        ELSIF (rule_rec.comparison_type = 'greater' AND current_value >= rule_rec.warning_threshold) OR
              (rule_rec.comparison_type = 'less' AND current_value <= rule_rec.warning_threshold) THEN
            RETURN QUERY SELECT 
                rule_rec.rule_id,
                rule_rec.metric_name,
                current_value,
                rule_rec.warning_threshold,
                'WARNING'::VARCHAR(20),
                CURRENT_TIMESTAMP,
                'ACTIVE'::VARCHAR(20);
        ELSE
            RETURN QUERY SELECT 
                rule_rec.rule_id,
                rule_rec.metric_name,
                current_value,
                rule_rec.warning_threshold,
                'NORMAL'::VARCHAR(20),
                CURRENT_TIMESTAMP,
                'OK'::VARCHAR(20);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 执行告警检查
SELECT * FROM check_alerts();

-- ================================================
-- 7. 监控仪表板数据
-- ================================================

-- 7.1 实时仪表板数据
CREATE OR REPLACE FUNCTION get_dashboard_data()
RETURNS TABLE(
    dashboard_section VARCHAR(100),
    metric_name VARCHAR(200),
    current_value TEXT,
    trend VARCHAR(20),
    status VARCHAR(20),
    last_updated TIMESTAMP
) AS $$
DECLARE
    db_stats RECORD;
BEGIN
    -- 获取数据库统计信息
    FOR db_stats IN 
        SELECT 
            datname,
            numbackends,
            xact_commit,
            xact_rollback,
            blks_read,
            blks_hit,
            tup_returned,
            tup_fetched,
            tup_inserted,
            tup_updated,
            tup_deleted
        FROM pg_stat_database 
        WHERE datname = current_database()
    LOOP
        RETURN QUERY VALUES
            ('Connections',
             'Active Connections',
             db_stats.numbackends::TEXT,
             CASE WHEN random() < 0.6 THEN 'stable' WHEN random() < 0.5 THEN 'up' ELSE 'down' END,
             CASE WHEN db_stats.numbackends < 50 THEN 'good' WHEN db_stats.numbackends < 100 ELSE 'warning' END,
             CURRENT_TIMESTAMP),
            ('Transactions',
             'Transaction Rate',
             ROUND((db_stats.xact_commit::NUMERIC / EXTRACT(EPOCH FROM NOW() - pg_postmaster_start_time())), 2)::TEXT || '/sec',
             CASE WHEN random() < 0.7 THEN 'stable' ELSE 'volatile' END,
             'good',
             CURRENT_TIMESTAMP),
            ('Cache Performance',
             'Cache Hit Ratio',
             ROUND(100.0 * db_stats.blks_hit / NULLIF(db_stats.blks_hit + db_stats.blks_read, 0), 2)::TEXT || '%',
             CASE WHEN random() < 0.8 THEN 'stable' ELSE 'declining' END,
             CASE WHEN (100.0 * db_stats.blks_hit / NULLIF(db_stats.blks_hit + db_stats.blks_read, 0)) > 95 THEN 'good' ELSE 'warning' END,
             CURRENT_TIMESTAMP),
            ('I/O Performance',
             'TPS',
             ROUND((db_stats.tup_returned + db_stats.tup_fetched)::NUMERIC / 60, 2)::TEXT || '/min',
             CASE WHEN random() < 0.6 THEN 'stable' ELSE 'increasing' END,
             'good',
             CURRENT_TIMESTAMP);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_dashboard_data();

-- ================================================
-- 8. 日志分析
-- ================================================

-- 8.1 错误日志分析
CREATE OR REPLACE FUNCTION analyze_error_logs(
    hours_back INTEGER DEFAULT 24
)
RETURNS TABLE(
    error_level VARCHAR(20),
    error_count INTEGER,
    common_errors TEXT[],
    latest_occurrence TIMESTAMP,
    trend VARCHAR(20)
) AS $$
BEGIN
    -- 模拟错误日志分析
    RETURN QUERY VALUES
        ('ERROR',
         5,
         ARRAY['connection refused', 'deadlock detected', 'disk full'],
         CURRENT_TIMESTAMP - (random() * 3600)::INTERVAL,
         CASE WHEN random() < 0.5 THEN 'decreasing' ELSE 'stable' END),
        ('WARNING',
         15,
         ARRAY['query plan not optimal', 'connection timeout', 'temp file usage high'],
         CURRENT_TIMESTAMP - (random() * 1800)::INTERVAL,
         'stable'),
        ('INFO',
         50,
         ARRAY['checkpoint complete', 'autovacuum started', 'archive complete'],
         CURRENT_TIMESTAMP - (random() * 300)::INTERVAL,
         'increasing'),
        ('DEBUG',
         200,
         ARRAY['connection established', 'query parse', 'plan generation'],
         CURRENT_TIMESTAMP - (random() * 60)::INTERVAL,
         'normal');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM analyze_error_logs(24);

-- ================================================
-- 9. 监控建议和最佳实践
-- ================================================

/*
监控最佳实践建议：

1. 监控频率配置
   - 关键指标：每1-5分钟
   - 性能指标：每5-15分钟
   - 资源指标：每1-5分钟
   - 日志分析：每小时

2. 告警设置策略
   - 告警阈值应基于历史数据和业务需求
   - 设置合理的告警频率，避免告警疲劳
   - 分级告警：CRITICAL, WARNING, INFO
   - 告警响应时间：CRITICAL < 15分钟，WARNING < 1小时

3. 数据保留策略
   - 实时数据：7天
   - 历史数据：1年
   - 聚合数据：3-5年
   - 定期清理过期数据

4. 监控覆盖范围
   - 系统资源使用
   - 数据库性能指标
   - 应用程序性能
   - 网络和存储性能
   - 安全和合规指标

5. 自动化监控
   - 自动收集和存储监控数据
   - 自动生成监控报告
   - 自动执行维护任务
   - 自动故障诊断和修复
*/
