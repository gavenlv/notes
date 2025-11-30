#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP缓存最佳实践
展示正确的缓存配置和使用模式
"""

from flask import Flask, request, make_response, jsonify, abort
import json
import hashlib
from datetime import datetime, timedelta, timezone
from functools import wraps
import time


app = Flask(__name__)

# 模拟不同类型的数据
STATIC_RESOURCES = {
    'logo.png': {
        'content': 'PNG image data...',
        'mime_type': 'image/png',
        'size': 10240
    },
    'styles.css': {
        'content': 'body { margin: 0; padding: 0; }',
        'mime_type': 'text/css',
        'size': 2048
    },
    'app.js': {
        'content': 'console.log("App loaded");',
        'mime_type': 'application/javascript',
        'size': 4096
    }
}

DYNAMIC_RESOURCES = {
    'user_profile': {
        'personal_info': {
            'name': '张三',
            'email': 'zhangsan@example.com'
        },
        'preferences': {
            'theme': 'dark',
            'language': 'zh-CN'
        }
    },
    'dashboard_data': {
        'metrics': {
            'visitors': 1250,
            'page_views': 5420,
            'conversion_rate': 3.2
        },
        'charts': {
            'daily_visits': [120, 135, 142, 128, 156, 168, 172],
            'sources': {
                'direct': 45,
                'social': 25,
                'search': 30
            }
        }
    }
}

# 用户会话数据（模拟）
USER_SESSIONS = {
    'session_abc123': {
        'user_id': 'user1',
        'login_time': datetime.now(timezone.utc) - timedelta(minutes=30),
        'last_activity': datetime.now(timezone.utc)
    }
}


class CacheBestPractices:
    """缓存最佳实践工具类"""
    
    @staticmethod
    def generate_etag(content: str) -> str:
        """
        生成强ETag
        
        Args:
            content (str): 内容字符串
            
        Returns:
            str: ETag值
        """
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def generate_weak_etag(content: str) -> str:
        """
        生成弱ETag（适用于可能变化但语义相同的资源）
        
        Args:
            content (str): 内容字符串
            
        Returns:
            str: 弱ETag值
        """
        return f"W/{hashlib.md5(content.encode()).hexdigest()}"
    
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


def cache_control(max_age=None, s_maxage=None, public=False, private=False, 
                  no_cache=False, no_store=False, must_revalidate=False,
                  immutable=False):
    """
    缓存控制装饰器
    
    Args:
        max_age (int): 最大缓存时间（秒）
        s_maxage (int): 共享缓存最大时间（秒）
        public (bool): 是否允许共享缓存
        private (bool): 是否仅限私有缓存
        no_cache (bool): 是否禁止缓存
        no_store (bool): 是否禁止存储
        must_revalidate (bool): 是否必须重新验证
        immutable (bool): 是否不可变
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 执行原始函数
            response = f(*args, **kwargs)
            
            # 构建Cache-Control头部
            cache_directives = []
            
            if no_store:
                cache_directives.append('no-store')
            elif no_cache:
                cache_directives.append('no-cache')
            else:
                if public:
                    cache_directives.append('public')
                if private:
                    cache_directives.append('private')
                if max_age is not None:
                    cache_directives.append(f'max-age={max_age}')
                if s_maxage is not None:
                    cache_directives.append(f's-maxage={s_maxage}')
                if must_revalidate:
                    cache_directives.append('must-revalidate')
                if immutable:
                    cache_directives.append('immutable')
            
            if cache_directives:
                if hasattr(response, 'headers'):
                    response.headers['Cache-Control'] = ', '.join(cache_directives)
            
            return response
        return decorated_function
    return decorator


def conditional_response(f):
    """
    条件响应装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 执行原始函数获取资源
        result = f(*args, **kwargs)
        
        if isinstance(result, tuple):
            data, last_modified = result
        else:
            data = result
            last_modified = datetime.now(timezone.utc)
        
        # 生成ETag
        content_str = json.dumps(data, sort_keys=True)
        etag = f'"{CacheBestPractices.generate_etag(content_str)}"'
        
        # 检查条件请求头部
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match and if_none_match == etag:
            # ETag匹配，返回304
            response = make_response('', 304)
            response.headers['ETag'] = etag
            response.headers['Last-Modified'] = CacheBestPractices.format_http_date(last_modified)
            return response
        
        if_modified_since = request.headers.get('If-Modified-Since')
        if if_modified_since:
            try:
                if_modified_dt = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=timezone.utc)
                if last_modified <= if_modified_dt:
                    # 资源未修改，返回304
                    response = make_response('', 304)
                    response.headers['ETag'] = etag
                    response.headers['Last-Modified'] = CacheBestPractices.format_http_date(last_modified)
                    return response
            except ValueError:
                pass
        
        # 返回完整响应
        if not isinstance(data, str):
            response = jsonify(data)
        else:
            response = make_response(data)
        
        response.headers['ETag'] = etag
        response.headers['Last-Modified'] = CacheBestPractices.format_http_date(last_modified)
        
        return response
    
    return decorated_function


@app.route('/')
def home():
    """首页"""
    html = '''
    <h1>HTTP缓存最佳实践演示</h1>
    <p>本演示展示了各种缓存策略的最佳实践:</p>
    <ul>
        <li>静态资源缓存</li>
        <li>动态数据缓存</li>
        <li>用户特定内容缓存</li>
        <li>条件请求</li>
        <li>缓存验证</li>
    </ul>
    <h2>可用端点:</h2>
    <h3>静态资源 (长期缓存)</h3>
    <ul>
        <li><a href="/static/logo.png">/static/logo.png</a></li>
        <li><a href="/static/styles.css">/static/styles.css</a></li>
        <li><a href="/static/app.js">/static/app.js</a></li>
    </ul>
    <h3>动态数据 (短期缓存)</h3>
    <ul>
        <li><a href="/api/dashboard">/api/dashboard</a> - 仪表板数据</li>
        <li><a href="/api/user/profile">/api/user/profile</a> - 用户资料</li>
    </ul>
    <h3>用户特定内容 (私有缓存)</h3>
    <ul>
        <li><a href="/api/user/preferences">/api/user/preferences</a> - 用户偏好</li>
    </ul>
    <h3>条件请求测试</h3>
    <ul>
        <li><a href="/api/conditional-test">/api/conditional-test</a></li>
    </ul>
    '''
    return html


@app.route('/static/<filename>')
@conditional_response
@cache_control(max_age=31536000, immutable=True)  # 1年缓存，不可变
def static_resource(filename):
    """静态资源（长期缓存）"""
    if filename not in STATIC_RESOURCES:
        abort(404)
    
    resource = STATIC_RESOURCES[filename]
    
    # 设置内容类型
    response = make_response(resource['content'])
    response.headers['Content-Type'] = resource['mime_type']
    
    # 静态资源通常很少改变，可以设置较长的缓存时间
    last_modified = datetime.now(timezone.utc) - timedelta(days=30)  # 假设30天前最后修改
    
    return response, last_modified


@app.route('/api/dashboard')
@conditional_response
@cache_control(max_age=300, s_maxage=600)  # 公共缓存5分钟，共享缓存10分钟
def dashboard_data():
    """仪表板数据（中等缓存时间）"""
    # 模拟数据更新
    data = DYNAMIC_RESOURCES['dashboard_data'].copy()
    data['timestamp'] = datetime.now().isoformat()
    data['cache_info'] = {
        'max_age': 300,
        'description': '此数据每5分钟更新一次'
    }
    
    last_modified = datetime.now(timezone.utc)
    
    return data, last_modified


@app.route('/api/user/profile')
@conditional_response
@cache_control(private=True, max_age=60)  # 私有缓存1分钟
def user_profile():
    """用户资料（短时间私有缓存）"""
    # 检查用户认证（简化版）
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 模拟用户数据
    data = DYNAMIC_RESOURCES['user_profile'].copy()
    data['timestamp'] = datetime.now().isoformat()
    data['cache_info'] = {
        'max_age': 60,
        'scope': 'private',
        'description': '此数据包含用户个人信息，仅用户本人可见'
    }
    
    last_modified = datetime.now(timezone.utc)
    
    return data, last_modified


@app.route('/api/user/preferences')
@conditional_response
@cache_control(private=True, max_age=300, must_revalidate=True)  # 私有缓存5分钟，必须重新验证
def user_preferences():
    """用户偏好设置（私有缓存，必须重新验证）"""
    # 检查用户认证
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 模拟用户偏好数据
    data = DYNAMIC_RESOURCES['user_profile']['preferences'].copy()
    data['timestamp'] = datetime.now().isoformat()
    data['cache_info'] = {
        'max_age': 300,
        'must_revalidate': True,
        'description': '用户偏好设置，更改后需要立即生效'
    }
    
    last_modified = datetime.now(timezone.utc)
    
    return data, last_modified


@app.route('/api/conditional-test')
@conditional_response
@cache_control(max_age=60)  # 1分钟缓存
def conditional_test():
    """条件请求测试端点"""
    # 模拟经常变化的数据
    data = {
        'message': '这是一个用于测试条件请求的端点',
        'timestamp': datetime.now().isoformat(),
        'counter': int(time.time()) % 1000,  # 模拟变化的数据
        'testing_info': {
            'purpose': '演示条件请求（If-None-Match, If-Modified-Since）',
            'instructions': '首次请求后，使用返回的ETag或Last-Modified进行条件请求'
        }
    }
    
    last_modified = datetime.now(timezone.utc)
    
    return data, last_modified


@app.route('/api/no-cache')
@cache_control(no_cache=True)  # 禁止缓存
def no_cache_endpoint():
    """禁用缓存的端点"""
    return jsonify({
        'message': '此端点禁用了缓存',
        'timestamp': datetime.now().isoformat(),
        'cache_policy': 'no-cache',
        'description': '每次请求都会重新验证'
    })


@app.route('/api/sensitive-data')
@cache_control(no_store=True)  # 禁止存储
def sensitive_data():
    """敏感数据（禁止缓存存储）"""
    return jsonify({
        'message': '敏感数据，禁止缓存存储',
        'data': '保密信息',
        'timestamp': datetime.now().isoformat(),
        'cache_policy': 'no-store',
        'description': '此数据不会被任何缓存存储'
    })


def demonstrate_cache_best_practices():
    """演示缓存最佳实践"""
    print("HTTP缓存最佳实践演示")
    print("=" * 30)
    
    print("缓存策略分类:")
    print("1. 静态资源: max-age=31536000, immutable (长期缓存)")
    print("2. 动态数据: max-age=300 (5分钟缓存)")
    print("3. 用户数据: private, max-age=60 (私有缓存1分钟)")
    print("4. 敏感数据: no-store (禁止缓存)")
    print("5. 实时数据: no-cache (每次都验证)")
    
    print("\n缓存头部说明:")
    print("- Cache-Control: 控制缓存行为的主要头部")
    print("- ETag: 资源的唯一标识符，用于验证")
    print("- Last-Modified: 资源最后修改时间")
    print("- Expires: 缓存过期时间（HTTP/1.0兼容）")
    
    print("\n最佳实践要点:")
    print("1. 为静态资源设置长期缓存")
    print("2. 为动态数据设置适当缓存时间")
    print("3. 用户特定内容使用私有缓存")
    print("4. 敏感数据禁用缓存")
    print("5. 使用ETag和条件请求优化性能")
    print("6. 正确设置Vary头部处理内容协商")
    
    print("\n测试方法:")
    print("curl -I http://localhost:5000/static/logo.png  # 查看缓存头部")
    print("curl -H 'If-None-Match: ETAG_VALUE' http://localhost:5000/api/conditional-test  # 条件请求")


if __name__ == '__main__':
    print("启动HTTP缓存最佳实践演示服务器...")
    print("访问 http://localhost:5000 查看演示")
    
    demonstrate_cache_best_practices()
    
    app.run(debug=True, port=5000)