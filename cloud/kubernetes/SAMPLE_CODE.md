# Kubernetes 学习指南示例代码

本指南旨在为 Kubernetes 学习指南中的所有示例代码提供集中管理和使用说明。

## 仓库结构

```
k8s-example-code/
├── chapter01-basic-concepts/
├── chapter02-environment-setup/
├── chapter03-pod-details/
├── chapter04-controllers/
├── chapter05-networking/
├── chapter06-storage/
├── chapter07-config-management/
├── chapter08-security/
├── chapter09-monitoring-logging/
├── chapter10-cluster-maintenance/
├── chapter11-advanced-scheduling/
├── chapter12-custom-resources/
├── chapter13-production-best-practices/
├── chapter14-troubleshooting/
├── utils/
└── README.md
```

## 各章节示例代码说明

### 第1章：Kubernetes简介和架构
- 架构图示例
- 组件交互示意图

### 第2章：安装和配置
```
chapter02-environment-setup/
├── kubeadm-config.yaml          # kubeadm 配置文件示例
├── kubelet-config.yaml          # kubelet 配置文件示例
├── kubectl-alias.sh             # kubectl 命令别名配置
└── dashboard-adminuser.yaml     # Dashboard 管理员用户配置
```

### 第3章：核心概念和资源对象
```
chapter03-pod-details/
├── simple-pod.yaml              # 简单 Pod 配置示例
├── multi-container-pod.yaml     # 多容器 Pod 配置示例
├── init-container-pod.yaml      # Init Container Pod 配置示例
└── pod-with-volumes.yaml        # 带卷的 Pod 配置示例
```

### 第4章：Pod管理和生命周期
```
chapter04-controllers/
├── deployment-example.yaml      # Deployment 配置示例
├── replicaset-example.yaml      # ReplicaSet 配置示例
├── daemonset-example.yaml       # DaemonSet 配置示例
├── statefulset-example.yaml     # StatefulSet 配置示例
├── job-example.yaml             # Job 配置示例
├── cronjob-example.yaml         # CronJob 配置示例
└── lifecycle-hooks.yaml         # 生命周期钩子示例
```

### 第5章：服务发现和网络
```
chapter05-networking/
├── clusterip-service.yaml       # ClusterIP 服务示例
├── nodeport-service.yaml        # NodePort 服务示例
├── loadbalancer-service.yaml    # LoadBalancer 服务示例
├── headless-service.yaml        # Headless 服务示例
├── ingress-example.yaml         # Ingress 配置示例
├── network-policy.yaml          # 网络策略示例
└── endpoint-example.yaml        # Endpoint 配置示例
```

### 第6章：存储管理
```
chapter06-storage/
├── emptyDir-volume.yaml         # emptyDir 卷示例
├── hostPath-volume.yaml         # hostPath 卷示例
├── persistent-volume.yaml       # PersistentVolume 示例
├── persistent-volume-claim.yaml # PersistentVolumeClaim 示例
├── storage-class.yaml           # StorageClass 示例
├── configmap-volume.yaml        # ConfigMap 卷示例
└── secret-volume.yaml           # Secret 卷示例
```

### 第7章：配置管理（ConfigMap和Secret）
```
chapter07-config-management/
├── configmap-literal.yaml       # 字面值 ConfigMap 示例
├── configmap-file.yaml          # 文件 ConfigMap 示例
├── secret-generic.yaml          # 通用 Secret 示例
├── secret-docker.yaml           # Docker 镜像仓库 Secret 示例
├── configmap-env.yaml           # 环境变量中使用 ConfigMap 示例
└── secret-volume.yaml           # 卷中使用 Secret 示例
```

### 第8章：安全机制和权限控制
```
chapter08-security/
├── rbac-role.yaml               # RBAC Role 示例
├── rbac-rolebinding.yaml        # RBAC RoleBinding 示例
├── rbac-clusterrole.yaml        # RBAC ClusterRole 示例
├── rbac-clusterrolebinding.yaml # RBAC ClusterRoleBinding 示例
├── service-account.yaml         # ServiceAccount 示例
├── pod-security-context.yaml    # Pod 安全上下文示例
└── container-security-context.yaml # 容器安全上下文示例
```

### 第9章：监控、日志和调试
```
chapter09-monitoring-logging/
├── liveness-probe.yaml          # 存活探针示例
├── readiness-probe.yaml         # 就绪探针示例
├── startup-probe.yaml           # 启动探针示例
├── fluentd-config.yaml          # Fluentd 配置示例
└── prometheus-config.yaml       # Prometheus 配置示例
```

### 第10章：集群维护和升级
```
chapter10-cluster-maintenance/
├── node-maintenance.yaml        # 节点维护示例
├── backup-etcd.yaml             # etcd 备份脚本
├── restore-etcd.yaml            # etcd 恢复脚本
└── upgrade-checklist.md         # 升级检查清单
```

### 第11章：高级调度和资源管理
```
chapter11-advanced-scheduling/
├── node-affinity.yaml           # 节点亲和性示例
├── pod-affinity.yaml            # Pod 亲和性示例
├── taint-toleration.yaml        # 污点和容忍示例
├── resource-quota.yaml          # 资源配额示例
├── limit-range.yaml             # 限制范围示例
└── priority-class.yaml          # 优先级类示例
```

### 第12章：自定义资源和Operator
```
chapter12-custom-resources/
├── crd-definition.yaml          # CRD 定义示例
├── cr-instance.yaml             # CR 实例示例
├── operator-deployment.yaml     # Operator 部署示例
├── webhook-configuration.yaml   # Webhook 配置示例
└── validation-schema.yaml       # 验证模式示例
```

### 第13章：生产环境最佳实践
```
chapter13-production-best-practices/
├── production-deployment.yaml   # 生产环境 Deployment 示例
├── hpa-example.yaml             # 水平自动伸缩示例
├── pdb-example.yaml             # Pod 干扰预算示例
├── pod-disruption-budget.yaml   # Pod 中断预算示例
└── resource-monitoring.yaml     # 资源监控示例
```

### 第14章：故障排查和性能优化
```
chapter14-troubleshooting/
├── debugging-pod.yaml           # 调试 Pod 示例
├── resource-optimization.yaml   # 资源优化示例
├── network-debugging.yaml       # 网络调试示例
└── performance-monitoring.yaml  # 性能监控示例
```

## 使用说明

### 克隆仓库
```bash
git clone https://github.com/your-username/k8s-example-code.git
cd k8s-example-code
```

### 应用示例配置
```bash
# 应用特定章节的示例配置
kubectl apply -f chapter03-pod-details/simple-pod.yaml

# 应用整个章节的配置
kubectl apply -f chapter04-controllers/
```

### 修改和定制
所有示例都可以根据您的具体需求进行修改和定制。请确保在生产环境中使用前进行充分测试。

## 贡献指南

欢迎贡献更多的示例代码和改进现有示例：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本示例代码仓库采用 [MIT License](LICENSE) 开源许可证。