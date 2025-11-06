# Day 5: 传感器与钩子练习题

## 基础练习

### 练习1: 基本文件传感器
创建一个DAG，使用FileSensor等待特定文件出现，然后使用BashOperator处理该文件。

**要求**:
- 使用FileSensor等待`/tmp/data/input.csv`文件出现
- 设置合理的poke_interval和timeout
- 文件出现后，使用BashOperator执行一个简单的处理脚本
- 添加适当的错误处理

**提示**:
- 考虑使用PythonOperator创建测试文件，以便测试
- 可以使用BashOperator的`trigger_rule`参数处理超时情况

### 练习2: SQL传感器与钩子结合
创建一个DAG，使用SqlSensor等待数据库中有新数据，然后使用PostgresHook处理这些数据。

**要求**:
- 使用SqlSensor检查数据库中是否有未处理的数据
- 使用PostgresHook获取未处理的数据
- 处理数据并更新状态
- 将处理结果保存到另一个表

**提示**:
- 可以先创建一个示例表并插入测试数据
- 使用PythonOperator结合PostgresHook处理数据

### 练习3: HTTP传感器与钩子结合
创建一个DAG，使用HttpSensor等待API可用，然后使用HttpHook获取数据并处理。

**要求**:
- 使用HttpSensor检查API健康状态
- 使用HttpHook获取数据
- 处理获取的数据（例如，提取特定字段）
- 将处理结果保存到文件或数据库

**提示**:
- 可以使用公共API（如JSONPlaceholder）进行测试
- 考虑使用response_check参数自定义健康检查

### 练习4: 时间传感器应用
创建一个DAG，使用TimeSensor等待特定时间点，然后执行任务。

**要求**:
- 使用TimeSensor等待当前时间后的特定时间点（例如1小时后）
- 在等待时间点后执行一个处理任务
- 使用reschedule模式优化资源使用

**提示**:
- 注意TimeSensor的target_time参数格式
- 考虑使用动态计算目标时间

### 练习5: 外部任务传感器
创建一个DAG，使用ExternalTaskSensor等待另一个DAG完成。

**要求**:
- 创建两个DAG：上游DAG和下游DAG
- 下游DAG使用ExternalTaskSensor等待上游DAG完成
- 上游DAG完成后，下游DAG执行处理任务

**提示**:
- 确保两个DAG的start_date设置正确
- 考虑设置合理的allowed_states和failed_states

## 进阶练习

### 练习6: 传感器模式比较
创建一个DAG，比较poke模式和reschedule模式的差异。

**要求**:
- 创建两个相似的传感器任务，一个使用poke模式，一个使用reschedule模式
- 设置相同的等待时间和检查间隔
- 添加日志记录，观察两种模式的资源使用情况
- 分析两种模式的适用场景

**提示**:
- 可以使用PythonOperator记录资源使用情况
- 考虑使用Airflow的日志系统分析差异

### 练习7: 多条件传感器链
创建一个DAG，使用多个传感器等待不同条件，所有条件满足后执行处理任务。

**要求**:
- 至少使用3种不同类型的传感器（如FileSensor、SqlSensor、HttpSensor）
- 所有传感器条件满足后才执行处理任务
- 添加适当的错误处理和超时机制
- 实现条件满足时的通知机制

**提示**:
- 考虑使用PythonOperator创建满足条件的资源
- 可以使用SlackHook或EmailHook发送通知

### 练习8: 动态传感器创建
创建一个DAG，根据配置动态创建多个传感器任务。

**要求**:
- 使用配置文件或变量定义要监控的资源列表
- 根据配置动态创建多个传感器任务
- 所有传感器条件满足后执行处理任务
- 支持配置更新后自动调整传感器任务

**提示**:
- 可以使用PythonOperator动态生成任务
- 考虑使用Airflow的变量存储配置

### 练习9: 传感器与钩子错误处理
创建一个DAG，实现传感器和钩子的全面错误处理。

**要求**:
- 为传感器任务添加超时和失败处理
- 为钩子操作添加重试和错误处理
- 实现错误时的通知机制
- 记录错误日志和恢复策略

**提示**:
- 使用on_failure_callback处理传感器失败
- 考虑使用try-except块处理钩子异常

### 练习10: 传感器性能优化
创建一个DAG，优化传感器的性能和资源使用。

**要求**:
- 分析不同传感器模式的资源消耗
- 优化检查间隔和超时设置
- 实现智能检查策略（例如，指数退避）
- 监控和记录传感器性能指标

**提示**:
- 可以使用PythonOperator实现自定义检查逻辑
- 考虑使用Airflow的监控功能

## 挑战练习

### 练习11: 分布式传感器系统
设计并实现一个分布式传感器系统，监控多个数据源。

**要求**:
- 支持监控多种类型的数据源（文件、数据库、API等）
- 实现分布式传感器协调机制
- 提供传感器状态监控和管理界面
- 支持动态添加和移除传感器

**提示**:
- 考虑使用消息队列协调传感器
- 可以使用Airflow的REST API管理传感器

### 练习12: 智能传感器框架
创建一个智能传感器框架，根据历史数据优化传感器行为。

**要求**:
- 收集和分析传感器历史数据
- 实现基于机器学习的预测模型
- 根据预测结果动态调整传感器参数
- 提供传感器性能分析和优化建议

**提示**:
- 可以使用Python的机器学习库
- 考虑使用Airflow的XComs传递分析结果

### 练习13: 传感器与钩子集成平台
设计一个传感器与钩子集成平台，简化复杂工作流的构建。

**要求**:
- 提供图形化界面设计传感器和钩子工作流
- 支持拖拽式工作流设计
- 实现工作流模板和复用机制
- 提供工作流执行监控和调试功能

**提示**:
- 可以使用前端框架构建界面
- 考虑使用Airflow的REST API与后端交互

## 解答参考

### 练习1: 基本文件传感器解答

```python
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='file_sensor_exercise',
    default_args=default_args,
    description='基本文件传感器练习',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'exercise'],
) as dag:
    
    # 创建测试文件
    def create_test_file():
        os.makedirs('/tmp/data', exist_ok=True)
        with open('/tmp/data/input.csv', 'w') as f:
            f.write('id,name,value\n')
            f.write('1,test,100\n')
            f.write('2,example,200\n')
        return "测试文件已创建"
    
    create_file = PythonOperator(
        task_id='create_file',
        python_callable=create_test_file,
    )
    
    # 等待文件出现
    wait_for_file = FileSensor(
        task_id='wait_for_file',
        filepath='/tmp/data/input.csv',
        poke_interval=10,
        timeout=60,
        mode='poke',
    )
    
    # 处理文件
    process_file = BashOperator(
        task_id='process_file',
        bash_command='echo "处理文件: $(cat /tmp/data/input.csv)"',
    )
    
    # 清理文件
    cleanup_file = BashOperator(
        task_id='cleanup_file',
        bash_command='rm -f /tmp/data/input.csv',
        trigger_rule=TriggerRule.ALL_DONE,
    )
    
    # 定义依赖关系
    create_file >> wait_for_file >> process_file >> cleanup_file
```

### 练习2: SQL传感器与钩子结合解答

```python
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.sensors.sql import SqlSensor

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='sql_sensor_hook_exercise',
    default_args=default_args,
    description='SQL传感器与钩子结合练习',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'hook', 'exercise'],
) as dag:
    
    # 创建测试表
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS source_data (
                id SERIAL PRIMARY KEY,
                data_value VARCHAR(255),
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS processed_data (
                id SERIAL PRIMARY KEY,
                source_id INTEGER,
                processed_value VARCHAR(255),
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES source_data(id)
            );
        """,
    )
    
    # 插入测试数据
    def insert_test_data():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 插入测试数据
        for i in range(5):
            postgres_hook.run(
                """
                INSERT INTO source_data (data_value, processed)
                VALUES (%s, %s);
                """,
                parameters=[f'test_data_{i}', False]
            )
        
        return "测试数据已插入"
    
    insert_data = PythonOperator(
        task_id='insert_data',
        python_callable=insert_test_data,
    )
    
    # 等待未处理数据
    wait_for_data = SqlSensor(
        task_id='wait_for_data',
        conn_id='postgres_default',
        sql="""
            SELECT COUNT(*) FROM source_data 
            WHERE processed = FALSE;
        """,
        poke_interval=10,
        timeout=60,
        mode='poke',
        check_success=lambda value: int(value[0][0]) > 0,
    )
    
    # 处理数据
    def process_data():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 获取未处理的数据
        records = postgres_hook.get_records(
            """
            SELECT id, data_value FROM source_data 
            WHERE processed = FALSE;
            """
        )
        
        # 处理数据
        for record in records:
            source_id = record[0]
            data_value = record[1]
            processed_value = f"processed_{data_value}"
            
            # 保存处理结果
            postgres_hook.run(
                """
                INSERT INTO processed_data (source_id, processed_value)
                VALUES (%s, %s);
                """,
                parameters=[source_id, processed_value]
            )
            
            # 更新原始数据状态
            postgres_hook.run(
                """
                UPDATE source_data 
                SET processed = TRUE 
                WHERE id = %s;
                """,
                parameters=[source_id]
            )
        
        return f"处理了 {len(records)} 条数据"
    
    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    # 定义依赖关系
    create_table >> insert_data >> wait_for_data >> process_data_task
```

### 练习3: HTTP传感器与钩子结合解答

```python
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.hooks.http import HttpHook

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='http_sensor_hook_exercise',
    default_args=default_args,
    description='HTTP传感器与钩子结合练习',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'hook', 'exercise'],
) as dag:
    
    # 等待API可用
    wait_for_api = HttpSensor(
        task_id='wait_for_api',
        http_conn_id='http_default',
        endpoint='posts/1',
        response_check=lambda response: response.status_code == 200,
        poke_interval=10,
        timeout=60,
        mode='poke',
    )
    
    # 获取并处理数据
    def fetch_and_process_data():
        # 使用HttpHook获取数据
        http_hook = HttpHook(http_conn_id='http_default', method='GET')
        
        # 获取多个帖子
        posts = []
        for post_id in range(1, 4):
            response = http_hook.run(endpoint=f'posts/{post_id}')
            if response.status_code == 200:
                posts.append(response.json())
        
        # 处理数据 - 提取标题和内容
        processed_data = []
        for post in posts:
            processed_data.append({
                'id': post['id'],
                'title': post['title'],
                'body': post['body'][:100] + '...' if len(post['body']) > 100 else post['body'],  # 截断内容
                'processed_at': datetime.now().isoformat()
            })
        
        # 保存处理结果到文件
        import json
        with open('/tmp/processed_posts.json', 'w') as f:
            json.dump(processed_data, f, indent=2)
        
        return f"处理了 {len(processed_data)} 条帖子"
    
    fetch_data = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_and_process_data,
    )
    
    # 定义依赖关系
    wait_for_api >> fetch_data
```

## 总结

这些练习题涵盖了传感器和钩子的各种使用场景，从基础的文件、数据库和API交互，到高级的动态创建、错误处理和性能优化。通过完成这些练习，你将能够：

1. 理解不同类型传感器的工作原理和适用场景
2. 掌握钩子与外部系统交互的方法
3. 学会结合使用传感器和钩子构建复杂工作流
4. 实现错误处理和性能优化
5. 设计可扩展和可维护的传感器与钩子系统

建议按照从基础到挑战的顺序完成练习，逐步提高你的Airflow技能。