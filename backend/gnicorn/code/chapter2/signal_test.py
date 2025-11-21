# signal_test.py
# 用于测试Gunicorn信号处理的示例应用

import os
import time
import signal
from flask import Flask, jsonify, request

app = Flask(__name__)

# 全局变量，用于跟踪信号
signal_received = None
worker_pid = os.getpid()

@app.route('/')
def hello():
    """简单响应，显示当前worker PID"""
    return jsonify({
        "message": "Hello from Gunicorn!",
        "worker_pid": worker_pid,
        "signal_received": signal_received
    })

@app.route('/long-task')
def long_task():
    """长时间运行的任务"""
    duration = request.args.get('duration', 30, type=int)
    
    print(f"Starting long task for {duration} seconds...")
    
    # 模拟长时间任务
    for i in range(duration):
        time.sleep(1)
        print(f"Progress: {i+1}/{duration}")
    
    return jsonify({
        "task": "completed",
        "duration": f"{duration} seconds",
        "worker_pid": worker_pid
    })

@app.route('/signal-status')
def signal_status():
    """检查信号状态"""
    return jsonify({
        "worker_pid": worker_pid,
        "signal_received": signal_received,
        "timestamp": time.time()
    })

def handle_signal(signum, frame):
    """自定义信号处理函数"""
    global signal_received
    signal_received = f"Signal {signum} received at {time.time()}"
    print(f"Worker {worker_pid}: {signal_received}")

# 注册信号处理函数
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGUSR1, handle_signal)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)