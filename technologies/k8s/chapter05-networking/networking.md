# 第5章 服务发现和网络

## 5.1 Kubernetes网络模型概述

### 5.1.1 Kubernetes网络基本原则

Kubernetes对网络有以下四个基本要求：
1. **Pod间通信**：所有Pod都可以直接通信，无需NAT
2. **Node-Pod通信**：Node和Pod之间可以直接通信，无需NAT
3. **Pod-Service通信**：Pod看到自己的IP与其他人看到的一样
4. **外部访问**：外部可以访问某些Pod

### 5.1.2 Kubernetes网络层次

Kubernetes网络涉及多个层面：
- **节点网络**：Node之间的网络通信
- **Pod网络**：Pod之间的网络通信
- **Service网络**：虚拟IP网络，用于服务发现
- **外部网络**：与集群外系统的通信

## 5.2 Pod网络详解

### 5.2.1 Pod网络特点

每个Pod都有一个独立的IP地址，这个IP在整个集群内都是唯一的。Pod内的所有容器共享同一个网络命名空间。

### 5.2.2 Pod网络实现

Pod网络通常由CNI（Container Network Interface）插件实现，常见的CNI插件包括：
- **Calico**：基于路由的网络方案
- **Flannel**：简单的覆盖网络方案
- **Cilium**：基于eBPF的高性能网络方案
- **Weave Net**：覆盖网络方案

### 5.2.3 Pod网络示例

```yaml
# pod-network-example.yaml
apiVersion: v1
kind: Pod
metadata:
  name: network-test-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

查看Pod IP：

```bash
# 创建Pod
kubectl apply -f pod-network-example.yaml

# 查看Pod IP
kubectl get pod network-test-pod -o wide

# 进入Pod查看网络信息
kubectl exec -it network-test-pod -- ip addr show

# 测试与其他Pod的连通性
kubectl exec -it network-test-pod -- ping <another-pod-ip>
```

## 5.3 Service详解

Service是Kubernetes中用于服务发现和负载均衡的核心概念。

### 5.3.1 Service类型

#### ClusterIP（默认）

只在集群内部可访问的虚拟IP：

```yaml
# clusterip-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

#### NodePort

在每个节点上开放端口，外部可通过NodeIP:NodePort访问：

```yaml
# nodeport-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
      nodePort: 30007  # 可选，默认会自动分配
```

#### LoadBalancer

云提供商的负载均衡器：

```yaml
# loadbalancer-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-loadbalancer-service
spec:
  type: LoadBalancer
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

#### ExternalName

将服务映射到DNS名称：

```yaml
# externalname-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-database-service
spec:
  type: ExternalName
  externalName: database.company.com
```

### 5.3.2 Service的工作原理

Service通过标签选择器关联Pod，并维护一个Endpoints对象：

```bash
# 查看Service
kubectl get service

# 查看Endpoints
kubectl get endpoints

# 查看详细的Service信息
kubectl describe service <service-name>
```

### 5.3.3 Service示例实践

创建一个完整的服务示例：

```yaml
# service-example.yaml
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
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

操作步骤：

```bash
# 1. 创建Deployment和服务
kubectl apply -f service-example.yaml

# 2. 查看创建的资源
kubectl get deployments
kubectl get pods
kubectl get services

# 3. 测试服务访问
kubectl run -it --rm debug --image=busybox -- sh
# 在容器内执行
wget -qO- http://nginx-service

# 4. 查看服务详细信息
kubectl describe service nginx-service

# 5. 查看Endpoints
kubectl get endpoints nginx-service
```

## 5.4 DNS服务发现

Kubernetes内置了DNS服务，用于服务发现。

### 5.4.1 CoreDNS

CoreDNS是Kubernetes默认的DNS服务器，它会自动为Service创建DNS记录。

### 5.4.2 DNS记录格式

对于名为`my-service`的服务在`my-namespace`命名空间中：
- A记录：`my-service.my-namespace.svc.cluster.local`
- 端口记录：SRV记录

在同一命名空间中可以直接使用服务名访问。

### 5.4.3 DNS测试

```bash
# 创建测试Pod
kubectl run -it --rm dns-test --image=busybox -- sh

# 在Pod中测试DNS解析
nslookup kubernetes
nslookup kubernetes.default
nslookup kubernetes.default.svc.cluster.local

# 解析自定义服务
nslookup <your-service-name>
nslookup <your-service-name>.<namespace>
```

### 5.4.4 自定义DNS配置

通过ConfigMap自定义DNS行为：

```yaml
# coredns-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
           ttl 30
        }
        prometheus :9153
        forward . /etc/resolv.conf {
           max_concurrent 1000
        }
        cache 30
        loop
        reload
        loadbalance
    }
```

## 5.5 Ingress控制器

Ingress提供了HTTP/HTTPS路由规则，可以将外部请求路由到集群内的服务。

### 5.5.1 Ingress资源定义

```yaml
# ingress-example.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /testpath
        pathType: Prefix
        backend:
          service:
            name: test
            port:
              number: 80
```

### 5.5.2 Ingress Controller

需要部署Ingress Controller来处理Ingress资源，常用的有：
- Nginx Ingress Controller
- Traefik
- HAProxy Ingress
- AWS Load Balancer Controller

### 5.5.3 Ingress示例

部署Nginx Ingress Controller：

```bash
# 安装Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.0/deploy/static/provider/cloud/deploy.yaml
```

创建Ingress资源：

```yaml
# ingress-full-example.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.21
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: web.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

操作步骤：

```bash
# 1. 部署应用和服务
kubectl apply -f ingress-full-example.yaml

# 2. 查看Ingress
kubectl get ingress

# 3. 查看详细信息
kubectl describe ingress web-ingress

# 4. 测试访问（需要配置hosts或使用真实域名）
curl -H "Host: web.example.com" http://<ingress-controller-ip>/
```

## 5.6 网络策略（Network Policies）

Network Policies用于控制Pod之间的网络流量。

### 5.6.1 Network Policy示例

```yaml
# network-policy-example.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except:
        - 172.17.1.0/24
    - namespaceSelector:
        matchLabels:
          project: myproject
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 6379
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 5978
```

### 5.6.2 应用Network Policy

```bash
# 应用网络策略
kubectl apply -f network-policy-example.yaml

# 查看网络策略
kubectl get networkpolicies

# 查看详细信息
kubectl describe networkpolicy test-network-policy
```

### 5.6.3 默认拒绝所有流量

```yaml
# default-deny-all.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

## 5.7 网络故障排除

### 5.7.1 常见网络问题

#### Pod无法访问Service

```bash
# 1. 检查Service是否存在
kubectl get service <service-name>

# 2. 检查Endpoints是否正确
kubectl get endpoints <service-name>

# 3. 检查Pod标签是否匹配
kubectl get pods --show-labels

# 4. 测试DNS解析
kubectl run -it --rm debug --image=busybox -- sh
nslookup <service-name>
```

#### Pod间无法通信

```bash
# 1. 检查Pod IP
kubectl get pods -o wide

# 2. 测试连通性
kubectl exec <pod-name> -- ping <target-pod-ip>

# 3. 检查网络插件状态
kubectl get pods -n kube-system

# 4. 检查网络策略
kubectl get networkpolicies
```

#### Ingress无法访问

```bash
# 1. 检查Ingress资源
kubectl get ingress

# 2. 检查Ingress Controller状态
kubectl get pods -n ingress-nginx

# 3. 检查Ingress Controller日志
kubectl logs -n ingress-nginx <ingress-controller-pod>

# 4. 检查服务和Endpoints
kubectl get services
kubectl get endpoints
```

### 5.7.2 网络诊断工具

#### 使用kubectl进行网络诊断

```bash
# 运行临时调试Pod
kubectl run -it --rm debug --image=nicolaka/netshoot -- sh

# 在调试Pod中使用网络工具
# 查看网络接口
ip addr

# 测试连通性
ping <target-ip>

# 测试DNS解析
dig <service-name>

# 测试端口可达性
nc -zv <service-name> <port>

# 抓包分析
tcpdump -i any port <port>
```

#### 检查集群网络组件

```bash
# 检查CoreDNS状态
kubectl get pods -n kube-system -l k8s-app=kube-dns

# 检查网络插件状态（以Calico为例）
kubectl get pods -n kube-system -l k8s-app=calico-node

# 检查kube-proxy状态
kubectl get pods -n kube-system -l k8s-app=kube-proxy
```

## 5.8 实验：网络实践操作

### 5.8.1 Service和DNS实验

```yaml
# network-lab.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1
  labels:
    app: app1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app1
  template:
    metadata:
      labels:
        app: app1
    spec:
      containers:
      - name: app1
        image: nginx:1.21
        ports:
        - containerPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app2
  labels:
    app: app2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app2
  template:
    metadata:
      labels:
        app: app2
    spec:
      containers:
      - name: app2
        image: httpd:2.4
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app1-service
spec:
  selector:
    app: app1
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app2-service
spec:
  selector:
    app: app2
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

实验步骤：

```bash
# 1. 部署应用和服务
kubectl apply -f network-lab.yaml

# 2. 查看创建的资源
kubectl get deployments
kubectl get pods
kubectl get services

# 3. 测试服务访问
kubectl run -it --rm debug --image=busybox -- sh

# 在调试Pod中执行以下命令：
# 测试DNS解析
nslookup app1-service
nslookup app2-service

# 测试服务访问
wget -qO- http://app1-service
wget -qO- http://app2-service

# 4. 测试跨命名空间访问（如果使用不同命名空间）
# wget -qO- http://app1-service.<namespace>.svc.cluster.local
```

### 5.8.2 Network Policy实验

```yaml
# network-policy-lab.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server
  labels:
    app: web-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-server
  template:
    metadata:
      labels:
        app: web-server
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: client-app
  labels:
    app: client-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: client-app
  template:
    metadata:
      labels:
        app: client-app
    spec:
      containers:
      - name: busybox
        image: busybox
        command: ["sleep", "3600"]
        ports:
        - containerPort: 80
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-client-to-web
spec:
  podSelector:
    matchLabels:
      app: web-server
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: client-app
    ports:
    - protocol: TCP
      port: 80
```

实验步骤：

```bash
# 1. 部署应用和网络策略
kubectl apply -f network-policy-lab.yaml

# 2. 测试客户端可以访问Web服务
CLIENT_POD=$(kubectl get pod -l app=client-app -o jsonpath="{.items[0].metadata.name}")
kubectl exec $CLIENT_POD -- wget -qO- http://web-service

# 3. 从另一个Pod测试访问应该被拒绝
kubectl run -it --rm test-client --image=busybox -- sh
# 在测试Pod中执行：
# wget -qO- http://web-service  # 应该超时或失败

# 4. 查看网络策略
kubectl get networkpolicies
kubectl describe networkpolicy allow-client-to-web
```

## 5.9 小结

本章我们深入学习了Kubernetes网络相关的核心概念和技术：

1. **Pod网络**：了解了Pod如何获得IP地址以及Pod间的通信机制
2. **Service机制**：掌握了四种Service类型及其应用场景
3. **DNS服务发现**：学习了Kubernetes如何通过DNS实现服务发现
4. **Ingress控制器**：了解了如何通过Ingress暴露HTTP/HTTPS服务
5. **网络策略**：掌握了如何通过Network Policy控制Pod间的流量
6. **网络故障排除**：学习了常见网络问题的诊断方法和工具
7. **实践操作**：通过实验加深了对网络概念的理解

下一章我们将学习Kubernetes的存储管理机制，包括持久化卷(PV)、持久化卷声明(PVC)以及各种存储类的使用。