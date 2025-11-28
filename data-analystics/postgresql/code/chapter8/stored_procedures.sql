-- PostgreSQL教程第8章：存储过程

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
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    manager_id INTEGER,
    location VARCHAR(50),
    budget DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(20),
    employee_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清空表并插入测试数据
TRUNCATE audit_log CASCADE;
TRUNCATE employees CASCADE;
TRUNCATE departments CASCADE;

INSERT INTO departments (department_name, manager_id, location, budget) VALUES
('IT Department', 1001, 'Beijing', 500000.00),
('Sales Department', 1002, 'Shanghai', 800000.00),
('HR Department', 1003, 'Guangzhou', 300000.00),
('Finance Department', 1004, 'Shenzhen', 600000.00);

INSERT INTO employees (first_name, last_name, email, phone, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES
('John', 'Smith', 'john.smith@company.com', '13800138001', '2020-01-15', 'SE', 12000.00, NULL, 1001, 1),
('Jane', 'Doe', 'jane.doe@company.com', '13800138002', '2020-02-20', 'SA', 8000.00, 0.05, 1002, 2),
('Bob', 'Johnson', 'bob.johnson@company.com', '13800138003', '2019-05-10', 'SE', 15000.00, NULL, 1001, 1),
('Alice', 'Brown', 'alice.brown@company.com', '13800138004', '2021-03-12', 'HR', 9000.00, NULL, 1003, 3),
('Charlie', 'Wilson', 'charlie.wilson@company.com', '13800138005', '2018-07-25', 'FM', 18000.00, NULL, 1004, 4);

-- 1. 基础存储过程

-- 1.1 无参数存储过程
CREATE OR REPLACE PROCEDURE initialize_database()
LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Initializing database...';
    
    -- 重置员工状态
    UPDATE employees SET status = 'active', updated_at = CURRENT_TIMESTAMP;
    
    -- 清空审计日志
    TRUNCATE audit_log;
    
    RAISE NOTICE 'Database initialization completed';
END;
$$;

-- 调用存储过程
CALL initialize_database();

-- 1.2 带输入参数的存储过程
CREATE OR REPLACE PROCEDURE add_employee(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_email VARCHAR,
    p_job_id VARCHAR,
    p_salary DECIMAL,
    p_department_id INTEGER,
    p_manager_id INTEGER DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    new_employee_id INTEGER;
BEGIN
    -- 参数验证
    IF p_first_name IS NULL OR TRIM(p_first_name) = '' THEN
        RAISE EXCEPTION 'First name cannot be empty';
    END IF;
    
    IF p_last_name IS NULL OR TRIM(p_last_name) = '' THEN
        RAISE EXCEPTION 'Last name cannot be empty';
    END IF;
    
    IF p_email IS NULL OR TRIM(p_email) = '' THEN
        RAISE EXCEPTION 'Email cannot be empty';
    END IF;
    
    IF p_salary IS NULL OR p_salary <= 0 THEN
        RAISE EXCEPTION 'Salary must be greater than 0';
    END IF;
    
    -- 检查邮箱唯一性
    IF EXISTS (SELECT 1 FROM employees WHERE email = p_email) THEN
        RAISE EXCEPTION 'Email % already exists', p_email;
    END IF;
    
    -- 检查部门是否存在
    IF NOT EXISTS (SELECT 1 FROM departments WHERE department_id = p_department_id) THEN
        RAISE EXCEPTION 'Department with ID % does not exist', p_department_id;
    END IF;
    
    -- 插入新员工
    INSERT INTO employees (
        first_name, last_name, email, job_id, salary, 
        department_id, manager_id, hire_date
    ) VALUES (
        p_first_name, p_last_name, p_email, p_job_id, p_salary,
        p_department_id, p_manager_id, CURRENT_DATE
    ) RETURNING employee_id INTO new_employee_id;
    
    RAISE NOTICE 'Employee added successfully with ID: %', new_employee_id;
    
END;
$$;

-- 调用存储过程
CALL add_employee('David', 'Chen', 'david.chen@company.com', 'DE', 14000.00, 1, 1001);
CALL add_employee('Eva', 'Liu', 'eva.liu@company.com', 'MK', 9500.00, 2, 1002);

-- 1.3 带输出参数的存储过程
CREATE OR REPLACE PROCEDURE calculate_employee_stats(
    p_employee_id INTEGER,
    OUT total_compensation DECIMAL,
    OUT annual_bonus DECIMAL,
    OUT salary_grade VARCHAR(10)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_salary DECIMAL;
    v_commission DECIMAL;
    v_bonus_rate DECIMAL;
BEGIN
    -- 获取员工薪资信息
    SELECT salary, commission_pct
    INTO v_salary, v_commission
    FROM employees
    WHERE employee_id = p_employee_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee with ID % not found', p_employee_id;
    END IF;
    
    -- 计算总补偿
    v_commission := COALESCE(v_commission, 0);
    total_compensation := v_salary + (v_salary * v_commission);
    
    -- 计算年度奖金
    IF v_salary >= 15000 THEN
        v_bonus_rate := 0.20;
    ELSIF v_salary >= 10000 THEN
        v_bonus_rate := 0.15;
    ELSIF v_salary >= 5000 THEN
        v_bonus_rate := 0.10;
    ELSE
        v_bonus_rate := 0.05;
    END IF;
    
    annual_bonus := v_salary * v_bonus_rate;
    
    -- 确定薪资等级
    IF v_salary >= 15000 THEN
        salary_grade := 'A+';
    ELSIF v_salary >= 12000 THEN
        salary_grade := 'A';
    ELSIF v_salary >= 10000 THEN
        salary_grade := 'B+';
    ELSIF v_salary >= 8000 THEN
        salary_grade := 'B';
    ELSIF v_salary >= 5000 THEN
        salary_grade := 'C';
    ELSE
        salary_grade := 'D';
    END IF;
    
    RAISE NOTICE 'Calculated stats for employee %: Compensation=%, Bonus=%, Grade=%', 
        p_employee_id, total_compensation, annual_bonus, salary_grade;
        
END;
$$;

-- 调用存储过程
CALL calculate_employee_stats(1, NULL, NULL, NULL);

-- 2. 复杂业务逻辑存储过程

-- 2.1 员工转部门存储过程
CREATE OR REPLACE PROCEDURE transfer_employee(
    p_employee_id INTEGER,
    p_new_department_id INTEGER,
    p_new_manager_id INTEGER DEFAULT NULL,
    p_salary_adjustment DECIMAL DEFAULT 0
)
LANGUAGE plpgsql AS $$
DECLARE
    v_current_department INTEGER;
    v_current_salary DECIMAL;
    v_new_salary DECIMAL;
BEGIN
    -- 获取员工当前信息
    SELECT department_id, salary
    INTO v_current_department, v_current_salary
    FROM employees
    WHERE employee_id = p_employee_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee with ID % not found', p_employee_id;
    END IF;
    
    -- 检查是否已在目标部门
    IF v_current_department = p_new_department_id THEN
        RAISE NOTICE 'Employee is already in the target department';
        RETURN;
    END IF;
    
    -- 检查目标部门是否存在
    IF NOT EXISTS (SELECT 1 FROM departments WHERE department_id = p_new_department_id) THEN
        RAISE EXCEPTION 'Target department with ID % does not exist', p_new_department_id;
    END IF;
    
    -- 计算新薪资
    v_new_salary := v_current_salary + p_salary_adjustment;
    
    IF v_new_salary < 0 THEN
        RAISE EXCEPTION 'Salary adjustment would result in negative salary';
    END IF;
    
    -- 开始事务
    BEGIN
        -- 更新员工信息
        UPDATE employees
        SET 
            department_id = p_new_department_id,
            manager_id = p_new_manager_id,
            salary = v_new_salary,
            updated_at = CURRENT_TIMESTAMP
        WHERE employee_id = p_employee_id;
        
        -- 记录审计日志
        INSERT INTO audit_log (
            table_name, operation, employee_id, old_values, new_values, changed_by
        ) VALUES (
            'employees', 'TRANSFER', p_employee_id,
            jsonb_build_object('department_id', v_current_department, 'salary', v_current_salary),
            jsonb_build_object('department_id', p_new_department_id, 'salary', v_new_salary),
            CURRENT_USER
        );
        
        RAISE NOTICE 'Employee % transferred from department % to % with salary adjustment: %', 
            p_employee_id, v_current_department, p_new_department_id, p_salary_adjustment;
            
    EXCEPTION WHEN OTHERS THEN
        RAISE EXCEPTION 'Transfer failed: %', SQLERRM;
    END;
    
END;
$$;

-- 测试员工转部门
CALL transfer_employee(2, 4, 1004, 2000.00);  -- 将Jane Doe转到Finance部门，薪资+2000

-- 2.2 批量薪资调整存储过程
CREATE OR REPLACE PROCEDURE bulk_salary_adjustment(
    p_department_id INTEGER,
    p_adjustment_percentage DECIMAL,
    p_min_salary DECIMAL DEFAULT NULL,
    p_max_salary DECIMAL DEFAULT NULL,
    OUT employees_updated INTEGER,
    OUT total_increase DECIMAL
)
LANGUAGE plpgsql AS $$
DECLARE
    emp_record RECORD;
    v_old_salary DECIMAL;
    v_new_salary DECIMAL;
    v_increase DECIMAL;
BEGIN
    employees_updated := 0;
    total_increase := 0;
    
    -- 遍历符合条件的员工
    FOR emp_record IN 
        SELECT employee_id, salary
        FROM employees
        WHERE department_id = p_department_id
          AND status = 'active'
          AND (p_min_salary IS NULL OR salary >= p_min_salary)
          AND (p_max_salary IS NULL OR salary <= p_max_salary)
    LOOP
        v_old_salary := emp_record.salary;
        v_new_salary := v_old_salary * (1 + p_adjustment_percentage / 100);
        v_increase := v_new_salary - v_old_salary;
        
        -- 更新薪资
        UPDATE employees
        SET salary = v_new_salary,
            updated_at = CURRENT_TIMESTAMP
        WHERE employee_id = emp_record.employee_id;
        
        -- 记录审计日志
        INSERT INTO audit_log (
            table_name, operation, employee_id, old_values, new_values, changed_by
        ) VALUES (
            'employees', 'SALARY_ADJUSTMENT', emp_record.employee_id,
            jsonb_build_object('salary', v_old_salary),
            jsonb_build_object('salary', v_new_salary),
            CURRENT_USER
        );
        
        employees_updated := employees_updated + 1;
        total_increase := total_increase + v_increase;
        
        RAISE NOTICE 'Updated employee %: % -> % (increase: %)', 
            emp_record.employee_id, v_old_salary, v_new_salary, v_increase;
    END LOOP;
    
    RAISE NOTICE 'Bulk salary adjustment completed. Employees updated: %, Total increase: %', 
        employees_updated, total_increase;
        
END;
$$;

-- 测试批量薪资调整
CALL bulk_salary_adjustment(1, 5.0, NULL, NULL);  -- IT部门所有员工薪资增长5%

-- 2.3 绩效评估存储过程
CREATE OR REPLACE PROCEDURE process_performance_review(
    p_employee_id INTEGER,
    p_performance_score INTEGER,
    p_review_comments TEXT,
    OUT review_id INTEGER,
    OUT new_salary DECIMAL,
    OUT promotion_eligible BOOLEAN
)
LANGUAGE plpgsql AS $$
DECLARE
    v_current_salary DECIMAL;
    v_current_department INTEGER;
    v_bonus_percentage DECIMAL;
    v_salary_increase DECIMAL;
    v_years_employed INTEGER;
    v_bonus_amount DECIMAL;
BEGIN
    -- 验证绩效评分
    IF p_performance_score < 1 OR p_performance_score > 5 THEN
        RAISE EXCEPTION 'Performance score must be between 1 and 5';
    END IF;
    
    -- 获取员工当前信息
    SELECT salary, department_id, hire_date
    INTO v_current_salary, v_current_department, NULL  -- hire_date will be used for years calculation
    FROM employees
    WHERE employee_id = p_employee_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee with ID % not found', p_employee_id;
    END IF;
    
    -- 计算工作年限
    SELECT EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date))::INTEGER
    INTO v_years_employed
    FROM employees WHERE employee_id = p_employee_id;
    
    -- 根据绩效评分确定奖金比例
    CASE p_performance_score
        WHEN 5 THEN v_bonus_percentage := 0.20;
        WHEN 4 THEN v_bonus_percentage := 0.15;
        WHEN 3 THEN v_bonus_percentage := 0.10;
        WHEN 2 THEN v_bonus_percentage := 0.05;
        WHEN 1 THEN v_bonus_percentage := 0.00;
    END CASE;
    
    -- 计算奖金
    v_bonus_amount := v_current_salary * v_bonus_percentage;
    
    -- 判断是否晋升
    promotion_eligible := FALSE;
    IF p_performance_score >= 4 AND v_years_employed >= 2 THEN
        promotion_eligible := TRUE;
        
        -- 给予薪资增长
        CASE p_performance_score
            WHEN 5 THEN v_salary_increase := 0.15;
            WHEN 4 THEN v_salary_increase := 0.10;
        END CASE;
        
        new_salary := v_current_salary * (1 + v_salary_increase);
        
        -- 更新薪资
        UPDATE employees
        SET salary = new_salary,
            updated_at = CURRENT_TIMESTAMP
        WHERE employee_id = p_employee_id;
        
        RAISE NOTICE 'Employee % promoted with %%% salary increase', 
            p_employee_id, (v_salary_increase * 100);
    ELSE
        new_salary := v_current_salary;
        RAISE NOTICE 'Employee % not eligible for promotion', p_employee_id;
    END IF;
    
    -- 记录绩效评估到审计日志
    INSERT INTO audit_log (
        table_name, operation, employee_id, new_values, changed_by
    ) VALUES (
        'employees', 'PERFORMANCE_REVIEW', p_employee_id,
        jsonb_build_object(
            'performance_score', p_performance_score,
            'review_comments', p_review_comments,
            'bonus_amount', v_bonus_amount,
            'promotion_eligible', promotion_eligible,
            'new_salary', new_salary
        ),
        CURRENT_USER
    );
    
    review_id := (SELECT MAX(log_id) FROM audit_log WHERE operation = 'PERFORMANCE_REVIEW');
    
    RAISE NOTICE 'Performance review completed for employee %: Score=%, Bonus=%, Promotion=%', 
        p_employee_id, p_performance_score, v_bonus_amount, promotion_eligible;
        
END;
$$;

-- 测试绩效评估
CALL process_performance_review(1, 4, 'Excellent performance this year', NULL, NULL, NULL);

-- 3. 数据维护存储过程

-- 3.1 数据清理存储过程
CREATE OR REPLACE PROCEDURE cleanup_old_audit_logs(
    p_days_to_keep INTEGER DEFAULT 90,
    OUT logs_deleted INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    -- 删除旧审计日志
    DELETE FROM audit_log 
    WHERE changed_at < CURRENT_DATE - INTERVAL '1 day' * p_days_to_keep;
    
    GET DIAGNOSTICS logs_deleted = ROW_COUNT;
    
    RAISE NOTICE 'Cleaned up % old audit logs (older than % days)', 
        logs_deleted, p_days_to_keep;
        
END;
$$;

-- 3.2 数据库维护存储过程
CREATE OR REPLACE PROCEDURE database_maintenance()
LANGUAGE plpgsql AS $$
DECLARE
    v_stats_info TEXT;
BEGIN
    RAISE NOTICE 'Starting database maintenance...';
    
    -- 更新表统计信息
    ANALYZE;
    
    -- 清理数据库
    VACUUM ANALYZE;
    
    -- 获取数据库大小信息
    SELECT pg_size_pretty(pg_database_size(current_database())) INTO v_stats_info;
    
    RAISE NOTICE 'Database maintenance completed. Database size: %', v_stats_info;
    
END;
$$;

-- 4. 通知和监控存储过程

-- 4.1 生成员工报告存储过程
CREATE OR REPLACE PROCEDURE generate_department_report(
    p_department_id INTEGER,
    OUT total_employees INTEGER,
    OUT avg_salary DECIMAL,
    OUT total_budget_used DECIMAL,
    OUT high_performers INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    -- 获取部门统计信息
    SELECT 
        COUNT(*),
        ROUND(AVG(salary), 2),
        SUM(salary)
    INTO total_employees, avg_salary, total_budget_used
    FROM employees
    WHERE department_id = p_department_id AND status = 'active';
    
    -- 计算高绩效员工数量（假设薪资>15000为高绩效）
    SELECT COUNT(*)
    INTO high_performers
    FROM employees
    WHERE department_id = p_department_id 
      AND status = 'active' 
      AND salary >= 15000;
    
    RAISE NOTICE 'Department report generated for department %: % employees, avg salary: %', 
        p_department_id, total_employees, avg_salary;
        
END;
$$;

-- 测试部门报告
CALL generate_department_report(1, NULL, NULL, NULL, NULL);

-- 4.2 监控存储过程
CREATE OR REPLACE PROCEDURE check_database_health()
LANGUAGE plpgsql AS $$
DECLARE
    v_active_connections INTEGER;
    v_database_size TEXT;
    v_table_counts INTEGER;
BEGIN
    -- 检查活跃连接数
    SELECT COUNT(*) INTO v_active_connections
    FROM pg_stat_activity 
    WHERE state = 'active';
    
    -- 获取数据库大小
    SELECT pg_size_pretty(pg_database_size(current_database())) INTO v_database_size;
    
    -- 获取表数量
    SELECT COUNT(*) INTO v_table_counts
    FROM information_schema.tables 
    WHERE table_schema = 'public';
    
    RAISE NOTICE 'Database Health Check:';
    RAISE NOTICE '- Active connections: %', v_active_connections;
    RAISE NOTICE '- Database size: %', v_database_size;
    RAISE NOTICE '- Total tables: %', v_table_counts;
    RAISE NOTICE '- Check completed at: %', CURRENT_TIMESTAMP;
    
END;
$$;

-- 5. 事务控制存储过程

-- 5.1 复杂事务存储过程
CREATE OR REPLACE PROCEDURE complete_employee_transfer(
    p_employee_id INTEGER,
    p_from_department INTEGER,
    p_to_department INTEGER,
    p_new_manager INTEGER,
    p_salary_adjustment DECIMAL DEFAULT 0
)
LANGUAGE plpgsql AS $$
DECLARE
    v_from_dept_name VARCHAR;
    v_to_dept_name VARCHAR;
    v_employee_name VARCHAR;
BEGIN
    -- 开始事务
    BEGIN
        -- 获取部门名称
        SELECT department_name INTO v_from_dept_name
        FROM departments WHERE department_id = p_from_department;
        
        SELECT department_name INTO v_to_dept_name
        FROM departments WHERE department_id = p_to_department;
        
        SELECT first_name || ' ' || last_name INTO v_employee_name
        FROM employees WHERE employee_id = p_employee_id;
        
        RAISE NOTICE 'Starting transfer process for % from % to %', 
            v_employee_name, v_from_dept_name, v_to_dept_name;
        
        -- 调用转部门存储过程
        CALL transfer_employee(p_employee_id, p_to_department, p_new_manager, p_salary_adjustment);
        
        -- 记录完整的转移审计日志
        INSERT INTO audit_log (
            table_name, operation, employee_id, new_values, changed_by
        ) VALUES (
            'employees', 'COMPLETE_TRANSFER', p_employee_id,
            jsonb_build_object(
                'from_department', v_from_dept_name,
                'to_department', v_to_dept_name,
                'adjustment', p_salary_adjustment,
                'transfer_date', CURRENT_DATE
            ),
            CURRENT_USER
        );
        
        RAISE NOTICE 'Transfer completed successfully for %', v_employee_name;
        
    EXCEPTION WHEN OTHERS THEN
        -- 如果出现任何错误，整个事务将回滚
        RAISE EXCEPTION 'Transfer failed: %', SQLERRM;
    END;
    
END;
$$;

-- 测试完整转移
CALL complete_employee_transfer(3, 1, 2, 1002, 1000.00);  -- Bob Johnson从IT转到Sales

-- 6. 存储过程管理

-- 6.1 列出所有存储过程
CREATE OR REPLACE PROCEDURE list_all_procedures()
LANGUAGE plpgsql AS $$
DECLARE
    proc_record RECORD;
BEGIN
    RAISE NOTICE 'Listing all procedures in the database:';
    RAISE NOTICE '==============================================';
    
    FOR proc_record IN
        SELECT 
            routine_name,
            routine_type,
            specific_name
        FROM information_schema.routines
        WHERE routine_schema = 'public'
          AND routine_type = 'PROCEDURE'
        ORDER BY routine_name
    LOOP
        RAISE NOTICE 'Procedure: %', proc_record.routine_name;
    END LOOP;
    
END;
$$;

-- 6.2 存储过程性能统计
CREATE OR REPLACE PROCEDURE analyze_procedure_performance()
LANGUAGE plpgsql AS $$
DECLARE
    stmt TEXT;
BEGIN
    RAISE NOTICE 'Analyzing stored procedure performance...';
    
    -- 创建临时视图来统计存储过程调用
    stmt := '
    CREATE TEMP VIEW procedure_stats AS
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        rows
    FROM pg_stat_statements
    WHERE query LIKE ''%CALL %''
    ORDER BY total_time DESC';
    
    EXECUTE stmt;
    
    RAISE NOTICE 'Procedure performance analysis completed. Check pg_stat_statements for details.';
    
END;
$$;

-- 7. 测试所有存储过程
SELECT '=== 测试存储过程功能 ===' as test_section;

-- 测试基础功能
CALL initialize_database();
CALL list_all_procedures();
CALL check_database_health();

-- 测试业务逻辑
CALL generate_department_report(2, NULL, NULL, NULL, NULL);
CALL cleanup_old_audit_logs(30, NULL);

-- 测试员工操作
SELECT * FROM employees ORDER BY employee_id;

-- 8. 清理和删除存储过程（如果需要）
/*
DROP PROCEDURE IF EXISTS initialize_database() CASCADE;
DROP PROCEDURE IF EXISTS add_employee(VARCHAR, VARCHAR, VARCHAR, VARCHAR, DECIMAL, INTEGER, INTEGER) CASCADE;
DROP PROCEDURE IF EXISTS calculate_employee_stats(INTEGER, OUT DECIMAL, OUT DECIMAL, OUT VARCHAR) CASCADE;
DROP PROCEDURE IF EXISTS transfer_employee(INTEGER, INTEGER, INTEGER, DECIMAL) CASCADE;
DROP PROCEDURE IF EXISTS bulk_salary_adjustment(INTEGER, DECIMAL, DECIMAL, DECIMAL, OUT INTEGER, OUT DECIMAL) CASCADE;
-- ... 更多清理语句
*/

SELECT '=== 存储过程测试完成 ===' as test_section;