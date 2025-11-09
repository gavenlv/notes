# 第2章：Jenkins安装和配置

## 📖 章节概述

本章将详细介绍Jenkins的各种安装方式、系统配置、插件管理以及最佳实践。我们将从基础安装开始，逐步深入到生产环境的最佳配置。

## 2.1 环境准备和系统要求

### 2.1.1 硬件要求

**最低配置（测试/学习环境）：**
- CPU：2核心
- 内存：4GB
- 磁盘：10GB可用空间
- 网络：稳定互联网连接

**推荐配置（生产环境）：**
- CPU：4核心以上
- 内存：8GB以上
- 磁盘：50GB以上可用空间（SSD推荐）
- 网络：高速稳定连接

### 2.1.2 软件要求

#### Java版本要求
```
Jenkins 2.346+：需要Java 11或17
Jenkins 2.164+：支持Java 8、11
Jenkins 2.357+：推荐使用Java 11 LTS
```

**检查Java版本：**
```bash
# 检查Java版本
java -version

# 输出示例：
# openjdk version "11.0.15" 2022-04-19
# OpenJDK Runtime Environment (build 11.0.15+10)
# OpenJDK 64-Bit Server VM (build 11.0.15+10, mixed mode)
```

#### 操作系统支持
- **Linux**：Ubuntu、CentOS、RHEL、Debian等
- **Windows**：Windows Server 2016+、Windows 10+
- **macOS**：macOS 10.14+
- **容器**：Docker、Kubernetes

### 2.1.3 网络和防火墙配置

**默认端口：**
- Jenkins Web界面：8080
- Jenkins Agent通信：50000
- 可自定义端口

**防火墙配置示例：**
```bash
# Ubuntu/Debian
sudo ufw allow 8080
sudo ufw allow 50000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=50000/tcp
sudo firewall-cmd --reload
```

## 2.2 Jenkins安装方式详解

### 2.2.1 方式一：使用系统包管理器安装

#### Ubuntu/Debian系统
```bash
# 1. 添加Jenkins仓库密钥
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -

# 2. 添加Jenkins软件源
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

# 3. 更新软件包列表
sudo apt-get update

# 4. 安装Jenkins
sudo apt-get install jenkins

# 5. 启动Jenkins服务
sudo systemctl start jenkins
sudo systemctl enable jenkins

# 6. 检查服务状态
sudo systemctl status jenkins
```

#### CentOS/RHEL系统
```bash
# 1. 添加Jenkins仓库
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key

# 2. 安装Jenkins
sudo yum install jenkins

# 3. 启动服务
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

### 2.2.2 方式二：使用Docker安装

#### 使用官方Docker镜像
```bash
# 1. 创建数据卷（持久化存储）
docker volume create jenkins-data

# 2. 运行Jenkins容器
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# 3. 查看初始管理员密码
docker logs jenkins
```

#### 使用Docker Compose（推荐）
```yaml
# docker-compose.yml
version: '3.8'
services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - ./jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    restart: unless-stopped
```

### 2.2.3 方式三：使用Kubernetes安装

#### Jenkins Kubernetes部署文件
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
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        ports:
        - containerPort: 8080
        - containerPort: 50000
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
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
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: jenkins-service
  namespace: jenkins
spec:
  type: NodePort
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080
  - port: 50000
    targetPort: 50000
    nodePort: 30081
  selector:
    app: jenkins
```

## 2.3 初始配置和访问设置

### 2.3.1 首次访问配置

#### 获取初始管理员密码
```bash
# 查看Docker容器日志
docker logs jenkins

# 或者查看文件（Linux安装）
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

#### 自定义安装插件
**推荐插件组合：**

```
核心插件（必选）：
- Pipeline: 流水线支持
- Git: Git集成
- GitHub: GitHub集成
- Docker: Docker集成
- SSH: SSH连接

构建工具插件：
- Maven Integration: Maven构建
- Gradle: Gradle构建

测试和报告插件：
- JUnit: 单元测试报告
- HTML Publisher: HTML报告

部署插件：
- Deploy to container: 容器部署
- Kubernetes: K8s集成

通知插件：
- Mailer: 邮件通知
- Slack Notification: Slack通知
```

### 2.3.2 创建管理员用户

**最佳实践：**
- 使用强密码策略
- 启用双因素认证（如果支持）
- 定期更换密码
- 避免使用默认管理员账户

## 2.4 Jenkins系统配置详解

### 2.4.1 全局安全配置

#### 认证和授权
```
认证方式：
- 内置用户数据库
- LDAP集成
- Active Directory
- GitHub OAuth
- SAML单点登录

授权策略：
- 基于矩阵的授权
- 基于项目的授权
- 角色策略授权
```

#### 安全加固配置
```
推荐配置：
- 启用CSRF保护
- 配置代理头部
- 限制脚本执行权限
- 启用内容安全策略
```

### 2.4.2 全局工具配置

#### JDK配置
```
配置多个JDK版本：
- Java 8（兼容旧项目）
- Java 11（推荐版本）
- Java 17（最新版本）
```

#### Maven配置
```bash
# 自动安装Maven
Maven名称: Maven 3.8.6
安装版本: 3.8.6
自动安装: 是

# 或者使用系统Maven
Maven名称: System Maven
MAVEN_HOME: /usr/share/maven
```

#### Git配置
```
Git可执行文件路径：
- 默认：git（系统PATH）
- 自定义路径：/usr/bin/git
```

### 2.4.3 系统设置

#### 系统信息配置
```
Jenkins URL: https://jenkins.yourcompany.com
系统管理员邮箱: admin@yourcompany.com
```

#### 执行器数量配置
```
主节点执行器数量：
- 开发环境：2-4个
- 生产环境：根据CPU核心数调整
- 建议：保留1-2个执行器给系统任务
```

## 2.5 插件管理最佳实践

### 2.5.1 插件安装和更新

#### 手动安装插件
```
步骤：
1. 访问 Jenkins → 系统管理 → 插件管理
2. 选择"可用插件"标签页
3. 搜索需要的插件
4. 勾选并安装
5. 重启Jenkins（如果需要）
```

#### 使用CLI安装插件
```bash
# 通过Jenkins CLI安装插件
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin \
  pipeline \
  git \
  docker-workflow

# 重启Jenkins
java -jar jenkins-cli.jar -s http://localhost:8080/ safe-restart
```

### 2.5.2 插件依赖管理

#### 检查插件依赖
```
安装插件时，Jenkins会自动处理依赖
但需要注意版本兼容性
定期检查插件更新
```

#### 插件版本冲突解决
```
常见问题：
- 插件A依赖库X版本1.0
- 插件B依赖库X版本2.0

解决方案：
- 使用兼容版本
- 联系插件维护者
- 考虑替代插件
```

### 2.5.3 插件安全扫描

#### 安全最佳实践
```
1. 定期更新插件到最新版本
2. 订阅Jenkins安全公告
3. 使用受信任的插件源
4. 定期扫描插件漏洞
```

## 2.6 备份和恢复策略

### 2.6.1 备份策略

#### 手动备份
```bash
# 备份JENKINS_HOME目录
sudo tar -czf jenkins-backup-$(date +%Y%m%d).tar.gz /var/lib/jenkins/

# 或者使用rsync
sudo rsync -av /var/lib/jenkins/ /backup/jenkins/
```

#### 使用插件自动备份
**ThinBackup插件配置：**
```
备份目录: /backup/jenkins
备份频率: 每天凌晨2点
保留策略: 保留最近30天备份
备份内容: 配置文件、任务、插件
```

### 2.6.2 恢复策略

#### 完整恢复
```bash
# 停止Jenkins服务
sudo systemctl stop jenkins

# 恢复备份
tar -xzf jenkins-backup-20231108.tar.gz -C /

# 启动Jenkins
sudo systemctl start jenkins
```

#### 部分恢复
```
选择性恢复：
- 只恢复任务配置
- 保留现有插件
- 合并用户数据
```

## 2.7 生产环境配置最佳实践

### 2.7.1 高可用配置

#### 主从架构
```
生产环境推荐使用主从架构：
- 1个主节点（管理配置）
- 多个从节点（执行构建）
- 负载均衡配置
- 故障转移机制
```

#### 数据库后端
```
使用外部数据库：
- MySQL
- PostgreSQL
- 提高性能和稳定性
- 便于备份和恢复
```

### 2.7.2 性能优化配置

#### JVM参数优化
```bash
# 修改JENKINS_HOME/jenkins.xml
<arguments>
  -Xmx4g -Xms2g 
  -XX:MaxMetaspaceSize=512m
  -Djava.awt.headless=true
  -Djenkins.install.runSetupWizard=false
</arguments>
```

#### 构建优化
```
配置建议：
- 合理设置执行器数量
- 启用构建缓存
- 使用增量构建
- 优化依赖下载
```

## 2.8 故障排除和监控

### 2.8.1 常见问题解决

#### Jenkins无法启动
```bash
# 检查服务状态
sudo systemctl status jenkins

# 查看日志
sudo journalctl -u jenkins -f

# 或者直接查看日志文件
sudo tail -f /var/log/jenkins/jenkins.log
```

#### 插件安装失败
```
解决方案：
1. 检查网络连接
2. 验证插件版本兼容性
3. 手动下载插件安装
4. 清理插件缓存
```

### 2.8.2 监控配置

#### 基础监控
```
监控指标：
- 系统负载
- 内存使用率
- 磁盘空间
- 构建队列长度
- 构建成功率
```

#### 使用Prometheus监控
```yaml
# prometheus-jenkins.yml
scrape_configs:
  - job_name: 'jenkins'
    static_configs:
      - targets: ['jenkins:8080']
    metrics_path: '/prometheus'
```

## 2.9 本章小结

### 关键知识点回顾
1. **环境准备**：硬件、软件、网络要求
2. **安装方式**：系统包、Docker、Kubernetes
3. **初始配置**：插件选择、用户创建
4. **系统配置**：安全、工具、全局设置
5. **插件管理**：安装、更新、安全
6. **备份恢复**：策略和实施
7. **生产配置**：高可用、性能优化
8. **故障排除**：常见问题解决

### 实践建议
- 根据实际环境选择合适的安装方式
- 制定定期的备份和更新计划
- 配置监控告警系统
- 记录配置变更日志

### 下一章预告
第3章将深入讲解Jenkins Pipeline，包括声明式流水线、脚本式流水线的语法和最佳实践，以及如何设计复杂的CI/CD流程。

---

**动手实践：**
1. 在你的环境中安装Jenkins
2. 配置基本的全局设置
3. 安装必要的插件
4. 创建一个简单的测试任务

在下一章中，我们将开始学习Jenkins最强大的功能——Pipeline as Code。