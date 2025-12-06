#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ集群管理器
实现集群部署、监控、健康检查、故障恢复等核心功能

功能特性：
- 集群节点管理（添加、移除、重启）
- 集群状态监控与健康检查
- 镜像队列同步管理
- 负载均衡配置
- 故障检测与自动恢复
- 性能监控与分析
- 集群配置管理
- 备份与灾难恢复
"""

import pika
import json
import time
import threading
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
import psutil
import statistics


class ClusterStatus(Enum):
    """集群状态枚举"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class NodeStatus(Enum):
    """节点状态枚举"""
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"
    DOWN = "down"


class MirrorPolicy(Enum):
    """镜像策略枚举"""
    ALL = "all"
    EXACTLY = "exactly"
    NODES = "nodes"


@dataclass
class NodeInfo:
    """节点信息数据类"""
    name: str
    host: str
    port: int
    status: NodeStatus
    memory_usage: float = 0.0
    disk_free: float = 0.0
    connections: int = 0
    queues: int = 0
    uptime: str = ""
    applications: List[str] = None
    
    def __post_init__(self):
        if self.applications is None:
            self.applications = []


@dataclass
class QueueInfo:
    """队列信息数据类"""
    name: str
    vhost: str
    durable: bool
    messages: int
    consumers: int
    policy: str = ""
    master_pid: str = ""
    slave_pids: List[str] = None
    sync_state: str = ""
    
    def __post_init__(self):
        if self.slave_pids is None:
            self.slave_pids = []


@dataclass
class ClusterMetrics:
    """集群指标数据类"""
    total_messages: int = 0
    total_queues: int = 0
    total_connections: int = 0
    avg_latency: float = 0.0
    msg_rate_in: float = 0.0
    msg_rate_out: float = 0.0
    memory_usage_pct: float = 0.0
    disk_usage_pct: float = 0.0


class ClusterHealthChecker:
    """集群健康检查器"""
    
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager
        self.logger = logging.getLogger(__name__)
        
    def check_node_health(self, node_info: NodeInfo) -> Dict:
        """检查单个节点健康状态"""
        health_status = {
            'node': node_info.name,
            'healthy': True,
            'checks': {},
            'issues': []
        }
        
        try:
            # 1. 连接检查
            connection_health = self._check_connection(node_info)
            health_status['checks']['connection'] = connection_health
            
            if not connection_health['success']:
                health_status['healthy'] = False
                health_status['issues'].append(f"连接失败: {connection_health['error']}")
            
            # 2. API检查
            api_health = self._check_api_health(node_info)
            health_status['checks']['api'] = api_health
            
            if not api_health['success']:
                health_status['healthy'] = False
                health_status['issues'].append(f"API检查失败: {api_health['error']}")
            
            # 3. 资源检查
            resource_health = self._check_resources(node_info)
            health_status['checks']['resources'] = resource_health
            
            if not resource_health['success']:
                health_status['issues'].append(f"资源检查失败: {resource_health['warning']}")
            
            # 4. 应用状态检查
            app_health = self._check_applications(node_info)
            health_status['checks']['applications'] = app_health
            
            if not app_health['success']:
                health_status['healthy'] = False
                health_status['issues'].append(f"应用状态异常: {app_health['error']}")
                
        except Exception as e:
            health_status['healthy'] = False
            health_status['checks']['exception'] = {'success': False, 'error': str(e)}
            health_status['issues'].append(f"检查异常: {e}")
        
        return health_status
    
    def _check_connection(self, node_info: NodeInfo) -> Dict:
        """检查节点连接"""
        try:
            credentials = pika.PlainCredentials(
                self.cluster_manager.username, 
                self.cluster_manager.password
            )
            parameters = pika.ConnectionParameters(
                host=node_info.host,
                port=node_info.port,
                credentials=credentials,
                connection_attempts=2,
                retry_delay=1,
                heartbeat=10
            )
            
            start_time = time.time()
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            end_time = time.time()
            
            # 简单的ping操作
            channel.queue_declare(queue='health_check', passive=True)
            
            connection.close()
            
            return {
                'success': True,
                'latency': (end_time - start_time) * 1000,  # ms
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _check_api_health(self, node_info: NodeInfo) -> Dict:
        """检查API健康状态"""
        try:
            url = f"http://{node_info.host}:15672/api/overview"
            response = requests.get(
                url,
                auth=(self.cluster_manager.username, self.cluster_manager.password),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response_time': response.elapsed.total_seconds(),
                    'rabbitmq_version': data.get('rabbitmq_version'),
                    'management_version': data.get('management_version')
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'response_time': response.elapsed.total_seconds()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_resources(self, node_info: NodeInfo) -> Dict:
        """检查系统资源"""
        issues = []
        warnings = []
        
        # 内存检查
        if node_info.memory_usage > 90:
            issues.append(f"内存使用率过高: {node_info.memory_usage}%")
        elif node_info.memory_usage > 80:
            warnings.append(f"内存使用率较高: {node_info.memory_usage}%")
        
        # 磁盘检查
        if node_info.disk_free < 1024 * 1024 * 1024:  # 1GB
            issues.append(f"磁盘空间不足: {node_info.disk_free / 1024 / 1024:.0f}MB")
        elif node_info.disk_free < 5 * 1024 * 1024 * 1024:  # 5GB
            warnings.append(f"磁盘空间较少: {node_info.disk_free / 1024 / 1024 / 1024:.1f}GB")
        
        # 连接数检查
        if node_info.connections > 10000:
            warnings.append(f"连接数较多: {node_info.connections}")
        
        return {
            'success': len(issues) == 0,
            'warnings': warnings,
            'issues': issues
        }
    
    def _check_applications(self, node_info: NodeInfo) -> Dict:
        """检查应用状态"""
        required_apps = ['rabbit', 'mnesia']
        missing_apps = []
        
        for app in required_apps:
            if app not in node_info.applications:
                missing_apps.append(app)
        
        if missing_apps:
            return {
                'success': False,
                'error': f"缺少应用: {missing_apps}",
                'running_apps': node_info.applications
            }
        
        return {
            'success': True,
            'running_apps': node_info.applications
        }
    
    def check_cluster_health(self) -> Dict:
        """检查整个集群健康状态"""
        cluster_health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': ClusterStatus.HEALTHY,
            'nodes': [],
            'cluster_metrics': ClusterMetrics(),
            'recommendations': []
        }
        
        healthy_nodes = 0
        total_nodes = len(self.cluster_manager.nodes)
        
        for node in self.cluster_manager.nodes:
            node_health = self.check_node_health(node)
            cluster_health['nodes'].append(node_health)
            
            if node_health['healthy']:
                healthy_nodes += 1
            
            # 收集节点指标
            if hasattr(node, 'metrics'):
                metrics = node.metrics
                cluster_health['cluster_metrics'].total_messages += metrics.get('messages', 0)
                cluster_health['cluster_metrics'].total_connections += metrics.get('connections', 0)
                cluster_health['cluster_metrics'].memory_usage_pct = max(
                    cluster_health['cluster_metrics'].memory_usage_pct,
                    metrics.get('memory_usage', 0)
                )
        
        # 计算集群健康状态
        healthy_ratio = healthy_nodes / total_nodes if total_nodes > 0 else 0
        
        if healthy_ratio == 1.0:
            cluster_health['overall_status'] = ClusterStatus.HEALTHY
        elif healthy_ratio >= 0.7:
            cluster_health['overall_status'] = ClusterStatus.WARNING
        else:
            cluster_health['overall_status'] = ClusterStatus.CRITICAL
        
        # 生成建议
        cluster_health['recommendations'] = self._generate_recommendations(cluster_health)
        
        return cluster_health
    
    def _generate_recommendations(self, cluster_health: Dict) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        # 基于健康状态的建议
        if cluster_health['overall_status'] == ClusterStatus.CRITICAL:
            recommendations.append("集群状态严重，请立即检查故障节点")
            recommendations.append("考虑启动应急故障恢复程序")
        elif cluster_health['overall_status'] == ClusterStatus.WARNING:
            recommendations.append("集群状态警告，建议检查资源使用情况")
        
        # 基于节点状态的建议
        unhealthy_nodes = [node for node in cluster_health['nodes'] if not node['healthy']]
        if len(unhealthy_nodes) > 0:
            recommendations.append(f"有 {len(unhealthy_nodes)} 个节点不健康，建议检查网络连接和资源使用")
        
        # 基于性能指标的建议
        metrics = cluster_health['cluster_metrics']
        if metrics.memory_usage_pct > 80:
            recommendations.append("内存使用率较高，建议优化应用或增加节点")
        
        if metrics.disk_usage_pct > 90:
            recommendations.append("磁盘使用率过高，建议清理旧数据或扩展存储")
        
        # 基于连接数的建议
        if metrics.total_connections > 5000:
            recommendations.append("连接数较多，建议检查是否有连接泄漏")
        
        return recommendations


class MirrorQueueManager:
    """镜像队列管理器"""
    
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager
        self.logger = logging.getLogger(__name__)
    
    def get_queue_info(self, queue_name: str, vhost: str = '/') -> Optional[QueueInfo]:
        """获取队列详细信息"""
        try:
            # 从任意健康节点获取信息
            healthy_node = self._get_healthy_node()
            if not healthy_node:
                return None
            
            url = f"http://{healthy_node.host}:15672/api/queues/{vhost}/{queue_name}"
            response = requests.get(
                url,
                auth=(self.cluster_manager.username, self.cluster_manager.password),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return QueueInfo(
                    name=data['name'],
                    vhost=data['vhost'],
                    durable=data['durable'],
                    messages=data['messages'],
                    consumers=data['consumer_details'] and len(data['consumer_details']) or 0,
                    policy=data.get('policy', ''),
                    master_pid=data.get('leader', ''),
                    slave_pids=data.get('mirror_senders', []),
                    sync_state=data.get('state', 'running')
                )
            
        except Exception as e:
            self.logger.error(f"获取队列信息失败: {e}")
        
        return None
    
    def set_mirror_policy(self, queue_name: str, policy: MirrorPolicy, 
                         params: Dict, vhost: str = '/') -> bool:
        """设置镜像策略"""
        try:
            healthy_node = self._get_healthy_node()
            if not healthy_node:
                return False
            
            # 构建策略参数
            if policy == MirrorPolicy.ALL:
                policy_config = {
                    "ha-mode": "all",
                    "ha-sync-mode": params.get("sync_mode", "automatic")
                }
            elif policy == MirrorPolicy.EXACTLY:
                policy_config = {
                    "ha-mode": "exactly",
                    "ha-params": params.get("exactly", 2)
                }
            elif policy == MirrorPolicy.NODES:
                policy_config = {
                    "ha-mode": "nodes",
                    "ha-nodes": params.get("nodes", [])
                }
            else:
                policy_config = {}
            
            policy_name = f"ha-{queue_name}"
            
            # 应用策略
            cmd = [
                "rabbitmqctl", "set_policy",
                "-p", vhost,
                policy_name,
                f"^{queue_name}$",
                json.dumps(policy_config)
            ]
            
            # 执行命令
            result = self._execute_command_on_node(healthy_node, cmd)
            return result.get('success', False)
            
        except Exception as e:
            self.logger.error(f"设置镜像策略失败: {e}")
            return False
    
    def sync_queue(self, queue_name: str, vhost: str = '/') -> bool:
        """手动同步队列"""
        try:
            healthy_node = self._get_healthy_node()
            if not healthy_node:
                return False
            
            cmd = ["rabbitmqctl", "sync_queue", "-p", vhost, queue_name]
            result = self._execute_command_on_node(healthy_node, cmd)
            
            return result.get('success', False)
            
        except Exception as e:
            self.logger.error(f"同步队列失败: {e}")
            return False
    
    def cancel_sync_queue(self, queue_name: str, vhost: str = '/') -> bool:
        """取消队列同步"""
        try:
            healthy_node = self._get_healthy_node()
            if not healthy_node:
                return False
            
            cmd = ["rabbitmqctl", "cancel_sync_queue", "-p", vhost, queue_name]
            result = self._execute_command_on_node(healthy_node, cmd)
            
            return result.get('success', False)
            
        except Exception as e:
            self.logger.error(f"取消队列同步失败: {e}")
            return False
    
    def get_all_queues_status(self) -> List[QueueInfo]:
        """获取所有队列状态"""
        queues = []
        
        try:
            healthy_node = self._get_healthy_node()
            if not healthy_node:
                return queues
            
            url = f"http://{healthy_node.host}:15672/api/queues"
            response = requests.get(
                url,
                auth=(self.cluster_manager.username, self.cluster_manager.password),
                timeout=10
            )
            
            if response.status_code == 200:
                for queue_data in response.json():
                    queue_info = QueueInfo(
                        name=queue_data['name'],
                        vhost=queue_data['vhost'],
                        durable=queue_data['durable'],
                        messages=queue_data['messages'],
                        consumers=queue_data['consumer_details'] and len(queue_data['consumer_details']) or 0,
                        policy=queue_data.get('policy', ''),
                        master_pid=queue_data.get('leader', ''),
                        slave_pids=queue_data.get('mirror_senders', []),
                        sync_state=queue_data.get('state', 'running')
                    )
                    queues.append(queue_info)
            
        except Exception as e:
            self.logger.error(f"获取队列状态失败: {e}")
        
        return queues
    
    def _get_healthy_node(self) -> Optional[NodeInfo]:
        """获取健康节点"""
        for node in self.cluster_manager.nodes:
            if node.status == NodeStatus.RUNNING:
                return node
        return None
    
    def _execute_command_on_node(self, node: NodeInfo, cmd: List[str]) -> Dict:
        """在指定节点执行命令"""
        try:
            ssh_cmd = ["ssh", "-o", "ConnectTimeout=10", f"root@{node.host}"] + cmd
            
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager
        self.logger = logging.getLogger(__name__)
        self.strategy = 'round_robin'
        self.node_weights = {}
        self.connection_counts = {}
    
    def set_strategy(self, strategy: str):
        """设置负载均衡策略"""
        valid_strategies = ['round_robin', 'least_connections', 'weighted', 'random']
        if strategy in valid_strategies:
            self.strategy = strategy
        else:
            raise ValueError(f"不支持的负载均衡策略: {strategy}")
    
    def set_node_weights(self, weights: Dict[str, float]):
        """设置节点权重"""
        self.node_weights = weights
    
    def select_node(self) -> Optional[NodeInfo]:
        """选择节点"""
        healthy_nodes = [
            node for node in self.cluster_manager.nodes 
            if node.status == NodeStatus.RUNNING
        ]
        
        if not healthy_nodes:
            return None
        
        if self.strategy == 'round_robin':
            return self._round_robin_select(healthy_nodes)
        elif self.strategy == 'least_connections':
            return self._least_connections_select(healthy_nodes)
        elif self.strategy == 'weighted':
            return self._weighted_select(healthy_nodes)
        elif self.strategy == 'random':
            import random
            return random.choice(healthy_nodes)
        
        return healthy_nodes[0]
    
    def _round_robin_select(self, nodes: List[NodeInfo]) -> NodeInfo:
        """轮询选择"""
        index = getattr(self, '_round_robin_index', 0)
        selected = nodes[index % len(nodes)]
        self._round_robin_index = (index + 1) % len(nodes)
        return selected
    
    def _least_connections_select(self, nodes: List[NodeInfo]) -> NodeInfo:
        """最少连接选择"""
        return min(nodes, key=lambda n: n.connections)
    
    def _weighted_select(self, nodes: List[NodeInfo]) -> NodeInfo:
        """加权选择"""
        weights = []
        total_weight = 0
        
        for node in nodes:
            weight = self.node_weights.get(node.name, 1.0)
            weights.append((node, weight))
            total_weight += weight
        
        if total_weight == 0:
            return nodes[0]
        
        import random
        random_weight = random.uniform(0, total_weight)
        
        weight_sum = 0
        for node, weight in weights:
            weight_sum += weight
            if random_weight <= weight_sum:
                return node
        
        return nodes[0]
    
    def get_connection(self, queue_name: str = None) -> Optional[pika.BlockingConnection]:
        """获取连接（带负载均衡）"""
        node = self.select_node()
        if not node:
            return None
        
        try:
            credentials = pika.PlainCredentials(
                self.cluster_manager.username,
                self.cluster_manager.password
            )
            parameters = pika.ConnectionParameters(
                host=node.host,
                port=node.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=1,
                heartbeat=60
            )
            
            connection = pika.BlockingConnection(parameters)
            
            # 更新连接计数
            self.connection_counts[node.name] = self.connection_counts.get(node.name, 0) + 1
            
            return connection
            
        except Exception as e:
            self.logger.error(f"创建连接到节点 {node.name} 失败: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """获取负载均衡统计"""
        total_connections = sum(self.connection_counts.values())
        
        return {
            'strategy': self.strategy,
            'total_connections': total_connections,
            'node_connections': self.connection_counts.copy(),
            'node_weights': self.node_weights.copy()
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.monitoring_active = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: int = 30):
        """启动性能监控"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("性能监控已停止")
    
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.monitoring_active:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # 保持历史记录数量（最近100条）
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                # 检查告警
                self._check_alerts(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
                time.sleep(interval)
    
    def collect_metrics(self) -> ClusterMetrics:
        """收集集群指标"""
        metrics = ClusterMetrics()
        
        for node in self.cluster_manager.nodes:
            if node.status == NodeStatus.RUNNING:
                try:
                    node_metrics = self._collect_node_metrics(node)
                    metrics.total_messages += node_metrics.get('messages', 0)
                    metrics.total_connections += node_metrics.get('connections', 0)
                    metrics.total_queues += node_metrics.get('queues', 0)
                    
                    # 计算总体指标
                    metrics.memory_usage_pct = max(
                        metrics.memory_usage_pct,
                        node_metrics.get('memory_usage', 0)
                    )
                    
                except Exception as e:
                    self.logger.error(f"收集节点 {node.name} 指标失败: {e}")
        
        return metrics
    
    def _collect_node_metrics(self, node: NodeInfo) -> Dict:
        """收集单个节点指标"""
        try:
            url = f"http://{node.host}:15672/api/overview"
            response = requests.get(
                url,
                auth=(self.cluster_manager.username, self.cluster_manager.password),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'messages': data.get('queue_totals', {}).get('messages', 0),
                    'connections': data.get('connection_totals', {}).get('current', 0),
                    'channels': data.get('channel_totals', {}).get('current', 0),
                    'exchanges': len(data.get('exchange_details', [])),
                    'queues': len(data.get('queue_details', [])),
                    'memory_usage': self._calculate_memory_usage(node),
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            self.logger.error(f"收集节点指标失败: {e}")
        
        return {}
    
    def _calculate_memory_usage(self, node: NodeInfo) -> float:
        """计算内存使用率"""
        # 这里应该调用系统API获取实际的内存使用情况
        # 暂时返回node_info中的值
        return node.memory_usage
    
    def _check_alerts(self, metrics: ClusterMetrics):
        """检查告警条件"""
        alerts = []
        
        # 内存使用告警
        if metrics.memory_usage_pct > 85:
            alerts.append(f"内存使用率过高: {metrics.memory_usage_pct:.1f}%")
        
        # 连接数告警
        if metrics.total_connections > 5000:
            alerts.append(f"连接数过多: {metrics.total_connections}")
        
        # 消息积压告警
        if metrics.total_messages > 100000:
            alerts.append(f"消息积压严重: {metrics.total_messages}")
        
        if alerts:
            self.logger.warning(f"性能告警: {'; '.join(alerts)}")
    
    def get_performance_report(self, duration_minutes: int = 60) -> Dict:
        """生成性能报告"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        # 过滤时间范围内的数据
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.get('timestamp', datetime.now().isoformat())) > cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': '没有足够的历史数据进行性能分析'}
        
        # 计算统计数据
        messages_count = [m.get('total_messages', 0) for m in recent_metrics]
        connections_count = [m.get('total_connections', 0) for m in recent_metrics]
        memory_usage = [m.get('memory_usage_pct', 0) for m in recent_metrics]
        
        report = {
            'duration_minutes': duration_minutes,
            'data_points': len(recent_metrics),
            'metrics': {
                'messages': {
                    'current': messages_count[-1] if messages_count else 0,
                    'min': min(messages_count) if messages_count else 0,
                    'max': max(messages_count) if messages_count else 0,
                    'avg': statistics.mean(messages_count) if messages_count else 0,
                    'trend': 'increasing' if len(messages_count) > 1 and messages_count[-1] > messages_count[0] else 'stable'
                },
                'connections': {
                    'current': connections_count[-1] if connections_count else 0,
                    'min': min(connections_count) if connections_count else 0,
                    'max': max(connections_count) if connections_count else 0,
                    'avg': statistics.mean(connections_count) if connections_count else 0,
                    'trend': 'increasing' if len(connections_count) > 1 and connections_count[-1] > connections_count[0] else 'stable'
                },
                'memory_usage': {
                    'current': memory_usage[-1] if memory_usage else 0,
                    'min': min(memory_usage) if memory_usage else 0,
                    'max': max(memory_usage) if memory_usage else 0,
                    'avg': statistics.mean(memory_usage) if memory_usage else 0,
                    'trend': 'increasing' if len(memory_usage) > 1 and memory_usage[-1] > memory_usage[0] else 'stable'
                }
            }
        }
        
        return report


class ClusterManager:
    """RabbitMQ集群管理器"""
    
    def __init__(self, nodes: List[str], username: str, password: str):
        self.nodes = [
            NodeInfo(
                name=f"rabbit@{node.split('.')[0]}",
                host=node,
                port=5672,
                status=NodeStatus.UNKNOWN
            ) for node in nodes
        ]
        self.username = username
        self.password = password
        
        # 初始化组件
        self.health_checker = ClusterHealthChecker(self)
        self.mirror_manager = MirrorQueueManager(self)
        self.load_balancer = LoadBalancer(self)
        self.performance_monitor = PerformanceMonitor(self)
        
        # 配置日志
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志记录"""
        logger = logging.getLogger('RabbitMQClusterManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def discover_nodes(self) -> List[NodeInfo]:
        """发现集群节点"""
        discovered_nodes = []
        
        for node in self.nodes:
            try:
                # 使用RabbitMQ API获取节点信息
                url = f"http://{node.host}:15672/api/nodes"
                response = requests.get(
                    url,
                    auth=(self.username, self.password),
                    timeout=10
                )
                
                if response.status_code == 200:
                    nodes_data = response.json()
                    
                    for node_data in nodes_data:
                        if node_data.get('running_applications'):
                            discovered_node = NodeInfo(
                                name=node_data['name'],
                                host=node.host,
                                port=5672,
                                status=NodeStatus.RUNNING,
                                memory_usage=self._calculate_memory_percent(node_data),
                                disk_free=node_data.get('disk_free', 0),
                                connections=0,  # 需要单独查询
                                uptime=node_data.get('uptime', 0),
                                applications=node_data.get('running_applications', [])
                            )
                            discovered_nodes.append(discovered_node)
                
            except Exception as e:
                self.logger.warning(f"发现节点 {node.host} 失败: {e}")
                discovered_nodes.append(NodeInfo(
                    name=f"rabbit@{node.host.split('.')[0]}",
                    host=node.host,
                    port=5672,
                    status=NodeStatus.DOWN
                ))
        
        self.nodes = discovered_nodes
        return discovered_nodes
    
    def _calculate_memory_percent(self, node_data: Dict) -> float:
        """计算内存使用率"""
        memory_used = node_data.get('memory_used', 0)
        memory_limit = node_data.get('memory_limit', 1)
        
        if memory_limit > 0:
            return (memory_used / memory_limit) * 100
        return 0
    
    def start_cluster(self):
        """启动集群"""
        for node in self.nodes:
            try:
                self.logger.info(f"启动节点: {node.name}")
                
                cmd = ["ssh", "-o", "ConnectTimeout=30", f"root@{node.host}", 
                       "systemctl", "start", "rabbitmq-server"]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    node.status = NodeStatus.RUNNING
                    self.logger.info(f"节点 {node.name} 启动成功")
                else:
                    node.status = NodeStatus.DOWN
                    self.logger.error(f"节点 {node.name} 启动失败: {result.stderr}")
                
            except Exception as e:
                node.status = NodeStatus.DOWN
                self.logger.error(f"启动节点 {node.name} 异常: {e}")
    
    def stop_cluster(self):
        """停止集群"""
        for node in self.nodes:
            try:
                self.logger.info(f"停止节点: {node.name}")
                
                cmd = ["ssh", "-o", "ConnectTimeout=30", f"root@{node.host}", 
                       "systemctl", "stop", "rabbitmq-server"]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    node.status = NodeStatus.STOPPED
                    self.logger.info(f"节点 {node.name} 停止成功")
                else:
                    self.logger.error(f"节点 {node.name} 停止失败: {result.stderr}")
                
            except Exception as e:
                self.logger.error(f"停止节点 {node.name} 异常: {e}")
    
    def restart_node(self, node_name: str) -> bool:
        """重启指定节点"""
        node = next((n for n in self.nodes if n.name == node_name), None)
        if not node:
            self.logger.error(f"节点不存在: {node_name}")
            return False
        
        try:
            self.logger.info(f"重启节点: {node_name}")
            
            cmd = ["ssh", "-o", "ConnectTimeout=30", f"root@{node.host}", 
                   "systemctl", "restart", "rabbitmq-server"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 等待服务启动
                time.sleep(30)
                node.status = NodeStatus.RUNNING
                self.logger.info(f"节点 {node_name} 重启成功")
                return True
            else:
                node.status = NodeStatus.DOWN
                self.logger.error(f"节点 {node_name} 重启失败: {result.stderr}")
                return False
            
        except Exception as e:
            node.status = NodeStatus.DOWN
            self.logger.error(f"重启节点 {node_name} 异常: {e}")
            return False
    
    def add_node_to_cluster(self, new_node: str, master_node: str = None) -> bool:
        """将节点加入集群"""
        if not master_node:
            # 选择第一个运行中的节点作为主节点
            master_node_obj = next((n for n in self.nodes if n.status == NodeStatus.RUNNING), None)
            if not master_node_obj:
                self.logger.error("没有可用的主节点")
                return False
            master_node = master_node_obj.name
        
        try:
            new_node_info = NodeInfo(
                name=f"rabbit@{new_node.split('.')[0]}",
                host=new_node,
                port=5672,
                status=NodeStatus.RUNNING
            )
            
            self.logger.info(f"将节点 {new_node} 加入集群，主节点: {master_node}")
            
            # 在新节点上执行join命令
            cmd = [
                "ssh", "-o", "ConnectTimeout=30", f"root@{new_node}",
                "rabbitmqctl", "stop_app", "&&",
                "rabbitmqctl", "reset", "&&",
                "rabbitmqctl", "join_cluster", master_node, "&&",
                "rabbitmqctl", "start_app"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.nodes.append(new_node_info)
                self.logger.info(f"节点 {new_node} 加入集群成功")
                return True
            else:
                self.logger.error(f"节点 {new_node} 加入集群失败: {result.stderr}")
                return False
            
        except Exception as e:
            self.logger.error(f"加入节点异常: {e}")
            return False
    
    def remove_node_from_cluster(self, node_name: str) -> bool:
        """从集群中移除节点"""
        node = next((n for n in self.nodes if n.name == node_name), None)
        if not node:
            self.logger.error(f"节点不存在: {node_name}")
            return False
        
        try:
            self.logger.info(f"从集群中移除节点: {node_name}")
            
            # 停止节点应用
            cmd = ["ssh", "-o", "ConnectTimeout=30", f"root@{node.host}", 
                   "rabbitmqctl", "forget_cluster_node", node_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 从本地节点列表中移除
                self.nodes = [n for n in self.nodes if n.name != node_name]
                self.logger.info(f"节点 {node_name} 移除成功")
                return True
            else:
                self.logger.error(f"节点 {node_name} 移除失败: {result.stderr}")
                return False
            
        except Exception as e:
            self.logger.error(f"移除节点异常: {e}")
            return False
    
    def get_cluster_status(self) -> Dict:
        """获取集群状态"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'cluster_name': 'rabbitmq_cluster',
            'nodes': [asdict(node) for node in self.nodes],
            'overall_status': self._calculate_overall_status(),
            'statistics': self._calculate_statistics()
        }
        
        return status
    
    def _calculate_overall_status(self) -> ClusterStatus:
        """计算整体集群状态"""
        running_nodes = sum(1 for node in self.nodes if node.status == NodeStatus.RUNNING)
        total_nodes = len(self.nodes)
        
        if total_nodes == 0:
            return ClusterStatus.UNKNOWN
        
        if running_nodes == total_nodes:
            return ClusterStatus.HEALTHY
        elif running_nodes >= total_nodes * 0.7:
            return ClusterStatus.WARNING
        else:
            return ClusterStatus.CRITICAL
    
    def _calculate_statistics(self) -> Dict:
        """计算集群统计信息"""
        total_messages = 0
        total_connections = 0
        total_queues = 0
        
        for node in self.nodes:
            if node.status == NodeStatus.RUNNING:
                total_messages += 0  # 需要从API获取
                total_connections += node.connections
                total_queues += node.queues
        
        return {
            'total_nodes': len(self.nodes),
            'running_nodes': sum(1 for n in self.nodes if n.status == NodeStatus.RUNNING),
            'total_messages': total_messages,
            'total_connections': total_connections,
            'total_queues': total_queues
        }
    
    def backup_cluster_config(self, backup_path: str) -> bool:
        """备份集群配置"""
        try:
            self.logger.info(f"开始备份集群配置到: {backup_path}")
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'cluster_config': self.get_cluster_status(),
                'users': self._export_users(),
                'policies': self._export_policies(),
                'queues': self._export_queue_configs()
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            self.logger.info("集群配置备份完成")
            return True
            
        except Exception as e:
            self.logger.error(f"备份集群配置失败: {e}")
            return False
    
    def _export_users(self) -> List[Dict]:
        """导出用户配置"""
        try:
            healthy_node = next((n for n in self.nodes if n.status == NodeStatus.RUNNING), None)
            if not healthy_node:
                return []
            
            cmd = ["rabbitmqctl", "list_users", "--formatter", "json"]
            
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=30", f"root@{healthy_node.host}"] + cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
        
        except Exception as e:
            self.logger.error(f"导出用户配置失败: {e}")
        
        return []
    
    def _export_policies(self) -> List[Dict]:
        """导出策略配置"""
        try:
            healthy_node = next((n for n in self.nodes if n.status == NodeStatus.RUNNING), None)
            if not healthy_node:
                return []
            
            cmd = ["rabbitmqctl", "list_policies", "--formatter", "json"]
            
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=30", f"root@{healthy_node.host}"] + cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
        
        except Exception as e:
            self.logger.error(f"导出策略配置失败: {e}")
        
        return []
    
    def _export_queue_configs(self) -> List[Dict]:
        """导出队列配置"""
        try:
            healthy_node = next((n for n in self.nodes if n.status == NodeStatus.RUNNING), None)
            if not healthy_node:
                return []
            
            # 获取队列列表
            cmd = ["rabbitmqctl", "list_queues", "name", "durable", "policy"]
            
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=30", f"root@{healthy_node.host}"] + cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                queues = []
                
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        queues.append({
                            'name': parts[0],
                            'durable': parts[1] == 'True',
                            'policy': parts[2] if len(parts) > 2 else ''
                        })
                
                return queues
        
        except Exception as e:
            self.logger.error(f"导出队列配置失败: {e}")
        
        return []


def main():
    """主函数 - 演示集群管理器功能"""
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 集群配置
    cluster_nodes = [
        "node1.example.com",
        "node2.example.com", 
        "node3.example.com"
    ]
    username = "admin"
    password = "admin123"
    
    # 创建集群管理器
    cluster_manager = ClusterManager(cluster_nodes, username, password)
    
    print("=== RabbitMQ集群管理器演示 ===")
    
    # 1. 发现集群节点
    print("\n1. 发现集群节点...")
    nodes = cluster_manager.discover_nodes()
    print(f"发现 {len(nodes)} 个节点")
    
    # 2. 获取集群状态
    print("\n2. 获取集群状态...")
    status = cluster_manager.get_cluster_status()
    print(f"集群状态: {status['overall_status'].value}")
    print(f"节点数量: {status['statistics']['total_nodes']}")
    
    # 3. 健康检查
    print("\n3. 执行健康检查...")
    health_report = cluster_manager.health_checker.check_cluster_health()
    print(f"集群健康状态: {health_report['overall_status'].value}")
    print(f"健康节点: {sum(1 for node in health_report['nodes'] if node['healthy'])}/{len(health_report['nodes'])}")
    
    # 4. 镜像队列管理
    print("\n4. 镜像队列管理...")
    queues = cluster_manager.mirror_manager.get_all_queues_status()
    print(f"发现 {len(queues)} 个队列")
    
    # 设置镜像策略示例
    # cluster_manager.mirror_manager.set_mirror_policy(
    #     "test_queue", 
    #     MirrorPolicy.ALL, 
    #     {"sync_mode": "automatic"}
    # )
    
    # 5. 负载均衡
    print("\n5. 负载均衡测试...")
    cluster_manager.load_balancer.set_strategy('least_connections')
    selected_node = cluster_manager.load_balancer.select_node()
    if selected_node:
        print(f"选择节点: {selected_node.name}")
    
    # 6. 性能监控
    print("\n6. 启动性能监控...")
    cluster_manager.performance_monitor.start_monitoring(interval=5)
    
    # 运行10秒监控
    time.sleep(10)
    
    # 获取性能报告
    performance_report = cluster_manager.performance_monitor.get_performance_report(duration_minutes=1)
    print(f"监控数据点: {performance_report.get('data_points', 0)}")
    
    # 停止监控
    cluster_manager.performance_monitor.stop_monitoring()
    
    # 7. 备份配置
    print("\n7. 备份集群配置...")
    backup_success = cluster_manager.backup_cluster_config("cluster_backup.json")
    print(f"备份结果: {'成功' if backup_success else '失败'}")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()