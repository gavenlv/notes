import os

# 数据库配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 安全配置
SECRET_KEY = 'your-secret-key-here'
WTF_CSRF_ENABLED = True

# 应用配置
APP_NAME = "Flask App-Builder REST API Demo"