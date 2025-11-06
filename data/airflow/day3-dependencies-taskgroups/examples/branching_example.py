from __future__ import annotations

import pendulum
import random

from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator

def choose_branch():
    """随机选择一个分支"""
    branches = ["branch_a", "branch_b", "branch_c"]
    return random.choice(branches)

def check_condition(**kwargs):
    """基于条件选择分支"""
    # 这里可以添加复杂的逻辑
    # 例如检查数据质量、时间条件等
    return "branch_a" if random.random() > 0.5 else "branch_b"

def process_branch_a():
    """处理分支A的逻辑"""
    print("Processing branch A")

def process_branch_b():
    """处理分支B的逻辑"""
    print("Processing branch B")

def process_branch_c():
    """处理分支C的逻辑"""
    print("Processing branch C")

with DAG(
    dag_id="branching_example",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["dependencies", "branching"],
) as dag:
    start = DummyOperator(task_id="start")
    
    # 使用BranchPythonOperator进行随机分支选择
    random_branching = BranchPythonOperator(
        task_id="random_branching",
        python_callable=choose_branch
    )
    
    # 使用BranchPythonOperator进行条件分支选择
    conditional_branching = BranchPythonOperator(
        task_id="conditional_branching",
        python_callable=check_condition
    )
    
    # 定义随机分支的任务
    branch_a = PythonOperator(
        task_id="branch_a",
        python_callable=process_branch_a
    )
    
    branch_b = PythonOperator(
        task_id="branch_b",
        python_callable=process_branch_b
    )
    
    branch_c = PythonOperator(
        task_id="branch_c",
        python_callable=process_branch_c
    )
    
    # 定义条件分支的任务
    path_a = PythonOperator(
        task_id="path_a",
        python_callable=process_branch_a
    )
    
    path_b = PythonOperator(
        task_id="path_b",
        python_callable=process_branch_b
    )
    
    # 合并点
    random_join = DummyOperator(
        task_id="random_join",
        trigger_rule="none_failed_or_skipped"
    )
    
    conditional_join = DummyOperator(
        task_id="conditional_join",
        trigger_rule="none_failed_or_skipped"
    )
    
    end = DummyOperator(task_id="end")
    
    # 设置依赖关系
    start >> [random_branching, conditional_branching]
    
    # 随机分支依赖
    random_branching >> [branch_a, branch_b, branch_c] >> random_join
    
    # 条件分支依赖
    conditional_branching >> [path_a, path_b] >> conditional_join
    
    # 最终合并
    [random_join, conditional_join] >> end