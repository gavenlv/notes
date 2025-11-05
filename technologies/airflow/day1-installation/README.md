# Day 1: 安装与环境配置

## 📋 学习目标

- 了解 Apache Airflow 的基本概念和应用场景
- 掌握 Airflow 的多种安装方式
- 配置 Airflow 开发环境
- 验证安装并运行第一个 DAG
- 理解 Airflow 的基本目录结构和配置文件

## 🎯 学习内容

### 1. Apache Airflow 简介

#### 什么是 Apache Airflow？
Apache Airflow 是一个开源的工作流管理平台，用于开发、调度和监控批处理工作流。它通过 Python 定义工作流（称为 DAG），具有丰富的用户界面，使工作流的监控和管理变得简单直观。

#### 核心特性
- **工作流即代码**: 使用 Python 定义工作流，版本控制友好
- **动态工作流**: 支持动态生成工作流，适应复杂场景
- **丰富的操作符**: 内置大量操作符，支持各种系统和工具
- **可扩展性**: 支持自定义操作符、插件和扩展
- **用户界面**: 直观的 Web UI 用于监控、管理和调试工作流
- **集成能力**: 易于与现有系统集成

#### 应用场景
- **数据 ETL/ELT**: 数据抽取、转换和加载流程
- **机器学习**: 模型训练、评估和部署流水线
- **报告生成**: 定期报告和数据分析
- **基础设施管理**: 自动化部署和配置管理
- **业务流程**: 跨系统工作流编排

### 2. 安装方式

#### 方式一: 使用 pip 安装（推荐初学者）

```bash
# 创建虚拟环境
python -m venv airflow-env
source airflow-env/bin/activate  # Linux/macOS
# 或
airflow-env\Scripts\activate  # Windows

# 安装 Airflow
pip install apache-airflow

# 安装特定版本的 Airflow
pip install apache-airflow==2.6.3

# 安装额外的提供者包
pip install apache-airflow-providers-postgres
pip install apache-airflow-providers-amazon
```

#### 方式二: 使用 Docker Compose（推荐生产环境）

```bash
# 克隆官方仓库
git clone https://github.com/apache/airflow.git
cd airflow

# 使用 Docker Compose 启动
docker-compose up -d
```

#### 方式三: 使用 Helm（Kubernetes 环境）

```bash
# 添加 Airflow Helm 仓库
helm repo add apache-airflow https://airflow.apache.org

# 安装 Airflow
helm install airflow apache-airflow/airflow
```

### 3. 环境配置

#### 基础配置

```bash
# 设置 Airflow 主目录
export AIRFLOW_HOME=~/airflow

# 初始化数据库
airflow db init

# 创建管理员用户
airflow users create \
    --username admin \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org
```

#### 配置文件 (airflow.cfg)

```ini
[core]
# Airflow 主目录
airflow_home = ~/airflow

# 执行器类型 (LocalExecutor, CeleryExecutor, KubernetesExecutor)
executor = LocalExecutor

# 元数据数据库连接
sql_alchemy_conn = sqlite:///~/airflow/airflow.db

# DAG 目录
dags_folder = ~/airflow/dags

# 插件目录
plugins_folder = ~/airflow/plugins

[webserver]
# Web 服务器端口
web_server_port = 8080

# 基本认证
authenticate = True

[scheduler]
# 调度器运行间隔
scheduler_heartbeat_sec = 5

[logging]
# 日志级别
base_log_folder = ~/airflow/logs
log_level = INFO
```

### 4. 目录结构

```
airflow/
├── airflow.cfg          # 主配置文件
├── airflow.db           # SQLite 数据库（默认）
├── dags/                # DAG 文件目录
├── logs/                # 日志文件目录
├── plugins/             # 插件目录
├── .airflowignore       # 忽略文件
└── webserver_config.py  # Web 服务器配置
```

### 5. 启动和验证

#### 启动 Airflow

```bash
# 启动 Web 服务器
airflow webserver --port 8080

# 启动调度器（新终端）
airflow scheduler

# 使用 standalone 模式（同时启动 Web 服务器和调度器）
airflow standalone
```

#### 验证安装

1. 访问 Web UI: http://localhost:8080
2. 使用创建的管理员账户登录
3. 检查示例 DAG 是否加载
4. 尝试手动运行示例 DAG

### 6. 第一个 DAG

创建一个简单的 DAG 来验证安装：

```python
# ~/airflow/dags/my_first_dag.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
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
    retries=3,
    dag=dag,
)

task1 >> task2
```

## 🛠️ 实践练习

### 练习 1: 安装 Airflow
1. 创建 Python 虚拟环境
2. 使用 pip 安装 Airflow
3. 初始化 Airflow 数据库
4. 创建管理员用户

### 练习 2: 配置 Airflow
1. 修改 airflow.cfg 配置文件
2. 调整日志级别和目录
3. 设置 DAG 目录路径
4. 配置 Web 服务器端口

### 练习 3: 创建第一个 DAG
1. 在 dags 目录中创建一个新的 Python 文件
2. 定义一个简单的 DAG，包含两个任务
3. 设置任务依赖关系
4. 在 Web UI 中启用并运行 DAG

### 练习 4: 验证安装
1. 启动 Airflow Web 服务器和调度器
2. 访问 Web UI 并登录
3. 检查 DAG 是否正确加载
4. 手动运行 DAG 并查看日志

## 📚 进阶阅读

- [Airflow 官方安装指南](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html)
- [Airflow 配置参考](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html)
- [Airflow 执行器比较](https://airflow.apache.org/docs/apache-airflow/stable/executor/index.html)

## 🎯 今日小结

今天我们学习了：
- Apache Airflow 的基本概念和应用场景
- 多种安装 Airflow 的方法
- 基础环境配置和目录结构
- 创建并运行第一个 DAG
- 验证 Airflow 安装

## 🚀 下一步

明天我们将深入学习 Airflow 的核心概念和架构，了解 DAG、任务、操作符等核心组件的工作原理。

---

**提示**: 如果在安装过程中遇到问题，请检查 Python 版本（需要 3.8+）和系统依赖。对于生产环境，推荐使用 PostgreSQL 作为元数据库和 CeleryExecutor 作为执行器。