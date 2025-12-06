# 第6章：RabbitMQ Docker化部署

## 📖 概述

本章节详细介绍了如何将RabbitMQ部署在Docker容器环境中，包括单节点部署、集群部署、监控配置、备份恢复和性能测试等企业级功能。

### 🎯 学习目标

- 掌握RabbitMQ的Docker化部署方法
- 理解Docker Compose在RabbitMQ集群中的应用
- 学会配置RabbitMQ的监控和告警系统
- 掌握数据备份和恢复的最佳实践
- 了解性能优化和故障排查技巧

## 📁 文件结构

```
chapter6/
├── README.md                           # 本文档
├── docker_deployment_examples.py       # Docker部署示例代码
├── docker_config/                      # 配置文件目录
│   ├── rabbitmq.conf                   # RabbitMQ主配置
│   ├── advanced.config                 # 高级配置
│   ├── prometheus.yml                  # Prometheus配置
│   └── grafana_dashboard.json          # Grafana仪表板
├── docker-compose.yml                  # 单节点部署配置
├── docker-compose-cluster.yml          # 集群部署配置
└── docker_backup/                      # 备份文件目录
```

## 🚀 快速开始

### 环境准备

1. **安装Docker和Docker Compose**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose
   
   # CentOS/RHEL
   sudo yum install docker docker-compose
   
   # 启动服务
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **验证安装**
   ```bash
   docker --version
   docker-compose --version
   sudo docker run hello-world
   ```

3. **配置Docker权限**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

### 运行示例

1. **克隆代码到本地**
   ```bash
   # 假设代码已下载到本地
   cd rabbitmq/code/chapter6
   ```

2. **安装依赖**
   ```bash
   pip install docker pyyaml
   ```

3. **运行演示程序**
   ```bash
   python docker_deployment_examples.py
   ```

## 🛠 代码组件详解

### 1. DockerManager类 - Docker管理器

负责Docker容器的创建、管理和监控：

```python
class DockerManager:
    """Docker管理器类"""
    
    def deploy_single_node(self, enable_monitoring: bool = True) -> None:
        """部署单节点RabbitMQ"""
        
    def check_status(self) -> Dict[str, Any]:
        """检查RabbitMQ状态"""
        
    def wait_for_ready(self, timeout: int = 300) -> None:
        """等待RabbitMQ服务就绪"""
```

**主要功能：**
- 自动创建Docker网络和数据卷
- 配置资源限制（CPU、内存）
- 实现健康检查机制
- 启用Prometheus监控插件
- 提供状态检查和监控接口

### 2. ComposeManager类 - Docker Compose管理器

管理Docker Compose编排文件：

```python
class ComposeManager:
    """Docker Compose管理器"""
    
    def generate_basic_compose(self, config: DockerConfig) -> Dict[str, Any]:
        """生成基本的Compose配置"""
        
    def generate_cluster_compose(self, node_count: int = 3) -> Dict[str, Any]:
        """生成集群Compose配置"""
        
    def up(self, detached: bool = True) -> None:
        """启动服务"""
```

**主要功能：**
- 生成单节点和集群配置
- 管理服务依赖关系
- 配置资源限制和重启策略
- 集成监控服务（Prometheus、Grafana）

### 3. ConfigManager类 - 配置管理器

生成各种配置文件：

```python
class ConfigManager:
    """配置管理器"""
    
    def generate_rabbitmq_conf(self, config: DockerConfig) -> None:
        """生成RabbitMQ配置文件"""
        
    def generate_prometheus_config(self) -> None:
        """生成Prometheus配置"""
        
    def generate_grafana_dashboard(self) -> Dict[str, Any]:
        """生成Grafana仪表板配置"""
```

### 4. BackupManager类 - 备份管理器

负责数据备份和恢复：

```python
class BackupManager:
    """备份管理器"""
    
    def create_backup(self) -> str:
        """创建备份"""
        
    def restore_backup(self, backup_path: str) -> None:
        """恢复备份"""
        
    def cleanup_old_backups(self, days: int = 30) -> None:
        """清理旧备份"""
```

### 5. PerformanceTester类 - 性能测试工具

进行性能测试和监控：

```python
class PerformanceTester:
    """性能测试工具"""
    
    def run_perf_test(self, producers: int = 10, consumers: int = 10, 
                     rate: int = 1000, duration: int = 300) -> Dict[str, Any]:
        """运行性能测试"""
        
    def test_resource_usage(self, duration: int = 60) -> Dict[str, Any]:
        """测试资源使用情况"""
```

## 📋 核心功能详解

### 1. 单节点Docker部署

#### 配置文件生成
```bash
# 运行配置生成示例
python -c "
from docker_deployment_examples import ConfigManager, DockerConfig
config_manager = ConfigManager('./docker_config')
config = DockerConfig()
config_manager.generate_rabbitmq_conf(config)
config_manager.generate_advanced_conf()
config_manager.generate_prometheus_config()
config_manager.generate_grafana_dashboard()
"
```

#### 启动单节点
```bash
# 使用Python管理器启动
python -c "
from docker_deployment_examples import DockerManager, DockerConfig
config = DockerConfig(
    image='rabbitmq:3.11-management',
    container_name='rabbitmq-single',
    memory_limit='1g',
    cpu_limit='1.0'
)
manager = DockerManager(config)
manager.deploy_single_node()
"
```

#### Docker Compose方式
```bash
# 启动服务
docker-compose -f docker-compose.yml up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f rabbitmq
```

### 2. 集群部署

#### 生成集群配置
```bash
python -c "
from docker_deployment_examples import ComposeManager
compose_manager = ComposeManager('rabbitmq-cluster')
cluster_config = compose_manager.generate_cluster_compose(3)
compose_manager.save_compose_file(cluster_config, 'docker-compose-cluster.yml')
"
```

#### 启动集群
```bash
# 启动集群
docker-compose -f docker-compose-cluster.yml up -d

# 检查集群状态
docker exec rabbitmq-node1 rabbitmqctl cluster_status
```

#### 节点加入集群
```bash
# 让节点2加入节点1
docker exec rabbitmq-node2 rabbitmqctl join_cluster rabbit@rabbitmq-node1

# 让节点3加入节点1
docker exec rabbitmq-node3 rabbitmqctl join_cluster rabbit@rabbitmq-node1
```

### 3. 监控配置

#### Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq-node1:15692']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

#### Grafana仪表板
```bash
# 启动Grafana
docker-compose -f docker-compose.yml up grafana

# 访问地址
# Grafana: http://localhost:3000 (admin/admin123)
# Prometheus: http://localhost:9090
# RabbitMQ管理: http://localhost:15672 (admin/admin123)
```

### 4. 备份恢复

#### 创建备份
```bash
python -c "
from docker_deployment_examples import BackupManager
backup_manager = BackupManager('rabbitmq-server', './docker_backup')
backup_path = backup_manager.create_backup()
print(f'备份已创建: {backup_path}')
"
```

#### 恢复备份
```bash
python -c "
from docker_deployment_examples import BackupManager
backup_manager = BackupManager('rabbitmq-server', './docker_backup')
backup_path = './docker_backup/rabbitmq_backup_20231201_143022.tar.gz'
backup_manager.restore_backup(backup_path)
"
```

### 5. 性能测试

#### 运行性能测试
```bash
python -c "
from docker_deployment_examples import PerformanceTester
tester = PerformanceTester('rabbitmq-server')
result = tester.run_perf_test(
    producers=10,
    consumers=10,
    rate=1000,
    duration=300
)
print('测试结果:', result)
"
```

#### 资源监控
```bash
python -c "
from docker_deployment_examples import PerformanceTester
tester = PerformanceTester('rabbitmq-server')
usage = tester.test_resource_usage()
print('资源使用情况:', usage)
"
```

## ⚙️ 配置参数详解

### Docker配置参数

```python
@dataclass
class DockerConfig:
    image: str = "rabbitmq:3.11-management"    # RabbitMQ镜像版本
    container_name: str = "rabbitmq-server"    # 容器名称
    amqp_port: int = 5672                      # AMQP端口
    management_port: int = 15672              # 管理界面端口
    username: str = "admin"                   # 默认用户名
    password: str = "admin123"                # 默认密码
    vhost: str = "/"                          # 默认虚拟主机
    memory_limit: str = "1g"                  # 内存限制
    cpu_limit: str = "1.0"                    # CPU限制
    volume_name: str = "rabbitmq_data"        # 数据卷名称
    network_name: str = "rabbitmq_network"    # 网络名称
```

### RabbitMQ配置参数

```
# rabbitmq.conf
default_user = admin
default_pass = admin123
default_vhost = /
default_connection_limit = 1000
heartbeat = 30
vm_memory_high_watermark = 0.6
disk_free_limit = 1GB
tcp_listen_options.backlog = 128
tcp_listen_options.nodelay = true
```

### Docker Compose配置

```yaml
version: '3.8'
services:
  rabbitmq:
    image: rabbitmq:3.11-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin123
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"
        reservations:
          memory: 512M
          cpus: "0.5"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔧 性能优化建议

### 1. 资源优化

```yaml
# 资源限制配置
deploy:
  resources:
    limits:
      memory: 2G
      cpus: "2.0"
    reservations:
      memory: 1G
      cpus: "1.0"
```

### 2. 网络优化

```python
# 创建专用网络
network = docker_client.networks.create(
    "rabbitmq_network",
    driver="bridge",
    ipam=docker.types.IPAMConfig(
        config=[docker.types.IPAMSubnet(subnet="172.20.0.0/16")]
    )
)
```

### 3. 存储优化

```yaml
# 挂载配置
volumes:
  - rabbitmq_data:/var/lib/rabbitmq
  - ./config:/etc/rabbitmq/conf.d
```

### 4. 监控优化

```python
# 启用监控插件
def enable_monitoring(self):
    # 启用Prometheus插件
    self.container.exec_run("rabbitmq-plugins enable rabbitmq_prometheus")
    
    # 启用Management插件
    self.container.exec_run("rabbitmq-plugins enable rabbitmq_management")
```

## 🔍 故障排查指南

### 常见问题排查

1. **容器启动失败**
   ```bash
   # 检查容器日志
   docker logs rabbitmq-server
   
   # 检查端口占用
   sudo netstat -tulpn | grep 5672
   ```

2. **连接失败**
   ```bash
   # 检查防火墙设置
   sudo iptables -L
   
   # 检查容器网络
   docker network ls
   docker network inspect rabbitmq_network
   ```

3. **内存不足**
   ```bash
   # 检查资源使用
   docker stats rabbitmq-server
   
   # 调整内存限制
   docker update --memory=2G rabbitmq-server
   ```

4. **数据持久化问题**
   ```bash
   # 检查数据卷
   docker volume ls
   docker volume inspect rabbitmq_data
   ```

### 日志分析

```bash
# 实时查看日志
docker logs -f rabbitmq-server

# 查看最近100行日志
docker logs --tail 100 rabbitmq-server

# 查看特定时间段的日志
docker logs --since 2023-12-01T10:00:00 rabbitmq-server
```

### 健康检查

```bash
# 手动健康检查
docker exec rabbitmq-server rabbitmq-diagnostics ping

# 检查集群状态
docker exec rabbitmq-node1 rabbitmqctl cluster_status

# 检查队列状态
docker exec rabbitmq-server rabbitmqctl list_queues
```

## 🚢 生产环境部署

### 1. 安全配置

```yaml
# 使用环境变量
environment:
  - RABBITMQ_DEFAULT_USER=${RABBITMQ_USER}
  - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
  - RABBITMQ_DEFAULT_VHOST=${RABBITMQ_VHOST}
```

### 2. SSL配置

```bash
# 生成SSL证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

```conf
# rabbitmq.conf
ssl_options.certfile = /etc/rabbitmq/ssl/cert.pem
ssl_options.keyfile = /etc/rabbitmq/ssl/key.pem
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
```

### 3. 高可用配置

```yaml
# 集群配置
services:
  rabbitmq-node1:
    environment:
      - RABBITMQ_ERLANG_COOKIE=RABBITMQ_SECRET_COOKIE
    command: >
      bash -c "
        rabbitmq-server &
        sleep 30 &&
        rabbitmqctl stop_app &&
        rabbitmqctl join_cluster rabbit@rabbitmq-node2 &&
        rabbitmqctl start_app
      "
```

### 4. 负载均衡

```nginx
# Nginx配置
upstream rabbitmq_backend {
    server rabbitmq-node1:5672;
    server rabbitmq-node2:5672;
    server rabbitmq-node3:5672;
}

server {
    listen 5672;
    location / {
        proxy_pass http://rabbitmq_backend;
    }
}
```

## 🧪 测试场景

### 1. 功能测试

```python
def test_basic_functionality():
    """测试基本功能"""
    import pika
    
    # 连接测试
    credentials = pika.PlainCredentials('admin', 'admin123')
    parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    
    # 发送消息
    channel = connection.channel()
    channel.queue_declare(queue='test_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='test_queue',
        body='Hello Docker World!',
        properties=pika.BasicProperties(
            delivery_mode=2,  # 持久化
        )
    )
    
    # 接收消息
    def callback(ch, method, properties, body):
        print(f"收到消息: {body}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    channel.basic_consume(queue='test_queue', on_message_callback=callback)
    channel.start_consuming()
    
    connection.close()
```

### 2. 性能测试

```python
def test_performance():
    """性能测试"""
    from docker_deployment_examples import PerformanceTester
    
    tester = PerformanceTester('rabbitmq-server')
    result = tester.run_perf_test(
        producers=10,
        consumers=10,
        rate=1000,
        duration=300
    )
    
    assert result['success']
    assert result['metrics']['publish_rate'] > 500
    assert result['metrics']['avg_latency_ms'] < 100
```

### 3. 故障恢复测试

```python
def test_failover():
    """故障恢复测试"""
    import docker
    
    client = docker.from_env()
    
    # 停止主节点
    container = client.containers.get('rabbitmq-node1')
    container.stop()
    
    # 检查从节点是否接管
    import time
    time.sleep(10)
    
    # 验证服务可用性
    # 这里应该测试消息发送和接收
    
    # 重启主节点
    container.start()
    time.sleep(30)
    
    # 验证集群状态
    result = container.exec_run('rabbitmqctl cluster_status')
    assert 'rabbitmq-node1' in result.output.decode()
```

### 4. 备份恢复测试

```python
def test_backup_restore():
    """备份恢复测试"""
    from docker_deployment_examples import BackupManager
    
    backup_manager = BackupManager('rabbitmq-server', './test_backup')
    
    # 创建备份
    backup_path = backup_manager.create_backup()
    assert Path(backup_path).exists()
    
    # 修改数据（添加测试队列和消息）
    # ... 发送测试消息 ...
    
    # 恢复备份
    backup_manager.restore_backup(backup_path)
    
    # 验证数据恢复
    # ... 检查队列和消息 ...
```

## 📊 监控指标

### 关键监控指标

1. **连接相关**
   - `rabbitmq_connections`: 连接数
   - `rabbitmq_channels`: 通道数
   - `rabbitmq_queues`: 队列数

2. **消息相关**
   - `rabbitmq_queue_messages`: 队列消息数
   - `rabbitmq_channel_messages`: 通道消息数
   - `rabbitmq_exchange_messages`: 交换器消息数

3. **性能相关**
   - `rabbitmq_process_resident_memory_bytes`: 内存使用
   - `rabbitmq_process_cpu_user_seconds_total`: CPU使用
   - `rabbitmq_node_fd_used`: 文件描述符使用

### 告警规则

```yaml
# prometheus_rules.yml
groups:
- name: rabbitmq
  rules:
  - alert: RabbitMQDown
    expr: up{job="rabbitmq"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "RabbitMQ instance is down"
      
  - alert: RabbitMQQueueMessagesHigh
    expr: rabbitmq_queue_messages > 10000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ queue {{ $labels.queue }} has high message count"
```

## 🔐 安全最佳实践

### 1. 认证和授权

```bash
# 创建专用用户
docker exec rabbitmq-server rabbitmqctl add_user app_user secure_password
docker exec rabbitmq-server rabbitmqctl set_permissions -p / app_user ".*" ".*" ".*"
docker exec rabbitmq-server rabbitmqctl set_user_tags app_user management
```

### 2. 网络安全

```yaml
# 网络隔离
networks:
  rabbitmq_internal:
    driver: bridge
    internal: true
```

### 3. 数据加密

```conf
# 启用SSL
ssl_options.certfile = /etc/rabbitmq/ssl/cert.pem
ssl_options.keyfile = /etc/rabbitmq/ssl/key.pem
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
```

### 4. 审计日志

```conf
# 启用审计
log_levels.default = info
log_levels.connection = debug
log_levels.authentication_failure_detailed = true
```

## 📈 扩展学习资源

### 官方文档
- [RabbitMQ Docker镜像文档](https://hub.docker.com/_/rabbitmq)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [RabbitMQ集群指南](https://www.rabbitmq.com/clustering.html)

### 社区资源
- [Docker Hub RabbitMQ](https://hub.docker.com/r/library/rabbitmq/)
- [RabbitMQ Management Plugin](https://www.rabbitmq.com/management.html)
- [Prometheus监控集成](https://www.rabbitmq.com/prometheus.html)

### 进阶主题
- Kubernetes部署
- Helm Charts
- Service Mesh集成
- 多数据中心集群
- 流式数据处理

---

## 💡 总结

本章节全面介绍了RabbitMQ的Docker化部署方案，涵盖了从单节点到集群的完整部署流程。通过Docker容器化技术，我们可以实现：

1. **标准化部署**: 确保环境一致性
2. **资源管理**: 灵活的CPU和内存限制
3. **高可用性**: 集群部署和故障恢复
4. **监控运维**: 完整的监控和告警体系
5. **安全加固**: 多层次的安全防护

通过合理使用本章节提供的工具和配置，您可以构建一个生产级的RabbitMQ Docker化环境。

**下一步**: 继续学习第7章，了解RabbitMQ在微服务架构中的应用。