#!/usr/bin/env python3
"""
Demo应用 - 生成HTTP请求指标用于PromQL练习
"""

from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import random
import time
from threading import Thread

app = Flask(__name__)

# 定义指标
http_requests_total = Counter(
    'http_requests_total',
    'HTTP请求总数',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP请求延迟',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

active_requests = Gauge(
    'http_active_requests',
    '当前活跃请求数'
)

# 模拟业务指标
order_total = Counter('order_total', '订单总数', ['status'])
payment_amount = Counter('payment_amount_total', '支付总金额')
user_login = Counter('user_login_total', '用户登录次数', ['method'])


@app.route('/metrics')
def metrics():
    """Prometheus指标接口"""
    return generate_latest(REGISTRY)


@app.route('/')
def home():
    """首页"""
    return jsonify({
        'service': 'Demo App for PromQL Learning',
        'endpoints': [
            '/metrics - Prometheus指标',
            '/api/users - 用户列表',
            '/api/orders - 订单列表',
            '/api/products - 产品列表',
            '/health - 健康检查'
        ]
    })


@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """用户API"""
    method = request.method
    status = '200' if random.random() > 0.1 else '500'
    
    with active_requests.track_inprogress():
        start = time.time()
        
        # 模拟处理时间
        time.sleep(random.uniform(0.01, 0.5))
        
        duration = time.time() - start
        http_request_duration_seconds.labels(method=method, endpoint='/api/users').observe(duration)
        http_requests_total.labels(method=method, endpoint='/api/users', status=status).inc()
        
        if status == '200':
            return jsonify({'users': ['Alice', 'Bob', 'Charlie']}), 200
        else:
            return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    """订单API"""
    method = request.method
    status = '200' if random.random() > 0.05 else '500'
    
    with active_requests.track_inprogress():
        start = time.time()
        
        # 模拟处理时间
        time.sleep(random.uniform(0.01, 1.0))
        
        duration = time.time() - start
        http_request_duration_seconds.labels(method=method, endpoint='/api/orders').observe(duration)
        http_requests_total.labels(method=method, endpoint='/api/orders', status=status).inc()
        
        # 模拟订单创建
        if method == 'POST':
            order_status = 'success' if status == '200' else 'failed'
            order_total.labels(status=order_status).inc()
            if order_status == 'success':
                payment_amount.inc(random.uniform(10, 1000))
        
        if status == '200':
            return jsonify({'orders': [{'id': 1, 'total': 100}, {'id': 2, 'total': 200}]}), 200
        else:
            return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/api/products', methods=['GET'])
def products():
    """产品API"""
    method = request.method
    status = '200' if random.random() > 0.02 else '404'
    
    with active_requests.track_inprogress():
        start = time.time()
        
        # 模拟处理时间
        time.sleep(random.uniform(0.005, 0.2))
        
        duration = time.time() - start
        http_request_duration_seconds.labels(method=method, endpoint='/api/products').observe(duration)
        http_requests_total.labels(method=method, endpoint='/api/products', status=status).inc()
        
        if status == '200':
            return jsonify({'products': ['Product A', 'Product B', 'Product C']}), 200
        else:
            return jsonify({'error': 'Not Found'}), 404


@app.route('/health')
def health():
    """健康检查"""
    http_requests_total.labels(method='GET', endpoint='/health', status='200').inc()
    return jsonify({'status': 'healthy'}), 200


def generate_traffic():
    """后台线程生成模拟流量"""
    import requests
    import time
    
    endpoints = [
        'http://localhost:8000/api/users',
        'http://localhost:8000/api/orders',
        'http://localhost:8000/api/products',
        'http://localhost:8000/health'
    ]
    
    methods = ['GET', 'POST']
    
    while True:
        try:
            endpoint = random.choice(endpoints)
            method = random.choice(methods) if '/api/' in endpoint else 'GET'
            
            if method == 'GET':
                requests.get(endpoint, timeout=5)
            else:
                requests.post(endpoint, json={'data': 'test'}, timeout=5)
            
            # 模拟用户登录
            if random.random() > 0.9:
                login_method = random.choice(['password', 'oauth', 'sso'])
                user_login.labels(method=login_method).inc()
            
            # 随机延迟
            time.sleep(random.uniform(0.1, 2.0))
        except:
            pass


if __name__ == '__main__':
    # 启动后台流量生成线程
    traffic_thread = Thread(target=generate_traffic, daemon=True)
    traffic_thread.start()
    
    # 启动Flask应用
    print("🚀 Demo App启动成功!")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("🏠 Home: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000)
