#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第5章：队列管理与负载均衡 - 队列管理基础示例
演示队列的创建、配置、监控和生命周期管理
"""

import pika
import time
import json
import threading
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from typing import Any


@dataclass
class QueueConfig:
    """队列配置"""
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class QueueMetrics:
    """队列指标"""
    queue_name: str
    message_count: int
    consumer_count: int
    timestamp: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


class QueueManagementDemo:
    """队列管理演示类"""
    
    def __init__(self, connection_params=None):
        """初始化"""
        self.connection_params = connection_params or pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=pika.PlainCredentials('guest', 'guest')
        )
        self.connection = None
        self.channel = None
        self.queues_created = []
        
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
            print("✅ 成功连接到RabbitMQ")
        except Exception as e:
            print(f"❌ 连接RabbitMQ失败: {e}")
            raise
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 已断开RabbitMQ连接")
    
    def create_queue(self, config: QueueConfig) -> bool:
        """创建队列"""
        try:
            self.channel.queue_declare(
                queue=config.name,
                durable=config.durable,
                exclusive=config.exclusive,
                auto_delete=config.auto_delete,
                arguments=config.arguments or {}
            )
            
            self.queues_created.append(config.name)
            print(f"✅ 队列创建成功: {config.name}")
            return True
            
        except Exception as e:
            print(f"❌ 创建队列失败 {config.name}: {e}")
            return False
    
    def create_multiple_queues(self, configs: List[QueueConfig]) -> int:
        """批量创建队列"""
        success_count = 0
        
        for config in configs:
            if self.create_queue(config):
                success_count += 1
        
        print(f"📊 批量创建结果: {success_count}/{len(configs)} 个队列创建成功")
        return success_count
    
    def get_queue_info(self, queue_name: str) -> Optional[QueueMetrics]:
        """获取队列信息"""
        try:
            result = self.channel.queue_declare(queue=queue_name, passive=True)
            
            # 获取系统指标
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            
            metrics = QueueMetrics(
                queue_name=queue_name,
                message_count=result.method.message_count,
                consumer_count=result.method.consumer_count,
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage
            )
            
            return metrics
            
        except Exception as e:
            print(f"❌ 获取队列信息失败 {queue_name}: {e}")
            return None
    
    def get_all_queues_info(self) -> Dict[str, QueueMetrics]:
        """获取所有队列信息"""
        queues_info = {}
        
        for queue_name in self.queues_created:
            metrics = self.get_queue_info(queue_name)
            if metrics:
                queues_info[queue_name] = metrics
        
        return queues_info
    
    def publish_messages(self, queue_name: str, count: int = 100, 
                        message_size: int = 1000) -> bool:
        """发布消息到队列"""
        try:
            messages_published = 0
            
            for i in range(count):
                # 生成测试消息
                message_data = {
                    'message_id': i,
                    'queue_name': queue_name,
                    'timestamp': time.time(),
                    'content': 'x' * message_size,
                    'priority': i % 10
                }
                
                properties = pika.BasicProperties(
                    message_id=str(i),
                    timestamp=int(time.time()),
                    delivery_mode=2,  # 持久化
                    priority=message_data['priority']
                )
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message_data),
                    properties=properties
                )
                
                messages_published += 1
                
                # 显示进度
                if (i + 1) % 10 == 0:
                    print(f"📨 已发布 {i + 1}/{count} 条消息到 {queue_name}")
            
            print(f"✅ 成功发布 {messages_published} 条消息到队列 {queue_name}")
            return True
            
        except Exception as e:
            print(f"❌ 发布消息失败: {e}")
            return False
    
    def consume_messages(self, queue_name: str, consumer_id: str, 
                        max_messages: int = 50) -> Dict[str, int]:
        """消费消息"""
        stats = {'processed': 0, 'errors': 0, 'start_time': time.time()}
        
        def callback(ch, method, properties, body):
            try:
                message_data = json.loads(body.decode())
                
                # 模拟消息处理
                processing_time = 0.1 + (message_data.get('priority', 5) * 0.01)
                time.sleep(processing_time)
                
                stats['processed'] += 1
                
                # 显示进度
                if stats['processed'] % 10 == 0:
                    print(f"👤 消费者 {consumer_id} 处理进度: {stats['processed']}")
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                stats['errors'] += 1
                print(f"❌ 消费者 {consumer_id} 处理错误: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            # 达到最大消息数时停止
            if stats['processed'] + stats['errors'] >= max_messages:
                ch.stop_consuming()
        
        try:
            # 设置公平分发
            self.channel.basic_qos(prefetch_count=1)
            
            # 开始消费
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                consumer_tag=f"consumer_{consumer_id}"
            )
            
            print(f"🚀 消费者 {consumer_id} 开始处理队列 {queue_name}")
            self.channel.start_consuming()
            
        except Exception as e:
            print(f"❌ 消费者 {consumer_id} 异常: {e}")
        
        return stats
    
    def start_consumer_thread(self, queue_name: str, consumer_id: str, 
                             max_messages: int = 100) -> threading.Thread:
        """启动消费者线程"""
        def consumer_worker():
            stats = self.consume_messages(queue_name, consumer_id, max_messages)
            
            duration = time.time() - stats['start_time']
            throughput = stats['processed'] / duration if duration > 0 else 0
            
            print(f"\n📊 消费者 {consumer_id} 完成:")
            print(f"  处理消息: {stats['processed']}")
            print(f"  错误消息: {stats['errors']}")
            print(f"  吞吐量: {throughput:.2f} 消息/秒")
        
        thread = threading.Thread(target=consumer_worker)
        thread.start()
        
        return thread
    
    def monitor_queues_realtime(self, duration: int = 30):
        """实时监控队列"""
        print(f"\n🔍 开始实时监控队列 (持续 {duration} 秒)")
        print("-" * 60)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n⏰ {current_time}")
            
            # 获取所有队列信息
            for queue_name in self.queues_created:
                metrics = self.get_queue_info(queue_name)
                if metrics:
                    status = "🟢"
                    if metrics.message_count > 100:
                        status = "🟡"
                    if metrics.message_count > 500:
                        status = "🔴"
                    
                    print(f"{status} {queue_name}: "
                          f"消息={metrics.message_count}, "
                          f"消费者={metrics.consumer_count}, "
                          f"CPU={metrics.cpu_usage:.1f}%")
            
            time.sleep(2)
        
        print("\n⏹️  实时监控结束")
    
    def cleanup_queues(self):
        """清理测试队列"""
        deleted_count = 0
        
        for queue_name in self.queues_created:
            try:
                # 清空队列
                self.channel.queue_purge(queue=queue_name)
                deleted_count += 1
                print(f"🧹 清空队列: {queue_name}")
                
            except Exception as e:
                print(f"❌ 清空队列失败 {queue_name}: {e}")
        
        self.queues_created.clear()
        print(f"✅ 清理完成: {deleted_count} 个队列")
    
    def demonstrate_queue_lifecycle(self):
        """演示队列生命周期"""
        print("\n" + "="*60)
        print("📋 队列生命周期演示")
        print("="*60)
        
        # 1. 创建测试队列
        print("\n1️⃣ 创建测试队列")
        test_configs = [
            QueueConfig("demo_queue_1", arguments={'x-message-ttl': 300000}),
            QueueConfig("demo_queue_2", arguments={'x-max-length': 100}),
            QueueConfig("demo_queue_3", durable=True, arguments={
                'x-max-priority': 10,
                'x-message-ttl': 600000
            })
        ]
        
        self.create_multiple_queues(test_configs)
        
        # 2. 发布测试消息
        print("\n2️⃣ 发布测试消息")
        for queue_name in ["demo_queue_1", "demo_queue_2"]:
            self.publish_messages(queue_name, count=50)
        
        # 3. 监控队列状态
        print("\n3️⃣ 监控队列状态")
        time.sleep(1)  # 等待消息发布完成
        self.monitor_queues_realtime(duration=10)
        
        # 4. 启动消费者
        print("\n4️⃣ 启动消费者处理消息")
        consumers = [
            self.start_consumer_thread("demo_queue_1", "consumer_1", 25),
            self.start_consumer_thread("demo_queue_2", "consumer_2", 25)
        ]
        
        # 等待消费者完成
        for consumer in consumers:
            consumer.join()
        
        # 5. 清理
        print("\n5️⃣ 清理测试队列")
        self.cleanup_queues()
    
    def demonstrate_performance_monitoring(self):
        """演示性能监控"""
        print("\n" + "="*60)
        print("📈 性能监控演示")
        print("="*60)
        
        # 创建性能测试队列
        perf_config = QueueConfig("performance_test_queue", durable=True)
        self.create_queue(perf_config)
        
        # 测试不同预取数量的性能
        print("\n🧪 测试不同预取数量的性能...")
        
        prefetch_results = []
        
        for prefetch_count in [1, 5, 10, 20, 50]:
            print(f"\n测试预取数量: {prefetch_count}")
            
            # 设置预取
            self.channel.basic_qos(prefetch_count=prefetch_count)
            
            # 发布消息
            message_count = 200
            self.publish_messages("performance_test_queue", count=message_count)
            
            # 消费并计时
            start_time = time.time()
            stats = self.consume_messages("performance_test_queue", "perf_test", 
                                        max_messages=message_count)
            end_time = time.time()
            
            duration = end_time - start_time
            throughput = message_count / duration if duration > 0 else 0
            
            result = {
                'prefetch_count': prefetch_count,
                'throughput': throughput,
                'duration': duration,
                'errors': stats['errors']
            }
            
            prefetch_results.append(result)
            
            print(f"  吞吐量: {throughput:.2f} 消息/秒")
            print(f"  耗时: {duration:.2f} 秒")
            print(f"  错误: {stats['errors']}")
        
        # 分析结果
        print("\n📊 预取性能分析:")
        print("-" * 40)
        print(f"{'预取数量':<10} {'吞吐量':<15} {'耗时':<10} {'错误':<5}")
        print("-" * 40)
        
        for result in prefetch_results:
            print(f"{result['prefetch_count']:<10} "
                  f"{result['throughput']:<15.2f} "
                  f"{result['duration']:<10.2f} "
                  f"{result['errors']:<5}")
        
        # 找到最佳预取数量
        best_result = max(prefetch_results, key=lambda x: x['throughput'])
        print(f"\n🏆 最佳预取数量: {best_result['prefetch_count']} "
              f"(吞吐量: {best_result['throughput']:.2f} 消息/秒)")
        
        # 清理
        self.cleanup_queues()
    
    def demonstrate_advanced_queue_config(self):
        """演示高级队列配置"""
        print("\n" + "="*60)
        print("⚙️  高级队列配置演示")
        print("="*60)
        
        # 创建带高级配置的队列
        advanced_configs = [
            QueueConfig(
                "ttl_queue",
                arguments={
                    'x-message-ttl': 60000,  # 1分钟TTL
                    'x-dead-letter-exchange': 'dlx',
                    'x-dead-letter-routing-key': 'dead_letter'
                }
            ),
            QueueConfig(
                "max_length_queue",
                arguments={
                    'x-max-length': 10,  # 最大长度10
                    'x-overflow': 'reject-publish'  # 拒绝新消息
                }
            ),
            QueueConfig(
                "priority_queue",
                arguments={
                    'x-max-priority': 5  # 最大优先级5
                }
            )
        ]
        
        print("\n1️⃣ 创建高级配置队列")
        self.create_multiple_queues(advanced_configs)
        
        # 测试TTL队列
        print("\n2️⃣ 测试TTL队列")
        print("发送消息到TTL队列（60秒过期）...")
        for i in range(3):
            message_data = {
                'message_id': i,
                'content': f'TTL测试消息 {i}'
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key='ttl_queue',
                body=json.dumps(message_data)
            )
            print(f"  发送: TTL测试消息 {i}")
        
        # 测试最大长度队列
        print("\n3️⃣ 测试最大长度队列")
        print("尝试发送超过最大长度限制的消息...")
        
        success_count = 0
        for i in range(15):  # 超过最大长度10
            try:
                message_data = {'message_id': i, 'content': f'长度限制测试 {i}'}
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key='max_length_queue',
                    body=json.dumps(message_data)
                )
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ 发送失败 (预期): 长度限制测试 {i}")
        
        print(f"  ✅ 成功发送 {success_count}/15 条消息 (10条限制生效)")
        
        # 测试优先级队列
        print("\n4️⃣ 测试优先级队列")
        print("发送不同优先级的消息...")
        
        for priority in [1, 5, 3, 4, 2]:
            message_data = {
                'content': f'优先级 {priority} 消息',
                'priority': priority
            }
            
            properties = pika.BasicProperties(priority=priority)
            
            self.channel.basic_publish(
                exchange='',
                routing_key='priority_queue',
                body=json.dumps(message_data),
                properties=properties
            )
            print(f"  📤 发送优先级 {priority} 消息")
        
        # 检查队列状态
        print("\n5️⃣ 检查队列状态")
        time.sleep(1)
        
        for queue_name in ['ttl_queue', 'max_length_queue', 'priority_queue']:
            metrics = self.get_queue_info(queue_name)
            if metrics:
                print(f"📊 {queue_name}: {metrics.message_count} 条消息")
        
        # 清理
        print("\n6️⃣ 清理测试队列")
        self.cleanup_queues()


def main():
    """主函数"""
    print("🐰 RabbitMQ 队列管理与负载均衡演示")
    print("=" * 60)
    
    try:
        with QueueManagementDemo() as queue_demo:
            # 1. 队列生命周期演示
            queue_demo.demonstrate_queue_lifecycle()
            
            # 2. 性能监控演示
            queue_demo.demonstrate_performance_monitoring()
            
            # 3. 高级队列配置演示
            queue_demo.demonstrate_advanced_queue_config()
            
            print("\n🎉 所有演示完成！")
            
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()