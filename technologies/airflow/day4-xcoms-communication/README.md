# Day 4: XComs与任务间通信

## 学习目标

- 深入理解XComs机制和原理
- 掌握XComs的推送与拉取方法
- 学习Jinja模板在任务中的应用
- 实践任务间复杂数据传递
- 了解XComs的限制和最佳实践

## XComs概述

### 什么是XComs

XComs（Cross-communications）是Airflow中任务间通信的机制，允许任务之间共享小量数据。XComs由任务推送，其他任务可以拉取这些数据。

### XComs特点

- **轻量级**: 适合传递小量数据（通常小于1MB）
- **持久化**: 数据存储在Airflow元数据数据库中
- **类型灵活**: 支持多种数据类型（字符串、数字、JSON等）
- **任务间共享**: 可以跨越任务组、DAG边界共享数据

## XComs基本操作

### 推送XComs

#### PythonOperator推送XComs

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None, catchup=False)
def xcom_push_example():
    
    @task
    def push_data():
        # 返回值会自动作为XCom推送
        return {"key": "value", "count": 10}
    
    @task
    def another_push():
        # 显式推送XCom
        from airflow.models.xcom import XCom
        from airflow.models.taskinstance import TaskInstance
        
        # 使用ti.xcom_push()方法
        ti = TaskInstance(context={'ti': TaskInstance})
        ti.xcom_push(key="custom_key", value="custom_value")
        
        # 返回多个值
        return {"result": "success", "items": [1, 2, 3]}
    
    push_data()
    another_push()

xcom_push_dag = xcom_push_example()
```

#### BashOperator推送XComs

```python
from airflow.operators.bash import BashOperator
from airflow.models.dag import DAG
from datetime import datetime

with DAG(
    dag_id='bash_xcom_push',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    # 使用echo命令推送JSON格式的数据
    push_json = BashOperator(
        task_id='push_json',
        bash_command='echo '{"data": "from bash", "count": 5}'',
        xcom_push=True  # 启用XCom推送
    )
    
    # 推送简单字符串
    push_string = BashOperator(
        task_id='push_string',
        bash_command='echo "simple string"',
        xcom_push=True
    )
```

### 拉取XComs

#### PythonOperator拉取XComs

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None, catchup=False)
def xcom_pull_example():
    
    @task
    def push_data():
        return {"key": "value", "count": 10}
    
    @task
    def pull_data(ti):
        # 拉取上一个任务的返回值
        previous_result = ti.xcom_pull(task_ids='push_data')
        print(f"Previous result: {previous_result}")
        
        # 拉取特定键的值
        count = ti.xcom_pull(task_ids='push_data', key='count')
        print(f"Count: {count}")
        
        # 拉取多个任务的值
        # values = ti.xcom_pull(task_ids=['task1', 'task2'])
        
        return f"Processed {count} items"
    
    push_data() >> pull_data()

xcom_pull_dag = xcom_pull_example()
```

#### BashOperator中使用XComs

```python
from airflow.operators.bash import BashOperator
from airflow.models.dag import DAG
from datetime import datetime

with DAG(
    dag_id='bash_xcom_pull',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    # 先推送数据
    push_data = BashOperator(
        task_id='push_data',
        bash_command='echo '{"path": "/data/files", "filename": "data.csv"}'',
        xcom_push=True
    )
    
    # 在BashOperator中使用Jinja模板拉取XCom
    use_data = BashOperator(
        task_id='use_data',
        bash_command="""
        echo "Processing file: {{ ti.xcom_pull(task_ids='push_data')['filename'] }}"
        echo "File path: {{ ti.xcom_pull(task_ids='push_data')['path'] }}"
        ls {{ ti.xcom_pull(task_ids='push_data')['path'] }}
        """
    )
    
    push_data >> use_data
```

## Jinja模板与XComs

### Jinja模板基础

Jinja模板是Airflow中用于动态生成命令和参数的强大工具，可以在各种操作符中使用。

### 在BashOperator中使用Jinja模板

```python
from airflow.operators.bash import BashOperator
from airflow.models.dag import DAG
from datetime import datetime

with DAG(
    dag_id='jinja_template_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    # 使用数据时间宏
    print_date = BashOperator(
        task_id='print_date',
        bash_command='echo "Today is {{ ds }}"'  # ds是执行日期
    )
    
    # 使用变量
    print_variable = BashOperator(
        task_id='print_variable',
        bash_command='echo "DAG run ID: {{ dag_run.run_id }}"'
    )
    
    # 使用XComs
    push_data = BashOperator(
        task_id='push_data',
        bash_command='echo "data_{{ ds_nodash }}.csv"',
        xcom_push=True
    )
    
    use_data = BashOperator(
        task_id='use_data',
        bash_command="""
        echo "Processing file: {{ ti.xcom_pull(task_ids='push_data') }}"
        echo "Execution date: {{ ds }}"
        echo "Previous execution date: {{ prev_ds }}"
        echo "Next execution date: {{ next_ds }}"
        """
    )
    
    print_date >> print_variable >> push_data >> use_data
```

### 在PythonOperator中使用Jinja模板

```python
from airflow.operators.python import PythonOperator
from airflow.models.dag import DAG
from datetime import datetime
import logging

def process_file(**kwargs):
    # 从模板渲染的参数中获取值
    file_path = kwargs['file_path']
    file_name = kwargs['file_name']
    
    # 从XCom中获取数据
    ti = kwargs['ti']
    file_info = ti.xcom_pull(task_ids='get_file_info')
    
    logging.info(f"Processing file: {file_path}/{file_name}")
    logging.info(f"File info: {file_info}")
    
    return {"status": "success", "processed_file": file_name}

with DAG(
    dag_id='python_jinja_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    get_file_info = PythonOperator(
        task_id='get_file_info',
        python_callable=lambda: {"size": "10MB", "type": "csv"}
    )
    
    # 使用模板渲染参数
    process_file_task = PythonOperator(
        task_id='process_file',
        python_callable=process_file,
        templates_dict={
            'file_path': '/data/processed',
            'file_name': '{{ ti.xcom_pull(task_ids="get_file_info")["type"] }}_{{ ds_nodash }}.csv'
        }
    )
    
    get_file_info >> process_file_task
```

## 复杂数据传递场景

### 跨任务组的XComs

```python
from airflow.decorators import dag, task, task_group
from datetime import datetime

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None, catchup=False)
def cross_taskgroup_xcoms():
    
    @task_group
    def data_extraction():
        @task
        def extract_customer_data():
            return {"customers": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
        
        @task
        def extract_order_data():
            return {"orders": [{"id": 101, "customer_id": 1}, {"id": 102, "customer_id": 2}]}
        
        extract_customer_data() >> extract_order_data()
    
    @task_group
    def data_processing():
        @task
        def process_data(ti):
            # 从不同任务组拉取XComs
            customer_data = ti.xcom_pull(task_ids='data_extraction.extract_customer_data')
            order_data = ti.xcom_pull(task_ids='data_extraction.extract_order_data')
            
            # 处理数据
            processed_data = {
                "customers": customer_data["customers"],
                "orders": order_data["orders"],
                "processed_at": "{{ ds }}"
            }
            
            return processed_data
        
        @task
        def validate_data(ti):
            processed_data = ti.xcom_pull(task_ids='process_data')
            
            # 验证数据
            if not processed_data.get("customers") or not processed_data.get("orders"):
                raise ValueError("Invalid data: missing customers or orders")
                
            return {"validation": "success", "record_count": len(processed_data["customers"])}
        
        process_data() >> validate_data()
    
    @task
    def store_results(ti):
        validation_result = ti.xcom_pull(task_ids='data_processing.validate_data')
        processed_data = ti.xcom_pull(task_ids='data_processing.process_data')
        
        # 存储结果
        print(f"Validation result: {validation_result}")
        print(f"Processed data: {processed_data}")
        
        return {"storage": "success", "records": validation_result["record_count"]}
    
    data_extraction() >> data_processing() >> store_results()

cross_taskgroup_xcoms_dag = cross_taskgroup_xcoms()
```

### 基于XComs的条件分支

```python
from airflow.decorators import dag, task, branch
from airflow.operators.dummy import DummyOperator
from datetime import datetime
import random

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None, catchup=False)
def xcom_based_branching():
    
    @task
    def generate_data():
        # 生成随机数据
        data_type = random.choice(["csv", "json", "xml"])
        data_size = random.randint(100, 1000)
        
        return {"type": data_type, "size": data_size}
    
    @branch
    def choose_processor(ti):
        data_info = ti.xcom_pull(task_ids='generate_data')
        data_type = data_info["type"]
        
        # 根据数据类型选择处理器
        if data_type == "csv":
            return "process_csv"
        elif data_type == "json":
            return "process_json"
        elif data_type == "xml":
            return "process_xml"
        else:
            return "process_unknown"
    
    @task
    def process_csv(ti):
        data_info = ti.xcom_pull(task_ids='generate_data')
        print(f"Processing CSV data of size {data_info['size']}")
        return {"processed": "csv", "records": data_info["size"]}
    
    @task
    def process_json(ti):
        data_info = ti.xcom_pull(task_ids='generate_data')
        print(f"Processing JSON data of size {data_info['size']}")
        return {"processed": "json", "records": data_info["size"]}
    
    @task
    def process_xml(ti):
        data_info = ti.xcom_pull(task_ids='generate_data')
        print(f"Processing XML data of size {data_info['size']}")
        return {"processed": "xml", "records": data_info["size"]}
    
    @task
    def process_unknown(ti):
        data_info = ti.xcom_pull(task_ids='generate_data')
        print(f"Unknown data type: {data_info['type']}")
        return {"processed": "unknown", "records": 0}
    
    @task
    def store_results(ti):
        # 拉取所有可能的处理结果
        csv_result = ti.xcom_pull(task_ids='process_csv')
        json_result = ti.xcom_pull(task_ids='process_json')
        xml_result = ti.xcom_pull(task_ids='process_xml')
        unknown_result = ti.xcom_pull(task_ids='process_unknown')
        
        # 确定实际执行的结果
        result = csv_result or json_result or xml_result or unknown_result
        print(f"Final result: {result}")
        
        return result
    
    join = DummyOperator(task_id='join')
    
    generate_data() >> choose_processor() >> [process_csv(), process_json(), process_xml(), process_unknown()] >> join >> store_results()

xcom_branching_dag = xcom_based_branching()
```

## XComs限制与最佳实践

### XComs限制

1. **数据大小限制**: XComs不适合传递大量数据，通常限制在1MB以内
2. **性能影响**: 频繁的XComs操作可能影响性能
3. **数据库负载**: XComs数据存储在元数据数据库中，大量使用可能增加数据库负载
4. **序列化限制**: 数据需要可序列化，某些复杂对象可能无法直接传递

### 最佳实践

1. **少量数据**: 只传递必要的元数据和小量数据
2. **文件路径**: 对于大量数据，传递文件路径而非数据本身
3. **清理旧数据**: 定期清理不再需要的XComs数据
4. **使用适当的键**: 使用有意义的键名，避免冲突
5. **考虑替代方案**: 对于大量数据，考虑使用外部存储（如S3、数据库）

### 清理XComs

```python
from airflow.decorators import dag, task
from airflow.models.xcom import XCom
from airflow.models.dag import DAG
from datetime import datetime, timedelta

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None, catchup=False)
def xcom_cleanup_example():
    
    @task
    def generate_data():
        return {"data": "example", "size": 100}
    
    @task
    def process_data(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        return {"processed": data["data"], "new_size": data["size"] * 2}
    
    @task
    def cleanup_xcoms():
        # 清理超过7天的XComs
        session = settings.Session()
        cutoff_date = datetime.now() - timedelta(days=7)
        
        deleted_count = session.query(XCom).filter(
            XCom.execution_date < cutoff_date
        ).delete()
        
        session.commit()
        session.close()
        
        return {"deleted_xcoms": deleted_count}
    
    generate_data() >> process_data() >> cleanup_xcoms()

xcom_cleanup_dag = xcom_cleanup_example()
```

## 实践练习

### 练习1: 基本XComs传递

创建一个DAG，包含以下任务：
1. 生成随机数据（数字、字符串、字典）
2. 处理数据（计算、转换）
3. 存储处理结果

### 练习2: 跨任务组XComs

创建一个包含多个任务组的DAG，实现：
1. 数据提取任务组（提取不同类型数据）
2. 数据处理任务组（处理提取的数据）
3. 数据验证任务组（验证处理结果）

### 练习3: 基于XComs的条件分支

创建一个DAG，根据XComs中的数据类型或状态，选择不同的处理路径。

### 练习4: Jinja模板与XComs结合

创建一个DAG，在BashOperator中使用Jinja模板和XComs，实现动态命令生成。

## 进阶阅读

- [Airflow XComs官方文档](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html)
- [Jinja模板官方文档](https://jinja.palletsprojects.com/en/3.1.x/)
- [Airflow模板系统](https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html)

## 今日小结

今天我们学习了XComs机制和任务间通信，包括：

- XComs的基本概念和特点
- 如何推送和拉取XComs数据
- Jinja模板在任务中的应用
- 跨任务组的XComs通信
- 基于XComs的条件分支
- XComs的限制和最佳实践

XComs是Airflow中实现任务间通信的重要机制，合理使用XComs可以构建灵活而强大的数据管道。

## 下一步计划

明天我们将学习传感器(Sensors)与钩子(Hooks)，了解如何与外部系统交互和等待外部事件。

---

*本文档基于Airflow 2.x版本编写，部分功能可能在不同版本中有所差异。*