from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup

with DAG(
    dag_id="task_group_example",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["dependencies", "task-groups"],
) as dag:
    start = DummyOperator(task_id="start")
    
    # 创建一个简单的任务组
    with TaskGroup("data_processing") as data_processing:
        extract = DummyOperator(task_id="extract")
        transform = DummyOperator(task_id="transform")
        load = DummyOperator(task_id="load")
        
        extract >> transform >> load
    
    # 创建嵌套任务组
    with TaskGroup("etl_pipeline") as etl_pipeline:
        with TaskGroup("extract") as extract_group:
            extract_db = DummyOperator(task_id="extract_from_db")
            extract_api = DummyOperator(task_id="extract_from_api")
            
        with TaskGroup("transform") as transform_group:
            clean_data = DummyOperator(task_id="clean_data")
            enrich_data = DummyOperator(task_id="enrich_data")
            
            clean_data >> enrich_data
            
        with TaskGroup("load") as load_group:
            load_warehouse = DummyOperator(task_id="load_to_warehouse")
            load_api = DummyOperator(task_id="load_to_api")
    
    # 创建并行任务组
    with TaskGroup("parallel_tasks") as parallel_tasks:
        with TaskGroup("branch_a") as branch_a:
            a1 = DummyOperator(task_id="a1")
            a2 = DummyOperator(task_id="a2")
            a1 >> a2
            
        with TaskGroup("branch_b") as branch_b:
            b1 = DummyOperator(task_id="b1")
            b2 = DummyOperator(task_id="b2")
            b1 >> b2
            
        with TaskGroup("branch_c") as branch_c:
            c1 = DummyOperator(task_id="c1")
            c2 = DummyOperator(task_id="c2")
            c1 >> c2
    
    end = DummyOperator(task_id="end")
    
    # 设置依赖关系
    start >> data_processing >> etl_pipeline >> parallel_tasks >> end