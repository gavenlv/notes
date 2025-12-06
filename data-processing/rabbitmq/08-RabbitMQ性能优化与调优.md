# 第8章：RabbitMQ性能优化与调优

## 章节概述

性能优化是RabbitMQ生产环境部署的关键环节。本章节将深入探讨RabbitMQ的性能优化策略，包括系统配置调优、连接池管理、消息处理优化、内存和磁盘管理、网络调优等核心主题。通过理论讲解和实践案例，帮助您构建高性能的消息队列系统。

## 学习目标

通过本章学习，您将掌握：

1. **系统级性能优化**
   - Linux系统参数调优
   - 网络配置优化
   - 文件系统优化
   - CPU和内存调优

2. **RabbitMQ配置优化**
   - 核心参数配置
   - 资源限制设置
   - 队列性能调优
   - 交换机优化策略

3. **消息处理优化**
   - 批量处理优化
   - 预取设置优化
   - 确认模式调优
   - 事务处理优化

4. **连接池与并发管理**
   - 连接池配置
   - 并发连接优化
   - 线程池管理
   - 连接复用策略

5. **内存与磁盘优化**
   - 内存管理策略
   - 磁盘I/O优化
   - 消息持久化调优
   - 垃圾回收优化

6. **监控与诊断**
   - 性能监控指标
   - 瓶颈分析方法
   - 性能测试工具
   - 调优效果评估

## 1. 系统级性能优化

### 1.1 Linux内核参数调优

#### 网络参数优化

```bash
# /etc/sysctl.conf

# 网络缓冲区设置
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# TCP连接优化
net.core.somaxconn = 4096
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3

# 文件描述符限制
fs.file-max = 2097152
fs.nr_open = 2097152

# 应用配置
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_max_tw_buckets = 400000
```

#### 应用网络参数

```bash
# /etc/security/limits.conf

# 用户文件描述符限制
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536

# RabbitMQ用户专用限制
rabbitmq soft nofile 65536
rabbitmq hard nofile 65536
rabbitmq soft nproc 65536
rabbitmq hard nproc 65536
```

### 1.2 CPU和内存优化

#### CPU调度优化

```bash
# CPU亲和性设置
echo 0 > /sys/devices/system/cpu/cpu0/online
echo 0 > /sys/devices/system/cpu/cpu1/online
echo 1 > /sys/devices/system/cpu/cpu2/online
echo 1 > /sys/devices/system/cpu/cpu3/online

# RabbitMQ进程绑定到特定CPU
taskset -c 2,3 $(pgrep beam.smp)
```

#### 内存管理优化

```bash
# 内存管理策略
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

# NUMA优化
echo 1 > /proc/sys/vm/zone_reclaim_mode
```

### 1.3 磁盘I/O优化

```bash
# I/O调度器设置
echo noop > /sys/block/sda/queue/scheduler

# 预读设置
blockdev --setra 4096 /dev/sda

# I/O优先级设置
ionice -c 1 -n 0 -p $(pgrep beam.smp)
```

## 2. RabbitMQ核心配置优化

### 2.1 基础配置优化

```erlang
% /etc/rabbitmq/rabbitmq.conf

% 连接设置
listeners.tcp.default = 5672
num_acceptors.tcp = 10
connection_max_infinity = true
handshake_timeout = 60000
shutdown_timeout = 7000

% 内存和磁盘设置
vm_memory_high_watermark.relative = 0.6
vm_memory_high_watermark_paging_ratio = 0.5
disk_free_limit.absolute = 1GB
disk_free_limit.absolute = 50MB
memory_monitoring = true

% 队列设置
queue_index_embed_msgs_below = 4096
default_queue_exclusive_owners_consumers = false
default_queue_type = classic

% 心跳设置
heartbeat = 60

% 性能相关
frame_max = 131072
channel_max = 0
consumer_timeout = 3600000
```

### 2.2 高并发配置

```erlang
% 高并发场景配置
listeners.tcp.default = 5672
num_acceptors.tcp = 32
num_acceptors.ssl = 32

% 连接池设置
channel_cache_size = 64
connection_max_infinity = true

% 队列性能优化
default_prefetch = 1000
prefetch_count.global = 0
consumer_timeout = 300000

% 内存优化
vm_memory_high_watermark.relative = 0.7
vm_memory_high_watermark_paging_ratio = 0.75
```

### 2.3 生产环境优化配置

```erlang
% 生产环境推荐配置
listeners.tcp.default = 5672
listeners.ssl.default = 5671

% SSL配置
ssl_options.cacertfile = /etc/rabbitmq/ssl/ca.pem
ssl_options.certfile = /etc/rabbitmq/ssl/server.pem
ssl_options.keyfile = /etc/rabbitmq/ssl/server.key
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = false

% 集群配置
cluster_formation.peer_discovery_backend = classic_config
cluster_formation.classic_config.nodes.1 = rabbit@node1
cluster_formation.classic_config.nodes.2 = rabbit@node2
cluster_formation.classic_config.nodes.3 = rabbit@node3

% 镜像队列配置
镜像队列配置（高级主题，将在后续章节详细介绍）
```

## 3. 消息处理优化策略

### 3.1 预取配置优化

```python
# 基础预取配置
def optimize_prefetch_settings():
    """
    根据消息处理能力和网络状况优化预取设置
    """
    scenarios = {
        'high_throughput': {
            'prefetch_count': 1000,
            'global_qos': True,
            'description': '高吞吐量场景'
        },
        'balanced': {
            'prefetch_count': 100,
            'global_qos': False,
            'description': '平衡场景'
        },
        'low_latency': {
            'prefetch_count': 1,
            'global_qos': False,
            'description': '低延迟场景'
        }
    }
    
    return scenarios

# Python客户端预取配置示例
import pika

def setup_optimized_consumer(channel, queue_name, prefetch_count=100):
    """
    设置优化后的消费者
    """
    # 设置预取数量
    channel.basic_qos(prefetch_count=prefetch_count, global_qos=False)
    
    # 启用手动确认
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=message_handler,
        auto_ack=False
    )
    
    return channel

def message_handler(ch, method, properties, body):
    """
    消息处理器，支持批量确认
    """
    try:
        # 处理消息
        process_message(body)
        
        # 手动确认
        ch.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
        
    except Exception as e:
        # 处理失败，拒绝消息
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### 3.2 批量处理优化

```python
import asyncio
from typing import List, Callable
import time

class BatchProcessor:
    """
    批量消息处理器
    """
    
    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.current_batch = []
        self.last_flush_time = time.time()
    
    async def add_message(self, message: dict):
        """
        添加消息到批次
        """
        self.current_batch.append(message)
        
        # 检查是否需要处理批次
        if (len(self.current_batch) >= self.batch_size or 
            time.time() - self.last_flush_time >= self.flush_interval):
            await self.flush()
    
    async def flush(self):
        """
        处理当前批次
        """
        if not self.current_batch:
            return
        
        try:
            # 批量处理消息
            await self.process_batch(self.current_batch)
            self.current_batch.clear()
            self.last_flush_time = time.time()
            
        except Exception as e:
            print(f"批量处理失败: {e}")
            # 可以选择重试或记录失败消息
    
    async def process_batch(self, batch: List[dict]):
        """
        实际批量处理逻辑
        """
        # 这里实现具体的批量处理逻辑
        for message in batch:
            process_single_message(message)
        
        print(f"批量处理了 {len(batch)} 条消息")

# 使用示例
async def optimized_consumer():
    """
    优化的消费者，使用批量处理
    """
    processor = BatchProcessor(batch_size=50, flush_interval=2.0)
    
    def message_handler(ch, method, properties, body):
        message = json.loads(body)
        asyncio.create_task(processor.add_message(message))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    # 设置消费者
    channel.basic_consume(
        queue='optimized_queue',
        on_message_callback=message_handler,
        auto_ack=False
    )
```

### 3.3 异步处理优化

```python
import asyncio
import aio_pika
from concurrent.futures import ThreadPoolExecutor

class AsyncMessageProcessor:
    """
    异步消息处理器
    """
    
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def consume_messages(self, connection_string: str, queue_name: str):
        """
        异步消费消息
        """
        connection = await aio_pika.connect_robust(connection_string)
        
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=100)
            
            queue = await channel.declare_queue(queue_name, durable=True)
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self.handle_message(message)
    
    async def handle_message(self, message: aio_pika.IncomingMessage):
        """
        处理单条消息
        """
        async with self.semaphore:
            try:
                # 异步处理消息
                await self.process_async(message.body)
                await message.ack()
                
            except Exception as e:
                print(f"消息处理失败: {e}")
                await message.nack(requeue=True)
    
    async def process_async(self, message_body: bytes):
        """
        异步消息处理逻辑
        """
        # 这里可以执行任何异步操作
        await asyncio.sleep(0.1)  # 模拟异步处理
        
        # 将CPU密集型任务委托给线程池
        await asyncio.get_event_loop().run_in_executor(
            self.executor, 
            self.process_cpu_intensive_task, 
            message_body
        )
    
    def process_cpu_intensive_task(self, message_body: bytes):
        """
        CPU密集型任务处理
        """
        # 执行CPU密集型计算
        pass
```

## 4. 连接池与并发管理

### 4.1 连接池配置

```python
import pika
from queue import Queue, Empty
import threading
import time
from typing import Optional, Dict, Any
import logging

class RabbitMQConnectionPool:
    """
    RabbitMQ连接池
    """
    
    def __init__(self, 
                 host: str,
                 port: int = 5672,
                 username: str = None,
                 password: str = None,
                 max_connections: int = 10,
                 min_connections: int = 5,
                 connection_timeout: int = 30,
                 heartbeat: int = 60):
        
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_timeout = connection_timeout
        self.heartbeat = heartbeat
        
        self.connection_pool = Queue(maxsize=max_connections)
        self.connections_in_use = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 初始化最小连接数
        self._initialize_connections()
    
    def _initialize_connections(self):
        """
        初始化最小连接数
        """
        for _ in range(self.min_connections):
            connection = self._create_connection()
            if connection:
                self.connection_pool.put(connection)
    
    def _create_connection(self) -> Optional[pika.BlockingConnection]:
        """
        创建新的连接
        """
        try:
            credentials = pika.PlainCredentials(self.username, self.password) if self.username else None
            
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=1,
                socket_timeout=self.connection_timeout,
                heartbeat=self.heartbeat,
                blocked_connection_timeout=300,
                client_properties={'connection_name': 'pool_connection'}
            )
            
            connection = pika.BlockingConnection(parameters)
            
            # 测试连接
            channel = connection.channel()
            channel.queue_declare(queue='test', passive=True)
            channel.close()
            
            self.logger.info(f"创建新连接: {connection}")
            return connection
            
        except Exception as e:
            self.logger.error(f"创建连接失败: {e}")
            return None
    
    def get_connection(self, timeout: float = 30.0) -> Optional[pika.BlockingConnection]:
        """
        获取连接
        """
        try:
            # 尝试从池中获取连接
            connection = self.connection_pool.get(timeout=timeout)
            
            # 检查连接是否有效
            if connection.is_open:
                with self.lock:
                    self.connections_in_use += 1
                return connection
            else:
                # 连接已关闭，重新创建
                new_connection = self._create_connection()
                if new_connection:
                    with self.lock:
                        self.connections_in_use += 1
                    return new_connection
                    
        except Empty:
            self.logger.warning("连接池已满，无法获取连接")
            
            # 尝试创建新连接
            if self.connections_in_use < self.max_connections:
                new_connection = self._create_connection()
                if new_connection:
                    with self.lock:
                        self.connections_in_use += 1
                    return new_connection
        
        return None
    
    def return_connection(self, connection: pika.BlockingConnection):
        """
        归还连接到池中
        """
        try:
            if connection.is_open:
                self.connection_pool.put(connection)
                with self.lock:
                    self.connections_in_use -= 1
            else:
                # 连接已关闭，创建新连接补充
                new_connection = self._create_connection()
                if new_connection:
                    self.connection_pool.put(new_connection)
                
                with self.lock:
                    self.connections_in_use -= 1
                    
        except Exception as e:
            self.logger.error(f"归还连接失败: {e}")
            with self.lock:
                self.connections_in_use -= 1
    
    def close_all_connections(self):
        """
        关闭所有连接
        """
        # 关闭池中的连接
        while not self.connection_pool.empty():
            try:
                connection = self.connection_pool.get_nowait()
                connection.close()
            except Empty:
                break
        
        # 关闭正在使用的连接
        with self.lock:
            self.connections_in_use = 0
        
        self.logger.info("所有连接已关闭")
```

### 4.2 线程池优化

```python
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import time
from typing import Callable, Any, List
import weakref

class OptimizedThreadPool:
    """
    优化的线程池，专门用于RabbitMQ消息处理
    """
    
    def __init__(self, 
                 max_workers: int = None,
                 thread_name_prefix: str = "RabbitMQ",
                 keepalive_time: int = 60):
        
        if max_workers is None:
            # 根据CPU核心数确定工作线程数
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        
        self.thread_pool = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
            keepalive_time=keepalive_time
        )
        
        self.active_tasks = {}
        self.task_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def submit_task(self, 
                   task_func: Callable, 
                   *args, 
                   callback: Callable = None, 
                   error_callback: Callable = None,
                   task_id: str = None):
        """
        提交任务到线程池
        """
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}"
        
        def wrapped_callback(future):
            try:
                result = future.result()
                if callback:
                    callback(result)
                
                with self.task_lock:
                    self.active_tasks.pop(task_id, None)
                    
            except Exception as e:
                self.logger.error(f"任务 {task_id} 执行失败: {e}")
                if error_callback:
                    error_callback(e)
                
                with self.task_lock:
                    self.active_tasks.pop(task_id, None)
        
        future = self.thread_pool.submit(task_func, *args)
        future.add_done_callback(wrapped_callback)
        
        with self.task_lock:
            self.active_tasks[task_id] = future
        
        return task_id, future
    
    def submit_batch(self, 
                    tasks: List[tuple], 
                    batch_callback: Callable = None):
        """
        批量提交任务
        """
        futures = []
        
        for task_args in tasks:
            task_func = task_args[0]
            task_params = task_args[1:] if len(task_args) > 1 else ()
            
            task_id, future = self.submit_task(task_func, *task_params)
            futures.append((task_id, future))
        
        # 等待所有任务完成
        if batch_callback:
            batch_callback(futures)
        
        return futures
    
    def get_active_tasks(self) -> Dict[str, Any]:
        """
        获取活跃任务状态
        """
        with self.task_lock:
            return dict(self.active_tasks)
    
    def shutdown(self, wait: bool = True):
        """
        关闭线程池
        """
        self.thread_pool.shutdown(wait=wait)
        self.logger.info("线程池已关闭")

# 使用示例
def create_message_processor():
    """
    创建消息处理器
    """
    thread_pool = OptimizedThreadPool(max_workers=20)
    
    def process_message_async(message_data):
        """
        异步处理消息
        """
        # 模拟消息处理
        time.sleep(0.1)
        result = f"Processed: {message_data}"
        return result
    
    def message_callback(result):
        print(f"消息处理结果: {result}")
    
    def error_callback(error):
        print(f"消息处理错误: {error}")
    
    return thread_pool, process_message_async, message_callback, error_callback
```

### 4.3 连接复用策略

```python
import weakref
import threading
from collections import defaultdict
from typing import Dict, Set, Optional

class ConnectionManager:
    """
    连接管理器，支持连接复用和负载均衡
    """
    
    def __init__(self):
        self.connections: Dict[str, weakref.ref] = {}
        self.connection_stats: Dict[str, Dict] = defaultdict(lambda: {
            'created_at': time.time(),
            'last_used': time.time(),
            'usage_count': 0,
            'errors': 0
        })
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def register_connection(self, connection_id: str, connection: pika.BlockingConnection):
        """
        注册连接
        """
        with self.lock:
            # 创建弱引用，避免循环引用
            weak_ref = weakref.ref(connection, lambda ref: self._cleanup_connection(connection_id))
            self.connections[connection_id] = weak_ref
            self.logger.info(f"注册连接: {connection_id}")
    
    def get_connection(self, connection_id: str) -> Optional[pika.BlockingConnection]:
        """
        获取连接
        """
        with self.lock:
            weak_ref = self.connections.get(connection_id)
            if weak_ref:
                connection = weak_ref()
                if connection and connection.is_open:
                    # 更新统计信息
                    self.connection_stats[connection_id]['last_used'] = time.time()
                    self.connection_stats[connection_id]['usage_count'] += 1
                    return connection
                else:
                    # 连接已关闭，清理记录
                    self._cleanup_connection(connection_id)
            
            return None
    
    def _cleanup_connection(self, connection_id: str):
        """
        清理已关闭的连接
        """
        with self.lock:
            if connection_id in self.connections:
                del self.connections[connection_id]
                self.logger.info(f"清理已关闭连接: {connection_id}")
    
    def get_least_used_connection(self) -> Optional[pika.BlockingConnection]:
        """
        获取使用次数最少的连接
        """
        with self.lock:
            if not self.connections:
                return None
            
            # 找到使用次数最少的连接
            least_used_id = min(
                self.connection_stats.keys(),
                key=lambda cid: self.connection_stats[cid]['usage_count']
            )
            
            return self.get_connection(least_used_id)
    
    def report_error(self, connection_id: str):
        """
        报告连接错误
        """
        with self.lock:
            if connection_id in self.connection_stats:
                self.connection_stats[connection_id]['errors'] += 1
    
    def get_connection_stats(self) -> Dict[str, Dict]:
        """
        获取连接统计信息
        """
        with self.lock:
            return dict(self.connection_stats)
    
    def get_healthy_connections(self) -> Set[str]:
        """
        获取健康连接列表
        """
        healthy_connections = set()
        
        with self.lock:
            for connection_id in list(self.connections.keys()):
                stats = self.connection_stats[connection_id]
                error_rate = stats['errors'] / max(stats['usage_count'], 1)
                
                # 如果错误率小于10%，认为连接是健康的
                if error_rate < 0.1:
                    healthy_connections.add(connection_id)
        
        return healthy_connections

# 负载均衡连接工厂
class LoadBalancedConnectionFactory:
    """
    负载均衡连接工厂
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.round_robin_index = 0
        self.lock = threading.Lock()
    
    def create_connection(self, connection_configs: List[Dict]) -> Optional[pika.BlockingConnection]:
        """
        创建负载均衡连接
        """
        healthy_connections = self.connection_manager.get_healthy_connections()
        
        if not healthy_connections:
            # 如果没有健康连接，尝试创建新连接
            config = connection_configs[0] if connection_configs else {}
            return self._create_new_connection(config)
        
        with self.lock:
            # 轮询选择连接
            connection_ids = list(healthy_connections)
            selected_id = connection_ids[self.round_robin_index % len(connection_ids)]
            self.round_robin_index += 1
            
            return self.connection_manager.get_connection(selected_id)
    
    def _create_new_connection(self, config: Dict) -> Optional[pika.BlockingConnection]:
        """
        创建新连接
        """
        try:
            parameters = pika.ConnectionParameters(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5672),
                credentials=pika.PlainCredentials(
                    config.get('username', 'guest'),
                    config.get('password', 'guest')
                ) if config.get('username') else None,
                connection_attempts=3,
                retry_delay=1
            )
            
            connection = pika.BlockingConnection(parameters)
            connection_id = f"conn_{int(time.time() * 1000)}"
            
            self.connection_manager.register_connection(connection_id, connection)
            return connection
            
        except Exception as e:
            self.logger.error(f"创建新连接失败: {e}")
            return None
```

## 5. 内存与磁盘优化

### 5.1 内存管理策略

```python
import psutil
import gc
import resource
from typing import Dict, Any, List
import time

class MemoryOptimizer:
    """
    内存优化管理器
    """
    
    def __init__(self, warning_threshold: float = 0.8, critical_threshold: float = 0.9):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.memory_stats = {
            'peak_usage': 0,
            'gc_collections': 0,
            'gc_objects': 0,
            'last_gc_time': 0
        }
        self.logger = logging.getLogger(__name__)
    
    def get_memory_status(self) -> Dict[str, Any]:
        """
        获取内存状态
        """
        # 系统内存状态
        memory = psutil.virtual_memory()
        process_memory = psutil.Process().memory_info()
        
        # RSS内存使用情况
        rss_mb = process_memory.rss / 1024 / 1024
        vms_mb = process_memory.vms / 1024 / 1024
        
        memory_info = {
            'system': {
                'total_gb': memory.total / 1024 / 1024 / 1024,
                'available_gb': memory.available / 1024 / 1024 / 1024,
                'used_percent': memory.percent,
                'used_gb': memory.used / 1024 / 1024 / 1024
            },
            'process': {
                'rss_mb': rss_mb,
                'vms_mb': vms_mb,
                'rss_percent': (process_memory.rss / memory.total) * 100
            },
            'limits': {
                'warning_threshold': self.warning_threshold,
                'critical_threshold': self.critical_threshold
            }
        }
        
        # 更新峰值使用记录
        if rss_mb > self.memory_stats['peak_usage']:
            self.memory_stats['peak_usage'] = rss_mb
            memory_info['process']['peak_rss_mb'] = rss_mb
        
        return memory_info
    
    def check_memory_pressure(self) -> str:
        """
        检查内存压力
        """
        memory_info = self.get_memory_status()
        used_percent = memory_info['system']['used_percent'] / 100
        
        if used_percent >= self.critical_threshold:
            return 'critical'
        elif used_percent >= self.warning_threshold:
            return 'warning'
        else:
            return 'normal'
    
    def optimize_memory(self) -> Dict[str, Any]:
        """
        执行内存优化
        """
        optimization_result = {
            'actions_taken': [],
            'memory_before': self.get_memory_status(),
            'memory_after': None,
            'duration': 0
        }
        
        start_time = time.time()
        
        try:
            # 执行垃圾回收
            gc.collect()
            self.memory_stats['gc_collections'] += 1
            
            # 获取对象数量统计
            gc_objects_before = len(gc.get_objects())
            
            # 清理缓存
            optimization_result['actions_taken'].append('garbage_collection')
            
            # 如果内存压力仍然很高，执行更激进的优化
            if self.check_memory_pressure() == 'critical':
                # 强制完整垃圾回收
                gc.collect(2)
                optimization_result['actions_taken'].append('force_gc')
                
                # 清理线程池
                self._cleanup_thread_pools()
                optimization_result['actions_taken'].append('cleanup_thread_pools')
            
            # 统计优化效果
            gc_objects_after = len(gc.get_objects())
            self.memory_stats['gc_objects'] += (gc_objects_before - gc_objects_after)
            
            optimization_result['memory_after'] = self.get_memory_status()
            optimization_result['objects_freed'] = gc_objects_before - gc_objects_after
            
        except Exception as e:
            optimization_result['error'] = str(e)
            self.logger.error(f"内存优化失败: {e}")
        
        optimization_result['duration'] = time.time() - start_time
        return optimization_result
    
    def _cleanup_thread_pools(self):
        """
        清理线程池中的空闲工作线程
        """
        # 这里可以实现线程池的清理逻辑
        # 例如，减少ThreadPoolExecutor中的工作线程数
        pass
    
    def monitor_memory_growth(self, interval: int = 60):
        """
        监控内存增长
        """
        previous_rss = 0
        growth_threshold = 100  # MB
        
        while True:
            try:
                current_status = self.get_memory_status()
                current_rss = current_status['process']['rss_mb']
                
                if previous_rss > 0:
                    growth = current_rss - previous_rss
                    if growth > growth_threshold:
                        self.logger.warning(f"内存增长过快: {growth:.2f}MB")
                        
                        # 自动触发优化
                        self.optimize_memory()
                
                previous_rss = current_rss
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"内存监控出错: {e}")
                time.sleep(interval)

class MessageMemoryManager:
    """
    消息内存管理器
    """
    
    def __init__(self, max_message_size: int = 1024 * 1024,  # 1MB
                 max_queue_size: int = 1000):
        self.max_message_size = max_message_size
        self.max_queue_size = max_queue_size
        self.compression_threshold = 10 * 1024  # 10KB
        self.message_cache = {}
        self.cache_lock = threading.Lock()
    
    def validate_message_size(self, message: bytes) -> bool:
        """
        验证消息大小
        """
        return len(message) <= self.max_message_size
    
    def compress_large_message(self, message: bytes) -> bytes:
        """
        压缩大消息
        """
        if len(message) > self.compression_threshold:
            import zlib
            return zlib.compress(message)
        return message
    
    def decompress_message(self, compressed_message: bytes, is_compressed: bool) -> bytes:
        """
        解压缩消息
        """
        if is_compressed:
            import zlib
            return zlib.decompress(compressed_message)
        return compressed_message
    
    def cache_message(self, message_id: str, message: bytes, ttl: int = 3600):
        """
        缓存消息
        """
        with self.cache_lock:
            if len(self.message_cache) >= self.max_queue_size:
                # 清理最久未使用的消息
                oldest_key = min(self.message_cache.keys(), 
                               key=lambda k: self.message_cache[k]['timestamp'])
                del self.message_cache[oldest_key]
            
            self.message_cache[message_id] = {
                'data': message,
                'timestamp': time.time(),
                'ttl': ttl
            }
    
    def get_cached_message(self, message_id: str) -> Optional[bytes]:
        """
        获取缓存消息
        """
        with self.cache_lock:
            if message_id in self.message_cache:
                cached_item = self.message_cache[message_id]
                
                # 检查TTL
                if time.time() - cached_item['timestamp'] < cached_item['ttl']:
                    return cached_item['data']
                else:
                    # 过期，删除
                    del self.message_cache[message_id]
            
            return None
    
    def cleanup_expired_cache(self):
        """
        清理过期缓存
        """
        with self.cache_lock:
            current_time = time.time()
            expired_keys = [
                key for key, item in self.message_cache.items()
                if current_time - item['timestamp'] >= item['ttl']
            ]
            
            for key in expired_keys:
                del self.message_cache[key]
            
            return len(expired_keys)
```

### 5.2 磁盘I/O优化

```python
import os
import tempfile
import shutil
from pathlib import Path
import mmap
from typing import List, Optional, Callable
import threading

class DiskIOManager:
    """
    磁盘I/O管理器
    """
    
    def __init__(self, 
                 data_directory: str,
                 max_file_size: int = 100 * 1024 * 1024,  # 100MB
                 buffer_size: int = 8192,
                 flush_interval: int = 5):  # 秒
        
        self.data_directory = Path(data_directory)
        self.max_file_size = max_file_size
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        
        # 创建数据目录
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        # 文件管理
        self.current_file = None
        self.current_file_path = None
        self.current_file_size = 0
        self.write_buffer = []
        self.buffer_lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            'total_writes': 0,
            'total_bytes_written': 0,
            'flush_count': 0,
            'files_created': 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # 启动定期刷新线程
        self.flush_thread = threading.Thread(target=self._periodic_flush, daemon=True)
        self.flush_thread.start()
    
    def _periodic_flush(self):
        """
        定期刷新缓冲数据
        """
        while True:
            try:
                time.sleep(self.flush_interval)
                self.flush_buffer()
            except Exception as e:
                self.logger.error(f"定期刷新失败: {e}")
    
    def _get_new_file_path(self) -> Path:
        """
        获取新文件路径
        """
        timestamp = int(time.time())
        filename = f"message_data_{timestamp}_{os.getpid()}.dat"
        return self.data_directory / filename
    
    def write_message(self, message_data: bytes, metadata: dict = None) -> bool:
        """
        写入消息数据
        """
        try:
            with self.buffer_lock:
                # 准备写入数据
                record = {
                    'timestamp': time.time(),
                    'data': message_data,
                    'metadata': metadata or {},
                    'size': len(message_data)
                }
                
                self.write_buffer.append(record)
                
                # 检查是否需要立即刷新
                if (self.current_file_size + len(message_data) > self.max_file_size or
                    len(self.write_buffer) >= 1000):
                    self.flush_buffer()
                
                return True
                
        except Exception as e:
            self.logger.error(f"写入消息失败: {e}")
            return False
    
    def flush_buffer(self):
        """
        刷新写入缓冲
        """
        with self.buffer_lock:
            if not self.write_buffer:
                return
            
            try:
                # 确保有当前文件
                if not self.current_file or self.current_file.closed:
                    self._open_new_file()
                
                # 写入缓冲数据
                for record in self.write_buffer:
                    # 写入时间戳
                    timestamp_bytes = str(record['timestamp']).encode('utf-8')
                    self.current_file.write(f"TS:{len(timestamp_bytes)}:{timestamp_bytes}\n".encode('utf-8'))
                    
                    # 写入数据大小
                    size_bytes = str(record['size']).encode('utf-8')
                    self.current_file.write(f"SZ:{len(size_bytes)}:{size_bytes}\n".encode('utf-8'))
                    
                    # 写入消息数据
                    self.current_file.write(record['data'])
                    self.current_file.write(b"\n")
                    
                    # 写入元数据（如果存在）
                    if record['metadata']:
                        metadata_str = str(record['metadata'])
                        metadata_bytes = metadata_str.encode('utf-8')
                        self.current_file.write(f"MD:{len(metadata_bytes)}:{metadata_bytes}\n".encode('utf-8'))
                    
                    self.current_file.write(b"==END==\n")
                    
                    self.current_file_size += len(record['data'])
                    self.stats['total_writes'] += 1
                    self.stats['total_bytes_written'] += len(record['data'])
                
                # 清空缓冲
                self.write_buffer.clear()
                self.stats['flush_count'] += 1
                
                # 强制刷新到磁盘
                self.current_file.flush()
                os.fsync(self.current_file.fileno())
                
            except Exception as e:
                self.logger.error(f"刷新缓冲失败: {e}")
    
    def _open_new_file(self):
        """
        打开新文件
        """
        try:
            # 关闭旧文件
            if self.current_file and not self.current_file.closed:
                self.current_file.close()
            
            # 创建新文件
            self.current_file_path = self._get_new_file_path()
            self.current_file = open(self.current_file_path, 'ab')
            self.current_file_size = 0
            self.stats['files_created'] += 1
            
            self.logger.info(f"创建新数据文件: {self.current_file_path}")
            
        except Exception as e:
            self.logger.error(f"打开新文件失败: {e}")
            raise
    
    def read_messages(self, 
                     start_timestamp: float = None,
                     end_timestamp: float = None,
                     message_filter: Callable = None) -> List[dict]:
        """
        读取消息数据
        """
        messages = []
        
        try:
            for file_path in self.data_directory.glob("*.dat"):
                with open(file_path, 'rb') as f:
                    messages.extend(self._parse_file(f, start_timestamp, end_timestamp, message_filter))
            
            return messages
            
        except Exception as e:
            self.logger.error(f"读取消息失败: {e}")
            return []
    
    def _parse_file(self, file_handle, start_timestamp, end_timestamp, message_filter):
        """
        解析文件数据
        """
        messages = []
        current_message = {}
        
        try:
            with mmap.mmap(file_handle.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                content = mmapped_file.read().decode('utf-8', errors='ignore')
                lines = content.split('\n')
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    if line.startswith("TS:"):
                        # 时间戳行
                        timestamp_info = line[3:].split(':', 1)
                        if len(timestamp_info) == 2:
                            timestamp = float(timestamp_info[1])
                            current_message['timestamp'] = timestamp
                    
                    elif line.startswith("SZ:"):
                        # 大小行
                        size_info = line[3:].split(':', 1)
                        if len(size_info) == 2:
                            current_message['size'] = int(size_info[1])
                    
                    elif line == "==END==":
                        # 消息结束
                        if 'timestamp' in current_message and 'size' in current_message:
                            # 检查时间范围
                            if (start_timestamp is None or current_message['timestamp'] >= start_timestamp) and \
                               (end_timestamp is None or current_message['timestamp'] <= end_timestamp):
                                messages.append(current_message.copy())
                        
                        current_message = {}
                    
                    elif line.startswith("MD:"):
                        # 元数据行
                        metadata_info = line[3:].split(':', 1)
                        if len(metadata_info) == 2:
                            try:
                                current_message['metadata'] = eval(metadata_info[1])
                            except:
                                current_message['metadata'] = {}
                    
                    elif line and not line.startswith("==END=="):
                        # 可能是数据行的一部分
                        if 'data' not in current_message:
                            current_message['data'] = []
                        current_message['data'].append(line.encode('utf-8'))
                    
                    i += 1
                
        except Exception as e:
            self.logger.error(f"解析文件失败: {e}")
        
        return messages
    
    def cleanup_old_files(self, retention_days: int = 7):
        """
        清理旧文件
        """
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        cleaned_files = 0
        
        try:
            for file_path in self.data_directory.glob("*.dat"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_files += 1
            
            self.logger.info(f"清理了 {cleaned_files} 个旧文件")
            return cleaned_files
            
        except Exception as e:
            self.logger.error(f"清理旧文件失败: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        """
        with self.buffer_lock:
            return {
                **self.stats,
                'buffer_size': len(self.write_buffer),
                'current_file': str(self.current_file_path) if self.current_file_path else None,
                'current_file_size_mb': self.current_file_size / 1024 / 1024,
                'data_directory': str(self.data_directory)
            }
    
    def close(self):
        """
        关闭管理器
        """
        try:
            self.flush_buffer()
            
            if self.current_file and not self.current_file.closed:
                self.current_file.close()
            
            self.logger.info("磁盘I/O管理器已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭磁盘I/O管理器失败: {e}")
```

## 6. 性能监控与诊断

### 6.1 性能指标收集器

```python
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from collections import defaultdict, deque
import json

@dataclass
class PerformanceMetrics:
    """
    性能指标数据类
    """
    timestamp: float
    metric_type: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    """
    性能指标收集器
    """
    
    def __init__(self, buffer_size: int = 10000):
        self.buffer_size = buffer_size
        self.metrics_buffer = deque(maxlen=buffer_size)
        self.metrics_lock = threading.Lock()
        self.subscribers: List[Callable] = []
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(lambda: deque(maxlen=1000))
        
        self.logger = logging.getLogger(__name__)
    
    def record_metric(self, 
                     metric_type: str, 
                     value: float, 
                     tags: Dict[str, str] = None, 
                     metadata: Dict[str, Any] = None):
        """
        记录指标
        """
        metric = PerformanceMetrics(
            timestamp=time.time(),
            metric_type=metric_type,
            value=value,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        with self.metrics_lock:
            self.metrics_buffer.append(metric)
        
        # 通知订阅者
        for subscriber in self.subscribers:
            try:
                subscriber(metric)
            except Exception as e:
                self.logger.error(f"指标订阅者处理失败: {e}")
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """
        增加计数器
        """
        self.counters[name] += value
        
        self.record_metric(
            metric_type='counter',
            value=self.counters[name],
            tags={'counter_name': name, **(tags or {})}
        )
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        设置仪表盘值
        """
        self.gauges[name] = value
        
        self.record_metric(
            metric_type='gauge',
            value=value,
            tags={'gauge_name': name, **(tags or {})}
        )
    
    def observe_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        观察直方图值
        """
        self.histograms[name].append(value)
        
        # 计算统计信息
        values = list(self.histograms[name])
        stats = {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'p50': self._percentile(values, 50),
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }
        
        self.record_metric(
            metric_type='histogram',
            value=value,
            tags={'histogram_name': name, **(tags or {})},
            metadata={'stats': stats}
        )
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """
        计算百分位数
        """
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = min(lower_index + 1, len(sorted_data) - 1)
            weight = index - lower_index
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def subscribe(self, callback: Callable):
        """
        订阅指标更新
        """
        self.subscribers.append(callback)
    
    def get_recent_metrics(self, count: int = 100) -> List[PerformanceMetrics]:
        """
        获取最近的指标
        """
        with self.metrics_lock:
            return list(self.metrics_buffer)[-count:]
    
    def get_metric_summary(self, time_window: int = 300) -> Dict[str, Any]:
        """
        获取指标摘要
        """
        cutoff_time = time.time() - time_window
        recent_metrics = [
            metric for metric in self.metrics_buffer 
            if metric.timestamp >= cutoff_time
        ]
        
        summary = {
            'time_window': time_window,
            'total_metrics': len(recent_metrics),
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histogram_stats': {}
        }
        
        # 统计直方图
        for name, values in self.histograms.items():
            if values:
                values_list = list(values)
                summary['histogram_stats'][name] = {
                    'count': len(values_list),
                    'min': min(values_list),
                    'max': max(values_list),
                    'avg': sum(values_list) / len(values_list),
                    'p50': self._percentile(values_list, 50),
                    'p95': self._percentile(values_list, 95),
                    'p99': self._percentile(values_list, 99)
                }
        
        return summary

class RabbitMQMetricsCollector:
    """
    RabbitMQ专用指标收集器
    """
    
    def __init__(self, connection_manager, metrics_collector: MetricsCollector):
        self.connection_manager = connection_manager
        self.metrics_collector = metrics_collector
        self.monitoring_thread = None
        self.is_monitoring = False
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self, interval: int = 30):
        """
        开始监控
        """
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info("RabbitMQ指标监控已启动")
    
    def stop_monitoring(self):
        """
        停止监控
        """
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("RabbitMQ指标监控已停止")
    
    def _monitoring_loop(self, interval: int):
        """
        监控循环
        """
        while self.is_monitoring:
            try:
                self._collect_rabbitmq_metrics()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"RabbitMQ指标收集失败: {e}")
                time.sleep(interval)
    
    def _collect_rabbitmq_metrics(self):
        """
        收集RabbitMQ指标
        """
        try:
            # 获取连接状态
            connections = self._get_connection_metrics()
            self.metrics_collector.set_gauge('rabbitmq.connections.active', len(connections))
            
            # 获取队列指标
            queues = self._get_queue_metrics()
            for queue_name, queue_metrics in queues.items():
                tags = {'queue': queue_name}
                
                self.metrics_collector.set_gauge('rabbitmq.queue.messages', 
                                               queue_metrics['messages'], tags)
                self.metrics_collector.set_gauge('rabbitmq.queue.rate', 
                                               queue_metrics['rate'], tags)
                self.metrics_collector.set_gauge('rabbitmq.queue.consumers', 
                                               queue_metrics['consumers'], tags)
            
            # 获取系统资源指标
            self._collect_system_metrics()
            
        except Exception as e:
            self.logger.error(f"收集RabbitMQ指标失败: {e}")
    
    def _get_connection_metrics(self) -> List[Dict]:
        """
        获取连接指标
        """
        try:
            # 这里应该使用RabbitMQ管理API或直接查询
            # 示例实现，需要根据实际情况调整
            return []  # 返回连接列表
        except Exception as e:
            self.logger.error(f"获取连接指标失败: {e}")
            return []
    
    def _get_queue_metrics(self) -> Dict[str, Dict]:
        """
        获取队列指标
        """
        try:
            # 这里应该使用RabbitMQ管理API或直接查询
            # 示例实现，需要根据实际情况调整
            return {}  # 返回队列指标字典
        except Exception as e:
            self.logger.error(f"获取队列指标失败: {e}")
            return {}
    
    def _collect_system_metrics(self):
        """
        收集系统指标
        """
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.set_gauge('system.cpu.usage', cpu_percent)
            
            # 内存使用
            memory = psutil.virtual_memory()
            self.metrics_collector.set_gauge('system.memory.usage_percent', memory.percent)
            self.metrics_collector.set_gauge('system.memory.available_mb', 
                                           memory.available / 1024 / 1024)
            
            # 磁盘I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.metrics_collector.increment_counter('system.disk.read_bytes', 
                                                       disk_io.read_bytes)
                self.metrics_collector.increment_counter('system.disk.write_bytes', 
                                                       disk_io.write_bytes)
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
```

### 6.2 性能瓶颈诊断器

```python
from typing import Dict, List, Tuple, Optional
import cProfile
import pstats
import io
from contextlib import contextmanager
import tracemalloc

class PerformanceProfiler:
    """
    性能分析器
    """
    
    def __init__(self):
        self.profiles = {}
        self.memory_snapshots = {}
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def profile_operation(self, operation_name: str):
        """
        性能分析上下文管理器
        """
        try:
            # 开始内存跟踪
            tracemalloc.start()
            
            # 开始CPU分析
            profiler = cProfile.Profile()
            profiler.enable()
            
            start_time = time.time()
            yield
            
        finally:
            end_time = time.time()
            
            # 停止CPU分析
            profiler.disable()
            
            # 获取内存快照
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # 保存分析结果
            profile_result = {
                'duration': end_time - start_time,
                'memory_current': current,
                'memory_peak': peak,
                'cpu_profile': self._analyze_profile(profiler),
                'timestamp': time.time()
            }
            
            self.profiles[operation_name] = profile_result
            
            self.logger.info(f"性能分析完成 - {operation_name}: "
                           f"耗时 {profile_result['duration']:.3f}s, "
                           f"内存峰值 {peak/1024/1024:.2f}MB")
    
    def _analyze_profile(self, profiler) -> Dict[str, Any]:
        """
        分析CPU性能分析结果
        """
        try:
            stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stream)
            
            # 获取最耗时的函数
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # 显示前20个函数
            
            profile_output = stream.getvalue()
            
            # 解析统计信息
            stats_dict = {}
            for line in profile_output.split('\n'):
                if line.strip() and not line.startswith('ncalls'):
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        func_name = ' '.join(parts[4:])
                        stats_dict[func_name] = {
                            'ncalls': parts[0],
                            'tottime': parts[1],
                            'cumtime': parts[2]
                        }
            
            return stats_dict
            
        except Exception as e:
            self.logger.error(f"分析性能分析结果失败: {e}")
            return {}

class BottleneckDetector:
    """
    性能瓶颈检测器
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.thresholds = {
            'message_processing_time': 1.0,  # 秒
            'memory_usage_percent': 80.0,
            'cpu_usage_percent': 80.0,
            'connection_count': 1000,
            'queue_length': 10000,
            'error_rate': 5.0  # 百分比
        }
        self.detected_bottlenecks = []
        self.logger = logging.getLogger(__name__)
    
    def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        检测性能瓶颈
        """
        bottlenecks = []
        
        try:
            # 检测消息处理瓶颈
            bottlenecks.extend(self._detect_processing_bottlenecks())
            
            # 检测资源使用瓶颈
            bottlenecks.extend(self._detect_resource_bottlenecks())
            
            # 检测队列性能瓶颈
            bottlenecks.extend(self._detect_queue_bottlenecks())
            
            # 检测连接性能瓶颈
            bottlenecks.extend(self._detect_connection_bottlenecks())
            
            self.detected_bottlenecks = bottlenecks
            return bottlenecks
            
        except Exception as e:
            self.logger.error(f"检测性能瓶颈失败: {e}")
            return []
    
    def _detect_processing_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        检测消息处理瓶颈
        """
        bottlenecks = []
        
        try:
            recent_metrics = self.metrics_collector.get_recent_metrics(count=100)
            processing_times = [
                m.value for m in recent_metrics 
                if m.metric_type == 'histogram' and 'processing_time' in m.tags
            ]
            
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
                
                if avg_processing_time > self.thresholds['message_processing_time']:
                    bottlenecks.append({
                        'type': 'message_processing',
                        'severity': 'high' if avg_processing_time > 2.0 * self.thresholds['message_processing_time'] else 'medium',
                        'description': f'消息处理时间过长: 平均 {avg_processing_time:.3f}s',
                        'metric_value': avg_processing_time,
                        'threshold': self.thresholds['message_processing_time'],
                        'timestamp': time.time()
                    })
        
        except Exception as e:
            self.logger.error(f"检测消息处理瓶颈失败: {e}")
        
        return bottlenecks
    
    def _detect_resource_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        检测资源使用瓶颈
        """
        bottlenecks = []
        
        try:
            recent_metrics = self.metrics_collector.get_recent_metrics(count=50)
            
            # 检测内存瓶颈
            memory_metrics = [
                m for m in recent_metrics 
                if m.metric_type == 'gauge' and m.tags.get('gauge_name') == 'system.memory.usage_percent'
            ]
            
            if memory_metrics:
                latest_memory = memory_metrics[-1].value
                
                if latest_memory > self.thresholds['memory_usage_percent']:
                    bottlenecks.append({
                        'type': 'memory_usage',
                        'severity': 'high' if latest_memory > 90.0 else 'medium',
                        'description': f'内存使用率过高: {latest_memory:.1f}%',
                        'metric_value': latest_memory,
                        'threshold': self.thresholds['memory_usage_percent'],
                        'timestamp': time.time()
                    })
            
            # 检测CPU瓶颈
            cpu_metrics = [
                m for m in recent_metrics 
                if m.metric_type == 'gauge' and m.tags.get('gauge_name') == 'system.cpu.usage'
            ]
            
            if cpu_metrics:
                latest_cpu = cpu_metrics[-1].value
                
                if latest_cpu > self.thresholds['cpu_usage_percent']:
                    bottlenecks.append({
                        'type': 'cpu_usage',
                        'severity': 'high' if latest_cpu > 90.0 else 'medium',
                        'description': f'CPU使用率过高: {latest_cpu:.1f}%',
                        'metric_value': latest_cpu,
                        'threshold': self.thresholds['cpu_usage_percent'],
                        'timestamp': time.time()
                    })
        
        except Exception as e:
            self.logger.error(f"检测资源瓶颈失败: {e}")
        
        return bottlenecks
    
    def _detect_queue_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        检测队列性能瓶颈
        """
        bottlenecks = []
        
        try:
            recent_metrics = self.metrics_collector.get_recent_metrics(count=100)
            
            # 查找队列长度指标
            queue_metrics = [
                m for m in recent_metrics 
                if m.metric_type == 'gauge' and m.tags.get('gauge_name') == 'rabbitmq.queue.messages'
            ]
            
            queue_stats = defaultdict(list)
            for metric in queue_metrics:
                queue_name = metric.tags.get('queue', 'unknown')
                queue_stats[queue_name].append(metric)
            
            for queue_name, metrics in queue_stats.items():
                if metrics:
                    latest_length = metrics[-1].value
                    
                    if latest_length > self.thresholds['queue_length']:
                        bottlenecks.append({
                            'type': 'queue_length',
                            'severity': 'high' if latest_length > 2.0 * self.thresholds['queue_length'] else 'medium',
                            'description': f'队列 {queue_name} 长度过长: {int(latest_length)}',
                            'metric_value': latest_length,
                            'threshold': self.thresholds['queue_length'],
                            'queue_name': queue_name,
                            'timestamp': time.time()
                        })
        
        except Exception as e:
            self.logger.error(f"检测队列瓶颈失败: {e}")
        
        return bottlenecks
    
    def _detect_connection_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        检测连接性能瓶颈
        """
        bottlenecks = []
        
        try:
            recent_metrics = self.metrics_collector.get_recent_metrics(count=50)
            
            connection_metrics = [
                m for m in recent_metrics 
                if m.metric_type == 'gauge' and m.tags.get('gauge_name') == 'rabbitmq.connections.active'
            ]
            
            if connection_metrics:
                latest_connections = connection_metrics[-1].value
                
                if latest_connections > self.thresholds['connection_count']:
                    bottlenecks.append({
                        'type': 'connection_count',
                        'severity': 'medium',
                        'description': f'活跃连接数过多: {int(latest_connections)}',
                        'metric_value': latest_connections,
                        'threshold': self.thresholds['connection_count'],
                        'timestamp': time.time()
                    })
        
        except Exception as e:
            self.logger.error(f"检测连接瓶颈失败: {e}")
        
        return bottlenecks
    
    def get_optimization_suggestions(self, bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        获取优化建议
        """
        suggestions = []
        
        for bottleneck in bottlenecks:
            bottleneck_type = bottleneck['type']
            
            if bottleneck_type == 'message_processing':
                suggestions.append({
                    'issue': '消息处理性能瓶颈',
                    'suggestion': '考虑优化消息处理逻辑，增加批量处理，使用异步处理或增加处理线程',
                    'priority': 'high'
                })
            
            elif bottleneck_type == 'memory_usage':
                suggestions.append({
                    'issue': '内存使用率过高',
                    'suggestion': '检查内存泄漏，优化数据结构，考虑增加内存或减少数据缓存',
                    'priority': 'high'
                })
            
            elif bottleneck_type == 'cpu_usage':
                suggestions.append({
                    'issue': 'CPU使用率过高',
                    'suggestion': '优化算法复杂度，考虑水平扩展，启用负载均衡',
                    'priority': 'high'
                })
            
            elif bottleneck_type == 'queue_length':
                suggestions.append({
                    'issue': '队列积压',
                    'suggestion': '增加消费者数量，优化消息处理速度，检查下游系统处理能力',
                    'priority': 'medium'
                })
            
            elif bottleneck_type == 'connection_count':
                suggestions.append({
                    'issue': '连接数过多',
                    'suggestion': '检查连接池配置，实现连接复用，减少不必要的连接创建',
                    'priority': 'medium'
                })
        
        return suggestions
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        生成性能报告
        """
        bottlenecks = self.detect_bottlenecks()
        suggestions = self.get_optimization_suggestions(bottlenecks)
        
        report = {
            'timestamp': time.time(),
            'summary': {
                'total_bottlenecks': len(bottlenecks),
                'high_severity': len([b for b in bottlenecks if b['severity'] == 'high']),
                'medium_severity': len([b for b in bottlenecks if b['severity'] == 'medium'])
            },
            'bottlenecks': bottlenecks,
            'optimization_suggestions': suggestions,
            'metrics_summary': self.metrics_collector.get_metric_summary()
        }
        
        return report
```

## 7. 实战案例与调优指南

### 7.1 高吞吐量场景优化

```python
class HighThroughputOptimizer:
    """
    高吞吐量场景优化器
    """
    
    def __init__(self, connection_pool, metrics_collector):
        self.connection_pool = connection_pool
        self.metrics_collector = metrics_collector
        self.optimization_strategies = {
            'connection_optimization': self._optimize_connections,
            'message_batching': self._optimize_message_batching,
            'prefetch_optimization': self._optimize_prefetch,
            'memory_management': self._optimize_memory_usage,
            'threading_optimization': self._optimize_threading
        }
        self.logger = logging.getLogger(__name__)
    
    def optimize_for_throughput(self, target_throughput: int = 10000) -> Dict[str, Any]:
        """
        为高吞吐量进行优化
        """
        optimization_results = {}
        
        try:
            self.logger.info(f"开始高吞吐量优化，目标: {target_throughput} msg/s")
            
            # 应用各种优化策略
            for strategy_name, strategy_func in self.optimization_strategies.items():
                try:
                    result = strategy_func(target_throughput)
                    optimization_results[strategy_name] = result
                    self.logger.info(f"完成 {strategy_name} 优化")
                    
                except Exception as e:
                    self.logger.error(f"{strategy_name} 优化失败: {e}")
                    optimization_results[strategy_name] = {'error': str(e)}
            
            # 验证优化效果
            validation_result = self._validate_optimization()
            optimization_results['validation'] = validation_result
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"高吞吐量优化失败: {e}")
            return {'error': str(e)}
    
    def _optimize_connections(self, target_throughput: int) -> Dict[str, Any]:
        """
        优化连接配置
        """
        # 根据目标吞吐量计算最优连接数
        optimal_connections = min(target_throughput // 100 + 5, 50)
        
        # 调整连接池大小
        original_size = self.connection_pool.max_connections
        self.connection_pool.max_connections = optimal_connections
        
        # 优化连接参数
        connection_optimizations = {
            'max_connections': optimal_connections,
            'heartbeat': 30,  # 减少心跳间隔
            'connection_timeout': 10,
            'blocked_connection_timeout': 60
        }
        
        self.logger.info(f"连接优化: {original_size} -> {optimal_connections}")
        
        return {
            'original_connections': original_size,
            'optimized_connections': optimal_connections,
            'connection_params': connection_optimizations
        }
    
    def _optimize_message_batching(self, target_throughput: int) -> Dict[str, Any]:
        """
        优化消息批处理
        """
        # 计算最优批次大小
        optimal_batch_size = min(target_throughput // 10, 1000)
        
        batch_optimizations = {
            'batch_size': optimal_batch_size,
            'batch_timeout': 0.1,  # 100ms超时
            'enable_compression': True,
            'enable_deduplication': False  # 吞吐量优先
        }
        
        return {
            'optimal_batch_size': optimal_batch_size,
            'batch_timeout': batch_optimizations['batch_timeout'],
            'compression_enabled': batch_optimizations['enable_compression']
        }
    
    def _optimize_prefetch(self, target_throughput: int) -> Dict[str, Any]:
        """
        优化预取配置
        """
        # 高吞吐量场景使用较大的预取值
        optimal_prefetch = min(target_throughput // 5, 5000)
        
        prefetch_optimizations = {
            'prefetch_count': optimal_prefetch,
            'global_qos': True,  # 全局QoS
            'auto_ack': False   # 手动确认以保证可靠性
        }
        
        return {
            'optimal_prefetch': optimal_prefetch,
            'global_qos': prefetch_optimizations['global_qos']
        }
    
    def _optimize_memory_usage(self, target_throughput: int) -> Dict[str, Any]:
        """
        优化内存使用
        """
        # 为高吞吐量预留更多内存
        memory_optimizations = {
            'max_memory_usage_percent': 70,
            'gc_threshold': 500,  # MB
            'message_cache_size': 10000,
            'enable_compression': True,
            'compression_threshold': 1024  # 1KB以上压缩
        }
        
        return memory_optimizations
    
    def _optimize_threading(self, target_throughput: int) -> Dict[str, Any]:
        """
        优化线程配置
        """
        # 计算最优工作线程数
        cpu_count = os.cpu_count() or 4
        optimal_workers = min(target_throughput // 100 + cpu_count, 32)
        
        threading_optimizations = {
            'worker_threads': optimal_workers,
            'io_threads': min(cpu_count, 8),
            'thread_pool_size': optimal_workers * 2,
            'enable_thread_pool': True
        }
        
        return threading_optimizations
    
    def _validate_optimization(self) -> Dict[str, Any]:
        """
        验证优化效果
        """
        # 执行短时间的性能测试
        test_duration = 10  # 10秒测试
        
        # 记录测试开始时的指标
        start_metrics = self.metrics_collector.get_metric_summary()
        
        # 执行测试（这里需要实际的发送/接收测试）
        time.sleep(test_duration)
        
        # 记录测试结束后的指标
        end_metrics = self.metrics_collector.get_metric_summary()
        
        validation_result = {
            'test_duration': test_duration,
            'start_metrics': start_metrics,
            'end_metrics': end_metrics,
            'recommendations': []
        }
        
        # 基于测试结果给出建议
        if validation_result['recommendations']:
            validation_result['optimization_needed'] = True
        else:
            validation_result['optimization_needed'] = False
        
        return validation_result

# 高吞吐量消费者示例
class HighThroughputConsumer:
    """
    高吞吐量消费者
    """
    
    def __init__(self, connection_pool, batch_size: int = 100, prefetch_count: int = 1000):
        self.connection_pool = connection_pool
        self.batch_size = batch_size
        self.prefetch_count = prefetch_count
        self.is_running = False
        self.processed_messages = 0
        self.processing_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def start_consuming(self, queue_name: str, num_workers: int = 10):
        """
        开始消费消息
        """
        self.is_running = True
        
        # 创建工作线程
        workers = []
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_thread,
                args=(queue_name, f"worker_{i}"),
                daemon=True
            )
            worker.start()
            workers.append(worker)
        
        self.logger.info(f"启动 {num_workers} 个工作线程消费队列: {queue_name}")
        
        # 等待所有工作线程完成
        for worker in workers:
            worker.join()
    
    def _worker_thread(self, queue_name: str, worker_id: str):
        """
        工作线程
        """
        while self.is_running:
            try:
                # 获取连接
                connection = self.connection_pool.get_connection()
                if not connection:
                    time.sleep(1)
                    continue
                
                # 创建通道
                channel = connection.channel()
                channel.basic_qos(prefetch_count=self.prefetch_count)
                
                # 批量消费消息
                self._batch_consume(channel, queue_name, worker_id)
                
                # 归还连接
                self.connection_pool.return_connection(connection)
                
            except Exception as e:
                self.logger.error(f"工作线程 {worker_id} 错误: {e}")
                time.sleep(1)
    
    def _batch_consume(self, channel, queue_name: str, worker_id: str):
        """
        批量消费消息
        """
        batch = []
        
        try:
            # 批量获取消息
            for _ in range(self.batch_size):
                try:
                    method_frame, header_frame, body = channel.basic_get(queue_name, auto_ack=False)
                    
                    if method_frame:
                        batch.append((method_frame, header_frame, body))
                    else:
                        break  # 队列为空
                        
                except Exception as e:
                    self.logger.error(f"获取消息失败: {e}")
                    break
            
            # 批量处理消息
            if batch:
                self._process_batch(batch, worker_id)
                
                # 批量确认
                for method_frame, _, _ in batch:
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        
        except Exception as e:
            self.logger.error(f"批量消费失败: {e}")
            
            # 批量拒绝（重新入队）
            for method_frame, _, _ in batch:
                try:
                    channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
                except:
                    pass
    
    def _process_batch(self, batch: List, worker_id: str):
        """
        批量处理消息
       