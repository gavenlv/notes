# ClickHouse Day 11: 安全权限

## 学习目标
- 掌握 ClickHouse 用户管理机制
- 理解权限控制和访问控制
- 学习数据安全和加密技术
- 实践安全配置和审计功能

## 1. 用户管理

### 1.1 用户管理基础

#### 传统配置文件方式
```xml
<!-- users.xml -->
<users>
    <user_name>
        <password>password_here</password>
        <!-- 或使用SHA256哈希 -->
        <password_sha256_hex>hash_here</password_sha256_hex>
        
        <networks>
            <ip>127.0.0.1</ip>
            <ip>10.0.0.0/8</ip>
            <ip>::1</ip>
        </networks>
        
        <profile>default</profile>
        <quota>default</quota>
        
        <databases>
            <database>database_name</database>
        </databases>
    </user_name>
</users>
```

#### SQL方式用户管理 (推荐)
```sql
-- 创建用户
CREATE USER john_doe 
IDENTIFIED WITH sha256_password BY 'secure_password';

-- 设置用户属性
CREATE USER analytics_user 
IDENTIFIED WITH sha256_password BY 'analytics_pass'
HOST IP '192.168.1.0/24', IP '10.0.0.0/8'
DEFAULT ROLE analyst;

-- 修改用户
ALTER USER john_doe 
IDENTIFIED WITH sha256_password BY 'new_password';

-- 删除用户
DROP USER john_doe;

-- 查看用户列表
SHOW USERS;

-- 查看当前用户
SELECT user();

-- 查看用户详细信息
SHOW CREATE USER john_doe;
```

### 1.2 认证方式

#### 1. 明文密码 (不推荐)
```sql
CREATE USER test_user IDENTIFIED WITH plaintext_password BY 'password123';
```

#### 2. SHA256 哈希密码 (推荐)
```sql
CREATE USER secure_user IDENTIFIED WITH sha256_password BY 'secure_password';
```

#### 3. SHA256 双重哈希
```sql
CREATE USER double_hash_user IDENTIFIED WITH double_sha1_password BY 'password';
```

#### 4. LDAP 认证
```sql
-- 需要在config.xml中配置LDAP服务器
CREATE USER ldap_user IDENTIFIED WITH ldap BY 'ldap_server';
```

#### 5. Kerberos 认证
```sql
CREATE USER kerberos_user IDENTIFIED WITH kerberos;
```

### 1.3 网络访问控制

```sql
-- 允许特定IP
CREATE USER restricted_user 
IDENTIFIED WITH sha256_password BY 'password'
HOST IP '192.168.1.100';

-- 允许IP段
CREATE USER network_user 
IDENTIFIED WITH sha256_password BY 'password'
HOST IP '10.0.0.0/8', IP '172.16.0.0/12';

-- 允许主机名
CREATE USER hostname_user 
IDENTIFIED WITH sha256_password BY 'password'
HOST NAME 'trusted-server.company.com';

-- 正则表达式匹配主机名
CREATE USER regex_user 
IDENTIFIED WITH sha256_password BY 'password'
HOST REGEXP '.*\.company\.com';

-- 允许任何地址 (不推荐)
CREATE USER any_user 
IDENTIFIED WITH sha256_password BY 'password'
HOST ANY;
```

## 2. 权限控制

### 2.1 权限模型

ClickHouse 采用基于角色的访问控制 (RBAC) 模型：
- **权限 (Privileges)**: 对特定资源的操作权限
- **角色 (Roles)**: 权限的集合
- **用户 (Users)**: 被分配角色的主体

### 2.2 权限类型

#### 系统权限
```sql
-- 查看所有权限类型
SHOW PRIVILEGES;

-- 主要权限类型：
-- SELECT, INSERT, ALTER, CREATE, DROP, TRUNCATE
-- OPTIMIZE, SHOW, KILL QUERY, ACCESS MANAGEMENT
-- SYSTEM, INTROSPECTION, DICTIONARIES
```

#### 数据库级权限
```sql
-- 授予数据库所有权限
GRANT ALL ON database_name.* TO user_name;

-- 授予特定权限
GRANT SELECT, INSERT ON database_name.* TO user_name;

-- 授予特定表权限
GRANT SELECT ON database_name.table_name TO user_name;

-- 授予列级权限
GRANT SELECT(column1, column2) ON database_name.table_name TO user_name;
```

#### 系统权限
```sql
-- 系统管理权限
GRANT SYSTEM ON *.* TO admin_user;

-- 查询管理权限
GRANT KILL QUERY ON *.* TO monitor_user;

-- 字典管理权限  
GRANT DICTIONARIES ON *.* TO dict_admin;
```

### 2.3 角色管理

#### 创建和管理角色
```sql
-- 创建角色
CREATE ROLE analyst;
CREATE ROLE data_engineer;
CREATE ROLE admin;

-- 为角色授权
GRANT SELECT ON analytics.* TO analyst;
GRANT INSERT, SELECT ON staging.* TO data_engineer;
GRANT ALL ON *.* TO admin;

-- 创建角色层次结构
GRANT analyst TO data_engineer;
GRANT data_engineer TO admin;

-- 查看角色
SHOW ROLES;
SHOW CREATE ROLE analyst;
```

#### 用户角色分配
```sql
-- 分配角色给用户
GRANT analyst TO john_doe;
GRANT data_engineer TO jane_smith;

-- 设置默认角色
ALTER USER john_doe DEFAULT ROLE analyst;

-- 查看用户角色
SHOW GRANTS FOR john_doe;

-- 撤销角色
REVOKE analyst FROM john_doe;
```

### 2.4 权限继承和优先级

```sql
-- 角色继承示例
CREATE ROLE base_user;
CREATE ROLE power_user;
CREATE ROLE admin_user;

-- 基础权限
GRANT SELECT ON public.* TO base_user;

-- 扩展权限
GRANT base_user TO power_user;
GRANT INSERT, UPDATE ON public.* TO power_user;

-- 管理员权限
GRANT power_user TO admin_user;
GRANT ALL ON *.* TO admin_user;

-- 用户获得层次化权限
GRANT admin_user TO super_admin;
```

## 3. 数据安全

### 3.1 数据加密

#### 存储加密
```xml
<!-- config.xml 中的磁盘加密配置 -->
<storage_configuration>
    <disks>
        <encrypted_disk>
            <type>encrypted</type>
            <disk>default</disk>
            <path>/var/lib/clickhouse/encrypted/</path>
            <key>your_encryption_key_here</key>
            <algorithm>AES_128_CTR</algorithm>
        </encrypted_disk>
    </disks>
    
    <policies>
        <encrypted_policy>
            <volumes>
                <main>
                    <disk>encrypted_disk</disk>
                </main>
            </volumes>
        </encrypted_policy>
    </policies>
</storage_configuration>
```

#### 列级加密
```sql
-- 创建带加密列的表
CREATE TABLE sensitive_data (
    id UInt64,
    name String,
    -- 加密敏感字段
    ssn String CODEC(AES_128_GCM_SIV),
    credit_card String CODEC(AES_256_GCM_SIV),
    salary Decimal64(2) CODEC(AES_128_GCM_SIV)
) ENGINE = MergeTree()
ORDER BY id;

-- 使用加密函数
CREATE TABLE encrypted_table (
    id UInt64,
    encrypted_data String DEFAULT encrypt('aes-256-gcm', original_data, 'secret_key', 'iv')
) ENGINE = MergeTree()
ORDER BY id;
```

### 3.2 传输加密 (TLS/SSL)

#### 服务器配置
```xml
<!-- config.xml -->
<https_port>8443</https_port>
<tcp_port_secure>9440</tcp_port_secure>

<openSSL>
    <server>
        <certificateFile>/etc/clickhouse-server/server.crt</certificateFile>
        <privateKeyFile>/etc/clickhouse-server/server.key</privateKeyFile>
        <dhParamsFile>/etc/clickhouse-server/dhparam.pem</dhParamsFile>
        <verificationMode>none</verificationMode>
        <loadDefaultCAFile>true</loadDefaultCAFile>
        <cacheSessions>true</cacheSessions>
        <disableProtocols>sslv2,sslv3</disableProtocols>
        <preferServerCiphers>true</preferServerCiphers>
    </server>
</openSSL>
```

#### 客户端连接
```bash
# 使用SSL连接
clickhouse-client --host localhost --port 9440 --secure

# 使用HTTPS
curl -k "https://localhost:8443/" -d "SELECT 1"
```

### 3.3 数据脱敏

```sql
-- 创建脱敏视图
CREATE VIEW customer_view AS
SELECT 
    id,
    name,
    -- 电话号码脱敏
    concat(substring(phone, 1, 3), '****', substring(phone, 8)) as phone_masked,
    -- 邮箱脱敏
    concat(substring(email, 1, 2), '***@', substring(email, position(email, '@') + 1)) as email_masked,
    -- 身份证脱敏
    concat(substring(id_card, 1, 6), '********', substring(id_card, 15)) as id_card_masked
FROM customer_table;

-- 动态脱敏函数
CREATE FUNCTION mask_phone AS (phone) -> 
    concat(substring(phone, 1, 3), '****', substring(phone, -4));

-- 使用脱敏函数
SELECT mask_phone(phone) FROM customer_table;
```

### 3.4 行级安全 (Row Level Security)

```sql
-- 创建行级安全策略
CREATE ROW POLICY regional_access ON sales_data
FOR SELECT
USING region = currentUser()
TO regional_manager;

-- 基于角色的行级安全
CREATE ROW POLICY department_access ON employee_data
FOR SELECT
USING department IN (
    SELECT department 
    FROM user_departments 
    WHERE user_name = currentUser()
)
TO department_manager;

-- 查看行级安全策略
SHOW ROW POLICIES;
SHOW CREATE ROW POLICY regional_access ON sales_data;
```

## 4. 安全配置和审计

### 4.1 安全配置

#### 密码策略
```xml
<!-- config.xml -->
<password_complexity>
    <min_length>8</min_length>
    <require_lowercase>true</require_lowercase>
    <require_uppercase>true</require_uppercase>
    <require_numbers>true</require_numbers>
    <require_symbols>true</require_symbols>
</password_complexity>

<password_history>
    <remember_count>5</remember_count>
</password_history>

<session_timeout>3600</session_timeout>
<max_login_attempts>3</max_login_attempts>
<lockout_duration>1800</lockout_duration>
```

#### 访问控制
```xml
<!-- 限制查询复杂度 -->
<profiles>
    <restricted>
        <max_memory_usage>1000000000</max_memory_usage>
        <max_execution_time>60</max_execution_time>
        <max_rows_to_read>10000000</max_rows_to_read>
        <readonly>1</readonly>
    </restricted>
</profiles>
```

### 4.2 审计日志

#### 启用审计日志
```xml
<!-- config.xml -->
<query_log>
    <database>system</database>
    <table>query_log</table>
    <partition_by>toYYYYMM(event_date)</partition_by>
    <flush_interval_milliseconds>7500</flush_interval_milliseconds>
</query_log>

<session_log>
    <database>system</database>
    <table>session_log</table>
    <partition_by>toYYYYMM(event_date)</partition_by>
    <flush_interval_milliseconds>7500</flush_interval_milliseconds>
</session_log>
```

#### 审计查询示例
```sql
-- 查看用户登录记录
SELECT 
    user,
    client_hostname,
    client_address,
    event_time,
    session_id
FROM system.session_log
WHERE event_date >= today() - 7
ORDER BY event_time DESC;

-- 查看敏感操作
SELECT 
    user,
    query,
    event_time,
    client_address
FROM system.query_log
WHERE query ILIKE '%DROP%' 
   OR query ILIKE '%ALTER%'
   OR query ILIKE '%CREATE USER%'
   OR query ILIKE '%GRANT%'
ORDER BY event_time DESC;

-- 查看失败的查询
SELECT 
    user,
    query,
    exception,
    event_time
FROM system.query_log
WHERE type = 'ExceptionWhileProcessing'
AND event_date >= today() - 1
ORDER BY event_time DESC;
```

### 4.3 安全监控

```sql
-- 创建安全监控视图
CREATE VIEW security_alerts AS
SELECT 
    'Failed Login' as alert_type,
    user,
    client_address,
    event_time,
    'Multiple failed login attempts' as description
FROM system.session_log
WHERE event_type = 'LoginFailure'
AND event_time >= now() - INTERVAL 1 HOUR
GROUP BY user, client_address, event_time
HAVING count() > 3

UNION ALL

SELECT 
    'Suspicious Query' as alert_type,
    user,
    client_address,
    event_time,
    'Potential SQL injection attempt' as description
FROM system.query_log
WHERE (query ILIKE '%UNION%SELECT%' 
    OR query ILIKE '%OR%1=1%'
    OR query ILIKE '%DROP%TABLE%')
AND event_time >= now() - INTERVAL 1 HOUR;
```

## 5. 最佳实践

### 5.1 用户管理最佳实践

1. **最小权限原则**
   - 只授予用户完成工作所需的最小权限
   - 定期审查和清理不必要的权限

2. **角色化管理**
   - 使用角色而非直接授权给用户
   - 建立清晰的角色层次结构

3. **强密码策略**
   - 使用复杂密码
   - 定期更换密码
   - 使用SHA256哈希存储

### 5.2 网络安全最佳实践

1. **网络隔离**
   - 使用防火墙限制访问
   - 配置IP白名单
   - 使用VPN或专用网络

2. **传输加密**
   - 启用TLS/SSL加密
   - 使用强加密算法
   - 定期更新证书

### 5.3 数据保护最佳实践

1. **敏感数据处理**
   - 对敏感数据进行加密
   - 实施数据脱敏
   - 使用行级安全控制

2. **备份和恢复**
   - 加密备份数据
   - 定期测试恢复过程
   - 安全存储备份

### 5.4 监控和审计最佳实践

1. **日志管理**
   - 启用全面的审计日志
   - 定期分析日志
   - 设置安全告警

2. **合规性**
   - 遵循相关法规要求
   - 定期安全评估
   - 建立事件响应流程

## 6. 实践练习

### 练习1：用户和角色管理
1. 创建不同级别的角色（只读、分析师、管理员）
2. 创建用户并分配相应角色
3. 测试权限控制效果

### 练习2：数据安全
1. 配置传输加密
2. 实施列级加密
3. 创建数据脱敏视图

### 练习3：安全监控
1. 启用审计日志
2. 创建安全监控查询
3. 设置告警机制

## 7. 常见安全问题和解决方案

### 问题1：权限过度授予
**解决方案**：
- 定期权限审查
- 实施最小权限原则
- 使用临时权限

### 问题2：弱密码策略
**解决方案**：
- 配置密码复杂度要求
- 强制定期更换密码
- 使用多因素认证

### 问题3：数据泄露风险
**解决方案**：
- 实施数据加密
- 使用数据脱敏
- 配置网络访问控制

## 8. 总结

ClickHouse 安全权限管理的核心要点：

1. **用户管理**：使用SQL方式管理用户，配置强认证
2. **权限控制**：基于RBAC模型，实施最小权限原则
3. **数据安全**：多层次加密保护，数据脱敏处理
4. **审计监控**：全面日志记录，实时安全监控

## 9. 下一步学习

- Day 12: 备份恢复策略
- 深入学习企业级安全架构
- 了解更多合规性要求和实现 