from flask_appbuilder.security.manager import SecurityManager
from flask_appbuilder.security.views import AuthDBView
from flask import flash, redirect, url_for
from datetime import datetime

class CustomAuthDBView(AuthDBView):
    login_template = 'security/login.html'
    
    def auth_user_db(self, username, password):
        # 添加额外的安全检查
        user = super().auth_user_db(username, password)
        if user:
            # 记录登录时间
            user.last_login = datetime.utcnow()
            self.appbuilder.get_session.commit()
            
            # 检查账户状态
            if not user.is_active:
                flash('Account is deactivated', 'warning')
                return None
                
        return user

class CustomSecurityManager(SecurityManager):
    authdbview = CustomAuthDBView
    
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        # 初始化自定义权限
        self.init_custom_permissions()
    
    def init_custom_permissions(self):
        """初始化自定义权限"""
        # 创建自定义权限
        self.add_permission('can_export_data')
        self.add_permission('can_manage_users')
        self.add_permission('can_view_audit_logs')
        
        # 分配权限给角色
        admin_role = self.find_role('Admin')
        if admin_role:
            self.add_permission_to_role(admin_role, self.find_permission('can_export_data'))
            self.add_permission_to_role(admin_role, self.find_permission('can_manage_users'))
    
    def can_access(self, permission_name, view_name):
        """自定义权限检查"""
        user = self.get_user()
        if not user:
            return False
            
        # 超级管理员拥有所有权限
        if user.username == 'superadmin':
            return True
            
        return super().can_access(permission_name, view_name)