"""
基础DAG示例
演示Airflow DAG的基本结构和任务定义
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

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
    'basic_dag',
    default_args=default_args,
    description='一个基础的DAG示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'basic'],
)

# 定义Python函数
def print_current_date():
    """打印当前日期"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    print(f"当前日期: {current_date}")
    return current_date

def print_current_time():
    """打印当前时间"""
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"当前时间: {current_time}")
    return current_time

# 创建任务
task1 = PythonOperator(
    task_id='print_date',
    python_callable=print_current_date,
    dag=dag,
)

task2 = BashOperator(
    task_id='print_hello',
    bash_command='echo "Hello World!"',
    dag=dag,
)

task3 = PythonOperator(
    task_id='print_time',
    python_callable=print_current_time,
    dag=dag,
)

# 设置任务依赖关系
task1 >> task2 >> task3