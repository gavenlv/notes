# 简单Pipeline示例

## 📋 示例概述

本示例演示最基本的Jenkins Pipeline，帮助理解Pipeline的核心概念和基本结构。

## 🎯 学习目标

- 理解Pipeline的基本语法
- 掌握声明式Pipeline的结构
- 学习如何运行和调试Pipeline
- 了解Pipeline的执行流程

## 📁 文件结构

```
simple-pipeline/
├── README.md                 # 本文档
├── Jenkinsfile              # Pipeline定义
├── scripts/
│   ├── build.sh            # 构建脚本
│   └── test.sh             # 测试脚本
├── src/
│   └── hello-world.java    # 示例源代码
└── configuration/
    └── maven-settings.xml  # Maven配置
```

## 🚀 快速开始

### 前提条件
- Jenkins 2.346+ 已安装
- Java 11+ 环境
- Git 客户端

### 运行步骤

1. **创建Pipeline任务**
   ```
   Jenkins首页 → 新建任务 → 输入任务名称 → 选择Pipeline → 确定
   ```

2. **配置Pipeline**
   - 定义：Pipeline script from SCM
   - SCM：Git
   - Repository URL：本示例的Git仓库地址
   - 脚本路径：Jenkinsfile

3. **立即构建**
   - 点击"立即构建"按钮
   - 观察构建控制台输出

## 📝 Jenkinsfile详解

### 完整Pipeline代码

```groovy
// Jenkinsfile
pipeline {
    // 指定运行环境
    agent any
    
    // 环境变量配置
    environment {
        APP_NAME = 'hello-world'
        VERSION = '1.0.0'
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
    }
    
    // 阶段定义
    stages {
        // 准备阶段
        stage('Preparation') {
            steps {
                echo '=== 准备阶段开始 ==='
                echo "应用名称: ${APP_NAME}"
                echo "版本号: ${VERSION}"
                echo "构建编号: ${BUILD_NUMBER}"
                
                // 检查环境
                sh 'java -version'
                sh 'mvn --version'
                echo '=== 准备阶段完成 ==='
            }
        }
        
        // 检出代码阶段
        stage('Checkout') {
            steps {
                echo '=== 检出代码阶段开始 ==='
                
                // 检出源代码
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [[$class: 'LocalBranch']],
                    userRemoteConfigs: [[url: 'https://github.com/your-org/hello-world.git']]
                ])
                
                // 显示检出结果
                sh 'ls -la'
                echo '=== 检出代码阶段完成 ==='
            }
        }
        
        // 构建阶段
        stage('Build') {
            steps {
                echo '=== 构建阶段开始 ==='
                
                // 使用Maven构建
                sh 'mvn clean compile'
                
                // 检查构建结果
                sh 'ls -la target/'
                echo '=== 构建阶段完成 ==='
            }
        }
        
        // 测试阶段
        stage('Test') {
            steps {
                echo '=== 测试阶段开始 ==='
                
                // 运行单元测试
                sh 'mvn test'
                
                // 生成测试报告
                junit 'target/surefire-reports/*.xml'
                
                echo '=== 测试阶段完成 ==='
            }
            
            // 测试阶段后处理
            post {
                always {
                    echo '测试阶段执行完成'
                    // 可以在这里添加测试报告发布等操作
                }
                success {
                    echo '所有测试通过！'
                }
                failure {
                    echo '有测试失败！'
                }
            }
        }
        
        // 打包阶段
        stage('Package') {
            steps {
                echo '=== 打包阶段开始 ==='
                
                // 打包应用
                sh 'mvn package -DskipTests'
                
                // 存档构建产物
                archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
                
                echo '=== 打包阶段完成 ==='
            }
        }
    }
    
    // 整个Pipeline的后处理
    post {
        // 总是执行
        always {
            echo '=== Pipeline执行完成 ==='
            echo "构建状态: ${currentBuild.result ?: 'SUCCESS'}"
            echo "构建URL: ${env.BUILD_URL}"
            
            // 清理工作空间
            cleanWs()
        }
        
        // 构建成功时执行
        success {
            echo '🎉 Pipeline执行成功！'
            
            // 发送成功通知（示例）
            // mail to: 'team@company.com',
            //      subject: "构建成功: ${APP_NAME} ${VERSION}",
            //      body: "构建 ${BUILD_NUMBER} 成功完成。"
        }
        
        // 构建失败时执行
        failure {
            echo '❌ Pipeline执行失败！'
            
            // 发送失败通知（示例）
            // mail to: 'devops@company.com',
            //      subject: "构建失败: ${APP_NAME} ${VERSION}",
            //      body: "构建 ${BUILD_NUMBER} 失败。请检查日志: ${env.BUILD_URL}"
        }
        
        // 构建不稳定时执行
        unstable {
            echo '⚠️ Pipeline执行不稳定'
        }
        
        // 构建被中止时执行
        aborted {
            echo '⏹️ Pipeline执行被中止'
        }
    }
}
```

## 🔧 配置说明

### agent指令
```groovy
agent any  // 在任何可用节点上运行
```

其他选项：
- `agent { label 'linux' }` - 在特定标签的节点上运行
- `agent { docker 'maven:3.8.6' }` - 在Docker容器中运行

### environment指令
```groovy
environment {
    // 定义环境变量
    APP_NAME = 'hello-world'
    VERSION = '1.0.0'
    
    // 使用Jenkins内置变量
    BUILD_NUMBER = "${env.BUILD_NUMBER}"
}
```

### stages和stage指令
```groovy
stages {
    stage('阶段名称') {
        steps {
            // 执行步骤
        }
    }
}
```

### post指令
```groovy
post {
    always {
        // 总是执行
    }
    success {
        // 成功时执行
    }
    failure {
        // 失败时执行
    }
}
```

## 🛠️ 辅助脚本

### build.sh - 构建脚本
```bash
#!/bin/bash

# 简单构建脚本
echo "开始构建..."

# 检查环境
java -version
mvn --version

# 执行构建
mvn clean compile

echo "构建完成"
```

### test.sh - 测试脚本
```bash
#!/bin/bash

# 简单测试脚本
echo "开始测试..."

# 运行测试
mvn test

# 检查测试结果
if [ $? -eq 0 ]; then
    echo "测试通过"
else
    echo "测试失败"
    exit 1
fi
```

## 📊 执行流程

### 可视化流程
```
开始
  ↓
Preparation (环境准备)
  ↓
Checkout (代码检出)
  ↓
Build (编译构建)
  ↓
Test (运行测试)
  ↓
Package (打包制品)
  ↓
Post Processing (后处理)
  ↓
结束
```

### 控制台输出示例
```
Started by user admin
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/simple-pipeline
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Preparation)
[Pipeline] echo
=== 准备阶段开始 ===
[Pipeline] echo
应用名称: hello-world
[Pipeline] echo
版本号: 1.0.0
[Pipeline] echo
构建编号: 1
[Pipeline] sh
+ java -version
openjdk version "11.0.15" 2022-04-19
[Pipeline] sh
+ mvn --version
Apache Maven 3.8.6
[Pipeline] echo
=== 准备阶段完成 ===
[Pipeline] }
...
```

## 🔍 调试技巧

### 1. 使用echo调试
```groovy
echo "当前变量值: ${variable}"
```

### 2. 使用script块
```groovy
script {
    def result = sh(script: 'ls -la', returnStdout: true)
    echo "命令输出: ${result}"
}
```

### 3. 查看构建日志
- 在Jenkins界面查看控制台输出
- 使用`tail -f`命令实时查看日志

## 🚨 常见问题

### Q: Pipeline执行失败怎么办？
A: 检查控制台输出，通常会有详细的错误信息。常见问题包括：
- 环境变量未定义
- 命令执行权限不足
- 依赖项缺失

### Q: 如何优化Pipeline性能？
A: 
- 使用并行执行
- 缓存依赖项
- 优化构建步骤

### Q: 如何实现条件执行？
A: 使用`when`指令：
```groovy
stage('Deploy') {
    when {
        branch 'main'
    }
    steps {
        // 仅当main分支时执行
    }
}
```

## 📈 扩展学习

完成本示例后，可以继续学习：
1. **参数化Pipeline** - 添加用户输入参数
2. **并行执行** - 提高构建效率
3. **共享库** - 代码复用和标准化

## 📞 技术支持

如果遇到问题，请：
1. 查看Jenkins官方文档
2. 检查控制台错误日志
3. 在GitHub Issues中反馈问题

---

**下一步：**尝试修改这个Pipeline，添加新的阶段或功能，体验Pipeline的强大之处！