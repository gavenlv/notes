# monitoring_app.py
# 用于演示Gunicorn监控和日志管理的应用

import time
import json
import logging
import psutil
import os
from flask import Flask, jsonify, request, g
from functools import wraps

app = Flask(__name__)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 请求计数器
request_count = 0
request_times = []
error_count = 0

# 请求装饰器
def track_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_count, request_times, error_count
        
        # 记录请求开始时间
        start_time = time.time()
        request_count += 1
        
        try:
            # 执行函数
            result = f(*args, **kwargs)
            status = 200
            
            return result
        except Exception as e:
            status = 500
            error_count += 1
            logger.exception(f"Request failed: {str(e)}")
            raise
        finally:
            # 记录请求时间
            request_time = time.time() - start_time
            request_times.append(request_time)
            
            # 只保留最近1000个请求的时间
            if len(request_times) > 1000:
                request_times = request_times[-1000:]
            
            # 记录请求日志
            logger.info(f"Request: {request.method} {request.path} - Status: {status} - Time: {request_time:.3f}s")
    
    return decorated_function

@app.route('/')
@track_request
def hello():
    return jsonify({"message": "Hello, Gunicorn Monitoring App!"})

@app.route('/metrics')
@track_request
def metrics():
    """提供指标数据"""
    # 计算统计信息
    avg_response_time = sum(request_times) / len(request_times) if request_times else 0
    p95_response_time = sorted(request_times)[int(len(request_times) * 0.95)] if request_times else 0
    
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # 获取进程信息
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    
    # 计算错误率
    error_rate = (error_count / request_count * 100) if request_count > 0 else 0
    
    metrics_data = {
        "timestamp": time.time(),
        "request_count": request_count,
        "error_count": error_count,
        "error_rate_percent": error_rate,
        "avg_response_time_seconds": avg_response_time,
        "p95_response_time_seconds": p95_response_time,
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used / (1024 * 1024),
            "memory_available_mb": memory.available / (1024 * 1024)
        },
        "process": {
            "pid": os.getpid(),
            "memory_rss_mb": process_memory.rss / (1024 * 1024),
            "memory_vms_mb": process_memory.vms / (1024 * 1024)
        }
    }
    
    return jsonify(metrics_data)

@app.route('/health')
@track_request
def health():
    """健康检查端点"""
    # 检查系统资源
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # 健康检查
    health_status = {
        "status": "ok",
        "timestamp": time.time(),
        "checks": {
            "memory": {
                "status": "ok" if memory.percent < 90 else "warning",
                "value": memory.percent,
                "threshold": 90
            },
            "disk": {
                "status": "ok" if disk.percent < 90 else "warning",
                "value": disk.percent,
                "threshold": 90
            },
            "error_rate": {
                "status": "ok" if (error_count / request_count * 100) < 5 else "warning",
                "value": error_count / request_count * 100 if request_count > 0 else 0,
                "threshold": 5
            }
        }
    }
    
    # 确定整体健康状态
    if any(check["status"] != "ok" for check in health_status["checks"].values()):
        health_status["status"] = "warning"
    
    status_code = 503 if health_status["status"] != "ok" else 200
    
    return jsonify(health_status), status_code

@app.route('/logs')
@track_request
def logs():
    """日志端点（仅用于演示，生产环境不推荐）"""
    # 读取最近的日志条目
    lines = request.args.get('lines', 50, type=int)
    level = request.args.get('level', 'INFO')
    
    # 实际应用中应该从日志文件读取
    # 这里仅返回模拟数据
    logs_data = []
    for i in range(lines):
        logs_data.append({
            "timestamp": time.time() - i,
            "level": level,
            "message": f"Sample log message {i} with level {level}"
        })
    
    return jsonify({
        "logs": logs_data,
        "total": len(logs_data)
    })

@app.route('/slow-request')
@track_request
def slow_request():
    """模拟慢请求"""
    delay = request.args.get('delay', 2, type=float)
    
    # 模拟慢操作
    time.sleep(delay)
    
    return jsonify({
        "message": f"This request took {delay} seconds to process",
        "delay": delay
    })

@app.route('/error')
@track_request
def error():
    """模拟错误"""
    error_type = request.args.get('type', 'exception')
    
    if error_type == 'exception':
        raise Exception("This is a test exception")
    elif error_type == 'value_error':
        raise ValueError("This is a test value error")
    elif error_type == 'type_error':
        raise TypeError("This is a test type error")
    else:
        return jsonify({"error": "Unknown error type"}), 400

@app.route('/prometheus-metrics')
@track_request
def prometheus_metrics():
    """Prometheus格式的指标"""
    # 计算统计信息
    avg_response_time = sum(request_times) / len(request_times) if request_times else 0
    
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # 获取进程信息
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    
    # Prometheus格式的指标
    metrics = [
        f"# HELP gunicorn_requests_total Total number of requests",
        f"# TYPE gunicorn_requests_total counter",
        f"gunicorn_requests_total {request_count}",
        "",
        f"# HELP gunicorn_errors_total Total number of errors",
        f"# TYPE gunicorn_errors_total counter",
        f"gunicorn_errors_total {error_count}",
        "",
        f"# HELP gunicorn_request_duration_seconds Request duration in seconds",
        f"# TYPE gunicorn_request_duration_seconds gauge",
        f"gunicorn_request_duration_seconds {avg_response_time}",
        "",
        f"# HELP gunicorn_cpu_usage_percent CPU usage percentage",
        f"# TYPE gunicorn_cpu_usage_percent gauge",
        f"gunicorn_cpu_usage_percent {cpu_percent}",
        "",
        f"# HELP gunicorn_memory_usage_bytes Memory usage in bytes",
        f"# TYPE gunicorn_memory_usage_bytes gauge",
        f"gunicorn_memory_usage_bytes {process_memory.rss}",
        ""
    ]
    
    # 返回文本格式的指标
    return "\n".join(metrics)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)