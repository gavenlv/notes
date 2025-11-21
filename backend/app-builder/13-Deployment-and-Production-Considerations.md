# 第十三章：部署和生产环境考虑

将Flask-AppBuilder应用程序从开发环境迁移到生产环境是一个复杂的过程，需要考虑多个方面以确保应用程序的安全性、性能和可靠性。本章将详细介绍部署Flask-AppBuilder应用程序的最佳实践和注意事项。

## 目录
1. 生产环境部署概述
2. 服务器配置
3. 数据库配置
4. 安全配置
5. 性能优化
6. 日志管理
7. 监控和告警
8. 备份和恢复
9. 容器化部署
10. 云平台部署
11. 完整部署示例
12. 故障排除

## 1. 生产环境部署概述

### 部署环境差异
生产环境与开发环境存在显著差异：
- **安全性要求更高**：需要严格的访问控制和数据保护
- **性能要求更高**：需要处理大量并发请求
- **稳定性要求更高**：需要最小化停机时间和错误率
- **监控要求更严格**：需要实时监控应用状态和性能指标

### 部署架构选择
常见的部署架构包括：
- **单服务器部署**：适用于小型应用
- **负载均衡部署**：适用于中大型应用
- **微服务架构**：适用于复杂应用系统

## 2. 服务器配置

### 操作系统选择
推荐使用稳定的Linux发行版：
- Ubuntu Server LTS
- CentOS/RHEL
- Debian Stable

### Web服务器配置
推荐使用以下Web服务器：
- Nginx：高性能反向代理和静态文件服务
- Apache：成熟稳定的Web服务器

### 应用服务器配置
常用的Python应用服务器：
- Gunicorn：轻量级WSGI服务器
- uWSGI：功能丰富的WSGI服务器
- Waitress：跨平台WSGI服务器

### 示例Nginx配置

```nginx
# /etc/nginx/sites-available/flask-appbuilder
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向HTTP到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 客户端最大请求体大小
    client_max_body_size 10M;
    
    # 静态文件处理
    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 反向代理到Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### 示例Gunicorn配置

```python
# gunicorn.conf.py
import multiprocessing

# 服务器套接字
bind = "127.0.0.1:8000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类
worker_class = "sync"

# 工作进程超时时间
timeout = 30

# 重启工作进程前的最大请求数
max_requests = 1000
max_requests_jitter = 100

# 日志配置
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# 进程命名
proc_name = "flask-appbuilder"

# 优雅重启
preload_app = True

# 守护进程模式
daemon = False
```

## 3. 数据库配置

### 数据库选择
生产环境中推荐使用的数据库：
- PostgreSQL：功能强大，支持高级特性
- MySQL/MariaDB：广泛使用，社区支持好
- SQLite：仅适用于小型应用

### 数据库连接池配置

```python
# config.py
class ProductionConfig(Config):
    # 数据库URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/dbname'
    
    # 连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30,
        'connect_args': {
            'connect_timeout': 10,
        }
    }
    
    # 关闭跟踪修改以节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 数据库备份策略

```bash
#!/bin/bash
# backup.sh - 数据库备份脚本

# 配置变量
DB_NAME="your_database"
BACKUP_DIR="/backup/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
pg_dump $DB_NAME > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

# 记录日志
echo "$(date): Backup completed - ${BACKUP_FILE}.gz" >> /var/log/backup.log
```

## 4. 安全配置

### 环境变量管理

```bash
# .env.production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.your-domain.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@your-domain.com
MAIL_PASSWORD=your-email-password
```

### Flask-AppBuilder安全配置

```python
# config.py
class ProductionConfig(Config):
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # CSRF保护
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = True
    
    # Session配置
    SESSION_COOKIE_SECURE = True  # 仅在HTTPS下传输
    SESSION_COOKIE_HTTPONLY = True  # 防止XSS攻击
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF保护
    
    # 密码安全
    PASSWORD_COMPLEXITY = {
        'min_length': 8,
        'special_chars': True,
        'digits': True,
        'upper_case': True,
        'lower_case': True
    }
    
    # 登录安全
    AUTH_LDAP_SERVER = "ldaps://ldap.example.com"
    AUTH_LDAP_USE_TLS = True
```

### HTTPS配置

```python
# app/__init__.py
from flask_talisman import Talisman

# HTTPS强制和安全头配置
Talisman(app, 
         force_https=True,
         force_https_permanent=True,
         frame_options='DENY',
         referrer_policy='no-referrer',
         content_security_policy={
             'default-src': "'self'",
             'script-src': "'self' 'unsafe-inline'",
             'style-src': "'self' 'unsafe-inline'"
         })
```

## 5. 性能优化

### 缓存配置

```python
# config.py
class ProductionConfig(Config):
    # Redis缓存配置
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 静态文件缓存
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1年
    
    # 压缩配置
    COMPRESS_MIMETYPES = [
        'text/html',
        'text/css',
        'text/xml',
        'application/json',
        'application/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
```

### 数据库查询优化

```python
# app/models.py
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref

class Category(Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)  # 添加索引
    products = relationship("Product", back_populates="category")
    
    # 添加复合索引
    __table_args__ = (
        Index('idx_category_name_active', 'name'),
    )

class Product(Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    price = Column(Integer, index=True)  # 为价格字段添加索引
    category_id = Column(Integer, ForeignKey('category.id'), index=True)
    category = relationship("Category", back_populates="products")
    
    # 添加复合索引
    __table_args__ = (
        Index('idx_product_category_price', 'category_id', 'price'),
        Index('idx_product_name_category', 'name', 'category_id'),
    )
```

## 6. 日志管理

### 日志配置

```python
# config.py
import logging
from logging.handlers import RotatingFileHandler

class ProductionConfig(Config):
    # 日志配置
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
    LOG_FILE = '/var/log/flask-appbuilder/app.log'
    LOG_MAX_BYTES = 1024 * 1024 * 100  # 100MB
    LOG_BACKUP_COUNT = 10
```

### 应用日志设置

```python
# app/__init__.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """设置应用日志"""
    if not app.debug and not app.testing:
        # 文件日志处理器
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/app.log'),
            maxBytes=app.config.get('LOG_MAX_BYTES', 1024*1024*100),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        
        file_handler.setFormatter(logging.Formatter(
            app.config.get('LOG_FORMAT', 
                          '%(asctime)s %(levelname)s %(name)s %(message)s')
        ))
        
        file_handler.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
        app.logger.info('Application startup')

def create_app(config_name='production'):
    """创建应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 设置日志
    setup_logging(app)
    
    # 初始化扩展
    db.init_app(app)
    appbuilder.init_app(app, db.session)
    
    return app
```

## 7. 监控和告警

### 健康检查端点

```python
# app/__init__.py
@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        # 检查Redis连接
        if app.config.get('CACHE_TYPE') == 'redis':
            from redis import Redis
            redis_client = Redis.from_url(app.config.get('CACHE_REDIS_URL'))
            redis_client.ping()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'database': 'ok',
                'redis': 'ok' if app.config.get('CACHE_TYPE') == 'redis' else 'not_configured'
            }
        }), 200
    except Exception as e:
        app.logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500
```

### Prometheus监控集成

```python
# app/__init__.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# 定义监控指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP Request Duration')

@app.before_request
def before_request():
    """请求前处理"""
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """请求后处理"""
    # 记录请求持续时间
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_DURATION.observe(duration)
    
    # 记录请求计数
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    
    return response

@app.route('/metrics')
def metrics():
    """Prometheus指标端点"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
```

## 8. 备份和恢复

### 应用备份脚本

```bash
#!/bin/bash
# backup_app.sh - 应用备份脚本

# 配置变量
APP_DIR="/var/www/flask-appbuilder"
BACKUP_DIR="/backup/application"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="flask-appbuilder-$DATE"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 停止应用服务
sudo systemctl stop flask-appbuilder

# 备份应用文件
tar -czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" -C $(dirname $APP_DIR) $(basename $APP_DIR)

# 备份数据库
pg_dump your_database > "$BACKUP_DIR/${BACKUP_NAME}-db.sql"

# 启动应用服务
sudo systemctl start flask-appbuilder

# 删除7天前的备份
find $BACKUP_DIR -name "flask-appbuilder-*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "flask-appbuilder-*-db.sql" -mtime +7 -delete

# 记录日志
echo "$(date): Application backup completed" >> /var/log/backup.log
```

### 恢复脚本

```bash
#!/bin/bash
# restore_app.sh - 应用恢复脚本

BACKUP_FILE=$1
DB_BACKUP_FILE=$2

if [ -z "$BACKUP_FILE" ] || [ -z "$DB_BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.tar.gz> <db-backup-file.sql>"
    exit 1
fi

# 停止应用服务
sudo systemctl stop flask-appbuilder

# 恢复应用文件
tar -xzf $BACKUP_FILE -C /var/www/

# 恢复数据库
psql your_database < $DB_BACKUP_FILE

# 启动应用服务
sudo systemctl start flask-appbuilder

echo "Application restored successfully"
```

## 9. 容器化部署

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--config", "gunicorn.conf.py", "run:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_CONFIG=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/flask_appbuilder
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: flask_appbuilder
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

## 10. 云平台部署

### AWS部署

```yaml
# AWS Elastic Beanstalk配置
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: run:app
  aws:elasticbeanstalk:application:environment:
    FLASK_CONFIG: production
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 10
  aws:autoscaling:trigger:
    BreachDuration: 5
    UpperThreshold: 60
    LowerThreshold: 20
```

### Heroku部署

```python
# Procfile
web: gunicorn run:app

# runtime.txt
python-3.9.7
```

```bash
# 部署命令
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set FLASK_CONFIG=production
git push heroku main
```

## 11. 完整部署示例

### 项目结构
```
chapter13/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── utils.py
├── config.py
├── run.py
├── requirements.txt
├── gunicorn.conf.py
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── backup.sh
├── restore.sh
└── systemd/
    └── flask-appbuilder.service
```

### requirements.txt

```txt
Flask-AppBuilder==4.3.0
gunicorn==20.1.0
psycopg2-binary==2.9.3
redis==4.3.4
Flask-Talisman==1.0.0
prometheus-client==0.14.1
python-dotenv==0.20.0
```

### 配置文件 (config.py)

```python
import os
from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    AUTH_TYPE = AUTH_DB
    AUTH_ROLE_ADMIN = 'Admin'
    AUTH_ROLE_PUBLIC = 'Public'
    APP_NAME = "Production App"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    # 生产环境配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/dbname'
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30,
        'connect_args': {
            'connect_timeout': 10,
        }
    }
    
    # 缓存配置
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/var/log/flask-appbuilder/app.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 1024 * 1024 * 100))  # 100MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 10))

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
```

### 应用初始化文件 (app/__init__.py)

```python
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, g
from flask_appbuilder import SQLA, AppBuilder
from datetime import datetime
import time

# 初始化扩展
db = SQLA()
appbuilder = AppBuilder()

def setup_logging(app):
    """设置应用日志"""
    if not app.debug and not app.testing:
        # 确保日志目录存在
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 文件日志处理器
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/app.log'),
            maxBytes=app.config.get('LOG_MAX_BYTES', 1024*1024*100),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        ))
        
        file_handler.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
        app.logger.info('Application startup')

def create_app(config_name=None):
    """创建应用实例"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 设置日志
    setup_logging(app)
    
    # 初始化扩展
    db.init_app(app)
    appbuilder.init_app(app, db.session)
    
    # 注册蓝图
    from .views import ProductModelView, CategoryModelView
    appbuilder.add_view(
        ProductModelView,
        "Products",
        icon="fa-product-hunt",
        category="Catalog"
    )
    
    appbuilder.add_view(
        CategoryModelView,
        "Categories",
        icon="fa-tags",
        category="Catalog"
    )
    
    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            
            # 检查Redis连接
            if app.config.get('CACHE_TYPE') == 'redis':
                from redis import Redis
                redis_client = Redis.from_url(app.config.get('CACHE_REDIS_URL'))
                redis_client.ping()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'database': 'ok',
                    'redis': 'ok' if app.config.get('CACHE_TYPE') == 'redis' else 'not_configured'
                }
            }), 200
        except Exception as e:
            app.logger.error(f'Health check failed: {str(e)}')
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500
    
    # 请求处理钩子
    @app.before_request
    def before_request():
        """请求前处理"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 记录请求日志
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.info(
                f'{request.remote_addr} "{request.method} {request.path}" '
                f'{response.status_code} {duration:.3f}s'
            )
        
        return response
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal error: {str(error)}')
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# 创建应用实例
app = create_app()
```

### 模型文件 (app/models.py)

```python
from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

class Category(Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    products = relationship("Product", back_populates="category")
    
    __table_args__ = (
        Index('idx_category_name', 'name'),
    )
    
    def __repr__(self):
        return self.name

class Product(Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    price = Column(Integer, index=True)
    category_id = Column(Integer, ForeignKey('category.id'), index=True)
    category = relationship("Category", back_populates="products")
    
    __table_args__ = (
        Index('idx_product_category_price', 'category_id', 'price'),
        Index('idx_product_name_category', 'name', 'category_id'),
    )
    
    def __repr__(self):
        return self.name
```

### 视图文件 (app/views.py)

```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Product, Category

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    list_columns = ['name', 'category.name', 'price']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'category', 'price']}),
    ]

class CategoryModelView(ModelView):
    datamodel = SQLAInterface(Category)
    list_columns = ['name']
```

### 运行文件 (run.py)

```python
import os
from app import app

if __name__ == '__main__':
    # 获取配置名称
    config_name = os.environ.get('FLASK_CONFIG', 'production')
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )
```

### Systemd服务文件 (systemd/flask-appbuilder.service)

```ini
[Unit]
Description=Flask AppBuilder Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/flask-appbuilder
Environment=FLASK_CONFIG=production
Environment=PATH=/var/www/flask-appbuilder/venv/bin
ExecStart=/var/www/flask-appbuilder/venv/bin/gunicorn --config gunicorn.conf.py run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx配置文件 (nginx.conf)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream flask_app {
        server 127.0.0.1:8000;
    }
    
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        ssl_certificate /etc/nginx/ssl/certificate.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        client_max_body_size 10M;
        
        location /static {
            alias /var/www/flask-appbuilder/app/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        location / {
            proxy_pass http://flask_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }
}
```

### 部署脚本 (deploy.sh)

```bash
#!/bin/bash
# deploy.sh - 自动部署脚本

set -e

# 配置变量
APP_NAME="flask-appbuilder"
APP_DIR="/var/www/$APP_NAME"
BACKUP_DIR="/backup/$APP_NAME"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Starting deployment..."

# 创建备份
echo "Creating backup..."
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" -C $(dirname $APP_DIR) $(basename $APP_DIR) 2>/dev/null || true

# 停止服务
echo "Stopping service..."
sudo systemctl stop $APP_NAME

# 更新代码
echo "Updating code..."
cd $APP_DIR
git pull origin main

# 安装依赖
echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 运行数据库迁移
echo "Running database migrations..."
flask db upgrade

# 启动服务
echo "Starting service..."
sudo systemctl start $APP_NAME

# 检查服务状态
echo "Checking service status..."
sleep 5
if sudo systemctl is-active --quiet $APP_NAME; then
    echo "Deployment successful!"
else
    echo "Deployment failed! Rolling back..."
    # 这里可以添加回滚逻辑
    exit 1
fi
```

## 12. 故障排除

### 常见问题和解决方案

1. **数据库连接失败**
   ```bash
   # 检查数据库服务状态
   sudo systemctl status postgresql
   
   # 检查连接字符串
   echo $DATABASE_URL
   
   # 测试数据库连接
   psql $DATABASE_URL
   ```

2. **应用启动失败**
   ```bash
   # 查看应用日志
   journalctl -u flask-appbuilder -f
   
   # 检查配置文件
   cat /var/www/flask-appbuilder/.env
   
   # 手动启动应用查看错误
   cd /var/www/flask-appbuilder
   source venv/bin/activate
   python run.py
   ```

3. **权限问题**
   ```bash
   # 检查文件权限
   ls -la /var/www/flask-appbuilder
   
   # 修复权限
   sudo chown -R www-data:www-data /var/www/flask-appbuilder
   sudo chmod -R 755 /var/www/flask-appbuilder
   ```

4. **性能问题**
   ```bash
   # 监控系统资源
   top
   htop
   
   # 查看应用日志中的慢查询
   grep "slow query" /var/log/flask-appbuilder/app.log
   
   # 分析数据库查询
   EXPLAIN ANALYZE SELECT * FROM product WHERE category_id = 1;
   ```

通过本章的学习，你应该能够：
- 理解生产环境部署的关键考虑因素
- 配置安全可靠的服务器环境
- 实现高可用的数据库部署方案
- 设置完善的日志管理和监控系统
- 使用容器化技术简化部署流程
- 处理常见的部署故障和问题