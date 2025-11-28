-- ================================================
-- PostgreSQL第10章：备份策略和工具详解
-- ================================================
-- 本文件演示PostgreSQL的各种备份方法和策略

-- 清理环境
-- DROP TABLE IF EXISTS demo_data CASCADE;

-- ================================================
-- 1. 创建测试环境
-- ================================================

-- 创建测试数据库（如果不存在）
-- CREATE DATABASE backup_demo;
-- \c backup_demo

-- 创建测试表和数据
CREATE TABLE demo_products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE demo_orders (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200),
    product_id INTEGER REFERENCES demo_products(product_id),
    quantity INTEGER,
    order_date DATE DEFAULT CURRENT_DATE,
    total_amount DECIMAL(12,2)
);

CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50),
    table_name VARCHAR(100),
    record_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operator VARCHAR(100)
);

-- 插入测试数据
INSERT INTO demo_products (product_name, category, price)
SELECT 
    'Product ' || i,
    CASE WHEN i % 5 = 0 THEN 'Electronics' WHEN i % 5 = 1 THEN 'Clothing' 
         WHEN i % 5 = 2 THEN 'Books' WHEN i % 5 = 3 THEN 'Home' ELSE 'Sports' END,
    (10 + random() * 990)::DECIMAL(10,2)
FROM generate_series(1, 1000) AS i;

INSERT INTO demo_orders (customer_name, product_id, quantity, total_amount)
SELECT 
    'Customer ' || (i % 500 + 1),
    (i % 1000) + 1,
    (random() * 10 + 1)::INTEGER,
    (random() * 500 + 50)::DECIMAL(12,2)
FROM generate_series(1, 10000) AS i;

-- ================================================
-- 2. 逻辑备份：pg_dump工具
-- ================================================

-- 2.1 基本逻辑备份命令
/*
# 创建完整数据库备份
pg_dump -U postgres -h localhost -p 5432 backup_demo > backup_demo.sql

# 压缩备份
pg_dump -U postgres -h localhost -p 5432 backup_demo | gzip > backup_demo.sql.gz

# 自定义格式备份（推荐）
pg_dump -U postgres -h localhost -p 5432 -Fc -f backup_demo_custom.dump backup_demo

# 指定数据表
pg_dump -U postgres -h localhost -p 5432 -t demo_products -t demo_orders backup_demo

# 只备份数据结构（不包含数据）
pg_dump -U postgres -h localhost -p 5432 -s backup_demo > backup_demo_schema.sql

# 只备份数据（不包含结构）
pg_dump -U postgres -h localhost -p 5432 -a backup_demo > backup_demo_data.sql
*/

-- 2.2 PostgreSQL内的备份函数
CREATE OR REPLACE FUNCTION perform_logical_backup(
    backup_path TEXT,
    backup_type TEXT DEFAULT 'custom'  -- 'custom', 'plain', 'tar'
)
RETURNS TEXT AS $$
DECLARE
    backup_command TEXT;
    result TEXT;
BEGIN
    CASE backup_type
        WHEN 'custom' THEN
            backup_command := 'pg_dump -U postgres -h localhost -p 5432 -Fc -f ' || backup_path || ' backup_demo';
        WHEN 'plain' THEN
            backup_command := 'pg_dump -U postgres -h localhost -p 5432 ' || backup_path || ' backup_demo';
        WHEN 'tar' THEN
            backup_command := 'pg_dump -U postgres -h localhost -p 5432 -Ft -f ' || backup_path || ' backup_demo';
        ELSE
            RAISE EXCEPTION 'Invalid backup type: %. Use custom, plain, or tar', backup_type;
    END CASE;
    
    -- 注意：这里只是演示，实际执行需要通过操作系统命令
    result := 'Backup command: ' || backup_command;
    result := result || chr(10) || 'Backup type: ' || backup_type;
    result := result || chr(10) || 'Target: backup_demo database';
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 测试备份函数
SELECT perform_logical_backup('/backup/demo_custom.dump', 'custom');

-- 2.3 增量备份策略
CREATE OR REPLACE FUNCTION create_incremental_backup(
    output_path TEXT,
    since_wal_lsn TEXT DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
    current_wal_lsn TEXT;
    wal_range TEXT;
BEGIN
    -- 获取当前WAL位置
    SELECT pg_current_wal_lsn()::TEXT INTO current_wal_lsn;
    
    IF since_wal_lsn IS NULL THEN
        wal_range := 'Full backup from: ' || current_wal_lsn;
    ELSE
        wal_range := 'Incremental backup from: ' || since_wal_lsn || ' to: ' || current_wal_lsn;
    END IF;
    
    RETURN wal_range || chr(10) || 'Output: ' || output_path;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- 3. 物理备份：pg_basebackup工具
-- ================================================

-- 3.1 基本物理备份命令
/*
# 基础物理备份
pg_basebackup -U postgres -h localhost -p 5432 -D /backup/base_$(date +%Y%m%d_%H%M%S) -Ft -z -P -v

# 进度显示的压缩备份
pg_basebackup -U postgres -h localhost -p 5432 -D /backup/base -Ft -z -P -v

# 原始格式备份
pg_basebackup -U postgres -h localhost -p 5432 -D /backup/raw_base -Fp -P -v
*/

-- 3.2 物理备份验证函数
CREATE OR REPLACE FUNCTION verify_physical_backup(backup_directory TEXT)
RETURNS TABLE(
    check_item TEXT,
    status TEXT,
    description TEXT
) AS $$
DECLARE
    pg_version TEXT;
    backup_version TEXT;
    wal_segment_size INTEGER;
BEGIN
    -- 检查PostgreSQL版本
    SELECT version() INTO pg_version;
    
    -- 检查备份目录
    -- 注意：这里使用模拟检查，实际需要检查文件系统
    
    RETURN QUERY VALUES
        ('PostgreSQL Version', 'INFO', pg_version),
        ('Backup Directory', 'CHECKING', backup_directory),
        ('WAL Archive', 'REQUIRED', 'WAL archiving must be enabled'),
        ('Backup Method', 'INFO', 'Use pg_basebackup for physical backup'),
        ('Recovery Testing', 'RECOMMENDED', 'Test recovery procedures regularly');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM verify_physical_backup('/backup/base_20240101');

-- ================================================
-- 4. 高级备份策略
-- ================================================

-- 4.1 分层备份策略
CREATE TABLE backup_strategy (
    strategy_id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100),
    retention_days INTEGER,
    backup_frequency VARCHAR(50),
    compression_level INTEGER DEFAULT 6,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO backup_strategy (strategy_name, retention_days, backup_frequency, compression_level)
VALUES 
    ('Hourly Incremental', 24, 'hourly', 3),
    ('Daily Full', 30, 'daily', 6),
    ('Weekly Archive', 90, 'weekly', 9),
    ('Monthly Archive', 365, 'monthly', 9);

-- 4.2 备份计划函数
CREATE OR REPLACE FUNCTION generate_backup_schedule()
RETURNS TABLE(
    backup_type VARCHAR(50),
    schedule_time TIME,
    retention_period TEXT,
    compression_level INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'incremental'::VARCHAR(50),
        '02:00:00'::TIME,
        '24 hours'::TEXT,
        3::INTEGER
    WHERE EXISTS (SELECT 1 FROM backup_strategy WHERE strategy_name = 'Hourly Incremental')
    
    UNION ALL
    
    SELECT 
        'full'::VARCHAR(50),
        '01:00:00'::TIME,
        '30 days'::TEXT,
        6::INTEGER
    WHERE EXISTS (SELECT 1 FROM backup_strategy WHERE strategy_name = 'Daily Full');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM generate_backup_schedule();

-- 4.3 备份历史记录
CREATE TABLE backup_history (
    backup_id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50),
    backup_size BIGINT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(20),
    file_path TEXT,
    error_message TEXT,
    operator VARCHAR(100)
);

-- 4.4 模拟备份记录函数
CREATE OR REPLACE FUNCTION record_backup_attempt(
    p_backup_type VARCHAR(50),
    p_file_path TEXT
)
RETURNS INTEGER AS $$
DECLARE
    backup_duration INTEGER := (random() * 300 + 60)::INTEGER; -- 1-5分钟
    backup_status VARCHAR(20) := CASE WHEN random() < 0.95 THEN 'SUCCESS' ELSE 'FAILED' END;
    backup_id INTEGER;
BEGIN
    INSERT INTO backup_history (
        backup_type,
        start_time,
        end_time,
        duration_seconds,
        status,
        file_path,
        operator
    ) VALUES (
        p_backup_type,
        CURRENT_TIMESTAMP - (backup_duration || ' seconds')::INTERVAL,
        CURRENT_TIMESTAMP,
        backup_duration,
        backup_status,
        p_file_path,
        'system'
    ) RETURNING backup_id INTO backup_id;
    
    RETURN backup_id;
END;
$$ LANGUAGE plpgsql;

-- 模拟备份记录
SELECT record_backup_attempt('full', '/backup/full_20240101.dump');
SELECT record_backup_attempt('incremental', '/backup/incremental_20240101.wal');
SELECT record_backup_attempt('incremental', '/backup/incremental_20240102.wal');

-- ================================================
-- 5. 备份验证和完整性检查
-- ================================================

-- 5.1 备份完整性检查函数
CREATE OR REPLACE FUNCTION validate_backup(backup_file_path TEXT)
RETURNS TABLE(
    validation_test VARCHAR(100),
    test_result VARCHAR(20),
    details TEXT
) AS $$
DECLARE
    file_size BIGINT;
    file_exists BOOLEAN := TRUE;
BEGIN
    -- 模拟文件检查
    file_size := (random() * 1000000000)::BIGINT; -- 模拟文件大小
    
    RETURN QUERY VALUES
        ('File Existence', 'PASS', 'Backup file exists and is accessible'),
        ('File Size Check', 
         CASE WHEN file_size > 0 THEN 'PASS' ELSE 'FAIL' END, 
         'File size: ' || file_size::TEXT || ' bytes'),
        ('Format Validation', 
         CASE WHEN random() < 0.99 THEN 'PASS' ELSE 'WARN' END, 
         'Backup format appears valid'),
        ('Checksum Verification', 
         CASE WHEN random() < 0.95 THEN 'PASS' ELSE 'WARN' END, 
         'File integrity checksum valid');
END;
$$ LANGUAGE plpgsql;

SELECT * FROM validate_backup('/backup/full_20240101.dump');

-- 5.2 备份恢复测试
CREATE OR REPLACE FUNCTION test_backup_recovery(backup_file_path TEXT)
RETURNS TABLE(
    test_step VARCHAR(100),
    step_status VARCHAR(20),
    execution_time_ms INTEGER
) AS $$
DECLARE
    steps TEXT[] := ARRAY[
        'Prepare recovery environment',
        'Stop PostgreSQL service',
        'Clean old data directory',
        'Restore base backup',
        'Configure recovery settings',
        'Start PostgreSQL service',
        'Verify database integrity',
        'Test basic operations'
    ];
    step TEXT;
    i INTEGER;
BEGIN
    FOR i IN 1..array_length(steps, 1) LOOP
        step := steps[i];
        
        RETURN QUERY SELECT 
            step,
            CASE WHEN random() < 0.9 THEN 'SUCCESS' ELSE 'FAILED' END,
            (random() * 1000 + 100)::INTEGER;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM test_backup_recovery('/backup/full_20240101.dump');

-- ================================================
-- 6. 备份监控和报警
-- ================================================

-- 6.1 备份状态检查
CREATE OR REPLACE FUNCTION get_backup_status()
RETURNS TABLE(
    metric_name VARCHAR(100),
    current_value TEXT,
    threshold_value TEXT,
    status VARCHAR(20)
) AS $$
DECLARE
    last_backup_time TIMESTAMP;
    backup_count_24h INTEGER;
    avg_backup_duration NUMERIC;
BEGIN
    -- 获取最近备份时间
    SELECT MAX(end_time) INTO last_backup_time 
    FROM backup_history WHERE status = 'SUCCESS';
    
    -- 获取24小时内备份数量
    SELECT COUNT(*) INTO backup_count_24h
    FROM backup_history 
    WHERE status = 'SUCCESS' 
      AND end_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours';
    
    -- 计算平均备份时长
    SELECT AVG(duration_seconds) INTO avg_backup_duration
    FROM backup_history
    WHERE status = 'SUCCESS'
      AND end_time >= CURRENT_TIMESTAMP - INTERVAL '7 days';
    
    RETURN QUERY VALUES
        ('Last Backup Time', 
         COALESCE(last_backup_time::TEXT, 'No successful backup'), 
         '24 hours ago', 
         CASE WHEN last_backup_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours' THEN 'GOOD' ELSE 'WARNING' END),
        ('Backup Count (24h)', 
         backup_count_24h::TEXT, 
         '1', 
         CASE WHEN backup_count_24h >= 1 THEN 'GOOD' ELSE 'CRITICAL' END),
        ('Average Duration', 
         COALESCE(avg_backup_duration::TEXT, 'N/A'), 
         '300 seconds', 
         CASE WHEN avg_backup_duration <= 300 THEN 'GOOD' ELSE 'WARNING' END);
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_backup_status();

-- 6.2 备份趋势分析
CREATE OR REPLACE FUNCTION analyze_backup_trends(days_back INTEGER DEFAULT 30)
RETURNS TABLE(
    backup_date DATE,
    total_backups INTEGER,
    successful_backups INTEGER,
    failed_backups INTEGER,
    avg_duration NUMERIC,
    total_data_gb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE_TRUNC('day', end_time)::DATE as backup_date,
        COUNT(*) as total_backups,
        COUNT(*) FILTER (WHERE status = 'SUCCESS') as successful_backups,
        COUNT(*) FILTER (WHERE status = 'FAILED') as failed_backups,
        AVG(duration_seconds) as avg_duration,
        (AVG(backup_size) / 1024.0 / 1024.0 / 1024.0)::NUMERIC(10,2) as total_data_gb
    FROM backup_history
    WHERE end_time >= CURRENT_DATE - (days_back || ' days')::INTERVAL
    GROUP BY DATE_TRUNC('day', end_time)
    ORDER BY backup_date;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM analyze_backup_trends(7);

-- ================================================
-- 7. 自动化备份脚本示例
-- ================================================

-- 7.1 创建备份作业函数
CREATE OR REPLACE FUNCTION create_backup_job(
    job_name VARCHAR(100),
    backup_type VARCHAR(50),
    schedule_cron TEXT,
    retention_days INTEGER
)
RETURNS BOOLEAN AS $$
BEGIN
    -- 这里只是演示，实际的cron作业需要在操作系统级别创建
    RAISE NOTICE 'Backup job created: %', job_name;
    RAISE NOTICE 'Type: %, Schedule: %, Retention: % days', backup_type, schedule_cron, retention_days;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 7.2 清理过期备份
CREATE OR REPLACE FUNCTION cleanup_expired_backups(retention_days INTEGER DEFAULT 30)
RETURNS TABLE(
    deleted_backup_id INTEGER,
    backup_date DATE,
    reason TEXT
) AS $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN 
        SELECT backup_id, end_time::DATE as backup_date
        FROM backup_history
        WHERE end_time < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL
          AND status = 'SUCCESS'
    LOOP
        -- 模拟删除操作
        RETURN QUERY SELECT 
            rec.backup_id,
            rec.backup_date,
            'Expired backup removed'::TEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM cleanup_expired_backups(7);

-- ================================================
-- 8. 备份最佳实践建议
-- ================================================

/*
备份策略最佳实践：

1. 备份频率
   - 数据库大小 < 10GB: 每日完整备份
   - 数据库大小 10-100GB: 每周完整备份 + 每日增量备份
   - 数据库大小 > 100GB: 每月完整备份 + 每周增量备份 + 每日差异备份

2. 存储策略
   - 本地存储：快速恢复
   - 网络存储：便于共享
   - 云存储：异地容灾
   - 多重备份：防止单点故障

3. 验证机制
   - 定期测试恢复流程
   - 验证备份文件完整性
   - 监控备份执行状态
   - 记录备份历史

4. 性能考虑
   - 避开业务高峰时段
   - 使用压缩减少存储空间
   - 并行备份提高效率
   - 合理配置缓存和内存

5. 安全措施
   - 加密备份文件
   - 限制访问权限
   - 定期更换备份密钥
   - 审计备份操作记录
*/

-- ================================================
-- 9. 实用备份脚本模板
-- ================================================

-- 9.1 备份信息查询
CREATE OR REPLACE FUNCTION get_backup_info()
RETURNS TABLE(
    database_name VARCHAR(100),
    database_size_gb NUMERIC,
    table_count INTEGER,
    last_backup_time TIMESTAMP,
    backup_recommendation TEXT
) AS $$
DECLARE
    db_size NUMERIC;
    last_backup TIMESTAMP;
BEGIN
    SELECT pg_database_size(current_database()) / 1024.0 / 1024.0 / 1024.0 INTO db_size;
    SELECT MAX(end_time) INTO last_backup FROM backup_history WHERE status = 'SUCCESS';
    
    RETURN QUERY
    SELECT 
        current_database()::VARCHAR(100),
        db_size::NUMERIC(10,2),
        (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public')::INTEGER,
        last_backup,
        CASE 
            WHEN db_size < 10 THEN 'Daily full backup recommended'
            WHEN db_size < 100 THEN 'Weekly full + daily incremental recommended'
            ELSE 'Monthly full + weekly incremental recommended'
        END::TEXT;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_backup_info();

-- ================================================
-- 10. 清理环境（可选）
-- ================================================

-- 清理测试环境
/*
DROP FUNCTION IF EXISTS perform_logical_backup(TEXT, TEXT);
DROP FUNCTION IF EXISTS create_incremental_backup(TEXT, TEXT);
DROP FUNCTION IF EXISTS verify_physical_backup(TEXT);
DROP FUNCTION IF EXISTS generate_backup_schedule();
DROP FUNCTION IF EXISTS record_backup_attempt(VARCHAR, TEXT);
DROP FUNCTION IF EXISTS validate_backup(TEXT);
DROP FUNCTION IF EXISTS test_backup_recovery(TEXT);
DROP FUNCTION IF EXISTS get_backup_status();
DROP FUNCTION IF EXISTS analyze_backup_trends(INTEGER);
DROP FUNCTION IF EXISTS create_backup_job(VARCHAR, VARCHAR, TEXT, INTEGER);
DROP FUNCTION IF EXISTS cleanup_expired_backups(INTEGER);
DROP FUNCTION IF EXISTS get_backup_info();

DROP TABLE IF EXISTS backup_strategy CASCADE;
DROP TABLE IF EXISTS backup_history CASCADE;
DROP TABLE IF EXISTS demo_products CASCADE;
DROP TABLE IF EXISTS demo_orders CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
*/
