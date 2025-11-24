# async_app.py
# 异步应用示例，用于测试异步Worker

import time
import json
import asyncio
import random
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    """简单响应"""
    return jsonify({"message": "Hello from Async Gunicorn!"})

@app.route('/async-io')
def async_io():
    """模拟异步I/O操作"""
    # 在实际应用中，这里可能是数据库查询、HTTP请求等异步操作
    # 注意：这个示例仍然是同步的，但可以用于测试异步Worker的性能
    time.sleep(0.1)  # 模拟100ms的I/O等待
    
    return jsonify({
        "task": "async_io",
        "wait_time": "100ms",
        "note": "This is still sync code but can benefit from async workers"
    })

@app.route('/simultaneous-requests')
def simultaneous_requests():
    """模拟同时处理多个请求"""
    # 在sync worker中，这会阻塞整个worker
    # 在async worker中，其他请求可以在此期间被处理
    time.sleep(0.5)  # 模拟500ms的处理时间
    
    return jsonify({
        "task": "simultaneous_requests",
        "processing_time": "500ms",
        "note": "Async workers can handle other requests during this time"
    })

@app.route('/long-polling')
def long_polling():
    """长轮询示例"""
    # 在实际应用中，这里可能等待某个事件发生
    max_wait = 30  # 最多等待30秒
    wait_time = random.uniform(1, 10)  # 随机等待1-10秒
    
    time.sleep(wait_time)
    
    return jsonify({
        "task": "long_polling",
        "waited": f"{wait_time:.2f} seconds",
        "max_wait": f"{max_wait} seconds"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)