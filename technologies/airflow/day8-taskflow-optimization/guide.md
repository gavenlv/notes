# Day 8: 任务流优化完整指南

## 概述

任务流优化是Airflow生产环境中的核心技能，直接影响数据处理效率、系统稳定性和资源利用率。本指南将深入探讨Airflow任务流优化的各个方面，从基础概念到高级技术，帮助你构建高性能的数据处理管道。

## 学习目标

完成本指南后，你将掌握：

- ✅ **性能调优策略**: DAG级别和操作符级别的优化技术
- ✅ **并发控制机制**: 理解并配置各种并发参数
- ✅ **资源管理技术**: 内存、CPU、磁盘I/O的优化方法
- ✅ **监控体系建设**: 建立完善的性能监控和告警机制
- ✅ **问题诊断技能**: 快速定位和解决性能瓶颈
- ✅ **最佳实践应用**: 在生产环境中应用优化技术

## 核心概念

### 1. 性能优化的重要性

在生产环境中，性能优化直接影响：
- **执行效率**: 减少任务执行时间，提高吞吐量
- **资源利用率**: 优化CPU、内存、磁盘和网络资源使用
- **成本控制**: 减少基础设施成本，提高ROI
- **用户体验**: 缩短数据处理延迟，提升服务质量
- **系统稳定性**: 避免资源耗尽导致的系统故障

### 2. 性能瓶颈类型

了解常见的性能瓶颈：
- **CPU瓶颈**: 计算密集型任务导致CPU使用率过高
- **内存瓶颈**: 内存泄漏或大数据集处理导致内存不足
- **I/O瓶颈**: 磁盘读写或网络传输速度限制
- **数据库瓶颈**: 查询性能差、连接数限制、锁竞争
- **配置瓶颈**: 不合理的并发参数或资源限制

### 3. 优化策略层次

性能优化涉及多个层次：
- **应用层**: DAG设计、任务逻辑、算法优化
- **框架层**: Airflow配置、执行器选择、参数调优
- **系统层**: 操作系统配置、资源分配、网络优化
- **基础设施层**: 硬件规格、云服务配置、架构设计

## 性能调优策略

### 1. DAG级别优化

#### 任务设计优化
```python
# 优化前：串行执行，效率低
def suboptimal_dag():
    task1 >> task2 >> task3 >> task4

# 优化后：并行执行，效率高
def optimized_dag():
    [task1, task2] >> task3 >> [task4, task5]
```

#### 依赖关系优化
- **最小化依赖**: 只建立必要的任务依赖
- **并行化设计**: 识别可以并行执行的任务
- **任务分组**: 使用TaskGroup组织相关任务
- **条件分支**: 使用BranchPythonOperator优化条件执行

#### 执行策略优化
```python
dag = DAG(
    'optimized_dag',
    max_active_tasks=10,      # 限制并发任务数
    max_active_runs=1,        # 限制并发DAG运行数
    catchup=False,            # 禁用回填避免资源浪费
    schedule_interval='@hourly', # 合理调度间隔
)
```

### 2. 操作符级别优化

#### 批量处理优化
```python
def batch_process_large_dataset(**context):
    """批量处理大数据集"""
    batch_size = 1000  # 根据内存和性能调整批次大小
    
    # 使用生成器减少内存占用
    def data_generator():
        for record in fetch_large_dataset():
            yield record
    
    batch = []
    for record in data_generator():
        batch.append(record)
        
        if len(batch) >= batch_size:
            process_batch(batch)
            batch.clear()  # 清理内存
            gc.collect()   # 垃圾回收
    
    # 处理剩余数据
    if batch:
        process_batch(batch)
```

#### 连接池优化
```python
# 使用连接池避免频繁创建连接
from airflow.hooks.base import BaseHook

def optimized_database_operation(**context):
    conn = BaseHook.get_connection('my_database')
    
    # 使用连接池
    with conn.get_hook().get_conn() as connection:
        cursor = connection.cursor()
        
        # 批量操作
        cursor.executemany(
            "INSERT INTO table VALUES (%s, %s)",
            batch_data
        )
        connection.commit()
```

#### 内存使用优化
```python
def memory_optimized_processing(**context):
    """内存优化的数据处理"""
    # 使用迭代器而非列表
    def process_large_file(filename):
        with open(filename, 'r') as file:
            for line in file:
                yield process_line(line)
    
    # 及时释放内存
    results = []
    for processed_data in process_large_file('large_file.txt'):
        results.append(processed_data)
        
        # 定期清理内存
        if len(results) > 1000:
            save_results(results)
            results.clear()
            gc.collect()
```

### 3. 数据库性能优化

#### 查询优化
```python
def optimized_database_query(**context):
    """优化的数据库查询"""
    # 使用索引
    query = """
        SELECT column1, column2 
        FROM large_table 
        WHERE indexed_column = %s
        ORDER BY indexed_column
        LIMIT %s
    """
    
    # 使用预编译语句
    with connection.cursor() as cursor:
        cursor.execute(query, (value, limit))
        results = cursor.fetchall()
```

#### 连接优化
```python
# 数据库连接配置优化
database_config = {
    'pool_size': 10,        # 连接池大小
    'max_overflow': 20,     # 最大溢出连接数
    'pool_timeout': 30,     # 连接超时时间
    'pool_recycle': 3600,   # 连接回收时间
    'echo': False,          # 禁用SQL日志
}
```

## 并发执行控制

### 1. 并发参数配置

#### 全局并发参数
```python
# airflow.cfg 配置
[core]
parallelism = 32                    # 全局最大并发任务数
dag_concurrency = 16               # 每个DAG最大并发任务数
max_active_runs_per_dag = 3        # 每个DAG最大并发运行数

[scheduler]
max_threads = 4                    # 调度器线程数
processor_poll_interval = 1        # 处理器轮询间隔
```

#### DAG级别并发控制
```python
dag = DAG(
    'concurrency_demo',
    max_active_tasks=8,     # DAG级别任务并发限制
    max_active_runs=2,      # DAG级别运行并发限制
    concurrency=4,          # 向后兼容的参数
)
```

#### 任务级别并发控制
```python
task = PythonOperator(
    task_id='limited_task',
    python_callable=my_function,
    pool='resource_pool',   # 使用资源池
    pool_slots=2,           # 占用资源池槽位数
    priority_weight=5,      # 任务优先级
    weight_rule='downstream', # 权重计算规则
    dag=dag,
)
```

### 2. 资源池管理

#### 创建资源池
```python
from airflow.models import Pool
from airflow.utils.db import create_session

def create_resource_pools():
    """创建资源池"""
    pools = [
        Pool(pool='cpu_intensive_pool', slots=2, description='CPU密集型任务'),
        Pool(pool='io_intensive_pool', slots=4, description='IO密集型任务'),
        Pool(pool='database_pool', slots=3, description='数据库连接池'),
        Pool(pool='api_pool', slots=5, description='API调用池'),
    ]
    
    with create_session() as session:
        for pool in pools:
            existing = session.query(Pool).filter(Pool.pool == pool.pool).first()
            if not existing:
                session.add(pool)
```

#### 使用资源池
```python
def cpu_intensive_task(**context):
    """CPU密集型任务"""
    # 模拟CPU密集型计算
    result = perform_complex_calculation()
    return result

# 使用CPU资源池
cpu_task = PythonOperator(
    task_id='cpu_intensive_task',
    python_callable=cpu_intensive_task,
    pool='cpu_intensive_pool',  # 限制CPU密集型任务并发
    dag=dag,
)
```

### 3. 执行器优化

#### LocalExecutor优化
```python
# 本地执行器配置
[core]
executor = LocalExecutor
parallelism = 16                  # 根据CPU核心数设置
dag_concurrency = 8               # 减少并发避免资源竞争
```

#### CeleryExecutor优化
```python
# Celery执行器配置
[celery]
worker_concurrency = 8            # 每个worker的并发数
worker_prefetch_multiplier = 1    # 预取倍数
worker_max_tasks_per_child = 1000 # 每个子进程最大任务数

# Redis配置
[celery_broker_transport_options]
visibility_timeout = 21600        # 可见性超时
max_retries = 3                   # 最大重试次数
```

## 内存和资源配置

### 1. 内存优化策略

#### 内存监控
```python
import psutil
import gc

def memory_aware_processing(**context):
    """内存感知的数据处理"""
    process = psutil.Process()
    
    # 监控内存使用
    def log_memory_usage(stage):
        memory_mb = process.memory_info().rss / 1024 / 1024
        logging.info(f"内存使用 [{stage}]: {memory_mb:.2f} MB")
        return memory_mb
    
    # 初始内存
    initial_memory = log_memory_usage("开始")
    
    # 处理大数据集
    for batch in read_data_in_batches():
        process_batch(batch)
        
        # 检查内存使用
        current_memory = log_memory_usage("批处理后")
        
        # 如果内存使用过高，进行清理
        if current_memory > initial_memory + 500:  # 超过500MB
            gc.collect()  # 垃圾回收
            log_memory_usage("垃圾回收后")
            
            # 如果仍然过高，暂停处理
            if current_memory > initial_memory + 800:
                logging.warning("内存使用过高，暂停处理")
                time.sleep(10)
```

#### 内存泄漏预防
```python
class MemoryEfficientProcessor:
    """内存高效的数据处理器"""
    
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.processed_count = 0
    
    def process_large_dataset(self, data_source):
        """处理大数据集"""
        try:
            batch = []
            
            for record in data_source:
                batch.append(record)
                
                if len(batch) >= self.batch_size:
                    self._process_batch(batch)
                    batch.clear()  # 显式清理
                    
                    # 定期垃圾回收
                    if self.processed_count % (self.batch_size * 10) == 0:
                        gc.collect()
            
            # 处理剩余数据
            if batch:
                self._process_batch(batch)
                
        except Exception as e:
            logging.error(f"处理失败: {e}")
            raise
        finally:
            # 确保资源清理
            gc.collect()
    
    def _process_batch(self, batch):
        """处理批次数据"""
        # 处理逻辑
        self.processed_count += len(batch)
        logging.info(f"已处理: {self.processed_count}")
```

### 2. CPU资源管理

#### 多核利用优化
```python
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

def parallel_data_processing(data_list, num_workers=None):
    """并行数据处理"""
    if num_workers is None:
        num_workers = min(multiprocessing.cpu_count(), 8)  # 限制最大8个worker
    
    # 数据分片
    chunk_size = len(data_list) // num_workers + 1
    chunks = [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]
    
    results = []
    
    # 使用进程池
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # 提交任务
        future_to_chunk = {
            executor.submit(process_chunk, chunk): chunk 
            for chunk in chunks
        }
        
        # 收集结果
        for future in as_completed(future_to_chunk):
            chunk = future_to_chunk[future]
            try:
                result = future.result(timeout=300)  # 5分钟超时
                results.extend(result)
            except Exception as exc:
                logging.error(f"处理块失败: {chunk[:100]}... 错误: {exc}")
                raise
    
    return results

def process_chunk(chunk):
    """处理数据块"""
    results = []
    for item in chunk:
        processed = process_item(item)
        results.append(processed)
    return results
```

#### CPU亲和性设置
```python
import os

def set_cpu_affinity(cpu_cores):
    """设置CPU亲和性"""
    try:
        # Linux系统下设置CPU亲和性
        os.system(f"taskset -cp {cpu_cores} {os.getpid()}")
        logging.info(f"CPU亲和性设置为: {cpu_cores}")
    except Exception as e:
        logging.warning(f"设置CPU亲和性失败: {e}")
```

### 3. 磁盘I/O优化

#### 文件操作优化
```python
def optimized_file_processing(filename):
    """优化的文件处理"""
    # 使用适当的缓冲区大小
    buffer_size = 8 * 1024 * 1024  # 8MB缓冲区
    
    with open(filename, 'r', buffering=buffer_size) as file:
        for line in file:
            # 逐行处理，避免一次性加载整个文件
            process_line(line)

def batch_file_write(data, filename):
    """批量文件写入"""
    # 收集数据后批量写入
    buffer = []
    
    with open(filename, 'w', buffering=8192) as file:
        for item in data:
            buffer.append(str(item) + '\n')
            
            if len(buffer) >= 1000:  # 每1000行写入一次
                file.writelines(buffer)
                buffer.clear()
        
        # 写入剩余数据
        if buffer:
            file.writelines(buffer)
```

#### 临时文件管理
```python
import tempfile
import shutil

def temp_file_processing(data):
    """临时文件处理"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_files = []
        
        try:
            # 分批处理数据
            for batch_num, batch in enumerate(create_batches(data)):
                temp_file = os.path.join(temp_dir, f"batch_{batch_num}.tmp")
                
                # 写入临时文件
                with open(temp_file, 'w') as f:
                    json.dump(batch, f)
                
                temp_files.append(temp_file)
                
                # 处理临时文件
                process_temp_file(temp_file)
            
            # 临时目录会自动清理
            logging.info(f"处理了 {len(temp_files)} 个临时文件")
            
        except Exception as e:
            logging.error(f"临时文件处理失败: {e}")
            raise
```

## 监控和指标收集

### 1. 性能指标定义

#### 关键性能指标(KPI)
```python
@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    
    # 时间指标
    execution_time: float          # 执行时间
    queue_time: float            # 排队时间
    total_duration: float          # 总持续时间
    
    # 资源指标
    cpu_usage: float              # CPU使用率
    memory_usage: float            # 内存使用量
    disk_io_rate: float           # 磁盘I/O速率
    network_io_rate: float        # 网络I/O速率
    
    # 业务指标
    records_processed: int       # 处理记录数
    throughput: float            # 吞吐量
    error_rate: float            # 错误率
    success_rate: float          # 成功率
```

#### 指标收集装饰器
```python
def performance_monitor(metric_name: str, track_memory: bool = True):
    """性能监控装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 开始监控
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss if track_memory else 0
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算指标
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss if track_memory else 0
                
                execution_time = end_time - start_time
                memory_used = (end_memory - start_memory) / 1024 / 1024  # MB
                
                # 记录指标
                logging.info(f"[{metric_name}] 执行时间: {execution_time:.3f}s, 内存使用: {memory_used:.2f}MB")
                
                # 发送到监控系统（如StatsD）
                if statsd_client:
                    statsd_client.timing(f"{metric_name}.execution_time", execution_time * 1000)
                    statsd_client.gauge(f"{metric_name}.memory_usage", memory_used)
                
                return result
                
            except Exception as e:
                # 记录错误指标
                if statsd_client:
                    statsd_client.increment(f"{metric_name}.errors")
                logging.error(f"[{metric_name}] 执行失败: {e}")
                raise
        
        return wrapper
    return decorator
```

### 2. 监控系统集成

#### StatsD集成
```python
import statsd

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, host='localhost', port=8125, prefix='airflow'):
        self.client = statsd.StatsClient(host, port, prefix)
    
    def record_execution_time(self, metric_name, duration_ms, tags=None):
        """记录执行时间"""
        self.client.timing(metric_name, duration_ms)
    
    def record_gauge(self, metric_name, value, tags=None):
        """记录仪表盘指标"""
        self.client.gauge(metric_name, value)
    
    def increment_counter(self, metric_name, value=1, tags=None):
        """增加计数器"""
        self.client.incr(metric_name, value)
    
    def record_histogram(self, metric_name, value, tags=None):
        """记录直方图指标"""
        # StatsD不支持直方图，使用计时器作为替代
        self.client.timing(metric_name, value)
```

#### Prometheus集成
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 定义指标
execution_time_histogram = Histogram(
    'airflow_task_execution_time_seconds',
    'Task execution time in seconds',
    ['dag_id', 'task_id', 'status']
)

task_counter = Counter(
    'airflow_task_total',
    'Total number of tasks executed',
    ['dag_id', 'task_id', 'status']
)

memory_usage_gauge = Gauge(
    'airflow_task_memory_usage_mb',
    'Task memory usage in MB',
    ['dag_id', 'task_id']
)

class PrometheusMetricsCollector:
    """Prometheus指标收集器"""
    
    def record_task_execution(self, dag_id, task_id, duration, status, memory_mb):
        """记录任务执行指标"""
        labels = {'dag_id': dag_id, 'task_id': task_id, 'status': status}
        
        execution_time_histogram.labels(**labels).observe(duration)
        task_counter.labels(**labels).inc()
        memory_usage_gauge.labels(dag_id=dag_id, task_id=task_id).set(memory_mb)
```

### 3. 日志和追踪

#### 结构化日志
```python
import json
import logging

class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log_performance(self, level, message, **kwargs):
        """记录性能日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'performance_data': kwargs
        }
        
        self.logger.log(level, json.dumps(log_entry))
    
    def log_task_execution(self, dag_id, task_id, execution_time, memory_usage, status):
        """记录任务执行日志"""
        self.log_performance(
            logging.INFO,
            f"Task {task_id} in DAG {dag_id} completed",
            dag_id=dag_id,
            task_id=task_id,
            execution_time_seconds=execution_time,
            memory_usage_mb=memory_usage,
            status=status
        )
```

#### 分布式追踪
```python
from jaeger_client import Config

class DistributedTracer:
    """分布式追踪器"""
    
    def __init__(self, service_name='airflow'):
        config = Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'local_agent': {
                    'reporting_host': 'jaeger-agent',
                    'reporting_port': '6831',
                },
                'logging': True,
            },
            service_name=service_name,
        )
        
        self.tracer = config.initialize_tracer()
    
    def trace_task_execution(self, dag_id, task_id, func, *args, **kwargs):
        """追踪任务执行"""
        with self.tracer.start_span(f"{dag_id}.{task_id}") as span:
            span.set_tag('dag_id', dag_id)
            span.set_tag('task_id', task_id)
            
            try:
                result = func(*args, **kwargs)
                span.set_tag('status', 'success')
                return result
            except Exception as e:
                span.set_tag('status', 'error')
                span.set_tag('error.message', str(e))
                raise
```

## 高级优化技术

### 1. 缓存策略

#### 内存缓存
```python
from functools import lru_cache
import hashlib

class MemoryCache:
    """内存缓存管理器"""
    
    def __init__(self, max_size=1000, ttl=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, key):
        """获取缓存值"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        """设置缓存值"""
        # 清理过期缓存
        self._cleanup_expired()
        
        # 如果缓存已满，清理最旧的
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, time.time())
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, (value, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]

# 使用装饰器实现函数缓存
def cache_result(ttl=3600, max_size=100):
    """结果缓存装饰器"""
    def decorator(func):
        cache = MemoryCache(max_size, ttl)
        
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logging.info(f"缓存命中: {func.__name__}")
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator

def _generate_cache_key(func_name, args, kwargs):
    """生成缓存键"""
    key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
    return hashlib.md5(key_data.encode()).hexdigest()

# 使用示例
@cache_result(ttl=1800)  # 30分钟缓存
def expensive_computation(param1, param2):
    """昂贵的计算函数"""
    time.sleep(2)  # 模拟耗时操作
    return param1 * param2 + random.randint(1, 100)
```

#### 分布式缓存
```python
import redis
import pickle

class RedisCache:
    """Redis分布式缓存"""
    
    def __init__(self, host='localhost', port=6379, db=0, ttl=3600):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.ttl = ttl
    
    def get(self, key):
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            logging.error(f"Redis缓存获取失败: {e}")
        return None
    
    def set(self, key, value, ttl=None):
        """设置缓存值"""
        try:
            serialized_value = pickle.dumps(value)
            expire_time = ttl or self.ttl
            self.redis_client.setex(key, expire_time, serialized_value)
        except Exception as e:
            logging.error(f"Redis缓存设置失败: {e}")
    
    def delete(self, key):
        """删除缓存"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logging.error(f"Redis缓存删除失败: {e}")
    
    def clear_pattern(self, pattern):
        """清除匹配模式的缓存"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logging.error(f"Redis缓存清理失败: {e}")
```

### 2. 异步处理

#### 异步任务执行
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class AsyncTaskProcessor:
    """异步任务处理器"""
    
    def __init__(self, max_workers=10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_tasks_async(self, tasks):
        """异步处理任务"""
        # 创建异步任务
        async_tasks = [
            self._execute_task_async(task) 
            for task in tasks
        ]
        
        # 并发执行
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # 处理结果
        successful_results = []
        failed_tasks = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_tasks.append((tasks[i], result))
            else:
                successful_results.append(result)
        
        return {
            'successful': successful_results,
            'failed': failed_tasks,
            'total': len(tasks),
            'success_rate': len(successful_results) / len(tasks) * 100
        }
    
    async def _execute_task_async(self, task):
        """异步执行任务"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中执行阻塞操作
        result = await loop.run_in_executor(
            self.executor,
            self._execute_task_sync,
            task
        )
        
        return result
    
    def _execute_task_sync(self, task):
        """同步执行任务（阻塞操作）"""
        # 模拟耗时操作
        time.sleep(random.uniform(0.1, 0.5))
        return f"任务 {task} 完成"
    
    def close(self):
        """关闭处理器"""
        self.executor.shutdown(wait=True)

# 使用示例
async def demo_async_processing():
    """演示异步处理"""
    processor = AsyncTaskProcessor(max_workers=5)
    
    # 创建测试任务
    tasks = list(range(20))
    
    # 异步处理
    results = await processor.process_tasks_async(tasks)
    
    logging.info(f"异步处理完成: {results['success_rate']:.1f}% 成功率")
    
    # 关闭处理器
    processor.close()
    
    return results
```

#### 异步HTTP请求
```python
import aiohttp
import asyncio

class AsyncHTTPClient:
    """异步HTTP客户端"""
    
    def __init__(self, max_connections=100, timeout=30):
        self.max_connections = max_connections
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器进入"""
        connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def fetch_url(self, url, method='GET', **kwargs):
        """获取URL内容"""
        try:
            async with self.session.request(method, url, **kwargs) as response:
                content = await response.text()
                return {
                    'url': url,
                    'status': response.status,
                    'content': content,
                    'headers': dict(response.headers)
                }
        except Exception as e:
            logging.error(f"获取URL失败 {url}: {e}")
            return {
                'url': url,
                'status': None,
                'error': str(e)
            }
    
    async def fetch_multiple_urls(self, urls, method='GET', **kwargs):
        """并发获取多个URL"""
        tasks = [
            self.fetch_url(url, method, **kwargs) 
            for url in urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        successful = []
        failed = []
        
        for result in results:
            if isinstance(result, Exception):
                failed.append({'error': str(result)})
            elif result.get('status') == 200:
                successful.append(result)
            else:
                failed.append(result)
        
        return {
            'successful': successful,
            'failed': failed,
            'total': len(urls),
            'success_rate': len(successful) / len(urls) * 100
        }
```

### 3. 数据分区策略

#### 水平分区
```python
class HorizontalPartitioner:
    """水平分区器"""
    
    def __init__(self, num_partitions, partition_key):
        self.num_partitions = num_partitions
        self.partition_key = partition_key
    
    def partition_data(self, data_list):
        """对数据进行水平分区"""
        partitions = [[] for _ in range(self.num_partitions)]
        
        for item in data_list:
            # 计算分区索引
            partition_index = self._calculate_partition_index(item)
            partitions[partition_index].append(item)
        
        return partitions
    
    def _calculate_partition_index(self, item):
        """计算分区索引"""
        # 基于哈希的分区
        key_value = item.get(self.partition_key, '')
        return hash(key_value) % self.num_partitions
    
    def process_partitions_parallel(self, data_list, process_func):
        """并行处理分区数据"""
        partitions = self.partition_data(data_list)
        
        with ProcessPoolExecutor(max_workers=self.num_partitions) as executor:
            # 提交分区处理任务
            futures = [
                executor.submit(process_func, partition, partition_id)
                for partition_id, partition in enumerate(partitions)
                if partition  # 只处理非空分区
            ]
            
            # 收集结果
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=300)
                    results.append(result)
                except Exception as e:
                    logging.error(f"分区处理失败: {e}")
                    raise
        
        return results

# 使用示例
def process_partition(partition_data, partition_id):
    """处理单个分区"""
    logging.info(f"处理分区 {partition_id}，数据量: {len(partition_data)}")
    
    # 模拟处理
    processed_count = 0
    for item in partition_data:
        # 处理逻辑
        processed_count += 1
        if processed_count % 1000 == 0:
            logging.info(f"分区 {partition_id} 处理进度: {processed_count}")
    
    return {
        'partition_id': partition_id,
        'processed_count': processed_count,
        'status': 'completed'
    }
```

#### 时间分区
```python
from datetime import datetime, timedelta

class TimePartitioner:
    """时间分区器"""
    
    def __init__(self, time_interval, time_field='timestamp'):
        self.time_interval = time_interval  # 例如: timedelta(hours=1)
        self.time_field = time_field
    
    def partition_by_time(self, data_list):
        """按时间分区"""
        partitions = {}
        
        for item in data_list:
            timestamp = item.get(self.time_field)
            if not timestamp:
                continue
            
            # 计算时间窗口
            time_window = self._get_time_window(timestamp)
            
            if time_window not in partitions:
                partitions[time_window] = []
            
            partitions[time_window].append(item)
        
        return partitions
    
    def _get_time_window(self, timestamp):
        """获取时间窗口"""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        # 计算时间窗口的开始时间
        window_start = timestamp - timedelta(
            seconds=timestamp.timestamp() % self.time_interval.total_seconds()
        )
        
        return window_start
    
    def create_time_based_dag(self, start_date, end_date, process_func):
        """创建基于时间的DAG"""
        current_date = start_date
        tasks = []
        
        while current_date < end_date:
            next_date = current_date + self.time_interval
            
            # 为每个时间窗口创建任务
            task_id = f"process_{current_date.strftime('%Y%m%d_%H')}"
            
            task = PythonOperator(
                task_id=task_id,
                python_callable=process_func,
                op_kwargs={
                    'start_time': current_date,
                    'end_time': next_date
                },
                dag=dag,
            )
            
            tasks.append(task)
            current_date = next_date
        
        # 设置任务依赖
        for i in range(len(tasks) - 1):
            tasks[i] >> tasks[i + 1]
        
        return tasks
```

## 错误处理和重试

### 1. 智能重试策略

#### 指数退避重试
```python
import random
import time

class ExponentialBackoffRetry:
    """指数退避重试机制"""
    
    def __init__(self, base_delay=1, max_delay=60, max_attempts=3, jitter=True):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_attempts = max_attempts
        self.jitter = jitter
    
    def execute_with_retry(self, func, *args, **kwargs):
        """执行函数并应用重试逻辑"""
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                return result
            
            except Exception as e:
                if attempt == self.max_attempts:
                    logging.error(f"函数执行失败，已达到最大重试次数: {e}")
                    raise
                
                # 计算延迟时间
                delay = self._calculate_delay(attempt)
                
                logging.warning(f"函数执行失败 (尝试 {attempt}/{self.max_attempts}): {e}")
                logging.info(f"等待 {delay:.2f} 秒后重试")
                
                time.sleep(delay)
    
    def _calculate_delay(self, attempt):
        """计算延迟时间"""
        # 指数退避: base_delay * (2 ^ (attempt - 1))
        delay = self.base_delay * (2 ** (attempt - 1))
        
        # 应用最大延迟限制
        delay = min(delay, self.max_delay)
        
        # 添加随机抖动
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay

# 使用示例
@performance_monitor("retry_operation")
def unreliable_operation():
    """不稳定的操作"""
    if random.random() < 0.7:  # 70%失败率
        raise Exception("模拟随机失败")
    return "操作成功"

# 应用重试机制
retry_handler = ExponentialBackoffRetry(
    base_delay=1,
    max_delay=30,
    max_attempts=5,
    jitter=True
)

result = retry_handler.execute_with_retry(unreliable_operation)
```

#### 条件重试
```python
class ConditionalRetry:
    """条件重试机制"""
    
    def __init__(self, retry_conditions, max_attempts=3, base_delay=1):
        self.retry_conditions = retry_conditions
        self.max_attempts = max_attempts
        self.base_delay = base_delay
    
    def should_retry(self, exception):
        """判断是否应该重试"""
        exception_type = type(exception)
        exception_message = str(exception)
        
        for condition in self.retry_conditions:
            # 检查异常类型
            if 'exception_types' in condition:
                if not any(isinstance(exception, exc_type) for exc_type in condition['exception_types']):
                    continue
            
            # 检查异常消息
            if 'message_patterns' in condition:
                if not any(pattern in exception_message for pattern in condition['message_patterns']):
                    continue
            
            # 检查重试策略
            retry_config = condition.get('retry_config', {})
            return {
                'should_retry': True,
                'max_attempts': retry_config.get('max_attempts', self.max_attempts),
                'base_delay': retry_config.get('base_delay', self.base_delay),
            }
        
        return {'should_retry': False}
    
    def execute_with_conditional_retry(self, func, *args, **kwargs):
        """执行函数并应用条件重试"""
        attempt = 1
        max_attempts = self.max_attempts
        base_delay = self.base_delay
        
        while attempt <= max_attempts:
            try:
                result = func(*args, **kwargs)
                return result
            
            except Exception as e:
                retry_decision = self.should_retry(e)
                
                if not retry_decision['should_retry']:
                    logging.error(f"异常类型不允许重试: {e}")
                    raise
                
                # 更新重试配置
                max_attempts = retry_decision.get('max_attempts', max_attempts)
                base_delay = retry_decision.get('base_delay', base_delay)
                
                if attempt >= max_attempts:
                    logging.error(f"函数执行失败，已达到最大重试次数 {max_attempts}: {e}")
                    raise
                
                delay = base_delay * (2 ** (attempt - 1))
                logging.warning(f"函数执行失败 (尝试 {attempt}/{max_attempts}): {e}")
                logging.info(f"等待 {delay:.2f} 秒后重试")
                
                time.sleep(delay)
                attempt += 1

# 定义重试条件
retry_conditions = [
    {
        'exception_types': [ConnectionError, TimeoutError],
        'message_patterns': ['connection', 'timeout', 'network'],
        'retry_config': {
            'max_attempts': 5,
            'base_delay': 2
        }
    },
    {
        'exception_types': [ValueError],
        'message_patterns': ['invalid', 'format'],
        'retry_config': {
            'max_attempts': 2,
            'base_delay': 1
        }
    },
    {
        'exception_types': [Exception],
        'message_patterns': ['temporary', 'transient'],
        'retry_config': {
            'max_attempts': 3,
            'base_delay': 1
        }
    }
]

# 使用条件重试
conditional_retry = ConditionalRetry(retry_conditions)
```

### 2. 错误分类和处理

#### 错误分类器
```python
class ErrorClassifier:
    """错误分类器"""
    
    def __init__(self):
        self.error_categories = {
            'network': {
                'exception_types': [ConnectionError, TimeoutError, requests.exceptions.RequestException],
                'message_patterns': ['connection', 'timeout', 'network', 'dns'],
                'severity': 'warning',
                'retry_strategy': 'exponential'
            },
            'database': {
                'exception_types': [psycopg2.Error, sqlalchemy.exc.SQLAlchemyError],
                'message_patterns': ['database', 'sql', 'connection', 'timeout'],
                'severity': 'error',
                'retry_strategy': 'linear'
            },
            'validation': {
                'exception_types': [ValueError, TypeError, ValidationError],
                'message_patterns': ['invalid', 'validation', 'format', 'required'],
                'severity': 'error',
                'retry_strategy': 'none'
            },
            'resource': {
                'exception_types': [MemoryError, OSError],
                'message_patterns': ['memory', 'disk', 'resource', 'quota'],
                'severity': 'critical',
                'retry_strategy': 'backoff'
            }
        }
    
    def classify_error(self, exception):
        """分类错误"""
        exception_type = type(exception)
        exception_message = str(exception).lower()
        
        for category, config in self.error_categories.items():
            # 检查异常类型
            type_match = any(
                isinstance(exception, exc_type) 
                for exc_type in config['exception_types']
            )
            
            # 检查异常消息
            message_match = any(
                pattern in exception_message 
                for pattern in config['message_patterns']
            )
            
            if type_match or message_match:
                return {
                    'category': category,
                    'severity': config['severity'],
                    'retry_strategy': config['retry_strategy'],
                    'original_error': str(exception)
                }
        
        # 默认分类
        return {
            'category': 'unknown',
            'severity': 'error',
            'retry_strategy': 'exponential',
            'original_error': str(exception)
        }
    
    def get_error_handler(self, error_category):
        """获取错误处理器"""
        category_config = self.error_categories.get(error_category, {})
        
        retry_strategy = category_config.get('retry_strategy', 'none')
        
        if retry_strategy == 'exponential':
            return ExponentialBackoffRetry()
        elif retry_strategy == 'linear':
            return LinearBackoffRetry()
        elif retry_strategy == 'backoff':
            return BackoffRetry()
        else:
            return NoRetry()

class LinearBackoffRetry:
    """线性退避重试"""
    
    def __init__(self, base_delay=1, max_delay=30, max_attempts=3):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_attempts = max_attempts
    
    def execute_with_retry(self, func, *args, **kwargs):
        """执行函数并应用线性重试"""
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if attempt == self.max_attempts:
                    raise
                
                delay = min(self.base_delay * attempt, self.max_delay)
                logging.warning(f"尝试 {attempt} 失败，等待 {delay}s 后重试: {e}")
                time.sleep(delay)

class BackoffRetry:
    """退避重试"""
    
    def __init__(self, initial_delay=1, backoff_factor=2, max_delay=60):
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
    
    def execute_with_retry(self, func, *args, **kwargs):
        """执行函数并应用退避重试"""
        delay = self.initial_delay
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                
                logging.warning(f"尝试 {attempt + 1} 失败，等待 {delay}s: {e}")
                time.sleep(delay)
                
                # 增加延迟
                delay = min(delay * self.backoff_factor, self.max_delay)

class NoRetry:
    """不重试"""
    
    def execute_with_retry(self, func, *args, **kwargs):
        """直接执行函数，不重试"""
        return func(*args, **kwargs)
```

## 最佳实践和常见陷阱

### 1. 性能优化最佳实践

#### 设计阶段优化
```python
# 1. 任务粒度设计
class TaskGranularityOptimizer:
    """任务粒度优化器"""
    
    @staticmethod
    def optimal_batch_size(data_size, available_memory, processing_time_per_item):
        """计算最优批次大小"""
        # 基于可用内存和处理时间计算
        memory_based_limit = available_memory * 0.8 / 1024  # 假设每个项目1KB
        time_based_limit = 300 / processing_time_per_item  # 5分钟限制
        
        return min(memory_based_limit, time_based_limit, 10000)  # 最大1万
    
    @staticmethod
    def should_parallelize(data_size, processing_complexity, available_cores):
        """判断是否应该并行化"""
        # 数据量足够大且处理复杂度高
        return data_size > 1000 and processing_complexity > 0.5 and available_cores > 2
```

#### 资源配置优化
```python
# 2. 资源配置计算器
class ResourceCalculator:
    """资源配置计算器"""
    
    @staticmethod
    def calculate_parallelism(total_cores, memory_gb, task_memory_mb):
        """计算并行度"""
        cpu_based = total_cores * 2  # CPU核心数的2倍
        memory_based = (memory_gb * 1024) / task_memory_mb  # 内存限制
        
        return min(cpu_based, memory_based, 32)  # 最大32
    
    @staticmethod
    def optimal_pool_size(task_type, resource_intensity, system_capacity):
        """计算资源池大小"""
        base_sizes = {
            'cpu_intensive': 2,
            'io_intensive': 4,
            'memory_intensive': 1,
            'network_intensive': 5
        }
        
        base_size = base_sizes.get(task_type, 2)
        intensity_factor = min(resource_intensity, 1.0)
        
        return int(base_size * intensity_factor * system_capacity)
```

#### 监控和告警配置
```python
# 3. 监控配置模板
class MonitoringConfig:
    """监控配置模板"""
    
    PERFORMANCE_THRESHOLDS = {
        'execution_time': {
            'warning': 300,    # 5分钟警告
            'critical': 600    # 10分钟严重
        },
        'memory_usage': {
            'warning': 80,     # 80%警告
            'critical': 95     # 95%严重
        },
        'cpu_usage': {
            'warning': 70,     # 70%警告
            'critical': 85     # 85%严重
        },
        'error_rate': {
            'warning': 5,      # 5%警告
            'critical': 10     # 10%严重
        }
    }
    
    ALERT_CHANNELS = {
        'email': {
            'enabled': True,
            'recipients': ['ops@company.com'],
            'severity_levels': ['warning', 'critical']
        },
        'slack': {
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/...',
            'severity_levels': ['critical']
        },
        'pagerduty': {
            'enabled': True,
            'service_key': 'your_service_key',
            'severity_levels': ['critical']
        }
    }
```

### 2. 常见陷阱和解决方案

#### 内存泄漏陷阱
```python
# 问题代码：内存泄漏
class MemoryLeakExample:
    def __init__(self):
        self.cache = []  # 持续增长，从不清理
    
    def process_data(self, data):
        self.cache.append(data)  # 内存持续增长
        return len(self.cache)

# 解决方案：使用弱引用和定期清理
import weakref
import gc

class MemorySafeProcessor:
    """内存安全的处理器"""
    
    def __init__(self, max_cache_size=1000):
        self._cache = weakref.WeakValueDictionary()
        self._strong_refs = []
        self.max_cache_size = max_cache_size
    
    def process_data(self, data):
        """处理数据"""
        # 生成缓存键
        cache_key = self._generate_key(data)
        
        # 检查缓存
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 处理数据
        result = self._expensive_operation(data)
        
        # 管理强引用
        self._strong_refs.append(result)
        if len(self._strong_refs) > self.max_cache_size:
            # 清理最旧的引用
            self._strong_refs = self._strong_refs[-self.max_cache_size//2:]
            gc.collect()  # 强制垃圾回收
        
        # 添加到弱引用缓存
        self._cache[cache_key] = result
        
        return result
```

#### 并发竞争条件
```python
# 问题代码：竞争条件
class RaceConditionExample:
    def __init__(self):
        self.counter = 0
    
    def increment(self):
        # 非线程安全操作
        current = self.counter
        time.sleep(0.001)  # 模拟处理时间
        self.counter = current + 1  # 竞争条件

# 解决方案：使用线程安全机制
import threading
from contextlib import contextmanager

class ThreadSafeCounter:
    """线程安全的计数器"""
    
    def __init__(self):
        self._counter = 0
        self._lock = threading.RLock()  # 可重入锁
    
    def increment(self):
        """线程安全的增量操作"""
        with self._lock:
            self._counter += 1
            return self._counter
    
    def get_value(self):
        """获取当前值"""
        with self._lock:
            return self._counter
    
    @contextmanager
    def batch_operation(self):
        """批量操作上下文管理器"""
        with self._lock:
            old_value = self._counter
            try:
                yield self
                # 批量操作完成
            finally:
                # 可以在这里添加验证逻辑
                pass

# 文件锁机制
import fcntl

class FileLock:
    """文件锁"""
    
    def __init__(self, lockfile):
        self.lockfile = lockfile
        self.fd = None
    
    def acquire(self, timeout=30):
        """获取锁"""
        start_time = time.time()
        self.fd = open(self.lockfile, 'w')
        
        while time.time() - start_time < timeout:
            try:
                fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except IOError:
                time.sleep(0.1)
        
        return False
    
    def release(self):
        """释放锁"""
        if self.fd:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
            self.fd.close()
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
```

#### 资源耗尽陷阱
```python
# 问题代码：资源耗尽
def resource_exhaustion_example():
    # 创建过多连接
    connections = []
    for i in range(1000):
        conn = create_database_connection()  # 可能耗尽连接池
        connections.append(conn)
    
    # 使用完不释放
    return len(connections)

# 解决方案：资源管理
from contextlib import ExitStack

class ResourceManager:
    """资源管理器"""
    
    def __init__(self, max_resources=10):
        self.max_resources = max_resources
        self.resources = []
        self.exit_stack = ExitStack()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def acquire_resource(self, resource_factory):
        """获取资源"""
        if len(self.resources) >= self.max_resources:
            raise ResourceExhaustedError("资源池已满")
        
        resource = self.exit_stack.enter_context(resource_factory())
        self.resources.append(resource)
        return resource
    
    def cleanup(self):
        """清理资源"""
        self.exit_stack.close()
        self.resources.clear()

# 连接池管理
class ConnectionPool:
    """数据库连接池"""
    
    def __init__(self, max_connections=10, connection_factory=None):
        self.max_connections = max_connections
        self.connection_factory = connection_factory
        self.pool = queue.Queue(maxsize=max_connections)
        self.semaphore = threading.Semaphore(max_connections)
    
    def get_connection(self, timeout=30):
        """获取连接"""
        if self.semaphore.acquire(timeout=timeout):
            try:
                return self.pool.get_nowait()
            except queue.Empty:
                return self.connection_factory()
        else:
            raise TimeoutError("获取连接超时")
    
    def return_connection(self, connection):
        """归还连接"""
        try:
            self.pool.put_nowait(connection)
        except queue.Full:
            connection.close()  # 池已满，关闭连接
        finally:
            self.semaphore.release()
    
    def __enter__(self):
        self.connection = self.get_connection()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.return_connection(self.connection)
```

## 性能测试和基准测试

### 1. 性能测试框架

```python
import time
import statistics
from typing import List, Dict, Any
import json

class PerformanceTestFramework:
    """性能测试框架"""
    
    def __init__(self, test_name: str, iterations: int = 10):
        self.test_name = test_name
        self.iterations = iterations
        self.results = []
    
    def run_performance_test(self, test_func, *args, **kwargs):
        """运行性能测试"""
        logging.info(f"开始性能测试: {self.test_name}")
        
        for i in range(self.iterations):
            # 清理内存
            gc.collect()
            
            # 记录开始状态
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                # 执行测试函数
                result = test_func(*args, **kwargs)
                
                # 记录结束状态
                end_time = time.time()
                end_memory = self._get_memory_usage()
                
                # 计算指标
                execution_time = end_time - start_time
                memory_usage = end_memory - start_memory
                
                test_result = {
                    'iteration': i + 1,
                    'execution_time': execution_time,
                    'memory_usage': memory_usage,
                    'status': 'success',
                    'result': result
                }
                
                self.results.append(test_result)
                
                logging.info(f"迭代 {i + 1}: 执行时间={execution_time:.3f}s, 内存使用={memory_usage:.2f}MB")
                
            except Exception as e:
                error_result = {
                    'iteration': i + 1,
                    'status': 'failed',
                    'error': str(e)
                }
                
                self.results.append(error_result)
                logging.error(f"迭代 {i + 1} 失败: {e}")
        
        # 生成测试报告
        return self.generate_test_report()
    
    def _get_memory_usage(self):
        """获取内存使用量"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def generate_test_report(self):
        """生成测试报告"""
        successful_results = [r for r in self.results if r['status'] == 'success']
        
        if not successful_results:
            return {
                'test_name': self.test_name,
                'status': 'all_failed',
                'total_iterations': len(self.results),
                'failed_iterations': len(self.results)
            }
        
        # 计算统计信息
        execution_times = [r['execution_time'] for r in successful_results]
        memory_usages = [r['memory_usage'] for r in successful_results]
        
        report = {
            'test_name': self.test_name,
            'status': 'completed',
            'total_iterations': self.iterations,
            'successful_iterations': len(successful_results),
            'failed_iterations': len(self.results) - len(successful_results),
            'execution_time_stats': {
                'mean': statistics.mean(execution_times),
                'median': statistics.median(execution_times),
                'min': min(execution_times),
                'max': max(execution_times),
                'stdev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            },
            'memory_usage_stats': {
                'mean': statistics.mean(memory_usages),
                'median': statistics.median(memory_usages),
                'min': min(memory_usages),
                'max': max(memory_usages),
                'stdev': statistics.stdev(memory_usages) if len(memory_usages) > 1 else 0
            },
            'raw_results': self.results
        }
        
        # 添加性能评级
        report['performance_grade'] = self._evaluate_performance_grade(report)
        
        return report
    
    def _evaluate_performance_grade(self, report):
        """评估性能等级"""
        execution_time_mean = report['execution_time_stats']['mean']
        memory_usage_mean = report['memory_usage_stats']['mean']
        
        # 基于执行时间和内存使用的简单评级
        if execution_time_mean < 1 and memory_usage_mean < 100:
            return 'A'
        elif execution_time_mean < 5 and memory_usage_mean < 500:
            return 'B'
        elif execution_time_mean < 10 and memory_usage_mean < 1000:
            return 'C'
        else:
            return 'D'
    
    def save_report(self, filepath):
        """保存测试报告"""
        report = self.generate_test_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logging.info(f"测试报告已保存: {filepath}")
        return report

# 性能测试示例
class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self):
        self.tests = []
    
    def add_test(self, name, test_func, iterations=10):
        """添加测试"""
        self.tests.append({
            'name': name,
            'test_func': test_func,
            'iterations': iterations
        })
    
    def run_all_tests(self):
        """运行所有测试"""
        all_results = []
        
        for test_config in self.tests:
            framework = PerformanceTestFramework(
                test_config['name'],
                test_config['iterations']
            )
            
            result = framework.run_performance_test(test_config['test_func'])
            all_results.append(result)
            
            logging.info(f"测试 {test_config['name']} 完成，等级: {result.get('performance_grade', 'N/A')}")
        
        return self.generate_comparative_report(all_results)
    
    def generate_comparative_report(self, results):
        """生成比较报告"""
        comparative_report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(results),
            'test_summary': []
        }
        
        for result in results:
            summary = {
                'test_name': result['test_name'],
                'performance_grade': result.get('performance_grade', 'N/A'),
                'mean_execution_time': result['execution_time_stats']['mean'],
                'mean_memory_usage': result['memory_usage_stats']['mean'],
                'success_rate': result['successful_iterations'] / result['total_iterations'] * 100
            }
            comparative_report['test_summary'].append(summary)
        
        return comparative_report

# 使用示例
def test_batch_processing():
    """测试批处理性能"""
    # 模拟批处理
    batch_size = 1000
    data = list(range(batch_size))
    
    # 处理数据
    results = []
    for item in data:
        result = item * 2 + random.randint(1, 10)
        results.append(result)
    
    return len(results)

def test_concurrent_processing():
    """测试并发处理性能"""
    def process_item(item):
        time.sleep(0.001)  # 模拟处理时间
        return item * 2
    
    data = list(range(100))
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_item, data))
    
    return len(results)

# 创建测试套件
performance_suite = PerformanceTestSuite()
performance_suite.add_test('batch_processing', test_batch_processing, iterations=5)
performance_suite.add_test('concurrent_processing', test_concurrent_processing, iterations=5)

# 运行测试
if __name__ == "__main__":
    results = performance_suite.run_all_tests()
    print(json.dumps(results, indent=2))
```

## 总结

任务流优化是Airflow生产部署的核心技能，涉及性能调优、资源管理、监控告警、错误处理等多个方面。通过系统性地应用这些优化技术，可以显著提升数据处理效率、系统稳定性和资源利用率。

### 关键要点：

1. **系统性优化**: 从应用层、框架层、系统层到基础设施层的全面优化
2. **监控驱动**: 基于监控数据指导优化决策，避免盲目优化
3. **渐进式改进**: 小步快跑，持续优化，避免一次性大幅改动
4. **平衡考虑**: 在性能、成本、复杂度之间找到平衡点
5. **文档记录**: 记录优化过程和结果，为后续优化提供参考

通过掌握这些优化技术，你将能够构建高性能、高可用、可扩展的企业级数据处理平台。