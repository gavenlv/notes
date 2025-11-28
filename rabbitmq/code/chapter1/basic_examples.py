#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ基础示例代码集合
第1章：RabbitMQ基础入门

包含：
1. 简单的Hello World示例
2. 工作队列示例
3. 发布/订阅模式示例
4. 主题交换机示例
5. 消息确认和持久化示例
6. 优先级队列示例
"""

import pika
import json
import time
import threading
import random
import os
from datetime import datetime
from typing import Dict, List, Optional


class RabbitMQConnector:
    """RabbitMQ连接管理器"""
    
    def __init__(self, host='localhost', port=5672, 
                 username='guest', password='guest', 
                 virtual_host='/'):
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password),
            virtual_host=virtual_host,
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


class BasicExamples:
    """基础RabbitMQ示例"""
    
    @staticmethod
    def hello_world_producer():
        """Hello World生产者"""
        print("\n📤 Hello World生产者启动")
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 声明队列
            channel.queue_declare(queue='hello', durable=True)
            
            # 发送消息
            for i in range(5):
                message = {
                    'type': 'greeting',
                    'content': f'Hello World! 消息 #{i+1}',
                    'timestamp': datetime.now().isoformat(),
                    'message_id': f'msg_{i+1}'
                }
                
                channel.basic_publish(
                    exchange='',
                    routing_key='hello',
                    body=json.dumps(message, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 消息持久化
                        content_type='application/json',
                        message_id=message['message_id'],
                        timestamp=int(time.time())
                    )
                )
                
                print(f"✅ 已发送消息 {i+1}: {message['content']}")
                time.sleep(1)
    
    @staticmethod
    def hello_world_consumer():
        """Hello World消费者"""
        print("\n📥 Hello World消费者启动")
        print("等待消息... (按 Ctrl+C 退出)")
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode('utf-8'))
                
                print(f"📨 收到消息:")
                print(f"   内容: {message['content']}")
                print(f"   ID: {properties.message_id}")
                print(f"   时间戳: {datetime.fromtimestamp(properties.timestamp).strftime('%H:%M:%S')}")
                
                # 模拟处理时间
                time.sleep(0.5)
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print("✅ 消息已确认并处理完成\n")
                
            except Exception as e:
                print(f"❌ 处理消息失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 声明队列
            channel.queue_declare(queue='hello', durable=True)
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            channel.basic_consume(
                queue='hello',
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                print("\n👋 消费者已停止")


class WorkQueueExamples:
    """工作队列示例"""
    
    @staticmethod
    def task_producer():
        """任务生产者"""
        print("\n📤 工作队列生产者启动")
        
        tasks = [
            "📊 分析销售数据",
            "🖼️ 处理图片文件", 
            "📧 发送营销邮件",
            "💾 备份数据库",
            "📈 生成财务报表",
            "🔍 扫描系统日志",
            "🎯 更新用户画像",
            "📋 处理订单审核"
        ]
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 声明持久化队列
            channel.queue_declare(queue='task_queue', durable=True)
            
            for i, task in enumerate(tasks, 1):
                # 随机设置任务优先级
                priority = random.randint(1, 5)
                
                message = {
                    'task': task,
                    'task_id': i,
                    'priority': priority,
                    'created_at': datetime.now().isoformat(),
                    'estimated_duration': random.randint(2, 10)
                }
                
                channel.basic_publish(
                    exchange='',
                    routing_key='task_queue',
                    body=json.dumps(message, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 持久化
                        priority=priority,  # 设置优先级
                        message_id=f'task_{i}'
                    )
                )
                
                print(f"✅ 已提交任务 {i}: {task} (优先级: {priority})")
                time.sleep(random.uniform(0.5, 2.0))
    
    @staticmethod
    def task_worker(worker_name):
        """任务工作者"""
        print(f"\n👷 {worker_name} 工作者启动")
        print("等待任务... (按 Ctrl+C 退出)")
        
        def callback(ch, method, properties, body):
            try:
                task_data = json.loads(body.decode('utf-8'))
                
                print(f"\n🔄 {worker_name} 开始处理:")
                print(f"   任务: {task_data['task']}")
                print(f"   优先级: {properties.priority}")
                print(f"   预计耗时: {task_data['estimated_duration']}秒")
                
                # 模拟任务处理
                duration = task_data['estimated_duration']
                for second in range(duration):
                    time.sleep(1)
                    progress = (second + 1) / duration * 100
                    print(f"   进度: {progress:.1f}%")
                
                print(f"✅ {worker_name} 完成任务: {task_data['task']}")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ {worker_name} 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 声明队列
            channel.queue_declare(queue='task_queue', durable=True)
            
            # 设置公平调度
            channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            channel.basic_consume(
                queue='task_queue',
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                print(f"\n👋 {worker_name} 已停止")


class PublishSubscribeExamples:
    """发布订阅模式示例"""
    
    @staticmethod
    def news_publisher():
        """新闻发布者"""
        print("\n📤 新闻发布者启动")
        
        news_items = [
            {
                "title": "🚀 科技突破：AI在医疗诊断领域取得重大进展",
                "content": "最新的研究报告显示，人工智能在医疗诊断领域的准确率已达到95%",
                "category": "科技",
                "priority": "high"
            },
            {
                "title": "📈 市场分析：电动车行业持续高速增长",
                "content": "2024年全球电动车销量预计将增长50%，达到1400万辆",
                "category": "商业",
                "priority": "medium"
            },
            {
                "title": "🌍 国际动态：多国签署气候合作协议",
                "content": "50个国家签署了新的气候合作协议，承诺2030年减排50%",
                "category": "国际",
                "priority": "high"
            },
            {
                "title": "🎯 教育改革：编程教育纳入中小学课程",
                "content": "教育部宣布将编程教育正式纳入中小学必修课程",
                "category": "教育",
                "priority": "medium"
            }
        ]
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 声明广播交换机
            channel.exchange_declare(
                exchange='news_exchange',
                exchange_type='fanout'
            )
            
            for news in news_items:
                news['timestamp'] = datetime.now().isoformat()
                news['publisher'] = '新闻中心'
                
                channel.basic_publish(
                    exchange='news_exchange',
                    routing_key='',  # 广播交换机忽略路由键
                    body=json.dumps(news, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        content_type='application/json',
                        message_id=f"news_{int(time.time())}_{random.randint(1000, 9999)}"
                    )
                )
                
                print(f"📰 发布新闻: {news['title']} (类别: {news['category']})")
                time.sleep(2)
        
        print("📤 所有新闻发布完成")
    
    @staticmethod
    def news_subscriber(subscriber_name):
        """新闻订阅者"""
        print(f"\n📥 {subscriber_name} 启动")
        
        def callback(ch, method, properties, body):
            try:
                news = json.loads(body.decode('utf-8'))
                
                print(f"\n📰 [{subscriber_name}] 收到新闻:")
                print(f"   📌 标题: {news['title']}")
                print(f"   📄 内容: {news['content']}")
                print(f"   🏷️  类别: {news['category']}")
                print(f"   ⚡ 优先级: {news['priority']}")
                print(f"   🕒 时间: {news['timestamp']}")
                print(f"   🏢 发布者: {news['publisher']}")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ [{subscriber_name}] 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 创建临时队列
            result = channel.queue_declare(
                queue=f'news_sub_{subscriber_name.replace(" ", "_")}',
                exclusive=True,
                auto_delete=True
            )
            
            queue_name = result.method.queue
            
            # 绑定到交换机
            channel.queue_bind(
                exchange='news_exchange',
                queue=queue_name
            )
            
            print(f"✅ {subscriber_name} 订阅成功，队列: {queue_name}")
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                print(f"\n👋 {subscriber_name} 已停止")


class TopicExchangeExamples:
    """主题交换机示例"""
    
    @staticmethod
    def log_publisher():
        """日志发布者"""
        print("\n📤 日志发布者启动")
        
        log_messages = [
            # 系统日志
            ('system.startup', '🔧 系统启动完成', 'system'),
            ('system.shutdown', '🔌 系统正在关闭', 'system'),
            ('system.error', '❌ 系统错误：内存不足', 'system'),
            ('system.performance', '⚡ 系统性能监控：CPU使用率80%', 'system'),
            
            # 应用日志
            ('app.user.login', '👤 用户登录成功：user_id=12345', 'app'),
            ('app.user.logout', '🚪 用户退出登录：user_id=12345', 'app'),
            ('app.error.database', '💾 数据库连接失败', 'app'),
            ('app.api.request', '🌐 API请求：GET /api/users', 'app'),
            
            # 安全日志
            ('security.attack', '🚨 检测到可疑攻击：SQL注入尝试', 'security'),
            ('security.login_failed', '🔒 登录失败：用户名或密码错误', 'security'),
            ('security.access_granted', '✅ 访问授权：管理员访问后台', 'security'),
            
            # 业务日志
            ('business.order.created', '📦 订单创建：订单号=ORDER_001', 'business'),
            ('business.order.shipped', '🚚 订单已发货：ORDER_001', 'business'),
            ('business.payment.completed', '💳 支付完成：订单=ORDER_001', 'business')
        ]
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 声明主题交换机
            channel.exchange_declare(
                exchange='topic_logs',
                exchange_type='topic'
            )
            
            for routing_key, message, category in log_messages:
                log_data = {
                    'message': message,
                    'category': category,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'log_publisher',
                    'level': 'INFO'
                }
                
                channel.basic_publish(
                    exchange='topic_logs',
                    routing_key=routing_key,
                    body=json.dumps(log_data, ensure_ascii=False),
                    properties=pika.BasicProperties(
                        content_type='application/json',
                        message_id=f"log_{int(time.time())}_{random.randint(1000, 9999)}"
                    )
                )
                
                print(f"📝 发布日志: [{category}] {message} (路由键: {routing_key})")
                time.sleep(1.5)
        
        print("📤 所有日志发布完成")
    
    @staticmethod
    def log_subscriber(pattern, subscriber_name):
        """日志订阅者"""
        print(f"\n📥 {subscriber_name} 启动 (模式: {pattern})")
        
        def callback(ch, method, properties, body):
            try:
                log_data = json.loads(body.decode('utf-8'))
                
                print(f"\n📝 [{subscriber_name}] 日志:")
                print(f"   📍 路由键: {method.routing_key}")
                print(f"   💬 消息: {log_data['message']}")
                print(f"   🏷️  类别: {log_data['category']}")
                print(f"   ⏰ 时间: {log_data['timestamp']}")
                print(f"   🏢 来源: {log_data['source']}")
                print(f"   📊 级别: {log_data['level']}")
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ [{subscriber_name}] 处理失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        with RabbitMQConnector() as connector:
            channel = connector.channel
            
            # 创建临时队列
            result = channel.queue_declare(
                queue=f'log_sub_{subscriber_name.replace(" ", "_")}_{pattern.replace("*", "star").replace("#", "hash")}',
                exclusive=True,
                auto_delete=True
            )
            
            queue_name = result.method.queue
            
            # 绑定到交换机
            channel.queue_bind(
                exchange='topic_logs',
                queue=queue_name,
                routing_key=pattern
            )
            
            print(f"✅ {subscriber_name} 订阅成功，队列: {queue_name}")
            print(f"   匹配模式: {pattern}")
            
            # 设置预取数量
            channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                print(f"\n👋 {subscriber_name} 已停止")


def demonstrate_monitoring():
    """演示监控功能"""
    print("\n📊 RabbitMQ 监控演示")
    
    try:
        import requests
        
        # 连接到管理API
        auth = ('admin', 'admin123')
        base_url = "http://localhost:15672/api"
        
        # 获取集群概览
        response = requests.get(f"{base_url}/overview", auth=auth)
        if response.status_code == 200:
            overview = response.json()
            print(f"集群名称: {overview.get('cluster_name', 'N/A')}")
            
            # 消息统计
            msg_stats = overview.get('message_stats', {})
            print(f"消息发布总数: {msg_stats.get('publish', 0)}")
            print(f"消息确认总数: {msg_stats.get('ack', 0)}")
            
        # 获取队列状态
        response = requests.get(f"{base_url}/queues", auth=auth)
        if response.status_code == 200:
            queues = response.json()
            print(f"\n队列总数: {len(queues)}")
            
            for queue in queues:
                if queue['vhost'] == '/':
                    print(f"  📦 {queue['name']}: {queue['messages']} 条消息, {queue['consumers']} 个消费者")
    
    except Exception as e:
        print(f"监控功能演示失败 (可能需要启用管理界面): {e}")


def main():
    """主函数 - 演示所有基础功能"""
    print("🐰 RabbitMQ 基础示例演示")
    print("=" * 50)
    
    # 检查连接
    try:
        with RabbitMQConnector() as connector:
            print("✅ RabbitMQ 连接正常")
    except Exception as e:
        print(f"❌ 无法连接到RabbitMQ: {e}")
        print("请确保RabbitMQ服务正在运行并启用了管理界面插件")
        return
    
    while True:
        print("\n请选择要演示的功能:")
        print("1. Hello World 示例")
        print("2. 工作队列示例") 
        print("3. 发布订阅模式示例")
        print("4. 主题交换机示例")
        print("5. 监控功能演示")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-5): ").strip()
            
            if choice == '1':
                print("\n选择模式:")
                print("1. 运行生产者")
                print("2. 运行消费者")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    BasicExamples.hello_world_producer()
                elif mode == '2':
                    BasicExamples.hello_world_consumer()
                    
            elif choice == '2':
                print("\n选择模式:")
                print("1. 运行生产者")
                print("2. 运行工作者")
                print("3. 运行多个工作者")
                mode = input("请选择 (1-3): ").strip()
                
                if mode == '1':
                    WorkQueueExamples.task_producer()
                elif mode == '2':
                    worker_name = input("请输入工作者名称: ").strip() or "Worker-1"
                    WorkQueueExamples.task_worker(worker_name)
                elif mode == '3':
                    # 启动多个工作者线程
                    import threading
                    
                    def run_workers():
                        for i in range(3):
                            thread = threading.Thread(
                                target=WorkQueueExamples.task_worker,
                                args=(f"Worker-{i+1}",)
                            )
                            thread.daemon = True
                            thread.start()
                            time.sleep(1)
                        
                        thread.join()
                    
                    run_workers()
                    
            elif choice == '3':
                print("\n选择模式:")
                print("1. 运行发布者")
                print("2. 运行订阅者")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    PublishSubscribeExamples.news_publisher()
                elif mode == '2':
                    subscriber_name = input("请输入订阅者名称: ").strip() or "订阅者-1"
                    PublishSubscribeExamples.news_subscriber(subscriber_name)
                    
            elif choice == '4':
                print("\n选择模式:")
                print("1. 运行日志发布者")
                print("2. 运行日志订阅者")
                mode = input("请选择 (1-2): ").strip()
                
                if mode == '1':
                    TopicExchangeExamples.log_publisher()
                elif mode == '2':
                    patterns = {
                        '1': 'system.*',
                        '2': '*.error', 
                        '3': '#',
                        '4': '*.log'
                    }
                    
                    print("选择订阅模式:")
                    for key, pattern in patterns.items():
                        print(f"{key}. {pattern}")
                    
                    pattern_choice = input("请选择模式 (1-4): ").strip()
                    pattern = patterns.get(pattern_choice, 'system.*')
                    subscriber_name = input("请输入订阅者名称: ").strip() or f"订阅者-{pattern}"
                    
                    TopicExchangeExamples.log_subscriber(pattern, subscriber_name)
                    
            elif choice == '5':
                demonstrate_monitoring()
                
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