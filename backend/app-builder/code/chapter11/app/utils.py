import time
from functools import wraps
from flask import current_app

def monitor_performance(f):
    """性能监控装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        current_app.logger.info(f"Function {f.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    return decorated_function