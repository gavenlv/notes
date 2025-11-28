#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第5章：队列管理与负载均衡 - 性能监控与健康检查
演示队列性能监控、健康检查、自动化扩缩容等管理功能
"""

import pika
import time
import json
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import logging


@dataclass
class QueueMetrics:
    """队列指标"""
    name: str
    message_count: int = 0
    consumer_count: int = 0
    pending_acks: int = 0
    rate_in: float = 0.0
    rate_out: float = 0.0
    memory_usage: int = 0
    disk_space: int = 0
    timestamp: float = 0.0


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    status: str  # 'healthy', 'warning', 'critical'
    score: float  # 0-100 健康分数
    details: Dict
    timestamp: float


@dataclass
class ScalingDecision:
    """扩缩容决策"""
    action: str  # 'scale_up', 'scale_down', 'no_action'
    reason: str
    current_instances: int
    target_instances: int
    confidence: float  # 0-1 决策置信度


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, window_size: int = 60):
        """初始化"""
        self.metrics_history = defaultdict(lambda: deque(maxlen=window_size))
        self.alert_thresholds = {
            'message_backlog': 1000,
            'consumer_lag': 100,
            'memory_usage': 80,  # 百分比
            'disk_usage': 90,    # 百分比
            'consumer_utilization': 0.9,  # 90%
            'throughput_drop': 0.3  # 30%
        }
        self.alerts = []
    
    def collect_queue_metrics(self, channel: pika.channel.Channel, queue_name: str) -> QueueMetrics:
        """收集队列指标"""
        try:
            # 获取队列信息
            queue_state = channel.queue_declare(queue=queue_name, passive=True)
            
            # 获取队列统计信息
            queue_info = channel.queue_declare(queue=queue_name, passive=True)
            
            metrics = QueueMetrics(
                name=queue_name,
                message_count=queue_state.method.message_count,
                consumer_count=queue_state.method.consumer_count,
                timestamp=time.time()
            )
            
            # 获取系统资源使用情况
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                # 这些指标通常需要管理API获取，这里模拟
                metrics.memory_usage = memory.percent
                
            except Exception as e:
                print(f"⚠️  获取系统指标失败: {e}")
            
            # 保存历史数据
            self.metrics_history[queue_name].append(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"❌ 收集队列 {queue_name} 指标失败: {e}")
            return QueueMetrics(name=queue_name, timestamp=time.time())
    
    def analyze_performance_trend(self, queue_name: str) -> Dict:
        """分析性能趋势"""
        if len(self.metrics_history[queue_name]) < 5:
            return {'status': 'insufficient_data'}
        
        recent_metrics = list(self.metrics_history[queue_name])[-10:]
        
        # 计算趋势
        message_counts = [m.message_count for m in recent_metrics]
        throughput_rates = [m.rate_out for m in recent_metrics if m.rate_out > 0]
        
        trends = {
            'message_count_trend': 'increasing' if message_counts[-1] > message_counts[0] else 'stable',
            'throughput_trend': 'improving' if len(throughput_rates) > 1 and 
                              throughput_rates[-1] > throughput_rates[0] else 'stable',
            'avg_queue_depth': statistics.mean(message_counts),
            'peak_queue_depth': max(message_counts),
            'throughput_variance': statistics.stdev(throughput_rates) if len(throughput_rates) > 1 else 0
        }
        
        return trends
    
    def check_alerts(self, metrics: QueueMetrics) -> List[str]:
        """检查告警条件"""
        alerts = []
        
        # 消息积压告警
        if metrics.message_count > self.alert_thresholds['message_backlog']:
            alerts.append(f"🚨 队列 {metrics.name} 消息积压严重: {metrics.message_count}")
        
        # 内存使用告警
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append(f"⚠️  系统内存使用过高: {metrics.memory_usage}%")
        
        # 消费者数量告警
        if metrics.consumer_count == 0 and metrics.message_count > 0:
            alerts.append(f"🚨 队列 {metrics.name} 有消息但没有消费者")
        
        return alerts
    
    def generate_performance_report(self, queue_name: str) -> Dict:
        """生成性能报告"""
        if queue_name not in self.metrics_history:
            return {'error': f'没有队列 {queue_name} 的监控数据'}
        
        metrics_list = list(self.metrics_history[queue_name])
        
        if not metrics_list:
            return {'error': f'队列 {queue_name} 没有历史数据'}
        
        # 计算统计指标
        message_counts = [m.message_count for m in metrics_list]
        consumer_counts = [m.consumer_count for m in metrics_list]
        memory_usage = [m.memory_usage for m in metrics_list if m.memory_usage > 0]
        
        report = {
            'queue_name': queue_name,
            'report_time': time.time(),
            'data_points': len(metrics_list),
            'statistics': {
                'message_count': {
                    'current': message_counts[-1] if message_counts else 0,
                    'average': statistics.mean(message_counts) if message_counts else 0,
                    'max': max(message_counts) if message_counts else 0,
                    'min': min(message_counts) if message_counts else 0
                },
                'consumer_count': {
                    'current': consumer_counts[-1] if consumer_counts else 0,
                    'average': statistics.mean(consumer_counts) if consumer_counts else 0,
                    'max': max(consumer_counts) if consumer_counts else 0
                },
                'memory_usage': {
                    'average': statistics.mean(memory_usage) if memory_usage else 0,
                    'max': max(memory_usage) if memory_usage else 0,
                    'current': memory_usage[-1] if memory_usage else 0
                }
            },
            'performance_trend': self.analyze_performance_trend(queue_name)
        }
        
        return report


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        """初始化"""
        self.check_results = []
        self.health_history = deque(maxlen=100)
        
    def check_rabbitmq_status(self, connection) -> HealthCheckResult:
        """检查RabbitMQ状态"""
        try:
            # 检查连接状态
            if not connection or connection.is_closed:
                return HealthCheckResult(
                    component='rabbitmq_connection',
                    status='critical',
                    score=0.0,
                    details={'error': '连接已关闭'},
                    timestamp=time.time()
                )
            
            # 检查网络
            channel = connection.channel()
            try:
                channel.queue_declare(queue='health_check', passive=True)
                channel.queue_delete(queue='health_check')
            except Exception:
                return HealthCheckResult(
                    component='rabbitmq_connection',
                    status='warning',
                    score=60.0,
                    details={'error': '无法访问队列'},
                    timestamp=time.time()
                )
            
            return HealthCheckResult(
                component='rabbitmq_connection',
                status='healthy',
                score=95.0,
                details={'message': 'RabbitMQ 连接正常'},
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheckResult(
                component='rabbitmq_connection',
                status='critical',
                score=0.0,
                details={'error': str(e)},
                timestamp=time.time()
            )
    
    def check_system_resources(self) -> HealthCheckResult:
        """检查系统资源"""
        try:
            # CPU 检查
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = 'healthy' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical'
            
            # 内存检查
            memory = psutil.virtual_memory()
            memory_status = 'healthy' if memory.percent < 80 else 'warning' if memory.percent < 95 else 'critical'
            
            # 磁盘检查
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_status = 'healthy' if disk_percent < 80 else 'warning' if disk_percent < 95 else 'critical'
            
            # 计算综合健康分数
            scores = {
                'healthy': 100,
                'warning': 70,
                'critical': 30
            }
            
            overall_score = min(scores[cpu_status], scores[memory_status], scores[disk_status])
            
            if overall_score >= 90:
                status = 'healthy'
            elif overall_score >= 60:
                status = 'warning'
            else:
                status = 'critical'
            
            result = HealthCheckResult(
                component='system_resources',
                status=status,
                score=overall_score,
                details={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk_percent
                },
                timestamp=time.time()
            )
            
            return result
            
        except Exception as e:
            return HealthCheckResult(
                component='system_resources',
                status='critical',
                score=0.0,
                details={'error': str(e)},
                timestamp=time.time()
            )
    
    def check_queue_health(self, channel: pika.channel.Channel, queue_name: str) -> HealthCheckResult:
        """检查队列健康状态"""
        try:
            # 获取队列信息
            queue_state = channel.queue_declare(queue=queue_name, passive=True)
            
            message_count = queue_state.method.message_count
            consumer_count = queue_state.method.consumer_count
            
            # 评估健康状态
            if consumer_count == 0 and message_count > 0:
                # 有消息但没有消费者
                status = 'critical'
                score = 20.0
                details = {'issue': '消息积压且无消费者'}
            elif message_count > 1000:
                # 消息过多
                status = 'warning'
                score = 60.0
                details = {'issue': f'消息积压过多: {message_count}'}
            elif consumer_count == 0:
                # 没有消费者
                status = 'warning'
                score = 70.0
                details = {'issue': '没有活跃消费者'}
            else:
                # 健康状态
                status = 'healthy'
                score = 90.0
                details = {'message': '队列运行正常'}
            
            result = HealthCheckResult(
                component=f'queue_{queue_name}',
                status=status,
                score=score,
                details={
                    'message_count': message_count,
                    'consumer_count': consumer_count,
                    **details
                },
                timestamp=time.time()
            )
            
            return result
            
        except Exception as e:
            return HealthCheckResult(
                component=f'queue_{queue_name}',
                status='critical',
                score=0.0,
                details={'error': str(e)},
                timestamp=time.time()
            )
    
    def get_overall_health(self) -> Dict:
        """获取整体健康状态"""
        if not self.health_history:
            return {'overall_status': 'unknown', 'score': 0.0}
        
        recent_checks = list(self.health_history)[-10:]
        
        # 统计健康状态
        status_counts = defaultdict(int)
        total_score = 0.0
        
        for check in recent_checks:
            status_counts[check.component] = check.status
            total_score += check.score
        
        # 计算整体健康分数
        avg_score = total_score / len(recent_checks) if recent_checks else 0.0
        
        # 确定整体状态
        if avg_score >= 90:
            overall_status = 'healthy'
        elif avg_score >= 60:
            overall_status = 'warning'
        else:
            overall_status = 'critical'
        
        return {
            'overall_status': overall_status,
            'average_score': avg_score,
            'check_count': len(recent_checks),
            'component_status': dict(status_counts),
            'last_update': time.time()
        }


class AutoScaler:
    """自动扩缩容管理器"""
    
    def __init__(self, min_instances: int = 1, max_instances: int = 10):
        """初始化"""
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.decisions_history = deque(maxlen=50)
        
    def analyze_scaling_needs(self, monitor: PerformanceMonitor, queue_name: str) -> ScalingDecision:
        """分析扩缩容需求"""
        try:
            if queue_name not in monitor.metrics_history:
                return ScalingDecision(
                    action='no_action',
                    reason='insufficient_data',
                    current_instances=1,
                    target_instances=1,
                    confidence=0.0
                )
            
            metrics_list = list(monitor.metrics_history[queue_name])
            
            if len(metrics_list) < 10:
                return ScalingDecision(
                    action='no_action',
                    reason='need_more_data',
                    current_instances=1,
                    target_instances=1,
                    confidence=0.0
                )
            
            # 分析趋势
            recent_metrics = metrics_list[-5:]
            older_metrics = metrics_list[-10:-5]
            
            # 计算平均消息数
            recent_avg_messages = statistics.mean([m.message_count for m in recent_metrics])
            older_avg_messages = statistics.mean([m.message_count for m in older_metrics]) if older_metrics else recent_avg_messages
            
            # 计算增长趋势
            message_growth_rate = (recent_avg_messages - older_avg_messages) / max(older_avg_messages, 1)
            
            # 估算当前消费者数量
            current_consumers = recent_metrics[-1].consumer_count if recent_metrics else 1
            
            # 决策逻辑
            if recent_avg_messages > 500 and message_growth_rate > 0.2:
                # 高负载，考虑扩容
                target_instances = min(current_consumers + 2, self.max_instances)
                confidence = min(0.9, 0.5 + abs(message_growth_rate))
                
                return ScalingDecision(
                    action='scale_up',
                    reason=f'高负载: 消息数 {recent_avg_messages:.0f}, 增长率 {message_growth_rate:.1%}',
                    current_instances=current_consumers,
                    target_instances=target_instances,
                    confidence=confidence
                )
            
            elif recent_avg_messages < 50 and message_growth_rate < -0.1 and current_consumers > self.min_instances:
                # 低负载，考虑缩容
                target_instances = max(current_consumers - 1, self.min_instances)
                confidence = min(0.8, 0.5 + abs(message_growth_rate))
                
                return ScalingDecision(
                    action='scale_down',
                    reason=f'低负载: 消息数 {recent_avg_messages:.0f}, 增长率 {message_growth_rate:.1%}',
                    current_instances=current_consumers,
                    target_instances=target_instances,
                    confidence=confidence
                )
            
            else:
                # 保持现状
                return ScalingDecision(
                    action='no_action',
                    reason=f'负载稳定: 消息数 {recent_avg_messages:.0f}',
                    current_instances=current_consumers,
                    target_instances=current_consumers,
                    confidence=0.6
                )
                
        except Exception as e:
            print(f"❌ 扩缩容分析失败: {e}")
            return ScalingDecision(
                action='no_action',
                reason=f'analysis_error: {str(e)}',
                current_instances=1,
                target_instances=1,
                confidence=0.0
            )
    
    def execute_scaling(self, decision: ScalingDecision, scaling_callback: Callable[[int], bool]) -> bool:
        """执行扩缩容操作"""
        if decision.action == 'no_action':
            print("ℹ️  当前负载稳定，无需扩缩容")
            return True
        
        try:
            print(f"🔄 执行扩缩容: {decision.reason}")
            print(f"   当前实例数: {decision.current_instances} → 目标实例数: {decision.target_instances}")
            
            # 调用扩缩容回调函数
            success = scaling_callback(decision.target_instances)
            
            if success:
                self.decisions_history.append(decision)
                print("✅ 扩缩容操作成功")
            else:
                print("❌ 扩缩容操作失败")
            
            return success
            
        except Exception as e:
            print(f"❌ 扩缩容执行异常: {e}")
            return False


class MonitoringHealthDemo:
    """监控和健康检查演示"""
    
    def __init__(self, connection_params=None):
        """初始化"""
        self.connection_params = connection_params or pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=pika.PlainCredentials('guest', 'guest')
        )
        self.connection = None
        self.channel = None
        
        self.monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        self.auto_scaler = AutoScaler()
        
        self.monitoring_active = False
        self.scaling_callback = None
        
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
        self.monitoring_active = False
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 已断开RabbitMQ连接")
    
    def setup_demo_queues(self):
        """设置演示队列"""
        queues = [
            'monitoring_high_load_queue',
            'monitoring_medium_load_queue',
            'monitoring_low_load_queue'
        ]
        
        for queue_name in queues:
            try:
                self.channel.queue_declare(queue=queue_name, durable=True)
                print(f"✅ 创建队列: {queue_name}")
            except Exception as e:
                print(f"❌ 创建队列失败 {queue_name}: {e}")
    
    def generate_test_traffic(self, queue_name: str, duration: int = 60):
        """生成测试流量"""
        print(f"📡 开始生成流量到队列: {queue_name}")
        
        end_time = time.time() + duration
        message_count = 0
        
        while time.time() < end_time and self.monitoring_active:
            try:
                # 模拟不同类型的消息
                if 'high' in queue_name:
                    # 高负载：快速发送大量消息
                    message_delay = 0.1
                    message_data = {
                        'type': 'high_load',
                        'timestamp': time.time(),
                        'data': f'高负载消息 {message_count}'
                    }
                elif 'medium' in queue_name:
                    # 中等负载：中等速度发送
                    message_delay = 0.5
                    message_data = {
                        'type': 'medium_load',
                        'timestamp': time.time(),
                        'data': f'中等负载消息 {message_count}'
                    }
                else:
                    # 低负载：慢速发送少量消息
                    message_delay = 2.0
                    message_data = {
                        'type': 'low_load',
                        'timestamp': time.time(),
                        'data': f'低负载消息 {message_count}'
                    }
                
                # 发送消息
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message_data),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                
                message_count += 1
                time.sleep(message_delay)
                
            except Exception as e:
                print(f"❌ 生成流量失败: {e}")
                break
        
        print(f"📤 流量生成完成，共发送 {message_count} 条消息")
    
    def collect_metrics_periodically(self, interval: int = 5):
        """定期收集指标"""
        queues = [
            'monitoring_high_load_queue',
            'monitoring_medium_load_queue',
            'monitoring_low_load_queue'
        ]
        
        while self.monitoring_active:
            try:
                for queue_name in queues:
                    # 收集队列指标
                    metrics = self.monitor.collect_queue_metrics(self.channel, queue_name)
                    
                    # 检查告警
                    alerts = self.monitor.check_alerts(metrics)
                    for alert in alerts:
                        print(alert)
                    
                    # 检查队列健康
                    health_result = self.health_checker.check_queue_health(
                        self.channel, queue_name
                    )
                    self.health_checker.health_history.append(health_result)
                    
                    # 分析扩缩容需求
                    scaling_decision = self.auto_scaler.analyze_scaling_needs(
                        self.monitor, queue_name
                    )
                    
                    if scaling_decision.action != 'no_action':
                        print(f"🔄 扩缩容建议 [{queue_name}]: {scaling_decision.reason}")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ 指标收集异常: {e}")
                time.sleep(interval)
    
    def run_monitoring_demo(self, duration: int = 60):
        """运行监控演示"""
        print("\n" + "="*60)
        print("📊 队列监控和健康检查演示")
        print("="*60)
        
        try:
            # 设置演示队列
            self.setup_demo_queues()
            
            # 启动监控
            self.monitoring_active = True
            
            print(f"\n🔍 开始监控，持续时间: {duration} 秒")
            print("   队列: monitoring_high_load_queue, monitoring_medium_load_queue, monitoring_low_load_queue")
            
            # 启动流量生成线程
            traffic_threads = []
            for queue_name in [
                'monitoring_high_load_queue',
                'monitoring_medium_load_queue', 
                'monitoring_low_load_queue'
            ]:
                thread = threading.Thread(
                    target=self.generate_test_traffic,
                    args=(queue_name, duration)
                )
                thread.daemon = True
                thread.start()
                traffic_threads.append(thread)
            
            # 启动指标收集线程
            metrics_thread = threading.Thread(
                target=self.collect_metrics_periodically,
                args=(5,)
            )
            metrics_thread.daemon = True
            metrics_thread.start()
            
            # 定期生成报告
            end_time = time.time() + duration
            while time.time() < end_time:
                try:
                    time.sleep(15)  # 每15秒生成一次报告
                    
                    # 生成性能报告
                    for queue_name in [
                        'monitoring_high_load_queue',
                        'monitoring_medium_load_queue',
                        'monitoring_low_load_queue'
                    ]:
                        report = self.monitor.generate_performance_report(queue_name)
                        if 'error' not in report:
                            print(f"\n📈 {queue_name} 性能报告:")
                            print(f"   当前消息数: {report['statistics']['message_count']['current']}")
                            print(f"   平均消息数: {report['statistics']['message_count']['average']:.1f}")
                            print(f"   当前消费者: {report['statistics']['consumer_count']['current']}")
                    
                    # 显示整体健康状态
                    overall_health = self.health_checker.get_overall_health()
                    status_emoji = {'healthy': '✅', 'warning': '⚠️', 'critical': '🚨', 'unknown': '❓'}
                    print(f"\n{status_emoji.get(overall_health['overall_status'], '❓')} "
                          f"整体健康状态: {overall_health['overall_status']} "
                          f"(分数: {overall_health['average_score']:.1f})")
                    
                except Exception as e:
                    print(f"❌ 生成报告异常: {e}")
            
            # 生成最终报告
            print(f"\n📋 监控总结报告")
            print("-" * 50)
            
            for queue_name in [
                'monitoring_high_load_queue',
                'monitoring_medium_load_queue',
                'monitoring_low_load_queue'
            ]:
                final_report = self.monitor.generate_performance_report(queue_name)
                if 'error' not in final_report:
                    print(f"\n📊 {queue_name}:")
                    stats = final_report['statistics']['message_count']
                    print(f"   消息处理统计: 最大 {stats['max']}, 平均 {stats['average']:.1f}")
            
            # 显示扩缩容历史
            if self.auto_scaler.decisions_history:
                print(f"\n🔄 扩缩容决策历史:")
                for decision in self.auto_scaler.decisions_history:
                    print(f"   {decision.action}: {decision.reason} "
                          f"(置信度: {decision.confidence:.1%})")
            
            print("\n✅ 监控演示完成")
            
        except KeyboardInterrupt:
            print("\n⏹️  监控被用户中断")
        except Exception as e:
            print(f"\n❌ 监控演示异常: {e}")
        finally:
            self.monitoring_active = False
    
    def run_comprehensive_health_check(self):
        """运行综合健康检查"""
        print("\n" + "="*60)
        print("🏥 综合健康检查")
        print("="*60)
        
        try:
            # RabbitMQ 连接检查
            if self.connection:
                rabbitmq_health = self.health_checker.check_rabbitmq_status(self.connection)
                status_emoji = {'healthy': '✅', 'warning': '⚠️', 'critical': '🚨'}
                print(f"{status_emoji.get(rabbitmq_health.status, '❓')} "
                      f"RabbitMQ连接: {rabbitmq_health.status} "
                      f"(分数: {rabbitmq_health.score:.1f})")
            
            # 系统资源检查
            system_health = self.health_checker.check_system_resources()
            print(f"{status_emoji.get(system_health.status, '❓')} "
                  f"系统资源: {system_health.status} "
                  f"(分数: {system_health.score:.1f})")
            
            details = system_health.details
            if 'cpu_percent' in details:
                print(f"   CPU: {details['cpu_percent']:.1f}%, "
                      f"内存: {details.get('memory_percent', 0):.1f}%, "
                      f"磁盘: {details.get('disk_percent', 0):.1f}%")
            
            # 队列健康检查
            queues = [
                'monitoring_high_load_queue',
                'monitoring_medium_load_queue', 
                'monitoring_low_load_queue'
            ]
            
            print(f"\n🏥 队列健康检查:")
            for queue_name in queues:
                try:
                    queue_health = self.health_checker.check_queue_health(self.channel, queue_name)
                    print(f"{status_emoji.get(queue_health.status, '❓')} "
                          f"{queue_name}: {queue_health.status} "
                          f"(分数: {queue_health.score:.1f})")
                    
                    queue_details = queue_health.details
                    if 'message_count' in queue_details:
                        print(f"   消息数: {queue_details['message_count']}, "
                              f"消费者数: {queue_details.get('consumer_count', 0)}")
                    
                except Exception as e:
                    print(f"❌ 检查队列 {queue_name} 失败: {e}")
            
            # 整体健康状态
            overall_health = self.health_checker.get_overall_health()
            print(f"\n📊 整体健康状态: {overall_health['overall_status']} "
                  f"(平均分数: {overall_health['average_score']:.1f})")
            
            if overall_health['overall_status'] == 'healthy':
                print("✅ 所有组件运行正常")
            elif overall_health['overall_status'] == 'warning':
                print("⚠️  部分组件需要关注")
            else:
                print("🚨 发现严重问题，需要立即处理")
                
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
    
    def cleanup_demo_queues(self):
        """清理演示队列"""
        queues = [
            'monitoring_high_load_queue',
            'monitoring_medium_load_queue',
            'monitoring_low_load_queue'
        ]
        
        for queue_name in queues:
            try:
                self.channel.queue_purge(queue=queue_name)
                print(f"🧹 已清空队列: {queue_name}")
            except Exception as e:
                print(f"⚠️  清空队列失败 {queue_name}: {e}")
        
        print("✅ 演示队列清理完成")


def main():
    """主函数"""
    print("🐰 RabbitMQ 队列监控与健康检查演示")
    print("=" * 60)
    
    try:
        with MonitoringHealthDemo() as demo:
            # 1. 监控演示
            demo.run_monitoring_demo(duration=60)
            
            # 清理并等待
            demo.cleanup_demo_queues()
            time.sleep(2)
            
            # 2. 综合健康检查
            demo.setup_demo_queues()
            demo.run_comprehensive_health_check()
            
            print("\n🎉 所有监控和健康检查演示完成！")
            
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()