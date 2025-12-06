# 第4章：RabbitMQ消息确认与持久化 - 代码示例
"""
消息确认与持久化示例代码
包含自动确认、手动确认、死信队列、发布者确认等核心功能的实现
"""

import pika
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
import asyncio
import aio_pika

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置参数
RABBITMQ_CONFIG = {
    'host': 'localhost',
    'port': 5672,
    'username': 'guest',
    'password': 'guest',
    'heartbeat': 30
}

class AcknowledgeType(Enum):
    """确认类型枚举"""
    AUTO = "auto"           # 自动确认
    MANUAL = "manual"       # 手动确认
    MULTIPLE = "multiple"   # 批量确认
    TRANSACTIONAL = "transactional"  # 事务性确认

class MessageState(Enum):
    """消息状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class MessageContext:
    """消息上下文"""
    delivery_tag: str
    exchange: str
    routing_key: str
    redelivered: bool
    message_id: Optional[str] = None
    timestamp: Optional[float] = None
    retry_count: int = 0
    state: MessageState = MessageState.PENDING

class ConnectionManager:
    """连接管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.channel = None
        
    def connect(self) -> bool:
        """建立连接"""
        try:
            credentials = pika.PlainCredentials(
                self.config['username'],
                self.config['password']
            )
            
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.config['host'],
                    port=self.config['port'],
                    credentials=credentials,
                    heartbeat=self.config.get('heartbeat', 30),
                    blocked_connection_timeout=300
                )
            )
            
            self.channel = self.connection.channel()
            logger.info("RabbitMQ连接建立成功")
            return True
            
        except Exception as e:
            logger.error(f"连接建立失败: {e}")
            return False
            
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ连接已关闭")
            
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connection and self.connection.is_open

class MessageReliabilityManager:
    """消息可靠性管理器"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.conn_manager = connection_manager
        self.pending_messages = {}
        self.processed_messages = set()
        self.failed_messages = {}
        self.stats = {
            'processed': 0,
            'failed': 0,
            'retried': 0,
            'dlq_messages': 0
        }
        
    def setup_durable_queue(self, queue_name: str, dlx_enabled: bool = True) -> bool:
        """设置持久化队列"""
        if not self.conn_manager.is_connected():
            logger.error("连接未建立")
            return False
            
        try:
            channel = self.conn_manager.channel
            
            # 队列参数
            arguments = {
                'x-message-ttl': 300000,  # 5分钟TTL
                'x-max-length': 10000,    # 最大长度
                'x-overflow': 'reject-publish'
            }
            
            # 如果启用死信队列
            if dlx_enabled:
                dlx_exchange = f"dlx_{queue_name}"
                dlq_queue = f"dlq_{queue_name}"
                
                # 创建死信交换机和队列
                channel.exchange_declare(exchange=dlx_exchange, exchange_type='direct', durable=True)
                channel.queue_declare(queue=dlq_queue, durable=True, arguments={
                    'x-message-ttl': 604800  # 7天TTL
                })
                channel.queue_bind(exchange=dlx_exchange, queue=dlq_queue, routing_key=dlq_queue)
                
                arguments.update({
                    'x-dead-letter-exchange': dlx_exchange,
                    'x-dead-letter-routing-key': dlq_queue
                })
            
            # 声明主队列
            channel.queue_declare(
                queue=queue_name,
                durable=True,  # 队列持久化
                arguments=arguments
            )
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=10)
            
            logger.info(f"持久化队列设置完成: {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"设置队列失败: {e}")
            return False
            
    def publish_with_persistence(self, queue_name: str, message: Dict[str, Any],
                               delivery_mode: int = 2) -> bool:
        """发布持久化消息"""
        try:
            message_id = message.get('id', f"msg_{time.time()}")
            
            # 创建消息属性
            properties = pika.BasicProperties(
                delivery_mode=delivery_mode,  # 消息持久化
                message_id=message_id,
                timestamp=time.time(),
                content_type='application/json',
                expiration=str(message.get('ttl', 300000))  # 消息级TTL
            )
            
            # 发布消息
            self.conn_manager.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=properties,
                mandatory=True
            )
            
            logger.info(f"持久化消息发布成功: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"发布消息失败: {e}")
            return False

class AcknowledgeExamples:
    """消息确认示例"""
    
    def __init__(self):
        self.conn_manager = ConnectionManager(RABBITMQ_CONFIG)
        self.reliability_manager = MessageReliabilityManager(self.conn_manager)
        
    def demo_auto_ack_consumer(self, queue_name: str = "auto_ack_queue"):
        """演示自动确认消费者"""
        if not self.conn_manager.connect():
            return
            
        try:
            # 设置队列
            self.reliability_manager.setup_durable_queue(queue_name, dlx_enabled=False)
            
            def auto_ack_callback(ch, method, properties, body):
                """自动确认回调"""
                try:
                    message_id = properties.message_id
                    message_data = json.loads(body.decode())
                    
                    logger.info(f"[自动确认] 收到消息: {message_id}")
                    logger.info(f"[自动确认] 消息内容: {message_data}")
                    
                    # 模拟消息处理
                    self._simulate_processing(message_data, delay=0.5)
                    
                    logger.info(f"[自动确认] 消息处理完成（已自动确认）: {message_id}")
                    
                except Exception as e:
                    logger.error(f"[自动确认] 消息处理失败: {e}")
                    # 注意：在自动确认模式下，即使处理失败，消息也会被标记为已确认
                    
            # 设置消费者（auto_ack=True）
            self.conn_manager.channel.basic_consume(
                queue=queue_name,
                auto_ack=True,  # 关键：设置为自动确认
                on_message_callback=auto_ack_callback
            )
            
            logger.info("开始消费消息（自动确认模式）...")
            self.conn_manager.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("停止消费")
            self.conn_manager.channel.stop_consuming()
        finally:
            self.conn_manager.close()
            
    def demo_manual_ack_consumer(self, queue_name: str = "manual_ack_queue"):
        """演示手动确认消费者"""
        if not self.conn_manager.connect():
            return
            
        try:
            # 设置队列
            self.reliability_manager.setup_durable_queue(queue_name, dlx_enabled=True)
            
            def manual_ack_callback(ch, method, properties, body):
                """手动确认回调"""
                try:
                    message_id = properties.message_id
                    message_data = json.loads(body.decode())
                    
                    logger.info(f"[手动确认] 收到消息: {message_id}")
                    
                    # 创建消息上下文
                    context = MessageContext(
                        delivery_tag=method.delivery_tag,
                        exchange=method.exchange,
                        routing_key=method.routing_key,
                        redelivered=method.redelivered,
                        message_id=message_id,
                        timestamp=time.time()
                    )
                    
                    # 处理消息
                    success = self._process_message_with_retry(message_data, context)
                    
                    if success:
                        # 处理成功，手动确认
                        ch.basic_ack(delivery_tag=context.delivery_tag)
                        logger.info(f"[手动确认] 消息处理成功并确认: {message_id}")
                        self.reliability_manager.stats['processed'] += 1
                    else:
                        # 处理失败，手动否认（重新入队）
                        ch.basic_nack(delivery_tag=context.delivery_tag, requeue=True)
                        logger.info(f"[手动确认] 消息处理失败并否认: {message_id}")
                        self.reliability_manager.stats['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"[手动确认] 消息处理异常: {e}")
                    # 异常情况下也否认消息
                    try:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    except:
                        pass
                    self.reliability_manager.stats['failed'] += 1
                    
            # 设置消费者（auto_ack=False）
            self.conn_manager.channel.basic_consume(
                queue=queue_name,
                auto_ack=False,  # 关键：设置为手动确认
                on_message_callback=manual_ack_callback
            )
            
            logger.info("开始消费消息（手动确认模式）...")
            self.conn_manager.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("停止消费")
            self.conn_manager.channel.stop_consuming()
        finally:
            self.conn_manager.close()
            
    def demo_batch_ack_consumer(self, queue_name: str = "batch_ack_queue"):
        """演示批量确认消费者"""
        if not self.conn_manager.connect():
            return
            
        try:
            # 设置队列
            self.reliability_manager.setup_durable_queue(queue_name, dlx_enabled=False)
            
            pending_batch = []
            batch_size = 5
            processing_messages = {}
            
            def batch_ack_callback(ch, method, properties, body):
                """批量确认回调"""
                nonlocal pending_batch, processing_messages
                
                try:
                    message_id = properties.message_id
                    message_data = json.loads(body.decode())
                    
                    logger.info(f"[批量确认] 收到消息: {message_id}")
                    
                    # 添加到待处理批次
                    context = MessageContext(
                        delivery_tag=method.delivery_tag,
                        exchange=method.exchange,
                        routing_key=method.routing_key,
                        redelivered=method.redelivered,
                        message_id=message_id,
                        timestamp=time.time()
                    )
                    
                    pending_batch.append((context, message_data))
                    processing_messages[message_id] = context
                    
                    # 检查批次大小
                    if len(pending_batch) >= batch_size:
                        self._process_batch(pending_batch, ch)
                        pending_batch.clear()
                        
                except Exception as e:
                    logger.error(f"[批量确认] 处理异常: {e}")
                    
            def _process_batch(batch: List, ch):
                """处理批次"""
                logger.info(f"开始处理批次，共{len(batch)}条消息")
                
                success_count = 0
                for context, message_data in batch:
                    try:
                        # 模拟处理
                        self._simulate_processing(message_data, delay=0.1)
                        success_count += 1
                        logger.info(f"[批量确认] 消息处理成功: {context.message_id}")
                    except Exception as e:
                        logger.error(f"[批量确认] 消息处理失败: {context.message_id}, {e}")
                        
                # 批量确认所有消息
                if success_count > 0:
                    # 确认最后一条消息（批量确认）
                    last_context, _ = batch[-1]
                    ch.basic_ack(delivery_tag=last_context.delivery_tag, multiple=True)
                    logger.info(f"[批量确认] 批量确认完成，成功处理{success_count}条消息")
                    
                # 移除已处理的消息
                for context, _ in batch:
                    processing_messages.pop(context.message_id, None)
                    
            # 设置消费者
            self.conn_manager.channel.basic_consume(
                queue=queue_name,
                auto_ack=False,
                on_message_callback=batch_ack_callback
            )
            
            logger.info("开始消费消息（批量确认模式）...")
            self.conn_manager.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("停止消费")
            self.conn_manager.channel.stop_consuming()
        finally:
            self.conn_manager.close()
            
    def _process_message_with_retry(self, message_data: Dict, context: MessageContext) -> bool:
        """带重试的消息处理"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 模拟消息处理
                self._simulate_processing(message_data, delay=0.5)
                return True
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # 指数退避
                    logger.info(f"处理失败，{wait_time}秒后重试 ({retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"处理最终失败，已重试{max_retries}次")
                    return False
                    
    def _simulate_processing(self, message_data: Dict, delay: float = 0.1):
        """模拟消息处理"""
        # 模拟处理时间
        time.sleep(delay)
        
        # 模拟处理失败
        if random.random() < 0.1:  # 10%失败率
            raise Exception("模拟处理失败")
            
    def demo_producer_with_auto_messages(self, queue_name: str, count: int = 20):
        """演示自动确认模式的生产者"""
        if not self.conn_manager.connect():
            return
            
        try:
            # 设置队列
            self.reliability_manager.setup_durable_queue(queue_name, dlx_enabled=False)
            
            logger.info(f"开始发布{count}条自动确认消息...")
            
            for i in range(count):
                message = {
                    'id': f'auto_msg_{i}',
                    'type': 'auto_ack',
                    'data': f'test data {i}',
                    'timestamp': time.time()
                }
                
                # 发布持久化消息
                if self.reliability_manager.publish_with_persistence(queue_name, message):
                    logger.info(f"消息发布成功: auto_msg_{i}")
                else:
                    logger.error(f"消息发布失败: auto_msg_{i}")
                    
                # 短暂延迟
                time.sleep(0.1)
                
            logger.info("所有消息发布完成")
            
        except Exception as e:
            logger.error(f"生产者异常: {e}")
        finally:
            self.conn_manager.close()
            
    def demo_producer_with_manual_messages(self, queue_name: str, count: int = 20):
        """演示手动确认模式的生产者"""
        if not self.conn_manager.connect():
            return
            
        try:
            # 设置队列
            self.reliability_manager.setup_durable_queue(queue_name, dlx_enabled=True)
            
            logger.info(f"开始发布{count}条手动确认消息...")
            
            for i in range(count):
                message = {
                    'id': f'manual_msg_{i}',
                    'type': 'manual_ack',
                    'data': f'test data {i}',
                    'timestamp': time.time(),
                    'ttl': 300000  # 5分钟TTL
                }
                
                # 发布持久化消息
                if self.reliability_manager.publish_with_persistence(queue_name, message):
                    logger.info(f"消息发布成功: manual_msg_{i}")
                else:
                    logger.error(f"消息发布失败: manual_msg_{i}")
                    
                # 短暂延迟
                time.sleep(0.1)
                
            logger.info("所有消息发布完成")
            
        except Exception as e:
            logger.error(f"生产者异常: {e}")
        finally:
            self.conn_manager.close()

class PublisherConfirmationExamples:
    """发布者确认示例"""
    
    def __init__(self):
        self.conn_manager = ConnectionManager(RABBITMQ_CONFIG)
        self.pending_confirmations = {}
        self.confirmation_stats = {
            'published': 0,
            'confirmed': 0,
            'failed': 0,
            'timeout': 0
        }
        
    def demo_publisher_confirmation(self, queue_name: str = "confirmation_queue", 
                                  count: int = 10):
        """演示发布者确认"""
        if not self.conn_manager.connect():
            return
            
        try:
            # 设置队列
            channel = self.conn_manager.channel
            channel.queue_declare(queue=queue_name, durable=True)
            
            # 启用发布者确认
            channel.confirm_delivery()
            logger.info("发布者确认机制已启用")
            
            logger.info(f"开始发布{count}条消息并等待确认...")
            
            for i in range(count):
                message_id = f'confirm_msg_{i}'
                message = {
                    'id': message_id,
                    'type': 'publisher_confirmation',
                    'data': f'test data {i}',
                    'timestamp': time.time()
                }
                
                try:
                    # 发布消息
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=json.dumps(message),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            message_id=message_id,
                            timestamp=time.time()
                        ),
                        mandatory=True
                    )
                    
                    self.confirmation_stats['published'] += 1
                    logger.info(f"消息已发布，等待确认: {message_id}")
                    
                    # 短暂延迟以模拟时间间隔
                    time.sleep(0.5)
                    
                except pika.exceptions.NackError:
                    logger.error(f"消息发布被拒绝: {message_id}")
                    self.confirmation_stats['failed'] += 1
                except Exception as e:
                    logger.error(f"消息发布异常: {e}")
                    self.confirmation_stats['failed'] += 1
                    
            logger.info("所有消息发布完成")
            
            # 打印统计信息
            self._print_confirmation_stats()
            
        except Exception as e:
            logger.error(f"发布者确认演示异常: {e}")
        finally:
            self.conn_manager.close()
            
    def demo_transactional_publisher(self, queue_name: str = "transactional_queue"):
        """演示事务性发布者"""
        if not self.conn_manager.connect():
            return
            
        try:
            # 设置队列
            channel = self.conn_manager.channel
            channel.queue_declare(queue=queue_name, durable=True)
            
            # 开始事务
            channel.tx_select()
            logger.info("事务模式已开启")
            
            messages = [
                {'id': 'tx_msg_1', 'data': 'transactional message 1'},
                {'id': 'tx_msg_2', 'data': 'transactional message 2'},
                {'id': 'tx_msg_3', 'data': 'transactional message 3'}
            ]
            
            # 尝试成功的事务
            logger.info("=== 成功事务演示 ===")
            try:
                for message in messages:
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=json.dumps(message),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            message_id=message['id']
                        )
                    )
                    logger.info(f"消息添加到事务: {message['id']}")
                    
                # 提交事务
                channel.tx_commit()
                logger.info("事务提交成功")
                
            except Exception as e:
                # 回滚事务
                channel.tx_rollback()
                logger.error(f"事务提交失败，已回滚: {e}")
                
            # 尝试失败的事务
            logger.info("=== 失败事务演示 ===")
            try:
                # 开始新事务
                channel.tx_select()
                
                # 添加一些消息
                for i in range(3):
                    message = {'id': f'failed_tx_msg_{i}', 'data': f'failed transaction {i}'}
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=json.dumps(message),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            message_id=message['id']
                        )
                    )
                    logger.info(f"消息添加到事务: {message['id']}")
                    
                # 模拟失败
                raise Exception("模拟事务失败")
                
            except Exception as e:
                # 回滚事务
                channel.tx_rollback()
                logger.error(f"事务失败，已回滚: {e}")
                
        except Exception as e:
            logger.error(f"事务性发布者演示异常: {e}")
        finally:
            self.conn_manager.close()
            
    def _print_confirmation_stats(self):
        """打印确认统计信息"""
        stats = self.confirmation_stats
        total = stats['published']
        
        if total > 0:
            confirmation_rate = (stats['confirmed'] / total) * 100
            failure_rate = ((stats['failed'] + stats['timeout']) / total) * 100
            
            logger.info("=== 发布者确认统计 ===")
            logger.info(f"总发布消息数: {total}")
            logger.info(f"确认成功: {stats['confirmed']} ({confirmation_rate:.1f}%)")
            logger.info(f"确认失败: {stats['failed']} + {stats['timeout']} = {stats['failed'] + stats['timeout']} ({failure_rate:.1f}%)")

class DeadLetterQueueExamples:
    """死信队列示例"""
    
    def __init__(self):
        self.conn_manager = ConnectionManager(RABBITMQ_CONFIG)
        
    def demo_dead_letter_queue(self, main_queue: str = "dlq_main", 
                             dlq_queue: str = "dlq_dead_letter"):
        """演示死信队列"""
        if not self.conn_manager.connect():
            return
            
        try:
            channel = self.conn_manager.channel
            
            # 清理之前的声明（如果存在）
            for queue in [main_queue, dlq_queue]:
                try:
                    channel.queue_delete(queue=queue)
                except:
                    pass
            
            # 创建死信交换机
            dlx_exchange = f"dlx_{main_queue}"
            channel.exchange_declare(exchange=dlx_exchange, exchange_type='direct', durable=True)
            
            # 创建死信队列
            channel.queue_declare(
                queue=dlq_queue,
                durable=True,
                arguments={
                    'x-message-ttl': 604800,  # 7天TTL
                    'x-max-length': 10000
                }
            )
            
            # 绑定死信队列
            channel.queue_bind(
                exchange=dlx_exchange,
                queue=dlq_queue,
                routing_key=dlq_queue
            )
            
            # 创建主队列（配置死信）
            channel.queue_declare(
                queue=main_queue,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': dlx_exchange,
                    'x-dead-letter-routing-key': dlq_queue,
                    'x-message-ttl': 10000,  # 10秒TTL，测试过期
                    'x-max-length': 5,       # 限制队列长度，测试队列溢出
                    'x-overflow': 'reject-publish'
                }
            )
            
            logger.info(f"死信队列设置完成 - 主队列: {main_queue}, 死信队列: {dlq_queue}")
            
            # 测试死信场景
            self._test_dlq_scenarios(main_queue, dlq_queue)
            
        except Exception as e:
            logger.error(f"死信队列演示异常: {e}")
        finally:
            self.conn_manager.close()
            
    def _test_dlq_scenarios(self, main_queue: str, dlq_queue: str):
        """测试死信队列场景"""
        channel = self.conn_manager.channel
        
        logger.info("=== 测试场景1: TTL过期消息 ===")
        # 发送一条短TTL的消息
        message_ttl = {
            'id': 'ttl_message',
            'type': 'ttl_test',
            'data': 'This message will expire',
            'timestamp': time.time()
        }
        
        properties = pika.BasicProperties(
            delivery_mode=2,
            message_id=message_ttl['id'],
            expiration='2000'  # 2秒TTL
        )
        
        channel.basic_publish(
            exchange='',
            routing_key=main_queue,
            body=json.dumps(message_ttl),
            properties=properties
        )
        logger.info(f"发送TTL消息: {message_ttl['id']}")
        
        # 等待TTL过期
        logger.info("等待TTL过期（3秒）...")
        time.sleep(3)
        
        logger.info("=== 测试场景2: 队列溢出消息 ===")
        # 快速发送多条消息触发队列溢出
        for i in range(8):  # 队列限制为5，所以会有3条被拒绝
            message_overflow = {
                'id': f'overflow_message_{i}',
                'type': 'overflow_test',
                'data': f'This message tests queue overflow {i}',
                'timestamp': time.time()
            }
            
            try:
                channel.basic_publish(
                    exchange='',
                    routing_key=main_queue,
                    body=json.dumps(message_overflow),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        message_id=message_overflow['id']
                    )
                )
                logger.info(f"发送消息: overflow_message_{i}")
            except Exception as e:
                logger.error(f"消息被拒绝（队列溢出）: overflow_message_{i}, {e}")
                
        logger.info("=== 测试场景3: 拒绝消息 ===")
        # 测试消费者拒绝消息
        self._test_rejected_messages(main_queue, dlq_queue)
        
        # 检查死信队列中的消息
        self._check_dead_letter_queue(dlq_queue)
        
    def _test_rejected_messages(self, main_queue: str, dlq_queue: str):
        """测试被拒绝的消息"""
        channel = self.conn_manager.channel
        
        def rejection_callback(ch, method, properties, body):
            """拒绝消息的回调"""
            message_id = properties.message_id
            logger.info(f"[拒绝测试] 收到消息: {message_id}")
            
            # 模拟处理失败
            if 'reject' in message_id:
                logger.info(f"[拒绝测试] 拒绝消息并重新入队: {message_id}")
                # 否认消息，重新入队
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                logger.info(f"[拒绝测试] 正常处理消息: {message_id}")
                # 正常确认
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        # 发送测试消息
        test_messages = [
            {'id': 'accept_message_1', 'data': 'This will be accepted'},
            {'id': 'reject_message_1', 'data': 'This will be rejected'},
            {'id': 'accept_message_2', 'data': 'This will be accepted'}
        ]
        
        for message in test_messages:
            channel.basic_publish(
                exchange='',
                routing_key=main_queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    message_id=message['id']
                )
            )
            logger.info(f"发送测试消息: {message['id']}")
            
        # 开始消费（只处理一条消息）
        channel.basic_consume(
            queue=main_queue,
            auto_ack=False,
            on_message_callback=rejection_callback
        )
        
        # 处理一条消息
        try:
            channel.start_consuming()
        except:
            pass
        
    def _check_dead_letter_queue(self, dlq_queue: str):
        """检查死信队列"""
        try:
            channel = self.conn_manager.channel
            
            # 获取队列状态
            result = channel.queue_declare(queue=dlq_queue, passive=True)
            message_count = result.method.message_count
            
            logger.info(f"=== 死信队列状态 ===")
            logger.info(f"死信队列: {dlq_queue}")
            logger.info(signal_count := f"死信消息数量: {message_count}")
            
            if message_count > 0:
                logger.info("开始消费死信队列消息...")
                
                for _ in range(min(message_count, 10)):  # 最多消费10条
                    try:
                        method_frame, header_frame, body = channel.basic_get(
                            queue=dlq_queue,
                            auto_ack=False
                        )
                        
                        if method_frame:
                            message_data = json.loads(body)
                            logger.info(f"死信消息: {message_data}")
                            # 确认并移除死信消息
                            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                        else:
                            break
                            
                    except Exception as e:
                        logger.error(f"处理死信消息失败: {e}")
                        
        except Exception as e:
            logger.error(f"检查死信队列失败: {e}")

def main():
    """主函数 - 交互式演示"""
    print("=" * 60)
    print("RabbitMQ 消息确认与持久化示例")
    print("=" * 60)
    
    while True:
        print("\n请选择演示功能：")
        print("1. 自动确认 - 生产者")
        print("2. 自动确认 - 消费者")
        print("3. 手动确认 - 生产者")
        print("4. 手动确认 - 消费者")
        print("5. 批量确认 - 消费者")
        print("6. 发布者确认")
        print("7. 事务性发布")
        print("8. 死信队列演示")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-8): ").strip()
        
        if choice == '0':
            print("退出程序")
            break
        elif choice == '1':
            ack_examples = AcknowledgeExamples()
            count = input("请输入要发送的消息数量 (默认20): ").strip()
            count = int(count) if count.isdigit() else 20
            ack_examples.demo_producer_with_auto_messages(count=count)
            
        elif choice == '2':
            ack_examples = AcknowledgeExamples()
            ack_examples.demo_auto_ack_consumer()
            
        elif choice == '3':
            ack_examples = AcknowledgeExamples()
            count = input("请输入要发送的消息数量 (默认20): ").strip()
            count = int(count) if count.isdigit() else 20
            ack_examples.demo_producer_with_manual_messages(count=count)
            
        elif choice == '4':
            ack_examples = AcknowledgeExamples()
            ack_examples.demo_manual_ack_consumer()
            
        elif choice == '5':
            ack_examples = AcknowledgeExamples()
            ack_examples.demo_batch_ack_consumer()
            
        elif choice == '6':
            pub_conf_examples = PublisherConfirmationExamples()
            count = input("请输入要发送的消息数量 (默认10): ").strip()
            count = int(count) if count.isdigit() else 10
            pub_conf_examples.demo_publisher_confirmation(count=count)
            
        elif choice == '7':
            pub_conf_examples = PublisherConfirmationExamples()
            pub_conf_examples.demo_transactional_publisher()
            
        elif choice == '8':
            dlq_examples = DeadLetterQueueExamples()
            dlq_examples.demo_dead_letter_queue()
            
        else:
            print("无效选择，请重新输入")
            
        input("\n按Enter键继续...")

if __name__ == "__main__":
    main()