# Celery任务执行与结果处理

本章将详细介绍Celery任务执行的各种方式、任务结果的获取与处理机制，以及相关的最佳实践。任务执行和结果处理是Celery使用过程中的核心环节，理解这些概念能够帮助我们更高效地使用Celery进行分布式任务处理。

## 目录
- [任务调用方式](#任务调用方式)
  - [延迟执行](#延迟执行)
  - [异步应用](#异步应用)
  - [任务签名](#任务签名)
- [任务执行选项](#任务执行选项)
  - [执行时间控制](#执行时间控制)
  - [执行优先级](#执行优先级)
  - [结果处理选项](#结果处理选项)
  - [任务路由选项](#任务路由选项)
- [结果后端详解](#结果后端详解)
  - [结果后端类型](#结果后端类型)
  - [结果后端配置](#结果后端配置)
- [结果获取与处理](#结果获取与处理)
  - [获取结果对象](#获取结果对象)
  - [检查任务状态](#检查任务状态)
  - [等待结果](#等待结果)
  - [结果元数据](#结果元数据)
- [结果序列化](#结果序列化)
  - [默认序列化器](#默认序列化器)
  - [自定义序列化器](#自定义序列化器)
- [结果过期与清理](#结果过期与清理)
  - [结果过期配置](#结果过期配置)
  - [手动清理结果](#手动清理结果)
- [批量任务执行](#批量任务执行)
  - [并行执行多个任务](#并行执行多个任务)
  - [工作流执行结果处理](#工作流执行结果处理)
- [实践示例](#实践示例)

## 任务调用方式

Celery提供了多种方式来调用任务，每种方式适用于不同的场景。下面详细介绍这些调用方式。

### 延迟执行

`delay()`方法是最常用的任务调用方式，它会将任务参数序列化后发送到消息代理，然后由Worker执行。这种方式适用于简单的任务调用场景。

**示例代码：**

```python
from myapp.tasks import add

# 延迟执行add任务
result = add.delay(4, 6)
```

`delay()`方法实际上是`apply_async()`的简化版本，它会将所有参数传递给`apply_async()`方法。

### 异步应用

`apply_async()`方法提供了更灵活的任务调用选项，允许我们设置执行时间、优先级等参数。

**基本语法：**

```python
# 基本调用
result = task.apply_async(args=[arg1, arg2], kwargs={'key': 'value'})

# 设置执行选项
result = task.apply_async(
    args=[arg1, arg2],
    countdown=10,      # 10秒后执行
    expires=60,        # 60秒后过期
    queue='important'  # 发送到指定队列
)
```

**示例代码：**

```python
from myapp.tasks import long_running_task
from datetime import datetime, timedelta

# 5秒后执行
result1 = long_running_task.apply_async(args=[10], countdown=5)

# 明天上午10点执行
tomorrow_10am = datetime.now() + timedelta(days=1)
tomorrow_10am = tomorrow_10am.replace(hour=10, minute=0, second=0, microsecond=0)
result2 = long_running_task.apply_async(args=[30], eta=tomorrow_10am)

# 设置任务过期时间和队列
result3 = long_running_task.apply_async(args=[5], expires=120, queue='priority')
```

### 任务签名

任务签名(Signature)是一种预定义的任务调用方式，它将任务函数和参数封装在一起，便于后续执行或组合。

**基本语法：**

```python
# 创建任务签名
sig = task.s(arg1, arg2, key='value')

# 执行签名任务
result = sig.delay()
# 或
result = sig.apply_async()
```

**示例代码：**

```python
from myapp.tasks import add, multiply

# 创建任务签名
add_sig = add.s(4, 6)  # add(4, 6)
multiply_sig = multiply.s(10)  # multiply(10, ...) - 一个参数稍后提供

# 执行签名任务
result1 = add_sig.delay()

# 部分参数应用
# multiply(10, 5) - 提供第二个参数
result2 = multiply_sig.delay(5)

# 使用apply_async执行签名
result3 = add_sig.apply_async(countdown=3)
```

**带部分参数的签名：**

```python
# 创建带部分参数的签名
sig_with_args = add.s(10)

# 后续提供剩余参数
sig_complete = sig_with_args(20)  # 相当于 add(10, 20)

# 执行完整签名
result = sig_complete.delay()
```

## 任务执行选项

Celery提供了丰富的任务执行选项，可以通过`apply_async()`方法设置。

### 执行时间控制

#### Countdown（倒计时）

设置任务在多少秒后执行：

```python
task.apply_async(args=[1, 2], countdown=10)  # 10秒后执行
```

#### ETA（预计执行时间）

设置任务的具体执行时间：

```python
from datetime import datetime, timedelta

future_time = datetime.now() + timedelta(hours=2)
task.apply_async(args=[1, 2], eta=future_time)  # 2小时后执行
```

#### Expires（过期时间）

设置任务的过期时间，可以是秒数或具体时间：

```python
# 秒数形式
task.apply_async(args=[1, 2], expires=300)  # 5分钟后过期

# 具体时间形式
from datetime import datetime, timedelta

expire_time = datetime.now() + timedelta(hours=1)
task.apply_async(args=[1, 2], expires=expire_time)  # 1小时后过期
```

过期的任务将不会被执行，Worker会忽略这些任务。

### 执行优先级

可以为任务设置优先级（0-9，数字越大优先级越高）：

```python
# 高优先级任务
task.apply_async(args=[1, 2], priority=9)

# 低优先级任务
task.apply_async(args=[1, 2], priority=1)
```

**注意：** 优先级功能依赖于消息代理的支持。Redis和RabbitMQ都支持优先级队列，但配置方式可能不同。

### 结果处理选项

#### Track Start Time（跟踪开始时间）

设置是否跟踪任务开始时间：

```python
task.apply_async(args=[1, 2], track_started=True)
```

启用此选项后，可以通过`result.started_at`获取任务开始时间。

### 任务路由选项

#### Queue（队列）

指定任务发送到哪个队列：

```python
task.apply_async(args=[1, 2], queue='image_processing')
```

#### Exchange（交换机）和Routing Key（路由键）

对于使用RabbitMQ作为消息代理的情况，可以更精确地控制消息路由：

```python
task.apply_async(
    args=[1, 2],
    exchange='tasks',
    routing_key='tasks.image'
)
```

## 结果后端详解

结果后端(Result Backend)是Celery用来存储任务执行结果的地方。Celery支持多种结果后端，包括Redis、RabbitMQ、数据库等。

### 结果后端类型

Celery支持以下几种主要的结果后端：

1. **Redis**：最常用的结果后端，性能好，支持多种数据类型
2. **RabbitMQ**：同时作为消息代理和结果后端
3. **数据库**：如PostgreSQL、MySQL、SQLite等
4. **Memcached**：内存中的键值存储
5. **Amazon S3**：云存储服务
6. **文件系统**：本地文件系统存储

### 结果后端配置

可以在Celery应用初始化时配置结果后端：

```python
from celery import Celery

# 使用Redis作为结果后端
app = Celery('myapp',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

# 或使用RabbitMQ
app = Celery('myapp',
             broker='amqp://guest@localhost//',
             backend='rpc://')

# 或使用数据库
app = Celery('myapp',
             broker='redis://localhost:6379/0',
             backend='db+sqlite:///results.sqlite')
```

也可以在配置文件中设置：

```python
app.conf.result_backend = 'redis://localhost:6379/0'
```

## 结果获取与处理

### 获取结果对象

当我们调用任务时，会返回一个`AsyncResult`对象，通过这个对象我们可以获取任务的状态和结果。

```python
from myapp.tasks import add

# 调用任务
result = add.delay(4, 6)

# result是一个AsyncResult对象
print(type(result))  # <class 'celery.result.AsyncResult'>
```

### 检查任务状态

可以通过`AsyncResult`对象的方法检查任务状态：

```python
# 检查任务是否已完成
result.ready()

# 检查任务是否成功
result.successful()

# 检查任务是否失败
result.failed()

# 获取任务状态
result.status  # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
```

### 等待结果

可以使用`get()`方法等待并获取任务结果：

```python
# 基本获取方式
result = add.delay(4, 6)
task_result = result.get()  # 阻塞直到任务完成
print(task_result)  # 10

# 设置超时
result = long_running_task.delay()
try:
    task_result = result.get(timeout=10)  # 10秒后超时
    print(task_result)
except TimeoutError:
    print("Task took too long to complete")
```

### 结果元数据

`AsyncResult`对象提供了一些属性来获取任务的元数据：

```python
# 获取任务ID
result.id  # 或 result.task_id

# 获取任务名称
result.task_name

# 获取任务状态
result.status

# 获取结果（如果任务已完成）
result.result

# 获取错误信息（如果任务失败）
result.traceback

# 获取任务开始时间（需要启用track_started）
result.started_at

# 获取任务完成时间
result.date_done
```

## 结果序列化

结果序列化决定了任务结果如何在Worker和客户端之间传输。

### 默认序列化器

Celery支持多种序列化器：

1. **JSON**：默认序列化器，适用于基本数据类型
2. **Pickle**：Python特有的序列化器，支持更复杂的数据结构，但存在安全风险
3. **YAML**：人类可读的序列化格式
4. **MessagePack**：高效的二进制序列化格式

可以在配置中设置默认序列化器：

```python
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
)
```

### 自定义序列化器

如果需要支持特定的数据类型，可以自定义序列化器：

```python
# 配置自定义序列化器
app.conf.task_serializers = {
    'custom_json': 'myapp.serializers.CustomJSONSerializer'
}
app.conf.result_serializers = {
    'custom_json': 'myapp.serializers.CustomJSONSerializer'
}
app.conf.accept_content = ['json', 'custom_json']

# 在任务中使用自定义序列化器
@app.task(serializer='custom_json')
def process_data(data):
    # 处理数据
    return result
```

## 结果过期与清理

### 结果过期配置

为了避免结果后端中存储过多的数据，可以设置结果的过期时间：

```python
# 全局配置结果过期时间（秒）
app.conf.result_expires = 3600  # 1小时

# 在任务级别设置
@app.task(result_expires=3600)
def my_task():
    return result
```

### 手动清理结果

也可以手动清理特定任务的结果：

```python
from celery.result import AsyncResult

# 获取任务结果对象
result = AsyncResult(task_id)

# 手动清理结果
result.forget()  # 从结果后端删除结果

# 或使用任务方法
task.forget(task_id)
```

## 批量任务执行

### 并行执行多个任务

当需要并行执行多个任务时，可以使用`group`：

```python
from celery import group
from myapp.tasks import add

# 创建任务组
task_group = group(add.s(i, i) for i in range(10))

# 执行任务组
result = task_group.apply_async()

# 获取所有结果
results = result.get()  # 返回一个包含所有任务结果的列表
print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### 工作流执行结果处理

在复杂工作流中，可以组合使用`group`、`chain`和`chord`，并处理它们的执行结果：

```python
from celery import chain, chord, group
from myapp.tasks import add, multiply, sum_list

# 1. 链式任务的结果处理
chain_result = chain(add.s(10, 20) | multiply.s(2) | subtract.s(5)).apply_async()
final_result = chain_result.get()  # 执行: (10+20)*2-5 = 55

# 2. 和弦任务的结果处理
chord_result = chord([add.s(i, i) for i in range(5)], sum_list.s()).apply_async()
total = chord_result.get()  # 对[0+0, 1+1, 2+2, 3+3, 4+4]求和
```

## 实践示例

下面通过一个完整的示例来演示Celery任务执行与结果处理的各种操作。

### 示例代码

```python
# tasks.py - Celery任务执行与结果处理示例

from celery import Celery
import time
import random
from datetime import datetime, timedelta

# 创建Celery应用
app = Celery('task_execution_example',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['tasks'])

# 配置
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,  # 跟踪任务开始时间
)

# 基本任务
@app.task
def add(x, y):
    print(f'Executing add({x}, {y})')
    time.sleep(1)  # 模拟处理时间
    return x + y

# 耗时任务
@app.task
def process_data(data, delay=2):
    print(f'Processing data: {data}')
    time.sleep(delay)  # 模拟处理时间
    return {'processed': data, 'timestamp': datetime.now().isoformat()}

# 可能失败的任务
@app.task(bind=True)
def unstable_task(self, attempt=0):
    print(f'Executing unstable task (attempt {attempt})')
    # 模拟随机失败
    if random.random() > 0.7:
        raise Exception('Task failed randomly')
    return f'Success on attempt {attempt}'

# 带有进度更新的任务
@app.task(bind=True)
def long_running_task(self, iterations):
    print(f'Starting long task with {iterations} iterations')
    total = 0
    for i in range(iterations):
        # 模拟工作
        time.sleep(0.5)
        total += i
        # 更新任务状态和进度
        progress = (i + 1) / iterations * 100
        self.update_state(state='PROGRESS',
                          meta={'iteration': i + 1,
                                'total': iterations,
                                'progress': progress})
    return {'total': total, 'iterations': iterations}

# 执行示例的函数
def run_execution_examples():
    print("=== Celery 任务执行与结果处理示例 ===")
    
    # 1. 基本任务调用
    print("\n1. 基本任务调用:")
    result1 = add.delay(5, 7)
    print(f"   Task ID: {result1.id}")
    print(f"   Task ready: {result1.ready()}")
    print(f"   Task result: {result1.get()}")
    print(f"   Task successful: {result1.successful()}")
    
    # 2. 使用apply_async
    print("\n2. 使用apply_async:")
    result2 = process_data.apply_async(
        args=["test_data"],
        kwargs={"delay": 3},
        countdown=2
    )
    print(f"   Task scheduled for execution in 2 seconds")
    
    # 等待并获取结果
    try:
        print(f"   Waiting for result...")
        result_value = result2.get(timeout=10)
        print(f"   Task result: {result_value}")
        print(f"   Task started at: {result2.started_at}")
        print(f"   Task completed at: {result2.date_done}")
    except TimeoutError:
        print("   Task timed out")
    
    # 3. 结果状态检查
    print("\n3. 结果状态检查:")
    result3 = unstable_task.delay()
    
    # 轮询任务状态
    while not result3.ready():
        print(f"   Current status: {result3.status}")
        time.sleep(1)
    
    # 获取结果，可能会抛出异常
    try:
        value = result3.get()
        print(f"   Task completed successfully: {value}")
    except Exception as e:
        print(f"   Task failed with error: {e}")
        print(f"   Traceback: {result3.traceback}")
    
    # 4. 带有进度更新的任务
    print("\n4. 带有进度更新的任务:")
    result4 = long_running_task.delay(5)
    
    # 轮询任务进度
    while not result4.ready():
        if result4.state == 'PROGRESS':
            meta = result4.result
            print(f"   Progress: {meta['progress']:.1f}% - {meta['iteration']}/{meta['total']}")
        else:
            print(f"   Current status: {result4.state}")
        time.sleep(1)
    
    # 获取最终结果
    final_result = result4.get()
    print(f"   Final result: {final_result}")
    
    # 5. 任务签名
    print("\n5. 任务签名:")
    # 创建签名
    add_sig = add.s(10)
    # 部分应用参数
    add_with_10_and_20 = add_sig(20)  # 相当于 add(10, 20)
    
    # 执行签名
    sig_result = add_with_10_and_20.delay()
    print(f"   Signature result: {sig_result.get()}")
    
    # 6. 任务过期
    print("\n6. 任务过期:")
    # 创建一个会很快过期的任务
    expire_result = add.apply_async(args=[100, 200], expires=1)
    time.sleep(2)  # 等待过期
    
    try:
        value = expire_result.get(timeout=5)
        print(f"   Task executed before expiration: {value}")
    except Exception as e:
        print(f"   Task expired or failed: {e}")

if __name__ == '__main__':
    print("Celery任务执行与结果处理示例")
    print("请先启动Celery Worker:")
    print("  celery -A tasks worker --loglevel=info")
    print("\n然后在另一个终端中导入此模块并运行run_execution_examples()")
```

### 运行示例

1. 确保Redis服务已启动
2. 保存上述代码为`tasks.py`
3. 启动Celery Worker：
   ```
   celery -A tasks worker --loglevel=info
   ```
4. 在Python解释器中运行：
   ```python
   from tasks import run_execution_examples
   run_execution_examples()
   ```

### 最佳实践

1. **设置合理的超时时间**：使用`get(timeout=...)`避免客户端无限等待
2. **处理任务失败**：始终在try/except块中获取结果
3. **配置结果过期**：避免结果后端数据过多导致性能问题
4. **使用适当的序列化器**：根据数据类型选择合适的序列化器
5. **任务状态更新**：对于长时间运行的任务，使用`update_state`提供进度信息

通过本章的学习，您已经掌握了Celery任务执行与结果处理的各种技术和最佳实践。在实际应用中，合理选择任务调用方式、配置结果后端、处理任务结果，可以有效提高系统的可靠性和用户体验。