-- PostgreSQL教程第7章：事务管理与并发控制 - 隔离级别演示

-- 创建测试表和数据
CREATE TABLE IF NOT EXISTS bank_accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_holder VARCHAR(100) NOT NULL,
    balance DECIMAL(15,2) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清空表并插入测试数据
TRUNCATE bank_accounts;
INSERT INTO bank_accounts (account_number, account_holder, balance) VALUES
('ACC001', '张三', 10000.00),
('ACC002', '李四', 5000.00),
('ACC003', '王五', 3000.00),
('ACC004', '赵六', 8000.00);

-- 创建订单表用于测试
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

TRUNCATE orders;

-- 1. READ COMMITTED 隔离级别（PostgreSQL默认值）

-- 在一个事务中设置隔离级别并执行操作
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 查询当前隔离级别
SHOW transaction_isolation;

-- 查询账户余额
SELECT 
    account_number, 
    account_holder, 
    balance, 
    last_updated
FROM bank_accounts 
WHERE account_number = 'ACC001';

-- 在另一个事务中（这里我们假设），张三的账户会被更新
-- 当前事务中查询仍然看到的是事务开始时的快照

-- 查询订单表
SELECT * FROM orders;

-- 提交事务
COMMIT;

-- 2. REPEATABLE READ 隔离级别演示

-- 开始一个可重复读事务
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 查看事务ID和隔离级别
SELECT 
    txid_current() as transaction_id,
    transaction_timestamp() as start_time,
    current_setting('transaction_isolation') as isolation_level;

-- 查询账户余额
SELECT 
    account_number,
    account_holder,
    balance,
    last_updated
FROM bank_accounts
ORDER BY account_number;

-- 在当前事务中创建订单
INSERT INTO orders (order_number, customer_id, total_amount, status) VALUES
('ORD-001', 1, 1500.00, 'processing'),
('ORD-002', 2, 2300.00, 'confirmed');

-- 查看插入的订单
SELECT * FROM orders WHERE order_number IN ('ORD-001', 'ORD-002');

-- 当前事务不会看到其他事务对accounts表的修改
-- 保持可重复读取

-- 提交事务
COMMIT;

-- 查看提交后的订单
SELECT * FROM orders ORDER BY created_at;

-- 3. SERIALIZABLE 隔离级别演示

BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 查询所有账户
SELECT 
    account_number,
    account_holder,
    balance
FROM bank_accounts
ORDER BY account_number;

-- 当前事务会对所有读取的行加锁
-- 防止其他事务修改这些数据

-- 如果其他事务试图更新这些数据，会被阻塞或失败

-- 提交事务
COMMIT;

-- 4. 脏读演示（虽然PostgreSQL不支持脏读）

-- 创建两个测试事务
-- 事务A：读取未提交的数据
-- 事务B：更新数据但不提交

/*
-- 事务A（假设代码）
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;  -- PostgreSQL会转换为READ COMMITTED
SELECT balance FROM bank_accounts WHERE account_number = 'ACC001';
-- 如果张三的账户被事务B更新但未提交，这里可能看到中间状态

-- 事务B（假设代码）
BEGIN;
UPDATE bank_accounts SET balance = balance - 500 WHERE account_number = 'ACC001';
-- 不执行COMMIT
*/

-- 5. 不可重复读现象演示

-- 事务1：开始READ COMMITTED事务
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 第一次查询
SELECT 
    account_number,
    balance,
    last_updated
FROM bank_accounts
WHERE account_number = 'ACC001';

-- 事务2：在另一个会话中更新同一条记录
/*
-- 在另一个会话中执行：
BEGIN;
UPDATE bank_accounts SET balance = 8000.00 WHERE account_number = 'ACC001';
COMMIT;
*/

-- 事务1：第二次查询（可能看到不同的结果）
SELECT 
    account_number,
    balance,
    last_updated
FROM bank_accounts
WHERE account_number = 'ACC001';

COMMIT;

-- 6. 幻读现象演示

-- 事务1：开始REPEATABLE READ事务
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 第一次查询：查找余额大于7000的账户
SELECT 
    account_number,
    account_holder,
    balance
FROM bank_accounts
WHERE balance > 7000
ORDER BY balance DESC;

-- 事务2：在另一个会话中插入新记录
/*
-- 在另一个会话中执行：
BEGIN;
INSERT INTO bank_accounts (account_number, account_holder, balance) 
VALUES ('ACC005', '钱九', 9500.00);
COMMIT;
*/

-- 事务1：第二次查询（可能看到新的记录）
SELECT 
    account_number,
    account_holder,
    balance
FROM bank_accounts
WHERE balance > 7000
ORDER BY balance DESC;

COMMIT;

-- 7. 事务冲突检测演示

-- 事务1：锁定一行数据
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

SELECT * FROM bank_accounts WHERE account_number = 'ACC001' FOR UPDATE;

-- 在另一个会话中尝试修改同一行
/*
-- 事务2（假设代码）：
BEGIN;
UPDATE bank_accounts SET balance = balance + 100 WHERE account_number = 'ACC001';
-- 这会被阻塞，因为事务1已经持有这行的锁

-- 或者在SERIALIZABLE级别下可能直接失败
*/

-- 提交事务1
COMMIT;

-- 8. 锁升级和死锁检测

-- 查看当前持有的锁
SELECT 
    locktype,
    mode,
    granted,
    relation::regclass as table_name,
    virtualxid as virtual_transaction,
    pid,
    usename
FROM pg_locks
WHERE pid = pg_backend_pid()
ORDER BY locktype, mode;

-- 查看表级锁信息
SELECT 
    t.relname as table_name,
    l.locktype,
    l.mode,
    l.granted,
    a.usename,
    a.client_addr
FROM pg_locks l
JOIN pg_class t ON l.relation = t.oid
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.relation IN (
    SELECT oid FROM pg_class WHERE relname IN ('bank_accounts', 'orders')
)
ORDER BY t.relname, l.locktype;

-- 9. 快照隔离演示

-- 查看事务快照信息
SELECT 
    txid_current() as current_transaction,
    txid_status(txid_current()) as tx_status,
    transaction_timestamp() as tx_start_time;

-- 查看活动事务
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    transaction_timestamp() as tx_start_time,
    query_start,
    query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- 查看事务冲突
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.relation = blocked_locks.relation
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 10. 隔离级别性能对比

-- 测试不同隔离级别的性能
-- 创建大量数据的表
CREATE TABLE IF NOT EXISTS performance_test (
    id SERIAL PRIMARY KEY,
    data_value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试数据
INSERT INTO performance_test (data_value)
SELECT (RANDOM() * 1000)::INTEGER
FROM generate_series(1, 10000);

-- 创建索引
CREATE INDEX idx_performance_data ON performance_test (data_value);

-- 测试READ COMMITTED级别
\timing on
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*), AVG(data_value) FROM performance_test WHERE data_value > 500;
COMMIT;
\timing off

-- 测试REPEATABLE READ级别
\timing on
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*), AVG(data_value) FROM performance_test WHERE data_value > 500;
COMMIT;
\timing off

-- 测试SERIALIZABLE级别
\timing on
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*), AVG(data_value) FROM performance_test WHERE data_value > 500;
COMMIT;
\timing off

-- 11. 事务和约束

-- 创建带约束的表
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER CHECK (quantity >= 0),
    price DECIMAL(10,2) CHECK (price > 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 在事务中插入数据
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 尝试插入违反约束的数据
INSERT INTO inventory (product_name, quantity, price) VALUES
('Test Product', -10, 99.99);  -- 违反quantity >= 0约束

COMMIT;  -- 这会失败，因为违反了CHECK约束

-- 正常插入数据
BEGIN TRANSACTION;
INSERT INTO inventory (product_name, quantity, price) VALUES
('iPhone 14', 100, 7999.00),
('MacBook Pro', 50, 19999.00),
('iPad', 75, 3999.00);

-- 查看插入结果
SELECT * FROM inventory;

COMMIT;

-- 清理测试表
DROP TABLE IF EXISTS performance_test CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS bank_accounts CASCADE;