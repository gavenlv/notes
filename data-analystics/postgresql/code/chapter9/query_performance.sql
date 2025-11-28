-- ================================================
-- PostgreSQL第9章：查询性能优化技巧和案例
-- ================================================
-- 本文件展示各种查询优化技术和实际案例

-- 清理环境
-- DROP TABLE IF EXISTS ecommerce_data CASCADE;
-- DROP SCHEMA IF EXISTS query_optimization CASCADE;

-- ================================================
-- 1. 查询优化基础
-- ================================================

-- 创建查询优化测试模式
CREATE SCHEMA IF NOT EXISTS query_optimization;
SET search_path TO query_optimization, public;

-- 创建测试表
CREATE TABLE sales_data (
    sale_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    sale_date DATE,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount GENERATED ALWAYS AS (quantity * unit_price) STORED,
    region VARCHAR(50),
    sales_rep VARCHAR(100)
);

CREATE TABLE customers_table (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200),
    email VARCHAR(100),
    country VARCHAR(50),
    registration_date DATE,
    customer_type VARCHAR(20)
);

CREATE TABLE products_table (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE inventory_table (
    product_id INTEGER REFERENCES products_table(product_id),
    warehouse_id INTEGER,
    quantity_available INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入大量测试数据
INSERT INTO customers_table (customer_name, email, country, registration_date, customer_type)
SELECT 
    'Customer ' || i,
    'customer' || i || '@company.com',
    CASE WHEN i % 5 = 0 THEN 'USA' WHEN i % 5 = 1 THEN 'Germany' WHEN i % 5 = 2 THEN 'UK' WHEN i % 5 = 3 THEN 'Japan' ELSE 'France' END,
    CURRENT_DATE - (random() * 365 * 3)::INTEGER,
    CASE WHEN random() < 0.3 THEN 'Premium' WHEN random() < 0.7 THEN 'Regular' ELSE 'Basic' END
FROM generate_series(1, 100000) AS i;

INSERT INTO products_table (product_name, category, brand, price)
SELECT 
    'Product ' || i,
    CASE WHEN i % 7 = 0 THEN 'Electronics' WHEN i % 7 = 1 THEN 'Clothing' WHEN i % 7 = 2 THEN 'Books' WHEN i % 7 = 3 THEN 'Home' WHEN i % 7 = 4 THEN 'Sports' WHEN i % 7 = 5 THEN 'Toys' ELSE 'Food' END,
    'Brand ' || (i % 50 + 1),
    (5 + random() * 995)::DECIMAL(10,2)
FROM generate_series(1, 50000) AS i;

INSERT INTO sales_data (customer_id, product_id, sale_date, quantity, unit_price, region, sales_rep)
SELECT 
    (i % 100000) + 1,
    (i % 50000) + 1,
    CURRENT_DATE - (random() * 365 * 2)::INTEGER,
    (random() * 10 + 1)::INTEGER,
    (10 + random() * 990)::DECIMAL(10,2),
    CASE WHEN i % 6 = 0 THEN 'North' WHEN i % 6 = 1 THEN 'South' WHEN i % 6 = 2 THEN 'East' WHEN i % 6 = 3 THEN 'West' WHEN i % 6 = 4 THEN 'Central' ELSE 'International' END,
    'Rep ' || (i % 200 + 1)
FROM generate_series(1, 500000) AS i;

INSERT INTO inventory_table (product_id, warehouse_id, quantity_available)
SELECT 
    (i % 50000) + 1,
    (i % 20) + 1,
    random() * 1000
FROM generate_series(1, 100000) AS i;

-- ================================================
-- 2. 避免常见性能陷阱
-- ================================================

-- 2.1 避免SELECT *
-- 原始查询（性能较差）
EXPLAIN ANALYZE
SELECT * FROM sales_data 
WHERE customer_id = 1000;

-- 优化后（只选择需要的列）
EXPLAIN ANALYZE
SELECT sale_id, sale_date, total_amount, region 
FROM sales_data 
WHERE customer_id = 1000;

-- 2.2 优化WHERE条件
-- 原始查询（复杂的WHERE条件）
EXPLAIN ANALYZE
SELECT * FROM sales_data s
JOIN customers_table c ON s.customer_id = c.customer_id
WHERE (c.country = 'USA' OR c.country = 'Germany') 
  AND s.sale_date >= '2023-01-01'
  AND s.total_amount > 100.00;

-- 优化后（使用IN替代OR）
EXPLAIN ANALYZE
SELECT s.sale_id, s.sale_date, c.customer_name, s.total_amount
FROM sales_data s
JOIN customers_table c ON s.customer_id = c.customer_id
WHERE c.country IN ('USA', 'Germany')
  AND s.sale_date >= '2023-01-01'
  AND s.total_amount > 100.00;

-- ================================================
-- 3. 连接优化技术
-- ================================================

-- 3.1 连接顺序优化
-- 创建必要的索引
CREATE INDEX idx_sales_customer_date ON sales_data(customer_id, sale_date);
CREATE INDEX idx_customers_country ON customers_table(country);
CREATE INDEX idx_sales_date_amount ON sales_data(sale_date, total_amount);

-- 优化前：小表作为驱动表
EXPLAIN ANALYZE
SELECT c.customer_name, s.total_amount
FROM sales_data s
JOIN customers_table c ON s.customer_id = c.customer_id
WHERE c.customer_type = 'Premium';

-- 优化后：让优化器选择最佳连接顺序
-- 注意：现代优化器通常能自动选择最佳连接顺序
EXPLAIN ANALYZE
SELECT c.customer_name, s.total_amount, s.sale_date
FROM customers_table c
JOIN sales_data s ON s.customer_id = c.customer_id
WHERE c.customer_type = 'Premium'
  AND s.sale_date >= '2024-01-01';

-- 3.2 减少连接操作
-- 原始查询（多层连接）
EXPLAIN ANALYZE
SELECT 
    c.customer_name,
    p.product_name,
    s.total_amount
FROM sales_data s
JOIN customers_table c ON s.customer_id = c.customer_id
JOIN products_table p ON s.product_id = p.product_id
WHERE c.country = 'USA'
  AND s.sale_date >= '2024-01-01'
ORDER BY s.total_amount DESC
LIMIT 100;

-- 优化后：使用子查询减少连接
EXPLAIN ANALYZE
SELECT 
    c.customer_name,
    p.product_name,
    s.total_amount
FROM (
    SELECT customer_id, product_id, total_amount
    FROM sales_data
    WHERE sale_date >= '2024-01-01'
) s
JOIN customers_table c ON s.customer_id = c.customer_id
JOIN products_table p ON s.product_id = p.product_id
WHERE c.country = 'USA'
ORDER BY s.total_amount DESC
LIMIT 100;

-- ================================================
-- 4. 聚合查询优化
-- ================================================

-- 4.1 使用索引优化聚合
-- 创建聚合索引
CREATE INDEX idx_sales_customer_amount ON sales_data(customer_id, total_amount);
CREATE INDEX idx_sales_date_category ON sales_data(sale_date, product_id);

-- 优化前：全表聚合
EXPLAIN ANALYZE
SELECT 
    customer_id,
    COUNT(*) as sale_count,
    SUM(total_amount) as total_spent,
    AVG(total_amount) as avg_order_value
FROM sales_data
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 100;

-- 优化后：使用索引预聚合
EXPLAIN ANALYZE
SELECT 
    customer_id,
    COUNT(*) as sale_count,
    SUM(total_amount) as total_spent,
    AVG(total_amount) as avg_order_value
FROM sales_data
WHERE sale_date >= '2024-01-01'
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 100;

-- 4.2 分区聚合（如果数据很大）
-- 创建按日期分区的表（假设PostgreSQL版本支持分区）
-- CREATE TABLE sales_data_partitioned (
--     sale_id SERIAL,
--     customer_id INTEGER,
--     product_id INTEGER,
--     sale_date DATE,
--     quantity INTEGER,
--     unit_price DECIMAL(10,2),
--     total_amount DECIMAL(12,2),
--     region VARCHAR(50),
--     sales_rep VARCHAR(100)
-- ) PARTITION BY RANGE (sale_date);

-- ================================================
-- 5. 子查询优化
-- ================================================

-- 5.1 将IN子查询转换为JOIN
-- 原始查询（使用IN）
EXPLAIN ANALYZE
SELECT customer_name, country, customer_type
FROM customers_table
WHERE customer_id IN (
    SELECT DISTINCT customer_id
    FROM sales_data
    WHERE total_amount > 1000.00
  AND sale_date >= '2024-01-01'
);

-- 优化后（使用EXISTS）
EXPLAIN ANALYZE
SELECT c.customer_name, c.country, c.customer_type
FROM customers_table c
WHERE EXISTS (
    SELECT 1 FROM sales_data s
    WHERE s.customer_id = c.customer_id
      AND s.total_amount > 1000.00
      AND s.sale_date >= '2024-01-01'
);

-- 5.2 优化相关子查询
-- 原始查询（相关子查询）
EXPLAIN ANALYZE
SELECT 
    c.customer_name,
    c.country,
    (
        SELECT SUM(s.total_amount)
        FROM sales_data s
        WHERE s.customer_id = c.customer_id
          AND s.sale_date >= '2024-01-01'
    ) as total_spent_2024
FROM customers_table c
WHERE c.customer_type = 'Premium';

-- 优化后（使用LEFT JOIN）
EXPLAIN ANALYZE
SELECT 
    c.customer_name,
    c.country,
    COALESCE(SUM(s.total_amount), 0) as total_spent_2024
FROM customers_table c
LEFT JOIN sales_data s ON s.customer_id = c.customer_id
  AND s.sale_date >= '2024-01-01'
WHERE c.customer_type = 'Premium'
GROUP BY c.customer_id, c.customer_name, c.country;

-- ================================================
-- 6. 分页查询优化
-- ================================================

-- 6.1 传统LIMIT/OFFSET的性能问题
-- 原始查询（OFFSET性能差）
EXPLAIN ANALYZE
SELECT customer_name, country, customer_type
FROM customers_table
ORDER BY customer_id
LIMIT 50 OFFSET 10000;

-- 优化后：使用WHERE子句进行游标分页
CREATE INDEX idx_customers_name ON customers_table(customer_name);
EXPLAIN ANALYZE
SELECT customer_name, country, customer_type
FROM customers_table
WHERE customer_name > (
    SELECT customer_name
    FROM customers_table
    ORDER BY customer_name
    LIMIT 1 OFFSET 9999
)
ORDER BY customer_name
LIMIT 50;

-- 6.2 使用键集分页
-- 为高效的键集分页创建索引
CREATE INDEX idx_customers_reg_date ON customers_table(registration_date, customer_id);

-- 键集分页查询
EXPLAIN ANALYZE
SELECT customer_name, country, registration_date
FROM customers_table
WHERE (registration_date, customer_id) > ('2023-06-15', 15000)
ORDER BY registration_date, customer_id
LIMIT 50;

-- ================================================
-- 7. 复杂查询优化案例
-- ================================================

-- 7.1 案例1：销售业绩分析
-- 原始复杂查询
EXPLAIN ANALYZE
SELECT 
    c.country,
    c.customer_type,
    p.category,
    COUNT(DISTINCT s.customer_id) as unique_customers,
    COUNT(s.sale_id) as total_orders,
    SUM(s.total_amount) as total_revenue,
    AVG(s.total_amount) as avg_order_value
FROM customers_table c
JOIN sales_data s ON c.customer_id = s.customer_id
JOIN products_table p ON s.product_id = p.product_id
WHERE s.sale_date >= '2023-01-01'
  AND s.sale_date < '2024-01-01'
GROUP BY c.country, c.customer_type, p.category
ORDER BY total_revenue DESC;

-- 优化1：分解为多个查询
-- 步骤1：先获取主要数据
CREATE TEMP TABLE sales_summary AS
SELECT 
    customer_id,
    country,
    customer_type,
    sale_date,
    product_id,
    total_amount
FROM sales_data s
JOIN customers_table c ON s.customer_id = c.customer_id
WHERE s.sale_date >= '2023-01-01'
  AND s.sale_date < '2024-01-01';

CREATE INDEX idx_sales_summary ON sales_summary(country, customer_type, product_id);

EXPLAIN ANALYZE
SELECT 
    country,
    customer_type,
    (SELECT category FROM products_table WHERE product_id = sales_summary.product_id) as category,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM sales_summary
GROUP BY country, customer_type, product_id
ORDER BY total_revenue DESC;

-- 7.2 案例2：库存预警查询
-- 原始查询（性能较差）
EXPLAIN ANALYZE
SELECT 
    p.product_name,
    p.category,
    i.quantity_available,
    SUM(s.quantity) as total_sold_last_30_days,
    CASE 
        WHEN SUM(s.quantity) > i.quantity_available * 0.8 THEN 'HIGH'
        WHEN SUM(s.quantity) > i.quantity_available * 0.5 THEN 'MEDIUM'
        ELSE 'LOW'
    END as reorder_priority
FROM products_table p
LEFT JOIN inventory_table i ON p.product_id = i.product_id
LEFT JOIN sales_data s ON p.product_id = s.product_id
  AND s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.product_id, p.product_name, p.category, i.quantity_available
HAVING SUM(s.quantity) > i.quantity_available * 0.3
ORDER BY reorder_priority, SUM(s.quantity) DESC;

-- 优化：预计算和物化视图
CREATE MATERIALIZED VIEW inventory_alert AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    COALESCE(i.quantity_available, 0) as quantity_available,
    COALESCE(s.total_sold_30d, 0) as total_sold_30_days,
    CASE 
        WHEN COALESCE(s.total_sold_30d, 0) > COALESCE(i.quantity_available, 0) * 0.8 THEN 'HIGH'
        WHEN COALESCE(s.total_sold_30d, 0) > COALESCE(i.quantity_available, 0) * 0.5 THEN 'MEDIUM'
        ELSE 'LOW'
    END as reorder_priority
FROM products_table p
LEFT JOIN (
    SELECT 
        product_id,
        SUM(quantity) as total_sold_30d
    FROM sales_data
    WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY product_id
) s ON p.product_id = s.product_id
LEFT JOIN inventory_table i ON p.product_id = i.product_id;

CREATE INDEX idx_inventory_alert ON inventory_alert(reorder_priority, total_sold_30_days);

-- 使用物化视图进行查询
EXPLAIN ANALYZE
SELECT *
FROM inventory_alert
WHERE reorder_priority IN ('HIGH', 'MEDIUM')
  AND total_sold_30_days > quantity_available * 0.3
ORDER BY reorder_priority, total_sold_30_days DESC;

-- ================================================
-- 8. 查询计划缓存和预编译
-- ================================================

-- 8.1 使用准备语句
-- PostgreSQL会自动缓存查询计划
PREPARE high_value_customers AS
SELECT customer_name, country, customer_type, total_spent
FROM customers_table c
LEFT JOIN (
    SELECT 
        customer_id,
        SUM(total_amount) as total_spent
    FROM sales_data
    WHERE sale_date >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY customer_id
) s ON c.customer_id = s.customer_id
WHERE total_spent > 10000;

-- 执行预编译查询
EXPLAIN ANALYZE EXECUTE high_value_customers;

-- 8.2 创建查询函数
CREATE OR REPLACE FUNCTION get_customer_sales_summary(
    p_customer_id INTEGER,
    p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '1 year',
    p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE(
    sale_date DATE,
    product_name VARCHAR(200),
    quantity INTEGER,
    total_amount DECIMAL(12,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.sale_date,
        p.product_name,
        s.quantity,
        s.total_amount
    FROM sales_data s
    JOIN products_table p ON s.product_id = p.product_id
    WHERE s.customer_id = p_customer_id
      AND s.sale_date BETWEEN p_start_date AND p_end_date
    ORDER BY s.sale_date DESC;
END;
$$ LANGUAGE plpgsql;

-- 测试函数性能
EXPLAIN ANALYZE
SELECT * FROM get_customer_sales_summary(1000);

-- ================================================
-- 9. 查询优化工具和函数
-- ================================================

-- 9.1 查询性能分析函数
CREATE OR REPLACE FUNCTION analyze_query_performance(query_text TEXT)
RETURNS TABLE(
    execution_info JSON
) AS $$
DECLARE
    plan_result JSON;
BEGIN
    EXECUTE 'EXPLAIN (FORMAT JSON) ' || query_text INTO plan_result;
    RETURN QUERY SELECT plan_result;
END;
$$ LANGUAGE plpgsql;

-- 9.2 批量查询性能测试
CREATE OR REPLACE FUNCTION benchmark_queries(queries TEXT[], iterations INTEGER DEFAULT 10)
RETURNS TABLE(
    query_number INTEGER,
    query_text TEXT,
    avg_time_ms NUMERIC,
    min_time_ms NUMERIC,
    max_time_ms NUMERIC
) AS $$
DECLARE
    query_text TEXT;
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    execution_times NUMERIC[];
    avg_time NUMERIC;
    min_time NUMERIC;
    max_time NUMERIC;
    query_num INTEGER := 1;
BEGIN
    FOREACH query_text IN ARRAY queries LOOP
        execution_times := array[]::NUMERIC[];
        
        FOR i IN 1..iterations LOOP
            start_time := clock_timestamp();
            EXECUTE query_text;
            end_time := clock_timestamp();
            execution_times := array_append(execution_times, 
                EXTRACT(EPOCH FROM (end_time - start_time)) * 1000);
        END LOOP;
        
        SELECT 
            AVG(execution_times) INTO avg_time,
            MIN(execution_times) INTO min_time,
            MAX(execution_times) INTO max_time
        FROM unnest(execution_times) as times;
        
        RETURN QUERY
        SELECT 
            query_num,
            query_text,
            avg_time,
            min_time,
            max_time;
        
        query_num := query_num + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 测试多个查询
-- SELECT * FROM benchmark_queries(ARRAY[
--     'SELECT COUNT(*) FROM sales_data',
--     'SELECT COUNT(DISTINCT customer_id) FROM sales_data',
--     'SELECT SUM(total_amount) FROM sales_data WHERE sale_date >= CURRENT_DATE - INTERVAL ''1 year'''
-- ], 5);

-- ================================================
-- 10. 实际性能优化建议
-- ================================================

-- 10.1 查询设计原则
/*
1. 明确查询目标，只返回必要的数据
2. 使用适当的索引支持查询模式
3. 避免在WHERE条件中使用函数
4. 利用统计信息帮助优化器
5. 定期分析查询执行计划
6. 监控慢查询并优化
7. 使用批量操作减少网络开销
8. 考虑查询结果缓存
*/

-- 10.2 监控和诊断
-- 启用查询统计
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看最耗时的查询
-- SELECT 
--     query,
--     calls,
--     total_time,
--     mean_time,
--     rows,
--     100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
-- FROM pg_stat_statements
-- ORDER BY total_time DESC
-- LIMIT 10;

-- 10.3 性能调优检查清单
/*
□ 检查是否使用了适当的索引
□ 避免SELECT *，只选择需要的列
□ 优化WHERE条件，使用IN代替OR
□ 减少不必要的连接操作
□ 使用子查询优化复杂逻辑
□ 考虑使用物化视图缓存结果
□ 定期更新表统计信息
□ 监控索引使用情况
□ 使用EXPLAIN ANALYZE验证优化效果
□ 设置合理的内存参数
*/

-- ================================================
-- 11. 清理环境（可选）
-- ================================================

-- 清理测试环境
/*
DROP SCHEMA IF EXISTS query_optimization CASCADE;
DROP MATERIALIZED VIEW IF EXISTS inventory_alert CASCADE;
DROP FUNCTION IF EXISTS analyze_query_performance(TEXT);
DROP FUNCTION IF EXISTS benchmark_queries(TEXT[], INTEGER);
DROP FUNCTION IF EXISTS get_customer_sales_summary(INTEGER, DATE, DATE);
DROP EXTENSION IF EXISTS pg_stat_statements;
*/
