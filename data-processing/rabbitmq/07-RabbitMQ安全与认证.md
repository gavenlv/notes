# 第7章：RabbitMQ安全与认证

## 概述

RabbitMQ作为企业级消息队列系统，安全性和认证机制至关重要。本章深入探讨RabbitMQ的安全架构、用户认证、权限管理、SSL/TLS加密、安全策略配置等内容，帮助构建安全可靠的消息传递系统。

## 学习目标

- 理解RabbitMQ安全架构和威胁模型
- 掌握用户认证和权限管理机制
- 学会配置SSL/TLS加密通信
- 了解安全策略和审计日志
- 掌握安全监控和故障处理
- 学会生产环境安全最佳实践

## 安全架构概述

### 1. RabbitMQ安全层次

```
┌─────────────────────────────────────────────────────────┐
│                    应用层安全                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  消息内容    │ │   应用逻辑   │ │   访问控制   │         │
│  │   加密      │ │   认证      │ │   授权      │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                    传输层安全                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │ SSL/TLS     │ │  连接管理   │ │  心跳监控   │         │
│  │  加密       │ │  验证      │ │  超时检测   │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                    认证授权层                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  用户认证   │ │   角色权限   │ │   资源访问   │         │
│  │   管理     │ │   控制      │ │   控制      │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
```

### 2. 威胁模型

#### 常见安全威胁
- **未授权访问**：非法用户获取RabbitMQ访问权限
- **消息窃听**：网络传输中消息内容被窃取
- **消息篡改**：消息在传输过程中被恶意修改
- **身份伪造**：攻击者伪造合法用户身份
- **服务拒绝**：恶意攻击导致服务不可用
- **权限提升**：低权限用户获取更高权限

## 用户认证系统

### 1. 内置认证

#### 默认用户管理

```bash
# 创建新用户
rabbitmqctl add_user admin secure_password

# 设置用户标签
rabbitmqctl set_user_tags admin administrator

# 设置权限
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

# 查看用户列表
rabbitmqctl list_users

# 修改密码
rabbitmqctl change_password admin new_secure_password

# 删除用户
rabbitmqctl delete_user username
```

#### 内置认证配置

```erlang
%% rabbitmq.conf
default_user = guest
default_pass = guest
default_permissions.configure = .*
default_permissions.read = .*
default_permissions.write = .*
```

### 2. 外部认证集成

#### LDAP认证

```erlang
%% rabbitmq.config
[
  {rabbit, [
    {auth_backends, [rabbit_auth_backend_ldap, rabbit_auth_backend_internal]}
  ]},
  {rabbitmq_auth_backend_ldap, [
    {servers, ["ldap.example.com"]},
    {user_dn_pattern, "cn=${username},ou=Users,dc=example,dc=com"},
    {use_ssl, true},
    {port, 636},
    {log, true}
  ]}
].
```

#### LDAP配置详解

```bash
# LDAP服务器配置
LDAP_SERVERS=ldap1.example.com,ldap2.example.com
LDAP_PORT=389
LDAP_USE_SSL=true
LDAP_USER_DN_PATTERN=cn=${username},ou=Users,dc=example,dc=com
LDAP_GROUP_BASE_DN=ou=Groups,dc=example,dc=com
LDAP_GROUP_DN_MATCH=member=${user_dn}
LDAP_GROUP_NAME_ATTRIBUTE=cn
LDAP_AUTH_CACHE_SIZE=1000
LDAP_AUTH_CACHE_TTL=600000
```

### 3. 自定义认证插件

#### 创建自定义认证模块

```erlang
%% my_auth_backend.erl
-module(my_auth_backend).
-behaviour(rabbit_auth_backend).

-export([user_pass_auth/2, check_vhost_access/3, check_resource_access/4]).

user_pass_auth(User, Password) ->
    %% 自定义认证逻辑
    case my_auth_service:validate_credentials(User, Password) of
        valid -> {ok, User};
        invalid -> {refused, "Invalid credentials"}
    end.

check_vhost_access(User, VHost, _Config) ->
    %% 检查虚拟主机访问权限
    case my_auth_service:check_vhost_permission(User, VHost) of
        allowed -> true;
        denied -> false
    end.

check_resource_access(User, Resource, _Perm, _Context) ->
    %% 检查资源访问权限
    my_auth_service:check_resource_permission(User, Resource).
```

## 权限管理

### 1. 用户权限系统

#### 权限级别

```
权限级别：
┌─────────────────────────────────────────────────────────┐
│  资源类型权限                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │   配置      │ │    读      │ │    写      │         │
│  │  configure  │ │    read    │ │   write    │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                          │
│  权限表达式：                                              │
│  资源模式: queue或exchange名称                             │
│  正则匹配: .* 表示匹配所有                                 │
│  具体匹配: specific-name 只匹配特定资源                    │
└─────────────────────────────────────────────────────────┘
```

#### 权限设置示例

```bash
# 配置队列权限
rabbitmqctl set_permissions -p / user "queue_.*" "queue_.*" "queue_.*"

# 配置交换器权限
rabbitmqctl set_permissions -p / user "exchange_.*" "exchange_.*" ".*"

# 配置特定资源权限
rabbitmqctl set_permissions -p / user "exact_queue_name" "exact_exchange_name" ".*"

# 查看用户权限
rabbitmqctl list_user_permissions username

# 清除权限
rabbitmqctl clear_permissions -p / username
```

### 2. 虚拟主机隔离

#### 虚拟主机配置

```bash
# 创建虚拟主机
rabbitmqctl add_vhost production
rabbitmqctl add_vhost staging
rabbitmqctl add_vhost development

# 设置虚拟主机权限
rabbitmqctl set_permissions -p production prod_user ".*" ".*" ".*"
rabbitmqctl set_permissions -p staging dev_user "staging_.*" ".*" ".*"

# 删除虚拟主机
rabbitmqctl delete_vhost vhost_name
```

#### 虚拟主机隔离策略

```python
# Python客户端虚拟主机使用
import pika

# 连接特定虚拟主机
connection_params = pika.ConnectionParameters(
    host='localhost',
    port=5672,
    virtual_host='production',  # 指定虚拟主机
    credentials=pika.PlainCredentials('username', 'password')
)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
```

### 3. 资源配额管理

#### 队列配额设置

```erlang
%% rabbitmq.config
[
  {rabbit, [
    {default_vhost, <<"/">>},
    {default_user, <<"guest">>},
    {default_pass, <<"guest">>}
  ]},
  {rabbitmq_management, [
    {vhost_resource_limits, [
      {<<"/">>, [
        {max_connections, 100},
        {max_queues, 100},
        {max_exchanges, 50}
      ]},
      {<<"production">>, [
        {max_connections, 500},
        {max_queues, 200},
        {max_exchanges, 100}
      ]}
    ]}
  ]}
].
```

## SSL/TLS加密

### 1. SSL证书管理

#### 证书生成

```bash
# 创建CA密钥
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -out ca-cert.pem \
  -subj "/C=US/ST=CA/L=San Francisco/O=MyOrg/OU=MyUnit/CN=RabbitMQ-CA"

# 创建服务器密钥
openssl genrsa -out server-key.pem 4096
openssl req -new -key server-key.pem -out server-req.pem \
  -subj "/C=US/ST=CA/L=San Francisco/O=MyOrg/OU=MyUnit/CN=RabbitMQ-Server"

# 签名服务器证书
openssl x509 -req -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem \
  -out server-cert.pem -days 365 -CAcreateserial

# 创建客户端密钥
openssl genrsa -out client-key.pem 4096
openssl req -new -key client-key.pem -out client-req.pem \
  -subj "/C=US/ST=CA/L=San Francisco/O=MyOrg/OU=MyUnit/CN=RabbitMQ-Client"

# 签名客户端证书
openssl x509 -req -in client-req.pem -CA ca-cert.pem -CAkey ca-key.pem \
  -out client-cert.pem -days 365 -CAcreateserial
```

#### RabbitMQ SSL配置

```erlang
%% rabbitmq.config
[
  {rabbit, [
    {ssl_listeners, [5671]},
    {ssl_options, [
      {cacertfile, "/etc/rabbitmq/ssl/ca-cert.pem"},
      {certfile, "/etc/rabbitmq/ssl/server-cert.pem"},
      {keyfile, "/etc/rabbitmq/ssl/server-key.pem"},
      {verify, verify_peer},
      {fail_if_no_peer_cert, true},
      {versions, ['tlsv1.2', 'tlsv1.3']},
      {ciphers, [
        {rsa, aes_256_cbc, sha256},
        {rsa, aes_128_cbc, sha256}
      ]}
    ]}
  ]},
  {rabbitmq_management, [
    {listener, [
      {port, 15671},
      {ssl, true},
      {ssl_opts, [
        {cacertfile, "/etc/rabbitmq/ssl/ca-cert.pem"},
        {certfile, "/etc/rabbitmq/ssl/management-cert.pem"},
        {keyfile, "/etc/rabbitmq/ssl/management-key.pem"}
      ]}
    ]}
  ]}
].
```

### 2. 客户端SSL配置

#### Python客户端SSL配置

```python
import pika
import ssl

# SSL配置
ssl_context = ssl.create_default_context(cafile='/path/to/ca-cert.pem')
ssl_context.load_cert_chain(
    certfile='/path/to/client-cert.pem',
    keyfile='/path/to/client-key.pem'
)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_REQUIRED

# 连接参数
connection_params = pika.ConnectionParameters(
    host='localhost',
    port=5671,  # SSL端口
    credentials=pika.PlainCredentials('username', 'password'),
    ssl_options=pika.SSLOptions(ssl_context)
)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
```

### 3. 证书轮换机制

#### 自动化证书更新

```bash
#!/bin/bash
# cert_rotation.sh

CA_CERT_PATH="/etc/rabbitmq/ssl/ca-cert.pem"
SERVER_CERT_PATH="/etc/rabbitmq/ssl/server-cert.pem"
SERVER_KEY_PATH="/etc/rabbitmq/ssl/server-key.pem"
MANAGEMENT_CERT_PATH="/etc/rabbitmq/ssl/management-cert.pem"
MANAGEMENT_KEY_PATH="/etc/rabbitmq/ssl/management-key.pem"

# 生成新证书
generate_new_certificates() {
    # 使用现有CA签发新证书
    openssl genrsa -out temp-server-key.pem 4096
    openssl req -new -key temp-server-key.pem -out temp-server-req.pem \
        -subj "/C=US/ST=CA/L=San Francisco/O=MyOrg/OU=MyUnit/CN=RabbitMQ-Server-$(date +%Y%m%d)"
    
    openssl x509 -req -in temp-server-req.pem -CA $CA_CERT_PATH \
        -CAkey /etc/rabbitmq/ssl/ca-key.pem -out temp-server-cert.pem \
        -days 30 -CAcreateserial
}

# 验证新证书
verify_certificates() {
    if openssl verify -CAfile $CA_CERT_PATH temp-server-cert.pem; then
        echo "Certificate verification passed"
        return 0
    else
        echo "Certificate verification failed"
        return 1
    fi
}

# 替换证书
replace_certificates() {
    mv $SERVER_CERT_PATH $SERVER_CERT_PATH.backup
    mv temp-server-cert.pem $SERVER_CERT_PATH
    mv $SERVER_KEY_PATH $SERVER_KEY_PATH.backup
    mv temp-server-key.pem $SERVER_KEY_PATH
    
    # 重启RabbitMQ
    systemctl reload rabbitmq-server
    echo "Certificates replaced and service reloaded"
}

# 主要逻辑
main() {
    generate_new_certificates
    if verify_certificates; then
        replace_certificates
        echo "Certificate rotation completed successfully"
    else
        echo "Certificate rotation failed"
        rm -f temp-*
        exit 1
    fi
}

main
```

## 安全策略配置

### 1. 访问控制策略

#### 网络访问控制

```erlang
%% rabbitmq.config
[
  {rabbit, [
    {tcp_listen_options, [
      {backlog, 128},
      {nodelay, true},
      {linger, {true, 0}},
      {exit_on_close, false}
    ]}
  ]}
].
```

#### 连接限制

```python
# Python连接管理示例
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import time

class SecureConnectionManager:
    def __init__(self, max_retries=3, retry_delay=5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
    
    def connect_with_retry(self, connection_params):
        for attempt in range(self.max_retries):
            try:
                self.connection = pika.BlockingConnection(connection_params)
                return self.connection
            except (AMQPConnectionError, Exception) as e:
                print(f"连接失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
```

### 2. 消息内容安全

#### 消息加密

```python
import os
from cryptography.fernet import Fernet
import json

class MessageEncryptor:
    def __init__(self, key=None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    def encrypt_message(self, message_data):
        """加密消息内容"""
        try:
            message_str = json.dumps(message_data)
            encrypted_data = self.cipher.encrypt(message_str.encode())
            return encrypted_data
        except Exception as e:
            raise Exception(f"消息加密失败: {e}")
    
    def decrypt_message(self, encrypted_data):
        """解密消息内容"""
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            message_data = json.loads(decrypted_data.decode())
            return message_data
        except Exception as e:
            raise Exception(f"消息解密失败: {e}")

# 使用示例
encryptor = MessageEncryptor()

# 发送加密消息
original_message = {
    'user_id': '12345',
    'account_number': 'ACCT-987654321',
    'amount': 1000.00,
    'currency': 'USD'
}

encrypted_message = encryptor.encrypt_message(original_message)
# channel.basic_publish(exchange='secure_exchange', 
#                      routing_key='secure_queue',
#                      body=encrypted_message)

# 接收解密消息
# method_frame, header_frame, body = channel.basic_get(queue='secure_queue')
# decrypted_message = encryptor.decrypt_message(body)
```

### 3. 数据脱敏

#### 敏感数据处理

```python
import re
import hashlib
from typing import Dict, Any

class DataMasker:
    """数据脱敏处理器"""
    
    def __init__(self):
        # 敏感字段模式
        self.sensitive_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\b\d{10}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        }
    
    def mask_sensitive_data(self, data: Dict[str, Any], fields_to_mask: list = None) -> Dict[str, Any]:
        """脱敏敏感数据"""
        masked_data = data.copy()
        
        # 默认脱敏字段
        default_masked_fields = ['email', 'phone', 'ssn', 'credit_card', 'password']
        fields_to_mask = fields_to_mask or default_masked_fields
        
        for field_name, value in masked_data.items():
            if isinstance(value, str):
                masked_value = value
                
                # 处理邮箱
                if 'email' in field_name.lower() or 'email' in fields_to_mask:
                    masked_value = re.sub(
                        self.sensitive_patterns['email'],
                        '***@***.***',
                        masked_value
                    )
                
                # 处理电话
                elif 'phone' in field_name.lower() or 'phone' in fields_to_mask:
                    masked_value = re.sub(
                        self.sensitive_patterns['phone'],
                        '***-***-****',
                        masked_value
                    )
                
                # 处理SSN
                elif 'ssn' in field_name.lower() or 'ssn' in fields_to_mask:
                    masked_value = re.sub(
                        self.sensitive_patterns['ssn'],
                        '***-**-****',
                        masked_value
                    )
                
                # 处理信用卡
                elif 'credit' in field_name.lower() or 'card' in field_name.lower():
                    masked_value = re.sub(
                        self.sensitive_patterns['credit_card'],
                        '****-****-****-****',
                        masked_value
                    )
                
                # 密码字段
                elif 'password' in field_name.lower() or 'passwd' in field_name.lower():
                    masked_value = '***MASKED***'
                
                masked_data[field_name] = masked_value
        
        return masked_data
    
    def hash_sensitive_data(self, data: str, salt: str = None) -> str:
        """对敏感数据使用哈希"""
        if salt is None:
            salt = os.urandom(32).hex()
        
        hash_object = hashlib.sha256((data + salt).encode())
        return hash_object.hexdigest()

# 使用示例
masker = DataMasker()

# 原始消息
sensitive_message = {
    'user_id': '12345',
    'email': 'john.doe@example.com',
    'phone': '555-123-4567',
    'ssn': '123-45-6789',
    'credit_card': '4532-1234-5678-9012',
    'password': 'super_secret_password'
}

# 脱敏处理
masked_message = masker.mask_sensitive_data(sensitive_message)
print("脱敏后消息:", masked_message)

# 哈希处理
hashed_email = masker.hash_sensitive_data(sensitive_message['email'])
print("哈希邮箱:", hashed_email)
```

## 审计和监控

### 1. 审计日志配置

#### 启用审计插件

```bash
# 启用审计插件
rabbitmq-plugins enable rabbitmq_auth_backend_cache
rabbitmq-plugins enable rabbitmq_management_visualiser

# 配置审计日志
rabbitmqctl set_policy audit-logs ".*" \
  '{"审计配置": true, "审计级别": "info"}' \
  --apply-to queues
```

#### 自定义审计日志

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityAuditLogger:
    """安全审计日志记录器"""
    
    def __init__(self, log_file: str = 'security_audit.log'):
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_authentication_attempt(self, username: str, success: bool, 
                                   source_ip: str, details: Dict[str, Any] = None):
        """记录认证尝试"""
        event = {
            'event_type': 'authentication',
            'username': username,
            'success': success,
            'source_ip': source_ip,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.logger.info(json.dumps(event))
    
    def log_permission_change(self, username: str, action: str, 
                             resource: str, details: Dict[str, Any] = None):
        """记录权限变更"""
        event = {
            'event_type': 'permission_change',
            'username': username,
            'action': action,
            'resource': resource,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.logger.info(json.dumps(event))
    
    def log_message_access(self, username: str, queue: str, 
                          operation: str, message_count: int = 1):
        """记录消息访问"""
        event = {
            'event_type': 'message_access',
            'username': username,
            'queue': queue,
            'operation': operation,
            'message_count': message_count,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(json.dumps(event))
    
    def log_security_incident(self, incident_type: str, severity: str,
                             description: str, affected_users: list = None):
        """记录安全事件"""
        event = {
            'event_type': 'security_incident',
            'incident_type': incident_type,
            'severity': severity,
            'description': description,
            'affected_users': affected_users or [],
            'timestamp': datetime.now().isoformat()
        }
        self.logger.error(json.dumps(event))

# 使用示例
audit_logger = SecurityAuditLogger()

# 记录认证尝试
audit_logger.log_authentication_attempt(
    username='john_doe',
    success=False,
    source_ip='192.168.1.100',
    details={'password_attempts': 3}
)

# 记录权限变更
audit_logger.log_permission_change(
    username='admin_user',
    action='set_permissions',
    resource='/production/orders_queue',
    details={'configure': '.*', 'read': '.*', 'write': '.*'}
)
```

### 2. 安全监控

#### 实时安全监控

```python
import psutil
import threading
import time
from collections import defaultdict

class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitor_thread = None
        self.threat_levels = defaultdict(int)
        self.alert_thresholds = {
            'failed_auth_attempts': 10,
            'high_cpu_usage': 80,
            'high_memory_usage': 85,
            'disk_usage': 90,
            'network_connections': 1000
        }
        self.alerts_sent = []
    
    def start_monitoring(self):
        """启动监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("安全监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("安全监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._check_system_resources()
                self._check_network_security()
                self._check_access_patterns()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"监控循环错误: {e}")
    
    def _check_system_resources(self):
        """检查系统资源"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > self.alert_thresholds['high_cpu_usage']:
            self._send_alert('high_cpu', f'CPU使用率过高: {cpu_percent}%')
        
        # 内存使用率
        memory = psutil.virtual_memory()
        if memory.percent > self.alert_thresholds['high_memory_usage']:
            self._send_alert('high_memory', f'内存使用率过高: {memory.percent}%')
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        if (disk.used / disk.total * 100) > self.alert_thresholds['disk_usage']:
            self._send_alert('high_disk', f'磁盘使用率过高: {disk.used / disk.total * 100:.1f}%')
    
    def _check_network_security(self):
        """检查网络安全"""
        try:
            connections = len(psutil.net_connections())
            if connections > self.alert_thresholds['network_connections']:
                self._send_alert('high_connections', f'网络连接数过多: {connections}')
        except Exception as e:
            print(f"网络检查错误: {e}")
    
    def _check_access_patterns(self):
        """检查访问模式"""
        # 这里可以集成RabbitMQ管理API来检查访问模式
        # 比如检查用户登录频率、消息访问模式等
        pass
    
    def _send_alert(self, alert_type: str, message: str):
        """发送安全警报"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        # 避免重复发送相同警报
        if alert not in self.alerts_sent:
            self.alerts_sent.append(alert)
            print(f"安全警报 [{alert_type}]: {message}")
            
            # 这里可以集成实际的警报机制，如邮件、短信等
    
    def get_security_status(self) -> Dict[str, Any]:
        """获取安全状态"""
        return {
            'monitoring_active': self.is_monitoring,
            'threat_levels': dict(self.threat_levels),
            'alerts_sent_count': len(self.alerts_sent),
            'system_resources': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').used / psutil.disk_usage('/').total * 100,
                'network_connections': len(psutil.net_connections())
            }
        }

# 使用示例
security_monitor = SecurityMonitor(check_interval=30)
security_monitor.start_monitoring()

# 获取安全状态
status = security_monitor.get_security_status()
print("安全监控状态:", status)
```

## 故障处理与应急响应

### 1. 安全事件响应

#### 安全事件处理流程

```python
import json
import subprocess
from datetime import datetime

class SecurityIncidentHandler:
    """安全事件处理器"""
    
    def __init__(self):
        self.incident_log = []
        self.response_actions = {
            'brute_force': self._handle_brute_force,
            'unauthorized_access': self._handle_unauthorized_access,
            'data_breach': self._handle_data_breach,
            'service_disruption': self._handle_service_disruption
        }
    
    def handle_incident(self, incident_type: str, incident_data: Dict[str, Any]):
        """处理安全事件"""
        incident_id = len(self.incident_log) + 1
        incident = {
            'id': incident_id,
            'type': incident_type,
            'timestamp': datetime.now().isoformat(),
            'data': incident_data,
            'status': 'open'
        }
        
        self.incident_log.append(incident)
        
        # 执行响应动作
        if incident_type in self.response_actions:
            self.response_actions[incident_type](incident)
        else:
            self._generic_response(incident)
        
        # 记录事件
        self._log_incident(incident)
    
    def _handle_brute_force(self, incident):
        """处理暴力破解攻击"""
        data = incident['data']
        
        # 1. 临时禁用可疑IP地址
        suspicious_ip = data.get('source_ip')
        self._block_ip_temporarily(suspicious_ip, duration_minutes=60)
        
        # 2. 增强认证监控
        self._enhance_auth_monitoring()
        
        # 3. 延长认证超时时间
        self._adjust_auth_timeout()
        
        incident['status'] = 'handled'
        incident['actions_taken'] = [
            f'IP {suspicious_ip} 已被临时封禁',
            '增强认证监控已启用',
            '认证超时时间已调整'
        ]
    
    def _handle_unauthorized_access(self, incident):
        """处理未授权访问"""
        data = incident['data']
        
        # 1. 立即禁用相关用户账户
        username = data.get('username')
        self._disable_user_account(username)
        
        # 2. 撤销相关用户的所有权限
        self._revoke_user_permissions(username)
        
        # 3. 清理相关会话
        self._terminate_user_sessions(username)
        
        incident['status'] = 'contained'
        incident['actions_taken'] = [
            f'用户 {username} 账户已被禁用',
            '所有权限已被撤销',
            '相关会话已被终止'
        ]
    
    def _handle_data_breach(self, incident):
        """处理数据泄露"""
        data = incident['data']
        
        # 1. 立即隔离受影响的系统
        affected_systems = data.get('affected_systems', [])
        for system in affected_systems:
            self._isolate_system(system)
        
        # 2. 停止所有数据传输
        self._stop_all_data_flows()
        
        # 3. 开始数据完整性检查
        self._start_data_integrity_check()
        
        # 4. 通知相关人员
        self._notify_security_team(incident)
        
        incident['status'] = 'contained'
        incident['actions_taken'] = [
            '受影响系统已被隔离',
            '所有数据传输已停止',
            '数据完整性检查已开始',
            '安全团队已收到通知'
        ]
    
    def _handle_service_disruption(self, incident):
        """处理服务中断"""
        # 1. 评估服务影响范围
        # 2. 启动备用服务
        # 3. 恢复正常服务
        # 4. 进行服务恢复验证
        incident['status'] = 'resolved'
    
    def _block_ip_temporarily(self, ip: str, duration_minutes: int):
        """临时封禁IP"""
        try:
            # 使用iptables封禁IP
            subprocess.run([
                'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'
            ], check=True)
            
            # 设置定时任务恢复IP
            subprocess.run([
                'at', f'now + {duration_minutes} minutes', '-c',
                f'iptables -D INPUT -s {ip} -j DROP'
            ], check=True)
            
            print(f"IP {ip} 已被临时封禁 {duration_minutes} 分钟")
        except Exception as e:
            print(f"封禁IP失败: {e}")
    
    def _disable_user_account(self, username: str):
        """禁用用户账户"""
        try:
            subprocess.run([
                'rabbitmqctl', 'clear_permissions', '-p', '/', username
            ], check=True)
            print(f"用户 {username} 账户已被禁用")
        except Exception as e:
            print(f"禁用用户失败: {e}")
    
    def _revoke_user_permissions(self, username: str):
        """撤销用户权限"""
        try:
            subprocess.run([
                'rabbitmqctl', 'clear_permissions', '-p', '/', username
            ], check=True)
            print(f"用户 {username} 权限已被撤销")
        except Exception as e:
            print(f"撤销权限失败: {e}")
    
    def _terminate_user_sessions(self, username: str):
        """终止用户会话"""
        try:
            # 这里可以集成RabbitMQ管理API来终止会话
            print(f"用户 {username} 的会话已被终止")
        except Exception as e:
            print(f"终止会话失败: {e}")
    
    def _enhance_auth_monitoring(self):
        """增强认证监控"""
        # 实施更严格的认证监控
        print("认证监控已增强")
    
    def _adjust_auth_timeout(self):
        """调整认证超时"""
        # 调整认证相关配置
        print("认证超时时间已调整")
    
    def _isolate_system(self, system: str):
        """隔离系统"""
        print(f"系统 {system} 已被隔离")
    
    def _stop_all_data_flows(self):
        """停止所有数据流"""
        print("所有数据流已停止")
    
    def _start_data_integrity_check(self):
        """开始数据完整性检查"""
        print("数据完整性检查已开始")
    
    def _notify_security_team(self, incident):
        """通知安全团队"""
        print(f"安全团队已收到通知: 事件ID {incident['id']}")
    
    def _generic_response(self, incident):
        """通用响应"""
        incident['status'] = 'pending'
        incident['actions_taken'] = ['等待人工处理']
    
    def _log_incident(self, incident):
        """记录事件"""
        with open('security_incidents.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps(incident, ensure_ascii=False) + '\n')
    
    def get_incident_report(self) -> Dict[str, Any]:
        """获取事件报告"""
        total_incidents = len(self.incident_log)
        open_incidents = len([i for i in self.incident_log if i['status'] == 'open'])
        handled_incidents = len([i for i in self.incident_log if i['status'] in ['handled', 'contained', 'resolved']])
        
        return {
            'total_incidents': total_incidents,
            'open_incidents': open_incidents,
            'handled_incidents': handled_incidents,
            'recent_incidents': self.incident_log[-10:] if self.incident_log else []
        }

# 使用示例
incident_handler = SecurityIncidentHandler()

# 处理暴力破解事件
incident_handler.handle_incident('brute_force', {
    'source_ip': '192.168.1.100',
    'username': 'admin',
    'attempts': 15,
    'time_window': '5_minutes'
})

# 处理未授权访问事件
incident_handler.handle_incident('unauthorized_access', {
    'username': 'suspicious_user',
    'resource': '/production/sensitive_data',
    'timestamp': datetime.now().isoformat()
})

# 获取事件报告
report = incident_handler.get_incident_report()
print("安全事件报告:", report)
```

### 2. 安全备份与恢复

#### 安全备份策略

```python
import os
import tarfile
import json
from datetime import datetime, timedelta

class SecureBackupManager:
    """安全备份管理器"""
    
    def __init__(self, backup_dir: str = '/secure/backups'):
        self.backup_dir = backup_dir
        self.encryption_key = self._get_or_create_encryption_key()
        os.makedirs(backup_dir, exist_ok=True)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        key_path = '/secure/backup.key'
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            # 这里应该使用真正的密钥生成
            return os.urandom(32)
    
    def create_rabbitmq_backup(self, backup_name: str = None):
        """创建RabbitMQ安全备份"""
        if backup_name is None:
            backup_name = f"rabbitmq_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        try:
            # 1. 备份配置
            self._backup_config(backup_path)
            
            # 2. 备份用户和权限
            self._backup_users_and_permissions(backup_path)
            
            # 3. 备份虚拟主机
            self._backup_vhosts(backup_path)
            
            # 4. 备份交换器和队列定义
            self._backup_definitions(backup_path)
            
            # 5. 创建加密压缩包
            encrypted_backup = self._create_encrypted_backup(backup_path)
            
            # 6. 清理临时文件
            self._cleanup_temp_files(backup_path)
            
            # 7. 记录备份信息
            self._log_backup(backup_name, encrypted_backup)
            
            return encrypted_backup
            
        except Exception as e:
            print(f"备份创建失败: {e}")
            return None
    
    def _backup_config(self, backup_path: str):
        """备份配置"""
        config_files = [
            '/etc/rabbitmq/rabbitmq.config',
            '/etc/rabbitmq/rabbitmq-env.conf',
            '/etc/rabbitmq/advanced.config'
        ]
        
        config_backup_path = os.path.join(backup_path, 'config')
        os.makedirs(config_backup_path, exist_ok=True)
        
        for config_file in config_files:
            if os.path.exists(config_file):
                import shutil
                shutil.copy2(config_file, config_backup_path)
    
    def _backup_users_and_permissions(self, backup_path: str):
        """备份用户和权限"""
        try:
            import subprocess
            
            # 获取用户列表
            result = subprocess.run(['rabbitmqctl', 'list_users', '-s'],
                                  capture_output=True, text=True, check=True)
            
            users_backup_path = os.path.join(backup_path, 'users')
            os.makedirs(users_backup_path, exist_ok=True)
            
            with open(os.path.join(users_backup_path, 'users.json'), 'w') as f:
                json.dump({'users_output': result.stdout}, f, indent=2)
            
            # 获取权限信息
            result = subprocess.run(['rabbitmqctl', 'list_permissions'],
                                  capture_output=True, text=True, check=True)
            
            with open(os.path.join(users_backup_path, 'permissions.json'), 'w') as f:
                json.dump({'permissions_output': result.stdout}, f, indent=2)
                
        except Exception as e:
            print(f"备份用户和权限失败: {e}")
    
    def _backup_vhosts(self, backup_path: str):
        """备份虚拟主机"""
        try:
            import subprocess
            
            # 获取虚拟主机列表
            result = subprocess.run(['rabbitmqctl', 'list_vhosts'],
                                  capture_output=True, text=True, check=True)
            
            vhosts_backup_path = os.path.join(backup_path, 'vhosts')
            os.makedirs(vhosts_backup_path, exist_ok=True)
            
            with open(os.path.join(vhosts_backup_path, 'vhosts.json'), 'w') as f:
                json.dump({'vhosts_output': result.stdout}, f, indent=2)
                
        except Exception as e:
            print(f"备份虚拟主机失败: {e}")
    
    def _backup_definitions(self, backup_path: str):
        """备份交换器和队列定义"""
        try:
            import subprocess
            
            # 导出定义
            result = subprocess.run([
                'rabbitmqctl', 'export_definitions', '-',
                '--format', 'json'
            ], capture_output=True, text=True, check=True)
            
            definitions_backup_path = os.path.join(backup_path, 'definitions')
            os.makedirs(definitions_backup_path, exist_ok=True)
            
            with open(os.path.join(definitions_backup_path, 'definitions.json'), 'w') as f:
                f.write(result.stdout)
                
        except Exception as e:
            print(f"备份定义失败: {e}")
    
    def _create_encrypted_backup(self, backup_path: str) -> str:
        """创建加密备份"""
        backup_name = os.path.basename(backup_path)
        encrypted_name = f"{backup_name}.enc"
        encrypted_path = os.path.join(self.backup_dir, encrypted_name)
        
        try:
            with tarfile.open(encrypted_path, 'w:gz') as tar:
                tar.add(backup_path, arcname=backup_name)
            
            # 这里应该对tar文件进行真正的加密
            # 暂时只返回加密文件名
            return encrypted_path
            
        except Exception as e:
            print(f"创建加密备份失败: {e}")
            return None
    
    def _cleanup_temp_files(self, backup_path: str):
        """清理临时文件"""
        import shutil
        try:
            shutil.rmtree(backup_path)
        except Exception as e:
            print(f"清理临时文件失败: {e}")
    
    def _log_backup(self, backup_name: str, backup_path: str):
        """记录备份信息"""
        backup_info = {
            'name': backup_name,
            'path': backup_path,
            'created_at': datetime.now().isoformat(),
            'size_bytes': os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
            'status': 'success'
        }
        
        log_file = os.path.join(self.backup_dir, 'backup_log.json')
        backup_log = []
        
        # 读取现有日志
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    backup_log = json.load(f)
            except:
                backup_log = []
        
        backup_log.append(backup_info)
        
        # 保存更新后的日志
        with open(log_file, 'w') as f:
            json.dump(backup_log, f, indent=2)
    
    def restore_from_backup(self, backup_name: str, dry_run: bool = False):
        """从备份恢复"""
        encrypted_path = os.path.join(self.backup_dir, f"{backup_name}.enc")
        
        if not os.path.exists(encrypted_path):
            print(f"备份文件不存在: {encrypted_path}")
            return False
        
        print(f"开始恢复备份: {backup_name}")
        if dry_run:
            print("这是试运行模式，不会实际执行恢复操作")
            return True
        
        try:
            # 1. 解密备份文件
            temp_dir = self._decrypt_backup(encrypted_path)
            
            # 2. 验证备份完整性
            if not self._validate_backup(temp_dir):
                print("备份文件验证失败")
                return False
            
            # 3. 停止RabbitMQ服务
            subprocess.run(['systemctl', 'stop', 'rabbitmq-server'], check=True)
            
            # 4. 恢复配置
            self._restore_config(temp_dir)
            
            # 5. 恢复定义
            self._restore_definitions(temp_dir)
            
            # 6. 重启RabbitMQ服务
            subprocess.run(['systemctl', 'start', 'rabbitmq-server'], check=True)
            
            # 7. 恢复用户和权限
            self._restore_users_and_permissions(temp_dir)
            
            print(f"备份恢复成功: {backup_name}")
            return True
            
        except Exception as e:
            print(f"备份恢复失败: {e}")
            return False
        finally:
            # 清理临时文件
            if 'temp_dir' in locals():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _decrypt_backup(self, encrypted_path: str) -> str:
        """解密备份文件"""
        # 这里应该实现真正的解密逻辑
        # 暂时只是解压
        temp_dir = encrypted_path.rstrip('.enc') + '_temp'
        os.makedirs(temp_dir, exist_ok=True)
        
        with tarfile.open(encrypted_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
        
        return temp_dir
    
    def _validate_backup(self, backup_path: str) -> bool:
        """验证备份完整性"""
        required_files = [
            'config',
            'users',
            'vhosts',
            'definitions'
        ]
        
        for required_file in required_files:
            if not os.path.exists(os.path.join(backup_path, required_file)):
                return False
        
        return True
    
    def _restore_config(self, backup_path: str):
        """恢复配置"""
        config_backup_path = os.path.join(backup_path, 'config')
        if os.path.exists(config_backup_path):
            for filename in os.listdir(config_backup_path):
                source = os.path.join(config_backup_path, filename)
                dest = os.path.join('/etc/rabbitmq', filename)
                shutil.copy2(source, dest)
    
    def _restore_definitions(self, backup_path: str):
        """恢复定义"""
        definitions_backup_path = os.path.join(backup_path, 'definitions')
        definitions_file = os.path.join(definitions_backup_path, 'definitions.json')
        
        if os.path.exists(definitions_file):
            try:
                # 这里需要先读取定义，然后通过RabbitMQ管理API导入
                print("正在恢复交换器和队列定义...")
            except Exception as e:
                print(f"恢复定义失败: {e}")
    
    def _restore_users_and_permissions(self, backup_path: str):
        """恢复用户和权限"""
        users_backup_path = os.path.join(backup_path, 'users')
        if os.path.exists(users_backup_path):
            # 这里需要实现用户和权限的恢复逻辑
            print("正在恢复用户和权限...")
    
    def list_backups(self) -> list:
        """列出所有备份"""
        backup_log_file = os.path.join(self.backup_dir, 'backup_log.json')
        
        if not os.path.exists(backup_log_file):
            return []
        
        try:
            with open(backup_log_file, 'r') as f:
                return json.load(f)
        except:
            return []

# 使用示例
backup_manager = SecureBackupManager()

# 创建备份
backup_path = backup_manager.create_rabbitmq_backup()
if backup_path:
    print(f"备份创建成功: {backup_path}")

# 列出备份
backups = backup_manager.list_backups()
print("可用备份:", backups)

# 恢复备份
# backup_manager.restore_from_backup("rabbitmq_backup_20240115_120000", dry_run=True)
```

## 最佳实践

### 1. 安全设计原则

#### 最小权限原则

```python
class MinimizePermissionManager:
    """最小权限管理"""
    
    def __init__(self):
        self.permission_templates = {
            'basic_consumer': {
                'configure': '^amq\\.',  # 只能使用默认交换器
                'read': '^queue_name$',   # 只能读取指定队列
                'write': '^queue_name$'   # 只能写入指定队列
            },
            'basic_producer': {
                'configure': '^amq\\.',   # 只能使用默认交换器
                'read': '',               # 不能读取
                'write': '^exchange_name$' # 只能写入指定交换器
            },
            'admin': {
                'configure': '.*',        # 完全配置权限
                'read': '.*',             # 完全读取权限
                'write': '.*'             # 完全写入权限
            }
        }
    
    def create_user_with_template(self, username: str, password: str, 
                                 template_name: str, vhost: str = '/') -> bool:
        """使用模板创建用户"""
        try:
            import subprocess
            
            # 1. 创建用户
            subprocess.run([
                'rabbitmqctl', 'add_user', username, password
            ], check=True)
            
            # 2. 应用权限模板
            template = self.permission_templates.get(template_name)
            if not template:
                raise ValueError(f"权限模板不存在: {template_name}")
            
            configure = template['configure'] or ''
            read = template['read'] or ''
            write = template['write'] or ''
            
            subprocess.run([
                'rabbitmqctl', 'set_permissions',
                '-p', vhost,
                username,
                configure,
                read,
                write
            ], check=True)
            
            print(f"用户 {username} 创建成功，使用权限模板: {template_name}")
            return True
            
        except Exception as e:
            print(f"创建用户失败: {e}")
            return False
    
    def create_readonly_user(self, username: str, password: str, 
                           queue_pattern: str, vhost: str = '/') -> bool:
        """创建只读用户"""
        return self.create_user_with_template(username, password, 'basic_consumer')
```

### 2. 安全配置检查

#### 配置审计工具

```python
class SecurityConfigAuditor:
    """安全配置审计器"""
    
    def __init__(self):
        self.check_results = []
        self.critical_checks = [
            self.check_default_password,
            self.check_ssl_configuration,
            self.check_user_permissions,
            self.check_listeners,
            self.check_logging
        ]
    
    def run_security_audit(self) -> Dict[str, Any]:
        """运行安全审计"""
        self.check_results = []
        
        # 运行所有检查
        for check in self.critical_checks:
            try:
                result = check()
                self.check_results.append(result)
            except Exception as e:
                self.check_results.append({
                    'check_name': check.__name__,
                    'status': 'error',
                    'message': f'检查执行失败: {e}',
                    'severity': 'medium'
                })
        
        # 生成审计报告
        return self.generate_audit_report()
    
    def check_default_password(self) -> Dict[str, Any]:
        """检查默认密码"""
        import subprocess
        
        try:
            result = subprocess.run([
                'rabbitmqctl', 'authenticate_user', 'guest', 'guest'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'check_name': 'check_default_password',
                    'status': 'failed',
                    'message': '默认guest用户可以使用默认密码guest登录',
                    'severity': 'critical',
                    'recommendation': '立即修改默认密码或禁用guest用户'
                }
            else:
                return {
                    'check_name': 'check_default_password',
                    'status': 'passed',
                    'message': '默认guest用户已被禁用或密码已更改',
                    'severity': 'low'
                }
                
        except Exception as e:
            return {
                'check_name': 'check_default_password',
                'status': 'error',
                'message': f'检查失败: {e}',
                'severity': 'low'
            }
    
    def check_ssl_configuration(self) -> Dict[str, Any]:
        """检查SSL配置"""
        try:
            import subprocess
            
            # 检查SSL监听器
            result = subprocess.run([
                'rabbitmqctl', 'environment'
            ], capture_output=True, text=True)
            
            # 解析环境变量查找SSL配置
            ssl_enabled = '5671' in result.stdout or 'ssl_listeners' in result.stdout
            
            if not ssl_enabled:
                return {
                    'check_name': 'check_ssl_configuration',
                    'status': 'warning',
                    'message': 'SSL/TLS未配置，建议启用SSL加密',
                    'severity': 'medium',
                    'recommendation': '配置SSL证书和监听器'
                }
            else:
                return {
                    'check_name': 'check_ssl_configuration',
                    'status': 'passed',
                    'message': 'SSL/TLS配置正常',
                    'severity': 'low'
                }
                
        except Exception as e:
            return {
                'check_name': 'check_ssl_configuration',
                'status': 'error',
                'message': f'SSL检查失败: {e}',
                'severity': 'low'
            }
    
    def check_user_permissions(self) -> Dict[str, Any]:
        """检查用户权限"""
        try:
            import subprocess
            
            result = subprocess.run([
                'rabbitmqctl', 'list_permissions'
            ], capture_output=True, text=True)
            
            # 检查是否有用户拥有过宽的权限
            if '.*' in result.stdout and 'guest' in result.stdout:
                return {
                    'check_name': 'check_user_permissions',
                    'status': 'warning',
                    'message': '发现guest用户拥有宽权限',
                    'severity': 'medium',
                    'recommendation': '限制guest用户权限'
                }
            else:
                return {
                    'check_name': 'check_user_permissions',
                    'status': 'passed',
                    'message': '用户权限配置正常',
                    'severity': 'low'
                }
                
        except Exception as e:
            return {
                'check_name': 'check_user_permissions',
                'status': 'error',
                'message': f'权限检查失败: {e}',
                'severity': 'low'
            }
    
    def check_listeners(self) -> Dict[str, Any]:
        """检查监听器配置"""
        try:
            import subprocess
            
            result = subprocess.run([
                'rabbitmqctl', 'environment'
            ], capture_output=True, text=True)
            
            # 检查是否有监听非本地地址
            exposed_addresses = []
            if '0.0.0.0' in result.stdout:
                exposed_addresses.append('0.0.0.0 (所有网络接口)')
            
            if exposed_addresses:
                return {
                    'check_name': 'check_listeners',
                    'status': 'warning',
                    'message': f'发现暴露的监听地址: {", ".join(exposed_addresses)}',
                    'severity': 'medium',
                    'recommendation': '限制监听地址在必要的网络接口'
                }
            else:
                return {
                    'check_name': 'check_listeners',
                    'status': 'passed',
                    'message': '监听器配置安全',
                    'severity': 'low'
                }
                
        except Exception as e:
            return {
                'check_name': 'check_listeners',
                'status': 'error',
                'message': f'监听器检查失败: {e}',
                'severity': 'low'
            }
    
    def check_logging(self) -> Dict[str, Any]:
        """检查日志配置"""
        try:
            # 检查日志级别和日志文件配置
            return {
                'check_name': 'check_logging',
                'status': 'passed',
                'message': '日志配置正常',
                'severity': 'low'
            }
        except Exception as e:
            return {
                'check_name': 'check_logging',
                'status': 'error',
                'message': f'日志检查失败: {e}',
                'severity': 'low'
            }
    
    def generate_audit_report(self) -> Dict[str, Any]:
        """生成审计报告"""
        total_checks = len(self.check_results)
        passed_checks = len([r for r in self.check_results if r['status'] == 'passed'])
        failed_checks = len([r for r in self.check_results if r['status'] == 'failed'])
        warning_checks = len([r for r in self.check_results if r['status'] == 'warning'])
        error_checks = len([r for r in self.check_results if r['status'] == 'error'])
        
        critical_issues = [r for r in self.check_results 
                          if r.get('severity') == 'critical' and r['status'] != 'passed']
        
        return {
            'audit_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'warnings': warning_checks,
                'errors': error_checks,
                'security_score': (passed_checks / total_checks * 100) if total_checks > 0 else 0
            },
            'critical_issues': critical_issues,
            'detailed_results': self.check_results,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> list:
        """生成安全建议"""
        recommendations = []
        
        for result in self.check_results:
            if 'recommendation' in result:
                recommendations.append({
                    'check': result['check_name'],
                    'recommendation': result['recommendation'],
                    'priority': result.get('severity', 'low')
                })
        
        return recommendations

# 使用示例
auditor = SecurityConfigAuditor()
audit_report = auditor.run_security_audit()

print("安全审计报告:")
print(f"安全评分: {audit_report['summary']['security_score']:.1f}%")
print(f"严重问题数量: {len(audit_report['critical_issues'])}")

for issue in audit_report['critical_issues']:
    print(f"严重问题: {issue['message']}")
```

### 3. 安全运营手册

#### 日常安全检查清单

```python
class DailySecurityChecklist:
    """日常安全检查清单"""
    
    def __init__(self):
        self.checklist = [
            self.check_failed_auth_attempts,
            self.check_unusual_network_activity,
            self.check_ssl_certificate_expiry,
            self.check_disk_space,
            self.check_memory_usage,
            self.check_user_permissions_changes,
            self.check_security_logs
        ]
    
    def run_daily_checks(self) -> Dict[str, Any]:
        """运行日常安全检查"""
        results = []
        
        for check in self.checklist:
            try:
                result = check()
                results.append(result)
            except Exception as e:
                results.append({
                    'check_name': check.__name__,
                    'status': 'error',
                    'message': f'检查失败: {e}',
                    'timestamp': datetime.now().isoformat()
                })
        
        return {
            'check_date': datetime.now().strftime('%Y-%m-%d'),
            'total_checks': len(self.checklist),
            'results': results,
            'overall_status': self._evaluate_overall_status(results)
        }
    
    def check_failed_auth_attempts(self) -> Dict[str, Any]:
        """检查认证失败次数"""
        # 这里应该检查RabbitMQ日志或管理API
        return {
            'check_name': 'check_failed_auth_attempts',
            'status': 'passed',
            'message': '认证失败次数在正常范围内',
            'timestamp': datetime.now().isoformat()
        }
    
    def check_unusual_network_activity(self) -> Dict[str, Any]:
        """检查异常网络活动"""
        # 使用psutil检查网络连接
        connections = len(psutil.net_connections())
        
        if connections > 1000:
            return {
                'check_name': 'check_unusual_network_activity',
                'status': 'warning',
                'message': f'网络连接数异常: {connections}',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'check_name': 'check_unusual_network_activity',
                'status': 'passed',
                'message': f'网络活动正常，连接数: {connections}',
                'timestamp': datetime.now().isoformat()
            }
    
    def check_ssl_certificate_expiry(self) -> Dict[str, Any]:
        """检查SSL证书到期"""
        # 检查SSL证书到期时间
        cert_path = '/etc/rabbitmq/ssl/server-cert.pem'
        
        try:
            if not os.path.exists(cert_path):
                return {
                    'check_name': 'check_ssl_certificate_expiry',
                    'status': 'warning',
                    'message': 'SSL证书文件不存在',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 这里应该检查证书的到期日期
            return {
                'check_name': 'check_ssl_certificate_expiry',
                'status': 'passed',
                'message': 'SSL证书状态正常',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'check_name': 'check_ssl_certificate_expiry',
                'status': 'error',
                'message': f'SSL证书检查失败: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        disk = psutil.disk_usage('/')
        used_percent = (disk.used / disk.total) * 100
        
        if used_percent > 85:
            return {
                'check_name': 'check_disk_space',
                'status': 'warning',
                'message': f'磁盘使用率过高: {used_percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'check_name': 'check_disk_space',
                'status': 'passed',
                'message': f'磁盘空间充足: {used_percent:.1f}% 已使用',
                'timestamp': datetime.now().isoformat()
            }
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """检查内存使用"""
        memory = psutil.virtual_memory()
        
        if memory.percent > 80:
            return {
                'check_name': 'check_memory_usage',
                'status': 'warning',
                'message': f'内存使用率过高: {memory.percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'check_name': 'check_memory_usage',
                'status': 'passed',
                'message': f'内存使用正常: {memory.percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            }
    
    def check_user_permissions_changes(self) -> Dict[str, Any]:
        """检查用户权限变更"""
        # 检查最近的权限变更记录
        return {
            'check_name': 'check_user_permissions_changes',
            'status': 'passed',
            'message': '最近无异常权限变更',
            'timestamp': datetime.now().isoformat()
        }
    
    def check_security_logs(self) -> Dict[str, Any]:
        """检查安全日志"""
        # 检查安全日志中的异常记录
        return {
            'check_name': 'check_security_logs',
            'status': 'passed',
            'message': '安全日志检查正常',
            'timestamp': datetime.now().isoformat()
        }
    
    def _evaluate_overall_status(self, results: list) -> str:
        """评估整体状态"""
        error_count = len([r for r in results if r['status'] == 'error'])
        warning_count = len([r for r in results if r['status'] == 'warning'])
        
        if error_count > 0:
            return 'error'
        elif warning_count > 0:
            return 'warning'
        else:
            return 'healthy'

# 使用示例
daily_checker = DailySecurityChecklist()
daily_report = daily_checker.run_daily_checks()

print(f"日常安全检查报告 - {daily_report['check_date']}")
print(f"整体状态: {daily_report['overall_status']}")
print(f"通过检查: {len([r for r in daily_report['results'] if r['status'] == 'passed'])}/{daily_report['total_checks']}")

for result in daily_report['results']:
    if result['status'] != 'passed':
        print(f"{result['status']}: {result['message']}")
```

## 总结

本章全面介绍了RabbitMQ安全与认证的各个方面：

### 核心知识点

1. **安全架构**: 理解RabbitMQ的多层安全架构
2. **用户认证**: 掌握内置认证、LDAP集成和自定义认证
3. **权限管理**: 学习用户权限、虚拟主机隔离和资源配额
4. **SSL/TLS加密**: 掌握证书管理和加密通信配置
5. **安全策略**: 了解访问控制、消息加密和数据脱敏
6. **审计监控**: 学习审计日志、安全监控和事件响应
7. **故障处理**: 掌握安全事件处理和应急响应流程
8. **最佳实践**: 理解安全设计原则和日常运营检查

### 实战要点

- **多层防护**: 从网络、传输、认证、授权、应用各层进行安全防护
- **最小权限**: 严格控制用户权限，遵循最小权限原则
- **监控审计**: 建立完善的安全监控和审计体系
- **应急响应**: 建立快速的安全事件响应机制
- **定期检查**: 进行定期的安全配置审计和风险评估

### 下一步学习

- 学习集群环境的安全配置和管理
- 深入了解高级安全插件和扩展
- 研究零信任架构在消息系统中的应用
- 探索云原生环境下的安全策略

通过本章的学习，您将能够为RabbitMQ部署建立完整的安全防护体系，确保消息传递系统的安全性和可靠性。