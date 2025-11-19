# 第二章 Flask路由与视图函数

## 2.1 路由基础

路由是Web应用中URL与处理函数之间的映射关系。在Flask中，我们使用装饰器`@app.route()`来定义路由。

### 基本路由定义
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '首页'

@app.route('/about')
def about():
    return '关于我们'
```

### HTTP方法限制
默认情况下，路由只接受GET请求。可以通过methods参数指定允许的HTTP方法：
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return '处理登录表单'
    else:
        return '显示登录表单'
```

## 2.2 动态路由

动态路由允许我们在URL中使用变量部分。

### 基本变量规则
```python
@app.route('/user/<username>')
def show_user_profile(username):
    return f'用户 {username}'
```

### 变量转换器
Flask支持多种变量转换器：
- string: 接受任何不带斜杠的文本（默认）
- int: 接受整数
- float: 接受浮点数
- path: 接受带斜杠的文本
- uuid: 接受UUID字符串

```python
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'文章ID: {post_id}'

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    return f'子路径: {subpath}'
```

## 2.3 视图函数

视图函数是处理请求并返回响应的函数。

### 返回值类型
视图函数可以返回多种类型的值：
```python
# 字符串
@app.route('/')
def index():
    return 'Hello World'

# 元组(响应内容, 状态码, 头部信息)
@app.route('/error')
def error():
    return '错误页面', 404

# JSON响应
from flask import jsonify

@app.route('/api/data')
def get_data():
    return jsonify({'name': '张三', 'age': 25})
```

### 请求对象
通过request对象可以获取请求信息：
```python
from flask import request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return f'用户名: {username}'
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    '''
```

## 2.4 URL构建

使用`url_for()`函数可以生成URL：
```python
from flask import url_for

@app.route('/')
def index():
    # 生成其他视图函数的URL
    login_url = url_for('login')
    user_url = url_for('show_user_profile', username='john')
    return f'登录链接: {login_url}<br>用户链接: {user_url}'
```

## 2.5 蓝图(Blueprint)

对于大型应用，可以使用蓝图来组织路由：
```python
from flask import Blueprint

# 创建蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_index():
    return '管理员面板'

@admin_bp.route('/users')
def admin_users():
    return '用户管理'

# 注册蓝图
app.register_blueprint(admin_bp)
```

## 2.6 错误处理

自定义错误页面：
```python
@app.errorhandler(404)
def not_found(error):
    return '页面不存在', 404

@app.errorhandler(500)
def internal_error(error):
    return '服务器内部错误', 500
```

## 2.7 总结

本章详细介绍了Flask的路由机制和视图函数，包括动态路由、HTTP方法处理、请求对象使用、URL构建以及蓝图的使用。这些是构建Web应用的基础知识。下一章我们将学习模板渲染和表单处理。