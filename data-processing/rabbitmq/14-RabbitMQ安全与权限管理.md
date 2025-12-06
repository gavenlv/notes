# 第14章：RabbitMQ安全与权限管理

## 安全基础概念

在分布式系统中，消息队列承载着关键的通信和业务数据，其安全性直接影响整个系统的安全性和可靠性。RabbitMQ提供了多层次的安全机制，包括认证、授权、加密和审计等功能。

### 核心安全原则

1. **最小权限原则**：用户和应用程序只应获得执行其功能所需的最小权限
2. **分层防护**：网络层、传输层、应用层的多重安全防护
3. **密钥管理**：安全的密钥生成、存储和轮换机制
4. **审计追踪**：完整的操作记录和异常检测
5. **定期安全评估**：定期的安全检查和漏洞扫描

## 认证机制

### 1. 内置认证

RabbitMQ支持多种内置认证机制：

#### 用户名密码认证
```python
import pika
from pika import PlainCredentials

# 使用用户名密码连接
credentials = PlainCredentials('username', 'password')
connection_parameters = pika.ConnectionParameters(
    'localhost',
    5672,
    '/',
    credentials
)

connection = pika.BlockingConnection(connection_parameters)
```

#### 虚拟主机认证
```python
# 连接时指定虚拟主机
connection_parameters = pika.ConnectionParameters(
    'localhost',
    5672,
    '/',
    credentials,
    connection_attempts=3,
    retry_delay=5
)

# 使用虚拟主机
channel = connection.channel()
channel.queue_declare(queue='secure_queue', durable=True)
```

### 2. LDAP认证

LDAP（轻量级目录访问协议）集成，允许使用企业级目录服务：

#### LDAP配置
```ini
# rabbitmq.config
[
    {rabbit, [
        {auth_backends, [rabbit_auth_backend_ldap, rabbit_auth_backend_internal]}
    ]},
    {rabbit_auth_backend_ldap, [
        {servers, ["ldap.example.com"]},
        {user_dn_pattern, "cn=${username},ou=users,dc=example,dc=com"},
        {use_ssl, true},
        {port, 636}
    ]}
].
```

#### 动态用户认证
```python
import ldap3

class LDAPAuthenticator:
    def __init__(self, ldap_server, base_dn):
        self.ldap_server = ldap_server
        self.base_dn = base_dn
    
    def authenticate(self, username, password):
        try:
            # 连接到LDAP服务器
            server = ldap3.Server(self.ldap_server)
            conn = ldap3.Connection(server)
            
            # 绑定用户
            user_dn = f"cn={username},ou=users,dc=example,dc=com"
            conn.bind(user_dn, password)
            
            return conn.result['result'] == ldap3.result.BIND_SUCCESS
        except Exception as e:
            print(f"LDAP认证失败: {e}")
            return False
    
    def get_user_groups(self, username):
        """获取用户所属组"""
        try:
            server = ldap3.Server(self.ldap_server)
            conn = ldap3.Connection(server)
            
            # 获取用户组信息
            search_filter = f"(cn={username})"
            conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                attributes=['memberOf']
            )
            
            if conn.entries:
                groups = conn.entries[0]['memberOf'].values
                return [group.split(',')[0].split('CN=')[1] for group in groups]
            
            return []
        except Exception as e:
            print(f"获取用户组失败: {e}")
            return []
```

### 3. OAuth 2.0认证

现代应用广泛使用OAuth 2.0进行身份认证：

#### OAuth 2.0集成
```python
import jwt
import requests
from datetime import datetime, timedelta

class OAuthAuthenticator:
    def __init__(self, auth_server_url, client_id, client_secret):
        self.auth_server_url = auth_server_url
        self.client_id = client_id
        self.client_secret = client_secret
    
    def generate_token(self, username, scope):
        """生成访问令牌"""
        payload = {
            'sub': username,
            'scope': scope,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        # 使用JWT库生成令牌
        token = jwt.encode(payload, self.client_secret, algorithm='HS256')
        return token
    
    def verify_token(self, token):
        """验证访问令牌"""
        try:
            payload = jwt.decode(token, self.client_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("令牌已过期")
        except jwt.InvalidTokenError:
            raise Exception("无效令牌")
    
    def get_user_permissions(self, token):
        """从令牌中获取用户权限"""
        payload = self.verify_token(token)
        return payload.get('scope', '').split(' ')
```

## 权限管理

### 1. 访问控制列表（ACL）

#### 基本权限配置
```python
import pika

def setup_user_permissions():
    """设置用户权限"""
    # 管理员连接RabbitMQ管理界面
    admin_credentials = PlainCredentials('admin', 'admin_password')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost', credentials=admin_credentials)
    )
    
    channel = connection.channel()
    
    # 创建用户
    channel.rpc_call('rabbit_user_management', 'create_user', {
        'user': 'app_user',
        'password': 'secure_password',
        'tags': 'application'
    })
    
    # 设置权限
    channel.rpc_call('rabbit_access_control', 'set_permissions', {
        'user': 'app_user',
        'vhost': '/',
        'configure': '^(?!.*exclusive).*',
        'write': '^app\.exchange\.',
        'read': '^app\.queue\..*'
    })
    
    # 创建vhost权限
    channel.rpc_call('rabbit_access_control', 'set_vhost_permissions', {
        'user': 'app_user',
        'vhost': 'app_vhost'
    })
```

#### 细粒度权限控制
```python
class PermissionManager:
    def __init__(self, connection):
        self.connection = connection
        self.channel = connection.channel()
    
    def create_user_with_permissions(self, username, password, vhost, permissions):
        """创建用户并设置权限"""
        # 创建用户
        self.channel.rpc_call('rabbit_user_management', 'create_user', {
            'user': username,
            'password': password,
            'tags': permissions.get('tags', '')
        })
        
        # 设置虚拟主机权限
        self.channel.rpc_call('rabbit_access_control', 'set_vhost_permissions', {
            'user': username,
            'vhost': vhost
        })
        
        # 设置具体权限
        self.channel.rpc_call('rabbit_access_control', 'set_permissions', {
            'user': username,
            'vhost': vhost,
            'configure': permissions.get('configure', '.*'),
            'write': permissions.get('write', '.*'),
            'read': permissions.get('read', '.*')
        })
    
    def update_user_permissions(self, username, vhost, new_permissions):
        """更新用户权限"""
        self.channel.rpc_call('rabbit_access_control', 'set_permissions', {
            'user': username,
            'vhost': vhost,
            'configure': new_permissions.get('configure', '.*'),
            'write': new_permissions.get('write', '.*'),
            'read': new_permissions.get('read', '.*')
        })
    
    def get_user_permissions(self, username):
        """获取用户权限"""
        return self.channel.rpc_call('rabbit_access_control', 'get_permissions', {
            'user': username
        })
    
    def delete_user(self, username):
        """删除用户"""
        self.channel.rpc_call('rabbit_user_management', 'delete_user', {
            'user': username
        })
```

### 2. 角色管理

#### 预定义角色
```python
class RoleManager:
    """角色管理器"""
    
    ROLES = {
        'application': {
            'tags': 'application',
            'permissions': {
                'configure': '^exclusive.*',  # 不能声明永久队列
                'write': '^app\.(exchange|queue)\..*',
                'read': '^app\.(queue)\..*'
            }
        },
        'monitoring': {
            'tags': 'monitoring',
            'permissions': {
                'configure': '',  # 无配置权限
                'write': '',      # 无写入权限
                'read': '.*'      # 读取所有资源
            }
        },
        'management': {
            'tags': 'management',
            'permissions': {
                'configure': '.*',
                'write': '.*',
                'read': '.*'
            }
        }
    }
    
    def __init__(self, connection):
        self.connection = connection
    
    def assign_role(self, username, role_name):
        """分配角色"""
        if role_name not in self.ROLES:
            raise ValueError(f"未知角色: {role_name}")
        
        role = self.ROLES[role_name]
        
        # 创建用户
        connection = self.connection
        channel = connection.channel()
        
        # 设置用户标签
        channel.rpc_call('rabbit_user_management', 'set_user_tags', {
            'user': username,
            'tags': role['tags']
        })
        
        # 设置权限
        channel.rpc_call('rabbit_access_control', 'set_permissions', {
            'user': username,
            'vhost': '/',
            'configure': role['permissions']['configure'],
            'write': role['permissions']['write'],
            'read': role['permissions']['read']
        })
        
        print(f"用户 {username} 已分配角色 {role_name}")
    
    def create_custom_role(self, role_name, permissions):
        """创建自定义角色"""
        self.ROLES[role_name] = {
            'tags': role_name,
            'permissions': permissions
        }
```

### 3. 条件权限控制

#### 基于条件的权限验证
```python
import re
from datetime import datetime

class ConditionalPermissionChecker:
    """条件权限检查器"""
    
    def __init__(self):
        self.permission_rules = {}
        self.user_context = {}
    
    def add_permission_rule(self, rule_name, condition_func, permissions):
        """添加权限规则"""
        self.permission_rules[rule_name] = {
            'condition': condition_func,
            'permissions': permissions
        }
    
    def check_permission(self, username, action, resource, context):
        """检查权限"""
        # 获取用户上下文
        user_context = self.user_context.get(username, {})
        
        # 检查每个规则
        for rule_name, rule in self.permission_rules.items():
            if rule['condition'](user_context, context):
                # 检查具体权限
                permission = rule['permissions'].get(action)
                if permission and re.match(permission, resource):
                    return True
        
        return False
    
    def set_user_context(self, username, context):
        """设置用户上下文"""
        self.user_context[username] = context

# 使用示例
def time_based_condition(user_context, context):
    """时间条件：工作时间才能访问"""
    current_hour = datetime.now().hour
    return 9 <= current_hour <= 17  # 工作时间

def department_based_condition(user_context, context):
    """部门条件：只有同部门才能访问"""
    return user_context.get('department') == context.get('target_department')

# 设置条件权限
checker = ConditionalPermissionChecker()
checker.add_permission_rule(
    'work_hours_only',
    time_based_condition,
    {'write': '.*queue.*', 'read': '.*queue.*'}
)
checker.add_permission_rule(
    'same_department',
    department_based_condition,
    {'configure': '.*queue.*'}
)
```

## 数据加密

### 1. 传输层加密

#### SSL/TLS配置
```python
import ssl
import pika
from pika import SSLOptions

def create_ssl_connection():
    """创建SSL连接"""
    # SSL上下文配置
    context = ssl.create_default_context(cafile='/path/to/ca.crt')
    context.load_cert_chain('/path/to/client.crt', '/path/to/client.key')
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    
    # SSL选项
    ssl_options = SSLOptions(context, server_hostname='rabbitmq.example.com')
    
    # 连接参数
    connection_parameters = pika.ConnectionParameters(
        host='rabbitmq.example.com',
        port=5671,
        ssl_options=ssl_options,
        credentials=PlainCredentials('username', 'password'),
        connection_attempts=3,
        retry_delay=5
    )
    
    return pika.BlockingConnection(connection_parameters)
```

#### 自定义SSL验证
```python
class CustomSSLValidator:
    """自定义SSL验证器"""
    
    def __init__(self, ca_cert_path, client_cert_path, client_key_path):
        self.ca_cert_path = ca_cert_path
        self.client_cert_path = client_cert_path
        self.client_key_path = client_key_path
    
    def create_ssl_context(self):
        """创建SSL上下文"""
        context = ssl.create_default_context(cafile=self.ca_cert_path)
        context.load_cert_chain(self.client_cert_path, self.client_key_path)
        
        # 自定义验证
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        return context
    
    def validate_certificate(self, peer_cert):
        """验证证书"""
        # 检查证书有效期
        if datetime.now() < peer_cert.not_valid_before or datetime.now() > peer_cert.not_valid_after:
            raise ValueError("证书已过期")
        
        # 检查证书主题
        if 'CN' not in peer_cert.subject:
            raise ValueError("证书缺少Common Name")
        
        # 检查证书颁发者
        expected_issuer = ['CN=RabbitMQ CA,O=Example,C=US']
        if str(peer_cert.issuer) not in expected_issuer:
            raise ValueError("证书颁发者不受信任")
        
        return True
```

### 2. 消息内容加密

#### 对称加密
```python
from cryptography.fernet import Fernet
import base64

class MessageEncryptor:
    """消息加密器"""
    
    def __init__(self, key=None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    def encrypt_message(self, message):
        """加密消息"""
        if isinstance(message, str):
            message = message.encode()
        
        encrypted_message = self.cipher.encrypt(message)
        return base64.b64encode(encrypted_message).decode()
    
    def decrypt_message(self, encrypted_message):
        """解密消息"""
        encrypted_message = base64.b64decode(encrypted_message.encode())
        decrypted_message = self.cipher.decrypt(encrypted_message)
        return decrypted_message.decode()
    
    def encrypt_publish(self, channel, exchange, routing_key, body):
        """加密发布消息"""
        encrypted_body = self.encrypt_message(body)
        
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=encrypted_body,
            properties=pika.BasicProperties(
                content_type='application/json',
                headers={'encrypted': True}
            )
        )
    
    def decrypt_consume(self, channel, method, properties, body):
        """解密消费消息"""
        if properties.headers and properties.headers.get('encrypted'):
            return self.decrypt_message(body)
        return body
```

#### 非对称加密
```python
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

class AsymmetricEncryptor:
    """非对称加密器"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_key_pair(self, key_size=2048):
        """生成密钥对"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def encrypt_with_public_key(self, data):
        """使用公钥加密"""
        if not self.public_key:
            raise ValueError("公钥未初始化")
        
        # 加密数据
        encrypted_data = self.public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_with_private_key(self, encrypted_data):
        """使用私钥解密"""
        if not self.private_key:
            raise ValueError("私钥未初始化")
        
        encrypted_data = base64.b64decode(encrypted_data.encode())
        
        # 解密数据
        decrypted_data = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_data.decode()
    
    def export_public_key(self):
        """导出公钥"""
        if not self.public_key:
            raise ValueError("公钥未初始化")
        
        public_key_pem = self.public_key.public_key_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key_pem.decode()
    
    def import_public_key(self, public_key_pem):
        """导入公钥"""
        self.public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
```

### 3. 字段级加密

#### 选择性字段加密
```python
import json
from cryptography.fernet import Fernet

class FieldLevelEncryptor:
    """字段级加密器"""
    
    def __init__(self, key=None):
        self.cipher = Fernet(key or Fernet.generate_key())
        self.encrypt_fields = set()
    
    def add_encrypt_field(self, field_name):
        """添加加密字段"""
        self.encrypt_fields.add(field_name)
    
    def encrypt_message_fields(self, message_data):
        """加密消息字段"""
        encrypted_data = message_data.copy()
        
        for field_name in self.encrypt_fields:
            if field_name in encrypted_data:
                field_value = str(encrypted_data[field_name])
                encrypted_value = self.cipher.encrypt(field_value.encode())
                encrypted_data[field_name] = base64.b64encode(encrypted_value).decode()
                encrypted_data[f'{field_name}_encrypted'] = True
        
        return encrypted_data
    
    def decrypt_message_fields(self, message_data):
        """解密消息字段"""
        decrypted_data = message_data.copy()
        
        for field_name in list(message_data.keys()):
            if f'{field_name}_encrypted' in message_data:
                encrypted_value = base64.b64decode(message_data[field_name].encode())
                decrypted_value = self.cipher.decrypt(encrypted_value).decode()
                decrypted_data[field_name] = decrypted_value
                del decrypted_data[field_name]
                del decrypted_data[f'{field_name}_encrypted']
        
        return decrypted_data

# 使用示例
def secure_message_handler(channel, method, properties, body):
    """安全消息处理器"""
    encryptor = FieldLevelEncryptor()
    encryptor.add_encrypt_field('ssn')
    encryptor.add_encrypt_field('credit_card')
    
    try:
        # 解析消息
        message_data = json.loads(body)
        
        # 解密敏感字段
        decrypted_data = encryptor.decrypt_message_fields(message_data)
        
        # 处理消息
        print(f"处理用户信息: {decrypted_data['user_id']}")
        
        # 确认消息
        channel.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"处理消息失败: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

## 安全审计

### 1. 操作审计

#### 审计记录器
```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityAuditor:
    """安全审计器"""
    
    def __init__(self, log_file='security_audit.log'):
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_authentication_attempt(self, username, success, source_ip, details=None):
        """记录认证尝试"""
        audit_data = {
            'event_type': 'authentication',
            'username': username,
            'success': success,
            'source_ip': source_ip,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(json.dumps(audit_data))
    
    def log_authorization_decision(self, username, action, resource, allowed, reason):
        """记录授权决策"""
        audit_data = {
            'event_type': 'authorization',
            'username': username,
            'action': action,
            'resource': resource,
            'allowed': allowed,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        level = logging.INFO if allowed else logging.WARNING
        self.logger.log(level, json.dumps(audit_data))
    
    def log_message_operation(self, username, operation, exchange, queue, success, details=None):
        """记录消息操作"""
        audit_data = {
            'event_type': 'message_operation',
            'username': username,
            'operation': operation,
            'exchange': exchange,
            'queue': queue,
            'success': success,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(json.dumps(audit_data))
    
    def log_configuration_change(self, username, change_type, resource, old_value, new_value):
        """记录配置变更"""
        audit_data = {
            'event_type': 'configuration_change',
            'username': username,
            'change_type': change_type,
            'resource': resource,
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.warning(json.dumps(audit_data))
    
    def generate_audit_report(self, start_date, end_date):
        """生成审计报告"""
        # 这里可以从日志文件中读取和分析审计数据
        # 实际实现中可能需要日志分析工具
        pass
```

#### 实时监控
```python
import threading
import time
from collections import defaultdict

class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self, auditor, alert_threshold=100):
        self.auditor = auditor
        self.alert_threshold = alert_threshold
        self.failed_attempts = defaultdict(list)
        self.anomaly_detector = AnomalyDetector()
        self.monitoring_thread = None
    
    def start_monitoring(self):
        """启动监控"""
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                self._check_failed_attempts()
                self._detect_anomalies()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(60)
    
    def _check_failed_attempts(self):
        """检查失败尝试"""
        current_time = time.time()
        
        for ip, attempts in self.failed_attempts.items():
            # 清理超时记录
            self.failed_attempts[ip] = [
                attempt_time for attempt_time in attempts
                if current_time - attempt_time < 3600  # 1小时内的尝试
            ]
            
            # 检查是否超过阈值
            if len(self.failed_attempts[ip]) > self.alert_threshold:
                self._raise_security_alert(f"IP地址 {ip} 认证失败次数过多")
    
    def _detect_anomalies(self):
        """检测异常"""
        anomalies = self.anomaly_detector.detect()
        for anomaly in anomalies:
            self._raise_security_alert(f"检测到异常活动: {anomaly}")
    
    def _raise_security_alert(self, message):
        """发出安全警报"""
        alert_data = {
            'alert_type': 'security_threat',
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'high'
        }
        
        print(f"安全警报: {message}")
        # 实际实现中可以发送邮件、短信等通知
        self.auditor.logger.warning(json.dumps(alert_data))

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self):
        self.baseline_stats = {}
    
    def detect(self):
        """检测异常活动"""
        anomalies = []
        
        # 简单的异常检测逻辑
        # 实际实现中可以基于机器学习模型
        current_hour = datetime.now().hour
        
        # 检测非工作时间的访问
        if not (9 <= current_hour <= 17):
            anomalies.append("非工作时间访问")
        
        # 检测大量失败的认证尝试
        # 这里可以从审计日志中分析
        
        return anomalies
```

### 2. 合规性检查

#### 合规性检查器
```python
import re
from typing import List, Dict, Any

class ComplianceChecker:
    """合规性检查器"""
    
    def __init__(self):
        self.compliance_rules = {}
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """设置默认合规规则"""
        # 密码策略
        self.compliance_rules['password_policy'] = self._check_password_policy
        
        # 数据保留策略
        self.compliance_rules['data_retention'] = self._check_data_retention
        
        # 访问控制策略
        self.compliance_rules['access_control'] = self._check_access_control
        
        # 加密策略
        self.compliance_rules['encryption'] = self._check_encryption
    
    def _check_password_policy(self, user_data):
        """检查密码策略"""
        issues = []
        
        password = user_data.get('password', '')
        
        # 检查密码复杂度
        if len(password) < 12:
            issues.append("密码长度不足12位")
        
        if not re.search(r'[A-Z]', password):
            issues.append("密码缺少大写字母")
        
        if not re.search(r'[a-z]', password):
            issues.append("密码缺少小写字母")
        
        if not re.search(r'[0-9]', password):
            issues.append("密码缺少数字")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("密码缺少特殊字符")
        
        # 检查密码历史
        # 这里需要与历史密码比较
        
        return {
            'rule': 'password_policy',
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def _check_data_retention(self, data_config):
        """检查数据保留策略"""
        issues = []
        
        retention_days = data_config.get('retention_days', 0)
        
        if retention_days > 90:  # 示例：90天保留期
            issues.append(f"数据保留期过长: {retention_days}天")
        
        # 检查数据是否有过期删除策略
        if not data_config.get('auto_delete', False):
            issues.append("缺少自动删除策略")
        
        return {
            'rule': 'data_retention',
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def _check_access_control(self, permissions):
        """检查访问控制策略"""
        issues = []
        
        # 检查是否使用了root权限
        if 'root' in permissions.get('tags', ''):
            issues.append("不应使用root权限")
        
        # 检查是否有过度权限
        if permissions.get('configure') == '.*':
            issues.append("配置权限过于宽泛")
        
        if permissions.get('write') == '.*':
            issues.append("写入权限过于宽泛")
        
        return {
            'rule': 'access_control',
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def _check_encryption(self, encryption_config):
        """检查加密策略"""
        issues = []
        
        # 检查是否启用了TLS
        if not encryption_config.get('tls_enabled', False):
            issues.append("未启用TLS加密")
        
        # 检查证书是否有效
        cert_info = encryption_config.get('certificate', {})
        if cert_info.get('expires_within_days', 0) < 30:
            issues.append("证书即将过期")
        
        # 检查加密算法强度
        cipher_suite = encryption_config.get('cipher_suite', '')
        weak_ciphers = ['RC4', 'DES', '3DES']
        
        for weak_cipher in weak_ciphers:
            if weak_cipher in cipher_suite:
                issues.append(f"使用了弱加密算法: {weak_cipher}")
        
        return {
            'rule': 'encryption',
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def run_compliance_check(self, check_data):
        """运行合规性检查"""
        results = {}
        
        for rule_name, check_function in self.compliance_rules.items():
            result = check_function(check_data)
            results[rule_name] = result
        
        # 计算总体合规性
        overall_compliant = all(result['compliant'] for result in results.values())
        
        return {
            'overall_compliant': overall_compliant,
            'rules': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_compliance_report(self, check_results):
        """生成合规性报告"""
        report = {
            'report_type': 'compliance_check',
            'timestamp': datetime.utcnow().isoformat(),
            'compliance_summary': {
                'overall_compliant': check_results['overall_compliant'],
                'total_rules': len(check_results['rules']),
                'compliant_rules': sum(1 for r in check_results['rules'].values() if r['compliant']),
                'non_compliant_rules': sum(1 for r in check_results['rules'].values() if not r['compliant'])
            },
            'rule_details': check_results['rules']
        }
        
        return report
```

## 安全最佳实践

### 1. 密码管理

#### 密码策略实施
```python
import secrets
import string
from typing import List

class PasswordManager:
    """密码管理器"""
    
    def __init__(self):
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special_chars = True
        self.password_history = set()
    
    def generate_strong_password(self) -> str:
        """生成强密码"""
        while True:
            password = self._generate_password()
            if self.is_password_strong(password) and password not in self.password_history:
                self.password_history.add(password)
                return password
    
    def _generate_password(self) -> str:
        """生成随机密码"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*(),.?\":{}|<>"
        
        # 确保密码包含所有必需字符类型
        password = []
        
        if self.require_uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if self.require_lowercase:
            password.append(secrets.choice(string.ascii_lowercase))
        if self.require_digits:
            password.append(secrets.choice(string.digits))
        if self.require_special_chars:
            password.append(secrets.choice("!@#$%^&*(),.?\":{}|<>"))
        
        # 填充剩余长度
        remaining_length = max(self.min_length - len(password), 8)
        for _ in range(remaining_length):
            password.append(secrets.choice(alphabet))
        
        # 打乱字符顺序
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def is_password_strong(self, password: str) -> List[str]:
        """检查密码强度"""
        issues = []
        
        if len(password) < self.min_length:
            issues.append(f"密码长度至少{self.min_length}位")
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            issues.append("密码必须包含大写字母")
        
        if self.require_lowercase and not any(c.islower() for c in password):
            issues.append("密码必须包含小写字母")
        
        if self.require_digits and not any(c.isdigit() for c in password):
            issues.append("密码必须包含数字")
        
        if self.require_special_chars and not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            issues.append("密码必须包含特殊字符")
        
        # 检查常见密码模式
        if self._is_common_pattern(password):
            issues.append("密码包含常见模式，不够安全")
        
        return issues
    
    def _is_common_pattern(self, password: str) -> bool:
        """检查是否包含常见模式"""
        common_patterns = [
            '123456', 'password', 'qwerty', 'admin',
            password.lower().replace('a', '4').replace('e', '3').replace('i', '1'),
        ]
        
        password_lower = password.lower()
        
        for pattern in common_patterns:
            if pattern in password_lower:
                return True
        
        return False
    
    def rotate_password(self, current_password: str) -> str:
        """密码轮换"""
        # 检查密码是否需要轮换
        if self._should_rotate_password(current_password):
            return self.generate_strong_password()
        return current_password
    
    def _should_rotate_password(self, password: str) -> bool:
        """检查是否需要轮换密码"""
        # 这里可以实现基于时间的密码轮换逻辑
        # 例如：每90天轮换一次
        # 实际实现需要存储密码创建时间
        return False  # 简化实现
```

### 2. 安全配置模板

#### 安全配置生成器
```python
import yaml

class SecurityConfigGenerator:
    """安全配置生成器"""
    
    def generate_rabbitmq_config(self, config_params):
        """生成RabbitMQ安全配置"""
        config = {
            'rabbitmq': {
                'auth_backends': ['rabbit_auth_backend_internal'],
                'default_user': '',
                'default_pass': '',
                'loopback_users': []
            },
            'ssl': {
                'enabled': True,
                'certfile': config_params.get('certfile'),
                'keyfile': config_params.get('keyfile'),
                'cacertfile': config_params.get('cacertfile'),
                'fail_if_no_peer_cert': True,
                'verify': 'verify_peer'
            },
            'log_levels': {
                'connection': 'info',
                'authentication': 'info',
                'authorization': 'info'
            },
            'memory': {
                'vm_memory_high_watermark': 0.6,
                'vm_memory_high_watermark_paging_ratio': 0.5
            },
            'disk': {
                'disk_free_limit': {'absolute': '10GB'}
            }
        }
        
        return config
    
    def generate_docker_compose_security(self, vhosts, users):
        """生成安全的Docker Compose配置"""
        compose_config = {
            'version': '3.8',
            'services': {
                'rabbitmq': {
                    'image': 'rabbitmq:3.8-management',
                    'environment': {
                        'RABBITMQ_DEFAULT_USER': users['admin']['username'],
                        'RABBITMQ_DEFAULT_PASS': users['admin']['password'],
                        'RABBITMQ_DEFAULT_VHOST': vhosts['production']['name']
                    },
                    'ports': [
                        '5671:5671',  # SSL端口
                        '15671:15671' # 管理SSL端口
                    ],
                    'volumes': [
                        './rabbitmq-data:/var/lib/rabbitmq',
                        './ssl:/etc/ssl/certs:ro'
                    ],
                    'networks': ['rabbitmq-net'],
                    'healthcheck': {
                        'test': ['CMD-SHELL', 'rabbitmq-diagnostics -q ping'],
                        'interval': '30s',
                        'timeout': '30s',
                        'retries': 3
                    }
                }
            },
            'networks': {
                'rabbitmq-net': {
                    'driver': 'bridge',
                    'internal': True
                }
            },
            'volumes': {
                'rabbitmq-data': {
                    'driver': 'local'
                }
            }
        }
        
        return compose_config
    
    def generate_k8s_security_policy(self):
        """生成Kubernetes安全策略"""
        security_policy = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'NetworkPolicy',
            'metadata': {
                'name': 'rabbitmq-network-policy'
            },
            'spec': {
                'podSelector': {
                    'matchLabels': {
                        'app': 'rabbitmq'
                    }
                },
                'policyTypes': [
                    'Ingress',
                    'Egress'
                ],
                'ingress': [
                    {
                        'from': [
                            {
                                'namespaceSelector': {
                                    'matchLabels': {
                                        'name': 'messaging'
                                    }
                                }
                            }
                        ],
                        'ports': [
                            {
                                'protocol': 'TCP',
                                'port': 5672
                            },
                            {
                                'protocol': 'TCP',
                                'port': 15672
                            }
                        ]
                    }
                ],
                'egress': [
                    {
                        'to': [],
                        'ports': [
                            {
                                'protocol': 'TCP',
                                'port': 53
                            },
                            {
                                'protocol': 'UDP',
                                'port': 53
                            }
                        ]
                    }
                ]
            }
        }
        
        return security_policy
    
    def save_config(self, config, filename, format='yaml'):
        """保存配置"""
        if format == 'yaml':
            with open(filename, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        elif format == 'json':
            import json
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
        else:
            raise ValueError(f"不支持的格式: {format}")
```

## 安全威胁防护

### 1. DDoS防护

#### 连接限制器
```python
import time
import threading
from collections import defaultdict, deque
from typing import Set

class ConnectionRateLimiter:
    """连接速率限制器"""
    
    def __init__(self, max_connections_per_minute=100):
        self.max_connections_per_minute = max_connections_per_minute
        self.connection_counts = defaultdict(deque)
        self.blocked_ips = set()
        self.lock = threading.Lock()
    
    def is_connection_allowed(self, source_ip: str) -> bool:
        """检查连接是否被允许"""
        current_time = time.time()
        
        with self.lock:
            # 检查IP是否被封禁
            if source_ip in self.blocked_ips:
                return False
            
            # 清理过期的连接记录
            self._cleanup_old_connections(source_ip, current_time)
            
            # 检查当前连接速率
            recent_connections = len(self.connection_counts[source_ip])
            
            if recent_connections >= self.max_connections_per_minute:
                # 超过限制，封禁IP
                self._block_ip(source_ip)
                return False
            
            # 记录新的连接
            self.connection_counts[source_ip].append(current_time)
            return True
    
    def _cleanup_old_connections(self, source_ip: str, current_time: float):
        """清理过期的连接记录"""
        cutoff_time = current_time - 60  # 1分钟前
        
        # 清理过期的连接
        while (self.connection_counts[source_ip] and 
               self.connection_counts[source_ip][0] < cutoff_time):
            self.connection_counts[source_ip].popleft()
        
        # 如果没有连接记录，删除该IP的记录以节省内存
        if not self.connection_counts[source_ip]:
            del self.connection_counts[source_ip]
    
    def _block_ip(self, source_ip: str, block_duration: int = 3600):
        """封禁IP地址"""
        self.blocked_ips.add(source_ip)
        
        # 定时解除封禁
        def unblock():
            time.sleep(block_duration)
            self.blocked_ips.discard(source_ip)
        
        thread = threading.Thread(target=unblock)
        thread.daemon = True
        thread.start()
    
    def get_connection_stats(self) -> dict:
        """获取连接统计"""
        with self.lock:
            stats = {
                'blocked_ips': len(self.blocked_ips),
                'active_ips': len(self.connection_counts),
                'recent_connections': sum(len(connections) for connections in self.connection_counts.values())
            }
            return stats
```

### 2. 消息注入防护

#### 消息验证器
```python
import re
import json
from typing import Any, Dict, List

class MessageValidator:
    """消息验证器"""
    
    def __init__(self):
        self.forbidden_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',  # JavaScript协议
            r'vbscript:',   # VBScript协议
            r'data:text/html',  # HTML数据协议
            r'\.\./',  # 路径遍历
            r';.*;(DROP|DELETE|INSERT|UPDATE|SELECT)',  # SQL注入
        ]
        self.max_message_size = 1024 * 1024  # 1MB
        self.allowed_content_types = {
            'application/json',
            'text/plain',
            'application/xml',
            'text/xml'
        }
    
    def validate_message(self, message: str, content_type: str = 'text/plain') -> Dict[str, Any]:
        """验证消息"""
        validation_result = {
            'valid': True,
            'issues': [],
            'sanitized_message': message
        }
        
        # 检查消息大小
        if len(message.encode('utf-8')) > self.max_message_size:
            validation_result['valid'] = False
            validation_result['issues'].append('消息大小超出限制')
        
        # 检查内容类型
        if content_type not in self.allowed_content_types:
            validation_result['valid'] = False
            validation_result['issues'].append(f'不支持的内容类型: {content_type}')
        
        # 检查禁止的模式
        for pattern in self.forbidden_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                validation_result['valid'] = False
                validation_result['issues'].append(f'检测到禁止的模式: {pattern}')
                break
        
        # 如果是JSON消息，验证JSON结构
        if content_type == 'application/json':
            json_validation = self._validate_json_structure(message)
            if not json_validation['valid']:
                validation_result['valid'] = False
                validation_result['issues'].extend(json_validation['issues'])
        
        # 消息清理
        if validation_result['valid']:
            validation_result['sanitized_message'] = self._sanitize_message(message, content_type)
        
        return validation_result
    
    def _validate_json_structure(self, message: str) -> Dict[str, Any]:
        """验证JSON结构"""
        try:
            data = json.loads(message)
            
            issues = []
            
            # 递归检查JSON数据
            self._validate_json_data(data, issues)
            
            return {
                'valid': len(issues) == 0,
                'issues': issues
            }
        except json.JSONDecodeError:
            return {
                'valid': False,
                'issues': ['JSON格式错误']
            }
    
    def _validate_json_data(self, data: Any, issues: List[str], path: str = 'root'):
        """递归验证JSON数据"""
        if isinstance(data, dict):
            for key, value in data.items():
                # 检查键名
                if not isinstance(key, str) or not key.strip():
                    issues.append(f'无效的键名: {path}.{key}')
                elif len(key) > 100:
                    issues.append(f'键名过长: {path}.{key}')
                
                # 递归验证值
                self._validate_json_data(value, issues, f'{path}.{key}')
        
        elif isinstance(data, list):
            if len(data) > 1000:  # 限制数组长度
                issues.append(f'数组过长: {path}')
            
            for i, item in enumerate(data):
                self._validate_json_data(item, issues, f'{path}[{i}]')
        
        elif isinstance(data, str):
            if len(data) > 10000:  # 限制字符串长度
                issues.append(f'字符串过长: {path}')
            
            # 检查特殊字符
            dangerous_chars = ['<', '>', '&', '"', "'", '\x00']
            for char in dangerous_chars:
                if char in data:
                    issues.append(f'包含危险字符: {path}')
                    break
    
    def _sanitize_message(self, message: str, content_type: str) -> str:
        """清理消息"""
        if content_type == 'text/plain':
            # 移除潜在的HTML标签
            message = re.sub(r'<[^>]+>', '', message)
            # 移除JavaScript协议
            message = re.sub(r'javascript:[^"\']*', '', message, flags=re.IGNORECASE)
        
        elif content_type == 'application/json':
            # JSON消息的清理
            try:
                data = json.loads(message)
                sanitized_data = self._sanitize_json_data(data)
                return json.dumps(sanitized_data, ensure_ascii=False)
            except:
                return message
        
        return message
    
    def _sanitize_json_data(self, data: Any) -> Any:
        """清理JSON数据"""
        if isinstance(data, dict):
            return {k: self._sanitize_json_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_json_data(item) for item in data]
        elif isinstance(data, str):
            # 移除危险字符
            return data.replace('<', '&lt;').replace('>', '&gt;')
        else:
            return data
```

### 3. 安全监控告警

#### 安全事件管理器
```python
from typing import Callable, Dict, Any
from enum import Enum
import asyncio
import threading

class SecurityAlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventManager:
    """安全事件管理器"""
    
    def __init__(self):
        self.alert_handlers: Dict[SecurityAlertLevel, List[Callable]] = defaultdict(list)
        self.event_queue = asyncio.Queue()
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def register_alert_handler(self, level: SecurityAlertLevel, handler: Callable):
        """注册告警处理器"""
        self.alert_handlers[level].append(handler)
    
    def report_security_event(self, event_type: str, level: SecurityAlertLevel, 
                            message: str, context: Dict[str, Any] = None):
        """报告安全事件"""
        event = {
            'type': event_type,
            'level': level,
            'message': message,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
            'id': str(uuid.uuid4())
        }
        
        # 放入事件队列
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(self.event_queue.put_nowait, event)
        except RuntimeError:
            # 没有事件循环，直接处理
            self._handle_event_sync(event)
    
    def start_monitoring(self):
        """启动监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event_sync(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"处理安全事件时出错: {e}")
    
    def _handle_event_sync(self, event):
        """同步处理事件"""
        level = SecurityAlertLevel(event['level'])
        
        # 调用相应的处理器
        handlers = self.alert_handlers[level]
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"告警处理器错误: {e}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

# 安全监控集成示例
class RabbitMQQSecurityMonitor:
    """RabbitMQ安全监控"""
    
    def __init__(self, connection):
        self.connection = connection
        self.event_manager = SecurityEventManager()
        self.setup_default_handlers()
    
    def setup_default_handlers(self):
        """设置默认告警处理器"""
        
        def email_alert_handler(event):
            """邮件告警处理器"""
            # 这里可以实现邮件发送逻辑
            print(f"邮件告警: {event['message']}")
        
        def sms_alert_handler(event):
            """短信告警处理器"""
            # 这里可以实现短信发送逻辑
            if event['level'] in [SecurityAlertLevel.HIGH, SecurityAlertLevel.CRITICAL]:
                print(f"短信告警: {event['message']}")
        
        def log_alert_handler(event):
            """日志告警处理器"""
            logging.warning(f"安全事件: {json.dumps(event)}")
        
        # 注册处理器
        self.event_manager.register_alert_handler(SecurityAlertLevel.LOW, log_alert_handler)
        self.event_manager.register_alert_handler(SecurityAlertLevel.MEDIUM, log_alert_handler)
        self.event_manager.register_alert_handler(SecurityAlertLevel.HIGH, email_alert_handler)
        self.event_manager.register_alert_handler(SecurityAlertLevel.CRITICAL, sms_alert_handler)
        self.event_manager.register_alert_handler(SecurityAlertLevel.CRITICAL, log_alert_handler)
    
    def start_security_monitoring(self):
        """启动安全监控"""
        self.event_manager.start_monitoring()
        
        # 开始监控RabbitMQ连接
        threading.Thread(target=self._monitor_rabbitmq_connections).start()
    
    def _monitor_rabbitmq_connections(self):
        """监控RabbitMQ连接"""
        while True:
            try:
                # 获取连接信息
                connections = self._get_rabbitmq_connections()
                
                # 检测异常连接
                for connection in connections:
                    self._analyze_connection(connection)
                
                time.sleep(30)  # 每30秒检查一次
            except Exception as e:
                print(f"监控RabbitMQ连接时出错: {e}")
                time.sleep(60)
    
    def _get_rabbitmq_connections(self):
        """获取RabbitMQ连接信息"""
        # 这里需要实现获取连接信息的逻辑
        # 可以通过RabbitMQ Management API或直接查询
        return []
    
    def _analyze_connection(self, connection):
        """分析连接"""
        # 检查连接来源
        source_ip = connection.get('peer_host')
        
        # 检查连接时间
        connected_at = connection.get('connected_at')
        
        # 检查是否可疑
        if self._is_suspicious_connection(connection):
            self.event_manager.report_security_event(
                'suspicious_connection',
                SecurityAlertLevel.MEDIUM,
                f'检测到可疑连接: {source_ip}',
                {'connection': connection}
            )
    
    def _is_suspicious_connection(self, connection) -> bool:
        """判断连接是否可疑"""
        # 实现可疑连接检测逻辑
        peer_host = connection.get('peer_host', '')
        
        # 检查是否来自内部网络
        if peer_host.startswith(('10.', '192.168.', '172.')):
            return False
        
        # 检查连接时间是否在非工作时间
        connected_at = connection.get('connected_at')
        if connected_at:
            hour = datetime.fromtimestamp(connected_at).hour
            if not (9 <= hour <= 17):
                return True
        
        return False
```

## 安全检查清单

### 1. 认证安全
- [ ] 使用强密码策略（12位以上，包含大小写字母、数字、特殊字符）
- [ ] 启用多因素认证
- [ ] 定期轮换认证令牌
- [ ] 禁用默认账户和密码
- [ ] 实现账户锁定机制
- [ ] 记录所有认证尝试

### 2. 授权安全
- [ ] 实施最小权限原则
- [ ] 定期审查用户权限
- [ ] 使用角色基于的访问控制
- [ ] 隔离不同环境的权限
- [ ] 审计权限变更操作

### 3. 数据安全
- [ ] 启用TLS/SSL加密
- [ ] 使用强加密算法
- [ ] 定期更新SSL证书
- [ ] 实施数据分类和标记
- [ ] 加密敏感消息内容
- [ ] 安全存储加密密钥

### 4. 网络安全
- [ ] 使用防火墙规则限制访问
- [ ] 隔离管理界面
- [ ] 禁用不必要的网络协议
- [ ] 实施网络监控
- [ ] 配置入侵检测系统

### 5. 运维安全
- [ ] 启用安全日志记录
- [ ] 定期进行安全审计
- [ ] 实施变更管理流程
- [ ] 建立备份和恢复计划
- [ ] 进行安全培训

### 6. 监控和告警
- [ ] 实施实时安全监控
- [ ] 配置异常行为告警
- [ ] 建立安全事件响应流程
- [ ] 定期进行渗透测试
- [ ] 维护威胁情报更新

## 总结

RabbitMQ安全与权限管理是一个复杂而重要的主题。本章我们详细探讨了：

1. **认证机制**：从基础的用户名密码到企业级LDAP和OAuth 2.0
2. **权限管理**：细粒度的访问控制和角色管理
3. **数据加密**：传输层和消息内容的加密保护
4. **安全审计**：全面的操作记录和合规性检查
5. **威胁防护**：DDoS防护、消息验证和安全监控

通过实施这些安全措施，可以显著提高RabbitMQ系统的安全性和可靠性，保护敏感数据和关键业务操作。记住，安全是一个持续的过程，需要定期评估和改进。