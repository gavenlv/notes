# 第8章：Docker Compose详解

## 📚 本章目标

- 理解Docker Compose的作用和优势
- 掌握docker-compose.yml语法
- 学会编排多容器应用
- 掌握服务管理和网络配置
- 理解环境变量和配置管理

## 8.1 Docker Compose简介

### 8.1.1 什么是Docker Compose？

**Docker Compose** 是用于定义和运行多容器Docker应用的工具。

**形象理解**：
```
单个容器 = 乐器演奏者
Docker Compose = 指挥家 + 乐谱
多容器应用 = 交响乐团

一个compose文件定义整个应用的所有服务
一个命令启动/停止整个应用栈
```

### 8.1.2 为什么需要Docker Compose？

**问题场景**：
```bash
# 手动启动多容器应用（繁琐）
docker network create app-network
docker run -d --name db --network app-network mysql
docker run -d --name redis --network app-network redis
docker run -d --name web --network app-network -p 80:80 nginx
```

**Compose解决方案**：
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: mysql
  redis:
    image: redis
  web:
    image: nginx
    ports:
      - "80:80"
```

```bash
# 一个命令启动所有服务
docker-compose up -d
```

### 8.1.3 安装Docker Compose

```bash
# Docker Desktop自带Compose（Windows/Mac）
docker-compose --version

# Linux安装
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

## 8.2 docker-compose.yml语法

### 8.2.1 基本结构

```yaml
version: '3.8'  # Compose文件版本

services:       # 定义服务
  service1:
    # 服务配置
  service2:
    # 服务配置

networks:       # 自定义网络（可选）
  # 网络配置

volumes:        # 数据卷（可选）
  # 卷配置
```

### 8.2.2 服务定义

**使用镜像**：
```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
```

**使用Dockerfile**：
```yaml
services:
  app:
    build: .              # 使用当前目录的Dockerfile
    # 或
    build:
      context: ./app      # 构建上下文
      dockerfile: Dockerfile.dev  # 指定Dockerfile
      args:               # 构建参数
        VERSION: 1.0
```

### 8.2.3 端口映射

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"         # 主机:容器
      - "8443:443"
      - "127.0.0.1:9000:9000"  # 指定IP
      - "3000-3005:3000-3005"  # 端口范围
```

### 8.2.4 环境变量

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: mydb
      MYSQL_USER: user
      MYSQL_PASSWORD: pass
    # 或从文件读取
    env_file:
      - .env
      - db.env
```

### 8.2.5 数据卷

```yaml
services:
  db:
    image: mysql
    volumes:
      # 命名卷
      - db-data:/var/lib/mysql
      # 绑定挂载
      - ./config:/etc/mysql/conf.d
      # 只读挂载
      - ./static:/usr/share/nginx/html:ro

volumes:
  db-data:  # 声明命名卷
```

### 8.2.6 依赖关系

```yaml
services:
  web:
    image: nginx
    depends_on:
      - app
      - db
  
  app:
    build: .
    depends_on:
      - db
  
  db:
    image: mysql
    
# 启动顺序: db → app → web
```

**健康检查依赖**：
```yaml
services:
  web:
    image: nginx
    depends_on:
      db:
        condition: service_healthy
  
  db:
    image: mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 8.2.7 网络配置

```yaml
services:
  web:
    image: nginx
    networks:
      - frontend
      - backend
  
  app:
    image: myapp
    networks:
      - backend
  
  db:
    image: mysql
    networks:
      - backend

networks:
  frontend:
  backend:
```

### 8.2.8 重启策略

```yaml
services:
  web:
    image: nginx
    restart: always  # no, always, on-failure, unless-stopped
```

### 8.2.9 资源限制

```yaml
services:
  app:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### 8.2.10 命令覆盖

```yaml
services:
  app:
    image: myapp
    command: python app.py --debug
    # 或
    command: ["python", "app.py", "--debug"]
    
    # 覆盖entrypoint
    entrypoint: /app/entrypoint.sh
```

## 8.3 完整示例

### 8.3.1 WordPress + MySQL

**docker-compose.yml**：
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    volumes:
      - db-data:/var/lib/mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppass
    networks:
      - wp-network

  wordpress:
    depends_on:
      - db
    image: wordpress:latest
    ports:
      - "8080:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppass
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wp-data:/var/www/html
    networks:
      - wp-network

volumes:
  db-data:
  wp-data:

networks:
  wp-network:
```

**启动**：
```bash
docker-compose up -d
# 访问 http://localhost:8080
```

### 8.3.2 Web应用 + 数据库 + Redis

**docker-compose.yml**：
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    networks:
      - frontend

  app:
    build: .
    environment:
      DB_HOST: db
      REDIS_HOST: redis
    depends_on:
      - db
      - redis
    networks:
      - frontend
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - backend

  redis:
    image: redis:alpine
    networks:
      - backend

volumes:
  postgres-data:

networks:
  frontend:
  backend:
```

### 8.3.3 微服务架构示例

**docker-compose.yml**：
```yaml
version: '3.8'

services:
  # API Gateway
  gateway:
    build: ./gateway
    ports:
      - "80:80"
    depends_on:
      - user-service
      - order-service
    networks:
      - microservices

  # 用户服务
  user-service:
    build: ./user-service
    environment:
      DB_HOST: user-db
    depends_on:
      - user-db
    networks:
      - microservices

  user-db:
    image: postgres:15
    environment:
      POSTGRES_DB: users
      POSTGRES_PASSWORD: secret
    volumes:
      - user-data:/var/lib/postgresql/data
    networks:
      - microservices

  # 订单服务
  order-service:
    build: ./order-service
    environment:
      DB_HOST: order-db
      REDIS_HOST: redis
    depends_on:
      - order-db
      - redis
    networks:
      - microservices

  order-db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: orders
      MYSQL_ROOT_PASSWORD: secret
    volumes:
      - order-data:/var/lib/mysql
    networks:
      - microservices

  # Redis缓存
  redis:
    image: redis:alpine
    networks:
      - microservices

  # 消息队列
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "15672:15672"  # 管理界面
    networks:
      - microservices

volumes:
  user-data:
  order-data:

networks:
  microservices:
    driver: bridge
```

## 8.4 Compose命令详解

### 8.4.1 启动服务

```bash
# 启动所有服务
docker-compose up

# 后台启动
docker-compose up -d

# 启动指定服务
docker-compose up -d web db

# 强制重新构建
docker-compose up --build

# 启动时不创建网络
docker-compose up --no-deps web
```

### 8.4.2 停止服务

```bash
# 停止所有服务
docker-compose stop

# 停止指定服务
docker-compose stop web

# 停止并删除容器、网络
docker-compose down

# 删除容器、网络、卷
docker-compose down -v

# 删除容器、网络、卷、镜像
docker-compose down -v --rmi all
```

### 8.4.3 查看服务

```bash
# 查看运行中的服务
docker-compose ps

# 查看所有服务（包括停止的）
docker-compose ps -a

# 查看服务日志
docker-compose logs

# 实时跟踪日志
docker-compose logs -f

# 查看指定服务日志
docker-compose logs -f web

# 查看最后100行
docker-compose logs --tail=100
```

### 8.4.4 执行命令

```bash
# 在服务中执行命令
docker-compose exec web bash

# 执行一次性命令
docker-compose run app python manage.py migrate

# 不启动依赖服务
docker-compose run --no-deps app pytest
```

### 8.4.5 扩展服务

```bash
# 扩展到3个实例
docker-compose up -d --scale web=3

# 扩展多个服务
docker-compose up -d --scale web=3 --scale worker=5
```

### 8.4.6 其他命令

```bash
# 验证配置文件
docker-compose config

# 查看服务配置
docker-compose config --services

# 构建镜像
docker-compose build

# 重启服务
docker-compose restart

# 暂停服务
docker-compose pause

# 恢复服务
docker-compose unpause

# 查看服务进程
docker-compose top
```

## 8.5 环境变量管理

### 8.5.1 .env文件

**.env**：
```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=secret
MYSQL_DATABASE=myapp

# 应用配置
APP_ENV=production
APP_PORT=8080
```

**docker-compose.yml**：
```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
  
  app:
    build: .
    ports:
      - "${APP_PORT}:8080"
```

### 8.5.2 多环境配置

**docker-compose.yml** (基础配置)：
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
```

**docker-compose.override.yml** (开发环境)：
```yaml
version: '3.8'
services:
  app:
    volumes:
      - ./:/app
    environment:
      DEBUG: "true"
```

**docker-compose.prod.yml** (生产环境)：
```yaml
version: '3.8'
services:
  app:
    restart: always
    environment:
      DEBUG: "false"
```

**使用**：
```bash
# 开发环境（自动加载override）
docker-compose up

# 生产环境
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 8.6 网络高级配置

### 8.6.1 自定义网络

```yaml
networks:
  frontend:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
  
  backend:
    driver: bridge
    internal: true  # 内部网络，无外部访问
```

### 8.6.2 外部网络

```yaml
services:
  web:
    image: nginx
    networks:
      - existing-network

networks:
  existing-network:
    external: true  # 使用已存在的网络
```

### 8.6.3 网络别名

```yaml
services:
  db:
    image: mysql
    networks:
      backend:
        aliases:
          - database
          - mysql-server
```

## 8.7 实战练习

### 练习1: LNMP环境

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./www:/var/www/html
    depends_on:
      - php
    networks:
      - lnmp

  php:
    image: php:8.1-fpm
    volumes:
      - ./www:/var/www/html
    networks:
      - lnmp

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: test
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - lnmp

volumes:
  mysql-data:

networks:
  lnmp:
```

### 练习2: 开发环境

```yaml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - ./:/app
      - /app/node_modules
    command: npm run dev
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: devdb
      POSTGRES_PASSWORD: devpass
    ports:
      - "5432:5432"
    volumes:
      - pg-data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  pg-data:
```

## 8.8 本章总结

### 核心知识点

✅ **Compose基础**
- 作用和优势
- 安装和使用
- YAML语法

✅ **服务配置**
- 镜像和构建
- 端口映射
- 环境变量
- 数据卷
- 网络配置

✅ **服务编排**
- 依赖关系
- 启动顺序
- 健康检查
- 重启策略

✅ **Compose命令**
- up/down
- ps/logs
- exec/run
- scale

✅ **高级特性**
- 多环境配置
- 环境变量管理
- 网络高级配置

### 下一章预告

在[第9章：Docker私有仓库](../chapter09-registry/README.md)中，我们将学习：
- Docker Hub使用
- 搭建私有Registry
- Harbor安装配置
- 镜像推送拉取

---

**掌握Docker Compose，轻松编排多容器应用！🚀**
