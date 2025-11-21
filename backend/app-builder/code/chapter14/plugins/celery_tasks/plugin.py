from flask_appbuilder import BasePlugin
from flask import current_app, current_app as app
from celery import Celery
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable

class CeleryTasksPlugin(BasePlugin):
    name = "Celery Tasks"
    category = "Background Processing"
    version = "1.0.0"
    
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        self.celery = None
        self.logger = logging.getLogger('celery_tasks')
        self.tasks = {}
        self.init_celery()
    
    def init_celery(self):
        """初始化Celery"""
        try:
            # 创建Celery实例
            self.celery = Celery(current_app.import_name)
            
            # 配置Celery
            self.celery.conf.update(
                broker_url=current_app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                result_backend=current_app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
                task_serializer=current_app.config.get('CELERY_TASK_SERIALIZER', 'json'),
                result_serializer=current_app.config.get('CELERY_RESULT_SERIALIZER', 'json'),
                accept_content=current_app.config.get('CELERY_ACCEPT_CONTENT', ['json']),
                timezone=current_app.config.get('CELERY_TIMEZONE', 'UTC'),
                enable_utc=current_app.config.get('CELERY_ENABLE_UTC', True),
                task_track_started=True,
                worker_prefetch_multiplier=1,
                task_acks_late=True
            )
            
            # 集成Flask应用上下文
            self.celery.conf.update(
                task_create_missing_queues=True,
                worker_hijack_root_logger=False
            )
            
            self.logger.info("Celery initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Celery: {str(e)}")
            self.celery = None
    
    def task(self, *args, **kwargs):
        """任务装饰器"""
        if not self.celery:
            # 如果Celery未初始化，返回一个空装饰器
            def empty_decorator(f):
                return f
            return empty_decorator
        
        return self.celery.task(*args, **kwargs)
    
    def async_task(self, func: Callable, *args, **kwargs) -> Optional[str]:
        """异步执行任务"""
        if not self.celery:
            self.logger.error("Celery not initialized")
            return None
        
        try:
            # 异步执行任务
            task_result = func.delay(*args, **kwargs)
            task_id = task_result.id
            
            # 记录任务信息
            self.tasks[task_id] = {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'created_at': datetime.now()
            }
            
            self.logger.info(f"Task {func.__name__} submitted with ID: {task_id}")
            return task_id
        except Exception as e:
            self.logger.error(f"Failed to submit task {func.__name__}: {str(e)}")
            return None
    
    def schedule_task(self, func: Callable, schedule: Dict[str, Any], *args, **kwargs) -> Optional[str]:
        """定时执行任务"""
        if not self.celery:
            self.logger.error("Celery not initialized")
            return None
        
        try:
            # 创建周期性任务
            task_name = f"scheduled_{func.__name__}"
            
            # 配置定时任务
            self.celery.conf.beat_schedule = {
                task_name: {
                    'task': f"{func.__module__}.{func.__name__}",
                    'schedule': schedule,
                    'args': args,
                    'kwargs': kwargs
                }
            }
            
            self.logger.info(f"Scheduled task {func.__name__} with schedule: {schedule}")
            return task_name
        except Exception as e:
            self.logger.error(f"Failed to schedule task {func.__name__}: {str(e)}")
            return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if not self.celery:
            self.logger.error("Celery not initialized")
            return None
        
        try:
            from celery.result import AsyncResult
            result = AsyncResult(task_id, app=self.celery)
            
            status_info = {
                'task_id': task_id,
                'status': result.status,
                'result': result.result if result.ready() else None,
                'traceback': result.traceback if result.failed() else None
            }
            
            # 如果任务信息存在，添加额外信息
            if task_id in self.tasks:
                status_info.update(self.tasks[task_id])
            
            return status_info
        except Exception as e:
            self.logger.error(f"Failed to get task status for {task_id}: {str(e)}")
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if not self.celery:
            self.logger.error("Celery not initialized")
            return False
        
        try:
            from celery.result import AsyncResult
            result = AsyncResult(task_id, app=self.celery)
            result.revoke(terminate=True)
            
            self.logger.info(f"Task {task_id} cancelled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False
    
    def retry_task(self, task_id: str) -> Optional[str]:
        """重试任务"""
        if not self.celery:
            self.logger.error("Celery not initialized")
            return None
        
        try:
            # 获取原始任务信息
            if task_id not in self.tasks:
                self.logger.error(f"Task {task_id} not found")
                return None
            
            task_info = self.tasks[task_id]
            func_name = task_info['function']
            args = task_info['args']
            kwargs = task_info['kwargs']
            
            # 重新提交任务
            # 注意：这里需要根据实际的应用结构来重新获取函数引用
            # 这是一个简化的实现
            self.logger.info(f"Retrying task {func_name} with ID: {task_id}")
            return task_id
        except Exception as e:
            self.logger.error(f"Failed to retry task {task_id}: {str(e)}")
            return None
    
    def get_active_tasks(self) -> list:
        """获取活跃任务列表"""
        if not self.celery:
            self.logger.error("Celery not initialized")
            return []
        
        try:
            # 获取活跃任务
            inspector = self.celery.control.inspect()
            active_tasks = inspector.active()
            
            if active_tasks:
                # 展平所有worker的任务
                all_tasks = []
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        task_info = {
                            'worker': worker,
                            'task_id': task['id'],
                            'name': task['name'],
                            'args': task['args'],
                            'kwargs': task['kwargs'],
                            'time_start': task['time_start']
                        }
                        all_tasks.append(task_info)
                return all_tasks
            
            return []
        except Exception as e:
            self.logger.error(f"Failed to get active tasks: {str(e)}")
            return []
    
    def get_task_stats(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        if not self.celery:
            self.logger.error("Celery not initialized")
            return {}
        
        try:
            inspector = self.celery.control.inspect()
            
            # 获取各种统计信息
            stats = {
                'registered_tasks': inspector.registered() or {},
                'active_tasks': len(self.get_active_tasks()),
                'scheduled_tasks': len(inspector.scheduled() or {}),
                'reserved_tasks': len(inspector.reserved() or {}),
                'revoked_tasks': len(inspector.revoked() or {})
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get task stats: {str(e)}")
            return {}

# 全局任务装饰器
def async_task(func):
    """全局异步任务装饰器"""
    def wrapper(*args, **kwargs):
        # 获取Celery插件实例
        appbuilder = app.extensions['appbuilder']
        celery_plugin = None
        for plugin in appbuilder.plugins:
            if isinstance(plugin, CeleryTasksPlugin):
                celery_plugin = plugin
                break
        
        if celery_plugin and celery_plugin.celery:
            # 使用Celery执行异步任务
            task_func = celery_plugin.celery.task(func)
            return task_func.delay(*args, **kwargs)
        else:
            # 如果没有找到Celery插件，则同步执行函数
            return func(*args, **kwargs)
    return wrapper

# 预定义的一些常用任务类型
@async_task
def send_email_task(recipient, subject, body):
    """发送邮件任务"""
    # 这里应该是实际的邮件发送逻辑
    print(f"Sending email to {recipient} with subject: {subject}")
    return f"Email sent to {recipient}"

@async_task
def process_file_task(file_path):
    """处理文件任务"""
    # 这里应该是实际的文件处理逻辑
    print(f"Processing file: {file_path}")
    return f"File {file_path} processed"

@async_task
def generate_report_task(report_type, data):
    """生成报告任务"""
    # 这里应该是实际的报告生成逻辑
    print(f"Generating {report_type} report")
    return f"{report_type} report generated"