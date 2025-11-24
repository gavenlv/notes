"""
Day 6: 高级DAG设计 - 条件分支与并行执行示例

这个示例展示了如何使用条件分支和并行执行来构建复杂的工作流。
条件分支允许根据运行时条件选择不同的执行路径，并行执行可以提高处理效率。
"""

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random


def create_branching_parallel_dag() -> DAG:
    """创建条件分支与并行执行的DAG"""
    
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
        'branching_parallel_workflow',
        default_args=default_args,
        description='条件分支与并行执行的高级工作流示例',
        schedule_interval=timedelta(hours=1),
        catchup=False,
        tags=['branching', 'parallel', 'advanced']
    )
    
    with dag:
        # 开始任务
        start = DummyOperator(
            task_id='start'
        )
        
        # 数据质量检查任务
        check_data_quality = PythonOperator(
            task_id='check_data_quality',
            python_callable=lambda **kwargs: {
                'quality_score': random.randint(80, 100),
                'data_size': random.randint(100, 10000),
                'source_system': random.choice(['production', 'staging', 'backup'])
            }
        )
        
        # 分支决策任务 - 根据数据质量选择处理路径
        decide_processing_path = BranchPythonOperator(
            task_id='decide_processing_path',
            python_callable=_decide_processing_path
        )
        
        # 不同处理路径的任务
        high_quality_processing = PythonOperator(
            task_id='high_quality_processing',
            python_callable=_high_quality_processing
        )
        
        medium_quality_processing = PythonOperator(
            task_id='medium_quality_processing',
            python_callable=_medium_quality_processing
        )
        
        low_quality_processing = PythonOperator(
            task_id='low_quality_processing',
            python_callable=_low_quality_processing
        )
        
        # 并行数据提取任务
        extract_user_data = PythonOperator(
            task_id='extract_user_data',
            python_callable=_extract_user_data
        )
        
        extract_product_data = PythonOperator(
            task_id='extract_product_data',
            python_callable=_extract_product_data
        )
        
        extract_order_data = PythonOperator(
            task_id='extract_order_data',
            python_callable=_extract_order_data
        )
        
        # 数据合并任务
        merge_extracted_data = PythonOperator(
            task_id='merge_extracted_data',
            python_callable=_merge_extracted_data,
            trigger_rule=TriggerRule.ALL_SUCCESS
        )
        
        # 条件分支：根据数据量选择处理策略
        decide_parallel_strategy = BranchPythonOperator(
            task_id='decide_parallel_strategy',
            python_callable=_decide_parallel_strategy
        )
        
        # 不同并行策略的任务
        single_thread_processing = PythonOperator(
            task_id='single_thread_processing',
            python_callable=_single_thread_processing
        )
        
        multi_thread_processing = PythonOperator(
            task_id='multi_thread_processing',
            python_callable=_multi_thread_processing
        )
        
        distributed_processing = PythonOperator(
            task_id='distributed_processing',
            python_callable=_distributed_processing
        )
        
        # 并行处理任务（多个相同类型的任务）
        parallel_tasks = []
        for i in range(5):
            task = PythonOperator(
                task_id=f'parallel_data_chunk_{i}',
                python_callable=_process_data_chunk,
                op_kwargs={'chunk_id': i},
                trigger_rule=TriggerRule.ALL_SUCCESS
            )
            parallel_tasks.append(task)
        
        # 合并并行处理结果
        merge_parallel_results = PythonOperator(
            task_id='merge_parallel_results',
            python_callable=_merge_parallel_results,
            trigger_rule=TriggerRule.ALL_SUCCESS
        )
        
        # 错误处理分支
        decide_error_handling = BranchPythonOperator(
            task_id='decide_error_handling',
            python_callable=_decide_error_handling
        )
        
        # 错误处理路径
        retry_processing = PythonOperator(
            task_id='retry_processing',
            python_callable=_retry_processing
        )
        
        skip_processing = PythonOperator(
            task_id='skip_processing',
            python_callable=_skip_processing
        )
        
        notify_administrator = PythonOperator(
            task_id='notify_administrator',
            python_callable=_notify_administrator
        )
        
        # 最终合并任务
        final_merge = PythonOperator(
            task_id='final_merge',
            python_callable=_final_merge,
            trigger_rule=TriggerRule.ONE_SUCCESS  # 只要有一个路径成功就继续
        )
        
        # 结束任务
        end = DummyOperator(
            task_id='end',
            trigger_rule=TriggerRule.ALL_SUCCESS
        )
        
        # 设置任务依赖关系
        
        # 第一层：数据质量检查
        start >> check_data_quality >> decide_processing_path
        
        # 第二层：根据质量选择处理路径
        decide_processing_path >> [high_quality_processing, medium_quality_processing, low_quality_processing]
        
        # 第三层：并行数据提取
        [high_quality_processing, medium_quality_processing, low_quality_processing] >> [extract_user_data, extract_product_data, extract_order_data]
        
        # 第四层：数据合并
        [extract_user_data, extract_product_data, extract_order_data] >> merge_extracted_data
        
        # 第五层：根据数据量选择并行策略
        merge_extracted_data >> decide_parallel_strategy
        decide_parallel_strategy >> [single_thread_processing, multi_thread_processing, distributed_processing]
        
        # 第六层：并行处理
        [single_thread_processing, multi_thread_processing, distributed_processing] >> parallel_tasks
        
        # 第七层：合并并行结果
        parallel_tasks >> merge_parallel_results
        
        # 第八层：错误处理决策
        merge_parallel_results >> decide_error_handling
        decide_error_handling >> [retry_processing, skip_processing, notify_administrator]
        
        # 第九层：最终合并
        [retry_processing, skip_processing, notify_administrator] >> final_merge
        
        # 第十层：结束
        final_merge >> end
    
    return dag


# 任务函数定义

def _decide_processing_path(**kwargs) -> str:
    """决定处理路径"""
    ti = kwargs['ti']
    quality_data = ti.xcom_pull(task_ids='check_data_quality')
    
    quality_score = quality_data['quality_score']
    
    if quality_score >= 95:
        return 'high_quality_processing'
    elif quality_score >= 85:
        return 'medium_quality_processing'
    else:
        return 'low_quality_processing'


def _high_quality_processing(**kwargs):
    """高质量数据处理"""
    print("执行高质量数据处理 - 使用高级算法")
    return {"processing_type": "high_quality", "algorithm": "advanced"}


def _medium_quality_processing(**kwargs):
    """中等质量数据处理"""
    print("执行中等质量数据处理 - 使用标准算法")
    return {"processing_type": "medium_quality", "algorithm": "standard"}


def _low_quality_processing(**kwargs):
    """低质量数据处理"""
    print("执行低质量数据处理 - 使用基础算法")
    return {"processing_type": "low_quality", "algorithm": "basic"}


def _extract_user_data(**kwargs):
    """提取用户数据"""
    print("并行提取用户数据")
    return {"data_type": "user", "records": random.randint(1000, 5000)}


def _extract_product_data(**kwargs):
    """提取产品数据"""
    print("并行提取产品数据")
    return {"data_type": "product", "records": random.randint(500, 2000)}


def _extract_order_data(**kwargs):
    """提取订单数据"""
    print("并行提取订单数据")
    return {"data_type": "order", "records": random.randint(2000, 10000)}


def _merge_extracted_data(**kwargs):
    """合并提取的数据"""
    ti = kwargs['ti']
    
    user_data = ti.xcom_pull(task_ids='extract_user_data')
    product_data = ti.xcom_pull(task_ids='extract_product_data')
    order_data = ti.xcom_pull(task_ids='extract_order_data')
    
    total_records = user_data['records'] + product_data['records'] + order_data['records']
    
    print(f"合并数据完成，总记录数: {total_records}")
    return {"total_records": total_records, "merge_time": datetime.now().isoformat()}


def _decide_parallel_strategy(**kwargs) -> str:
    """决定并行处理策略"""
    ti = kwargs['ti']
    merge_data = ti.xcom_pull(task_ids='merge_extracted_data')
    
    total_records = merge_data['total_records']
    
    if total_records <= 1000:
        return 'single_thread_processing'
    elif total_records <= 5000:
        return 'multi_thread_processing'
    else:
        return 'distributed_processing'


def _single_thread_processing(**kwargs):
    """单线程处理"""
    print("使用单线程处理数据")
    return {"strategy": "single_thread", "performance": "low"}


def _multi_thread_processing(**kwargs):
    """多线程处理"""
    print("使用多线程处理数据")
    return {"strategy": "multi_thread", "performance": "medium"}


def _distributed_processing(**kwargs):
    """分布式处理"""
    print("使用分布式处理数据")
    return {"strategy": "distributed", "performance": "high"}


def _process_data_chunk(chunk_id: int, **kwargs):
    """处理数据块"""
    import time
    
    print(f"处理数据块 {chunk_id}")
    time.sleep(1)  # 模拟处理时间
    
    return {"chunk_id": chunk_id, "status": "processed", "processed_at": datetime.now().isoformat()}


def _merge_parallel_results(**kwargs):
    """合并并行处理结果"""
    ti = kwargs['ti']
    
    results = []
    for i in range(5):
        result = ti.xcom_pull(task_ids=f'parallel_data_chunk_{i}')
        if result:
            results.append(result)
    
    print(f"合并 {len(results)} 个并行处理结果")
    return {"total_chunks": len(results), "merge_status": "completed"}


def _decide_error_handling(**kwargs) -> str:
    """决定错误处理策略"""
    # 模拟随机错误情况
    error_scenario = random.choice(['retry', 'skip', 'notify'])
    
    if error_scenario == 'retry':
        return 'retry_processing'
    elif error_scenario == 'skip':
        return 'skip_processing'
    else:
        return 'notify_administrator'


def _retry_processing(**kwargs):
    """重试处理"""
    print("执行重试处理逻辑")
    return {"action": "retry", "attempt": 1, "status": "retrying"}


def _skip_processing(**kwargs):
    """跳过处理"""
    print("跳过当前处理步骤")
    return {"action": "skip", "reason": "non_critical_error"}


def _notify_administrator(**kwargs):
    """通知管理员"""
    print("发送管理员通知")
    return {"action": "notify", "recipient": "admin@company.com", "severity": "high"}


def _final_merge(**kwargs):
    """最终合并"""
    print("执行最终数据合并")
    return {"final_status": "completed", "completion_time": datetime.now().isoformat()}


# 创建DAG实例
branching_parallel_dag = create_branching_parallel_dag()


# 测试函数
def test_branching_parallel_dag():
    """测试条件分支与并行执行DAG"""
    dag = create_branching_parallel_dag()
    
    print("条件分支与并行执行DAG信息:")
    print(f"DAG ID: {dag.dag_id}")
    print(f"任务数量: {len(dag.tasks)}")
    
    print("\n任务类型统计:")
    task_types = {}
    for task in dag.tasks:
        task_type = type(task).__name__
        task_types[task_type] = task_types.get(task_type, 0) + 1
    
    for task_type, count in task_types.items():
        print(f"{task_type}: {count}")
    
    print("\n分支任务:")
    branch_tasks = [task for task in dag.tasks if isinstance(task, BranchPythonOperator)]
    for task in branch_tasks:
        print(f"- {task.task_id}")
    
    print("\n并行任务组:")
    parallel_groups = {}
    for task in dag.tasks:
        if 'parallel_data_chunk' in task.task_id:
            group = task.task_id.split('_')[-1]
            parallel_groups[group] = parallel_groups.get(group, 0) + 1
    
    for group, count in parallel_groups.items():
        print(f"并行组 {group}: {count} 个任务")


if __name__ == "__main__":
    test_branching_parallel_dag()