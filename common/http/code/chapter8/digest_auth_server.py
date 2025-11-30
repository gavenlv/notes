#!/usr/bin/env python3
"""
HTTP 摘要认证服务器示例

这个模块演示了如何在 Flask 应用中实现 HTTP 摘要认证机制。
它包括摘要认证的核心逻辑、挑战-响应机制以及用户凭证验证。

主要组件：
1. DigestAuth 类：处理摘要认证的核心逻辑
2. require_digest_auth 装饰器：用于保护需要认证的路由
3. 各种示例端点：展示不同的认证场景

学习目标：
- 理解摘要认证的工作原理
- 掌握摘要认证的安全优势
- 实践摘要认证在 Web 应用中的实现
"""

import hashlib
import uuid
import time
from functools import wraps
from flask import Flask, request, jsonify, Response

# 初始化 Flask 应用
app = Flask(__name__)

# 模拟用户数据库 (实际应用中应该使用更安全的存储方式)
USERS_DB = {
    "admin": {
        "password": "admin123",
        "realm": "Protected Area"
    },
    "user": {
        "password": "user123",
        "realm": "User Area"
    }
}

class DigestAuth:
    """处理 HTTP 摘要认证的核心逻辑"""
    
    def __init__(self, realm="Protected Area"):
        """
        初始化摘要认证处理器
        
        Args:
            realm (str): 认证领域名称
        """
        self.realm = realm
        self.nonce_dict = {}  # 存储 nonce 和相关信息
    
    def generate_nonce(self):
        """
        生成随机的 nonce 值
        
        Returns:
            str: Base64 编码的 nonce 字符串
        """
        return hashlib.md5(uuid.uuid4().bytes).hexdigest()
    
    def generate_opaque(self):
        """
        生成 opaque 值
        
        Returns:
            str: opaque 字符串
        """
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    
    def create_digest_challenge(self):
        """
        创建摘要认证挑战
        
        Returns:
            str: WWW-Authenticate 头部值
        """
        nonce = self.generate_nonce()
        opaque = self.generate_opaque()
        
        # 存储 nonce 信息用于后续验证
        self.nonce_dict[nonce] = {
            "created_time": time.time(),
            "opaque": opaque
        }
        
        challenge = f'Digest realm="{self.realm}", nonce="{nonce}", opaque="{opaque}", algorithm=MD5, qop="auth"'
        return challenge
    
    def validate_credentials(self, username, realm, nonce, uri, response, cnonce, nc, qop):
        """
        验证用户提供的摘要认证凭据
        
        Args:
            username (str): 用户名
            realm (str): 认证领域
            nonce (str): 服务器生成的随机值
            uri (str): 请求 URI
            response (str): 客户端计算的响应值
            cnonce (str): 客户端生成的随机值
            nc (str): 请求计数器
            qop (str): 保护质量
            
        Returns:
            bool: 凭据是否有效
        """
        # 检查用户是否存在
        if username not in USERS_DB:
            return False
        
        user_info = USERS_DB[username]
        if user_info.get("realm") != realm:
            return False
        
        # 检查 nonce 是否有效
        if nonce not in self.nonce_dict:
            return False
        
        # 检查 nonce 是否过期 (这里设置为 5 分钟)
        nonce_info = self.nonce_dict[nonce]
        if time.time() - nonce_info["created_time"] > 300:
            del self.nonce_dict[nonce]
            return False
        
        # 获取用户密码
        password = user_info["password"]
        
        # 计算 HA1 (A1 = username:realm:password)
        ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
        
        # 计算 HA2 (A2 = method:digestURI)
        ha2 = hashlib.md5(f"GET:{uri}".encode()).hexdigest()
        
        # 计算预期的响应值
        expected_response = hashlib.md5(
            f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()
        ).hexdigest()
        
        # 比较客户端响应和预期响应
        return response == expected_response

# 创建摘要认证实例
digest_auth = DigestAuth()

def require_digest_auth(f):
    """
    装饰器：要求 HTTP 摘要认证
    
    Args:
        f (function): 被装饰的视图函数
        
    Returns:
        function: 包装后的视图函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查 Authorization 头部
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            # 返回 401 未授权状态码和摘要认证挑战
            challenge = digest_auth.create_digest_challenge()
            return Response(
                'Authentication required', 
                401, 
                {'WWW-Authenticate': challenge}
            )
        
        # 解析摘要认证头部
        if not auth_header.startswith('Digest '):
            return Response('Invalid authorization header', 400)
        
        # 提取认证参数
        auth_params = {}
        for param in auth_header[7:].split(','):
            key, value = param.strip().split('=', 1)
            auth_params[key] = value.strip('"')
        
        # 验证必需的参数
        required_params = ['username', 'realm', 'nonce', 'uri', 'response']
        if not all(param in auth_params for param in required_params):
            return Response('Missing authentication parameters', 400)
        
        # 验证凭据
        is_valid = digest_auth.validate_credentials(
            username=auth_params['username'],
            realm=auth_params['realm'],
            nonce=auth_params['nonce'],
            uri=auth_params['uri'],
            response=auth_params['response'],
            cnonce=auth_params.get('cnonce', ''),
            nc=auth_params.get('nc', ''),
            qop=auth_params.get('qop', '')
        )
        
        if not is_valid:
            # 认证失败，返回新的挑战
            challenge = digest_auth.create_digest_challenge()
            return Response(
                'Invalid credentials', 
                401, 
                {'WWW-Authenticate': challenge}
            )
        
        # 认证成功，继续执行被装饰的函数
        return f(auth_params['username'], *args, **kwargs)
    
    return decorated_function

@app.route('/')
def home():
    """
    主页路由
    
    Returns:
        JSON: 包含欢迎信息的响应
    """
    return jsonify({
        "message": "Welcome to HTTP Digest Authentication Demo Server",
        "description": "This server demonstrates HTTP Digest Authentication mechanism",
        "endpoints": {
            "/": "This page",
            "/public": "Public resource (no authentication required)",
            "/protected": "Protected resource (digest authentication required)",
            "/admin": "Admin resource (digest authentication required)"
        }
    })

@app.route('/public')
def public_resource():
    """
    公共资源路由（无需认证）
    
    Returns:
        JSON: 包含公共资源信息的响应
    """
    return jsonify({
        "message": "This is a public resource",
        "access": "Available to everyone",
        "timestamp": time.time()
    })

@app.route('/protected')
@require_digest_auth
def protected_resource(username):
    """
    受保护资源路由（需要摘要认证）
    
    Args:
        username (str): 经过认证的用户名
        
    Returns:
        JSON: 包含受保护资源信息的响应
    """
    return jsonify({
        "message": "This is a protected resource",
        "access": f"Access granted to user: {username}",
        "resource_type": "Protected Content",
        "timestamp": time.time()
    })

@app.route('/admin')
@require_digest_auth
def admin_resource(username):
    """
    管理员资源路由（需要摘要认证）
    
    Args:
        username (str): 经过认证的用户名
        
    Returns:
        JSON: 包含管理员资源信息的响应
    """
    # 检查用户权限（简单示例，实际应用中应有更复杂的权限系统）
    if username != "admin":
        challenge = digest_auth.create_digest_challenge()
        return Response(
            'Forbidden: Admin access required', 
            403, 
            {'WWW-Authenticate': challenge}
        )
    
    return jsonify({
        "message": "This is an admin resource",
        "access": f"Admin access granted to user: {username}",
        "resource_type": "Administrative Content",
        "timestamp": time.time()
    })

@app.route('/users')
@require_digest_auth
def list_users(username):
    """
    用户列表路由（需要摘要认证）
    
    Args:
        username (str): 经过认证的用户名
        
    Returns:
        JSON: 包含用户列表的响应
    """
    # 只有管理员可以查看所有用户
    if username != "admin":
        return jsonify({"error": "Access denied"}), 403
    
    # 返回简化版用户信息（不包含密码）
    users_list = []
    for user, info in USERS_DB.items():
        users_list.append({
            "username": user,
            "realm": info.get("realm")
        })
    
    return jsonify({
        "users": users_list,
        "count": len(users_list)
    })

if __name__ == '__main__':
    print("Starting HTTP Digest Authentication Demo Server...")
    print("Server running on http://localhost:5001")
    print("\nEndpoints:")
    print("  GET /              - Home page")
    print("  GET /public        - Public resource (no auth)")
    print("  GET /protected     - Protected resource (digest auth)")
    print("  GET /admin         - Admin resource (digest auth)")
    print("  GET /users         - User list (admin only)")
    print("\nTest credentials:")
    print("  Username: admin, Password: admin123")
    print("  Username: user, Password: user123")
    
    app.run(debug=True, port=5001)