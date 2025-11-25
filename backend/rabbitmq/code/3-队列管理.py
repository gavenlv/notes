#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第3章：队列管理
完整可运行的代码示例

本文件包含了第3章中所有队列管理相关的完整示例：
1. 队列属性设置
2. 不同类型队列的创建与使用
3. 队列生命周期管理
4. 消费者管理
5. 队列监控与诊断
6. 任务队列系统
7. 日志收集系统

运行方式：
python 3-队列管理.py [demo_type]

demo_type可选：
- properties  : 运行队列属性演示
- types       : 运行队列类型演示
- lifecycle   : 运行队列生命周期演示
- consumers   : 运行消费者管理演示
- monitoring  : 运行队列监控演示
- tasks       : 运行任务队列系统演示
- logs        : 运行日志收集系统演示
- all         : 依次运行所有演示（默认）
"""

import pika
import threading
import time
import sys
import json
import uuid
import random
import argparse


class QueuePropertiesDemo:
    """队列属性演示"""
    
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
    
    def demo_basic_properties(self):
        """演示基本队列属性"""
        print("\n=== 基本队列属性演示 ===")
        
        # 1. 持久化队列
        self.channel.queue_declare(
            queue='durable_queue',
            durable=True
        )
        print(" [*] 创建持久化队列: durable_queue")
        
        # 2. 非持久化队列
        self.channel.queue_declare(
            queue='transient_queue',
            durable=False
        )
        print(" [*] 创建非持久化队列: transient_queue")
        
        # 3. 独占队列
        self.channel.queue_declare(
            queue='exclusive_queue',
            exclusive=True
        )
        print(" [*] 创建独占队列: exclusive_queue")
        
        # 4. 自动删除队列
        self.channel.queue_declare(
            queue='auto_delete_queue',
            auto_delete=True
        )
        print(" [*] 创建自动删除队列: auto_delete_queue")
    
    def demo_advanced_properties(self):
        """演示高级队列属性"""
        print("\n=== 高级队列属性演示 ===")
        
        # 1. 消息TTL
        self.channel.queue_declare(
            queue='ttl_queue',
            arguments={
                'x-message-ttl': 60000  # 消息TTL为60秒
            }
        )
        print(" [*] 创建TTL队列: ttl_queue (消息TTL: 60秒)")
        
        # 2. 队列TTL
        self.channel.queue_declare(
            queue='queue_ttl',
            arguments={
                'x-expires': 1800000  # 队列TTL为30分钟
            }
        )
        print(" [*] 创建队列TTL队列: queue_ttl (队列TTL: 30分钟)")
        
        # 3. 最大长度限制
        self.channel.queue_declare(
            queue='length_limited_queue',
            arguments={
                'x-max-length': 100,  # 最大100条消息
                'x-overflow': 'drop-head'  # 溢出时删除头部消息
            }
        )
        print(" [*] 创建长度限制队列: length_limited_queue (最大100条消息)")
        
        # 4. 大小限制
        self.channel.queue_declare(
            queue='size_limited_queue',
            arguments={
                'x-max-length-bytes': 1024 * 1024  # 最大1MB
            }
        )
        print(" [*] 创建大小限制队列: size_limited_queue (最大1MB)")
        
        # 5. 死信交换机
        # 先创建死信交换机和队列
        self.channel.exchange_declare(exchange='dlx_exchange', exchange_type='direct')
        self.channel.queue_declare(queue='dlx_queue')
        self.channel.queue_bind(
            exchange='dlx_exchange',
            queue='dlx_queue',
            routing_key='dlx_routing_key'
        )
        print(" [*] 创建死信交换机和队列: dlx_exchange -> dlx_queue")
        
        # 创建主队列并配置死信交换机
        self.channel.queue_declare(
            queue='main_queue',
            arguments={
                'x-dead-letter-exchange': 'dlx_exchange',
                'x-dead-letter-routing-key': 'dlx_routing_key'
            }
        )
        print(" [*] 创建主队列: main_queue (配置死信交换机)")
        
        # 6. 优先级队列
        self.channel.queue_declare(
            queue='priority_queue',
            arguments={
                'x-max-priority': 10  # 最大优先级为10
            }
        )
        print(" [*] 创建优先级队列: priority_queue (最大优先级: 10)")
    
    def test_ttl_queue(self):
        """测试TTL队列"""
        print("\n=== 测试TTL队列 ===")
        
        # 发送消息到TTL队列
        for i in range(3):
            self.channel.basic_publish(
                exchange='',
                routing_key='ttl_queue',
                body=f'TTL测试消息 {i+1}'
            )
            print(f" [x] 发送消息到TTL队列: TTL测试消息 {i+1}")
        
        # 检查队列中的消息数
        for i in range(3):
            method_frame = self.channel.queue_declare(queue='ttl_queue', passive=True)
            message_count = method_frame.method.message_count
            print(f" [+] {i+1}秒后队列中消息数: {message_count}")
            time.sleep(1)
        
        # 等待消息过期
        print(" [*] 等待消息过期...")
        time.sleep(61)
        
        # 再次检查队列中的消息数
        method_frame = self.channel.queue_declare(queue='ttl_queue', passive=True)
        message_count = method_frame.method.message_count
        print(f" [+] 61秒后队列中消息数: {message_count}")
    
    def test_length_limited_queue(self):
        """测试长度限制队列"""
        print("\n=== 测试长度限制队列 ===")
        
        # 发送超过限制的消息
        for i in range(15):  # 发送15条消息，超过100的限制
            self.channel.basic_publish(
                exchange='',
                routing_key='length_limited_queue',
                body=f'长度限制测试消息 {i+1}'
            )
            if i < 5:  # 只显示前5条
                print(f" [x] 发送消息到长度限制队列: 长度限制测试消息 {i+1}")
        
        # 检查队列中的消息数
        method_frame = self.channel.queue_declare(queue='length_limited_queue', passive=True)
        message_count = method_frame.method.message_count
        print(f" [+] 队列中消息数: {message_count} (最多100条)")
    
    def test_priority_queue(self):
        """测试优先级队列"""
        print("\n=== 测试优先级队列 ===")
        
        # 发送不同优先级的消息
        priorities = [1, 10, 5, 8, 2, 9, 3]
        messages = [
            "低优先级消息 1",
            "最高优先级消息 1",
            "中等优先级消息 1",
            "高优先级消息 1",
            "低优先级消息 2",
            "最高优先级消息 2",
            "中等优先级消息 2"
        ]
        
        for priority, message in zip(priorities, messages):
            self.channel.basic_publish(
                exchange='',
                routing_key='priority_queue',
                body=message,
                properties=pika.BasicProperties(priority=priority)
            )
            print(f" [x] 发送优先级 {priority} 消息: {message}")
        
        # 创建消费者接收消息
        received_messages = []
        
        def callback(ch, method, properties, body):
            received_messages.append({
                'priority': properties.priority,
                'body': body.decode('utf-8')
            })
            print(f" [+] 收到优先级 {properties.priority} 消息: {body.decode('utf-8')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='priority_queue',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 消费所有消息
        start_time = time.time()
        while len(received_messages) < len(priorities) and time.time() - start_time < 5:
            self.connection.process_data_events(time_limit=0.1)
        
        # 停止消费者
        self.channel.stop_consuming()
        
        # 验证消息是否按优先级处理
        print("\n [+] 优先级队列处理结果:")
        for i, msg in enumerate(received_messages):
            print(f"  {i+1}. 优先级 {msg['priority']}: {msg['body']}")
    
    def run_demo(self):
        """运行队列属性演示"""
        print("\n=== 队列属性演示 ===")
        
        self.connect()
        
        try:
            self.demo_basic_properties()
            self.demo_advanced_properties()
            self.test_ttl_queue()
            self.test_length_limited_queue()
            self.test_priority_queue()
        finally:
            self.disconnect()
        
        print("\n [*] 队列属性演示完成")


class QueueTypesDemo:
    """队列类型演示"""
    
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
    
    def demo_classic_queue(self):
        """演示经典队列"""
        print("\n=== 经典队列演示 ===")
        
        # 显式声明经典队列
        self.channel.queue_declare(
            queue='classic_queue_demo',
            arguments={'x-queue-type': 'classic'}
        )
        print(" [*] 创建经典队列: classic_queue_demo")
        
        # 发送消息
        for i in range(5):
            self.channel.basic_publish(
                exchange='',
                routing_key='classic_queue_demo',
                body=f'经典队列消息 {i+1}'
            )
            print(f" [x] 发送消息: 经典队列消息 {i+1}")
        
        # 创建消费者
        def callback(ch, method, properties, body):
            print(f" [+] 收到消息: {body.decode('utf-8')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='classic_queue_demo',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 消费所有消息
        message_count = 0
        start_time = time.time()
        while message_count < 5 and time.time() - start_time < 3:
            method, properties, body = self.channel.basic_get(queue='classic_queue_demo')
            if method:
                callback(self.channel, method, properties, body)
                message_count += 1
            else:
                time.sleep(0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 共处理 {message_count} 条消息")
    
    def demo_quorum_queue(self):
        """演示仲裁队列"""
        print("\n=== 仲裁队列演示 ===")
        
        try:
            # 声明仲裁队列
            self.channel.queue_declare(
                queue='quorum_queue_demo',
                arguments={
                    'x-queue-type': 'quorum',
                    'x-quorum-initial-group-size': 1  # 单节点集群，设为1
                }
            )
            print(" [*] 创建仲裁队列: quorum_queue_demo")
            
            # 发送消息
            for i in range(5):
                self.channel.basic_publish(
                    exchange='',
                    routing_key='quorum_queue_demo',
                    body=f'仲裁队列消息 {i+1}',
                    properties=pika.BasicProperties(delivery_mode=2)  # 持久化
                )
                print(f" [x] 发送持久化消息: 仲裁队列消息 {i+1}")
            
            # 创建消费者
            def callback(ch, method, properties, body):
                print(f" [+] 收到持久化消息: {body.decode('utf-8')}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            self.channel.basic_consume(
                queue='quorum_queue_demo',
                on_message_callback=callback,
                auto_ack=False
            )
            
            # 消费所有消息
            message_count = 0
            start_time = time.time()
            while message_count < 5 and time.time() - start_time < 3:
                method, properties, body = self.channel.basic_get(queue='quorum_queue_demo')
                if method:
                    callback(self.channel, method, properties, body)
                    message_count += 1
                else:
                    time.sleep(0.1)
            
            self.channel.stop_consuming()
            print(f" [+] 共处理 {message_count} 条持久化消息")
            
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f" [!] 创建仲裁队列失败: {e}")
            print(" [!] 可能是因为RabbitMQ版本不支持仲裁队列或单节点集群配置")
    
    def demo_stream_queue(self):
        """演示流队列"""
        print("\n=== 流队列演示 ===")
        
        try:
            # 声明流队列
            self.channel.queue_declare(
                queue='stream_queue_demo',
                arguments={
                    'x-queue-type': 'stream',
                    'x-max-length-bytes': 10 * 1024 * 1024  # 10MB
                }
            )
            print(" [*] 创建流队列: stream_queue_demo")
            
            # 发送消息
            for i in range(10):
                message = f'流队列消息 {i+1}'
                self.channel.basic_publish(
                    exchange='',
                    routing_key='stream_queue_demo',
                    body=message
                )
                print(f" [x] 发送消息: {message}")
            
            # 流队列的读取需要特殊的API，这里只做演示
            print(" [+] 流队列创建成功，特殊API读取需要RabbitMQ Stream客户端")
            
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f" [!] 创建流队列失败: {e}")
            print(" [!] 可能是因为RabbitMQ版本不支持流队列或未启用流插件")
    
    def demo_lazy_queue(self):
        """演示惰性队列"""
        print("\n=== 惰性队列演示 ===")
        
        # 声明惰性队列
        self.channel.queue_declare(
            queue='lazy_queue_demo',
            arguments={
                'x-queue-mode': 'lazy'
            }
        )
        print(" [*] 创建惰性队列: lazy_queue_demo")
        
        # 发送较大的消息
        for i in range(3):
            # 创建一个较大的消息
            large_message = 'x' * 10000  # 10KB的消息
            message = f'惰性队列消息 {i+1}: {large_message[:50]}...'
            
            self.channel.basic_publish(
                exchange='',
                routing_key='lazy_queue_demo',
                body=message
            )
            print(f" [x] 发送大消息 {i+1} (约10KB)")
        
        # 创建消费者
        def callback(ch, method, properties, body):
            message = body.decode('utf-8')
            print(f" [+] 收到大消息: {message[:50]}... (长度: {len(message)})")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='lazy_queue_demo',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 消费所有消息
        message_count = 0
        start_time = time.time()
        while message_count < 3 and time.time() - start_time < 3:
            method, properties, body = self.channel.basic_get(queue='lazy_queue_demo')
            if method:
                callback(self.channel, method, properties, body)
                message_count += 1
            else:
                time.sleep(0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 共处理 {message_count} 条大消息")
    
    def run_demo(self):
        """运行队列类型演示"""
        print("\n=== 队列类型演示 ===")
        
        self.connect()
        
        try:
            self.demo_classic_queue()
            self.demo_quorum_queue()
            self.demo_stream_queue()
            self.demo_lazy_queue()
        finally:
            self.disconnect()
        
        print("\n [*] 队列类型演示完成")


class QueueLifecycleDemo:
    """队列生命周期演示"""
    
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
    
    def demo_queue_creation(self):
        """演示队列创建"""
        print("\n=== 队列创建演示 ===")
        
        # 1. 主动创建
        self.channel.queue_declare(queue='active_created_queue')
        print(" [*] 主动创建队列: active_created_queue")
        
        # 2. 被动检查
        try:
            self.channel.queue_declare(queue='active_created_queue', passive=True)
            print(" [+] 被动检查: active_created_queue 存在")
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f" [!] 被动检查失败: {e}")
    
    def demo_queue_status(self):
        """演示队列状态查询"""
        print("\n=== 队列状态查询演示 ===")
        
        # 先添加一些消息
        for i in range(3):
            self.channel.basic_publish(
                exchange='',
                routing_key='active_created_queue',
                body=f'状态查询测试消息 {i+1}'
            )
        
        # 查询队列状态
        method_frame = self.channel.queue_declare(queue='active_created_queue', passive=True)
        message_count = method_frame.method.message_count
        consumer_count = method_frame.method.consumer_count
        
        print(f" [+] 队列 'active_created_queue' 状态:")
        print(f"    消息数: {message_count}")
        print(f"    消费者数: {consumer_count}")
    
    def demo_queue_purge(self):
        """演示队列清空"""
        print("\n=== 队列清空演示 ===")
        
        # 查询清空前状态
        method_frame = self.channel.queue_declare(queue='active_created_queue', passive=True)
        message_count_before = method_frame.method.message_count
        print(f" [+] 清空前消息数: {message_count_before}")
        
        # 清空队列
        self.channel.queue_purge(queue='active_created_queue')
        print(" [*] 队列已清空")
        
        # 查询清空后状态
        method_frame = self.channel.queue_declare(queue='active_created_queue', passive=True)
        message_count_after = method_frame.method.message_count
        print(f" [+] 清空后消息数: {message_count_after}")
    
    def demo_queue_deletion(self):
        """演示队列删除"""
        print("\n=== 队列删除演示 ===")
        
        # 创建临时队列
        self.channel.queue_declare(queue='temporary_queue')
        print(" [*] 创建临时队列: temporary_queue")
        
        # 添加一些消息
        for i in range(2):
            self.channel.basic_publish(
                exchange='',
                routing_key='temporary_queue',
                body=f'临时队列消息 {i+1}'
            )
        
        # 查询状态
        method_frame = self.channel.queue_declare(queue='temporary_queue', passive=True)
        message_count = method_frame.method.message_count
        print(f" [+] 删除前消息数: {message_count}")
        
        # 删除队列
        self.channel.queue_delete(queue='temporary_queue')
        print(" [*] 队列已删除")
        
        # 尝试检查队列是否存在
        try:
            self.channel.queue_declare(queue='temporary_queue', passive=True)
            print(" [+] 队列仍然存在")
        except pika.exceptions.ChannelClosedByBroker as e:
            if e.reply_code == 404:
                print(" [+] 队列已成功删除")
    
    def demo_auto_delete_queue(self):
        """演示自动删除队列"""
        print("\n=== 自动删除队列演示 ===")
        
        # 创建自动删除队列
        self.channel.queue_declare(
            queue='auto_delete_demo',
            auto_delete=True
        )
        print(" [*] 创建自动删除队列: auto_delete_demo")
        
        # 创建消费者
        def callback(ch, method, properties, body):
            print(f" [+] 收到消息: {body.decode('utf-8')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        consumer_tag = self.channel.basic_consume(
            queue='auto_delete_demo',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 发送消息
        for i in range(2):
            self.channel.basic_publish(
                exchange='',
                routing_key='auto_delete_demo',
                body=f'自动删除队列消息 {i+1}'
            )
        
        # 消费消息
        start_time = time.time()
        consumed = 0
        while consumed < 2 and time.time() - start_time < 3:
            method, properties, body = self.channel.basic_get(queue='auto_delete_demo')
            if method:
                callback(self.channel, method, properties, body)
                consumed += 1
            else:
                time.sleep(0.1)
        
        # 取消消费者
        self.channel.basic_cancel(consumer_tag)
        print(" [*] 取消消费者")
        
        # 队列应该被自动删除
        try:
            self.channel.queue_declare(queue='auto_delete_demo', passive=True)
            print(" [!] 队列仍然存在")
        except pika.exceptions.ChannelClosedByBroker as e:
            if e.reply_code == 404:
                print(" [+] 队列已自动删除")
    
    def run_demo(self):
        """运行队列生命周期演示"""
        print("\n=== 队列生命周期演示 ===")
        
        self.connect()
        
        try:
            self.demo_queue_creation()
            self.demo_queue_status()
            self.demo_queue_purge()
            self.demo_queue_deletion()
            self.demo_auto_delete_queue()
        finally:
            self.disconnect()
        
        print("\n [*] 队列生命周期演示完成")


class ConsumerManagementDemo:
    """消费者管理演示"""
    
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
    
    def setup_queues(self):
        """设置测试队列"""
        # 创建队列用于演示
        self.channel.queue_declare(queue='auto_ack_queue')
        self.channel.queue_declare(queue='manual_ack_queue')
        self.channel.queue_declare(queue='prefetch_queue')
        self.channel.queue_declare(queue='cancellation_queue')
        
        # 添加消息
        for i in range(10):
            message = f'消费者管理测试消息 {i+1}'
            self.channel.basic_publish(exchange='', routing_key='auto_ack_queue', body=message)
            self.channel.basic_publish(exchange='', routing_key='manual_ack_queue', body=message)
            self.channel.basic_publish(exchange='', routing_key='prefetch_queue', body=message)
            self.channel.basic_publish(exchange='', routing_key='cancellation_queue', body=message)
        
        print(" [*] 设置测试队列和消息完成")
    
    def demo_auto_ack(self):
        """演示自动确认"""
        print("\n=== 自动确认演示 ===")
        
        received = []
        
        def callback(ch, method, properties, body):
            received.append(body.decode('utf-8'))
            print(f" [+] 自动确认收到: {body.decode('utf-8')}")
            # 无需手动确认
        
        self.channel.basic_consume(
            queue='auto_ack_queue',
            on_message_callback=callback,
            auto_ack=True  # 自动确认
        )
        
        # 消费所有消息
        start_time = time.time()
        while len(received) < 3 and time.time() - start_time < 3:
            self.connection.process_data_events(time_limit=0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 共收到 {len(received)} 条消息")
    
    def demo_manual_ack(self):
        """演示手动确认"""
        print("\n=== 手动确认演示 ===")
        
        received = []
        
        def callback(ch, method, properties, body):
            received.append(body.decode('utf-8'))
            print(f" [+] 手动确认收到: {body.decode('utf-8')}")
            # 手动确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='manual_ack_queue',
            on_message_callback=callback,
            auto_ack=False  # 手动确认
        )
        
        # 消费所有消息
        start_time = time.time()
        while len(received) < 3 and time.time() - start_time < 3:
            self.connection.process_data_events(time_limit=0.1)
        
        self.channel.stop_consuming()
        print(f" [+] 共收到 {len(received)} 条消息")
    
    def demo_prefetch(self):
        """演示消费者预取"""
        print("\n=== 消费者预取演示 ===")
        
        # 创建两个消费者，使用不同的预取设置
        consumer1_received = []
        consumer2_received = []
        
        # 消费者1，预取数量为1
        self.channel.basic_qos(prefetch_count=1)
        
        def callback1(ch, method, properties, body):
            consumer1_received.append(body.decode('utf-8'))
            print(f" [+] 消费者1收到 (预取1): {body.decode('utf-8')}")
            time.sleep(0.2)  # 模拟处理时间
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        consumer1_tag = self.channel.basic_consume(
            queue='prefetch_queue',
            on_message_callback=callback1,
            auto_ack=False
        )
        
        # 消费者2，预取数量为5
        self.channel2 = self.connection.channel()
        self.channel2.basic_qos(prefetch_count=5)
        
        def callback2(ch, method, properties, body):
            consumer2_received.append(body.decode('utf-8'))
            print(f" [+] 消费者2收到 (预取5): {body.decode('utf-8')}")
            time.sleep(0.1)  # 模拟处理时间
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        consumer2_tag = self.channel2.basic_consume(
            queue='prefetch_queue',
            on_message_callback=callback2,
            auto_ack=False
        )
        
        # 等待消息处理
        start_time = time.time()
        while len(consumer1_received) + len(consumer2_received) < 6 and time.time() - start_time < 5:
            self.connection.process_data_events(time_limit=0.1)
        
        # 停止消费者
        self.channel.basic_cancel(consumer1_tag)
        self.channel2.basic_cancel(consumer2_tag)
        
        print(f" [+] 消费者1共收到 {len(consumer1_received)} 条消息")
        print(f" [+] 消费者2共收到 {len(consumer2_received)} 条消息")
    
    def demo_consumer_cancellation(self):
        """演示消费者取消"""
        print("\n=== 消费者取消演示 ===")
        
        received = []
        
        def callback(ch, method, properties, body):
            received.append(body.decode('utf-8'))
            print(f" [+] 消费者收到: {body.decode('utf-8')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_qos(prefetch_count=1)
        
        # 启动消费者
        consumer_tag = self.channel.basic_consume(
            queue='cancellation_queue',
            on_message_callback=callback,
            auto_ack=False,
            consumer_tag='cancellable_consumer'  # 自定义标签
        )
        
        print(f" [*] 启动消费者，标签: {consumer_tag}")
        
        # 消费一条消息
        start_time = time.time()
        while len(received) < 1 and time.time() - start_time < 3:
            self.connection.process_data_events(time_limit=0.1)
        
        # 取消消费者
        self.channel.basic_cancel(consumer_tag)
        print(f" [*] 取消消费者: {consumer_tag}")
        
        # 再次尝试消费
        start_time = time.time()
        while len(received) < 2 and time.time() - start_time < 3:
            self.connection.process_data_events(time_limit=0.1)
        
        print(f" [+] 取消后消费者共收到 {len(received)} 条消息 (应该只有1条)")
    
    def run_demo(self):
        """运行消费者管理演示"""
        print("\n=== 消费者管理演示 ===")
        
        self.connect()
        
        try:
            self.setup_queues()
            self.demo_auto_ack()
            self.demo_manual_ack()
            self.demo_prefetch()
            self.demo_consumer_cancellation()
        finally:
            self.disconnect()
        
        print("\n [*] 消费者管理演示完成")


class QueueMonitoringDemo:
    """队列监控演示"""
    
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
    
    def setup_monitoring_queues(self):
        """设置监控用的队列"""
        # 创建不同状态的队列
        self.channel.queue_declare(queue='empty_queue')
        self.channel.queue_declare(queue='moderate_queue')
        self.channel.queue_declare(queue='full_queue')
        
        # 添加消息到不同队列
        for i in range(20):  # 添加20条消息到full_queue
            self.channel.basic_publish(
                exchange='',
                routing_key='full_queue',
                body=f'满队列消息 {i+1}'
            )
        
        for i in range(5):  # 添加5条消息到moderate_queue
            self.channel.basic_publish(
                exchange='',
                routing_key='moderate_queue',
                body=f'中等队列消息 {i+1}'
            )
        
        print(" [*] 设置监控队列完成")
    
    def demo_queue_status_monitoring(self):
        """演示队列状态监控"""
        print("\n=== 队列状态监控演示 ===")
        
        queues = ['empty_queue', 'moderate_queue', 'full_queue']
        
        for queue in queues:
            try:
                method_frame = self.channel.queue_declare(queue=queue, passive=True)
                message_count = method_frame.method.message_count
                consumer_count = method_frame.method.consumer_count
                
                print(f"队列 '{queue}':")
                print(f"  消息数: {message_count}")
                print(f"  消费者数: {consumer_count}")
                
                # 提供状态评估
                if message_count == 0:
                    status = "空闲"
                elif message_count < 10:
                    status = "正常"
                elif message_count < 50:
                    status = "繁忙"
                else:
                    status = "拥堵"
                
                print(f"  状态: {status}")
                
            except pika.exceptions.ChannelClosedByBroker as e:
                if e.reply_code == 404:
                    print(f"队列 '{queue}': 不存在")
    
    def demo_queue_health_check(self):
        """演示队列健康检查"""
        print("\n=== 队列健康检查演示 ===")
        
        queues = ['empty_queue', 'moderate_queue', 'full_queue']
        
        for queue in queues:
            try:
                method_frame = self.channel.queue_declare(queue=queue, passive=True)
                message_count = method_frame.method.message_count
                consumer_count = method_frame.method.consumer_count
                
                # 健康评分
                health_score = 100
                
                # 消息积压扣分
                if message_count > 100:
                    health_score -= 30
                elif message_count > 50:
                    health_score -= 20
                elif message_count > 20:
                    health_score -= 10
                elif message_count > 10:
                    health_score -= 5
                
                # 缺少消费者扣分
                if consumer_count == 0:
                    health_score -= 20
                elif consumer_count < 2:
                    health_score -= 10
                
                # 健康状态
                if health_score >= 80:
                    status = "健康"
                elif health_score >= 60:
                    status = "警告"
                else:
                    status = "危险"
                
                print(f"队列 '{queue}': {status} ({health_score}/100)")
                
                # 提供建议
                if message_count > 20:
                    print(f"  建议: 消息积压严重，考虑增加消费者")
                
                if consumer_count == 0:
                    print(f"  建议: 没有消费者，检查消费者状态")
                
            except pika.exceptions.ChannelClosedByBroker as e:
                if e.reply_code == 404:
                    print(f"队列 '{queue}': 不存在 (0/100)")
    
    def demo_continuous_monitoring(self):
        """演示连续监控"""
        print("\n=== 连续监控演示 ===")
        
        queue = 'moderate_queue'
        rounds = 3
        interval = 1  # 1秒间隔
        
        print(f"监控队列 '{queue}'，共 {rounds} 轮，间隔 {interval} 秒")
        
        for i in range(rounds):
            try:
                method_frame = self.channel.queue_declare(queue=queue, passive=True)
                message_count = method_frame.method.message_count
                consumer_count = method_frame.method.consumer_count
                
                timestamp = time.strftime('%H:%M:%S', time.localtime())
                print(f"[{timestamp}] 轮次 {i+1}: 消息数={message_count}, 消费者数={consumer_count}")
                
                # 模拟消息消费
                if message_count > 0 and i < rounds - 1:
                    method, properties, body = self.channel.basic_get(queue=queue)
                    if method:
                        self.channel.basic_ack(delivery_tag=method.delivery_tag)
                        print(f"    消费一条消息: {body.decode('utf-8')}")
                
            except pika.exceptions.ChannelClosedByBroker as e:
                if e.reply_code == 404:
                    print(f"队列 '{queue}': 不存在")
            
            if i < rounds - 1:  # 不是最后一轮
                time.sleep(interval)
    
    def demo_queue_diagnostics(self):
        """演示队列诊断"""
        print("\n=== 队列诊断演示 ===")
        
        queue = 'full_queue'
        
        try:
            # 获取队列信息
            method_frame = self.channel.queue_declare(queue=queue, passive=True)
            message_count = method_frame.method.message_count
            consumer_count = method_frame.method.consumer_count
            
            print(f"诊断队列: {queue}")
            print(f"  消息数: {message_count}")
            print(f"  消费者数: {consumer_count}")
            
            # 诊断建议
            if message_count > 10:
                print("  警告: 消息积压严重")
                print("    建议: 增加消费者或优化处理逻辑")
            
            if consumer_count == 0:
                print("  警告: 没有活跃的消费者")
                print("    建议: 检查消费者是否正常运行")
            
            # 测试消息流
            print("  测试消息流...")
            test_message = f"诊断测试消息 - {time.time()}"
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=test_message
            )
            
            # 获取消息
            method, properties, body = self.channel.basic_get(queue=queue)
            
            if method and body.decode('utf-8') == test_message:
                print("    消息流测试: 成功")
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print("    消息流测试: 失败，消息不匹配")
                
        except pika.exceptions.ChannelClosedByBroker as e:
            if e.reply_code == 404:
                print(f"  错误: 队列 '{queue}' 不存在")
    
    def run_demo(self):
        """运行队列监控演示"""
        print("\n=== 队列监控演示 ===")
        
        self.connect()
        
        try:
            self.setup_monitoring_queues()
            self.demo_queue_status_monitoring()
            self.demo_queue_health_check()
            self.demo_continuous_monitoring()
            self.demo_queue_diagnostics()
        finally:
            self.disconnect()
        
        print("\n [*] 队列监控演示完成")


class TaskQueueSystemDemo:
    """任务队列系统演示"""
    
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
    
    def setup_task_queues(self):
        """设置任务队列系统"""
        # 高优先级任务队列
        self.channel.queue_declare(
            queue='high_priority_tasks',
            durable=True,
            arguments={
                'x-max-priority': 10,
                'x-queue-mode': 'lazy'  # 任务可能较大，使用惰性队列
            }
        )
        
        # 普通任务队列
        self.channel.queue_declare(
            queue='normal_tasks',
            durable=True
        )
        
        # 失败任务队列（死信队列）
        self.channel.exchange_declare(exchange='failed_tasks_exchange', exchange_type='direct')
        self.channel.queue_declare(queue='failed_tasks', durable=True)
        self.channel.queue_bind(
            exchange='failed_tasks_exchange',
            queue='failed_tasks'
        )
        
        # 为主队列设置死信交换机
        for queue in ['high_priority_tasks', 'normal_tasks']:
            self.channel.queue_declare(
                queue=queue,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': 'failed_tasks_exchange',
                    'x-message-ttl': 86400000  # 24小时TTL
                }
            )
        
        print(" [*] 任务队列系统设置完成")
    
    def submit_task(self, task_data, priority='normal'):
        """提交任务"""
        task_json = json.dumps(task_data)
        
        if priority == 'high':
            queue = 'high_priority_tasks'
            priority_value = 10
        else:
            queue = 'normal_tasks'
            priority_value = 5
        
        properties = pika.BasicProperties(
            delivery_mode=2,  # 持久化
            priority=priority_value
        )
        
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=task_json,
            properties=properties
        )
        
        print(f"任务已提交: {task_data.get('task_id', 'unknown')} (优先级: {priority})")
    
    def create_task_worker(self, queue, worker_id=None):
        """创建任务工作者"""
        if worker_id is None:
            worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        
        def task_callback(ch, method, properties, body):
            try:
                task = json.loads(body.decode('utf-8'))
                
                print(f"[{worker_id}] 开始处理任务: {task.get('task_id', 'unknown')}")
                
                # 模拟任务处理
                self._process_task(task)
                
                print(f"[{worker_id}] 完成任务: {task.get('task_id', 'unknown')}")
                
                # 确认任务完成
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"[{worker_id}] 任务处理失败: {e}")
                # 拒绝任务，不重新入队（将发送到死信队列）
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        # 设置预取数量
        self.channel.basic_qos(prefetch_count=1)
        
        # 创建消费者
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=task_callback,
            auto_ack=False
        )
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        print(f"任务工作者已启动: {worker_id} (队列: {queue})")
        
        return consumer
    
    def _process_task(self, task):
        """处理任务的实际逻辑"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'email':
            # 模拟发送邮件
            time.sleep(1)
            print(f"  发送邮件给: {task.get('recipient', 'unknown')}")
        elif task_type == 'report':
            # 模拟生成报告
            time.sleep(2)
            print(f"  生成报告: {task.get('report_name', 'unknown')}")
        else:
            # 通用任务处理
            time.sleep(0.5)
            print(f"  处理通用任务: {task.get('description', 'unknown')}")
    
    def run_demo(self):
        """运行任务队列系统演示"""
        print("\n=== 任务队列系统演示 ===")
        
        self.connect()
        
        try:
            self.setup_task_queues()
            
            # 提交各种任务
            print("\n提交任务:")
            self.submit_task({
                'task_id': 'task_001',
                'type': 'email',
                'recipient': 'user@example.com',
                'subject': 'Welcome',
                'priority': 'high'
            }, priority='high')
            
            self.submit_task({
                'task_id': 'task_002',
                'type': 'report',
                'report_name': 'Monthly Sales',
                'priority': 'normal'
            })
            
            self.submit_task({
                'task_id': 'task_003',
                'type': 'email',
                'recipient': 'admin@example.com',
                'subject': 'System Alert',
                'priority': 'high'
            }, priority='high')
            
            self.submit_task({
                'task_id': 'task_004',
                'type': 'cleanup',
                'description': 'Clean up temporary files',
                'priority': 'normal'
            })
            
            # 创建工作者
            print("\n启动任务工作者:")
            self.create_task_worker('high_priority_tasks', 'high_priority_worker')
            self.create_task_worker('normal_tasks', 'normal_worker_1')
            self.create_task_worker('normal_tasks', 'normal_worker_2')
            
            # 等待任务处理
            print("\n等待任务处理...")
            time.sleep(10)
            
        finally:
            self.disconnect()
        
        print("\n [*] 任务队列系统演示完成")


class LogCollectionSystemDemo:
    """日志收集系统演示"""
    
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
    
    def setup_log_system(self):
        """设置日志收集系统"""
        # 创建日志交换机
        self.channel.exchange_declare(exchange='log_direct', exchange_type='direct')
        self.channel.exchange_declare(exchange='log_topic', exchange_type='topic')
        
        # 创建日志队列
        log_levels = ['debug', 'info', 'warning', 'error']
        for level in log_levels:
            # 按级别分类的队列
            self.channel.queue_declare(
                queue=f'logs.{level}',
                durable=True,
                arguments={
                    'x-message-ttl': 7 * 24 * 3600 * 1000  # 7天过期
                }
            )
            
            # 绑定到直接交换机
            self.channel.queue_bind(
                exchange='log_direct',
                queue=f'logs.{level}',
                routing_key=level
            )
            
            # 绑定到主题交换机
            self.channel.queue_bind(
                exchange='log_topic',
                queue=f'logs.{level}',
                routing_key=f'*.{level}'
            )
        
        # 创建按应用分类的队列
        applications = ['web', 'api', 'database']
        for app in applications:
            self.channel.queue_declare(
                queue=f'logs.app.{app}',
                durable=True,
                arguments={
                    'x-message-ttl': 7 * 24 * 3600 * 1000  # 7天过期
                }
            )
            
            # 绑定到主题交换机
            self.channel.queue_bind(
                exchange='log_topic',
                queue=f'logs.app.{app}',
                routing_key=f'{app}.*'
            )
        
        print(" [*] 日志收集系统设置完成")
    
    def send_log(self, application, level, message):
        """发送日志消息"""
        log_data = {
            'application': application,
            'level': level,
            'message': message,
            'timestamp': int(time.time())
        }
        
        # 发送到直接交换机
        self.channel.basic_publish(
            exchange='log_direct',
            routing_key=level,
            body=json.dumps(log_data),
            properties=pika.BasicProperties(
                delivery_mode=1,  # 日志通常不需要持久化
                timestamp=log_data['timestamp']
            )
        )
        
        # 发送到主题交换机
        self.channel.basic_publish(
            exchange='log_topic',
            routing_key=f'{application}.{level}',
            body=json.dumps(log_data),
            properties=pika.BasicProperties(
                delivery_mode=1,
                timestamp=log_data['timestamp']
            )
        )
        
        print(f"发送日志: [{application}] [{level}] {message}")
    
    def create_log_consumer(self, queue_name):
        """创建日志消费者"""
        def log_callback(ch, method, properties, body):
            log_data = json.loads(body.decode('utf-8'))
            level = log_data.get('level', 'unknown')
            app = log_data.get('application', 'unknown')
            message = log_data.get('message', '')
            timestamp = log_data.get('timestamp', 0)
            
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            print(f"[{formatted_time}] [{app}] [{level.upper()}] {message}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=log_callback,
            auto_ack=False
        )
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        print(f"日志消费者已启动: {queue_name}")
        
        return consumer
    
    def run_demo(self):
        """运行日志收集系统演示"""
        print("\n=== 日志收集系统演示 ===")
        
        self.connect()
        
        try:
            self.setup_log_system()
            
            # 创建日志消费者
            print("\n启动日志消费者:")
            self.create_log_consumer('logs.error')     # 错误日志消费者
            self.create_log_consumer('logs.app.web')    # Web应用日志消费者
            
            # 等待消费者启动
            time.sleep(1)
            
            # 发送日志
            print("\n发送日志消息:")
            self.send_log('web', 'info', 'User logged in: admin')
            self.send_log('api', 'warning', 'Rate limit approaching for user 123')
            self.send_log('database', 'error', 'Connection timeout to replica')
            self.send_log('web', 'error', '500 Internal Server Error on /checkout')
            self.send_log('api', 'info', 'API request processed successfully')
            self.send_log('database', 'info', 'Backup completed successfully')
            
            # 等待日志处理
            print("\n等待日志处理...")
            time.sleep(5)
            
        finally:
            self.disconnect()
        
        print("\n [*] 日志收集系统演示完成")


def main():
    """主函数，根据参数运行不同的演示"""
    parser = argparse.ArgumentParser(description='RabbitMQ Queue Management Demo')
    parser.add_argument(
        '--type',
        choices=['properties', 'types', 'lifecycle', 'consumers', 'monitoring', 'tasks', 'logs', 'all'],
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
        'properties': QueuePropertiesDemo(args.host),
        'types': QueueTypesDemo(args.host),
        'lifecycle': QueueLifecycleDemo(args.host),
        'consumers': ConsumerManagementDemo(args.host),
        'monitoring': QueueMonitoringDemo(args.host),
        'tasks': TaskQueueSystemDemo(args.host),
        'logs': LogCollectionSystemDemo(args.host)
    }
    
    if args.type == 'all':
        # 运行所有演示
        for demo_type, demo in demos.items():
            try:
                demo.run_demo()
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