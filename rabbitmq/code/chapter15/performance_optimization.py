#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ性能优化与调优 - 核心代码示例
=====================================

本文件包含RabbitMQ性能优化的核心实现，包括：
1. 性能监控与分析
2. 系统资源优化
3. RabbitMQ服务器优化
4. 客户端性能优化
5. 网络通信优化
6. 存储和持久化优化
7. 集群性能调优
8. 基准测试与性能评估
9. 故障排查与性能诊断

Author: Claude
Date: 2024
"""

import os
import sys
import time
import psutil
import pika
import logging
import threading
import statistics
import subprocess
import json
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import queue
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aio_pika

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# 1. 性能监控与分析类
# =============================================================================

class PerformanceMetric(Enum):
    """性能指标类型"""
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESOURCE_USAGE = "resource_usage"
    QUEUE_SIZE = "queue_size"
    CONNECTION_COUNT = "connection_count"
    MESSAGE_RATE = "message_rate"
    ERROR_RATE = "error_rate"


@dataclass
class PerformanceData:
    """性能数据容器"""
    timestamp: float
    metric_type: str
    value: float
    labels: Dict[str, Any]


class LatencyAnalyzer:
    """延迟分析器"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.latencies: List[float] = []
        self.lock = threading.Lock()
    
    def record_latency(self, latency: float) -> None:
        """记录延迟数据"""
        with self.lock:
            self.latencies.append(latency)
            if len(self.latencies) > self.window_size:
                self.latencies.pop(0)
    
    def get_latency_stats(self) -> Dict[str, float]:
        """获取延迟统计信息"""
        with self.lock:
            if not self.latencies:
                return {}
            
            sorted_latencies = sorted(self.latencies)
            n = len(sorted_latencies)
            
            return {
                'count': n,
                'min': sorted_latencies[0],
                'max': sorted_latencies[-1],
                'mean': statistics.mean(sorted_latencies),
                'median': statistics.median(sorted_latencies),
                'p95': sorted_latencies[int(n * 0.95)],
                'p99': sorted_latencies[int(n * 0.99)],
                'stddev': statistics.stdev(sorted_latencies) if n > 1 else 0
            }
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """检测延迟异常"""
        stats = self.get_latency_stats()
        if not stats or stats['count'] < 100:
            return []
        
        mean = stats['mean']
        stddev = stats['stddev']
        
        anomalies = []
        with self.lock:
            for latency in self.latencies[-100:]:  # 最近100个
                if abs(latency - mean) > threshold * stddev:
                    anomalies.append({
                        'latency': latency,
                        'deviation': abs(latency - mean) / stddev if stddev > 0 else 0,
                        'timestamp': time.time()
                    })
        
        return anomalies


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, rabbitmq_config: Dict[str, Any]):
        self.config = rabbitmq_config
        self.latency_analyzer = LatencyAnalyzer()
        self.metrics_buffer: List[PerformanceData] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.collectors = {
            'system': self._collect_system_metrics,
            'rabbitmq': self._collect_rabbitmq_metrics,
            'network': self._collect_network_metrics
        }
    
    def start_monitoring(self, interval: float = 1.0) -> None:
        """开始性能监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("性能监控已启动")
    
    def stop_monitoring(self) -> None:
        """停止性能监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("性能监控已停止")
    
    def _monitoring_loop(self, interval: float) -> None:
        """监控循环"""
        while self.monitoring:
            try:
                # 收集各类指标
                for collector_name, collector_func in self.collectors.items():
                    metrics = collector_func()
                    for metric in metrics:
                        self.metrics_buffer.append(metric)
                
                # 清理缓存（保留最近1000条记录）
                if len(self.metrics_buffer) > 1000:
                    self.metrics_buffer = self.metrics_buffer[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"监控过程中发生错误: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> List[PerformanceData]:
        """收集系统指标"""
        metrics = []
        timestamp = time.time()
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(PerformanceData(
            timestamp=timestamp,
            metric_type='cpu_utilization',
            value=cpu_percent,
            labels={'component': 'system'}
        ))
        
        # 内存使用率
        memory = psutil.virtual_memory()
        metrics.append(PerformanceData(
            timestamp=timestamp,
            metric_type='memory_utilization',
            value=memory.percent,
            labels={'component': 'system'}
        ))
        
        # 磁盘I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            metrics.append(PerformanceData(
                timestamp=timestamp,
                metric_type='disk_read_bytes_per_sec',
                value=disk_io.read_bytes,
                labels={'component': 'system', 'device': 'sda'}
            ))
            metrics.append(PerformanceData(
                timestamp=timestamp,
                metric_type='disk_write_bytes_per_sec',
                value=disk_io.write_bytes,
                labels={'component': 'system', 'device': 'sda'}
            ))
        
        return metrics
    
    def _collect_rabbitmq_metrics(self) -> List[PerformanceData]:
        """收集RabbitMQ指标"""
        metrics = []
        timestamp = time.time()
        
        try:
            connection = self._create_rabbitmq_connection()
            channel = connection.channel()
            
            # 队列统计
            queues = channel.queue_declare('', exclusive=True, auto_delete=True)
            
            metrics.append(PerformanceData(
                timestamp=timestamp,
                metric_type='queue_messages',
                value=queues.method.message_count,
                labels={'queue': 'monitor_queue'}
            ))
            
            metrics.append(PerformanceData(
                timestamp=timestamp,
                metric_type='queue_consumers',
                value=queues.method.consumer_count,
                labels={'queue': 'monitor_queue'}
            ))
            
            connection.close()
            
        except Exception as e:
            logger.error(f"收集RabbitMQ指标失败: {e}")
        
        return metrics
    
    def _collect_network_metrics(self) -> List[PerformanceData]:
        """收集网络指标"""
        metrics = []
        timestamp = time.time()
        
        try:
            # 网络接口统计
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.append(PerformanceData(
                    timestamp=timestamp,
                    metric_type='network_bytes_sent_per_sec',
                    value=net_io.bytes_sent,
                    labels={'interface': 'total'}
                ))
                metrics.append(PerformanceData(
                    timestamp=timestamp,
                    metric_type='network_bytes_recv_per_sec',
                    value=net_io.bytes_recv,
                    labels={'interface': 'total'}
                ))
        
        except Exception as e:
            logger.error(f"收集网络指标失败: {e}")
        
        return metrics
    
    def _create_rabbitmq_connection(self) -> pika.BlockingConnection:
        """创建RabbitMQ连接"""
        credentials = pika.PlainCredentials(
            self.config.get('username', 'guest'),
            self.config.get('password', 'guest')
        )
        
        parameters = pika.ConnectionParameters(
            host=self.config.get('host', 'localhost'),
            port=self.config.get('port', 5672),
            credentials=credentials,
            heartbeat=30,
            connection_attempts=3,
            retry_delay=5
        )
        
        return pika.BlockingConnection(parameters)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_buffer:
            return {}
        
        latest_metrics = {}
        for metric in self.metrics_buffer[-100:]:  # 最近100条记录
            key = f"{metric.metric_type}_{metric.labels.get('component', 'unknown')}"
            if key not in latest_metrics:
                latest_metrics[key] = []
            latest_metrics[key].append(metric.value)
        
        summary = {}
        for key, values in latest_metrics.items():
            summary[key] = {
                'current': values[-1] if values else 0,
                'average': statistics.mean(values) if values else 0,
                'min': min(values) if values else 0,
                'max': max(values) if values else 0
            }
        
        # 添加延迟分析
        summary['latency_analysis'] = self.latency_analyzer.get_latency_stats()
        summary['latency_anomalies'] = self.latency_analyzer.detect_anomalies()
        
        return summary


# =============================================================================
# 2. 智能连接池管理
# =============================================================================

@dataclass
class ConnectionConfig:
    """连接配置"""
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    virtual_host: str = '/'
    heartbeat: int = 30
    connection_timeout: int = 30
    blocked_connection_timeout: int = 300


class IntelligentConnectionPool:
    """智能连接池"""
    
    def __init__(self, config: ConnectionConfig, max_size: int = 20):
        self.config = config
        self.max_size = max_size
        self.available_connections = queue.Queue(maxsize=max_size)
        self.active_connections = set()
        self.connection_stats = {
            'created': 0,
            'reused': 0,
            'failed': 0,
            'closed': 0
        }
        self.lock = threading.Lock()
        self.last_activity = {}
        
    def get_connection(self) -> Optional[pika.BlockingConnection]:
        """获取连接"""
        try:
            # 尝试从可用连接池获取
            try:
                connection = self.available_connections.get_nowait()
                if self._is_connection_valid(connection):
                    with self.lock:
                        self.active_connections.add(connection)
                        self.connection_stats['reused'] += 1
                        self.last_activity[id(connection)] = time.time()
                    return connection
            except queue.Empty:
                pass
            
            # 创建新连接
            if len(self.active_connections) < self.max_size:
                connection = self._create_connection()
                if connection:
                    with self.lock:
                        self.active_connections.add(connection)
                        self.connection_stats['created'] += 1
                        self.last_activity[id(connection)] = time.time()
                    return connection
            
            return None
            
        except Exception as e:
            logger.error(f"获取连接失败: {e}")
            self.connection_stats['failed'] += 1
            return None
    
    def return_connection(self, connection: pika.BlockingConnection) -> None:
        """归还连接"""
        try:
            with self.lock:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
                    self.last_activity[id(connection)] = time.time()
            
            if self._is_connection_valid(connection):
                try:
                    self.available_connections.put_nowait(connection)
                except queue.Full:
                    connection.close()
                    with self.lock:
                        self.connection_stats['closed'] += 1
            else:
                connection.close()
                with self.lock:
                    self.connection_stats['closed'] += 1
                    
        except Exception as e:
            logger.error(f"归还连接失败: {e}")
            try:
                connection.close()
            except:
                pass
    
    def _create_connection(self) -> Optional[pika.BlockingConnection]:
        """创建新连接"""
        try:
            credentials = pika.PlainCredentials(
                self.config.username, 
                self.config.password
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.virtual_host,
                credentials=credentials,
                heartbeat=self.config.heartbeat,
                connection_attempts=3,
                retry_delay=5,
                blocked_connection_timeout=self.config.blocked_connection_timeout,
                socket_timeout=self.config.connection_timeout
            )
            
            return pika.BlockingConnection(parameters)
            
        except Exception as e:
            logger.error(f"创建连接失败: {e}")
            return None
    
    def _is_connection_valid(self, connection: pika.BlockingConnection) -> bool:
        """检查连接有效性"""
        try:
            return (connection.is_open and 
                   hasattr(connection, '_impl') and
                   connection._impl.is_baselayer_transport_tcp_socket_connected())
        except:
            return False
    
    def cleanup_idle_connections(self, idle_timeout: int = 300) -> None:
        """清理空闲连接"""
        current_time = time.time()
        connections_to_close = []
        
        with self.lock:
            for conn_id, last_time in self.last_activity.items():
                if current_time - last_time > idle_timeout:
                    # 查找对应的连接对象
                    for conn in self.active_connections:
                        if id(conn) == conn_id:
                            connections_to_close.append(conn)
                            break
        
        for conn in connections_to_close:
            try:
                conn.close()
                with self.lock:
                    if conn in self.active_connections:
                        self.active_connections.remove(conn)
                        self.connection_stats['closed'] += 1
            except:
                pass
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        with self.lock:
            return {
                'pool_size': self.max_size,
                'active_connections': len(self.active_connections),
                'available_connections': self.available_connections.qsize(),
                'total_capacity': self.max_size,
                'utilization_rate': len(self.active_connections) / self.max_size,
                'stats': self.connection_stats.copy()
            }


# =============================================================================
# 3. 批量消息处理
# =============================================================================

class BatchProducer:
    """批量生产者"""
    
    def __init__(self, channel: pika.channel.Channel, 
                 batch_size: int = 100, 
                 flush_interval: float = 1.0):
        self.channel = channel
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending_messages: List[Dict[str, Any]] = []
        self.last_flush_time = time.time()
        self.batch_stats = {
            'total_messages': 0,
            'total_batches': 0,
            'flush_count': 0,
            'average_batch_size': 0,
            'failed_batches': 0
        }
        self.lock = threading.Lock()
    
    def publish_batch(self, exchange: str, routing_key: str, 
                     message: Union[str, bytes], 
                     properties: Optional[pika.spec.BasicProperties] = None) -> bool:
        """批量发布消息"""
        with self.lock:
            self.pending_messages.append({
                'exchange': exchange,
                'routing_key': routing_key,
                'body': message,
                'properties': properties,
                'timestamp': time.time()
            })
            
            self.batch_stats['total_messages'] += 1
            
            # 检查是否需要批量发送
            should_flush = (
                len(self.pending_messages) >= self.batch_size or
                time.time() - self.last_flush_time >= self.flush_interval
            )
            
            if should_flush:
                return self._flush_batch()
        
        return True
    
    def _flush_batch(self) -> bool:
        """批量发送消息"""
        if not self.pending_messages:
            return True
        
        try:
            with self.lock:
                messages_to_send = self.pending_messages.copy()
                self.pending_messages.clear()
            
            # 事务性批量发送
            self.channel.tx_select()
            
            for msg in messages_to_send:
                self.channel.basic_publish(
                    exchange=msg['exchange'],
                    routing_key=msg['routing_key'],
                    body=msg['body'],
                    properties=msg['properties'],
                    mandatory=True
                )
            
            # 提交事务
            self.channel.tx_commit()
            
            # 更新统计信息
            with self.lock:
                self.batch_stats['total_batches'] += len(messages_to_send)
                self.batch_stats['flush_count'] += 1
                self.batch_stats['average_batch_size'] = (
                    self.batch_stats['total_messages'] / max(1, self.batch_stats['flush_count'])
                )
            
            return True
            
        except Exception as e:
            # 回滚事务
            try:
                self.channel.tx_rollback()
            except:
                pass
            
            logger.error(f"批量发送失败: {e}")
            
            with self.lock:
                self.batch_stats['failed_batches'] += 1
            
            return False
    
    def flush_remaining(self) -> bool:
        """强制发送剩余消息"""
        with self.lock:
            if not self.pending_messages:
                return True
        
        return self._flush_batch()
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """获取批量处理统计信息"""
        with self.lock:
            return self.batch_stats.copy()


class BatchConsumer:
    """批量消费者"""
    
    def __init__(self, channel: pika.channel.Channel, 
                 queue_name: str, 
                 batch_size: int = 50,
                 processing_timeout: float = 30.0):
        self.channel = channel
        self.queue_name = queue_name
        self.batch_size = batch_size
        self.processing_timeout = processing_timeout
        self.consumed_messages: List[Dict[str, Any]] = []
        self.batch_stats = {
            'total_messages': 0,
            'total_batches': 0,
            'processing_time': 0,
            'throughput': 0,
            'failed_batches': 0
        }
        self.lock = threading.Lock()
        self.processing = False
        self.message_handler: Optional[Callable] = None
    
    def start_batch_consumption(self, message_handler: Callable[[List[Dict[str, Any]]], None]) -> None:
        """开始批量消费"""
        self.message_handler = message_handler
        self.processing = True
        
        while self.processing:
            try:
                # 批量获取消息
                messages = self._get_batch_messages()
                
                if messages:
                    start_time = time.time()
                    
                    # 处理消息批次
                    success = self._process_batch(messages)
                    
                    processing_time = time.time() - start_time
                    
                    with self.lock:
                        self.batch_stats['total_messages'] += len(messages)
                        self.batch_stats['total_batches'] += 1
                        self.batch_stats['processing_time'] += processing_time
                        if self.batch_stats['processing_time'] > 0:
                            self.batch_stats['throughput'] = (
                                self.batch_stats['total_messages'] / 
                                self.batch_stats['processing_time']
                            )
                        if not success:
                            self.batch_stats['failed_batches'] += 1
                    
                else:
                    # 没有消息，等待一段时间
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"批量消费错误: {e}")
                time.sleep(1)
    
    def _get_batch_messages(self) -> List[Dict[str, Any]]:
        """批量获取消息"""
        messages = []
        
        for _ in range(self.batch_size):
            try:
                method_frame, header_frame, body = self.channel.basic_get(
                    queue=self.queue_name, 
                    auto_ack=False
                )
                
                if method_frame is None:
                    break
                
                messages.append({
                    'method': method_frame,
                    'header': header_frame,
                    'body': body,
                    'delivery_tag': method_frame.delivery_tag
                })
                
            except Exception as e:
                logger.error(f"获取消息失败: {e}")
                break
        
        return messages
    
    def _process_batch(self, messages: List[Dict[str, Any]]) -> bool:
        """处理消息批次"""
        try:
            # 使用事务性处理
            self.channel.tx_select()
            
            # 调用消息处理器
            if self.message_handler:
                self.message_handler(messages)
            
            # 确认所有消息
            for msg in messages:
                self.channel.basic_ack(
                    delivery_tag=msg['delivery_tag'], 
                    multiple=True
                )
            
            # 提交事务
            self.channel.tx_commit()
            
            return True
            
        except Exception as e:
            # 回滚事务，消息将重新投递
            try:
                self.channel.tx_rollback()
            except:
                pass
            logger.error(f"批次处理失败: {e}")
            return False
    
    def stop_consumption(self) -> None:
        """停止消费"""
        self.processing = False
    
    def get_consumption_stats(self) -> Dict[str, Any]:
        """获取消费统计信息"""
        with self.lock:
            return self.batch_stats.copy()


# =============================================================================
# 4. 消息压缩优化
# =============================================================================

class CompressionType(Enum):
    """压缩类型"""
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"


class MessageCompressor:
    """消息压缩器"""
    
    def __init__(self, compression_type: CompressionType = CompressionType.GZIP,
                 compression_level: int = 6, 
                 min_size_for_compression: int = 1024):
        self.compression_type = compression_type
        self.compression_level = compression_level
        self.min_size = min_size_for_compression
        
        # 预计算的压缩器
        self._compressors = {
            CompressionType.ZLIB: lambda data: __import__('zlib').compress(
                data, self.compression_level
            ),
            CompressionType.GZIP: lambda data: __import__('gzip').compress(
                data, self.compression_level
            )
        }
        
        self._decompressors = {
            CompressionType.ZLIB: __import__('zlib').decompress,
            CompressionType.GZIP: __import__('gzip').decompress
        }
        
        # 压缩统计
        self.compression_stats = {
            'original_size': 0,
            'compressed_size': 0,
            'compression_count': 0,
            'saved_bytes': 0,
            'compression_ratio': 1.0
        }
        self.stats_lock = threading.Lock()
    
    def compress_message(self, message: Union[str, bytes]) -> bytes:
        """压缩消息"""
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # 检查是否需要压缩
        if len(message) < self.min_size:
            return message
        
        original_size = len(message)
        
        try:
            if self.compression_type in self._compressors:
                compressed_data = self._compressors[self.compression_type](message)
                
                with self.stats_lock:
                    self.compression_stats['original_size'] += original_size
                    self.compression_stats['compressed_size'] += len(compressed_data)
                    self.compression_stats['compression_count'] += 1
                    self.compression_stats['saved_bytes'] += (original_size - len(compressed_data))
                    
                    # 更新压缩比
                    if self.compression_stats['compressed_size'] > 0:
                        self.compression_stats['compression_ratio'] = (
                            self.compression_stats['original_size'] / 
                            self.compression_stats['compressed_size']
                        )
                
                return compressed_data
            else:
                return message
                
        except Exception as e:
            logger.error(f"消息压缩失败: {e}")
            return message
    
    def decompress_message(self, compressed_data: bytes, 
                          original_type: str = 'utf-8') -> str:
        """解压缩消息"""
        try:
            if self.compression_type in self._decompressors:
                decompressed_data = self._decompressors[self.compression_type](
                    compressed_data
                )
                return decompressed_data.decode(original_type)
            else:
                # 假设数据未经压缩
                return compressed_data.decode(original_type)
                
        except Exception as e:
            logger.error(f"消息解压缩失败: {e}")
            # 尝试直接解码
            try:
                return compressed_data.decode(original_type)
            except:
                return str(compressed_data)
    
    def get_compression_efficiency(self) -> Dict[str, Any]:
        """获取压缩效率统计"""
        with self.stats_lock:
            stats = self.compression_stats.copy()
        
        if stats['compression_count'] > 0:
            stats['avg_compression_ratio'] = stats['compression_ratio']
            stats['compression_rate'] = (
                stats['compression_count'] / 
                max(1, stats['original_size'] // self.min_size)
            )
        
        return stats


class CompressedProducer:
    """压缩生产者"""
    
    def __init__(self, channel: pika.channel.Channel, 
                 compressor: MessageCompressor):
        self.channel = channel
        self.compressor = compressor
        self.produced_messages = 0
    
    def publish_compressed(self, exchange: str, routing_key: str, 
                          message: Union[str, bytes]) -> bool:
        """发布压缩消息"""
        try:
            # 决定是否压缩
            message_size = len(message) if isinstance(message, str) else len(message)
            
            if message_size >= self.compressor.min_size:
                # 压缩消息
                compressed_message = self.compressor.compress_message(message)
                
                # 设置压缩属性
                properties = pika.BasicProperties(
                    content_type='application/json' if isinstance(message, str) else 'application/octet-stream',
                    headers={
                        'compression': self.compressor.compression_type.value,
                        'original_size': message_size,
                        'compressed_size': len(compressed_message)
                    }
                )
                
                body_to_send = compressed_message
            else:
                # 不压缩
                body_to_send = message
                properties = pika.BasicProperties(
                    content_type='application/json' if isinstance(message, str) else 'application/octet-stream',
                    headers={'compression': 'none'}
                )
            
            # 发布消息
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body_to_send,
                properties=properties,
                mandatory=True
            )
            
            self.produced_messages += 1
            return True
            
        except Exception as e:
            logger.error(f"发布压缩消息失败: {e}")
            return False


class CompressedConsumer:
    """压缩消费者"""
    
    def __init__(self, channel: pika.channel.Channel, 
                 compressor: MessageCompressor):
        self.channel = channel
        self.compressor = compressor
        self.consumed_messages = 0
    
    def start_consumption(self, queue: str, callback: Callable) -> None:
        """开始消费压缩消息"""
        def process_compressed_message(ch, method, properties, body):
            try:
                # 检查压缩头
                compression = properties.headers.get('compression', 'none')
                
                if compression != 'none':
                    # 设置正确的压缩类型
                    original_type = self.compressor.compression_type
                    self.compressor.compression_type = CompressionType(compression)
                    
                    # 解压缩消息
                    decompressed_message = self.compressor.decompress_message(body)
                    
                    # 恢复原始压缩类型
                    self.compressor.compression_type = original_type
                else:
                    # 不需要解压缩
                    decompressed_message = body.decode('utf-8') if isinstance(body, bytes) else body
                
                # 调用原始回调
                callback(ch, method, properties, decompressed_message)
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"处理压缩消息失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # 开始消费
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=process_compressed_message,
            auto_ack=False
        )
        
        self.channel.start_consuming()


# =============================================================================
# 5. 系统资源优化
# =============================================================================

class SystemOptimizer:
    """系统资源优化器"""
    
    def __init__(self):
        self.optimization_rules = {
            'network': self._optimize_network_settings,
            'memory': self._optimize_memory_settings,
            'io': self._optimize_io_settings,
            'cpu': self._optimize_cpu_settings
        }
    
    def optimize_all(self) -> Dict[str, Any]:
        """优化所有系统设置"""
        results = {}
        
        for category, optimization_func in self.optimization_rules.items():
            try:
                result = optimization_func()
                results[category] = result
                logger.info(f"{category} 优化完成")
            except Exception as e:
                logger.error(f"{category} 优化失败: {e}")
                results[category] = {'error': str(e)}
        
        return results
    
    def _optimize_network_settings(self) -> Dict[str, Any]:
        """优化网络设置"""
        optimizations = {}
        
        try:
            # 读取当前网络配置
            with open('/proc/sys/net/core/rmem_max', 'r') as f:
                current_rmem = int(f.read().strip())
            
            with open('/proc/sys/net/core/wmem_max', 'r') as f:
                current_wmem = int(f.read().strip())
            
            # 设置优化的网络参数
            optimized_values = {
                'net.core.rmem_max': 16777216,  # 16MB
                'net.core.wmem_max': 16777216,  # 16MB
                'net.ipv4.tcp_rmem': '4096 65536 16777216',
                'net.ipv4.tcp_wmem': '4096 65536 16777216',
                'net.core.netdev_max_backlog': 5000,
                'net.ipv4.tcp_congestion_control': 'bbr'
            }
            
            for param, value in optimized_values.items():
                try:
                    # 使用sysctl设置参数（需要管理员权限）
                    cmd = f"sysctl -w {param}={value}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    optimizations[param] = {
                        'status': 'success' if result.returncode == 0 else 'failed',
                        'output': result.stdout.strip(),
                        'error': result.stderr.strip() if result.stderr else None
                    }
                except Exception as e:
                    optimizations[param] = {'status': 'error', 'error': str(e)}
            
            # 检查是否需要管理员权限
            if os.geteuid() != 0:
                optimizations['permission'] = '需要管理员权限进行网络优化'
            
        except Exception as e:
            optimizations['error'] = f"网络优化失败: {e}"
        
        return optimizations
    
    def _optimize_memory_settings(self) -> Dict[str, Any]:
        """优化内存设置"""
        optimizations = {}
        
        try:
            # 获取系统内存信息
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024**3)
            
            # 计算RabbitMQ内存限制
            rabbitmq_memory_limit = int(total_memory_gb * 0.6)  # 使用60%内存
            
            optimizations['system_memory'] = {
                'total_gb': round(total_memory_gb, 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'rabbitmq_suggested_limit_gb': rabbitmq_memory_limit
            }
            
            # 内存优化参数
            memory_optimizations = {
                'vm.swappiness': 1,                    # 减少swap使用
                'vm.dirty_ratio': 15,                  # 脏页比例
                'vm.dirty_background_ratio': 5,        # 后台脏页比例
                'vm.overcommit_memory': 1              # 内存分配策略
            }
            
            for param, value in memory_optimizations.items():
                try:
                    cmd = f"sysctl -w {param}={value}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    optimizations[f'memory_{param}'] = {
                        'status': 'success' if result.returncode == 0 else 'failed'
                    }
                except Exception as e:
                    optimizations[f'memory_{param}'] = {'status': 'error', 'error': str(e)}
            
        except Exception as e:
            optimizations['error'] = f"内存优化失败: {e}"
        
        return optimizations
    
    def _optimize_io_settings(self) -> Dict[str, Any]:
        """优化I/O设置"""
        optimizations = {}
        
        try:
            # 检查磁盘I/O性能
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            optimizations['disk_info'] = {
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'used_gb': round(disk_usage.used / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 2)
            }
            
            if disk_io:
                optimizations['disk_io'] = {
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count
                }
            
            # I/O调度器优化（需要管理员权限）
            if os.geteuid() == 0:
                try:
                    # 设置deadline调度器（适合数据库工作负载）
                    scheduler_cmd = "echo deadline > /sys/block/sda/queue/scheduler"
                    result = subprocess.run(scheduler_cmd, shell=True, capture_output=True)
                    optimizations['scheduler'] = {
                        'status': 'success' if result.returncode == 0 else 'failed'
                    }
                except Exception as e:
                    optimizations['scheduler'] = {'status': 'error', 'error': str(e)}
            
        except Exception as e:
            optimizations['error'] = f"I/O优化失败: {e}"
        
        return optimizations
    
    def _optimize_cpu_settings(self) -> Dict[str, Any]:
        """优化CPU设置"""
        optimizations = {}
        
        try:
            # CPU信息
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            optimizations['cpu_info'] = {
                'cores': cpu_count,
                'max_frequency_mhz': cpu_freq.max if cpu_freq else 'unknown',
                'min_frequency_mhz': cpu_freq.min if cpu_freq else 'unknown',
                'current_frequency_mhz': cpu_freq.current if cpu_freq else 'unknown'
            }
            
            # 建议的工作线程数
            suggested_threads = max(8, cpu_count * 2)
            optimizations['suggested_settings'] = {
                'rabbitmq_A_parameter': suggested_threads,
                'description': 'Erlang虚拟机工作线程数建议'
            }
            
            # CPU亲和性建议
            optimizations['affinity_suggestion'] = {
                'command': f'taskset -cp 0-{cpu_count-1} $RABBITMQ_BEAM_PID',
                'description': '设置RabbitMQ进程CPU亲和性'
            }
            
        except Exception as e:
            optimizations['error'] = f"CPU优化失败: {e}"
        
        return optimizations


# =============================================================================
# 6. 性能基准测试
# =============================================================================

class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.benchmark_results = {}
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """运行综合性能基准测试"""
        logger.info("开始综合性能基准测试")
        
        results = {
            'start_time': time.time(),
            'tests': {}
        }
        
        # 1. 吞吐量基准测试
        logger.info("运行吞吐量基准测试")
        results['tests']['throughput'] = self._benchmark_throughput()
        
        # 2. 延迟基准测试
        logger.info("运行延迟基准测试")
        results['tests']['latency'] = self._benchmark_latency()
        
        # 3. 连接基准测试
        logger.info("运行连接基准测试")
        results['tests']['connection'] = self._benchmark_connection()
        
        # 4. 内存使用基准测试
        logger.info("运行内存使用基准测试")
        results['tests']['memory'] = self._benchmark_memory_usage()
        
        results['end_time'] = time.time()
        results['total_duration'] = results['end_time'] - results['start_time']
        
        self.benchmark_results = results
        return results
    
    def _benchmark_throughput(self) -> Dict[str, Any]:
        """吞吐量基准测试"""
        config = self.config.copy()
        config['message_size'] = 1024  # 1KB消息
        
        # 性能测试配置
        test_configs = [
            {'duration': 30, 'concurrent_producers': 1, 'batch_size': 1},
            {'duration': 30, 'concurrent_producers': 5, 'batch_size': 10},
            {'duration': 30, 'concurrent_producers': 10, 'batch_size': 50},
        ]
        
        results = {}
        
        for i, test_config in enumerate(test_configs):
            logger.info(f"运行吞吐量测试 {i+1}/{len(test_configs)}: {test_config}")
            
            test_result = self._run_throughput_test(test_config)
            results[f'test_{i+1}'] = test_result
        
        return results
    
    def _run_throughput_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个吞吐量测试"""
        duration = config['duration']
        concurrent_producers = config['concurrent_producers']
        batch_size = config['batch_size']
        
        # 创建连接池
        connection_pool = IntelligentConnectionPool(
            ConnectionConfig(**{
                'host': self.config.get('host', 'localhost'),
                'port': self.config.get('port', 5672),
                'username': self.config.get('username', 'guest'),
                'password': self.config.get('password', 'guest')
            }),
            max_size=concurrent_producers + 5
        )
        
        # 生产者线程函数
        def producer_thread(thread_id):
            connection = connection_pool.get_connection()
            if not connection:
                return {'thread_id': thread_id, 'error': '无法获取连接'}
            
            try:
                channel = connection.channel()
                
                # 创建专用队列
                queue_name = f'perf_test_queue_{thread_id}'
                channel.queue_declare(queue=queue_name, durable=False, auto_delete=True)
                
                # 批量生产者
                batch_producer = BatchProducer(channel, batch_size=batch_size)
                
                messages_sent = 0
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    message = f'性能测试消息 {thread_id} {messages_sent} ' + 'x' * (self.config.get('message_size', 1024) - 50)
                    
                    batch_producer.publish_batch(
                        exchange='',
                        routing_key=queue_name,
                        message=message
                    )
                    
                    messages_sent += batch_size
                
                # 发送剩余消息
                batch_producer.flush_remaining()
                
                return {
                    'thread_id': thread_id,
                    'messages_sent': messages_sent,
                    'duration': time.time() - start_time
                }
                
            except Exception as e:
                return {'thread_id': thread_id, 'error': str(e)}
            finally:
                connection_pool.return_connection(connection)
        
        # 运行并发生产者
        with ThreadPoolExecutor(max_workers=concurrent_producers) as executor:
            futures = [executor.submit(producer_thread, i) for i in range(concurrent_producers)]
            
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 分析结果
        total_messages = sum(r.get('messages_sent', 0) for r in results)
        total_duration = max(r.get('duration', 0) for r in results)
        
        messages_per_second = total_messages / total_duration if total_duration > 0 else 0
        
        return {
            'concurrent_producers': concurrent_producers,
            'batch_size': batch_size,
            'total_messages': total_messages,
            'total_duration': total_duration,
            'messages_per_second': messages_per_second,
            'individual_results': results
        }
    
    def _benchmark_latency(self) -> Dict[str, Any]:
        """延迟基准测试"""
        connection_pool = IntelligentConnectionPool(
            ConnectionConfig(**{
                'host': self.config.get('host', 'localhost'),
                'port': self.config.get('port', 5672),
                'username': self.config.get('username', 'guest'),
                'password': self.config.get('password', 'guest')
            }),
            max_size=10
        )
        
        connection = connection_pool.get_connection()
        if not connection:
            return {'error': '无法获取连接'}
        
        try:
            channel = connection.channel()
            
            # 创建专用队列
            queue_name = 'latency_test_queue'
            channel.queue_declare(queue=queue_name, durable=False, auto_delete=True)
            
            # 延迟测试：发送并接收1000条消息
            latencies = []
            test_message = '延迟测试消息 ' + 'x' * 1000  # 1KB消息
            
            for i in range(1000):
                # 发送消息并记录时间
                send_time = time.time()
                
                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=f"{send_time}:{i}:{test_message}"
                )
                
                # 接收消息并计算延迟
                method_frame, header_frame, body = channel.basic_get(
                    queue=queue_name,
                    auto_ack=True
                )
                
                if method_frame:
                    receive_time = time.time()
                    latency = (receive_time - float(body.split(b':')[0])) * 1000  # 毫秒
                    latencies.append(latency)
                else:
                    logger.warning(f"延迟测试：第{i}条消息接收失败")
            
            # 计算延迟统计
            if latencies:
                latencies.sort()
                n = len(latencies)
                
                return {
                    'sample_count': len(latencies),
                    'min_latency_ms': latencies[0],
                    'max_latency_ms': latencies[-1],
                    'avg_latency_ms': statistics.mean(latencies),
                    'median_latency_ms': statistics.median(latencies),
                    'p95_latency_ms': latencies[int(n * 0.95)],
                    'p99_latency_ms': latencies[int(n * 0.99)],
                    'stddev_latency_ms': statistics.stdev(latencies) if n > 1 else 0
                }
            else:
                return {'error': '延迟测试失败：未接收到任何消息'}
                
        except Exception as e:
            return {'error': f'延迟测试失败: {e}'}
        finally:
            connection_pool.return_connection(connection)
    
    def _benchmark_connection(self) -> Dict[str, Any]:
        """连接基准测试"""
        results = {}
        
        # 测试大量并发连接
        max_connections = 1000
        connection_pool = IntelligentConnectionPool(
            ConnectionConfig(**{
                'host': self.config.get('host', 'localhost'),
                'port': self.config.get('port', 5672),
                'username': self.config.get('username', 'guest'),
                'password': self.config.get('password', 'guest')
            }),
            max_size=max_connections
        )
        
        connections_created = 0
        start_time = time.time()
        connection_errors = []
        
        # 尝试创建大量连接
        for i in range(max_connections):
            connection = connection_pool.get_connection()
            if connection:
                connections_created += 1
                # 立即归还连接以测试连接复用
                connection_pool.return_connection(connection)
            else:
                connection_errors.append(f'连接 {i} 创建失败')
        
        creation_time = time.time() - start_time
        
        # 获取连接池统计
        pool_stats = connection_pool.get_pool_stats()
        
        results['connection_creation'] = {
            'max_connections': max_connections,
            'connections_created': connections_created,
            'creation_time_seconds': creation_time,
            'connections_per_second': connections_created / creation_time if creation_time > 0 else 0,
            'creation_success_rate': connections_created / max_connections,
            'errors': connection_errors[:10]  # 只记录前10个错误
        }
        
        results['pool_stats'] = pool_stats
        
        return results
    
    def _benchmark_memory_usage(self) -> Dict[str, Any]:
        """内存使用基准测试"""
        # 监控内存使用情况
        memory_before = psutil.virtual_memory()
        
        # 创建大量连接和通道进行压力测试
        connection_pool = IntelligentConnectionPool(
            ConnectionConfig(**{
                'host': self.config.get('host', 'localhost'),
                'port': self.config.get('port', 5672),
                'username': self.config.get('username', 'guest'),
                'password': self.config.get('password', 'guest')
            }),
            max_size=100
        )
        
        # 创建连接
        connections = []
        for i in range(50):
            connection = connection_pool.get_connection()
            if connection:
                connections.append(connection)
        
        memory_during = psutil.virtual_memory()
        
        # 创建通道
        channels = []
        for connection in connections:
            try:
                channel = connection.channel()
                channels.append(channel)
            except Exception as e:
                logger.error(f"创建通道失败: {e}")
        
        memory_after_channels = psutil.virtual_memory()
        
        # 清理
        for connection in connections:
            connection_pool.return_connection(connection)
        
        memory_after_cleanup = psutil.virtual_memory()
        
        results = {
            'memory_before_test': {
                'total_gb': round(memory_before.total / (1024**3), 2),
                'available_gb': round(memory_before.available / (1024**3), 2),
                'used_percent': memory_before.percent
            },
            'memory_after_connections': {
                'total_gb': round(memory_during.total / (1024**3), 2),
                'available_gb': round(memory_during.available / (1024**3), 2),
                'used_percent': memory_during.percent,
                'memory_increase': round((memory_before.available - memory_during.available) / (1024**2), 2)
            },
            'memory_after_channels': {
                'total_gb': round(memory_after_channels.total / (1024**3), 2),
                'available_gb': round(memory_after_channels.available / (1024**3), 2),
                'used_percent': memory_after_channels.percent,
                'additional_memory_increase': round((memory_during.available - memory_after_channels.available) / (1024**2), 2)
            },
            'memory_after_cleanup': {
                'total_gb': round(memory_after_cleanup.total / (1024**3), 2),
                'available_gb': round(memory_after_cleanup.available / (1024**3), 2),
                'used_percent': memory_after_cleanup.percent,
                'memory_freed': round((memory_after_channels.available - memory_after_cleanup.available) / (1024**2), 2)
            },
            'test_summary': {
                'connections_created': len(connections),
                'channels_created': len(channels),
                'memory_leak_detected': memory_after_cleanup.available < memory_before.available
            }
        }
        
        return results
    
    def generate_report(self) -> str:
        """生成性能测试报告"""
        if not self.benchmark_results:
            return "暂无性能测试结果"
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("RabbitMQ 性能基准测试报告")
        report_lines.append("=" * 60)
        report_lines.append(f"测试时间: {datetime.fromtimestamp(self.benchmark_results['start_time']).strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"总耗时: {self.benchmark_results['total_duration']:.2f} 秒")
        report_lines.append("")
        
        # 吞吐量测试结果
        throughput_results = self.benchmark_results['tests'].get('throughput', {})
        if throughput_results:
            report_lines.append("1. 吞吐量测试结果:")
            report_lines.append("-" * 30)
            
            for test_name, test_result in throughput_results.items():
                if isinstance(test_result, dict) and 'messages_per_second' in test_result:
                    report_lines.append(f"{test_name}:")
                    report_lines.append(f"  并发生产者数: {test_result['concurrent_producers']}")
                    report_lines.append(f"  批处理大小: {test_result['batch_size']}")
                    report_lines.append(f"  发送消息总数: {test_result['total_messages']:,}")
                    report_lines.append(f"  吞吐量: {test_result['messages_per_second']:,.2f} 消息/秒")
                    report_lines.append("")
        
        # 延迟测试结果
        latency_results = self.benchmark_results['tests'].get('latency', {})
        if latency_results and 'avg_latency_ms' in latency_results:
            report_lines.append("2. 延迟测试结果:")
            report_lines.append("-" * 30)
            report_lines.append(f"  样本数量: {latency_results['sample_count']}")
            report_lines.append(f"  平均延迟: {latency_results['avg_latency_ms']:.2f} 毫秒")
            report_lines.append(f"  最小延迟: {latency_results['min_latency_ms']:.2f} 毫秒")
            report_lines.append(f"  最大延迟: {latency_results['max_latency_ms']:.2f} 毫秒")
            report_lines.append(f"  P95延迟: {latency_results['p95_latency_ms']:.2f} 毫秒")
            report_lines.append(f"  P99延迟: {latency_results['p99_latency_ms']:.2f} 毫秒")
            report_lines.append("")
        
        # 连接测试结果
        connection_results = self.benchmark_results['tests'].get('connection', {})
        if connection_results and 'connection_creation' in connection_results:
            conn_data = connection_results['connection_creation']
            report_lines.append("3. 连接测试结果:")
            report_lines.append("-" * 30)
            report_lines.append(f"  最大连接数: {conn_data['max_connections']}")
            report_lines.append(f"  成功创建连接: {conn_data['connections_created']}")
            report_lines.append(f"  连接创建速度: {conn_data['connections_per_second']:.2f} 连接/秒")
            report_lines.append(f"  创建成功率: {conn_data['creation_success_rate']*100:.2f}%")
            report_lines.append("")
        
        # 内存测试结果
        memory_results = self.benchmark_results['tests'].get('memory', {})
        if memory_results:
            report_lines.append("4. 内存使用测试结果:")
            report_lines.append("-" * 30)
            summary = memory_results.get('test_summary', {})
            report_lines.append(f"  连接创建: {summary.get('connections_created', 0)}")
            report_lines.append(f"  通道创建: {summary.get('channels_created', 0)}")
            
            memory_before = memory_results.get('memory_before_test', {})
            memory_after = memory_results.get('memory_after_cleanup', {})
            
            if memory_before and memory_after:
                memory_leaked = summary.get('memory_leak_detected', False)
                status = "检测到内存泄漏" if memory_leaked else "无内存泄漏"
                report_lines.append(f"  内存状态: {status}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        report_lines.append("建议和优化:")
        report_lines.append("-" * 30)
        
        # 根据测试结果给出建议
        if throughput_results:
            best_throughput = max(
                (r for r in throughput_results.values() if isinstance(r, dict) and 'messages_per_second' in r),
                key=lambda x: x['messages_per_second'],
                default=None
            )
            if best_throughput:
                report_lines.append(f"• 最佳吞吐量配置: 并发生产者 {best_throughput['concurrent_producers']}, 批处理大小 {best_throughput['batch_size']}")
        
        if latency_results and latency_results.get('avg_latency_ms', 0) > 100:
            report_lines.append("• 延迟较高，建议优化网络配置和队列设置")
        
        if memory_results and memory_results.get('test_summary', {}).get('memory_leak_detected', False):
            report_lines.append("• 检测到内存泄漏，建议检查连接和通道管理")
        
        report_lines.append("• 建议定期运行性能基准测试以监控系统性能")
        
        return "\n".join(report_lines)


# =============================================================================
# 7. 主要优化函数示例
# =============================================================================

def create_optimized_producer(config: Dict[str, Any]) -> Callable[[str, str, Union[str, bytes]], bool]:
    """创建优化的生产者"""
    
    def optimized_publish(exchange: str, routing_key: str, message: Union[str, bytes]) -> bool:
        """优化的发布函数"""
        try:
            # 1. 使用智能连接池
            connection_pool = IntelligentConnectionPool(
                ConnectionConfig(**{
                    'host': config.get('host', 'localhost'),
                    'port': config.get('port', 5672),
                    'username': config.get('username', 'guest'),
                    'password': config.get('password', 'guest')
                }),
                max_size=20
            )
            
            # 2. 获取连接
            connection = connection_pool.get_connection()
            if not connection:
                logger.error("无法获取连接")
                return False
            
            # 3. 使用批量处理
            channel = connection.channel()
            batch_producer = BatchProducer(channel, batch_size=50)
            
            # 4. 使用消息压缩
            compressor = MessageCompressor(
                compression_type=CompressionType.GZIP,
                min_size_for_compression=1024
            )
            
            compressed_message = compressor.compress_message(message)
            
            # 5. 发布消息
            properties = pika.BasicProperties(
                content_type='application/json' if isinstance(message, str) else 'application/octet-stream',
                headers={'compression': compressor.compression_type.value}
            )
            
            batch_producer.publish_batch(exchange, routing_key, compressed_message, properties)
            batch_producer.flush_remaining()
            
            # 6. 归还连接
            connection_pool.return_connection(connection)
            
            return True
            
        except Exception as e:
            logger.error(f"优化发布失败: {e}")
            return False
    
    return optimized_publish


def create_optimized_consumer(config: Dict[str, Any], queue_name: str, message_handler: Callable) -> None:
    """创建优化的消费者"""
    
    try:
        # 1. 使用智能连接池
        connection_pool = IntelligentConnectionPool(
            ConnectionConfig(**{
                'host': config.get('host', 'localhost'),
                'port': config.get('port', 5672),
                'username': config.get('username', 'guest'),
                'password': config.get('password', 'guest')
            }),
            max_size=10
        )
        
        # 2. 获取连接
        connection = connection_pool.get_connection()
        if not connection:
            logger.error("无法获取连接")
            return
        
        # 3. 使用批量消费
        channel = connection.channel()
        batch_consumer = BatchConsumer(channel, queue_name, batch_size=20)
        
        # 4. 创建压缩消费者
        compressor = MessageCompressor()
        compressed_consumer = CompressedConsumer(channel, compressor)
        
        # 5. 定义消息处理函数
        def batch_message_handler(messages: List[Dict[str, Any]]):
            """批量消息处理器"""
            for msg in messages:
                try:
                    # 解压缩消息
                    body = msg['body']
                    if isinstance(body, bytes):
                        decompressed_message = compressor.decompress_message(body)
                        message_handler(decompressed_message)
                    else:
                        message_handler(body)
                        
                except Exception as e:
                    logger.error(f"处理消息失败: {e}")
        
        # 6. 开始消费
        batch_consumer.start_batch_consumption(batch_message_handler)
        
    except Exception as e:
        logger.error(f"优化消费者创建失败: {e}")


def run_performance_optimization_demo():
    """运行性能优化演示"""
    print("RabbitMQ 性能优化与调优演示")
    print("=" * 50)
    
    # RabbitMQ连接配置
    rabbitmq_config = {
        'host': 'localhost',
        'port': 5672,
        'username': 'guest',
        'password': 'guest'
    }
    
    try:
        # 1. 系统优化
        print("1. 执行系统资源优化...")
        system_optimizer = SystemOptimizer()
        optimization_results = system_optimizer.optimize_all()
        print("系统优化完成")
        
        # 2. 性能监控
        print("2. 启动性能监控...")
        monitor = PerformanceMonitor(rabbitmq_config)
        monitor.start_monitoring(interval=1.0)
        print("性能监控已启动")
        
        # 3. 运行基准测试
        print("3. 运行性能基准测试...")
        benchmark = PerformanceBenchmark(rabbitmq_config)
        benchmark_results = benchmark.run_comprehensive_benchmark()
        
        # 4. 生成测试报告
        report = benchmark.generate_report()
        print("\n性能测试报告:")
        print(report)
        
        # 5. 优化建议
        print("\n性能优化建议:")
        print("- 使用智能连接池管理连接")
        print("- 采用批量消息处理提高吞吐量")
        print("- 启用消息压缩减少网络带宽")
        print("- 定期监控性能指标")
        print("- 根据基准测试结果调整配置")
        
        # 停止监控
        print("\n停止性能监控...")
        monitor.stop_monitoring()
        
        print("\n性能优化演示完成!")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        print(f"演示失败: {e}")


if __name__ == "__main__":
    # 运行性能优化演示
    run_performance_optimization_demo()