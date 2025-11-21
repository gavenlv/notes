# 第二章：安装与环境配置

## 2.1 环境准备

在安装 Apache Superset 之前，我们需要准备好相应的运行环境。Superset 支持多种安装方式，包括 Docker、pip 安装和从源码构建。

### 系统要求

- **操作系统**：Linux, macOS, Windows (WSL推荐)
- **Python 版本**：3.8+ (推荐 3.9+)
- **内存**：至少 4GB RAM (推荐 8GB+)
- **磁盘空间**：至少 2GB 可用空间

### 依赖组件

1. **数据库**：用于存储元数据（默认使用 SQLite，生产环境推荐 PostgreSQL 或 MySQL）
2. **缓存系统**：用于提高性能（推荐 Redis 或 Memcached）
3. **消息队列**：用于异步任务处理（推荐 Celery + Redis/RabbitMQ）

## 2.2 安装方式对比

### 方式一：Docker 安装（推荐）

Docker 安装是最简单快捷的方式，适合快速体验和开发环境。

优点：
- 安装简单，一键启动
- 环境隔离，避免依赖冲突
- 易于部署和迁移

缺点：
- 自定义配置相对复杂
- 性能略低于原生安装

### 方式二：pip 安装

直接使用 pip 安装适合需要自定义配置的场景。

优点：
- 灵活性高，易于自定义
- 性能较好
- 便于集成到现有 Python 环境

缺点：
- 需要手动处理依赖
- 环境配置相对复杂

### 方式三：从源码构建

适合需要深度定制或参与开发的场景。

优点：
- 完全可控
- 便于开发和调试
- 可以使用最新特性

缺点：
- 安装复杂
- 需要较强的开发能力

## 2.3 Docker 安装详细步骤

### 步骤 1：安装 Docker 和 Docker Compose

确保系统已安装 Docker 和 Docker Compose：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# macOS
# 下载 Docker Desktop for Mac

# Windows
# 下载 Docker Desktop for Windows
```

### 步骤 2：获取官方 Docker Compose 文件

```bash
# 创建项目目录
mkdir superset-demo && cd superset-demo

# 下载官方 docker-compose.yml
wget https://raw.githubusercontent.com/apache/superset/master/docker-compose.yml
```

### 步骤 3：启动 Superset

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 步骤 4：初始化 Superset

```bash
# 初始化数据库
docker-compose exec superset superset-db upgrade

# 创建管理员账户
docker-compose exec superset superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password admin

# 加载示例数据（可选）
docker-compose exec superset superset load_examples

# 初始化角色和权限
docker-compose exec superset superset init
```

### 步骤 5：访问 Superset

打开浏览器访问 `http://localhost:8088`，使用刚才创建的管理员账户登录。

## 2.4 pip 安装详细步骤

### 步骤 1：创建虚拟环境

```bash
# 创建虚拟环境
python -m venv superset-env

# 激活虚拟环境
# Linux/macOS
source superset-env/bin/activate
# Windows
superset-env\Scripts\activate
```

### 步骤 2：安装 Superset

```bash
# 升级 pip
pip install --upgrade pip

# 安装 Superset
pip install apache-superset
```

### 步骤 3：初始化数据库

```bash
# 初始化数据库
superset db upgrade

# 创建管理员账户
export FLASK_APP=superset
superset fab create-admin

# 加载示例数据（可选）
superset load_examples

# 初始化角色和权限
superset init
```

### 步骤 4：启动 Superset

```bash
# 启动开发服务器
superset run -p 8088 --with-threads --reload --debugger
```

## 2.5 生产环境配置

### 数据库配置

生产环境中建议使用 PostgreSQL 或 MySQL 替代默认的 SQLite：

```python
# superset_config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@host:port/database'
```

### Redis 配置

配置 Redis 作为缓存和消息队列：

```python
# superset_config.py
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_CELERY_DB = 0
REDIS_RESULTS_DB = 1

class CeleryConfig(object):
    BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}'
    
CELERY_CONFIG = CeleryConfig
```

### 安全配置

```python
# superset_config.py
# 修改默认密钥
SECRET_KEY = 'YOUR_OWN_RANDOM_GENERATED_SECRET_KEY'

# 设置 CSRF 密钥
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# 设置公共角色权限
PUBLIC_ROLE_LIKE = 'Gamma'
```

## 2.6 常见问题解决

### 问题 1：端口被占用

```bash
# 查找占用端口的进程
lsof -i :8088

# 杀死进程
kill -9 <PID>
```

### 问题 2：权限不足

```bash
# 在 Linux 系统中，可能需要使用 sudo
sudo docker-compose up -d
```

### 问题 3：数据库连接失败

检查数据库服务是否正常运行，网络连接是否畅通，用户名密码是否正确。

## 2.7 验证安装

安装完成后，可以通过以下方式验证：

1. 访问 Web 界面：`http://localhost:8088`
2. 登录系统，查看主界面
3. 检查是否能正常创建数据源和图表

## 2.8 小结

本章介绍了 Apache Superset 的多种安装方式，其中 Docker 安装最为简便，适合快速体验；pip 安装适合需要自定义配置的场景；而从源码构建则适合深度定制需求。根据实际需求选择合适的安装方式，并按照相应步骤进行配置，即可成功部署 Superset 环境。