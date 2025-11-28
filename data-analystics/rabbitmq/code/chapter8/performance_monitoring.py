#!/usr/bin/env python3
"""
第8章：性能监控与调优示例
 RabbitMQ 性能监控、基准测试和实时调优工具
"""

import time
import threading
import json
import asyncio
import statistics
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import heapq
import time
import threading
from collections import deque, defaultdict
import logging


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: float
    level: AlertLevel
    description: str
    enabled: bool = True


@dataclass
class Alert:
    """告警"""
    rule_name: str
    metric_name: str
    value: float
    threshold: float
    level: AlertLevel
    message: str
    timestamp: float
    resolved: bool = False


class PerformanceCounter:
    """性能计数器"""
    
    def __init__(self, name: str):
        self.name = name
        self.value = 0
        self._lock = threading.Lock()
    
    def increment(self, amount: float = 1):
        """增加计数器"""
        with self._lock:
            self.value += amount
    
    def decrement(self, amount: float = 1):
        """减少计数器"""
        with self._lock:
            self.value -= amount
    
    def reset(self):
        """重置计数器"""
        with self._lock:
            self.value = 0
    
    def get_value(self) -> float:
        """获取当前值"""
        with self._lock:
            return self.value


class PerformanceGauge:
    """性能仪表"""
    
    def __init__(self, name: str):
        self.name = name
        self.value = 0.0
        self._lock = threading.Lock()
    
    def set(self, value: float):
        """设置值"""
        with self._lock:
            self.value = value
    
    def get_value(self) -> float:
        """获取当前值"""
        with self._lock:
            return self.value


class PerformanceHistogram:
    """性能直方图"""
    
    def __init__(self, name: str, buckets: List[float] = None):
        self.name = name
        self.count = 0
        self.sum = 0.0
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        self.bucket_counts = {bucket: 0 for bucket in self.buckets}
        self.max_value = 0.0
        self._lock = threading.Lock()
    
    def observe(self, value: float):
        """记录观测值"""
        with self._lock:
            self.count += 1
            self.sum += value
            self.max_value = max(self.max_value, value)
            
            # 更新桶计数
            for bucket in self.buckets:
                if value <= bucket:
                    self.bucket_counts[bucket] += 1
    
    def get_quantile(self, quantile: float) -> float:
        """获取分位数"""
        with self._lock:
            if self.count == 0:
                return 0.0
            
            # 简化实现，返回百分位数
            sorted_values = []
            # 这里应该有完整的数据点存储，简化处理
            if quantile <= 0.5:
                return self.max_value * quantile * 2
            else:
                return self.max_value
    
    def get_stats(self) -> Dict[str, float]:
        """获取统计信息"""
        with self._lock:
            if self.count == 0:
                return {
                    'count': 0,
                    'sum': 0.0,
                    'avg': 0.0,
                    'max': 0.0
                }
            
            return {
                'count': self.count,
                'sum': self.sum,
                'avg': self.sum / self.count,
                'max': self.max_value
            }


class PerformanceTimer:
    """性能计时器"""
    
    def __init__(self, name: str):
        self.name = name
        self.histogram = PerformanceHistogram(name)
        self._lock = threading.Lock()
    
    def time_function(self, func: Callable, *args, **kwargs):
        """计时执行函数"""
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            self.histogram.observe(elapsed)
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            self.histogram.observe(elapsed)
            raise e
    
    def time_context(self):
        """上下文管理器计时"""
        return TimerContext(self.histogram)


class TimerContext:
    """计时上下文管理器"""
    
    def __init__(self, histogram: PerformanceHistogram):
        self.histogram = histogram
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start_time
        self.histogram.observe(elapsed)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.timers = {}
        self._lock = threading.Lock()
        
        # 实时数据
        self.current_metrics = {}
        self.metric_history = defaultdict(deque)
        
    def get_counter(self, name: str) -> PerformanceCounter:
        """获取或创建计数器"""
        with self._lock:
            if name not in self.counters:
                self.counters[name] = PerformanceCounter(name)
            return self.counters[name]
    
    def get_gauge(self, name: str) -> PerformanceGauge:
        """获取或创建仪表"""
        with self._lock:
            if name not in self.gauges:
                self.gauges[name] = PerformanceGauge(name)
            return self.gauges[name]
    
    def get_histogram(self, name: str, buckets: List[float] = None) -> PerformanceHistogram:
        """获取或创建直方图"""
        with self._lock:
            if name not in self.histograms:
                self.histograms[name] = PerformanceHistogram(name, buckets)
            return self.histograms[name]
    
    def get_timer(self, name: str) -> PerformanceTimer:
        """获取或创建计时器"""
        with self._lock:
            if name not in self.timers:
                self.timers[name] = PerformanceTimer(name)
            return self.timers[name]
    
    def record_metric(self, metric: PerformanceMetric):
        """记录指标"""
        with self._lock:
            self.current_metrics[metric.name] = metric
            # 保持历史数据（最近100个数据点）
            history = self.metric_history[metric.name]
            history.append(metric)
            if len(history) > 100:
                history.popleft()
    
    def get_current_metrics(self) -> Dict[str, PerformanceMetric]:
        """获取当前指标"""
        with self._lock:
            return self.current_metrics.copy()
    
    def get_metric_history(self, name: str, limit: int = 100) -> List[PerformanceMetric]:
        """获取指标历史"""
        with self._lock:
            history = self.metric_history[name]
            return list(history)[-limit:]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有统计信息"""
        stats = {}
        
        with self._lock:
            # 计数器统计
            for name, counter in self.counters.items():
                stats[name] = {
                    'type': 'counter',
                    'value': counter.get_value()
                }
            
            # 仪表统计
            for name, gauge in self.gauges.items():
                stats[name] = {
                    'type': 'gauge',
                    'value': gauge.get_value()
                }
            
            # 直方图统计
            for name, histogram in self.histograms.items():
                stats[name] = {
                    'type': 'histogram',
                    'stats': histogram.get_stats()
                }
            
            # 计时器统计
            for name, timer in self.timers.items():
                stats[name] = {
                    'type': 'timer',
                    'stats': timer.histogram.get_stats()
                }
        
        return stats


class AlertEngine:
    """告警引擎"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self._lock = threading.Lock()
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        with self._lock:
            self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        with self._lock:
            self.rules = [r for r in self.rules if r.name != rule_name]
    
    def evaluate_rules(self, metrics: Dict[str, PerformanceMetric]) -> List[Alert]:
        """评估告警规则"""
        new_alerts = []
        
        with self._lock:
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                if rule.metric_name not in metrics:
                    continue
                
                metric_value = metrics[rule.metric_name].value
                triggered = False
                
                if rule.condition == ">" and metric_value > rule.threshold:
                    triggered = True
                elif rule.condition == "<" and metric_value < rule.threshold:
                    triggered = True
                elif rule.condition == ">=" and metric_value >= rule.threshold:
                    triggered = True
                elif rule.condition == "<=" and metric_value <= rule.threshold:
                    triggered = True
                elif rule.condition == "==" and metric_value == rule.threshold:
                    triggered = True
                elif rule.condition == "!=" and metric_value != rule.threshold:
                    triggered = True
                
                if triggered:
                    alert = Alert(
                        rule_name=rule.name,
                        metric_name=rule.metric_name,
                        value=metric_value,
                        threshold=rule.threshold,
                        level=rule.level,
                        message=f"{rule.name}: {rule.metric_name} {rule.condition} {rule.threshold}, 当前值: {metric_value}",
                        timestamp=time.time(),
                        resolved=False
                    )
                    new_alerts.append(alert)
        
        # 添加到告警列表
        if new_alerts:
            with self._lock:
                self.active_alerts.extend(new_alerts)
                self.alert_history.extend(new_alerts)
        
        return new_alerts
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        with self._lock:
            for alert in self.active_alerts:
                if alert.rule_name == alert_id:
                    alert.resolved = True
            self.active_alerts = [a for a in self.active_alerts if not a.resolved]
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        with self._lock:
            return [a for a in self.active_alerts if not a.resolved]


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.collector = MetricsCollector()
        self.alert_engine = AlertEngine()
        self.monitoring = False
        self.monitor_thread = None
        
        # 监控回调函数
        self.monitor_callbacks = []
        
        # 默认告警规则
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                metric_name="system.cpu.usage",
                condition=">",
                threshold=80.0,
                level=AlertLevel.WARNING,
                description="CPU使用率过高"
            ),
            AlertRule(
                name="high_memory_usage",
                metric_name="system.memory.usage_percent",
                condition=">",
                threshold=85.0,
                level=AlertLevel.WARNING,
                description="内存使用率过高"
            ),
            AlertRule(
                name="slow_message_processing",
                metric_name="rabbitmq.message.process_time",
                condition=">",
                threshold=1.0,
                level=AlertLevel.WARNING,
                description="消息处理时间过长"
            ),
            AlertRule(
                name="high_queue_length",
                metric_name="rabbitmq.queue.length",
                condition=">",
                threshold=1000,
                level=AlertLevel.CRITICAL,
                description="队列长度过高"
            )
        ]
        
        for rule in default_rules:
            self.alert_engine.add_rule(rule)
    
    def add_monitor_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """添加监控回调函数"""
        self.monitor_callbacks.append(callback)
    
    def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 收集系统指标
                self._collect_system_metrics()
                
                # 收集应用指标
                self._collect_application_metrics()
                
                # 评估告警规则
                current_metrics = self.collector.get_current_metrics()
                alerts = self.alert_engine.evaluate_rules(current_metrics)
                
                # 触发回调函数
                if self.monitor_callbacks:
                    monitor_data = {
                        'timestamp': time.time(),
                        'metrics': current_metrics,
                        'alerts': alerts,
                        'stats': self.collector.get_all_stats()
                    }
                    
                    for callback in self.monitor_callbacks:
                        try:
                            callback(monitor_data)
                        except Exception as e:
                            logging.error(f"监控回调执行失败: {e}")
                
                time.sleep(self.interval)
                
            except Exception as e:
                logging.error(f"监控循环错误: {e}")
                time.sleep(self.interval)
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.collector.record_metric(PerformanceMetric(
                name="system.cpu.usage",
                value=cpu_percent,
                metric_type=MetricType.GAUGE,
                timestamp=time.time(),
                tags={"component": "system"}
            ))
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self.collector.record_metric(PerformanceMetric(
                name="system.memory.usage_percent",
                value=memory.percent,
                metric_type=MetricType.GAUGE,
                timestamp=time.time(),
                tags={"component": "system"}
            ))
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.collector.record_metric(PerformanceMetric(
                name="system.disk.usage_percent",
                value=disk_percent,
                metric_type=MetricType.GAUGE,
                timestamp=time.time(),
                tags={"component": "system"}
            ))
            
            # 网络I/O
            net_io = psutil.net_io_counters()
            if net_io:
                self.collector.record_metric(PerformanceMetric(
                    name="system.network.bytes_sent",
                    value=net_io.bytes_sent,
                    metric_type=MetricType.COUNTER,
                    timestamp=time.time(),
                    tags={"component": "system"}
                ))
                
                self.collector.record_metric(PerformanceMetric(
                    name="system.network.bytes_recv",
                    value=net_io.bytes_recv,
                    metric_type=MetricType.COUNTER,
                    timestamp=time.time(),
                    tags={"component": "system"}
                ))
        
        except ImportError:
            # 如果没有psutil，生成模拟数据
            import random
            self.collector.record_metric(PerformanceMetric(
                name="system.cpu.usage",
                value=random.uniform(20, 80),
                metric_type=MetricType.GAUGE,
                timestamp=time.time(),
                tags={"component": "system"}
            ))
    
    def _collect_application_metrics(self):
        """收集应用指标"""
        # 这里应该收集RabbitMQ相关指标
        # 简化实现，生成模拟数据
        
        import random
        
        # 消息处理时间
        process_time = random.uniform(0.1, 2.0)
        self.collector.record_metric(PerformanceMetric(
            name="rabbitmq.message.process_time",
            value=process_time,
            metric_type=MetricType.TIMER,
            timestamp=time.time(),
            tags={"component": "rabbitmq"}
        ))
        
        # 队列长度
        queue_length = random.randint(100, 2000)
        self.collector.record_metric(PerformanceMetric(
            name="rabbitmq.queue.length",
            value=queue_length,
            metric_type=MetricType.GAUGE,
            timestamp=time.time(),
            tags={"component": "rabbitmq"}
        ))
        
        # 连接数
        connection_count = random.randint(10, 100)
        self.collector.record_metric(PerformanceMetric(
            name="rabbitmq.connections.count",
            value=connection_count,
            metric_type=MetricType.GAUGE,
            timestamp=time.time(),
            tags={"component": "rabbitmq"}
        ))


class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.results = {}
    
    def run_throughput_benchmark(self, duration: int = 60, message_size: int = 1024) -> Dict[str, Any]:
        """运行吞吐量基准测试"""
        print(f"开始吞吐量基准测试，持续时间: {duration}秒，消息大小: {message_size}字节")
        
        start_time = time.time()
        message_count = 0
        timer = self.monitor.collector.get_timer("benchmark.throughput")
        
        # 生成并处理消息的模拟函数
        def process_message():
            nonlocal message_count
            # 模拟消息处理
            time.sleep(0.001)  # 1ms处理时间
            with timer.time_context():
                # 模拟消息处理工作
                data = "x" * message_size
                processed_data = data.upper()
                message_count += 1
                return processed_data
        
        # 运行基准测试
        end_time = start_time + duration
        while time.time() < end_time:
            try:
                process_message()
            except Exception as e:
                print(f"消息处理错误: {e}")
        
        total_time = time.time() - start_time
        throughput = message_count / total_time
        
        results = {
            'duration': total_time,
            'total_messages': message_count,
            'throughput': throughput,
            'message_size': message_size,
            'avg_processing_time': timer.histogram.get_stats()['avg']
        }
        
        print(f"吞吐量基准测试结果:")
        print(f"  总消息数: {message_count}")
        print(f"  总时间: {total_time:.2f}秒")
        print(f"  吞吐量: {throughput:.2f}消息/秒")
        print(f"  平均处理时间: {timer.histogram.get_stats()['avg']:.4f}秒")
        
        return results
    
    def run_latency_benchmark(self, test_count: int = 1000) -> Dict[str, Any]:
        """运行延迟基准测试"""
        print(f"开始延迟基准测试，测试次数: {test_count}")
        
        latencies = []
        timer = self.monitor.collector.get_timer("benchmark.latency")
        
        # 延迟测试函数
        def measure_latency():
            with timer.time_context():
                # 模拟消息处理
                start = time.perf_counter()
                time.sleep(0.01)  # 10ms基准延迟
                end = time.perf_counter()
                latency = end - start
                latencies.append(latency)
        
        # 运行延迟测试
        for i in range(test_count):
            if i % 100 == 0:
                print(f"进度: {i}/{test_count}")
            measure_latency()
        
        # 计算统计信息
        latencies.sort()
        count = len(latencies)
        
        results = {
            'test_count': count,
            'min_latency': min(latencies),
            'max_latency': max(latencies),
            'avg_latency': statistics.mean(latencies),
            'median_latency': statistics.median(latencies),
            'p95_latency': latencies[int(count * 0.95)],
            'p99_latency': latencies[int(count * 0.99)]
        }
        
        print(f"延迟基准测试结果:")
        print(f"  最小延迟: {results['min_latency']:.4f}秒")
        print(f"  最大延迟: {results['max_latency']:.4f}秒")
        print(f"  平均延迟: {results['avg_latency']:.4f}秒")
        print(f"  中位数延迟: {results['median_latency']:.4f}秒")
        print(f"  95%延迟: {results['p95_latency']:.4f}秒")
        print(f"  99%延迟: {results['p99_latency']:.4f}秒")
        
        return results
    
    def run_concurrent_benchmark(self, concurrent_threads: int = 10, duration: int = 30) -> Dict[str, Any]:
        """运行并发基准测试"""
        print(f"开始并发基准测试，并发线程数: {concurrent_threads}，持续时间: {duration}秒")
        
        results = {
            'concurrent_threads': concurrent_threads,
            'duration': duration,
            'thread_results': []
        }
        
        def worker_thread(thread_id: int):
            thread_results = {
                'thread_id': thread_id,
                'messages_processed': 0,
                'start_time': time.time(),
                'errors': 0
            }
            
            timer = self.monitor.collector.get_timer(f"benchmark.concurrent.{thread_id}")
            
            end_time = thread_results['start_time'] + duration
            while time.time() < end_time:
                try:
                    with timer.time_context():
                        # 模拟消息处理
                        time.sleep(0.005)  # 5ms处理时间
                        thread_results['messages_processed'] += 1
                except Exception as e:
                    thread_results['errors'] += 1
            
            thread_results['end_time'] = time.time()
            thread_results['total_time'] = thread_results['end_time'] - thread_results['start_time']
            thread_results['throughput'] = thread_results['messages_processed'] / thread_results['total_time']
            
            return thread_results
        
        # 启动工作线程
        threads = []
        for i in range(concurrent_threads):
            thread = threading.Thread(target=lambda: results['thread_results'].append(worker_thread(i)))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 计算总体统计
        total_messages = sum(r['messages_processed'] for r in results['thread_results'])
        total_time = duration
        overall_throughput = total_messages / total_time
        
        # 计算延迟统计
        all_latencies = []
        for i in range(concurrent_threads):
            timer = self.monitor.collector.get_timer(f"benchmark.concurrent.{i}")
            stats = timer.histogram.get_stats()
            # 估算延迟分布
            all_latencies.extend([stats['avg']] * int(stats['count'] / concurrent_threads))
        
        results.update({
            'total_messages': total_messages,
            'overall_throughput': overall_throughput,
            'avg_latency': statistics.mean(all_latencies) if all_latencies else 0,
            'thread_stats': results['thread_results']
        })
        
        print(f"并发基准测试结果:")
        print(f"  总消息数: {total_messages}")
        print(f"  总体吞吐量: {overall_throughput:.2f}消息/秒")
        print(f"  平均延迟: {results['avg_latency']:.4f}秒")
        print(f"  各线程统计:")
        for thread_result in results['thread_results']:
            print(f"    线程{thread_result['thread_id']}: {thread_result['messages_processed']}消息, "
                  f"{thread_result['throughput']:.2f}消息/秒")
        
        return results


class AutoTuningManager:
    """自动调优管理器"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.tuning_rules = []
        self.current_config = {}
        self.auto_tuning_enabled = False
        
    def enable_auto_tuning(self, enabled: bool = True):
        """启用或禁用自动调优"""
        self.auto_tuning_enabled = enabled
    
    def add_tuning_rule(self, condition: Dict[str, Any], action: Callable):
        """添加调优规则"""
        self.tuning_rules.append({
            'condition': condition,
            'action': action
        })
    
    def analyze_and_tune(self):
        """分析当前性能并调优"""
        if not self.auto_tuning_enabled:
            return
        
        metrics = self.monitor.collector.get_current_metrics()
        
        for rule in self.tuning_rules:
            if self._evaluate_condition(rule['condition'], metrics):
                try:
                    rule['action'](metrics)
                except Exception as e:
                    print(f"调优操作失败: {e}")
    
    def _evaluate_condition(self, condition: Dict[str, Any], metrics: Dict[str, PerformanceMetric]) -> bool:
        """评估条件"""
        metric_name = condition['metric']
        operator = condition['operator']
        threshold = condition['threshold']
        
        if metric_name not in metrics:
            return False
        
        value = metrics[metric_name].value
        
        if operator == '>' and value > threshold:
            return True
        elif operator == '<' and value < threshold:
            return True
        elif operator == '>=' and value >= threshold:
            return True
        elif operator == '<=' and value <= threshold:
            return True
        elif operator == '==' and value == threshold:
            return True
        elif operator == '!=' and value != threshold:
            return True
        
        return False
    
    def apply_rabbitmq_optimizations(self, metrics: Dict[str, PerformanceMetric]):
        """应用RabbitMQ优化"""
        print("正在应用RabbitMQ自动优化...")
        
        # 根据指标调整配置
        cpu_usage = metrics.get('system.cpu.usage', PerformanceMetric('dummy', 0, MetricType.GAUGE, 0)).value
        memory_usage = metrics.get('system.memory.usage_percent', PerformanceMetric('dummy', 0, MetricType.GAUGE, 0)).value
        
        if cpu_usage > 80:
            print("检测到高CPU使用率，建议:")
            print("  - 减少并发连接数")
            print("  - 调整队列消费者数量")
            print("  - 考虑增加节点")
        
        if memory_usage > 85:
            print("检测到高内存使用率，建议:")
            print("  - 降低队列消息TTL")
            print("  - 减少消息积压")
            print("  - 调整内存限制参数")


class PerformanceMonitoringDemo:
    """性能监控演示"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor(interval=1.0)
        self.benchmark_runner = BenchmarkRunner(self.monitor)
        self.auto_tuning = AutoTuningManager(self.monitor)
        
        # 设置监控回调
        self.monitor.add_monitor_callback(self._monitor_callback)
        
        # 添加默认调优规则
        self._setup_default_tuning_rules()
    
    def _setup_default_tuning_rules(self):
        """设置默认调优规则"""
        # 高CPU使用率调优规则
        self.auto_tuning.add_tuning_rule(
            condition={
                'metric': 'system.cpu.usage',
                'operator': '>',
                'threshold': 80.0
            },
            action=self.auto_tuning.apply_rabbitmq_optimizations
        )
        
        # 高内存使用率调优规则
        self.auto_tuning.add_tuning_rule(
            condition={
                'metric': 'system.memory.usage_percent',
                'operator': '>',
                'threshold': 85.0
            },
            action=self.auto_tuning.apply_rabbitmq_optimizations
        )
    
    def _monitor_callback(self, monitor_data: Dict[str, Any]):
        """监控回调函数"""
        timestamp = datetime.fromtimestamp(monitor_data['timestamp'])
        alerts = monitor_data['alerts']
        
        if alerts:
            print(f"[{timestamp.strftime('%H:%M:%S')}] 检测到告警:")
            for alert in alerts:
                print(f"  - {alert.level.value.upper()}: {alert.message}")
        
        # 自动调优
        if self.auto_tuning.auto_tuning_enabled:
            self.auto_tuning.analyze_and_tune()
    
    def demonstrate_basic_monitoring(self):
        """演示基础监控功能"""
        print("=== 基础性能监控演示 ===")
        
        # 模拟应用指标
        import random
        
        print("启动监控系统...")
        self.monitor.start_monitoring()
        
        try:
            print("运行监控30秒...")
            time.sleep(30)
        except KeyboardInterrupt:
            print("监控中断")
        finally:
            print("停止监控系统...")
            self.monitor.stop_monitoring()
        
        # 显示统计结果
        stats = self.monitor.collector.get_all_stats()
        print("\n📊 性能统计结果:")
        for metric_name, metric_data in stats.items():
            print(f"\n{metric_name}:")
            if metric_data['type'] == 'counter':
                print(f"  数值: {metric_data['value']}")
            elif metric_data['type'] == 'gauge':
                print(f"  数值: {metric_data['value']}")
            elif metric_data['type'] in ['histogram', 'timer']:
                metric_stats = metric_data['stats']
                print(f"  计数: {metric_stats['count']}")
                print(f"  平均值: {metric_stats['avg']:.4f}秒")
                print(f"  最大值: {metric_stats['max']:.4f}秒")
        
        # 显示活跃告警
        active_alerts = self.monitor.alert_engine.get_active_alerts()
        if active_alerts:
            print(f"\n🚨 活跃告警 ({len(active_alerts)}个):")
            for alert in active_alerts:
                print(f"  - {alert.level.value.upper()}: {alert.message}")
        
        print()
    
    def demonstrate_benchmark_testing(self):
        """演示基准测试"""
        print("=== 性能基准测试演示 ===")
        
        # 吞吐量测试
        print("\n1. 吞吐量基准测试:")
        throughput_results = self.benchmark_runner.run_throughput_benchmark(
            duration=10,  # 10秒测试
            message_size=1024
        )
        
        # 延迟测试
        print("\n2. 延迟基准测试:")
        latency_results = self.benchmark_runner.run_latency_benchmark(
            test_count=100  # 100次测试
        )
        
        # 并发测试
        print("\n3. 并发基准测试:")
        concurrent_results = self.benchmark_runner.run_concurrent_benchmark(
            concurrent_threads=5,  # 5个并发线程
            duration=10
        )
        
        # 保存结果
        self.benchmark_runner.results = {
            'throughput': throughput_results,
            'latency': latency_results,
            'concurrent': concurrent_results
        }
        
        print("\n✅ 基准测试完成")
        print()
    
    def demonstrate_auto_tuning(self):
        """演示自动调优"""
        print("=== 自动调优演示 ===")
        
        # 启用自动调优
        print("启用自动调优功能...")
        self.auto_tuning.enable_auto_tuning(True)
        
        # 启动监控
        self.monitor.start_monitoring()
        
        try:
            print("运行自动调优测试30秒...")
            
            # 模拟负载变化
            import random
            for i in range(30):
                # 随机改变负载情况
                cpu_load = random.uniform(70, 95)  # 模拟高CPU负载
                memory_load = random.uniform(75, 90)  # 模拟高内存负载
                
                self.monitor.collector.record_metric(PerformanceMetric(
                    name="system.cpu.usage",
                    value=cpu_load,
                    metric_type=MetricType.GAUGE,
                    timestamp=time.time()
                ))
                
                self.monitor.collector.record_metric(PerformanceMetric(
                    name="system.memory.usage_percent",
                    value=memory_load,
                    metric_type=MetricType.GAUGE,
                    timestamp=time.time()
                ))
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("自动调优测试中断")
        finally:
            self.monitor.stop_monitoring()
        
        print("✅ 自动调优演示完成")
        print()
    
    def demonstrate_alert_system(self):
        """演示告警系统"""
        print("=== 告警系统演示 ===")
        
        # 添加自定义告警规则
        custom_rule = AlertRule(
            name="test_high_cpu",
            metric_name="system.cpu.usage",
            condition=">",
            threshold=90.0,
            level=AlertLevel.CRITICAL,
            description="测试用CPU告警"
        )
        
        self.monitor.alert_engine.add_rule(custom_rule)
        
        # 启动监控
        self.monitor.start_monitoring()
        
        try:
            print("生成测试告警场景...")
            import random
            
            # 模拟高CPU使用率触发告警
            for i in range(20):
                cpu_usage = random.uniform(85, 98)  # 模拟高CPU使用
                
                self.monitor.collector.record_metric(PerformanceMetric(
                    name="system.cpu.usage",
                    value=cpu_usage,
                    metric_type=MetricType.GAUGE,
                    timestamp=time.time()
                ))
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("告警测试中断")
        finally:
            self.monitor.stop_monitoring()
        
        # 显示告警结果
        active_alerts = self.monitor.alert_engine.get_active_alerts()
        print(f"\n📢 活跃告警 ({len(active_alerts)}个):")
        for alert in active_alerts:
            print(f"  - {alert.level.value.upper()}: {alert.message}")
        
        print("✅ 告警系统演示完成")
        print()


if __name__ == "__main__":
    # 运行性能监控演示
    demo = PerformanceMonitoringDemo()
    
    print("🔧 RabbitMQ 性能监控与调优系统")
    print("=" * 50)
    print()
    
    try:
        # 1. 基础监控演示
        demo.demonstrate_basic_monitoring()
        
        # 2. 基准测试演示
        demo.demonstrate_benchmark_testing()
        
        # 3. 自动调优演示
        demo.demonstrate_auto_tuning()
        
        # 4. 告警系统演示
        demo.demonstrate_alert_system()
        
        print("🎉 所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序执行错误: {e}")
    finally:
        # 确保监控停止
        demo.monitor.stop_monitoring()