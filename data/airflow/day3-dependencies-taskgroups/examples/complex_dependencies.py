from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

def extract_data():
    """模拟数据提取"""
    print("Extracting data from source...")
    return {"records": 1000, "status": "success"}

def transform_data():
    """模拟数据转换"""
    print("Transforming data...")
    return {"records": 950, "status": "success"}  # 一些记录被过滤

def load_data():
    """模拟数据加载"""
    print("Loading data to destination...")
    return {"records": 950, "status": "success"}

def validate_data():
    """模拟数据验证"""
    print("Validating data quality...")
    # 在实际场景中，这里会有实际的验证逻辑
    return {"quality_score": 0.85, "status": "pass"}

def notify_success():
    """发送成功通知"""
    print("Sending success notification...")

def notify_failure():
    """发送失败通知"""
    print("Sending failure notification...")

def cleanup():
    """清理临时资源"""
    print("Cleaning up temporary resources...")

with DAG(
    dag_id="complex_dependencies_example",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["dependencies", "complex"],
) as dag:
    # 开始任务
    start = DummyOperator(task_id="start")
    
    # ETL任务
    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_data
    )
    
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_data
    )
    
    load = PythonOperator(
        task_id="load",
        python_callable=load_data
    )
    
    # 数据质量检查
    validate = PythonOperator(
        task_id="validate",
        python_callable=validate_data
    )
    
    # 通知任务
    success_notification = PythonOperator(
        task_id="success_notification",
        python_callable=notify_success,
        trigger_rule="all_success"
    )
    
    failure_notification = PythonOperator(
        task_id="failure_notification",
        python_callable=notify_failure,
        trigger_rule="one_failed"
    )
    
    # 清理任务 - 无论成功或失败都会执行
    cleanup_task = PythonOperator(
        task_id="cleanup",
        python_callable=cleanup,
        trigger_rule="all_done"
    )
    
    # 结束任务
    end = DummyOperator(
        task_id="end",
        trigger_rule="all_done"
    )
    
    # 设置复杂的依赖关系
    start >> extract >> transform >> load >> validate
    
    # 验证成功后发送成功通知
    validate >> success_notification
    
    # 任何任务失败后发送失败通知
    extract >> failure_notification
    transform >> failure_notification
    load >> failure_notification
    validate >> failure_notification
    
    # 清理任务在所有任务完成后执行
    [success_notification, failure_notification] >> cleanup_task >> end