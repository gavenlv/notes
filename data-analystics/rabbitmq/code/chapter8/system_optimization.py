#!/usr/bin/env python3
"""
第8章：系统优化示例
系统级和操作系统级别的性能优化工具
"""

import os
import sys
import time
import psutil
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import socket


class OptimizerType(Enum):
    """优化器类型"""
    NETWORK = "network"
    MEMORY = "memory"
    DISK = "disk"
    CPU = "cpu"
    OS = "os"


@dataclass
class SystemConfig:
    """系统配置项"""
    parameter: str
    current_value: str
    recommended_value: str
    description: str
    optimization_impact: str


class SystemOptimizer:
    """系统优化器"""
    
    def __init__(self):
        self.optimizers = {
            OptimizerType.NETWORK: NetworkOptimizer(),
            OptimizerType.MEMORY: MemoryOptimizer(),
            OptimizerType.DISK: DiskOptimizer(),
            OptimizerType.CPU: CPUOptimizer(),
            OptimizerType.OS: OSOptimizer()
        }
    
    def analyze_current_system(self) -> Dict[str, Any]:
        """分析当前系统状态"""
        analysis = {
            'timestamp': time.time(),
            'system_info': self._get_system_info(),
            'network_config': self._get_network_config(),
            'memory_config': self._get_memory_config(),
            'disk_config': self._get_disk_config(),
            'cpu_config': self._get_cpu_config(),
            'rabbitmq_process': self._get_rabbitmq_process_info()
        }
        return analysis
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统基本信息"""
        try:
            return {
                'platform': sys.platform,
                'architecture': os.uname().machine if hasattr(os, 'uname') else 'unknown',
                'hostname': socket.gethostname(),
                'uptime': time.time() - psutil.boot_time(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_network_config(self) -> Dict[str, str]:
        """获取网络配置"""
        configs = {}
        network_params = [
            'net.core.rmem_max',
            'net.core.wmem_max',
            'net.core.netdev_max_backlog',
            'net.ipv4.tcp_rmem',
            'net.ipv4.tcp_wmem',
            'net.ipv4.tcp_keepalive_time',
            'net.ipv4.tcp_fin_timeout'
        ]
        
        for param in network_params:
            try:
                value = subprocess.check_output(['sysctl', '-n', param], 
                                              stderr=subprocess.DEVNULL).decode().strip()
                configs[param] = value
            except subprocess.CalledProcessError:
                configs[param] = 'N/A'
        
        return configs
    
    def _get_memory_config(self) -> Dict[str, Any]:
        """获取内存配置"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                'total_gb': mem.total / (1024**3),
                'available_gb': mem.available / (1024**3),
                'used_percent': mem.percent,
                'swap_total_gb': swap.total / (1024**3),
                'swap_used_percent': swap.percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_config(self) -> Dict[str, Any]:
        """获取磁盘配置"""
        try:
            disk = psutil.disk_usage('/')
            io_counters = psutil.disk_io_counters()
            return {
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3),
                'usage_percent': (disk.used / disk.total) * 100,
                'io_read_mb': io_counters.read_bytes / (1024**2) if io_counters else 0,
                'io_write_mb': io_counters.write_bytes / (1024**2) if io_counters else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_cpu_config(self) -> Dict[str, Any]:
        """获取CPU配置"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_freq_max': psutil.cpu_freq().max if psutil.cpu_freq() else 'unknown',
                'cpu_usage_current': psutil.cpu_percent(interval=1),
                'cpu_usage_per_core': psutil.cpu_percent(interval=1, percpu=True)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_rabbitmq_process_info(self) -> Dict[str, Any]:
        """获取RabbitMQ进程信息"""
        try:
            rabbitmq_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                if 'beam' in proc.info['name'].lower() or 'rabbitmq' in proc.info['name'].lower():
                    rabbitmq_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_percent': proc.info['memory_percent'],
                        'cpu_percent': proc.info['cpu_percent']
                    })
            
            return {
                'processes': rabbitmq_processes,
                'total_processes': len(rabbitmq_processes)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_optimization_recommendations(self, analysis: Dict[str, Any]) -> List[SystemConfig]:
        """生成系统优化建议"""
        recommendations = []
        
        # 网络优化建议
        network_config = analysis.get('network_config', {})
        recommendations.extend(self._get_network_recommendations(network_config))
        
        # 内存优化建议
        memory_config = analysis.get('memory_config', {})
        recommendations.extend(self._get_memory_recommendations(memory_config))
        
        # 磁盘优化建议
        disk_config = analysis.get('disk_config', {})
        recommendations.extend(self._get_disk_recommendations(disk_config))
        
        # CPU优化建议
        cpu_config = analysis.get('cpu_config', {})
        recommendations.extend(self._get_cpu_recommendations(cpu_config))
        
        return recommendations
    
    def _get_network_recommendations(self, config: Dict[str, str]) -> List[SystemConfig]:
        """获取网络优化建议"""
        recommendations = []
        
        # TCP缓冲区大小优化
        current_rmem = config.get('net.core.rmem_max', '0')
        if int(current_rmem) < 16777216:
            recommendations.append(SystemConfig(
                parameter='net.core.rmem_max',
                current_value=current_rmem,
                recommended_value='16777216',
                description='TCP接收缓冲区最大大小',
                optimization_impact='提高网络吞吐量'
            ))
        
        current_wmem = config.get('net.core.wmem_max', '0')
        if int(current_wmem) < 16777216:
            recommendations.append(SystemConfig(
                parameter='net.core.wmem_max',
                current_value=current_wmem,
                recommended_value='16777216',
                description='TCP发送缓冲区最大大小',
                optimization_impact='提高网络吞吐量'
            ))
        
        # TCP keepalive优化
        keepalive_time = config.get('net.ipv4.tcp_keepalive_time', '0')
        if int(keepalive_time) > 7200:
            recommendations.append(SystemConfig(
                parameter='net.ipv4.tcp_keepalive_time',
                current_value=keepalive_time,
                recommended_value='600',
                description='TCP keepalive时间（秒）',
                optimization_impact='更快检测死连接'
            ))
        
        return recommendations
    
    def _get_memory_recommendations(self, config: Dict[str, Any]) -> List[SystemConfig]:
        """获取内存优化建议"""
        recommendations = []
        
        if 'used_percent' in config and config['used_percent'] > 80:
            recommendations.append(SystemConfig(
                parameter='vm.swappiness',
                current_value='60',
                recommended_value='1',
                description='减少交换空间使用',
                optimization_impact='提高系统性能'
            ))
        
        return recommendations
    
    def _get_disk_recommendations(self, config: Dict[str, Any]) -> List[SystemConfig]:
        """获取磁盘优化建议"""
        recommendations = []
        
        if 'usage_percent' in config and config['usage_percent'] > 80:
            recommendations.append(SystemConfig(
                parameter='disk_usage',
                current_value=f"{config['usage_percent']:.1f}%",
                recommended_value='<80%',
                description='磁盘使用率过高',
                optimization_impact='释放磁盘空间或扩展存储'
            ))
        
        return recommendations
    
    def _get_cpu_recommendations(self, config: Dict[str, Any]) -> List[SystemConfig]:
        """获取CPU优化建议"""
        recommendations = []
        
        if 'cpu_usage_current' in config and config['cpu_usage_current'] > 80:
            recommendations.append(SystemConfig(
                parameter='cpu_governor',
                current_value='balanced',
                recommended_value='performance',
                description='CPU调速器设置为性能模式',
                optimization_impact='提高CPU响应速度'
            ))
        
        return recommendations
    
    def apply_system_optimizations(self, recommendations: List[SystemConfig]) -> Dict[str, bool]:
        """应用系统优化"""
        results = {}
        
        for recommendation in recommendations:
            try:
                if recommendation.parameter.startswith('net.') or recommendation.parameter.startswith('vm.'):
                    # 应用sysctl参数
                    cmd = ['sudo', 'sysctl', '-w', f"{recommendation.parameter}={recommendation.recommended_value}"]
                    subprocess.run(cmd, check=True, capture_output=True)
                    results[recommendation.parameter] = True
                else:
                    # 其他类型的优化（记录但不实际应用）
                    results[recommendation.parameter] = False  # 需要手动配置
                    
            except subprocess.CalledProcessError as e:
                print(f"Failed to apply {recommendation.parameter}: {e}")
                results[recommendation.parameter] = False
            except PermissionError:
                print(f"Permission denied for {recommendation.parameter}")
                results[recommendation.parameter] = False
        
        return results


class NetworkOptimizer:
    """网络优化器"""
    
    def __init__(self):
        self.tcp_params = {
            'TCP_NODELAY': '禁用Nagle算法，降低延迟',
            'SO_KEEPALIVE': '启用TCP keepalive',
            'SO_REUSEADDR': '允许地址重用',
            'SO_RCVBUF': '接收缓冲区大小',
            'SO_SNDBUF': '发送缓冲区大小'
        }
    
    def optimize_rabbitmq_connections(self, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """优化RabbitMQ连接"""
        optimizations = {
            'connection_factory_settings': {
                'requested_heartbeat': connection_config.get('heartbeat', 60),
                'connection_timeout': connection_config.get('timeout', 30000),
                'handshake_timeout': connection_config.get('handshake_timeout', 10000),
                'shutdown_timeout': connection_config.get('shutdown_timeout', 10000)
            },
            'socket_options': {
                'TCP_NODELAY': True,
                'SO_KEEPALIVE': True,
                'SO_RCVBUF': 262144,  # 256KB
                'SO_SNDBUF': 262144   # 256KB
            }
        }
        
        return optimizations
    
    def configure_load_balancing(self, node_count: int) -> Dict[str, Any]:
        """配置负载均衡"""
        if node_count <= 1:
            return {'strategy': 'single_node', 'description': '单节点无需负载均衡'}
        elif node_count <= 3:
            return {
                'strategy': 'round_robin',
                'description': '轮询负载均衡',
                'connection_string': 'amqp://node1:5672,node2:5672,node3:5672'
            }
        else:
            return {
                'strategy': 'weighted_round_robin',
                'description': '加权轮询负载均衡',
                'connection_string': 'amqp://node1:5672,node2:5672,node3:5672,node4:5672'
            }


class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self):
        self.memory_zones = ['atom', 'binary', 'code', 'ets', 'proc_heap']
    
    def analyze_memory_usage(self) -> Dict[str, Any]:
        """分析内存使用情况"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            return {
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024),
                'memory_percent': memory_percent,
                'available_system_memory_mb': psutil.virtual_memory().available / (1024 * 1024)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def optimize_heap_settings(self, message_rate: int, avg_message_size: int) -> Dict[str, Any]:
        """优化堆设置"""
        # 计算建议的堆大小
        messages_per_second = message_rate
        message_overhead = avg_message_size * 2  # 考虑索引和元数据开销
        estimated_heap_size = messages_per_second * message_overhead * 60  # 1分钟的消息量
        
        return {
            'heap_size_hard_limit': f"{estimated_heap_size // 1024 // 1024}m",
            'heap_size_soft_limit': f"{estimated_heap_size // 1024 // 1024 // 2}m",
            'fullsweep_after': 10000,
            'max_heap_size': '1GB',
            'process_limit': 100000
        }
    
    def configure_memory_limits(self, queue_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """配置内存限制"""
        total_queue_limit = 0
        for queue_config in queue_configs:
            max_length = queue_config.get('max_length', 10000)
            avg_message_size = queue_config.get('avg_message_size', 1024)
            queue_limit = max_length * avg_message_size
            total_queue_limit += queue_limit
        
        # 建议系统内存使用不超过60%
        total_system_memory = psutil.virtual_memory().total
        max_memory_usage = total_system_memory * 0.6
        
        return {
            'vm_memory_high_watermark': 0.6,
            'total_queue_memory_limit_mb': total_queue_limit // (1024 * 1024),
            'system_memory_limit_mb': max_memory_usage // (1024 * 1024),
            'per_queue_memory_limit_mb': max_memory_usage // (1024 * 1024) // len(queue_configs) if queue_configs else 0
        }


class DiskOptimizer:
    """磁盘优化器"""
    
    def __init__(self):
        self.io_schedulers = ['deadline', 'cfq', 'noop', 'mq-deadline', 'bfq']
    
    def analyze_disk_performance(self) -> Dict[str, Any]:
        """分析磁盘性能"""
        try:
            disk_usage = psutil.disk_usage('/var/lib/rabbitmq')
            disk_io = psutil.disk_io_counters()
            
            return {
                'total_space_gb': disk_usage.total / (1024**3),
                'free_space_gb': disk_usage.free / (1024**3),
                'used_percent': (disk_usage.used / disk_usage.total) * 100,
                'read_mb_per_sec': disk_io.read_bytes / (1024**2) if disk_io else 0,
                'write_mb_per_sec': disk_io.write_bytes / (1024**2) if disk_io else 0,
                'io_utilization': self._estimate_io_utilization(disk_io)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _estimate_io_utilization(self, disk_io) -> float:
        """估算I/O利用率"""
        if not disk_io:
            return 0.0
        
        # 简单的I/O利用率估算
        total_io = disk_io.read_bytes + disk_io.write_bytes
        # 这里应该基于实际时间间隔计算，简化处理
        return min(total_io / (1024 * 1024 * 1024) * 100, 100.0)  # 转换为百分比
    
    def recommend_io_scheduler(self, storage_type: str, workload: str) -> Dict[str, Any]:
        """推荐I/O调度器"""
        if storage_type.lower() == 'ssd':
            if workload == 'database':
                return {'scheduler': 'noop', 'reason': 'SSD上无寻道开销'}
            elif workload == 'messaging':
                return {'scheduler': 'deadline', 'reason': '降低延迟'}
            else:
                return {'scheduler': 'noop', 'reason': '最小开销'}
        else:
            # 传统硬盘
            if workload == 'high_throughput':
                return {'scheduler': 'deadline', 'reason': '适合高吞吐量'}
            elif workload == 'interactive':
                return {'scheduler': 'cfq', 'reason': '公平调度'}
            else:
                return {'scheduler': 'deadline', 'reason': '通用性能'}
    
    def calculate_storage_requirements(self, message_rate: int, avg_message_size: int, 
                                     retention_hours: int, replication_factor: int = 1) -> Dict[str, Any]:
        """计算存储需求"""
        # 计算每小时消息量
        hourly_messages = message_rate * 3600
        hourly_data_mb = hourly_messages * avg_message_size / (1024 * 1024)
        
        # 考虑冗余和系统开销
        total_hourly_mb = hourly_data_mb * replication_factor * 1.5  # 50%额外开销
        total_retention_mb = total_hourly_mb * retention_hours
        
        return {
            'hourly_data_mb': hourly_data_mb,
            'total_hourly_mb': total_hourly_mb,
            'retention_mb': total_retention_mb,
            'retention_gb': total_retention_mb / 1024,
            'recommendation': f"建议至少分配{retention_hours}小时的数据存储"
        }


class CPUOptimizer:
    """CPU优化器"""
    
    def analyze_cpu_performance(self) -> Dict[str, Any]:
        """分析CPU性能"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'cpu_freq_current': cpu_freq.current if cpu_freq else 'unknown',
                'cpu_freq_max': cpu_freq.max if cpu_freq else 'unknown',
                'cpu_usage_current': psutil.cpu_percent(interval=1),
                'cpu_usage_per_core': psutil.cpu_percent(interval=1, percpu=True)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def configure_cpu_affinity(self, process_name: str = 'beam') -> Dict[str, Any]:
        """配置CPU亲和性"""
        try:
            # 查找RabbitMQ进程
            rabbitmq_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_affinity']):
                if process_name in proc.info['name'].lower():
                    rabbitmq_processes.append({
                        'pid': proc.info['pid'],
                        'current_affinity': proc.info['cpu_affinity']
                    })
            
            return {
                'processes': rabbitmq_processes,
                'total_processes': len(rabbitmq_processes)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def optimize_erlang_scheduler(self, cpu_count: int) -> Dict[str, Any]:
        """优化Erlang调度器"""
        # Erlang调度器建议配置
        if cpu_count <= 4:
            schedulers = cpu_count
        elif cpu_count <= 8:
            schedulers = cpu_count // 2
        else:
            schedulers = cpu_count // 4
        
        return {
            '+S': f"{schedulers}:{cpu_count}",
            'description': f'Erlang调度器设置：{schedulers}个调度器，{cpu_count}个CPU',
            'expected_improvement': '提高CPU利用率'
        }


class OSOptimizer:
    """操作系统优化器"""
    
    def __init__(self):
        self.optimization_params = {
            'fs.file-max': 2097152,           # 最大文件描述符数
            'fs.nr_open': 2097152,            # 最大打开文件数
            'vm.swappiness': 1,               # 减少交换空间使用
            'vm.dirty_ratio': 15,             # 脏页比例
            'vm.dirty_background_ratio': 5,   # 后台刷新阈值
            'kernel.sem': '250 32000 100 128', # 信号量设置
            'kernel.shmmax': 17179869184      # 最大共享内存段
        }
    
    def apply_os_optimizations(self) -> Dict[str, bool]:
        """应用操作系统优化"""
        results = {}
        
        for param, value in self.optimization_params.items():
            try:
                cmd = ['sudo', 'sysctl', '-w', f"{param}={value}"]
                subprocess.run(cmd, check=True, capture_output=True)
                results[param] = True
            except (subprocess.CalledProcessError, PermissionError):
                results[param] = False
        
        return results
    
    def configure_limits(self) -> Dict[str, str]:
        """配置系统限制"""
        limits = {
            'rabbitmq soft nofile': '65536',
            'rabbitmq hard nofile': '65536',
            'rabbitmq soft nproc': '32768',
            'rabbitmq hard nproc': '32768'
        }
        
        return limits


class PerformanceDemo:
    """性能优化演示"""
    
    def __init__(self):
        self.optimizer = SystemOptimizer()
    
    def demonstrate_system_analysis(self):
        """演示系统分析"""
        print("=== RabbitMQ 系统优化分析 ===")
        print()
        
        # 分析当前系统状态
        analysis = self.optimizer.analyze_current_system()
        
        print("📊 系统信息:")
        system_info = analysis.get('system_info', {})
        print(f"  平台: {system_info.get('platform', 'unknown')}")
        print(f"  CPU核心数: {system_info.get('cpu_count', 'unknown')}")
        print(f"  总内存: {system_info.get('memory_total', 0) / (1024**3):.1f} GB")
        print(f"  总磁盘: {system_info.get('disk_total', 0) / (1024**3):.1f} GB")
        print()
        
        # 显示内存配置
        memory_config = analysis.get('memory_config', {})
        print("💾 内存配置:")
        print(f"  总内存: {memory_config.get('total_gb', 0):.1f} GB")
        print(f"  已用内存: {memory_config.get('used_percent', 0):.1f}%")
        print(f"  交换空间使用: {memory_config.get('swap_used_percent', 0):.1f}%")
        print()
        
        # 显示磁盘配置
        disk_config = analysis.get('disk_config', {})
        print("💽 磁盘配置:")
        print(f"  总空间: {disk_config.get('total_gb', 0):.1f} GB")
        print(f"  已用空间: {disk_config.get('used_gb', 0):.1f} GB ({disk_config.get('usage_percent', 0):.1f}%)")
        print(f"  读取速率: {disk_config.get('io_read_mb', 0):.1f} MB")
        print(f"  写入速率: {disk_config.get('io_write_mb', 0):.1f} MB")
        print()
        
        # 显示RabbitMQ进程信息
        rabbitmq_info = analysis.get('rabbitmq_process', {})
        print("🐰 RabbitMQ进程:")
        print(f"  进程数量: {rabbitmq_info.get('total_processes', 0)}")
        for process in rabbitmq_info.get('processes', []):
            print(f"    PID {process['pid']}: 内存 {process['memory_percent']:.1f}%, CPU {process['cpu_percent']:.1f}%")
        print()
        
        return analysis
    
    def demonstrate_optimization_recommendations(self, analysis: Dict[str, Any]):
        """演示优化建议"""
        print("💡 系统优化建议:")
        print()
        
        recommendations = self.optimizer.generate_optimization_recommendations(analysis)
        
        if not recommendations:
            print("  系统配置良好，无需额外优化")
            return
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. 参数: {rec.parameter}")
            print(f"   当前值: {rec.current_value}")
            print(f"   建议值: {rec.recommended_value}")
            print(f"   说明: {rec.description}")
            print(f"   影响: {rec.optimization_impact}")
            print()
    
    def demonstrate_network_optimization(self):
        """演示网络优化"""
        print("🌐 网络优化示例:")
        print()
        
        network_optimizer = NetworkOptimizer()
        
        # 连接优化示例
        connection_config = {
            'heartbeat': 30,
            'timeout': 20000,
            'handshake_timeout': 8000
        }
        
        optimizations = network_optimizer.optimize_rabbitmq_connections(connection_config)
        
        print("连接工厂设置:")
        for key, value in optimizations['connection_factory_settings'].items():
            print(f"  {key}: {value}")
        print()
        
        print("套接字选项:")
        for key, value in optimizations['socket_options'].items():
            print(f"  {key}: {value}")
        print()
        
        # 负载均衡示例
        lb_config = network_optimizer.configure_load_balancing(3)
        print("负载均衡配置:")
        print(f"  策略: {lb_config['strategy']}")
        print(f"  描述: {lb_config['description']}")
        print(f"  连接字符串: {lb_config['connection_string']}")
        print()
    
    def demonstrate_memory_optimization(self):
        """演示内存优化"""
        print("💾 内存优化示例:")
        print()
        
        memory_optimizer = MemoryOptimizer()
        
        # 内存使用分析
        mem_analysis = memory_optimizer.analyze_memory_usage()
        print("当前内存使用:")
        for key, value in mem_analysis.items():
            print(f"  {key}: {value}")
        print()
        
        # 堆设置优化
        heap_settings = memory_optimizer.optimize_heap_settings(
            message_rate=1000,  # 每秒1000条消息
            avg_message_size=1024  # 1KB消息
        )
        print("建议的堆设置:")
        for key, value in heap_settings.items():
            print(f"  {key}: {value}")
        print()
        
        # 内存限制配置
        queue_configs = [
            {'name': 'orders', 'max_length': 10000, 'avg_message_size': 1024},
            {'name': 'notifications', 'max_length': 5000, 'avg_message_size': 512}
        ]
        
        memory_limits = memory_optimizer.configure_memory_limits(queue_configs)
        print("内存限制配置:")
        for key, value in memory_limits.items():
            print(f"  {key}: {value}")
        print()
    
    def demonstrate_disk_optimization(self):
        """演示磁盘优化"""
        print("💽 磁盘优化示例:")
        print()
        
        disk_optimizer = DiskOptimizer()
        
        # 磁盘性能分析
        disk_analysis = disk_optimizer.analyze_disk_performance()
        print("当前磁盘性能:")
        for key, value in disk_analysis.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.1f}")
            else:
                print(f"  {key}: {value}")
        print()
        
        # I/O调度器推荐
        scheduler_rec = disk_optimizer.recommend_io_scheduler('ssd', 'messaging')
        print("I/O调度器推荐:")
        print(f"  调度器: {scheduler_rec['scheduler']}")
        print(f"  原因: {scheduler_rec['reason']}")
        print()
        
        # 存储需求计算
        storage_req = disk_optimizer.calculate_storage_requirements(
            message_rate=1000,
            avg_message_size=1024,
            retention_hours=24,
            replication_factor=2
        )
        print("存储需求计算:")
        for key, value in storage_req.items():
            print(f"  {key}: {value}")
        print()
    
    def demonstrate_cpu_optimization(self):
        """演示CPU优化"""
        print("💻 CPU优化示例:")
        print()
        
        cpu_optimizer = CPUOptimizer()
        
        # CPU性能分析
        cpu_analysis = cpu_optimizer.analyze_cpu_performance()
        print("当前CPU性能:")
        for key, value in cpu_analysis.items():
            print(f"  {key}: {value}")
        print()
        
        # CPU亲和性配置
        affinity_config = cpu_optimizer.configure_cpu_affinity()
        print("CPU亲和性配置:")
        print(f"  进程数量: {affinity_config.get('total_processes', 0)}")
        for process in affinity_config.get('processes', []):
            print(f"    PID {process['pid']}: 亲和性 {process['current_affinity']}")
        print()
        
        # Erlang调度器优化
        scheduler_config = cpu_optimizer.optimize_erlang_scheduler(
            cpu_count=cpu_analysis.get('cpu_count', 4)
        )
        print("Erlang调度器优化:")
        for key, value in scheduler_config.items():
            print(f"  {key}: {value}")
        print()
    
    def demonstrate_os_optimization(self):
        """演示操作系统优化"""
        print("⚙️ 操作系统优化示例:")
        print()
        
        os_optimizer = OSOptimizer()
        
        # 系统优化参数
        print("系统优化参数:")
        for param, value in os_optimizer.optimization_params.items():
            print(f"  {param} = {value}")
        print()
        
        # 系统限制配置
        limits = os_optimizer.configure_limits()
        print("系统限制配置:")
        for limit, value in limits.items():
            print(f"  {limit} {value}")
        print()
        
        # 应用优化的模拟结果
        print("应用优化结果（模拟）:")
        for param in os_optimizer.optimization_params.keys():
            print(f"  {param}: 应用成功")
        print()


if __name__ == "__main__":
    # 运行性能优化演示
    demo = PerformanceDemo()
    
    print("🔧 RabbitMQ 性能优化系统")
    print("=" * 50)
    print()
    
    # 1. 系统分析
    analysis = demo.demonstrate_system_analysis()
    
    # 2. 优化建议
    demo.demonstrate_optimization_recommendations(analysis)
    
    # 3. 各类优化演示
    demo.demonstrate_network_optimization()
    demo.demonstrate_memory_optimization()
    demo.demonstrate_disk_optimization()
    demo.demonstrate_cpu_optimization()
    demo.demonstrate_os_optimization()
    
    print("✅ 系统优化演示完成")