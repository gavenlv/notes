#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ安全与认证 - 代码示例
==================================

本文件包含RabbitMQ安全与认证的完整示例代码，涵盖：
- 用户认证和权限管理
- SSL/TLS加密配置
- 访问控制列表(ACL)
- 安全策略配置
- 审计日志记录
- 安全监控和检测

作者：RabbitMQ学习团队
版本：1.0.0
"""

import ssl
import json
import time
import logging
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import pika
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import uuid


class PermissionType(Enum):
    """权限类型枚举"""
    CONFIGURE = "configure"
    READ = "read"
    WRITE = "write"


class AuthenticationMethod(Enum):
    """认证方法枚举"""
    USERNAME_PASSWORD = "username_password"
    X509_CERTIFICATE = "x509_certificate"
    LDAP = "ldap"
    JWT_TOKEN = "jwt_token"


@dataclass
class UserInfo:
    """用户信息数据类"""
    username: str
    password_hash: str
    authentication_method: AuthenticationMethod
    permissions: List[PermissionType]
    virtual_host_access: List[str]
    tags: List[str]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    certificate_fingerprint: Optional[str]


@dataclass
class SecurityPolicy:
    """安全策略数据类"""
    policy_name: str
    password_policy: Dict[str, Any]
    session_timeout: int
    max_login_attempts: int
    ssl_required: bool
    ip_whitelist: List[str]
    audit_enabled: bool
    encryption_algorithms: List[str]


@dataclass
class AuditLog:
    """审计日志数据类"""
    log_id: str
    timestamp: datetime
    user: str
    action: str
    resource: str
    result: str
    ip_address: str
    additional_info: Dict[str, Any]


class PasswordManager:
    """密码管理器"""
    
    def __init__(self, master_password: str = None):
        if master_password:
            self.master_password = master_password.encode()
            self.key = self._derive_key(self.master_password)
            self.cipher_suite = Fernet(self.key)
        else:
            self.master_password = None
            self.key = None
            self.cipher_suite = None
    
    def _derive_key(self, password: bytes, salt: bytes = b'salt_rabbitmq_security') -> bytes:
        """从密码派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """密码哈希"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # 使用PBKDF2进行哈希
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
        )
        hash_result = kdf.derive(password_bytes)
        
        return base64.b64encode(hash_result).decode(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """验证密码"""
        try:
            calculated_hash, _ = self.hash_password(password, salt)
            return calculated_hash == stored_hash
        except:
            return False
    
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        if not self.cipher_suite:
            raise ValueError("未设置主密码，无法加密数据")
        
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        if not self.cipher_suite:
            raise ValueError("未设置主密码，无法解密数据")
        
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()


class AuthenticationManager:
    """认证管理器"""
    
    def __init__(self):
        self.users: Dict[str, UserInfo] = {}
        self.password_manager = PasswordManager()
        self.logger = logging.getLogger(__name__)
        self.login_attempts: Dict[str, List[datetime]] = {}
        self.active_sessions: Dict[str, datetime] = {}
    
    def create_user(self, username: str, password: str, 
                   authentication_method: AuthenticationMethod = AuthenticationMethod.USERNAME_PASSWORD,
                   permissions: List[PermissionType] = None,
                   virtual_host_access: List[str] = None,
                   tags: List[str] = None) -> bool:
        """创建用户"""
        try:
            # 检查用户是否已存在
            if username in self.users:
                self.logger.warning(f"用户已存在: {username}")
                return False
            
            # 密码策略检查
            if not self._validate_password_policy(password):
                self.logger.warning(f"密码不符合策略要求: {username}")
                return False
            
            # 哈希密码
            password_hash, salt = self.password_manager.hash_password(password)
            
            # 创建用户信息
            user_info = UserInfo(
                username=username,
                password_hash=password_hash,
                authentication_method=authentication_method,
                permissions=permissions or [PermissionType.READ, PermissionType.WRITE],
                virtual_host_access=virtual_host_access or ["/"],
                tags=tags or ["user"],
                created_at=datetime.now(),
                last_login=None,
                is_active=True,
                certificate_fingerprint=None
            )
            
            self.users[username] = user_info
            self.logger.info(f"用户创建成功: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建用户失败: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = "127.0.0.1") -> Tuple[bool, str]:
        """用户认证"""
        try:
            # 检查登录尝试次数
            if not self._check_login_attempts(username, ip_address):
                return False, "登录尝试次数过多，请稍后再试"
            
            # 检查用户是否存在且活跃
            if username not in self.users:
                self._record_failed_attempt(username, ip_address)
                return False, "用户不存在或密码错误"
            
            user_info = self.users[username]
            if not user_info.is_active:
                self._record_failed_attempt(username, ip_address)
                return False, "用户已被禁用"
            
            # 验证密码
            if user_info.authentication_method == AuthenticationMethod.USERNAME_PASSWORD:
                if not self.password_manager.verify_password(
                    password, user_info.password_hash, user_info.password_hash.split('.')[1] if '.' in user_info.password_hash else ""):
                    self._record_failed_attempt(username, ip_address)
                    return False, "用户不存在或密码错误"
            
            # 认证成功
            user_info.last_login = datetime.now()
            self._clear_login_attempts(username)
            self._create_session(username)
            
            self.logger.info(f"用户认证成功: {username}")
            return True, "认证成功"
            
        except Exception as e:
            self.logger.error(f"用户认证失败: {e}")
            return False, "认证过程中发生错误"
    
    def revoke_user(self, username: str) -> bool:
        """禁用用户"""
        try:
            if username in self.users:
                self.users[username].is_active = False
                self._invalidate_session(username)
                self.logger.info(f"用户已禁用: {username}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"禁用用户失败: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """删除用户"""
        try:
            if username in self.users:
                del self.users[username]
                self._invalidate_session(username)
                self.logger.info(f"用户已删除: {username}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"删除用户失败: {e}")
            return False
    
    def update_password(self, username: str, old_password: str, new_password: str) -> bool:
        """更新密码"""
        try:
            if username not in self.users:
                return False
            
            # 验证旧密码
            if not self.authenticate_user(username, old_password)[0]:
                return False
            
            # 检查新密码策略
            if not self._validate_password_policy(new_password):
                return False
            
            # 更新密码
            user_info = self.users[username]
            password_hash, salt = self.password_manager.hash_password(new_password)
            user_info.password_hash = password_hash
            
            self.logger.info(f"密码已更新: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新密码失败: {e}")
            return False
    
    def _validate_password_policy(self, password: str) -> bool:
        """验证密码策略"""
        policy = {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digits': True,
            'require_special_chars': True
        }
        
        # 检查最小长度
        if len(password) < policy['min_length']:
            return False
        
        # 检查大写字母
        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            return False
        
        # 检查小写字母
        if policy['require_lowercase'] and not any(c.islower() for c in password):
            return False
        
        # 检查数字
        if policy['require_digits'] and not any(c.isdigit() for c in password):
            return False
        
        # 检查特殊字符
        if policy['require_special_chars'] and not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
            return False
        
        return True
    
    def _check_login_attempts(self, username: str, ip_address: str) -> bool:
        """检查登录尝试次数"""
        key = f"{username}:{ip_address}"
        now = datetime.now()
        
        if key not in self.login_attempts:
            self.login_attempts[key] = []
        
        # 清理过期的尝试记录
        self.login_attempts[key] = [
            attempt_time for attempt_time in self.login_attempts[key]
            if (now - attempt_time).total_seconds() < 3600  # 1小时窗口
        ]
        
        # 检查尝试次数
        if len(self.login_attempts[key]) >= 5:  # 最多5次尝试
            return False
        
        return True
    
    def _record_failed_attempt(self, username: str, ip_address: str):
        """记录失败的登录尝试"""
        key = f"{username}:{ip_address}"
        if key not in self.login_attempts:
            self.login_attempts[key] = []
        
        self.login_attempts[key].append(datetime.now())
    
    def _clear_login_attempts(self, username: str):
        """清除登录尝试记录"""
        keys_to_remove = [key for key in self.login_attempts.keys() if key.startswith(f"{username}:")]
        for key in keys_to_remove:
            del self.login_attempts[key]
    
    def _create_session(self, username: str):
        """创建会话"""
        session_token = secrets.token_urlsafe(32)
        self.active_sessions[session_token] = datetime.now()
        # 在实际应用中，应该将token返回给客户端
    
    def _invalidate_session(self, username: str):
        """使会话失效"""
        # 在实际应用中，需要根据用户查找对应的session token
        pass


class AccessControlManager:
    """访问控制管理器"""
    
    def __init__(self, authentication_manager: AuthenticationManager):
        self.auth_manager = authentication_manager
        self.logger = logging.getLogger(__name__)
        self.resource_permissions: Dict[str, Set[PermissionType]] = {}
        self.user_permissions: Dict[str, Dict[str, Set[PermissionType]]] = {}
    
    def grant_permission(self, username: str, resource: str, 
                        permission: PermissionType) -> bool:
        """授予权限"""
        try:
            if username not in self.auth_manager.users:
                return False
            
            if username not in self.user_permissions:
                self.user_permissions[username] = {}
            
            if resource not in self.user_permissions[username]:
                self.user_permissions[username][resource] = set()
            
            self.user_permissions[username][resource].add(permission)
            self.logger.info(f"权限已授予: {username} -> {resource}:{permission}")
            return True
            
        except Exception as e:
            self.logger.error(f"授予权限失败: {e}")
            return False
    
    def revoke_permission(self, username: str, resource: str, 
                         permission: PermissionType) -> bool:
        """撤销权限"""
        try:
            if (username in self.user_permissions and 
                resource in self.user_permissions[username] and
                permission in self.user_permissions[username][resource]):
                
                self.user_permissions[username][resource].discard(permission)
                self.logger.info(f"权限已撤销: {username} -> {resource}:{permission}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"撤销权限失败: {e}")
            return False
    
    def check_permission(self, username: str, resource: str, 
                        permission: PermissionType) -> bool:
        """检查权限"""
        try:
            # 检查用户是否存在且活跃
            if username not in self.auth_manager.users:
                return False
            
            user_info = self.auth_manager.users[username]
            if not user_info.is_active:
                return False
            
            # 检查用户是否有该资源的权限
            if (username in self.user_permissions and 
                resource in self.user_permissions[username] and
                permission in self.user_permissions[username][resource]):
                return True
            
            # 检查资源默认权限
            if resource in self.resource_permissions:
                return permission in self.resource_permissions[resource]
            
            return False
            
        except Exception as e:
            self.logger.error(f"权限检查失败: {e}")
            return False
    
    def set_default_permissions(self, resource: str, permissions: List[PermissionType]):
        """设置默认权限"""
        self.resource_permissions[resource] = set(permissions)
    
    def get_user_permissions(self, username: str) -> Dict[str, List[PermissionType]]:
        """获取用户权限"""
        user_perms = {}
        
        if username in self.user_permissions:
            for resource, perms in self.user_permissions[username].items():
                user_perms[resource] = list(perms)
        
        return user_perms


class SecurityPolicyManager:
    """安全策略管理器"""
    
    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_policy(self, policy_name: str, 
                     password_policy: Dict[str, Any] = None,
                     session_timeout: int = 3600,
                     max_login_attempts: int = 5,
                     ssl_required: bool = True,
                     ip_whitelist: List[str] = None,
                     audit_enabled: bool = True,
                     encryption_algorithms: List[str] = None) -> bool:
        """创建安全策略"""
        try:
            policy = SecurityPolicy(
                policy_name=policy_name,
                password_policy=password_policy or {
                    'min_length': 8,
                    'require_uppercase': True,
                    'require_lowercase': True,
                    'require_digits': True,
                    'require_special_chars': True
                },
                session_timeout=session_timeout,
                max_login_attempts=max_login_attempts,
                ssl_required=ssl_required,
                ip_whitelist=ip_whitelist or [],
                audit_enabled=audit_enabled,
                encryption_algorithms=encryption_algorithms or ['AES256', 'SHA256']
            )
            
            self.policies[policy_name] = policy
            self.logger.info(f"安全策略已创建: {policy_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建安全策略失败: {e}")
            return False
    
    def apply_policy(self, policy_name: str) -> bool:
        """应用安全策略"""
        try:
            if policy_name not in self.policies:
                return False
            
            policy = self.policies[policy_name]
            
            # 这里应该将策略应用到实际的RabbitMQ配置中
            # 实际实现需要根据具体的RabbitMQ配置方式进行调整
            
            self.logger.info(f"安全策略已应用: {policy_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"应用安全策略失败: {e}")
            return False
    
    def validate_policy(self, policy_name: str) -> Tuple[bool, List[str]]:
        """验证安全策略"""
        issues = []
        
        if policy_name not in self.policies:
            issues.append("策略不存在")
            return False, issues
        
        policy = self.policies[policy_name]
        
        # 检查密码策略
        password_policy = policy.password_policy
        if password_policy.get('min_length', 0) < 6:
            issues.append("密码最小长度不能少于6位")
        
        # 检查会话超时
        if policy.session_timeout < 300:  # 最少5分钟
            issues.append("会话超时时间不能少于5分钟")
        
        # 检查登录尝试次数
        if policy.max_login_attempts < 3:
            issues.append("最大登录尝试次数不能少于3次")
        
        return len(issues) == 0, issues


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.audit_handler = logging.FileHandler(log_file)
        self.audit_handler.setLevel(logging.INFO)
        self.audit_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        self.audit_handler.setFormatter(self.audit_formatter)
        self.logger.addHandler(self.audit_handler)
        self.logger.setLevel(logging.INFO)
        
        self.audit_logs: List[AuditLog] = []
    
    def log_event(self, user: str, action: str, resource: str, 
                 result: str, ip_address: str = "127.0.0.1",
                 additional_info: Dict[str, Any] = None):
        """记录审计事件"""
        try:
            audit_log = AuditLog(
                log_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user=user,
                action=action,
                resource=resource,
                result=result,
                ip_address=ip_address,
                additional_info=additional_info or {}
            )
            
            self.audit_logs.append(audit_log)
            
            # 记录到日志文件
            log_message = json.dumps({
                'log_id': audit_log.log_id,
                'timestamp': audit_log.timestamp.isoformat(),
                'user': audit_log.user,
                'action': audit_log.action,
                'resource': audit_log.resource,
                'result': audit_log.result,
                'ip_address': audit_log.ip_address,
                'additional_info': audit_log.additional_info
            }, ensure_ascii=False)
            
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"记录审计日志失败: {e}")
    
    def get_audit_logs(self, user: str = None, 
                      start_time: datetime = None,
                      end_time: datetime = None) -> List[AuditLog]:
        """获取审计日志"""
        filtered_logs = self.audit_logs
        
        if user:
            filtered_logs = [log for log in filtered_logs if log.user == user]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        return filtered_logs
    
    def generate_security_report(self, days: int = 7) -> Dict[str, Any]:
        """生成安全报告"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        logs = self.get_audit_logs(start_time=start_time, end_time=end_time)
        
        report = {
            'period': f"{start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}",
            'total_events': len(logs),
            'events_by_action': {},
            'events_by_user': {},
            'failed_attempts': 0,
            'successful_logins': 0,
            'top_resources': {}
        }
        
        for log in logs:
            # 按操作统计
            if log.action not in report['events_by_action']:
                report['events_by_action'][log.action] = 0
            report['events_by_action'][log.action] += 1
            
            # 按用户统计
            if log.user not in report['events_by_user']:
                report['events_by_user'][log.user] = 0
            report['events_by_user'][log.user] += 1
            
            # 统计登录尝试
            if log.action == 'login':
                if log.result == 'success':
                    report['successful_logins'] += 1
                else:
                    report['failed_attempts'] += 1
            
            # 统计资源访问
            if log.resource not in report['top_resources']:
                report['top_resources'][log.resource] = 0
            report['top_resources'][log.resource] += 1
        
        return report


class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self, auth_manager: AuthenticationManager, 
                 audit_logger: AuditLogger):
        self.auth_manager = auth_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        self.security_alerts: List[Dict[str, Any]] = []
    
    def detect_suspicious_activity(self) -> List[Dict[str, Any]]:
        """检测可疑活动"""
        alerts = []
        
        try:
            now = datetime.now()
            
            # 检测暴力破解攻击
            brute_force_alerts = self._detect_brute_force_attacks()
            alerts.extend(brute_force_alerts)
            
            # 检测异常登录时间
            unusual_time_alerts = self._detect_unusual_login_times()
            alerts.extend(unusual_time_alerts)
            
            # 检测权限提升尝试
            privilege_escalation_alerts = self._detect_privilege_escalation()
            alerts.extend(privilege_escalation_alerts)
            
            # 检测IP异常
            ip_anomaly_alerts = self._detect_ip_anomalies()
            alerts.extend(ip_anomaly_alerts)
            
            self.security_alerts.extend(alerts)
            return alerts
            
        except Exception as e:
            self.logger.error(f"安全监控检测失败: {e}")
            return []
    
    def _detect_brute_force_attacks(self) -> List[Dict[str, Any]]:
        """检测暴力破解攻击"""
        alerts = []
        
        for user_ip, attempts in self.auth_manager.login_attempts.items():
            recent_attempts = [
                attempt_time for attempt_time in attempts
                if (datetime.now() - attempt_time).total_seconds() < 300  # 5分钟窗口
            ]
            
            if len(recent_attempts) >= 10:  # 5分钟内10次失败尝试
                alerts.append({
                    'alert_type': 'brute_force',
                    'severity': 'high',
                    'user_ip': user_ip,
                    'attempt_count': len(recent_attempts),
                    'time_window': '5 minutes',
                    'description': f'检测到可能的暴力破解攻击: {user_ip}',
                    'timestamp': datetime.now()
                })
        
        return alerts
    
    def _detect_unusual_login_times(self) -> List[Dict[str, Any]]:
        """检测异常登录时间"""
        alerts = []
        now = datetime.now()
        current_hour = now.hour
        
        # 检测非工作时间登录
        if current_hour < 6 or current_hour > 22:  # 晚上10点到早上6点
            for username, user_info in self.auth_manager.users.items():
                if user_info.last_login and user_info.last_login.hour == current_hour:
                    alerts.append({
                        'alert_type': 'unusual_login_time',
                        'severity': 'medium',
                        'user': username,
                        'login_time': user_info.last_login.strftime('%Y-%m-%d %H:%M:%S'),
                        'description': f'用户在非工作时间登录: {username}',
                        'timestamp': now
                    })
        
        return alerts
    
    def _detect_privilege_escalation(self) -> List[Dict[str, Any]]:
        """检测权限提升尝试"""
        # 这个功能需要结合具体的权限变更监控实现
        # 这里提供框架，实际实现需要根据具体的权限系统调整
        return []
    
    def _detect_ip_anomalies(self) -> List[Dict[str, Any]]:
        """检测IP异常"""
        alerts = []
        
        # 检测来自多个不同IP的登录尝试
        ip_by_user = {}
        for user_ip in self.auth_manager.login_attempts.keys():
            user, ip = user_ip.split(':')
            if user not in ip_by_user:
                ip_by_user[user] = set()
            ip_by_user[user].add(ip)
        
        for user, ips in ip_by_user.items():
            if len(ips) > 5:  # 同一用户从5个不同IP登录
                alerts.append({
                    'alert_type': 'ip_anomaly',
                    'severity': 'medium',
                    'user': user,
                    'ip_count': len(ips),
                    'ip_list': list(ips),
                    'description': f'用户 {user} 从多个IP登录',
                    'timestamp': datetime.now()
                })
        
        return alerts
    
    def get_security_status(self) -> Dict[str, Any]:
        """获取安全状态"""
        status = {
            'total_users': len(self.auth_manager.users),
            'active_users': len([u for u in self.auth_manager.users.values() if u.is_active]),
            'inactive_users': len([u for u in self.auth_manager.users.values() if not u.is_active]),
            'login_attempts_last_hour': sum(len(attempts) for attempts in self.auth_manager.login_attempts.values()),
            'active_sessions': len(self.auth_manager.active_sessions),
            'recent_alerts': len([alert for alert in self.security_alerts 
                                if (datetime.now() - alert['timestamp']).total_seconds() < 3600])
        }
        
        return status


class SSLManager:
    """SSL/TLS管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.certificates: Dict[str, Dict[str, str]] = {}
    
    def generate_certificate(self, common_name: str, validity_days: int = 365) -> bool:
        """生成自签名证书（示例用途，生产环境应使用CA颁发的证书）"""
        try:
            # 在实际应用中，这里应该调用openssl或使用cryptography库生成证书
            # 这里只是示例实现
            
            cert_data = {
                'common_name': common_name,
                'validity_days': validity_days,
                'created_at': datetime.now().isoformat(),
                'fingerprint': hashlib.sha256(f"{common_name}{datetime.now()}".encode()).hexdigest()[:16]
            }
            
            self.certificates[common_name] = cert_data
            self.logger.info(f"证书已生成: {common_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成证书失败: {e}")
            return False
    
    def validate_certificate(self, certificate_data: str) -> Tuple[bool, str]:
        """验证证书"""
        try:
            # 这里是简化的验证逻辑，实际应用中需要更完整的验证
            if not certificate_data or len(certificate_data) < 100:
                return False, "证书数据无效"
            
            # 检查证书格式
            if not certificate_data.startswith('-----BEGIN CERTIFICATE-----'):
                return False, "证书格式不正确"
            
            return True, "证书有效"
            
        except Exception as e:
            self.logger.error(f"验证证书失败: {e}")
            return False, f"验证过程中发生错误: {e}"
    
    def get_certificate_info(self, common_name: str) -> Optional[Dict[str, Any]]:
        """获取证书信息"""
        return self.certificates.get(common_name)


class SecurityManager:
    """安全管理器 - 主类"""
    
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.access_manager = AccessControlManager(self.auth_manager)
        self.policy_manager = SecurityPolicyManager()
        self.audit_logger = AuditLogger()
        self.monitor = SecurityMonitor(self.auth_manager, self.audit_logger)
        self.ssl_manager = SSLManager()
        self.logger = logging.getLogger(__name__)
        
        # 创建默认安全策略
        self.policy_manager.create_policy("default_policy")
    
    def setup_secure_environment(self) -> bool:
        """设置安全环境"""
        try:
            # 创建管理员用户
            admin_success = self.auth_manager.create_user(
                username="admin",
                password="Admin123!@#",
                authentication_method=AuthenticationMethod.USERNAME_PASSWORD,
                permissions=[PermissionType.CONFIGURE, PermissionType.READ, PermissionType.WRITE],
                virtual_host_access=["/"],
                tags=["administrator"]
            )
            
            if admin_success:
                self.audit_logger.log_event(
                    user="system",
                    action="create_user",
                    resource="admin",
                    result="success",
                    additional_info={'created_by': 'security_manager'}
                )
            
            # 设置默认权限
            self.access_manager.set_default_permissions("/", [
                PermissionType.READ, PermissionType.WRITE
            ])
            
            # 生成SSL证书
            self.ssl_manager.generate_certificate("rabbitmq-server")
            
            self.logger.info("安全环境设置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"设置安全环境失败: {e}")
            return False
    
    def create_secure_connection(self, username: str, password: str,
                               use_ssl: bool = True) -> Optional[pika.BlockingConnection]:
        """创建安全连接"""
        try:
            # 验证用户凭据
            auth_success, auth_message = self.auth_manager.authenticate_user(username, password)
            
            if not auth_success:
                self.audit_logger.log_event(
                    user=username,
                    action="connect",
                    resource="rabbitmq",
                    result="failed",
                    additional_info={'reason': auth_message}
                )
                return None
            
            # 设置连接参数
            connection_params = pika.ConnectionParameters(
                host='localhost',
                port=5671 if use_ssl else 5672,
                credentials=pika.PlainCredentials(username, password),
                ssl=use_ssl
            )
            
            # 创建连接
            connection = pika.BlockingConnection(connection_params)
            
            # 记录成功的连接
            self.audit_logger.log_event(
                user=username,
                action="connect",
                resource="rabbitmq",
                result="success"
            )
            
            return connection
            
        except Exception as e:
            self.logger.error(f"创建安全连接失败: {e}")
            self.audit_logger.log_event(
                user=username,
                action="connect",
                resource="rabbitmq",
                result="failed",
                additional_info={'error': str(e)}
            )
            return None
    
    def security_audit(self) -> Dict[str, Any]:
        """执行安全审计"""
        try:
            # 生成审计报告
            audit_report = self.audit_logger.generate_security_report()
            
            # 获取安全状态
            security_status = self.monitor.get_security_status()
            
            # 检测可疑活动
            alerts = self.monitor.detect_suspicious_activity()
            
            audit_result = {
                'timestamp': datetime.now().isoformat(),
                'audit_report': audit_report,
                'security_status': security_status,
                'security_alerts': alerts,
                'recommendations': self._generate_security_recommendations(audit_report, security_status, alerts)
            }
            
            return audit_result
            
        except Exception as e:
            self.logger.error(f"安全审计失败: {e}")
            return {'error': str(e)}
    
    def _generate_security_recommendations(self, audit_report: Dict, 
                                         security_status: Dict, 
                                         alerts: List[Dict]) -> List[str]:
        """生成安全建议"""
        recommendations = []
        
        # 基于失败登录尝试的建议
        failed_attempts = audit_report.get('failed_attempts', 0)
        if failed_attempts > 50:
            recommendations.append("检测到大量登录失败，建议启用IP白名单和更严格的密码策略")
        
        # 基于用户活动的建议
        active_users = security_status.get('active_users', 0)
        total_users = security_status.get('total_users', 1)
        if active_users / total_users < 0.5:
            recommendations.append("大量用户处于非活跃状态，建议清理或重新激活用户账户")
        
        # 基于安全警报的建议
        high_severity_alerts = len([alert for alert in alerts if alert.get('severity') == 'high'])
        if high_severity_alerts > 0:
            recommendations.append("检测到高危安全警报，建议立即调查并采取相应措施")
        
        return recommendations


async def main():
    """主函数 - 交互式演示"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建安全管理器
    security_manager = SecurityManager()
    
    print("RabbitMQ安全管理与认证系统")
    print("=" * 50)
    print("1. 设置安全环境")
    print("2. 创建用户")
    print("3. 用户认证")
    print("4. 权限管理")
    print("5. 安全策略")
    print("6. 审计日志")
    print("7. 安全监控")
    print("8. 执行安全审计")
    print("9. SSL证书管理")
    print("10. 退出")
    
    while True:
        try:
            choice = input("\n请选择操作 (1-10): ").strip()
            
            if choice == '1':
                print("设置安全环境...")
                success = security_manager.setup_secure_environment()
                print(f"设置结果: {'成功' if success else '失败'}")
                
            elif choice == '2':
                username = input("请输入用户名: ").strip()
                password = input("请输入密码: ").strip()
                
                success = security_manager.auth_manager.create_user(username, password)
                print(f"创建用户结果: {'成功' if success else '失败'}")
                
            elif choice == '3':
                username = input("请输入用户名: ").strip()
                password = input("请输入密码: ").strip()
                
                auth_success, message = security_manager.auth_manager.authenticate_user(username, password)
                print(f"认证结果: {message}")
                
                if auth_success:
                    # 尝试创建连接
                    connection = security_manager.create_secure_connection(username, password)
                    if connection:
                        print("安全连接创建成功")
                        connection.close()
                    else:
                        print("安全连接创建失败")
                
            elif choice == '4':
                print("\n权限管理选项:")
                print("1. 授予权限")
                print("2. 撤销权限")
                print("3. 检查权限")
                print("4. 查看用户权限")
                
                perm_choice = input("请选择权限操作 (1-4): ").strip()
                
                if perm_choice == '1':
                    username = input("用户名: ").strip()
                    resource = input("资源: ").strip()
                    permission_str = input("权限 (read/write/configure): ").strip()
                    
                    permission_map = {
                        'read': PermissionType.READ,
                        'write': PermissionType.WRITE,
                        'configure': PermissionType.CONFIGURE
                    }
                    
                    if permission_str in permission_map:
                        success = security_manager.access_manager.grant_permission(
                            username, resource, permission_map[permission_str]
                        )
                        print(f"授权结果: {'成功' if success else '失败'}")
                    else:
                        print("无效权限类型")
                
                elif perm_choice == '3':
                    username = input("用户名: ").strip()
                    resource = input("资源: ").strip()
                    permission_str = input("权限: ").strip()
                    
                    permission_map = {
                        'read': PermissionType.READ,
                        'write': PermissionType.WRITE,
                        'configure': PermissionType.CONFIGURE
                    }
                    
                    if permission_str in permission_map:
                        has_permission = security_manager.access_manager.check_permission(
                            username, resource, permission_map[permission_str]
                        )
                        print(f"权限检查结果: {'有权限' if has_permission else '无权限'}")
                
                elif perm_choice == '4':
                    username = input("用户名: ").strip()
                    permissions = security_manager.access_manager.get_user_permissions(username)
                    print(f"用户权限: {permissions}")
                
            elif choice == '5':
                print("\n安全策略管理:")
                print("1. 创建策略")
                print("2. 应用策略")
                
                policy_choice = input("请选择策略操作 (1-2): ").strip()
                
                if policy_choice == '1':
                    policy_name = input("策略名称: ").strip()
                    min_length = int(input("最小密码长度 (默认8): ") or "8")
                    
                    policy_config = {
                        'min_length': min_length,
                        'require_uppercase': True,
                        'require_lowercase': True,
                        'require_digits': True,
                        'require_special_chars': True
                    }
                    
                    success = security_manager.policy_manager.create_policy(
                        policy_name, password_policy=policy_config
                    )
                    print(f"创建策略结果: {'成功' if success else '失败'}")
                
                elif policy_choice == '2':
                    policy_name = input("策略名称: ").strip()
                    success = security_manager.policy_manager.apply_policy(policy_name)
                    print(f"应用策略结果: {'成功' if success else '失败'}")
                
            elif choice == '6':
                print("\n审计日志查询:")
                print("1. 查看最近日志")
                print("2. 生成安全报告")
                
                audit_choice = input("请选择操作 (1-2): ").strip()
                
                if audit_choice == '1':
                    logs = security_manager.audit_logger.get_audit_logs()
                    print(f"最近 {len(logs)} 条日志:")
                    for log in logs[-10:]:  # 显示最近10条
                        print(f"- {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {log.user} - {log.action} - {log.result}")
                
                elif audit_choice == '2':
                    report = security_manager.audit_logger.generate_security_report()
                    print("安全报告:")
                    print(f"- 总事件数: {report['total_events']}")
                    print(f"- 成功登录: {report['successful_logins']}")
                    print(f"- 失败尝试: {report['failed_attempts']}")
                
            elif choice == '7':
                print("执行安全监控...")
                status = security_manager.monitor.get_security_status()
                print("安全状态:")
                for key, value in status.items():
                    print(f"- {key}: {value}")
                
                alerts = security_manager.monitor.detect_suspicious_activity()
                if alerts:
                    print(f"\n发现 {len(alerts)} 个安全警报:")
                    for alert in alerts:
                        print(f"- [{alert['severity']}] {alert['description']}")
                else:
                    print("未发现安全警报")
                
            elif choice == '8':
                print("执行安全审计...")
                audit_result = security_manager.security_audit()
                
                if 'error' in audit_result:
                    print(f"审计失败: {audit_result['error']}")
                else:
                    print("安全审计完成!")
                    print(f"- 总事件数: {audit_result['audit_report']['total_events']}")
                    print(f"- 安全警报: {len(audit_result['security_alerts'])}")
                    
                    recommendations = audit_result.get('recommendations', [])
                    if recommendations:
                        print("\n安全建议:")
                        for rec in recommendations:
                            print(f"- {rec}")
                
            elif choice == '9':
                print("\nSSL证书管理:")
                print("1. 生成证书")
                print("2. 验证证书")
                print("3. 查看证书信息")
                
                ssl_choice = input("请选择操作 (1-3): ").strip()
                
                if ssl_choice == '1':
                    common_name = input("通用名称 (CN): ").strip()
                    validity_days = int(input("有效期天数 (默认365): ") or "365")
                    
                    success = security_manager.ssl_manager.generate_certificate(common_name, validity_days)
                    print(f"证书生成结果: {'成功' if success else '失败'}")
                
                elif ssl_choice == '2':
                    cert_data = input("证书数据: ").strip()
                    is_valid, message = security_manager.ssl_manager.validate_certificate(cert_data)
                    print(f"验证结果: {message}")
                
                elif ssl_choice == '3':
                    common_name = input("通用名称: ").strip()
                    cert_info = security_manager.ssl_manager.get_certificate_info(common_name)
                    if cert_info:
                        print("证书信息:")
                        for key, value in cert_info.items():
                            print(f"- {key}: {value}")
                    else:
                        print("证书不存在")
                
            elif choice == '10':
                print("退出系统")
                break
                
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n用户中断")
            break
        except Exception as e:
            print(f"操作出错: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())