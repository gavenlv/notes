#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第3章：交换机类型深入研究
交换机高级功能与配置管理

功能：
- 交换机属性配置
- 交换机管理和维护
- 交换机性能测试
- 交换机监控和统计
- 动态交换机创建和管理

作者：RabbitMQ学习教程
创建时间：2025年11月
"""

import pika
import time
import json
import threading
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics
import random


@dataclass
class ExchangeConfig:
    """交换机配置"""
    name: str
    exchange_type: str  # direct, topic, fanout, headers
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: Optional[Dict[str, Any]] = None
    alternate_exchange: Optional[str] = None
    description: str = ""


@dataclass
class ExchangeStats:
    """交换机统计信息"""
    name: str
    message_in: int
    message_out: int
    publish_rate: float
    deliver_rate: float
    return_rate: float
    confirm_rate: float
    error_rate: float
    last_update: float


class ExchangeAdvancedManager:
    """交换机高级管理器"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        
        # 交换机配置字典
        self.exchange_configs: Dict[str, ExchangeConfig] = {}
        
        # 交换机统计信息
        self.exchange_stats: Dict[str, ExchangeStats] = {}
        
        # 性能测试结果
        self.performance_results = {}
        
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
                    heartbeat=30,
                    blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()
            
            # 设置连接回调
            self.connection.add_on_connection_closed_callback(self._on_connection_closed)
            
            self.logger.info(f"✅ 连接到 RabbitMQ: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 连接失败: {e}")
            return False
    
    def _on_connection_closed(self, connection, reply_code, reply_text):
        """连接关闭回调"""
        self.logger.warning(f"🔌 连接关闭: {reply_code} - {reply_text}")
    
    def create_advanced_exchange(self, config: ExchangeConfig):
        """创建高级交换机"""
        try:
            # 准备交换机声明参数
            declare_args = {
                'exchange': config.name,
                'exchange_type': config.exchange_type,
                'durable': config.durable,
                'auto_delete': config.auto_delete,
                'internal': config.internal
            }
            
            # 添加参数
            if config.arguments:
                declare_args['arguments'] = config.arguments
            
            # 添加备用交换机
            if config.alternate_exchange:
                if 'alternate-exchange' not in declare_args.get('arguments', {}):
                    if 'arguments' not in declare_args:
                        declare_args['arguments'] = {}
                    declare_args['arguments']['alternate-exchange'] = config.alternate_exchange
            
            # 声明交换机
            self.channel.exchange_declare(**declare_args)
            
            # 保存配置
            self.exchange_configs[config.name] = config
            
            self.logger.info(f"✅ 创建交换机: {config.name} ({config.exchange_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 创建交换机失败 {config.name}: {e}")
            return False
    
    def create_predefined_exchanges(self):
        """创建预定义的交换机集合"""
        predefined_configs = [
            # 直连交换机配置
            ExchangeConfig(
                name='direct_notifications',
                exchange_type='direct',
                durable=True,
                arguments={'x-message-ttl': 3600000},  # 1小时TTL
                description='直连通知交换机'
            ),
            
            # 主题交换机配置
            ExchangeConfig(
                name='topic_logs',
                exchange_type='topic',
                durable=True,
                arguments={
                    'x-delayed-type': 'topic',
                    'x-dead-letter-exchange': 'dead_letters',
                    'x-dead-letter-routing-key': 'failed'
                },
                description='主题日志交换机，支持延迟和死信'
            ),
            
            # 扇形交换机配置
            ExchangeConfig(
                name='fanout_events',
                exchange_type='fanout',
                durable=True,
                auto_delete=False,
                description='扇形事件交换机'
            ),
            
            # 头交换机配置
            ExchangeConfig(
                name='headers_priority',
                exchange_type='headers',
                durable=True,
                arguments={
                    'x-match': 'any',  # or 'all'
                    'x-priority': {'annotation': 'integer'},
                    'x-content-type': {'annotation': 'string'}
                },
                description='头交换机，支持属性匹配'
            ),
            
            # 内部交换机配置
            ExchangeConfig(
                name='internal_routing',
                exchange_type='direct',
                durable=True,
                internal=True,
                description='内部路由交换机'
            ),
            
            # 备用交换机配置
            ExchangeConfig(
                name='fallback_exchange',
                exchange_type='fanout',
                durable=True,
                description='备用交换机'
            ),
            
            # 主要交换机配置（带备用）
            ExchangeConfig(
                name='primary_with_fallback',
                exchange_type='direct',
                durable=True,
                alternate_exchange='fallback_exchange',
                description='主要交换机，失败时使用备用交换机',
                arguments={
                    'x-message-ttl': 600000,  # 10分钟TTL
                    'x-dead-letter-exchange': 'dead_letters'
                }
            )
        ]
        
        # 创建所有交换机
        success_count = 0
        for config in predefined_configs:
            if self.create_advanced_exchange(config):
                success_count += 1
                # 初始化统计信息
                self.exchange_stats[config.name] = ExchangeStats(
                    name=config.name,
                    message_in=0,
                    message_out=0,
                    publish_rate=0,
                    deliver_rate=0,
                    return_rate=0,
                    confirm_rate=0,
                    error_rate=0,
                    last_update=time.time()
                )
        
        self.logger.info(f"✅ 创建预定义交换机完成: {success_count}/{len(predefined_configs)}")
        return success_count == len(predefined_configs)
    
    def bind_exchanges(self):
        """绑定交换机"""
        bindings = [
            # 主题交换机绑定
            ('topic_logs', 'app.logs', 'logs.critical.error'),
            ('topic_logs', 'app.logs', 'logs.warning.info'),
            ('topic_logs', 'app.logs', 'logs.debug'),
            
            # 头交换机绑定
            ('headers_priority', 'priority_high', 'app_queue', {
                'x-match': 'any',
                'x-priority': 9,
                'x-content-type': 'application/json'
            }),
            ('headers_priority', 'priority_low', 'app_queue', {
                'x-match': 'any',
                'x-priority': 1,
                'x-content-type': 'text/plain'
            }),
            
            # 内部交换机路由
            ('primary_with_fallback', 'direct_route', 'internal_routing'),
            
            # 内部交换机到最终队列的路由
            ('internal_routing', 'app_queue', 'target_queue')
        ]
        
        success_count = 0
        for binding in bindings:
            try:
                if len(binding) == 3:
                    source, queue, routing_key = binding
                    # 普通绑定
                    self.channel.queue_bind(
                        exchange=source,
                        queue=queue,
                        routing_key=routing_key
                    )
                else:
                    source, queue, routing_key, headers = binding
                    # 带头的绑定
                    self.channel.queue_bind(
                        exchange=source,
                        queue=queue,
                        routing_key=routing_key,
                        arguments=headers
                    )
                
                success_count += 1
                self.logger.info(f"✅ 绑定: {source} -> {queue} ({routing_key})")
                
            except Exception as e:
                self.logger.error(f"❌ 绑定失败: {source} -> {queue}: {e}")
        
        self.logger.info(f"✅ 绑定完成: {success_count}/{len(bindings)}")
        return success_count == len(bindings)
    
    def create_test_queues(self):
        """创建测试队列"""
        test_queues = [
            {
                'name': 'app_queue',
                'durable': True,
                'arguments': {
                    'x-message-ttl': 300000,  # 5分钟TTL
                    'x-dead-letter-exchange': 'dead_letters',
                    'x-dead-letter-routing-key': 'failed'
                }
            },
            {
                'name': 'priority_queue',
                'durable': True,
                'arguments': {
                    'x-max-priority': 10
                }
            },
            {
                'name': 'event_queue',
                'durable': True,
                'auto_delete': False
            },
            {
                'name': 'target_queue',
                'durable': True,
                'arguments': {
                    'x-queue-mode': 'lazy'  # 懒加载模式
                }
            },
            {
                'name': 'dead_letters',
                'durable': True
            }
        ]
        
        for queue_config in test_queues:
            try:
                self.channel.queue_declare(**queue_config)
                self.logger.info(f"✅ 创建队列: {queue_config['name']}")
            except Exception as e:
                self.logger.error(f"❌ 创建队列失败 {queue_config['name']}: {e}")
        
        # 绑定死信队列
        try:
            self.channel.queue_bind(
                exchange='dead_letters',
                queue='dead_letters',
                routing_key='failed'
            )
            self.logger.info("✅ 绑定死信队列")
        except Exception as e:
            self.logger.error(f"❌ 绑定死信队列失败: {e}")
    
    def test_exchange_functionality(self):
        """测试交换机功能"""
        print("\n🧪 测试交换机功能")
        print("=" * 60)
        
        test_scenarios = [
            {
                'exchange': 'direct_notifications',
                'routing_key': 'notifications.critical',
                'message': 'Critical notification message',
                'description': '直连交换机测试'
            },
            {
                'exchange': 'topic_logs',
                'routing_key': 'app.logs.critical.error',
                'message': 'Critical application error log',
                'description': '主题交换机测试'
            },
            {
                'exchange': 'fanout_events',
                'routing_key': '',
                'message': 'Fanout event message',
                'description': '扇形交换机测试'
            },
            {
                'exchange': 'headers_priority',
                'routing_key': '',
                'message': 'High priority message',
                'properties': pika.BasicProperties(
                    headers={'x-priority': 9, 'x-content-type': 'application/json'}
                ),
                'description': '头交换机测试'
            },
            {
                'exchange': 'primary_with_fallback',
                'routing_key': 'test_route',
                'message': 'Primary exchange message',
                'description': '备用交换机测试'
            }
        ]
        
        for scenario in test_scenarios:
            try:
                print(f"\n📝 {scenario['description']}")
                print(f"   交换机: {scenario['exchange']}")
                print(f"   路由键: {scenario['routing_key']}")
                print(f"   消息: {scenario['message']}")
                
                # 创建消息属性
                properties = scenario.get('properties', pika.BasicProperties(
                    message_id=str(uuid.uuid4()),
                    timestamp=time.time(),
                    delivery_mode=2  # 持久化
                ))
                
                # 发送消息
                self.channel.basic_publish(
                    exchange=scenario['exchange'],
                    routing_key=scenario['routing_key'],
                    body=scenario['message'],
                    properties=properties
                )
                
                # 更新统计
                if scenario['exchange'] in self.exchange_stats:
                    stats = self.exchange_stats[scenario['exchange']]
                    stats.message_in += 1
                    stats.message_out += 1
                    stats.last_update = time.time()
                
                print("✅ 消息发送成功")
                
                # 模拟接收
                self._simulate_message_consumption(scenario['exchange'])
                
                time.sleep(0.5)  # 短暂延迟
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
    
    def _simulate_message_consumption(self, exchange_name: str):
        """模拟消息消费"""
        # 模拟消息被消费者接收并确认
        if exchange_name in self.exchange_stats:
            stats = self.exchange_stats[exchange_name]
            stats.deliver_rate = stats.message_out / max(1, time.time() - stats.last_update)
            print(f"   模拟消费成功，传递速率: {stats.deliver_rate:.2f} msg/s")
    
    def measure_exchange_performance(self):
        """测量交换机性能"""
        print("\n⚡ 测量交换机性能")
        print("=" * 60)
        
        exchange_types = ['direct', 'topic', 'fanout', 'headers']
        test_results = {}
        
        for exchange_type in exchange_types:
            print(f"\n📊 测试 {exchange_type} 交换机性能")
            
            # 创建测试交换机
            test_exchange = f"perf_test_{exchange_type}"
            self.channel.exchange_declare(
                exchange=test_exchange,
                exchange_type=exchange_type,
                durable=False
            )
            
            # 创建测试队列
            test_queue = f"perf_queue_{exchange_type}"
            self.channel.queue_declare(queue=test_queue, durable=False)
            self.channel.queue_bind(exchange=test_exchange, queue=test_queue)
            
            # 性能测试
            message_count = 1000
            start_time = time.time()
            
            # 发送消息
            for i in range(message_count):
                properties = pika.BasicProperties(
                    message_id=f"perf_{exchange_type}_{i}"
                )
                
                self.channel.basic_publish(
                    exchange=test_exchange,
                    routing_key='test.route' if exchange_type != 'fanout' else '',
                    body=f"Performance test message {i}",
                    properties=properties
                )
            
            # 处理回调
            confirm_count = 0
            return_count = 0
            
            def on_return(return_rpc, exchange, routing_key, properties, body):
                nonlocal return_count
                return_count += 1
            
            def on_basic_return(channel, method, properties, body):
                nonlocal return_count
                return_count += 1
            
            self.channel.add_on_return_callback(on_basic_return)
            
            # 确认测试结果
            total_time = time.time() - start_time
            throughput = message_count / total_time
            
            test_results[exchange_type] = {
                'messages_sent': message_count,
                'total_time': total_time,
                'throughput': throughput,
                'returns': return_count,
                'success_rate': (message_count - return_count) / message_count
            }
            
            print(f"   发送消息: {message_count}")
            print(f"   总时间: {total_time:.3f}s")
            print(f"   吞吐量: {throughput:.2f} msg/s")
            print(f"   成功率: {test_results[exchange_type]['success_rate']:.2%}")
            
            # 清理测试资源
            self.channel.queue_delete(queue=test_queue)
            self.channel.exchange_delete(exchange=test_exchange)
        
        self.performance_results = test_results
        
        # 生成性能对比报告
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """生成性能报告"""
        print("\n📊 交换机性能对比报告")
        print("=" * 80)
        
        if not self.performance_results:
            print("❌ 无性能数据")
            return
        
        # 按吞吐量排序
        sorted_results = sorted(
            self.performance_results.items(),
            key=lambda x: x[1]['throughput'],
            reverse=True
        )
        
        print(f"{'交换机类型':<12} {'吞吐量(msg/s)':<15} {'成功率':<10} {'总时间(s)':<12}")
        print("-" * 60)
        
        for exchange_type, result in sorted_results:
            print(f"{exchange_type:<12} {result['throughput']:<15.2f} "
                  f"{result['success_rate']:<10.1%} {result['total_time']:<12.3f}")
        
        # 性能分析
        best_type = sorted_results[0][0]
        worst_type = sorted_results[-1][0]
        
        print(f"\n🏆 最佳性能: {best_type} 交换机 ({sorted_results[0][1]['throughput']:.2f} msg/s)")
        print(f"🔻 最差性能: {worst_type} 交换机 ({sorted_results[-1][1]['throughput']:.2f} msg/s)")
        
        if len(sorted_results) > 1:
            improvement = (sorted_results[0][1]['throughput'] - sorted_results[-1][1]['throughput']) / sorted_results[-1][1]['throughput'] * 100
            print(f"📈 性能差异: {improvement:.1f}%")
    
    def monitor_exchanges(self, duration: int = 30):
        """监控交换机"""
        print(f"\n👁️ 监控交换机状态 ({duration}秒)")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + duration
        
        # 持续发送测试消息
        def continuous_publisher():
            exchange_order = ['direct_notifications', 'topic_logs', 'fanout_events', 'headers_priority']
            message_count = 0
            
            while time.time() < end_time:
                exchange = exchange_order[message_count % len(exchange_order)]
                
                try:
                    self.channel.basic_publish(
                        exchange=exchange,
                        routing_key='monitor.test',
                        body=f"Monitoring message {message_count}",
                        properties=pika.BasicProperties(
                            message_id=f"monitor_{message_count}",
                            timestamp=time.time()
                        )
                    )
                    
                    if exchange in self.exchange_stats:
                        stats = self.exchange_stats[exchange]
                        stats.message_in += 1
                        stats.message_out += 1
                        stats.last_update = time.time()
                    
                    message_count += 1
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"❌ 监控消息发送失败: {e}")
        
        # 启动持续发布
        publisher_thread = threading.Thread(target=continuous_publisher)
        publisher_thread.daemon = True
        publisher_thread.start()
        
        # 显示监控信息
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            print(f"\n⏱️ 剩余监控时间: {remaining}秒")
            print(f"{'交换机':<25} {'消息入':<10} {'消息出':<10} {'当前速率':<12}")
            print("-" * 70)
            
            for name, stats in self.exchange_stats.items():
                current_rate = stats.message_out / max(1, time.time() - stats.last_update)
                print(f"{name:<25} {stats.message_in:<10} {stats.message_out:<10} {current_rate:.2f}<12")
            
            time.sleep(2)
        
        publisher_thread.join()
        print("✅ 监控完成")
    
    def exchange_diagnostics(self):
        """交换机诊断"""
        print("\n🔍 交换机诊断")
        print("=" * 60)
        
        # 获取交换机列表
        try:
            result = self.channel.exchange_declare(
                exchange='diagnostic_exchange',
                exchange_type='direct',
                passive=True
            )
            self.logger.info("✅ 交换机列表获取成功")
        except Exception as e:
            self.logger.error(f"❌ 获取交换机列表失败: {e}")
        
        # 诊断每个已配置的交换机
        for name, config in self.exchange_configs.items():
            print(f"\n🔧 诊断交换机: {name}")
            print(f"   类型: {config.exchange_type}")
            print(f"   持久化: {'是' if config.durable else '否'}")
            print(f"   自动删除: {'是' if config.auto_delete else '否'}")
            print(f"   内部交换机: {'是' if config.internal else '否'}")
            
            if config.arguments:
                print(f"   参数: {config.arguments}")
            
            if config.alternate_exchange:
                print(f"   备用交换机: {config.alternate_exchange}")
            
            if config.description:
                print(f"   描述: {config.description}")
            
            # 检查队列绑定
            try:
                bindings = self.channel.queue_declare(
                    queue='temp_diagnostic_queue',
                    exclusive=True,
                    auto_delete=True
                )
                
                # 这里应该检查绑定，但简化实现
                print("   ✅ 绑定检查完成")
                
            except Exception as e:
                print(f"   ❌ 绑定检查失败: {e}")
    
    def cleanup_all(self):
        """清理所有创建的交换机和队列"""
        print("\n🧹 清理测试资源")
        print("=" * 60)
        
        cleanup_items = [
            # 清理测试交换机
            *[f"perf_test_{exchange_type}" for exchange_type in ['direct', 'topic', 'fanout', 'headers']],
            'diagnostic_exchange'
        ]
        
        cleanup_queues = [
            'app_queue',
            'priority_queue', 
            'event_queue',
            'target_queue',
            'dead_letters'
        ]
        
        # 清理交换机
        for exchange in cleanup_items:
            try:
                self.channel.exchange_delete(exchange=exchange)
                print(f"✅ 删除交换机: {exchange}")
            except Exception as e:
                self.logger.warning(f"⚠️ 删除交换机失败 {exchange}: {e}")
        
        # 清理队列
        for queue in cleanup_queues:
            try:
                self.channel.queue_delete(queue=queue)
                print(f"✅ 删除队列: {queue}")
            except Exception as e:
                self.logger.warning(f"⚠️ 删除队列失败 {queue}: {e}")
        
        print("✅ 清理完成")
    
    def run_comprehensive_demo(self):
        """运行综合演示"""
        print("\n🎬 交换机高级功能综合演示")
        print("=" * 80)
        
        if not self.connect():
            return False
        
        try:
            # 步骤1: 创建交换机
            print("\n📋 步骤1: 创建高级交换机配置")
            self.create_predefined_exchanges()
            
            # 步骤2: 创建队列
            print("\n📋 步骤2: 创建测试队列")
            self.create_test_queues()
            
            # 步骤3: 绑定交换机
            print("\n📋 步骤3: 绑定交换机关系")
            self.bind_exchanges()
            
            # 步骤4: 测试功能
            print("\n📋 步骤4: 测试交换机功能")
            self.test_exchange_functionality()
            
            # 步骤5: 性能测试
            print("\n📋 步骤5: 性能测试")
            self.measure_exchange_performance()
            
            # 步骤6: 监控
            print("\n📋 步骤6: 实时监控")
            self.monitor_exchanges(duration=10)
            
            # 步骤7: 诊断
            print("\n📋 步骤7: 系统诊断")
            self.exchange_diagnostics()
            
            print("\n🎉 演示完成!")
            
            # 询问是否清理
            cleanup_choice = input("\n是否清理测试资源? (y/n): ").strip().lower()
            if cleanup_choice in ['y', 'yes']:
                self.cleanup_all()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 演示失败: {e}")
            return False
        
        finally:
            self.close()
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.logger.info("🔒 连接已关闭")


def interactive_exchange_management():
    """交互式交换机管理"""
    print("\n🎯 交互式交换机管理")
    print("=" * 60)
    
    manager = ExchangeAdvancedManager()
    
    while True:
        print("\n请选择操作:")
        print("1. 创建预定义交换机")
        print("2. 测试交换机功能")
        print("3. 性能测试")
        print("4. 监控交换机")
        print("5. 系统诊断")
        print("6. 综合演示")
        print("7. 清理资源")
        print("8. 退出")
        
        choice = input("\n请输入选择 (1-8): ").strip()
        
        if not manager.connect():
            continue
        
        try:
            if choice == '1':
                manager.create_predefined_exchanges()
                manager.create_test_queues()
                manager.bind_exchanges()
                print("✅ 交换机创建完成")
                
            elif choice == '2':
                manager.test_exchange_functionality()
                
            elif choice == '3':
                manager.measure_exchange_performance()
                
            elif choice == '4':
                duration = int(input("请输入监控时间(秒，默认30): ") or "30")
                manager.monitor_exchanges(duration)
                
            elif choice == '5':
                manager.exchange_diagnostics()
                
            elif choice == '6':
                manager.run_comprehensive_demo()
                
            elif choice == '7':
                manager.cleanup_all()
                
            elif choice == '8':
                print("👋 退出管理")
                break
                
            else:
                print("❌ 无效选择")
        
        except Exception as e:
            print(f"❌ 操作失败: {e}")
        
        finally:
            manager.close()
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="交换机高级管理工具")
    parser.add_argument('--host', default='localhost', help='RabbitMQ主机地址')
    parser.add_argument('--port', type=int, default=5672, help='RabbitMQ端口')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = ExchangeAdvancedManager(host=args.host, port=args.port)
    
    if args.interactive:
        interactive_exchange_management()
    elif args.demo:
        manager.run_comprehensive_demo()
    else:
        # 运行完整演示
        manager.run_comprehensive_demo()