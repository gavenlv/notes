# 第3章：RabbitMQ高级特性详解

## 📚 章节概述

RabbitMQ作为企业级消息队列解决方案，不仅提供了基础的消息传递功能，还具备许多强大的高级特性。这些特性使得RabbitMQ能够应对复杂的业务场景，提供可靠、高效、可扩展的消息处理能力。

本章节将深入探讨RabbitMQ的核心高级特性，包括消息确认机制、持久化策略、死信队列、消息TTL、优先级队列、集群配置等，帮助您构建健壮的企业级消息系统。

## 🔄 消息确认机制

### 1. 确认机制概述

消息确认是确保消息可靠传递的关键机制。RabbitMQ提供了多种确认方式：

#### 1.1 生产者确认（Publisher Confirms）

生产者确认确保消息成功到达RabbitMQ服务器：

```python
import pika

# 启用发布者确认
channel.confirm_delivery()

# 发送消息 - 如果确认失败会抛出异常
channel.basic_publish(
    exchange='amq.direct',
    routing_key='test.queue',
    body='Hello World!'
)
```

#### 1.2 消费者确认（Consumer Acknowledgments）

消费者确认确保消息被正确处理：

```python
def callback(ch, method, properties, body):
    try:
        # 处理消息
        process_message(body)
        # 手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # 确认拒绝消息，可能重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

#### 1.3 事务机制

提供类似数据库事务的保证：

```python
# 开始事务
channel.tx_select()

try:
    # 发送消息
    channel.basic_publish(...)
    # 提交事务
    channel.tx_commit()
except:
    # 回滚事务
    channel.tx_rollback()
```

### 2. 确认模式详解

#### 2.1 自动确认模式
```python
# 自动确认 - 消息一旦发送给消费者就确认
channel.basic_consume(queue='test_queue', on_message_callback=callback)
```

**特点**：
- 吞吐量高
- 不保证消息处理
- 可能导致消息丢失

#### 2.2 手动确认模式
```python
# 手动确认
channel.basic_consume(
    queue='test_queue',
    on_message_callback=callback,
    auto_ack=False
)

def callback(ch, method, properties, body):
    # 处理消息
    process_message(body)
    # 手动确认
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

**优点**：
- 可靠的消息传递
- 支持失败重试
- 精确的流控制

#### 2.3 预取数量控制

```python
# 设置预取数量为1，确保一次只处理一条消息
channel.basic_qos(prefetch_count=1)

# 预取多条消息，提高吞吐量
channel.basic_qos(prefetch_count=10)
```

## 💾 消息持久化

### 1. 持久化策略

#### 1.1 交换机持久化
```python
channel.exchange_declare(
    exchange='durable_exchange',
    exchange_type='direct',
    durable=True  # 交换机持久化
)
```

#### 1.2 队列持久化
```python
channel.queue_declare(
    queue='durable_queue',
    durable=True  # 队列持久化
)
```

#### 1.3 消息持久化
```python
channel.basic_publish(
    exchange='amq.direct',
    routing_key='test.queue',
    body='Persistent message',
    properties=pika.BasicProperties(
        delivery_mode=2,  # 消息持久化 (1=非持久, 2=持久)
        priority=1,       # 消息优先级
        message_id='msg_001',
        correlation_id='cor_001',
        reply_to='reply_queue',
        expiration='60000',  # 消息TTL (毫秒)
        timestamp=datetime.now(),
        type='event',
        user_id='user',
        app_id='app_001'
    )
)
```

### 2. 持久化原理

#### 2.1 写入策略
- **队列镜像**：消息复制到集群多个节点
- **队列落盘**：消息持久化到磁盘
- **确认机制**：确保消息成功落盘

#### 2.2 性能影响
- **内存存储**：快速但可能丢失
- **磁盘存储**：可靠但速度较慢
- **混合策略**：根据消息重要性选择

## ⚰️ 死信队列（Dead Letter Queue）

### 1. 死信队列概述

死信队列用于处理无法正常处理的消息，避免消息丢失。

### 2. 死信队列配置

#### 2.1 声明死信交换机
```python
# 声明死信交换机
channel.exchange_declare(
    exchange='dlx_exchange',
    exchange_type='direct',
    durable=True
)

# 声明死信队列
channel.queue_declare(
    queue='dead_letter_queue',
    durable=True
)

# 绑定死信交换机到死信队列
channel.queue_bind(
    exchange='dlx_exchange',
    queue='dead_letter_queue',
    routing_key='dead_letter'
)
```

#### 2.2 配置主队列的死信属性
```python
channel.queue_declare(
    queue='main_queue',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx_exchange',  # 死信交换机
        'x-dead-letter-routing-key': 'dead_letter',  # 死信路由键
        'x-message-ttl': 30000,  # 消息TTL (30秒)
        'x-max-priority': 10  # 最大优先级
    }
)
```

### 3. 死信触发条件

#### 3.1 消息被拒绝且不重新入队
```python
def callback(ch, method, properties, body):
    try:
        # 处理消息失败
        if not process_message(body):
            # 拒绝消息但不重新入队
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        # 拒绝消息并重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

#### 3.2 消息过期
```python
# 设置消息过期时间
properties = pika.BasicProperties(
    expiration='10000'  # 10秒后过期
)

channel.basic_publish(
    exchange='amq.direct',
    routing_key='main_queue',
    body='Message with TTL',
    properties=properties
)
```

#### 3.3 队列达到最大长度
```python
# 声明有最大长度限制的队列
channel.queue_declare(
    queue='limited_queue',
    durable=True,
    arguments={
        'x-max-length': 100,  # 最大队列长度
        'x-dead-letter-exchange': 'dlx_exchange'
    }
)
```

## ⏰ 消息TTL（Time To Live）

### 1. TTL类型

#### 1.1 队列级TTL
```python
# 为队列中的所有消息设置TTL
channel.queue_declare(
    queue='ttl_queue',
    arguments={
        'x-message-ttl': 60000  # 60秒
    }
)
```

#### 1.2 消息级TTL
```python
# 为单个消息设置TTL
properties = pika.BasicProperties(
    expiration='30000'  # 30秒
)

channel.basic_publish(
    exchange='amq.direct',
    routing_key='ttl_queue',
    body='Message with individual TTL',
    properties=properties
)
```

### 2. TTL处理机制

#### 2.1 TTL检查
- **队列检查**：定期检查队列中的过期消息
- **优先级处理**：按照优先级顺序检查
- **精确时间**：使用Unix时间戳精确计算

#### 2.2 TTL过期处理
- **转入死信队列**：过期消息自动转入DLQ
- **立即删除**：没有死信队列配置的队列直接删除
- **批量清理**：批量处理过期消息提高性能

## 🎯 优先级队列

### 1. 优先级队列配置

```python
# 声明最大优先级为10的队列
channel.queue_declare(
    queue='priority_queue',
    durable=True,
    arguments={
        'x-max-priority': 10  # 最大优先级
    }
)
```

### 2. 发送优先级消息

```python
# 发送高优先级消息
properties = pika.BasicProperties(
    priority=9  # 高优先级
)

channel.basic_publish(
    exchange='amq.direct',
    routing_key='priority_queue',
    body='High priority message',
    properties=properties
)

# 发送普通优先级消息
properties = pika.BasicProperties(
    priority=1  # 普通优先级
)

channel.basic_publish(
    exchange='amq.direct',
    routing_key='priority_queue',
    body='Normal priority message',
    properties=properties
)
```

### 3. 优先级处理机制

#### 3.1 队列内部结构
- **优先级堆**：使用堆数据结构维护优先级
- **多队列**：不同优先级的消息存储在不同的虚拟队列中
- **智能调度**：优先处理高优先级消息

#### 3.2 消费顺序
1. 高优先级消息优先消费
2. 同优先级消息按FIFO顺序消费
3. 确保消息处理顺序的相对稳定性

## 🔒 消息属性详解

### 1. 基本属性

```python
properties = pika.BasicProperties(
    delivery_mode=2,        # 消息持久化 (1=非持久, 2=持久)
    priority=5,             # 消息优先级 (0-255)
    message_id='unique_id', # 消息唯一标识
    correlation_id='corr_123', # 关联ID，用于请求/响应
    reply_to='reply_queue', # 回复队列名称
    timestamp=datetime.now(), # 消息时间戳
    type='event_type',      # 消息类型
    user_id='user123',      # 用户ID
    app_id='app_456'        # 应用ID
)
```

### 2. 消息属性应用场景

#### 2.1 请求/响应模式
```python
# 发送请求
def send_request(message, correlation_id):
    properties = pika.BasicProperties(
        reply_to='response_queue',
        correlation_id=correlation_id
    )
    channel.basic_publish(
        exchange='request_exchange',
        routing_key='request_routing_key',
        body=message,
        properties=properties
    )

# 处理响应
def handle_response(ch, method, properties, body):
    correlation_id = properties.correlation_id
    response_queue = properties.reply_to
    # 处理响应数据...
```

#### 2.2 消息追踪
```python
properties = pika.BasicProperties(
    message_id=f"msg_{uuid.uuid4()}",
    timestamp=datetime.now(),
    user_id='user_service',
    app_id='order_service',
    type='order_created'
)
```

## 🌐 RabbitMQ集群配置

### 1. 集群基础架构

#### 1.1 节点类型
- **磁盘节点**：持久化存储，性能较慢
- **内存节点**：仅内存存储，性能较快，重启后数据丢失

#### 1.2 集群配置
```bash
# 停止RabbitMQ服务
sudo systemctl stop rabbitmq-server

# 复制Erlang Cookie
sudo cp /var/lib/rabbitmq/.erlang.cookie /home/user/.erlang.cookie
sudo chmod 400 /home/user/.erlang.cookie
sudo chown user:user /home/user/.erlang.cookie

# 重启RabbitMQ服务
sudo systemctl start rabbitmq-server

# 加入集群
sudo rabbitmqctl stop_app
sudo rabbitmqctl join_cluster rabbit@node2
sudo rabbitmqctl start_app
```

### 2. 高可用配置

#### 2.1 队列镜像
```python
# 声明镜像队列
channel.queue_declare(
    queue='mirrored_queue',
    durable=True,
    arguments={
        'x-ha-policy': 'all'  # 所有节点镜像
    }
)

# 或者指定特定节点镜像
channel.queue_declare(
    queue='mirrored_queue',
    durable=True,
    arguments={
        'x-ha-policy': 'nodes',
        'x-ha-nodes': ['rabbit@node1', 'rabbit@node2']
    }
)
```

#### 2.2 负载均衡
```bash
# 安装负载均衡器
sudo apt install haproxy

# 配置HAProxy
# /etc/haproxy/haproxy.cfg
frontend rabbitmq_front
    bind *:5672
    default_backend rabbitmq_backend

backend rabbitmq_backend
    balance roundrobin
    server rabbit1 rabbit@node1:5672 check
    server rabbit2 rabbit@node2:5672 check
    server rabbit3 rabbit@node3:5672 check
```

### 3. 集群管理

#### 3.1 集群状态监控
```python
# 使用management API监控集群
import requests

def get_cluster_status():
    url = 'http://localhost:15672/api/cluster-name'
    auth = ('guest', 'guest')
    
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    return None
```

#### 3.2 节点管理
```bash
# 查看集群状态
sudo rabbitmqctl cluster_status

# 移除节点
sudo rabbitmqctl forget_cluster_node rabbit@node_to_remove

# 设置节点类型
sudo rabbitmqctl set_policy ha-mirror "^ha\." '{"ha-mode":"all"}'
```

## 🔄 消息幂等性

### 1. 幂等性设计

#### 1.1 消息去重
```python
import hashlib

class IdempotentMessageHandler:
    def __init__(self):
        self.processed_messages = set()
        self.ttl = 3600  # 1小时
    
    def process_message(self, message_id, message_body):
        # 检查消息是否已经处理过
        if message_id in self.processed_messages:
            print(f"消息 {message_id} 已经处理过，跳过")
            return
        
        # 记录消息ID
        self.processed_messages.add(message_id)
        
        # 处理消息
        self._execute_logic(message_body)
        
        # 清理过期消息ID（简化实现）
        if len(self.processed_messages) > 10000:
            self.processed_messages.clear()
```

#### 1.2 状态检查
```python
class OrderProcessor:
    def process_order_created(self, order_data):
        order_id = order_data['order_id']
        
        # 检查订单是否已经处理过
        if self.is_order_processed(order_id):
            print(f"订单 {order_id} 已经处理过")
            return
        
        # 检查订单状态
        current_status = self.get_order_status(order_id)
        if current_status != 'created':
            print(f"订单状态不匹配: {current_status}")
            return
        
        # 处理订单
        self.update_order_status(order_id, 'processing')
        self._create_inventory_reservation(order_id)
        self._send_confirmation_email(order_id)
        self.update_order_status(order_id, 'processed')
    
    def is_order_processed(self, order_id):
        # 查询数据库或缓存
        return self.db.order_status.get(order_id) == 'processed'
    
    def get_order_status(self, order_id):
        return self.db.order_status.get(order_id, 'unknown')
```

### 2. 分布式锁机制

#### 2.1 基于Redis的分布式锁
```python
import redis
import uuid

class DistributedLock:
    def __init__(self, redis_client, key, expire_time=30):
        self.redis_client = redis_client
        self.key = key
        self.expire_time = expire_time
        self.token = None
    
    def acquire(self, timeout=10):
        """尝试获取锁"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self.token = str(uuid.uuid4())
            
            result = self.redis_client.set(
                self.key, 
                self.token, 
                nx=True, 
                ex=self.expire_time
            )
            
            if result:
                return True
            
            time.sleep(0.1)
        
        return False
    
    def release(self):
        """释放锁"""
        if self.token:
            script = '''
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            '''
            self.redis_client.eval(script, 1, self.key, self.token)

# 使用示例
def process_message_with_lock(message_data):
    lock = DistributedLock(
        redis_client=redis.Redis(),
        key=f"message_lock:{message_data['id']}"
    )
    
    if lock.acquire(timeout=5):
        try:
            # 处理消息
            process_message(message_data)
        finally:
            lock.release()
    else:
        print("无法获取锁，消息已被其他节点处理")
```

## 🔐 安全配置

### 1. 用户认证

#### 1.1 创建用户和权限
```bash
# 创建用户
sudo rabbitmqctl add_user admin admin123

# 设置用户标签
sudo rabbitmqctl set_user_tags admin administrator

# 设置权限
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

# 删除用户
sudo rabbitmqctl delete_user username
```

#### 1.2 SSL/TLS配置
```bash
# 生成SSL证书
sudo mkdir /etc/rabbitmq/ssl
cd /etc/rabbitmq/ssl

# 生成CA证书
openssl genrsa -out ca-key.pem 2048
openssl req -new -x509 -days 1000 -key ca-key.pem -out ca-cert.pem -subj "/C=US/ST=CA/L=San Francisco/O=MyOrg/OU=MyUnit/CN=my-ca"

# 生成服务器证书
openssl genrsa -out server-key.pem 2048
openssl req -new -key server-key.pem -out server-req.pem -subj "/C=US/ST=CA/L=San Francisco/O=MyOrg/OU=MyUnit/CN=localhost"
openssl x509 -req -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 1000
```

### 2. 网络安全

#### 2.1 防火墙配置
```bash
# 允许特定IP访问
sudo ufw allow from 192.168.1.0/24 to any port 5672
sudo ufw allow from 192.168.1.0/24 to any port 15672

# 阻止外部访问管理界面
sudo ufw deny 15672
```

#### 2.2 网络隔离
```bash
# RabbitMQ配置文件
# /etc/rabbitmq/rabbitmq.conf
listeners.tcp.default = 5672
loopback_users.guest = false
default_permissions.configure = (.*)
default_permissions.read = (.*)
default_permissions.write = (.*)
```

## 📊 监控与运维

### 1. 性能监控

#### 1.1 关键指标
- **队列深度**：队列中未确认的消息数量
- **消息速率**：每秒处理的消息数
- **内存使用**：RabbitMQ进程内存占用
- **磁盘使用**：持久化存储占用
- **连接数量**：活跃的客户端连接数
- **通道数量**：活跃的AMQP通道数

#### 1.2 Prometheus监控
```python
from prometheus_client import Gauge, Counter, Histogram

# 定义监控指标
QUEUE_LENGTH = Gauge('rabbitmq_queue_length', 'Queue length', ['queue_name'])
MESSAGE_RATE = Counter('rabbitmq_message_rate', 'Messages processed per second', ['queue_name'])
PROCESSING_TIME = Histogram('rabbitmq_processing_time', 'Message processing time', ['queue_name'])

def monitor_queue():
    """监控队列状态"""
    while True:
        try:
            # 获取队列状态
            channel = get_rabbitmq_channel()
            queues = get_all_queues(channel)
            
            for queue in queues:
                QUEUE_LENGTH.labels(queue_name=queue['name']).set(queue['messages'])
                # 其他监控逻辑...
                
        except Exception as e:
            print(f"监控错误: {e}")
        
        time.sleep(30)  # 每30秒监控一次
```

### 2. 日志管理

#### 2.1 日志级别配置
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rabbitmq_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def process_message(ch, method, properties, body):
    try:
        logger.info(f"开始处理消息: {properties.message_id}")
        
        # 处理逻辑
        result = process_order(body)
        
        logger.info(f"消息处理完成: {properties.message_id}, 结果: {result}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"消息处理失败: {properties.message_id}, 错误: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

#### 2.2 结构化日志
```python
import json
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def log_message_processing(message_id, operation, status):
    logger.info(
        "message_processing",
        message_id=message_id,
        operation=operation,
        status=status,
        timestamp=datetime.now().isoformat()
    )
```

## 🔧 故障处理与恢复

### 1. 常见故障场景

#### 1.1 消息积压
```python
def handle_queue_backlog(channel, queue_name):
    """处理队列积压"""
    # 监控队列长度
    result = channel.queue_declare(queue=queue_name, passive=True)
    queue_length = result.method.message_count
    
    if queue_length > 1000:
        logger.warning(f"队列 {queue_name} 积压严重: {queue_length} 条消息")
        
        # 启动多个消费者处理
        for i in range(5):  # 启动5个消费者
            start_consumer_thread(queue_name, f"worker_{i}")
    
    return queue_length
```

#### 1.2 网络分区
```python
class NetworkPartitionHandler:
    def __init__(self):
        self.partition_detection_time = None
        self.partition_threshold = 30  # 30秒
    
    def detect_partition(self):
        """检测网络分区"""
        cluster_status = get_cluster_status()
        nodes = cluster_status['running_nodes']
        
        if len(nodes) < expected_nodes:
            if not self.partition_detection_time:
                self.partition_detection_time = time.time()
            elif time.time() - self.partition_detection_time > self.partition_threshold:
                logger.critical("检测到网络分区，执行恢复策略")
                self.execute_recovery_strategy()
        else:
            self.partition_detection_time = None
    
    def execute_recovery_strategy(self):
        """执行恢复策略"""
        # 重新连接节点
        restart_cluster_nodes()
        # 重新建立镜像队列
        recreate_mirrored_queues()
        # 验证数据一致性
        verify_data_consistency()
```

### 2. 数据恢复

#### 2.1 消息恢复
```python
def recover_lost_messages(channel, recovery_queue='dead_letter_queue'):
    """从死信队列恢复丢失的消息"""
    try:
        # 获取死信队列中的消息
        result = channel.queue_declare(queue=recovery_queue, passive=True)
        message_count = result.method.message_count
        
        logger.info(f"发现 {message_count} 条死信消息，准备恢复")
        
        recovered_count = 0
        while message_count > 0:
            # 获取一条消息
            method_frame, header_frame, body = channel.basic_get(
                queue=recovery_queue,
                auto_ack=False
            )
            
            if method_frame:
                try:
                    # 解析消息
                    message_data = json.loads(body.decode('utf-8'))
                    
                    # 分析死信原因
                    if self.is_recoverable(message_data):
                        # 恢复消息到原始队列
                        self.recover_message_to_original_queue(message_data)
                        recovered_count += 1
                    
                    # 确认处理
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    
                except Exception as e:
                    logger.error(f"恢复消息失败: {e}")
                    channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
            
            message_count -= 1
        
        logger.info(f"成功恢复 {recovered_count} 条消息")
        
    except Exception as e:
        logger.error(f"消息恢复失败: {e}")
```

## 🚀 最佳实践

### 1. 性能优化

#### 1.1 连接池管理
```python
import threading
from queue import Queue
import pika

class ConnectionPool:
    def __init__(self, connection_params, pool_size=10):
        self.connection_params = connection_params
        self.pool_size = pool_size
        self.connections = Queue()
        self.lock = threading.Lock()
    
    def get_connection(self):
        """获取连接"""
        try:
            # 尝试从池中获取现有连接
            connection = self.connections.get_nowait()
            
            # 检查连接是否仍然有效
            if connection.is_open:
                return connection
            
            connection.close()
            
        except:
            pass
        
        # 创建新连接
        return pika.BlockingConnection(self.connection_params)
    
    def return_connection(self, connection):
        """归还连接"""
        try:
            if connection.is_open:
                self.connections.put_nowait(connection)
        except:
            connection.close()
    
    def close_all(self):
        """关闭所有连接"""
        while not self.connections.empty():
            try:
                connection = self.connections.get_nowait()
                connection.close()
            except:
                break
```

#### 1.2 批处理优化
```python
class BatchMessageHandler:
    def __init__(self, batch_size=100, batch_timeout=5):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_messages = []
        self.last_batch_time = time.time()
    
    def add_message(self, message_data):
        """添加消息到批处理"""
        self.pending_messages.append(message_data)
        
        # 检查是否达到批处理大小或超时
        if (len(self.pending_messages) >= self.batch_size or 
            time.time() - self.last_batch_time > self.batch_timeout):
            return self.process_batch()
        
        return False
    
    def process_batch(self):
        """处理批次"""
        if not self.pending_messages:
            return False
        
        batch = self.pending_messages.copy()
        self.pending_messages.clear()
        self.last_batch_time = time.time()
        
        try:
            # 批量处理消息
            self.batch_process(batch)
            logger.info(f"批处理完成，处理了 {len(batch)} 条消息")
            return True
            
        except Exception as e:
            logger.error(f"批处理失败: {e}")
            # 将消息重新加入待处理队列
            self.pending_messages.extend(batch)
            return False
    
    def batch_process(self, messages):
        """实际批量处理逻辑"""
        # 使用数据库事务批量插入
        with self.db.transaction():
            for message in messages:
                self.process_single_message(message)
```

### 2. 架构设计模式

#### 2.1 事件驱动架构
```python
class EventBus:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, handler):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event_type, data):
        """发布事件"""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"事件处理器执行失败: {e}")
    
    def handle_rabbitmq_message(self, ch, method, properties, body):
        """处理RabbitMQ消息并发布事件"""
        try:
            event_data = json.loads(body.decode('utf-8'))
            event_type = event_data.get('type')
            
            if event_type:
                self.publish(event_type, event_data)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"事件处理失败: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

#### 2.2 CQRS模式
```python
class CommandHandler:
    """命令处理器 - 写操作"""
    def __init__(self, rabbitmq_channel):
        self.channel = rabbitmq_channel
    
    def handle_order_created(self, order_data):
        """处理订单创建命令"""
        try:
            # 验证命令
            self.validate_order(order_data)
            
            # 更新写模型（数据库）
            order_id = self.create_order(order_data)
            
            # 发布领域事件
            event = {
                'type': 'order_created',
                'order_id': order_id,
                'data': order_data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.publish_event(event)
            
        except Exception as e:
            logger.error(f"订单创建失败: {e}")
            raise

class EventHandler:
    """事件处理器 - 读操作"""
    def __init__(self, rabbitmq_channel, read_model_db):
        self.channel = rabbitmq_channel
        self.read_model_db = read_model_db
    
    def handle_order_created_event(self, ch, method, properties, body):
        """处理订单创建事件"""
        try:
            event_data = json.loads(body.decode('utf-8'))
            
            # 更新读模型（缓存、搜索索引等）
            self.update_order_summary(event_data)
            
            # 更新统计信息
            self.update_statistics(event_data)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"事件处理失败: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

## 📈 扩展阅读

### 1. 性能调优
- RabbitMQ性能调优指南
- 集群容量规划
- 高并发场景优化

### 2. 监控运维
- Prometheus + Grafana监控方案
- ELK日志分析系统
- 告警规则设计

### 3. 架构模式
- 事件溯源（Event Sourcing）
- Saga分布式事务
- 消息驱动微服务

### 4. 故障处理
- 灾难恢复计划
- 数据一致性保障
- 业务连续性设计

## 🎯 总结

RabbitMQ的高级特性为企业级消息系统提供了强大的基础能力：

1. **可靠传递**：通过消息确认和持久化确保消息不丢失
2. **灵活路由**：多种交换机类型支持复杂的路由需求
3. **高可用**：集群和镜像队列提供高可用性保障
4. **可扩展**：支持水平扩展和负载均衡
5. **安全性**：完整的认证授权和安全机制
6. **可监控**：丰富的监控指标和运维工具

掌握这些高级特性，能够帮助您构建健壮、高效、可扩展的企业级消息系统。在实际项目中，需要根据业务需求选择合适的特性组合，并进行充分的测试和调优。

**下一步学习**：建议结合实际项目场景，深入学习RabbitMQ与具体业务系统的集成方案，以及在云原生环境下的部署和运维实践。