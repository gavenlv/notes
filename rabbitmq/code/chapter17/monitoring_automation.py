#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ监控与运维核心组件

本章实现RabbitMQ监控与运维的核心组件，包括：
1. 健康检查器 - 检查集群和节点健康状态
2. 性能监控器 - 收集和分析性能指标
3. 日志分析器 - 解析和分析系统日志
4. 告警管理器 - 管理和发送告警通知
5. 自动化运维工具 - 自动化故障恢复和日常运维任务
6. 基准测试器 - 进行性能基准测试

Author: RabbitMQ高级教程
Date: 2024
"""

import pika
import json
import time
import threading
import requests
import smtplib
import psutil
import logging
import subprocess
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, deque
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable
import queue
import warnings


class HealthChecker:
    """RabbitMQ健康检查器"""
    
    def __init__(self, management_api_url: str, username: str, password: str):
        self.api_url = management_api_url.rstrip('/')
        self.auth = (username, password)
        self.logger = logging.getLogger(__name__)
        
    def check_cluster_health(self) -> Dict[str, Any]:
        """检查集群整体健康状态"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'nodes': [],
            'queues': [],
            'connections': [],
            'alerts': []
        }
        
        try:
            # 检查集群概览
            overview = self._get_overview()
            if overview:
                health_status.update(overview)
            
            # 检查所有节点
            nodes_health = self._check_nodes_health()
            health_status['nodes'] = nodes_health
            
            # 检查队列状态
            queues_health = self._check_queues_health()
            health_status['queues'] = queues_health
            
            # 检查连接状态
            connections_health = self._check_connections_health()
            health_status['connections'] = connections_health
            
            # 计算整体健康状态
            health_status['overall_status'] = self._calculate_overall_status(health_status)
            
        except Exception as e:
            health_status['alerts'].append({
                'level': 'critical',
                'type': 'health_check_failed',
                'message': f'健康检查失败: {str(e)}'
            })
            health_status['overall_status'] = 'error'
        
        return health_status
    
    def _get_overview(self) -> Optional[Dict]:
        """获取集群概览信息"""
        try:
            response = requests.get(
                f"{self.api_url}/api/overview",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'cluster_name': data.get('cluster_name'),
                    'rabbitmq_version': data.get('rabbitmq_version'),
                    'management_version': data.get('management_version'),
                    'statistics_db_event_queue': data.get('statistics_db_event_queue'),
                    'queue_totals': data.get('queue_totals', {}),
                    'connection_totals': data.get('connection_totals', {}),
                    'channel_totals': data.get('channel_totals', {})
                }
            else:
                self.logger.warning(f"获取概览信息失败: HTTP {response.status_code}")
                return None
        
        except Exception as e:
            self.logger.error(f"获取概览信息异常: {e}")
            return None
    
    def _check_nodes_health(self) -> List[Dict]:
        """检查所有节点健康状态"""
        nodes_health = []
        
        try:
            response = requests.get(
                f"{self.api_url}/api/nodes",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                nodes_data = response.json()
                
                for node in nodes_data:
                    node_health = {
                        'name': node['name'],
                        'type': node.get('type', 'disc'),
                        'running': node.get('running', False),
                        'memory': node.get('memory', {}),
                        'fd_total': node.get('fd_total', 0),
                        'fd_used': node.get('fd_used', 0),
                        'sockets_total': node.get('sockets_total', 0),
                        'sockets_used': node.get('sockets_used', 0),
                        'status': 'healthy',
                        'alerts': []
                    }
                    
                    # 检查内存使用
                    if node_health['memory']:
                        memory_used = node_health['memory'].get('mem_used', 0)
                        memory_limit = node_health['memory'].get('mem_limit', 1)
                        memory_pct = (memory_used / memory_limit * 100) if memory_limit > 0 else 0
                        
                        if memory_pct > 85:
                            node_health['alerts'].append({
                                'level': 'warning',
                                'type': 'high_memory',
                                'message': f'内存使用率过高: {memory_pct:.1f}%'
                            })
                            if memory_pct > 95:
                                node_health['status'] = 'critical'
                                node_health['alerts'][-1]['level'] = 'critical'
                    
                    # 检查文件描述符
                    fd_pct = (node_health['fd_used'] / node_health['fd_total'] * 100) if node_health['fd_total'] > 0 else 0
                    if fd_pct > 80:
                        node_health['alerts'].append({
                            'level': 'warning',
                            'type': 'high_fd',
                            'message': f'文件描述符使用率过高: {fd_pct:.1f}%'
                        })
                    
                    # 检查套接字
                    socket_pct = (node_health['sockets_used'] / node_health['sockets_total'] * 100) if node_health['sockets_total'] > 0 else 0
                    if socket_pct > 80:
                        node_health['alerts'].append({
                            'level': 'warning',
                            'type': 'high_sockets',
                            'message': f'套接字使用率过高: {socket_pct:.1f}%'
                        })
                    
                    if not node_health['running']:
                        node_health['status'] = 'down'
                        node_health['alerts'].append({
                            'level': 'critical',
                            'type': 'node_down',
                            'message': '节点未运行'
                        })
                    
                    nodes_health.append(node_health)
        
        except Exception as e:
            self.logger.error(f"检查节点健康状态异常: {e}")
            nodes_health.append({
                'name': 'unknown',
                'status': 'error',
                'alerts': [{'level': 'critical', 'type': 'node_check_failed', 'message': f'节点检查失败: {e}'}]
            })
        
        return nodes_health
    
    def _check_queues_health(self) -> List[Dict]:
        """检查队列健康状态"""
        queues_health = []
        
        try:
            response = requests.get(
                f"{self.api_url}/api/queues",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                queues_data = response.json()
                
                for queue in queues_data:
                    queue_health = {
                        'name': queue['name'],
                        'vhost': queue['vhost'],
                        'durable': queue.get('durable', False),
                        'messages': queue.get('messages', 0),
                        'messages_ready': queue.get('messages_ready', 0),
                        'messages_unacknowledged': queue.get('messages_unacknowledged', 0),
                        'consumers': len(queue.get('consumer_details', [])),
                        'memory': queue.get('memory', 0),
                        'status': 'healthy',
                        'alerts': []
                    }
                    
                    # 检查消息积压
                    if queue_health['messages'] > 10000:
                        queue_health['alerts'].append({
                            'level': 'warning',
                            'type': 'message_backlog',
                            'message': f'消息积压严重: {queue_health["messages"]} 条'
                        })
                        if queue_health['messages'] > 50000:
                            queue_health['status'] = 'critical'
                            queue_health['alerts'][-1]['level'] = 'critical'
                    
                    # 检查无消费者
                    if queue_health['messages'] > 0 and queue_health['consumers'] == 0:
                        queue_health['alerts'].append({
                            'level': 'critical',
                            'type': 'no_consumer',
                            'message': '有消息但无消费者'
                        })
                        queue_health['status'] = 'critical'
                    
                    # 检查未确认消息
                    if queue_health['messages_unacknowledged'] > 1000:
                        queue_health['alerts'].append({
                            'level': 'warning',
                            'type': 'unacked_messages',
                            'message': f'未确认消息过多: {queue_health["messages_unacknowledged"]} 条'
                        })
                    
                    queues_health.append(queue_health)
        
        except Exception as e:
            self.logger.error(f"检查队列健康状态异常: {e}")
            queues_health.append({
                'name': 'unknown',
                'status': 'error',
                'alerts': [{'level': 'critical', 'type': 'queue_check_failed', 'message': f'队列检查失败: {e}'}]
            })
        
        return queues_health
    
    def _check_connections_health(self) -> List[Dict]:
        """检查连接健康状态"""
        connections_health = []
        
        try:
            response = requests.get(
                f"{self.api_url}/api/connections",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                connections_data = response.json()
                
                for conn in connections_data:
                    conn_health = {
                        'address': conn.get('address'),
                        'user': conn.get('user'),
                        'state': conn.get('state'),
                        'channels': conn.get('channels', 0),
                        'connected_at': conn.get('connected_at'),
                        'client_properties': conn.get('client_properties', {}),
                        'status': 'healthy',
                        'alerts': []
                    }
                    
                    # 检查连接状态
                    if conn_health['state'] not in ['running', 'blocking']:
                        conn_health['alerts'].append({
                            'level': 'warning',
                            'type': 'connection_state',
                            'message': f'连接状态异常: {conn_health["state"]}'
                        })
                    
                    # 检查连接时长
                    if conn_health['connected_at']:
                        connected_time = datetime.fromisoformat(conn_health['connected_at'].replace('Z', '+00:00'))
                        duration = datetime.now(connected_time.tzinfo) - connected_time
                        
                        if duration.total_seconds() < 60:  # 连接时间太短
                            conn_health['alerts'].append({
                                'level': 'warning',
                                'type': 'short_connection',
                                'message': f'连接时间过短: {duration.total_seconds():.0f}秒'
                            })
                    
                    connections_health.append(conn_health)
        
        except Exception as e:
            self.logger.error(f"检查连接健康状态异常: {e}")
            connections_health.append({
                'address': 'unknown',
                'status': 'error',
                'alerts': [{'level': 'critical', 'type': 'connection_check_failed', 'message': f'连接检查失败: {e}'}]
            })
        
        return connections_health
    
    def _calculate_overall_status(self, health_status: Dict) -> str:
        """计算整体健康状态"""
        all_alerts = []
        for node in health_status.get('nodes', []):
            all_alerts.extend(node.get('alerts', []))
        for queue in health_status.get('queues', []):
            all_alerts.extend(queue.get('alerts', []))
        for conn in health_status.get('connections', []):
            all_alerts.extend(conn.get('alerts', []))
        all_alerts.extend(health_status.get('alerts', []))
        
        critical_count = len([a for a in all_alerts if a.get('level') == 'critical'])
        warning_count = len([a for a in all_alerts if a.get('level') == 'warning'])
        
        if critical_count > 0:
            return 'critical'
        elif warning_count > 0:
            return 'warning'
        else:
            return 'healthy'


class PerformanceMonitor:
    """RabbitMQ性能监控器"""
    
    def __init__(self, management_api_url: str, username: str, password: str):
        self.api_url = management_api_url.rstrip('/')
        self.auth = (username, password)
        self.logger = logging.getLogger(__name__)
        self.metrics_history = defaultdict(deque)
        self.max_history_size = 1000
    
    def collect_metrics(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """收集性能指标"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        metrics = {
            'collection_time': end_time.isoformat(),
            'duration_minutes': duration_minutes,
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'queues': {},
            'system': {},
            'trends': {}
        }
        
        try:
            # 收集队列指标
            queues_metrics = self._collect_queues_metrics()
            metrics['queues'] = queues_metrics
            
            # 收集系统指标
            system_metrics = self._collect_system_metrics()
            metrics['system'] = system_metrics
            
            # 计算趋势
            trends = self._calculate_trends()
            metrics['trends'] = trends
            
            # 保存到历史记录
            self._save_to_history(metrics)
        
        except Exception as e:
            self.logger.error(f"收集性能指标异常: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    def _collect_queues_metrics(self) -> Dict:
        """收集队列级指标"""
        queues_metrics = {}
        
        try:
            response = requests.get(
                f"{self.api_url}/api/queues",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                queues_data = response.json()
                
                for queue in queues_data:
                    queue_name = f"{queue['vhost']}/{queue['name']}"
                    
                    # 收集基础指标
                    metrics = {
                        'messages': queue.get('messages', 0),
                        'messages_ready': queue.get('messages_ready', 0),
                        'messages_unacknowledged': queue.get('messages_unacknowledged', 0),
                        'consumers': len(queue.get('consumer_details', [])),
                        'memory': queue.get('memory', 0),
                        'durable': queue.get('durable', False)
                    }
                    
                    # 收集统计信息
                    message_stats = queue.get('message_stats', {})
                    if message_stats:
                        metrics.update({
                            'publish_details': message_stats.get('publish_details', {}),
                            'confirm_details': message_stats.get('confirm_details', {}),
                            'deliver_get_details': message_stats.get('deliver_get_details', {}),
                            'get_details': message_stats.get('get_details', {}),
                            'ack_details': message_stats.get('ack_details', {})
                        })
                    
                    # 计算衍生指标
                    metrics.update(self._calculate_queue_derived_metrics(metrics))
                    
                    queues_metrics[queue_name] = metrics
        
        except Exception as e:
            self.logger.error(f"收集队列指标异常: {e}")
            queues_metrics['error'] = str(e)
        
        return queues_metrics
    
    def _collect_system_metrics(self) -> Dict:
        """收集系统级指标"""
        system_metrics = {}
        
        try:
            # 获取集群概览
            overview = self._get_overview()
            if overview:
                system_metrics['cluster'] = overview
            
            # 获取节点信息
            nodes_metrics = self._get_nodes_metrics()
            system_metrics['nodes'] = nodes_metrics
            
            # 获取交换机信息
            exchanges_metrics = self._get_exchanges_metrics()
            system_metrics['exchanges'] = exchanges_metrics
        
        except Exception as e:
            self.logger.error(f"收集系统指标异常: {e}")
            system_metrics['error'] = str(e)
        
        return system_metrics
    
    def _calculate_queue_derived_metrics(self, queue_metrics: Dict) -> Dict:
        """计算队列衍生指标"""
        derived = {}
        
        # 计算消息确认率
        ack_details = queue_metrics.get('ack_details', {})
        if ack_details:
            ack_rate = ack_details.get('rate', 0)
            derived['ack_rate'] = ack_rate
        
        # 计算消息处理延迟（基于队列长度和出队速率）
        messages = queue_metrics.get('messages', 0)
        consumers = queue_metrics.get('consumers', 0)
        
        if consumers > 0:
            # 假设每个消费者每秒处理能力为100条消息
            estimated_throughput = consumers * 100
            if estimated_throughput > 0:
                derived['estimated_processing_delay'] = messages / estimated_throughput
            else:
                derived['estimated_processing_delay'] = float('inf')
        else:
            derived['estimated_processing_delay'] = float('inf')
        
        # 计算消息年龄分布（基于未确认消息）
        unacked = queue_metrics.get('messages_unacknowledged', 0)
        if unacked > 0:
            derived['unacked_ratio'] = unacked / max(messages, 1)
        else:
            derived['unacked_ratio'] = 0
        
        return derived
    
    def _calculate_trends(self) -> Dict:
        """计算性能趋势"""
        trends = {}
        
        try:
            # 分析消息量趋势
            message_trends = self._analyze_message_trends()
            trends['messages'] = message_trends
            
            # 分析消费者趋势
            consumer_trends = self._analyze_consumer_trends()
            trends['consumers'] = consumer_trends
        
        except Exception as e:
            self.logger.error(f"计算趋势异常: {e}")
            trends['error'] = str(e)
        
        return trends
    
    def _analyze_message_trends(self) -> Dict:
        """分析消息量趋势"""
        if len(self.metrics_history['total_messages']) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_messages = list(self.metrics_history['total_messages'])[-10:]
        
        if len(recent_messages) >= 3:
            # 计算简单的线性趋势
            x = list(range(len(recent_messages)))
            y = recent_messages
            
            # 计算斜率
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                if slope > 10:
                    trend = 'increasing_rapidly'
                elif slope > 2:
                    trend = 'increasing'
                elif slope < -10:
                    trend = 'decreasing_rapidly'
                elif slope < -2:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
                
                return {
                    'trend': trend,
                    'slope': slope,
                    'recent_values': recent_messages
                }
        
        return {'trend': 'stable', 'recent_values': recent_messages}
    
    def _analyze_consumer_trends(self) -> Dict:
        """分析消费者趋势"""
        if len(self.metrics_history['total_consumers']) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_consumers = list(self.metrics_history['total_consumers'])[-10:]
        
        if len(recent_consumers) >= 3:
            avg_consumers = statistics.mean(recent_consumers)
            current_consumers = recent_consumers[-1]
            
            if current_consumers > avg_consumers * 1.2:
                trend = 'increasing'
            elif current_consumers < avg_consumers * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'current': current_consumers,
                'average': avg_consumers,
                'recent_values': recent_consumers
            }
        
        return {'trend': 'stable', 'recent_values': recent_consumers}
    
    def _get_overview(self) -> Optional[Dict]:
        """获取集群概览"""
        try:
            response = requests.get(
                f"{self.api_url}/api/overview",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"获取概览失败: HTTP {response.status_code}")
                return None
        
        except Exception as e:
            self.logger.error(f"获取概览异常: {e}")
            return None
    
    def _get_nodes_metrics(self) -> List[Dict]:
        """获取节点指标"""
        nodes_metrics = []
        
        try:
            response = requests.get(
                f"{self.api_url}/api/nodes",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                nodes_data = response.json()
                
                for node in nodes_data:
                    node_metrics = {
                        'name': node['name'],
                        'type': node.get('type', 'disc'),
                        'running': node.get('running', False),
                        'memory': node.get('memory', {}),
                        'fd_used': node.get('fd_used', 0),
                        'fd_total': node.get('fd_total', 0),
                        'sockets_used': node.get('sockets_used', 0),
                        'sockets_total': node.get('sockets_total', 0),
                        'processes': node.get('processes', 0),
                        'run_queue': node.get('run_queue', 0)
                    }
                    nodes_metrics.append(node_metrics)
        
        except Exception as e:
            self.logger.error(f"获取节点指标异常: {e}")
        
        return nodes_metrics
    
    def _get_exchanges_metrics(self) -> List[Dict]:
        """获取交换机指标"""
        exchanges_metrics = []
        
        try:
            response = requests.get(
                f"{self.api_url}/api/exchanges",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                exchanges_data = response.json()
                
                for exchange in exchanges_data:
                    exchange_metrics = {
                        'name': exchange['name'],
                        'vhost': exchange['vhost'],
                        'type': exchange.get('type', 'topic'),
                        'durable': exchange.get('durable', False),
                        'internal': exchange.get('internal', False),
                        'auto_delete': exchange.get('auto_delete', False),
                        'message_stats': exchange.get('message_stats', {})
                    }
                    exchanges_metrics.append(exchange_metrics)
        
        except Exception as e:
            self.logger.error(f"获取交换机指标异常: {e}")
        
        return exchanges_metrics
    
    def _save_to_history(self, metrics: Dict):
        """保存指标到历史记录"""
        try:
            # 计算总数
            total_messages = 0
            total_consumers = 0
            
            for queue_metrics in metrics.get('queues', {}).values():
                if isinstance(queue_metrics, dict):
                    total_messages += queue_metrics.get('messages', 0)
                    total_consumers += queue_metrics.get('consumers', 0)
            
            self.metrics_history['total_messages'].append(total_messages)
            self.metrics_history['total_consumers'].append(total_consumers)
            self.metrics_history['collection_time'].append(datetime.now())
            
            # 限制历史记录大小
            for key in self.metrics_history:
                while len(self.metrics_history[key]) > self.max_history_size:
                    self.metrics_history[key].popleft()
        
        except Exception as e:
            self.logger.error(f"保存历史记录异常: {e}")


class AlertManager:
    """RabbitMQ告警管理器"""
    
    def __init__(self, alert_rules: Dict, notification_channels: Dict):
        self.alert_rules = alert_rules
        self.notification_channels = notification_channels
        self.logger = logging.getLogger(__name__)
        self.alert_history = deque(maxlen=1000)
        self.suppressed_alerts = set()
    
    def process_alerts(self, health_status: Dict, performance_metrics: Dict) -> List[Dict]:
        """处理告警信息"""
        alerts = []
        
        try:
            # 处理健康检查告警
            health_alerts = self._process_health_alerts(health_status)
            alerts.extend(health_alerts)
            
            # 处理性能告警
            performance_alerts = self._process_performance_alerts(performance_metrics)
            alerts.extend(performance_alerts)
            
            # 处理告警抑制
            filtered_alerts = self._filter_alerts(alerts)
            
            # 发送通知
            if filtered_alerts:
                self._send_notifications(filtered_alerts)
            
            # 更新告警历史
            self.alert_history.extend(filtered_alerts)
            
            return filtered_alerts
        
        except Exception as e:
            self.logger.error(f"处理告警异常: {e}")
            return []
    
    def _process_health_alerts(self, health_status: Dict) -> List[Dict]:
        """处理健康检查告警"""
        alerts = []
        
        try:
            # 检查整体健康状态
            overall_status = health_status.get('overall_status', 'unknown')
            if overall_status == 'critical':
                alerts.append({
                    'id': f'cluster_critical_{int(time.time())}',
                    'level': 'critical',
                    'type': 'cluster_critical',
                    'title': '集群整体状态严重',
                    'message': f'集群整体状态为: {overall_status}',
                    'timestamp': datetime.now().isoformat(),
                    'source': 'health_check'
                })
            
            # 检查节点告警
            for node in health_status.get('nodes', []):
                for alert in node.get('alerts', []):
                    alerts.append({
                        'id': f'node_{node["name"]}_{alert["type"]}_{int(time.time())}',
                        'level': alert['level'],
                        'type': f'node_{alert["type"]}',
                        'title': f'节点 {node["name"]} 异常',
                        'message': f'{node["name"]}: {alert["message"]}',
                        'timestamp': datetime.now().isoformat(),
                        'source': 'health_check',
                        'target': node['name']
                    })
            
            # 检查队列告警
            for queue in health_status.get('queues', []):
                for alert in queue.get('alerts', []):
                    alerts.append({
                        'id': f'queue_{queue["name"]}_{alert["type"]}_{int(time.time())}',
                        'level': alert['level'],
                        'type': f'queue_{alert["type"]}',
                        'title': f'队列 {queue["name"]} 异常',
                        'message': f'{queue["name"]}: {alert["message"]}',
                        'timestamp': datetime.now().isoformat(),
                        'source': 'health_check',
                        'target': queue['name']
                    })
        
        except Exception as e:
            self.logger.error(f"处理健康告警异常: {e}")
        
        return alerts
    
    def _process_performance_alerts(self, performance_metrics: Dict) -> List[Dict]:
        """处理性能告警"""
        alerts = []
        
        try:
            # 检查队列性能
            for queue_name, queue_metrics in performance_metrics.get('queues', {}).items():
                if isinstance(queue_metrics, dict):
                    # 检查处理延迟
                    processing_delay = queue_metrics.get('estimated_processing_delay', 0)
                    if processing_delay > 300:  # 5分钟
                        alerts.append({
                            'id': f'queue_delay_{queue_name}_{int(time.time())}',
                            'level': 'warning',
                            'type': 'processing_delay',
                            'title': f'队列处理延迟过高',
                            'message': f'{queue_name} 预计处理延迟: {processing_delay:.1f}秒',
                            'timestamp': datetime.now().isoformat(),
                            'source': 'performance_monitor',
                            'target': queue_name,
                            'value': processing_delay
                        })
                    
                    # 检查未确认消息比例
                    unacked_ratio = queue_metrics.get('unacked_ratio', 0)
                    if unacked_ratio > 0.5:  # 超过50%
                        alerts.append({
                            'id': f'queue_unacked_{queue_name}_{int(time.time())}',
                            'level': 'warning',
                            'type': 'unacked_ratio',
                            'title': f'队列未确认消息比例过高',
                            'message': f'{queue_name} 未确认消息比例: {unacked_ratio:.1%}',
                            'timestamp': datetime.now().isoformat(),
                            'source': 'performance_monitor',
                            'target': queue_name,
                            'value': unacked_ratio
                        })
            
            # 检查系统性能趋势
            trends = performance_metrics.get('trends', {})
            
            # 消息量快速增长的告警
            message_trend = trends.get('messages', {})
            if message_trend.get('trend') == 'increasing_rapidly':
                alerts.append({
                    'id': f'message_growth_{int(time.time())}',
                    'level': 'warning',
                    'type': 'message_growth_rapid',
                    'title': '消息量快速增长',
                    'message': f'消息量呈现快速增长趋势，斜率: {message_trend.get("slope", 0):.2f}',
                    'timestamp': datetime.now().isoformat(),
                    'source': 'performance_monitor'
                })
        
        except Exception as e:
            self.logger.error(f"处理性能告警异常: {e}")
        
        return alerts
    
    def _filter_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """过滤告警（应用抑制规则）"""
        filtered = []
        
        for alert in alerts:
            # 检查是否在抑制列表中
            alert_key = f"{alert['type']}_{alert.get('target', 'global')}"
            
            if alert_key in self.suppressed_alerts:
                continue
            
            # 检查告警规则
            rule = self.alert_rules.get(alert['type'], {})
            if not rule.get('enabled', True):
                continue
            
            # 检查告警级别
            if alert['level'] not in rule.get('levels', ['warning', 'critical']):
                continue
            
            filtered.append(alert)
            
            # 如果是持续性告警，添加到抑制列表
            if rule.get('dedup_enabled', True) and alert['level'] in ['warning', 'critical']:
                self.suppressed_alerts.add(alert_key)
                
                # 设置抑制时间
                dedup_duration = rule.get('dedup_duration', 300)  # 5分钟
                threading.Timer(dedup_duration, self._remove_suppression, args=[alert_key]).start()
        
        return filtered
    
    def _remove_suppression(self, alert_key: str):
        """移除告警抑制"""
        self.suppressed_alerts.discard(alert_key)
    
    def _send_notifications(self, alerts: List[Dict]):
        """发送通知"""
        try:
            # 邮件通知
            if self.notification_channels.get('email', {}).get('enabled'):
                self._send_email_notifications(alerts)
            
            # Webhook通知
            if self.notification_channels.get('webhook', {}).get('enabled'):
                self._send_webhook_notifications(alerts)
            
            # 日志通知
            self._log_notifications(alerts)
        
        except Exception as e:
            self.logger.error(f"发送通知异常: {e}")
    
    def _send_email_notifications(self, alerts: List[Dict]):
        """发送邮件通知"""
        try:
            email_config = self.notification_channels['email']
            
            # 构建邮件内容
            critical_alerts = [a for a in alerts if a['level'] == 'critical']
            warning_alerts = [a for a in alerts if a['level'] == 'warning']
            
            subject = f"RabbitMQ告警通知 - {len(critical_alerts)}个严重, {len(warning_alerts)}个警告"
            
            body = f"""
RabbitMQ告警通知

告警时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总告警数: {len(alerts)}
严重告警: {len(critical_alerts)}
警告告警: {len(warning_alerts)}

=== 严重告警 ===
"""
            
            for alert in critical_alerts:
                body += f"[{alert['level'].upper()}] {alert['title']}\n"
                body += f"消息: {alert['message']}\n"
                body += f"目标: {alert.get('target', 'N/A')}\n"
                body += f"时间: {alert['timestamp']}\n\n"
            
            body += "\n=== 警告告警 ===\n"
            for alert in warning_alerts:
                body += f"[{alert['level'].upper()}] {alert['title']}\n"
                body += f"消息: {alert['message']}\n"
                body += f"目标: {alert.get('target', 'N/A')}\n"
                body += f"时间: {alert['timestamp']}\n\n"
            
            # 发送邮件
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = email_config['from']
            msg['To'] = email_config['to']
            
            if email_config.get('use_tls', True):
                server = smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 587))
                server.starttls()
            else:
                server = smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 25))
            
            if email_config.get('username') and email_config.get('password'):
                server.login(email_config['username'], email_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"邮件通知已发送: {subject}")
        
        except Exception as e:
            self.logger.error(f"发送邮件通知异常: {e}")
    
    def _send_webhook_notifications(self, alerts: List[Dict]):
        """发送Webhook通知"""
        try:
            webhook_config = self.notification_channels['webhook']
            
            # 构建payload
            payload = {
                'timestamp': datetime.now().isoformat(),
                'alert_count': len(alerts),
                'alerts': alerts
            }
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {'Content-Type': 'application/json'}),
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Webhook通知发送成功")
            else:
                self.logger.warning(f"Webhook通知发送失败: HTTP {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"发送Webhook通知异常: {e}")
    
    def _log_notifications(self, alerts: List[Dict]):
        """记录告警日志"""
        for alert in alerts:
            if alert['level'] == 'critical':
                self.logger.critical(f"[{alert['type']}] {alert['message']}")
            elif alert['level'] == 'warning':
                self.logger.warning(f"[{alert['type']}] {alert['message']}")
            else:
                self.logger.info(f"[{alert['type']}] {alert['message']}")
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]


class LogAnalyzer:
    """RabbitMQ日志分析器"""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.logger = logging.getLogger(__name__)
        
        # 定义日志模式
        self.log_patterns = {
            'connection_errors': {
                'pattern': r'connection_closed.*(Connection|closed|refused)',
                'level': 'ERROR',
                'category': 'connection'
            },
            'memory_warnings': {
                'pattern': r'memory.*(high|warning|usage|alarm)',
                'level': 'WARNING',
                'category': 'performance'
            },
            'queue_errors': {
                'pattern': r'queue.*(error|failed|crash|exception)',
                'level': 'ERROR',
                'category': 'queue'
            },
            'authentication_failures': {
                'pattern': r'(authentication|login).*failed|denied|rejected',
                'level': 'WARNING',
                'category': 'security'
            },
            'performance_issues': {
                'pattern': r'(slow|timeout|blocked|deadlocked)',
                'level': 'WARNING',
                'category': 'performance'
            }
        }
    
    def analyze_logs(self, hours: int = 24) -> Dict[str, Any]:
        """分析日志文件"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            log_entries = self._parse_log_entries(cutoff_time)
            
            analysis_result = {
                'analysis_time': datetime.now().isoformat(),
                'time_range': {
                    'start': cutoff_time.isoformat(),
                    'end': datetime.now().isoformat()
                },
                'total_entries': len(log_entries),
                'pattern_matches': {},
                'error_summary': {},
                'time_distribution': {},
                'recommendations': []
            }
            
            # 分析模式匹配
            pattern_analysis = self._analyze_patterns(log_entries)
            analysis_result['pattern_matches'] = pattern_analysis
            
            # 生成错误摘要
            error_summary = self._generate_error_summary(log_entries)
            analysis_result['error_summary'] = error_summary
            
            # 时间分布分析
            time_distribution = self._analyze_time_distribution(log_entries)
            analysis_result['time_distribution'] = time_distribution
            
            # 生成建议
            recommendations = self._generate_recommendations(analysis_result)
            analysis_result['recommendations'] = recommendations
            
            return analysis_result
        
        except Exception as e:
            self.logger.error(f"分析日志异常: {e}")
            return {'error': str(e)}
    
    def _parse_log_entries(self, cutoff_time: datetime) -> List[Dict]:
        """解析日志条目"""
        log_entries = []
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = self._parse_single_line(line, line_num)
                        if entry and entry['timestamp'] > cutoff_time:
                            log_entries.append(entry)
                    except Exception as e:
                        # 忽略无法解析的行
                        continue
        
        except FileNotFoundError:
            self.logger.warning(f"日志文件未找到: {self.log_file_path}")
        except Exception as e:
            self.logger.error(f"读取日志文件异常: {e}")
        
        return log_entries
    
    def _parse_single_line(self, line: str, line_num: int) -> Optional[Dict]:
        """解析单行日志"""
        import re
        
        # 提取时间戳 (支持多种格式)
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})',
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\]'
        ]
        
        timestamp = None
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    timestamp = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
                    break
                except ValueError:
                    continue
        
        if not timestamp:
            return None
        
        # 提取日志级别
        level_patterns = [
            r'\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+',
            r'\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]'
        ]
        
        level = 'INFO'
        for pattern in level_patterns:
            match = re.search(pattern, line)
            if match:
                level = match.group(1)
                break
        
        return {
            'line_number': line_num,
            'timestamp': timestamp,
            'level': level,
            'raw_line': line.strip(),
            'parsed_time': timestamp
        }
    
    def _analyze_patterns(self, log_entries: List[Dict]) -> Dict:
        """分析日志模式匹配"""
        pattern_matches = {}
        
        import re
        
        for pattern_name, pattern_config in self.log_patterns.items():
            pattern = re.compile(pattern_config['pattern'], re.IGNORECASE)
            matches = []
            
            for entry in log_entries:
                if re.search(pattern, entry['raw_line']):
                    matches.append({
                        'timestamp': entry['timestamp'].isoformat(),
                        'level': entry['level'],
                        'line': entry['raw_line']
                    })
            
            pattern_matches[pattern_name] = {
                'count': len(matches),
                'pattern': pattern_config['pattern'],
                'level': pattern_config['level'],
                'category': pattern_config['category'],
                'samples': matches[:5]  # 只保留前5个样本
            }
        
        return pattern_matches
    
    def _generate_error_summary(self, log_entries: List[Dict]) -> Dict:
        """生成错误摘要"""
        error_entries = [e for e in log_entries if e['level'] in ['ERROR', 'CRITICAL']]
        
        if not error_entries:
            return {'total_errors': 0}
        
        # 按级别统计
        error_by_level = defaultdict(int)
        for entry in error_entries:
            error_by_level[entry['level']] += 1
        
        # 按小时统计
        error_by_hour = defaultdict(int)
        for entry in error_entries:
            hour_key = entry['timestamp'].strftime('%Y-%m-%d %H:00')
            error_by_hour[hour_key] += 1
        
        # 提取常见错误模式
        error_patterns = defaultdict(int)
        for entry in error_entries:
            # 提取前50个字符作为模式
            pattern = entry['raw_line'][:50].strip()
            error_patterns[pattern] += 1
        
        # 排序取前10
        top_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_errors': len(error_entries),
            'by_level': dict(error_by_level),
            'by_hour': dict(error_by_hour),
            'top_patterns': top_patterns,
            'first_error': error_entries[0]['timestamp'].isoformat() if error_entries else None,
            'last_error': error_entries[-1]['timestamp'].isoformat() if error_entries else None
        }
    
    def _analyze_time_distribution(self, log_entries: List[Dict]) -> Dict:
        """分析时间分布"""
        if not log_entries:
            return {}
        
        # 按小时统计
        hourly_distribution = defaultdict(int)
        for entry in log_entries:
            hour_key = entry['timestamp'].strftime('%Y-%m-%d %H:00')
            hourly_distribution[hour_key] += 1
        
        # 按星期几统计
        weekday_distribution = defaultdict(int)
        for entry in log_entries:
            weekday_key = entry['timestamp'].strftime('%A')
            weekday_distribution[weekday_key] += 1
        
        # 按小时统计（一天中的小时）
        hour_of_day_distribution = defaultdict(int)
        for entry in log_entries:
            hour_key = entry['timestamp'].hour
            hour_of_day_distribution[hour_key] += 1
        
        return {
            'by_hour': dict(hourly_distribution),
            'by_weekday': dict(weekday_distribution),
            'by_hour_of_day': dict(hour_of_day_distribution),
            'peak_hour': max(hour_of_day_distribution.items(), key=lambda x: x[1])[0] if hour_of_day_distribution else None,
            'busiest_day': max(weekday_distribution.items(), key=lambda x: x[1])[0] if weekday_distribution else None
        }
    
    def _generate_recommendations(self, analysis_result: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        try:
            # 基于错误数量的建议
            error_summary = analysis_result.get('error_summary', {})
            total_errors = error_summary.get('total_errors', 0)
            
            if total_errors > 100:
                recommendations.append("错误数量过多，建议进行深度问题排查")
            elif total_errors > 20:
                recommendations.append("错误数量偏多，建议加强监控")
            
            # 基于模式分析的建议
            pattern_matches = analysis_result.get('pattern_matches', {})
            
            for pattern_name, pattern_data in pattern_matches.items():
                count = pattern_data.get('count', 0)
                category = pattern_data.get('category', '')
                
                if category == 'memory' and count > 10:
                    recommendations.append("内存相关告警频繁，建议检查内存配置和队列配置")
                elif category == 'connection' and count > 50:
                    recommendations.append("连接错误频繁，建议检查网络稳定性和连接池配置")
                elif category == 'security' and count > 5:
                    recommendations.append("认证失败频繁，建议检查用户权限配置")
                elif category == 'performance' and count > 20:
                    recommendations.append("性能问题频繁，建议进行性能优化")
            
            # 基于时间分布的建议
            time_dist = analysis_result.get('time_distribution', {})
            peak_hour = time_dist.get('peak_hour')
            
            if peak_hour is not None:
                hour = int(peak_hour)
                if 9 <= hour <= 18:
                    recommendations.append(f"在工作时间({hour}:00)错误较多，可能与业务高峰相关")
                elif 0 <= hour <= 6:
                    recommendations.append(f"在深夜({hour}:00)错误较多，建议检查定时任务")
            
            # 默认建议
            if not recommendations:
                recommendations.append("系统运行正常，继续保持当前配置")
        
        except Exception as e:
            self.logger.error(f"生成建议异常: {e}")
            recommendations.append("建议生成失败，请手动检查系统状态")
        
        return recommendations


class AutomationTool:
    """RabbitMQ自动化运维工具"""
    
    def __init__(self, management_api_url: str, username: str, password: str):
        self.api_url = management_api_url.rstrip('/')
        self.auth = (username, password)
        self.logger = logging.getLogger(__name__)
    
    def restart_rabbitmq_service(self) -> Dict[str, Any]:
        """重启RabbitMQ服务"""
        try:
            self.logger.info("开始重启RabbitMQ服务...")
            
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', 'rabbitmq-server'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # 等待服务启动
                time.sleep(30)
                
                # 检查服务状态
                status_result = subprocess.run(
                    ['sudo', 'systemctl', 'is-active', 'rabbitmq-server'],
                    capture_output=True,
                    text=True
                )
                
                if status_result.stdout.strip() == 'active':
                    return {
                        'success': True,
                        'message': 'RabbitMQ服务重启成功',
                        'output': result.stdout,
                        'restart_time': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'message': 'RabbitMQ服务重启后状态异常',
                        'output': result.stderr,
                        'error': status_result.stderr
                    }
            else:
                return {
                    'success': False,
                    'message': 'RabbitMQ服务重启失败',
                    'error': result.stderr,
                    'output': result.stdout
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'RabbitMQ服务重启超时'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'重启服务异常: {str(e)}'
            }
    
    def clear_queue_messages(self, vhost: str = '/', queue_name: str = None) -> Dict[str, Any]:
        """清空队列消息"""
        try:
            # 如果没有指定队列名称，获取所有队列
            if queue_name is None:
                queues = self._get_all_queues(vhost)
                queue_names = [q['name'] for q in queues]
            else:
                queue_names = [queue_name]
            
            results = {}
            
            for q_name in queue_names:
                try:
                    # 删除队列
                    response = requests.delete(
                        f"{self.api_url}/api/queues/{vhost}/{q_name}",
                        auth=self.auth,
                        timeout=30
                    )
                    
                    if response.status_code == 204:
                        # 重新创建队列
                        queue_config = self._get_queue_config(vhost, q_name)
                        if queue_config:
                            create_response = requests.put(
                                f"{self.api_url}/api/queues/{vhost}/{q_name}",
                                auth=self.auth,
                                json=queue_config,
                                timeout=30
                            )
                            
                            if create_response.status_code == 201:
                                results[q_name] = {
                                    'success': True,
                                    'message': '队列消息清空成功'
                                }
                            else:
                                results[q_name] = {
                                    'success': False,
                                    'message': '队列重建失败',
                                    'error': create_response.text
                                }
                        else:
                            results[q_name] = {
                                'success': False,
                                'message': '无法获取队列配置信息'
                            }
                    else:
                        results[q_name] = {
                            'success': False,
                            'message': f'删除队列失败: HTTP {response.status_code}'
                        }
                
                except Exception as e:
                    results[q_name] = {
                        'success': False,
                        'message': f'处理队列异常: {str(e)}'
                    }
            
            return {
                'success': True,
                'processed_queues': len(queue_names),
                'results': results,
                'operation_time': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'清空队列异常: {str(e)}'
            }
    
    def optimize_queue_settings(self, vhost: str = '/') -> Dict[str, Any]:
        """优化队列设置"""
        try:
            queues = self._get_all_queues(vhost)
            optimization_results = {}
            
            for queue in queues:
                queue_name = queue['name']
                
                # 检查当前设置
                current_settings = {
                    'durable': queue.get('durable', False),
                    'auto_delete': queue.get('auto_delete', True),
                    'arguments': queue.get('arguments', {})
                }
                
                # 建议的优化设置
                recommended_settings = {
                    'durable': True,  # 生产环境建议持久化
                    'auto_delete': False,  # 避免意外删除
                    'arguments': {
                        'x-max-length': 10000,  # 限制队列最大长度
                        'x-overflow': 'reject-publish',  # 超出限制时拒绝新消息
                        'x-message-ttl': 3600000,  # 消息1小时过期
                        'x-dead-letter-exchange': 'dlx',  # 死信交换机
                        'x-dead-letter-routing-key': f'deadletter.{queue_name}'
                    }
                }
                
                # 应用优化设置（仅在需要时）
                needs_optimization = False
                for key, value in recommended_settings.items():
                    if key == 'arguments':
                        continue
                    if current_settings.get(key) != value:
                        needs_optimization = True
                        break
                
                if needs_optimization:
                    try:
                        # 应用新设置
                        response = requests.put(
                            f"{self.api_url}/api/queues/{vhost}/{queue_name}",
                            auth=self.auth,
                            json=recommended_settings,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            optimization_results[queue_name] = {
                                'success': True,
                                'message': '队列设置优化成功',
                                'old_settings': current_settings,
                                'new_settings': recommended_settings
                            }
                        else:
                            optimization_results[queue_name] = {
                                'success': False,
                                'message': f'优化失败: HTTP {response.status_code}',
                                'error': response.text
                            }
                    
                    except Exception as e:
                        optimization_results[queue_name] = {
                            'success': False,
                            'message': f'优化异常: {str(e)}'
                        }
                else:
                    optimization_results[queue_name] = {
                        'success': True,
                        'message': '队列设置已是最优',
                        'settings': current_settings
                    }
            
            return {
                'success': True,
                'processed_queues': len(queues),
                'optimization_results': optimization_results,
                'optimization_time': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'优化队列设置异常: {str(e)}'
            }
    
    def emergency_recovery(self) -> Dict[str, Any]:
        """紧急恢复流程"""
        self.logger.info("开始紧急恢复流程...")
        
        recovery_steps = []
        
        try:
            # 步骤1: 检查服务状态
            service_status = subprocess.run(
                ['sudo', 'systemctl', 'is-active', 'rabbitmq-server'],
                capture_output=True,
                text=True
            )
            
            recovery_steps.append({
                'step': 1,
                'action': '检查服务状态',
                'result': service_status.stdout.strip(),
                'status': 'success' if service_status.returncode == 0 else 'failed'
            })
            
            if service_status.stdout.strip() != 'active':
                # 步骤2: 重启服务
                restart_result = self.restart_rabbitmq_service()
                recovery_steps.append({
                    'step': 2,
                    'action': '重启RabbitMQ服务',
                    'result': restart_result,
                    'status': 'success' if restart_result['success'] else 'failed'
                })
                
                if not restart_result['success']:
                    # 步骤3: 强制重置（危险操作）
                    self.logger.warning("重启失败，尝试强制重置")
                    force_reset = self._force_reset_cluster()
                    recovery_steps.append({
                        'step': 3,
                        'action': '强制重置集群',
                        'result': force_reset,
                        'status': 'success' if force_reset['success'] else 'failed'
                    })
            
            # 步骤4: 清理积压消息
            clear_result = self.clear_queue_messages()
            recovery_steps.append({
                'step': 4,
                'action': '清理积压消息',
                'result': clear_result,
                'status': 'success' if clear_result['success'] else 'warning'
            })
            
            # 步骤5: 验证恢复
            health_check = HealthChecker(
                self.api_url.rreplace('/api', '', 1),
                self.auth[0],
                self.auth[1]
            )
            
            health_status = health_check.check_cluster_health()
            recovery_steps.append({
                'step': 5,
                'action': '验证恢复状态',
                'result': health_status,
                'status': 'success' if health_status['overall_status'] == 'healthy' else 'failed'
            })
            
            overall_success = all(step['status'] in ['success', 'warning'] for step in recovery_steps)
            
            return {
                'success': overall_success,
                'recovery_steps': recovery_steps,
                'final_status': health_status.get('overall_status', 'unknown'),
                'recovery_time': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'紧急恢复异常: {str(e)}',
                'recovery_steps': recovery_steps
            }
    
    def _get_all_queues(self, vhost: str) -> List[Dict]:
        """获取所有队列"""
        try:
            response = requests.get(
                f"{self.api_url}/api/queues/{vhost}",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
        
        except Exception as e:
            self.logger.error(f"获取队列列表异常: {e}")
            return []
    
    def _get_queue_config(self, vhost: str, queue_name: str) -> Optional[Dict]:
        """获取队列配置"""
        try:
            response = requests.get(
                f"{self.api_url}/api/queues/{vhost}/{queue_name}",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            self.logger.error(f"获取队列配置异常: {e}")
            return None
    
    def _force_reset_cluster(self) -> Dict[str, Any]:
        """强制重置集群（危险操作）"""
        try:
            # 停止应用
            stop_result = subprocess.run(
                ['rabbitmqctl', 'stop_app'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if stop_result.returncode != 0:
                return {
                    'success': False,
                    'message': '停止应用失败',
                    'error': stop_result.stderr
                }
            
            # 重置应用
            reset_result = subprocess.run(
                ['rabbitmqctl', 'reset'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if reset_result.returncode != 0:
                return {
                    'success': False,
                    'message': '重置应用失败',
                    'error': reset_result.stderr
                }
            
            # 启动应用
            start_result = subprocess.run(
                ['rabbitmqctl', 'start_app'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if start_result.returncode != 0:
                return {
                    'success': False,
                    'message': '启动应用失败',
                    'error': start_result.stderr
                }
            
            return {
                'success': True,
                'message': '集群重置成功'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'强制重置异常: {str(e)}'
            }


class BenchmarkTester:
    """RabbitMQ性能基准测试器"""
    
    def __init__(self, connection_params: Dict):
        self.connection_params = connection_params
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """运行综合性能基准测试"""
        try:
            self.logger.info("开始综合性能基准测试")
            
            test_scenarios = [
                {
                    'name': 'basic_throughput',
                    'description': '基础吞吐量测试',
                    'message_count': 1000,
                    'message_size': 1024,
                    'threads': 1,
                    'duration': 60
                },
                {
                    'name': 'high_throughput',
                    'description': '高吞吐量测试',
                    'message_count': 10000,
                    'message_size': 1024,
                    'threads': 5,
                    'duration': 120
                },
                {
                    'name': 'large_message',
                    'description': '大消息测试',
                    'message_count': 100,
                    'message_size': 10240,  # 10KB
                    'threads': 1,
                    'duration': 60
                },
                {
                    'name': 'concurrent_consumer',
                    'description': '并发消费者测试',
                    'message_count': 5000,
                    'message_size': 1024,
                    'threads': 10,
                    'duration': 180
                }
            ]
            
            benchmark_results = {
                'test_start_time': datetime.now().isoformat(),
                'scenarios': {},
                'summary': {}
            }
            
            for scenario in test_scenarios:
                self.logger.info(f"运行测试场景: {scenario['name']}")
                
                try:
                    scenario_result = self._run_single_scenario(scenario)
                    benchmark_results['scenarios'][scenario['name']] = scenario_result
                    
                    # 清理队列
                    self._cleanup_test_queues(scenario['name'])
                
                except Exception as e:
                    self.logger.error(f"测试场景 {scenario['name']} 失败: {e}")
                    benchmark_results['scenarios'][scenario['name']] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # 生成摘要
            summary = self._generate_benchmark_summary(benchmark_results['scenarios'])
            benchmark_results['summary'] = summary
            benchmark_results['test_end_time'] = datetime.now().isoformat()
            
            self.test_results = benchmark_results
            return benchmark_results
        
        except Exception as e:
            self.logger.error(f"综合基准测试异常: {e}")
            return {'error': str(e)}
    
    def _run_single_scenario(self, scenario: Dict) -> Dict[str, Any]:
        """运行单个测试场景"""
        scenario_result = {
            'scenario': scenario,
            'success': False,
            'results': {}
        }
        
        try:
            # 创建测试队列
            queue_name = f"benchmark_{scenario['name']}"
            self._create_test_queue(queue_name)
            
            # 并发执行生产者和消费者测试
            with ThreadPoolExecutor(max_workers=scenario['threads'] * 2) as executor:
                # 启动生产者
                producer_future = executor.submit(
                    self._benchmark_producer,
                    queue_name,
                    scenario['message_count'],
                    scenario['message_size'],
                    scenario['threads']
                )
                
                # 启动消费者
                consumer_future = executor.submit(
                    self._benchmark_consumer,
                    queue_name,
                    scenario['message_count'],
                    scenario['threads']
                )
                
                # 等待完成
                producer_result = producer_future.result(timeout=scenario['duration'] * 2)
                consumer_result = consumer_future.result(timeout=scenario['duration'] * 2)
                
                scenario_result['results'] = {
                    'producer': producer_result,
                    'consumer': consumer_result
                }
                
                # 计算端到端性能
                if producer_result['success'] and consumer_result['success']:
                    end_to_end_latency = producer_result.get('avg_latency', 0) + consumer_result.get('avg_processing_time', 0)
                    throughput = min(
                        producer_result.get('throughput_msg_per_sec', 0),
                        consumer_result.get('throughput_msg_per_sec', 0)
                    )
                    
                    scenario_result['end_to_end'] = {
                        'latency_ms': end_to_end_latency,
                        'throughput_msg_per_sec': throughput
                    }
                
                scenario_result['success'] = True
            
        except Exception as e:
            scenario_result['error'] = str(e)
            self.logger.error(f"测试场景执行异常: {e}")
        
        finally:
            # 清理测试队列
            self._cleanup_test_queues(queue_name)
        
        return scenario_result
    
    def _create_test_queue(self, queue_name: str):
        """创建测试队列"""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(**self.connection_params))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            connection.close()
        except Exception as e:
            self.logger.error(f"创建测试队列异常: {e}")
            raise
    
    def _benchmark_producer(self, queue_name: str, message_count: int, 
                          message_size: int, threads: int) -> Dict[str, Any]:
        """基准测试生产者"""
        message = b'x' * message_size
        send_times = []
        successful_sends = 0
        
        def producer_worker(worker_id: int, messages_per_thread: int):
            nonlocal successful_sends
            
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(**self.connection_params))
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=True)
                
                for i in range(messages_per_thread):
                    start_time = time.time()
                    
                    try:
                        channel.basic_publish(
                            exchange='',
                            routing_key=queue_name,
                            body=message,
                            properties=pika.BasicProperties(delivery_mode=2)
                        )
                        
                        end_time = time.time()
                        latency = (end_time - start_time) * 1000
                        send_times.append(latency)
                        successful_sends += 1
                    
                    except Exception as e:
                        self.logger.error(f"Worker {worker_id} 发送消息失败: {e}")
                
                connection.close()
            except Exception as e:
                self.logger.error(f"Producer worker {worker_id} 异常: {e}")
        
        # 计算每个线程的消息数
        messages_per_thread = message_count // threads
        remaining_messages = message_count % threads
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            
            for i in range(threads):
                msg_count = messages_per_thread + (1 if i < remaining_messages else 0)
                future = executor.submit(producer_worker, i, msg_count)
                futures.append(future)
            
            for future in as_completed(futures):
                future.result()  # 等待完成
        
        total_time = time.time() - start_time
        
        return {
            'success': True,
            'messages_sent': successful_sends,
            'total_time': total_time,
            'throughput_msg_per_sec': successful_sends / total_time,
            'throughput_bytes_per_sec': (successful_sends * message_size) / total_time,
            'avg_latency': statistics.mean(send_times) if send_times else 0,
            'min_latency': min(send_times) if send_times else 0,
            'max_latency': max(send_times) if send_times else 0,
            'latency_95th': sorted(send_times)[int(len(send_times) * 0.95)] if send_times else 0,
            'latency_99th': sorted(send_times)[int(len(send_times) * 0.99)] if send_times else 0
        }
    
    def _benchmark_consumer(self, queue_name: str, message_count: int, 
                          threads: int) -> Dict[str, Any]:
        """基准测试消费者"""
        processed_messages = 0
        processing_times = []
        
        def consumer_worker(worker_id: int):
            nonlocal processed_messages
            
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(**self.connection_params))
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=True)
                channel.basic_qos(prefetch_count=100 // threads)
                
                messages_processed = 0
                
                def callback(ch, method, properties, body):
                    nonlocal processed_messages
                    
                    try:
                        process_start_time = time.time()
                        
                        # 模拟消息处理
                        time.sleep(0.001)  # 1ms处理时间
                        
                        process_end_time = time.time()
                        processing_time = (process_end_time - process_start_time) * 1000
                        
                        processing_times.append(processing_time)
                        processed_messages += 1
                        messages_processed += 1
                        
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                    except Exception as e:
                        self.logger.error(f"Consumer worker {worker_id} 处理消息失败: {e}")
                
                channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
                
                # 消费消息直到达到目标数量
                while processed_messages < message_count:
                    try:
                        connection.process_data_events(time_limit=1)
                    except Exception as e:
                        self.logger.error(f"Consumer worker {worker_id} 处理事件失败: {e}")
                        break
                
                connection.close()
                return messages_processed
            
            except Exception as e:
                self.logger.error(f"Consumer worker {worker_id} 异常: {e}")
                return 0
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(consumer_worker, i) for i in range(threads)]
            
            for future in as_completed(futures):
                future.result(timeout=300)  # 5分钟超时
        
        total_time = time.time() - start_time
        
        return {
            'success': True,
            'messages_processed': processed_messages,
            'total_time': total_time,
            'throughput_msg_per_sec': processed_messages / total_time,
            'avg_processing_time': statistics.mean(processing_times) if processing_times else 0,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0,
            'processing_time_95th': sorted(processing_times)[int(len(processing_times) * 0.95)] if processing_times else 0
        }
    
    def _cleanup_test_queues(self, queue_name: str):
        """清理测试队列"""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(**self.connection_params))
            channel = connection.channel()
            
            try:
                channel.queue_delete(queue=queue_name)
            except:
                pass  # 队列可能已经不存在
            
            connection.close()
        except Exception as e:
            self.logger.error(f"清理测试队列异常: {e}")
    
    def _generate_benchmark_summary(self, scenario_results: Dict) -> Dict:
        """生成基准测试摘要"""
        summary = {
            'total_scenarios': len(scenario_results),
            'successful_scenarios': 0,
            'failed_scenarios': 0,
            'performance_metrics': {},
            'recommendations': []
        }
        
        # 统计成功率
        for result in scenario_results.values():
            if result.get('success', False):
                summary['successful_scenarios'] += 1
            else:
                summary['failed_scenarios'] += 1
        
        # 提取性能指标
        throughput_values = []
        latency_values = []
        
        for name, result in scenario_results.items():
            if result.get('success') and 'end_to_end' in result:
                throughput_values.append(result['end_to_end']['throughput_msg_per_sec'])
                latency_values.append(result['end_to_end']['latency_ms'])
        
        if throughput_values:
            summary['performance_metrics'] = {
                'avg_throughput_msg_per_sec': statistics.mean(throughput_values),
                'max_throughput_msg_per_sec': max(throughput_values),
                'avg_latency_ms': statistics.mean(latency_values),
                'max_latency_ms': max(latency_values)
            }
            
            # 生成建议
            if summary['performance_metrics']['avg_throughput_msg_per_sec'] < 1000:
                summary['recommendations'].append("吞吐量较低，建议优化网络配置和客户端设置")
            
            if summary['performance_metrics']['avg_latency_ms'] > 100:
                summary['recommendations'].append("延迟较高，建议检查网络延迟和消息处理逻辑")
        else:
            summary['recommendations'].append("测试结果异常，建议检查测试环境和配置")
        
        return summary
    
    def save_benchmark_results(self, filename: str) -> str:
        """保存基准测试结果"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
            
            return f"基准测试结果已保存到: {filename}"
        except Exception as e:
            return f"保存基准测试结果失败: {str(e)}"


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
       