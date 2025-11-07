# 第3章 Pod详解和实践

## 3.1 Pod深入理解

### 3.1.1 Pod的本质

Pod是Kubernetes中最小的可部署单元，代表集群中运行的一个进程实例。理解Pod的本质对于掌握Kubernetes至关重要。

#### Pod的设计理念

1. **共享网络命名空间**：Pod中的所有容器共享同一个IP地址和端口空间
2. **共享存储**：Pod中的容器可以共享存储卷
3. **紧密关联**：Pod中的容器应该紧密协作，共同完成一个任务

#### Pod的生命周期

Pod有以下几种状态：
- **Pending**：Pod已被Kubernetes系统接受，但有一个或多个容器尚未创建
- **Running**：Pod已经绑定到节点，并且所有容器都已创建
- **Succeeded**：Pod中所有容器都已成功终止，并且不会重启
- **Failed**：Pod中所有容器都已终止，至少有一个容器异常终止
- **Unknown**：由于某些原因无法获取Pod的状态

### 3.1.2 Pod的网络模型

每个Pod都有一个唯一的IP地址，这个IP地址在Pod的生命周期内保持不变。

#### 网络特性

1. **Pod内部通信**：Pod内的容器通过localhost通信
2. **Pod间通信**：所有Pod都在一个可以直接连通的扁平网络中
3. **Pod与Service通信**：通过Service实现负载均衡

```yaml
# 示例：多容器Pod
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: web
    image: nginx
    ports:
    - containerPort: 80
  - name: logger
    image: busybox
    command: ["/bin/sh", "-c"]
    args:
    - while true; do
        echo "$(date) INFO Web server is running" >> /var/log/web.log;
        sleep 10;
      done
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log
  volumes:
  - name: shared-logs
    emptyDir: {}
```

## 3.2 Pod的定义和配置

### 3.2.1 Pod的基本结构

Pod的定义包含以下几个主要部分：

1. **apiVersion**：API版本
2. **kind**：资源类型（Pod）
3. **metadata**：元数据（名称、标签、注解等）
4. **spec**：Pod的规格说明（容器、卷、网络等）

```yaml
# Pod定义的完整结构
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
  labels:
    app: web
    version: v1
  annotations:
    description: "This is an example pod"
spec:
  containers:
  - name: web-container
    image: nginx:1.21
    ports:
    - containerPort: 80
    env:
    - name: ENV
      value: "production"
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
  restartPolicy: Always
```

### 3.2.2 容器配置详解

#### 镜像和端口配置

```yaml
containers:
- name: app
  image: myapp:1.0
  imagePullPolicy: Always  # Always, Never, IfNotPresent
  ports:
  - containerPort: 8080
    protocol: TCP
    name: http
```

#### 环境变量配置

```yaml
env:
# 直接设置值
- name: DATABASE_URL
  value: "mysql://localhost:3306/mydb"

# 从ConfigMap引用
- name: CONFIG_VALUE
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: config-value

# 从Secret引用
- name: SECRET_PASSWORD
  valueFrom:
    secretKeyRef:
      name: app-secret
      key: password

# 从字段引用
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
```

#### 资源限制和请求

```yaml
resources:
  requests:  # 资源请求（调度依据）
    memory: "64Mi"
    cpu: "250m"
  limits:    # 资源限制（硬限制）
    memory: "128Mi"
    cpu: "500m"
```

### 3.2.3 存储卷配置

#### emptyDir卷

```yaml
volumes:
- name: temp-storage
  emptyDir: {}

containers:
- name: app
  volumeMounts:
  - name: temp-storage
    mountPath: /tmp/data
```

#### hostPath卷

```yaml
volumes:
- name: host-data
  hostPath:
    path: /data
    type: Directory

containers:
- name: app
  volumeMounts:
  - name: host-data
    mountPath: /app/data
```

#### persistentVolumeClaim卷

```yaml
volumes:
- name: persistent-storage
  persistentVolumeClaim:
    claimName: my-pvc

containers:
- name: app
  volumeMounts:
  - name: persistent-storage
    mountPath: /app/data
```

## 3.3 Pod的高级特性

### 3.3.1 Init Containers（初始化容器）

Init Containers在应用容器启动之前运行，用于执行初始化任务。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  containers:
  - name: app
    image: nginx
    ports:
    - containerPort: 80
  initContainers:
  - name: init-myservice
    image: busybox:1.28
    command: ['sh', '-c', 'until nslookup myservice; do echo waiting for myservice; sleep 2; done;']
  - name: init-mydb
    image: busybox:1.28
    command: ['sh', '-c', 'until nslookup mydb; do echo waiting for mydb; sleep 2; done;']
```

### 3.3.2 Sidecar模式

Sidecar容器与主应用容器一起运行，提供辅助功能。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
spec:
  containers:
  # 主应用容器
  - name: app
    image: nginx
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  # 日志收集Sidecar容器
  - name: log-collector
    image: fluentd
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  volumes:
  - name: shared-logs
    emptyDir: {}
```

### 3.3.3 生命周期钩子

#### PostStart钩子

在容器创建后立即执行：

```yaml
lifecycle:
  postStart:
    exec:
      command: ["/bin/sh", "-c", "echo Hello from the postStart handler > /usr/share/message"]
```

#### PreStop钩子

在容器终止前执行：

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "nginx -s quit; while killall -0 nginx; do sleep 1; done"]
```

### 3.3.4 健康检查

#### 存活探针（Liveness Probe）

检测容器是否正在运行：

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
```

#### 就绪探针（Readiness Probe）

检测容器是否准备好接收流量：

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

#### 启动探针（Startup Probe）

检测应用是否已启动：

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

## 3.4 Pod的管理和操作

### 3.4.1 Pod的基本操作

#### 创建Pod

```bash
# 从YAML文件创建
kubectl apply -f pod.yaml

# 直接运行
kubectl run nginx --image=nginx --port=80
```

#### 查看Pod

```bash
# 查看所有Pod
kubectl get pods

# 查看详细信息
kubectl describe pod <pod-name>

# 查看Pod日志
kubectl logs <pod-name>

# 进入Pod容器
kubectl exec -it <pod-name> -- /bin/bash
```

#### 删除Pod

```bash
# 删除指定Pod
kubectl delete pod <pod-name>

# 从文件删除
kubectl delete -f pod.yaml
```

### 3.4.2 Pod的调试技巧

#### 查看Pod状态

```bash
# 查看Pod状态详细信息
kubectl get pod <pod-name> -o wide

# 查看Pod的YAML定义
kubectl get pod <pod-name> -o yaml

# 查看Pod事件
kubectl describe pod <pod-name>
```

#### 查看容器日志

```bash
# 查看当前日志
kubectl logs <pod-name>

# 查看历史日志
kubectl logs <pod-name> --previous

# 实时查看日志
kubectl logs -f <pod-name>

# 查看特定容器日志（多容器Pod）
kubectl logs <pod-name> -c <container-name>
```

#### 进入容器调试

```bash
# 进入容器
kubectl exec -it <pod-name> -- /bin/bash

# 在容器中执行命令
kubectl exec <pod-name> -- ps aux

# 多容器Pod中指定容器
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash
```

## 3.5 实验：Pod实践操作

### 3.5.1 创建多容器Pod

创建一个包含Web服务器和日志收集器的Pod：

```yaml
# multi-container-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-logger-pod
  labels:
    app: web-logger
spec:
  containers:
  - name: web
    image: nginx:1.21
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  - name: logger
    image: busybox
    command: ["/bin/sh", "-c"]
    args:
    - while true; do
        echo "$(date): Access log entry" >> /var/log/shared/access.log;
        sleep 30;
      done
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/shared
  volumes:
  - name: shared-logs
    emptyDir: {}
```

应用配置并验证：

```bash
# 创建Pod
kubectl apply -f multi-container-pod.yaml

# 查看Pod状态
kubectl get pods

# 查看日志
kubectl logs web-logger-pod -c web
kubectl logs web-logger-pod -c logger

# 进入容器检查共享卷
kubectl exec -it web-logger-pod -c web -- ls /var/log/nginx
kubectl exec -it web-logger-pod -c logger -- cat /var/log/shared/access.log
```

### 3.5.2 配置健康检查

创建带健康检查的Pod：

```yaml
# health-check-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: health-check-pod
spec:
  containers:
  - name: app
    image: nginx:1.21
    ports:
    - containerPort: 80
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

应用配置并观察：

```bash
# 创建Pod
kubectl apply -f health-check-pod.yaml

# 观察Pod状态
kubectl get pods -w

# 查看探针状态
kubectl describe pod health-check-pod
```

### 3.5.3 使用Init Containers

创建使用初始化容器的Pod：

```yaml
# init-container-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-container-pod
spec:
  containers:
  - name: app
    image: nginx:1.21
    ports:
    - containerPort: 80
  initContainers:
  - name: init-config
    image: busybox
    command: ['sh', '-c', 'echo "App is starting at $(date)" > /work-dir/config.txt']
    volumeMounts:
    - name: workdir
      mountPath: /work-dir
  volumes:
  - name: workdir
    emptyDir: {}
```

应用配置并验证：

```bash
# 创建Pod
kubectl apply -f init-container-pod.yaml

# 查看Pod状态
kubectl get pods

# 检查初始化容器是否完成
kubectl describe pod init-container-pod

# 进入主容器查看初始化结果
kubectl exec -it init-container-pod -- cat /work-dir/config.txt
```

## 3.6 Pod故障排除

### 3.6.1 常见问题诊断

#### Pod处于Pending状态

```bash
# 查看详细信息
kubectl describe pod <pod-name>

# 可能的原因：
# 1. 资源不足
# 2. 节点选择器不匹配
# 3. 持久卷绑定失败
# 4. 镜像拉取失败
```

#### Pod处于CrashLoopBackOff状态

```bash
# 查看日志
kubectl logs <pod-name> --previous

# 进入容器调试
kubectl exec -it <pod-name> -- /bin/bash

# 检查资源限制
kubectl describe pod <pod-name>
```

#### 镜像拉取失败

```bash
# 检查镜像名称和标签
kubectl describe pod <pod-name>

# 手动拉取镜像测试
docker pull <image-name>:<tag>
```

### 3.6.2 调试工具和技巧

#### 使用临时容器调试

```bash
# 为现有Pod添加调试容器
kubectl debug <pod-name> -it --image=busybox --target=<container-name>
```

#### 端口转发调试

```bash
# 将本地端口转发到Pod端口
kubectl port-forward <pod-name> 8080:80
```

#### 复制文件进行调试

```bash
# 将文件复制到Pod
kubectl cp <local-file> <pod-name>:<pod-path>

# 从Pod复制文件
kubectl cp <pod-name>:<pod-path> <local-file>
```

## 3.7 小结

本章我们深入学习了Pod的相关知识：
- Pod的本质和设计理念
- Pod的定义和配置方法
- Pod的高级特性，包括Init Containers、Sidecar模式、生命周期钩子和健康检查
- Pod的管理和操作方法
- 通过实验加深了对Pod的理解
- Pod故障排除的方法和技巧

下一章我们将学习控制器的概念，包括Deployment、StatefulSet、DaemonSet等，它们用于管理Pod的生命周期。