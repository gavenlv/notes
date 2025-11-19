#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Celery定时任务与调度示例代码
chapter5_example.py

这个文件演示了Celery中定时任务与调度的各种功能和使用方法，包括：
1. 基本定时任务配置
2. 不同类型的调度表达式（间隔、crontab、日照）
3. 任务参数传递
4. 高级特性（超时、重试、过期等）
5. 自定义调度器
"""

from celery import Celery
from celery.schedules import crontab, interval, solar
from celery.decorators import periodic_task  # 注意：这在Celery 4.0+中已弃用
from datetime import datetime, timedelta
import time
import random
import json

# ========================= 创建Celery应用 ==========================

app = Celery('chapter5_example',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['chapter5_example'])

# 配置
app.conf.update(
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    
    # 定时任务配置
    beat_schedule={
        # 1. 基本间隔调度任务
        'task-basic-interval': {
            'task': 'chapter5_example.basic_task',
            'schedule': 30.0,  # 每30秒执行一次
            'args': ('interval',),
        },
        
        # 2. 更精确的间隔调度
        'task-precise-interval': {
            'task': 'chapter5_example.basic_task',
            'schedule': interval(minutes=1, seconds=30),  # 每1分30秒执行一次
            'args': ('precise_interval',),
        },
        
        # 3. Crontab调度 - 每5分钟执行一次
        'task-crontab-5min': {
            'task': 'chapter5_example.crontab_task',
            'schedule': crontab(minute='*/5'),  # 每5分钟执行一次
            'args': ('every_5_minutes',),
        },
        
        # 4. Crontab调度 - 每天上午9点执行
        'task-daily-morning': {
            'task': 'chapter5_example.crontab_task',
            'schedule': crontab(hour=9, minute=0),  # 每天上午9点
            'args': ('daily_morning',),
        },
        
        # 5. Crontab调度 - 工作日下午5点执行
        'task-weekday-evening': {
            'task': 'chapter5_example.crontab_task',
            'schedule': crontab(hour=17, minute=0, day_of_week='1-5'),  # 周一到周五
            'args': ('weekday_evening',),
        },
        
        # 6. 任务参数传递示例
        'task-with-params': {
            'task': 'chapter5_example.task_with_params',
            'schedule': 60.0,  # 每分钟执行一次
            'args': (10, 20),  # 位置参数
            'kwargs': {'multiplier': 2},  # 关键字参数
        },
        
        # 7. 任务高级选项示例
        'task-with-options': {
            'task': 'chapter5_example.unstable_task',
            'schedule': 120.0,  # 每2分钟执行一次
            'options': {
                'expires': 60,  # 60秒后过期
                'time_limit': 30,  # 30秒超时
                'retry_policy': {
                    'max_retries': 3,
                    'interval_start': 0,
                    'interval_step': 0.2,
                    'interval_max': 0.2,
                },
            },
        },
        
        # 8. 报表生成任务（高优先级）
        'task-report-generation': {
            'task': 'chapter5_example.generate_report',
            'schedule': crontab(minute='*/30'),  # 每30分钟执行一次
            'kwargs': {'report_type': 'status', 'email': 'admin@example.com'},
            'options': {
                'priority': 9,  # 高优先级
                'queue': 'reports',  # 使用专用队列
            },
        },
        
        # 9. 使用日照表达式（仅用于演示，实际使用时需要配置正确的经纬度）
        'task-solar': {
            'task': 'chapter5_example.solar_task',
            'schedule': solar('sunrise', offset=15 * 60),  # 日出后15分钟
            'args': ('morning',),
        },
    }
)

# ========================= 任务定义 ==========================

@app.task(bind=True)
def basic_task(self, source):
    """基础任务示例"""
    print(f"[{datetime.now()}] 执行基础任务 - 来源: {source} - 任务ID: {self.request.id}")
    return {
        'time': datetime.now().isoformat(),
        'source': source,
        'task_id': self.request.id
    }


@app.task(bind=True)
def crontab_task(self, schedule_type):
    """Crontab调度任务示例"""
    print(f"[{datetime.now()}] 执行Crontab任务 - 类型: {schedule_type}")
    
    # 获取当前时间信息用于日志
    now = datetime.now()
    time_info = {
        'year': now.year,
        'month': now.month,
        'day': now.day,
        'hour': now.hour,
        'minute': now.minute,
        'weekday': now.weekday(),  # 0=Monday, 6=Sunday
        'schedule_type': schedule_type
    }
    
    print(f"[{datetime.now()}] 时间信息: {time_info}")
    return time_info


@app.task(bind=True)
def task_with_params(self, a, b, multiplier=1):
    """带参数的任务示例"""
    print(f"[{datetime.now()}] 执行带参数任务 - a={a}, b={b}, multiplier={multiplier}")
    
    # 执行计算
    sum_result = a + b
    product_result = a * b
    scaled_result = (a + b) * multiplier
    
    result = {
        'sum': sum_result,
        'product': product_result,
        'scaled_sum': scaled_result,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"[{datetime.now()}] 计算结果: {result}")
    return result


@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3}, retry_backoff=True)
def unstable_task(self):
    """不稳定任务示例（演示重试机制）"""
    attempt = self.request.retries + 1
    print(f"[{datetime.now()}] 执行不稳定任务 - 尝试 {attempt}/{self.max_retries + 1}")
    
    # 模拟随机失败，随着尝试次数增加，成功率提高
    failure_probability = 0.7 - (attempt * 0.2)  # 第一次70%概率失败，第二次50%，第三次30%
    if random.random() < failure_probability:
        error_msg = f"任务执行失败（尝试 {attempt}/{self.max_retries + 1}）"
        print(f"[{datetime.now()}] {error_msg}")
        raise Exception(error_msg)
    
    # 成功执行
    print(f"[{datetime.now()}] 不稳定任务执行成功！")
    return {
        'success': True,
        'attempts': attempt,
        'timestamp': datetime.now().isoformat()
    }


@app.task(bind=True)
def generate_report(self, report_type, email=None):
    """报表生成任务示例"""
    print(f"[{datetime.now()}] 生成报表 - 类型: {report_type}")
    
    # 模拟报表生成过程
    try:
        # 模拟一些处理时间
        time.sleep(2)
        
        # 生成报表数据
        report_id = f"{report_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        report_data = {
            'id': report_id,
            'type': report_type,
            'generated_at': datetime.now().isoformat(),
            'data_points': random.randint(100, 1000),
            'summary': f"这是一个{report_type}类型的报表"
        }
        
        # 模拟发送邮件（如果提供了邮箱）
        if email:
            print(f"[{datetime.now()}] 报表 {report_id} 已发送至 {email}")
        
        print(f"[{datetime.now()}] 报表生成成功: {report_id}")
        return report_data
    
    except Exception as e:
        print(f"[{datetime.now()}] 报表生成失败: {str(e)}")
        raise


@app.task(bind=True)
def solar_task(self, period):
    """日照相关任务示例"""
    print(f"[{datetime.now()}] 执行日照任务 - 时段: {period}")
    
    # 在实际应用中，这里可以根据日出日落时间执行特定任务
    # 例如日出时开启某些服务，日落时关闭某些服务等
    return {
        'period': period,
        'timestamp': datetime.now().isoformat(),
        'message': f"这是一个{period}时段的日照相关任务"
    }


@app.task(bind=True)
def cleanup_task(self, days=7):
    """数据清理任务示例"""
    print(f"[{datetime.now()}] 执行数据清理任务 - 清理 {days} 天前的数据")
    
    # 模拟清理过程
    try:
        # 计算清理日期
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 模拟清理的数据量
        cleaned_count = random.randint(100, 1000)
        
        result = {
            'cleaned_count': cleaned_count,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"[{datetime.now()}] 数据清理完成: {cleaned_count} 条记录")
        return result
    
    except Exception as e:
        print(f"[{datetime.now()}] 数据清理失败: {str(e)}")
        raise


# ========================= 自定义调度器 ==========================

class WorkdaySchedule:
    """自定义工作日调度器：工作日的上午10点和下午3点执行"""
    
    def __init__(self):
        self.description = "工作日上午10点和下午3点执行"
    
    def is_due(self, last_run_at):
        """检查任务是否应该执行"""
        now = datetime.now()
        
        # 检查是否是工作日（周一到周五）
        if now.weekday() >= 5:  # 5是周六，6是周日
            # 计算到下周一的时间
            days_to_monday = 7 - now.weekday()
            next_run = now + timedelta(days=days_to_monday)
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
                next_run = now + timedelta(days=1)
                if next_run.weekday() >= 5:  # 如果是周末
                    days_to_monday = 7 - next_run.weekday()
                    next_run = next_run + timedelta(days=days_to_monday)
                next_run = next_run.replace(hour=10, minute=0, second=0, microsecond=0)
            
            # 计算距离下次执行的时间
            wait_seconds = (next_run - now).total_seconds()
            return (wait_seconds <= 0, max(0, wait_seconds))
        else:
            # 非工作时间，计算到下一个工作时间的开始
            if now.hour >= 17:  # 下午5点之后
                next_run = now + timedelta(days=1)
            else:  # 上午9点之前
                next_run = now
            
            # 设置为上午10点
            next_run = next_run.replace(hour=10, minute=0, second=0, microsecond=0)
            
            # 检查是否是周末
            if next_run.weekday() >= 5:
                days_to_monday = 7 - next_run.weekday()
                next_run = next_run + timedelta(days=days_to_monday)
            
            # 计算等待时间
            wait_seconds = (next_run - now).total_seconds()
            return (False, wait_seconds)
    
    def __repr__(self):
        return f"<WorkdaySchedule: {self.description}>"

    def __reduce__(self):
        """使调度器可以被序列化"""
        return (WorkdaySchedule, ())


# 使用自定义调度器
app.conf.beat_schedule['task-custom-schedule'] = {
    'task': 'chapter5_example.basic_task',
    'schedule': WorkdaySchedule(),
    'args': ('custom_schedule',),
}


# ========================= 动态任务管理 ==========================

# 这里只是一个演示，实际的动态任务管理通常需要使用数据库或其他持久化存储
# 例如使用Django Celery Beat或自定义调度器

def dynamic_task_manager_demo():
    """动态任务管理演示函数（在实际应用中会集成到Web API或管理接口中）"""
    print("\n动态任务管理演示:")
    print("===================")
    
    # 注意：以下代码在实际使用中需要结合具体的调度器实现
    # 对于数据库调度器（如Django Celery Beat），可以通过ORM操作任务
    # 对于自定义调度器，需要实现相应的添加/删除/修改接口
    
    print("1. 添加新的定时任务")
    print("   在实际应用中，可以通过API或管理界面动态添加任务")
    print("   例如：")
    print("   - 使用Django管理界面添加任务")
    print("   - 通过REST API添加任务")
    
    print("\n2. 修改现有任务")
    print("   可以更改任务的执行频率、参数或其他配置")
    
    print("\n3. 禁用/启用任务")
    print("   可以临时禁用任务而不删除它")
    
    print("\n4. 删除任务")
    print("   永久移除不再需要的任务")


# ========================= 演示代码 ==========================

def demonstrate_periodic_tasks():
    """演示如何手动触发和测试定时任务"""
    print("\n手动测试定时任务:")
    print("===================")
    
    # 手动调用各种任务进行测试
    print("\n1. 执行基础任务:")
    result = basic_task.delay('manual_test')
    print(f"   任务ID: {result.id}")
    print(f"   结果: {result.get()}")
    
    print("\n2. 执行带参数任务:")
    result = task_with_params.delay(5, 10, multiplier=3)
    print(f"   任务ID: {result.id}")
    print(f"   结果: {result.get()}")
    
    print("\n3. 测试报表生成任务:")
    result = generate_report.delay('test', email='test@example.com')
    print(f"   任务ID: {result.id}")
    print(f"   结果: {result.get()}")
    
    print("\n4. 测试数据清理任务:")
    result = cleanup_task.delay(days=1)
    print(f"   任务ID: {result.id}")
    print(f"   结果: {result.get()}")


def show_schedule_info():
    """显示调度信息"""
    print("\n调度配置信息:")
    print("===================")
    print(f"时区: {app.conf.timezone}")
    print(f"启用UTC: {app.conf.enable_utc}")
    
    print("\n定时任务列表:")
    for name, config in app.conf.beat_schedule.items():
        print(f"\n任务名称: {name}")
        print(f"  任务: {config['task']}")
        print(f"  调度器: {config['schedule']}")
        print(f"  参数: {config.get('args', [])}")
        print(f"  关键字参数: {config.get('kwargs', {})}")
        print(f"  选项: {config.get('options', {})}")


def print_usage_instructions():
    """打印使用说明"""
    print("Celery定时任务与调度示例")
    print("=========================")
    print("这个示例演示了Celery中定时任务与调度的各种功能和使用方法")
    print("\n使用前准备:")
    print("1. 确保Redis服务已启动")
    print("2. 安装必要的依赖: pip install celery redis")
    print("\n运行示例:")
    print("1. 启动Celery Worker:")
    print("   celery -A chapter5_example worker --loglevel=info")
    print("\n2. 启动Celery Beat (在另一个终端):")
    print("   celery -A chapter5_example beat --loglevel=info")
    print("\n3. 开发环境可以同时启动Worker和Beat:")
    print("   celery -A chapter5_example worker --beat --loglevel=info")
    print("\n4. 查看任务执行状态 (可选):")
    print("   安装Flower: pip install flower")
    print("   启动Flower: celery -A chapter5_example flower")
    print("   然后访问: http://localhost:5555")
    
    show_schedule_info()
    dynamic_task_manager_demo()


if __name__ == '__main__':
    print_usage_instructions()
    demonstrate_periodic_tasks()