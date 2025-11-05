# Day 5: 传感器与钩子快速参考

## 传感器(Sensors)快速参考

### 传感器基本语法

```python
from airflow.sensors.base import BaseSensorOperator

# 通用参数
sensor = SensorClass(
    task_id='sensor_task',
    poke_interval=30,      # 检查间隔(秒)，默认30秒
    timeout=600,           # 超时时间(秒)，默认7天
    mode='poke',           # 模式: 'poke' 或 'reschedule'
    soft_fail=False,       # 软失败，超时时不标记为失败
    exponential_backoff=True,  # 指数退避
    max_wait=3600,         # 最大等待时间(秒)
    # 其他特定参数...
)
```

### 传感器模式对比

| 特性 | Poke模式 | Reschedule模式 |
|------|----------|----------------|
| 工作方式 | 持续占用工作槽位 | 检查间隙释放工作槽位 |
| 适用场景 | 短时间等待(几分钟) | 长时间等待(几十分钟到几小时) |
| 资源消耗 | 高 | 低 |
| 响应速度 | 快 | 慢 |
| 默认模式 | 是 | 否 |

### 常用传感器类型

#### FileSensor - 文件系统传感器

```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file',              # 文件路径
    fs_conn_id='fs_default',               # 文件系统连接(可选)
    poke_interval=30,
    timeout=600,
    mode='poke',
)
```

#### SqlSensor - SQL传感器

```python
from airflow.providers.postgres.sensors.sql import SqlSensor

wait_for_data = SqlSensor(
    task_id='wait_for_data',
    conn_id='postgres_default',            # 数据库连接
    sql="SELECT COUNT(*) FROM table WHERE condition",  # SQL查询
    poke_interval=60,
    timeout=1800,
    mode='reschedule',
    check_success=lambda value: int(value[0][0]) > 0,  # 自定义成功条件
)
```

#### HttpSensor - HTTP传感器

```python
from airflow.providers.http.sensors.http import HttpSensor

wait_for_api = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='http_default',           # HTTP连接
    endpoint='api/health',                 # API端点
    request_params={},                     # 请求参数
    headers={},                            # 请求头
    response_check=lambda response: response.status_code == 200,  # 响应检查
    poke_interval=30,
    timeout=600,
    mode='poke',
)
```

#### TimeSensor - 时间传感器

```python
from airflow.sensors.time_sensor import TimeSensor, TimeDeltaSensor

# 等待特定时间点
wait_for_time = TimeSensor(
    task_id='wait_for_time',
    target_time=(datetime.now() + timedelta(hours=2)).time(),  # 目标时间
    mode='reschedule',
)

# 等待时间增量
wait_for_delta = TimeDeltaSensor(
    task_id='wait_for_delta',
    delta=timedelta(hours=1),              # 时间增量
    mode='reschedule',
)
```

#### ExternalTaskSensor - 外部任务传感器

```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_dag = ExternalTaskSensor(
    task_id='wait_for_dag',
    external_dag_id='upstream_dag',        # 外部DAG ID
    external_task_id='specific_task',      # 外部任务ID(可选)
    allowed_states=['success'],            # 允许的状态
    failed_states=['failed', 'skipped'],   # 失败的状态
    poke_interval=60,
    timeout=3600,
    mode='reschedule',
)
```

## 钩子(Hooks)快速参考

### 钩子基本语法

```python
from airflow.providers.{provider}.hooks.{hook_type} import HookClass

# 在Python操作符中使用钩子
def my_function(**context):
    # 创建钩子实例
    hook = HookClass(conn_id='connection_id')
    
    # 使用钩子方法
    result = hook.some_method()
    
    return result
```

### 常用钩子类型

#### PostgresHook - PostgreSQL钩子

```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

def process_data():
    # 创建钩子
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 执行查询
    records = postgres_hook.get_records("SELECT * FROM table")
    
    # 获取单条记录
    record = postgres_hook.get_first("SELECT * FROM table WHERE id = 1")
    
    # 执行无返回查询
    postgres_hook.run("UPDATE table SET column = 'value'")
    
    # 执行带参数查询
    postgres_hook.run(
        "INSERT INTO table (column1, column2) VALUES (%s, %s)",
        parameters=('value1', 'value2')
    )
    
    return len(records)
```

#### HttpHook - HTTP钩子

```python
from airflow.providers.http.hooks.http import HttpHook

def fetch_data():
    # 创建钩子
    http_hook = HttpHook(http_conn_id='http_default', method='GET')
    
    # 发送GET请求
    response = http_hook.run(endpoint='api/data')
    
    # 发送POST请求
    post_hook = HttpHook(http_conn_id='http_default', method='POST')
    post_response = post_hook.run(
        endpoint='api/submit',
        data={'key': 'value'},
        headers={'Content-Type': 'application/json'}
    )
    
    return response.json()
```

#### S3Hook - Amazon S3钩子

```python
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def process_s3_data():
    # 创建钩子
    s3_hook = S3Hook(aws_conn_id='aws_default')
    
    # 上传字符串
    s3_hook.load_string(
        string_data='Hello, S3!',
        key='test/file.txt',
        bucket_name='my-bucket',
        replace=True
    )
    
    # 上传文件
    s3_hook.load_file(
        filename='/tmp/local_file.txt',
        key='remote/file.txt',
        bucket_name='my-bucket',
        replace=True
    )
    
    # 下载文件
    s3_hook.download_file(
        key='remote/file.txt',
        bucket_name='my-bucket',
        local_path='/tmp/downloaded_file.txt'
    )
    
    # 检查键是否存在
    exists = s3_hook.check_for_key(
        key='remote/file.txt',
        bucket_name='my-bucket'
    )
    
    # 列出键
    keys = s3_hook.list_keys(
        bucket_name='my-bucket',
        prefix='data/'
    )
    
    return f"处理了 {len(keys)} 个文件"
```

#### SlackHook - Slack钩子

```python
from airflow.providers.slack.hooks.slack import SlackHook

def send_notification():
    # 创建钩子
    slack_hook = SlackHook(slack_conn_id='slack_default')
    
    # 发送消息
    slack_hook.call(
        method='chat.postMessage',
        json={
            'channel': '#general',
            'text': 'Hello from Airflow!',
            'username': 'Airflow Bot'
        }
    )
    
    return "通知已发送"
```

## 传感器与钩子结合模式

### 基本结合模式

```python
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator

# 传感器等待条件
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=30,
    timeout=600,
)

# 钩子处理数据
def process_data():
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 读取文件并处理
    with open('/tmp/data.csv', 'r') as f:
        # 处理文件内容
        pass
    
    # 使用钩子保存结果
    postgres_hook.run("INSERT INTO results (data) VALUES ('processed')")
    
    return "处理完成"

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
)

# 定义依赖关系
wait_for_file >> process_task
```

### 错误处理模式

```python
from airflow.operators.python import PythonOperator
from airflow.providers.slack.hooks.slack import SlackHook

def handle_sensor_failure(context):
    """处理传感器失败"""
    slack_hook = SlackHook(slack_conn_id='slack_default')
    
    task_instance = context['task_instance']
    dag_id = task_instance.dag_id
    task_id = task_instance.task_id
    
    slack_hook.call(
        method='chat.postMessage',
        json={
            'channel': '#alerts',
            'text': f'传感器失败: {dag_id}.{task_id}',
            'username': 'Airflow Alert'
        }
    )

# 使用on_failure_callback
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=30,
    timeout=600,
    on_failure_callback=handle_sensor_failure,
)
```

### 条件分支模式

```python
from airflow.operators.python import BranchPythonOperator

def choose_processing_path(**context):
    """根据数据选择处理路径"""
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 检查数据类型
    result = postgres_hook.get_first(
        "SELECT data_type FROM metadata WHERE date = %s",
        parameters=[context['ds']]
    )
    
    if result and result[0] == 'premium':
        return 'premium_processing'
    else:
        return 'standard_processing'

choose_path = BranchPythonOperator(
    task_id='choose_path',
    python_callable=choose_processing_path,
)

# 定义不同处理路径
premium_processing = PythonOperator(
    task_id='premium_processing',
    python_callable=lambda: "处理高级数据",
)

standard_processing = PythonOperator(
    task_id='standard_processing',
    python_callable=lambda: "处理标准数据",
)

# 定义依赖关系
wait_for_file >> choose_path >> [premium_processing, standard_processing]
```

## 最佳实践

### 传感器最佳实践

1. **选择合适的模式**:
   ```python
   # 短时间等待(几分钟内)使用poke模式
   short_wait_sensor = FileSensor(
       task_id='short_wait',
       filepath='/tmp/small_file.txt',
       poke_interval=10,
       timeout=60,
       mode='poke',
   )
   
   # 长时间等待(几十分钟到几小时)使用reschedule模式
   long_wait_sensor = SqlSensor(
       task_id='long_wait',
       sql="SELECT COUNT(*) FROM table WHERE ready = TRUE",
       poke_interval=300,
       timeout=3600,
       mode='reschedule',
   )
   ```

2. **设置合理的超时时间**:
   ```python
   # 避免无限等待
   sensor_with_timeout = FileSensor(
       task_id='sensor_with_timeout',
       filepath='/tmp/data.csv',
       timeout=3600,  # 1小时超时
   )
   ```

3. **优化检查间隔**:
   ```python
   # 平衡响应速度和资源消耗
   optimized_sensor = FileSensor(
       task_id='optimized_sensor',
       filepath='/tmp/data.csv',
       poke_interval=60,  # 适中的检查间隔
   )
   ```

4. **使用自定义检查函数**:
   ```python
   # 自定义成功条件
   custom_sensor = SqlSensor(
       task_id='custom_sensor',
       sql="SELECT status, count FROM table",
       check_success=lambda value: value[0][0] == 'ready' and int(value[0][1]) > 10,
   )
   ```

### 钩子最佳实践

1. **使用连接管理**:
   ```python
   # 在Airflow UI中配置连接，而不是硬编码
   postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
   ```

2. **错误处理**:
   ```python
   def safe_database_operation():
       try:
           postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
           result = postgres_hook.get_records("SELECT * FROM table")
           return result
       except Exception as e:
           print(f"数据库操作失败: {e}")
           raise
   ```

3. **批量操作**:
   ```python
   # 批量插入而非单条插入
   def batch_insert(data_list):
       postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
       
       # 准备批量插入数据
       values = [(item['id'], item['value']) for item in data_list]
       
       # 执行批量插入
       postgres_hook.insert_rows(
           table='target_table',
           rows=values,
           target_fields=['id', 'value']
       )
   ```

4. **资源管理**:
   ```python
   # 使用with语句确保资源释放
   def safe_s3_operation():
       s3_hook = S3Hook(aws_conn_id='aws_default')
       
       # 使用with语句确保连接关闭
       with s3_hook.get_conn() as conn:
           # 执行S3操作
           pass
   ```

## 常见问题与解决

### 传感器常见问题

1. **传感器卡住不继续**:
   - 检查超时设置
   - 确认条件是否可能满足
   - 检查自定义检查函数

2. **资源消耗过高**:
   - 切换到reschedule模式
   - 增加检查间隔
   - 减少并发传感器数量

3. **传感器失败处理**:
   - 使用on_failure_callback
   - 设置适当的重试策略
   - 考虑使用soft_fail参数

### 钩子常见问题

1. **连接失败**:
   - 检查连接配置
   - 验证网络访问
   - 确认认证信息

2. **权限问题**:
   - 检查用户权限
   - 使用最小权限原则
   - 验证资源访问权限

3. **性能问题**:
   - 使用批量操作
   - 优化查询
   - 考虑连接池

## 有用命令

### Airflow命令

```bash
# 列出所有DAG
airflow dags list

# 列出DAG的任务
airflow tasks list dag_id

# 测试任务
airflow tasks test dag_id task_id execution_date

# 暂停/取消暂停DAG
airflow dags pause dag_id
airflow dags unpause dag_id

# 触发DAG运行
airflow dags trigger dag_id

# 查看任务日志
airflow tasks log dag_id task_id execution_date
```

### 数据库命令

```bash
# 检查传感器状态
SELECT dag_id, task_id, state, execution_date 
FROM task_instance 
WHERE task_type = 'SensorOperator';

# 检查长时间运行的任务
SELECT dag_id, task_id, start_date, duration 
FROM task_instance 
WHERE state = 'running' 
ORDER BY start_date;
```

## 总结

这个快速参考指南提供了传感器和钩子的核心概念、语法和最佳实践。在实际使用中，请根据具体需求选择合适的传感器类型和模式，并遵循最佳实践以确保工作流的可靠性和效率。