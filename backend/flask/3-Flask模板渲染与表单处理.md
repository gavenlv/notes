# 第三章 Flask模板渲染与表单处理

## 3.1 模板基础

Flask使用Jinja2作为模板引擎，它可以将Python代码与HTML代码分离，使前端开发更加清晰。

### 模板配置
默认情况下，Flask会在`templates`文件夹中查找模板文件。

### 基本模板渲染
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='首页', name='张三')
```

### 模板语法
在模板中使用变量和控制结构：
```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Hello {{ name }}!</h1>
    
    <!-- 条件语句 -->
    {% if name %}
        <p>欢迎回来，{{ name }}!</p>
    {% else %}
        <p>请先登录</p>
    {% endif %}
    
    <!-- 循环语句 -->
    <ul>
    {% for item in ['苹果', '香蕉', '橙子'] %}
        <li>{{ item }}</li>
    {% endfor %}
    </ul>
</body>
</html>
```

## 3.2 模板继承

模板继承可以避免重复代码，提高维护性。

### 基础模板
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    <div id="content">
        {% block content %}{% endblock %}
    </div>
    
    <div id="footer">
        {% block footer %}
            &copy; Copyright 2023 by <a href="/about">我们</a>.
        {% endblock %}
    </div>
</body>
</html>
```

### 子模板
```html
<!-- templates/page.html -->
{% extends "base.html" %}

{% block title %}页面标题{% endblock %}

{% block content %}
    <h1>这是页面内容</h1>
    <p>这里是具体内容...</p>
{% endblock %}
```

## 3.3 表单处理

Web应用经常需要处理用户提交的表单数据。

### GET和POST方法
```python
from flask import request

@app.route('/form', methods=['GET', 'POST'])
def form_handler():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form['username']
        email = request.form['email']
        return f'用户名: {username}, 邮箱: {email}'
    
    # 显示表单
    return '''
        <form method="post">
            <p><input type="text" name="username" placeholder="用户名"></p>
            <p><input type="email" name="email" placeholder="邮箱"></p>
            <p><input type="submit" value="提交"></p>
        </form>
    '''
```

### 表单验证
```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 简单验证
        if len(username) < 3:
            error = '用户名至少3个字符'
        elif len(password) < 6:
            error = '密码至少6个字符'
        else:
            # 处理注册逻辑
            return '注册成功!'
    
    return render_template('register.html', error=error)
```

对应的模板文件：
```html
<!-- templates/register.html -->
{% extends "base.html" %}

{% block content %}
    <h1>用户注册</h1>
    
    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
    
    <form method="post">
        <p>
            <label>用户名:</label>
            <input type="text" name="username" required>
        </p>
        <p>
            <label>密码:</label>
            <input type="password" name="password" required>
        </p>
        <p>
            <input type="submit" value="注册">
        </p>
    </form>
{% endblock %}
```

## 3.4 文件上传

处理文件上传是Web应用的常见需求。

### HTML表单
```html
<!-- templates/upload.html -->
<form method="post" enctype="multipart/form-data">
    <p><input type="file" name="file"></p>
    <p><input type="submit" value="上传"></p>
</form>
```

### Flask处理
```python
import os
from werkzeug.utils import secure_filename

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 检查是否有文件
        if 'file' not in request.files:
            return '没有选择文件'
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return '没有选择文件'
        
        # 保存文件
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return '文件上传成功'
    
    return render_template('upload.html')
```

## 3.5 消息闪现(Flashing)

Flask提供了一个消息闪现系统，可以在请求之间传递消息。

```python
from flask import flash, get_flashed_messages

@app.route('/flash')
def flash_message():
    flash('这是一条闪现消息!')
    return render_template('flash_demo.html')

@app.route('/show_flash')
def show_flash():
    messages = get_flashed_messages()
    return render_template('show_flash.html', messages=messages)
```

模板中显示闪现消息：
```html
<!-- templates/show_flash.html -->
{% with messages = get_flashed_messages() %}
    {% if messages %}
        <ul>
        {% for message in messages %}
            <li>{{ message }}</li>
        {% endfor %}
        </ul>
    {% endif %}
{% endwith %}
```

## 3.6 总结

本章介绍了Flask的模板渲染机制和表单处理方法，包括Jinja2模板语法、模板继承、表单数据获取与验证、文件上传以及消息闪现等功能。这些都是构建交互式Web应用的重要组成部分。下一章我们将学习数据库集成。