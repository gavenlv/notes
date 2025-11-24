"""
Airflow 资源管理优化示例代码
展示如何优化 Airflow 中的内存和 CPU 使用
"""

import psutil
import time
import gc
from datetime import datetime, timedelta
from functools import wraps
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable


# 内存监控装饰器
def monitor_memory(func):
    """
    装饰器：监控函数执行过程中的内存使用情况
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取执行前的内存使用情况
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        print(f"执行前内存使用: {mem_before:.2f} MB")
        
        # 执行函数
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # 获取执行后的内存使用情况
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_diff = mem_after - mem_before
        
        print(f"执行后内存使用: {mem_after:.2f} MB")
        print(f"内存变化: {mem_diff:+.2f} MB")
        print(f"执行时间: {execution_time:.4f} 秒")
        
        return result
    return wrapper


# 内存优化任务示例
@monitor_memory
def memory_intensive_task(**context):
    """
    模拟内存密集型任务，并展示优化技巧
    """
    print("开始执行内存密集型任务...")
    
    # 1. 避免创建不必要的大型数据结构
    # 不好的做法：
    # large_list = [i for i in range(10000000)]  # 创建大型列表
    
    # 优化做法：使用生成器
    def data_generator():
        for i in range(10000000):
            yield i * 2
    
    # 2. 及时释放不需要的变量
    temp_data = list(range(100000))
    # 处理数据...
    processed_data = [x * 2 for x in temp_data[:1000]]  # 只处理前1000个元素
    
    # 显式删除不需要的变量
    del temp_data
    gc.collect()  # 强制垃圾回收
    
    # 3. 使用适当的数据类型
    # 不好的做法：
    # status_list = ['active', 'inactive', 'pending'] * 1000000
    
    # 优化做法：使用枚举或整数
    STATUS_MAP = {'active': 1, 'inactive': 0, 'pending': 2}
    status_codes = [1, 0, 2] * 1000000  # 使用整数而不是字符串
    
    # 4. 分批处理大数据集
    batch_size = 10000
    total_items = 1000000
    
    for i in range(0, total_items, batch_size):
        batch = list(range(i, min(i + batch_size, total_items)))
        # 处理批次数据
        processed_batch = [x ** 2 for x in batch]
        # 处理完成后立即释放
        del processed_batch
    
    print(f"内存密集型任务完成，处理了 {total_items} 个项目")
    return processed_data


# CPU 优化任务示例
@monitor_memory
def cpu_intensive_task(**context):
    """
    模拟 CPU 密集型任务，并展示优化技巧
    """
    print("开始执行 CPU 密集型任务...")
    
    # 1. 使用内置函数和库优化
    # 不好的做法：
    # result = []
    # for i in range(1000000):
    #     result.append(i ** 2)
    
    # 优化做法：使用列表推导式和内置函数
    numbers = range(1000000)
    squares = [x ** 2 for x in numbers]
    
    # 2. 避免重复计算
    cache = {}
    
    def expensive_calculation(n):
        if n in cache:
            return cache[n]
        
        # 模拟复杂计算
        result = sum(i ** 2 for i in range(n))
        cache[n] = result
        return result
    
    # 3. 使用适当的数据结构
    # 对于频繁查找操作，使用 set 或 dict 而不是 list
    lookup_data = set(range(100000))  # O(1) 查找时间
    
    # 4. 并行处理（如果适用）
    import concurrent.futures
    
    def worker(n):
        return sum(i ** 2 for i in range(n, n + 1000))
    
    # 使用线程池处理并行任务
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(worker, i) for i in range(0, 10000, 1000)]
        results = [future.result() for future in futures]
    
    print(f"CPU 密集型任务完成，计算结果数量: {len(results)}")
    return results


# 资源限制任务示例
def resource_limited_task(**context):
    """
    展示如何在 Airflow 中限制任务资源使用
    """
    print("开始执行资源受限任务...")
    
    # 1. 从 Airflow Variables 获取资源限制配置
    try:
        max_memory_mb = int(Variable.get("max_task_memory_mb", default_var=512))
        max_execution_time = int(Variable.get("max_task_execution_seconds", default_var=300))
    except Exception as e:
        print(f"获取资源限制配置失败，使用默认值: {e}")
        max_memory_mb = 512
        max_execution_time = 300
    
    print(f"资源限制 - 最大内存: {max_memory_mb} MB, 最大执行时间: {max_execution_time} 秒")
    
    # 2. 监控资源使用并在超出限制时采取措施
    start_time = time.time()
    process = psutil.Process()
    
    # 模拟任务执行
    data = []
    for i in range(100000):
        data.append(i ** 2)
        
        # 定期检查资源使用情况
        if i % 10000 == 0:
            current_time = time.time()
            elapsed_time = current_time - start_time
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"进度 {i/100000*100:.1f}% - 内存使用: {current_memory:.2f} MB, 已用时间: {elapsed_time:.2f} 秒")
            
            # 检查是否超出资源限制
            if current_memory > max_memory_mb:
                print(f"警告: 内存使用 {current_memory:.2f} MB 超出限制 {max_memory_mb} MB")
                # 可以采取措施如清理数据、减小处理规模等
                del data[-5000:]  # 清理部分数据
                
            if elapsed_time > max_execution_time:
                print(f"警告: 执行时间 {elapsed_time:.2f} 秒超出限制 {max_execution_time} 秒")
                break
    
    print("资源受限任务完成")
    return len(data)


# 动态资源分配示例
def dynamic_resource_allocation(**context):
    """
    根据任务复杂度动态调整资源分配
    """
    print("开始执行动态资源分配任务...")
    
    # 从上下文获取任务信息
    dag_id = context['dag_run'].dag_id
    task_id = context['task_instance'].task_id
    execution_date = context['execution_date']
    
    print(f"任务信息 - DAG: {dag_id}, Task: {task_id}, Execution Date: {execution_date}")
    
    # 根据任务类型或历史数据决定资源分配
    task_complexity = "medium"  # 这里可以基于业务逻辑动态确定
    
    # 定义不同复杂度的资源配置
    resource_configs = {
        "low": {
            "memory_mb": 256,
            "cpu_cores": 1,
            "timeout_seconds": 60
        },
        "medium": {
            "memory_mb": 512,
            "cpu_cores": 2,
            "timeout_seconds": 180
        },
        "high": {
            "memory_mb": 1024,
            "cpu_cores": 4,
            "timeout_seconds": 600
        }
    }
    
    config = resource_configs.get(task_complexity, resource_configs["medium"])
    print(f"使用资源配置: {config}")
    
    # 应用资源配置（在实际环境中可能需要与执行器或容器平台集成）
    # 这里仅演示配置信息的获取和使用
    
    # 执行任务逻辑
    result_size = 0
    batch_size = config["memory_mb"] * 100  # 简单示例：根据内存配置调整批处理大小
    
    for i in range(0, 100000, batch_size):
        batch = list(range(i, min(i + batch_size, 100000)))
        processed_batch = [x ** 2 for x in batch]
        result_size += len(processed_batch)
        del processed_batch  # 及时释放内存
        
        # 模拟处理时间
        time.sleep(0.01)
    
    print(f"动态资源分配任务完成，处理了 {result_size} 个项目")
    return result_size


# 创建资源管理优化 DAG
def create_resource_optimization_dag():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        'resource_management_optimization',
        default_args=default_args,
        description='Airflow 资源管理优化演示',
        schedule_interval=timedelta(days=1),
        catchup=False,
        max_active_runs=1,
    )

    # 内存优化任务
    memory_task = PythonOperator(
        task_id='memory_optimization_task',
        python_callable=memory_intensive_task,
        dag=dag,
    )

    # CPU 优化任务
    cpu_task = PythonOperator(
        task_id='cpu_optimization_task',
        python_callable=cpu_intensive_task,
        dag=dag,
    )

    # 资源限制任务
    resource_task = PythonOperator(
        task_id='resource_limited_task',
        python_callable=resource_limited_task,
        dag=dag,
    )

    # 动态资源分配任务
    dynamic_task = PythonOperator(
        task_id='dynamic_resource_allocation',
        python_callable=dynamic_resource_allocation,
        dag=dag,
    )

    # 设置任务依赖关系
    memory_task >> cpu_task >> resource_task >> dynamic_task

    return dag


# 资源使用报告生成函数
def generate_resource_report(**context):
    """
    生成资源使用报告
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    cpu_percent = process.cpu_percent()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "memory_rss_mb": memory_info.rss / 1024 / 1024,
        "memory_vms_mb": memory_info.vms / 1024 / 1024,
        "cpu_percent": cpu_percent,
        "num_threads": process.num_threads(),
        "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 'N/A'
    }
    
    print("资源使用报告:")
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    return report


# 系统资源监控函数
def system_resource_monitor(**context):
    """
    监控系统整体资源使用情况
    """
    # CPU 使用情况
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 内存使用情况
    memory = psutil.virtual_memory()
    
    # 磁盘使用情况
    disk = psutil.disk_usage('/')
    
    print("系统资源监控:")
    print(f"  CPU 使用率: {cpu_percent}%")
    print(f"  内存使用率: {memory.percent}%")
    print(f"  可用内存: {memory.available / 1024 / 1024 / 1024:.2f} GB")
    print(f"  磁盘使用率: {disk.percent}%")
    print(f"  可用磁盘空间: {disk.free / 1024 / 1024 / 1024:.2f} GB")
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent
    }


# 主函数
if __name__ == '__main__':
    print("Airflow Resource Management Optimization Examples")
    print("=" * 50)
    
    # 演示内存监控装饰器
    print("1. 内存密集型任务演示:")
    memory_intensive_task()
    
    print("\n2. CPU 密集型任务演示:")
    cpu_intensive_task()
    
    print("\n资源管理优化示例创建完成!")
    print("主要包括:")
    print("- 内存使用监控和优化")
    print("- CPU 使用优化")
    print("- 资源限制管理")
    print("- 动态资源分配")