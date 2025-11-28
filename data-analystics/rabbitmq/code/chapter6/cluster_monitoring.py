#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ集群监控与告警系统

这个模块提供了完整的集群监控功能：
- 实时节点状态监控
- 队列性能指标收集
- 告警规则配置
- 性能报告生成
- 历史数据分析
"""

import pika
import json
import time
import threading
import requests
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ClusterMetrics:
    """集群指标数据类"""
    timestamp: str
    node_name: str
    queue_name: str
    message_count: int
    consumer_count: int
    memory_usage: int
    cpu_usage: float
    connection_count: int
    channel_count: int

@dataclass
class AlertRule:
    """告警规则数据类"""
    name: str
    metric: str
    condition: str  # '>', '<', '>=', '<='
    threshold: float
    duration: int  # 持续时间（秒）
    severity: str  # 'info', 'warning', 'critical'
    enabled: bool = True

class ClusterNodeMonitor:
    """单个节点监控器"""
    
    def __init__(self, node_name: str, host: str, port: int = 5672, 
                 username: str = 'admin', password: str = 'admin123'):
        self.node_name = node_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self.is_connected = False
        
        # 监控历史数据
        self.metrics_history = deque(maxlen=1000)  # 保留1000条记录
        self.alerts = []
        
    def connect(self) -> bool:
        """连接到节点"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=30,
                connection_attempts=3,
                retry_delay=5
            )
            
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            self.is_connected = True
            
            logger.info(f"✅ 连接到节点: {self.node_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接节点失败 {self.node_name}: {e}")
            self.is_connected = False
            return False
    
    def collect_system_metrics(self) -> Dict:
        """收集系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'disk_usage': disk.percent,
                'disk_free': disk.free,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 收集系统指标失败 {self.node_name}: {e}")
            return {}
    
    def collect_queue_metrics(self) -> List[Dict]:
        """收集队列指标"""
        if not self.is_connected:
            return []
        
        queue_metrics = []
        
        try:
            # 声明临时队列获取队列列表
            result = self.channel.queue_declare('', exclusive=True, auto_delete=True)
            
            # 获取所有队列信息（使用HTTP API）
            api_url = f"http://{self.host}:15672/api/queues"
            auth = (self.username, self.password)
            
            response = requests.get(api_url, auth=auth, timeout=10)
            if response.status_code == 200:
                queues_data = response.json()
                
                for queue_data in queues_data:
                    metrics = ClusterMetrics(
                        timestamp=datetime.now().isoformat(),
                        node_name=self.node_name,
                        queue_name=queue_data.get('name', ''),
                        message_count=queue_data.get('messages', 0),
                        consumer_count=queue_data.get('consumers', 0),
                        memory_usage=queue_data.get('memory', 0),
                        cpu_usage=0.0,  # 通过系统收集
                        connection_count=len(queue_data.get('node_details', {}).get('channels', [])),
                        channel_count=queue_data.get('channels', 0)
                    )
                    
                    queue_metrics.append(asdict(metrics))
                    
        except Exception as e:
            logger.error(f"❌ 收集队列指标失败 {self.node_name}: {e}")
        
        return queue_metrics
    
    def collect_cluster_metrics(self) -> Dict:
        """收集集群整体指标"""
        if not self.is_connected:
            return {}
        
        try:
            api_url = f"http://{self.host}:15672/api/overview"
            auth = (self.username, self.password)
            
            response = requests.get(api_url, auth=auth, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'total_connections': data.get('connection_totals', {}).get('current', 0),
                    'total_channels': data.get('channel_totals', {}).get('current', 0),
                    'total_queues': data.get('queue_totals', {}).get('messages', 0),
                    'object_totals': data.get('object_totals', {}),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ 收集集群指标失败 {self.node_name}: {e}")
        
        return {}
    
    def collect_all_metrics(self) -> Dict:
        """收集所有指标"""
        timestamp = datetime.now().isoformat()
        
        # 收集系统指标
        system_metrics = self.collect_system_metrics()
        
        # 收集队列指标
        queue_metrics = self.collect_queue_metrics()
        
        # 收集集群指标
        cluster_metrics = self.collect_cluster_metrics()
        
        metrics_data = {
            'node_name': self.node_name,
            'timestamp': timestamp,
            'system': system_metrics,
            'queues': queue_metrics,
            'cluster': cluster_metrics,
            'status': 'connected' if self.is_connected else 'disconnected'
        }
        
        # 保存到历史记录
        self.metrics_history.append(metrics_data)
        
        return metrics_data
    
    def disconnect(self):
        """断开连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.is_connected = False
            logger.info(f"🔌 断开节点连接: {self.node_name}")

class ClusterAlertManager:
    """集群告警管理器"""
    
    def __init__(self, notification_callbacks: Optional[List[Callable]] = None):
        self.rules = []
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.notification_callbacks = notification_callbacks or []
        
        # 默认告警规则
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """设置默认告警规则"""
        default_rules = [
            AlertRule("高内存使用", "memory_usage", ">", 80, 60, "warning"),
            AlertRule("极高内存使用", "memory_usage", ">", 95, 30, "critical"),
            AlertRule("高CPU使用", "cpu_usage", ">", 80, 60, "warning"),
            AlertRule("极高CPU使用", "cpu_usage", ">", 95, 30, "critical"),
            AlertRule("队列消息积压", "queue_messages", ">", 1000, 120, "warning"),
            AlertRule("队列消息严重积压", "queue_messages", ">", 10000, 60, "critical"),
            AlertRule("节点离线", "status", "==", 0, 10, "critical"),
            AlertRule("无消费者", "consumers", "<", 1, 180, "warning")
        ]
        
        self.rules = default_rules
        logger.info(f"📋 设置了 {len(default_rules)} 个默认告警规则")
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules.append(rule)
        logger.info(f"➕ 添加告警规则: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """删除告警规则"""
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
        logger.info(f"➖ 删除告警规则: {rule_name}")
    
    def evaluate_metrics(self, metrics_data: Dict) -> List[Dict]:
        """评估指标并生成告警"""
        triggered_alerts = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            alert = self._check_rule(rule, metrics_data)
            if alert:
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def _check_rule(self, rule: AlertRule, metrics_data: Dict) -> Optional[Dict]:
        """检查单个告警规则"""
        try:
            metric_value = self._get_metric_value(metrics_data, rule.metric)
            if metric_value is None:
                return None
            
            # 检查条件
            condition_met = self._evaluate_condition(metric_value, rule.condition, rule.threshold)
            
            if condition_met:
                # 创建告警记录
                alert = {
                    'id': f"{rule.name}_{metrics_data['node_name']}_{int(time.time())}",
                    'name': rule.name,
                    'rule': rule,
                    'metric': rule.metric,
                    'value': metric_value,
                    'threshold': rule.threshold,
                    'condition': rule.condition,
                    'node': metrics_data['node_name'],
                    'timestamp': metrics_data['timestamp'],
                    'severity': rule.severity,
                    'status': 'triggered'
                }
                
                # 检查是否为持续告警
                if rule.duration > 0:
                    alert_key = f"{rule.name}_{metrics_data['node_name']}"
                    if alert_key not in self.active_alerts:
                        self.active_alerts[alert_key] = {
                            'first_triggered': time.time(),
                            'alert': alert
                        }
                    else:
                        duration_passed = time.time() - self.active_alerts[alert_key]['first_triggered']
                        if duration_passed < rule.duration:
                            return None  # 持续时间未到，不触发告警
                        else:
                            alert['duration'] = duration_passed
                else:
                    # 非持续告警，立即触发
                    alert_key = f"{rule.name}_{metrics_data['node_name']}"
                    self.active_alerts[alert_key] = {
                        'first_triggered': time.time(),
                        'alert': alert
                    }
                
                logger.warning(f"🚨 触发告警: {rule.name} - {metrics_data['node_name']}: {metric_value}")
                
                # 发送通知
                self._send_notifications(alert)
                
                return alert
        
        except Exception as e:
            logger.error(f"❌ 检查告警规则失败 {rule.name}: {e}")
        
        return None
    
    def _get_metric_value(self, metrics_data: Dict, metric: str) -> Optional[float]:
        """获取指标值"""
        try:
            if metric == "memory_usage":
                return metrics_data.get('system', {}).get('memory_usage', 0)
            elif metric == "cpu_usage":
                return metrics_data.get('system', {}).get('cpu_usage', 0)
            elif metric == "status":
                return 1.0 if metrics_data.get('status') == 'connected' else 0.0
            elif metric.startswith("queue_"):
                queue_name = metric.split("_")[1]  # 简化处理
                for queue_metrics in metrics_data.get('queues', []):
                    return float(queue_metrics.get('message_count', 0))
            elif metric == "queue_messages":
                # 返回最大队列消息数
                max_messages = 0
                for queue_metrics in metrics_data.get('queues', []):
                    max_messages = max(max_messages, queue_metrics.get('message_count', 0))
                return float(max_messages)
            elif metric == "consumers":
                # 返回最小消费者数
                min_consumers = float('inf')
                for queue_metrics in metrics_data.get('queues', []):
                    min_consumers = min(min_consumers, queue_metrics.get('consumer_count', 0))
                return min_consumers if min_consumers != float('inf') else 0.0
            
        except Exception as e:
            logger.error(f"❌ 获取指标值失败 {metric}: {e}")
        
        return None
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """评估条件"""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        
        return False
    
    def _send_notifications(self, alert: Dict):
        """发送告警通知"""
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"❌ 告警通知发送失败: {e}")
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        for alert_key, alert_info in list(self.active_alerts.items()):
            if alert_info['alert']['id'] == alert_id:
                alert_info['alert']['status'] = 'resolved'
                alert_info['alert']['resolved_at'] = datetime.now().isoformat()
                
                # 添加到历史记录
                self.alert_history.append(alert_info['alert'])
                
                # 从活动告警中移除
                del self.active_alerts[alert_key]
                
                logger.info(f"✅ 告警已解决: {alert_id}")
                break

class ClusterMonitor:
    """集群监控主类"""
    
    def __init__(self, cluster_config: List[Dict], alert_config: Optional[Dict] = None):
        self.cluster_config = cluster_config
        self.nodes = []
        self.alert_manager = ClusterAlertManager()
        
        # 监控配置
        self.monitoring_interval = 30  # 30秒
        self.is_monitoring = False
        
        # 数据存储
        self.global_metrics_history = deque(maxlen=10000)
        
        # 设置告警回调
        if alert_config:
            self._setup_alert_callbacks(alert_config)
        
        # 初始化节点
        self._initialize_nodes()
    
    def _initialize_nodes(self):
        """初始化节点监控器"""
        for config in self.cluster_config:
            node_monitor = ClusterNodeMonitor(
                node_name=config['name'],
                host=config['host'],
                port=config.get('port', 5672),
                username=config.get('username', 'admin'),
                password=config.get('password', 'admin123')
            )
            self.nodes.append(node_monitor)
        
        logger.info(f"🔧 初始化了 {len(self.nodes)} 个节点监控器")
    
    def _setup_alert_callbacks(self, alert_config: Dict):
        """设置告警回调函数"""
        def log_alert(alert):
            logger.warning(f"🚨 告警: {alert['name']} - {alert['node']} - {alert['value']}")
        
        def email_alert(alert):
            if 'email' in alert_config:
                # 这里可以集成邮件发送功能
                logger.info(f"📧 邮件告警: {alert['name']} - {alert['node']}")
        
        def webhook_alert(alert):
            if 'webhook_url' in alert_config:
                try:
                    payload = {
                        'alert_name': alert['name'],
                        'node': alert['node'],
                        'severity': alert['severity'],
                        'value': alert['value'],
                        'timestamp': alert['timestamp']
                    }
                    requests.post(alert_config['webhook_url'], json=payload, timeout=5)
                except Exception as e:
                    logger.error(f"❌ Webhook告警发送失败: {e}")
        
        self.alert_manager.notification_callbacks = [log_alert]
        if 'email' in alert_config:
            self.alert_manager.notification_callbacks.append(email_alert)
        if 'webhook_url' in alert_config:
            self.alert_manager.notification_callbacks.append(webhook_alert)
    
    def connect_all_nodes(self) -> Dict[str, bool]:
        """连接所有节点"""
        results = {}
        threads = []
        
        def connect_node(node):
            results[node.node_name] = node.connect()
        
        for node in self.nodes:
            thread = threading.Thread(target=connect_node, args=(node,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        connected_count = sum(results.values())
        logger.info(f"📊 节点连接结果: {connected_count}/{len(self.nodes)} 连接成功")
        
        return results
    
    def start_monitoring(self):
        """开始监控"""
        logger.info("🔍 开始集群监控...")
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                # 收集所有节点的指标
                all_metrics = []
                for node in self.nodes:
                    if node.is_connected:
                        metrics = node.collect_all_metrics()
                        if metrics:
                            all_metrics.append(metrics)
                
                # 全局告警检查
                for metrics in all_metrics:
                    alerts = self.alert_manager.evaluate_metrics(metrics)
                    # 告警已通过回调处理
                
                # 保存全局历史数据
                self.global_metrics_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'nodes_metrics': all_metrics,
                    'cluster_summary': self._generate_cluster_summary(all_metrics)
                })
                
                # 输出监控摘要
                if all_metrics:
                    summary = self._generate_cluster_summary(all_metrics)
                    logger.info(f"📊 集群监控摘要: {summary}")
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"❌ 监控异常: {e}")
                time.sleep(5)
        
        logger.info("🏁 集群监控停止")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        logger.info("⏹️  正在停止监控...")
    
    def _generate_cluster_summary(self, all_metrics: List[Dict]) -> Dict:
        """生成集群摘要"""
        if not all_metrics:
            return {}
        
        summary = {
            'total_nodes': len(self.nodes),
            'connected_nodes': len(all_metrics),
            'total_messages': 0,
            'total_consumers': 0,
            'average_memory': 0,
            'average_cpu': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        memory_usage = []
        cpu_usage = []
        
        for metrics in all_metrics:
            # 统计队列指标
            for queue_metrics in metrics.get('queues', []):
                summary['total_messages'] += queue_metrics.get('message_count', 0)
                summary['total_consumers'] += queue_metrics.get('consumer_count', 0)
            
            # 系统指标
            system_metrics = metrics.get('system', {})
            memory_usage.append(system_metrics.get('memory_usage', 0))
            cpu_usage.append(system_metrics.get('cpu_usage', 0))
        
        # 计算平均值
        if memory_usage:
            summary['average_memory'] = sum(memory_usage) / len(memory_usage)
        if cpu_usage:
            summary['average_cpu'] = sum(cpu_usage) / len(cpu_usage)
        
        return summary
    
    def generate_performance_report(self, duration_hours: int = 24) -> Dict:
        """生成性能报告"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=duration_hours)
        
        # 筛选时间范围内的数据
        recent_data = [
            data for data in self.global_metrics_history
            if start_time <= datetime.fromisoformat(data['timestamp']) <= end_time
        ]
        
        if not recent_data:
            return {'error': '没有足够的历史数据生成报告'}
        
        # 分析数据
        messages_over_time = []
        cpu_over_time = []
        memory_over_time = []
        alert_counts = defaultdict(int)
        
        for data in recent_data:
            cluster_summary = data.get('cluster_summary', {})
            messages_over_time.append(cluster_summary.get('total_messages', 0))
            cpu_over_time.append(cluster_summary.get('average_cpu', 0))
            memory_over_time.append(cluster_summary.get('average_memory', 0))
        
        # 告警统计
        for alert in self.alert_manager.alert_history:
            alert_counts[alert['severity']] += 1
        
        report = {
            'report_period': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_hours': duration_hours
            },
            'statistics': {
                'max_messages': max(messages_over_time) if messages_over_time else 0,
                'min_messages': min(messages_over_time) if messages_over_time else 0,
                'avg_messages': sum(messages_over_time) / len(messages_over_time) if messages_over_time else 0,
                'max_cpu': max(cpu_over_time) if cpu_over_time else 0,
                'min_cpu': min(cpu_over_time) if cpu_over_time else 0,
                'avg_cpu': sum(cpu_over_time) / len(cpu_over_time) if cpu_over_time else 0,
                'max_memory': max(memory_over_time) if memory_over_time else 0,
                'min_memory': min(memory_over_time) if memory_over_time else 0,
                'avg_memory': sum(memory_over_time) / len(memory_over_time) if memory_over_time else 0
            },
            'alerts_summary': dict(alert_counts),
            'recommendations': self._generate_recommendations(recent_data)
        }
        
        return report
    
    def _generate_recommendations(self, data: List[Dict]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 分析历史数据生成建议
        if len(data) >= 10:
            # 检查趋势
            last_10_summaries = [d.get('cluster_summary', {}) for d in data[-10:]]
            
            avg_messages = [s.get('total_messages', 0) for s in last_10_summaries]
            avg_cpu = [s.get('average_cpu', 0) for s in last_10_summaries]
            avg_memory = [s.get('average_memory', 0) for s in last_10_summaries]
            
            if sum(avg_messages) / len(avg_messages) > 1000:
                recommendations.append("队列消息积压较多，建议增加消费者数量或优化消息处理速度")
            
            if sum(avg_cpu) / len(avg_cpu) > 80:
                recommendations.append("CPU使用率较高，建议升级硬件或优化应用程序性能")
            
            if sum(avg_memory) / len(avg_memory) > 80:
                recommendations.append("内存使用率较高，建议增加内存容量或优化内存使用")
        
        return recommendations
    
    def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理监控资源...")
        
        self.stop_monitoring()
        
        for node in self.nodes:
            node.disconnect()
        
        logger.info("✅ 监控资源清理完成")

def main():
    """主函数 - 演示监控功能"""
    
    # 集群配置
    cluster_config = [
        {'name': 'node1', 'host': 'rabbitmq-node1', 'port': 5672},
        {'name': 'node2', 'host': 'rabbitmq-node2', 'port': 5672},
        {'name': 'node3', 'host': 'rabbitmq-node3', 'port': 5672}
    ]
    
    # 告警配置
    alert_config = {
        'email': 'admin@company.com',  # 邮件接收者
        'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'  # Slack webhook
    }
    
    # 创建集群监控器
    monitor = ClusterMonitor(cluster_config, alert_config)
    
    try:
        # 连接所有节点
        logger.info("🔗 连接集群节点...")
        monitor.connect_all_nodes()
        
        # 开始监控（后台运行）
        logger.info("🔍 启动监控...")
        monitoring_thread = threading.Thread(target=monitor.start_monitoring)
        monitoring_thread.start()
        
        # 运行5分钟监控演示
        print("📊 开始5分钟监控演示...")
        time.sleep(300)  # 5分钟
        
        # 生成性能报告
        logger.info("📈 生成性能报告...")
        report = monitor.generate_performance_report(duration_hours=1)
        logger.info(f"📋 性能报告: {json.dumps(report, indent=2, ensure_ascii=False)}")
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  用户中断")
    finally:
        monitor.cleanup()

if __name__ == '__main__':
    main()