# Apache Airflow 高可用部署指南

## 1. 概述

### 1.1 目的
本文档旨在为Apache Airflow提供高可用部署的完整指南，涵盖架构设计、组件冗余、负载均衡、故障转移、监控告警等方面，确保Airflow服务在生产环境中的稳定性和可靠性。

### 1.2 适用范围
本指南适用于所有需要在生产环境中部署高可用Apache Airflow集群的项目，包括金融、电商、数据科学等对服务可用性有严格要求的场景。

### 1.3 高可用架构概览
```mermaid
graph TD
    A[客户端请求] --> B[负载均衡器]
    B --> C1[Web Server 1]
    B --> C2[Web Server 2]
    B --> C3[Web Server N]
    
    C1 --> D[(共享存储)]
    C2 --> D
    C3 --> D
    
    C1 --> E[数据库]
    C2 --> E
    C3 --> E
    
    F[Schedulers] --> D
    F --> E
    F --> G[Redis/RabbitMQ]
    
    H[Workers] --> G
    H --> D
    H --> E
    
    I[Triggerers] --> D
    I --> E
    
    J[监控系统] --> C1
    J --> C2
    J --> C3
    J --> F
    J --> H
    J --> I
    
    K[告警系统] --> J
```

## 2. 架构设计原则

### 2.1 无状态设计
```yaml
# 无状态Web Server配置
webserver:
  # 禁用本地会话存储
  secret_key: "随机生成的密钥"
  rbac: true
  session_backend: "database"  # 使用数据库存储会话
  
# 无状态Worker配置
worker:
  # 不在本地存储状态
  dag_processing_logs_location: "/shared/logs"
  child_process_log_directory: "/shared/logs/scheduler"
```

### 2.2 组件冗余
```yaml
# 组件冗余配置
# Web Server冗余
webserver:
  replicas: 3  # 至少3个副本
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
      
# Scheduler冗余
scheduler:
  replicas: 2  # 至少2个副本
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
      
# Worker冗余
worker:
  replicas: 5  # 根据负载调整
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    
# Triggerer冗余
triggerer:
  replicas: 2  # 至少2个副本
```

### 2.3 数据一致性
```sql
-- 数据一致性检查脚本
-- 检查DAG版本一致性
SELECT 
    dag_id,
    COUNT(DISTINCT fileloc) as file_versions,
    COUNT(*) as total_instances
FROM serialized_dag
GROUP BY dag_id
HAVING COUNT(DISTINCT fileloc) > 1;

-- 检查任务实例状态一致性
SELECT 
    dag_id,
    task_id,
    execution_date,
    COUNT(DISTINCT state) as state_count
FROM task_instance
GROUP BY dag_id, task_id, execution_date
HAVING COUNT(DISTINCT state) > 1;

-- 检查DAG运行状态一致性
SELECT 
    dag_id,
    execution_date,
    COUNT(DISTINCT state) as state_count
FROM dag_run
GROUP BY dag_id, execution_date
HAVING COUNT(DISTINCT state) > 1;
```

## 3. 数据库高可用

### 3.1 PostgreSQL主从复制
```yaml
# PostgreSQL主从复制配置
# 主库配置 postgresql.conf
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 256MB
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
hot_standby = on

# 从库配置 recovery.conf
standby_mode = on
primary_conninfo = 'host=postgres-master port=5432 user=replicator password=replicator_password'
primary_slot_name = 'airflow_replica_slot'
hot_standby = on

# 从库配置 postgresql.conf
hot_standby = on
max_standby_archive_delay = 30s
max_standby_streaming_delay = 30s
```

### 3.2 数据库连接池
```python
# database_connection_pool.py
# 数据库连接池配置

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import logging

class AirflowDatabasePool:
    def __init__(self, database_url: str, pool_size: int = 20, max_overflow: int = 30):
        self.logger = logging.getLogger(__name__)
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine = None
        self._create_engine()
        
    def _create_engine(self):
        """创建数据库引擎"""
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_pre_ping=True,  # 连接前检查
            pool_recycle=3600,   # 1小时回收连接
            echo=False
        )
        
    def get_connection(self):
        """获取数据库连接"""
        try:
            connection = self.engine.connect()
            self.logger.debug("成功获取数据库连接")
            return connection
        except Exception as e:
            self.logger.error(f"获取数据库连接失败: {e}")
            raise
            
    def execute_query(self, query: str, params: dict = None):
        """执行查询"""
        with self.get_connection() as conn:
            result = conn.execute(query, params or {})
            return result.fetchall()
            
    def execute_transaction(self, queries: list):
        """执行事务"""
        with self.get_connection() as conn:
            trans = conn.begin()
            try:
                for query, params in queries:
                    conn.execute(query, params or {})
                trans.commit()
                self.logger.info("事务执行成功")
            except Exception as e:
                trans.rollback()
                self.logger.error(f"事务执行失败: {e}")
                raise

# 使用示例
def setup_airflow_database_pool():
    """设置Airflow数据库连接池"""
    db_url = "postgresql://airflow:password@postgres-ha:5432/airflow"
    pool = AirflowDatabasePool(db_url, pool_size=20, max_overflow=30)
    return pool
```

### 3.3 数据库故障转移
```bash
#!/bin/bash
# database_failover.sh
# 数据库故障转移脚本

# 检查主库状态
check_master_status() {
    local master_host=$1
    local master_port=$2
    
    pg_isready -h $master_host -p $master_port
    return $?
}

# 切换主从
promote_standby() {
    local standby_host=$1
    local standby_port=$2
    
    echo "正在提升备库为新主库: $standby_host:$standby_port"
    
    # 在备库上执行提升
    ssh $standby_host "pg_ctl promote -D /var/lib/postgresql/data"
    
    # 更新配置
    update_application_config $standby_host $standby_port
    
    echo "备库提升完成"
}

# 更新应用配置
update_application_config() {
    local new_master_host=$1
    local new_master_port=$2
    
    # 更新Kubernetes ConfigMap
    kubectl patch configmap airflow-config -n airflow \
        -p='{"data":{"DATABASE_HOST": "'$new_master_host'"}}'
        
    # 重启相关服务
    kubectl rollout restart deployment airflow-webserver -n airflow
    kubectl rollout restart deployment airflow-scheduler -n airflow
}

# 主故障转移逻辑
main_failover() {
    local current_master="postgres-master"
    local standby1="postgres-standby1"
    local standby2="postgres-standby2"
    
    # 检查主库状态
    if ! check_master_status $current_master 5432; then
        echo "主库故障检测到，开始故障转移..."
        
        # 选择新的主库
        if check_master_status $standby1 5432; then
            promote_standby $standby1 5432
        elif check_master_status $standby2 5432; then
            promote_standby $standby2 5432
        else
            echo "所有数据库实例都不可用，无法进行故障转移"
            exit 1
        fi
    else
        echo "主库运行正常"
    fi
}

# 定期检查
while true; do
    main_failover
    sleep 30
done
```

## 4. 消息队列高可用

### 4.1 Redis集群模式
```yaml
# redis-cluster.yaml
# Redis集群配置

# Redis主节点
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-master
spec:
  serviceName: redis-master
  replicas: 3
  selector:
    matchLabels:
      app: redis
      role: master
  template:
    metadata:
      labels:
        app: redis
        role: master
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          command:
            - "redis-server"
          args:
            - "--cluster-enabled"
            - "yes"
            - "--cluster-config-file"
            - "nodes.conf"
            - "--cluster-node-timeout"
            - "15000"
            - "--appendonly"
            - "yes"
          ports:
            - containerPort: 6379
              name: redis
          volumeMounts:
            - name: redis-data
              mountPath: /data
      volumes:
        - name: redis-data
          persistentVolumeClaim:
            claimName: redis-data-pvc
            
# Redis从节点
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-slave
spec:
  serviceName: redis-slave
  replicas: 3
  selector:
    matchLabels:
      app: redis
      role: slave
  template:
    metadata:
      labels:
        app: redis
        role: slave
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          command:
            - "redis-server"
          args:
            - "--slaveof"
            - "redis-master-0.redis-master"
            - "6379"
            - "--appendonly"
            - "yes"
          ports:
            - containerPort: 6379
              name: redis
          volumeMounts:
            - name: redis-data
              mountPath: /data
      volumes:
        - name: redis-data
          persistentVolumeClaim:
            claimName: redis-data-pvc
```

### 4.2 RabbitMQ集群模式
```yaml
# rabbitmq-cluster.yaml
# RabbitMQ集群配置

apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: rabbitmq
spec:
  serviceName: rabbitmq
  replicas: 3
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
        - name: rabbitmq
          image: rabbitmq:3-management
          env:
            - name: RABBITMQ_ERLANG_COOKIE
              value: "SWQOKODSQALRPCLNMEQG"
            - name: RABBITMQ_DEFAULT_USER
              value: "airflow"
            - name: RABBITMQ_DEFAULT_PASS
              value: "airflow"
            - name: RABBITMQ_DEFAULT_VHOST
              value: "/"
          ports:
            - containerPort: 5672
              name: amqp
            - containerPort: 15672
              name: http
          volumeMounts:
            - name: rabbitmq-data
              mountPath: /var/lib/rabbitmq
            - name: rabbitmq-config
              mountPath: /etc/rabbitmq/
      volumes:
        - name: rabbitmq-config
          configMap:
            name: rabbitmq-config
  volumeClaimTemplates:
    - metadata:
        name: rabbitmq-data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        resources:
          requests:
            storage: 10Gi
            
# RabbitMQ配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: rabbitmq-config
data:
  rabbitmq.conf: |
    cluster_formation.peer_discovery_backend = rabbit_peer_discovery_k8s
    cluster_formation.k8s.host = kubernetes.default.svc.cluster.local
    cluster_formation.k8s.address_type = hostname
    cluster_formation.node_cleanup.interval = 30
    cluster_formation.node_cleanup.only_log_warning = true
    cluster_partition_handling = autoheal
    queue_master_locator = min-masters
    loopback_users.guest = false
```

### 4.3 消息队列监控
```python
# message_queue_monitoring.py
# 消息队列监控

import redis
import pika
import logging
import time
from typing import Dict, Any

class MessageQueueMonitor:
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379,
                 rabbitmq_host: str = "localhost", rabbitmq_port: int = 5672):
        self.logger = logging.getLogger(__name__)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.redis_client = None
        self.rabbitmq_client = None
        
    def connect_redis(self):
        """连接Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.info("Redis连接成功")
        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            raise
            
    def connect_rabbitmq(self):
        """连接RabbitMQ"""
        try:
            credentials = pika.PlainCredentials('airflow', 'airflow')
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials
            )
            self.rabbitmq_client = pika.BlockingConnection(parameters)
            self.logger.info("RabbitMQ连接成功")
        except Exception as e:
            self.logger.error(f"RabbitMQ连接失败: {e}")
            raise
            
    def get_redis_metrics(self) -> Dict[str, Any]:
        """获取Redis指标"""
        if not self.redis_client:
            self.connect_redis()
            
        try:
            info = self.redis_client.info()
            metrics = {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
            return metrics
        except Exception as e:
            self.logger.error(f"获取Redis指标失败: {e}")
            return {}
            
    def get_rabbitmq_metrics(self) -> Dict[str, Any]:
        """获取RabbitMQ指标"""
        if not self.rabbitmq_client:
            self.connect_rabbitmq()
            
        try:
            channel = self.rabbitmq_client.channel()
            queues = channel.queue_declare(queue='celery', passive=True)
            
            metrics = {
                'message_count': queues.method.message_count,
                'consumer_count': queues.method.consumer_count
            }
            
            channel.close()
            return metrics
        except Exception as e:
            self.logger.error(f"获取RabbitMQ指标失败: {e}")
            return {}
            
    def check_queue_health(self) -> Dict[str, Any]:
        """检查队列健康状态"""
        health_status = {
            'timestamp': time.time(),
            'redis': self.get_redis_metrics(),
            'rabbitmq': self.get_rabbitmq_metrics()
        }
        
        # 检查队列积压
        redis_metrics = health_status['redis']
        rabbitmq_metrics = health_status['rabbitmq']
        
        if redis_metrics.get('instantaneous_ops_per_sec', 0) > 1000:
            self.logger.warning("Redis操作频率过高")
            
        if rabbitmq_metrics.get('message_count', 0) > 10000:
            self.logger.warning("RabbitMQ消息积压严重")
            
        return health_status

# 使用示例
def monitor_message_queues():
    """监控消息队列"""
    monitor = MessageQueueMonitor(
        redis_host="redis-cluster",
        rabbitmq_host="rabbitmq"
    )
    
    while True:
        try:
            metrics = monitor.check_queue_health()
            print(f"队列健康状态: {metrics}")
            time.sleep(30)
        except Exception as e:
            print(f"监控失败: {e}")
            time.sleep(5)
```

## 5. Web Server高可用

### 5.1 负载均衡配置
```yaml
# ingress.yaml
# Ingress负载均衡配置

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airflow-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "route"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
    nginx.ingress.kubernetes.io/upstream-hash-by: "$remote_addr"  # IP哈希
spec:
  rules:
    - host: airflow.company.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: airflow-webserver
                port:
                  number: 8080
  tls:
    - hosts:
        - airflow.company.com
      secretName: airflow-tls
      
# Service配置
apiVersion: v1
kind: Service
metadata:
  name: airflow-webserver
spec:
  selector:
    app: airflow
    component: webserver
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
  sessionAffinity: ClientIP  # 客户端IP亲和性
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

### 5.2 Web Server健康检查
```python
# webserver_health_check.py
# Web Server健康检查

import requests
import logging
import time
from typing import Dict, List
import psutil
import socket

class WebServerHealthChecker:
    def __init__(self, webserver_urls: List[str], timeout: int = 5):
        self.logger = logging.getLogger(__name__)
        self.webserver_urls = webserver_urls
        self.timeout = timeout
        
    def check_http_health(self, url: str) -> Dict[str, Any]:
        """检查HTTP健康状态"""
        try:
            response = requests.get(
                f"{url}/health",
                timeout=self.timeout
            )
            
            return {
                'url': url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'healthy': response.status_code == 200,
                'timestamp': time.time()
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP健康检查失败 {url}: {e}")
            return {
                'url': url,
                'status_code': None,
                'response_time': None,
                'healthy': False,
                'error': str(e),
                'timestamp': time.time()
            }
            
    def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_connections': len(psutil.net_connections()),
            'timestamp': time.time()
        }
        
    def check_database_connectivity(self, db_url: str) -> bool:
        """检查数据库连接"""
        try:
            # 这里应该实际测试数据库连接
            # 简化实现
            return True
        except Exception as e:
            self.logger.error(f"数据库连接检查失败: {e}")
            return False
            
    def perform_health_check(self) -> Dict[str, Any]:
        """执行完整的健康检查"""
        results = {
            'timestamp': time.time(),
            'http_checks': [],
            'system_health': self.check_system_health(),
            'database_healthy': self.check_database_connectivity("postgresql://...")
        }
        
        # 检查每个Web Server实例
        for url in self.webserver_urls:
            http_result = self.check_http_health(url)
            results['http_checks'].append(http_result)
            
        # 计算整体健康状态
        healthy_servers = sum(1 for check in results['http_checks'] if check['healthy'])
        results['overall_healthy'] = (
            healthy_servers >= len(self.webserver_urls) // 2 + 1 and  # 多数节点健康
            results['system_health']['cpu_percent'] < 80 and
            results['system_health']['memory_percent'] < 80 and
            results['system_health']['disk_usage'] < 80 and
            results['database_healthy']
        )
        
        return results

# 使用示例
def run_webserver_health_checks():
    """运行Web Server健康检查"""
    checker = WebServerHealthChecker([
        "http://airflow-webserver-0.airflow-webserver:8080",
        "http://airflow-webserver-1.airflow-webserver:8080",
        "http://airflow-webserver-2.airflow-webserver:8080"
    ])
    
    while True:
        try:
            results = checker.perform_health_check()
            print(f"健康检查结果: {results}")
            
            if not results['overall_healthy']:
                print("警告: Web Server集群健康状态异常")
                
            time.sleep(30)
        except Exception as e:
            print(f"健康检查执行失败: {e}")
            time.sleep(5)
```

### 5.3 故障转移和自动恢复
```bash
#!/bin/bash
# webserver_failover.sh
# Web Server故障转移脚本

# 检查Web Server健康状态
check_webserver_health() {
    local url=$1
    local timeout=${2:-5}
    
    curl -s -o /dev/null -w "%{http_code}" --max-time $timeout $url/health
    return $?
}

# 重启故障的Pod
restart_failed_pod() {
    local pod_name=$1
    local namespace=${2:-airflow}
    
    echo "重启故障Pod: $pod_name"
    kubectl delete pod $pod_name -n $namespace
    
    # 等待Pod重新启动
    echo "等待Pod重新启动..."
    kubectl wait --for=condition=ready pod/$pod_name -n $namespace --timeout=300s
}

# 负载均衡器健康检查
check_load_balancer() {
    local lb_service=$1
    local namespace=${2:-airflow}
    
    # 检查Service端点
    endpoints=$(kubectl get endpoints $lb_service -n $namespace -o jsonpath='{.subsets[*].addresses[*].ip}')
    
    if [ -z "$endpoints" ]; then
        echo "负载均衡器没有可用的后端"
        return 1
    fi
    
    echo "负载均衡器后端: $endpoints"
    return 0
}

# 主健康检查循环
main_health_check() {
    local namespace=${1:-airflow}
    local service_name=${2:-airflow-webserver}
    
    # 获取所有Web Server Pod
    pods=$(kubectl get pods -n $namespace -l component=webserver -o jsonpath='{.items[*].metadata.name}')
    
    for pod in $pods; do
        # 获取Pod IP
        pod_ip=$(kubectl get pod $pod -n $namespace -o jsonpath='{.status.podIP}')
        
        if [ -n "$pod_ip" ]; then
            # 检查Pod健康状态
            health_status=$(check_webserver_health "http://$pod_ip:8080")
            
            if [ "$health_status" != "200" ]; then
                echo "检测到故障Pod: $pod (IP: $pod_ip)"
                
                # 记录日志
                kubectl logs $pod -n $namespace --tail=50
                
                # 重启Pod
                restart_failed_pod $pod $namespace
            else
                echo "Pod健康: $pod (IP: $pod_ip)"
            fi
        fi
    done
    
    # 检查负载均衡器
    check_load_balancer $service_name $namespace
}

# 运行健康检查
while true; do
    main_health_check
    sleep 60
done
```

## 6. Scheduler高可用

### 6.1 多Scheduler配置
```yaml
# scheduler-ha.yaml
# 多Scheduler配置

apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-scheduler
spec:
  replicas: 2  # 至少2个副本
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: airflow
      component: scheduler
  template:
    metadata:
      labels:
        app: airflow
        component: scheduler
    spec:
      containers:
        - name: scheduler
          image: company/airflow:1.0.0
          command: ["airflow", "scheduler"]
          env:
            # 启用HA模式
            - name: AIRFLOW__SCHEDULER__USE_ROW_LEVEL_LOCKING
              value: "True"
            - name: AIRFLOW__SCHEDULER__MAX_TIS_PER_QUERY
              value: "16"
            - name: AIRFLOW__SCHEDULER__SCHEDULER_HEARTBEAT_SEC
              value: "5"
            - name: AIRFLOW__SCHEDULER__SCHEDULER_ZOMBIE_TASK_DETECTION
              value: "True"
            - name: AIRFLOW__SCHEDULER__CLEAN_TOMBSTONED_DAG_RUNS
              value: "True"
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              cpu: "1"
              memory: "2Gi"
          livenessProbe:
            exec:
              command:
                - python
                - -c
                - |
                  import requests
                  response = requests.get('http://localhost:8080/health')
                  if response.status_code != 200:
                      exit(1)
            initialDelaySeconds: 60
            periodSeconds: 30
            timeoutSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
```

### 6.2 Scheduler健康监控
```python
# scheduler_monitoring.py
# Scheduler健康监控

import logging
import time
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SchedulerMonitor:
    def __init__(self, scheduler_urls: List[str], database_url: str):
        self.logger = logging.getLogger(__name__)
        self.scheduler_urls = scheduler_urls
        self.database_url = database_url
        
    def check_scheduler_health(self, url: str) -> Dict[str, Any]:
        """检查单个Scheduler健康状态"""
        try:
            # 检查HTTP健康端点
            response = requests.get(f"{url}/health", timeout=5)
            http_healthy = response.status_code == 200
            
            # 检查调度器特定指标
            metrics_response = requests.get(f"{url}/admin/metrics", timeout=5)
            metrics_healthy = metrics_response.status_code == 200
            
            return {
                'url': url,
                'http_healthy': http_healthy,
                'metrics_healthy': metrics_healthy,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Scheduler健康检查失败 {url}: {e}")
            return {
                'url': url,
                'http_healthy': False,
                'metrics_healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def check_dag_processing(self) -> Dict[str, Any]:
        """检查DAG处理状态"""
        try:
            # 这里应该查询数据库获取DAG处理信息
            # 简化实现
            return {
                'dags_processed': 100,
                'processing_delay': 5,  # 秒
                'failed_dags': 2,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"DAG处理检查失败: {e}")
            return {
                'dags_processed': 0,
                'processing_delay': None,
                'failed_dags': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源使用情况"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
        
    def check_database_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        try:
            # 这里应该实际测试数据库连接和查询
            # 简化实现
            return {
                'connection_healthy': True,
                'query_response_time': 0.1,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"数据库健康检查失败: {e}")
            return {
                'connection_healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def perform_comprehensive_check(self) -> Dict[str, Any]:
        """执行全面的健康检查"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'scheduler_checks': [],
            'dag_processing': self.check_dag_processing(),
            'system_resources': self.check_system_resources(),
            'database_health': self.check_database_health()
        }
        
        # 检查每个Scheduler实例
        for url in self.scheduler_urls:
            scheduler_result = self.check_scheduler_health(url)
            results['scheduler_checks'].append(scheduler_result)
            
        # 计算整体健康状态
        healthy_schedulers = sum(1 for check in results['scheduler_checks'] 
                               if check.get('http_healthy', False))
        
        results['overall_healthy'] = (
            healthy_schedulers >= len(self.scheduler_urls) // 2 + 1 and
            results['system_resources']['cpu_percent'] < 80 and
            results['system_resources']['memory_percent'] < 80 and
            results['database_health']['connection_healthy'] and
            results['dag_processing']['processing_delay'] is not None and
            results['dag_processing']['processing_delay'] < 30
        )
        
        return results

# 使用示例
def monitor_schedulers():
    """监控Scheduler"""
    monitor = SchedulerMonitor(
        scheduler_urls=[
            "http://airflow-scheduler-0:8080",
            "http://airflow-scheduler-1:8080"
        ],
        database_url="postgresql://airflow:password@postgres:5432/airflow"
    )
    
    while True:
        try:
            results = monitor.perform_comprehensive_check()
            print(f"Scheduler健康检查结果: {results}")
            
            if not results['overall_healthy']:
                print("警告: Scheduler集群健康状态异常")
                
            time.sleep(60)
        except Exception as e:
            print(f"监控执行失败: {e}")
            time.sleep(10)
```

### 6.3 Scheduler故障恢复
```bash
#!/bin/bash
# scheduler_failover.sh
# Scheduler故障转移脚本

# 检查Scheduler健康状态
check_scheduler_health() {
    local scheduler_pod=$1
    local namespace=${2:-airflow}
    
    # 检查Pod状态
    pod_status=$(kubectl get pod $scheduler_pod -n $namespace -o jsonpath='{.status.phase}')
    
    if [ "$pod_status" != "Running" ]; then
        echo "Scheduler Pod状态异常: $pod_status"
        return 1
    fi
    
    # 检查容器就绪状态
    ready_containers=$(kubectl get pod $scheduler_pod -n $namespace -o jsonpath='{.status.containerStatuses[?(@.ready==true)]}' | wc -l)
    total_containers=$(kubectl get pod $scheduler_pod -n $namespace -o jsonpath='{.spec.containers[*]}' | wc -w)
    
    if [ "$ready_containers" -ne "$total_containers" ]; then
        echo "Scheduler容器未就绪: $ready_containers/$total_containers"
        return 1
    fi
    
    # 检查健康端点
    pod_ip=$(kubectl get pod $scheduler_pod -n $namespace -o jsonpath='{.status.podIP}')
    if [ -n "$pod_ip" ]; then
        health_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://$pod_ip:8080/health)
        if [ "$health_status" != "200" ]; then
            echo "Scheduler健康检查失败: HTTP $health_status"
            return 1
        fi
    fi
    
    echo "Scheduler健康: $scheduler_pod"
    return 0
}

# 重启故障的Scheduler
restart_scheduler() {
    local scheduler_pod=$1
    local namespace=${2:-airflow}
    
    echo "重启故障Scheduler: $scheduler_pod"
    
    # 记录日志
    echo "=== 故障Scheduler日志 ==="
    kubectl logs $scheduler_pod -n $namespace --tail=100
    
    # 重启Pod
    kubectl delete pod $scheduler_pod -n $namespace
    
    # 等待Pod重新启动
    echo "等待Scheduler重新启动..."
    kubectl wait --for=condition=ready pod/$scheduler_pod -n $namespace --timeout=300s
    
    echo "Scheduler重启完成: $scheduler_pod"
}

# 检查Scheduler负载均衡
check_scheduler_load_balancing() {
    local namespace=${1:-airflow}
    
    # 获取所有Scheduler Pod
    pods=$(kubectl get pods -n $namespace -l component=scheduler -o jsonpath='{.items[*].metadata.name}')
    
    echo "=== Scheduler负载情况 ==="
    for pod in $pods; do
        # 获取Pod指标
        cpu_usage=$(kubectl top pod $pod -n $namespace --no-headers | awk '{print $2}')
        memory_usage=$(kubectl top pod $pod -n $namespace --no-headers | awk '{print $3}')
        echo "Pod: $pod, CPU: $cpu_usage, Memory: $memory_usage"
    done
}

# 主监控循环
main_scheduler_monitoring() {
    local namespace=${1:-airflow}
    
    # 获取所有Scheduler Pod
    pods=$(kubectl get pods -n $namespace -l component=scheduler -o jsonpath='{.items[*].metadata.name}')
    
    echo "=== 开始Scheduler健康检查 ==="
    local unhealthy_count=0
    
    for pod in $pods; do
        if ! check_scheduler_health $pod $namespace; then
            echo "检测到不健康的Scheduler: $pod"
            restart_scheduler $pod $namespace
            ((unhealthy_count++))
        fi
    done
    
    echo "=== Scheduler健康检查完成 ==="
    echo "不健康Scheduler数量: $unhealthy_count"
    
    # 检查负载均衡
    check_scheduler_load_balancing $namespace
}

# 运行监控
while true; do
    main_scheduler_monitoring
    sleep 120
done
```

## 7. Worker高可用

### 7.1 Worker自动扩缩容
```yaml
# worker-autoscaling.yaml
# Worker自动扩缩容配置

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airflow-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airflow-worker
  minReplicas: 3
  maxReplicas: 20
  metrics:
    # 基于CPU使用率扩缩容
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
          
    # 基于内存使用率扩缩容
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
          
    # 基于自定义指标扩缩容
    - type: Pods
      pods:
        metric:
          name: airflow_task_queue_length
        target:
          type: AverageValue
          averageValue: "10"
          
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
        - type: Pods
          value: 2
          periodSeconds: 60
      selectPolicy: Min
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
        - type: Pods
          value: 4
          periodSeconds: 60
      selectPolicy: Max

# 垂直Pod自动扩缩容
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: airflow-worker-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: airflow-worker
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
      - containerName: "worker"
        maxAllowed:
          cpu: "4"
          memory: "8Gi"
        minAllowed:
          cpu: "500m"
          memory: "1Gi"
```

### 7.2 Worker健康监控
```python
# worker_monitoring.py
# Worker健康监控

import logging
import time
import psutil
import requests
from datetime import datetime
from typing import Dict, List, Any

class WorkerMonitor:
    def __init__(self, worker_urls: List[str]):
        self.logger = logging.getLogger(__name__)
        self.worker_urls = worker_urls
        
    def check_worker_health(self, url: str) -> Dict[str, Any]:
        """检查单个Worker健康状态"""
        try:
            # 检查HTTP健康端点
            response = requests.get(f"{url}/health", timeout=5)
            http_healthy = response.status_code == 200
            
            # 检查Celery工作状态
            celery_response = requests.get(f"{url}/api/v1/health", timeout=5)
            celery_healthy = celery_response.status_code == 200
            
            return {
                'url': url,
                'http_healthy': http_healthy,
                'celery_healthy': celery_healthy,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Worker健康检查失败 {url}: {e}")
            return {
                'url': url,
                'http_healthy': False,
                'celery_healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def check_task_queue_status(self) -> Dict[str, Any]:
        """检查任务队列状态"""
        try:
            # 这里应该查询消息队列获取任务队列信息
            # 简化实现
            return {
                'queue_length': 50,
                'active_tasks': 20,
                'reserved_tasks': 5,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"任务队列状态检查失败: {e}")
            return {
                'queue_length': None,
                'active_tasks': None,
                'reserved_tasks': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源使用情况"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
        
    def check_worker_performance(self) -> Dict[str, Any]:
        """检查Worker性能指标"""
        try:
            # 这里应该从监控系统获取性能指标
            # 简化实现
            return {
                'task_completion_rate': 100,  # 每分钟完成任务数
                'average_task_duration': 30,  # 秒
                'task_failure_rate': 0.01,    # 1%
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Worker性能检查失败: {e}")
            return {
                'task_completion_rate': None,
                'average_task_duration': None,
                'task_failure_rate': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def perform_comprehensive_check(self) -> Dict[str, Any]:
        """执行全面的健康检查"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'worker_checks': [],
            'queue_status': self.check_task_queue_status(),
            'system_resources': self.check_system_resources(),
            'performance_metrics': self.check_worker_performance()
        }
        
        # 检查每个Worker实例
        for url in self.worker_urls:
            worker_result = self.check_worker_health(url)
            results['worker_checks'].append(worker_result)
            
        # 计算整体健康状态
        healthy_workers = sum(1 for check in results['worker_checks'] 
                            if check.get('http_healthy', False) and 
                               check.get('celery_healthy', False))
        
        results['overall_healthy'] = (
            healthy_workers >= len(self.worker_urls) * 0.8 and  # 80%以上健康
            results['system_resources']['cpu_percent'] < 85 and
            results['system_resources']['memory_percent'] < 85 and
            results['queue_status']['queue_length'] is not None and
            results['queue_status']['queue_length'] < 1000 and  # 队列长度限制
            results['performance_metrics']['task_failure_rate'] is not None and
            results['performance_metrics']['task_failure_rate'] < 0.05  # 失败率限制
        )
        
        return results

# 使用示例
def monitor_workers():
    """监控Worker"""
    monitor = WorkerMonitor([
        "http://airflow-worker-0:8080",
        "http://airflow-worker-1:8080",
        "http://airflow-worker-2:8080"
    ])
    
    while True:
        try:
            results = monitor.perform_comprehensive_check()
            print(f"Worker健康检查结果: {results}")
            
            if not results['overall_healthy']:
                print("警告: Worker集群健康状态异常")
                
            time.sleep(60)
        except Exception as e:
            print(f"监控执行失败: {e}")
            time.sleep(10)
```

### 7.3 Worker故障恢复
```bash
#!/bin/bash
# worker_failover.sh
# Worker故障转移脚本

# 检查Worker健康状态
check_worker_health() {
    local worker_pod=$1
    local namespace=${2:-airflow}
    
    # 检查Pod状态
    pod_status=$(kubectl get pod $worker_pod -n $namespace -o jsonpath='{.status.phase}')
    
    if [ "$pod_status" != "Running" ]; then
        echo "Worker Pod状态异常: $pod_status"
        return 1
    fi
    
    # 检查容器就绪状态
    ready_containers=$(kubectl get pod $worker_pod -n $namespace -o jsonpath='{.status.containerStatuses[?(@.ready==true)]}' | wc -l)
    total_containers=$(kubectl get pod $worker_pod -n $namespace -o jsonpath='{.spec.containers[*]}' | wc -w)
    
    if [ "$ready_containers" -ne "$total_containers" ]; then
        echo "Worker容器未就绪: $ready_containers/$total_containers"
        return 1
    fi
    
    # 检查健康端点
    pod_ip=$(kubectl get pod $worker_pod -n $namespace -o jsonpath='{.status.podIP}')
    if [ -n "$pod_ip" ]; then
        health_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://$pod_ip:8080/health)
        if [ "$health_status" != "200" ]; then
            echo "Worker健康检查失败: HTTP $health_status"
            return 1
        fi
    fi
    
    echo "Worker健康: $worker_pod"
    return 0
}

# 重启故障的Worker
restart_worker() {
    local worker_pod=$1
    local namespace=${2:-airflow}
    
    echo "重启故障Worker: $worker_pod"
    
    # 记录日志
    echo "=== 故障Worker日志 ==="
    kubectl logs $worker_pod -n $namespace --tail=100
    
    # 重启Pod
    kubectl delete pod $worker_pod -n $namespace
    
    # 等待Pod重新启动
    echo "等待Worker重新启动..."
    kubectl wait --for=condition=ready pod/$worker_pod -n $namespace --timeout=300s
    
    echo "Worker重启完成: $worker_pod"
}

# 检查Worker负载均衡
check_worker_load_balancing() {
    local namespace=${1:-airflow}
    
    # 获取所有Worker Pod
    pods=$(kubectl get pods -n $namespace -l component=worker -o jsonpath='{.items[*].metadata.name}')
    
    echo "=== Worker负载情况 ==="
    local total_queue_length=0
    local worker_count=0
    
    for pod in $pods; do
        # 获取Pod指标
        cpu_usage=$(kubectl top pod $pod -n $namespace --no-headers | awk '{print $2}')
        memory_usage=$(kubectl top pod $pod -n $namespace --no-headers | awk '{print $3}')
        
        # 模拟获取队列长度（实际应从监控系统获取）
        queue_length=$((RANDOM % 100))
        total_queue_length=$((total_queue_length + queue_length))
        worker_count=$((worker_count + 1))
        
        echo "Pod: $pod, CPU: $cpu_usage, Memory: $memory_usage, Queue: $queue_length"
    done
    
    if [ $worker_count -gt 0 ]; then
        avg_queue_length=$((total_queue_length / worker_count))
        echo "平均队列长度: $avg_queue_length"
        
        # 如果平均队列长度过高，可能需要扩容
        if [ $avg_queue_length -gt 50 ]; then
            echo "警告: 平均队列长度过高，考虑扩容Worker"
        fi
    fi
}

# 主监控循环
main_worker_monitoring() {
    local namespace=${1:-airflow}
    
    # 获取所有Worker Pod
    pods=$(kubectl get pods -n $namespace -l component=worker -o jsonpath='{.items[*].metadata.name}')
    
    echo "=== 开始Worker健康检查 ==="
    local unhealthy_count=0
    
    for pod in $pods; do
        if ! check_worker_health $pod $namespace; then
            echo "检测到不健康的Worker: $pod"
            restart_worker $pod $namespace
            ((unhealthy_count++))
        fi
    done
    
    echo "=== Worker健康检查完成 ==="
    echo "不健康Worker数量: $unhealthy_count"
    
    # 检查负载均衡
    check_worker_load_balancing $namespace
}

# 运行监控
while true; do
    main_worker_monitoring
    sleep 120
done
```

## 8. 存储高可用

### 8.1 共享存储配置
```yaml
# shared-storage.yaml
# 共享存储配置

# NFS存储类
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-shared-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer

# NFS持久卷
apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-dags-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs-shared-storage
  nfs:
    server: nfs-server.company.com
    path: "/exports/airflow/dags"
  mountOptions:
    - vers=4.1
    - rsize=1048576
    - wsize=1048576
    - hard
    - timeo=600
    - retrans=2

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-logs-pv
spec:
  capacity:
    storage: 200Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs-shared-storage
  nfs:
    server: nfs-server.company.com
    path: "/exports/airflow/logs"

# 持久卷声明
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: airflow-dags-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: nfs-shared-storage

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: airflow-logs-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 200Gi
  storageClassName: nfs-shared-storage
```

### 8.2 存储备份策略
```bash
#!/bin/bash
# storage_backup.sh
# 存储备份脚本

# 备份DAGs
backup_dags() {
    local backup_dir="/backups/dags"
    local source_dir="/shared/dags"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    echo "开始备份DAGs..."
    
    # 创建备份目录
    mkdir -p $backup_dir/$timestamp
    
    # 备份DAGs
    rsync -av --delete $source_dir/ $backup_dir/$timestamp/
    
    # 压缩备份
    tar -czf $backup_dir/dags_$timestamp.tar.gz -C $backup_dir $timestamp
    
    # 删除临时目录
    rm -rf $backup_dir/$timestamp
    
    # 上传到对象存储
    aws s3 cp $backup_dir/dags_$timestamp.tar.gz s3://company-backups/airflow/dags/
    
    # 清理旧备份（保留7天）
    find $backup_dir -name "dags_*.tar.gz" -mtime +7 -delete
    
    echo "DAGs备份完成"
}

# 备份日志
backup_logs() {
    local backup_dir="/backups/logs"
    local source_dir="/shared/logs"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    echo "开始备份日志..."
    
    # 创建备份目录
    mkdir -p $backup_dir/$timestamp
    
    # 备份日志（只备份最近7天）
    find $source_dir -type f -mtime -7 -exec cp --parents {} $backup_dir/$timestamp/ \;
    
    # 压缩备份
    tar -czf $backup_dir/logs_$timestamp.tar.gz -C $backup_dir $timestamp
    
    # 删除临时目录
    rm -rf $backup_dir/$timestamp
    
    # 上传到对象存储
    aws s3 cp $backup_dir/logs_$timestamp.tar.gz s3://company-backups/airflow/logs/
    
    # 清理旧备份（保留30天）
    find $backup_dir -name "logs_*.tar.gz" -mtime +30 -delete
    
    echo "日志备份完成"
}

# 验证备份
verify_backup() {
    local backup_file=$1
    
    echo "验证备份文件: $backup_file"
    
    # 检查文件完整性
    if [ -f "$backup_file" ]; then
        file_size=$(stat -c%s "$backup_file")
        if [ $file_size -gt 0 ]; then
            echo "备份文件完整: $backup_file (大小: $file_size bytes)"
            return 0
        else
            echo "备份文件为空: $backup_file"
            return 1
        fi
    else
        echo "备份文件不存在: $backup_file"
        return 1
    fi
}

# 恢复DAGs
restore_dags() {
    local backup_file=$1
    local restore_dir="/shared/dags"
    
    echo "开始恢复DAGs..."
    
    # 下载备份文件
    aws s3 cp s3://company-backups/airflow/dags/$backup_file /tmp/
    
    # 验证备份
    if ! verify_backup "/tmp/$backup_file"; then
        echo "备份文件验证失败"
        return 1
    fi
    
    # 解压备份
    mkdir -p /tmp/dags_restore
    tar -xzf /tmp/$backup_file -C /tmp/dags_restore
    
    # 恢复DAGs
    rsync -av --delete /tmp/dags_restore/*/ $restore_dir/
    
    # 清理临时文件
    rm -rf /tmp/dags_restore /tmp/$backup_file
    
    # 重新加载DAGs
    airflow dags reserialize
    
    echo "DAGs恢复完成"
}

# 主备份函数
main_backup() {
    echo "=== 开始存储备份 ==="
    local start_time=$(date)
    
    # 备份DAGs
    backup_dags
    
    # 备份日志
    backup_logs
    
    local end_time=$(date)
    echo "=== 存储备份完成 ==="
    echo "开始时间: $start_time"
    echo "结束时间: $end_time"
}

# 定期备份
while true; do
    main_backup
    sleep 86400  # 每天执行一次
done
```

### 8.3 存储监控和告警
```python
# storage_monitoring.py
# 存储监控

import logging
import time
import os
import shutil
from datetime import datetime
from typing import Dict, Any

class StorageMonitor:
    def __init__(self, storage_paths: Dict[str, str]):
        self.logger = logging.getLogger(__name__)
        self.storage_paths = storage_paths
        
    def check_storage_usage(self, path: str) -> Dict[str, Any]:
        """检查存储使用情况"""
        try:
            total, used, free = shutil.disk_usage(path)
            usage_percent = (used / total) * 100
            
            return {
                'path': path,
                'total_bytes': total,
                'used_bytes': used,
                'free_bytes': free,
                'usage_percent': usage_percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"存储使用情况检查失败 {path}: {e}")
            return {
                'path': path,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def check_file_integrity(self, path: str, file_patterns: list) -> Dict[str, Any]:
        """检查文件完整性"""
        try:
            file_count = 0
            total_size = 0
            
            for root, dirs, files in os.walk(path):
                for file in files:
                    # 检查文件模式匹配
                    if any(pattern in file for pattern in file_patterns):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            file_count += 1
                            total_size += file_size
                        except OSError as e:
                            self.logger.warning(f"无法获取文件大小 {file_path}: {e}")
                            
            return {
                'path': path,
                'file_count': file_count,
                'total_size': total_size,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"文件完整性检查失败 {path}: {e}")
            return {
                'path': path,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def check_nfs_connectivity(self, nfs_server: str, nfs_path: str) -> Dict[str, Any]:
        """检查NFS连接性"""
        try:
            # 这里应该实际测试NFS连接
            # 简化实现
            return {
                'server': nfs_server,
                'path': nfs_path,
                'connected': True,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"NFS连接性检查失败 {nfs_server}:{nfs_path}: {e}")
            return {
                'server': nfs_server,
                'path': nfs_path,
                'connected': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def perform_storage_check(self) -> Dict[str, Any]:
        """执行存储检查"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'storage_usage': [],
            'file_integrity': [],
            'nfs_connectivity': []
        }
        
        # 检查存储使用情况
        for name, path in self.storage_paths.items():
            usage_result = self.check_storage_usage(path)
            results['storage_usage'].append(usage_result)
            
            # 检查文件完整性（针对特定路径）
            if 'dags' in name.lower():
                integrity_result = self.check_file_integrity(path, ['.py', '.sql'])
                results['file_integrity'].append(integrity_result)
            elif 'logs' in name.lower():
                integrity_result = self.check_file_integrity(path, ['.log'])
                results['file_integrity'].append(integrity_result)
                
        # 检查NFS连接性（假设配置在环境变量中）
        nfs_server = os.getenv('NFS_SERVER', 'nfs-server.company.com')
        for name, path in self.storage_paths.items():
            if 'nfs' in path.lower():
                nfs_result = self.check_nfs_connectivity(nfs_server, path)
                results['nfs_connectivity'].append(nfs_result)
                
        # 计算整体健康状态
        critical_usage = sum(1 for usage in results['storage_usage'] 
                           if usage.get('usage_percent', 0) > 90)
        
        results['overall_healthy'] = (
            critical_usage == 0 and
            all(conn.get('connected', False) for conn in results['nfs_connectivity'])
        )
        
        return results

# 使用示例
def monitor_storage():
    """监控存储"""
    monitor = StorageMonitor({
        'dags': '/shared/dags',
        'logs': '/shared/logs',
        'nfs_dags': '/nfs/dags',
        'nfs_logs': '/nfs/logs'
    })
    
    while True:
        try:
            results = monitor.perform_storage_check()
            print(f"存储检查结果: {results}")
            
            # 检查告警条件
            for usage in results['storage_usage']:
                if usage.get('usage_percent', 0) > 80:
                    print(f"警告: 存储使用率过高 {usage['path']}: {usage['usage_percent']:.2f}%")
                    
            if not results['overall_healthy']:
                print("警告: 存储系统健康状态异常")
                
            time.sleep(300)  # 每5分钟检查一次
        except Exception as e:
            print(f"存储监控执行失败: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_storage()
```

## 9. 监控和告警系统

### 9.1 Prometheus监控配置
```yaml
# prometheus-monitoring.yaml
# Prometheus监控配置

# ServiceMonitor配置
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: airflow-monitor
  labels:
    app: airflow
spec:
  selector:
    matchLabels:
      app: airflow
  endpoints:
    - port: metrics
      interval: 30s
      path: /admin/metrics
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_name]
          targetLabel: pod
        - sourceLabels: [__meta_kubernetes_pod_node_name]
          targetLabel: node
          
# PrometheusRule配置
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: airflow-alerts
  labels:
    app: airflow
spec:
  groups:
    - name: airflow.rules
      rules:
        # Web Server健康检查
        - alert: AirflowWebServerDown
          expr: absent(up{job="airflow-webserver"} == 1)
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "Airflow Web Server is down"
            description: "Airflow Web Server has disappeared from Prometheus target discovery."
            
        # Scheduler健康检查
        - alert: AirflowSchedulerDown
          expr: absent(up{job="airflow-scheduler"} == 1)
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "Airflow Scheduler is down"
            description: "Airflow Scheduler has disappeared from Prometheus target discovery."
            
        # Worker健康检查
        - alert: AirflowWorkerDown
          expr: absent(up{job="airflow-worker"} == 1)
          for: 2m
          labels:
            severity: warning
          annotations:
            summary: "Airflow Worker is down"
            description: "Airflow Worker has disappeared from Prometheus target discovery."
            
        # 数据库连接问题
        - alert: AirflowDatabaseConnectionFailed
          expr: airflow_database_connection_failures > 5
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Airflow database connection failures"
            description: "Airflow is experiencing database connection failures."
            
        # DAG执行延迟
        - alert: AirflowDagExecutionDelay
          expr: airflow_dag_run_duration > 3600
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "Airflow DAG execution delay"
            description: "DAG execution duration exceeds 1 hour."
            
        # 任务失败率过高
        - alert: AirflowTaskFailureRateHigh
          expr: rate(airflow_task_failures[5m]) > 0.1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Airflow task failure rate is high"
            description: "Task failure rate exceeds 10% in the last 5 minutes."
            
        # 存储使用率过高
        - alert: AirflowStorageUsageHigh
          expr: kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes * 100 > 85
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Airflow storage usage is high"
            description: "Storage usage exceeds 85%."
```

### 9.2 Grafana仪表板配置
```json
{
  "dashboard": {
    "id": null,
    "title": "Airflow High Availability Dashboard",
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 0,
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "type": "graph",
        "title": "Web Server Health",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "up{job=\"airflow-webserver\"}",
            "legendFormat": "{{pod}}"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {
                "params": [1],
                "type": "lt"
              },
              "operator": {
                "type": "and"
              },
              "query": {
                "params": ["A", "5m", "now"]
              },
              "reducer": {
                "params": [],
                "type": "avg"
              },
              "type": "query"
            }
          ],
          "executionErrorState": "alerting",
          "frequency": "60s",
          "handler": 1,
          "name": "Web Server Down alert",
          "noDataState": "no_data",
          "notifications": [
            {
              "uid": "alertmanager"
            }
          ]
        }
      },
      {
        "id": 2,
        "type": "graph",
        "title": "Scheduler Health",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "up{job=\"airflow-scheduler\"}",
            "legendFormat": "{{pod}}"
          }
        ]
      },
      {
        "id": 3,
        "type": "graph",
        "title": "Worker Health",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "up{job=\"airflow-worker\"}",
            "legendFormat": "{{pod}}"
          }
        ]
      },
      {
        "id": 4,
        "type": "graph",
        "title": "Database Connection Pool",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "airflow_database_connections_used",
            "legendFormat": "Used Connections"
          },
          {
            "expr": "airflow_database_connections_available",
            "legendFormat": "Available Connections"
          }
        ]
      },
      {
        "id": 5,
        "type": "graph",
        "title": "Task Execution Rate",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(airflow_task_successes[5m])",
            "legendFormat": "Success Rate"
          },
          {
            "expr": "rate(airflow_task_failures[5m])",
            "legendFormat": "Failure Rate"
          }
        ]
      },
      {
        "id": 6,
        "type": "graph",
        "title": "Storage Usage",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes * 100",
            "legendFormat": "{{persistentvolumeclaim}}"
          }
        ]
      }
    ]
  }
}
```

### 9.3 告警通知配置
```yaml
# alertmanager-config.yaml
# Alertmanager配置

global:
  smtp_smarthost: 'smtp.company.com:587'
  smtp_from: 'alertmanager@company.com'
  smtp_auth_username: 'alertmanager'
  smtp_auth_password: 'password'
  
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team-airflow'
  
receivers:
  - name: 'team-airflow'
    email_configs:
      - to: 'airflow-team@company.com'
        send_resolved: true
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
        channel: '#airflow-alerts'
        send_resolved: true
        title: '{{ template "slack.airflow.title" . }}'
        text: '{{ template "slack.airflow.text" . }}'
    webhook_configs:
      - url: 'https://webhook.company.com/airflow-alerts'
        send_resolved: true
        
templates:
  - '/etc/alertmanager/template/*.tmpl'
```

## 10. 故障排除和恢复

### 10.1 常见故障诊断
```bash
#!/bin/bash
# troubleshooting.sh
# 故障排除脚本

# 检查集群整体状态
check_cluster_status() {
    echo "=== 集群整体状态 ==="
    kubectl get nodes -o wide
    kubectl get pods -n airflow -o wide
    kubectl get services -n airflow
    kubectl get ingress -n airflow
}

# 检查Web Server状态
check_webserver_status() {
    echo "=== Web Server状态 ==="
    kubectl get pods -n airflow -l component=webserver
    kubectl get svc airflow-webserver -n airflow
    kubectl describe svc airflow-webserver -n airflow
}

# 检查Scheduler状态
check_scheduler_status() {
    echo "=== Scheduler状态 ==="
    kubectl get pods -n airflow -l component=scheduler
    kubectl logs -n airflow -l component=scheduler --tail=100
}

# 检查Worker状态
check_worker_status() {
    echo "=== Worker状态 ==="
    kubectl get pods -n airflow -l component=worker
    kubectl logs -n airflow -l component=worker --tail=50
}

# 检查数据库状态
check_database_status() {
    echo "=== 数据库状态 ==="
    kubectl get pods -n airflow -l app=postgresql
    kubectl logs -n airflow -l app=postgresql --tail=50
}

# 检查存储状态
check_storage_status() {
    echo "=== 存储状态 ==="
    kubectl get pv
    kubectl get pvc -n airflow
    kubectl describe pvc airflow-dags-pvc -n airflow
    kubectl describe pvc airflow-logs-pvc -n airflow
}

# 检查网络连接
check_network_connectivity() {
    echo "=== 网络连接检查 ==="
    
    # 检查Pod间连接
    webserver_pod=$(kubectl get pods -n airflow -l component=webserver -o jsonpath='{.items[0].metadata.name}')
    scheduler_pod=$(kubectl get pods -n airflow -l component=scheduler -o jsonpath='{.items[0].metadata.name}')
    
    echo "从Web Server