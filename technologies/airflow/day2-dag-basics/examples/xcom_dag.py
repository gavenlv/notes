"""
XComs示例DAG
演示任务间通信（XComs）的使用方法
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models.xcom import XCom

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
    'xcom_dag',
    default_args=default_args,
    description='演示XComs使用的DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'xcom'],
)

# 定义Python函数
def generate_random_number(**kwargs):
    """生成随机数"""
    import random
    number = random.randint(1, 100)
    print(f"生成的随机数: {number}")
    # 推送XCom值
    kwargs['ti'].xcom_push(key='random_number', value=number)
    return number

def process_number(**kwargs):
    """处理数字"""
    # 拉取XCom值
    ti = kwargs['ti']
    number = ti.xcom_pull(task_ids='generate_number', key='random_number')
    
    # 处理数字
    if number % 2 == 0:
        result = f"{number} 是偶数"
    else:
        result = f"{number} 是奇数"
    
    print(f"处理结果: {result}")
    # 推送处理结果
    ti.xcom_push(key='processing_result', value=result)
    return result

def print_result(**kwargs):
    """打印结果"""
    # 拉取处理结果
    ti = kwargs['ti']
    result = ti.xcom_pull(task_ids='process_number', key='processing_result')
    print(f"最终结果: {result}")
    return result

# 创建任务
generate_task = PythonOperator(
    task_id='generate_number',
    python_callable=generate_random_number,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_number',
    python_callable=process_number,
    dag=dag,
)

print_task = PythonOperator(
    task_id='print_result',
    python_callable=print_result,
    dag=dag,
)

# 使用BashOperator和XCom
bash_push_task = BashOperator(
    task_id='bash_push',
    bash_command='echo "42" && echo "{{ ti.xcom_push(task_ids=\'bash_push\', key=\'bash_value\', value=42) }}"',
    do_xcom_push=True,
    dag=dag,
)

bash_pull_task = BashOperator(
    task_id='bash_pull',
    bash_command='echo "从Bash任务获取的值: {{ ti.xcom_pull(task_ids=\'bash_push\', key=\'bash_value\') }}"',
    dag=dag,
)

# Jinja模板中使用XCom
jinja_task = BashOperator(
    task_id='jinja_template',
    bash_command='echo "Python任务生成的随机数: {{ ti.xcom_pull(task_ids=\'generate_number\') }}"',
    dag=dag,
)

# 设置任务依赖关系
generate_task >> process_task >> print_task
generate_task >> bash_push_task >> bash_pull_task
process_task >> jinja_task