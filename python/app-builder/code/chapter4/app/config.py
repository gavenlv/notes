import os

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 认证配置
AUTH_TYPE = 1  # 数据库认证
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = 'Public'

# 应用配置
APP_NAME = "Flask App-Builder Auth Tutorial"
APP_THEME = ""

# 安全日志
SECURITY_LOGGING = True