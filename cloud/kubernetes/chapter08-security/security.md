# 第8章：安全机制和权限控制

## 本章概要
本章将详细介绍 Kubernetes 的安全机制和权限控制系统。我们将从认证、授权和准入控制三个层面来讲解 K8s 的安全体系，深入理解 ServiceAccount、RBAC（基于角色的访问控制）等核心概念，并通过实际案例演示如何配置和管理集群的安全策略。

## 目标
- 理解 Kubernetes 安全体系的三个层面
- 掌握认证机制（Authentication）
- 掌握授权机制（Authorization）
- 学会使用 RBAC 进行权限管理
- 理解准入控制（Admission Control）
- 实践安全配置和故障排除

## 8.1 Kubernetes 安全体系概述

### 8.1.1 安全的三个层面
Kubernetes 安全体系主要分为以下三个层面：
1. **认证（Authentication）**：识别用户身份
2. **授权（Authorization）**：确定用户权限
3. **准入控制（Admission Control）**：拦截请求进行额外处理

### 8.1.2 用户类型
Kubernetes 中有两种类型的用户：
- **普通用户（Normal Users）**：由外部系统管理，例如通过客户端证书、Bearer Token 或身份认证代理等方式进行认证
- **服务账户（Service Accounts）**：由 Kubernetes API 管理，用于 Pod 内运行的进程访问 API Server

## 8.2 认证机制（Authentication）

### 8.2.1 客户端证书认证
客户端证书是最常见的认证方式，用户需要提供有效的 X.509 客户端证书。

#### 创建客户端证书示例
```bash
# 生成私钥
openssl genrsa -out user.key 2048

# 创建证书签名请求
openssl req -new -key user.key -out user.csr -subj "/CN=user/O=dev"

# 使用集群 CA 签名证书
openssl x509 -req -in user.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out user.crt -days 365
```

### 8.2.2 Bearer Token 认证
通过静态 Token 文件或 ServiceAccount Token 进行认证。

#### 配置 kubeconfig 使用 Token
```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <CA_DATA>
    server: https://kubernetes:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: user
  name: user@kubernetes
current-context: user@kubernetes
users:
- name: user
  user:
    token: <TOKEN>
```

### 8.2.3 Bootstrap Token 认证
用于节点加入集群时的临时认证机制。

### 8.2.4 JWT Token 认证
通过身份提供商（如 OIDC）发放的 JWT Token 进行认证。

## 8.3 授权机制（Authorization）

### 8.3.1 ABAC（基于属性的访问控制）
ABAC 是一种较老的授权机制，通过策略文件定义访问规则。

### 8.3.2 RBAC（基于角色的访问控制）
RBAC 是目前最常用的授权机制，通过角色和角色绑定来控制访问权限。

#### RBAC 核心概念
1. **Role**：定义一组权限规则
2. **ClusterRole**：集群范围的角色定义
3. **RoleBinding**：将角色绑定到用户或组
4. **ClusterRoleBinding**：集群范围的角色绑定

### 8.3.3 Webhook 授权
通过外部授权服务进行授权决策。

### 8.3.4 Node 授权
专门针对节点的特殊授权机制。

## 8.4 RBAC 详解

### 8.4.1 Role 和 RoleBinding

#### 创建 Role 示例
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

#### 创建 RoleBinding 示例
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 8.4.2 ClusterRole 和 ClusterRoleBinding

#### 创建 ClusterRole 示例
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "watch", "list"]
```

#### 创建 ClusterRoleBinding 示例
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-secrets-global
subjects:
- kind: Group
  name: manager
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### 8.4.3 聚合 ClusterRole
可以将多个 ClusterRole 聚合成一个。

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.example.com/aggregate-to-monitoring: "true"
rules: []
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
  labels:
    rbac.example.com/aggregate-to-monitoring: "true"
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
```

## 8.5 服务账户（ServiceAccount）

### 8.5.1 默认服务账户
每个命名空间都会自动创建一个默认的服务账户。

### 8.5.2 自定义服务账户

#### 创建 ServiceAccount 示例
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: build-robot
  namespace: default
automountServiceAccountToken: false
```

#### 在 Pod 中使用 ServiceAccount
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: build-robot
  containers:
  - name: nginx
    image: nginx
```

### 8.5.3 为 ServiceAccount 添加 ImagePullSecrets
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
  namespace: default
imagePullSecrets:
- name: myregistrykey
```

## 8.6 准入控制（Admission Control）

### 8.6.1 准入控制器类型
1. **验证型（Validating）**：检查对象是否符合规范
2. **变更型（Mutating）**：修改对象以满足特定要求

### 8.6.2 常见准入控制器
- **AlwaysPullImages**：强制每次拉取镜像
- **LimitRanger**：限制资源使用
- **ResourceQuota**：配额管理
- **NamespaceLifecycle**：命名空间生命周期管理
- **ServiceAccount**：服务账户自动化

### 8.6.3 动态准入控制
通过 Webhook 实现更灵活的准入控制。

#### ValidatingWebhookConfiguration 示例
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: "pod-policy.example.com"
webhooks:
- name: "pod-policy.example.com"
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["pods"]
    scope: "Namespaced"
  clientConfig:
    service:
      namespace: "webhook-server"
      name: "webhook-server"
    caBundle: "<CA_BUNDLE>"
  admissionReviewVersions: ["v1", "v1beta1"]
  sideEffects: None
  timeoutSeconds: 5
```

## 8.7 安全上下文（Security Context）

### 8.7.1 Pod 安全上下文
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  volumes:
  - name: sec-ctx-vol
    emptyDir: {}
  containers:
  - name: sec-ctx-demo
    image: busybox
    command: [ "sh", "-c", "sleep 1h" ]
    volumeMounts:
    - name: sec-ctx-vol
      mountPath: /data/demo
    securityContext:
      allowPrivilegeEscalation: false
```

### 8.7.2 容器安全上下文
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo-2
spec:
  containers:
  - name: sec-ctx-demo-2
    image: busybox
    command: [ "sh", "-c", "sleep 1h" ]
    securityContext:
      runAsUser: 2000
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["NET_RAW"]
```

## 8.8 网络策略（Network Policy）

### 8.8.1 NetworkPolicy 示例
```yaml
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

## 8.9 实验：配置 RBAC 权限控制

### 实验目标
创建一个开发人员角色，允许其读取 Pod 并创建 Deployment，但不能删除任何资源。

### 实验步骤

1. 创建开发人员命名空间：
```bash
kubectl create namespace dev-team
```

2. 创建开发人员角色：
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev-team
  name: developer
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
```

3. 创建测试用户证书（在主节点上执行）：
```bash
# 生成私钥
openssl genrsa -out dev-user.key 2048

# 创建证书签名请求
openssl req -new -key dev-user.key -out dev-user.csr -subj "/CN=dev-user/O=dev-team"

# 使用集群 CA 签名证书
openssl x509 -req -in dev-user.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out dev-user.crt -days 365
```

4. 创建 RoleBinding：
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: dev-team
subjects:
- kind: User
  name: dev-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
```

5. 配置 kubeconfig：
```bash
kubectl config set-credentials dev-user \
  --client-certificate=dev-user.crt \
  --client-key=dev-user.key \
  --embed-certs=true

kubectl config set-context dev-user-context \
  --cluster=kubernetes \
  --user=dev-user \
  --namespace=dev-team

kubectl config use-context dev-user-context
```

6. 测试权限：
```bash
# 应该可以列出 pods
kubectl get pods

# 应该可以创建 deployment
kubectl create deployment nginx --image=nginx

# 应该不能删除 deployment（会被拒绝）
kubectl delete deployment nginx
```

## 8.10 故障排除

### 8.10.1 权限不足错误
当用户尝试执行没有权限的操作时，会收到类似以下错误：
```
Error from server (Forbidden): pods is forbidden: User "dev-user" cannot list resource "pods" in API group "" in the namespace "default"
```

解决方法：
1. 检查用户的 Role 和 RoleBinding 配置
2. 确认角色具有所需权限
3. 确认角色绑定正确关联了用户和服务账户

### 8.10.2 服务账户令牌问题
如果 Pod 无法访问 API Server，可能是因为：
1. ServiceAccount 不存在或配置错误
2. automountServiceAccountToken 设置为 false
3. Token 文件挂载失败

检查方法：
```bash
# 查看 Pod 的 ServiceAccount
kubectl get pod <pod-name> -o yaml | grep serviceAccount

# 检查容器内是否有 token 文件
kubectl exec <pod-name> -- ls /var/run/secrets/kubernetes.io/serviceaccount/
```

### 8.10.3 网络策略阻止连接
如果 Pod 之间无法通信，可能是网络策略导致的。

检查方法：
```bash
# 查看网络策略
kubectl get networkpolicy -n <namespace>

# 描述网络策略详情
kubectl describe networkpolicy <policy-name> -n <namespace>
```

## 8.11 最佳实践

### 8.11.1 最小权限原则
始终遵循最小权限原则，只授予用户和应用所需的最小权限。

### 8.11.2 使用 RBAC 而不是 ABAC
RBAC 更易于管理和维护，应该优先使用。

### 8.11.3 定期审查权限
定期审查用户和服务账户的权限，确保没有不必要的权限分配。

### 8.11.4 启用审计日志
启用审计日志可以帮助跟踪和分析安全相关事件。

### 8.11.5 使用网络策略
在网络层面限制 Pod 之间的通信，增强安全性。

## 总结
本章我们深入了解了 Kubernetes 的安全机制，包括认证、授权和准入控制三个方面。我们重点学习了 RBAC 权限管理系统，掌握了如何创建和管理角色、角色绑定以及服务账户。通过实验，我们实践了如何为开发团队配置合适的权限，同时了解了常见安全问题的故障排除方法。这些知识对于构建安全可靠的 Kubernetes 集群至关重要。