import os

# Flask配置
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-chapter15'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-AppBuilder配置
APP_NAME = "Chapter 15 - REST API Demo"
APP_THEME = ""
APP_ICON = ""

# JWT配置
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时

# 缓存配置
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

# Swagger配置
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTX_MASK_SWAGGER = False