# Day 5: 传感器与钩子故障排除指南

## 传感器故障排除

### 1. 传感器卡住不继续执行

#### 问题症状
- 传感器任务长时间处于"running"状态
- 下游任务不执行
- 工作流停滞

#### 可能原因
- 条件永远无法满足
- 超时时间设置过长
- 传感器模式选择不当
- 自定义检查函数有误

#### 解决方案

**检查条件是否可能满足**
```python
# 在测试环境中验证条件
def test_condition():
    # 模拟传感器检查条件
    import os
    file_exists = os.path.exists('/tmp/data.csv')
    print(f"文件存在: {file_exists}")
    return file_exists

# 在DAG中添加调试日志
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=30,
    timeout=300,  # 减少超时时间用于测试
    mode='poke',
)
```

**调整超时设置**
```python
# 设置合理的超时时间
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=30,
    timeout=1800,  # 30分钟超时
    mode='poke',
)
```

**切换传感器模式**
```python
# 对于长时间等待，使用reschedule模式
wait_for_data = SqlSensor(
    task_id='wait_for_data',
    sql="SELECT COUNT(*) FROM table WHERE ready = TRUE",
    poke_interval=300,  # 5分钟检查一次
    timeout=3600,       # 1小时超时
    mode='reschedule',  # 释放工作槽位
)
```

**验证自定义检查函数**
```python
# 添加日志到自定义检查函数
def debug_check_function(value):
    print(f"检查函数接收到的值: {value}")
    result = int(value[0][0]) > 0
    print(f"检查结果: {result}")
    return result

wait_for_data = SqlSensor(
    task_id='wait_for_data',
    sql="SELECT COUNT(*) FROM table WHERE ready = TRUE",
    check_success=debug_check_function,
)
```

### 2. 传感器资源消耗过高

#### 问题症状
- 工作槽位被长时间占用
- 系统资源使用率高
- 其他任务无法执行

#### 可能原因
- 使用poke模式进行长时间等待
- 检查间隔设置过短
- 并发传感器过多

#### 解决方案

**使用reschedule模式**
```python
# 将poke模式改为reschedule模式
wait_for_data = SqlSensor(
    task_id='wait_for_data',
    sql="SELECT COUNT(*) FROM table WHERE ready = TRUE",
    poke_interval=300,  # 5分钟检查一次
    timeout=3600,       # 1小时超时
    mode='reschedule',  # 释放工作槽位
)
```

**增加检查间隔**
```python
# 适当增加检查间隔
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=120,  # 从30秒增加到2分钟
    timeout=1800,
)
```

**限制并发传感器数量**
```python
# 在airflow.cfg中设置
# [core]
# max_active_tasks_per_dag = 3  # 限制每个DAG的并发任务数
```

### 3. 传感器频繁失败

#### 问题症状
- 传感器任务频繁进入"failed"状态
- 工作流执行中断
- 错误日志显示异常

#### 可能原因
- 网络连接问题
- 认证失败
- 资源不可访问
- 传感器配置错误

#### 解决方案

**添加重试机制**
```python
# 增加重试次数和间隔
wait_for_api = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='api_default',
    endpoint='api/health',
    poke_interval=60,
    timeout=1800,
    retries=3,  # 增加重试次数
    retry_delay=timedelta(minutes=5),  # 重试间隔
)
```

**使用软失败**
```python
# 使用soft_fail避免标记为失败
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=30,
    timeout=600,
    soft_fail=True,  # 超时不标记为失败
    mode='poke',
)
```

**添加错误处理**
```python
def handle_sensor_failure(context):
    """处理传感器失败"""
    from airflow.providers.slack.hooks.slack import SlackHook
    
    task_instance = context['task_instance']
    dag_id = task_instance.dag_id
    task_id = task_instance.task_id
    exception = context.get('exception')
    
    slack_hook = SlackHook(slack_conn_id='slack_default')
    slack_hook.call(
        method='chat.postMessage',
        json={
            'channel': '#alerts',
            'text': f'传感器失败: {dag_id}.{task_id}\n错误: {str(exception)}',
        }
    )

wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
    poke_interval=30,
    timeout=600,
    on_failure_callback=handle_sensor_failure,
)
```

### 4. 传感器条件检查不准确

#### 问题症状
- 传感器过早成功
- 传感器条件判断错误
- 下游任务接收错误数据

#### 可能原因
- SQL查询不准确
- 响应检查函数有误
- 条件逻辑错误

#### 解决方案

**验证SQL查询**
```python
# 在测试环境中验证SQL查询
def test_sql_query():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    records = postgres_hook.get_records(
        "SELECT COUNT(*) FROM table WHERE ready = TRUE"
    )
    
    print(f"查询结果: {records}")
    return records

# 使用更精确的SQL查询
wait_for_data = SqlSensor(
    task_id='wait_for_data',
    sql="""
        SELECT COUNT(*) 
        FROM table 
        WHERE ready = TRUE 
        AND created_date = '{{ ds }}'
    """,
    check_success=lambda value: int(value[0][0]) > 0,
)
```

**调试响应检查函数**
```python
# 添加详细日志到响应检查函数
def debug_response_check(response):
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"解析的JSON: {data}")
            return data.get('status') == 'ready'
        except ValueError:
            print("无法解析JSON")
            return False
    
    return False

wait_for_api = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='api_default',
    endpoint='api/health',
    response_check=debug_response_check,
)
```

## 钩子故障排除

### 1. 钩子连接失败

#### 问题症状
- 钩子操作失败
- 连接超时错误
- 认证失败错误

#### 可能原因
- 连接配置错误
- 网络问题
- 认证信息过期
- 服务不可用

#### 解决方案

**验证连接配置**
```python
# 测试连接
def test_connection():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = postgres_hook.get_conn()
        print("连接成功")
        conn.close()
        return True
    except Exception as e:
        print(f"连接失败: {e}")
        return False

# 在DAG中添加连接测试
test_conn_task = PythonOperator(
    task_id='test_connection',
    python_callable=test_connection,
)
```

**使用连接测试**
```python
# 使用钩子的测试连接方法
def test_hook_connection():
    from airflow.providers.http.hooks.http import HttpHook
    
    http_hook = HttpHook(http_conn_id='http_default')
    try:
        http_hook.test_connection()
        print("HTTP连接测试成功")
        return True
    except Exception as e:
        print(f"HTTP连接测试失败: {e}")
        return False
```

**添加连接重试**
```python
# 实现自定义连接重试逻辑
def connect_with_retry(hook_class, conn_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            hook = hook_class(conn_id=conn_id)
            hook.test_connection()
            print(f"连接成功，尝试次数: {attempt + 1}")
            return hook
        except Exception as e:
            print(f"连接失败，尝试次数: {attempt + 1}, 错误: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
    
    return None

# 在DAG中使用
def fetch_data_with_retry():
    http_hook = connect_with_retry(HttpHook, 'http_default')
    response = http_hook.run(endpoint='api/data')
    return response.json()
```

### 2. 钩子操作失败

#### 问题症状
- 钩子方法执行失败
- 数据操作错误
- 权限不足错误

#### 可能原因
- 操作参数错误
- 数据格式不匹配
- 权限不足
- 资源限制

#### 解决方案

**添加详细日志**
```python
def debug_database_operation():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    try:
        # 添加详细日志
        sql = "SELECT * FROM table WHERE id = %s"
        params = (1,)
        print(f"执行SQL: {sql}")
        print(f"参数: {params}")
        
        records = postgres_hook.get_records(sql, params)
        print(f"查询结果: {records}")
        
        return records
    except Exception as e:
        print(f"数据库操作失败: {e}")
        raise
```

**验证数据格式**
```python
def validate_data_before_insert(data):
    """验证数据格式"""
    if not isinstance(data, dict):
        raise ValueError("数据必须是字典格式")
    
    required_fields = ['id', 'name', 'value']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必需字段: {field}")
    
    return True

def safe_insert_data(data):
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    # 验证数据
    validate_data_before_insert(data)
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    try:
        postgres_hook.run(
            "INSERT INTO table (id, name, value) VALUES (%s, %s, %s)",
            parameters=(data['id'], data['name'], data['value'])
        )
        return "插入成功"
    except Exception as e:
        print(f"插入失败: {e}")
        raise
```

**处理权限问题**
```python
def check_permissions():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    try:
        # 检查表权限
        result = postgres_hook.get_records(
            "SELECT has_table_privilege(current_user, 'table_name', 'SELECT')"
        )
        print(f"SELECT权限: {result[0][0]}")
        
        result = postgres_hook.get_records(
            "SELECT has_table_privilege(current_user, 'table_name', 'INSERT')"
        )
        print(f"INSERT权限: {result[0][0]}")
        
        return True
    except Exception as e:
        print(f"权限检查失败: {e}")
        return False
```

### 3. 钩子性能问题

#### 问题症状
- 钩子操作执行缓慢
- 大量数据操作超时
- 内存使用过高

#### 可能原因
- 大量数据操作
- 未使用批量处理
- 查询未优化
- 连接池配置不当

#### 解决方案

**使用批量操作**
```python
def batch_insert_data(data_list):
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 准备批量数据
    batch_size = 1000
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i+batch_size]
        
        # 使用insert_rows进行批量插入
        postgres_hook.insert_rows(
            table='target_table',
            rows=batch,
            target_fields=['id', 'name', 'value']
        )
        
        print(f"已插入 {i+len(batch)} / {len(data_list)} 条记录")
    
    return f"批量插入完成，共 {len(data_list)} 条记录"
```

**优化查询**
```python
def optimized_query():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 使用索引和限制优化查询
    sql = """
        SELECT id, name, value 
        FROM large_table 
        WHERE created_date >= %s 
        AND status = 'active'
        ORDER BY id
        LIMIT 10000
    """
    
    records = postgres_hook.get_records(
        sql,
        parameters=('2023-01-01',)
    )
    
    return records
```

**使用连接池**
```python
# 在airflow.cfg中配置连接池
# [core]
# sql_engine_pool_size = 5
# sql_engine_max_overflow = 10

# 在钩子中使用连接池
def use_connection_pool():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 使用with语句确保连接正确释放
    with postgres_hook.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table")
        results = cursor.fetchall()
        
    return results
```

## 传感器与钩子集成问题

### 1. 数据传递问题

#### 问题症状
- 传感器检查条件但钩子无法访问数据
- 数据格式不匹配
- 数据丢失

#### 解决方案

**使用XComs传递数据**
```python
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

def extract_file_info(**context):
    """提取文件信息并通过XComs传递"""
    import os
    
    file_path = '/tmp/data.csv'
    file_info = {
        'path': file_path,
        'size': os.path.getsize(file_path),
        'modified': os.path.getmtime(file_path)
    }
    
    # 通过XComs传递数据
    return file_info

wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
)

extract_info = PythonOperator(
    task_id='extract_info',
    python_callable=extract_file_info,
)

def process_with_hook(**context):
    """使用钩子处理数据"""
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    # 从XComs获取数据
    file_info = context['task_instance'].xcom_pull(task_ids='extract_info')
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 使用文件信息
    postgres_hook.run(
        "INSERT INTO file_log (path, size, modified) VALUES (%s, %s, %s)",
        parameters=(file_info['path'], file_info['size'], file_info['modified'])
    )
    
    return "处理完成"

process_data = PythonOperator(
    task_id='process_data',
    python_callable=process_with_hook,
)

wait_for_file >> extract_info >> process_data
```

### 2. 时序问题

#### 问题症状
- 传感器条件满足但数据尚未准备好
- 钩子操作时数据不一致
- 竞态条件

#### 解决方案

**添加延迟**
```python
from airflow.operators.timedelta import TimeDeltaSensor

# 在传感器和钩子之间添加延迟
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/tmp/data.csv',
)

add_delay = TimeDeltaSensor(
    task_id='add_delay',
    delta=timedelta(minutes=5),  # 5分钟延迟
)

process_data = PythonOperator(
    task_id='process_data',
    python_callable=process_with_hook,
)

wait_for_file >> add_delay >> process_data
```

**使用事务**
```python
def transactional_operation():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    try:
        # 开始事务
        postgres_hook.run("BEGIN")
        
        # 检查条件
        result = postgres_hook.get_records(
            "SELECT COUNT(*) FROM table WHERE ready = TRUE FOR UPDATE"
        )
        
        if int(result[0][0]) > 0:
            # 处理数据
            postgres_hook.run("UPDATE table SET processed = TRUE WHERE ready = TRUE")
            postgres_hook.run("COMMIT")
            return "处理成功"
        else:
            postgres_hook.run("ROLLBACK")
            return "没有可处理的数据"
            
    except Exception as e:
        postgres_hook.run("ROLLBACK")
        raise e
```

## 调试技巧

### 1. 使用日志

```python
import logging

# 设置详细日志
logger = logging.getLogger(__name__)

def debug_function():
    logger.info("开始执行函数")
    
    try:
        # 操作代码
        result = some_operation()
        logger.info(f"操作成功，结果: {result}")
        return result
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        raise
```

### 2. 使用临时任务

```python
# 添加临时调试任务
def debug_sensor_condition():
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # 模拟传感器条件检查
    records = postgres_hook.get_records("SELECT COUNT(*) FROM table WHERE ready = TRUE")
    count = int(records[0][0])
    
    print(f"当前满足条件的记录数: {count}")
    print(f"条件是否满足: {count > 0}")
    
    return count > 0

debug_task = PythonOperator(
    task_id='debug_sensor_condition',
    python_callable=debug_sensor_condition,
)
```

### 3. 使用Airflow CLI

```bash
# 测试特定任务
airflow tasks test dag_id task_id execution_date

# 查看任务日志
airflow tasks log dag_id task_id execution_date

# 列出DAG的任务
airflow tasks list dag_id

# 检查DAG状态
airflow dags state dag_id execution_date
```

## 总结

传感器和钩子是Airflow工作流中的关键组件，但它们也可能成为故障点。通过理解常见问题和解决方案，你可以更有效地诊断和解决问题：

1. **传感器问题**:
   - 卡住不继续：检查条件、超时设置和模式选择
   - 资源消耗高：使用reschedule模式和增加检查间隔
   - 频繁失败：添加重试机制和错误处理
   - 条件检查不准确：验证查询和检查函数

2. **钩子问题**:
   - 连接失败：验证连接配置和网络
   - 操作失败：添加详细日志和数据验证
   - 性能问题：使用批量操作和优化查询

3. **集成问题**:
   - 数据传递：使用XComs和验证数据格式
   - 时序问题：添加延迟和使用事务

4. **调试技巧**:
   - 使用详细日志
   - 添加临时调试任务
   - 使用Airflow CLI工具

通过系统化的故障排除方法，你可以快速定位和解决传感器与钩子相关的问题，确保Airflow工作流的稳定运行。