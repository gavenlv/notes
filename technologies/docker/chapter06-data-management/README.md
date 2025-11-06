# 第6章：Docker数据管理

## 📚 本章目标

- 理解Docker数据持久化的三种方式
- 掌握数据卷(Volumes)的使用
- 学会绑定挂载(Bind Mounts)
- 理解tmpfs挂载的应用场景
- 掌握数据备份和恢复策略

## 6.1 Docker数据存储概述

### 6.1.1 为什么需要数据持久化？

**问题**：
```bash
# 容器删除后数据丢失
docker run --name db mysql
# 在容器中写入数据
docker rm db
# 数据永久丢失！❌
```

**解决方案**：使用数据持久化
- ✅ 数据独立于容器生命周期
- ✅ 多容器共享数据
- ✅ 数据备份和迁移

### 6.1.2 三种数据存储方式

```
┌────────────────────────────────────────┐
│           Docker主机                    │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Volumes (数据卷)                  │ │
│  │ /var/lib/docker/volumes/          │ │
│  │ ✅ Docker管理                      │ │
│  │ ✅ 推荐使用                        │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Bind Mounts (绑定挂载)            │ │
│  │ /host/path → /container/path      │ │
│  │ ⚠️  依赖主机目录结构               │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ tmpfs (内存挂载)                  │ │
│  │ 存储在内存中                       │ │
│  │ ⚡ 高性能临时数据                  │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## 6.2 数据卷 (Volumes)

### 6.2.1 创建和使用数据卷

```bash
# 创建数据卷
docker volume create my-vol

# 查看数据卷列表
docker volume ls

# 查看数据卷详情
docker volume inspect my-vol

# 使用数据卷运行容器
docker run -d --name db \
  -v my-vol:/var/lib/mysql \
  mysql

# 匿名卷（自动创建）
docker run -d -v /var/lib/mysql mysql
```

### 6.2.2 数据卷操作

```bash
# 删除数据卷
docker volume rm my-vol

# 清理未使用的卷
docker volume prune

# 查看卷的挂载点（Linux）
docker volume inspect my-vol --format '{{.Mountpoint}}'
# /var/lib/docker/volumes/my-vol/_data
```

### 6.2.3 数据卷实战

**MySQL持久化**：
```bash
# 创建卷
docker volume create mysql-data

# 运行MySQL
docker run -d \
  --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=secret \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# 数据持久化验证
docker exec -it mysql-db mysql -uroot -psecret
mysql> CREATE DATABASE testdb;
mysql> exit

# 删除容器
docker rm -f mysql-db

# 重新创建容器，数据仍在
docker run -d \
  --name mysql-db-new \
  -e MYSQL_ROOT_PASSWORD=secret \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

docker exec -it mysql-db-new mysql -uroot -psecret
mysql> SHOW DATABASES;  # testdb仍然存在 ✅
```

## 6.3 绑定挂载 (Bind Mounts)

### 6.3.1 基本使用

```bash
# Windows PowerShell
docker run -d -v ${PWD}/html:/usr/share/nginx/html nginx

# Linux/Mac
docker run -d -v $(pwd)/html:/usr/share/nginx/html nginx

# 只读挂载
docker run -d -v $(pwd)/config:/etc/nginx:ro nginx

# 完整语法
docker run -d \
  --mount type=bind,source=/host/path,target=/container/path \
  nginx
```

### 6.3.2 实战示例

**开发环境代码同步**：
```bash
# 项目目录
project/
├── app.py
├── requirements.txt
└── templates/

# 挂载代码目录
docker run -d \
  -v $(pwd):/app \
  -w /app \
  -p 5000:5000 \
  python:3.9 \
  python app.py

# 修改app.py → 容器内自动更新
```

**配置文件挂载**：
```bash
# 挂载Nginx配置
docker run -d \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  -p 80:80 \
  nginx
```

### 6.3.3 权限问题处理

```bash
# 问题：权限拒绝
docker run -v $(pwd)/data:/data alpine touch /data/test.txt
# Permission denied

# 解决方案1：使用当前用户UID
docker run --user $(id -u):$(id -g) \
  -v $(pwd)/data:/data \
  alpine touch /data/test.txt

# 解决方案2：修改主机目录权限
chmod 777 data/
```

## 6.4 tmpfs挂载

### 6.4.1 使用场景

```bash
# tmpfs挂载（存储在内存）
docker run -d \
  --tmpfs /tmp:rw,size=100m \
  nginx

# 适用场景：
# - 临时文件
# - 缓存数据
# - 敏感信息（不写入磁盘）
# - 高性能临时数据
```

## 6.5 数据共享

### 6.5.1 多容器共享数据卷

```bash
# 创建共享卷
docker volume create shared-data

# 容器1写入数据
docker run -v shared-data:/data alpine \
  sh -c "echo 'Hello' > /data/message.txt"

# 容器2读取数据
docker run -v shared-data:/data alpine \
  cat /data/message.txt
# 输出: Hello ✅
```

### 6.5.2 数据容器模式（已过时）

```bash
# 数据容器（不推荐，使用命名卷代替）
docker create -v /data --name datastore busybox
docker run --volumes-from datastore alpine ls /data
```

## 6.6 数据备份和恢复

### 6.6.1 数据卷备份

```bash
# 备份数据卷
docker run --rm \
  -v mysql-data:/source \
  -v $(pwd)/backup:/backup \
  alpine \
  tar czf /backup/mysql-backup.tar.gz -C /source .

# 验证备份
ls -lh backup/mysql-backup.tar.gz
```

### 6.6.2 数据卷恢复

```bash
# 恢复数据卷
docker run --rm \
  -v mysql-data:/target \
  -v $(pwd)/backup:/backup \
  alpine \
  tar xzf /backup/mysql-backup.tar.gz -C /target
```

### 6.6.3 完整备份恢复流程

```bash
# 1. 停止使用数据的容器
docker stop mysql-db

# 2. 备份数据
docker run --rm \
  -v mysql-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/mysql-$(date +%Y%m%d).tar.gz -C /data .

# 3. 重启容器
docker start mysql-db

# 恢复数据（如需要）
# 1. 创建新卷
docker volume create mysql-restored

# 2. 恢复数据
docker run --rm \
  -v mysql-restored:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/mysql-20240106.tar.gz -C /data

# 3. 使用恢复的数据
docker run -d \
  -v mysql-restored:/var/lib/mysql \
  mysql:8.0
```

## 6.7 实战练习

### 练习1：数据库持久化

```bash
# 1. 创建PostgreSQL容器
docker run -d \
  --name pg-db \
  -e POSTGRES_PASSWORD=secret \
  -v pg-data:/var/lib/postgresql/data \
  postgres:15

# 2. 创建测试数据
docker exec -it pg-db psql -U postgres
CREATE DATABASE testdb;
\c testdb
CREATE TABLE users (id SERIAL, name VARCHAR(50));
INSERT INTO users (name) VALUES ('Alice'), ('Bob');
\q

# 3. 删除并重建容器
docker rm -f pg-db
docker run -d \
  --name pg-db-new \
  -e POSTGRES_PASSWORD=secret \
  -v pg-data:/var/lib/postgresql/data \
  postgres:15

# 4. 验证数据
docker exec -it pg-db-new psql -U postgres testdb
SELECT * FROM users;  # 数据仍在
```

### 练习2：配置文件管理

```bash
# 创建配置文件
mkdir config
cat > config/nginx.conf <<EOF
server {
    listen 80;
    location / {
        return 200 "Custom Nginx Config\n";
    }
}
EOF

# 挂载配置运行
docker run -d \
  -v $(pwd)/config/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -p 8080:80 \
  nginx

# 测试
curl http://localhost:8080
```

## 6.8 本章总结

### 核心知识点

✅ **三种存储方式**
- Volumes（推荐）
- Bind Mounts（开发）
- tmpfs（临时）

✅ **数据卷管理**
- 创建和删除
- 命名卷vs匿名卷
- 数据持久化

✅ **绑定挂载**
- 代码同步
- 配置管理
- 权限处理

✅ **数据备份**
- 备份策略
- 恢复流程

---

**掌握数据管理，确保数据安全！🚀**
