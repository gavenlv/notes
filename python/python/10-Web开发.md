# 第10章：Web开发(Flask/Django)

> **学习时长**: 10-12小时  
> **难度**: ⭐⭐⭐⭐⭐  
> **前置知识**: 第1-9章

## 本章目标

学完本章后,你将能够:

- ✅ 使用Flask创建Web应用
- ✅ 理解路由与视图函数
- ✅ 使用模板引擎渲染页面
- ✅ 处理表单和文件上传
- ✅ 操作数据库(SQLite/MySQL)
- ✅ 实现RESTful API
- ✅ 了解Django框架基础

---

## 10.1 Flask入门

### 10.1.1 安装Flask

```bash
pip install flask
```

### 10.1.2 第一个Flask应用

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Flask!'

@app.route('/about')
def about():
    return 'About Page'

if __name__ == '__main__':
    app.run(debug=True)
```

运行:
```bash
python app.py
```

访问: `http://127.0.0.1:5000/`

---

## 10.2 路由与视图

### 10.2.1 基本路由

```python
from flask import Flask

app = Flask(__name__)

# 基本路由
@app.route('/')
def index():
    return 'Index Page'

# 动态路由
@app.route('/user/<username>')
def show_user(username):
    return f'User: {username}'

# 类型转换
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post ID: {post_id}'

# 多种类型
# <int:id>    整数
# <float:num> 浮点数
# <path:path> 路径(可包含/)
# <uuid:id>   UUID

# 多个HTTP方法
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'Processing login...'
    return 'Login form'
```

### 10.2.2 URL构建

```python
from flask import url_for, redirect

@app.route('/')
def index():
    return 'Index'

@app.route('/user/<name>')
def user(name):
    return f'User: {name}'

@app.route('/goto_user')
def goto_user():
    # 生成URL
    url = url_for('user', name='Alice')
    return redirect(url)  # 重定向
```

---

## 10.3 模板

### 10.3.1 渲染模板

项目结构:
```
app.py
templates/
    index.html
    user.html
```

**app.py**:
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
```

**templates/index.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Welcome to Flask!</h1>
    <p>This is the index page.</p>
</body>
</html>
```

**templates/user.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>User Profile</title>
</head>
<body>
    <h1>Hello, {{ name }}!</h1>
</body>
</html>
```

### 10.3.2 Jinja2模板语法

```html
<!-- 变量 -->
{{ variable }}

<!-- 条件 -->
{% if user %}
    <p>Hello, {{ user }}!</p>
{% else %}
    <p>Hello, Guest!</p>
{% endif %}

<!-- 循环 -->
<ul>
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
</ul>

<!-- 过滤器 -->
{{ name|upper }}         <!-- 转大写 -->
{{ text|truncate(20) }}  <!-- 截断 -->
{{ date|datetimeformat }} <!-- 格式化日期 -->

<!-- 继承 -->
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

<!-- child.html -->
{% extends "base.html" %}

{% block title %}Custom Title{% endblock %}

{% block content %}
    <h1>Page Content</h1>
{% endblock %}
```

---

## 10.4 表单处理

### 10.4.1 处理表单

```python
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 验证用户
        if username == 'admin' and password == 'password':
            return 'Login successful!'
        else:
            return 'Login failed!'
    
    return render_template('login.html')
```

**templates/login.html**:
```html
<!DOCTYPE html>
<html>
<body>
    <h1>Login</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>
```

### 10.4.2 文件上传

```python
from flask import Flask, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return f'File {filename} uploaded successfully!'
    
    return '''
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
    '''
```

---

## 10.5 数据库操作

### 10.5.1 使用SQLite

```python
from flask import Flask, g
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        db.commit()

@app.route('/users')
def users():
    db = get_db()
    cursor = db.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    
    db = get_db()
    db.execute('INSERT INTO users (username, email) VALUES (?, ?)',
               [username, email])
    db.commit()
    
    return redirect(url_for('users'))
```

### 10.5.2 使用Flask-SQLAlchemy

```bash
pip install flask-sqlalchemy
```

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

# 定义模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

# 创建表
with app.app_context():
    db.create_all()

# 添加用户
@app.route('/create_user/<username>/<email>')
def create_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return f'User {username} created!'

# 查询用户
@app.route('/users')
def get_users():
    users = User.query.all()
    return render_template('users.html', users=users)

# 查找特定用户
@app.route('/user/<username>')
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return f'User: {user.username}, Email: {user.email}'
    return 'User not found'

# 更新用户
@app.route('/update_user/<username>/<new_email>')
def update_user(username, new_email):
    user = User.query.filter_by(username=username).first()
    if user:
        user.email = new_email
        db.session.commit()
        return f'User {username} updated!'
    return 'User not found'

# 删除用户
@app.route('/delete_user/<username>')
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return f'User {username} deleted!'
    return 'User not found'
```

---

## 10.6 RESTful API

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# 模拟数据库
books = [
    {'id': 1, 'title': 'Python编程', 'author': '张三'},
    {'id': 2, 'title': '算法导论', 'author': '李四'}
]

# GET - 获取所有书籍
@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify(books)

# GET - 获取单本书
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404

# POST - 添加书籍
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = {
        'id': len(books) + 1,
        'title': data['title'],
        'author': data['author']
    }
    books.append(new_book)
    return jsonify(new_book), 201

# PUT - 更新书籍
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        data = request.get_json()
        book['title'] = data.get('title', book['title'])
        book['author'] = data.get('author', book['author'])
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404

# DELETE - 删除书籍
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    books = [b for b in books if b['id'] != book_id]
    return jsonify({'message': 'Book deleted'}), 200
```

测试API:
```bash
# GET所有书籍
curl http://localhost:5000/api/books

# POST添加书籍
curl -X POST http://localhost:5000/api/books \
     -H "Content-Type: application/json" \
     -d '{"title":"深度学习","author":"王五"}'

# PUT更新书籍
curl -X PUT http://localhost:5000/api/books/1 \
     -H "Content-Type: application/json" \
     -d '{"title":"Python高级编程"}'

# DELETE删除书籍
curl -X DELETE http://localhost:5000/api/books/1
```

---

## 10.7 实验:博客系统

```python
"""
简单博客系统
功能:
- 文章列表
- 文章详情
- 发布文章
- 评论
"""

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

# 模型
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 创建数据库
with app.app_context():
    db.create_all()

# 首页 - 文章列表
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# 文章详情
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# 发布文章
@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('new_post.html')

# 添加评论
@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    content = request.form['content']
    
    comment = Comment(content=content, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    
    return redirect(url_for('post_detail', post_id=post_id))

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 10.8 Django简介

### 10.8.1 安装Django

```bash
pip install django
```

### 10.8.2 创建项目

```bash
# 创建项目
django-admin startproject mysite

# 项目结构
mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        wsgi.py

# 运行开发服务器
cd mysite
python manage.py runserver
```

### 10.8.3 创建应用

```bash
python manage.py startapp blog

# 应用结构
blog/
    __init__.py
    admin.py
    apps.py
    models.py
    tests.py
    views.py
    migrations/
```

---

## 10.9 课后练习

### 练习1: Todo应用

创建待办事项应用:
- 添加任务
- 标记完成
- 删除任务

### 练习2: 用户认证

实现用户系统:
- 注册
- 登录
- 登出

### 练习3: API服务

创建天气API:
- 查询城市天气
- 历史天气记录
- JSON响应

---

## 10.10 本章小结

### Flask核心概念

```python
from flask import Flask, render_template, request

app = Flask(__name__)

# 路由
@app.route('/')
def index():
    return render_template('index.html')

# 动态路由
@app.route('/user/<name>')
def user(name):
    return f'User: {name}'

# 表单处理
@app.route('/form', methods=['POST'])
def form():
    data = request.form['field']
    return data

# 数据库
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
```

### 下一章预告

**第11章 - 数据分析与可视化**,将学习:
- 📊 Matplotlib绘图
- 📈 Seaborn统计可视化
- 🎨 Plotly交互图表
- 📉 数据可视化最佳实践

---

[← 上一章](./9-数据处理.md) | [返回目录](./README.md) | [下一章: 数据分析与可视化 →](./11-数据分析与可视化.md)
