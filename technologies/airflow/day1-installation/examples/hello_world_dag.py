"""
这是一个简单的 "Hello World" DAG 示例，用于演示 Airflow 的基本概念和语法。
这个 DAG 包含两个简单的任务，展示了基本的任务定义和依赖关系设置。
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# 定义默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建 DAG 实例
dag = DAG(
    'hello_world_dag',
    default_args=default_args,
    description='A simple hello world DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'basic'],
)

# 定义一个简单的 Python 函数
def print_hello():
    """打印 Hello World 消息"""
    return "Hello World!"

# 创建任务
task1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

task2 = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

task3 = BashOperator(
    task_id='print_goodbye',
    bash_command='echo "Goodbye World!"',
    dag=dag,
)

# 设置任务依赖关系
task1 >> task2 >> task3