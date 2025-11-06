# Day 1 练习题：Airflow 安装与环境配置

## 基础练习

### 练习 1：环境准备

**目标：** 检查并准备 Airflow 运行所需的环境

**任务：**
1. 检查系统上安装的 Python 版本，确认是否满足 Airflow 要求
2. 创建一个 Python 虚拟环境并激活
3. 升级 pip 到最新版本

**验证步骤：**
- 运行 `python --version` 并记录版本号
- 运行 `which python`（Linux/Mac）或 `where python`（Windows）确认使用的是虚拟环境中的 Python
- 运行 `pip --version` 确认 pip 已升级

**提示：**
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

---

### 练习 2：安装 Airflow

**目标：** 在虚拟环境中安装 Airflow

**任务：**
1. 使用 pip 安装最新稳定版的 Airflow
2. 安装至少两个 Airflow 提供者包
3. 验证 Airflow 安装是否成功

**验证步骤：**
- 运行 `pip show apache-airflow` 查看 Airflow 版本信息
- 运行 `airflow version` 确认 Airflow 命令可用
- 列出已安装的提供者包

**提示：**
```bash
# 安装 Airflow
pip install apache-airflow

# 安装提供者包
pip install apache-airflow-providers-postgres
pip install apache-airflow-providers-amazon

# 验证安装
airflow version
```

---

### 练习 3：配置 Airflow

**目标：** 配置 Airflow 基本设置

**任务：**
1. 设置 AIRFLOW_HOME 环境变量
2. 创建必要的目录结构（dags、logs、plugins）
3. 初始化 Airflow 数据库
4. 创建管理员用户

**验证步骤：**
- 运行 `echo $AIRFLOW_HOME`（Linux/Mac）或 `echo $env:AIRFLOW_HOME`（Windows）确认环境变量设置
- 检查目录结构是否创建成功
- 验证数据库初始化是否完成
- 尝试使用创建的管理员用户登录

**提示：**
```bash
# 设置环境变量 (Linux/Mac)
export AIRFLOW_HOME=~/airflow

# 设置环境变量 (Windows PowerShell)
$env:AIRFLOW_HOME = "$env:USERPROFILE\airflow"

# 创建目录
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

---

### 练习 4：启动 Airflow 服务

**目标：** 启动 Airflow Web 服务器和调度器

**任务：**
1. 启动 Airflow Web 服务器
2. 在另一个终端启动 Airflow 调度器
3. 访问 Airflow Web UI

**验证步骤：**
- 确认 Web 服务器成功启动并监听端口 8080
- 确认调度器成功启动
- 访问 http://localhost:8080 并能够登录

**提示：**
```bash
# 启动 Web 服务器
airflow webserver --port 8080

# 在另一个终端启动调度器
airflow scheduler

# 或者使用 standalone 模式同时启动两个服务
airflow standalone
```

---

## 进阶练习

### 练习 5：创建第一个 DAG

**目标：** 创建一个简单的 DAG 并验证其运行

**任务：**
1. 在 dags 目录下创建一个简单的 DAG 文件
2. DAG 应包含至少两个任务
3. 设置任务之间的依赖关系
4. 手动触发 DAG 运行并观察结果

**验证步骤：**
- 在 Airflow Web UI 中看到新创建的 DAG
- 成功触发 DAG 运行
- 查看任务执行日志

**提示：**
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_first_dag',
    default_args=default_args,
    description='My first DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

task1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

task2 = BashOperator(
    task_id='sleep',
    bash_command='sleep 5',
    dag=dag,
)

task3 = BashOperator(
    task_id='print_hello',
    bash_command='echo "Hello world!"',
    dag=dag,
)

task1 >> [task2, task3]
```

---

### 练习 6：配置不同的执行器

**目标：** 尝试使用不同的执行器运行 Airflow

**任务：**
1. 将执行器从 LocalExecutor 更改为 SequentialExecutor
2. 重新初始化数据库（如果需要）
3. 重启 Airflow 服务并验证执行器更改
4. 比较不同执行器的行为差异

**验证步骤：**
- 在 Airflow 配置中确认执行器已更改
- 运行一个简单的 DAG 并观察任务执行方式
- 记录两种执行器的区别

**提示：**
```ini
# 在 airflow.cfg 中修改
[core]
executor = SequentialExecutor

# 重新初始化数据库
airflow db init
```

---

### 练习 7：使用 Docker 运行 Airflow

**目标：** 使用 Docker Compose 运行 Airflow

**任务：**
1. 创建一个基本的 docker-compose.yml 文件
2. 使用 Docker Compose 启动 Airflow
3. 访问 Airflow Web UI
4. 在 Docker 环境中创建一个 DAG

**验证步骤：**
- Docker 容器成功启动
- 能够访问 Airflow Web UI
- DAG 在 Docker 环境中正常运行

**提示：**
```yaml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data

  airflow:
    image: apache/airflow:2.5.0
    depends_on:
      - postgres
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CORE__FERNET_KEY=your-fernet-key-here
      - AIRFLOW__CORE__LOAD_EXAMPLES=false
    volumes:
      - ./dags:/opt/airflow/dags
    ports:
      - "8080:8080"
    command: webserver

volumes:
  postgres-db-volume:
```

---

### 练习 8：配置邮件通知

**目标：** 配置 Airflow 发送邮件通知

**任务：**
1. 在 Airflow 配置中设置 SMTP 服务器
2. 创建一个失败的任务来测试邮件通知
3. 验证是否收到邮件通知

**验证步骤：**
- 配置 SMTP 服务器设置
- 任务失败时收到邮件通知

**提示：**
```ini
# 在 airflow.cfg 中配置
[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_port = 587
smtp_user = your-email@gmail.com
smtp_password = your-app-password
smtp_mail_from = your-email@gmail.com

# 在 DAG 中设置
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': ['your-email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
```

---

## 挑战练习

### 练习 9：自定义插件开发

**目标：** 创建一个简单的自定义 Airflow 插件

**任务：**
1. 在 plugins 目录下创建一个简单的插件
2. 插件应包含一个自定义操作符
3. 在 DAG 中使用自定义操作符
4. 验证插件是否正常工作

**验证步骤：**
- Airflow 成功加载自定义插件
- DAG 使用自定义操作符成功运行

**提示：**
```python
# 在 plugins 目录下创建 my_plugin.py
from airflow.plugins_manager import AirflowPlugin
from airflow.operators.bash import BashOperator

class MyCustomOperator(BashOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bash_command = "echo 'This is a custom operator!'"

class MyPlugin(AirflowPlugin):
    name = "my_plugin"
    operators = [MyCustomOperator]

# 在 DAG 中使用
from airflow.operators.my_plugin import MyCustomOperator

custom_task = MyCustomOperator(
    task_id='custom_task',
    dag=dag,
)
```

---

### 练习 10：性能调优

**目标：** 优化 Airflow 配置以提高性能

**任务：**
1. 分析当前 Airflow 配置
2. 调整并行度和资源分配参数
3. 优化数据库连接池设置
4. 测试配置更改对性能的影响

**验证步骤：**
- 记录配置更改前后的性能指标
- 验证系统稳定性

**提示：**
```ini
# 在 airflow.cfg 中调整
[core]
parallelism = 32
dag_concurrency = 16
max_active_tasks_per_dag = 16

[database]
sql_alchemy_pool_size = 5
sql_alchemy_max_overflow = 10

[scheduler]
scheduler_heartbeat_sec = 5
```

---

## 提交答案

完成练习后，请将以下内容提交：

1. 每个练习的解决方案代码或配置
2. 运行结果的截图或日志输出
3. 遇到的问题及解决方法
4. 对练习的反思和建议

这些练习将帮助您巩固 Airflow 安装和配置的知识，为后续学习打下坚实基础。