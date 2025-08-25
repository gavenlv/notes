# Day 3: Configuration & Administration

## User Story 1: Configure Basic Superset Settings

**Title**: As a system administrator, I want to configure basic Superset settings through superset_config.py so that the application behaves according to our organization's requirements.

**Description**: 
The superset_config.py file is the primary configuration file for Apache Superset. It controls database connections, security settings, caching, and other core functionality.

**Acceptance Criteria**:
- [ ] superset_config.py file is created and loaded
- [ ] Database connection is properly configured
- [ ] Security settings are applied
- [ ] Application starts without errors
- [ ] Configuration changes take effect

**Step-by-Step Guide**:

1. **Create Configuration File**
   ```bash
   touch superset_config.py
   ```

2. **Basic Configuration Template**
   ```python
   # superset_config.py
   import os
   
   # Database Configuration
   SQLALCHEMY_DATABASE_URI = os.environ.get(
       'SQLALCHEMY_DATABASE_URI',
       'sqlite:////path/to/superset.db'
   )
   
   # Secret Key for Security
   SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
   
   # Cache Configuration
   CACHE_CONFIG = {
       'CACHE_TYPE': 'simple',
       'CACHE_DEFAULT_TIMEOUT': 300,
       'CACHE_KEY_PREFIX': 'superset_',
   }
   
   # Feature Flags
   FEATURE_FLAGS = {
       'ENABLE_TEMPLATE_PROCESSING': True,
       'DASHBOARD_NATIVE_FILTERS': True,
   }
   ```

3. **Set Environment Variable**
   ```bash
   export SUPERSET_CONFIG_PATH=/path/to/superset_config.py
   ```

**Reference Documents**:
- [Official Configuration Guide](https://superset.apache.org/docs/installation/configuring-superset)
- [Configuration Reference](https://superset.apache.org/docs/installation/configuring-superset#configuration)

---

## User Story 2: Configure Database Connections

**Title**: As a database administrator, I want to configure multiple database connections in Superset so that users can access different data sources for their dashboards.

**Description**: 
Superset supports connections to various databases including PostgreSQL, MySQL, BigQuery, Snowflake, and many others.

**Acceptance Criteria**:
- [ ] Database connections are configured securely
- [ ] Connection parameters are properly set
- [ ] Test connections work successfully
- [ ] Users can access configured databases

**Step-by-Step Guide**:

1. **Install Database Drivers**
   ```bash
   pip install psycopg2-binary mysqlclient pyodbc
   ```

2. **Configure Database URLs**
   ```python
   # In superset_config.py
   
   # PostgreSQL
   POSTGRES_DB_URI = "postgresql://user:password@localhost:5432/database"
   
   # MySQL
   MYSQL_DB_URI = "mysql://user:password@localhost:3306/database"
   ```

3. **Add Database Connections via UI**
   - Navigate to Data → Databases → + Database
   - Enter connection string
   - Test connection
   - Save

**Reference Documents**:
- [Database Connections](https://superset.apache.org/docs/installation/configuring-superset#database)
- [Supported Databases](https://superset.apache.org/docs/installation/databases)

---

## User Story 3: Configure Security and Authentication

**Title**: As a security administrator, I want to configure authentication and authorization in Superset so that only authorized users can access the system.

**Description**: 
Superset provides multiple authentication backends and role-based access control (RBAC) to secure the application.

**Acceptance Criteria**:
- [ ] Authentication backend is configured
- [ ] User roles and permissions are set up
- [ ] Row-level security is implemented
- [ ] Security policies are enforced

**Step-by-Step Guide**:

1. **Configure Authentication Backend**
   ```python
   # In superset_config.py
   
   # LDAP Authentication
   AUTH_TYPE = AUTH_LDAP
   AUTH_LDAP_SERVER = "ldap://ldap.example.com"
   AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
   AUTH_LDAP_BIND_PASSWORD = "password"
   AUTH_LDAP_SEARCH = "dc=example,dc=com"
   AUTH_LDAP_UID_FIELD = "uid"
   ```

2. **Configure Row-Level Security**
   ```python
   # Row-level security
   ROW_LEVEL_SECURITY_FILTERS = {
       'user_id_filter': {
           'filter_type': 'Base',
           'clause': 'user_id = {{ current_user_id() }}',
       }
   }
   ```

3. **Set Up User Roles**
   ```bash
   superset fab create-role --name "Analyst" --permissions "all_datasource_access"
   superset fab create-role --name "Viewer" --permissions "all_dashboard_access"
   ```

**Reference Documents**:
- [Security Configuration](https://superset.apache.org/docs/installation/configuring-superset#security)
- [Authentication](https://superset.apache.org/docs/installation/configuring-superset#authentication)

---

## User Story 4: Configure Caching and Performance

**Title**: As a performance engineer, I want to configure caching and performance optimizations in Superset so that dashboards load quickly.

**Description**: 
Proper caching configuration significantly improves Superset performance by caching query results and session data.

**Acceptance Criteria**:
- [ ] Redis caching is configured
- [ ] Query result caching is working
- [ ] Performance metrics show improvement
- [ ] System handles concurrent users

**Step-by-Step Guide**:

1. **Configure Redis Caching**
   ```python
   # In superset_config.py
   
   import redis
   
   CACHE_CONFIG = {
       'CACHE_TYPE': 'redis',
       'CACHE_DEFAULT_TIMEOUT': 300,
       'CACHE_KEY_PREFIX': 'superset_',
       'CACHE_REDIS_HOST': 'localhost',
       'CACHE_REDIS_PORT': 6379,
       'CACHE_REDIS_DB': 1,
   }
   
   SESSION_TYPE = 'redis'
   SESSION_REDIS = redis.from_url('redis://localhost:6379/2')
   ```

2. **Configure Celery for Async Tasks**
   ```python
   CELERY_CONFIG = {
       'broker_url': 'redis://localhost:6379/0',
       'result_backend': 'redis://localhost:6379/0',
   }
   ```

**Reference Documents**:
- [Caching Configuration](https://superset.apache.org/docs/installation/configuring-superset#caching)
- [Performance Tuning](https://superset.apache.org/docs/installation/running-on-production)

---

## Configuration Best Practices

### 1. Environment-Specific Configuration
```python
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///superset.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
```

### 2. Security Hardening
```python
WTF_CSRF_ENABLED = True
SESSION_COOKIE_SECURE = True  # In production
SESSION_COOKIE_HTTPONLY = True
```

### 3. Performance Optimization
```python
SQL_MAX_ROW = 100000
SUPERSET_WEBSERVER_TIMEOUT = 60
SUPERSET_WEBSERVER_WORKERS = 4
```

## Next Steps

After completing the configuration, proceed to:
- [Day 4: Security & Permissions](../day4-security/security.md)
- [Day 5: Building Dashboards](../day5-dashboards/dashboards.md)