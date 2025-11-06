# 第11章：高级调度和资源管理

## 本章概要
本章将深入探讨 Kubernetes 的高级调度机制和资源管理策略。我们将学习如何使用各种调度器特性来优化工作负载分布，包括亲和性和反亲和性、污点和容忍、节点选择器等。同时，我们还将了解资源配额、限制范围和优先级类等资源管理机制，以确保集群资源的合理分配和高效利用。

## 目标
- 掌握 Kubernetes 高级调度机制
- 学会使用亲和性和反亲和性优化调度
- 理解污点和容忍机制的应用场景
- 掌握资源配额和限制范围的配置方法
- 学会使用优先级类和抢占机制

## 11.1 调度器概述

### 11.1.1 调度过程
Kubernetes 调度器通过以下步骤将 Pod 调度到合适的节点：

1. **过滤（Filtering）**：根据资源需求、节点标签、污点等条件筛选出合适的节点
2. **打分（Scoring）**：对筛选出的节点进行打分，选择最优节点
3. **绑定（Binding）**：将 Pod 绑定到选中的节点

### 11.1.2 调度器架构
Kubernetes 调度器采用插件化架构，主要包括：
- **调度队列**：存储待调度的 Pod
- **过滤插件**：实现节点筛选逻辑
- **打分插件**：实现节点评分逻辑
- **绑定插件**：实现 Pod 绑定逻辑

## 11.2 节点选择器（Node Selector）

### 11.2.1 基本用法
节点选择器是最简单的节点选择机制，通过匹配节点标签来选择节点。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
  nodeSelector:
    disktype: ssd
    environment: production
```

### 11.2.2 节点标签管理
```bash
# 为节点添加标签
kubectl label nodes <node-name> disktype=ssd environment=production

# 查看节点标签
kubectl get nodes --show-labels

# 删除节点标签
kubectl label nodes <node-name> disktype-
```

## 11.3 亲和性和反亲和性

### 11.3.1 节点亲和性（Node Affinity）
节点亲和性允许更灵活的节点选择策略。

#### requiredDuringSchedulingIgnoredDuringExecution
硬性要求，必须满足条件才能调度：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-node-affinity
spec:
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
  containers:
  - name: with-node-affinity
    image: k8s.gcr.io/pause:2.0
```

#### preferredDuringSchedulingIgnoredDuringExecution
软性偏好，尽量满足条件：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-node-affinity
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: another-node-label-key
            operator: In
            values:
            - another-node-label-value
  containers:
  - name: with-node-affinity
    image: k8s.gcr.io/pause:2.0
```

### 11.3.2 Pod 亲和性和反亲和性
Pod 亲和性控制 Pod 之间的调度关系。

#### Pod 亲和性示例
将 Pod 调度到与特定 Pod 相同拓扑域的节点上：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-pod-affinity
spec:
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
  containers:
  - name: with-pod-affinity
    image: k8s.gcr.io/pause:2.0
```

#### Pod 反亲和性示例
将 Pod 调度到与特定 Pod 不同拓扑域的节点上：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-pod-anti-affinity
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: security
              operator: In
              values:
              - S2
          topologyKey: topology.kubernetes.io/zone
  containers:
  - name: with-pod-anti-affinity
    image: k8s.gcr.io/pause:2.0
```

## 11.4 污点和容忍（Taints and Tolerations）

### 11.4.1 污点（Taints）
污点应用于节点，阻止 Pod 调度到该节点，除非 Pod 有相应的容忍。

#### 添加污点
```bash
# 为节点添加污点
kubectl taint nodes node1 key1=value1:NoSchedule

# 为节点添加多个污点
kubectl taint nodes node1 key1=value1:NoSchedule key2=value2:PreferNoSchedule
```

#### 污点效果类型
1. **NoSchedule**：不允许调度（硬性要求）
2. **PreferNoSchedule**：尽量不调度（软性偏好）
3. **NoExecute**：不仅不允许调度，还会驱逐已存在的不匹配 Pod

### 11.4.2 容忍（Tolerations）
容忍应用于 Pod，允许 Pod 调度到有特定污点的节点。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-toleration
spec:
  tolerations:
  - key: "key1"
    operator: "Equal"
    value: "value1"
    effect: "NoSchedule"
  containers:
  - name: with-toleration
    image: nginx
```

#### 容忍所有污点
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tolerate-all
spec:
  tolerations:
  - operator: "Exists"
  containers:
  - name: tolerate-all
    image: nginx
```

### 11.4.3 应用场景
1. **专用节点**：为特定应用保留节点资源
2. **硬件隔离**：将特殊硬件节点分配给特定工作负载
3. **维护节点**：在节点维护期间阻止新 Pod 调度

## 11.5 资源管理

### 11.5.1 资源请求和限制
通过资源请求和限制控制 Pod 的资源使用：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: demo
    image: nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### 11.5.2 资源配额（Resource Quota）
资源配额限制命名空间中的资源使用总量：

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: mem-cpu-demo
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    pods: "10"
```

#### 对象配额
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: object-counts
spec:
  hard:
    configmaps: "10"
    persistentvolumeclaims: "4"
    replicationcontrollers: "20"
    secrets: "10"
    services: "10"
```

### 11.5.3 限制范围（Limit Range）
限制范围设置命名空间中对象的默认资源请求和限制：

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: mem-limit-range
spec:
  limits:
  - default:
      memory: 512Mi
    defaultRequest:
      memory: 256Mi
    type: Container
```

#### 多种资源类型的限制范围
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: example-limit-range
spec:
  limits:
  - default:
      cpu: 200m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 256Mi
    max:
      cpu: 1
      memory: 1Gi
    min:
      cpu: 50m
      memory: 100Mi
    type: Container
  - max:
      storage: 10Gi
    min:
      storage: 1Gi
    type: PersistentVolumeClaim
```

## 11.6 优先级类（Priority Class）

### 11.6.1 优先级类定义
优先级类定义 Pod 的优先级，影响调度和抢占行为：

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "This priority class should be used for high priority service pods only."
```

### 11.6.2 使用优先级类
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: high-priority-pod
spec:
  priorityClassName: high-priority
  containers:
  - name: high-priority-pod
    image: nginx
```

### 11.6.3 抢占机制
当高优先级 Pod 无法调度时，调度器会抢占（驱逐）低优先级 Pod 为其腾出资源：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: preempting-pod
spec:
  priorityClassName: high-priority
  containers:
  - name: preempting-pod
    image: nginx
    resources:
      requests:
        cpu: 2
        memory: 4Gi
```

## 11.7 拓扑管理器（Topology Manager）

### 11.7.1 拓扑管理器策略
拓扑管理器确保 Pod 的资源分配符合 NUMA 拓扑要求：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: topo-manager-demo
spec:
  containers:
  - name: demo
    image: nginx
    resources:
      requests:
        cpu: 2
        memory: 1Gi
      limits:
        cpu: 2
        memory: 1Gi
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: demo
```

## 11.8 实验：高级调度配置实践

### 实验目标
通过实际操作掌握 Kubernetes 高级调度和资源管理技术，包括亲和性、污点容忍、资源配额等特性的配置和使用。

### 实验环境准备
1. 准备一个至少包含3个节点的 Kubernetes 集群
2. 为节点添加不同的标签

### 实验步骤

1. **节点标签配置**
```bash
# 为节点添加标签
kubectl label nodes node1 disktype=ssd environment=production
kubectl label nodes node2 disktype=hdd environment=development
kubectl label nodes node3 gpu=true environment=production
```

2. **污点和容忍配置**
```bash
# 为节点添加污点
kubectl taint nodes node3 gpu=true:NoSchedule

# 部署需要 GPU 的应用
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gpu-app
  template:
    metadata:
      labels:
        app: gpu-app
    spec:
      tolerations:
      - key: "gpu"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      containers:
      - name: gpu-container
        image: nginx
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
EOF
```

3. **亲和性配置**
```bash
# 部署生产环境应用，使用节点亲和性
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prod-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prod-app
  template:
    metadata:
      labels:
        app: prod-app
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: environment
                operator: In
                values:
                - production
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: prod-app
              topologyKey: kubernetes.io/hostname
      containers:
      - name: prod-container
        image: nginx
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
EOF
```

4. **资源配额配置**
```bash
# 创建命名空间
kubectl create namespace quota-demo

# 配置资源配额
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: demo-quota
  namespace: quota-demo
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    pods: "6"
EOF

# 配置限制范围
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: demo-limit-range
  namespace: quota-demo
spec:
  limits:
  - default:
      cpu: 200m
      memory: 256Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
EOF
```

5. **在配额命名空间中部署应用**
```bash
# 部署应用到配额命名空间
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quota-app
  namespace: quota-demo
spec:
  replicas: 3
  selector:
    matchLabels:
      app: quota-app
  template:
    metadata:
      labels:
        app: quota-app
    spec:
      containers:
      - name: quota-container
        image: nginx
        resources:
          requests:
            memory: "200Mi"
            cpu: "100m"
          limits:
            memory: "400Mi"
            cpu: "200m"
EOF
```

6. **验证调度和资源管理效果**
```bash
# 查看节点标签
kubectl get nodes --show-labels

# 查看节点污点
kubectl describe nodes | grep Taints

# 查看 Pod 调度情况
kubectl get pods -o wide

# 查看资源配额使用情况
kubectl get resourcequota -n quota-demo

# 查看限制范围
kubectl get limitrange -n quota-demo

# 查看 Pod 资源使用
kubectl describe pods -n quota-demo
```

## 11.9 故障排除

### 11.9.1 调度失败问题
1. **节点选择器不匹配**
```bash
# 查看 Pod 调度状态
kubectl describe pod <pod-name>

# 检查节点标签
kubectl get nodes --show-labels
```

2. **污点和容忍不匹配**
```bash
# 查看节点污点
kubectl describe nodes <node-name> | grep Taints

# 查看 Pod 容忍
kubectl describe pod <pod-name> | grep Tolerations
```

3. **资源不足**
```bash
# 查看节点资源使用
kubectl describe nodes <node-name>

# 查看命名空间资源配额
kubectl describe resourcequota -n <namespace>
```

### 11.9.2 亲和性配置问题
1. **标签选择器错误**
```bash
# 验证标签选择器
kubectl get pods --show-labels

# 检查亲和性配置
kubectl describe pod <pod-name>
```

2. **拓扑键不匹配**
```bash
# 查看节点标签
kubectl get nodes --show-labels | grep <topology-key>
```

### 11.9.3 资源管理问题
1. **超出配额限制**
```bash
# 查看配额使用情况
kubectl describe resourcequota -n <namespace>
```

2. **违反限制范围**
```bash
# 查看限制范围
kubectl describe limitrange -n <namespace>
```

## 11.10 最佳实践

### 11.10.1 调度最佳实践
1. **合理使用标签**：为节点和 Pod 设置有意义的标签
2. **避免过度约束**：不要设置过多的调度约束，影响调度成功率
3. **使用反亲和性**：提高应用的高可用性
4. **定期审查调度策略**：根据业务变化调整调度策略

### 11.10.2 资源管理最佳实践
1. **设置合理的资源请求和限制**：避免资源浪费和争抢
2. **使用命名空间隔离**：通过命名空间管理不同团队的资源
3. **配置资源配额**：防止某个团队或应用占用过多资源
4. **监控资源使用**：定期监控和分析资源使用情况

### 11.10.3 优先级和抢占最佳实践
1. **定义清晰的优先级层级**：为不同类型的业务定义合适的优先级
2. **谨慎使用抢占**：避免频繁的 Pod 抢占影响业务稳定性
3. **监控抢占事件**：及时发现和处理抢占相关问题

## 总结
本章我们深入学习了 Kubernetes 的高级调度和资源管理机制。通过节点选择器、亲和性和反亲和性、污点和容忍等特性，我们可以实现更灵活和精确的调度控制。通过资源配额、限制范围和优先级类等机制，我们可以确保集群资源的合理分配和高效利用。这些高级特性对于构建稳定、高效的 Kubernetes 集群至关重要，需要根据实际业务需求合理配置和使用。