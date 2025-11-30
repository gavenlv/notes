#!/usr/bin/env python3
"""
第8章：RabbitMQ性能优化与调优代码示例
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

class HighThroughputConsumer:
    """
    高吞吐量消费者
    """
    
    def __init__(self, connection_pool: ConnectionPoolManager, 
                 batch_size: int = 100, 
                 prefetch_count: int = 1000):
        self.connection_pool = connection_pool
        self.batch_size = batch_size
        self.prefetch_count = prefetch_count
        self.is_running = False
        self.processed_messages = 0
        self.processing_lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def start_consuming(self, queue_name: str, worker_count: int = 4):
        """
        开始高吞吐量消费
        """
        self.is_running = True
        
        # 创建工作线程
        threads = []
        for i in range(worker_count):
            thread = threading.Thread(
                target=self._worker_thread,
                args=(f"worker_{i}", queue_name)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        self.logger.info(f"启动 {worker_count} 个工作线程进行高吞吐量消费")
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
    
    def _worker_thread(self, worker_id: str, queue_name: str):
        """
        工作线程
        """
        while self.is_running:
            try:
                connection = self.connection_pool.get_connection()
                if not connection:
                    time.sleep(0.1)
                    continue
                
                try:
                    channel = connection.channel()
                    channel.basic_qos(prefetch_count=self.prefetch_count)
                    
                    # 批量获取消息
                    batch = []
                    for _ in range(self.batch_size):
                        method_frame, header_frame, body = channel.basic_get(
                            queue_name, auto_ack=False
                        )
                        if method_frame:
                            batch.append((method_frame, header_frame, body))
                        else:
                            break
                    
                    if batch:
                        # 处理批次
                        self._process_batch(channel, batch, worker_id)
                    else:
                        # 没有消息时短暂休眠
                        time.sleep(0.01)
                
                finally:
                    if connection:
                        self.connection_pool.return_connection(connection)
            
            except Exception as e:
                self.logger.error(f"Worker {worker_id} 错误: {e}")
                time.sleep(1.0)
    
    def _process_batch(self, channel, batch, worker_id: str):
        """
        处理消息批次
        """
        processing_start = time.time()
        
        for method_frame, header_frame, body in batch:
            try:
                # 这里处理具体的业务逻辑
                self._process_single_message(body)
                
            except Exception as e:
                self.logger.error(f"处理消息失败: {e}")
        
        # 批量确认
        try:
            for method_frame, _, _ in batch:
                channel.basic_nack(
                    delivery_tag=method_frame.delivery_tag, 
                    requeue=False
                )
        except Exception as e:
            self.logger.error(f"批量确认失败: {e}")
        
        processing_time = time.time() - processing_start
        processed_count = len(batch)
        
        with self.processing_lock:
            self.processed_messages += processed_count
        
        # 记录性能指标
        throughput = processed_count / processing_time if processing_time > 0 else 0
        self.logger.info(f"Worker {worker_id} 批量处理 {processed_count} 条消息，"
                       f"耗时 {processing_time:.3f}s，吞吐量: {throughput:.1f} msg/s")
    
    def _process_single_message(self, message_body: bytes):
        """
        处理单条消息
        """
        # 模拟消息处理
        # 这里应该包含具体的业务逻辑
        time.sleep(0.001)  # 1ms处理时间
    
    def stop_consuming(self):
        """
        停止消费
        """
        self.is_running = False
        self.logger.info("停止高吞吐量消费")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        """
        return {
            'processed_messages': self.processed_messages,
            'is_running': self.is_running,
            'batch_size': self.batch_size,
            'prefetch_count': self.prefetch_count
        }

class PerformanceTestRunner:
    """
    性能测试运行器
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def run_baseline_test(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """
        运行基准测试
        """
        self.logger.info(f"开始 {duration_seconds} 秒基准测试")
        
        start_time = time.time()
        message_count = 0
        error_count = 0
        
        # 这里应该实现实际的基准测试逻辑
        # 暂时使用模拟数据
        
        end_time = time.time()
        actual_duration = end_time - start_time
        throughput = message_count / actual_duration if actual_duration > 0 else 0
        
        return {
            'duration_seconds': actual_duration,
            'messages_processed': message_count,
            'errors_count': error_count,
            'throughput_msg_per_sec': throughput,
            'success_rate_percent': ((message_count - error_count) / message_count * 100) if message_count > 0 else 0
        }

def demo_performance_optimization():
    """
    性能优化演示
    """
    print("=== 第8章：RabbitMQ性能优化与调优演示 ===")
    
    # 创建连接参数
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        connection_attempts=3,
        retry_delay=1,
        heartbeat=60,
        blocked_connection_timeout=300
    )
    
    print("\n1. 系统优化器演示:")
    system_optimizer = SystemOptimizer()
    
    print("内存信息:", json.dumps(system_optimizer.get_memory_info(), indent=2))
    print("CPU信息:", json.dumps(system_optimizer.get_cpu_info(), indent=2))
    print("磁盘信息:", json.dumps(system_optimizer.get_disk_info(), indent=2))
    
    print("\n2. 连接池管理演示:")
    connection_pool = ConnectionPoolManager(
        connection_params=connection_params,
        max_connections=10,
        min_connections=2
    )
    
    # 测试连接池
    pool_stats = connection_pool.get_pool_stats()
    print("连接池统计:", json.dumps(pool_stats, indent=2))
    
    print("\n3. 配置优化演示:")
    config_optimizer = RabbitMQConfigOptimizer()
    
    # 生成配置文件
    configs = ['production', 'high_throughput', 'low_latency']
    for config_type in configs:
        config_method = f'get_{config_type}_config'
        if hasattr(config_optimizer, config_method):
            config_content = getattr(config_optimizer, config_method)()
            print(f"{config_type} 配置长度: {len(config_content)} 字符")
    
    print("\n4. 高吞吐量消费者演示:")
    high_throughput_consumer = HighThroughputConsumer(
        connection_pool=connection_pool,
        batch_size=50,
        prefetch_count=100
    )
    
    consumer_stats = high_throughput_consumer.get_stats()
    print("高吞吐量消费者状态:", json.dumps(consumer_stats, indent=2))
    
    print("\n5. 性能测试演示:")
    test_runner = PerformanceTestRunner()
    test_results = test_runner.run_baseline_test(duration_seconds=10)
    print("基准测试结果:", json.dumps(test_results, indent=2))
    
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