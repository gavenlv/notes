# Celery监控与管理

本章将详细介绍Celery的监控与管理功能，这对于确保分布式任务处理系统的稳定运行至关重要。通过有效的监控和管理，我们可以实时了解系统状态、及时发现并解决问题、优化系统性能，以及确保任务的可靠执行。

## 目录
- [监控与管理概述](#监控与管理概述)
  - [为什么需要监控](#为什么需要监控)
  - [监控的关键指标](#监控的关键指标)
  - [监控工具选择](#监控工具选择)
- [Flower：Celery的实时监控工具](#flowercelery的实时监控工具)
  - [Flower简介](#flower简介)
  - [安装与配置](#安装与配置)
  - [启动Flower服务](#启动flower服务)
  - [Flower界面详解](#flower界面详解)
    - [仪表盘](#仪表盘)
    - [任务列表](#任务列表)
    - [工作进程](#工作进程)
    - [Broker状态](#broker状态)
    - [Beat状态](#beat状态)
    - [监控配置](#监控配置)
  - [Flower API](#flower-api)
  - [Flower安全配置](#flower安全配置)
- [Celery日志系统](#celery日志系统)
  - [日志配置基础](#日志配置基础)
  - [日志级别与格式](#日志级别与格式)
  - [文件日志配置](#文件日志配置)
  - [多进程日志处理](#多进程日志处理)
  - [集成外部日志系统](#集成外部日志系统)
- [任务状态管理](#任务状态管理)
  - [任务状态查询](#任务状态查询)
  - [任务结果跟踪](#任务结果跟踪)
  - [任务取消与终止](#任务取消与终止)
  - [任务优先级管理](#任务优先级管理)
- [工作进程管理](#工作进程管理)
  - [工作进程生命周期](#工作进程生命周期)
  - [进程池设置](#进程池设置)
  - [工作进程健康检查](#工作进程健康检查)
  - [工作进程热重启](#工作进程热重启)
  - [工作进程资源限制](#工作进程资源限制)
- [系统级监控](#系统级监控)
  - [系统资源监控](#系统资源监控)
  - [集成Prometheus](#集成prometheus)
  - [集成Grafana](#集成grafana)
  - [自定义监控指标](#自定义监控指标)
- [告警与通知](#告警与通知)
  - [任务失败告警](#任务失败告警)
  - [系统异常告警](#系统异常告警)
  - [集成第三方告警系统](#集成第三方告警系统)
- [Beat监控与管理](#beat监控与管理)
  - [Beat状态监控](#beat状态监控)
  - [Beat进程管理](#beat进程管理)
  - [定时任务监控](#定时任务监控)
- [监控最佳实践](#监控最佳实践)
  - [分层监控策略](#分层监控策略)
  - [监控面板设计](#监控面板设计)
  - [日志聚合与分析](#日志聚合与分析)
  - [性能基线建立](#性能基线建立)
  - [常见问题排查](#常见问题排查)
- [实践示例](#实践示例)

## 监控与管理概述

### 为什么需要监控

在生产环境中，监控Celery系统至关重要，原因包括：

1. **问题早发现**：通过实时监控可以尽早发现系统异常，避免问题扩大
2. **性能优化**：了解系统瓶颈和性能热点，针对性地进行优化
3. **可靠性保障**：确保任务按预期执行，减少失败率
4. **资源利用**：监控系统资源使用情况，合理分配资源
5. **容量规划**：根据历史数据预测未来需求，进行容量规划

### 监控的关键指标

监控Celery系统时，需要关注以下关键指标：

1. **任务指标**：
   - 任务执行率（成功/失败/总任务）
   - 任务等待时间
   - 任务执行时间
   - 任务队列长度
   - 任务优先级分布

2. **工作进程指标**：
   - 活跃工作进程数量
   - 工作进程负载
   - 工作进程内存使用
   - 工作进程CPU使用率
   - 工作进程生命周期

3. **系统指标**：
   - Broker连接状态
   - Broker队列长度
   - 系统资源（CPU、内存、磁盘I/O、网络）
   - 错误率和异常数量
   - 系统吞吐量

### 监控工具选择

对于Celery系统的监控，有多种工具可选：

1. **Flower**：Celery官方推荐的实时监控工具，提供Web界面
2. **Prometheus + Grafana**：开源监控和可视化解决方案
3. **ELK Stack**：日志聚合、分析和可视化
4. **Datadog/New Relic**：商业监控服务，提供Celery集成
5. **自定义监控**：基于Celery API开发自定义监控系统

本章将重点介绍Flower和基于Prometheus的监控方案。

## Flower：Celery的实时监控工具

### Flower简介

[Flower](https://flower.readthedocs.io/)是Celery的实时监控和管理工具，提供直观的Web界面，支持以下功能：

- 任务监控与管理（查看、撤销、终止任务）
- 工作进程监控（状态、负载、性能）
- 任务历史记录和统计信息
- Broker监控
- Beat调度器监控
- HTTP API接口
- 访问控制和认证

### 安装与配置

安装Flower非常简单：

```bash
pip install flower
```

Flower可以通过命令行参数或配置文件进行配置。以下是一些常用配置选项：

```bash
# 设置监听端口（默认为5555）
celery -A proj flower --port=5555

# 设置监听地址（默认为localhost）
celery -A proj flower --address=0.0.0.0

# 设置认证
celery -A proj flower --basic_auth=user1:password1,user2:password2

# 设置日志级别
celery -A proj flower --loglevel=info

# 配置持久化
celery -A proj flower --persistent=True

# 设置最大任务历史记录
celery -A proj flower --max-tasks=10000
```

### 启动Flower服务

启动Flower服务有多种方式：

**1. 直接命令行启动**：

```bash
celery -A your_project flower
```

**2. 作为系统服务启动**：

创建systemd服务文件（`/etc/systemd/system/flower.service`）：

```ini
[Unit]
Description=Celery Flower Service
After=network.target

[Service]
User=celery
Group=celery
WorkingDirectory=/path/to/your/project
ExecStart=/usr/local/bin/celery -A your_project flower --port=5555 --address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl enable flower
sudo systemctl start flower
```

**3. 使用Docker容器**：

```bash
docker run -d --name flower -p 5555:5555 --link redis:redis mher/flower celery flower --broker=redis://redis:6379/0
```

### Flower界面详解

启动Flower服务后，可以通过浏览器访问`http://localhost:5555`（或配置的其他地址和端口）来查看和管理Celery系统。

#### 仪表盘

仪表盘页面显示Celery系统的概览信息，包括：

- 活跃任务数量
- 任务成功/失败/重试的统计信息
- 任务执行时间分布图
- 工作进程数量和状态
- Broker队列信息
- 最近执行的任务列表

#### 任务列表

任务列表页面显示所有任务的详细信息，可以按照状态、时间、任务名称等进行筛选和排序。主要功能包括：

- 查看任务状态、ID、名称、参数、执行时间等信息
- 撤销任务（如果任务尚未开始执行）
- 终止任务（如果任务正在执行）
- 重试失败的任务
- 查看任务详情和日志

#### 工作进程

工作进程页面显示所有工作进程的信息，包括：

- 进程ID
- 主机名
- 状态（活跃/空闲）
- 执行的任务数量
- 进程启动时间
- CPU和内存使用率
- 队列分配

#### Broker状态

Broker状态页面显示消息代理的详细信息，包括：

- Broker URL
- 队列列表和长度
- 消息统计（发布/接收/确认）
- 连接状态

#### Beat状态

如果启用了Celery Beat，Beat状态页面会显示调度器的信息，包括：

- Beat进程状态
- 调度的任务列表
- 下次执行时间

#### 监控配置

Flower还提供了一些配置选项，可以根据需要进行调整：

- 刷新间隔（默认2秒）
- 显示的任务数量
- 过滤条件
- 图表设置

### Flower API

Flower提供了RESTful API，可以通过HTTP请求来监控和管理Celery系统。以下是一些常用API示例：

**1. 获取工作进程列表**：

```bash
curl http://localhost:5555/api/workers
```

**2. 获取任务列表**：

```bash
curl http://localhost:5555/api/tasks
```

**3. 获取单个任务信息**：

```bash
curl http://localhost:5555/api/task/task_id
```

**4. 获取队列信息**：

```bash
curl http://localhost:5555/api/queues
```

**5. 撤销任务**：

```bash
curl -X POST http://localhost:5555/api/task/revoke/task_id
```

**6. 重试任务**：

```bash
curl -X POST http://localhost:5555/api/task/retry/task_id
```

**7. 终止任务**：

```bash
curl -X POST http://localhost:5555/api/task/terminate/task_id
```

Flower API的完整文档可以在[官方文档](https://flower.readthedocs.io/en/latest/api.html)中找到。

### Flower安全配置

在生产环境中，确保Flower的安全访问非常重要。以下是一些安全配置建议：

**1. 基本认证**：

```bash
celery -A your_project flower --basic_auth=username:password
```

**2. 使用HTTPS**：

```bash
celery -A your_project flower --broker=amqp://guest@localhost// --port=5555 --url-prefix=flower --basic_auth=user:pass --keyfile=/path/to/key.pem --certfile=/path/to/cert.pem
```

**3. 访问控制**：

通过反向代理（如Nginx）限制访问IP：

```nginx
server {
    listen 80;
    server_name flower.yourdomain.com;
    
    # 限制访问IP
    allow 192.168.1.0/24;
    deny all;
    
    location / {
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**4. 使用Flower的权限系统**：

Flower支持不同的权限级别，可以在启动时配置：

```bash
# 只读用户
celery -A your_project flower --basic_auth=read:readpass,admin:adminpass --auth_provider=flower.views.auth.GoogleAuth2State
```

## Celery日志系统

日志是监控和排查问题的重要工具。Celery提供了灵活的日志配置选项。

### 日志配置基础

在Celery中，可以通过配置文件或命令行参数来设置日志级别和格式：

**命令行参数**：

```bash
celery -A your_project worker --loglevel=info
```

**配置文件**：

```python
# celeryconfig.py

# 日志级别
worker_loglevel = 'INFO'
beat_loglevel = 'INFO'

# 日志格式
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
beat_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
```

### 日志级别与格式

Celery支持以下日志级别（从低到高）：

- DEBUG：详细的调试信息
- INFO：一般信息
- WARNING：警告信息
- ERROR：错误信息
- CRITICAL：严重错误信息

日志格式可以自定义，支持以下格式变量：

- `%(asctime)s`：时间戳
- `%(levelname)s`：日志级别
- `%(processName)s`：进程名
- `%(task_name)s`：任务名（仅任务日志）
- `%(task_id)s`：任务ID（仅任务日志）
- `%(message)s`：日志消息

### 文件日志配置

可以将Celery日志输出到文件：

```python
# celeryconfig.py
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logger = logging.getLogger('celery')
logger.setLevel(logging.INFO)

# 创建文件处理器
fh = RotatingFileHandler('celery.log', maxBytes=10*1024*1024, backupCount=5)
fh.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter('[%(asctime)s: %(levelname)s/%(processName)s] %(message)s')
fh.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(fh)

# Celery配置
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
```

### 多进程日志处理

由于Celery使用多进程处理任务，需要特别注意日志处理。以下是一些建议：

1. **使用RotatingFileHandler**：避免多进程写入同一文件时的竞争条件
2. **使用进程ID**：在日志文件名中包含进程ID，避免冲突
3. **使用中央日志系统**：将日志发送到中央日志系统，如ELK Stack

### 集成外部日志系统

将Celery日志集成到外部日志系统是生产环境的最佳实践：

**1. 集成ELK Stack**：

```python
# celeryconfig.py
import logging
from elasticsearch import Elasticsearch
from pythonjsonlogger import jsonlogger
from logstash_async.handler import AsynchronousLogstashHandler

# 配置Logstash
logstash_handler = AsynchronousLogstashHandler(
    'logstash_host', 5000, database_path='logstash.db')
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(processName)s %(task_name)s %(task_id)s %(message)s')
logstash_handler.setFormatter(formatter)

# 配置Celery日志
logger = logging.getLogger('celery')
logger.addHandler(logstash_handler)
```

**2. 集成Sentry**：

```bash
pip install sentry-sdk
```

```python
# 在项目入口文件中
sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[CeleryIntegration()],
    traces_sample_rate=1.0,
)
```

## 任务状态管理

### 任务状态查询

可以通过以下方式查询任务状态：

**1. 使用AsyncResult**：

```python
from celery.result import AsyncResult

# 获取任务结果
result = AsyncResult('task_id')

# 检查任务状态
print(f"Task status: {result.status}")
print(f"Task successful: {result.successful()}")
print(f"Task failed: {result.failed()}")
print(f"Task ready: {result.ready()}")
```

**2. 使用Flower Web界面**：

通过Flower界面可以直观地查看所有任务的状态和详情。

**3. 使用Celery API**：

```python
from celery.app.control import Control

control = Control(app)
tasks = control.inspect().active()  # 获取活跃任务
print(tasks)
```

### 任务结果跟踪

要跟踪任务结果，需要配置结果后端：

```python
# celeryconfig.py
result_backend = 'redis://localhost:6379/0'
task_track_started = True  # 跟踪任务开始状态
result_expires = 3600  # 结果过期时间（秒）
```

在任务中，可以通过更新状态来提供进度信息：

```python
@app.task(bind=True)
def long_running_task(self, iterations):
    for i in range(iterations):
        # 执行部分工作
        time.sleep(1)
        
        # 更新进度状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': iterations,
                'percentage': (i + 1) / iterations * 100
            }
        )
    
    return {'status': 'completed', 'result': iterations}
```

### 任务取消与终止

**取消任务**：

```python
# 从应用中撤销任务
app.control.revoke('task_id', terminate=False)  # 仅撤销未开始的任务

# 从任务结果撤销
result = AsyncResult('task_id')
result.revoke()
```

**终止任务**：

```python
# 强制终止正在执行的任务
app.control.revoke('task_id', terminate=True, signal='SIGKILL')
```

### 任务优先级管理

Celery支持任务优先级，可以通过设置`priority`参数来指定任务的优先级：

```python
# 提交高优先级任务
task.apply_async(args=[1, 2], priority=9)

# 提交低优先级任务
task.apply_async(args=[3, 4], priority=1)
```

默认情况下，优先级范围是0-9，数字越大优先级越高。可以在配置中修改优先级范围：

```python
# celeryconfig.py
task_queue_max_priority = 10  # 设置最大优先级为10
```

## 工作进程管理

### 工作进程生命周期

工作进程的生命周期包括：

1. **启动**：加载配置，连接到Broker和结果后端
2. **运行**：处理任务，发送结果
3. **关闭**：处理完当前任务后正常退出
4. **崩溃**：异常退出，需要重新启动

### 进程池设置

可以通过配置来控制工作进程池的大小和行为：

```bash
# 启动指定数量的工作进程
celery -A your_project worker --loglevel=info --concurrency=4
```

```python
# celeryconfig.py
worker_concurrency = 4  # 并发工作进程数
worker_prefetch_multiplier = 1  # 预取任务数
worker_max_tasks_per_child = 1000  # 每个工作进程最多执行的任务数
```

### 工作进程健康检查

可以通过以下方式检查工作进程的健康状态：

**1. 使用Flower**：

Flower界面提供了工作进程的实时状态和健康信息。

**2. 使用Celery API**：

```python
from celery.app.control import Control

control = Control(app)

# 检查工作进程状态
status = control.ping()
print(f"Worker status: {status}")

# 获取工作进程统计信息
stats = control.stats()
print(f"Worker stats: {stats}")
```

**3. 自定义健康检查任务**：

```python
@app.task
def health_check():
    """健康检查任务"""
    import psutil
    import os
    
    # 获取进程信息
    process = psutil.Process(os.getpid())
    
    # 收集健康信息
    health_info = {
        'cpu_percent': process.cpu_percent(interval=1),
        'memory_percent': process.memory_percent(),
        'task_count': getattr(health_check, '_task_count', 0),
        'timestamp': datetime.now().isoformat()
    }
    
    # 更新任务计数
    health_check._task_count = getattr(health_check, '_task_count', 0) + 1
    
    return health_info
```

### 工作进程热重启

可以在不中断服务的情况下重启工作进程：

```bash
# 发送HUP信号重启工作进程
kill -HUP $(pgrep -f 'celery worker')

# 或者使用Celery控制命令
celery -A your_project control restart
```

### 工作进程资源限制

可以为工作进程设置资源限制，防止单个任务消耗过多资源：

```python
# celeryconfig.py

# 软时间限制（秒），超过后会抛出SoftTimeLimitExceeded异常
task_soft_time_limit = 60

# 硬时间限制（秒），超过后会被强制终止
task_time_limit = 120

# 任务内存限制（MB）
worker_max_memory_per_child = 200  # 200MB
```

## 系统级监控

### 系统资源监控

监控Celery运行的系统资源对于确保系统稳定性至关重要。可以使用以下工具：

1. **top/htop**：Linux系统资源监控命令
2. **psutil**：Python库，用于获取系统和进程信息
3. **Node Exporter**：Prometheus的系统监控组件

### 集成Prometheus

Prometheus是一个强大的监控系统，适合监控Celery及其运行环境。

**安装依赖**：

```bash
pip install prometheus_client
```

**基本配置**：

```python
# 在Celery应用中集成Prometheus
from prometheus_client import Counter, Histogram, start_http_server

# 定义指标
TASK_COUNTER = Counter('celery_tasks_total', 'Total number of tasks by state', ['state'])
TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task duration in seconds', ['task_name'])

# 创建任务装饰器
def prometheus_task(task_func):
    @functools.wraps(task_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = task_func(*args, **kwargs)
            TASK_COUNTER.labels(state='success').inc()
            return result
        except Exception as e:
            TASK_COUNTER.labels(state='error').inc()
            raise
        finally:
            duration = time.time() - start_time
            TASK_DURATION.labels(task_name=task_func.__name__).observe(duration)
    return wrapper

# 在任务上使用装饰器
@app.task
@prometheus_task
def my_task():
    # 任务逻辑
    pass

# 启动Prometheus HTTP服务器
start_http_server(8000)
```

### 集成Grafana

Grafana可以连接Prometheus作为数据源，创建美观的监控面板。

**基本步骤**：

1. 安装Grafana
2. 配置Prometheus作为数据源
3. 创建Celery监控面板

可以导入社区维护的Celery监控面板模板，例如面板ID：10086。

### 自定义监控指标

除了内置指标，还可以定义自定义指标来监控特定业务逻辑：

```python
from prometheus_client import Gauge

# 定义自定义指标
QUEUE_SIZE = Gauge('celery_queue_size', 'Size of specific queue', ['queue_name'])
ACTIVE_USERS = Gauge('active_users', 'Number of active users')

# 更新指标
QUEUE_SIZE.labels(queue_name='default').set(get_queue_size('default'))
ACTIVE_USERS.set(get_active_users_count())
```

## 告警与通知

### 任务失败告警

当任务失败时，及时收到告警可以帮助快速响应问题：

**使用Celery信号**：

```python
from celery.signals import task_failure
import smtplib
from email.message import EmailMessage

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """任务失败时发送邮件告警"""
    msg = EmailMessage()
    msg.set_content(f"任务失败: {sender.name}\n任务ID: {task_id}\n错误: {exception}")
    msg['Subject'] = f'任务失败告警: {sender.name}'
    msg['From'] = 'alerts@example.com'
    msg['To'] = 'admin@example.com'
    
    # 发送邮件
    server = smtplib.SMTP('smtp.example.com')
    server.send_message(msg)
    server.quit()
```

### 系统异常告警

除了任务失败，还需要监控系统级别的异常：

```python
from celery.signals import worker_ready, worker_shutdown, worker_process_init, worker_process_shutdown

@worker_shutdown.connect
def worker_shutdown_handler(sender, **kwargs):
    """工作进程关闭时发送通知"""
    # 发送通知...

@worker_shutdown.connect
def worker_crash_handler(sender, exitcode, **kwargs):
    """工作进程异常退出时发送告警"""
    if exitcode != 0:
        # 发送告警...
```

### 集成第三方告警系统

将Celery告警集成到成熟的告警系统中可以提高管理效率：

**1. 集成Sentry**：

```python
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[CeleryIntegration()],
    traces_sample_rate=1.0,
    # 配置告警规则
    alerts={
        "failure_rate": {
            "threshold": 5,  # 5%的失败率
            "time_window": 60,  # 60秒
        }
    }
)
```

**2. 集成PagerDuty**：

```python
import pypd

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """任务失败时创建PagerDuty事件"""
    pypd.EventV2.create(
        routing_key='your-pagerduty-integration-key',
        event_action='trigger',
        payload={
            'summary': f'任务失败: {sender.name}',
            'severity': 'error',
            'source': 'celery-worker',
            'details': {
                'task_id': task_id,
                'exception': str(exception),
                'task': sender.name
            }
        }
    )
```

## Beat监控与管理

### Beat状态监控

监控Celery Beat进程的状态和健康情况：

**1. 使用Flower**：

Flower提供了Beat状态页面，可以查看Beat的运行状态和调度任务。

**2. 自定义监控**：

```python
import requests
import time
from datetime import datetime

def monitor_beat(flower_url='http://localhost:5555', check_interval=60):
    """监控Beat状态"""
    while True:
        try:
            # 从Flower API获取Beat状态
            response = requests.get(f"{flower_url}/api/beat")
            if response.status_code == 200:
                beat_status = response.json()
                if beat_status.get('active'):
                    print(f"Beat is active. Last seen: {beat_status.get('last_seen')}")
                else:
                    print("WARNING: Beat is not active!")
                    # 发送告警...
            else:
                print(f"Failed to get Beat status. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error monitoring Beat: {e}")
            # 发送告警...
        
        time.sleep(check_interval)
```

### Beat进程管理

确保Beat进程稳定运行的最佳实践：

**1. 使用supervisor管理Beat进程**：

```ini
[program:celery-beat]
command=/path/to/celery -A your_project beat --loglevel=info
user=celery
directory=/path/to/your/project
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.err.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
```

**2. 防止Beat进程重复运行**：

```python
# celeryconfig.py
# 使用文件锁防止多个Beat实例
beat_sync_every = 30  # 与文件系统同步的频率（秒）
```

### 定时任务监控

监控定时任务的执行情况：

**1. 记录任务执行历史**：

```python
@app.task(bind=True)
def scheduled_task(self):
    """定时任务，记录执行历史"""
    start_time = time.time()
    try:
        # 任务逻辑
        result = do_work()
        
        # 记录执行成功
        record_task_execution(self.name, status='success', duration=time.time() - start_time)
        return result
    except Exception as e:
        # 记录执行失败
        record_task_execution(self.name, status='error', duration=time.time() - start_time, error=str(e))
        raise

def record_task_execution(task_name, status, duration, error=None):
    """记录任务执行情况到数据库"""
    # 这里实现记录逻辑，可以存储到数据库或日志系统
    pass
```

**2. 监控任务错过执行**：

```python
# 在任务中检查是否错过执行窗口
@app.task(bind=True)
def time_sensitive_task(self):
    scheduled_time = self.request.get('eta')  # 获取计划执行时间
    if scheduled_time:
        now = datetime.now(timezone.utc)
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        delay = (now - scheduled_dt).total_seconds()
        
        if delay > 300:  # 如果延迟超过5分钟
            # 记录错过执行窗口的情况
            record_missed_execution(self.name, delay)
    
    # 任务逻辑
    # ...
```

## 监控最佳实践

### 分层监控策略

采用分层监控策略可以全面覆盖系统的各个方面：

1. **基础设施层**：监控服务器CPU、内存、磁盘等资源
2. **中间件层**：监控Redis/Broker、数据库等
3. **应用层**：监控Celery Worker、Beat等组件
4. **业务层**：监控业务任务执行情况和关键指标

### 监控面板设计

设计有效的监控面板可以帮助快速理解系统状态：

1. **概览面板**：显示系统整体健康状态和关键指标
2. **任务面板**：详细展示任务执行情况、成功率、延迟等
3. **资源面板**：监控系统资源使用情况
4. **告警面板**：展示历史告警和当前未解决的问题

### 日志聚合与分析

集中管理和分析日志对于排查问题至关重要：

1. **集中收集**：使用ELK Stack或Graylog等工具集中收集日志
2. **结构化日志**：使用JSON格式的结构化日志，便于分析
3. **日志搜索**：配置日志索引和搜索功能，便于快速定位问题
4. **日志分析**：使用日志分析工具发现潜在问题和模式

### 性能基线建立

建立性能基线可以帮助识别异常情况：

1. **收集历史数据**：记录正常运行时的性能指标
2. **分析模式**：识别性能的正常波动模式（如工作日vs周末）
3. **设置阈值**：基于基线设置合理的告警阈值
4. **定期审查**：定期审查基线，适应系统变化

### 常见问题排查

以下是一些常见问题的排查方法：

**1. 任务队列积压**：
   - 增加工作进程数量
   - 检查工作进程是否正常运行
   - 分析任务执行时间是否过长

**2. 任务频繁失败**：
   - 检查错误日志，确定失败原因
   - 检查外部依赖是否正常（数据库、API等）
   - 考虑增加重试机制和错误处理

**3. 工作进程崩溃**：
   - 检查是否有内存泄漏
   - 调整任务超时设置
   - 配置进程自动重启

**4. Broker连接问题**：
   - 检查网络连接
   - 验证认证信息
   - 监控Broker资源使用情况

## 实践示例

下面通过一个完整的示例来演示Celery监控与管理的各种功能和最佳实践。

### 示例代码

```python
# monitoring_example.py - Celery监控与管理示例

from celery import Celery
import time
import random
import logging
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import functools
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='celery_monitoring.log'
)
logger = logging.getLogger(__name__)

# 创建Celery应用
app = Celery('monitoring_example',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['monitoring_example'])

# 配置
app.conf.update(
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    
    # 日志配置
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # 工作进程配置
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # 任务配置
    task_soft_time_limit=60,
    task_time_limit=120,
    
    # 结果配置
    result_expires=3600,
)

# ==================== Prometheus指标 ====================

# 任务计数器
TASK_COUNTER = Counter('celery_tasks_total', 'Total number of tasks by state', ['state', 'task_name'])

# 任务执行时间直方图
TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task duration in seconds', ['task_name'])

# 活跃任务数量
ACTIVE_TASKS = Gauge('celery_active_tasks', 'Number of active tasks')

# 任务队列长度
QUEUE_SIZE = Gauge('celery_queue_size', 'Size of task queue', ['queue_name'])

# ==================== 任务装饰器 ====================

def monitored_task(task_func):
    """任务监控装饰器"""
    @functools.wraps(task_func)
    def wrapper(*args, **kwargs):
        task_name = task_func.__name__
        
        # 增加活跃任务计数
        ACTIVE_TASKS.inc()
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 执行任务
            result = task_func(*args, **kwargs)
            
            # 记录成功
            TASK_COUNTER.labels(state='success', task_name=task_name).inc()
            logger.info(f"Task {task_name} completed successfully")
            
            return result
        except Exception as e:
            # 记录失败
            TASK_COUNTER.labels(state='error', task_name=task_name).inc()
            logger.error(f"Task {task_name} failed: {str(e)}")
            
            # 这里可以添加告警逻辑，如发送邮件、短信等
            # send_alert(f"Task {task_name} failed", str(e))
            
            raise
        finally:
            # 更新任务执行时间
            duration = time.time() - start_time
            TASK_DURATION.labels(task_name=task_name).observe(duration)
            
            # 减少活跃任务计数
            ACTIVE_TASKS.dec()
            
            # 记录执行时间
            logger.info(f"Task {task_name} took {duration:.2f} seconds")
    
    return wrapper

# ==================== 任务定义 ====================

@app.task(bind=True)
@monitored_task
def basic_task(self, x, y):
    """基础任务示例"""
    logger.info(f"Executing basic_task with args: {x}, {y}")
    time.sleep(0.5)  # 模拟工作
    return x + y


@app.task(bind=True)
@monitored_task
def long_running_task(self, iterations):
    """长时间运行的任务示例，带进度更新"""
    logger.info(f"Executing long_running_task with {iterations} iterations")
    
    for i in range(iterations):
        # 模拟工作
        time.sleep(0.1)
        
        # 更新进度
        progress = (i + 1) / iterations * 100
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': iterations,
                'progress': progress
            }
        )
    
    logger.info(f"long_running_task completed {iterations} iterations")
    return {'completed_iterations': iterations}


@app.task(bind=True)
@monitored_task
def unstable_task(self):
    """不稳定任务示例，可能会失败"""
    logger.info("Executing unstable_task")
    
    # 30%的概率失败
    if random.random() < 0.3:
        error_msg = "Task failed randomly"
        logger.warning(error_msg)
        raise Exception(error_msg)
    
    time.sleep(1)  # 模拟工作
    logger.info("unstable_task completed successfully")
    return {'status': 'success'}


@app.task(bind=True)
@monitored_task
def resource_intensive_task(self):
    """资源密集型任务示例"""
    logger.info("Executing resource_intensive_task")
    
    # 模拟CPU密集型计算
    result = 0
    for i in range(10_000_000):
        result += i
    
    logger.info(f"resource_intensive_task completed, result: {result}")
    return {'result': result}


@app.task(bind=True)
@monitored_task
def external_dependency_task(self):
    """依赖外部服务的任务示例"""
    logger.info("Executing external_dependency_task")
    
    try:
        # 模拟调用外部API
        # 实际应用中，这里会调用真实的API
        if random.random() < 0.2:  # 20%的概率API调用失败
            raise requests.exceptions.RequestException("External API request failed")
        
        time.sleep(0.5)  # 模拟网络延迟
        logger.info("external_dependency_task completed successfully")
        return {'api_response': 'success'}
    except requests.exceptions.RequestException as e:
        logger.error(f"External API call failed: {str(e)}")
        # 这里可以添加重试逻辑或其他错误处理
        raise

# ==================== 监控工具 ====================

def update_queue_metrics():
    """更新队列长度指标"""
    try:
        # 获取所有队列的长度
        # 注意：这需要配置正确的权限访问Redis
        import redis
        r = redis.Redis()
        
        # 获取所有以 'celery' 开头的列表（默认队列名）
        queues = r.keys('celery*')
        for queue in queues:
            queue_name = queue.decode('utf-8')
            queue_length = r.llen(queue)
            QUEUE_SIZE.labels(queue_name=queue_name).set(queue_length)
            logger.info(f"Queue {queue_name} length: {queue_length}")
    except Exception as e:
        logger.error(f"Failed to update queue metrics: {str(e)}")


# 创建一个定期更新队列长度的任务
@app.task(bind=True)
def update_metrics_task(self):
    """定期更新监控指标的任务"""
    try:
        update_queue_metrics()
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"update_metrics_task failed: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# ==================== 定时任务配置 ====================

# 配置定时任务
app.conf.beat_schedule = {
    'update-metrics-every-minute': {
        'task': 'monitoring_example.update_metrics_task',
        'schedule': 60.0,  # 每分钟执行一次
    },
    'run-unstable-task-every-5-minutes': {
        'task': 'monitoring_example.unstable_task',
        'schedule': 300.0,  # 每5分钟执行一次
    },
}

# ==================== 启动Prometheus HTTP服务器 ====================

def start_metrics_server(port=8000):
    """启动Prometheus指标HTTP服务器"""
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start Prometheus metrics server: {str(e)}")


# ==================== 启动和配置 ====================

def configure_monitoring():
    """配置监控"""
    # 启动Prometheus指标服务器
    start_metrics_server()
    
    # 初始更新队列指标
    update_queue_metrics()
    
    logger.info("Monitoring configured successfully")


# 如果直接运行此文件，则配置监控并显示使用说明
def print_usage_instructions():
    print("Celery监控与管理示例")
    print("=====================")
    print("\n这个示例演示了如何监控和管理Celery系统，包括:")
    print("1. 任务执行监控")
    print("2. Prometheus指标集成")
    print("3. 日志管理")
    print("4. 任务状态跟踪")
    print("\n使用方法:")
    print("1. 确保Redis服务已启动")
    print("2. 安装依赖: pip install celery redis prometheus_client requests")
    print("\n运行组件:")
    print("1. 启动Celery Worker:")
    print("   celery -A monitoring_example worker --loglevel=info")
    print("\n2. 启动Celery Beat:")
    print("   celery -A monitoring_example beat --loglevel=info")
    print("\n3. 启动Flower监控:")
    print("   celery -A monitoring_example flower")
    print("\n4. 查看Prometheus指标:")
    print("   访问 http://localhost:8000/metrics")
    print("\n提交测试任务:")
    print("   python -c """
    print("   from monitoring_example import *")
    print("   configure_monitoring()")
    print("   basic_task.delay(10, 20)")
    print("   long_running_task.delay(100)")
    print("   unstable_task.delay()")
    print("   """)


if __name__ == '__main__':
    configure_monitoring()
    print_usage_instructions()
```

### 运行示例

1. 确保Redis服务已启动
2. 安装必要的依赖：
   ```bash
   pip install celery redis prometheus_client requests
   ```
3. 保存上述代码为`monitoring_example.py`
4. 启动监控配置：
   ```bash
   python monitoring_example.py
   ```
5. 启动Celery Worker：
   ```bash
   celery -A monitoring_example worker --loglevel=info
   ```
6. 在另一个终端启动Celery Beat：
   ```bash
   celery -A monitoring_example beat --loglevel=info
   ```
7. 启动Flower监控：
   ```bash
   celery -A monitoring_example flower
   ```

### 观察监控结果

通过以下方式观察监控结果：

1. **Flower界面**：访问 http://localhost:5555 查看实时监控信息
2. **Prometheus指标**：访问 http://localhost:8000/metrics 查看指标数据
3. **日志文件**：查看 `celery_monitoring.log` 文件
4. **提交测试任务**：使用Python代码或Flower界面提交测试任务

通过这个示例，您可以了解到如何全面监控和管理Celery系统，包括任务执行监控、指标收集、日志管理等多个方面。在实际应用中，可以根据需要扩展和定制监控功能。