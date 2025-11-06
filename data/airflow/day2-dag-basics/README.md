# Day 2: 核心概念与DAG基础

## 学习目标

- 理解Airflow的核心概念和架构
- 掌握DAG（有向无环图）的基本结构和语法
- 学习任务（Task）的定义和配置
- 了解不同类型的操作符（Operators）
- 掌握DAG的创建、导入和验证

## 目录

- [Airflow核心概念](#airflow核心概念)
- [DAG基础结构](#dag基础结构)
- [任务定义](#任务定义)
- [常用操作符](#常用操作符)
- [DAG创建最佳实践](#dag创建最佳实践)
- [实践练习](#实践练习)
- [进阶阅读](#进阶阅读)
- [今日小结](#今日小结)
- [下一步计划](#下一步计划)

## Airflow核心概念

### DAG (有向无环图)

DAG（Directed Acyclic Graph，有向无环图）是Airflow的核心概念，它定义了一个工作流的结构和依赖关系。DAG由任务（Task）和任务之间的依赖关系组成，确保工作流按照正确的顺序执行。

**DAG的特点：**
- 有向：任务之间的依赖关系是有方向的
- 无环：没有循环依赖，确保工作流能够完成
- 图：由节点（任务）和边（依赖关系）组成

### 任务 (Task)

任务是DAG中的基本执行单元，代表一个具体的工作。每个任务由操作符（Operator）定义，指定了要执行的操作和配置参数。

**任务的特点：**
- 每个任务有唯一的任务ID（task_id）
- 任务属于一个特定的DAG
- 任务可以有重试策略和超时设置
- 任务之间可以设置依赖关系

### 操作符 (Operator)

操作符是定义任务行为的模板，它封装了特定的功能。Airflow提供了多种内置操作符，也可以创建自定义操作符。

**常用操作符类型：**
- BashOperator：执行bash命令
- PythonOperator：执行Python函数
- EmailOperator：发送邮件
- HttpOperator：发送HTTP请求
- SqlOperator：执行SQL查询

### 实例 (Instance)

实例是DAG或任务在特定时间点的运行实例。每个DAG运行（DAG Run）和任务实例（Task Instance）都有唯一的状态。

**实例状态：**
- 运行中（running）
- 成功（success）
- 失败（failed）
- 跳过（skipped）
- 上游失败（upstream_failed）

### 执行日期 (Execution Date)

执行日期是DAG运行的逻辑时间点，用于确定数据处理的范围。执行日期不一定是实际运行时间，而是数据的时间点。

## DAG基础结构

### DAG定义

DAG是一个Python对象，通过DAG类实例化创建。以下是DAG的基本结构：

```python
from datetime import datetime, timedelta
from airflow import DAG

# 创建DAG实例
dag = DAG(
    dag_id='my_dag',  # DAG的唯一标识符
    default_args=default_args,  # 默认参数
    schedule_interval=timedelta(days=1),  # 调度间隔
    start_date=datetime(2023, 1, 1),  # 开始日期
    catchup=False,  # 是否补跑历史数据
    tags=['example'],  # 标签
)
```

### DAG参数

DAG类支持多种参数，用于配置DAG的行为：

```python
dag = DAG(
    dag_id='my_dag',  # 必需，DAG的唯一标识符
    description='My first DAG',  # 可选，DAG描述
    schedule_interval=timedelta(days=1),  # 可选，调度间隔
    start_date=datetime(2023, 1, 1),  # 必需，开始日期
    end_date=datetime(2023, 12, 31),  # 可选，结束日期
    full_filepath=None,  # 可选，DAG文件的完整路径
    template_searchpath=None,  # 可选，模板搜索路径
    template_undefined=jinja2.StrictUndefined,  # 可选，模板未定义处理
    user_defined_macros=None,  # 可选，用户定义的宏
    user_defined_filters=None,  # 可选，用户定义的过滤器
    access_control=None,  # 可选，访问控制
    render_template_as_native_obj=False,  # 可选，是否以原生对象渲染模板
    max_active_runs=1,  # 可选，最大同时运行数
    max_active_tasks=16,  # 可选，最大同时任务数
    dagrun_timeout=None,  # 可选，DAG运行超时时间
    default_args=None,  # 可选，默认参数
    default_view='grid',  # 可选，默认视图
    orientation='LR',  # 可选，图方向
    catchup=True,  # 可选，是否补跑历史数据
    on_failure_callback=None,  # 可选，失败回调函数
    on_success_callback=None,  # 可选，成功回调函数
    sla_miss_callback=None,  # 可选，SLA未达成回调函数
    params=None,  # 可选，参数字典
    concurrency=None,  # 可选，并发数
    jinja_environment_kwargs=None,  # 可选，Jinja环境参数
    tags=None,  # 可选，标签列表
    is_paused_upon_creation=None,  # 可选，创建时是否暂停
)
```

### 默认参数

默认参数（default_args）是应用于DAG中所有任务的参数字典，可以避免重复配置：

```python
default_args = {
    'owner': 'airflow',  # 任务所有者
    'depends_on_past': False,  # 是否依赖过去的任务成功
    'start_date': datetime(2023, 1, 1),  # 开始日期
    'email': ['airflow@example.com'],  # 通知邮箱
    'email_on_failure': False,  # 失败时是否发送邮件
    'email_on_retry': False,  # 重试时是否发送邮件
    'retries': 1,  # 重试次数
    'retry_delay': timedelta(minutes=5),  # 重试延迟
    'queue': 'default',  # 队列
    'pool': 'default_pool',  # 资源池
    'priority_weight': 1,  # 优先级权重
    'weight_rule': 'downstream',  # 权重规则
    'run_as_user': None,  # 运行用户
    'task_concurrency': 1,  # 任务并发数
    'resources': None,  # 资源需求
    'executor_config': None,  # 执行器配置
    'do_xcom_push': True,  # 是否推送XCom
    'inlets': [],  # 输入数据集
    'outlets': [],  # 输出数据集
    'sla': None,  # 服务级别协议
    'execution_timeout': None,  # 执行超时
    'on_failure_callback': None,  # 失败回调函数
    'on_success_callback': None,  # 成功回调函数
    'on_retry_callback': None,  # 重试回调函数
    'on_skipped_callback': None,  # 跳过回调函数
    'trigger_rule': 'all_success',  # 触发规则
    'doc_md': None,  # 文档
    'doc': None,  # 文档
    'doc_json': None,  # JSON文档
    'doc_yaml': None,  # YAML文档
    'doc_rst': None,  # RST文档
    'doc_md': None,  # Markdown文档
}
```

### 调度间隔

调度间隔（schedule_interval）定义了DAG的运行频率，可以使用多种格式：

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
schedule_interval='0 0 1 * *'  # 每月1日午夜运行

# 不调度（手动触发）
schedule_interval=None
```

## 任务定义

### 任务创建

任务是DAG中的基本执行单元，通过操作符（Operator）创建。以下是创建任务的基本方法：

```python
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# 使用BashOperator创建任务
bash_task = BashOperator(
    task_id='bash_task',  # 必需，任务的唯一标识符
    bash_command='echo "Hello World!"',  # 必需，要执行的bash命令
    dag=dag,  # 必需，所属的DAG
)

# 使用PythonOperator创建任务
def python_function():
    """Python函数示例"""
    return "Hello from Python!"

python_task = PythonOperator(
    task_id='python_task',  # 必需，任务的唯一标识符
    python_callable=python_function,  # 必需，要执行的Python函数
    dag=dag,  # 必需，所属的DAG
)
```

### 任务参数

任务支持多种参数，用于配置任务的行为：

```python
task = BashOperator(
    task_id='my_task',  # 必需，任务的唯一标识符
    bash_command='echo "Hello World!"',  # 必需，要执行的bash命令
    owner='airflow',  # 可选，任务所有者
    retries=3,  # 可选，重试次数
    retry_delay=timedelta(minutes=5),  # 可选，重试延迟
    email_on_failure=True,  # 可选，失败时是否发送邮件
    email=['airflow@example.com'],  # 可选，通知邮箱
    queue='default',  # 可选，队列
    pool='default_pool',  # 可选，资源池
    priority_weight=1,  # 可选，优先级权重
    weight_rule='downstream',  # 可选，权重规则
    run_as_user=None,  # 可选，运行用户
    task_concurrency=1,  # 可选，任务并发数
    resources=None,  # 可选，资源需求
    executor_config=None,  # 可选，执行器配置
    do_xcom_push=True,  # 可选，是否推送XCom
    inlets=[],  # 可选，输入数据集
    outlets=[],  # 可选，输出数据集
    sla=None,  # 可选，服务级别协议
    execution_timeout=None,  # 可选，执行超时
    on_failure_callback=None,  # 可选，失败回调函数
    on_success_callback=None,  # 可选，成功回调函数
    on_retry_callback=None,  # 可选，重试回调函数
    on_skipped_callback=None,  # 可选，跳过回调函数
    trigger_rule='all_success',  # 可选，触发规则
    doc_md=None,  # 可选，文档
    dag=dag,  # 必需，所属的DAG
)
```

### 任务文档

任务可以添加文档，用于描述任务的功能和用途：

```python
task = BashOperator(
    task_id='my_task',
    bash_command='echo "Hello World!"',
    doc_md="""
    # 任务文档

    这个任务用于打印"Hello World!"消息。

    ## 功能
    - 打印消息到控制台
    - 返回执行结果

    ## 参数
    - 无参数

    ## 返回值
    - 无返回值
    """,
    dag=dag,
)
```

### 任务回调

任务可以设置回调函数，在特定事件发生时执行：

```python
def failure_callback(context):
    """失败回调函数"""
    print(f"任务 {context['task_instance'].task_id} 失败")

def success_callback(context):
    """成功回调函数"""
    print(f"任务 {context['task_instance'].task_id} 成功")

task = BashOperator(
    task_id='my_task',
    bash_command='echo "Hello World!"',
    on_failure_callback=failure_callback,
    on_success_callback=success_callback,
    dag=dag,
)
```

## 常用操作符

### BashOperator

BashOperator用于执行bash命令：

```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World!"',
    dag=dag,
)
```

### PythonOperator

PythonOperator用于执行Python函数：

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

### EmailOperator

EmailOperator用于发送邮件：

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

### HttpOperator

HttpOperator用于发送HTTP请求：

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

### SqlOperator

SqlOperator用于执行SQL查询：

```python
from airflow.providers.common.sql.operators.sql import SqlOperator

task = SqlOperator(
    task_id='sql_task',
    sql='SELECT * FROM table',
    conn_id='my_db_conn',
    dag=dag,
)
```

### BranchPythonOperator

BranchPythonOperator用于根据条件选择执行路径：

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

## DAG创建最佳实践

### 文件组织

将DAG文件组织在合理的目录结构中：

```
dags/
├── __init__.py
├── common/
│   ├── __init__.py
│   └── utils.py
├── data_pipeline/
│   ├── __init__.py
│   ├── etl_dag.py
│   └── analytics_dag.py
└── monitoring/
    ├── __init__.py
    └── health_check_dag.py
```

### 代码重用

使用函数和类来重用代码：

```python
# common/utils.py
def create_bash_task(task_id, command, dag):
    """创建Bash任务的辅助函数"""
    return BashOperator(
        task_id=task_id,
        bash_command=command,
        dag=dag,
    )

# data_pipeline/etl_dag.py
from common.utils import create_bash_task

extract_task = create_bash_task('extract', 'extract_data.sh', dag)
transform_task = create_bash_task('transform', 'transform_data.sh', dag)
load_task = create_bash_task('load', 'load_data.sh', dag)
```

### 配置管理

使用配置文件或环境变量管理配置：

```python
import os
from configparser import ConfigParser

# 读取配置
config = ConfigParser()
config.read('config.ini')

# 使用配置
db_conn_id = config.get('database', 'conn_id')
api_endpoint = config.get('api', 'endpoint')
```

### 错误处理

设置适当的重试策略和错误处理：

```python
task = BashOperator(
    task_id='unstable_task',
    bash_command='unstable_command.sh',
    retries=3,
    retry_delay=timedelta(minutes=5),
    execution_timeout=timedelta(hours=1),
    on_failure_callback=notify_failure,
    dag=dag,
)
```

### 测试

编写单元测试和集成测试：

```python
import unittest
from airflow.models import DagBag

class TestDAG(unittest.TestCase):
    """DAG测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.dagbag = DagBag(dag_folder='dags/', include_examples=False)
    
    def test_dag_loaded(self):
        """测试DAG是否正确加载"""
        dag = self.dagbag.get_dag(dag_id='my_dag')
        self.assertIsNotNone(dag)
    
    def test_dag_structure(self):
        """测试DAG结构"""
        dag = self.dagbag.get_dag(dag_id='my_dag')
        self.assertEqual(len(dag.tasks), 3)
```

## 实践练习

### 练习1：创建简单DAG

创建一个包含3个任务的简单DAG：
1. 任务1：打印当前日期
2. 任务2：打印"Hello World!"
3. 任务3：打印当前时间

设置任务之间的依赖关系为：任务1 → 任务2 → 任务3

### 练习2：使用不同操作符

创建一个包含不同操作符的DAG：
1. BashOperator：执行系统命令
2. PythonOperator：执行Python函数
3. EmailOperator：发送邮件通知

### 练习3：条件分支

创建一个包含条件分支的DAG：
1. 使用BranchPythonOperator根据条件选择执行路径
2. 设置不同的分支任务
3. 合并分支结果

### 练习4：参数传递

创建一个在任务之间传递参数的DAG：
1. 任务1：生成随机数
2. 任务2：使用任务1的结果
3. 任务3：处理最终结果

## 进阶阅读

- [Airflow官方文档 - DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Airflow官方文档 - Operators](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html)
- [Airflow最佳实践](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Airflow DAG示例](https://github.com/apache/airflow/tree/main/airflow/example_dags)

## 今日小结

今天我们学习了Airflow的核心概念和DAG基础结构，包括：

1. Airflow的核心概念：DAG、任务、操作符、实例、执行日期
2. DAG的基本结构和参数配置
3. 任务的定义和配置
4. 常用操作符的使用方法
5. DAG创建的最佳实践

通过今天的学习，您应该能够创建基本的DAG，定义任务，并设置任务之间的依赖关系。

## 下一步计划

明天我们将学习更复杂的DAG结构，包括：

- 任务依赖关系的高级配置
- XComs（任务间通信）
- 子DAG和任务组
- 动态DAG生成

请确保完成今天的练习，为明天的学习做好准备。