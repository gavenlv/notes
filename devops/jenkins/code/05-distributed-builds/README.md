# Jenkins分布式构建示例

本目录包含完整的Jenkins分布式构建配置和示例，展示了如何搭建和管理分布式构建环境。

## 项目结构

```
distributed-builds/
├── ssh-node-setup/                 # SSH节点配置
│   ├── setup-ssh-node.sh           # SSH节点设置脚本
│   ├── jenkins-ssh-config.groovy   # Jenkins SSH配置
│   └── README.md
├── docker-agent-config/            # Docker代理配置
│   ├── Dockerfile                  # 自定义Docker镜像
│   ├── docker-compose.yml          # Docker环境编排
│   ├── jenkins-docker-config.groovy
│   └── README.md
├── kubernetes-pod-templates/       # Kubernetes Pod模板
│   ├── maven-pod.yaml              # Maven构建Pod
│   ├── nodejs-pod.yaml             # Node.js构建Pod
│   ├── jenkins-kubernetes-config.groovy
│   └── README.md
├── load-testing/                   # 负载测试
│   ├── performance-test-pipeline.groovy
│   ├── load-generator.sh
│   └── README.md
├── scheduling-strategies/          # 调度策略
│   ├── load-based-scheduler.groovy
│   ├── priority-scheduler.groovy
│   └── README.md
└── monitoring/                     # 监控配置
    ├── node-monitoring-pipeline.groovy
    ├── prometheus-metrics.groovy
    └── README.md
```

## 功能特性

### 1. 多种节点类型支持
- **SSH节点**：远程Linux服务器
- **Docker节点**：容器化构建环境
- **Kubernetes节点**：云原生构建集群
- **云实例**：AWS、Azure、GCP云节点

### 2. 智能调度策略
- 负载均衡调度
- 优先级调度
- 标签匹配调度
- 动态资源分配

### 3. 性能监控
- 节点健康监控
- 构建性能指标
- 资源使用统计
- 告警和通知

## 快速开始

### 环境要求
- Jenkins 2.303.1+
- Docker 20.10+
- Kubernetes 1.20+
- 至少2个构建节点

### 1. SSH节点配置

#### 设置SSH节点
```bash
cd ssh-node-setup
./setup-ssh-node.sh
```

#### Jenkins配置
```groovy
// 通过Groovy脚本添加SSH节点
import jenkins.model.*
import hudson.plugins.sshslaves.*

// 创建SSH连接
def sshLauncher = new SSHLauncher(
    'build-server.example.com',
    22,
    'jenkins',
    '',
    '/var/jenkins_home/.ssh/id_rsa',
    '',
    '',
    '',
    60, 3, 30
)

// 创建节点
def sshNode = new DumbSlave(
    'ssh-build-node',
    '/home/jenkins/workspace',
    sshLauncher
)

sshNode.setNumExecutors(4)
sshNode.setLabelString('linux docker maven')
Jenkins.instance.addNode(sshNode)
```

### 2. Docker节点配置

#### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'
services:
  jenkins-docker-agent:
    build: .
    privileged: true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /shared/maven-cache:/root/.m2
    environment:
      - JENKINS_URL=http://jenkins.example.com:8080
      - JENKINS_SECRET=your-agent-secret
    networks:
      - jenkins

networks:
  jenkins:
    driver: bridge
```

#### Jenkins Docker配置
```groovy
// Docker云配置
import com.cloudbees.jenkins.plugins.docker_build_env.Docker
import org.csanchez.jenkins.plugins.kubernetes.*
import org.csanchez.jenkins.plugins.kubernetes.model.*
import org.csanchez.jenkins.plugins.kubernetes.volumes.*

// 添加Docker云配置
def dockerCloud = new DockerCloud(
    'docker-cloud',
    [
        new DockerTemplate(
            new DockerTemplateImage('maven:3.8.1-openjdk-11'),
            'maven-docker-agent',
            '/home/jenkins/agent',
            'docker maven',
            new DockerContainerLifecycle(),
            new RetentionStrategy.Always()
        )
    ],
    'unix:///var/run/docker.sock',
    10
)

Jenkins.instance.clouds.add(dockerCloud)
```

### 3. Kubernetes节点配置

#### Pod模板配置
```yaml
# maven-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: jenkins-maven-agent
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:alpine
    env:
    - name: JAVA_OPTS
      value: -Xmx512m -Xms256m
    resources:
      requests:
        memory: "512Mi"
        cpu: "500m"
      limits:
        memory: "1Gi"
        cpu: "1000m"
  - name: maven
    image: maven:3.8.1-openjdk-11
    command: ['cat']
    tty: true
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
    volumeMounts:
    - name: maven-cache
      mountPath: /root/.m2
  volumes:
  - name: maven-cache
    persistentVolumeClaim:
      claimName: maven-cache-pvc
```

#### Jenkins Kubernetes配置
```groovy
// Kubernetes云配置
import org.csanchez.jenkins.plugins.kubernetes.*
import org.csanchez.jenkins.plugins.kubernetes.model.*

// 创建Kubernetes云
def kubernetesCloud = new KubernetesCloud('kubernetes')
kubernetesCloud.serverUrl = 'https://kubernetes.default.svc'
kubernetesCloud.namespace = 'jenkins'
kubernetesCloud.jenkinsUrl = 'http://jenkins.example.com:8080'

// 添加Pod模板
def podTemplate = new PodTemplate()
podTemplate.name = 'maven-pod'
podTemplate.label = 'kubernetes maven'
podTemplate.containers = [
    new ContainerTemplate(
        'maven',
        'maven:3.8.1-openjdk-11',
        'cat',
        '/home/jenkins/agent'
    )
]

kubernetesCloud.templates = [podTemplate]
Jenkins.instance.clouds.add(kubernetesCloud)
```

## 高级调度策略

### 负载均衡调度
```groovy
// 负载感知调度器
@NonCPS
def scheduleWithLoadBalance(String jobName, Map requirements) {
    def jenkins = Jenkins.instance
    
    // 获取合适的节点
    def suitableNodes = jenkins.nodes.findAll { node ->
        def computer = node.toComputer()
        computer?.online && computer.acceptingTasks &&
        node.labelString.contains(requirements.labels)
    }
    
    // 选择负载最低的节点
    def selectedNode = suitableNodes.min { node ->
        def computer = node.toComputer()
        
        // 计算负载分数
        def loadScore = computer.countBusy() / node.numExecutors
        
        // 考虑内存使用率
        def memoryMonitor = computer.getMonitor(hudson.node_monitors.SwapSpaceMonitor.class)
        if (memoryMonitor) {
            def memoryUsage = 1 - (memoryMonitor.availablePhysicalMemory / memoryMonitor.totalPhysicalMemory)
            loadScore += memoryUsage
        }
        
        return loadScore
    }
    
    return selectedNode.displayName
}
```

### 优先级调度
```groovy
// 优先级调度系统
class PriorityScheduler {
    
    @NonCPS
    static String schedule(String jobName, int priority) {
        def nodeLabel = getNodeLabelByPriority(priority)
        
        def jenkins = Jenkins.instance
        def suitableNodes = jenkins.nodes.findAll { node ->
            node.toComputer()?.online && node.labelString.contains(nodeLabel)
        }
        
        if (suitableNodes.isEmpty()) {
            // 降级处理
            return schedule(jobName, priority - 1)
        }
        
        return suitableNodes.min { it.toComputer().countBusy() }.displayName
    }
    
    @NonCPS
    static String getNodeLabelByPriority(int priority) {
        switch(priority) {
            case 1: return 'high-performance'
            case 2: return 'production'
            case 3: return 'staging'
            case 4: return 'development'
            default: return 'built-in'
        }
    }
}
```

## 性能监控

### 节点健康监控
```groovy
// 节点监控Pipeline
pipeline {
    agent any
    
    stages {
        stage('Node Health Check') {
            steps {
                script {
                    def healthReport = monitorNodeHealth()
                    
                    if (healthReport.unhealthyNodes > 0) {
                        echo "发现 ${healthReport.unhealthyNodes} 个不健康节点"
                        
                        // 发送告警
                        slackSend(
                            channel: '#jenkins-alerts',
                            message: "节点健康告警: ${healthReport.unhealthyNodes} 个节点异常"
                        )
                    }
                }
            }
        }
    }
}

@NonCPS
def monitorNodeHealth() {
    def jenkins = Jenkins.instance
    def report = [
        totalNodes: jenkins.nodes.size(),
        onlineNodes: 0,
        unhealthyNodes: 0,
        nodes: []
    ]
    
    jenkins.nodes.each { node ->
        def computer = node.toComputer()
        def nodeInfo = [
            name: node.displayName,
            online: computer?.online ?: false,
            healthIndicators: []
        ]
        
        if (computer?.online) {
            report.onlineNodes++
            
            // 检查响应时间
            def responseTimeMonitor = computer.getMonitor(hudson.node_monitors.ResponseTimeMonitor.class)
            if (responseTimeMonitor?.getResponseTime(node) > 5000) {
                nodeInfo.healthIndicators.add('响应时间慢')
                report.unhealthyNodes++
            }
            
            // 检查内存使用
            def memoryMonitor = computer.getMonitor(hudson.node_monitors.SwapSpaceMonitor.class)
            if (memoryMonitor && (1 - memoryMonitor.availablePhysicalMemory / memoryMonitor.totalPhysicalMemory) > 0.9) {
                nodeInfo.healthIndicators.add('内存使用率高')
                report.unhealthyNodes++
            }
        }
        
        report.nodes.add(nodeInfo)
    }
    
    return report
}
```

### Prometheus指标导出
```groovy
// Prometheus指标导出
@NonCPS
def exportPrometheusMetrics() {
    def jenkins = Jenkins.instance
    def metrics = []
    
    jenkins.nodes.each { node ->
        def computer = node.toComputer()
        
        metrics.add("jenkins_node_online{node=\"${node.displayName}\"} ${computer?.online ? 1 : 0}")
        metrics.add("jenkins_node_busy_executors{node=\"${node.displayName}\"} ${computer?.countBusy() ?: 0}")
        metrics.add("jenkins_node_total_executors{node=\"${node.displayName}\"} ${node.numExecutors}")
    }
    
    // 发送到Prometheus pushgateway
    def metricsData = metrics.join('\n')
    sh """
        echo '${metricsData}' | \\
        curl -X POST --data-binary @- \\
        http://prometheus:9091/metrics/job/jenkins_nodes
    """
}
```

## 负载测试

### 并行构建测试
```groovy
// 并行构建负载测试
pipeline {
    agent none
    
    parameters {
        choice(name: 'PARALLEL_JOBS', choices: ['5', '10', '20'], description: '并行作业数')
    }
    
    stages {
        stage('Load Test') {
            steps {
                script {
                    def parallelJobs = [:] 
                    
                    (1..params.PARALLEL_JOBS.toInteger()).each { jobNumber ->
                        parallelJobs["Job-${jobNumber}"] = {
                            node {
                                stage("Build ${jobNumber}") {
                                    // 模拟构建工作负载
                                    sh '''
                                        echo "开始构建作业 ${jobNumber}"
                                        sleep 30  # 模拟30秒构建时间
                                        echo "构建作业 ${jobNumber} 完成"
                                    '''
                                }
                            }
                        }
                    }
                    
                    parallel parallelJobs
                }
            }
        }
        
        stage('Performance Analysis') {
            steps {
                script {
                    // 分析性能指标
                    def performanceReport = analyzePerformance()
                    
                    echo "总构建时间: ${performanceReport.totalTime}s"
                    echo "平均构建时间: ${performanceReport.avgTime}s"
                    echo "最大并行度: ${performanceReport.maxParallel}"
                }
            }
        }
    }
}
```

## 最佳实践

### 节点管理
1. **定期维护**：清理离线节点和临时文件
2. **监控告警**：设置节点健康监控
3. **容量规划**：根据构建需求调整节点数量

### 调度优化
1. **标签策略**：合理使用节点标签
2. **负载均衡**：避免节点过载
3. **优先级管理**：重要作业优先执行

### 性能调优
1. **缓存优化**：共享依赖缓存
2. **资源限制**：合理设置资源限制
3. **网络优化**：优化节点间网络通信

## 故障排除

### 常见问题
1. **节点连接失败**：检查网络和认证配置
2. **资源不足**：调整节点资源或添加更多节点
3. **调度性能差**：优化调度策略和节点配置

### 调试工具
```bash
# 查看节点状态
java -jar jenkins-cli.jar -s http://jenkins.example.com:8080/ list-nodes

# 检查节点日志
tail -f /var/jenkins_home/logs/jenkins.log | grep -i node
```

## 扩展开发

### 自定义调度器
实现自定义调度器来满足特定需求：
1. 扩展`hudson.model.QueueScheduler`
2. 实现调度算法
3. 配置调度策略

### 集成监控系统
集成Prometheus、Grafana等监控工具：
1. 导出构建指标
2. 设置监控仪表板
3. 配置告警规则

这个分布式构建示例提供了完整的配置和最佳实践，可以帮助您搭建高性能的Jenkins分布式构建环境。