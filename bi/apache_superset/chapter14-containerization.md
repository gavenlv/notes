# 第十四章：容器化部署

## 14.1 容器化部署概述

随着容器技术的快速发展，Docker 已成为现代应用部署的主流方式。Apache Superset 也提供了官方的 Docker 镜像，使得部署和管理变得更加简单和标准化。容器化部署不仅简化了部署流程，还提供了更好的可移植性、一致性和资源隔离。

### 容器化的优势

1. **环境一致性**：消除"在我机器上能运行"的问题
2. **快速部署**：通过镜像快速启动和扩展服务
3. **资源隔离**：每个容器独立运行，互不干扰
4. **易于扩展**：支持水平扩展和负载均衡
5. **版本管理**：通过镜像版本管理应用版本
6. **简化运维**：统一的部署和管理方式

### 容器化部署架构

在容器化部署中，Apache Superset 通常包含以下组件：

- **Superset Web Server**：提供 Web 界面和 API 服务
- **Superset Worker**：处理异步任务和定时任务
- **Superset Beat**：调度定时任务
- **Redis**：缓存和消息队列
- **数据库**：存储元数据（MySQL/PostgreSQL）
- **负载均衡器**（可选）：分发请求到多个 Web 服务器实例

## 14.2 官方 Docker 镜像使用

### 获取官方镜像

```bash
# 拉取最新版本的 Superset 镜像
docker pull apache/superset:latest

# 拉取特定版本的 Superset 镜像
docker pull apache/superset:2.1.0

# 查看可用的标签
docker search apache/superset
```

### 基本容器运行

```bash
# 运行简单的 Superset 容器
docker run -d \
  --name superset \
  -p 8088:8088 \
  apache/superset:latest

# 访问 http://localhost:8088 查看 Superset 界面
```

### 环境变量配置

```bash
# 使用环境变量配置 Superset
docker run -d \
  --name superset \
  -p 8088:8088 \
  -e "SUPERSET_SECRET_KEY=your-secret-key" \
  -e "SQLALCHEMY_DATABASE_URI=postgresql://user:pass@db:5432/superset" \
  -e "REDIS_HOST=redis" \
  -e "REDIS_PORT=6379" \
  apache/superset:latest
```

### 常用环境变量

```bash
# 核心配置
SUPERSET_SECRET_KEY=your-very-secret-key-here
SQLALCHEMY_DATABASE_URI=postgresql://superset:superset@db:5432/superset
REDIS_HOST=redis
REDIS_PORT=6379

# 管理员账户
ADMIN_USERNAME=admin
ADMIN_FIRST_NAME=Admin
ADMIN_LAST_NAME=User
ADMIN_EMAIL=admin@superset.com
ADMIN_PWD=admin

# 其他配置
MAPBOX_API_KEY=your-mapbox-api-key
GOOGLE_API_KEY=your-google-api-key
```

## 14.3 Docker Compose 部署

### 基础 Docker Compose 文件

```yaml
# docker-compose.yml
version: '3.7'

services:
  redis:
    image: redis:7
    container_name: superset_cache
    restart: unless-stopped
    volumes:
      - redis_data:/data

  db:
    image: postgres:15
    container_name: superset_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: superset
      POSTGRES_PASSWORD: superset
      POSTGRES_DB: superset
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d

  superset:
    image: apache/superset:latest
    container_name: superset_app
    restart: unless-stopped
    depends_on:
      - db
      - redis
    environment:
      SUPERSET_SECRET_KEY: your-very-secret-key-here
      SQLALCHEMY_DATABASE_URI: postgresql://superset:superset@db:5432/superset
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "8088:8088"
    volumes:
      - superset_home:/app/superset_home

volumes:
  db_data:
  redis_data:
  superset_home:
```

### 完整的生产级 Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.7'

services:
  redis:
    image: redis:7-alpine
    container_name: superset_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - superset_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: superset_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-superset}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-superset}
      POSTGRES_DB: ${POSTGRES_DB:-superset}
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d
    networks:
      - superset_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-superset}"]
      interval: 10s
      timeout: 5s
      retries: 5

  superset-web:
    image: apache/superset:latest
    container_name: superset_web
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      SUPERSET_SECRET_KEY: ${SUPERSET_SECRET_KEY:-your-very-secret-key-here}
      SQLALCHEMY_DATABASE_URI: postgresql://${POSTGRES_USER:-superset}:${POSTGRES_PASSWORD:-superset}@db:5432/${POSTGRES_DB:-superset}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      # 管理员账户配置
      ADMIN_USERNAME: ${ADMIN_USERNAME:-admin}
      ADMIN_FIRST_NAME: ${ADMIN_FIRST_NAME:-Superset}
      ADMIN_LAST_NAME: ${ADMIN_LAST_NAME:-Admin}
      ADMIN_EMAIL: ${ADMIN_EMAIL:-admin@superset.org}
      ADMIN_PWD: ${ADMIN_PWD:-admin}
    ports:
      - "8088:8088"
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  superset-worker:
    image: apache/superset:latest
    container_name: superset_worker
    restart: unless-stopped
    depends_on:
      superset-web:
        condition: service_started
    environment:
      SUPERSET_SECRET_KEY: ${SUPERSET_SECRET_KEY:-your-very-secret-key-here}
      SQLALCHEMY_DATABASE_URI: postgresql://${POSTGRES_USER:-superset}:${POSTGRES_PASSWORD:-superset}@db:5432/${POSTGRES_DB:-superset}
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    command: celery --app=superset.tasks.celery_app:app worker
    healthcheck:
      test: ["CMD", "celery", "-A", "superset.tasks.celery_app:app", "inspect", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  superset-beat:
    image: apache/superset:latest
    container_name: superset_beat
    restart: unless-stopped
    depends_on:
      superset-worker:
        condition: service_started
    environment:
      SUPERSET_SECRET_KEY: ${SUPERSET_SECRET_KEY:-your-very-secret-key-here}
      SQLALCHEMY_DATABASE_URI: postgresql://${POSTGRES_USER:-superset}:${POSTGRES_PASSWORD:-superset}@db:5432/${POSTGRES_DB:-superset}
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    command: celery --app=superset.tasks.celery_app:app beat --pidfile /tmp/celerybeat.pid

networks:
  superset_network:
    driver: bridge

volumes:
  db_data:
  redis_data:
  superset_home:
```

### 环境变量文件

```bash
# .env
# 数据库配置
POSTGRES_USER=superset
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=superset

# Superset 配置
SUPERSET_SECRET_KEY=your-very-long-and-secure-secret-key-here
ADMIN_USERNAME=admin
ADMIN_FIRST_NAME=Admin
ADMIN_LAST_NAME=User
ADMIN_EMAIL=admin@example.com
ADMIN_PWD=your_admin_password

# 可选配置
MAPBOX_API_KEY=your_mapbox_api_key
GOOGLE_API_KEY=your_google_api_key
```

## 14.4 自定义配置

### 自定义配置文件

```python
# superset_config.py
import os

# 基本配置
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'your-fallback-secret-key')
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'postgresql://superset:superset@db:5432/superset'
)

# Redis 配置
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

# 应用配置
ROW_LIMIT = 10000
SUPERSET_WORKERS = 4
SUPERSET_WEBSERVER_TIMEOUT = 300

# 图表配置
DEFAULT_RELATIVE_START_TIME = '-7 days'
DEFAULT_RELATIVE_END_TIME = 'now'

# 安全配置
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 7  # 7 days

# 缓存配置
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 1,
    'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
}

# Celery 配置
class CeleryConfig:
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    imports = ('superset.sql_lab', 'superset.tasks')
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    worker_log_level = 'DEBUG'
    worker_prefetch_multiplier = 10
    task_acks_late = True
    task_routes = {
        'queries': {'queue': 'queries'},
        'reports.scheduler': {'queue': 'reports'},
        'reports.execute': {'queue': 'reports'}
    }

CELERY_CONFIG = CeleryConfig

# 特性标志
FEATURE_FLAGS = {
    'ALERT_REPORTS': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'VERSIONED_EXPORT': True,
    'TAGGING_SYSTEM': True
}

# UI 配置
APP_NAME = 'My Superset'
APP_ICON = '/static/assets/images/superset-logo-horiz.png'

# 主题配置
THEME = 'light'  # 或 'dark'
```

### 自定义启动脚本

```bash
#!/bin/bash
# docker-init.sh

# 等待数据库就绪
echo "Waiting for database to be ready..."
until pg_isready -h db -p 5432 -U superset; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up - continuing"

# 初始化数据库
echo "Initializing database..."
superset db upgrade

# 创建默认角色和权限
echo "Creating default roles and permissions..."
superset init

# 创建管理员账户
echo "Creating admin user..."
superset fab create-admin \
  --username ${ADMIN_USERNAME:-admin} \
  --firstname ${ADMIN_FIRST_NAME:-Superset} \
  --lastname ${ADMIN_LAST_NAME:-Admin} \
  --email ${ADMIN_EMAIL:-admin@superset.org} \
  --password ${ADMIN_PWD:-admin}

echo "Initialization completed!"
```

## 14.5 多实例部署

### 负载均衡配置

```yaml
# docker-compose.with-loadbalancer.yml
version: '3.7'

services:
  redis:
    image: redis:7-alpine
    container_name: superset_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - superset_network

  db:
    image: postgres:15-alpine
    container_name: superset_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: superset
      POSTGRES_PASSWORD: superset
      POSTGRES_DB: superset
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - superset_network

  superset-web-1:
    image: apache/superset:latest
    container_name: superset_web_1
    restart: unless-stopped
    depends_on:
      - db
      - redis
    environment:
      SUPERSET_SECRET_KEY: your-very-secret-key-here
      SQLALCHEMY_DATABASE_URI: postgresql://superset:superset@db:5432/superset
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  superset-web-2:
    image: apache/superset:latest
    container_name: superset_web_2
    restart: unless-stopped
    depends_on:
      - db
      - redis
    environment:
      SUPERSET_SECRET_KEY: your-very-secret-key-here
      SQLALCHEMY_DATABASE_URI: postgresql://superset:superset@db:5432/superset
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  superset-worker:
    image: apache/superset:latest
    container_name: superset_worker
    restart: unless-stopped
    depends_on:
      - superset-web-1
    environment:
      SUPERSET_SECRET_KEY: your-very-secret-key-here
      SQLALCHEMY_DATABASE_URI: postgresql://superset:superset@db:5432/superset
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    command: celery --app=superset.tasks.celery_app:app worker

  superset-beat:
    image: apache/superset:latest
    container_name: superset_beat
    restart: unless-stopped
    depends_on:
      - superset-worker
    environment:
      SUPERSET_SECRET_KEY: your-very-secret-key-here
      SQLALCHEMY_DATABASE_URI: postgresql://superset:superset@db:5432/superset
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    command: celery --app=superset.tasks.celery_app:app beat --pidfile /tmp/celerybeat.pid

  nginx:
    image: nginx:alpine
    container_name: superset_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - superset-web-1
      - superset-web-2
    networks:
      - superset_network

networks:
  superset_network:
    driver: bridge

volumes:
  db_data:
  redis_data:
  superset_home:
```

### Nginx 配置

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream superset_backend {
        server superset-web-1:8088;
        server superset-web-2:8088;
    }

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS 服务器
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL 配置
        ssl_certificate /etc/nginx/ssl/your-cert.pem;
        ssl_certificate_key /etc/nginx/ssl/your-key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        location / {
            proxy_pass http://superset_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # 健康检查端点
        location /health {
            access_log off;
            proxy_pass http://superset_backend;
        }
    }
}
```

## 14.6 持久化存储

### 数据卷管理

```yaml
# docker-compose.with-volumes.yml
version: '3.7'

services:
  redis:
    image: redis:7-alpine
    container_name: superset_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - /data/superset/redis:/data
    networks:
      - superset_network

  db:
    image: postgres:15-alpine
    container_name: superset_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: superset
      POSTGRES_PASSWORD: superset
      POSTGRES_DB: superset
    volumes:
      - /data/superset/postgres:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d
    networks:
      - superset_network

  superset:
    image: apache/superset:latest
    container_name: superset_app
    restart: unless-stopped
    depends_on:
      - db
      - redis
    environment:
      SUPERSET_SECRET_KEY: your-very-secret-key-here
      SQLALCHEMY_DATABASE_URI: postgresql://superset:superset@db:5432/superset
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "8088:8088"
    volumes:
      - /data/superset/home:/app/superset_home
      - /data/superset/config:/app/config
      - /data/superset/logs:/app/superset_home/log
      - /etc/localtime:/etc/localtime:ro
    networks:
      - superset_network

networks:
  superset_network:
    driver: bridge
```

### 备份和恢复脚本

```bash
#!/bin/bash
# backup-docker-volumes.sh

# 配置变量
BACKUP_DIR="/backup/superset"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_PROJECT="superset"

# 创建备份目录
mkdir -p ${BACKUP_DIR}/${DATE}

# 备份数据库卷
echo "Backing up database volume..."
docker run --rm \
  -v superset_db_data:/source \
  -v ${BACKUP_DIR}/${DATE}:/backup \
  alpine tar czf /backup/db_data.tar.gz -C /source .

# 备份 Redis 卷
echo "Backing up Redis volume..."
docker run --rm \
  -v superset_redis_data:/source \
  -v ${BACKUP_DIR}/${DATE}:/backup \
  alpine tar czf /backup/redis_data.tar.gz -C /source .

# 备份 Superset 主目录
echo "Backing up Superset home volume..."
docker run --rm \
  -v superset_home:/source \
  -v ${BACKUP_DIR}/${DATE}:/backup \
  alpine tar czf /backup/superset_home.tar.gz -C /source .

echo "Backup completed: ${BACKUP_DIR}/${DATE}"

# 删除7天前的备份
find ${BACKUP_DIR} -mindepth 1 -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;
```

```bash
#!/bin/bash
# restore-docker-volumes.sh

# 配置变量
BACKUP_DIR="/backup/superset"
BACKUP_DATE=$1  # 从命令行参数获取备份日期

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    ls -la ${BACKUP_DIR}
    exit 1
fi

if [ ! -d "${BACKUP_DIR}/${BACKUP_DATE}" ]; then
    echo "Backup not found: ${BACKUP_DIR}/${BACKUP_DATE}"
    exit 1
fi

# 停止所有服务
echo "Stopping services..."
docker-compose down

# 恢复数据库卷
echo "Restoring database volume..."
docker run --rm \
  -v superset_db_data:/target \
  -v ${BACKUP_DIR}/${BACKUP_DATE}:/backup \
  alpine sh -c "cd /target && rm -rf * && tar xzf /backup/db_data.tar.gz"

# 恢复 Redis 卷
echo "Restoring Redis volume..."
docker run --rm \
  -v superset_redis_data:/target \
  -v ${BACKUP_DIR}/${BACKUP_DATE}:/backup \
  alpine sh -c "cd /target && rm -rf * && tar xzf /backup/redis_data.tar.gz"

# 恢复 Superset 主目录
echo "Restoring Superset home volume..."
docker run --rm \
  -v superset_home:/target \
  -v ${BACKUP_DIR}/${BACKUP_DATE}:/backup \
  alpine sh -c "cd /target && rm -rf * && tar xzf /backup/superset_home.tar.gz"

# 启动服务
echo "Starting services..."
docker-compose up -d

echo "Restore completed from ${BACKUP_DIR}/${BACKUP_DATE}"
```

## 14.7 监控和日志

### 容器监控配置

```yaml
# docker-compose.with-monitoring.yml
version: '3.7'

services:
  redis:
    image: redis:7-alpine
    container_name: superset_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - superset_network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:15-alpine
    container_name: superset_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: superset
      POSTGRES_PASSWORD: superset
      POSTGRES_DB: superset
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - superset_network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  superset:
    image: apache/superset:latest
    container_name: superset_app
    restart: unless-stopped
    depends_on:
      - db
      - redis
    environment:
      SUPERSET_SECRET_KEY: your-very-secret-key-here
      SQLALCHEMY_DATABASE_URI: postgresql://superset:superset@db:5432/superset
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "8088:8088"
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: superset_prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - superset_network

  grafana:
    image: grafana/grafana:latest
    container_name: superset_grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - superset_network
    depends_on:
      - prometheus

networks:
  superset_network:
    driver: bridge

volumes:
  db_data:
  redis_data:
  superset_home:
  prometheus_data:
  grafana_data:
```

### Prometheus 配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'superset'
    static_configs:
      - targets: ['superset:8088']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "superset_rules.yml"
```

## 14.8 安全加固

### 网络安全配置

```yaml
# docker-compose.secure.yml
version: '3.7'

services:
  redis:
    image: redis:7-alpine
    container_name: superset_redis
    restart: unless-stopped
    command: >
      redis-server
      --appendonly yes
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      superset_internal:
        aliases:
          - redis
    expose:
      - "6379"

  db:
    image: postgres:15-alpine
    container_name: superset_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256 --auth-local=scram-sha-256"
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d
    networks:
      superset_internal:
        aliases:
          - db
    expose:
      - "5432"

  superset:
    image: apache/superset:latest
    container_name: superset_app
    restart: unless-stopped
    depends_on:
      - db
      - redis
    environment:
      SUPERSET_SECRET_KEY: ${SUPERSET_SECRET_KEY}
      SQLALCHEMY_DATABASE_URI: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      # 安全配置
      WTF_CSRF_ENABLED: "True"
      TALISMAN_ENABLED: "True"
      HTTP_HEADERS: >
        {
          "X-Frame-Options": "SAMEORIGIN",
          "X-Content-Type-Options": "nosniff",
          "X-XSS-Protection": "1; mode=block",
          "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
          "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        }
    ports:
      - "127.0.0.1:8088:8088"  # 仅绑定到本地回环接口
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/superset_config.py
    networks:
      - superset_internal
      - superset_external
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID

networks:
  superset_internal:
    driver: bridge
    internal: true  # 内部网络，无外网访问
  superset_external:
    driver: bridge

volumes:
  db_data:
  redis_data:
  superset_home:
```

### SSL/TLS 配置

```bash
#!/bin/bash
# generate-ssl-cert.sh

# 配置变量
DOMAIN="your-domain.com"
CERT_DIR="./ssl"
OPENSSL_CONFIG="./openssl.cnf"

# 创建证书目录
mkdir -p ${CERT_DIR}

# 生成私钥
openssl genrsa -out ${CERT_DIR}/private.key 2048

# 生成证书签名请求
openssl req -new -key ${CERT_DIR}/private.key -out ${CERT_DIR}/certificate.csr \
  -subj "/C=CN/ST=State/L=City/O=Organization/CN=${DOMAIN}"

# 生成自签名证书（生产环境应使用 CA 签名的证书）
openssl x509 -req -days 365 -in ${CERT_DIR}/certificate.csr \
  -signkey ${CERT_DIR}/private.key -out ${CERT_DIR}/certificate.crt

# 设置权限
chmod 600 ${CERT_DIR}/private.key
chmod 644 ${CERT_DIR}/certificate.crt

echo "SSL certificates generated in ${CERT_DIR}"
```

## 14.9 CI/CD 集成

### Dockerfile 自定义构建

```dockerfile
# Dockerfile
FROM apache/superset:latest

# 安装额外的依赖
USER root
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 切换回 superset 用户
USER superset

# 安装额外的 Python 包
COPY requirements-extra.txt /app/
RUN pip install -r requirements-extra.txt

# 复制自定义配置
COPY superset_config.py /app/
COPY superset-init.sh /app/

# 设置启动脚本权限
RUN chmod +x /app/superset-init.sh

# 设置工作目录
WORKDIR /app

# 暴露端口
EXPOSE 8088

# 设置启动命令
ENTRYPOINT ["/app/superset-init.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8088", "--workers", "4", "--timeout", "120", "--limit-request-line", "0", "--limit-request-field_size", "0", "superset:app"]
```

### CI/CD 流水线配置

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  CONTAINER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG

before_script:
  - docker info

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build --pull -t $CONTAINER_IMAGE .
    - docker push $CONTAINER_IMAGE
  only:
    - master
    - develop

test:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  variables:
    POSTGRES_DB: superset_test
    POSTGRES_USER: superset
    POSTGRES_PASSWORD: superset
  script:
    - docker-compose -f docker-compose.test.yml up -d
    - sleep 30
    - docker-compose -f docker-compose.test.yml exec -T superset-web superset db upgrade
    - docker-compose -f docker-compose.test.yml exec -T superset-web pytest tests/
    - docker-compose -f docker-compose.test.yml down
  only:
    - merge_requests
    - master

deploy:
  stage: deploy
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker pull $CONTAINER_IMAGE
    - docker stack deploy --compose-file docker-compose.prod.yml superset
  environment:
    name: production
  only:
    - master
```

## 14.10 最佳实践总结

### 部署最佳实践

1. **使用环境变量管理配置**：
   - 敏感信息通过环境变量传递
   - 配置文件版本控制
   - 不同环境使用不同的配置

2. **数据持久化**：
   - 使用命名卷或绑定挂载
   - 定期备份重要数据
   - 实施灾难恢复计划

3. **安全性**：
   - 使用非 root 用户运行容器
   - 限制容器权限
   - 启用网络安全策略
   - 使用 HTTPS/TLS 加密

4. **监控和日志**：
   - 集中化日志管理
   - 实施健康检查
   - 配置监控告警
   - 性能指标收集

5. **高可用性**：
   - 多实例部署
   - 负载均衡
   - 故障自动恢复
   - 滚动更新策略

### 常见问题解决

1. **容器启动失败**：
   ```bash
   # 查看容器日志
   docker logs superset_app
   
   # 检查容器状态
   docker ps -a
   
   # 进入容器调试
   docker exec -it superset_app bash
   ```

2. **数据库连接问题**：
   ```bash
   # 测试数据库连接
   docker exec superset_app \
     python -c "import sqlalchemy; sqlalchemy.create_engine('postgresql://user:pass@db:5432/db').connect()"
   ```

3. **权限问题**：
   ```bash
   # 检查卷权限
   docker exec superset_app ls -la /app/superset_home
   
   # 修复权限
   docker exec superset_app chown -R superset:superset /app/superset_home
   ```

## 14.11 小结

本章详细介绍了 Apache Superset 的容器化部署方案，包括官方镜像使用、Docker Compose 部署、自定义配置、多实例部署、持久化存储、监控日志、安全加固以及 CI/CD 集成等多个方面。通过容器化部署，可以实现 Superset 的快速部署、弹性扩展和标准化管理。

在下一章中，我们将探讨 Apache Superset 的性能调优技巧。