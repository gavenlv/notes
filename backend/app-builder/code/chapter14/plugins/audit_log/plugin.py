from flask_appbuilder import BasePlugin
from flask import request, g, current_app
from datetime import datetime
import logging
import json
import os
from functools import wraps

class AuditLogPlugin(BasePlugin):
    name = "Audit Log"
    category = "Security"
    version = "1.0.0"
    
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        self.logger = logging.getLogger('audit')
        self.setup_logger()
    
    def setup_logger(self):
        """设置审计日志记录器"""
        # 确保日志目录存在
        log_dir = os.path.join(current_app.root_path, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 设置审计日志处理器
        log_file = current_app.config.get('AUDIT_LOG_FILE', 
                                         os.path.join(log_dir, 'audit.log'))
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_action(self, action, details=None, user=None):
        """记录操作日志"""
        if user is None:
            user = getattr(g, 'user', None)
        
        user_info = f"{user.username} ({user.id})" if user else "Anonymous"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user_info,
            'action': action,
            'ip': request.remote_addr if request else 'Unknown',
            'url': request.url if request else 'Unknown',
            'method': request.method if request else 'Unknown',
            'user_agent': request.headers.get('User-Agent') if request else 'Unknown',
            'details': details or {}
        }
        
        self.logger.info(f"AUDIT: {json.dumps(log_entry, ensure_ascii=False)}")
    
    def log_model_change(self, operation, model_name, record_id, changes=None):
        """记录模型变更"""
        details = {
            'model': model_name,
            'record_id': record_id,
            'changes': changes or {}
        }
        self.log_action(f"MODEL_{operation.upper()}", details)
    
    def log_security_event(self, event_type, details=None):
        """记录安全事件"""
        self.log_action(f"SECURITY_{event_type.upper()}", details)
    
    def audit_decorator(self, action_name=None):
        """审计装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                action = action_name or f.__name__
                try:
                    result = f(*args, **kwargs)
                    self.log_action(action, {'status': 'success'})
                    return result
                except Exception as e:
                    self.log_action(action, {'status': 'error', 'error': str(e)})
                    raise
            return decorated_function
        return decorator

# 全局审计装饰器
def audit_action(action_name):
    """全局审计装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 获取审计插件实例
            appbuilder = current_app.extensions['appbuilder']
            audit_plugin = None
            for plugin in appbuilder.plugins:
                if isinstance(plugin, AuditLogPlugin):
                    audit_plugin = plugin
                    break
            
            if audit_plugin:
                try:
                    result = f(*args, **kwargs)
                    audit_plugin.log_action(action_name, {'status': 'success'})
                    return result
                except Exception as e:
                    audit_plugin.log_action(action_name, {'status': 'error', 'error': str(e)})
                    raise
            else:
                # 如果没有找到审计插件，则正常执行函数
                return f(*args, **kwargs)
        return wrapper
    return decorator