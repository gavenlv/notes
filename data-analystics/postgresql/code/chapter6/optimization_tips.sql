-- 第6章：索引和性能优化 - 查询优化技巧演示

-- 1. 基本查询优化原则

-- 1.1 选择最有效率的表名顺序
-- 基础表（只返回少量记录）放在FROM子句的后面
-- 连接表时将范围小的表（记录条数少）作为基础表

-- 差的示例：基础表放在前面
EXPLAIN ANALYZE
SELECT e.name, d.name 
FROM employees e, departments d 
WHERE e.department_id = d.id AND d.id = 1;

-- 好的示例：基础表放在后面
EXPLAIN ANALYZE
SELECT e.name, d.name 
FROM departments d, employees e 
WHERE d.id = 1 AND e.department_id = d.id;

-- 1.2 WHERE子句优化

-- 差的示例：使用函数
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE UPPER(name) = 'EMPLOYEE_50000';

-- 好的示例：避免在WHERE子句中使用函数
CREATE INDEX idx_employees_name_upper ON employees ((UPPER(name)));
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE UPPER(name) = 'EMPLOYEE_50000';

-- 1.3 避免使用OR，用UNION ALL替代

-- 差的示例：使用OR
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE department_id = 1 OR department_id = 2 OR salary > 80000;

-- 好的示例：使用UNION ALL（如果OR条件使用索引查询）
EXPLAIN ANALYZE
SELECT * FROM employees WHERE department_id = 1
UNION ALL
SELECT * FROM employees WHERE department_id = 2
UNION ALL
SELECT * FROM employees WHERE salary > 80000;

-- 2. 索引优化技巧

-- 2.1 复合索引最佳实践
-- 原则：精确匹配左前缀、等值查询优先、范围查询在后

-- 创建演示表
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    region VARCHAR(50),
    salesperson VARCHAR(100),
    sale_date DATE,
    amount DECIMAL(10,2),
    customer_type VARCHAR(20)
);

-- 插入测试数据
INSERT INTO sales (region, salesperson, sale_date, amount, customer_type)
SELECT 
    CASE (RANDOM() * 4)::INTEGER
        WHEN 0 THEN 'North'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'East'
        WHEN 3 THEN 'West'
    END,
    'SalesPerson_' || (RANDOM() * 10)::INTEGER,
    '2023-01-01'::DATE + (RANDOM() * 365)::INTEGER,
    (RANDOM() * 10000 + 100)::DECIMAL(10,2),
    CASE (RANDOM() * 2)::INTEGER
        WHEN 0 THEN 'Corporate'
        WHEN 1 THEN 'Individual'
    END
FROM generate_series(1, 10000);

-- 2.1.1 错误的复合索引顺序
CREATE INDEX idx_sales_bad ON sales (customer_type, region, sale_date);

-- 2.1.2 正确的复合索引顺序（常用查询模式）
-- 如果经常查询：region = ? AND sale_date BETWEEN ? AND ?
CREATE INDEX idx_sales_region_date ON sales (region, sale_date);
-- 如果经常查询：region = ? AND salesperson = ? ORDER BY sale_date
CREATE INDEX idx_sales_person_date ON sales (region, salesperson, sale_date);

-- 测试索引效果
EXPLAIN ANALYZE
SELECT * FROM sales 
WHERE region = 'North' AND sale_date BETWEEN '2023-06-01' AND '2023-12-31'
ORDER BY sale_date;

-- 2.2 表达式索引

-- 2.2.1 对计算结果建立索引
CREATE INDEX idx_sales_month ON sales (EXTRACT(MONTH FROM sale_date));

-- 2.2.2 对字符串函数建立索引
CREATE INDEX idx_sales_salesperson_lower ON sales (LOWER(salesperson));

-- 测试表达式索引
EXPLAIN ANALYZE
SELECT * FROM sales 
WHERE EXTRACT(MONTH FROM sale_date) = 6
ORDER BY sale_date;

-- 2.3 部分索引（条件索引）

-- 2.3.1 只对活跃记录建立索引
CREATE INDEX idx_sales_active ON sales (region, sale_date) WHERE amount > 5000;

-- 2.3.2 对特定类型的数据建立索引
CREATE INDEX idx_sales_corporate ON sales (salesperson) WHERE customer_type = 'Corporate';

-- 测试部分索引
EXPLAIN ANALYZE
SELECT * FROM sales 
WHERE region = 'North' AND amount > 5000;

-- 3. 查询重写技巧

-- 3.1 用IN替代EXISTS（通常IN在子查询表较小的情况下更快）

-- EXISTS示例
EXPLAIN ANALYZE
SELECT * FROM employees e
WHERE EXISTS (
    SELECT 1 FROM sales s 
    WHERE s.salesperson = e.name
);

-- IN示例（当子查询结果较少时更快）
EXPLAIN ANALYZE
SELECT * FROM employees e
WHERE e.name IN (
    SELECT DISTINCT salesperson FROM sales
);

-- 3.2 用UNION ALL替代UNION（避免去重操作）

-- UNION示例（会进行去重）
EXPLAIN ANALYZE
SELECT name FROM employees WHERE department_id = 1
UNION
SELECT name FROM employees WHERE salary > 70000;

-- UNION ALL示例（不进行去重，速度更快）
EXPLAIN ANALYZE
SELECT name FROM employees WHERE department_id = 1
UNION ALL
SELECT name FROM employees WHERE salary > 70000;

-- 4. 表结构优化

-- 4.1 避免在WHERE子句中使用NULL值判断
-- 创建测试表
CREATE TABLE test_null (
    id SERIAL PRIMARY KEY,
    value1 INTEGER,
    value2 INTEGER
);

INSERT INTO test_null (value1, value2)
SELECT (RANDOM() * 100)::INTEGER, (RANDOM() * 100)::INTEGER
FROM generate_series(1, 1000);

-- 添加NULL值
UPDATE test_null SET value2 = NULL WHERE id % 5 = 0;

-- 创建NOT NULL约束的索引
CREATE INDEX idx_test_value1 ON test_null (value1);

-- 差的示例：在WHERE中使用IS NULL
EXPLAIN ANALYZE
SELECT * FROM test_null WHERE value2 IS NOT NULL AND value1 > 50;

-- 好的示例：使用NOT NULL约束或检查约束
-- 创建检查约束
ALTER TABLE test_null ADD CONSTRAINT chk_value2_not_null CHECK (value2 IS NOT NULL);

-- 4.2 规范化vs反规范化

-- 4.2.1 高度规范化的表结构（查询较慢）
CREATE TABLE orders_normalized (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE,
    total_amount DECIMAL(10,2)
);

CREATE TABLE order_items_normalized (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders_normalized(order_id),
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2)
);

-- 4.2.2 反规范化表（查询更快）
CREATE TABLE orders_denormalized (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    order_date DATE,
    total_amount DECIMAL(10,2),
    item_count INTEGER,
    avg_item_price DECIMAL(10,2),
    total_items_value DECIMAL(10,2)
);

-- 5. 分区表优化

-- 5.1 创建按时间分区的表
CREATE TABLE sales_partitioned (
    id SERIAL PRIMARY KEY,
    region VARCHAR(50),
    salesperson VARCHAR(100),
    sale_date DATE,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

-- 创建月度分区
CREATE TABLE sales_2023_01 PARTITION OF sales_partitioned
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');

CREATE TABLE sales_2023_02 PARTITION OF sales_partitioned
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

-- 创建季度分区模板
CREATE TABLE sales_q1_2023 PARTITION OF sales_partitioned
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

-- 6. 统计信息和ANALYZE

-- 6.1 手动更新统计信息
ANALYZE employees;
ANALYZE sales;

-- 6.2 自动统计信息更新配置
-- 查看当前统计信息设置
SHOW autovacuum;
SHOW auto_analyze;

-- 7. 连接池和缓存

-- 7.1 连接池建议
-- 使用pgBouncer或类似工具管理连接

-- 7.2 共享缓冲区配置
-- 查看当前配置
SHOW shared_buffers;
SHOW effective_cache_size;
SHOW work_mem;

-- 建议设置（根据系统内存调整）
-- shared_buffers = 25% of RAM
-- effective_cache_size = 75% of RAM
-- work_mem = available memory / max_connections

-- 8. 实际优化案例

-- 8.1 优化慢查询
-- 原始慢查询
EXPLAIN ANALYZE
SELECT 
    s.region,
    s.salesperson,
    SUM(s.amount) as total_sales,
    COUNT(*) as sale_count,
    AVG(s.amount) as avg_sale_amount
FROM sales s
WHERE s.sale_date >= '2023-01-01' 
  AND s.sale_date < '2024-01-01'
  AND s.amount > 1000
GROUP BY s.region, s.salesperson
ORDER BY total_sales DESC
LIMIT 10;

-- 优化后的查询（添加索引）
CREATE INDEX idx_sales_date_amount ON sales (sale_date, amount, region, salesperson);

-- 8.2 优化JOIN查询
-- 原始查询
EXPLAIN ANALYZE
SELECT 
    d.name as department,
    e.name as employee,
    e.salary,
    COUNT(s.id) as sales_count,
    SUM(s.amount) as total_sales
FROM departments d
JOIN employees e ON d.id = e.department_id
LEFT JOIN sales s ON s.salesperson = e.name
WHERE d.id = 1
GROUP BY d.name, e.name, e.salary
ORDER BY total_sales DESC NULLS LAST;

-- 优化建议：添加合适的索引
CREATE INDEX idx_sales_salesperson ON sales (salesperson);
CREATE INDEX idx_employees_dept ON employees (department_id);

-- 9. 监控和维护

-- 9.1 检查未使用的索引
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan < 10
ORDER BY pg_relation_size(indexrelid) DESC;

-- 9.2 检查统计信息
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC;

-- 10. 性能调优检查清单

/*
性能调优检查清单：

1. 索引优化：
   □ 检查是否有合适的索引
   □ 检查索引使用情况
   □ 删除未使用的索引
   □ 确保复合索引的顺序正确

2. 查询优化：
   □ 避免在WHERE子句中使用函数
   □ 使用EXPLAIN ANALYZE分析查询
   □ 重写低效的SQL语句
   □ 使用合适的数据类型

3. 表结构优化：
   □ 规范化设计
   □ 考虑反规范化以提高查询性能
   □ 使用分区表处理大表
   □ 适当的NOT NULL约束

4. 配置优化：
   □ 调整shared_buffers
   □ 调整work_mem
   □ 配置autovacuum
   □ 启用合适的统计信息

5. 监控和维护：
   □ 定期运行ANALYZE
   □ 监控慢查询
   □ 维护索引
   □ 检查表膨胀
*/