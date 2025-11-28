#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第2章：AMQP协议深入理解
实验：交换机类型对比实验

功能：
- 对比四种交换机类型（直连、主题、扇形、头交换机）的路由效果
- 验证不同绑定规则的消息分发
- 展示交换机类型的应用场景

作者：RabbitMQ学习教程
创建时间：2025年11月
"""

import pika
import json
import time
import sys
from typing import Dict, List, Any


class ExchangeComparison:
    """交换机对比实验类"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self.test_queues = []
        
    def connect(self):
        """建立连接"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()
            print(f"✅ 成功连接到 RabbitMQ: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def cleanup_exchanges(self):
        """清理现有的测试交换机"""
        exchanges = ['direct_exp', 'topic_exp', 'fanout_exp', 'headers_exp']
        
        for exchange in exchanges:
            try:
                self.channel.exchange_delete(exchange=exchange)
                print(f"🗑️ 删除交换机: {exchange}")
            except:
                pass  # 交换机不存在，忽略错误
        
        # 清理测试队列
        for queue in self.test_queues:
            try:
                self.channel.queue_delete(queue=queue)
                print(f"🗑️ 删除队列: {queue}")
            except:
                pass
    
    def setup_exchanges(self):
        """设置所有类型的交换机"""
        exchanges = {
            'direct': ('direct_exp', 'direct'),
            'topic': ('topic_exp', 'topic'), 
            'fanout': ('fanout_exp', 'fanout'),
            'headers': ('headers_exp', 'headers')
        }
        
        for name, (exchange, exch_type) in exchanges.items():
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type=exch_type,
                durable=True,
                arguments={'description': f'交换机对比实验 - {name}交换机'}
            )
            print(f"✅ 创建{exchange} ({exch_type})")
        
        return exchanges
    
    def setup_queues_and_bindings(self):
        """设置测试队列和绑定"""
        # 1. 直连交换机绑定
        self.test_queues.extend(['direct_q1', 'direct_q2'])
        
        self.channel.queue_declare(queue='direct_q1', durable=True)
        self.channel.queue_declare(queue='direct_q2', durable=True)
        
        self.channel.queue_bind('direct_exp', 'direct_q1', 'order.created')
        self.channel.queue_bind('direct_exp', 'direct_q2', 'order.updated')
        print("📋 直连交换机绑定: order.created → direct_q1, order.updated → direct_q2")
        
        # 2. 主题交换机绑定
        self.test_queues.extend(['topic_q1', 'topic_q2'])
        
        self.channel.queue_declare(queue='topic_q1', durable=True)
        self.channel.queue_declare(queue='topic_q2', durable=True)
        
        self.channel.queue_bind('topic_exp', 'topic_q1', 'order.*')
        self.channel.queue_bind('topic_exp', 'topic_q2', '*.created')
        print("📋 主题交换机绑定: order.* → topic_q1, *.created → topic_q2")
        
        # 3. 扇形交换机绑定
        self.test_queues.extend(['fanout_q1', 'fanout_q2'])
        
        self.channel.queue_declare(queue='fanout_q1', durable=True)
        self.channel.queue_declare(queue='fanout_q2', durable=True)
        
        self.channel.queue_bind('fanout_exp', 'fanout_q1', '')
        self.channel.queue_bind('fanout_exp', 'fanout_q2', '')
        print("📋 扇形交换机绑定: 广播到所有绑定队列")
        
        # 4. 头交换机绑定
        self.test_queues.extend(['headers_q1', 'headers_q2'])
        
        self.channel.queue_declare(queue='headers_q1', durable=True)
        self.channel.queue_declare(queue='headers_q2', durable=True)
        
        self.channel.queue_bind('headers_exp', 'headers_q1', '', 
                               arguments={'x-match': 'all', 'type': 'order'})
        self.channel.queue_bind('headers_exp', 'headers_q2', '',
                               arguments={'x-match': 'any', 'category': 'notification'})
        print("📋 头交换机绑定: x-match=all&type=order → headers_q1, x-match=any&category=notification → headers_q2")
    
    def send_test_messages(self):
        """发送测试消息"""
        print("\n🚀 开始发送测试消息...")
        print("=" * 80)
        
        test_scenarios = [
            # 直连交换机测试
            {
                'type': 'direct',
                'routing_key': 'order.created',
                'message': '直连交换机测试1 - 订单创建',
                'headers': None
            },
            {
                'type': 'direct',
                'routing_key': 'order.updated',
                'message': '直连交换机测试2 - 订单更新',
                'headers': None
            },
            {
                'type': 'direct',
                'routing_key': 'user.created',
                'message': '直连交换机测试3 - 用户创建（无匹配）',
                'headers': None
            },
            
            # 主题交换机测试
            {
                'type': 'topic',
                'routing_key': 'order.created',
                'message': '主题交换机测试1 - 订单创建',
                'headers': None
            },
            {
                'type': 'topic',
                'routing_key': 'order.updated',
                'message': '主题交换机测试2 - 订单更新',
                'headers': None
            },
            {
                'type': 'topic',
                'routing_key': 'user.created',
                'message': '主题交换机测试3 - 用户创建',
                'headers': None
            },
            {
                'type': 'topic',
                'routing_key': 'payment.processed',
                'message': '主题交换机测试4 - 支付处理',
                'headers': None
            },
            
            # 扇形交换机测试
            {
                'type': 'fanout',
                'routing_key': '',
                'message': '扇形交换机测试 - 系统广播消息',
                'headers': None
            },
            
            # 头交换机测试
            {
                'type': 'headers',
                'routing_key': '',
                'message': '头交换机测试1 - 订单类型',
                'headers': {'type': 'order', 'priority': 'high'}
            },
            {
                'type': 'headers',
                'routing_key': '',
                'message': '头交换机测试2 - 通知类型',
                'headers': {'category': 'notification', 'priority': 'low'}
            },
            {
                'type': 'headers',
                'routing_key': '',
                'message': '头交换机测试3 - 混合类型',
                'headers': {'type': 'order', 'category': 'notification'}
            }
        ]
        
        exchange_mapping = {
            'direct': 'direct_exp',
            'topic': 'topic_exp',
            'fanout': 'fanout_exp',
            'headers': 'headers_exp'
        }
        
        for i, scenario in enumerate(test_scenarios, 1):
            exchange = exchange_mapping[scenario['type']]
            
            # 设置消息属性
            properties = pika.BasicProperties(
                delivery_mode=2,  # 持久化
                message_id=f'{scenario["type"]}-{i}',
                timestamp=time.time(),
                headers=scenario['headers']
            )
            
            try:
                self.channel.basic_publish(
                    exchange=exchange,
                    routing_key=scenario['routing_key'],
                    body=scenario['message'],
                    properties=properties
                )
                
                header_info = f" [headers: {scenario['headers']}]" if scenario['headers'] else ""
                print(f"📤 [{scenario['type'].upper()}] 发送: '{scenario['message']}' → '{scenario['routing_key']}'{header_info}")
                
            except Exception as e:
                print(f"❌ 发送失败: {e}")
    
    def verify_routing_results(self):
        """验证消息路由结果"""
        print("\n🔍 验证消息路由结果...")
        print("=" * 80)
        
        queue_descriptions = {
            'direct_q1': '直连交换机 - 订单创建队列',
            'direct_q2': '直连交换机 - 订单更新队列',
            'topic_q1': '主题交换机 - 订单匹配队列',
            'topic_q2': '主题交换机 - 创建事件队列',
            'fanout_q1': '扇形交换机 - 订阅者1',
            'fanout_q2': '扇形交换机 - 订阅者2',
            'headers_q1': '头交换机 - 订单匹配队列',
            'headers_q2': '头交换机 - 通知匹配队列'
        }
        
        for queue in self.test_queues:
            messages = []
            
            # 获取队列中的所有消息
            try:
                while True:
                    method, properties, body = self.channel.basic_get(
                        queue=queue, 
                        auto_ack=True
                    )
                    
                    if not method:
                        break
                    
                    message_info = {
                        'body': body.decode(),
                        'message_id': properties.message_id,
                        'timestamp': time.strftime('%H:%M:%S', time.localtime(properties.timestamp))
                    }
                    messages.append(message_info)
                
                # 显示结果
                description = queue_descriptions.get(queue, queue)
                print(f"\n📋 队列: {description}")
                print(f"   队列名: {queue}")
                
                if messages:
                    for i, msg in enumerate(messages, 1):
                        print(f"   📥 消息 {i}: {msg['body']} [ID: {msg['message_id']} @ {msg['timestamp']}]")
                else:
                    print(f"   📭 队列为空")
                    
            except Exception as e:
                print(f"❌ 验证队列 {queue} 失败: {e}")
    
    def run_comparison(self):
        """运行完整的对比实验"""
        print("🚀 开始交换机类型对比实验")
        print("=" * 80)
        
        if not self.connect():
            return False
        
        try:
            # 清理环境
            self.cleanup_exchanges()
            
            # 设置交换机
            self.setup_exchanges()
            
            # 设置队列和绑定
            self.setup_queues_and_bindings()
            
            print("\n⏳ 等待交换机和队列创建完成...")
            time.sleep(1)
            
            # 发送测试消息
            self.send_test_messages()
            
            print("\n⏳ 等待消息路由完成...")
            time.sleep(2)
            
            # 验证路由结果
            self.verify_routing_results()
            
            print("\n✅ 交换机类型对比实验完成!")
            
        except Exception as e:
            print(f"❌ 实验执行失败: {e}")
            return False
        
        finally:
            self.close()
        
        return True
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("🔒 连接已关闭")


def demo_interactive_comparison():
    """交互式演示"""
    print("\n🎯 交互式交换机类型演示")
    print("=" * 50)
    
    comparison = ExchangeComparison()
    
    while True:
        print("\n请选择演示模式:")
        print("1. 自动对比实验")
        print("2. 自定义消息发送")
        print("3. 队列消息查看")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            comparison.run_comparison()
            
        elif choice == '2':
            if not comparison.connect():
                continue
                
            exchange_name = input("请输入交换机名称 (direct_exp/topic_exp/fanout_exp/headers_exp): ").strip()
            routing_key = input("请输入路由键 (头交换机可为空): ").strip()
            message = input("请输入消息内容: ").strip()
            
            if exchange_name and message:
                headers = {}
                if exchange_name == 'headers_exp':
                    print("设置头交换机属性:")
                    headers['type'] = input("type: ").strip()
                    headers['category'] = input("category: ").strip()
                    headers = {k: v for k, v in headers.items() if v}
                
                properties = pika.BasicProperties(
                    delivery_mode=2,
                    headers=headers if headers else None
                )
                
                comparison.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key=routing_key,
                    body=message,
                    properties=properties
                )
                
                print(f"✅ 消息已发送: {message}")
            else:
                print("❌ 输入信息不完整")
            
            comparison.close()
            
        elif choice == '3':
            if not comparison.connect():
                continue
                
            queue_name = input("请输入要查看的队列名称: ").strip()
            
            if queue_name:
                try:
                    method, properties, body = comparison.channel.basic_get(
                        queue=queue_name, 
                        auto_ack=True
                    )
                    
                    if method:
                        print(f"📥 消息: {body.decode()}")
                        print(f"📝 属性: Message-ID={properties.message_id}")
                    else:
                        print(f"📭 队列 {queue_name} 为空")
                        
                except Exception as e:
                    print(f"❌ 查看队列失败: {e}")
            
            comparison.close()
            
        elif choice == '4':
            print("👋 退出演示")
            break
            
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RabbitMQ交换机类型对比实验")
    parser.add_argument('--host', default='localhost', help='RabbitMQ主机地址')
    parser.add_argument('--port', type=int, default=5672, help='RabbitMQ端口')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    # 创建实验实例
    comparison = ExchangeComparison(host=args.host, port=args.port)
    
    if args.interactive:
        demo_interactive_comparison()
    else:
        # 运行自动对比实验
        comparison.run_comparison()
        
        # 询问是否进入交互模式
        choice = input("\n是否进入交互模式? (y/n): ").strip().lower()
        if choice == 'y':
            demo_interactive_comparison()