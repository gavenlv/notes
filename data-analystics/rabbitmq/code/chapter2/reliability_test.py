#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第2章：AMQP协议深入理解
实验：消息可靠性测试

功能：
- 测试消息确认机制（手动确认、自动确认）
- 测试消息持久化机制
- 测试事务处理
- 测试死信队列处理
- 测试消息过期处理

作者：RabbitMQ学习教程
创建时间：2025年11月
"""

import pika
import json
import time
import threading
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class MessageReliabilityTester:
    """消息可靠性测试器"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self.test_results = {}
        
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
            print(f"✅ 连接到 RabbitMQ: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def setup_test_queues(self):
        """设置测试队列"""
        # 创建各种测试队列
        test_queues = {
            'ack_test': {'durable': True, 'auto_delete': False},
            'transaction_test': {'durable': True, 'auto_delete': False},
            'durable_test': {'durable': True, 'auto_delete': False},
            'expiry_test': {
                'durable': True, 
                'arguments': {'x-message-ttl': 5000}  # 5秒TTL
            },
            'priority_test': {
                'durable': True,
                'arguments': {'x-max-priority': 10}
            },
            'dead_letter_test': {
                'durable': True,
                'arguments': {
                    'x-dead-letter-exchange': 'dlx',
                    'x-dead-letter-routing-key': 'dead'
                }
            }
        }
        
        # 创建死信交换机
        self.channel.exchange_declare(exchange='dlx', exchange_type='direct', durable=True)
        self.channel.queue_declare(queue='dead', durable=True)
        self.channel.queue_bind(exchange='dlx', queue='dead', routing_key='dead')
        
        # 创建测试队列
        for queue, args in test_queues.items():
            self.channel.queue_declare(queue=queue, **args)
            print(f"✅ 创建测试队列: {queue}")
        
        # 统计信息队列
        self.channel.queue_declare(queue='stats_queue', durable=True)
        self.stats_channel = self.connection.channel()
        
        print("✅ 所有测试队列创建完成")
    
    def test_message_acknowledgment(self):
        """测试消息确认机制"""
        print("\n🧪 测试1: 消息确认机制")
        print("=" * 50)
        
        test_messages = [
            "正常消息1 - 应该被确认",
            "错误消息ERROR - 应该被拒绝",
            "正常消息2 - 应该被确认",
            "失败消息FAIL - 应该被拒绝",
            "正常消息3 - 应该被确认"
        ]
        
        sent_count = 0
        ack_count = 0
        nack_count = 0
        
        # 发送测试消息
        for i, message in enumerate(test_messages):
            properties = pika.BasicProperties(
                delivery_mode=2,
                message_id=f'ack-test-{i}',
                timestamp=time.time()
            )
            
            self.channel.basic_publish(
                exchange='',
                routing_key='ack_test',
                body=message,
                properties=properties
            )
            sent_count += 1
            print(f"📤 发送: {message}")
        
        # 模拟消费者处理
        def ack_consumer():
            nonlocal ack_count, nack_count
            
            method, properties, body = self.channel.basic_get(
                queue='ack_test', 
                auto_ack=False
            )
            
            while method:
                message_body = body.decode()
                print(f"📥 消费: {message_body}")
                
                if "ERROR" in message_body or "FAIL" in message_body:
                    print("❌ 处理失败，拒绝消息")
                    self.channel.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=False
                    )
                    nack_count += 1
                else:
                    print("✅ 处理成功，确认消息")
                    self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    ack_count += 1
                
                # 获取下一条消息
                method, properties, body = self.channel.basic_get(
                    queue='ack_test', 
                    auto_ack=False
                )
        
        # 执行消费
        ack_consumer()
        
        # 记录结果
        self.test_results['acknowledgment'] = {
            'sent': sent_count,
            'acked': ack_count,
            'nacked': nack_count,
            'success_rate': ack_count / sent_count if sent_count > 0 else 0
        }
        
        print(f"📊 确认测试结果: 发送={sent_count}, 确认={ack_count}, 拒绝={nack_count}")
        print(f"   成功率: {self.test_results['acknowledgment']['success_rate']:.2%}")
    
    def test_transaction_reliability(self):
        """测试事务可靠性"""
        print("\n🧪 测试2: 事务可靠性")
        print("=" * 50)
        
        transaction_scenarios = [
            {
                'name': '事务成功',
                'messages': ['事务消息1', '事务消息2', '事务消息3'],
                'commit': True
            },
            {
                'name': '事务失败回滚',
                'messages': ['回滚消息1', '回滚消息2', '回滚消息3'],
                'commit': False,
                'simulate_error': True
            }
        ]
        
        for scenario in transaction_scenarios:
            print(f"\n📝 执行 {scenario['name']}")
            
            try:
                # 开始事务
                self.channel.tx_select()
                
                for i, message in enumerate(scenario['messages']):
                    self.channel.basic_publish(
                        exchange='',
                        routing_key='transaction_test',
                        body=message,
                        properties=pika.BasicProperties(
                            message_id=f'tx-{scenario["name"]}-{i}'
                        )
                    )
                    print(f"📤 事务发布: {message}")
                
                if scenario.get('simulate_error', False):
                    print("🔄 模拟错误，执行回滚")
                    raise Exception("模拟事务处理错误")
                
                if scenario['commit']:
                    self.channel.tx_commit()
                    print("✅ 事务提交成功")
                else:
                    self.channel.tx_rollback()
                    print("🔄 事务已回滚")
                    
            except Exception as e:
                print(f"❌ 事务错误: {e}")
                self.channel.tx_rollback()
                print("🔄 事务已回滚")
    
    def test_message_durability(self):
        """测试消息持久化"""
        print("\n🧪 测试3: 消息持久化")
        print("=" * 50)
        
        durable_messages = [f"持久化消息{i}" for i in range(10)]
        
        # 发送持久化消息
        for i, message in enumerate(durable_messages):
            self.channel.basic_publish(
                exchange='',
                routing_key='durable_test',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                    message_id=f'durable-{i}',
                    timestamp=time.time()
                )
            )
            print(f"📤 发送持久化消息: {message}")
        
        # 验证消息持久化
        message_count = 0
        durable_count = 0
        
        while True:
            method, properties, body = self.channel.basic_get(
                queue='durable_test',
                auto_ack=True
            )
            
            if not method:
                break
                
            message_count += 1
            if properties.delivery_mode == 2:
                durable_count += 1
            
            print(f"📥 验证消息: {body.decode()} (持久化: {properties.delivery_mode == 2})")
        
        self.test_results['durability'] = {
            'total_sent': len(durable_messages),
            'total_received': message_count,
            'durable_count': durable_count,
            'durability_rate': durable_count / len(durable_messages) if durable_messages else 0
        }
        
        print(f"📊 持久化测试: 发送={len(durable_messages)}, 接收={message_count}, 持久化={durable_count}")
        print(f"   持久化率: {self.test_results['durability']['durability_rate']:.2%}")
    
    def test_message_expiry(self):
        """测试消息过期"""
        print("\n🧪 测试4: 消息过期")
        print("=" * 50)
        
        # 发送不同过期时间的消息
        expiry_messages = [
            {'message': '立即过期消息', 'expiry': '1000'},    # 1秒过期
            {'message': '3秒过期消息', 'expiry': '3000'},     # 3秒过期
            {'message': '永久消息', 'expiry': None}          # 不过期
        ]
        
        for i, msg_data in enumerate(expiry_messages):
            properties = pika.BasicProperties(
                delivery_mode=2,
                message_id=f'expiry-{i}',
                expiration=msg_data['expiry']  # 设置过期时间
            )
            
            self.channel.basic_publish(
                exchange='',
                routing_key='expiry_test',
                body=msg_data['message'],
                properties=properties
            )
            
            expiry_str = msg_data['expiry'] if msg_data['expiry'] else '不过期'
            print(f"📤 发送消息 (过期: {expiry_str}ms): {msg_data['message']}")
        
        # 等待过期检查
        print("⏳ 等待过期消息被处理...")
        time.sleep(6)  # 等待所有过期消息被删除
        
        # 检查剩余消息
        remaining_messages = 0
        while True:
            method, properties, body = self.channel.basic_get(
                queue='expiry_test',
                auto_ack=True
            )
            
            if not method:
                break
                
            remaining_messages += 1
            print(f"📥 剩余消息: {body.decode()}")
        
        self.test_results['expiry'] = {
            'total_sent': len(expiry_messages),
            'remaining': remaining_messages,
            'expired': len(expiry_messages) - remaining_messages
        }
        
        print(f"📊 过期测试: 发送={len(expiry_messages)}, 剩余={remaining_messages}, 过期={len(expiry_messages) - remaining_messages}")
    
    def test_message_priority(self):
        """测试消息优先级"""
        print("\n🧪 测试5: 消息优先级")
        print("=" * 50)
        
        # 发送不同优先级的消息
        priority_messages = [
            {'message': '低优先级消息1', 'priority': 1},
            {'message': '低优先级消息2', 'priority': 2},
            {'message': '中优先级消息1', 'priority': 5},
            {'message': '高优先级消息1', 'priority': 9},
            {'message': '高优先级消息2', 'priority': 8},
        ]
        
        for i, msg_data in enumerate(priority_messages):
            properties = pika.BasicProperties(
                delivery_mode=2,
                message_id=f'priority-{i}',
                priority=msg_data['priority']
            )
            
            self.channel.basic_publish(
                exchange='',
                routing_key='priority_test',
                body=msg_data['message'],
                properties=properties
            )
            
            print(f"📤 发送消息 [优先级 {msg_data['priority']}]: {msg_data['message']}")
        
        # 消费消息，查看优先级顺序
        received_priorities = []
        received_messages = []
        
        while True:
            method, properties, body = self.channel.basic_get(
                queue='priority_test',
                auto_ack=True
            )
            
            if not method:
                break
                
            received_priorities.append(properties.priority)
            received_messages.append(body.decode())
            print(f"📥 收到消息 [优先级 {properties.priority}]: {body.decode()}")
        
        # 检查是否按优先级降序消费
        is_priority_correct = received_priorities == sorted(received_priorities, reverse=True)
        
        self.test_results['priority'] = {
            'sent': priority_messages,
            'received_priorities': received_priorities,
            'priority_order_correct': is_priority_correct
        }
        
        print(f"📊 优先级测试: 消费顺序正确 = {is_priority_correct}")
        print(f"   实际消费优先级: {received_priorities}")
        print(f"   期望消费优先级: {sorted(received_priorities, reverse=True)}")
    
    def test_dead_letter_queue(self):
        """测试死信队列"""
        print("\n🧪 测试6: 死信队列")
        print("=" * 50)
        
        # 发送会进入死信队列的消息
        dlx_messages = [
            {'message': '正常处理消息', 'should_fail': False},
            {'message': '处理失败消息', 'should_fail': True},
            {'message': '另一条失败消息', 'should_fail': True},
            {'message': '另一条正常消息', 'should_fail': False}
        ]
        
        for i, msg_data in enumerate(dlx_messages):
            properties = pika.BasicProperties(
                delivery_mode=2,
                message_id=f'dlx-{i}'
            )
            
            self.channel.basic_publish(
                exchange='',
                routing_key='dead_letter_test',
                body=msg_data['message'],
                properties=properties
            )
            
            print(f"📤 发送消息: {msg_data['message']} {'[预期失败]' if msg_data['should_fail'] else ''}")
        
        # 模拟消费者，部分消息处理失败
        def dlx_consumer():
            for msg_data in dlx_messages:
                method, properties, body = self.channel.basic_get(
                    queue='dead_letter_test',
                    auto_ack=False
                )
                
                if method:
                    print(f"📥 处理消息: {body.decode()}")
                    
                    if msg_data['should_fail']:
                        print("❌ 模拟处理失败，进入死信队列")
                        self.channel.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=False
                        )
                    else:
                        print("✅ 处理成功")
                        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        
        dlx_consumer()
        
        # 检查死信队列中的消息
        dlx_message_count = 0
        while True:
            method, properties, body = self.channel.basic_get(
                queue='dead',
                auto_ack=True
            )
            
            if not method:
                break
                
            dlx_message_count += 1
            print(f"📥 死信消息: {body.decode()}")
        
        self.test_results['dead_letter'] = {
            'sent': len(dlx_messages),
            'failed': sum(1 for msg in dlx_messages if msg['should_fail']),
            'dead_letter_count': dlx_message_count
        }
        
        print(f"📊 死信测试: 发送={len(dlx_messages)}, 失败={sum(1 for msg in dlx_messages if msg['should_fail'])}, 死信={dlx_message_count}")
    
    def run_all_tests(self):
        """运行所有可靠性测试"""
        print("🚀 开始消息可靠性测试")
        print("=" * 80)
        
        if not self.connect():
            return False
        
        try:
            # 设置测试环境
            self.setup_test_queues()
            
            # 运行各种测试
            self.test_message_acknowledgment()
            self.test_transaction_reliability()
            self.test_message_durability()
            self.test_message_expiry()
            self.test_message_priority()
            self.test_dead_letter_queue()
            
            # 生成测试报告
            self.generate_test_report()
            
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            return False
        
        finally:
            self.close()
        
        return True
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n📊 可靠性测试报告")
        print("=" * 80)
        
        # 确认测试报告
        if 'acknowledgment' in self.test_results:
            ack = self.test_results['acknowledgment']
            print(f"\n✅ 消息确认测试:")
            print(f"   发送消息数: {ack['sent']}")
            print(f"   成功确认: {ack['acked']}")
            print(f"   拒绝确认: {ack['nacked']}")
            print(f"   成功率: {ack['success_rate']:.2%}")
        
        # 持久化测试报告
        if 'durability' in self.test_results:
            dur = self.test_results['durability']
            print(f"\n💾 消息持久化测试:")
            print(f"   发送消息数: {dur['total_sent']}")
            print(f"   接收消息数: {dur['total_received']}")
            print(f"   持久化消息: {dur['durable_count']}")
            print(f"   持久化率: {dur['durability_rate']:.2%}")
        
        # 过期测试报告
        if 'expiry' in self.test_results:
            exp = self.test_results['expiry']
            print(f"\n⏰ 消息过期测试:")
            print(f"   发送消息数: {exp['total_sent']}")
            print(f"   剩余消息: {exp['remaining']}")
            print(f"   过期消息: {exp['expired']}")
        
        # 优先级测试报告
        if 'priority' in self.test_results:
            pri = self.test_results['priority']
            print(f"\n🔢 消息优先级测试:")
            print(f"   优先级顺序正确: {'是' if pri['priority_order_correct'] else '否'}")
            print(f"   消费优先级顺序: {pri['received_priorities']}")
        
        # 死信队列测试报告
        if 'dead_letter' in self.test_results:
            dlx = self.test_results['dead_letter']
            print(f"\n💀 死信队列测试:")
            print(f"   发送消息数: {dlx['sent']}")
            print(f"   处理失败数: {dlx['failed']}")
            print(f"   死信消息数: {dlx['dead_letter_count']}")
        
        print(f"\n🎉 可靠性测试完成!")
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("🔒 连接已关闭")


def interactive_reliability_test():
    """交互式可靠性测试"""
    print("\n🎯 交互式消息可靠性测试")
    print("=" * 60)
    
    tester = MessageReliabilityTester()
    
    while True:
        print("\n请选择测试类型:")
        print("1. 消息确认测试")
        print("2. 事务测试")
        print("3. 持久化测试")
        print("4. 过期测试")
        print("5. 优先级测试")
        print("6. 死信队列测试")
        print("7. 运行所有测试")
        print("8. 退出")
        
        choice = input("\n请输入选择 (1-8): ").strip()
        
        if not tester.connect():
            continue
        
        try:
            tester.setup_test_queues()
            
            if choice == '1':
                tester.test_message_acknowledgment()
            elif choice == '2':
                tester.test_transaction_reliability()
            elif choice == '3':
                tester.test_message_durability()
            elif choice == '4':
                tester.test_message_expiry()
            elif choice == '5':
                tester.test_message_priority()
            elif choice == '6':
                tester.test_dead_letter_queue()
            elif choice == '7':
                tester.run_all_tests()
            elif choice == '8':
                print("👋 退出测试")
                break
            else:
                print("❌ 无效选择")
        
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        finally:
            tester.close()
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RabbitMQ消息可靠性测试")
    parser.add_argument('--host', default='localhost', help='RabbitMQ主机地址')
    parser.add_argument('--port', type=int, default=5672, help='RabbitMQ端口')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    # 创建测试实例
    tester = MessageReliabilityTester(host=args.host, port=args.port)
    
    if args.interactive:
        interactive_reliability_test()
    else:
        # 运行完整测试
        tester.run_all_tests()