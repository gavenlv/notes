"""
第13章：微服务架构消息模式核心实现
包含请求-响应、发布-订阅、事件驱动架构和Saga事务模式
"""

import asyncio
import pika
import uuid
import json
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod


class MessagePattern(Enum):
    """消息模式枚举"""
    REQUEST_RESPONSE = "request_response"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    WORK_QUEUE = "work_queue"
    EVENT_DRIVEN = "event_driven"


class ServiceStatus(Enum):
    """服务状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class EventType(Enum):
    """事件类型"""
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    ORDER_CREATED = "order.created"
    ORDER_PAID = "order.paid"
    ORDER_SHIPPED = "order.shipped"


class CommandType(Enum):
    """命令类型"""
    CREATE_ORDER = "create_order"
    CANCEL_ORDER = "cancel_order"
    PROCESS_PAYMENT = "process_payment"
    RESERVE_INVENTORY = "reserve_inventory"


class SagaStatus(Enum):
    """Saga状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class Message:
    """消息基类"""
    message_id: str
    message_type: str
    payload: dict
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    priority: int = 0
    headers: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "priority": self.priority,
            "headers": self.headers
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        return cls(
            message_id=data["message_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            priority=data.get("priority", 0),
            headers=data.get("headers", {})
        )


@dataclass
class Event:
    """事件"""
    event_id: str
    event_type: EventType
    aggregate_id: str
    data: dict
    timestamp: datetime
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "aggregate_id": self.aggregate_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            aggregate_id=data["aggregate_id"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data.get("version", 1),
            metadata=data.get("metadata", {})
        )


@dataclass
class Command:
    """命令"""
    command_id: str
    command_type: CommandType
    aggregate_id: str
    data: dict
    timestamp: datetime
    timeout: int = 300
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> dict:
        return {
            "command_id": self.command_id,
            "command_type": self.command_type.value,
            "aggregate_id": self.aggregate_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
class SagaStep:
    """Saga步骤"""
    step_id: str
    action_name: str
    compensate_name: str
    action_data: dict
    compensate_data: dict
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300


@dataclass
class SagaTransaction:
    """Saga事务"""
    saga_id: str
    steps: List[SagaStep]
    status: SagaStatus = SagaStatus.PENDING
    current_step_index: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


class MessageConnector:
    """消息连接器"""
    
    def __init__(self, host: str = 'localhost', port: int = 5672, 
                 username: str = None, password: str = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        
    def connect(self):
        """建立连接"""
        credentials = None
        if self.username and self.password:
            credentials = pika.PlainCredentials(self.username, self.password)
        
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # 声明交换机
        self.channel.exchange_declare(exchange='direct_exchange', exchange_type='direct', durable=True)
        self.channel.exchange_declare(exchange='topic_exchange', exchange_type='topic', durable=True)
        self.channel.exchange_declare(exchange='fanout_exchange', exchange_type='fanout', durable=True)
        
        # 声明死信交换机
        self.channel.exchange_declare(exchange='dead_letter_exchange', exchange_type='direct', durable=True)
        
        return self.connection, self.channel
    
    def close(self):
        """关闭连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


class RequestResponsePattern:
    """请求-响应模式实现"""
    
    def __init__(self, connector: MessageConnector, service_name: str):
        self.connector = connector
        self.service_name = service_name
        self.pending_requests = {}
        self.response_queue = f"response_{service_name}_{uuid.uuid4().hex[:8]}"
        
    def setup(self):
        """设置请求-响应模式"""
        channel = self.connector.channel
        
        # 声明响应队列
        channel.queue_declare(queue=self.response_queue, exclusive=True, auto_delete=True)
        
        # 设置消费者监听响应
        channel.basic_consume(
            queue=self.response_queue,
            on_message_callback=self._on_response_received,
            auto_ack=True
        )
        
        # 启动消费者线程
        response_thread = threading.Thread(target=channel.start_consuming)
        response_thread.daemon = True
        response_thread.start()
    
    def _on_response_received(self, channel, method, properties, body):
        """响应接收处理"""
        correlation_id = properties.correlation_id
        if correlation_id in self.pending_requests:
            future = self.pending_requests[correlation_id]
            try:
                response_data = json.loads(body)
                future.set_result(response_data)
            except Exception as e:
                future.set_exception(e)
            finally:
                del self.pending_requests[correlation_id]
    
    async def call(self, method: str, params: dict, timeout: int = 30) -> dict:
        """发起请求调用"""
        loop = asyncio.get_event_loop()
        correlation_id = str(uuid.uuid4())
        
        # 创建future
        future = loop.create_future()
        self.pending_requests[correlation_id] = future
        
        # 构建消息
        message = Message(
            message_id=str(uuid.uuid4()),
            message_type="request",
            payload={"method": method, "params": params},
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id,
            reply_to=self.response_queue
        )
        
        # 发送消息
        self.connector.channel.basic_publish(
            exchange='direct_exchange',
            routing_key=f"request.{self.service_name}",
            properties=pika.BasicProperties(
                delivery_mode=2,
                correlation_id=correlation_id,
                reply_to=self.response_queue,
                content_type='application/json',
                headers={'service': self.service_name}
            ),
            body=json.dumps(message.to_dict())
        )
        
        try:
            # 等待响应
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            del self.pending_requests[correlation_id]
            raise TimeoutError(f"请求超时: {method}")
    
    def handle_request(self, handler_func: Callable):
        """处理请求"""
        def request_handler(channel, method, properties, body):
            try:
                message_data = json.loads(body)
                message = Message.from_dict(message_data)
                
                # 调用处理函数
                result = handler_func(message.payload["method"], message.payload["params"])
                
                # 发送响应
                if message.reply_to:
                    self.connector.channel.basic_publish(
                        exchange='',
                        routing_key=message.reply_to,
                        properties=pika.BasicProperties(
                            correlation_id=message.correlation_id,
                            content_type='application/json'
                        ),
                        body=json.dumps(result)
                    )
                
                channel.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"处理请求失败: {e}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # 设置消费者
        request_queue = f"request.{self.service_name}"
        self.connector.channel.queue_declare(queue=request_queue, durable=True)
        self.connector.channel.basic_consume(
            queue=request_queue,
            on_message_callback=request_handler
        )
    
    def start_consuming(self):
        """开始消费消息"""
        self.connector.channel.start_consuming()


class PublishSubscribePattern:
    """发布-订阅模式实现"""
    
    def __init__(self, connector: MessageConnector):
        self.connector = connector
        self.subscribers = {}  # event_type -> [callback_functions]
        self.exchange_name = "event_bus"
        
    def setup(self):
        """设置发布-订阅模式"""
        # 交换机已由MessageConnector创建
        
    def subscribe(self, event_type: EventType, callback: Callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        
        # 为每个订阅者创建独立的队列
        queue_name = f"event_queue_{callback.__name__}_{event_type.value}"
        
        self.connector.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-message-ttl': 86400000,  # 24小时过期
                'x-dead-letter-exchange': 'dead_letter_exchange',
                'x-dead-letter-routing-key': f"dead_letter_{event_type.value}"
            }
        )
        
        # 绑定队列到交换机
        self.connector.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=event_type.value
        )
        
        # 设置消费者
        def event_consumer(channel, method, properties, body):
            try:
                event_data = json.loads(body)
                event = Event.from_dict(event_data)
                
                # 调用订阅者回调
                for callback in self.subscribers[event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"事件处理失败: {e}")
                
                channel.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"处理事件失败: {e}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.connector.channel.basic_consume(
            queue=queue_name,
            on_message_callback=event_consumer
        )
    
    def publish(self, event: Event):
        """发布事件"""
        self.connector.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=event.event_type.value,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json',
                headers={
                    'event_type': event.event_type.value,
                    'aggregate_id': event.aggregate_id
                }
            ),
            body=json.dumps(event.to_dict())
        )
    
    def start_consuming(self):
        """开始消费事件"""
        self.connector.channel.start_consuming()


class WorkQueuePattern:
    """工作队列模式实现"""
    
    def __init__(self, connector: MessageConnector, queue_name: str, worker_count: int = 4):
        self.connector = connector
        self.queue_name = queue_name
        self.worker_count = worker_count
        self.task_handlers = {}
        
    def setup(self):
        """设置工作队列"""
        # 声明持久化队列
        self.connector.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments={
                'x-message-ttl': 86400000,  # 24小时过期
                'x-dead-letter-exchange': 'dead_letter_exchange',
                'x-dead-letter-routing-key': f"dead_letter_{self.queue_name}"
            }
        )
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.task_handlers[task_type] = handler
    
    def start_workers(self):
        """启动工作进程"""
        print(f"启动 {self.worker_count} 个工作进程...")
        
        for worker_id in range(self.worker_count):
            thread = threading.Thread(
                target=self.worker_process,
                args=(f"worker_{worker_id}",)
            )
            thread.daemon = True
            thread.start()
    
    def worker_process(self, worker_id: str):
        """工作进程"""
        print(f"工作进程 {worker_id} 已启动")
        
        def task_consumer(channel, method, properties, body):
            try:
                task_data = json.loads(body)
                task_type = task_data.get("type")
                task_params = task_data.get("params", {})
                
                # 查找处理器
                if task_type in self.task_handlers:
                    print(f"工作进程 {worker_id} 处理任务: {task_type}")
                    
                    # 调用处理器
                    result = self.task_handlers[task_type](**task_params)
                    
                    if result.get("success", True):
                        print(f"工作进程 {worker_id} 完成任务: {task_type}")
                        channel.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        print(f"工作进程 {worker_id} 任务失败: {task_type} - {result.get('error')}")
                        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                else:
                    print(f"未知任务类型: {task_type}")
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    
            except Exception as e:
                print(f"工作进程 {worker_id} 处理任务失败: {e}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # 设置消费者
        self.connector.channel.basic_qos(prefetch_count=1)
        self.connector.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=task_consumer
        )
        
        # 启动消费
        try:
            self.connector.channel.start_consuming()
        except KeyboardInterrupt:
            self.connector.channel.stop_consuming()
    
    def submit_task(self, task_type: str, params: dict, priority: int = 0):
        """提交任务"""
        task_data = {
            "type": task_type,
            "params": params,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": priority
        }
        
        # 设置消息优先级
        properties = pika.BasicProperties(
            priority=priority,
            delivery_mode=2
        )
        
        self.connector.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=properties,
            body=json.dumps(task_data)
        )
        
        print(f"任务已提交: {task_type}")


class EventDrivenArchitecture:
    """事件驱动架构实现"""
    
    def __init__(self, connector: MessageConnector):
        self.connector = connector
        self.event_store = {}
        self.event_handlers = {}
        self.projection_handlers = {}
        
    def setup(self):
        """设置事件驱动架构"""
        # 声明事件存储交换机
        self.connector.channel.exchange_declare(
            exchange="event_store",
            exchange_type='topic',
            durable=True
        )
        
        # 声明事件存储队列
        self.connector.channel.queue_declare(
            queue="events",
            durable=True
        )
        
        self.connector.channel.queue_bind(
            exchange="event_store",
            queue="events",
            routing_key="events.*"
        )
    
    def save_event(self, event: Event):
        """保存事件"""
        # 保存到事件存储
        if event.aggregate_id not in self.event_store:
            self.event_store[event.aggregate_id] = []
        
        self.event_store[event.aggregate_id].append(event)
        
        # 发布事件
        routing_key = f"events.{event.event_type.value}"
        
        self.connector.channel.basic_publish(
            exchange="event_store",
            routing_key=routing_key,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json',
                headers={
                    'aggregate_id': event.aggregate_id,
                    'version': event.version,
                    'event_type': event.event_type.value
                }
            ),
            body=json.dumps(event.to_dict())
        )
    
    def get_events(self, aggregate_id: str) -> List[Event]:
        """获取聚合的所有事件"""
        return self.event_store.get(aggregate_id, [])
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        
        # 设置消费者
        queue_name = f"event_handler_{event_type.value}"
        self.connector.channel.queue_declare(queue=queue_name, durable=True)
        self.connector.channel.queue_bind(
            exchange="event_store",
            queue=queue_name,
            routing_key=f"events.{event_type.value}"
        )
        
        def handler_consumer(channel, method, properties, body):
            try:
                event_data = json.loads(body)
                event = Event.from_dict(event_data)
                
                # 调用事件处理器
                for handler in self.event_handlers[event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        print(f"事件处理器失败: {e}")
                
                channel.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"处理事件失败: {e}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.connector.channel.basic_consume(
            queue=queue_name,
            on_message_callback=handler_consumer
        )
    
    def register_projection_handler(self, projection_name: str, handler: Callable):
        """注册投影处理器"""
        self.projection_handlers[projection_name] = handler
        
        # 为投影创建专用队列
        queue_name = f"projection_{projection_name}"
        self.connector.channel.queue_declare(queue=queue_name, durable=True)
        self.connector.channel.queue_bind(
            exchange="event_store",
            queue=queue_name,
            routing_key="events.*"
        )
        
        def projection_consumer(channel, method, properties, body):
            try:
                event_data = json.loads(body)
                event = Event.from_dict(event_data)
                
                # 更新投影
                if projection_name in self.projection_handlers:
                    self.projection_handlers[projection_name](event)
                
                channel.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"投影更新失败: {e}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.connector.channel.basic_consume(
            queue=queue_name,
            on_message_callback=projection_consumer
        )


class SagaPattern:
    """Saga事务模式实现"""
    
    def __init__(self, connector: MessageConnector):
        self.connector = connector
        self.saga_storage = {}
        self.action_handlers = {}
        self.compensate_handlers = {}
        
    def setup(self):
        """设置Saga模式"""
        # 声明Saga交换机
        self.connector.channel.exchange_declare(
            exchange="saga_bus",
            exchange_type='topic',
            durable=True
        )
        
        # 声明相关队列
        self.connector.channel.queue_declare(queue="saga_commands", durable=True)
        self.connector.channel.queue_declare(queue="saga_events", durable=True)
        
        self.connector.channel.queue_bind(
            exchange="saga_bus",
            queue="saga_commands",
            routing_key="saga.commands.*"
        )
        
        self.connector.channel.queue_bind(
            exchange="saga_bus",
            queue="saga_events",
            routing_key="saga.events.*"
        )
    
    def register_action_handler(self, action_name: str, handler: Callable):
        """注册动作处理器"""
        self.action_handlers[action_name] = handler
    
    def register_compensate_handler(self, compensate_name: str, handler: Callable):
        """注册补偿处理器"""
        self.compensate_handlers[compensate_name] = handler
    
    def create_saga(self, saga_id: str, steps: List[dict]) -> SagaTransaction:
        """创建Saga事务"""
        saga_steps = []
        for step_data in steps:
            saga_steps.append(SagaStep(
                step_id=step_data["step_id"],
                action_name=step_data["action_name"],
                compensate_name=step_data["compensate_name"],
                action_data=step_data.get("action_data", {}),
                compensate_data=step_data.get("compensate_data", {}),
                max_retries=step_data.get("max_retries", 3),
                timeout=step_data.get("timeout", 300)
            ))
        
        saga = SagaTransaction(
            saga_id=saga_id,
            steps=saga_steps,
            start_time=datetime.utcnow()
        )
        
        self.saga_storage[saga_id] = saga
        return saga
    
    def execute_saga(self, saga: SagaTransaction):
        """执行Saga事务"""
        saga.status = SagaStatus.RUNNING
        print(f"开始执行Saga: {saga.saga_id}")
        
        # 发送开始事件
        self._send_saga_event("saga.started", {
            "saga_id": saga.saga_id,
            "total_steps": len(saga.steps)
        })
        
        # 开始执行第一步
        if saga.steps:
            self._execute_step(saga, saga.steps[0])
    
    def _execute_step(self, saga: SagaTransaction, step: SagaStep):
        """执行Saga步骤"""
        step.status = "running"
        print(f"执行Saga步骤: {saga.saga_id} - {step.action_name}")
        
        # 发送步骤开始事件
        self._send_saga_event("saga.step_started", {
            "saga_id": saga.saga_id,
            "step_id": step.step_id,
            "action_name": step.action_name
        })
        
        if step.action_name in self.action_handlers:
            try:
                # 调用动作处理器
                result = self.action_handlers[step.action_name](step.action_data)
                
                if result.get("success", True):
                    step.status = "completed"
                    self._advance_saga(saga)
                else:
                    step.status = "failed"
                    self._handle_step_failure(saga, step, result.get("error", "动作执行失败"))
                    
            except Exception as e:
                step.status = "failed"
                self._handle_step_failure(saga, step, str(e))
        else:
            step.status = "failed"
            self._handle_step_failure(saga, step, f"未找到处理器: {step.action_name}")
    
    def _advance_saga(self, saga: SagaTransaction):
        """推进Saga执行"""
        completed_steps = sum(1 for step in saga.steps if step.status == "completed")
        
        if completed_steps == len(saga.steps):
            # 所有步骤完成
            saga.status = SagaStatus.COMPLETED
            saga.end_time = datetime.utcnow()
            
            # 发送完成事件
            self._send_saga_event("saga.completed", {
                "saga_id": saga.saga_id,
                "duration": (saga.end_time - saga.start_time).total_seconds()
            })
            
            print(f"Saga {saga.saga_id} 执行完成")
        else:
            # 执行下一步
            next_step = saga.steps[completed_steps]
            self._execute_step(saga, next_step)
    
    def _handle_step_failure(self, saga: SagaTransaction, step: SagaStep, error: str):
        """处理步骤失败"""
        step.retry_count += 1
        
        if step.retry_count <= step.max_retries:
            # 重试
            print(f"Saga步骤重试: {saga.saga_id} - {step.action_name} (第{step.retry_count}次)")
            
            # 指数退避
            delay = 2 ** step.retry_count
            threading.Timer(delay, self._execute_step, args=(saga, step)).start()
        else:
            # 开始补偿事务
            print(f"Saga步骤失败，开始补偿: {saga.saga_id} - {step.action_name}")
            saga.status = SagaStatus.COMPENSATING
            self._start_compensation(saga)
    
    def _start_compensation(self, saga: SagaTransaction):
        """开始补偿事务"""
        # 找到最后一个成功执行的步骤
        completed_steps = [step for step in saga.steps if step.status == "completed"]
        
        if completed_steps:
            # 从后往前补偿
            last_successful_step = completed_steps[-1]
            self._compensate_step(saga, last_successful_step)
        else:
            # 没有成功步骤，标记为补偿完成
            saga.status = SagaStatus.COMPENSATED
            saga.end_time = datetime.utcnow()
            saga.error_message = "所有步骤都补偿完成"
    
    def _compensate_step(self, saga: SagaTransaction, step: SagaStep):
        """补偿Saga步骤"""
        step.status = "compensating"
        print(f"执行补偿步骤: {saga.saga_id} - {step.compensate_name}")
        
        # 发送补偿开始事件
        self._send_saga_event("saga.compensation_started", {
            "saga_id": saga.saga_id,
            "step_id": step.step_id,
            "compensate_name": step.compensate_name
        })
        
        if step.compensate_name in self.compensate_handlers:
            try:
                # 调用补偿处理器
                result = self.compensate_handlers[step.compensate_name](step.compensate_data)
                
                if result.get("success", True):
                    step.status = "compensated"
                    self._advance_compensation(saga)
                else:
                    step.status = "failed"
                    print(f"补偿步骤失败: {saga.saga_id} - {step.compensate_name}")
                    
            except Exception as e:
                step.status = "failed"
                print(f"补偿步骤异常: {saga.saga_id} - {step.compensate_name} - {e}")
        else:
            step.status = "compensated"
            print(f"未找到补偿处理器，标记为已补偿: {step.compensate_name}")
            self._advance_compensation(saga)
    
    def _advance_compensation(self, saga: SagaTransaction):
        """推进补偿事务"""
        # 找到下一个需要补偿的步骤
        steps_to_compensate = [step for step in saga.steps if step.status == "completed"]
        
        if steps_to_compensate:
            # 继续补偿
            next_step = steps_to_compensate[-1]
            self._compensate_step(saga, next_step)
        else:
            # 补偿完成
            saga.status = SagaStatus.COMPENSATED
            saga.end_time = datetime.utcnow()
            
            # 发送补偿完成事件
            self._send_saga_event("saga.compensated", {
                "saga_id": saga.saga_id,
                "duration": (saga.end_time - saga.start_time).total_seconds()
            })
            
            print(f"Saga {saga.saga_id} 补偿完成")
    
    def _send_saga_event(self, event_type: str, event_data: dict):
        """发送Saga事件"""
        routing_key = f"saga.events.{event_type}"
        
        self.connector.channel.basic_publish(
            exchange="saga_bus",
            routing_key=routing_key,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            ),
            body=json.dumps(event_data)
        )


class MicroserviceBus:
    """微服务总线 - 整合所有消息模式"""
    
    def __init__(self, host: str = 'localhost', port: int = 5672):
        self.connector = MessageConnector(host, port)
        self.request_response = None
        self.publish_subscribe = None
        self.work_queue = None
        self.event_driven = None
        self.saga_pattern = None
        
        # 服务健康状态
        self.service_status = ServiceStatus.HEALTHY
        
    def initialize(self):
        """初始化微服务总线"""
        # 建立连接
        self.connector.connect()
        
        # 初始化各种模式
        self.request_response = RequestResponsePattern(self.connector, "microservice_bus")
        self.publish_subscribe = PublishSubscribePattern(self.connector)
        self.work_queue = WorkQueuePattern(self.connector, "microservice_queue", 4)
        self.event_driven = EventDrivenArchitecture(self.connector)
        self.saga_pattern = SagaPattern(self.connector)
        
        # 设置各种模式
        self.request_response.setup()
        self.publish_subscribe.setup()
        self.work_queue.setup()
        self.event_driven.setup()
        self.saga_pattern.setup()
        
        print("微服务总线初始化完成")
    
    def register_request_handler(self, handler: Callable):
        """注册请求处理器"""
        self.request_response.handle_request(handler)
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """注册事件处理器"""
        self.event_driven.register_event_handler(event_type, handler)
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.work_queue.register_task_handler(task_type, handler)
    
    def register_action_handler(self, action_name: str, handler: Callable):
        """注册Saga动作处理器"""
        self.saga_pattern.register_action_handler(action_name, handler)
    
    def register_compensate_handler(self, compensate_name: str, handler: Callable):
        """注册Saga补偿处理器"""
        self.saga_pattern.register_compensate_handler(compensate_name, handler)
    
    def start(self):
        """启动微服务总线"""
        # 启动工作队列
        self.work_queue.start_workers()
        
        # 启动消费线程
        consumer_thread = threading.Thread(target=self._consume_messages)
        consumer_thread.daemon = True
        consumer_thread.start()
        
        print("微服务总线已启动")
    
    def _consume_messages(self):
        """消费消息"""
        try:
            self.connector.channel.start_consuming()
        except KeyboardInterrupt:
            self.connector.channel.stop_consuming()
    
    async def send_request(self, method: str, params: dict, timeout: int = 30) -> dict:
        """发送请求"""
        return await self.request_response.call(method, params, timeout)
    
    def publish_event(self, event: Event):
        """发布事件"""
        self.publish_subscribe.publish(event)
        self.event_driven.save_event(event)
    
    def submit_task(self, task_type: str, params: dict, priority: int = 0):
        """提交任务"""
        self.work_queue.submit_task(task_type, params, priority)
    
    def create_saga(self, saga_id: str, steps: List[dict]) -> SagaTransaction:
        """创建Saga事务"""
        return self.saga_pattern.create_saga(saga_id, steps)
    
    def execute_saga(self, saga: SagaTransaction):
        """执行Saga事务"""
        self.saga_pattern.execute_saga(saga)
    
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态"""
        return self.service_status
    
    def health_check(self) -> dict:
        """健康检查"""
        status_info = {
            "status": self.service_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "connection": "connected" if self.connector.connection and 
                        not self.connector.connection.is_closed else "disconnected"
        }
        
        return status_info
    
    def shutdown(self):
        """关闭微服务总线"""
        print("正在关闭微服务总线...")
        self.connector.close()


# 示例使用代码
async def example_usage():
    """使用示例"""
    
    # 创建微服务总线
    bus = MicroserviceBus("localhost")
    bus.initialize()
    
    # 注册各种处理器
    
    # 请求-响应处理器
    def handle_request(method: str, params: dict) -> dict:
        if method == "get_user":
            return {"user_id": params.get("user_id"), "name": "张三", "email": "user@example.com"}
        elif method == "create_order":
            return {"order_id": f"order_{uuid.uuid4().hex[:8]}", "status": "created"}
        else:
            return {"error": f"未知方法: {method}"}
    
    bus.register_request_handler(handle_request)
    
    # 事件处理器
    def handle_user_registered(event: Event):
        print(f"处理用户注册事件: {event.aggregate_id}")
    
    bus.register_event_handler(EventType.USER_REGISTERED, handle_user_registered)
    
    # 任务处理器
    def send_email(email: str, subject: str, content: str):
        print(f"发送邮件: {email} - {subject}")
        return {"success": True}
    
    bus.register_task_handler("send_email", send_email)
    
    # Saga处理器
    def create_order_action(data: dict) -> dict:
        print(f"创建订单: {data}")
        return {"success": True, "order_id": "order_123"}
    
    def reserve_inventory_action(data: dict) -> dict:
        print(f"预留库存: {data}")
        return {"success": True}
    
    bus.register_action_handler("create_order", create_order_action)
    bus.register_action_handler("reserve_inventory", reserve_inventory_action)
    
    def cancel_order_compensate(data: dict) -> dict:
        print(f"取消订单补偿: {data}")
        return {"success": True}
    
    bus.register_compensate_handler("cancel_order", cancel_order_compensate)
    
    # 启动总线
    bus.start()
    
    # 使用各种模式
    
    # 1. 请求-响应模式
    try:
        result = await bus.send_request("get_user", {"user_id": "123"})
        print(f"请求响应结果: {result}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 发布-订阅模式
    event = Event(
        event_id=str(uuid.uuid4()),
        event_type=EventType.USER_REGISTERED,
        aggregate_id="user_123",
        data={"email": "user@example.com", "name": "张三"},
        timestamp=datetime.utcnow()
    )
    bus.publish_event(event)
    
    # 3. 工作队列模式
    bus.submit_task("send_email", {
        "email": "user@example.com",
        "subject": "欢迎注册",
        "content": "欢迎加入我们的平台"
    })
    
    # 4. Saga事务模式
    saga_steps = [
        {
            "step_id": "create_order",
            "action_name": "create_order",
            "compensate_name": "cancel_order",
            "action_data": {"items": ["item1", "item2"]},
            "compensate_data": {"order_id": "order_123"}
        },
        {
            "step_id": "reserve_inventory",
            "action_name": "reserve_inventory",
            "compensate_name": "cancel_order",
            "action_data": {"items": ["item1", "item2"]},
            "compensate_data": {}
        }
    ]
    
    saga = bus.create_saga("order_saga_123", saga_steps)
    bus.execute_saga(saga)
    
    # 保持程序运行
    try:
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        bus.shutdown()


if __name__ == "__main__":
    asyncio.run(example_usage())