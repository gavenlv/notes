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
AUTH_USER_REGISTRATION_ROLE = 'User'

# 安全配置
SECRET_KEY = 'your-secret-key-here'
WTF_CSRF_ENABLED = True
CSRF_ENABLED = True

# 会话安全
SESSION_COOKIE_SECURE = False  # 开发环境设为False，生产环境设为True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 1800

# 应用配置
APP_NAME = "Flask App-Builder Advanced Security Demo"
APP_THEME = ""