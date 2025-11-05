# Day 2 故障排除指南

## 常见问题与解决方案

### DAG相关问题

#### 1. DAG不显示在UI中

**症状**：创建的DAG没有出现在Airflow Web UI的DAG列表中。

**可能原因**：
- DAG文件语法错误
- DAG文件不在正确的DAGs文件夹中
- Airflow配置中的DAGs文件夹路径不正确
- DAG文件包含未定义的变量或函数

**解决方案**：
1. 检查DAG文件语法：
   ```bash
   python -m py_compile your_dag_file.py
   ```

2. 确认DAG文件位置：
   - 检查`airflow.cfg`中的`dags_folder`配置
   - 确保DAG文件在指定目录中

3. 查看Airflow日志：
   ```bash
   # 查看调度器日志
   tail -f $AIRFLOW_HOME/logs/scheduler/*.log
   
   # 查看Web服务器日志
   tail -f $AIRFLOW_HOME/logs/webserver/*.log
   ```

4. 检查DAG文件导入错误：
   - 确保所有导入的模块都已安装
   - 检查自定义模块的导入路径

#### 2. DAG显示为暂停状态

**症状**：DAG在UI中显示，但处于暂停状态，无法自动调度。

**可能原因**：
- DAG创建时默认设置为暂停
- 手动暂停了DAG
- DAG文件中的`is_paused_upon_creation`参数设置为`True`

**解决方案**：
1. 在UI中手动取消暂停：
   - 进入DAG详情页面
   - 点击"Off/On"切换开关

2. 使用CLI命令取消暂停：
   ```bash
   airflow dags unpause your_dag_id
   ```

3. 在DAG定义中设置：
   ```python
   dag = DAG(
       'your_dag_id',
       is_paused_upon_creation=False,
       ...
   )
   ```

#### 3. DAG调度间隔不正确

**症状**：DAG没有按照预期的时间间隔运行。

**可能原因**：
- `schedule_interval`参数设置不正确
- `start_date`设置在未来
- `catchup=False`导致历史运行被跳过

**解决方案**：
1. 检查`schedule_interval`设置：
   ```python
   # 使用timedelta对象
   schedule_interval=timedelta(days=1)
   
   # 使用预设字符串
   schedule_interval='@daily'
   
   # 使用cron表达式
   schedule_interval='0 3 * * *'
   ```

2. 确保`start_date`在过去：
   ```python
   start_date=datetime(2023, 1, 1)
   ```

3. 调整`catchup`参数：
   ```python
   catchup=True  # 补跑历史数据
   catchup=False  # 不补跑历史数据
   ```

### 任务相关问题

#### 4. 任务失败

**症状**：任务执行失败，显示红色状态。

**可能原因**：
- 任务代码错误
- 依赖资源不可用
- 权限问题
- 网络连接问题

**解决方案**：
1. 查看任务日志：
   - 在UI中点击任务实例
   - 查看详细日志信息
   - 识别错误原因

2. 增加重试次数：
   ```python
   default_args = {
       'retries': 3,
       'retry_delay': timedelta(minutes=5),
       'retry_exponential_backoff': True,
   }
   ```

3. 添加错误处理：
   ```python
   def safe_function():
       try:
           # 可能出错的代码
           pass
       except Exception as e:
           print(f"错误: {e}")
           raise
   
   task = PythonOperator(
       task_id='safe_task',
       python_callable=safe_function,
       dag=dag,
   )
   ```

4. 设置执行超时：
   ```python
   task = BashOperator(
       task_id='timeout_task',
       bash_command='long_running_command.sh',
       execution_timeout=timedelta(hours=1),
       dag=dag,
   )
   ```

#### 5. 任务卡在运行状态

**症状**：任务长时间处于运行状态，不完成也不失败。

**可能原因**：
- 任务执行时间过长
- 死锁或无限循环
- 资源不足
- 外部依赖问题

**解决方案**：
1. 设置执行超时：
   ```python
   task = BashOperator(
       task_id='timeout_task',
       bash_command='long_running_command.sh',
       execution_timeout=timedelta(hours=1),
       dag=dag,
   )
   ```

2. 监控资源使用：
   - 检查CPU、内存使用情况
   - 查看系统负载

3. 手动标记任务为失败：
   ```bash
   airflow tasks fail --execution-date 2023-01-01 your_dag_id your_task_id
   ```

4. 重启Airflow组件：
   ```bash
   # 重启调度器
   airflow scheduler stop
   airflow scheduler start
   
   # 重启工作进程
   airflow worker stop
   airflow worker start
   ```

#### 6. 任务不执行

**症状**：任务被跳过或从未开始执行。

**可能原因**：
- 上游任务失败
- 触发规则设置不正确
- DAG处于暂停状态
- 资源池限制

**解决方案**：
1. 检查上游任务状态：
   - 确保所有上游任务已成功完成
   - 查看上游任务的日志

2. 检查触发规则：
   ```python
   task = BashOperator(
       task_id='trigger_rule_task',
       bash_command='echo "Hello"',
       trigger_rule='all_success',  # 或其他适当的规则
       dag=dag,
   )
   ```

3. 检查资源池：
   - 确保资源池有足够的槽位
   - 调整任务优先级

4. 手动触发任务：
   ```bash
   airflow tasks test your_dag_id your_task_id 2023-01-01
   ```

### XComs相关问题

#### 7. XCom值传递失败

**症状**：任务无法从XCom中获取值，或获取的值为None。

**可能原因**：
- 上游任务未推送XCom值
- XCom键名不匹配
- 任务ID不正确
- XCom值过大

**解决方案**：
1. 确保上游任务推送XCom值：
   ```python
   def push_function(**kwargs):
       value = "要传递的值"
       kwargs['ti'].xcom_push(key='my_key', value=value)
       return value
   
   task = PythonOperator(
       task_id='push_task',
       python_callable=push_function,
       dag=dag,
   )
   ```

2. 检查XCom拉取参数：
   ```python
   def pull_function(**kwargs):
       ti = kwargs['ti']
       # 确保任务ID和键名正确
       value = ti.xcom_pull(task_ids='push_task', key='my_key')
       print(f"拉取的值: {value}")
       return value
   ```

3. 使用默认值：
   ```python
   value = ti.xcom_pull(task_ids='push_task', key='my_key', default='默认值')
   ```

4. 检查XCom大小限制：
   - 默认XCom值大小限制为48KB
   - 对于大数据，考虑使用文件或数据库

### 依赖关系问题

#### 8. 依赖关系设置不正确

**症状**：任务执行顺序不符合预期。

**可能原因**：
- 依赖关系设置错误
- 触发规则设置不当
- 循环依赖

**解决方案**：
1. 检查依赖关系设置：
   ```python
   # 使用>>操作符
   task1 >> task2 >> task3
   
   # 使用set_upstream和set_downstream方法
   task4.set_upstream(task3)
   task5.set_downstream(task4)
   ```

2. 检查触发规则：
   ```python
   task = BashOperator(
       task_id='trigger_rule_task',
       bash_command='echo "Hello"',
       trigger_rule='all_success',  # 确保触发规则正确
       dag=dag,
   )
   ```

3. 避免循环依赖：
   - 使用DAG可视化工具检查依赖关系
   - 确保没有A→B→C→A这样的循环

4. 使用任务组组织复杂依赖：
   ```python
   from airflow.utils.task_group import TaskGroup
   
   with TaskGroup("processing_group") as processing_group:
       task1 = BashOperator(task_id="task1", bash_command="echo 1")
       task2 = BashOperator(task_id="task2", bash_command="echo 2")
       task3 = BashOperator(task_id="task3", bash_command="echo 3")
       
       task1 >> [task2, task3]
   
   start_task >> processing_group >> end_task
   ```

### 性能问题

#### 9. DAG加载缓慢

**症状**：Airflow UI加载缓慢，DAG列表显示延迟。

**可能原因**：
- DAG文件过多或过大
- 复杂的DAG定义
- 频繁的文件系统访问

**解决方案**：
1. 优化DAG文件：
   - 减少DAG文件中的复杂计算
   - 将复杂逻辑移至任务函数中
   - 使用延迟导入

2. 调整Airflow配置：
   ```ini
   [core]
   # 增加DAG处理线程数
   dag_processing_num_threads = 4
   
   # 减少DAG发现间隔
   dag_discovery_safe_mode = False
   min_file_process_interval = 0
   ```

3. 使用DAG包：
   - 将相关DAG组织到包中
   - 减少顶层DAG文件数量

#### 10. 任务执行缓慢

**症状**：任务执行时间过长，影响整体工作流性能。

**可能原因**：
- 任务逻辑复杂
- 资源不足
- 外部依赖响应慢

**解决方案**：
1. 优化任务逻辑：
   - 使用更高效的算法
   - 减少不必要的数据处理
   - 并行化可并行的操作

2. 增加资源：
   ```python
   # 设置任务优先级
   task = BashOperator(
       task_id='priority_task',
       bash_command='important_command.sh',
       priority_weight=10,
       dag=dag,
   )
   
   # 使用专用资源池
   task = BashOperator(
       task_id='pool_task',
       bash_command='resource_intensive_command.sh',
       pool='high_priority_pool',
       dag=dag,
   )
   ```

3. 使用传感器优化等待：
   ```python
   from airflow.sensors.filesystem import FileSensor
   
   # 使用传感器替代轮询
   wait_for_file = FileSensor(
       task_id='wait_for_file',
       filepath='/path/to/file',
       poke_interval=30,  # 每30秒检查一次
       timeout=600,       # 10分钟超时
       mode='poke',       # 或 'reschedule'
       dag=dag,
   )
   ```

## 调试技巧

### 1. 使用测试模式

```bash
# 测试单个任务
airflow tasks test your_dag_id your_task_id 2023-01-01

# 测试整个DAG
airflow dags test your_dag_id 2023-01-01
```

### 2. 添加日志输出

```python
def debug_function(**kwargs):
    ti = kwargs['ti']
    print(f"执行日期: {ti.execution_date}")
    print(f"任务实例: {ti}")
    # 其他调试信息
    pass

task = PythonOperator(
    task_id='debug_task',
    python_callable=debug_function,
    dag=dag,
)
```

### 3. 使用临时DAG

创建一个简化的DAG来测试特定功能：

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def test_function():
    """测试函数"""
    print("测试输出")
    return "测试结果"

test_dag = DAG(
    'test_dag',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test'],
)

test_task = PythonOperator(
    task_id='test_task',
    python_callable=test_function,
    dag=test_dag,
)
```

### 4. 使用Airflow CLI

```bash
# 列出DAG
airflow dags list

# 列出任务
airflow tasks list your_dag_id

# 查看DAG信息
airflow dags report

# 检查DAG文件
airflow dags report your_dag_id

# 变量管理
airflow variables list
airflow variables get your_variable
airflow variables set your_variable "your_value"

# 连接管理
airflow connections list
airflow connections get your_conn_id
```

### 5. 使用Airflow REST API

```bash
# 获取DAG列表
curl -X GET "http://localhost:8080/api/v1/dags"

# 获取DAG详情
curl -X GET "http://localhost:8080/api/v1/dags/your_dag_id"

# 触发DAG
curl -X POST "http://localhost:8080/api/v1/dags/your_dag_id/dagRuns" \
  -H "Content-Type: application/json" \
  -d '{"execution_date": "2023-01-01T00:00:00Z"}'
```

## 获取帮助

### 1. 官方文档

- [Airflow官方文档](https://airflow.apache.org/docs/apache-airflow/stable/)
- [Airflow FAQ](https://airflow.apache.org/docs/apache-airflow/stable/faq.html)
- [Airflow最佳实践](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

### 2. 社区资源

- [Airflow邮件列表](https://airflow.apache.org/community/)
- [Airflow Slack](https://apache-airflow.slack.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/apache-airflow)

### 3. 代码示例

- [Airflow示例DAGs](https://github.com/apache/airflow/tree/main/airflow/example_dags)
- [Airflow提供商包](https://airflow.apache.org/docs/apache-airflow-providers/stable/)

## 预防措施

### 1. 代码审查

- 在部署前进行代码审查
- 使用静态代码分析工具
- 编写单元测试

### 2. 渐进式部署

- 先在开发环境测试
- 使用测试DAG验证功能
- 逐步部署到生产环境

### 3. 监控和警报

- 设置任务失败警报
- 监控DAG执行性能
- 定期检查系统资源使用情况

### 4. 文档和注释

- 为DAG添加详细文档
- 注释复杂逻辑
- 记录已知问题和解决方案

通过遵循这些故障排除指南和最佳实践，您可以更有效地识别和解决Airflow中的常见问题，提高DAG的可靠性和性能。