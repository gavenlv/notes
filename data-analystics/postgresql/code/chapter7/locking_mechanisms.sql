-- PostgreSQL教程第7章：事务管理与并发控制 - 锁机制演示

-- 创建测试表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    stock_quantity INTEGER DEFAULT 0,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending'
);

-- 清空表并插入测试数据
TRUNCATE products CASCADE;
INSERT INTO products (name, price, stock_quantity, category) VALUES
('iPhone 14', 7999.00, 100, 'Mobile'),
('MacBook Pro', 19999.00, 50, 'Computer'),
('iPad', 3999.00, 75, 'Tablet'),
('AirPods', 1999.00, 200, 'Audio'),
('Apple Watch', 2999.00, 150, 'Wearable');

-- 1. 锁的基本概念

-- 1.1 查看当前持有的锁
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name,
    virtualxid as virtual_transaction,
    pid,
    usename,
    client_addr
FROM pg_locks
WHERE pid = pg_backend_pid()
ORDER BY locktype, mode;

-- 1.2 查看所有锁信息
SELECT 
    schemaname,
    tablename,
    table_mode,
    locktype,
    mode,
    granted,
    pid,
    usename
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
JOIN pg_class c ON l.relation = c.oid
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE schemaname = 'public'
ORDER BY tablename, locktype;

-- 2. 表级锁演示

-- 2.1 ACCESS SHARE 锁（访问共享锁）
-- 发生在SELECT查询时
BEGIN;
SELECT * FROM products WHERE id = 1;
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
COMMIT;

-- 2.2 ROW SHARE 锁（行共享锁）
-- 发生在SELECT FOR UPDATE、SELECT FOR SHARE时
BEGIN;
SELECT * FROM products FOR UPDATE;
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
COMMIT;

-- 2.3 ROW EXCLUSIVE 锁（行排他锁）
-- 发生在INSERT、UPDATE、DELETE时
BEGIN;
UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id = 1;
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
COMMIT;

-- 2.4 SHARE UPDATE EXCLUSIVE 锁
-- 发生在ALTER TABLE、CREATE INDEX等操作时
BEGIN;
CREATE INDEX idx_products_category_price ON products (category, price);
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
COMMIT;

-- 2.5 SHARE 锁（共享锁）
-- 发生在CREATE INDEX时（表级）
BEGIN;
CREATE INDEX CONCURRENTLY idx_products_name ON products (name);
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
COMMIT;

-- 2.6 SHARE ROW EXCLUSIVE 锁
-- 发生在ALTER TABLE等操作时
BEGIN;
ALTER TABLE products ADD COLUMN last_sold_date DATE;
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
COMMIT;

-- 2.7 EXCLUSIVE 锁（排他锁）
-- 很少直接使用
-- 可以通过LOCK TABLE table_name EXCLUSIVE获得

-- 2.8 ACCESS EXCLUSIVE 锁（访问排他锁）
-- 发生在DROP TABLE、TRUNCATE等操作时
BEGIN;
ALTER TABLE products RENAME TO products_backup;
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid();
COMMIT;

-- 恢复表名
ALTER TABLE products_backup RENAME TO products;

-- 3. 行级锁演示

-- 3.1 FOR UPDATE 锁
BEGIN;
-- 锁定特定行进行更新
SELECT * FROM products WHERE id = 1 FOR UPDATE;
-- 查看行锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name,
    page,
    virtualtransaction,
    pid,
    usename
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
-- 更新并提交
UPDATE products SET stock_quantity = 99 WHERE id = 1;
COMMIT;

-- 3.2 FOR SHARE 锁
BEGIN;
-- 锁定行用于共享读取
SELECT * FROM products WHERE category = 'Mobile' FOR SHARE;
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products';
COMMIT;

-- 3.3 FOR NO KEY UPDATE 锁
BEGIN;
SELECT * FROM products WHERE id = 1 FOR NO KEY UPDATE;
COMMIT;

-- 3.4 FOR KEY SHARE 锁
BEGIN;
SELECT * FROM products WHERE id = 1 FOR KEY SHARE;
COMMIT;

-- 4. 锁兼容性矩阵演示

-- 创建冲突测试表
CREATE TABLE IF NOT EXISTS lock_test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    value INTEGER
);

INSERT INTO lock_test (name, value) VALUES ('test', 1);

-- 测试锁兼容性
-- 事务1：获得ACCESS SHARE锁
BEGIN;
SELECT * FROM lock_test;
-- 查看锁信息
SELECT 
    locktype,
    mode,
    granted,
    pid
FROM pg_locks
WHERE relation::regclass::text = 'lock_test'
ORDER BY granted;

-- 事务2：尝试获得EXCLUSIVE锁（会冲突）
-- 这会阻塞，因为事务1持有ACCESS SHARE锁
/*
BEGIN;
LOCK TABLE lock_test IN EXCLUSIVE MODE;
*/

-- 提交事务1
COMMIT;

-- 5. 意向锁演示

-- 意向锁用于表示事务即将对表中的行进行锁定
BEGIN;
-- 执行会锁定行的操作
SELECT * FROM products WHERE id = 1 FOR UPDATE;
-- 查看意向锁
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name,
    page,
    pid
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND relation::regclass::text = 'products'
ORDER BY locktype;
COMMIT;

-- 6. 死锁演示

-- 死锁：两个或多个事务相互等待对方释放锁
/*
-- 事务1：
BEGIN;
SELECT * FROM products WHERE id = 1 FOR UPDATE;  -- 获得行1的锁
-- 等待一段时间
SELECT pg_sleep(1);
SELECT * FROM products WHERE id = 2 FOR UPDATE;  -- 尝试获得行2的锁
COMMIT;

-- 事务2：
BEGIN;
SELECT * FROM products WHERE id = 2 FOR UPDATE;  -- 获得行2的锁
SELECT pg_sleep(1);
SELECT * FROM products WHERE id = 1 FOR UPDATE;  -- 尝试获得行1的锁（已死锁）
COMMIT;
*/

-- 7. 锁等待和超时

-- 设置锁超时时间
SET lock_timeout = '5s';

BEGIN;
-- 执行可能需要等待锁的操作
UPDATE products SET stock_quantity = stock_quantity - 2 WHERE id = 1;
-- 如果等待超过5秒，会抛出错误
COMMIT;

-- 重置锁超时
RESET lock_timeout;

-- 8. 锁监控和管理

-- 8.1 查看锁等待情况
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocked_activity.client_addr AS blocked_addr,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocking_activity.client_addr AS blocking_addr,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity 
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 8.2 查看最长时间等待的锁
SELECT 
    a.pid,
    a.usename,
    a.client_addr,
    l.locktype,
    l.mode,
    l.granted,
    l.relation::regclass as table_name,
    l.page,
    l.tuple,
    now() - a.query_start as wait_duration,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted
ORDER BY wait_duration DESC;

-- 8.3 查看锁持有情况统计
SELECT 
    locktype,
    mode,
    COUNT(*) as lock_count,
    array_agg(DISTINCT relation::regclass::text) as tables
FROM pg_locks
WHERE relation IS NOT NULL
GROUP BY locktype, mode
ORDER BY lock_count DESC;

-- 9. 锁优化建议

-- 9.1 分析锁使用情况
SELECT 
    schemaname,
    tablename,
    locks_table,
    waits_table,
    CASE 
        WHEN waits_table > 0 THEN 'Potential Issue'
        ELSE 'OK'
    END as lock_status
FROM (
    SELECT 
        schemaname,
        tablename,
        COUNT(*) as locks_table,
        SUM(CASE WHEN NOT granted THEN 1 ELSE 0 END) as waits_table
    FROM pg_locks l
    JOIN pg_class c ON l.relation = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE schemaname = 'public'
    GROUP BY schemaname, tablename
) lock_summary
ORDER BY waits_table DESC, locks_table DESC;

-- 10. 行锁细节

-- 10.1 查看行锁的具体信息
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name,
    page,
    tuple,
    virtualtransaction,
    pid
FROM pg_locks
WHERE pid = pg_backend_pid()
  AND locktype = 'tuple';

-- 10.2 查看被锁定的具体行
-- PostgreSQL不直接显示被锁定的行号，但可以通过pg_stat_activity查看阻塞情况

-- 11. 锁的性能影响

-- 测试锁对性能的影响
\timing on
-- 无锁查询
SELECT COUNT(*) FROM products WHERE stock_quantity > 100;
\timing off

\timing on
-- 有锁查询（行级锁）
BEGIN;
SELECT * FROM products WHERE id = 1 FOR UPDATE;
UPDATE products SET price = price * 1.01 WHERE id = 1;
COMMIT;
\timing off

-- 12. 手动锁管理

-- 12.1 手动锁定表
LOCK TABLE products IN SHARE MODE;
-- 执行一些操作
SELECT * FROM products WHERE category = 'Mobile';
-- 释放锁（在事务结束时自动释放）
COMMIT;

-- 12.2 使用NOWAIT选项
BEGIN;
-- 如果锁不能立即获得，立即报错而不是等待
SELECT * FROM products WHERE id = 1 FOR UPDATE NOWAIT;
-- 如果被其他事务锁定，会立即失败
COMMIT;

-- 13. 锁相关配置

-- 查看锁相关配置
SHOW max_locks_per_transaction;
SHOW deadlock_timeout;
SHOW log_lock_waits;

-- 设置死锁检测时间
SET deadlock_timeout = '1s';

-- 启用锁等待日志
SET log_lock_waits = on;

-- 14. 清理测试数据
DELETE FROM lock_test;
DROP TABLE IF EXISTS lock_test CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;