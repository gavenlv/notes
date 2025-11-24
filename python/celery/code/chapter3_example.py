# chapter3_example.py - Celery任务创建与配置示例代码

# 注意：运行此示例前，请确保已安装必要依赖并启动Redis服务
# 安装命令: pip install celery[redis]

from celery import Celery, Task
import time
import random
from datetime import datetime, timedelta

# 创建Celery应用实例
app = Celery('task_creation_example',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['chapter3_example'])

# 全局任务配置
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
    # 任务过期时间（秒）
    task_expires=3600,
    # 任务结果过期时间（秒）
    result_expires=3600,
    # 任务执行超时时间（秒）
    task_time_limit=30,
    # 任务软超时时间（秒）
    task_soft_time_limit=20,
)


# ==================== 基本任务创建 ====================

# 1. 基本任务
@app.task
def add(x, y):
    """一个简单的加法任务"""
    print(f'Executing add({x}, {y})')
    time.sleep(0.5)  # 模拟处理时间
    return x + y


# 2. 自定义任务名称
@app.task(name='custom_multiply')
def multiply(x, y):
    """使用自定义名称的乘法任务"""
    print(f'Executing multiply({x}, {y})')
    time.sleep(0.7)  # 模拟处理时间
    return x * y


# ==================== 任务装饰器参数 ====================

# 3. 配置重试策略的任务
@app.task(
    autoretry_for=(Exception,),  # 对所有异常自动重试
    retry_backoff=2,  # 重试间隔指数退避
    retry_jitter=True,  # 添加随机抖动避免雪崩效应
    max_retries=3  # 最大重试次数
)
def unstable_task():
    """一个可能会失败的任务，演示自动重试功能"""
    print('Executing unstable task...')
    # 模拟50%的失败概率
    if random.random() > 0.5:
        error_msg = 'Task failed randomly'
        print(error_msg)
        raise Exception(error_msg)
    print('Task succeeded!')
    return 'Success'


# 4. 配置超时的任务
@app.task(
    time_limit=10,  # 硬超时：超过10秒会被强制终止
    soft_time_limit=5,  # 软超时：超过5秒会抛出异常但可以清理资源
    acks_late=True  # 任务完成后才确认，确保任务不会丢失
)
def long_running_task(duration):
    """演示超时设置的长时间运行任务"""
    print(f'Running task for {duration} seconds with time limits')
    try:
        for i in range(duration):
            print(f'Progress: {i+1}/{duration}')
            time.sleep(1)
        return f'Completed task after {duration} seconds'
    except Exception as e:
        print(f'Task interrupted: {e}')
        # 这里可以进行资源清理
        raise


# 5. 忽略结果的任务
@app.task(ignore_result=True)
def log_message(message, level='info'):
    """日志记录任务，不需要返回结果"""
    print(f'[{level.upper()}] {message}')
    time.sleep(0.2)
    # 即使有返回值也不会被存储
    return 'This result will be ignored'


# ==================== 任务绑定与上下文访问 ====================

# 6. 绑定任务
@app.task(bind=True)
def bound_task(self, arg):
    """绑定到任务实例的任务，可以访问任务上下文"""
    # 访问任务属性
    print(f'Task ID: {self.request.id}')
    print(f'Task name: {self.name}')
    print(f'Task args: {self.request.args}')
    print(f'Task kwargs: {self.request.kwargs}')
    print(f'Retry count: {self.request.retries}')
    print(f'ETA: {self.request.eta}')
    print(f'Expires: {self.request.expires}')
    
    # 更新任务状态
    self.update_state(state='PROGRESS', meta={'progress': 50})
    time.sleep(1)
    
    return f'Processed argument: {arg}'


# 7. 手动重试的任务
@app.task(bind=True)
def manual_retry_task(self, url):
    """演示手动触发重试的任务"""
    try:
        print(f'Trying to access URL: {url}')
        # 模拟网络请求
        if random.random() > 0.7:
            raise ConnectionError('Network error')
        return f'Successfully accessed {url}'
    except ConnectionError as exc:
        print(f'Failed to access URL, retrying... (Retry count: {self.request.retries})')
        # 手动触发重试，设置10秒后重试
        self.retry(exc=exc, countdown=10, max_retries=3)


# ==================== 自定义任务基类 ====================

# 8. 自定义抽象任务基类
class AbstractBaseTask(Task):
    """自定义抽象任务基类"""
    abstract = True  # 标记为抽象类，不能直接执行
    
    def before_start(self, task_id, args, kwargs):
        """任务开始前的钩子"""
        print(f'[Task {task_id}] About to start')
        self.start_time = time.time()
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功完成时的钩子"""
        execution_time = time.time() - self.start_time
        print(f'[Task {task_id}] Success! Execution time: {execution_time:.2f}s')
        return super().on_success(retval, task_id, args, kwargs)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的钩子"""
        print(f'[Task {task_id}] Failed with error: {exc}')
        return super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """任务返回后的钩子，无论成功失败都会执行"""
        print(f'[Task {task_id}] Returned with status: {status}')


# 使用自定义基类的任务
@app.task(base=AbstractBaseTask)
def task_with_custom_base(data):
    """使用自定义基类的任务"""
    print(f'Processing data: {data}')
    time.sleep(1)
    return f'Processed: {data.upper()}' if isinstance(data, str) else data


# ==================== 任务组合与工作流 ====================

# 用于任务链和组合的辅助任务
@app.task
def subtract(x, y):
    """减法任务"""
    print(f'Executing subtract({x}, {y})')
    time.sleep(0.5)
    return x - y


@app.task
def sum_list(values):
    """求和任务，用于和弦任务的回调"""
    print(f'Summing list: {values}')
    return sum(values)


# ==================== 任务调用演示 ====================

if __name__ == '__main__':
    print("Celery任务创建与配置示例")
    print("========================")
    print("\n本示例展示了各种任务创建和配置方式。")
    print("\n要运行完整示例，请按以下步骤操作：")
    print("\n1. 确保Redis服务已启动")
    print("\n2. 启动Celery Worker：")
    print("   celery -A chapter3_example worker --loglevel=info")
    print("\n3. 在Python解释器中运行以下代码调用各种任务：")
    print("\n   from chapter3_example import *")
    print("   from celery import group, chain, chord")
    print("\n   # 1. 基本任务调用")
    print("   result1 = add.delay(10, 20)")
    print("   print(f'Result: {result1.get()}')")
    print("\n   # 2. 使用自定义名称的任务")
    print("   result2 = multiply.delay(3, 7)")
    print("   print(f'Task name: {result2.task_name}')")
    print("   print(f'Result: {result2.get()}')")
    print("\n   # 3. 带自动重试的不稳定任务")
    print("   result3 = unstable_task.delay()")
    print("   try:")
    print("       print(f'Result: {result3.get()}')")
    print("   except Exception as e:")
    print("       print(f'Task failed after retries: {e}')")
    print("\n   # 4. 超时任务")
    print("   # 正常完成的情况")
    print("   result4 = long_running_task.delay(3)")
    print("   print(f'Result: {result4.get()}')")
    print("   # 超时的情况（会抛出异常）")
    print("   result5 = long_running_task.delay(15)")
    print("   try:")
    print("       print(f'Result: {result5.get(timeout=12)}')")
    print("   except Exception as e:")
    print("       print(f'Task timed out: {e}')")
    print("\n   # 5. 忽略结果的任务")
    print("   log_message.delay('This is a test message')")
    print("   log_message.delay('This is an error message', level='error')")
    print("\n   # 6. 绑定任务")
    print("   result6 = bound_task.delay('test_value')")
    print("   print(f'Result: {result6.get()}')")
    print("\n   # 7. 手动重试任务")
    print("   result7 = manual_retry_task.delay('http://example.com')")
    print("   try:")
    print("       print(f'Result: {result7.get(timeout=35)}')")
    print("   except Exception as e:")
    print("       print(f'Task failed after manual retries: {e}')")
    print("\n   # 8. 使用自定义基类的任务")
    print("   result8 = task_with_custom_base.delay('hello world')")
    print("   print(f'Result: {result8.get()}')")
    print("\n   # 9. 任务组")
    print("   group_result = group(add.s(i, i+1) for i in range(5)).apply_async()")
    print("   group_values = group_result.get()")
    print(f'Group results: {group_values}')")
    print("\n   # 10. 任务链")
    print("   chain_result = chain(add.s(10, 20) | multiply.s(2) | subtract.s(5)).apply_async()")
    print(f'Chain result: {chain_result.get()}')  # 执行: (10+20)*2-5 = 55
    print("\n   # 11. 和弦任务")
    print("   chord_result = chord([add.s(i, i) for i in range(5)], sum_list.s()).apply_async()")
    print(f'Chord result: {chord_result.get()}')  # 对[0+0, 1+1, 2+2, 3+3, 4+4]求和
    print("\n   # 12. 高级任务调用选项")
    print("   # 延迟执行")
    print("   future_result = add.apply_async((100, 200), countdown=5)")
    print("   # 定时执行")
    print("   tomorrow = datetime.now() + timedelta(days=1)")
    print("   scheduled_result = add.apply_async((300, 400), eta=tomorrow)")
    print("   # 设置过期时间")
    print("   expiring_result = add.apply_async((500, 600), expires=30)")
    print("   print(f'Expiring task result: {expiring_result.get()}')")
