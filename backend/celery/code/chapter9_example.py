"""
Celery性能优化与最佳实践示例

本章代码演示了如何实现Celery的各种性能优化技术，包括：
1. 工作进程优化配置
2. 任务粒度和优先级设计
3. 消息代理和结果后端优化
4. 资源池管理
5. 分布式锁实现
6. 任务路由和队列设计
7. 监控和错误处理
"""

import os
import time
import logging
from functools import wraps
from datetime import timedelta
from celery import Celery, Task, chain, group, chord
from celery.signals import after_setup_task_logger, worker_process_init, worker_process_shutdown
import redis
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 设置基础日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Celery应用
app = Celery('performance_optimization')

# 配置加载 - 根据环境变量选择配置
ENV = os.environ.get('CELERY_ENV', 'development')

# 配置类
class BaseConfig:
    """基础配置类"""
    # 消息代理配置
    BROKER_URL = 'redis://localhost:6379/0'
    BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,  # 任务可见性超时时间
        'max_retries': 3,
        'socket_connect_timeout': 5,
        'socket_timeout': 30,
    }
    BROKER_POOL_LIMIT = 10  # 连接池大小
    
    # 结果后端配置
    RESULT_BACKEND = 'redis://localhost:6379/0'
    RESULT_SERIALIZER = 'json'
    RESULT_EXPIRES = 3600  # 结果过期时间
    RESULT_BACKEND_TRANSPORT_OPTIONS = {
        'visibility_timeout': 86400,
    }
    
    # 任务配置
    TASK_SERIALIZER = 'json'
    ACCEPT_CONTENT = ['json', 'msgpack']  # 支持的内容类型
    TASK_COMPRESSION = 'gzip'  # 启用压缩
    TASK_SEND_SENT_EVENT = True  # 发送任务事件
    TASK_IGNORE_RESULT = False  # 默认存储结果
    
    # 工作进程配置
    WORKER_PREFETCH_MULTIPLIER = 1  # 预取任务数
    WORKER_MAX_TASKS_PER_CHILD = 1000  # 每个子进程最大任务数
    WORKER_DISABLE_RATE_LIMITS = True  # 禁用速率限制
    
    # 路由配置
    TASK_ROUTES = {
        'performance_optimization.cpu_intensive.*': {'queue': 'cpu_intensive'},
        'performance_optimization.io_intensive.*': {'queue': 'io_intensive'},
        'performance_optimization.critical.*': {'queue': 'critical'},
    }
    
    # 任务队列配置
    TASK_QUEUES = {
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
        },
        'critical': {
            'exchange': 'critical_tasks',
            'exchange_type': 'direct',
            'routing_key': 'task.critical',
        }
    }
    TASK_QUEUE_MAX_PRIORITY = 10  # 最大优先级
    
    # 数据库配置
    DATABASE_URL = 'sqlite:///:memory:'
    
    # Redis配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0

class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    CELERYD_LOG_LEVEL = 'DEBUG'
    CELERYD_PREFETCH_MULTIPLIER = 1
    WORKER_MAX_TASKS_PER_CHILD = 100

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    # 增加连接池大小
    BROKER_POOL_LIMIT = 20
    
    # 生产环境结果存储时间更长
    RESULT_EXPIRES = 86400  # 1天
    
    # 工作进程配置更严格
    WORKER_PREFETCH_MULTIPLIER = 4  # 预取更多任务
    WORKER_MAX_TASKS_PER_CHILD = 500  # 避免内存泄漏
    WORKER_MAX_MEMORY_PER_CHILD = 50000  # 50MB内存限制

# 根据环境加载配置
if ENV == 'development':
    app.config_from_object(DevelopmentConfig)
elif ENV == 'production':
    app.config_from_object(ProductionConfig)
else:
    app.config_from_object(BaseConfig)

# 配置日志
@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    """设置任务日志格式"""
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(task_name)s(%(task_id)s)] - %(message)s'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 全局资源池 - 使用threading.local存储线程本地资源
import threading
_local = threading.local()

@worker_process_init.connect
def init_worker_process(**kwargs):
    """工作进程初始化时创建资源池"""
    # 数据库连接池
    _local.db_engine = create_engine(
        app.conf.get('DATABASE_URL'),
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800
    )
    
    # Redis客户端
    _local.redis_client = redis.Redis(
        host=app.conf.get('REDIS_HOST'),
        port=app.conf.get('REDIS_PORT'),
        db=app.conf.get('REDIS_DB'),
        socket_connect_timeout=5,
        socket_timeout=30
    )
    
    # HTTP会话池
    _local.http_session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1)
    adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=retry)
    _local.http_session.mount('http://', adapter)
    _local.http_session.mount('https://', adapter)

@worker_process_shutdown.connect
def shutdown_worker_process(**kwargs):
    """工作进程关闭时清理资源"""
    if hasattr(_local, 'db_engine'):
        _local.db_engine.dispose()
    
    if hasattr(_local, 'http_session'):
        _local.http_session.close()

# 获取本地资源的辅助函数
def get_db_engine():
    """获取数据库引擎"""
    return getattr(_local, 'db_engine', None)

def get_redis_client():
    """获取Redis客户端"""
    return getattr(_local, 'redis_client', None)

def get_http_session():
    """获取HTTP会话"""
    return getattr(_local, 'http_session', requests)

# 自定义任务基类
class OptimizedTask(Task):
    """优化的任务基类"""
    abstract = True
    autoretry_for = (Exception,)
    retry_backoff = 2
    retry_backoff_max = 300
    retry_jitter = True
    
    def __init__(self):
        self.logger = logging.getLogger(f"celery.task.{self.name}")
    
    def before_start(self, task_id, args, kwargs):
        """任务开始前的钩子"""
        self.logger.info(f"Starting task with args: {args}, kwargs: {kwargs}")
        # 记录任务开始时间
        self.start_time = time.time()
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功后的钩子"""
        execution_time = time.time() - self.start_time
        self.logger.info(f"Task completed in {execution_time:.2f}s with result: {retval}")
        
        # 可选：记录性能指标到监控系统
        redis_client = get_redis_client()
        if redis_client:
            redis_client.hincrby('celery:metrics', f'task:{self.name}:success', 1)
            redis_client.hincrbyfloat('celery:metrics', f'task:{self.name}:time', execution_time)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败后的钩子"""
        execution_time = time.time() - self.start_time
        self.logger.error(f"Task failed after {execution_time:.2f}s with error: {exc}")
        
        # 可选：记录失败指标和告警
        redis_client = get_redis_client()
        if redis_client:
            redis_client.hincrby('celery:metrics', f'task:{self.name}:failure', 1)
            
            # 记录失败详情，用于后续分析
            error_key = f'celery:errors:{task_id}'
            error_info = {
                'task': self.name,
                'error': str(exc),
                'args': str(args),
                'kwargs': str(kwargs),
                'timestamp': time.time()
            }
            redis_client.hset(error_key, mapping=error_info)
            redis_client.expire(error_key, 86400)  # 24小时过期

# 分布式锁辅助函数
def acquire_lock(lock_name, timeout=60):
    """获取分布式锁"""
    redis_client = get_redis_client()
    if redis_client:
        return redis_client.lock(lock_name, timeout=timeout)
    return None

# 任务装饰器

def task_time_limit(seconds):
    """任务执行时间限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            if execution_time > seconds:
                logger.warning(
                    f"Task {func.__name__} executed in {execution_time:.2f}s, "
                    f"exceeding the recommended limit of {seconds}s"
                )
            
            return result
        return wrapper
    return decorator

# CPU密集型任务示例

@app.task(base=OptimizedTask, queue='cpu_intensive', priority=5, 
         name='performance_optimization.cpu_intensive.data_processing')
@task_time_limit(10)  # 设置时间限制

def data_processing_task(data_id):
    """CPU密集型数据处理任务"""
    # 实际应用中应该从数据库获取数据
    logger.info(f"Processing data with ID: {data_id}")
    
    # 模拟CPU密集型计算
    result = 0
    for i in range(10000000):  # 大数据量计算
        result += i * data_id
    
    # 模拟保存结果
    redis_client = get_redis_client()
    if redis_client:
        redis_client.setex(f"processed_data:{data_id}", 3600, str(result))
    
    return {"status": "success", "processed_id": data_id, "result": result % 1000}

@app.task(base=OptimizedTask, queue='cpu_intensive', priority=3,
         name='performance_optimization.cpu_intensive.batch_process')

def batch_process_task(data_items):
    """批量数据处理任务 - 展示任务粒度优化"""
    # 更新任务状态和进度
    total_items = len(data_items)
    processed_items = 0
    
    results = []
    for item in data_items:
        # 处理单个项目
        result = process_single_item(item)
        results.append(result)
        
        processed_items += 1
        # 每处理10%的项目更新一次状态
        if processed_items % max(1, total_items // 10) == 0:
            progress = int(processed_items / total_items * 100)
            # 更新任务进度
            batch_process_task.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'processed': processed_items,
                    'total': total_items
                }
            )
    
    return {
        "status": "success",
        "processed_count": len(results),
        "results": results[:10]  # 只返回部分结果，避免结果过大
    }

def process_single_item(item):
    """处理单个项目"""
    # 模拟处理
    time.sleep(0.05)
    return {"item": item, "processed": True, "value": item * 2}

# I/O密集型任务示例

@app.task(base=OptimizedTask, queue='io_intensive', priority=10,
         name='performance_optimization.io_intensive.external_api_call')

def external_api_task(endpoint, params, timeout=10):
    """I/O密集型API调用任务"""
    logger.info(f"Calling external API: {endpoint} with params: {params}")
    
    # 使用HTTP会话池发送请求
    http_session = get_http_session()
    
    try:
        # 尝试从缓存获取结果（如果适用）
        redis_client = get_redis_client()
        cache_key = None
        if redis_client and 'cache' in params and params['cache']:
            cache_key = f"api_cache:{hash(endpoint + str(params))}"
            cached_result = redis_client.get(cache_key)
            if cached_result:
                import json
                logger.info(f"Returning cached result for {endpoint}")
                return json.loads(cached_result)
        
        # 发送实际请求
        response = http_session.get(
            endpoint,
            params=params,
            timeout=timeout
        )
        response.raise_for_status()
        
        result = response.json()
        
        # 缓存结果（如果适用）
        if cache_key:
            redis_client.setex(cache_key, 3600, response.content)  # 缓存1小时
        
        return result
    
    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        # 对于临时错误（如超时），我们可以重试
        if isinstance(e, (requests.Timeout, requests.ConnectionError)):
            raise
        # 对于其他错误，直接返回错误信息
        return {"error": str(e), "endpoint": endpoint}

@app.task(base=OptimizedTask, queue='io_intensive', priority=5, ignore_result=True,
         name='performance_optimization.io_intensive.file_processing')

def file_processing_task(file_path):
    """文件处理任务 - 不需要返回结果"""
    logger.info(f"Processing file: {file_path}")
    
    try:
        # 模拟文件处理
        time.sleep(1)  # 模拟I/O操作时间
        
        # 实际应用中应该处理文件内容
        # 这里只是演示，检查文件是否存在
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.info(f"Processed file: {file_path}, size: {file_size} bytes")
        else:
            logger.warning(f"File not found: {file_path}")
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise

# 关键任务示例

@app.task(base=OptimizedTask, queue='critical', priority=15,
         name='performance_optimization.critical.payment_processing')

def payment_processing_task(payment_id, amount, user_id):
    """关键支付处理任务 - 使用分布式锁确保幂等性"""
    logger.info(f"Processing payment: {payment_id} for user: {user_id}, amount: {amount}")
    
    # 获取分布式锁，确保任务只执行一次
    lock_name = f"payment_lock:{payment_id}"
    lock = acquire_lock(lock_name, timeout=60)
    
    if not lock:
        logger.error("Could not acquire distributed lock for payment processing")
        raise RuntimeError("Could not acquire distributed lock for payment processing")
    
    with lock:
        # 检查支付是否已处理（幂等性检查）
        redis_client = get_redis_client()
        payment_status = redis_client.get(f"payment_status:{payment_id}")
        
        if payment_status == b"completed":
            logger.info(f"Payment {payment_id} already processed, skipping")
            return {"payment_id": payment_id, "status": "completed", "duplicate": True}
        
        # 模拟支付处理
        time.sleep(2)  # 模拟支付网关调用
        
        # 更新支付状态
        redis_client.setex(f"payment_status:{payment_id}", 86400, "completed")
        
        # 记录支付日志
        payment_log = {
            "payment_id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "timestamp": time.time(),
            "status": "completed"
        }
        
        # 保存到Redis哈希结构
        redis_client.hset(f"payment_log:{payment_id}", mapping=payment_log)
        
        logger.info(f"Payment {payment_id} processed successfully")
        return {"payment_id": payment_id, "status": "completed", "amount": amount, "user_id": user_id}

# 任务链和工作流示例

@app.task(base=OptimizedTask)
def verify_order(order_id):
    """验证订单"""
    logger.info(f"Verifying order: {order_id}")
    time.sleep(0.5)  # 模拟验证时间
    return order_id

@app.task(base=OptimizedTask)
def process_order_item(item_id, order_id):
    """处理订单项"""
    logger.info(f"Processing order item: {item_id} for order: {order_id}")
    time.sleep(0.3)  # 模拟处理时间
    return {"item_id": item_id, "status": "processed"}

@app.task(base=OptimizedTask)
def calculate_total(results, order_id):
    """计算订单总额"""
    logger.info(f"Calculating total for order: {order_id}")
    # 模拟计算
    time.sleep(0.5)
    return {
        "order_id": order_id,
        "total_items": len(results),
        "status": "calculated"
    }

@app.task(base=OptimizedTask)
def generate_invoice(order_data):
    """生成发票"""
    order_id = order_data['order_id']
    logger.info(f"Generating invoice for order: {order_id}")
    time.sleep(1)  # 模拟发票生成
    return {
        "order_id": order_id,
        "invoice_id": f"INV-{order_id}-{int(time.time())}",
        "status": "invoice_generated"
    }

@app.task(base=OptimizedTask)
def notify_customer(invoice_data):
    """通知客户"""
    order_id = invoice_data['order_id']
    invoice_id = invoice_data['invoice_id']
    logger.info(f"Notifying customer about order: {order_id} and invoice: {invoice_id}")
    return {
        "order_id": order_id,
        "invoice_id": invoice_id,
        "status": "notification_sent",
        "timestamp": time.time()
    }

def process_order_workflow(order_id, item_ids):
    """完整订单处理工作流"""
    # 1. 验证订单
    verify_task = verify_order.s(order_id)
    
    # 2. 并行处理所有订单项
    item_tasks = group(process_order_item.s(item_id, order_id) for item_id in item_ids)
    
    # 3. 计算总额
    calculate_task = calculate_total.s(order_id)
    
    # 4. 生成发票
    invoice_task = generate_invoice.s()
    
    # 5. 通知客户
    notify_task = notify_customer.s()
    
    # 创建完整的任务链
    workflow = verify_task | item_tasks | calculate_task | invoice_task | notify_task
    
    # 提交工作流
    result = workflow.apply_async()
    logger.info(f"Submitted order processing workflow for order: {order_id}, task_id: {result.id}")
    return result.id

# 性能优化辅助函数

def optimize_task_submission(tasks, batch_size=100):
    """批量提交任务的优化函数"""
    """
    批量提交任务而不是一个一个提交，可以显著减少与消息代理的通信开销
    适用于需要提交大量相似任务的场景
    """
    # 分割成批次
    batches = [tasks[i:i+batch_size] for i in range(0, len(tasks), batch_size)]
    
    # 记录开始时间
    start_time = time.time()
    batch_results = []
    
    # 批量提交
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i+1}/{len(batches)} with {len(batch)} tasks")
        
        # 创建任务组
        task_group = group(batch)
        result = task_group.apply_async()
        batch_results.append(result)
    
    # 计算总时间
    total_time = time.time() - start_time
    logger.info(f"Submitted {len(tasks)} tasks in {total_time:.2f}s ({len(tasks)/total_time:.2f} tasks/s)")
    
    return batch_results

# 性能基准测试

def run_performance_benchmark():
    """运行性能基准测试"""
    logger.info("=== Starting Performance Benchmark ===")
    
    # 测试1: 任务提交性能
    logger.info("\nTest 1: Task Submission Performance")
    
    # 创建100个简单任务
    simple_tasks = [simple_task.s(i) for i in range(100)]
    
    # 批量提交
    batch_results = optimize_task_submission(simple_tasks, batch_size=20)
    
    # 等待结果
    for result in batch_results:
        result.wait()
    
    # 测试2: 不同并发模式性能对比
    logger.info("\nTest 2: Concurrency Pattern Performance")
    
    # 测试CPU密集型任务
    cpu_tasks = [data_processing_task.s(i) for i in range(10)]
    cpu_start = time.time()
    cpu_results = group(cpu_tasks).apply_async()
    cpu_results.wait()
    cpu_time = time.time() - cpu_start
    logger.info(f"CPU-intensive tasks completed in {cpu_time:.2f}s")
    
    # 测试I/O密集型任务（使用模拟端点）
    io_tasks = [external_api_task.s("https://httpbin.org/delay/1", {"test": i}) for i in range(10)]
    io_start = time.time()
    io_results = group(io_tasks).apply_async()
    io_results.wait()
    io_time = time.time() - io_start
    logger.info(f"I/O-intensive tasks completed in {io_time:.2f}s")
    
    logger.info("\n=== Benchmark Completed ===")

@app.task(base=OptimizedTask)
def simple_task(n):
    """简单任务，用于性能测试"""
    return n * 2

# 主函数
def main():
    """演示函数"""
    print("Celery性能优化与最佳实践示例")
    print("\n本示例展示了以下优化技术:")
    print("1. 工作进程配置优化")
    print("2. 任务路由与优先级设置")
    print("3. 资源池管理（数据库、Redis、HTTP）")
    print("4. 任务粒度优化与批量处理")
    print("5. 分布式锁与幂等性保证")
    print("6. 任务链与工作流优化")
    print("7. 监控与性能指标收集")
    
    print("\n如何使用:")
    print("1. 确保Redis服务正在运行")
    print("2. 根据任务类型启动不同的工作进程:")
    print("   - CPU密集型: celery -A chapter9_example worker --loglevel=info -Q cpu_intensive -P prefork -c 4")
    print("   - I/O密集型: celery -A chapter9_example worker --loglevel=info -Q io_intensive -P gevent -c 100")
    print("   - 关键任务: celery -A chapter9_example worker --loglevel=info -Q critical")
    print("   - 默认队列: celery -A chapter9_example worker --loglevel=info -Q default")
    
    print("\n示例任务调用:")
    
    # 提交CPU密集型任务
    cpu_task = data_processing_task.delay(42)
    print(f"\n提交的CPU密集型任务ID: {cpu_task.id}")
    
    # 提交I/O密集型任务（使用httpbin.org作为测试端点）
    io_task = external_api_task.delay("https://httpbin.org/get", {"test": "example", "cache": True})
    print(f"提交的I/O密集型任务ID: {io_task.id}")
    
    # 提交关键任务（支付处理）
    payment_task = payment_processing_task.delay("PAY-12345", 99.99, "user-123")
    print(f"提交的关键任务ID: {payment_task.id}")
    
    # 运行订单处理工作流
    workflow_id = process_order_workflow("ORD-1000", [1, 2, 3, 4, 5])
    print(f"提交的工作流ID: {workflow_id}")
    
    print("\n要运行性能基准测试，请调用 run_performance_benchmark()")

if __name__ == "__main__":
    main()
