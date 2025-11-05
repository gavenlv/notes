"""
操作符示例DAG
演示不同类型操作符的使用方法
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.common.sql.operators.sql import SqlOperator
from airflow.operators.dummy import DummyOperator
import random

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
    'operators_dag',
    default_args=default_args,
    description='演示不同类型操作符的DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'operators'],
)

# 开始任务
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

# BashOperator示例
bash_task = BashOperator(
    task_id='bash_example',
    bash_command='echo "这是一个BashOperator示例" && date',
    dag=dag,
)

# PythonOperator示例
def python_function():
    """Python函数示例"""
    number = random.randint(1, 100)
    print(f"随机生成的数字: {number}")
    return number

python_task = PythonOperator(
    task_id='python_example',
    python_callable=python_function,
    dag=dag,
)

# BranchPythonOperator示例
def branch_function():
    """分支函数示例"""
    number = random.randint(1, 10)
    print(f"随机数字: {number}")
    if number <= 5:
        return 'branch_a'
    else:
        return 'branch_b'

branch_task = BranchPythonOperator(
    task_id='branch_example',
    python_callable=branch_function,
    dag=dag,
)

# 分支A
branch_a = BashOperator(
    task_id='branch_a',
    bash_command='echo "执行分支A"',
    dag=dag,
)

# 分支B
branch_b = BashOperator(
    task_id='branch_b',
    bash_command='echo "执行分支B"',
    dag=dag,
)

# 合并分支
join_task = DummyOperator(
    task_id='join',
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)

# HttpOperator示例（需要配置HTTP连接）
http_task = HttpOperator(
    task_id='http_example',
    http_conn_id='http_default',
    endpoint='api/v1/data',
    method='GET',
    dag=dag,
)

# SqlOperator示例（需要配置数据库连接）
sql_task = SqlOperator(
    task_id='sql_example',
    sql='SELECT COUNT(*) FROM table',
    conn_id='my_db_conn',
    dag=dag,
)

# EmailOperator示例（需要配置SMTP）
email_task = EmailOperator(
    task_id='email_example',
    to='recipient@example.com',
    subject='Airflow DAG执行完成',
    html_content='<h3>DAG执行成功</h3><p>这是一个操作符示例DAG的执行结果。</p>',
    dag=dag,
)

# 结束任务
end_task = DummyOperator(
    task_id='end',
    dag=dag,
)

# 设置任务依赖关系
start_task >> bash_task >> python_task >> branch_task
branch_task >> [branch_a, branch_b] >> join_task
join_task >> [http_task, sql_task] >> email_task >> end_task