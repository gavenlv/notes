-- ================================================
-- PostgreSQL第9章：EXPLAIN命令和查询计划分析
-- ================================================
-- 本文件演示如何使用EXPLAIN命令分析查询执行计划
-- 理解查询优化器的工作原理和性能优化策略

-- 清理环境
-- DROP TABLE IF EXISTS orders, order_items, customers, products, employees CASCADE;
-- DROP SCHEMA IF EXISTS performance_test CASCADE;

-- ================================================
-- 1. 测试数据准备
-- ================================================

-- 创建测试模式
CREATE SCHEMA IF NOT EXISTS performance_test;

-- 启用统计信息收集
SET track_activities = on;
SET track_counts = on;
SET track_io_timing = on;
SET track_functions = all;

-- 创建测试表
CREATE TABLE performance_test.customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registration_date DATE DEFAULT CURRENT_DATE,
    country VARCHAR(50) DEFAULT 'USA',
    city VARCHAR(50),
    total_spent DECIMAL(12,2) DEFAULT 0.00
);

CREATE TABLE performance_test.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    created_date DATE DEFAULT CURRENT_DATE,
    rating DECIMAL(3,2) DEFAULT 4.0
);

CREATE TABLE performance_test.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES performance_test.customers(customer_id),
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(12,2) DEFAULT 0.00,
    shipping_country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE performance_test.order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES performance_test.orders(order_id),
    product_id INTEGER NOT NULL REFERENCES performance_test.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0.00,
    subtotal DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount/100)) STORED
);

CREATE TABLE performance_test.employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    hire_date DATE DEFAULT CURRENT_DATE,
    salary DECIMAL(10,2),
    manager_id INTEGER
);

-- 插入大量测试数据
INSERT INTO performance_test.customers (first_name, last_name, email, country, city, total_spent)
SELECT 
    'FirstName' || i,
    'LastName' || i,
    'customer' || i || '@example.com',
    CASE WHEN i % 5 = 0 THEN 'USA' WHEN i % 5 = 1 THEN 'China' WHEN i % 5 = 2 THEN 'UK' WHEN i % 5 = 3 THEN 'Germany' ELSE 'France' END,
    'City' || (i % 100),
    (i * 100.50 + random() * 1000)::DECIMAL(12,2)
FROM generate_series(1, 10000) AS i;

INSERT INTO performance_test.products (product_name, category, price, stock_quantity, rating)
SELECT 
    'Product ' || i,
    CASE WHEN i % 4 = 0 THEN 'Electronics' WHEN i % 4 = 1 THEN 'Clothing' WHEN i % 4 = 2 THEN 'Books' ELSE 'Home' END,
    (i * 10.50 + random() * 100)::DECIMAL(10,2),
    i % 500,
    (3.0 + random() * 2.0)::DECIMAL(3,2)
FROM generate_series(1, 5000) AS i;

-- 创建订单数据
INSERT INTO performance_test.orders (customer_id, order_date, status, total_amount, shipping_country)
SELECT 
    (i % 10000) + 1,
    CURRENT_DATE - (i % 365),
    CASE WHEN i % 7 = 0 THEN 'delivered' WHEN i % 7 = 1 THEN 'shipped' WHEN i % 7 = 2 THEN 'processing' ELSE 'pending' END,
    (i * 25.50 + random() * 500)::DECIMAL(12,2),
    CASE WHEN i % 5 = 0 THEN 'USA' WHEN i % 5 = 1 THEN 'China' WHEN i % 5 = 2 THEN 'UK' WHEN i % 5 = 3 THEN 'Germany' ELSE 'France' END
FROM generate_series(1, 20000) AS i;

-- 创建订单项目数据
INSERT INTO performance_test.order_items (order_id, product_id, quantity, unit_price, discount)
SELECT 
    (i % 20000) + 1,
    (i % 5000) + 1,
    (i % 5) + 1,
    ((i % 5000) + 1) * 10.50,
    CASE WHEN i % 10 = 0 THEN 10.0 WHEN i % 10 = 1 THEN 5.0 ELSE 0.0 END
FROM generate_series(1, 50000) AS i;

-- 更新订单总金额
UPDATE performance_test.orders 
SET total_amount = (
    SELECT COALESCE(SUM(subtotal), 0)
    FROM performance_test.order_items 
    WHERE order_items.order_id = orders.order_id
);

-- 更新客户总消费
UPDATE performance_test.customers 
SET total_spent = (
    SELECT COALESCE(SUM(total_amount), 0)
    FROM performance_test.orders 
    WHERE orders.customer_id = customers.customer_id
);

-- 插入员工数据
INSERT INTO performance_test.employees (first_name, last_name, department, hire_date, salary, manager_id)
SELECT 
    'Employee' || i,
    'Name' || i,
    CASE WHEN i % 4 = 0 THEN 'IT' WHEN i % 4 = 1 THEN 'Sales' WHEN i % 4 = 2 THEN 'HR' ELSE 'Finance' END,
    CURRENT_DATE - (i % 1000),
    (i * 1000 + random() * 5000)::DECIMAL(10,2),
    CASE WHEN i % 10 = 0 THEN NULL ELSE (i % 10) + 1 END
FROM generate_series(1, 1000) AS i;

-- 收集统计信息
ANALYZE performance_test.customers;
ANALYZE performance_test.products;
ANALYZE performance_test.orders;
ANALYZE performance_test.order_items;
ANALYZE performance_test.employees;

-- ================================================
-- 2. EXPLAIN基础使用
-- ================================================

-- 2.1 最简单的EXPLAIN
-- 只显示查询计划，不执行查询
EXPLAIN 
SELECT * FROM performance_test.customers 
WHERE customer_id = 1;

-- 2.2 EXPLAIN ANALYZE
-- 执行查询并显示实际的执行时间和统计信息
EXPLAIN ANALYZE
SELECT * FROM performance_test.customers 
WHERE customer_id = 1;

-- 2.3 EXPLAIN (FORMAT JSON)
-- 以JSON格式输出查询计划，便于程序解析
EXPLAIN (FORMAT JSON)
SELECT c.first_name, c.last_name, COUNT(o.order_id) as order_count
FROM performance_test.customers c
LEFT JOIN performance_test.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(o.order_id) > 5;

-- ================================================
-- 3. 扫描类型分析
-- ================================================

-- 3.1 顺序扫描 (Seq Scan)
-- 全表扫描，通常性能较低
EXPLAIN ANALYZE
SELECT * FROM performance_test.customers 
WHERE country = 'China';

-- 3.2 索引扫描 (Index Scan)
-- 使用索引进行扫描，性能较好
CREATE INDEX idx_customers_country ON performance_test.customers(country);
EXPLAIN ANALYZE
SELECT * FROM performance_test.customers 
WHERE country = 'China';

-- 3.3 索引唯一扫描 (Index Only Scan)
-- 仅访问索引，性能最佳
CREATE UNIQUE INDEX idx_customers_email ON performance_test.customers(email);
EXPLAIN ANALYZE
SELECT email FROM performance_test.customers 
WHERE email = 'customer1@example.com';

-- 3.4 位图扫描 (Bitmap Scan)
-- 结合多个条件时的扫描方式
CREATE INDEX idx_orders_status ON performance_test.orders(status);
CREATE INDEX idx_orders_date ON performance_test.orders(order_date);

EXPLAIN ANALYZE
SELECT * FROM performance_test.orders 
WHERE status = 'delivered' 
  AND order_date >= '2024-01-01';

-- ================================================
-- 4. 连接类型分析
-- ================================================

-- 4.1 嵌套循环连接 (Nested Loop Join)
EXPLAIN ANALYZE
SELECT c.first_name, c.last_name, o.order_id, o.order_date
FROM performance_test.customers c
INNER JOIN performance_test.orders o ON c.customer_id = o.customer_id
WHERE c.customer_id <= 100;

-- 4.2 哈希连接 (Hash Join)
-- 为大表连接优化创建索引
CREATE INDEX idx_orders_customer ON performance_test.orders(customer_id);
CREATE INDEX idx_customers_id ON performance_test.customers(customer_id);

EXPLAIN ANALYZE
SELECT c.first_name, c.last_name, o.total_amount
FROM performance_test.customers c
INNER JOIN performance_test.orders o ON c.customer_id = o.customer_id
WHERE o.total_amount > 1000.00;

-- 4.3 合并连接 (Merge Join)
-- 对已排序的数据执行高效连接
EXPLAIN ANALYZE
SELECT e.first_name, e.last_name, m.first_name as manager_first
FROM performance_test.employees e
LEFT JOIN performance_test.employees m ON e.manager_id = m.employee_id
WHERE e.department = 'IT';

-- ================================================
-- 5. 查询计划成本分析
-- ================================================

-- 5.1 启用详细分析选项
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS)
SELECT c.first_name, c.last_name, o.order_id, p.product_name, oi.quantity
FROM performance_test.customers c
INNER JOIN performance_test.orders o ON c.customer_id = o.customer_id
INNER JOIN performance_test.order_items oi ON o.order_id = oi.order_id
INNER JOIN performance_test.products p ON oi.product_id = p.product_id
WHERE c.country = 'USA' 
  AND o.status = 'delivered'
  AND p.category = 'Electronics';

-- 5.2 比较不同查询方式的成本
-- 方法1：JOIN查询
EXPLAIN ANALYZE
SELECT p.product_name, COUNT(oi.item_id) as total_sold
FROM performance_test.products p
INNER JOIN performance_test.order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_sold DESC
LIMIT 10;

-- 方法2：子查询
EXPLAIN ANALYZE
SELECT product_name, 
       (SELECT COUNT(*) 
        FROM performance_test.order_items oi 
        WHERE oi.product_id = p.product_id) as total_sold
FROM performance_test.products p
ORDER BY total_sold DESC
LIMIT 10;

-- ================================================
-- 6. 索引使用分析
-- ================================================

-- 6.1 查看索引使用统计
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'performance_test'
ORDER BY idx_scan DESC;

-- 6.2 查看表访问统计
SELECT 
    relname,
    seq_scan as sequential_scans,
    seq_tup_read as tuples_read_seq,
    index_scan as index_scans,
    idx_tup_fetch as tuples_fetched_idx,
    n_tup_ins + n_tup_upd + n_tup_del as total_modifications
FROM pg_stat_user_tables
WHERE schemaname = 'performance_test'
ORDER BY seq_scan DESC;

-- 6.3 分析索引效率
-- 找出从未被使用的索引
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0 
  AND schemaname = 'performance_test'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ================================================
-- 7. 查询优化案例
-- ================================================

-- 7.1 案例1：优化大表查询
-- 原始查询（性能较差）
EXPLAIN ANALYZE
SELECT *
FROM performance_test.orders o
INNER JOIN performance_test.customers c ON o.customer_id = c.customer_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND c.country = 'USA'
  AND o.status = 'delivered';

-- 优化版本1：添加复合索引
CREATE INDEX idx_orders_date_status ON performance_test.orders(order_date, status);
CREATE INDEX idx_customers_country ON performance_test.customers(country);

EXPLAIN ANALYZE
SELECT o.order_id, o.order_date, c.first_name, c.last_name, o.total_amount
FROM performance_test.orders o
INNER JOIN performance_test.customers c ON o.customer_id = c.customer_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND c.country = 'USA'
  AND o.status = 'delivered';

-- 优化版本2：减少返回列
EXPLAIN ANALYZE
SELECT o.order_id, o.order_date, o.total_amount, c.email
FROM performance_test.orders o
INNER JOIN performance_test.customers c ON o.customer_id = c.customer_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND c.country = 'USA'
  AND o.status = 'delivered';

-- 7.2 案例2：优化聚合查询
-- 原始查询
EXPLAIN ANALYZE
SELECT 
    c.country,
    c.city,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM performance_test.customers c
INNER JOIN performance_test.orders o ON c.customer_id = o.customer_id
GROUP BY c.country, c.city
ORDER BY total_revenue DESC
LIMIT 20;

-- 优化版本：预聚合
EXPLAIN ANALYZE
SELECT 
    country,
    city,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM (
    SELECT 
        c.country, 
        c.city, 
        o.total_amount
    FROM performance_test.customers c
    INNER JOIN performance_test.orders o ON c.customer_id = o.customer_id
    WHERE o.order_date >= '2024-01-01'
) subquery
GROUP BY country, city
ORDER BY total_revenue DESC
LIMIT 20;

-- ================================================
-- 8. 高级EXPLAIN分析
-- ================================================

-- 8.1 查看执行计划的层级结构
EXPLAIN (FORMAT TREE)
SELECT p.product_name, COUNT(oi.item_id) as sold_count
FROM performance_test.products p
INNER JOIN performance_test.order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
ORDER BY sold_count DESC
LIMIT 5;

-- 8.2 成本参数调优
-- 查看当前成本参数
SHOW work_mem;
SHOW random_page_cost;
SHOW effective_cache_size;

-- 模拟不同参数下的执行计划
SET work_mem = '4MB';
EXPLAIN ANALYZE
SELECT c.first_name, 
       COUNT(o.order_id) as order_count,
       SUM(o.total_amount) as total_spent
FROM performance_test.customers c
INNER JOIN performance_test.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name
ORDER BY total_spent DESC;

SET work_mem = '256MB';
EXPLAIN ANALYZE
SELECT c.first_name, 
       COUNT(o.order_id) as order_count,
       SUM(o.total_amount) as total_spent
FROM performance_test.customers c
INNER JOIN performance_test.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name
ORDER BY total_spent DESC;

-- 8.3 并行查询分析
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;
SET parallel_tuple_cost = 0.1;
SET parallel_setup_cost = 1000;

EXPLAIN ANALYZE
SELECT country, COUNT(*) as customer_count, AVG(total_spent) as avg_spent
FROM performance_test.customers
GROUP BY country
ORDER BY customer_count DESC;

-- ================================================
-- 9. 性能诊断函数
-- ================================================

-- 9.1 分析查询计划的关键指标
CREATE OR REPLACE FUNCTION analyze_query_plan(query_text TEXT)
RETURNS TABLE(
    total_cost NUMERIC,
    plan_type TEXT,
    rows_returned BIGINT,
    loops INTEGER,
    actual_time_ms NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        plan.total_cost,
        plan.plan_type,
        plan.rows_returned,
        plan.loops,
        plan.actual_time_ms
    FROM (
        EXECUTE 'EXPLAIN (ANALYZE, FORMAT JSON) ' || query_text
    ) AS result;
END;
$$ LANGUAGE plpgsql;

-- 9.2 检查索引使用情况
CREATE OR REPLACE FUNCTION check_index_usage(schema_name TEXT DEFAULT 'performance_test')
RETURNS TABLE(
    table_name TEXT,
    index_name TEXT,
    scans BIGINT,
    effectiveness NUMERIC,
    size_bytes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.relname::TEXT as table_name,
        i.indexname::TEXT as index_name,
        s.idx_scan as scans,
        CASE 
            WHEN s.idx_scan = 0 THEN 0
            ELSE s.idx_tup_fetch::NUMERIC / s.idx_scan
        END as effectiveness,
        pg_relation_size(i.indexrelid) as size_bytes
    FROM pg_class t
    JOIN pg_namespace n ON t.relnamespace = n.oid
    JOIN pg_index ix ON t.oid = ix.indrelid
    JOIN pg_class i ON i.oid = ix.indexrelid
    JOIN pg_stat_user_indexes s ON s.indexrelid = ix.indexrelid
    WHERE n.nspname = schema_name
      AND t.relkind = 'r'
    ORDER BY s.idx_scan ASC, pg_relation_size(i.indexrelid) DESC;
END;
$$ LANGUAGE plpgsql;

-- 使用诊断函数
-- SELECT * FROM analyze_query_plan('SELECT * FROM performance_test.orders WHERE customer_id = 1');
-- SELECT * FROM check_index_usage('performance_test');

-- ================================================
-- 10. 总结和最佳实践
-- ================================================

-- 10.1 查询优化的基本原则
/*
1. 优先使用索引而非全表扫描
2. 减少返回的列和数据量
3. 使用适当的连接类型
4. 优化WHERE条件顺序
5. 考虑数据分布和统计信息
6. 定期更新统计信息
7. 监控查询性能变化
8. 避免不必要的复杂查询
*/

-- 10.2 EXPLAIN分析技巧
/*
1. 使用ANALYZE获取实际执行时间
2. 关注成本最高的操作
3. 比较不同查询方式的成本
4. 检查索引是否被使用
5. 理解不同扫描类型的含义
6. 分析连接操作的效率
7. 监控并行查询的效果
8. 记录优化前后的性能对比
*/

-- 10.3 清理测试数据（可选）
-- 此操作会删除所有测试数据，请谨慎使用
/*
DROP SCHEMA IF EXISTS performance_test CASCADE;
*/
