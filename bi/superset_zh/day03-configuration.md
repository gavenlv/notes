# 第三天：配置与管理

## 用户故事1：配置基本的Superset设置

**标题**：作为一名系统管理员，我希望通过superset_config.py配置基本的Superset设置，以便应用程序按照我们组织的要求运行。

**描述**：
superset_config.py文件是Apache Superset的主要配置文件。它控制数据库连接、安全设置、缓存和其他核心功能。

**验收标准**：
- [ ] superset_config.py文件已创建并加载
- [ ] 数据库连接已正确配置
- [ ] 安全设置已应用
- [ ] 应用程序启动时没有错误
- [ ] 配置更改生效

**分步指南**：

1. **创建配置文件**
   ```bash
   touch superset_config.py
   ```

2. **基本配置模板**
   ```python
   # superset_config.py
   import os
   
   # 数据库配置
   SQLALCHEMY_DATABASE_URI = os.environ.get(
       'SQLALCHEMY_DATABASE_URI',
       'sqlite:////path/to/superset.db'
   )
   
   # 安全密钥
   SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
   
   # 缓存配置
   CACHE_CONFIG = {
       'CACHE_TYPE': 'simple',
       'CACHE_DEFAULT_TIMEOUT': 300,
       'CACHE_KEY_PREFIX': 'superset_',
   }
   
   # 功能标志
   FEATURE_FLAGS = {
       'ENABLE_TEMPLATE_PROCESSING': True,
       'DASHBOARD_NATIVE_FILTERS': True,
   }
   ```

3. **设置环境变量**
   ```bash
   export SUPERSET_CONFIG_PATH=/path/to/superset_config.py
   ```

**参考文档**：
- [官方配置指南](https://superset.apache.org/docs/installation/configuring-superset)
- [配置参考](https://superset.apache.org/docs/installation/configuring-superset#configuration)

---

## 用户故事2：配置数据库连接

**标题**：作为一名数据库管理员，我希望在Superset中配置多个数据库连接，以便用户可以访问不同的数据源来创建他们的仪表板。

**描述**：
Superset支持连接到各种数据库，包括PostgreSQL、MySQL、BigQuery、Snowflake等。

**验收标准**：
- [ ] 数据库连接已安全配置
- [ ] 连接参数已正确设置
- [ ] 测试连接成功
- [ ] 用户可以访问已配置的数据库

**分步指南**：

1. **安装数据库驱动**
   ```bash
   pip install psycopg2-binary mysqlclient pyodbc
   ```

2. **配置数据库URL**
   ```python
   # 在superset_config.py中
   
   # PostgreSQL
   POSTGRES_DB_URI = "postgresql://user:password@localhost:5432/database"
   
   # MySQL
   MYSQL_DB_URI = "mysql://user:password@localhost:3306/database"
   ```

3. **通过UI添加数据库连接**
   - 导航到数据→数据库→+数据库
   - 输入连接字符串
   - 测试连接
   - 保存

**参考文档**：
- [数据库连接](https://superset.apache.org/docs/installation/configuring-superset#database)
- [支持的数据库](https://superset.apache.org/docs/installation/databases)

---

## 用户故事3：配置安全和认证

**标题**：作为一名安全管理员，我希望在Superset中配置认证和授权，以便只有授权用户才能访问系统。

**描述**：
Superset提供了多种认证后端和基于角色的访问控制(RBAC)来保护应用程序。

**验收标准**：
- [ ] 认证后端已配置
- [ ] 用户角色和权限已设置
- [ ] 行级安全已实施
- [ ] 安全策略已强制执行

**分步指南**：

1. **配置认证后端**
   ```python
   # 在superset_config.py中
   
   # LDAP认证
   AUTH_TYPE = AUTH_LDAP
   AUTH_LDAP_SERVER = "ldap://ldap.example.com"
   AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
   AUTH_LDAP_BIND_PASSWORD = "password"
   AUTH_LDAP_SEARCH = "dc=example,dc=com"
   AUTH_LDAP_UID_FIELD = "uid"
   ```

2. **配置行级安全**
   ```python
   # 行级安全
   ROW_LEVEL_SECURITY_FILTERS = {
       'user_id_filter': {
           'filter_type': 'Base',
           'clause': 'user_id = {{ current_user_id() }}',
       }
   }
   ```

3. **设置用户角色**
   ```bash
   superset fab create-role --name "Analyst" --permissions "all_datasource_access"
   superset fab create-role --name "Viewer" --permissions "all_dashboard_access"
   ```

**参考文档**：
- [安全配置](https://superset.apache.org/docs/installation/configuring-superset#security)
- [认证](https://superset.apache.org/docs/installation/configuring-superset#authentication)

---

## 用户故事4：配置缓存和性能

**标题**：作为一名性能工程师，我希望在Superset中配置缓存和性能优化，以便仪表板能快速加载。

**描述**：
正确的缓存配置通过缓存查询结果和会话数据显著提高Superset性能。

**验收标准**：
- [ ] Redis缓存已配置
- [ ] 查询结果缓存正在工作
- [ ] 性能指标显示改善
- [ ] 系统能处理并发用户

**分步指南**：

1. **配置Redis缓存**
   ```python
   # 在superset_config.py中
   
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

2. **为异步任务配置Celery**
   ```python
   CELERY_CONFIG = {
       'broker_url': 'redis://localhost:6379/0',
       'result_backend': 'redis://localhost:6379/0',
   }
   ```

**参考文档**：
- [缓存配置](https://superset.apache.org/docs/installation/configuring-superset#caching)
- [性能调优](https://superset.apache.org/docs/installation/running-on-production)

---

## 配置最佳实践

### 1. 环境特定配置
```python
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///superset.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
```

### 2. 安全强化
```python
WTF_CSRF_ENABLED = True
SESSION_COOKIE_SECURE = True  # 在生产环境中
SESSION_COOKIE_HTTPONLY = True
```

### 3. 性能优化
```python
SQL_MAX_ROW = 100000
SUPERSET_WEBSERVER_TIMEOUT = 60
SUPERSET_WEBSERVER_WORKERS = 4
```

## 下一步

完成配置后，请继续：
- [第四天：安全与权限](../day4-security/security.md)
- [第五天：构建仪表板](../day5-dashboards/dashboards.md)