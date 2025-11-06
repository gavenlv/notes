# 第4章：Helm部署策略

## 🎯 本章目标

- 掌握Helm的部署和升级策略
- 理解回滚机制和版本管理
- 学会使用生命周期钩子
- 掌握多环境部署策略

## 🔄 部署和升级策略

### 4.1 部署策略类型

#### 蓝绿部署（Blue-Green）
```yaml
# values-blue.yaml
replicaCount: 3
service:
  selector: 
    version: blue
image:
  tag: v1.0.0

# values-green.yaml  
replicaCount: 3
service:
  selector:
    version: green
image:
  tag: v2.0.0
```

#### 金丝雀部署（Canary）
```yaml
# values-canary.yaml
replicaCount: 1  # 少量实例进行测试
image:
  tag: v2.0.0
service:
  annotations:
    traffic.sidecar.istio.io/canary: "true"
    traffic.sidecar.istio.io/canaryWeight: "10"
```

#### 滚动更新（Rolling Update）
```yaml
# 默认策略
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 25%
```

### 4.2 升级命令详解

```bash
# 基础升级
helm upgrade my-release ./my-chart

# 带参数升级
helm upgrade my-release ./my-chart --set replicaCount=3

# 使用values文件升级
helm upgrade my-release ./my-chart -f values-prod.yaml

# 强制升级（即使有错误也继续）
helm upgrade my-release ./my-chart --force

# 等待升级完成
helm upgrade my-release ./my-chart --wait --timeout=10m

# 原子升级（要么全部成功，要么回滚）
helm upgrade my-release ./my-chart --atomic
```

### 4.3 升级策略配置

在values.yaml中配置升级策略：

```yaml
# 部署策略配置
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0

# 资源更新策略
updateStrategy:
  type: OnDelete  # 或 RollingUpdate

# Pod中断预算
podDisruptionBudget:
  enabled: true
  minAvailable: 1
  maxUnavailable: 1
```

## 🔙 回滚和版本管理

### 4.4 回滚机制

```bash
# 查看发布历史
helm history my-release

# 回滚到上一个版本
helm rollback my-release

# 回滚到特定版本
helm rollback my-release 2

# 获取发布详情
helm get manifest my-release
helm get values my-release
helm get hooks my-release

# 比较版本差异
helm get manifest my-release --revision=1 > v1.yaml
helm get manifest my-release --revision=2 > v2.yaml
diff v1.yaml v2.yaml
```

### 4.5 版本管理最佳实践

```bash
# 为每个版本添加注释
helm upgrade my-release ./my-chart --description="Deploy feature X"

# 使用语义化版本
helm package . --version 1.2.3

# 版本锁定
helm dependency update --version-lock
```

## ⚡ 生命周期钩子

### 4.6 钩子类型和使用

#### 预安装钩子（pre-install）
```yaml
# templates/pre-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" . }}-pre-install
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      containers:
      - name: pre-install
        image: busybox
        command: ['sh', '-c', 'echo "Running pre-install checks"']
      restartPolicy: Never
```

#### 后安装钩子（post-install）
```yaml
# templates/post-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" . }}-post-install
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      containers:
      - name: post-install
        image: busybox
        command: ['sh', '-c', 'echo "Running post-install setup"']
      restartPolicy: Never
```

#### 预升级钩子（pre-upgrade）
```yaml
# templates/pre-upgrade-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" . }}-pre-upgrade
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      containers:
      - name: pre-upgrade
        image: busybox
        command: ['sh', '-c', 'echo "Running pre-upgrade checks"']
      restartPolicy: Never
```

### 4.7 钩子权重和删除策略

```yaml
# 钩子权重控制执行顺序
"helm.sh/hook-weight": "-10"  # 最先执行
"helm.sh/hook-weight": "0"     # 默认
"helm.sh/hook-weight": "10"    # 最后执行

# 删除策略
"helm.sh/hook-delete-policy": hook-succeeded      # 钩子成功后删除
"helm.sh/hook-delete-policy": hook-failed         # 钩子失败后删除
"helm.sh/hook-delete-policy": before-hook-creation # 创建新钩子前删除旧钩子
```

## 🌍 多环境部署策略

### 4.8 环境特定配置

#### 开发环境（dev）
```yaml
# values-dev.yaml
replicaCount: 1
image:
  tag: latest
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
debug: true
```

#### 测试环境（test）
```yaml
# values-test.yaml
replicaCount: 2
image:
  tag: stable
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
monitoring:
  enabled: true
```

#### 生产环境（prod）
```yaml
# values-prod.yaml
replicaCount: 3
image:
  tag: v1.0.0
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
backup:
  enabled: true
```

### 4.9 环境隔离策略

```bash
# 使用命名空间隔离环境
helm install my-app ./my-chart -n dev
helm install my-app ./my-chart -n test
helm install my-app ./my-chart -n prod

# 环境特定的values文件
helm install my-app ./my-chart -f values-base.yaml -f values-dev.yaml
helm install my-app ./my-chart -f values-base.yaml -f values-prod.yaml

# 使用环境变量
helm install my-app ./my-chart --set environment=dev
helm install my-app ./my-chart --set environment=prod
```

## 🔒 安全和权限控制

### 4.10 RBAC配置

```yaml
# templates/rbac.yaml
{{- if .Values.rbac.enabled }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "myapp.fullname" . }}
  namespace: {{ .Release.Namespace }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "myapp.fullname" . }}
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "myapp.fullname" . }}
subjects:
- kind: ServiceAccount
  name: {{ include "myapp.fullname" . }}
roleRef:
  kind: Role
  name: {{ include "myapp.fullname" . }}
  apiGroup: rbac.authorization.k8s.io
{{- end }}
```

### 4.11 安全最佳实践

```bash
# 使用安全上下文
helm install my-app ./my-chart --set securityContext.runAsNonRoot=true

# 限制权限
helm install my-app ./my-chart --set serviceAccount.create=false

# 使用网络策略
helm install my-app ./my-chart --set networkPolicy.enabled=true
```

## 🧪 实验：部署策略实战

### 实验1：蓝绿部署实践

```bash
# 部署蓝色版本
helm install my-app-blue ./my-chart -f values-blue.yaml

# 部署绿色版本
helm install my-app-green ./my-chart -f values-green.yaml

# 切换流量到绿色版本
kubectl patch service my-app-service -p '{"spec":{"selector":{"version":"green"}}}'

# 验证绿色版本
kubectl get pods -l version=green

# 清理蓝色版本
helm uninstall my-app-blue
```

### 实验2：金丝雀部署实践

```bash
# 部署稳定版本
helm install my-app ./my-chart --set replicaCount=3

# 部署金丝雀版本
helm install my-app-canary ./my-chart -f values-canary.yaml

# 逐步增加金丝雀流量
kubectl patch service my-app-service -p '{"metadata":{"annotations":{"traffic.sidecar.istio.io/canaryWeight":"50"}}}'

# 验证金丝雀版本
curl http://my-app-service

# 完全切换到新版本
helm upgrade my-app ./my-chart --set image.tag=v2.0.0
helm uninstall my-app-canary
```

### 实验3：生命周期钩子实践

```bash
# 部署带钩子的应用
helm install my-app ./my-chart

# 查看钩子执行状态
kubectl get jobs -l "helm.sh/hook"

# 升级应用（触发升级钩子）
helm upgrade my-app ./my-chart --set image.tag=v2.0.0

# 查看钩子日志
kubectl logs job/my-app-pre-upgrade-xxxxx
```

## 📝 本章总结

### 关键知识点

1. **部署策略**：蓝绿部署、金丝雀部署、滚动更新
2. **升级管理**：升级命令、参数配置、策略控制
3. **回滚机制**：版本历史、回滚操作、差异比较
4. **生命周期钩子**：各种钩子类型、权重控制、删除策略
5. **多环境部署**：环境隔离、配置管理、安全控制

### 实践技能

- ✅ 能够实施各种部署策略
- ✅ 能够管理应用版本和回滚
- ✅ 能够配置和使用生命周期钩子
- ✅ 能够实现多环境部署隔离
- ✅ 能够配置安全策略和权限控制

### 最佳实践

1. **渐进式部署**：使用金丝雀部署降低风险
2. **版本控制**：为每个版本添加描述信息
3. **钩子谨慎使用**：避免钩子导致部署失败
4. **环境隔离**：使用命名空间和配置分离环境
5. **安全第一**：配置适当的安全上下文和权限

### 下一步学习

在下一章中，我们将学习企业级最佳实践，包括Chart仓库管理、CI/CD集成、监控告警等生产环境部署的高级主题。

---

**💡 提示：完成本章学习后，建议进入 `code/multi-service/` 目录进行实践练习，巩固所学知识。**