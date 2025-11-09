# Jenkins容器化集成示例

本目录包含Jenkins与容器化技术（Docker、Kubernetes）集成的完整示例，展示如何构建云原生CI/CD流水线。

## 项目结构

```
07-container-integration/
├── docker-pipeline/            # Docker Pipeline集成
│   ├── Jenkinsfile            # 基础Docker Pipeline
│   ├── multi-stage-build/     # 多阶段构建
│   ├── image-security/       # 镜像安全扫描
│   ├── registry-integration/  # 镜像仓库集成
│   └── README.md
├── kubernetes-pipeline/       # Kubernetes Pipeline集成
│   ├── Jenkinsfile            # Kubernetes部署Pipeline
│   ├── helm-deployment/       # Helm部署
│   ├── canary-deployment/     # 金丝雀部署
│   ├── service-mesh/         # 服务网格集成
│   └── README.md
├── jenkins-x/                 # Jenkins X配置
│   ├── jx-requirements.yaml   # Jenkins X配置
│   ├── preview-environment/  # 预览环境
│   ├── gitops-workflow/      # GitOps工作流
│   └── README.md
├── cloud-native-ci-cd/        # 云原生CI/CD
│   ├── tekton-pipelines/      # Tekton Pipeline
│   ├── argocd-integration/    # ArgoCD集成
│   ├── gitlab-ci/            # GitLab CI集成
│   └── README.md
└── README.md                 # 本文档
```

## 功能特性

### 1. Docker Pipeline集成
- **容器化构建**：在Docker容器中运行构建步骤
- **镜像构建**：自动化构建和推送Docker镜像
- **安全扫描**：集成镜像安全扫描工具
- **多阶段构建**：优化镜像大小和构建效率

### 2. Kubernetes Pipeline集成
- **K8s部署**：自动化部署到Kubernetes集群
- **Helm集成**：使用Helm进行应用部署
- **金丝雀发布**：实现渐进式发布策略
- **服务网格**：集成Istio等服务网格

### 3. Jenkins X
- **云原生CI/CD**：基于Kubernetes的云原生CI/CD
- **GitOps工作流**：声明式配置管理
- **预览环境**：自动创建预览环境
- **流水线自动化**：自动化流水线创建

### 4. 云原生工具链
- **Tekton**：Kubernetes原生CI/CD工具
- **ArgoCD**：GitOps持续交付工具
- **多工具集成**：与各种云原生工具集成

## 快速开始

### 环境要求
- Docker 20.10+
- Kubernetes 1.20+
- Helm 3.8+
- Jenkins 2.346+

### 1. Docker Pipeline示例

#### 基础Docker Pipeline
```groovy
// docker-pipeline/Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.example.com'
        IMAGE_NAME = 'myapp'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/user/myapp.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    sh 'trivy image --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG}'
                }
            }
        }
        
        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry('https://${DOCKER_REGISTRY}', 'docker-credentials') {
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()
                    }
                }
            }
        }
    }
}
```

#### 多阶段构建Pipeline
```groovy
// multi-stage-build/Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build and Test') {
            agent {
                docker {
                    image 'maven:3.8-openjdk-11'
                    args '-v /home/jenkins/.m2:/root/.m2'
                }
            }
            steps {
                sh 'mvn clean compile test'
            }
        }
        
        stage('Build Production Image') {
            steps {
                script {
                    def customImage = docker.build("myapp:${env.BUILD_NUMBER}", \
                        "--target production --build-arg BUILD_NUMBER=${env.BUILD_NUMBER} .")
                    
                    customImage.push()
                }
            }
        }
    }
}
```

### 2. Kubernetes Pipeline示例

#### 基础Kubernetes部署
```groovy
// kubernetes-pipeline/Jenkinsfile
pipeline {
    agent any
    
    environment {
        KUBE_CONFIG = credentials('kubeconfig')
        NAMESPACE = 'myapp-production'
    }
    
    stages {
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // 应用Kubernetes配置
                    sh "kubectl apply -f k8s/deployment.yaml --namespace=${NAMESPACE}"
                    
                    // 等待部署完成
                    sh "kubectl rollout status deployment/myapp --namespace=${NAMESPACE}"
                    
                    // 运行健康检查
                    sh "kubectl exec deployment/myapp -- curl -f http://localhost:8080/health"
                }
            }
        }
        
        stage('Smoke Test') {
            steps {
                script {
                    // 获取服务地址
                    def serviceIp = sh(script: \
                        "kubectl get service myapp --namespace=${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'", \
                        returnStdout: true).trim()
                    
                    // 运行冒烟测试
                    sh "curl -f http://${serviceIp}:8080/api/health"
                }
            }
        }
    }
}
```

#### Helm部署Pipeline
```groovy
// helm-deployment/Jenkinsfile
pipeline {
    agent any
    
    environment {
        HELM_REPO = 'https://charts.example.com'
        CHART_NAME = 'myapp'
        NAMESPACE = 'myapp-production'
    }
    
    stages {
        stage('Package Helm Chart') {
            steps {
                script {
                    sh 'helm package charts/myapp'
                    sh 'helm repo index . --url ${HELM_REPO}'
                }
            }
        }
        
        stage('Deploy with Helm') {
            steps {
                script {
                    // 添加Helm仓库
                    sh 'helm repo add myrepo ${HELM_REPO}'
                    
                    // 部署应用
                    sh "helm upgrade --install myapp myrepo/${CHART_NAME} \
                        --namespace ${NAMESPACE} \
                        --set image.tag=${env.BUILD_NUMBER} \
                        --wait --timeout 300s"
                }
            }
        }
    }
}
```

### 3. Jenkins X配置示例

#### Jenkins X流水线
```yaml
# jenkins-x/jenkins-x.yml
buildPack: none
pipelineConfig:
  pipelines:
    pullRequest:
      pipeline:
        agent:
          image: golang
        stages:
        - name: pr-checks
          steps:
          - name: unit-tests
            command: make test
            args:
            - -v
          - name: build
            command: make build
    release:
      pipeline:
        agent:
          image: golang
        stages:
        - name: release
          steps:
          - name: build-release
            command: make release
          - name: promote
            command: jx step changelog
```

### 4. Tekton Pipeline示例

#### Tekton任务定义
```yaml
# cloud-native-ci-cd/tekton-pipelines/build-task.yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: build-app
spec:
  params:
  - name: app-name
    type: string
  - name: git-url
    type: string
  - name: git-revision
    type: string
    default: main
  steps:
  - name: clone
    image: alpine/git
    script: |
      git clone $(params.git-url) /workspace/source
      cd /workspace/source
      git checkout $(params.git-revision)
  - name: build
    image: maven:3.8-openjdk-11
    script: |
      cd /workspace/source
      mvn clean compile -DskipTests
  - name: test
    image: maven:3.8-openjdk-11
    script: |
      cd /workspace/source
      mvn test
```

## 高级特性

### 金丝雀部署
```groovy
// canary-deployment/Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Canary Deployment') {
            steps {
                script {
                    // 部署金丝雀版本（10%流量）
                    sh "kubectl apply -f k8s/canary-deployment.yaml"
                    
                    // 等待金丝雀稳定
                    sleep time: 300, unit: 'SECONDS'
                    
                    // 检查金丝雀指标
                    def metrics = getCanaryMetrics()
                    
                    if (metrics.errorRate < 0.01) {
                        // 金丝雀成功，进行全量部署
                        sh "kubectl apply -f k8s/full-deployment.yaml"
                    } else {
                        // 金丝雀失败，回滚
                        sh "kubectl rollout undo deployment/myapp"
                        error "Canary deployment failed"
                    }
                }
            }
        }
    }
}
```

### 服务网格集成
```groovy
// service-mesh/Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Deploy with Service Mesh') {
            steps {
                script {
                    // 部署应用
                    sh 'kubectl apply -f k8s/deployment.yaml'
                    
                    // 配置服务网格路由
                    sh 'kubectl apply -f k8s/virtual-service.yaml'
                    sh 'kubectl apply -f k8s/destination-rule.yaml'
                    
                    // 配置流量策略
                    sh 'kubectl apply -f k8s/traffic-policy.yaml'
                }
            }
        }
        
        stage('Traffic Management') {
            steps {
                script {
                    // 逐步迁移流量
                    migrateTraffic()
                    
                    // 监控服务指标
                    monitorServiceMetrics()
                }
            }
        }
    }
}
```

## 最佳实践

### 安全性
- 使用非root用户运行容器
- 扫描镜像漏洞
- 配置安全上下文
- 使用只读文件系统

### 可靠性
- 实现健康检查
- 配置资源限制
- 设置就绪和存活探针
- 实现优雅关闭

### 性能
- 使用多阶段构建
- 优化镜像大小
- 缓存构建依赖
- 并行执行任务

### 可观测性
- 集成监控工具
- 收集日志和指标
- 配置告警规则
- 实现追踪功能

## 故障排除

### 常见问题

1. **镜像构建失败**
   - 检查Dockerfile语法
   - 验证基础镜像可用性
   - 检查网络连接

2. **Kubernetes部署失败**
   - 检查资源配置
   - 验证权限设置
   - 查看Pod日志

3. **服务连接问题**
   - 检查网络策略
   - 验证服务发现
   - 测试端口连通性

### 调试命令

```bash
# 查看Pod状态
kubectl get pods --all-namespaces

# 查看Pod日志
kubectl logs <pod-name> -n <namespace>

# 检查服务端点
kubectl get endpoints <service-name>

# 检查网络策略
kubectl get networkpolicies
```

这些容器化集成示例展示了Jenkins如何与现代化容器技术无缝集成，帮助您构建云原生的CI/CD流水线。