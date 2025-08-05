# Day 4: Security & Permissions

## User Story 1: Configure Authentication Methods

**Title**: Configure Multiple Authentication Methods

**Description**: Set up various authentication methods including database, LDAP, and OAuth to provide flexible user access to Superset.

**Acceptance Criteria**:
- Database authentication is configured and working
- LDAP authentication is set up (optional)
- OAuth integration is configured (optional)
- Users can log in using configured methods
- Failed login attempts are logged

**Step-by-Step Guide**:

1. **Database Authentication Setup**:
```python
# superset_config.py
AUTH_TYPE = AUTH_DB
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Gamma"
```

2. **LDAP Authentication Setup**:
```python
# superset_config.py
AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://ldap.example.com"
AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "password"
AUTH_LDAP_SEARCH = "dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"
```

3. **OAuth Setup**:
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

**Reference Documents**:
- [Superset Security Documentation](https://superset.apache.org/docs/security)
- [Flask-AppBuilder Security](https://flask-appbuilder.readthedocs.io/en/latest/security.html)

---

## User Story 2: Implement Role-Based Access Control (RBAC)

**Title**: Configure Role-Based Access Control

**Description**: Set up comprehensive RBAC to control user access to dashboards, datasets, and features based on their roles.

**Acceptance Criteria**:
- Admin role has full access to all features
- Alpha role can access all data sources
- Gamma role has limited access to specific datasets
- Custom roles can be created
- Row-level security is implemented

**Step-by-Step Guide**:

1. **Create Custom Roles**:
```python
# superset_config.py
CUSTOM_SECURITY_MANAGER = CustomSecurityManager

# Create custom security manager
class CustomSecurityManager(SupersetSecurityManager):
    def create_custom_roles(self):
        # Create custom roles
        pass
```

2. **Row-Level Security Setup**:
```python
# superset_config.py
ROW_LEVEL_SECURITY_FILTERS = {
    'region_filter': {
        'clause': 'region = "{}"'.format(g.user.region),
        'tables': ['sales_data']
    }
}
```

3. **Database Permissions**:
```sql
-- Grant specific permissions
GRANT SELECT ON sales_data TO gamma_role;
GRANT ALL ON superset.* TO admin_role;
```

**Reference Documents**:
- [Superset RBAC Documentation](https://superset.apache.org/docs/security)
- [Row-Level Security Guide](https://superset.apache.org/docs/security#row-level-security)

---

## User Story 3: Configure Security Settings

**Title**: Implement Security Best Practices

**Description**: Configure security settings including session management, CSRF protection, and audit logging.

**Acceptance Criteria**:
- Session timeout is configured
- CSRF protection is enabled
- Audit logging is active
- Password policies are enforced
- HTTPS is enforced in production

**Step-by-Step Guide**:

1. **Session Configuration**:
```python
# superset_config.py
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

2. **CSRF Protection**:
```python
# superset_config.py
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None
```

3. **Audit Logging**:
```python
# superset_config.py
ENABLE_PROXY_FIX = True
ENABLE_TEMPLATE_PROCESSING = True
```

**Reference Documents**:
- [Superset Security Best Practices](https://superset.apache.org/docs/security)
- [Flask Security Configuration](https://flask-security.readthedocs.io/en/latest/)

---

## User Story 4: Data Source Security

**Title**: Secure Data Source Access

**Description**: Implement security measures for data source connections including connection encryption and access controls.

**Acceptance Criteria**:
- Database connections are encrypted
- Connection credentials are secured
- Access to sensitive data is restricted
- Connection pooling is configured securely

**Step-by-Step Guide**:

1. **Secure Database Connections**:
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

2. **Encrypt Connection Strings**:
```python
# superset_config.py
ENCRYPTED_FIELD_KEY = os.environ.get('ENCRYPTED_FIELD_KEY')
```

3. **Connection Pool Security**:
```python
# superset_config.py
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
SQLALCHEMY_POOL_TIMEOUT = 30
```

**Reference Documents**:
- [Database Connection Security](https://superset.apache.org/docs/security)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/core/engines.html)

---

## Summary

Key security concepts covered:
- **Authentication Methods**: Database, LDAP, OAuth
- **Authorization**: RBAC, custom roles, row-level security
- **Security Settings**: Session management, CSRF, audit logging
- **Data Security**: Connection encryption, credential management
- **Best Practices**: HTTPS, password policies, access controls

**Next Steps**:
- Test all authentication methods
- Verify role permissions
- Review security logs
- Implement additional security measures as needed 