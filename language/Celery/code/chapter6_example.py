#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chapter6_example.py - Celery监控与管理示例代码

这个示例演示了如何监控和管理Celery系统，包括：
1. 任务执行监控
2. Prometheus指标集成
3. 日志管理与配置
4. Flower监控工具集成
5. 任务状态跟踪和管理
6. 系统资源监控
7. 告警与通知机制
8. 健康检查任务
"""

from celery import Celery
import time
import random
import logging
import os
import sys
import functools
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil
import json

# 确保中文显示正常
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# ==================================== 配置日志 ====================================

# 创建日志目录
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# 配置根日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'celery_monitor.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

# 创建特定的日志记录器
logger = logging.getLogger('celery.monitor')
worker_logger = logging.getLogger('celery.worker')
task_logger = logging.getLogger('celery.task')

# ==================================== 创建Celery应用 ====================================

app = Celery(
    'monitoring_example',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['chapter6_example']  # 确保任务可以被发现
)

# ==================================== 应用配置 ====================================

app.conf.update(
    # 基本配置
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务跟踪配置
    task_track_started=True,
    task_acks_late=True,  # 任务完成后才确认
    
    # 日志配置
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    worker_loglevel='INFO',
    
    # 工作进程配置
    worker_concurrency=4,  # 并发工作进程数
    worker_prefetch_multiplier=1,  # 每个工作进程预取的任务数
    worker_max_tasks_per_child=100,  # 每个工作进程最多执行的任务数
    worker_disable_rate_limits=True,  # 禁用速率限制
    
    # 任务配置
    task_soft_time_limit=60,  # 软时间限制（秒）
    task_time_limit=120,  # 硬时间限制（秒）
    task_reject_on_worker_lost=True,  # 工作进程意外终止时拒绝任务
    
    # 结果配置
    result_backend='redis://localhost:6379/0',
    result_expires=3600,  # 结果过期时间（秒）
    
    # 任务路由配置
    task_routes={
        'chapter6_example.health_check': {'queue': 'monitoring'},
        'chapter6_example.metrics_task': {'queue': 'monitoring'},
        'chapter6_example.critical_task': {'queue': 'critical'}
    },
    
    # 定时任务配置
    beat_schedule={
        'health-check-every-30-seconds': {
            'task': 'chapter6_example.health_check',
            'schedule': 30.0,
        },
        'update-metrics-every-minute': {
            'task': 'chapter6_example.metrics_task',
            'schedule': 60.0,
        },
        'run-sample-task-every-10-seconds': {
            'task': 'chapter6_example.sample_task',
            'schedule': 10.0,
            'args': (random.randint(1, 10),),
        },
    },
)

# ==================================== Prometheus指标定义 ====================================

# 任务计数器 - 按状态和任务名称分类
TASK_COUNTER = Counter('celery_tasks_total', 'Total number of tasks by state', ['state', 'task_name'])

# 任务执行时间直方图
TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task execution time in seconds', ['task_name'])

# 活跃任务数
ACTIVE_TASKS = Gauge('celery_active_tasks', 'Number of currently active tasks')

# 任务队列长度
QUEUE_SIZE = Gauge('celery_queue_size', 'Current size of task queues', ['queue_name'])

# 工作进程状态指标
WORKER_STATUS = Gauge('celery_worker_status', 'Worker status (1=active, 0=inactive)', ['worker_name'])
WORKER_MEMORY = Gauge('celery_worker_memory_percent', 'Worker memory usage percentage', ['worker_name'])
WORKER_CPU = Gauge('celery_worker_cpu_percent', 'Worker CPU usage percentage', ['worker_name'])

# 系统资源指标
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage percentage')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'System memory usage percentage')
SYSTEM_DISK = Gauge('system_disk_percent', 'System disk usage percentage', ['mount_point'])

# ==================================== 任务装饰器 ====================================

def monitored_task(task_func):
    """
    任务监控装饰器 - 添加监控指标收集功能
    
    Args:
        task_func: 原始任务函数
        
    Returns:
        装饰后的任务函数
    """
    @functools.wraps(task_func)
    def wrapper(self, *args, **kwargs):
        task_name = task_func.__name__
        
        # 增加活跃任务计数
        ACTIVE_TASKS.inc()
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 记录任务开始
            task_logger.info(f"Task {task_name} started with args={args}, kwargs={kwargs}")
            
            # 执行任务
            result = task_func(self, *args, **kwargs)
            
            # 记录成功
            TASK_COUNTER.labels(state='success', task_name=task_name).inc()
            task_logger.info(f"Task {task_name} completed successfully")
            
            return result
            
        except Exception as e:
            # 记录失败
            TASK_COUNTER.labels(state='error', task_name=task_name).inc()
            task_logger.error(f"Task {task_name} failed with error: {str(e)}", exc_info=True)
            
            # 这里可以添加告警逻辑
            # send_alert(f"Task {task_name} failed", str(e))
            
            # 重新抛出异常
            raise
            
        finally:
            # 计算执行时间
            duration = time.time() - start_time
            
            # 更新指标
            TASK_DURATION.labels(task_name=task_name).observe(duration)
            ACTIVE_TASKS.dec()
            
            # 记录执行时间
            task_logger.info(f"Task {task_name} execution time: {duration:.2f} seconds")
    
    return wrapper

# ==================================== 任务定义 ====================================

@app.task(bind=True, name='chapter6_example.sample_task')
@monitored_task
def sample_task(self, iterations=5):
    """
    示例任务 - 模拟基本计算工作
    
    Args:
        iterations: 迭代次数
        
    Returns:
        计算结果
    """
    result = 0
    for i in range(iterations):
        result += i * i
        time.sleep(0.1)  # 模拟工作
    return {'result': result, 'iterations': iterations}


@app.task(bind=True, name='chapter6_example.long_running_task')
@monitored_task
def long_running_task(self, total_steps=100):
    """
    长时间运行的任务 - 演示进度更新
    
    Args:
        total_steps: 总步骤数
        
    Returns:
        任务结果
    """
    for step in range(total_steps):
        # 模拟工作
        time.sleep(0.05)
        
        # 计算进度
        progress = (step + 1) / total_steps * 100
        
        # 更新任务状态（进度）
        self.update_state(
            state='PROGRESS',
            meta={
                'current': step + 1,
                'total': total_steps,
                'progress': progress,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # 记录进度（高进度时记录，避免日志过多）
        if (step + 1) % 20 == 0 or step + 1 == total_steps:
            task_logger.info(f"Task progress: {progress:.1f}% ({step + 1}/{total_steps})")
    
    return {
        'status': 'completed',
        'total_steps': total_steps,
        'timestamp': datetime.now().isoformat()
    }


@app.task(bind=True, name='chapter6_example.unstable_task')
@monitored_task
def unstable_task(self, failure_probability=0.3):
    """
    不稳定任务 - 模拟可能失败的任务
    
    Args:
        failure_probability: 失败概率 (0-1之间)
        
    Returns:
        任务结果
    """
    task_logger.info(f"Executing unstable task with failure probability: {failure_probability}")
    
    # 模拟一些工作
    time.sleep(0.5)
    
    # 随机失败
    if random.random() < failure_probability:
        error_msg = f"Task failed randomly (probability: {failure_probability})"
        task_logger.warning(error_msg)
        raise Exception(error_msg)
    
    # 模拟更多工作
    time.sleep(0.5)
    
    return {'status': 'success', 'message': 'Task completed successfully'}


@app.task(bind=True, name='chapter6_example.critical_task')
@monitored_task
def critical_task(self, data=None):
    """
    关键任务 - 高优先级任务示例
    
    Args:
        data: 任务数据
        
    Returns:
        处理结果
    """
    task_logger.info(f"Processing critical task with data: {data}")
    
    # 模拟关键处理
    time.sleep(1.0)
    
    result = {
        'status': 'processed',
        'timestamp': datetime.now().isoformat(),
        'data': data,
        'processed_by': self.request.hostname
    }
    
    task_logger.info(f"Critical task processed: {json.dumps(result)}")
    return result


@app.task(bind=True, name='chapter6_example.resource_intensive_task')
@monitored_task
def resource_intensive_task(self):
    """
    资源密集型任务 - 模拟CPU密集型计算
    
    Returns:
        计算结果
    """
    task_logger.info("Starting resource intensive task")
    
    # 模拟CPU密集型计算
    result = 0
    iterations = 10_000_000  # 1千万次迭代
    for i in range(iterations):
        result += i * i * i  # 更复杂的计算
    
    task_logger.info(f"Resource intensive task completed. Result: {result}")
    return {
        'result': result,
        'iterations': iterations
    }


@app.task(bind=True, name='chapter6_example.health_check')
@monitored_task
def health_check(self):
    """
    健康检查任务 - 监控系统和工作进程健康状态
    
    Returns:
        健康状态信息
    """
    # 获取进程信息
    process = psutil.Process()
    
    # 获取系统信息
    system_info = {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': {part.mountpoint: psutil.disk_usage(part.mountpoint).percent 
                        for part in psutil.disk_partitions()},
        'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
        'timestamp': datetime.now().isoformat()
    }
    
    # 获取进程信息
    process_info = {
        'pid': process.pid,
        'cpu_percent': process.cpu_percent(interval=0.1),
        'memory_percent': process.memory_percent(),
        'name': process.name(),
        'status': process.status(),
        'threads': len(process.threads()),
        'created_at': datetime.fromtimestamp(process.create_time()).isoformat()
    }
    
    # 更新Prometheus指标
    SYSTEM_CPU.set(system_info['cpu_percent'])
    SYSTEM_MEMORY.set(system_info['memory_percent'])
    
    for mount_point, percent in system_info['disk_percent'].items():
        SYSTEM_DISK.labels(mount_point=mount_point).set(percent)
    
    worker_name = f"worker@{self.request.hostname}"
    WORKER_STATUS.labels(worker_name=worker_name).set(1)
    WORKER_MEMORY.labels(worker_name=worker_name).set(process_info['memory_percent'])
    WORKER_CPU.labels(worker_name=worker_name).set(process_info['cpu_percent'])
    
    # 记录健康检查结果
    health_logger = logging.getLogger('celery.health')
    health_logger.info(f"Health check result: system_cpu={system_info['cpu_percent']}%, "
                     f"system_memory={system_info['memory_percent']}%, "
                     f"process_cpu={process_info['cpu_percent']}%, "
                     f"process_memory={process_info['memory_percent']}%")
    
    # 检查阈值，记录警告
    if system_info['cpu_percent'] > 90:
        health_logger.warning(f"HIGH SYSTEM CPU USAGE: {system_info['cpu_percent']}%")
    
    if system_info['memory_percent'] > 90:
        health_logger.warning(f"HIGH SYSTEM MEMORY USAGE: {system_info['memory_percent']}%")
    
    return {
        'system': system_info,
        'process': process_info,
        'hostname': self.request.hostname,
        'worker_pid': os.getpid()
    }


@app.task(bind=True, name='chapter6_example.metrics_task')
@monitored_task
def metrics_task(self):
    """
    指标收集任务 - 收集和更新系统监控指标
    
    Returns:
        收集的指标信息
    """
    # 这里可以添加更多的指标收集逻辑
    # 例如，从Redis获取队列长度等
    
    # 示例：模拟队列长度更新
    try:
        import redis
        r = redis.Redis()
        
        # 获取默认队列长度
        default_queue_length = r.llen('celery')
        QUEUE_SIZE.labels(queue_name='celery').set(default_queue_length)
        
        # 获取监控队列长度
        monitoring_queue_length = r.llen('monitoring')
        QUEUE_SIZE.labels(queue_name='monitoring').set(monitoring_queue_length)
        
        # 获取关键队列长度
        critical_queue_length = r.llen('critical')
        QUEUE_SIZE.labels(queue_name='critical').set(critical_queue_length)
        
        logger.info(f"Updated queue metrics - default: {default_queue_length}, "
                  f"monitoring: {monitoring_queue_length}, critical: {critical_queue_length}")
    except Exception as e:
        logger.error(f"Failed to update queue metrics: {str(e)}")
    
    return {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'message': 'Metrics collected successfully'
    }


@app.task(bind=True, name='chapter6_example.create_sample_data')
@monitored_task
def create_sample_data(self, task_count=100):
    """
    创建示例数据 - 生成多个任务用于测试和监控
    
    Args:
        task_count: 要创建的任务数量
        
    Returns:
        创建的任务信息
    """
    task_logger.info(f"Creating {task_count} sample tasks")
    
    # 记录开始时间
    start_time = time.time()
    created_tasks = 0
    task_ids = []
    
    try:
        # 创建不同类型的任务
        for i in range(task_count):
            # 随机选择任务类型
            task_type = random.choice(['sample', 'long_running', 'unstable', 'resource_intensive'])
            
            # 提交任务
            if task_type == 'sample':
                result = sample_task.delay(random.randint(1, 20))
            elif task_type == 'long_running':
                result = long_running_task.delay(random.randint(50, 200))
            elif task_type == 'unstable':
                result = unstable_task.delay(random.uniform(0.1, 0.5))
            else:  # resource_intensive
                # 减少资源密集型任务的数量
                if i % 10 == 0:
                    result = resource_intensive_task.delay()
                    task_ids.append(result.id)
                    created_tasks += 1
                continue
            
            task_ids.append(result.id)
            created_tasks += 1
            
            # 小延迟，避免过多并发
            if i % 20 == 0:
                time.sleep(0.1)
        
        duration = time.time() - start_time
        task_logger.info(f"Created {created_tasks} sample tasks in {duration:.2f} seconds")
        
        return {
            'task_count': created_tasks,
            'task_ids': task_ids[:10],  # 只返回部分ID，避免过大
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        task_logger.error(f"Failed to create sample tasks: {str(e)}")
        raise

# ==================================== 监控工具函数 ====================================

def start_prometheus_server(port=8000):
    """
    启动Prometheus指标HTTP服务器
    
    Args:
        port: 服务器端口
    """
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
        return True
    except Exception as e:
        logger.error(f"Failed to start Prometheus metrics server: {str(e)}")
        return False


def setup_monitoring():
    """
    设置完整的监控系统
    
    Returns:
        配置结果
    """
    # 启动Prometheus服务器
    prometheus_started = start_prometheus_server()
    
    # 初始化指标
    ACTIVE_TASKS.set(0)
    SYSTEM_CPU.set(0)
    SYSTEM_MEMORY.set(0)
    
    # 为常见队列初始化指标
    for queue_name in ['celery', 'monitoring', 'critical']:
        QUEUE_SIZE.labels(queue_name=queue_name).set(0)
    
    logger.info("Monitoring system initialized")
    return {
        'prometheus_started': prometheus_started,
        'timestamp': datetime.now().isoformat()
    }


# ==================================== 演示函数 ====================================

def demonstrate_usage():
    """
    演示如何使用这个监控示例
    """
    print("\n" + "="*80)
    print("Celery监控与管理示例")
    print("="*80)
    print("\n这个示例演示了Celery的完整监控与管理功能，包括:")
    print("  1. 任务执行监控")
    print("  2. Prometheus指标收集")
    print("  3. 日志管理")
    print("  4. 工作进程健康检查")
    print("  5. 系统资源监控")
    print("  6. 任务进度跟踪")
    print("  7. 队列监控")
    
    print("\n要运行此示例，请按照以下步骤操作:")
    print("\n1. 确保Redis服务已启动")
    print("   可以通过以下命令检查:")
    print("   redis-cli ping")
    print("   (应该返回: PONG)")
    
    print("\n2. 安装必要的依赖:")
    print("   pip install celery redis prometheus_client psutil matplotlib")
    
    print("\n3. 启动Celery Worker:")
    print("   celery -A chapter6_example worker --loglevel=info -Q celery,monitoring,critical")
    
    print("\n4. 在另一个终端启动Celery Beat:")
    print("   celery -A chapter6_example beat --loglevel=info")
    
    print("\n5. 在另一个终端启动Flower监控:")
    print("   celery -A chapter6_example flower")
    print("   然后访问 http://localhost:5555")
    
    print("\n6. 查看Prometheus指标:")
    print("   访问 http://localhost:8000/metrics")
    
    print("\n7. 提交示例任务:")
    print("   python -c """
    print("   from chapter6_example import *")
    print("   setup_monitoring()")
    print("   print('提交示例任务...')")
    print("   # 提交单个任务")
    print("   result = sample_task.delay(10)")
    print("   print(f'基本任务ID: {result.id}')")
    print("   # 提交长时间运行的任务")
    print("   long_result = long_running_task.delay(50)")
    print("   print(f'长时间运行任务ID: {long_result.id}')")
    print("   # 提交多个测试任务")
    print("   batch_result = create_sample_data.delay(20)")
    print("   print(f'批量任务ID: {batch_result.id}')")
    print("   """)
    
    print("\n监控技巧:")
    print("  - 在Flower界面查看实时任务状态和工作进程信息")
    print("  - 检查日志文件了解详细执行情况")
    print("  - 通过Prometheus指标分析系统性能")
    print("  - 观察不同类型任务的执行行为")
    print("\n" + "="*80 + "\n")

# ==================================== 主函数 ====================================

if __name__ == '__main__':
    # 设置监控
    setup_monitoring()
    
    # 显示使用说明
    demonstrate_usage()
    
    # 可以直接在这里提交一些测试任务
    print("提交演示任务...")
    
    try:
        # 提交一个示例任务
        result = sample_task.delay(5)
        print(f"示例任务已提交，任务ID: {result.id}")
        
        # 提交一个长时间运行的任务用于演示进度
        long_result = long_running_task.delay(30)
        print(f"进度跟踪任务已提交，任务ID: {long_result.id}")
        
        # 提交几个不稳定任务
        for _ in range(3):
            unstable_task.delay(0.2)  # 20%的失败概率
        print("已提交3个不稳定任务用于测试错误处理")
        
        print("\n请启动Celery Worker和Beat来处理这些任务。")
        print("查看Flower界面 (http://localhost:5555) 监控任务执行情况。")
        
    except Exception as e:
        print(f"提交任务时出错: {str(e)}")
        print("请确保Redis服务已启动并且可访问。")
