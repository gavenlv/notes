# 第12章：自定义资源和Operator

## 本章概要
本章将深入探讨 Kubernetes 的自定义资源定义（CRD）和 Operator 模式。我们将学习如何扩展 Kubernetes API 以支持自定义资源，以及如何使用 Operator 来自动化应用程序的生命周期管理。通过实际示例，我们将掌握 CRD 的创建、验证、子资源配置，以及 Operator 的开发和部署。

## 目标
- 理解自定义资源定义（CRD）的概念和用途
- 学会创建和管理自定义资源
- 掌握 Operator 模式的核心概念
- 学会使用 Operator SDK 开发自定义 Operator
- 了解 CRD 的高级特性和最佳实践

## 12.1 自定义资源定义（CRD）概述

### 12.1.1 什么是 CRD
自定义资源定义（Custom Resource Definition，CRD）是 Kubernetes 的一种原生扩展机制，允许用户定义自己的资源类型，扩展 Kubernetes API。CRD 使得 Kubernetes 可以管理任何类型的应用和服务，而不仅限于内置的资源类型（如 Pod、Service、Deployment 等）。

### 12.1.2 CRD 与自定义资源的关系
- **CRD**：定义自定义资源的结构和行为
- **自定义资源**：根据 CRD 创建的具体实例

### 12.1.3 CRD 的优势
1. **扩展性**：无需修改 Kubernetes 核心代码即可扩展功能
2. **标准化**：使用 Kubernetes 原生 API 管理自定义资源
3. **生态集成**：与 Kubernetes 生态工具（如 kubectl、Helm）无缝集成
4. **声明式管理**：支持声明式配置和自动化管理

## 12.2 创建自定义资源定义（CRD）

### 12.2.1 基本 CRD 示例
创建一个简单的应用配置 CRD：

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: appconfigs.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              replicas:
                type: integer
              image:
                type: string
  scope: Namespaced
  names:
    plural: appconfigs
    singular: appconfig
    kind: AppConfig
    shortNames:
    - ac
```

应用 CRD：
```bash
kubectl apply -f appconfig-crd.yaml
```

### 12.2.2 创建自定义资源实例
```yaml
apiVersion: example.com/v1
kind: AppConfig
metadata:
  name: my-app
spec:
  replicas: 3
  image: nginx:latest
```

### 12.2.3 验证 CRD 和自定义资源
```bash
# 查看 CRD
kubectl get crd

# 查看自定义资源
kubectl get appconfigs

# 查看自定义资源详细信息
kubectl describe appconfig my-app
```

## 12.3 CRD 高级特性

### 12.3.1 数据验证
使用 OpenAPI v3 schema 定义数据验证规则：

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: appconfigs.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required:
            - replicas
            - image
            properties:
              replicas:
                type: integer
                minimum: 1
                maximum: 10
              image:
                type: string
                pattern: '^[a-zA-Z0-9/]+:[a-zA-Z0-9_.-]+$'
              ports:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    port:
                      type: integer
                      minimum: 1
                      maximum: 65535
                  required:
                  - port
        required:
        - spec
  scope: Namespaced
  names:
    plural: appconfigs
    singular: appconfig
    kind: AppConfig
```

### 12.3.2 子资源支持
启用状态子资源和扩展资源：

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: appconfigs.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              replicas:
                type: integer
              image:
                type: string
          status:
            type: object
            properties:
              phase:
                type: string
              replicas:
                type: integer
    # 启用子资源
    subresources:
      status: {}
      scale:
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.replicas
  scope: Namespaced
  names:
    plural: appconfigs
    singular: appconfig
    kind: AppConfig
```

### 12.3.3 打印列定义
自定义 kubectl get 输出列：

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: appconfigs.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              replicas:
                type: integer
              image:
                type: string
          status:
            type: object
            properties:
              phase:
                type: string
    additionalPrinterColumns:
    - name: Replicas
      type: integer
      jsonPath: .spec.replicas
    - name: Image
      type: string
      jsonPath: .spec.image
    - name: Phase
      type: string
      jsonPath: .status.phase
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
  scope: Namespaced
  names:
    plural: appconfigs
    singular: appconfig
    kind: AppConfig
```

## 12.4 Operator 模式

### 12.4.1 什么是 Operator
Operator 是一种 Kubernetes 扩展模式，它使用自定义资源和控制器来管理复杂应用程序的生命周期。Operator 将运维知识编码到软件中，实现应用程序的自动化管理。

### 12.4.2 Operator 的核心组件
1. **自定义资源定义（CRD）**：定义应用程序的配置和状态
2. **控制器（Controller）**：监视自定义资源变化并执行相应操作
3. **Operator 逻辑**：实现应用程序的部署、配置、升级、备份等操作

### 12.4.3 Operator 工作原理
1. 控制器监视自定义资源的变化
2. 当资源发生变化时，控制器对比期望状态和当前状态
3. 控制器执行必要的操作使当前状态接近期望状态
4. 控制器更新资源状态

## 12.5 使用 Operator SDK 开发 Operator

### 12.5.1 安装 Operator SDK
```bash
# 下载 Operator SDK
curl -LO https://github.com/operator-framework/operator-sdk/releases/download/v1.24.0/operator-sdk_linux_amd64
chmod +x operator-sdk_linux_amd64
sudo mv operator-sdk_linux_amd64 /usr/local/bin/operator-sdk
```

### 12.5.2 创建 Operator 项目
```bash
# 创建项目目录
mkdir my-operator
cd my-operator

# 初始化 Operator 项目
operator-sdk init --domain=example.com --repo=github.com/example/my-operator
```

### 12.5.3 创建 API 和控制器
```bash
# 创建 API
operator-sdk create api --group=apps --version=v1alpha1 --kind=MyApp --resource --controller
```

### 12.5.4 定义 API 类型
编辑 `api/v1alpha1/myapp_types.go`：

```go
type MyAppSpec struct {
  // INSERT ADDITIONAL SPEC FIELDS - desired state of cluster
  Replicas int32  `json:"replicas"`
  Image    string `json:"image"`
}

type MyAppStatus struct {
  // INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
  Phase  string `json:"phase,omitempty"`
  Reason string `json:"reason,omitempty"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// MyApp is the Schema for the myapps API
type MyApp struct {
  metav1.TypeMeta   `json:",inline"`
  metav1.ObjectMeta `json:"metadata,omitempty"`

  Spec   MyAppSpec   `json:"spec,omitempty"`
  Status MyAppStatus `json:"status,omitempty"`
}
```

### 12.5.5 实现控制器逻辑
编辑 `controllers/myapp_controller.go`：

```go
func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
  log := r.Log.WithValues("myapp", req.NamespacedName)

  // 获取 MyApp 实例
  myapp := &appsv1alpha1.MyApp{}
  err := r.Get(ctx, req.NamespacedName, myapp)
  if err != nil {
    if errors.IsNotFound(err) {
      // 资源已删除
      return ctrl.Result{}, nil
    }
    // 其他错误
    return ctrl.Result{}, err
  }

  // 创建或更新 Deployment
  deployment := &appsv1.Deployment{}
  deployment.Name = myapp.Name
  deployment.Namespace = myapp.Namespace
  deployment.Spec.Replicas = &myapp.Spec.Replicas
  deployment.Spec.Selector = &metav1.LabelSelector{
    MatchLabels: map[string]string{
      "app": myapp.Name,
    },
  }
  deployment.Spec.Template.Spec.Containers = []corev1.Container{
    {
      Name:  "app",
      Image: myapp.Spec.Image,
    },
  }

  // 设置控制器引用
  if err := ctrl.SetControllerReference(myapp, deployment, r.Scheme); err != nil {
    return ctrl.Result{}, err
  }

  // 创建或更新 Deployment
  _, err = ctrl.CreateOrUpdate(ctx, r.Client, deployment, func() error {
    // 更新 Deployment 规格
    deployment.Spec.Replicas = &myapp.Spec.Replicas
    deployment.Spec.Template.Spec.Containers[0].Image = myapp.Spec.Image
    return nil
  })
  if err != nil {
    log.Error(err, "Failed to create or update Deployment")
    return ctrl.Result{}, err
  }

  // 更新状态
  myapp.Status.Phase = "Running"
  if err := r.Status().Update(ctx, myapp); err != nil {
    log.Error(err, "Failed to update MyApp status")
    return ctrl.Result{}, err
  }

  return ctrl.Result{}, nil
}
```

### 12.5.6 生成 CRD 清单
```bash
# 生成 CRD
make manifests

# 生成代码
make generate
```

### 12.5.7 构建和部署 Operator
```bash
# 构建 Operator 镜像
make docker-build docker-push IMG=example/my-operator:v0.0.1

# 部署 Operator
make deploy IMG=example/my-operator:v0.0.1
```

## 12.6 部署和使用自定义 Operator

### 12.6.1 部署 CRD
```bash
# 部署 CRD
kubectl apply -f config/crd/bases
```

### 12.6.2 创建自定义资源实例
```yaml
apiVersion: apps.example.com/v1alpha1
kind: MyApp
metadata:
  name: my-app-instance
spec:
  replicas: 3
  image: nginx:latest
```

### 12.6.3 验证 Operator 工作
```bash
# 查看自定义资源
kubectl get myapps

# 查看由 Operator 创建的 Deployment
kubectl get deployments

# 查看 Operator 日志
kubectl logs -n my-operator-system deployment/my-operator-controller-manager -c manager
```

## 12.7 实验：创建和部署自定义 Operator

### 实验目标
通过实际操作掌握自定义资源定义（CRD）和 Operator 的创建、部署和使用方法。

### 实验环境准备
1. 安装 Kubernetes 集群（推荐使用 Kind 或 Minikube）
2. 安装 kubectl 命令行工具
3. 安装 Operator SDK

### 实验步骤

1. **创建 Operator 项目**
```bash
# 创建项目目录
mkdir visitor-operator
cd visitor-operator

# 初始化 Operator 项目
operator-sdk init --domain=example.com --repo=github.com/example/visitor-operator
```

2. **创建 API 和控制器**
```bash
# 创建 API
operator-sdk create api --group=web --version=v1alpha1 --kind=VisitorApp --resource --controller
```

3. **定义 API 类型**
编辑 `api/v1alpha1/visitorapp_types.go`，添加以下字段：

```go
type VisitorAppSpec struct {
  Size    int32  `json:"size"`
  Version string `json:"version"`
}

type VisitorAppStatus struct {
  Nodes []string `json:"nodes"`
}
```

4. **实现控制器逻辑**
编辑 `controllers/visitorapp_controller.go`，实现以下功能：
- 创建 Deployment 运行 visitor-app 容器
- 创建 Service 暴露应用
- 更新状态信息

```go
func (r *VisitorAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
  log := r.Log.WithValues("visitorapp", req.NamespacedName)

  // 获取 VisitorApp 实例
  visitorApp := &webv1alpha1.VisitorApp{}
  err := r.Get(ctx, req.NamespacedName, visitorApp)
  if err != nil {
    if errors.IsNotFound(err) {
      return ctrl.Result{}, nil
    }
    return ctrl.Result{}, err
  }

  // 创建或更新 Deployment
  deploy := &appsv1.Deployment{
    ObjectMeta: metav1.ObjectMeta{
      Name:      visitorApp.Name,
      Namespace: visitorApp.Namespace,
    },
  }

  _, err = ctrl.CreateOrUpdate(ctx, r.Client, deploy, func() error {
    // 设置 Deployment 规格
    deploy.Spec.Replicas = &visitorApp.Spec.Size
    deploy.Spec.Selector = &metav1.LabelSelector{
      MatchLabels: map[string]string{
        "app": visitorApp.Name,
      },
    }
    deploy.Spec.Template.Spec.Containers = []corev1.Container{
      {
        Name:  "visitor-app",
        Image: fmt.Sprintf("nginx:%s", visitorApp.Spec.Version),
        Ports: []corev1.ContainerPort{
          {
            ContainerPort: 80,
          },
        },
      },
    }
    deploy.Spec.Template.ObjectMeta.Labels = map[string]string{
      "app": visitorApp.Name,
    }
    
    // 设置控制器引用
    return ctrl.SetControllerReference(visitorApp, deploy, r.Scheme)
  })
  
  if err != nil {
    log.Error(err, "Failed to create or update Deployment")
    return ctrl.Result{}, err
  }

  // 创建或更新 Service
  svc := &corev1.Service{
    ObjectMeta: metav1.ObjectMeta{
      Name:      visitorApp.Name + "-service",
      Namespace: visitorApp.Namespace,
    },
  }

  _, err = ctrl.CreateOrUpdate(ctx, r.Client, svc, func() error {
    svc.Spec.Selector = map[string]string{
      "app": visitorApp.Name,
    }
    svc.Spec.Ports = []corev1.ServicePort{
      {
        Port:       80,
        TargetPort: intstr.FromInt(80),
      },
    }
    svc.Spec.Type = corev1.ServiceTypeClusterIP
    
    return ctrl.SetControllerReference(visitorApp, svc, r.Scheme)
  })
  
  if err != nil {
    log.Error(err, "Failed to create or update Service")
    return ctrl.Result{}, err
  }

  // 更新状态
  nodeList := &corev1.NodeList{}
  if err := r.List(ctx, nodeList); err != nil {
    log.Error(err, "Failed to list nodes")
    return ctrl.Result{}, err
  }

  var nodeNames []string
  for _, node := range nodeList.Items {
    nodeNames = append(nodeNames, node.Name)
  }

  visitorApp.Status.Nodes = nodeNames
  if err := r.Status().Update(ctx, visitorApp); err != nil {
    log.Error(err, "Failed to update VisitorApp status")
    return ctrl.Result{}, err
  }

  return ctrl.Result{}, nil
}
```

5. **生成 CRD 和代码**
```bash
# 生成 CRD
make manifests

# 生成代码
make generate
```

6. **部署 Operator**
```bash
# 安装 CRD
make install

# 部署控制器到集群
make deploy IMG=example/visitor-operator:v0.0.1
```

7. **创建自定义资源实例**
```yaml
apiVersion: web.example.com/v1alpha1
kind: VisitorApp
metadata:
  name: my-visitor-app
spec:
  size: 2
  version: "1.20"
```

8. **验证部署结果**
```bash
# 查看自定义资源
kubectl get visitorapps

# 查看创建的 Deployment 和 Service
kubectl get deployments,services

# 查看应用状态
kubectl get visitorapp my-visitor-app -o yaml

# 测试应用访问
kubectl port-forward service/my-visitor-app-service 8080:80
# 在浏览器中访问 http://localhost:8080
```

## 12.8 故障排除

### 12.8.1 CRD 相关问题
1. **CRD 未生效**
```bash
# 检查 CRD 是否已创建
kubectl get crd | grep <crd-name>

# 检查 CRD 状态
kubectl describe crd <crd-name>
```

2. **自定义资源验证失败**
```bash
# 查看详细错误信息
kubectl describe <resource-type> <resource-name>

# 检查 CRD 验证规则
kubectl get crd <crd-name> -o yaml
```

### 12.8.2 Operator 相关问题
1. **控制器未响应**
```bash
# 查看控制器日志
kubectl logs -n <operator-namespace> deployment/<operator-name>-controller-manager -c manager

# 检查控制器状态
kubectl get pods -n <operator-namespace>
```

2. **权限问题**
```bash
# 检查 RBAC 配置
kubectl get roles,rolebindings -n <operator-namespace>

# 检查 ServiceAccount
kubectl get serviceaccount -n <operator-namespace>
```

3. **资源创建失败**
```bash
# 查看事件
kubectl get events

# 检查资源状态
kubectl describe <resource-type> <resource-name>
```

## 12.9 最佳实践

### 12.9.1 CRD 设计最佳实践
1. **合理的 API 版本管理**：使用 v1alpha1、v1beta1、v1 等版本标识
2. **清晰的命名规范**：使用有意义的组名、版本和资源名
3. **完整的数据验证**：定义详细的 OpenAPI v3 schema 验证规则
4. **状态子资源**：为自定义资源启用状态子资源
5. **打印列配置**：自定义 kubectl get 输出列

### 12.9.2 Operator 开发最佳实践
1. **幂等性设计**：确保 Reconcile 函数可以安全地多次执行
2. **错误处理**：正确处理和返回错误，避免无限重试
3. **资源所有权**：使用控制器引用建立资源所有权关系
4. **状态更新**：及时更新自定义资源状态
5. **日志记录**：添加详细的日志记录便于调试
6. **测试覆盖**：编写单元测试和集成测试

### 12.9.3 安全最佳实践
1. **最小权限原则**：为 Operator 配置最小必要权限
2. **镜像安全**：使用安全的基础镜像和扫描工具
3. **网络安全**：配置网络策略限制 Operator 访问
4. **审计日志**：启用审计日志记录关键操作

## 总结
本章我们深入学习了 Kubernetes 的自定义资源定义（CRD）和 Operator 模式。通过创建 CRD，我们可以扩展 Kubernetes API 以支持自定义资源类型。通过开发 Operator，我们可以实现复杂应用程序的自动化管理。这些高级特性使得 Kubernetes 成为一个真正可扩展的平台，能够管理各种类型的应用和服务。掌握这些技能对于构建企业级 Kubernetes 解决方案至关重要。