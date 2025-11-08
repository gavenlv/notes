# 多团队项目协作示例

## 概述

这个示例展示了如何在企业环境中使用Skaffold管理多个团队的项目协作，包括：
- 团队间的配置共享
- 统一的构建和部署流程
- 环境隔离和权限管理
- 跨团队依赖管理

## 项目结构

```
multi-team-project/
├── README.md
├── skaffold.yaml                    # 根配置
├── team-a/                          # A团队项目
│   ├── skaffold.yaml               # 团队特定配置
│   ├── src/                        # 源代码
│   └── k8s/                        # Kubernetes配置
├── team-b/                          # B团队项目
│   ├── skaffold.yaml
│   ├── src/
│   └── k8s/
├── shared-libraries/                # 共享库
│   ├── skaffold-base.yaml          # 基础配置
│   ├── common-utils/               # 公共工具
│   └── monitoring-configs/          # 监控配置
└── platform/                       # 平台团队配置
    ├── base-configs/               # 基础配置模板
    ├── security-policies/          # 安全策略
    └── ci-cd-templates/           # CI/CD模板
```

## 快速开始

### 1. 设置共享配置

```bash
# 克隆共享配置库
git clone https://github.com/company/shared-configs.git shared-libraries/

# 安装基础依赖
cd multi-team-project
skaffold config set --global default-repo registry.company.com
```

### 2. 团队A部署

```bash
# 切换到团队A目录
cd team-a

# 部署团队A应用
skaffold run --profile=development

# 验证部署
kubectl get pods -l team=team-a
```

### 3. 团队B部署

```bash
# 切换到团队B目录
cd team-b

# 部署团队B应用
skaffold run --profile=development

# 验证部署
kubectl get pods -l team=team-b
```

### 4. 跨团队协作部署

```bash
# 从根目录部署所有团队应用
cd multi-team-project
skaffold run --profile=collaboration

# 验证整体部署
kubectl get pods --all-namespaces -l environment=collaboration
```

## 配置说明

### 根配置 (skaffold.yaml)

```yaml
apiVersion: skaffold/v2beta29
kind: Config
metadata:
  name: multi-team-project
  description: "企业多团队项目协作配置"

# 导入共享配置
requires:
  - path: ./shared-libraries/skaffold-base.yaml
  - path: ./platform/base-configs/security.yaml

# 全局配置
build:
  local:
    push: false
  artifacts: []

deploy:
  kubectl:
    manifests: []

# 团队配置导入
profiles:
  - name: collaboration
    patches:
      - op: add
        path: /build/artifacts
        value:
          - requires:
              - path: ./team-a/skaffold.yaml
          - requires:
              - path: ./team-b/skaffold.yaml
      
  - name: team-a-only
    patches:
      - op: replace
        path: /build/artifacts
        value:
          - requires:
              - path: ./team-a/skaffold.yaml
      
  - name: team-b-only
    patches:
      - op: replace
        path: /build/artifacts
        value:
          - requires:
              - path: ./team-b/skaffold.yaml
```

### 团队A配置 (team-a/skaffold.yaml)

```yaml
apiVersion: skaffold/v2beta29
kind: Config
metadata:
  name: team-a-app
  team: team-a

# 继承共享配置
requires:
  - path: ../shared-libraries/skaffold-base.yaml

build:
  artifacts:
    - image: team-a/frontend
      context: ./src/frontend
      docker:
        dockerfile: Dockerfile
      sync:
        manual:
          - src: "src/**/*.js"
            dest: /app
    
    - image: team-a/backend
      context: ./src/backend
      docker:
        dockerfile: Dockerfile
        target: production

deploy:
  kubectl:
    manifests:
      - k8s/namespace.yaml
      - k8s/deployment.yaml
      - k8s/service.yaml
      - k8s/ingress.yaml

profiles:
  - name: development
    patches:
      - op: replace
        path: /build/artifacts/0/image
        value: team-a/frontend-dev
      - op: replace
        path: /build/artifacts/1/image
        value: team-a/backend-dev
      - op: replace
        path: /deploy/kubectl/manifests
        value:
          - k8s/overlays/development/
```

### 团队B配置 (team-b/skaffold.yaml)

```yaml
apiVersion: skaffold/v2beta29
kind: Config
metadata:
  name: team-b-app
  team: team-b

# 继承共享配置
requires:
  - path: ../shared-libraries/skaffold-base.yaml

build:
  artifacts:
    - image: team-b/api-service
      context: ./src
      docker:
        dockerfile: Dockerfile
      kaniko:
        cache: {}
    
    - image: team-b/worker
      context: ./src/worker
      docker:
        dockerfile: Dockerfile
        target: worker

deploy:
  helm:
    releases:
      - name: team-b-api
        chartPath: ./charts/api
        valuesFiles:
          - ./charts/api/values.yaml
        namespace: team-b
        wait: true
        
      - name: team-b-worker
        chartPath: ./charts/worker
        valuesFiles:
          - ./charts/worker/values.yaml
        namespace: team-b
```

### 共享库配置 (shared-libraries/skaffold-base.yaml)

```yaml
apiVersion: skaffold/v2beta29
kind: Config
metadata:
  name: shared-base-config

# 全局构建配置
build:
  local:
    concurrency: 3
    useBuildkit: true
  
  # 安全扫描配置
test:
  - image: "*"
    structureTests:
      - ../security-tests/structure.yaml
    custom:
      - command: "trivy image --exit-code 1 --severity HIGH,CRITICAL {{.IMAGE}}"

# 全局部署配置
deploy:
  kubectl:
    flags:
      global:
        - --validate=true
        - --server-side=true

# 团队标签配置
profiles:
  - name: security
    patches:
      - op: add
        path: /build/artifacts/0/docker/buildArgs
        value:
          SECURITY_SCAN: "true"
          
  - name: performance
    patches:
      - op: add
        path: /build/artifacts/0/docker/buildArgs
        value:
          OPTIMIZE: "true"
```

## 协作工作流

### 1. 独立开发

每个团队可以独立开发自己的应用：

```bash
# 团队A开发流程
cd team-a
skaffold dev --profile=development

# 团队B开发流程  
cd team-b
skaffold dev --profile=development
```

### 2. 集成测试

团队间集成测试：

```bash
# 部署所有团队应用进行集成测试
cd multi-team-project
skaffold run --profile=integration

# 运行集成测试
skaffold test --profile=integration
```

### 3. 生产部署

协调的生产部署：

```bash
# 生产环境部署
skaffold run --profile=production

# 蓝绿部署验证
skaffold run --profile=blue-green
```

## 权限管理

### 命名空间隔离

```yaml
# team-a/k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-a
  labels:
    team: team-a
    environment: development
```

### RBAC配置

```yaml
# platform/security-policies/team-a-rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: team-a
  name: team-a-developer
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
```

## 最佳实践

### 1. 配置管理
- 使用共享配置避免重复
- 团队特定配置覆盖共享配置
- 版本控制所有配置变更

### 2. 依赖管理
- 明确定义团队间依赖关系
- 使用接口契约管理跨团队调用
- 定期同步共享库版本

### 3. 安全实践
- 每个团队独立的命名空间
- 最小权限原则
- 定期安全审计

这个多团队协作示例展示了如何在大规模企业环境中有效管理多个团队的Skaffold项目，确保配置一致性、安全性和可维护性。