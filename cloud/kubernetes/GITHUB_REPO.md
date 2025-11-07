# Kubernetes 学习指南示例代码仓库

这个仓库包含了 Kubernetes 学习指南中所有章节的示例代码和配置文件，旨在帮助读者通过实际操作加深对 Kubernetes 的理解。

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

## 使用说明

### 克隆仓库

```bash
git clone https://github.com/your-username/k8s-example-code.git
cd k8s-example-code
```

### 环境要求

- Kubernetes 1.20 或更高版本
- kubectl 命令行工具
- Docker 或其他容器运行时
- Helm (部分章节需要)

### 应用示例配置

```bash
# 应用特定章节的示例配置
kubectl apply -f chapter03-pod-details/simple-pod.yaml

# 应用整个章节的配置
kubectl apply -f chapter04-controllers/
```

### 实验环境搭建

建议使用以下任一方式搭建实验环境：

1. **Minikube** (推荐用于本地开发)
```bash
minikube start
```

2. **Kind** (Kubernetes in Docker)
```bash
kind create cluster
```

3. **K3s** (轻量级 Kubernetes)
```bash
curl -sfL https://get.k3s.io | sh -
```

## 各章节内容概览

### 第1章：Kubernetes简介和架构
- Kubernetes 架构图示例
- 组件交互示意图

### 第2章：安装和配置
- kubeadm 配置文件示例
- kubelet 配置文件示例
- kubectl 命令别名配置
- Dashboard 管理员用户配置

### 第3章：核心概念和资源对象
- 简单 Pod 配置示例
- 多容器 Pod 配置示例
- Init Container Pod 配置示例
- 带卷的 Pod 配置示例

### 第4章：Pod管理和生命周期
- Deployment 配置示例
- ReplicaSet 配置示例
- DaemonSet 配置示例
- StatefulSet 配置示例
- Job 配置示例
- CronJob 配置示例
- 生命周期钩子示例

### 第5章：服务发现和网络
- ClusterIP 服务示例
- NodePort 服务示例
- LoadBalancer 服务示例
- Headless 服务示例
- Ingress 配置示例
- 网络策略示例
- Endpoint 配置示例

### 第6章：存储管理
- emptyDir 卷示例
- hostPath 卷示例
- PersistentVolume 示例
- PersistentVolumeClaim 示例
- StorageClass 示例
- ConfigMap 卷示例
- Secret 卷示例

### 第7章：配置管理（ConfigMap和Secret）
- 字面值 ConfigMap 示例
- 文件 ConfigMap 示例
- 通用 Secret 示例
- Docker 镜像仓库 Secret 示例
- 环境变量中使用 ConfigMap 示例
- 卷中使用 Secret 示例

### 第8章：安全机制和权限控制
- RBAC Role 示例
- RBAC RoleBinding 示例
- RBAC ClusterRole 示例
- RBAC ClusterRoleBinding 示例
- ServiceAccount 示例
- Pod 安全上下文示例
- 容器安全上下文示例

### 第9章：监控、日志和调试
- 存活探针示例
- 就绪探针示例
- 启动探针示例
- Fluentd 配置示例
- Prometheus 配置示例

### 第10章：集群维护和升级
- 节点维护示例
- etcd 备份脚本
- etcd 恢复脚本
- 升级检查清单

### 第11章：高级调度和资源管理
- 节点亲和性示例
- Pod 亲和性示例
- 污点和容忍示例
- 资源配额示例
- 限制范围示例
- 优先级类示例

### 第12章：自定义资源和Operator
- CRD 定义示例
- CR 实例示例
- Operator 部署示例
- Webhook 配置示例
- 验证模式示例

### 第13章：生产环境最佳实践
- 生产环境 Deployment 示例
- 水平自动伸缩示例
- Pod 干扰预算示例
- Pod 中断预算示例
- 资源监控示例

### 第14章：故障排查和性能优化
- 调试 Pod 示例
- 资源优化示例
- 网络调试示例
- 性能监控示例

## 贡献指南

欢迎贡献更多的示例代码和改进现有示例：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本示例代码仓库采用 MIT License 开源许可证。

## 联系方式

如果您有任何问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至 [your-email@example.com]

感谢您使用 Kubernetes 学习指南示例代码仓库！