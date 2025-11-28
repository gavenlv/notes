-- ================================================
-- PostgreSQL第9章：索引策略和优化技术
-- ================================================
-- 本文件演示各种索引类型的使用策略和优化技巧

-- ================================================
-- 1. 基础索引创建和优化
-- ================================================

-- 创建性能测试模式
CREATE SCHEMA IF NOT EXISTS index_optimization;
SET search_path TO index_optimization, public;

-- 创建基础测试表
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    registration_date DATE,
    country VARCHAR(50),
    city VARCHAR(50),
    total_purchases DECIMAL(12,2) DEFAULT 0
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE,
    status VARCHAR(20),
    total_amount DECIMAL(12,2),
    shipping_country VARCHAR(50)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(100),
    price DECIMAL(10,2),
    stock_quantity INTEGER,
    created_date DATE
);

-- 插入测试数据
INSERT INTO customers (email, first_name, last_name, registration_date, country, city, total_purchases)
SELECT 
    'user' || i || '@example.com',
    'FirstName' || i,
    'LastName' || i,
    CURRENT_DATE - (random() * 365)::INTEGER,
    CASE WHEN i % 5 = 0 THEN 'USA' WHEN i % 5 = 1 THEN 'China' WHEN i % 5 = 2 THEN 'UK' WHEN i % 5 = 3 THEN 'Germany' ELSE 'Japan' END,
    'City' || (i % 100),
    (random() * 10000)::DECIMAL(12,2)
FROM generate_series(1, 50000) AS i;

INSERT INTO products (name, category, price, stock_quantity, created_date)
SELECT 
    'Product ' || i,
    CASE WHEN i % 4 = 0 THEN 'Electronics' WHEN i % 4 = 1 THEN 'Clothing' WHEN i % 4 = 2 THEN 'Books' ELSE 'Home' END,
    (10 + random() * 990)::DECIMAL(10,2),
    random() * 1000,
    CURRENT_DATE - (random() * 1000)::INTEGER
FROM generate_series(1, 10000) AS i;

INSERT INTO orders (customer_id, order_date, status, total_amount, shipping_country)
SELECT 
    (i % 50000) + 1,
    CURRENT_DATE - (random() * 365)::INTEGER,
    CASE WHEN i % 6 = 0 THEN 'delivered' WHEN i % 6 = 1 THEN 'shipped' WHEN i % 6 = 2 THEN 'processing' WHEN i % 6 = 3 THEN 'cancelled' ELSE 'pending' END,
    (10 + random() * 990)::DECIMAL(12,2),
    CASE WHEN i % 5 = 0 THEN 'USA' WHEN i % 5 = 1 THEN 'China' WHEN i % 5 = 2 THEN 'UK' WHEN i % 5 = 3 THEN 'Germany' ELSE 'Japan' END
FROM generate_series(1, 100000) AS i;

-- ================================================
-- 2. 单列索引优化
-- ================================================

-- 2.1 基础单列索引
-- 适用于等值查询和范围查询
CREATE INDEX idx_customers_country ON customers(country);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_products_category ON products(category);

-- 2.2 唯一索引
-- 用于确保数据唯一性，同时提高查询性能
CREATE UNIQUE INDEX idx_customers_email ON customers(email);

-- 2.3 函数索引
-- 对表达式或函数结果建立索引
CREATE INDEX idx_customers_lower_email ON customers(lower(email));
CREATE INDEX idx_customers_full_name ON customers((first_name || ' ' || last_name));

-- 2.4 部分索引（条件索引）
-- 只对满足特定条件的行创建索引
CREATE INDEX idx_orders_high_value ON orders(customer_id) WHERE total_amount > 1000.00;
CREATE INDEX idx_customers_recent ON customers(customer_id) WHERE registration_date >= CURRENT_DATE - INTERVAL '1 year';

-- ================================================
-- 3. 复合索引（多列索引）
-- ================================================

-- 3.1 复合索引基础
-- 适用于多条件查询，列顺序很重要
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX idx_customers_country_city ON customers(country, city);
CREATE INDEX idx_products_category_price ON products(category, price);

-- 3.2 复合索引优化规则
/*
1. 高选择性列放在前面
2. 常用查询条件放在前面
3. 范围查询列放在最后
4. 考虑查询的WHERE子句顺序
*/

-- 3.3 验证复合索引效果
-- 单列索引查询
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 100;
-- 复合索引查询
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 100 AND order_date >= '2024-01-01';

-- ================================================
-- 4. 覆盖索引
-- ================================================

-- 4.1 覆盖索引定义
-- 索引包含查询所需的所有列，避免回表操作
CREATE INDEX idx_orders_covering ON orders(customer_id, order_date, status, total_amount);

-- 4.2 测试覆盖索引效果
-- 会使用覆盖索引（Index Only Scan）
EXPLAIN ANALYZE 
SELECT customer_id, order_date, status, total_amount
FROM orders 
WHERE customer_id BETWEEN 1000 AND 2000;

-- 不会使用覆盖索引（需要回表）
EXPLAIN ANALYZE 
SELECT * FROM orders 
WHERE customer_id BETWEEN 1000 AND 2000;

-- ================================================
-- 5. 特殊索引类型
-- ================================================

-- 5.1 空间索引（如果启用PostGIS）
-- CREATE EXTENSION IF NOT EXISTS postgis;
-- CREATE TABLE locations (
--     location_id SERIAL PRIMARY KEY,
--     name VARCHAR(100),
--     coordinates GEOMETRY(Point, 4326)
-- );
-- CREATE INDEX idx_locations_coordinates ON locations USING GIST(coordinates);

-- 5.2 文本搜索索引
-- 使用全文搜索
CREATE INDEX idx_products_name_fts ON products USING GIN(to_tsvector('english', name));
CREATE INDEX idx_products_category_fts ON products USING GIN(to_tsvector('english', category));

-- 5.3 数组索引
CREATE TABLE orders_with_array (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    product_ids INTEGER[]
);
CREATE INDEX idx_orders_product_ids ON orders_with_array USING GIN(product_ids);

-- ================================================
-- 6. 索引维护和优化
-- ================================================

-- 6.1 索引膨胀分析
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    pg_size_pretty(pg_total_relation_size(indexrelid)) as total_size,
    idx_scan as index_scans
FROM pg_stat_user_indexes
WHERE schemaname = 'index_optimization'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 6.2 检查未使用的索引
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    CASE 
        WHEN idx_scan = 0 THEN 'Unused'
        WHEN idx_scan < 10 THEN 'Rarely used'
        ELSE 'In use'
    END as usage_status
FROM pg_stat_user_indexes
WHERE schemaname = 'index_optimization'
  AND indexname NOT LIKE '%_pkey%';

-- 6.3 索引统计信息
SELECT 
    t.relname as table_name,
    i.relname as index_name,
    s.idx_scan as index_scans,
    s.idx_tup_read as tuples_read,
    s.idx_tup_fetch as tuples_fetched,
    CASE 
        WHEN s.idx_scan > 0 THEN s.idx_tup_fetch::NUMERIC / s.idx_scan
        ELSE 0
    END as avg_tuples_per_scan
FROM pg_class t
JOIN pg_namespace n ON t.relnamespace = n.oid
JOIN pg_index ix ON t.oid = ix.indrelid
JOIN pg_class i ON i.oid = ix.indexrelid
JOIN pg_stat_user_indexes s ON s.indexrelid = ix.indexrelid
WHERE n.nspname = 'index_optimization'
ORDER BY s.idx_scan DESC;

-- ================================================
-- 7. 索引创建时机和策略
-- ================================================

-- 7.1 查询模式分析
-- 分析查询日志，找出最频繁的查询模式
CREATE VIEW frequent_queries AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE calls > 100
ORDER BY total_time DESC
LIMIT 20;

-- 7.2 根据查询模式创建索引
-- 如果经常查询某个组合，创建复合索引
CREATE INDEX idx_customers_recent_high_value ON customers(country, total_purchases) 
WHERE registration_date >= CURRENT_DATE - INTERVAL '6 months' 
  AND total_purchases > 1000;

-- ================================================
-- 8. 索引优化案例
-- ================================================

-- 8.1 案例1：优化客户查询
-- 原始查询（无索引）
EXPLAIN ANALYZE 
SELECT * FROM customers 
WHERE country = 'USA' 
  AND registration_date >= '2024-01-01'
ORDER BY total_purchases DESC;

-- 优化1：添加单列索引
CREATE INDEX idx_customers_country_reg_date ON customers(country, registration_date);
EXPLAIN ANALYZE 
SELECT customer_id, first_name, total_purchases 
FROM customers 
WHERE country = 'USA' 
  AND registration_date >= '2024-01-01'
ORDER BY total_purchases DESC;

-- 8.2 案例2：优化订单查询
-- 分析订单查询模式
SELECT 
    status,
    COUNT(*) as order_count,
    AVG(total_amount) as avg_amount
FROM orders
GROUP BY status;

-- 为频繁状态创建部分索引
CREATE INDEX idx_orders_pending ON orders(customer_id, order_date) 
WHERE status = 'pending';
CREATE INDEX idx_orders_delivered ON orders(customer_id, order_date) 
WHERE status = 'delivered';

-- ================================================
-- 9. 索引性能测试
-- ================================================

-- 9.1 基准测试函数
CREATE OR REPLACE FUNCTION benchmark_index_performance(
    table_name TEXT,
    query_conditions TEXT,
    iterations INTEGER DEFAULT 1000
)
RETURNS TABLE(
    query_type TEXT,
    avg_time_ms NUMERIC,
    min_time_ms NUMERIC,
    max_time_ms NUMERIC
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    execution_times NUMERIC[];
    i INTEGER;
    query_text TEXT;
BEGIN
    -- 测试有索引的查询
    query_text := 'SELECT * FROM ' || table_name || ' WHERE ' || query_conditions;
    
    FOR i IN 1..iterations LOOP
        start_time := clock_timestamp();
        EXECUTE query_text;
        end_time := clock_timestamp();
        execution_times := array_append(execution_times, EXTRACT(EPOCH FROM (end_time - start_time)) * 1000);
    END LOOP;
    
    RETURN QUERY
    SELECT 
        'With Index'::TEXT as query_type,
        AVG(execution_times)::NUMERIC as avg_time_ms,
        MIN(execution_times)::NUMERIC as min_time_ms,
        MAX(execution_times)::NUMERIC as max_time_ms
    FROM unnest(execution_times) as times;
END;
$$ LANGUAGE plpgsql;

-- 9.2 性能对比测试
-- DROP INDEX idx_customers_country;
-- SELECT * FROM benchmark_index_performance('customers', 'country = ''USA''', 100);

-- CREATE INDEX idx_customers_country ON customers(country);
-- SELECT * FROM benchmark_index_performance('customers', 'country = ''USA''', 100);

-- ================================================
-- 10. 索引最佳实践
-- ================================================

-- 10.1 索引选择指南
/*
1. 经常在WHERE子句中使用的列
2. 经常用于JOIN连接的列
3. 经常在ORDER BY子句中的列
4. 经常在GROUP BY子句中的列
5. 高基数（唯一值多）的列
6. 考虑维护成本vs查询收益
*/

-- 10.2 索引创建原则
/*
1. 小表通常不需要索引
2. 避免为低选择性列创建索引
3. 定期分析和更新统计信息
4. 监控索引使用情况
5. 删除不使用的索引
6. 考虑索引顺序的重要性
7. 使用部分索引减少空间
8. 考虑覆盖索引避免回表
*/

-- 10.3 索引维护计划
/*
-- 定期执行的任务：
REINDEX INDEX index_name;           -- 重建索引
ANALYZE table_name;                 -- 更新统计信息
SELECT pg_stat_reset();             -- 重置统计信息（谨慎使用）
*/

-- 10.4 监控索引健康状况
CREATE VIEW index_health_check AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    CASE 
        WHEN idx_scan = 0 THEN 'RED - Unused'
        WHEN idx_scan < 100 THEN 'YELLOW - Low usage'
        ELSE 'GREEN - In use'
    END as health_status,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'index_optimization'
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;

-- 查看索引健康状况
-- SELECT * FROM index_health_check;

-- ================================================
-- 11. 清理环境（可选）
-- ================================================

-- 清理测试环境
/*
DROP SCHEMA IF EXISTS index_optimization CASCADE;
DROP VIEW IF EXISTS frequent_queries, index_health_check;
DROP FUNCTION IF EXISTS benchmark_index_performance(text, text, integer);
*/
