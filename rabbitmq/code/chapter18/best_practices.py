# RabbitMQ最佳实践与设计模式代码示例

import pika
import json
import asyncio
import aio_pika
import gzip
import time
import logging
import threading
import queue
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import psutil
import requests
from collections import defaultdict
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 枚举类定义
class ServiceType(Enum):
    USER_SERVICE = "user_service"
    ORDER_SERVICE = "order_service"
    PAYMENT_SERVICE = "payment_service"
    NOTIFICATION_SERVICE = "notification_service"
    INVENTORY_SERVICE = "inventory_service"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

class EventType(Enum):
    USER_REGISTERED = "user.registered"
    ORDER_CREATED = "order.created"
    ORDER_PAID = "order.paid"
    INVENTORY_UPDATED = "inventory.updated"
    NOTIFICATION_SENT = "notification.sent"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# 数据类定义
@dataclass
class Task:
    task_id: str
    payload: Dict[str, Any]
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class User:
    username: str
    password_hash: str
    permissions: List[Dict[str, Any]]
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DomainEvent:
    event_id: str
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    version: int
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    causation_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class SecurityPolicy:
    policy_name: str
    pattern: str
    definition: str
    priority: int = 0
    apply_to: str = "queues"

@dataclass
class Alert:
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

# 工作队列模式实现
class WorkQueuePattern:
    """工作队列模式实现类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.channel = None
        self.exchange_name = 'work_queue_exchange'
        self.queue_name = 'task_queue'
        self.dl_queue_name = 'task_dlq'
        self.routing_key = 'task'
        self.task_handlers: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        self.processed_tasks = set()
        
    def connect(self) -> bool:
        """建立连接"""
        try:
            credentials = pika.PlainCredentials(
                self.config.get('username', 'guest'),
                self.config.get('password', 'guest')
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5672),
                virtual_host=self.config.get('virtual_host', '/'),
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5,
                heartbeat=30,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("工作队列连接建立成功")
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def setup_queues(self) -> bool:
        """设置队列和交换机"""
        try:
            # 声明工作队列
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True,
                arguments={
                    'x-max-priority': 10,
                    'x-dead-letter-exchange': 'dlx_exchange',
                    'x-dead-letter-routing-key': 'dlq_task',
                    'x-message-ttl': 3600000  # 1小时TTL
                }
            )
            
            # 声明死信队列
            self.channel.queue_declare(
                queue=self.dl_queue_name,
                durable=True
            )
            
            # 声明死信交换机
            self.channel.exchange_declare(
                exchange='dlx_exchange',
                exchange_type='direct',
                durable=True
            )
            
            # 绑定死信队列
            self.channel.queue_bind(
                exchange='dlx_exchange',
                queue=self.dl_queue_name,
                routing_key='dlq_task'
            )
            
            # 声明工作交换机
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='direct',
                durable=True
            )
            
            # 绑定工作队列
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.routing_key
            )
            
            logger.info("队列和交换机设置完成")
            return True
            
        except Exception as e:
            logger.error(f"队列设置失败: {e}")
            return False
    
    def register_task_handler(self, task_type: str, handler: Callable[[Task], bool]):
        """注册任务处理器"""
        with self.lock:
            self.task_handlers[task_type] = handler
            logger.info(f"注册任务处理器: {task_type}")
    
    def submit_task(self, task: Task) -> bool:
        """提交任务"""
        try:
            # 创建任务消息
            message_body = json.dumps({
                'task_id': task.task_id,
                'task_type': task.payload.get('task_type', 'generic'),
                'payload': task.payload,
                'priority': task.priority,
                'retry_count': task.retry_count,
                'created_at': task.created_at.isoformat()
            })
            
            # 设置消息属性
            properties = pika.BasicProperties(
                delivery_mode=2,  # 持久化
                priority=task.priority,
                message_id=task.task_id,
                timestamp=int(task.created_at.timestamp()),
                correlation_id=task.task_id
            )
            
            # 发布消息
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=message_body,
                properties=properties
            )
            
            logger.info(f"任务提交成功: {task.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"任务提交失败: {e}")
            return False
    
    def start_consuming(self, prefetch_count: int = 100):
        """开始消费消息"""
        try:
            # 设置QoS
            self.channel.basic_qos(prefetch_count=prefetch_count)
            
            # 开始消费
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._process_message,
                auto_ack=False
            )
            
            logger.info("开始消费消息")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("停止消费消息")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"消费消息异常: {e}")
    
    def _process_message(self, ch, method, properties, body):
        """处理消息"""
        try:
            message_data = json.loads(body.decode())
            task_id = message_data['task_id']
            task_type = message_data['task_type']
            
            # 检查是否已处理过（幂等性）
            if task_id in self.processed_tasks:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # 创建任务对象
            task = Task(
                task_id=task_id,
                payload=message_data['payload'],
                priority=message_data.get('priority', 0),
                retry_count=message_data.get('retry_count', 0),
                created_at=datetime.fromisoformat(message_data['created_at'])
            )
            
            # 处理任务
            if task_type in self.task_handlers:
                success = self.task_handlers[task_type](task)
                
                if success:
                    # 添加到已处理集合
                    self.processed_tasks.add(task_id)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"任务处理成功: {task_id}")
                else:
                    # 处理失败，检查重试次数
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        # 重新发布消息
                        message_data['retry_count'] = task.retry_count
                        new_body = json.dumps(message_data).encode()
                        
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=True
                        )
                        
                        # 延迟重试
                        time.sleep(2 ** task.retry_count)
                        
                        ch.basic_publish(
                            exchange=self.exchange_name,
                            routing_key=self.routing_key,
                            body=new_body,
                            properties=properties
                        )
                    else:
                        # 超过最大重试次数，进入死信队列
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=False
                        )
                        logger.warning(f"任务处理失败，已进入死信队列: {task_id}")
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.warning(f"未找到任务处理器: {task_type}")
                
        except Exception as e:
            logger.error(f"消息处理异常: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("工作队列连接已关闭")

# 发布/订阅模式实现
class PubSubPattern:
    """发布/订阅模式实现类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.channel = None
        self.exchange_name = 'pub_sub_exchange'
        self.subscribers: Dict[str, Callable] = {}
        self.message_patterns: Dict[str, List[str]] = {}
        self.lock = threading.Lock()
        
    def connect(self) -> bool:
        """建立连接"""
        try:
            credentials = pika.PlainCredentials(
                self.config.get('username', 'guest'),
                self.config.get('password', 'guest')
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5672),
                virtual_host=self.config.get('virtual_host', '/'),
                credentials=credentials,
                heartbeat=30
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def setup_exchange(self) -> bool:
        """设置主题交换机"""
        try:
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True,
                arguments={
                    'x-delayed-message': 'x-delayed-type',
                    'x-message-ttl': 3600000
                }
            )
            logger.info(f"主题交换机 '{self.exchange_name}' 创建成功")
            return True
            
        except Exception as e:
            logger.error(f"交换机设置失败: {e}")
            return False
    
    def publish_message(self, routing_key: str, message: Dict[str, Any], headers: Dict[str, str] = None):
        """发布消息"""
        try:
            message_body = json.dumps(message)
            properties = pika.BasicProperties(
                delivery_mode=2,
                headers=headers or {},
                timestamp=int(datetime.now().timestamp()),
                message_id=str(uuid.uuid4())
            )
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=message_body,
                properties=properties
            )
            
            logger.info(f"消息发布成功: {routing_key}")
            
        except Exception as e:
            logger.error(f"消息发布失败: {e}")
    
    def subscribe(self, subscriber_id: str, routing_pattern: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """订阅消息"""
        try:
            queue_name = f"subscriber_{subscriber_id}_{int(time.time())}"
            
            # 创建临时队列
            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments={
                    'x-message-ttl': 3600000,
                    'x-expires': 7200000
                }
            )
            
            # 绑定队列到交换机
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=routing_pattern
            )
            
            # 保存订阅者信息
            with self.lock:
                self.subscribers[subscriber_id] = handler
                self.message_patterns[subscriber_id] = routing_pattern
            
            # 开始消费
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=lambda ch, method, properties, body: self._handle_message(subscriber_id, body),
                auto_ack=True
            )
            
            logger.info(f"订阅者 {subscriber_id} 成功订阅模式: {routing_pattern}")
            return True
            
        except Exception as e:
            logger.error(f"订阅失败: {e}")
            return False
    
    def _handle_message(self, subscriber_id: str, body: bytes):
        """处理订阅消息"""
        try:
            message_data = json.loads(body.decode())
            if subscriber_id in self.subscribers:
                self.subscribers[subscriber_id](message_data)
        except Exception as e:
            logger.error(f"订阅消息处理异常: {e}")
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()

# 微服务通信模式实现
class MicroServiceBus:
    """微服务总线实现类"""
    
    def __init__(self, service_name: ServiceType, config: Dict[str, Any]):
        self.service_name = service_name
        self.config = config
        self.connection = None
        self.channel = None
        self.exchange_name = 'microservice_bus'
        self.request_queue_name = f"{service_name.value}_requests"
        self.response_queue_name = f"{service_name.value}_responses"
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.handlers: Dict[str, Callable] = {}
        
    async def connect(self) -> bool:
        """异步建立连接"""
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5672),
                login=self.config.get('username', 'guest'),
                password=self.config.get('password', 'guest'),
                loop=asyncio.get_event_loop()
            )
            
            self.channel = await self.connection.channel()
            await self.setup_queues()
            await self.start_consuming()
            
            logger.info(f"{self.service_name.value} 连接建立成功")
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    async def setup_queues(self):
        """设置队列"""
        # 声明交换机
        await self.channel.set_qos(prefetch_count=10)
        
        # 声明请求队列
        await self.channel.declare_queue(
            self.request_queue_name,
            durable=True,
            arguments={'x-message-ttl': 30000}  # 30秒TTL
        )
        
        # 声明响应队列
        await self.channel.declare_queue(
            self.response_queue_name,
            durable=True,
            arguments={'x-message-ttl': 30000}
        )
        
        # 绑定请求队列
        await self.channel.set_qos(prefetch_count=10)
        
    async def register_handler(self, action: str, handler: Callable):
        """注册请求处理器"""
        self.handlers[action] = handler
        logger.info(f"注册处理器: {action}")
    
    async def send_request(self, target_service: ServiceType, action: str, payload: Dict[str, Any], timeout: int = 30) -> Optional[Dict[str, Any]]:
        """发送服务请求"""
        try:
            correlation_id = str(uuid.uuid4())
            
            # 创建Future等待响应
            response_future = asyncio.Future()
            self.pending_requests[correlation_id] = response_future
            
            # 创建请求消息
            message_data = {
                'source_service': self.service_name.value,
                'target_service': target_service.value,
                'action': action,
                'payload': payload,
                'timestamp': datetime.now().isoformat(),
                'correlation_id': correlation_id
            }
            
            message = aio_pika.Message(
                json.dumps(message_data).encode(),
                delivery_mode=2,
                correlation_id=correlation_id,
                reply_to=self.response_queue_name,
                timestamp=int(datetime.now().timestamp())
            )
            
            # 发送请求
            routing_key = f"{target_service.value}.{action}"
            await self.channel.default_exchange.publish(message, routing_key=routing_key)
            
            logger.info(f"发送请求: {self.service_name.value} -> {target_service.value}.{action}")
            
            # 等待响应
            try:
                response = await asyncio.wait_for(response_future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                logger.warning(f"请求超时: {correlation_id}")
                self.pending_requests.pop(correlation_id, None)
                return None
                
        except Exception as e:
            logger.error(f"发送请求失败: {e}")
            return None
    
    async def start_consuming(self):
        """开始消费"""
        await self.channel.consume(self._handle_request, no_ack=True)
        await self.channel.consume(self._handle_response, self.response_queue_name, no_ack=True)
    
    async def _handle_request(self, message: aio_pika.IncomingMessage):
        """处理服务请求"""
        try:
            data = json.loads(message.body.decode())
            action = data['action']
            
            if action in self.handlers:
                response_data = await self.handlers[action](data['payload'])
                
                # 发送响应
                response = aio_pika.Message(
                    json.dumps(response_data).encode(),
                    correlation_id=message.correlation_id,
                    delivery_mode=2
                )
                
                await self.channel.default_exchange.publish(
                    response,
                    routing_key=message.reply_to
                )
                
                logger.info(f"处理请求成功: {action}")
            else:
                logger.warning(f"未找到处理器: {action}")
                
        except Exception as e:
            logger.error(f"处理请求异常: {e}")
    
    async def _handle_response(self, message: aio_pika.IncomingMessage):
        """处理服务响应"""
        try:
            correlation_id = message.correlation_id
            if correlation_id in self.pending_requests:
                response_data = json.loads(message.body.decode())
                self.pending_requests[correlation_id].set_result(response_data)
                self.pending_requests.pop(correlation_id, None)
        except Exception as e:
            logger.error(f"处理响应异常: {e}")

# 事件驱动架构实现
class EventBus:
    """事件总线实现类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.connection = None
        self.channel = None
        self.exchange_name = 'event_bus'
        
    async def connect(self) -> bool:
        """异步建立连接"""
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5672),
                login=self.config.get('username', 'guest'),
                password=self.config.get('password', 'guest')
            )
            
            self.channel = await self.connection.channel()
            await self.setup_exchange()
            await self.start_consuming()
            
            logger.info("事件总线连接建立成功")
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    async def setup_exchange(self):
        """设置事件交换机"""
        await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
    
    async def publish_event(self, event: DomainEvent):
        """发布事件"""
        try:
            message_data = {
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'aggregate_id': event.aggregate_id,
                'aggregate_type': event.aggregate_type,
                'version': event.version,
                'payload': event.payload,
                'metadata': event.metadata,
                'timestamp': event.timestamp.isoformat(),
                'causation_id': event.causation_id,
                'correlation_id': event.correlation_id
            }
            
            message = aio_pika.Message(
                json.dumps(message_data).encode(),
                delivery_mode=2,
                correlation_id=event.correlation_id,
                timestamp=int(event.timestamp.timestamp())
            )
            
            routing_key = f"{event.event_type.value}.*"
            await self.channel.default_exchange.publish(
                message,
                routing_key=routing_key
            )
            
            logger.info(f"事件发布成功: {event.event_id}")
            
        except Exception as e:
            logger.error(f"事件发布失败: {e}")
    
    def subscribe(self, event_type: EventType, handler: Callable[[DomainEvent], None]):
        """订阅事件"""
        self.event_handlers[event_type].append(handler)
        logger.info(f"订阅事件: {event_type.value}")
    
    async def start_consuming(self):
        """开始消费事件"""
        queue = await self.channel.declare_queue('', exclusive=True, durable=True)
        
        # 绑定所有事件主题
        for event_type in EventType:
            await queue.bind(
                self.exchange_name,
                routing_key=f"{event_type.value}.*"
            )
        
        await queue.consume(self._handle_event)
    
    async def _handle_event(self, message: aio_pika.IncomingMessage):
        """处理事件"""
        try:
            data = json.loads(message.body.decode())
            event_type = EventType(data['event_type'])
            
            # 创建事件对象
            event = DomainEvent(
                event_id=data['event_id'],
                event_type=event_type,
                aggregate_id=data['aggregate_id'],
                aggregate_type=data['aggregate_type'],
                version=data['version'],
                payload=data['payload'],
                metadata=data['metadata'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                causation_id=data.get('causation_id'),
                correlation_id=data['correlation_id']
            )
            
            # 调用事件处理器
            for handler in self.event_handlers.get(event_type, []):
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"事件处理器异常: {e}")
                    
        except Exception as e:
            logger.error(f"事件处理异常: {e}")

# 连接池管理器
class ConnectionPool:
    """连接池管理器"""
    
    def __init__(self, config: Dict[str, Any], pool_size: int = 10):
        self.config = config
        self.pool_size = pool_size
        self.connections = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.pool_size):
            connection = self._create_connection()
            if connection:
                self.connections.put(connection)
    
    def _create_connection(self) -> Optional[pika.BlockingConnection]:
        """创建新连接"""
        try:
            credentials = pika.PlainCredentials(
                self.config.get('username', 'guest'),
                self.config.get('password', 'guest')
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5672),
                virtual_host=self.config.get('virtual_host', '/'),
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5,
                heartbeat=30,
                blocked_connection_timeout=300
            )
            
            connection = pika.BlockingConnection(parameters)
            logger.info(f"创建新连接: {connection}")
            return connection
            
        except Exception as e:
            logger.error(f"创建连接失败: {e}")
            return None
    
    def get_connection(self, timeout: int = 10) -> Optional[pika.BlockingConnection]:
        """获取连接"""
        try:
            return self.connections.get(timeout=timeout)
        except queue.Empty:
            logger.warning("连接池已满，无法获取连接")
            return None
    
    def return_connection(self, connection: pika.BlockingConnection):
        """归还连接"""
        if connection and connection.is_open:
            try:
                self.connections.put(connection, timeout=1)
            except queue.Full:
                logger.warning("连接池已满，关闭多余连接")
                connection.close()

# 安全管理器
class SecurityManager:
    """安全管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.management_api_url = config.get('management_api_url', 'http://localhost:15672')
        self.username = config.get('admin_username', 'guest')
        self.password = config.get('admin_password', 'guest')
        self.users: Dict[str, User] = {}
        self.policies: Dict[str, SecurityPolicy] = {}
    
    def create_user(self, username: str, password: str, permissions: List[Dict[str, Any]], tags: List[str] = None) -> bool:
        """创建用户"""
        try:
            # 调用RabbitMQ Management API
            api_data = {
                'password': password,
                'tags': ','.join(tags or []),
                'permissions': permissions
            }
            
            response = requests.put(
                f"{self.management_api_url}/api/users/{username}",
                json=api_data,
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code in [201, 204]:
                logger.info(f"用户 {username} 创建成功")
                return True
            else:
                logger.error(f"用户创建失败: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"创建用户异常: {e}")
            return False
    
    def generate_security_report(self) -> Dict[str, Any]:
        """生成安全报告"""
        try:
            # 获取用户列表
            response = requests.get(
                f"{self.management_api_url}/api/users",
                auth=(self.username, self.password),
                timeout=10
            )
            
            users_data = response.json() if response.status_code == 200 else []
            
            # 获取连接列表
            response = requests.get(
                f"{self.management_api_url}/api/connections",
                auth=(self.username, self.password),
                timeout=10
            )
            
            connections_data = response.json() if response.status_code == 200 else []
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'user_summary': {
                    'total_users': len(users_data),
                    'active_users': len([u for u in users_data if u.get('tags')]),
                    'users_without_tags': len([u for u in users_data if not u.get('tags')])
                },
                'connection_summary': {
                    'total_connections': len(connections_data),
                    'ssl_connections': len([c for c in connections_data if c.get('ssl')]),
                    'non_ssl_connections': len([c for c in connections_data if not c.get('ssl')])
                },
                'security_issues': [],
                'recommendations': []
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成安全报告异常: {e}")
            return {}

# 监控系统
class MonitoringSystem:
    """监控系统"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.management_api_url = config.get('management_api_url', 'http://localhost:15672')
        self.username = config.get('username', 'guest')
        self.password = config.get('password', 'guest')
        self.metrics_history: List[Dict[str, Any]] = []
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_io': {
                    'bytes_sent': psutil.net_io_counters().bytes_sent,
                    'bytes_recv': psutil.net_io_counters().bytes_recv
                },
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
            return {}
    
    def collect_rabbitmq_metrics(self) -> Dict[str, Any]:
        """收集RabbitMQ指标"""
        try:
            # 获取队列指标
            response = requests.get(
                f"{self.management_api_url}/api/queues",
                auth=(self.username, self.password),
                timeout=10
            )
            
            queues = response.json() if response.status_code == 200 else []
            
            # 获取连接指标
            response = requests.get(
                f"{self.management_api_url}/api/connections",
                auth=(self.username, self.password),
                timeout=10
            )
            
            connections = response.json() if response.status_code == 200 else []
            
            # 获取交换机指标
            response = requests.get(
                f"{self.management_api_url}/api/exchanges",
                auth=(self.username, self.password),
                timeout=10
            )
            
            exchanges = response.json() if response.status_code == 200 else []
            
            return {
                'timestamp': datetime.now().isoformat(),
                'queues': queues,
                'connections': connections,
                'exchanges': exchanges,
                'queue_summary': {
                    'total_queues': len(queues),
                    'total_messages': sum(q.get('messages', 0) for q in queues),
                    'queue_details': [{'name': q['name'], 'messages': q.get('messages', 0)} for q in queues[:10]]
                },
                'connection_summary': {
                    'total_connections': len(connections),
                    'channel_details': [{'user': c.get('user'), 'state': c.get('state')} for c in connections[:10]]
                }
            }
            
        except Exception as e:
            logger.error(f"收集RabbitMQ指标失败: {e}")
            return {}
    
    def generate_health_report(self) -> Dict[str, Any]:
        """生成健康报告"""
        system_metrics = self.collect_system_metrics()
        rabbitmq_metrics = self.collect_rabbitmq_metrics()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'system_health': self._assess_system_health(system_metrics),
            'rabbitmq_health': self._assess_rabbitmq_health(rabbitmq_metrics),
            'overall_health': self._calculate_overall_health(system_metrics, rabbitmq_metrics),
            'recommendations': self._generate_recommendations(system_metrics, rabbitmq_metrics)
        }
        
        return report
    
    def _assess_system_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估系统健康状态"""
        health_score = 100
        
        cpu_percent = metrics.get('cpu_percent', 0)
        memory_percent = metrics.get('memory_percent', 0)
        disk_percent = metrics.get('disk_percent', 0)
        
        if cpu_percent > 80:
            health_score -= 20
        elif cpu_percent > 60:
            health_score -= 10
            
        if memory_percent > 85:
            health_score -= 30
        elif memory_percent > 70:
            health_score -= 15
            
        if disk_percent > 90:
            health_score -= 25
        elif disk_percent > 80:
            health_score -= 10
        
        health_status = 'healthy'
        if health_score < 70:
            health_status = 'warning'
        elif health_score < 40:
            health_status = 'critical'
        
        return {
            'status': health_status,
            'score': health_score,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent
        }
    
    def _assess_rabbitmq_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估RabbitMQ健康状态"""
        health_score = 100
        
        total_messages = metrics.get('queue_summary', {}).get('total_messages', 0)
        total_connections = metrics.get('connection_summary', {}).get('total_connections', 0)
        
        if total_messages > 10000:
            health_score -= 20
        elif total_messages > 5000:
            health_score -= 10
            
        if total_connections == 0:
            health_score -= 50
        
        health_status = 'healthy'
        if health_score < 70:
            health_status = 'warning'
        elif health_score < 40:
            health_status = 'critical'
        
        return {
            'status': health_status,
            'score': health_score,
            'total_messages': total_messages,
            'total_connections': total_connections
        }
    
    def _calculate_overall_health(self, system_metrics: Dict[str, Any], rabbitmq_metrics: Dict[str, Any]) -> str:
        """计算整体健康状态"""
        system_health = self._assess_system_health(system_metrics)
        rabbitmq_health = self._assess_rabbitmq_health(rabbitmq_metrics)
        
        avg_score = (system_health['score'] + rabbitmq_health['score']) / 2
        
        if avg_score >= 80:
            return 'healthy'
        elif avg_score >= 60:
            return 'warning'
        else:
            return 'critical'
    
    def _generate_recommendations(self, system_metrics: Dict[str, Any], rabbitmq_metrics: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        cpu_percent = system_metrics.get('cpu_percent', 0)
        memory_percent = system_metrics.get('memory_percent', 0)
        disk_percent = system_metrics.get('disk_percent', 0)
        total_messages = rabbitmq_metrics.get('queue_summary', {}).get('total_messages', 0)
        
        if cpu_percent > 80:
            recommendations.append("CPU使用率过高，建议优化应用性能或增加硬件资源")
        
        if memory_percent > 85:
            recommendations.append("内存使用率过高，建议增加内存或优化内存使用")
        
        if disk_percent > 90:
            recommendations.append("磁盘使用率过高，建议清理磁盘空间或扩展存储")
        
        if total_messages > 10000:
            recommendations.append("队列消息数量过多，建议检查消息处理逻辑或增加消费者数量")
        
        if not recommendations:
            recommendations.append("系统运行状态良好")
        
        return recommendations

# 故障检测系统
class FaultDetection:
    """故障检测系统"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.health_checks = {}
        self.thresholds = config.get('thresholds', {})
        self.alerts: List[Alert] = []
    
    def check_connection_health(self) -> Dict[str, Any]:
        """检查连接健康状态"""
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.config.get('host', 'localhost'),
                    port=self.config.get('port', 5672),
                    credentials=pika.PlainCredentials(
                        self.config.get('username', 'guest'),
                        self.config.get('password', 'guest')
                    )
                )
            )
            
            health_status = {
                'status': 'healthy',
                'connection_open': True,
                'response_time': 0.1,
                'checked_at': datetime.now().isoformat()
            }
            
            connection.close()
            return health_status
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection_open': False,
                'checked_at': datetime.now().isoformat()
            }
    
    def detect_performance_issues(self, metrics: Dict[str, Any]) -> List[Alert]:
        """检测性能问题"""
        alerts = []
        
        # 检查队列深度
        queue_depth_threshold = self.thresholds.get('queue_depth', 1000)
        for queue in metrics.get('queues', []):
            if queue.get('messages', 0) > queue_depth_threshold:
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    alert_type='queue_overflow',
                    severity=AlertSeverity.HIGH,
                    message=f"队列 {queue['name']} 消息数量过多",
                    details={
                        'queue': queue['name'],
                        'current_depth': queue['messages'],
                        'threshold': queue_depth_threshold
                    }
                )
                alerts.append(alert)
        
        # 检查消息速率
        message_rate_threshold = self.thresholds.get('message_rate', 100)
        current_rate = metrics.get('message_rate', 0)
        if current_rate > message_rate_threshold:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                alert_type='high_message_rate',
                severity=AlertSeverity.MEDIUM,
                message=f"消息处理速率过高: {current_rate} msgs/s",
                details={
                    'current_rate': current_rate,
                    'threshold': message_rate_threshold
                }
            )
            alerts.append(alert)
        
        # 检查连接数
        connection_threshold = self.thresholds.get('max_connections', 100)
        current_connections = len(metrics.get('connections', []))
        if current_connections > connection_threshold:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                alert_type='too_many_connections',
                severity=AlertSeverity.MEDIUM,
                message=f"连接数量过多: {current_connections}",
                details={
                    'current_connections': current_connections,
                    'threshold': connection_threshold
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def check_cluster_health(self) -> Dict[str, Any]:
        """检查集群健康状态"""
        try:
            # 这里应该调用RabbitMQ集群管理API来检查集群状态
            # 简化实现，返回示例数据
            return {
                'cluster_status': 'running',
                'nodes': [
                    {'name': 'rabbit@node1', 'status': 'running'},
                    {'name': 'rabbit@node2', 'status': 'running'},
                    {'name': 'rabbit@node3', 'status': 'running'}
                ],
                'mirrored_queues': 5,
                'queue_masters': 3
            }
        except Exception as e:
            logger.error(f"集群健康检查失败: {e}")
            return {'cluster_status': 'error', 'error': str(e)}

# 性能优化器
class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection_pool = ConnectionPool(config)
        self.optimization_strategies = [
            self._optimize_connection_pool,
            self._optimize_prefetch_count,
            self._optimize_batch_processing,
            self._optimize_message_size,
            self._optimize_queue_settings
        ]
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """分析性能指标"""
        analysis = {
            'performance_score': 100,
            'bottlenecks': [],
            'optimizations': [],
            'recommendations': []
        }
        
        # 分析连接池使用
        connections_count = len(metrics.get('connections', []))
        if connections_count == 0:
            analysis['bottlenecks'].append('no_connections')
            analysis['performance_score'] -= 20
        
        # 分析队列深度
        queues = metrics.get('queues', [])
        total_messages = sum(q.get('messages', 0) for q in queues)
        if total_messages > 5000:
            analysis['bottlenecks'].append('high_queue_depth')
            analysis['performance_score'] -= 30
        
        # 生成优化建议
        if analysis['performance_score'] < 70:
            analysis['recommendations'].append('考虑增加消费者数量以处理积压消息')
        
        if connections_count > 100:
            analysis['recommendations'].append('连接数过多，考虑使用连接池优化')
        
        return analysis
    
    def _optimize_connection_pool(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """优化连接池"""
        connections_count = len(metrics.get('connections', []))
        optimal_pool_size = min(max(connections_count // 2, 10), 50)
        
        return {
            'optimization': 'connection_pool',
            'recommended_size': optimal_pool_size,
            'current_size': connections_count,
            'impact': 'high'
        }
    
    def _optimize_prefetch_count(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """优化prefetch count"""
        queues = metrics.get('queues', [])
        total_messages = sum(q.get('messages', 0) for q in queues)
        
        if total_messages > 10000:
            recommended_prefetch = 200
        elif total_messages > 5000:
            recommended_prefetch = 100
        else:
            recommended_prefetch = 50
        
        return {
            'optimization': 'prefetch_count',
            'recommended_value': recommended_prefetch,
            'impact': 'medium'
        }
    
    def _optimize_batch_processing(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """优化批量处理"""
        return {
            'optimization': 'batch_processing',
            'recommended_batch_size': 100,
            'impact': 'high'
        }
    
    def _optimize_message_size(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """优化消息大小"""
        return {
            'optimization': 'message_compression',
            'enable_compression': True,
            'compression_threshold': 1024,  # 1KB
            'impact': 'medium'
        }
    
    def _optimize_queue_settings(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """优化队列设置"""
        return {
            'optimization': 'queue_settings',
            'recommended_ttl': 3600000,  # 1小时
            'max_queue_length': 10000,
            'dead_letter_exchange': True,
            'impact': 'medium'
        }
    
    def apply_optimizations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用优化策略"""
        applied_optimizations = []
        
        for strategy in self.optimization_strategies:
            optimization_result = strategy(analysis.get('metrics', {}))
            if optimization_result:
                applied_optimizations.append(optimization_result)
        
        return applied_optimizations

# 最佳实践演示函数
def demonstrate_best_practices():
    """演示RabbitMQ最佳实践"""
    print("=== RabbitMQ最佳实践演示 ===")
    
    # 1. 工作队列模式演示
    print("\n1. 工作队列模式演示")
    work_queue_config = {
        'host': 'localhost',
        'port': 5672,
        'username': 'guest',
        'password': 'guest'
    }
    
    work_queue = WorkQueuePattern(work_queue_config)
    if work_queue.connect():
        work_queue.setup_queues()
        
        # 注册任务处理器
        def handle_task(task: Task) -> bool:
            print(f"处理任务: {task.task_id}, 负载: {task.payload}")
            time.sleep(1)  # 模拟处理时间
            return True
        
        work_queue.register_task_handler('data_processing', handle_task)
        
        # 提交任务
        for i in range(5):
            task = Task(
                task_id=f"task_{i}",
                payload={'task_type': 'data_processing', 'data': f'数据{i}'}
            )
            work_queue.submit_task(task)
        
        work_queue.close()
    
    # 2. 发布/订阅模式演示
    print("\n2. 发布/订阅模式演示")
    pubsub = PubSubPattern(work_queue_config)
    if pubsub.connect():
        pubsub.setup_exchange()
        
        # 定义消息处理器
        def notification_handler(message: Dict[str, Any]):
            print(f"通知消息: {message}")
        
        # 订阅消息
        pubsub.subscribe("notification_service", "notifications.*", notification_handler)
        
        # 发布消息
        pubsub.publish_message("notifications.user_update", {
            'user_id': '123',
            'action': 'profile_updated',
            'timestamp': datetime.now().isoformat()
        })
        
        pubsub.close()
    
    # 3. 监控系统演示
    print("\n3. 监控系统演示")
    monitoring_config = {
        'management_api_url': 'http://localhost:15672',
        'username': 'guest',
        'password': 'guest'
    }
    
    monitoring = MonitoringSystem(monitoring_config)
    
    # 收集系统指标
    system_metrics = monitoring.collect_system_metrics()
    print(f"系统指标: CPU {system_metrics.get('cpu_percent', 0)}%, 内存 {system_metrics.get('memory_percent', 0)}%")
    
    # 收集RabbitMQ指标
    rabbitmq_metrics = monitoring.collect_rabbitmq_metrics()
    print(f"RabbitMQ指标: 总连接数 {len(rabbitmq_metrics.get('connections', []))}, 队列数 {len(rabbitmq_metrics.get('queues', []))}")
    
    # 生成健康报告
    health_report = monitoring.generate_health_report()
    print(f"整体健康状态: {health_report['overall_health']}")
    
    # 4. 安全检查演示
    print("\n4. 安全检查演示")
    security = SecurityManager(monitoring_config)
    
    # 生成安全报告
    security_report = security.generate_security_report()
    print(f"安全报告: 用户数 {security_report['user_summary']['total_users']}, 连接数 {security_report['connection_summary']['total_connections']}")
    
    # 5. 性能优化演示
    print("\n5. 性能优化演示")
    optimizer = PerformanceOptimizer(work_queue_config)
    
    # 分析性能
    performance_analysis = optimizer.analyze_performance(rabbitmq_metrics)
    print(f"性能评分: {performance_analysis['performance_score']}")
    print(f"瓶颈问题: {performance_analysis['bottlenecks']}")
    print(f"优化建议: {performance_analysis['recommendations']}")
    
    print("\n=== 最佳实践演示完成 ===")

# 主函数
if __name__ == "__main__":
    demonstrate_best_practices()
