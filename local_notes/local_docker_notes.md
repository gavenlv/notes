# Docker 本地环境配置与命令笔记

## 1. MySQL 容器部署

```bash
docker run \
-p 3306:3306 \
--restart=always \
--name mysql \
--privileged=true \
-v //c:/sandbox/docker-mount/mysql8:/var/log/mysql \
-v //c:/sandbox/docker-mount/mysql8:/var/lib/mysql \
-v //c:/sandbox/docker-mount/mysql8/my.cnf:/etc/mysql/my.cnf \
-e MYSQL_ROOT_PASSWORD=mysql \
-d mysql:8.3.0  
```

**注意事项**：
- 数据卷挂载路径：`/c/sandbox/docker-mount/mysql8`
- 确保挂载目录存在并有正确权限
- `--privileged=true` 授予容器额外权限，解决部分权限问题

## 2. Redis 容器部署

```bash
docker run \
--restart=always \
--log-opt max-size=100m \
--log-opt max-file=2 \
-p 6379:6379 \
--name redis \
-v //c/sandbox/docker-mount/redis/conf/redis.conf:/etc/redis/redis.conf \
-v //c/sandbox/docker-mount/redis/data:/data \
-d redis:latest \
redis-server /etc/redis/redis.conf \
--appendonly yes \
--requirepass 123456 
```

**优化说明**：
- 日志限制：每个日志文件最大100MB，最多保留2个
- 持久化：开启 AOF 持久化（appendonly yes）
- 访问控制：设置密码认证

## 3. ClickHouse 容器部署

### 3.1 基本部署（带数据持久化）

```gitbash
docker run -d -p 8123:8123 -p 9000:9000 --name clickhouse-server --ulimit nofile=262144:262144 \
-e CLICKHOUSE_USER=admin \
-e CLICKHOUSE_PASSWORD=admin \
-u 101:101 \
-v //c/sandbox/docker-mount/clickhouse/data:/var/lib/clickhouse \
-v //c/sandbox/docker-mount/clickhouse/logs:/var/log/clickhouse-server \
clickhouse/clickhouse-server
```

### 3.2 快速测试部署（无持久化）

```gitbash
docker run -d -p 8123:8123 -p 9000:9000 --name clickhouse-server --ulimit nofile=262144:262144 \
-e CLICKHOUSE_USER=admin \
-e CLICKHOUSE_PASSWORD=admin \
clickhouse/clickhouse-server
```

### 3.3 添加自定义配置

```bash
# 添加到docker run命令中
-v //c/sandbox/docker-mount/clickhouse/configs/config.xml:/etc/clickhouse-server/config.xml \
```

### 3.4 连接到 ClickHouse 容器

```bash
docker exec -it clickhouse-server clickhouse-client --user admin --password admin
```

## 4. Nginx 容器部署

### 4.1 基本部署（带数据卷挂载）

```bash
# Git Bash 环境下的命令
docker run -d \
  -v //d/docker_data/nginx:/usr/share/nginx/html \
  -p 8087:80 \
  --name nginx \
  nginx:latest
```

### 4.2 Windows 路径挂载注意事项

- Windows 路径在 Docker 中应使用 `//d/path/to/dir` 格式
- 避免使用 `;` 字符，它在 Windows 中是路径分隔符
- 确保挂载目录存在，否则 Docker 可能会创建错误的挂载点

## 5. StarRocks 容器部署

```bash
docker run -p 9030:9030 -p 8030:8030 -p 8040:8040 -itd --name quickstart starrocks/allin1-ubuntu
```

## 6. 常用 Docker 管理命令

### 6.1 容器管理

```bash
# 列出运行中的容器
docker ps

# 列出所有容器（包括停止的）
docker ps -a

# 启动/停止/重启容器
docker start mysql
docker stop mysql
docker restart mysql

# 查看容器日志
docker logs mysql
docker logs -f --tail 100 mysql  # 实时查看最后100行日志

# 进入容器内部
docker exec -it mysql bash

# 删除容器（必须先停止）
docker rm mysql
```

### 6.2 镜像管理

```bash
# 列出本地镜像
docker images

# 拉取镜像
docker pull mysql:8.0

# 删除镜像
docker rmi mysql:8.0

# 构建镜像
docker build -t myapp:latest .
```

### 6.3 数据卷管理

```bash
# 列出数据卷
docker volume ls

# 创建数据卷
docker volume create myvolume

# 删除数据卷
docker volume rm myvolume

# 清理未使用的数据卷
docker volume prune
```

## 7. Docker Compose 示例

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.3.0
    container_name: mysql
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - mysql_config:/etc/mysql/conf.d
    environment:
      MYSQL_ROOT_PASSWORD: mysql
      MYSQL_DATABASE: app_db
    restart: always

  redis:
    image: redis:latest
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass 123456
    restart: always

volumes:
  mysql_data:
  mysql_config:
  redis_data:
```

运行命令：
```bash
docker-compose up -d
```

## 8. Windows Docker 环境优化建议

1. **使用 WSL 2 后端**：提升 Docker 性能
2. **调整内存和 CPU 分配**：在 Docker Desktop 设置中优化资源分配
3. **使用 Docker Desktop 的文件共享**：避免使用过于复杂的路径映射
4. **定期清理**：使用 `docker system prune` 清理未使用的资源

## 9. 故障排查常见问题

### 权限问题
```bash
# 为挂载目录设置适当权限（Linux环境）
chown -R 1000:1000 /path/to/mount

# Windows环境下使用 --privileged 或调整文件共享设置
```

### 端口冲突
```bash
# 查找占用端口的进程
netstat -ano | findstr :3306

# 使用不同端口映射
-p 3307:3306
```

### 日志过大
```bash
# 设置日志限制
--log-opt max-size=100m --log-opt max-file=3

# 清理容器日志
docker exec -it mysql truncate -s 0 /var/log/mysql/error.log
```

### local docker, list all top use images
```dotnetcli
docker pull zlsmshoqvwt6q1.xuanyuan.run/library/redis:latest
docker pull zlsmshoqvwt6q1.xuanyuan.run/nginx:latest
docker pull zlsmshoqvwt6q1.xuanyuan.run/bitnami/postgresql:latest
docker pull zlsmshoqvwt6q1.xuanyuan.run/library/mysql:8.3.0
docker pull zlsmshoqvwt6q1.xuanyuan.run/library/starrocks:latest
docker pull zlsmshoqvwt6q1.xuanyuan.run/library/node:latest
docker pull zlsmshoqvwt6q1.xuanyuan.run/library/elasticsearch:9.2.0


```

