import os
from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

# Your App secret key
SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h'

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 数据库连接池配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True,
    'max_overflow': 20
}

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# Authentication configuration
AUTH_TYPE = AUTH_DB
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# 缓存配置
CACHE_TYPE = 'simple'  # 生产环境建议使用Redis或Memcached
CACHE_DEFAULT_TIMEOUT = 300

# 静态文件缓存
SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1年

APP_NAME = "Performance Optimized App"