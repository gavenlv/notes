# 第9章：监控、日志和调试

## 本章概要
本章将详细介绍 Kubernetes 集群的监控、日志收集和调试技术。我们将学习如何使用 Metrics Server、Prometheus 等工具监控集群状态，如何收集和分析应用日志，以及如何使用各种调试技巧诊断和解决问题。

## 目标
- 掌握 Kubernetes 监控体系和常用监控工具
- 学会部署和使用 Metrics Server
- 了解 Prometheus 监控解决方案
- 掌握日志收集和分析方法
- 学会使用 kubectl 和其他工具进行调试

## 9.1 Kubernetes 监控体系

### 9.1.1 监控层次
Kubernetes 监控通常分为以下几个层次：
1. **基础设施层监控**：节点资源使用情况（CPU、内存、磁盘、网络）
2. **Kubernetes 组件监控**：API Server、etcd、kubelet 等核心组件状态
3. **应用层监控**：Pod、Service 等资源状态和应用指标
4. **业务层监控**：应用业务指标和用户体验数据

### 9.1.2 监控指标类型
1. **核心指标（Core Metrics）**：CPU 和内存使用率等基本资源指标
2. **自定义指标（Custom Metrics）**：应用程序暴露的特定指标
3. **外部指标（External Metrics）**：来自集群外系统的指标

## 9.2 Metrics Server

### 9.2.1 Metrics Server 简介
Metrics Server 是 Kubernetes 集群中的核心组件监控工具，它实现了 Resource Metrics API，为 Horizontal Pod Autoscaler (HPA) 和 Vertical Pod Autoscaler (VPA) 提供指标数据。

### 9.2.2 部署 Metrics Server

#### 使用 Helm 部署
```bash
# 添加 metrics-server Helm 仓库
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/

# 更新 Helm 仓库
helm repo update

# 安装 metrics-server
helm upgrade --install metrics-server metrics-server/metrics-server \
  --set args={--kubelet-insecure-tls} \
  --namespace kube-system
```

#### 使用 YAML 文件部署
```bash
# 下载并应用 YAML 文件
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 9.2.3 验证 Metrics Server
```bash
# 查看 Metrics Server Pod 状态
kubectl get pods -n kube-system | grep metrics-server

# 查看节点资源使用情况
kubectl top nodes

# 查看 Pod 资源使用情况
kubectl top pods -A
```

### 9.2.4 常见问题和解决方法
1. **证书问题**：添加 `--kubelet-insecure-tls` 参数跳过证书验证
2. **无法获取指标**：检查 Metrics Server 日志
```bash
kubectl logs -n kube-system <metrics-server-pod-name>
```

## 9.3 Prometheus 监控解决方案

### 9.3.1 Prometheus 架构
Prometheus 是云原生监控领域的事实标准，其架构主要包括：
- **Prometheus Server**：负责数据采集和存储
- **Client Libraries**：应用集成的客户端库
- **Pushgateway**：处理短期任务的指标推送
- **Alertmanager**：处理告警通知
- **Service Discovery**：自动发现监控目标

### 9.3.2 使用 Prometheus Operator 部署

#### 安装 Prometheus Operator
```bash
# 添加 Prometheus Community Helm 仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# 更新 Helm 仓库
helm repo update

# 创建监控命名空间
kubectl create namespace monitoring

# 安装 kube-prometheus-stack
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false
```

### 9.3.3 访问 Prometheus 和 Grafana
```bash
# 获取 Prometheus 服务信息
kubectl get svc -n monitoring

# 端口转发访问 Prometheus
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090

# 端口转发访问 Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
```

### 9.3.4 配置 ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: example-app
  namespace: default
  labels:
    app: example-app
spec:
  selector:
    matchLabels:
      app: example-app
  endpoints:
  - port: web
    interval: 30s
```

### 9.3.5 自定义告警规则
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: example-rules
  namespace: monitoring
spec:
  groups:
  - name: example.rules
    rules:
    - alert: HighRequestLatency
      expr: job:request_latency_seconds:mean5m{job="myjob"} > 0.5
      for: 10m
      labels:
        severity: page
      annotations:
        summary: High request latency
```

## 9.4 日志收集和分析

### 9.4.1 Kubernetes 日志类型
1. **节点级日志**：系统组件和容器引擎日志
2. **Pod 级日志**：应用容器的标准输出和标准错误
3. **事件日志**：Kubernetes 对象的生命周期事件

### 9.4.2 查看 Pod 日志
```bash
# 查看 Pod 日志
kubectl logs <pod-name>

# 查看 Pod 中特定容器的日志
kubectl logs <pod-name> -c <container-name>

# 实时查看日志
kubectl logs -f <pod-name>

# 查看前一个容器实例的日志（容器重启后）
kubectl logs <pod-name> --previous

# 查看最近 1 小时的日志
kubectl logs --since=1h <pod-name>
```

### 9.4.3 使用 EFK 栈收集日志

#### 部署 Elasticsearch
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:7.10.1
        env:
        - name: discovery.type
          value: single-node
        ports:
        - containerPort: 9200
        - containerPort: 9300
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  namespace: logging
spec:
  selector:
    app: elasticsearch
  ports:
  - port: 9200
    targetPort: 9200
  - port: 9300
    targetPort: 9300
```

#### 部署 Fluentd
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: logging
  labels:
    app: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      serviceAccountName: fluentd
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1.12.0-debian-elasticsearch7-1.0
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.logging.svc"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluentd
  namespace: logging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluentd
rules:
- apiGroups:
  - ""
  resources:
  - pods
  - namespaces
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fluentd
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: fluentd
subjects:
- kind: ServiceAccount
  name: fluentd
  namespace: logging
```

#### 部署 Kibana
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kibana
  template:
    metadata:
      labels:
        app: kibana
    spec:
      containers:
      - name: kibana
        image: docker.elastic.co/kibana/kibana:7.10.1
        env:
        - name: ELASTICSEARCH_HOSTS
          value: '["http://elasticsearch.logging.svc:9200"]'
        ports:
        - containerPort: 5601
---
apiVersion: v1
kind: Service
metadata:
  name: kibana
  namespace: logging
spec:
  selector:
    app: kibana
  ports:
  - port: 5601
    targetPort: 5601
```

### 9.4.4 使用 Loki 收集日志

#### 部署 Loki Stack
```bash
# 添加 grafana Helm 仓库
helm repo add grafana https://grafana.github.io/helm-charts

# 更新 Helm 仓库
helm repo update

# 安装 loki-stack
helm upgrade --install loki grafana/loki-stack \
  --namespace=logging \
  --set grafana.enabled=true,prometheus.enabled=true,prometheus.alertmanager.persistentVolume.enabled=false,prometheus.server.persistentVolume.enabled=false
```

## 9.5 调试技巧和工具

### 9.5.1 kubectl 调试命令

#### 查看资源状态
```bash
# 查看 Pod 状态详情
kubectl describe pod <pod-name>

# 查看节点状态
kubectl describe node <node-name>

# 查看所有事件
kubectl get events --sort-by=.metadata.creationTimestamp

# 查看特定命名空间的事件
kubectl get events -n <namespace>
```

#### 执行命令和调试
```bash
# 在 Pod 中执行命令
kubectl exec -it <pod-name> -- /bin/sh

# 在 Pod 中执行命令（指定容器）
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh

# 复制文件到/从 Pod
kubectl cp <local-file> <pod-name>:<pod-path>
kubectl cp <pod-name>:<pod-path> <local-file>
```

#### 端口转发
```bash
# 端口转发到 Pod
kubectl port-forward <pod-name> <local-port>:<pod-port>

# 端口转发到 Service
kubectl port-forward service/<service-name> <local-port>:<service-port>
```

### 9.5.2 使用临时调试容器
```bash
# 为现有 Pod 添加临时调试容器
kubectl debug <pod-name> -it --image=busybox --target=<container-name>

# 创建带有调试容器的新 Pod
kubectl run debug --image=busybox -it --rm
```

### 9.5.3 网络调试工具

#### 安装网络调试工具
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: network-debug
spec:
  containers:
  - name: debug
    image: nicolaka/netshoot
    command: ["/bin/bash"]
    stdin: true
    tty: true
```

#### 常用网络调试命令
```bash
# 测试 DNS 解析
nslookup kubernetes.default

# 测试网络连通性
ping google.com

# 测试端口连通性
telnet <service-ip> <port>

# 查看网络接口
ip addr

# 抓包分析
tcpdump -i eth0
```

## 9.6 实验：搭建完整监控和日志系统

### 实验目标
部署一套完整的 Kubernetes 监控和日志收集系统，包括 Prometheus、Grafana 和 Loki。

### 实验步骤

1. 创建监控命名空间：
```bash
kubectl create namespace monitoring
```

2. 安装 kube-prometheus-stack：
```bash
# 添加 Helm 仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 安装
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false
```

3. 安装 Loki Stack：
```bash
# 添加 Helm 仓库
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 安装
helm upgrade --install loki grafana/loki-stack \
  --namespace=monitoring \
  --set grafana.enabled=true,prometheus.enabled=false
```

4. 配置 Grafana 数据源：
```bash
# 获取 Grafana admin 密码
kubectl get secret --namespace monitoring kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

# 端口转发访问 Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
```

5. 在 Grafana 中添加 Loki 数据源：
   - 登录 Grafana (默认用户名 admin)
   - 进入 Configuration -> Data Sources
   - 添加新的数据源，选择 Loki
   - URL 设置为: `http://loki:3100`
   - 点击 Save & Test

6. 部署测试应用并查看监控数据：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
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
        image: nginx:1.20
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

7. 查看监控和日志：
   - 在 Grafana 中查看 Kubernetes 集群指标
   - 在 Grafana 中查询应用日志
   - 观察 HPA 是否正常工作

## 9.7 故障排除

### 9.7.1 监控指标缺失
可能原因和解决方法：
1. **Metrics Server 未部署或异常**
   ```bash
   # 检查 Metrics Server 状态
   kubectl get pods -n kube-system | grep metrics-server
   
   # 查看 Metrics Server 日志
   kubectl logs -n kube-system <metrics-server-pod-name>
   ```

2. **Pod 未就绪**
   ```bash
   # 检查 Pod 状态
   kubectl get pods <pod-name>
   
   # 查看 Pod 详情
   kubectl describe pod <pod-name>
   ```

### 9.7.2 日志收集异常
可能原因和解决方法：
1. **Fluentd/DaemonSet 未正常运行**
   ```bash
   # 检查 Fluentd 状态
   kubectl get pods -n logging
   
   # 查看 Fluentd 日志
   kubectl logs -n logging <fluentd-pod-name>
   ```

2. **权限问题**
   ```bash
   # 检查 ServiceAccount 和 RBAC 配置
   kubectl get sa,clusterrole,clusterrolebinding -n logging
   ```

### 9.7.3 网络调试常见问题
1. **DNS 解析失败**
   ```bash
   # 检查 CoreDNS 状态
   kubectl get pods -n kube-system | grep coredns
   
   # 测试 DNS 解析
   kubectl run -it --rm debug --image=busybox -- nslookup kubernetes.default
   ```

2. **网络策略阻止通信**
   ```bash
   # 检查网络策略
   kubectl get networkpolicy -A
   
   # 测试网络连通性
   kubectl run -it --rm debug --image=busybox -- wget -O- <service-ip>:<port>
   ```

## 9.8 最佳实践

### 9.8.1 监控最佳实践
1. **分层监控**：建立基础设施、平台和应用三层监控体系
2. **关键指标告警**：关注 SLI/SLO，设置合理的告警阈值
3. **长期存储**：为重要指标配置长期存储方案
4. **可视化展示**：使用 Grafana 等工具建立直观的仪表板

### 9.8.2 日志最佳实践
1. **结构化日志**：应用输出 JSON 格式的结构化日志
2. **日志级别控制**：合理设置不同环境的日志级别
3. **日志轮转**：避免单个日志文件过大
4. **敏感信息过滤**：避免在日志中记录密码等敏感信息

### 9.8.3 调试最佳实践
1. **渐进式调试**：从宏观到微观逐步缩小问题范围
2. **保留现场**：在调试过程中尽量保持问题现场
3. **记录过程**：详细记录调试步骤和发现
4. **复盘总结**：对复杂问题进行复盘，形成知识库

## 总结
本章我们全面介绍了 Kubernetes 的监控、日志和调试技术。我们学习了如何使用 Metrics Server 和 Prometheus 进行集群监控，如何通过 EFK 或 Loki 栈收集和分析日志，以及如何运用各种调试技巧快速定位和解决问题。通过实践搭建完整的监控和日志系统，我们掌握了在生产环境中保障 Kubernetes 集群稳定运行的关键技能。这些能力对于运维工程师和开发人员都至关重要，有助于提升系统的可观测性和可靠性。