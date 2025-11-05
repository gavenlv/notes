# XComs与任务间通信快速参考

## XComs基本操作

### 推送XComs

#### PythonOperator自动推送

```python
from airflow.decorators import task

@task
def push_data():
    # 返回值会自动作为XCom推送
    return {"key": "value", "count": 10}
```

#### 显式推送XComs

```python
from airflow.decorators import task

@task
def push_data_explicit():
    # 使用ti.xcom_push()方法
    ti = kwargs['ti']  # 在函数参数中获取ti
    ti.xcom_push(key="custom_key", value="custom_value")
    
    # 返回多个值
    return {"result": "success", "items": [1, 2, 3]}
```

#### BashOperator推送XComs

```python
from airflow.operators.bash import BashOperator

# 推送JSON格式的数据
push_json = BashOperator(
    task_id='push_json',
    bash_command='echo '{"data": "from bash", "count": 5}"',
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
from airflow.decorators import task

@task
def pull_data(ti):
    # 拉取上一个任务的返回值
    previous_result = ti.xcom_pull(task_ids='push_data')
    
    # 拉取特定键的值
    count = ti.xcom_pull(task_ids='push_data', key='custom_key')
    
    # 拉取多个任务的值
    values = ti.xcom_pull(task_ids=['task1', 'task2'])
    
    return f"Processed {count} items"
```

#### BashOperator中使用Jinja模板拉取XComs

```python
from airflow.operators.bash import BashOperator

# 在Bash命令中使用Jinja模板
use_data = BashOperator(
    task_id='use_data',
    bash_command="""
    echo "Processing file: {{ ti.xcom_pull(task_ids='push_data')['filename'] }}"
    echo "File path: {{ ti.xcom_pull(task_ids='push_data')['path'] }}"
    """
)
```

## Jinja模板与XComs

### 常用Jinja模板变量

```python
# 数据时间变量
{{ ds }}          # 执行日期 (YYYY-MM-DD)
{{ ds_nodash }}   # 执行日期 (YYYYMMDD)
{{ prev_ds }}     # 上次执行日期
{{ next_ds }}     # 下次执行日期
{{ ts }}          # 时间戳
{{ ts_nodash }}   # 无分隔符的时间戳

# DAG运行变量
{{ dag.dag_id }}  # DAG ID
{{ dag_run.run_id }}  # DAG运行ID
{{ dag_run.execution_date }}  # 执行日期

# 任务实例变量
{{ task.task_id }}  # 任务ID
{{ ti }}  # 任务实例对象
```

### 在BashOperator中使用Jinja模板

```python
from airflow.operators.bash import BashOperator

# 使用数据时间宏
print_date = BashOperator(
    task_id='print_date',
    bash_command='echo "Today is {{ ds }}"'
)

# 使用XComs
use_xcom = BashOperator(
    task_id='use_xcom',
    bash_command="""
    echo "Data: {{ ti.xcom_pull(task_ids='get_data') }}"
    echo "Processing date: {{ ds }}"
    """
)

# 复杂命令生成
dynamic_command = BashOperator(
    task_id='dynamic_command',
    bash_command="""
    DATA="{{ ti.xcom_pull(task_ids='get_data') }}"
    INPUT_PATH=$(echo "$DATA" | python -c "import sys, json; print(json.load(sys.stdin)['path'])")
    echo "Processing file at: $INPUT_PATH"
    """
)
```

### 在PythonOperator中使用模板参数

```python
from airflow.operators.python import PythonOperator

def process_file(**kwargs):
    # 从模板渲染的参数中获取值
    file_path = kwargs['file_path']
    file_name = kwargs['file_name']
    
    # 从XCom中获取数据
    ti = kwargs['ti']
    file_info = ti.xcom_pull(task_ids='get_file_info')
    
    return {"status": "success", "processed_file": file_name}

# 使用模板渲染参数
process_file_task = PythonOperator(
    task_id='process_file',
    python_callable=process_file,
    templates_dict={
        'file_path': '/data/processed',
        'file_name': '{{ ti.xcom_pull(task_ids="get_file_info")["type"] }}_{{ ds_nodash }}.csv'
    }
)
```

## 跨任务组XComs

### 任务组间数据传递

```python
from airflow.decorators import dag, task, task_group

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None)
def cross_taskgroup_xcoms():
    
    @task_group
    def data_extraction():
        @task
        def extract_data():
            return {"records": [{"id": 1, "name": "Item 1"}]}
        
        extract_data()
    
    @task_group
    def data_processing():
        @task
        def process_data(ti):
            # 从不同任务组拉取XComs
            extracted_data = ti.xcom_pull(task_ids='data_extraction.extract_data')
            
            # 处理数据
            processed_data = {
                "records": extracted_data["records"],
                "processed_at": "{{ ds }}"
            }
            
            return processed_data
        
        process_data()
    
    data_extraction() >> data_processing()
```

### 嵌套任务组XComs

```python
from airflow.decorators import dag, task, task_group

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None)
def nested_taskgroup_xcoms():
    
    @task_group
    def etl_pipeline():
        @task_group
        def extract():
            @task
            def extract_customer_data():
                return {"customers": [{"id": 1, "name": "Alice"}]}
            
            @task
            def extract_order_data():
                return {"orders": [{"id": 101, "customer_id": 1}]}
            
            [extract_customer_data(), extract_order_data()]
        
        @task_group
        def transform():
            @task
            def transform_data(ti):
                # 从嵌套任务组拉取XComs
                customer_data = ti.xcom_pull(task_ids='etl_pipeline.extract.extract_customer_data')
                order_data = ti.xcom_pull(task_ids='etl_pipeline.extract.extract_order_data')
                
                return {"customers": customer_data["customers"], "orders": order_data["orders"]}
            
            transform_data()
        
        extract() >> transform()
    
    etl_pipeline()
```

## 基于XComs的条件分支

### BranchPythonOperator与XComs

```python
from airflow.decorators import dag, task, branch
from airflow.operators.dummy import DummyOperator

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None)
def xcom_based_branching():
    
    @task
    def generate_data():
        return {"type": "csv", "size": 1000}
    
    @branch
    def choose_processor(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        data_type = data["type"]
        
        if data_type == "csv":
            return 'process_csv'
        elif data_type == "json":
            return 'process_json'
        else:
            return 'process_unknown'
    
    @task
    def process_csv(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        return {"processed": "csv", "records": data["size"]}
    
    @task
    def process_json(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        return {"processed": "json", "records": data["size"]}
    
    @task
    def process_unknown(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        return {"processed": "unknown", "records": 0}
    
    join = DummyOperator(task_id='join')
    
    generate_data() >> choose_processor() >> [
        process_csv(), 
        process_json(), 
        process_unknown()
    ] >> join
```

## XComs最佳实践

### 数据大小限制

```python
# 不推荐：传递大量数据
@task
def process_large_dataset():
    # 假设这是一个大型数据集
    large_data = fetch_large_dataset()  # 可能有几百MB
    return large_data  # 不推荐作为XCom传递

# 推荐：传递文件路径或引用
@task
def process_large_dataset():
    # 处理大型数据集
    large_data = fetch_large_dataset()
    
    # 保存到外部存储
    file_path = save_to_storage(large_data)
    
    # 只传递文件路径
    return {"file_path": file_path, "size": len(large_data)}

@task
def analyze_data(ti):
    # 获取文件路径
    result = ti.xcom_pull(task_ids='process_large_dataset')
    file_path = result["file_path"]
    
    # 从文件加载数据
    data = load_from_storage(file_path)
    
    # 分析数据
    return analyze(data)
```

### 清理XComs

```python
from airflow.models.xcom import XCom
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

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

cleanup_task = PythonOperator(
    task_id='cleanup_xcoms',
    python_callable=cleanup_xcoms
)
```

### XComs错误处理

```python
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException

@dag(start_date=datetime(2023, 1, 1), schedule_interval=None)
def xcom_error_handling():
    
    @task
    def push_data():
        return {"key": "value"}
    
    @task
    def pull_data_with_retry(ti, max_retries=3):
        retries = 0
        
        while retries < max_retries:
            try:
                data = ti.xcom_pull(task_ids='push_data')
                
                if not data:
                    raise ValueError("No data received")
                
                return data
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise AirflowException(f"Failed to pull XCom after {max_retries} retries: {str(e)}")
                
                # 等待一段时间后重试
                time.sleep(2 ** retries)  # 指数退避
    
    push_data() >> pull_data_with_retry()
```

## 常见问题解决

### XComs不显示

```python
# 确保任务返回了值
@task
def my_task():
    # 错误：没有返回值
    print("This won't be pushed as XCom")
    
    # 正确：返回值会被推送为XCom
    return {"status": "success"}

# 确保启用了XCom推送（对于BashOperator）
bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "some data"',
    xcom_push=True  # 必须设置为True
)
```

### XComs拉取失败

```python
# 检查任务ID是否正确
@task
def pull_data(ti):
    # 错误：任务ID不正确
    data = ti.xcom_pull(task_ids='non_existent_task')
    
    # 正确：使用正确的任务ID
    data = ti.xcom_pull(task_ids='push_data')
    
    # 检查XCom是否存在
    if not data:
        raise ValueError("No XCom found for task 'push_data'")
    
    return data
```

### Jinja模板渲染问题

```python
# 确保Jinja模板语法正确
bash_task = BashOperator(
    task_id='bash_task',
    # 错误：缺少引号
    bash_command='echo {{ ti.xcom_pull(task_ids="push_data") }}',
    
    # 正确：添加引号
    bash_command='echo "{{ ti.xcom_pull(task_ids="push_data") }}"',
    
    # 对于JSON数据，需要额外处理
    bash_command="""
    DATA="{{ ti.xcom_pull(task_ids='push_data') }}"
    echo "$DATA"
    """
)
```

## 有用命令

### 查看XComs

```bash
# 使用Airflow CLI查看XComs
airflow xcoms list --dag-id my_dag --task-id my_task

# 使用Airflow CLI获取特定XCom
airflow xcoms get --dag-id my_dag --task-id my_task --execution-date 2023-01-01
```

### 清理XComs

```bash
# 使用Airflow CLI清理XComs
airflow xcoms delete --dag-id my_dag --task-id my_task --execution-date 2023-01-01

# 清理所有XComs（谨慎使用）
airflow xcoms delete --all
```

---

这份快速参考提供了XComs和任务间通信的常用操作和最佳实践，可以作为日常开发时的参考手册。