#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP头部服务器示例
展示如何在Flask应用中正确设置各种HTTP头部
"""

from flask import Flask, jsonify, request, make_response
import json
from datetime import datetime, timedelta


app = Flask(__name__)


@app.route('/')
def home():
    """首页"""
    return jsonify({
        "message": "HTTP头部服务器示例",
        "endpoints": [
            "GET /api/users - 获取用户列表",
            "POST /api/users - 创建用户",
            "GET /api/users/<id> - 获取特定用户",
            "OPTIONS /api/users - 获取支持的方法",
            "GET /api/secure-data - 安全数据（需要认证）",
            "GET /api/cache-example - 缓存示例",
            "GET /api/cors-example - CORS示例"
        ]
    })


@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    # 设置安全头部
    response = make_response(jsonify({
        "users": [
            {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
            {"id": 2, "name": "李四", "email": "lisi@example.com"}
        ],
        "total": 2
    }))
    
    # 设置安全头部
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 设置缓存控制（公共资源可以缓存）
    response.headers['Cache-Control'] = 'public, max-age=300'  # 缓存5分钟
    
    return response


@app.route('/api/users', methods=['POST'])
def create_user():
    """创建新用户"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        response = make_response(jsonify({
            "error": "缺少必要参数",
            "required": ["name", "email"]
        }), 400)
        
        # 错误响应不缓存
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # 模拟创建用户
    new_user = {
        "id": 3,
        "name": data['name'],
        "email": data['email'],
        "created_at": datetime.now().isoformat()
    }
    
    response = make_response(jsonify(new_user), 201)
    
    # 成功创建资源后不缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取特定用户"""
    # 模拟查找用户
    if user_id == 1:
        user = {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
    elif user_id == 2:
        user = {"id": 2, "name": "李四", "email": "lisi@example.com"}
    else:
        response = make_response(jsonify({"error": "用户不存在"}), 404)
        response.headers['Cache-Control'] = 'no-cache'
        return response
    
    response = make_response(jsonify(user))
    
    # 用户信息可以短时间缓存
    response.headers['Cache-Control'] = 'public, max-age=60'  # 缓存1分钟
    response.headers['ETag'] = f'user-{user_id}-{hash(str(user))}'
    
    return response


@app.route('/api/users', methods=['OPTIONS'])
def users_options():
    """返回支持的HTTP方法"""
    response = make_response('', 204)
    
    # 设置CORS头部
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # 设置其他安全头部
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    
    return response


@app.route('/api/secure-data', methods=['GET'])
def get_secure_data():
    """获取需要认证的安全数据"""
    # 检查Authorization头部（简化示例）
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        response = make_response(jsonify({"error": "需要认证"}), 401)
        response.headers['WWW-Authenticate'] = 'Bearer realm="Secure Data"'
        response.headers['Cache-Control'] = 'no-cache'
        return response
    
    # 验证token（简化示例）
    token = auth_header.split(' ')[1]
    if token != 'valid-token':
        response = make_response(jsonify({"error": "无效的认证令牌"}), 401)
        response.headers['WWW-Authenticate'] = 'Bearer realm="Secure Data", error="invalid_token"'
        response.headers['Cache-Control'] = 'no-cache'
        return response
    
    # 返回安全数据
    response = make_response(jsonify({
        "data": "这是受保护的安全数据",
        "sensitive_info": "只有认证用户才能访问"
    }))
    
    # 安全数据不缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # 设置安全头部
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
    
    return response


@app.route('/api/cache-example', methods=['GET'])
def cache_example():
    """缓存示例"""
    # 生成动态内容
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    response = make_response(jsonify({
        "message": "这个响应会被缓存",
        "generated_at": current_time,
        "cache_info": "设置了不同的缓存策略"
    }))
    
    # 根据查询参数设置不同的缓存策略
    cache_type = request.args.get('type', 'default')
    
    if cache_type == 'public':
        # 公共缓存
        response.headers['Cache-Control'] = 'public, max-age=3600'  # 缓存1小时
    elif cache_type == 'private':
        # 私有缓存
        response.headers['Cache-Control'] = 'private, max-age=1800'  # 缓存30分钟
    elif cache_type == 'no-cache':
        # 不缓存
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    else:
        # 默认缓存
        response.headers['Cache-Control'] = 'public, max-age=600'  # 缓存10分钟
    
    # 设置ETag
    response.headers['ETag'] = f'cache-example-{hash(current_time)}'
    
    return response


@app.route('/api/cors-example', methods=['GET', 'POST'])
def cors_example():
    """CORS示例"""
    origin = request.headers.get('Origin', '*')
    
    if request.method == 'GET':
        response = make_response(jsonify({
            "message": "CORS GET请求示例",
            "method": "GET",
            "origin": origin
        }))
    else:  # POST
        data = request.get_json() or {}
        response = make_response(jsonify({
            "message": "CORS POST请求示例",
            "method": "POST",
            "received_data": data,
            "origin": origin
        }))
    
    # 设置CORS头部
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    # 设置安全头部
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response


@app.route('/api/download')
def download_example():
    """下载示例"""
    content = "这是一个下载文件的内容示例"
    
    response = make_response(content)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename="example.txt"'
    response.headers['Content-Length'] = str(len(content))
    
    # 下载内容不缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@app.after_request
def after_request(response):
    """
    在每个请求后添加通用头部
    """
    # 添加安全头部
    if 'X-Content-Type-Options' not in response.headers:
        response.headers['X-Content-Type-Options'] = 'nosniff'
    
    if 'X-Frame-Options' not in response.headers:
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # 添加HSTS（仅适用于HTTPS）
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # 添加引用策略
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)