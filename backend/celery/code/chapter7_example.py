from celery import Celery
from celery.exceptions import Retry
from datetime import datetime
import time
import random
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Celery应用
app = Celery(
    'error_handling_example',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# 全局配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    # 任务结果过期时间
    result_expires=3600,
    # 配置任务队列
    task_queues={
        'default': {
            'exchange': 'default',
            'routing_key': 'default',
        },
        'dead_letter': {
            'exchange': 'dead_letter',
            'routing_key': 'dead_letter',
        }
    }
)

# 自定义错误类型
class TemporaryError(Exception):
    """临时错误，可以重试"""
    pass

class PermanentError(Exception):
    """永久错误，不应该重试"""
    pass

# 自定义任务基类
class BaseTask(app.Task):
    """
    自定义任务基类，提供通用的错误处理功能
    """
    abstract = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        任务失败时的回调
        """
        # 记录失败信息
        logger.error(
            f"任务 {task_id} 失败:\n" 
            f"异常: {str(exc)}\n" 
            f"参数: {args}, {kwargs}\n" 
            f"重试次数: {self.request.retries}"
        )
        
        # 如果已达到最大重试次数，发送到死信队列或进行特殊处理
        if self.max_retries and self.request.retries >= self.max_retries:
            logger.critical(f"任务 {task_id} 已达到最大重试次数")
            # 将任务发送到死信队列
            self.app.send_task(
                'dead_letter_handler',
                args=[task_id, str(exc), args, kwargs],
                queue='dead_letter',
                exchange='dead_letter',
                routing_key='dead_letter'
            )

# 死信队列处理任务
@app.task
def dead_letter_handler(task_id, exception_message, args, kwargs):
    """
    处理死信队列中的任务
    """
    logger.error(f"处理死信任务: {task_id}, 异常: {exception_message}")
    # 这里可以实现死信任务的处理逻辑，如发送通知、保存到数据库等
    return {"task_id": task_id, "status": "handled", "time": datetime.now().isoformat()}

# 自定义退避函数
def custom_backoff(retry_count):
    """
    自定义退避函数，可以根据需求实现更复杂的退避逻辑
    """
    # 基础退避时间 = 2^重试次数
    base_delay = 2 ** retry_count
    # 加上一些随机值避免"雪崩效应"
    jitter = random.uniform(0.8, 1.2)
    # 限制最大延迟
    return min(base_delay * jitter, 300)

# 检测是否为临时错误
def is_temporary_error(exc):
    """
    判断一个错误是否为临时性错误
    """
    # 网络相关的临时错误
    network_errors = (ConnectionError, TimeoutError)
    
    # 数据库连接错误
    if 'database connection' in str(exc).lower() or 'db connection' in str(exc).lower():
        return True
    
    # 服务器错误（如5xx相关错误信息）
    if 'server error' in str(exc).lower() or '500' in str(exc):
        return True
    
    # 超时相关错误
    if 'timeout' in str(exc).lower():
        return True
    
    # 检查是否为临时错误类型
    return isinstance(exc, network_errors)

# 示例1: 自动重试配置
@app.task(bind=True, autoretry_for=(ConnectionError, TimeoutError), 
          retry_kwargs={'max_retries': 3, 'countdown': 5})
def fetch_remote_data(self, url):
    """
    尝试从远程获取数据，如果遇到连接错误或超时会自动重试
    """
    logger.info(f"尝试获取远程数据: {url}, 尝试次数: {self.request.retries + 1}")
    
    # 模拟网络操作
    if random.random() > 0.7:
        error_type = random.choice(['connection', 'timeout', 'other'])
        if error_type == 'connection':
            raise ConnectionError(f"无法连接到 {url}")
        elif error_type == 'timeout':
            raise TimeoutError(f"连接 {url} 超时")
        else:
            raise ValueError(f"无效的URL: {url}")
    
    # 模拟成功响应
    return {"url": url, "data": "sample_data", "timestamp": datetime.now().isoformat()}

# 示例2: 手动触发重试
@app.task(bind=True, max_retries=5)
def process_with_manual_retry(self, data, retry_delay=10):
    """
    演示如何手动触发任务重试
    """
    try:
        logger.info(f"处理数据: {data}, 尝试次数: {self.request.retries + 1}")
        
        # 模拟处理逻辑
        if data.get('should_fail', False):
            # 手动触发重试
            logger.warning(f"手动触发重试，延迟 {retry_delay} 秒")
            raise self.retry(countdown=retry_delay, exc=ValueError("需要重试"))
        
        return f"成功处理: {data}"
    except Retry:
        # 重新抛出Retry异常，让Celery处理
        raise
    except Exception as exc:
        # 其他异常也可以选择性地触发重试
        logger.error(f"处理错误: {str(exc)}")
        self.retry(exc=exc, countdown=retry_delay)

# 示例3: 指数退避策略
@app.task(bind=True, autoretry_for=(Exception,), 
          retry_backoff=True, retry_backoff_max=300, retry_jitter=True, 
          max_retries=5)
def process_with_exponential_backoff(self, data):
    """
    使用指数退避策略进行重试
    - 第1次重试: 约1秒后
    - 第2次重试: 约2秒后
    - 第3次重试: 约4秒后
    - 第4次重试: 约8秒后
    - 以此类推，直到达到最大退避时间300秒
    """
    logger.info(f"处理带指数退避的数据: {data}, 尝试次数: {self.request.retries + 1}")
    
    # 模拟不稳定的操作
    if random.random() > 0.7:
        raise Exception("模拟随机失败")
    
    return f"处理成功: {data}"

# 示例4: 使用自定义退避函数
@app.task(bind=True, max_retries=5)
def process_with_custom_backoff(self, data):
    """
    使用自定义退避函数进行重试
    """
    try:
        logger.info(f"使用自定义退避处理数据: {data}, 尝试次数: {self.request.retries + 1}")
        
        if random.random() > 0.7:
            raise Exception("模拟随机失败")
            
        return f"处理成功: {data}"
    except Exception as exc:
        # 使用自定义退避函数计算等待时间
        countdown = custom_backoff(self.request.retries)
        logger.info(f"自定义退避: {countdown:.2f}秒后重试")
        raise self.retry(exc=exc, countdown=countdown)

# 示例5: 自定义任务状态
@app.task(bind=True)
def long_running_task(self, items):
    """
    长时间运行的任务，使用自定义状态跟踪进度
    """
    logger.info(f"开始长时间运行任务，共 {len(items)} 个项目")
    
    total = len(items)
    results = []
    
    for i, item in enumerate(items):
        # 更新自定义状态
        progress = (i + 1) / total * 100
        self.update_state(
            state='PROCESSING',
            meta={
                'current': i + 1,
                'total': total,
                'status': f'处理项目 {item}',
                'percent_complete': progress
            }
        )
        
        # 模拟处理
        time.sleep(0.2)
        
        # 模拟随机错误
        if random.random() < 0.1:
            error_msg = f"处理项目 {item} 时出错"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        results.append(f"处理结果: {item}")
    
    logger.info("长时间运行任务完成")
    return {'processed': total, 'results': results, 'status': '完成'}

# 示例6: 错误分类与处理
@app.task(bind=True, autoretry_for=(TemporaryError,), max_retries=3, base=BaseTask)
def process_with_error_classification(self, data):
    """
    根据错误类型采取不同的处理策略
    """
    logger.info(f"使用错误分类处理数据: {data}")
    
    try:
        # 模拟业务逻辑
        if data.get('type') == 'temporary':
            logger.warning("遇到临时错误，将重试")
            raise TemporaryError("这是一个临时错误")
        elif data.get('type') == 'permanent':
            logger.error("遇到永久错误，不重试")
            raise PermanentError("这是一个永久错误")
        
        return f"成功处理: {data}"
    except PermanentError as exc:
        # 记录错误并放弃，不再重试
        logger.error(f"遇到永久性错误，放弃处理: {str(exc)}")
        raise
    except Exception as exc:
        # 其他错误会根据配置决定是否重试
        logger.warning(f"处理出错，可能会重试: {str(exc)}")
        raise

# 示例7: 智能错误处理
@app.task(bind=True, max_retries=5, base=BaseTask)
def robust_task(self, data):
    """
    健壮的任务处理函数，能够智能地决定是否重试
    """
    logger.info(f"健壮处理数据: {data}, 尝试次数: {self.request.retries + 1}")
    
    try:
        # 模拟业务逻辑
        if random.random() > 0.7:
            error_type = random.choice(['network', 'server', 'client', 'other'])
            if error_type == 'network':
                raise ConnectionError("模拟网络错误")
            elif error_type == 'server':
                raise Exception("服务器错误 503 Service Unavailable")
            elif error_type == 'client':
                raise ValueError("无效的参数")
            else:
                raise Exception("未知错误")
        
        return f"健壮处理成功: {data}"
    except Exception as exc:
        if is_temporary_error(exc):
            # 临时错误，使用指数退避策略重试
            countdown = min(2 ** self.request.retries, 60)
            logger.info(f"检测到临时错误，{countdown}秒后重试: {str(exc)}")
            raise self.retry(exc=exc, countdown=countdown)
        else:
            # 永久错误，记录并放弃
            logger.error(f"检测到永久错误，不重试: {str(exc)}")
            raise

# 示例8: 不重试的关键任务
@app.task(bind=True, max_retries=0, base=BaseTask)
def critical_no_retry_task(self, data):
    """
    演示不重试的任务，适用于对时效性要求高或失败后无法恢复的操作
    """
    logger.info(f"执行不重试的关键任务: {data}")
    
    try:
        # 模拟处理逻辑
        if random.random() > 0.8:
            raise Exception("模拟关键任务失败")
            
        return f"关键任务成功: {data}"
        
    except Exception as exc:
        # 记录错误但不重试
        logger.error(f"关键任务失败，不重试: {str(exc)}")
        # 可以发送通知或执行其他清理操作
        # send_alert(f"关键任务失败: {self.request.id}")
        raise

# 演示函数
def run_demo():
    """
    运行演示，展示不同的错误处理场景
    """
    print("=== Celery错误处理与重试机制演示 ===")
    
    # 1. 自动重试示例
    task1 = fetch_remote_data.delay("https://api.example.com/data")
    print(f"1. 启动带自动重试的任务，ID: {task1.id}")
    
    # 2. 手动重试示例
    task2 = process_with_manual_retry.delay({"should_fail": True}, retry_delay=5)
    print(f"2. 启动带手动重试的任务，ID: {task2.id}")
    
    # 3. 指数退避示例
    task3 = process_with_exponential_backoff.delay({"key": "value3"})
    print(f"3. 启动带指数退避的任务，ID: {task3.id}")
    
    # 4. 自定义退避示例
    task4 = process_with_custom_backoff.delay({"key": "value4"})
    print(f"4. 启动带自定义退避的任务，ID: {task4.id}")
    
    # 5. 长时间运行任务（带进度）
    items = [f"item-{i}" for i in range(10)]
    task5 = long_running_task.delay(items)
    print(f"5. 启动长时间运行任务，ID: {task5.id}")
    
    # 6. 错误分类示例
    task6_temp = process_with_error_classification.delay({"type": "temporary"})
    task6_perm = process_with_error_classification.delay({"type": "permanent"})
    print(f"6. 启动错误分类任务（临时错误），ID: {task6_temp.id}")
    print(f"   启动错误分类任务（永久错误），ID: {task6_perm.id}")
    
    # 7. 智能错误处理示例
    task7 = robust_task.delay({"key": "value7"})
    print(f"7. 启动智能错误处理任务，ID: {task7.id}")
    
    # 8. 不重试的关键任务示例
    task8 = critical_no_retry_task.delay({"important": True})
    print(f"8. 启动不重试的关键任务，ID: {task8.id}")
    
    print("\n请在另一个终端运行工作进程:")
    print("celery -A chapter7_example worker --loglevel=info")
    print("\n然后可以通过任务ID查询状态和结果")

if __name__ == "__main__":
    run_demo()
