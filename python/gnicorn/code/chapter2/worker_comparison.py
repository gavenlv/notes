# worker_comparison.py
# 用于比较不同Worker类型性能的测试应用

import time
import random
import json
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    """简单响应"""
    return jsonify({"message": "Hello from Gunicorn!"})

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
        "worker_type": "sync"
    })

@app.route('/io-intensive')
def io_intensive():
    """I/O密集型任务（模拟）"""
    # 模拟I/O等待（实际应用中可能是数据库查询、HTTP请求等）
    time.sleep(0.1)  # 模拟100ms的I/O等待
    
    return jsonify({
        "task": "io_intensive",
        "wait_time": "100ms",
        "worker_type": "sync"
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
        "worker_type": "sync"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)