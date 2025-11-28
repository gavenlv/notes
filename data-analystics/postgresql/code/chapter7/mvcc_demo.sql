-- PostgreSQL教程第7章：事务管理与并发控制 - MVCC演示

-- 创建测试表
CREATE TABLE IF NOT EXISTS bank_accounts (
    account_id SERIAL PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_holder VARCHAR(100) NOT NULL,
    balance DECIMAL(15,2) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清空表并插入测试数据
TRUNCATE bank_accounts CASCADE;
INSERT INTO bank_accounts (account_number, account_holder, balance) VALUES
('ACC001', '张三', 10000.00),
('ACC002', '李四', 5000.00),
('ACC003', '王五', 8000.00);

TRUNCATE inventory CASCADE;
INSERT INTO inventory (product_name, quantity, version) VALUES
('iPhone 14', 100, 1),
('MacBook Pro', 50, 1),
('iPad', 75, 1);

-- 1. MVCC基本概念演示

-- 1.1 查看事务隔离级别
SHOW transaction_isolation;

-- 1.2 查看当前事务ID
SELECT txid_current() as current_transaction_id;

-- 1.3 查看表的多版本信息
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- 2. 事务隔离级别的MVCC行为

-- 2.1 READ COMMITTED（读已提交）- 默认级别
-- 这个级别下，每个查询都会看到已提交的数据
/*
-- 会话1：
BEGIN ISOLATION LEVEL READ COMMITTED;
-- 查询账户余额
SELECT account_holder, balance FROM bank_accounts WHERE account_id = 1;
-- 输出: 张三, 10000.00

-- 会话2：
BEGIN ISOLATION LEVEL READ COMMITTED;
UPDATE bank_accounts SET balance = balance - 1000 WHERE account_id = 1;
COMMIT;

-- 会话1再次查询：
SELECT account_holder, balance FROM bank_accounts WHERE account_id = 1;
-- 输出: 张三, 9000.00 （看到已提交的更改）
COMMIT;
*/

-- 2.2 REPEATABLE READ（可重复读）
-- 这个级别下，整个事务期间看到的都是一致的数据快照
/*
-- 会话1：
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT account_holder, balance FROM bank_accounts WHERE account_id = 1;
-- 输出: 张三, 10000.00

-- 会话2：
UPDATE bank_accounts SET balance = balance - 1000 WHERE account_id = 1;
COMMIT;

-- 会话1再次查询：
SELECT account_holder, balance FROM bank_accounts WHERE account_id = 1;
-- 输出: 张三, 10000.00 （看不到更改，保持快照一致性）
COMMIT;
*/

-- 2.3 SERIALIZABLE（串行化）
-- 最高隔离级别，提供完全的事务隔离
/*
-- 会话1：
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- 执行一些查询
SELECT COUNT(*) FROM bank_accounts;
-- 会话2尝试修改数据时会检测到潜在冲突
COMMIT;
*/

-- 3. 脏读、不可重复读和幻读演示

-- 3.1 脏读演示（PostgreSQL中不会发生）
/*
-- 会话1：
BEGIN;
UPDATE bank_accounts SET balance = balance - 500 WHERE account_id = 1;
-- 在这个事务中，更改还未提交

-- 会话2：
BEGIN;
-- 在PostgreSQL的默认READ COMMITTED级别下，
-- 这个SELECT不会看到会话1未提交的更改
-- 脏读被防止
SELECT balance FROM bank_accounts WHERE account_id = 1;
COMMIT;

-- 会话1：
COMMIT; -- 提交更改
*/

-- 3.2 不可重复读演示
/*
-- 会话1：
BEGIN ISOLATION LEVEL READ COMMITTED;
-- 第一次查询
SELECT balance FROM bank_accounts WHERE account_id = 1;
-- 输出: 10000.00

-- 会话2：
BEGIN;
UPDATE bank_accounts SET balance = balance + 1000 WHERE account_id = 1;
COMMIT;

-- 会话1第二次查询 - 能看到更改（不可重复读）
SELECT balance FROM bank_accounts WHERE account_id = 1;
-- 输出: 11000.00
COMMIT;
*/

-- 3.3 幻读演示
/*
-- 会话1：
BEGIN ISOLATION LEVEL READ COMMITTED;
-- 查询大于5000的账户数量
SELECT COUNT(*) FROM bank_accounts WHERE balance > 5000;
-- 输出: 2

-- 会话2：
BEGIN;
INSERT INTO bank_accounts (account_number, account_holder, balance) VALUES ('ACC004', '赵六', 6000.00);
COMMIT;

-- 会话1再次查询 - 可能看到新行（幻读）
SELECT COUNT(*) FROM bank_accounts WHERE balance > 5000;
-- 输出: 3
COMMIT;
*/

-- 4. 快照隔离演示

-- 4.1 查看事务快照信息
/*
-- 在事务中执行以下查询
SELECT 
    txid_current() as current_xid,
    txid_current_snapshot() as current_snapshot,
    pg_snapshot_xip(txid_current_snapshot()) as active_transactions;

-- 查看快照内容
SELECT 
    s::text as snapshot_info
FROM pg_catalog.pg_split_snapshot(txid_current_snapshot()) s;
*/

-- 4.2 MVCC版本链演示
/*
-- 插入一行数据并查看其版本信息
BEGIN;
INSERT INTO bank_accounts (account_number, account_holder, balance) VALUES ('ACC004', '赵六', 6000.00);

-- 查看表中的元组信息
SELECT 
    ctid, -- 物理位置
    xmin, -- 插入该行的事务ID
    xmax, -- 删除或更新该行的事务ID
    cmin, -- 命令序列号（在事务中）
    cmax,
    account_holder,
    balance
FROM bank_accounts 
WHERE account_number = 'ACC004';

COMMIT;
*/

-- 5. 版本号和可见性规则

-- 5.1 查看行版本信息
-- 插入测试数据
INSERT INTO bank_accounts (account_number, account_holder, balance) VALUES ('ACC004', '赵六', 6000.00);

-- 查看行的版本控制信息
SELECT 
    ctid as physical_location,
    xmin as insert_xid,
    xmax as delete_update_xid,
    cmin as command_sequence,
    cmax as command_sequence_max,
    account_holder,
    balance,
    CASE 
        WHEN xmax = 0 THEN 'Active'
        WHEN xmax IN (SELECT txid FROM pg_prepared_xacts) THEN 'Prepared'
        ELSE 'Deleted/Updated'
    END as row_status
FROM bank_accounts 
ORDER BY account_id;

-- 5.2 查看可见性规则
/*
-- 事务1：查看某个时刻的数据快照
BEGIN;
-- 设置事务时间戳
SELECT clock_timestamp() as tx_start_time;
SELECT * FROM bank_accounts WHERE account_id = 1;
COMMIT;

-- 事务2：修改数据
BEGIN;
UPDATE bank_accounts SET balance = balance - 500 WHERE account_id = 1;
SELECT clock_timestamp() as update_time;
COMMIT;

-- 事务3：在事务1的时间戳之后查看数据
BEGIN;
-- 这个事务的可见性基于事务1的时间戳
SELECT * FROM bank_accounts WHERE account_id = 1;
COMMIT;
*/

-- 6. MVCC性能优化演示

-- 6.1 清理死亡元组
VACUUM ANALYZE bank_accounts;

-- 6.2 查看表统计信息
SELECT 
    relname as table_name,
    n_tup_ins as total_inserts,
    n_tup_upd as total_updates,
    n_tup_del as total_deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
ORDER BY relname;

-- 6.3 查看膨胀情况
SELECT 
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    ROUND(n_dead_tup::numeric / GREATEST(n_live_tup, 1) * 100, 2) as dead_tuple_percentage
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY dead_tuple_percentage DESC;

-- 7. 并发控制和锁配合

-- 7.1 行级锁和MVCC
/*
-- 事务1：锁定特定行
BEGIN;
SELECT balance FROM bank_accounts WHERE account_id = 1 FOR UPDATE;
-- 这会锁定该行，其他事务不能修改它
-- 但其他事务仍然可以读取它（基于MVCC）

-- 事务2：
BEGIN;
-- 这个SELECT不会阻塞，因为MVCC提供了一致性读取
SELECT balance FROM bank_accounts WHERE account_id = 1;
-- 但更新操作会阻塞
-- UPDATE bank_accounts SET balance = balance + 100 WHERE account_id = 1; -- 这会阻塞
COMMIT;

-- 事务1：
COMMIT;
*/

-- 7.2 乐观并发控制
/*
-- 模拟基于版本的并发控制
BEGIN;
-- 读取当前版本号
SELECT quantity, version FROM inventory WHERE product_id = 1;
-- 假设版本是1，现在要更新

-- 检查版本是否还是1
DO $$
DECLARE
    current_version INTEGER;
BEGIN
    -- 读取当前版本
    SELECT version INTO current_version 
    FROM inventory WHERE product_id = 1;
    
    IF current_version = 1 THEN
        -- 版本匹配，可以更新
        UPDATE inventory 
        SET quantity = quantity + 10, 
            version = version + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = 1;
    ELSE
        RAISE NOTICE 'Version mismatch, retry needed';
    END IF;
END $$;
COMMIT;
*/

-- 8. 可见性规则详细分析

-- 8.1 查看事务ID的可见性
/*
-- 查看所有事务的状态
SELECT 
    txid,
    state,
    query,
    query_start,
    xact_start,
    lock_wait_start,
    state_change
FROM pg_stat_activity 
WHERE backend_xid IS NOT NULL
ORDER BY xact_start;
*/

-- 8.2 检查行版本的可见性
/*
-- 创建函数来检查行的可见性
CREATE OR REPLACE FUNCTION check_row_visibility(
    table_name text,
    row_ctid text,
    observer_xid bigint DEFAULT txid_current()
) RETURNS text AS $$
DECLARE
    tuple_info record;
    result text;
BEGIN
    -- 获取元组信息
    EXECUTE format('SELECT xmin, xmax, cmin, cmax FROM %s WHERE ctid = $1', table_name)
    INTO tuple_info
    USING row_ctid;
    
    -- 检查可见性规则
    IF tuple_info.xmax = 0 THEN
        -- 行未被删除
        IF tuple_info.xmin <= observer_xid THEN
            -- 插入事务在观察事务之前开始
            result := 'Visible';
        ELSE
            result := 'Invisible';
        END IF;
    ELSE
        -- 行被删除或更新
        IF tuple_info.xmax > observer_xid THEN
            -- 删除事务还未提交
            result := 'Visible (deleted by future transaction)';
        ELSE
            result := 'Invisible (deleted by committed transaction)';
        END IF;
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
*/

-- 9. MVCC的优缺点

-- 9.1 MVCC的优点：
-- - 读写不冲突，提高并发性能
-- - 不需要锁读操作
-- - 提供一致性快照

-- 9.2 MVCC的缺点：
-- - 需要存储多个版本的行，造成空间膨胀
-- - 需要定期清理死亡元组（VACUUM）
-- - 长事务可能导致膨胀问题

-- 10. 实际应用场景

-- 10.1 银行转账模拟
/*
-- 转账操作演示MVCC如何保证一致性
-- 账户A转给账户B 500元

-- 开始事务
BEGIN;
-- 检查源账户余额（使用行锁防止并发修改）
SELECT balance FROM bank_accounts WHERE account_id = 1 FOR UPDATE;
-- 输出当前余额：10000.00

-- 执行扣款（在这个事务中看到的是一致的余额）
UPDATE bank_accounts 
SET balance = balance - 500, 
    last_updated = CURRENT_TIMESTAMP 
WHERE account_id = 1;

-- 检查目标账户（同样锁定）
SELECT balance FROM bank_accounts WHERE account_id = 2 FOR UPDATE;
-- 输出当前余额：5000.00

-- 执行存款
UPDATE bank_accounts 
SET balance = balance + 500, 
    last_updated = CURRENT_TIMESTAMP 
WHERE account_id = 2;

-- 检查转账后余额
SELECT balance FROM bank_accounts WHERE account_id = 1;
-- 输出：9500.00
SELECT balance FROM bank_accounts WHERE account_id = 2;
-- 输出：5500.00

-- 提交事务
COMMIT;
*/

-- 10.2 库存管理演示
/*
-- 库存扣减操作
BEGIN;
-- 锁定要扣减库存的产品
SELECT quantity FROM inventory WHERE product_id = 1 FOR UPDATE;

-- 检查库存是否充足
DO $$
DECLARE
    current_qty INTEGER;
    new_version INTEGER;
BEGIN
    SELECT quantity, version INTO current_qty, new_version
    FROM inventory WHERE product_id = 1;
    
    IF current_qty >= 10 THEN
        -- 库存充足，执行扣减
        UPDATE inventory 
        SET quantity = quantity - 10,
            version = version + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = 1;
    ELSE
        RAISE NOTICE 'Insufficient inventory. Current: %, Required: 10', current_qty;
    END IF;
END $$;

COMMIT;
*/

-- 11. MVCC监控和诊断

-- 11.1 查看活跃事务
SELECT 
    pid,
    usename,
    client_addr,
    backend_xid,
    backend_xmin,
    query_start,
    state,
    query
FROM pg_stat_activity 
WHERE backend_xid IS NOT NULL
ORDER BY query_start;

-- 11.2 查看准备中的事务
SELECT 
    gid as transaction_id,
    prepared,
    owner,
    database
FROM pg_prepared_xacts
ORDER BY prepared;

-- 11.3 检查长事务
SELECT 
    pid,
    usename,
    client_addr,
    query_start,
    now() - query_start as duration,
    state,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity 
WHERE state = 'active' 
  AND now() - query_start > interval '5 minutes'
ORDER BY duration DESC;

-- 12. MVCC优化建议

-- 12.1 避免长事务
/*
-- 检查长时间运行的事务
SELECT 
    pid,
    usename,
    now() - xact_start as transaction_duration,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND now() - xact_start > interval '10 minutes'
ORDER BY transaction_duration DESC;
*/

-- 12.2 定期清理
-- 建议的清理计划
SELECT 
    'VACUUM ANALYZE bank_accounts;' as recommended_action,
    n_dead_tup,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables 
WHERE relname = 'bank_accounts';

-- 12.3 监控膨胀
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(oid)) as total_size,
    pg_size_pretty(pg_relation_size(oid)) as table_size,
    pg_size_pretty(pg_total_relation_size(oid) - pg_relation_size(oid)) as index_size,
    n_dead_tup,
    ROUND(n_dead_tup::numeric / GREATEST(n_live_tup, 1) * 100, 2) as dead_ratio
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_stat_user_tables t ON t.relname = c.relname
WHERE n.nspname = 'public'
ORDER BY dead_ratio DESC;

-- 13. 清理测试数据
-- 注意：在实际环境中不要随意删除数据
-- 这里只清理测试表
/*
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS bank_accounts CASCADE;
DROP FUNCTION IF EXISTS check_row_visibility(text, text, bigint);
*/