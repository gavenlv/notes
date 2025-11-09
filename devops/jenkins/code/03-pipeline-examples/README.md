# Jenkins Pipeline示例集合

本目录包含各种类型的Jenkins Pipeline示例，从基础的声明式Pipeline到高级的多分支和共享库Pipeline。

## 项目结构

```
03-pipeline-examples/
├── declarative-pipeline/       # 声明式Pipeline
│   ├── Jenkinsfile            # 基础声明式Pipeline
│   ├── parallel-pipeline/      # 并行执行Pipeline
│   ├── conditional-pipeline/    # 条件执行Pipeline
│   └── README.md
├── scripted-pipeline/          # 脚本式Pipeline
│   ├── Jenkinsfile            # 基础脚本式Pipeline
│   ├── advanced-scripting/    # 高级脚本功能
│   ├── error-handling/        # 错误处理机制
│   └── README.md
├── multi-branch-pipeline/     # 多分支Pipeline
│   ├── Jenkinsfile            # 多分支配置
│   ├── branch-strategies/     # 分支策略
│   ├── pr-validation/         # PR验证流程
│   └── README.md
├── shared-library/            # 共享库示例
│   ├── src/                   # 共享库源代码
│   ├── vars/                  # 全局变量定义
│   ├── resources/             # 资源文件
│   └── README.md
├── advanced-pipeline/         # 高级Pipeline特性
│   ├── matrix-pipeline/       # 矩阵构建
│   ├── nested-pipeline/       # 嵌套Pipeline
│   ├── plugin-integration/   # 插件集成
│   └── README.md
└── README.md                 # 本文档
```

## 功能特性

### 1. 声明式Pipeline
- **语法简洁**：易于理解和维护
- **内置验证**：语法检查和验证
- **结构化阶段**：清晰的执行流程
- **错误处理**：内置的错误处理机制

### 2. 脚本式Pipeline
- **灵活性高**：支持复杂的逻辑控制
- **编程能力**：完整的Groovy编程能力
- **动态生成**：运行时动态生成Pipeline
- **高级功能**：支持各种高级功能

### 3. 多分支Pipeline
- **自动发现**：自动发现分支和PR
- **分支策略**：自定义分支构建策略
- **PR验证**：Pull Request自动验证
- **环境隔离**：不同分支的环境隔离

### 4. 共享库
- **代码复用**：公共功能的代码复用
- **标准化**：统一的构建流程标准
- **版本控制**：共享库版本管理
- **测试支持**：共享库单元测试

## 快速开始

### 环境要求
- Jenkins 2.346+
- Pipeline插件
- Git插件
- 基本构建工具（Maven/Gradle）

### 1. 声明式Pipeline示例

#### 基础Pipeline
```groovy
// declarative-pipeline/Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/user/repo.git'
            }
        }
        
        stage('Build') {
            steps {
                sh 'mvn clean compile'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
                junit 'target/surefire-reports/*.xml'
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline执行完成'
        }
    }
}
```

#### 并行执行Pipeline
```groovy
// parallel-pipeline/Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build and Test') {
            parallel {
                stage('Unit Test') {
                    steps {
                        sh 'mvn test'
                    }
                }
                stage('Integration Test') {
                    steps {
                        sh 'mvn integration-test'
                    }
                }
                stage('Code Quality') {
                    steps {
                        sh 'mvn sonar:sonar'
                    }
                }
            }
        }
    }
}
```

### 2. 脚本式Pipeline示例

#### 基础脚本式Pipeline
```groovy
// scripted-pipeline/Jenkinsfile
node {
    stage('Checkout') {
        git 'https://github.com/user/repo.git'
    }
    
    stage('Build') {
        if (env.BRANCH_NAME == 'main') {
            echo 'Building main branch'
            sh 'mvn clean compile'
        } else {
            echo 'Building feature branch'
            sh 'mvn clean compile -DskipTests'
        }
    }
    
    stage('Test') {
        try {
            sh 'mvn test'
            junit 'target/surefire-reports/*.xml'
        } catch (Exception e) {
            echo "Test failed: ${e.message}"
            currentBuild.result = 'UNSTABLE'
        }
    }
}
```

### 3. 多分支Pipeline示例

#### 多分支配置
```groovy
// multi-branch-pipeline/Jenkinsfile
properties([
    pipelineTriggers([
        cron('H */4 * * *')
    ])
])

pipeline {
    agent any
    
    tools {
        maven 'Maven-3.8'
        jdk 'Java-11'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    branch 'release/*'
                }
            }
            steps {
                sh 'mvn clean compile'
            }
        }
        
        stage('Test') {
            when {
                not { branch 'PR-*' }
            }
            steps {
                sh 'mvn test'
            }
        }
    }
}
```

### 4. 共享库示例

#### 共享库结构
```
shared-library/
├── src/
│   └── com/
│       └── company/
│           └── JenkinsPipeline.groovy
├── vars/
│   ├── buildApp.groovy
│   ├── deployApp.groovy
│   └── notifyTeam.groovy
└── resources/
    └── com/company/templates/
        ├── deployment.yaml
        └── service.yaml
```

#### 共享库使用示例
```groovy
// 使用共享库的Pipeline
@Library('my-shared-library@master') _

pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                buildApp()
            }
        }
        
        stage('Deploy') {
            steps {
                deployApp()
            }
        }
        
        stage('Notify') {
            steps {
                notifyTeam()
            }
        }
    }
}
```

## 高级特性

### 矩阵构建
```groovy
// matrix-pipeline/Jenkinsfile
pipeline {
    agent none
    
    stages {
        stage('Test Matrix') {
            matrix {
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'linux', 'windows', 'mac'
                    }
                    axis {
                        name 'BROWSER'
                        values 'chrome', 'firefox', 'safari'
                    }
                }
                stages {
                    stage('Test') {
                        steps {
                            echo "Testing on ${PLATFORM} with ${BROWSER}"
                            sh './run-tests.sh'
                        }
                    }
                }
            }
        }
    }
}
```

### 嵌套Pipeline
```groovy
// nested-pipeline/Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build App') {
            steps {
                build(job: 'app-build-job', wait: true)
            }
        }
        
        stage('Build DB') {
            steps {
                build(job: 'db-build-job', wait: true)
            }
        }
        
        stage('Integration Test') {
            steps {
                build(job: 'integration-test-job', wait: true)
            }
        }
    }
}
```

## 最佳实践

### 1. 代码组织
- 将复杂的逻辑封装到共享库中
- 使用有意义的阶段名称
- 保持Pipeline简洁和可读性

### 2. 错误处理
- 使用try-catch处理预期错误
- 配置适当的超时设置
- 实现优雅的失败处理

### 3. 性能优化
- 使用并行执行提高效率
- 缓存依赖项减少构建时间
- 优化构建步骤的顺序

### 4. 安全性
- 使用凭据管理敏感信息
- 限制Pipeline的执行权限
- 定期审查Pipeline代码

## 故障排除

### 常见问题

1. **语法错误**
   - 使用Pipeline语法验证工具
   - 检查Groovy语法正确性
   - 验证插件版本兼容性

2. **权限问题**
   - 检查节点和执行器权限
   - 验证凭据访问权限
   - 确认文件系统权限

3. **性能问题**
   - 分析构建时间线
   - 优化资源使用
   - 检查网络连接

### 调试技巧

```groovy
// 添加调试信息
stage('Debug') {
    steps {
        script {
            echo "Current environment: ${env}"
            echo "Build parameters: ${params}"
            echo "Current node: ${env.NODE_NAME}"
        }
    }
}
```

## 扩展学习

完成这些示例后，您可以进一步学习：
- **Pipeline DSL参考**：深入了解Pipeline语法
- **插件开发**：创建自定义Pipeline步骤
- **性能优化**：优化大规模Pipeline性能
- **安全最佳实践**：确保Pipeline安全性

这些Pipeline示例涵盖了从基础到高级的各种场景，帮助您掌握Jenkins Pipeline的强大功能。