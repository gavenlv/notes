#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于角色的访问控制（RBAC）系统
实现一个完整的RBAC系统，包括用户、角色、权限管理和访问控制
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any
import json
from datetime import datetime
import getpass
import hashlib
import uuid

class Permission(Enum):
    """权限枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"

class Role:
    """角色类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.permissions: Set[Permission] = set()
        self.created_at = datetime.now()
        self.created_by = ""
    
    def add_permission(self, permission: Permission):
        """添加权限"""
        self.permissions.add(permission)
        return True
    
    def remove_permission(self, permission: Permission):
        """移除权限"""
        self.permissions.discard(permission)
        return True
    
    def has_permission(self, permission: Permission) -> bool:
        """检查是否有权限"""
        return permission in self.permissions
    
    def get_permissions(self) -> List[str]:
        """获取权限列表"""
        return [perm.value for perm in self.permissions]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "permissions": self.get_permissions(),
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }
    
    def __str__(self):
        return f"Role({self.name}, {self.get_permissions()})"

class User:
    """用户类"""
    
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.roles: List[Role] = []
        self.created_at = datetime.now()
        self.last_login = None
        self.is_active = True
        self.password_hash = ""
        self.salt = ""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def set_password(self, password: str):
        """设置密码"""
        self.salt = str(uuid.uuid4())
        self.password_hash = self._hash_password(password, self.salt)
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash or not self.salt:
            return False
        
        hashed_password = self._hash_password(password, self.salt)
        return hashed_password == self.password_hash
    
    def _hash_password(self, password: str, salt: str) -> str:
        """哈希密码"""
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def assign_role(self, role: Role):
        """分配角色"""
        if role not in self.roles:
            self.roles.append(role)
            return True
        return False
    
    def revoke_role(self, role: Role):
        """撤销角色"""
        if role in self.roles:
            self.roles.remove(role)
            return True
        return False
    
    def has_permission(self, permission: Permission) -> bool:
        """检查用户是否有权限"""
        if not self.is_active:
            return False
        
        if self.is_locked():
            return False
        
        for role in self.roles:
            if role.has_permission(permission):
                return True
        
        return False
    
    def get_effective_permissions(self) -> Set[Permission]:
        """获取用户有效权限"""
        effective_permissions = set()
        
        for role in self.roles:
            effective_permissions.update(role.permissions)
        
        return effective_permissions
    
    def get_role_names(self) -> List[str]:
        """获取角色名列表"""
        return [role.name for role in self.roles]
    
    def record_login(self, success: bool):
        """记录登录尝试"""
        if success:
            self.last_login = datetime.now()
            self.failed_login_attempts = 0
            self.locked_until = None
        else:
            self.failed_login_attempts += 1
            
            # 连续失败5次后锁定30分钟
            if self.failed_login_attempts >= 5:
                from datetime import timedelta
                self.locked_until = datetime.now() + timedelta(minutes=30)
    
    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        if not self.locked_until:
            return False
        
        return datetime.now() < self.locked_until
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "roles": self.get_role_names(),
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "is_locked": self.is_locked(),
            "locked_until": self.locked_until.isoformat() if self.locked_until else None
        }
    
    def __str__(self):
        return f"User({self.user_id}, {self.name}, {self.get_role_names()})"

class Resource:
    """资源类"""
    
    def __init__(self, resource_id: str, name: str, resource_type: str):
        self.resource_id = resource_id
        self.name = name
        self.resource_type = resource_type
        self.required_permissions: Dict[str, Permission] = {}  # 操作名 -> 权限
        self.created_at = datetime.now()
        self.owner_id = ""
        self.sensitivity_level = "medium"  # low, medium, high, critical
    
    def set_required_permission(self, action: str, permission: Permission):
        """设置操作所需的权限"""
        self.required_permissions[action] = permission
        return True
    
    def remove_required_permission(self, action: str):
        """移除操作所需权限"""
        if action in self.required_permissions:
            del self.required_permissions[action]
            return True
        return False
    
    def get_required_permissions(self) -> Dict[str, str]:
        """获取所需权限字典"""
        return {action: perm.value for action, perm in self.required_permissions.items()}
    
    def check_access(self, user: User, action: str) -> bool:
        """检查用户是否可以访问资源"""
        if action not in self.required_permissions:
            return False  # 未定义的操作
        
        required_permission = self.required_permissions[action]
        return user.has_permission(required_permission)
    
    def get_access_matrix(self) -> Dict[str, str]:
        """获取访问矩阵"""
        return {
            "action": action,
            "required_permission": perm.value,
            "description": f"需要 {perm.value} 权限"
        }
        for action, perm in self.required_permissions.items()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "resource_type": self.resource_type,
            "required_permissions": self.get_required_permissions(),
            "created_at": self.created_at.isoformat(),
            "owner_id": self.owner_id,
            "sensitivity_level": self.sensitivity_level
        }
    
    def __str__(self):
        return f"Resource({self.resource_id}, {self.name}, {self.resource_type})"

class RBACSystem:
    """基于角色的访问控制系统"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.resources: Dict[str, Resource] = {}
        self.audit_log: List[Dict] = []
        self.session_tokens: Dict[str, Dict] = {}
    
    # 用户管理
    def create_user(self, user_id: str, name: str, email: str, password: str = None) -> User:
        """创建用户"""
        if user_id in self.users:
            raise ValueError(f"用户ID {user_id} 已存在")
        
        user = User(user_id, name, email)
        
        if password:
            user.set_password(password)
        
        self.users[user_id] = user
        
        self._log_action("create_user", {
            "user_id": user_id,
            "name": name,
            "email": email
        })
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """更新用户信息"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self._log_action("update_user", {
            "user_id": user_id,
            "updated_fields": list(kwargs.keys())
        })
        
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # 撤销所有角色
        user.roles = []
        
        # 删除用户
        del self.users[user_id]
        
        self._log_action("delete_user", {
            "user_id": user_id
        })
        
        return True
    
    def authenticate_user(self, user_id: str, password: str) -> Optional[str]:
        """用户认证"""
        if user_id not in self.users:
            self._log_action("authentication_failed", {
                "user_id": user_id,
                "reason": "用户不存在"
            })
            return None
        
        user = self.users[user_id]
        
        if not user.is_active:
            self._log_action("authentication_failed", {
                "user_id": user_id,
                "reason": "用户已禁用"
            })
            return None
        
        if user.is_locked():
            self._log_action("authentication_failed", {
                "user_id": user_id,
                "reason": "用户已锁定"
            })
            return None
        
        if not user.verify_password(password):
            user.record_login(False)
            self._log_action("authentication_failed", {
                "user_id": user_id,
                "reason": "密码错误",
                "failed_attempts": user.failed_login_attempts
            })
            return None
        
        # 认证成功
        user.record_login(True)
        
        # 生成会话令牌
        session_token = str(uuid.uuid4())
        self.session_tokens[session_token] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24)  # 24小时过期
        }
        
        self._log_action("authentication_success", {
            "user_id": user_id,
            "session_token": session_token[:8] + "..."  # 只记录部分令牌
        })
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """验证会话"""
        if session_token not in self.session_tokens:
            return None
        
        session = self.session_tokens[session_token]
        
        # 检查会话是否过期
        if datetime.now() > session["expires_at"]:
            del self.session_tokens[session_token]
            return None
        
        # 获取用户
        user_id = session["user_id"]
        return self.users.get(user_id)
    
    def logout(self, session_token: str) -> bool:
        """用户登出"""
        if session_token in self.session_tokens:
            session = self.session_tokens[session_token]
            user_id = session["user_id"]
            
            del self.session_tokens[session_token]
            
            self._log_action("logout", {
                "user_id": user_id
            })
            
            return True
        
        return False
    
    # 角色管理
    def create_role(self, role_name: str, description: str = "", created_by: str = "") -> Role:
        """创建角色"""
        if role_name in self.roles:
            raise ValueError(f"角色 {role_name} 已存在")
        
        role = Role(role_name, description)
        role.created_by = created_by
        
        self.roles[role_name] = role
        
        self._log_action("create_role", {
            "role_name": role_name,
            "description": description,
            "created_by": created_by
        })
        
        return role
    
    def get_role(self, role_name: str) -> Optional[Role]:
        """获取角色"""
        return self.roles.get(role_name)
    
    def update_role(self, role_name: str, **kwargs) -> bool:
        """更新角色"""
        if role_name not in self.roles:
            return False
        
        role = self.roles[role_name]
        
        for key, value in kwargs.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        self._log_action("update_role", {
            "role_name": role_name,
            "updated_fields": list(kwargs.keys())
        })
        
        return True
    
    def delete_role(self, role_name: str) -> bool:
        """删除角色"""
        if role_name not in self.roles:
            return False
        
        # 从所有用户中移除该角色
        for user in self.users.values():
            role = self.roles[role_name]
            user.revoke_role(role)
        
        # 删除角色
        del self.roles[role_name]
        
        self._log_action("delete_role", {
            "role_name": role_name
        })
        
        return True
    
    def assign_role_to_user(self, user_id: str, role_name: str, assigned_by: str = "") -> bool:
        """为用户分配角色"""
        if user_id not in self.users:
            return False
        
        if role_name not in self.roles:
            return False
        
        user = self.users[user_id]
        role = self.roles[role_name]
        
        if user.assign_role(role):
            self._log_action("assign_role", {
                "user_id": user_id,
                "role_name": role_name,
                "assigned_by": assigned_by
            })
            return True
        
        return False
    
    def revoke_role_from_user(self, user_id: str, role_name: str, revoked_by: str = "") -> bool:
        """从用户撤销角色"""
        if user_id not in self.users:
            return False
        
        if role_name not in self.roles:
            return False
        
        user = self.users[user_id]
        role = self.roles[role_name]
        
        if user.revoke_role(role):
            self._log_action("revoke_role", {
                "user_id": user_id,
                "role_name": role_name,
                "revoked_by": revoked_by
            })
            return True
        
        return False
    
    # 资源管理
    def create_resource(self, resource_id: str, name: str, resource_type: str, owner_id: str = "") -> Resource:
        """创建资源"""
        if resource_id in self.resources:
            raise ValueError(f"资源ID {resource_id} 已存在")
        
        resource = Resource(resource_id, name, resource_type)
        resource.owner_id = owner_id
        
        self.resources[resource_id] = resource
        
        self._log_action("create_resource", {
            "resource_id": resource_id,
            "name": name,
            "resource_type": resource_type,
            "owner_id": owner_id
        })
        
        return resource
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """获取资源"""
        return self.resources.get(resource_id)
    
    def update_resource(self, resource_id: str, **kwargs) -> bool:
        """更新资源"""
        if resource_id not in self.resources:
            return False
        
        resource = self.resources[resource_id]
        
        for key, value in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
        
        self._log_action("update_resource", {
            "resource_id": resource_id,
            "updated_fields": list(kwargs.keys())
        })
        
        return True
    
    def delete_resource(self, resource_id: str) -> bool:
        """删除资源"""
        if resource_id not in self.resources:
            return False
        
        del self.resources[resource_id]
        
        self._log_action("delete_resource", {
            "resource_id": resource_id
        })
        
        return True
    
    # 访问控制
    def check_access(self, user_id: str, resource_id: str, action: str, session_token: str = None) -> Dict:
        """检查访问权限"""
        result = {
            "access_granted": False,
            "reason": "",
            "user_id": user_id,
            "resource_id": resource_id,
            "action": action
        }
        
        # 验证用户
        if user_id not in self.users:
            result["reason"] = "用户不存在"
            self._log_action("access_denied", result)
            return result
        
        # 验证资源
        if resource_id not in self.resources:
            result["reason"] = "资源不存在"
            self._log_action("access_denied", result)
            return result
        
        # 如果提供了会话令牌，验证会话
        if session_token:
            user = self.validate_session(session_token)
            if not user or user.user_id != user_id:
                result["reason"] = "无效会话"
                self._log_action("access_denied", result)
                return result
        
        user = self.users[user_id]
        resource = self.resources[resource_id]
        
        # 检查用户状态
        if not user.is_active:
            result["reason"] = "用户已禁用"
            self._log_action("access_denied", result)
            return result
        
        if user.is_locked():
            result["reason"] = "用户已锁定"
            self._log_action("access_denied", result)
            return result
        
        # 检查访问权限
        if resource.check_access(user, action):
            result["access_granted"] = True
            result["reason"] = "权限验证通过"
        else:
            result["reason"] = "权限不足"
        
        self._log_action("access_check", result)
        
        return result
    
    def get_user_permissions(self, user_id: str) -> Dict:
        """获取用户权限"""
        if user_id not in self.users:
            return {}
        
        user = self.users[user_id]
        permissions = user.get_effective_permissions()
        
        return {
            "user_id": user_id,
            "user_name": user.name,
            "roles": user.get_role_names(),
            "permissions": [perm.value for perm in permissions]
        }
    
    def get_role_permissions(self, role_name: str) -> Dict:
        """获取角色权限"""
        if role_name not in self.roles:
            return {}
        
        role = self.roles[role_name]
        
        return {
            "role_name": role_name,
            "description": role.description,
            "permissions": role.get_permissions()
        }
    
    def get_resource_permissions(self, resource_id: str) -> Dict:
        """获取资源权限要求"""
        if resource_id not in self.resources:
            return {}
        
        resource = self.resources[resource_id]
        
        return {
            "resource_id": resource_id,
            "name": resource.name,
            "resource_type": resource.resource_type,
            "required_permissions": resource.get_required_permissions(),
            "owner_id": resource.owner_id
        }
    
    # 审计和报告
    def _log_action(self, action: str, details: Dict):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        self.audit_log.append(log_entry)
    
    def get_audit_log(self, action_filter: Optional[str] = None, user_filter: Optional[str] = None) -> List[Dict]:
        """获取审计日志"""
        filtered_log = self.audit_log
        
        if action_filter:
            filtered_log = [log for log in filtered_log if log["action"] == action_filter]
        
        if user_filter:
            filtered_log = [
                log for log in filtered_log 
                if "user_id" in log["details"] and log["details"]["user_id"] == user_filter
            ]
        
        return filtered_log
    
    def get_access_report(self, user_id: str = None, resource_id: str = None) -> Dict:
        """生成访问报告"""
        access_logs = self.get_audit_log("access_check")
        
        # 过滤日志
        if user_id:
            access_logs = [
                log for log in access_logs 
                if "user_id" in log["details"] and log["details"]["user_id"] == user_id
            ]
        
        if resource_id:
            access_logs = [
                log for log in access_logs 
                if "resource_id" in log["details"] and log["details"]["resource_id"] == resource_id
            ]
        
        # 统计访问情况
        total_attempts = len(access_logs)
        successful_attempts = len([
            log for log in access_logs 
            if log["details"].get("access_granted", False)
        ])
        denied_attempts = total_attempts - successful_attempts
        
        return {
            "report_time": datetime.now().isoformat(),
            "filters": {
                "user_id": user_id,
                "resource_id": resource_id
            },
            "statistics": {
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "denied_attempts": denied_attempts,
                "success_rate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            },
            "recent_access": access_logs[-10:] if access_logs else []
        }
    
    def generate_rbac_report(self) -> Dict:
        """生成RBAC系统报告"""
        # 统计用户、角色和资源数量
        user_count = len(self.users)
        role_count = len(self.roles)
        resource_count = len(self.resources)
        
        # 统计活跃用户数
        active_users = len([u for u in self.users.values() if u.is_active])
        
        # 统计角色分配情况
        role_assignments = sum(len(user.roles) for user in self.users.values())
        
        # 统计资源权限设置
        resources_with_permissions = len([
            r for r in self.resources.values() 
            if r.required_permissions
        ])
        
        return {
            "report_time": datetime.now().isoformat(),
            "summary": {
                "users": {
                    "total": user_count,
                    "active": active_users,
                    "inactive": user_count - active_users
                },
                "roles": {
                    "total": role_count,
                    "assignments": role_assignments
                },
                "resources": {
                    "total": resource_count,
                    "with_permissions": resources_with_permissions
                }
            },
            "permissions": {
                "role_permissions": {
                    role_name: role.get_permissions()
                    for role_name, role in self.roles.items()
                },
                "resource_permissions": {
                    resource_id: resource.get_required_permissions()
                    for resource_id, resource in self.resources.items()
                }
            }
        }

# 使用示例和测试
def demo_rbac_system():
    """演示RBAC系统"""
    print("基于角色的访问控制系统（RBAC）演示")
    print("=" * 50)
    
    # 创建RBAC系统
    rbac = RBACSystem()
    
    # 1. 创建角色
    print("\n1. 创建角色:")
    admin_role = rbac.create_role("admin", "系统管理员", "system")
    admin_role.add_permission(Permission.READ)
    admin_role.add_permission(Permission.WRITE)
    admin_role.add_permission(Permission.DELETE)
    admin_role.add_permission(Permission.EXECUTE)
    admin_role.add_permission(Permission.ADMIN)
    
    analyst_role = rbac.create_role("analyst", "数据分析师", "system")
    analyst_role.add_permission(Permission.READ)
    analyst_role.add_permission(Permission.EXECUTE)
    
    viewer_role = rbac.create_role("viewer", "只读用户", "system")
    viewer_role.add_permission(Permission.READ)
    
    print(f"  创建角色: {admin_role.name}")
    print(f"  创建角色: {analyst_role.name}")
    print(f"  创建角色: {viewer_role.name}")
    
    # 2. 创建用户
    print("\n2. 创建用户:")
    admin_user = rbac.create_user("admin01", "张三", "zhangsan@example.com", "Admin123!")
    analyst_user = rbac.create_user("analyst01", "李四", "lisi@example.com", "Analyst123!")
    viewer_user = rbac.create_user("viewer01", "王五", "wangwu@example.com", "Viewer123!")
    
    print(f"  创建用户: {admin_user.name}")
    print(f"  创建用户: {analyst_user.name}")
    print(f"  创建用户: {viewer_user.name}")
    
    # 3. 分配角色
    print("\n3. 分配角色:")
    rbac.assign_role_to_user("admin01", "admin", "system")
    rbac.assign_role_to_user("analyst01", "analyst", "system")
    rbac.assign_role_to_user("viewer01", "viewer", "system")
    
    print(f"  为 {admin_user.name} 分配角色: {admin_user.get_role_names()}")
    print(f"  为 {analyst_user.name} 分配角色: {analyst_user.get_role_names()}")
    print(f"  为 {viewer_user.name} 分配角色: {viewer_user.get_role_names()}")
    
    # 4. 创建资源
    print("\n4. 创建资源:")
    customer_data = rbac.create_resource("customer_data", "客户数据", "database", "system")
    customer_data.set_required_permission("read", Permission.READ)
    customer_data.set_required_permission("write", Permission.WRITE)
    customer_data.set_required_permission("delete", Permission.DELETE)
    
    report_system = rbac.create_resource("report_system", "报表系统", "application", "system")
    report_system.set_required_permission("view", Permission.READ)
    report_system.set_required_permission("generate", Permission.EXECUTE)
    
    print(f"  创建资源: {customer_data.name}")
    print(f"  创建资源: {report_system.name}")
    
    # 5. 测试访问权限
    print("\n5. 测试访问权限:")
    
    # 认证用户
    admin_token = rbac.authenticate_user("admin01", "Admin123!")
    analyst_token = rbac.authenticate_user("analyst01", "Analyst123!")
    viewer_token = rbac.authenticate_user("viewer01", "Viewer123!")
    
    # 测试管理员权限
    admin_read = rbac.check_access("admin01", "customer_data", "read", admin_token)
    admin_delete = rbac.check_access("admin01", "customer_data", "delete", admin_token)
    admin_generate = rbac.check_access("admin01", "report_system", "generate", admin_token)
    
    print(f"  管理员读取客户数据: {admin_read['access_granted']} ({admin_read['reason']})")
    print(f"  管理员删除客户数据: {admin_delete['access_granted']} ({admin_delete['reason']})")
    print(f"  管理员生成报表: {admin_generate['access_granted']} ({admin_generate['reason']})")
    
    # 测试分析师权限
    analyst_read = rbac.check_access("analyst01", "customer_data", "read", analyst_token)
    analyst_delete = rbac.check_access("analyst01", "customer_data", "delete", analyst_token)
    analyst_generate = rbac.check_access("analyst01", "report_system", "generate", analyst_token)
    
    print(f"  分析师读取客户数据: {analyst_read['access_granted']} ({analyst_read['reason']})")
    print(f"  分析师删除客户数据: {analyst_delete['access_granted']} ({analyst_delete['reason']})")
    print(f"  分析师生成报表: {analyst_generate['access_granted']} ({analyst_generate['reason']})")
    
    # 测试只读用户权限
    viewer_read = rbac.check_access("viewer01", "customer_data", "read", viewer_token)
    viewer_delete = rbac.check_access("viewer01", "customer_data", "delete", viewer_token)
    viewer_generate = rbac.check_access("viewer01", "report_system", "generate", viewer_token)
    
    print(f"  只读用户读取客户数据: {viewer_read['access_granted']} ({viewer_read['reason']})")
    print(f"  只读用户删除客户数据: {viewer_delete['access_granted']} ({viewer_delete['reason']})")
    print(f"  只读用户生成报表: {viewer_generate['access_granted']} ({viewer_generate['reason']})")
    
    # 6. 查看用户权限
    print("\n6. 用户权限:")
    for user_id in ["admin01", "analyst01", "viewer01"]:
        user_permissions = rbac.get_user_permissions(user_id)
        print(f"\n  {user_permissions['user_name']} ({user_permissions['user_id']}):")
        print(f"    角色: {', '.join(user_permissions['roles'])}")
        print(f"    权限: {', '.join(user_permissions['permissions'])}")
    
    # 7. 生成访问报告
    print("\n7. 访问报告:")
    access_report = rbac.get_access_report()
    print(f"  总访问尝试: {access_report['statistics']['total_attempts']}")
    print(f"  成功访问: {access_report['statistics']['successful_attempts']}")
    print(f"  被拒访问: {access_report['statistics']['denied_attempts']}")
    print(f"  成功率: {access_report['statistics']['success_rate']:.1f}%")
    
    # 8. 生成系统报告
    print("\n8. 系统报告:")
    system_report = rbac.generate_rbac_report()
    summary = system_report['summary']
    print(f"  用户总数: {summary['users']['total']} (活跃: {summary['users']['active']})")
    print(f"  角色总数: {summary['roles']['total']} (分配次数: {summary['roles']['assignments']})")
    print(f"  资源总数: {summary['resources']['total']} (有权限设置: {summary['resources']['with_permissions']})")
    
    # 9. 测试用户锁定机制
    print("\n9. 测试用户锁定机制:")
    
    # 模拟多次登录失败
    for i in range(5):
        rbac.authenticate_user("viewer01", "wrongpassword")
    
    # 尝试用正确密码登录
    login_after_lock = rbac.authenticate_user("viewer01", "Viewer123!")
    
    print(f"  5次错误密码后尝试登录: {login_after_lock is None} (预期: True，因为用户被锁定)")
    
    return rbac

# 运行演示
if __name__ == "__main__":
    rbac_system = demo_rbac_system()