# 第3章：Jenkins Pipeline详解

## 📖 章节概述

本章将深入讲解Jenkins Pipeline，这是Jenkins 2.x最重要的特性。我们将从基础语法开始，逐步深入到高级用法和最佳实践。

## 3.1 Pipeline基础概念

### 3.1.1 什么是Pipeline as Code？

**Pipeline as Code** 是一种将CI/CD流程定义为代码的方法，具有以下优势：

- ✅ **版本控制**：Pipeline配置可以像代码一样进行版本管理
- ✅ **代码审查**：可以进行代码审查，提高质量
- ✅ **可重复性**：确保环境一致性
- ✅ **可测试性**：Pipeline本身可以测试

### 3.1.2 Pipeline核心概念

#### 节点 (Node)
```groovy
node {
    // 在任意可用节点上执行
    echo 'Hello World'
}

node('linux') {
    // 在特定标签的节点上执行
    sh 'uname -a'
}
```

#### 阶段 (Stage)
```groovy
stage('Build') {
    echo 'Building the application'
}

stage('Test') {
    echo 'Running tests'
}
```

#### 步骤 (Step)
```groovy
steps {
    sh 'mvn clean compile'  // Shell命令
    echo 'Build completed'   // 输出消息
    junit '**/target/*.xml' // 测试报告
}
```

## 3.2 声明式Pipeline详解

### 3.2.1 基本声明式Pipeline结构

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

### 3.2.2 agent指令详解

#### 在不同环境中运行
```groovy
pipeline {
    // 在任何可用节点上运行
    agent any
    
    // 或者指定特定标签
    agent {
        label 'linux && docker'
    }
    
    // 使用Docker容器
    agent {
        docker {
            image 'maven:3.8.6-openjdk-11'
            args '-v /tmp:/tmp'
        }
    }
    
    // 使用Kubernetes Pod
    agent {
        kubernetes {
            label 'maven-pod'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.8.6-openjdk-11
    command: ['cat']
    tty: true
'''
        }
    }
}
```

### 3.2.3 stages和stage指令

#### 复杂阶段结构
```groovy
pipeline {
    agent any
    
    stages {
        stage('Preparation') {
            steps {
                echo 'Preparing environment...'
            }
            post {
                always {
                    echo 'Preparation stage completed'
                }
            }
        }
        
        stage('Build and Test') {
            parallel {
                stage('Unit Test') {
                    steps {
                        echo 'Running unit tests...'
                    }
                }
                stage('Integration Test') {
                    steps {
                        echo 'Running integration tests...'
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                expression { 
                    return currentBuild.result == null || currentBuild.result == 'SUCCESS' 
                }
            }
            steps {
                echo 'Running quality checks...'
            }
        }
    }
}
```

### 3.2.4 environment指令

#### 环境变量管理
```groovy
pipeline {
    agent any
    
    environment {
        // 基本环境变量
        APP_NAME = 'my-application'
        VERSION = '1.0.0'
        
        // 从Jenkins凭据获取
        DOCKER_REGISTRY = credentials('docker-registry')
        
        // 条件环境变量
        BUILD_ENV = "${params.ENVIRONMENT ?: 'development'}"
    }
    
    stages {
        stage('Build') {
            environment {
                // 阶段级环境变量
                MAVEN_OPTS = '-Xmx2g'
            }
            steps {
                echo "Building ${APP_NAME} version ${VERSION}"
                echo "Environment: ${BUILD_ENV}"
            }
        }
    }
}
```

### 3.2.5 options指令

#### Pipeline配置选项
```groovy
pipeline {
    agent any
    
    options {
        // 构建超时设置
        timeout(time: 1, unit: 'HOURS')
        
        // 保留构建历史
        buildDiscarder(logRotator(numToKeepStr: '10'))
        
        // 禁止并发构建
        disableConcurrentBuilds()
        
        // 重试次数
        retry(3)
        
        // 跳过默认的checkout
        skipDefaultCheckout()
        
        // 时间戳
        timestamps()
        
        // 静默期
        quietPeriod(30)
    }
    
    stages {
        stage('Example') {
            steps {
                echo 'Hello World'
            }
        }
    }
}
```

### 3.2.6 parameters指令

#### 参数化Pipeline
```groovy
pipeline {
    agent any
    
    parameters {
        // 字符串参数
        string(name: 'BRANCH', defaultValue: 'main', description: 'Git branch to build')
        
        // 选择参数
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Deployment environment')
        
        // 布尔参数
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run tests?')
        
        // 文本参数
        text(name: 'DEPLOYMENT_NOTES', defaultValue: '', description: 'Deployment notes')
        
        // 文件参数
        file(name: 'CONFIG_FILE', description: 'Configuration file')
        
        // 密码参数
        password(name: 'API_KEY', description: 'API key for deployment')
    }
    
    stages {
        stage('Build') {
            steps {
                echo "Building branch: ${params.BRANCH}"
                echo "Environment: ${params.ENVIRONMENT}"
                script {
                    if (params.RUN_TESTS) {
                        echo 'Running tests...'
                    }
                }
            }
        }
    }
}
```

### 3.2.7 triggers指令

#### 构建触发器
```groovy
pipeline {
    agent any
    
    triggers {
        // 定时构建
        cron('H */4 * * 1-5')  // 工作日每4小时
        
        // 轮询SCM
        pollSCM('H/15 * * * *')  // 每15分钟检查一次
        
        // 上游项目触发
        upstream(upstreamProjects: 'project-a', threshold: hudson.model.Result.SUCCESS)
    }
    
    stages {
        stage('Example') {
            steps {
                echo 'Triggered build'
            }
        }
    }
}
```

### 3.2.8 tools指令

#### 工具配置
```groovy
pipeline {
    agent any
    
    tools {
        // JDK配置
        jdk 'jdk11'
        
        // Maven配置
        maven 'maven-3.8.6'
        
        // Node.js配置
        nodejs 'nodejs-16'
        
        // Gradle配置
        gradle 'gradle-7'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn --version'
                sh 'java -version'
            }
        }
    }
}
```

### 3.2.9 when指令

#### 条件执行
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            when {
                // 分支条件
                branch 'main'
                
                // 或者多分支条件
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
                
                // 表达式条件
                expression {
                    return params.DEPLOY_TO_PROD == true
                }
                
                // 环境条件
                environment name: 'DEPLOY_ENV', value: 'production'
                
                // 变更集条件
                changeset "**/*.java"
                
                // 构建标签条件
                buildingTag()
            }
            steps {
                echo 'Conditional build step'
            }
        }
        
        stage('Deploy to Staging') {
            when {
                // 非生产环境才执行
                not {
                    branch 'main'
                }
            }
            steps {
                echo 'Deploying to staging'
            }
        }
        
        stage('Deploy to Production') {
            when {
                // 需要人工审批
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                echo 'Deploying to production'
            }
        }
    }
}
```

## 3.3 脚本式Pipeline详解

### 3.3.1 基本脚本式Pipeline

```groovy
node {
    // 定义变量
    def appName = 'my-app'
    def version = '1.0.0'
    
    try {
        stage('Checkout') {
            echo 'Checking out source code...'
            checkout scm
        }
        
        stage('Build') {
            echo 'Building application...'
            sh "mvn clean compile -Dapp.name=${appName} -Dapp.version=${version}"
        }
        
        stage('Test') {
            echo 'Running tests...'
            sh 'mvn test'
            junit 'target/surefire-reports/*.xml'
        }
        
        stage('Deploy') {
            echo 'Deploying application...'
            if (env.BRANCH_NAME == 'main') {
                echo 'Deploying to production'
                // 生产部署逻辑
            } else {
                echo 'Deploying to staging'
                // 测试环境部署逻辑
            }
        }
        
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        echo "Build failed: ${e.message}"
        throw e
    } finally {
        echo 'Pipeline execution completed'
    }
}
```

### 3.3.2 高级脚本特性

#### 并行执行
```groovy
node {
    stage('Build') {
        // 串行构建
        echo 'Building sequentially...'
    }
    
    stage('Test') {
        // 并行测试
        parallel(
            "Unit Tests": {
                node {
                    stage('Unit Tests') {
                        echo 'Running unit tests...'
                        sh 'mvn test -Dtest=*UnitTest'
                    }
                }
            },
            "Integration Tests": {
                node {
                    stage('Integration Tests') {
                        echo 'Running integration tests...'
                        sh 'mvn test -Dtest=*IntegrationTest'
                    }
                }
            }
        )
    }
}
```

#### 共享库使用
```groovy
// 加载共享库
@Library('my-shared-library')_

node {
    stage('Build') {
        // 使用共享库函数
        buildMavenProject()
    }
    
    stage('Test') {
        runUnitTests()
        runIntegrationTests()
    }
    
    stage('Deploy') {
        deployToStaging()
    }
}
```

## 3.4 多分支Pipeline

### 3.4.1 多分支Pipeline配置

```groovy
// Jenkinsfile (在代码仓库根目录)
pipeline {
    agent any
    
    tools {
        maven 'maven-3.8.6'
        jdk 'jdk11'
    }
    
    environment {
        APP_NAME = 'my-application'
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                script {
                    // 根据分支执行不同构建
                    if (env.BRANCH_NAME == 'main') {
                        echo 'Building main branch for production'
                        sh 'mvn clean compile -Pproduction'
                    } else if (env.BRANCH_NAME == 'develop') {
                        echo 'Building develop branch'
                        sh 'mvn clean compile -Pdevelopment'
                    } else if (env.BRANCH_NAME.startsWith('feature/')) {
                        echo 'Building feature branch'
                        sh 'mvn clean compile -Pfeature'
                    }
                }
            }
        }
        
        stage('Test') {
            when {
                // 仅在有代码变更时运行测试
                changeset "src/**/*.java"
            }
            steps {
                sh 'mvn test'
                junit 'target/surefire-reports/*.xml'
            }
        }
        
        stage('Deploy') {
            when {
                // 根据分支决定部署环境
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        input message: 'Deploy to production?', ok: 'Deploy'
                        echo 'Deploying to production...'
                    } else if (env.BRANCH_NAME == 'develop') {
                        echo 'Deploying to staging...'
                    }
                }
            }
        }
    }
    
    post {
        always {
            // 清理工作空间
            cleanWs()
            
            // 发送构建通知
            emailext (
                subject: "Build ${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.result}. Check console output at ${env.BUILD_URL}",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        
        success {
            echo 'Pipeline succeeded!'
        }
        
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

### 3.4.2 分支策略配置

#### 分支发现策略
```groovy
// 在Jenkins多分支Pipeline配置中
properties([
    pipelineTriggers([
        // GitHub webhook触发
        [$class: 'GitHubPushTrigger'],
        
        // 定期扫描
        [$class: 'SCMTrigger', scmpoll_spec: 'H/5 * * * *']
    ]),
    
    // 分支过滤策略
    branchDiscovery([
        // 只处理特定分支
        [$class: 'ExcludeBranchesByRegex', regex: '.*test.*'],
        [$class: 'IncludeBranchesByRegex', regex: '(main|develop|feature/.*)']
    ]),
    
    // 构建策略
    buildStrategies([
        // 跳过初次构建
        [$class: 'SkipInitialBuildOnFirstBranchIndexing'],
        
        // 仅构建有变更的分支
        [$class: 'ChangeRequestBuildStrategy']
    ])
])
```

## 3.5 Pipeline共享库

### 3.5.1 共享库结构

```
shared-library/
├── src/
│   └── com/
│       └── company/
│           └── jenkins/
│               ├── BuildTools.groovy
│               ├── DeployTools.groovy
│               └── TestTools.groovy
├── vars/
│   ├── buildMavenProject.groovy
│   ├── deployToEnvironment.groovy
│   └── runTests.groovy
└── resources/
    └── com/company/jenkins/
        ├── deployment-templates/
        └── configuration-files/
```

### 3.5.2 共享库示例

#### vars/buildMavenProject.groovy
```groovy
def call(Map config = [:]) {
    def defaults = [
        goals: 'clean compile',
        profile: 'default',
        skipTests: false
    ]
    
    config = defaults + config
    
    echo "Building Maven project with goals: ${config.goals}"
    
    def mavenCommand = "mvn ${config.goals}"
    
    if (config.profile != 'default') {
        mavenCommand += " -P${config.profile}"
    }
    
    if (config.skipTests) {
        mavenCommand += ' -DskipTests'
    }
    
    sh mavenCommand
}
```

#### vars/deployToEnvironment.groovy
```groovy
def call(String environment) {
    switch(environment.toLowerCase()) {
        case 'development':
            deployToDev()
            break
        case 'staging':
            deployToStaging()
            break
        case 'production':
            deployToProduction()
            break
        default:
            error "Unknown environment: ${environment}"
    }
}

private void deployToDev() {
    echo 'Deploying to development environment'
    // 开发环境部署逻辑
}

private void deployToStaging() {
    echo 'Deploying to staging environment'
    // 测试环境部署逻辑
}

private void deployToProduction() {
    echo 'Deploying to production environment'
    // 生产环境部署逻辑
}
```

### 3.5.3 在Pipeline中使用共享库

```groovy
@Library('my-shared-library')_

pipeline {
    agent any
    
    parameters {
        choice(name: 'DEPLOY_ENV', choices: ['development', 'staging', 'production'], description: 'Deployment environment')
    }
    
    stages {
        stage('Build') {
            steps {
                buildMavenProject(
                    goals: 'clean compile package',
                    profile: 'ci',
                    skipTests: false
                )
            }
        }
        
        stage('Test') {
            steps {
                runTests()
            }
        }
        
        stage('Deploy') {
            steps {
                deployToEnvironment(params.DEPLOY_ENV)
            }
        }
    }
}
```

## 3.6 Pipeline最佳实践

### 3.6.1 代码组织和结构

#### 模块化Pipeline
```groovy
// 将复杂Pipeline分解为多个文件

// Jenkinsfile (主文件)
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    load('build.groovy')()
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    load('test.groovy')()
                }
            }
        }
    }
}

// build.groovy
return {
    echo 'Building application...'
    sh 'mvn clean compile'
}

// test.groovy
return {
    echo 'Running tests...'
    sh 'mvn test'
}
```

### 3.6.2 错误处理和重试

#### 健壮的错误处理
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                retry(3) {
                    echo 'Attempting build...'
                    sh 'mvn clean compile'
                }
                
                timeout(time: 10, unit: 'MINUTES') {
                    echo 'Running build with timeout...'
                    sh 'mvn test'
                }
            }
            
            post {
                success {
                    echo 'Build stage succeeded'
                }
                
                failure {
                    echo 'Build stage failed'
                    // 发送警报
                    emailext (
                        subject: "Build Failed: ${env.JOB_NAME}",
                        body: "Build stage failed. Check console output at ${env.BUILD_URL}",
                        to: 'devops@company.com'
                    )
                }
                
                unstable {
                    echo 'Build stage unstable'
                }
                
                aborted {
                    echo 'Build stage aborted'
                }
            }
        }
    }
}
```

### 3.6.3 性能优化

#### 并行执行优化
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            parallel {
                stage('Backend Build') {
                    agent {
                        label 'maven'
                    }
                    steps {
                        sh 'mvn clean compile -pl backend'
                    }
                }
                
                stage('Frontend Build') {
                    agent {
                        label 'nodejs'
                    }
                    steps {
                        sh 'npm install && npm run build'
                    }
                }
                
                stage('Database Migration') {
                    agent {
                        label 'database'
                    }
                    steps {
                        sh './scripts/migrate-database.sh'
                    }
                }
            }
        }
    }
}
```

## 3.7 本章小结

### 关键知识点回顾
1. **Pipeline基础**：声明式和脚本式Pipeline的区别
2. **声明式语法**：agent、stages、environment等指令
3. **脚本式特性**：Groovy脚本的强大功能
4. **多分支Pipeline**：自动处理多个分支的构建
5. **共享库**：代码复用和标准化
6. **最佳实践**：错误处理、性能优化、代码组织

### 实践建议
- 从简单的声明式Pipeline开始学习
- 逐步引入复杂条件和并行执行
- 使用共享库提高代码复用性
- 实施错误处理和监控机制

### 下一章预告
第4章将深入讲解Jenkins插件生态系统，包括核心插件的使用、自定义插件开发、以及插件管理和安全最佳实践。

---

**动手实践：**
1. 创建一个简单的声明式Pipeline
2. 添加参数化和条件执行
3. 实现多分支Pipeline
4. 创建和使用共享库

在下一章中，我们将探索Jenkins强大的插件生态系统。