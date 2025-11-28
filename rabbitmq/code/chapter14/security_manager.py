"""
RabbitMQ安全与权限管理核心组件
Security Manager for RabbitMQ Authentication, Authorization, and Audit
"""

import pika
import ssl
import hashlib
import hmac
import json
import time
import logging
import threading
import jwt
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from collections import defaultdict, deque
import ldap3
import yaml
import re


# 枚举类定义
class SecurityLevel(Enum):
    """安全级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthMethod(Enum):
    """认证方法"""
    PASSWORD = "password"
    LDAP = "ldap"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"


class PermissionType(Enum):
    """权限类型"""
    CONFIGURE = "configure"
    WRITE = "write"
    READ = "read"


class SecurityEvent(Enum):
    """安全事件类型"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PERMISSION_DENIED = "permission_denied"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_COMPROMISE = "system_compromise"


# 数据类定义
@dataclass
class User:
    """用户信息"""
    username: str
    password_hash: str
    auth_method: AuthMethod
    permissions: Dict[str, Any]
    vhost_access: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    session_tokens: List[str] = None

    def __post_init__(self):
        if self.session_tokens is None:
            self.session_tokens = []


@dataclass
class SecurityEventRecord:
    """安全事件记录"""
    event_type: SecurityEvent
    timestamp: datetime
    user_id: str
    source_ip: str
    details: Dict[str, Any]
    security_level: SecurityLevel
    resolved: bool = False


@dataclass
class EncryptionConfig:
    """加密配置"""
    algorithm: str
    key_size: int
    iv_size: int
    salt_size: int
    iterations: int


# 加密管理器
class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.cipher = Fernet(master_key or Fernet.generate_key())
        self.sym_key = secrets.token_bytes(32)  # 256位对称密钥
    
    def encrypt_message(self, message: Union[str, bytes]) -> str:
        """加密消息"""
        if isinstance(message, str):
            message = message.encode()
        
        encrypted = self.cipher.encrypt(message)
        return base64.b64encode(encrypted).decode()
    
    def decrypt_message(self, encrypted_message: str) -> bytes:
        """解密消息"""
        encrypted_bytes = base64.b64decode(encrypted_message.encode())
        return self.cipher.decrypt(encrypted_bytes)
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """密码哈希"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        hash_value = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return hash_value.hex(), salt.hex()
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """验证密码"""
        test_hash, _ = self.hash_password(password, bytes.fromhex(salt))
        return hmac.compare_digest(test_hash, hash_value)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """生成安全令牌"""
        return secrets.token_urlsafe(length)
    
    def generate_password(self, length: int = 16, 
                         uppercase: bool = True, 
                         lowercase: bool = True,
                         digits: bool = True, 
                         symbols: bool = True) -> str:
        """生成强密码"""
        charset = ""
        if uppercase:
            charset += string.ascii_uppercase
        if lowercase:
            charset += string.ascii_lowercase
        if digits:
            charset += string.digits
        if symbols:
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        password = []
        
        # 确保包含所有要求的字符类型
        if uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if lowercase:
            password.append(secrets.choice(string.ascii_lowercase))
        if digits:
            password.append(secrets.choice(string.digits))
        if symbols:
            password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        # 填充剩余长度
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(charset))
        
        # 打乱字符顺序
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)


# 认证管理器
class AuthenticationManager:
    """认证管理器"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.users: Dict[str, User] = {}
        self.failed_attempts: Dict[str, deque] = defaultdict(deque)
        self.locked_accounts: Dict[str, datetime] = {}
        self.session_tokens: Dict[str, str] = {}  # token -> username
        self.lock = threading.Lock()
    
    def register_user(self, username: str, password: str, 
                     auth_method: AuthMethod = AuthMethod.PASSWORD,
                     permissions: Optional[Dict] = None,
                     vhost_access: Optional[List[str]] = None) -> bool:
        """注册用户"""
        with self.lock:
            if username in self.users:
                return False
            
            # 验证密码强度
            issues = self._validate_password_strength(password)
            if issues:
                raise ValueError(f"密码不符合安全要求: {', '.join(issues)}")
            
            # 加密密码
            password_hash, salt = self.encryption_manager.hash_password(password)
            
            # 创建用户
            user = User(
                username=username,
                password_hash=password_hash,
                auth_method=auth_method,
                permissions=permissions or {'configure': '', 'write': '', 'read': ''},
                vhost_access=vhost_access or ['/'],
                created_at=datetime.utcnow()
            )
            
            # 存储额外信息（salt通过特殊字段存储）
            user.salt = salt
            
            self.users[username] = user
            return True
    
    def authenticate_user(self, username: str, password: str, 
                         source_ip: str = "unknown") -> Optional[str]:
        """用户认证"""
        with self.lock:
            # 检查账户是否被锁定
            if username in self.locked_accounts:
                lock_time = self.locked_accounts[username]
                if datetime.utcnow() - lock_time < timedelta(hours=1):
                    return None  # 账户仍被锁定
                else:
                    del self.locked_accounts[username]  # 解除锁定
            
            # 验证用户名
            if username not in self.users:
                self._record_failed_attempt(username, source_ip)
                return None
            
            user = self.users[username]
            
            # 验证密码
            if not self.encryption_manager.verify_password(password, 
                                                          user.password_hash, 
                                                          user.salt):
                self._record_failed_attempt(username, source_ip)
                return None
            
            # 生成会话令牌
            token = self.encryption_manager.generate_secure_token()
            user.session_tokens.append(token)
            self.session_tokens[token] = username
            
            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            
            return token
    
    def verify_token(self, token: str) -> Optional[str]:
        """验证会话令牌"""
        with self.lock:
            return self.session_tokens.get(token)
    
    def logout_user(self, token: str) -> bool:
        """用户登出"""
        with self.lock:
            username = self.session_tokens.get(token)
            if username:
                user = self.users.get(username)
                if user and token in user.session_tokens:
                    user.session_tokens.remove(token)
                del self.session_tokens[token]
                return True
            return False
    
    def revoke_user_sessions(self, username: str) -> bool:
        """撤销用户所有会话"""
        with self.lock:
            if username in self.users:
                user = self.users[username]
                for token in user.session_tokens.copy():
                    del self.session_tokens[token]
                user.session_tokens.clear()
                return True
            return False
    
    def _validate_password_strength(self, password: str) -> List[str]:
        """验证密码强度"""
        issues = []
        
        if len(password) < 12:
            issues.append("密码长度至少12位")
        
        if not re.search(r'[A-Z]', password):
            issues.append("密码必须包含大写字母")
        
        if not re.search(r'[a-z]', password):
            issues.append("密码必须包含小写字母")
        
        if not re.search(r'[0-9]', password):
            issues.append("密码必须包含数字")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("密码必须包含特殊字符")
        
        # 检查常见模式
        common_patterns = ['123456', 'password', 'qwerty', 'admin']
        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                issues.append("密码包含常见模式")
                break
        
        return issues
    
    def _record_failed_attempt(self, username: str, source_ip: str):
        """记录失败尝试"""
        current_time = time.time()
        self.failed_attempts[username].append(current_time)
        
        # 清理过期的失败记录
        cutoff_time = current_time - 3600  # 1小时前
        while (self.failed_attempts[username] and 
               self.failed_attempts[username][0] < cutoff_time):
            self.failed_attempts[username].popleft()
        
        # 检查是否超过失败次数限制
        if len(self.failed_attempts[username]) >= 5:  # 5次失败后锁定
            self.locked_accounts[username] = datetime.utcnow()


# 权限管理器
class PermissionManager:
    """权限管理器"""
    
    def __init__(self, authentication_manager: AuthenticationManager):
        self.auth_manager = authentication_manager
        self.acl_rules: List[Dict] = []
        self.role_definitions: Dict[str, Dict] = {
            'application': {
                'tags': 'application',
                'permissions': {
                    'configure': r'^exclusive.*',
                    'write': r'^app\.(exchange|queue)\..*',
                    'read': r'^app\.(queue)\..*'
                }
            },
            'monitoring': {
                'tags': 'monitoring',
                'permissions': {
                    'configure': '',
                    'write': '',
                    'read': '.*'
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
    
    def assign_role(self, username: str, role_name: str) -> bool:
        """分配角色"""
        if role_name not in self.role_definitions:
            return False
        
        if username not in self.auth_manager.users:
            return False
        
        role = self.role_definitions[role_name]
        user = self.auth_manager.users[username]
        
        user.permissions = role['permissions'].copy()
        return True
    
    def create_custom_role(self, role_name: str, permissions: Dict[str, str]):
        """创建自定义角色"""
        self.role_definitions[role_name] = {
            'tags': role_name,
            'permissions': permissions
        }
    
    def check_permission(self, token: str, action: PermissionType, 
                        resource: str, vhost: str = '/') -> bool:
        """检查权限"""
        username = self.auth_manager.verify_token(token)
        if not username:
            return False
        
        user = self.auth_manager.users.get(username)
        if not user or not user.is_active:
            return False
        
        # 检查虚拟主机访问权限
        if vhost not in user.vhost_access:
            return False
        
        # 获取权限配置
        permission_pattern = user.permissions.get(action.value, '')
        
        # 空权限表示没有该操作的权限
        if not permission_pattern:
            return False
        
        # 正则表达式匹配
        return bool(re.match(permission_pattern, resource))
    
    def add_acl_rule(self, condition_func: Callable, permissions: Dict[str, str]):
        """添加ACL规则"""
        self.acl_rules.append({
            'condition': condition_func,
            'permissions': permissions
        })
    
    def get_user_permissions(self, username: str) -> Dict[str, Any]:
        """获取用户权限"""
        user = self.auth_manager.users.get(username)
        if not user:
            return {}
        
        return {
            'permissions': user.permissions,
            'vhost_access': user.vhost_access,
            'role_tags': [tag for tag, config in self.role_definitions.items()
                         if user.permissions == config.get('permissions', {})]
        }


# 安全审计管理器
class SecurityAuditManager:
    """安全审计管理器"""
    
    def __init__(self, log_file: str = 'security_audit.log'):
        self.log_file = log_file
        self.events: List[SecurityEventRecord] = []
        self.lock = threading.Lock()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('security_audit')
    
    def log_event(self, event_type: SecurityEvent, username: str, 
                 source_ip: str, details: Dict[str, Any] = None,
                 security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """记录安全事件"""
        with self.lock:
            event = SecurityEventRecord(
                event_type=event_type,
                timestamp=datetime.utcnow(),
                user_id=username,
                source_ip=source_ip,
                details=details or {},
                security_level=security_level
            )
            
            self.events.append(event)
            
            # 记录到日志文件
            log_message = {
                'event_type': event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'user_id': username,
                'source_ip': source_ip,
                'details': details,
                'security_level': security_level.value
            }
            
            if security_level == SecurityLevel.HIGH:
                self.logger.warning(json.dumps(log_message))
            elif security_level == SecurityLevel.CRITICAL:
                self.logger.error(json.dumps(log_message))
            else:
                self.logger.info(json.dumps(log_message))
            
            # 限制事件记录数量（保留最近10000条）
            if len(self.events) > 10000:
                self.events = self.events[-8000:]  # 保留最新的8000条
    
    def get_events(self, start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  event_type: Optional[SecurityEvent] = None,
                  security_level: Optional[SecurityLevel] = None) -> List[SecurityEventRecord]:
        """查询事件记录"""
        with self.lock:
            filtered_events = self.events.copy()
            
            if start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            
            if end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
            if event_type:
                filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
            if security_level:
                filtered_events = [e for e in filtered_events if e.security_level == security_level]
            
            return sorted(filtered_events, key=lambda x: x.timestamp, reverse=True)
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """生成安全报告"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_events = [e for e in self.events if e.timestamp >= cutoff_time]
            
            # 统计各类型事件数量
            event_counts = defaultdict(int)
            security_level_counts = defaultdict(int)
            
            for event in recent_events:
                event_counts[event.event_type.value] += 1
                security_level_counts[event.security_level.value] += 1
            
            # 计算安全指标
            failed_logins = event_counts[SecurityEvent.LOGIN_FAILURE.value]
            successful_logins = event_counts[SecurityEvent.LOGIN_SUCCESS.value]
            failed_rate = failed_logins / max(failed_logins + successful_logins, 1)
            
            return {
                'report_period_hours': hours,
                'total_events': len(recent_events),
                'event_counts': dict(event_counts),
                'security_level_counts': dict(security_level_counts),
                'failed_login_rate': failed_rate,
                'timestamp': datetime.utcnow().isoformat()
            }


# 合规性检查器
class ComplianceChecker:
    """合规性检查器"""
    
    def __init__(self):
        self.compliance_rules = {
            'password_policy': self._check_password_policy,
            'access_control': self._check_access_control,
            'audit_logging': self._check_audit_logging,
            'encryption': self._check_encryption
        }
    
    def run_compliance_check(self, auth_manager: AuthenticationManager,
                           audit_manager: SecurityAuditManager) -> Dict[str, Any]:
        """运行合规性检查"""
        results = {}
        
        for rule_name, check_function in self.compliance_rules.items():
            try:
                result = check_function(auth_manager, audit_manager)
                results[rule_name] = result
            except Exception as e:
                results[rule_name] = {
                    'compliant': False,
                    'error': str(e)
                }
        
        # 计算总体合规性
        overall_compliant = all(
            result.get('compliant', False) for result in results.values()
        )
        
        return {
            'overall_compliant': overall_compliant,
            'rule_results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_password_policy(self, auth_manager: AuthenticationManager, 
                              audit_manager: SecurityAuditManager) -> Dict[str, Any]:
        """检查密码策略"""
        issues = []
        
        for username, user in auth_manager.users.items():
            # 检查是否有密码（密码哈希不为空）
            if not user.password_hash:
                issues.append(f"用户 {username} 没有设置密码")
            
            # 检查账户是否被锁定
            if username in auth_manager.locked_accounts:
                issues.append(f"用户 {username} 账户被锁定")
            
            # 检查最后登录时间
            if user.last_login:
                days_since_login = (datetime.utcnow() - user.last_login).days
                if days_since_login > 90:
                    issues.append(f"用户 {username} 超过90天未登录")
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def _check_access_control(self, auth_manager: AuthenticationManager,
                            audit_manager: SecurityAuditManager) -> Dict[str, Any]:
        """检查访问控制"""
        issues = []
        
        # 检查管理员权限用户数量
        admin_count = 0
        for user in auth_manager.users.values():
            if user.permissions.get('configure') == '.*':
                admin_count += 1
        
        if admin_count > 2:
            issues.append(f"管理员权限用户过多: {admin_count}")
        
        # 检查未使用账户
        current_time = datetime.utcnow()
        for username, user in auth_manager.users.items():
            if (user.last_login and 
                current_time - user.last_login > timedelta(days=30)):
                # 检查最近30天是否有权限使用记录
                recent_events = audit_manager.get_events(
                    start_time=current_time - timedelta(days=30)
                )
                has_permission_use = any(
                    e.user_id == username and e.event_type in [
                        SecurityEvent.LOGIN_SUCCESS,
                        SecurityEvent.UNAUTHORIZED_ACCESS
                    ] for e in recent_events
                )
                if not has_permission_use:
                    issues.append(f"用户 {username} 30天内未使用权限")
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def _check_audit_logging(self, auth_manager: AuthenticationManager,
                           audit_manager: SecurityAuditManager) -> Dict[str, Any]:
        """检查审计日志"""
        issues = []
        
        # 检查最近的登录事件
        recent_events = audit_manager.get_events(
            start_time=datetime.utcnow() - timedelta(days=7)
        )
        
        login_events = [
            e for e in recent_events 
            if e.event_type in [SecurityEvent.LOGIN_SUCCESS, SecurityEvent.LOGIN_FAILURE]
        ]
        
        if len(login_events) == 0:
            issues.append("过去7天内没有登录事件记录")
        
        # 检查高级别安全事件
        critical_events = [
            e for e in recent_events 
            if e.security_level == SecurityLevel.CRITICAL
        ]
        
        if critical_events:
            issues.append(f"检测到 {len(critical_events)} 个关键安全事件")
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    def _check_encryption(self, auth_manager: AuthenticationManager,
                        audit_manager: SecurityAuditManager) -> Dict[str, Any]:
        """检查加密策略"""
        issues = []
        
        # 这里可以添加具体的加密检查逻辑
        # 例如：检查密码哈希算法强度、证书有效性等
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues
        }


# 安全监控器
class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self, auth_manager: AuthenticationManager,
                 audit_manager: SecurityAuditManager,
                 alert_threshold: int = 10):
        self.auth_manager = auth_manager
        self.audit_manager = audit_manager
        self.alert_threshold = alert_threshold
        self.monitoring_active = False
        self.monitor_thread = None
        self.alert_handlers: List[Callable] = []
    
    def add_alert_handler(self, handler: Callable):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def start_monitoring(self):
        """启动监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                self._check_failed_login_attempts()
                self._detect_suspicious_activity()
                self._check_security_events()
                
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                print(f"安全监控错误: {e}")
                time.sleep(60)
    
    def _check_failed_login_attempts(self):
        """检查失败登录尝试"""
        current_time = datetime.utcnow()
        recent_failures = self.audit_manager.get_events(
            start_time=current_time - timedelta(minutes=5)
        )
        
        failed_logins = [
            e for e in recent_failures 
            if e.event_type == SecurityEvent.LOGIN_FAILURE
        ]
        
        # 按IP统计失败次数
        ip_failures = defaultdict(int)
        for event in failed_logins:
            ip_failures[event.source_ip] += 1
        
        # 检查是否超过阈值
        for ip, count in ip_failures.items():
            if count >= self.alert_threshold:
                self._trigger_alert(
                    f"IP地址 {ip} 5分钟内失败登录尝试 {count} 次",
                    SecurityLevel.HIGH,
                    {'ip': ip, 'failed_attempts': count}
                )
    
    def _detect_suspicious_activity(self):
        """检测可疑活动"""
        current_time = datetime.utcnow()
        
        # 检查非工作时间的登录
        recent_logins = self.audit_manager.get_events(
            start_time=current_time - timedelta(hours=1)
        )
        
        successful_logins = [
            e for e in recent_logins 
            if e.event_type == SecurityEvent.LOGIN_SUCCESS
        ]
        
        for event in successful_logins:
            login_hour = event.timestamp.hour
            
            # 非工作时间登录（假设工作时间9-17点）
            if not (9 <= login_hour <= 17):
                self._trigger_alert(
                    f"用户 {event.user_id} 在非工作时间登录",
                    SecurityLevel.MEDIUM,
                    {'user': event.user_id, 'login_time': event.timestamp.isoformat()}
                )
    
    def _check_security_events(self):
        """检查安全事件"""
        current_time = datetime.utcnow()
        recent_events = self.audit_manager.get_events(
            start_time=current_time - timedelta(minutes=10)
        )
        
        critical_events = [
            e for e in recent_events 
            if e.security_level == SecurityLevel.CRITICAL
        ]
        
        for event in critical_events:
            self._trigger_alert(
                f"检测到关键安全事件: {event.event_type.value}",
                SecurityLevel.CRITICAL,
                {
                    'event_type': event.event_type.value,
                    'user': event.user_id,
                    'source_ip': event.source_ip,
                    'details': event.details
                }
            )
    
    def _trigger_alert(self, message: str, level: SecurityLevel, context: Dict[str, Any]):
        """触发告警"""
        print(f"安全告警 [{level.value}]: {message}")
        
        # 调用告警处理器
        for handler in self.alert_handlers:
            try:
                handler(message, level, context)
            except Exception as e:
                print(f"告警处理器错误: {e}")


# RabbitMQ安全连接管理器
class SecureRabbitMQConnection:
    """安全的RabbitMQ连接管理器"""
    
    def __init__(self, host: str = 'localhost', port: int = 5671,
                 virtual_host: str = '/', ssl_enabled: bool = True,
                 ca_cert: Optional[str] = None, 
                 client_cert: Optional[str] = None,
                 client_key: Optional[str] = None):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.ssl_enabled = ssl_enabled
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.client_key = client_key
        self.connection = None
        self.channel = None
    
    def connect(self, username: str, password: str, 
               token: Optional[str] = None) -> bool:
        """建立安全连接"""
        try:
            # 准备连接参数
            credentials = pika.PlainCredentials(username, password)
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # 配置SSL
            if self.ssl_enabled:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = True
                ssl_context.verify_mode = ssl.CERT_REQUIRED
                
                if self.ca_cert:
                    ssl_context.load_verify_locations(self.ca_cert)
                
                if self.client_cert and self.client_key:
                    ssl_context.load_cert_chain(self.client_cert, self.client_key)
                
                ssl_options = pika.SSLOptions(ssl_context, server_hostname=self.host)
                connection_params.ssl_options = ssl_options
            
            # 建立连接
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            return True
            
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def secure_publish(self, exchange: str, routing_key: str, 
                      message: Union[str, bytes], 
                      encryption_manager: Optional[EncryptionManager] = None):
        """安全发布消息"""
        try:
            body = message
            
            # 如果提供了加密管理器，启用消息加密
            if encryption_manager:
                if isinstance(message, str):
                    message = message.encode()
                encrypted_message = encryption_manager.encrypt_message(message)
                body = encrypted_message
                # 添加加密标记头
                properties = pika.BasicProperties(
                    content_type='application/json',
                    headers={'encrypted': True}
                )
            else:
                properties = pika.BasicProperties(content_type='text/plain')
            
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=True
            )
            
            return True
            
        except Exception as e:
            print(f"消息发布失败: {e}")
            return False
    
    def secure_consume(self, queue: str, callback: Callable,
                      decryption_manager: Optional[EncryptionManager] = None):
        """安全消费消息"""
        def secure_callback(ch, method, properties, body):
            try:
                message = body
                
                # 如果启用了加密，尝试解密消息
                if (decryption_manager and 
                    properties.headers and 
                    properties.headers.get('encrypted')):
                    decrypted_bytes = decryption_manager.decrypt_message(message)
                    message = decrypted_bytes.decode()
                
                # 调用原始回调
                callback(ch, method, properties, message)
                
            except Exception as e:
                print(f"消息处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # 开始消费
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=secure_callback,
            auto_ack=False
        )
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
    
    def close(self):
        """关闭连接"""
        if self.channel:
            self.channel.close()
        
        if self.connection:
            self.connection.close()


# 安全配置管理器
class SecurityConfigManager:
    """安全配置管理器"""
    
    def __init__(self, config_file: str = 'security_config.yaml'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        default_config = {
            'rabbitmq': {
                'host': 'localhost',
                'port': 5671,
                'ssl_enabled': True,
                'virtual_host': '/'
            },
            'authentication': {
                'method': 'password',
                'session_timeout': 3600,
                'max_failed_attempts': 5,
                'lockout_duration': 3600
            },
            'encryption': {
                'algorithm': 'AES-256-GCM',
                'key_size': 32,
                'iv_size': 12,
                'salt_size': 16,
                'iterations': 100000
            },
            'audit': {
                'log_file': 'security_audit.log',
                'retention_days': 30,
                'enable_real_time_monitoring': True
            },
            'compliance': {
                'password_min_length': 12,
                'require_complex_passwords': True,
                'session_timeout_days': 30,
                'audit_log_retention_days': 90
            }
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """保存配置"""
        if config:
            self.config = config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到最后一级的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        self.save_config()


# 集成安全管理器
class IntegratedSecurityManager:
    """集成安全管理器"""
    
    def __init__(self, config_file: str = 'security_config.yaml'):
        self.config_manager = SecurityConfigManager(config_file)
        self.encryption_manager = EncryptionManager()
        self.auth_manager = AuthenticationManager(self.encryption_manager)
        self.permission_manager = PermissionManager(self.auth_manager)
        self.audit_manager = SecurityAuditManager()
        self.compliance_checker = ComplianceChecker()
        self.security_monitor = SecurityMonitor(self.auth_manager, self.audit_manager)
    
    def initialize_default_users(self):
        """初始化默认用户"""
        try:
            # 创建管理员用户
            admin_password = self.encryption_manager.generate_password()
            self.auth_manager.register_user(
                username='admin',
                password=admin_password,
                auth_method=AuthMethod.PASSWORD,
                permissions={
                    'configure': '.*',
                    'write': '.*',
                    'read': '.*'
                },
                vhost_access=['/']
            )
            self.permission_manager.assign_role('admin', 'management')
            
            # 创建应用程序用户
            app_password = self.encryption_manager.generate_password()
            self.auth_manager.register_user(
                username='app_user',
                password=app_password,
                auth_method=AuthMethod.PASSWORD,
                permissions={
                    'configure': '^exclusive.*',
                    'write': '^app\.(exchange|queue)\..*',
                    'read': '^app\.(queue)\..*'
                },
                vhost_access=['/', 'app_vhost']
            )
            self.permission_manager.assign_role('app_user', 'application')
            
            # 创建监控用户
            monitor_password = self.encryption_manager.generate_password()
            self.auth_manager.register_user(
                username='monitor_user',
                password=monitor_password,
                auth_method=AuthMethod.PASSWORD,
                permissions={
                    'configure': '',
                    'write': '',
                    'read': '.*'
                },
                vhost_access=['/']
            )
            self.permission_manager.assign_role('monitor_user', 'monitoring')
            
            # 记录初始化事件
            self.audit_manager.log_event(
                SecurityEvent.SYSTEM_COMPROMISE,
                'system',
                'localhost',
                {'action': 'initialize_default_users'},
                SecurityLevel.LOW
            )
            
            return {
                'admin': {'password': admin_password},
                'app_user': {'password': app_password},
                'monitor_user': {'password': monitor_password}
            }
            
        except Exception as e:
            self.audit_manager.log_event(
                SecurityEvent.SYSTEM_COMPROMISE,
                'system',
                'localhost',
                {'action': 'initialize_default_users', 'error': str(e)},
                SecurityLevel.CRITICAL
            )
            raise
    
    def run_security_assessment(self) -> Dict[str, Any]:
        """运行安全评估"""
        assessment_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'compliance_check': self.compliance_checker.run_compliance_check(
                self.auth_manager, self.audit_manager
            ),
            'security_report': self.audit_manager.generate_security_report(),
            'user_summary': {
                'total_users': len(self.auth_manager.users),
                'locked_accounts': len(self.auth_manager.locked_accounts),
                'active_sessions': len(self.auth_manager.session_tokens)
            }
        }
        
        return assessment_result
    
    def start_comprehensive_monitoring(self):
        """启动全面监控"""
        # 添加默认告警处理器
        def email_alert_handler(message: str, level: SecurityLevel, context: Dict):
            # 这里可以实现邮件发送逻辑
            print(f"邮件告警 [{level.value}]: {message}")
        
        def sms_alert_handler(message: str, level: SecurityLevel, context: Dict):
            # 这里可以实现短信发送逻辑
            if level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                print(f"短信告警 [{level.value}]: {message}")
        
        # 注册告警处理器
        self.security_monitor.add_alert_handler(email_alert_handler)
        self.security_monitor.add_alert_handler(sms_alert_handler)
        
        # 启动监控
        self.security_monitor.start_monitoring()


# 演示函数
def demonstrate_security_manager():
    """演示安全管理器功能"""
    print("=== RabbitMQ安全管理器演示 ===\n")
    
    # 创建集成安全管理器
    security_manager = IntegratedSecurityManager()
    
    # 初始化默认用户
    print("1. 初始化默认用户...")
    default_passwords = security_manager.initialize_default_users()
    print("默认用户创建成功:")
    for user, creds in default_passwords.items():
        print(f"  用户: {user}, 密码: {creds['password']}")
    print()
    
    # 用户认证演示
    print("2. 用户认证演示...")
    
    # 管理员登录
    admin_token = security_manager.auth_manager.authenticate_user(
        'admin', default_passwords['admin']['password'], '192.168.1.100'
    )
    print(f"管理员登录令牌: {admin_token[:20]}...")
    
    # 应用程序用户登录
    app_token = security_manager.auth_manager.authenticate_user(
        'app_user', default_passwords['app_user']['password'], '192.168.1.101'
    )
    print(f"应用用户登录令牌: {app_token[:20]}...")
    print()
    
    # 权限检查演示
    print("3. 权限检查演示...")
    
    # 检查管理员权限
    admin_has_permission = security_manager.permission_manager.check_permission(
        admin_token, PermissionType.CONFIGURE, 'amq.direct', '/'
    )
    print(f"管理员对 amq.direct 的配置权限: {admin_has_permission}")
    
    # 检查应用用户权限
    app_has_permission = security_manager.permission_manager.check_permission(
        app_token, PermissionType.CONFIGURE, 'exclusive_queue', 'app_vhost'
    )
    print(f"应用用户对 exclusive_queue 的配置权限: {app_has_permission}")
    
    # 检查应用用户对永久队列的权限（应该被拒绝）
    app_denied_permission = security_manager.permission_manager.check_permission(
        app_token, PermissionType.CONFIGURE, 'amq.direct', 'app_vhost'
    )
    print(f"应用用户对 amq.direct 的配置权限（应该为False）: {app_denied_permission}")
    print()
    
    # 失败登录演示
    print("4. 失败登录演示...")
    
    # 模拟多次失败登录
    for i in range(3):
        success = security_manager.auth_manager.authenticate_user(
            'admin', 'wrong_password', '192.168.1.200'
        )
        print(f"第{i+1}次失败登录尝试: {'成功' if success else '失败'}")
    
    # 记录安全事件
    security_manager.audit_manager.log_event(
        SecurityEvent.SUSPICIOUS_ACTIVITY,
        'admin',
        '192.168.1.200',
        {'action': 'multiple_failed_logins'},
        SecurityLevel.HIGH
    )
    
    # 安全事件查询
    recent_events = security_manager.audit_manager.get_events(
        start_time=datetime.utcnow() - timedelta(minutes=5)
    )
    print(f"最近5分钟的安全事件数量: {len(recent_events)}")
    print()
    
    # 安全报告生成
    print("5. 安全报告生成...")
    security_report = security_manager.audit_manager.generate_security_report()
    print("安全报告概要:")
    print(f"  报告时间范围: {security_report['report_period_hours']}小时")
    print(f"  总事件数: {security_report['total_events']}")
    print(f"  事件类型分布: {security_report['event_counts']}")
    print(f"  安全级别分布: {security_report['security_level_counts']}")
    print(f"  登录失败率: {security_report['failed_login_rate']:.2%}")
    print()
    
    # 合规性检查
    print("6. 合规性检查...")
    compliance_result = security_manager.compliance_checker.run_compliance_check(
        security_manager.auth_manager,
        security_manager.audit_manager
    )
    print(f"总体合规性: {'合规' if compliance_result['overall_compliant'] else '不合规'}")
    print("合规检查详情:")
    for rule, result in compliance_result['rule_results'].items():
        status = '合规' if result['compliant'] else '不合规'
        print(f"  {rule}: {status}")
        if not result['compliant'] and 'issues' in result:
            for issue in result['issues']:
                print(f"    - {issue}")
    print()
    
    # 安全配置示例
    print("7. 安全配置管理...")
    config_manager = security_manager.config_manager
    
    # 获取当前配置
    current_host = config_manager.get('rabbitmq.host')
    print(f"当前RabbitMQ主机: {current_host}")
    
    # 修改配置
    config_manager.set('rabbitmq.port', 5671)
    new_port = config_manager.get('rabbitmq.port')
    print(f"更新后的端口: {new_port}")
    print()
    
    # 安全连接演示
    print("8. 安全连接演示...")
    secure_conn = SecureRabbitMQConnection(
        host='localhost',
        port=5671,
        ssl_enabled=True
    )
    
    # 这里演示如何使用安全连接（实际使用需要RabbitMQ服务器）
    # connection_success = secure_conn.connect(
    #     'app_user', 
    #     default_passwords['app_user']['password'],
    #     app_token
    # )
    # print(f"安全连接建立: {'成功' if connection_success else '失败'}")
    print("安全连接配置已准备就绪")
    print()
    
    # 安全评估报告
    print("9. 综合安全评估...")
    assessment = security_manager.run_security_assessment()
    print("综合安全评估报告:")
    print(f"  用户总数: {assessment['user_summary']['total_users']}")
    print(f"  锁定账户: {assessment['user_summary']['locked_accounts']}")
    print(f"  活跃会话: {assessment['user_summary']['active_sessions']}")
    print(f"  合规状态: {'合规' if assessment['compliance_check']['overall_compliant'] else '不合规'}")
    print()
    
    print("=== 安全演示完成 ===")
    
    return security_manager


if __name__ == "__main__":
    # 运行演示
    security_manager = demonstrate_security_manager()
    
    # 可选：启动实时监控
    print("\n启动实时安全监控...")
    security_manager.start_comprehensive_monitoring()
    
    try:
        # 保持程序运行以便观察监控效果
        print("监控已启动，按Ctrl+C退出...")
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n停止监控...")
        security_manager.security_monitor.stop_monitoring()
        print("演示结束。")