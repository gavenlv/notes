#!/usr/bin/env python3
"""
HTTP 认证安全头部和防护措施演示

这个模块演示了如何在 Flask 应用中实现各种安全头部和防护措施，
以增强认证和授权机制的安全性。

主要内容：
1. 安全头部设置（Security Headers）
2. 内容安全策略（CSP）
3. 跨站请求伪造（CSRF）防护
4. 点击劫持防护
5. XSS 防护
6. 严格传输安全（HSTS）

学习目标：
- 理解各种安全头部的作用和配置
- 掌握如何防止常见的 Web 安全威胁
- 实践在 Web 应用中实施综合安全措施
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from functools import wraps
import secrets
import hashlib
import os
import base64

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 用于会话管理

# 模拟用户数据库
USERS_DB = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "administrator"
    },
    "user": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user"
    }
}

class SecurityHeaders:
    """安全头部管理类"""
    
    @staticmethod
    def apply_security_headers(response):
        """
        应用安全头部到响应
        
        Args:
            response (Response): Flask 响应对象
            
        Returns:
            Response: 添加了安全头部的响应对象
        """
        # 1. 内容安全策略 (Content Security Policy)
        # 限制哪些资源可以被加载，防止 XSS 攻击
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # 生产环境中应避免 'unsafe-inline'
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "  # 防止点击劫持
            "form-action 'self'; "  # 限制表单提交的目标
            "upgrade-insecure-requests;"  # 自动升级 HTTP 请求到 HTTPS
        )
        
        # 2. X-Frame-Options - 防止点击劫持
        response.headers['X-Frame-Options'] = 'DENY'
        
        # 3. X-Content-Type-Options - 防止 MIME 类型嗅探
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # 4. X-XSS-Protection - XSS 过滤（现代浏览器已逐渐弃用，但仍有益处）
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 5. Strict-Transport-Security (HSTS) - 强制 HTTPS
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains; preload'  # 1年
        )
        
        # 6. Referrer-Policy - 控制 Referer 头部信息
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 7. Permissions-Policy - 控制浏览器功能的使用
        response.headers['Permissions-Policy'] = (
            "geolocation=(), midi=(), notifications=(), push=(), "
            "sync-xhr=(), microphone=(), camera=(), magnetometer=(), "
            "gyroscope=(), speaker=(), vibrate=(), fullscreen=(), "
            "payment=()"
        )
        
        return response

class CSRFProtection:
    """CSRF 防护类"""
    
    @staticmethod
    def generate_csrf_token():
        """
        生成 CSRF 令牌
        
        Returns:
            str: CSRF 令牌
        """
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return session['csrf_token']
    
    @staticmethod
    def validate_csrf_token(token):
        """
        验证 CSRF 令牌
        
        Args:
            token (str): 提交的 CSRF 令牌
            
        Returns:
            bool: 令牌是否有效
        """
        return 'csrf_token' in session and session['csrf_token'] == token

def require_auth(f):
    """
    装饰器：要求用户认证
    
    Args:
        f (function): 被装饰的视图函数
        
    Returns:
        function: 包装后的视图函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def add_security_headers(f):
    """
    装饰器：添加安全头部
    
    Args:
        f (function): 被装饰的视图函数
        
    Returns:
        function: 包装后的视图函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 执行原始函数
        response = f(*args, **kwargs)
        
        # 应用安全头部
        if hasattr(response, 'headers'):
            response = SecurityHeaders.apply_security_headers(response)
        
        return response
    return decorated_function

@app.before_request
def before_request():
    """在每个请求前执行"""
    # 对于非静态资源，生成 CSRF 令牌
    if not request.path.startswith('/static'):
        CSRFProtection.generate_csrf_token()

@app.after_request
def after_request(response):
    """在每个响应后执行"""
    # 应用安全头部
    response = SecurityHeaders.apply_security_headers(response)
    return response

@app.route('/')
@add_security_headers
def home():
    """
    主页路由
    
    Returns:
        HTML: 包含主页内容的响应
    """
    user_info = ""
    if 'user_id' in session:
        user_info = f"<p>Logged in as: {session['user_id']} ({session.get('user_role', 'user')})</p>"
        logout_link = '<p><a href="/logout">Logout</a></p>'
    else:
        user_info = "<p>Not logged in</p>"
        logout_link = '<p><a href="/login">Login</a></p>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Headers Demo</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px 0; }}
            .btn:hover {{ background-color: #0056b3; }}
            input {{ padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
            form {{ margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>HTTP Security Headers Demo</h1>
            {user_info}
            {logout_link}
            
            <div class="section">
                <h2>Demo Features</h2>
                <ul>
                    <li>Content Security Policy (CSP)</li>
                    <li>X-Frame-Options (Clickjacking Protection)</li>
                    <li>X-Content-Type-Options (MIME Sniffing Prevention)</li>
                    <li>X-XSS-Protection</li>
                    <li>Strict-Transport-Security (HSTS)</li>
                    <li>Referrer-Policy</li>
                    <li>Permissions-Policy</li>
                    <li>CSRF Protection</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>Protected Resources</h2>
                <a href="/dashboard" class="btn">Access Dashboard</a>
                <a href="/admin" class="btn">Access Admin Panel</a>
            </div>
            
            <div class="section">
                <h2>Security Test Forms</h2>
                <form action="/test-csp" method="POST">
                    <input type="hidden" name="csrf_token" value="{CSRFProtection.generate_csrf_token()}">
                    <button type="submit" class="btn">Test CSP Violation</button>
                </form>
                
                <form action="/test-xss" method="POST">
                    <input type="hidden" name="csrf_token" value="{CSRFProtection.generate_csrf_token()}">
                    <input type="text" name="xss_input" placeholder="Enter text to test XSS protection">
                    <button type="submit" class="btn">Test XSS Protection</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/login', methods=['GET', 'POST'])
@add_security_headers
def login():
    """
    登录路由
    
    Returns:
        HTML: 登录页面或登录结果
    """
    if request.method == 'POST':
        # 验证 CSRF 令牌
        csrf_token = request.form.get('csrf_token')
        if not CSRFProtection.validate_csrf_token(csrf_token):
            return "CSRF token validation failed", 400
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 验证用户凭据
        if username in USERS_DB:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if USERS_DB[username]['password_hash'] == password_hash:
                # 登录成功
                session['user_id'] = username
                session['user_role'] = USERS_DB[username]['role']
                return redirect(url_for('home'))
        
        # 登录失败
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Failed</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .error { color: red; }
                .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1 class="error">Login Failed</h1>
            <p>Invalid username or password.</p>
            <a href="/login" class="btn">Try Again</a>
        </body>
        </html>
        """)
    
    # 显示登录表单
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            .container {{ max-width: 400px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            .btn {{ width: 100%; padding: 12px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .btn:hover {{ background-color: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Login</h1>
            <form method="POST">
                <input type="hidden" name="csrf_token" value="{CSRFProtection.generate_csrf_token()}">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit" class="btn">Login</button>
            </form>
            <p><small>Test accounts: admin/admin123 or user/user123</small></p>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/logout')
@add_security_headers
def logout():
    """
    注销路由
    
    Returns:
        Redirect: 重定向到主页
    """
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@require_auth
@add_security_headers
def dashboard():
    """
    仪表板路由（需要认证）
    
    Returns:
        HTML: 仪表板页面
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            .btn:hover {{ background-color: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Dashboard</h1>
            <p>Welcome to your dashboard, {session['user_id']}!</p>
            <p>This is a protected resource that requires authentication.</p>
            <a href="/" class="btn">Back to Home</a>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/admin')
@require_auth
@add_security_headers
def admin_panel():
    """
    管理员面板路由（需要管理员权限）
    
    Returns:
        HTML: 管理员面板页面或拒绝访问页面
    """
    # 检查用户权限
    if session.get('user_role') != 'administrator':
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Access Denied</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .error { color: red; }
                .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1 class="error">Access Denied</h1>
            <p>You do not have permission to access the admin panel.</p>
            <a href="/" class="btn">Back to Home</a>
        </body>
        </html>
        """), 403
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .btn:hover { background-color: #0056b3; }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Admin Panel</h1>
            <p>Welcome to the administrator panel.</p>
            
            <div class="section">
                <h2>User Management</h2>
                <ul>
                    <li>Create new users</li>
                    <li>Modify user permissions</li>
                    <li>Delete users</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>System Configuration</h2>
                <ul>
                    <li>Update security settings</li>
                    <li>Manage API keys</li>
                    <li>Configure integrations</li>
                </ul>
            </div>
            
            <a href="/" class="btn">Back to Home</a>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/test-csp', methods=['POST'])
@require_auth
@add_security_headers
def test_csp():
    """
    测试 CSP 违规的路由
    
    Returns:
        HTML: 包含内联脚本的页面（会被 CSP 阻止）
    """
    # 验证 CSRF 令牌
    csrf_token = request.form.get('csrf_token')
    if not CSRFProtection.validate_csrf_token(csrf_token):
        return "CSRF token validation failed", 400
    
    # 这个页面包含违反 CSP 的内联脚本
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSP Test</title>
    </head>
    <body>
        <h1>CSP Test Page</h1>
        <p>This page attempts to execute inline JavaScript, which should be blocked by CSP.</p>
        
        <script>
            // This inline script should be blocked by CSP
            alert('If you see this alert, CSP is not working properly!');
            document.body.style.backgroundColor = 'red';
        </script>
        
        <p>If CSP is working correctly, you should NOT see an alert and the background should remain white.</p>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """
    return html_content

@app.route('/test-xss', methods=['POST'])
@require_auth
@add_security_headers
def test_xss():
    """
    测试 XSS 防护的路由
    
    Returns:
        HTML: 显示用户输入的页面
    """
    # 验证 CSRF 令牌
    csrf_token = request.form.get('csrf_token')
    if not CSRFProtection.validate_csrf_token(csrf_token):
        return "CSRF token validation failed", 400
    
    xss_input = request.form.get('xss_input', '')
    
    # 注意：在真实应用中，应该对用户输入进行适当的转义
    # 这里为了演示目的，我们显示原始输入，但 CSP 和其他安全措施应该能提供保护
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>XSS Test Result</title>
    </head>
    <body>
        <h1>XSS Test Result</h1>
        <p>You entered: {xss_input}</p>
        <p>If proper escaping was implemented, any HTML/JavaScript would be rendered as plain text.</p>
        <p>Security headers should also help prevent XSS attacks.</p>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """
    return html_content

# 自定义错误处理程序
@app.errorhandler(404)
@add_security_headers
def not_found(error):
    """处理 404 错误"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Page Not Found</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .error { color: red; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1 class="error">404 - Page Not Found</h1>
        <p>The requested page could not be found.</p>
        <a href="/" class="btn">Back to Home</a>
    </body>
    </html>
    """), 404

@app.errorhandler(403)
@add_security_headers
def forbidden(error):
    """处理 403 错误"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Access Forbidden</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .error { color: red; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1 class="error">403 - Access Forbidden</h1>
        <p>You don't have permission to access this resource.</p>
        <a href="/" class="btn">Back to Home</a>
    </body>
    </html>
    """), 403

if __name__ == '__main__':
    print("Starting HTTP Security Headers Demo Server...")
    print("Server running on http://localhost:5004")
    print("\nFeatures demonstrated:")
    print("  1. Content Security Policy (CSP)")
    print("  2. X-Frame-Options (Clickjacking Protection)")
    print("  3. X-Content-Type-Options (MIME Sniffing Prevention)")
    print("  4. X-XSS-Protection")
    print("  5. Strict-Transport-Security (HSTS)")
    print("  6. Referrer-Policy")
    print("  7. Permissions-Policy")
    print("  8. CSRF Protection")
    print("\nTest accounts:")
    print("  Username: admin, Password: admin123 (Administrator)")
    print("  Username: user, Password: user123 (Regular User)")
    
    app.run(debug=True, port=5004)