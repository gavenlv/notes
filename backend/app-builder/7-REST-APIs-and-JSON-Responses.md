# 第七章：REST APIs 和 JSON 响应

在现代Web应用程序开发中，RESTful API已成为标准做法。Flask App-Builder 提供了强大的支持来创建 REST API端点，使您的应用能够与其他服务或前端框架（如React、Vue.js等）进行交互。

## 目录
1. [API基础概念](#api基础概念)
2. [创建API端点](#创建api端点)
3. [数据序列化](#数据序列化)
4. [请求验证](#请求验证)
5. [错误处理](#错误处理)
6. [API安全性](#api安全性)
7. [完整示例](#完整示例)
8. [测试API](#测试api)
9. [最佳实践](#最佳实践)

## API基础概念

### 什么是REST API？
REST (Representational State Transfer) 是一种软件架构风格，它定义了一组约束条件和原则用于创建Web服务。RESTful API遵循这些原则，具有以下特点：
- **无状态性**：每个请求都包含处理该请求所需的所有信息
- **客户端-服务器分离**：关注点分离，提高可移植性
- **统一接口**：使用标准HTTP方法（GET, POST, PUT, DELETE）
- **可缓存性**：响应可以被缓存以提高性能

### HTTP方法映射
| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 获取资源 | `GET /api/users/1` |
| POST | 创建资源 | `POST /api/users` |
| PUT | 更新资源 | `PUT /api/users/1` |
| DELETE | 删除资源 | `DELETE /api/users/1` |

## 创建API端点

### 使用BaseAPIView
Flask App-Builder提供了`BaseAPIView`类专门用于创建API端点：

```python
from flask_appbuilder.api import BaseApi, expose
from flask import request, jsonify
from .models import Contact

class ContactApi(BaseApi):
    resource_name = 'contact'
    
    @expose('/<int:id>', methods=['GET'])
    def get_contact(self, id):
        """获取单个联系人"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        return self.response(
            200,
            result={
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone
            }
        )
    
    @expose('/', methods=['GET'])
    def get_contacts(self):
        """获取所有联系人"""
        contacts = self.appbuilder.get_session.query(Contact).all()
        result = []
        for contact in contacts:
            result.append({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone
            })
        
        return self.response(200, result=result)
    
    @expose('/', methods=['POST'])
    def create_contact(self):
        """创建新联系人"""
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('name') or not data.get('email'):
            return self.response_400(message='Name and email are required')
        
        contact = Contact()
        contact.name = data['name']
        contact.email = data['email']
        contact.phone = data.get('phone', '')
        
        self.appbuilder.get_session.add(contact)
        self.appbuilder.get_session.commit()
        
        return self.response(
            201,
            result={
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone
            },
            message='Contact created successfully'
        )

# 注册API
appbuilder.add_api(ContactApi)
```

### 使用ModelRestApi
对于简单的CRUD操作，Flask App-Builder还提供了`ModelRestApi`类：

```python
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Contact

class ContactModelApi(ModelRestApi):
    resource_name = 'contact_model'
    datamodel = SQLAInterface(Contact)
    
    # 定义允许的字段
    allow_columns = ['name', 'email', 'phone']
    
    # 定义搜索字段
    search_columns = ['name', 'email']

# 注册API
appbuilder.add_api(ContactModelApi)
```

## 数据序列化

### 自定义序列化器
为了更好地控制API响应的数据格式，我们可以创建自定义序列化器：

```python
from marshmallow import Schema, fields

class ContactSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str()
    created_on = fields.DateTime(dump_only=True)
    changed_on = fields.DateTime(dump_only=True)

class ContactApiWithSchema(BaseApi):
    resource_name = 'contact_schema'
    contact_schema = ContactSchema()
    
    @expose('/<int:id>', methods=['GET'])
    def get_contact(self, id):
        """获取单个联系人（使用序列化器）"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        result = self.contact_schema.dump(contact)
        return self.response(200, result=result)
```

## 请求验证

### 使用Marshmallow验证
Marshmallow是一个强大的序列化/反序列化库，非常适合用于API请求验证：

```python
from marshmallow import Schema, fields, ValidationError

class ContactCreateSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x) > 0)
    email = fields.Email(required=True)
    phone = fields.Str()

class ContactUpdateSchema(Schema):
    name = fields.Str(validate=lambda x: len(x) > 0)
    email = fields.Email()
    phone = fields.Str()

class ValidatedContactApi(BaseApi):
    resource_name = 'validated_contact'
    create_schema = ContactCreateSchema()
    update_schema = ContactUpdateSchema()
    
    @expose('/', methods=['POST'])
    def create_contact(self):
        """创建联系人（带验证）"""
        try:
            data = self.create_schema.load(request.get_json())
        except ValidationError as err:
            return self.response_400(message='Validation Error', errors=err.messages)
        
        contact = Contact(**data)
        self.appbuilder.get_session.add(contact)
        self.appbuilder.get_session.commit()
        
        result = self.create_schema.dump(contact)
        return self.response(201, result=result, message='Contact created')
    
    @expose('/<int:id>', methods=['PUT'])
    def update_contact(self, id):
        """更新联系人（带验证）"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        try:
            data = self.update_schema.load(request.get_json(), partial=True)
        except ValidationError as err:
            return self.response_400(message='Validation Error', errors=err.messages)
        
        # 更新字段
        for key, value in data.items():
            setattr(contact, key, value)
        
        self.appbuilder.get_session.commit()
        
        result = self.update_schema.dump(contact)
        return self.response(200, result=result, message='Contact updated')
```

## 错误处理

### 统一错误响应格式
良好的API应该有一致的错误响应格式：

```python
from flask_appbuilder.api import BaseApi

class ApiWithErrorHandling(BaseApi):
    resource_name = 'error_handling'
    
    def response_404(self, message='Resource not found'):
        """404错误响应"""
        return self.response(404, message=message)
    
    def response_400(self, message='Bad Request', errors=None):
        """400错误响应"""
        response = {'message': message}
        if errors:
            response['errors'] = errors
        return self.response(400, **response)
    
    def response_500(self, message='Internal Server Error'):
        """500错误响应"""
        return self.response(500, message=message)
    
    @expose('/protected', methods=['GET'])
    @permission_name('can_access_protected')
    def protected_endpoint(self):
        """受保护的端点"""
        try:
            # 可能出错的操作
            result = self.perform_operation()
            return self.response(200, result=result)
        except Exception as e:
            self.log.exception("Error in protected endpoint")
            return self.response_500('An error occurred while processing your request')
```

## API安全性

### 认证和授权
确保API端点的安全性是至关重要的：

```python
from flask_appbuilder.api import BaseApi
from flask_appbuilder.security.decorators import protect

class SecureApi(BaseApi):
    resource_name = 'secure'
    
    @expose('/data', methods=['GET'])
    @protect()
    def get_protected_data(self):
        """需要认证才能访问的数据"""
        user = self.appbuilder.sm.current_user
        return self.response(
            200,
            result={'user': user.username, 'data': 'sensitive information'}
        )
    
    @expose('/admin', methods=['GET'])
    @protect()
    @permission_name('can_access_admin_api')
    def admin_endpoint(self):
        """需要特定权限才能访问的端点"""
        return self.response(200, result={'message': 'admin data'})
```

### API密钥认证
对于第三方集成，可以实现API密钥认证：

```python
from flask import request
from flask_appbuilder.api import BaseApi

class ApiKeyProtectedApi(BaseApi):
    resource_name = 'apikey'
    
    def check_api_key(self):
        """检查API密钥"""
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False
        
        # 在实际应用中，应该查询数据库验证API密钥
        valid_keys = ['your-secret-api-key']
        return api_key in valid_keys
    
    def before_request(self, method_name, **kwargs):
        """在每个请求前执行"""
        if not self.check_api_key():
            return self.response_401()
        return super().before_request(method_name, **kwargs)
    
    @expose('/data', methods=['GET'])
    def get_data(self):
        """受API密钥保护的数据端点"""
        return self.response(200, result={'data': 'protected information'})
```

## 完整示例

让我们创建一个完整的联系人管理API示例：

### 项目结构
```
chapter7/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── api.py
│   └── schemas.py
├── config.py
└── run.py
```

### 模型定义 (models.py)
```python
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String

class Contact(AuditMixin, Model):
    __tablename__ = 'contact'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50))
    
    def __repr__(self):
        return self.name
```

### 序列化器 (schemas.py)
```python
from marshmallow import Schema, fields

class ContactSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str()
    created_on = fields.DateTime(dump_only=True)
    changed_on = fields.DateTime(dump_only=True)

class ContactCreateSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str()

class ContactUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    phone = fields.Str()
```

### API实现 (api.py)
```python
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import request
from marshmallow import ValidationError
from .models import Contact
from .schemas import ContactSchema, ContactCreateSchema, ContactUpdateSchema

class ContactApi(BaseApi):
    resource_name = 'contacts'
    contact_schema = ContactSchema()
    create_schema = ContactCreateSchema()
    update_schema = ContactUpdateSchema()
    
    @expose('/', methods=['GET'])
    def get_list(self):
        """获取联系人列表"""
        contacts = self.appbuilder.get_session.query(Contact).all()
        result = self.contact_schema.dump(contacts, many=True)
        return self.response(200, result=result)
    
    @expose('/<int:id>', methods=['GET'])
    def get(self, id):
        """获取单个联系人"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        result = self.contact_schema.dump(contact)
        return self.response(200, result=result)
    
    @expose('/', methods=['POST'])
    def create(self):
        """创建联系人"""
        try:
            data = self.create_schema.load(request.get_json())
        except ValidationError as err:
            return self.response_400(errors=err.messages)
        
        contact = Contact(**data)
        self.appbuilder.get_session.add(contact)
        self.appbuilder.get_session.commit()
        
        result = self.contact_schema.dump(contact)
        return self.response(201, result=result, message='Contact created')
    
    @expose('/<int:id>', methods=['PUT'])
    def update(self, id):
        """更新联系人"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        try:
            data = self.update_schema.load(request.get_json(), partial=True)
        except ValidationError as err:
            return self.response_400(errors=err.messages)
        
        for key, value in data.items():
            setattr(contact, key, value)
        
        self.appbuilder.get_session.commit()
        
        result = self.contact_schema.dump(contact)
        return self.response(200, result=result, message='Contact updated')
    
    @expose('/<int:id>', methods=['DELETE'])
    def delete(self, id):
        """删除联系人"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        self.appbuilder.get_session.delete(contact)
        self.appbuilder.get_session.commit()
        
        return self.response(200, message='Contact deleted')

# 注册API
# appbuilder.add_api(ContactApi)
```

### 应用初始化 (__init__.py)
```python
import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_appbuilder.api import Api

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 创建API
api = Api(app)
from . import api
appbuilder.add_api(api.ContactApi)

# 创建表
db.create_all()

# 添加初始数据
from .models import Contact
if not db.session.query(Contact).first():
    contact = Contact()
    contact.name = "John Doe"
    contact.email = "john@example.com"
    contact.phone = "123-456-7890"
    db.session.add(contact)
    db.session.commit()
```

### 配置文件 (config.py)
```python
import os

# 数据库配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 安全配置
SECRET_KEY = 'your-secret-key-here'
WTF_CSRF_ENABLED = True

# 应用配置
APP_NAME = "Flask App-Builder REST API Demo"
```

### 运行文件 (run.py)
```python
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

## 测试API

### 使用curl测试
```bash
# 获取所有联系人
curl -X GET http://localhost:8080/api/v1/contacts/

# 获取单个联系人
curl -X GET http://localhost:8080/api/v1/contacts/1

# 创建新联系人
curl -X POST http://localhost:8080/api/v1/contacts/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Smith","email":"jane@example.com","phone":"098-765-4321"}'

# 更新联系人
curl -X PUT http://localhost:8080/api/v1/contacts/1 \
  -H "Content-Type: application/json" \
  -d '{"phone":"111-222-3333"}'

# 删除联系人
curl -X DELETE http://localhost:8080/api/v1/contacts/1
```

### 使用Python测试
```python
import requests
import json

BASE_URL = 'http://localhost:8080/api/v1'

def test_api():
    # 获取所有联系人
    response = requests.get(f'{BASE_URL}/contacts/')
    print("GET /contacts/:", response.status_code, response.json())
    
    # 创建新联系人
    new_contact = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '555-1234'
    }
    response = requests.post(
        f'{BASE_URL}/contacts/',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(new_contact)
    )
    print("POST /contacts/:", response.status_code, response.json())
    
    # 获取刚创建的联系人
    contact_id = response.json()['result']['id']
    response = requests.get(f'{BASE_URL}/contacts/{contact_id}')
    print("GET /contacts/{id}:", response.status_code, response.json())

if __name__ == '__main__':
    test_api()
```

## 最佳实践

### 1. 版本控制
始终对API进行版本控制：
```python
class ContactApiV1(BaseApi):
    resource_name = 'v1/contacts'

class ContactApiV2(BaseApi):
    resource_name = 'v2/contacts'
```

### 2. 分页处理
对于大量数据，实现分页：
```python
@expose('/', methods=['GET'])
def get_list(self):
    """获取联系人列表（带分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    contacts = self.appbuilder.get_session.query(Contact)\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    result = self.contact_schema.dump(contacts.items, many=True)
    
    return self.response(
        200,
        result=result,
        pagination={
            'page': page,
            'per_page': per_page,
            'total': contacts.total,
            'pages': contacts.pages
        }
    )
```

### 3. 缓存策略
对不经常变化的数据实施缓存：
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@expose('/stats', methods=['GET'])
@cache.cached(timeout=300)  # 缓存5分钟
def get_stats(self):
    """获取统计信息"""
    total_contacts = self.appbuilder.get_session.query(Contact).count()
    return self.response(200, result={'total_contacts': total_contacts})
```

### 4. 日志记录
记录重要操作：
```python
import logging

logger = logging.getLogger(__name__)

@expose('/', methods=['POST'])
def create(self):
    """创建联系人（带日志）"""
    try:
        # ... 创建逻辑 ...
        logger.info(f"Contact created: {contact.id}")
        return self.response(201, result=result, message='Contact created')
    except Exception as e:
        logger.error(f"Failed to create contact: {str(e)}")
        return self.response_500()
```

通过本章的学习，您已经掌握了如何在Flask App-Builder中创建RESTful API，包括端点设计、数据序列化、请求验证、错误处理和安全保护等方面的知识。这些技能将帮助您构建更加强大和灵活的Web应用程序。