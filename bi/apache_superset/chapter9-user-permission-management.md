# 第九章：用户与权限管理

## 9.1 权限管理概述

Apache Superset 提供了一套完整的用户和权限管理系统，用于控制用户对系统资源的访问。这套系统基于角色的访问控制（RBAC）模型，通过精细化的权限分配确保数据安全和系统稳定。

### 核心概念

#### 用户（User）

用户是系统的使用者，每个用户都有唯一的用户名和密码用于身份验证。用户可以被分配到一个或多个角色中。

#### 角色（Role）

角色是一组权限的集合，代表了用户在系统中的职责和权限范围。通过将用户分配到合适的角色，可以批量管理用户的权限。

#### 权限（Permission）

权限是对系统资源的具体操作许可，如查看、编辑、删除等。权限通常与特定的资源类型绑定。

#### 资源（Resource）

资源是系统中可以被访问的对象，如数据源、数据集、图表、仪表板等。

### 权限模型

Superset 采用基于角色的访问控制（Role-Based Access Control, RBAC）模型：

1. **用户-角色关联**：用户可以属于一个或多个角色
2. **角色-权限关联**：角色拥有特定的权限集合
3. **权限-资源关联**：权限控制对具体资源的操作

这种模型的优势在于：
- 简化权限管理：通过角色而非单个用户来分配权限
- 提高安全性：最小权限原则，仅授予必需的权限
- 易于维护：当组织结构变化时，只需调整角色分配

## 9.2 用户管理

### 用户创建

#### 通过管理界面创建用户

1. 登录管理员账户
2. 导航到 **Settings** > **Users**
3. 点击 **+ User** 按钮
4. 填写用户信息：
   - **Username**：用户登录名
   - **First Name**：名字
   - **Last Name**：姓氏
   - **Email**：邮箱地址
   - **Password**：密码
   - **Roles**：分配角色
5. 点击 **Save** 保存用户

#### 通过命令行创建用户

```bash
# 使用 Flask CLI 创建用户
flask fab create-user \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password admin123 \
  --role Admin
```

### 用户信息管理

#### 修改用户信息

管理员可以在用户管理界面中修改用户的基本信息：
- 更改姓名和邮箱
- 重置密码
- 调整角色分配
- 激活或停用用户账户

#### 批量用户导入

通过 CSV 文件批量导入用户：

```csv
username,first_name,last_name,email,password,roles
user1,John,Doe,john@example.com,password123,Alpha
user2,Jane,Smith,jane@example.com,password123,Beta
user3,Bob,Johnson,bob@example.com,password123,Gamma
```

### 用户状态管理

#### 激活/停用用户

管理员可以随时激活或停用用户账户：
- **Active**：用户可以正常登录和使用系统
- **Inactive**：用户无法登录系统，但仍保留账户信息

#### 密码策略

配置密码安全策略：

```python
# superset_config.py
PASSWORD_COMPLEXITY = {
    'min_length': 8,
    'require_lowercase': True,
    'require_uppercase': True,
    'require_digit': True,
    'require_special_char': True,
}
```

## 9.3 角色管理

### 内置角色

Superset 提供了几个内置角色：

#### 1. Admin（管理员）

拥有系统最高权限的角色：
- 管理所有用户和角色
- 访问和管理所有数据源、数据集、图表和仪表板
- 系统配置和设置
- 审计日志查看

#### 2. Alpha（高级用户）

具有广泛创建和编辑权限的角色：
- 创建和编辑自己的数据源、数据集、图表和仪表板
- 查看和编辑他人共享的内容
- 有限的管理功能

#### 3. Gamma（普通用户）

基础用户角色：
- 查看授权的数据源、数据集、图表和仪表板
- 创建和编辑自己的内容
- 不能创建新的数据源

#### 4. granter（授权者）

专门用于权限分配的角色：
- 可以为其他用户分配特定权限
- 不能访问实际的数据内容

#### 5. Public（公共用户）

匿名访问角色：
- 用于未登录用户的访问权限
- 通常权限非常有限

### 自定义角色创建

#### 创建新角色

1. 导航到 **Settings** > **Roles**
2. 点击 **+ Role** 按钮
3. 输入角色名称和描述
4. 从权限列表中选择该角色应该拥有的权限
5. 点击 **Save** 保存角色

#### 权限分配策略

根据不同业务需求创建自定义角色：

```python
# 销售角色示例
SALES_ROLE_PERMISSIONS = [
    'datasource_access_on_sale_database',
    'database_access_on_sale_database',
    'all_datasource_access',
    'can_chart',
    'can_dashboard',
    'menu_access_Charts',
    'menu_access_Dashboards',
]
```

### 角色权限细化

#### 数据源权限

控制用户对特定数据源的访问：

```python
# 配置数据源访问权限
DATASOURCE_ACCESS_PERMISSION = {
    'schema.sales_data': ['Sales Team', 'Managers'],
    'schema.marketing_data': ['Marketing Team', 'Managers'],
    'schema.finance_data': ['Finance Team', 'Managers'],
}
```

#### 数据集权限

控制用户对特定数据集的访问：

```python
# 行级安全策略
ROW_LEVEL_SECURITY = [
    {
        'dataset': 'employee_data',
        'filter': "department = '{{ current_user().extra_attributes.department }}'",
        'roles': ['Employee']
    },
    {
        'dataset': 'sales_data',
        'filter': "region = '{{ current_user().extra_attributes.region }}'",
        'roles': ['Regional Manager']
    }
]
```

## 9.4 数据权限控制

### 数据源访问控制

#### 数据库级别权限

控制用户对整个数据库的访问权限：

```python
# superset_config.py
DATABASE_ACCESS_PERMISSIONS = {
    'mysql_business_db': ['Business Analysts', 'Admin'],
    'postgres_analytics_db': ['Data Scientists', 'Admin'],
    'redshift_warehouse': ['Data Engineers', 'Admin'],
}
```

#### Schema 级别权限

控制用户对特定 Schema 的访问：

```python
# 控制 Schema 访问
SCHEMA_ACCESS_PERMISSIONS = {
    'business_db.sales_schema': ['Sales Team'],
    'business_db.marketing_schema': ['Marketing Team'],
    'analytics_db.modeling_schema': ['Data Scientists'],
}
```

### 数据集访问控制

#### 列级权限

控制用户对特定字段的访问：

```python
# 列级安全策略
COLUMN_LEVEL_SECURITY = [
    {
        'dataset': 'employee_data',
        'columns': ['salary', 'ssn'],
        'roles': ['HR', 'Management'],
        'access': 'deny'  # 或 'allow'
    }
]
```

#### 行级权限

控制用户能看到哪些数据行：

```python
# 行级安全示例
ROW_LEVEL_SECURITY = [
    {
        'dataset': 'customer_orders',
        'filter': "sales_rep = '{{ current_user().username }}'",
        'roles': ['Sales Rep']
    },
    {
        'dataset': 'financial_reports',
        'filter': "department = '{{ current_user().extra_attributes.department }}'",
        'roles': ['Department Head']
    }
]
```

### 动态权限控制

基于用户属性的动态权限：

```python
# 动态权限配置
def get_user_filter(user):
    """根据用户属性生成过滤条件"""
    if 'Regional Manager' in user.roles:
        return f"region = '{user.extra_attributes.region}'"
    elif 'Team Lead' in user.roles:
        return f"team = '{user.extra_attributes.team}'"
    else:
        return "1=0"  # 不允许访问

# 应用动态权限
DYNAMIC_ROW_LEVEL_SECURITY = {
    'sales_performance': get_user_filter
}
```

## 9.5 权限继承与组合

### 权限继承机制

角色之间可以建立继承关系：

```python
# 角色继承配置
ROLE_INHERITANCE = {
    'Manager': ['Employee'],  # Manager 继承 Employee 的所有权限
    'Admin': ['Manager', 'Analyst'],  # Admin 继承 Manager 和 Analyst 的权限
}
```

### 权限组合策略

通过组合不同角色实现精细权限控制：

```python
# 组合角色示例
COMPOSITE_ROLES = {
    'Sales_Manager': {
        'inherits': ['Sales_Rep', 'Report_Viewer'],
        'additional_permissions': [
            'can_approve_forecasts',
            'can_manage_team_quota'
        ]
    },
    'Data_Scientist': {
        'inherits': ['Analyst'],
        'additional_permissions': [
            'can_create_ml_models',
            'can_access_advanced_analytics'
        ]
    }
}
```

## 9.6 审计与监控

### 访问日志

记录用户访问行为：

```python
# 启用访问日志
ENABLE_ACCESS_LOG = True
ACCESS_LOG_RETENTION_DAYS = 90

# 日志格式配置
ACCESS_LOG_FORMAT = {
    'timestamp': '%Y-%m-%d %H:%M:%S',
    'user': '{user.username}',
    'action': '{request.method} {request.path}',
    'ip_address': '{request.remote_addr}',
    'user_agent': '{request.user_agent}'
}
```

### 权限变更审计

跟踪权限变更历史：

```python
# 权限变更日志
PERMISSION_AUDIT_LOG = {
    'enabled': True,
    'log_level': 'INFO',
    'retention_days': 365,
    'notify_on_critical_changes': True
}
```

### 异常访问检测

检测异常访问行为：

```python
# 异常访问检测规则
ANOMALY_DETECTION_RULES = [
    {
        'name': 'High Volume Access',
        'condition': 'query_count > 1000 in 1 hour',
        'action': 'alert_admin'
    },
    {
        'name': 'Unauthorized Access Attempt',
        'condition': 'access_denied_count > 5 in 10 minutes',
        'action': 'temp_ban_user'
    }
]
```

## 9.7 安全最佳实践

### 密码安全

```python
# 强密码策略
PASSWORD_POLICY = {
    'min_length': 12,
    'require_mixed_case': True,
    'require_numbers': True,
    'require_special_chars': True,
    'prevent_common_passwords': True,
    'password_expiration_days': 90,
    'password_history_count': 5
}
```

### 多因素认证

```python
# 启用 MFA
MFA_ENABLED = True
MFA_PROVIDERS = ['totp', 'sms', 'email']
MFA_ENFORCE_FOR_ADMIN = True
MFA_ENFORCE_FOR_SENSITIVE_ROLES = ['Finance', 'HR']
```

### 会话管理

```python
# 会话安全配置
SESSION_CONFIG = {
    'timeout': 3600,  # 1小时超时
    'refresh_on_activity': True,
    'max_concurrent_sessions': 2,
    'secure_cookies': True,
    'http_only_cookies': True
}
```

### 数据加密

```python
# 数据传输加密
SSL_REQUIRED = True
ENFORCE_SSL = True

# 敏感数据加密存储
SENSITIVE_DATA_ENCRYPTION = {
    'enabled': True,
    'algorithm': 'AES-256-GCM',
    'key_rotation_days': 90
}
```

## 9.8 集成外部认证系统

### LDAP 集成

```python
# LDAP 配置
AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://ldap.example.com"
AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "admin_password"
AUTH_LDAP_SEARCH = "ou=users,dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"

# LDAP 角色映射
AUTH_LDAP_GROUP_FIELD = "memberOf"
LDAP_ROLE_MAPPING = {
    "cn=admins,ou=groups,dc=example,dc=com": ["Admin"],
    "cn=sales,ou=groups,dc=example,dc=com": ["Sales"],
    "cn=marketing,ou=groups,dc=example,dc=com": ["Marketing"]
}
```

### OAuth 集成

```python
# OAuth 配置
OAUTH_PROVIDERS = [
    {
        'name': 'google',
        'icon': 'fa-google',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': 'GOOGLE_CLIENT_ID',
            'client_secret': 'GOOGLE_CLIENT_SECRET',
            'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
            'client_kwargs': {
                'scope': 'email profile'
            },
            'access_token_url': 'https://accounts.google.com/o/oauth2/token',
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'request_token_url': None,
        }
    }
]
```

### SAML 集成

```python
# SAML 配置
AUTH_TYPE = AUTH_SAML
SAML_CERT = '/path/to/saml_cert.pem'
SAML_PRIVATE_KEY = '/path/to/saml_private_key.pem'
SAML_METADATA_URL = 'https://idp.example.com/metadata'

# SAML 属性映射
SAML_ATTRIBUTE_MAPPING = {
    'uid': ['username'],
    'email': ['email'],
    'firstName': ['first_name'],
    'lastName': ['last_name']
}
```

## 9.9 权限管理自动化

### 脚本化权限管理

```python
# 权限管理脚本示例
from superset import security_manager

def bulk_assign_roles():
    """批量分配角色"""
    users = ['user1', 'user2', 'user3']
    roles = ['Sales', 'Reports']
    
    for username in users:
        user = security_manager.find_user(username=username)
        if user:
            for role_name in roles:
                role = security_manager.find_role(role_name)
                if role and role not in user.roles:
                    user.roles.append(role)
            security_manager.update_user(user)

def create_department_roles():
    """为各部门创建角色"""
    departments = ['Sales', 'Marketing', 'Engineering', 'Finance']
    
    for dept in departments:
        role_name = f"{dept}_Team"
        if not security_manager.find_role(role_name):
            role = security_manager.add_role(role_name)
            # 分配部门相关的权限
            permissions = get_department_permissions(dept)
            for perm in permissions:
                security_manager.add_permission_role(role, perm)
```

### 定期权限审查

```python
# 定期权限审查脚本
def audit_user_permissions():
    """审计用户权限"""
    inactive_users = []
    overprivileged_users = []
    
    for user in security_manager.get_all_users():
        # 检查不活跃用户
        if not user.is_active:
            inactive_users.append(user.username)
        
        # 检查权限过多的用户
        if len(user.roles) > 10:  # 假设超过10个角色为异常
            overprivileged_users.append({
                'username': user.username,
                'role_count': len(user.roles)
            })
    
    return {
        'inactive_users': inactive_users,
        'overprivileged_users': overprivileged_users
    }
```

## 9.10 小结

本章详细介绍了 Apache Superset 的用户和权限管理系统，包括用户管理、角色管理、数据权限控制、审计监控以及安全最佳实践等内容。通过合理配置权限系统，可以确保数据安全并满足企业的合规要求。

在下一章中，我们将学习 Apache Superset 的安全配置与加固措施。