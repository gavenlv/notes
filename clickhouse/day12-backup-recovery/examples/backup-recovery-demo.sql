-- ClickHouse Day 12: 备份恢复实践示例
-- 演示数据备份、恢复和版本升级的各种方法

-- =====================================
-- 1. 准备测试数据
-- =====================================

-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS backup_demo;
USE backup_demo;

-- 创建用户表
CREATE TABLE users (
    id UInt64,
    username String,
    email String,
    created_at DateTime DEFAULT now(),
    last_login DateTime,
    is_active UInt8 DEFAULT 1
) ENGINE = MergeTree()
ORDER BY id
PARTITION BY toYYYYMM(created_at);

-- 创建订单表
CREATE TABLE orders (
    order_id UInt64,
    user_id UInt64,
    product_name String,
    quantity UInt32,
    price Decimal64(2),
    order_date DateTime DEFAULT now(),
    status Enum8('pending' = 1, 'processing' = 2, 'shipped' = 3, 'delivered' = 4, 'cancelled' = 5)
) ENGINE = MergeTree()
ORDER BY (user_id, order_date)
PARTITION BY toYYYYMM(order_date);

-- 创建日志表
CREATE TABLE user_activity_log (
    log_id UInt64,
    user_id UInt64,
    action String,
    ip_address IPv4,
    user_agent String,
    timestamp DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp)
PARTITION BY toYYYYMMDD(timestamp)
TTL timestamp + INTERVAL 90 DAY;

-- 插入测试数据
INSERT INTO users (id, username, email, created_at, last_login, is_active)
SELECT 
    number as id,
    concat('user_', toString(number)) as username,
    concat('user_', toString(number), '@example.com') as email,
    now() - INTERVAL (number % 365) DAY as created_at,
    now() - INTERVAL (number % 30) DAY as last_login,
    if(number % 10 = 0, 0, 1) as is_active
FROM numbers(10000);

INSERT INTO orders (order_id, user_id, product_name, quantity, price, order_date, status)
SELECT 
    number as order_id,
    (number % 10000) + 1 as user_id,
    concat('Product_', toString(number % 100)) as product_name,
    (number % 5) + 1 as quantity,
    round((number % 1000) + 10.99, 2) as price,
    now() - INTERVAL (number % 180) DAY as order_date,
    (['pending', 'processing', 'shipped', 'delivered', 'cancelled'])[number % 5 + 1] as status
FROM numbers(50000);

INSERT INTO user_activity_log (log_id, user_id, action, ip_address, user_agent, timestamp)
SELECT 
    number as log_id,
    (number % 10000) + 1 as user_id,
    (['login', 'logout', 'view_product', 'add_to_cart', 'checkout'])[number % 5 + 1] as action,
    toIPv4(concat(toString((number % 255) + 1), '.', toString((number % 255) + 1), '.', toString((number % 255) + 1), '.', toString((number % 255) + 1))) as ip_address,
    concat('Mozilla/5.0 (compatible; Bot/', toString(number % 100), ')') as user_agent,
    now() - INTERVAL (number % 30) DAY as timestamp
FROM numbers(100000);

-- 验证数据
SELECT 'users' as table_name, count() as row_count FROM users
UNION ALL
SELECT 'orders' as table_name, count() as row_count FROM orders  
UNION ALL
SELECT 'user_activity_log' as table_name, count() as row_count FROM user_activity_log;

-- =====================================
-- 2. 内置备份功能演示（ClickHouse 22.8+）
-- =====================================

-- 注意：以下命令需要在支持BACKUP/RESTORE的ClickHouse版本中执行

-- 备份单个表
-- BACKUP TABLE backup_demo.users TO Disk('default', 'users_backup_20240101.zip');

-- 备份多个表
-- BACKUP TABLE backup_demo.users, backup_demo.orders TO Disk('default', 'multi_table_backup.zip');

-- 备份整个数据库
-- BACKUP DATABASE backup_demo TO Disk('default', 'database_backup_20240101.zip');

-- 增量备份（基于之前的备份）
-- BACKUP DATABASE backup_demo TO Disk('default', 'incremental_backup.zip') 
-- SETTINGS base_backup = Disk('default', 'database_backup_20240101.zip');

-- 异步备份
-- BACKUP DATABASE backup_demo TO Disk('default', 'async_backup.zip') ASYNC;

-- 查看备份进度
-- SELECT * FROM system.backups;

-- =====================================
-- 3. 逻辑备份演示
-- =====================================

-- 导出表结构
-- 在命令行执行：
-- clickhouse-client --query="SHOW CREATE TABLE backup_demo.users" > users_schema.sql
-- clickhouse-client --query="SHOW CREATE TABLE backup_demo.orders" > orders_schema.sql

-- 导出数据（Native格式，推荐）
-- clickhouse-client --query="SELECT * FROM backup_demo.users FORMAT Native" > users_data.native

-- 导出数据（CSV格式）
-- clickhouse-client --query="SELECT * FROM backup_demo.users FORMAT CSV" > users_data.csv

-- 导出数据（压缩格式）
-- clickhouse-client --query="SELECT * FROM backup_demo.users FORMAT Native" | gzip > users_data.native.gz

-- 导出特定分区的数据
-- clickhouse-client --query="SELECT * FROM backup_demo.orders WHERE toYYYYMM(order_date) = 202401 FORMAT Native" > orders_202401.native

-- 创建备份用的视图（用于数据验证）
CREATE VIEW backup_summary AS
SELECT 
    'Full Backup' as backup_type,
    now() as backup_time,
    (SELECT count() FROM users) as users_count,
    (SELECT count() FROM orders) as orders_count,
    (SELECT count() FROM user_activity_log) as logs_count,
    (SELECT formatReadableSize(sum(bytes_on_disk)) FROM system.parts WHERE database = 'backup_demo') as total_size;

-- 查看备份摘要
SELECT * FROM backup_summary;

-- =====================================
-- 4. 数据恢复演示
-- =====================================

-- 创建恢复测试数据库
CREATE DATABASE IF NOT EXISTS restore_demo;

-- 恢复表结构示例（需要先有备份文件）
-- 在命令行执行：
-- clickhouse-client --database=restore_demo < users_schema.sql

-- 恢复数据示例
-- clickhouse-client --query="INSERT INTO restore_demo.users FORMAT Native" < users_data.native

-- 使用内置RESTORE命令恢复（ClickHouse 22.8+）
-- RESTORE TABLE backup_demo.users AS restore_demo.users_restored FROM Disk('default', 'users_backup.zip');

-- 恢复整个数据库
-- RESTORE DATABASE backup_demo AS restore_demo FROM Disk('default', 'database_backup.zip');

-- 增量恢复
-- RESTORE DATABASE backup_demo AS restore_demo FROM Disk('default', 'incremental_backup.zip');

-- =====================================
-- 5. 复制表备份演示
-- =====================================

-- 创建复制表作为备份（需要ZooKeeper）
-- 注意：这需要配置ZooKeeper或ClickHouse Keeper

/*
CREATE TABLE users_replica
(
    id UInt64,
    username String,
    email String,
    created_at DateTime DEFAULT now(),
    last_login DateTime,
    is_active UInt8 DEFAULT 1
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/backup_demo/users_replica', 'replica1')
ORDER BY id
PARTITION BY toYYYYMM(created_at);

-- 从主表复制数据到复制表
INSERT INTO users_replica SELECT * FROM users;

-- 创建物化视图实现实时同步
CREATE MATERIALIZED VIEW users_backup_sync TO users_replica AS
SELECT * FROM users;
*/

-- =====================================
-- 6. 备份验证和测试
-- =====================================

-- 创建备份验证函数
CREATE OR REPLACE FUNCTION validateBackup AS (table_name) -> (
    SELECT 
        table_name,
        count() as row_count,
        uniq(id) as unique_ids,
        min(created_at) as min_date,
        max(created_at) as max_date,
        formatReadableSize(sum(bytes_on_disk)) as size_on_disk
    FROM system.parts 
    WHERE table = table_name AND database = 'backup_demo'
    GROUP BY table_name
);

-- 验证原始数据
SELECT 'Original Data Validation' as check_type;
SELECT validateBackup('users');
SELECT validateBackup('orders');

-- 数据完整性检查
SELECT 'Data Integrity Check' as check_type;

-- 检查用户数据完整性
SELECT 
    'users_integrity' as check_name,
    count() as total_users,
    count(DISTINCT id) as unique_users,
    countIf(email LIKE '%@%') as valid_emails,
    countIf(is_active IN (0, 1)) as valid_status
FROM users;

-- 检查订单数据完整性
SELECT 
    'orders_integrity' as check_name,
    count() as total_orders,
    count(DISTINCT order_id) as unique_orders,
    countIf(price > 0) as valid_prices,
    countIf(user_id > 0) as valid_user_refs
FROM orders;

-- 检查数据关联性
SELECT 
    'data_relationships' as check_name,
    count(DISTINCT o.user_id) as users_with_orders,
    count(DISTINCT u.id) as total_users,
    round(count(DISTINCT o.user_id) * 100.0 / count(DISTINCT u.id), 2) as user_order_ratio
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- =====================================
-- 7. 模拟数据丢失和恢复
-- =====================================

-- 创建数据丢失模拟场景
CREATE DATABASE IF NOT EXISTS disaster_simulation;

-- 复制原始数据到模拟环境
CREATE TABLE disaster_simulation.users AS backup_demo.users;
CREATE TABLE disaster_simulation.orders AS backup_demo.orders;

INSERT INTO disaster_simulation.users SELECT * FROM backup_demo.users;
INSERT INTO disaster_simulation.orders SELECT * FROM backup_demo.orders;

-- 验证模拟环境数据
SELECT 'Disaster Simulation Environment' as info;
SELECT 'users' as table_name, count() as row_count FROM disaster_simulation.users
UNION ALL
SELECT 'orders' as table_name, count() as row_count FROM disaster_simulation.orders;

-- 模拟部分数据丢失
ALTER TABLE disaster_simulation.users DELETE WHERE id % 100 = 0;
ALTER TABLE disaster_simulation.orders DELETE WHERE order_id % 1000 = 0;

-- 检查数据丢失情况
SELECT 'After Data Loss Simulation' as info;
SELECT 'users' as table_name, count() as row_count FROM disaster_simulation.users
UNION ALL
SELECT 'orders' as table_name, count() as row_count FROM disaster_simulation.orders;

-- 模拟恢复过程（从备份数据恢复）
-- 在实际环境中，这里会从备份文件恢复
TRUNCATE TABLE disaster_simulation.users;
TRUNCATE TABLE disaster_simulation.orders;

INSERT INTO disaster_simulation.users SELECT * FROM backup_demo.users;
INSERT INTO disaster_simulation.orders SELECT * FROM backup_demo.orders;

-- 验证恢复结果
SELECT 'After Recovery Simulation' as info;
SELECT 'users' as table_name, count() as row_count FROM disaster_simulation.users
UNION ALL
SELECT 'orders' as table_name, count() as row_count FROM disaster_simulation.orders;

-- =====================================
-- 8. 版本兼容性检查
-- =====================================

-- 检查当前版本信息
SELECT 'Version Information' as info;
SELECT version() as clickhouse_version;
SELECT name, value FROM system.build_options WHERE name IN ('CXX_FLAGS', 'BUILD_TYPE');

-- 检查表引擎兼容性
SELECT 'Table Engine Compatibility' as info;
SELECT 
    database,
    table,
    engine,
    engine_full,
    CASE 
        WHEN engine IN ('Log', 'TinyLog', 'StripeLog') THEN 'Legacy - Consider Migration'
        WHEN engine LIKE '%MergeTree%' THEN 'Modern - Compatible'
        WHEN engine LIKE '%Replicated%' THEN 'Replicated - Check Configuration'
        ELSE 'Other - Review Needed'
    END as compatibility_status
FROM system.tables
WHERE database IN ('backup_demo', 'disaster_simulation')
ORDER BY database, table;

-- 检查系统设置变更
SELECT 'Modified Settings' as info;
SELECT name, value, default, changed, description
FROM system.settings 
WHERE changed = 1
ORDER BY name;

-- 检查可能需要迁移的功能
SELECT 'Deprecated Features Check' as info;
SELECT 
    database,
    table,
    engine,
    'Check for deprecated engine features' as recommendation
FROM system.tables
WHERE engine IN ('Log', 'TinyLog', 'StripeLog', 'Memory')
AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA');

-- =====================================
-- 9. 备份性能测试
-- =====================================

-- 创建性能测试表
CREATE TABLE backup_performance_test (
    id UInt64,
    data String,
    timestamp DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

-- 插入大量测试数据
INSERT INTO backup_performance_test (id, data)
SELECT 
    number as id,
    concat('test_data_', toString(number), '_', toString(rand())) as data
FROM numbers(1000000);

-- 测试导出性能
SELECT 'Backup Performance Test' as info;
SELECT 
    'backup_performance_test' as table_name,
    count() as total_rows,
    formatReadableSize(sum(bytes_on_disk)) as size_on_disk,
    formatReadableSize(sum(bytes)) as uncompressed_size
FROM system.parts
WHERE table = 'backup_performance_test' AND database = 'backup_demo';

-- 清理性能测试数据
DROP TABLE IF EXISTS backup_performance_test;

-- =====================================
-- 10. 备份策略推荐
-- =====================================

-- 创建备份策略视图
CREATE VIEW backup_strategy_recommendations AS
SELECT 
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as table_size,
    count() as part_count,
    max(modification_time) as last_modified,
    CASE 
        WHEN sum(bytes_on_disk) > 10*1024*1024*1024 THEN 'Large Table - Daily Incremental + Weekly Full'
        WHEN sum(bytes_on_disk) > 1*1024*1024*1024 THEN 'Medium Table - Daily Full Backup'
        WHEN sum(bytes_on_disk) > 100*1024*1024 THEN 'Small Table - Weekly Full Backup'
        ELSE 'Tiny Table - Monthly Full Backup'
    END as recommended_strategy,
    CASE 
        WHEN engine LIKE '%Replicated%' THEN 'Use Replication for HA'
        WHEN engine LIKE '%MergeTree%' THEN 'Standard Backup Strategy'
        ELSE 'Custom Backup Strategy Needed'
    END as backup_method
FROM system.parts p
JOIN system.tables t ON p.database = t.database AND p.table = t.table
WHERE p.database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
GROUP BY database, table, engine
ORDER BY sum(bytes_on_disk) DESC;

-- 查看备份策略推荐
SELECT * FROM backup_strategy_recommendations;

-- =====================================
-- 11. 清理和总结
-- =====================================

-- 查看创建的所有对象
SELECT 'Created Objects Summary' as info;
SELECT 
    database,
    count() as table_count,
    formatReadableSize(sum(bytes_on_disk)) as total_size
FROM system.parts
WHERE database IN ('backup_demo', 'restore_demo', 'disaster_simulation')
GROUP BY database
ORDER BY database;

-- 备份恢复最佳实践总结
SELECT 'Backup Recovery Best Practices' as summary;
SELECT '1. Regular automated backups with retention policy' as practice
UNION ALL SELECT '2. Test restore procedures regularly'
UNION ALL SELECT '3. Use multiple backup types (full, incremental, differential)'
UNION ALL SELECT '4. Store backups in multiple locations'
UNION ALL SELECT '5. Encrypt sensitive backup data'
UNION ALL SELECT '6. Monitor backup job success/failure'
UNION ALL SELECT '7. Document recovery procedures'
UNION ALL SELECT '8. Test disaster recovery scenarios'
UNION ALL SELECT '9. Validate backup integrity'
UNION ALL SELECT '10. Plan for version compatibility during upgrades';

-- 可选：清理演示数据
-- DROP DATABASE IF EXISTS backup_demo;
-- DROP DATABASE IF EXISTS restore_demo;
-- DROP DATABASE IF EXISTS disaster_simulation; 