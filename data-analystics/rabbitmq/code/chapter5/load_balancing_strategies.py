#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第5章：队列管理与负载均衡 - 负载均衡策略演示
演示多种负载均衡策略：轮询、公平分发、优先级、权重等
"""

import pika
import time
import json
import threading
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue


@dataclass
class LoadBalanceConfig:
    """负载均衡配置"""
    name: str
    strategy: str  # 'round_robin', 'fair_distribution', 'priority', 'weighted'
    prefetch_count: int = 1
    consumer_count: int = 3
    priority_levels: Optional[Dict[int, str]] = None
    weights: Optional[Dict[str, int]] = None


class ConsumerStats:
    """消费者统计"""
    def __init__(self, consumer_id: str):
        self.consumer_id = consumer_id
        self.messages_processed = 0
        self.processing_time = 0.0
        self.errors = 0
        self.start_time = time.time()
        self.message_history = []
    
    def add_message(self, processing_time: float, message_id: str = None):
        """添加消息处理记录"""
        self.messages_processed += 1
        self.processing_time += processing_time
        
        if message_id:
            self.message_history.append({
                'message_id': message_id,
                'processing_time': processing_time,
                'timestamp': time.time()
            })
    
    def add_error(self):
        """添加错误记录"""
        self.errors += 1
    
    def get_throughput(self) -> float:
        """获取吞吐量"""
        duration = time.time() - self.start_time
        return self.messages_processed / duration if duration > 0 else 0.0
    
    def get_avg_processing_time(self) -> float:
        """获取平均处理时间"""
        return (self.processing_time / self.messages_processed 
                if self.messages_processed > 0 else 0.0)


class LoadBalancingDemo:
    """负载均衡演示类"""
    
    def __init__(self, connection_params=None):
        """初始化"""
        self.connection_params = connection_params or pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=pika.PlainCredentials('guest', 'guest')
        )
        self.connection = None
        self.channel = None
        self.consumers = {}
        self.consumer_stats = {}
        self.exchange_name = 'load_balance_exchange'
        
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
    
    def connect(self):
        """连接RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            
            # 声明交换机
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            print("✅ 成功连接到RabbitMQ")
        except Exception as e:
            print(f"❌ 连接RabbitMQ失败: {e}")
            raise
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 已断开RabbitMQ连接")
    
    def setup_round_robin_queue(self, queue_name: str) -> str:
        """设置轮询分发队列"""
        try:
            # 创建队列
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # 绑定到交换机
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=f'rr.{queue_name}'
            )
            
            print(f"✅ 轮询队列设置完成: {queue_name}")
            return queue_name
            
        except Exception as e:
            print(f"❌ 设置轮询队列失败: {e}")
            raise
    
    def setup_fair_distribution_queue(self, queue_name: str) -> str:
        """设置公平分发队列"""
        try:
            # 创建队列
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # 绑定到交换机
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=f'fd.{queue_name}'
            )
            
            print(f"✅ 公平分发队列设置完成: {queue_name}")
            return queue_name
            
        except Exception as e:
            print(f"❌ 设置公平分发队列失败: {e}")
            raise
    
    def setup_priority_queues(self) -> Dict[str, str]:
        """设置优先级队列"""
        queues = {}
        
        try:
            priority_queue_names = [
                'priority_high_queue',
                'priority_normal_queue',
                'priority_low_queue'
            ]
            
            for queue_name in priority_queue_names:
                # 创建队列
                self.channel.queue_declare(queue=queue_name, durable=True)
                
                # 绑定到交换机
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key=f'prio.{queue_name.split("_")[1]}'
                )
                
                queues[queue_name] = queue_name
            
            print(f"✅ 优先级队列设置完成: {list(queues.keys())}")
            return queues
            
        except Exception as e:
            print(f"❌ 设置优先级队列失败: {e}")
            raise
    
    def setup_weighted_queues(self) -> Dict[str, str]:
        """设置权重队列"""
        queues = {}
        
        try:
            weight_queue_names = [
                'weighted_slow_queue',
                'weighted_fast_queue',
                'weighted_premium_queue'
            ]
            
            for queue_name in weight_queue_names:
                # 创建队列
                self.channel.queue_declare(queue=queue_name, durable=True)
                
                # 绑定到交换机
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key=f'weight.{queue_name.split("_")[1]}'
                )
                
                queues[queue_name] = queue_name
            
            print(f"✅ 权重队列设置完成: {list(queues.keys())}")
            return queues
            
        except Exception as e:
            print(f"❌ 设置权重队列失败: {e}")
            raise
    
    def publish_test_messages(self, queue_name: str, count: int = 100,
                             message_type: str = 'normal') -> bool:
        """发布测试消息"""
        try:
            messages_published = 0
            
            for i in range(count):
                message_data = {
                    'message_id': f"{message_type}_{i}",
                    'timestamp': time.time(),
                    'content': f'测试消息 {i} (类型: {message_type})',
                    'processing_delay': random.uniform(0.1, 0.5)  # 随机处理延迟
                }
                
                # 设置路由键
                if 'priority' in queue_name:
                    if 'high' in queue_name:
                        routing_key = 'prio.high'
                        priority = 9
                    elif 'low' in queue_name:
                        routing_key = 'prio.low'
                        priority = 1
                    else:
                        routing_key = 'prio.normal'
                        priority = 5
                    
                    properties = pika.BasicProperties(
                        priority=priority,
                        delivery_mode=2
                    )
                    
                elif 'weighted' in queue_name:
                    if 'slow' in queue_name:
                        routing_key = 'weight.slow'
                    elif 'premium' in queue_name:
                        routing_key = 'weight.premium'
                    else:
                        routing_key = 'weight.fast'
                    
                    properties = pika.BasicProperties(delivery_mode=2)
                    
                else:  # 普通队列
                    if 'rr' in queue_name:
                        routing_key = f'rr.{queue_name}'
                    else:
                        routing_key = f'fd.{queue_name}'
                    
                    properties = pika.BasicProperties(delivery_mode=2)
                
                # 发布消息
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=routing_key,
                    body=json.dumps(message_data),
                    properties=properties
                )
                
                messages_published += 1
                
                # 显示进度
                if (i + 1) % 20 == 0:
                    print(f"  📨 已发布 {i + 1}/{count} 条消息")
            
            print(f"✅ 成功发布 {messages_published} 条消息到 {queue_name}")
            return True
            
        except Exception as e:
            print(f"❌ 发布消息失败: {e}")
            return False
    
    def create_consumer(self, queue_name: str, consumer_id: str, 
                       strategy: str = 'normal') -> threading.Thread:
        """创建消费者线程"""
        def consumer_worker():
            stats = ConsumerStats(consumer_id)
            self.consumer_stats[consumer_id] = stats
            
            def callback(ch, method, properties, body):
                try:
                    start_time = time.time()
                    
                    # 解析消息
                    message_data = json.loads(body.decode())
                    processing_delay = message_data.get('processing_delay', 0.1)
                    
                    # 模拟消息处理
                    time.sleep(processing_delay)
                    
                    end_time = time.time()
                    actual_processing_time = end_time - start_time
                    
                    # 更新统计
                    stats.add_message(actual_processing_time, message_data['message_id'])
                    
                    # 显示处理进度
                    if stats.messages_processed % 10 == 0:
                        print(f"  👤 消费者 {consumer_id}: "
                              f"处理了 {stats.messages_processed} 条消息 "
                              f"(平均 {stats.get_avg_processing_time():.3f}s)")
                    
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    stats.add_error()
                    print(f"❌ 消费者 {consumer_id} 处理错误: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            try:
                # 设置预取策略
                if strategy == 'fair':
                    self.channel.basic_qos(prefetch_count=1)  # 公平分发
                elif strategy == 'batch':
                    self.channel.basic_qos(prefetch_count=10)  # 批处理
                else:
                    self.channel.basic_qos(prefetch_count=1)  # 默认
                
                # 开始消费
                self.channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=callback,
                    consumer_tag=f"consumer_{consumer_id}"
                )
                
                print(f"🚀 消费者 {consumer_id} 开始处理队列 {queue_name}")
                
                # 开始消费循环
                self.channel.start_consuming()
                
            except Exception as e:
                print(f"❌ 消费者 {consumer_id} 异常: {e}")
        
        thread = threading.Thread(target=consumer_worker)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def run_round_robin_test(self, duration: int = 30):
        """运行轮询分发测试"""
        print("\n" + "="*60)
        print("🔄 轮询分发测试")
        print("="*60)
        
        queue_name = self.setup_round_robin_queue('test_round_robin')
        
        # 发布测试消息
        print("\n📤 发布测试消息...")
        message_count = 60
        self.publish_test_messages(queue_name, message_count, 'round_robin')
        
        # 启动消费者
        print(f"\n👥 启动 {3} 个消费者...")
        consumers = []
        for i in range(3):
            consumer = self.create_consumer(queue_name, f'rr_consumer_{i+1}', 'normal')
            consumers.append(consumer)
        
        # 等待消息处理完成
        print(f"\n⏳ 等待消息处理完成...")
        for i in range(duration):
            time.sleep(1)
            if i % 5 == 0:
                remaining = message_count - sum(stats.messages_processed 
                                              for stats in self.consumer_stats.values())
                print(f"  ⏱️  处理进度: {message_count - remaining}/{message_count} 条完成")
                if remaining <= 0:
                    break
        
        # 等待消费者完成当前消息
        time.sleep(2)
        
        # 停止消费
        self.channel.stop_consuming()
        
        # 显示结果
        self.print_test_results('Round Robin', message_count)
    
    def run_fair_distribution_test(self, duration: int = 30):
        """运行公平分发测试"""
        print("\n" + "="*60)
        print("⚖️  公平分发测试")
        print("="*60)
        
        queue_name = self.setup_fair_distribution_queue('test_fair_distribution')
        
        # 发布测试消息
        print("\n📤 发布测试消息...")
        message_count = 60
        self.publish_test_messages(queue_name, message_count, 'fair_distribution')
        
        # 启动不同性能的消费者
        print(f"\n👥 启动不同性能的消费者...")
        consumers = []
        
        # 快速消费者
        consumer1 = self.create_consumer(queue_name, 'fd_fast_consumer', 'fair')
        consumers.append(consumer1)
        
        # 慢速消费者
        consumer2 = self.create_consumer(queue_name, 'fd_slow_consumer', 'fair')
        consumers.append(consumer2)
        
        # 等待处理完成
        print(f"\n⏳ 等待消息处理完成...")
        for i in range(duration):
            time.sleep(1)
            if i % 5 == 0:
                completed = sum(stats.messages_processed 
                              for stats in self.consumer_stats.values())
                remaining = message_count - completed
                print(f"  ⏱️  处理进度: {completed}/{message_count} 条完成")
                if remaining <= 0:
                    break
        
        time.sleep(2)
        self.channel.stop_consuming()
        
        # 显示结果
        self.print_test_results('Fair Distribution', message_count)
    
    def run_priority_test(self, duration: int = 30):
        """运行优先级测试"""
        print("\n" + "="*60)
        print("🎯 优先级队列测试")
        print("="*60)
        
        priority_queues = self.setup_priority_queues()
        
        # 发布不同优先级的消息
        print("\n📤 发布不同优先级的消息...")
        
        # 高优先级消息
        print("  🔥 高优先级消息...")
        for i in range(10):
            message_data = {
                'message_id': f'priority_high_{i}',
                'priority_level': 'high',
                'content': f'高优先级消息 {i}',
                'processing_delay': 0.1
            }
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='prio.high',
                body=json.dumps(message_data),
                properties=pika.BasicProperties(priority=9)
            )
        
        # 普通优先级消息
        print("  📋 普通优先级消息...")
        for i in range(20):
            message_data = {
                'message_id': f'priority_normal_{i}',
                'priority_level': 'normal',
                'content': f'普通优先级消息 {i}',
                'processing_delay': 0.2
            }
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='prio.normal',
                body=json.dumps(message_data),
                properties=pika.BasicProperties(priority=5)
            )
        
        # 低优先级消息
        print("  🔽 低优先级消息...")
        for i in range(15):
            message_data = {
                'message_id': f'priority_low_{i}',
                'priority_level': 'low',
                'content': f'低优先级消息 {i}',
                'processing_delay': 0.3
            }
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='prio.low',
                body=json.dumps(message_data),
                properties=pika.BasicProperties(priority=1)
            )
        
        # 启动优先级消费者
        print(f"\n👥 启动优先级消费者...")
        consumers = []
        
        # 高优先级队列消费者
        consumer1 = self.create_consumer('priority_high_queue', 'prio_high_consumer')
        consumers.append(consumer1)
        
        # 普通优先级队列消费者
        consumer2 = self.create_consumer('priority_normal_queue', 'prio_normal_consumer')
        consumers.append(consumer2)
        
        # 低优先级队列消费者
        consumer3 = self.create_consumer('priority_low_queue', 'prio_low_consumer')
        consumers.append(consumer3)
        
        # 等待处理完成
        print(f"\n⏳ 等待消息处理完成...")
        for i in range(duration):
            time.sleep(1)
            total_processed = sum(stats.messages_processed 
                                for stats in self.consumer_stats.values())
            if total_processed >= 45:  # 总消息数
                break
            if i % 5 == 0:
                print(f"  ⏱️  处理进度: {total_processed}/45 条完成")
        
        time.sleep(2)
        self.channel.stop_consuming()
        
        # 显示结果
        self.print_test_results('Priority Queue', 45)
    
    def run_weighted_test(self, duration: int = 30):
        """运行权重测试"""
        print("\n" + "="*60)
        print("⚖️  权重队列测试")
        print("="*60)
        
        weighted_queues = self.setup_weighted_queues()
        
        # 发布不同权重的消息
        print("\n📤 发布不同权重的消息...")
        
        # 发送到慢队列
        for i in range(30):
            message_data = {
                'message_id': f'weighted_slow_{i}',
                'weight_type': 'slow',
                'content': f'慢处理消息 {i}',
                'processing_delay': 0.8
            }
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='weight.slow',
                body=json.dumps(message_data)
            )
        
        # 发送到快队列
        for i in range(30):
            message_data = {
                'message_id': f'weighted_fast_{i}',
                'weight_type': 'fast',
                'content': f'快处理消息 {i}',
                'processing_delay': 0.2
            }
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='weight.fast',
                body=json.dumps(message_data)
            )
        
        # 发送到高级队列
        for i in range(15):
            message_data = {
                'message_id': f'weighted_premium_{i}',
                'weight_type': 'premium',
                'content': f'高级处理消息 {i}',
                'processing_delay': 0.1
            }
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='weight.premium',
                body=json.dumps(message_data)
            )
        
        # 启动权重消费者
        print(f"\n👥 启动权重消费者...")
        consumers = []
        
        # 慢处理消费者
        consumer1 = self.create_consumer('weighted_slow_queue', 'weight_slow_consumer')
        consumers.append(consumer1)
        
        # 快处理消费者
        consumer2 = self.create_consumer('weighted_fast_queue', 'weight_fast_consumer')
        consumers.append(consumer2)
        
        # 高级处理消费者
        consumer3 = self.create_consumer('weighted_premium_queue', 'weight_premium_consumer')
        consumers.append(consumer3)
        
        # 等待处理完成
        print(f"\n⏳ 等待消息处理完成...")
        for i in range(duration):
            time.sleep(1)
            total_processed = sum(stats.messages_processed 
                                for stats in self.consumer_stats.values())
            if total_processed >= 75:  # 总消息数
                break
            if i % 5 == 0:
                print(f"  ⏱️  处理进度: {total_processed}/75 条完成")
        
        time.sleep(2)
        self.channel.stop_consuming()
        
        # 显示结果
        self.print_test_results('Weighted Queue', 75)
    
    def print_test_results(self, test_name: str, expected_count: int):
        """打印测试结果"""
        print(f"\n📊 {test_name} 测试结果")
        print("-" * 50)
        
        if not self.consumer_stats:
            print("❌ 没有消费者统计数据")
            return
        
        total_processed = sum(stats.messages_processed for stats in self.consumer_stats.values())
        total_errors = sum(stats.errors for stats in self.consumer_stats.values())
        
        print(f"📈 总体统计:")
        print(f"  期望消息数: {expected_count}")
        print(f"  处理消息数: {total_processed}")
        print(f"  错误消息数: {total_errors}")
        print(f"  成功率: {(total_processed / expected_count * 100):.1f}%")
        
        print(f"\n👤 消费者详细统计:")
        print(f"{'消费者ID':<20} {'处理数':<8} {'吞吐量':<12} {'平均耗时':<10} {'错误':<6}")
        print("-" * 60)
        
        for consumer_id, stats in self.consumer_stats.items():
            throughput = stats.get_throughput()
            avg_time = stats.get_avg_processing_time()
            
            print(f"{consumer_id:<20} {stats.messages_processed:<8} "
                  f"{throughput:<12.2f} {avg_time:<10.3f} {stats.errors:<6}")
        
        # 分析负载均衡效果
        if len(self.consumer_stats) > 1:
            message_counts = [stats.messages_processed for stats in self.consumer_stats.values()]
            max_count = max(message_counts)
            min_count = min(message_counts)
            load_balance_ratio = min_count / max_count if max_count > 0 else 0
            
            print(f"\n⚖️  负载均衡效果:")
            print(f"  最大处理量: {max_count}")
            print(f"  最小处理量: {min_count}")
            print(f"  均衡比例: {load_balance_ratio:.2%}")
            
            if load_balance_ratio > 0.8:
                print("  ✅ 负载均衡效果良好")
            elif load_balance_ratio > 0.6:
                print("  ⚠️  负载均衡效果一般")
            else:
                print("  ❌ 负载均衡效果较差")
    
    def cleanup_test_queues(self):
        """清理测试队列"""
        test_queues = [
            'test_round_robin',
            'test_fair_distribution',
            'priority_high_queue',
            'priority_normal_queue',
            'priority_low_queue',
            'weighted_slow_queue',
            'weighted_fast_queue',
            'weighted_premium_queue'
        ]
        
        for queue_name in test_queues:
            try:
                # 清空队列
                self.channel.queue_purge(queue=queue_name)
                print(f"🧹 已清空队列: {queue_name}")
            except Exception as e:
                print(f"❌ 清空队列失败 {queue_name}: {e}")
        
        print("✅ 测试队列清理完成")


def main():
    """主函数"""
    print("🐰 RabbitMQ 负载均衡策略演示")
    print("=" * 60)
    
    try:
        with LoadBalancingDemo() as demo:
            # 1. 轮询分发测试
            demo.run_round_robin_test()
            
            # 清理并等待
            time.sleep(2)
            demo.cleanup_test_queues()
            time.sleep(1)
            
            # 2. 公平分发测试
            demo.run_fair_distribution_test()
            
            # 清理并等待
            time.sleep(2)
            demo.cleanup_test_queues()
            time.sleep(1)
            
            # 3. 优先级测试
            demo.run_priority_test()
            
            # 清理并等待
            time.sleep(2)
            demo.cleanup_test_queues()
            time.sleep(1)
            
            # 4. 权重测试
            demo.run_weighted_test()
            
            print("\n🎉 所有负载均衡测试完成！")
            
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()