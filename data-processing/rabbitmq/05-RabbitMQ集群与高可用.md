# 05-RabbitMQ集群与高可用

## 概述

在生产环境中，消息系统的可靠性和可用性至关重要。RabbitMQ集群通过分布式架构提供了高可用性、负载均衡和故障恢复能力。本章将深入探讨RabbitMQ集群的配置、管理和最佳实践。

## 1. 集群架构基础

### 1.1 集群概念

RabbitMQ集群是一个由多个RabbitMQ节点组成的逻辑组，这些节点共享队列、交换机、绑定关系和用户信息等元数据。

#### 集群核心特性
- **元数据共享**：队列、交换机、绑定关系在集群中复制
- **消息路由**：消息在集群中根据路由规则正确路由
- **队列镜像**：重要队列可以在多个节点上创建镜像
- **故障转移**：节点故障时自动切换到可用节点

### 1.2 集群架构模型

#### 对等集群（Peer-to-Peer）
```
    [Node1] --- [Node2] --- [Node3]
       |          |          |
       +----------+----------+
                 |
              [Client]
```

#### 负载均衡集群
```
           [Load Balancer]
                 |
    +------------+------------+
    |            |            |
[Node1]      [Node2]      [Node3]
```

#### 分层集群
```
              [Master]
                /  \
               /    \
        [Node1]    [Node2]
             \        /
              +------+
```

### 1.3 集群组件

#### 集群元数据
- **虚拟主机**：集群范围内的虚拟主机配置
- **交换机**：交换机定义和绑定关系
- **队列**：队列定义（非镜像队列的元数据）
- **用户**：用户凭证和权限
- **策略**：集群范围的配置策略

#### Erlang分布式系统
```bash
# Erlang Cookie位置
$HOME/.erlang.cookie

# 检查Erlang分布式名称
erl -name test@hostname
```

## 2. 集群配置与部署

### 2.1 基础集群配置

#### 安装和准备

```bash
# 1. 安装RabbitMQ（所有节点）
sudo apt-get install rabbitmq-server

# 2. 设置Erlang Cookie（所有节点）
# 在每个节点上设置相同的cookie
sudo cp /var/lib/rabbitmq/.erlang.cookie /root/.erlang.cookie
chmod 400 /root/.erlang.cookie

# 3. 设置主机名（每个节点不同）
sudo hostnamectl set-hostname rabbitmq-node1
sudo hostnamectl set-hostname rabbitmq-node2
sudo hostnamectl set-hostname rabbitmq-node3

# 4. 更新/etc/hosts（所有节点）
echo "192.168.1.100 rabbitmq-node1" >> /etc/hosts
echo "192.168.1.101 rabbitmq-node2" >> /etc/hosts
echo "192.168.1.102 rabbitmq-node3" >> /etc/hosts
```

#### 集群加入脚本

```bash
#!/bin/bash
# cluster_setup.sh

NODES=("rabbitmq-node1" "rabbitmq-node2" "rabbitmq-node3")
BASE_PORT=25672

# 停止RabbitMQ服务
for node in "${NODES[@]}"; do
    ssh $node "sudo systemctl stop rabbitmq-server"
done

# 配置环境变量
for i in "${!NODES[@]}"; do
    node=${NODES[$i]}
    port=$((BASE_PORT + i))
    
    ssh $node << EOF
sudo tee /etc/rabbitmq/rabbitmq-env.conf > /dev/null << ENV_EOF
NODENAME=rabbit@$node
NODE_PORT=$port
MNESIA_BASE=/var/lib/rabbitmq/mnesia
LOG_BASE=/var/log/rabbitmq
ENV_EOF

sudo systemctl start rabbitmq-server
EOF
done

# 加入集群
for node in "${NODES[@]:1}"; do
    ssh $node "sudo rabbitmqctl stop_app"
    ssh $node "sudo rabbitmqctl join_cluster rabbit@${NODES[0]}"
    ssh $node "sudo rabbitmqctl start_app"
done

# 检查集群状态
sudo rabbitmqctl cluster_status
```

### 2.2 Docker集群部署

#### Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'
services:
  rabbitmq1:
    image: rabbitmq:3.8-management
    hostname: rabbitmq1
    environment:
      RABBITMQ_ERLANG_COOKIE: "test_cookie"
      RABBITMQ_DEFAULT_USER: "admin"
      RABBITMQ_DEFAULT_PASS: "admin123"
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq1_data:/var/lib/rabbitmq
      - rabbitmq1_logs:/var/log/rabbitmq
    networks:
      - rabbitmq_cluster

  rabbitmq2:
    image: rabbitmq:3.8-management
    hostname: rabbitmq2
    environment:
      RABBITMQ_ERLANG_COOKIE: "test_cookie"
    ports:
      - "5673:5672"
      - "15673:15672"
    volumes:
      - rabbitmq2_data:/var/lib/rabbitmq
      - rabbitmq2_logs:/var/log/rabbitmq
    networks:
      - rabbitmq_cluster
    depends_on:
      - rabbitmq1

  rabbitmq3:
    image: rabbitmq:3.8-management
    hostname: rabbitmq3
    environment:
      RABBITMQ_ERLANG_COOKIE: "test_cookie"
    ports:
      - "5674:5672"
      - "15674:15672"
    volumes:
      - rabbitmq3_data:/var/lib/rabbitmq
      - rabbitmq3_logs:/var/log/rabbitmq
    networks:
      - rabbitmq_cluster
    depends_on:
      - rabbitmq1

volumes:
  rabbitmq1_data:
  rabbitmq1_logs:
  rabbitmq2_data:
  rabbitmq2_logs:
  rabbitmq3_data:
  rabbitmq3_logs:

networks:
  rabbitmq_cluster:
    driver: bridge
```

#### 集群初始化脚本

```bash
#!/bin/bash
# init_cluster.sh

# 等待所有节点启动
sleep 10

# 在第一个节点上创建集群
docker exec rabbitmq1 rabbitmqctl stop_app
docker exec rabbitmq1 rabbitmqctl reset
docker exec rabbitmq1 rabbitmqctl start_app

# 添加其他节点到集群
docker exec rabbitmq2 rabbitmqctl stop_app
docker exec rabbitmq2 rabbitmqctl reset
docker exec rabbitmq2 rabbitmqctl join_cluster rabbit@rabbitmq1
docker exec rabbitmq2 rabbitmqctl start_app

docker exec rabbitmq3 rabbitmqctl stop_app
docker exec rabbitmq3 rabbitmqctl reset
docker exec rabbitmq3 rabbitmqctl join_cluster rabbit@rabbitmq1
docker exec rabbitmq3 rabbitmqctl start_app

# 检查集群状态
docker exec rabbitmq1 rabbitmqctl cluster_status
```

### 2.3 Kubernetes集群部署

#### StateSet配置

```yaml
# rabbitmq-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: rabbitmq-cluster
spec:
  serviceName: rabbitmq-cluster
  replicas: 3
  selector:
    matchLabels:
      app: rabbitmq-cluster
  template:
    metadata:
      labels:
        app: rabbitmq-cluster
    spec:
      containers:
      - name: rabbitmq
        image: rabbitmq:3.8-management-alpine
        ports:
        - containerPort: 5672
          name: amqp
        - containerPort: 15672
          name: management
        env:
        - name: RABBITMQ_ERLANG_COOKIE
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: erlang-cookie
        - name: RABBITMQ_DEFAULT_USER
          value: "admin"
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: admin-password
        volumeMounts:
        - name: rabbitmq-persistent-storage
          mountPath: /var/lib/rabbitmq/mnesia
        readinessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - ping
          initialDelaySeconds: 60
          periodSeconds: 30
      volumes:
      - name: rabbitmq-config
        configMap:
          name: rabbitmq-config
  volumeClaimTemplates:
  - metadata:
      name: rabbitmq-persistent-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

#### 初始化Job

```yaml
# rabbitmq-init-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: rabbitmq-cluster-init
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: init-rabbitmq
        image: rabbitmq:3.8-management-alpine
        command: ["/bin/sh", "-c"]
        args:
        - |
          # 等待所有pod就绪
          until kubectl get statefulset rabbitmq-cluster -o jsonpath='{.status.readyReplicas}' 2>/dev/null | grep -q "3"; do
            echo "Waiting for RabbitMQ cluster to be ready..."
            sleep 5
          done
          
          # 设置集群
          echo "Setting up RabbitMQ cluster..."
          rabbitmqctl stop_app --all
          rabbitmqctl reset --all
          rabbitmqctl start_app --all
          rabbitmqctl set_policy ha-all ".*" '{"ha-mode":"all"}'
      restartPolicy: OnFailure
```

## 3. 镜像队列与高可用

### 3.1 镜像队列概念

镜像队列是RabbitMQ实现高可用的核心机制，它在集群的多个节点上复制队列内容。

#### 镜像类型
- **none**：不镜像
- **all**：镜像到所有节点
- **exactly**：镜像到指定数量的节点
- **nodes**：镜像到指定节点列表

### 3.2 镜像队列配置

#### 通过管理界面配置

```bash
# 创建镜像策略
curl -u admin:admin123 \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{"pattern":"^ha\.", "definition":{"ha-mode":"all", "ha-sync-mode":"automatic"}, "priority":1}' \
  http://localhost:15672/api/policies/%2f/ha-all
```

#### 通过CLI配置

```bash
# 自动镜像到所有节点
rabbitmqctl set_policy ha-all ".*" \
  '{"ha-mode":"all","ha-sync-mode":"automatic"}'

# 镜像到特定节点
rabbitmqctl set_policy ha-nodes "^ha\." \
  '{"ha-mode":"nodes","ha-nodes":["rabbit@node1","rabbit@node2"],"ha-sync-mode":"automatic"}'

# 镜像到指定数量的节点
rabbitmqctl set_policy ha-exactly "^ha\." \
  '{"ha-mode":"exactly","ha-params":2,"ha-sync-mode":"automatic"}'
```

#### Python代码配置镜像

```python
import requests
import json

class RabbitMQClusterManager:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}:15672/api"
        
    def set_mirror_policy(self, policy_name, pattern, definition, priority=0):
        """设置镜像策略"""
        url = f"{self.base_url}/policies/%2f/{policy_name}"
        
        payload = {
            "pattern": pattern,
            "definition": definition,
            "priority": priority
        }
        
        response = requests.put(
            url,
            data=json.dumps(payload),
            auth=(self.username, self.password),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"镜像策略 {policy_name} 设置成功")
            return True
        else:
            print(f"设置镜像策略失败: {response.text}")
            return False
            
    def create_ha_queue(self, queue_name):
        """创建高可用队列"""
        url = f"{self.base_url}/queues/%2f"
        
        payload = {
            "durable": True,
            "arguments": {
                "x-queue-type": "classic"
            }
        }
        
        response = requests.put(
            f"{url}/{queue_name}",
            data=json.dumps(payload),
            auth=(self.username, self.password),
            headers={"Content-Type": "application/json"}
        )
        
        return response.status_code == 200

# 使用示例
manager = RabbitMQClusterManager('localhost', 'admin', 'admin123')

# 设置自动镜像策略
manager.set_mirror_policy(
    'ha-all',
    '^ha\.',
    {
        'ha-mode': 'all',
        'ha-sync-mode': 'automatic'
    }
)

# 创建高可用队列
manager.create_ha_queue('ha-orders')
```

### 3.3 镜像同步

#### 同步模式

- **automatic**：新镜像自动同步
- **manual**：手动触发同步

#### 同步状态监控

```python
def monitor_mirror_sync(self, vhost='%2f'):
    """监控镜像同步状态"""
    url = f"{self.base_url}/queues/{vhost}"
    response = requests.get(url, auth=(self.username, self.password))
    
    if response.status_code == 200:
        queues = response.json()
        
        for queue in queues:
            print(f"队列: {queue['name']}")
            print(f"  状态: {queue['state']}")
            print(f"  镜像数: {queue['mirrors']}")
            
            for mirror in queue.get('mirrors', []):
                print(f"    镜像节点: {mirror['name']}")
                print(f"    同步状态: {mirror['sync_state']}")
```

### 3.4 故障转移机制

#### 客户端连接重试

```python
import pika
import time
from typing import List, Optional

class ClusterConnectionManager:
    def __init__(self, nodes: List[str], username: str, password: str):
        self.nodes = nodes
        self.username = username
        self.password = password
        self.current_node_index = 0
        self.connection = None
        self.channel = None
        
    def connect(self) -> bool:
        """连接集群"""
        for i, node in enumerate(self.nodes):
            try:
                logger.info(f"尝试连接到节点: {node}")
                
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=node.split(':')[0],
                    port=int(node.split(':')[1]) if ':' in node else 5672,
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=5,
                    blocked_connection_timeout=300
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.current_node_index = i
                
                logger.info(f"成功连接到节点: {node}")
                return True
                
            except Exception as e:
                logger.error(f"连接节点 {node} 失败: {e}")
                continue
                
        return False
        
    def reconnect(self) -> bool:
        """重新连接"""
        logger.info("尝试重新连接到集群")
        self.disconnect()
        return self.connect()
        
    def disconnect(self):
        """断开连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            
    def publish(self, exchange: str, routing_key: str, message: dict):
        """发布消息"""
        max_retries = len(self.nodes)
        
        for _ in range(max_retries):
            try:
                if not self.connection or not self.connection.is_open:
                    self.reconnect()
                    
                if self.channel and self.channel.is_open:
                    self.channel.basic_publish(
                        exchange=exchange,
                        routing_key=routing_key,
                        body=json.dumps(message)
                    )
                    return True
                    
            except Exception as e:
                logger.error(f"发布消息失败: {e}")
                # 尝试连接到下一个节点
                self.current_node_index = (self.current_node_index + 1) % len(self.nodes)
                time.sleep(1)
                
        logger.error("所有节点连接失败")
        return False
```

## 4. 负载均衡与流量分发

### 4.1 负载均衡器配置

#### HAProxy配置

```haproxy
# haproxy.cfg
global
    daemon
    maxconn 4096

defaults
    mode tcp
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend rabbitmq_frontend
    bind *:5672
    default_backend rabbitmq_backend

frontend rabbitmq_management
    bind *:15672
    default_backend rabbitmq_management_backend

backend rabbitmq_backend
    balance roundrobin
    option tcplog
    server rabbitmq1 192.168.1.100:5672 check inter 2000 rise 2 fall 3
    server rabbitmq2 192.168.1.101:5672 check inter 2000 rise 2 fall 3
    server rabbitmq3 192.168.1.102:5672 check inter 2000 rise 2 fall 3

backend rabbitmq_management_backend
    balance roundrobin
    option tcplog
    server rabbitmq1 192.168.1.100:15672 check inter 2000 rise 2 fall 3
    server rabbitmq2 192.168.1.101:15672 check inter 2000 rise 2 fall 3
    server rabbitmq3 192.168.1.102:15672 check inter 2000 rise 2 fall 3
```

#### Nginx配置

```nginx
# nginx_rabbitmq.conf
upstream rabbitmq_backend {
    least_conn;
    server 192.168.1.100:5672 max_fails=3 fail_timeout=30s;
    server 192.168.1.101:5672 max_fails=3 fail_timeout=30s;
    server 192.168.1.102:5672 max_fails=3 fail_timeout=30s;
}

upstream rabbitmq_management {
    least_conn;
    server 192.168.1.100:15672 max_fails=3 fail_timeout=30s;
    server 192.168.1.101:15672 max_fails=3 fail_timeout=30s;
    server 192.168.1.102:15672 max_fails=3 fail_timeout=30s;
}

server {
    listen 5672;
    proxy_pass rabbitmq_backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

server {
    listen 15672;
    location / {
        proxy_pass http://rabbitmq_management;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4.2 客户端负载均衡

#### 智能客户端

```python
import random
import pika
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SmartRabbitMQClient:
    def __init__(self, config: Dict):
        self.nodes = config['nodes']
        self.credentials = pika.PlainCredentials(
            config['username'], 
            config['password']
        )
        self.connection_params = []
        
        # 创建每个节点的连接参数
        for node in self.nodes:
            host, port = node.split(':')
            params = pika.ConnectionParameters(
                host=host,
                port=int(port),
                credentials=self.credentials,
                connection_attempts=3,
                retry_delay=5,
                heartbeat=30
            )
            self.connection_params.append(params)
            
    def get_connection_params(self, strategy='random'):
        """根据策略选择连接参数"""
        if strategy == 'random':
            return random.choice(self.connection_params)
        elif strategy == 'round_robin':
            return self.connection_params[0]  # 简单轮询实现
        elif strategy == 'least_connections':
            return self._least_connected_node()
            
    def _least_connected_node(self):
        """选择连接数最少的节点"""
        # 这里简化实现，实际需要获取节点状态
        return random.choice(self.connection_params)
        
    def create_connection(self):
        """创建连接"""
        for attempt in range(len(self.connection_params)):
            try:
                params = self.get_connection_params('random')
                connection = pika.BlockingConnection(params)
                logger.info(f"连接到节点: {params.host}:{params.port}")
                return connection
            except Exception as e:
                logger.error(f"连接失败: {e}")
                continue
                
        raise Exception("无法连接到任何RabbitMQ节点")
        
    def publish_message(self, queue_name: str, message: dict):
        """发布消息"""
        connection = self.create_connection()
        channel = connection.channel()
        
        channel.queue_declare(queue=queue_name, durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        
        connection.close()
        logger.info(f"消息发布到队列: {queue_name}")
```

### 4.3 流量分发策略

#### 基于权重的分发

```python
class WeightedConnectionManager:
    def __init__(self, weighted_nodes: Dict[str, int]):
        self.weighted_nodes = weighted_nodes
        self.total_weight = sum(weight for weight in weighted_nodes.values())
        
    def get_node(self):
        """根据权重选择节点"""
        random_weight = random.randint(1, self.total_weight)
        
        for node, weight in self.weighted_nodes.items():
            random_weight -= weight
            if random_weight <= 0:
                return node
                
        return list(self.weighted_nodes.keys())[0]

# 使用示例
weighted_manager = WeightedConnectionManager({
    'node1:5672': 10,  # 高性能节点，权重高
    'node2:5672': 5,   # 普通节点
    'node3:5672': 1    # 低性能节点，权重低
})
```

#### 基于延迟的分发

```python
import time
import subprocess
import re
from collections import defaultdict

class LatencyAwareClient:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.latency_cache = defaultdict(lambda: float('inf'))
        self.last_check = defaultdict(float)
        
    def measure_latency(self, node: str) -> float:
        """测量节点延迟"""
        try:
            host = node.split(':')[0]
            # 使用ping测量延迟
            result = subprocess.run(
                ['ping', '-c', '3', '-W', '1000', host],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 解析ping结果
            match = re.search(r'min/avg/max.*= ([\d.]+)/([\d.]+)/([\d.]+)', result.stdout)
            if match:
                avg_latency = float(match.group(2))
                return avg_latency
                
        except Exception as e:
            logger.error(f"测量延迟失败 {node}: {e}")
            
        return float('inf')
        
    def get_best_node(self) -> str:
        """选择延迟最低的节点"""
        current_time = time.time()
        best_node = None
        best_latency = float('inf')
        
        for node in self.nodes:
            # 检查缓存是否过期（1分钟）
            if current_time - self.last_check[node] > 60:
                latency = self.measure_latency(node)
                self.latency_cache[node] = latency
                self.last_check[node] = current_time
            else:
                latency = self.latency_cache[node]
                
            if latency < best_latency:
                best_latency = latency
                best_node = node
                
        return best_node or self.nodes[0]
```

## 5. 集群监控与运维

### 5.1 集群状态监控

#### 集群健康检查脚本

```python
import requests
import json
from datetime import datetime
from typing import Dict, List

class ClusterMonitor:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}:15672/api"
        
    def get_cluster_status(self) -> Dict:
        """获取集群状态"""
        url = f"{self.base_url}/cluster-name"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
            
    def get_nodes_status(self) -> List[Dict]:
        """获取所有节点状态"""
        url = f"{self.base_url}/nodes"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取节点状态失败: {e}")
            return []
            
    def get_queue_status(self) -> List[Dict]:
        """获取队列状态"""
        url = f"{self.base_url}/queues"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取队列状态失败: {e}")
            return []
            
    def check_cluster_health(self) -> Dict:
        """集群健康检查"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "cluster_status": self.get_cluster_status(),
            "nodes": self.get_nodes_status(),
            "queues": self.get_queue_status(),
            "health_score": 0
        }
        
        # 计算健康评分
        nodes = status["nodes"]
        if nodes:
            healthy_nodes = sum(1 for node in nodes if node.get("running", False))
            total_nodes = len(nodes)
            status["health_score"] = (healthy_nodes / total_nodes) * 100
            
        return status
        
    def generate_health_report(self) -> str:
        """生成健康报告"""
        health = self.check_cluster_health()
        
        report = f"""
RabbitMQ集群健康报告
===================
时间: {health['timestamp']}
健康评分: {health['health_score']:.1f}%

集群状态:
{json.dumps(health['cluster_status'], indent=2)}

节点详情:
"""
        
        for node in health['nodes']:
            status = "运行中" if node.get("running", False) else "已停止"
            report += f"  - {node.get('name', 'Unknown')} ({node.get('type', 'unknown')}): {status}\n"
            
        report += f"\n队列概况:\n"
        for queue in health['queues']:
            report += f"  - {queue.get('name', 'Unknown')}: {queue.get('messages', 0)} 条消息\n"
            
        return report
```

#### 监控指标收集

```python
import time
import json
from prometheus_client import start_http_server, Gauge, Counter
from threading import Thread

# Prometheus指标
cluster_health_gauge = Gauge('rabbitmq_cluster_health', 'Cluster health percentage')
queue_messages_gauge = Gauge('rabbitmq_queue_messages', 'Number of messages in queue', ['queue_name'])
nodes_connected_gauge = Gauge('rabbitmq_nodes_connected', 'Number of connected nodes')
messages_published_counter = Counter('rabbitmq_messages_published', 'Number of published messages', ['queue_name'])
messages_consumed_counter = Counter('rabbitmq_messages_consumed', 'Number of consumed messages', ['queue_name'])

class ClusterMetricsCollector:
    def __init__(self, monitor: ClusterMonitor, interval: int = 30):
        self.monitor = monitor
        self.interval = interval
        self.running = False
        
    def collect_metrics(self):
        """收集指标"""
        while self.running:
            try:
                # 获取集群状态
                health = self.monitor.check_cluster_health()
                
                # 更新健康评分
                cluster_health_gauge.set(health['health_score'])
                
                # 更新节点数
                running_nodes = sum(1 for node in health['nodes'] if node.get("running", False))
                nodes_connected_gauge.set(running_nodes)
                
                # 更新队列消息数
                for queue in health['queues']:
                    queue_messages_gauge.labels(queue_name=queue.get('name', 'unknown')).set(
                        queue.get('messages', 0)
                    )
                    
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"收集指标失败: {e}")
                time.sleep(5)
                
    def start_collector(self):
        """启动指标收集器"""
        self.running = True
        thread = Thread(target=self.collect_metrics)
        thread.daemon = True
        thread.start()
        
    def stop_collector(self):
        """停止指标收集器"""
        self.running = False
```

### 5.2 自动化运维脚本

#### 节点管理脚本

```python
import paramiko
import time
from typing import List

class ClusterOperations:
    def __init__(self, nodes: List[str], username: str, key_file: str):
        self.nodes = nodes
        self.username = username
        self.key_file = key_file
        
    def execute_on_node(self, node: str, command: str) -> str:
        """在指定节点执行命令"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=node,
                username=self.username,
                key_filename=self.key_file
            )
            
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            ssh.close()
            
            if error:
                logger.error(f"命令执行错误: {error}")
                
            return output
            
        except Exception as e:
            logger.error(f"在节点 {node} 执行命令失败: {e}")
            return ""
            
    def restart_node(self, node: str):
        """重启节点"""
        logger.info(f"重启节点: {node}")
        command = "sudo systemctl restart rabbitmq-server"
        return self.execute_on_node(node, command)
        
    def stop_node(self, node: str):
        """停止节点"""
        logger.info(f"停止节点: {node}")
        command = "sudo systemctl stop rabbitmq-server"
        return self.execute_on_node(node, command)
        
    def start_node(self, node: str):
        """启动节点"""
        logger.info(f"启动节点: {node}")
        command = "sudo systemctl start rabbitmq-server"
        return self.execute_on_node(node, command)
        
    def check_node_health(self, node: str) -> Dict:
        """检查节点健康状态"""
        commands = {
            "status": "sudo systemctl is-active rabbitmq-server",
            "processes": "ps aux | grep beam | grep -v grep",
            "memory": "free -h",
            "disk": "df -h /var/lib/rabbitmq"
        }
        
        health_status = {"node": node, "status": "unknown"}
        
        for check_name, command in commands.items():
            output = self.execute_on_node(node, command)
            health_status[check_name] = output
            
        return health_status
        
    def add_node_to_cluster(self, new_node: str, master_node: str):
        """添加节点到集群"""
        logger.info(f"添加节点 {new_node} 到集群")
        
        commands = [
            f"sudo rabbitmqctl stop_app",
            f"sudo rabbitmqctl reset",
            f"sudo rabbitmqctl join_cluster rabbit@{master_node.split('.')[0]}",
            f"sudo rabbitmqctl start_app"
        ]
        
        for command in commands:
            output = self.execute_on_node(new_node, command)
            logger.info(f"执行: {command}, 结果: {output}")
            time.sleep(2)
            
    def remove_node_from_cluster(self, node: str):
        """从集群中移除节点"""
        logger.info(f"从集群移除节点: {node}")
        
        commands = [
            f"sudo rabbitmqctl stop_app",
            f"sudo rabbitmqctl forget_cluster_node rabbit@{node.split('.')[0]}"
        ]
        
        for command in commands:
            output = self.execute_on_node(node, command)
            logger.info(f"执行: {command}, 结果: {output}")
            time.sleep(2)
```

### 5.3 告警系统

#### Prometheus告警规则

```yaml
# rabbitmq_alerts.yml
groups:
- name: rabbitmq.rules
  rules:
  - alert: RabbitMQDown
    expr: up{job="rabbitmq"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "RabbitMQ instance is down"
      description: "RabbitMQ instance {{ $labels.instance }} is down"
      
  - alert: RabbitMQClusterNotHealthy
    expr: rabbitmq_cluster_health < 80
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ cluster health degraded"
      description: "Cluster health is {{ $value }}%"
      
  - alert: QueueBacklogHigh
    expr: rabbitmq_queue_messages > 1000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High message backlog in {{ $labels.queue_name }}"
      description: "Queue {{ $labels.queue_name }} has {{ $value }} messages"
      
  - alert: NodeMemoryHigh
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is {{ $value }}%"
```

#### 邮件告警脚本

```python
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import json

class AlertManager:
    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
        
    def send_alert(self, subject: str, message: str, severity: str = "info"):
        """发送告警邮件"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.smtp_config['sender']
            msg['To'] = ', '.join(self.smtp_config['recipients'])
            msg['Subject'] = f"[{severity.upper()}] {subject}"
            
            # 设置HTML内容
            html_content = f"""
            <html>
            <body>
                <h2>RabbitMQ集群告警</h2>
                <p><strong>告警级别:</strong> {severity.upper()}</p>
                <p><strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>内容:</strong></p>
                <pre>{message}</pre>
                <hr>
                <p><small>此邮件由RabbitMQ监控系统自动发送</small></p>
            </body>
            </html>
            """
            
            msg.attach(MimeText(html_content, 'html'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                if self.smtp_config.get('use_tls', False):
                    server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
                
            logger.info(f"告警邮件发送成功: {subject}")
            
        except Exception as e:
            logger.error(f"发送告警邮件失败: {e}")
            
    def check_and_alert(self, monitor: ClusterMonitor):
        """检查并告警"""
        health = monitor.check_cluster_health()
        
        # 检查集群健康状态
        if health['health_score'] < 80:
            self.send_alert(
                "集群健康状态告警",
                f"集群健康评分: {health['health_score']}%\n{json.dumps(health, indent=2)}",
                "warning"
            )
            
        # 检查队列积压
        for queue in health['queues']:
            if queue.get('messages', 0) > 1000:
                self.send_alert(
                    f"队列积压告警 - {queue.get('name', 'Unknown')}",
                    f"队列: {queue.get('name', 'Unknown')}\n消息数: {queue.get('messages', 0)}",
                    "warning"
                )
                
        # 检查节点状态
        for node in health['nodes']:
            if not node.get('running', False):
                self.send_alert(
                    f"节点故障告警 - {node.get('name', 'Unknown')}",
                    f"节点: {node.get('name', 'Unknown')}\n状态: 已停止",
                    "critical"
                )
```

## 6. 性能调优与故障处理

### 6.1 性能调优

#### JVM调优

```bash
# /etc/rabbitmq/rabbitmq-env.conf
RABBITMQ_NODENAME=rabbit@localhost
RABBITMQ_NODE_PORT=5672

# JVM参数
RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS="-noinput +MBas agecbf +MHas agecbf +MBlmbcs 512 +MFlmbcs 2048 +MBlmbcs 512 +MFlmbcs 2048 +HMs 512"

# 环境变量
export RABBITMQ_NODENAME=rabbit@localhost
export RABBITMQ_CONFIG_FILE=/etc/rabbitmq/rabbitmq
export RABBITMQ_MNESIA_BASE=/var/lib/rabbitmq/mnesia
export RABBITMQ_LOG_BASE=/var/log/rabbitmq
```

#### 内核参数调优

```bash
# /etc/sysctl.conf
# 网络参数
net.core.somaxconn = 4096
net.core.netdev_max_backlog = 4096
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216

# 文件描述符限制
fs.file-max = 2097152
fs.nr_open = 2097152

# 应用参数
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_tw_buckets = 400000
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3

# 应用设置
sudo sysctl -p
```

#### RabbitMQ配置调优

```json
// /etc/rabbitmq/rabbitmq.json
{
  "default_user": "admin",
  "default_pass": "admin123",
  "default_permissions": [
    ".*",
    ".*",
    ".*"
  ],
  "listeners": {
    "tcp": {
      "default": 5672,
      "backlog": 128,
      "nodelay": true
    }
  },
  "cluster_formation": {
    "peer_discovery_backend": "rabbitmq_discovery_classic_config"
  },
  "memory_watermark": {
    "absolute": "4GB"
  },
  "disk_watermark": {
    "absolute": "3GB"
  },
  "cluster_keepalive_interval": 10000,
  "heartbeat": 30,
  "queue_leader_locator": "min-nodes",
  "ha_mirroring_supervisor_mode": "one-shot"
}
```

### 6.2 故障处理

#### 常见故障诊断

```python
class FaultDiagnosis:
    def __init__(self, monitor: ClusterMonitor):
        self.monitor = monitor
        
    def diagnose_node_crashed(self, node_name: str) -> Dict:
        """节点崩溃诊断"""
        diagnosis = {
            "issue": "Node Crash",
            "node": node_name,
            "checks": []
        }
        
        # 检查系统日志
        check_result = self._check_system_logs(node_name)
        diagnosis["checks"].append(check_result)
        
        # 检查磁盘空间
        check_result = self._check_disk_space(node_name)
        diagnosis["checks"].append(check_result)
        
        # 检查内存使用
        check_result = self._check_memory_usage(node_name)
        diagnosis["checks"].append(check_result)
        
        # 检查Erlang进程
        check_result = self._check_erlang_process(node_name)
        diagnosis["checks"].append(check_result)
        
        return diagnosis
        
    def diagnose_cluster_split_brain(self) -> Dict:
        """集群脑裂诊断"""
        health = self.monitor.check_cluster_health()
        
        diagnosis = {
            "issue": "Cluster Split Brain",
            "nodes": health['nodes'],
            "quorum_check": self._check_quorum()
        }
        
        return diagnosis
        
    def _check_system_logs(self, node: str) -> Dict:
        """检查系统日志"""
        return {
            "check": "System Logs",
            "description": "检查/var/log/rabbitmq/目录下的错误日志",
            "command": f"tail -n 100 /var/log/rabbitmq/rabbit@{node}.log",
            "expected": "无严重错误信息"
        }
        
    def _check_disk_space(self, node: str) -> Dict:
        """检查磁盘空间"""
        return {
            "check": "Disk Space",
            "description": "检查/var/lib/rabbitmq目录磁盘空间",
            "command": "df -h /var/lib/rabbitmq",
            "expected": "可用空间 > 10%"
        }
        
    def _check_memory_usage(self, node: str) -> Dict:
        """检查内存使用"""
        return {
            "check": "Memory Usage",
            "description": "检查节点内存使用率",
            "command": "free -h",
            "expected": "可用内存 > 20%"
        }
        
    def _check_erlang_process(self, node: str) -> Dict:
        """检查Erlang进程"""
        return {
            "check": "Erlang Process",
            "description": "检查beam.smp进程状态",
            "command": "ps aux | grep beam",
            "expected": "进程正常运行"
        }
        
    def _check_quorum(self) -> Dict:
        """检查集群仲裁"""
        nodes = self.monitor.get_nodes_status()
        running_nodes = [node for node in nodes if node.get("running", False)]
        
        return {
            "total_nodes": len(nodes),
            "running_nodes": len(running_nodes),
            "quorum": len(running_nodes) > len(nodes) / 2,
            "recommendation": "需要至少 majority 节点在线"
        }
```

#### 故障恢复脚本

```python
import subprocess
import time
from typing import List

class ClusterRecovery:
    def __init__(self, ops: ClusterOperations):
        self.ops = ops
        
    def recover_node(self, failed_node: str, master_node: str) -> bool:
        """恢复故障节点"""
        logger.info(f"开始恢复故障节点: {failed_node}")
        
        try:
            # 1. 停止故障节点
            self.ops.stop_node(failed_node)
            time.sleep(5)
            
            # 2. 清理Mnesia数据库
            self._clean_mnesia_data(failed_node)
            
            # 3. 重启节点
            self.ops.start_node(failed_node)
            time.sleep(10)
            
            # 4. 重新加入集群
            self.ops.add_node_to_cluster(failed_node, master_node)
            
            # 5. 验证恢复结果
            time.sleep(30)  # 等待集群同步
            return self._verify_recovery(failed_node)
            
        except Exception as e:
            logger.error(f"恢复节点失败: {e}")
            return False
            
    def _clean_mnesia_data(self, node: str):
        """清理Mnesia数据"""
        commands = [
            "sudo systemctl stop rabbitmq-server",
            "sudo rm -rf /var/lib/rabbitmq/mnesia/*",
            "sudo systemctl start rabbitmq-server"
        ]
        
        for command in commands:
            output = self.ops.execute_on_node(node, command)
            logger.info(f"执行: {command}")
            time.sleep(3)
            
    def _verify_recovery(self, node: str) -> bool:
        """验证恢复结果"""
        try:
            # 检查节点是否在线
            node_status = self.ops.check_node_health(node)
            
            if "running" in node_status.get("status", ""):
                logger.info(f"节点 {node} 恢复成功")
                return True
            else:
                logger.error(f"节点 {node} 恢复失败")
                return False
                
        except Exception as e:
            logger.error(f"验证恢复结果失败: {e}")
            return False
            
    def handle_cluster_split_brain(self, nodes: List[str]) -> bool:
        """处理集群脑裂"""
        logger.info("检测到集群脑裂，开始处理")
        
        try:
            # 1. 确定主集群（大多数节点）
            running_nodes = []
            for node in nodes:
                status = self.ops.check_node_health(node)
                if "running" in status.get("status", ""):
                    running_nodes.append(node)
                    
            if len(running_nodes) > len(nodes) / 2:
                master_cluster = running_nodes
                slave_cluster = [node for node in nodes if node not in running_nodes]
            else:
                master_cluster = nodes[:len(nodes)//2 + 1]
                slave_cluster = [node for node in nodes if node not in master_cluster]
                
            logger.info(f"主集群节点: {master_cluster}")
            logger.info(f"从集群节点: {slave_cluster}")
            
            # 2. 停止从集群节点
            for node in slave_cluster:
                self.ops.stop_node(node)
                time.sleep(2)
                
            # 3. 重置并重新加入从集群节点
            for node in slave_cluster:
                self.ops.stop_node(node)
                self._clean_mnesia_data(node)
                self.ops.start_node(node)
                time.sleep(10)
                self.ops.add_node_to_cluster(node, master_cluster[0])
                time.sleep(5)
                
            # 4. 验证恢复
            time.sleep(30)
            return self._verify_cluster_health(nodes)
            
        except Exception as e:
            logger.error(f"处理集群脑裂失败: {e}")
            return False
            
    def _verify_cluster_health(self, nodes: List[str]) -> bool:
        """验证集群健康"""
        healthy_count = 0
        
        for node in nodes:
            status = self.ops.check_node_health(node)
            if "running" in status.get("status", ""):
                healthy_count += 1
                
        return healthy_count == len(nodes)
```

## 7. 最佳实践与建议

### 7.1 集群设计原则

#### 架构设计原则
1. **奇数节点**: 使用3、5、7等奇数个节点确保仲裁
2. **地理分布**: 根据业务需求考虑节点地理分布
3. **负载分离**: 管理接口和消息处理接口分离
4. **资源隔离**: 不同环境的集群物理隔离

#### 容量规划
```python
def calculate_cluster_capacity(messages_per_second: int, 
                             message_size_kb: int,
                             retention_hours: int) -> Dict:
    """计算集群容量需求"""
    
    # 消息存储需求
    messages_per_hour = messages_per_second * 3600
    storage_per_hour_mb = (messages_per_hour * message_size_kb) / 1024
    storage_per_day_mb = storage_per_hour_mb * 24
    storage_needed_gb = (storage_per_day_mb * retention_hours) / 24 / 1024
    
    # CPU和内存需求（基于经验公式）
    cpu_cores_per_node = max(4, messages_per_second // 1000)
    memory_gb_per_node = max(8, storage_needed_gb // 10)
    
    # 节点数量建议
    recommended_nodes = max(3, int(messages_per_second / 5000) + 1)
    
    return {
        "storage_per_node_gb": storage_needed_gb,
        "cpu_cores_per_node": cpu_cores_per_node,
        "memory_gb_per_node": memory_gb_per_node,
        "recommended_nodes": recommended_nodes,
        "warnings": []
    }
```

### 7.2 监控最佳实践

#### 关键监控指标
```python
class KeyMetrics:
    """关键监控指标"""
    
    CRITICAL_METRICS = {
        "cluster_nodes_down": "集群节点故障",
        "queue_backlog_critical": "队列严重积压", 
        "memory_usage_critical": "内存使用率过高",
        "disk_space_critical": "磁盘空间不足"
    }
    
    WARNING_METRICS = {
        "queue_backlog_warning": "队列积压警告",
        "memory_usage_warning": "内存使用警告",
        "connection_count_warning": "连接数过高"
    }
    
    HEALTH_METRICS = {
        "cluster_health_score": "集群健康评分",
        "message_throughput": "消息吞吐量",
        "consumer_lag": "消费者延迟"
    }
```

### 7.3 运维最佳实践

#### 备份策略
```bash
#!/bin/bash
# backup_cluster.sh

BACKUP_DIR="/var/backups/rabbitmq"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CLUSTER_BACKUP="$BACKUP_DIR/cluster_$TIMESTAMP"

mkdir -p $CLUSTER_BACKUP

# 备份配置
cp -r /etc/rabbitmq/* $CLUSTER_BACKUP/

# 备份Mnesia数据库
for node in node1 node2 node3; do
    ssh $node "tar -czf - /var/lib/rabbitmq/mnesia" > $CLUSTER_BACKUP/mnesia_$node.tar.gz
done

# 备份日志
for node in node1 node2 node3; do
    ssh $node "tar -czf - /var/log/rabbitmq" > $CLUSTER_BACKUP/logs_$node.tar.gz
done

echo "集群备份完成: $CLUSTER_BACKUP"
```

#### 升级策略
```python
class ClusterUpgradeManager:
    """集群升级管理器"""
    
    def __init__(self, ops: ClusterOperations):
        self.ops = ops
        
    def rolling_upgrade(self, nodes: List[str], new_version: str) -> bool:
        """滚动升级"""
        for i, node in enumerate(nodes):
            logger.info(f"升级节点 {node} 到版本 {new_version}")
            
            # 1. 通知负载均衡器暂时不分配新连接到该节点
            
            # 2. 停止节点
            self.ops.stop_node(node)
            
            # 3. 升级软件
            self._upgrade_software(node, new_version)
            
            # 4. 重启节点
            self.ops.start_node(node)
            
            # 5. 等待节点就绪
            time.sleep(30)
            
            # 6. 验证节点状态
            if not self._verify_node_status(node):
                logger.error(f"节点 {node} 升级后状态异常")
                return False
                
            # 7. 恢复负载均衡器分配
            
            logger.info(f"节点 {node} 升级完成")
            
        return True
        
    def _upgrade_software(self, node: str, version: str):
        """升级软件"""
        commands = [
            f"sudo apt-get update",
            f"sudo apt-get install -y rabbitmq-server={version}"
        ]
        
        for command in commands:
            output = self.ops.execute_on_node(node, command)
            logger.info(f"执行: {command}")
            time.sleep(10)
```

## 8. 总结

RabbitMQ集群与高可用性是构建可靠消息系统的关键要素。本章涵盖了：

1. **集群架构**: 理解了集群的基本概念和不同架构模型
2. **配置部署**: 掌握了手动、Docker、Kubernetes等不同方式的集群部署
3. **镜像队列**: 学会了高可用队列的配置和管理
4. **负载均衡**: 了解了多种负载均衡策略和实现方式
5. **监控运维**: 掌握了集群监控、告警和自动化运维
6. **性能调优**: 学会了系统级和RabbitMQ级别的性能优化
7. **故障处理**: 了解了常见故障的诊断和恢复方法
8. **最佳实践**: 总结了生产环境部署的最佳实践

通过本章节的学习，你将能够设计和部署高可用的RabbitMQ集群，确保消息系统的稳定性和可靠性。在实际部署中，建议结合具体的业务需求和基础设施条件，选择合适的架构方案和运维策略。