# Airflow 安全与权限管理 - 详细学习材料

## 1. Airflow 安全架构

### 1.1 安全组件概述

Apache Airflow 的安全架构由多个组件构成，每个组件都有其特定的安全职责：

#### Web Server 安全
Web 服务器是用户与 Airflow 交互的主要界面，需要特别注意以下安全考虑：
- 身份验证和授权
- HTTPS 加密传输
- 输入验证和 XSS 防护
- CSRF 保护
- 会话管理和超时

#### Scheduler 安全
调度器负责解析 DAG 并触发任务执行，其安全要点包括：
- 文件系统访问控制
- 数据库连接安全
- DAG 解析过程中的代码执行安全

#### Worker 安全
Worker 执行实际的任务，是最容易受到攻击的部分：
- 任务代码沙箱化
- 环境变量和密钥保护
- 网络访问限制
- 资源隔离

#### Metadata Database 安全
元数据数据库存储了所有 DAG、任务实例、连接等敏感信息：
- 数据库访问控制
- 数据传输加密
- 数据备份和恢复安全
- 审计日志记录

### 1.2 认证 vs 授权

#### 认证（Authentication）
认证是验证用户身份的过程，Airflow 支持多种认证方式：
- 用户名/密码认证（默认）
- LDAP 认证
- OAuth 认证（GitHub, Google, Azure 等）
- 自定义认证后端

#### 授权（Authorization）
授权是确定已认证用户可以访问哪些资源的过程，在 Airflow 中通过 RBAC 实现：
- 角色定义
- 权限分配
- 资源访问控制

## 2. 身份验证机制

### 2.1 默认身份验证
Airflow 默认使用基于数据库的身份验证系统：

```python
# airflow.cfg 中的相关配置
[webserver]
authenticate = True
auth_backend = airflow.contrib.auth.backends.password_auth

# 创建管理员用户
from airflow.contrib.auth.backends.password_auth import PasswordUser
from airflow import models, settings

user = PasswordUser(username='admin')
user.password = 'secure_password'
user.superuser = True
session = settings.Session()
session.add(user)
session.commit()
session.close()
```

### 2.2 LDAP 集成

LDAP 是企业环境中常用的身份验证方式，Airflow 可以与其集成：

```python
# airflow.cfg 中的 LDAP 配置
[ldap]
uri = ldap://ldap.example.com:389
user_filter = objectClass=*
user_name_attr = uid
group_member_attr = memberUid
superuser_filter = memberOf=cn=airflow_admins,ou=groups,dc=example,dc=com
data_profiler_filter = memberOf=cn=airflow_users,ou=groups,dc=example,dc=com
bind_user = cn=Manager,dc=example,dc=com
bind_password = admin_password
basedn = dc=example,dc=com
cacert = /etc/ssl/certs/ldap.crt
search_scope = LEVEL
```

```python
# 自定义 LDAP 认证后端
from airflow.contrib.auth.backends.ldap_auth import LdapUser
from flask_appbuilder.security.manager import AUTH_LDAP

# 在 webserver_config.py 中配置
AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://ldap.example.com:389"
AUTH_LDAP_BIND_USER = "cn=Manager,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "admin_password"
AUTH_LDAP_SEARCH = "dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"
```

### 2.3 OAuth 集成

OAuth 允许用户使用第三方服务进行身份验证：

```python
# webserver_config.py 中的 GitHub OAuth 配置
from flask_appbuilder.security.manager import AUTH_OAUTH

AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {
        'name': 'github',
        'whitelist': ['@company.com'],  # 可选：限制特定域的用户
        'token_key': 'access_token',
        'icon': 'fa-github',
        'remote_app': {
            'client_id': 'YOUR_GITHUB_CLIENT_ID',
            'client_secret': 'YOUR_GITHUB_CLIENT_SECRET',
            'api_base_url': 'https://api.github.com/user',
            'client_kwargs': {
                'scope': 'read:user'
            },
            'request_token_url': None,
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'authorize_url': 'https://github.com/login/oauth/authorize'
        }
    }
]
```

## 3. 角色基础访问控制（RBAC）

### 3.1 默认角色

Airflow 提供了几个默认角色，每个角色具有不同的权限：

| 角色 | 权限 |
|------|------|
| Admin | 所有权限 |
| User | DAG 编辑、任务实例查看、日志查看等 |
| Op | 任务操作、DAG 运行、连接管理等 |
| Viewer | 只读访问 |
| Public | 有限的公共访问 |

### 3.2 自定义角色创建

可以根据业务需求创建自定义角色：

```python
# 创建自定义角色的 Python 脚本
from airflow import models, settings
from airflow.www.security import AirflowSecurityManager

def create_custom_role():
    security_manager = AirflowSecurityManager()
    
    # 定义角色名称和权限
    role_name = "DataEngineer"
    permissions = [
        "can_dag_read",
        "can_dag_edit",
        "can_task_instance_read",
        "can_task_reschedule_read",
        "can_log_read"
    ]
    
    # 创建角色
    role = security_manager.find_role(role_name)
    if not role:
        role = security_manager.add_role(role_name)
    
    # 分配权限
    for perm_name in permissions:
        perm = security_manager.find_permission_view_menu(perm_name, "DAG")
        if perm:
            security_manager.add_permission_role(role, perm)
    
    print(f"Custom role '{role_name}' created successfully")

# 运行脚本
create_custom_role()
```

### 3.3 权限分配和管理

权限可以在用户级别或角色级别进行分配：

```python
# 为用户分配角色
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser

def assign_role_to_user(username, role_name):
    session = settings.Session()
    
    # 查找用户
    user = session.query(PasswordUser).filter(PasswordUser.username == username).first()
    if not user:
        print(f"User {username} not found")
        return
    
    # 查找角色
    security_manager = AirflowSecurityManager()
    role = security_manager.find_role(role_name)
    if not role:
        print(f"Role {role_name} not found")
        return
    
    # 分配角色
    if role not in user.roles:
        user.roles.append(role)
        session.commit()
        print(f"Role {role_name} assigned to user {username}")
    else:
        print(f"User {username} already has role {role_name}")

# 使用示例
assign_role_to_user("data_analyst", "Viewer")
```

## 4. 安全连接和密钥管理

### 4.1 Airflow Connections 安全使用

Connections 用于存储外部系统的连接信息，如数据库、API 等：

```python
# 安全地创建和使用 Connection
from airflow.models import Connection
from airflow import settings

def create_secure_connection():
    session = settings.Session()
    
    # 创建加密的 Connection
    conn = Connection(
        conn_id="secure_database",
        conn_type="postgres",
        host="db.example.com",
        port=5432,
        login="airflow_user",
        password="encrypted_password",  # 这会被自动加密存储
        schema="analytics",
        extra='{"sslmode": "require"}'  # 额外参数，也会被加密
    )
    
    session.add(conn)
    session.commit()
    session.close()
    
    print("Secure connection created successfully")

# 在 DAG 中使用 Connection
from airflow.providers.postgres.operators.postgres import PostgresOperator

task = PostgresOperator(
    task_id="query_data",
    postgres_conn_id="secure_database",
    sql="SELECT * FROM sensitive_table LIMIT 10;"
)
```

### 4.2 Variables 加密存储

Variables 用于存储配置值，敏感数据应启用加密：

```python
# 创建加密的 Variable
from airflow.models import Variable

# 存储普通变量
Variable.set("normal_config", "value")

# 存储加密变量
Variable.set("secret_api_key", "my_secret_key", serialize_json=False)

# 启用加密需要在 airflow.cfg 中配置
"""
[core]
fernet_key = your_fernet_key_here
"""

# 在 DAG 中使用加密变量
api_key = Variable.get("secret_api_key")  # 自动解密
```

### 4.3 外部密钥管理系统集成

#### HashiCorp Vault 集成

```python
# 配置 Vault 后端
"""
[secrets]
backend = airflow.providers.hashicorp.secrets.vault.VaultBackend
backend_kwargs = {"connections_path": "connections", "variables_path": "variables", "url": "http://vault:8200", "token": "s.7wIqpdzjJZrXQW9T5C5v6F8z"}
"""

# 在 DAG 中使用 Vault 存储的密钥
from airflow.hooks.base import BaseHook

def get_vault_connection():
    # Airflow 会自动从 Vault 获取连接信息
    conn = BaseHook.get_connection("vault_stored_connection")
    return conn
```

#### AWS Secrets Manager 集成

```python
# 配置 AWS Secrets Manager 后端
"""
[secrets]
backend = airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend
backend_kwargs = {"connections_prefix": "airflow/connections", "variables_prefix": "airflow/variables"}
"""

# 使用示例
from airflow.models import Variable

# 从 AWS Secrets Manager 获取变量
api_key = Variable.get("aws_secret_api_key")
```

## 5. 网络安全配置

### 5.1 HTTPS 配置

为 Web 服务器启用 HTTPS：

```python
# 在 airflow.cfg 中配置
"""
[webserver]
web_server_ssl_cert = /path/to/certificate.crt
web_server_ssl_key = /path/to/private.key
"""

# 使用反向代理（如 Nginx）配置 HTTPS
"""
server {
    listen 443 ssl;
    server_name airflow.example.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""
```

### 5.2 CORS 设置

配置跨域资源共享：

```python
# 在 webserver_config.py 中设置
from flask import Flask
from airflow.www.app import cached_app

app = cached_app()

# 配置 CORS
from flask_cors import CORS
CORS(app, origins=["https://trusted-domain.com"])
```

### 5.3 API 安全

保护 REST API 访问：

```python
# 在 airflow.cfg 中配置 API 认证
"""
[api]
auth_backend = airflow.api.auth.backend.basic_auth
"""

# 使用 API 密钥
import requests
from requests.auth import HTTPBasicAuth

def call_airflow_api():
    url = "http://localhost:8080/api/v1/dags"
    auth = HTTPBasicAuth('api_user', 'api_password')
    
    response = requests.get(url, auth=auth)
    return response.json()
```

## 6. 审计和监控

### 6.1 安全日志配置

配置详细的日志记录：

```python
# 在 airflow.cfg 中配置日志
"""
[logging]
base_log_folder = /var/log/airflow
remote_logging = False

# 安全日志配置
[audit]
enabled = True
log_file = /var/log/airflow/audit.log
"""

# 自定义审计日志处理器
import logging
from airflow.utils.log.logging_mixin import LoggingMixin

class AuditLogger(LoggingMixin):
    def __init__(self):
        super().__init__()
        self.audit_logger = logging.getLogger("airflow.audit")
    
    def log_access(self, user, resource, action):
        self.audit_logger.info(
            f"AUDIT: User {user} performed {action} on {resource}",
            extra={
                "user": user,
                "resource": resource,
                "action": action
            }
        )

# 使用审计日志
audit_logger = AuditLogger()
audit_logger.log_access("john_doe", "DAG:example_dag", "trigger")
```

### 6.2 用户活动跟踪

跟踪用户的重要操作：

```python
# 在 DAG 中添加用户活动跟踪
from airflow.operators.python import PythonOperator
from datetime import datetime

def track_user_activity(**context):
    user = context.get('dag_run').conf.get('user', 'unknown')
    dag_id = context['dag'].dag_id
    task_id = context['task'].task_id
    
    # 记录用户活动
    audit_logger.log_access(user, f"DAG:{dag_id}", f"execute_task:{task_id}")

track_task = PythonOperator(
    task_id='track_activity',
    python_callable=track_user_activity
)
```

### 6.3 异常行为检测

实现基本的异常行为检测：

```python
# 异常登录检测
from datetime import datetime, timedelta
from collections import defaultdict

class AnomalyDetector:
    def __init__(self):
        self.login_attempts = defaultdict(list)
        self.threshold = 5  # 5次尝试阈值
        self.time_window = timedelta(minutes=10)  # 10分钟窗口
    
    def record_login_attempt(self, user, ip_address, success=True):
        timestamp = datetime.now()
        self.login_attempts[user].append({
            'timestamp': timestamp,
            'ip_address': ip_address,
            'success': success
        })
        
        # 检查是否为异常行为
        return self._check_anomalies(user, ip_address)
    
    def _check_anomalies(self, user, ip_address):
        attempts = self.login_attempts[user]
        recent_attempts = [
            attempt for attempt in attempts 
            if datetime.now() - attempt['timestamp'] < self.time_window
        ]
        
        failed_attempts = [
            attempt for attempt in recent_attempts 
            if not attempt['success']
        ]
        
        # 如果失败次数超过阈值，标记为异常
        if len(failed_attempts) >= self.threshold:
            return True
        
        # 检查是否来自多个 IP 地址
        unique_ips = set(attempt['ip_address'] for attempt in recent_attempts)
        if len(unique_ips) > 3:
            return True
            
        return False

# 使用示例
detector = AnomalyDetector()
is_anomalous = detector.record_login_attempt("user123", "192.168.1.100", success=False)
```

## 7. 安全最佳实践

### 7.1 配置管理

```python
# 使用环境变量而不是硬编码敏感信息
import os
from airflow.models import Variable

# 推荐做法
database_password = os.environ.get('DATABASE_PASSWORD')
# 或者
database_password = Variable.get("database_password")

# 不推荐的做法
database_password = "hardcoded_password"
```

### 7.2 网络隔离

```yaml
# docker-compose.yml 中的网络隔离示例
version: '3'
services:
  webserver:
    # ... 其他配置
    networks:
      - airflow-frontend
      - airflow-backend
      
  scheduler:
    # ... 其他配置
    networks:
      - airflow-backend
      - airflow-database
      
  worker:
    # ... 其他配置
    networks:
      - airflow-backend
      
  redis:
    # ... 其他配置
    networks:
      - airflow-backend
      
  postgres:
    # ... 其他配置
    networks:
      - airflow-database

networks:
  airflow-frontend:
    driver: bridge
  airflow-backend:
    driver: bridge
    internal: true  # 内部网络，不对外暴露
  airflow-database:
    driver: bridge
    internal: true
```

### 7.3 定期安全审计

```python
# 安全审计脚本示例
import subprocess
import json
from datetime import datetime

def run_security_audit():
    """运行安全审计检查"""
    audit_results = {
        'timestamp': datetime.now().isoformat(),
        'checks': []
    }
    
    # 检查是否有默认密码
    default_password_check = {
        'name': 'Default Password Check',
        'status': 'passed',
        'details': 'No default passwords found'
    }
    
    # 检查是否启用了 HTTPS
    https_check = {
        'name': 'HTTPS Configuration',
        'status': 'passed',
        'details': 'HTTPS is enabled'
    }
    
    # 检查是否启用了审计日志
    audit_log_check = {
        'name': 'Audit Logging',
        'status': 'warning',
        'details': 'Audit logging is enabled but retention policy not set'
    }
    
    audit_results['checks'] = [
        default_password_check,
        https_check,
        audit_log_check
    ]
    
    return audit_results

# 运行审计并保存结果
results = run_security_audit()
with open('/var/log/airflow/security_audit.json', 'w') as f:
    json.dump(results, f, indent=2)
```

通过以上详细的学习材料，你应该对 Airflow 的安全机制有了全面的了解。在实践中，请始终遵循最小权限原则，定期审查和更新安全配置，并保持对最新安全威胁的关注。