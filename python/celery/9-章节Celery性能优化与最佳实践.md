# 第9章 Celery性能优化与最佳实践

## 9.1 性能优化概述

在生产环境中使用Celery时，性能优化至关重要。良好的性能不仅可以提高任务处理效率，还能降低资源消耗，确保系统的稳定性和可扩展性。本章将介绍Celery各个组件的性能优化策略和最佳实践。

### 9.1.1 性能优化的维度

Celery性能优化可以从以下几个维度考虑：

1. **工作进程优化**：调整工作进程的数量、并发度和资源分配
2. **任务设计优化**：改进任务结构、粒度和执行逻辑
3. **消息队列优化**：选择合适的消息代理并进行优化配置
4. **结果后端优化**：高效管理任务结果和元数据
5. **资源管理优化**：内存使用、CPU利用率和I/O操作优化
6. **架构优化**：扩展策略、负载均衡和故障转移机制

### 9.1.2 性能基准测试

在进行任何优化之前，建立性能基准测试是很重要的。这可以帮助我们：

- 识别当前系统的瓶颈
- 量化优化措施的效果
- 为后续优化提供参考

```python
# 简单的性能基准测试示例
import time
from celery import Celery

app = Celery('benchmark')
app.config_from_object('celeryconfig')

@app.task
def benchmark_task(n):
    """基准测试任务"""
    result = 0
    for i in range(n):
        result += i
    return result

def run_benchmark():
    """运行基准测试"""
    iterations = 1000000
    
    # 同步执行时间
    start_time = time.time()
    benchmark_task(iterations)
    sync_time = time.time() - start_time
    
    # 异步执行时间
    start_time = time.time()
    result = benchmark_task.delay(iterations)
    result.wait()  # 等待任务完成
    async_time = time.time() - start_time
    
    print(f"同步执行时间: {sync_time:.4f}秒")
    print(f"异步执行时间: {async_time:.4f}秒")
    print(f"额外开销: {(async_time - sync_time):.4f}秒")
```

## 9.2 工作进程优化

工作进程是执行任务的组件，其配置和行为对整体性能有重要影响。

### 9.2.1 工作进程数量调整

工作进程的数量应根据服务器的CPU核心数和任务类型进行调整：

```bash
# 根据CPU核心数启动工作进程
celery -A proj worker --loglevel=info --autoscale=10,3
```

这里的`--autoscale=10,3`表示最多10个进程，最少3个进程，系统会根据负载自动调整。

**最佳实践**：
- CPU密集型任务：工作进程数通常不超过CPU核心数
- I/O密集型任务：工作进程数可以设置为CPU核心数的2-4倍
- 混合任务类型：根据实际负载测试来确定最佳值

### 9.2.2 并发模式选择

Celery支持多种并发模式，可以根据任务特性选择：

1. **prefork**：默认模式，使用多进程
2. **eventlet**：基于协程的并发模式
3. **gevent**：基于协程的并发模式，性能较好
4. **solo**：单线程模式，仅用于调试

```bash
# 使用gevent并发模式，1000个绿色线程
celery -A proj worker --loglevel=info -P gevent -c 1000
```

**选择建议**：
- CPU密集型任务：使用prefork
- 大量I/O操作任务：使用gevent或eventlet
- 网络请求密集型任务：使用gevent或eventlet

### 9.2.3 工作进程资源限制

限制工作进程的资源使用可以防止单个任务消耗过多资源：

```python
# 在celeryconfig.py中设置
worker_prefetch_multiplier = 1  # 预取任务数
worker_max_tasks_per_child = 1000  # 每个子进程最多执行的任务数
worker_disable_rate_limits = False  # 启用速率限制
```

**优化参数**：
- `worker_prefetch_multiplier`：控制每个工作进程预取的任务数，I/O密集型任务可以设为更高值
- `worker_max_tasks_per_child`：防止内存泄漏，定期重启工作进程
- `worker_max_memory_per_child`：限制每个子进程的内存使用

### 9.2.4 工作进程监控与自动恢复

监控工作进程状态并设置自动恢复机制：

```bash
# 启动时自动恢复未完成的任务
celery -A proj worker --loglevel=info --task-events --autoreload
```

```python
# 使用supervisor管理Celery进程的配置示例
# supervisor.conf
[program:celery_worker]
command=celery -A proj worker --loglevel=info
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
user=celery
```

## 9.3 任务设计优化

合理的任务设计可以显著提高系统性能和可靠性。

### 9.3.1 任务粒度设计

任务粒度指任务的大小和复杂度，合理的粒度设计可以提高并行处理效率：

**最佳实践**：
- **避免巨型任务**：将大型任务拆分为多个小任务
- **避免微型任务**：过于微小的任务会增加消息传递开销
- **任务分组**：相关任务可以分组执行，减少通信开销

```python
# 反例：单个大型任务
@app.task
def process_large_dataset(dataset_id):
    # 下载数据
    # 处理数据（多步骤）
    # 保存结果
    # 发送通知
    pass

# 正例：拆分为多个小任务
@app.task
def download_data(dataset_id):
    # 下载数据
    return data_path

@app.task
def process_data(data_path):
    # 处理数据
    return result_path

@app.task
def save_results(result_path):
    # 保存结果
    return save_status

@app.task
def send_notification(save_status):
    # 发送通知
    pass

# 任务链
chain = download_data.s(dataset_id) | process_data.s() | save_results.s() | send_notification.s()
chain.apply_async()
```

### 9.3.2 任务优先级策略

使用任务优先级可以确保重要任务优先执行：

```python
# 设置任务优先级
@app.task(priority=10)  # 较高优先级
def critical_task():
    pass

@app.task(priority=1)  # 较低优先级
def non_critical_task():
    pass

# 提交任务时设置优先级
app.send_task('tasks.long_running', priority=5)
```

**优先级最佳实践**：
- 关键业务任务：高优先级
- 批量处理任务：中低优先级
- 后台维护任务：最低优先级
- 避免过多优先级级别，建议不超过5-7个级别

### 9.3.3 任务路由优化

合理的任务路由可以将不同类型的任务分配给专门的工作进程：

```python
# celeryconfig.py
task_queues = {
    'default': {
        'exchange': 'default',
        'exchange_type': 'direct',
        'routing_key': 'default',
    },
    'cpu_intensive': {
        'exchange': 'cpu_tasks',
        'exchange_type': 'direct',
        'routing_key': 'cpu.intensive',
    },
    'io_intensive': {
        'exchange': 'io_tasks',
        'exchange_type': 'direct',
        'routing_key': 'io.intensive',
    }
}

task_routes = {
    'tasks.cpu_task': {'queue': 'cpu_intensive'},
    'tasks.io_task': {'queue': 'io_intensive'},
}
```

启动专用工作进程：

```bash
# 启动CPU密集型任务的工作进程
celery -A proj worker --loglevel=info -Q cpu_intensive -P prefork -c 4

# 启动I/O密集型任务的工作进程
celery -A proj worker --loglevel=info -Q io_intensive -P gevent -c 100
```

### 9.3.4 任务去重与幂等性

实现任务去重和确保任务幂等性可以避免重复执行相同任务：

```python
# 使用任务ID实现去重
from celery import Task

class DedupTask(Task):
    def apply_async(self, *args, **kwargs):
        # 检查任务是否已经在执行
        if self.backend.get_task_meta(self.request.id):
            # 任务已存在，不重复提交
            return None
        return super(DedupTask, self).apply_async(*args, **kwargs)

@app.task(base=DedupTask)
def idempotent_task(data_id):
    # 使用数据ID作为唯一标识，确保幂等性
    # 1. 检查结果是否已存在
    # 2. 如果存在，直接返回结果
    # 3. 如果不存在，执行任务
    pass
```

**幂等性设计要点**：
- 使用唯一标识符
- 先检查后执行
- 操作可重复执行且结果一致
- 避免副作用或限制副作用范围

## 9.4 消息代理优化

消息代理是Celery的核心组件之一，其性能直接影响整个系统的吞吐量。

### 9.4.1 消息代理选择

选择适合业务场景的消息代理：

| 消息代理 | 优点 | 缺点 | 适用场景 |
|---------|------|------|----------|
| Redis | 高性能、配置简单、支持优先级、持久化 | 大规模集群配置复杂 | 大多数中小型应用 |
| RabbitMQ | 可靠性高、支持复杂路由、适合高并发 | 配置相对复杂 | 企业级应用、对可靠性要求高的系统 |
| SQS | 托管服务、无需维护、弹性扩展 | 功能有限、成本较高 | AWS环境下的应用 |
| Azure Queue | 托管服务、与Azure集成 | 功能有限、成本较高 | Azure环境下的应用 |

### 9.4.2 Redis优化配置

Redis作为消息代理时的优化配置：

```python
# celeryconfig.py
# 连接池配置
broker_pool_limit = 10  # 连接池大小

# 传输选项
broker_transport_options = {
    'visibility_timeout': 3600,  # 任务可见性超时时间
    'max_retries': 3,  # 连接重试次数
    'socket_connect_timeout': 5,  # 连接超时时间
    'socket_timeout': 30,  # 套接字超时时间
}

# 结果后端配置
result_backend_transport_options = {
    'visibility_timeout': 86400,  # 结果可见性超时时间
    'socket_connect_timeout': 5,
    'socket_timeout': 30,
}
```

Redis服务器优化：

```conf
# redis.conf 优化配置
# 内存管理
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化配置
appendonly yes
appendfsync everysec

# 网络优化
tcp-keepalive 300
```

### 9.4.3 RabbitMQ优化配置

RabbitMQ作为消息代理时的优化配置：

```python
# celeryconfig.py
# 连接池配置
broker_pool_limit = 10

# 传输选项
broker_transport_options = {
    'confirm_publish': True,  # 启用发布确认
    'max_retries': 3,
    'interval_start': 0.1,
    'interval_step': 0.2,
    'interval_max': 1.0,
}

# 消息压缩（对于大型消息）
task_compression = 'gzip'
```

RabbitMQ服务器优化：

```conf
# rabbitmq.conf 优化配置
# 内存管理
vm_memory_high_watermark.absolute = 2GB
vm_memory_high_watermark_paging_ratio = 0.5

# 并行处理
channel_max = 1000

# 网络优化
tcp_listen_options.backlog = 128
tcp_listen_options.nodelay = true
```

### 9.4.4 消息序列化与压缩

优化消息序列化和压缩可以减少网络传输开销：

```python
# celeryconfig.py
# 序列化器选择
task_serializer = 'json'  # 或使用 msgpack 获得更好性能
result_serializer = 'json'
accept_content = ['json', 'msgpack']

# 消息压缩配置
task_compression = 'gzip'  # 对大型消息启用压缩
```

**序列化器性能对比**：
- `pickle`：Python原生，序列化速度快，但安全性较低
- `json`：通用格式，安全性好，速度适中
- `msgpack`：二进制格式，序列化速度快，体积小
- `yaml`：可读性好，但序列化速度慢

## 9.5 结果后端优化

结果后端存储任务执行结果和状态，合理的配置可以提高性能并减少资源消耗。

### 9.5.1 结果后端选择

根据业务需求选择合适的结果后端：

| 结果后端 | 优点 | 缺点 | 适用场景 |
|---------|------|------|----------|
| Redis | 高性能、配置简单、支持TTL | 内存有限、大规模数据可能有压力 | 大多数应用场景 |
| Database | 持久化存储、查询灵活 | 性能相对较低 | 需要长期存储结果的应用 |
| Memcached | 高性能、分布式 | 不支持持久化、功能简单 | 临时性结果缓存 |
| RPC | 轻量级、无额外依赖 | 不适合长时间运行的任务 | 简单任务、短期结果 |

### 9.5.2 结果过期策略

设置合理的结果过期时间可以自动清理不再需要的结果数据：

```python
# celeryconfig.py
# 结果过期时间（秒）
result_expires = 3600  # 1小时

# 每个任务可以单独设置过期时间
@app.task(result_expires=7200)  # 2小时
def long_running_task():
    pass
```

**过期时间建议**：
- 实时性任务：几分钟到几小时
- 批处理任务：几小时到几天
- 报表任务：几天到几周
- 重要业务任务：可设置较长过期时间或手动清理

### 9.5.3 结果存储优化

优化结果存储可以减少存储空间和提高查询性能：

```python
# celeryconfig.py
# 禁用某些任务的结果存储
app.conf.task_ignore_result = True

# 选择性启用结果存储
@app.task(ignore_result=False)  # 需要结果的任务
def important_task():
    return "需要跟踪的结果"

@app.task(ignore_result=True)  # 不需要结果的任务
def background_task():
    # 执行后台操作，不需要返回结果
    pass
```

**存储优化技巧**：
- 只存储必要的结果数据
- 使用结果引用而非完整数据
- 对大型结果进行压缩
- 考虑异步保存大型结果到文件系统或对象存储

## 9.6 资源管理与优化

合理管理系统资源可以提高Celery的性能和稳定性。

### 9.6.1 内存使用优化

内存泄漏是Celery应用中常见的问题，以下是一些优化策略：

```python
# celeryconfig.py
# 定期重启工作进程，防止内存泄漏
worker_max_tasks_per_child = 1000  # 每个子进程处理的最大任务数
worker_max_memory_per_child = 50000  # 每个子进程的最大内存使用量（KB）
```

**内存优化最佳实践**：
- 避免在任务中创建过大的临时对象
- 及时释放不再需要的大型对象引用
- 使用迭代器处理大型数据集
- 监控内存使用情况，及时发现泄漏

### 9.6.2 数据库连接池管理

优化数据库连接可以减少连接建立和销毁的开销：

```python
# 使用连接池优化数据库操作
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 创建带连接池的引擎
engine = create_engine(
    'postgresql://user:password@localhost/dbname',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

@app.task
def db_task():
    # 从连接池获取连接
    with engine.connect() as conn:
        # 执行数据库操作
        result = conn.execute("SELECT * FROM users")
        # 处理结果
```

**连接池优化参数**：
- `pool_size`：连接池中的连接数
- `max_overflow`：允许的最大额外连接数
- `pool_timeout`：获取连接的超时时间
- `pool_recycle`：连接回收时间，防止连接过期

### 9.6.3 网络请求优化

任务中涉及的网络请求需要进行优化：

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 创建会话和连接池
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.1)
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

@app.task
def api_task(url):
    # 使用连接池发送请求
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

**网络请求优化技巧**：
- 使用连接池减少连接建立开销
- 设置合理的超时时间
- 实现重试机制处理临时网络故障
- 考虑使用异步HTTP客户端（如aiohttp）处理大量请求

## 9.7 扩展性优化

随着业务增长，Celery系统需要能够水平扩展以处理更多任务。

### 9.7.1 水平扩展策略

水平扩展是通过增加更多工作节点来提高系统处理能力：

```bash
# 在多个服务器上启动工作进程
# 服务器1
celery -A proj worker --loglevel=info -Q default

# 服务器2
celery -A proj worker --loglevel=info -Q cpu_intensive

# 服务器3
celery -A proj worker --loglevel=info -Q io_intensive
```

**水平扩展最佳实践**：
- 使用容器化技术（Docker）简化部署
- 使用编排工具（Kubernetes）管理工作节点
- 实现自动扩缩容，根据负载动态调整工作节点数量
- 确保消息代理和结果后端能够处理增加的负载

### 9.7.2 集群配置与负载均衡

合理配置集群和实现负载均衡可以优化资源利用率：

```python
# celeryconfig.py
# 启用任务事件，便于监控和负载均衡
task_send_sent_event = True

# 配置任务路由，实现负载分散
task_routes = {
    'tasks.cpu_task': {'queue': 'cpu_intensive'},
    'tasks.io_task': {'queue': 'io_intensive'},
    'tasks.default_task': {'queue': 'default'},
}

# 使用优先级队列实现更精细的负载控制
task_queue_max_priority = 10
```

**集群配置要点**：
- 根据任务类型分组工作节点
- 为不同类型的任务设置专用队列
- 使用负载均衡器分发任务
- 监控每个工作节点的性能指标

### 9.7.3 分布式锁与协调

在分布式环境中，需要使用分布式锁来协调任务执行：

```python
import redis
from redis.lock import Lock

# Redis客户端
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.task
def critical_task(resource_id):
    # 获取分布式锁
    lock_name = f"lock:resource:{resource_id}"
    
    with Lock(redis_client, lock_name, timeout=60):  # 60秒超时
        # 执行需要互斥的操作
        # ...
        return "操作完成"
```

**分布式协调策略**：
- 使用Redis或ZooKeeper实现分布式锁
- 设置合理的锁超时时间
- 考虑使用分布式事务处理复杂业务场景
- 实现死锁检测和预防机制

## 9.8 部署架构优化

优化部署架构可以提高系统的可用性和可靠性。

### 9.8.1 多环境部署

建立开发、测试和生产多环境部署架构：

```python
# 根据环境加载不同配置
import os

app = Celery('proj')

# 从环境变量获取配置
env = os.environ.get('CELERY_ENV', 'development')

if env == 'development':
    app.config_from_object('proj.config.DevelopmentConfig')
elif env == 'testing':
    app.config_from_object('proj.config.TestingConfig')
elif env == 'production':
    app.config_from_object('proj.config.ProductionConfig')
```

**环境隔离最佳实践**：
- 使用环境变量区分不同环境
- 为每个环境维护独立的配置文件
- 确保开发和生产环境配置相似但不完全相同
- 使用配置管理工具（如Ansible、Chef）自动化部署

### 9.8.2 高可用部署

实现高可用部署确保系统在单点故障时仍能正常运行：

```bash
# 部署多个消息代理节点
# RabbitMQ集群
rabbitmq-server -detached

# Redis Sentinel配置
redis-sentinel /path/to/sentinel.conf
```

```python
# 配置多个消息代理节点
broker_url = 'pyamqp://user:password@rabbit1,rabbit2,rabbit3//'

# Redis Sentinel配置
result_backend = 'redis+sentinel://master/0'
broker_transport_options = {
    'master_name': 'mymaster',
    'sentinels': [
        ('sentinel1', 26379),
        ('sentinel2', 26379),
        ('sentinel3', 26379),
    ]
}
```

**高可用部署要点**：
- 消息代理集群化部署
- 结果后端高可用配置
- 工作节点多服务器部署
- 实现自动故障检测和恢复

### 9.8.3 容器化部署

使用容器化技术简化部署和扩展：

```dockerfile
# Dockerfile for Celery worker
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 启动Celery工作进程
CMD celery -A proj worker --loglevel=info -Q default
```

```yaml
# docker-compose.yml
version: '3'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker_cpu:
    build: .
    command: celery -A proj worker --loglevel=info -Q cpu_intensive -P prefork -c 4
    depends_on:
      - redis

  celery_worker_io:
    build: .
    command: celery -A proj worker --loglevel=info -Q io_intensive -P gevent -c 100
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A proj flower
    ports:
      - "5555:5555"
    depends_on:
      - redis

volumes:
  redis_data:
```

**容器化优势**：
- 环境一致性
- 部署简化
- 扩展灵活
- 资源隔离

## 9.9 最佳实践总结

综合以上各节内容，以下是Celery性能优化与最佳实践的总结。

### 9.9.1 任务设计最佳实践

1. **任务粒度**：将大型任务拆分为多个小任务，但避免过于微小的任务
2. **任务命名**：使用清晰、描述性的任务名称
3. **参数传递**：避免传递大型对象，使用引用或ID
4. **幂等设计**：确保任务可以安全地重复执行
5. **错误处理**：实现适当的错误处理和重试机制

### 9.9.2 配置优化最佳实践

1. **工作进程配置**：根据任务类型和服务器资源调整工作进程数量和并发模式
2. **消息代理**：选择合适的消息代理并进行优化配置
3. **结果管理**：设置合理的结果过期时间，只存储必要的结果
4. **资源限制**：设置工作进程的内存和任务数限制，防止资源泄漏
5. **监控配置**：启用任务事件和日志，便于监控和调试

### 9.9.3 生产环境部署最佳实践

1. **环境隔离**：建立开发、测试和生产多环境
2. **高可用设计**：实现消息代理和结果后端的高可用配置
3. **自动化部署**：使用容器化和编排工具简化部署和扩展
4. **监控告警**：部署全面的监控和告警系统
5. **定期维护**：定期更新依赖、清理结果和优化配置

### 9.9.4 常见问题排查

1. **任务队列积压**：增加工作进程数、优化任务执行时间、检查工作进程是否正常运行
2. **内存泄漏**：设置`worker_max_tasks_per_child`和`worker_max_memory_per_child`，定期重启工作进程
3. **连接超时**：检查网络连接，优化连接池配置，增加超时时间
4. **任务失败**：检查任务日志，实现适当的重试机制，考虑死信队列
5. **性能下降**：监控系统指标，查找瓶颈，优化任务设计和配置

通过遵循这些最佳实践，您可以构建一个高性能、可靠的Celery分布式任务队列系统，满足各种业务场景的需求。记住，性能优化是一个持续的过程，需要根据实际负载和业务需求不断调整和改进。

## 9.10 实践示例

下面提供一个综合优化的Celery应用示例，演示如何实现上述最佳实践。

```python
"""
高性能Celery应用示例

本示例演示了如何构建一个高性能、可扩展的Celery应用，包括：
1. 优化的任务设计
2. 合理的工作进程配置
3. 任务路由和优先级
4. 资源管理
5. 错误处理和监控
"""

from celery import Celery, Task
from celery.signals import after_setup_task_logger
import logging
import os
import redis
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 应用配置
app = Celery('high_performance')

# 加载配置
env = os.environ.get('CELERY_ENV', 'development')
if env == 'development':
    app.config_from_object('config.DevelopmentConfig')
elif env == 'production':
    app.config_from_object('config.ProductionConfig')

# 设置日志
@after_setup_task_logger.connect

def setup_task_logger(logger, *args, **kwargs):
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(task_name)s(%(task_id)s)] - %(message)s'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 初始化资源池

# 1. 数据库连接池
db_engine = create_engine(
    app.conf.get('DATABASE_URL'),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# 2. Redis客户端
redis_client = redis.Redis(
    host=app.conf.get('REDIS_HOST'),
    port=app.conf.get('REDIS_PORT'),
    db=app.conf.get('REDIS_DB', 0),
    socket_connect_timeout=5,
    socket_timeout=30
)

# 3. HTTP会话池
http_session = requests.Session()
retry = Retry(total=3, backoff_factor=0.1)
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry)
http_session.mount('http://', adapter)
http_session.mount('https://', adapter)

# 自定义任务基类
class OptimizedTask(Task):
    """优化的任务基类"""
    abstract = True
    autoretry_for = (Exception,)
    retry_backoff = 2
    retry_backoff_max = 300
    retry_jitter = True
    
    def before_start(self, task_id, args, kwargs):
        """任务开始前的钩子"""
        self.logger.info(f"Starting task with args: {args}, kwargs: {kwargs}")
        
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功后的钩子"""
        self.logger.info(f"Task completed with result: {retval}")
        
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败后的钩子"""
        self.logger.error(f"Task failed with error: {exc}")
        
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """任务返回后的钩子"""
        # 清理资源
        pass

# 分布式锁辅助函数
def acquire_lock(lock_name, timeout=60):
    """获取分布式锁"""
    return redis_client.lock(lock_name, timeout=timeout)

# 任务示例

@app.task(base=OptimizedTask, queue='cpu_intensive', priority=5)
def data_processing_task(data_id):
    """CPU密集型数据处理任务"""
    # 从数据库获取数据
    with db_engine.connect() as conn:
        result = conn.execute(f"SELECT * FROM data WHERE id = {data_id}")
        data = result.fetchone()
    
    if not data:
        raise ValueError(f"Data with id {data_id} not found")
    
    # 处理数据（CPU密集型操作）
    import time
    # 模拟CPU密集型计算
    time.sleep(5)
    
    # 保存结果
    with db_engine.connect() as conn:
        conn.execute(f"UPDATE data SET processed = TRUE WHERE id = {data_id}")
    
    return {"status": "success", "processed_id": data_id}

@app.task(base=OptimizedTask, queue='io_intensive', priority=10)
def external_api_task(endpoint, params):
    """I/O密集型API调用任务"""
    # 使用HTTP会话池发送请求
    response = http_session.get(
        endpoint,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    
    # 处理响应
    data = response.json()
    
    # 保存结果到Redis
    cache_key = f"api_result:{endpoint}:{hash(str(params))}"
    redis_client.setex(cache_key, 3600, response.content)
    
    return data

@app.task(base=OptimizedTask, queue='default', priority=3, ignore_result=True)
def notification_task(user_id, message):
    """通知任务，不需要结果"""
    # 获取用户信息
    with db_engine.connect() as conn:
        result = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
        user = result.fetchone()
    
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    # 获取分布式锁，防止重复发送
    lock_name = f"notification_lock:{user_id}:{hash(message)}"
    with acquire_lock(lock_name, timeout=10):
        # 模拟发送通知
        print(f"Sending notification to user {user_id}: {message}")
        # 这里应该调用实际的通知服务

@app.task(base=OptimizedTask, queue='critical', priority=15)
def critical_business_task(business_id):
    """关键业务任务，高优先级"""
    # 获取分布式锁确保任务互斥执行
    lock_name = f"business_lock:{business_id}"
    with acquire_lock(lock_name, timeout=60):
        # 执行关键业务逻辑
        print(f"Processing critical business task: {business_id}")
        # 模拟业务处理
        import time
        time.sleep(2)
    
    return {"business_id": business_id, "status": "processed"}

# 任务链和组示例
def process_workflow(batch_id):
    """处理工作流示例"""
    from celery import chain, group, chord
    
    # 步骤1: 验证批次
    verify_task = verify_batch.s(batch_id)
    
    # 步骤2: 并行处理所有项目
    def get_items(batch_id):
        # 实际实现中应该从数据库获取项目列表
        return [1, 2, 3, 4, 5]
    
    # 动态创建任务组
    item_tasks = group(process_item.s(item_id) for item_id in get_items(batch_id))
    
    # 步骤3: 汇总结果
    summarize_task = summarize_batch.s(batch_id)
    
    # 创建任务链
    workflow = verify_task | item_tasks | summarize_task
    
    # 执行工作流
    result = workflow.apply_async()
    return result.id

@app.task(base=OptimizedTask)
def verify_batch(batch_id):
    """验证批次"""
    print(f"Verifying batch: {batch_id}")
    return batch_id

@app.task(base=OptimizedTask)
def process_item(item_id):
    """处理单个项目"""
    print(f"Processing item: {item_id}")
    return {"item_id": item_id, "status": "processed"}

@app.task(base=OptimizedTask)
def summarize_batch(results, batch_id):
    """汇总批次结果"""
    processed_count = len(results)
    print(f"Batch {batch_id} processed: {processed_count} items")
    return {"batch_id": batch_id, "processed_count": processed_count}

# 主函数
def main():
    """演示函数"""
    print("高性能Celery应用示例")
    print("\n可用的任务:")
    print("1. data_processing_task - CPU密集型数据处理")
    print("2. external_api_task - I/O密集型API调用")
    print("3. notification_task - 通知任务")
    print("4. critical_business_task - 关键业务任务")
    print("5. process_workflow - 工作流处理")
    
    # 示例调用
    task_id = data_processing_task.delay(123)
    print(f"\n提交的数据处理任务ID: {task_id}")

if __name__ == "__main__":
    main()
```

这个示例展示了如何构建一个高性能的Celery应用，包括任务设计优化、资源池管理、分布式锁实现、任务路由和优先级设置等。通过遵循这些最佳实践，您可以显著提高Celery应用的性能和可靠性。
