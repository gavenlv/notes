# 第8天：数据源连接与配置

## 用户故事1：配置多种数据库连接

**标题**：作为一名数据工程师，我希望在Superset中配置多种类型的数据库连接，以便团队能够可视化来自不同数据源的数据。

**描述**：
Superset支持连接到多种数据库系统，包括关系型数据库、NoSQL数据库和云数据仓库。正确配置这些连接对于数据可视化至关重要。

**验收标准**：
- [ ] 成功配置至少3种不同类型的数据库连接
- [ ] 所有连接都通过连接测试
- [ ] 用户能够访问并查询这些数据库中的数据
- [ ] 连接配置遵循安全最佳实践

**分步指南**：

### 1. 安装数据库驱动

在配置数据库连接前，需要安装相应的Python驱动程序：

```bash
# PostgreSQL\pip install psycopg2-binary

# MySQL\pip install mysqlclient

# SQLite (通常已内置)

# Microsoft SQL Server\pip install pyodbc

# Oracle\pip install cx_Oracle

# BigQuery
pip install google-cloud-bigquery

# Snowflake
pip install snowflake-sqlalchemy

# Redshift
pip install sqlalchemy-redshift

# Presto/Trino
pip install pyhive

# Druid
pip install pydruid
```

### 2. 通过UI配置数据库连接

1. **访问数据库配置页面**
   - 登录Superset
   - 导航至：数据 → 数据库 → + 数据库

2. **PostgreSQL连接配置**
   
   **连接字符串格式**：
   ```
   postgresql://用户名:密码@主机名:端口/数据库名
   ```
   
   **示例配置**：
   ```
   postgresql://superset:password@localhost:5432/superset_data
   ```
   
   **连接参数**：
   ```json
   {
     "engine_params": {
       "pool_size": 10,
       "max_overflow": 20
     },
     "metadata_params": {},
     "schemas_allowed_for_csv_upload": []
   }
   ```

3. **MySQL连接配置**
   
   **连接字符串格式**：
   ```
   mysql://用户名:密码@主机名:端口/数据库名
   ```
   
   **示例配置**：
   ```
   mysql://superset:password@localhost:3306/superset_data
   ```
   
   **连接参数**：
   ```json
   {
     "engine_params": {
       "pool_pre_ping": true,
       "pool_size": 10
     },
     "metadata_params": {},
     "schemas_allowed_for_csv_upload": []
   }
   ```

4. **BigQuery连接配置**
   
   **连接字符串格式**：
   ```
   bigquery://{项目ID}
   ```
   
   **示例配置**：
   ```
   bigquery://my-project-id
   ```
   
   **连接参数**：
   ```json
   {
     "engine_params": {
       "credentials_path": "/path/to/credentials.json"
     },
     "metadata_params": {},
     "schemas_allowed_for_csv_upload": []
   }
   ```

5. **Snowflake连接配置**
   
   **连接字符串格式**：
   ```
   snowflake://用户名:密码@账户名/数据库/架构?warehouse=仓库名&role=角色名
   ```
   
   **示例配置**：
   ```
   snowflake://user:password@myaccount/my_database/public?warehouse=compute_wh&role=analyst
   ```
   
   **连接参数**：
   ```json
   {
     "engine_params": {
       "connect_args": {
         "client_session_keep_alive": true
       }
     },
     "metadata_params": {},
     "schemas_allowed_for_csv_upload": []
   }
   ```

### 3. 测试连接

配置完成后，点击"测试连接"按钮验证连接是否成功。如果连接失败，请检查：
- 数据库服务是否正在运行
- 网络连接是否正常
- 用户名和密码是否正确
- 数据库权限是否适当
- 防火墙设置是否允许连接

### 4. 配置高级选项

**SQLAlchemy引擎参数**：
- `pool_size`: 连接池大小
- `max_overflow`: 最大溢出连接数
- `pool_timeout`: 连接池超时时间（秒）
- `pool_recycle`: 连接回收时间（秒）
- `pool_pre_ping`: 连接有效性检查

**示例高级配置**：
```json
{
  "engine_params": {
    "pool_size": 15,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    "pool_pre_ping": true
  },
  "metadata_params": {},
  "schemas_allowed_for_csv_upload": []
}
```

**参考文档**：
- [Superset支持的数据库](https://superset.apache.org/docs/databases/installing-database-drivers)
- [SQLAlchemy连接池配置](https://docs.sqlalchemy.org/en/14/core/pooling.html)

---

## 用户故事2：配置安全的数据库连接

**标题**：作为一名安全管理员，我希望确保所有数据库连接都是安全的，以保护敏感数据和系统安全。

**描述**：
数据库连接涉及凭据和敏感信息，需要适当的安全措施来防止未授权访问和数据泄露。

**验收标准**：
- [ ] 数据库凭据不以明文形式存储
- [ ] 连接使用TLS/SSL加密
- [ ] 数据库用户权限遵循最小权限原则
- [ ] 敏感连接信息通过环境变量或密钥管理系统配置
- [ ] 连接日志记录已启用

**分步指南**：

### 1. 使用环境变量存储凭据

避免在配置文件中硬编码敏感信息，使用环境变量：

```python
# 在superset_config.py中
import os

# 从环境变量获取数据库URL
DATABASE_CONNECTIONS = {
    'postgresql': os.environ.get('POSTGRES_CONNECTION_STRING'),
    'mysql': os.environ.get('MYSQL_CONNECTION_STRING'),
    'snowflake': os.environ.get('SNOWFLAKE_CONNECTION_STRING')
}
```

### 2. 配置SSL/TLS加密连接

**PostgreSQL SSL配置**：
```python
# 在superset_config.py中
POSTGRES_CONNECTION_ARGS = {
    'sslmode': 'require',  # 可选: disable, allow, prefer, require, verify-ca, verify-full
    'sslrootcert': '/path/to/ca-cert.pem',  # 用于verify-ca或verify-full模式
    'sslcert': '/path/to/client-cert.pem',  # 客户端证书
    'sslkey': '/path/to/client-key.pem'  # 客户端密钥
}
```

**MySQL SSL配置**：
```python
# 在superset_config.py中
MYSQL_CONNECTION_ARGS = {
    'ssl': {
        'ca': '/path/to/ca-cert.pem',
        'cert': '/path/to/client-cert.pem',
        'key': '/path/to/client-key.pem'
    }
}
```

### 3. 实施最小权限原则

为Superset创建专用数据库用户，仅授予必要的权限：

**PostgreSQL示例**：
```sql
-- 创建专用用户
CREATE USER superset_user WITH PASSWORD 'secure_password';

-- 授予只读权限
GRANT CONNECT ON DATABASE analytics_db TO superset_user;
GRANT USAGE ON SCHEMA public TO superset_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO superset_user;

-- 确保对未来创建的表也有权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_user;
```

**MySQL示例**：
```sql
-- 创建专用用户并限制主机
CREATE USER 'superset_user'@'%' IDENTIFIED BY 'secure_password';

-- 授予只读权限
GRANT SELECT ON analytics_db.* TO 'superset_user'@'%';
FLUSH PRIVILEGES;
```

### 4. 使用密钥管理系统

对于生产环境，建议使用AWS Secrets Manager、HashiCorp Vault等密钥管理系统：

```python
# 使用AWS Secrets Manager的示例
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-west-2'
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        return get_secret_value_response['SecretString']
    except ClientError as e:
        raise e

# 在superset_config.py中使用
import json
db_credentials = json.loads(get_secret("superset/database/credentials"))
SQLALCHEMY_DATABASE_URI = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['dbname']}"
```

### 5. 启用连接日志

**在superset_config.py中配置日志**：
```python
# 增强数据库连接日志记录
import logging

# 设置SQLAlchemy日志级别
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 配置日志格式
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
LOG_LEVEL = 'INFO'

# 数据库特定日志配置
DB_LOGGER = logging.getLogger('superset.db')
DB_LOGGER.setLevel(logging.INFO)
```

**参考文档**：
- [Superset安全最佳实践](https://superset.apache.org/docs/security/)
- [AWS Secrets Manager文档](https://docs.aws.amazon.com/secretsmanager/)
- [PostgreSQL SSL文档](https://www.postgresql.org/docs/current/libpq-ssl.html)

---

## 用户故事3：优化数据库连接性能

**标题**：作为一名性能工程师，我希望优化Superset的数据库连接配置，以提高查询性能和用户体验。

**描述**：
数据库连接性能直接影响Superset的响应速度和用户体验。合理配置连接池和相关参数可以显著提升性能。

**验收标准**：
- [ ] 连接池已优化配置
- [ ] 查询响应时间有所改善
- [ ] 数据库连接错误减少
- [ ] 资源利用率得到优化
- [ ] 高负载下系统保持稳定

**分步指南**：

### 1. 优化连接池配置

**在superset_config.py中配置连接池**：
```python
# 连接池通用配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,               # 核心连接池大小
    'max_overflow': 30,            # 最大溢出连接数
    'pool_timeout': 30,            # 获取连接的超时时间（秒）
    'pool_recycle': 1800,          # 连接回收时间（秒），防止连接过期
    'pool_pre_ping': True,         # 连接有效性检查
    'pool_reset_on_return': 'rollback',  # 连接返回池时重置事务
    'echo': False,                 # 生产环境设为False
    'echo_pool': False             # 生产环境设为False
}
```

### 2. 针对特定数据库的优化

**PostgreSQL优化**：
```python
# PostgreSQL特定优化
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'pool_pre_ping': True,
    'connect_args': {
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
}
```

**Snowflake优化**：
```python
# Snowflake特定优化
SNOWFLAKE_ENGINE_OPTIONS = {
    'connect_args': {
        'client_session_keep_alive': True,
        'ocsp_response_cache_filename': '/tmp/ocsp_response_cache',
        'warehouse': 'COMPUTE_WH',
        'role': 'ANALYST_ROLE'
    }
}
```

### 3. 配置查询超时

**在superset_config.py中设置查询超时**：
```python
# 设置查询超时时间（秒）
SQLLAB_TIMEOUT = 300  # SQL Lab查询超时时间
SQLLAB_ASYNC_TIME_LIMIT_SEC = 600  # 异步查询超时时间
DEFAULT_SQLLAB_LIMIT = 10000  # 默认返回行数限制
```

### 4. 启用查询缓存

**配置Redis缓存**：
```python
# 缓存配置
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_'
}

# 数据查询缓存
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://localhost:6379/1',
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1小时
    'CACHE_KEY_PREFIX': 'superset_data_'
}

# 查询结果缓存
RESULTS_BACKEND = RedisCache(
    host='localhost',
    port=6379,
    db=2,
    default_timeout=3600
)
```

### 5. 监控和调整连接

**设置监控指标**：
```python
# 启用Prometheus指标
ENABLE_PROGRESS_BAR = True
ENABLE_JAVASCRIPT_CONTROLS = True
```

**性能监控查询**：

**PostgreSQL连接监控**：
```sql
-- 查看当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 按状态查看连接
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- 查看活跃查询
SELECT pid, usename, query_start, state, query 
FROM pg_stat_activity 
WHERE state = 'active';
```

**参考文档**：
- [Superset性能优化](https://superset.apache.org/docs/installation/performance-tuning)
- [SQLAlchemy连接池文档](https://docs.sqlalchemy.org/en/14/core/pooling.html)
- [PostgreSQL连接管理](https://www.postgresql.org/docs/current/runtime-config-connection.html)

---

## 用户故事4：配置数据上传和虚拟数据集

**标题**：作为一名数据分析师，我希望能够上传CSV文件并创建虚拟数据集，以便快速分析临时数据。

**描述**：
除了连接到现有数据库外，Superset还允许用户上传数据文件并创建基于SQL的虚拟数据集，以满足临时分析需求。

**验收标准**：
- [ ] 数据上传功能已正确配置
- [ ] 能够成功上传CSV/Excel文件
- [ ] 能够创建和查询虚拟数据集
- [ ] 上传的数据已正确映射和类型识别
- [ ] 数据上传权限已适当设置

**分步指南**：

### 1. 配置数据上传功能

**在superset_config.py中启用数据上传**：
```python
# 启用数据上传
ENABLE_CSV_DIRECT_UPLAOD = True

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}

# 上传文件大小限制（字节）
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# 配置上传目录
UPLOAD_FOLDER = '/path/to/uploads'

# 允许上传到的数据库连接
CSV_TO_SQLLITE = True
```

### 2. 配置支持上传的数据库

**PostgreSQL配置**：
1. 在数据库编辑页面，找到"高级"部分
2. 在"额外"JSON字段中添加：
```json
{
  "metadata_params": {},
  "engine_params": {},
  "schemas_allowed_for_csv_upload": ["public", "uploads"]
}
```

### 3. 创建上传专用架构

**PostgreSQL示例**：
```sql
-- 创建上传专用架构
CREATE SCHEMA uploads;

-- 授予权限
GRANT USAGE ON SCHEMA uploads TO superset_user;
GRANT CREATE ON SCHEMA uploads TO superset_user;
GRANT ALL ON ALL TABLES IN SCHEMA uploads TO superset_user;
```

### 4. 上传数据文件

1. **访问数据上传页面**
   - 导航至：数据 → 上传数据

2. **上传CSV文件**
   - 选择目标数据库和架构
   - 上传CSV文件
   - 配置表名和列映射
   - 点击"保存"

3. **列类型配置**
   - 自动检测：Superset会尝试自动识别数据类型
   - 手动设置：为每列选择适当的数据类型
   - 日期格式：设置日期字段的格式

### 5. 创建虚拟数据集

1. **通过SQL Lab创建**
   - 导航至：SQL Lab → SQL编辑器
   - 编写SQL查询（例如联合多个表）
   - 运行查询验证结果
   - 点击"保存数据集"

2. **配置虚拟数据集**
   - 设置数据集名称
   - 选择所有者
   - 配置列元数据
   - 保存数据集

**示例虚拟数据集SQL**：
```sql
-- 创建销售和客户数据的虚拟数据集
SELECT 
    s.order_id,
    s.order_date,
    s.product_id,
    s.quantity,
    s.amount,
    c.customer_name,
    c.customer_segment,
    c.region
FROM sales_data s
JOIN customer_data c ON s.customer_id = c.customer_id
WHERE s.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
```

**参考文档**：
- [Superset数据上传](https://superset.apache.org/docs/using-superset/exploring-data/creating-charts-datasets/uploading-csvs)
- [虚拟数据集创建](https://superset.apache.org/docs/using-superset/sql-lab)

---

## 用户故事5：配置数据库访问控制

**标题**：作为一名系统管理员，我希望能够控制不同用户对数据库的访问权限，以确保数据安全性和合规性。

**描述**：
在多用户环境中，需要精细控制用户对不同数据库、模式和表的访问权限，以保护敏感数据并满足合规要求。

**验收标准**：
- [ ] 已创建数据库访问角色
- [ ] 用户已分配适当的数据库访问权限
- [ ] 行级安全性已配置
- [ ] 权限设置已生效并经过测试
- [ ] 权限变更已记录

**分步指南**：

### 1. 创建数据库访问角色

1. **访问角色管理页面**
   - 导航至：安全 → 角色列表 → + 角色

2. **创建数据库特定角色**
   - 角色名称：例如 `analytics_read_only`
   - 添加权限：
     - `database_access`
     - `schema_access`
     - `table_access`

### 2. 配置数据库级别的权限

**在数据库编辑页面设置权限**：

1. 导航至：数据 → 数据库
2. 编辑目标数据库
3. 在"高级"部分设置权限

**Row Level Security配置**：
```json
{
  "metadata_params": {},
  "engine_params": {},
  "row_level_security": [
    {
      "clause": "department = 'sales'",
      "schema": "public",
      "table": "sales_data",
      "roles": ["sales_team"]
    },
    {
      "clause": "department = 'marketing'",
      "schema": "public",
      "table": "marketing_data",
      "roles": ["marketing_team"]
    }
  ]
}
```

### 3. 配置模式级别的权限

**为模式创建权限**：
1. 导航至：安全 → 权限列表 → + 权限
2. 创建新权限：
   - 权限名称：`schema_access_on_public`
   - 权限视图：选择对应的模式
   - 权限类型：`schema_access`

### 4. 配置表级别的权限

**使用SQLAlchemy访问控制**：
```python
# 在superset_config.py中
from superset.security import SupersetSecurityManager

class CustomSecurityManager(SupersetSecurityManager):
    def get_schema_perm(self, database, schema):
        """获取模式权限"""
        return f"[{database}]\.{schema}*"
    
    def get_table_perm(self, database, schema, table):
        """获取表权限"""
        return f"[{database}]\.{schema}\.{table}"

# 使用自定义安全管理器
CUSTOM_SECURITY_MANAGER = CustomSecurityManager
```

### 5. 行级安全性配置示例

**PostgreSQL行级安全策略**：
```sql
-- 为sales表启用行级安全性
ALTER TABLE sales_data ENABLE ROW LEVEL SECURITY;

-- 创建策略：销售人员只能看到自己部门的数据
CREATE POLICY sales_team_policy ON sales_data
    FOR ALL
    TO superset_sales_user
    USING (department = 'sales');

-- 创建策略：市场人员只能看到自己部门的数据
CREATE POLICY marketing_team_policy ON marketing_data
    FOR ALL
    TO superset_marketing_user
    USING (department = 'marketing');
```

### 6. 权限分配与测试

1. **为用户分配角色**
   - 导航至：安全 → 用户列表
   - 编辑用户
   - 在"角色"部分添加适当的角色

2. **测试权限设置**
   - 使用不同角色的用户登录
   - 验证他们只能访问被授权的数据
   - 检查行级安全性是否正常工作

**参考文档**：
- [Superset安全文档](https://superset.apache.org/docs/security/)
- [数据库角色与权限](https://superset.apache.org/docs/security/roles)
- [PostgreSQL行级安全性](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

## 参考资料

### 官方文档
- [Superset数据库连接](https://superset.apache.org/docs/databases/)
- [数据库驱动安装](https://superset.apache.org/docs/databases/installing-database-drivers)
- [安全最佳实践](https://superset.apache.org/docs/security/)

### 数据库特定文档
- [PostgreSQL连接字符串](https://www.postgresql.org/docs/current/libpq-connect.html)
- [MySQL连接参数](https://dev.mysql.com/doc/refman/8.0/en/connection-parameters.html)
- [Snowflake SQLAlchemy连接器](https://docs.snowflake.com/en/user-guide/sqlalchemy)

### 性能优化
- [SQLAlchemy性能调优](https://docs.sqlalchemy.org/en/14/core/performance.html)
- [连接池管理](https://docs.sqlalchemy.org/en/14/core/pooling.html)

## 总结

本章节详细介绍了Superset中的数据源连接配置，包括：

1. **多种数据库连接配置**：支持PostgreSQL、MySQL、BigQuery、Snowflake等多种数据库系统
2. **安全连接配置**：使用环境变量存储凭据、配置SSL/TLS加密、实施最小权限原则
3. **性能优化**：连接池配置、查询超时设置、缓存启用等
4. **数据上传功能**：CSV文件上传、虚拟数据集创建
5. **访问控制**：角色管理、数据库/模式/表级别权限、行级安全性

正确配置数据源连接是Superset有效运行的基础。通过实施本章节介绍的最佳实践，您可以确保：
- 数据访问的安全性和合规性
- 系统在高负载下的稳定性和性能
- 用户能够方便地访问和分析所需的数据
- 敏感数据得到适当保护

在配置生产环境时，建议从安全和性能两个方面综合考虑，根据实际需求调整连接参数，并定期审查和更新配置，以适应不断变化的业务需求。

**下一步学习**：
- [第9天：高级功能配置](./day09-advanced-features.md)