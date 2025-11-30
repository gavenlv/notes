#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全Cookies服务器示例
演示了各种Cookie安全特性的实现和使用
"""

from flask import Flask, request, make_response, jsonify, redirect, url_for
import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional
from itsdangerous import Signer, BadSignature


app = Flask(__name__)
app.secret_key = 'your-very-secret-key-for-signing-cookies'

# 简单的用户存储
users = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password_hash': hashlib.sha256('password'.encode()).hexdigest(),
        'role': 'admin'
    },
    'user': {
        'id': 2,
        'username': 'user',
        'password_hash': hashlib.sha256('password'.encode()).hexdigest(),
        'role': 'user'
    }
}


class SecurityCookieManager:
    """安全Cookie管理器"""
    
    def __init__(self, secret_key: str):
        self.signer = Signer(secret_key)
    
    def sign_cookie_value(self, value: str) -> str:
        """
        对Cookie值进行签名
        
        Args:
            value (str): 原始值
            
        Returns:
            str: 签名后的值
        """
        return self.signer.sign(value)
    
    def unsign_cookie_value(self, signed_value: str) -> Optional[str]:
        """
        验证并解签Cookie值
        
        Args:
            signed_value (str): 签名的值
            
        Returns:
            Optional[str]: 原始值，如果验证失败则返回None
        """
        try:
            return self.signer.unsign(signed_value).decode()
        except BadSignature:
            return None


# 创建安全Cookie管理器实例
security_manager = SecurityCookieManager(app.secret_key)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    用户认证
    
    Args:
        username (str): 用户名
        password (str): 密码
        
    Returns:
        Optional[dict]: 用户信息，认证失败返回None
    """
    user = users.get(username)
    if user and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
        return user
    return None


@app.route('/')
def home():
    """首页"""
    # 检查各种安全Cookie
    session_cookie = request.cookies.get('session_id')
    signed_cookie = request.cookies.get('signed_data')
    preference_cookie = request.cookies.get('user_preference')
    
    html = '''
    <h1>安全Cookies演示</h1>
    <p><a href="/login">登录</a> | <a href="/secure-demo">安全特性演示</a> | <a href="/logout">登出</a></p>
    
    <h2>当前Cookies状态:</h2>
    <ul>
        <li>会话Cookie: {}</li>
        <li>签名Cookie: {}</li>
        <li>偏好Cookie: {}</li>
    </ul>
    
    <h2>功能演示:</h2>
    <ul>
        <li><a href="/set-secure-cookies">设置安全Cookies</a></li>
        <li><a href="/csrf-demo">CSRF防护演示</a></li>
        <li><a href="/sensitive-data">访问敏感数据</a></li>
    </ul>
    '''.format(
        '存在' if session_cookie else '不存在',
        '存在' if signed_cookie else '不存在',
        preference_cookie or '未设置'
    )
    
    return html


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            # 创建会话ID
            session_id = secrets.token_urlsafe(32)
            
            # 设置安全会话Cookie
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie(
                'session_id',
                session_id,
                httponly=True,      # 防止XSS攻击
                secure=request.is_secure,  # 仅HTTPS环境设置
                samesite='Lax',     # CSRF防护
                max_age=3600        # 1小时过期
            )
            
            # 设置签名Cookie存储用户角色
            signed_role = security_manager.sign_cookie_value(user['role'])
            response.set_cookie(
                'user_role',
                signed_role,
                httponly=True,
                secure=request.is_secure,
                samesite='Lax',
                max_age=3600
            )
            
            return response
        else:
            return '<h2>登录失败</h2><p>用户名或密码错误</p><a href="/login">重新登录</a>', 401
    
    return '''
    <h2>用户登录</h2>
    <form method="post">
        <p><label>用户名: <input type="text" name="username" required></label></p>
        <p><label>密码: <input type="password" name="password" required></label></p>
        <p><input type="submit" value="登录"></p>
    </form>
    <p><a href="/">返回首页</a></p>
    '''


@app.route('/dashboard')
def dashboard():
    """仪表板页面"""
    # 验证会话
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('login'))
    
    # 验证签名Cookie
    signed_role = request.cookies.get('user_role')
    user_role = None
    if signed_role:
        user_role = security_manager.unsign_cookie_value(signed_role)
    
    return f'''
    <h1>用户仪表板</h1>
    <p>欢迎访问安全区域！</p>
    <p>用户角色: {user_role or '未知'}</p>
    <p><a href="/sensitive-data">访问敏感数据</a></p>
    <p><a href="/logout">登出</a></p>
    <p><a href="/">返回首页</a></p>
    '''


@app.route('/set-secure-cookies')
def set_secure_cookies():
    """设置各种安全特性的Cookie"""
    response = make_response(redirect(url_for('home')))
    
    # 1. HttpOnly Cookie
    response.set_cookie(
        'httponly_cookie',
        'httponly_value',
        httponly=True,
        secure=request.is_secure,
        samesite='Lax'
    )
    
    # 2. Secure Cookie (仅在HTTPS环境下生效)
    response.set_cookie(
        'secure_cookie',
        'secure_value',
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    
    # 3. SameSite Cookie
    response.set_cookie(
        'samesite_cookie',
        'strict_value',
        samesite='Strict',
        httponly=True,
        secure=request.is_secure
    )
    
    # 4. 带有过期时间的Cookie
    response.set_cookie(
        'expiring_cookie',
        'temporary_value',
        max_age=300,  # 5分钟过期
        httponly=True,
        secure=request.is_secure,
        samesite='Lax'
    )
    
    # 5. 限制域名和路径的Cookie
    response.set_cookie(
        'restricted_cookie',
        'restricted_value',
        domain=request.host.split(':')[0],  # 限制域名
        path='/restricted',                  # 限制路径
        httponly=True,
        secure=request.is_secure,
        samesite='Lax'
    )
    
    # 6. 签名Cookie
    signed_data = security_manager.sign_cookie_value('sensitive_user_data')
    response.set_cookie(
        'signed_data',
        signed_data,
        httponly=True,
        secure=request.is_secure,
        samesite='Lax'
    )
    
    return response


@app.route('/secure-demo')
def secure_demo():
    """安全特性演示页面"""
    # 检查各种安全Cookie
    cookies_info = []
    
    # HttpOnly Cookie
    httponly_cookie = request.cookies.get('httponly_cookie')
    cookies_info.append(('HttpOnly Cookie', httponly_cookie, '可通过JavaScript访问' if httponly_cookie else '不可通过JavaScript访问'))
    
    # Secure Cookie
    secure_cookie = request.cookies.get('secure_cookie')
    cookies_info.append(('Secure Cookie', secure_cookie, '仅在HTTPS传输' if secure_cookie else '可能在HTTP传输'))
    
    # SameSite Cookie
    samesite_cookie = request.cookies.get('samesite_cookie')
    cookies_info.append(('SameSite Cookie', samesite_cookie, '跨站请求保护' if samesite_cookie else '无跨站保护'))
    
    # 签名Cookie验证
    signed_data = request.cookies.get('signed_data')
    unsigned_data = None
    if signed_data:
        unsigned_data = security_manager.unsign_cookie_value(signed_data)
    cookies_info.append(('签名Cookie', unsigned_data, '数据完整性验证' if unsigned_data else '签名验证失败或不存在'))
    
    # 构建HTML响应
    html = '''
    <h1>安全Cookie特性演示</h1>
    <table border="1" cellpadding="10">
        <tr>
            <th>Cookie类型</th>
            <th>值</th>
            <th>安全特性</th>
        </tr>
    '''
    
    for name, value, description in cookies_info:
        html += f'''
        <tr>
            <td>{name}</td>
            <td>{value or '未设置'}</td>
            <td>{description}</td>
        </tr>
        '''
    
    html += '''
    </table>
    <p><a href="/set-secure-cookies">重新设置安全Cookies</a></p>
    <p><a href="/">返回首页</a></p>
    
    <h2>JavaScript测试</h2>
    <button onclick="testCookies()">测试Cookie可访问性</button>
    <div id="cookie-test-results"></div>
    
    <script>
    function testCookies() {
        const results = [];
        
        // 测试普通Cookie
        document.cookie = "test_cookie=test_value";
        if (document.cookie.includes("test_cookie")) {
            results.push("普通Cookie: 可通过JavaScript访问");
        } else {
            results.push("普通Cookie: 不可通过JavaScript访问");
        }
        
        // 测试HttpOnly Cookie（应该无法访问）
        if (document.cookie.includes("httponly_cookie")) {
            results.push("HttpOnly Cookie: 可通过JavaScript访问（配置错误！）");
        } else {
            results.push("HttpOnly Cookie: 不可通过JavaScript访问（正确配置）");
        }
        
        // 显示结果
        document.getElementById("cookie-test-results").innerHTML = 
            "<h3>测试结果:</h3><ul><li>" + results.join("</li><li>") + "</li></ul>";
    }
    </script>
    '''
    
    return html


@app.route('/csrf-demo', methods=['GET', 'POST'])
def csrf_demo():
    """CSRF防护演示"""
    if request.method == 'POST':
        # 检查CSRF Token
        csrf_token = request.form.get('csrf_token')
        cookie_token = request.cookies.get('csrf_token')
        
        if csrf_token and cookie_token and csrf_token == cookie_token:
            return '''
            <h2>CSRF防护成功</h2>
            <p>表单提交已验证，不是CSRF攻击</p>
            <p><a href="/csrf-demo">重新测试</a></p>
            <p><a href="/">返回首页</a></p>
            '''
        else:
            return '''
            <h2>CSRF防护拦截</h2>
            <p>检测到可能的CSRF攻击</p>
            <p>Token匹配失败</p>
            <p><a href="/csrf-demo">重新测试</a></p>
            <p><a href="/">返回首页</a></p>
            ''', 403
    
    # 生成CSRF Token
    csrf_token = secrets.token_urlsafe(32)
    
    # 设置CSRF Token Cookie
    response = make_response(f'''
    <h1>CSRF防护演示</h1>
    <form method="post">
        <input type="hidden" name="csrf_token" value="{csrf_token}">
        <p><label>测试数据: <input type="text" name="test_data" value="test_value"></label></p>
        <p><input type="submit" value="提交表单"></p>
    </form>
    <p><a href="/">返回首页</a></p>
    
    <h2>说明</h2>
    <p>这个表单包含了CSRF防护机制：</p>
    <ul>
        <li>服务器生成随机CSRF Token</li>
        <li>Token同时存储在表单隐藏字段和Cookie中</li>
        <li>提交时验证两个Token是否匹配</li>
    </ul>
    ''')
    
    response.set_cookie(
        'csrf_token',
        csrf_token,
        httponly=True,
        secure=request.is_secure,
        samesite='Strict'
    )
    
    return response


@app.route('/sensitive-data')
def sensitive_data():
    """敏感数据访问页面"""
    # 验证会话
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('login'))
    
    # 验证签名Cookie中的用户角色
    signed_role = request.cookies.get('user_role')
    user_role = None
    if signed_role:
        user_role = security_manager.unsign_cookie_value(signed_role)
    
    # 根据角色控制访问权限
    if user_role == 'admin':
        return '''
        <h1>敏感数据</h1>
        <p>这里是管理员专用的敏感数据</p>
        <pre>
系统配置信息:
- 数据库连接: mysql://admin:****@localhost:3306/production
- API密钥: sk-************************************************
- 服务器IP: 192.168.1.100
        </pre>
        <p><a href="/dashboard">返回仪表板</a></p>
        <p><a href="/">返回首页</a></p>
        '''
    elif user_role == 'user':
        return '''
        <h1>受限数据</h1>
        <p>这里是普通用户可以访问的数据</p>
        <p>您的账户信息正常，无异常活动。</p>
        <p><a href="/dashboard">返回仪表板</a></p>
        <p><a href="/">返回首页</a></p>
        '''
    else:
        return '''
        <h1>访问拒绝</h1>
        <p>您没有权限访问此资源</p>
        <p><a href="/dashboard">返回仪表板</a></p>
        <p><a href="/">返回首页</a></p>
        ''', 403


@app.route('/logout')
def logout():
    """登出接口"""
    response = make_response(redirect(url_for('home')))
    
    # 清除所有安全Cookie
    cookies_to_clear = [
        'session_id',
        'user_role',
        'httponly_cookie',
        'secure_cookie',
        'samesite_cookie',
        'expiring_cookie',
        'restricted_cookie',
        'signed_data',
        'csrf_token'
    ]
    
    for cookie_name in cookies_to_clear:
        response.delete_cookie(cookie_name)
    
    return response


@app.route('/restricted')
def restricted_area():
    """受限区域演示路径限制Cookie"""
    restricted_cookie = request.cookies.get('restricted_cookie')
    
    if restricted_cookie:
        return f'''
        <h1>受限区域</h1>
        <p>受限Cookie值: {restricted_cookie}</p>
        <p>只有在特定路径下才能访问此Cookie</p>
        <p><a href="/">返回首页</a></p>
        '''
    else:
        return '''
        <h1>受限区域</h1>
        <p>无法访问受限Cookie</p>
        <p>请先设置受限Cookie</p>
        <p><a href="/set-secure-cookies">设置安全Cookies</a></p>
        <p><a href="/">返回首页</a></p>
        '''


# 安全头部中间件
@app.after_request
def after_request(response):
    """添加安全头部"""
    # 防止点击劫持
    response.headers['X-Frame-Options'] = 'DENY'
    
    # XSS防护
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 内容类型嗅探保护
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # 严格传输安全（仅在HTTPS环境下）
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


if __name__ == '__main__':
    print("启动安全Cookies服务器...")
    print("访问 http://localhost:5000 查看演示")
    app.run(debug=True, port=5000)