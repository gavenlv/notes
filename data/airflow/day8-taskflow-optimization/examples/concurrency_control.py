"""
Airflow并发控制和资源管理示例
展示如何配置和优化并发参数，管理资源池
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Pool
from airflow.utils.db import create_session
from airflow.exceptions import AirflowException
import time
import random
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import json

# 默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

# 并发控制DAG
dag = DAG(
    'concurrency_control_demo',
    default_args=default_args,
    description='并发控制和资源管理示例',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    # DAG级别的并发控制
    max_active_tasks=6,  # 同时最多运行6个任务
    max_active_runs=1,   # 同时最多运行1个DAG实例
    tags=['concurrency', 'optimization', 'resource-management'],
)

def setup_resource_pools():
    """设置资源池"""
    try:
        with create_session() as session:
            # CPU密集型任务池
            cpu_pool = Pool(
                pool='cpu_intensive_pool',
                slots=2,  # 最多2个并发
                description='CPU密集型任务资源池'
            )
            
            # IO密集型任务池
            io_pool = Pool(
                pool='io_intensive_pool',
                slots=4,  # 最多4个并发
                description='IO密集型任务资源池'
            )
            
            # 内存密集型任务池
            memory_pool = Pool(
                pool='memory_intensive_pool',
                slots=1,  # 最多1个并发
                description='内存密集型任务资源池'
            )
            
            # 数据库连接池
            db_pool = Pool(
                pool='database_pool',
                slots=3,  # 最多3个并发数据库连接
                description='数据库连接资源池'
            )
            
            # 合并或创建资源池
            for pool in [cpu_pool, io_pool, memory_pool, db_pool]:
                existing_pool = session.query(Pool).filter(Pool.pool == pool.pool).first()
                if existing_pool:
                    existing_pool.slots = pool.slots
                    existing_pool.description = pool.description
                else:
                    session.add(pool)
            
            session.commit()
            logging.info("资源池设置完成")
            
    except Exception as e:
        logging.error(f"设置资源池失败: {e}")
        raise

def cpu_intensive_task(task_id: int, duration: int = 10):
    """CPU密集型任务"""
    logging.info(f"CPU任务 {task_id} 开始执行")
    
    # 模拟CPU密集型计算
    start_time = time.time()
    result = 0
    
    while time.time() - start_time < duration:
        # 执行CPU密集型计算
        for i in range(100000):
            result += i ** 2 % 1000000
        
        # 检查系统资源
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > 90:
            logging.warning(f"CPU使用率过高: {cpu_percent}%")
            time.sleep(0.5)  # 短暂休眠以降低CPU负载
    
    logging.info(f"CPU任务 {task_id} 完成")
    return {"task_id": task_id, "cpu_intensive_result": result}

def io_intensive_task(task_id: int, file_count: int = 5):
    """IO密集型任务"""
    logging.info(f"IO任务 {task_id} 开始执行")
    
    results = []
    
    for i in range(file_count):
        # 模拟文件读写操作
        filename = f"/tmp/io_test_{task_id}_{i}.txt"
        
        try:
            # 写入文件
            with open(filename, 'w') as f:
                for j in range(1000):
                    f.write(f"Line {j}: Test data for task {task_id}\n")
            
            # 读取文件
            with open(filename, 'r') as f:
                content = f.read()
                file_size = len(content)
            
            results.append({
                'file_id': i,
                'filename': filename,
                'size': file_size,
                'status': 'completed'
            })
            
            # 模拟网络延迟
            time.sleep(random.uniform(0.1, 0.5))
            
        except Exception as e:
            logging.error(f"IO任务 {task_id} 文件操作失败: {e}")
            results.append({
                'file_id': i,
                'status': 'failed',
                'error': str(e)
            })
    
    logging.info(f"IO任务 {task_id} 完成，处理了 {len(results)} 个文件")
    return {"task_id": task_id, "io_results": results}

def memory_intensive_task(task_id: int, data_size: int = 10000):
    """内存密集型任务"""
    logging.info(f"内存任务 {task_id} 开始执行")
    
    # 监控内存使用
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 创建大数据结构
    large_data = []
    
    for i in range(data_size):
        # 创建较大的数据结构
        record = {
            'id': i,
            'data': 'x' * 1000,  # 1KB的数据
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'task_id': task_id,
                'index': i
            }
        }
        large_data.append(record)
        
        # 定期清理和监控
        if i % 1000 == 0:
            current_memory = process.memory_info().rss / 1024 / 1024
            logging.info(f"内存任务 {task_id} 进度: {i}/{data_size}, 内存使用: {current_memory:.2f}MB")
            
            # 如果内存使用过高，进行清理
            if current_memory > start_memory + 100:  # 超过100MB
                logging.warning(f"内存使用过高，进行清理: {current_memory:.2f}MB")
                # 清理部分数据
                if len(large_data) > 1000:
                    large_data = large_data[-500:]  # 只保留最近500条
                
                # 强制垃圾回收
                import gc
                gc.collect()
                time.sleep(1)
    
    # 处理数据
    result_count = len(large_data)
    
    # 清理内存
    large_data.clear()
    import gc
    gc.collect()
    
    end_memory = process.memory_info().rss / 1024 / 1024
    
    logging.info(f"内存任务 {task_id} 完成，处理了 {result_count} 条记录，内存使用: {start_memory:.2f}MB -> {end_memory:.2f}MB")
    return {"task_id": task_id, "processed_count": result_count, "memory_usage": end_memory - start_memory}

def database_task(task_id: int, query_count: int = 10):
    """数据库任务"""
    logging.info(f"数据库任务 {task_id} 开始执行")
    
    results = []
    
    for i in range(query_count):
        # 模拟数据库查询
        query_start = time.time()
        
        try:
            # 模拟查询执行时间
            query_time = random.uniform(0.1, 0.5)
            time.sleep(query_time)
            
            # 模拟结果
            result = {
                'query_id': i,
                'execution_time': query_time,
                'rows_affected': random.randint(10, 1000),
                'status': 'success'
            }
            results.append(result)
            
            logging.info(f"数据库任务 {task_id} 查询 {i} 完成，耗时: {query_time:.3f}s")
            
        except Exception as e:
            logging.error(f"数据库任务 {task_id} 查询 {i} 失败: {e}")
            results.append({
                'query_id': i,
                'status': 'failed',
                'error': str(e)
            })
    
    total_time = sum(r.get('execution_time', 0) for r in results if r.get('status') == 'success')
    logging.info(f"数据库任务 {task_id} 完成，总查询时间: {total_time:.3f}s")
    return {"task_id": task_id, "total_query_time": total_time, "results": results}

def monitor_system_resources(**context):
    """监控系统资源"""
    logging.info("开始监控系统资源")
    
    # 获取系统信息
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # 获取进程信息
    process = psutil.Process()
    process_memory = process.memory_info()
    
    resource_info = {
        'timestamp': datetime.now().isoformat(),
        'cpu': {
            'percent': cpu_percent,
            'count': psutil.cpu_count(),
            'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        },
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used,
            'process_rss': process_memory.rss,
            'process_vms': process_memory.vms
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': (disk.used / disk.total) * 100
        },
        'process': {
            'pid': process.pid,
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent()
        }
    }
    
    # 检查资源告警
    alerts = []
    
    if cpu_percent > 80:
        alerts.append(f"CPU使用率过高: {cpu_percent}%")
    
    if memory.percent > 85:
        alerts.append(f"内存使用率过高: {memory.percent}%")
    
    if disk.free < 1024 * 1024 * 1024:  # 小于1GB
        alerts.append(f"磁盘空间不足: {disk.free / 1024 / 1024:.2f}MB")
    
    resource_info['alerts'] = alerts
    
    if alerts:
        logging.warning(f"资源告警: {alerts}")
    
    logging.info(f"系统资源监控完成: CPU {cpu_percent}%, 内存 {memory.percent}%")
    return resource_info

def analyze_concurrency_performance(**context):
    """分析并发性能"""
    logging.info("开始分析并发性能")
    
    # 收集所有任务的结果
    task_results = {}
    
    # CPU任务结果
    cpu_results = []
    for i in range(1, 5):  # 4个CPU任务
        try:
            result = context['task_instance'].xcom_pull(
                task_ids=f'cpu_intensive_tasks.cpu_task_{i}'
            )
            if result:
                cpu_results.append(result)
        except Exception as e:
            logging.error(f"获取CPU任务 {i} 结果失败: {e}")
    
    # IO任务结果
    io_results = []
    for i in range(1, 7):  # 6个IO任务
        try:
            result = context['task_instance'].xcom_pull(
                task_ids=f'io_intensive_tasks.io_task_{i}'
            )
            if result:
                io_results.append(result)
        except Exception as e:
            logging.error(f"获取IO任务 {i} 结果失败: {e}")
    
    # 内存任务结果
    memory_results = []
    for i in range(1, 3):  # 2个内存任务
        try:
            result = context['task_instance'].xcom_pull(
                task_ids=f'memory_intensive_tasks.memory_task_{i}'
            )
            if result:
                memory_results.append(result)
        except Exception as e:
            logging.error(f"获取内存任务 {i} 结果失败: {e}")
    
    # 数据库任务结果
    db_results = []
    for i in range(1, 4):  # 3个数据库任务
        try:
            result = context['task_instance'].xcom_pull(
                task_ids=f'database_tasks.db_task_{i}'
            )
            if result:
                db_results.append(result)
        except Exception as e:
            logging.error(f"获取数据库任务 {i} 结果失败: {e}")
    
    # 系统资源监控结果
    resource_info = context['task_instance'].xcom_pull(
        task_ids='system_resource_monitor'
    )
    
    # 生成分析报告
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'cpu_tasks_completed': len(cpu_results),
            'io_tasks_completed': len(io_results),
            'memory_tasks_completed': len(memory_results),
            'database_tasks_completed': len(db_results),
            'total_tasks': len(cpu_results) + len(io_results) + len(memory_results) + len(db_results)
        },
        'performance': {
            'cpu_tasks': cpu_results,
            'io_tasks': io_results,
            'memory_tasks': memory_results,
            'database_tasks': db_results
        },
        'resource_usage': resource_info,
        'recommendations': generate_concurrency_recommendations(
            cpu_results, io_results, memory_results, db_results, resource_info
        )
    }
    
    # 保存分析报告
    with open('/tmp/concurrency_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    logging.info(f"并发性能分析完成，处理了 {analysis['summary']['total_tasks']} 个任务")
    return analysis

def generate_concurrency_recommendations(cpu_results, io_results, memory_results, db_results, resource_info):
    """生成并发优化建议"""
    recommendations = []
    
    # 基于资源使用情况生成建议
    if resource_info:
        if resource_info['cpu']['percent'] > 80:
            recommendations.append("CPU使用率较高，考虑减少CPU密集型任务的并发度")
        
        if resource_info['memory']['percent'] > 85:
            recommendations.append("内存使用率较高，考虑增加内存或优化内存使用")
        
        if resource_info['disk']['percent'] > 90:
            recommendations.append("磁盘使用率较高，考虑清理临时文件或扩展存储")
    
    # 基于任务完成情况生成建议
    if len(cpu_results) < 4:
        recommendations.append("部分CPU任务未完成，检查资源池配置")
    
    if len(io_results) < 6:
        recommendations.append("部分IO任务未完成，检查磁盘空间和IO性能")
    
    if len(memory_results) < 2:
        recommendations.append("部分内存任务未完成，检查内存配置")
    
    if len(db_results) < 3:
        recommendations.append("部分数据库任务未完成，检查数据库连接配置")
    
    # 通用建议
    recommendations.extend([
        "根据实际负载调整资源池大小",
        "监控任务执行时间，识别性能瓶颈",
        "使用任务优先级管理重要任务",
        "定期清理临时文件和日志",
        "考虑使用动态资源分配策略"
    ])
    
    return recommendations

# 定义任务
with dag:
    
    # 设置资源池
    setup_pools_task = PythonOperator(
        task_id='setup_resource_pools',
        python_callable=setup_resource_pools,
        dag=dag,
    )
    
    # 系统资源监控
    monitor_task = PythonOperator(
        task_id='system_resource_monitor',
        python_callable=monitor_system_resources,
        dag=dag,
    )
    
    # CPU密集型任务组
    with TaskGroup("cpu_intensive_tasks", dag=dag) as cpu_tasks:
        for i in range(1, 5):
            PythonOperator(
                task_id=f'cpu_task_{i}',
                python_callable=cpu_intensive_task,
                op_kwargs={'task_id': i, 'duration': random.randint(5, 15)},
                pool='cpu_intensive_pool',  # 使用CPU资源池
                dag=dag,
            )
    
    # IO密集型任务组
    with TaskGroup("io_intensive_tasks", dag=dag) as io_tasks:
        for i in range(1, 7):
            PythonOperator(
                task_id=f'io_task_{i}',
                python_callable=io_intensive_task,
                op_kwargs={'task_id': i, 'file_count': random.randint(3, 8)},
                pool='io_intensive_pool',  # 使用IO资源池
                dag=dag,
            )
    
    # 内存密集型任务组
    with TaskGroup("memory_intensive_tasks", dag=dag) as memory_tasks:
        for i in range(1, 3):
            PythonOperator(
                task_id=f'memory_task_{i}',
                python_callable=memory_intensive_task,
                op_kwargs={'task_id': i, 'data_size': random.randint(5000, 15000)},
                pool='memory_intensive_pool',  # 使用内存资源池
                dag=dag,
            )
    
    # 数据库任务组
    with TaskGroup("database_tasks", dag=dag) as db_tasks:
        for i in range(1, 4):
            PythonOperator(
                task_id=f'db_task_{i}',
                python_callable=database_task,
                op_kwargs={'task_id': i, 'query_count': random.randint(5, 15)},
                pool='database_pool',  # 使用数据库资源池
                dag=dag,
            )
    
    # 并发性能分析
    analysis_task = PythonOperator(
        task_id='concurrency_performance_analysis',
        python_callable=analyze_concurrency_performance,
        dag=dag,
    )
    
    # 设置任务依赖
    setup_pools_task >> [cpu_tasks, io_tasks, memory_tasks, db_tasks] >> monitor_task >> analysis_task