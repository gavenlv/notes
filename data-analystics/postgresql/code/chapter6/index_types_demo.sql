-- 第6章：索引和性能优化 - 索引类型演示

-- 创建示例表和数据
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department_id INTEGER NOT NULL,
    salary DECIMAL(10,2),
    hire_date DATE,
    location POINT,  -- 用于GiST索引演示
    skills TEXT[],    -- 用于GIN索引演示
    profile JSONB,    -- 用于GIN索引演示
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 插入示例数据
INSERT INTO departments (name, description) VALUES 
('Engineering', 'Software development team'),
('Marketing', 'Marketing and promotion team'),
('Sales', 'Sales and business development'),
('HR', 'Human resources management'),
('Finance', 'Financial management');

-- 插入大量员工数据用于性能测试
INSERT INTO employees (name, email, department_id, salary, hire_date, location, skills, profile, is_active)
SELECT 
    'Employee_' || i,
    'employee' || i || '@company.com',
    (RANDOM() * 4)::INTEGER + 1,
    (RANDOM() * 80000 + 20000)::DECIMAL(10,2),
    CURRENT_DATE - (RANDOM() * 1825)::INTEGER,  -- 过去5年内
    POINT(RANDOM() * 360 - 180, RANDOM() * 180 - 90),  -- 经纬度坐标
    CASE (RANDOM() * 3)::INTEGER
        WHEN 0 THEN ARRAY['SQL', 'Python', 'Java']
        WHEN 1 THEN ARRAY['JavaScript', 'React', 'Node.js']
        ELSE ARRAY['Java', 'Spring', 'Microservices']
    END,
    jsonb_build_object(
        'experience', (RANDOM() * 20)::INTEGER,
        'certifications', ARRAY['AWS', 'PostgreSQL', 'Docker'][(RANDOM() * 2 + 1)::INTEGER],
        'languages', CASE (RANDOM() * 2)::INTEGER WHEN 0 THEN '["English", "Spanish"]' ELSE '["English", "Chinese", "Japanese"]' END
    ),
    CASE WHEN RANDOM() > 0.1 THEN true ELSE false END  -- 90%员工活跃
FROM generate_series(1, 100000);

-- 1. B-Tree索引演示
-- 创建标准B-Tree索引
CREATE INDEX idx_employees_name ON employees (name);
CREATE INDEX idx_employees_department ON employees (department_id);
CREATE INDEX idx_employees_salary ON employees (salary);
CREATE INDEX idx_employees_hire_date ON employees (hire_date);

-- 复合B-Tree索引
CREATE INDEX idx_employees_dept_salary ON employees (department_id, salary);
CREATE INDEX idx_employees_dept_hire ON employees (department_id, hire_date);

-- 降序索引
CREATE INDEX idx_employees_salary_desc ON employees (salary DESC);

-- 唯一索引
-- (email列已经有UNIQUE约束，这里演示如何创建唯一索引)
-- CREATE UNIQUE INDEX idx_employees_email_unique ON employees (email);

-- 2. Hash索引演示
-- 创建Hash索引（仅适用于等值查询）
CREATE INDEX idx_employees_name_hash ON employees USING HASH (name);

-- 3. GiST索引演示
-- 创建几何数据GiST索引
CREATE INDEX idx_employees_location ON employees USING GIST (location);

-- 4. GIN索引演示
-- 数组列的GIN索引
CREATE INDEX idx_employees_skills ON employees USING GIN (skills);

-- JSONB列的GIN索引
CREATE INDEX idx_employees_profile ON employees USING GIN (profile);
CREATE INDEX idx_employees_profile_experience ON employees USING GIN ((profile->'experience'));

-- 5. 表达式索引演示
-- 基于表达式的索引
CREATE INDEX idx_employees_name_upper ON employees (UPPER(name));
CREATE INDEX idx_employees_hire_year ON employees (EXTRACT(YEAR FROM hire_date));
CREATE INDEX idx_employees_name_length ON employees (LENGTH(name));

-- 6. 部分索引演示
-- 只为活跃员工创建索引
CREATE INDEX idx_active_employees_dept ON employees (department_id) WHERE is_active = true;
CREATE INDEX idx_active_employees_salary ON employees (salary) WHERE is_active = true AND salary > 50000;

-- 7. BRIN索引演示
-- 创建BRIN索引（适合大表的时间序列数据）
CREATE INDEX idx_employees_hire_date_brin ON employees USING BRIN (hire_date);
CREATE INDEX idx_employees_salary_brin ON employees USING BRIN (salary);

-- 性能测试和对比

-- 测试1：基本索引查询性能
EXPLAIN ANALYZE 
SELECT * FROM employees 
WHERE department_id = 1 AND salary > 60000
ORDER BY salary DESC;

-- 测试2：复合索引使用情况
EXPLAIN ANALYZE 
SELECT * FROM employees 
WHERE department_id = 1
ORDER BY salary DESC;

-- 测试3：范围查询
EXPLAIN ANALYZE 
SELECT * FROM employees 
WHERE hire_date >= '2020-01-01' AND hire_date <= '2023-12-31';

-- 测试4：数组查询
EXPLAIN ANALYZE 
SELECT name, skills 
FROM employees 
WHERE skills @> ARRAY['Python'];

-- 测试5：JSON查询
EXPLAIN ANALYZE 
SELECT name, profile->'experience' as experience
FROM employees 
WHERE profile->>'certifications' = 'PostgreSQL';

-- 测试6：文本搜索
EXPLAIN ANALYZE 
SELECT name 
FROM employees 
WHERE UPPER(name) LIKE 'EMPLOYEE_%';

-- 测试7：部分索引使用情况
EXPLAIN ANALYZE 
SELECT * FROM employees 
WHERE is_active = true AND department_id = 1;

-- 测试8：非活跃员工的查询（不会使用部分索引）
EXPLAIN ANALYZE 
SELECT * FROM employees 
WHERE is_active = false AND department_id = 1;

-- 检查索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'employees'
ORDER BY idx_scan DESC;

-- 查看表和索引大小
SELECT 
    n.nspname as schema_name,
    c.relname as table_name,
    c.relnatts as column_count,
    c.reln_tup_id as live_tuples,
    c.reln_dead_tup as dead_tuples,
    pg_size_pretty(pg_relation_size(c.oid)) as table_size,
    pg_size_pretty(pg_total_relation_size(c.oid)) as total_size
FROM pg_class c
LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relname = 'employees'
ORDER BY pg_total_relation_size(c.oid) DESC;

-- 查看索引详情
SELECT 
    i.relname as index_name,
    a.attname as column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
    CASE WHEN x.indisprimary THEN 'PRIMARY'
         WHEN x.indisunique THEN 'UNIQUE'
         ELSE ''
    END as constraint_type
FROM pg_class t
JOIN pg_index x ON t.oid = x.indrelid
JOIN pg_class i ON i.oid = x.indexrelid
JOIN pg_attribute a ON a.attrelid = t.oid
WHERE t.relname = 'employees' AND a.attnum = ANY(x.indkey) AND t.relkind = 'r'
ORDER BY i.relname, a.attnum;

-- 清理示例（保留表结构以便后续测试）
-- DROP TABLE IF EXISTS employees, departments;