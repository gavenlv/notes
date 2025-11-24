# Day 9: 连接与密钥管理 - 学习资料

## 核心概念

### 连接管理

#### 什么是连接？
在Airflow中，连接是一种安全存储外部系统认证信息和其他配置参数的机制。连接信息包括主机名、端口、登录凭据、额外参数等。

#### 连接类型
Airflow支持多种预定义的连接类型：
- **数据库连接**：Postgres, MySQL, SQLite, Oracle, MSSQL等
- **云服务连接**：AWS, GCP, Azure, Snowflake等
- **消息队列连接**：Redis, RabbitMQ, Kafka等
- **API连接**：HTTP, FTP, SFTP等
- **其他连接**：SSH, Docker, Kubernetes等

#### 连接参数
每个连接包含以下核心参数：
- **Conn Id**：连接的唯一标识符
- **Conn Type**：连接类型
- **Host**：主机地址
- **Schema**：数据库模式或协议
- **Login**：用户名
- **Password**：密码
- **Port**：端口号
- **Extra**：额外的JSON格式参数

### 密钥管理

#### 敏感信息处理
Airflow提供了多种方式来安全地处理敏感信息：
- **连接加密**：数据库中的连接密码会被加密存储
- **环境变量**：通过环境变量传递敏感信息
- **密钥后端**：使用外部密钥管理系统
- **变量加密**：Airflow变量支持加密存储

#### 密钥后端
Airflow支持多种密钥后端：
- **AWS Secrets Manager**
- **Google Secret Manager**
- **Azure Key Vault**
- **Hashicorp Vault**

## 实践指南

### 1. 创建和管理连接

#### 通过UI创建连接
1. 访问Airflow Web UI
2. 进入Admin > Connections
3. 点击"+"号创建新连接
4. 填写连接信息
5. 保存连接

#### 通过CLI创建连接
```bash
# 创建连接
airflow connections add 'my_postgres_conn' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-port '5432' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-schema 'airflow'

# 列出所有连接
airflow connections list

# 获取连接信息
airflow connections get 'my_postgres_conn'

# 删除连接
airflow connections delete 'my_postgres_conn'
```

#### 通过代码创建连接
```python
from airflow.models import Connection
from airflow.utils.session import create_session

def create_connection():
    new_conn = Connection(
        conn_id='my_postgres_conn',
        conn_type='postgres',
        host='localhost',
        port=5432,
        login='airflow',
        password='airflow',
        schema='airflow'
    )
    
    with create_session() as session:
        session.add(new_conn)
        session.commit()
```

### 2. 使用连接

#### 在Hook中使用连接
```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

def use_connection_example(**context):
    # 使用连接ID创建Hook
    postgres_hook = PostgresHook(postgres_conn_id='my_postgres_conn')
    
    # 执行SQL查询
    sql = "SELECT COUNT(*) FROM users"
    result = postgres_hook.get_first(sql)
    
    print(f"用户总数: {result[0]}")
```

#### 在Operator中使用连接
```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

# 在DAG中使用
postgres_task = PostgresOperator(
    task_id='query_users',
    postgres_conn_id='my_postgres_conn',
    sql='SELECT COUNT(*) FROM users',
    dag=dag
)
```

### 3. 环境变量管理

#### 设置环境变量
```bash
# Linux/Mac
export AIRFLOW_CONN_MY_POSTGRES_CONN='postgresql://airflow:airflow@localhost:5432/airflow'

# Windows PowerShell
$env:AIRFLOW_CONN_MY_POSTGRES_CONN="postgresql://airflow:airflow@localhost:5432/airflow"
```

#### 在Docker中使用环境变量
```yaml
# docker-compose.yml
version: '3'
services:
  airflow:
    image: apache/airflow:2.7.0
    environment:
      - AIRFLOW_CONN_MY_POSTGRES_CONN=postgresql://airflow:airflow@postgres:5432/airflow
    # ... 其他配置
```

### 4. 密钥后端配置

#### AWS Secrets Manager
```python
# airflow.cfg
[secrets]
backend = airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend
backend_kwargs = {"connections_prefix": "airflow/connections", "variables_prefix": "airflow/variables"}
```

#### Google Secret Manager
```python
# airflow.cfg
[secrets]
backend = airflow.providers.google.cloud.secrets.secret_manager.CloudSecretManagerBackend
backend_kwargs = {"connections_prefix": "airflow-connections", "variables_prefix": "airflow-variables"}
```

## 安全最佳实践

### 1. 连接安全
- 不要在代码中硬编码敏感信息
- 使用连接加密功能
- 定期轮换密码和密钥
- 限制连接的权限范围
- 定期审计连接使用情况

### 2. 环境变量安全
- 不要将敏感信息提交到版本控制系统
- 使用.env文件管理环境变量
- 在生产环境中使用密钥管理服务
- 限制环境变量的访问权限

### 3. 权限管理
- 遵循最小权限原则
- 为不同的连接设置不同的用户权限
- 定期审查和更新权限配置
- 使用角色基础的访问控制(RBAC)

### 4. 监控和审计
- 启用详细的日志记录
- 监控连接使用情况
- 定期审查安全日志
- 设置异常访问告警

## 常见问题和解决方案

### 问题1：连接测试失败
**可能原因**：
- 网络连接问题
- 认证信息错误
- 防火墙或安全组限制

**解决方案**：
```python
# 测试连接的诊断代码
def diagnose_connection(conn_id):
    from airflow.hooks.base import BaseHook
    
    try:
        # 获取连接
        conn = BaseHook.get_connection(conn_id)
        print(f"连接信息: {conn.host}:{conn.port}")
        
        # 根据连接类型进行测试
        if conn.conn_type == 'postgres':
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            hook = PostgresHook(postgres_conn_id=conn_id)
            hook.get_conn()
            print("连接成功!")
        # 其他连接类型的测试...
        
    except Exception as e:
        print(f"连接失败: {e}")
```

### 问题2：密钥泄露
**预防措施**：
- 使用密钥后端而不是环境变量
- 定期轮换密钥
- 启用审计日志
- 限制访问权限

### 问题3：权限不足
**解决方案**：
```python
# 权限检查代码示例
def check_connection_permissions(conn_id):
    from airflow.hooks.base import BaseHook
    
    try:
        conn = BaseHook.get_connection(conn_id)
        # 根据连接类型检查权限
        if conn.conn_type == 'postgres':
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            hook = PostgresHook(postgres_conn_id=conn_id)
            # 尝试执行需要权限的操作
            hook.run("SELECT current_user;")
            print("权限检查通过")
    except Exception as e:
        print(f"权限检查失败: {e}")
```

## 参考资料

1. [Airflow官方文档 - Connections](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html)
2. [Airflow官方文档 - Secrets Backends](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/index.html)
3. [Airflow Providers Documentation](https://airflow.apache.org/docs/)
4. [Security Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/security/index.html)