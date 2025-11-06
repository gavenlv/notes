# 第2章 Kubernetes环境搭建和工具安装

## 2.1 Kubernetes安装方式概述

Kubernetes有多种安装方式，适用于不同的使用场景和需求。选择合适的安装方式对于后续的学习和生产环境部署至关重要。

### 2.1.1 本地开发环境

对于初学者和开发人员来说，本地环境是最方便的选择：
- **Minikube**：最流行的单节点Kubernetes集群，适合学习和开发
- **Kind (Kubernetes in Docker)**：使用Docker容器作为节点运行Kubernetes
- **Docker Desktop**：Docker官方提供的Kubernetes集成环境

### 2.1.2 生产环境部署方案

对于生产环境，有以下几种主要的部署方案：
- **kubeadm**：官方推荐的引导工具，用于创建符合最佳实践的生产集群
- **云厂商托管服务**：如AWS EKS、Azure AKS、Google GKE等
- **企业级发行版**：如Red Hat OpenShift、Rancher等

### 2.1.3 自动化部署工具

用于大规模部署和管理多个Kubernetes集群：
- **Kops**：专门用于在AWS上部署Kubernetes
- **Kubespray**：基于Ansible的多平台部署工具
- **Terraform**：基础设施即代码工具，可用于部署Kubernetes

## 2.2 本地开发环境搭建

### 2.2.1 Minikube安装与配置

Minikube是在本地运行Kubernetes的最简单方式。

#### 安装前提条件
1. 安装hypervisor（虚拟机管理程序）
   - Windows: Hyper-V, VirtualBox, VMware Workstation
   - macOS: HyperKit, VirtualBox, VMware Fusion
   - Linux: VirtualBox, KVM

2. 安装kubectl（Kubernetes命令行工具）

#### 在Windows上安装Minikube

1. 使用Chocolatey安装（推荐）：
```powershell
choco install minikube
```

2. 或者直接下载二进制文件：
```powershell
# 下载最新版本
curl -Lo minikube.exe https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe

# 添加到PATH环境变量
$env:PATH += ";C:\path\to\minikube"
```

3. 验证安装：
```powershell
minikube version
```

#### 启动Minikube集群

1. 启动集群：
```powershell
# 使用默认驱动启动
minikube start

# 指定驱动启动（如使用VirtualBox）
minikube start --driver=virtualbox

# 指定Kubernetes版本
minikube start --kubernetes-version=v1.25.0
```

2. 验证集群状态：
```powershell
kubectl cluster-info
kubectl get nodes
```

#### Minikube常用命令

```powershell
# 查看集群状态
minikube status

# 停止集群
minikube stop

# 删除集群
minikube delete

# 进入节点
minikube ssh

# 查看仪表板
minikube dashboard

# 查看插件
minikube addons list

# 启用插件
minikube addons enable metrics-server
```

### 2.2.2 Kind安装与配置

Kind（Kubernetes in Docker）使用Docker容器作为节点运行Kubernetes。

#### 安装Kind

1. 使用Chocolatey安装（Windows）：
```powershell
choco install kind
```

2. 或者直接下载二进制文件：
```powershell
# 下载最新版本
curl -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.17.0/kind-windows-amd64

# 重命名为kind并添加到PATH
ren kind-windows-amd64.exe kind.exe
```

#### 创建Kubernetes集群

1. 创建基本集群：
```powershell
kind create cluster
```

2. 创建指定名称的集群：
```powershell
kind create cluster --name my-cluster
```

3. 使用配置文件创建复杂集群：
```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
```

```powershell
kind create cluster --config kind-config.yaml
```

#### Kind常用命令

```powershell
# 查看集群
kind get clusters

# 删除集群
kind delete cluster

# 导出kubeconfig
kind export kubeconfig

# 加载Docker镜像到集群
kind load docker-image my-image:latest
```

### 2.2.3 Docker Desktop集成Kubernetes

Docker Desktop提供了内置的Kubernetes支持。

#### 启用Kubernetes

1. 打开Docker Desktop设置
2. 进入Kubernetes选项卡
3. 勾选"Enable Kubernetes"
4. 点击Apply & Restart

#### 验证安装

```powershell
kubectl cluster-info
kubectl get nodes
```

## 2.3 kubectl安装与配置

kubectl是Kubernetes的命令行工具，用于与集群进行交互。

### 2.3.1 安装kubectl

#### Windows安装

1. 使用Chocolatey安装：
```powershell
choco install kubernetes-cli
```

2. 或者使用curl下载：
```powershell
curl -LO "https://dl.k8s.io/release/v1.25.0/bin/windows/amd64/kubectl.exe"
```

#### 验证安装

```powershell
kubectl version --client
```

### 2.3.2 kubectl配置文件

kubectl使用kubeconfig文件来连接集群，默认位置为`~/.kube/config`。

#### 配置文件结构

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <证书数据>
    server: https://kubernetes.docker.internal:6443
  name: docker-desktop
contexts:
- context:
    cluster: docker-desktop
    user: docker-desktop
  name: docker-desktop
current-context: docker-desktop
kind: Config
preferences: {}
users:
- name: docker-desktop
  user:
    client-certificate-data: <客户端证书数据>
    client-key-data: <客户端密钥数据>
```

#### 常用配置命令

```powershell
# 查看当前配置
kubectl config view

# 查看当前上下文
kubectl config current-context

# 切换上下文
kubectl config use-context docker-desktop

# 设置别名（PowerShell）
Set-Alias -Name k -Value kubectl
```

### 2.3.3 kubectl基本命令

#### 资源查看命令

```powershell
# 查看节点
kubectl get nodes

# 查看Pod
kubectl get pods

# 查看所有资源
kubectl get all

# 查看详细信息
kubectl describe node <node-name>
kubectl describe pod <pod-name>
```

#### 资源创建和删除

```powershell
# 创建资源
kubectl create -f <file.yaml>

# 应用配置
kubectl apply -f <file.yaml>

# 删除资源
kubectl delete pod <pod-name>
kubectl delete -f <file.yaml>
```

#### 日志和执行命令

```powershell
# 查看日志
kubectl logs <pod-name>

# 进入容器
kubectl exec -it <pod-name> -- /bin/bash

# 复制文件
kubectl cp <local-file> <pod-name>:<pod-path>
```

## 2.4 Helm安装与使用

Helm是Kubernetes的包管理器，类似于Linux的APT或YUM。

### 2.4.1 安装Helm

#### Windows安装

1. 使用Chocolatey安装：
```powershell
choco install kubernetes-helm
```

2. 或者下载二进制文件：
```powershell
# 下载最新版本
curl -LO https://get.helm.sh/helm-v3.10.0-windows-amd64.zip

# 解压并添加到PATH
Expand-Archive helm-v3.10.0-windows-amd64.zip
```

#### 验证安装

```powershell
helm version
```

### 2.4.2 Helm基本概念

- **Chart**：Helm包，包含了运行一个应用所需的Kubernetes资源定义
- **Repository**：Charts的仓库
- **Release**：Chart在一个集群中的运行实例

### 2.4.3 Helm常用命令

```powershell
# 添加仓库
helm repo add stable https://charts.helm.sh/stable

# 更新仓库
helm repo update

# 搜索Chart
helm search repo nginx

# 安装Chart
helm install my-nginx stable/nginx-ingress

# 查看已安装的Release
helm list

# 卸载Release
helm uninstall my-nginx
```

## 2.5 实验：搭建完整的本地开发环境

### 2.5.1 安装所有必需工具

1. 安装Docker Desktop（包含Kubernetes）
2. 安装kubectl
3. 安装Helm
4. 安装Minikube

### 2.5.2 验证安装

```powershell
# 检查Docker
docker version

# 检查kubectl
kubectl version

# 检查Helm
helm version

# 检查Minikube
minikube version
```

### 2.5.3 启动并验证集群

```powershell
# 启动Minikube
minikube start

# 验证集群
kubectl cluster-info
kubectl get nodes

# 部署一个测试应用
kubectl create deployment hello-minikube --image=kicbase/echo-server:1.0
kubectl expose deployment hello-minikube --type=NodePort --port=8080

# 获取服务URL
minikube service hello-minikube --url
```

### 2.5.4 使用Helm部署应用

```powershell
# 添加Bitnami仓库
helm repo add bitnami https://charts.bitnami.com/bitnami

# 安装WordPress
helm install my-wordpress bitnami/wordpress

# 查看状态
helm status my-wordpress

# 获取访问信息
kubectl get svc --namespace default my-wordpress
```

## 2.6 故障排除

### 2.6.1 常见问题

#### Minikube启动失败

```powershell
# 检查驱动
minikube start --driver=virtualbox

# 清理并重新启动
minikube delete
minikube start
```

#### kubectl无法连接集群

```powershell
# 检查配置
kubectl config view

# 重置配置
kubectl config use-context docker-desktop
```

#### 权限问题

```powershell
# 检查当前用户
kubectl auth can-i get pods

# 创建RBAC角色
kubectl create clusterrolebinding permissive-binding \
  --clusterrole=cluster-admin \
  --user=admin \
  --user=kubelet \
  --group=system:serviceaccounts
```

## 2.7 小结

本章我们详细介绍了Kubernetes环境的搭建方法：
- 不同的安装方式及其适用场景
- 本地开发环境（Minikube、Kind、Docker Desktop）的安装和配置
- kubectl命令行工具的安装和基本使用
- Helm包管理器的安装和使用
- 通过实验验证了完整的本地开发环境

下一章我们将深入学习Pod的概念和使用方法，这是Kubernetes中最基本的部署单元。