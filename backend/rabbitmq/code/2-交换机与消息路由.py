#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第2章：交换机与消息路由
完整可运行的代码示例

本文件包含了第2章中所有交换机类型的完整示例：
1. Direct Exchange（直连交换机）
2. Fanout Exchange（扇形交换机）
3. Topic Exchange（主题交换机）
4. Headers Exchange（头交换机）
5. 交换机高级特性示例
6. 实际应用案例

运行方式：
python 2-交换机与消息路由.py [demo_type]

demo_type可选：
- direct  : 运行Direct Exchange演示
- fanout  : 运行Fanout Exchange演示
- topic   : 运行Topic Exchange演示
- headers : 运行Headers Exchange演示
- all     : 依次运行所有演示（默认）
"""

import pika
import threading
import time
import sys
import json
import uuid
import random
import argparse


class RabbitMQDemoBase:
    """RabbitMQ演示基类"""
    
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
    
    def cleanup_consumers(self):
        """清理消费者线程"""
        for consumer in self.consumers:
            if consumer.is_alive():
                consumer.join(timeout=1)


class DirectExchangeDemo(RabbitMQDemoBase):
    """Direct Exchange演示"""
    
    def __init__(self, host='localhost'):
        super().__init__(host)
        self.exchange_name = 'direct_logs_demo'
    
    def setup(self):
        """设置交换机和队列"""
        self.connect()
        
        # 声明交换机
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='direct',
            durable=True
        )
        
        # 定义队列和路由键
        self.queues = ['queue_info', 'queue_warning', 'queue_error']
        self.severities = ['info', 'warning', 'error']
        self.queue_names = {}
        
        # 为每个严重级别创建队列
        for queue in self.queues:
            # 声明队列
            result = self.channel.queue_declare(
                queue=queue,
                durable=True
            )
            self.queue_names[queue] = result.method.queue
            
            # 绑定队列到交换机
            for i, severity in enumerate(self.severities):
                if i == self.queues.index(queue) or (i == 2 and queue == 'queue_error'):
                    self.channel.queue_bind(
                        exchange=self.exchange_name,
                        queue=queue,
                        routing_key=severity
                    )
        
        print(" [*] Direct Exchange setup completed")
    
    def publish_messages(self, message_count=20):
        """发布消息到Direct Exchange"""
        print(f" [*] Publishing {message_count} messages...")
        
        for i in range(message_count):
            # 随机选择严重级别
            severity = random.choice(self.severities)
            message = f"Message {i+1} with severity: {severity}"
            
            # 发送消息
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=severity,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                )
            )
            
            print(f" [x] Sent severity:{severity} message:'{message}'")
            time.sleep(0.5)
    
    def create_consumer(self, queue_name, auto_ack=True):
        """为指定队列创建消费者"""
        
        def callback(ch, method, properties, body):
            print(f" [Consumer {queue_name}] Received {method.routing_key}:{body.decode('utf-8')}")
            if not auto_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=auto_ack
        )
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        return consumer
    
    def run_demo(self):
        """运行Direct Exchange演示"""
        print("\n=== Direct Exchange Demo ===")
        
        self.setup()
        
        # 为每个队列创建消费者
        for queue in self.queues:
            self.create_consumer(queue)
            print(f" [*] Started consumer for {queue}")
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发布消息
        self.publish_messages()
        
        # 等待一段时间让消费者处理消息
        time.sleep(5)
        
        # 清理
        self.cleanup_consumers()
        self.disconnect()
        print(" [*] Direct Exchange demo completed\n")


class FanoutExchangeDemo(RabbitMQDemoBase):
    """Fanout Exchange演示"""
    
    def __init__(self, host='localhost'):
        super().__init__(host)
        self.exchange_name = 'fanout_logs_demo'
        self.consumer_count = 0
    
    def setup(self):
        """设置交换机"""
        self.connect()
        
        # 声明交换机
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='fanout',
            durable=True
        )
        
        print(" [*] Fanout Exchange setup completed")
    
    def create_consumer(self, name=None):
        """创建新的消费者"""
        if name is None:
            name = f"consumer_{self.consumer_count}"
        
        # 创建临时队列
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # 将队列绑定到交换机
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name
        )
        
        def callback(ch, method, properties, body):
            print(f" [Consumer {name}] Received: {body.decode('utf-8')}")
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        
        self.consumer_count += 1
        print(f" [*] Created consumer {name} (total: {self.consumer_count})")
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        return consumer
    
    def publish_messages(self, message_count=10):
        """发布消息到Fanout Exchange"""
        print(f" [*] Publishing {message_count} messages...")
        
        messages = [
            "System started",
            "User logged in: admin",
            "Database backup completed",
            "Scheduled maintenance initiated",
            "Nightly maintenance started"
        ]
        
        for i in range(message_count):
            # 随机选择消息
            message = messages[i % len(messages)]
            
            # 发送消息
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='',  # Fanout Exchange忽略路由键
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    timestamp=time.time()
                )
            )
            
            print(f" [x] Published: '{message}'")
            time.sleep(1)
    
    def add_consumer_dynamically(self):
        """动态添加消费者"""
        def add_consumer():
            for i in range(3):
                time.sleep(2)
                self.create_consumer(name=f"dynamic_{i}")
        
        adder = threading.Thread(target=add_consumer)
        adder.daemon = True
        adder.start()
        
        return adder
    
    def run_demo(self):
        """运行Fanout Exchange演示"""
        print("\n=== Fanout Exchange Demo ===")
        
        self.setup()
        
        # 初始创建两个消费者
        for i in range(2):
            self.create_consumer(name=f"initial_{i}")
        
        # 启动动态添加消费者的线程
        self.add_consumer_dynamically()
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发布消息
        self.publish_messages()
        
        # 等待生产者完成
        time.sleep(2)
        
        # 等待一段时间让消费者处理消息
        time.sleep(5)
        
        # 清理
        self.cleanup_consumers()
        self.disconnect()
        print(" [*] Fanout Exchange demo completed\n")


class TopicExchangeDemo(RabbitMQDemoBase):
    """Topic Exchange演示"""
    
    def __init__(self, host='localhost'):
        super().__init__(host)
        self.exchange_name = 'topic_logs_demo'
        self.consumer_count = 0
    
    def setup(self):
        """设置交换机"""
        self.connect()
        
        # 声明交换机
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='topic',
            durable=True
        )
        
        print(" [*] Topic Exchange setup completed")
    
    def create_consumer(self, name=None, binding_keys=None):
        """创建新的消费者"""
        if name is None:
            name = f"consumer_{self.consumer_count}"
        
        if binding_keys is None:
            binding_keys = ["#"]  # 默认接收所有消息
        
        # 创建临时队列
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # 将队列绑定到交换机
        for binding_key in binding_keys:
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=binding_key
            )
        
        def callback(ch, method, properties, body):
            print(f" [Consumer {name}] Received {method.routing_key}:{body.decode('utf-8')}")
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        
        self.consumer_count += 1
        print(f" [*] Created consumer {name} with bindings: {binding_keys}")
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        return consumer
    
    def publish_messages(self, message_count=15):
        """发布消息到Topic Exchange"""
        print(f" [*] Publishing {message_count} messages...")
        
        message_types = [
            ("info", "system", "Information message"),
            ("warning", "database", "Database warning"),
            ("error", "application", "Error log entry"),
            ("debug", "api", "Debug information"),
            ("critical", "security", "Security alert")
        ]
        
        for i in range(message_count):
            # 随机选择消息类型
            level, source, content = random.choice(message_types)
            routing_key = f"{level}.{source}.server{i%3+1}"  # 添加服务器编号
            
            message = f"{content} on server{i%3+1}"
            
            # 发送消息
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    timestamp=time.time()
                )
            )
            
            print(f" [x] Published routing_key:{routing_key} message:'{message}'")
            time.sleep(0.5)
    
    def create_specialized_consumers(self):
        """创建专门的消费者"""
        # 系统管理员 - 接收所有critical和error消息
        self.create_consumer(
            name="system_admin",
            binding_keys=["critical.#", "error.#"]
        )
        
        # 数据库管理员 - 只接收数据库相关消息
        self.create_consumer(
            name="db_admin",
            binding_keys=["*.database.*"]
        )
        
        # API开发者 - 只接收API相关消息
        self.create_consumer(
            name="api_dev",
            binding_keys=["debug.api.*"]
        )
        
        # 安全分析师 - 只接收安全相关消息
        self.create_consumer(
            name="security_analyst",
            binding_keys=["*.security.*"]
        )
    
    def run_demo(self):
        """运行Topic Exchange演示"""
        print("\n=== Topic Exchange Demo ===")
        
        self.setup()
        
        # 创建专门的消费者
        self.create_specialized_consumers()
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发布消息
        self.publish_messages()
        
        # 等待生产者完成
        time.sleep(2)
        
        # 等待一段时间让消费者处理消息
        time.sleep(5)
        
        # 清理
        self.cleanup_consumers()
        self.disconnect()
        print(" [*] Topic Exchange demo completed\n")


class HeadersExchangeDemo(RabbitMQDemoBase):
    """Headers Exchange演示"""
    
    def __init__(self, host='localhost'):
        super().__init__(host)
        self.exchange_name = 'headers_demo'
        self.consumer_count = 0
    
    def setup(self):
        """设置交换机"""
        self.connect()
        
        # 声明交换机
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type='headers',
            durable=True
        )
        
        print(" [*] Headers Exchange setup completed")
    
    def create_consumer(self, name=None, binding_headers=None):
        """创建新的消费者"""
        if name is None:
            name = f"consumer_{self.consumer_count}"
        
        if binding_headers is None:
            binding_headers = {'x-match': 'any'}  # 默认接收所有消息
        
        # 创建临时队列
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # 将队列绑定到交换机
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            arguments=binding_headers
        )
        
        def callback(ch, method, properties, body):
            data = json.loads(body.decode('utf-8'))
            print(f" [Consumer {name}] Received data: {data}")
            print(f" [Consumer {name}] Message headers: {properties.headers}")
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        
        self.consumer_count += 1
        print(f" [*] Created consumer {name} with binding headers: {binding_headers}")
        
        # 在单独线程中运行消费者
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        return consumer
    
    def publish_messages(self, message_count=15):
        """发布消息到Headers Exchange"""
        print(f" [*] Publishing {message_count} messages...")
        
        sources = ['web', 'mobile', 'api']
        versions = ['1.0', '2.0', '2.1']
        regions = ['north', 'south', 'east', 'west']
        event_types = ['order_created', 'user_registered', 'payment_processed', 'product_viewed']
        
        for i in range(message_count):
            # 随机生成消息数据
            data = {
                'user_id': random.randint(1000, 9999),
                'product_id': f'PROD-{random.randint(100, 999)}',
                'price': round(random.uniform(10.0, 500.0), 2),
                'category': random.choice(['electronics', 'clothing', 'books', 'home']),
                'region': random.choice(regions),
                'priority': random.choice(['low', 'medium', 'high'])
            }
            
            # 随机生成消息头
            headers = {
                'source': random.choice(sources),
                'version': random.choice(versions),
                'region': data['region'],
                'event_type': random.choice(event_types),
                'timestamp': int(time.time())
            }
            
            # 发送消息
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='',  # Headers Exchange忽略路由键
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    headers=headers,
                    content_type='application/json'
                )
            )
            
            print(f" [x] Published message with headers: {headers}")
            time.sleep(0.5)
    
    def create_specialized_consumers(self):
        """创建专门的消费者"""
        # Web应用消费者 - 接收所有来自web的消息
        self.create_consumer(
            name="web_consumer",
            binding_headers={'x-match': 'all', 'source': 'web'}
        )
        
        # 高优先级消费者 - 接收所有高优先级消息
        self.create_consumer(
            name="high_priority_consumer",
            binding_headers={'x-match': 'all', 'priority': 'high'}
        )
        
        # 北方区域消费者 - 接收所有北方区域的消息
        self.create_consumer(
            name="north_region_consumer",
            binding_headers={'x-match': 'all', 'region': 'north'}
        )
        
        # 多条件消费者 - 接收来自mobile且版本为2.0的消息
        self.create_consumer(
            name="mobile_v2_consumer",
            binding_headers={'x-match': 'all', 'source': 'mobile', 'version': '2.0'}
        )
        
        # 多条件或消费者 - 接收订单创建或用户注册的消息
        self.create_consumer(
            name="order_user_consumer",
            binding_headers={'x-match': 'any', 'event_type': 'order_created', 'event_type': 'user_registered'}
        )
    
    def run_demo(self):
        """运行Headers Exchange演示"""
        print("\n=== Headers Exchange Demo ===")
        
        self.setup()
        
        # 创建专门的消费者
        self.create_specialized_consumers()
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发布消息
        self.publish_messages()
        
        # 等待生产者完成
        time.sleep(2)
        
        # 等待一段时间让消费者处理消息
        time.sleep(5)
        
        # 清理
        self.cleanup_consumers()
        self.disconnect()
        print(" [*] Headers Exchange demo completed\n")


class AdvancedExchangeFeaturesDemo(RabbitMQDemoBase):
    """交换机高级特性演示"""
    
    def __init__(self, host='localhost'):
        super().__init__(host)
    
    def setup_alternate_exchange(self):
        """设置备用交换机"""
        self.connect()
        
        # 声明备用交换机
        self.channel.exchange_declare(
            exchange='unrouted_exchange',
            exchange_type='fanout',
            durable=True
        )
        
        # 创建队列绑定到备用交换机
        self.channel.queue_declare(queue='unrouted_messages', durable=True)
        self.channel.queue_bind(
            exchange='unrouted_exchange',
            queue='unrouted_messages'
        )
        
        # 声明主交换机，并指定备用交换机
        self.channel.exchange_declare(
            exchange='main_exchange',
            exchange_type='direct',
            durable=True,
            arguments={
                'alternate-exchange': 'unrouted_exchange'  # 指定备用交换机
            }
        )
        
        print(" [*] Alternate exchange setup completed")
    
    def demo_alternate_exchange(self):
        """演示备用交换机"""
        print("\n=== Alternate Exchange Demo ===")
        
        self.setup_alternate_exchange()
        
        # 创建消费者接收备用交换机的消息
        def callback(ch, method, properties, body):
            print(f" [Unrouted Message Consumer] Received: {body.decode('utf-8')}")
        
        self.channel.basic_consume(
            queue='unrouted_messages',
            on_message_callback=callback,
            auto_ack=True
        )
        
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发送一个会正常路由的消息
        self.channel.queue_declare(queue='normal_queue', durable=True)
        self.channel.queue_bind(
            exchange='main_exchange',
            queue='normal_queue',
            routing_key='normal_key'
        )
        
        def normal_callback(ch, method, properties, body):
            print(f" [Normal Message Consumer] Received: {body.decode('utf-8')}")
        
        self.channel.basic_consume(
            queue='normal_queue',
            on_message_callback=normal_callback,
            auto_ack=True
        )
        
        normal_consumer = threading.Thread(target=self.channel.start_consuming)
        normal_consumer.daemon = True
        normal_consumer.start()
        self.consumers.append(normal_consumer)
        
        # 发送正常路由的消息
        self.channel.basic_publish(
            exchange='main_exchange',
            routing_key='normal_key',
            body='This message will be routed normally'
        )
        
        # 发送无法路由的消息（没有队列绑定这个路由键）
        self.channel.basic_publish(
            exchange='main_exchange',
            routing_key='nonexistent_key',
            body='This message will go to the alternate exchange'
        )
        
        # 等待消息处理
        time.sleep(2)
        
        # 清理
        self.cleanup_consumers()
        self.disconnect()
        print(" [*] Alternate Exchange demo completed\n")
    
    def demo_exchange_to_exchange_binding(self):
        """演示交换机到交换机的绑定"""
        print("\n=== Exchange-to-Exchange Binding Demo ===")
        
        self.connect()
        
        # 声明第一个交换机
        self.channel.exchange_declare(
            exchange='exchange1',
            exchange_type='direct',
            durable=True
        )
        
        # 声明第二个交换机
        self.channel.exchange_declare(
            exchange='exchange2',
            exchange_type='topic',
            durable=True
        )
        
        # 将第一个交换机绑定到第二个交换机
        self.channel.exchange_bind(
            destination='exchange2',
            source='exchange1',
            routing_key='routing.from.exchange1'
        )
        
        # 声明队列并绑定到第二个交换机
        self.channel.queue_declare(queue='final_queue', durable=True)
        self.channel.queue_bind(
            exchange='exchange2',
            queue='final_queue',
            routing_key='routing.from.exchange1'
        )
        
        # 创建消费者
        def callback(ch, method, properties, body):
            print(f" [Final Consumer] Received through exchange chain: {body.decode('utf-8')}")
        
        self.channel.basic_consume(
            queue='final_queue',
            on_message_callback=callback,
            auto_ack=True
        )
        
        consumer = threading.Thread(target=self.channel.start_consuming)
        consumer.daemon = True
        consumer.start()
        self.consumers.append(consumer)
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发送消息到第一个交换机
        self.channel.basic_publish(
            exchange='exchange1',
            routing_key='routing.from.exchange1',
            body='Message through exchange binding chain'
        )
        
        # 等待消息处理
        time.sleep(2)
        
        # 清理
        self.cleanup_consumers()
        self.disconnect()
        print(" [*] Exchange-to-Exchange Binding demo completed\n")


class ECommerceMessageArchitectureDemo(RabbitMQDemoBase):
    """电商系统消息架构演示"""
    
    def __init__(self, host='localhost'):
        super().__init__(host)
    
    def setup_exchanges(self):
        """设置电商系统的交换机架构"""
        self.connect()
        
        # 1. 订单交换机 - Direct类型，根据订单类型路由
        self.channel.exchange_declare(
            exchange='ecommerce.orders',
            exchange_type='direct',
            durable=True
        )
        
        # 2. 通知交换机 - Fanout类型，广播通知到所有通知服务
        self.channel.exchange_declare(
            exchange='ecommerce.notifications',
            exchange_type='fanout',
            durable=True
        )
        
        # 3. 库存交换机 - Topic类型，按产品和操作类型路由
        self.channel.exchange_declare(
            exchange='ecommerce.inventory',
            exchange_type='topic',
            durable=True
        )
        
        # 4. 事件交换机 - Headers类型，基于事件元数据路由
        self.channel.exchange_declare(
            exchange='ecommerce.events',
            exchange_type='headers',
            durable=True
        )
        
        # 5. 设置备用交换机，处理无法路由的消息
        self.channel.exchange_declare(
            exchange='ecommerce.unrouted',
            exchange_type='fanout',
            durable=True
        )
        
        print(" [*] E-commerce exchanges setup completed")
    
    def setup_queues_and_bindings(self):
        """设置队列和绑定关系"""
        # 订单处理队列
        order_types = ['standard', 'express', 'international']
        for order_type in order_types:
            queue_name = f'orders.{order_type}'
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                exchange='ecommerce.orders',
                queue=queue_name,
                routing_key=order_type
            )
        
        # 通知服务队列
        notification_services = ['email', 'sms', 'push']
        for service in notification_services:
            queue_name = f'notifications.{service}'
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                exchange='ecommerce.notifications',
                queue=queue_name  # Fanout交换机不需要routing_key
            )
        
        # 库存管理队列
        inventory_bindings = [
            ('inventory.reservation', 'product.*.reserve'),
            ('inventory.release', 'product.*.release'),
            ('inventory.adjustment', 'product.*.adjust')
        ]
        
        for queue, binding_key in inventory_bindings:
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.queue_bind(
                exchange='ecommerce.inventory',
                queue=queue,
                routing_key=binding_key
            )
        
        # 事件处理队列
        event_bindings = [
            ('events.user', {'x-match': 'all', 'event_type': 'user_action'}),
            ('events.order', {'x-match': 'all', 'event_type': 'order_event'}),
            ('events.payment', {'x-match': 'all', 'event_type': 'payment_event'})
        ]
        
        for queue, headers in event_bindings:
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.queue_bind(
                exchange='ecommerce.events',
                queue=queue,
                arguments=headers
            )
        
        # 未路由消息队列
        self.channel.queue_declare(queue='unrouted.messages', durable=True)
        self.channel.queue_bind(
            exchange='ecommerce.unrouted',
            queue='unrouted.messages'
        )
        
        print(" [*] E-commerce queues and bindings setup completed")
    
    def create_consumers(self):
        """创建消费者"""
        consumers = []
        
        # 订单处理消费者
        def order_callback(ch, method, properties, body):
            print(f" [Order Consumer {method.routing_key}] Received: {body.decode('utf-8')}")
        
        for order_type in ['standard', 'express', 'international']:
            queue_name = f'orders.{order_type}'
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=order_callback,
                auto_ack=True
            )
            
            consumer = threading.Thread(target=self.channel.start_consuming)
            consumer.daemon = True
            consumer.start()
            consumers.append(consumer)
        
        # 通知服务消费者
        def notification_callback(ch, method, properties, body):
            print(f" [Notification Consumer] Received: {body.decode('utf-8')}")
        
        for service in ['email', 'sms', 'push']:
            queue_name = f'notifications.{service}'
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=notification_callback,
                auto_ack=True
            )
            
            consumer = threading.Thread(target=self.channel.start_consuming)
            consumer.daemon = True
            consumer.start()
            consumers.append(consumer)
        
        # 库存管理消费者
        def inventory_callback(ch, method, properties, body):
            print(f" [Inventory Consumer {method.routing_key}] Received: {body.decode('utf-8')}")
        
        for queue in ['inventory.reservation', 'inventory.release', 'inventory.adjustment']:
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=inventory_callback,
                auto_ack=True
            )
            
            consumer = threading.Thread(target=self.channel.start_consuming)
            consumer.daemon = True
            consumer.start()
            consumers.append(consumer)
        
        # 事件处理消费者
        def event_callback(ch, method, properties, body):
            data = json.loads(body.decode('utf-8'))
            print(f" [Event Consumer] Received event: {data.get('event_type', 'unknown')}")
        
        for queue in ['events.user', 'events.order', 'events.payment']:
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=event_callback,
                auto_ack=True
            )
            
            consumer = threading.Thread(target=self.channel.start_consuming)
            consumer.daemon = True
            consumer.start()
            consumers.append(consumer)
        
        # 未路由消息消费者
        def unrouted_callback(ch, method, properties, body):
            print(f" [Unrouted Consumer] Received unrouted message: {body.decode('utf-8')}")
        
        self.channel.basic_consume(
            queue='unrouted.messages',
            on_message_callback=unrouted_callback,
            auto_ack=True
        )
        
        unrouted_consumer = threading.Thread(target=self.channel.start_consuming)
        unrouted_consumer.daemon = True
        unrouted_consumer.start()
        consumers.append(unrouted_consumer)
        
        self.consumers = consumers
        print(" [*] E-commerce consumers setup completed")
        
        return consumers
    
    def publish_messages(self):
        """发布各种类型的消息"""
        # 1. 发布订单消息
        order_types = ['standard', 'express', 'international']
        for i in range(5):
            order_type = random.choice(order_types)
            order_data = {
                'order_id': f'ORD-{1000 + i}',
                'customer_id': f'CUST-{random.randint(100, 999)}',
                'amount': round(random.uniform(10.0, 500.0), 2),
                'items': random.randint(1, 10)
            }
            
            self.channel.basic_publish(
                exchange='ecommerce.orders',
                routing_key=order_type,
                body=json.dumps(order_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
        
        # 2. 发布通知消息
        for i in range(3):
            notification_data = {
                'notification_id': f'NOTIF-{1000 + i}',
                'recipient_id': f'CUST-{random.randint(100, 999)}',
                'message': f'Your order #{random.randint(1000, 9999)} has been processed',
                'type': random.choice(['email', 'sms', 'push'])
            }
            
            self.channel.basic_publish(
                exchange='ecommerce.notifications',
                routing_key='',  # Fanout交换机忽略路由键
                body=json.dumps(notification_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
        
        # 3. 发布库存消息
        product_ids = ['PROD-001', 'PROD-002', 'PROD-003']
        operations = ['reserve', 'release', 'adjust']
        
        for i in range(6):
            product_id = random.choice(product_ids)
            operation = random.choice(operations)
            routing_key = f'product.{product_id}.{operation}'
            
            inventory_data = {
                'product_id': product_id,
                'operation': operation,
                'quantity': random.randint(1, 10),
                'location': f'LOC-{random.randint(1, 5)}'
            }
            
            self.channel.basic_publish(
                exchange='ecommerce.inventory',
                routing_key=routing_key,
                body=json.dumps(inventory_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
        
        # 4. 发布事件消息
        event_types = ['user_action', 'order_event', 'payment_event']
        for i in range(4):
            event_type = random.choice(event_types)
            
            event_data = {
                'event_id': f'EVT-{1000 + i}',
                'event_type': event_type,
                'user_id': f'USER-{random.randint(100, 999)}',
                'timestamp': int(time.time())
            }
            
            headers = {
                'event_type': event_type,
                'source': 'ecommerce_system',
                'version': '1.0'
            }
            
            self.channel.basic_publish(
                exchange='ecommerce.events',
                routing_key='',  # Headers交换机忽略路由键
                body=json.dumps(event_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    headers=headers,
                    content_type='application/json'
                )
            )
        
        # 5. 发布一个无法路由的消息
        self.channel.basic_publish(
            exchange='ecommerce.orders',
            routing_key='unknown_order_type',  # 没有队列绑定这个路由键
            body=json.dumps({'message': 'This will go to the alternate exchange'}),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        
        print(" [*] Published all test messages")
    
    def run_demo(self):
        """运行电商系统消息架构演示"""
        print("\n=== E-commerce Message Architecture Demo ===")
        
        self.setup_exchanges()
        self.setup_queues_and_bindings()
        self.create_consumers()
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发布消息
        self.publish_messages()
        
        # 等待消息处理
        time.sleep(3)
        
        # 清理
        self.cleanup_consumers()
        self.disconnect()
        print(" [*] E-commerce Message Architecture demo completed\n")


def main():
    """主函数，根据参数运行不同的演示"""
    parser = argparse.ArgumentParser(description='RabbitMQ Exchange Demo')
    parser.add_argument(
        '--type', 
        choices=['direct', 'fanout', 'topic', 'headers', 'advanced', 'ecommerce', 'all'],
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
        'direct': DirectExchangeDemo(args.host),
        'fanout': FanoutExchangeDemo(args.host),
        'topic': TopicExchangeDemo(args.host),
        'headers': HeadersExchangeDemo(args.host),
        'advanced': AdvancedExchangeFeaturesDemo(args.host),
        'ecommerce': ECommerceMessageArchitectureDemo(args.host)
    }
    
    if args.type == 'all':
        # 运行所有演示
        for demo_type, demo in demos.items():
            try:
                if demo_type in ['direct', 'fanout', 'topic', 'headers']:
                    demo.run_demo()
                elif demo_type == 'advanced':
                    demo.demo_alternate_exchange()
                    demo.demo_exchange_to_exchange_binding()
                elif demo_type == 'ecommerce':
                    demo.run_demo()
            except Exception as e:
                print(f"Error running {demo_type} demo: {e}")
    else:
        # 运行指定演示
        try:
            if args.type in ['direct', 'fanout', 'topic', 'headers']:
                demos[args.type].run_demo()
            elif args.type == 'advanced':
                demos['advanced'].demo_alternate_exchange()
                demos['advanced'].demo_exchange_to_exchange_binding()
            elif args.type == 'ecommerce':
                demos['ecommerce'].run_demo()
        except Exception as e:
            print(f"Error running {args.type} demo: {e}")


if __name__ == '__main__':
    main()