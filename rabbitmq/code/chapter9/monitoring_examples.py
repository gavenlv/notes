#!/usr/bin/env python3
"""
RabbitMQ监控与运维代码示例
第9章：RabbitMQ监控与运维
"""

import json
import time
import logging
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import pika
import psutil
import docker

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """监控配置"""
    rabbitmq_url: str = "amqp://admin:password@localhost:5672"
    rabbitmq_api_url: str = "http://localhost:15672"
    username: str = "admin"
    password: str = "password"
    prometheus_url: str = "http://localhost:9090"
    grafana_url: str = "http://localhost:3000"
    alertmanager_url: str = "http://localhost:9093"


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics_cache = {}
        self.last_check_time = {}
        
    def collect_system_metrics(self) -> Dict:
        """收集系统指标"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict(),
            'process_count': len(psutil.pids()),
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }
        
    def collect_rabbitmq_metrics(self) -> Dict:
        """收集RabbitMQ指标"""
        try:
            # 获取连接信息
            connections = self._get_api_data("/api/connections")
            
            # 获取队列信息
            queues = self._get_api_data("/api/queues")
            
            # 获取节点信息
            nodes = self._get_api_data("/api/nodes")
            
            # 获取集群概览
            overview = self._get_api_data("/api/overview")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'connections': {
                    'total_count': len(connections),
                    'channels': sum(conn.get('channels', 0) for conn in connections),
                    'client_properties': [conn.get('client_properties', {}) for conn in connections[:5]]
                },
                'queues': {
                    'total_count': len(queues),
                    'total_messages': sum(queue.get('messages', 0) for queue in queues),
                    'queue_details': [
                        {
                            'name': queue.get('name'),
                            'messages': queue.get('messages'),
                            'durable': queue.get('durable'),
                            'auto_delete': queue.get('auto_delete')
                        }
                        for queue in queues[:10]
                    ]
                },
                'nodes': {
                    'total_count': len(nodes),
                    'running_count': len([node for node in nodes if node.get('running', False)]),
                    'node_details': [
                        {
                            'name': node.get('name'),
                            'running': node.get('running'),
                            'mem_used': node.get('mem_used'),
                            'fd_used': node.get('fd_used'),
                            'sockets_used': node.get('sockets_used')
                        }
                        for node in nodes
                    ]
                },
                'overview': overview
            }
        except Exception as e:
            logger.error(f"收集RabbitMQ指标失败: {e}")
            return {}
            
    def _get_api_data(self, endpoint: str) -> List[Dict]:
        """获取API数据"""
        url = f"{self.config.rabbitmq_api_url}{endpoint}"
        try:
            response = requests.get(url, auth=(self.config.username, self.config.password))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取API数据失败 {endpoint}: {e}")
            return []
            
    def monitor_message_throughput(self, queue_name: str = None, duration: int = 60) -> Dict:
        """监控消息吞吐量"""
        start_time = datetime.now()
        messages_published = 0
        messages_consumed = 0
        message_sizes = []
        
        def message_callback(ch, method, properties, body):
            nonlocal messages_consumed
            messages_consumed += 1
            message_sizes.append(len(body))
            
        # 创建临时连接
        connection = pika.BlockingConnection(pika.URLParameters(self.config.rabbitmq_url))
        channel = connection.channel()
        
        # 设置消费者
        if queue_name:
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=message_callback,
                auto_ack=True
            )
            
            # 开始监控
            logger.info(f"开始监控队列 {queue_name} 的吞吐量...")
            
            try:
                while (datetime.now() - start_time).total_seconds() < duration:
                    connection.process_data_events(time_limit=1)
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                logger.info("监控被中断")
            finally:
                connection.close()
                
        # 模拟消息发布
        test_connection = pika.BlockingConnection(pika.URLParameters(self.config.rabbitmq_url))
        test_channel = test_connection.channel()
        
        for i in range(100):  # 发布100条测试消息
            message = f"test_message_{i}_{time.time()}".encode()
            test_channel.basic_publish(
                exchange='',
                routing_key=queue_name or 'test_queue',
                body=message
            )
            messages_published += 1
            
        test_connection.close()
        
        # 计算吞吐量指标
        end_time = datetime.now()
        actual_duration = (end_time - start_time).total_seconds()
        
        return {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': actual_duration,
            'messages_published': messages_published,
            'messages_consumed': messages_consumed,
            'publish_rate_per_second': messages_published / actual_duration,
            'consume_rate_per_second': messages_consumed / actual_duration,
            'average_message_size': sum(message_sizes) / len(message_sizes) if message_sizes else 0,
            'throughput_efficiency': (messages_consumed / messages_published) * 100 if messages_published > 0 else 0
        }


class AlertManager:
    """告警管理器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_rules = []
        self.alert_history = []
        self.suppression_rules = defaultdict(timedelta)
        
    def add_alert_rule(self, name: str, condition: str, threshold: float, 
                      severity: str, duration: int = 300, 
                      action: str = "email") -> None:
        """添加告警规则"""
        rule = {
            'name': name,
            'condition': condition,
            'threshold': threshold,
            'severity': severity,
            'duration': duration,
            'action': action,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        self.alert_rules.append(rule)
        
    def evaluate_alerts(self, metrics: Dict) -> List[Dict]:
        """评估告警"""
        active_alerts = []
        current_time = datetime.now()
        
        for rule in self.alert_rules:
            if not rule['enabled']:
                continue
                
            value = self._extract_metric_value(metrics, rule['condition'])
            
            if self._check_threshold(value, rule['threshold']):
                alert = {
                    'rule_name': rule['name'],
                    'severity': rule['severity'],
                    'condition': rule['condition'],
                    'value': value,
                    'threshold': rule['threshold'],
                    'timestamp': current_time.isoformat(),
                    'message': f"{rule['name']} triggered: {value} >= {rule['threshold']}"
                }
                
                # 检查告警抑制
                if self._should_suppress_alert(alert):
                    logger.info(f"告警被抑制: {rule['name']}")
                    continue
                    
                active_alerts.append(alert)
                self._send_alert(alert)
                
        return active_alerts
        
    def _extract_metric_value(self, metrics: Dict, condition: str) -> float:
        """提取指标值"""
        # 简化的指标提取逻辑
        condition_parts = condition.split('.')
        value = metrics
        
        for part in condition_parts:
            if isinstance(value, dict):
                value = value.get(part, 0)
            else:
                return 0.0
                
        return float(value) if value else 0.0
        
    def _check_threshold(self, value: float, threshold: float) -> bool:
        """检查阈值"""
        return value >= threshold
        
    def _should_suppress_alert(self, alert: Dict) -> bool:
        """检查告警抑制"""
        rule_name = alert['rule_name']
        last_alert_time = None
        
        # 查找最近的相同告警
        for stored_alert in reversed(self.alert_history):
            if stored_alert['rule_name'] == rule_name:
                last_alert_time = stored_alert['timestamp']
                break
                
        if last_alert_time:
            last_time = datetime.fromisoformat(last_alert_time)
            suppression_period = self.suppression_rules.get(rule_name, timedelta(minutes=5))
            
            if datetime.now() - last_time < suppression_period:
                return True
                
        return False
        
    def _send_alert(self, alert: Dict):
        """发送告警"""
        if alert['action'] == 'email':
            self._send_email_alert(alert)
        elif alert['action'] == 'slack':
            self._send_slack_alert(alert)
        elif alert['action'] == 'webhook':
            self._send_webhook_alert(alert)
            
        # 记录告警历史
        self.alert_history.append(alert)
        logger.warning(f"发送告警: {alert['message']}")
        
    def _send_email_alert(self, alert: Dict):
        """发送邮件告警"""
        logger.info(f"邮件告警: {alert['message']}")
        # 这里应该实现实际的邮件发送逻辑
        
    def _send_slack_alert(self, alert: Dict):
        """发送Slack告警"""
        logger.info(f"Slack告警: {alert['message']}")
        # 这里应该实现实际的Slack API调用逻辑
        
    def _send_webhook_alert(self, alert: Dict):
        """发送Webhook告警"""
        try:
            payload = {
                'alert_name': alert['rule_name'],
                'severity': alert['severity'],
                'message': alert['message'],
                'value': alert['value'],
                'timestamp': alert['timestamp']
            }
            
            response = requests.post(
                "http://localhost:5000/webhook/alerts",
                json=payload,
                timeout=10
            )
            
            logger.info(f"Webhook告警发送状态: {response.status_code}")
            
        except Exception as e:
            logger.error(f"发送Webhook告警失败: {e}")


class ClusterHealthChecker:
    """集群健康检查器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.docker_client = docker.from_env()
        
    def check_cluster_health(self) -> Dict:
        """检查集群健康状态"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'node_status': {},
            'queue_status': {},
            'connection_status': {},
            'alerts': []
        }
        
        # 检查节点状态
        nodes = self._get_nodes()
        healthy_nodes = 0
        total_nodes = len(nodes)
        
        for node in nodes:
            node_health = self._check_node_health(node['name'])
            health_status['node_status'][node['name']] = node_health
            
            if node_health['status'] == 'healthy':
                healthy_nodes += 1
            else:
                health_status['alerts'].append(f"Node {node['name']}: {node_health['status']}")
                
        # 检查队列状态
        queues = self._get_queues()
        problematic_queues = []
        
        for queue in queues:
            queue_health = self._check_queue_health(queue['name'])
            health_status['queue_status'][queue['name']] = queue_health
            
            if not queue_health['healthy']:
                problematic_queues.append(queue['name'])
                health_status['alerts'].append(f"Queue {queue['name']}: {queue_health['issue']}")
                
        # 检查连接状态
        connections = self._get_connections()
        suspicious_connections = []
        
        for connection in connections:
            conn_health = self._check_connection_health(connection)
            if not conn_health['healthy']:
                suspicious_connections.append(connection.get('name', 'unknown'))
                
        # 评估整体健康状态
        if healthy_nodes < total_nodes:
            health_status['overall_status'] = 'degraded'
        if len(problematic_queues) > len(queues) * 0.1:
            health_status['overall_status'] = 'warning'
        if healthy_nodes == 0:
            health_status['overall_status'] = 'critical'
            
        health_status['summary'] = {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'total_queues': len(queues),
            'problematic_queues': len(problematic_queues),
            'total_connections': len(connections),
            'suspicious_connections': len(suspicious_connections)
        }
        
        return health_status
        
    def _get_nodes(self) -> List[Dict]:
        """获取节点信息"""
        try:
            url = f"{self.config.rabbitmq_api_url}/api/nodes"
            response = requests.get(url, auth=(self.config.username, self.config.password))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取节点信息失败: {e}")
            return []
            
    def _get_queues(self) -> List[Dict]:
        """获取队列信息"""
        try:
            url = f"{self.config.rabbitmq_api_url}/api/queues"
            response = requests.get(url, auth=(self.config.username, self.config.password))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取队列信息失败: {e}")
            return []
            
    def _get_connections(self) -> List[Dict]:
        """获取连接信息"""
        try:
            url = f"{self.config.rabbitmq_api_url}/api/connections"
            response = requests.get(url, auth=(self.config.username, self.config.password))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取连接信息失败: {e}")
            return []
            
    def _check_node_health(self, node_name: str) -> Dict:
        """检查节点健康状态"""
        try:
            # 检查节点是否运行
            url = f"{self.config.rabbitmq_api_url}/api/nodes/{node_name}"
            response = requests.get(url, auth=(self.config.username, self.config.password))
            response.raise_for_status()
            node_data = response.json()
            
            status = 'healthy' if node_data.get('running', False) else 'down'
            
            # 检查资源使用
            mem_used = node_data.get('mem_used', 0)
            fd_used = node_data.get('fd_used', 0)
            
            # 资源警告
            warnings = []
            if mem_used > 2 * 1024 * 1024 * 1024:  # 2GB
                warnings.append('High memory usage')
            if fd_used > 1000:
                warnings.append('High file descriptor usage')
                
            return {
                'status': status,
                'mem_used': mem_used,
                'fd_used': fd_used,
                'warnings': warnings,
                'uptime': node_data.get('uptime')
            }
            
        except Exception as e:
            logger.error(f"检查节点健康失败 {node_name}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def _check_queue_health(self, queue_name: str) -> Dict:
        """检查队列健康状态"""
        try:
            url = f"{self.config.rabbitmq_api_url}/api/queues/%2F/{queue_name}"
            response = requests.get(url, auth=(self.config.username, self.config.password))
            response.raise_for_status()
            queue_data = response.json()
            
            messages = queue_data.get('messages', 0)
            durable = queue_data.get('durable', False)
            auto_delete = queue_data.get('auto_delete', False)
            
            issue = None
            if messages > 10000:
                issue = f'High message count: {messages}'
            elif messages < 0:
                issue = 'Negative message count'
            elif not durable:
                issue = 'Queue is not durable'
            elif auto_delete:
                issue = 'Queue has auto_delete enabled'
                
            return {
                'healthy': issue is None,
                'issue': issue,
                'messages': messages,
                'consumers': queue_data.get('consumers', 0),
                'durable': durable
            }
            
        except Exception as e:
            logger.error(f"检查队列健康失败 {queue_name}: {e}")
            return {
                'healthy': False,
                'error': str(e)
            }
            
    def _check_connection_health(self, connection: Dict) -> Dict:
        """检查连接健康状态"""
        try:
            # 检查连接状态
            state = connection.get('state', 'unknown')
            client_properties = connection.get('client_properties', {})
            
            # 检查是否有异常
            issues = []
            if state not in ['running', 'blocked']:
                issues.append(f'Unusual connection state: {state}')
                
            # 检查连接时间
            created_at = connection.get('connected_at')
            if created_at:
                connected_time = datetime.fromtimestamp(created_at)
                if datetime.now() - connected_time > timedelta(hours=24):
                    issues.append('Long running connection')
                    
            return {
                'healthy': len(issues) == 0,
                'issues': issues,
                'state': state,
                'client_properties': client_properties
            }
            
        except Exception as e:
            logger.error(f"检查连接健康失败: {e}")
            return {
                'healthy': False,
                'error': str(e)
            }


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.log_patterns = [
            {
                'name': 'connection_error',
                'pattern': r'Connection error.*',
                'severity': 'warning',
                'action': 'log'
            },
            {
                'name': 'queue_full',
                'pattern': r'Queue.*is full.*',
                'severity': 'critical',
                'action': 'alert'
            },
            {
                'name': 'memory_warning',
                'pattern': r'Memory alarm.*',
                'severity': 'warning',
                'action': 'alert'
            },
            {
                'name': 'disk_warning',
                'pattern': r'Disk alarm.*',
                'severity': 'critical',
                'action': 'alert'
            }
        ]
        
    def analyze_log_file(self, log_file_path: str, time_range: int = 3600) -> Dict:
        """分析日志文件"""
        try:
            current_time = datetime.now()
            start_time = current_time - timedelta(seconds=time_range)
            
            pattern_counts = defaultdict(int)
            alerts = []
            
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # 检查时间戳
                    try:
                        line_time = self._parse_log_timestamp(line)
                        if line_time and line_time >= start_time:
                            # 检查模式匹配
                            for pattern in self.log_patterns:
                                import re
                                if re.search(pattern['pattern'], line):
                                    pattern_counts[pattern['name']] += 1
                                    
                                    if pattern['action'] == 'alert':
                                        alerts.append({
                                            'pattern': pattern['name'],
                                            'severity': pattern['severity'],
                                            'message': line.strip(),
                                            'timestamp': line_time.isoformat()
                                        })
                    except Exception as e:
                        # 忽略无法解析的行
                        continue
                        
            return {
                'analysis_period_seconds': time_range,
                'pattern_counts': dict(pattern_counts),
                'alerts': alerts,
                'summary': self._generate_log_summary(pattern_counts, alerts),
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"分析日志文件失败: {e}")
            return {'error': str(e)}
            
    def _parse_log_timestamp(self, log_line: str) -> Optional[datetime]:
        """解析日志时间戳"""
        # RabbitMQ日志格式: 2024-01-01 12:00:00.000 [info] <...> message
        import re
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.[\d{3}]'
        match = re.search(timestamp_pattern, log_line)
        
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
                
        return None
        
    def _generate_log_summary(self, pattern_counts: Dict, alerts: List[Dict]) -> Dict:
        """生成日志摘要"""
        total_patterns = sum(pattern_counts.values())
        critical_alerts = len([alert for alert in alerts if alert['severity'] == 'critical'])
        warning_alerts = len([alert for alert in alerts if alert['severity'] == 'warning'])
        
        return {
            'total_pattern_matches': total_patterns,
            'critical_alerts': critical_alerts,
            'warning_alerts': warning_alerts,
            'risk_level': 'high' if critical_alerts > 0 else 'medium' if warning_alerts > 0 else 'low',
            'most_common_pattern': max(pattern_counts, key=pattern_counts.get) if pattern_counts else None
        }


class CapacityPlanner:
    """容量规划器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.historical_data = []
        
    def collect_capacity_data(self, duration_hours: int = 24) -> Dict:
        """收集容量数据"""
        try:
            # 获取历史指标数据
            historical_metrics = self._get_historical_metrics(duration_hours)
            
            # 分析趋势
            trends = self._analyze_trends(historical_metrics)
            
            # 生成容量建议
            recommendations = self._generate_capacity_recommendations(trends)
            
            return {
                'collection_period_hours': duration_hours,
                'data_points': len(historical_metrics),
                'trends': trends,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"收集容量数据失败: {e}")
            return {'error': str(e)}
            
    def _get_historical_metrics(self, duration_hours: int) -> List[Dict]:
        """获取历史指标数据"""
        # 这里应该从Prometheus或监控系统获取历史数据
        # 简化实现，生成模拟数据
        metrics = []
        current_time = datetime.now()
        
        for i in range(duration_hours):
            timestamp = current_time - timedelta(hours=i)
            metric = {
                'timestamp': timestamp.isoformat(),
                'connection_count': 400 + i * 10 + (i % 20) * 5,  # 模拟连接数增长
                'queue_count': 80 + i,  # 模拟队列数增长
                'message_rate': 800 + i * 5,  # 模拟消息速率增长
                'memory_usage': 1.5 + i * 0.1,  # 模拟内存使用增长
                'disk_usage': 5.0 + i * 0.2,  # 模拟磁盘使用增长
                'cpu_usage': 30 + i * 0.5  # 模拟CPU使用增长
            }
            metrics.append(metric)
            
        return metrics
        
    def _analyze_trends(self, metrics: List[Dict]) -> Dict:
        """分析趋势"""
        if len(metrics) < 2:
            return {}
            
        trends = {}
        
        # 计算每种指标的增长率
        for metric_name in ['connection_count', 'queue_count', 'message_rate', 'memory_usage', 'disk_usage', 'cpu_usage']:
            values = [m[metric_name] for m in metrics if metric_name in m]
            
            if len(values) >= 2:
                # 简单线性回归计算增长率
                growth_rate = (values[-1] - values[0]) / len(values)
                
                # 计算趋势类型
                recent_values = values[-5:] if len(values) >= 5 else values
                if len(recent_values) >= 2:
                    recent_growth = recent_values[-1] - recent_values[0]
                    trend_type = 'increasing' if recent_growth > 0 else 'decreasing' if recent_growth < 0 else 'stable'
                else:
                    trend_type = 'unknown'
                    
                trends[metric_name] = {
                    'growth_rate_per_hour': growth_rate,
                    'current_value': values[-1],
                    'trend_type': trend_type,
                    'estimated_weekly_growth': growth_rate * 24 * 7
                }
                
        return trends
        
    def _generate_capacity_recommendations(self, trends: Dict) -> List[str]:
        """生成容量建议"""
        recommendations = []
        
        for metric_name, trend in trends.items():
            if trend['trend_type'] == 'increasing':
                weekly_growth = trend['estimated_weekly_growth']
                current_value = trend['current_value']
                
                if weekly_growth > 0:
                    # 预测下周的值
                    predicted_next_week = current_value + weekly_growth
                    
                    if metric_name == 'memory_usage':
                        if predicted_next_week > 3.5:
                            recommendations.append(f"内存使用量预计下周到 {predicted_next_week:.1f}GB，建议增加内存容量")
                        elif predicted_next_week > 3.0:
                            recommendations.append(f"内存使用量预计下周到 {predicted_next_week:.1f}GB，建议优化内存使用")
                            
                    elif metric_name == 'disk_usage':
                        if predicted_next_week > 40:
                            recommendations.append(f"磁盘使用量预计下周到 {predicted_next_week:.1f}GB，建议增加磁盘空间")
                        elif predicted_next_week > 30:
                            recommendations.append(f"磁盘使用量预计下周到 {predicted_next_week:.1f}GB，建议清理磁盘空间")
                            
                    elif metric_name == 'connection_count':
                        if predicted_next_week > 800:
                            recommendations.append(f"连接数预计下周到 {predicted_next_week:.0f}，建议考虑连接池优化")
                            
                    elif metric_name == 'queue_count':
                        if predicted_next_week > 200:
                            recommendations.append(f"队列数量预计下周到 {predicted_next_week:.0f}，建议考虑队列合并")
                            
        if not recommendations:
            recommendations.append("目前容量规划良好，暂无扩容建议")
            
        return recommendations


class MonitoringDashboard:
    """监控仪表板"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor(config)
        self.alert_manager = AlertManager(config)
        self.health_checker = ClusterHealthChecker(config)
        self.capacity_planner = CapacityPlanner(config)
        
        # 设置默认告警规则
        self._setup_default_alerts()
        
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        self.alert_manager.add_alert_rule(
            "High Memory Usage", 
            "memory_percent", 
            80.0, 
            "warning", 
            duration=300
        )
        
        self.alert_manager.add_alert_rule(
            "Critical Memory Usage", 
            "memory_percent", 
            90.0, 
            "critical", 
            duration=60
        )
        
        self.alert_manager.add_alert_rule(
            "High CPU Usage", 
            "cpu_percent", 
            80.0, 
            "warning", 
            duration=300
        )
        
        self.alert_manager.add_alert_rule(
            "Critical CPU Usage", 
            "cpu_percent", 
            90.0, 
            "critical", 
            duration=60
        )
        
        self.alert_manager.add_alert_rule(
            "High Disk Usage", 
            "disk_percent", 
            85.0, 
            "warning", 
            duration=300
        )
        
        self.alert_manager.add_alert_rule(
            "Critical Disk Usage", 
            "disk_percent", 
            95.0, 
            "critical", 
            duration=60
        )
        
    def run_comprehensive_monitoring(self) -> Dict:
        """运行综合监控"""
        logger.info("开始综合监控检查...")
        
        # 收集系统指标
        system_metrics = self.performance_monitor.collect_system_metrics()
        
        # 收集RabbitMQ指标
        rabbitmq_metrics = self.performance_monitor.collect_rabbitmq_metrics()
        
        # 检查集群健康
        cluster_health = self.health_checker.check_cluster_health()
        
        # 合并指标
        combined_metrics = {**system_metrics, **rabbitmq_metrics}
        
        # 评估告警
        alerts = self.alert_manager.evaluate_alerts(combined_metrics)
        
        # 收集容量数据
        capacity_data = self.capacity_planner.collect_capacity_data()
        
        # 生成综合报告
        report = {
            'monitoring_session': {
                'start_time': datetime.now().isoformat(),
                'duration_seconds': time.time() - time.time()  # 临时值，实际应记录开始时间
            },
            'system_metrics': system_metrics,
            'rabbitmq_metrics': rabbitmq_metrics,
            'cluster_health': cluster_health,
            'active_alerts': alerts,
            'capacity_analysis': capacity_data,
            'summary': {
                'overall_status': self._determine_overall_status(cluster_health, alerts),
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['severity'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['severity'] == 'warning']),
                'recommendations': self._generate_summary_recommendations(alerts, cluster_health, capacity_data)
            }
        }
        
        return report
        
    def _determine_overall_status(self, cluster_health: Dict, alerts: List[Dict]) -> str:
        """确定整体状态"""
        if cluster_health.get('overall_status') == 'critical':
            return 'critical'
            
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        if critical_alerts:
            return 'critical'
            
        warning_alerts = [a for a in alerts if a['severity'] == 'warning']
        if warning_alerts or cluster_health.get('overall_status') == 'degraded':
            return 'warning'
            
        if cluster_health.get('overall_status') == 'healthy':
            return 'healthy'
            
        return 'unknown'
        
    def _generate_summary_recommendations(self, alerts: List[Dict], cluster_health: Dict, capacity_data: Dict) -> List[str]:
        """生成摘要建议"""
        recommendations = []
        
        # 基于告警的建议
        if alerts:
            recommendations.append(f"发现 {len(alerts)} 个告警，请查看详细告警信息")
            
        # 基于集群健康的建议
        if cluster_health.get('overall_status') == 'degraded':
            recommendations.append("集群状态降级，建议检查节点健康状态")
        elif cluster_health.get('overall_status') == 'critical':
            recommendations.append("集群状态严重，建议立即检查和修复")
            
        # 基于容量分析的建议
        if capacity_data and 'recommendations' in capacity_data:
            recommendations.extend(capacity_data['recommendations'])
            
        if not recommendations:
            recommendations.append("系统运行正常，暂无特别建议")
            
        return recommendations
        
    def save_monitoring_report(self, report: Dict, file_path: str = None):
        """保存监控报告"""
        if not file_path:
            file_path = f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"监控报告已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存监控报告失败: {e}")


def interactive_monitoring_menu():
    """交互式监控菜单"""
    config = MonitoringConfig()
    dashboard = MonitoringDashboard(config)
    
    while True:
        print("\n" + "="*60)
        print("RabbitMQ 监控与运维系统")
        print("="*60)
        print("1. 收集系统指标")
        print("2. 收集RabbitMQ指标")
        print("3. 检查集群健康状态")
        print("4. 分析消息吞吐量")
        print("5. 运行综合监控")
        print("6. 配置告警规则")
        print("7. 容量规划分析")
        print("8. 分析日志文件")
        print("9. 保存监控报告")
        print("0. 退出")
        print("-"*60)
        
        choice = input("请选择操作 (0-9): ").strip()
        
        if choice == '0':
            print("感谢使用监控与运维系统！")
            break
        elif choice == '1':
            print("正在收集系统指标...")
            metrics = dashboard.performance_monitor.collect_system_metrics()
            print(json.dumps(metrics, indent=2, ensure_ascii=False))
        elif choice == '2':
            print("正在收集RabbitMQ指标...")
            metrics = dashboard.performance_monitor.collect_rabbitmq_metrics()
            print(json.dumps(metrics, indent=2, ensure_ascii=False))
        elif choice == '3':
            print("正在检查集群健康状态...")
            health = dashboard.health_checker.check_cluster_health()
            print(json.dumps(health, indent=2, ensure_ascii=False))
        elif choice == '4':
            print("正在分析消息吞吐量...")
            queue_name = input("请输入队列名称 (默认为 'test_queue'): ").strip() or 'test_queue'
            duration = int(input("请输入监控时长 (秒，默认60): ").strip() or '60')
            throughput = dashboard.performance_monitor.monitor_message_throughput(queue_name, duration)
            print(json.dumps(throughput, indent=2, ensure_ascii=False))
        elif choice == '5':
            print("正在运行综合监控...")
            report = dashboard.run_comprehensive_monitoring()
            print(f"整体状态: {report['summary']['overall_status']}")
            print(f"总告警数: {report['summary']['total_alerts']}")
            print(f"严重告警: {report['summary']['critical_alerts']}")
            print(f"警告告警: {report['summary']['warning_alerts']}")
        elif choice == '6':
            print("配置告警规则")
            name = input("告警名称: ")
            condition = input("监控指标 (如: cpu_percent): ")
            threshold = float(input("阈值: "))
            severity = input("严重程度 (warning/critical): ")
            dashboard.alert_manager.add_alert_rule(name, condition, threshold, severity)
            print("告警规则已添加")
        elif choice == '7':
            print("正在分析容量规划...")
            duration = int(input("分析时长 (小时，默认24): ").strip() or '24')
            capacity_data = dashboard.capacity_planner.collect_capacity_data(duration)
            print(json.dumps(capacity_data, indent=2, ensure_ascii=False))
        elif choice == '8':
            print("分析日志文件")
            log_file = input("日志文件路径: ")
            analyzer = LogAnalyzer(config)
            analysis = analyzer.analyze_log_file(log_file)
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        elif choice == '9':
            print("正在生成和保存监控报告...")
            report = dashboard.run_comprehensive_monitoring()
            filename = input("文件名 (回车使用默认名称): ").strip()
            dashboard.save_monitoring_report(report, filename)
            print("监控报告已保存")
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    print("启动RabbitMQ监控与运维系统...")
    try:
        interactive_monitoring_menu()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行错误: {e}")
        logger.error(f"程序运行错误: {e}", exc_info=True)