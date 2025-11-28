"""
健康检查与故障诊断模块
Chapter 10: 故障处理与恢复

提供系统健康检查、故障诊断、性能监控和异常检测等功能
"""

import os
import sys
import time
import json
import socket
import platform
import subprocess
import threading
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import psutil
import requests


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """组件类型枚举"""
    RABBITMQ_SERVICE = "rabbitmq_service"
    RABBITMQ_API = "rabbitmq_api"
    RABBITMQ_QUEUES = "rabbitmq_queues"
    SYSTEM_CPU = "system_cpu"
    SYSTEM_MEMORY = "system_memory"
    SYSTEM_DISK = "system_disk"
    SYSTEM_NETWORK = "system_network"
    RABBITMQ_NODES = "rabbitmq_nodes"
    CLUSTER_STATUS = "cluster_status"


@dataclass
class HealthMetric:
    """健康指标"""
    component: ComponentType
    status: HealthStatus
    value: Union[float, int, str]
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    description: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class HealthReport:
    """健康报告"""
    overall_status: HealthStatus
    metrics: List[HealthMetric]
    issues: List[str]
    warnings: List[str]
    timestamp: datetime
    duration_seconds: float = 0.0


class RabbitMQHealthChecker:
    """RabbitMQ健康检查器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5672)
        self.api_port = config.get('api_port', 15672)
        self.username = config.get('username', 'guest')
        self.password = config.get('password', 'guest')
        self.timeout = config.get('timeout', 10)
    
    def check_service_health(self) -> HealthMetric:
        """检查RabbitMQ服务健康状态"""
        try:
            import pika
            
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2,
                timeout=self.timeout
            )
            
            start_time = time.time()
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # 测试基本操作
            channel.queue_declare(queue='health_check_temp', auto_delete=True)
            channel.queue_delete(queue='health_check_temp')
            
            connection.close()
            
            response_time = time.time() - start_time
            
            status = HealthStatus.HEALTHY
            if response_time > 5.0:
                status = HealthStatus.WARNING
            elif response_time > 10.0:
                status = HealthStatus.CRITICAL
            
            return HealthMetric(
                component=ComponentType.RABBITMQ_SERVICE,
                status=status,
                value=response_time,
                threshold_warning=5.0,
                threshold_critical=10.0,
                description=f"RabbitMQ服务响应时间: {response_time:.2f}秒"
            )
            
        except Exception as e:
            return HealthMetric(
                component=ComponentType.RABBITMQ_SERVICE,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"RabbitMQ服务连接失败: {str(e)}"
            )
    
    def check_api_health(self) -> HealthMetric:
        """检查RabbitMQ API健康状态"""
        try:
            url = f"http://{self.host}:{self.api_port}/api/overview"
            auth = (self.username, self.password)
            
            start_time = time.time()
            response = requests.get(url, auth=auth, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查API响应数据
                management_version = data.get('management_version', 'unknown')
                rabbitmq_version = data.get('rabbitmq_version', 'unknown')
                
                status = HealthStatus.HEALTHY
                if response_time > 3.0:
                    status = HealthStatus.WARNING
                elif response_time > 5.0:
                    status = HealthStatus.CRITICAL
                
                description = f"API响应正常 (v{management_version}, RabbitMQ {rabbitmq_version})"
                
                return HealthMetric(
                    component=ComponentType.RABBITMQ_API,
                    status=status,
                    value=response_time,
                    threshold_warning=3.0,
                    threshold_critical=5.0,
                    description=description
                )
            else:
                return HealthMetric(
                    component=ComponentType.RABBITMQ_API,
                    status=HealthStatus.CRITICAL,
                    value=response.status_code,
                    description=f"API返回状态码: {response.status_code}"
                )
                
        except Exception as e:
            return HealthMetric(
                component=ComponentType.RABBITMQ_API,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"API健康检查失败: {str(e)}"
            )
    
    def check_queue_health(self) -> HealthMetric:
        """检查队列健康状态"""
        try:
            url = f"http://{self.host}:{self.api_port}/api/queues"
            auth = (self.username, self.password)
            
            response = requests.get(url, auth=auth, timeout=self.timeout)
            
            if response.status_code == 200:
                queues = response.json()
                
                total_messages = sum(q.get('messages', 0) for q in queues)
                total_ready = sum(q.get('messages_ready', 0) for q in queues)
                total_unacked = sum(q.get('messages_unacknowledged', 0) for q in queues)
                
                # 评估队列状态
                status = HealthStatus.HEALTHY
                if total_unacked > 1000:
                    status = HealthStatus.WARNING
                elif total_unacked > 5000:
                    status = HealthStatus.CRITICAL
                
                description = f"队列数: {len(queues)}, 总消息: {total_messages}, " \
                            f"未确认: {total_unacked}, 就绪: {total_ready}"
                
                return HealthMetric(
                    component=ComponentType.RABBITMQ_QUEUES,
                    status=status,
                    value=total_unacked,
                    threshold_warning=1000,
                    threshold_critical=5000,
                    description=description
                )
            else:
                return HealthMetric(
                    component=ComponentType.RABBITMQ_QUEUES,
                    status=HealthStatus.CRITICAL,
                    value=response.status_code,
                    description=f"队列API返回状态码: {response.status_code}"
                )
                
        except Exception as e:
            return HealthMetric(
                component=ComponentType.RABBITMQ_QUEUES,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"队列健康检查失败: {str(e)}"
            )
    
    def check_cluster_status(self) -> HealthMetric:
        """检查集群状态"""
        try:
            url = f"http://{self.host}:{self.api_port}/api/nodes"
            auth = (self.username, self.password)
            
            response = requests.get(url, auth=auth, timeout=self.timeout)
            
            if response.status_code == 200:
                nodes = response.json()
                
                running_nodes = sum(1 for node in nodes if node.get('running', False))
                total_nodes = len(nodes)
                
                status = HealthStatus.HEALTHY
                if running_nodes < total_nodes:
                    if running_nodes / total_nodes > 0.7:
                        status = HealthStatus.WARNING
                    else:
                        status = HealthStatus.CRITICAL
                
                description = f"集群节点状态: {running_nodes}/{total_nodes} 正常运行"
                
                return HealthMetric(
                    component=ComponentType.CLUSTER_STATUS,
                    status=status,
                    value=running_nodes / total_nodes,
                    threshold_warning=0.7,
                    threshold_critical=0.5,
                    description=description
                )
            else:
                return HealthMetric(
                    component=ComponentType.CLUSTER_STATUS,
                    status=HealthStatus.CRITICAL,
                    value=response.status_code,
                    description=f"集群API返回状态码: {response.status_code}"
                )
                
        except Exception as e:
            return HealthMetric(
                component=ComponentType.CLUSTER_STATUS,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"集群状态检查失败: {str(e)}"
            )


class SystemHealthChecker:
    """系统健康检查器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cpu_threshold_warning = self.config.get('cpu_threshold_warning', 80.0)
        self.cpu_threshold_critical = self.config.get('cpu_threshold_critical', 95.0)
        self.memory_threshold_warning = self.config.get('memory_threshold_warning', 80.0)
        self.memory_threshold_critical = self.config.get('memory_threshold_critical', 95.0)
        self.disk_threshold_warning = self.config.get('disk_threshold_warning', 85.0)
        self.disk_threshold_critical = self.config.get('disk_threshold_critical', 95.0)
    
    def check_cpu_health(self) -> HealthMetric:
        """检查CPU健康状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            status = HealthStatus.HEALTHY
            if cpu_percent > self.cpu_threshold_critical:
                status = HealthStatus.CRITICAL
            elif cpu_percent > self.cpu_threshold_warning:
                status = HealthStatus.WARNING
            
            # 获取CPU信息
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            description = f"CPU使用率: {cpu_percent:.1f}%, 核心数: {cpu_count}, " \
                        f"负载: {load_avg[0]:.2f}"
            
            return HealthMetric(
                component=ComponentType.SYSTEM_CPU,
                status=status,
                value=cpu_percent,
                threshold_warning=self.cpu_threshold_warning,
                threshold_critical=self.cpu_threshold_critical,
                description=description
            )
            
        except Exception as e:
            return HealthMetric(
                component=ComponentType.SYSTEM_CPU,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"CPU健康检查失败: {str(e)}"
            )
    
    def check_memory_health(self) -> HealthMetric:
        """检查内存健康状态"""
        try:
            memory = psutil.virtual_memory()
            
            status = HealthStatus.HEALTHY
            if memory.percent > self.memory_threshold_critical:
                status = HealthStatus.CRITICAL
            elif memory.percent > self.memory_threshold_warning:
                status = HealthStatus.WARNING
            
            description = f"内存使用率: {memory.percent:.1f}%, " \
                        f"可用: {memory.available / (1024**3):.2f}GB, " \
                        f"总计: {memory.total / (1024**3):.2f}GB"
            
            return HealthMetric(
                component=ComponentType.SYSTEM_MEMORY,
                status=status,
                value=memory.percent,
                threshold_warning=self.memory_threshold_warning,
                threshold_critical=self.memory_threshold_critical,
                description=description
            )
            
        except Exception as e:
            return HealthMetric(
                component=ComponentType.SYSTEM_MEMORY,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"内存健康检查失败: {str(e)}"
            )
    
    def check_disk_health(self, path: str = '/') -> HealthMetric:
        """检查磁盘健康状态"""
        try:
            disk = psutil.disk_usage(path)
            disk_percent = (disk.used / disk.total) * 100
            
            status = HealthStatus.HEALTHY
            if disk_percent > self.disk_threshold_critical:
                status = HealthStatus.CRITICAL
            elif disk_percent > self.disk_threshold_warning:
                status = HealthStatus.WARNING
            
            description = f"磁盘使用率: {disk_percent:.1f}%, " \
                        f"已用: {disk.used / (1024**3):.2f}GB, " \
                        f"总计: {disk.total / (1024**3):.2f}GB"
            
            return HealthMetric(
                component=ComponentType.SYSTEM_DISK,
                status=status,
                value=disk_percent,
                threshold_warning=self.disk_threshold_warning,
                threshold_critical=self.disk_threshold_critical,
                description=description
            )
            
        except Exception as e:
            return HealthMetric(
                component=ComponentType.SYSTEM_DISK,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"磁盘健康检查失败: {str(e)}"
            )
    
    def check_network_health(self) -> HealthMetric:
        """检查网络健康状态"""
        try:
            network = psutil.net_io_counters()
            
            # 计算网络速率（需要两次测量）
            time.sleep(1)
            network2 = psutil.net_io_counters()
            
            bytes_sent_rate = (network2.bytes_sent - network.bytes_sent)
            bytes_recv_rate = (network2.bytes_recv - network.bytes_recv)
            
            # 评估网络负载
            total_rate = bytes_sent_rate + bytes_recv_rate
            
            status = HealthStatus.HEALTHY
            if total_rate > 100 * 1024 * 1024:  # 100MB/s
                status = HealthStatus.WARNING
            elif total_rate > 500 * 1024 * 1024:  # 500MB/s
                status = HealthStatus.CRITICAL
            
            description = f"网络发送: {bytes_sent_rate / 1024:.1f}KB/s, " \
                        f"接收: {bytes_recv_rate / 1024:.1f}KB/s"
            
            return HealthMetric(
                component=ComponentType.SYSTEM_NETWORK,
                status=status,
                value=total_rate / 1024 / 1024,  # MB/s
                threshold_warning=100,
                threshold_critical=500,
                description=description
            )
            
        except Exception as e:
            return HealthMetric(
                component=ComponentType.SYSTEM_NETWORK,
                status=HealthStatus.CRITICAL,
                value=str(e),
                description=f"网络健康检查失败: {str(e)}"
            )


class NetworkDiagnostics:
    """网络诊断工具"""
    
    @staticmethod
    def ping_host(host: str, count: int = 4) -> Dict[str, Any]:
        """Ping主机测试"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', str(count), host]
            else:
                cmd = ['ping', '-c', str(count), host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0
            
            # 解析输出
            output_lines = result.stdout.split('\n')
            successful_pings = 0
            times = []
            
            for line in output_lines:
                if 'time=' in line:
                    # 提取时间
                    import re
                    time_match = re.search(r'time[<=]([\d.]+)', line)
                    if time_match:
                        times.append(float(time_match.group(1)))
                elif 'Reply from' in line or 'bytes from' in line:
                    successful_pings += 1
            
            avg_time = sum(times) / len(times) if times else 0
            
            return {
                'success': success,
                'successful_pings': successful_pings,
                'total_pings': count,
                'avg_time_ms': avg_time,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'successful_pings': 0,
                'total_pings': count,
                'avg_time_ms': 0
            }
    
    @staticmethod
    def check_port_connectivity(host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
        """检查端口连通性"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = time.time()
            result = sock.connect_ex((host, port))
            response_time = (time.time() - start_time) * 1000
            
            sock.close()
            
            return {
                'success': result == 0,
                'response_time_ms': response_time,
                'port': port,
                'host': host
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'port': port,
                'host': host,
                'response_time_ms': 0
            }
    
    @staticmethod
    def dns_resolution_test(hostname: str) -> Dict[str, Any]:
        """DNS解析测试"""
        try:
            ip_address = socket.gethostbyname(hostname)
            return {
                'success': True,
                'hostname': hostname,
                'ip_address': ip_address
            }
        except Exception as e:
            return {
                'success': False,
                'hostname': hostname,
                'error': str(e)
            }


class ComprehensiveHealthChecker:
    """综合健康检查器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rabbitmq_config = config.get('rabbitmq', {})
        self.system_config = config.get('system', {})
        
        self.rabbitmq_checker = RabbitMQHealthChecker(self.rabbitmq_config)
        self.system_checker = SystemHealthChecker(self.system_config)
        self.network_diagnostics = NetworkDiagnostics()
    
    def run_comprehensive_health_check(self) -> HealthReport:
        """运行综合健康检查"""
        start_time = time.time()
        metrics = []
        issues = []
        warnings = []
        
        try:
            # 系统健康检查
            metrics.extend([
                self.system_checker.check_cpu_health(),
                self.system_checker.check_memory_health(),
                self.system_checker.check_disk_health(),
                self.system_checker.check_network_health()
            ])
            
            # RabbitMQ健康检查
            metrics.extend([
                self.rabbitmq_checker.check_service_health(),
                self.rabbitmq_checker.check_api_health(),
                self.rabbitmq_checker.check_queue_health(),
                self.rabbitmq_checker.check_cluster_status()
            ])
            
            # 收集问题和建议
            for metric in metrics:
                if metric.status == HealthStatus.CRITICAL:
                    issues.append(f"{metric.component.value}: {metric.description}")
                elif metric.status == HealthStatus.WARNING:
                    warnings.append(f"{metric.component.value}: {metric.description}")
            
            # 评估整体状态
            overall_status = self._evaluate_overall_status(metrics)
            
            # 计算检查耗时
            duration = time.time() - start_time
            
            return HealthReport(
                overall_status=overall_status,
                metrics=metrics,
                issues=issues,
                warnings=warnings,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
            
        except Exception as e:
            # 发生异常时的处理
            duration = time.time() - start_time
            
            return HealthReport(
                overall_status=HealthStatus.CRITICAL,
                metrics=metrics,
                issues=[f"健康检查执行失败: {str(e)}"],
                warnings=warnings,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
    
    def _evaluate_overall_status(self, metrics: List[HealthMetric]) -> HealthStatus:
        """评估整体健康状态"""
        critical_count = 0
        warning_count = 0
        healthy_count = 0
        
        for metric in metrics:
            if metric.status == HealthStatus.CRITICAL:
                critical_count += 1
            elif metric.status == HealthStatus.WARNING:
                warning_count += 1
            elif metric.status == HealthStatus.HEALTHY:
                healthy_count += 1
        
        total_metrics = len(metrics)
        
        if critical_count > 0:
            if critical_count / total_metrics > 0.5:
                return HealthStatus.CRITICAL
            else:
                return HealthStatus.WARNING
        elif warning_count > 0:
            if warning_count / total_metrics > 0.7:
                return HealthStatus.WARNING
            else:
                return HealthStatus.HEALTHY
        else:
            return HealthStatus.HEALTHY
    
    def run_network_diagnostics(self) -> Dict[str, Any]:
        """运行网络诊断"""
        host = self.rabbitmq_config.get('host', 'localhost')
        
        diagnostics = {
            'host': host,
            'ping_test': self.network_diagnostics.ping_host(host),
            'port_tests': {
                'amqp_port': self.network_diagnostics.check_port_connectivity(
                    host, self.rabbitmq_config.get('port', 5672)
                ),
                'api_port': self.network_diagnostics.check_port_connectivity(
                    host, self.rabbitmq_config.get('api_port', 15672)
                )
            },
            'dns_resolution': self.network_diagnostics.dns_resolution_test(host),
            'timestamp': datetime.now().isoformat()
        }
        
        return diagnostics
    
    def generate_health_report(self, format_type: str = 'dict') -> Union[Dict, str]:
        """生成健康报告"""
        report = self.run_comprehensive_health_check()
        
        if format_type == 'dict':
            return asdict(report)
        elif format_type == 'json':
            return json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str)
        elif format_type == 'text':
            return self._format_report_as_text(report)
        else:
            raise ValueError(f"不支持的报告格式: {format_type}")
    
    def _format_report_as_text(self, report: HealthReport) -> str:
        """格式化报告为文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("RabbitMQ 健康检查报告")
        lines.append("=" * 60)
        lines.append(f"检查时间: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"总耗时: {report.duration_seconds:.2f}秒")
        lines.append(f"整体状态: {report.overall_status.value.upper()}")
        lines.append("")
        
        # 详细指标
        lines.append("详细指标:")
        lines.append("-" * 40)
        
        for metric in report.metrics:
            status_symbol = {
                HealthStatus.HEALTHY: "✓",
                HealthStatus.WARNING: "⚠",
                HealthStatus.CRITICAL: "✗",
                HealthStatus.UNKNOWN: "?"
            }[metric.status]
            
            lines.append(f"{status_symbol} {metric.component.value}: {metric.description}")
        
        lines.append("")
        
        # 问题和建议
        if report.issues:
            lines.append("关键问题:")
            lines.append("-" * 20)
            for issue in report.issues:
                lines.append(f"✗ {issue}")
            lines.append("")
        
        if report.warnings:
            lines.append("警告:")
            lines.append("-" * 10)
            for warning in report.warnings:
                lines.append(f"⚠ {warning}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


class HealthMonitor:
    """健康监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.checker = ComprehensiveHealthChecker(config)
        self.running = False
        self.monitor_thread = None
        self.callbacks = []
        
        # 监控配置
        self.check_interval = config.get('check_interval', 60)  # 秒
        self.max_history = config.get('max_history', 100)
        
        # 历史记录
        self.health_history = []
    
    def add_callback(self, callback: callable):
        """添加健康状态变化回调"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """开始健康监控"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            print("健康监控已启动")
    
    def stop_monitoring(self):
        """停止健康监控"""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            print("健康监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 运行健康检查
                report = self.checker.run_comprehensive_health_check()
                
                # 保存历史记录
                self._save_health_record(report)
                
                # 检查状态变化并触发回调
                self._check_status_changes(report)
                
                # 等待下一次检查
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"健康监控循环异常: {e}")
                time.sleep(5)
    
    def _save_health_record(self, report: HealthReport):
        """保存健康记录"""
        self.health_history.append({
            'timestamp': report.timestamp.isoformat(),
            'overall_status': report.overall_status.value,
            'issues_count': len(report.issues),
            'warnings_count': len(report.warnings),
            'duration': report.duration_seconds
        })
        
        # 限制历史记录数量
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history:]
    
    def _check_status_changes(self, report: HealthReport):
        """检查状态变化并触发回调"""
        if not self.callbacks:
            return
        
        # 获取上一次状态
        last_status = None
        if len(self.health_history) >= 2:
            last_status = self.health_history[-2]['overall_status']
        
        current_status = report.overall_status.value
        
        # 如果状态发生变化，触发回调
        if last_status and last_status != current_status:
            for callback in self.callbacks:
                try:
                    callback(last_status, current_status, report)
                except Exception as e:
                    print(f"健康状态回调执行失败: {e}")
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """获取健康趋势"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_history = [
            record for record in self.health_history
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]
        
        if not recent_history:
            return {"message": "没有足够的健康历史数据"}
        
        # 计算趋势
        status_counts = defaultdict(int)
        avg_duration = sum(r['duration'] for r in recent_history) / len(recent_history)
        avg_issues = sum(r['issues_count'] for r in recent_history) / len(recent_history)
        avg_warnings = sum(r['warnings_count'] for r in recent_history) / len(recent_history)
        
        for record in recent_history:
            status_counts[record['overall_status']] += 1
        
        # 状态分布百分比
        total_records = len(recent_history)
        status_distribution = {
            status: (count / total_records) * 100
            for status, count in status_counts.items()
        }
        
        return {
            'time_period_hours': hours,
            'total_checks': total_records,
            'status_distribution': status_distribution,
            'avg_duration_seconds': avg_duration,
            'avg_issues_per_check': avg_issues,
            'avg_warnings_per_check': avg_warnings,
            'recent_records': recent_history[-10:] if len(recent_history) > 10 else recent_history
        }


class HealthCheckDemo:
    """健康检查演示"""
    
    def __init__(self):
        # 示例配置
        self.config = {
            'rabbitmq': {
                'host': 'localhost',
                'port': 5672,
                'api_port': 15672,
                'username': 'guest',
                'password': 'guest',
                'timeout': 10
            },
            'system': {
                'cpu_threshold_warning': 80.0,
                'cpu_threshold_critical': 95.0,
                'memory_threshold_warning': 80.0,
                'memory_threshold_critical': 95.0,
                'disk_threshold_warning': 85.0,
                'disk_threshold_critical': 95.0
            },
            'check_interval': 30,
            'max_history': 50
        }
        
        self.checker = None
        self.monitor = None
    
    def demo_basic_health_check(self):
        """演示基础健康检查"""
        print("=" * 50)
        print("基础健康检查演示")
        print("=" * 50)
        
        # 创建健康检查器
        self.checker = ComprehensiveHealthChecker(self.config)
        
        # 运行综合健康检查
        print("运行综合健康检查...")
        report = self.checker.run_comprehensive_health_check()
        
        # 显示文本报告
        print(self.checker.generate_health_report('text'))
        
        return report
    
    def demo_network_diagnostics(self):
        """演示网络诊断"""
        print("=" * 50)
        print("网络诊断演示")
        print("=" * 50)
        
        # 运行网络诊断
        print("运行网络诊断...")
        diagnostics = self.checker.run_network_diagnostics()
        
        print(json.dumps(diagnostics, indent=2, ensure_ascii=False))
        
        return diagnostics
    
    def demo_real_time_monitoring(self):
        """演示实时监控"""
        print("=" * 50)
        print("实时监控演示")
        print("=" * 50)
        
        # 创建健康监控器
        self.monitor = HealthMonitor(self.config)
        
        # 添加状态变化回调
        def health_status_callback(old_status, new_status, report):
            print(f"健康状态变化: {old_status} -> {new_status}")
            print(f"检查耗时: {report.duration_seconds:.2f}秒")
            print(f"问题数: {len(report.issues)}, 警告数: {len(report.warnings)}")
            print("-" * 30)
        
        self.monitor.add_callback(health_status_callback)
        
        # 启动监控
        self.monitor.start_monitoring()
        
        try:
            print("开始实时监控，持续60秒...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("收到中断信号...")
        finally:
            self.monitor.stop_monitoring()
            
            # 显示健康趋势
            print("=" * 30)
            print("健康趋势分析")
            print("=" * 30)
            
            trends = self.monitor.get_health_trends(hours=1)
            print(json.dumps(trends, indent=2, ensure_ascii=False, default=str))
    
    def demo_stress_test(self):
        """演示压力测试"""
        print("=" * 50)
        print("压力测试演示")
        print("=" * 50)
        
        results = []
        
        print("运行20次连续健康检查...")
        for i in range(20):
            report = self.checker.run_comprehensive_health_check()
            
            results.append({
                'check_number': i + 1,
                'overall_status': report.overall_status.value,
                'duration': report.duration_seconds,
                'issues_count': len(report.issues),
                'warnings_count': len(report.warnings)
            })
            
            print(f"检查 {i+1:2d}: 状态={report.overall_status.value:8s}, "
                  f"耗时={report.duration_seconds:.2f}s, "
                  f"问题={len(report.issues):2d}, 警告={len(report.warnings):2d}")
        
        # 统计分析
        total_checks = len(results)
        avg_duration = sum(r['duration'] for r in results) / total_checks
        healthy_count = sum(1 for r in results if r['overall_status'] == 'healthy')
        warning_count = sum(1 for r in results if r['overall_status'] == 'warning')
        critical_count = sum(1 for r in results if r['overall_status'] == 'critical')
        
        print("\n" + "=" * 30)
        print("压力测试结果统计")
        print("=" * 30)
        print(f"总检查次数: {total_checks}")
        print(f"平均耗时: {avg_duration:.2f}秒")
        print(f"健康状态: {healthy_count} ({healthy_count/total_checks*100:.1f}%)")
        print(f"警告状态: {warning_count} ({warning_count/total_checks*100:.1f}%)")
        print(f"严重状态: {critical_count} ({critical_count/total_checks*100:.1f}%)")


def main():
    """主函数"""
    demo = HealthCheckDemo()
    
    try:
        # 基础健康检查
        demo.demo_basic_health_check()
        
        # 网络诊断
        demo.demo_network_diagnostics()
        
        # 实时监控（可选）
        response = input("\n是否运行实时监控演示？(y/N): ").strip().lower()
        if response == 'y':
            demo.demo_real_time_monitoring()
        
        # 压力测试（可选）
        response = input("\n是否运行压力测试演示？(y/N): ").strip().lower()
        if response == 'y':
            demo.demo_stress_test()
            
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示执行出错: {e}")


if __name__ == "__main__":
    main()