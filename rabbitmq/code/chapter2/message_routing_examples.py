#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ消息模式与路由示例代码集合
第2章：RabbitMQ消息模式与路由

包含：
1. 直连交换机示例 (Direct Exchange)
2. 主题交换机示例 (Topic Exchange)  
3. 广播交换机示例 (Fanout Exchange)
4. 头交换机示例 (Headers Exchange)
5. 高级路由模式
6. 动态路由配置
7. 实际应用案例（电商订单处理、日志收集）
"""

import pika
import json
import time
import threading
import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from abc import ABC, abstractmethod


class ExchangeManager:
    """交换机管理器"""
    
    def __init__(self, host='localhost', port=5672, 
                 username='guest', password='guest'):
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password),
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = None
        self.channel = None
    
    def connect(self):
        """建立连接"""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            print(f"✅ 成功连接到RabbitMQ服务器")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                print("🔌 已断开连接")
        except Exception as e:
            print(f"断开连接时出错: {e}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class DirectExchangeExamples:
    """直连交换机示例"""
    
    @staticmethod
    def order_processor_producer():
        """订单处理器生产者"""
        print("\n📤 订单处理器生产者启动")
        
        order_types = ['created', 'updated', 'cancelled', 'paid', 'shipped', 'delivered']
        orders_data = []
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明直连交换机
            channel.exchange_declare(
                exchange='order_direct',
                exchange_type='direct',
                durable=True
            )
            
            # 模拟生成订单
            for i in range(15):
                order_type = random.choice(order_types)
                order_id = f"ORDER_{1000 + i}"
                
                order_data = {
                    'order_id': order_id,
                    'type': order_type,
                    'customer_id': f"CUST_{random.randint(100, 999)}",
                    'amount': round(random.uniform(10.0, 1000.0), 2),
                    'timestamp': datetime.now().isoformat(),
                    'items': [
                        {
                            'product_id': f"PROD_{random.randint(1, 50)}",
                            'quantity': random.randint(1, 5),
                            'price': round(random.uniform(5.0, 100.0), 2)
                        }
                        for _ in range(random.randint(1, 3))
                    ]
                }
                
                orders_data.append(order_data)
                
                # 发送消息到特定路由键
                routing_key = f"order.{order_type}"
                
                channel.basic_publish(
                    exchange='order_direct',
                    routing_key=routing_key,
                    body=json.dumps(order_data, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 持久化
                        content_type='application/json',
                        message_id=f"{order_id}_{order_type}",
                        priority=random.randint(1, 5) if order_type in ['paid', 'urgent'] else 0
                    )
                )
                
                print(f"✅ 发送订单: {order_id} - {order_type}")
                time.sleep(0.8)
        
        print(f"📤 所有订单数据发送完成，共 {len(orders_data)} 条")
        return orders_data
    
    @staticmethod
    def order_processor_consumer(queue_name, routing_key_pattern):
        """订单处理器消费者"""
        print(f"\n📥 {queue_name} 消费者启动")
        print(f"   监听路由键: {routing_key_pattern}")
        
        def callback(ch, method, properties, body):
            try:
                order_data = json.loads(body.decode('utf-8'))
                
                print(f"\n🔄 [{queue_name}] 处理订单:")
                print(f"   订单ID: {order_data['order_id']}")
                print(f"   类型: {order_data['type']}")
                print(f"   客户: {order_data['customer_id']}")
                print(f"   金额: ¥{order_data['amount']}")
                print(f"   商品数量: {len(order_data['items'])}")
                print(f"   时间: {order_data['timestamp']}")
                if properties.priority > 0:
                    print(f"   优先级: {properties.priority}")
                
                # 模拟处理时间
                processing_time = random.uniform(0.5, 2.0)
                time.sleep(processing_time)
                
                print(f"✅ [{queue_name}] 处理完成，耗时 {processing_time:.1f}秒")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ [{queue_name}] 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明临时队列
            result = channel.queue_declare(
                queue=f'direct_consumer_{queue_name.replace(" ", "_")}',
                exclusive=True,
                auto_delete=True
            )
            
            queue_name_full = result.method.queue
            
            # 绑定到直连交换机
            channel.queue_bind(
                exchange='order_direct',
                queue=queue_name_full,
                routing_key=routing_key_pattern
            )
            
            print(f"✅ 队列绑定成功: {queue_name_full}")
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=2)
            
            # 开始消费
            channel.basic_consume(
                queue=queue_name_full,
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                print("⏳ 等待消息... (按 Ctrl+C 退出)")
                channel.start_consuming()
            except KeyboardInterrupt:
                print(f"\n👋 {queue_name} 消费者已停止")


class TopicExchangeExamples:
    """主题交换机示例"""
    
    @staticmethod
    def log_producer():
        """日志生产者"""
        print("\n📤 日志生产者启动")
        
        # 定义日志模式和消息
        log_patterns = {
            'system.startup': '🔧 系统启动完成',
            'system.shutdown': '🔌 系统正在关闭', 
            'system.error': '❌ 系统错误：内存不足警告',
            'system.performance': '⚡ 系统性能监控：CPU使用率85%',
            'app.user.login': '👤 用户登录成功：user_id=12345',
            'app.user.logout': '🚪 用户退出登录：user_id=12345',
            'app.error.database': '💾 数据库连接失败，正在重试',
            'app.api.request': '🌐 API请求：GET /api/users',
            'security.attack': '🚨 检测到可疑攻击：SQL注入尝试',
            'security.login_failed': '🔒 登录失败：用户名或密码错误',
            'security.access_granted': '✅ 访问授权：管理员访问后台',
            'business.order.created': '📦 订单创建：订单号=ORDER_001',
            'business.order.shipped': '🚚 订单已发货：ORDER_001',
            'business.payment.completed': '💳 支付完成：订单=ORDER_001'
        }
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明主题交换机
            channel.exchange_declare(
                exchange='logs_topic',
                exchange_type='topic',
                durable=True
            )
            
            sent_logs = 0
            for routing_key, message in log_patterns.items():
                log_entry = {
                    'routing_key': routing_key,
                    'message': message,
                    'category': routing_key.split('.')[0],
                    'timestamp': datetime.now().isoformat(),
                    'source': 'log_producer',
                    'level': 'INFO',
                    'host': 'server-01',
                    'environment': 'production',
                    'metadata': {
                        'request_id': f"req_{random.randint(1000, 9999)}",
                        'user_id': f"user_{random.randint(100, 999)}",
                        'session_id': f"sess_{random.randint(1000, 9999)}"
                    }
                }
                
                channel.basic_publish(
                    exchange='logs_topic',
                    routing_key=routing_key,
                    body=json.dumps(log_entry, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json',
                        message_id=f"log_{int(time.time())}_{random.randint(1000, 9999)}"
                    )
                )
                
                print(f"📝 发布日志: [{routing_key}] {message}")
                sent_logs += 1
                time.sleep(1.2)
        
        print(f"📤 所有日志发布完成，共 {sent_logs} 条")
    
    @staticmethod
    def log_subscriber(subscriber_name, subscription_pattern):
        """日志订阅者"""
        print(f"\n📥 {subscriber_name} 订阅者启动")
        print(f"   订阅模式: {subscription_pattern}")
        
        def callback(ch, method, properties, body):
            try:
                log_entry = json.loads(body.decode('utf-8'))
                
                print(f"\n📝 [{subscriber_name}] 收到日志:")
                print(f"   📍 路由键: {method.routing_key}")
                print(f"   💬 消息: {log_entry['message']}")
                print(f"   🏷️  类别: {log_entry['category']}")
                print(f"   ⏰ 时间: {log_entry['timestamp']}")
                print(f"   🏢 来源: {log_entry['source']}")
                print(f"   📊 级别: {log_entry['level']}")
                print(f"   🖥️  主机: {log_entry['host']}")
                print(f"   🌍 环境: {log_entry['environment']}")
                if log_entry.get('metadata'):
                    print(f"   📋 元数据: {log_entry['metadata']}")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ [{subscriber_name}] 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 创建临时队列
            result = channel.queue_declare(
                queue=f'topic_sub_{subscriber_name.replace(" ", "_")}',
                exclusive=True,
                auto_delete=True
            )
            
            queue_name = result.method.queue
            
            # 绑定到主题交换机
            channel.queue_bind(
                exchange='logs_topic',
                queue=queue_name,
                routing_key=subscription_pattern
            )
            
            print(f"✅ 订阅成功，队列: {queue_name}")
            print(f"   匹配模式: {subscription_pattern}")
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                print("⏳ 等待消息... (按 Ctrl+C 退出)")
                channel.start_consuming()
            except KeyboardInterrupt:
                print(f"\n👋 {subscriber_name} 订阅者已停止")


class FanoutExchangeExamples:
    """广播交换机示例"""
    
    @staticmethod
    def notification_producer():
        """通知生产者"""
        print("\n📤 通知广播者启动")
        
        notifications = [
            {
                'title': '🚀 系统升级通知',
                'message': '系统将于今晚22:00进行维护升级，预计影响2小时',
                'type': 'maintenance',
                'priority': 'high',
                'channels': ['email', 'sms', 'push']
            },
            {
                'title': '🎉 新功能发布',
                'message': '最新版本v2.1已发布，新增AI智能推荐功能',
                'type': 'feature',
                'priority': 'medium',
                'channels': ['email', 'push']
            },
            {
                'title': '⚠️ 安全提醒',
                'message': '检测到异常登录尝试，请及时检查账户安全',
                'type': 'security',
                'priority': 'urgent',
                'channels': ['sms', 'email', 'push']
            },
            {
                'title': '📊 月度报告',
                'message': '您的月度使用报告已生成，可查看详细数据分析',
                'type': 'report',
                'priority': 'low',
                'channels': ['email']
            },
            {
                'title': '🎁 优惠活动',
                'message': '双11优惠活动开始啦！全场商品8折优惠',
                'type': 'promotion',
                'priority': 'medium',
                'channels': ['email', 'push']
            }
        ]
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明广播交换机
            channel.exchange_declare(
                exchange='notifications_fanout',
                exchange_type='fanout',
                durable=True
            )
            
            for notification in notifications:
                notification_data = {
                    **notification,
                    'id': f"notif_{int(time.time())}_{random.randint(1000, 9999)}",
                    'timestamp': datetime.now().isoformat(),
                    'sender': 'system_admin'
                }
                
                channel.basic_publish(
                    exchange='notifications_fanout',
                    routing_key='',  # 广播交换机忽略路由键
                    body=json.dumps(notification_data, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json',
                        message_id=notification_data['id']
                    )
                )
                
                print(f"📢 广播通知: {notification['title']}")
                print(f"   消息: {notification['message']}")
                print(f"   类型: {notification['type']} | 优先级: {notification['priority']}")
                print(f"   渠道: {', '.join(notification['channels'])}")
                print()
                
                time.sleep(1.5)
        
        print("📤 所有通知广播完成")
    
    @staticmethod
    def notification_channel_handler(channel_name):
        """通知渠道处理器"""
        print(f"\n📥 {channel_name} 渠道处理器启动")
        
        def callback(ch, method, properties, body):
            try:
                notification = json.loads(body.decode('utf-8'))
                
                print(f"\n📢 [{channel_name}] 收到通知:")
                print(f"   📌 标题: {notification['title']}")
                print(f"   💬 内容: {notification['message']}")
                print(f"   🏷️  类型: {notification['type']}")
                print(f"   ⚡ 优先级: {notification['priority']}")
                print(f"   📧 发送者: {notification['sender']}")
                print(f"   ⏰ 时间: {notification['timestamp']}")
                
                # 模拟渠道特定的发送处理
                if channel_name == 'Email服务':
                    print(f"   📧 发送邮件到用户收件箱")
                elif channel_name == 'SMS服务':
                    print(f"   📱 发送短信到用户手机")
                elif channel_name == 'Push推送':
                    print(f"   📲 发送推送通知到移动端")
                
                # 模拟发送延迟
                send_time = random.uniform(0.2, 1.0)
                time.sleep(send_time)
                
                print(f"✅ [{channel_name}] 发送完成")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ [{channel_name}] 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 创建临时队列
            result = channel.queue_declare(
                queue=f'fanout_handler_{channel_name.replace(" ", "_")}',
                exclusive=True,
                auto_delete=True
            )
            
            queue_name = result.method.queue
            
            # 绑定到广播交换机
            channel.queue_bind(
                exchange='notifications_fanout',
                queue=queue_name
            )
            
            print(f"✅ 渠道处理器就绪，队列: {queue_name}")
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=2)
            
            # 开始消费
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                print("⏳ 等待通知... (按 Ctrl+C 退出)")
                channel.start_consuming()
            except KeyboardInterrupt:
                print(f"\n👋 {channel_name} 渠道处理器已停止")


class HeadersExchangeExamples:
    """头交换机示例"""
    
    @staticmethod
    def content_router_producer():
        """内容路由器生产者"""
        print("\n📤 内容路由器生产者启动")
        
        # 定义不同类型的内容消息
        content_messages = [
            {
                'content_id': 'CONTENT_001',
                'title': '最新AI技术报告',
                'body': '深度分析人工智能在各行业的应用现状与未来趋势',
                'content_type': 'report',
                'language': 'zh-CN',
                'priority': 'high',
                'audience': 'tech_professionals',
                'format': 'pdf',
                'tags': ['AI', 'technology', 'report']
            },
            {
                'content_id': 'CONTENT_002', 
                'title': '产品营销邮件模板',
                'body': '针对新产品发布的营销邮件内容模板',
                'content_type': 'marketing',
                'language': 'zh-CN',
                'priority': 'medium',
                'audience': 'customers',
                'format': 'html',
                'tags': ['marketing', 'email', 'template']
            },
            {
                'content_id': 'CONTENT_003',
                'title': '系统更新公告',
                'body': '本次更新修复了多个安全漏洞和性能问题',
                'content_type': 'announcement',
                'language': 'en-US',
                'priority': 'urgent',
                'audience': 'all_users',
                'format': 'text',
                'tags': ['update', 'security', 'announcement']
            },
            {
                'content_id': 'CONTENT_004',
                'title': 'API使用指南',
                'body': '详细介绍如何使用我们的REST API接口',
                'content_type': 'documentation',
                'language': 'zh-CN',
                'priority': 'medium',
                'audience': 'developers',
                'format': 'markdown',
                'tags': ['API', 'documentation', 'guide']
            }
        ]
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明头交换机
            channel.exchange_declare(
                exchange='content_headers',
                exchange_type='headers',
                durable=True
            )
            
            for content in content_messages:
                message_data = {
                    **content,
                    'timestamp': datetime.now().isoformat(),
                    'publisher': 'content_team'
                }
                
                # 定义消息头属性
                headers = {
                    'content-type': content['content_type'],
                    'language': content['language'],
                    'priority': content['priority'],
                    'audience': content['audience'],
                    'format': content['format']
                }
                
                channel.basic_publish(
                    exchange='content_headers',
                    routing_key='',  # 头交换机忽略路由键
                    body=json.dumps(message_data, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json',
                        message_id=content['content_id'],
                        headers=headers
                    )
                )
                
                print(f"📄 路由内容: {content['content_id']} - {content['title']}")
                print(f"   类型: {content['content_type']} | 语言: {content['language']}")
                print(f"   优先级: {content['priority']} | 受众: {content['audience']}")
                print(f"   格式: {content['format']}")
                print()
                
                time.sleep(1.2)
        
        print("📤 所有内容路由消息发送完成")
    
    @staticmethod
    def content_processor_consumer(consumer_name, header_filters):
        """内容处理器消费者"""
        print(f"\n📥 {consumer_name} 处理器启动")
        print(f"   头过滤器: {header_filters}")
        
        def callback(ch, method, properties, body):
            try:
                content = json.loads(body.decode('utf-8'))
                headers = properties.headers or {}
                
                print(f"\n📄 [{consumer_name}] 收到内容:")
                print(f"   📌 标题: {content['title']}")
                print(f"   📝 内容: {content['body'][:50]}...")
                print(f"   🏷️  类型: {content['content_type']}")
                print(f"   🌐 语言: {content['language']}")
                print(f"   ⚡ 优先级: {content['priority']}")
                print(f"   👥 受众: {content['audience']}")
                print(f"   📄 格式: {content['format']}")
                print(f"   🏷️  标签: {content['tags']}")
                print(f"   ⏰ 时间: {content['timestamp']}")
                
                # 模拟处理过程
                processing_time = random.uniform(0.5, 1.5)
                
                if consumer_name == '高优先级处理器':
                    if content['priority'] in ['high', 'urgent']:
                        print(f"   ✅ 确认为高优先级内容，开始处理")
                        time.sleep(processing_time)
                    else:
                        print(f"   ⚠️  跳过低优先级内容")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                        
                elif consumer_name == '技术文档处理器':
                    if content['content_type'] == 'documentation':
                        print(f"   ✅ 确认为技术文档，开始处理")
                        time.sleep(processing_time)
                    else:
                        print(f"   ⚠️  跳过非技术文档")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                        
                elif consumer_name == '中文内容处理器':
                    if content['language'] == 'zh-CN':
                        print(f"   ✅ 确认为中文内容，开始处理")
                        time.sleep(processing_time)
                    else:
                        print(f"   ⚠️  跳过非中文内容")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                
                print(f"✅ [{consumer_name}] 处理完成")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ [{consumer_name}] 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 创建临时队列
            result = channel.queue_declare(
                queue=f'headers_consumer_{consumer_name.replace(" ", "_")}',
                exclusive=True,
                auto_delete=True
            )
            
            queue_name = result.method.queue
            
            # 绑定到头交换机
            channel.queue_bind(
                exchange='content_headers',
                queue=queue_name,
                arguments=header_filters
            )
            
            print(f"✅ 处理器就绪，队列: {queue_name}")
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                print("⏳ 等待消息... (按 Ctrl+C 退出)")
                channel.start_consuming()
            except KeyboardInterrupt:
                print(f"\n👋 {consumer_name} 处理器已停止")


class AdvancedRoutingExamples:
    """高级路由模式示例"""
    
    @staticmethod
    def multi_level_router():
        """多层路由器示例"""
        print("\n📤 多层路由器生产者启动")
        
        # 第一层：业务域路由
        business_domains = {
            'ecommerce': ['order', 'payment', 'inventory', 'shipping'],
            'finance': ['transaction', 'balance', 'loan', 'investment'],
            'social': ['post', 'comment', 'friend', 'message'],
            'analytics': ['event', 'metric', 'report', 'dashboard']
        }
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明多层交换机
            # 第一层：业务域交换机
            for domain in business_domains.keys():
                channel.exchange_declare(
                    exchange=f'{domain}_domain',
                    exchange_type='topic',
                    durable=True
                )
            
            # 第二层：全局事件交换机
            channel.exchange_declare(
                exchange='global_events',
                exchange_type='topic',
                durable=True
            )
            
            # 生成复合事件消息
            events_count = 0
            for domain, event_types in business_domains.items():
                for event_type in event_types:
                    for i in range(2):  # 每个类型生成2个事件
                        event_data = {
                            'event_id': f"{domain}_{event_type}_{i+1}",
                            'domain': domain,
                            'event_type': event_type,
                            'timestamp': datetime.now().isoformat(),
                            'data': {
                                'user_id': f"user_{random.randint(1000, 9999)}",
                                'session_id': f"sess_{random.randint(1000, 9999)}",
                                'source': 'multi_level_router'
                            }
                        }
                        
                        # 路由键格式：domain.event_type
                        routing_key = f"{domain}.{event_type}.*"
                        
                        # 第一步：发送到业务域交换机
                        channel.basic_publish(
                            exchange=f'{domain}_domain',
                            routing_key=routing_key,
                            body=json.dumps(event_data, ensure_ascii=False),
                            properties=pika.BasicProperties(
                                delivery_mode=2,
                                content_type='application/json',
                                message_id=event_data['event_id']
                            )
                        )
                        
                        # 第二步：转发到全局事件交换机
                        global_routing_key = f"*.{event_type}.*"
                        channel.basic_publish(
                            exchange='global_events',
                            routing_key=global_routing_key,
                            body=json.dumps(event_data, ensure_ascii=False),
                            properties=pika.BasicProperties(
                                delivery_mode=2,
                                content_type='application/json',
                                message_id=f"global_{event_data['event_id']}"
                            )
                        )
                        
                        print(f"📡 路由事件: {domain}.{event_type}.* → 全局事件")
                        events_count += 2  # 每个事件发送到两个交换机
                        time.sleep(0.3)
        
        print(f"📤 多层路由完成，共发送 {events_count} 条消息")
    
    @staticmethod
    def dynamic_router_consumer():
        """动态路由器消费者"""
        print(f"\n📥 动态路由器消费者启动")
        print("模拟不同的动态路由规则")
        
        # 动态路由规则
        routing_rules = {
            'time_based': {
                'pattern': lambda msg: msg['timestamp'].split('T')[1][:2],  # 基于小时
                'queues': {
                    '09': 'morning_queue',
                    '14': 'afternoon_queue', 
                    '20': 'evening_queue'
                }
            },
            'load_based': {
                'pattern': lambda msg: 'high' if msg.get('priority') == 'urgent' else 'normal',
                'queues': {
                    'high': 'high_priority_queue',
                    'normal': 'normal_queue'
                }
            },
            'content_based': {
                'pattern': lambda msg: msg.get('event_type', 'unknown'),
                'queues': {
                    'order': 'order_queue',
                    'payment': 'payment_queue',
                    'transaction': 'finance_queue'
                }
            }
        }
        
        for rule_name, rule_config in routing_rules.items():
            print(f"\n🔄 测试路由规则: {rule_name}")
            
            # 创建示例消息
            sample_messages = []
            for i in range(6):
                message = {
                    'message_id': f"msg_{rule_name}_{i+1}",
                    'timestamp': datetime.now().isoformat(),
                    'priority': random.choice(['urgent', 'normal']),
                    'event_type': random.choice(['order', 'payment', 'transaction']),
                    'routing_rule': rule_name
                }
                sample_messages.append(message)
            
            # 应用路由规则
            for message in sample_messages:
                try:
                    # 提取路由值
                    route_value = rule_config['pattern'](message)
                    
                    # 确定目标队列
                    target_queue = rule_config['queues'].get(route_value, 'default_queue')
                    
                    print(f"   消息 {message['message_id']} → {route_value} → {target_queue}")
                    
                except Exception as e:
                    print(f"   ❌ 路由失败 {message['message_id']}: {e}")
            
            time.sleep(1)


class RealWorldExamples:
    """实际应用案例示例"""
    
    @staticmethod
    def ecommerce_order_flow():
        """电商订单流程处理"""
        print("\n📤 电商订单流程生产者启动")
        
        # 模拟订单处理流程
        order_flows = [
            {
                'order_id': 'ORDER_001',
                'customer_id': 'CUST_123',
                'flow': 'standard',
                'steps': ['inventory_check', 'payment_process', 'order_confirmation', 'shipping_prep']
            },
            {
                'order_id': 'ORDER_002', 
                'customer_id': 'CUST_456',
                'flow': 'express',
                'steps': ['inventory_check', 'payment_process', 'order_confirmation', 'express_shipping']
            },
            {
                'order_id': 'ORDER_003',
                'customer_id': 'CUST_789',
                'flow': 'pre_order',
                'steps': ['inventory_check', 'payment_process', 'pre_order_confirmation', 'future_shipping']
            }
        ]
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明订单交换机
            channel.exchange_declare(
                exchange='order_workflow',
                exchange_type='topic',
                durable=True
            )
            
            for order_flow in order_flows:
                print(f"\n📦 处理订单流程: {order_flow['order_id']}")
                print(f"   客户: {order_flow['customer_id']}")
                print(f"   流程: {order_flow['flow']}")
                
                # 发送订单开始消息
                start_message = {
                    'order_id': order_flow['order_id'],
                    'customer_id': order_flow['customer_id'],
                    'flow_type': order_flow['flow'],
                    'step': 'start',
                    'timestamp': datetime.now().isoformat(),
                    'steps': order_flow['steps']
                }
                
                # 发送到订单开始队列
                channel.basic_publish(
                    exchange='order_workflow',
                    routing_key='order.started',
                    body=json.dumps(start_message, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json',
                        message_id=f"{order_flow['order_id']}_start"
                    )
                )
                
                print(f"   ✅ 订单流程启动")
                
                # 模拟步骤处理
                for step_idx, step in enumerate(order_flow['steps']):
                    time.sleep(0.8)
                    
                    step_message = {
                        'order_id': order_flow['order_id'],
                        'customer_id': order_flow['customer_id'],
                        'flow_type': order_flow['flow'],
                        'step': step,
                        'step_index': step_idx,
                        'timestamp': datetime.now().isoformat(),
                        'status': random.choice(['completed', 'pending', 'failed']) if step_idx < len(order_flow['steps']) - 1 else 'completed'
                    }
                    
                    routing_key = f'order.{step}'
                    
                    channel.basic_publish(
                        exchange='order_workflow',
                        routing_key=routing_key,
                        body=json.dumps(step_message, ensure_ascii=False),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json',
                            message_id=f"{order_flow['order_id']}_{step}"
                        )
                    )
                    
                    print(f"   🔄 步骤 {step_idx + 1}: {step} - {step_message['status']}")
        
        print("📤 所有订单流程消息发送完成")
    
    @staticmethod
    def centralized_logging_system():
        """集中式日志收集系统"""
        print("\n📤 集中式日志系统生产者启动")
        
        # 定义不同服务的日志模式
        service_logs = {
            'web_server': [
                ('web_server.access', 'GET /api/users 200 OK'),
                ('web_server.access', 'POST /api/login 401 Unauthorized'),
                ('web_server.error', 'Database connection timeout'),
                ('web_server.performance', 'Response time: 250ms')
            ],
            'api_gateway': [
                ('api_gateway.request', 'Request forwarded to user_service'),
                ('api_gateway.rate_limit', 'Rate limit exceeded for client 192.168.1.100'),
                ('api_gateway.error', 'Upstream service unavailable'),
                ('api_gateway.auth', 'Token validation failed')
            ],
            'database': [
                ('database.query', 'SELECT * FROM users WHERE id=123'),
                ('database.slow_query', 'Complex JOIN query took 5s'),
                ('database.error', 'Deadlock detected on table orders'),
                ('database.backup', 'Daily backup completed successfully')
            ],
            'cache': [
                ('cache.hit', 'Key: user_123 found in cache'),
                ('cache.miss', 'Key: session_456 not found'),
                ('cache.eviction', 'LRU eviction: removed 100 items'),
                ('cache.error', 'Redis connection failed')
            ]
        }
        
        with ExchangeManager() as manager:
            channel = manager.channel
            
            # 声明日志交换机
            channel.exchange_declare(
                exchange='centralized_logs',
                exchange_type='topic',
                durable=True
            )
            
            total_logs = 0
            for service, log_patterns in service_logs.items():
                print(f"\n📝 收集 {service} 日志:")
                
                for routing_key, log_message in log_patterns:
                    log_entry = {
                        'service': service,
                        'log_level': routing_key.split('.')[-1],
                        'message': log_message,
                        'timestamp': datetime.now().isoformat(),
                        'host': f'{service}-01',
                        'environment': 'production',
                        'facility': 'application',
                        'severity': random.choice(['INFO', 'WARNING', 'ERROR', 'DEBUG']),
                        'metadata': {
                            'request_id': f"req_{random.randint(10000, 99999)}",
                            'trace_id': f"trace_{random.randint(10000, 99999)}",
                            'span_id': f"span_{random.randint(10000, 99999)}"
                        }
                    }
                    
                    channel.basic_publish(
                        exchange='centralized_logs',
                        routing_key=routing_key,
                        body=json.dumps(log_entry, ensure_ascii=False),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json',
                            message_id=f"log_{service}_{int(time.time())}_{random.randint(1000, 9999)}"
                        )
                    )
                    
                    print(f"   📄 {routing_key}: {log_message}")
                    total_logs += 1
                    time.sleep(0.4)
        
        print(f"📤 集中式日志收集完成，共 {total_logs} 条日志")


def main():
    """主函数 - 演示所有消息路由功能"""
    print("🔀 RabbitMQ 消息模式与路由演示")
    print("=" * 50)
    
    # 检查连接
    try:
        with ExchangeManager() as connector:
            print("✅ RabbitMQ 连接正常")
    except Exception as e:
        print(f"❌ 无法连接到RabbitMQ: {e}")
        print("请确保RabbitMQ服务正在运行并启用了管理界面插件")
        return
    
    while True:
        print("\n请选择要演示的功能:")
        print("1. 直连交换机示例 (Direct Exchange)")
        print("2. 主题交换机示例 (Topic Exchange)")
        print("3. 广播交换机示例 (Fanout Exchange)")
        print("4. 头交换机示例 (Headers Exchange)")
        print("5. 高级路由模式示例")
        print("6. 实际应用案例示例")
        print("7. 电商订单流程处理")
        print("8. 集中式日志收集系统")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-8): ").strip()
            
            if choice == '1':
                print("\n选择模式:")
                print("1. 运行订单生产者")
                print("2. 运行订单消费者")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    DirectExchangeExamples.order_processor_producer()
                elif mode == '2':
                    print("选择消费者类型:")
                    consumers = [
                        ("创建订单处理器", "order.created"),
                        ("支付订单处理器", "order.paid"),
                        ("错误处理器", "order.error"),
                        ("通用处理器", "order.*")
                    ]
                    
                    for i, (name, pattern) in enumerate(consumers, 1):
                        print(f"{i}. {name} (模式: {pattern})")
                    
                    consumer_choice = input("请选择消费者 (1-4): ").strip()
                    if consumer_choice in ['1', '2', '3', '4']:
                        selected = consumers[int(consumer_choice) - 1]
                        DirectExchangeExamples.order_processor_consumer(selected[0], selected[1])
                    
            elif choice == '2':
                print("\n选择模式:")
                print("1. 运行日志生产者")
                print("2. 运行日志订阅者")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    TopicExchangeExamples.log_producer()
                elif mode == '2':
                    print("选择订阅模式:")
                    patterns = [
                        ("系统日志订阅者", "system.*"),
                        ("应用日志订阅者", "app.*"),
                        ("安全日志订阅者", "security.*"),
                        ("错误日志订阅者", "*.error"),
                        ("全量日志订阅者", "#")
                    ]
                    
                    for i, (name, pattern) in enumerate(patterns, 1):
                        print(f"{i}. {name} (模式: {pattern})")
                    
                    pattern_choice = input("请选择模式 (1-5): ").strip()
                    if pattern_choice in ['1', '2', '3', '4', '5']:
                        selected = patterns[int(pattern_choice) - 1]
                        TopicExchangeExamples.log_subscriber(selected[0], selected[1])
                        
            elif choice == '3':
                print("\n选择模式:")
                print("1. 运行通知广播者")
                print("2. 运行通知渠道处理器")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    FanoutExchangeExamples.notification_producer()
                elif mode == '2':
                    print("选择渠道:")
                    channels = [
                        "Email服务",
                        "SMS服务", 
                        "Push推送"
                    ]
                    
                    for i, channel in enumerate(channels, 1):
                        print(f"{i}. {channel}")
                    
                    channel_choice = input("请选择渠道 (1-3): ").strip()
                    if channel_choice in ['1', '2', '3']:
                        selected_channel = channels[int(channel_choice) - 1]
                        FanoutExchangeExamples.notification_channel_handler(selected_channel)
                        
            elif choice == '4':
                print("\n选择模式:")
                print("1. 运行内容路由器生产者")
                print("2. 运行内容处理器消费者")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    HeadersExchangeExamples.content_router_producer()
                elif mode == '2':
                    print("选择处理器:")
                    consumers = [
                        ("高优先级处理器", {'x-match': 'all', 'priority': 'high'}),
                        ("技术文档处理器", {'x-match': 'all', 'content-type': 'documentation'}),
                        ("中文内容处理器", {'x-match': 'all', 'language': 'zh-CN'})
                    ]
                    
                    for i, (name, filters) in enumerate(consumers, 1):
                        print(f"{i}. {name}")
                    
                    consumer_choice = input("请选择处理器 (1-3): ").strip()
                    if consumer_choice in ['1', '2', '3']:
                        selected = consumers[int(consumer_choice) - 1]
                        HeadersExchangeExamples.content_processor_consumer(selected[0], selected[1])
                        
            elif choice == '5':
                print("\n选择高级路由模式:")
                print("1. 多层路由系统")
                print("2. 动态路由器消费者")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    AdvancedRoutingExamples.multi_level_router()
                elif mode == '2':
                    AdvancedRoutingExamples.dynamic_router_consumer()
                    
            elif choice == '6':
                print("\n选择实际应用案例:")
                print("1. 电商订单流程处理")
                print("2. 集中式日志收集系统")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    RealWorldExamples.ecommerce_order_flow()
                elif mode == '2':
                    RealWorldExamples.centralized_logging_system()
                    
            elif choice == '7':
                RealWorldExamples.ecommerce_order_flow()
                
            elif choice == '8':
                RealWorldExamples.centralized_logging_system()
                
            elif choice == '0':
                print("👋 再见!")
                break
                
            else:
                print("❌ 无效选择，请重试")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，程序退出")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            
        input("\n按回车键继续...")


if __name__ == '__main__':
    main()