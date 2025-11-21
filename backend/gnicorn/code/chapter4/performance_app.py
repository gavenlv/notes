# performance_app.py
# 用于测试Gunicorn性能的应用

import time
import json
import random
from flask import Flask, jsonify, request
from functools import wraps

app = Flask(__name__)

# 简单内存缓存
cache = {}

def cache_result(timeout=60):
    """简单的缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键
            key = f"{f.__name__}:{request.url}"
            
            # 检查缓存
            if key in cache:
                data, timestamp = cache[key]
                if time.time() - timestamp < timeout:
                    return data
            
            # 执行函数并缓存结果
            result = f(*args, **kwargs)
            cache[key] = (result, time.time())
            
            return result
        return decorated_function
    return decorator

@app.route('/')
def hello():
    """简单响应"""
    return jsonify({"message": "Hello, Gunicorn Performance Test!"})

@app.route('/cpu-intensive')
def cpu_intensive():
    """CPU密集型任务"""
    # 模拟CPU密集型计算
    result = 0
    for i in range(1000000):
        result += random.random()
    
    return jsonify({
        "task": "cpu_intensive",
        "result": result,
        "worker": "sync"
    })

@app.route('/io-intensive')
def io_intensive():
    """I/O密集型任务（模拟）"""
    # 模拟I/O等待（实际应用中可能是数据库查询、HTTP请求等）
    time.sleep(0.1)  # 模拟100ms的I/O等待
    
    return jsonify({
        "task": "io_intensive",
        "wait_time": "100ms",
        "worker": "sync"
    })

@app.route('/mixed')
def mixed():
    """混合型任务"""
    # CPU计算
    result = sum(random.random() for _ in range(100000))
    
    # I/O等待
    time.sleep(0.05)  # 模拟50ms的I/O等待
    
    return jsonify({
        "task": "mixed",
        "result": result,
        "wait_time": "50ms",
        "worker": "sync"
    })

@app.route('/cached-data')
@cache_result(timeout=60)
def cached_data():
    """缓存数据端点"""
    # 模拟耗时操作
    time.sleep(0.5)
    
    data = {
        "timestamp": time.time(),
        "random_value": random.randint(1, 1000),
        "cached": True
    }
    
    return jsonify(data)

@app.route('/expensive-computation')
def expensive_computation():
    """昂贵的计算"""
    n = request.args.get('n', 1000, type=int)
    
    # 计算斐波那契数列（递归实现，效率低）
    def fibonacci(k):
        if k <= 1:
            return k
        return fibonacci(k-1) + fibonacci(k-2)
    
    result = fibonacci(n)
    
    return jsonify({
        "n": n,
        "fibonacci": result,
        "time_complexity": "O(2^n)"
    })

@app.route('/memory-test')
def memory_test():
    """内存使用测试"""
    # 分配内存
    size = request.args.get('size', 10, type=int)
    data = [random.random() for _ in range(size * 1000000)]  # 分配size MB的数据
    
    return jsonify({
        "message": f"Allocated {size}MB of data",
        "data_length": len(data),
        "first_value": data[0],
        "last_value": data[-1]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)