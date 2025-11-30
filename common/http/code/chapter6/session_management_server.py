#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Flask的会话管理服务器示例
演示了完整的会话管理实现，包括登录、会话验证、登出等功能
"""

from flask import Flask, request, make_response, jsonify, redirect, url_for
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib


app = Flask(__name__)
app.secret_key = 'your-secret-key-for-session-signing'

# 简单的内存用户存储（生产环境应使用数据库）
users = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password_hash': hashlib.sha256('password'.encode()).hexdigest(),  # 简化的密码哈希
        'email': 'admin@example.com'
    },
    'user1': {
        'id': 2,
        'username': 'user1',
        'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
        'email': 'user1@example.com'
    }
}

# 会话存储（生产环境应使用Redis等外部存储）
sessions = {}


class SessionManager:
    """会话管理器"""
    
    @staticmethod
    def generate_session_id() -> str:
        """生成唯一的会话ID"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_session(user_id: int) -> str:
        """创建新会话"""
        session_id = SessionManager.generate_session_id()
        sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        if not session_id or session_id not in sessions:
            return None
        
        session = sessions[session_id]
        
        # 检查会话是否过期（30分钟）
        if datetime.now() - session['last_accessed'] > timedelta(minutes=30):
            SessionManager.destroy_session(session_id)
            return None
        
        # 更新最后访问时间
        session['last_accessed'] = datetime.now()
        return session
    
    @staticmethod
    def destroy_session(session_id: str) -> bool:
        """销毁会话"""
        if session_id in sessions:
            del sessions[session_id]
            return True
        return False
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """根据用户ID获取用户信息"""
        for user in users.values():
            if user['id'] == user_id:
                return user
        return None


def require_authentication(f):
    """认证装饰器"""
    def wrapper(*args, **kwargs):
        session_id = request.cookies.get('session_id')
        session = SessionManager.get_session(session_id) if session_id else None
        
        if not session:
            return jsonify({'error': '未认证'}), 401
        
        # 将用户信息添加到请求上下文
        request.current_user = SessionManager.get_user_by_id(session['user_id'])
        request.session = session
        
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/')
def home():
    """首页 - 显示当前登录状态"""
    session_id = request.cookies.get('session_id')
    session = SessionManager.get_session(session_id) if session_id else None
    
    if session:
        user = SessionManager.get_user_by_id(session['user_id'])
        return f'''
        <h1>欢迎回来！</h1>
        <p>用户名: {user['username']}</p>
        <p>邮箱: {user['email']}</p>
        <p><a href="/profile">查看个人资料</a></p>
        <p><a href="/logout">登出</a></p>
        '''
    else:
        return '''
        <h1>HTTP会话管理演示</h1>
        <p><a href="/login">请登录</a></p>
        '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 验证用户凭据
        user = users.get(username)
        if user and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
            # 创建会话
            session_id = SessionManager.create_session(user['id'])
            
            # 设置会话Cookie
            response = make_response(redirect(url_for('home')))
            response.set_cookie(
                'session_id',
                session_id,
                httponly=True,      # 防止XSS攻击
                secure=request.is_secure,  # 仅HTTPS环境设置
                samesite='Lax',     # CSRF防护
                max_age=1800        # 30分钟过期
            )
            
            # 添加安全日志
            print(f"用户 {username} 登录成功，会话ID: {session_id[:10]}...")
            return response
        else:
            return '''
            <h2>登录失败</h2>
            <p>用户名或密码错误</p>
            <a href="/login">重新登录</a>
            ''', 401
    
    # 显示登录表单
    return '''
    <h2>用户登录</h2>
    <form method="post">
        <p>
            <label>用户名: <input type="text" name="username" required></label>
        </p>
        <p>
            <label>密码: <input type="password" name="password" required></label>
        </p>
        <p>
            <input type="submit" value="登录">
        </p>
    </form>
    <p><a href="/">返回首页</a></p>
    '''


@app.route('/logout')
def logout():
    """登出接口"""
    session_id = request.cookies.get('session_id')
    if session_id:
        SessionManager.destroy_session(session_id)
    
    # 清除Cookie
    response = make_response(redirect(url_for('home')))
    response.delete_cookie('session_id')
    
    return response


@app.route('/profile')
@require_authentication
def profile():
    """个人资料页面（需要认证）"""
    user = request.current_user
    session = request.session
    
    return f'''
    <h2>个人资料</h2>
    <p>用户名: {user['username']}</p>
    <p>邮箱: {user['email']}</p>
    <p>用户ID: {user['id']}</p>
    <hr>
    <h3>会话信息</h3>
    <p>会话创建时间: {session['created_at'].strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>最后访问时间: {session['last_accessed'].strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>IP地址: {session['ip_address']}</p>
    <p><a href="/">返回首页</a></p>
    '''


@app.route('/api/session/check')
def api_session_check():
    """API接口：检查会话状态"""
    session_id = request.cookies.get('session_id')
    session = SessionManager.get_session(session_id) if session_id else None
    
    if session:
        user = SessionManager.get_user_by_id(session['user_id'])
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            },
            'session': {
                'created_at': session['created_at'].isoformat(),
                'last_accessed': session['last_accessed'].isoformat()
            }
        })
    else:
        return jsonify({
            'authenticated': False
        }), 401


@app.route('/api/protected')
@require_authentication
def api_protected():
    """受保护的API端点"""
    user = request.current_user
    
    return jsonify({
        'message': '这是受保护的资源',
        'user': {
            'id': user['id'],
            'username': user['username']
        }
    })


@app.route('/admin')
@require_authentication
def admin():
    """管理员页面"""
    user = request.current_user
    
    # 检查是否为管理员
    if user['username'] != 'admin':
        return '<h2>权限不足</h2><p>此页面仅限管理员访问</p>', 403
    
    return f'''
    <h2>管理员面板</h2>
    <p>欢迎管理员 {user['username']}</p>
    <p>这里是管理员专用区域</p>
    <p><a href="/">返回首页</a></p>
    '''


# 会话管理API
@app.route('/api/admin/sessions')
@require_authentication
def api_list_sessions():
    """API接口：列出所有活动会话（管理员专用）"""
    user = request.current_user
    
    # 检查管理员权限
    if user['username'] != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    # 返回会话列表（隐藏敏感信息）
    session_list = []
    for session_id, session_data in sessions.items():
        user_info = SessionManager.get_user_by_id(session_data['user_id'])
        session_list.append({
            'session_id': session_id[:10] + '...',  # 隐藏完整会话ID
            'user': {
                'id': user_info['id'],
                'username': user_info['username']
            },
            'created_at': session_data['created_at'].isoformat(),
            'last_accessed': session_data['last_accessed'].isoformat(),
            'ip_address': session_data['ip_address']
        })
    
    return jsonify({
        'sessions': session_list,
        'total': len(session_list)
    })


@app.route('/api/admin/sessions/<session_id>/revoke', methods=['POST'])
@require_authentication
def api_revoke_session(session_id):
    """API接口：撤销指定会话（管理员专用）"""
    user = request.current_user
    
    # 检查管理员权限
    if user['username'] != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    # 查找完整会话ID（因为我们只显示了部分）
    full_session_id = None
    for sid in sessions.keys():
        if sid.startswith(session_id.replace('...', '')):
            full_session_id = sid
            break
    
    if full_session_id and SessionManager.destroy_session(full_session_id):
        return jsonify({'success': True, 'message': '会话已撤销'})
    else:
        return jsonify({'error': '会话不存在'}), 404


def cleanup_expired_sessions():
    """清理过期会话的后台任务"""
    now = datetime.now()
    expired_sessions = [
        sid for sid, session in sessions.items()
        if now - session['last_accessed'] > timedelta(minutes=30)
    ]
    
    for sid in expired_sessions:
        del sessions[sid]
    
    if expired_sessions:
        print(f"清理了 {len(expired_sessions)} 个过期会话")


# 定时清理过期会话（简化版，实际应使用定时任务）
@app.before_request
def before_request():
    """在每个请求前清理过期会话"""
    if len(sessions) > 100:  # 当会话数量较多时才清理
        cleanup_expired_sessions()


if __name__ == '__main__':
    print("启动会话管理服务器...")
    print("访问 http://localhost:5000 查看演示")
    app.run(debug=True, port=5000)