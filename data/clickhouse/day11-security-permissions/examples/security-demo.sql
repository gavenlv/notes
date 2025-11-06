-- ClickHouse Day 11: 安全权限实践示例
-- 演示用户管理、权限控制和数据安全技术

-- =====================================
-- 1. 用户管理示例
-- =====================================

-- 1.1 创建不同类型的用户
-- 创建管理员用户
CREATE USER admin_user 
IDENTIFIED WITH sha256_password BY 'Admin@123456'
HOST IP '10.0.0.0/8', IP '127.0.0.1'
SETTINGS PROFILE 'default';

-- 创建分析师用户
CREATE USER analyst_user 
IDENTIFIED WITH sha256_password BY 'Analyst@123'
HOST IP '192.168.1.0/24'
SETTINGS PROFILE 'readonly';

-- 创建API用户（用于应用程序连接）
CREATE USER api_user 
IDENTIFIED WITH sha256_password BY 'ApiUser@789'
HOST IP '10.0.0.100', IP '10.0.0.101'
SETTINGS PROFILE 'realtime';

-- 创建ETL用户（用于数据处理）
CREATE USER etl_user 
IDENTIFIED WITH sha256_password BY 'ETL@User456'
HOST IP '10.0.1.0/24'
SETTINGS PROFILE 'batch_processing';

-- 1.2 查看用户信息
SHOW USERS;
SHOW CREATE USER admin_user;

-- 1.3 修改用户
-- 修改密码
ALTER USER analyst_user IDENTIFIED WITH sha256_password BY 'NewPassword@123';

-- 修改网络访问
ALTER USER api_user HOST IP '10.0.0.0/24';

-- 1.4 用户认证方式演示
-- SHA256双重哈希
CREATE USER secure_user IDENTIFIED WITH double_sha1_password BY 'SecurePass@123';

-- 无密码用户（仅限本地连接）
CREATE USER local_user IDENTIFIED WITH no_password HOST LOCAL;

-- =====================================
-- 2. 角色管理示例
-- =====================================

-- 2.1 创建角色层次结构
-- 基础角色
CREATE ROLE basic_reader;
CREATE ROLE data_analyst;
CREATE ROLE data_engineer; 
CREATE ROLE system_admin;

-- 2.2 为角色分配权限
-- 基础读取权限
GRANT SELECT ON public.* TO basic_reader;

-- 分析师权限
GRANT basic_reader TO data_analyst;
GRANT SELECT ON analytics.* TO data_analyst;
GRANT SELECT ON reporting.* TO data_analyst;

-- 数据工程师权限
GRANT data_analyst TO data_engineer;
GRANT INSERT, ALTER, CREATE, DROP ON staging.* TO data_engineer;
GRANT INSERT ON analytics.* TO data_engineer;

-- 系统管理员权限
GRANT data_engineer TO system_admin;
GRANT ALL ON *.* TO system_admin;
GRANT SYSTEM, ACCESS MANAGEMENT ON *.* TO system_admin;

-- 2.3 分配角色给用户
GRANT basic_reader TO analyst_user;
GRANT data_engineer TO etl_user;
GRANT system_admin TO admin_user;

-- 设置默认角色
ALTER USER analyst_user DEFAULT ROLE basic_reader;
ALTER USER etl_user DEFAULT ROLE data_engineer;
ALTER USER admin_user DEFAULT ROLE system_admin;

-- 2.4 查看角色和权限
SHOW ROLES;
SHOW GRANTS FOR analyst_user;
SHOW GRANTS FOR data_analyst;

-- =====================================
-- 3. 数据库和表权限示例
-- =====================================

-- 3.1 创建测试数据库和表
CREATE DATABASE IF NOT EXISTS security_demo;
CREATE DATABASE IF NOT EXISTS sensitive_data;

USE security_demo;

-- 创建测试表
CREATE TABLE public_data (
    id UInt64,
    name String,
    category String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

CREATE TABLE sensitive_info (
    id UInt64,
    user_id UInt64,
    ssn String,
    credit_card String,
    salary Decimal64(2),
    department String
) ENGINE = MergeTree()
ORDER BY id;

-- 插入测试数据
INSERT INTO public_data VALUES 
(1, 'Product A', 'Electronics', '2024-01-01 10:00:00'),
(2, 'Product B', 'Books', '2024-01-02 11:00:00'),
(3, 'Product C', 'Clothing', '2024-01-03 12:00:00');

INSERT INTO sensitive_info VALUES 
(1, 1001, '123-45-6789', '1234-5678-9012-3456', 75000.00, 'Engineering'),
(2, 1002, '987-65-4321', '9876-5432-1098-7654', 85000.00, 'Marketing'),
(3, 1003, '456-78-9123', '4567-8901-2345-6789', 95000.00, 'Finance');

-- 3.2 细粒度权限控制
-- 创建部门经理角色
CREATE ROLE dept_manager;

-- 只允许查看特定列
GRANT SELECT(id, name, category) ON security_demo.public_data TO dept_manager;

-- 创建HR角色，可以查看薪资信息
CREATE ROLE hr_manager;
GRANT SELECT ON security_demo.sensitive_info TO hr_manager;

-- 创建财务角色，只能查看薪资相关信息
CREATE ROLE finance_manager;
GRANT SELECT(id, user_id, salary, department) ON security_demo.sensitive_info TO finance_manager;

-- =====================================
-- 4. 数据加密和脱敏示例
-- =====================================

-- 4.1 创建加密表
CREATE TABLE encrypted_customer_data (
    id UInt64,
    name String,
    -- 加密敏感字段
    phone String CODEC(AES_128_GCM_SIV),
    email String CODEC(AES_128_GCM_SIV),
    ssn String CODEC(AES_256_GCM_SIV),
    credit_card String CODEC(AES_256_GCM_SIV),
    address String CODEC(AES_128_GCM_SIV)
) ENGINE = MergeTree()
ORDER BY id;

-- 插入加密数据
INSERT INTO encrypted_customer_data VALUES 
(1, 'John Doe', '555-1234', 'john@example.com', '123-45-6789', '1234-5678-9012-3456', '123 Main St'),
(2, 'Jane Smith', '555-5678', 'jane@example.com', '987-65-4321', '9876-5432-1098-7654', '456 Oak Ave'),
(3, 'Bob Johnson', '555-9012', 'bob@example.com', '456-78-9123', '4567-8901-2345-6789', '789 Pine Rd');

-- 4.2 创建脱敏视图
CREATE VIEW customer_masked_view AS
SELECT 
    id,
    name,
    -- 电话号码脱敏：显示前3位和后4位
    concat(substring(phone, 1, 3), '-****-', substring(phone, -4)) as phone_masked,
    -- 邮箱脱敏：显示前2位和域名
    concat(substring(email, 1, 2), '***@', 
           substring(email, position(email, '@') + 1)) as email_masked,
    -- SSN脱敏：只显示后4位
    concat('***-**-', substring(ssn, -4)) as ssn_masked,
    -- 信用卡脱敏：只显示后4位
    concat('****-****-****-', substring(credit_card, -4)) as credit_card_masked,
    -- 地址脱敏：只显示门牌号
    substring(address, 1, position(address, ' ')) as address_masked
FROM encrypted_customer_data;

-- 4.3 使用加密函数
CREATE TABLE manual_encryption (
    id UInt64,
    name String,
    encrypted_data String
) ENGINE = MergeTree()
ORDER BY id;

-- 手动加密插入（注意：实际使用中应该使用更安全的密钥管理）
INSERT INTO manual_encryption 
SELECT 
    number as id,
    concat('User ', toString(number)) as name,
    encrypt('aes-256-gcm', concat('sensitive_data_', toString(number)), 'secret_key_32_chars_long_exactly', 'random_iv_12b') as encrypted_data
FROM numbers(5);

-- 解密数据（需要相同的密钥和IV）
SELECT 
    id,
    name,
    decrypt('aes-256-gcm', encrypted_data, 'secret_key_32_chars_long_exactly', 'random_iv_12b') as decrypted_data
FROM manual_encryption;

-- =====================================
-- 5. 行级安全示例
-- =====================================

-- 5.1 创建部门数据表
CREATE TABLE employee_data (
    id UInt64,
    name String,
    department String,
    salary Decimal64(2),
    manager String
) ENGINE = MergeTree()
ORDER BY id;

INSERT INTO employee_data VALUES 
(1, 'Alice Johnson', 'Engineering', 85000, 'John Smith'),
(2, 'Bob Wilson', 'Engineering', 75000, 'John Smith'),
(3, 'Carol Davis', 'Marketing', 70000, 'Jane Doe'),
(4, 'Dave Brown', 'Marketing', 68000, 'Jane Doe'),
(5, 'Eve Miller', 'Finance', 90000, 'Mike Johnson'),
(6, 'Frank Garcia', 'Finance', 82000, 'Mike Johnson');

-- 5.2 创建部门映射表
CREATE TABLE user_departments (
    user_name String,
    department String,
    role String
) ENGINE = MergeTree()
ORDER BY user_name;

INSERT INTO user_departments VALUES 
('dept_eng_manager', 'Engineering', 'manager'),
('dept_mkt_manager', 'Marketing', 'manager'),
('dept_fin_manager', 'Finance', 'manager');

-- 5.3 创建行级安全策略
-- 部门经理只能查看自己部门的数据
CREATE ROW POLICY dept_access ON employee_data
FOR SELECT
USING department IN (
    SELECT department 
    FROM user_departments 
    WHERE user_name = currentUser()
)
TO dept_manager;

-- 经理只能查看自己管理的员工
CREATE ROW POLICY manager_access ON employee_data  
FOR SELECT
USING manager = currentUser()
TO manager_role;

-- 查看行级安全策略
SHOW ROW POLICIES;

-- =====================================
-- 6. 审计和监控示例
-- =====================================

-- 6.1 创建审计视图
CREATE VIEW user_activity_audit AS
SELECT 
    user,
    client_address,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage,
    left(query, 100) as query_snippet,
    event_time
FROM system.query_log 
WHERE type = 'QueryFinish'
AND event_date >= today() - 1;

-- 6.2 安全事件监控
CREATE VIEW security_events AS
-- 登录失败事件
SELECT 
    'Login Failure' as event_type,
    user,
    client_address,
    event_time,
    'Failed login attempt' as description
FROM system.session_log
WHERE event_type = 'LoginFailure'
AND event_time >= now() - INTERVAL 24 HOUR

UNION ALL

-- 权限相关操作
SELECT 
    'Permission Change' as event_type,
    user,
    client_address,
    event_time,
    'User/Role management operation' as description
FROM system.query_log
WHERE (query ILIKE '%CREATE USER%' 
    OR query ILIKE '%DROP USER%'
    OR query ILIKE '%GRANT%'
    OR query ILIKE '%REVOKE%'
    OR query ILIKE '%CREATE ROLE%'
    OR query ILIKE '%DROP ROLE%')
AND event_time >= now() - INTERVAL 24 HOUR

UNION ALL

-- 数据删除操作
SELECT 
    'Data Deletion' as event_type,
    user,
    client_address,
    event_time,
    'Potentially dangerous data operation' as description  
FROM system.query_log
WHERE (query ILIKE '%DROP TABLE%'
    OR query ILIKE '%TRUNCATE%'
    OR query ILIKE '%DELETE%')
AND event_time >= now() - INTERVAL 24 HOUR;

-- 6.3 查看当前活跃用户
SELECT 
    user,
    client_address,
    query_id,
    elapsed,
    left(query, 80) as current_query,
    memory_usage
FROM system.processes
WHERE user != 'default'
ORDER BY elapsed DESC;

-- =====================================
-- 7. 配额和限制示例
-- =====================================

-- 7.1 创建用户配额
-- 创建限制配额
CREATE QUOTA limited_quota 
FOR INTERVAL 1 HOUR MAX queries = 100, errors = 10, result_rows = 1000000, 
    read_rows = 10000000, execution_time = 3600;

-- 创建高级用户配额  
CREATE QUOTA premium_quota
FOR INTERVAL 1 HOUR MAX queries = 1000, errors = 50, result_rows = 100000000,
    read_rows = 1000000000, execution_time = 7200;

-- 7.2 创建设置配置文件
CREATE SETTINGS PROFILE restricted_profile SETTINGS 
    max_memory_usage = 1000000000,
    max_execution_time = 60,
    readonly = 1;

CREATE SETTINGS PROFILE power_user_profile SETTINGS
    max_memory_usage = 10000000000,
    max_execution_time = 1800,
    max_threads = 16;

-- 7.3 应用配额和配置文件
-- 创建受限用户
CREATE USER restricted_user 
IDENTIFIED WITH sha256_password BY 'RestrictedPass@123'
SETTINGS PROFILE 'restricted_profile'
QUOTA 'limited_quota';

-- 创建高级用户
CREATE USER power_user
IDENTIFIED WITH sha256_password BY 'PowerUser@456'  
SETTINGS PROFILE 'power_user_profile'
QUOTA 'premium_quota';

-- =====================================
-- 8. 测试权限和安全配置
-- =====================================

-- 8.1 权限测试查询
-- 以不同用户身份执行以下查询来测试权限

-- 测试基础读取权限
SELECT count() FROM security_demo.public_data;

-- 测试敏感数据访问
SELECT * FROM security_demo.sensitive_info LIMIT 5;

-- 测试脱敏视图
SELECT * FROM customer_masked_view LIMIT 5;

-- 测试行级安全
SELECT name, department, salary FROM employee_data;

-- 8.2 查看加密效果
-- 查看原始数据（加密存储）
SELECT name, length(phone) as phone_encrypted_length 
FROM encrypted_customer_data;

-- 查看脱敏后的数据
SELECT * FROM customer_masked_view;

-- =====================================
-- 9. 权限管理维护
-- =====================================

-- 9.1 定期权限审查
-- 查看所有用户及其角色
SELECT 
    name as user_name,
    default_roles_list,
    granted_roles_list
FROM system.users;

-- 查看所有角色及其权限
SELECT 
    role_name,
    granted_roles_list  
FROM system.roles;

-- 查看具体权限
SELECT 
    user_name,
    role_name,
    access_type,
    database,
    table,
    column
FROM system.grants
WHERE user_name IS NOT NULL OR role_name IS NOT NULL;

-- 9.2 清理和维护
-- 撤销不需要的权限
-- REVOKE SELECT ON sensitive_data.* FROM old_user;

-- 删除不使用的用户和角色
-- DROP USER IF EXISTS temp_user;
-- DROP ROLE IF EXISTS temp_role;

-- 9.3 安全检查查询
-- 检查无密码用户
SELECT name FROM system.users WHERE auth_type = 'no_password';

-- 检查弱权限配置
SELECT name FROM system.users WHERE host_names_regexp = '.*';

-- 检查过期或异常的会话
SELECT 
    user,
    client_address,
    session_id,
    login_time,
    now() - login_time as session_duration
FROM system.session_log 
WHERE event_type = 'LoginSuccess'
AND now() - login_time > INTERVAL 24 HOUR;

-- =====================================
-- 10. 备份安全配置
-- =====================================

-- 10.1 导出用户配置
-- 查看用户创建语句（用于备份）
SHOW CREATE USER admin_user;
SHOW CREATE USER analyst_user;

-- 10.2 导出角色配置
SHOW CREATE ROLE data_analyst;
SHOW CREATE ROLE data_engineer;

-- 10.3 导出权限配置
-- 这些查询的结果可以用于重建权限结构
SELECT 
    concat('GRANT ', access_type, ' ON ', 
           if(database = '', '*', database), '.', 
           if(table = '', '*', table), 
           ' TO ', if(user_name != '', user_name, role_name), ';') as grant_statement
FROM system.grants
WHERE (user_name != '' OR role_name != '');

-- =====================================
-- 清理示例数据 (可选)
-- =====================================

-- 清理测试用户和角色
-- DROP USER IF EXISTS admin_user;
-- DROP USER IF EXISTS analyst_user; 
-- DROP USER IF EXISTS api_user;
-- DROP USER IF EXISTS etl_user;

-- DROP ROLE IF EXISTS basic_reader;
-- DROP ROLE IF EXISTS data_analyst;
-- DROP ROLE IF EXISTS data_engineer;
-- DROP ROLE IF EXISTS system_admin;

-- 清理测试数据库
-- DROP DATABASE IF EXISTS security_demo;
-- DROP DATABASE IF EXISTS sensitive_data; 