"""
Airflow任务流性能优化示例
包含多种性能优化策略和最佳实践
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.hooks.base import BaseHook
import time
import random
import psutil
import gc
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from typing import List, Dict, Any

# 性能监控装饰器
def performance_monitor(func_name: str):
    """性能监控装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                execution_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                logging.info(f"[{func_name}] 执行时间: {execution_time:.2f}s, 内存使用: {memory_used:.2f}MB")
                
                return result
            except Exception as e:
                logging.error(f"[{func_name}] 执行失败: {str(e)}")
                raise
        
        return wrapper
    return decorator

# 默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1,  # 限制并发运行实例
}

# 性能优化DAG
dag = DAG(
    'performance_optimization_demo',
    default_args=default_args,
    description='任务流性能优化示例',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    max_active_tasks=10,  # DAG级别的并发限制
    tags=['performance', 'optimization'],
)

# 1. 批量处理优化示例
@performance_monitor("batch_processor")
def batch_process_data(**context):
    """批量数据处理优化"""
    # 获取批量大小配置
    batch_size = Variable.get("batch_size", default_var=1000)
    
    # 模拟大数据集
    total_records = 10000
    
    # 使用生成器减少内存占用
    def data_generator():
        for i in range(total_records):
            yield {
                'id': i,
                'value': random.randint(1, 100),
                'timestamp': datetime.now().isoformat()
            }
    
    # 批量处理
    batch_results = []
    batch_count = 0
    
    for record in data_generator():
        batch_results.append(record)
        
        # 当批次满时处理
        if len(batch_results) >= batch_size:
            # 模拟批处理逻辑
            processed_batch = process_batch(batch_results)
            
            # 清理内存
            batch_results.clear()
            gc.collect()
            
            batch_count += 1
            logging.info(f"处理批次 {batch_count}, 大小: {batch_size}")
    
    # 处理剩余数据
    if batch_results:
        process_batch(batch_results)
    
    return {"total_batches": batch_count, "total_records": total_records}

def process_batch(batch_data: List[Dict]) -> List[Dict]:
    """批次数据处理"""
    # 模拟数据处理
    time.sleep(0.01)  # 模拟处理时间
    
    # 返回处理结果
    return [
        {**record, 'processed': True, 'processed_at': datetime.now().isoformat()}
        for record in batch_data
    ]

# 2. 并发处理优化示例
@performance_monitor("concurrent_processor")
def concurrent_process_data(**context):
    """并发数据处理优化"""
    # 获取并发配置
    max_workers = int(Variable.get("max_workers", default_var=4))
    
    # 模拟任务列表
    tasks = list(range(20))
    
    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(process_single_task, task): task 
            for task in tasks
        }
        
        results = []
        # 收集结果
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result(timeout=30)  # 设置超时
                results.append(result)
            except Exception as exc:
                logging.error(f"任务 {task} 处理失败: {exc}")
                raise
    
    return {"total_tasks": len(tasks), "completed": len(results)}

def process_single_task(task_id: int) -> Dict:
    """单个任务处理"""
    # 模拟不同复杂度的任务
    complexity = random.randint(1, 5)
    time.sleep(complexity * 0.1)  # 模拟处理时间
    
    return {
        'task_id': task_id,
        'complexity': complexity,
        'status': 'completed',
        'duration': complexity * 0.1
    }

# 3. 内存优化示例
@performance_monitor("memory_optimizer")
def memory_optimized_processing(**context):
    """内存优化处理"""
    # 配置内存限制
    memory_limit_mb = int(Variable.get("memory_limit_mb", default_var=500))
    
    # 监控内存使用
    process = psutil.Process()
    
    # 模拟大数据处理
    chunk_size = 1000
    total_chunks = 10
    
    results = []
    
    for chunk_id in range(total_chunks):
        # 检查内存使用
        current_memory = process.memory_info().rss / 1024 / 1024
        
        if current_memory > memory_limit_mb:
            logging.warning(f"内存使用超过限制: {current_memory:.2f}MB > {memory_limit_mb}MB")
            # 执行垃圾回收
            gc.collect()
            time.sleep(1)  # 给系统时间清理内存
        
        # 处理数据块
        chunk_data = generate_chunk_data(chunk_size)
        processed_chunk = process_chunk(chunk_data)
        
        # 只保留必要的结果，减少内存占用
        results.append({
            'chunk_id': chunk_id,
            'record_count': len(processed_chunk),
            'summary': summarize_chunk(processed_chunk)
        })
        
        # 清理临时数据
        del chunk_data, processed_chunk
        
        # 定期执行垃圾回收
        if chunk_id % 3 == 0:
            gc.collect()
    
    return {
        "total_chunks": total_chunks,
        "memory_usage": f"{process.memory_info().rss / 1024 / 1024:.2f}MB",
        "results": results
    }

def generate_chunk_data(size: int) -> pd.DataFrame:
    """生成数据块"""
    return pd.DataFrame({
        'id': range(size),
        'value': [random.randint(1, 100) for _ in range(size)],
        'category': [random.choice(['A', 'B', 'C']) for _ in range(size)]
    })

def process_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """处理数据块"""
    # 模拟数据处理
    df['processed_value'] = df['value'] * 2
    df['processed_category'] = df['category'] + '_processed'
    return df

def summarize_chunk(df: pd.DataFrame) -> Dict:
    """数据块摘要"""
    return {
        'avg_value': df['value'].mean(),
        'category_counts': df['category'].value_counts().to_dict(),
        'record_count': len(df)
    }

# 4. 数据库连接优化示例
@performance_monitor("db_connection_optimizer")
def database_connection_optimization(**context):
    """数据库连接优化"""
    # 使用连接池和批量操作
    
    # 模拟数据库操作
    connection_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_pass'
    }
    
    # 批量插入数据
    batch_size = 500
    total_records = 2000
    
    # 使用批量操作减少数据库往返
    for batch_start in range(0, total_records, batch_size):
        batch_end = min(batch_start + batch_size, total_records)
        
        # 模拟批量数据准备
        batch_data = [
            {
                'id': i,
                'data': f'record_{i}',
                'timestamp': datetime.now().isoformat()
            }
            for i in range(batch_start, batch_end)
        ]
        
        # 模拟批量插入
        batch_insert(batch_data)
        
        logging.info(f"批量插入: {batch_start}-{batch_end}/{total_records}")
    
    return {
        "total_records": total_records,
        "batch_size": batch_size,
        "batches": total_records // batch_size
    }

def batch_insert(data: List[Dict]) -> None:
    """批量插入数据"""
    # 模拟数据库批量插入
    time.sleep(0.05)  # 模拟插入时间
    
    # 实际应用中应该使用真正的批量插入语句
    # 例如: INSERT INTO table (col1, col2) VALUES (%s, %s), (%s, %s), ...

# 5. 缓存优化示例
@performance_monitor("cache_optimizer")
def cache_optimization(**context):
    """缓存优化处理"""
    # 简单的内存缓存实现
    cache = {}
    
    # 模拟需要缓存的计算
    def expensive_computation(key: str) -> str:
        """昂贵的计算"""
        if key in cache:
            logging.info(f"缓存命中: {key}")
            return cache[key]
        
        # 模拟昂贵计算
        time.sleep(0.1)
        result = f"computed_result_for_{key}"
        
        # 缓存结果
        cache[key] = result
        logging.info(f"缓存未命中，计算并缓存: {key}")
        
        return result
    
    # 测试缓存效果
    test_keys = ['key1', 'key2', 'key1', 'key3', 'key2', 'key1']
    
    results = []
    for key in test_keys:
        start_time = time.time()
        result = expensive_computation(key)
        duration = time.time() - start_time
        
        results.append({
            'key': key,
            'duration': duration,
            'cached': key in cache
        })
    
    return {
        "cache_size": len(cache),
        "cache_hit_rate": sum(1 for r in results if r['cached']) / len(results),
        "results": results
    }

# 定义任务
with TaskGroup("performance_tests", dag=dag) as performance_tests:
    
    # 批量处理任务
    batch_task = PythonOperator(
        task_id='batch_processing',
        python_callable=batch_process_data,
        dag=dag,
    )
    
    # 并发处理任务
    concurrent_task = PythonOperator(
        task_id='concurrent_processing',
        python_callable=concurrent_process_data,
        dag=dag,
    )
    
    # 内存优化任务
    memory_task = PythonOperator(
        task_id='memory_optimization',
        python_callable=memory_optimized_processing,
        dag=dag,
    )
    
    # 数据库优化任务
    db_task = PythonOperator(
        task_id='database_optimization',
        python_callable=database_connection_optimization,
        dag=dag,
    )
    
    # 缓存优化任务
    cache_task = PythonOperator(
        task_id='cache_optimization',
        python_callable=cache_optimization,
        dag=dag,
    )

# 性能汇总任务
def performance_summary(**context):
    """性能汇总"""
    # 收集所有任务的结果
    task_results = {}
    
    task_ids = [
        'performance_tests.batch_processing',
        'performance_tests.concurrent_processing',
        'performance_tests.memory_optimization',
        'performance_tests.database_optimization',
        'performance_tests.cache_optimization'
    ]
    
    for task_id in task_ids:
        try:
            result = context['task_instance'].xcom_pull(task_ids=task_id)
            task_results[task_id.split('.')[-1]] = result
        except Exception as e:
            logging.error(f"获取任务 {task_id} 结果失败: {e}")
    
    # 生成性能报告
    summary = {
        "timestamp": datetime.now().isoformat(),
        "optimization_techniques": list(task_results.keys()),
        "results": task_results,
        "recommendations": generate_performance_recommendations(task_results)
    }
    
    # 保存性能报告
    with open('/tmp/performance_report.json', 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logging.info("性能优化测试完成，报告已保存到 /tmp/performance_report.json")
    return summary

def generate_performance_recommendations(results: Dict) -> List[str]:
    """生成性能优化建议"""
    recommendations = []
    
    # 基于结果生成建议
    if 'batch_processing' in results:
        batch_result = results['batch_processing']
        if batch_result.get('total_batches', 0) > 100:
            recommendations.append("考虑增加批处理大小以提高效率")
    
    if 'memory_optimization' in results:
        memory_result = results['memory_optimization']
        if 'memory_usage' in memory_result:
            memory_usage = float(memory_result['memory_usage'].replace('MB', ''))
            if memory_usage > 400:
                recommendations.append("内存使用较高，考虑进一步优化数据结构和算法")
    
    recommendations.extend([
        "定期监控性能指标",
        "根据实际负载调整并发参数",
        "使用连接池管理数据库连接",
        "实现适当的缓存策略",
        "定期清理临时文件和日志"
    ])
    
    return recommendations

# 汇总任务
summary_task = PythonOperator(
    task_id='performance_summary',
    python_callable=performance_summary,
    dag=dag,
)

# 设置任务依赖
performance_tests >> summary_task