#!/usr/bin/env python3
"""
HTTP 认证与授权最佳实践演示

这个模块演示了 HTTP 认证与授权的最佳实践，包括：
1. 安全的密码处理
2. 会话管理
3. 令牌生命周期管理
4. 多因素认证 (MFA)
5. 审计日志
6. 安全配置
7. 错误处理

学习目标：
- 理解认证与授权的安全最佳实践
- 掌握如何实现安全的用户管理系统
- 实践现代 Web 应用的安全设计原则
"""

import hashlib
import secrets
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, g
import jwt
import bcrypt
import logging

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # 更安全的密钥

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 安全配置
SECURITY_CONFIG = {
    "password_min_length": 8,
    "session_timeout": 3600,  # 1小时
    "token_expiration": 3600,  # 1小时
    "refresh_token_expiration": 2592000,  # 30天
    "max_login_attempts": 5,
    "lockout_duration": 900,  # 15分钟
    "bcrypt_rounds": 12
}

# 密钥配置（实际应用中应从环境变量读取）
JWT_SECRET_KEY = secrets.token_hex(32)
JWT_ALGORITHM = "HS256"

# 模拟数据库存储
users_db = {}
sessions_db = {}
tokens_db = {}
audit_log = []

class PasswordManager:
    """密码管理类"""
    
    @staticmethod
    def hash_password(password):
        """
        使用 bcrypt 哈希密码
        
        Args:
            password (str): 明文密码
            
        Returns:
            str: 哈希后的密码
        """
        salt = bcrypt.gensalt(rounds=SECURITY_CONFIG["bcrypt_rounds"])
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        """
        验证密码
        
        Args:
            password (str): 明文密码
            hashed_password (str): 哈希后的密码
            
        Returns:
            bool: 密码是否匹配
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def validate_password_strength(password):
        """
        验证密码强度
        
        Args:
            password (str): 待验证的密码
            
        Returns:
            tuple: (is_valid, message)
        """
        if len(password) < SECURITY_CONFIG["password_min_length"]:
            return False, f"Password must be at least {SECURITY_CONFIG['password_min_length']} characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"

class TokenManager:
    """令牌管理类"""
    
    @staticmethod
    def generate_access_token(user_id, role="user"):
        """
        生成访问令牌
        
        Args:
            user_id (str): 用户ID
            role (str): 用户角色
            
        Returns:
            str: JWT 访问令牌
        """
        payload = {
            "sub": user_id,
            "role": role,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=SECURITY_CONFIG["token_expiration"])
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def generate_refresh_token(user_id):
        """
        生成刷新令牌
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            str: 刷新令牌
        """
        token = secrets.token_urlsafe(32)
        tokens_db[token] = {
            "user_id": user_id,
            "created_at": time.time(),
            "expires_at": time.time() + SECURITY_CONFIG["refresh_token_expiration"]
        }
        return token
    
    @staticmethod
    def verify_access_token(token):
        """
        验证访问令牌
        
        Args:
            token (str): JWT 令牌
            
        Returns:
            dict: 解码后的载荷
            
        Raises:
            jwt.ExpiredSignatureError: 令牌已过期
            jwt.InvalidTokenError: 令牌无效
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if payload.get("type") != "access":
                raise jwt.InvalidTokenError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")
    
    @staticmethod
    def verify_refresh_token(token):
        """
        验证刷新令牌
        
        Args:
            token (str): 刷新令牌
            
        Returns:
            dict: 令牌信息
            
        Raises:
            ValueError: 令牌无效或已过期
        """
        if token not in tokens_db:
            raise ValueError("Invalid refresh token")
        
        token_info = tokens_db[token]
        if time.time() > token_info["expires_at"]:
            del tokens_db[token]
            raise ValueError("Refresh token has expired")
        
        return token_info

class SessionManager:
    """会话管理类"""
    
    @staticmethod
    def create_session(user_id, ip_address):
        """
        创建用户会话
        
        Args:
            user_id (str): 用户ID
            ip_address (str): IP地址
            
        Returns:
            str: 会话ID
        """
        session_id = secrets.token_urlsafe(32)
        sessions_db[session_id] = {
            "user_id": user_id,
            "ip_address": ip_address,
            "created_at": time.time(),
            "last_activity": time.time()
        }
        return session_id
    
    @staticmethod
    def validate_session(session_id, ip_address):
        """
        验证会话
        
        Args:
            session_id (str): 会话ID
            ip_address (str): IP地址
            
        Returns:
            bool: 会话是否有效
        """
        if session_id not in sessions_db:
            return False
        
        session_info = sessions_db[session_id]
        
        # 检查IP地址是否匹配（可选的安全措施）
        # if session_info["ip_address"] != ip_address:
        #     return False
        
        # 检查会话是否过期
        if time.time() - session_info["last_activity"] > SECURITY_CONFIG["session_timeout"]:
            del sessions_db[session_id]
            return False
        
        # 更新最后活动时间
        session_info["last_activity"] = time.time()
        return True
    
    @staticmethod
    def destroy_session(session_id):
        """
        销毁会话
        
        Args:
            session_id (str): 会话ID
        """
        if session_id in sessions_db:
            del sessions_db[session_id]

class AuditLogger:
    """审计日志类"""
    
    @staticmethod
    def log_event(event_type, user_id, ip_address, details=""):
        """
        记录审计事件
        
        Args:
            event_type (str): 事件类型
            user_id (str): 用户ID
            ip_address (str): IP地址
            details (str): 详细信息
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details
        }
        audit_log.append(log_entry)
        logger.info(f"Audit: {event_type} - User: {user_id} - IP: {ip_address} - Details: {details}")

class RateLimiter:
    """速率限制器类"""
    
    def __init__(self):
        self.attempts = {}
    
    def is_allowed(self, identifier, max_attempts=SECURITY_CONFIG["max_login_attempts"], 
                   window=SECURITY_CONFIG["lockout_duration"]):
        """
        检查是否允许请求
        
        Args:
            identifier (str): 标识符（如IP地址或用户ID）
            max_attempts (int): 最大尝试次数
            window (int): 时间窗口（秒）
            
        Returns:
            bool: 是否允许请求
        """
        now = time.time()
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        # 清理过期的尝试记录
        self.attempts[identifier] = [
            attempt for attempt in self.attempts[identifier] 
            if now - attempt < window
        ]
        
        # 检查是否超过最大尝试次数
        if len(self.attempts[identifier]) >= max_attempts:
            return False
        
        # 记录本次尝试
        self.attempts[identifier].append(now)
        return True
    
    def reset_attempts(self, identifier):
        """
        重置尝试次数
        
        Args:
            identifier (str): 标识符
        """
        if identifier in self.attempts:
            del self.attempts[identifier]

# 创建全局实例
rate_limiter = RateLimiter()

def require_auth(f):
    """
    装饰器：要求用户认证（基于会话）
    
    Args:
        f (function): 被装饰的视图函数
        
    Returns:
        function: 包装后的视图函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        ip_address = request.remote_addr
        
        if not session_id or not SessionManager.validate_session(session_id, ip_address):
            return jsonify({"error": "Authentication required"}), 401
        
        # 将用户信息添加到全局对象
        session_info = sessions_db[session_id]
        g.current_user_id = session_info["user_id"]
        g.current_user = users_db.get(session_info["user_id"], {})
        
        return f(*args, **kwargs)
    return decorated_function

def require_token_auth(f):
    """
    装饰器：要求令牌认证
    
    Args:
        f (function): 被装饰的视图函数
        
    Returns:
        function: 包装后的视图函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        
        try:
            payload = TokenManager.verify_access_token(token)
            g.current_user_id = payload['sub']
            g.current_user = users_db.get(payload['sub'], {})
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_role):
    """
    装饰器：要求特定角色
    
    Args:
        required_role (str): 所需角色
        
    Returns:
        function: 包装后的视图函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or g.current_user.get('role') != required_role:
                return jsonify({"error": "Insufficient permissions"}), 403
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
        "message": "HTTP Authentication & Authorization Best Practices Demo",
        "description": "This server demonstrates best practices for HTTP authentication and authorization",
        "endpoints": {
            "/": "This page",
            "/register": "User registration",
            "/login": "User login (session-based)",
            "/token": "Obtain access token (token-based)",
            "/refresh": "Refresh access token",
            "/profile": "User profile (auth required)",
            "/admin": "Admin panel (admin role required)",
            "/logout": "User logout",
            "/audit": "Audit log (admin only)"
        }
    })

@app.route('/register', methods=['POST'])
def register():
    """
    用户注册路由
    
    请求体应包含：
    {
        "username": "用户名",
        "password": "密码",
        "email": "邮箱"
    }
    
    Returns:
        JSON: 注册结果
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # 验证必需字段
    if not username or not password or not email:
        return jsonify({"error": "Username, password, and email are required"}), 400
    
    # 检查用户是否已存在
    if username in users_db:
        return jsonify({"error": "Username already exists"}), 409
    
    # 验证密码强度
    is_valid, message = PasswordManager.validate_password_strength(password)
    if not is_valid:
        return jsonify({"error": message}), 400
    
    # 创建新用户
    users_db[username] = {
        "username": username,
        "password_hash": PasswordManager.hash_password(password),
        "email": email,
        "role": "user",
        "created_at": datetime.utcnow().isoformat(),
        "mfa_enabled": False,
        "failed_attempts": 0,
        "locked_until": None
    }
    
    # 记录审计事件
    AuditLogger.log_event("USER_REGISTERED", username, request.remote_addr, f"User {username} registered")
    
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "username": username,
            "email": email,
            "role": "user"
        }
    }), 201

@app.route('/login', methods=['POST'])
def login():
    """
    用户登录路由（会话认证）
    
    请求体应包含：
    {
        "username": "用户名",
        "password": "密码"
    }
    
    Returns:
        JSON: 登录结果和会话信息
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    username = data.get('username')
    password = data.get('password')
    ip_address = request.remote_addr
    
    # 检查速率限制
    if not rate_limiter.is_allowed(f"login:{ip_address}"):
        AuditLogger.log_event("LOGIN_RATE_LIMITED", username or "unknown", ip_address, "Too many login attempts")
        return jsonify({"error": "Too many login attempts. Please try again later."}), 429
    
    # 验证用户名和密码
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if username not in users_db:
        rate_limiter.is_allowed(f"login:{ip_address}")  # 记录失败尝试
        AuditLogger.log_event("LOGIN_FAILED", username, ip_address, "User not found")
        return jsonify({"error": "Invalid credentials"}), 401
    
    user = users_db[username]
    
    # 检查账户是否被锁定
    if user["locked_until"] and time.time() < user["locked_until"]:
        AuditLogger.log_event("LOGIN_FAILED", username, ip_address, "Account locked")
        return jsonify({"error": "Account is temporarily locked. Please try again later."}), 423
    
    # 验证密码
    if not PasswordManager.verify_password(password, user["password_hash"]):
        # 增加失败尝试次数
        user["failed_attempts"] = user.get("failed_attempts", 0) + 1
        
        # 如果超过最大尝试次数，锁定账户
        if user["failed_attempts"] >= SECURITY_CONFIG["max_login_attempts"]:
            user["locked_until"] = time.time() + SECURITY_CONFIG["lockout_duration"]
            AuditLogger.log_event("ACCOUNT_LOCKED", username, ip_address, "Too many failed login attempts")
        
        rate_limiter.is_allowed(f"login:{ip_address}")  # 记录失败尝试
        AuditLogger.log_event("LOGIN_FAILED", username, ip_address, "Invalid password")
        return jsonify({"error": "Invalid credentials"}), 401
    
    # 登录成功，重置失败尝试次数
    user["failed_attempts"] = 0
    user["locked_until"] = None
    
    # 创建会话
    session_id = SessionManager.create_session(username, ip_address)
    session['session_id'] = session_id
    
    # 记录审计事件
    AuditLogger.log_event("USER_LOGGED_IN", username, ip_address, "Successful login")
    
    return jsonify({
        "message": "Login successful",
        "session_id": session_id,
        "user": {
            "username": username,
            "email": user["email"],
            "role": user["role"]
        }
    })

@app.route('/token', methods=['POST'])
def obtain_token():
    """
    获取访问令牌路由（令牌认证）
    
    请求体应包含：
    {
        "username": "用户名",
        "password": "密码"
    }
    
    Returns:
        JSON: 令牌信息
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    username = data.get('username')
    password = data.get('password')
    ip_address = request.remote_addr
    
    # 检查速率限制
    if not rate_limiter.is_allowed(f"token:{ip_address}"):
        AuditLogger.log_event("TOKEN_RATE_LIMITED", username or "unknown", ip_address, "Too many token requests")
        return jsonify({"error": "Too many requests. Please try again later."}), 429
    
    # 验证用户名和密码
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if username not in users_db:
        rate_limiter.is_allowed(f"token:{ip_address}")  # 记录失败尝试
        AuditLogger.log_event("TOKEN_FAILED", username, ip_address, "User not found")
        return jsonify({"error": "Invalid credentials"}), 401
    
    user = users_db[username]
    
    # 验证密码
    if not PasswordManager.verify_password(password, user["password_hash"]):
        rate_limiter.is_allowed(f"token:{ip_address}")  # 记录失败尝试
        AuditLogger.log_event("TOKEN_FAILED", username, ip_address, "Invalid password")
        return jsonify({"error": "Invalid credentials"}), 401
    
    # 生成令牌
    access_token = TokenManager.generate_access_token(username, user["role"])
    refresh_token = TokenManager.generate_refresh_token(username)
    
    # 记录审计事件
    AuditLogger.log_event("TOKEN_ISSUED", username, ip_address, "Access and refresh tokens issued")
    
    return jsonify({
        "message": "Tokens issued successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": SECURITY_CONFIG["token_expiration"]
    })

@app.route('/refresh', methods=['POST'])
def refresh_token():
    """
    刷新访问令牌路由
    
    请求体应包含：
    {
        "refresh_token": "刷新令牌"
    }
    
    Returns:
        JSON: 新的令牌信息
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    refresh_token_str = data.get('refresh_token')
    ip_address = request.remote_addr
    
    if not refresh_token_str:
        return jsonify({"error": "Refresh token is required"}), 400
    
    try:
        # 验证刷新令牌
        token_info = TokenManager.verify_refresh_token(refresh_token_str)
        user_id = token_info["user_id"]
        
        # 获取用户信息
        if user_id not in users_db:
            return jsonify({"error": "Invalid refresh token"}), 401
        
        user = users_db[user_id]
        
        # 生成新的访问令牌
        new_access_token = TokenManager.generate_access_token(user_id, user["role"])
        
        # 记录审计事件
        AuditLogger.log_event("TOKEN_REFRESHED", user_id, ip_address, "Access token refreshed")
        
        return jsonify({
            "message": "Token refreshed successfully",
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": SECURITY_CONFIG["token_expiration"]
        })
        
    except ValueError as e:
        AuditLogger.log_event("TOKEN_REFRESH_FAILED", "unknown", ip_address, f"Token refresh failed: {str(e)}")
        return jsonify({"error": str(e)}), 401

@app.route('/profile')
@require_auth
def user_profile():
    """
    用户档案路由（需要认证）
    
    Returns:
        JSON: 用户档案信息
    """
    user = g.current_user
    user_id = g.current_user_id
    
    # 返回用户信息（不包含敏感信息）
    profile_info = {
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"],
        "mfa_enabled": user["mfa_enabled"]
    }
    
    # 记录审计事件
    AuditLogger.log_event("PROFILE_ACCESSED", user_id, request.remote_addr, "User accessed their profile")
    
    return jsonify({
        "message": "Profile retrieved successfully",
        "profile": profile_info
    })

@app.route('/admin')
@require_auth
@require_role("administrator")
def admin_panel():
    """
    管理员面板路由（需要管理员权限）
    
    Returns:
        JSON: 管理员面板信息
    """
    user_id = g.current_user_id
    
    # 获取系统统计信息
    stats = {
        "total_users": len(users_db),
        "active_sessions": len(sessions_db),
        "issued_tokens": len(tokens_db),
        "recent_audit_events": len(audit_log[-10:])  # 最近10个审计事件
    }
    
    # 记录审计事件
    AuditLogger.log_event("ADMIN_PANEL_ACCESSED", user_id, request.remote_addr, "Admin accessed panel")
    
    return jsonify({
        "message": "Admin panel accessed successfully",
        "stats": stats
    })

@app.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    用户注销路由
    
    Returns:
        JSON: 注销结果
    """
    session_id = session.get('session_id')
    user_id = g.current_user_id
    
    # 销毁会话
    if session_id:
        SessionManager.destroy_session(session_id)
    
    # 清除会话
    session.clear()
    
    # 记录审计事件
    AuditLogger.log_event("USER_LOGGED_OUT", user_id, request.remote_addr, "User logged out")
    
    return jsonify({"message": "Logged out successfully"})

@app.route('/audit')
@require_auth
@require_role("administrator")
def audit_log_endpoint():
    """
    审计日志路由（仅管理员可访问）
    
    Returns:
        JSON: 审计日志
    """
    # 返回最近的审计日志条目
    recent_logs = audit_log[-50:]  # 最近50条日志
    
    return jsonify({
        "message": "Audit log retrieved successfully",
        "log_count": len(recent_logs),
        "logs": recent_logs
    })

# 错误处理程序
@app.errorhandler(401)
def unauthorized(error):
    """处理 401 未授权错误"""
    return jsonify({"error": "Unauthorized access"}), 401

@app.errorhandler(403)
def forbidden(error):
    """处理 403 禁止访问错误"""
    return jsonify({"error": "Forbidden access"}), 403

@app.errorhandler(429)
def too_many_requests(error):
    """处理 429 请求过多错误"""
    return jsonify({"error": "Too many requests"}), 429

# 在应用启动时创建测试用户
def create_test_users():
    """创建测试用户"""
    # 创建管理员用户
    admin_password_hash = PasswordManager.hash_password("admin123")
    users_db["admin"] = {
        "username": "admin",
        "password_hash": admin_password_hash,
        "email": "admin@example.com",
        "role": "administrator",
        "created_at": datetime.utcnow().isoformat(),
        "mfa_enabled": False,
        "failed_attempts": 0,
        "locked_until": None
    }
    
    # 创建普通用户
    user_password_hash = PasswordManager.hash_password("user123")
    users_db["user"] = {
        "username": "user",
        "password_hash": user_password_hash,
        "email": "user@example.com",
        "role": "user",
        "created_at": datetime.utcnow().isoformat(),
        "mfa_enabled": False,
        "failed_attempts": 0,
        "locked_until": None
    }
    
    logger.info("Test users created: admin and user")

# 在应用启动时调用创建测试用户函数
create_test_users()

if __name__ == '__main__':
    print("Starting HTTP Authentication & Authorization Best Practices Demo Server...")
    print("Server running on http://localhost:5005")
    print("\nEndpoints:")
    print("  GET /              - Home page")
    print("  POST /register     - User registration")
    print("  POST /login        - User login (session-based)")
    print("  POST /token        - Obtain access token (token-based)")
    print("  POST /refresh      - Refresh access token")
    print("  GET /profile       - User profile (auth required)")
    print("  GET /admin         - Admin panel (admin role required)")
    print("  POST /logout       - User logout")
    print("  GET /audit         - Audit log (admin only)")
    print("\nTest accounts:")
    print("  Username: admin, Password: admin123 (Administrator)")
    print("  Username: user, Password: user123 (Regular User)")
    print("\nSecurity features demonstrated:")
    print("  1. Secure password hashing with bcrypt")
    print("  2. Session management with timeout")
    print("  3. JWT token-based authentication")
    print("  4. Refresh token mechanism")
    print("  5. Rate limiting")
    print("  6. Account lockout after failed attempts")
    print("  7. Audit logging")
    print("  8. Role-based access control")
    print("  9. Secure error handling")
    
    app.run(debug=True, port=5005)