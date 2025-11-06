# 第4章：Docker容器高级操作

## 📚 本章目标

- 掌握容器的高级运行选项
- 理解容器资源限制和配额
- 学习容器的重启策略
- 掌握容器的健康检查机制
- 理解容器的环境变量管理
- 学习容器间的通信方式

## 4.1 容器运行的高级选项

### 4.1.1 容器命名和标识

```bash
# 自定义容器名称
docker run --name my-web nginx

# 自动生成名称
docker run nginx
# Docker会生成类似 "graceful_euler" 的随机名称

# 容器ID vs 容器名称
docker ps
# 可以使用ID或名称来操作容器
docker stop abc123456789  # 使用ID
docker stop my-web        # 使用名称

# 使用短ID（前3-4位）
docker stop abc1
```

### 4.1.2 后台运行和前台运行

```bash
# 前台运行（阻塞终端）
docker run nginx

# 后台运行（-d, detached模式）
docker run -d nginx

# 后台运行并查看日志
docker run -d --name web nginx
docker logs -f web

# 运行一次性任务
docker run --rm ubuntu echo "Hello"
# --rm: 容器退出后自动删除
```

### 4.1.3 交互式容器

```bash
# 交互式终端
docker run -it ubuntu bash
# -i: 保持STDIN开放
# -t: 分配伪终端

# 后台运行交互式容器
docker run -dit --name ubuntu-shell ubuntu bash

# 稍后附加到容器
docker attach ubuntu-shell

# 或使用exec进入
docker exec -it ubuntu-shell bash
```

## 4.2 容器资源限制

### 4.2.1 内存限制

```bash
# 限制内存为512MB
docker run -d --name mem-limited -m 512m nginx

# 内存 + Swap限制
docker run -d -m 512m --memory-swap 1g nginx
# memory-swap: 总内存限制（内存+swap）

# 禁用swap
docker run -d -m 512m --memory-swap 512m nginx

# 内存预留（软限制）
docker run -d --memory-reservation 256m nginx

# OOM Kill优先级
docker run -d --oom-kill-disable nginx  # 禁用OOM Kill（谨慎使用）
docker run -d --oom-score-adj 500 nginx # 调整优先级(-1000到1000)
```

**内存限制验证**：
```bash
# 运行一个内存测试容器
docker run -d --name mem-test -m 512m nginx

# 查看内存限制
docker inspect mem-test --format='{{.HostConfig.Memory}}'
# 输出: 536870912 (512MB in bytes)

# 查看实际使用
docker stats mem-test --no-stream
```

### 4.2.2 CPU限制

```bash
# 限制CPU核心数
docker run -d --cpus="1.5" nginx
# 最多使用1.5个CPU核心

# CPU配额（相对权重）
docker run -d --cpu-shares 512 nginx
# 默认值: 1024
# 512 = 50%权重, 2048 = 200%权重

# 指定CPU核心
docker run -d --cpuset-cpus="0,1" nginx
# 只能使用CPU 0和1

# CPU配额周期
docker run -d --cpu-period=100000 --cpu-quota=50000 nginx
# period: 100ms, quota: 50ms = 50% CPU
```

**CPU限制验证**：
```bash
# 运行CPU密集型任务
docker run -d --name cpu-test --cpus="0.5" ubuntu \
  bash -c "while true; do echo test > /dev/null; done"

# 查看CPU使用
docker stats cpu-test
# 应该看到CPU使用率在50%左右

# 停止测试
docker stop cpu-test
docker rm cpu-test
```

### 4.2.3 磁盘I/O限制

```bash
# 限制读写速度（字节/秒）
docker run -d \
  --device-read-bps /dev/sda:1mb \
  --device-write-bps /dev/sda:1mb \
  nginx

# 限制IOPS（操作/秒）
docker run -d \
  --device-read-iops /dev/sda:100 \
  --device-write-iops /dev/sda:100 \
  nginx

# 磁盘配额（需要存储驱动支持）
docker run -d --storage-opt size=10G nginx
```

### 4.2.4 PID限制

```bash
# 限制容器可创建的进程数
docker run -d --pids-limit 100 nginx

# 查看限制
docker inspect --format='{{.HostConfig.PidsLimit}}' <container>
```

## 4.3 容器重启策略

### 4.3.1 重启策略类型

```bash
# no: 不自动重启（默认）
docker run -d --restart no nginx

# always: 总是重启
docker run -d --restart always nginx

# on-failure: 失败时重启
docker run -d --restart on-failure nginx

# on-failure:3: 最多重启3次
docker run -d --restart on-failure:3 nginx

# unless-stopped: 除非手动停止，否则总是重启
docker run -d --restart unless-stopped nginx
```

### 4.3.2 重启策略对比

| 策略 | 容器退出码=0 | 容器退出码!=0 | Docker重启 | 手动停止 |
|------|-------------|--------------|-----------|---------|
| `no` | 不重启 | 不重启 | 不重启 | - |
| `always` | 重启 | 重启 | 重启 | 重启 |
| `on-failure` | 不重启 | 重启 | 重启 | 不重启 |
| `unless-stopped` | 重启 | 重启 | 重启 | 不重启 |

### 4.3.3 重启策略实战

```bash
# 场景1: Web服务器（应该总是运行）
docker run -d --restart always --name web nginx

# 场景2: 批处理任务（失败才重启）
docker run -d --restart on-failure:5 --name batch-job my-batch-app

# 场景3: 开发环境（手动控制）
docker run -d --restart no --name dev-app my-app

# 修改运行中容器的重启策略
docker update --restart always web
```

## 4.4 容器健康检查

### 4.4.1 健康检查配置

```bash
# 基本健康检查
docker run -d \
  --name web \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  --health-start-period=40s \
  nginx

# 参数说明：
# --health-cmd: 检查命令
# --health-interval: 检查间隔（默认30s）
# --health-timeout: 超时时间（默认30s）
# --health-retries: 失败重试次数（默认3次）
# --health-start-period: 启动宽限期（默认0s）
```

### 4.4.2 健康检查状态

```bash
# 查看健康状态
docker ps
# STATUS列会显示 (healthy) 或 (unhealthy)

# 详细健康信息
docker inspect --format='{{json .State.Health}}' web | jq

# 输出示例：
# {
#   "Status": "healthy",
#   "FailingStreak": 0,
#   "Log": [...]
# }
```

### 4.4.3 健康检查示例

```bash
# Web应用健康检查
docker run -d \
  --name webapp \
  --health-cmd="curl -f http://localhost:8080/health || exit 1" \
  --health-interval=10s \
  my-webapp

# 数据库健康检查
docker run -d \
  --name mysql \
  --health-cmd="mysqladmin ping -h localhost || exit 1" \
  --health-interval=10s \
  mysql:8.0

# Redis健康检查
docker run -d \
  --name redis \
  --health-cmd="redis-cli ping || exit 1" \
  --health-interval=5s \
  redis

# 自定义脚本健康检查
docker run -d \
  --name app \
  --health-cmd="/app/health-check.sh" \
  my-app
```

## 4.5 环境变量管理

### 4.5.1 设置环境变量

```bash
# 单个环境变量
docker run -d -e MYSQL_ROOT_PASSWORD=secret mysql

# 多个环境变量
docker run -d \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=mydb \
  -e MYSQL_USER=user \
  -e MYSQL_PASSWORD=pass \
  mysql

# 从文件读取环境变量
# env.list:
# MYSQL_ROOT_PASSWORD=secret
# MYSQL_DATABASE=mydb

docker run -d --env-file env.list mysql
```

### 4.5.2 查看环境变量

```bash
# 查看容器的环境变量
docker exec my-container env

# 通过inspect查看
docker inspect --format='{{.Config.Env}}' my-container

# 在容器内查看
docker exec -it my-container bash
root@container# echo $MYSQL_ROOT_PASSWORD
```

### 4.5.3 环境变量最佳实践

```bash
# ❌ 不要在命令行直接暴露敏感信息
docker run -e DB_PASSWORD=secret123 my-app

# ✅ 使用环境变量文件
docker run --env-file .env my-app

# ✅ 使用Docker Secrets（Swarm模式）
echo "secret123" | docker secret create db_password -
docker service create --secret db_password my-app

# ✅ 使用外部密钥管理系统
# HashiCorp Vault, AWS Secrets Manager, etc.
```

## 4.6 容器工作目录

### 4.6.1 指定工作目录

```bash
# 使用-w指定工作目录
docker run -w /app ubuntu pwd
# 输出: /app

# 在指定目录执行命令
docker run -w /etc ubuntu ls
# 列出/etc目录内容

# 实际应用
docker run -d -w /var/www/html \
  -v $(pwd)/html:/var/www/html \
  nginx
```

## 4.7 容器用户管理

### 4.7.1 指定运行用户

```bash
# 以特定用户运行
docker run --user 1000:1000 ubuntu id
# uid=1000 gid=1000

# 以root用户运行（默认）
docker run ubuntu id
# uid=0(root) gid=0(root)

# 使用用户名
docker run --user nginx nginx id

# 安全实践: 非root用户运行
docker run --user 1000:1000 my-app
```

### 4.7.2 用户权限问题

```bash
# 问题: 权限拒绝
docker run -v $(pwd)/data:/data --user 1000 ubuntu \
  touch /data/test.txt
# Permission denied

# 解决方案1: 修改主机目录权限
chmod 777 data/

# 解决方案2: 使用正确的UID
id  # 查看当前用户UID
docker run -v $(pwd)/data:/data --user $(id -u):$(id -g) ubuntu \
  touch /data/test.txt
```

## 4.8 容器标签

### 4.8.1 添加标签

```bash
# 运行时添加标签
docker run -d \
  --label environment=production \
  --label version=1.0 \
  --label team=backend \
  nginx

# 查看标签
docker inspect --format='{{json .Config.Labels}}' <container>
```

### 4.8.2 使用标签过滤

```bash
# 按标签过滤容器
docker ps --filter "label=environment=production"

# 按标签删除容器
docker rm $(docker ps -a --filter "label=environment=dev" -q)

# 多个标签过滤
docker ps \
  --filter "label=environment=production" \
  --filter "label=team=backend"
```

## 4.9 容器网络配置

### 4.9.1 端口映射

```bash
# 映射单个端口
docker run -d -p 8080:80 nginx

# 映射多个端口
docker run -d -p 8080:80 -p 8443:443 nginx

# 映射到随机端口
docker run -d -p 80 nginx

# 查看端口映射
docker port <container>

# 指定IP地址
docker run -d -p 127.0.0.1:8080:80 nginx
# 只能从localhost访问
```

### 4.9.2 网络模式

```bash
# bridge模式（默认）
docker run -d --network bridge nginx

# host模式（与主机共享网络）
docker run -d --network host nginx

# none模式（无网络）
docker run -d --network none nginx

# container模式（共享其他容器网络）
docker run -d --name web1 nginx
docker run -d --network container:web1 nginx
```

## 4.10 容器日志配置

### 4.10.1 日志驱动

```bash
# 默认json-file驱动
docker run -d nginx

# syslog驱动
docker run -d --log-driver syslog nginx

# none驱动（无日志）
docker run -d --log-driver none nginx

# 查看日志驱动
docker inspect --format='{{.HostConfig.LogConfig.Type}}' <container>
```

### 4.10.2 日志配置选项

```bash
# 限制日志大小
docker run -d \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx

# 日志标签
docker run -d \
  --log-opt labels=production \
  --log-opt env=APP_ENV \
  nginx
```

## 4.11 实战练习

### 练习1: 资源限制测试

```bash
# 1. 启动内存限制容器
docker run -d --name mem-test -m 256m nginx

# 2. 查看资源使用
docker stats mem-test --no-stream

# 3. 尝试超出限制
docker exec mem-test sh -c 'dd if=/dev/zero of=/tmp/test bs=1M count=300'

# 4. 观察容器行为
docker logs mem-test
```

### 练习2: 重启策略验证

```bash
# 1. 启动一个会失败的容器
docker run -d --name fail-test \
  --restart on-failure:3 \
  ubuntu bash -c "exit 1"

# 2. 观察重启次数
docker ps -a --filter name=fail-test

# 3. 查看事件日志
docker events --filter container=fail-test
```

### 练习3: 健康检查实战

```bash
# 1. 启动带健康检查的nginx
docker run -d --name healthy-web \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=5s \
  nginx

# 2. 查看健康状态
watch -n 1 'docker ps | grep healthy-web'

# 3. 破坏健康检查
docker exec healthy-web rm /usr/share/nginx/html/index.html

# 4. 观察状态变化
docker inspect --format='{{.State.Health.Status}}' healthy-web
```

## 4.12 本章总结

### 核心知识点

✅ **容器高级选项**
- 命名和标识
- 运行模式
- 交互式容器

✅ **资源限制**
- 内存限制
- CPU限制
- 磁盘I/O限制
- PID限制

✅ **重启策略**
- 四种重启策略
- 应用场景
- 策略对比

✅ **健康检查**
- 健康检查配置
- 状态监控
- 实际应用

✅ **环境变量**
- 设置和查看
- 安全最佳实践

✅ **其他配置**
- 工作目录
- 用户管理
- 标签管理
- 网络配置
- 日志配置

### 下一章预告

在[第5章：Dockerfile详解](../chapter05-dockerfile/README.md)中，我们将学习：
- Dockerfile语法和指令
- 构建高效镜像
- 多阶段构建
- 镜像优化技巧

---

**掌握容器高级操作，成为Docker专家！🚀**
