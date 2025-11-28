-- PostgreSQL教程第8章：触发器

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

-- 审计和日志表
CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(20),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET
);

CREATE TABLE IF NOT EXISTS employee_history (
    history_id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    change_type VARCHAR(20),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    salary DECIMAL(10,2),
    department_id INTEGER,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS salary_change_requests (
    request_id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    current_salary DECIMAL(10,2),
    requested_salary DECIMAL(10,2),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    requested_by VARCHAR(100),
    approved_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP
);

-- 业务规则检查表
CREATE TABLE IF NOT EXISTS business_rules (
    rule_id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50),
    rule_expression TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清空表并插入测试数据
TRUNCATE salary_change_requests CASCADE;
TRUNCATE employee_history CASCADE;
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

INSERT INTO business_rules (rule_name, rule_type, rule_expression, is_active) VALUES
('Max Salary Increase', 'salary', 'new.salary <= old.salary * 1.2', TRUE),
('Min Working Age', 'hire', 'EXTRACT(YEAR FROM AGE(CURRENT_DATE, new.hire_date)) >= 18', TRUE),
('Email Format', 'email', 'new.email ~ ''^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$''', TRUE);

-- 1. 基本触发器函数

-- 1.1 简单审计日志触发器函数
CREATE OR REPLACE FUNCTION audit_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (
            table_name, operation, record_id, old_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            OLD.employee_id,
            row_to_json(OLD),
            CURRENT_USER,
            CURRENT_TIMESTAMP
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (
            table_name, operation, record_id, old_values, new_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            NEW.employee_id,
            row_to_json(OLD),
            row_to_json(NEW),
            CURRENT_USER,
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (
            table_name, operation, record_id, new_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            NEW.employee_id,
            row_to_json(NEW),
            CURRENT_USER,
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 1.2 创建基本触发器
DROP TRIGGER IF EXISTS audit_employees ON employees CASCADE;
CREATE TRIGGER audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_employee_changes();

-- 1.3 自动更新updated_at列触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为employees表添加updated_at触发器
DROP TRIGGER IF EXISTS update_employees_updated_at ON employees;
CREATE TRIGGER update_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为departments表添加updated_at触发器
DROP TRIGGER IF EXISTS update_departments_updated_at ON departments;
CREATE TRIGGER update_departments_updated_at
    BEFORE UPDATE ON departments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 2. 行级触发器

-- 2.1 员工入职验证触发器
CREATE OR REPLACE FUNCTION validate_employee_data()
RETURNS TRIGGER AS $$
DECLARE
    v_age INTEGER;
    v_manager_exists BOOLEAN;
    v_department_exists BOOLEAN;
BEGIN
    -- 检查必填字段
    IF NEW.first_name IS NULL OR TRIM(NEW.first_name) = '' THEN
        RAISE EXCEPTION 'First name cannot be empty';
    END IF;
    
    IF NEW.last_name IS NULL OR TRIM(NEW.last_name) = '' THEN
        RAISE EXCEPTION 'Last name cannot be empty';
    END IF;
    
    IF NEW.email IS NULL OR TRIM(NEW.email) = '' THEN
        RAISE EXCEPTION 'Email cannot be empty';
    END IF;
    
    -- 验证邮箱格式
    IF NEW.email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        RAISE EXCEPTION 'Invalid email format: %', NEW.email;
    END IF;
    
    -- 检查邮箱唯一性
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND OLD.email != NEW.email) THEN
        IF EXISTS (SELECT 1 FROM employees WHERE email = NEW.email AND employee_id != COALESCE(NEW.employee_id, -1)) THEN
            RAISE EXCEPTION 'Email % already exists', NEW.email;
        END IF;
    END IF;
    
    -- 检查年龄（如果提供了出生日期，可以扩展这个逻辑）
    -- 这里简化处理，只检查薪资范围
    IF NEW.salary IS NOT NULL AND NEW.salary < 0 THEN
        RAISE EXCEPTION 'Salary cannot be negative';
    END IF;
    
    -- 检查经理是否存在（如果指定了经理）
    IF NEW.manager_id IS NOT NULL THEN
        SELECT EXISTS(
            SELECT 1 FROM employees 
            WHERE employee_id = NEW.manager_id AND status = 'active'
        ) INTO v_manager_exists;
        
        IF NOT v_manager_exists THEN
            RAISE EXCEPTION 'Manager with ID % does not exist or is not active', NEW.manager_id;
        END IF;
        
        -- 防止自管理
        IF NEW.manager_id = NEW.employee_id THEN
            RAISE EXCEPTION 'Employee cannot be their own manager';
        END IF;
    END IF;
    
    -- 检查部门是否存在
    SELECT EXISTS(
        SELECT 1 FROM departments WHERE department_id = NEW.department_id
    ) INTO v_department_exists;
    
    IF NOT v_department_exists THEN
        RAISE EXCEPTION 'Department with ID % does not exist', NEW.department_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建员工数据验证触发器
DROP TRIGGER IF EXISTS validate_employee_data_trigger ON employees;
CREATE TRIGGER validate_employee_data_trigger
    BEFORE INSERT OR UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION validate_employee_data();

-- 2.2 薪资变更历史记录触发器
CREATE OR REPLACE FUNCTION track_salary_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- 只有当薪资发生变化时才记录
    IF TG_OP = 'UPDATE' AND OLD.salary != NEW.salary THEN
        INSERT INTO employee_history (
            employee_id, change_type, first_name, last_name, email, 
            salary, department_id, changed_by, reason
        ) VALUES (
            NEW.employee_id,
            'SALARY_CHANGE',
            NEW.first_name,
            NEW.last_name,
            NEW.email,
            NEW.salary,
            NEW.department_id,
            CURRENT_USER,
            'Salary changed from ' || OLD.salary || ' to ' || NEW.salary
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建薪资变更跟踪触发器
DROP TRIGGER IF EXISTS track_salary_changes_trigger ON employees;
CREATE TRIGGER track_salary_changes_trigger
    AFTER UPDATE ON employees
    FOR EACH ROW
    WHEN (OLD.salary IS DISTINCT FROM NEW.salary)
    EXECUTE FUNCTION track_salary_changes();

-- 3. 业务规则触发器

-- 3.1 薪资增长率检查触发器
CREATE OR REPLACE FUNCTION check_salary_increase()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查薪资增长是否合理（不能超过20%）
    IF TG_OP = 'UPDATE' AND NEW.salary > OLD.salary * 1.2 THEN
        RAISE EXCEPTION 'Salary increase cannot exceed 20%%. Current: %, Proposed: %', 
            OLD.salary, NEW.salary;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_salary_increase_trigger
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION check_salary_increase();

-- 3.2 部门预算检查触发器
CREATE OR REPLACE FUNCTION check_department_budget()
RETURNS TRIGGER AS $$
DECLARE
    v_current_total DECIMAL;
    v_budget_limit DECIMAL;
BEGIN
    -- 当员工薪资或部门发生变化时检查预算
    IF (TG_OP = 'INSERT') OR 
       (TG_OP = 'UPDATE' AND (OLD.department_id != NEW.department_id OR OLD.salary != NEW.salary)) THEN
        
        -- 获取部门预算限制
        SELECT budget INTO v_budget_limit
        FROM departments
        WHERE department_id = NEW.department_id;
        
        -- 计算该部门当前总薪资
        SELECT COALESCE(SUM(salary), 0) INTO v_current_total
        FROM employees
        WHERE department_id = NEW.department_id AND status = 'active';
        
        -- 如果是新员工，加上其薪资
        IF TG_OP = 'INSERT' THEN
            v_current_total := v_current_total + NEW.salary;
        -- 如果是转部门员工，从旧部门减去，从新部门加上
        ELSIF TG_OP = 'UPDATE' AND OLD.department_id != NEW.department_id THEN
            v_current_total := v_current_total + NEW.salary;
        END IF;
        
        -- 检查是否超出预算
        IF v_current_total > v_budget_limit THEN
            RAISE EXCEPTION 'Department budget exceeded. Current total: %, Budget limit: %', 
                v_current_total, v_budget_limit;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_department_budget_trigger
    BEFORE INSERT OR UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION check_department_budget();

-- 4. 状态变更触发器

-- 4.1 员工状态变更触发器
CREATE OR REPLACE FUNCTION handle_employee_status_change()
RETURNS TRIGGER AS $$
BEGIN
    -- 记录状态变更历史
    IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
        INSERT INTO employee_history (
            employee_id, change_type, first_name, last_name, email,
            department_id, changed_by, reason
        ) VALUES (
            NEW.employee_id,
            'STATUS_CHANGE',
            NEW.first_name,
            NEW.last_name,
            NEW.email,
            NEW.department_id,
            CURRENT_USER,
            'Status changed from ' || OLD.status || ' to ' || NEW.status
        );
        
        -- 如果员工被停用，清除经理关系
        IF NEW.status = 'inactive' THEN
            NEW.manager_id := NULL;
            RAISE NOTICE 'Manager relationship cleared for inactive employee %', NEW.employee_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER handle_employee_status_change_trigger
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION handle_employee_status_change();

-- 5. 高级触发器

-- 5.1 异步通知触发器（模拟）
CREATE OR REPLACE FUNCTION notify_salary_change()
RETURNS TRIGGER AS $$
BEGIN
    -- 这里可以集成消息队列系统
    -- 目前使用RAISE NOTICE模拟通知
    IF TG_OP = 'UPDATE' AND OLD.salary != NEW.salary THEN
        RAISE NOTICE 'NOTIFICATION: Salary change for employee % (% %) from % to %', 
            NEW.employee_id, NEW.first_name, NEW.last_name, OLD.salary, NEW.salary;
            
        -- 可以发送到日志表
        INSERT INTO audit_log (
            table_name, operation, record_id, new_values, changed_by, changed_at
        ) VALUES (
            'notifications',
            'SALARY_CHANGE_NOTICE',
            NEW.employee_id,
            jsonb_build_object(
                'message', 'Salary changed',
                'old_salary', OLD.salary,
                'new_salary', NEW.salary
            ),
            'system',
            CURRENT_TIMESTAMP
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notify_salary_change_trigger
    AFTER UPDATE ON employees
    FOR EACH ROW
    WHEN (OLD.salary IS DISTINCT FROM NEW.salary)
    EXECUTE FUNCTION notify_salary_change();

-- 5.2 批量操作触发器（语句级触发器）
CREATE OR REPLACE FUNCTION log_bulk_operations()
RETURNS TRIGGER AS $$
DECLARE
    operation_summary TEXT;
BEGIN
    -- 统计操作数量
    CASE TG_OP
        WHEN 'INSERT' THEN
            SELECT COUNT(*) INTO operation_summary
            FROM new_table;
        WHEN 'UPDATE' THEN
            SELECT COUNT(*) INTO operation_summary
            FROM new_table;
        WHEN 'DELETE' THEN
            SELECT COUNT(*) INTO operation_summary
            FROM old_table;
    END CASE;
    
    -- 记录批量操作审计日志
    INSERT INTO audit_log (
        table_name, operation, record_id, new_values, changed_by, changed_at
    ) VALUES (
        TG_TABLE_NAME,
        'BULK_' || TG_OP,
        NULL,
        jsonb_build_object(
            'operation_type', TG_OP,
            'affected_rows', operation_summary,
            'statement_only', TRUE
        ),
        CURRENT_USER,
        CURRENT_TIMESTAMP
    );
    
    RAISE NOTICE 'Bulk % operation logged: % rows affected', TG_OP, operation_summary;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建语句级批量操作审计触发器
DROP TRIGGER IF EXISTS audit_bulk_operations ON employees;
CREATE TRIGGER audit_bulk_operations
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION log_bulk_operations();

-- 6. 条件触发器

-- 6.1 只在特定条件触发的触发器
CREATE OR REPLACE FUNCTION conditional_salary_check()
RETURNS TRIGGER AS $$
BEGIN
    -- 只在薪资显著增长时（>10%）触发额外检查
    IF TG_OP = 'UPDATE' AND NEW.salary > OLD.salary * 1.1 THEN
        -- 需要上级批准标记
        INSERT INTO salary_change_requests (
            employee_id, current_salary, requested_salary, reason, requested_by
        ) VALUES (
            NEW.employee_id,
            OLD.salary,
            NEW.salary,
            'Significant salary increase detected',
            CURRENT_USER
        );
        
        RAISE NOTICE 'Salary increase approval required for employee % (from % to %)', 
            NEW.employee_id, OLD.salary, NEW.salary;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conditional_salary_check_trigger
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION conditional_salary_check();

-- 7. INSTEAD OF 触发器（视图触发器）

-- 创建员工统计视图
CREATE OR REPLACE VIEW employee_department_summary AS
SELECT 
    d.department_id,
    d.department_name,
    COUNT(e.employee_id) as employee_count,
    AVG(e.salary) as avg_salary,
    SUM(e.salary) as total_salary,
    MAX(e.salary) as max_salary,
    MIN(e.salary) as min_salary
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id AND e.status = 'active'
GROUP BY d.department_id, d.department_name;

-- 创建更新视图的INSTEAD OF触发器函数
CREATE OR REPLACE FUNCTION update_department_budget()
RETURNS TRIGGER AS $$
BEGIN
    -- 允许更新部门预算
    UPDATE departments
    SET budget = NEW.total_salary * 1.2  -- 设置为总薪资的120%
    WHERE department_id = NEW.department_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建INSTEAD OF触发器
DROP TRIGGER IF EXISTS instead_of_update_department ON employee_department_summary;
CREATE TRIGGER instead_of_update_department
    INSTEAD OF UPDATE ON employee_department_summary
    FOR EACH ROW
    EXECUTE FUNCTION update_department_budget();

-- 8. 触发器管理

-- 8.1 列出所有触发器
CREATE OR REPLACE FUNCTION list_triggers()
RETURNS TABLE (
    trigger_name VARCHAR,
    table_name VARCHAR,
    event_manipulation VARCHAR,
    action_timing VARCHAR,
    action_statement TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.trigger_name,
        t.event_object_table,
        t.event_manipulation,
        t.action_timing,
        t.action_statement
    FROM information_schema.triggers t
    WHERE t.trigger_schema = 'public'
    ORDER BY t.event_object_table, t.trigger_name;
END;
$$ LANGUAGE plpgsql;

-- 8.2 检查触发器状态
CREATE OR REPLACE FUNCTION check_trigger_status()
RETURNS TABLE (
    trigger_name VARCHAR,
    table_name VARCHAR,
    is_enabled BOOLEAN,
    last_fired TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.trigger_name,
        t.event_object_table,
        CASE WHEN t.trigger_name IN (
            SELECT tgname FROM pg_trigger WHERE NOT tgisinternal
        ) THEN TRUE ELSE FALSE END as is_enabled,
        NULL::TIMESTAMP as last_fired
    FROM information_schema.triggers t
    WHERE t.trigger_schema = 'public';
END;
$$ LANGUAGE plpgsql;

-- 9. 测试触发器

-- 9.1 测试基本触发器
SELECT '=== 测试基本触发器 ===' as test_section;

-- 插入新员工（会触发多个触发器）
INSERT INTO employees (first_name, last_name, email, phone, job_id, salary, department_id) 
VALUES ('Test', 'User', 'test.user@company.com', '13900139000', 'TW', 7500.00, 1);

-- 更新员工薪资（会触发多个触发器）
UPDATE employees 
SET salary = 13000.00 
WHERE email = 'john.smith@company.com';

-- 删除员工（触发审计日志）
-- DELETE FROM employees WHERE email = 'test.user@company.com';

SELECT * FROM audit_log ORDER BY changed_at DESC LIMIT 5;
SELECT * FROM employee_history ORDER BY changed_at DESC LIMIT 5;

-- 9.2 测试业务规则触发器
SELECT '=== 测试业务规则触发器 ===' as test_section;

-- 测试薪资增长限制（应该失败）
DO $$
BEGIN
    BEGIN
        UPDATE employees SET salary = 20000.00 WHERE email = 'john.smith@company.com';
        RAISE NOTICE 'Update succeeded unexpectedly';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Salary increase limit triggered: %', SQLERRM;
    END;
END $$;

-- 测试预算检查
DO $$
DECLARE
    dept_budget DECIMAL;
BEGIN
    -- 查看部门1的预算
    SELECT budget INTO dept_budget FROM departments WHERE department_id = 1;
    RAISE NOTICE 'Department 1 budget: %', dept_budget;
END $$;

-- 9.3 测试条件触发器
SELECT '=== 测试条件触发器 ===' as test_section;

-- 更新薪资超过10%（应该创建审批请求）
UPDATE employees 
SET salary = 18000.00 
WHERE email = 'jane.doe@company.com';  -- 从8000调到18000（125%增长）

SELECT * FROM salary_change_requests;

-- 9.4 查看触发器信息
SELECT '=== 查看触发器信息 ===' as test_section;
SELECT * FROM list_triggers();
SELECT * FROM check_trigger_status();

-- 10. 清理测试数据
-- 注意：在生产环境中请谨慎执行删除操作
/*
-- 删除触发器
DROP TRIGGER IF EXISTS audit_employees ON employees CASCADE;
DROP TRIGGER IF EXISTS update_employees_updated_at ON employees CASCADE;
-- ... 更多清理语句

-- 删除函数
DROP FUNCTION IF EXISTS audit_employee_changes() CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
-- ... 更多清理语句
*/

SELECT '=== 触发器测试完成 ===' as test_section;