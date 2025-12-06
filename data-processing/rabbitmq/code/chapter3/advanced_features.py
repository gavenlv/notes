#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ 高级特性示例
================

本文件演示了RabbitMQ的多种高级特性，包括：
- 消息确认机制
- 持久化策略
- 死信队列
- 消息TTL
- 优先级队列
- 集群配置
- 消息幂等性
- 安全配置
- 性能优化

作者: RabbitMQ学习团队
版本: 1.0.0
"""

import pika
import json
import time
import threading
import uuid
import hashlib
import logging
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
import redis
import structlog

# 配置结构化日志
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

class DeliveryMode(Enum):
    """消息传递模式"""
    NON_PERSISTENT = 1
    PERSISTENT = 2

class AckMode(Enum):
    """确认模式"""
    AUTO = "auto"
    MANUAL = "manual"
    NONE = "none"

@dataclass
class MessageProperties:
    """消息属性"""
    delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    priority: int = 0
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    timestamp: Optional[datetime] = None
    expiration: Optional[str] = None
    type: Optional[str] = None
    user_id: Optional[str] = None
    app_id: Optional[str] = None

class ConnectionManager:
    """连接管理器"""
    
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self._lock = threading.Lock()
    
    def connect(self, use_ssl=False, ssl_options=None):
        """建立连接"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
                connection_attempts=3,
                retry_delay=5
            )
            
            if use_ssl:
                parameters.ssl_options = pika.SSLOptions(**ssl_options)
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"RabbitMQ连接建立成功: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"RabbitMQ连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("RabbitMQ连接已断开")
        except Exception as e:
            logger.error(f"断开连接时发生错误: {e}")
    
    @contextmanager
    def get_channel(self):
        """获取通道上下文管理器"""
        channel = None
        try:
            if not self.channel or self.channel.is_closed:
                if not self.connection or self.connection.is_closed:
                    self.connect()
                self.channel = self.connection.channel()
            channel = self.channel
            yield channel
        except Exception as e:
            logger.error(f"通道操作失败: {e}")
            raise

class AcknowledgmentExamples:
    """消息确认机制示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
        self.auto_ack_enabled = False
    
    def setup_queues(self):
        """设置演示队列"""
        with self.cm.get_channel() as channel:
            # 手动确认队列
            channel.queue_declare(queue='manual_ack_queue', durable=True)
            # 自动确认队列
            channel.queue_declare(queue='auto_ack_queue', durable=True)
            
            logger.info("确认机制演示队列创建完成")
    
    def send_messages_with_manual_ack(self):
        """发送消息到手动确认队列"""
        with self.cm.get_channel() as channel:
            # 启用发布者确认
            channel.confirm_delivery()
            
            messages = [
                {"id": 1, "content": "第一条消息"},
                {"id": 2, "content": "第二条消息"},
                {"id": 3, "content": "第三条消息"}
            ]
            
            for message in messages:
                try:
                    properties = MessageProperties(
                        message_id=str(message["id"]),
                        correlation_id=str(uuid.uuid4()),
                        timestamp=datetime.now()
                    )
                    
                    channel.basic_publish(
                        exchange='amq.direct',
                        routing_key='manual_ack_queue',
                        body=json.dumps(message),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            message_id=properties.message_id,
                            correlation_id=properties.correlation_id,
                            timestamp=properties.timestamp,
                            priority=properties.priority
                        ),
                        mandatory=True
                    )
                    logger.info(f"消息已发送: {message['id']}")
                    
                except pika.exceptions.NackError:
                    logger.error(f"消息发送失败 (未确认): {message['id']}")
                except Exception as e:
                    logger.error(f"消息发送失败: {message['id']}, 错误: {e}")
    
    def consume_messages_manual_ack(self):
        """手动确认消费者"""
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode('utf-8'))
                logger.info(f"收到消息: {message['id']}, 内容: {message['content']}")
                
                # 模拟消息处理时间
                time.sleep(2)
                
                # 模拟处理成功，手动确认
                logger.info(f"消息处理完成: {message['id']}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"消息处理失败: {e}")
                # 处理失败时，可以选择重新入队或丢弃
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with self.cm.get_channel() as channel:
            channel.basic_qos(prefetch_count=1)  # 一次只处理一条消息
            channel.basic_consume(
                queue='manual_ack_queue',
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("手动确认消费者启动，等待消息...")
            channel.start_consuming()
    
    def consume_messages_auto_ack(self):
        """自动确认消费者"""
        def callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))
            logger.info(f"自动确认收到消息: {message['id']}, 内容: {message['content']}")
            
            # 模拟消息处理时间
            time.sleep(1)
            logger.info(f"自动确认消息处理完成: {message['id']}")
        
        with self.cm.get_channel() as channel:
            channel.basic_consume(
                queue='auto_ack_queue',
                on_message_callback=callback,
                auto_ack=True  # 自动确认
            )
            
            logger.info("自动确认消费者启动，等待消息...")
            channel.start_consuming()
    
    def demonstrate_prefetch_count(self):
        """演示预取数量控制"""
        def callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))
            logger.info(f"收到消息: {message}")
            
            # 模拟处理时间
            processing_time = message.get('processing_time', 1)
            time.sleep(processing_time)
            
            # 手动确认
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        with self.cm.get_channel() as channel:
            # 设置预取数量为3
            channel.basic_qos(prefetch_count=3)
            channel.basic_consume(
                queue='manual_ack_queue',
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("预取数量演示消费者启动（预取=3）...")
            channel.start_consuming()

class PersistenceExamples:
    """持久化策略示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
    
    def setup_persistent_queues(self):
        """设置持久化队列和交换机"""
        with self.cm.get_channel() as channel:
            # 声明持久化交换机
            channel.exchange_declare(
                exchange='durable_exchange',
                exchange_type='direct',
                durable=True
            )
            
            # 声明持久化队列
            channel.queue_declare(queue='durable_queue', durable=True)
            
            # 绑定交换机和队列
            channel.queue_bind(
                exchange='durable_exchange',
                queue='durable_queue',
                routing_key='persistent_key'
            )
            
            logger.info("持久化队列和交换机创建完成")
    
    def send_persistent_messages(self):
        """发送持久化消息"""
        messages = [
            {
                "id": str(uuid.uuid4()),
                "content": "重要业务数据1",
                "timestamp": datetime.now().isoformat(),
                "priority": "high"
            },
            {
                "id": str(uuid.uuid4()),
                "content": "重要业务数据2", 
                "timestamp": datetime.now().isoformat(),
                "priority": "medium"
            },
            {
                "id": str(uuid.uuid4()),
                "content": "重要业务数据3",
                "timestamp": datetime.now().isoformat(),
                "priority": "low"
            }
        ]
        
        with self.cm.get_channel() as channel:
            # 启用发布者确认
            channel.confirm_delivery()
            
            for message in messages:
                try:
                    properties = pika.BasicProperties(
                        delivery_mode=2,  # 消息持久化
                        message_id=message["id"],
                        timestamp=datetime.now(),
                        priority=1 if message["priority"] == "high" else 0
                    )
                    
                    channel.basic_publish(
                        exchange='durable_exchange',
                        routing_key='persistent_key',
                        body=json.dumps(message),
                        properties=properties,
                        mandatory=True
                    )
                    
                    logger.info(f"持久化消息发送成功: {message['id']}")
                    
                except pika.exceptions.NackError:
                    logger.error(f"持久化消息发送失败（未确认）: {message['id']}")
                except Exception as e:
                    logger.error(f"持久化消息发送失败: {message['id']}, 错误: {e}")
    
    def check_queue_persistence(self):
        """检查队列持久化状态"""
        with self.cm.get_channel() as channel:
            try:
                # 获取队列信息
                result = channel.queue_declare(queue='durable_queue', passive=True)
                queue_info = {
                    'queue': result.method.queue,
                    'message_count': result.method.message_count,
                    'consumer_count': result.method.consumer_count
                }
                
                logger.info(f"持久化队列状态: {queue_info}")
                return queue_info
                
            except Exception as e:
                logger.error(f"获取队列信息失败: {e}")
                return None

class DeadLetterQueueExamples:
    """死信队列示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
    
    def setup_dead_letter_queues(self):
        """设置死信队列"""
        with self.cm.get_channel() as channel:
            # 声明死信交换机
            channel.exchange_declare(
                exchange='dlx_exchange',
                exchange_type='direct',
                durable=True
            )
            
            # 声明死信队列
            channel.queue_declare(queue='dead_letter_queue', durable=True)
            
            # 绑定死信交换机到死信队列
            channel.queue_bind(
                exchange='dlx_exchange',
                queue='dead_letter_queue',
                routing_key='dead_letter'
            )
            
            # 声明主队列（配置死信属性）
            channel.queue_declare(
                queue='main_queue_with_dlx',
                durable=True,
                arguments={
                    'x-dead-letter-exchange': 'dlx_exchange',
                    'x-dead-letter-routing-key': 'dead_letter',
                    'x-message-ttl': 10000,  # 10秒TTL
                    'x-max-priority': 5,
                    'x-max-length': 10  # 最大队列长度
                }
            )
            
            logger.info("死信队列设置完成")
    
    def send_messages_that_will_fail(self):
        """发送会失败的消息"""
        with self.cm.get_channel() as channel:
            test_messages = [
                {"id": "1", "content": "正常消息"},
                {"id": "2", "content": "将要失败的消息"},
                {"id": "3", "content": "另一个要失败的消息"}
            ]
            
            for message in test_messages:
                try:
                    properties = pika.BasicProperties(
                        delivery_mode=2,
                        message_id=message["id"],
                        timestamp=datetime.now(),
                        expiration='5000'  # 5秒后过期
                    )
                    
                    channel.basic_publish(
                        exchange='amq.direct',
                        routing_key='main_queue_with_dlx',
                        body=json.dumps(message),
                        properties=properties
                    )
                    
                    logger.info(f"消息已发送到主队列: {message['id']}")
                    
                except Exception as e:
                    logger.error(f"发送消息失败: {e}")
    
    def consume_and_reject_messages(self):
        """消费消息并拒绝"""
        def callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))
            message_id = message.get('id')
            
            logger.info(f"收到消息: {message_id}")
            
            try:
                # 模拟处理逻辑
                if message_id == "2":
                    # 模拟处理失败，拒绝消息
                    logger.error(f"消息处理失败，拒绝: {message_id}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                elif message_id == "3":
                    # 模拟处理失败，但重新入队
                    logger.error(f"消息处理失败，重新入队: {message_id}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                else:
                    # 处理成功
                    logger.info(f"消息处理成功: {message_id}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
            except Exception as e:
                logger.error(f"处理消息时发生异常: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with self.cm.get_channel() as channel:
            channel.basic_consume(
                queue='main_queue_with_dlx',
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("死信队列演示消费者启动...")
            channel.start_consuming()
    
    def consume_dead_letter_messages(self):
        """消费死信队列中的消息"""
        def callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))
            
            # 获取原始消息属性
            original_exchange = properties.headers.get('x-death', [{}])[0].get('exchange', 'unknown')
            original_routing_key = properties.headers.get('x-death', [{}])[0].get('routing-keys', ['unknown'])[0]
            
            logger.info(f"收到死信消息: {message['id']}")
            logger.info(f"死信原因: 原始交换机={original_exchange}, 原始路由键={original_routing_key}")
            logger.info(f"死信时间戳: {properties.timestamp}")
            
            # 确认死信消息处理完成
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        with self.cm.get_channel() as channel:
            channel.basic_consume(
                queue='dead_letter_queue',
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("死信队列消费者启动...")
            channel.start_consuming()

class TTLExamples:
    """TTL示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
    
    def setup_ttl_queues(self):
        """设置TTL队列"""
        with self.cm.get_channel() as channel:
            # 队列级TTL - 所有消息30秒后过期
            channel.queue_declare(
                queue='queue_ttl_30s',
                arguments={
                    'x-message-ttl': 30000
                }
            )
            
            # 队列级TTL - 所有消息60秒后过期
            channel.queue_declare(
                queue='queue_ttl_60s',
                arguments={
                    'x-message-ttl': 60000
                }
            )
            
            # 无TTL的普通队列
            channel.queue_declare(queue='no_ttl_queue', durable=True)
            
            logger.info("TTL队列设置完成")
    
    def send_ttl_messages(self):
        """发送TTL消息"""
        with self.cm.get_channel() as channel:
            # 发送队列级TTL消息（30秒）
            for i in range(3):
                message = {
                    "id": f"queue_ttl_{i}",
                    "content": f"队列TTL消息 {i}",
                    "timestamp": datetime.now().isoformat()
                }
                
                channel.basic_publish(
                    exchange='amq.direct',
                    routing_key='queue_ttl_30s',
                    body=json.dumps(message)
                )
                logger.info(f"发送队列TTL消息: {i}")
            
            # 发送消息级TTL消息（5秒）
            properties = pika.BasicProperties(
                expiration='5000'  # 5秒后过期
            )
            
            message = {
                "id": "message_ttl_5s",
                "content": "消息级TTL消息",
                "timestamp": datetime.now().isoformat()
            }
            
            channel.basic_publish(
                exchange='amq.direct',
                routing_key='queue_ttl_30s',
                body=json.dumps(message),
                properties=properties
            )
            logger.info("发送消息级TTL消息（5秒过期）")

class PriorityQueueExamples:
    """优先级队列示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
    
    def setup_priority_queues(self):
        """设置优先级队列"""
        with self.cm.get_channel() as channel:
            # 最大优先级为10的队列
            channel.queue_declare(
                queue='priority_queue',
                durable=True,
                arguments={
                    'x-max-priority': 10
                }
            )
            
            logger.info("优先级队列设置完成")
    
    def send_priority_messages(self):
        """发送优先级消息"""
        with self.cm.get_channel() as channel:
            # 高优先级消息 (优先级9)
            high_priority_message = {
                "id": "high_priority_001",
                "content": "高优先级消息 - 紧急修复",
                "timestamp": datetime.now().isoformat()
            }
            
            properties = pika.BasicProperties(priority=9)
            
            channel.basic_publish(
                exchange='amq.direct',
                routing_key='priority_queue',
                body=json.dumps(high_priority_message),
                properties=properties
            )
            logger.info("发送高优先级消息")
            
            # 普通优先级消息 (优先级1)
            normal_messages = [
                {"id": f"normal_{i}", "content": f"普通优先级消息 {i}", "timestamp": datetime.now().isoformat()}
                for i in range(5)
            ]
            
            for message in normal_messages:
                properties = pika.BasicProperties(priority=1)
                channel.basic_publish(
                    exchange='amq.direct',
                    routing_key='priority_queue',
                    body=json.dumps(message),
                    properties=properties
                )
            
            logger.info(f"发送{len(normal_messages)}条普通优先级消息")
    
    def consume_priority_messages(self):
        """消费优先级消息"""
        def callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))
            priority = properties.priority
            
            logger.info(f"收到消息 - ID: {message['id']}, 优先级: {priority}, 内容: {message['content']}")
            
            # 模拟处理时间
            time.sleep(1)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        with self.cm.get_channel() as channel:
            # 设置预取数量，确保按优先级顺序处理
            channel.basic_qos(prefetch_count=1)
            
            channel.basic_consume(
                queue='priority_queue',
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("优先级队列消费者启动...")
            channel.start_consuming()

class IdempotencyExamples:
    """消息幂等性示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.processed_messages = set()
    
    def setup_idempotency_queues(self):
        """设置幂等性队列"""
        with self.cm.get_channel() as channel:
            channel.queue_declare(queue='idempotency_queue', durable=True)
            
            logger.info("幂等性队列设置完成")
    
    def is_message_processed(self, message_id: str) -> bool:
        """检查消息是否已经处理过"""
        # 检查内存缓存
        if message_id in self.processed_messages:
            return True
        
        # 检查Redis缓存
        if self.redis_client.exists(f"processed_message:{message_id}"):
            return True
        
        return False
    
    def mark_message_as_processed(self, message_id: str, ttl: int = 3600):
        """标记消息为已处理"""
        # 添加到内存缓存
        self.processed_messages.add(message_id)
        
        # 添加到Redis缓存（带TTL）
        self.redis_client.setex(
            f"processed_message:{message_id}",
            ttl,
            "processed"
        )
        
        # 清理内存缓存（防止无限增长）
        if len(self.processed_messages) > 1000:
            self.processed_messages.clear()
    
    def send_idempotent_messages(self):
        """发送需要幂等性处理的消息"""
        with self.cm.get_channel() as channel:
            # 重复发送相同的消息（模拟重复消息场景）
            base_message = {
                "id": "order_123",
                "content": "创建订单操作",
                "order_id": "ORD-2024-001",
                "amount": 1000,
                "timestamp": datetime.now().isoformat()
            }
            
            # 发送多次相同消息
            for i in range(5):
                message = base_message.copy()
                message["send_time"] = datetime.now().isoformat()
                message["sequence"] = i + 1
                
                channel.basic_publish(
                    exchange='amq.direct',
                    routing_key='idempotency_queue',
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        message_id=base_message["id"],  # 相同的消息ID
                        delivery_mode=2
                    )
                )
                
                logger.info(f"发送幂等性消息 #{i+1}")
    
    def consume_idempotent_messages(self):
        """消费幂等性消息"""
        def callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))
            message_id = message.get('id')
            sequence = message.get('sequence', 1)
            
            logger.info(f"尝试处理消息 #{sequence}: {message_id}")
            
            try:
                # 检查消息是否已经处理过
                if self.is_message_processed(message_id):
                    logger.info(f"消息 {message_id} 已经处理过，跳过")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                # 模拟消息处理逻辑
                logger.info(f"处理消息: {message_id}, 内容: {message['content']}")
                time.sleep(2)  # 模拟处理时间
                
                # 标记消息为已处理
                self.mark_message_as_processed(message_id)
                logger.info(f"消息 {message_id} 处理完成并标记")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"处理消息时发生错误: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with self.cm.get_channel() as channel:
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue='idempotency_queue',
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("幂等性消费者启动...")
            channel.start_consuming()

class SecurityExamples:
    """安全配置示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
    
    def setup_secure_connection(self):
        """设置安全连接"""
        try:
            # SSL配置
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.load_verify_locations('/path/to/ca-cert.pem')
            ssl_context.load_cert_chain('/path/to/client-cert.pem', '/path/to/client-key.pem')
            
            ssl_options = {
                'cert_reqs': ssl.CERT_REQUIRED,
                'ssl_options': ssl_context
            }
            
            # 连接（需要证书）
            self.cm.connect(use_ssl=True, ssl_options=ssl_options)
            logger.info("安全连接建立成功")
            
        except Exception as e:
            logger.error(f"安全连接失败: {e}")
            raise
    
    def authenticate_and_authorize(self):
        """认证和授权示例"""
        try:
            # 创建具有特定权限的用户
            with self.cm.get_channel() as channel:
                # 检查用户权限
                result = channel.queue_declare(queue='secure_queue', durable=True)
                
                # 声明交换机时检查权限
                channel.exchange_declare(
                    exchange='secure_exchange',
                    exchange_type='topic',
                    durable=True
                )
                
                logger.info("认证和授权验证成功")
                
        except Exception as e:
            logger.error(f"认证授权失败: {e}")
            raise

class MonitoringExamples:
    """监控示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
        self.monitoring_stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_failed': 0,
            'processing_times': [],
            'errors': []
        }
    
    def monitor_queue_status(self, queue_name: str) -> Dict[str, Any]:
        """监控队列状态"""
        try:
            with self.cm.get_channel() as channel:
                result = channel.queue_declare(queue=queue_name, passive=True)
                
                queue_stats = {
                    'queue_name': queue_name,
                    'message_count': result.method.message_count,
                    'consumer_count': result.method.consumer_count,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"队列状态监控: {queue_stats}")
                return queue_stats
                
        except Exception as e:
            logger.error(f"队列状态监控失败: {e}")
            return {'error': str(e)}
    
    def track_message_metrics(self, message_id: str, processing_time: float, success: bool):
        """跟踪消息指标"""
        if success:
            self.monitoring_stats['messages_received'] += 1
            self.monitoring_stats['processing_times'].append(processing_time)
        else:
            self.monitoring_stats['messages_failed'] += 1
            self.monitoring_stats['errors'].append({
                'message_id': message_id,
                'error_time': datetime.now().isoformat()
            })
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        processing_times = self.monitoring_stats['processing_times']
        
        stats = {
            'total_messages_processed': self.monitoring_stats['messages_received'],
            'total_messages_failed': self.monitoring_stats['messages_failed'],
            'average_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'recent_errors': self.monitoring_stats['errors'][-10:],  # 最近10个错误
            'success_rate': (
                self.monitoring_stats['messages_received'] / 
                max(1, self.monitoring_stats['messages_received'] + self.monitoring_stats['messages_failed'])
            ) * 100
        }
        
        logger.info(f"处理统计信息: {stats}")
        return stats

class BatchProcessingExamples:
    """批处理示例"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.cm = connection_manager
        self.batch_size = 10
        self.batch_timeout = 30  # 30秒
        self.pending_messages = []
        self.last_batch_time = time.time()
    
    def setup_batch_queues(self):
        """设置批处理队列"""
        with self.cm.get_channel() as channel:
            channel.queue_declare(queue='batch_processing_queue', durable=True)
            
            logger.info("批处理队列设置完成")
    
    def add_to_batch(self, message_data: Dict[str, Any]) -> bool:
        """添加消息到批处理"""
        self.pending_messages.append(message_data)
        
        # 检查是否达到批处理条件
        if (len(self.pending_messages) >= self.batch_size or 
            time.time() - self.last_batch_time > self.batch_timeout):
            return self.process_batch()
        
        return False
    
    def process_batch(self) -> bool:
        """处理批次"""
        if not self.pending_messages:
            return False
        
        batch = self.pending_messages.copy()
        self.pending_messages.clear()
        self.last_batch_time = time.time()
        
        try:
            logger.info(f"开始批处理 {len(batch)} 条消息")
            
            # 模拟批处理逻辑
            for message in batch:
                # 这里应该是实际的批处理逻辑
                time.sleep(0.1)  # 模拟处理时间
            
            logger.info(f"批处理完成，成功处理 {len(batch)} 条消息")
            return True
            
        except Exception as e:
            logger.error(f"批处理失败: {e}")
            # 将消息重新加入待处理队列
            self.pending_messages.extend(batch)
            return False
    
    def send_batch_messages(self):
        """发送批处理消息"""
        with self.cm.get_channel() as channel:
            for i in range(15):  # 发送15条消息（超过批处理大小10）
                message = {
                    "id": f"batch_{i}",
                    "content": f"批处理消息 {i}",
                    "timestamp": datetime.now().isoformat()
                }
                
                if not self.add_to_batch(message):
                    # 如果没有触发批处理，手动发送到队列
                    channel.basic_publish(
                        exchange='amq.direct',
                        routing_key='batch_processing_queue',
                        body=json.dumps(message)
                    )
            
            # 确保剩余消息被处理
            self.process_batch()

class MainApplication:
    """主应用程序"""
    
    def __init__(self):
        # 初始化连接管理器
        self.connection_manager = ConnectionManager(
            host='localhost',
            port=5672,
            username='guest',
            password='guest'
        )
        
        # 初始化各种示例
        self.ack_examples = AcknowledgmentExamples(self.connection_manager)
        self.persistence_examples = PersistenceExamples(self.connection_manager)
        self.dlx_examples = DeadLetterQueueExamples(self.connection_manager)
        self.ttl_examples = TTLExamples(self.connection_manager)
        self.priority_examples = PriorityQueueExamples(self.connection_manager)
        self.idempotency_examples = IdempotencyExamples(self.connection_manager)
        self.security_examples = SecurityExamples(self.connection_manager)
        self.monitoring_examples = MonitoringExamples(self.connection_manager)
        self.batch_examples = BatchProcessingExamples(self.connection_manager)
    
    def connect_to_rabbitmq(self) -> bool:
        """连接到RabbitMQ"""
        logger.info("正在连接到RabbitMQ...")
        return self.connection_manager.connect()
    
    def run_acknowledgment_demo(self):
        """运行消息确认演示"""
        logger.info("=== 消息确认机制演示 ===")
        
        try:
            # 设置队列
            self.ack_examples.setup_queues()
            
            # 发送消息
            self.ack_examples.send_messages_with_manual_ack()
            
            # 启动消费者（在实际使用中，消费者应该在单独线程中运行）
            # self.ack_examples.consume_messages_manual_ack()
            
            logger.info("消息确认演示完成")
            
        except KeyboardInterrupt:
            logger.info("演示被用户中断")
        except Exception as e:
            logger.error(f"消息确认演示失败: {e}")
    
    def run_persistence_demo(self):
        """运行持久化演示"""
        logger.info("=== 持久化策略演示 ===")
        
        try:
            # 设置持久化队列
            self.persistence_examples.setup_persistent_queues()
            
            # 发送持久化消息
            self.persistence_examples.send_persistent_messages()
            
            # 检查队列状态
            self.persistence_examples.check_queue_persistence()
            
            logger.info("持久化演示完成")
            
        except Exception as e:
            logger.error(f"持久化演示失败: {e}")
    
    def run_dlx_demo(self):
        """运行死信队列演示"""
        logger.info("=== 死信队列演示 ===")
        
        try:
            # 设置死信队列
            self.dlx_examples.setup_dead_letter_queues()
            
            # 发送会失败的消息
            self.dlx_examples.send_messages_that_will_fail()
            
            # 启动消费者（在实际使用中应该在单独线程中运行）
            # self.dlx_examples.consume_and_reject_messages()
            # self.dlx_examples.consume_dead_letter_messages()
            
            logger.info("死信队列演示完成")
            
        except Exception as e:
            logger.error(f"死信队列演示失败: {e}")
    
    def run_ttl_demo(self):
        """运行TTL演示"""
        logger.info("=== TTL演示 ===")
        
        try:
            # 设置TTL队列
            self.ttl_examples.setup_ttl_queues()
            
            # 发送TTL消息
            self.ttl_examples.send_ttl_messages()
            
            # 等待消息过期（实际演示中可能需要较长时间）
            logger.info("TTL消息已发送，请等待观察消息过期效果")
            
        except Exception as e:
            logger.error(f"TTL演示失败: {e}")
    
    def run_priority_demo(self):
        """运行优先级队列演示"""
        logger.info("=== 优先级队列演示 ===")
        
        try:
            # 设置优先级队列
            self.priority_examples.setup_priority_queues()
            
            # 发送优先级消息
            self.priority_examples.send_priority_messages()
            
            # 启动消费者（在实际使用中应该在单独线程中运行）
            # self.priority_examples.consume_priority_messages()
            
            logger.info("优先级队列演示完成")
            
        except Exception as e:
            logger.error(f"优先级队列演示失败: {e}")
    
    def run_idempotency_demo(self):
        """运行幂等性演示"""
        logger.info("=== 消息幂等性演示 ===")
        
        try:
            # 设置幂等性队列
            self.idempotency_examples.setup_idempotency_queues()
            
            # 发送重复消息
            self.idempotency_examples.send_idempotent_messages()
            
            # 启动消费者（在实际使用中应该在单独线程中运行）
            # self.idempotency_examples.consume_idempotent_messages()
            
            logger.info("幂等性演示完成")
            
        except Exception as e:
            logger.error(f"幂等性演示失败: {e}")
    
    def run_monitoring_demo(self):
        """运行监控演示"""
        logger.info("=== 监控演示 ===")
        
        try:
            # 模拟监控多个队列
            queues_to_monitor = ['manual_ack_queue', 'auto_ack_queue', 'durable_queue']
            
            for queue in queues_to_monitor:
                status = self.monitoring_examples.monitor_queue_status(queue)
                logger.info(f"队列 {queue} 状态: {status}")
            
            # 模拟处理统计
            for i in range(10):
                success = i % 3 != 0  # 1/3的消息处理失败
                processing_time = 1.0 + (i % 3) * 0.5  # 处理时间1-2秒
                self.monitoring_examples.track_message_metrics(
                    f"msg_{i}", 
                    processing_time, 
                    success
                )
            
            # 获取统计信息
            stats = self.monitoring_examples.get_processing_statistics()
            logger.info(f"最终统计: {stats}")
            
        except Exception as e:
            logger.error(f"监控演示失败: {e}")
    
    def run_batch_demo(self):
        """运行批处理演示"""
        logger.info("=== 批处理演示 ===")
        
        try:
            # 设置批处理队列
            self.batch_examples.setup_batch_queues()
            
            # 发送批处理消息
            self.batch_examples.send_batch_messages()
            
            logger.info("批处理演示完成")
            
        except Exception as e:
            logger.error(f"批处理演示失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        logger.info("正在清理资源...")
        self.connection_manager.disconnect()
    
    def run_interactive_demo(self):
        """运行交互式演示"""
        """运行交互式演示"""
        print("\n" + "="*50)
        print("    RabbitMQ 高级特性演示程序")
        print("="*50)
        print("请选择要运行的演示:")
        print("1. 消息确认机制")
        print("2. 持久化策略")
        print("3. 死信队列")
        print("4. 消息TTL")
        print("5. 优先级队列")
        print("6. 消息幂等性")
        print("7. 监控示例")
        print("8. 批处理")
        print("9. 运行所有演示")
        print("0. 退出")
        print("-"*50)
        
        while True:
            try:
                choice = input("请输入选择 (0-9): ").strip()
                
                if choice == '0':
                    print("感谢使用RabbitMQ高级特性演示程序！")
                    break
                elif choice == '1':
                    self.run_acknowledgment_demo()
                elif choice == '2':
                    self.run_persistence_demo()
                elif choice == '3':
                    self.run_dlx_demo()
                elif choice == '4':
                    self.run_ttl_demo()
                elif choice == '5':
                    self.run_priority_demo()
                elif choice == '6':
                    self.run_idempotency_demo()
                elif choice == '7':
                    self.run_monitoring_demo()
                elif choice == '8':
                    self.run_batch_demo()
                elif choice == '9':
                    print("运行所有演示...")
                    self.run_acknowledgment_demo()
                    time.sleep(2)
                    self.run_persistence_demo()
                    time.sleep(2)
                    self.run_dlx_demo()
                    time.sleep(2)
                    self.run_ttl_demo()
                    time.sleep(2)
                    self.run_priority_demo()
                    time.sleep(2)
                    self.run_idempotency_demo()
                    time.sleep(2)
                    self.run_monitoring_demo()
                    time.sleep(2)
                    self.run_batch_demo()
                    print("所有演示完成！")
                else:
                    print("无效选择，请重新输入")
                
                input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"发生错误: {e}")
                continue
        
        self.cleanup()

if __name__ == "__main__":
    # 创建并运行应用程序
    app = MainApplication()
    
    try:
        # 连接到RabbitMQ
        if app.connect_to_rabbitmq():
            app.run_interactive_demo()
        else:
            print("无法连接到RabbitMQ，请检查服务是否运行")
    except Exception as e:
        print(f"应用程序运行失败: {e}")
    finally:
        app.cleanup()