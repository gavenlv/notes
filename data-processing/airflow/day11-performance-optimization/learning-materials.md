# Day 11: Airflow性能优化学习材料

## 核心概念解析

### 1. 性能优化基础

#### 性能优化原则
性能优化应遵循以下原则：
1. **测量先行**: 优化前先测量基线性能，优化后验证效果
2. **瓶颈优先**: 优先解决最影响性能的瓶颈问题
3. **渐进优化**: 小步快跑，持续优化，避免一次性大幅改动
4. **权衡考虑**: 在性能、成本、复杂度之间找到平衡点
5. **监控驱动**: 基于监控数据指导优化决策

#### 关键性能指标(KPI)
衡量Airflow性能的关键指标包括：
- **任务执行时间**: 单个任务从开始到完成的时间
- **DAG执行时间**: 整个工作流从开始到完成的时间
- **任务成功率**: 成功执行的任务占总任务的比例
- **资源使用率**: CPU、内存、磁盘、网络等资源的使用情况
- **队列长度**: 等待执行的任务数量
- **调度延迟**: 任务实际执行时间与计划执行时间的差值

#### 性能瓶颈类型
常见的Airflow性能瓶颈包括：
1. **CPU瓶颈**: 计算密集型任务导致CPU使用率过高
2. **内存瓶颈**: 内存泄漏或大数据集处理导致内存不足
3. **I/O瓶颈**: 磁盘读写或网络传输速度限制
4. **数据库瓶颈**: 元数据库查询慢或连接数不足
5. **调度瓶颈**: 调度器处理能力不足导致任务调度延迟
6. **网络瓶颈**: 分布式环境中网络延迟或带宽限制

### 2. 配置参数调优

#### 核心并发参数
```ini
[core]
# 整个Airflow实例的最大并发任务数
parallelism = 32

# 每个DAG的最大并发运行数
max_active_runs_per_dag = 16

# 向后兼容参数，功能同max_active_tasks
dag_concurrency = 16

[scheduler]
# 调度器检查DAG间隔时间(秒)
processor_poll_interval = 1

# 调度器心跳间隔(秒)
scheduler_heartbeat_sec = 5

# 调度器进程数
max_threads = 2

[celery]
# Celery worker并发数
worker_concurrency = 16
```

#### 数据库连接参数
```ini
[core]
# 数据库连接池大小
sql_alchemy_pool_size = 10

# 连接池溢出大小
sql_alchemy_max_overflow = 10

# 连接超时时间(秒)
sql_alchemy_connect_timeout = 30

# 回收连接时间(秒)
sql_alchemy_pool_recycle = 3600
```

#### Web Server参数
```ini
[webserver]
# Web Server工作进程数
workers = 4

# 工作进程类
worker_class = sync

# 每个工作进程的连接数
worker_connections = 1000

# 请求超时时间(秒)
web_server_worker_timeout = 120
```

### 3. 执行器优化策略

#### SequentialExecutor
适用于：
- 开发测试环境
- 简单的DAG执行
- 资源受限的环境

优化要点：
- 仅用于开发测试，不适用于生产环境
- 任务串行执行，无并发能力

#### LocalExecutor
适用于：
- 单机部署环境
- 中小型工作负载
- 对分布式部署无特殊要求的场景

优化要点：
- 合理设置`parallelism`参数
- 监控系统资源使用情况
- 避免内存密集型任务导致OOM

#### CeleryExecutor
适用于：
- 分布式部署环境
- 大规模任务并发执行
- 需要弹性伸缩的场景

优化要点：
- 合理配置Celery Broker(Redis/RabbitMQ)
- 设置合适的worker数量和并发数
- 监控任务队列长度和处理延迟

#### KubernetesExecutor
适用于：
- 容器化部署环境
- 需要任务隔离的场景
- 云原生架构

优化要点：
- 合理配置Pod资源请求和限制
- 优化镜像大小和拉取策略
- 设置合适的worker资源配额

### 4. 数据库性能优化

#### 索引优化
关键表的推荐索引：
```sql
-- dag_run表索引
CREATE INDEX idx_dag_run_dag_id_state ON dag_run (dag_id, state);
CREATE INDEX idx_dag_run_state ON dag_run (state);

-- task_instance表索引
CREATE INDEX idx_task_instance_dag_id_task_id ON task_instance (dag_id, task_id);
CREATE INDEX idx_task_instance_state ON task_instance (state);
CREATE INDEX idx_task_instance_dag_id_state ON task_instance (dag_id, state);

-- job表索引
CREATE INDEX idx_job_job_type ON job (job_type);
CREATE INDEX idx_job_state ON job (state);
```

#### 查询优化
常见的慢查询优化：
1. **避免全表扫描**: 为WHERE条件字段添加索引
2. **减少JOIN操作**: 适当的数据冗余减少表关联
3. **分页查询优化**: 使用游标而非OFFSET进行分页
4. **统计查询优化**: 预计算统计信息减少实时计算

#### 连接池配置
合理的连接池配置：
```python
# SQLAlchemy连接池配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 30,
}
```

### 5. 资源管理优化

#### 内存优化策略
1. **监控内存使用**:
```python
import psutil
import gc

def monitor_memory():
    """监控内存使用情况"""
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # 显示垃圾回收统计
    gc_stats = gc.get_stats()
    print(f"GC stats: {gc_stats}")
```

2. **内存泄漏预防**:
```python
from contextlib import contextmanager

@contextmanager
def managed_resource(resource):
    """资源管理上下文"""
    try:
        yield resource
    finally:
        # 确保资源正确释放
        if hasattr(resource, 'close'):
            resource.close()
```

3. **大数据处理优化**:
```python
import pandas as pd

def process_large_dataset(file_path, chunk_size=10000):
    """分块处理大文件"""
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # 处理每个数据块
        processed_chunk = process_chunk(chunk)
        yield processed_chunk
```

#### CPU优化策略
1. **多进程并行处理**:
```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

def parallel_process(data_list, process_func, max_workers=None):
    """并行处理数据"""
    if max_workers is None:
        max_workers = mp.cpu_count()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_func, data_list))
    return results
```

2. **任务调度优化**:
```python
from airflow.decorators import task

@task(max_active_tis_per_dag=10)
def cpu_intensive_task(data):
    """CPU密集型任务"""
    # 执行计算密集型操作
    result = complex_calculation(data)
    return result
```

#### 磁盘I/O优化
1. **日志轮转配置**:
```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'airflow': {'format': '%(asctime)s %(levelname)s - %(message)s'},
    },
    'handlers': {
        'rotating_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'airflow',
            'filename': '/var/log/airflow/airflow.log',
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'airflow': {
            'handlers': ['rotating_file'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}
```

2. **临时文件管理**:
```python
import tempfile
import os

def process_with_temp_file(data):
    """使用临时文件处理数据"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        # 写入数据到临时文件
        temp_file.write(data)
        temp_file_path = temp_file.name
    
    try:
        # 处理临时文件
        result = process_file(temp_file_path)
        return result
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
```

### 6. 监控和分析工具

#### Prometheus指标收集
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
TASK_EXECUTION_TIME = Histogram('airflow_task_execution_time_seconds', 
                               'Task execution time in seconds',
                               ['dag_id', 'task_id'])
TASK_FAILURE_COUNT = Counter('airflow_task_failures_total',
                            'Total number of task failures',
                            ['dag_id', 'task_id'])
ACTIVE_TASKS = Gauge('airflow_active_tasks',
                     'Number of currently active tasks')

def monitor_task_execution(dag_id, task_id, func):
    """监控任务执行"""
    ACTIVE_TASKS.inc()
    
    start_time = time.time()
    try:
        result = func()
        TASK_EXECUTION_TIME.labels(dag_id=dag_id, task_id=task_id).observe(
            time.time() - start_time)
        return result
    except Exception as e:
        TASK_FAILURE_COUNT.labels(dag_id=dag_id, task_id=task_id).inc()
        raise
    finally:
        ACTIVE_TASKS.dec()
```

#### 性能分析工具
1. **py-spy采样分析**:
```bash
# 安装py-spy
pip install py-spy

# 分析Airflow进程
py-spy top --pid <airflow_scheduler_pid>
py-spy record -o profile.svg --duration 60 --pid <airflow_scheduler_pid>
```

2. **memory_profiler内存分析**:
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """内存密集型函数"""
    data = [i for i in range(1000000)]
    processed_data = [x * 2 for x in data]
    return processed_data
```

3. **line_profiler行级分析**:
```python
# 安装line_profiler
pip install line_profiler

# 在函数前添加@profile装饰器
@profile
def slow_function():
    # 一些慢操作
    result = sum(range(1000000))
    return result

# 运行分析
kernprof -l -v script.py
```

## 实践指南

### 性能测试方法
1. **基准测试**:
```python
import time
from datetime import datetime, timedelta

def benchmark_dag_execution(dag_id, num_runs=10):
    """基准测试DAG执行性能"""
    execution_times = []
    
    for i in range(num_runs):
        start_time = time.time()
        
        # 触发DAG执行
        # 这里应该是实际的DAG触发代码
        
        end_time = time.time()
        execution_times.append(end_time - start_time)
    
    # 计算统计信息
    avg_time = sum(execution_times) / len(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)
    
    print(f"Average execution time: {avg_time:.2f}s")
    print(f"Min execution time: {min_time:.2f}s")
    print(f"Max execution time: {max_time:.2f}s")
```

2. **压力测试**:
```python
import threading
import time

def stress_test_dag_trigger(dag_id, concurrent_runs=10):
    """并发触发DAG进行压力测试"""
    def trigger_dag():
        # DAG触发逻辑
        pass
    
    threads = []
    start_time = time.time()
    
    # 创建并发线程
    for i in range(concurrent_runs):
        thread = threading.Thread(target=trigger_dag)
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print(f"Stress test completed in {end_time - start_time:.2f}s")
```

### 优化案例分析

#### 案例1: 大规模DAG调度优化
问题描述：当系统中有数千个DAG时，调度器性能下降明显。

优化方案：
1. 调整调度器参数：
```ini
[scheduler]
# 增加调度器进程数
max_threads = 4
# 减少DAG文件处理间隔
processor_poll_interval = 5
# 增加心跳间隔减少数据库写入
scheduler_heartbeat_sec = 10
```

2. DAG文件优化：
```python
# 使用DAG工厂模式减少重复代码
from airflow.decorators import dag

@dag(
    schedule_interval="@daily",
    max_active_runs=1,
    catchup=False
)
def optimized_dag():
    # DAG任务定义
    pass

# 实例化DAG
optimized_dag()
```

#### 案例2: 内存泄漏问题解决
问题描述：长时间运行的任务出现内存持续增长。

优化方案：
1. 添加内存监控：
```python
import psutil
from airflow.models import Variable

def check_memory_usage(task_instance):
    """检查任务内存使用情况"""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    # 获取内存阈值
    memory_threshold = int(Variable.get("memory_threshold_mb", default_var=1024))
    
    if memory_mb > memory_threshold:
        task_instance.log.warning(f"Memory usage high: {memory_mb:.2f}MB")
        # 可以选择重启任务或发送告警
```

2. 优化数据处理：
```python
# 使用生成器而非列表存储大量数据
def process_data_generator(data_source):
    """使用生成器处理数据"""
    for item in data_source:
        processed_item = process_item(item)
        yield processed_item

# 分批处理而非一次性加载所有数据
def batch_process(data, batch_size=1000):
    """分批处理数据"""
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        process_batch(batch)
```

## 总结

Airflow性能优化是一个综合性的工作，需要从配置、架构、代码、监控等多个维度进行考虑。通过系统性地应用这些优化技术和最佳实践，可以显著提升Airflow系统的性能和稳定性。

关键要点：
1. **系统性优化**: 从应用层到基础设施层的全面优化
2. **监控驱动**: 基于监控数据指导优化决策
3. **渐进式改进**: 小步快跑，持续优化
4. **平衡考虑**: 在性能、成本、复杂度之间找到平衡点
5. **文档记录**: 记录优化过程和结果，为后续优化提供参考

通过掌握这些优化技术，你将能够构建高性能、高可用、可扩展的企业级数据处理平台。