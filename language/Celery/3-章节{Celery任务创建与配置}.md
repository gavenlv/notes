# 3-章节{Celery任务创建与配置}

## 1. 任务创建基础

在Celery中，任务是异步执行的基本单元。创建任务是使用Celery的第一步，在这一章中，我们将详细介绍如何创建和配置各种类型的任务。

### 1.1 基本任务创建

创建Celery任务最基本的方法是使用`@app.task`装饰器：

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def add(x, y):
    return x + y
```

这个简单的例子展示了创建Celery任务的基本结构：
1. 导入Celery类
2. 创建Celery应用实例
3. 使用`@app.task`装饰器定义任务函数

### 1.2 任务名称

默认情况下，任务名称是模块名称加上函数名称。例如，上面的任务名称为`tasks.add`。可以通过装饰器参数自定义任务名称：

```python
@app.task(name='custom_add')
def add(x, y):
    return x + y
```

自定义任务名称的好处：
- 避免因模块结构更改导致任务名称变化
- 使用更有意义的名称，便于监控和调试
- 在使用不同模块或不同语言实现相同功能时保持一致性

## 2. 任务装饰器参数详解

`@app.task`装饰器接受多个参数，可以用来配置任务的各种行为。以下是一些常用的装饰器参数：

### 2.1 任务标识相关

- **name**: 任务的唯一标识符
- **base**: 任务的基类，默认为`app.Task`
- **bind**: 是否绑定任务实例到第一个参数(self)

```python
@app.task(bind=True, name='custom_task')
def my_task(self, arg1, arg2):
    # self指向任务实例，可以访问任务状态和方法
    print(f'Task ID: {self.request.id}')
    print(f'Task args: {arg1}, {arg2}')
    return arg1 + arg2
```

### 2.2 任务执行相关

- **max_retries**: 最大重试次数
- **retry_backoff**: 重试间隔的指数退避因子
- **retry_jitter**: 是否在重试间隔中添加随机抖动
- **autoretry_for**: 自动重试的异常类型列表

```python
@app.task(
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=3
)
def unstable_task():
    # 可能会失败的任务
    import random
    if random.random() > 0.5:
        raise Exception('Task failed randomly')
    return 'Success'
```

### 2.3 任务时间控制

- **time_limit**: 任务执行的硬时间限制（秒），超过后会被强制终止
- **soft_time_limit**: 任务执行的软时间限制（秒），超过后会抛出SoftTimeLimitExceeded异常
- **acks_late**: 是否在任务完成后才确认（默认是在开始执行前确认）

```python
@app.task(
    time_limit=30,
    soft_time_limit=20,
    acks_late=True
)
def long_running_task():
    import time
    for i in range(100):
        print(f'Progress: {i}%')
        time.sleep(1)
    return 'Completed'
```

### 2.4 任务结果处理

- **ignore_result**: 是否忽略任务结果
- **store_errors_even_if_ignored**: 即使忽略结果，是否仍然存储错误信息

```python
@app.task(ignore_result=True)
def send_notification(message):
    # 发送通知，不需要返回结果
    print(f'Sending notification: {message}')
    return None  # 结果不会被存储
```

## 3. 任务绑定与上下文访问

### 3.1 任务绑定

使用`bind=True`参数可以将任务实例绑定到函数的第一个参数(self)，这样可以访问任务的上下文和属性：

```python
@app.task(bind=True)
def bind_task(self, arg1):
    # 访问任务请求信息
    print(f'Task ID: {self.request.id}')
    print(f'Task name: {self.name}')
    print(f'Task args: {self.request.args}')
    print(f'Task kwargs: {self.request.kwargs}')
    print(f'Retry count: {self.request.retries}')
    return f'Processed {arg1}'
```

### 3.2 访问任务上下文的方法

绑定任务后，可以访问以下常用方法：

- **self.retry()**: 手动触发任务重试
- **self.update_state()**: 更新任务状态
- **self.get_priority()**: 获取任务优先级
- **self.set_priority()**: 设置任务优先级

```python
@app.task(bind=True)
def retryable_task(self, url):
    try:
        # 尝试访问URL
        import requests
        response = requests.get(url, timeout=5)
        return response.text
    except requests.RequestException as exc:
        # 发生异常时重试
        self.retry(exc=exc, countdown=10, max_retries=3)
```

## 4. 任务签名与部分参数应用

### 4.1 任务签名

任务签名(Signature)是一个包含任务调用参数的对象，可以稍后执行或传递给其他任务：

```python
from celery import signature

# 创建任务签名
add_signature = add.s(10, 20)

# 执行签名
result = add_signature.delay()

# 或者使用apply_async
result = add_signature.apply_async()
```

### 4.2 部分参数应用

可以使用`partial`方法创建部分应用的任务签名，类似于Python的`functools.partial`：

```python
# 创建部分应用的签名，预设第一个参数为10
add_ten = add.s(10)

# 调用时只需要提供剩余参数
result1 = add_ten.delay(20)  # 执行 add(10, 20)
result2 = add_ten.delay(30)  # 执行 add(10, 30)
```

### 4.3 任务签名的高级用法

任务签名可以与其他任务组合，创建复杂的工作流：

```python
# 创建多个签名
add_task = add.s(10, 20)
mul_task = multiply.s(5)

# 链式调用：先执行add，再用结果乘以5
chain_task = add_task | mul_task
result = chain_task.delay()  # 执行 multiply(add(10, 20), 5)
```

## 5. 任务配置

### 5.1 全局配置

可以在Celery应用实例上设置全局任务配置：

```python
app.conf.update(
    # 任务序列化方式
    task_serializer='json',
    # 结果序列化方式
    result_serializer='json',
    # 接受的内容类型
    accept_content=['json'],
    # 时区设置
    timezone='Asia/Shanghai',
    # 启用UTC
    enable_utc=True,
    # 任务过期时间
    task_expires=3600,
    # 任务结果过期时间
    result_expires=3600,
    # 任务执行超时时间
    task_time_limit=30,
    # 任务软超时时间
    task_soft_time_limit=20,
    # 任务重试延迟时间
    task_retry_delay=10,
)
```

### 5.2 配置文件

对于大型项目，最好使用单独的配置文件：

```python
# celeryconfig.py
from celery.schedules import crontab

# 消息代理设置
broker_url = 'redis://localhost:6379/0'

# 结果后端设置
result_backend = 'redis://localhost:6379/0'

# 任务序列化设置
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# 时区设置
timezone = 'Asia/Shanghai'
enable_utc = True

# 任务超时设置
task_time_limit = 30
task_soft_time_limit = 20

# 任务路由设置
task_routes = {
    'myapp.tasks.email.*': {'queue': 'email'},
    'myapp.tasks.image.*': {'queue': 'image'},
}

# 任务调度设置
beat_schedule = {
    'cleanup-task': {
        'task': 'myapp.tasks.cleanup',
        'schedule': crontab(hour=0, minute=0),  # 每天午夜执行
    },
}
```

然后在应用中加载配置：

```python
# app.py
from celery import Celery

app = Celery('myapp')
app.config_from_object('celeryconfig')
```

### 5.3 环境变量配置

Celery支持从环境变量读取配置：

```python
# 从环境变量CELERY_BROKER_URL读取代理URL
app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# 从环境变量CELERY_RESULT_BACKEND读取结果后端URL
app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
```

## 6. 不同类型的任务

### 6.1 普通任务

最基本的任务类型，适合大多数场景：

```python
@app.task
def simple_task(arg1, arg2):
    return arg1 + arg2
```

### 6.2 绑定任务

绑定到任务实例，可以访问任务上下文：

```python
@app.task(bind=True)
def bound_task(self, arg):
    print(f'Task ID: {self.request.id}')
    return f'Processed {arg}'
```

### 6.3 基类任务

通过继承`Task`类创建自定义任务类：

```python
from celery import Task

class CustomTask(Task):
    