"""
第7章：安全与认证 - 端到端安全消息系统
演示完整的安全消息处理流程，包括消息加密、身份验证、权限检查、安全传输等
"""

import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import secrets
import uuid


class MessageSecurityLevel(Enum):
    """消息安全级别"""
    PUBLIC = "public"          # 公开消息
    INTERNAL = "internal"      # 内部消息
    CONFIDENTIAL = "confidential"  # 机密消息
    SECRET = "secret"          # 绝密消息


class MessagePriority(Enum):
    """消息优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class SecureMessage:
    """安全消息数据类"""
    message_id: str
    sender_id: str
    recipient_id: str
    content: str
    security_level: MessageSecurityLevel
    priority: MessagePriority
    timestamp: datetime
    encrypted_content: str = ""
    signature: str = ""
    encryption_key_id: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self):
        """转换为字典格式"""
        data = asdict(self)
        data['security_level'] = self.security_level.value
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class CryptographicManager:
    """密码学管理器"""
    
    def __init__(self):
        self.master_key = self._generate_master_key()
        self.key_derivation_rounds = 100000
        
    def _generate_master_key(self) -> bytes:
        """生成主密钥"""
        return secrets.token_bytes(32)  # 256位密钥
    
    def derive_key(self, key_id: str, purpose: str) -> bytes:
        """从主密钥派生子密钥"""
        # 使用HMAC派生密钥
        derivation_input = f"{key_id}:{purpose}".encode('utf-8')
        derived_key = hmac.new(
            self.master_key,
            derivation_input,
            hashlib.sha256
        ).digest()
        return derived_key
    
    def encrypt_content(self, content: str, key_id: str, security_level: MessageSecurityLevel) -> tuple:
        """加密消息内容"""
        if security_level == MessageSecurityLevel.PUBLIC:
            # 公开消息不需要加密，但仍然签名
            encryption_key = self.derive_key(key_id, "signing")
            signature = self._generate_signature(content.encode('utf-8'), encryption_key)
            return content, signature, key_id
        
        # 其他级别需要加密
        encryption_key = self.derive_key(key_id, "encryption")
        encrypted_content = self._simple_encrypt(content, encryption_key)
        signature = self._generate_signature(encrypted_content, encryption_key)
        return encrypted_content, signature, key_id
    
    def decrypt_content(self, encrypted_content: str, key_id: str, signature: str, 
                       security_level: MessageSecurityLevel) -> tuple:
        """解密消息内容"""
        if security_level == MessageSecurityLevel.PUBLIC:
            # 公开消息不需要解密
            encryption_key = self.derive_key(key_id, "signing")
            if self._verify_signature(encrypted_content.encode('utf-8'), signature, encryption_key):
                return encrypted_content, True
            else:
                return None, False
        
        # 解密其他级别的消息
        encryption_key = self.derive_key(key_id, "encryption")
        if self._verify_signature(encrypted_content.encode('utf-8'), signature, encryption_key):
            decrypted_content = self._simple_decrypt(encrypted_content, encryption_key)
            return decrypted_content, True
        else:
            return None, False
    
    def _simple_encrypt(self, content: str, key: bytes) -> str:
        """简单加密实现（实际生产环境应使用专业的加密库）"""
        # 这里使用XOR加密作为演示，实际应使用AES等标准加密算法
        content_bytes = content.encode('utf-8')
        key_bytes = key * (len(content_bytes) // len(key) + 1)
        encrypted_bytes = bytes(a ^ b for a, b in zip(content_bytes, key_bytes))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def _simple_decrypt(self, encrypted_content: str, key: bytes) -> str:
        """简单解密实现"""
        encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
        key_bytes = key * (len(encrypted_bytes) // len(key) + 1)
        decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, key_bytes))
        return decrypted_bytes.decode('utf-8')
    
    def _generate_signature(self, content: bytes, key: bytes) -> str:
        """生成消息签名"""
        signature = hmac.new(key, content, hashlib.sha256).hexdigest()
        return signature
    
    def _verify_signature(self, content: bytes, signature: str, key: bytes) -> bool:
        """验证消息签名"""
        expected_signature = self._generate_signature(content, key)
        return hmac.compare_digest(expected_signature, signature)


class AccessControlManager:
    """访问控制管理器"""
    
    def __init__(self):
        # 用户权限映射
        self.user_permissions = {
            'admin': {
                'queues': ['*'],  # 全部队列
                'operations': ['read', 'write', 'configure', 'delete'],
                'security_levels': ['public', 'internal', 'confidential', 'secret']
            },
            'user_manager': {
                'queues': ['user_management_*', 'notifications'],
                'operations': ['read', 'write'],
                'security_levels': ['public', 'internal', 'confidential']
            },
            'financial_analyst': {
                'queues': ['financial_*', 'reports_*'],
                'operations': ['read', 'write'],
                'security_levels': ['public', 'internal', 'confidential']
            },
            'regular_user': {
                'queues': ['general_*', 'notifications'],
                'operations': ['read', 'write'],
                'security_levels': ['public', 'internal']
            }
        }
        
        # 消息级别权限矩阵
        self.security_level_requirements = {
            MessageSecurityLevel.PUBLIC: ['read'],
            MessageSecurityLevel.INTERNAL: ['read', 'internal_access'],
            MessageSecurityLevel.CONFIDENTIAL: ['read', 'confidential_access'],
            MessageSecurityLevel.SECRET: ['read', 'secret_access', 'approval_required']
        }
    
    def check_user_permission(self, user_id: str, operation: str, 
                            queue_name: str, security_level: MessageSecurityLevel) -> tuple:
        """检查用户权限"""
        user_perms = self.user_permissions.get(user_id, {})
        
        # 检查用户是否存在
        if not user_perms:
            return False, f"用户 {user_id} 未找到"
        
        # 检查操作权限
        if operation not in user_perms.get('operations', []):
            return False, f"用户 {user_id} 没有 {operation} 权限"
        
        # 检查队列权限
        queue_permissions = user_perms.get('queues', [])
        queue_access = False
        for allowed_queue_pattern in queue_permissions:
            if allowed_queue_pattern == '*' or self._match_queue_pattern(queue_name, allowed_queue_pattern):
                queue_access = True
                break
        
        if not queue_access:
            return False, f"用户 {user_id} 没有访问队列 {queue_name} 的权限"
        
        # 检查消息安全级别权限
        user_security_levels = user_perms.get('security_levels', [])
        if security_level.value not in user_security_levels:
            return False, f"用户 {user_id} 没有访问 {security_level.value} 级别消息的权限"
        
        # 检查特殊权限要求
        required_perms = self.security_level_requirements.get(security_level, [])
        for req_perm in required_perms:
            if req_perm not in user_perms.get('operations', []):
                return False, f"用户 {user_id} 缺少访问 {security_level.value} 消息的 {req_perm} 权限"
        
        return True, "权限检查通过"
    
    def _match_queue_pattern(self, queue_name: str, pattern: str) -> bool:
        """检查队列名是否匹配模式"""
        if pattern.endswith('*'):
            return queue_name.startswith(pattern[:-1])
        return queue_name == pattern
    
    def get_user_permissions(self, user_id: str) -> Dict:
        """获取用户权限详情"""
        return self.user_permissions.get(user_id, {})
    
    def add_user_permissions(self, user_id: str, permissions: Dict):
        """添加用户权限"""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = {
                'queues': [],
                'operations': [],
                'security_levels': []
            }
        
        for key, value in permissions.items():
            if key in self.user_permissions[user_id]:
                self.user_permissions[user_id][key].extend(value)
                # 去重
                self.user_permissions[user_id][key] = list(set(self.user_permissions[user_id][key]))


class SecurityMessageHandler:
    """安全消息处理器"""
    
    def __init__(self):
        self.crypto_manager = CryptographicManager()
        self.access_control = AccessControlManager()
        self.message_store: Dict[str, SecureMessage] = {}
        self.audit_log: List[Dict] = []
    
    def create_secure_message(self, sender_id: str, recipient_id: str, content: str,
                            security_level: MessageSecurityLevel, priority: MessagePriority,
                            queue_name: str) -> tuple:
        """创建安全消息"""
        message_id = str(uuid.uuid4())
        
        # 生成消息密钥ID
        key_id = f"{sender_id}:{recipient_id}:{message_id}"
        
        # 加密消息内容
        encrypted_content, signature, final_key_id = self.crypto_manager.encrypt_content(
            content, key_id, security_level
        )
        
        # 创建安全消息
        message = SecureMessage(
            message_id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,  # 在实际应用中，这应该只在发送方保留
            security_level=security_level,
            priority=priority,
            timestamp=datetime.now(),
            encrypted_content=encrypted_content,
            signature=signature,
            encryption_key_id=final_key_id,
            metadata={
                'queue_name': queue_name,
                'key_derivation_info': {
                    'sender': sender_id,
                    'recipient': recipient_id,
                    'message_id': message_id
                }
            }
        )
        
        # 存储消息
        self.message_store[message_id] = message
        
        # 记录审计日志
        self._log_audit_event('message_created', {
            'message_id': message_id,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'security_level': security_level.value,
            'queue_name': queue_name
        })
        
        return message_id, "消息创建成功"
    
    def process_secure_message(self, message_id: str, recipient_id: str, 
                             queue_name: str) -> tuple:
        """处理安全消息"""
        message = self.message_store.get(message_id)
        
        if not message:
            return None, "消息未找到"
        
        # 检查权限
        can_access, reason = self.access_control.check_user_permission(
            recipient_id, 'read', queue_name, message.security_level
        )
        
        if not can_access:
            # 记录权限拒绝审计
            self._log_audit_event('access_denied', {
                'user_id': recipient_id,
                'message_id': message_id,
                'reason': reason,
                'security_level': message.security_level.value
            })
            return None, reason
        
        # 解密消息内容
        decrypted_content, decrypt_success = self.crypto_manager.decrypt_content(
            message.encrypted_content,
            message.encryption_key_id,
            message.signature,
            message.security_level
        )
        
        if not decrypt_success:
            self._log_audit_event('decryption_failed', {
                'user_id': recipient_id,
                'message_id': message_id,
                'reason': '签名验证失败'
            })
            return None, "消息签名验证失败，内容可能已被篡改"
        
        # 记录成功访问审计
        self._log_audit_event('message_accessed', {
            'user_id': recipient_id,
            'message_id': message_id,
            'security_level': message.security_level.value,
            'queue_name': queue_name
        })
        
        return decrypted_content, "消息处理成功"
    
    def broadcast_secure_message(self, sender_id: str, recipient_ids: List[str],
                               content: str, security_level: MessageSecurityLevel,
                               queue_prefix: str) -> Dict[str, tuple]:
        """广播安全消息"""
        results = {}
        
        for recipient_id in recipient_ids:
            queue_name = f"{queue_prefix}_{recipient_id}"
            message_id, status = self.create_secure_message(
                sender_id, recipient_id, content, security_level,
                MessagePriority.NORMAL, queue_name
            )
            results[recipient_id] = (message_id, status)
        
        return results
    
    def validate_message_integrity(self, message_id: str) -> tuple:
        """验证消息完整性"""
        message = self.message_store.get(message_id)
        
        if not message:
            return False, "消息未找到"
        
        # 重新验证签名
        key_id = message.encryption_key_id
        security_level = message.security_level
        
        # 对于非公开消息，需要解密来验证完整性
        if security_level != MessageSecurityLevel.PUBLIC:
            decrypted_content, decrypt_success = self.crypto_manager.decrypt_content(
                message.encrypted_content,
                key_id,
                message.signature,
                security_level
            )
            
            if not decrypt_success:
                return False, "消息完整性验证失败：解密失败"
            
            # 重新加密并比较
            _, new_signature, _ = self.crypto_manager.encrypt_content(
                decrypted_content, key_id, security_level
            )
            
            is_valid = hmac.compare_digest(message.signature, new_signature)
            return is_valid, "消息完整性验证通过" if is_valid else "消息完整性验证失败：签名不匹配"
        
        else:
            # 公开消息只需要验证签名
            encryption_key = self.crypto_manager.derive_key(key_id, "signing")
            is_valid = self.crypto_manager._verify_signature(
                message.content.encode('utf-8'), message.signature, encryption_key
            )
            return is_valid, "消息完整性验证通过" if is_valid else "消息完整性验证失败：签名不匹配"
    
    def purge_expired_messages(self, max_age_hours: int = 24) -> int:
        """清理过期消息"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        expired_messages = []
        for message_id, message in self.message_store.items():
            if message.timestamp < cutoff_time:
                expired_messages.append(message_id)
        
        # 删除过期消息
        for message_id in expired_messages:
            del self.message_store[message_id]
            
            # 记录清理审计
            self._log_audit_event('message_purged', {
                'message_id': message_id,
                'reason': 'expired',
                'age_hours': max_age_hours
            })
        
        return len(expired_messages)
    
    def _log_audit_event(self, event_type: str, details: Dict):
        """记录审计事件"""
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.audit_log.append(audit_record)
        
        # 保持审计日志大小在合理范围内
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-500:]  # 保留最近500条记录
    
    def get_security_report(self) -> Dict:
        """获取安全报告"""
        # 统计各种类型的事件
        event_counts = {}
        user_activity = {}
        
        for record in self.audit_log:
            event_type = record['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # 统计用户活动
            user_id = record['details'].get('user_id')
            if user_id:
                user_activity[user_id] = user_activity.get(user_id, 0) + 1
        
        # 统计消息安全级别分布
        security_level_stats = {}
        for message in self.message_store.values():
            level = message.security_level.value
            security_level_stats[level] = security_level_stats.get(level, 0) + 1
        
        return {
            'total_messages': len(self.message_store),
            'total_audit_events': len(self.audit_log),
            'event_counts': event_counts,
            'user_activity': user_activity,
            'security_level_distribution': security_level_stats,
            'report_generated': datetime.now().isoformat()
        }


class SecureMessagingDemo:
    """安全消息系统演示"""
    
    def __init__(self):
        self.handler = SecurityMessageHandler()
    
    def demonstrate_basic_secure_messaging(self):
        """演示基础安全消息"""
        print("🔐 基础安全消息演示")
        print("-" * 40)
        
        # 创建不同安全级别的消息
        scenarios = [
            {
                'sender': 'admin',
                'recipient': 'user1',
                'content': '这是一个公开信息，所有用户都可以查看',
                'level': MessageSecurityLevel.PUBLIC,
                'queue': 'general_notifications'
            },
            {
                'sender': 'admin',
                'recipient': 'financial_analyst',
                'content': '本月财务报表：收入增长15%，需要详细分析',
                'level': MessageSecurityLevel.CONFIDENTIAL,
                'queue': 'financial_reports'
            },
            {
                'sender': 'security_admin',
                'recipient': 'admin',
                'content': '发现潜在安全威胁，建议立即采取行动',
                'level': MessageSecurityLevel.SECRET,
                'queue': 'security_alerts'
            }
        ]
        
        message_ids = {}
        
        for scenario in scenarios:
            message_id, status = self.handler.create_secure_message(
                scenario['sender'],
                scenario['recipient'],
                scenario['content'],
                scenario['level'],
                MessagePriority.NORMAL,
                scenario['queue']
            )
            
            message_ids[scenario['level'].value] = message_id
            print(f"✅ {scenario['level'].value.upper()} 消息创建: {message_id[:8]}... - {status}")
        
        # 演示消息访问
        print("\n📖 消息访问演示:")
        access_tests = [
            {
                'user': 'user1',
                'message_level': 'public',
                'queue': 'general_notifications'
            },
            {
                'user': 'regular_user',
                'message_level': 'confidential',
                'queue': 'financial_reports'
            },
            {
                'user': 'financial_analyst',
                'message_level': 'confidential',
                'queue': 'financial_reports'
            }
        ]
        
        for test in access_tests:
            message_id = message_ids[test['message_level']]
            content, status = self.handler.process_secure_message(
                message_id, test['user'], test['queue']
            )
            
            result = "✅" if content else "❌"
            print(f"   {result} 用户 {test['user']} 访问 {test['message_level']} 消息: {status}")
            if content:
                print(f"      内容: {content[:50]}...")
    
    def demonstrate_message_integrity(self):
        """演示消息完整性检查"""
        print("\n🔍 消息完整性检查演示")
        print("-" * 40)
        
        # 创建一个机密消息
        message_id, _ = self.handler.create_secure_message(
            'sender', 'recipient', '机密测试消息',
            MessageSecurityLevel.CONFIDENTIAL, MessagePriority.NORMAL, 'test_queue'
        )
        
        # 验证完整性
        is_valid, reason = self.handler.validate_message_integrity(message_id)
        print(f"📊 原始消息完整性: {'✅' if is_valid else '❌'} - {reason}")
        
        # 模拟消息被篡改（在实际应用中应该修改存储的签名）
        message = self.handler.message_store[message_id]
        original_signature = message.signature
        message.signature = "tampered_signature"
        
        # 重新验证
        is_valid, reason = self.handler.validate_message_integrity(message_id)
        print(f"📊 篡改后完整性: {'✅' if is_valid else '❌'} - {reason}")
        
        # 恢复原始签名
        message.signature = original_signature
    
    def demonstrate_broadcast_messaging(self):
        """演示广播消息"""
        print("\n📡 广播消息演示")
        print("-" * 40)
        
        # 广播给多个收件人
        recipient_list = ['user1', 'user2', 'financial_analyst']
        results = self.handler.broadcast_secure_message(
            'admin', recipient_list, '系统维护通知：今晚22:00-24:00进行维护',
            MessageSecurityLevel.INTERNAL, 'maintenance'
        )
        
        print("📊 广播结果:")
        for recipient, (message_id, status) in results.items():
            print(f"   {recipient}: {message_id[:8]}... - {status}")
        
        # 模拟不同用户访问广播消息
        print("\n📖 广播消息访问测试:")
        for recipient in recipient_list:
            if results[recipient][0]:  # 如果消息创建成功
                content, status = self.handler.process_secure_message(
                    results[recipient][0], recipient, f'maintenance_{recipient}'
                )
                print(f"   {recipient}: {'✅' if content else '❌'} - {status}")
    
    def demonstrate_access_control(self):
        """演示访问控制"""
        print("\n🔐 访问控制演示")
        print("-" * 40)
        
        # 显示当前用户权限
        print("👥 用户权限配置:")
        users = ['admin', 'user_manager', 'financial_analyst', 'regular_user']
        
        for user in users:
            perms = self.handler.access_control.get_user_permissions(user)
            print(f"   {user}:")
            print(f"      队列: {perms.get('queues', [])}")
            print(f"      操作: {perms.get('operations', [])}")
            print(f"      安全级别: {perms.get('security_levels', [])}")
    
    def demonstrate_security_monitoring(self):
        """演示安全监控"""
        print("\n📊 安全监控演示")
        print("-" * 40)
        
        # 清理过期消息
        purged_count = self.handler.purge_expired_messages(max_age_hours=0)  # 清理所有消息
        print(f"🧹 清理了 {purged_count} 条过期消息")
        
        # 生成安全报告
        report = self.handler.get_security_report()
        print(f"\n📈 安全报告:")
        print(f"   总消息数: {report['total_messages']}")
        print(f"   总审计事件: {report['total_audit_events']}")
        print(f"   事件统计: {report['event_counts']}")
        print(f"   用户活动: {report['user_activity']}")
        print(f"   安全级别分布: {report['security_level_distribution']}")
    
    def run_secure_messaging_demo(self):
        """运行安全消息系统演示"""
        print("🔐 RabbitMQ 端到端安全消息系统演示")
        print("=" * 60)
        
        try:
            # 基础安全消息演示
            self.demonstrate_basic_secure_messaging()
            
            # 消息完整性检查
            self.demonstrate_message_integrity()
            
            # 广播消息演示
            self.demonstrate_broadcast_messaging()
            
            # 访问控制演示
            self.demonstrate_access_control()
            
            # 安全监控演示
            self.demonstrate_security_monitoring()
            
        except KeyboardInterrupt:
            print("\n⏹️ 演示被用户中断")
        except Exception as e:
            print(f"❌ 演示运行失败: {e}")
        
        print(f"\n🏁 端到端安全消息系统演示完成")


if __name__ == "__main__":
    # 运行安全消息系统演示
    demo = SecureMessagingDemo()
    demo.run_secure_messaging_demo()