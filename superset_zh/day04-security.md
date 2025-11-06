# 第四天：安全与权限

## 用户故事1：配置认证方法

**标题**：配置多种认证方法

**描述**：设置包括数据库、LDAP和OAuth在内的各种认证方法，为用户提供灵活的Superset访问方式。

**验收标准**：
- 数据库认证已配置并正常工作
- LDAP认证已设置（可选）
- OAuth集成已配置（可选）
- 用户可以使用配置的方法登录
- 失败的登录尝试已被记录

**分步指南**：

1. **数据库认证设置**：
```python
# superset_config.py
AUTH_TYPE = AUTH_DB
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Gamma"
```

2. **LDAP认证设置**：
```python
# superset_config.py
AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://ldap.example.com"
AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "password"
AUTH_LDAP_SEARCH = "dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"
```

3. **OAuth设置**：
```python
# superset_config.py
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = {
    'google': {
        'name': 'google',
        'icon': 'fa-google',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': 'your-client-id',
            'client_secret': 'your-client-secret',
            'api_base_url': 'https://www.googleapis.com/oauth2/v1/',
            'client_kwargs': {
                'scope': 'openid email profile'
            },
        }
    }
}
```

**参考文档**：
- [Superset安全文档](https://superset.apache.org/docs/security)
- [Flask-AppBuilder安全](https://flask-appbuilder.readthedocs.io/en/latest/security.html)

---

## 用户故事2：实施基于角色的访问控制(RBAC)

**标题**：配置基于角色的访问控制

**描述**：建立全面的RBAC，根据用户的角色控制他们对仪表板、数据集和功能的访问。

**验收标准**：
- 管理员角色拥有所有功能的完全访问权限
- Alpha角色可以访问所有数据源
- Gamma角色只能有限地访问特定数据集
- 可以创建自定义角色
- 已实施行级安全

**分步指南**：

1. **创建自定义角色**：
```python
# superset_config.py
CUSTOM_SECURITY_MANAGER = CustomSecurityManager

# 创建自定义安全管理器
class CustomSecurityManager(SupersetSecurityManager):
    def create_custom_roles(self):
        # 创建自定义角色
        pass
```

2. **行级安全设置**：
```python
# superset_config.py
ROW_LEVEL_SECURITY_FILTERS = {
    'region_filter': {
        'clause': 'region = "{}"'.format(g.user.region),
        'tables': ['sales_data']
    }
}
```

3. **数据库权限**：
```sql
-- 授予特定权限
GRANT SELECT ON sales_data TO gamma_role;
GRANT ALL ON superset.* TO admin_role;
```

**参考文档**：
- [Superset RBAC文档](https://superset.apache.org/docs/security)
- [行级安全指南](https://superset.apache.org/docs/security#row-level-security)

---

## 用户故事3：配置安全设置

**标题**：实施安全最佳实践

**描述**：配置安全设置，包括会话管理、CSRF保护和审计日志。

**验收标准**：
- 会话超时已配置
- CSRF保护已启用
- 审计日志处于活动状态
- 密码策略已强制执行
- 生产环境中强制使用HTTPS

**分步指南**：

1. **会话配置**：
```python
# superset_config.py
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

2. **CSRF保护**：
```python
# superset_config.py
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None
```

3. **审计日志**：
```python
# superset_config.py
ENABLE_PROXY_FIX = True
ENABLE_TEMPLATE_PROCESSING = True
```

**参考文档**：
- [Superset安全最佳实践](https://superset.apache.org/docs/security)
- [Flask安全配置](https://flask-security.readthedocs.io/en/latest/)

---

## 用户故事4：数据源安全

**标题**：保护数据源访问

**描述**：为数据源连接实施安全措施，包括连接加密和访问控制。

**验收标准**：
- 数据库连接已加密
- 连接凭证已保护
- 对敏感数据的访问受到限制
- 连接池已安全配置

**分步指南**：

1. **安全数据库连接**：
```python
# superset_config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'sslmode': 'require'
    }
}
```

2. **加密连接字符串**：
```python
# superset_config.py
ENCRYPTED_FIELD_KEY = os.environ.get('ENCRYPTED_FIELD_KEY')
```

3. **连接池安全**：
```python
# superset_config.py
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
SQLALCHEMY_POOL_TIMEOUT = 30
```

**参考文档**：
- [数据库连接安全](https://superset.apache.org/docs/security)
- [SQLAlchemy安全](https://docs.sqlalchemy.org/en/14/core/engines.html)

---

## 摘要

涵盖的关键安全概念：
- **认证方法**：数据库、LDAP、OAuth
- **授权**：RBAC、自定义角色、行级安全
- **安全设置**：会话管理、CSRF、审计日志
- **数据安全**：连接加密、凭证管理
- **最佳实践**：HTTPS、密码策略、访问控制

**下一步**：
- 测试所有认证方法
- 验证角色权限
- 查看安全日志
- 根据需要实施额外的安全措施