#!/usr/bin/env python3
"""
第8章：队列优化示例
 RabbitMQ 队列性能优化和配置调优工具
"""

import time
import threading
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import logging
import heapq
import uuid


class QueueType(Enum):
    """队列类型"""
    DURABLE = "durable"
    TRANSIENT = "transient"
    QUORUM = "quorum"
    STREAM = "stream"


class MessageTTL(Enum):
    """消息TTL策略"""
    NONE = "none"
    FIXED = "fixed"
    DYNAMIC = "dynamic"


@dataclass
class QueueConfig:
    """队列配置"""
    name: str
    durable: bool = True
    auto_delete: bool = False
    exclusive: bool = False
    max_length: Optional[int] = None
    max_length_bytes: Optional[int] = None
    message_ttl: Optional[int] = None  # 毫秒
    expires: Optional[int] = None      # 毫秒
    dead_letter_exchange: Optional[str] = None
    dead_letter_routing_key: Optional[str] = None
    max_priority: Optional[int] = None
    overflow: str = "reject-publish"  # "reject-publish" 或 "drop-head"
    queue_type: QueueType = QueueType.DURABLE
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class QueueMetrics:
    """队列指标"""
    queue_name: str
    message_count: int
    consumer_count: int
    ready_messages: int
    unacknowledged_messages: int
    durable_messages: int
    transient_messages: int
    rate_in: float
    rate_out: float
    memory_usage_bytes: int
    disk_usage_bytes: int
    timestamp: float


@dataclass
class PerformanceBenchmark:
    """性能基准测试结果"""
    test_name: str
    duration: float
    total_messages: int
    throughput: float
    latency_avg: float
    latency_p95: float
    latency_p99: float
    memory_peak: int
    memory_avg: int
    error_count: int


class QueueOptimizer:
    """队列优化器"""
    
    def __init__(self):
        self.configs = {}
        self.metrics = {}
        self.optimization_strategies = {
            'high_throughput': self._high_throughput_strategy,
            'low_latency': self._low_latency_strategy,
            'low_memory': self._low_memory_strategy,
            'balanced': self._balanced_strategy,
            'reliable': self._reliable_strategy
        }
    
    def generate_optimized_config(self, 
                                queue_name: str,
                                workload_type: str,
                                message_rate: int,
                                avg_message_size: int,
                                consumer_count: int = 1,
                                requirements: Dict[str, Any] = None) -> QueueConfig:
        """生成优化的队列配置"""
        
        strategy = self.optimization_strategies.get(workload_type, self._balanced_strategy)
        base_config = QueueConfig(name=queue_name)
        
        return strategy(base_config, message_rate, avg_message_size, consumer_count, requirements or {})
    
    def _high_throughput_strategy(self, 
                                 config: QueueConfig,
                                 message_rate: int,
                                 avg_message_size: int,
                                 consumer_count: int,
                                 requirements: Dict[str, Any]) -> QueueConfig:
        """高吞吐量优化策略"""
        # 高吞吐量优化：最大化处理能力
        
        # 关闭持久化以提高性能
        config.durable = not requirements.get('require_durability', False)
        
        # 设置队列长度限制以控制内存使用
        if message_rate > 10000:
            config.max_length = message_rate * 60  # 1分钟的消息量
        elif message_rate > 1000:
            config.max_length = message_rate * 30  # 30秒的消息量
        
        # 设置合理的TTL
        if not config.message_ttl:
            config.message_ttl = 300000  # 5分钟
        
        # 禁用自动删除（避免频繁创建删除开销）
        config.auto_delete = False
        
        # 配置arguments
        config.arguments = config.arguments or {}
        config.arguments.update({
            'x-queue-type': QueueType.TRANSIENT.value,
            'x-overflow': 'reject-publish',
            'x-max-priority': 1 if requirements.get('priority_support', False) else None
        })
        
        # 清理None值
        config.arguments = {k: v for k, v in config.arguments.items() if v is not None}
        
        return config
    
    def _low_latency_strategy(self,
                            config: QueueConfig,
                            message_rate: int,
                            avg_message_size: int,
                            consumer_count: int,
                            requirements: Dict[str, Any]) -> QueueConfig:
        """低延迟优化策略"""
        # 低延迟优化：最小化处理延迟
        
        # 使用内存队列（非持久化）
        config.durable = False
        config.auto_delete = False
        
        # 不设置队列长度限制，保证消息不丢失
        config.max_length = None
        
        # 启用优先级支持
        if requirements.get('priority_support', True):
            config.max_priority = 10
        
        # 设置较短TTL
        config.message_ttl = 60000  # 1分钟
        
        # 配置arguments
        config.arguments = config.arguments or {}
        config.arguments.update({
            'x-queue-type': QueueType.TRANSIENT.value,
            'x-max-priority': config.max_priority,
            'x-overflow': 'reject-publish'
        })
        
        return config
    
    def _low_memory_strategy(self,
                           config: QueueConfig,
                           message_rate: int,
                           avg_message_size: int,
                           consumer_count: int,
                           requirements: Dict[str, Any]) -> QueueConfig:
        """低内存优化策略"""
        # 低内存优化：最小化内存占用
        
        # 设置严格的队列长度限制
        if message_rate > 100:
            config.max_length = min(message_rate * 10, 1000)  # 最大1000条消息
        else:
            config.max_length = 100
        
        # 设置队列长度字节限制
        config.max_length_bytes = avg_message_size * config.max_length
        
        # 设置较短TTL
        config.message_ttl = 300000  # 5分钟
        
        # 配置arguments
        config.arguments = config.arguments or {}
        config.arguments.update({
            'x-queue-type': QueueType.TRANSIENT.value,
            'x-overflow': 'drop-head',  # 删除旧消息
            'x-max-length': config.max_length,
            'x-max-length-bytes': config.max_length_bytes
        })
        
        return config
    
    def _balanced_strategy(self,
                         config: QueueConfig,
                         message_rate: int,
                         avg_message_size: int,
                         consumer_count: int,
                         requirements: Dict[str, Any]) -> QueueConfig:
        """平衡优化策略"""
        # 平衡性能与可靠性
        
        # 启用持久化
        config.durable = True
        config.auto_delete = False
        
        # 设置适中的队列长度限制
        config.max_length = message_rate * 60  # 1分钟的消息量
        config.message_ttl = 1800000  # 30分钟
        
        # 启用优先级支持
        if requirements.get('priority_support', False):
            config.max_priority = 5
        
        # 配置arguments
        config.arguments = config.arguments or {}
        config.arguments.update({
            'x-queue-type': QueueType.DURABLE.value,
            'x-overflow': 'reject-publish',
            'x-max-priority': config.max_priority
        })
        
        return config
    
    def _reliable_strategy(self,
                         config: QueueConfig,
                         message_rate: int,
                         avg_message_size: int,
                         consumer_count: int,
                         requirements: Dict[str, Any]) -> QueueConfig:
        """可靠性优化策略"""
        # 可靠性优化：保证消息不丢失
        
        # 强制持久化
        config.durable = True
        config.auto_delete = False
        config.exclusive = False
        
        # 不设置队列长度限制
        config.max_length = None
        
        # 不设置TTL
        config.message_ttl = None
        
        # 设置死信队列
        config.dead_letter_exchange = 'dlx'
        config.dead_letter_routing_key = f"{config.name}.dead"
        
        # 启用优先级支持
        config.max_priority = 8
        
        # 配置arguments
        config.arguments = config.arguments or {}
        config.arguments.update({
            'x-queue-type': QueueType.DURABLE.value,
            'x-dead-letter-exchange': config.dead_letter_exchange,
            'x-dead-letter-routing-key': config.dead_letter_routing_key,
            'x-max-priority': config.max_priority
        })
        
        return config
    
    def analyze_queue_performance(self, metrics_history: List[QueueMetrics]) -> Dict[str, Any]:
        """分析队列性能"""
        if not metrics_history:
            return {}
        
        # 计算平均值和趋势
        total_messages = [m.message_count for m in metrics_history]
        consumer_counts = [m.consumer_count for m in metrics_history]
        rate_ins = [m.rate_in for m in metrics_history]
        rate_outs = [m.rate_out for m in metrics_history]
        
        analysis = {
            'avg_messages': sum(total_messages) / len(total_messages),
            'avg_consumers': sum(consumer_counts) / len(consumer_counts),
            'avg_rate_in': sum(rate_ins) / len(rate_ins),
            'avg_rate_out': sum(rate_outs) / len(rate_outs),
            'throughput_efficiency': sum(rate_outs) / sum(rate_ins) if sum(rate_ins) > 0 else 0,
            'trend': self._calculate_trend([(i, m.message_count) for i, m in enumerate(metrics_history)]),
            'recommendations': self._generate_performance_recommendations(metrics_history)
        }
        
        return analysis
    
    def _calculate_trend(self, data_points: List[tuple]) -> str:
        """计算趋势"""
        if len(data_points) < 2:
            return 'stable'
        
        # 简单线性回归
        n = len(data_points)
        sum_x = sum(x for x, y in data_points)
        sum_y = sum(y for x, y in data_points)
        sum_xy = sum(x * y for x, y in data_points)
        sum_x2 = sum(x * x for x, y in data_points)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _generate_performance_recommendations(self, metrics_history: List[QueueMetrics]) -> List[str]:
        """生成性能建议"""
        recommendations = []
        
        latest_metrics = metrics_history[-1]
        
        # 基于队列长度建议
        if latest_metrics.message_count > 1000:
            recommendations.append("队列消息过多，考虑增加消费者数量或提高处理速度")
        
        if latest_metrics.message_count < 10:
            recommendations.append("队列消息较少，可以减少消费者数量以节省资源")
        
        # 基于消费者效率建议
        if latest_metrics.consumer_count > 0:
            efficiency = latest_metrics.message_count / latest_metrics.consumer_count
            if efficiency > 100:
                recommendations.append("消费者效率较高，可以考虑增加并发处理")
            elif efficiency < 10:
                recommendations.append("消费者效率较低，检查消息处理逻辑")
        
        # 基于速率建议
        if latest_metrics.rate_in > latest_metrics.rate_out * 1.2:
            recommendations.append("消息积压严重，消费者处理速度跟不上生产者")
        
        if latest_metrics.rate_out > latest_metrics.rate_in * 1.2:
            recommendations.append("消费者处理速度快于生产，可以增加生产速率或减少消费者")
        
        # 基于内存使用建议
        if latest_metrics.memory_usage_bytes > 100 * 1024 * 1024:  # 100MB
            recommendations.append("内存使用过高，考虑设置队列长度限制或TTL")
        
        return recommendations


class QueueBenchmarker:
    """队列基准测试器"""
    
    def __init__(self):
        self.test_results = []
        self.concurrent_tests = []
    
    def run_basic_benchmark(self,
                          queue_config: QueueConfig,
                          message_count: int = 1000,
                          message_size: int = 1024,
                          consumer_count: int = 1,
                          message_rate: int = 100) -> PerformanceBenchmark:
        """运行基础基准测试"""
        print(f"开始基础队列基准测试:")
        print(f"  队列: {queue_config.name}")
        print(f"  消息数: {message_count}")
        print(f"  消息大小: {message_size}字节")
        print(f"  消费者数: {consumer_count}")
        print(f"  生产速率: {message_rate}/秒")
        print()
        
        start_time = time.time()
        messages_produced = 0
        messages_consumed = 0
        latencies = []
        memory_usage = []
        error_count = 0
        
        # 模拟消息生产者
        def producer():
            nonlocal messages_produced
            message_data = "x" * message_size
            
            for i in range(message_count):
                try:
                    send_time = time.time()
                    
                    # 模拟消息发送
                    self._simulate_send_message(queue_config, message_data)
                    
                    messages_produced += 1
                    
                    # 模拟发送延迟
                    if message_rate > 0:
                        time.sleep(1.0 / message_rate)
                
                except Exception as e:
                    nonlocal error_count
                    error_count += 1
                    print(f"生产消息错误: {e}")
        
        # 模拟消息消费者
        def consumer(consumer_id: int):
            nonlocal messages_consumed, latencies
            consumer_start = time.time()
            
            while (messages_consumed < message_count or 
                   time.time() - consumer_start < 30):  # 最多等待30秒
                try:
                    receive_time = time.time()
                    
                    # 模拟接收消息
                    message = self._simulate_receive_message(queue_config)
                    
                    if message:
                        messages_consumed += 1
                        
                        # 计算延迟（模拟）
                        latency = time.time() - receive_time
                        latencies.append(latency)
                
                except Exception as e:
                    error_count += 1
                    print(f"消费者{consumer_id}处理消息错误: {e}")
                
                time.sleep(0.001)  # 1ms处理间隔
        
        # 启动线程
        threads = []
        
        # 启动生产者
        producer_thread = threading.Thread(target=producer)
        threads.append(producer_thread)
        producer_thread.start()
        
        # 启动消费者
        for i in range(consumer_count):
            consumer_thread = threading.Thread(target=consumer, args=(i,))
            threads.append(consumer_thread)
            consumer_thread.start()
        
        # 等待所有线程完成
        producer_thread.join()
        for thread in threads[1:]:
            thread.join()
        
        # 计算结果
        end_time = time.time()
        duration = end_time - start_time
        throughput = messages_consumed / duration
        
        # 计算延迟统计
        if latencies:
            latencies.sort()
            p95_idx = int(len(latencies) * 0.95)
            p99_idx = int(len(latencies) * 0.99)
            
            latency_avg = sum(latencies) / len(latencies)
            latency_p95 = latencies[p95_idx]
            latency_p99 = latencies[p99_idx]
        else:
            latency_avg = latency_p95 = latency_p99 = 0
        
        # 模拟内存使用
        memory_peak = queue_config.max_length_bytes or 1024 * 1024
        memory_avg = memory_peak // 2
        
        result = PerformanceBenchmark(
            test_name=f"basic_{queue_config.name}",
            duration=duration,
            total_messages=messages_consumed,
            throughput=throughput,
            latency_avg=latency_avg,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            memory_peak=memory_peak,
            memory_avg=memory_avg,
            error_count=error_count
        )
        
        # 输出结果
        print("✅ 基础基准测试完成:")
        print(f"  总耗时: {duration:.2f}秒")
        print(f"  处理消息: {messages_consumed}")
        print(f"  吞吐量: {throughput:.2f}消息/秒")
        print(f"  平均延迟: {latency_avg:.4f}秒")
        print(f"  95%延迟: {latency_p95:.4f}秒")
        print(f"  99%延迟: {latency_p99:.4f}秒")
        print(f"  内存峰值: {memory_peak / 1024 / 1024:.1f}MB")
        print(f"  错误数: {error_count}")
        print()
        
        self.test_results.append(result)
        return result
    
    def _simulate_send_message(self, queue_config: QueueConfig, message_data: str) -> str:
        """模拟发送消息"""
        # 这里是模拟实现，实际应该连接RabbitMQ
        message_id = str(uuid.uuid4())
        
        # 模拟消息大小检查
        if queue_config.max_length_bytes and len(message_data) > queue_config.max_length_bytes:
            raise Exception("消息大小超过限制")
        
        return message_id
    
    def _simulate_receive_message(self, queue_config: QueueConfig) -> Optional[Dict[str, Any]]:
        """模拟接收消息"""
        # 这里是模拟实现
        import random
        
        # 模拟消息接收
        if random.random() < 0.1:  # 10%的概率接收不到消息
            return None
        
        return {
            'id': str(uuid.uuid4()),
            'data': "x" * 1024,
            'timestamp': time.time()
        }
    
    def run_stress_test(self,
                      queue_config: QueueConfig,
                      stress_duration: int = 60,
                      ramp_up_time: int = 10) -> PerformanceBenchmark:
        """运行压力测试"""
        print(f"开始压力测试:")
        print(f"  队列: {queue_config.name}")
        print(f"  测试时长: {stress_duration}秒")
        print(f"  预热时间: {ramp_up_time}秒")
        print()
        
        start_time = time.time()
        messages_produced = 0
        messages_consumed = 0
        latencies = []
        error_count = 0
        
        # 压力测试参数
        high_message_rate = 1000  # 高速率
        consumer_count = 10  # 10个消费者
        
        def stress_producer():
            nonlocal messages_produced
            
            ramp_end = start_time + ramp_up_time
            test_end = start_time + stress_duration
            
            while time.time() < test_end:
                try:
                    # 预热期间使用较低速率
                    current_rate = high_message_rate if time.time() >= ramp_end else high_message_rate // 4
                    
                    message_data = "stress_test_message" * 100  # 大消息
                    self._simulate_send_message(queue_config, message_data)
                    messages_produced += 1
                    
                    # 控制发送速率
                    if current_rate > 0:
                        time.sleep(1.0 / current_rate)
                
                except Exception as e:
                    error_count += 1
                    if error_count < 10:  # 只打印前10个错误
                        print(f"压力测试生产错误: {e}")
        
        def stress_consumer():
            nonlocal messages_consumed
            
            test_end = start_time + stress_duration
            
            while time.time() < test_end:
                try:
                    message = self._simulate_receive_message(queue_config)
                    
                    if message:
                        messages_consumed += 1
                        latency = time.time() - message.get('timestamp', time.time())
                        latencies.append(latency)
                
                except Exception as e:
                    error_count += 1
                    if error_count < 10:
                        print(f"压力测试消费错误: {e}")
                
                time.sleep(0.001)  # 1ms处理间隔
        
        # 启动压力测试线程
        threads = []
        
        # 启动多个生产者
        for i in range(3):
            producer_thread = threading.Thread(target=stress_producer)
            threads.append(producer_thread)
            producer_thread.start()
        
        # 启动多个消费者
        for i in range(consumer_count):
            consumer_thread = threading.Thread(target=stress_consumer)
            threads.append(consumer_thread)
            consumer_thread.start()
        
        # 等待测试完成
        for thread in threads:
            thread.join()
        
        # 计算结果
        end_time = time.time()
        duration = end_time - start_time
        throughput = messages_consumed / duration
        
        # 延迟统计
        if latencies:
            latencies.sort()
            p95_idx = int(len(latencies) * 0.95)
            p99_idx = int(len(latencies) * 0.99)
            
            latency_avg = sum(latencies) / len(latencies)
            latency_p95 = latencies[p95_idx]
            latency_p99 = latencies[p99_idx]
        else:
            latency_avg = latency_p95 = latency_p99 = 0
        
        result = PerformanceBenchmark(
            test_name=f"stress_{queue_config.name}",
            duration=duration,
            total_messages=messages_consumed,
            throughput=throughput,
            latency_avg=latency_avg,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            memory_peak=50 * 1024 * 1024,  # 50MB
            memory_avg=30 * 1024 * 1024,   # 30MB
            error_count=error_count
        )
        
        print("✅ 压力测试完成:")
        print(f"  总耗时: {duration:.2f}秒")
        print(f"  处理消息: {messages_consumed}")
        print(f"  吞吐量: {throughput:.2f}消息/秒")
        print(f"  平均延迟: {latency_avg:.4f}秒")
        print(f"  95%延迟: {latency_p95:.4f}秒")
        print(f"  99%延迟: {latency_p99:.4f}秒")
        print(f"  错误数: {error_count}")
        print()
        
        self.test_results.append(result)
        return result
    
    def run_concurrent_benchmark(self,
                               queue_configs: List[QueueConfig],
                               total_messages: int = 1000,
                               message_size: int = 1024) -> Dict[str, PerformanceBenchmark]:
        """运行并发队列基准测试"""
        print(f"开始并发队列基准测试:")
        print(f"  队列数量: {len(queue_configs)}")
        print(f"  总消息数: {total_messages}")
        print(f"  消息大小: {message_size}字节")
        print()
        
        results = {}
        
        def concurrent_producer_consumer(queue_config: QueueConfig, queue_index: int):
            queue_messages = total_messages // len(queue_configs)
            messages_consumed = 0
            latencies = []
            
            # 生产消息
            for i in range(queue_messages):
                try:
                    message_data = f"concurrent_message_{queue_index}_{i}" * (message_size // 50)
                    self._simulate_send_message(queue_config, message_data)
                except Exception as e:
                    print(f"队列{queue_index}生产错误: {e}")
            
            # 消费消息
            while messages_consumed < queue_messages:
                try:
                    message = self._simulate_receive_message(queue_config)
                    if message:
                        messages_consumed += 1
                        latency = time.time() - message.get('timestamp', time.time())
                        latencies.append(latency)
                except Exception as e:
                    print(f"队列{queue_index}消费错误: {e}")
                
                time.sleep(0.001)
            
            # 计算队列性能
            if latencies:
                latencies.sort()
                latency_avg = sum(latencies) / len(latencies)
                latency_p95 = latencies[int(len(latencies) * 0.95)]
                latency_p99 = latencies[int(len(latencies) * 0.99)]
            else:
                latency_avg = latency_p95 = latency_p99 = 0
            
            result = PerformanceBenchmark(
                test_name=f"concurrent_{queue_config.name}",
                duration=30.0,  # 模拟30秒
                total_messages=messages_consumed,
                throughput=messages_consumed / 30.0,
                latency_avg=latency_avg,
                latency_p95=latency_p95,
                latency_p99=latency_p99,
                memory_peak=10 * 1024 * 1024,  # 10MB
                memory_avg=5 * 1024 * 1024,    # 5MB
                error_count=0
            )
            
            results[queue_config.name] = result
        
        # 启动并发测试
        threads = []
        for i, config in enumerate(queue_configs):
            thread = threading.Thread(target=concurrent_producer_consumer, args=(config, i))
            threads.append(thread)
            thread.start()
        
        # 等待所有队列完成
        for thread in threads:
            thread.join()
        
        # 输出结果
        print("✅ 并发队列基准测试完成:")
        for queue_name, result in results.items():
            print(f"  {queue_name}:")
            print(f"    吞吐量: {result.throughput:.2f}消息/秒")
            print(f"    平均延迟: {result.latency_avg:.4f}秒")
            print(f"    95%延迟: {result.latency_p95:.4f}秒")
        print()
        
        return results


class QueuePerformanceAnalyzer:
    """队列性能分析器"""
    
    def __init__(self):
        self.historical_data = defaultdict(list)
        self.alerts = []
    
    def analyze_benchmark_results(self, results: List[PerformanceBenchmark]) -> Dict[str, Any]:
        """分析基准测试结果"""
        if not results:
            return {}
        
        analysis = {
            'summary': {
                'total_tests': len(results),
                'avg_throughput': sum(r.throughput for r in results) / len(results),
                'avg_latency': sum(r.latency_avg for r in results) / len(results),
                'total_messages': sum(r.total_messages for r in results),
                'total_errors': sum(r.error_count for r in results)
            },
            'performance_comparison': {},
            'recommendations': []
        }
        
        # 性能对比
        best_throughput = max(results, key=lambda r: r.throughput)
        best_latency = min(results, key=lambda r: r.latency_avg)
        worst_throughput = min(results, key=lambda r: r.throughput)
        worst_latency = max(results, key=lambda r: r.latency_avg)
        
        analysis['performance_comparison'] = {
            'best_throughput': {
                'test': best_throughput.test_name,
                'value': best_throughput.throughput
            },
            'best_latency': {
                'test': best_latency.test_name,
                'value': best_latency.latency_avg
            },
            'worst_throughput': {
                'test': worst_throughput.test_name,
                'value': worst_throughput.throughput
            },
            'worst_latency': {
                'test': worst_latency.test_name,
                'value': worst_latency.latency_avg
            }
        }
        
        # 生成建议
        analysis['recommendations'] = self._generate_optimization_recommendations(results)
        
        return analysis
    
    def _generate_optimization_recommendations(self, results: List[PerformanceBenchmark]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于吞吐量分析
        throughputs = [r.throughput for r in results]
        avg_throughput = sum(throughputs) / len(throughputs)
        min_throughput = min(throughputs)
        
        if min_throughput < avg_throughput * 0.5:
            recommendations.append("存在性能瓶颈队列，需要重点优化")
        
        # 基于延迟分析
        latencies = [r.latency_avg for r in results]
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        if max_latency > avg_latency * 2:
            recommendations.append("存在高延迟队列，建议检查队列配置和处理逻辑")
        
        # 基于错误率分析
        for result in results:
            error_rate = result.error_count / result.total_messages if result.total_messages > 0 else 0
            if error_rate > 0.01:  # 1%错误率
                recommendations.append(f"测试{result.test_name}错误率过高，需要检查错误处理")
        
        # 基于内存使用分析
        memory_peaks = [r.memory_peak for r in results]
        avg_memory = sum(memory_peaks) / len(memory_peaks)
        max_memory = max(memory_peaks)
        
        if max_memory > avg_memory * 2:
            recommendations.append("内存使用不均衡，建议优化大内存队列的配置")
        
        if avg_memory > 100 * 1024 * 1024:  # 100MB
            recommendations.append("平均内存使用过高，建议启用消息TTL或队列长度限制")
        
        return recommendations
    
    def generate_performance_report(self, analysis: Dict[str, Any]) -> str:
        """生成性能报告"""
        report = []
        report.append("# RabbitMQ 队列性能分析报告")
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 测试概述
        summary = analysis.get('summary', {})
        report.append("\n## 测试概述")
        report.append(f"- 总测试数量: {summary.get('total_tests', 0)}")
        report.append(f"- 平均吞吐量: {summary.get('avg_throughput', 0):.2f} 消息/秒")
        report.append(f"- 平均延迟: {summary.get('avg_latency', 0):.4f} 秒")
        report.append(f"- 总处理消息: {summary.get('total_messages', 0)}")
        report.append(f"- 总错误数: {summary.get('total_errors', 0)}")
        
        # 性能对比
        comparison = analysis.get('performance_comparison', {})
        if comparison:
            report.append("\n## 性能对比")
            report.append(f"- 最佳吞吐量: {comparison.get('best_throughput', {}).get('value', 0):.2f} 消息/秒 ({comparison.get('best_throughput', {}).get('test', 'unknown')})")
            report.append(f"- 最佳延迟: {comparison.get('best_latency', {}).get('value', 0):.4f} 秒 ({comparison.get('best_latency', {}).get('test', 'unknown')})")
            report.append(f"- 最差吞吐量: {comparison.get('worst_throughput', {}).get('value', 0):.2f} 消息/秒 ({comparison.get('worst_throughput', {}).get('test', 'unknown')})")
            report.append(f"- 最差延迟: {comparison.get('worst_latency', {}).get('value', 0):.4f} 秒 ({comparison.get('worst_latency', {}).get('test', 'unknown')})")
        
        # 优化建议
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            report.append("\n## 优化建议")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
        
        report.append("\n## 总结")
        report.append("基于以上分析，建议按照优先级实施优化措施，持续监控系统性能。")
        
        return "\n".join(report)


class QueueOptimizationDemo:
    """队列优化演示"""
    
    def __init__(self):
        self.optimizer = QueueOptimizer()
        self.benchmarker = QueueBenchmarker()
        self.analyzer = QueuePerformanceAnalyzer()
    
    def demonstrate_optimization_strategies(self):
        """演示不同的优化策略"""
        print("=== 队列优化策略演示 ===")
        print()
        
        # 不同工作负载类型的优化配置
        test_configs = [
            {
                'name': 'high_throughput_queue',
                'type': 'high_throughput',
                'message_rate': 5000,
                'avg_message_size': 1024,
                'consumer_count': 10
            },
            {
                'name': 'low_latency_queue',
                'type': 'low_latency',
                'message_rate': 100,
                'avg_message_size': 512,
                'consumer_count': 5
            },
            {
                'name': 'low_memory_queue',
                'type': 'low_memory',
                'message_rate': 1000,
                'avg_message_size': 2048,
                'consumer_count': 3
            },
            {
                'name': 'balanced_queue',
                'type': 'balanced',
                'message_rate': 2000,
                'avg_message_size': 1024,
                'consumer_count': 5
            }
        ]
        
        optimized_configs = {}
        
        for config in test_configs:
            print(f"生成{config['type']}策略配置:")
            
            # 生成优化配置
            optimized_config = self.optimizer.generate_optimized_config(
                queue_name=config['name'],
                workload_type=config['type'],
                message_rate=config['message_rate'],
                avg_message_size=config['avg_message_size'],
                consumer_count=config['consumer_count'],
                requirements={
                    'require_durability': config['type'] in ['balanced', 'reliable'],
                    'priority_support': True
                }
            )
            
            optimized_configs[config['name']] = optimized_config
            
            # 显示配置详情
            print(f"  队列名: {optimized_config.name}")
            print(f"  持久化: {optimized_config.durable}")
            print(f"  最大长度: {optimized_config.max_length}")
            print(f"  消息TTL: {optimized_config.message_ttl}ms")
            print(f"  优先级: {optimized_config.max_priority}")
            print(f"  参数: {optimized_config.arguments}")
            print()
        
        return optimized_configs
    
    def demonstrate_performance_testing(self, configs: Dict[str, QueueConfig]):
        """演示性能测试"""
        print("=== 队列性能测试演示 ===")
        print()
        
        all_results = []
        
        # 对每个配置运行基准测试
        for config_name, config in configs.items():
            print(f"测试队列配置: {config_name}")
            print("-" * 40)
            
            # 基础性能测试
            result = self.benchmarker.run_basic_benchmark(
                queue_config=config,
                message_count=500,  # 较少的消息用于演示
                message_size=1024,
                consumer_count=3,
                message_rate=100
            )
            all_results.append(result)
            
            print()
        
        # 分析测试结果
        print("=== 性能测试结果分析 ===")
        analysis = self.analyzer.analyze_benchmark_results(all_results)
        
        # 输出分析结果
        summary = analysis.get('summary', {})
        print("📊 测试总结:")
        print(f"  平均吞吐量: {summary.get('avg_throughput', 0):.2f} 消息/秒")
        print(f"  平均延迟: {summary.get('avg_latency', 0):.4f} 秒")
        print(f"  总处理消息: {summary.get('total_messages', 0)}")
        
        comparison = analysis.get('performance_comparison', {})
        if comparison:
            print(f"  最佳吞吐量: {comparison.get('best_throughput', {}).get('value', 0):.2f} 消息/秒")
            print(f"  最佳延迟: {comparison.get('best_latency', {}).get('value', 0):.4f} 秒")
        
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print("💡 优化建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print()
        
        return analysis
    
    def demonstrate_stress_testing(self):
        """演示压力测试"""
        print("=== 压力测试演示 ===")
        print()
        
        # 创建压力测试配置
        stress_config = QueueConfig(
            name="stress_test_queue",
            durable=True,
            max_length=10000,  # 限制队列长度
            message_ttl=300000,  # 5分钟TTL
            overflow="reject-publish"
        )
        
        # 运行压力测试
        result = self.benchmarker.run_stress_test(
            queue_config=stress_config,
            stress_duration=30,  # 30秒压力测试
            ramp_up_time=5      # 5秒预热
        )
        
        print("✅ 压力测试完成")
        print()
        
        return result
    
    def demonstrate_concurrent_testing(self):
        """演示并发测试"""
        print("=== 并发队列测试演示 ===")
        print()
        
        # 创建多个队列配置
        queue_configs = [
            QueueConfig("concurrent_queue_1", max_length=5000),
            QueueConfig("concurrent_queue_2", max_length=3000),
            QueueConfig("concurrent_queue_3", max_length=2000),
        ]
        
        # 运行并发测试
        results = self.benchmarker.run_concurrent_benchmark(
            queue_configs=queue_configs,
            total_messages=3000,  # 每个队列1000条消息
            message_size=512
        )
        
        print("✅ 并发测试完成")
        print()
        
        return results
    
    def demonstrate_performance_analysis(self, test_results: List[PerformanceBenchmark]):
        """演示性能分析"""
        print("=== 性能分析演示 ===")
        print()
        
        if not test_results:
            print("没有测试结果可分析")
            return
        
        # 生成性能报告
        analysis = self.analyzer.analyze_benchmark_results(test_results)
        report = self.analyzer.generate_performance_report(analysis)
        
        print("📄 性能报告:")
        print(report)
        print()
        
        # 输出建议的队列配置
        print("💡 推荐的高性能队列配置:")
        
        high_throughput_config = self.optimizer.generate_optimized_config(
            queue_name="recommended_high_throughput",
            workload_type="high_throughput",
            message_rate=10000,
            avg_message_size=1024,
            consumer_count=20
        )
        
        print("高吞吐量配置:")
        print(f"  durable: {high_throughput_config.durable}")
        print(f"  max_length: {high_throughput_config.max_length}")
        print(f"  message_ttl: {high_throughput_config.message_ttl}")
        print(f"  arguments: {high_throughput_config.arguments}")
        
        low_latency_config = self.optimizer.generate_optimized_config(
            queue_name="recommended_low_latency",
            workload_type="low_latency",
            message_rate=500,
            avg_message_size=512,
            consumer_count=10
        )
        
        print("\n低延迟配置:")
        print(f"  durable: {low_latency_config.durable}")
        print(f"  max_length: {low_latency_config.max_length}")
        print(f"  max_priority: {low_latency_config.max_priority}")
        print(f"  arguments: {low_latency_config.arguments}")
        
        print()


if __name__ == "__main__":
    # 运行队列优化演示
    demo = QueueOptimizationDemo()
    
    print("🚀 RabbitMQ 队列优化与调优系统")
    print("=" * 50)
    print()
    
    try:
        # 1. 演示优化策略
        configs = demo.demonstrate_optimization_strategies()
        
        # 2. 演示性能测试
        analysis = demo.demonstrate_performance_testing(configs)
        
        # 3. 演示压力测试
        stress_result = demo.demonstrate_stress_testing()
        
        # 4. 演示并发测试
        concurrent_results = demo.demonstrate_concurrent_testing()
        
        # 5. 演示性能分析
        test_results = demo.benchmarker.test_results
        demo.demonstrate_performance_analysis(test_results)
        
        print("🎉 队列优化演示完成!")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序执行错误: {e}")
        import traceback
        traceback.print_exc()