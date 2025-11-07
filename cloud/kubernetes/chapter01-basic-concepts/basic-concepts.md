# 第1章 Kubernetes基础概念和架构

## 1.1 什么是Kubernetes？

### 1.1.1 容器编排的必要性

在现代软件开发中，容器技术（如Docker）已经成为打包和部署应用程序的标准方式。然而，当我们的系统规模扩大，需要管理成百上千个容器时，手动管理这些容器就变得极其困难。这就引出了容器编排的需求。

容器编排解决了以下关键问题：
- 如何在多台服务器上部署容器？
- 如何实现容器间的通信？
- 如何自动扩缩容以应对流量变化？
- 如何在容器失败时自动恢复？
- 如何滚动更新应用程序而不中断服务？

### 1.1.2 Kubernetes简介

Kubernetes（通常简称为K8s）是一个开源的容器编排平台，它提供了自动化部署、扩展和管理容器化应用程序的能力。Kubernetes最初由Google设计，基于其内部的Borg系统，后来捐赠给了Cloud Native Computing Foundation（CNCF）。

Kubernetes的主要功能包括：
- **服务发现和负载均衡**：自动暴露容器和服务给外部访问
- **存储编排**：自动挂载存储系统，无论是本地存储还是云存储
- **自动回滚**：如果更新导致问题，可以自动回滚到之前的版本
- **自动扩缩容**：根据CPU使用率或其他指标自动调整应用程序实例数量
- **配置和密钥管理**：无需重新构建镜像即可部署和更新配置和密钥
- **批量执行**：除了服务，还能管理批处理和CI工作负载

## 1.2 Kubernetes核心概念

### 1.2.1 Pod

Pod是Kubernetes中最小的可部署单元。一个Pod代表集群中运行的一个进程实例。Pod封装了一个或多个容器、存储资源、唯一的网络IP以及其他管理容器运行方式的选项。

#### Pod的特点：
- Pod内的容器共享网络命名空间，因此它们可以通过localhost相互通信
- Pod内的容器共享存储卷，可以访问相同的文件系统
- 每个Pod都有一个唯一的IP地址
- Pod是短暂的，一旦被销毁，就会被分配新的IP地址

```yaml
# 示例：简单的Pod定义
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

### 1.2.2 Service

Service是Kubernetes中定义了一组Pod的逻辑集合和访问这组Pod的策略。由于Pod是动态的，IP地址会经常变化，Service提供了一个稳定的访问入口。

#### Service的类型：
1. **ClusterIP**：默认类型，在集群内部暴露服务
2. **NodePort**：在每个节点上开放一个端口来暴露服务
3. **LoadBalancer**：在云提供商环境中创建一个外部负载均衡器
4. **ExternalName**：将服务映射到externalName字段的内容

```yaml
# 示例：NodePort类型的Service
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
```

### 1.2.3 Deployment

Deployment为Pod和ReplicaSet提供声明式更新。你只需要描述Deployment中应用程序的最终状态，Deployment Controller会以受控速率将实际状态改变为期望状态。

```yaml
# 示例：Deployment定义
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
        image: nginx:1.21
        ports:
        - containerPort: 80
```

### 1.2.4 其他重要概念

#### ReplicaSet
确保任何时间都有指定数量的Pod副本在运行。

#### Namespace
用于在多个用户之间划分集群资源。

#### ConfigMap
用于存储非机密性的配置数据。

#### Secret
用于存储敏感信息，如密码、OAuth令牌等。

#### Volume
为Pod提供持久化存储。

## 1.3 Kubernetes架构组件

### 1.3.1 控制平面组件（Control Plane Components）

控制平面负责管理整个集群，做出全局决策。

#### kube-apiserver
API服务器是Kubernetes控制平面的前端，处理所有REST请求并提供集群状态。

#### etcd
一致且高可用的键值存储，用于存储所有集群数据。

#### kube-scheduler
监视新创建的、未指定运行节点的Pod，并选择一个节点来运行Pod。

#### kube-controller-manager
运行控制器进程，包括：
- 节点控制器：负责节点故障检测和响应
- 副本控制器：维护Pod副本数量
- 端点控制器：填充Endpoint对象
- 服务账户和令牌控制器：为新的命名空间创建默认账户和API访问令牌

#### cloud-controller-manager
与底层云提供商交互的控制器管理器。

### 1.3.2 节点组件（Node Components）

节点组件运行在每个节点上，维护运行的Pod并提供Kubernetes运行环境。

#### kubelet
确保Pod中容器都运行正常，与控制平面通信。

#### kube-proxy
实现Kubernetes服务(Service)概念的一部分，维护节点上的网络规则。

#### 容器运行时
负责运行容器的软件，如Docker、containerd或CRI-O。

### 1.3.3 插件（Addons）

插件扩展了Kubernetes的功能。

#### DNS
集群内的DNS服务，例如CoreDNS。

#### Web UI (Dashboard)
Kubernetes的Web界面。

#### 容器资源监控
收集和存储容器指标。

#### 集群层面日志
保存容器日志到中央日志存储。

## 1.4 实验：搭建Minikube环境

为了更好地理解Kubernetes的概念，我们将使用Minikube搭建一个单节点的Kubernetes集群。

### 1.4.1 安装Minikube

1. 下载并安装Minikube：
```bash
# Windows (使用Chocolatey)
choco install minikube

# 或者直接下载二进制文件
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe
ren minikube-windows-amd64.exe minikube.exe
```

2. 启动Minikube集群：
```bash
minikube start
```

3. 验证集群状态：
```bash
kubectl cluster-info
kubectl get nodes
```

### 1.4.2 创建第一个Pod

1. 创建一个简单的Nginx Pod：
```bash
kubectl run nginx --image=nginx:1.21 --port=80
```

2. 查看Pod状态：
```bash
kubectl get pods
kubectl describe pod nginx
```

3. 暴露Pod为Service：
```bash
kubectl expose pod nginx --type=NodePort --port=80
```

4. 访问服务：
```bash
minikube service nginx
```

### 1.4.3 使用YAML文件创建资源

1. 创建一个Pod的YAML文件：
```yaml
# nginx-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-yaml-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

2. 应用YAML文件：
```bash
kubectl apply -f nginx-pod.yaml
```

3. 验证创建结果：
```bash
kubectl get pods
```

## 1.5 小结

本章我们介绍了Kubernetes的基本概念和架构，包括：
- Kubernetes作为容器编排平台的重要性
- 核心概念：Pod、Service、Deployment等
- Kubernetes架构：控制平面组件和节点组件
- 通过Minikube搭建实验环境并进行简单操作

下一章我们将详细介绍如何搭建完整的Kubernetes环境，包括多种安装方式的选择和配置。