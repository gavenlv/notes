# 第3章：Docker镜像管理

## 📚 本章目标

- 掌握镜像的搜索、拉取、推送操作
- 理解镜像标签管理
- 学会镜像的导入导出
- 深入理解镜像的分层存储
- 掌握镜像的清理和优化

## 3.1 镜像的来源

### 3.1.1 官方镜像仓库

**Docker Hub** - 官方公共仓库
```bash
# 搜索官方镜像
docker search nginx --filter is-official=true

# 常用官方镜像
docker pull nginx        # Web服务器
docker pull mysql        # 数据库
docker pull redis        # 缓存
docker pull python       # Python运行环境
docker pull node         # Node.js运行环境
docker pull ubuntu       # Ubuntu操作系统
```

### 3.1.2 镜像命名详解

```
完整格式：
[registry]/[namespace]/[repository]:[tag]

示例分析：
docker.io/library/nginx:1.21.6
│        │      │      └── 标签(版本号)
│        │      └───────── 仓库名称
│        └──────────────── 命名空间(用户/组织)
└───────────────────────── 仓库地址

简写规则：
nginx               = docker.io/library/nginx:latest
nginx:1.21          = docker.io/library/nginx:1.21
username/myapp      = docker.io/username/myapp:latest
gcr.io/proj/image   = gcr.io/proj/image:latest
```

### 3.1.3 镜像标签策略

**语义化版本标签**：
```bash
# 主版本号
docker pull python:3       # Python 3.x最新版

# 主.次版本号
docker pull python:3.9     # Python 3.9.x最新版

# 完整版本号
docker pull python:3.9.18  # 精确版本

# 特殊标签
docker pull python:latest  # 最新稳定版
docker pull python:alpine  # Alpine Linux版本(更小)
docker pull python:slim    # 精简版
```

## 3.2 镜像操作详解

### 3.2.1 搜索镜像

```bash
# 基本搜索
docker search python

# 限制结果数量
docker search --limit 10 python

# 过滤官方镜像
docker search --filter is-official=true python

# 过滤星标数
docker search --filter stars=100 python

# 格式化输出
docker search --format "table {{.Name}}\t{{.Description}}\t{{.StarCount}}" python
```

**输出示例**：
```
NAME        DESCRIPTION                          STARS
python      Python is an interpreted...          8000
pypy        PyPy is a fast...                    500
```

### 3.2.2 拉取镜像

```bash
# 拉取最新版本
docker pull nginx

# 拉取指定版本
docker pull nginx:1.21.6

# 拉取所有标签（不推荐）
docker pull -a nginx

# 指定平台架构
docker pull --platform linux/amd64 nginx
docker pull --platform linux/arm64 nginx

# 查看拉取进度
docker pull ubuntu
```

**拉取过程详解**：
```
Using default tag: latest
latest: Pulling from library/ubuntu

e96e057aae67: Pull complete    ← Layer 1
9e3ea8720c6d: Pull complete    ← Layer 2
d23faea7e0ef: Pull complete    ← Layer 3
b234f539f7a1: Pull complete    ← Layer 4

Digest: sha256:abc123...       ← 镜像摘要(唯一标识)
Status: Downloaded newer image for ubuntu:latest
docker.io/library/ubuntu:latest
```

### 3.2.3 查看镜像

```bash
# 列出所有镜像
docker images

# 列出指定镜像
docker images nginx

# 显示摘要信息
docker images --digests

# 只显示镜像ID
docker images -q

# 过滤显示
docker images --filter "dangling=true"    # 悬空镜像
docker images --filter "before=nginx"     # 指定镜像之前的
docker images --filter "since=nginx"      # 指定镜像之后的

# 自定义格式
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

**输出示例**：
```
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
nginx        latest    abc123456789   2 weeks ago   142MB
python       3.9       def987654321   3 weeks ago   885MB
```

### 3.2.4 查看镜像详细信息

```bash
# 查看镜像详细配置
docker inspect nginx:latest

# 查看镜像历史
docker history nginx:latest

# 查看镜像大小详情
docker history --human=false --no-trunc nginx

# 提取特定信息(使用format)
docker inspect --format='{{.Config.Env}}' nginx
docker inspect --format='{{.Architecture}}' nginx
```

### 3.2.5 镜像分层分析

```bash
# 查看镜像层历史
docker history nginx:latest

# 输出示例
IMAGE          CREATED BY                                      SIZE
abc123         /bin/sh -c #(nop)  CMD ["nginx"]               0B
def456         /bin/sh -c #(nop)  EXPOSE 80                   0B
ghi789         /bin/sh -c ln -sf /dev/stdout...               22B
jkl012         /bin/sh -c apt-get update && apt-get...        54MB
mno345         /bin/sh -c #(nop) ADD file:abc123...           72MB
```

**理解层的作用**：
- 每一行代表一个层
- SIZE列显示该层增加的大小
- 0B表示仅元数据变化，无文件变化
- 层是只读的，可被多个镜像共享

## 3.3 镜像标签管理

### 3.3.1 创建镜像标签

```bash
# 基本语法
docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]

# 示例
docker tag nginx:latest mynginx:v1.0
docker tag nginx:latest myregistry.com/mynginx:latest

# 为同一镜像创建多个标签
docker tag myapp:latest myapp:1.0
docker tag myapp:latest myapp:stable
docker tag myapp:latest myregistry.com/myapp:latest
```

**标签原理**：
```
镜像层(不变)
    ↑
    ├── nginx:latest  (标签1)
    ├── nginx:1.21    (标签2)
    └── mynginx:v1    (标签3)

同一个镜像，多个标签指向它
删除标签不影响镜像层(除非是最后一个标签)
```

### 3.3.2 标签最佳实践

**版本标签策略**：
```bash
# 开发环境
myapp:dev
myapp:dev-20240106

# 测试环境
myapp:test
myapp:test-v1.2.3

# 生产环境
myapp:prod
myapp:1.0.0
myapp:1.0
myapp:latest

# Git提交版本
myapp:git-abc1234
```

## 3.4 镜像的导入导出

### 3.4.1 导出镜像为文件

```bash
# 保存单个镜像
docker save -o nginx.tar nginx:latest

# 保存多个镜像
docker save -o images.tar nginx:latest mysql:8.0 redis:latest

# 使用压缩
docker save nginx:latest | gzip > nginx.tar.gz
```

### 3.4.2 从文件导入镜像

```bash
# 加载镜像
docker load -i nginx.tar

# 加载压缩镜像
docker load < nginx.tar.gz
gunzip -c nginx.tar.gz | docker load
```

### 3.4.3 导出导入的应用场景

**使用场景**：
1. **离线环境部署**
   ```bash
   # 在线环境导出
   docker save -o app-bundle.tar app:latest db:latest cache:latest
   
   # 拷贝到离线环境
   # 在离线环境加载
   docker load -i app-bundle.tar
   ```

2. **镜像备份**
   ```bash
   # 定期备份重要镜像
   docker save myapp:prod | gzip > backup/myapp-$(date +%Y%m%d).tar.gz
   ```

3. **跨主机迁移**
   ```bash
   # 主机A导出
   docker save -o app.tar myapp:latest
   
   # 传输到主机B
   scp app.tar user@hostB:/tmp/
   
   # 主机B导入
   ssh user@hostB 'docker load -i /tmp/app.tar'
   ```

## 3.5 镜像的推送和分享

### 3.5.1 推送到Docker Hub

```bash
# 1. 登录Docker Hub
docker login

# 2. 为镜像打标签(包含用户名)
docker tag myapp:latest username/myapp:latest

# 3. 推送镜像
docker push username/myapp:latest

# 4. 推送多个标签
docker push username/myapp:1.0
docker push username/myapp:latest

# 5. 推送所有标签
docker push --all-tags username/myapp
```

### 3.5.2 推送到私有仓库

```bash
# 1. 标记镜像(包含私有仓库地址)
docker tag myapp:latest myregistry.com:5000/myapp:latest

# 2. 登录私有仓库
docker login myregistry.com:5000

# 3. 推送镜像
docker push myregistry.com:5000/myapp:latest
```

## 3.6 镜像清理和优化

### 3.6.1 删除镜像

```bash
# 删除单个镜像
docker rmi nginx:latest

# 删除多个镜像
docker rmi nginx mysql redis

# 强制删除(即使有容器使用)
docker rmi -f nginx

# 删除所有未使用的镜像
docker image prune

# 删除所有镜像(包括未使用的)
docker image prune -a

# 删除悬空镜像(dangling images)
docker rmi $(docker images -f "dangling=true" -q)
```

### 3.6.2 清理策略

```bash
# 查看磁盘使用情况
docker system df

# 输出示例
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          10        5         2.5GB     1.2GB (48%)
Containers      5         2         100MB     50MB (50%)
Local Volumes   3         1         500MB     300MB (60%)

# 清理所有未使用资源
docker system prune

# 清理所有资源(包括未使用的镜像)
docker system prune -a

# 清理指定时间前的资源
docker image prune -a --filter "until=24h"
```

## 3.7 实战练习

### 练习1：镜像版本管理

```bash
# 1. 拉取不同版本的Python镜像
docker pull python:3.8
docker pull python:3.9
docker pull python:3.10
docker pull python:3.11

# 2. 查看镜像大小对比
docker images python

# 3. 为镜像创建自定义标签
docker tag python:3.11 my-python:latest
docker tag python:3.11 my-python:prod

# 4. 查看镜像层详情
docker history python:3.11
```

### 练习2：镜像导入导出

```bash
# 1. 保存镜像
docker save -o python3.tar python:3.11

# 2. 删除原镜像
docker rmi python:3.11

# 3. 验证镜像已删除
docker images python

# 4. 重新加载镜像
docker load -i python3.tar

# 5. 验证恢复成功
docker images python
```

### 练习3：镜像清理

```bash
# 1. 查看当前磁盘使用
docker system df

# 2. 拉取一些测试镜像
docker pull alpine
docker pull busybox
docker pull hello-world

# 3. 创建一些悬空镜像(后续Dockerfile章节详解)
# 此处先跳过

# 4. 清理未使用的镜像
docker image prune

# 5. 再次查看磁盘使用
docker system df
```

## 3.8 本章总结

### 核心知识点

✅ **镜像来源和命名**
- Docker Hub和私有仓库
- 镜像命名规则
- 标签策略

✅ **镜像操作**
- 搜索、拉取、查看镜像
- 镜像详细信息和历史
- 镜像分层分析

✅ **标签管理**
- 创建和管理标签
- 标签最佳实践

✅ **导入导出**
- save和load命令
- 应用场景

✅ **镜像分享**
- 推送到Docker Hub
- 推送到私有仓库

✅ **清理优化**
- 删除镜像
- 清理策略
- 磁盘管理

### 下一章预告

在[第4章：Docker容器操作](../chapter04-container-operations/README.md)中，我们将学习：
- 容器的高级运行选项
- 容器资源限制
- 容器的重启策略
- 容器的健康检查

---

**继续学习Docker镜像的深入知识！🚀**

## 附录：常用镜像推荐

### Web服务器
- `nginx` - 高性能Web服务器
- `httpd` - Apache HTTP服务器
- `caddy` - 现代化Web服务器

### 数据库
- `mysql` - MySQL关系数据库
- `postgres` - PostgreSQL数据库
- `mongodb` - MongoDB文档数据库
- `redis` - Redis缓存数据库

### 编程语言运行时
- `python` - Python运行环境
- `node` - Node.js运行环境
- `openjdk` - Java运行环境
- `golang` - Go语言环境

### 操作系统基础镜像
- `ubuntu` - Ubuntu Linux
- `debian` - Debian Linux
- `alpine` - Alpine Linux(极小)
- `centos` - CentOS Linux
