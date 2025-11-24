import os
from flask_appbuilder.security.manager import AUTH_DB

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))

# SQLAlchemy配置
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Flask-AppBuilder配置
APP_NAME = "Flask AppBuilder Plugin Demo"
APP_THEME = ""
APP_ICON = ""

# 认证配置
AUTH_TYPE = AUTH_DB
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# CSRF保护
WTF_CSRF_ENABLED = True

# 邮件配置
MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'admin@example.com'

# Redis配置
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

# Celery配置
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# 插件启用配置
ENABLE_AUDIT_LOG_PLUGIN = True
ENABLE_EMAIL_SERVICE_PLUGIN = True
ENABLE_TASK_MANAGER_PLUGIN = True
ENABLE_REDIS_CACHE_PLUGIN = True
ENABLE_CELERY_TASKS_PLUGIN = True

# 安全配置
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
SECURITY_REGISTER_USER = True

# 文件上传配置
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# 日志配置
LOG_LEVEL = 'INFO'
AUDIT_LOG_FILE = os.path.join(basedir, 'logs', 'audit.log')

# 缓存配置
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = REDIS_URL
CACHE_DEFAULT_TIMEOUT = 300

class Config:
    """配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-AppBuilder配置
    APP_NAME = "Flask AppBuilder Plugin Demo"
    APP_THEME = ""
    
    # 认证配置
    AUTH_TYPE = AUTH_DB
    AUTH_ROLE_ADMIN = 'Admin'
    AUTH_ROLE_PUBLIC = 'Public'
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # 插件配置
    ENABLE_AUDIT_LOG_PLUGIN = True
    ENABLE_EMAIL_SERVICE_PLUGIN = True
    ENABLE_TASK_MANAGER_PLUGIN = True
    ENABLE_REDIS_CACHE_PLUGIN = True
    ENABLE_CELERY_TASKS_PLUGIN = True
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}