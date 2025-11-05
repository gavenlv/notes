# Day 2 快速参考指南

## DAG基本结构

### 创建DAG

```python
from datetime import datetime, timedelta
from airflow import DAG

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_dag',  # DAG ID
    default_args=default_args,
    description='我的DAG描述',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example'],
)
```

### 常用DAG参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `dag_id` | DAG的唯一标识符 | `'my_dag'` |
| `description` | DAG描述 | `'我的DAG描述'` |
| `schedule_interval` | 调度间隔 | `timedelta(days=1)` 或 `'@daily'` |
| `start_date` | 开始日期 | `datetime(2023, 1, 1)` |
| `end_date` | 结束日期 | `datetime(2023, 12, 31)` |
| `catchup` | 是否补跑历史数据 | `False` |
| `tags` | 标签列表 | `['example', 'data']` |
| `max_active_runs` | 最大同时运行数 | `1` |
| `max_active_tasks` | 最大同时任务数 | `16` |

### 调度间隔格式

```python
# 使用timedelta对象
schedule_interval=timedelta(days=1)  # 每天运行
schedule_interval=timedelta(hours=2)  # 每2小时运行
schedule_interval=timedelta(minutes=30)  # 每30分钟运行

# 使用预设字符串
schedule_interval='@daily'  # 每天午夜运行
schedule_interval='@weekly'  # 每周午夜运行
schedule_interval='@monthly'  # 每月第一天午夜运行
schedule_interval='@yearly'  # 每年1月1日午夜运行
schedule_interval='@hourly'  # 每小时运行

# 使用cron表达式
schedule_interval='0 3 * * *'  # 每天凌晨3点运行
schedule_interval='0 0 * * 0'  # 每周日午夜运行

# 不调度（手动触发）
schedule_interval=None
```

## 任务定义

### 常用操作符

#### BashOperator

```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World!"',
    dag=dag,
)
```

#### PythonOperator

```python
from airflow.operators.python import PythonOperator

def python_function():
    """Python函数示例"""
    return "Hello from Python!"

task = PythonOperator(
    task_id='python_task',
    python_callable=python_function,
    dag=dag,
)
```

#### EmailOperator

```python
from airflow.operators.email import EmailOperator

task = EmailOperator(
    task_id='email_task',
    to='recipient@example.com',
    subject='Airflow Alert',
    html_content='<h3>DAG completed successfully</h3>',
    dag=dag,
)
```

#### HttpOperator

```python
from airflow.providers.http.operators.http import HttpOperator

task = HttpOperator(
    task_id='http_task',
    http_conn_id='http_default',
    endpoint='api/v1/data',
    method='GET',
    dag=dag,
)
```

#### SqlOperator

```python
from airflow.providers.common.sql.operators.sql import SqlOperator

task = SqlOperator(
    task_id='sql_task',
    sql='SELECT * FROM table',
    conn_id='my_db_conn',
    dag=dag,
)
```

#### BranchPythonOperator

```python
from airflow.operators.python import BranchPythonOperator

def branch_function():
    """分支函数"""
    return 'task_a'  # 返回要执行的任务ID

task = BranchPythonOperator(
    task_id='branch_task',
    python_callable=branch_function,
    dag=dag,
)
```

### 任务参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `task_id` | 任务的唯一标识符 | `'my_task'` |
| `owner` | 任务所有者 | `'airflow'` |
| `retries` | 重试次数 | `3` |
| `retry_delay` | 重试延迟 | `timedelta(minutes=5)` |
| `email_on_failure` | 失败时是否发送邮件 | `True` |
| `email` | 通知邮箱 | `['airflow@example.com']` |
| `queue` | 队列 | `'default'` |
| `pool` | 资源池 | `'default_pool'` |
| `priority_weight` | 优先级权重 | `1` |
| `execution_timeout` | 执行超时 | `timedelta(hours=1)` |
| `trigger_rule` | 触发规则 | `'all_success'` |

## 任务依赖关系

### 设置依赖关系

```python
# 使用>>操作符
task1 >> task2 >> task3

# 使用<<操作符
task4 << task3

# 使用set_upstream和set_downstream方法
task5.set_upstream(task4)
task6.set_downstream(task5)

# 设置多个依赖
task7.set_upstream([task5, task6])
# 或者
[task5, task6] >> task7
```

### 触发规则

| 触发规则 | 描述 |
|----------|------|
| `'all_success'` | 所有上游任务成功 |
| `'all_failed'` | 所有上游任务失败 |
| `'all_done'` | 所有上游任务完成（无论成功或失败） |
| `'one_success'` | 至少一个上游任务成功 |
| `'one_failed'` | 至少一个上游任务失败 |
| `'none_failed'` | 没有上游任务失败 |
| `'none_failed_or_skipped'` | 没有上游任务失败或跳过 |

## XComs（任务间通信）

### 推送XCom值

```python
from airflow.operators.python import PythonOperator

def push_function(**kwargs):
    """推送XCom值的函数"""
    value = "要传递的值"
    kwargs['ti'].xcom_push(key='my_key', value=value)
    return value

task = PythonOperator(
    task_id='push_task',
    python_callable=push_function,
    dag=dag,
)
```

### 拉取XCom值

```python
def pull_function(**kwargs):
    """拉取XCom值的函数"""
    ti = kwargs['ti']
    value = ti.xcom_pull(task_ids='push_task', key='my_key')
    print(f"拉取的值: {value}")
    return value

task = PythonOperator(
    task_id='pull_task',
    python_callable=pull_function,
    dag=dag,
)
```

### 在BashOperator中使用XCom

```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='bash_pull',
    bash_command='echo "从Python任务获取的值: {{ ti.xcom_pull(task_ids=\'push_task\') }}"',
    dag=dag,
)
```

## Jinja模板

### 常用宏变量

| 宏变量 | 描述 | 示例 |
|--------|------|------|
| `{{ ds }}` | 执行日期 | `'2023-01-01'` |
| `{{ ds_nodash }}` | 无分隔符的执行日期 | `'20230101'` |
| `{{ ts }}` | 执行时间戳 | `'2023-01-01T00:00:00+00:00'` |
| `{{ ts_nodash }}` | 无分隔符的执行时间戳 | `'20230101T000000'` |
| `{{ prev_ds }}` | 上一次执行日期 | `'2022-12-31'` |
| `{{ next_ds }}` | 下一次执行日期 | `'2023-01-02'` |
| `{{ data_interval_start }}` | 数据间隔开始 | `'2023-01-01T00:00:00+00:00'` |
| `{{ data_interval_end }}` | 数据间隔结束 | `'2023-01-02T00:00:00+00:00'` |
| `{{ logical_date }}` | 逻辑日期 | `'2023-01-01T00:00:00+00:00'` |
| `{{ task_instance_key_str }}` | 任务实例键字符串 | `'my_dag__push_task__20230101'` |

### 在任务中使用模板

```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='templated_task',
    bash_command="""
    echo "执行日期: {{ ds }}"
    echo "数据间隔: {{ data_interval_start }} 到 {{ data_interval_end }}"
    echo "任务实例: {{ task_instance_key_str }}"
    """,
    dag=dag,
)
```

## 动态任务生成

### 使用循环创建任务

```python
from airflow.operators.bash import BashOperator

# 数据类型列表
data_types = ['user', 'order', 'product', 'inventory']

# 动态创建任务
tasks = []
for data_type in data_types:
    task = BashOperator(
        task_id=f'process_{data_type}',
        bash_command=f'echo "处理 {data_type} 数据"',
        dag=dag,
    )
    tasks.append(task)

# 设置依赖关系
for i in range(len(tasks) - 1):
    tasks[i] >> tasks[i + 1]
```

### 使用函数创建任务

```python
def create_processing_task(data_type, dag):
    """创建处理任务的辅助函数"""
    return BashOperator(
        task_id=f'process_{data_type}',
        bash_command=f'echo "处理 {data_type} 数据"',
        dag=dag,
    )

# 使用函数创建任务
user_task = create_processing_task('user', dag)
order_task = create_processing_task('order', dag)

# 设置依赖关系
user_task >> order_task
```

## 错误处理和重试

### 设置重试策略

```python
task = BashOperator(
    task_id='unstable_task',
    bash_command='unstable_command.sh',
    retries=3,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(hours=1),
    dag=dag,
)
```

### 设置回调函数

```python
def failure_callback(context):
    """失败回调函数"""
    print(f"任务 {context['task_instance'].task_id} 失败")
    # 可以发送通知或记录日志

def success_callback(context):
    """成功回调函数"""
    print(f"任务 {context['task_instance'].task_id} 成功")

task = BashOperator(
    task_id='callback_task',
    bash_command='echo "Hello World!"',
    on_failure_callback=failure_callback,
    on_success_callback=success_callback,
    dag=dag,
)
```

## 条件分支

### 使用BranchPythonOperator

```python
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator

def branch_function(**kwargs):
    """分支函数"""
    ti = kwargs['ti']
    # 可以从XCom获取值
    condition = ti.xcom_pull(task_ids='previous_task')
    
    if condition:
        return 'branch_a'
    else:
        return 'branch_b'

branch_task = BranchPythonOperator(
    task_id='branch_task',
    python_callable=branch_function,
    dag=dag,
)

# 分支任务
branch_a = DummyOperator(task_id='branch_a', dag=dag)
branch_b = DummyOperator(task_id='branch_b', dag=dag)

# 合并分支
join_task = DummyOperator(
    task_id='join',
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)

# 设置依赖关系
branch_task >> [branch_a, branch_b] >> join_task
```

## DAG最佳实践

### 代码组织

```python
# 导入语句
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# 常量定义
DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 函数定义
def process_data():
    """处理数据的函数"""
    # 处理逻辑
    pass

# DAG定义
dag = DAG(
    'well_structured_dag',
    default_args=DEFAULT_ARGS,
    description='结构良好的DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example'],
)

# 任务定义
task1 = BashOperator(
    task_id='task1',
    bash_command='echo "Task 1"',
    dag=dag,
)

task2 = PythonOperator(
    task_id='task2',
    python_callable=process_data,
    dag=dag,
)

# 依赖关系设置
task1 >> task2
```

### 文档和注释

```python
"""
DAG文档字符串
描述DAG的目的、功能和数据流
"""

def process_data():
    """
    处理数据的函数
    
    这个函数负责处理输入数据，执行以下操作：
    1. 清洗数据
    2. 转换数据格式
    3. 验证数据质量
    
    Returns:
        bool: 处理是否成功
    """
    # 函数实现
    pass

task = PythonOperator(
    task_id='documented_task',
    python_callable=process_data,
    # 任务文档
    doc_md="""
    ## 任务文档
    
    这个任务负责处理数据，包括：
    - 数据清洗
    - 数据转换
    - 数据验证
    
    ### 依赖
    - 需要上游任务提供原始数据
    - 输出处理后的数据给下游任务
    """,
    dag=dag,
)
```

## 常见问题解决

### DAG不显示在UI中

1. 检查DAG文件语法是否正确
2. 确认DAG文件在正确的DAGs文件夹中
3. 检查Airflow配置中的DAGs文件夹路径
4. 查看Airflow日志中的错误信息

### 任务失败

1. 检查任务日志中的错误信息
2. 确认任务所需的依赖和资源是否可用
3. 检查任务执行环境
4. 增加重试次数或调整重试延迟

### 任务不执行

1. 检查DAG是否已启用（未暂停）
2. 确认调度间隔设置是否正确
3. 检查开始日期是否在未来
4. 确认上游任务是否成功完成

## 有用的命令

```bash
# 列出所有DAG
airflow dags list

# 列出特定DAG的任务
airflow tasks list my_dag

# 触发DAG运行
airflow dags trigger my_dag

# 暂停DAG
airflow dags pause my_dag

# 取消暂停DAG
airflow dags unpause my_dag

# 测试任务
airflow tasks test my_dag my_task 2023-01-01

# 清空DAG状态
airflow dags clear my_dag

# 检查DAG文件语法
python -m py_compile my_dag_file.py
```

## 学习资源

- [Airflow官方文档](https://airflow.apache.org/docs/apache-airflow/stable/)
- [Airflow DAG示例](https://github.com/apache/airflow/tree/main/airflow/example_dags)
- [Airflow最佳实践](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)