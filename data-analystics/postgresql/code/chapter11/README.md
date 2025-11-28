# PostgreSQL第11章：安全与权限管理
## PostgreSQL Security and Access Control

### 章节概述

PostgreSQL提供了强大的安全功能和多层权限管理体系。本章将学习PostgreSQL的用户管理、权限控制、角色管理、审计日志、SSL配置、加密存储等安全最佳实践，确保数据库的安全性和合规性。

### 学习目标

- 掌握PostgreSQL用户和角色管理
- 理解权限系统（GRANT/REVOKE）
- 学习行级安全（RLS）策略
- 掌握数据库审计和日志监控
- 了解SSL/TLS配置和数据加密
- 学会安全配置和合规性检查

### 文件说明

1. **user_management.sql** - 用户和角色管理
   - 用户创建和管理
   - 角色权限分配
   - 角色继承和组合
   - 密码策略和安全设置

2. **permission_management.sql** - 权限管理系统
   - 细粒度权限控制
   - 行级安全策略(RLS)
   - 权限继承和角色权限管理
   - 权限审计和监控

3. **security_policies.sql** - 安全策略管理
   - 数据分类和访问控制策略
   - 审计和监控策略
   - 数据脱敏和隐私保护策略
   - 安全策略管理和报告

4. **security_compliance.py** - Python安全合规脚本
   - GDPR/SOX合规检查
   - 数据分类和标记管理
   - 合规报告生成
   - 风险评估和管理

### 环境准备

#### PostgreSQL安全配置
```sql
-- 设置密码复杂度策略
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();

-- 启用审计扩展（需要先安装）
-- CREATE EXTENSION IF NOT EXISTS pgaudit;
```

#### 目录准备
```bash
# 创建SSL证书目录
mkdir -p /var/lib/postgresql/ssl/{certs,private}
chown postgres:postgres /var/lib/postgresql/ssl

# 创建审计日志目录
mkdir -p /var/log/postgresql/audit
chown postgres:postgres /var/log/postgresql/audit
```

### 运行指南

#### 1. 用户和权限管理测试
```sql
-- 登录PostgreSQL
psql -U postgres -d your_database

-- 执行权限管理相关SQL文件
\i user_management.sql
\i permission_control.sql
\i row_level_security.sql
```

#### 2. 安全审计测试
```sql
-- 执行审计相关SQL文件
\i audit_security.sql
\i ssl_encryption.sql
```

#### 3. Python安全脚本运行
```bash
# 安装Python依赖
pip install -r requirements.txt

# 运行安全脚本
python security_examples.py

# 或单独运行安全检查
python -c "from security_examples import SecurityManager; SecurityManager().check_permissions()"
```

### 关键命令示例

#### 用户管理
```sql
-- 创建用户和角色
CREATE ROLE app_readonly LOGIN PASSWORD 'secure_password';
CREATE ROLE app_readwrite;
CREATE ROLE admin_user WITH CREATEDB CREATEROLE;

-- 分配权限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT ALL PRIVILEGES ON DATABASE your_database TO admin_user;

-- 角色继承
GRANT app_readonly TO app_readwrite;
```

#### 行级安全策略
```sql
-- 启用行级安全
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY user_isolation ON users
    FOR ALL TO application_user
    USING (user_id = current_user_id());

-- 测试策略
SET ROLE application_user;
SELECT * FROM users;  -- 只返回当前用户的记录
RESET ROLE;
```

#### 审计查询
```sql
-- 查看登录日志
SELECT 
    log_time,
    user_name,
    session_id,
    remote_host,
    session_line_num,
    command_tag,
    statement
FROM pg_stat_activity
WHERE log_time >= CURRENT_DATE;

-- 查看权限变更
SELECT 
    timestamp,
    user_name,
    action,
    object_name,
    details
FROM information_schema.role_table_grants
WHERE grantee = 'your_user';
```

#### SSL配置检查
```sql
-- 检查SSL连接状态
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    ssl,
    ssl_version,
    ssl_cipher,
    ssl_bits
FROM pg_stat_activity
WHERE ssl = true;

-- 强制SSL连接
REVOKE CONNECT ON DATABASE your_database FROM PUBLIC;
GRANT CONNECT ON DATABASE your_database TO your_user REQUIRE SSL;
```

### 注意事项

1. **密码安全**
   - 使用强密码策略
   - 定期更换密码
   - 启用密码验证插件
   - 禁用空密码

2. **权限最小化原则**
   - 只授予必要的权限
   - 定期审查权限分配
   - 使用角色分组管理
   - 避免使用超级用户权限

3. **网络安全**
   - 强制SSL连接
   - 限制连接来源
   - 使用防火墙规则
   - 定期更新安全配置

4. **审计合规**
   - 启用详细审计日志
   - 定期分析安全日志
   - 设置异常行为告警
   - 保留合规性记录

### 扩展学习资源

- [PostgreSQL安全文档](https://www.postgresql.org/docs/current/security.html)
- [PCI DSS合规指南](https://www.postgresql.org/docs/current/pg雪花-encryption.html)
- [行级安全最佳实践](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [审计扩展pgAudit](https://www.pgaudit.org/)

### 下一步学习

1. 深入学习PostgreSQL高级特性
2. 学习PostgreSQL集群和高可用
3. 研究大数据处理和分析
4. 探索PostgreSQL在云环境中的应用

---

*完成PostgreSQL教程系列后，你将具备全面的PostgreSQL数据库管理和开发能力，能够胜任生产环境的数据库管理工作。*
