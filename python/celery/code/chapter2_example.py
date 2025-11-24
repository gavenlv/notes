# chapter2_example.py - Celery核心组件与架构示例代码

# 注意：运行此示例前，请确保已安装必要依赖并启动Redis服务
# 安装命令: pip install celery[redis] kombu

from celery import Celery
from kombu import Exchange, Queue
import time
import random

# 创建Celery应用实例
app = Celery('celery_architecture_example',
             broker='redis://localhost:6379/0',  # 使用Redis作为消息代理
             backend='redis://localhost:6379/0',  # 使用Redis作为结果后端
             include=['chapter2_example'])  # 包含当前模块中的任务

# 定义不同的交换器
default_exchange = Exchange('default', type='direct')
email_exchange = Exchange('email', type='direct')
image_exchange = Exchange('image', type='direct')

# 配置任务队列
app.conf.task_queues = [
    # 默认队列
    Queue('default', default_exchange, routing_key='default'),
    # 邮件处理队列
    Queue('email', email_exchange, routing_key='email'),
    # 图像处理队列
    Queue('image', image_exchange, routing_key='image'),
    # 关键任务队列，设置优先级
    Queue('critical', default_exchange, routing_key='critical', 
          queue_arguments={'x-max-priority': 10} if app.conf.broker_url.startswith('amqp') else {})
]

# 配置任务路由规则
app.conf.task_routes = {
    # 所有以email.开头的任务发送到email队列
    'chapter2_example.email.*': {
        'queue': 'email',
        'routing_key': 'email'
    },
    # 所有以image.开头的任务发送到image队列
    'chapter2_example.image.*': {
        'queue': 'image',
        'routing_key': 'image'
    },
    # 关键任务发送到critical队列
    'chapter2_example.critical_task': {
        'queue': 'critical',
        'routing_key': 'critical'
    }
}

# 其他Celery配置
app.conf.update(
    # 结果过期时间为1小时
    result_expires=3600,
    # 任务序列化格式
    task_serializer='json',
    # 接受的内容类型
    accept_content=['json'],
    # 结果序列化格式
    result_serializer='json',
    # 时区设置
    timezone='Asia/Shanghai',
    # 启用UTC
    enable_utc=True,
    # 任务超时设置（秒）
    task_time_limit=300,
    # 任务软超时设置（秒）
    task_soft_time_limit=180,
)


# 定义默认队列任务
@app.task
def add(x, y):
    """简单的加法任务，发送到默认队列"""
    print(f'Processing add({x}, {y}) in default queue')
    time.sleep(1)  # 模拟处理时间
    return x + y


@app.task
def multiply(x, y):
    """乘法任务，发送到默认队列"""
    print(f'Processing multiply({x}, {y}) in default queue')
    time.sleep(1.5)  # 模拟处理时间
    return x * y


# 定义邮件相关任务
@app.task
def email.send_welcome_email(recipient, username):
    """发送欢迎邮件的任务，将被路由到email队列"""
    print(f'Sending welcome email to {recipient} for user {username}')
    # 模拟发送邮件的耗时操作
    time.sleep(2)  
    return {
        'status': 'sent',
        'recipient': recipient,
        'username': username,
        'timestamp': time.time()
    }


@app.task
def email.send_notification(recipient, message):
    """发送通知邮件的任务，将被路由到email队列"""
    print(f'Sending notification to {recipient}: {message}')
    # 模拟发送邮件的耗时操作
    time.sleep(1.5)
    return {
        'status': 'sent',
        'recipient': recipient,
        'message_length': len(message),
        'timestamp': time.time()
    }


# 定义图像处理相关任务
@app.task
def image.resize_image(image_path, width, height):
    """调整图像大小的任务，将被路由到image队列"""
    print(f'Resizing image {image_path} to {width}x{height}')
    # 模拟图像处理的耗时操作
    time.sleep(3)
    return {
        'status': 'processed',
        'image_path': image_path,
        'new_dimensions': f'{width}x{height}',
        'timestamp': time.time()
    }


@app.task
def image.convert_image(image_path, format):
    """转换图像格式的任务，将被路由到image队列"""
    print(f'Converting image {image_path} to {format} format')
    # 模拟图像处理的耗时操作
    time.sleep(2.5)
    return {
        'status': 'converted',
        'image_path': image_path,
        'format': format,
        'timestamp': time.time()
    }


# 定义关键任务
@app.task
def critical_task():
    """关键任务，将被路由到critical队列"""
    print(f'Executing critical task at {time.time()}')
    # 模拟关键任务的执行
    time.sleep(0.5)
    return {
        'status': 'completed',
        'priority': 'critical',
        'timestamp': time.time()
    }


# 自定义路由函数示例（未使用，但展示了高级路由功能）
def custom_router(name, args, kwargs, options, task=None, **kw):
    """自定义任务路由器，根据任务名称和参数决定路由"""
    # 检查是否是图像处理任务且文件大小大于阈值
    if name.startswith('chapter2_example.image.') and kwargs.get('size', 0) > 1024*1024:
        return {'queue': 'large_image'}
    # 其他任务按照默认规则路由
    return None


# 演示代码：展示如何启动不同队列的工作进程和调用任务
if __name__ == '__main__':
    print("Celery核心组件与架构示例")
    print("========================")
    print("\n本示例展示了如何配置多队列、任务路由以及组件间的交互。")
    print("\n要运行完整示例，请按以下步骤操作：")
    print("\n1. 确保Redis服务已启动")
    print("\n2. 启动多个工作进程，分别处理不同的队列：")
    print("   - 处理默认队列和关键队列:")
    print("     celery -A chapter2_example worker --loglevel=info -Q default,critical --concurrency=4")
    print("   - 处理邮件队列:")
    print("     celery -A chapter2_example worker --loglevel=info -Q email --concurrency=2")
    print("   - 处理图像队列:")
    print("     celery -A chapter2_example worker --loglevel=info -Q image --concurrency=2")
    print("\n3. 在Python解释器中运行以下代码调用任务：")
    print("\n   from chapter2_example import *")
    print("   from chapter2_example.email import *")
    print("   from chapter2_example.image import *")
    print("\n   # 发送到默认队列")
    print("   result1 = add.delay(4, 6)")
    print("   result2 = multiply.delay(3, 7)")
    print("\n   # 发送到邮件队列（通过路由规则）")
    print("   result3 = send_welcome_email.delay('user@example.com', 'john_doe')")
    print("   result4 = send_notification.delay('admin@example.com', 'System alert!')")
    print("\n   # 发送到图像队列（通过路由规则）")
    print("   result5 = resize_image.delay('/path/to/image.jpg', 800, 600)")
    print("   result6 = convert_image.delay('/path/to/image.jpg', 'png')")
    print("\n   # 发送到关键队列（通过路由规则）")
    print("   result7 = critical_task.delay()")
    print("\n   # 手动指定队列")
    print("   result8 = add.apply_async((10, 20), queue='critical')")
    print("   result9 = multiply.apply_async((5, 6), queue='email')")
    print("\n4. 观察不同工作进程的日志，确认任务被正确路由")
    print("\n5. 获取任务结果：")
    print("   print(result1.get())")
    print("   print(result3.get())")
    print("   print(result5.get())")
