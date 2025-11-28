#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第3章：交换机类型深入研究
交换机模式演示和案例研究

功能：
- 直连交换机模式演示
- 主题交换机模式演示  
- 扇形交换机模式演示
- 头交换机模式演示
- 复杂路由场景演示
- 实际应用案例模拟

作者：RabbitMQ学习教程
创建时间：2025年11月
"""

import pika
import time
import json
import threading
import uuid
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class MessageType(Enum):
    """消息类型枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MessagePriority(Enum):
    """消息优先级枚举"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class LogMessage:
    """日志消息结构"""
    message_id: str
    timestamp: float
    source: str
    level: MessageType
    priority: MessagePriority
    content: str
    metadata: Dict[str, Any]


class ExchangePatternsDemo:
    """交换机模式演示"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        
        # 演示场景配置
        self.demo_scenarios = {}
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """建立连接"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    heartbeat=30
                )
            )
            self.channel = self.connection.channel()
            
            self.logger.info(f"✅ 连接到 RabbitMQ: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 连接失败: {e}")
            return False
    
    def setup_demo_environment(self):
        """设置演示环境"""
        print("\n🏗️ 设置演示环境")
        print("=" * 50)
        
        # 1. 直连交换机配置
        self.setup_direct_exchange_scenario()
        
        # 2. 主题交换机配置
        self.setup_topic_exchange_scenario()
        
        # 3. 扇形交换机配置
        self.setup_fanout_exchange_scenario()
        
        # 4. 头交换机配置
        self.setup_headers_exchange_scenario()
        
        # 5. 复杂路由场景
        self.setup_complex_routing_scenario()
        
        print("✅ 演示环境设置完成")
    
    def setup_direct_exchange_scenario(self):
        """设置直连交换机场景"""
        # 创建直连交换机
        self.channel.exchange_declare(
            exchange='direct.logs',
            exchange_type='direct',
            durable=True
        )
        
        # 创建目标队列
        queues = {
            'error_queue': {'durable': True},
            'warning_queue': {'durable': True},
            'info_queue': {'durable': True}
        }
        
        for queue_name, args in queues.items():
            self.channel.queue_declare(queue=queue_name, **args)
            self.channel.queue_bind(
                exchange='direct.logs',
                queue=queue_name,
                routing_key=queue_name.replace('_queue', '')
            )
        
        self.demo_scenarios['direct'] = {
            'exchange': 'direct.logs',
            'queues': list(queues.keys())
        }
        
        print("✅ 直连交换机场景配置完成")
    
    def setup_topic_exchange_scenario(self):
        """设置主题交换机场景"""
        # 创建主题交换机
        self.channel.exchange_declare(
            exchange='topic.logs',
            exchange_type='topic',
            durable=True
        )
        
        # 创建主题绑定队列
        topic_bindings = [
            ('*.critical', 'critical_logs'),
            ('app.*.error', 'app_errors'),
            ('*.warning', 'all_warnings'),
            ('*.*.*', 'all_logs')  # 捕获所有日志
        ]
        
        for routing_key, queue_name in topic_bindings:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                exchange='topic.logs',
                queue=queue_name,
                routing_key=routing_key
            )
        
        self.demo_scenarios['topic'] = {
            'exchange': 'topic.logs',
            'bindings': topic_bindings
        }
        
        print("✅ 主题交换机场景配置完成")
    
    def setup_fanout_exchange_scenario(self):
        """设置扇形交换机场景"""
        # 创建扇形交换机
        self.channel.exchange_declare(
            exchange='fanout.events',
            exchange_type='fanout',
            durable=True
        )
        
        # 创建订阅者队列
        subscribers = [
            'notification_subscriber',
            'analytics_subscriber', 
            'monitoring_subscriber'
        ]
        
        for subscriber in subscribers:
            self.channel.queue_declare(queue=subscriber, durable=True)
            self.channel.queue_bind(
                exchange='fanout.events',
                queue=subscriber
            )
        
        self.demo_scenarios['fanout'] = {
            'exchange': 'fanout.events',
            'subscribers': subscribers
        }
        
        print("✅ 扇形交换机场景配置完成")
    
    def setup_headers_exchange_scenario(self):
        """设置头交换机场景"""
        # 创建头交换机
        self.channel.exchange_declare(
            exchange='headers.messages',
            exchange_type='headers',
            durable=True
        )
        
        # 创建头匹配队列
        header_bindings = [
            {
                'queue': 'high_priority_queue',
                'arguments': {
                    'x-match': 'any',
                    'priority': {'annotation': 'integer'},
                    'content-type': {'annotation': 'string'}
                }
            },
            {
                'queue': 'business_messages',
                'arguments': {
                    'x-match': 'all',
                    'service': 'business',
                    'content-type': {'annotation': 'string'}
                }
            },
            {
                'queue': 'system_messages',
                'arguments': {
                    'x-match': 'all', 
                    'service': 'system'
                }
            }
        ]
        
        for binding in header_bindings:
            self.channel.queue_declare(queue=binding['queue'], durable=True)
            self.channel.queue_bind(
                exchange='headers.messages',
                queue=binding['queue'],
                arguments=binding['arguments']
            )
        
        self.demo_scenarios['headers'] = {
            'exchange': 'headers.messages',
            'bindings': header_bindings
        }
        
        print("✅ 头交换机场景配置完成")
    
    def setup_complex_routing_scenario(self):
        """设置复杂路由场景"""
        # 创建复杂路由交换机
        self.channel.exchange_declare(
            exchange='complex.routing',
            exchange_type='topic',
            durable=True
        )
        
        # 创建路由处理器交换机
        self.channel.exchange_declare(
            exchange='route.handler',
            exchange_type='direct',
            durable=True
        )
        
        # 创建处理器队列
        handlers = ['business_handler', 'system_handler', 'user_handler']
        for handler in handlers:
            self.channel.queue_declare(queue=handler, durable=True)
            self.channel.queue_bind(
                exchange='complex.routing',
                queue=handler
            )
            self.channel.queue_bind(
                exchange='route.handler',
                queue=handler
            )
        
        self.demo_scenarios['complex'] = {
            'main_exchange': 'complex.routing',
            'handler_exchange': 'route.handler',
            'handlers': handlers
        }
        
        print("✅ 复杂路由场景配置完成")
    
    def demo_direct_exchange(self):
        """演示直连交换机"""
        print("\n🎬 直连交换机演示")
        print("=" * 50)
        print("场景：系统日志按级别分发到不同队列")
        
        # 创建测试日志消息
        log_messages = [
            LogMessage(
                message_id=str(uuid.uuid4()),
                timestamp=time.time(),
                source="system",
                level=MessageType.ERROR,
                priority=MessagePriority.HIGH,
                content="数据库连接失败",
                metadata={"component": "database", "retry": 3}
            ),
            LogMessage(
                message_id=str(uuid.uuid4()),
                timestamp=time.time(),
                source="user_service",
                level=MessageType.WARNING,
                priority=MessagePriority.NORMAL,
                content="用户登录尝试异常频繁",
                metadata={"user_id": "12345", "ip": "192.168.1.100"}
            ),
            LogMessage(
                message_id=str(uuid.uuid4()),
                timestamp=time.time(),
                source="payment",
                level=MessageType.INFO,
                priority=MessagePriority.NORMAL,
                content="支付处理成功",
                metadata={"amount": 100.50, "currency": "USD"}
            )
        ]
        
        # 发送消息到对应的队列
        for log_msg in log_messages:
            routing_key = log_msg.level.value + '_queue'
            
            properties = pika.BasicProperties(
                message_id=log_msg.message_id,
                timestamp=log_msg.timestamp,
                delivery_mode=2  # 持久化
            )
            
            message_body = json.dumps(asdict(log_msg), ensure_ascii=False)
            
            self.channel.basic_publish(
                exchange='direct.logs',
                routing_key=routing_key,
                body=message_body,
                properties=properties
            )
            
            print(f"📤 发送 {log_msg.level.value} 消息到 {routing_key}")
            print(f"   内容: {log_msg.content}")
        
        # 模拟消费
        self.simulate_consumer_consumption('direct.logs')
    
    def demo_topic_exchange(self):
        """演示主题交换机"""
        print("\n🎬 主题交换机演示")
        print("=" * 50)
        print("场景：多级日志按模式匹配分发")
        
        # 创建测试消息
        test_messages = [
            {
                'routing_key': 'app.payment.error',
                'content': '应用支付模块错误',
                'description': '匹配 *.critical, app.*.error, *.warning'
            },
            {
                'routing_key': 'system.database.critical', 
                'content': '系统数据库关键错误',
                'description': '匹配 *.critical, 所有日志'
            },
            {
                'routing_key': 'user.auth.warning',
                'content': '用户认证服务警告',
                'description': '匹配 *.warning'
            },
            {
                'routing_key': 'api.gateway.info',
                'content': 'API网关信息日志',
                'description': '匹配 *.*.* (所有日志)'
            }
        ]
        
        for msg_info in test_messages:
            message_id = str(uuid.uuid4())
            properties = pika.BasicProperties(
                message_id=message_id,
                timestamp=time.time()
            )
            
            self.channel.basic_publish(
                exchange='topic.logs',
                routing_key=msg_info['routing_key'],
                body=msg_info['content'],
                properties=properties
            )
            
            print(f"📤 发送: {msg_info['routing_key']}")
            print(f"   内容: {msg_info['content']}")
            print(f"   匹配: {msg_info['description']}")
        
        print("\n📊 消息分发结果:")
        self.show_routing_results('topic.logs')
    
    def demo_fanout_exchange(self):
        """演示扇形交换机"""
        print("\n🎬 扇形交换机演示")
        print("=" * 50)
        print("场景：系统事件广播到所有订阅者")
        
        # 创建事件消息
        events = [
            {
                'type': 'user_registered',
                'content': '新用户注册事件',
                'metadata': {'user_id': '12345', 'email': 'user@example.com'}
            },
            {
                'type': 'order_completed',
                'content': '订单完成事件',
                'metadata': {'order_id': 'ORD-001', 'amount': 299.99}
            },
            {
                'type': 'system_maintenance',
                'content': '系统维护事件',
                'metadata': {'maintenance_start': '2025-11-28 02:00:00'}
            }
        ]
        
        for event in events:
            message_id = str(uuid.uuid4())
            event_data = {
                'event_id': message_id,
                'timestamp': time.time(),
                'type': event['type'],
                'content': event['content'],
                'metadata': event['metadata']
            }
            
            properties = pika.BasicProperties(
                message_id=message_id,
                timestamp=time.time(),
                content_type='application/json'
            )
            
            self.channel.basic_publish(
                exchange='fanout.events',
                routing_key='',
                body=json.dumps(event_data, ensure_ascii=False),
                properties=properties
            )
            
            print(f"📤 广播事件: {event['type']}")
            print(f"   内容: {event['content']}")
        
        print("\n📊 广播结果:")
        print("   所有订阅者都将收到相同的事件消息")
        
        # 模拟多个订阅者
        subscribers = self.demo_scenarios['fanout']['subscribers']
        for subscriber in subscribers:
            print(f"   📥 订阅者 {subscriber} 收到事件")
    
    def demo_headers_exchange(self):
        """演示头交换机"""
        print("\n🎬 头交换机演示")
        print("=" * 50)
        print("场景：基于消息头属性的智能分发")
        
        # 创建带头属性的消息
        test_messages = [
            {
                'headers': {'priority': 9, 'content-type': 'application/json'},
                'body': '{"service": "payment", "action": "refund", "amount": 100}',
                'description': '高优先级JSON业务消息'
            },
            {
                'headers': {'priority': 2, 'content-type': 'text/plain', 'service': 'system'},
                'body': 'System maintenance log entry',
                'description': '低优先级系统文本消息'
            },
            {
                'headers': {'service': 'business', 'content-type': 'application/json'},
                'body': '{"service": "inventory", "action": "update", "item_id": "123"}',
                'description': '中优先级业务JSON消息'
            }
        ]
        
        for msg_info in test_messages:
            message_id = str(uuid.uuid4())
            properties = pika.BasicProperties(
                message_id=message_id,
                timestamp=time.time(),
                headers=msg_info['headers']
            )
            
            self.channel.basic_publish(
                exchange='headers.messages',
                routing_key='',
                body=msg_info['body'],
                properties=properties
            )
            
            print(f"📤 发送消息:")
            print(f"   头部: {msg_info['headers']}")
            print(f"   内容: {msg_info['body']}")
            print(f"   说明: {msg_info['description']}")
        
        print("\n📊 头匹配结果:")
        print("   high_priority_queue: 收到高优先级JSON消息")
        print("   system_messages: 收到系统服务消息")
        print("   business_messages: 收到业务服务消息")
    
    def demo_complex_routing(self):
        """演示复杂路由场景"""
        print("\n🎬 复杂路由演示")
        print("=" * 50)
        print("场景：多级路由和消息处理链")
        
        # 模拟复杂的路由场景
        routing_scenarios = [
            {
                'level': 1,
                'exchange': 'complex.routing',
                'routing_key': 'user.create',
                'message': '用户创建请求',
                'target_handlers': ['business_handler']
            },
            {
                'level': 1,
                'exchange': 'complex.routing',
                'routing_key': 'system.alert',
                'message': '系统警报',
                'target_handlers': ['system_handler', 'monitoring_subscriber']
            },
            {
                'level': 2,
                'exchange': 'route.handler',
                'routing_key': 'business_handler',
                'message': '业务处理器确认',
                'result': '处理完成，回调业务系统'
            }
        ]
        
        for scenario in routing_scenarios:
            message_id = str(uuid.uuid4())
            properties = pika.BasicProperties(
                message_id=message_id,
                timestamp=time.time(),
                correlation_id=f"parent_{scenario['level']}" if scenario['level'] > 1 else None
            )
            
            self.channel.basic_publish(
                exchange=scenario['exchange'],
                routing_key=scenario['routing_key'],
                body=scenario['message'],
                properties=properties
            )
            
            print(f"📤 级别{scenario['level']}路由:")
            print(f"   交换机: {scenario['exchange']}")
            print(f"   路由键: {scenario['routing_key']}")
            print(f"   消息: {scenario['message']}")
            
            if 'target_handlers' in scenario:
                print(f"   目标处理器: {scenario['target_handlers']}")
            if 'result' in scenario:
                print(f"   处理结果: {scenario['result']}")
        
        print("\n📊 复杂路由结果:")
        print("   消息通过多级交换机进行智能路由")
        print("   不同处理器处理不同类型的请求")
        print("   支持异步处理和回调机制")
    
    def simulate_consumer_consumption(self, exchange_name: str):
        """模拟消费者消费消息"""
        print(f"\n📥 模拟消费者消费")
        print("=" * 40)
        
        # 获取与该交换机绑定的队列
        scenario_info = self.get_exchange_scenario(exchange_name)
        
        if scenario_info:
            if 'queues' in scenario_info:  # 直连交换机
                for queue in scenario_info['queues']:
                    print(f"   队列 {queue} 收到相关消息")
            elif 'subscribers' in scenario_info:  # 扇形交换机
                for subscriber in scenario_info['subscribers']:
                    print(f"   订阅者 {subscriber} 收到广播消息")
            elif 'bindings' in scenario_info:  # 主题交换机
                print("   主题匹配队列收到消息:")
                for routing_key, queue_name in scenario_info['bindings']:
                    print(f"     {routing_key} -> {queue_name}")
        
        print("   ✅ 所有消息已被处理")
    
    def get_exchange_scenario(self, exchange_name: str):
        """获取交换机场景信息"""
        for scenario_name, scenario_info in self.demo_scenarios.items():
            if scenario_info.get('exchange') == exchange_name:
                return scenario_info
        return None
    
    def show_routing_results(self, exchange_name: str):
        """显示路由结果"""
        scenario_info = self.get_exchange_scenario(exchange_name)
        
        if not scenario_info:
            return
        
        if 'bindings' in scenario_info:
            print("   主题路由结果:")
            for routing_key, queue_name in scenario_info['bindings']:
                print(f"     {routing_key} -> {queue_name}")
        elif 'queues' in scenario_info:
            print("   直连路由结果:")
            for queue in scenario_info['queues']:
                print(f"     {queue} 收到消息")
        elif 'subscribers' in scenario_info:
            print("   扇形广播结果:")
            for subscriber in scenario_info['subscribers']:
                print(f"     {subscriber} 收到广播")
    
    def interactive_demo(self):
        """交互式演示"""
        print("\n🎯 交互式交换机模式演示")
        print("=" * 60)
        
        while True:
            print("\n请选择演示场景:")
            print("1. 直连交换机 - 系统日志分发")
            print("2. 主题交换机 - 多级日志匹配")
            print("3. 扇形交换机 - 事件广播")
            print("4. 头交换机 - 属性匹配分发")
            print("5. 复杂路由 - 多级处理链")
            print("6. 运行所有演示")
            print("7. 退出")
            
            choice = input("\n请输入选择 (1-7): ").strip()
            
            if not self.connect():
                continue
            
            try:
                if choice == '1':
                    self.setup_demo_environment()
                    self.demo_direct_exchange()
                    
                elif choice == '2':
                    self.setup_demo_environment()
                    self.demo_topic_exchange()
                    
                elif choice == '3':
                    self.setup_demo_environment()
                    self.demo_fanout_exchange()
                    
                elif choice == '4':
                    self.setup_demo_environment()
                    self.demo_headers_exchange()
                    
                elif choice == '5':
                    self.setup_demo_environment()
                    self.demo_complex_routing()
                    
                elif choice == '6':
                    self.setup_demo_environment()
                    print("\n🎬 运行完整演示")
                    self.demo_direct_exchange()
                    time.sleep(1)
                    self.demo_topic_exchange()
                    time.sleep(1)
                    self.demo_fanout_exchange()
                    time.sleep(1)
                    self.demo_headers_exchange()
                    time.sleep(1)
                    self.demo_complex_routing()
                    print("\n🎉 所有演示完成!")
                    
                elif choice == '7':
                    print("👋 退出演示")
                    break
                    
                else:
                    print("❌ 无效选择")
                    
            except Exception as e:
                print(f"❌ 演示失败: {e}")
            
            finally:
                self.close()
            
            input("\n按回车键继续...")
    
    def cleanup_demo_environment(self):
        """清理演示环境"""
        print("\n🧹 清理演示环境")
        print("=" * 40)
        
        # 清理交换机
        exchanges_to_cleanup = [
            'direct.logs', 'topic.logs', 'fanout.events',
            'headers.messages', 'complex.routing', 'route.handler'
        ]
        
        for exchange in exchanges_to_cleanup:
            try:
                self.channel.exchange_delete(exchange=exchange)
                print(f"✅ 删除交换机: {exchange}")
            except Exception as e:
                self.logger.warning(f"⚠️ 删除交换机失败 {exchange}: {e}")
        
        # 清理队列
        queues_to_cleanup = [
            'error_queue', 'warning_queue', 'info_queue',
            'critical_logs', 'app_errors', 'all_warnings', 'all_logs',
            'notification_subscriber', 'analytics_subscriber', 'monitoring_subscriber',
            'high_priority_queue', 'business_messages', 'system_messages',
            'business_handler', 'system_handler', 'user_handler'
        ]
        
        for queue in queues_to_cleanup:
            try:
                self.channel.queue_delete(queue=queue)
                print(f"✅ 删除队列: {queue}")
            except Exception as e:
                self.logger.warning(f"⚠️ 删除队列失败 {queue}: {e}")
        
        print("✅ 清理完成")
    
    def run_comprehensive_demo(self):
        """运行综合演示"""
        print("\n🎬 交换机模式综合演示")
        print("=" * 80)
        
        if not self.connect():
            return False
        
        try:
            # 设置环境
            self.setup_demo_environment()
            
            # 运行所有演示
            self.demo_direct_exchange()
            time.sleep(1)
            
            self.demo_topic_exchange()
            time.sleep(1)
            
            self.demo_fanout_exchange()
            time.sleep(1)
            
            self.demo_headers_exchange()
            time.sleep(1)
            
            self.demo_complex_routing()
            
            print("\n🎉 综合演示完成!")
            
            # 询问是否清理
            cleanup_choice = input("\n是否清理演示环境? (y/n): ").strip().lower()
            if cleanup_choice in ['y', 'yes']:
                self.cleanup_demo_environment()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 演示失败: {e}")
            return False
        
        finally:
            self.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="交换机模式演示工具")
    parser.add_argument('--host', default='localhost', help='RabbitMQ主机地址')
    parser.add_argument('--port', type=int, default=5672, help='RabbitMQ端口')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    # 创建演示器
    demo = ExchangePatternsDemo(host=args.host, port=args.port)
    
    if args.interactive:
        demo.interactive_demo()
    elif args.demo:
        demo.run_comprehensive_demo()
    else:
        # 运行完整演示
        demo.run_comprehensive_demo()