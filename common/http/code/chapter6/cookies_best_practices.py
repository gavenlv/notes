#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookies最佳实践示例
演示了Cookies使用的最佳实践和常见陷阱避免
"""

from flask import Flask, request, make_response, jsonify, redirect, url_for
import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re


app = Flask(__name__)
app.secret_key = 'your-very-secret-key-for-best-practices-demo'

# 用户存储
users = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password_hash': hashlib.sha256('password'.encode()).hexdigest(),
        'preferences': {
            'theme': 'dark',
            'language': 'zh-CN',
            'notifications': True
        }
    },
    'user': {
        'id': 2,
        'username': 'user',
        'password_hash': hashlib.sha256('password'.encode()).hexdigest(),
        'preferences': {
            'theme': 'light',
            'language': 'en-US',
            'notifications': False
        }
    }
}


class BestPracticesCookieManager:
    """Cookies最佳实践管理器"""
    
    @staticmethod
    def set_minimal_session_cookie(response, session_id: str, user_role: str):
        """
        设置最小化的会话Cookie
        
        Args:
            response: Flask响应对象
            session_id (str): 会话ID
            user_role (str): 用户角色
        """
        # 只存储会话ID，不存储用户信息
        response.set_cookie(
            'sid',
            session_id,
            httponly=True,
            secure=True,  # 生产环境必须使用HTTPS
            samesite='Lax',
            max_age=1800,  # 30分钟过期
            path='/'
        )
        
        # 如果需要角色信息，使用单独的签名Cookie
        role_signature = hashlib.sha256(f"{session_id}:{user_role}".encode()).hexdigest()[:16]
        response.set_cookie(
            'role_sig',
            role_signature,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=1800,
            path='/'
        )
    
    @staticmethod
    def set_preference_cookie(response, preference_name: str, preference_value: str):
        """
        设置用户偏好Cookie
        
        Args:
            response: Flask响应对象
            preference_name (str): 偏好名称
            preference_value (str): 偏好值
        """
        # 验证偏好值
        if not BestPracticesCookieManager._is_valid_preference(preference_name, preference_value):
            raise ValueError(f"无效的偏好值: {preference_name}={preference_value}")
        
        # 设置长期有效的偏好Cookie
        response.set_cookie(
            f'pref_{preference_name}',
            preference_value,
            max_age=31536000,  # 1年过期
            httponly=False,    # 前端需要访问
            secure=True,
            samesite='Lax',
            path='/'
        )
    
    @staticmethod
    def _is_valid_preference(preference_name: str, preference_value: str) -> bool:
        """
        验证偏好值是否有效
        
        Args:
            preference_name (str): 偏好名称
            preference_value (str): 偏好值
            
        Returns:
            bool: 是否有效
        """
        valid_preferences = {
            'theme': ['light', 'dark'],
            'language': ['en-US', 'zh-CN', 'ja-JP'],
            'notifications': ['true', 'false']
        }
        
        if preference_name not in valid_preferences:
            return False
        
        valid_values = valid_preferences[preference_name]
        return preference_value in valid_values
    
    @staticmethod
    def get_user_preferences_from_cookies() -> Dict[str, str]:
        """
        从Cookies中获取用户偏好设置
        
        Returns:
            Dict[str, str]: 用户偏好设置
        """
        preferences = {}
        
        # 从Cookies中读取偏好设置
        for pref_name in ['theme', 'language', 'notifications']:
            cookie_name = f'pref_{pref_name}'
            pref_value = request.cookies.get(cookie_name)
            if pref_value and BestPracticesCookieManager._is_valid_preference(pref_name, pref_value):
                preferences[pref_name] = pref_value
        
        return preferences
    
    @staticmethod
    def prevent_session_fixation(response, old_session_id: str = None):
        """
        防止会话固定攻击
        
        Args:
            response: Flask响应对象
            old_session_id (str): 旧会话ID（可选）
        """
        # 生成新的会话ID
        new_session_id = secrets.token_urlsafe(32)
        
        # 如果有旧会话ID，在服务器端标记为无效
        if old_session_id:
            # 在实际应用中，这里应该在会话存储中标记旧会话为无效
            print(f"会话固定防护：使旧会话 {old_session_id[:10]}... 失效")
        
        # 设置新的会话Cookie
        response.set_cookie(
            'sid',
            new_session_id,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=1800,
            path='/'
        )
        
        return new_session_id


# 会话存储（简化版，生产环境应使用Redis等）
sessions = {}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """用户认证"""
    user = users.get(username)
    if user and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
        return user
    return None


def get_session_user(session_id: str) -> Optional[dict]:
    """根据会话ID获取用户信息"""
    if session_id in sessions:
        user_id = sessions[session_id]
        for user in users.values():
            if user['id'] == user_id:
                return user
    return None


@app.route('/')
def home():
    """首页"""
    # 检查会话
    session_id = request.cookies.get('sid')
    user = get_session_user(session_id) if session_id else None
    
    # 获取用户偏好
    preferences = BestPracticesCookieManager.get_user_preferences_from_cookies()
    
    html = f'''
    <h1>Cookies最佳实践演示</h1>
    <p>当前主题: {preferences.get('theme', '未设置')}</p>
    <p>语言设置: {preferences.get('language', '未设置')}</p>
    <p>通知设置: {preferences.get('notifications', '未设置')}</p>
    
    '''
    
    if user:
        html += f'''
        <p>欢迎, {user['username']}!</p>
        <p><a href="/dashboard">用户仪表板</a></p>
        <p><a href="/preferences">偏好设置</a></p>
        <p><a href="/logout">登出</a></p>
        '''
    else:
        html += '''
        <p><a href="/login">请登录</a></p>
        '''
    
    html += '''
    <h2>最佳实践演示:</h2>
    <ul>
        <li><a href="/login">安全登录（防会话固定）</a></li>
        <li><a href="/preferences">用户偏好管理</a></li>
        <li><a href="/secure-download">安全下载</a></li>
        <li><a href="/api/stats">API统计信息</a></li>
    </ul>
    '''
    
    return html


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面（实现会话固定防护）"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            # 实施会话固定防护
            response = make_response(redirect(url_for('dashboard')))
            new_session_id = BestPracticesCookieManager.prevent_session_fixation(response)
            
            # 在服务器端存储会话
            sessions[new_session_id] = user['id']
            
            # 设置角色签名
            role_signature = hashlib.sha256(f"{new_session_id}:{user['role']}".encode()).hexdigest()[:16]
            response.set_cookie(
                'role_sig',
                role_signature,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=1800,
                path='/'
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
    """用户仪表板"""
    session_id = request.cookies.get('sid')
    user = get_session_user(session_id) if session_id else None
    
    if not user:
        return redirect(url_for('login'))
    
    return f'''
    <h1>用户仪表板</h1>
    <p>欢迎, {user['username']}!</p>
    <p>用户ID: {user['id']}</p>
    <p>角色: {user.get('role', 'user')}</p>
    <p><a href="/preferences">偏好设置</a></p>
    <p><a href="/secure-download">安全下载</a></p>
    <p><a href="/logout">登出</a></p>
    <p><a href="/">返回首页</a></p>
    '''


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    """用户偏好设置"""
    session_id = request.cookies.get('sid')
    user = get_session_user(session_id) if session_id else None
    
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # 获取表单数据
        theme = request.form.get('theme', 'light')
        language = request.form.get('language', 'en-US')
        notifications = request.form.get('notifications', 'false')
        
        # 验证数据
        if theme not in ['light', 'dark']:
            theme = 'light'
        if language not in ['en-US', 'zh-CN', 'ja-JP']:
            language = 'en-US'
        if notifications not in ['true', 'false']:
            notifications = 'false'
        
        # 设置偏好Cookie
        response = make_response(redirect(url_for('preferences')))
        try:
            BestPracticesCookieManager.set_preference_cookie(response, 'theme', theme)
            BestPracticesCookieManager.set_preference_cookie(response, 'language', language)
            BestPracticesCookieManager.set_preference_cookie(response, 'notifications', notifications)
        except ValueError as e:
            return f'<h2>设置失败</h2><p>{e}</p><a href="/preferences">重新设置</a>'
        
        return response
    
    # 获取当前偏好设置
    current_prefs = BestPracticesCookieManager.get_user_preferences_from_cookies()
    
    # 如果没有设置，则使用用户默认偏好
    if not current_prefs:
        current_prefs = user.get('preferences', {})
    
    return f'''
    <h1>用户偏好设置</h1>
    <form method="post">
        <p>
            <label>主题: 
                <select name="theme">
                    <option value="light" {"selected" if current_prefs.get('theme') == 'light' else ""}>浅色</option>
                    <option value="dark" {"selected" if current_prefs.get('theme') == 'dark' else ""}>深色</option>
                </select>
            </label>
        </p>
        <p>
            <label>语言: 
                <select name="language">
                    <option value="en-US" {"selected" if current_prefs.get('language') == 'en-US' else ""}>English</option>
                    <option value="zh-CN" {"selected" if current_prefs.get('language') == 'zh-CN' else ""}>中文</option>
                    <option value="ja-JP" {"selected" if current_prefs.get('language') == 'ja-JP' else ""}>日本語</option>
                </select>
            </label>
        </p>
        <p>
            <label>
                <input type="checkbox" name="notifications" value="true" {"checked" if current_prefs.get('notifications') == 'true' else ""}>
                启用通知
            </label>
        </p>
        <p><input type="submit" value="保存设置"></p>
    </form>
    <p><a href="/dashboard">返回仪表板</a></p>
    <p><a href="/">返回首页</a></p>
    '''


@app.route('/secure-download')
def secure_download():
    """安全下载演示"""
    session_id = request.cookies.get('sid')
    user = get_session_user(session_id) if session_id else None
    
    if not user:
        return redirect(url_for('login'))
    
    # 生成一次性下载令牌
    download_token = secrets.token_urlsafe(16)
    
    # 设置下载令牌Cookie（短期有效）
    response = make_response(f'''
    <h1>安全下载</h1>
    <p>准备下载敏感文件...</p>
    <p><a href="/download-file/{download_token}">点击下载</a></p>
    <p>注意：下载链接只能使用一次，且5分钟内有效</p>
    <p><a href="/dashboard">返回仪表板</a></p>
    <p><a href="/">返回首页</a></p>
    ''')
    
    response.set_cookie(
        'dl_token',
        download_token,
        httponly=True,
        secure=True,
        samesite='Lax',
        max_age=300,  # 5分钟过期
        path='/'
    )
    
    return response


@app.route('/download-file/<token>')
def download_file(token):
    """文件下载端点"""
    # 验证下载令牌
    dl_token = request.cookies.get('dl_token')
    
    if not dl_token or dl_token != token:
        return '<h2>下载失败</h2><p>无效的下载令牌</p>', 403
    
    # 清除下载令牌Cookie（一次性使用）
    response = make_response('''
    <h1>文件下载</h1>
    <p>这是一个模拟的敏感文件内容</p>
    <pre>
机密数据:
- 项目计划书 v2.1
- 财务报表 Q3 2023
- 客户名单
    </pre>
    <p>实际应用中，这里应该是文件流响应</p>
    <p><a href="/dashboard">返回仪表板</a></p>
    <p><a href="/">返回首页</a></p>
    ''')
    
    response.delete_cookie('dl_token')
    return response


@app.route('/api/stats')
def api_stats():
    """API统计信息（演示最小化Cookie原则）"""
    # 不需要用户认证的公开API
    stats = {
        'total_users': len(users),
        'active_sessions': len(sessions),
        'server_time': datetime.now().isoformat()
    }
    
    # 设置最小化的API统计Cookie（如果需要）
    response = jsonify(stats)
    
    # 只设置必要的Cookie，且尽量少
    response.set_cookie(
        'api_last_access',
        datetime.now().isoformat(),
        max_age=86400,  # 1天过期
        httponly=True,
        secure=True,
        samesite='Lax'
    )
    
    return response


@app.route('/logout')
def logout():
    """登出接口"""
    session_id = request.cookies.get('sid')
    
    # 在服务器端清除会话
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    # 清除所有相关Cookie
    response = make_response(redirect(url_for('home')))
    response.delete_cookie('sid')
    response.delete_cookie('role_sig')
    response.delete_cookie('dl_token')
    
    # 注意：保留用户偏好Cookie，因为它们是长期设置
    # pref_* cookies 不会被删除
    
    return response


# 安全中间件
@app.after_request
def security_headers(response):
    """添加安全头部"""
    # 内容安全策略
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    
    # 防止点击劫持
    response.headers['X-Frame-Options'] = 'DENY'
    
    # XSS防护
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 内容类型嗅探保护
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # 严格传输安全
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


# Cookie大小监控
@app.before_request
def monitor_cookie_size():
    """监控Cookie大小"""
    total_cookie_size = sum(len(name) + len(value) for name, value in request.cookies.items())
    
    # 如果Cookie总大小超过4KB，记录警告
    if total_cookie_size > 4096:
        print(f"警告：Cookie总大小过大 ({total_cookie_size} bytes)")


if __name__ == '__main__':
    print("启动Cookies最佳实践演示服务器...")
    print("访问 http://localhost:5000 查看演示")
    print("\n最佳实践要点:")
    print("1. 最小化Cookie数据")
    print("2. 设置合适的安全标志")
    print("3. 实施会话固定防护")
    print("4. 验证Cookie值")
    print("5. 正确处理Cookie过期")
    app.run(debug=True, port=5000)