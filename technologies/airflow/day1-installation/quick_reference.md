# Airflow Day 1 快速参考指南

## 常用命令

### 环境设置
```bash
# 创建虚拟环境
python -m venv airflow-env

# 激活虚拟环境 (Linux/Mac)
source airflow-env/bin/activate

# 激活虚拟环境 (Windows)
.\airflow-env\Scripts\Activate.ps1

# 升级 pip
pip install --upgrade pip
```

### 安装 Airflow
```bash
# 安装 Airflow
pip install apache-airflow

# 安装特定版本
pip install apache-airflow==2.5.0

# 安装提供者包
pip install apache-airflow-providers-postgres
pip install apache-airflow-providers-amazon
pip install apache-airflow-providers-docker

# 验证安装
airflow version
```

### 配置 Airflow
```bash
# 设置环境变量 (Linux/Mac)
export AIRFLOW_HOME=~/airflow

# 设置环境变量 (Windows PowerShell)
$env:AIRFLOW_HOME = "$env:USERPROFILE\airflow"

# 创建目录结构
mkdir -p $AIRFLOW_HOME/{dags,logs,plugins}

# 初始化数据库
airflow db init

# 创建管理员用户
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

### 启动服务
```bash
# 启动 Web 服务器
airflow webserver --port 8080

# 启动调度器 (在另一个终端)
airflow scheduler

# 同时启动 Web 服务器和调度器
airflow standalone
```

### DAG 管理
```bash
# 列出所有 DAG
airflow dags list

# 列出 DAG 的任务
airflow tasks list your_dag_id

# 手动触发 DAG
airflow dags trigger your_dag_id

# 暂停/取消暂停 DAG
airflow dags pause your_dag_id
airflow dags unpause your_dag_id

# 测试任务
airflow tasks test your_dag_id your_task_id 2023-01-01
```

## 基本配置

### airflow.cfg 关键配置
```ini
[core]
executor = LocalExecutor
sql_alchemy_conn = sqlite:////airflow/airflow.db
load_examples = True
dags_folder = /path/to/your/dags
plugins_folder = /path/to/your/plugins

[webserver]
web_server_host = 0.0.0.0
web_server_port = 8080
rbac = True

[logging]
base_log_folder = /path/to/your/logs
log_level = INFO

[scheduler]
scheduler_heartbeat_sec = 5
```

### 环境变量
```bash
# Linux/Mac
export AIRFLOW_HOME=~/airflow
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:////airflow/airflow.db

# Windows PowerShell
$env:AIRFLOW_HOME = "$env:USERPROFILE\airflow"
$env:AIRFLOW__CORE__EXECUTOR = "LocalExecutor"
$env:AIRFLOW__CORE__SQL_ALCHEMY_CONN = "sqlite:////airflow/airflow.db"
```

## 简单 DAG 模板

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# 默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建 DAG
dag = DAG(
    'simple_dag',
    default_args=default_args,
    description='A simple DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example'],
)

# 定义 Python 函数
def python_function():
    """Python 函数示例"""
    return "Hello from Python function"

# 创建任务
task1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

task2 = PythonOperator(
    task_id='python_task',
    python_callable=python_function,
    dag=dag,
)

task3 = BashOperator(
    task_id='print_hello',
    bash_command='echo "Hello World!"',
    dag=dag,
)

# 设置依赖关系
task1 >> task2 >> task3
```

## 目录结构

```
airflow/
├── dags/                    # DAG 文件目录
│   └── your_dag.py
├── logs/                    # 日志目录
│   ├── scheduler/
│   └── webserver/
├── plugins/                 # 插件目录
├── airflow.cfg              # 配置文件
└── airflow.db               # SQLite 数据库 (默认)
```

## 常用操作符

### BashOperator
```python
from airflow.operators.bash import BashOperator

bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World!"',
    dag=dag,
)
```

### PythonOperator
```python
from airflow.operators.python import PythonOperator

def my_python_function():
    print("Hello from Python!")
    return "Success"

python_task = PythonOperator(
    task_id='python_task',
    python_callable=my_python_function,
    dag=dag,
)
```

### EmailOperator
```python
from airflow.operators.email import EmailOperator

email_task = EmailOperator(
    task_id='send_email',
    to='recipient@example.com',
    subject='Airflow Alert',
    html_content='<h3>DAG completed successfully</h3>',
    dag=dag,
)
```

## 依赖关系设置

```python
# 线性依赖
task1 >> task2 >> task3

# 分支依赖
task1 >> [task2, task3]
task2 >> task4
task3 >> task4

# 合并依赖
[task1, task2] >> task3

# 使用 set_upstream 和 set_downstream
task2.set_upstream(task1)
task3.set_upstream(task2)
# 或者
task1.set_downstream(task2)
task2.set_downstream(task3)
```

## 常见问题解决

### 数据库连接问题
```bash
# 检查数据库连接
airflow db check

# 重置数据库
airflow db reset
```

### DAG 不显示
```bash
# 检查 DAG 文件语法
python -m py_compile your_dag.py

# 刷新 DAG 列表
airflow dags list
```

### 权限问题
```bash
# 设置目录权限 (Linux/Mac)
chmod -R 755 $AIRFLOW_HOME

# 检查目录所有者
ls -la $AIRFLOW_HOME
```

## Web UI 快速导航

- **DAGs**: 查看所有 DAG 列表
- **Grid View**: 查看 DAG 运行历史和任务状态
- **Graph View**: 查看 DAG 的依赖关系图
- **Calendar View**: 查看 DAG 运行日历
- **Task Duration**: 查看任务执行时间统计
- **Task Instances**: 查看任务实例详情
- **XComs**: 查看任务间通信数据
- **Browse**: 浏览连接、变量、池等资源
- **Admin**: 管理用户、配置等
- **Docs**: 查看 Airflow 文档

## 有用的链接

- [Airflow 官方文档](https://airflow.apache.org/docs/)
- [Airflow GitHub](https://github.com/apache/airflow)
- [Airflow 邮件列表](https://airflow.apache.org/community/)
- [Airflow Slack](https://apache-airflow.slack.com/)

## 快速检查清单

安装完成后，检查以下项目：

- [ ] Python 版本 >= 3.8
- [ ] 虚拟环境已创建并激活
- [ ] Airflow 已安装
- [ ] AIRFLOW_HOME 环境变量已设置
- [ ] 必要的目录已创建
- [ ] 数据库已初始化
- [ ] 管理员用户已创建
- [ ] Web 服务器能够启动
- [ ] 调度器能够启动
- [ ] 能够访问 Web UI
- [ ] 示例 DAG 能够运行

完成以上检查后，您的 Airflow 环境就准备就绪了！