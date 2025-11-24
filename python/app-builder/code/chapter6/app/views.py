from flask_appbuilder import BaseView, expose, ModelView
from flask_appbuilder.security.decorators import has_access, permission_name
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import flash, redirect
from .models import User, AuditLog

class UserManagementView(ModelView):
    datamodel = SQLAInterface(User)
    list_columns = ['username', 'email', 'is_active', 'department', 'last_login']
    
    @has_access
    def deactivate_user(self, pk):
        """停用用户"""
        user = self.datamodel.get(pk)
        if user:
            user.is_active = False
            self.datamodel.edit(user)
            flash(f'User {user.username} has been deactivated', 'info')
        return redirect(self.get_redirect())
    
    @has_access
    def activate_user(self, pk):
        """激活用户"""
        user = self.datamodel.get(pk)
        if user:
            user.is_active = True
            self.datamodel.edit(user)
            flash(f'User {user.username} has been activated', 'info')
        return redirect(self.get_redirect())

class AuditLogView(ModelView):
    datamodel = SQLAInterface(AuditLog)
    list_columns = ['user_id', 'action', 'resource', 'timestamp', 'details']
    search_columns = ['action', 'resource', 'timestamp']

class AdminView(BaseView):
    route_base = '/admin'
    
    @expose('/settings/')
    @permission_name('can_change_settings')
    @has_access
    def settings(self):
        return self.render_template('admin/settings.html')
    
    @expose('/reports/')
    @permission_name('can_view_reports')
    @has_access
    def reports(self):
        return self.render_template('admin/reports.html')
    
    @expose('/export/')
    @permission_name('can_export_data')
    @has_access
    def export_data(self):
        flash('Data exported successfully', 'success')
        return redirect('/admin/reports/')