#!/usr/bin/env python3
"""
HTTP Bearer Token 认证服务器示例

这个模块演示了如何在 Flask 应用中实现 HTTP Bearer Token 认证机制。
它包括 JWT 令牌的生成、验证以及基于令牌的访问控制。

主要组件：
1. TokenManager 类：处理 JWT 令牌的生成和验证
2. require_bearer_token 装饰器：用于保护需要认证的路由
3. 各种示例端点：展示不同的认证场景

学习目标：
- 理解 Bearer Token 认证的工作原理
- 掌握 JWT 令牌的结构和使用方法
- 实践 Bearer Token 认证在 Web 应用中的实现
"""

import jwt
import datetime
import secrets
from functools import wraps
from flask import Flask, request, jsonify, Response

# 初始化 Flask 应用
app = Flask(__name__)

# 密钥（实际应用中应该从环境变量或配置文件中读取）
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# 模拟用户数据库 (实际应用中应该使用更安全的存储方式)
USERS_DB = {
    "admin": {
        "password": "admin123",
        "role": "administrator",
        "permissions": ["read", "write", "delete", "admin"]
    },
    "user": {
        "password": "user123",
        "role": "user",
        "permissions": ["read", "write"]
    },
    "guest": {
        "password": "guest123",
        "role": "guest",
        "permissions": ["read"]
    }
}

class TokenManager:
    """处理 JWT 令牌的生成和验证"""
    
    def __init__(self, secret_key, algorithm="HS256"):
        """
        初始化令牌管理器
        
        Args:
            secret_key (str): 用于签名 JWT 的密钥
            algorithm (str): 加密算法
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, username, expires_in=3600):
        """
        为用户生成 JWT 令牌
        
        Args:
            username (str): 用户名
            expires_in (int): 令牌有效期（秒）
            
        Returns:
            str: JWT 令牌
        """
        # 获取用户信息
        if username not in USERS_DB:
            raise ValueError("User not found")
        
        user_info = USERS_DB[username]
        
        # 设置令牌载荷
        payload = {
            "sub": username,  # 主题（用户标识）
            "role": user_info["role"],  # 用户角色
            "permissions": user_info["permissions"],  # 用户权限
            "iat": datetime.datetime.utcnow(),  # 签发时间
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)  # 过期时间
        }
        
        # 生成并返回 JWT 令牌
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token):
        """
        验证 JWT 令牌
        
        Args:
            token (str): JWT 令牌
            
        Returns:
            dict: 解码后的令牌载荷
            
        Raises:
            jwt.ExpiredSignatureError: 令牌已过期
            jwt.InvalidTokenError: 令牌无效
        """
        try:
            # 解码并验证令牌
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")

# 创建令牌管理器实例
token_manager = TokenManager(SECRET_KEY, ALGORITHM)

def require_bearer_token(required_permissions=None):
    """
    装饰器：要求 HTTP Bearer Token 认证
    
    Args:
        required_permissions (list): 所需权限列表（可选）
        
    Returns:
        function: 包装后的视图函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查 Authorization 头部
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "Authorization header is missing"}), 401
            
            # 解析 Bearer Token
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Invalid authorization header format"}), 401
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            
            try:
                # 验证令牌
                payload = token_manager.verify_token(token)
                
                # 检查权限（如果指定了所需权限）
                if required_permissions:
                    user_permissions = payload.get("permissions", [])
                    if not all(permission in user_permissions for permission in required_permissions):
                        return jsonify({"error": "Insufficient permissions"}), 403
                
                # 将用户信息添加到请求上下文
                request.current_user = payload
                
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            except Exception as e:
                return jsonify({"error": f"Authentication error: {str(e)}"}), 401
            
            # 认证成功，继续执行被装饰的函数
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

@app.route('/')
def home():
    """
    主页路由
    
    Returns:
        JSON: 包含欢迎信息的响应
    """
    return jsonify({
        "message": "Welcome to HTTP Bearer Token Authentication Demo Server",
        "description": "This server demonstrates HTTP Bearer Token Authentication mechanism using JWT",
        "endpoints": {
            "/": "This page",
            "/public": "Public resource (no authentication required)",
            "/login": "Login endpoint to obtain Bearer token",
            "/protected": "Protected resource (bearer token authentication required)",
            "/admin": "Admin resource (bearer token with admin permission required)",
            "/profile": "User profile (bearer token required)"
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
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route('/login', methods=['POST'])
def login():
    """
    登录路由，用于获取 Bearer Token
    
    请求体应包含：
    {
        "username": "用户名",
        "password": "密码"
    }
    
    Returns:
        JSON: 包含访问令牌的响应
    """
    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # 验证用户名和密码
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if username not in USERS_DB:
        return jsonify({"error": "Invalid credentials"}), 401
    
    user_info = USERS_DB[username]
    if user_info["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    try:
        # 生成访问令牌（默认1小时有效期）
        access_token = token_manager.generate_token(username)
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600  # 1小时
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate token: {str(e)}"}), 500

@app.route('/protected')
@require_bearer_token()
def protected_resource():
    """
    受保护资源路由（需要 Bearer Token 认证）
    
    Returns:
        JSON: 包含受保护资源信息的响应
    """
    # 获取当前用户信息
    current_user = request.current_user
    
    return jsonify({
        "message": "This is a protected resource",
        "access": f"Access granted to user: {current_user['sub']}",
        "user_role": current_user['role'],
        "user_permissions": current_user['permissions'],
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route('/admin')
@require_bearer_token(required_permissions=["admin"])
def admin_resource():
    """
    管理员资源路由（需要 Bearer Token 认证和管理员权限）
    
    Returns:
        JSON: 包含管理员资源信息的响应
    """
    # 获取当前用户信息
    current_user = request.current_user
    
    return jsonify({
        "message": "This is an admin resource",
        "access": f"Admin access granted to user: {current_user['sub']}",
        "resource_type": "Administrative Content",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route('/profile')
@require_bearer_token()
def user_profile():
    """
    用户档案路由（需要 Bearer Token 认证）
    
    Returns:
        JSON: 包含用户档案信息的响应
    """
    # 获取当前用户信息
    current_user = request.current_user
    
    # 获取用户详细信息（不包含密码）
    user_details = USERS_DB.get(current_user['sub'], {})
    profile_info = {
        "username": current_user['sub'],
        "role": current_user['role'],
        "permissions": current_user['permissions'],
        "joined_date": "2023-01-01"  # 示例数据
    }
    
    return jsonify({
        "message": "User profile retrieved successfully",
        "profile": profile_info
    })

@app.route('/refresh-token')
@require_bearer_token()
def refresh_token():
    """
    刷新令牌路由（需要有效的 Bearer Token）
    
    Returns:
        JSON: 包含新访问令牌的响应
    """
    # 获取当前用户信息
    current_user = request.current_user
    username = current_user['sub']
    
    try:
        # 生成新的访问令牌
        new_token = token_manager.generate_token(username)
        
        return jsonify({
            "message": "Token refreshed successfully",
            "access_token": new_token,
            "token_type": "Bearer",
            "expires_in": 3600
        })
    except Exception as e:
        return jsonify({"error": f"Failed to refresh token: {str(e)}"}), 500

# 错误处理程序
@app.errorhandler(401)
def unauthorized(error):
    """处理 401 未授权错误"""
    return jsonify({"error": "Unauthorized access"}), 401

@app.errorhandler(403)
def forbidden(error):
    """处理 403 禁止访问错误"""
    return jsonify({"error": "Forbidden access"}), 403

if __name__ == '__main__':
    print("Starting HTTP Bearer Token Authentication Demo Server...")
    print("Server running on http://localhost:5002")
    print("\nEndpoints:")
    print("  GET /                   - Home page")
    print("  GET /public             - Public resource (no auth)")
    print("  POST /login             - Login to get Bearer token")
    print("  GET /protected          - Protected resource (bearer token auth)")
    print("  GET /admin              - Admin resource (admin permission required)")
    print("  GET /profile            - User profile (bearer token required)")
    print("  GET /refresh-token      - Refresh token (valid token required)")
    print("\nTo get a token, send POST request to /login with:")
    print('  {"username": "admin", "password": "admin123"}')
    print("\nTo access protected resources, include header:")
    print("  Authorization: Bearer <your-token>")
    
    app.run(debug=True, port=5002)