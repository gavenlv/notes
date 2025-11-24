"""
动态DAG示例
演示如何动态生成DAG和任务
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

# 定义默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建DAG实例
dag = DAG(
    'dynamic_dag',
    default_args=default_args,
    description='动态生成任务的DAG示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'dynamic'],
)

# 定义处理函数
def process_data(data_type, **kwargs):
    """处理数据的通用函数"""
    print(f"处理 {data_type} 数据")
    # 这里可以添加实际的数据处理逻辑
    return f"已处理 {data_type} 数据"

# 数据类型列表
data_types = ['user', 'order', 'product', 'inventory', 'analytics']

# 创建开始任务
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

# 创建结束任务
end_task = DummyOperator(
    task_id='end',
    dag=dag,
)

# 动态创建任务
tasks = []
for data_type in data_types:
    # 创建数据验证任务
    validate_task = BashOperator(
        task_id=f'validate_{data_type}',
        bash_command=f'echo "验证 {data_type} 数据"',
        dag=dag,
    )
    
    # 创建数据处理任务
    process_task = PythonOperator(
        task_id=f'process_{data_type}',
        python_callable=process_data,
        op_kwargs={'data_type': data_type},
        dag=dag,
    )
    
    # 创建数据存储任务
    store_task = BashOperator(
        task_id=f'store_{data_type}',
        bash_command=f'echo "存储 {data_type} 数据"',
        dag=dag,
    )
    
    # 设置任务依赖关系
    validate_task >> process_task >> store_task
    
    # 将任务添加到列表
    tasks.append((validate_task, process_task, store_task))

# 设置所有数据处理任务完成后才能执行结束任务
for _, _, store_task in tasks:
    store_task >> end_task

# 设置开始任务到所有验证任务的依赖
for validate_task, _, _ in tasks:
    start_task >> validate_task

# 创建动态条件任务
def check_condition(**kwargs):
    """检查条件"""
    import random
    condition = random.choice([True, False])
    print(f"条件检查结果: {condition}")
    return condition

check_task = PythonOperator(
    task_id='check_condition',
    python_callable=check_condition,
    dag=dag,
)

# 创建条件分支任务
def branch_function(**kwargs):
    """分支函数"""
    ti = kwargs['ti']
    condition = ti.xcom_pull(task_ids='check_condition')
    if condition:
        return 'branch_true'
    else:
        return 'branch_false'

branch_task = PythonOperator(
    task_id='branch_decision',
    python_callable=branch_function,
    dag=dag,
)

# 创建分支任务
branch_true = BashOperator(
    task_id='branch_true',
    bash_command='echo "条件为真，执行分支A"',
    dag=dag,
)

branch_false = BashOperator(
    task_id='branch_false',
    bash_command='echo "条件为假，执行分支B"',
    dag=dag,
)

# 合并分支
join_task = DummyOperator(
    task_id='join_branches',
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)

# 设置条件任务的依赖关系
end_task >> check_task >> branch_task
branch_task >> [branch_true, branch_false] >> join_task

# 创建最终报告任务
final_report = BashOperator(
    task_id='final_report',
    bash_command='echo "生成最终报告"',
    dag=dag,
)

# 设置最终任务的依赖
join_task >> final_report