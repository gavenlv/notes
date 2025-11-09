# Jenkins自定义插件开发示例

本目录包含完整的Jenkins自定义插件开发示例，展示了如何从零开始开发一个功能完整的Jenkins插件。

## 项目结构

```
custom-plugin/
├── src/main/java/com/example/jenkins/plugin/
│   ├── CustomBuildStep.java           # 自定义构建步骤
│   ├── CustomPipelineStep.java        # Pipeline步骤
│   ├── CustomNotifier.java            # 构建通知器
│   └── descriptors/                    # 描述符类
├── src/main/resources/
│   ├── com/example/jenkins/plugin/
│   │   ├── CustomBuildStep/
│   │   │   └── config.jelly           # 配置界面
│   │   └── messages.properties        # 国际化资源
│   └── index.jelly                    # 插件主页
├── Jenkinsfile                        # 插件构建流水线
├── pom.xml                            # Maven配置
├── test/                              # 测试代码
└── README.md                          # 本文档
```

## 插件功能特性

### 1. 自定义构建步骤
- 支持外部脚本执行
- 环境变量配置
- 详细的日志输出
- 错误处理和重试机制

### 2. Pipeline步骤支持
- 声明式Pipeline集成
- 脚本式Pipeline支持
- 参数化配置
- 步骤级日志记录

### 3. 构建通知器
- 多种通知方式（邮件、Slack等）
- 自定义通知模板
- 构建状态跟踪
- 失败重试机制

## 快速开始

### 环境要求
- Java 8或11
- Maven 3.6+
- Jenkins 2.303.1+

### 构建插件
```bash
# 克隆项目
cd custom-plugin

# 编译插件
mvn clean compile

# 运行测试
mvn test

# 打包插件
mvn package

# 安装到Jenkins
mvn hpi:run
```

### 在Jenkins中使用

#### 自由风格项目
```groovy
// 在构建步骤中添加自定义构建步骤
customBuildStep {
    scriptPath = 'build-scripts/deploy.sh'
    environment = 'production'
    verbose = true
}
```

#### Pipeline项目
```groovy
pipeline {
    agent any
    
    stages {
        stage('Custom Step') {
            steps {
                customStep {
                    message = '开始自定义构建步骤'
                    level = 'INFO'
                }
            }
        }
    }
}
```

## 开发指南

### 扩展点开发
插件实现了以下扩展点：
- `Builder` - 自定义构建步骤
- `Step` - Pipeline步骤
- `Notifier` - 构建后通知

### 配置界面开发
使用Jelly框架开发配置界面：
- `config.jelly` - 步骤配置表单
- `global.jelly` - 全局配置
- `messages.properties` - 国际化支持

### 测试策略
- 单元测试：测试核心业务逻辑
- 集成测试：验证Jenkins集成
- 功能测试：测试完整功能流程

## 部署和维护

### 插件安装
1. 打包插件：`mvn package`
2. 在Jenkins管理界面安装`.hpi`文件
3. 重启Jenkins实例

### 配置管理
```xml
<!-- 全局配置示例 -->
<com.example.jenkins.plugin.CustomPluginConfiguration>
  <defaultScriptPath>/var/jenkins/scripts</defaultScriptPath>
  <enableNotifications>true</enableNotifications>
  <notificationChannels>
    <string>email</string>
    <string>slack</string>
  </notificationChannels>
</com.example.jenkins.plugin.CustomPluginConfiguration>
```

### 监控和日志
```groovy
// 启用详细日志
customBuildStep {
    scriptPath = 'deploy.sh'
    environment = 'production'
    verbose = true
    logLevel = 'DEBUG'
}
```

## 最佳实践

### 安全性
- 验证输入参数
- 使用安全的文件操作
- 实现适当的权限检查

### 性能
- 避免阻塞操作
- 使用异步处理
- 优化资源使用

### 可维护性
- 清晰的代码结构
- 完整的文档
- 充分的测试覆盖

## 故障排除

### 常见问题
1. **插件加载失败**：检查依赖版本兼容性
2. **配置不生效**：验证配置界面绑定
3. **权限问题**：检查Jenkins安全设置

### 调试技巧
```bash
# 启用调试模式
mvn hpi:run -Djenkins.runlevel=DEBUG

# 查看详细日志
tail -f $JENKINS_HOME/logs/jenkins.log
```

## 扩展开发

### 添加新功能
1. 实现新的扩展点
2. 开发配置界面
3. 编写测试用例
4. 更新文档

### 集成其他插件
```java
// 集成Credentials插件
@Inject
private transient CredentialsProvider credentialsProvider;
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个插件示例。

### 开发流程
1. Fork项目
2. 创建功能分支
3. 实现功能并测试
4. 提交Pull Request

## 许可证

本项目采用MIT许可证，详情参见LICENSE文件。