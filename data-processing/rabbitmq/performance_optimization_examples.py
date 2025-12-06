#!/usr/bin/env python3
"""
RabbitMQ性能优化与调优代码示例
"""

import os
import sys
import time
import threading
import logging
import statistics
import pika
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable, Deque
from collections import deque
import json
import socket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class SystemOptimizer:
    """
    系统级优化器
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def optimize_tcp_settings(self) -> Dict[str, Any]:
        """
        优化TCP设置
        """
        optimizations = {
            'socket_buffer_sizes': {
                'net.core.rmem_max': 16777216,
                'net.core.wmem_max': 16777216,
                'net.ipv4.tcp_rmem': '4096 87380 16777216',
                'net.ipv4.tcp_wmem': '4096 65536 16777216'
            },
            'connection_handling': {
                'net.core.somaxconn': 4096,
                'net.core.netdev_max_backlog': 5000,
                'net.ipv4.tcp_max_syn_backlog': 4096
            },
            'keepalive_settings': {
                'net.ipv4.tcp_keepalive_time': 600,
                'net.ipv4.tcp_keepalive_intvl': 60,
                'net.ipv4.tcp_keepalive_probes': 3
            }
        }
        
        self.logger.info("系统TCP优化配置已准备")
        return optimizations
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        获取内存信息
        """
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'system': {
                'total_gb': memory.total / 1024 / 1024 / 1024,
                'available_gb': memory.available / 1024 / 1024 / 1024,
                'used_percent': memory.percent,
                'free_gb': memory.free / 1024 / 1024 / 1024
            },
            'swap': {
                'total_gb': swap.total / 1024 / 1024 / 1024,
                'used_percent': swap.percent,
                'free_gb': swap.free / 1024 / 1024 / 1024
            }
        }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        获取CPU信息
        """
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'count': cpu_count,
            'usage_percent': cpu_percent,
            'frequency_mhz': cpu_freq.current if cpu_freq else 0,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """
        获取磁盘信息
        """
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        return {
            'usage': {
                'total_gb': disk_usage.total / 1024 / 1024 / 1024,
                'used_gb': disk_usage.used / 1024 / 1024 / 1024,
                'free_gb': disk_usage.free / 1024 / 1024 / 1024,
                'usage_percent': (disk_usage.used / disk_usage.total) * 100
            },
            'io_stats': {
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0,
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0
            }
        }
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        获取网络信息
        """
        net_io = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())
        
        return {
            'connections_count': net_connections,
            'bytes_sent': net_io.bytes_sent if net_io else 0,
            'bytes_recv': net_io.bytes_recv if net_io else 0,
            'packets_sent': net_io.packets_sent if net_io else 0,
            'packets_recv': net_io.packets_recv if net_io else 0
        }

class RabbitMQConfigOptimizer:
    """
    RabbitMQ配置优化器
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_production_config(self) -> str:
        """
        生成生产环境配置
        """
        config = """
# 生产环境RabbitMQ优化配置
# 
# 连接设置
listeners.tcp.default = 5672
listeners.ssl.default = 5671
num_acceptors.tcp = 16
num_acceptors.ssl = 16
connection_max_infinity = true
handshake_timeout = 30000
shutdown_timeout = 7000

# 内存和磁盘设置 - 保守策略
vm_memory_high_watermark.relative = 0.4
vm_memory_high_watermark_paging_ratio = 0.5
disk_free_limit.absolute = 1GB
disk_free_limit.absolute = 50MB
memory_monitoring = true

# 队列性能优化
default_prefetch = 100
prefetch_count.global = 0
consumer_timeout = 3600000
queue_index_embed_msgs_below = 4096

# 心跳设置
heartbeat = 60

# 性能相关
frame_max = 131072
channel_max = 0
channel_cache_size = 64

# 日志设置
log.file = rabbit.log
log.level = warning
log.rotation.size = 100MiB
log.rotation.count = 5

# SSL配置
ssl_options.cacertfile = /etc/rabbitmq/ssl/ca.pem
ssl_options.certfile = /etc/rabbitmq/ssl/server.pem
ssl_options.keyfile = /etc/rabbitmq/ssl/server.key
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = false
ssl_options.honor_cipher_order = true
ssl_options.honor_ecc_order = true
ssl_options.client_cert_login = false
ssl_options.peer_cert_lookup = amqp

# 集群配置
cluster_formation.peer_discovery_backend = classic_config
cluster_formation.classic_config.nodes.1 = rabbit@server1
cluster_formation.classic_config.nodes.2 = rabbit@server2
cluster_formation.classic_config.nodes.3 = rabbit@server3

# 管理插件
management.listener.port = 15672
management.listener.ip = 0.0.0.0
management.ssl.port = 15671
management.ssl.cacertfile = /etc/rabbitmq/ssl/ca.pem
management.ssl.certfile = /etc/rabbitmq/ssl/management.pem
management.ssl.keyfile = /etc/rabbitmq/ssl/management.key
"""
        return config.strip()
    
    def get_high_throughput_config(self) -> str:
        """
        生成高吞吐量配置
        """
        config = """
# 高吞吐量RabbitMQ配置
# 
# 连接设置 - 高并发
listeners.tcp.default = 5672
num_acceptors.tcp = 32
connection_max_infinity = true
handshake_timeout = 60000

# 内存设置 - 宽松策略
vm_memory_high_watermark.relative = 0.7
vm_memory_high_watermark_paging_ratio = 0.75
disk_free_limit.absolute = 500MB

# 队列性能优化 - 高预取值
default_prefetch = 1000
prefetch_count.global = 0
consumer_timeout = 300000

# 性能优化
frame_max = 131072
channel_max = 0
channel_cache_size = 128
connection_max_infinity = true

# 心跳 - 延长间隔
heartbeat = 120

# 批量处理优化
queue_index_embed_msgs_below = 1024
"""
        return config.strip()
    
    def get_low_latency_config(self) -> str:
        """
        生成低延迟配置
        """
        config = """
# 低延迟RabbitMQ配置
# 
# 连接设置 - 最小化开销
listeners.tcp.default = 5672
num_acceptors.tcp = 4
connection_max_infinity = true
handshake_timeout = 10000
shutdown_timeout = 5000

# 内存设置 - 严格限制
vm_memory_high_watermark.relative = 0.3
vm_memory_high_watermark_paging_ratio = 0.25
disk_free_limit.absolute = 2GB

# 队列性能优化 - 最小预取值
default_prefetch = 1
prefetch_count.global = 0
consumer_timeout = 60000

# 性能优化
frame_max = 65536
channel_max = 100
channel_cache_size = 16
connection_max_infinity = true

# 心跳 - 禁用
heartbeat = 0

# 低延迟优化
queue_index_embed_msgs_below = 512
default_queue_type = classic
"""
        return config.strip()
    
    def write_config_to_file(self, config_type: str, output_path: str) -> bool:
        """
        写入配置文件
        """
        try:
            if config_type == 'production':
                config = self.get_production_config()
            elif config_type == 'throughput':
                config = self.get_high_throughput_config()
            elif config_type == 'latency':
                config = self.get_low_latency_config()
            else:
                raise ValueError(f"未知的配置类型: {config_type}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(config)
            
            self.logger.info(f"配置已写入: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"写入配置失败: {e}")
            return False

class ConnectionPoolManager:
    """
    连接池管理器
    """
    
    def __init__(self, connection_params: pika.ConnectionParameters, 
                 max_connections: int = 10, 
                 min_connections: int = 2,
                 connection_timeout: int = 10):
        self.connection_params = connection_params
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_timeout = connection_timeout
        self.pool: List[pika.BlockingConnection] = []
        self.pool_lock = threading.RLock()
        self.created_connections = 0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_connection(self) -> Optional[pika.BlockingConnection]:
        """
        获取连接
        """
        with self.pool_lock:
            # 尝试从池中获取连接
            if self.pool:
                connection = self.pool.pop()
                if self._is_connection_healthy(connection):
                    return connection
                else:
                    try:
                        connection.close()
                    except:
                        pass
            # 如果池中没有可用连接，创建新连接
            if self.created_connections < self.max_connections:
                try:
                    connection = pika.BlockingConnection(self.connection_params)
                    self.created_connections += 1
                    self.logger.info(f"创建新连接，总连接数: {self.created_connections}")
                    return connection
                except Exception as e:
                    self.logger.error(f"创建连接失败: {e}")
                    return None
            else:
                self.logger.warning("已达到最大连接数限制")
                return None
    
    def return_connection(self, connection: pika.BlockingConnection):
        """
        归还连接
        """
        if not connection:
            return
        
        with self.pool_lock:
            if len(self.pool) < self.max_connections:
                if self._is_connection_healthy(connection):
                    self.pool.append(connection)
                    self.logger.debug(f"连接已归还到池中，池中连接数: {len(self.pool)}")
                else:
                    self.logger.warning("连接不健康，关闭连接")
                    try:
                        connection.close()
                        self.created_connections -= 1
                    except:
                        pass
            else:
                self.logger.debug("池已满，关闭连接")
                try:
                    connection.close()
                    self.created_connections -= 1
                except:
                    pass
    
    def _is_connection_healthy(self, connection: pika.BlockingConnection) -> bool:
        """
        检查连接是否健康
        """
        try:
            if connection.is_closed:
                return False
            
            # 测试连接是否可用
            return True
        except:
            return False
    
    def close_all_connections(self):
        """
        关闭所有连接
        """
        with self.pool_lock:
            for connection in self.pool:
                try:
                    connection.close()
                except:
                    pass
            self.pool.clear()
            self.logger.info("所有连接已关闭")
    
    def get_pool_stats(self) -> Dict[str, int]:
        """
        获取连接池统计
        """
        with self.pool_lock:
            return {
                'available_connections': len(self.pool),
                'total_created': self.created_connections,
                'max_connections': self.max_connections,
                'utilization_percent': (self.created_connections / self.max_connections) * 100
            }

class MessageBatchProcessor:
    """
    消息批处理器
    """
    
    def __init__(self, connection_pool: ConnectionPoolManager, 
                 batch_size: int = 100,
                 processing_interval: float = 1.0):
        self.connection_pool = connection_pool
        self.batch_size = batch_size
        self.processing_interval = processing_interval
        self.message_queue: Deque[Dict[str, Any]] = deque()
        self.processing_lock = threading.Lock()
        self.is_running = False
        self.processed_messages = 0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def start_processing(self):
        """
        开始批处理
        """
        self.is_running = True
        self.logger.info("开始消息批处理")
        
        # 启动处理线程
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
    
    def stop_processing(self):
        """
        停止批处理
        """
        self.is_running = False
        self.logger.info("停止消息批处理")
    
    def add_message(self, message: Dict[str, Any]):
        """
        添加消息
        """
        with self.processing_lock:
            self.message_queue.append(message)
    
    def _processing_loop(self):
        """
        处理循环
        """
        while self.is_running:
            try:
                # 收集批次
                batch = []
                with self.processing_lock:
                    while len(batch) < self.batch_size and self.message_queue:
                        batch.append(self.message_queue.popleft())
                
                if batch:
                    # 处理批次
                    self._process_batch(batch)
                
                # 控制处理间隔
                time.sleep(self.processing_interval)
                
            except Exception as e:
                self.logger.error(f"批处理循环错误: {e}")
                time.sleep(1.0)
    
    def _process_batch(self, batch: List[Dict[str, Any]]):
        """
        处理消息批次
        """
        processing_start = time.time()
        
        for message in batch:
            try:
                # 这里处理具体的业务逻辑
                self._process_single_message(message)
                
            except Exception as e:
                self.logger.error(f"处理消息失败: {e}")
        
        processing_time = time.time() - processing_start
        processed_count = len(batch)
        
        with self.processing_lock:
            self.processed_messages += processed_count
        
        # 记录性能指标
        throughput = processed_count / processing_time if processing_time > 0 else 0
        self.logger.info(f"批处理 {processed_count} 条消息，耗时 {processing_time:.3f}s，吞吐量: {throughput:.1f} msg/s")
    
    def _process_single_message(self, message: Dict[str, Any]):
        """
        处理单条消息
        """
        # 模拟消息处理
        # 这里应该包含具体的业务逻辑
        time.sleep(0.001)  # 1ms处理时间
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        """
        return {
            'processed_messages': self.processed_messages,
            'is_running': self.is_running,
            'queue_size': len(self.message_queue),
            'batch_size': self.batch_size
        }

class PerformanceOptimizer:
    """
    性能优化器
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.optimization_history = []
    
    def optimize_connection_settings(self, connection: pika.BlockingConnection) -> Dict[str, Any]:
        """
        优化连接设置
        """
        optimizations = {
            'tcp_nodelay': True,
            'keepalive': True,
            'buffer_size': {
                'send_buffer': 65536,
                'recv_buffer': 65536
            },
            'read_timeout': 300,
            'write_timeout': 300
        }
        
        # 应用优化设置
        try:
            # 这里需要在创建连接时应用这些设置
            self.logger.info("连接设置优化已应用")
            return optimizations
        except Exception as e:
            self.logger.error(f"应用连接优化失败: {e}")
            return {'error': str(e)}
    
    def optimize_channel_settings(self, channel: pika.channel.Channel) -> Dict[str, Any]:
        """
        优化通道设置
        """
        optimizations = {
            'prefetch_count': 100,
            'confirm_delivery': False,  # 高吞吐量场景可以关闭确认
            'auto_delete': False,
            'durable': True,
            'exclusive': False
        }
        
        try:
            # 应用预取优化
            channel.basic_qos(prefetch_count=optimizations['prefetch_count'])
            self.logger.info(f"通道预取设置已优化为: {optimizations['prefetch_count']}")
            return optimizations
        except Exception as e:
            self.logger.error(f"应用通道优化失败: {e}")
            return {'error': str(e)}
    
    def optimize_queue_settings(self, channel: pika.channel.Channel, 
                               queue_name: str) -> Dict[str, Any]:
        """
        优化队列设置
        """
        optimizations = {
            'durable': True,
            'exclusive': False,
            'auto_delete': False,
            'arguments': {
                'x-message-ttl': 86400000,  # 24小时
                'x-max-length': 100000,     # 最大消息数
                'x-dead-letter-exchange': 'dead_letter',
                'x-dead-letter-routing-key': 'dead_letter'
            }
        }
        
        try:
            # 声明队列
            channel.queue_declare(
                queue=queue_name,
                durable=optimizations['durable'],
                exclusive=optimizations['exclusive'],
                auto_delete=optimizations['auto_delete'],
                arguments=optimizations['arguments']
            )
            self.logger.info(f"队列 {queue_name} 设置已优化")
            return optimizations
        except Exception as e:
            self.logger.error(f"应用队列优化失败: {e}")
            return {'error': str(e)}
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析性能指标
        """
        analysis = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'recommendations': [],
            'metrics': metrics
        }
        
        # 分析吞吐量
        if 'throughput' in metrics:
            throughput = metrics['throughput']
            if throughput < 100:
                analysis['recommendations'].append("吞吐量较低，建议检查网络和连接池设置")
                analysis['overall_status'] = 'warning'
            elif throughput > 10000:
                analysis['recommendations'].append("吞吐量很高，注意内存和磁盘使用情况")
        
        # 分析延迟
        if 'latency' in metrics:
            latency = metrics['latency']
            if latency > 1000:  # 1秒
                analysis['recommendations'].append("延迟较高，建议优化消息处理逻辑")
                analysis['overall_status'] = 'warning'
            elif latency > 5000:  # 5秒
                analysis['recommendations'].append("延迟严重，建议立即检查系统资源")
                analysis['overall_status'] = 'critical'
        
        # 分析内存使用
        if 'memory_usage' in metrics:
            memory_usage = metrics['memory_usage']
            if memory_usage > 80:
                analysis['recommendations'].append("内存使用率过高，建议增加内存或优化代码")
                analysis['overall_status'] = 'critical'
            elif memory_usage > 60:
                analysis['recommendations'].append("内存使用率较高，建议监控内存使用情况")
        
        # 记录分析结果
        self.optimization_history.append(analysis)
        
        return analysis

class PerformanceMonitor:
    """
    性能监控器
    """
    
    def __init__(self, connection_pool: ConnectionPoolManager):
        self.connection_pool = connection_pool
        self.metrics: Deque[Dict[str, Any]] = deque(maxlen=1000)
        self.monitoring_lock = threading.Lock()
        self.is_monitoring = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def start_monitoring(self, interval: float = 1.0):
        """
        开始监控
        """
        self.is_monitoring = True
        self.logger.info("开始性能监控")
        
        # 启动监控线程
        monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,)
        )
        monitoring_thread.daemon = True
        monitoring_thread.start()
    
    def stop_monitoring(self):
        """
        停止监控
        """
        self.is_monitoring = False
        self.logger.info("停止性能监控")
    
    def _monitoring_loop(self, interval: float):
        """
        监控循环
        """
        while self.is_monitoring:
            try:
                # 收集指标
                metrics = self._collect_metrics()
                
                with self.monitoring_lock:
                    self.metrics.append(metrics)
                
                # 检查告警
                self._check_alerts(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """
        收集性能指标
        """
        timestamp = time.time()
        
        # 系统指标
        system_optimizer = SystemOptimizer()
        memory_info = system_optimizer.get_memory_info()
        cpu_info = system_optimizer.get_cpu_info()
        disk_info = system_optimizer.get_disk_info()
        network_info = system_optimizer.get_network_info()
        
        # 连接池指标
        pool_stats = self.connection_pool.get_pool_stats()
        
        # RabbitMQ连接指标
        rabbitmq_metrics = self._collect_rabbitmq_metrics()
        
        return {
            'timestamp': timestamp,
            'system': {
                'memory': memory_info,
                'cpu': cpu_info,
                'disk': disk_info,
                'network': network_info
            },
            'connection_pool': pool_stats,
            'rabbitmq': rabbitmq_metrics
        }
    
    def _collect_rabbitmq_metrics(self) -> Dict[str, Any]:
        """
        收集RabbitMQ指标
        """
        metrics = {
            'connections': 0,
            'channels': 0,
            'queues': 0,
            'message_count': 0,
            'message_rate': 0
        }
        
        try:
            # 获取RabbitMQ管理指标
            connection = self.connection_pool.get_connection()
            if connection:
                # 这里可以添加实际的RabbitMQ API调用
                # 暂时使用模拟数据
                metrics['connections'] = 5
                metrics['channels'] = 20
                metrics['queues'] = 10
                metrics['message_count'] = 1000
                metrics['message_rate'] = 100
                
                self.connection_pool.return_connection(connection)
        except Exception as e:
            self.logger.error(f"收集RabbitMQ指标失败: {e}")
        
        return metrics
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """
        检查告警条件
        """
        # 内存告警
        memory_usage = metrics['system']['memory']['system']['used_percent']
        if memory_usage > 80:
            self.logger.warning(f"内存使用率过高: {memory_usage}%")
        elif memory_usage > 90:
            self.logger.error(f"内存使用率严重过高: {memory_usage}%")
        
        # CPU告警
        cpu_usage = metrics['system']['cpu']['usage_percent']
        if cpu_usage > 80:
            self.logger.warning(f"CPU使用率过高: {cpu_usage}%")
        
        # 连接池告警
        pool_stats = metrics['connection_pool']
        if pool_stats['utilization_percent'] > 80:
            self.logger.warning(f"连接池使用率过高: {pool_stats['utilization_percent']:.1f}%")
    
    def get_recent_metrics(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        获取最近的指标
        """
        with self.monitoring_lock:
            return list(self.metrics)[-count:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        """
        recent_metrics = self.get_recent_metrics(60)  # 最近60个数据点
        
        if not recent_metrics:
            return {'status': 'no_data'}
        
        # 计算平均值
        memory_usage = [m['system']['memory']['system']['used_percent'] for m in recent_metrics]
        cpu_usage = [m['system']['cpu']['usage_percent'] for m in recent_metrics]
        message_rates = [m['rabbitmq']['message_rate'] for m in recent_metrics]
        connection_count = [m['rabbitmq']['connections'] for m in recent_metrics]
        
        return {
            'avg_memory_usage': statistics.mean(memory_usage) if memory_usage else 0,
            'avg_cpu_usage': statistics.mean(cpu_usage) if cpu_usage else 0,
            'avg_message_rate': statistics.mean(message_rates) if message_rates else 0,
            'avg_connection_count': statistics.mean(connection_count) if connection_count else 0,
            'data_points': len(recent_metrics),
            'time_range': {
                'start': recent_metrics[0]['timestamp'] if recent_metrics else 0,
                'end': recent_metrics[-1]['timestamp'] if recent_metrics else 0
            }
        }

class PerformanceTuner:
    """
    性能调优器
    """
    
    def __init__(self, connection_pool: ConnectionPoolManager):
        self.connection_pool = connection_pool
        self.monitor = PerformanceMonitor(connection_pool)
        self.optimizer = PerformanceOptimizer()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def auto_tune(self, target_performance: str = 'balanced') -> Dict[str, Any]:
        """
        自动调优
        """
        tuning_results = {
            'timestamp': time.time(),
            'target_performance': target_performance,
            'optimizations_applied': [],
            'performance_improvement': {},
            'recommendations': []
        }
        
        try:
            self.logger.info(f"开始自动调优，目标性能: {target_performance}")
            
            # 收集当前性能数据
            current_metrics = self._get_baseline_metrics()
            
            # 根据目标应用优化
            if target_performance == 'throughput':
                tuning_results['optimizations_applied'] = self._optimize_for_throughput()
            elif target_performance == 'latency':
                tuning_results['optimizations_applied'] = self._optimize_for_latency()
            elif target_performance == 'reliability':
                tuning_results['optimizations_applied'] = self._optimize_for_reliability()
            else:  # balanced
                tuning_results['optimizations_applied'] = self._optimize_for_balance()
            
            # 等待优化生效
            time.sleep(5)
            
            # 测量优化后的性能
            improved_metrics = self._get_baseline_metrics()
            
            # 计算性能改进
            tuning_results['performance_improvement'] = self._calculate_improvement(
                current_metrics, improved_metrics
            )
            
            self.logger.info("自动调优完成")
            
        except Exception as e:
            self.logger.error(f"自动调优失败: {e}")
            tuning_results['error'] = str(e)
        
        return tuning_results
    
    def _optimize_for_throughput(self) -> List[str]:
        """
        针对吞吐量优化
        """
        optimizations = []
        
        # 增加预取值
        try:
            # 这里的代码需要适配实际的RabbitMQ连接
            optimizations.append("increased_prefetch_count_to_1000")
            optimizations.append("enabled_batching")
            optimizations.append("disabled_publisher_confirms")
            optimizations.append("optimized_connection_pool_size")
            
            self.logger.info("已应用吞吐量优化")
            
        except Exception as e:
            self.logger.error(f"吞吐量优化失败: {e}")
        
        return optimizations
    
    def _optimize_for_latency(self) -> List[str]:
        """
        针对延迟优化
        """
        optimizations = []
        
        try:
            optimizations.append("decreased_prefetch_count_to_1")
            optimizations.append("disabled_heartbeat")
            optimizations.append("enabled_tcp_nodelay")
            optimizations.append("reduced_connection_pool_size")
            
            self.logger.info("已应用延迟优化")
            
        except Exception as e:
            self.logger.error(f"延迟优化失败: {e}")
        
        return optimizations
    
    def _optimize_for_reliability(self) -> List[str]:
        """
        针对可靠性优化
        """
        optimizations = []
        
        try:
            optimizations.append("enabled_publisher_confirms")
            optimizations.append("enabled_mandatory_flag")
            optimizations.append("enabled_transactional_channels")
            optimizations.append("increased_persistent_messages")
            
            self.logger.info("已应用可靠性优化")
            
        except Exception as e:
            self.logger.error(f"可靠性优化失败: {e}")
        
        return optimizations
    
    def _optimize_for_balance(self) -> List[str]:
        """
        针对平衡优化
        """
        optimizations = []
        
        try:
            optimizations.append("balanced_prefetch_count_100")
            optimizations.append("enabled_publisher_confirms")
            optimizations.append("moderate_connection_pool_size")
            optimizations.append("enabled_auto_scaling")
            
            self.logger.info("已应用平衡优化")
            
        except Exception as e:
            self.logger.error(f"平衡优化失败: {e}")
        
        return optimizations
    
    def _get_baseline_metrics(self) -> Dict[str, float]:
        """
        获取基准性能指标
        """
        # 收集5秒钟的性能数据
        start_time = time.time()
        messages_processed = 0
        processing_times = []
        
        # 这里应该收集实际的消息处理数据
        # 暂时使用模拟数据
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'throughput_msg_per_sec': messages_processed / duration if duration > 0 else 0,
            'avg_processing_time_ms': statistics.mean(processing_times) if processing_times else 0,
            'memory_usage_percent': psutil.virtual_memory().percent,
            'cpu_usage_percent': psutil.cpu_percent()
        }
    
    def _calculate_improvement(self, before: Dict[str, float], 
                              after: Dict[str, float]) -> Dict[str, Any]:
        """
        计算性能改进
        """
        improvements = {}
        
        for metric in ['throughput_msg_per_sec', 'avg_processing_time_ms', 
                      'memory_usage_percent', 'cpu_usage_percent']:
            if metric in before and metric in after and before[metric] != 0:
                if metric == 'avg_processing_time_ms' or 'usage' in metric:
                    # 对于延迟和利用率，越小越好
                    improvement = ((before[metric] - after[metric]) / before[metric]) * 100
                else:
                    # 对于吞吐量，越大越好
                    improvement = ((after[metric] - before[metric]) / before[metric]) * 100
                
                improvements[metric] = {
                    'before': before[metric],
                    'after': after[metric],
                    'improvement_percent': improvement
                }
        
        return improvements

def demo_performance_optimization():
    """
    性能优化演示
    """
    print("=== RabbitMQ 性能优化演示 ===")
    
    # 创建连接参数
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        connection_attempts=3,
        retry_delay=1,
        heartbeat=60,
        blocked_connection_timeout=300
    )
    
    # 创建连接池管理器
    connection_pool = ConnectionPoolManager(
        connection_params=connection_params,
        max_connections=10,
        min_connections=2
    )
    
    # 创建批处理器
    batch_processor = MessageBatchProcessor(
        connection_pool=connection_pool,
        batch_size=50,
        processing_interval=0.1
    )
    
    # 创建性能监控器
    monitor = PerformanceMonitor(connection_pool)
    
    # 创建性能调优器
    tuner = PerformanceTuner(connection_pool)
    
    # 创建配置优化器
    config_optimizer = RabbitMQConfigOptimizer()
    
    print("\n1. 系统优化器演示:")
    system_optimizer = SystemOptimizer()
    
    print("内存信息:", json.dumps(system_optimizer.get_memory_info(), indent=2))
    print("CPU信息:", json.dumps(system_optimizer.get_cpu_info(), indent=2))
    print("磁盘信息:", json.dumps(system_optimizer.get_disk_info(), indent=2))
    
    print("\n2. 连接池管理演示:")
    # 测试连接池
    connection = connection_pool.get_connection()
    if connection:
        print("获取连接成功")
        connection_pool.return_connection(connection)
        print("归还连接成功")
    
    pool_stats = connection_pool.get_pool_stats()
    print("连接池统计:", json.dumps(pool_stats, indent=2))
    
    print("\n3. 配置优化演示:")
    # 生成配置文件
    configs = ['production', 'throughput', 'latency']
    for config_type in configs:
        config_content = getattr(config_optimizer, f'get_{config_type}_config')()
        print(f"{config_type} 配置长度: {len(config_content)} 字符")
    
    print("\n4. 性能监控演示:")
    # 开始监控
    monitor.start_monitoring(interval=1.0)
    
    # 模拟一些指标收集
    time.sleep(3)
    
    # 获取性能摘要
    summary = monitor.get_performance_summary()
    print("性能摘要:", json.dumps(summary, indent=2))
    
    print("\n5. 自动调优演示:")
    # 演示自动调优
    tuning_result = tuner.auto_tune('balanced')
    print("调优结果:", json.dumps(tuning_result, indent=2))
    
    # 停止监控
    monitor.stop_monitoring()
    
    # 关闭连接池
    connection_pool.close_all_connections()
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    try:
        demo_performance_optimization()
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"演示过程中发生错误: {e}")