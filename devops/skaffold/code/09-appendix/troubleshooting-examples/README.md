# 故障排除示例集

## 概述

这个示例集包含了各种常见的Skaffold故障场景及其解决方案，帮助您快速诊断和解决问题。

## 目录结构

```
troubleshooting-examples/
├── README.md
├── build-issues/              # 构建问题
│   ├── dockerfile-errors/     # Dockerfile错误
│   ├── network-problems/      # 网络问题
│   └── permission-issues/     # 权限问题
├── deploy-issues/            # 部署问题
│   ├── kubectl-errors/       # kubectl错误
│   ├── helm-problems/         # Helm问题
│   └── resource-conflicts/    # 资源冲突
├── sync-issues/              # 同步问题
│   ├── file-sync-failures/    # 文件同步失败
│   └── port-forwarding/      # 端口转发问题
└── performance-issues/       # 性能问题
    ├── slow-builds/          # 构建缓慢
    └── memory-usage/         # 内存使用问题
```

## 快速开始

### 1. 模拟问题场景

```bash
# 进入特定问题目录
cd build-issues/dockerfile-errors

# 运行问题场景
skaffold dev

# 观察错误信息并查看解决方案
cat solution.md
```

### 2. 使用诊断工具

```bash
# 运行详细诊断
skaffold diagnose -v debug

# 检查配置语法
skaffold schema

# 分析构建日志
skaffold build --file-output=build.log
```

## 问题分类和解决方案

### 构建问题 (Build Issues)

#### 1. Dockerfile语法错误

**问题现象：**
```
Error: Dockerfile parse error line 5: unknown instruction: RUNADD
```

**解决方案：**
```dockerfile
# 错误示例
FROM node:16
RUNADD package.json /app/

# 正确示例
FROM node:16
COPY package.json /app/
RUN npm install
```

**诊断命令：**
```bash
# 验证Dockerfile语法
docker build --no-cache -t test .

# 使用hadolint检查
hadolint Dockerfile
```

#### 2. 网络连接问题

**问题现象：**
```
Error: Get "https://registry-1.docker.io/v2/": dial tcp: lookup registry-1.docker.io: no such host
```

**解决方案：**
```bash
# 检查网络连接
ping registry-1.docker.io

# 配置Docker镜像加速器
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": ["https://mirror.ccs.tencentyun.com"]
}
EOF

# 重启Docker服务
sudo systemctl restart docker
```

#### 3. 权限问题

**问题现象：**
```
Error: permission denied while trying to connect to the Docker daemon socket
```

**解决方案：**
```bash
# 将用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或重启会话
newgrp docker

# 验证权限
docker ps
```

### 部署问题 (Deploy Issues)

#### 1. kubectl配置错误

**问题现象：**
```
Error: the server doesn't have a resource type "deployments"
```

**解决方案：**
```bash
# 检查kubectl配置
kubectl config view

# 验证集群连接
kubectl cluster-info

# 检查API版本兼容性
kubectl api-versions | grep apps

# 更新配置使用正确的API版本
# k8s/deployment.yaml
apiVersion: apps/v1  # 而不是extensions/v1beta1
kind: Deployment
```

#### 2. Helm版本兼容性

**问题现象：**
```
Error: rendered manifests contain a resource that already exists
```

**解决方案：**
```yaml
# skaffold.yaml - Helm配置优化
deploy:
  helm:
    releases:
      - name: my-app
        chartPath: charts/my-app
        # 启用资源清理
        recreatePods: true
        force: false
        # 处理资源冲突
        skipCRDs: false
        # 等待资源就绪
        wait: true
        timeout: 10m
```

#### 3. 资源配额限制

**问题现象：**
```
Error: pods "my-app" is forbidden: exceeded quota: resource-quota
```

**解决方案：**
```yaml
# 优化资源请求
# k8s/deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```

### 同步问题 (Sync Issues)

#### 1. 文件同步失败

**问题现象：**
```
Syncing 1 files for gcr.io/k8s-skaffold/example:latest
Watching for changes...
Error: sync failed: copying files: didn't sync any files
```

**解决方案：**
```yaml
# 优化同步配置
build:
  artifacts:
    - image: my-app
      sync:
        manual:
          - src: "src/**/*.js"
            dest: /app
            strip: "src/"
        # 启用自动推断
        auto: true
        # 明确排除不需要同步的文件
        infer:
          - "**/*.js"
          - "**/*.css"
        ignore:
          - "node_modules/**"
          - ".git/**"
```

#### 2. 端口转发问题

**问题现象：**
```
Error: unable to forward port because pod is not running. Current status=Failed
```

**解决方案：**
```yaml
# 配置健康检查
portForward:
  - resourceType: deployment
    resourceName: my-app
    port: 8080
    localPort: 9000
    # 等待Pod就绪
    namespace: default

# 添加就绪探针
# k8s/deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: app
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 性能问题 (Performance Issues)

#### 1. 构建缓慢

**问题现象：**
```
Building takes more than 5 minutes for simple changes
```

**解决方案：**
```yaml
# 优化构建配置
build:
  # 启用构建缓存
  local:
    useBuildkit: true
    push: false
    # 并行构建
    concurrency: 3
  
  artifacts:
    - image: my-app
      docker:
        dockerfile: Dockerfile
        # 使用多阶段构建
        target: production
        # 构建缓存配置
        cacheFrom:
          - my-app:latest
        cacheTo:
          - type: registry
            params:
              mode: max
```

#### 2. 内存使用过高

**问题现象：**
```
Docker daemon runs out of memory during build
```

**解决方案：**
```bash
# 调整Docker内存限制
# /etc/docker/daemon.json
{
  "default-shm-size": "1g",
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# 清理Docker缓存
docker system prune -a

# 使用更轻量的基础镜像
# Dockerfile
FROM node:16-alpine  # 而不是node:16
```

## 诊断工具和技巧

### 1. 详细日志分析

```bash
# 启用所有组件的详细日志
export SKAFFOLD_VERBOSITY=debug
skaffold dev

# 或者使用命令行参数
skaffold dev -v debug --timestamps=true

# 将日志输出到文件
skaffold dev 2>&1 | tee skaffold.log
```

### 2. RPC事件监控

```bash
# 启用RPC端口
skaffold dev --rpc-http-port=50051

# 监控事件流
curl -s http://localhost:50051/v1/events | jq '.'

# 实时监控
watch -n 1 'curl -s http://localhost:50051/v1/events | jq \'.events[-1]\''
```

### 3. 性能分析

```bash
# 构建性能分析
skaffold build --profile=performance --file-output=build.json

# 分析构建时间
jq '.builds[] | {image: .imageName, duration: .duration}' build.json

# 部署性能分析
skaffold deploy --dry-run --render-only
```

### 4. 网络诊断

```bash
# 检查网络连接
nslookup registry-1.docker.io

# 测试镜像拉取速度
time docker pull node:16-alpine

# 检查代理设置
echo $HTTP_PROXY $HTTPS_PROXY
```

## 预防措施

### 1. 配置验证

```bash
# 验证skaffold.yaml语法
skaffold schema

# 检查配置兼容性
skaffold fix --dry-run

# 预渲染Kubernetes清单
skaffold render --output=rendered.yaml
```

### 2. 健康检查集成

```yaml
# 集成健康检查
test:
  - image: "*"
    custom:
      - command: "curl -f http://localhost:8080/health"
        timeout: 30s
      - command: "kubectl rollout status deployment/my-app --timeout=300s"
```

### 3. 监控和告警

```yaml
# 集成监控
profiles:
  - name: monitoring
    patches:
      - op: add
        path: /deploy/kubectl/manifests
        value:
          - k8s/monitoring/service-monitor.yaml
          - k8s/monitoring/prometheus-rule.yaml
```

这个故障排除示例集提供了从基础到高级的各种问题解决方案，帮助您快速诊断和解决Skaffold使用过程中遇到的各种问题。