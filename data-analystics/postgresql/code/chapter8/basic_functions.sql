-- PostgreSQL教程第8章：存储过程和函数 - 基础函数演示

-- 创建测试表
CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    hire_date DATE DEFAULT CURRENT_DATE,
    job_id VARCHAR(10),
    salary DECIMAL(10,2),
    commission_pct DECIMAL(5,2),
    manager_id INTEGER,
    department_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    manager_id INTEGER,
    location VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清空表并插入测试数据
TRUNCATE employees CASCADE;
TRUNCATE departments CASCADE;

INSERT INTO departments (department_name, manager_id, location) VALUES
('IT', 1001, 'Beijing'),
('Sales', 1002, 'Shanghai'),
('HR', 1003, 'Guangzhou'),
('Finance', 1004, 'Shenzhen');

INSERT INTO employees (first_name, last_name, email, phone, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES
('John', 'Smith', 'john.smith@company.com', '13800138001', '2020-01-15', 'SE', 12000.00, NULL, 1001, 1),
('Jane', 'Doe', 'jane.doe@company.com', '13800138002', '2020-02-20', 'SA', 8000.00, 0.05, 1002, 2),
('Bob', 'Johnson', 'bob.johnson@company.com', '13800138003', '2019-05-10', 'SE', 15000.00, NULL, 1001, 1),
('Alice', 'Brown', 'alice.brown@company.com', '13800138004', '2021-03-12', 'HR', 9000.00, NULL, 1003, 3),
('Charlie', 'Wilson', 'charlie.wilson@company.com', '13800138005', '2018-07-25', 'FM', 18000.00, NULL, 1004, 4);

-- 1. 基础函数创建

-- 1.1 简单的标量函数
CREATE OR REPLACE FUNCTION get_employee_count()
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM employees);
END;
$$ LANGUAGE plpgsql;

-- 调用函数
SELECT get_employee_count();

-- 1.2 带参数的基础函数
CREATE OR REPLACE FUNCTION calculate_bonus(p_salary DECIMAL, p_commission_pct DECIMAL DEFAULT 0)
RETURNS DECIMAL AS $$
BEGIN
    RETURN p_salary * (p_commission_pct / 100);
END;
$$ LANGUAGE plpgsql;

-- 测试函数
SELECT 
    first_name,
    last_name,
    salary,
    commission_pct,
    calculate_bonus(salary, commission_pct) as bonus
FROM employees;

-- 1.3 返回记录的函数
CREATE OR REPLACE FUNCTION get_employee_details(p_employee_id INTEGER)
RETURNS TABLE (
    employee_id INTEGER,
    full_name VARCHAR(100),
    email VARCHAR(100),
    job_title VARCHAR(10),
    department_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name as full_name,
        e.email,
        e.job_id,
        d.department_name
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.department_id
    WHERE e.employee_id = p_employee_id;
END;
$$ LANGUAGE plpgsql;

-- 调用返回记录的函数
SELECT * FROM get_employee_details(1);

-- 1.4 返回集合的函数
CREATE OR REPLACE FUNCTION get_high_salary_employees(p_min_salary DECIMAL DEFAULT 10000)
RETURNS SETOF employees AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM employees
    WHERE salary >= p_min_salary
    ORDER BY salary DESC;
END;
$$ LANGUAGE plpgsql;

-- 调用返回集合的函数
SELECT * FROM get_high_salary_employees(12000);

-- 2. 参数类型和默认值

-- 2.1 带有默认参数值的函数
CREATE OR REPLACE FUNCTION calculate_total_salary(
    p_base_salary DECIMAL,
    p_bonus DECIMAL DEFAULT 0,
    p_commission DECIMAL DEFAULT 0
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN p_base_salary + p_bonus + p_commission;
END;
$$ LANGUAGE plpgsql;

-- 测试不同参数组合
SELECT 
    calculate_total_salary(10000) as basic_salary,
    calculate_total_salary(10000, 1000) as with_bonus,
    calculate_total_salary(10000, 1000, 500) as with_commission;

-- 2.2 参数模式：IN、OUT、INOUT
CREATE OR REPLACE FUNCTION calculate_net_salary(
    IN p_gross_salary DECIMAL,
    IN p_tax_rate DECIMAL DEFAULT 0.1,
    IN p_insurance_rate DECIMAL DEFAULT 0.075,
    OUT net_salary DECIMAL,
    OUT tax_amount DECIMAL,
    OUT insurance_amount DECIMAL
) AS $$
BEGIN
    tax_amount := p_gross_salary * p_tax_rate;
    insurance_amount := p_gross_salary * p_insurance_rate;
    net_salary := p_gross_salary - tax_amount - insurance_amount;
END;
$$ LANGUAGE plpgsql;

-- 调用OUT参数函数
SELECT 
    first_name,
    salary as gross_salary,
    calculate_net_salary(salary).*
FROM employees;

-- 2.3 使用INOUT参数的函数
CREATE OR REPLACE FUNCTION increment_value(INOUT value INTEGER, increment_by INTEGER DEFAULT 1)
AS $$
BEGIN
    value := value + increment_by;
END;
$$ LANGUAGE plpgsql;

-- 测试INOUT参数
DO $$
DECLARE
    test_value INTEGER := 10;
BEGIN
    PERFORM increment_value(test_value, 5);
    RAISE NOTICE 'Incremented value: %', test_value;
END $$;

-- 3. 变量声明和赋值

-- 3.1 基础变量声明
CREATE OR REPLACE FUNCTION get_employee_statistics()
RETURNS TABLE (
    total_count INTEGER,
    avg_salary DECIMAL,
    max_salary DECIMAL,
    min_salary DECIMAL
) AS $$
DECLARE
    v_total INTEGER;
    v_avg_salary DECIMAL;
    v_max_salary DECIMAL;
    v_min_salary DECIMAL;
BEGIN
    -- 使用SELECT INTO赋值
    SELECT COUNT(*), AVG(salary), MAX(salary), MIN(salary)
    INTO v_total, v_avg_salary, v_max_salary, v_min_salary
    FROM employees;
    
    RETURN QUERY SELECT v_total, v_avg_salary, v_max_salary, v_min_salary;
END;
$$ LANGUAGE plpgsql;

-- 3.2 使用记录类型
CREATE OR REPLACE FUNCTION get_employee_by_id(p_employee_id INTEGER)
RETURNS employees AS $$
DECLARE
    emp_record employees%ROWTYPE;
BEGIN
    SELECT * INTO emp_record
    FROM employees
    WHERE employee_id = p_employee_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee with ID % not found', p_employee_id;
    END IF;
    
    RETURN emp_record;
END;
$$ LANGUAGE plpgsql;

-- 4. 控制结构

-- 4.1 IF-THEN-ELSE条件语句
CREATE OR REPLACE FUNCTION get_salary_level(p_salary DECIMAL)
RETURNS VARCHAR(20) AS $$
DECLARE
    v_level VARCHAR(20);
BEGIN
    IF p_salary >= 15000 THEN
        v_level := 'High';
    ELSIF p_salary >= 10000 THEN
        v_level := 'Medium';
    ELSIF p_salary >= 5000 THEN
        v_level := 'Low';
    ELSE
        v_level := 'Very Low';
    END IF;
    
    RETURN v_level;
END;
$$ LANGUAGE plpgsql;

-- 测试条件语句
SELECT 
    first_name,
    salary,
    get_salary_level(salary) as salary_level
FROM employees;

-- 4.2 CASE语句
CREATE OR REPLACE FUNCTION get_department_bonus(p_department_id INTEGER)
RETURNS DECIMAL AS $$
DECLARE
    v_bonus_rate DECIMAL;
BEGIN
    CASE p_department_id
        WHEN 1 THEN v_bonus_rate := 0.15;  -- IT
        WHEN 2 THEN v_bonus_rate := 0.20;  -- Sales
        WHEN 3 THEN v_bonus_rate := 0.10;  -- HR
        WHEN 4 THEN v_bonus_rate := 0.18;  -- Finance
        ELSE v_badge_rate := 0.05;
    END CASE;
    
    RETURN v_bonus_rate;
END;
$$ LANGUAGE plpgsql;

-- 4.3 循环语句

-- 4.3.1 LOOP循环
CREATE OR REPLACE FUNCTION factorial(n INTEGER)
RETURNS BIGINT AS $$
DECLARE
    i INTEGER;
    result BIGINT := 1;
BEGIN
    IF n < 0 THEN
        RAISE EXCEPTION 'Factorial is not defined for negative numbers';
    END IF;
    
    i := 1;
    LOOP
        result := result * i;
        i := i + 1;
        EXIT WHEN i > n;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 4.3.2 WHILE循环
CREATE OR REPLACE FUNCTION count_primes(limit INTEGER)
RETURNS INTEGER AS $$
DECLARE
    i INTEGER := 2;
    count INTEGER := 0;
    j INTEGER;
    is_prime BOOLEAN;
BEGIN
    WHILE i <= limit LOOP
        is_prime := TRUE;
        j := 2;
        
        WHILE j * j <= i LOOP
            IF i % j = 0 THEN
                is_prime := FALSE;
                EXIT;
            END IF;
            j := j + 1;
        END LOOP;
        
        IF is_prime THEN
            count := count + 1;
        END IF;
        
        i := i + 1;
    END LOOP;
    
    RETURN count;
END;
$$ LANGUAGE plpgsql;

-- 4.3.3 FOR循环（遍历查询结果）
CREATE OR REPLACE FUNCTION list_employee_names()
RETURNS TEXT AS $$
DECLARE
    emp_record RECORD;
    name_list TEXT := '';
BEGIN
    FOR emp_record IN 
        SELECT first_name, last_name 
        FROM employees 
        ORDER BY last_name, first_name
    LOOP
        name_list := name_list || emp_record.first_name || ' ' || emp_record.last_name || ', ';
    END LOOP;
    
    -- 移除最后的逗号
    IF LENGTH(name_list) > 0 THEN
        name_list := SUBSTRING(name_list FROM 1 FOR LENGTH(name_list) - 2);
    END IF;
    
    RETURN name_list;
END;
$$ LANGUAGE plpgsql;

-- 5. 异常处理

-- 5.1 基本异常处理
CREATE OR REPLACE FUNCTION divide_numbers(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE EXCEPTION 'Division by zero is not allowed';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'An error occurred: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 5.2 自定义异常处理
CREATE OR REPLACE FUNCTION update_salary(p_employee_id INTEGER, new_salary DECIMAL)
RETURNS VARCHAR(50) AS $$
DECLARE
    current_salary DECIMAL;
BEGIN
    -- 检查员工是否存在
    SELECT salary INTO current_salary
    FROM employees
    WHERE employee_id = p_employee_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee with ID % does not exist', p_employee_id;
    END IF;
    
    -- 检查新工资是否合理
    IF new_salary < 0 THEN
        RAISE EXCEPTION 'Salary cannot be negative';
    END IF;
    
    IF new_salary > current_salary * 2 THEN
        RAISE EXCEPTION 'Salary increase cannot exceed 100%%';
    END IF;
    
    -- 更新工资
    UPDATE employees
    SET salary = new_salary,
        updated_at = CURRENT_TIMESTAMP
    WHERE employee_id = p_employee_id;
    
    RETURN 'Salary updated successfully';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 6. 动态SQL

-- 6.1 使用EXECUTE执行动态SQL
CREATE OR REPLACE FUNCTION execute_dynamic_query(p_table_name VARCHAR, p_column_name VARCHAR, p_value VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    query_string TEXT;
    row_count INTEGER;
BEGIN
    query_string := 'DELETE FROM ' || quote_ident(p_table_name) || 
                   ' WHERE ' || quote_ident(p_column_name) || ' = $1';
    
    EXECUTE query_string INTO row_count USING p_value;
    
    RETURN row_count;
END;
$$ LANGUAGE plpgsql;

-- 6.2 动态表查询
CREATE OR REPLACE FUNCTION get_table_info(p_table_name VARCHAR)
RETURNS TABLE (
    column_name VARCHAR,
    data_type VARCHAR,
    is_nullable VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    EXECUTE 'SELECT column_name::VARCHAR, data_type::VARCHAR, is_nullable::VARCHAR
             FROM information_schema.columns
             WHERE table_name = $1'
    USING p_table_name;
END;
$$ LANGUAGE plpgsql;

-- 7. 数组和集合操作

-- 7.1 数组参数函数
CREATE OR REPLACE FUNCTION calculate_average(numbers INTEGER[])
RETURNS DECIMAL AS $$
DECLARE
    sum INTEGER := 0;
    count INTEGER := 0;
    num INTEGER;
BEGIN
    FOREACH num IN ARRAY numbers LOOP
        sum := sum + num;
        count := count + 1;
    END LOOP;
    
    IF count = 0 THEN
        RETURN 0;
    END IF;
    
    RETURN sum::DECIMAL / count;
END;
$$ LANGUAGE plpgsql;

-- 7.2 返回数组的函数
CREATE OR REPLACE FUNCTION get_employee_ids_by_department(p_department_id INTEGER)
RETURNS INTEGER[] AS $$
DECLARE
    id_array INTEGER[] := '{}';
    emp_id INTEGER;
BEGIN
    FOR emp_id IN 
        SELECT employee_id 
        FROM employees 
        WHERE department_id = p_department_id
        ORDER BY employee_id
    LOOP
        id_array := array_append(id_array, emp_id);
    END LOOP;
    
    RETURN id_array;
END;
$$ LANGUAGE plpgsql;

-- 8. 递归函数

-- 8.1 递归计算斐波那契数列
CREATE OR REPLACE FUNCTION fibonacci(n INTEGER)
RETURNS INTEGER AS $$
BEGIN
    IF n <= 0 THEN
        RETURN 0;
    ELSIF n = 1 THEN
        RETURN 1;
    ELSE
        RETURN fibonacci(n - 1) + fibonacci(n - 2);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 8.2 递归遍历组织结构
CREATE OR REPLACE FUNCTION get_subordinates(p_manager_id INTEGER)
RETURNS TABLE (
    employee_id INTEGER,
    first_name VARCHAR,
    last_name VARCHAR,
    manager_id INTEGER,
    level_depth INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE employee_hierarchy AS (
        -- 基础查询：直接下属
        SELECT 
            e.employee_id,
            e.first_name,
            e.last_name,
            e.manager_id,
            1 as level_depth
        FROM employees e
        WHERE e.manager_id = p_manager_id
        
        UNION ALL
        
        -- 递归部分：下属的下属
        SELECT 
            e.employee_id,
            e.first_name,
            e.last_name,
            e.manager_id,
            eh.level_depth + 1
        FROM employees e
        JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
    )
    SELECT * FROM employee_hierarchy;
END;
$$ LANGUAGE plpgsql;

-- 9. 触发器相关函数

-- 9.1 审计日志函数
CREATE OR REPLACE FUNCTION audit_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE NOTICE 'Employee deleted: % %', OLD.first_name, OLD.last_name;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        RAISE NOTICE 'Employee updated: % %', NEW.first_name, NEW.last_name;
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        RAISE NOTICE 'Employee inserted: % %', NEW.first_name, NEW.last_name;
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 9.2 自动更新updated_at列
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 10. 性能测试和函数使用

-- 10.1 创建测试视图
CREATE OR REPLACE VIEW employee_summary AS
SELECT 
    d.department_name,
    COUNT(e.employee_id) as employee_count,
    AVG(e.salary) as avg_salary,
    MAX(e.salary) as max_salary,
    MIN(e.salary) as min_salary
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;

-- 10.2 函数性能对比
CREATE OR REPLACE FUNCTION get_dept_salary_info_sql()
RETURNS TABLE (
    department_name VARCHAR,
    employee_count BIGINT,
    avg_salary NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        es.department_name,
        es.employee_count,
        es.avg_salary
    FROM employee_summary es;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_dept_salary_info_function()
RETURNS TABLE (
    department_name VARCHAR,
    employee_count BIGINT,
    avg_salary NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.department_name,
        COUNT(e.employee_id) as employee_count,
        ROUND(AVG(e.salary), 2) as avg_salary
    FROM departments d
    LEFT JOIN employees e ON d.department_id = e.department_id
    GROUP BY d.department_name
    ORDER BY d.department_name;
END;
$$ LANGUAGE plpgsql;

-- 11. 测试函数

-- 测试所有创建的函数
SELECT '=== 测试基础函数 ===' as test_section;
SELECT get_employee_count() as total_employees;
SELECT * FROM get_employee_details(1);

SELECT '=== 测试参数函数 ===' as test_section;
SELECT calculate_bonus(10000, 0.10) as bonus;
SELECT calculate_total_salary(10000, 1000, 500) as total_salary;
SELECT calculate_net_salary(10000).*;

SELECT '=== 测试控制结构 ===' as test_section;
SELECT factorial(5) as factorial_5;
SELECT count_primes(20) as prime_count_up_to_20;

SELECT '=== 测试递归 ===' as test_section;
SELECT fibonacci(10) as fibonacci_10;
SELECT * FROM get_subordinates(1001);

SELECT '=== 测试性能对比 ===' as test_section;
SELECT * FROM get_dept_salary_info_sql();
SELECT * FROM get_dept_salary_info_function();

SELECT '=== 测试异常处理 ===' as test_section;
SELECT divide_numbers(10, 2) as division_result;
SELECT update_salary(1, 25000) as update_result;

SELECT '=== 测试数组函数 ===' as test_section;
SELECT calculate_average(ARRAY[1, 2, 3, 4, 5]) as array_average;
SELECT get_employee_ids_by_department(1) as dept_1_employee_ids;

-- 12. 清理测试数据（可选）
-- 注意：在生产环境中请谨慎执行删除操作
/*
DROP FUNCTION IF EXISTS get_employee_count() CASCADE;
DROP FUNCTION IF EXISTS calculate_bonus(DECIMAL, DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS get_employee_details(INTEGER) CASCADE;
-- ... (更多清理语句)
*/