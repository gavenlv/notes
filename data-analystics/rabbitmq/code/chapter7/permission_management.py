"""
第7章：安全与认证 - 权限管理演示
演示RBAC权限控制、动态权限管理、细粒度权限配置
"""

import pika
import json
import time
from typing import Dict, List, Set
import re
from datetime import datetime


class UserPermission:
    """用户权限类"""
    
    def __init__(self, username: str):
        self.username = username
        self.roles: Set[str] = set()
        self.permissions: Set[str] = set()
        self.resource_access: Dict[str, List[str]] = {}  # {resource: [permissions]}
        self.created_at = datetime.now()
        self.last_login = None
    
    def add_role(self, role: str):
        """添加角色"""
        self.roles.add(role)
    
    def remove_role(self, role: str):
        """移除角色"""
        self.roles.discard(role)
    
    def grant_permission(self, permission: str, resource: str = None):
        """授予权限"""
        self.permissions.add(permission)
        if resource:
            if resource not in self.resource_access:
                self.resource_access[resource] = []
            if permission not in self.resource_access[resource]:
                self.resource_access[resource].append(permission)
    
    def revoke_permission(self, permission: str, resource: str = None):
        """撤销权限"""
        self.permissions.discard(permission)
        if resource and resource in self.resource_access:
            if permission in self.resource_access[resource]:
                self.resource_access[resource].remove(permission)
            if not self.resource_access[resource]:
                del self.resource_access[resource]
    
    def has_permission(self, permission: str, resource: str = None) -> bool:
        """检查权限"""
        if resource:
            return permission in self.resource_access.get(resource, [])
        return permission in self.permissions
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.now()


class RBACManager:
    """基于角色的访问控制管理器"""
    
    def __init__(self):
        self.roles = {
            'admin': {
                'description': '系统管理员',
                'permissions': ['configure', 'read', 'write'],
                'resources': ['.*']  # 所有资源
            },
            'publisher': {
                'description': '消息发布者',
                'permissions': ['write'],
                'resources': ['events.*', 'notifications.*', 'logs.*']
            },
            'consumer': {
                'description': '消息消费者',
                'permissions': ['read'],
                'resources': ['events.*', 'notifications.*', 'logs.*', 'status.*']
            },
            'viewer': {
                'description': '只读用户',
                'permissions': ['read'],
                'resources': ['status.*', 'monitoring.*']
            },
            'api_client': {
                'description': 'API客户端',
                'permissions': ['read', 'write'],
                'resources': ['api.*', 'webhook.*']
            }
        }
        
        self.user_permissions: Dict[str, UserPermission] = {}
        self.default_user_role = 'viewer'
    
    def create_user(self, username: str, role: str = None) -> bool:
        """创建用户"""
        try:
            if username in self.user_permissions:
                print(f"⚠️ 用户 {username} 已存在")
                return False
            
            user_perm = UserPermission(username)
            
            if role and role in self.roles:
                user_perm.add_role(role)
                role_info = self.roles[role]
                
                # 授予角色权限
                for permission in role_info['permissions']:
                    user_perm.grant_permission(permission)
                    # 为所有允许的资源授予权限
                    for resource_pattern in role_info['resources']:
                        user_perm.grant_permission(permission, resource_pattern)
            else:
                # 使用默认角色
                user_perm.add_role(self.default_user_role)
                user_perm.grant_permission('read')
            
            self.user_permissions[username] = user_perm
            print(f"✅ 创建用户 {username} 成功，角色: {role or self.default_user_role}")
            return True
            
        except Exception as e:
            print(f"❌ 创建用户失败: {e}")
            return False
    
    def assign_role(self, username: str, role: str) -> bool:
        """分配角色"""
        try:
            if role not in self.roles:
                print(f"❌ 角色 {role} 不存在")
                return False
            
            if username not in self.user_permissions:
                print(f"❌ 用户 {username} 不存在")
                return False
            
            user_perm = self.user_permissions[username]
            
            # 添加角色
            user_perm.add_role(role)
            
            # 授予权限
            role_info = self.roles[role]
            for permission in role_info['permissions']:
                user_perm.grant_permission(permission)
                for resource_pattern in role_info['resources']:
                    user_perm.grant_permission(permission, resource_pattern)
            
            print(f"✅ 为用户 {username} 分配角色 {role}")
            return True
            
        except Exception as e:
            print(f"❌ 分配角色失败: {e}")
            return False
    
    def revoke_role(self, username: str, role: str) -> bool:
        """撤销角色"""
        try:
            if role not in self.roles:
                print(f"❌ 角色 {role} 不存在")
                return False
            
            if username not in self.user_permissions:
                print(f"❌ 用户 {username} 不存在")
                return False
            
            user_perm = self.user_permissions[username]
            
            if role not in user_perm.roles:
                print(f"❌ 用户 {username} 没有角色 {role}")
                return False
            
            # 移除角色
            user_perm.remove_role(role)
            
            # 重新计算权限（移除角色相关的权限）
            remaining_roles = user_perm.roles
            user_perm.permissions.clear()
            user_perm.resource_access.clear()
            
            # 重新授予剩余角色的权限
            for remaining_role in remaining_roles:
                if remaining_role in self.roles:
                    role_info = self.roles[remaining_role]
                    for permission in role_info['permissions']:
                        user_perm.grant_permission(permission)
                        for resource_pattern in role_info['resources']:
                            user_perm.grant_permission(permission, resource_pattern)
            
            print(f"✅ 从用户 {username} 撤销角色 {role}")
            return True
            
        except Exception as e:
            print(f"❌ 撤销角色失败: {e}")
            return False
    
    def check_permission(self, username: str, operation: str, resource: str) -> bool:
        """检查权限"""
        try:
            if username not in self.user_permissions:
                return False
            
            user_perm = self.user_permissions[username]
            return user_perm.has_permission(operation, resource)
            
        except Exception as e:
            print(f"❌ 权限检查失败: {e}")
            return False
    
    def get_user_info(self, username: str) -> Dict:
        """获取用户信息"""
        if username not in self.user_permissions:
            return None
        
        user_perm = self.user_permissions[username]
        return {
            'username': user_perm.username,
            'roles': list(user_perm.roles),
            'permissions': list(user_perm.permissions),
            'resource_access': user_perm.resource_access,
            'created_at': user_perm.created_at.isoformat(),
            'last_login': user_perm.last_login.isoformat() if user_perm.last_login else None
        }
    
    def list_users(self) -> List[str]:
        """列出所有用户"""
        return list(self.user_permissions.keys())
    
    def list_roles(self) -> Dict[str, Dict]:
        """列出所有角色"""
        return self.roles.copy()


class QueuePermissionManager:
    """队列权限管理器"""
    
    def __init__(self, rbac_manager: RBACManager):
        self.rbac_manager = rbac_manager
        self.queue_permissions: Dict[str, Dict[str, List[str]]] = {}  # {queue: {operation: [users]}}
    
    def grant_queue_permission(self, queue: str, operation: str, username: str) -> bool:
        """授予队列权限"""
        try:
            if queue not in self.queue_permissions:
                self.queue_permissions[queue] = {}
            
            if operation not in self.queue_permissions[queue]:
                self.queue_permissions[queue][operation] = []
            
            if username not in self.queue_permissions[queue][operation]:
                self.queue_permissions[queue][operation].append(username)
                print(f"✅ 为用户 {username} 授予队列 {queue} 的 {operation} 权限")
            
            return True
            
        except Exception as e:
            print(f"❌ 授予队列权限失败: {e}")
            return False
    
    def revoke_queue_permission(self, queue: str, operation: str, username: str) -> bool:
        """撤销队列权限"""
        try:
            if queue in self.queue_permissions and operation in self.queue_permissions[queue]:
                if username in self.queue_permissions[queue][operation]:
                    self.queue_permissions[queue][operation].remove(username)
                    print(f"✅ 从用户 {username} 撤销队列 {queue} 的 {operation} 权限")
                    
                    # 如果没有用户了，删除这个操作的权限记录
                    if not self.queue_permissions[queue][operation]:
                        del self.queue_permissions[queue][operation]
                        if not self.queue_permissions[queue]:
                            del self.queue_permissions[queue]
            
            return True
            
        except Exception as e:
            print(f"❌ 撤销队列权限失败: {e}")
            return False
    
    def check_queue_permission(self, username: str, operation: str, queue: str) -> bool:
        """检查队列权限"""
        try:
            # 首先检查RBAC权限
            if not self.rbac_manager.check_permission(username, operation, queue):
                return False
            
            # 然后检查队列特定的权限
            if queue in self.queue_permissions:
                if operation in self.queue_permissions[queue]:
                    return username in self.queue_permissions[queue][operation]
            
            return True  # RBAC权限允许
            
        except Exception as e:
            print(f"❌ 队列权限检查失败: {e}")
            return False
    
    def get_queue_permissions(self, queue: str) -> Dict:
        """获取队列权限"""
        return self.queue_permissions.get(queue, {})


class PermissionAwareConnection:
    """支持权限检查的连接"""
    
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
    
    def connect(self, rbac_manager: RBACManager) -> bool:
        """连接（带权限验证）"""
        try:
            # 检查用户是否有连接权限
            if not rbac_manager.check_permission(self.username, 'read', 'connection'):
                print(f"❌ 用户 {self.username} 没有连接权限")
                return False
            
            credentials = pika.PlainCredentials(self.username, self.password)
            connection_parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            
            self.connection = pika.BlockingConnection(connection_parameters)
            self.channel = self.connection.channel()
            
            # 更新用户最后登录时间
            if self.username in rbac_manager.user_permissions:
                rbac_manager.user_permissions[self.username].update_last_login()
            
            print(f"✅ 用户 {self.username} 连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def create_queue(self, queue: str, queue_manager: QueuePermissionManager) -> bool:
        """创建队列（带权限检查）"""
        try:
            # 检查权限
            if not queue_manager.check_queue_permission(self.username, 'write', queue):
                print(f"❌ 用户 {self.username} 没有创建队列 {queue} 的权限")
                return False
            
            self.channel.queue_declare(queue=queue, durable=True)
            print(f"✅ 用户 {self.username} 创建队列 {queue} 成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建队列失败: {e}")
            return False
    
    def publish_message(self, queue: str, message: Dict, queue_manager: QueuePermissionManager) -> bool:
        """发布消息（带权限检查）"""
        try:
            # 检查权限
            if not queue_manager.check_queue_permission(self.username, 'write', queue):
                print(f"❌ 用户 {self.username} 没有向队列 {queue} 发布消息的权限")
                return False
            
            message['publisher'] = self.username
            message['timestamp'] = datetime.now().isoformat()
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            print(f"✅ 用户 {self.username} 向队列 {queue} 发布消息成功")
            return True
            
        except Exception as e:
            print(f"❌ 发布消息失败: {e}")
            return False
    
    def consume_message(self, queue: str, queue_manager: QueuePermissionManager) -> bool:
        """消费消息（带权限检查）"""
        try:
            # 检查权限
            if not queue_manager.check_queue_permission(self.username, 'read', queue):
                print(f"❌ 用户 {self.username} 没有从队列 {queue} 消费消息的权限")
                return False
            
            def callback(ch, method, properties, body):
                try:
                    message_data = json.loads(body.decode('utf-8'))
                    consumer = message_data.get('publisher', 'unknown')
                    print(f"📥 用户 {self.username} 从队列 {queue} 消费消息 (发布者: {consumer})")
                    
                    # 确认消息
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    print(f"❌ 消息处理失败: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=callback,
                auto_ack=False
            )
            
            print(f"✅ 用户 {self.username} 开始从队列 {queue} 消费消息")
            self.channel.start_consuming()
            return True
            
        except Exception as e:
            print(f"❌ 消费消息失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(f"🔌 用户 {self.username} 断开连接")


class PermissionDemo:
    """权限管理演示"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.rbac_manager = RBACManager()
        self.queue_manager = QueuePermissionManager(self.rbac_manager)
    
    def setup_demo_users(self):
        """设置演示用户"""
        print("👥 设置演示用户")
        print("-" * 40)
        
        # 创建不同角色的用户
        users = [
            ('admin_user', 'admin'),
            ('publisher_user', 'publisher'),
            ('consumer_user', 'consumer'),
            ('viewer_user', 'viewer'),
            ('api_client', 'api_client')
        ]
        
        for username, role in users:
            self.rbac_manager.create_user(username, role)
    
    def setup_demo_permissions(self):
        """设置演示权限"""
        print("\n🔐 设置演示权限")
        print("-" * 40)
        
        # 为特定队列设置额外权限
        queue_permissions = [
            ('secure_queue', 'write', 'consumer_user'),  # 允许消费者写入安全队列
            ('admin_queue', 'read', 'publisher_user')    # 允许发布者读取管理员队列
        ]
        
        for queue, operation, username in queue_permissions:
            self.queue_manager.grant_queue_permission(queue, operation, username)
    
    def demonstrate_permission_checking(self):
        """演示权限检查"""
        print("\n🔍 权限检查演示")
        print("-" * 40)
        
        test_cases = [
            ('admin_user', 'write', 'events.test'),
            ('publisher_user', 'write', 'notifications.alert'),
            ('consumer_user', 'read', 'events.test'),
            ('viewer_user', 'write', 'events.test'),  # 应该失败
            ('consumer_user', 'read', 'admin_queue'),  # 应该成功（额外权限）
            ('consumer_user', 'write', 'admin_queue')  # 应该失败（没有写权限）
        ]
        
        for username, operation, resource in test_cases:
            has_permission = self.rbac_manager.check_permission(username, operation, resource)
            result = "✅ 允许" if has_permission else "❌ 拒绝"
            print(f"{result} - {username} {operation} {resource}")
    
    def demonstrate_secure_messaging(self):
        """演示安全消息传递"""
        print("\n📨 安全消息传递演示")
        print("-" * 40)
        
        try:
            # 模拟不同用户的消息传递
            
            # 管理员用户 - 应该可以访问所有资源
            admin_conn = PermissionAwareConnection('localhost', 5672, 'admin_user', 'password')
            if admin_conn.connect(self.rbac_manager):
                admin_conn.create_queue('admin_test_queue', self.queue_manager)
                admin_conn.publish_message('admin_test_queue', {
                    'type': 'admin_message',
                    'content': '管理员消息'
                }, self.queue_manager)
                admin_conn.close()
            
            # 发布者用户 - 应该可以发布到事件队列
            publisher_conn = PermissionAwareConnection('localhost', 5672, 'publisher_user', 'password')
            if publisher_conn.connect(self.rbac_manager):
                # 应该成功
                publisher_conn.publish_message('events.test', {
                    'type': 'event',
                    'content': '发布者消息'
                }, self.queue_manager)
                
                # 应该失败（没有权限）
                publisher_conn.publish_message('admin_test_queue', {
                    'type': 'unauthorized',
                    'content': '未经授权的消息'
                }, self.queue_manager)
                publisher_conn.close()
            
            # 消费者用户 - 应该可以读取事件队列
            consumer_conn = PermissionAwareConnection('localhost', 5672, 'consumer_user', 'password')
            if consumer_conn.connect(self.rbac_manager):
                consumer_conn.consume_message('admin_test_queue', self.queue_manager)
                consumer_conn.close()
                
        except Exception as e:
            print(f"❌ 安全消息传递演示失败: {e}")
    
    def demonstrate_user_management(self):
        """演示用户管理"""
        print("\n👨‍💼 用户管理演示")
        print("-" * 40)
        
        # 创建新用户
        self.rbac_manager.create_user('new_user')
        print("📋 用户列表:", self.rbac_manager.list_users())
        
        # 分配角色
        self.rbac_manager.assign_role('new_user', 'publisher')
        user_info = self.rbac_manager.get_user_info('new_user')
        print(f"📄 新用户信息: {user_info}")
        
        # 撤销角色
        self.rbac_manager.revoke_role('new_user', 'publisher')
        user_info = self.rbac_manager.get_user_info('new_user')
        print(f"📄 撤销角色后: {user_info}")
    
    def demonstrate_dynamic_permissions(self):
        """演示动态权限"""
        print("\n⚡ 动态权限演示")
        print("-" * 40)
        
        # 演示实时权限变更
        username = 'dynamic_user'
        
        # 创建用户
        self.rbac_manager.create_user(username)
        
        # 初始权限检查
        print(f"初始权限检查 - {username}:")
        has_write = self.rbac_manager.check_permission(username, 'write', 'events.test')
        print(f"  写入权限: {'是' if has_write else '否'}")
        
        # 分配发布者角色
        print(f"\n分配发布者角色...")
        self.rbac_manager.assign_role(username, 'publisher')
        
        # 重新检查权限
        has_write = self.rbac_manager.check_permission(username, 'write', 'events.test')
        print(f"  分配角色后写入权限: {'是' if has_write else '否'}")
        
        # 撤销角色
        print(f"\n撤销发布者角色...")
        self.rbac_manager.revoke_role(username, 'publisher')
        
        # 再次检查权限
        has_write = self.rbac_manager.check_permission(username, 'write', 'events.test')
        print(f"  撤销角色后写入权限: {'是' if has_write else '否'}")
    
    def run_permission_demo(self):
        """运行权限管理演示"""
        print("🔐 RabbitMQ 权限管理演示")
        print("=" * 60)
        
        try:
            # 设置演示环境
            self.setup_demo_users()
            self.setup_demo_permissions()
            
            # 运行各种演示
            self.demonstrate_permission_checking()
            self.demonstrate_dynamic_permissions()
            self.demonstrate_user_management()
            
            # 安全消息传递演示（需要实际的RabbitMQ连接）
            print("\n💡 安全消息传递演示需要RabbitMQ服务器运行")
            print("   请确保RabbitMQ服务已启动并配置相应用户")
            
        except KeyboardInterrupt:
            print("\n⏹️ 演示被用户中断")
        except Exception as e:
            print(f"❌ 演示运行失败: {e}")
        
        print(f"\n🏁 权限管理演示完成")


if __name__ == "__main__":
    # 运行权限管理演示
    demo = PermissionDemo()
    demo.run_permission_demo()