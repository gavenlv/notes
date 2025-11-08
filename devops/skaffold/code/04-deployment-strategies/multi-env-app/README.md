# 多环境部署策略示例

## 项目概述

这是一个完整的多环境Skaffold部署示例，演示如何在开发、预发布和生产环境中使用不同的部署策略。

## 目录结构

```
multi-env-app/
├── README.md                    # 项目说明
├── skaffold.yaml                # 主配置文件
├── Dockerfile                   # 应用镜像构建
├── app/                         # 应用源码
│   └── main.go
├── k8s/                         # Kubernetes资源文件
│   ├── base/                    # 基础配置
│   │   ├── kustomization.yaml
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── dev/                     # 开发环境
│   │   ├── kustomization.yaml
│   │   ├── configmap.yaml
│   │   └── patch-deployment.yaml
│   ├── staging/                 # 预发布环境
│   │   ├── kustomization.yaml
│   │   ├── hpa.yaml
│   │   └── patch-deployment.yaml
│   └── prod/                    # 生产环境
│       ├── kustomization.yaml
│       ├── hpa.yaml
│       ├── pdb.yaml
│       └── patch-deployment.yaml
├── charts/                      # Helm Chart
│   └── my-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       └── values/
│           ├── dev.yaml
│           ├── staging.yaml
│           └── prod.yaml
└── scripts/                     # 辅助脚本
    ├── deploy.sh
    └── cleanup.sh
```

## 部署策略

### 1. kubectl部署（默认）
```bash
# 开发环境部署
skaffold dev

# 预发布环境部署
skaffold dev -p staging

# 生产环境部署
skaffold dev -p prod
```

### 2. kustomize部署
```bash
# 使用kustomize部署开发环境
skaffold dev --profile kustomize-dev

# 使用kustomize部署生产环境
skaffold dev --profile kustomize-prod
```

### 3. Helm部署
```bash
# 使用Helm部署开发环境
skaffold dev --profile helm-dev

# 使用Helm部署生产环境
skaffold dev --profile helm-prod
```

## 环境差异

### 开发环境
- 单副本部署
- 最小资源请求
- 调试工具启用
- 本地镜像仓库

### 预发布环境
- 2副本部署
- 中等资源分配
- 自动扩缩容
- 内部镜像仓库

### 生产环境
- 3+副本部署
- 完整资源分配
- Pod中断预算
- 安全加固配置

## 快速开始

1. **克隆项目**
   ```bash
   cd multi-env-app
   ```

2. **开发环境部署**
   ```bash
   skaffold dev
   ```

3. **切换环境**
   ```bash
   # 预发布环境
   skaffold dev -p staging
   
   # 生产环境
   skaffold dev -p prod
   ```

4. **清理资源**
   ```bash
   skaffold delete
   ```

## 配置说明

### 环境变量配置
```bash
# 镜像仓库配置
export DOCKER_REGISTRY=my-registry.com

# 命名空间配置
export NAMESPACE_PREFIX=my-team

# 认证配置
export KUBECONFIG=~/.kube/config
```

### 性能调优
- 开发环境：快速启动，最小资源
- 预发布环境：性能测试，真实负载
- 生产环境：高可用，安全加固

## 注意事项

1. **权限配置**：确保有足够的Kubernetes权限
2. **镜像仓库**：配置正确的镜像仓库地址
3. **网络策略**：根据需要配置网络访问规则
4. **资源配额**：检查集群资源配额限制