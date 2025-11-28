-- 第6章：索引和性能优化 - 性能分析和执行计划演示

-- 确保使用示例表
-- 如果employees表不存在，先运行index_types_demo.sql中的创建语句

-- 1. 基础执行计划分析

-- 查询1：简单查询
EXPLAIN 
SELECT * FROM employees 
WHERE id = 50000;

-- 查询2：带WHERE条件的查询
EXPLAIN 
SELECT name, salary, hire_date 
FROM employees 
WHERE department_id = 2 AND salary > 60000
ORDER BY salary DESC;

-- 查询3：聚合查询
EXPLAIN ANALYZE
SELECT department_id, 
       COUNT(*) as employee_count,
       AVG(salary) as avg_salary,
       MIN(salary) as min_salary,
       MAX(salary) as max_salary
FROM employees
GROUP BY department_id
ORDER BY avg_salary DESC;

-- 2. 连接查询执行计划

-- 创建关联表用于连接测试
CREATE TABLE department_stats (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL,
    total_budget DECIMAL(15,2),
    manager_name VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO department_stats (department_id, total_budget, manager_name) VALUES
(1, 500000.00, 'John Smith'),
(2, 300000.00, 'Sarah Johnson'),
(3, 400000.00, 'Mike Davis'),
(4, 200000.00, 'Lisa Wilson'),
(5, 250000.00, 'Tom Brown');

-- 简单连接查询
EXPLAIN ANALYZE
SELECT 
    e.name,
    e.salary,
    d.name as department_name,
    ds.total_budget,
    ds.manager_name
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN department_stats ds ON e.department_id = ds.department_id
WHERE e.salary > 70000
ORDER BY e.salary DESC;

-- 3. 子查询执行计划

-- 相关子查询
EXPLAIN ANALYZE
SELECT 
    e.name,
    e.salary,
    e.department_id,
    (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id) as dept_avg_salary,
    (SELECT COUNT(*) FROM employees WHERE department_id = e.department_id) as dept_employee_count
FROM employees e
WHERE e.salary > 70000
ORDER BY e.salary DESC;

-- 非相关子查询
EXPLAIN ANALYZE
SELECT 
    name,
    salary,
    department_id
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;

-- 4. 复杂查询执行计划分析

-- 4.1 窗口函数查询
EXPLAIN ANALYZE
SELECT 
    name,
    department_id,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as salary_rank,
    PERCENT_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as salary_percentile
FROM employees
WHERE department_id = 1
ORDER BY salary_rank;

-- 4.2 CTE（公用表表达式）
EXPLAIN ANALYZE
WITH high_salary_employees AS (
    SELECT 
        name,
        department_id,
        salary,
        hire_date
    FROM employees
    WHERE salary > 70000
),
dept_avg AS (
    SELECT 
        department_id,
        AVG(salary) as avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT 
    hse.name,
    hse.salary,
    d.name as department_name,
    da.avg_salary,
    hse.salary - da.avg_salary as salary_diff
FROM high_salary_employees hse
JOIN departments d ON hse.department_id = d.id
JOIN dept_avg da ON hse.department_id = da.department_id
ORDER BY hse.salary DESC;

-- 5. 执行计划性能对比

-- 5.1 删除索引后的性能对比
-- 首先分析有索引时的查询
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE department_id = 1 AND salary BETWEEN 50000 AND 80000;

-- 删除索引
DROP INDEX IF EXISTS idx_employees_dept_salary;
DROP INDEX IF EXISTS idx_employees_salary;

-- 分析无索引时的查询
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE department_id = 1 AND salary BETWEEN 50000 AND 80000;

-- 重新创建索引
CREATE INDEX idx_employees_dept_salary ON employees (department_id, salary);

-- 5.2 索引类型性能对比
-- 测试B-Tree索引
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE name = 'Employee_50000';

-- 创建Hash索引并测试
CREATE INDEX idx_employees_name_hash ON employees USING HASH (name);
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE name = 'Employee_50000';

-- 6. 查询优化器设置影响

-- 6.1 禁用某个查询优化器规则
-- 关闭连接重排序优化
SET enable_material = off;
EXPLAIN ANALYZE
SELECT 
    e.name,
    d.name as department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE e.salary > 70000;

-- 恢复设置
RESET enable_material;

-- 6.2 设置不同的查询优化策略
-- 设置成本参数
SET random_page_cost = 1.0;  -- SSD环境
EXPLAIN ANALYZE
SELECT * FROM employees 
WHERE salary > 70000
ORDER BY salary DESC;

-- 7. 高级性能分析

-- 7.1 分区表性能分析（如果支持）
-- 创建分区表示例
CREATE TABLE employees_partitioned (
    LIKE employees INCLUDING ALL
) PARTITION BY RANGE (hire_date);

-- 创建月度分区
CREATE TABLE employees_2023_01 PARTITION OF employees_partitioned
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
CREATE TABLE employees_2023_02 PARTITION OF employees_partitioned
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

-- 分析分区表查询
EXPLAIN ANALYZE
SELECT COUNT(*) FROM employees_partitioned
WHERE hire_date >= '2023-01-01' AND hire_date < '2023-02-01';

-- 8. 统计信息分析

-- 查看表统计信息
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename = 'employees';

-- 查看列统计信息
SELECT 
    attname,
    inherited,
    null_frac,
    avg_width,
    n_distinct,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE tablename = 'employees'
ORDER BY attname;

-- 查看索引统计信息
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'employees'
ORDER BY idx_scan DESC;

-- 9. 实际性能测试

-- 9.1 大批量数据操作性能
\timing on
-- 插入大量数据测试
INSERT INTO employees (name, email, department_id, salary, hire_date)
SELECT 
    'Test_' || i,
    'test' || i || '@company.com',
    (RANDOM() * 4)::INTEGER + 1,
    (RANDOM() * 80000 + 20000)::DECIMAL(10,2),
    CURRENT_DATE
FROM generate_series(1, 10000);
\timing off

-- 9.2 复杂查询性能测试
\timing on
SELECT 
    d.name,
    COUNT(*) as employee_count,
    AVG(e.salary) as avg_salary,
    STRING_AGG(DISTINCT e.skills::text, ', ') as common_skills
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.is_active = true
GROUP BY d.id, d.name
HAVING COUNT(*) > 1000
ORDER BY avg_salary DESC;
\timing off

-- 10. 查询建议和优化提示

-- 基于实际统计信息提供优化建议
WITH index_usage AS (
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_scan,
        pg_relation_size(indexrelid) as index_size
    FROM pg_stat_user_indexes
    WHERE tablename = 'employees'
),
table_stats AS (
    SELECT 
        schemaname,
        tablename,
        n_live_tup as row_count,
        pg_relation_size(c.oid) as table_size
    FROM pg_stat_user_tables st
    JOIN pg_class c ON c.relname = st.tablename
    WHERE tablename = 'employees'
)
SELECT 
    iu.indexname,
    iu.index_size,
    iu.idx_scan,
    CASE 
        WHEN iu.idx_scan = 0 THEN 'Unused - Consider dropping'
        WHEN iu.idx_scan < 10 THEN 'Low usage - Monitor'
        ELSE 'Active index'
    END as usage_status,
    ROUND(iu.idx_scan * 100.0 / NULLIF((SELECT row_count FROM table_stats ts WHERE ts.tablename = iu.tablename), 0), 2) as scan_to_rows_ratio
FROM index_usage iu
ORDER BY iu.idx_scan;