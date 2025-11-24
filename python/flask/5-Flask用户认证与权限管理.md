# 第五章 Flask用户认证与权限管理

## 5.1 认证基础

用户认证是Web应用安全的重要组成部分，确保只有授权用户才能访问特定资源。

### Flask-Login扩展
Flask-Login是处理用户会话管理的流行扩展。

### 安装依赖
```bash
pip install Flask-Login
```

## 5.2 用户模型

首先需要创建一个符合Flask-Login要求的用户模型。

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
```

## 5.3 Flask-Login配置

### 初始化扩展
```python
from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 初始化数据库
db.init_app(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 设置登录视图
login_manager.login_message = '请先登录访问此页面'

@login_manager.user_loader
def load_user(user_id):
    """加载用户回调函数"""
    return User.query.get(int(user_id))
```

## 5.4 登录功能

### 登录表单
```python
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        # 验证用户和密码
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('登录成功!')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')
```

### 登录模板
```html
<!-- templates/login.html -->
{% extends "base.html" %}

{% block content %}
<h2>用户登录</h2>

{% with messages = get_flashed_messages() %}
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-info">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

<form method="post">
    <div class="form-group">
        <label>用户名:</label>
        <input type="text" name="username" class="form-control" required>
    </div>
    <div class="form-group">
        <label>密码:</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    <div class="form-check">
        <input type="checkbox" name="remember" class="form-check-input">
        <label class="form-check-label">记住我</label>
    </div>
    <button type="submit" class="btn btn-primary">登录</button>
</form>
{% endblock %}
```

## 5.5 注册功能

### 注册视图
```python
from flask_login import logout_user

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('register'))
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return redirect(url_for('register'))
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    
    return render_template('register.html')
```

## 5.6 登出功能

```python
@app.route('/logout')
def logout():
    logout_user()
    flash('您已成功登出')
    return redirect(url_for('index'))
```

## 5.7 权限控制

### 装饰器保护视图
```python
from flask_login import login_required, current_user

@app.route('/profile')
@login_required  # 需要登录才能访问
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/admin')
@login_required
def admin():
    # 检查用户权限
    if not current_user.is_admin:
        flash('您没有访问此页面的权限')
        return redirect(url_for('index'))
    return render_template('admin.html')
```

### 自定义权限装饰器
```python
from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # 禁止访问
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return '管理员仪表板'
```

## 5.8 会话管理

### 配置会话
```python
# 在应用配置中设置会话相关参数
app.config['PERMANENT_SESSION_LIFETIME'] = 30 * 60  # 30分钟
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS环境下使用
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止XSS攻击
```

### 用户属性
```python
# 在User模型中添加更多属性
class User(UserMixin, db.Model):
    # ... 其他字段 ...
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Flask-Login要求的方法
    def is_active(self):
        return self.is_active
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True
```

## 5.9 密码重置

### 忘记密码功能
```python
from itsdangerous import URLSafeTimedSerializer
import hashlib

# 配置密钥
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SECURITY_PASSWORD_SALT'] = 'your-password-salt'

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = generate_reset_token(email)
            # 这里应该发送邮件给用户
            flash('密码重置链接已发送到您的邮箱')
        else:
            flash('邮箱地址不存在')
    
    return render_template('reset_password_request.html')
```

## 5.10 总结

本章详细介绍了Flask中的用户认证和权限管理，包括Flask-Login的使用、用户模型设计、登录/注册/登出功能实现、权限控制装饰器、会话管理和密码重置功能。这些是构建安全Web应用的关键组件。下一章我们将学习RESTful API开发。