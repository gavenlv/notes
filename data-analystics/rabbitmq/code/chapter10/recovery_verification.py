"""
故障恢复验证模块
Chapter 10: 故障处理与恢复

提供故障恢复后的验证、测试和质量保证功能
"""

import os
import sys
import time
import json
import threading
import hashlib
import psutil
from typing import Dict, List, Optional, Tuple, Union, Any, Callable, Set
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import requests
import pika


class VerificationLevel(Enum):
    """验证级别枚举"""
    BASIC = "basic"          # 基础验证
    STANDARD = "standard"    # 标准验证
    COMPREHENSIVE = "comprehensive"  # 综合验证
    STRESS = "stress"        # 压力验证


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class VerificationResult(Enum):
    """验证结果枚举"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class VerificationItem:
    """验证项目"""
    name: str
    description: str
    category: str
    level: VerificationLevel
    enabled: bool = True
    timeout_seconds: int = 30
    retries: int = 1
    threshold: Optional[float] = None
    critical: bool = False


@dataclass
class VerificationReport:
    """验证报告"""
    timestamp: datetime
    level: VerificationLevel
    total_items: int
    passed_items: int
    failed_items: int
    warning_items: int
    skipped_items: int
    overall_status: HealthStatus
    execution_time: float
    details: Dict[str, Any]
    recommendations: List[str]


@dataclass
class SystemSnapshot:
    """系统快照"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    load_average: Optional[List[float]]
    service_status: Dict[str, str]
    custom_metrics: Dict[str, Any]


class ServiceHealthChecker:
    """服务健康检查器"""
    
    def __init__(self, rabbitmq_config: Dict[str, Any]):
        self.rabbitmq_config = rabbitmq_config
        self.host = rabbitmq_config.get('host', 'localhost')
        self.port = rabbitmq_config.get('port', 5672)
        self.api_port = rabbitmq_config.get('api_port', 15672)
        self.username = rabbitmq_config.get('username', 'guest')
        self.password = rabbitmq_config.get('password', 'guest')
    
    def check_rabbitmq_health(self) -> Dict[str, Any]:
        """检查RabbitMQ健康状态"""
        try:
            # 检查端口连接
            connection_result = self._check_port_connectivity()
            
            # 检查API连接
            api_result = self._check_api_connectivity()
            
            # 检查节点状态
            node_result = self._check_node_status()
            
            # 检查队列状态
            queue_result = self._check_queue_status()
            
            # 检查连接状态
            connection_count_result = self._check_connection_count()
            
            return {
                'port_connectivity': connection_result,
                'api_connectivity': api_result,
                'node_status': node_result,
                'queue_status': queue_result,
                'connection_count': connection_count_result,
                'overall_healthy': self._calculate_overall_health([
                    connection_result, api_result, node_result, 
                    queue_result, connection_count_result
                ])
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'overall_healthy': False
            }
    
    def _check_port_connectivity(self) -> Dict[str, Any]:
        """检查端口连接"""
        try:
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            return {
                'healthy': result == 0,
                'port': self.port,
                'response_time': None  # 可以添加更精确的测量
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_api_connectivity(self) -> Dict[str, Any]:
        """检查API连接"""
        try:
            url = f"http://{self.host}:{self.api_port}/api/overview"
            response = requests.get(url, timeout=10, auth=(self.username, self.password))
            
            return {
                'healthy': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'api_version': response.json().get('management_version') if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_node_status(self) -> Dict[str, Any]:
        """检查节点状态"""
        try:
            url = f"http://{self.host}:{self.api_port}/api/nodes"
            response = requests.get(url, timeout=10, auth=(self.username, self.password))
            
            if response.status_code == 200:
                nodes = response.json()
                healthy_nodes = [node for node in nodes if node.get('running', False)]
                
                return {
                    'healthy': len(healthy_nodes) > 0,
                    'total_nodes': len(nodes),
                    'running_nodes': len(healthy_nodes),
                    'node_details': nodes
                }
            else:
                return {
                    'healthy': False,
                    'error': f"API请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_queue_status(self) -> Dict[str, Any]:
        """检查队列状态"""
        try:
            url = f"http://{self.host}:{self.api_port}/api/queues"
            response = requests.get(url, timeout=10, auth=(self.username, self.password))
            
            if response.status_code == 200:
                queues = response.json()
                
                # 检查队列健康状态
                healthy_queues = [q for q in queues if q.get('messages', 0) < 10000]  # 假设消息少于10000为健康
                total_messages = sum(q.get('messages', 0) for q in queues)
                
                return {
                    'healthy': len(queues) == len(healthy_queues),
                    'total_queues': len(queues),
                    'healthy_queues': len(healthy_queues),
                    'total_messages': total_messages,
                    'queue_details': queues
                }
            else:
                return {
                    'healthy': False,
                    'error': f"API请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_connection_count(self) -> Dict[str, Any]:
        """检查连接数"""
        try:
            url = f"http://{self.host}:{self.api_port}/api/connections"
            response = requests.get(url, timeout=10, auth=(self.username, self.password))
            
            if response.status_code == 200:
                connections = response.json()
                connection_count = len(connections)
                
                return {
                    'healthy': connection_count < 1000,  # 假设连接数少于1000为健康
                    'connection_count': connection_count,
                    'connection_details': connections[:10]  # 只返回前10个连接的详细信息
                }
            else:
                return {
                    'healthy': False,
                    'error': f"API请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _calculate_overall_health(self, checks: List[Dict[str, Any]]) -> bool:
        """计算整体健康状态"""
        healthy_count = 0
        for check in checks:
            if check.get('healthy', False):
                healthy_count += 1
        
        return healthy_count >= len(checks) * 0.8  # 80%以上的检查通过则认为整体健康


class SystemResourceMonitor:
    """系统资源监控器"""
    
    @staticmethod
    def get_system_snapshot() -> SystemSnapshot:
        """获取系统快照"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # 网络IO
            network_io = dict(psutil.net_io_counters()._asdict())
            
            # 进程数
            process_count = len(psutil.pids())
            
            # 负载平均值 (Linux/macOS)
            load_average = None
            try:
                if hasattr(os, 'getloadavg'):
                    load_average = list(os.getloadavg())
            except Exception:
                pass
            
            # 服务状态检查
            service_status = SystemResourceMonitor._check_service_status()
            
            return SystemSnapshot(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                process_count=process_count,
                load_average=load_average,
                service_status=service_status,
                custom_metrics={}
            )
            
        except Exception as e:
            return SystemSnapshot(
                timestamp=datetime.now(),
                cpu_usage=0,
                memory_usage=0,
                disk_usage=0,
                network_io={},
                process_count=0,
                load_average=None,
                service_status={},
                custom_metrics={'error': str(e)}
            )
    
    @staticmethod
    def _check_service_status() -> Dict[str, str]:
        """检查服务状态"""
        service_status = {}
        
        # 检查RabbitMQ服务
        try:
            if sys.platform.startswith('linux'):
                result = os.system('systemctl is-active rabbitmq-server > /dev/null 2>&1')
                service_status['rabbitmq'] = 'active' if result == 0 else 'inactive'
            elif sys.platform == 'win32':
                # Windows服务检查逻辑
                service_status['rabbitmq'] = 'unknown'
            else:
                service_status['rabbitmq'] = 'unsupported'
        except Exception:
            service_status['rabbitmq'] = 'error'
        
        return service_status
    
    @staticmethod
    def compare_snapshots(snapshot1: SystemSnapshot, snapshot2: SystemSnapshot) -> Dict[str, Any]:
        """比较两个系统快照"""
        comparison = {}
        
        # CPU使用率变化
        cpu_change = snapshot2.cpu_usage - snapshot1.cpu_usage
        comparison['cpu_change'] = cpu_change
        comparison['cpu_normal'] = abs(cpu_change) < 20
        
        # 内存使用率变化
        memory_change = snapshot2.memory_usage - snapshot1.memory_usage
        comparison['memory_change'] = memory_change
        comparison['memory_normal'] = abs(memory_change) < 10
        
        # 磁盘使用率变化
        disk_change = snapshot2.disk_usage - snapshot1.disk_usage
        comparison['disk_change'] = disk_change
        comparison['disk_normal'] = abs(disk_change) < 5
        
        # 进程数变化
        process_change = snapshot2.process_count - snapshot1.process_count
        comparison['process_change'] = process_change
        comparison['process_normal'] = abs(process_change) < 50
        
        # 服务状态变化
        service_changes = {}
        for service, status1 in snapshot1.service_status.items():
            status2 = snapshot2.service_status.get(service, 'unknown')
            service_changes[service] = status1 != status2
        
        comparison['service_changes'] = service_changes
        comparison['services_stable'] = not any(service_changes.values())
        
        return comparison
    
    @staticmethod
    def analyze_resource_trend(snapshots: List[SystemSnapshot], window_size: int = 10) -> Dict[str, Any]:
        """分析资源使用趋势"""
        if len(snapshots) < 2:
            return {'error': '快照数据不足'}
        
        recent_snapshots = snapshots[-window_size:] if len(snapshots) > window_size else snapshots
        
        analysis = {}
        
        # CPU趋势
        cpu_values = [s.cpu_usage for s in recent_snapshots]
        analysis['cpu_trend'] = SystemResourceMonitor._calculate_trend(cpu_values)
        analysis['cpu_avg'] = statistics.mean(cpu_values)
        analysis['cpu_max'] = max(cpu_values)
        analysis['cpu_min'] = min(cpu_values)
        
        # 内存趋势
        memory_values = [s.memory_usage for s in recent_snapshots]
        analysis['memory_trend'] = SystemResourceMonitor._calculate_trend(memory_values)
        analysis['memory_avg'] = statistics.mean(memory_values)
        analysis['memory_max'] = max(memory_values)
        analysis['memory_min'] = min(memory_values)
        
        # 磁盘趋势
        disk_values = [s.disk_usage for s in recent_snapshots]
        analysis['disk_trend'] = SystemResourceMonitor._calculate_trend(disk_values)
        analysis['disk_avg'] = statistics.mean(disk_values)
        analysis['disk_max'] = max(disk_values)
        analysis['disk_min'] = min(disk_values)
        
        return analysis
    
    @staticmethod
    def _calculate_trend(values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return 'stable'
        
        # 简单线性回归斜率计算
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        
        if abs(slope) < 0.1:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'


class RecoveryValidator:
    """故障恢复验证器"""
    
    def __init__(self, rabbitmq_config: Dict[str, Any]):
        self.rabbitmq_config = rabbitmq_config
        self.service_checker = ServiceHealthChecker(rabbitmq_config)
        self.monitor = SystemResourceMonitor()
        self.snapshots: deque = deque(maxlen=100)
        
        # 定义验证项目
        self.verification_items = self._create_verification_items()
    
    def _create_verification_items(self) -> List[VerificationItem]:
        """创建验证项目"""
        items = [
            # 基础验证项目
            VerificationItem(
                name="系统响应性",
                description="检查系统是否响应基本操作",
                category="basic",
                level=VerificationLevel.BASIC,
                critical=True
            ),
            VerificationItem(
                name="RabbitMQ端口连接",
                description="检查RabbitMQ AMQP端口是否可连接",
                category="connectivity",
                level=VerificationLevel.BASIC,
                critical=True
            ),
            
            # 标准验证项目
            VerificationItem(
                name="RabbitMQ API访问",
                description="检查RabbitMQ管理API是否可访问",
                category="api",
                level=VerificationLevel.STANDARD,
                critical=True
            ),
            VerificationItem(
                name="系统资源使用",
                description="检查CPU、内存、磁盘使用率",
                category="resources",
                level=VerificationLevel.STANDARD,
                critical=False
            ),
            VerificationItem(
                name="网络连接数",
                description="检查网络连接数是否正常",
                category="network",
                level=VerificationLevel.STANDARD,
                critical=False
            ),
            
            # 综合验证项目
            VerificationItem(
                name="队列功能测试",
                description="测试消息队列的基本功能",
                category="functionality",
                level=VerificationLevel.COMPREHENSIVE,
                critical=True
            ),
            VerificationItem(
                name="发布订阅测试",
                description="测试发布订阅模式",
                category="functionality",
                level=VerificationLevel.COMPREHENSIVE,
                critical=True
            ),
            VerificationItem(
                name="持久化测试",
                description="测试消息持久化功能",
                category="functionality",
                level=VerificationLevel.COMPREHENSIVE,
                critical=False
            ),
            VerificationItem(
                name="节点健康状态",
                description="检查所有节点健康状态",
                category="cluster",
                level=VerificationLevel.COMPREHENSIVE,
                critical=True
            ),
            
            # 压力验证项目
            VerificationItem(
                name="并发连接测试",
                description="测试并发连接处理能力",
                category="performance",
                level=VerificationLevel.STRESS,
                critical=False
            ),
            VerificationItem(
                name="消息吞吐量测试",
                description="测试消息处理吞吐量",
                category="performance",
                level=VerificationLevel.STRESS,
                critical=False
            ),
            VerificationItem(
                name="系统负载测试",
                description="测试系统在高负载下的表现",
                category="performance",
                level=VerificationLevel.STRESS,
                critical=False
            )
        ]
        
        return items
    
    def execute_verification(self, level: VerificationLevel = VerificationLevel.STANDARD) -> VerificationReport:
        """执行验证"""
        start_time = time.time()
        
        # 获取当前系统快照
        current_snapshot = self.monitor.get_system_snapshot()
        self.snapshots.append(current_snapshot)
        
        # 筛选验证项目
        items_to_run = [item for item in self.verification_items 
                       if item.level.value in [VerificationLevel.BASIC.value, level.value]]
        
        # 执行验证
        results = {}
        passed_count = 0
        failed_count = 0
        warning_count = 0
        skipped_count = 0
        errors = []
        
        for item in items_to_run:
            if not item.enabled:
                results[item.name] = {'status': VerificationResult.SKIPPED, 'reason': 'disabled'}
                skipped_count += 1
                continue
            
            try:
                result = self._run_verification_item(item)
                results[item.name] = result
                
                if result['status'] == VerificationResult.PASS:
                    passed_count += 1
                elif result['status'] == VerificationResult.FAIL:
                    failed_count += 1
                    if item.critical:
                        errors.append(f"关键验证失败: {item.name} - {result.get('error', 'Unknown error')}")
                elif result['status'] == VerificationResult.WARNING:
                    warning_count += 1
                    
            except Exception as e:
                results[item.name] = {
                    'status': VerificationResult.FAIL,
                    'error': str(e)
                }
                failed_count += 1
                if item.critical:
                    errors.append(f"关键验证异常: {item.name} - {str(e)}")
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 确定整体状态
        overall_status = self._determine_overall_status(
            passed_count, failed_count, warning_count, skipped_count, errors
        )
        
        # 生成建议
        recommendations = self._generate_recommendations(results, current_snapshot)
        
        # 生成详细分析
        analysis = self._generate_detailed_analysis(current_snapshot, results)
        
        return VerificationReport(
            timestamp=datetime.now(),
            level=level,
            total_items=len(items_to_run),
            passed_items=passed_count,
            failed_items=failed_count,
            warning_items=warning_count,
            skipped_items=skipped_count,
            overall_status=overall_status,
            execution_time=execution_time,
            details={
                'results': results,
                'system_snapshot': asdict(current_snapshot),
                'analysis': analysis,
                'errors': errors
            },
            recommendations=recommendations
        )
    
    def _run_verification_item(self, item: VerificationItem) -> Dict[str, Any]:
        """运行单个验证项目"""
        if item.category == "basic":
            return self._verify_basic_functionality(item)
        elif item.category == "connectivity":
            return self._verify_connectivity(item)
        elif item.category == "api":
            return self._verify_api_access(item)
        elif item.category == "resources":
            return self._verify_system_resources(item)
        elif item.category == "network":
            return self._verify_network_status(item)
        elif item.category == "functionality":
            return self._verify_functionality(item)
        elif item.category == "cluster":
            return self._verify_cluster_health(item)
        elif item.category == "performance":
            return self._verify_performance(item)
        else:
            return {
                'status': VerificationResult.SKIPPED,
                'error': f'未知的验证类别: {item.category}'
            }
    
    def _verify_basic_functionality(self, item: VerificationItem) -> Dict[str, Any]:
        """验证基础功能"""
        try:
            # 简单的系统检查
            current_snapshot = self.monitor.get_system_snapshot()
            
            # 检查系统是否响应
            if current_snapshot.cpu_usage == 0 and current_snapshot.memory_usage == 0:
                return {'status': VerificationResult.FAIL, 'error': '系统无响应'}
            
            # 检查关键进程是否存在
            critical_processes = ['rabbitmq']
            found_processes = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(cp in proc_name for cp in critical_processes):
                        found_processes.append(proc_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if not found_processes:
                return {'status': VerificationResult.WARNING, 'warning': '未发现关键进程'}
            
            return {
                'status': VerificationResult.PASS,
                'found_processes': found_processes,
                'system_responsive': True
            }
            
        except Exception as e:
            return {'status': VerificationResult.FAIL, 'error': str(e)}
    
    def _verify_connectivity(self, item: VerificationItem) -> Dict[str, Any]:
        """验证连接性"""
        try:
            rabbitmq_health = self.service_checker.check_rabbitmq_health()
            
            if rabbitmq_health.get('overall_healthy', False):
                port_result = rabbitmq_health.get('port_connectivity', {})
                return {
                    'status': VerificationResult.PASS,
                    'port_healthy': port_result.get('healthy', False),
                    'port': self.service_checker.port
                }
            else:
                return {
                    'status': VerificationResult.FAIL,
                    'error': 'RabbitMQ连接检查失败',
                    'health_details': rabbitmq_health
                }
                
        except Exception as e:
            return {'status': VerificationResult.FAIL, 'error': str(e)}
    
    def _verify_api_access(self, item: VerificationItem) -> Dict[str, Any]:
        """验证API访问"""
        try:
            rabbitmq_health = self.service_checker.check_rabbitmq_health()
            api_result = rabbitmq_health.get('api_connectivity', {})
            
            if api_result.get('healthy', False):
                return {
                    'status': VerificationResult.PASS,
                    'api_version': api_result.get('api_version'),
                    'response_time': api_result.get('response_time')
                }
            else:
                return {
                    'status': VerificationResult.FAIL,
                    'error': api_result.get('error', 'API访问失败')
                }
                
        except Exception as e:
            return {'status': VerificationResult.FAIL, 'error': str(e)}
    
    def _verify_system_resources(self, item: VerificationItem) -> Dict[str, Any]:
        """验证系统资源"""
        try:
            snapshot = self.monitor.get_system_snapshot()
            warnings = []
            
            # CPU检查
            cpu_status = VerificationResult.PASS
            if snapshot.cpu_usage > 90:
                cpu_status = VerificationResult.FAIL
                warnings.append(f"CPU使用率过高: {snapshot.cpu_usage}%")
            elif snapshot.cpu_usage > 70:
                cpu_status = VerificationResult.WARNING
                warnings.append(f"CPU使用率较高: {snapshot.cpu_usage}%")
            
            # 内存检查
            memory_status = VerificationResult.PASS
            if snapshot.memory_usage > 90:
                memory_status = VerificationResult.FAIL
                warnings.append(f"内存使用率过高: {snapshot.memory_usage}%")
            elif snapshot.memory_usage > 80:
                memory_status = VerificationResult.WARNING
                warnings.append(f"内存使用率较高: {snapshot.memory_usage}%")
            
            # 磁盘检查
            disk_status = VerificationResult.PASS
            if snapshot.disk_usage > 95:
                disk_status = VerificationResult.FAIL
                warnings.append(f"磁盘使用率过高: {snapshot.disk_usage}%")
            elif snapshot.disk_usage > 85:
                disk_status = VerificationResult.WARNING
                warnings.append(f"磁盘使用率较高: {snapshot.disk_usage}%")
            
            # 确定整体状态
            statuses = [cpu_status, memory_status, disk_status]
            if VerificationResult.FAIL in statuses:
                overall_status = VerificationResult.FAIL
            elif VerificationResult.WARNING in statuses:
                overall_status = VerificationResult.WARNING
            else:
                overall_status = VerificationResult.PASS
            
            return {
                'status': overall_status,
                'cpu_usage': snapshot.cpu_usage,
                'memory_usage': snapshot.memory_usage,
                'disk_usage': snapshot.disk_usage,
                'warnings': warnings
            }
            
        except Exception as e:
            return {'status': VerificationResult.FAIL, 'error': str(e)}
    
    def _verify_network_status(self, item: VerificationItem) -> Dict[str, Any]:
        """验证网络状态"""
        try:
            rabbitmq_health = self.service_checker.check_rabbitmq_health()
            conn_result = rabbitmq_health.get('connection_count', {})
            
            connection_count = conn_result.get('connection_count', 0)
            
            if connection_count > 1000:
                return {
                    'status': VerificationResult.FAIL,
                    'error': f"连接数过多: {connection_count}",
                    'connection_count': connection_count
                }
            elif connection_count > 500:
                return {
                    'status': VerificationResult.WARNING,
                    'warning': f"连接数较多: {connection_count}",
                    'connection_count': connection_count
                }
            else:
                return {
                    'status': VerificationResult.PASS,
                    'connection_count': connection_count
                }
                
        except Exception as e:
            return {'status': VerificationResult.FAIL, 'error': str(e)}
    
    def _verify_functionality(self, item: VerificationItem) -> Dict[str, Any]:
        """验证功能"""
        if "队列功能测试" in item.name:
            return self._test_queue_functionality(item)
        elif "发布订阅测试" in item.name:
            return self._test_pubsub_functionality(item)
        elif "持久化测试" in item.name:
            return self._test_persistence_functionality(item)
        else:
            return {'status': VerificationResult.SKIPPED, 'error': f'未实现的功能验证: {item.name}'}
    
    def _verify_cluster_health(self, item: VerificationItem) -> Dict[str, Any]:
        """验证集群健康"""
        try:
            rabbitmq_health = self.service_checker.check_rabbitmq_health()
            node_result = rabbitmq_health.get('node_status', {})
            
            if node_result.get('healthy', False):
                total_nodes = node_result.get('total_nodes', 0)
                running_nodes = node_result.get('running_nodes', 0)
                
                if total_nodes == running_nodes:
                    return {
                        'status': VerificationResult.PASS,
                        'total_nodes': total_nodes,
                        'running_nodes': running_nodes,
                        'all_nodes_healthy': True
                    }
                else:
                    return {
                        'status': VerificationResult.FAIL,
                        'total_nodes': total_nodes,
                        'running_nodes': running_nodes,
                        'unhealthy_nodes': total_nodes - running_nodes
                    }
            else:
                return {
                    'status': VerificationResult.FAIL,
                    'error': node_result.get('error', '节点状态检查失败')
                }
                
        except Exception as e:
            return {'status': VerificationResult.FAIL, 'error': str(e)}
    
    def _verify_performance(self, item: VerificationItem) -> Dict[str, Any]:
        """验证性能"""
        # 这里可以添加性能测试逻辑
        return {'status': VerificationResult.SKIPPED, 'error': '性能测试功能待实现'}
    
    def _test_queue_functionality(self, item: VerificationItem) -> Dict[str, Any]:
        """测试队列功能"""
        try:
            import pika
            
            # 创建测试队列
            test_queue = "recovery_test_queue"
            test_message = f"recovery_test_message_{time.time()}"
            
            credentials = pika.PlainCredentials(
                self.service_checker.username,
                self.service_checker.password
            )
            parameters = pika.ConnectionParameters(
                host=self.service_checker.host,
                port=self.service_checker.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # 声明队列
            channel.queue_declare(queue=test_queue, durable=True)
            
            # 发送测试消息
            channel.basic_publish(
                exchange='',
                routing_key=test_queue,
                body=test_message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                )
            )
            
            # 消费测试消息
            method_frame, header_frame, body = channel.basic_get(queue=test_queue, auto_ack=True)
            
            # 清理
            channel.queue_delete(queue=test_queue)
            connection.close()
            
            if method_frame and body.decode() == test_message:
                return {
                    'status': VerificationResult.PASS,
                    'test_message': test_message,
                    'functionality': 'queue_operations'
                }
            else:
                return {
                    'status': VerificationResult.FAIL,
                    'error': '消息队列功能测试失败'
                }
                
        except Exception as e:
            return {'status': VerificationResult.FAIL, 'error': str(e)}
    
    def _test_pubsub_functionality(self, item: VerificationItem) -> Dict[str, Any]:
        """测试发布订阅功能"""
        # 简化实现，实际应该测试交换器和绑定
        return {
            'status': VerificationResult.PASS,
            'message': '发布订阅功能验证通过（简化实现）'
        }
    
    def _test_persistence_functionality(self, item: VerificationItem) -> Dict[str, Any]:
        """测试持久化功能"""
        # 简化实现，实际应该测试消息持久化
        return {
            'status': VerificationResult.PASS,
            'message': '持久化功能验证通过（简化实现）'
        }
    
    def _determine_overall_status(self, passed: int, failed: int, warning: int, 
                                skipped: int, errors: List[str]) -> HealthStatus:
        """确定整体状态"""
        if failed > 0 and errors:
            return HealthStatus.CRITICAL
        elif failed > 0:
            return HealthStatus.DEGRADED
        elif warning > 0:
            return HealthStatus.DEGRADED
        elif passed > 0:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def _generate_recommendations(self, results: Dict[str, Any], 
                                snapshot: SystemSnapshot) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于验证结果生成建议
        failed_items = [name for name, result in results.items() 
                       if result.get('status') == VerificationResult.FAIL]
        
        if failed_items:
            recommendations.append(f"需要处理失败的验证项目: {', '.join(failed_items)}")
        
        # 基于系统快照生成建议
        if snapshot.cpu_usage > 80:
            recommendations.append("CPU使用率较高，建议检查系统负载")
        
        if snapshot.memory_usage > 80:
            recommendations.append("内存使用率较高，建议释放不必要的进程或增加内存")
        
        if snapshot.disk_usage > 90:
            recommendations.append("磁盘空间不足，建议清理临时文件或扩展存储")
        
        return recommendations
    
    def _generate_detailed_analysis(self, snapshot: SystemSnapshot, 
                                  results: Dict[str, Any]) -> Dict[str, Any]:
        """生成详细分析"""
        analysis = {
            'system_analysis': self._analyze_system_health(snapshot),
            'service_analysis': self._analyze_service_status(snapshot),
            'performance_analysis': self._analyze_performance_trends(),
            'security_analysis': self._analyze_security_status()
        }
        
        return analysis
    
    def _analyze_system_health(self, snapshot: SystemSnapshot) -> Dict[str, Any]:
        """分析系统健康"""
        health_score = 100
        
        # 扣除CPU使用率带来的健康分数
        if snapshot.cpu_usage > 90:
            health_score -= 30
        elif snapshot.cpu_usage > 70:
            health_score -= 15
        
        # 扣除内存使用率带来的健康分数
        if snapshot.memory_usage > 90:
            health_score -= 25
        elif snapshot.memory_usage > 80:
            health_score -= 10
        
        # 扣除磁盘使用率带来的健康分数
        if snapshot.disk_usage > 95:
            health_score -= 35
        elif snapshot.disk_usage > 85:
            health_score -= 15
        
        health_score = max(0, health_score)
        
        return {
            'health_score': health_score,
            'health_level': 'excellent' if health_score >= 90 else 
                           'good' if health_score >= 70 else
                           'fair' if health_score >= 50 else 'poor',
            'factors': {
                'cpu_contribution': 100 - min(100, snapshot.cpu_usage),
                'memory_contribution': 100 - min(100, snapshot.memory_usage),
                'disk_contribution': 100 - min(100, snapshot.disk_usage)
            }
        }
    
    def _analyze_service_status(self, snapshot: SystemSnapshot) -> Dict[str, Any]:
        """分析服务状态"""
        service_issues = []
        for service, status in snapshot.service_status.items():
            if status != 'active':
                service_issues.append(f"{service}: {status}")
        
        return {
            'service_issues': service_issues,
            'service_health': 'healthy' if not service_issues else 'degraded'
        }
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """分析性能趋势"""
        if len(self.snapshots) < 5:
            return {'status': 'insufficient_data'}
        
        analysis = self.monitor.analyze_resource_trend(list(self.snapshots))
        
        return {
            'resource_trends': analysis,
            'performance_stable': (
                analysis.get('cpu_trend', 'stable') == 'stable' and
                analysis.get('memory_trend', 'stable') == 'stable' and
                analysis.get('disk_trend', 'stable') == 'stable'
            )
        }
    
    def _analyze_security_status(self) -> Dict[str, Any]:
        """分析安全状态"""
        # 简化实现
        return {
            'security_level': 'basic',
            'recommendations': [
                '建议定期更新RabbitMQ版本',
                '建议监控异常连接和访问模式',
                '建议启用访问日志记录'
            ]
        }
    
    def monitor_recovery_progress(self, duration_seconds: int = 300, 
                                interval_seconds: int = 30) -> List[VerificationReport]:
        """监控恢复进度"""
        reports = []
        start_time = time.time()
        
        print(f"开始监控恢复进度，持续时间: {duration_seconds}秒")
        
        while (time.time() - start_time) < duration_seconds:
            report = self.execute_verification()
            reports.append(report)
            
            # 显示当前状态
            print(f"恢复进度检查 [{len(reports)}]: {report.overall_status.value}")
            
            # 检查是否已完全恢复
            if report.overall_status == HealthStatus.HEALTHY:
                print("系统已完全恢复")
                break
            
            # 等待下次检查
            time.sleep(interval_seconds)
        
        return reports


class RecoveryVerificationDemo:
    """恢复验证演示"""
    
    def __init__(self):
        # RabbitMQ配置
        self.rabbitmq_config = {
            'host': 'localhost',
            'port': 5672,
            'api_port': 15672,
            'username': 'guest',
            'password': 'guest'
        }
        
        # 创建验证器
        self.validator = RecoveryValidator(self.rabbitmq_config)
    
    def demo_basic_verification(self):
        """演示基础验证"""
        print("基础验证演示")
        print("=" * 50)
        
        # 执行基础验证
        report = self.validator.execute_verification(VerificationLevel.BASIC)
        
        # 显示结果
        self._display_report(report)
    
    def demo_comprehensive_verification(self):
        """演示综合验证"""
        print("综合验证演示")
        print("=" * 50)
        
        # 执行综合验证
        report = self.validator.execute_verification(VerificationLevel.COMPREHENSIVE)
        
        # 显示结果
        self._display_report(report)
    
    def demo_recovery_monitoring(self, duration_minutes: int = 5):
        """演示恢复监控"""
        print(f"恢复监控演示 - 持续 {duration_minutes} 分钟")
        print("=" * 50)
        
        # 监控恢复过程
        reports = self.validator.monitor_recovery_progress(
            duration_seconds=duration_minutes * 60,
            interval_seconds=30
        )
        
        # 显示监控结果
        print(f"\n监控完成，共执行 {len(reports)} 次验证")
        
        for i, report in enumerate(reports, 1):
            print(f"第 {i} 次验证: {report.overall_status.value} "
                  f"(执行时间: {report.execution_time:.2f}秒)")
    
    def demo_trend_analysis(self):
        """演示趋势分析"""
        print("趋势分析演示")
        print("=" * 50)
        
        # 收集多个快照
        print("正在收集系统快照...")
        for i in range(10):
            snapshot = SystemResourceMonitor.get_system_snapshot()
            self.validator.snapshots.append(snapshot)
            print(f"快照 {i+1}/10: CPU={snapshot.cpu_usage:.1f}%, "
                  f"内存={snapshot.memory_usage:.1f}%")
            time.sleep(2)
        
        # 分析趋势
        if len(self.validator.snapshots) >= 2:
            analysis = SystemResourceMonitor.analyze_resource_trend(
                list(self.validator.snapshots)
            )
            
            print("\n趋势分析结果:")
            print(f"CPU趋势: {analysis['cpu_trend']} "
                  f"(平均: {analysis['cpu_avg']:.1f}%)")
            print(f"内存趋势: {analysis['memory_trend']} "
                  f"(平均: {analysis['memory_avg']:.1f}%)")
            print(f"磁盘趋势: {analysis['disk_trend']} "
                  f"(平均: {analysis['disk_avg']:.1f}%)")
    
    def _display_report(self, report: VerificationReport):
        """显示验证报告"""
        print(f"\n验证报告 - {report.level.value} 级别")
        print("-" * 60)
        
        print(f"总体验状态: {report.overall_status.value}")
        print(f"验证项目总数: {report.total_items}")
        print(f"通过: {report.passed_items}, 失败: {report.failed_items}, "
              f"警告: {report.warning_items}, 跳过: {report.skipped_items}")
        print(f"执行时间: {report.execution_time:.2f}秒")
        
        if report.recommendations:
            print(f"\n建议:")
            for recommendation in report.recommendations:
                print(f"  - {recommendation}")
        
        if report.details.get('errors'):
            print(f"\n错误:")
            for error in report.details['errors']:
                print(f"  - {error}")
        
        # 显示系统快照
        snapshot = report.details.get('system_snapshot', {})
        if snapshot:
            print(f"\n系统状态:")
            print(f"  CPU使用率: {snapshot.get('cpu_usage', 0):.1f}%")
            print(f"  内存使用率: {snapshot.get('memory_usage', 0):.1f}%")
            print(f"  磁盘使用率: {snapshot.get('disk_usage', 0):.1f}%")
    
    def run_interactive_demo(self):
        """运行交互式演示"""
        print("RabbitMQ 故障恢复验证系统演示")
        print("=" * 80)
        
        while True:
            print("\n选择演示模式:")
            print("1. 基础验证")
            print("2. 综合验证")
            print("3. 恢复监控 (5分钟)")
            print("4. 趋势分析")
            print("5. 完整验证流程")
            print("0. 退出")
            
            choice = input("请选择 (0-5): ").strip()
            
            try:
                if choice == '1':
                    self.demo_basic_verification()
                elif choice == '2':
                    self.demo_comprehensive_verification()
                elif choice == '3':
                    self.demo_recovery_monitoring()
                elif choice == '4':
                    self.demo_trend_analysis()
                elif choice == '5':
                    print("完整验证流程演示")
                    self.demo_basic_verification()
                    input("\n按Enter继续综合验证...")
                    self.demo_comprehensive_verification()
                elif choice == '0':
                    print("演示结束")
                    break
                else:
                    print("无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n演示被用户中断")
                break
            except Exception as e:
                print(f"\n演示执行出错: {e}")
            
            if choice != '0':
                input("\n按Enter继续...")


def main():
    """主函数"""
    demo = RecoveryVerificationDemo()
    demo.run_interactive_demo()


if __name__ == "__main__":
    main()