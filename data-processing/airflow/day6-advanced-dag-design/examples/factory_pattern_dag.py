"""
Day 6: 高级DAG设计 - 工厂模式DAG示例

这个示例展示了如何使用工厂模式创建可重用的DAG组件。
工厂模式可以帮助我们创建标准化的DAG模板，提高代码的可维护性和可重用性。
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional


def create_data_processing_task(
    dag: DAG,
    task_id: str,
    processing_function: Callable,
    dependencies: Optional[List[str]] = None
) -> PythonOperator:
    """
    创建数据处理任务的工厂函数
    
    Args:
        dag: DAG对象
        task_id: 任务ID
        processing_function: 处理函数
        dependencies: 依赖的任务ID列表
        
    Returns:
        PythonOperator: 创建的任务对象
    """
    def task_wrapper(**kwargs):
        """任务包装器，添加日志和错误处理"""
        try:
            print(f"开始执行任务: {task_id}")
            result = processing_function(**kwargs)
            print(f"任务 {task_id} 执行成功")
            return result
        except Exception as e:
            print(f"任务 {task_id} 执行失败: {str(e)}")
            raise
    
    return PythonOperator(
        task_id=task_id,
        python_callable=task_wrapper,
        dag=dag,
        provide_context=True
    )


def create_branching_task(
    dag: DAG,
    task_id: str,
    branch_function: Callable,
    branch_targets: Dict[str, str]
) -> PythonOperator:
    """
    创建分支任务的工厂函数
    
    Args:
        dag: DAG对象
        task_id: 任务ID
        branch_function: 分支判断函数
        branch_targets: 分支目标映射
        
    Returns:
        PythonOperator: 创建的分支任务
    """
    def branching_wrapper(**kwargs):
        """分支包装器"""
        condition = branch_function(**kwargs)
        target_task = branch_targets.get(condition, 'default')
        print(f"分支条件: {condition}, 目标任务: {target_task}")
        return target_task
    
    return PythonOperator(
        task_id=task_id,
        python_callable=branching_wrapper,
        dag=dag,
        provide_context=True
    )


# 数据处理函数定义
def extract_data():
    """数据提取函数"""
    print("提取数据...")
    return {"data": [1, 2, 3, 4, 5], "source": "database"}


def transform_data(**kwargs):
    """数据转换函数"""
    ti = kwargs['ti']
    extracted_data = ti.xcom_pull(task_ids='extract_data')
    
    print(f"转换数据: {extracted_data}")
    transformed = [x * 2 for x in extracted_data["data"]]
    return {"transformed_data": transformed, "original_source": extracted_data["source"]}


def load_data(**kwargs):
    """数据加载函数"""
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_data')
    
    print(f"加载数据到目标系统: {transformed_data}")
    return {"status": "success", "records_processed": len(transformed_data["transformed_data"])}


def validate_data(**kwargs):
    """数据验证函数"""
    ti = kwargs['ti']
    loaded_data = ti.xcom_pull(task_ids='load_data')
    
    print(f"验证数据质量: {loaded_data}")
    return {"validation_passed": True, "quality_score": 95}


# 分支判断函数
def determine_processing_path(**kwargs):
    """决定数据处理路径"""
    ti = kwargs['ti']
    extracted_data = ti.xcom_pull(task_ids='extract_data')
    
    data_size = len(extracted_data["data"])
    
    if data_size > 100:
        return "batch_processing"
    elif data_size > 10:
        return "standard_processing"
    else:
        return "quick_processing"


# 创建DAG
def create_factory_pattern_dag():
    """创建工厂模式DAG"""
    
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
        'factory_pattern_dag',
        default_args=default_args,
        description='使用工厂模式创建的DAG示例',
        schedule_interval=timedelta(days=1),
        catchup=False,
        tags=['advanced', 'factory-pattern']
    )
    
    # 使用工厂函数创建任务
    extract_task = create_data_processing_task(
        dag, 'extract_data', extract_data
    )
    
    transform_task = create_data_processing_task(
        dag, 'transform_data', transform_data
    )
    
    load_task = create_data_processing_task(
        dag, 'load_data', load_data
    )
    
    validate_task = create_data_processing_task(
        dag, 'validate_data', validate_data
    )
    
    # 创建分支任务
    branch_task = create_branching_task(
        dag,
        'determine_processing_path',
        determine_processing_path,
        {
            'batch_processing': 'batch_transform',
            'standard_processing': 'transform_data', 
            'quick_processing': 'quick_transform'
        }
    )
    
    # 创建其他处理路径的任务
    batch_transform_task = create_data_processing_task(
        dag, 'batch_transform', lambda **kwargs: print("批量处理数据")
    )
    
    quick_transform_task = create_data_processing_task(
        dag, 'quick_transform', lambda **kwargs: print("快速处理数据")
    )
    
    # 设置任务依赖关系
    extract_task >> branch_task
    
    # 根据分支结果设置不同的依赖路径
    branch_task >> transform_task
    branch_task >> batch_transform_task  
    branch_task >> quick_transform_task
    
    transform_task >> load_task
    batch_transform_task >> load_task
    quick_transform_task >> load_task
    
    load_task >> validate_task
    
    return dag


# 创建DAG实例
factory_dag = create_factory_pattern_dag()


# 测试函数
def test_factory_pattern():
    """测试工厂模式DAG"""
    dag = create_factory_pattern_dag()
    
    print("DAG任务列表:")
    for task in dag.tasks:
        print(f"- {task.task_id}")
    
    print("\nDAG依赖关系:")
    for task in dag.tasks:
        downstream_tasks = task.downstream_list
        if downstream_tasks:
            print(f"{task.task_id} -> {[t.task_id for t in downstream_tasks]}")


if __name__ == "__main__":
    test_factory_pattern()