#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存控制演示器
演示HTTP缓存控制的各种策略和效果
"""

from flask import Flask, request, make_response, jsonify
import hashlib
import time
from datetime import datetime, timedelta
import json


app = Flask(__name__)


class CacheControlDemonstrator:
    """缓存控制演示器类"""
    
    @staticmethod
    def set_cache_control(response, strategy: str, max_age: int = 3600):
        """
        设置缓存控制策略
        
        Args:
            response: Flask响应对象
            strategy (str): 缓存策略 ('public', 'private', 'no-cache', 'no-store')
            max_age (int): 最大缓存时间（秒）
        """
        if strategy == 'public':
            # 公共缓存：可以被任何缓存存储
            response.headers['Cache-Control'] = f'public, max-age={max_age}'
        elif strategy == 'private':
            # 私有缓存：只能被单个用户缓存
            response.headers['Cache-Control'] = f'private, max-age={max_age}'
        elif strategy == 'no-cache':
            # 无缓存：每次都需要验证
            response.headers['Cache-Control'] = 'no-cache'
        elif strategy == 'no-store':
            # 不存储：禁止缓存存储任何信息
            response.headers['Cache-Control'] = 'no-store'
        elif strategy == 'must-revalidate':
            # 必须重新验证：过期后必须向服务器验证
            response.headers['Cache-Control'] = f'must-revalidate, max-age={max_age}'
        
        return response


@app.route('/')
def home():
    """首页"""
    html = '''
    <h1>HTTP缓存控制演示器</h1>
    <p>请选择要测试的缓存策略:</p>
    <ul>
        <li><a href="/public">公共缓存 (Public)</a></li>
        <li><a href="/private">私有缓存 (Private)</a></li>
        <li><a href="/no-cache">无缓存 (No-Cache)</a></li>
        <li><a href="/no-store">不存储 (No-Store)</a></li>
        <li><a href="/must-revalidate">必须重新验证 (Must-Revalidate)</a></li>
        <li><a href="/vary-example">Vary头部示例</a></li>
        <li><a href="/expires-example">Expires头部示例</a></li>
    </ul>
    <p>使用浏览器开发者工具的Network面板观察响应头部</p>
    '''
    return html


@app.route('/public')
def public_cache():
    """公共缓存示例"""
    response = make_response(jsonify({
        'message': '这是公共缓存示例',
        'timestamp': datetime.now().isoformat(),
        'strategy': 'public',
        'data': '此响应可以被任何缓存存储，包括代理服务器和CDN'
    }))
    
    # 设置公共缓存，有效期1小时
    response = CacheControlDemonstrator.set_cache_control(response, 'public', 3600)
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'Public Cache Example'
    
    return response


@app.route('/private')
def private_cache():
    """私有缓存示例"""
    response = make_response(jsonify({
        'message': '这是私有缓存示例',
        'timestamp': datetime.now().isoformat(),
        'strategy': 'private',
        'user_specific_data': f'用户特定数据: {request.remote_addr}'
    }))
    
    # 设置私有缓存，有效期30分钟
    response = CacheControlDemonstrator.set_cache_control(response, 'private', 1800)
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'Private Cache Example'
    
    return response


@app.route('/no-cache')
def no_cache():
    """无缓存示例"""
    response = make_response(jsonify({
        'message': '这是无缓存示例',
        'timestamp': datetime.now().isoformat(),
        'strategy': 'no-cache',
        'data': '每次请求都需要向服务器验证缓存是否仍然有效'
    }))
    
    # 设置无缓存
    response = CacheControlDemonstrator.set_cache_control(response, 'no-cache')
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'No-Cache Example'
    
    return response


@app.route('/no-store')
def no_store():
    """不存储示例"""
    response = make_response(jsonify({
        'message': '这是不存储示例',
        'timestamp': datetime.now().isoformat(),
        'strategy': 'no-store',
        'sensitive_data': '敏感信息，不应被缓存存储'
    }))
    
    # 设置不存储
    response = CacheControlDemonstrator.set_cache_control(response, 'no-store')
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'No-Store Example'
    
    return response


@app.route('/must-revalidate')
def must_revalidate():
    """必须重新验证示例"""
    response = make_response(jsonify({
        'message': '这是必须重新验证示例',
        'timestamp': datetime.now().isoformat(),
        'strategy': 'must-revalidate',
        'data': '缓存过期后必须向服务器验证才能使用'
    }))
    
    # 设置必须重新验证，有效期10秒（便于测试）
    response = CacheControlDemonstrator.set_cache_control(response, 'must-revalidate', 10)
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'Must-Revalidate Example'
    
    return response


@app.route('/vary-example')
def vary_example():
    """Vary头部示例"""
    user_agent = request.headers.get('User-Agent', 'Unknown')
    accept_encoding = request.headers.get('Accept-Encoding', 'identity')
    
    # 根据User-Agent和Accept-Encoding生成不同的内容
    content_type = 'desktop' if 'Mobile' not in user_agent else 'mobile'
    encoding_type = 'compressed' if 'gzip' in accept_encoding else 'uncompressed'
    
    response = make_response(jsonify({
        'message': '这是Vary头部示例',
        'timestamp': datetime.now().isoformat(),
        'user_agent_type': content_type,
        'encoding_type': encoding_type,
        'data': f'根据User-Agent({content_type})和Accept-Encoding({encoding_type})生成的内容'
    }))
    
    # 设置缓存控制
    response = CacheControlDemonstrator.set_cache_control(response, 'public', 300)
    
    # 设置Vary头部，告诉缓存根据这些头部的不同值存储不同版本
    response.headers['Vary'] = 'User-Agent, Accept-Encoding'
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'Vary Header Example'
    
    return response


@app.route('/expires-example')
def expires_example():
    """Expires头部示例"""
    response = make_response(jsonify({
        'message': '这是Expires头部示例',
        'timestamp': datetime.now().isoformat(),
        'strategy': 'expires',
        'data': '使用Expires头部指定绝对过期时间'
    }))
    
    # 设置Expires头部（HTTP/1.0方式）
    expires_time = datetime.now() + timedelta(minutes=10)
    response.headers['Expires'] = expires_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 同时设置Cache-Control（HTTP/1.1方式，优先级更高）
    response = CacheControlDemonstrator.set_cache_control(response, 'public', 600)
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'Expires Header Example'
    
    return response


@app.route('/advanced-cache-control')
def advanced_cache_control():
    """高级缓存控制示例"""
    response = make_response(jsonify({
        'message': '这是高级缓存控制示例',
        'timestamp': datetime.now().isoformat(),
        'strategy': 'advanced',
        'data': '演示复杂的缓存控制指令组合'
    }))
    
    # 设置复杂的缓存控制
    cache_control = [
        'public',           # 可以被公共缓存存储
        'max-age=3600',     # 客户端缓存1小时
        's-maxage=1800',    # 共享缓存（如CDN）缓存30分钟
        'must-revalidate',  # 过期后必须重新验证
        'proxy-revalidate'  # 共享缓存过期后必须重新验证
    ]
    
    response.headers['Cache-Control'] = ', '.join(cache_control)
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'Advanced Cache Control Example'
    
    return response


@app.route('/cache-busting')
def cache_busting():
    """缓存破坏示例"""
    # 生成基于内容的ETag
    content = {
        'message': '这是缓存破坏示例',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }
    
    # 使用内容生成ETag
    content_str = json.dumps(content, sort_keys=True)
    etag = hashlib.md5(content_str.encode()).hexdigest()
    
    response = make_response(jsonify(content))
    
    # 设置ETag和缓存控制
    response.headers['ETag'] = f'"{etag}"'
    response = CacheControlDemonstrator.set_cache_control(response, 'public', 86400)  # 缓存1天
    
    # 添加额外信息便于观察
    response.headers['X-Demo-Info'] = 'Cache Busting Example'
    
    return response


def demonstrate_cache_control_strategies():
    """演示不同的缓存控制策略"""
    print("HTTP缓存控制策略演示")
    print("=" * 40)
    
    strategies = [
        ('public', '公共缓存'),
        ('private', '私有缓存'),
        ('no-cache', '无缓存'),
        ('no-store', '不存储'),
        ('must-revalidate', '必须重新验证')
    ]
    
    print("可用的缓存控制策略:")
    for strategy, description in strategies:
        print(f"  {strategy}: {description}")
    
    print("\n运行说明:")
    print("1. 启动服务器: python cache_control_demonstrator.py")
    print("2. 访问 http://localhost:5000 查看演示")
    print("3. 使用浏览器开发者工具观察不同策略下的响应头部")
    print("4. 刷新页面观察缓存行为差异")
    
    print("\n缓存控制最佳实践:")
    print("1. 静态资源使用public和长max-age")
    print("2. 用户特定内容使用private")
    print("3. 敏感信息使用no-store")
    print("4. 重要数据使用must-revalidate")
    print("5. 根据内容变化使用缓存破坏技术")


if __name__ == '__main__':
    print("启动HTTP缓存控制演示器...")
    print("访问 http://localhost:5000 查看演示")
    print("\n缓存控制策略说明:")
    print("- Public: 可以被任何缓存存储")
    print("- Private: 只能被单个用户缓存")
    print("- No-Cache: 每次使用前需要验证")
    print("- No-Store: 禁止缓存存储")
    print("- Must-Revalidate: 过期后必须验证")
    
    app.run(debug=True, port=5000)