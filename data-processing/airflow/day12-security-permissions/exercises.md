# Day 12: 安全与权限管理 - 实践练习

## 概述
今天的实践练习将帮助你巩固在理论学习中获得的安全知识。我们将通过一系列由浅入深的练习，让你掌握 Airflow 安全配置、身份验证集成、权限管理和密钥保护等关键技能。

## 基础练习

### 练习 1: 配置 RBAC 并创建自定义角色

#### 目标
创建一个具有特定权限的自定义角色，并将其分配给用户。

#### 步骤
1. 创建一个名为 "DataAnalyst" 的自定义角色
2. 为该角色分配以下权限：
   - 查看所有 DAG
   - 查看任务实例
   - 查看日志
   - 不能编辑 DAG
3. 创建一个新用户并分配该角色

#### 代码示例
```python
# exercise1_rbac_setup.py
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser
from airflow.www.security import AirflowSecurityManager

def create_data_analyst_role():
    """创建 DataAnalyst 角色"""
    security_manager = AirflowSecurityManager()
    
    # 创建角色
    role_name = "DataAnalyst"
    role = security_manager.find_role(role_name)
    if not role:
        role = security_manager.add_role(role_name)
        print(f"Created role: {role_name}")
    else:
        print(f"Role {role_name} already exists")
    
    # 定义权限
    permissions = [
        ("menu_access", "DAG Runs"),
        ("menu_access", "Browse"),
        ("menu_access", "Docs"),
        ("can_dag_read", "DAG"),
        ("can_task_instance_read", "DAG"),
        ("can_log_read", "DAG")
    ]
    
    # 分配权限
    for perm_name, view_menu in permissions:
        perm_view = security_manager.add_permission_view_menu(perm_name, view_menu)
        security_manager.add_permission_role(role, perm_view)
    
    print(f"Assigned permissions to role: {role_name}")
    return role

def create_user_with_role(username, password, role_name):
    """创建用户并分配角色"""
    session = settings.Session()
    
    # 检查用户是否已存在
    existing_user = session.query(PasswordUser).filter(
        PasswordUser.username == username
    ).first()
    
    if existing_user:
        print(f"User {username} already exists")
        user = existing_user
    else:
        # 创建新用户
        user = PasswordUser(username=username)
        user.password = password
        user.superuser = False
        session.add(user)
        session.commit()
        print(f"Created user: {username}")
    
    # 分配角色
    security_manager = AirflowSecurityManager()
    role = security_manager.find_role(role_name)
    if role:
        if role not in user.roles:
            user.roles.append(role)
            session.commit()
            print(f"Assigned role {role_name} to user {username}")
        else:
            print(f"User {username} already has role {role_name}")
    else:
        print(f"Role {role_name} not found")
    
    session.close()

# 执行练习
if __name__ == "__main__":
    # 创建角色
    role = create_data_analyst_role()
    
    # 创建用户
    create_user_with_role("analyst1", "secure_password_123", "DataAnalyst")
    create_user_with_role("analyst2", "another_secure_password", "DataAnalyst")
```

#### 验证
1. 登录 Airflow Web UI
2. 使用新创建的用户账户登录
3. 验证用户只能查看 DAG 和日志，不能编辑 DAG

### 练习 2: 实现 LDAP 身份验证集成

#### 目标
配置 Airflow 以使用 LDAP 进行身份验证。

#### 步骤
1. 设置 LDAP 服务器（可以使用示例配置）
2. 配置 Airflow 以连接到 LDAP 服务器
3. 测试 LDAP 身份验证

#### 配置文件示例
```ini
# ldap_config.cfg - LDAP 配置文件
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
# webserver_config.py - Web 服务器配置
import os
from flask_appbuilder.security.manager import AUTH_LDAP

# 数据库 URI
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://airflow:airflow@postgres/airflow'

# 认证类型
AUTH_TYPE = AUTH_LDAP

# LDAP 配置
AUTH_LDAP_SERVER = "ldap://ldap.example.com:389"
AUTH_LDAP_BIND_USER = "cn=Manager,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "admin_password"
AUTH_LDAP_SEARCH = "dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"

# 用户注册相关
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Viewer"

# LDAP 组映射
AUTH_LDAP_GROUP_FIELD = "memberOf"
AUTH_LDAP_GROUP_USER_ATTRIBUTE = "dn"
```

#### 测试脚本
```python
# exercise2_ldap_test.py
import ldap
from airflow import settings
from airflow.contrib.auth.backends.ldap_auth import LdapUser

def test_ldap_connection():
    """测试 LDAP 连接"""
    ldap_server = "ldap://ldap.example.com:389"
    bind_user = "cn=Manager,dc=example,dc=com"
    bind_password = "admin_password"
    
    try:
        # 连接到 LDAP 服务器
        conn = ldap.initialize(ldap_server)
        conn.simple_bind_s(bind_user, bind_password)
        print("LDAP connection successful")
        
        # 搜索用户
        base_dn = "dc=example,dc=com"
        search_filter = "(uid=testuser)"
        attrs = ["uid", "cn", "mail"]
        
        result = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, attrs)
        if result:
            print(f"Found user: {result[0][1]}")
        else:
            print("User not found")
            
        conn.unbind()
        return True
    except ldap.INVALID_CREDENTIALS:
        print("Invalid credentials")
        return False
    except ldap.SERVER_DOWN:
        print("LDAP server is down")
        return False
    except Exception as e:
        print(f"LDAP connection failed: {e}")
        return False

def create_ldap_user(username):
    """创建 LDAP 用户对象"""
    session = settings.Session()
    
    # 检查用户是否已存在
    user = session.query(LdapUser).filter(
        LdapUser.username == username
    ).first()
    
    if not user:
        user = LdapUser(username=username)
        session.add(user)
        session.commit()
        print(f"Created LDAP user: {username}")
    else:
        print(f"LDAP user {username} already exists")
    
    session.close()
    return user

# 执行测试
if __name__ == "__main__":
    # 测试 LDAP 连接
    if test_ldap_connection():
        # 创建测试用户
        create_ldap_user("testuser")
        print("LDAP exercise completed successfully")
    else:
        print("LDAP exercise failed")
```

### 练习 3: 配置 HTTPS 支持

#### 目标
为 Airflow Web 服务器配置 HTTPS 支持。

#### 步骤
1. 生成自签名证书（用于测试）
2. 配置 Airflow 使用 HTTPS
3. 验证 HTTPS 配置

#### 证书生成脚本
```bash
# generate_cert.sh - 生成自签名证书
#!/bin/bash

# 创建私钥
openssl genrsa -out private.key 2048

# 创建证书签名请求
openssl req -new -key private.key -out certificate.csr \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# 创建自签名证书
openssl x509 -req -days 365 -in certificate.csr -signkey private.key -out certificate.crt

# 清理临时文件
rm certificate.csr

echo "Certificate generated successfully"
```

#### Airflow 配置
```ini
# airflow.cfg - HTTPS 配置
[webserver]
web_server_ssl_cert = /path/to/certificate.crt
web_server_ssl_key = /path/to/private.key
```

#### 验证脚本
```python
# exercise3_https_check.py
import ssl
import socket
from urllib.request import urlopen
from urllib.error import URLError

def check_https_certificate(hostname, port=443):
    """检查 HTTPS 证书"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"Certificate subject: {cert['subject']}")
                print(f"Certificate issuer: {cert['issuer']}")
                print(f"Certificate version: {cert['version']}")
                print(f"Certificate valid from: {cert['notBefore']}")
                print(f"Certificate valid until: {cert['notAfter']}")
                return True
    except Exception as e:
        print(f"Certificate check failed: {e}")
        return False

def test_https_connection(url):
    """测试 HTTPS 连接"""
    try:
        response = urlopen(url, timeout=10)
        print(f"HTTPS connection successful: {response.status}")
        print(f"Response headers: {response.headers}")
        return True
    except URLError as e:
        print(f"HTTPS connection failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# 执行检查
if __name__ == "__main__":
    hostname = "localhost"
    url = "https://localhost:8443"  # 假设 Airflow 运行在 8443 端口
    
    print("Checking HTTPS certificate...")
    if check_https_certificate(hostname):
        print("\nTesting HTTPS connection...")
        test_https_connection(url)
    else:
        print("HTTPS configuration exercise failed")
```

## 进阶练习

### 练习 4: 集成 HashiCorp Vault 进行密钥管理

#### 目标
配置 Airflow 使用 HashiCorp Vault 存储和检索敏感信息。

#### 步骤
1. 启动 Vault 服务器
2. 配置 Vault 存储连接信息和变量
3. 配置 Airflow 使用 Vault 后端
4. 在 DAG 中使用 Vault 存储的密钥

#### Vault 配置
```hcl
# vault_config.hcl - Vault 配置文件
storage "file" {
  path = "/var/lib/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"
```

#### Vault 数据存储脚本
```python
# exercise4_vault_setup.py
import hvac
import json

def setup_vault_secrets():
    """在 Vault 中设置 Airflow 密钥"""
    # 连接到 Vault
    client = hvac.Client(url='http://127.0.0.1:8200')
    
    # 启用 kv v2 引擎
    try:
        client.sys.enable_secrets_engine(
            backend_type='kv',
            path='airflow',
            options={'version': 2}
        )
        print("KV v2 engine enabled")
    except hvac.exceptions.InvalidRequest:
        print("KV v2 engine already enabled")
    
    # 存储连接信息
    connections_data = {
        'postgres_default': {
            'conn_type': 'postgres',
            'host': 'postgres.example.com',
            'port': 5432,
            'login': 'airflow',
            'password': 'encrypted_password',
            'schema': 'airflow'
        },
        'redis_default': {
            'conn_type': 'redis',
            'host': 'redis.example.com',
            'port': 6379,
            'password': 'redis_password'
        }
    }
    
    # 写入连接信息
    for conn_id, conn_data in connections_data.items():
        client.secrets.kv.v2.create_or_update_secret(
            path=f'airflow/connections/{conn_id}',
            secret=conn_data
        )
        print(f"Stored connection: {conn_id}")
    
    # 存储变量
    variables_data = {
        'api_key': 'secret_api_key_12345',
        'secret_token': 'jwt_token_xxxxxxxxxx',
        'encryption_key': 'aes_encryption_key'
    }
    
    # 写入变量
    for var_name, var_value in variables_data.items():
        client.secrets.kv.v2.create_or_update_secret(
            path=f'airflow/variables/{var_name}',
            secret={'value': var_value}
        )
        print(f"Stored variable: {var_name}")

def read_vault_secrets():
    """从 Vault 读取密钥"""
    client = hvac.Client(url='http://127.0.0.1:8200')
    
    # 读取连接信息
    try:
        conn_response = client.secrets.kv.v2.read_secret_version(
            path='airflow/connections/postgres_default'
        )
        conn_data = conn_response['data']['data']
        print(f"Postgres connection: {conn_data}")
    except Exception as e:
        print(f"Failed to read connection: {e}")
    
    # 读取变量
    try:
        var_response = client.secrets.kv.v2.read_secret_version(
            path='airflow/variables/api_key'
        )
        var_data = var_response['data']['data']
        print(f"API key: {var_data['value']}")
    except Exception as e:
        print(f"Failed to read variable: {e}")

# 执行设置
if __name__ == "__main__":
    setup_vault_secrets()
    read_vault_secrets()
```

#### Airflow 配置
```ini
# airflow.cfg - Vault 后端配置
[secrets]
backend = airflow.providers.hashicorp.secrets.vault.VaultBackend
backend_kwargs = {"connections_path": "airflow/connections", "variables_path": "airflow/variables", "url": "http://127.0.0.1:8200"}
```

### 练习 5: 实现自定义权限检查

#### 目标
创建一个自定义权限检查机制，用于控制对特定 DAG 的访问。

#### 步骤
1. 创建自定义权限类
2. 实现基于用户组的 DAG 访问控制
3. 在 Web UI 中集成权限检查

#### 自定义权限实现
```python
# exercise5_custom_permissions.py
from airflow.models import DagModel
from airflow.www.security import AirflowSecurityManager
from airflow import settings
from typing import List, Set

class CustomSecurityManager(AirflowSecurityManager):
    """自定义安全管理器"""
    
    def get_user_dag_permissions(self, user) -> Set[str]:
        """获取用户有权限访问的 DAG 列表"""
        session = settings.Session()
        
        # 获取用户角色
        user_roles = [role.name for role in user.roles]
        
        # 根据角色确定可访问的 DAG
        allowed_dags = set()
        
        if "Admin" in user_roles:
            # 管理员可以访问所有 DAG
            dags = session.query(DagModel).all()
            allowed_dags = {dag.dag_id for dag in dags}
        elif "DataEngineer" in user_roles:
            # 数据工程师可以访问特定前缀的 DAG
            dags = session.query(DagModel).filter(
                DagModel.dag_id.like('data_engineering_%')
            ).all()
            allowed_dags = {dag.dag_id for dag in dags}
        elif "DataAnalyst" in user_roles:
            # 数据分析师可以访问特定前缀的 DAG
            dags = session.query(DagModel).filter(
                DagModel.dag_id.like('analytics_%')
            ).all()
            allowed_dags = {dag.dag_id for dag in dags}
        else:
            # 其他用户只能访问公开的 DAG
            dags = session.query(DagModel).filter(
                DagModel.is_paused == False
            ).all()
            allowed_dags = {dag.dag_id for dag in dags}
        
        session.close()
        return allowed_dags
    
    def can_access_dag(self, dag_id: str, user) -> bool:
        """检查用户是否可以访问指定的 DAG"""
        allowed_dags = self.get_user_dag_permissions(user)
        return dag_id in allowed_dags or "*" in allowed_dags

def check_dag_access(user, dag_id: str) -> bool:
    """检查用户对 DAG 的访问权限"""
    security_manager = CustomSecurityManager()
    return security_manager.can_access_dag(dag_id, user)

# 使用示例
def demo_custom_permissions():
    """演示自定义权限检查"""
    # 假设我们有以下用户和角色
    class MockUser:
        def __init__(self, username, roles):
            self.username = username
            self.roles = [type('Role', (), {'name': role})() for role in roles]
    
    users = [
        MockUser("admin_user", ["Admin"]),
        MockUser("engineer_user", ["DataEngineer"]),
        MockUser("analyst_user", ["DataAnalyst"]),
        MockUser("guest_user", ["Public"])
    ]
    
    # 测试不同的 DAG
    test_dags = [
        "data_engineering_etl_pipeline",
        "analytics_reporting_dashboard",
        "finance_monthly_report",
        "hr_employee_onboarding"
    ]
    
    # 检查每个用户对每个 DAG 的访问权限
    for user in users:
        print(f"\nUser: {user.username} (Roles: {[r.name for r in user.roles]})")
        for dag in test_dags:
            can_access = check_dag_access(user, dag)
            status = "✓" if can_access else "✗"
            print(f"  {status} Access to {dag}: {can_access}")

# 执行演示
if __name__ == "__main__":
    demo_custom_permissions()
```

## 挑战练习

### 练习 6: 构建完整的安全监控仪表板

#### 目标
创建一个安全监控仪表板，实时显示用户活动、异常行为和安全指标。

#### 步骤
1. 设计安全监控指标
2. 实现日志收集和分析
3. 创建可视化仪表板
4. 配置告警机制

#### 安全监控实现
```python
# exercise6_security_dashboard.py
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class SecurityEvent:
    """安全事件数据类"""
    timestamp: datetime
    event_type: str
    user: str
    ip_address: str
    resource: str
    details: str
    severity: str

class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self):
        self.events = deque(maxlen=1000)  # 保留最近1000个事件
        self.user_activity = defaultdict(list)
        self.ip_activity = defaultdict(list)
        self.failed_logins = defaultdict(int)
        self.lock = threading.Lock()
        
    def log_event(self, event_type: str, user: str, ip_address: str, 
                  resource: str = "", details: str = "", severity: str = "info"):
        """记录安全事件"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            user=user,
            ip_address=ip_address,
            resource=resource,
            details=details,
            severity=severity
        )
        
        with self.lock:
            self.events.append(event)
            self.user_activity[user].append(event)
            self.ip_activity[ip_address].append(event)
            
            # 记录失败的登录尝试
            if event_type == "failed_login":
                self.failed_logins[ip_address] += 1
    
    def get_recent_events(self, minutes: int = 60) -> List[SecurityEvent]:
        """获取最近的事件"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            return [event for event in self.events if event.timestamp >= cutoff_time]
    
    def get_user_activity_summary(self, user: str) -> Dict:
        """获取用户活动摘要"""
        with self.lock:
            user_events = self.user_activity.get(user, [])
            if not user_events:
                return {}
            
            # 按事件类型统计
            event_types = defaultdict(int)
            for event in user_events:
                event_types[event.event_type] += 1
            
            # 最近活动时间
            last_activity = max(event.timestamp for event in user_events)
            
            return {
                "total_events": len(user_events),
                "event_types": dict(event_types),
                "last_activity": last_activity.isoformat()
            }
    
    def detect_anomalies(self) -> List[Dict]:
        """检测异常行为"""
        anomalies = []
        now = datetime.now()
        
        with self.lock:
            # 检测高频失败登录
            for ip, count in self.failed_logins.items():
                if count >= 5:  # 5次失败登录阈值
                    anomalies.append({
                        "type": "high_failed_logins",
                        "ip": ip,
                        "count": count,
                        "severity": "high",
                        "description": f"High number of failed login attempts from IP {ip}"
                    })
            
            # 检测异常时间活动
            recent_events = self.get_recent_events(60)
            for event in recent_events:
                # 检测深夜活动（假设为异常）
                hour = event.timestamp.hour
                if hour >= 22 or hour <= 6:
                    anomalies.append({
                        "type": "unusual_time_activity",
                        "user": event.user,
                        "time": event.timestamp.isoformat(),
                        "severity": "medium",
                        "description": f"Activity at unusual time: {event.event_type}"
                    })
            
            # 检测多IP登录同一用户
            user_ips = defaultdict(set)
            for event in recent_events:
                user_ips[event.user].add(event.ip_address)
            
            for user, ips in user_ips.items():
                if len(ips) > 2:  # 同一用户从多个IP登录
                    anomalies.append({
                        "type": "multiple_ips",
                        "user": user,
                        "ips": list(ips),
                        "severity": "medium",
                        "description": f"User {user} logged in from {len(ips)} different IPs"
                    })
        
        return anomalies
    
    def get_security_metrics(self) -> Dict:
        """获取安全指标"""
        with self.lock:
            total_events = len(self.events)
            failed_logins = sum(self.failed_logins.values())
            
            # 计算成功率
            successful_logins = len([e for e in self.events if e.event_type == "successful_login"])
            total_logins = successful_logins + failed_logins
            success_rate = (successful_logins / total_logins * 100) if total_logins > 0 else 0
            
            # 获取最近事件
            recent_events = self.get_recent_events(10)  # 最近10分钟
            
            return {
                "total_events": total_events,
                "failed_logins": failed_logins,
                "successful_logins": successful_logins,
                "login_success_rate": round(success_rate, 2),
                "recent_events": [asdict(event) for event in recent_events[-10:]],  # 最近10个事件
                "active_users": len(self.user_activity),
                "active_ips": len(self.ip_activity)
            }

# 模拟安全事件生成器
class SecurityEventGenerator:
    """安全事件生成器（用于演示）"""
    
    def __init__(self, monitor: SecurityMonitor):
        self.monitor = monitor
        self.running = False
        self.thread = None
    
    def start(self):
        """开始生成事件"""
        self.running = True
        self.thread = threading.Thread(target=self._generate_events)
        self.thread.start()
    
    def stop(self):
        """停止生成事件"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _generate_events(self):
        """生成模拟安全事件"""
        import random
        
        users = ["admin", "analyst1", "engineer1", "guest"]
        ips = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "10.0.0.5"]
        resources = ["DAG:etl_pipeline", "DAG:report_generator", "connection:postgres_db"]
        event_types = ["successful_login", "failed_login", "dag_triggered", "task_executed", "config_changed"]
        
        while self.running:
            # 随机生成事件
            user = random.choice(users)
            ip = random.choice(ips)
            resource = random.choice(resources)
            event_type = random.choice(event_types)
            
            # 有一定概率生成失败登录
            if random.random() < 0.1:  # 10% 概率
                event_type = "failed_login"
            
            # 记录事件
            self.monitor.log_event(
                event_type=event_type,
                user=user,
                ip_address=ip,
                resource=resource,
                details=f"Simulated {event_type} event",
                severity="info" if event_type != "failed_login" else "warning"
            )
            
            # 随机延迟
            time.sleep(random.uniform(1, 5))

# 仪表板展示
def display_security_dashboard(monitor: SecurityMonitor):
    """显示安全监控仪表板"""
    print("\n" + "="*60)
    print("           AIRFLOW SECURITY MONITORING DASHBOARD")
    print("="*60)
    
    # 获取安全指标
    metrics = monitor.get_security_metrics()
    
    print(f"\n📊 SECURITY METRICS")
    print(f"   Total Events: {metrics['total_events']}")
    print(f"   Active Users: {metrics['active_users']}")
    print(f"   Active IPs: {metrics['active_ips']}")
    print(f"   Login Success Rate: {metrics['login_success_rate']}%")
    print(f"   Failed Logins: {metrics['failed_logins']}")
    
    print(f"\n🔍 RECENT EVENTS (Last 10 minutes)")
    for event in metrics['recent_events']:
        timestamp = event['timestamp']
        event_type = event['event_type']
        user = event['user']
        severity = event['severity']
        severity_icon = {"high": "🔴", "medium": "🟡", "info": "🟢"}.get(severity, "⚪")
        print(f"   {severity_icon} [{timestamp}] {event_type} by {user}")
    
    # 检测异常
    print(f"\n⚠️  ANOMALY DETECTION")
    anomalies = monitor.detect_anomalies()
    if anomalies:
        for anomaly in anomalies:
            severity_icon = {"high": "🔴", "medium": "🟡", "info": "🟢"}.get(anomaly['severity'], "⚪")
            print(f"   {severity_icon} {anomaly['description']}")
    else:
        print("   🟢 No anomalies detected")
    
    print("="*60)

# 演示程序
def run_security_dashboard_demo():
    """运行安全监控仪表板演示"""
    # 创建监控器
    monitor = SecurityMonitor()
    
    # 创建事件生成器
    generator = SecurityEventGenerator(monitor)
    
    try:
        # 开始生成事件
        print("Starting security event generation...")
        generator.start()
        
        # 模拟运行一段时间
        for i in range(10):
            time.sleep(3)
            display_security_dashboard(monitor)
            
    except KeyboardInterrupt:
        print("\nStopping security monitoring...")
    finally:
        generator.stop()

# 执行演示
if __name__ == "__main__":
    run_security_dashboard_demo()
```

### 练习 7: 实现多因素身份验证

#### 目标
为 Airflow 实现多因素身份验证（MFA）机制。

#### 步骤
1. 实现 TOTP（基于时间的一次性密码）验证
2. 集成到 Airflow 身份验证流程
3. 创建用户注册和密钥管理界面

#### MFA 实现
```python
# exercise7_mfa_implementation.py
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib
import hmac

class MFAService:
    """多因素身份验证服务"""
    
    def __init__(self):
        self.user_secrets = {}  # 存储用户密钥（实际应用中应加密存储）
        self.failed_attempts = {}  # 记录失败尝试
        self.totp_window = 1  # TOTP 时间窗口（分钟）
    
    def generate_secret_key(self) -> str:
        """生成用户密钥"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, username: str, secret: str, issuer: str = "Airflow") -> str:
        """生成 QR 码用于身份验证器应用"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer
        )
        
        # 生成 QR 码
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # 转换为 base64 图像数据
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return base64.b64encode(img_buffer.getvalue()).decode()
    
    def enable_mfa_for_user(self, username: str) -> Dict[str, str]:
        """为用户启用 MFA"""
        secret = self.generate_secret_key()
        self.user_secrets[username] = secret
        
        # 生成 QR 码
        qr_code = self.generate_qr_code(username, secret)
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": self.generate_backup_codes(username)
        }
    
    def generate_backup_codes(self, username: str, count: int = 10) -> List[str]:
        """生成备份代码"""
        import secrets
        backup_codes = []
        for _ in range(count):
            code = secrets.token_urlsafe(16)[:16]
            backup_codes.append(code)
        return backup_codes
    
    def verify_totp(self, username: str, token: str) -> bool:
        """验证 TOTP 令牌"""
        if username not in self.user_secrets:
            return False
        
        secret = self.user_secrets[username]
        totp = pyotp.TOTP(secret)
        
        # 验证令牌（允许一定时间窗口）
        return totp.verify(token, valid_window=self.totp_window)
    
    def verify_backup_code(self, username: str, backup_code: str) -> bool:
        """验证备份代码（简化实现）"""
        # 在实际应用中，备份代码应该存储在数据库中并标记为已使用
        # 这里简化处理，只是验证格式
        return len(backup_code) == 16 and backup_code.isalnum()
    
    def is_mfa_enabled(self, username: str) -> bool:
        """检查用户是否启用了 MFA"""
        return username in self.user_secrets
    
    def record_failed_attempt(self, username: str):
        """记录失败的验证尝试"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.now())
        
        # 清理超过1小时的记录
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.failed_attempts[username] = [
            attempt for attempt in self.failed_attempts[username]
            if attempt > cutoff_time
        ]
    
    def is_user_locked_out(self, username: str, max_attempts: int = 5) -> bool:
        """检查用户是否被锁定"""
        if username not in self.failed_attempts:
            return False
        
        recent_attempts = self.failed_attempts[username]
        return len(recent_attempts) >= max_attempts

# MFA 集成到身份验证流程
class EnhancedAuthManager:
    """增强的身份验证管理器"""
    
    def __init__(self):
        self.mfa_service = MFAService()
        self.users = {
            "admin": {"password": "admin123", "mfa_enabled": True},
            "user1": {"password": "user123", "mfa_enabled": False}
        }
    
    def authenticate_user(self, username: str, password: str, mfa_token: Optional[str] = None) -> Dict:
        """用户身份验证"""
        result = {
            "success": False,
            "message": "",
            "requires_mfa": False,
            "mfa_setup_required": False
        }
        
        # 检查用户是否存在
        if username not in self.users:
            result["message"] = "Invalid username or password"
            return result
        
        user = self.users[username]
        
        # 检查用户是否被锁定
        if self.mfa_service.is_user_locked_out(username):
            result["message"] = "Account temporarily locked due to multiple failed attempts"
            return result
        
        # 验证密码
        if user["password"] != password:
            self.mfa_service.record_failed_attempt(username)
            result["message"] = "Invalid username or password"
            return result
        
        # 检查是否需要 MFA
        if user.get("mfa_enabled", False):
            if not self.mfa_service.is_mfa_enabled(username):
                # 用户启用了 MFA 但尚未设置
                result["requires_mfa"] = True
                result["mfa_setup_required"] = True
                result["message"] = "MFA setup required"
                return result
            
            # 需要 MFA 令牌
            if not mfa_token:
                result["requires_mfa"] = True
                result["message"] = "MFA token required"
                return result
            
            # 验证 MFA 令牌
            if not self.mfa_service.verify_totp(username, mfa_token):
                self.mfa_service.record_failed_attempt(username)
                result["message"] = "Invalid MFA token"
                return result
        
        # 验证成功
        result["success"] = True
        result["message"] = "Authentication successful"
        return result
    
    def setup_mfa_for_user(self, username: str) -> Dict:
        """为用户设置 MFA"""
        if username not in self.users:
            return {"success": False, "message": "User not found"}
        
        # 启用 MFA
        self.users[username]["mfa_enabled"] = True
        
        # 生成 MFA 设置信息
        mfa_info = self.mfa_service.enable_mfa_for_user(username)
        
        return {
            "success": True,
            "message": "MFA setup completed",
            "secret": mfa_info["secret"],
            "qr_code": mfa_info["qr_code"],
            "backup_codes": mfa_info["backup_codes"]
        }

# 演示程序
def demo_mfa_authentication():
    """演示 MFA 身份验证"""
    auth_manager = EnhancedAuthManager()
    
    print("🔐 Airflow MFA Authentication Demo")
    print("=" * 50)
    
    # 为管理员设置 MFA
    print("\n1. Setting up MFA for admin user...")
    mfa_setup = auth_manager.setup_mfa_for_user("admin")
    if mfa_setup["success"]:
        print("✅ MFA setup completed")
        print(f"   Secret: {mfa_setup['secret']}")
        print(f"   Backup codes generated: {len(mfa_setup['backup_codes'])}")
    else:
        print(f"❌ MFA setup failed: {mfa_setup['message']}")
        return
    
    # 生成 TOTP 令牌用于测试
    secret = mfa_setup['secret']
    totp = pyotp.TOTP(secret)
    current_token = totp.now()
    
    print(f"\n2. Current TOTP token: {current_token}")
    
    # 测试身份验证
    print("\n3. Testing authentication...")
    
    # 不带 MFA 令牌的验证（应该失败）
    print("\n   a) Authentication without MFA token:")
    result = auth_manager.authenticate_user("admin", "admin123")
    print(f"      Result: {result['message']}")
    print(f"      Requires MFA: {result['requires_mfa']}")
    
    # 带错误 MFA 令牌的验证（应该失败）
    print("\n   b) Authentication with wrong MFA token:")
    result = auth_manager.authenticate_user("admin", "admin123", "123456")
    print(f"      Result: {result['message']}")
    
    # 带正确 MFA 令牌的验证（应该成功）
    print("\n   c) Authentication with correct MFA token:")
    result = auth_manager.authenticate_user("admin", "admin123", current_token)
    print(f"      Result: {result['message']}")
    print(f"      Success: {result['success']}")
    
    # 测试未启用 MFA 的用户
    print("\n4. Testing user without MFA:")
    result = auth_manager.authenticate_user("user1", "user123")
    print(f"   Result: {result['message']}")
    print(f"   Success: {result['success']}")

# 执行演示
if __name__ == "__main__":
    demo_mfa_authentication()
```

通过完成这些实践练习，你将掌握 Airflow 安全管理的核心技能，包括 RBAC 配置、LDAP 集成、HTTPS 配置、密钥管理、自定义权限控制以及高级安全监控等。这些技能对于在生产环境中安全地部署和管理 Airflow 至关重要。