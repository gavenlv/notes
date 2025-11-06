# Day 13: 部署策略

## 用户故事 1: 开发环境部署

### 描述
作为数据科学家/开发人员，我希望在开发环境中快速部署Superset，以便我可以开发、测试和调试新的图表和仪表板。

### 验收标准
- 能够在本地开发环境中快速启动Superset实例
- 支持代码和配置的实时更新
- 包含开发工具和调试选项
- 适合开发和测试新功能

### 分步指南

#### Docker Compose 开发环境

```yaml
# docker-compose-dev.yml
version: '3.8'

services:
  superset:
    image: apache/superset:latest-dev
    container_name: superset-dev
    ports:
      - "8088:8088"  # Web界面端口
      - "5000:5000"  # 调试端口
    environment:
      - SUPERSET_ENVIRONMENT=development
      - SUPERSET_CONFIG_PATH=/app/pythonpath_dev/superset_config.py
      - PYTHONDONTWRITEBYTECODE=1  # 禁用.pyc文件生成
      - PYTHONUNBUFFERED=1  # 实时输出
    volumes:
      - ./superset-config:/app/pythonpath_dev  # 挂载自定义配置
      - ./superset:/app/superset  # 挂载Superset源码用于开发
      - ./requirements-dev.txt:/app/requirements-dev.txt
    command: |
      bash -c "pip install -r requirements-dev.txt && \
              superset db upgrade && \
              superset fab create-admin \
                --username admin \
                --firstname Superset \
                --lastname Admin \
                --email admin@example.com \
                --password admin && \
              superset init && \
              flask run --host=0.0.0.0 --port=8088 --with-threads"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8088/health"]
      interval: 1m
      timeout: 10s
      retries: 3
```

#### 开发配置文件

```python
# superset_config.py - 开发环境配置
import os
from datetime import timedelta

# 基础配置
SECRET_KEY = 'dev-secret-key-change-in-production'
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 开发环境特定配置
DEBUG = True
ASSETS_DEBUG = True  # 静态文件调试模式
WTF_CSRF_ENABLED = False  # 开发环境禁用CSRF保护
TALISMAN_ENABLED = False  # 开发环境禁用Talisman安全头

# 缓存配置 - 开发环境使用内存缓存
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
}

# 会话配置
SESSION_COOKIE_SECURE = False  # 开发环境不强制HTTPS
SESSION_COOKIE_HTTPONLY = False  # 开发环境允许JavaScript访问Cookie
SESSION_COOKIE_SAMESITE = None  # 开发环境不限制SameSite

# 日志配置
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s'

# Flask-Babel配置（国际化）
BABEL_DEFAULT_LOCALE = 'zh'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

# SQL Lab配置
SQLLAB_ASYNC_TIME_LIMIT_SEC = 300  # 异步查询超时
SQLLAB_TIMEOUT = 300  # SQL Lab查询超时
SQLLAB_QUERY_COST_FORMATTERS = {}
SQLLAB_MAX_ROW = 10000  # 结果集最大行数

# 时间范围设置
DEFAULT_TIME_GRAIN = 'P1D'  # 默认时间粒度（1天）
DEFAULT_RELATIVE_START_TIME = '-1 month'  # 默认相对开始时间
DEFAULT_RELATIVE_END_TIME = 'now'  # 默认相对结束时间

# 图表配置
CHART_TYPE_REGISTRY = {}

# 允许的额外CSS类
ADDITIONAL_CSS_CLASES = []

# 允许的额外JS文件
ADDITIONAL_JS_FILES = []

# 开发工具集成
ENABLE_PROXY_FIX = True
ENABLE_CORS = True
CORS_OPTIONS = {
    'origins': ['*'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['*'],
}

# 自定义插件路径
PLUGINS_FOLDER = os.path.join(os.path.dirname(__file__), 'plugins')

# 自定义主题
THEMES_PATH = os.path.join(os.path.dirname(__file__), 'themes')

# 自定义颜色方案
DEFAULT_COLOR_SCHEMA = 'superset'
DEFAULT_SERIES_COLORS = [
    '#0074D9', '#FF4136', '#2ECC40', '#FFDC00', '#B10DC9',
    '#FF851B', '#7FDBFF', '#85144b', '#F012BE', '#39CCCC',
    '#01FF70', '#FFDC00', '#B10DC9', '#FF851B', '#7FDBFF'
]
```

#### 开发环境快速启动脚本

```bash
#!/bin/bash
# start-dev-env.sh

# 创建必要的目录
mkdir -p superset-config superset

# 创建基础配置文件
cat > superset-config/superset_config.py << 'EOF'
import os
SECRET_KEY = 'dev-secret-key-change-in-production'
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset.db'
DEBUG = True
ASSETS_DEBUG = True
WTF_CSRF_ENABLED = False
TALISMAN_ENABLED = False
EOF

# 创建requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
pytest
pytest-cov
black
flake8
isort
jupyter
jupyterlab
EOF

# 启动开发环境
docker-compose -f docker-compose-dev.yml up -d

echo "开发环境启动中，请等待30秒后访问 http://localhost:8088"
echo "用户名: admin, 密码: admin"
```

## 用户故事 2: 生产环境部署

### 描述
作为系统管理员/DevOps工程师，我希望在生产环境中安全、稳定地部署Superset，以支持公司内部的数据分析和报表需求。

### 验收标准
- 采用安全的配置和最佳实践
- 支持高并发访问和大规模数据处理
- 包含完整的监控和日志系统
- 提供备份和恢复机制
- 符合企业安全合规要求

### 分步指南

#### 生产环境架构设计

```mermaid
graph TD
    A[用户] --> B[负载均衡器]
    B --> C1[Superset Web 服务器 1]
    B --> C2[Superset Web 服务器 2]
    B --> C3[Superset Web 服务器 N]
    
    C1 --> D[(PostgreSQL 数据库)]
    C2 --> D
    C3 --> D
    
    C1 --> E[Redis 缓存]
    C2 --> E
    C3 --> E
    
    F[(对象存储 - 图表缓存和查询结果)] --> C1
    F --> C2
    F --> C3
    
    G[监控系统] --> C1
    G --> C2
    G --> C3
    G --> D
    G --> E
    
    H[告警系统] --> G
```

#### PostgreSQL 数据库配置

```sql
-- 创建Superset数据库和用户
CREATE DATABASE superset;
CREATE USER superset WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE superset TO superset;

-- 连接到Superset数据库
\c superset

-- 授予权限
GRANT ALL ON SCHEMA public TO superset;
-- 为生产环境设置适当的表空间
CREATE TABLESPACE superset_tablespace OWNER superset LOCATION '/var/lib/postgresql/data/superset';

-- 优化配置（在postgresql.conf中）
/*
shared_buffers = 25% 系统内存
work_mem = 64MB
maintenance_work_mem = 512MB
random_page_cost = 1.1 （SSD存储）或 4.0 （HDD存储）
effective_cache_size = 50% 系统内存
max_connections = 200
*/
```

#### Redis 缓存配置

```conf
# redis.conf - 生产环境配置

# 基本配置
bind 127.0.0.1 192.168.1.100  # 绑定特定IP
port 6379

# 安全配置
requirepass "your_strong_password"  # 设置密码
rename-command FLUSHALL ""  # 禁用危险命令
rename-command FLUSHDB ""  # 禁用危险命令
databases 1  # 只使用一个数据库

# 持久化配置
save 900 1  # 900秒内有1个修改就保存
save 300 10  # 300秒内有10个修改就保存
save 60 10000  # 60秒内有10000个修改就保存
dbfilename dump.rdb
appendonly yes  # 启用AOF持久化
appendfilename "appendonly.aof"
appendfsync everysec  # 每秒同步一次

# 内存管理
maxmemory 4gb  # 设置最大内存
maxmemory-policy allkeys-lru  # 使用LRU算法淘汰

# 性能配置
io-threads 4  # 启用多线程I/O
io-threads-do-reads yes
```

#### 生产环境配置文件

```python
# superset_config.py - 生产环境配置
import os
from datetime import timedelta

# 基础配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key')
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 
                                         'postgresql://superset:secure_password@postgres:5432/superset')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 安全配置
DEBUG = False
WTF_CSRF_ENABLED = True  # 启用CSRF保护
SESSION_COOKIE_SECURE = True  # 强制HTTPS
SESSION_COOKIE_HTTPONLY = True  # 防止XSS攻击
SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF攻击

# 启用Talisman安全头
from flask_talisman import Talisman
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    'content_security_policy': {
        'default-src': ["'self'"],
        'img-src': ["'self'", 'data:'],
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'"]
    },
    'force_https': True,
    'frame_options': 'DENY'
}

# Redis缓存配置
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://:password@redis:6379/1'),
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
}

# Celery配置（用于异步查询）
class CeleryConfig:
    broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://:password@redis:6379/2')
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://:password@redis:6379/3')
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    timezone = 'Asia/Shanghai'
    enable_utc = True
    task_track_started = True
    task_time_limit = 3600
    task_soft_time_limit = 300
    worker_prefetch_multiplier = 1
    worker_max_tasks_per_child = 1000
    worker_disable_rate_limits = True

CELERY_CONFIG = CeleryConfig()

# 异步查询配置
ENABLE_ASYNC_QUERIES = True
ASYNC_QUERIES_TRACKING = True
SQLLAB_ASYNC_TIME_LIMIT_SEC = 3600
SQLLAB_TIMEOUT = 300
SQLLAB_QUERY_COST_FORMATTERS = {
    'postgresql': lambda x: x / 1000000,
    'mysql': lambda x: x / 1000,
}
SQLLAB_MAX_ROW = 100000

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s'
LOG_FILE = '/app/logs/superset.log'
LOG_RECORD_TIMEZONE = 'Asia/Shanghai'

# Flask-Babel配置（国际化）
BABEL_DEFAULT_LOCALE = 'zh'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

# 安全认证配置
AUTH_TYPE = AUTH_DB  # 数据库认证
AUTH_USER_REGISTRATION = False  # 禁止用户自助注册
AUTH_USER_REGISTRATION_ROLE = 'Public'

# 权限管理配置
ROBOT_PERMISSIONS = [
    'can_read',
    'can_dataset_access',
    'can_dashboard_access',
    'can_slice_access',
]

# 会话管理配置
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
SESSION_REFRESH_EACH_REQUEST = True
REFRESH_JWT_ON_REFRESH = True
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

# 电子邮件配置
EMAIL_NOTIFICATIONS = False
SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = os.environ.get('SMTP_PORT', 587)
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SMTP_MAIL_FROM = os.environ.get('SMTP_MAIL_FROM', 'superset@company.com')

# 自定义主题
ENABLE_PROXY_FIX = True
ENABLE_CORS = True
CORS_OPTIONS = {
    'origins': ['https://your-company-domain.com'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization'],
    'supports_credentials': True,
}

# 自定义插件路径
PLUGINS_FOLDER = os.path.join(os.path.dirname(__file__), 'plugins')

# 自定义颜色方案
DEFAULT_COLOR_SCHEMA = 'superset'
DEFAULT_SERIES_COLORS = [
    '#0074D9', '#FF4136', '#2ECC40', '#FFDC00', '#B10DC9',
    '#FF851B', '#7FDBFF', '#85144b', '#F012BE', '#39CCCC',
    '#01FF70', '#FFDC00', '#B10DC9', '#FF851B', '#7FDBFF'
]
```

#### 生产环境部署脚本

```bash
#!/bin/bash
# deploy-superset-prod.sh

# 环境变量设置
export SECRET_KEY=$(openssl rand -hex 32)
export SQLALCHEMY_DATABASE_URI="postgresql://superset:secure_password@postgres:5432/superset"
export REDIS_URL="redis://:password@redis:6379/1"
export CELERY_BROKER_URL="redis://:password@redis:6379/2"
export CELERY_RESULT_BACKEND="redis://:password@redis:6379/3"
export SMTP_HOST="smtp.company.com"
export SMTP_PORT="587"
export SMTP_USER="smtp_user"
export SMTP_PASSWORD="smtp_password"
export SMTP_MAIL_FROM="superset@company.com"

# 创建必要的目录
mkdir -p /opt/superset/logs /opt/superset/config /opt/superset/plugins

# 安装Superset
pip install apache-superset gunicorn redis psycopg2-binary

# 复制配置文件
cp superset_config.py /opt/superset/config/
export SUPERSET_CONFIG_PATH="/opt/superset/config/superset_config.py"

# 初始化数据库
superset db upgrade

# 创建管理员用户
superset fab create-admin \
  --username admin \
  --firstname Superset \
  --lastname Admin \
  --email admin@example.com \
  --password admin123

# 初始化权限
superset init

# 创建systemd服务文件
cat > /etc/systemd/system/superset-web.service << 'EOF'
[Unit]
Description=Apache Superset Web Service
After=network.target postgresql.service redis.service

[Service]
User=superset
Group=superset
WorkingDirectory=/opt/superset
EnvironmentFile=/opt/superset/.env
ExecStart=/usr/local/bin/gunicorn \
  --workers 4 \
  --worker-class gthread \
  --threads 20 \
  --timeout 120 \
  --bind 0.0.0.0:8088 \
  --limit-request-line 0 \
  --limit-request-field_size 0 \
  --access-logfile /opt/superset/logs/access.log \
  --error-logfile /opt/superset/logs/error.log \
  --log-level info \
  superset.app:create_app()
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/superset-worker.service << 'EOF'
[Unit]
Description=Apache Superset Worker Service
After=network.target postgresql.service redis.service

[Service]
User=superset
Group=superset
WorkingDirectory=/opt/superset
EnvironmentFile=/opt/superset/.env
ExecStart=/usr/local/bin/celery \
  --app=superset.tasks.celery_app:app \
  worker \
  --pool=prefork \
  --autoscale=8,2 \
  --loglevel=INFO \
  --logfile=/opt/superset/logs/celery-worker.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 创建Celery Beat服务
cat > /etc/systemd/system/superset-beat.service << 'EOF'
[Unit]
Description=Apache Superset Beat Service
After=network.target postgresql.service redis.service

[Service]
User=superset
Group=superset
WorkingDirectory=/opt/superset
EnvironmentFile=/opt/superset/.env
ExecStart=/usr/local/bin/celery \
  --app=superset.tasks.celery_app:app \
  beat \
  --loglevel=INFO \
  --logfile=/opt/superset/logs/celery-beat.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 创建环境变量文件
cat > /opt/superset/.env << EOF
SECRET_KEY=$SECRET_KEY
SQLALCHEMY_DATABASE_URI=$SQLALCHEMY_DATABASE_URI
REDIS_URL=$REDIS_URL
CELERY_BROKER_URL=$CELERY_BROKER_URL
CELERY_RESULT_BACKEND=$CELERY_RESULT_BACKEND
SMTP_HOST=$SMTP_HOST
SMTP_PORT=$SMTP_PORT
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASSWORD
SMTP_MAIL_FROM=$SMTP_MAIL_FROM
SUPERSET_CONFIG_PATH=/opt/superset/config/superset_config.py
EOF

# 创建用户和设置权限
useradd -r -s /bin/false superset
chown -R superset:superset /opt/superset

# 启动服务
systemctl daemon-reload
systemctl start superset-web.service superset-worker.service superset-beat.service
systemctl enable superset-web.service superset-worker.service superset-beat.service

echo "Superset生产环境部署完成！"
echo "Web界面: http://服务器IP:8088"
echo "请在首次登录后修改管理员密码！"
```

## 用户故事 3: 容器化部署

### 描述
作为DevOps工程师，我希望使用容器化技术（Docker/Kubernetes）部署Superset，以实现更好的可扩展性、可移植性和管理性。

### 验收标准
- 使用Docker容器化Superset及其依赖组件
- 提供Kubernetes部署配置
- 支持水平扩展
- 包含配置管理和持久化存储
- 支持CI/CD集成

### 分步指南

#### Dockerfile

```dockerfile
# Dockerfile - 生产环境Superset
FROM apache/superset:latest

# 切换到root用户安装依赖
USER root

# 安装额外依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 切换回superset用户
USER superset

# 安装Python依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制配置文件
COPY superset_config.py /app/pythonpath/

# 环境变量
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

# 暴露端口
EXPOSE 8088

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8088/health || exit 1

# 入口点
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["superset db upgrade && superset init && gunicorn --bind 0.0.0.0:8088 --workers 4 --worker-class gthread --threads 20 --timeout 120 superset.app:create_app()"]
```

#### Docker Compose 生产配置

```yaml
# docker-compose-prod.yml
version: '3.8'

x-superset-common:
  &superset-common
  image: your-registry/superset:latest
  restart: always
  environment:
    - SECRET_KEY=${SECRET_KEY}
    - SQLALCHEMY_DATABASE_URI=postgresql://superset:${POSTGRES_PASSWORD}@db:5432/superset
    - REDIS_URL=redis://redis:6379/1
    - CELERY_BROKER_URL=redis://redis:6379/2
    - CELERY_RESULT_BACKEND=redis://redis:6379/3
    - SMTP_HOST=${SMTP_HOST}
    - SMTP_PORT=${SMTP_PORT}
    - SMTP_USER=${SMTP_USER}
    - SMTP_PASSWORD=${SMTP_PASSWORD}
    - SMTP_MAIL_FROM=${SMTP_MAIL_FROM}
  volumes:
    - superset-config:/app/pythonpath
    - superset-upload:/app/superset/static/assets

volumes:
  superset-config:
  superset-upload:
  postgres-data:
  redis-data:

services:
  # PostgreSQL数据库
  db:
    image: postgres:13
    restart: always
    environment:
      - POSTGRES_USER=superset
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=superset
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U superset -d superset"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G

  # Redis缓存
  redis:
    image: redis:6
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # Superset初始化
  superset-init:
    <<: *superset-common
    command: >
      bash -c "
        superset db upgrade && \
        superset fab create-admin \
          --username admin \
          --firstname Superset \
          --lastname Admin \
          --email admin@example.com \
          --password ${ADMIN_PASSWORD} && \
        superset init
      "
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Superset Web服务器
  superset-web:
    <<: *superset-common
    ports:
      - "8088:8088"
    command: gunicorn --bind 0.0.0.0:8088 --workers 4 --worker-class gthread --threads 20 --timeout 120 superset.app:create_app()
    depends_on:
      - db
      - redis
      - superset-init
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
      replicas: 2

  # Superset Worker
  superset-worker:
    <<: *superset-common
    command: celery --app=superset.tasks.celery_app:app worker --pool=prefork --autoscale=8,2 --loglevel=INFO
    depends_on:
      - db
      - redis
      - superset-init
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
      replicas: 3

  # Superset Beat
  superset-beat:
    <<: *superset-common
    command: celery --app=superset.tasks.celery_app:app beat --loglevel=INFO
    depends_on:
      - db
      - redis
      - superset-init
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
```

#### Kubernetes 部署配置

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: superset
  labels:
    name: superset
---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: superset-config
  namespace: superset
data:
  superset_config.py: |
    import os
    from datetime import timedelta

    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 安全配置
    DEBUG = False
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Redis缓存配置
    CACHE_CONFIG = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_KEY_PREFIX': 'superset_',
    }

    # Celery配置
    class CeleryConfig:
        broker_url = os.environ.get('CELERY_BROKER_URL')
        result_backend = os.environ.get('CELERY_RESULT_BACKEND')
        task_serializer = 'json'
        result_serializer = 'json'
        accept_content = ['json']
        timezone = 'Asia/Shanghai'
        enable_utc = True
        task_track_started = True
        task_time_limit = 3600

    CELERY_CONFIG = CeleryConfig()

    # 异步查询配置
    ENABLE_ASYNC_QUERIES = True
    ASYNC_QUERIES_TRACKING = True

    # 国际化配置
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'
---
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: superset-secrets
  namespace: superset
type: Opaque
data:
  # 注意：这些值需要使用base64编码
  secret-key: <base64-encoded-secret-key>
  postgres-password: <base64-encoded-password>
  redis-password: <base64-encoded-password>
  admin-password: <base64-encoded-password>
  smtp-user: <base64-encoded-user>
  smtp-password: <base64-encoded-password>
---
# kubernetes/deployment-web.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: superset-web
  namespace: superset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: superset
      component: web
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: superset
        component: web
    spec:
      initContainers:
        - name: wait-for-postgres
          image: busybox:1.32
          command: ['sh', '-c', 'until nc -z postgres 5432; do echo "等待PostgreSQL..."; sleep 5; done;']
        - name: wait-for-redis
          image: busybox:1.32
          command: ['sh', '-c', 'until nc -z redis 6379; do echo "等待Redis..."; sleep 5; done;']
      containers:
        - name: superset-web
          image: your-registry/superset:latest
          ports:
            - containerPort: 8088
          env:
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: secret-key
            - name: SQLALCHEMY_DATABASE_URI
              value: postgresql://superset:$(POSTGRES_PASSWORD)@postgres:5432/superset
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: postgres-password
            - name: REDIS_URL
              value: redis://:$(REDIS_PASSWORD)@redis:6379/1
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: redis-password
            - name: CELERY_BROKER_URL
              value: redis://:$(REDIS_PASSWORD)@redis:6379/2
            - name: CELERY_RESULT_BACKEND
              value: redis://:$(REDIS_PASSWORD)@redis:6379/3
          resources:
            requests:
              cpu: 1
              memory: 2Gi
            limits:
              cpu: 2
              memory: 4Gi
          volumeMounts:
            - name: superset-config
              mountPath: /app/pythonpath/superset_config.py
              subPath: superset_config.py
            - name: superset-upload
              mountPath: /app/superset/static/assets
          livenessProbe:
            httpGet:
              path: /health
              port: 8088
            initialDelaySeconds: 60
            periodSeconds: 30
            timeoutSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8088
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
      volumes:
        - name: superset-config
          configMap:
            name: superset-config
        - name: superset-upload
          persistentVolumeClaim:
            claimName: superset-upload-pvc
---
# kubernetes/service-web.yaml
apiVersion: v1
kind: Service
metadata:
  name: superset-web
  namespace: superset
spec:
  selector:
    app: superset
    component: web
  ports:
    - port: 8088
      targetPort: 8088
  type: ClusterIP
---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: superset-ingress
  namespace: superset
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/proxy-body-size: 50m
spec:
  tls:
    - hosts:
        - superset.your-company.com
      secretName: superset-tls
  rules:
    - host: superset.your-company.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: superset-web
                port:
                  number: 8088
---
# kubernetes/deployment-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: superset-worker
  namespace: superset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: superset
      component: worker
  template:
    metadata:
      labels:
        app: superset
        component: worker
    spec:
      initContainers:
        - name: wait-for-postgres
          image: busybox:1.32
          command: ['sh', '-c', 'until nc -z postgres 5432; do echo "等待PostgreSQL..."; sleep 5; done;']
        - name: wait-for-redis
          image: busybox:1.32
          command: ['sh', '-c', 'until nc -z redis 6379; do echo "等待Redis..."; sleep 5; done;']
      containers:
        - name: superset-worker
          image: your-registry/superset:latest
          command: ["celery"]
          args: ["--app=superset.tasks.celery_app:app", "worker", "--pool=prefork", "--autoscale=8,2", "--loglevel=INFO"]
          env:
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: secret-key
            - name: SQLALCHEMY_DATABASE_URI
              value: postgresql://superset:$(POSTGRES_PASSWORD)@postgres:5432/superset
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: postgres-password
            - name: REDIS_URL
              value: redis://:$(REDIS_PASSWORD)@redis:6379/1
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: redis-password
            - name: CELERY_BROKER_URL
              value: redis://:$(REDIS_PASSWORD)@redis:6379/2
            - name: CELERY_RESULT_BACKEND
              value: redis://:$(REDIS_PASSWORD)@redis:6379/3
          resources:
            requests:
              cpu: 0.5
              memory: 1Gi
            limits:
              cpu: 1
              memory: 2Gi
          volumeMounts:
            - name: superset-config
              mountPath: /app/pythonpath/superset_config.py
              subPath: superset_config.py
            - name: superset-upload
              mountPath: /app/superset/static/assets
      volumes:
        - name: superset-config
          configMap:
            name: superset-config
        - name: superset-upload
          persistentVolumeClaim:
            claimName: superset-upload-pvc
---
# kubernetes/deployment-beat.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: superset-beat
  namespace: superset
spec:
  replicas: 1
  selector:
    matchLabels:
      app: superset
      component: beat
  template:
    metadata:
      labels:
        app: superset
        component: beat
    spec:
      initContainers:
        - name: wait-for-postgres
          image: busybox:1.32
          command: ['sh', '-c', 'until nc -z postgres 5432; do echo "等待PostgreSQL..."; sleep 5; done;']
        - name: wait-for-redis
          image: busybox:1.32
          command: ['sh', '-c', 'until nc -z redis 6379; do echo "等待Redis..."; sleep 5; done;']
      containers:
        - name: superset-beat
          image: your-registry/superset:latest
          command: ["celery"]
          args: ["--app=superset.tasks.celery_app:app", "beat", "--loglevel=INFO"]
          env:
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: secret-key
            - name: SQLALCHEMY_DATABASE_URI
              value: postgresql://superset:$(POSTGRES_PASSWORD)@postgres:5432/superset
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: postgres-password
            - name: REDIS_URL
              value: redis://:$(REDIS_PASSWORD)@redis:6379/1
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: superset-secrets
                  key: redis-password
            - name: CELERY_BROKER_URL
              value: redis://:$(REDIS_PASSWORD)@redis:6379/2
            - name: CELERY_RESULT_BACKEND
              value: redis://:$(REDIS_PASSWORD)@redis:6379/3
          resources:
            requests:
              cpu: 0.5
              memory: 512Mi
            limits:
              cpu: 1
              memory: 1Gi
          volumeMounts:
            - name: superset-config
              mountPath: /app/pythonpath/superset_config.py
              subPath: superset_config.py
            - name: superset-upload
              mountPath: /app/superset/static/assets
      volumes:
        - name: superset-config
          configMap:
            name: superset-config
        - name: superset-upload
          persistentVolumeClaim:
            claimName: superset-upload-pvc
---
# kubernetes/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: superset-upload-pvc
  namespace: superset
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: managed-nfs-storage
```

## 用户故事 4: 高可用架构设计

### 描述
作为架构师/系统管理员，我希望设计一个高可用的Superset架构，以确保服务的连续可用性和可靠性，满足企业级应用需求。

### 验收标准
- 所有关键组件实现冗余部署
- 支持自动故障转移
- 实现负载均衡
- 提供数据备份和恢复机制
- 确保系统在节点故障时仍然可用

### 分步指南

#### 高可用架构组件

1. **前端层**
   - 多个Superset Web服务器实例
   - 负载均衡器（如Nginx、HAProxy或云提供商的负载均衡服务）
   - SSL终止

2. **应用层**
   - 多实例Superset Web服务器
   - 多实例Superset Worker
   - 单一Superset Beat实例（可配置备用）

3. **数据层**
   - PostgreSQL主从复制
   - Redis集群或哨兵模式
   - 共享文件系统（如NFS、EFS、S3等）

4. **监控与告警**
   - Prometheus + Grafana监控
   - 健康检查
   - 自动告警

#### PostgreSQL 主从复制配置

```bash
#!/bin/bash
# setup-postgres-replication.sh

# 主库配置
MASTER_IP="192.168.1.10"
SLAVE_IP="192.168.1.11"
REP_USER="repl_user"
REP_PASSWORD="repl_password"

# 在主库上创建复制用户
ssh postgres@$MASTER_IP "psql -c \"CREATE ROLE $REP_USER WITH REPLICATION LOGIN PASSWORD '$REP_PASSWORD';\""

# 配置主库
cat << EOF | ssh postgres@$MASTER_IP "cat > /etc/postgresql/13/main/postgresql.conf"
listen_addresses = '*'
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
effective_cache_size = 2GB
shared_buffers = 1GB
work_mem = 64MB
maintenance_work_mem = 512MB
EOF

# 配置pg_hba.conf
cat << EOF | ssh postgres@$MASTER_IP "cat >> /etc/postgresql/13/main/pg_hba.conf"
# 允许从库连接
host    replication     $REP_USER     $SLAVE_IP/32            md5
EOF

# 重启主库
ssh postgres@$MASTER_IP "sudo systemctl restart postgresql"

# 在从库上停止PostgreSQL
ssh postgres@$SLAVE_IP "sudo systemctl stop postgresql"

# 删除从库数据目录内容
ssh postgres@$SLAVE_IP "sudo rm -rf /var/lib/postgresql/13/main/*"

# 从主库复制基础备份
ssh postgres@$SLAVE_IP "pg_basebackup -h $MASTER_IP -U $REP_USER -D /var/lib/postgresql/13/main -P -v -R"

# 配置从库
cat << EOF | ssh postgres@$SLAVE_IP "cat > /etc/postgresql/13/main/postgresql.conf"
listen_addresses = '*'
wal_level = replica
max_wal_senders = 10
hot_standby = on
effective_cache_size = 2GB
shared_buffers = 1GB
work_mem = 64MB
maintenance_work_mem = 512MB
EOF

# 重启从库
ssh postgres@$SLAVE_IP "sudo systemctl start postgresql"

# 验证复制状态
echo "验证主库复制状态:"
ssh postgres@$MASTER_IP "psql -c \"SELECT * FROM pg_stat_replication;\""

echo "验证从库复制状态:"
ssh postgres@$SLAVE_IP "psql -c \"SELECT * FROM pg_stat_wal_receiver;\""
echo "PostgreSQL主从复制配置完成！"
```

#### Redis 哨兵模式配置

```bash
#!/bin/bash
# setup-redis-sentinel.sh

# Redis节点配置
MASTER_IP="192.168.1.12"
SLAVE1_IP="192.168.1.13"
SLAVE2_IP="192.168.1.14"
SENTINEL1_IP="192.168.1.12"
SENTINEL2_IP="192.168.1.13"
SENTINEL3_IP="192.168.1.14"
REDIS_PASSWORD="strong_password"
MASTER_NAME="mymaster"
QUORUM=2

# 配置主Redis
cat << EOF | ssh admin@$MASTER_IP "sudo tee /etc/redis/redis.conf"
port 6379
bind 0.0.0.0
protected-mode yes
requirepass $REDIS_PASSWORD
masterauth $REDIS_PASSWORD
dir /var/lib/redis
dbfilename dump.rdb
aof yes
appendonly yes
appendfilename "appendonly.aof"
maxmemory 2gb
maxmemory-policy allkeys-lru
EOF

# 配置从Redis 1
cat << EOF | ssh admin@$SLAVE1_IP "sudo tee /etc/redis/redis.conf"
port 6379
bind 0.0.0.0
protected-mode yes
requirepass $REDIS_PASSWORD
masterauth $REDIS_PASSWORD
dir /var/lib/redis
dbfilename dump.rdb
aof yes
appendonly yes
maxmemory 2gb
maxmemory-policy allkeys-lru
replicaof $MASTER_IP 6379
EOF

# 配置从Redis 2
cat << EOF | ssh admin@$SLAVE2_IP "sudo tee /etc/redis/redis.conf"
port 6379
bind 0.0.0.0
protected-mode yes
requirepass $REDIS_PASSWORD
masterauth $REDIS_PASSWORD
dir /var/lib/redis
dbfilename dump.rdb
aof yes
appendonly yes
maxmemory 2gb
maxmemory-policy allkeys-lru
replicaof $MASTER_IP 6379
EOF

# 配置Redis Sentinel 1
cat << EOF | ssh admin@$SENTINEL1_IP "sudo tee /etc/redis/sentinel.conf"
port 26379
bind 0.0.0.0
sentinel monitor $MASTER_NAME $MASTER_IP 6379 $QUORUM
sentinel auth-pass $MASTER_NAME $REDIS_PASSWORD
sentinel down-after-milliseconds $MASTER_NAME 5000
sentinel failover-timeout $MASTER_NAME 60000
sentinel parallel-syncs $MASTER_NAME 1
sentinel deny-scripts-reconfig yes
logfile /var/log/redis/sentinel.log
dir /tmp
EOF

# 配置Redis Sentinel 2
cat << EOF | ssh admin@$SENTINEL2_IP "sudo tee /etc/redis/sentinel.conf"
port 26379
bind 0.0.0.0
sentinel monitor $MASTER_NAME $MASTER_IP 6379 $QUORUM
sentinel auth-pass $MASTER_NAME $REDIS_PASSWORD
sentinel down-after-milliseconds $MASTER_NAME 5000
sentinel failover-timeout $MASTER_NAME 60000
sentinel parallel-syncs $MASTER_NAME 1
sentinel deny-scripts-reconfig yes
logfile /var/log/redis/sentinel.log
dir /tmp
EOF

# 配置Redis Sentinel 3
cat << EOF | ssh admin@$SENTINEL3_IP "sudo tee /etc/redis/sentinel.conf"
port 26379
bind 0.0.0.0
sentinel monitor $MASTER_NAME $MASTER_IP 6379 $QUORUM
sentinel auth-pass $MASTER_NAME $REDIS_PASSWORD
sentinel down-after-milliseconds $MASTER_NAME 5000
sentinel failover-timeout $MASTER_NAME 60000
sentinel parallel-syncs $MASTER_NAME 1
sentinel deny-scripts-reconfig yes
logfile /var/log/redis/sentinel.log
dir /tmp
EOF

# 重启所有Redis服务
for IP in $MASTER_IP $SLAVE1_IP $SLAVE2_IP; do
  ssh admin@$IP "sudo systemctl restart redis"
done

# 启动所有Sentinel服务
for IP in $SENTINEL1_IP $SENTINEL2_IP $SENTINEL3_IP; do
  ssh admin@$IP "sudo systemctl restart redis-sentinel"
done

echo "验证主Redis状态:"
ssh admin@$MASTER_IP "redis-cli -a $REDIS_PASSWORD info replication"

echo "验证Sentinel状态:"
ssh admin@$SENTINEL1_IP "redis-cli -p 26379 sentinel master $MASTER_NAME"

echo "Redis哨兵模式配置完成！"
echo "连接字符串格式: redis://:$REDIS_PASSWORD@$SENTINEL1_IP:26379,$SENTINEL2_IP:26379,$SENTINEL3_IP:26379?master=$MASTER_NAME"
```

#### 负载均衡器配置

```nginx
# nginx.conf
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 请求缓冲区
    client_body_buffer_size 128k;
    client_max_body_size 50m;
    
    # 日志配置
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # 负载均衡池
    upstream superset_web {
        # 使用IP哈希保持会话粘性
        ip_hash;
        
        # 添加多个Superset Web服务器实例
        server 192.168.1.20:8088 max_fails=3 fail_timeout=30s;
        server 192.168.1.21:8088 max_fails=3 fail_timeout=30s;
        server 192.168.1.22:8088 max_fails=3 fail_timeout=30s;
        
        # 健康检查
        # 使用NGINX Plus或第三方模块实现更复杂的健康检查
    }
    
    # 主服务器配置
    server {
        listen 80;
        server_name superset.your-company.com;
        
        # 重定向到HTTPS
        return 301 https://$host$request_uri;
    }
    
    # HTTPS服务器配置
    server {
        listen 443 ssl;
        server_name superset.your-company.com;
        
        # SSL证书
        ssl_certificate /etc/nginx/ssl/superset.crt;
        ssl_certificate_key /etc/nginx/ssl/superset.key;
        
        # 代理配置
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 300s;  # 增加超时以支持长时间运行的查询
        proxy_send_timeout 300s;
        
        # 根位置
        location / {
            proxy_pass http://superset_web;
        }
        
        # 健康检查端点
        location /health {
            proxy_pass http://superset_web/health;
            access_log off;
        }
        
        # 静态文件缓存
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            proxy_pass http://superset_web;
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }
    }
}
```

#### 高可用监控配置

```yaml
# prometheus-config.yaml
# Prometheus配置用于监控高可用Superset集群

global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  # 监控Superset Web服务器
  - job_name: 'superset-web'
    metrics_path: '/admin/metrics'
    scrape_interval: 10s
    static_configs:
      - targets: ['192.168.1.20:8088', '192.168.1.21:8088', '192.168.1.22:8088']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '(.*)'  # 保留原始IP:端口作为实例标签

  # 监控Superset Worker
  - job_name: 'superset-worker'
    metrics_path: '/admin/metrics'
    scrape_interval: 10s
    static_configs:
      - targets: ['192.168.1.23:8088', '192.168.1.24:8088', '192.168.1.25:8088']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '(.*)'  # 保留原始IP:端口作为实例标签

  # 监控PostgreSQL数据库
  - job_name: 'postgres'
    static_configs:
      - targets: ['192.168.1.10:9187', '192.168.1.11:9187']

  # 监控Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['192.168.1.12:9121', '192.168.1.13:9121', '192.168.1.14:9121']

  # 监控节点
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['192.168.1.10:9100', '192.168.1.11:9100', '192.168.1.12:9100', 
                  '192.168.1.13:9100', '192.168.1.14:9100', '192.168.1.20:9100', 
                  '192.168.1.21:9100', '192.168.1.22:9100', '192.168.1.23:9100', 
                  '192.168.1.24:9100', '192.168.1.25:9100']
```

```yaml
# alert_rules.yml
# 高可用Superset集群告警规则

groups:
- name: superset_alerts
  rules:
  # Web服务器健康检查
  - alert: SupersetWebServerDown
    expr: up{job="superset-web"} == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Superset Web服务器宕机"
      description: "Superset Web服务器 {{ $labels.instance }} 已宕机超过2分钟"

  # Worker健康检查
  - alert: SupersetWorkerDown
    expr: up{job="superset-worker"} == 0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Superset Worker宕机"
      description: "Superset Worker {{ $labels.instance }} 已宕机超过2分钟"

  # 数据库连接问题
  - alert: SupersetDatabaseConnectionIssues
    expr: sum(rate(superset_db_connection_errors_total[5m])) > 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Superset数据库连接问题"
      description: "检测到数据库连接错误"

  # 缓存连接问题
  - alert: SupersetCacheConnectionIssues
    expr: sum(rate(superset_cache_errors_total[5m])) > 0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Superset缓存连接问题"
      description: "检测到缓存连接错误"

  # 响应时间过长
  - alert: SupersetHighResponseTime
    expr: histogram_quantile(0.95, sum(rate(superset_request_duration_seconds_bucket[5m])) by (le)) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Superset响应时间过长"
      description: "95%的请求响应时间超过5秒"

  # CPU使用率过高
  - alert: SupersetHighCPUUsage
    expr: (sum(rate(process_cpu_seconds_total{job=~"superset-.*"}[5m])) by (instance) / on(instance) count(node_cpu_seconds_total{mode="idle"}) by (instance)) * 100 > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Superset CPU使用率过高"
      description: "实例 {{ $labels.instance }} 的CPU使用率超过80%"

  # 内存使用率过高
  - alert: SupersetHighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Superset内存使用率过高"
      description: "节点 {{ $labels.instance }} 的内存使用率超过85%"

  # PostgreSQL复制延迟
  - alert: PostgresReplicationLag
    expr: pg_stat_replication_replay_lag > 30
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "PostgreSQL复制延迟"
      description: "PostgreSQL复制延迟超过30秒"

  # Redis Sentinel故障
  - alert: RedisSentinelDown
    expr: redis_sentinel_masters > 0 and on() redis_sentinel_up < 3
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Redis Sentinel故障"
      description: "Redis Sentinel实例数量不足，当前可用: {{ $value }}"
```

## 参考文档

1. [Apache Superset 官方部署文档](https://superset.apache.org/docs/installation/deployment)
2. [PostgreSQL 高可用最佳实践](https://www.postgresql.org/docs/current/hot-standby.html)
3. [Redis 哨兵模式文档](https://redis.io/topics/sentinel)
4. [NGINX 负载均衡配置](https://nginx.org/en/docs/http/load_balancing.html)
5. [Kubernetes 部署最佳实践](https://kubernetes.io/docs/concepts/cluster-administration/best-practices/)
6. [Docker Compose 生产环境配置](https://docs.docker.com/compose/production/)
7. [Prometheus 监控指南](https://prometheus.io/docs/introduction/overview/)
8. [Grafana 仪表板配置](https://grafana.com/docs/grafana/latest/dashboards/)
9. [Python 应用性能优化](https://docs.python.org/3/library/profile.html)
10. [安全配置最佳实践](https://owasp.org/www-project-top-ten/)