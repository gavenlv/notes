# chapter1_example.py - Celery入门示例代码

# 注意：在实际运行前，请确保已安装必要的依赖并启动Redis服务
# 安装命令: pip install celery[redis]

# 导入必要的模块
from celery import Celery
import time

# 创建Celery实例
# 配置Redis作为消息代理和结果后端
app = Celery('celery_example',
             broker='redis://localhost:6379/0',  # 消息代理
             backend='redis://localhost:6379/0',  # 结果后端
             include=['chapter1_example'])

# 配置Celery实例
app.conf.update(
    result_expires=3600,  # 结果过期时间为1小时
    task_serializer='json',  # 任务序列化格式
    accept_content=['json'],  # 接受的内容类型
    result_serializer='json',  # 结果序列化格式
    timezone='Asia/Shanghai',  # 设置时区
    enable_utc=True,  # 启用UTC
)


# 定义一个简单的加法任务
@app.task
def add(x, y):
    """
    一个简单的加法任务
    
    Args:
        x: 第一个数字
        y: 第二个数字
    
    Returns:
        两个数字的和
    """
    print(f'Executing add({x}, {y})')
    time.sleep(1)  # 模拟耗时操作
    return x + y


# 定义一个乘法任务
@app.task
def multiply(x, y):
    """
    一个简单的乘法任务
    
    Args:
        x: 第一个数字
        y: 第二个数字
    
    Returns:
        两个数字的乘积
    """
    print(f'Executing multiply({x}, {y})')
    time.sleep(2)  # 模拟耗时操作
    return x * y


# 定义一个字符串处理任务
@app.task
def process_string(text):
    """
    处理字符串的任务
    
    Args:
        text: 要处理的字符串
    
    Returns:
        处理后的字符串（大写并添加后缀）
    """
    print(f'Processing string: {text}')
    time.sleep(1.5)  # 模拟耗时操作
    return f"PROCESSED: {text.upper()}"


# 定义一个可能失败的任务，用于演示错误处理
@app.task(bind=True, autoretry_for=(ZeroDivisionError,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def risky_division(a, b):
    """
    一个可能失败的除法任务
    
    Args:
        a: 被除数
        b: 除数
    
    Returns:
        除法结果
    
    Raises:
        ZeroDivisionError: 当除数为零时
    """
    print(f'Performing risky division: {a} / {b}')
    return a / b


# 如果直接运行此文件（而不是作为模块导入），则启动交互式演示
if __name__ == '__main__':
    print("Celery入门示例")
    print("================")
    print("注意：在运行此演示前，请确保：")
    print("1. Redis服务已启动")
    print("2. Celery Worker已启动：celery -A chapter1_example worker --loglevel=info")
    print("\n要演示任务执行，请在Python解释器中运行以下代码：")
    print("\nfrom chapter1_example import add, multiply, process_string, risky_division")
    print("\n# 异步调用任务")
    print("result1 = add.delay(4, 6)")
    print("result2 = multiply.delay(3, 7)")
    print("result3 = process_string.delay('hello world')")
    print("\n# 检查任务状态")
    print("print(result1.ready())  # 检查任务是否完成")
    print("print(result1.status)  # 查看任务状态")
    print("\n# 获取任务结果")
    print("print(result1.get())  # 获取结果（可能会阻塞）")
    print("print(result2.get())")
    print("print(result3.get())")
    print("\n# 演示错误处理和重试")
    print("result_error = risky_division.delay(10, 0)  # 将触发重试")
    print("try:")
    print("    print(result_error.get(timeout=20))")
    print("except ZeroDivisionError:")
    print("    print('任务在多次重试后仍然失败')")
