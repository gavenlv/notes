# chapter4_example.py - Celery任务执行与结果处理示例代码

# 注意：运行此示例前，请确保已安装必要依赖并启动Redis服务
# 安装命令: pip install celery[redis]

from celery import Celery, group, chain, chord
import time
import random
from datetime import datetime, timedelta
import json

# 创建Celery应用实例
app = Celery('task_execution_example',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['chapter4_example'])

# 配置
app.conf.update(
    # 任务序列化配置
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    # 时区设置
    timezone='Asia/Shanghai',
    enable_utc=True,
    # 结果过期时间（秒）
    result_expires=3600,
    # 启用任务开始时间跟踪
    task_track_started=True,
)


# ==================== 基础任务定义 ====================

@app.task
def add(x, y):
    """简单的加法任务"""
    print(f'Executing add({x}, {y})')
    time.sleep(1)  # 模拟处理时间
    return x + y


@app.task
def multiply(x, y):
    """乘法任务"""
    print(f'Executing multiply({x}, {y})')
    time.sleep(0.8)
    return x * y


@app.task
def subtract(x, y):
    """减法任务"""
    print(f'Executing subtract({x}, {y})')
    time.sleep(0.5)
    return x - y


@app.task
def process_data(data, delay=2):
    """处理数据的任务"""
    print(f'Processing data: {data}')
    time.sleep(delay)
    # 返回包含元数据的结果
    return {
        'processed': data,
        'timestamp': datetime.now().isoformat(),
        'processed_value': data.upper() if isinstance(data, str) else data * 2
    }


# ==================== 结果处理示例任务 ====================

@app.task(bind=True)
def unstable_task(self, attempt_count=0):
    """不稳定任务，模拟随机失败"""
    print(f'Executing unstable task (attempt {attempt_count})')
    # 增加重试次数
    attempt_count += 1
    
    # 70%的概率失败
    if random.random() > 0.3:
        error_msg = f'Task failed randomly on attempt {attempt_count}'
        print(error_msg)
        # 抛出异常以触发错误状态
        raise Exception(error_msg)
    
    result_msg = f'Success on attempt {attempt_count}'
    print(result_msg)
    return result_msg


@app.task(bind=True)
def long_running_task(self, iterations):
    """长时间运行的任务，提供进度更新"""
    print(f'Starting long task with {iterations} iterations')
    total = 0
    
    for i in range(iterations):
        # 模拟工作
        time.sleep(0.5)
        total += i
        
        # 每2次迭代更新一次状态
        if i % 2 == 0 or i == iterations - 1:
            # 计算进度百分比
            progress = (i + 1) / iterations * 100
            # 更新任务状态和进度
            self.update_state(
                state='PROGRESS',
                meta={
                    'iteration': i + 1,
                    'total': iterations,
                    'progress': round(progress, 2),
                    'current_total': total
                }
            )
            print(f'Progress updated: {progress:.2f}%')
    
    # 返回最终结果
    return {
        'total': total,
        'iterations': iterations,
        'average': total / iterations if iterations > 0 else 0
    }


@app.task
def sum_list(values):
    """求和任务，用于和弦任务的回调"""
    print(f'Summing list: {values}')
    return sum(values)


@app.task(ignore_result=True)
def log_result(task_id, result):
    """记录任务结果的任务（不存储自己的结果）"""
    print(f'Logging result for task {task_id}: {result}')
    # 这里可以将结果写入日志文件、数据库等
    return None


# ==================== 自定义JSON编码器 ====================

class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，支持datetime对象"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# ==================== 结果处理演示函数 ====================

if __name__ == '__main__':
    print("=== Celery 任务执行与结果处理示例 ===")
    print("\n使用说明：")
    print("1. 确保Redis服务已启动")
    print("2. 启动Celery Worker：")
    print("   celery -A chapter4_example worker --loglevel=info")
    print("3. 在Python解释器中导入此模块并运行相应函数")
    print("\n示例函数：")
    print("   - run_basic_execution() - 基本任务执行与结果获取")
    print("   - run_async_execution() - 使用apply_async的高级执行选项")
    print("   - run_result_monitoring() - 任务结果监控")
    print("   - run_progress_tracking() - 任务进度跟踪")
    print("   - run_signature_demo() - 任务签名演示")
    print("   - run_batch_execution() - 批量任务执行")
    print("   - run_error_handling() - 错误处理演示")
    print("\n请根据需要选择相应的函数运行")

def run_basic_execution():
    """基本任务执行与结果获取演示"""
    print("\n=== 基本任务执行与结果获取 ===")
    
    # 使用delay()方法执行任务
    print("\n1. 使用delay()执行任务:")
    result = add.delay(5, 7)
    
    # 任务ID和状态
    print(f"   任务ID: {result.id}")
    print(f"   任务名称: {result.task_name}")
    print(f"   任务就绪: {result.ready()}")
    print(f"   任务状态: {result.status}")
    
    # 阻塞等待并获取结果
    print("   等待结果...")
    task_result = result.get()
    
    print(f"   任务结果: {task_result}")
    print(f"   任务就绪: {result.ready()}")
    print(f"   任务成功: {result.successful()}")
    print(f"   任务状态: {result.status}")
    
    # 使用get()的返回值
    print(f"   直接从get()获取结果: {result.get()}")

def run_async_execution():
    """使用apply_async的高级执行选项演示"""
    print("\n=== 使用apply_async的高级执行选项 ===")
    
    # 基本apply_async调用
    print("\n1. 基本apply_async调用:")
    result1 = add.apply_async(args=[10, 20])
    print(f"   基本结果: {result1.get()}")
    
    # 使用countdown参数（延迟执行）
    print("\n2. 使用countdown参数（延迟3秒执行）:")
    result2 = multiply.apply_async(args=[5, 6], countdown=3)
    print(f"   任务调度在3秒后执行，任务ID: {result2.id}")
    print(f"   当前状态: {result2.status}")
    print("   等待结果...")
    print(f"   结果: {result2.get()}")
    
    # 使用eta参数（定时执行）
    print("\n3. 使用eta参数（定时执行，5秒后）:")
    future_time = datetime.now() + timedelta(seconds=5)
    result3 = process_data.apply_async(args=["test_data"], eta=future_time)
    print(f"   任务调度在: {future_time}")
    print(f"   等待结果...")
    print(f"   结果: {result3.get()}")
    
    # 使用expires参数（设置过期时间）
    print("\n4. 使用expires参数（设置过期时间为2秒）:")
    result4 = add.apply_async(args=[100, 200], expires=2)
    print(f"   任务设置为2秒后过期，立即尝试获取结果:")
    try:
        print(f"   结果: {result4.get(timeout=3)}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 设置超时的长时间任务
    print("\n5. 设置客户端超时:")
    result5 = process_data.apply_async(args=["timeout_test"], kwargs={"delay": 5})
    try:
        print("   尝试在3秒内获取结果...")
        result5.get(timeout=3)
    except Exception as e:
        print(f"   预期的超时错误: {e}")

def run_result_monitoring():
    """任务结果监控演示"""
    print("\n=== 任务结果监控 ===")
    
    # 提交任务
    print("\n1. 提交处理任务:")
    result = process_data.delay("monitoring_test", delay=4)
    
    # 轮询任务状态
    print("   轮询任务状态...")
    while not result.ready():
        # 获取当前状态
        status = result.status
        print(f"   当前状态: {status}")
        
        # 如果任务已开始，可以获取开始时间
        if status in ('STARTED', 'PROGRESS'):
            try:
                print(f"   开始时间: {result.started_at}")
            except (AttributeError, NotImplementedError):
                print("   开始时间: 不可用")
        
        time.sleep(1)
    
    # 任务完成后获取详细信息
    print(f"\n2. 任务完成信息:")
    print(f"   状态: {result.status}")
    print(f"   是否成功: {result.successful()}")
    print(f"   结果: {result.result}")
    
    # 尝试获取完成时间
    try:
        print(f"   完成时间: {result.date_done}")
    except (AttributeError, NotImplementedError):
        print("   完成时间: 不可用")

def run_progress_tracking():
    """任务进度跟踪演示"""
    print("\n=== 任务进度跟踪 ===")
    
    # 启动长时间运行的任务
    iterations = 10  # 10次迭代，每次0.5秒，总共约5秒
    print(f"\n1. 启动长时间运行的任务 ({iterations}次迭代):")
    result = long_running_task.delay(iterations)
    
    # 轮询任务状态和进度
    print("   跟踪任务进度...")
    while not result.ready():
        # 获取当前状态
        status = result.status
        print(f"   状态: {status}")
        
        # 如果任务正在进行中，获取进度信息
        if status == 'PROGRESS':
            try:
                # 获取进度元数据
                progress_info = result.result
                print(f"   进度: {progress_info['progress']}% - "
                      f"第 {progress_info['iteration']}/{progress_info['total']} 次迭代")
                print(f"   当前累计: {progress_info['current_total']}")
            except (AttributeError, KeyError):
                print("   无法获取进度信息")
        
        time.sleep(1)
    
    # 获取最终结果
    print(f"\n2. 任务完成:")
    final_result = result.get()
    print(f"   最终结果: {final_result}")

def run_signature_demo():
    """任务签名演示"""
    print("\n=== 任务签名演示 ===")
    
    # 1. 创建基本任务签名
    print("\n1. 创建基本任务签名:")
    add_sig = add.s(10, 20)  # add(10, 20)
    print(f"   签名: {add_sig}")
    print(f"   任务: {add_sig.task}")
    print(f"   参数: {add_sig.args}, {add_sig.kwargs}")
    
    # 执行签名
    result1 = add_sig.delay()
    print(f"   执行结果: {result1.get()}")
    
    # 2. 部分参数应用
    print("\n2. 部分参数应用:")
    # 创建一个只提供一个参数的签名
    multiply_by_10 = multiply.s(10)  # multiply(10, ?)
    
    # 稍后提供第二个参数
    result2 = multiply_by_10.delay(5)  # 执行 multiply(10, 5)
    print(f"   multiply(10, 5) = {result2.get()}")
    
    # 或使用更明确的方式
    multiply_10_6 = multiply_by_10(6)  # multiply(10, 6)
    result3 = multiply_10_6.delay()
    print(f"   multiply(10, 6) = {result3.get()}")
    
    # 3. 结合apply_async使用签名
    print("\n3. 结合apply_async使用签名:")
    sig = add.s(50, 50)
    result4 = sig.apply_async(countdown=2)
    print("   2秒后执行 add(50, 50)")
    print(f"   结果: {result4.get()}")

def run_batch_execution():
    """批量任务执行演示"""
    print("\n=== 批量任务执行 ===")
    
    # 1. 任务组 - 并行执行多个任务
    print("\n1. 任务组 (Group):")
    print("   并行执行多个加法任务")
    
    # 创建任务组
    task_group = group(add.s(i, i+1) for i in range(5))  # [add(0,1), add(1,2), ..., add(4,5)]
    
    # 执行任务组
    group_result = task_group.apply_async()
    
    # 获取所有结果
    print("   等待所有任务完成...")
    results = group_result.get()
    print(f"   所有任务结果: {results}")
    print(f"   任务组成功: {group_result.successful()}")
    
    # 2. 任务链 - 顺序执行任务
    print("\n2. 任务链 (Chain):")
    print("   执行链式任务: add(10, 20) | multiply(2) | subtract(5)")
    
    # 创建任务链
    task_chain = chain(add.s(10, 20) | multiply.s(2) | subtract.s(5))
    
    # 执行任务链
    chain_result = task_chain.apply_async()
    
    # 获取最终结果
    final_result = chain_result.get()
    print(f"   最终结果: {final_result}  (计算: ((10+20)*2)-5 = 55)")
    
    # 3. 和弦任务 - 并行任务完成后执行回调
    print("\n3. 和弦任务 (Chord):")
    print("   执行并行任务后，对结果求和")
    
    # 创建和弦任务
    # 先并行执行多个add任务，然后对结果调用sum_list
    chord_task = chord([add.s(i, i) for i in range(5)], sum_list.s())
    
    # 执行和弦任务
    chord_result = chord_task.apply_async()
    
    # 获取结果
    total_sum = chord_result.get()
    print(f"   计算 [0+0, 1+1, 2+2, 3+3, 4+4] 的和 = {total_sum}")

def run_error_handling():
    """错误处理演示"""
    print("\n=== 错误处理 ===")
    
    # 1. 处理任务失败
    print("\n1. 处理任务失败:")
    print("   执行不稳定任务，可能会失败")
    
    result = unstable_task.delay()
    
    # 使用try/except获取结果
    try:
        task_result = result.get()
        print(f"   任务成功完成: {task_result}")
    except Exception as e:
        print(f"   任务失败: {e}")
        
        # 获取失败信息
        if hasattr(result, 'traceback'):
            print("   错误堆栈:")
            # 为了简洁，只打印一部分堆栈信息
            traceback_lines = result.traceback.split('\n')
            for line in traceback_lines[-5:]:  # 只打印最后5行
                print(f"     {line}")
    
    # 2. 检查任务状态
    print(f"\n2. 任务状态:")
    print(f"   是否就绪: {result.ready()}")
    print(f"   是否成功: {result.successful()}")
    print(f"   是否失败: {result.failed()}")
    print(f"   最终状态: {result.status}")
    
    # 3. 重试失败的任务
    print("\n3. 重试失败的任务:")
    # 如果之前的任务失败了，我们可以重试
    if result.failed():
        print("   创建一个新的任务实例进行重试")
        retry_result = unstable_task.delay()
        try:
            retry_task_result = retry_result.get(timeout=5)
            print(f"   重试成功: {retry_task_result}")
        except Exception as e:
            print(f"   重试也失败了: {e}")
    
    # 4. 处理超时
    print("\n4. 处理超时:")
    long_result = process_data.apply_async(args=["timeout_test"], kwargs={"delay": 5})
    
    try:
        print("   尝试在3秒内获取需要5秒的任务结果")
        long_result.get(timeout=3)
    except TimeoutError:
        print("   捕获到超时错误")
        # 注意：任务仍在后台执行，只是客户端不再等待
        print(f"   任务仍在后台执行，状态: {long_result.status}")
        
        # 我们可以稍后再尝试获取结果
        print("   等待一会儿后再次尝试...")
        time.sleep(3)
        try:
            final_value = long_result.get(timeout=2)
            print(f"   成功获取到结果: {final_value}")
        except Exception as e:
            print(f"   仍然无法获取结果: {e}")
