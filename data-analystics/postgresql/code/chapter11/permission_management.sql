-- ================================================
-- PostgreSQL第11章：权限管理
-- ================================================
-- 本文件演示PostgreSQL的权限管理功能

-- ================================================
-- 1. 基础权限管理测试环境
-- ================================================

-- 1.1 创建权限管理测试环境
DROP TABLE IF EXISTS test_permissions.sales_data CASCADE;
DROP TABLE IF EXISTS test_permissions.employee_records CASCADE;
DROP TABLE IF EXISTS test_permissions.financial_data CASCADE;
DROP TABLE IF EXISTS test_permissions.audit_log CASCADE;
DROP SCHEMA IF EXISTS test_permissions CASCADE;

-- 创建测试模式
CREATE SCHEMA test_permissions;

-- 创建测试表结构
CREATE TABLE test_permissions.sales_data (
    id SERIAL PRIMARY KEY,
    sale_id VARCHAR(20) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    customer_id VARCHAR(20),
    sale_amount DECIMAL(15,2),
    sale_date DATE DEFAULT CURRENT_DATE,
    sales_rep_id VARCHAR(20),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_permissions.employee_records (
    emp_id SERIAL PRIMARY KEY,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(100),
    position VARCHAR(100),
    salary DECIMAL(12,2),
    hire_date DATE DEFAULT CURRENT_DATE,
    termination_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_permissions.financial_data (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(20) UNIQUE NOT NULL,
    account_number VARCHAR(50),
    transaction_type VARCHAR(50),
    amount DECIMAL(15,2),
    description TEXT,
    transaction_date DATE DEFAULT CURRENT_DATE,
    processed_by VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_permissions.audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    action VARCHAR(100),
    table_name VARCHAR(100),
    record_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    application VARCHAR(100)
);

-- 插入测试数据
INSERT INTO test_permissions.sales_data (sale_id, product_name, customer_id, sale_amount, sales_rep_id, region) VALUES
    ('S001', 'Product A', 'C001', 15000.00, 'SR001', 'North'),
    ('S002', 'Product B', 'C002', 25000.00, 'SR002', 'South'),
    ('S003', 'Product C', 'C003', 18000.00, 'SR003', 'East'),
    ('S004', 'Product A', 'C004', 12000.00, 'SR004', 'West'),
    ('S005', 'Product D', 'C005', 30000.00, 'SR005', 'North');

INSERT INTO test_permissions.employee_records (employee_number, full_name, email, department, position, salary) VALUES
    ('EMP001', 'John Doe', 'john.doe@company.com', 'Sales', 'Sales Manager', 75000.00),
    ('EMP002', 'Jane Smith', 'jane.smith@company.com', 'Engineering', 'Senior Developer', 85000.00),
    ('EMP003', 'Bob Johnson', 'bob.johnson@company.com', 'HR', 'HR Manager', 70000.00),
    ('EMP004', 'Alice Brown', 'alice.brown@company.com', 'Finance', 'Accountant', 60000.00);

INSERT INTO test_permissions.financial_data (transaction_id, account_number, transaction_type, amount, description, processed_by) VALUES
    ('T001', 'ACC001', 'Payment', 5000.00, 'Customer Payment', 'FIN001'),
    ('T002', 'ACC002', 'Expense', 1200.00, 'Office Supplies', 'FIN002'),
    ('T003', 'ACC003', 'Revenue', 25000.00, 'Sales Commission', 'FIN003');

INSERT INTO test_permissions.audit_log (user_id, action, table_name, record_id, new_values) VALUES
    ('admin_user', 'INSERT', 'sales_data', 'S001', '{"sale_id": "S001", "amount": 15000}'),
    ('admin_user', 'INSERT', 'employee_records', 'EMP001', '{"employee_number": "EMP001", "name": "John Doe"}'),
    ('app_service', 'UPDATE', 'financial_data', 'T001', '{"status": "processed"}');

-- 1.2 创建权限测试用户
-- 只读用户
CREATE ROLE perm_readonly NOLOGIN;
GRANT CONNECT ON DATABASE postgres TO perm_readonly;
GRANT USAGE ON SCHEMA test_permissions TO perm_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA test_permissions TO perm_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA test_permissions TO perm_readonly;

-- 基础读写用户
CREATE ROLE perm_basic_write NOLOGIN;
GRANT perm_readonly TO perm_basic_write;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA test_permissions TO perm_basic_write;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA test_permissions TO perm_basic_write;

-- 高级用户（管理员）
CREATE ROLE perm_admin NOLOGIN;
GRANT perm_basic_write TO perm_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_permissions TO perm_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test_permissions TO perm_admin;
GRANT CREATE ON SCHEMA test_permissions TO perm_admin;

-- ================================================
-- 2. 细粒度权限控制
-- ================================================

-- 2.1 创建列级权限
-- 创建只读员工邮箱的用户
CREATE ROLE perm_read_emp_email NOLOGIN;

-- 先撤销默认权限
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_permissions FROM perm_read_emp_email;

-- 重新授予特定列的权限
GRANT CONNECT ON DATABASE postgres TO perm_read_emp_email;
GRANT USAGE ON SCHEMA test_permissions TO perm_read_emp_email;

-- 授予员工表的基本字段读取权限
GRANT SELECT (emp_id, employee_number, full_name, department, position, hire_date, is_active) 
ON test_permissions.employee_records TO perm_read_emp_email;

-- 特殊权限：只能查看自己的邮箱
CREATE POLICY employee_email_policy ON test_permissions.employee_records
FOR SELECT USING (
    current_user = 'perm_read_emp_email' AND (
        email IS NULL OR 
        -- 这里需要根据实际用户映射逻辑调整
        full_name = 'Demo Employee'
    )
);

-- 2.2 创建动态权限检查函数
CREATE OR REPLACE FUNCTION check_table_access(
    p_table_name TEXT,
    p_operation TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    has_permission BOOLEAN;
BEGIN
    -- 检查用户是否有权限访问表
    SELECT EXISTS(
        SELECT 1 FROM information_schema.table_privileges
        WHERE grantee = current_user
        AND table_schema = 'test_permissions'
        AND table_name = p_table_name
        AND privilege_type = p_operation
    ) INTO has_permission;
    
    IF NOT has_permission THEN
        RAISE NOTICE 'Access denied for operation % on table %', p_operation, p_table_name;
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2.3 创建权限验证函数
CREATE OR REPLACE FUNCTION validate_user_permissions(
    p_user_name TEXT,
    p_table_name TEXT DEFAULT NULL
)
RETURNS TABLE(
    object_type TEXT,
    object_name TEXT,
    privilege_type TEXT,
    is_grantable BOOLEAN,
    can_execute BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH user_permissions AS (
        SELECT 
            tg.privilege_type,
            tg.table_name,
            tg.is_grantable,
            'table' as obj_type
        FROM information_schema.table_privileges tg
        WHERE tg.grantee = p_user_name
        AND (p_table_name IS NULL OR tg.table_name = p_table_name)
        AND tg.table_schema = 'test_permissions'
        
        UNION ALL
        
        SELECT 
            COALESCE(sg.privilege_type, 'USAGE') as privilege_type,
            sg.sequence_name as table_name,
            sg.is_grantable,
            'sequence' as obj_type
        FROM information_schema.sequence_privileges sg
        WHERE sg.grantee = p_user_name
        AND (p_table_name IS NULL OR sg.sequence_name = p_table_name)
        AND sg.sequence_schema = 'test_permissions'
    )
    SELECT 
        up.obj_type::TEXT as object_type,
        up.table_name::TEXT as object_name,
        up.privilege_type::TEXT as privilege_type,
        up.is_grantable::BOOLEAN as is_grantable,
        (
            SELECT EXISTS(
                SELECT 1 FROM information_schema.table_privileges
                WHERE grantee = current_user
                AND table_schema = 'test_permissions'
                AND table_name = up.table_name
                AND privilege_type = up.privilege_type
            )
        ) as can_execute
    FROM user_permissions up
    ORDER BY up.obj_type, up.table_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 3. 行级安全策略(RLS)
-- ================================================

-- 3.1 启用行级安全
ALTER TABLE test_permissions.sales_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_permissions.employee_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_permissions.financial_data ENABLE ROW LEVEL SECURITY;

-- 3.2 创建基于用户的行级安全策略
-- 销售数据：用户只能查看自己销售区域的数据
CREATE POLICY sales_data_region_policy ON test_permissions.sales_data
FOR ALL TO perm_basic_write
USING (
    CASE 
        WHEN current_user = 'user_north' THEN region = 'North'
        WHEN current_user = 'user_south' THEN region = 'South'
        WHEN current_user = 'user_east' THEN region = 'East'
        WHEN current_user = 'user_west' THEN region = 'West'
        -- 管理员可以查看所有数据
        WHEN current_user IN ('admin_user', 'perm_admin') THEN TRUE
        -- 其他用户无法访问
        ELSE FALSE
    END
);

-- 员工记录：基于部门的访问控制
CREATE POLICY employee_dept_policy ON test_permissions.employee_records
FOR ALL TO perm_basic_write
USING (
    CASE 
        -- HR部门用户可以查看所有员工信息
        WHEN current_user IN ('admin_user', 'perm_admin', 'hr_user') THEN TRUE
        -- 其他部门用户只能查看同部门员工
        WHEN department IN (
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_user::regnamespace::TEXT
        ) THEN TRUE
        -- 默认拒绝
        ELSE FALSE
    END
);

-- 财务数据：基于角色的访问控制
CREATE POLICY financial_access_policy ON test_permissions.financial_data
FOR ALL TO perm_basic_write
USING (
    CASE 
        -- 财务管理员可以查看所有财务数据
        WHEN current_user IN ('admin_user', 'perm_admin', 'finance_admin') THEN TRUE
        -- 财务专员只能查看自己的处理数据
        WHEN processed_by = current_user THEN TRUE
        -- 默认拒绝
        ELSE FALSE
    END
);

-- 3.3 创建动态权限检查函数
CREATE OR REPLACE FUNCTION check_row_access(
    p_table_name TEXT,
    p_action TEXT,
    p_record_data JSONB DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    has_access BOOLEAN;
BEGIN
    -- 根据不同的表和操作检查权限
    IF p_table_name = 'sales_data' THEN
        CASE p_action
            WHEN 'SELECT' THEN
                SELECT EXISTS(
                    SELECT 1 FROM test_permissions.sales_data
                    WHERE id = COALESCE((p_record_data->>'id')::INTEGER, 0)
                ) INTO has_access;
            WHEN 'INSERT' THEN
                -- 检查是否有销售数据的INSERT权限
                has_access := check_table_access('sales_data', 'INSERT');
            WHEN 'UPDATE' THEN
                has_access := check_table_access('sales_data', 'UPDATE');
            WHEN 'DELETE' THEN
                has_access := check_table_access('sales_data', 'DELETE');
        END CASE;
    ELSIF p_table_name = 'employee_records' THEN
        CASE p_action
            WHEN 'SELECT' THEN
                -- 检查员工记录的SELECT权限
                has_access := check_table_access('employee_records', 'SELECT');
            WHEN 'INSERT' THEN
                -- 只有HR或管理员可以插入员工记录
                has_access := current_user IN ('admin_user', 'perm_admin', 'hr_user');
            WHEN 'UPDATE' THEN
                -- 检查UPDATE权限
                has_access := check_table_access('employee_records', 'UPDATE');
            WHEN 'DELETE' THEN
                -- 只有管理员可以删除员工记录
                has_access := current_user IN ('admin_user', 'perm_admin');
        END CASE;
    ELSE
        has_access := FALSE;
    END IF;
    
    RETURN COALESCE(has_access, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 4. 权限继承和角色权限管理
-- ================================================

-- 4.1 创建分层权限结构
-- 基础权限层
CREATE ROLE role_basic NOLOGIN;
GRANT CONNECT ON DATABASE postgres TO role_basic;
GRANT USAGE ON SCHEMA test_permissions TO role_basic;

-- 业务权限层
CREATE ROLE role_sales NOLOGIN;
CREATE ROLE role_hr NOLOGIN;
CREATE ROLE role_finance NOLOGIN;

-- 继承基础权限
GRANT role_basic TO role_sales;
GRANT role_basic TO role_hr;
GRANT role_basic TO role_finance;

-- 部门特定权限
-- 销售部门权限
GRANT SELECT, INSERT, UPDATE ON test_permissions.sales_data TO role_sales;
GRANT SELECT ON test_permissions.employee_records TO role_sales;

-- 人力资源权限
GRANT SELECT, INSERT, UPDATE, DELETE ON test_permissions.employee_records TO role_hr;
GRANT SELECT ON test_permissions.sales_data TO role_hr;

-- 财务部门权限
GRANT SELECT, INSERT, UPDATE, DELETE ON test_permissions.financial_data TO role_finance;
GRANT SELECT ON test_permissions.sales_data TO role_finance;
GRANT SELECT, INSERT, UPDATE ON test_permissions.audit_log TO role_finance;

-- 4.2 创建权限转移函数
CREATE OR REPLACE FUNCTION transfer_privileges(
    p_from_role TEXT,
    p_to_role TEXT,
    p_object_type TEXT DEFAULT 'table'
)
RETURNS TEXT AS $$
DECLARE
    sql_statement TEXT;
    privilege_record RECORD;
    result_message TEXT;
BEGIN
    result_message := '';
    
    -- 转移表权限
    IF p_object_type = 'table' OR p_object_type = 'all' THEN
        FOR privilege_record IN
            SELECT table_name, privilege_type
            FROM information_schema.table_privileges
            WHERE grantee = p_from_role
            AND table_schema = 'test_permissions'
            AND table_type = 'BASE TABLE'
        LOOP
            sql_statement := format(
                'GRANT %s ON test_permissions.%s TO %s',
                privilege_record.privilege_type,
                privilege_record.table_name,
                p_to_role
            );
            
            BEGIN
                EXECUTE sql_statement;
                result_message := result_message || 'Granted ' || privilege_record.privilege_type || 
                                ' on ' || privilege_record.table_name || '; ';
            EXCEPTION WHEN OTHERS THEN
                result_message := result_message || 'Error granting ' || privilege_record.privilege_type || 
                                ' on ' || privilege_record.table_name || ': ' || SQLERRM || '; ';
            END;
        END LOOP;
    END IF;
    
    -- 转移序列权限
    IF p_object_type = 'sequence' OR p_object_type = 'all' THEN
        FOR privilege_record IN
            SELECT sequence_name, privilege_type
            FROM information_schema.sequence_privileges
            WHERE grantee = p_from_role
            AND sequence_schema = 'test_permissions'
        LOOP
            sql_statement := format(
                'GRANT %s ON SEQUENCE test_permissions.%s TO %s',
                privilege_record.privilege_type,
                privilege_record.sequence_name,
                p_to_role
            );
            
            BEGIN
                EXECUTE sql_statement;
                result_message := result_message || 'Granted ' || privilege_record.privilege_type || 
                                ' on sequence ' || privilege_record.sequence_name || '; ';
            EXCEPTION WHEN OTHERS THEN
                result_message := result_message || 'Error granting ' || privilege_record.privilege_type || 
                                ' on sequence ' || privilege_record.sequence_name || ': ' || SQLERRM || '; ';
            END;
        END LOOP;
    END IF;
    
    RETURN COALESCE(result_message, 'No privileges transferred');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4.3 创建权限同步函数
CREATE OR REPLACE FUNCTION sync_role_permissions(
    p_source_role TEXT,
    p_target_roles TEXT[]
)
RETURNS TABLE(
    target_role TEXT,
    permission_status TEXT,
    details TEXT
) AS $$
DECLARE
    target_role TEXT;
    permission_details TEXT;
BEGIN
    FOREACH target_role IN ARRAY p_target_roles
    LOOP
        -- 复制所有权限
        SELECT transfer_privileges(p_source_role, target_role, 'all')
        INTO permission_details;
        
        RETURN QUERY SELECT 
            target_role::TEXT,
            CASE 
                WHEN permission_details LIKE '%Error%' THEN 'FAILED'
                ELSE 'SUCCESS'
            END,
            permission_details;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 5. 权限审计和监控
-- ================================================

-- 5.1 创建权限变更记录表
CREATE TABLE IF NOT EXISTS permission_audit_log (
    audit_id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50), -- GRANT, REVOKE, CREATE_USER, etc.
    grantee VARCHAR(100),
    grantor VARCHAR(100),
    object_type VARCHAR(50), -- TABLE, SCHEMA, DATABASE, etc.
    object_name TEXT,
    privilege_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id BIGINT,
    ip_address INET,
    success BOOLEAN,
    error_message TEXT
);

-- 5.2 创建权限变更触发器函数
CREATE OR REPLACE FUNCTION log_permission_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- 记录GRANT权限操作
    IF TG_OP = 'INSERT' AND TG_TABLE_NAME = 'role_table_grants' THEN
        INSERT INTO permission_audit_log (
            operation_type, grantee, grantor, object_type, 
            object_name, privilege_type, session_id
        ) VALUES (
            'GRANT', NEW.grantee, current_user, 'TABLE',
            NEW.table_schema || '.' || NEW.table_name, NEW.privilege_type,
            pg_backend_pid()
        );
    END IF;
    
    -- 记录REVOKE权限操作
    IF TG_OP = 'DELETE' AND TG_TABLE_NAME = 'role_table_grants' THEN
        INSERT INTO permission_audit_log (
            operation_type, grantee, grantor, object_type,
            object_name, privilege_type, session_id
        ) VALUES (
            'REVOKE', OLD.grantee, current_user, 'TABLE',
            OLD.table_schema || '.' || OLD.table_name, OLD.privilege_type,
            pg_backend_pid()
        );
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 5.3 创建权限使用统计函数
CREATE OR REPLACE FUNCTION get_permission_usage_stats()
RETURNS TABLE(
    object_type TEXT,
    object_name TEXT,
    grantee TEXT,
    privilege_type TEXT,
    grantor TEXT,
    usage_count INTEGER,
    last_used TIMESTAMP,
    avg_access_time INTERVAL
) AS $$
BEGIN
    -- 这里使用pg_stat_statements来模拟权限使用统计
    -- 实际环境中应该结合真实的访问日志
    RETURN QUERY
    SELECT 
        'table'::TEXT as object_type,
        table_name::TEXT as object_name,
        grantee::TEXT,
        privilege_type::TEXT,
        grantor::TEXT,
        FLOOR(random() * 100)::INTEGER as usage_count,
        (CURRENT_TIMESTAMP - (random() * 30 || ' days')::INTERVAL)::TIMESTAMP as last_used,
        (random() * 1000 || ' milliseconds')::INTERVAL as avg_access_time
    FROM information_schema.table_privileges
    WHERE table_schema = 'test_permissions'
    ORDER BY usage_count DESC, last_used DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 6. 权限异常检测
-- ================================================

-- 6.1 创建异常权限检测函数
CREATE OR REPLACE FUNCTION detect_permission_anomalies()
RETURNS TABLE(
    anomaly_type TEXT,
    description TEXT,
    severity TEXT,
    recommended_action TEXT
) AS $$
BEGIN
    -- 检测过度权限
    RETURN QUERY
    SELECT 
        'EXCESSIVE_PERMISSIONS'::TEXT as anomaly_type,
        'User has more than 50 table privileges'::TEXT as description,
        'MEDIUM'::TEXT as severity,
        'Review and revoke unnecessary privileges'::TEXT as recommended_action
    FROM (
        SELECT grantee, COUNT(*) as privilege_count
        FROM information_schema.table_privileges
        WHERE table_schema = 'test_permissions'
        GROUP BY grantee
        HAVING COUNT(*) > 50
    ) excessive_permissions;
    
    -- 检测孤立的权限
    RETURN QUERY
    SELECT 
        'ORPHANED_PERMISSIONS'::TEXT as anomaly_type,
        'Privileges exist for non-existent users'::TEXT as description,
        'LOW'::TEXT as severity,
        'Clean up orphaned permissions'::TEXT as recommended_action
    FROM information_schema.table_privileges tp
    WHERE tp.table_schema = 'test_permissions'
    AND NOT EXISTS (
        SELECT 1 FROM pg_roles pr WHERE pr.rolname = tp.grantee
    );
    
    -- 检测敏感的权限组合
    RETURN QUERY
    SELECT 
        'PRIVILEGE_COMBINATION'::TEXT as anomaly_type,
        'User has both INSERT and DELETE privileges on same table'::TEXT as description,
        'HIGH'::TEXT as severity,
        'Consider separating INSERT and DELETE roles for better security'::TEXT as recommended_action
    FROM (
        SELECT grantee, table_name, 
               COUNT(CASE WHEN privilege_type = 'INSERT' THEN 1 END) as insert_priv,
               COUNT(CASE WHEN privilege_type = 'DELETE' THEN 1 END) as delete_priv
        FROM information_schema.table_privileges
        WHERE table_schema = 'test_permissions'
        GROUP BY grantee, table_name
        HAVING COUNT(CASE WHEN privilege_type = 'INSERT' THEN 1 END) > 0
        AND COUNT(CASE WHEN privilege_type = 'DELETE' THEN 1 END) > 0
    ) combo_permissions;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 7. 权限推荐和建议系统
-- ================================================

-- 7.1 创建基于角色的权限推荐函数
CREATE OR REPLACE FUNCTION recommend_permissions(
    p_user_name TEXT,
    p_access_pattern TEXT DEFAULT 'full'
)
RETURNS TABLE(
    object_type TEXT,
    object_name TEXT,
    recommended_privilege TEXT,
    reason TEXT,
    confidence TEXT
) AS $$
BEGIN
    -- 基于用户名称推荐权限
    IF p_access_pattern = 'sales' OR p_user_name LIKE '%sales%' THEN
        RETURN QUERY
        SELECT 
            'table'::TEXT as object_type,
            'sales_data'::TEXT as object_name,
            'SELECT, INSERT, UPDATE'::TEXT as recommended_privilege,
            'Based on sales role pattern'::TEXT as reason,
            'HIGH'::TEXT as confidence;
    END IF;
    
    IF p_access_pattern = 'hr' OR p_user_name LIKE '%hr%' OR p_user_name LIKE '%employee%' THEN
        RETURN QUERY
        SELECT 
            'table'::TEXT as object_type,
            'employee_records'::TEXT as object_name,
            'SELECT, INSERT, UPDATE, DELETE'::TEXT as recommended_privilege,
            'Based on HR role pattern'::TEXT as reason,
            'HIGH'::TEXT as confidence;
    END IF;
    
    IF p_access_pattern = 'finance' OR p_user_name LIKE '%finance%' OR p_user_name LIKE '%finance%' THEN
        RETURN QUERY
        SELECT 
            'table'::TEXT as object_type,
            'financial_data'::TEXT as object_name,
            'SELECT, INSERT, UPDATE, DELETE'::TEXT as recommended_privilege,
            'Based on finance role pattern'::TEXT as reason,
            'HIGH'::TEXT as confidence;
    END IF;
    
    -- 默认权限建议
    RETURN QUERY
    SELECT 
        'table'::TEXT as object_type,
        'sales_data'::TEXT as object_name,
        'SELECT'::TEXT as recommended_privilege,
        'Default read-only access'::TEXT as reason,
        'MEDIUM'::TEXT as confidence;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7.2 创建权限合规检查函数
CREATE OR REPLACE FUNCTION check_compliance_requirements()
RETURNS TABLE(
    requirement_name TEXT,
    compliance_status TEXT,
    details TEXT,
    remediation_suggestion TEXT
) AS $$
BEGIN
    -- 检查是否有未加密的密码
    RETURN QUERY
    SELECT 
        'PASSWORD_ENCRYPTION'::TEXT as requirement_name,
        CASE 
            WHEN current_setting('password_encryption', true) = 'scram-sha-256' 
            THEN 'COMPLIANT' 
            ELSE 'NON_COMPLIANT' 
        END as compliance_status,
        'Current encryption: ' || current_setting('password_encryption', true) as details,
        'Enable scram-sha-256 password encryption' as remediation_suggestion;
    
    -- 检查SSL配置
    RETURN QUERY
    SELECT 
        'SSL_CONNECTION'::TEXT as requirement_name,
        CASE 
            WHEN current_setting('ssl', true) = 'on' 
            THEN 'COMPLIANT' 
            ELSE 'NON_COMPLIANT' 
        END as compliance_status,
        'SSL status: ' || current_setting('ssl', true) as details,
        'Enable SSL for all database connections' as remediation_suggestion;
    
    -- 检查日志配置
    RETURN QUERY
    SELECT 
        'AUDIT_LOGGING'::TEXT as requirement_name,
        CASE 
            WHEN current_setting('log_statement', true) != 'none' 
            THEN 'COMPLIANT' 
            ELSE 'NON_COMPLIANT' 
        END as compliance_status,
        'Current log statement setting: ' || current_setting('log_statement', true) as details,
        'Enable statement logging for audit purposes' as remediation_suggestion;
    
    -- 检查RLS启用情况
    RETURN QUERY
    SELECT 
        'ROW_LEVEL_SECURITY'::TEXT as requirement_name,
        CASE 
            WHEN EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'test_permissions' 
                AND row_security = 'YES'
            )
            THEN 'COMPLIANT' 
            ELSE 'PARTIAL' 
        END as compliance_status,
        'RLS tables in test_permissions: ' || 
        COUNT(CASE WHEN row_security = 'YES' THEN 1 END)::TEXT as details,
        'Enable RLS for sensitive tables' as remediation_suggestion
    FROM information_schema.tables
    WHERE table_schema = 'test_permissions';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 8. 权限管理演示和测试
-- ================================================

-- 测试权限检查函数
SELECT * FROM validate_user_permissions('perm_readonly');
SELECT * FROM validate_user_permissions('perm_basic_write');
SELECT * FROM check_table_access('sales_data', 'SELECT');

-- 测试权限推荐
SELECT * FROM recommend_permissions('sales_user', 'sales');
SELECT * FROM recommend_permissions('hr_admin', 'hr');

-- 测试合规检查
SELECT * FROM check_compliance_requirements();

-- 测试权限使用统计
SELECT * FROM get_permission_usage_stats();

-- 测试权限转移
SELECT * FROM transfer_privileges('role_sales', 'role_finance', 'table');

-- 测试异常检测
SELECT * FROM detect_permission_anomalies();

/*
权限管理最佳实践：

1. 最小权限原则
   - 分配最小必要的权限
   - 定期审查权限分配
   - 及时撤销不需要的权限

2. 角色驱动管理
   - 使用角色分组管理权限
   - 创建层次化的权限结构
   - 避免直接给用户分配权限

3. 行级安全(RLS)
   - 在敏感表上启用RLS
   - 创建基于用户身份的行级策略
   - 定期测试RLS策略的有效性

4. 权限审计
   - 记录所有权限变更
   - 监控权限使用情况
   - 生成权限合规报告

5. 安全配置
   - 启用SSL/TLS连接
   - 使用强密码加密
   - 启用审计日志

6. 异常检测
   - 识别过度权限
   - 检测权限异常模式
   - 建立权限告警机制
*/
