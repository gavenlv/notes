-- PostgreSQL教程第7章：事务管理与并发控制 - 并发控制示例

-- 创建测试表
CREATE TABLE IF NOT EXISTS concurrent_orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_inventory (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_balance (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    available_balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    frozen_balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清空表并插入测试数据
TRUNCATE concurrent_orders CASCADE;
TRUNCATE product_inventory CASCADE;
TRUNCATE customer_balance CASCADE;

INSERT INTO product_inventory (product_id, product_name, stock_quantity) VALUES
(1, 'iPhone 14', 100),
(2, 'MacBook Pro', 50),
(3, 'iPad', 75),
(4, 'AirPods', 200),
(5, 'Apple Watch', 150);

INSERT INTO customer_balance (customer_id, customer_name, available_balance) VALUES
(1, '张三', 10000.00),
(2, '李四', 8000.00),
(3, '王五', 12000.00),
(4, '赵六', 6000.00),
(5, '钱七', 15000.00);

-- 1. 并发订单处理演示

-- 1.1 创建订单处理函数
CREATE OR REPLACE FUNCTION process_order(
    p_customer_id INTEGER,
    p_product_id INTEGER,
    p_quantity INTEGER
) RETURNS TEXT AS $$
DECLARE
    customer_balance DECIMAL(10,2);
    product_stock INTEGER;
    order_price DECIMAL(10,2);
    total_amount DECIMAL(10,2);
    result_msg TEXT;
    current_version INTEGER;
BEGIN
    -- 获取产品信息
    SELECT price INTO order_price
    FROM (
        SELECT 1 as product_id, 7999.00 as price
        UNION ALL SELECT 2, 19999.00
        UNION ALL SELECT 3, 3999.00
        UNION ALL SELECT 4, 1999.00
        UNION ALL SELECT 5, 2999.00
    ) prices
    WHERE product_id = p_product_id;
    
    total_amount := order_price * p_quantity;
    
    -- 检查客户余额（使用行锁防止并发修改）
    SELECT available_balance INTO customer_balance
    FROM customer_balance
    WHERE customer_id = p_customer_id
    FOR UPDATE;
    
    -- 检查库存（使用行锁防止并发修改）
    SELECT stock_quantity INTO product_stock
    FROM product_inventory
    WHERE product_id = p_product_id
    FOR UPDATE;
    
    -- 检查业务逻辑
    IF customer_balance IS NULL THEN
        RETURN 'Customer not found';
    END IF;
    
    IF product_stock IS NULL THEN
        RETURN 'Product not found';
    END IF;
    
    IF customer_balance < total_amount THEN
        RETURN 'Insufficient balance';
    END IF;
    
    IF product_stock < p_quantity THEN
        RETURN 'Insufficient stock';
    END IF;
    
    -- 创建订单
    INSERT INTO concurrent_orders (customer_id, product_id, quantity, price, status)
    VALUES (p_customer_id, p_product_id, p_quantity, order_price, 'confirmed');
    
    -- 扣减库存
    UPDATE product_inventory 
    SET stock_quantity = stock_quantity - p_quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = p_product_id;
    
    -- 扣减客户余额
    UPDATE customer_balance 
    SET available_balance = available_balance - total_amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE customer_id = p_customer_id;
    
    result_msg := 'Order processed successfully. Amount: ' || total_amount || ', New balance: ' || (customer_balance - total_amount);
    
    RETURN result_msg;
END;
$$ LANGUAGE plpgsql;

-- 2. 死锁演示

-- 2.1 创建可能发生死锁的函数
CREATE OR REPLACE FUNCTION trigger_deadlock_demo() RETURNS TEXT AS $$
BEGIN
    -- 这个函数故意设计为可能引起死锁
    -- 在实际应用中应该避免这种模式
    RAISE NOTICE 'Deadlock scenario - Order by ID 1 then 2';
    RETURN 'Ready for deadlock demonstration';
END;
$$ LANGUAGE plpgsql;

-- 2.2 演示死锁场景（需要两个会话）
/*
-- 会话1：
BEGIN;
-- 先锁定customer_id=1
SELECT * FROM customer_balance WHERE customer_id = 1 FOR UPDATE;
SELECT pg_sleep(2); -- 等待2秒
-- 然后尝试锁定customer_id=2
SELECT * FROM customer_balance WHERE customer_id = 2 FOR UPDATE;
COMMIT;

-- 会话2：
BEGIN;
-- 先锁定customer_id=2
SELECT * FROM customer_balance WHERE customer_id = 2 FOR UPDATE;
SELECT pg_sleep(2); -- 等待2秒
-- 然后尝试锁定customer_id=1（这会与会话1产生死锁）
SELECT * FROM customer_balance WHERE customer_id = 1 FOR UPDATE;
COMMIT;

-- PostgreSQL会自动检测死锁并回滚其中一个事务
*/

-- 3. 乐观锁演示

-- 3.1 使用版本号的乐观锁
CREATE OR REPLACE FUNCTION update_customer_balance_optimistic(
    p_customer_id INTEGER,
    p_amount DECIMAL(10,2)
) RETURNS TEXT AS $$
DECLARE
    current_version INTEGER;
    updated_rows INTEGER;
BEGIN
    -- 获取当前版本
    SELECT version INTO current_version
    FROM customer_balance
    WHERE customer_id = p_customer_id;
    
    IF current_version IS NULL THEN
        RETURN 'Customer not found';
    END IF;
    
    -- 执行更新，检查版本是否一致
    UPDATE customer_balance 
    SET available_balance = available_balance + p_amount,
        version = version + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE customer_id = p_customer_id 
      AND version = current_version;
    
    GET DIAGNOSTICS updated_rows = ROW_COUNT;
    
    IF updated_rows = 0 THEN
        RETURN 'Update failed - version mismatch or no rows affected';
    ELSE
        RETURN 'Update successful';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 4. 库存预订系统演示

-- 4.1 库存预订函数
CREATE OR RESERVE FUNCTION reserve_inventory(
    p_customer_id INTEGER,
    p_product_id INTEGER,
    p_quantity INTEGER
) RETURNS TEXT AS $$
DECLARE
    current_stock INTEGER;
    current_reserved INTEGER;
    order_id INTEGER;
BEGIN
    -- 使用行级锁检查库存
    SELECT stock_quantity, reserved_quantity INTO current_stock, current_reserved
    FROM product_inventory
    WHERE product_id = p_product_id
    FOR UPDATE;
    
    IF current_stock IS NULL THEN
        RETURN 'Product not found';
    END IF;
    
    -- 检查可用库存
    IF (current_stock - current_reserved) < p_quantity THEN
        RETURN 'Insufficient available inventory';
    END IF;
    
    -- 创建订单
    INSERT INTO concurrent_orders (customer_id, product_id, quantity, price, status)
    SELECT p_customer_id, p_product_id, p_quantity, price, 'reserved'
    FROM (
        SELECT 1 as product_id, 7999.00 as price
        UNION ALL SELECT 2, 19999.00
        UNION ALL SELECT 3, 3999.00
        UNION ALL SELECT 4, 1999.00
        UNION ALL SELECT 5, 2999.00
    ) prices
    WHERE product_id = p_product_id
    RETURNING order_id INTO order_id;
    
    -- 更新预订数量
    UPDATE product_inventory 
    SET reserved_quantity = reserved_quantity + p_quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = p_product_id;
    
    RETURN 'Inventory reserved successfully. Order ID: ' || order_id;
END;
$$ LANGUAGE plpgsql;

-- 5. 事务超时演示

-- 5.1 创建长时间运行的事务
CREATE OR REPLACE FUNCTION long_transaction_demo() RETURNS TEXT AS $$
BEGIN
    RAISE NOTICE 'Starting long transaction...';
    SELECT pg_sleep(5); -- 模拟长时间操作
    RAISE NOTICE 'Long transaction completed';
    RETURN 'Long transaction finished';
END;
$$ LANGUAGE plpgsql;

-- 6. 并发测试场景

-- 6.1 批量订单处理模拟
CREATE OR REPLACE FUNCTION batch_order_processing(
    p_customer_id INTEGER,
    p_order_count INTEGER
) RETURNS TEXT AS $$
DECLARE
    i INTEGER;
    results TEXT := '';
BEGIN
    FOR i IN 1..p_order_count LOOP
        BEGIN
            -- 随机选择产品和数量
            INSERT INTO concurrent_orders (customer_id, product_id, quantity, price, status)
            VALUES (
                p_customer_id,
                (random() * 4 + 1)::INTEGER,
                (random() * 3 + 1)::INTEGER,
                (random() * 1000 + 1000)::DECIMAL(10,2),
                'processing'
            );
            results := results || 'Order ' || i || ' created; ';
        EXCEPTION WHEN OTHERS THEN
            results := results || 'Order ' || i || ' failed: ' || SQLERRM || '; ';
        END;
    END LOOP;
    
    RETURN results;
END;
$$ LANGUAGE plpgsql;

-- 7. 锁等待监控

-- 7.1 监控锁等待情况的函数
CREATE OR REPLACE FUNCTION monitor_locks() RETURNS TABLE (
    blocked_pid BIGINT,
    blocking_pid BIGINT,
    blocked_query TEXT,
    blocking_query TEXT,
    lock_type TEXT,
    table_name TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l1.pid as blocked_pid,
        l2.pid as blocking_pid,
        a1.query as blocked_query,
        a2.query as blocking_query,
        l1.locktype as lock_type,
        c.relname as table_name
    FROM pg_locks l1
    JOIN pg_locks l2 ON l1.locktype = l2.locktype 
        AND l1.relation IS NOT NULL 
        AND l1.relation = l2.relation
    JOIN pg_stat_activity a1 ON l1.pid = a1.pid
    JOIN pg_stat_activity a2 ON l2.pid = a2.pid
    JOIN pg_class c ON l1.relation = c.oid
    WHERE NOT l1.granted AND l2.granted
      AND l1.pid != l2.pid;
END;
$$ LANGUAGE plpgsql;

-- 8. 实际并发控制测试

-- 8.1 多个客户同时购买同一商品
/*
-- 这个演示需要多个会话来同时执行
-- 模拟高并发购买场景

-- 客户1尝试购买
SELECT process_order(1, 1, 5);  -- 张三买5台iPhone

-- 客户2同时尝试购买
SELECT process_order(2, 1, 3);  -- 李四买3台iPhone

-- 客户3同时尝试购买
SELECT process_order(3, 1, 10); -- 王五买10台iPhone

-- 这些操作应该能正确处理库存和余额
*/

-- 8.2 库存预订测试
/*
-- 同时进行库存预订
SELECT reserve_inventory(1, 1, 10);  -- 张三预订10台iPhone
SELECT reserve_inventory(2, 1, 5);   -- 李四预订5台iPhone
SELECT reserve_inventory(3, 1, 3);   -- 王五预订3台iPhone
*/

-- 9. 并发性能测试

-- 9.1 并发插入测试
CREATE OR REPLACE FUNCTION concurrent_insert_test(p_count INTEGER) RETURNS INTEGER AS $$
DECLARE
    i INTEGER;
    inserted_count INTEGER := 0;
BEGIN
    FOR i IN 1..p_count LOOP
        BEGIN
            INSERT INTO concurrent_orders (customer_id, product_id, quantity, price, status)
            VALUES (
                (random() * 4 + 1)::INTEGER,
                (random() * 4 + 1)::INTEGER,
                (random() * 5 + 1)::INTEGER,
                (random() * 1000 + 500)::DECIMAL(10,2),
                'test'
            );
            inserted_count := inserted_count + 1;
        EXCEPTION WHEN OTHERS THEN
            -- 记录失败但继续
            NULL;
        END;
    END LOOP;
    
    RETURN inserted_count;
END;
$$ LANGUAGE plpgsql;

-- 10. 事务隔离级别测试

-- 10.1 创建测试隔离级别效果的函数
CREATE OR REPLACE FUNCTION test_isolation_level(
    p_customer_id INTEGER
) RETURNS TABLE (
    isolation_level TEXT,
    initial_balance DECIMAL(10,2),
    balance_after_other_txn DECIMAL(10,2),
    final_balance DECIMAL(10,2)
) AS $$
DECLARE
    initial_bal DECIMAL(10,2);
    after_change DECIMAL(10,2);
    final_bal DECIMAL(10,2);
BEGIN
    -- 获取初始余额
    SELECT available_balance INTO initial_bal
    FROM customer_balance 
    WHERE customer_id = p_customer_id;
    
    -- 在另一个事务中修改余额（需要模拟）
    -- 这里我们只是记录测试场景
    
    -- 在当前事务中查看变化
    SELECT available_balance INTO after_change
    FROM customer_balance 
    WHERE customer_id = p_customer_id;
    
    -- 最终余额
    SELECT available_balance INTO final_bal
    FROM customer_balance 
    WHERE customer_id = p_customer_id;
    
    RETURN QUERY SELECT 
        'CURRENT'::TEXT,
        initial_bal,
        after_change,
        final_bal;
END;
$$ LANGUAGE plpgsql;

-- 11. 错误处理和回滚演示

-- 11.1 事务回滚演示
/*
BEGIN;
    -- 插入测试数据
    INSERT INTO concurrent_orders (customer_id, product_id, quantity, price)
    VALUES (999, 999, 1, 100.00);
    
    -- 故意触发错误
    RAISE EXCEPTION 'Simulated error for rollback demonstration';
    
    -- 这个INSERT不会执行
    INSERT INTO concurrent_orders (customer_id, product_id, quantity, price)
    VALUES (888, 888, 2, 200.00);
    
COMMIT; -- 这里不会执行到

-- 执行时会发生回滚
*/

-- 11.2 保存点演示
/*
BEGIN;
    -- 设置保存点
    SAVEPOINT before_test_insert;
    
    -- 执行可能出错的操作
    INSERT INTO concurrent_orders (customer_id, product_id, quantity, price)
    VALUES (777, 777, 1, 300.00);
    
    -- 如果出错，可以回滚到保存点
    -- ROLLBACK TO before_test_insert;
    
    -- 继续执行其他操作
    INSERT INTO concurrent_orders (customer_id, product_id, quantity, price)
    VALUES (666, 666, 2, 400.00);
    
    -- 提交事务
COMMIT;
*/

-- 12. 并发控制最佳实践

-- 12.1 锁顺序一致性
CREATE OR REPLACE FUNCTION consistent_lock_order_demo(
    p_customer_id1 INTEGER,
    p_customer_id2 INTEGER
) RETURNS TEXT AS $$
DECLARE
    customer1_id INTEGER := LEAST(p_customer_id1, p_customer_id2);
    customer2_id INTEGER := GREATEST(p_customer_id1, p_customer_id2);
BEGIN
    -- 始终按照ID从小到大的顺序锁定，避免死锁
    IF customer1_id = customer2_id THEN
        -- 相同客户，只需要锁定一次
        SELECT * FROM customer_balance 
        WHERE customer_id = customer1_id 
        FOR UPDATE;
    ELSE
        -- 按顺序锁定两个不同的客户
        SELECT * FROM customer_balance 
        WHERE customer_id = customer1_id 
        FOR UPDATE;
        
        SELECT * FROM customer_balance 
        WHERE customer_id = customer2_id 
        FOR UPDATE;
    END IF;
    
    -- 执行转账操作
    -- 这里可以实现具体的业务逻辑
    
    RETURN 'Transfer completed with consistent locking order';
END;
$$ LANGUAGE plpgsql;

-- 13. 性能监控和诊断

-- 13.1 查看当前并发活动
SELECT 
    pid,
    usename,
    client_addr,
    backend_start,
    query_start,
    state,
    CASE state
        WHEN 'active' THEN 'Running query'
        WHEN 'idle' THEN 'Waiting for command'
        WHEN 'idle in transaction' THEN 'In transaction but idle'
        ELSE state
    END as state_description,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity
WHERE schemaname = 'public'
  AND backend_type = 'client backend'
ORDER BY backend_start DESC;

-- 13.2 查看表锁情况
SELECT 
    schemaname,
    tablename,
    locktype,
    mode,
    COUNT(*) as lock_count,
    array_agg(DISTINCT pid::text) as pids
FROM pg_locks l
JOIN pg_class c ON l.relation = c.oid
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE schemaname = 'public'
GROUP BY schemaname, tablename, locktype, mode
ORDER BY lock_count DESC;

-- 14. 并发测试总结

-- 14.1 创建测试报告
SELECT 
    'Concurrent Orders Test Summary' as report_title,
    COUNT(*) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_id) as unique_products,
    SUM(quantity) as total_quantity,
    SUM(price * quantity) as total_amount
FROM concurrent_orders;

-- 14.2 库存状态检查
SELECT 
    pi.product_name,
    pi.stock_quantity,
    pi.reserved_quantity,
    (pi.stock_quantity - pi.reserved_quantity) as available_quantity,
    co.order_count,
    co.total_ordered
FROM product_inventory pi
LEFT JOIN (
    SELECT 
        product_id,
        COUNT(*) as order_count,
        SUM(quantity) as total_ordered
    FROM concurrent_orders
    GROUP BY product_id
) co ON pi.product_id = co.product_id
ORDER BY pi.product_id;

-- 15. 清理函数和表
CREATE OR REPLACE FUNCTION cleanup_concurrent_test_data() RETURNS TEXT AS $$
BEGIN
    -- 清空测试数据
    TRUNCATE TABLE concurrent_orders RESTART IDENTITY CASCADE;
    
    -- 重置库存和余额
    UPDATE product_inventory SET 
        stock_quantity = CASE 
            WHEN product_id = 1 THEN 100
            WHEN product_id = 2 THEN 50
            WHEN product_id = 3 THEN 75
            WHEN product_id = 4 THEN 200
            WHEN product_id = 5 THEN 150
        END,
        reserved_quantity = 0,
        updated_at = CURRENT_TIMESTAMP;
    
    UPDATE customer_balance SET 
        available_balance = CASE 
            WHEN customer_id = 1 THEN 10000.00
            WHEN customer_id = 2 THEN 8000.00
            WHEN customer_id = 3 THEN 12000.00
            WHEN customer_id = 4 THEN 6000.00
            WHEN customer_id = 5 THEN 15000.00
        END,
        frozen_balance = 0.00,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN 'Test data cleaned successfully';
END;
$$ LANGUAGE plpgsql;

-- 执行清理（可选）
-- SELECT cleanup_concurrent_test_data();