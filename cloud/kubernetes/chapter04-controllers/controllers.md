# 第4章 控制器详解（Deployment、StatefulSet、DaemonSet等）

## 4.1 控制器概述

### 4.1.1 控制器的作用

控制器是Kubernetes中负责维护期望状态的组件。它们通过持续监控集群状态并进行必要的更改来确保集群的实际状态与用户定义的期望状态相匹配。

控制器的核心功能包括：
- 管理Pod的生命周期
- 维持期望的副本数量
- 执行滚动更新和回滚
- 处理节点故障

### 4.1.2 控制器的工作原理

控制器通过以下方式工作：
1. **观察（Observe）**：监控集群中资源的实际状态
2. **比较（Diff）**：将实际状态与期望状态进行比较
3. **协调（Reconcile）**：执行必要的操作使实际状态接近期望状态

这个过程被称为控制循环（Control Loop）或调和循环（Reconciliation Loop）。

## 4.2 Deployment控制器

Deployment是Kubernetes中最常用的控制器，用于管理无状态应用的部署。

### 4.2.1 Deployment的特点

- **声明式更新**：通过声明期望状态来管理应用
- **滚动更新**：支持零停机时间的应用更新
- **回滚功能**：可以回滚到之前的版本
- **扩缩容**：支持动态调整副本数量
- **自我修复**：自动替换不健康的Pod

### 4.2.2 Deployment的定义

```yaml
# deployment-example.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

### 4.2.3 Deployment的操作

#### 创建Deployment

```bash
# 从YAML文件创建
kubectl apply -f deployment-example.yaml

# 直接创建
kubectl create deployment nginx --image=nginx:1.21
```

#### 查看Deployment状态

```bash
# 查看Deployment
kubectl get deployments

# 查看详细信息
kubectl describe deployment nginx-deployment

# 查看相关的ReplicaSet
kubectl get rs

# 查看Pod
kubectl get pods -l app=nginx
```

#### 更新Deployment

```bash
# 更新镜像
kubectl set image deployment/nginx-deployment nginx=nginx:1.22

# 编辑Deployment
kubectl edit deployment/nginx-deployment

# 扩缩容
kubectl scale deployment/nginx-deployment --replicas=5
```

#### 回滚Deployment

```bash
# 查看更新历史
kubectl rollout history deployment/nginx-deployment

# 回滚到上一个版本
kubectl rollout undo deployment/nginx-deployment

# 回滚到指定版本
kubectl rollout undo deployment/nginx-deployment --to-revision=2
```

### 4.2.4 Deployment的更新策略

#### 滚动更新策略

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1      # 最大不可用Pod数
      maxSurge: 1           # 最大超出期望Pod数
```

#### 重新创建策略

```yaml
spec:
  strategy:
    type: Recreate
```

### 4.2.5 Deployment的最佳实践

1. **设置资源限制**：
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
```

2. **配置健康检查**：
```yaml
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

## 4.3 StatefulSet控制器

StatefulSet用于管理有状态应用，为每个Pod提供稳定的网络标识和持久存储。

### 4.3.1 StatefulSet的特点

- **稳定的网络标识**：每个Pod有唯一的、稳定的网络标识
- **稳定的持久存储**：Pod重新调度时保留存储
- **有序部署和删除**：按顺序创建和删除Pod
- **有序滚动更新**：按顺序更新Pod

### 4.3.2 StatefulSet的定义

```yaml
# statefulset-example.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx
  serviceName: "nginx"
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

### 4.3.3 StatefulSet的操作

#### 创建StatefulSet

```bash
# 创建Headless Service（StatefulSet必需）
kubectl apply -f headless-service.yaml

# 创建StatefulSet
kubectl apply -f statefulset-example.yaml
```

#### 查看StatefulSet状态

```bash
# 查看StatefulSet
kubectl get statefulsets

# 查看Pod（注意命名规律）
kubectl get pods -l app=nginx

# 查看PVC
kubectl get pvc
```

#### 更新StatefulSet

```bash
# 更新镜像
kubectl patch statefulset web -p '{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.22"}]}}}}'

# 扩缩容
kubectl scale statefulset web --replicas=5
```

### 4.3.4 StatefulSet的网络标识

```yaml
# Headless Service定义
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None  # Headless Service
  selector:
    app: nginx
```

## 4.4 DaemonSet控制器

DaemonSet确保所有（或部分）节点上运行一个Pod副本，常用于日志收集、监控等系统级任务。

### 4.4.1 DaemonSet的特点

- **节点全覆盖**：在每个节点上运行一个Pod副本
- **自动调度**：新节点加入时自动调度Pod
- **节点选择**：可以选择在特定节点上运行

### 4.4.2 DaemonSet的定义

```yaml
# daemonset-example.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-elasticsearch
  namespace: kube-system
  labels:
    k8s-app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations:
      # 允许在master节点上调度
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

### 4.4.3 DaemonSet的操作

#### 创建DaemonSet

```bash
kubectl apply -f daemonset-example.yaml
```

#### 查看DaemonSet状态

```bash
# 查看DaemonSet
kubectl get daemonsets -n kube-system

# 查看Pod
kubectl get pods -n kube-system -l name=fluentd-elasticsearch
```

#### 更新DaemonSet

```bash
# 更新镜像
kubectl set image daemonset/fluentd-elasticsearch fluentd-elasticsearch=quay.io/fluentd_elasticsearch/fluentd:v3.0.0 -n kube-system
```

## 4.5 Job和CronJob控制器

### 4.5.1 Job控制器

Job用于运行一次性任务，确保指定数量的Pod成功完成。

```yaml
# job-example.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl
        command: ["perl",  "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4
```

#### Job的操作

```bash
# 创建Job
kubectl apply -f job-example.yaml

# 查看Job状态
kubectl get jobs

# 查看Pod
kubectl get pods -l job-name=pi

# 查看日志
kubectl logs -l job-name=pi
```

### 4.5.2 CronJob控制器

CronJob用于按计划运行Job，类似于Linux的cron。

```yaml
# cronjob-example.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            imagePullPolicy: IfNotPresent
            command:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure
```

#### CronJob的操作

```bash
# 创建CronJob
kubectl apply -f cronjob-example.yaml

# 查看CronJob
kubectl get cronjobs

# 查看Job历史
kubectl get jobs --watch
```

## 4.6 控制器的高级特性

### 4.6.1 亲和性和反亲和性

#### 节点亲和性

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/e2e-az-name
          operator: In
          values:
          - e2e-az1
          - e2e-az2
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 1
      preference:
        matchExpressions:
        - key: another-node-label-key
          operator: In
          values:
          - another-node-label-value
```

#### Pod亲和性

```yaml
affinity:
  podAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: security
          operator: In
          values:
          - S1
      topologyKey: topology.kubernetes.io/zone
```

#### Pod反亲和性

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - web
        topologyKey: kubernetes.io/hostname
```

### 4.6.2 污点和容忍

#### 为节点添加污点

```bash
# 添加污点
kubectl taint nodes node1 key=value:NoSchedule

# 移除污点
kubectl taint nodes node1 key=value:NoSchedule-
```

#### 在Pod中配置容忍

```yaml
tolerations:
- key: "key"
  operator: "Equal"
  value: "value"
  effect: "NoSchedule"
- key: "key"
  operator: "Exists"
  effect: "NoSchedule"
```

## 4.7 实验：控制器实践操作

### 4.7.1 Deployment实践

创建一个完整的Deployment应用：

```yaml
# complete-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: complete-app
  labels:
    app: complete-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: complete-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    metadata:
      labels:
        app: complete-app
    spec:
      containers:
      - name: app
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
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
---
apiVersion: v1
kind: Service
metadata:
  name: complete-app-service
spec:
  selector:
    app: complete-app
  ports:
  - port: 80
    targetPort: 80
  type: NodePort
```

操作步骤：

```bash
# 1. 创建Deployment和Service
kubectl apply -f complete-deployment.yaml

# 2. 查看状态
kubectl get deployments
kubectl get pods
kubectl get services

# 3. 执行滚动更新
kubectl set image deployment/complete-app app=nginx:1.22

# 4. 观察更新过程
kubectl get pods -w

# 5. 回滚更新
kubectl rollout undo deployment/complete-app

# 6. 查看更新历史
kubectl rollout history deployment/complete-app
```

### 4.7.2 StatefulSet实践

创建一个简单的StatefulSet应用：

```yaml
# statefulset-practice.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-statefulset
  labels:
    app: nginx-statefulset
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
  selector:
    app: nginx-statefulset
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-statefulset
spec:
  selector:
    matchLabels:
      app: nginx-statefulset
  serviceName: "nginx-statefulset"
  replicas: 2
  template:
    metadata:
      labels:
        app: nginx-statefulset
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

操作步骤：

```bash
# 1. 创建StatefulSet
kubectl apply -f statefulset-practice.yaml

# 2. 查看状态
kubectl get statefulsets
kubectl get pods
kubectl get pvc

# 3. 验证网络标识
kubectl run -it --rm debug --image=busybox -- sh
# 在容器内执行
nslookup web-statefulset-0.nginx-statefulset
nslookup web-statefulset-1.nginx-statefulset

# 4. 扩缩容
kubectl scale statefulset web-statefulset --replicas=4
```

## 4.8 控制器故障排除

### 4.8.1 常见问题诊断

#### Deployment更新失败

```bash
# 查看Deployment状态
kubectl describe deployment <deployment-name>

# 查看ReplicaSet状态
kubectl get rs

# 查看Pod状态
kubectl get pods -l app=<app-name>

# 查看Pod详细信息和事件
kubectl describe pod <pod-name>
```

#### StatefulSet Pod卡住

```bash
# 检查Pod状态
kubectl describe pod <statefulset-pod-name>

# 检查PVC状态
kubectl get pvc

# 检查PV状态
kubectl get pv
```

#### DaemonSet未在所有节点上运行

```bash
# 查看DaemonSet状态
kubectl describe daemonset <daemonset-name>

# 检查节点污点
kubectl describe nodes

# 检查Pod调度情况
kubectl get pods -o wide
```

### 4.8.2 调试技巧

#### 查看控制器事件

```bash
# 查看Deployment事件
kubectl describe deployment <deployment-name>

# 查看控制器管理器日志
kubectl logs -n kube-system -l component=kube-controller-manager
```

#### 强制重启控制器

```bash
# 删除Pod触发重建
kubectl delete pod <pod-name>

# 重新应用配置
kubectl apply -f <controller-config.yaml>
```

## 4.9 小结

本章我们详细学习了Kubernetes中的各种控制器：
- Deployment：用于管理无状态应用
- StatefulSet：用于管理有状态应用
- DaemonSet：确保每个节点运行一个Pod副本
- Job和CronJob：用于运行一次性任务和定时任务
- 控制器的高级特性：亲和性、污点和容忍
- 通过实验加深了对控制器的理解
- 控制器故障排除的方法和技巧

下一章我们将学习Kubernetes中的服务发现和网络机制，这是连接应用组件的关键。