#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP基本认证服务器示例
演示HTTP基本认证机制的实现
"""

from flask import Flask, request, jsonify, make_response
import base64
from functools import wraps


app = Flask(__name__)

# 模拟用户数据库（实际应用中应使用安全的密码存储）
USERS = {
    'admin': 'admin123',
    'user1': 'password1',
    'user2': 'password2'
}


class BasicAuth:
    """基本认证工具类"""
    
    @staticmethod
    def authenticate(username, password):
        """
        验证用户凭证
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 验证是否成功
        """
        if username in USERS:
            return USERS[username] == password
        return False
    
    @staticmethod
    def decode_credentials(auth_header):
        """
        解码Authorization头部中的凭证
        
        Args:
            auth_header (str): Authorization头部值
            
        Returns:
            tuple: (username, password) 或 (None, None)
        """
        if not auth_header or not auth_header.startswith('Basic '):
            return None, None
        
        try:
            # 解码Base64编码的凭证
            encoded_credentials = auth_header.split(' ', 1)[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            
            # 分离用户名和密码
            username, password = decoded_credentials.split(':', 1)
            return username, password
        except Exception:
            return None, None


def require_basic_auth(f):
    """
    基本认证装饰器
    
    Args:
        f (function): 被装饰的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Authorization头部
        auth_header = request.headers.get('Authorization')
        
        # 解码凭证
        username, password = BasicAuth.decode_credentials(auth_header)
        
        # 验证凭证
        if not username or not password or not BasicAuth.authenticate(username, password):
            # 认证失败，返回401状态码和WWW-Authenticate头部
            response = make_response(jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid credentials'
            }), 401)
            response.headers['WWW-Authenticate'] = 'Basic realm="Access to the staging site"'
            return response
        
        # 认证成功，将用户信息添加到请求上下文
        request.current_user = username
        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/')
def home():
    """首页"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>HTTP基本认证演示</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>HTTP基本认证服务器演示</h1>
        <p>这是一个演示HTTP基本认证机制的服务器。</p>
        
        <h2>可用端点:</h2>
        <ul>
            <li><a href="/public">/public</a> - 公共资源（无需认证）</li>
            <li><a href="/protected">/protected</a> - 受保护资源（需要基本认证）</li>
            <li><a href="/admin">/admin</a> - 管理员资源（需要admin用户）</li>
        </ul>
        
        <h2>测试方法:</h2>
        <p>使用curl命令测试:</p>
        <pre>
# 访问公共资源
curl http://localhost:5000/public

# 访问受保护资源（使用user1:password1）
curl -u user1:password1 http://localhost:5000/protected

# 访问管理员资源（使用admin:admin123）
curl -u admin:admin123 http://localhost:5000/admin
        </pre>
        
        <h2>用户账户:</h2>
        <ul>
            <li>admin: admin123</li>
            <li>user1: password1</li>
            <li>user2: password2</li>
        </ul>
    </body>
    </html>
    '''
    return html


@app.route('/public')
def public_resource():
    """公共资源（无需认证）"""
    return jsonify({
        'message': '这是公共资源，无需认证即可访问',
        'resource': 'public_data',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


@app.route('/protected')
@require_basic_auth
def protected_resource():
    """受保护资源（需要基本认证）"""
    current_user = getattr(request, 'current_user', 'Unknown')
    
    return jsonify({
        'message': f'认证成功！欢迎用户 {current_user}',
        'resource': 'protected_data',
        'user': current_user,
        'access_level': 'user',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


@app.route('/admin')
@require_basic_auth
def admin_resource():
    """管理员资源（需要admin用户）"""
    current_user = getattr(request, 'current_user', 'Unknown')
    
    # 检查是否为管理员用户
    if current_user != 'admin':
        return jsonify({
            'error': 'Forbidden',
            'message': '需要管理员权限才能访问此资源'
        }), 403
    
    return jsonify({
        'message': f'管理员 {current_user} 访问成功',
        'resource': 'admin_data',
        'user': current_user,
        'access_level': 'admin',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


def demonstrate_basic_auth():
    """演示基本认证的使用"""
    print("HTTP基本认证演示")
    print("=" * 30)
    
    print("基本认证工作原理:")
    print("1. 客户端请求受保护资源")
    print("2. 服务器返回401状态码和WWW-Authenticate头部")
    print("3. 客户端将用户名和密码组合后Base64编码")
    print("4. 客户端在Authorization头部发送编码后的凭证")
    print("5. 服务器解码并验证凭证")
    print("6. 验证成功则返回请求的资源")
    
    print("\n安全注意事项:")
    print("- 基本认证凭证以明文形式传输（Base64不是加密）")
    print("- 必须配合HTTPS使用")
    print("- 不应在高安全要求的场景中使用")
    print("- 应该定期更换密码")
    
    print("\n测试命令:")
    print("# 访问公共资源")
    print("curl http://localhost:5000/public")
    print()
    print("# 访问受保护资源")
    print("curl -u user1:password1 http://localhost:5000/protected")
    print()
    print("# 访问管理员资源")
    print("curl -u admin:admin123 http://localhost:5000/admin")


if __name__ == '__main__':
    print("启动HTTP基本认证服务器...")
    print("访问 http://localhost:5000 查看演示")
    
    demonstrate_basic_auth()
    
    app.run(debug=True, port=5000)