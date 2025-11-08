# 第7章：Skaffold与CI/CD集成详解

## 7.1 CI/CD基础概念

### 7.1.1 什么是CI/CD
持续集成（Continuous Integration）和持续部署（Continuous Deployment）是现代软件开发的核心实践。

**CI/CD的核心价值：**
- **自动化**：减少人工操作，提高效率
- **一致性**：确保开发、测试、生产环境一致
- **快速反馈**：快速发现和修复问题
- **可靠发布**：降低发布风险

### 7.1.2 Skaffold在CI/CD中的角色
Skaffold作为容器化应用的开发工具，在CI/CD流水线中扮演关键角色：

```yaml
# Skaffold在CI/CD中的定位
开发环境   ->  构建环境   ->  测试环境   ->  生产环境
    ↓           ↓           ↓           ↓
 Skaffold   Skaffold    Skaffold    部署工具
 本地开发   CI构建     集成测试    生产部署
```

## 7.2 Skaffold与GitHub Actions集成

### 7.2.1 GitHub Actions基础配置

**基础CI流水线配置：**
```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Install Skaffold
      run: |
        curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
        sudo install skaffold /usr/local/bin/
        skaffold version
    
    - name: Run Skaffold build
      run: skaffold build --file-output=build.json
    
    - name: Run tests
      run: skaffold test --build-artifacts=build.json
```

### 7.2.2 多环境部署策略

**完整的多环境CI/CD流水线：**
```yaml
# .github/workflows/cd.yml
name: CD Pipeline
on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy-to-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy to staging
      run: |
        skaffold run --profile=staging \
          --default-repo=$REGISTRY/$IMAGE_NAME \
          --tag=${{ github.sha }}
      env:
        KUBECONFIG: ${{ secrets.STAGING_KUBECONFIG }}

  deploy-to-production:
    runs-on: ubuntu-latest
    needs: deploy-to-staging
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        skaffold run --profile=production \
          --default-repo=$REGISTRY/$IMAGE_NAME \
          --tag=${{ github.ref_name }}
      env:
        KUBECONFIG: ${{ secrets.PRODUCTION_KUBECONFIG }}
```

## 7.3 Skaffold与GitLab CI/CD集成

### 7.3.1 GitLab CI基础配置

**GitLab CI流水线配置：**
```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy-staging
  - deploy-production

variables:
  SKAFFOLD_DEFAULT_REPO: $CI_REGISTRY_IMAGE

.build-template: &build-template
  stage: build
  image: docker:24.0
  services:
    - docker:24.0-dind
  before_script:
    - apk add --no-cache curl
    - curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
    - chmod +x skaffold
    - mv skaffold /usr/local/bin/
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - skaffold build --file-output=build-artifacts.json

build:
  <<: *build-template
  only:
    - merge_requests
    - main
    - develop

test:
  stage: test
  image: docker:24.0
  services:
    - docker:24.0-dind
  script:
    - skaffold test --build-artifacts=build-artifacts.json
  dependencies:
    - build
  only:
    - merge_requests
    - main
```

### 7.3.2 高级GitLab CI特性

**条件部署和手动审批：**
```yaml
deploy-staging:
  stage: deploy-staging
  image: docker:24.0
  services:
    - docker:24.0-dind
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - echo "$STAGING_KUBECONFIG" | base64 -d > kubeconfig
    - export KUBECONFIG=kubeconfig
    - skaffold run --profile=staging --tag=$CI_COMMIT_SHA
  only:
    - main
  when: manual
  allow_failure: false

deploy-production:
  stage: deploy-production
  image: docker:24.0
  services:
    - docker:24.0-dind
  environment:
    name: production
    url: https://example.com
  script:
    - echo "$PRODUCTION_KUBECONFIG" | base64 -d > kubeconfig
    - export KUBECONFIG=kubeconfig
    - skaffold run --profile=production --tag=$CI_COMMIT_TAG
  only:
    - tags
  when: manual
```

## 7.4 Skaffold与Jenkins集成

### 7.4.1 Jenkins Pipeline配置

**声明式Pipeline配置：**
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        SKAFFOLD_VERSION = '2.7.0'
        DOCKER_REGISTRY = 'registry.example.com'
        PROJECT_NAME = 'my-app'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                # 安装Skaffold
                curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/v${SKAFFOLD_VERSION}/skaffold-linux-amd64
                chmod +x skaffold
                sudo mv skaffold /usr/local/bin/
                
                # 验证安装
                skaffold version
                '''
            }
        }
        
        stage('Build') {
            steps {
                sh '''
                # 构建镜像
                skaffold build \
                  --default-repo=${DOCKER_REGISTRY}/${PROJECT_NAME} \
                  --file-output=build-artifacts.json
                '''
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                # 运行测试
                skaffold test --build-artifacts=build-artifacts.json
                '''
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                # 部署到预发布环境
                skaffold run --profile=staging \
                  --default-repo=${DOCKER_REGISTRY}/${PROJECT_NAME} \
                  --tag=${GIT_COMMIT}
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                tag pattern: 'v.*', comparator: 'REGEXP'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh '''
                # 部署到生产环境
                skaffold run --profile=production \
                  --default-repo=${DOCKER_REGISTRY}/${PROJECT_NAME} \
                  --tag=${TAG_NAME}
                '''
            }
        }
    }
    
    post {
        always {
            // 清理资源
            sh 'skaffold delete'
        }
        success {
            // 成功通知
            echo 'Pipeline executed successfully'
        }
        failure {
            // 失败通知
            echo 'Pipeline failed'
        }
    }
}
```

### 7.4.2 Jenkins共享库

**可重用的Skaffold流水线库：**
```groovy
// vars/skaffoldPipeline.groovy
def call(Map config = [:]) {
    def defaults = [
        skaffoldVersion: '2.7.0',
        registry: 'registry.example.com',
        projectName: env.JOB_BASE_NAME,
        profiles: ['dev', 'staging', 'production']
    ]
    config = defaults + config
    
    pipeline {
        agent any
        
        stages {
            stage('Setup Skaffold') {
                steps {
                    setupSkaffold(config.skaffoldVersion)
                }
            }
            
            stage('Build Images') {
                steps {
                    buildImages(config)
                }
            }
            
            stage('Run Tests') {
                steps {
                    runTests(config)
                }
            }
            
            stage('Deploy') {
                steps {
                    script {
                        if (env.BRANCH_NAME == 'main') {
                            deployToStaging(config)
                        }
                        if (env.TAG_NAME) {
                            deployToProduction(config)
                        }
                    }
                }
            }
        }
    }
}

def setupSkaffold(version) {
    sh """
    curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/v${version}/skaffold-linux-amd64
    chmod +x skaffold
    sudo mv skaffold /usr/local/bin/
    skaffold version
    """
}
```

## 7.5 高级CI/CD模式

### 7.5.1 蓝绿部署策略

**基于Skaffold的蓝绿部署：**
```yaml
# skaffold.yaml
apiVersion: skaffold/v2beta29
kind: Config
profiles:
  - name: blue
    deploy:
      kubectl:
        manifests:
          - k8s/blue-deployment.yaml
          - k8s/service.yaml
    
  - name: green
    deploy:
      kubectl:
        manifests:
          - k8s/green-deployment.yaml
          - k8s/service.yaml

# 蓝绿部署CI脚本
blue-green-deploy:
  stage: deploy
  script:
    - |
      # 确定当前活动版本
      CURRENT_COLOR=$(kubectl get svc my-app -o jsonpath='{.spec.selector.color}')
      
      if [ "$CURRENT_COLOR" = "blue" ]; then
        TARGET_COLOR="green"
      else
        TARGET_COLOR="blue"
      fi
      
      # 部署新版本
      skaffold run --profile=$TARGET_COLOR --tag=$CI_COMMIT_SHA
      
      # 等待新版本就绪
      kubectl rollout status deployment/my-app-$TARGET_COLOR --timeout=300s
      
      # 切换流量
      kubectl patch service my-app -p '{"spec":{"selector":{"color":"'$TARGET_COLOR'"}}}'
      
      # 清理旧版本（可选）
      if [ "$CLEANUP_OLD" = "true" ]; then
        skaffold delete --profile=$CURRENT_COLOR
      fi
```

### 7.5.2 金丝雀部署策略

**基于Skaffold的金丝雀部署：**
```yaml
# skaffold.yaml
apiVersion: skaffold/v2beta29
kind: Config
profiles:
  - name: canary
    deploy:
      kubectl:
        manifests:
          - k8s/canary-deployment.yaml
          - k8s/service.yaml

# 金丝雀部署CI脚本
canary-deploy:
  stage: deploy
  script:
    - |
      # 部署金丝雀版本（10%流量）
      skaffold run --profile=canary --tag=$CI_COMMIT_SHA
      
      # 监控金丝雀版本
      echo "Monitoring canary deployment for 15 minutes..."
      sleep 900
      
      # 检查金丝雀健康状况
      CANARY_STATUS=$(kubectl get deployment my-app-canary -o jsonpath='{.status.readyReplicas}')
      CANARY_ERRORS=$(kubectl logs -l app=my-app,version=canary | grep -c "ERROR")
      
      if [ "$CANARY_STATUS" -eq 1 ] && [ "$CANARY_ERRORS" -lt 10 ]; then
        # 金丝雀健康，扩大流量
        echo "Canary is healthy, scaling to 50%"
        kubectl scale deployment/my-app-canary --replicas=5
        
        # 等待并检查
        sleep 300
        
        # 如果仍然健康，完全替换
        if kubectl rollout status deployment/my-app-canary --timeout=300s; then
          echo "Canary deployment successful, replacing stable version"
          skaffold run --profile=stable --tag=$CI_COMMIT_SHA
          skaffold delete --profile=canary
        fi
      else
        # 金丝雀不健康，回滚
        echo "Canary deployment failed, rolling back"
        skaffold delete --profile=canary
        exit 1
      fi
```

## 7.6 安全最佳实践

### 7.6.1 密钥管理

**安全的密钥处理：**
```yaml
# 使用外部密钥管理
apiVersion: skaffold/v2beta29
kind: Config
build:
  artifacts:
    - image: my-app
      docker:
        dockerfile: Dockerfile
        secret:
          id: docker-config
          dst: /kaniko/.docker/config.json

deploy:
  kubectl:
    manifests:
      - k8s/**.yaml
    # 使用Kubernetes Secrets
    flags:
      global:
        - --namespace=my-app

# CI/CD中的密钥管理
secure-deploy:
  stage: deploy
  before_script:
    - |
      # 从Vault获取密钥
      export DOCKER_PASSWORD=$(vault read -field=password secret/docker)
      echo "$DOCKER_PASSWORD" | docker login -u $DOCKER_USERNAME --password-stdin
      
      # 配置Kubernetes访问
      echo "$KUBECONFIG" | base64 -d > kubeconfig
      export KUBECONFIG=kubeconfig
  script:
    - skaffold run --default-repo=$REGISTRY
```

### 7.6.2 安全扫描集成

**集成安全扫描的CI流水线：**
```yaml
security-scan:
  stage: security
  script:
    - |
      # 构建镜像
      skaffold build --file-output=build.json
      
      # 安全扫描
      for image in $(cat build.json | jq -r '.builds[].imageName'); do
        echo "Scanning $image"
        
        # Trivy漏洞扫描
        trivy image --exit-code 1 --severity HIGH,CRITICAL $image
        
        # Grype漏洞扫描
        grype $image --fail-on high
        
        # 镜像签名验证
        cosign verify $image --key cosign.pub
      done
  allow_failure: false
```

## 7.7 监控和日志

### 7.7.1 部署监控

**部署状态监控和通知：**
```yaml
deploy-monitor:
  stage: monitor
  script:
    - |
      # 部署应用
      skaffold run
      
      # 监控部署状态
      TIMEOUT=600
      INTERVAL=10
      ELAPSED=0
      
      while [ $ELAPSED -lt $TIMEOUT ]; do
        if kubectl rollout status deployment/my-app --timeout=60s; then
          echo "Deployment successful"
          
          # 发送成功通知
          curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"Deployment successful: $CI_PIPELINE_URL"}' \
            $SLACK_WEBHOOK_URL
          break
        fi
        
        ELAPSED=$((ELAPSED + INTERVAL))
        sleep $INTERVAL
      done
      
      if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "Deployment timeout"
        
        # 获取失败日志
        kubectl logs -l app=my-app --tail=50
        
        # 发送失败通知
        curl -X POST -H 'Content-type: application/json' \
          --data '{"text":"Deployment failed: $CI_PIPELINE_URL"}' \
          $SLACK_WEBHOOK_URL
        exit 1
      fi
```

### 7.7.2 性能指标收集

**部署性能指标：**
```yaml
performance-metrics:
  stage: metrics
  script:
    - |
      # 开始时间
      START_TIME=$(date +%s)
      
      # 执行部署
      skaffold run
      
      # 结束时间
      END_TIME=$(date +%s)
      DEPLOYMENT_DURATION=$((END_TIME - START_TIME))
      
      # 收集指标
      POD_START_TIME=$(kubectl get pods -l app=my-app -o jsonpath='{.items[0].status.startTime}')
      READY_TIME=$(date +%s -d "$POD_START_TIME")
      STARTUP_TIME=$((READY_TIME - START_TIME))
      
      # 发送指标到监控系统
      curl -X POST "http://monitoring:9090/api/v1/write" \
        -d "deployment_duration_seconds $DEPLOYMENT_DURATION"
      curl -X POST "http://monitoring:9090/api/v1/write" \
        -d "startup_time_seconds $STARTUP_TIME"
```

## 7.8 故障排除和调试

### 7.8.1 CI/CD常见问题

**调试技巧：**
```yaml
debug-pipeline:
  stage: debug
  script:
    - |
      # 启用详细日志
      export SKAFFOLD_VERBOSITY=debug
      
      # 检查配置
      skaffold config list
      skaffold diagnose
      
      # 测试连接
      kubectl cluster-info
      docker info
      
      # 验证配置文件
      skaffold schema
      skaffold render --output=rendered.yaml
      
      # 分步执行
      skaffold build --dry-run
      skaffold deploy --images=my-app:latest --dry-run
```

本章详细介绍了Skaffold与各种CI/CD工具的集成，包括基础配置、高级部署策略、安全实践和故障排除。这些内容将为实际的企业级部署提供完整指导。