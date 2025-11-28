-- PostgreSQL教程第7章：事务管理与并发控制 - 基础事务操作演示

-- 1. 基础事务操作

-- 1.1 创建测试表
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    holder_name VARCHAR(100) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 插入测试数据
INSERT INTO accounts (account_number, holder_name, balance) VALUES
('1001', '张三', 10000.00),
('1002', '李四', 5000.00),
('1003', '王五', 8000.00),
('1004', '赵六', 3000.00);

-- 显示初始数据
SELECT * FROM accounts;

-- 1.3 基础事务示例
-- 开始一个事务
BEGIN;

-- 查看当前事务状态
SELECT 
    txid_current() as transaction_id,
    current_transaction_id() as current_tx_id,
    transaction_timestamp() as tx_start_time;

-- 执行一些操作
UPDATE accounts 
SET balance = balance + 1000 
WHERE account_number = '1001';

UPDATE accounts 
SET balance = balance - 1000 
WHERE account_number = '1002';

-- 查看更新后的数据（事务内）
SELECT * FROM accounts;

-- 提交事务
COMMIT;

-- 查看提交后的数据
SELECT * FROM accounts;

-- 2. 事务回滚示例

-- 开始一个新事务
BEGIN;

-- 查看当前事务ID
SELECT 
    txid_current() as current_transaction_id,
    txid_status(txid_current()) as transaction_status;

-- 执行一些操作
UPDATE accounts 
SET balance = balance + 2000 
WHERE account_number = '1003';

-- 插入一条新记录
INSERT INTO accounts (account_number, holder_name, balance) 
VALUES ('1005', '孙七', 2000.00);

-- 查看操作后的数据
SELECT * FROM accounts;

-- 回滚事务（撤销所有更改）
ROLLBACK;

-- 查看回滚后的数据（应该回到操作前的状态）
SELECT * FROM accounts;

-- 3. 保存点示例

-- 开始事务
BEGIN;

-- 设置保存点1
SAVEPOINT savepoint_1;

-- 执行第一个操作
UPDATE accounts 
SET balance = balance + 500 
WHERE account_number = '1001';

-- 查看第一次操作的结果
SELECT * FROM accounts WHERE account_number = '1001';

-- 设置保存点2
SAVEPOINT savepoint_2;

-- 执行第二个操作
INSERT INTO accounts (account_number, holder_name, balance) 
VALUES ('1006', '周八', 1500.00);

-- 查看第二次操作的结果
SELECT account_number, holder_name FROM accounts WHERE account_number = '1006';

-- 回滚到保存点2（撤销第二个操作，但保留第一个操作）
ROLLBACK TO savepoint_2;

-- 验证回滚结果
SELECT * FROM accounts WHERE account_number = '1001';
SELECT * FROM accounts WHERE account_number = '1006';  -- 这条记录应该被撤销

-- 设置新的保存点
SAVEPOINT savepoint_3;

-- 执行第三个操作
UPDATE accounts 
SET balance = balance + 300 
WHERE account_number = '1002';

-- 查看第三次操作的结果
SELECT * FROM accounts WHERE account_number = '1002';

-- 回滚到保存点1（撤销所有在savepoint_1之后的操作）
ROLLBACK TO savepoint_1;

-- 验证最终结果
SELECT * FROM accounts WHERE account_number = '1001';  -- 只保留了第一次操作
SELECT * FROM accounts WHERE account_number = '1002';  -- 应该恢复到原始值

-- 释放保存点
RELEASE savepoint_1;

-- 提交剩余的操作
COMMIT;

-- 查看最终结果
SELECT * FROM accounts;

-- 4. 自动提交模式演示

-- 查看当前自动提交模式
SHOW AUTOCOMMIT;

-- 设置自动提交模式为OFF
SET AUTOCOMMIT = OFF;

-- 执行不自动提交的操作
UPDATE accounts 
SET balance = balance + 100 
WHERE account_number = '1003';

-- 查看操作结果（即使没有COMMIT，操作也已经生效）
SELECT * FROM accounts WHERE account_number = '1003';

-- 手动回滚
ROLLBACK;

-- 验证回滚结果
SELECT * FROM accounts WHERE account_number = '1003';

-- 重新执行操作并提交
UPDATE accounts 
SET balance = balance + 100 
WHERE account_number = '1003';
COMMIT;

-- 恢复自动提交模式
SET AUTOCOMMIT = ON;

-- 5. 事务隔离级别设置

-- 查看当前隔离级别
SHOW transaction_isolation;

-- 设置事务隔离级别
-- READ UNCOMMITTED（读未提交）
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- READ COMMITTED（读已提交）- PostgreSQL默认值
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- REPEATABLE READ（可重复读）
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- SERIALIZABLE（串行化）
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 6. 事务错误处理

-- 创建测试表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    stock INTEGER DEFAULT 0
);

-- 事务中错误处理示例
BEGIN;

-- 设置保存点
SAVEPOINT before_insert;

-- 尝试插入无效数据（name不能为NULL，但这里会故意尝试）
-- INSERT INTO products (name, price, stock) VALUES (NULL, 10.00, 100);

-- 如果上面的语句被取消注释，会产生错误，可以这样处理：
-- ROLLBACK TO before_insert;

-- 正常插入数据
INSERT INTO products (name, price, stock) VALUES 
('iPhone 14', 7999.00, 50),
('MacBook Pro', 19999.00, 20),
('iPad', 3999.00, 30);

-- 查看插入结果
SELECT * FROM products;

-- 提交事务
COMMIT;

-- 7. 事务时间监控

-- 查看事务相关信息
SELECT 
    txid_current() as current_transaction_id,
    transaction_timestamp() as current_timestamp,
    now() as now_timestamp,
    clock_timestamp() as clock_timestamp;

-- 查看长时间运行的事务
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    now() - query_start as duration,
    query
FROM pg_stat_activity 
WHERE state = 'active' 
  AND now() - query_start > interval '5 minutes'
ORDER BY duration DESC;

-- 8. 锁相关查询

-- 查看当前锁信息
SELECT 
    locktype,
    mode,
    granted,
    relname,
    virtualtransaction,
    pid,
    usename,
    query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT granted;

-- 查看表的锁信息
SELECT 
    schemaname,
    tablename,
    table_mode,
    locktype,
    mode,
    granted
FROM pg_locks l
JOIN pg_class c ON l.relation = c.oid
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE schemaname = 'public'
ORDER BY tablename, locktype;

-- 9. 事务和并发控制基础概念

/*
事务ACID属性：
- 原子性（Atomicity）：事务中的所有操作要么全部成功，要么全部失败
- 一致性（Consistency）：事务执行前后数据库都处于一致状态
- 隔离性（Isolation）：并发执行的事务互不干扰
- 持久性（Durability）：一旦提交，数据永久保存

PostgreSQL事务特点：
1. 默认使用自动提交模式
2. 支持嵌套事务（通过保存点实现）
3. 使用MVCC实现高并发
4. 支持多种隔离级别
5. 自动检测和解决死锁
*/

-- 10. 清理测试数据
DELETE FROM products;
DELETE FROM accounts WHERE account_number IN ('1005', '1006');

-- 显示最终清理后的数据
SELECT * FROM accounts;