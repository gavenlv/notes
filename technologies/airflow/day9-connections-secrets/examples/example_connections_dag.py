"""
示例DAG：展示如何在Apache Airflow中使用连接和密钥管理

此DAG演示了以下概念：
1. 如何在DAG中使用数据库连接
2. 如何安全地访问API密钥
3. 如何使用环境变量
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook
from airflow.models import Variable
import os

# 默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建DAG
dag = DAG(
    'example_connections_secrets',
    default_args=default_args,
    description='示例DAG：展示连接和密钥管理',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'connections', 'secrets']
)

def use_database_connection():
    """演示如何使用数据库连接"""
    # 获取数据库连接
    conn = BaseHook.get_connection('my_postgres_db')
    
    # 打印连接信息（注意：在实际应用中不要打印密码）
    print(f"连接主机: {conn.host}")
    print(f"连接端口: {conn.port}")
    print(f"数据库名: {conn.schema}")
    print(f"用户名: {conn.login}")
    # 注意：不要在日志中打印密码
    # print(f"密码: {conn.password}")
    
    # 在实际应用中，这里会使用这些信息建立数据库连接
    # 并执行相应的数据库操作

def use_api_key():
    """演示如何安全地使用API密钥"""
    # 方法1：通过Airflow Variables获取API密钥
    try:
        api_key = Variable.get("my_api_key")
        print("成功获取API密钥")
        # 在实际应用中，这里会使用API密钥调用外部服务
    except Exception as e:
        print(f"获取API密钥失败: {e}")
    
    # 方法2：通过环境变量获取API密钥
    api_key_env = os.getenv('MY_API_KEY')
    if api_key_env:
        print("成功从环境变量获取API密钥")
    else:
        print("未能从环境变量获取API密钥")

def demonstrate_best_practices():
    """演示安全最佳实践"""
    print("安全最佳实践:")
    print("1. 永远不要在代码中硬编码敏感信息")
    print("2. 使用Airflow Connections存储数据库凭证")
    print("3. 使用Airflow Variables或Secrets Backends存储API密钥")
    print("4. 限制对敏感信息的访问权限")
    print("5. 定期轮换密钥和凭证")

# 创建任务
task1 = PythonOperator(
    task_id='use_database_connection',
    python_callable=use_database_connection,
    dag=dag,
)

task2 = PythonOperator(
    task_id='use_api_key',
    python_callable=use_api_key,
    dag=dag,
)

task3 = PythonOperator(
    task_id='demonstrate_best_practices',
    python_callable=demonstrate_best_practices,
    dag=dag,
)

# 设置任务依赖
task1 >> task2 >> task3