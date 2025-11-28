"""
RabbitMQ性能监控模块
提供RabbitMQ服务的实时性能监控、分析和告警功能
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import statistics


class RabbitMQAlertLevel(Enum):
    """RabbitMQ告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class RabbitMQMetric:
    """RabbitMQ指标"""
    timestamp: datetime
    queue_messages: int
    queue_rate_in: float
    queue_rate_out: float
    connection_count: int
    channel_count: int
    memory_usage: int
    disk_usage: int
    ready_messages: int
    unacknowledged_messages: int


@dataclass
class QueueInfo:
    """队列信息"""
    name: str
    messages: int
    rate_in: float
    rate_out: float
    consumers: int
    durable: bool
    auto_delete: bool


@dataclass
class ConnectionInfo:
    """连接信息"""
    name: str
    state: str
    channels: int
    recv_cnt: int
    send_cnt: int
    user: str
    vhost: str


class RabbitMQAPIClient:
    """RabbitMQ API客户端"""
    
    def __init__(self, host: str = 'localhost', port: int = 15672, 
                 user: str = 'guest', password: str = 'guest'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.base_url = f"http://{host}:{port}/api"
        self.auth = (user, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.timeout = 5
    
    def get_overview(self) -> Dict[str, Any]:
        """获取概览信息"""
        try:
            response = self.session.get(f"{self.base_url}/overview")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"获取RabbitMQ概览失败: {e}")
            return {}
    
    def get_queues(self) -> List[Dict[str, Any]]:
        """获取队列信息"""
        try:
            response = self.session.get(f"{self.base_url}/queues")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"获取队列信息失败: {e}")
            return []
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """获取连接信息"""
        try:
            response = self.session.get(f"{self.base_url}/connections")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"获取连接信息失败: {e}")
            return []
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """获取通道信息"""
        try:
            response = self.session.get(f"{self.base_url}/channels")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"获取通道信息失败: {e}")
            return []
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """获取节点信息"""
        try:
            response = self.session.get(f"{self.base_url}/nodes")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"获取节点信息失败: {e}")
            return []
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            overview = self.get_overview()
            return bool(overview)
        except Exception:
            return False


class PerformanceCollector:
    """性能数据收集器"""
    
    def __init__(self, api_client: RabbitMQAPIClient, collection_interval: int = 30):
        self.api_client = api_client
        self.collection_interval = collection_interval
        self.metrics_history = deque(maxlen=1000)
        self.collecting = False
        self.collect_thread = None
        self.logger = logging.getLogger(__name__)
    
    def start_collection(self):
        """开始数据收集"""
        if not self.collecting:
            self.collecting = True
            self.collect_thread = threading.Thread(target=self._collection_loop, daemon=True)
            self.collect_thread.start()
            self.logger.info("RabbitMQ性能数据收集已启动")
    
    def stop_collection(self):
        """停止数据收集"""
        self.collecting = False
        if self.collect_thread:
            self.collect_thread.join(timeout=5)
        self.logger.info("RabbitMQ性能数据收集已停止")
    
    def _collection_loop(self):
        """收集循环"""
        while self.collecting:
            try:
                metric = self._collect_current_metric()
                if metric:
                    self.metrics_history.append(metric)
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"性能数据收集错误: {e}")
                time.sleep(5)
    
    def _collect_current_metric(self) -> Optional[RabbitMQMetric]:
        """收集当前指标"""
        overview = self.api_client.get_overview()
        if not overview:
            return None
        
        # 计算队列统计
        queues = self.api_client.get_queues()
        total_messages = sum(queue.get('messages', 0) for queue in queues)
        
        # 计算消息速率
        queue_rate_in = sum(queue.get('message_stats', {}).get('publish_details', {}).get('rate', 0) 
                           for queue in queues if 'message_stats' in queue)
        queue_rate_out = sum(queue.get('message_stats', {}).get('get_details', {}).get('rate', 0)
                            for queue in queues if 'message_stats' in queue)
        
        # 连接和通道统计
        connection_count = overview.get('object_totals', {}).get('connections', 0)
        channel_count = overview.get('object_totals', {}).get('channels', 0)
        
        # 内存和磁盘使用
        memory_usage = overview.get('memory', {}).get('used', 0)
        disk_usage = overview.get('disk', {}).get('free', 0)
        
        return RabbitMQMetric(
            timestamp=datetime.now(),
            queue_messages=total_messages,
            queue_rate_in=queue_rate_in,
            queue_rate_out=queue_rate_out,
            connection_count=connection_count,
            channel_count=channel_count,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            ready_messages=total_messages,  # 简化处理
            unacknowledged_messages=0  # 需要单独查询
        )
    
    def get_current_metrics(self) -> Optional[RabbitMQMetric]:
        """获取当前指标"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_in_range(self, minutes: int = 30) -> List[RabbitMQMetric]:
        """获取指定时间范围的指标"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=minutes)
        
        return [
            metric for metric in self.metrics_history
            if start_time <= metric.timestamp <= end_time
        ]


class MetricsAggregator:
    """指标聚合器"""
    
    def __init__(self, collector: PerformanceCollector):
        self.collector = collector
    
    def get_throughput_stats(self, minutes: int = 30) -> Dict[str, float]:
        """获取吞吐量统计"""
        metrics = self.collector.get_metrics_in_range(minutes)
        
        if not metrics:
            return {}
        
        rates_in = [m.queue_rate_in for m in metrics]
        rates_out = [m.queue_rate_out for m in metrics]
        
        return {
            'in_avg': statistics.mean(rates_in),
            'in_max': max(rates_in),
            'in_min': min(rates_in),
            'out_avg': statistics.mean(rates_out),
            'out_max': max(rates_out),
            'out_min': min(rates_out),
            'sample_count': len(metrics)
        }
    
    def get_connection_stats(self, minutes: int = 30) -> Dict[str, float]:
        """获取连接统计"""
        metrics = self.collector.get_metrics_in_range(minutes)
        
        if not metrics:
            return {}
        
        connections = [m.connection_count for m in metrics]
        channels = [m.channel_count for m in metrics]
        
        return {
            'connections_avg': statistics.mean(connections),
            'connections_max': max(connections),
            'channels_avg': statistics.mean(channels),
            'channels_max': max(channels),
            'sample_count': len(metrics)
        }
    
    def get_performance_trend(self, hours: int = 1) -> Dict[str, str]:
        """分析性能趋势"""
        metrics = self.collector.get_metrics_in_range(hours * 60)
        
        if len(metrics) < 2:
            return {'trend': 'insufficient_data'}
        
        # 计算趋势
        recent_half = metrics[len(metrics)//2:]
        old_half = metrics[:len(metrics)//2]
        
        recent_avg = statistics.mean([m.queue_rate_in for m in recent_half])
        old_avg = statistics.mean([m.queue_rate_in for m in old_half])
        
        if recent_avg > old_avg * 1.1:
            trend = 'increasing'
        elif recent_avg < old_avg * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'throughput_trend': trend,
            'throughput_change': f"{(recent_avg - old_avg) / old_avg * 100:.1f}%"
        }
    
    def calculate_health_score(self, minutes: int = 30) -> float:
        """计算RabbitMQ健康度分数"""
        metrics = self.collector.get_metrics_in_range(minutes)
        
        if not metrics:
            return 0.0
        
        latest_metric = metrics[-1]
        scores = []
        
        # 队列深度分数 (40%权重)
        if latest_metric.queue_messages < 1000:
            queue_score = 100
        elif latest_metric.queue_messages < 5000:
            queue_score = 80
        elif latest_metric.queue_messages < 10000:
            queue_score = 60
        else:
            queue_score = 30
        scores.append(queue_score * 0.4)
        
        # 连接健康度 (30%权重)
        connection_stats = self.get_connection_stats(minutes)
        avg_connections = connection_stats.get('connections_avg', 0)
        if avg_connections < 100:
            connection_score = 100
        elif avg_connections < 500:
            connection_score = 80
        else:
            connection_score = 60
        scores.append(connection_score * 0.3)
        
        # 吞吐量分数 (30%权重)
        throughput_stats = self.get_throughput_stats(minutes)
        avg_rate = throughput_stats.get('in_avg', 0)
        if avg_rate > 1000:
            throughput_score = 100
        elif avg_rate > 500:
            throughput_score = 80
        elif avg_rate > 100:
            throughput_score = 60
        else:
            throughput_score = 40
        scores.append(throughput_score * 0.3)
        
        return round(sum(scores), 2)


class RabbitMQAlertManager:
    """RabbitMQ告警管理器"""
    
    def __init__(self):
        self.alert_rules = []
        self.alert_callbacks = []
        self.active_alerts = {}
        self.logger = logging.getLogger(__name__)
    
    def add_alert_rule(self, name: str, metric_name: str, condition: str, 
                      threshold: float, level: RabbitMQAlertLevel, description: str):
        """添加告警规则"""
        self.alert_rules.append({
            'name': name,
            'metric': metric_name,
            'condition': condition,
            'threshold': threshold,
            'level': level,
            'description': description
        })
    
    def add_alert_callback(self, callback: Callable[[Dict], None]):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def check_alerts(self, metric: RabbitMQMetric) -> List[Dict]:
        """检查告警"""
        alerts = []
        metrics = {
            'queue_messages': metric.queue_messages,
            'queue_rate_in': metric.queue_rate_in,
            'queue_rate_out': metric.queue_rate_out,
            'connection_count': metric.connection_count,
            'channel_count': metric.channel_count,
            'memory_usage': metric.memory_usage
        }
        
        for rule in self.alert_rules:
            metric_value = metrics.get(rule['metric'])
            if metric_value is None:
                continue
            
            # 检查条件
            triggered = False
            if rule['condition'] == '>' and metric_value > rule['threshold']:
                triggered = True
            elif rule['condition'] == '<' and metric_value < rule['threshold']:
                triggered = True
            elif rule['condition'] == '>=' and metric_value >= rule['threshold']:
                triggered = True
            elif rule['condition'] == '<=' and metric_value <= rule['threshold']:
                triggered = True
            
            alert_key = f"{rule['name']}:{rule['metric']}"
            
            if triggered:
                if alert_key not in self.active_alerts:
                    alert = {
                        'id': alert_key,
                        'name': rule['name'],
                        'level': rule['level'],
                        'metric': rule['metric'],
                        'value': metric_value,
                        'threshold': rule['threshold'],
                        'message': rule['description'].format(
                            value=metric_value, 
                            threshold=rule['threshold']
                        ),
                        'timestamp': datetime.now()
                    }
                    
                    self.active_alerts[alert_key] = alert
                    alerts.append(alert)
                    
                    # 调用回调
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            self.logger.error(f"告警回调失败: {e}")
            
            else:
                # 告警恢复
                if alert_key in self.active_alerts:
                    del self.active_alerts[alert_key]
                    self.logger.info(f"告警恢复: {rule['name']}")
        
        return alerts


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, api_client: RabbitMQAPIClient):
        self.api_client = api_client
        self.collector = PerformanceCollector(api_client)
        self.aggregator = MetricsAggregator(self.collector)
        self.alert_manager = RabbitMQAlertManager()
        self.monitoring = False
        self.monitor_thread = None
        
        # 设置默认告警规则
        self._setup_default_alerts()
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        self.alert_manager.add_alert_rule(
            name='queue_backlog_high',
            metric_name='queue_messages',
            condition='>',
            threshold=10000,
            level=RabbitMQAlertLevel.WARNING,
            description='队列消息积压严重: {value} (阈值: {threshold})'
        )
        
        self.alert_manager.add_alert_rule(
            name='queue_backlog_critical',
            metric_name='queue_messages',
            condition='>',
            threshold=50000,
            level=RabbitMQAlertLevel.CRITICAL,
            description='队列消息积压危险: {value} (阈值: {threshold})'
        )
        
        self.alert_manager.add_alert_rule(
            name='low_throughput',
            metric_name='queue_rate_in',
            condition='<',
            threshold=10.0,
            level=RabbitMQAlertLevel.WARNING,
            description='消息吞吐量过低: {value}/s (阈值: {threshold}/s)'
        )
        
        self.alert_manager.add_alert_rule(
            name='high_connection_count',
            metric_name='connection_count',
            condition='>',
            threshold=1000,
            level=RabbitMQAlertLevel.WARNING,
            description='连接数过多: {value} (阈值: {threshold})'
        )
    
    def start_monitoring(self):
        """开始监控"""
        if not self.monitoring:
            # 测试连接
            if not self.api_client.test_connection():
                raise Exception("RabbitMQ连接测试失败")
            
            self.monitoring = True
            self.collector.start_collection()
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("RabbitMQ性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        self.collector.stop_collection()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("RabbitMQ性能监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                current_metric = self.collector.get_current_metrics()
                if current_metric:
                    # 检查告警
                    self.alert_manager.check_alerts(current_metric)
                
                time.sleep(10)  # 10秒检查一次告警
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(5)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控面板数据"""
        current_metric = self.collector.get_current_metrics()
        if not current_metric:
            return {'status': 'no_data'}
        
        # 获取详细队列信息
        queues = self.api_client.get_queues()
        connections = self.api_client.get_connections()
        overview = self.api_client.get_overview()
        
        # 计算健康度
        health_score = self.aggregator.calculate_health_score()
        
        # 获取性能统计
        throughput_stats = self.aggregator.get_throughput_stats()
        connection_stats = self.aggregator.get_connection_stats()
        performance_trend = self.aggregator.get_performance_trend()
        
        # 获取活跃告警
        active_alerts = list(self.alert_manager.active_alerts.values())
        
        return {
            'timestamp': current_metric.timestamp.isoformat(),
            'status': 'healthy' if health_score > 80 else 'warning' if health_score > 60 else 'critical',
            'health_score': health_score,
            'metrics': asdict(current_metric),
            'overview': overview,
            'queues': len(queues),
            'connections': len(connections),
            'throughput_stats': throughput_stats,
            'connection_stats': connection_stats,
            'performance_trend': performance_trend,
            'active_alerts': len(active_alerts),
            'alert_details': active_alerts
        }


class PerformanceReporting:
    """性能报告生成器"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """生成性能报告"""
        dashboard_data = self.monitor.get_dashboard_data()
        
        # 分析瓶颈
        bottlenecks = self._analyze_bottlenecks()
        
        # 生成建议
        recommendations = self._generate_recommendations(bottlenecks)
        
        # 计算可用性
        availability = self._calculate_availability(hours)
        
        return {
            'report_time': datetime.now().isoformat(),
            'time_range_hours': hours,
            'health_summary': {
                'overall_score': dashboard_data.get('health_score', 0),
                'status': dashboard_data.get('status', 'unknown'),
                'active_alerts': dashboard_data.get('active_alerts', 0)
            },
            'performance_summary': {
                'throughput': dashboard_data.get('throughput_stats', {}),
                'connections': dashboard_data.get('connection_stats', {}),
                'trend': dashboard_data.get('performance_trend', {})
            },
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'availability': availability,
            'key_metrics': self._extract_key_metrics()
        }
    
    def _analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """分析性能瓶颈"""
        bottlenecks = []
        
        dashboard_data = self.monitor.get_dashboard_data()
        
        # 检查队列积压
        metric = dashboard_data.get('metrics', {})
        queue_messages = metric.get('queue_messages', 0)
        
        if queue_messages > 10000:
            bottlenecks.append({
                'type': 'queue_backlog',
                'severity': 'high' if queue_messages > 50000 else 'medium',
                'description': f'队列消息积压严重，当前积压 {queue_messages} 条消息',
                'impact': '消息处理延迟增加，可能导致业务超时'
            })
        
        # 检查连接数
        connection_count = metric.get('connection_count', 0)
        if connection_count > 1000:
            bottlenecks.append({
                'type': 'high_connections',
                'severity': 'medium',
                'description': f'连接数过高，当前 {connection_count} 个连接',
                'impact': '可能影响服务器性能'
            })
        
        # 检查吞吐量
        throughput = dashboard_data.get('throughput_stats', {})
        if throughput.get('in_avg', 0) < 50:
            bottlenecks.append({
                'type': 'low_throughput',
                'severity': 'medium',
                'description': f'消息吞吐量较低，平均 {throughput.get("in_avg", 0):.1f} 消息/秒',
                'impact': '系统处理能力不足'
            })
        
        return bottlenecks
    
    def _generate_recommendations(self, bottlenecks: List[Dict]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        bottleneck_types = [b['type'] for b in bottlenecks]
        
        if 'queue_backlog' in bottleneck_types:
            recommendations.append("增加消费者实例或优化消息处理逻辑")
            recommendations.append("检查消息处理逻辑，消除性能瓶颈")
            recommendations.append("考虑水平扩展RabbitMQ集群")
        
        if 'high_connections' in bottleneck_types:
            recommendations.append("检查连接池配置，避免连接泄漏")
            recommendations.append("考虑使用长连接减少连接建立开销")
        
        if 'low_throughput' in bottleneck_types:
            recommendations.append("优化消息生产者发送频率")
            recommendations.append("检查网络带宽和延迟")
            recommendations.append("调整RabbitMQ性能参数")
        
        if not bottlenecks:
            recommendations.append("系统运行良好，建议保持当前配置")
        
        return recommendations
    
    def _calculate_availability(self, hours: int) -> Dict[str, float]:
        """计算系统可用性"""
        # 这里可以实现更复杂的可用性计算逻辑
        # 简化实现：基于告警数量和时间计算
        active_alerts = len(self.monitor.alert_manager.active_alerts)
        
        if active_alerts == 0:
            availability = 100.0
        elif active_alerts <= 2:
            availability = 95.0
        elif active_alerts <= 5:
            availability = 90.0
        else:
            availability = 80.0
        
        return {
            'availability_percent': availability,
            'downtime_hours': (100 - availability) / 100 * hours,
            'sla_compliant': availability >= 99.0
        }
    
    def _extract_key_metrics(self) -> Dict[str, Any]:
        """提取关键指标"""
        dashboard_data = self.monitor.get_dashboard_data()
        
        return {
            'current_queue_messages': dashboard_data.get('metrics', {}).get('queue_messages', 0),
            'current_connection_count': dashboard_data.get('metrics', {}).get('connection_count', 0),
            'current_throughput': dashboard_data.get('throughput_stats', {}).get('in_avg', 0),
            'health_score': dashboard_data.get('health_score', 0)
        }


class PerformanceMonitoringDemo:
    """性能监控演示"""
    
    def __init__(self, host='localhost', port=15672, user='guest', password='guest'):
        self.api_client = RabbitMQAPIClient(host, port, user, password)
        self.monitor = PerformanceMonitor(self.api_client)
        self.reporting = PerformanceReporting(self.monitor)
        
        # 添加告警回调
        self.monitor.alert_manager.add_alert_callback(self._alert_callback)
    
    def _alert_callback(self, alert: Dict):
        """告警回调函数"""
        level_icon = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨'
        }
        icon = level_icon.get(alert['level'].value, '❓')
        print(f"{icon} 告警: {alert['name']} - {alert['message']}")
    
    def demo_connection_test(self):
        """演示连接测试"""
        print("=== RabbitMQ连接测试 ===")
        
        if self.api_client.test_connection():
            print("✅ RabbitMQ连接测试成功")
            
            # 获取基本信息
            overview = self.api_client.get_overview()
            if overview:
                print(f"RabbitMQ版本: {overview.get('rabbitmq_version', 'unknown')}")
                print(f"管理插件版本: {overview.get('management_version', 'unknown')}")
            
            queues = self.api_client.get_queues()
            connections = self.api_client.get_connections()
            print(f"队列数量: {len(queues)}")
            print(f"连接数量: {len(connections)}")
            
        else:
            print("❌ RabbitMQ连接测试失败")
            print("请确保RabbitMQ管理插件已启用且配置正确")
    
    def demo_basic_monitoring(self):
        """演示基础监控"""
        print("\n=== 基础性能监控演示 ===")
        
        try:
            self.monitor.start_monitoring()
            print("监控已启动，等待数据收集...")
            
            # 等待一些数据
            time.sleep(60)
            
            # 获取监控数据
            dashboard_data = self.monitor.get_dashboard_data()
            
            print(f"监控状态: {dashboard_data.get('status', 'unknown')}")
            print(f"健康度分数: {dashboard_data.get('health_score', 0)}/100")
            print(f"队列数量: {dashboard_data.get('queues', 0)}")
            print(f"连接数量: {dashboard_data.get('connections', 0)}")
            
            # 显示性能统计
            throughput_stats = dashboard_data.get('throughput_stats', {})
            if throughput_stats:
                print(f"平均消息入队速率: {throughput_stats.get('in_avg', 0):.1f} 消息/秒")
                print(f"平均消息出队速率: {throughput_stats.get('out_avg', 0):.1f} 消息/秒")
            
            # 显示趋势
            trend = dashboard_data.get('performance_trend', {})
            if trend:
                print(f"吞吐量趋势: {trend.get('throughput_trend', 'unknown')}")
                print(f"变化幅度: {trend.get('throughput_change', 'unknown')}")
            
        except Exception as e:
            print(f"监控演示失败: {e}")
        finally:
            self.monitor.stop_monitoring()
    
    def demo_alert_system(self):
        """演示告警系统"""
        print("\n=== 告警系统演示 ===")
        
        # 添加一个测试告警规则
        self.monitor.alert_manager.add_alert_rule(
            name='test_high_messages',
            metric_name='queue_messages',
            condition='>',
            threshold=100,  # 设置较低阈值用于演示
            level=RabbitMQAlertLevel.WARNING,
            description='测试告警: 队列消息数量超过阈值 {value} > {threshold}'
        )
        
        try:
            print("启动监控并生成测试告警...")
            self.monitor.start_monitoring()
            
            # 长时间监控以触发告警
            print("监控60秒...")
            time.sleep(60)
            
            # 显示告警统计
            active_alerts = list(self.monitor.alert_manager.active_alerts.values())
            print(f"当前活跃告警数: {len(active_alerts)}")
            
            if active_alerts:
                print("活跃告警详情:")
                for alert in active_alerts:
                    print(f"  - {alert['name']}: {alert['message']}")
            
        except Exception as e:
            print(f"告警演示失败: {e}")
        finally:
            self.monitor.stop_monitoring()
    
    def demo_performance_report(self):
        """演示性能报告"""
        print("\n=== 性能报告演示 ===")
        
        try:
            print("收集性能数据...")
            self.monitor.start_monitoring()
            
            # 收集5分钟数据
            time.sleep(300)
            
            # 生成报告
            report = self.reporting.generate_performance_report(hours=1)
            
            print(f"报告生成时间: {report['report_time']}")
            print(f"监控时间范围: {report['time_range_hours']} 小时")
            
            # 健康摘要
            health = report['health_summary']
            print(f"整体健康分数: {health['overall_score']}/100")
            print(f"系统状态: {health['status']}")
            print(f"活跃告警: {health['active_alerts']} 个")
            
            # 性能摘要
            performance = report['performance_summary']
            throughput = performance.get('throughput', {})
            if throughput:
                print(f"平均吞吐量: {throughput.get('in_avg', 0):.1f} 消息/秒")
            
            # 瓶颈分析
            bottlenecks = report['bottlenecks']
            if bottlenecks:
                print("检测到的性能瓶颈:")
                for bottleneck in bottlenecks:
                    print(f"  - {bottleneck['type']} ({bottleneck['severity']}): {bottleneck['description']}")
            else:
                print("未检测到性能瓶颈")
            
            # 优化建议
            recommendations = report['recommendations']
            if recommendations:
                print("优化建议:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
            
            # 可用性
            availability = report['availability']
            print(f"系统可用性: {availability['availability_percent']:.1f}%")
            
        except Exception as e:
            print(f"报告演示失败: {e}")
        finally:
            self.monitor.stop_monitoring()
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("RabbitMQ性能监控演示开始")
        print("=" * 50)
        
        try:
            # 1. 连接测试
            self.demo_connection_test()
            
            # 2. 基础监控
            self.demo_basic_monitoring()
            
            # 3. 告警系统
            self.demo_alert_system()
            
            # 4. 性能报告
            self.demo_performance_report()
            
            print("\n演示完成!")
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
            self.monitor.stop_monitoring()
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")
            self.monitor.stop_monitoring()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    demo = PerformanceMonitoringDemo()
    demo.run_complete_demo()