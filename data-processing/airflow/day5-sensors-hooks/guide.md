# Day 5: 传感器与钩子学习指南

## 概述

在Airflow中，传感器(Sensors)和钩子(Hooks)是构建强大工作流的关键组件。传感器用于等待特定条件满足，而钩子则提供了与外部系统交互的接口。本指南将详细介绍如何有效使用这些组件。

## 传感器(Sensors)详解

### 1. 传感器的基本概念

传感器是一种特殊类型的操作符，它会定期检查某个条件是否满足，只有条件满足时才会继续执行下游任务。这对于构建事件驱动的工作流至关重要。

### 2. 传感器的两种工作模式

#### Poke模式
- **特点**: 传感器持续占用工作槽位，定期检查条件
- **适用场景**: 短时间等待，检查间隔短
- **资源消耗**: 持续占用工作槽位，资源消耗较高

```python
# Poke模式示例
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file',
    poke_interval=30,  # 每30秒检查一次
    timeout=600,      # 最大等待时间10分钟
    mode='poke',      # 显式指定poke模式
)
```

#### Reschedule模式
- **特点**: 传感器在两次检查之间释放工作槽位
- **适用场景**: 长时间等待，检查间隔较长
- **资源消耗**: 仅在检查时占用工作槽位，资源消耗较低

```python
# Reschedule模式示例
wait_for_data = SqlSensor(
    task_id='wait_for_data',
    conn_id='postgres_default',
    sql="SELECT COUNT(*) FROM table WHERE date = '{{ ds }}'",
    poke_interval=300,  # 每5分钟检查一次
    timeout=3600,       # 最大等待时间1小时
    mode='reschedule',  # 显式指定reschedule模式
)
```

### 3. 常用传感器类型

#### 文件系统传感器(FileSensor)
等待文件或目录出现：

```python
from airflow.sensors.filesystem import FileSensor

wait_for_data_file = FileSensor(
    task_id='wait_for_data_file',
    filepath='/data/{{ ds }}/processed_data.csv',
    fs_conn_id='fs_default',  # 可选，用于远程文件系统
    poke_interval=30,
    timeout=600,
)
```

#### SQL传感器(SqlSensor)
等待数据库中满足特定条件：

```python
from airflow.providers.postgres.sensors.sql import SqlSensor

wait_for_records = SqlSensor(
    task_id='wait_for_records',
    conn_id='postgres_default',
    sql="SELECT COUNT(*) FROM records WHERE status = 'ready'",
    poke_interval=60,
    timeout=1800,
    # 自定义成功条件
    check_success=lambda value: int(value[0][0]) > 0,
)
```

#### HTTP传感器(HttpSensor)
等待HTTP端点满足条件：

```python
from airflow.providers.http.sensors.http import HttpSensor

wait_for_api = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='api_default',
    endpoint='api/health',
    # 自定义响应检查
    response_check=lambda response: response.status_code == 200 and response.json()['status'] == 'ready',
    poke_interval=30,
    timeout=600,
)
```

#### 时间传感器(TimeSensor)
等待特定时间点：

```python
from airflow.sensors.time_sensor import TimeSensor

wait_for_business_hours = TimeSensor(
    task_id='wait_for_business_hours',
    target_time=(datetime.now() + timedelta(hours=2)).time(),
    mode='reschedule',
)
```

#### 外部任务传感器(ExternalTaskSensor)
等待另一个DAG或任务完成：

```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_upstream',
    external_dag_id='upstream_dag',
    external_task_id='final_task',  # 可选，默认等待整个DAG
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    mode='reschedule',
    poke_interval=60,
    timeout=3600,
)
```

### 4. 传感器最佳实践

1. **选择合适的模式**:
   - 短时间等待(几分钟内)使用poke模式
   - 长时间等待(几十分钟到几小时)使用reschedule模式

2. **设置合理的超时时间**:
   - 避免无限等待
   - 根据业务需求设置合理的超时时间

3. **优化检查间隔**:
   - 平衡响应速度和资源消耗
   - 避免过于频繁的检查

4. **使用自定义检查函数**:
   - 对于复杂条件，使用`check_success`或`response_check`参数

5. **错误处理**:
   - 设置适当的重试策略
   - 考虑添加失败时的通知机制

## 钩子(Hooks)详解

### 1. 钩子的基本概念

钩子是Airflow与外部系统交互的接口抽象。它们封装了与特定系统通信的细节，使DAG代码更加简洁和可维护。

### 2. 常用钩子类型

#### 数据库钩子
- **PostgresHook**: 与PostgreSQL数据库交互
- **MySqlHook**: 与MySQL数据库交互
- **SqliteHook**: 与SQLite数据库交互
- **OracleHook**: 与Oracle数据库交互

#### 云服务钩子
- **S3Hook**: 与Amazon S3交互
- **GCSHook**: 与Google Cloud Storage交互
- **AzureBlobStorageHook**: 与Azure Blob Storage交互

#### API钩子
- **HttpHook**: 与HTTP API交互
- **SlackHook**: 与Slack API交互
- **JiraHook**: 与Jira API交互

#### 其他钩子
- **EmailHook**: 发送邮件
- **SFTPHook**: 与SFTP服务器交互
- **DockerHook**: 与Docker交互

### 3. 钩子的使用方式

#### 在Python操作符中使用钩子
```python
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator

def extract_data(**context):
    # 创建钩子实例
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 执行查询
    records = postgres_hook.get_records(
        "SELECT * FROM source_table WHERE date = %s",
        parameters=[context['ds']]
    )
    
    # 处理数据
    # ...
    
    return len(records)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
)
```

#### 使用预定义的钩子操作符
```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

create_table = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='postgres_default',
    sql="""
        CREATE TABLE IF NOT EXISTS target_table (
            id SERIAL PRIMARY KEY,
            data VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
)
```

### 4. 钩子最佳实践

1. **使用连接管理**:
   - 在Airflow UI中配置连接，而不是在代码中硬编码凭证
   - 使用变量存储敏感信息

2. **错误处理**:
   - 实现适当的错误处理和重试逻辑
   - 考虑使用try-except块处理特定异常

3. **资源管理**:
   - 确保钩子资源正确释放
   - 对于长时间运行的任务，考虑使用连接池

4. **性能优化**:
   - 批量操作而非单条记录操作
   - 使用适当的索引和查询优化

5. **安全性**:
   - 避免在代码中存储敏感信息
   - 使用最小权限原则配置连接

## 传感器与钩子的结合应用

### 1. 典型场景

#### 数据管道工作流
1. 传感器等待数据源就绪
2. 使用钩子提取数据
3. 处理数据
4. 使用钩子加载到目标系统
5. 使用钩子发送通知

#### API集成工作流
1. 传感器等待外部API可用
2. 使用钩子获取数据
3. 处理数据
4. 使用钩子发送结果

#### 文件处理工作流
1. 传感器等待文件出现
2. 使用钩子读取文件
3. 处理文件内容
4. 使用钩子移动/归档文件

### 2. 高级模式

#### 传感器链
```python
# 多个传感器串联，等待多个条件
wait_for_file = FileSensor(task_id='wait_for_file', filepath='/data/input.csv')
wait_for_db = SqlSensor(task_id='wait_for_db', sql="SELECT COUNT(*) FROM table WHERE ready = TRUE")
wait_for_api = HttpSensor(task_id='wait_for_api', endpoint='api/status')

# 所有条件满足后才继续处理
process_data = BashOperator(task_id='process_data', bash_command='python process.py')

wait_for_file >> wait_for_db >> wait_for_api >> process_data
```

#### 传感器分支
```python
# 基于不同条件选择不同处理路径
from airflow.operators.python import BranchPythonOperator

def choose_processing_path(**context):
    # 使用钩子检查数据类型
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    result = postgres_hook.get_first("SELECT data_type FROM metadata WHERE date = %s", parameters=[context['ds']])
    
    if result and result[0] == 'premium':
        return 'premium_processing'
    else:
        return 'standard_processing'

choose_path = BranchPythonOperator(
    task_id='choose_path',
    python_callable=choose_processing_path,
)

premium_processing = BashOperator(task_id='premium_processing', bash_command='python premium_process.py')
standard_processing = BashOperator(task_id='standard_processing', bash_command='python standard_process.py')

choose_path >> [premium_processing, standard_processing]
```

#### 传感器与钩子的错误处理
```python
def handle_sensor_failure(**context):
    # 使用钩子发送错误通知
    slack_hook = SlackHook(slack_conn_id='slack_default')
    slack_hook.call(
        method='chat.postMessage',
        json={
            'channel': '#alerts',
            'text': f"传感器超时: {context['task_instance'].task_id}"
        }
    )

# 使用on_failure_callback处理传感器失败
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input.csv',
    timeout=600,
    on_failure_callback=handle_sensor_failure,
)
```

## 实践练习

### 练习1: 基本传感器使用
创建一个DAG，使用FileSensor等待文件出现，然后使用BashOperator处理该文件。

### 练习2: SQL传感器与钩子结合
创建一个DAG，使用SqlSensor等待数据库中有新数据，然后使用PostgresHook处理这些数据。

### 练习3: HTTP传感器与钩子结合
创建一个DAG，使用HttpSensor等待API可用，然后使用HttpHook获取数据并处理。

### 练习4: 多传感器工作流
创建一个DAG，使用多个传感器等待不同条件，所有条件满足后执行处理任务。

### 练习5: 传感器分支工作流
创建一个DAG，使用传感器检查数据，然后根据数据类型选择不同的处理路径。

## 总结

传感器和钩子是构建强大Airflow工作流的关键组件：

1. **传感器**:
   - 用于等待特定条件满足
   - 支持poke和reschedule两种工作模式
   - 提供多种类型满足不同需求

2. **钩子**:
   - 提供与外部系统交互的接口
   - 封装了通信细节，简化代码
   - 支持多种系统和协议

3. **最佳实践**:
   - 根据场景选择合适的传感器模式
   - 合理设置超时时间和检查间隔
   - 使用连接管理而非硬编码凭证
   - 实现适当的错误处理和重试逻辑

通过掌握传感器和钩子的使用，你可以构建更加智能和可靠的数据工作流，实现与外部系统的无缝集成。