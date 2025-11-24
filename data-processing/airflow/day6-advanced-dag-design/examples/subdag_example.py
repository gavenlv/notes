"""
Day 6: 高级DAG设计 - 子DAG使用示例

这个示例展示了如何使用子DAG来组织复杂的DAG结构。
子DAG可以帮助我们将大型DAG分解为更小、更可管理的部分。
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.subdag import SubDagOperator
from datetime import datetime, timedelta
from typing import Dict, List, Any


def create_data_extraction_subdag(
    parent_dag_name: str,
    child_dag_name: str,
    args: Dict[str, Any]
) -> DAG:
    """
    创建数据提取子DAG
    
    Args:
        parent_dag_name: 父DAG名称
        child_dag_name: 子DAG名称
        args: 参数字典
        
    Returns:
        DAG: 子DAG对象
    """
    dag_id = f"{parent_dag_name}.{child_dag_name}"
    
    subdag = DAG(
        dag_id=dag_id,
        default_args=args,
        schedule_interval=None,  # 子DAG不应该有自己的调度
        catchup=False,
    )
    
    # 创建子DAG任务
    with subdag:
        start_extraction = DummyOperator(
            task_id='start_extraction',
            dag=subdag
        )
        
        extract_user_data = PythonOperator(
            task_id='extract_user_data',
            python_callable=lambda **kwargs: print("提取用户数据"),
            dag=subdag
        )
        
        extract_order_data = PythonOperator(
            task_id='extract_order_data',
            python_callable=lambda **kwargs: print("提取订单数据"),
            dag=subdag
        )
        
        extract_product_data = PythonOperator(
            task_id='extract_product_data',
            python_callable=lambda **kwargs: print("提取产品数据"),
            dag=subdag
        )
        
        merge_extracted_data = PythonOperator(
            task_id='merge_extracted_data',
            python_callable=lambda **kwargs: print("合并提取的数据"),
            dag=subdag
        )
        
        end_extraction = DummyOperator(
            task_id='end_extraction',
            dag=subdag
        )
        
        # 设置子DAG内部依赖关系
        start_extraction >> [extract_user_data, extract_order_data, extract_product_data]
        [extract_user_data, extract_order_data, extract_product_data] >> merge_extracted_data
        merge_extracted_data >> end_extraction
    
    return subdag


def create_data_processing_subdag(
    parent_dag_name: str,
    child_dag_name: str,
    args: Dict[str, Any]
) -> DAG:
    """
    创建数据处理子DAG
    
    Args:
        parent_dag_name: 父DAG名称
        child_dag_name: 子DAG名称
        args: 参数字典
        
    Returns:
        DAG: 子DAG对象
    """
    dag_id = f"{parent_dag_name}.{child_dag_name}"
    
    subdag = DAG(
        dag_id=dag_id,
        default_args=args,
        schedule_interval=None,
        catchup=False,
    )
    
    with subdag:
        start_processing = DummyOperator(
            task_id='start_processing',
            dag=subdag
        )
        
        clean_data = PythonOperator(
            task_id='clean_data',
            python_callable=lambda **kwargs: print("数据清洗"),
            dag=subdag
        )
        
        transform_data = PythonOperator(
            task_id='transform_data',
            python_callable=lambda **kwargs: print("数据转换"),
            dag=subdag
        )
        
        enrich_data = PythonOperator(
            task_id='enrich_data',
            python_callable=lambda **kwargs: print("数据增强"),
            dag=subdag
        )
        
        aggregate_data = PythonOperator(
            task_id='aggregate_data',
            python_callable=lambda **kwargs: print("数据聚合"),
            dag=subdag
        )
        
        end_processing = DummyOperator(
            task_id='end_processing',
            dag=subdag
        )
        
        # 设置处理流程依赖
        start_processing >> clean_data >> transform_data
        transform_data >> [enrich_data, aggregate_data]
        [enrich_data, aggregate_data] >> end_processing
    
    return subdag


def create_quality_validation_subdag(
    parent_dag_name: str,
    child_dag_name: str,
    args: Dict[str, Any]
) -> DAG:
    """
    创建质量验证子DAG
    
    Args:
        parent_dag_name: 父DAG名称
        child_dag_name: 子DAG名称
        args: 参数字典
        
    Returns:
        DAG: 子DAG对象
    """
    dag_id = f"{parent_dag_name}.{child_dag_name}"
    
    subdag = DAG(
        dag_id=dag_id,
        default_args=args,
        schedule_interval=None,
        catchup=False,
    )
    
    with subdag:
        start_validation = DummyOperator(
            task_id='start_validation',
            dag=subdag
        )
        
        validate_schema = PythonOperator(
            task_id='validate_schema',
            python_callable=lambda **kwargs: print("验证数据模式"),
            dag=subdag
        )
        
        check_completeness = PythonOperator(
            task_id='check_completeness',
            python_callable=lambda **kwargs: print("检查数据完整性"),
            dag=subdag
        )
        
        verify_accuracy = PythonOperator(
            task_id='verify_accuracy',
            python_callable=lambda **kwargs: print("验证数据准确性"),
            dag=subdag
        )
        
        generate_quality_report = PythonOperator(
            task_id='generate_quality_report',
            python_callable=lambda **kwargs: print("生成质量报告"),
            dag=subdag
        )
        
        end_validation = DummyOperator(
            task_id='end_validation',
            dag=subdag
        )
        
        # 设置验证流程依赖
        start_validation >> [validate_schema, check_completeness, verify_accuracy]
        [validate_schema, check_completeness, verify_accuracy] >> generate_quality_report
        generate_quality_report >> end_validation
    
    return subdag


def create_reporting_subdag(
    parent_dag_name: str,
    child_dag_name: str,
    args: Dict[str, Any]
) -> DAG:
    """
    创建报表生成子DAG
    
    Args:
        parent_dag_name: 父DAG名称
        child_dag_name: 子DAG名称
        args: 参数字典
        
    Returns:
        DAG: 子DAG对象
    """
    dag_id = f"{parent_dag_name}.{child_dag_name}"
    
    subdag = DAG(
        dag_id=dag_id,
        default_args=args,
        schedule_interval=None,
        catchup=False,
    )
    
    with subdag:
        start_reporting = DummyOperator(
            task_id='start_reporting',
            dag=subdag
        )
        
        generate_daily_report = PythonOperator(
            task_id='generate_daily_report',
            python_callable=lambda **kwargs: print("生成日报表"),
            dag=subdag
        )
        
        generate_weekly_summary = PythonOperator(
            task_id='generate_weekly_summary',
            python_callable=lambda **kwargs: print("生成周汇总"),
            dag=subdag
        )
        
        create_executive_dashboard = PythonOperator(
            task_id='create_executive_dashboard',
            python_callable=lambda **kwargs: print("创建执行仪表板"),
            dag=subdag
        )
        
        distribute_reports = PythonOperator(
            task_id='distribute_reports',
            python_callable=lambda **kwargs: print("分发报表"),
            dag=subdag
        )
        
        end_reporting = DummyOperator(
            task_id='end_reporting',
            dag=subdag
        )
        
        # 设置报表生成流程依赖
        start_reporting >> [generate_daily_report, generate_weekly_summary]
        [generate_daily_report, generate_weekly_summary] >> create_executive_dashboard
        create_executive_dashboard >> distribute_reports
        distribute_reports >> end_reporting
    
    return subdag


# 创建主DAG
def create_main_dag_with_subdags() -> DAG:
    """创建包含子DAG的主DAG"""
    
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
        'enterprise_data_pipeline',
        default_args=default_args,
        description='企业级数据管道 - 使用子DAG组织复杂工作流',
        schedule_interval=timedelta(days=1),
        catchup=False,
        tags=['enterprise', 'subdag', 'advanced']
    )
    
    with dag:
        # 主DAG的开始和结束任务
        start_pipeline = DummyOperator(
            task_id='start_pipeline'
        )
        
        end_pipeline = DummyOperator(
            task_id='end_pipeline'
        )
        
        # 创建子DAG操作符
        data_extraction_subdag = SubDagOperator(
            task_id='data_extraction',
            subdag=create_data_extraction_subdag(
                'enterprise_data_pipeline',
                'data_extraction',
                default_args
            ),
            dag=dag,
        )
        
        data_processing_subdag = SubDagOperator(
            task_id='data_processing',
            subdag=create_data_processing_subdag(
                'enterprise_data_pipeline',
                'data_processing',
                default_args
            ),
            dag=dag,
        )
        
        quality_validation_subdag = SubDagOperator(
            task_id='quality_validation',
            subdag=create_quality_validation_subdag(
                'enterprise_data_pipeline',
                'quality_validation',
                default_args
            ),
            dag=dag,
        )
        
        reporting_subdag = SubDagOperator(
            task_id='reporting',
            subdag=create_reporting_subdag(
                'enterprise_data_pipeline',
                'reporting',
                default_args
            ),
            dag=dag,
        )
        
        # 设置主DAG依赖关系
        start_pipeline >> data_extraction_subdag
        data_extraction_subdag >> data_processing_subdag
        data_processing_subdag >> quality_validation_subdag
        quality_validation_subdag >> reporting_subdag
        reporting_subdag >> end_pipeline
    
    return dag


# 创建并行处理子DAG示例
def create_parallel_processing_subdag(
    parent_dag_name: str,
    child_dag_name: str,
    args: Dict[str, Any],
    num_parallel_tasks: int = 3
) -> DAG:
    """
    创建并行处理子DAG
    
    Args:
        parent_dag_name: 父DAG名称
        child_dag_name: 子DAG名称
        args: 参数字典
        num_parallel_tasks: 并行任务数量
        
    Returns:
        DAG: 子DAG对象
    """
    dag_id = f"{parent_dag_name}.{child_dag_name}"
    
    subdag = DAG(
        dag_id=dag_id,
        default_args=args,
        schedule_interval=None,
        catchup=False,
    )
    
    with subdag:
        start_parallel = DummyOperator(
            task_id='start_parallel',
            dag=subdag
        )
        
        parallel_tasks = []
        for i in range(num_parallel_tasks):
            task = PythonOperator(
                task_id=f'parallel_task_{i+1}',
                python_callable=lambda task_id, **kwargs: print(f"执行并行任务 {task_id}"),
                op_kwargs={'task_id': f'task_{i+1}'},
                dag=subdag
            )
            parallel_tasks.append(task)
        
        merge_results = PythonOperator(
            task_id='merge_results',
            python_callable=lambda **kwargs: print("合并并行任务结果"),
            dag=subdag
        )
        
        end_parallel = DummyOperator(
            task_id='end_parallel',
            dag=subdag
        )
        
        # 设置并行处理依赖
        start_parallel >> parallel_tasks
        parallel_tasks >> merge_results
        merge_results >> end_parallel
    
    return subdag


# 测试函数
def test_subdag_creation():
    """测试子DAG创建"""
    default_args = {
        'owner': 'airflow',
        'start_date': datetime(2024, 1, 1),
    }
    
    # 测试各个子DAG
    subdags = [
        ('data_extraction', create_data_extraction_subdag('test', 'data_extraction', default_args)),
        ('data_processing', create_data_processing_subdag('test', 'data_processing', default_args)),
        ('quality_validation', create_quality_validation_subdag('test', 'quality_validation', default_args)),
        ('reporting', create_reporting_subdag('test', 'reporting', default_args)),
        ('parallel_processing', create_parallel_processing_subdag('test', 'parallel_processing', default_args, 3))
    ]
    
    print("子DAG测试结果:")
    for name, subdag in subdags:
        print(f"{name}: {len(subdag.tasks)} 个任务")
    
    # 测试主DAG
    main_dag = create_main_dag_with_subdags()
    print(f"\n主DAG: {len(main_dag.tasks)} 个任务 (包含子DAG)")
    
    # 显示子DAG结构
    print("\n子DAG结构:")
    for task in main_dag.tasks:
        if hasattr(task, 'subdag') and task.subdag:
            print(f"{task.task_id}: {len(task.subdag.tasks)} 个子任务")


if __name__ == "__main__":
    test_subdag_creation()