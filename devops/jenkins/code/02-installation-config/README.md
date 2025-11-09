# Jenkins安装和配置示例

本目录包含Jenkins各种安装方式和配置管理的最佳实践示例。

## 项目结构

```
02-installation-config/
├── docker-installation/          # Docker安装配置
│   ├── docker-compose.yml       # Docker编排文件
│   ├── Dockerfile               # 自定义Jenkins镜像
│   ├── jenkins-home/            # Jenkins数据目录配置
│   ├── plugins.txt              # 必需插件列表
│   └── README.md
├── kubernetes-install/          # Kubernetes安装
│   ├── jenkins-deployment.yaml  # Jenkins部署配置
│   ├── jenkins-service.yaml     # 服务配置
│   ├── jenkins-pvc.yaml         # 持久化存储
│   ├── jenkins-rbac.yaml        # 权限配置
│   └── README.md
├── backup-recovery/             # 备份恢复策略
│   ├── backup-script.sh         # 备份脚本
│   ├── restore-script.sh       # 恢复脚本
│   ├── jenkins-backup-pipeline.groovy
│   └── README.md
├── production-setup/            # 生产环境配置
│   ├── security-config.groovy   # 安全配置
│   ├── performance-tuning.groovy # 性能调优
│   ├── monitoring-setup.groovy  # 监控配置
│   └── README.md
└── README.md                    # 本文档
```

## 功能特性

### 1. 多种安装方式
- **Docker安装**：容器化部署，快速启动
- **Kubernetes安装**：云原生部署，弹性伸缩
- **传统安装**：二进制包安装，稳定可靠

### 2. 配置管理
- **插件管理**：自动安装必需插件
- **安全配置**：安全加固和认证配置
- **性能优化**：系统调优和资源管理

### 3. 运维工具
- **备份恢复**：数据保护和灾难恢复
- **监控告警**：性能监控和故障告警
- **升级迁移**：版本升级和数据迁移

## 快速开始

### 环境要求
- Docker 20.10+
- Kubernetes 1.20+
- 至少4GB内存
- 20GB磁盘空间

### 1. Docker安装

#### 使用Docker Compose
```bash
cd docker-installation

docker-compose up -d
```

#### 自定义Docker镜像
```dockerfile
# Dockerfile
FROM jenkins/jenkins:lts-jdk11

# 安装必需工具
USER root
RUN apt-get update && apt-get install -y \
    docker.io \
    kubectl \
    maven \
    && rm -rf /var/lib/apt/lists/*

# 切换到jenkins用户
USER jenkins

# 安装插件
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

# 复制配置
COPY jenkins-home/ /var/jenkins_home/
```

### 2. Kubernetes安装

#### 部署配置
```yaml
# jenkins-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      serviceAccountName: jenkins
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts-jdk11
        ports:
        - containerPort: 8080
        - containerPort: 50000
        env:
        - name: JAVA_OPTS
          value: "-Djenkins.install.runSetupWizard=false"
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
        - name: jenkins-plugins
          mountPath: /usr/share/jenkins/ref/plugins/
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: jenkins-home
        persistentVolumeClaim:
          claimName: jenkins-pvc
      - name: jenkins-plugins
        configMap:
          name: jenkins-plugins
```

### 3. 备份恢复

#### 备份脚本
```bash
#!/bin/bash
# backup-script.sh

JENKINS_HOME="/var/jenkins_home"
BACKUP_DIR="/backup/jenkins"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR/$DATE

# 备份Jenkins配置
tar -czf $BACKUP_DIR/$DATE/jenkins-config.tar.gz \
    --exclude="workspace/*" \
    --exclude="jobs/*/workspace/*" \
    $JENKINS_HOME

# 备份插件列表
jenkins-plugin-cli --list > $BACKUP_DIR/$DATE/plugins.txt

# 保留最近7天的备份
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +

echo "Jenkins备份完成: $BACKUP_DIR/$DATE"
```

## 高级配置

### 安全配置
```groovy
// security-config.groovy
import jenkins.model.*
import jenkins.security.s2m.AdminWhitelistRule
import hudson.security.*
import jenkins.security.QueueItemAuthenticatorConfiguration

// 启用安全
def instance = Jenkins.getInstance()

def strategy = new hudson.security.FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

// 配置认证
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount("admin", "secure-password")
instance.setSecurityRealm(realm)

// 启用CSRF保护
instance.setCrumbIssuer(new hudson.security.csrf.DefaultCrumbIssuer(true))

// 配置节点到主控安全
instance.getInjector().getInstance(AdminWhitelistRule.class).setMasterKillSwitch(false)

instance.save()
```

### 性能调优
```groovy
// performance-tuning.groovy
import jenkins.model.*

// 获取Jenkins实例
def instance = Jenkins.getInstance()

// 优化执行器数量
instance.setNumExecutors(4)

// 配置系统属性
System.setProperty("hudson.model.LoadStatistics.clock", "1000")
System.setProperty("jenkins.model.Jenkins.parallelLoad", "true")

// 优化内存设置
System.setProperty("jenkins.model.Jenkins.workspaceDir", "${JENKINS_HOME}/workspace/${ITEM_FULL_NAME}")

// 配置GC参数
System.setProperty("java.awt.headless", "true")
System.setProperty("jenkins.slaves.NioChannelSelector", "false")

instance.save()
```

## 生产环境配置

### 监控配置
```groovy
// monitoring-setup.groovy
import jenkins.model.*
import jenkins.metrics.impl.*
import jenkins.metrics.api.*

// 启用指标收集
def metrics = Metrics.metricRegistry()

// 配置健康检查
HealthCheckRegistry.instance.register(
    new jenkins.metrics.impl.HealthCheckImpl(
        "jenkins-health",
        "Jenkins Master Health",
        { -> 
            def jenkins = Jenkins.getInstance()
            if (jenkins.isQuietingDown()) {
                return Result.unhealthy("Jenkins is quieting down")
            }
            return Result.healthy()
        }
    )
)

// 配置性能监控
Metrics.metricRegistry().register("jenkins.builds.completed", 
    new jenkins.metrics.impl.CounterImpl("completed-builds"))

println "监控配置完成"
```

## 故障排除

### 常见问题

1. **插件安装失败**
   - 检查网络连接
   - 验证插件版本兼容性
   - 查看Jenkins日志

2. **性能问题**
   - 检查内存使用情况
   - 优化执行器配置
   - 清理工作空间

3. **备份恢复失败**
   - 验证备份文件完整性
   - 检查权限配置
   - 查看恢复日志

### 调试命令
```bash
# 查看Jenkins日志
docker logs jenkins-container

# 检查插件状态
curl -s http://localhost:8080/pluginManager/api/json | jq '.plugins[] | select(.enabled==true) | .shortName'

# 性能监控
java -jar jenkins-cli.jar -s http://localhost:8080/ build-monitor
```

## 最佳实践

### 安全性
- 定期更新Jenkins和插件
- 使用强密码和双因素认证
- 配置网络访问控制

### 可靠性
- 设置定期备份
- 配置监控告警
- 建立灾难恢复计划

### 性能
- 优化资源分配
- 使用缓存策略
- 定期清理无用数据

这个安装配置示例提供了从基础安装到生产环境配置的完整指导，帮助您搭建稳定可靠的Jenkins环境。