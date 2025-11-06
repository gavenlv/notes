# 第5章：Dockerfile详解

## 📚 本章目标

- 掌握Dockerfile的基本语法和指令
- 理解镜像构建的工作原理
- 学会编写高效的Dockerfile
- 掌握多阶段构建技术
- 学习镜像优化的最佳实践

## 5.1 Dockerfile简介

### 5.1.1 什么是Dockerfile？

**Dockerfile** 是一个文本文件，包含了构建Docker镜像所需的所有指令。

**形象理解**：
```
Dockerfile = 建筑施工图纸
每一行指令 = 施工步骤
docker build = 施工过程
最终镜像 = 建成的建筑物
```

### 5.1.2 第一个Dockerfile

```dockerfile
# 使用官方Python镜像作为基础
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制文件到容器
COPY app.py /app/

# 安装依赖
RUN pip install flask

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["python", "app.py"]
```

**构建镜像**：
```bash
docker build -t my-python-app .
```

## 5.2 Dockerfile指令详解

### 5.2.1 FROM - 基础镜像

```dockerfile
# 使用官方镜像
FROM ubuntu:20.04

# 使用特定版本
FROM python:3.9.18

# 使用轻量级镜像
FROM alpine:3.18

# 多阶段构建的第一阶段
FROM golang:1.21 AS builder

# scratch（空镜像，用于构建最小镜像）
FROM scratch
```

**最佳实践**：
```dockerfile
# ✅ 使用具体版本标签
FROM python:3.9.18

# ❌ 避免使用latest标签
FROM python:latest  # 不推荐，版本不固定
```

### 5.2.2 RUN - 执行命令

```dockerfile
# Shell形式
RUN apt-get update && apt-get install -y curl

# Exec形式
RUN ["/bin/bash", "-c", "echo hello"]

# 多个命令合并（减少层数）
RUN apt-get update && \
    apt-get install -y \
        curl \
        vim \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ❌ 避免每个命令一个RUN
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y vim
```

**构建缓存**：
```dockerfile
# 第一次构建
FROM ubuntu:20.04
RUN apt-get update          # 执行
RUN apt-get install -y curl # 执行

# 第二次构建（未修改）
FROM ubuntu:20.04
RUN apt-get update          # ✅ 使用缓存
RUN apt-get install -y curl # ✅ 使用缓存

# 修改后构建
FROM ubuntu:20.04
RUN apt-get update          # ✅ 使用缓存
RUN apt-get install -y vim  # ❌ 重新执行（缓存失效）
```

### 5.2.3 COPY - 复制文件

```dockerfile
# 复制单个文件
COPY app.py /app/

# 复制目录
COPY ./src /app/src

# 复制多个文件
COPY app.py config.py /app/

# 使用通配符
COPY *.py /app/

# 设置权限
COPY --chown=user:group app.py /app/

# 从构建阶段复制（多阶段构建）
COPY --from=builder /app/binary /app/
```

### 5.2.4 ADD - 高级复制

```dockerfile
# 基本复制（类似COPY）
ADD app.py /app/

# 自动解压tar文件
ADD archive.tar.gz /app/

# 从URL下载（不推荐，应该用RUN + wget/curl）
ADD https://example.com/file.txt /app/
```

**COPY vs ADD**：
```dockerfile
# ✅ 推荐：普通文件使用COPY
COPY app.py /app/

# ✅ 需要自动解压时使用ADD
ADD archive.tar.gz /app/

# ❌ 避免：从URL下载使用ADD
# 应该用RUN + wget
RUN wget https://example.com/file.txt -O /app/file.txt
```

### 5.2.5 WORKDIR - 工作目录

```dockerfile
# 设置工作目录
WORKDIR /app

# 相对路径（相对于上一个WORKDIR）
WORKDIR /app
WORKDIR src    # 实际路径: /app/src

# 自动创建目录
WORKDIR /path/that/does/not/exist  # 会自动创建
```

**最佳实践**：
```dockerfile
# ✅ 使用WORKDIR
WORKDIR /app
COPY app.py .
RUN python app.py

# ❌ 避免使用cd
RUN cd /app && \
    python app.py
```

### 5.2.6 ENV - 环境变量

```dockerfile
# 设置单个环境变量
ENV NODE_ENV production

# 设置多个环境变量
ENV NODE_ENV=production \
    PORT=3000 \
    DB_HOST=localhost

# 在后续指令中使用
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . $APP_HOME
```

### 5.2.7 EXPOSE - 暴露端口

```dockerfile
# 声明容器监听的端口
EXPOSE 80

# 多个端口
EXPOSE 80 443

# 指定协议
EXPOSE 80/tcp
EXPOSE 53/udp

# 注意：EXPOSE只是声明，实际映射需要-p参数
```

### 5.2.8 CMD - 默认命令

```dockerfile
# Exec形式（推荐）
CMD ["python", "app.py"]

# Shell形式
CMD python app.py

# 为ENTRYPOINT提供参数
ENTRYPOINT ["python"]
CMD ["app.py"]
```

**注意事项**：
```dockerfile
# Dockerfile中只有最后一个CMD生效
CMD ["echo", "first"]
CMD ["echo", "second"]  # 只有这个会执行

# docker run可以覆盖CMD
docker run my-image echo "override"
```

### 5.2.9 ENTRYPOINT - 入口点

```dockerfile
# Exec形式
ENTRYPOINT ["python", "app.py"]

# Shell形式
ENTRYPOINT python app.py

# 与CMD组合
ENTRYPOINT ["python"]
CMD ["app.py"]  # 默认参数

# docker run传递参数
docker run my-image script.py  # 执行: python script.py
```

**CMD vs ENTRYPOINT**：
```dockerfile
# 场景1: 可执行容器（推荐ENTRYPOINT）
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]

# 场景2: 灵活命令（推荐CMD）
CMD ["python", "app.py"]

# 场景3: 组合使用
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
```

### 5.2.10 ARG - 构建参数

```dockerfile
# 定义构建参数
ARG VERSION=1.0
ARG BUILD_DATE

# 使用构建参数
FROM python:${VERSION}
LABEL build_date=${BUILD_DATE}

# 构建时传递参数
# docker build --build-arg VERSION=3.9 --build-arg BUILD_DATE=2024-01-01 .
```

**ARG vs ENV**：
```dockerfile
# ARG: 只在构建时可用
ARG BUILD_ENV=dev
RUN echo $BUILD_ENV  # ✅ 可用

# ENV: 构建时和运行时都可用
ENV APP_ENV=production
RUN echo $APP_ENV    # ✅ 可用
# 容器运行时也可用
```

### 5.2.11 VOLUME - 数据卷

```dockerfile
# 声明挂载点
VOLUME /data

# 多个挂载点
VOLUME ["/var/log", "/var/db"]

# 实际使用时仍需-v参数
# docker run -v /host/data:/data my-image
```

### 5.2.12 USER - 运行用户

```dockerfile
# 创建用户并切换
RUN useradd -m appuser
USER appuser

# 切换到特定UID
USER 1000

# 用户:组
USER appuser:appgroup

# 切换回root
USER root
```

### 5.2.13 LABEL - 元数据

```dockerfile
# 添加元数据
LABEL version="1.0"
LABEL description="My application"
LABEL maintainer="user@example.com"

# 多个标签
LABEL version="1.0" \
      description="My app" \
      maintainer="user@example.com"
```

## 5.3 构建上下文

### 5.3.1 理解构建上下文

```bash
# 构建命令
docker build -t my-image .
#                         ↑
#                    构建上下文路径

# 构建过程
1. Docker客户端打包构建上下文
2. 发送到Docker守护进程
3. 守护进程逐行执行Dockerfile
4. 生成最终镜像
```

### 5.3.2 优化构建上下文

**使用.dockerignore**：
```
# .dockerignore文件
node_modules
.git
*.log
.env
__pycache__
*.pyc
.DS_Store
```

**目录结构**：
```
project/
├── Dockerfile
├── .dockerignore
├── app.py
├── requirements.txt
├── node_modules/      # 被忽略
└── .git/              # 被忽略
```

## 5.4 多阶段构建

### 5.4.1 为什么需要多阶段构建？

**问题**：
```dockerfile
# 单阶段构建（镜像大）
FROM golang:1.21
WORKDIR /app
COPY . .
RUN go build -o myapp
CMD ["./myapp"]

# 结果：镜像包含整个Go工具链（~800MB）
```

**解决方案**：
```dockerfile
# 多阶段构建（镜像小）
# 阶段1: 编译
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o myapp

# 阶段2: 运行
FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/myapp .
CMD ["./myapp"]

# 结果：只包含可执行文件（~10MB）
```

### 5.4.2 多阶段构建示例

**Python应用**：
```dockerfile
# 构建阶段
FROM python:3.9 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app.py .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

**Node.js应用**：
```dockerfile
# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

**Java应用**：
```dockerfile
# 编译阶段
FROM maven:3.8-openjdk-17 AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package

# 运行阶段
FROM openjdk:17-jre-slim
WORKDIR /app
COPY --from=builder /app/target/app.jar .
CMD ["java", "-jar", "app.jar"]
```

### 5.4.3 指定构建目标

```bash
# 构建特定阶段
docker build --target builder -t my-app:builder .

# 用于调试
FROM golang:1.21 AS builder
# ... 构建代码 ...

FROM alpine:3.18 AS debug
COPY --from=builder /app/myapp .
RUN apk add --no-cache gdb
CMD ["gdb", "./myapp"]

FROM alpine:3.18 AS release
COPY --from=builder /app/myapp .
CMD ["./myapp"]

# 构建debug版本
docker build --target debug -t my-app:debug .

# 构建release版本
docker build --target release -t my-app:release .
```

## 5.5 镜像优化技巧

### 5.5.1 减少层数

```dockerfile
# ❌ 多个RUN（多层）
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y vim
RUN rm -rf /var/lib/apt/lists/*

# ✅ 合并RUN（单层）
RUN apt-get update && \
    apt-get install -y curl vim && \
    rm -rf /var/lib/apt/lists/*
```

### 5.5.2 使用轻量级基础镜像

```dockerfile
# 镜像大小对比
FROM ubuntu:20.04    # ~72MB
FROM debian:11-slim  # ~27MB
FROM alpine:3.18     # ~7MB
FROM scratch         # 0MB（空镜像）

# 推荐使用alpine
FROM python:3.9-alpine  # 比python:3.9小很多
```

### 5.5.3 清理缓存

```dockerfile
# ✅ 清理apt缓存
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# ✅ 清理pip缓存
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 清理apk缓存（Alpine）
RUN apk add --no-cache curl
```

### 5.5.4 利用构建缓存

```dockerfile
# ❌ 依赖变化导致后续全部重建
COPY . /app
RUN pip install -r requirements.txt

# ✅ 先复制依赖文件
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
# 代码变化不影响依赖安装缓存
```

### 5.5.5 .dockerignore优化

```
# .dockerignore
.git
.gitignore
README.md
.env
.vscode
.idea
node_modules
*.log
*.md
.DS_Store
```

## 5.6 实战示例

### 5.6.1 Flask Web应用

**app.py**：
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Docker!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**requirements.txt**：
```
Flask==2.3.0
```

**Dockerfile**：
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

# 暴露端口
EXPOSE 5000

# 非root用户运行
RUN useradd -m appuser
USER appuser

# 启动应用
CMD ["python", "app.py"]
```

**构建和运行**：
```bash
docker build -t flask-app .
docker run -d -p 5000:5000 flask-app
curl http://localhost:5000
```

### 5.6.2 Node.js应用

**Dockerfile**：
```dockerfile
# 多阶段构建
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
USER node
CMD ["node", "server.js"]
```

### 5.6.3 Go应用

**Dockerfile**：
```dockerfile
# 构建阶段
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# 运行阶段
FROM scratch
COPY --from=builder /app/main /main
EXPOSE 8080
ENTRYPOINT ["/main"]
```

## 5.7 构建命令详解

### 5.7.1 基本构建

```bash
# 基本构建
docker build .

# 指定标签
docker build -t my-app:1.0 .

# 多个标签
docker build -t my-app:1.0 -t my-app:latest .

# 指定Dockerfile
docker build -f Dockerfile.dev -t my-app:dev .
```

### 5.7.2 构建参数

```bash
# 传递构建参数
docker build --build-arg VERSION=1.0 .

# 多个参数
docker build \
  --build-arg ENV=production \
  --build-arg PORT=8080 \
  -t my-app .
```

### 5.7.3 构建选项

```bash
# 不使用缓存
docker build --no-cache -t my-app .

# 强制删除中间容器
docker build --rm -t my-app .

# 设置内存限制
docker build --memory 2g -t my-app .

# 指定目标平台
docker build --platform linux/amd64 -t my-app .
```

## 5.8 本章总结

### 核心知识点

✅ **Dockerfile基础**
- Dockerfile结构
- 基本指令
- 指令最佳实践

✅ **常用指令**
- FROM, RUN, COPY, ADD
- WORKDIR, ENV, EXPOSE
- CMD, ENTRYPOINT
- ARG, VOLUME, USER, LABEL

✅ **构建上下文**
- 构建过程
- .dockerignore
- 上下文优化

✅ **多阶段构建**
- 原理和优势
- 实战示例
- 构建目标

✅ **镜像优化**
- 减少层数
- 轻量级基础镜像
- 清理缓存
- 利用构建缓存

### 下一章预告

在[第6章：Docker数据管理](../chapter06-data-management/README.md)中，我们将学习：
- 数据卷（Volumes）
- 绑定挂载（Bind Mounts）
- 数据备份和恢复
- 数据共享策略

---

**掌握Dockerfile，构建高效镜像！🚀**
