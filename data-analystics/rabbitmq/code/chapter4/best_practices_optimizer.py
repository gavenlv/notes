#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第4章：消息确认最佳实践和性能优化演示
展示实际生产环境中的优化策略和监控方法
"""

import pika
import time
import uuid
import threading
import json
import queue
import statistics
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging

@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    queue_length: int
    throughput: float
    latency_ms: float
    error_rate: float

class OptimizerLevel(Enum):
    """优化级别"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    PRODUCTION = "production"

class BackoffStrategy(Enum):
    """重试策略"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    IMMEDIATE = "immediate"

class MessageProcessor:
    """消息处理器"""
    
    def __init__(self, processor_id: str, complexity: int = 1):
        self.processor_id = processor_id
        self.complexity = complexity
        self.processed_count = 0
        self.error_count = 0
        self.processing_times = deque(maxlen=1000)
        self.lock = threading.Lock()
    
    def process(self, message: Dict) -> Tuple[bool, float]:
        """处理消息"""
        start_time = time.time()
        
        try:
            # 模拟复杂处理逻辑
            for _ in range(self.complexity):
                # CPU密集型操作
                result = sum(i * i for i in range(100))
                
                # 内存操作
                temp_data = [0] * 1000
                temp_data.clear()
                
                # I/O操作模拟
                time.sleep(0.0001)
            
            processing_time = time.time() - start_time
            
            # 模拟随机错误
            if self.processed_count % 17 == 0:
                raise Exception("随机处理错误")
            
            with self.lock:
                self.processed_count += 1
                self.processing_times.append(processing_time)
                return True, processing_time
                
        except Exception as e:
            with self.lock:
                self.error_count += 1
                return False, time.time() - start_time
    
    def get_metrics(self) -> Dict:
        """获取处理器指标"""
        with self.lock:
            avg_time = statistics.mean(self.processing_times) if self.processing_times else 0
            error_rate = (self.error_count / max(1, self.processed_count + self.error_count)) * 100
            
            return {
                'processor_id': self.processor_id,
                'processed_count': self.processed_count,
                'error_count': self.error_count,
                'avg_processing_time': avg_time,
                'error_rate': error_rate,
                'complexity': self.complexity
            }

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.metrics = deque(maxlen=3600)  # 存储1小时的数据
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
    
    def start_monitoring(self):
        """开始监控"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = PerformanceMetrics(
                    timestamp=time.time(),
                    cpu_percent=psutil.cpu_percent(),
                    memory_mb=psutil.virtual_memory().used / 1024 / 1024,
                    queue_length=0,  # 由外部设置
                    throughput=0,    # 由外部设置
                    latency_ms=0,    # 由外部设置
                    error_rate=0     # 由外部设置
                )
                
                with self.lock:
                    self.metrics.append(metrics)
                
                time.sleep(self.interval)
                
            except Exception as e:
                logging.error(f"监控错误: {e}")
                time.sleep(self.interval)
    
    def add_metrics(self, queue_length: int, throughput: float, latency_ms: float, error_rate: float):
        """添加指标"""
        if self.metrics:
            with self.lock:
                last_metrics = self.metrics[-1]
                updated_metrics = PerformanceMetrics(
                    timestamp=time.time(),
                    cpu_percent=last_metrics.cpu_percent,
                    memory_mb=last_metrics.memory_mb,
                    queue_length=queue_length,
                    throughput=throughput,
                    latency_ms=latency_ms,
                    error_rate=error_rate
                )
                self.metrics.append(updated_metrics)
    
    def get_recent_metrics(self, duration_minutes: int = 5) -> List[PerformanceMetrics]:
        """获取最近的指标"""
        cutoff_time = time.time() - (duration_minutes * 60)
        
        with self.lock:
            return [m for m in self.metrics if m.timestamp >= cutoff_time]
    
    def print_performance_report(self):
        """打印性能报告"""
        recent_metrics = self.get_recent_metrics()
        
        if not recent_metrics:
            return
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_mb for m in recent_metrics]
        throughput_values = [m.throughput for m in recent_metrics]
        latency_values = [m.latency_ms for m in recent_metrics]
        error_rate_values = [m.error_rate for m in recent_metrics]
        
        print(f"\n📊 系统性能报告 (最近 {len(recent_metrics)} 秒):")
        print(f"  CPU使用率: {statistics.mean(cpu_values):.1f}% (最大: {max(cpu_values):.1f}%)")
        print(f"  内存使用: {statistics.mean(memory_values):.0f}MB (最大: {max(memory_values):.0f}MB)")
        print(f"  平均吞吐量: {statistics.mean(throughput_values):.2f} 消息/秒")
        print(f"  平均延迟: {statistics.mean(latency_values):.2f}ms")
        print(f"  平均错误率: {statistics.mean(error_rate_values):.2f}%")

class OptimizedMessageConsumer:
    """优化的消息消费者"""
    
    def __init__(self, queue_name: str, processor_count: int = 4, 
                 prefetch_count: int = 50, auto_scale: bool = True):
        self.queue_name = queue_name
        self.processor_count = processor_count
        self.prefetch_count = prefetch_count
        self.auto_scale = auto_scale
        
        self.connection_params = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            heartbeat=30,
            connection_attempts=3
        )
        
        self.processors = [
            MessageProcessor(f"processor_{i}", complexity=2) 
            for i in range(processor_count)
        ]
        
        self.message_queue = queue.Queue(maxsize=1000)
        self.is_running = False
        self.consumer_threads = []
        self.processor_threads = []
        
        # 性能统计
        self.total_processed = 0
        self.total_errors = 0
        self.lock = threading.Lock()
    
    def _get_connection(self):
        """获取连接"""
        return pika.BlockingConnection(self.connection_params)
    
    def _adaptive_prefetch(self):
        """自适应预取"""
        recent_metrics = [
            p.get_metrics()['avg_processing_time'] 
            for p in self.processors
        ]
        
        if not recent_metrics:
            return self.prefetch_count
        
        avg_processing_time = statistics.mean(recent_metrics)
        
        # 根据处理时间动态调整预取数量
        if avg_processing_time > 0.1:  # 处理时间超过100ms
            return max(10, self.prefetch_count // 2)
        elif avg_processing_time < 0.01:  # 处理时间少于10ms
            return min(100, self.prefetch_count * 2)
        else:
            return self.prefetch_count
    
    def _auto_scaling(self):
        """自动扩缩容"""
        if not self.auto_scale:
            return
        
        avg_error_rate = statistics.mean([
            p.get_metrics()['error_rate'] 
            for p in self.processors
        ])
        
        avg_processing_time = statistics.mean([
            p.get_metrics()['avg_processing_time'] 
            for p in self.processors
        ])
        
        # 如果错误率过高或处理时间过长，添加处理器
        if avg_error_rate > 10 or avg_processing_time > 0.2:
            if len(self.processors) < 8:  # 最大8个处理器
                new_processor = MessageProcessor(
                    f"processor_{len(self.processors)}", 
                    complexity=1  # 新处理器复杂度较低
                )
                self.processors.append(new_processor)
                
                # 启动新的处理器线程
                processor_thread = threading.Thread(
                    target=self._processor_worker, 
                    args=(new_processor,)
                )
                processor_thread.start()
                self.processor_threads.append(processor_thread)
                
                print(f"🔧 自动扩容：添加处理器 {new_processor.processor_id}")
    
    def _consumer_worker(self, connection):
        """消费者工作线程"""
        channel = connection.channel()
        
        # 设置预取
        current_prefetch = self._adaptive_prefetch()
        channel.basic_qos(prefetch_count=current_prefetch)
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode())
                
                # 检查队列大小
                if self.message_queue.qsize() > 800:
                    print("⚠️ 队列接近满载，减慢消费速度")
                    time.sleep(0.1)
                
                # 将消息放入处理队列
                self.message_queue.put((message, method, properties), timeout=1.0)
                
                # 自动扩缩容检查
                if self.total_processed % 100 == 0:
                    self._auto_scaling()
                
            except queue.Full:
                print("❌ 处理队列已满，消息可能被重复投递")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except Exception as e:
                print(f"❌ 接收消息失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        try:
            channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            # 处理消息事件
            while self.is_running:
                connection.process_data_events(time_limit=1.0)
                
        except Exception as e:
            print(f"❌ 消费者工作线程错误: {e}")
        finally:
            if channel.is_open:
                channel.close()
    
    def _processor_worker(self, processor: MessageProcessor):
        """处理器工作线程"""
        while self.is_running:
            try:
                # 从队列获取消息
                message, method, properties = self.message_queue.get(timeout=1.0)
                
                # 处理消息
                success, processing_time = processor.process(message)
                
                with self.lock:
                    if success:
                        self.total_processed += 1
                    else:
                        self.total_errors += 1
                
                # 确认消息
                try:
                    if success:
                        # 模拟延迟确认以优化性能
                        time.sleep(0.0001)
                        # 这里需要访问连接，但在多线程环境中需要特殊处理
                        # 实际实现中应该通过回调或消息传递来确认
                    
                except Exception as e:
                    print(f"❌ 消息确认失败: {e}")
                
                self.message_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 处理器 {processor.processor_id} 错误: {e}")
    
    def start(self):
        """启动消费者"""
        self.is_running = True
        
        # 启动处理器线程
        for processor in self.processors:
            thread = threading.Thread(target=self._processor_worker, args=(processor,))
            thread.start()
            self.processor_threads.append(thread)
        
        # 启动消费者线程
        def consumer_wrapper():
            while self.is_running:
                try:
                    connection = self._get_connection()
                    self._consumer_worker(connection)
                except Exception as e:
                    print(f"❌ 连接错误: {e}")
                    time.sleep(5)  # 等待重连
        
        consumer_thread = threading.Thread(target=consumer_wrapper)
        consumer_thread.start()
        self.consumer_threads.append(consumer_thread)
        
        print(f"🚀 启动优化的消息消费者，队列: {self.queue_name}")
    
    def stop(self):
        """停止消费者"""
        self.is_running = False
        
        # 等待所有线程结束
        for thread in self.consumer_threads + self.processor_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        print("⏹️ 优化的消息消费者已停止")
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        with self.lock:
            error_rate = (self.total_errors / max(1, self.total_processed + self.total_errors)) * 100
        
        # 处理器统计
        processor_stats = [p.get_metrics() for p in self.processors]
        
        return {
            'total_processed': self.total_processed,
            'total_errors': self.total_errors,
            'error_rate': error_rate,
            'queue_size': self.message_queue.qsize(),
            'processor_count': len(self.processors),
            'prefetch_count': self.prefetch_count,
            'processor_stats': processor_stats
        }

class BestPracticesDemo:
    """最佳实践演示"""
    
    def __init__(self):
        self.monitor = SystemMonitor(interval=2.0)
        self.consumers = {}
        self.connection_params = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            heartbeat=30
        )
    
    def setup_optimized_queues(self):
        """设置优化的队列"""
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 创建优化队列
        queues = [
            {
                'name': 'optimized_queue',
                'args': {
                    'x-max-length': 10000,          # 最大队列长度
                    'x-overflow': 'reject-publish', # 溢出策略
                    'x-dead-letter-exchange': 'dlx_optimized',
                    'x-dead-letter-routing-key': 'dead_letter_optimized'
                }
            },
            {
                'name': 'high_priority_queue',
                'args': {
                    'x-max-priority': 10,           # 最大优先级
                    'x-max-length': 5000,           # 最大队列长度
                    'x-message-ttl': 3600000        # 1小时TTL
                }
            }
        ]
        
        # 创建死信交换机
        channel.exchange_declare(
            exchange='dlx_optimized',
            exchange_type='direct',
            durable=True
        )
        
        channel.queue_declare(
            queue='dead_letter_optimized',
            durable=True
        )
        
        channel.queue_bind(
            exchange='dlx_optimized',
            queue='dead_letter_optimized',
            routing_key='dead_letter_optimized'
        )
        
        # 创建队列
        for queue_config in queues:
            try:
                channel.queue_declare(
                    queue=queue_config['name'],
                    durable=True,
                    arguments=queue_config['args']
                )
                print(f"✅ 创建队列: {queue_config['name']}")
            except Exception as e:
                print(f"❌ 创建队列失败 {queue_config['name']}: {e}")
        
        connection.close()
    
    def demo_basic_optimization(self):
        """基础优化演示"""
        print("\n🔧 基础优化演示")
        print("-" * 40)
        
        # 创建消费者
        consumer = OptimizedMessageConsumer(
            queue_name='optimized_queue',
            processor_count=3,
            prefetch_count=20,
            auto_scale=False
        )
        
        self.consumers['basic'] = consumer
        consumer.start()
        
        # 发送测试消息
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        print("📤 发送测试消息...")
        for i in range(100):
            message = {
                'id': str(uuid.uuid4()),
                'sequence': i,
                'content': f'基础优化测试消息 {i}',
                'priority': i % 5
            }
            
            properties = pika.BasicProperties(
                priority=message['priority'],
                delivery_mode=2,
                message_id=message['id']
            )
            
            channel.basic_publish(
                exchange='',
                routing_key='optimized_queue',
                body=json.dumps(message),
                properties=properties
            )
        
        connection.close()
        
        # 监控处理过程
        print("📊 监控处理过程...")
        for i in range(30):
            time.sleep(2)
            
            metrics = consumer.get_performance_metrics()
            self.monitor.add_metrics(
                queue_length=metrics['queue_size'],
                throughput=metrics['total_processed'],
                latency_ms=0,  # 这里可以添加更精确的延迟测量
                error_rate=metrics['error_rate']
            )
            
            print(f"  进度: 处理 {metrics['total_processed']}, 错误 {metrics['total_errors']}, "
                  f"队列 {metrics['queue_size']}")
        
        consumer.stop()
        self.monitor.print_performance_report()
    
    def demo_advanced_optimization(self):
        """高级优化演示"""
        print("\n🚀 高级优化演示")
        print("-" * 40)
        
        # 创建消费者
        consumer = OptimizedMessageConsumer(
            queue_name='optimized_queue',
            processor_count=4,
            prefetch_count=50,
            auto_scale=True
        )
        
        self.consumers['advanced'] = consumer
        consumer.start()
        
        # 发送大量测试消息
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        print("📤 发送大量测试消息...")
        for i in range(500):
            message = {
                'id': str(uuid.uuid4()),
                'sequence': i,
                'content': f'高级优化测试消息 {i}',
                'data': 'x' * 1000  # 增加消息大小
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='optimized_queue',
                body=json.dumps(message)
            )
        
        connection.close()
        
        # 监控处理过程
        print("📊 监控高级优化过程...")
        for i in range(60):
            time.sleep(2)
            
            metrics = consumer.get_performance_metrics()
            
            # 添加处理器指标
            total_avg_time = statistics.mean([
                p['avg_processing_time'] 
                for p in metrics['processor_stats']
            ])
            
            self.monitor.add_metrics(
                queue_length=metrics['queue_size'],
                throughput=metrics['total_processed'],
                latency_ms=total_avg_time * 1000,
                error_rate=metrics['error_rate']
            )
            
            if i % 5 == 0:  # 每10秒打印一次
                print(f"  处理器数量: {metrics['processor_count']}, "
                      f"处理数: {metrics['total_processed']}, "
                      f"错误率: {metrics['error_rate']:.1f}%")
        
        consumer.stop()
        self.monitor.print_performance_report()
    
    def demo_production_patterns(self):
        """生产环境模式演示"""
        print("\n🏭 生产环境模式演示")
        print("-" * 40)
        
        # 启动系统监控
        self.monitor.start_monitoring()
        
        # 创建多个消费者
        consumers = []
        for i in range(3):
            consumer = OptimizedMessageConsumer(
                queue_name=f'pattern_queue_{i}',
                processor_count=2,
                prefetch_count=30,
                auto_scale=True
            )
            consumers.append(consumer)
            consumer.start()
            self.consumers[f'pattern_{i}'] = consumer
        
        # 发送不同类型的消息
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        print("📤 发送不同类型的消息...")
        
        for i in range(300):
            # 创建不同复杂度的消息
            if i % 3 == 0:
                # 简单消息
                message = {'type': 'simple', 'id': i, 'data': 'x' * 100}
            elif i % 3 == 1:
                # 中等消息
                message = {'type': 'medium', 'id': i, 'data': 'x' * 500}
            else:
                # 复杂消息
                message = {'type': 'complex', 'id': i, 'data': 'x' * 1000}
            
            # 发送到不同队列
            queue_name = f'pattern_queue_{i % 3}'
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message)
            )
        
        connection.close()
        
        # 监控所有消费者
        print("📊 监控生产环境模式...")
        for i in range(45):
            time.sleep(3)
            
            total_processed = 0
            total_errors = 0
            total_queue_size = 0
            
            for consumer in consumers:
                metrics = consumer.get_performance_metrics()
                total_processed += metrics['total_processed']
                total_errors += metrics['total_errors']
                total_queue_size += metrics['queue_size']
            
            total_error_rate = (total_errors / max(1, total_processed + total_errors)) * 100
            
            self.monitor.add_metrics(
                queue_length=total_queue_size,
                throughput=total_processed,
                latency_ms=0,
                error_rate=total_error_rate
            )
            
            if i % 3 == 0:  # 每9秒打印一次
                print(f"  总处理: {total_processed}, 总错误: {total_errors}, "
                      f"总队列: {total_queue_size}")
        
        # 停止所有消费者
        for consumer in consumers:
            consumer.stop()
        
        # 停止监控
        self.monitor.stop_monitoring()
        self.monitor.print_performance_report()
    
    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理资源...")
        
        # 停止所有消费者
        for name, consumer in self.consumers.items():
            try:
                consumer.stop()
            except:
                pass
        
        # 清理队列
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            
            queues_to_clean = [
                'optimized_queue', 'high_priority_queue',
                'pattern_queue_0', 'pattern_queue_1', 'pattern_queue_2',
                'dead_letter_optimized'
            ]
            
            for queue_name in queues_to_clean:
                try:
                    channel.queue_delete(queue=queue_name)
                except:
                    pass
            
            try:
                channel.exchange_delete(exchange='dlx_optimized')
            except:
                pass
            
            connection.close()
            
        except Exception as e:
            print(f"⚠️ 清理过程中出现错误: {e}")
        
        print("✅ 资源清理完成")
    
    def run_comprehensive_demo(self):
        """运行综合演示"""
        print("🏆 消息确认最佳实践和性能优化演示")
        print("=" * 60)
        
        try:
            # 设置队列
            self.setup_optimized_queues()
            
            # 运行各种优化演示
            self.demo_basic_optimization()
            self.demo_advanced_optimization()
            self.demo_production_patterns()
            
            # 生成优化建议
            self.generate_optimization_recommendations()
            
        except KeyboardInterrupt:
            print("\n⏹️ 演示被用户中断")
        except Exception as e:
            print(f"\n❌ 演示执行失败: {e}")
        finally:
            self.cleanup()
    
    def generate_optimization_recommendations(self):
        """生成优化建议"""
        print("\n" + "=" * 60)
        print("💡 消息确认和持久化优化建议")
        print("=" * 60)
        
        recommendations = {
            "性能优化": [
                "使用合理的手动确认模式，提高消息可靠性",
                "根据处理能力调整prefetch_count，避免队列过载",
                "实施批处理确认，减少网络开销",
                "使用持久化队列和消息，但注意性能影响",
                "考虑消息压缩以减少网络传输"
            ],
            "可靠性保证": [
                "启用消息确认机制，避免消息丢失",
                "使用死信队列处理失败消息",
                "实施重试机制和指数退避",
                "监控队列长度和消息积压",
                "设置合理的消息TTL"
            ],
            "扩展性设计": [
                "设计水平扩展的消费模式",
                "使用多队列分发消息",
                "实施动态负载均衡",
                "考虑消息分区和顺序性",
                "监控和自动扩缩容"
            ],
            "运维监控": [
                "监控CPU、内存和网络使用",
                "跟踪消息处理延迟和吞吐量",
                "记录错误率和失败原因",
                "监控队列健康状态",
                "设置告警和通知机制"
            ]
        }
        
        for category, items in recommendations.items():
            print(f"\n📌 {category}:")
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item}")

def main():
    """主函数"""
    print("⚡ 消息确认最佳实践和性能优化演示")
    print("确保RabbitMQ服务正在运行...")
    
    try:
        demo = BestPracticesDemo()
        demo.run_comprehensive_demo()
        
    except Exception as e:
        print(f"\n❌ 演示执行失败: {e}")
        print("请确保:")
        print("1. RabbitMQ服务正在运行")
        print("2. 可以连接到 localhost:5672")
        print("3. 已安装依赖: pip install pika psutil")

if __name__ == "__main__":
    main()