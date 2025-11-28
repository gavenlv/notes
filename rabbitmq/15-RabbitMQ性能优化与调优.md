# 第15章：RabbitMQ性能优化与调优

## 章节概述

性能优化与调优是企业级RabbitMQ部署的关键环节。本章深入探讨RabbitMQ的性能优化策略、监控分析、基准测试和故障排查，为构建高性能、高可靠性的消息系统提供完整的技术指导。

## 目录

1. [性能优化基础概念](#性能优化基础概念)
2. [性能监控与分析](#性能监控与分析)
3. [系统资源优化](#系统资源优化)
4. [RabbitMQ服务器优化](#RabbitMQ服务器优化)
5. [客户端性能优化](#客户端性能优化)
6. [网络通信优化](#网络通信优化)
7. [存储和持久化优化](#存储和持久化优化)
8. [集群性能调优](#集群性能调优)
9. [基准测试与性能评估](#基准测试与性能评估)
10. [故障排查与性能诊断](#故障排查与性能诊断)
11. [生产环境最佳实践](#生产环境最佳实践)
12. [案例研究与优化经验](#案例研究与优化经验)

## 性能优化基础概念

### 1. 性能指标体系

**吞吐量指标**
- **消息生产速率**: producer.publish_rate (msg/sec)
- **消息消费速率**: consumer.deliver_rate (msg/sec)
- **队列消息积压**: queue.messages (pending messages)
- **交换机路由速率**: exchange.publish_rate (msg/sec)

**延迟指标**
- **端到端延迟**: e2e_latency (milliseconds)
- **队列等待时间**: queue.message_wait_time (milliseconds)
- **消息处理时间**: message.processing_time (milliseconds)
- **网络延迟**: network_latency (milliseconds)

**资源利用率**
- **CPU利用率**: system.cpu_utilization (percentage)
- **内存使用率**: system.memory_utilization (percentage)
- **磁盘I/O**: system.disk_io_ops (ops/sec)
- **网络带宽**: system.network_throughput (MB/sec)

**可用性指标**
- **连接数**: connections.active (count)
- **通道数**: channels.active (count)
- **队列数**: queues.total (count)
- **消费者数**: consumers.total (count)

### 2. 性能瓶颈识别

**常见性能瓶颈**
1. **内存瓶颈**: 消息堆积、内存泄漏、缓存命中率低
2. **CPU瓶颈**: 消息处理效率低、死锁争用、算法复杂度高
3. **I/O瓶颈**: 磁盘写入慢、网络带宽限制、数据库延迟
4. **网络瓶颈**: 高延迟、连接数限制、协议开销大
5. **队列瓶颈**: 队列过载、消费者不均衡、确认机制不当

**性能瓶颈诊断方法**
- **CPU分析**: 使用top、htop、perf等工具分析CPU使用
- **内存分析**: 使用free、vmstat、valgrind等工具分析内存
- **I/O分析**: 使用iostat、iotop等工具分析磁盘I/O
- **网络分析**: 使用netstat、tcpdump、iftop等工具分析网络

## 性能监控与分析

### 1. 内置监控指标

**队列监控**
```python
# 队列状态监控
import pika

def monitor_queue_performance():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # 获取队列统计信息
    queue_stats = channel.queue_declare('', exclusive=True, auto_delete=True)
    
    # 监控指标
    metrics = {
        'messages': queue_stats.method.message_count,
        'consumers': queue_stats.method.consumer_count,
        'timestamp': time.time()
    }
    
    return metrics
```

**连接和通道监控**
```python
# 连接池管理
class ConnectionPool:
    def __init__(self, host='localhost', max_connections=10):
        self.host = host
        self.max_connections = max_connections
        self.active_connections = []
        self.available_connections = []
        self.lock = threading.Lock()
    
    def get_connection(self):
        with self.lock:
            if self.available_connections:
                return self.available_connections.pop()
            elif len(self.active_connections) < self.max_connections:
                conn = self._create_connection()
                self.active_connections.append(conn)
                return conn
            else:
                return None
    
    def return_connection(self, connection):
        with self.lock:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
                self.available_connections.append(connection)
```

### 2. Prometheus监控集成

**指标收集器**
```python
from prometheus_client import Counter, Histogram, Gauge

# 定义监控指标
MESSAGE_PUBLISHED = Counter('rabbitmq_messages_published_total', 'Total published messages')
MESSAGE_CONSUMED = Counter('rabbitmq_messages_consumed_total', 'Total consumed messages')
MESSAGE_LATENCY = Histogram('rabbitmq_message_latency_seconds', 'Message processing latency')
QUEUE_SIZE = Gauge('rabbitmq_queue_size', 'Queue size')

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def record_message_published(self, exchange, routing_key, latency):
        MESSAGE_PUBLISHED.inc()
        if routing_key:
            queue_name = self._get_queue_for_routing_key(routing_key)
            QUEUE_SIZE.set(self._get_queue_size(queue_name))
        MESSAGE_LATENCY.observe(latency)
    
    def record_message_consumed(self, queue, processing_time):
        MESSAGE_CONSUMED.inc()
        QUEUE_SIZE.set(self._get_queue_size(queue))
    
    def _get_queue_for_routing_key(self, routing_key):
        # 根据路由键获取队列名
        return f"queue_{routing_key}"
    
    def _get_queue_size(self, queue_name):
        # 获取队列大小
        return len(self._get_queue_messages(queue_name))
```

**Grafana仪表板配置**
```json
{
  "dashboard": {
    "title": "RabbitMQ Performance Dashboard",
    "panels": [
      {
        "title": "Message Throughput",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(rabbitmq_messages_published_total[1m])",
            "legendFormat": "Published/sec"
          },
          {
            "expr": "rate(rabbitmq_messages_consumed_total[1m])",
            "legendFormat": "Consumed/sec"
          }
        ]
      },
      {
        "title": "Message Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(rabbitmq_message_latency_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Queue Sizes",
        "type": "graph",
        "targets": [
          {
            "expr": "rabbitmq_queue_size",
            "legendFormat": "{{queue}}"
          }
        ]
      }
    ]
  }
}
```

### 3. 性能分析工具

**延迟分析器**
```python
import statistics
import time
from datetime import datetime, timedelta

class LatencyAnalyzer:
    def __init__(self, window_size=1000):
        self.window_size = window_size
        self.latencies = []
        self.lock = threading.Lock()
    
    def record_latency(self, latency):
        with self.lock:
            self.latencies.append(latency)
            if len(self.latencies) > self.window_size:
                self.latencies.pop(0)
    
    def get_latency_stats(self):
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
    
    def detect_anomalies(self, threshold=2.0):
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
                        'deviation': abs(latency - mean) / stddev,
                        'timestamp': time.time()
                    })
        
        return anomalies
```

## 系统资源优化

### 1. 操作系统优化

**Linux内核参数调优**
```bash
# /etc/sysctl.conf
# 网络参数优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 12582912 16777216
net.ipv4.tcp_wmem = 4096 12582912 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# 文件描述符限制
fs.file-max = 2097152
fs.nr_open = 2097152

# 虚拟内存管理
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# 应用参数
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_syncookies = 1
```

**文件描述符优化**
```bash
# /etc/security/limits.conf
rabbitmq soft nofile 65536
rabbitmq hard nofile 65536
rabbitmq soft nproc 65536
rabbitmq hard nproc 65536
```

**RabbitMQ启动脚本优化**
```bash
#!/bin/bash
# /etc/systemd/system/rabbitmq-server.service

[Unit]
Description=RabbitMQ Server
After=network.target

[Service]
Type=notify
User=rabbitmq
Group=rabbitmq
WorkingDirectory=/var/lib/rabbitmq
ExecStart=/usr/lib/erlang/erts-12.2.1/bin/beam.smp \
  -W w \
  -K true \
  -A 64 \
  -P 1048576 \
  -t 600000 \
  -MBas ageffcbf \
  -MHas ageffcbf \
  -MBlmbcs 512 \
  -MHlmbcs 512 \
  -MMmcs 30 \
  -zdbbl 128000 \
  -setcookie ${COOKIE} \
  -rabbitmq_loglevel notice \
  -rabbitmq disk_free_limit 1GB \
  -rabbitmq memory_berkeleydb_overrides "{bdb, [{log_maxdir, 536870912}]}" \
  -kernel 'inet_dist_listen_min 45001' \
  -kernel 'inet_dist_listen_max 45100' \
  -shutdown_gracefully \
  -rabbitmq_amqp1_0_default_protocol \
  -rabbitmq_stomp default_user guest default_pass <%= @default_pass %>
LimitNOFILE=65536
LimitNPROC=65536
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. 内存管理优化

**内存分配策略**
```erlang
%% rabbitmq.config
[
  {kernel, [
    {inet_default_connect_options, [{nodelay, true}]},
    {inet_default_listen_options, [{nodelay, true}]}
  ]},
  {rabbit, [
    {disk_free_limit, 1000000000},  % 1GB
    {memory_relative_limit, 0.5},    % 使用50%内存
    {vm_memory_calculation_strategy, allocated},  % 内存计算策略
    {vm_memory_high_watermark, 0.6}  % 高水位标记
  ]},
  {rabbitmq_management, [
    {rates_mode, detailed}  % 详细监控模式
  ]}
].
```

**内存监控脚本**
```python
import psutil
import subprocess
import json

class MemoryOptimizer:
    def __init__(self):
        self.rabbit_process = None
        self.memory_threshold = 0.7  # 70%内存使用率
    
    def monitor_rabbitmq_memory(self):
        try:
            # 获取RabbitMQ进程
            rabbit_processes = [
                p for p in psutil.process_iter(['pid', 'name'])
                if 'beam' in p.info['name'] or 'rabbitmq' in p.info['name']
            ]
            
            memory_info = []
            for proc in rabbit_processes:
                try:
                    mem_info = proc.memory_info()
                    memory_percent = proc.memory_percent()
                    memory_info.append({
                        'pid': proc.pid,
                        'rss': mem_info.rss,
                        'vms': mem_info.vms,
                        'percent': memory_percent
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return memory_info
            
        except Exception as e:
            print(f"内存监控错误: {e}")
            return []
    
    def optimize_memory_settings(self):
        """优化内存设置"""
        # 获取系统总内存
        total_memory = psutil.virtual_memory().total
        
        # 计算RabbitMQ可用内存
        rabbit_memory_limit = int(total_memory * 0.6)  # 使用60%内存
        
        # 设置RabbitMQ内存限制
        memory_config = {
            'vm_memory_high_watermark': 0.6,
            'memory_berkeleydb_overrides': {
                'bdb': [
                    {'log_maxdir', rabbit_memory_limit // 4}
                ]
            }
        }
        
        return memory_config
    
    def check_memory_pressure(self):
        """检查内存压力"""
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            return {
                'pressure': 'high',
                'available_gb': memory.available / (1024**3),
                'percent_used': memory.percent
            }
        elif memory.percent > 60:
            return {
                'pressure': 'medium',
                'available_gb': memory.available / (1024**3),
                'percent_used': memory.percent
            }
        else:
            return {
                'pressure': 'low',
                'available_gb': memory.available / (1024**3),
                'percent_used': memory.percent
            }
```

### 3. CPU优化

**CPU亲和性设置**
```python
import psutil
import subprocess
import os

class CPUOptimizer:
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.rabbitmq_pids = []
    
    def set_rabbitmq_cpu_affinity(self, cpu_cores):
        """设置RabbitMQ进程CPU亲和性"""
        try:
            # 查找RabbitMQ进程
            for proc in psutil.process_iter(['pid', 'name']):
                if 'beam' in proc.info['name']:
                    self.rabbitmq_pids.append(proc.pid)
            
            # 设置CPU亲和性
            for pid in self.rabbitmq_pids:
                self._set_process_cpu_affinity(pid, cpu_cores)
                
        except Exception as e:
            print(f"设置CPU亲和性失败: {e}")
    
    def _set_process_cpu_affinity(self, pid, cpu_cores):
        """设置进程CPU亲和性"""
        # 获取当前CPU亲和性
        cmd = f"taskset -pc {','.join(map(str, cpu_cores))} {pid}"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"已设置进程 {pid} 的CPU亲和性为 {cpu_cores}")
        except subprocess.CalledProcessError as e:
            print(f"设置CPU亲和性失败: {e}")
    
    def optimize_rabbitmq_threads(self):
        """优化RabbitMQ线程数量"""
        # 根据CPU核心数设置工作线程数
        worker_threads = max(8, self.cpu_count * 2)
        
        # 获取当前RabbitMQ配置
        config = self._get_current_config()
        
        # 更新线程配置
        if '+A' not in config:
            config.append('+A 64')
        
        # 更新工作线程数
        config = [c for c in config if not c.startswith('+A')]
        config.append(f'+A {worker_threads}')
        
        return config
    
    def monitor_cpu_usage(self):
        """监控CPU使用情况"""
        cpu_stats = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            if 'beam' in proc.info['name']:
                try:
                    proc.cpu_percent(interval=1)
                    cpu_percent = proc.cpu_percent()
                    cpu_stats.append({
                        'pid': proc.pid,
                        'cpu_percent': cpu_percent
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        return cpu_stats
    
    def _get_current_config(self):
        """获取当前配置"""
        # 实际实现中需要读取RabbitMQ配置文件
        return []
```

## RabbitMQ服务器优化

### 1. 服务器配置优化

**核心参数调优**
```erlang
%% 优化的RabbitMQ配置文件
[
  {kernel, [
    {inet_default_connect_options, [
      {nodelay, true},
      {packet, raw},
      {buffer, 32},
      {header, 0}
    ]},
    {inet_default_listen_options, [
      {nodelay, true},
      {packet, raw},
      {buffer, 32}
    ]}
  ]},
  {rabbit, [
    % 内存和磁盘配置
    {disk_free_limit, 500000000},  % 500MB
    {vm_memory_high_watermark, 0.4},
    {memory_relative_limit, 1.0},
    
    % 连接和通道配置
    {connection_max, 32768},
    {channel_max, 131072},
    {heartbeat, 30},
    
    % 队列配置
    {queue_index_max_journal_entries, 32768},
    {vm_memory_calculation_strategy, allocated},
    
    % 网络配置
    {tcp_listen_options, [
      {backlog, 128},
      {linger, {true, 0}},
      {exit_on_close, false}
    ]},
    
    % 认证配置
    {auth_backends, [rabbit_auth_backend_ldap]},
    
    % 日志配置
    {log_levels, [
      {connection, warning},
      {mirroring, info},
      {management, none}
    ]}
  ]},
  {rabbitmq_management, [
    {rates_mode, detailed},
    {sample_retention_policies, [
      {global, [{60, 10}, {1800, 10}]},
      {basic, none},
      {detailed, 10}
    ]}
  ]},
  {rabbitmq_mnesia, [
    {dump_log_write_threshold, 50000},
    {extra_db_nodes, []}
  ]}
].
```

### 2. 队列优化策略

**高性能队列配置**
```python
class HighPerformanceQueue:
    def __init__(self, connection):
        self.connection = connection
        self.channel = None
    
    def declare_high_performance_queue(self, queue_name, durable=True):
        """声明高性能队列"""
        # 高性能队列配置
        arguments = {
            'x-message-ttl': 86400000,  % 24小时TTL
            'x-dead-letter-exchange': 'dlx',
            'x-dead-letter-routing-key': 'dead.letter',
            'x-max-length': 1000000,  % 最大消息数
            'x-max-length-bytes': 1073741824,  % 最大大小1GB
            'x-queue-mode': 'lazy',  % 懒加载模式
            'x-queue-type': 'classic'  % 经典队列类型
        }
        
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            arguments=arguments,
            auto_delete=False,
            exclusive=False
        )
        
        return queue_name
    
    def setup_lazy_queue(self, queue_name):
        """设置懒加载队列"""
        arguments = {
            'x-queue-type': 'lazy',
            'x-max-in-memory-length': 1000,  % 内存中保留1000条消息
            'x-max-in-memory-bytes': 67108864  % 64MB内存使用限制
        }
        
        return self.declare_high_performance_queue(queue_name)
    
    def setup_priority_queue(self, queue_name, priority_levels=10):
        """设置优先级队列"""
        arguments = {
            'x-max-priority': priority_levels,
            'x-queue-type': 'classic'
        }
        
        return self.declare_high_performance_queue(queue_name)
```

**队列均衡策略**
```python
class QueueBalancer:
    def __init__(self, connection):
        self.connection = connection
        self.channel = connection.channel()
    
    def distribute_queues_evenly(self, queue_prefix, queue_count, worker_nodes):
        """均衡分布队列到不同节点"""
        queues = []
        
        for i in range(queue_count):
            queue_name = f"{queue_prefix}.{i}"
            node_index = i % len(worker_nodes)
            target_node = worker_nodes[node_index]
            
            # 在目标节点创建队列
            self.channel.queue_declare(
                queue=queue_name,
                arguments={'x-rabbitmq-stream-accumulator': target_node}
            )
            
            queues.append({
                'name': queue_name,
                'node': target_node,
                'index': i
            })
        
        return queues
    
    def monitor_queue_load(self, queues):
        """监控队列负载"""
        queue_stats = {}
        
        for queue_info in queues:
            queue_name = queue_info['name']
            
            # 获取队列统计信息
            result = self.channel.queue_declare(
                queue_name, passive=True
            )
            
            queue_stats[queue_name] = {
                'messages': result.method.message_count,
                'consumers': result.method.consumer_count,
                'node': queue_info['node']
            }
        
        return queue_stats
    
    def rebalance_queues(self, queue_stats):
        """重新平衡队列负载"""
        # 计算每个节点的负载
        node_loads = {}
        for queue_name, stats in queue_stats.items():
            node = stats['node']
            if node not in node_loads:
                node_loads[node] = 0
            node_loads[node] += stats['messages']
        
        # 识别过载和轻载节点
        avg_load = sum(node_loads.values()) / len(node_loads)
        
        overloaded_nodes = [
            node for node, load in node_loads.items() 
            if load > avg_load * 1.5
        ]
        
        underloaded_nodes = [
            node for node, load in node_loads.items() 
            if load < avg_load * 0.5
        ]
        
        return {
            'overloaded': overloaded_nodes,
            'underloaded': underloaded_nodes,
            'avg_load': avg_load
        }
```

### 3. 交换机优化

**交换机类型选择**
```python
class ExchangeOptimizer:
    def __init__(self, connection):
        self.connection = connection
        self.channel = connection.channel()
    
    def optimize_exchange_configuration(self, exchange_patterns):
        """优化交换机配置"""
        optimized_exchanges = []
        
        for pattern in exchange_patterns:
            if self._is_high_volume_route(pattern):
                # 高吞吐量场景使用直接交换机
                exchange = self._create_direct_exchange(pattern)
            elif self._is_complex_routing(pattern):
                # 复杂路由使用主题交换机
                exchange = self._create_topic_exchange(pattern)
            else:
                # 默认使用扇形交换机
                exchange = self._create_fanout_exchange(pattern)
            
            optimized_exchanges.append(exchange)
        
        return optimized_exchanges
    
    def _create_direct_exchange(self, pattern):
        """创建直接交换机"""
        exchange_name = f"direct.{pattern}"
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='direct',
            durable=True,
            auto_delete=False
        )
        
        return {
            'name': exchange_name,
            'type': 'direct',
            'durable': True,
            'auto_delete': False
        }
    
    def _create_topic_exchange(self, pattern):
        """创建主题交换机"""
        exchange_name = f"topic.{pattern}"
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='topic',
            durable=True,
            auto_delete=False
        )
        
        return {
            'name': exchange_name,
            'type': 'topic',
            'durable': True,
            'auto_delete': False
        }
    
    def _create_fanout_exchange(self, pattern):
        """创建扇形交换机"""
        exchange_name = f"fanout.{pattern}"
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='fanout',
            durable=True,
            auto_delete=False
        )
        
        return {
            'name': exchange_name,
            'type': 'fanout',
            'durable': True,
            'auto_delete': False
        }
    
    def _is_high_volume_route(self, pattern):
        """判断是否为高吞吐量路由"""
        # 基于模式的性能评估
        high_volume_keywords = ['real-time', 'stream', 'batch']
        return any(keyword in pattern for keyword in high_volume_keywords)
    
    def _is_complex_routing(self, pattern):
        """判断是否为复杂路由"""
        # 基于模式的路由复杂度评估
        return '*' in pattern or '#' in pattern
```

## 客户端性能优化

### 1. 连接池管理

**智能连接池**
```python
import queue
import threading
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class ConnectionConfig:
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    virtual_host: str = '/'
    heartbeat: int = 30
    connection_timeout: int = 30
    blocked_connection_timeout: int = 300

class IntelligentConnectionPool:
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
            
            # 连接池已满，等待回收
            return self._wait_for_available_connection()
            
        except Exception as e:
            logging.error(f"获取连接失败: {e}")
            self.connection_stats['failed'] += 1
            return None
    
    def return_connection(self, connection: pika.BlockingConnection):
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
                    # 连接池已满，关闭连接
                    connection.close()
                    with self.lock:
                        self.connection_stats['closed'] += 1
            else:
                connection.close()
                with self.lock:
                    self.connection_stats['closed'] += 1
                    
        except Exception as e:
            logging.error(f"归还连接失败: {e}")
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
            logging.error(f"创建连接失败: {e}")
            return None
    
    def _is_connection_valid(self, connection: pika.BlockingConnection) -> bool:
        """检查连接有效性"""
        try:
            return (connection.is_open and 
                   connection._impl.is_baselayer_transport_tcp_socket_connected())
        except:
            return False
    
    def _wait_for_available_connection(self, timeout: float = 30.0) -> Optional[pika.BlockingConnection]:
        """等待可用连接"""
        try:
            return self.available_connections.get(timeout=timeout)
        except queue.Empty:
            logging.warning("等待连接超时")
            return None
    
    def cleanup_idle_connections(self, idle_timeout: int = 300):
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
    
    def get_pool_stats(self) -> Dict:
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
```

### 2. 批量消息处理

**批量生产者**
```python
class BatchProducer:
    def __init__(self, channel: pika.channel.Channel, 
                 batch_size: int = 100, 
                 flush_interval: float = 1.0):
        self.channel = channel
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending_messages = []
        self.last_flush_time = time.time()
        self.batch_stats = {
            'total_messages': 0,
            'total_batches': 0,
            'flush_count': 0,
            'average_batch_size': 0
        }
        self.lock = threading.Lock()
    
    def publish_batch(self, exchange: str, routing_key: str, 
                     message: bytes, properties: Optional[pika.spec.BasicProperties] = None):
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
                self._flush_batch()
    
    def _flush_batch(self):
        """批量发送消息"""
        if not self.pending_messages:
            return
        
        try:
            # 事务性批量发送
            self.channel.tx_select()
            
            for msg in self.pending_messages:
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
            self.batch_stats['total_batches'] += len(self.pending_messages)
            self.batch_stats['flush_count'] += 1
            self.batch_stats['average_batch_size'] = (
                self.batch_stats['total_messages'] / self.batch_stats['flush_count']
            )
            
        except Exception as e:
            # 回滚事务
            try:
                self.channel.tx_rollback()
            except:
                pass
            raise e
        finally:
            self.pending_messages.clear()
            self.last_flush_time = time.time()
    
    def flush_remaining(self):
        """强制发送剩余消息"""
        with self.lock:
            if self.pending_messages:
                self._flush_batch()
    
    def get_batch_stats(self) -> Dict:
        """获取批量处理统计信息"""
        with self.lock:
            return self.batch_stats.copy()
```

**批量消费者**
```python
class BatchConsumer:
    def __init__(self, channel: pika.channel.Channel, 
                 queue_name: str, 
                 batch_size: int = 50,
                 processing_timeout: float = 30.0):
        self.channel = channel
        self.queue_name = queue_name
        self.batch_size = batch_size
        self.processing_timeout = processing_timeout
        self.consumed_messages = []
        self.batch_stats = {
            'total_messages': 0,
            'total_batches': 0,
            'processing_time': 0,
            'throughput': 0
        }
        self.lock = threading.Lock()
        self.processing = False
    
    def start_batch_consumption(self, message_handler: callable):
        """开始批量消费"""
        self.processing = True
        
        while self.processing:
            try:
                # 批量获取消息
                messages = self._get_batch_messages()
                
                if messages:
                    start_time = time.time()
                    
                    # 处理消息批次
                    self._process_batch(messages, message_handler)
                    
                    processing_time = time.time() - start_time
                    
                    with self.lock:
                        self.batch_stats['total_messages'] += len(messages)
                        self.batch_stats['total_batches'] += 1
                        self.batch_stats['processing_time'] += processing_time
                        if self.batch_stats['total_batches'] > 0:
                            self.batch_stats['throughput'] = (
                                self.batch_stats['total_messages'] / 
                                self.batch_stats['processing_time']
                            )
                    
                else:
                    # 没有消息，等待一段时间
                    time.sleep(0.1)
                    
            except Exception as e:
                logging.error(f"批量消费错误: {e}")
                time.sleep(1)
    
    def _get_batch_messages(self) -> List[Dict]:
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
                logging.error(f"获取消息失败: {e}")
                break
        
        return messages
    
    def _process_batch(self, messages: List[Dict], message_handler: callable):
        """处理消息批次"""
        try:
            # 使用事务性处理
            self.channel.tx_select()
            
            # 调用消息处理器
            message_handler(messages)
            
            # 确认所有消息
            for msg in messages:
                self.channel.basic_ack(
                    delivery_tag=msg['delivery_tag'], 
                    multiple=True
                )
            
            # 提交事务
            self.channel.tx_commit()
            
        except Exception as e:
            # 回滚事务，消息将重新投递
            try:
                self.channel.tx_rollback()
            except:
                pass
            raise e
    
    def stop_consumption(self):
        """停止消费"""
        self.processing = False
    
    def get_consumption_stats(self) -> Dict:
        """获取消费统计信息"""
        with self.lock:
            return self.batch_stats.copy()
```

### 3. 异步处理优化

**异步生产者**
```python
import asyncio
import aio_pika
from typing import Callable, Optional

class AsyncBatchProducer:
    def __init__(self, connection_string: str, batch_size: int = 100):
        self.connection_string = connection_string
        self.batch_size = batch_size
        self.connection = None
        self.channel = None
        self.pending_messages = asyncio.Queue()
        self.producing = False
        self.producer_task = None
    
    async def start(self):
        """启动异步生产者"""
        self.connection = await aio_pika.connect_robust(self.connection_string)
        self.channel = await self.connection.channel()
        
        # 设置QoS
        await self.channel.set_qos(prefetch_count=0)
        
        self.producing = True
        self.producer_task = asyncio.create_task(self._produce_messages())
    
    async def publish(self, exchange: str, routing_key: str, 
                     message: str, properties: Optional[aio_pika.spec.Basic.Properties] = None):
        """发布消息"""
        await self.pending_messages.put({
            'exchange': exchange,
            'routing_key': routing_key,
            'message': message,
            'properties': properties,
            'timestamp': time.time()
        })
    
    async def _produce_messages(self):
        """异步消息生产循环"""
        batch = []
        
        while self.producing:
            try:
                # 批量获取消息
                try:
                    msg = await asyncio.wait_for(
                        self.pending_messages.get(), 
                        timeout=0.1
                    )
                    batch.append(msg)
                except asyncio.TimeoutError:
                    pass
                
                # 检查是否需要发送批次
                if batch and (
                    len(batch) >= self.batch_size or 
                    time.time() - (batch[0]['timestamp'] if batch else 0) > 1.0
                ):
                    await self._send_batch(batch)
                    batch.clear()
                
            except Exception as e:
                logging.error(f"异步生产错误: {e}")
                await asyncio.sleep(0.1)
        
        # 发送剩余消息
        if batch:
            await self._send_batch(batch)
    
    async def _send_batch(self, batch: List[Dict]):
        """批量发送消息"""
        try:
            # 使用事务性发送
            async with self.channel.transaction():
                for msg in batch:
                    await self.channel.default_exchange.publish(
                        aio_pika.Message(
                            msg['message'].encode(),
                            properties=msg['properties']
                        ),
                        routing_key=msg['routing_key']
                    )
        except Exception as e:
            logging.error(f"批量发送失败: {e}")
            raise
    
    async def stop(self):
        """停止生产者"""
        self.producing = False
        if self.producer_task:
            self.producer_task.cancel()
            try:
                await self.producer_task
            except asyncio.CancelledError:
                pass
        
        if self.channel:
            await self.channel.close()
        
        if self.connection:
            await self.connection.close()
```

## 网络通信优化

### 1. 连接优化配置

**网络参数调优**
```python
import socket
import ssl
from typing import Dict, Any

class NetworkOptimizer:
    def __init__(self):
        self.socket_options = {
            'TCP_NODELAY': True,      # 禁用Nagle算法
            'SO_KEEPALIVE': True,     # 启用Keep-Alive
            'SO_REUSEADDR': True,     # 端口复用
            'SO_LINGER': (1, 0),      # 快速关闭
            'SO_SNDBUF': 1048576,     # 发送缓冲区1MB
            'SO_RCVBUF': 1048576      # 接收缓冲区1MB
        }
        
        self.tcp_options = {
            'tcp_keepalive_idle': 600,    # 600秒后开始探测
            'tcp_keepalive_interval': 60, # 60秒探测间隔
            'tcp_keepalive_probes': 5     # 最多5次探测
        }
    
    def optimize_socket_settings(self, connection):
        """优化套接字设置"""
        try:
            # 获取底层socket
            if hasattr(connection, '_impl'):
                sock = connection._impl.socket
            elif hasattr(connection, 'socket'):
                sock = connection.socket
            else:
                return False
            
            # 设置套接字选项
            for option, value in self.socket_options.items():
                sock.setsockopt(socket.SOL_SOCKET, getattr(socket, option), value)
            
            # TCP Keep-Alive设置
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 
                           self.tcp_options['tcp_keepalive_idle'])
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 
                           self.tcp_options['tcp_keepalive_interval'])
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 
                           self.tcp_options['tcp_keepalive_probes'])
            
            return True
            
        except Exception as e:
            logging.error(f"优化套接字设置失败: {e}")
            return False
    
    def configure_ssl_optimization(self) -> Dict[str, Any]:
        """配置SSL优化"""
        ssl_context = ssl.create_default_context()
        
        # 启用会话缓存
        ssl_context.options |= ssl.OP_NO_TICKET
        
        # 优化密码套件选择
        ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        # 启用会话恢复
        ssl_context.session_cache_mode = ssl.SESS_CACHE_BOTH
        
        return ssl_context
    
    def analyze_network_performance(self) -> Dict[str, Any]:
        """分析网络性能"""
        import psutil
        
        # 获取网络接口统计
        net_stats = psutil.net_io_counters(pernic=True)
        
        performance_data = {}
        for interface, stats in net_stats.items():
            performance_data[interface] = {
                'bytes_sent_per_sec': stats.bytes_sent,
                'bytes_recv_per_sec': stats.bytes_recv,
                'packets_sent_per_sec': stats.packets_sent,
                'packets_recv_per_sec': stats.packets_recv,
                'errin': stats.errin,
                'errout': stats.errout,
                'dropin': stats.dropin,
                'dropout': stats.dropout
            }
        
        return performance_data
```

### 2. 压缩优化

**消息压缩策略**
```python
import zlib
import gzip
import json
import time
from typing import Union, Dict, Any
from enum import Enum

class CompressionType(Enum):
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    SNAPPY = "snappy"  # 需要安装python-snappy

class MessageCompressor:
    def __init__(self, compression_type: CompressionType = CompressionType.GZIP,
                 compression_level: int = 6, 
                 min_size_for_compression: int = 1024):
        self.compression_type = compression_type
        self.compression_level = compression_level
        self.min_size = min_size_for_compression
        
        # 预计算的压缩器
        self._compressors = {
            CompressionType.ZLIB: lambda data: zlib.compress(
                data, self.compression_level
            ),
            CompressionType.GZIP: lambda data: gzip.compress(
                data, self.compression_level
            )
        }
        
        self._decompressors = {
            CompressionType.ZLIB: zlib.decompress,
            CompressionType.GZIP: gzip.decompress
        }
        
        # 压缩统计
        self.compression_stats = {
            'original_size': 0,
            'compressed_size': 0,
            'compression_count': 0,
            'saved_bytes': 0,
            'compression_ratio': 0
        }
    
    def compress_message(self, message: Union[str, bytes]) -> bytes:
        """压缩消息"""
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # 检查是否需要压缩
        if len(message) < self.min_size:
            return message
        
        original_size = len(message)
        self.compression_stats['original_size'] += original_size
        
        try:
            if self.compression_type in self._compressors:
                compressed_data = self._compressors[self.compression_type](message)
                
                compressed_size = len(compressed_data)
                self.compression_stats['compressed_size'] += compressed_size
                self.compression_stats['compression_count'] += 1
                self.compression_stats['saved_bytes'] += (original_size - compressed_size)
                
                # 计算压缩比
                if self.compression_stats['compressed_size'] > 0:
                    self.compression_stats['compression_ratio'] = (
                        self.compression_stats['original_size'] / 
                        self.compression_stats['compressed_size']
                    )
                
                return compressed_data
            else:
                return message
                
        except Exception as e:
            logging.error(f"消息压缩失败: {e}")
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
            logging.error(f"消息解压缩失败: {e}")
            # 尝试直接解码
            try:
                return compressed_data.decode(original_type)
            except:
                return str(compressed_data)
    
    def get_compression_efficiency(self) -> Dict[str, Any]:
        """获取压缩效率统计"""
        stats = self.compression_stats.copy()
        
        if stats['compression_count'] > 0:
            stats['avg_compression_ratio'] = (
                stats['original_size'] / stats['compressed_size']
            ) if stats['compressed_size'] > 0 else 1.0
            
            stats['compression_rate'] = (
                stats['compression_count'] / 
                (stats['original_size'] / self.min_size)
            )
        
        return stats
    
    def adaptive_compression_enabled(self, message_size: int) -> bool:
        """自适应压缩启用判断"""
        if message_size < self.min_size:
            return False
        
        # 基于消息大小动态调整压缩策略
        if message_size > 1024 * 1024:  # 1MB以上
            return True
        elif message_size > 1024:  # 1KB以上
            return self.compression_type != CompressionType.NONE
        
        return False

class CompressedProducer:
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
            
            if self.compressor.adaptive_compression_enabled(message_size):
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
            else:
                # 不压缩
                compressed_message = message
                properties = pika.BasicProperties(
                    content_type='application/json' if isinstance(message, str) else 'application/octet-stream',
                    headers={'compression': 'none'}
                )
            
            # 发布消息
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=compressed_message,
                properties=properties,
                mandatory=True
            )
            
            self.produced_messages += 1
            return True
            
        except Exception as e:
            logging.error(f"发布压缩消息失败: {e}")
            return False

class CompressedConsumer:
    def __init__(self, channel: pika.channel.Channel, 
                 compressor: MessageCompressor):
        self.channel = channel
        self.compressor = compressor
        self.consumed_messages = 0
    
    def start_consumption(self, queue: str, callback: callable):
        """开始消费压缩消息"""
        def process_compressed_message(ch, method, properties, body):
            try:
                # 检查压缩头
                compression = properties.headers.get('compression', 'none')
                
                if compression != 'none':
                    # 设置正确的压缩类型
                    self.compressor.compression_type = CompressionType(compression)
                    
                    # 解压缩消息
                    decompressed_message = self.compressor.decompress_message(body)
                else:
                    # 不需要解压缩
                    decompressed_message = body.decode('utf-8') if isinstance(body, bytes) else body
                
                # 调用原始回调
                callback(ch, method, properties, decompressed_message)
                
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logging.error(f"处理压缩消息失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # 开始消费
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=process_compressed_message,
            auto_ack=False
        )
        
        self.channel.start_consuming()
```

## 存储和持久化优化

### 1. 磁盘I/O优化

**磁盘监控与优化**
```python
import os
import time
import psutil
from typing import Dict, List, Any

class DiskIOMonitor:
    def __init__(self, rabbitmq_data_dir: str):
        self.data_dir = rabbitmq_data_dir
        self.disk_stats = {
            'read_ops': 0,
            'write_ops': 0,
            'read_bytes': 0,
            'write_bytes': 0,
            'read_time': 0,
            'write_time': 0
        }
        self.last_check = time.time()
    
    def monitor_disk_performance(self) -> Dict[str, Any]:
        """监控磁盘性能"""
        try:
            # 获取磁盘使用情况
            disk_usage = psutil.disk_usage(self.data_dir)
            
            # 获取磁盘I/O统计
            disk_io = psutil.disk_io_counters()
            
            # 获取磁盘延迟
            disk_latency = self._measure_disk_latency()
            
            # 获取队列文件大小
            queue_files = self._analyze_queue_files()
            
            return {
                'disk_usage': {
                    'total_gb': disk_usage.total / (1024**3),
                    'used_gb': disk_usage.used / (1024**3),
                    'free_gb': disk_usage.free / (1024**3),
                    'usage_percent': (disk_usage.used / disk_usage.total) * 100
                },
                'disk_io': {
                    'read_ops': disk_io.read_count,
                    'write_ops': disk_io.write_count,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_time_ms': disk_io.read_time,
                    'write_time_ms': disk_io.write_time
                },
                'disk_latency': disk_latency,
                'queue_files': queue_files
            }
            
        except Exception as e:
            logging.error(f"磁盘性能监控失败: {e}")
            return {}
    
    def _measure_disk_latency(self, sample_count: int = 10) -> Dict[str, Any]:
        """测量磁盘延迟"""
        latencies = []
        
        for _ in range(sample_count):
            start_time = time.time()
            
            try:
                # 执行一个小的读写操作
                test_file = os.path.join(self.data_dir, '.latency_test')
                with open(test_file, 'wb') as f:
                    f.write(b'0' * 1024)  # 写入1KB
                
                with open(test_file, 'rb') as f:
                    f.read(1024)  # 读取1KB
                
                os.remove(test_file)
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # 转换为毫秒
                latencies.append(latency)
                
            except Exception:
                continue
        
        if latencies:
            return {
                'avg_latency_ms': sum(latencies) / len(latencies),
                'min_latency_ms': min(latencies),
                'max_latency_ms': max(latencies),
                'latency_samples': len(latencies)
            }
        else:
            return {'avg_latency_ms': 0, 'error': '无法测量延迟'}
    
    def _analyze_queue_files(self) -> Dict[str, Any]:
        """分析队列文件"""
        queue_files = []
        
        try:
            # 扫描数据目录下的队列文件
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    if file.endswith(('.idx', '.rdq', '.dvr')):
                        file_path = os.path.join(root, file)
                        stat_info = os.stat(file_path)
                        
                        queue_files.append({
                            'name': file,
                            'path': file_path,
                            'size_mb': stat_info.st_size / (1024**2),
                            'modified_time': stat_info.st_mtime
                        })
        except Exception as e:
            logging.error(f"分析队列文件失败: {e}")
        
        if queue_files:
            total_size = sum(f['size_mb'] for f in queue_files)
            return {
                'total_files': len(queue_files),
                'total_size_mb': total_size,
                'avg_file_size_mb': total_size / len(queue_files),
                'largest_files': sorted(queue_files, key=lambda x: x['size_mb'], reverse=True)[:5]
            }
        else:
            return {'total_files': 0, 'total_size_mb': 0}
    
    def optimize_disk_settings(self) -> Dict[str, str]:
        """优化磁盘设置"""
        optimizations = {}
        
        try:
            # 检查和设置I/O调度器
            current_scheduler = self._get_io_scheduler()
            if current_scheduler not in ['deadline', 'noop']:
                optimizations['scheduler'] = 'deadline'
                self._set_io_scheduler('deadline')
            
            # 检查和设置文件系统挂载选项
            mount_options = self._get_mount_options()
            if 'noatime' not in mount_options:
                optimizations['mount_options'] = '添加noatime选项'
                self._suggest_mount_options()
            
            # 检查文件预分配
            optimizations['preallocation'] = 'prealloc'
            
        except Exception as e:
            logging.error(f"磁盘优化失败: {e}")
        
        return optimizations
    
    def _get_io_scheduler(self) -> str:
        """获取当前I/O调度器"""
        try:
            with open('/sys/block/sda/queue/scheduler', 'r') as f:
                content = f.read().strip()
                # 提取当前启用的调度器
                for line in content.split('[')[1:]:
                    if ']' in line:
                        scheduler = line.split(']')[0]
                        return scheduler
        except:
            pass
        return 'unknown'
    
    def _set_io_scheduler(self, scheduler: str):
        """设置I/O调度器"""
        try:
            with open('/sys/block/sda/queue/scheduler', 'w') as f:
                f.write(scheduler)
        except Exception as e:
            logging.error(f"设置I/O调度器失败: {e}")
    
    def _get_mount_options(self) -> List[str]:
        """获取文件系统挂载选项"""
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    if self.data_dir in line:
                        options = line.split()[3]
                        return options.split(',')
        except:
            pass
        return []
    
    def _suggest_mount_options(self):
        """建议挂载选项优化"""
        suggestions = [
            "添加noatime选项：减少不必要的磁盘写入",
            "添加nodiratime选项：减少目录访问时间写入",
            "考虑使用SSD时：添加discard选项启用TRIM"
        ]
        logging.info("磁盘挂载优化建议: %s", suggestions)
```

### 2. 数据库优化

**Mnesia配置优化**
```erlang
%% 优化的Mnesia配置
[
  {mnesia, [
    {dc_dump_limit, 40},              % DC转储频率
    {dump_log_write_threshold, 50000}, % 日志转储阈值
    {dump_log_time_threshold, 60000},  % 日志转储时间阈值
    {extra_db_nodes, []},
    {schema_location, disc_copies},
    {snapshot_after_mnesia_dirty, true},
    {dirty_schedulers, 8},            % 脏数据调度器数量
    {dirty_schedulers_common_sup, true}
  ]},
  {rabbit, [
    % 队列索引优化
    {queue_index_max_journal_entries, 32768},
    {queue_index_embedded_content_overflow, 100000000},
    
    % 消息存储优化
    {msg_store_file_size_limit, 16777216},  % 16MB文件大小
    {msg_store_io_batch_size, 1024},        % I/O批处理大小
    
    % 数据库优化
    {mnesia_dir, "/var/lib/rabbitmq/mnesia"}
  ]}
].
```

**数据库监控脚本**
```python
class DatabaseOptimizer:
    def __init__(self, mnesia_dir: str):
        self.mnesia_dir = mnesia_dir
        self.db_stats = {}
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """分析数据库性能"""
        try:
            # 分析Mnesia表文件
            table_stats = self._analyze_mnesia_tables()
            
            # 分析事务日志
            log_stats = self._analyze_transaction_logs()
            
            # 分析数据库大小
            size_stats = self._analyze_database_size()
            
            # 分析查询性能
            query_stats = self._analyze_query_performance()
            
            return {
                'table_stats': table_stats,
                'log_stats': log_stats,
                'size_stats': size_stats,
                'query_stats': query_stats
            }
            
        except Exception as e:
            logging.error(f"数据库性能分析失败: {e}")
            return {}
    
    def _analyze_mnesia_tables(self) -> Dict[str, Any]:
        """分析Mnesia表"""
        tables = []
        
        try:
            # 扫描Mnesia目录下的表文件
            for file in os.listdir(self.mnesia_dir):
                if file.endswith('.DAT'):
                    table_name = file[:-4]  # 移除.DAT扩展名
                    file_path = os.path.join(self.mnesia_dir, file)
                    stat_info = os.stat(file_path)
                    
                    tables.append({
                        'name': table_name,
                        'size_mb': stat_info.st_size / (1024**2),
                        'records': self._estimate_table_records(table_name, stat_info.st_size)
                    })
        except Exception as e:
            logging.error(f"分析Mnesia表失败: {e}")
        
        if tables:
            total_size = sum(t['size_mb'] for t in tables)
            return {
                'total_tables': len(tables),
                'total_size_mb': total_size,
                'avg_table_size_mb': total_size / len(tables),
                'tables': sorted(tables, key=lambda x: x['size_mb'], reverse=True)
            }
        else:
            return {'total_tables': 0, 'total_size_mb': 0}
    
    def _estimate_table_records(self, table_name: str, file_size: int) -> int:
        """估算表记录数"""
        # 基于平均记录大小估算
        avg_record_sizes = {
            'route': 256,      % 路由表
            'queue': 512,      % 队列表
            'user': 1024,      % 用户表
            'exchange': 384    % 交换机表
        }
        
        avg_size = avg_record_sizes.get(table_name, 512)
        return max(1, int(file_size / avg_size))
    
    def _analyze_transaction_logs(self) -> Dict[str, Any]:
        """分析事务日志"""
        log_files = []
        
        try:
            # 扫描事务日志文件
            for file in os.listdir(self.mnesia_dir):
                if file.startswith('schema.DCD') or file.startswith('.schema.DCD'):
                    file_path = os.path.join(self.mnesia_dir, file)
                    stat_info = os.stat(file_path)
                    
                    log_files.append({
                        'name': file,
                        'size_mb': stat_info.st_size / (1024**2),
                        'age_hours': (time.time() - stat_info.st_mtime) / 3600
                    })
        except Exception as e:
            logging.error(f"分析事务日志失败: {e}")
        
        if log_files:
            total_size = sum(f['size_mb'] for f in log_files)
            oldest_log = max(log_files, key=lambda x: x['age_hours'])
            
            return {
                'total_logs': len(log_files),
                'total_size_mb': total_size,
                'oldest_log_age_hours': oldest_log['age_hours'],
                'logs': sorted(log_files, key=lambda x: x['age_hours'], reverse=True)
            }
        else:
            return {'total_logs': 0, 'total_size_mb': 0}
    
    def _analyze_database_size(self) -> Dict[str, Any]:
        """分析数据库大小"""
        try:
            total_size = 0
            file_counts = {
                '.DAT': 0,   % 数据文件
                '.DCD': 0,   % 事务日志文件
                '.DCL': 0,   % 锁文件
                '.AMD': 0    % 辅助文件
            }
            
            for file in os.listdir(self.mnesia_dir):
                if file.endswith(('.DAT', '.DCD', '.DCL', '.AMD')):
                    file_path = os.path.join(self.mnesia_dir, file)
                    stat_info = os.stat(file_path)
                    total_size += stat_info.st_size
                    
                    ext = os.path.splitext(file)[1]
                    file_counts[ext] += 1
            
            return {
                'total_size_gb': total_size / (1024**3),
                'file_counts': file_counts,
                'fragmentation': self._calculate_fragmentation(file_counts)
            }
            
        except Exception as e:
            logging.error(f"分析数据库大小失败: {e}")
            return {}
    
    def _calculate_fragmentation(self, file_counts: Dict[str, int]) -> float:
        """计算数据库碎片化程度"""
        total_files = sum(file_counts.values())
        if total_files == 0:
            return 0.0
        
        # 基于文件数量计算碎片化程度
        large_file_count = file_counts.get('.DAT', 0)
        if large_file_count > 100:
            return min(1.0, large_file_count / 1000)
        else:
            return 0.0
    
    def _analyze_query_performance(self) -> Dict[str, Any]:
        """分析查询性能"""
        # 这里可以实现更详细的查询性能分析
        # 例如：跟踪慢查询、统计查询类型等
        
        return {
            'avg_query_time_ms': 0,
            'slow_queries_count': 0,
            'query_types_distribution': {}
        }
    
    def optimize_database_settings(self) -> Dict[str, Any]:
        """优化数据库设置"""
        optimizations = {}
        
        try:
            # 分析当前性能数据
            current_perf = self.analyze_database_performance()
            
            # 根据性能数据推荐优化方案
            if current_perf.get('size_stats', {}).get('fragmentation', 0) > 0.5:
                optimizations['defragmentation'] = '建议进行数据库碎片整理'
            
            if current_perf.get('log_stats', {}).get('total_logs', 0) > 50:
                optimizations['log_rotation'] = '建议增加事务日志轮转频率'
            
            db_size = current_perf.get('size_stats', {}).get('total_size_gb', 0)
            if db_size > 10:
                optimizations['partitioning'] = '建议考虑数据库分区'
            
        except Exception as e:
            logging.error(f"数据库优化分析失败: {e}")
        
        return optimizations
```

## 集群性能调优

### 1. 集群配置优化

**集群参数调优**
```erlang
%% 优化的集群配置
[
  {rabbit, [
    % 集群配置
    {cluster_nodes, {['rabbit@node1', 'rabbit@node2', 'rabbit@node3'], disc}},
    {cluster_partition_handling, pause_minority},
    {mirroring_sup_queue, false},      % 禁用镜像队列同步
    {mirroring_sup_flow, true},        % 启用镜像流控制
    
    % 复制配置
    {queue_master_locator, <<"min-masters">>},
    {default_prefetch, 1000},          % 默认预取数量
    {channel_max, 2048},               % 最大通道数
    
    % 网络配置
    {dist_listen_min, 25672},
    {dist_listen_max, 25672},
    {tcp_listen_options, [
      {backlog, 128},
      {linger, {true, 0}}
    ]}
  ]},
  {kernel, [
    {inet_dist_listen_options, [{ifaddr, {0,0,0,0}}]}
  ]},
  {rabbitmq_mnesia, [
    {extra_db_nodes, ['rabbit@node1', 'rabbit@node2', 'rabbit@node3']}
  ]}
].
```

**集群管理器**
```python
import paramiko
import time
from typing import List, Dict, Any

class ClusterOptimizer:
    def __init__(self, cluster_nodes: List[str]):
        self.cluster_nodes = cluster_nodes
        self.node_ssh_clients = {}
    
    def optimize_cluster_performance(self) -> Dict[str, Any]:
        """优化集群性能"""
        optimization_results = {}
        
        # 优化每个节点
        for node in self.cluster_nodes:
            node_result = self._optimize_single_node(node)
            optimization_results[node] = node_result
        
        # 集群级别优化
        cluster_result = self._optimize_cluster_level()
        optimization_results['cluster'] = cluster_result
        
        return optimization_results
    
    def _optimize_single_node(self, node: str) -> Dict[str, Any]:
        """优化单个节点"""
        try:
            ssh_client = self._get_ssh_client(node)
            
            # 系统优化
            system_result = self._optimize_system_settings(ssh_client)
            
            # RabbitMQ优化
            rabbitmq_result = self._optimize_rabbitmq_settings(ssh_client)
            
            # 网络优化
            network_result = self._optimize_network_settings(ssh_client)
            
            ssh_client.close()
            
            return {
                'system': system_result,
                'rabbitmq': rabbitmq_result,
                'network': network_result
            }
            
        except Exception as e:
            logging.error(f"优化节点 {node} 失败: {e}")
            return {'error': str(e)}
    
    def _optimize_system_settings(self, ssh_client) -> Dict[str, Any]:
        """优化系统设置"""
        results = {}
        
        # 优化内核参数
        kernel_optimizations = [
            'net.core.rmem_max = 16777216',
            'net.core.wmem_max = 16777216',
            'net.ipv4.tcp_rmem = 4096 65536 16777216',
            'net.ipv4.tcp_wmem = 4096 65536 16777216',
            'vm.swappiness = 1',
            'fs.file-max = 2097152'
        ]
        
        # 写入sysctl配置
        sysctl_commands = [
            f'echo "{opt}" >> /etc/sysctl.conf' for opt in kernel_optimizations
        ]
        
        for cmd in sysctl_commands:
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            results[f'sysctl_{cmd.split()[-1]}'] = stdout.channel.recv_exit_status()
        
        # 应用设置
        stdin, stdout, stderr = ssh_client.exec_command('sysctl -p')
        results['sysctl_applied'] = stdout.channel.recv_exit_status()
        
        return results
    
    def _optimize_rabbitmq_settings(self, ssh_client) -> Dict[str, Any]:
        """优化RabbitMQ设置"""
        results = {}
        
        # 创建优化的RabbitMQ配置文件
        config_template = """
[
  {kernel, [
    {inet_default_connect_options, [{nodelay, true}]},
    {inet_default_listen_options, [{nodelay, true}]}
  ]},
  {rabbit, [
    {disk_free_limit, 1000000000},
    {vm_memory_high_watermark, 0.6},
    {memory_relative_limit, 1.0},
    {connection_max, 32768},
    {channel_max, 131072},
    {heartbeat, 30},
    {queue_index_max_journal_entries, 32768},
    {vm_memory_calculation_strategy, allocated},
    {tcp_listen_options, [
      {backlog, 128},
      {linger, {true, 0}},
      {exit_on_close, false}
    ]},
    {log_levels, [
      {connection, warning},
      {mirroring, info}
    ]}
  ]}
].
"""
        
        # 备份原有配置
        stdin, stdout, stderr = ssh_client.exec_command('cp /etc/rabbitmq/rabbitmq.config /etc/rabbitmq/rabbitmq.config.backup')
        results['backup_old_config'] = stdout.channel.recv_exit_status()
        
        # 写入新配置
        sftp = ssh_client.open_sftp()
        with sftp.open('/etc/rabbitmq/rabbitmq.config', 'w') as f:
            f.write(config_template)
        sftp.close()
        
        results['new_config_applied'] = True
        
        return results
    
    def _optimize_network_settings(self, ssh_client) -> Dict[str, Any]:
        """优化网络设置"""
        results = {}
        
        # 设置连接跟踪限制
        network_commands = [
            'echo 65536 > /proc/sys/net/netfilter/nf_conntrack_max',
            'echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse',
            'echo 1 > /proc/sys/net/ipv4/tcp_fin_timeout'
        ]
        
        for cmd in network_commands:
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            results[cmd.split()[-1]] = stdout.channel.recv_exit_status()
        
        return results
    
    def _optimize_cluster_level(self) -> Dict[str, Any]:
        """集群级别优化"""
        results = {}
        
        try:
            # 检查集群健康状态
            cluster_health = self._check_cluster_health()
            results['health'] = cluster_health
            
            # 负载均衡检查
            load_balance = self