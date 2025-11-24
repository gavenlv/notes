"""
示例DAG：基本XComs推送与拉取
演示如何在任务之间传递数据
"""

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime
import random

@dag(
    dag_id='basic_xcom_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['xcoms', 'basic'],
    doc_md="""
    ### 基本XComs示例
    
    这个DAG演示了XComs的基本用法：
    - Python任务推送和拉取XComs
    - Bash任务推送和拉取XComs
    - 不同类型数据的传递
    """
)
def basic_xcom_example():
    
    @task
    def generate_random_number():
        """生成随机数并作为XCom推送"""
        number = random.randint(1, 100)
        print(f"Generated random number: {number}")
        return number
    
    @task
    def generate_random_string():
        """生成随机字符串并作为XCom推送"""
        import string
        length = random.randint(5, 15)
        random_str = ''.join(random.choices(string.ascii_letters, k=length))
        print(f"Generated random string: {random_str}")
        return random_str
    
    @task
    def generate_dict_data():
        """生成字典数据并作为XCom推送"""
        data = {
            "id": random.randint(1000, 9999),
            "name": f"Item_{random.randint(1, 100)}",
            "value": round(random.uniform(10.0, 100.0), 2),
            "tags": [f"tag_{i}" for i in range(random.randint(1, 5))]
        }
        print(f"Generated dictionary data: {data}")
        return data
    
    @task
    def process_number(ti):
        """拉取并处理数字"""
        number = ti.xcom_pull(task_ids='generate_random_number')
        processed = number * 2
        print(f"Original number: {number}, Processed: {processed}")
        return {"original": number, "processed": processed}
    
    @task
    def process_string(ti):
        """拉取并处理字符串"""
        original_str = ti.xcom_pull(task_ids='generate_random_string')
        processed_str = original_str.upper()
        print(f"Original string: {original_str}, Processed: {processed_str}")
        return {"original": original_str, "processed": processed_str}
    
    @task
    def process_dict(ti):
        """拉取并处理字典"""
        original_dict = ti.xcom_pull(task_ids='generate_dict_data')
        processed_dict = original_dict.copy()
        processed_dict["processed_at"] = "{{ ds }}"
        processed_dict["value"] = round(processed_dict["value"] * 1.1, 2)
        print(f"Original dict: {original_dict}")
        print(f"Processed dict: {processed_dict}")
        return processed_dict
    
    # Bash任务推送XCom
    bash_push_json = BashOperator(
        task_id='bash_push_json',
        bash_command='echo '{"type": "bash", "status": "success", "count": 5}"',
        xcom_push=True,
        doc_md="使用BashOperator推送JSON格式的XCom"
    )
    
    @task
    def process_bash_data(ti):
        """处理Bash任务推送的数据"""
        bash_data = ti.xcom_pull(task_ids='bash_push_json')
        print(f"Bash data: {bash_data}")
        return {"source": "bash", "data": bash_data}
    
    # 设置任务依赖
    generate_random_number() >> process_number()
    generate_random_string() >> process_string()
    generate_dict_data() >> process_dict()
    bash_push_json >> process_bash_data()

basic_xcom_dag = basic_xcom_example()