import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLA(app)

# 导入自定义安全管理器
from app.security import CustomSecurityManager
appbuilder = AppBuilder(app, db.session, security_manager_class=CustomSecurityManager)

# 创建表
@app.before_first_request
def create_tables():
    db.create_all()
    
    # 创建默认用户和角色
    create_default_data()

def create_default_data():
    """创建默认数据"""
    # 创建角色
    admin_role = appbuilder.sm.find_role('Admin')
    if not admin_role:
        appbuilder.sm.add_role('Admin')
    
    user_role = appbuilder.sm.find_role('User')
    if not user_role:
        appbuilder.sm.add_role('User')
    
    # 创建管理员用户
    admin_user = appbuilder.sm.find_user(username='admin')
    if not admin_user:
        appbuilder.sm.add_user(
            'admin', 'Admin', 'User', 'admin@example.com',
            appbuilder.sm.find_role('Admin'),
            password='admin123'
        )

# 注册视图
from app.views import UserManagementView, AuditLogView, AdminView

appbuilder.add_view(UserManagementView, "User Management", icon="fa-user", category="Admin")
appbuilder.add_view(AuditLogView, "Audit Logs", icon="fa-list", category="Admin")
appbuilder.add_view_no_menu(AdminView)
appbuilder.add_link("Settings", href='/admin/settings/', icon="fa-cog", category="Admin")
appbuilder.add_link("Reports", href='/admin/reports/', icon="fa-bar-chart", category="Admin")

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder Advanced Security!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)