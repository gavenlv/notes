#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP头部最佳实践示例
展示如何正确设置和使用HTTP头部
"""

import requests
from flask import Flask, jsonify, request, make_response
import json
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__)


def add_security_headers(response):
    """
    为响应添加安全头部
    
    Args:
        response: Flask响应对象
        
    Returns:
        添加了安全头部的响应对象
    """
    # 防止MIME类型嗅探
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # 防止点击劫持
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # XSS保护（虽然现代浏览器已逐渐弃用）
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 引用策略
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    
    # 权限策略
    response.headers['Permissions-Policy'] = (
        "geolocation=(), microphone=(), camera=()"
    )
    
    return response


def require_https(f):
    """
    装饰器：要求HTTPS连接
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and app.config.get('REQUIRE_HTTPS', False):
            # 重定向到HTTPS版本
            https_url = request.url.replace('http://', 'https://', 1)
            response = make_response('', 301)
            response.headers['Location'] = https_url
            return response
        return f(*args, **kwargs)
    return decorated_function


def cache_control(max_age=None, public=False, private=False, no_cache=False):
    """
    装饰器：设置缓存控制
    
    Args:
        max_age: 最大缓存时间（秒）
        public: 是否允许公共缓存
        private: 是否为私有缓存
        no_cache: 是否禁用缓存
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            
            if no_cache:
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            else:
                cache_directives = []
                if public:
                    cache_directives.append('public')
                elif private:
                    cache_directives.append('private')
                
                if max_age is not None:
                    cache_directives.append(f'max-age={max_age}')
                
                if cache_directives:
                    response.headers['Cache-Control'] = ', '.join(cache_directives)
            
            return response
        return decorated_function
    return decorator


@app.route('/')
def home():
    """首页 - 展示最佳实践"""
    response = make_response(jsonify({
        "message": "HTTP头部最佳实践示例",
        "practices": {
            "security": "已应用安全头部",
            "caching": "已应用缓存策略",
            "cors": "已配置CORS",
            "hsts": "HTTPS环境下启用HSTS"
        }
    }))
    
    # 应用安全头部
    response = add_security_headers(response)
    
    # 如果是HTTPS，添加HSTS
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains; preload'
        )
    
    # 设置缓存策略
    response.headers['Cache-Control'] = 'public, max-age=300'  # 缓存5分钟
    
    return response


@app.route('/api/users')
@require_https
@cache_control(max_age=300, public=True)  # 公共资源缓存5分钟
def get_users():
    """获取用户列表 - 应用安全和缓存最佳实践"""
    users = [
        {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
        {"id": 2, "name": "李四", "email": "lisi@example.com"}
    ]
    
    response = jsonify({"users": users, "total": len(users)})
    response = add_security_headers(response)
    
    # 添加ETag
    response.headers['ETag'] = f'users-list-{hash(str(users))}'
    
    return response


@app.route('/api/users', methods=['POST'])
@require_https
@cache_control(no_cache=True)  # POST响应不缓存
def create_user():
    """创建用户 - 不缓存敏感操作"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        response = make_response(jsonify({
            "error": "缺少必要参数",
            "required": ["name", "email"]
        }), 400)
        response = add_security_headers(response)
        return response
    
    # 模拟创建用户
    new_user = {
        "id": 3,
        "name": data['name'],
        "email": data['email'],
        "created_at": datetime.now().isoformat()
    }
    
    response = make_response(jsonify(new_user), 201)
    response = add_security_headers(response)
    
    return response


@app.route('/api/sensitive-data')
@require_https
@cache_control(no_cache=True)  # 敏感数据不缓存
def get_sensitive_data():
    """获取敏感数据 - 应用严格的安全措施"""
    # 检查认证（简化示例）
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        response = make_response(jsonify({"error": "需要认证"}), 401)
        response.headers['WWW-Authenticate'] = 'Bearer realm="Sensitive Data"'
        response = add_security_headers(response)
        return response
    
    # 返回敏感数据
    response = jsonify({
        "message": "这是敏感数据",
        "data": "只有授权用户才能访问的信息"
    })
    
    # 应用额外的安全头部
    response = add_security_headers(response)
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    
    return response


@app.route('/api/download-report')
@require_https
@cache_control(no_cache=True)  # 下载内容不缓存
def download_report():
    """下载报告 - 正确设置下载相关头部"""
    content = "这是一个重要报告的内容"
    
    response = make_response(content)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename="report.txt"'
    response.headers['Content-Length'] = str(len(content))
    
    # 下载内容不缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # 添加安全头部
    response = add_security_headers(response)
    
    return response


@app.route('/api/search')
@require_https
@cache_control(public=True, max_age=60)  # 搜索结果缓存1分钟
def search():
    """搜索接口 - 根据参数调整缓存策略"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # 模拟搜索结果
    results = {
        "query": query,
        "page": page,
        "results": [
            {"id": 1, "title": f"结果1 - 查询: {query}"},
            {"id": 2, "title": f"结果2 - 查询: {query}"}
        ],
        "total": 2
    }
    
    response = jsonify(results)
    response = add_security_headers(response)
    
    # 根据查询内容调整缓存
    if not query:
        # 空查询不缓存
        response.headers['Cache-Control'] = 'no-cache'
    else:
        # 有查询内容可以缓存
        response.headers['Cache-Control'] = 'public, max-age=60'
        response.headers['ETag'] = f'search-{hash(query)}-{page}'
    
    return response


@app.after_request
def after_request(response):
    """
    在每个请求后应用通用的最佳实践
    """
    # 确保安全头部已设置
    response = add_security_headers(response)
    
    # HTTPS环境下添加HSTS
    if request.is_secure:
        if 'Strict-Transport-Security' not in response.headers:
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
    
    # 设置内容类型（如果未设置）
    if 'Content-Type' not in response.headers and response.is_sequence:
        response.headers['Content-Type'] = 'application/json'
    
    return response


# CORS处理示例
@app.before_request
def handle_cors_preflight():
    """处理CORS预检请求"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24小时
        return response


@app.route('/api/data', methods=['GET', 'POST', 'OPTIONS'])
def cors_enabled_endpoint():
    """支持CORS的端点"""
    if request.method == 'OPTIONS':
        # 预检请求由before_request处理
        return ''
    
    origin = request.headers.get('Origin', '*')
    
    if request.method == 'GET':
        response = jsonify({"message": "CORS enabled GET request"})
    else:
        response = jsonify({"message": "CORS enabled POST request"})
    
    # 设置CORS头部
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response


class BestPracticesClient:
    """最佳实践客户端示例"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BestPracticesClient/1.0',
            'Accept': 'application/json'
        })
    
    def demonstrate_conditional_requests(self):
        """演示条件请求的使用"""
        print("=== 条件请求演示 ===")
        
        # 首先获取资源和ETag
        response = self.session.get(f"{self.base_url}/api/users")
        if response.status_code == 200:
            etag = response.headers.get('ETag')
            print(f"获取ETag: {etag}")
            
            if etag:
                # 使用ETag进行条件请求
                headers = {'If-None-Match': etag}
                response2 = self.session.get(
                    f"{self.base_url}/api/users",
                    headers=headers
                )
                print(f"条件请求状态码: {response2.status_code}")
                if response2.status_code == 304:
                    print("服务器返回304 Not Modified - 节省带宽")
                else:
                    print("服务器返回新数据")
    
    def demonstrate_cache_validation(self):
        """演示缓存验证"""
        print("\n=== 缓存验证演示 ===")
        
        # 获取带有Last-Modified的资源
        response = self.session.get(f"{self.base_url}/")
        last_modified = response.headers.get('Last-Modified')
        
        if last_modified:
            print(f"Last-Modified: {last_modified}")
            
            # 使用If-Modified-Since进行条件请求
            headers = {'If-Modified-Since': last_modified}
            response2 = self.session.get(
                f"{self.base_url}/",
                headers=headers
            )
            print(f"条件请求状态码: {response2.status_code}")
            if response2.status_code == 304:
                print("资源未修改，使用缓存版本")
    
    def demonstrate_proper_error_handling(self):
        """演示正确的错误处理"""
        print("\n=== 错误处理演示 ===")
        
        # 尝试访问需要认证的端点
        response = self.session.get(f"{self.base_url}/api/sensitive-data")
        print(f"未认证访问状态码: {response.status_code}")
        
        if response.status_code == 401:
            www_authenticate = response.headers.get('WWW-Authenticate')
            print(f"WWW-Authenticate头部: {www_authenticate}")
            print("客户端应该根据此头部提示用户进行认证")


def main():
    """主函数"""
    print("HTTP头部最佳实践示例")
    print("=" * 50)
    
    # 启动服务器示例
    print("\n启动Flask服务器...")
    print("请在另一个终端运行客户端示例:")
    print("python http_headers_best_practices.py --client")
    
    app.run(host='0.0.0.0', port=5000, debug=True)


def run_client_demo():
    """运行客户端演示"""
    print("HTTP头部最佳实践客户端演示")
    print("=" * 50)
    
    client = BestPracticesClient()
    
    # 演示各种最佳实践
    client.demonstrate_conditional_requests()
    client.demonstrate_cache_validation()
    client.demonstrate_proper_error_handling()


if __name__ == '__main__':
    import sys
    if '--client' in sys.argv:
        run_client_demo()
    else:
        main()