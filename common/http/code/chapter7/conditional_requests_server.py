#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
条件请求服务器
实现基于Last-Modified和ETag的条件请求处理
"""

from flask import Flask, request, make_response, jsonify, abort
import hashlib
import time
from datetime import datetime, timezone
from functools import wraps
import json


app = Flask(__name__)

# 模拟资源存储
resources = {
    'article1': {
        'title': 'HTTP缓存机制详解',
        'content': '这是关于HTTP缓存机制的详细文章内容...',
        'author': '张三',
        'last_modified': datetime.now(timezone.utc)
    },
    'article2': {
        'title': 'Web性能优化指南',
        'content': '这是关于Web性能优化的实用指南...',
        'author': '李四',
        'last_modified': datetime.now(timezone.utc)
    }
}

# 模拟用户数据
users = {
    'user1': {
        'name': 'Alice',
        'email': 'alice@example.com',
        'last_login': datetime.now(timezone.utc)
    },
    'user2': {
        'name': 'Bob',
        'email': 'bob@example.com',
        'last_login': datetime.now(timezone.utc)
    }
}


class ConditionalRequestHandler:
    """条件请求处理器"""
    
    @staticmethod
    def generate_etag(content: str) -> str:
        """
        生成ETag
        
        Args:
            content (str): 内容字符串
            
        Returns:
            str: ETag值
        """
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def format_http_date(dt: datetime) -> str:
        """
        格式化HTTP日期
        
        Args:
            dt (datetime): 日期时间对象
            
        Returns:
            str: HTTP格式的日期字符串
        """
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    @staticmethod
    def parse_http_date(date_str: str) -> datetime:
        """
        解析HTTP日期
        
        Args:
            date_str (str): HTTP日期字符串
            
        Returns:
            datetime: 日期时间对象
        """
        try:
            return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)


def conditional_response(f):
    """
    条件响应装饰器
    处理If-Modified-Since和If-None-Match头部
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 执行原始函数获取资源
        resource_data = f(*args, **kwargs)
        
        if isinstance(resource_data, tuple):
            data, last_modified = resource_data
        else:
            data = resource_data
            last_modified = datetime.now(timezone.utc)
        
        # 生成ETag
        content_str = json.dumps(data, sort_keys=True)
        etag = f'"{ConditionalRequestHandler.generate_etag(content_str)}"'
        
        # 检查If-None-Match头部
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match and if_none_match == etag:
            # ETag匹配，返回304
            response = make_response('', 304)
            response.headers['ETag'] = etag
            response.headers['Last-Modified'] = ConditionalRequestHandler.format_http_date(last_modified)
            return response
        
        # 检查If-Modified-Since头部
        if_modified_since = request.headers.get('If-Modified-Since')
        if if_modified_since:
            if_modified_dt = ConditionalRequestHandler.parse_http_date(if_modified_since)
            if last_modified <= if_modified_dt:
                # 资源未修改，返回304
                response = make_response('', 304)
                response.headers['ETag'] = etag
                response.headers['Last-Modified'] = ConditionalRequestHandler.format_http_date(last_modified)
                return response
        
        # 返回完整响应
        response = jsonify(data)
        response.headers['ETag'] = etag
        response.headers['Last-Modified'] = ConditionalRequestHandler.format_http_date(last_modified)
        
        return response
    
    return decorated_function


@app.route('/')
def home():
    """首页"""
    html = '''
    <h1>条件请求服务器演示</h1>
    <p>可用的API端点:</p>
    <ul>
        <li><a href="/articles">文章列表</a></li>
        <li><a href="/articles/article1">文章1详情</a></li>
        <li><a href="/articles/article2">文章2详情</a></li>
        <li><a href="/users">用户列表</a></li>
        <li><a href="/users/user1">用户1详情</a></li>
        <li><a href="/users/user2">用户2详情</a></li>
    </ul>
    <p>使用curl或浏览器开发者工具测试条件请求:</p>
    <pre>
# 首次请求获取资源和ETag
curl -i http://localhost:5000/articles/article1

# 使用ETag进行条件请求
curl -i -H "If-None-Match: \\"ETAG_VALUE\\"" http://localhost:5000/articles/article1

# 使用Last-Modified进行条件请求
curl -i -H "If-Modified-Since: LAST_MODIFIED_DATE" http://localhost:5000/articles/article1
    </pre>
    '''
    return html


@app.route('/articles')
@conditional_response
def get_articles():
    """获取文章列表"""
    articles_list = []
    latest_modified = datetime.min.replace(tzinfo=timezone.utc)
    
    for article_id, article in resources.items():
        articles_list.append({
            'id': article_id,
            'title': article['title'],
            'author': article['author']
        })
        if article['last_modified'] > latest_modified:
            latest_modified = article['last_modified']
    
    return {
        'articles': articles_list,
        'total': len(articles_list)
    }, latest_modified


@app.route('/articles/<article_id>')
@conditional_response
def get_article(article_id):
    """获取文章详情"""
    if article_id not in resources:
        abort(404)
    
    article = resources[article_id]
    return {
        'id': article_id,
        'title': article['title'],
        'content': article['content'],
        'author': article['author'],
        'last_modified': article['last_modified'].isoformat()
    }, article['last_modified']


@app.route('/users')
@conditional_response
def get_users():
    """获取用户列表"""
    users_list = []
    latest_login = datetime.min.replace(tzinfo=timezone.utc)
    
    for user_id, user in users.items():
        users_list.append({
            'id': user_id,
            'name': user['name'],
            'email': user['email']
        })
        if user['last_login'] > latest_login:
            latest_login = user['last_login']
    
    return {
        'users': users_list,
        'total': len(users_list)
    }, latest_login


@app.route('/users/<user_id>')
@conditional_response
def get_user(user_id):
    """获取用户详情"""
    if user_id not in users:
        abort(404)
    
    user = users[user_id]
    return {
        'id': user_id,
        'name': user['name'],
        'email': user['email'],
        'last_login': user['last_login'].isoformat()
    }, user['last_login']


@app.route('/update-article/<article_id>', methods=['POST'])
def update_article(article_id):
    """更新文章（用于测试条件请求）"""
    if article_id not in resources:
        abort(404)
    
    # 更新文章的最后修改时间
    resources[article_id]['last_modified'] = datetime.now(timezone.utc)
    
    return jsonify({
        'message': f'文章 {article_id} 已更新',
        'new_last_modified': resources[article_id]['last_modified'].isoformat()
    })


@app.route('/advanced-conditional')
@conditional_response
def advanced_conditional():
    """高级条件请求示例"""
    # 模拟复杂资源
    complex_resource = {
        'metadata': {
            'version': '2.1.0',
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'schema': 'resource-v2'
        },
        'data': {
            'items': [
                {'id': 1, 'name': 'Item 1', 'value': 100},
                {'id': 2, 'name': 'Item 2', 'value': 200},
                {'id': 3, 'name': 'Item 3', 'value': 300}
            ],
            'statistics': {
                'count': 3,
                'sum': 600,
                'average': 200.0
            }
        },
        'links': {
            'self': '/advanced-conditional',
            'related': '/related-resources'
        }
    }
    
    last_modified = datetime.now(timezone.utc)
    
    return complex_resource, last_modified


def demonstrate_conditional_requests():
    """演示条件请求的使用"""
    print("条件请求服务器演示")
    print("=" * 30)
    
    print("条件请求工作原理:")
    print("1. 服务器在响应中包含ETag和Last-Modified头部")
    print("2. 客户端在后续请求中发送If-None-Match或If-Modified-Since头部")
    print("3. 服务器比较这些值决定是否返回完整响应或304状态码")
    
    print("\n测试命令示例:")
    print("# 首次请求")
    print("curl -i http://localhost:5000/articles/article1")
    print()
    print("# 使用ETag进行条件请求")
    print("curl -i -H 'If-None-Match: \"ETAG_VALUE\"' http://localhost:5000/articles/article1")
    print()
    print("# 使用Last-Modified进行条件请求")
    print("curl -i -H 'If-Modified-Since: Wed, 21 Oct 2023 07:28:00 GMT' http://localhost:5000/articles/article1")
    
    print("\n条件请求优势:")
    print("- 减少带宽使用")
    print("- 降低服务器负载")
    print("- 提高响应速度")
    print("- 保持数据一致性")


if __name__ == '__main__':
    print("启动条件请求服务器...")
    print("访问 http://localhost:5000 查看演示")
    print("\n条件请求说明:")
    print("- ETag: 基于资源内容的唯一标识符")
    print("- Last-Modified: 资源最后修改时间")
    print("- 304 Not Modified: 资源未修改，使用缓存")
    
    app.run(debug=True, port=5000)