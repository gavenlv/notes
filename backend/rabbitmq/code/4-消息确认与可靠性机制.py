#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第4章：消息确认与可靠性机制
完整可运行的代码示例

本文件包含了第4章中所有消息确认与可靠性机制相关的完整示例：
1. 生产者确认机制
2. 消费者确认机制
3. 消息持久化
4. 事务机制
5. 死信机制
6. 消息重试机制
7. 可靠性最佳实践
8. 可靠性监控

运行方式：
python 4-消息确认与可靠性机制.py [demo_type]

demo_type可选：
- producer_confirms : 运行生产者确认演示
- consumer_confirms : 运行消费者确认演示
- persistence      : 运行消息持久化演示
- transactions     : 运行事務机制演示
- dead_letter      : 运行死信机制演示
- retry            : 运行消息重试演示
- best_practices   : 运行可靠性最佳实践演示
- monitoring       : 运行可靠性监控演示
- all              : 依次运行所有演示（默认）
"""

import pika
import threading
import time
import sys
import json
import uuid
import random
import argparse


class PublisherConfirmsDemo:
    """生产者确认机制演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def setup_infrastructure(self):
        """设置基础设施"""
        # 声明交换机和队列
        self.channel.exchange_declare(
            exchange='confirms_exchange',
            exchange_type='direct',
            durable=True
        )
        self.channel.queue_declare(queue='confirms_queue', durable=True)
        self.channel.queue_bind(
            exchange='confirms_exchange',
            queue='confirms_queue',
            routing_key='confirms_key'
        )
        
        print(" [*] 基础设施设置完成")
    
    def demo_normal_confirm(self):
        """演示普通确认"""
        print("\n=== 普通确认演示 ===")
        
        # 启用确认
        self.channel.confirm_delivery()
        
        success_count = 0
        total_count = 5
        
        for i in range(total_count):
            message = f"普通确认消息 {i+1}"
            try:
                # 发送消息
                self.channel.basic_publish(
                    exchange='confirms_exchange',
                    routing_key='confirms_key',
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 持久化
                        message_id=f"normal_{i+1}"
                    )
                )
                
                # 等待确认
                if self.channel.wait_for_confirms(timeout=5):
                    print(f" [x] 确认成功: {message}")
                    success_count += 1
                else:
                    print(f" [!] 确认失败: {message}")
            except pika.exceptions.AMQPConnectionError as e:
                print(f" [!] 确认超时: {message} - {e}")
        
        print(f" [+] 普通: {success_count}/{total_count} 消息确认成功")
    
    def demo_batch_confirm(self):
        """演示批量确认"""
        print("\n=== 批量确认演示 ===")
        
        batch_size = 5
        message_count = 0
        success_count = 0
        
        try:
            # 发送一批消息
            for i in range(batch_size):
                message = f"批量确认消息 {i+1}"
                self.channel.basic_publish(
                    exchange='confirms_exchange',
                    routing_key='confirms_key',
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        message_id=f"batch_{i+1}"
                    )
                )
                message_count += 1
                print(f" [x] 发送: {message}")
            
            # 等待所有消息的确认
            if self.channel.wait_for_confirms(timeout=10):
                print(f" [+] 批量确认成功，共 {message_count} 条消息")
                success_count = message_count
            else:
                print(f" [!] 批量确认失败")
        except pika.exceptions.AMQPConnectionError as e:
            print(f" [!] 批量确认超时: {e}")
        
        print(f" [+] 批量: {success_count}/{message_count} 消息确认成功")
    
    def demo_async_confirm(self):
        """演示异步确认"""
        print("\n=== 异步确认演示 ===")
        
        # 用于跟踪未确认消息
        unconfirmed_messages = {}
        delivery_tags = []
        confirmed_count = 0
        nacked_count = 0
        returned_count = 0
        confirm_event = threading.Event()
        
        # 确认回调
        def on_ack(channel, method_frame):
            nonlocal confirmed_count
            delivery_tag = method_frame.delivery_tag
            if delivery_tag in unconfirmed_messages:
                message = unconfirmed_messages.pop(delivery_tag)
                delivery_tags.remove(delivery_tag)
                confirmed_count += 1
                print(f" [✓] 消息确认: {message} (delivery_tag: {delivery_tag})")
                
                if not unconfirmed_messages:
                    confirm_event.set()
        
        # 未确认回调（Negative ACK，NACK）
        def on_nack(channel, method_frame):
            nonlocal nacked_count
            delivery_tag = method_frame.delivery_tag
            if delivery_tag in unconfirmed_messages:
                message = unconfirmed_messages[delivery_tag]
                nacked_count += 1
                print(f" [✗] 消息未确认(NACK): {message} (delivery_tag: {delivery_tag})")
                
                if not unconfirmed_messages:
                    confirm_event.set()
        
        # 返回回调（消息被Broker接收）
        def on_return(channel, method_frame, header_frame, body):
            nonlocal returned_count
            message = body.decode('utf-8')
            returned_count += 1
            print(f" [←] 消息返回: {message} (reply_code: {method_frame.reply_code}, reply_text: {method_frame.reply_text})")
        
        # 启用确认并设置回调
        self.channel.confirm_delivery()
        
        # 对于pika版本兼容性，尝试不同的回调设置方法
        try:
            # pika 1.2+ 版本
            self.channel.add_callback_threadsafe(
                lambda: self.channel.add_callback(on_ack, replies=[pika.spec.Basic.Ack], one_shot=False)
            )
            self.channel.add_callback_threadsafe(
                lambda: self.channel.add_callback(on_nack, replies=[pika.spec.Basic.Nack], one_shot=False)
            )
        except AttributeError:
            # 旧版本pika
            self.channel.add_callback(on_ack, replies=[pika.spec.Basic.Ack], one_shot=False)
            self.channel.add_callback(on_nack, replies=[pika.spec.Basic.Nack], one_shot=False)
        
        self.channel.add_on_return_callback(on_return)
        
        # 发送消息
        message_count = 5
        for i in range(message_count):
            message = f'异步确认消息 {i+1}'
            
            # 发送消息并获取delivery_tag
            result = self.channel.basic_publish(
                exchange='confirms_exchange',
                routing_key='confirms_key',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    message_id=f"async_{i+1}"
                ),
                mandatory=True  # 如果消息无法路由，返回给生产者
            )
            
            # 存储未确认消息
            if hasattr(result, 'method') and hasattr(result.method, 'delivery_tag'):
                delivery_tag = result.method.delivery_tag
                unconfirmed_messages[delivery_tag] = message
                delivery_tags.append(delivery_tag)
            else:
                # pika 0.12+版本可能有不同的返回值
                delivery_tag = len(unconfirmed_messages) + 1  # 简单模拟
                unconfirmed_messages[delivery_tag] = message
                delivery_tags.append(delivery_tag)
            
            print(f" [x] 发送消息: {message} (delivery_tag: {delivery_tag})")
        
        # 等待所有消息确认
        print(" [*] 等待所有消息确认...")
        confirm_event.wait(timeout=10)
        
        total_sent = confirmed_count + nacked_count
        print(f" [+] 异步确认统计:")
        print(f"     已确认: {confirmed_count}")
        print(f"     未确认: {nacked_count}")
        print(f"     返回: {returned_count}")
        print(f"     发送总数: {total_sent}")
    
    def demo_reliable_publisher(self):
        """演示可靠发布者"""
        print("\n=== 可靠发布者演示 ===")
        
        class ReliablePublisher:
            def __init__(self, channel, exchange_name):
                self.channel = channel
                self.exchange_name = exchange_name
                self.unconfirmed = {}
                self.confirm_event = threading.Event()
                
                # 设置确认回调
                self.channel.add_callback(
                    self.on_ack,
                    replies=[pika.spec.Basic.Ack],
                    one_shot=False
                )
                
                self.channel.add_callback(
                    self.on_nack,
                    replies=[pika.spec.Basic.Nack],
                    one_shot=False
                )
                
                # 启用确认
                self.channel.confirm_delivery()
            
            def on_ack(self, frame):
                """确认回调"""
                delivery_tag = frame.method.delivery_tag
                if delivery_tag in self.unconfirmed:
                    message = self.unconfirmed.pop(delivery_tag)
                    print(f" [✓] 确认: {message}")
                    if not self.unconfirmed:
                        self.confirm_event.set()
            
            def on_nack(self, frame):
                """未确认回调"""
                delivery_tag = frame.method.delivery_tag
                if delivery_tag in self.unconfirmed:
                    message = self.unconfirmed.pop(delivery_tag)
                    print(f" [✗] 未确认: {message}")
                    if not self.unconfirmed:
                        self.confirm_event.set()
            
            def publish_with_confirmation(self, routing_key, message, timeout=10):
                """带确认的消息发布"""
                # 发送消息
                result = self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=routing_key,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2  # 持久化
                    )
                )
                
                # 存储未确认消息
                if hasattr(result, 'method') and hasattr(result.method, 'delivery_tag'):
                    delivery_tag = result.method.delivery_tag
                    self.unconfirmed[delivery_tag] = message
                else:
                    delivery_tag = len(self.unconfirmed) + 1  # 简单模拟
                    self.unconfirmed[delivery_tag] = message
                
                # 等待确认
                self.confirm_event.clear()
                confirmed = self.confirm_event.wait(timeout=timeout)
                
                return confirmed
        
        # 创建可靠发布者
        publisher = ReliablePublisher(self.channel, 'confirms_exchange')
        
        # 发送消息并等待确认
        success_count = 0
        total_count = 5
        
        for i in range(total_count):
            message = f"可靠发布消息 {i+1}"
            confirmed = publisher.publish_with_confirmation('confirms_key', message)
            if confirmed:
                success_count += 1
            print(f" [{'✓' if confirmed else '✗'}] 发送: {message}")
        
        print(f" [+] 可靠发布者: {success_count}/{total_count} 消息确认成功")
    
    def run_demo(self):
        """运行生产者确认演示"""
        print("\n=== 生产者确认机制演示 ===")
        
        self.connect()
        
        try:
            self.setup_infrastructure()
            self.demo_normal_confirm()
            self.demo_batch_confirm()
            self.demo_async_confirm()
            self.demo_reliable_publisher()
        finally:
            self.disconnect()
        
        print("\n [*] 生产者确认机制演示完成")


class ConsumerConfirmsDemo:
    """消费者确认机制演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
        self.consumers = []
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def setup_infrastructure(self):
        """设置基础设施"""
        # 声明队列
        self.channel.queue_declare(queue='auto_ack_queue', durable=True)
        self.channel.queue_declare(queue='manual_ack_queue', durable=True)
        self.channel.queue_declare(queue='batch_ack_queue', durable=True)
        
        # 添加测试消息
        for queue in ['auto_ack_queue', 'manual_ack_queue', 'batch_ack_queue']:
            for i in range(5):
                message = f"{queue.split('_')[0]} 测试消息 {i+1}"
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=message
                )
        
        print(" [*] 基础设施设置完成")
    
    def demo_auto_ack(self):
        """演示自动确认"""
        print("\n=== 自动确认演示 ===")
        
        received = []
        
        def auto_ack_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            received.append(message)
            print(f" [+] 自动确认收到: {message}")
            # 无需手动确认，消息发送后立即被确认
        
        self.channel.basic_consume(
            queue='auto_ack_queue',
            on_message_callback=auto_ack_callback,
            auto_ack=True  # 自动确认
        )
        
        # 消费所有消息
        start_time = time.time()
        while len(received) < 5 and time.time() - start_time < 3:
            self.connection.process_data_events(time_limit=0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 自动确认: 共收到 {len(received)} 条消息")
    
    def demo_manual_ack(self):
        """演示手动确认"""
        print("\n=== 手动确认演示 ===")
        
        received = []
        
        def manual_ack_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            received.append(message)
            print(f" [+] 手动确认收到: {message}")
            # 手动确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='manual_ack_queue',
            on_message_callback=manual_ack_callback,
            auto_ack=False  # 手动确认
        )
        
        # 消费所有消息
        start_time = time.time()
        while len(received) < 5 and time.time() - start_time < 3:
            self.connection.process_data_events(time_limit=0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 手动确认: 共收到 {len(received)} 条消息")
    
    def demo_batch_ack(self):
        """演示批量确认"""
        print("\n=== 批量确认演示 ===")
        
        processed_messages = []
        batch_size = 3
        
        def batch_ack_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            print(f" [+] 收到: {message}")
            
            # 存储delivery_tag用于批量确认
            processed_messages.append(method.delivery_tag)
            
            # 达到批次大小时，批量确认
            if len(processed_messages) >= batch_size:
                # 确认最后一条消息，确认multiple=True时，所有小于等于此delivery_tag的消息都会被确认
                last_delivery_tag = processed_messages[-1]
                ch.basic_ack(delivery_tag=last_delivery_tag, multiple=True)
                print(f" [✓] 批量确认 {len(processed_messages)} 条消息")
                processed_messages.clear()
        
        self.channel.basic_consume(
            queue='batch_ack_queue',
            on_message_callback=batch_ack_callback,
            auto_ack=False  # 手动确认
        )
        
        # 消费所有消息
        start_time = time.time()
        while len(processed_messages) > 0 or time.time() - start_time < 3:
            self.connection.process_data_events(time_limit=0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 批量确认: 处理完成")
    
    def demo_reliable_consumer(self):
        """演示可靠消费者"""
        print("\n=== 可靠消费者演示 ===")
        
        class ReliableConsumer:
            def __init__(self, channel, queue_name):
                self.channel = channel
                self.queue_name = queue_name
                self.processed = 0
                self.failed = 0
                self.start_time = time.time()
            
            def reliable_callback(self, ch, method, properties, body):
                """可靠的回调处理"""
                message = body.decode('utf-8')
                delivery_tag = method.delivery_tag
                
                try:
                    # 解析消息
                    data = json.loads(message) if self.is_json(message) else message
                    
                    # 业务逻辑处理
                    result = self.process_message(data)
                    
                    # 处理成功
                    if result:
                        ch.basic_ack(delivery_tag=delivery_tag)
                        self.processed += 1
                        print(f" [✓] 处理成功: {delivery_tag}")
                    else:
                        # 业务逻辑返回失败
                        ch.basic_nack(delivery_tag=delivery_tag, requeue=False)
                        self.failed += 1
                        print(f" [✗] 业务失败: {delivery_tag}")
                
                except json.JSONDecodeError:
                    # JSON解析错误
                    print(f" [✗] JSON解析错误: {message}")
                    ch.basic_nack(delivery_tag=delivery_tag, requeue=False)
                    self.failed += 1
                
                except Exception as e:
                    # 处理异常
                    print(f" [✗] 处理异常: {e}")
                    
                    # 根据异常类型决定是否重新入队
                    if self.is_transient_error(e):
                        # 临时错误，重新入队稍后重试
                        ch.basic_nack(delivery_tag=delivery_tag, requeue=True)
                        print(f" [↻] 临时错误，消息重新入队: {delivery_tag}")
                    else:
                        # 永久错误，丢弃消息
                        ch.basic_nack(delivery_tag=delivery_tag, requeue=False)
                        self.failed += 1
                        print(f" [✗] 永久错误，消息丢弃: {delivery_tag}")
            
            def is_json(self, message):
                """检查消息是否为JSON格式"""
                try:
                    json.loads(message)
                    return True
                except:
                    return False
            
            def process_message(self, data):
                """处理消息的业务逻辑（示例）"""
                # 这里实现具体的业务逻辑
                if isinstance(data, dict) and 'operation' in data:
                    operation = data['operation']
                    
                    if operation == 'success':
                        return True
                    elif operation == 'permanent_failure':
                        return False
                    elif operation == 'transient_error':
                        raise ConnectionError("模拟临时连接错误")
                    else:
                        print(f"未知操作: {operation}")
                        return False
                else:
                    # 对于非JSON消息，随机成功或失败
                    return random.choice([True, False])
            
            def is_transient_error(self, exception):
                """判断是否为临时错误"""
                # 这里可以定义哪些异常被认为是临时的
                transient_errors = [
                    'ConnectionError',
                    'TimeoutError',
                    'ServiceUnavailableError'
                ]
                
                error_name = type(exception).__name__
                return any(err in error_name for err in transient_errors)
        
        # 创建测试消息
        test_messages = [
            '{"operation": "success", "message": "成功操作"}',
            '{"operation": "permanent_failure", "message": "永久失败"}',
            '{"operation": "transient_error", "message": "临时错误"}',
            '{"operation": "unknown", "message": "未知操作"}',
            '非JSON消息'
        ]
        
        # 创建可靠队列
        self.channel.queue_declare(queue='reliable_queue', durable=True)
        
        # 发送测试消息
        for message in test_messages:
            self.channel.basic_publish(
                exchange='',
                routing_key='reliable_queue',
                body=message
            )
        
        # 创建可靠消费者
        reliable_consumer = ReliableConsumer(self.channel, 'reliable_queue')
        self.channel.basic_consume(
            queue='reliable_queue',
            on_message_callback=reliable_consumer.reliable_callback,
            auto_ack=False
        )
        
        # 消费所有消息
        message_count = len(test_messages)
        consumed = 0
        start_time = time.time()
        
        while consumed < message_count and time.time() - start_time < 10:
            method, properties, body = self.channel.basic_get(queue='reliable_queue')
            if method:
                reliable_consumer.reliable_callback(self.channel, method, properties, body)
                consumed += 1
            else:
                time.sleep(0.1)
        
        # 停止消费
        self.channel.stop_consuming()
        
        # 计算统计信息
        duration = time.time() - reliable_consumer.start_time
        total = reliable_consumer.processed + reliable_consumer.failed
        success_rate = (reliable_consumer.processed / total * 100) if total > 0 else 0
        
        print(f" [+] 可靠消费者统计:")
        print(f"     处理成功: {reliable_consumer.processed}")
        print(f"     处理失败: {reliable_consumer.failed}")
        print(f"     成功率: {success_rate:.2f}%")
        print(f"     总耗时: {duration:.2f}秒")
        if duration > 0:
            print(f"     平均速率: {total/duration:.2f}条/秒")
    
    def run_demo(self):
        """运行消费者确认演示"""
        print("\n=== 消费者确认机制演示 ===")
        
        self.connect()
        
        try:
            self.setup_infrastructure()
            self.demo_auto_ack()
            self.demo_manual_ack()
            self.demo_batch_ack()
            self.demo_reliable_consumer()
        finally:
            self.disconnect()
        
        print("\n [*] 消费者确认机制演示完成")


class MessagePersistenceDemo:
    """消息持久化演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def demo_persistence_setup(self):
        """演示持久化设置"""
        print("\n=== 持久化设置演示 ===")
        
        # 1. 声明持久化交换机
        self.channel.exchange_declare(
            exchange='durable_exchange',
            exchange_type='direct',
            durable=True  # 交换机持久化
        )
        print(" [*] 声明持久化交换机: durable_exchange")
        
        # 2. 声明持久化队列
        self.channel.queue_declare(
            queue='durable_queue',
            durable=True  # 队列持久化
        )
        print(" [*] 声明持久化队列: durable_queue")
        
        # 3. 发送持久化消息
        for i in range(3):
            message = f"持久化消息 {i+1}"
            self.channel.basic_publish(
                exchange='durable_exchange',
                routing_key='durable_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化 (1=非持久化, 2=持久化)
                    priority=i+1,    # 优先级
                    timestamp=int(time.time()),  # 时间戳
                    message_id=f"persistent_{i+1}"  # 消息ID
                )
            )
            print(f" [x] 发送持久化消息: {message}")
        
        # 4. 绑定队列到交换机
        self.channel.queue_bind(
            exchange='durable_exchange',
            queue='durable_queue',
            routing_key='durable_key'
        )
        print(" [*] 绑定队列到交换机")
    
    def demo_non_persistence_setup(self):
        """演示非持久化设置"""
        print("\n=== 非持久化设置演示 ===")
        
        # 1. 声明非持久化交换机
        self.channel.exchange_declare(
            exchange='transient_exchange',
            exchange_type='direct',
            durable=False  # 非持久化交换机
        )
        print(" [*] 声明非持久化交换机: transient_exchange")
        
        # 2. 声明非持久化队列
        self.channel.queue_declare(
            queue='transient_queue',
            durable=False  # 非持久化队列
        )
        print(" [*] 声明非持久化队列: transient_queue")
        
        # 3. 发送非持久化消息
        for i in range(3):
            message = f"非持久化消息 {i+1}"
            self.channel.basic_publish(
                exchange='transient_exchange',
                routing_key='transient_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=1,  # 非持久化消息
                    priority=i+1,     # 优先级
                    timestamp=int(time.time()),  # 时间戳
                    message_id=f"transient_{i+1}"  # 消息ID
                )
            )
            print(f" [x] 发送非持久化消息: {message}")
        
        # 4. 绑定队列到交换机
        self.channel.queue_bind(
            exchange='transient_exchange',
            queue='transient_queue',
            routing_key='transient_key'
        )
        print(" [*] 绑定队列到交换机")
    
    def demo_lazy_queue(self):
        """演示惰性队列"""
        print("\n=== 惰性队列演示 ===")
        
        # 声明惰性队列，减少内存使用
        self.channel.queue_declare(
            queue='lazy_durable_queue',
            durable=True,
            arguments={
                'x-queue-mode': 'lazy'  # 惰性队列，减少内存压力
            }
        )
        print(" [*] 声明惰性队列: lazy_durable_queue")
        
        # 发送较大的消息
        for i in range(3):
            # 创建一个较大的消息
            large_message = 'x' * 1000  # 1KB的消息
            message = f'惰性队列消息 {i+1}: {large_message[:50]}...'
            
            self.channel.basic_publish(
                exchange='',
                routing_key='lazy_durable_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    message_id=f"lazy_{i+1}"
                )
            )
            print(f" [x] 发送大消息 {i+1} (约1KB)")
        
        # 创建消费者
        def callback(ch, method, properties, body):
            message = body.decode('utf-8')
            print(f" [+] 收到大消息: {message[:50]}... (长度: {len(message)})")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='lazy_durable_queue',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 消费所有消息
        message_count = 0
        start_time = time.time()
        while message_count < 3 and time.time() - start_time < 3:
            method, properties, body = self.channel.basic_get(queue='lazy_durable_queue')
            if method:
                callback(self.channel, method, properties, body)
                message_count += 1
            else:
                time.sleep(0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 共处理 {message_count} 条大消息")
    
    def demo_quorum_queue(self):
        """演示仲裁队列"""
        print("\n=== 仲裁队列演示 ===")
        
        try:
            # 使用仲裁队列，提供更好的性能和可靠性
            self.channel.queue_declare(
                queue='quorum_durable_queue',
                durable=True,
                arguments={
                    'x-queue-type': 'quorum'  # 仲裁队列
                }
            )
            print(" [*] 声明仲裁队列: quorum_durable_queue")
            
            # 发送消息
            for i in range(3):
                message = f"仲裁队列消息 {i+1}"
                self.channel.basic_publish(
                    exchange='',
                    routing_key='quorum_durable_queue',
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 持久化
                        message_id=f"quorum_{i+1}"
                    )
                )
                print(f" [x] 发送仲裁队列消息: {message}")
            
            # 创建消费者
            def callback(ch, method, properties, body):
                message = body.decode('utf-8')
                print(f" [+] 收到仲裁队列消息: {message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            self.channel.basic_consume(
                queue='quorum_durable_queue',
                on_message_callback=callback,
                auto_ack=False
            )
            
            # 消费所有消息
            message_count = 0
            start_time = time.time()
            while message_count < 3 and time.time() - start_time < 3:
                method, properties, body = self.channel.basic_get(queue='quorum_durable_queue')
                if method:
                    callback(self.channel, method, properties, body)
                    message_count += 1
                else:
                    time.sleep(0.1)
            
            self.channel.stop_consuming()
            print(f" [+] 共处理 {message_count} 条仲裁队列消息")
            
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f" [!] 创建仲裁队列失败: {e}")
            print(" [!] 可能是因为RabbitMQ版本不支持仲裁队列或单节点集群配置")
    
    def demo_batch_persistence(self):
        """演示批量持久化"""
        print("\n=== 批量持久化演示 ===")
        
        class OptimizedPersistence:
            def __init__(self, channel):
                self.channel = channel
                self.setup_persistence()
            
            def setup_persistence(self):
                """设置优化的持久化配置"""
                # 声明惰性队列，减少内存使用
                self.channel.queue_declare(
                    queue='batch_lazy_queue',
                    durable=True,
                    arguments={
                        'x-queue-mode': 'lazy'  # 惰性队列，减少内存压力
                    }
                )
                print(" [*] 声明批量惰性队列: batch_lazy_queue")
            
            def send_batch_messages(self, messages):
                """批量发送消息，减少网络开销"""
                # 启用发布者确认
                self.channel.confirm_delivery()
                
                for message in messages:
                    self.channel.basic_publish(
                        exchange='',
                        routing_key='batch_lazy_queue',
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # 持久化
                            content_type='application/json'
                        )
                    )
                
                # 确认所有消息
                confirmed = self.channel.wait_for_confirms(timeout=5)
                return confirmed
        
        # 创建批量持久化实例
        batch_persistence = OptimizedPersistence(self.channel)
        
        # 创建消息批次
        messages = []
        for i in range(10):
            message = {
                'id': i+1,
                'content': f'批量持久化消息 {i+1}',
                'timestamp': int(time.time())
            }
            messages.append(json.dumps(message))
        
        # 批量发送消息
        print(f" [x] 批量发送 {len(messages)} 条消息")
        confirmed = batch_persistence.send_batch_messages(messages)
        
        print(f" [✓] 批量持久化: {'成功' if confirmed else '失败'}")
        
        # 消费所有消息
        def callback(ch, method, properties, body):
            data = json.loads(body.decode('utf-8'))
            print(f" [+] 收到批量消息: {data['content']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='batch_lazy_queue',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 消费所有消息
        message_count = 0
        start_time = time.time()
        while message_count < len(messages) and time.time() - start_time < 5:
            method, properties, body = self.channel.basic_get(queue='batch_lazy_queue')
            if method:
                callback(self.channel, method, properties, body)
                message_count += 1
            else:
                time.sleep(0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 共处理 {message_count} 条批量消息")
    
    def run_demo(self):
        """运行消息持久化演示"""
        print("\n=== 消息持久化演示 ===")
        
        self.connect()
        
        try:
            self.demo_persistence_setup()
            self.demo_non_persistence_setup()
            self.demo_lazy_queue()
            self.demo_quorum_queue()
            self.demo_batch_persistence()
        finally:
            self.disconnect()
        
        print("\n [*] 消息持久化演示完成")


class TransactionsDemo:
    """事务机制演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def setup_infrastructure(self):
        """设置基础设施"""
        self.channel.queue_declare(queue='transaction_queue', durable=True)
        self.channel.queue_declare(queue='confirm_queue', durable=True)
        
        print(" [*] 基础设施设置完成")
    
    def demo_transaction(self):
        """演示事务"""
        print("\n=== 事务演示 ===")
        
        try:
            # 开始事务
            self.channel.tx_select()
            print(" [*] 开始事务")
            
            # 在事务中执行多个操作
            for i in range(5):
                message = f'事务消息 {i+1}'
                self.channel.basic_publish(
                    exchange='',
                    routing_key='transaction_queue',
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2  # 持久化
                    )
                )
                print(f" [x] 在事务中发送: {message}")
            
            # 提交事务
            self.channel.tx_commit()
            print(" [*] 事务提交成功")
            success = True
            
        except Exception as e:
            print(f" [!] 事务执行失败: {e}")
            try:
                # 回滚事务
                self.channel.tx_rollback()
                print(" [*] 事务回滚成功")
            except Exception as rollback_error:
                print(f" [!] 事务回滚失败: {rollback_error}")
            success = False
        
        # 验证事务结果
        if success:
            message_count = 0
            for i in range(5):
                method, properties, body = self.channel.basic_get(queue='transaction_queue')
                if method:
                    message_count += 1
                    print(f" [+] 确认事务消息: {body.decode('utf-8')}")
                    self.channel.basic_ack(delivery_tag=method.delivery_tag)
            
            print(f" [+] 事务验证: {message_count}/5 条消息")
    
    def demo_transaction_rollback(self):
        """演示事务回滚"""
        print("\n=== 事务回滚演示 ===")
        
        try:
            # 开始事务
            self.channel.tx_select()
            print(" [*] 开始事务")
            
            # 在事务中执行操作
            for i in range(3):
                message = f'回滚测试消息 {i+1}'
                self.channel.basic_publish(
                    exchange='',
                    routing_key='transaction_queue',
                    body=message
                )
                print(f" [x] 在事务中发送: {message}")
            
            # 模拟异常
            print(" [*] 模拟异常，回滚事务")
            raise Exception("模拟处理异常")
            
        except Exception as e:
            print(f" [!] 事务执行失败: {e}")
            try:
                # 回滚事务
                self.channel.tx_rollback()
                print(" [*] 事务回滚成功")
            except Exception as rollback_error:
                print(f" [!] 事务回滚失败: {rollback_error}")
        
        # 验证回滚结果
        message_count = 0
        for i in range(5):  # 最多检查5次
            method, properties, body = self.channel.basic_get(queue='transaction_queue')
            if method:
                message_count += 1
                print(f" [+] 队列中消息: {body.decode('utf-8')}")
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                break
        
        print(f" [+] 回滚验证: 队列中有 {message_count} 条消息（应该是0）")
    
    def compare_mechanisms(self):
        """比较事务与确认机制"""
        print("\n=== 事务与确认机制比较 ===")
        
        class CompareMechanisms:
            def __init__(self, channel):
                self.channel = channel
            
            def with_transaction(self, messages):
                """使用事务发送消息"""
                start_time = time.time()
                
                try:
                    # 开始事务
                    self.channel.tx_select()
                    
                    # 发送消息
                    for message in messages:
                        self.channel.basic_publish(
                            exchange='',
                            routing_key='transaction_queue',
                            body=message
                        )
                    
                    # 提交事务
                    self.channel.tx_commit()
                    success = True
                except Exception as e:
                    print(f" [!] 事务失败: {e}")
                    try:
                        self.channel.tx_rollback()
                    except:
                        pass
                    success = False
                
                end_time = time.time()
                duration = end_time - start_time
                
                return success, duration
            
            def with_confirms(self, messages):
                """使用发布者确认发送消息"""
                start_time = time.time()
                
                try:
                    # 启用确认
                    self.channel.confirm_delivery()
                    
                    # 发送消息
                    for message in messages:
                        self.channel.basic_publish(
                            exchange='',
                            routing_key='confirm_queue',
                            body=message
                        )
                    
                    # 等待确认
                    confirmed = self.channel.wait_for_confirms(timeout=5)
                    success = confirmed
                except Exception as e:
                    print(f" [!] 确认失败: {e}")
                    success = False
                
                end_time = time.time()
                duration = end_time - start_time
                
                return success, duration
            
            def compare_performance(self, message_count=20):
                """比较性能"""
                messages = [f'性能测试消息 {i}' for i in range(message_count)]
                
                # 测试事务性能
                print(" [x] 测试事务性能...")
                tx_success, tx_duration = self.with_transaction(messages)
                print(f" [+] 事务: 成功={tx_success}, 耗时={tx_duration:.3f}秒")
                
                # 测试确认性能
                print(" [x] 测试确认性能...")
                confirm_success, confirm_duration = self.with_confirms(messages)
                print(f" [+] 确认: 成功={confirm_success}, 耗时={confirm_duration:.3f}秒")
                
                # 计算性能差异
                if tx_duration > 0 and confirm_duration > 0:
                    speedup = tx_duration / confirm_duration
                    print(f" [+] 发布者确认比事务快 {speedup:.2f} 倍")
                
                return {
                    'transaction': {'success': tx_success, 'duration': tx_duration},
                    'confirm': {'success': confirm_success, 'duration': confirm_duration},
                    'speedup': speedup if tx_duration > 0 and confirm_duration > 0 else 0
                }
        
        # 创建比较实例
        comparator = CompareMechanisms(self.channel)
        
        # 运行性能比较
        results = comparator.compare_performance(message_count=20)
        
        # 显示结果
        print(f"\n [+] 性能比较结果:")
        print(f"     事务: {results['transaction']['success']}, {results['transaction']['duration']:.3f}秒")
        print(f"     确认: {results['confirm']['success']}, {results['confirm']['duration']:.3f}秒")
        print(f"     速度比: {results['speedup']:.2f}倍")
    
    def run_demo(self):
        """运行事务机制演示"""
        print("\n=== 事务机制演示 ===")
        
        self.connect()
        
        try:
            self.setup_infrastructure()
            self.demo_transaction()
            self.demo_transaction_rollback()
            self.compare_mechanisms()
        finally:
            self.disconnect()
        
        print("\n [*] 事务机制演示完成")


class DeadLetterDemo:
    """死信机制演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
        self.consumers = []
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def setup_dead_letter_infrastructure(self):
        """设置死信机制"""
        # 1. 声明死信交换机
        self.channel.exchange_declare(
            exchange='dlx_exchange',
            exchange_type='direct',
            durable=True
        )
        print(" [*] 声明死信交换机: dlx_exchange")
        
        # 2. 声明死信队列
        self.channel.queue_declare(
            queue='dlx_queue',
            durable=True
        )
        print(" [*] 声明死信队列: dlx_queue")
        
        # 3. 绑定死信队列到死信交换机
        self.channel.queue_bind(
            exchange='dlx_exchange',
            queue='dlx_queue',
            routing_key='dlx_routing_key'
        )
        print(" [*] 绑定死信队列到死信交换机")
        
        # 4. 声明主队列并配置死信交换机
        self.channel.queue_declare(
            queue='main_queue',
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx_exchange',      # 死信交换机名称
                'x-dead-letter-routing-key': 'dlx_routing_key' # 死信路由键
            }
        )
        print(" [*] 声明主队列并配置死信交换机: main_queue")
        
        # 5. TTL队列（消息TTL过期后变成死信）
        self.channel.queue_declare(
            queue='ttl_queue',
            durable=True,
            arguments={
                'x-message-ttl': 5000,  # 5秒TTL
                'x-dead-letter-exchange': 'dlx_exchange',
                'x-dead-letter-routing-key': 'dlx_routing_key'
            }
        )
        print(" [*] 声明TTL队列: ttl_queue (5秒TTL)")
        
        # 6. 长度限制队列（队列满后新消息变成死信）
        self.channel.queue_declare(
            queue='maxlen_queue',
            durable=True,
            arguments={
                'x-max-length': 3,     # 最大3条消息
                'x-dead-letter-exchange': 'dlx_exchange',
                'x-dead-letter-routing-key': 'dlx_routing_key'
            }
        )
        print(" [*] 声明长度限制队列: maxlen_queue (最大3条消息)")
    
    def start_dead_letter_consumer(self):
        """启动死信消费者"""
        def dead_letter_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            
            # 获取原始消息信息
            original_headers = properties.headers if properties.headers else {}
            death_info = original_headers.get('x-death', [{}])[0] if original_headers.get('x-death') else {}
            
            original_exchange = death_info.get('exchange', 'unknown')
            original_routing_keys = death_info.get('routing-keys', ['unknown'])
            original_queue = death_info.get('queue', 'unknown')
            reason = death_info.get('reason', 'unknown')
            count = death_info.get('count', 1)
            
            print(f" [†] 死信消息: {message}")
            print(f"     原始交换机: {original_exchange}")
            print(f"     原始路由键: {original_routing_keys}")
            print(f"     原始队列: {original_queue}")
            print(f"     死信原因: {reason}")
            print(f"     死信次数: {count}")
            
            # 分析死信原因并采取相应措施
            self.analyze_and_handle(message, reason, original_headers)
            
            # 确认死信消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='dlx_queue',
            on_message_callback=dead_letter_callback,
            auto_ack=False
        )
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        print(" [*] 死信消费者已启动")
        return consumer
    
    def analyze_and_handle(self, message, reason, headers):
        """分析死信原因并处理"""
        if reason == 'expired':
            print("     处理: 消息TTL过期，记录日志")
            self.log_expired_message(message, headers)
        
        elif reason == 'maxlen':
            print("     处理: 队列达到最大长度，增加消费者或调整队列大小")
            self.handle_maxlen_issue(message, headers)
        
        elif reason == 'rejected':
            print("     处理: 消息被消费者拒绝，检查消息格式或处理逻辑")
            self.handle_rejected_message(message, headers)
        
        else:
            print(f"     处理: 未知死信原因 {reason}，人工处理")
            self.unknown_dead_letter(message, reason, headers)
    
    def log_expired_message(self, message, headers):
        """记录过期消息"""
        print(f"     [日志] 过期消息: {message}")
    
    def handle_maxlen_issue(self, message, headers):
        """处理队列长度问题"""
        print("     [警报] 队列达到最大长度")
    
    def handle_rejected_message(self, message, headers):
        """处理被拒绝的消息"""
        # 可以将消息发送到修复队列
        self.send_to_repair_queue(message, headers)
    
    def send_to_repair_queue(self, message, headers):
        """发送消息到修复队列"""
        # 声明修复队列
        self.channel.queue_declare(queue='repair_queue', durable=True)
        
        # 发送消息到修复队列
        self.channel.basic_publish(
            exchange='',
            routing_key='repair_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers=headers
            )
        )
        
        print("     已将消息发送到修复队列")
    
    def unknown_dead_letter(self, message, reason, headers):
        """处理未知死信"""
        # 发送通知给管理员
        print(f"     [警报] 需要人工处理的消息: {message}")
    
    def demo_ttl_dead_letter(self):
        """演示TTL死信"""
        print("\n=== TTL死信演示 ===")
        
        # 发送带TTL的消息
        for i in range(3):
            message = f"TTL测试消息 {i+1}"
            self.channel.basic_publish(
                exchange='',
                routing_key='ttl_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    expiration=str((i+1) * 2000)  # 2秒, 4秒, 6秒
                )
            )
            print(f" [x] 发送TTL消息 {i+1} (TTL: {(i+1)*2}秒): {message}")
        
        # 等待消息过期
        print(" [*] 等待消息过期...")
        time.sleep(8)  # 等待8秒，确保所有消息过期
    
    def demo_maxlen_dead_letter(self):
        """演示队列长度限制死信"""
        print("\n=== 队列长度限制死信演示 ===")
        
        # 发送超过限制的消息
        for i in range(6):  # 发送6条消息，超过限制的3条
            message = f"长度限制测试消息 {i+1}"
            self.channel.basic_publish(
                exchange='',
                routing_key='maxlen_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )
            
            if i < 3:  # 只显示前3条
                print(f" [x] 发送消息 {i+1}: {message}")
        
        print(" [*] 队列最多保存3条消息，其余3条变成死信")
        time.sleep(2)  # 等待死信处理
    
    def demo_rejected_dead_letter(self):
        """演示被拒绝的死信"""
        print("\n=== 被拒绝的死信演示 ===")
        
        # 创建拒绝测试队列
        self.channel.queue_declare(
            queue='reject_test_queue',
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx_exchange',
                'x-dead-letter-routing-key': 'dlx_routing_key'
            }
        )
        
        # 发送测试消息
        for i in range(3):
            message = f"拒绝测试消息 {i+1}"
            self.channel.basic_publish(
                exchange='',
                routing_key='reject_test_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )
            print(f" [x] 发送消息 {i+1}: {message}")
        
        # 创建拒绝消费者
        def reject_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            print(f" [x] 拒绝消息: {message}")
            # 拒绝消息，不重新入队，发送到死信队列
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_consume(
            queue='reject_test_queue',
            on_message_callback=reject_callback,
            auto_ack=False
        )
        
        # 消费并拒绝所有消息
        for i in range(3):
            method, properties, body = self.channel.basic_get(queue='reject_test_queue')
            if method:
                reject_callback(self.channel, method, properties, body)
        
        self.channel.stop_consuming()
        print(" [*] 所有消息被拒绝并发送到死信队列")
        time.sleep(2)  # 等待死信处理
    
    def run_demo(self):
        """运行死信机制演示"""
        print("\n=== 死信机制演示 ===")
        
        self.connect()
        
        try:
            self.setup_dead_letter_infrastructure()
            
            # 启动死信消费者
            self.start_dead_letter_consumer()
            time.sleep(1)  # 等待消费者启动
            
            self.demo_ttl_dead_letter()
            self.demo_maxlen_dead_letter()
            self.demo_rejected_dead_letter()
            
            # 等待死信处理完成
            time.sleep(3)
            
        finally:
            self.disconnect()
        
        print("\n [*] 死信机制演示完成")


class RetryMechanismDemo:
    """消息重试机制演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
        self.consumers = []
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def setup_simple_retry_infrastructure(self):
        """设置简单重试基础设施"""
        # 主队列
        self.channel.queue_declare(queue='retry_main_queue', durable=True)
        
        # 重试队列
        self.channel.queue_declare(
            queue='retry_queue',
            durable=True,
            arguments={
                'x-message-ttl': 5000,  # 5秒后重试
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': 'retry_main_queue'
            }
        )
        
        # 失败队列
        self.channel.queue_declare(queue='failed_queue', durable=True)
        
        print(" [*] 简单重试基础设施设置完成")
    
    def demo_simple_retry(self):
        """演示简单重试"""
        print("\n=== 简单重试演示 ===")
        
        self.setup_simple_retry_infrastructure()
        
        # 创建重试消费者
        processed = set()  # 跟踪已处理的消息
        retries = {}       # 跟踪重试次数
        
        def retry_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            headers = properties.headers if properties.headers else {}
            retry_count = headers.get('x-retry-count', 0)
            
            # 检查是否已处理过
            if message in processed:
                print(f" [✓] 消息已处理过: {message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            try:
                # 模拟处理
                if "fail" in message.lower():
                    raise Exception(f"模拟处理失败: {message}")
                
                # 成功处理
                print(f" [✓] 处理成功: {message}")
                processed.add(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f" [✗] 处理失败: {e}")
                
                # 检查是否达到最大重试次数
                if retry_count >= 2:
                    print(f" [✗] 达到最大重试次数，发送到失败队列: {message}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    
                    # 手动发送到失败队列
                    self.channel.basic_publish(
                        exchange='',
                        routing_key='failed_queue',
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            headers={
                                'x-retry-count': retry_count,
                                'original-queue': 'retry_main_queue',
                                'failure-reason': str(e)
                            }
                        )
                    )
                else:
                    # 发送到重试队列
                    retry_count += 1
                    print(f" [↻] 发送到重试队列, 重试次数: {retry_count}")
                    
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    
                    # 手动发送到重试队列
                    self.channel.basic_publish(
                        exchange='',
                        routing_key='retry_queue',
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            headers={
                                'x-retry-count': retry_count,
                                'original-queue': 'retry_main_queue',
                                'failure-reason': str(e)
                            }
                        )
                    )
        
        self.channel.basic_consume(
            queue='retry_main_queue',
            on_message_callback=retry_callback,
            auto_ack=False
        )
        
        # 创建重试队列消费者
        def retry_queue_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            headers = properties.headers if properties.headers else {}
            retry_count = headers.get('x-retry-count', 0)
            
            print(f" [↻] 从重试队列收到: {message} (重试次数: {retry_count})")
            
            # 拒绝消息，将发送回主队列
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.channel.basic_consume(
            queue='retry_queue',
            on_message_callback=retry_queue_callback,
            auto_ack=False
        )
        
        # 创建失败队列消费者
        def failed_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            headers = properties.headers if properties.headers else {}
            retry_count = headers.get('x-retry-count', 0)
            failure_reason = headers.get('failure-reason', 'unknown')
            
            print(f" [✗] 失败队列消息: {message}")
            print(f"     重试次数: {retry_count}")
            print(f"     失败原因: {failure_reason}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='failed_queue',
            on_message_callback=failed_callback,
            auto_ack=False
        )
        
        # 发送测试消息
        test_messages = [
            "成功消息 1",
            "失败消息 1 - fail",
            "成功消息 2",
            "失败消息 2 - fail",
            "成功消息 3"
        ]
        
        for message in test_messages:
            self.channel.basic_publish(
                exchange='',
                routing_key='retry_main_queue',
                body=message
            )
            print(f" [x] 发送: {message}")
        
        # 启动消费者
        print("\n [*] 启动重试消费者...")
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        # 等待处理完成
        time.sleep(15)  # 等待15秒，足够重试完成
    
    def setup_exponential_backoff_infrastructure(self):
        """设置指数退避重试基础设施"""
        # 主队列
        self.channel.queue_declare(queue='exp_main_queue', durable=True)
        
        # 设置死信交换机
        self.channel.exchange_declare(exchange='exp_retry_exchange', exchange_type='direct', durable=True)
        
        # 为每个重试级别创建队列
        self.initial_delay = 2  # 初始延迟2秒
        self.max_delay = 30    # 最大延迟30秒
        self.max_retries = 3    # 最大重试次数
        self.backoff_factor = 2 # 退避因子
        
        for retry_count in range(1, self.max_retries + 1):
            # 计算延迟时间（指数增长）
            delay = min(
                self.initial_delay * (self.backoff_factor ** (retry_count - 1)),
                self.max_delay
            )
            
            retry_queue_name = f'exp_retry_{retry_count}'
            self.channel.queue_declare(
                queue=retry_queue_name,
                durable=True,
                arguments={
                    'x-message-ttl': delay * 1000,  # TTL毫秒
                    'x-dead-letter-exchange': 'exp_retry_exchange',
                    'x-dead-letter-routing-key': 'exp_retry' if retry_count < self.max_retries else 'exp_failed'
                }
            )
            
            # 绑定重试队列到重试交换机
            if retry_count < self.max_retries:
                self.channel.queue_bind(
                    exchange='exp_retry_exchange',
                    queue=retry_queue_name,
                    routing_key='exp_retry'
                )
        
        # 失败队列
        self.channel.queue_declare(queue='exp_failed_queue', durable=True)
        self.channel.queue_bind(
            exchange='exp_retry_exchange',
            queue='exp_failed_queue',
            routing_key='exp_failed'
        )
        
        print(" [*] 指数退避重试基础设施设置完成")
    
    def demo_exponential_backoff(self):
        """演示指数退避重试"""
        print("\n=== 指数退避重试演示 ===")
        
        self.setup_exponential_backoff_infrastructure()
        
        # 创建指数退避消费者
        def exp_backoff_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            headers = properties.headers if properties.headers else {}
            retry_count = headers.get('x-retry-count', 0)
            
            try:
                # 处理消息
                if "fail" in message.lower():
                    raise Exception(f"模拟处理失败: {message}")
                
                # 成功处理
                print(f" [✓] 处理成功: {message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f" [✗] 处理失败: {e}")
                
                # 检查是否达到最大重试次数
                if retry_count >= self.max_retries:
                    print(f" [✗] 达到最大重试次数，发送到失败队列: {message}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                else:
                    # 计算延迟时间
                    delay = min(
                        self.initial_delay * (self.backoff_factor ** retry_count),
                        self.max_delay
                    )
                    
                    retry_count += 1
                    retry_queue_name = f'exp_retry_{retry_count}'
                    
                    print(f" [↻] 指数退避重试: 延迟 {delay}秒, 重试次数: {retry_count}")
                    
                    # 拒绝消息并重试
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    
                    # 手动发送到重试队列
                    self.channel.basic_publish(
                        exchange='',
                        routing_key=retry_queue_name,
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            headers={
                                'x-retry-count': retry_count,
                                'original-queue': 'exp_main_queue',
                                'failure-reason': str(e),
                                'retry-delay': delay
                            }
                        )
                    )
        
        self.channel.basic_consume(
            queue='exp_main_queue',
            on_message_callback=exp_backoff_callback,
            auto_ack=False
        )
        
        # 创建失败队列消费者
        def exp_failed_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            headers = properties.headers if properties.headers else {}
            retry_count = headers.get('x-retry-count', 0)
            failure_reason = headers.get('failure-reason', 'unknown')
            
            print(f" [✗] 指数退避失败消息: {message}")
            print(f"     重试次数: {retry_count}")
            print(f"     失败原因: {failure_reason}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='exp_failed_queue',
            on_message_callback=exp_failed_callback,
            auto_ack=False
        )
        
        # 发送测试消息
        test_messages = [
            "指数退避成功消息",
            "指数退避失败消息 - fail"
        ]
        
        for message in test_messages:
            self.channel.basic_publish(
                exchange='',
                routing_key='exp_main_queue',
                body=message
            )
            print(f" [x] 发送: {message}")
        
        # 启动消费者
        print("\n [*] 启动指数退避消费者...")
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        # 等待处理完成
        time.sleep(20)  # 等待20秒，足够指数退避重试完成
    
    def run_demo(self):
        """运行消息重试机制演示"""
        print("\n=== 消息重试机制演示 ===")
        
        self.connect()
        
        try:
            self.demo_simple_retry()
            time.sleep(2)  # 等待旧消息清理
            self.demo_exponential_backoff()
        finally:
            self.disconnect()
        
        print("\n [*] 消息重试机制演示完成")


class ReliabilityBestPracticesDemo:
    """可靠性最佳实践演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
        self.consumers = []
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def setup_reliable_infrastructure(self):
        """设置可靠性基础设施"""
        # 1. 持久化交换机
        self.channel.exchange_declare(
            exchange='reliable_exchange',
            exchange_type='direct',
            durable=True
        )
        
        # 2. 仲裁队列（高可靠性和性能）
        self.channel.queue_declare(
            queue='reliable_queue',
            durable=True,
            arguments={
                'x-queue-type': 'quorum',
                'x-quorum-initial-group-size': 1  # 单节点集群设为1
            }
        )
        
        # 3. 死信机制
        self.channel.exchange_declare(exchange='dlx', exchange_type='direct', durable=True)
        self.channel.queue_declare(queue='dead_letter_queue', durable=True)
        self.channel.queue_bind(exchange='dlx', queue='dead_letter_queue', routing_key='dead')
        
        # 4. 重试队列
        self.channel.queue_declare(
            queue='retry_queue',
            durable=True,
            arguments={
                'x-message-ttl': 30000,  # 30秒后重试
                'x-dead-letter-exchange': 'reliable_exchange',
                'x-dead-letter-routing-key': 'reliable'
            }
        )
        
        # 5. 主队列配置
        self.channel.queue_declare(
            queue='reliable_queue',
            durable=True,
            arguments={
                'x-queue-type': 'quorum',
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': 'dead'
            }
        )
        
        # 6. 绑定
        self.channel.queue_bind(
            exchange='reliable_exchange',
            queue='reliable_queue',
            routing_key='reliable'
        )
        
        print(" [*] 可靠性基础设施设置完成")
    
    def demo_reliable_publisher(self):
        """演示可靠发布者"""
        print("\n=== 可靠发布者演示 ===")
        
        class ReliablePublisher:
            def __init__(self, channel, exchange_name):
                self.channel = channel
                self.exchange_name = exchange_name
                self.confirmed_count = 0
                self.nacked_count = 0
                self.returned_count = 0
                
                # 设置确认回调
                self.channel.add_callback(
                    self.on_ack,
                    replies=[pika.spec.Basic.Ack],
                    one_shot=False
                )
                
                self.channel.add_callback(
                    self.on_nack,
                    replies=[pika.spec.Basic.Nack],
                    one_shot=False
                )
                
                # 设置返回回调
                self.channel.add_on_return_callback(self.on_return)
                
                # 启用确认
                self.channel.confirm_delivery()
            
            def on_ack(self, frame):
                """确认回调"""
                self.confirmed_count += 1
                print(f" [✓] 消息确认: {frame.method.delivery_tag}")
            
            def on_nack(self, frame):
                """未确认回调"""
                self.nacked_count += 1
                print(f" [✗] 消息未确认: {frame.method.delivery_tag}")
            
            def on_return(self, method_frame, header_frame, body):
                """消息返回回调"""
                self.returned_count += 1
                message = body.decode('utf-8')
                print(f" [←] 消息返回: {message} (原因: {method_frame.reply_text})")
            
            def publish_reliable_message(self, routing_key, message):
                """发送可靠消息"""
                try:
                    self.channel.basic_publish(
                        exchange=self.exchange_name,
                        routing_key=routing_key,
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # 持久化
                            priority=5,       # 中等优先级
                            timestamp=int(time.time()),  # 时间戳
                            message_id=str(uuid.uuid4()), # 消息ID
                            headers={
                                'source': 'reliable_publisher',
                                'version': '1.0'
                            }
                        ),
                        mandatory=True  # 如果无法路由，返回给生产者
                    )
                    
                    # 等待确认
                    confirmed = self.channel.wait_for_confirms(timeout=5)
                    if confirmed:
                        print(f" [✓] 消息可靠发送成功: {message}")
                        return True
                    else:
                        print(f" [✗] 消息发送未确认: {message}")
                        return False
                except Exception as e:
                    print(f" [✗] 消息发送失败: {e}")
                    return False
        
        # 创建可靠发布者
        publisher = ReliablePublisher(self.channel, 'reliable_exchange')
        
        # 发送测试消息
        success_count = 0
        total_count = 5
        
        for i in range(total_count):
            message = f"可靠发布消息 {i+1}"
            confirmed = publisher.publish_reliable_message('reliable', message)
            if confirmed:
                success_count += 1
        
        print(f" [+] 可靠发布者统计:")
        print(f"     确认: {publisher.confirmed_count}")
        print(f"     未确认: {publisher.nacked_count}")
        print(f"     返回: {publisher.returned_count}")
        print(f"     成功率: {success_count/total_count*100:.2f}%")
    
    def demo_reliable_consumer(self):
        """演示可靠消费者"""
        print("\n=== 可靠消费者演示 ===")
        
        processed = []
        failed = []
        
        def reliable_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            
            try:
                # 模拟处理
                print(f" [→] 处理消息: {message}")
                
                # 模拟处理时间
                time.sleep(0.2)
                
                # 模拟失败
                if "fail" in message.lower():
                    raise Exception("模拟处理失败")
                
                # 成功处理
                processed.append(message)
                print(f" [✓] 处理成功: {message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f" [✗] 处理失败: {e}")
                
                # 检查是否应该重试
                headers = properties.headers if properties.headers else {}
                retry_count = headers.get('x-retry-count', 0)
                
                if retry_count < 2:
                    # 重试
                    print(f" [↻] 重试消息: {message} (重试次数: {retry_count+1})")
                    
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    
                    # 发送到重试队列
                    self.channel.basic_publish(
                        exchange='',
                        routing_key='retry_queue',
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            headers={
                                'x-retry-count': retry_count + 1,
                                'original-queue': 'reliable_queue',
                                'failure-reason': str(e)
                            }
                        )
                    )
                else:
                    # 失败，发送到死信队列
                    failed.append(message)
                    print(f" [†] 发送到死信队列: {message}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        # 设置预取数量
        self.channel.basic_qos(prefetch_count=1)
        
        self.channel.basic_consume(
            queue='reliable_queue',
            on_message_callback=reliable_callback,
            auto_ack=False
        )
        
        # 创建死信队列消费者
        def dead_letter_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            headers = properties.headers if properties.headers else {}
            retry_count = headers.get('x-retry-count', 0)
            failure_reason = headers.get('failure-reason', 'unknown')
            
            print(f" [†] 死信消息: {message}")
            print(f"     重试次数: {retry_count}")
            print(f"     失败原因: {failure_reason}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='dead_letter_queue',
            on_message_callback=dead_letter_callback,
            auto_ack=False
        )
        
        # 启动消费者
        print(" [*] 启动可靠消费者...")
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        # 发送测试消息
        test_messages = [
            "可靠处理消息 1",
            "可靠处理消息 2",
            "可靠处理消息 3 - fail",
            "可靠处理消息 4",
            "可靠处理消息 5 - fail"
        ]
        
        for message in test_messages:
            self.channel.basic_publish(
                exchange='reliable_exchange',
                routing_key='reliable',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )
            print(f" [x] 发送: {message}")
        
        # 等待处理完成
        time.sleep(15)
        
        # 显示统计
        print(f" [+] 可靠消费者统计:")
        print(f"     处理成功: {len(processed)}")
        print(f"     处理失败: {len(failed)}")
        print(f"     成功率: {len(processed)/len(test_messages)*100:.2f}%")
    
    def run_demo(self):
        """运行可靠性最佳实践演示"""
        print("\n=== 可靠性最佳实践演示 ===")
        
        self.connect()
        
        try:
            self.setup_reliable_infrastructure()
            self.demo_reliable_publisher()
            time.sleep(2)  # 等待消息处理
            self.demo_reliable_consumer()
            
            # 等待处理完成
            time.sleep(10)
        finally:
            self.disconnect()
        
        print("\n [*] 可靠性最佳实践演示完成")


class ReliabilityMonitoringDemo:
    """可靠性监控演示"""
    
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
        self.consumers = []
        
        # 监控指标
        self.metrics = {
            'published': 0,
            'confirmed': 0,
            'nacked': 0,
            'returned': 0,
            'consumed': 0,
            'rejected': 0
        }
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        print(f" [*] Connected to RabbitMQ at {self.host}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [*] Disconnected from RabbitMQ")
    
    def setup_monitoring_infrastructure(self):
        """设置监控基础设施"""
        # 声明交换机和队列
        self.channel.exchange_declare(
            exchange='monitor_exchange',
            exchange_type='direct',
            durable=True
        )
        self.channel.queue_declare(queue='monitor_queue', durable=True)
        self.channel.queue_bind(
            exchange='monitor_exchange',
            queue='monitor_queue',
            routing_key='monitor_key'
        )
        
        print(" [*] 监控基础设施设置完成")
    
    def setup_monitoring_callbacks(self):
        """设置监控回调"""
        # 启用发布者确认
        self.channel.confirm_delivery()
        
        # 设置确认回调
        self.channel.add_callback(
            self.on_ack,
            replies=[pika.spec.Basic.Ack],
            one_shot=False
        )
        
        # 设置未确认回调
        self.channel.add_callback(
            self.on_nack,
            replies=[pika.spec.Basic.Nack],
            one_shot=False
        )
        
        # 设置返回回调
        self.channel.add_on_return_callback(self.on_return)
    
    def on_ack(self, frame):
        """确认回调"""
        self.metrics['confirmed'] += 1
        print(f" [✓] 消息确认: {frame.method.delivery_tag}")
    
    def on_nack(self, frame):
        """未确认回调"""
        self.metrics['nacked'] += 1
        print(f" [✗] 消息未确认: {frame.method.delivery_tag}")
    
    def on_return(self, method_frame, header_frame, body):
        """消息返回回调"""
        self.metrics['returned'] += 1
        message = body.decode('utf-8')
        print(f" [←] 消息返回: {message} (原因: {method_frame.reply_text})")
    
    def demo_reliability_monitoring(self):
        """演示可靠性监控"""
        print("\n=== 可靠性监控演示 ===")
        
        self.setup_monitoring_infrastructure()
        self.setup_monitoring_callbacks()
        
        # 发送监控消息
        print("\n发送监控消息:")
        test_messages = [
            "监控消息 1",
            "监控消息 2",
            "监控消息 3",
            "监控消息 4",
            "监控消息 5"
        ]
        
        for message in test_messages:
            self.send_monitored_message('monitor_exchange', 'monitor_key', message)
        
        # 显示发布统计
        print("\n发布统计:")
        self.get_metrics()
        
        # 启动消费者监控
        self.monitor_consumer('monitor_queue')
        
        # 等待处理完成
        time.sleep(5)
        
        # 显示最终统计
        print("\n最终统计:")
        self.get_metrics()
    
    def send_monitored_message(self, exchange, routing_key, message):
        """发送监控消息"""
        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True
            )
            
            self.metrics['published'] += 1
            print(f" [x] 发送监控消息: {message}")
            return True
        except Exception as e:
            print(f" [!] 发送消息失败: {e}")
            return False
    
    def monitor_consumer(self, queue):
        """监控消费者"""
        def monitored_callback(ch, method, properties, body):
            message = body.decode('utf-8')
            
            try:
                # 处理消息
                print(f" [→] 处理消息: {message}")
                
                # 模拟处理
                time.sleep(0.2)
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                self.metrics['consumed'] += 1
                print(f" [✓] 消费成功: {message}")
                
            except Exception as e:
                print(f" [✗] 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                self.metrics['rejected'] += 1
        
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=monitored_callback,
            auto_ack=False
        )
        
        print(f" [→] 启动监控消费者: {queue}")
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        return consumer
    
    def get_metrics(self):
        """获取监控指标"""
        total = self.metrics['published']
        if total > 0:
            confirmation_rate = (self.metrics['confirmed'] / total) * 100
        else:
            confirmation_rate = 0
        
        print(f"可靠性指标:")
        print(f"  发布: {self.metrics['published']}")
        print(f"  确认: {self.metrics['confirmed']}")
        print(f"  未确认: {self.metrics['nacked']}")
        print(f"  返回: {self.metrics['returned']}")
        print(f"  消费: {self.metrics['consumed']}")
        print(f"  拒绝: {self.metrics['rejected']}")
        print(f"  确认率: {confirmation_rate:.2f}%")
        
        return self.metrics
    
    def demo_performance_monitoring(self):
        """演示性能监控"""
        print("\n=== 性能监控演示 ===")
        
        # 重置指标
        self.metrics = {
            'published': 0,
            'confirmed': 0,
            'nacked': 0,
            'returned': 0,
            'consumed': 0,
            'rejected': 0
        }
        
        # 设置监控基础设施
        self.channel.exchange_declare(exchange='perf_exchange', exchange_type='direct', durable=True)
        self.channel.queue_declare(queue='perf_queue', durable=True)
        self.channel.queue_bind(exchange='perf_exchange', queue='perf_queue', routing_key='perf_key')
        
        self.setup_monitoring_callbacks()
        
        # 启动消费者
        self.monitor_consumer('perf_queue')
        
        # 测试不同负载下的性能
        message_counts = [10, 50, 100]
        
        for count in message_counts:
            print(f"\n测试负载: {count} 条消息")
            
            # 记录开始时间
            start_time = time.time()
            
            # 发送消息
            for i in range(count):
                message = f"性能测试消息 {i+1}"
                self.send_monitored_message('perf_exchange', 'perf_key', message)
            
            # 等待确认
            self.channel.wait_for_confirms(timeout=10)
            
            # 记录结束时间
            end_time = time.time()
            duration = end_time - start_time
            
            # 计算性能指标
            throughput = count / duration if duration > 0 else 0
            confirmation_rate = (self.metrics['confirmed'] / self.metrics['published']) * 100 if self.metrics['published'] > 0 else 0
            
            print(f"性能指标 (负载 {count}):")
            print(f"  发送速率: {throughput:.2f} 条/秒")
            print(f"  确认率: {confirmation_rate:.2f}%")
            print(f"  确认延迟: {duration/count:.3f} 秒/条")
            
            # 等待处理完成
            time.sleep(3)
    
    def run_demo(self):
        """运行可靠性监控演示"""
        print("\n=== 可靠性监控演示 ===")
        
        self.connect()
        
        try:
            self.demo_reliability_monitoring()
            self.demo_performance_monitoring()
        finally:
            self.disconnect()
        
        print("\n [*] 可靠性监控演示完成")


def main():
    """主函数，根据参数运行不同的演示"""
    parser = argparse.ArgumentParser(description='RabbitMQ Message Reliability Demo')
    parser.add_argument(
        '--type',
        choices=['producer_confirms', 'consumer_confirms', 'persistence', 'transactions', 
                 'dead_letter', 'retry', 'best_practices', 'monitoring', 'all'],
        default='all',
        help='Type of demo to run (default: all)'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='RabbitMQ server host (default: localhost)'
    )
    
    args = parser.parse_args()
    
    demos = {
        'producer_confirms': PublisherConfirmsDemo(args.host),
        'consumer_confirms': ConsumerConfirmsDemo(args.host),
        'persistence': MessagePersistenceDemo(args.host),
        'transactions': TransactionsDemo(args.host),
        'dead_letter': DeadLetterDemo(args.host),
        'retry': RetryMechanismDemo(args.host),
        'best_practices': ReliabilityBestPracticesDemo(args.host),
        'monitoring': ReliabilityMonitoringDemo(args.host)
    }
    
    if args.type == 'all':
        # 运行所有演示
        for demo_type, demo in demos.items():
            try:
                demo.run_demo()
                # 等待一段时间，让RabbitMQ处理完消息
                time.sleep(2)
            except Exception as e:
                print(f"Error running {demo_type} demo: {e}")
    else:
        # 运行指定演示
        try:
            demos[args.type].run_demo()
        except Exception as e:
            print(f"Error running {args.type} demo: {e}")


if __name__ == '__main__':
    main()