# Celery高级特性：定时任务与调度

本章将详细介绍Celery的定时任务与调度功能，这是Celery提供的强大高级特性之一。通过定时任务与调度，我们可以让任务按照预定的时间或周期自动执行，这对于需要定期执行的操作（如数据备份、报表生成、系统清理等）非常有用。

## 目录
- [定时任务概述](#定时任务概述)
  - [什么是定时任务](#什么是定时任务)
  - [应用场景](#应用场景)
  - [Celery Beat介绍](#celery-beat介绍)
- [启用Celery Beat](#启用celery-beat)
  - [基本配置](#基本配置)
  - [启动Celery Beat服务](#启动celery-beat服务)
- [定时任务配置方式](#定时任务配置方式)
  - [装饰器方式](#装饰器方式)
  - [配置文件方式](#配置文件方式)
  - [数据库方式](#数据库方式)
- [调度表达式详解](#调度表达式详解)
  - [crontab表达式](#crontab表达式)
  - [interval间隔表达式](#interval间隔表达式)
  - [solar日照表达式](#solar日照表达式)
  - [组合调度表达式](#组合调度表达式)
- [定时任务高级特性](#定时任务高级特性)
  - [任务参数传递](#任务参数传递)
  - [任务过期时间设置](#任务过期时间设置)
  - [任务执行超时设置](#任务执行超时设置)
  - [任务重试设置](#任务重试设置)
- [动态添加与移除定时任务](#动态添加与移除定时任务)
  - [数据库调度器](#数据库调度器)
  - [自定义调度器](#自定义调度器)
- [定时任务监控](#定时任务监控)
  - [日志监控](#日志监控)
  - [状态检查](#状态检查)
- [定时任务最佳实践](#定时任务最佳实践)
  - [任务设计原则](#任务设计原则)
  - [性能优化](#性能优化)
  - [错误处理](#错误处理)
- [实践示例](#实践示例)

## 定时任务概述

### 什么是定时任务

定时任务是指按照预定的时间或周期性地自动执行的任务。在Celery中，定时任务通过Celery Beat调度器来管理和触发。

### 应用场景

定时任务在许多场景中都非常有用，例如：

- 数据备份和同步
- 报表生成和发送
- 系统清理和维护
- 数据统计和分析
- 定期通知和提醒
- 接口调用和数据采集
- 缓存更新和预热

### Celery Beat介绍

Celery Beat是Celery的调度器组件，负责按照预定的时间表调度任务。它是一个独立运行的进程，可以读取任务调度配置，并在适当的时间将任务发送到消息代理中供Worker执行。

**工作原理**：
1. Celery Beat读取任务调度配置
2. 根据配置计算下一次任务执行的时间
3. 在到达执行时间时，创建任务实例并发送到消息代理
4. Worker从消息代理获取任务并执行
5. Celery Beat继续监控下一次任务执行时间

## 启用Celery Beat

### 基本配置

要使用Celery Beat，首先需要在Celery应用中配置定时任务。

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

# 配置Celery Beat的定时任务
app.conf.beat_schedule = {
    # 任务1: 每10秒执行一次
    'task-every-10-seconds': {
        'task': 'tasks.add',  # 任务名称
        'schedule': 10.0,     # 间隔时间（秒）
        'args': (16, 16)      # 任务参数
    },
    # 任务2: 每天凌晨2点执行
    'task-daily-at-2am': {
        'task': 'tasks.multiply',
        'schedule': crontab(hour=2, minute=0),
        'args': (10, 10)
    },
}

# 设置时区（对于crontab任务很重要）
app.conf.timezone = 'Asia/Shanghai'
```

### 启动Celery Beat服务

配置完成后，需要启动Celery Beat服务。通常，我们需要同时启动Worker和Beat：

```bash
# 启动Worker
bash$ celery -A tasks worker --loglevel=info

# 启动Beat（在另一个终端）
bash$ celery -A tasks beat --loglevel=info

# 或者在一个命令中同时启动Worker和Beat（仅用于开发环境）
bash$ celery -A tasks worker --beat --loglevel=info
```

**注意**：在生产环境中，建议将Worker和Beat作为单独的服务运行，以便于管理和监控。

## 定时任务配置方式

Celery提供了多种配置定时任务的方式，下面介绍常用的几种。

### 装饰器方式

使用装饰器是最直接的配置定时任务的方式。

```python
from celery import Celery
from celery.schedules import crontab
from celery.decorators import periodic_task

app = Celery('tasks')

# 使用装饰器定义定时任务
@periodic_task(run_every=10.0)  # 每10秒执行一次
def add_periodic(x=10, y=20):
    print(f'Running periodic task: {x} + {y} = {x+y}')
    return x + y

# 使用crontab表达式
@periodic_task(run_every=crontab(minute='*/5'))  # 每5分钟执行一次
def multiply_periodic(x=5, y=5):
    print(f'Running periodic task: {x} * {y} = {x*y}')
    return x * y
```

**注意**：从Celery 4.0开始，`@periodic_task`装饰器已被弃用，推荐使用`@app.task`配合配置文件的方式。

### 配置文件方式

在配置文件中定义定时任务是更灵活和推荐的方式，特别是对于需要集中管理的复杂应用。

```python
# celeryconfig.py
from celery.schedules import crontab, solar

# 定时任务配置
beat_schedule = {
    # 每30秒执行一次的任务
    'add-every-30-seconds': {
        'task': 'tasks.add',
        'schedule': 30.0,
        'args': (16, 16)
    },
    
    # 每天早上7:30执行的任务
    'morning-report': {
        'task': 'tasks.generate_report',
        'schedule': crontab(hour=7, minute=30),
        'args': ('daily',)
    },
    
    # 每周一早上9点执行的任务
    'weekly-summary': {
        'task': 'tasks.generate_summary',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # day_of_week: 0-6, 0是周日
        'args': ('weekly',)
    },
    
    # 每月1号凌晨1点执行的任务
    'monthly-backup': {
        'task': 'tasks.perform_backup',
        'schedule': crontab(hour=1, minute=0, day_of_month=1),
        'args': ('full',)
    },
    
    # 使用日照表达式（日出后15分钟执行）
    'morning-task': {
        'task': 'tasks.morning_task',
        'schedule': solar('sunrise', offset=15 * 60),  # 日出后15分钟
    },
}

# 时区设置
timezone = 'Asia/Shanghai'
```

然后在主应用中导入这个配置：

```python
# tasks.py
from celery import Celery

app = Celery('tasks')

# 加载配置
app.config_from_object('celeryconfig')

@app.task
def add(x, y):
    return x + y

@app.task
def generate_report(report_type):
    print(f'Generating {report_type} report')
    # 生成报表的逻辑
    return f'{report_type} report generated'

# 其他任务定义...
```

### 数据库方式

对于需要动态管理定时任务的场景，可以使用数据库来存储和管理定时任务配置。Celery提供了多种数据库调度器，例如Django Celery Beat。

#### 使用Django Celery Beat

**安装**：

```bash
pip install django-celery-beat
```

**配置**：

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_celery_beat',
]

# Celery配置
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

**数据库迁移**：

```bash
python manage.py migrate
```

然后可以通过Django管理界面或API动态创建、修改和删除定时任务。

## 调度表达式详解

Celery提供了几种不同类型的调度表达式，用于定义任务的执行计划。

### crontab表达式

crontab表达式是最灵活和常用的调度表达式，类似于Linux系统的crontab格式。

**基本语法**：

```python
from celery.schedules import crontab

# 每小时执行一次
crontab(minute=0)

# 每天早上8:30执行
crontab(hour=8, minute=30)

# 每5分钟执行一次
crontab(minute='*/5')

# 每天的9点到17点，每30分钟执行一次
crontab(minute='*/30', hour='9-17')

# 每周一到周五的早上9点执行
crontab(hour=9, minute=0, day_of_week=1-5)

# 每月1号和15号的凌晨3点执行
crontab(hour=3, minute=0, day_of_month='1,15')
```

**参数说明**：

- `minute`: 分钟，0-59
- `hour`: 小时，0-23
- `day_of_week`: 星期几，0-6（0是周日）或'mon'-'sun'
- `day_of_month`: 月份中的日期，1-31
- `month_of_year`: 年份中的月份，1-12或'jan'-'dec'

每个参数都可以是整数、字符串、列表或元组，支持以下特殊格式：

- `*`: 匹配所有值
- `*/n`: 每n个单位执行一次
- `a-b`: 匹配a到b之间的所有值
- `a,b,c`: 匹配指定的值列表

### interval间隔表达式

interval表达式用于定义固定时间间隔执行的任务。

**基本语法**：

```python
from celery.schedules import interval

# 每10秒执行一次
interval(seconds=10)

# 每5分钟执行一次
interval(minutes=5)

# 每2小时执行一次
interval(hours=2)

# 每3天执行一次
interval(days=3)
```

**参数说明**：

- `microseconds`: 微秒
- `milliseconds`: 毫秒
- `seconds`: 秒
- `minutes`: 分钟
- `hours`: 小时
- `days`: 天

也可以直接使用数字作为interval：

```python
# 每10秒执行一次
'schedule': 10.0
```

### solar日照表达式

对于需要根据日出日落时间执行的任务，可以使用solar表达式。

**基本语法**：

```python
from celery.schedules import solar

# 日出时执行
solar('sunrise')

# 日落时执行
solar('sunset')

# 日出后15分钟执行
solar('sunrise', offset=15 * 60)

# 日落前30分钟执行
solar('sunset', offset=-30 * 60)
```

**参数说明**：

- `event`: 'sunrise'（日出）或'sunset'（日落）
- `offset`: 偏移秒数，正数表示事件后，负数表示事件前
- `latitude`: 纬度（可选）
- `longitude`: 经度（可选）

如果不指定经纬度，将使用系统默认值或在配置中设置的`beat_schedule_solar_latitude`和`beat_schedule_solar_longitude`。

### 组合调度表达式

对于复杂的调度需求，可以组合使用不同的调度表达式，或者创建自定义的调度器。

**示例：自定义调度逻辑**

```python
from celery.schedules import base
import datetime

class CustomSchedule(base.BaseSchedule):
    """自定义调度器，实现工作日的上午10点和下午3点执行"""
    
    def is_due(self, last_run_at):
        now = datetime.datetime.now()
        
        # 检查是否是工作日（周一到周五）
        if now.weekday() >= 5:  # 5是周六，6是周日
            # 计算到下周一的时间
            days_to_monday = 7 - now.weekday()
            next_run = now + datetime.timedelta(days=days_to_monday)
            next_run = next_run.replace(hour=10, minute=0, second=0, microsecond=0)
            return (False, (next_run - now).total_seconds())
        
        # 检查当前时间是否在工作时间内
        if 9 <= now.hour < 17:  # 9点到17点之间
            # 确定下一个执行时间点
            if now.hour < 10 or (now.hour == 10 and now.minute < 0):
                # 今天上午10点
                next_run = now.replace(hour=10, minute=0, second=0, microsecond=0)
            elif now.hour < 15 or (now.hour == 15 and now.minute < 0):
                # 今天下午3点
                next_run = now.replace(hour=15, minute=0, second=0, microsecond=0)
            else:
                # 下一个工作日上午10点
                next_run = now + datetime.timedelta(days=1)
                if next_run.weekday() >= 5:  # 如果是周末
                    days_to_monday = 7 - next_run.weekday()
                    next_run = next_run + datetime.timedelta(days=days_to_monday)
                next_run = next_run.replace(hour=10, minute=0, second=0, microsecond=0)
            
            # 计算距离下次执行的时间
            wait_seconds = (next_run - now).total_seconds()
            return (wait_seconds <= 0, max(0, wait_seconds))
        else:
            # 非工作时间，计算到下一个工作时间的开始
            if now.hour >= 17:  # 下午5点之后
                next_run = now + datetime.timedelta(days=1)
            else:  # 上午9点之前
                next_run = now
            
            # 设置为上午10点
            next_run = next_run.replace(hour=10, minute=0, second=0, microsecond=0)
            
            # 检查是否是周末
            if next_run.weekday() >= 5:
                days_to_monday = 7 - next_run.weekday()
                next_run = next_run + datetime.timedelta(days=days_to_monday)
            
            # 计算等待时间
            wait_seconds = (next_run - now).total_seconds()
            return (False, wait_seconds)
    
    def __repr__(self):
        return '<CustomSchedule: 工作日上午10点和下午3点>'

# 在配置中使用自定义调度器
app.conf.beat_schedule = {
    'custom-schedule-task': {
        'task': 'tasks.custom_task',
        'schedule': CustomSchedule(),
        'args': (),
    },
}
```

## 定时任务高级特性

### 任务参数传递

为定时任务传递参数有几种方式：

**1. 固定参数**

```python
app.conf.beat_schedule = {
    'task-with-args': {
        'task': 'tasks.add',
        'schedule': 10.0,
        'args': (10, 20),        # 位置参数
        'kwargs': {'z': 30},     # 关键字参数
    },
}
```

**2. 动态参数**

如果需要每次执行时使用不同的参数，可以在任务中动态生成：

```python
@app.task
def dynamic_args_task():
    # 动态生成参数
    import random
    x = random.randint(1, 100)
    y = random.randint(1, 100)
    
    # 执行实际操作
    print(f'Processing with dynamic args: {x}, {y}')
    return x + y
```

### 任务过期时间设置

可以为定时任务设置过期时间，避免任务堆积：

```python
app.conf.beat_schedule = {
    'task-with-expires': {
        'task': 'tasks.long_running_task',
        'schedule': 60.0,
        'options': {
            'expires': 30,  # 30秒后过期
        },
    },
}
```

### 任务执行超时设置

设置任务执行的最大时间：

```python
app.conf.beat_schedule = {
    'task-with-timeout': {
        'task': 'tasks.long_running_task',
        'schedule': 60.0,
        'options': {
            'time_limit': 10,  # 硬超时，超过10秒强制终止
            'soft_time_limit': 5,  # 软超时，超过5秒抛出异常
        },
    },
}
```

### 任务重试设置

配置任务失败时的重试策略：

```python
app.conf.beat_schedule = {
    'task-with-retry': {
        'task': 'tasks.unstable_task',
        'schedule': 60.0,
        'options': {
            'autoretry_for': (Exception,),
            'retry_kwargs': {'max_retries': 3},
            'retry_backoff': 2,  # 指数退避策略
        },
    },
}
```

## 动态添加与移除定时任务

对于需要在运行时动态管理定时任务的场景，可以使用数据库调度器或自定义调度器。

### 数据库调度器

以Django Celery Beat为例，可以通过API动态管理定时任务：

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json

# 创建间隔调度（每10秒执行一次）
interval, created = IntervalSchedule.objects.get_or_create(
    every=10,
    period=IntervalSchedule.SECONDS,
)

# 创建定时任务
PeriodicTask.objects.create(
    interval=interval,  # 引用间隔调度
    name='动态添加的间隔任务',  # 任务名称，必须唯一
    task='tasks.add',  # 任务路径
    args=json.dumps([10, 20]),  # 任务参数，必须是JSON格式的字符串
)

# 创建cron调度（每天凌晨2点执行）
crontab, created = CrontabSchedule.objects.get_or_create(
    hour=2,
    minute=0,
)

# 创建定时任务
PeriodicTask.objects.create(
    crontab=crontab,  # 引用cron调度
    name='动态添加的Cron任务',
    task='tasks.multiply',
    args=json.dumps([10, 20]),
)

# 禁用任务
task = PeriodicTask.objects.get(name='动态添加的间隔任务')
task.enabled = False
task.save()

# 删除任务
task.delete()
```

### 自定义调度器

如果不使用Django，也可以实现自定义调度器来动态管理任务：

```python
from celery import Celery
from celery.beat import Scheduler, ScheduleEntry
import time
import threading

# 内存中的任务存储
class MemoryTaskStore:
    def __init__(self):
        self.tasks = {}
        self.lock = threading.RLock()
    
    def add_task(self, name, task, schedule, args=None, kwargs=None, options=None):
        with self.lock:
            self.tasks[name] = {
                'task': task,
                'schedule': schedule,
                'args': args or (),
                'kwargs': kwargs or {},
                'options': options or {}
            }
    
    def remove_task(self, name):
        with self.lock:
            if name in self.tasks:
                del self.tasks[name]
    
    def get_tasks(self):
        with self.lock:
            return self.tasks.copy()

# 自定义调度器
class DynamicScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        self.task_store = MemoryTaskStore()
        super().__init__(*args, **kwargs)
    
    def schedule_changed(self):
        # 检查调度是否更改
        return True  # 简化实现，总是检查更新
    
    def get_schedule(self):
        # 从任务存储中获取调度
        tasks = self.task_store.get_tasks()
        entries = {}
        
        for name, task_config in tasks.items():
            # 创建调度条目
            entry = ScheduleEntry(
                name=name,
                task=task_config['task'],
                schedule=task_config['schedule'],
                args=task_config['args'],
                kwargs=task_config['kwargs'],
                options=task_config['options'],
                app=self.app
            )
            entries[name] = entry
        
        return entries

# 配置使用自定义调度器
app.conf.beat_scheduler = 'path.to.DynamicScheduler'

# 动态添加/删除任务的API
def add_periodic_task(name, task, schedule, args=None, kwargs=None, options=None):
    # 获取beat实例
    from celery.app.base import Celery
    app = Celery.current_app
    scheduler = app.conf.beat_scheduler_instance
    
    # 添加任务到调度器
    scheduler.task_store.add_task(name, task, schedule, args, kwargs, options)

def remove_periodic_task(name):
    app = Celery.current_app
    scheduler = app.conf.beat_scheduler_instance
    scheduler.task_store.remove_task(name)
```

## 定时任务监控

### 日志监控

确保启用适当的日志级别，以便监控定时任务的执行情况：

```python
# celeryconfig.py

# 日志配置
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
beat_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# 日志级别
worker_loglevel = 'INFO'
beat_loglevel = 'INFO'
```

### 状态检查

可以使用Flower或自定义监控脚本来检查定时任务的执行状态：

**使用Flower**：

```bash
# 安装Flower
pip install flower

# 启动Flower
bash$ celery -A tasks flower
```

然后通过浏览器访问 http://localhost:5555 查看任务执行状态。

**自定义状态检查**：

```python
from celery.result import AsyncResult
from datetime import datetime, timedelta

def check_task_status(task_id, timeout=30):
    """检查任务状态"""
    result = AsyncResult(task_id)
    start_time = datetime.now()
    
    while (datetime.now() - start_time).total_seconds() < timeout:
        if result.ready():
            if result.successful():
                return {'status': 'success', 'result': result.result}
            else:
                return {'status': 'failed', 'error': str(result.result)}
        time.sleep(1)
    
    return {'status': 'timeout'}
```

## 定时任务最佳实践

### 任务设计原则

1. **保持任务简洁**：每个任务应该专注于一个具体功能
2. **幂等性设计**：确保任务重复执行不会产生副作用
3. **错误处理**：实现完善的错误处理和日志记录
4. **超时控制**：为长时间运行的任务设置合理的超时时间
5. **资源清理**：确保任务执行完毕后释放所有资源

### 性能优化

1. **合理设置执行间隔**：避免过于频繁的任务消耗过多资源
2. **批量处理**：对于数据处理任务，考虑批量处理而非单条处理
3. **优先级设置**：为重要任务设置更高的优先级
4. **任务队列分离**：将定时任务与普通任务分离到不同的队列
5. **监控资源使用**：定期检查任务执行的资源消耗情况

### 错误处理

1. **重试策略**：为不稳定的任务配置合适的重试策略
2. **失败通知**：实现任务失败时的通知机制（邮件、短信等）
3. **死信队列**：配置死信队列，处理最终失败的任务
4. **故障转移**：实现关键任务的故障转移机制

## 实践示例

下面通过一个完整的示例来演示Celery定时任务的各种功能和最佳实践。

### 示例代码

```python
# periodic_tasks.py - Celery定时任务示例

from celery import Celery
from celery.schedules import crontab, interval
import time
import random
from datetime import datetime

# 创建Celery应用
app = Celery('periodic_tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['periodic_tasks'])

# 配置
app.conf.update(
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    
    # 定时任务配置
    beat_schedule={
        # 1. 每10秒执行一次的基础任务
        'add-every-10-seconds': {
            'task': 'periodic_tasks.add_numbers',
            'schedule': 10.0,
            'args': (10, 20),
            'options': {
                'expires': 5,  # 5秒后过期
            },
        },
        
        # 2. 每1分钟执行一次的数据处理任务
        'process-data-every-minute': {
            'task': 'periodic_tasks.process_data',
            'schedule': interval(minutes=1),
            'kwargs': {'batch_size': 100},
        },
        
        # 3. 每天上午8点执行的报表生成任务
        'generate-daily-report': {
            'task': 'periodic_tasks.generate_report',
            'schedule': crontab(hour=8, minute=0),
            'args': ('daily',),
            'options': {
                'priority': 9,  # 高优先级
                'time_limit': 300,  # 5分钟超时
            },
        },
        
        # 4. 每周一早上9点执行的清理任务
        'weekly-cleanup': {
            'task': 'periodic_tasks.cleanup_old_data',
            'schedule': crontab(hour=9, minute=0, day_of_week=1),  # 1是周一
            'args': (7,),  # 清理7天前的数据
        },
        
        # 5. 每小时执行一次的健康检查任务
        'health-check-every-hour': {
            'task': 'periodic_tasks.health_check',
            'schedule': crontab(minute=0),  # 每小时的0分钟
        },
    }
)

# ==================== 任务定义 ====================

@app.task(bind=True)
def add_numbers(self, x, y):
    """简单的加法任务示例"""
    print(f"[{datetime.now()}] Executing add_numbers({x}, {y})")
    result = x + y
    print(f"[{datetime.now()}] Result: {result}")
    return result


@app.task(bind=True)
def process_data(self, batch_size=100):
    """数据处理任务，模拟批量处理数据"""
    print(f"[{datetime.now()}] Starting data processing with batch size {batch_size}")
    
    # 模拟数据处理
    processed_count = 0
    try:
        for i in range(batch_size):
            # 模拟处理时间
            time.sleep(0.01)
            processed_count += 1
            
            # 每10个记录更新一次状态
            if i % 10 == 0:
                progress = (i + 1) / batch_size * 100
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'processed': processed_count,
                        'total': batch_size,
                        'progress': progress
                    }
                )
        
        print(f"[{datetime.now()}] Data processing completed. Processed {processed_count} records.")
        return {"status": "success", "processed_count": processed_count}
    
    except Exception as e:
        print(f"[{datetime.now()}] Error in data processing: {str(e)}")
        # 记录错误但不重试，让定时任务下次再尝试
        return {"status": "error", "message": str(e), "processed_count": processed_count}


@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3}, retry_backoff=2)
def generate_report(self, report_type):
    """报表生成任务，包含重试机制"""
    print(f"[{datetime.now()}] Generating {report_type} report (attempt {self.request.retries})")
    
    # 模拟报表生成过程
    try:
        # 模拟一些随机失败
        if random.random() > 0.8 and self.request.retries < 2:
            raise Exception("Random report generation failure")
        
        # 模拟处理时间
        time.sleep(2)
        
        # 生成报表ID
        report_id = f"{report_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        print(f"[{datetime.now()}] {report_type} report generated successfully: {report_id}")
        return {"status": "success", "report_id": report_id, "type": report_type}
    
    except Exception as e:
        print(f"[{datetime.now()}] Failed to generate {report_type} report: {str(e)}")
        # 将触发自动重试
        raise


@app.task(bind=True)
def cleanup_old_data(self, days=7):
    """清理旧数据任务"""
    print(f"[{datetime.now()}] Starting cleanup of data older than {days} days")
    
    # 模拟清理过程
    try:
        # 模拟一些随机延迟
        time.sleep(random.uniform(1, 3))
        
        # 模拟清理的数据量
        cleaned_count = random.randint(100, 1000)
        
        print(f"[{datetime.now()}] Cleanup completed. Removed {cleaned_count} records older than {days} days.")
        return {"status": "success", "cleaned_count": cleaned_count, "days_old": days}
    
    except Exception as e:
        print(f"[{datetime.now()}] Error during cleanup: {str(e)}")
        # 记录错误但不重试，清理任务通常不是关键任务
        return {"status": "error", "message": str(e)}


@app.task(bind=True, ignore_result=True)
def health_check(self):
    """系统健康检查任务，不需要返回结果"""
    print(f"[{datetime.now()}] Performing system health check")
    
    # 模拟健康检查过程
    try:
        # 检查各种系统组件
        checks = {
            'database': True,
            'cache': True,
            'external_service': random.random() > 0.1  # 模拟90%的可用性
        }
        
        # 模拟处理时间
        time.sleep(1)
        
        # 检查是否所有组件都健康
        all_healthy = all(checks.values())
        
        if all_healthy:
            print(f"[{datetime.now()}] All systems healthy")
        else:
            unhealthy_services = [k for k, v in checks.items() if not v]
            print(f"[{datetime.now()}] Health check failed for: {', '.join(unhealthy_services)}")
            # 这里可以添加通知逻辑，如发送邮件或短信
        
    except Exception as e:
        print(f"[{datetime.now()}] Health check error: {str(e)}")


if __name__ == '__main__':
    print("Celery 定时任务示例")
    print("请先启动Redis服务")
    print("\n然后启动Celery Worker和Beat:")
    print("  # 启动Worker")
    print("  celery -A periodic_tasks worker --loglevel=info")
    print("  ")
    print("  # 在另一个终端启动Beat")
    print("  celery -A periodic_tasks beat --loglevel=info")
    print("  ")
    print("或者在开发环境中同时启动Worker和Beat:")
    print("  celery -A periodic_tasks worker --beat --loglevel=info")
```

### 运行示例

1. 确保Redis服务已启动
2. 保存上述代码为`periodic_tasks.py`
3. 启动Celery Worker：
   ```bash
   celery -A periodic_tasks worker --loglevel=info
   ```
4. 在另一个终端启动Celery Beat：
   ```bash
   celery -A periodic_tasks beat --loglevel=info
   ```

### 观察结果

在Worker和Beat的日志中，您将看到定时任务按照配置的时间间隔自动执行。特别是：

- `add_numbers`任务每10秒执行一次
- `process_data`任务每1分钟执行一次
- `generate_report`任务每天上午8点执行
- `cleanup_old_data`任务每周一上午9点执行
- `health_check`任务每小时执行一次

通过这个示例，您可以了解到Celery定时任务的基本使用方法、配置选项以及一些最佳实践。在实际应用中，您可以根据需要调整任务的执行频率、参数和错误处理策略。