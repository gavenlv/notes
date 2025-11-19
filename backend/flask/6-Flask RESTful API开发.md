# 第六章 Flask RESTful API开发

## 6.1 RESTful API基础

REST(Representational State Transfer)是一种软件架构风格，用于设计网络应用程序的API。

### REST原则
- **无状态**: 每个请求都包含处理该请求所需的所有信息
- **统一接口**: 使用标准HTTP方法(GET, POST, PUT, DELETE)
- **资源导向**: 将数据视为资源，通过URI标识
- **可缓存**: 响应可以被缓存以提高性能

### HTTP方法对应操作
- GET: 获取资源
- POST: 创建资源
- PUT: 更新资源(完整更新)
- PATCH: 更新资源(部分更新)
- DELETE: 删除资源

## 6.2 Flask-RESTful扩展

Flask-RESTful是构建REST APIs的Flask扩展，提供了便捷的工具。

### 安装依赖
```bash
pip install Flask-RESTful
```

### 基本使用
```python
from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)
```

## 6.3 资源定义

### 基本资源类
```python
from flask_restful import Resource, reqparse
from flask import jsonify

class UserResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, help='用户名不能为空')
        self.parser.add_argument('email', type=str, required=True, help='邮箱不能为空')
    
    def get(self, user_id=None):
        """获取用户信息"""
        if user_id:
            # 获取单个用户
            user = User.query.get_or_404(user_id)
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        else:
            # 获取所有用户
            users = User.query.all()
            return [{
                'id': user.id,
                'username': user.username,
                'email': user.email
            } for user in users]
    
    def post(self):
        """创建新用户"""
        args = self.parser.parse_args()
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=args['username']).first():
            return {'message': '用户名已存在'}, 400
        
        user = User(username=args['username'], email=args['email'])
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }, 201
    
    def put(self, user_id):
        """更新用户信息"""
        user = User.query.get_or_404(user_id)
        args = self.parser.parse_args()
        
        user.username = args['username']
        user.email = args['email']
        db.session.commit()
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    
    def delete(self, user_id):
        """删除用户"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': '用户删除成功'}, 204

# 注册资源
api.add_resource(UserResource, '/api/users', '/api/users/<int:user_id>')
```

## 6.4 输入验证

### 使用reqparse进行参数验证
```python
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, help='用户名是必需的')
parser.add_argument('email', type=str, required=True, help='邮箱是必需的')
parser.add_argument('age', type=int, required=False, default=0)
parser.add_argument('is_active', type=bool, required=False, default=True)

class UserCreate(Resource):
    def post(self):
        args = parser.parse_args()
        # 参数验证通过后处理业务逻辑
        return {'message': '用户创建成功', 'data': args}
```

### 自定义验证
```python
def email_validator(value):
    """自定义邮箱验证函数"""
    if '@' not in value:
        raise ValueError("邮箱格式不正确")
    return value

parser.add_argument('email', type=email_validator, required=True)
```

## 6.5 输出字段格式化

### 使用fields定义输出格式
```python
from flask_restful import fields, marshal_with

# 定义输出字段格式
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'uri': fields.Url('user', absolute=True)
}

class UserListResource(Resource):
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return users
```

### 嵌套字段
```python
from flask_restful import fields

# 嵌套字段定义
post_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'author': fields.Nested({
        'id': fields.Integer,
        'username': fields.String
    })
}

class PostResource(Resource):
    @marshal_with(post_fields)
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        return post
```

## 6.6 错误处理

### 自定义错误消息
```python
from flask_restful import abort

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            abort(404, message=f"用户 {user_id} 不存在")
        return user

# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    return {'message': '资源未找到'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'message': '服务器内部错误'}, 500
```

## 6.7 认证与授权

### Token认证
```python
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return False
    g.current_user = User.query.get(data['id'])
    return True

class ProtectedResource(Resource):
    @auth.login_required
    def get(self):
        return {'message': f'Hello, {g.current_user.username}!'}

api.add_resource(ProtectedResource, '/api/protected')
```

### 生成Token
```python
@app.route('/api/token', methods=['POST'])
def get_token():
    # 验证用户名和密码
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        s = Serializer(app.config['SECRET_KEY'], expires_in=3600)
        return {'token': s.dumps({'id': user.id}).decode()}
    
    return {'message': '用户名或密码错误'}, 401
```

## 6.8 分页与过滤

### 实现分页
```python
from flask_restful import Resource, reqparse

class UserListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('per_page', type=int, default=10, choices=[10, 20, 50])
    
    def get(self):
        args = self.parser.parse_args()
        page = args['page']
        per_page = args['per_page']
        
        pagination = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = pagination.items
        return {
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email
            } for user in users],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
```

## 6.9 版本控制

### API版本管理
```python
# v1版本
api_v1 = Api(prefix='/api/v1')
api_v1.add_resource(UserResource, '/users')

# v2版本
api_v2 = Api(prefix='/api/v2')
api_v2.add_resource(UserResourceV2, '/users')

# 注册不同版本的API
api_v1.init_app(app)
api_v2.init_app(app)
```

## 6.10 测试RESTful API

### 使用unittest测试
```python
import unittest
from app import app, db

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        with app.app_context():
            db.drop_all()
    
    def test_get_users(self):
        response = self.app.get('/api/users')
        self.assertEqual(response.status_code, 200)
    
    def test_create_user(self):
        response = self.app.post('/api/users', 
                                json={'username': 'test', 'email': 'test@example.com'})
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
```

## 6.11 总结

本章详细介绍了如何使用Flask开发RESTful API，包括Flask-RESTful扩展的使用、资源定义、输入验证、输出格式化、错误处理、认证授权、分页过滤等功能。这些是构建现代化Web服务的重要技能。下一章我们将学习部署和性能优化。