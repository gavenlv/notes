-- ================================================
-- PostgreSQL第11章：用户和角色管理
-- ================================================
-- 本文件演示PostgreSQL的用户和角色管理功能

-- ================================================
-- 1. 基础角色和用户管理
-- ================================================

-- 1.1 创建基础测试环境
DROP TABLE IF EXISTS test_security.users CASCADE;
DROP TABLE IF EXISTS test_security.departments CASCADE;
DROP TABLE IF EXISTS test_security.employees CASCADE;

-- 创建测试模式
CREATE SCHEMA IF NOT EXISTS test_security;

-- 创建测试表
CREATE TABLE test_security.departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    budget NUMERIC(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_security.employees (
    emp_id SERIAL PRIMARY KEY,
    emp_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    dept_id INTEGER REFERENCES test_security.departments(dept_id),
    manager_id INTEGER REFERENCES test_security.employees(emp_id),
    salary NUMERIC(10,2),
    hire_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试数据
INSERT INTO test_security.departments (dept_name, location, budget) VALUES
    ('Engineering', 'New York', 500000.00),
    ('Marketing', 'San Francisco', 300000.00),
    ('Sales', 'Chicago', 400000.00),
    ('HR', 'Boston', 150000.00);

INSERT INTO test_security.employees (emp_name, email, dept_id, salary, hire_date) VALUES
    ('John Smith', 'john.smith@company.com', 1, 75000.00, '2020-01-15'),
    ('Jane Doe', 'jane.doe@company.com', 1, 85000.00, '2019-03-20'),
    ('Bob Johnson', 'bob.johnson@company.com', 2, 70000.00, '2021-06-10'),
    ('Alice Brown', 'alice.brown@company.com', 3, 90000.00, '2018-11-05'),
    ('Charlie Wilson', 'charlie.wilson@company.com', 4, 65000.00, '2022-02-28');

-- 1.2 创建角色层级结构
-- 基础只读角色
CREATE ROLE app_readonly NOLOGIN;

-- 读写角色（继承只读角色）
CREATE ROLE app_readwrite NOLOGIN;
GRANT app_readonly TO app_readwrite;

-- 管理员角色
CREATE ROLE app_admin NOLOGIN;
GRANT app_readwrite TO app_admin;

-- 超级管理员角色
CREATE ROLE super_admin NOLOGIN;
GRANT app_admin TO super_admin;

-- 1.3 创建具体用户
-- 只读用户
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'readonly_user') THEN
        CREATE ROLE readonly_user LOGIN PASSWORD 'ReadOnly2023!' 
            VALID UNTIL '2024-12-31' IN ROLE app_readonly;
    END IF;
END $$;

-- 读写用户
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'readwrite_user') THEN
        CREATE ROLE readwrite_user LOGIN PASSWORD 'ReadWrite2023!'
            VALID UNTIL '2024-12-31' IN ROLE app_readwrite;
    END IF;
END $$;

-- 管理员用户
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'admin_user') THEN
        CREATE ROLE admin_user LOGIN PASSWORD 'Admin2023!'
            VALID UNTIL '2024-12-31' CREATEDB IN ROLE app_admin;
    END IF;
END $$;

-- 应用服务用户
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_service') THEN
        CREATE ROLE app_service LOGIN PASSWORD 'AppService2023!';
    END IF;
END $$;

-- 1.4 权限分配
-- 只读权限
GRANT CONNECT ON DATABASE postgres TO app_readonly;
GRANT USAGE ON SCHEMA test_security TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA test_security TO app_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA test_security TO app_readonly;
GRANT SELECT ON test_security.departments TO app_readonly;
GRANT SELECT ON test_security.employees TO app_readonly;

-- 读写权限
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA test_security TO app_readwrite;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA test_security TO app_readwrite;

-- 管理员权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_security TO app_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test_security TO app_admin;
GRANT CREATE ON SCHEMA test_security TO app_admin;

-- ================================================
-- 2. 高级角色管理
-- ================================================

-- 2.1 创建部门级角色
CREATE ROLE dept_engineering NOLOGIN;
CREATE ROLE dept_marketing NOLOGIN;
CREATE ROLE dept_sales NOLOGIN;
CREATE ROLE dept_hr NOLOGIN;

-- 2.2 创建临时角色
CREATE ROLE temp_user TEMP NOLOGIN PASSWORD 'Temp2023!' VALID UNTIL '2023-12-31';

-- 2.3 创建配置文件角色
CREATE ROLE config_manager NOLOGIN;

-- 2.4 创建角色权限管理函数
CREATE OR REPLACE FUNCTION assign_user_to_role(
    p_user_name TEXT,
    p_role_name TEXT,
    p_assignor TEXT DEFAULT current_user
)
RETURNS TEXT AS $$
DECLARE
    user_exists BOOLEAN;
    role_exists BOOLEAN;
BEGIN
    -- 检查用户是否存在
    SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_user_name) INTO user_exists;
    -- 检查角色是否存在
    SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_role_name) INTO role_exists;
    
    IF NOT user_exists THEN
        RETURN 'Error: User ' || p_user_name || ' does not exist';
    END IF;
    
    IF NOT role_exists THEN
        RETURN 'Error: Role ' || p_role_name || ' does not exist';
    END IF;
    
    -- 检查权限
    IF NOT EXISTS(
        SELECT 1 FROM pg_roles 
        WHERE rolname = current_user 
        AND rolname IN ('super_admin', 'app_admin')
    ) THEN
        RETURN 'Error: Insufficient privileges to assign roles';
    END IF;
    
    -- 执行角色分配
    EXECUTE 'GRANT ' || p_role_name || ' TO ' || p_user_name;
    
    RETURN 'Success: Role ' || p_role_name || ' assigned to user ' || p_user_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2.5 创建角色撤销函数
CREATE OR REPLACE FUNCTION revoke_role_from_user(
    p_user_name TEXT,
    p_role_name TEXT
)
RETURNS TEXT AS $$
DECLARE
    user_exists BOOLEAN;
    role_exists BOOLEAN;
BEGIN
    -- 检查用户是否存在
    SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_user_name) INTO user_exists;
    -- 检查角色是否存在
    SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_role_name) INTO role_exists;
    
    IF NOT user_exists THEN
        RETURN 'Error: User ' || p_user_name || ' does not exist';
    END IF;
    
    IF NOT role_exists THEN
        RETURN 'Error: Role ' || p_role_name || ' does not exist';
    END IF;
    
    -- 检查权限
    IF NOT EXISTS(
        SELECT 1 FROM pg_roles 
        WHERE rolname = current_user 
        AND rolname IN ('super_admin', 'app_admin')
    ) THEN
        RETURN 'Error: Insufficient privileges to revoke roles';
    END IF;
    
    -- 执行角色撤销
    EXECUTE 'REVOKE ' || p_role_name || ' FROM ' || p_user_name;
    
    RETURN 'Success: Role ' || p_role_name || ' revoked from user ' || p_user_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 测试角色分配
SELECT assign_user_to_role('readonly_user', 'dept_engineering');
SELECT assign_user_to_role('readwrite_user', 'dept_marketing');

-- ================================================
-- 3. 密码策略和安全设置
-- ================================================

-- 3.1 创建密码复杂度检查函数
CREATE OR REPLACE FUNCTION validate_password_complexity(
    p_password TEXT,
    p_username TEXT DEFAULT ''
)
RETURNS BOOLEAN AS $$
DECLARE
    has_uppercase BOOLEAN := FALSE;
    has_lowercase BOOLEAN := FALSE;
    has_digit BOOLEAN := FALSE;
    has_special BOOLEAN := FALSE;
    pwd_length INTEGER;
    i INTEGER;
    char_ascii INTEGER;
BEGIN
    pwd_length := length(p_password);
    
    -- 检查密码长度
    IF pwd_length < 8 THEN
        RAISE EXCEPTION 'Password must be at least 8 characters long';
    END IF;
    
    -- 检查字符复杂度
    FOR i IN 1..pwd_length LOOP
        char_ascii := ascii(substring(p_password from i for 1));
        
        IF char_ascii >= 65 AND char_ascii <= 90 THEN
            has_uppercase := TRUE;
        ELSIF char_ascii >= 97 AND char_ascii <= 122 THEN
            has_lowercase := TRUE;
        ELSIF char_ascii >= 48 AND char_ascii <= 57 THEN
            has_digit := TRUE;
        ELSIF char_ascii IN (33, 35, 36, 37, 38, 40, 41, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 95, 96, 123, 124, 125, 126) THEN
            has_special := TRUE;
        END IF;
    END LOOP;
    
    -- 检查是否包含用户名（简单的密码策略）
    IF p_username != '' AND position(lower(p_username) in lower(p_password)) > 0 THEN
        RAISE EXCEPTION 'Password cannot contain the username';
    END IF;
    
    -- 验证所有条件
    IF NOT has_uppercase THEN
        RAISE EXCEPTION 'Password must contain at least one uppercase letter';
    END IF;
    
    IF NOT has_lowercase THEN
        RAISE EXCEPTION 'Password must contain at least one lowercase letter';
    END IF;
    
    IF NOT has_digit THEN
        RAISE EXCEPTION 'Password must contain at least one digit';
    END IF;
    
    IF NOT has_special THEN
        RAISE EXCEPTION 'Password must contain at least one special character';
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3.2 创建密码历史检查函数
CREATE TABLE IF NOT EXISTS password_history (
    user_name VARCHAR(100) PRIMARY KEY,
    password_hash TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION check_password_history(
    p_user_name TEXT,
    p_password TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    old_hash TEXT;
    pwd_hash TEXT;
BEGIN
    -- 获取旧密码哈希
    SELECT password_hash INTO old_hash
    FROM password_history
    WHERE user_name = p_user_name
    ORDER BY changed_at DESC
    LIMIT 1;
    
    -- 计算新密码哈希（这里简化处理，实际中应该使用加密库）
    pwd_hash := encode(digest(p_password || p_user_name, 'sha256'), 'hex');
    
    -- 检查密码是否重复
    IF old_hash IS NOT NULL AND old_hash = pwd_hash THEN
        RAISE EXCEPTION 'Password cannot be the same as previous passwords';
    END IF;
    
    -- 记录密码变更历史
    INSERT INTO password_history (user_name, password_hash)
    VALUES (p_user_name, pwd_hash)
    ON CONFLICT (user_name) 
    DO UPDATE SET 
        password_hash = excluded.password_hash,
        changed_at = excluded.changed_at;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 4. 用户权限查询和分析
-- ================================================

-- 4.1 创建用户权限查询函数
CREATE OR REPLACE FUNCTION get_user_permissions(
    p_user_name TEXT DEFAULT NULL
)
RETURNS TABLE(
    user_name VARCHAR(100),
    permission_type VARCHAR(50),
    object_name TEXT,
    object_type VARCHAR(50),
    privilege_type VARCHAR(50),
    is_grantable BOOLEAN
) AS $$
BEGIN
    IF p_user_name IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            p_user_name::VARCHAR(100),
            'Database'::VARCHAR(50) as permission_type,
            ''::TEXT as object_name,
            'Database'::VARCHAR(50) as object_type,
            privilege_type,
            is_grantable
        FROM information_schema.role_database_grants
        WHERE grantee = p_user_name
        AND table_name IS NULL
        
        UNION ALL
        
        SELECT 
            p_user_name::VARCHAR(100),
            'Schema'::VARCHAR(50) as permission_type,
            privilege_type::TEXT as object_name,
            'Schema'::VARCHAR(50) as object_type,
            privilege_type,
            is_grantable
        FROM information_schema.role_schema_grants
        WHERE grantee = p_user_name
        
        UNION ALL
        
        SELECT 
            p_user_name::VARCHAR(100),
            'Table'::VARCHAR(50) as permission_type,
            table_name::TEXT as object_name,
            'Table'::VARCHAR(50) as object_type,
            privilege_type,
            is_grantable
        FROM information_schema.role_table_grants
        WHERE grantee = p_user_name
        
        UNION ALL
        
        SELECT 
            p_user_name::VARCHAR(100),
            'Column'::VARCHAR(50) as permission_type,
            table_name || '.' || column_name::TEXT as object_name,
            'Column'::VARCHAR(50) as object_type,
            privilege_type,
            is_grantable
        FROM information_schema.role_column_grants
        WHERE grantee = p_user_name
        
        UNION ALL
        
        SELECT 
            p_user_name::VARCHAR(100),
            'Sequence'::VARCHAR(50) as permission_type,
            sequence_name::TEXT as object_name,
            'Sequence'::VARCHAR(50) as object_type,
            privilege_type,
            is_grantable
        FROM information_schema.role_sequence_grants
        WHERE grantee = p_user_name
        
        ORDER BY permission_type, object_name;
    ELSE
        RETURN QUERY
        SELECT 
            grantee::VARCHAR(100),
            'Database'::VARCHAR(50) as permission_type,
            ''::TEXT as object_name,
            'Database'::VARCHAR(50) as object_type,
            privilege_type,
            is_grantable
        FROM information_schema.role_database_grants
        WHERE table_name IS NULL;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4.2 创建角色层级查询函数
CREATE OR REPLACE FUNCTION get_role_hierarchy(
    p_role_name TEXT DEFAULT NULL
)
RETURNS TABLE(
    role_name VARCHAR(100),
    parent_role VARCHAR(100),
    level INTEGER,
    is_admin BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE role_tree AS (
        SELECT 
            r.rolname as role_name,
            NULL::VARCHAR(100) as parent_role,
            0 as level,
            r.rolsuper or r.rolcreaterole as is_admin
        FROM pg_roles r
        WHERE (p_role_name IS NULL OR r.rolname = p_role_name)
        AND r.rolname NOT LIKE 'pg_%'
        
        UNION ALL
        
        SELECT 
            m.rolname as role_name,
            r.rolname as parent_role,
            rt.level + 1 as level,
            m.rolsuper or m.rolcreaterole as is_admin
        FROM pg_roles m
        JOIN pg_auth_members am ON m.oid = am.member
        JOIN pg_roles r ON am.roleid = r.oid
        JOIN role_tree rt ON r.rolname = rt.role_name
        WHERE m.rolname NOT LIKE 'pg_%'
    )
    SELECT * FROM role_tree
    ORDER BY level, role_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 5. 用户活动监控
-- ================================================

-- 5.1 创建用户连接历史表
CREATE TABLE IF NOT EXISTS user_connection_history (
    record_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    session_id BIGINT,
    connection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disconnection_time TIMESTAMP,
    client_address INET,
    application_name VARCHAR(200),
    login_failed BOOLEAN DEFAULT FALSE,
    session_duration INTERVAL
);

-- 5.2 创建连接监控函数
CREATE OR REPLACE FUNCTION monitor_user_connections()
RETURNS TABLE(
    user_name VARCHAR(100),
    active_connections INTEGER,
    total_sessions_today INTEGER,
    average_session_duration INTERVAL,
    last_activity TIMESTAMP,
    failed_logins_today INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH daily_stats AS (
        SELECT 
            usename as user_name,
            COUNT(*) as session_count,
            AVG(CASE WHEN state = 'inactive' 
                THEN EXTRACT(EPOCH FROM (now() - query_start)) 
                ELSE NULL END) as avg_duration_seconds,
            MAX(query_start) as last_activity
        FROM pg_stat_activity
        WHERE usename NOT LIKE 'pg_%'
        GROUP BY usename
    )
    SELECT 
        pg_roles.rolname::VARCHAR(100),
        COALESCE(active_sessions.cnt, 0),
        COALESCE(stats.session_count, 0),
        CASE WHEN stats.avg_duration_seconds IS NOT NULL 
            THEN (stats.avg_duration_seconds || ' seconds')::INTERVAL 
            ELSE NULL END,
        stats.last_activity,
        COALESCE(failed.cnt, 0)
    FROM pg_roles
    LEFT JOIN (
        SELECT 
            usename,
            COUNT(*) as cnt
        FROM pg_stat_activity
        WHERE state = 'active'
        AND usename NOT LIKE 'pg_%'
        GROUP BY usename
    ) active_sessions ON pg_roles.rolname = active_sessions.usename
    LEFT JOIN daily_stats stats ON pg_roles.rolname = stats.user_name
    LEFT JOIN (
        SELECT 
            user_name,
            COUNT(*) as cnt
        FROM user_connection_history
        WHERE DATE(connection_time) = CURRENT_DATE
        AND login_failed = TRUE
        GROUP BY user_name
    ) failed ON pg_roles.rolname = failed.user_name
    WHERE pg_roles.rolname NOT LIKE 'pg_%'
    ORDER BY active_connections DESC, total_sessions_today DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5.3 创建用户权限变更审计函数
CREATE OR REPLACE FUNCTION audit_permission_changes(
    p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE(
    change_time TIMESTAMP,
    grantor VARCHAR(100),
    grantee VARCHAR(100),
    object_name TEXT,
    object_type VARCHAR(50),
    privilege_type VARCHAR(50),
    change_type VARCHAR(10)
) AS $$
BEGIN
    -- 这里使用pg_stat_statements来模拟审计日志
    -- 实际环境中应该使用专门的审计扩展如pgaudit
    RETURN QUERY
    SELECT 
        (CURRENT_TIMESTAMP - (random() * p_days_back || ' days')::INTERVAL)::TIMESTAMP as change_time,
        (ARRAY['postgres', 'app_admin', 'admin_user'])[floor(random() * 3) + 1]::VARCHAR(100) as grantor,
        (ARRAY['readonly_user', 'readwrite_user', 'app_service'])[floor(random() * 3) + 1]::VARCHAR(100) as grantee,
        ('test_security.' || (ARRAY['departments', 'employees'])[floor(random() * 2) + 1])::TEXT as object_name,
        'Table'::VARCHAR(50) as object_type,
        (ARRAY['SELECT', 'INSERT', 'UPDATE', 'DELETE'])[floor(random() * 4) + 1]::VARCHAR(50) as privilege_type,
        (ARRAY['GRANT', 'REVOKE'])[floor(random() * 2) + 1]::VARCHAR(10) as change_type
    FROM generate_series(1, floor(random() * 10) + 5)
    ORDER BY change_time DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 6. 安全配置函数
-- ================================================

-- 6.1 创建安全配置检查函数
CREATE OR REPLACE FUNCTION check_security_configuration()
RETURNS TABLE(
    setting_name VARCHAR(100),
    current_value TEXT,
    recommended_value TEXT,
    security_level VARCHAR(20),
    description TEXT,
    action_required BOOLEAN
) AS $$
DECLARE
    ssl_setting TEXT;
    log_connections TEXT;
    log_disconnections TEXT;
    password_encryption TEXT;
    shared_preload_libraries TEXT;
BEGIN
    -- 获取当前安全设置
    SHOW ssl TO ssl_setting;
    SHOW log_connections TO log_connections;
    SHOW log_disconnections TO log_disconnections;
    SHOW password_encryption TO password_encryption;
    SHOW shared_preload_libraries TO shared_preload_libraries;
    
    RETURN QUERY VALUES
        ('ssl',
         ssl_setting,
         'on',
         'HIGH',
         '启用SSL/TLS加密连接',
         ssl_setting != 'on'),
        ('log_connections',
         log_connections,
         'on',
         'MEDIUM',
         '记录连接日志',
         log_connections != 'on'),
        ('log_disconnections',
         log_disconnections,
         'on',
         'MEDIUM',
         '记录断开连接日志',
         log_disconnections != 'on'),
        ('password_encryption',
         password_encryption,
         'scram-sha-256',
         'HIGH',
         '密码加密算法',
         password_encryption != 'scram-sha-256'),
        ('shared_preload_libraries',
         shared_preload_libraries,
         'pg_stat_statements',
         'MEDIUM',
         '预加载扩展库',
         NOT shared_preload_libraries LIKE '%pg_stat_statements%');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 6.2 创建密码过期检查函数
CREATE OR REPLACE FUNCTION check_password_expiry()
RETURNS TABLE(
    user_name VARCHAR(100),
    password_expires TIMESTAMP,
    days_until_expiry INTEGER,
    status VARCHAR(20),
    action_required BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.rolname::VARCHAR(100),
        r.rolvaliduntil,
        CASE 
            WHEN r.rolvaliduntil IS NULL THEN NULL
            ELSE (r.rolvaliduntil - CURRENT_DATE)::INTEGER
        END as days_until_expiry,
        CASE 
            WHEN r.rolvaliduntil IS NULL THEN 'NEVER_EXPIRES'
            WHEN r.rolvaliduntil < CURRENT_DATE THEN 'EXPIRED'
            WHEN (r.rolvaliduntil - CURRENT_DATE) <= 30 THEN 'EXPIRING_SOON'
            ELSE 'ACTIVE'
        END as status,
        CASE 
            WHEN r.rolvaliduntil IS NULL THEN FALSE
            WHEN r.rolvaliduntil < CURRENT_DATE THEN TRUE
            WHEN (r.rolvaliduntil - CURRENT_DATE) <= 30 THEN TRUE
            ELSE FALSE
        END as action_required
    FROM pg_roles r
    WHERE r.rolname NOT LIKE 'pg_%'
    AND r.rolname != 'postgres'
    ORDER BY 
        CASE 
            WHEN r.rolvaliduntil IS NULL THEN 999999
            ELSE (r.rolvaliduntil - CURRENT_DATE)::INTEGER
        END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 7. 用户管理操作演示
-- ================================================

-- 测试函数调用
SELECT * FROM get_user_permissions('readonly_user');
SELECT * FROM get_role_hierarchy('app_admin');
SELECT * FROM monitor_user_connections();
SELECT * FROM check_security_configuration();
SELECT * FROM check_password_expiry();

-- ================================================
-- 8. 用户管理最佳实践函数
-- ================================================

-- 8.1 创建批量用户创建函数
CREATE OR REPLACE FUNCTION create_user_batch(
    users_info JSONB
)
RETURNS TABLE(
    user_name TEXT,
    status TEXT,
    message TEXT
) AS $$
DECLARE
    user_info RECORD;
    password_hash TEXT;
    role_list TEXT;
    expires_at TIMESTAMP;
BEGIN
    FOR user_info IN 
        SELECT * FROM jsonb_populate_recordset(NULL::record, users_info) 
        AS t(username TEXT, password TEXT, roles TEXT[], expires_at TIMESTAMP)
    LOOP
        BEGIN
            -- 创建用户
            EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L VALID UNTIL %L',
                user_info.username,
                user_info.password,
                user_info.expires_at
            );
            
            -- 分配角色
            FOREACH role_list IN ARRAY user_info.roles
            LOOP
                EXECUTE format('GRANT %I TO %I', role_list, user_info.username);
            END LOOP;
            
            -- 记录日志
            RETURN QUERY SELECT 
                user_info.username,
                'SUCCESS',
                'User created and roles assigned successfully';
                
        EXCEPTION WHEN OTHERS THEN
            RETURN QUERY SELECT 
                user_info.username,
                'ERROR',
                SQLERRM;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8.2 创建用户清理函数
CREATE OR REPLACE FUNCTION cleanup_inactive_users(
    days_inactive INTEGER DEFAULT 90
)
RETURNS TABLE(
    user_name TEXT,
    last_activity TIMESTAMP,
    action_taken TEXT
) AS $$
DECLARE
    inactive_user RECORD;
BEGIN
    FOR inactive_user IN
        SELECT 
            r.rolname,
            MAX(a.query_start) as last_activity
        FROM pg_roles r
        LEFT JOIN pg_stat_activity a ON a.usename = r.rolname
        WHERE r.rolname NOT LIKE 'pg_%'
        AND r.rolname != 'postgres'
        GROUP BY r.rolname
        HAVING MAX(a.query_start) < CURRENT_DATE - (days_inactive || ' days')::INTERVAL
        OR MAX(a.query_start) IS NULL
    LOOP
        BEGIN
            -- 撤销所有角色
            EXECUTE format('REVOKE ALL FROM %I', inactive_user.rolname);
            
            -- 禁用用户
            EXECUTE format('ALTER ROLE %I NOLOGIN', inactive_user.rolname);
            
            RETURN QUERY SELECT 
                inactive_user.rolname,
                inactive_user.last_activity,
                'User disabled';
                
        EXCEPTION WHEN OTHERS THEN
            RETURN QUERY SELECT 
                inactive_user.rolname,
                inactive_user.last_activity,
                'Error: ' || SQLERRM;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 9. 安全报告生成
-- ================================================

-- 9.1 生成综合安全报告
CREATE OR REPLACE FUNCTION generate_security_report()
RETURNS TABLE(
    section_name VARCHAR(100),
    metric_name VARCHAR(200),
    metric_value TEXT,
    status VARCHAR(20),
    recommendations TEXT
) AS $$
BEGIN
    -- 用户统计
    RETURN QUERY
    SELECT 
        'User Management'::VARCHAR(100),
        'Total Users'::VARCHAR(200),
        COUNT(*)::TEXT,
        CASE 
            WHEN COUNT(*) <= 20 THEN 'GOOD'
            WHEN COUNT(*) <= 50 THEN 'WARNING'
            ELSE 'ALERT'
        END,
        'Review user list and remove unused accounts'::TEXT
    FROM pg_roles 
    WHERE rolname NOT LIKE 'pg_%'
    AND rolname != 'postgres';
    
    -- 密码过期状态
    RETURN QUERY
    SELECT 
        'Password Security'::VARCHAR(100),
        'Users with Password Expiring Soon'::VARCHAR(200),
        COUNT(*)::TEXT,
        CASE 
            WHEN COUNT(*) = 0 THEN 'GOOD'
            WHEN COUNT(*) <= 3 THEN 'WARNING'
            ELSE 'CRITICAL'
        END,
        'Update passwords for users with expired credentials'::TEXT
    FROM pg_roles 
    WHERE rolvaliduntil BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
    AND rolvaliduntil IS NOT NULL;
    
    -- 连接活动
    RETURN QUERY
    SELECT 
        'Connection Monitoring'::VARCHAR(100),
        'Active Connections'::VARCHAR(200),
        COUNT(*)::TEXT,
        CASE 
            WHEN COUNT(*) < 50 THEN 'GOOD'
            WHEN COUNT(*) < 100 THEN 'WARNING'
            ELSE 'CRITICAL'
        END,
        'Monitor connection patterns and implement connection pooling'::TEXT
    FROM pg_stat_activity
    WHERE state = 'active';
    
    -- SSL配置
    RETURN QUERY
    SELECT 
        'SSL Configuration'::VARCHAR(100),
        'SSL Enabled'::VARCHAR(200),
        current_setting('ssl', true),
        CASE 
            WHEN current_setting('ssl', true) = 'on' THEN 'GOOD'
            ELSE 'CRITICAL'
        END,
        'Enable SSL/TLS encryption for all connections'::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 执行安全报告
SELECT * FROM generate_security_report();

/*
用户管理最佳实践：

1. 密码策略
   - 最小8位字符
   - 包含大小写字母、数字和特殊字符
   - 不包含用户名
   - 定期更换（90天）

2. 权限管理
   - 遵循最小权限原则
   - 使用角色分组管理
   - 定期审查权限分配
   - 记录权限变更历史

3. 用户生命周期
   - 用户创建时分配最小权限
   - 定期检查用户活动状态
   - 及时禁用/删除不再需要的账户
   - 记录所有权限变更

4. 监控和审计
   - 启用登录日志记录
   - 监控异常登录活动
   - 定期生成安全报告
   - 设置安全告警

5. 网络安全
   - 强制使用SSL连接
   - 限制连接来源IP
   - 使用防火墙规则
   - 定期更新安全配置
*/
