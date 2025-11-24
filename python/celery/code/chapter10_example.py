#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Celery实际应用案例与项目实践 - 完整示例代码

本文件包含第10章中介绍的各种实际应用案例的完整实现，包括：
1. 图像处理服务
2. 数据分析与报表生成系统
3. 实时消息推送系统
4. 微服务架构中的任务协调
5. 分布式锁与幂等性保证
6. 批量任务处理

使用方法：
1. 确保已安装所有依赖：pip install celery redis pillow pandas matplotlib
2. 启动Redis服务
3. 启动Celery worker：celery -A chapter10_example worker --loglevel=info
4. 如果需要定时任务，同时启动beat：celery -A chapter10_example beat --loglevel=info
"""

import os
import json
import uuid
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import redis
from PIL import Image, ImageDraw, ImageFont
from celery import Celery, chain, group, chord
from celery.schedules import crontab

# =============================================================================
# Celery应用配置
# =============================================================================

# 初始化Celery应用
app = Celery(
    'practical_examples',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# 应用配置
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=500,
    task_time_limit=300,
    task_soft_time_limit=240,
    task_queues={
        'default': {
            'exchange': 'default',
            'exchange_type': 'direct',
            'routing_key': 'default',
        },
        'image_processing': {
            'exchange': 'image_tasks',
            'exchange_type': 'direct',
            'routing_key': 'image.processing',
        },
        'reports': {
            'exchange': 'report_tasks',
            'exchange_type': 'direct',
            'routing_key': 'reports',
        },
        'notifications': {
            'exchange': 'notification_tasks',
            'exchange_type': 'direct',
            'routing_key': 'notifications',
        },
        'priority': {
            'exchange': 'priority_tasks',
            'exchange_type': 'direct',
            'routing_key': 'priority',
            'queue_arguments': {'x-max-priority': 10},
        },
    },
    task_routes={
        'chapter10_example.process_image': {'queue': 'image_processing'},
        'chapter10_example.batch_process_images': {'queue': 'image_processing'},
        'chapter10_example.generate_sales_report': {'queue': 'reports'},
        'chapter10_example.send_notification': {'queue': 'notifications'},
        'chapter10_example.batch_send_notifications': {'queue': 'notifications'},
    }
)

# 配置定时任务
app.conf.beat_schedule = {
    # 每日销售报表
    'daily-sales-report': {
        'task': 'chapter10_example.generate_sales_report',
        'schedule': crontab(hour=1, minute=0),  # 每天凌晨1点执行
        'args': (lambda: (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                 lambda: datetime.datetime.now().strftime('%Y-%m-%d'),
                 'daily')
    },
    # 每周销售报表
    'weekly-sales-report': {
        'task': 'chapter10_example.generate_sales_report',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # 每周日凌晨2点执行
        'args': (lambda: (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                 lambda: datetime.datetime.now().strftime('%Y-%m-%d'),
                 'weekly')
    },
}

# 任务基类
class BaseTask(app.Task):
    """所有任务的基类，提供通用功能"""
    abstract = True
    autoretry_for = (Exception,)
    retry_backoff = 2
    retry_kwargs = {'max_retries': 3}
    
    def __call__(self, *args, **kwargs):
        """任务执行前的钩子"""
        print(f"[{self.name}] 开始执行，参数: {args}, {kwargs}")
        return super().__call__(*args, **kwargs)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败的钩子"""
        print(f"[{self.name}] 执行失败: {exc}")
        # 这里可以添加错误报告、告警等逻辑

# 设置默认任务基类
app.Task = BaseTask

# Redis客户端用于分布式锁等功能
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# =============================================================================
# 1. 图像处理服务
# =============================================================================

@app.task(queue='image_processing')
def process_image(image_path, operations):
    """
    处理图片的任务
    
    参数:
        image_path: 图片路径
        operations: 操作列表，如 [
            {"type": "resize", "width": 800, "height": 600},
            {"type": "thumbnail", "size": (150, 150)},
            {"type": "watermark", "text": "MySite", "position": "bottom-right"}
        ]
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
        # 打开图片
        img = Image.open(image_path)
        
        # 创建处理后的文件路径
        base, ext = os.path.splitext(image_path)
        result_paths = []
        
        # 执行操作
        for i, op in enumerate(operations):
            # 创建副本以避免修改原图
            processed_img = img.copy()
            
            # 根据操作类型进行处理
            if op["type"] == "resize":
                processed_img = processed_img.resize((op["width"], op["height"]))
            elif op["type"] == "thumbnail":
                processed_img.thumbnail(op["size"])
            elif op["type"] == "watermark":
                # 添加水印
                draw = ImageDraw.Draw(processed_img)
                # 尝试加载字体或使用默认字体
                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except IOError:
                    font = ImageFont.load_default()
                    
                text = op["text"]
                # 对于PIL 8.0+，使用textbbox替代textsize
                try:
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                except AttributeError:
                    # 旧版本PIL
                    text_width, text_height = draw.textsize(text, font=font)
                
                # 计算水印位置
                img_width, img_height = processed_img.size
                if op["position"] == "bottom-right":
                    x = img_width - text_width - 10
                    y = img_height - text_height - 10
                else:
                    x, y = 10, 10
                
                # 添加水印文本
                draw.text((x, y), text, font=font, fill=(255, 255, 255, 128))
                
            # 保存处理后的图片
            result_path = f"{base}_processed_{i}{ext}"
            processed_img.save(result_path)
            result_paths.append(result_path)
            
        return {"success": True, "paths": result_paths}
        
    except Exception as e:
        # 记录错误并重试
        print(f"图像处理失败: {str(e)}")
        raise

@app.task(queue='image_processing')
def batch_process_images(image_paths, operations):
    """
    批量处理多个图片
    """
    # 创建任务组
    tasks = [process_image.s(path, operations) for path in image_paths]
    
    # 使用group执行并行任务
    job = group(tasks)
    result = job.apply_async()
    
    # 返回任务组ID，以便客户端可以查询结果
    return {"group_id": result.id, "total_images": len(image_paths)}

# =============================================================================
# 2. 数据分析与报表生成系统
# =============================================================================

@app.task(queue='reports')
def generate_sales_report(start_date, end_date, report_type="daily"):
    """
    生成销售报表
    
    参数:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        report_type: 报表类型 (daily, weekly, monthly)
    """
    try:
        # 确保输出目录存在
        output_dir = f"reports/{report_type}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 记录开始时间
        start_time = datetime.datetime.now()
        
        # 模拟从数据库获取数据
        df = fetch_sales_data(start_date, end_date)
        
        # 生成报表ID
        report_id = f"sales_{report_type}_{start_date}_{end_date}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 生成数据摘要
        summary = {
            'period': f"{start_date} to {end_date}",
            'total_sales': float(df['sales'].sum()),
            'total_orders': int(df['orders'].sum()),
            'avg_order_value': float(df['sales'].sum() / df['orders'].sum()) if df['orders'].sum() > 0 else 0,
            'report_date': datetime.datetime.now().isoformat()
        }
        
        # 保存CSV数据
        csv_path = os.path.join(output_dir, f"{report_id}.csv")
        df.to_csv(csv_path, index=False)
        
        # 生成可视化图表
        plt.figure(figsize=(12, 6))
        
        # 销售额趋势图
        plt.subplot(1, 2, 1)
        plt.plot(df['date'], df['sales'], marker='o')
        plt.title('Sales Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 订单量趋势图
        plt.subplot(1, 2, 2)
        plt.bar(df['date'], df['orders'])
        plt.title('Orders Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(output_dir, f"{report_id}_chart.png")
        plt.savefig(chart_path)
        plt.close()
        
        # 记录完成时间
        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 构建结果
        result = {
            'report_id': report_id,
            'summary': summary,
            'files': {
                'data': csv_path,
                'chart': chart_path
            },
            'execution_time': execution_time,
            'status': 'completed'
        }
        
        # 发送通知
        send_report_notification.delay(result)
        
        return result
        
    except Exception as e:
        # 记录错误
        print(f"生成销售报表错误: {str(e)}")
        raise

def fetch_sales_data(start, end):
    """
    模拟从数据库获取销售数据
    实际应用中，这里应该是SQL查询或API调用
    """
    # 模拟数据获取延迟
    time.sleep(2)  # 模拟数据查询耗时
    
    # 生成示例数据
    date_range = pd.date_range(start=start, end=end)
    data = {
        'date': date_range,
        'sales': [1000 + i*10 for i in range(len(date_range))],
        'orders': [50 + i for i in range(len(date_range))],
        'avg_order_value': [20 + i*0.1 for i in range(len(date_range))]
    }
    return pd.DataFrame(data)

@app.task(queue='notifications')
def send_report_notification(report_data):
    """
    发送报表通知
    """
    # 模拟发送邮件或消息
    print(f"报表 {report_data['report_id']} 已准备就绪。正在发送通知...")
    print(f"摘要: {report_data['summary']}")
    # 实际应用中，这里应该调用邮件服务或消息系统
    return {"status": "notification_sent"}

# =============================================================================
# 3. 实时消息推送系统
# =============================================================================

@app.task(queue='notifications')
def send_notification(user_id, notification_type, content, priority=5):
    """
    发送通知给用户
    
    参数:
        user_id: 用户ID
        notification_type: 通知类型 (email, push, sms, in_app)
        content: 通知内容
        priority: 优先级 (1-10，数字越大优先级越高)
    """
    try:
        # 记录任务信息
        task_start_time = datetime.datetime.now()
        print(f"发送 {notification_type} 通知给用户 {user_id}，优先级 {priority}")
        
        # 获取用户的联系方式
        user_contact = get_user_contact_info(user_id)
        if not user_contact:
            raise ValueError(f"找不到用户 {user_id} 的联系方式")
        
        # 根据通知类型发送不同的消息
        if notification_type == 'email':
            result = send_email(user_contact.get('email'), content)
        elif notification_type == 'push':
            result = send_push_notification(user_contact.get('device_token'), content)
        elif notification_type == 'sms':
            result = send_sms(user_contact.get('phone'), content)
        elif notification_type == 'in_app':
            result = store_in_app_notification(user_id, content)
        else:
            raise ValueError(f"未知的通知类型: {notification_type}")
        
        # 记录发送日志
        log_notification(user_id, notification_type, content, result)
        
        # 更新任务执行时间
        execution_time = (datetime.datetime.now() - task_start_time).total_seconds()
        
        return {
            'status': 'success',
            'user_id': user_id,
            'notification_type': notification_type,
            'execution_time': execution_time,
            'result': result
        }
        
    except Exception as e:
        # 记录错误
        print(f"发送 {notification_type} 通知失败: {str(e)}")
        raise

def get_user_contact_info(user_id):
    """
    从数据库获取用户的联系方式
    实际应用中，这里应该查询数据库或缓存
    """
    # 模拟数据
    mock_users = {
        'user1': {
            'email': 'user1@example.com',
            'phone': '+1234567890',
            'device_token': 'device_token_1'
        },
        'user2': {
            'email': 'user2@example.com',
            'phone': '+1987654321',
            'device_token': 'device_token_2'
        }
    }
    return mock_users.get(user_id)

def send_email(email, content):
    """
    发送邮件
    实际应用中，这里应该调用邮件服务API
    """
    print(f"发送邮件到 {email}: {content}")
    # 模拟API调用
    time.sleep(0.5)
    return {'status': 'sent', 'email': email}

def send_push_notification(device_token, content):
    """
    发送推送通知
    实际应用中，这里应该调用推送服务API
    """
    print(f"发送推送通知到 {device_token}: {content}")
    # 模拟API调用
    time.sleep(0.3)
    return {'status': 'sent', 'device_token': device_token}

def send_sms(phone, content):
    """
    发送短信
    实际应用中，这里应该调用短信服务API
    """
    print(f"发送短信到 {phone}: {content}")
    # 模拟API调用
    time.sleep(0.8)
    return {'status': 'sent', 'phone': phone}

def store_in_app_notification(user_id, content):
    """
    存储应用内通知
    实际应用中，这里应该将通知保存到数据库
    """
    print(f"存储应用内通知给用户 {user_id}: {content}")
    # 模拟数据库操作
    time.sleep(0.2)
    notification_id = f"notif_{user_id}_{int(time.time())}"
    return {'status': 'stored', 'notification_id': notification_id}

def log_notification(user_id, notification_type, content, result):
    """
    记录通知日志
    """
    log_entry = {
        'user_id': user_id,
        'type': notification_type,
        'content': content,
        'result': result,
        'timestamp': datetime.datetime.now().isoformat()
    }
    print(f"通知日志: {json.dumps(log_entry)}")
    # 实际应用中，这里应该将日志保存到数据库或日志系统

@app.task(queue='notifications')
def batch_send_notifications(notification_list):
    """
    批量发送通知
    
    参数:
        notification_list: 通知列表，每个通知包含 user_id, notification_type, content, priority
    """
    # 创建任务组
    tasks = [
        send_notification.s(
            item['user_id'],
            item['notification_type'],
            item['content'],
            item.get('priority', 5)
        ) for item in notification_list
    ]
    
    # 执行并行任务
    job = group(tasks)
    result = job.apply_async()
    
    return {
        'group_id': result.id,
        'total_notifications': len(notification_list)
    }

# =============================================================================
# 4. 微服务架构中的任务协调
# =============================================================================

@app.task
def create_order(order_data):
    """创建订单"""
    print(f"创建订单，数据: {order_data}")
    # 实际应用中应该保存订单到数据库
    order_id = f"ORDER-{order_data.get('user_id', 'unknown')}-{order_data.get('timestamp', int(time.time()))}"
    return {"order_id": order_id, "status": "created", **order_data}

@app.task
def process_payment(payment_data):
    """处理支付 - 模拟调用支付服务"""
    print(f"处理支付: {payment_data}")
    # 实际应用中应该通过API调用支付服务
    return {"payment_id": f"PAY-{payment_data.get('order_id', 'unknown')}", "status": "completed", **payment_data}

@app.task
def update_inventory(inventory_data):
    """更新库存 - 模拟调用库存服务"""
    print(f"更新库存: {inventory_data}")
    # 实际应用中应该通过API调用库存服务
    return {"status": "updated", **inventory_data}

@app.task
def notify_user(notification_data):
    """通知用户 - 模拟调用通知服务"""
    print(f"通知用户: {notification_data}")
    # 实际应用中应该通过API调用通知服务
    return {"status": "notified", **notification_data}

@app.task
def order_workflow(order_data):
    """订单处理工作流"""
    # 创建任务链
    workflow = chain(
        create_order.s(order_data),
        process_payment.s(),
        update_inventory.s(),
        notify_user.s()
    )
    
    # 执行工作流
    result = workflow.apply_async()
    return {"workflow_id": result.id, "order_id": order_data.get("order_id")}

# =============================================================================
# 5. 分布式锁与幂等性保证
# =============================================================================

@app.task(bind=True)
def process_payment_with_lock(self, payment_id, user_id, amount):
    """
    处理支付 - 使用分布式锁确保幂等性
    
    参数:
        self: 任务实例
        payment_id: 支付ID
        user_id: 用户ID
        amount: 金额
    """
    # 生成锁名称
    lock_name = f"payment_lock:{payment_id}"
    
    # 生成唯一标识
    identifier = str(uuid.uuid4())
    
    # 尝试获取锁
    acquired = redis_client.set(lock_name, identifier, nx=True, ex=60)  # 60秒过期
    
    if not acquired:
        # 检查是否是当前任务持有锁（可能是重试）
        current_holder = redis_client.get(lock_name)
        if current_holder and current_holder == identifier:
            # 当前任务已持有锁，继续执行
            pass
        else:
            # 其他任务正在处理，等待并重试
            self.retry(countdown=5, max_retries=3)
    
    try:
        # 检查支付是否已处理（幂等性检查）
        payment_status = redis_client.get(f"payment_status:{payment_id}")
        if payment_status == "completed":
            return {
                "payment_id": payment_id,
                "status": "completed",
                "message": "支付已处理",
                "duplicate": True
            }
        
        # 执行支付处理逻辑
        print(f"处理支付 {payment_id}，用户 {user_id}，金额 {amount}")
        
        # 模拟支付处理延迟
        time.sleep(2)
        
        # 更新支付状态
        redis_client.setex(f"payment_status:{payment_id}", 86400, "completed")
        
        # 记录支付日志
        payment_data = {
            "payment_id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "timestamp": time.time(),
            "status": "completed"
        }
        
        # 保存支付记录
        for key, value in payment_data.items():
            redis_client.hset(f"payment:{payment_id}", key, value)
        
        return {
            "payment_id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "status": "completed"
        }
        
    finally:
        # 释放锁
        if acquired:
            # 确保只释放自己的锁
            current_holder = redis_client.get(lock_name)
            if current_holder and current_holder == identifier:
                redis_client.delete(lock_name)

# =============================================================================
# 6. 批量任务处理与分片
# =============================================================================

@app.task
def process_batch_items(items):
    """
    批量处理项目
    
    参数:
        items: 项目列表
    """
    results = []
    for item in items:
        # 处理单个项目
        result = process_single_item(item)
        results.append(result)
    return results

def process_single_item(item):
    """
    处理单个项目
    """
    # 模拟处理
    time.sleep(0.1)
    return {"item": item, "processed": True, "timestamp": time.time()}

@app.task
def process_large_dataset(dataset_id, total_shards, shard_id):
    """
    处理数据集的一个分片
    
    参数:
        dataset_id: 数据集ID
        total_shards: 总分片数
        shard_id: 当前分片ID
    """
    # 计算分片范围
    dataset_size = get_dataset_size(dataset_id)
    items_per_shard = dataset_size // total_shards
    start_idx = shard_id * items_per_shard
    end_idx = start_idx + items_per_shard
    
    # 获取分片数据
    shard_data = get_dataset_shard(dataset_id, start_idx, end_idx)
    
    # 处理数据
    results = []
    for item in shard_data:
        # 处理单个项目
        results.append(process_data_item(item))
    
    return {
        'dataset_id': dataset_id,
        'shard_id': shard_id,
        'total_shards': total_shards,
        'processed_count': len(results),
        'results': results
    }

@app.task
def aggregate_results(results):
    """
    聚合所有分片的结果
    
    参数:
        results: 分片结果列表
    """
    total_processed = sum(r['processed_count'] for r in results)
    dataset_id = results[0]['dataset_id'] if results else "unknown"
    return {
        'dataset_id': dataset_id,
        'status': 'completed',
        'total_processed': total_processed,
        'shards_processed': len(results)
    }

def get_dataset_size(dataset_id):
    """
    获取数据集大小
    实际应用中应该从数据库查询
    """
    # 模拟数据集大小
    return 10000

def get_dataset_shard(dataset_id, start_idx, end_idx):
    """
    获取数据集的一个分片
    实际应用中应该从数据库或文件系统读取
    """
    # 模拟数据
    return [f"item_{i}" for i in range(start_idx, end_idx)]

def process_data_item(item):
    """
    处理单个数据项
    """
    # 模拟处理
    time.sleep(0.05)
    return {"item": item, "processed": True}

def start_sharded_processing(dataset_id, num_shards=10):
    """
    启动数据集的分片处理
    
    参数:
        dataset_id: 数据集ID
        num_shards: 分片数量
    """
    # 创建分片任务
    tasks = [process_large_dataset.s(dataset_id, num_shards, i) for i in range(num_shards)]
    
    # 使用chord确保所有分片处理完成后执行回调
    task = chord(tasks)(aggregate_results.s())
    return task.id

# =============================================================================
# 演示函数
# =============================================================================

def demo_image_processing():
    """
    演示图像处理功能
    """
    # 创建测试目录
    os.makedirs("test_images", exist_ok=True)
    
    # 创建一个简单的测试图像
    img = Image.new('RGB', (1000, 800), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((500, 400), "Test Image", fill='black', anchor='mm')
    test_image_path = "test_images/test.jpg"
    img.save(test_image_path)
    
    print(f"创建测试图像: {test_image_path}")
    
    # 定义图像处理操作
    operations = [
        {"type": "resize", "width": 800, "height": 600},
        {"type": "thumbnail", "size": (150, 150)},
        {"type": "watermark", "text": "Demo Site", "position": "bottom-right"}
    ]
    
    # 提交图像处理任务
    result = process_image.delay(test_image_path, operations)
    print(f"图像处理任务已提交，任务ID: {result.id}")
    
    # 等待任务完成并获取结果
    try:
        task_result = result.get(timeout=30)
        print(f"图像处理完成: {task_result}")
    except Exception as e:
        print(f"获取任务结果失败: {e}")

def demo_order_workflow():
    """
    演示订单处理工作流
    """
    # 准备订单数据
    order_data = {
        "user_id": "user1",
        "items": ["product1", "product2"],
        "total_amount": 199.99,
        "timestamp": int(time.time())
    }
    
    # 提交订单处理工作流
    result = order_workflow.delay(order_data)
    print(f"订单工作流已提交，工作流ID: {result.id}")
    
    # 等待工作流完成并获取结果
    try:
        task_result = result.get(timeout=30)
        print(f"订单工作流完成: {task_result}")
    except Exception as e:
        print(f"获取工作流结果失败: {e}")

def demo_distributed_payment():
    """
    演示分布式支付处理（带锁和幂等性保证）
    """
    # 准备支付数据
    payment_id = f"PAY-{int(time.time())}"
    user_id = "user1"
    amount = 99.99
    
    print(f"准备处理支付: {payment_id}, 用户: {user_id}, 金额: {amount}")
    
    # 模拟并发调用多次
    task_ids = []
    for i in range(3):
        result = process_payment_with_lock.delay(payment_id, user_id, amount)
        task_ids.append(result.id)
        print(f"提交支付任务 #{i+1}，任务ID: {result.id}")
    
    # 等待所有任务完成
    for i, task_id in enumerate(task_ids):
        try:
            from celery.result import AsyncResult
            result = AsyncResult(task_id)
            task_result = result.get(timeout=30)
            print(f"支付任务 #{i+1} 结果: {task_result}")
        except Exception as e:
            print(f"获取支付任务 #{i+1} 结果失败: {e}")

def demo_sharded_processing():
    """
    演示分片处理大型数据集
    """
    dataset_id = f"dataset-{int(time.time())}"
    num_shards = 5
    
    print(f"开始处理数据集: {dataset_id}，分片数量: {num_shards}")
    
    # 启动分片处理
    workflow_id = start_sharded_processing(dataset_id, num_shards)
    print(f"分片处理工作流已启动，工作流ID: {workflow_id}")
    
    # 等待工作流完成并获取结果
    try:
        from celery.result import AsyncResult
        result = AsyncResult(workflow_id)
        task_result = result.get(timeout=60)
        print(f"分片处理完成: {task_result}")
    except Exception as e:
        print(f"获取工作流结果失败: {e}")

def main():
    """
    主函数，演示所有功能
    """
    print("=== Celery 实际应用案例演示 ===")
    
    # 演示图像处理
    print("\n1. 演示图像处理")
    demo_image_processing()
    
    # 演示订单处理工作流
    print("\n2. 演示订单处理工作流")
    demo_order_workflow()
    
    # 演示分布式支付处理
    print("\n3. 演示分布式支付处理")
    demo_distributed_payment()
    
    # 演示分片处理
    print("\n4. 演示分片处理大型数据集")
    demo_sharded_processing()
    
    print("\n=== 演示完成 ===")
    print("注意：请确保Celery worker正在运行以处理这些任务。")

if __name__ == "__main__":
    main()
