# 第十五章：使用Flask-AppBuilder构建REST API

Flask-AppBuilder不仅是一个强大的管理界面框架，还提供了构建REST API的功能。通过FAB的API生成器，我们可以快速创建符合REST规范的API端点，而无需手动编写大量重复代码。本章将详细介绍如何使用Flask-AppBuilder构建和定制REST API。

## 目录
1. REST API概述
2. FAB API生成器基础
3. 创建基本API端点
4. 自定义API行为
5. API认证和授权
6. 数据序列化和验证
7. 分页和过滤
8. 错误处理和响应格式
9. API文档生成
10. 性能优化
11. 测试REST API
12. 完整API示例

## 1. REST API概述

### 什么是REST API？
REST（Representational State Transfer）是一种软件架构风格，用于设计网络应用程序的API。RESTful API遵循以下原则：
- **无状态性**：每个请求都包含处理该请求所需的所有信息
- **统一接口**：使用标准HTTP方法（GET、POST、PUT、DELETE等）
- **资源导向**：将数据视为资源，通过URI进行标识
- **可缓存性**：响应可以被缓存以提高性能

### REST成熟度模型
Leonard Richardson提出了REST成熟度模型，将REST API分为四个层次：
1. **Level 0**：单纯的HTTP协议传输，没有使用REST原则
2. **Level 1**：使用资源概念，但只有一个入口点
3. **Level 2**：使用多种HTTP动词和状态码
4. **Level 3**：支持超媒体驱动（HATEOAS）

## 2. FAB API生成器基础

### API生成器简介
Flask-AppBuilder提供了一个强大的API生成器，可以自动为模型创建RESTful端点。API生成器基于以下组件：
- **ModelRestApi**：用于创建模型的REST API
- **BaseApi**：用于创建自定义API端点
- **Marshmallow**：用于数据序列化和验证

### API生成器优势
- **自动生成CRUD操作**：自动创建增删改查端点
- **内置认证和授权**：与FAB的安全系统集成
- **数据验证**：自动验证请求数据
- **分页和排序**：内置分页和排序功能
- **过滤和搜索**：支持复杂的查询过滤

## 3. 创建基本API端点

### 使用ModelRestApi

```python
# api/product_api.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields
from ..models import Product

class ProductApi(ModelRestApi):
    resource_name = 'product'
    datamodel = SQLAInterface(Product)
    
    # 定义允许的操作
    allow_browser_login = True
    
    # 定义列表视图的字段
    list_columns = ['id', 'name', 'price', 'category.name']
    
    # 定义显示视图的字段
    show_columns = ['id', 'name', 'description', 'price', 'category.name', 'created_on']
    
    # 定义添加视图的字段
    add_columns = ['name', 'description', 'price', 'category']
    
    # 定义编辑视图的字段
    edit_columns = ['name', 'description', 'price', 'category']

# 注册API
appbuilder.add_api(ProductApi)
```

### 使用BaseApi创建自定义端点

```python
# api/custom_api.py
from flask_appbuilder.api import BaseApi
from flask_appbuilder import expose
from flask import request, jsonify
from ..models import Product

class CustomApi(BaseApi):
    resource_name = 'custom'
    
    @expose('/hello', methods=['GET'])
    def hello(self):
        """简单的问候端点"""
        return self.response(200, message="Hello, World!")
    
    @expose('/products/stats', methods=['GET'])
    def product_stats(self):
        """产品统计信息"""
        total_products = self.appbuilder.get_session.query(Product).count()
        avg_price = self.appbuilder.get_session.query(
            func.avg(Product.price)
        ).scalar() or 0
        
        return self.response(200, 
            total_products=total_products,
            average_price=float(avg_price)
        )

# 注册API
appbuilder.add_api(CustomApi)
```

## 4. 自定义API行为

### 覆盖默认方法

```python
# api/enhanced_product_api.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import request
from ..models import Product

class EnhancedProductApi(ModelRestApi):
    resource_name = 'enhanced-product'
    datamodel = SQLAInterface(Product)
    
    # 自定义获取列表的方法
    def get_list(self):
        """自定义列表获取逻辑"""
        # 添加额外的业务逻辑
        # 例如：只返回活跃的产品
        filters = self.datamodel.get_filters()
        filters.add_filter('is_active', self.datamodel.FilterEqual, True)
        
        return super().get_list(filters=filters)
    
    # 自定义创建方法
    def post(self):
        """自定义创建逻辑"""
        # 在创建之前添加业务逻辑
        data = request.get_json()
        data['created_by'] = self.get_user_id()
        
        return super().post()
    
    # 自定义更新方法
    def put(self, pk):
        """自定义更新逻辑"""
        # 添加审计日志
        self.log_action('update_product', {'product_id': pk})
        
        return super().put(pk)
```

### 添加自定义字段

```python
# api/product_schema.py
from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields, post_dump
from ..models import Product

class ProductSchema(BaseModelSchema):
    class Meta:
        model = Product
        load_instance = True
    
    # 添加计算字段
    discounted_price = fields.Method("get_discounted_price")
    
    def get_discounted_price(self, obj):
        """计算折扣价格"""
        if obj.price:
            return float(obj.price) * 0.9  # 10%折扣
        return 0

class ProductApiWithSchema(ModelRestApi):
    resource_name = 'product-schema'
    datamodel = SQLAInterface(Product)
    schemas = {
        'ProductSchema': ProductSchema
    }
```

## 5. API认证和授权

### JWT令牌认证

```python
# api/auth_api.py
from flask_appbuilder.api import BaseApi
from flask_appbuilder.security.decorators import authenticate
from flask_appbuilder.security.api import SecurityManager
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import request, jsonify

class AuthApi(BaseApi):
    resource_name = 'auth'
    
    @expose('/login', methods=['POST'])
    def login(self):
        """JWT登录端点"""
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        
        # 验证用户凭据
        user = self.appbuilder.sm.auth_user_db(username, password)
        if not user:
            return self.response_401(message="Invalid credentials")
        
        # 创建访问令牌
        access_token = create_access_token(identity=user.id)
        return self.response(200, access_token=access_token)
    
    @expose('/profile', methods=['GET'])
    @jwt_required()
    def profile(self):
        """获取用户资料"""
        current_user_id = get_jwt_identity()
        user = self.appbuilder.sm.get_user_by_id(current_user_id)
        
        if not user:
            return self.response_404(message="User not found")
        
        return self.response(200, 
            id=user.id,
            username=user.username,
            email=user.email
        )
```

### 基于角色的访问控制

```python
# api/protected_api.py
from flask_appbuilder.api import BaseApi
from flask_appbuilder.security.decorators import protect, has_access
from flask import request

class ProtectedApi(BaseApi):
    resource_name = 'protected'
    
    @expose('/admin-only', methods=['GET'])
    @protect()
    @has_access('can_admin')
    def admin_only(self):
        """仅管理员可访问"""
        return self.response(200, message="Admin access granted")
    
    @expose('/user-data', methods=['GET'])
    @protect()
    def user_data(self):
        """用户数据访问"""
        user = self.get_user()
        return self.response(200, 
            user_id=user.id,
            username=user.username
        )
```

## 6. 数据序列化和验证

### 使用Marshmallow进行数据验证

```python
# api/product_validation.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields, validate, validates_schema, ValidationError
from ..models import Product

class ProductValidationSchema(BaseModelSchema):
    class Meta:
        model = Product
        load_instance = True
        exclude = ('created_on', 'changed_on')
    
    # 字段验证
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Int(required=True, validate=validate.Range(min=0))
    description = fields.Str(validate=validate.Length(max=500))
    
    # 自定义验证
    @validates_schema
    def validate_price_range(self, data, **kwargs):
        """验证价格范围"""
        if 'price' in data and data['price'] > 1000000:
            raise ValidationError('Price cannot exceed 1,000,000', 'price')

class ValidatedProductApi(ModelRestApi):
    resource_name = 'validated-product'
    datamodel = SQLAInterface(Product)
    schemas = {
        'ProductValidationSchema': ProductValidationSchema
    }
    
    # 指定使用的schema
    add_model_schema = 'ProductValidationSchema'
    edit_model_schema = 'ProductValidationSchema'
```

### 嵌套对象序列化

```python
# api/nested_serialization.py
from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields
from ..models import Product, Category

class CategorySchema(BaseModelSchema):
    class Meta:
        model = Category
        load_instance = True

class ProductWithCategorySchema(BaseModelSchema):
    class Meta:
        model = Product
        load_instance = True
    
    # 嵌套序列化
    category = fields.Nested(CategorySchema)

class NestedProductApi(ModelRestApi):
    resource_name = 'nested-product'
    datamodel = SQLAInterface(Product)
    schemas = {
        'ProductWithCategorySchema': ProductWithCategorySchema
    }
    show_model_schema = 'ProductWithCategorySchema'
```

## 7. 分页和过滤

### 高级分页配置

```python
# api/paginated_api.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from ..models import Product

class PaginatedProductApi(ModelRestApi):
    resource_name = 'paginated-product'
    datamodel = SQLAInterface(Product)
    
    # 分页配置
    page_size = 20
    max_page_size = 100
    
    # 默认排序
    order_columns = ['id', 'name', 'price']
    order_direction = 'asc'
    
    # 允许的过滤字段
    search_columns = ['name', 'description', 'price', 'category.name']
```

### 自定义过滤器

```python
# api/custom_filters.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.filters import BaseFilter
from sqlalchemy import func
from ..models import Product

class PriceRangeFilter(BaseFilter):
    """价格范围过滤器"""
    name = "Price Range"
    arg_name = "price_range"
    
    def apply(self, query, value):
        min_price, max_price = map(int, value.split('-'))
        return query.filter(
            self.model.price >= min_price,
            self.model.price <= max_price
        )

class FilteredProductApi(ModelRestApi):
    resource_name = 'filtered-product'
    datamodel = SQLAInterface(Product)
    
    # 添加自定义过滤器
    filters = [
        PriceRangeFilter()
    ]
    
    # 允许的搜索字段
    search_columns = ['name', 'description', 'price']
```

## 8. 错误处理和响应格式

### 统一错误响应格式

```python
# api/error_handling.py
from flask_appbuilder.api import BaseApi
from flask import request
from werkzeug.exceptions import HTTPException
import logging

class ErrorHandlingApi(BaseApi):
    resource_name = 'error-handling'
    
    def handle_exception(self, e):
        """统一异常处理"""
        # 记录错误日志
        logging.error(f"API Error: {str(e)}", exc_info=True)
        
        # 处理HTTP异常
        if isinstance(e, HTTPException):
            return self.response(e.code, message=e.description)
        
        # 处理验证错误
        if hasattr(e, 'messages'):
            return self.response_422(message="Validation error", errors=e.messages)
        
        # 处理其他异常
        return self.response_500(message="Internal server error")
    
    @expose('/trigger-error', methods=['GET'])
    def trigger_error(self):
        """触发错误示例"""
        # 故意触发一个错误
        raise ValueError("This is a test error")
```

### 自定义响应格式

```python
# api/custom_response.py
from flask_appbuilder.api import BaseApi
from flask import jsonify
from datetime import datetime

class CustomResponseApi(BaseApi):
    resource_name = 'custom-response'
    
    def response(self, code, **kwargs):
        """自定义响应格式"""
        response_data = {
            'status': 'success' if 200 <= code < 400 else 'error',
            'code': code,
            'timestamp': datetime.utcnow().isoformat(),
            'data': kwargs
        }
        return jsonify(response_data), code
    
    @expose('/custom-data', methods=['GET'])
    def custom_data(self):
        """自定义数据响应"""
        return self.response(200, 
            message="Custom response format",
            items=[1, 2, 3, 4, 5]
        )
```

## 9. API文档生成

### 使用Swagger/OpenAPI

```python
# api/swagger_docs.py
from flask_appbuilder.api import BaseApi
from flask_appbuilder import expose
from flask_swagger_ui import get_swaggerui_blueprint

class DocumentedApi(BaseApi):
    resource_name = 'documented'
    
    @expose('/data', methods=['GET'])
    def get_data(self):
        """
        获取数据
        ---
        tags:
          - Documented API
        responses:
          200:
            description: 成功获取数据
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: string
        """
        return self.response(200, data=["item1", "item2", "item3"])
    
    @expose('/data', methods=['POST'])
    def create_data(self):
        """
        创建数据
        ---
        tags:
          - Documented API
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
        responses:
          201:
            description: 数据创建成功
        """
        return self.response(201, message="Data created")
```

### 集成Flasgger

```python
# app/__init__.py
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    # 初始化数据库
    db = SQLA(app)
    
    # 初始化Flask-AppBuilder
    appbuilder = AppBuilder(app, db.session)
    
    # 初始化Swagger
    swagger = Swagger(app)
    
    return app
```

## 10. 性能优化

### 查询优化

```python
# api/optimized_api.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy.orm import joinedload
from ..models import Product

class OptimizedProductApi(ModelRestApi):
    resource_name = 'optimized-product'
    datamodel = SQLAInterface(Product)
    
    # 预加载关联对象以避免N+1查询问题
    list_query_rel_fields = {
        'category': [['name'], ['asc']]
    }
    
    # 使用joinedload优化查询
    def get_list(self, **kwargs):
        query = self.datamodel.session.query(self.datamodel.obj)
        query = query.options(joinedload(Product.category))
        return super().get_list(query=query, **kwargs)
```

### 缓存策略

```python
# api/cached_api.py
from flask_appbuilder.api import BaseApi
from flask_caching import Cache
from flask import request

class CachedApi(BaseApi):
    resource_name = 'cached'
    
    def __init__(self):
        super().__init__()
        self.cache = Cache(self.appbuilder.get_app)
    
    @expose('/expensive-operation', methods=['GET'])
    def expensive_operation(self):
        """昂贵的操作，使用缓存"""
        cache_key = f"expensive_op_{request.args.get('param', '')}"
        
        # 尝试从缓存获取结果
        result = self.cache.get(cache_key)
        if result is None:
            # 执行昂贵的操作
            result = self.perform_expensive_operation()
            # 缓存结果（5分钟过期）
            self.cache.set(cache_key, result, timeout=300)
        
        return self.response(200, result=result)
    
    def perform_expensive_operation(self):
        """模拟昂贵的操作"""
        import time
        time.sleep(2)  # 模拟耗时操作
        return {"data": "expensive result", "timestamp": time.time()}
```

## 11. 测试REST API

### 单元测试

```python
# tests/test_product_api.py
import unittest
import json
from flask_appbuilder.tests.fixtures import BaseTestCase
from app import app, db
from app.models import Product, Category

class TestProductApi(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        # 创建测试数据
        self.category = Category(name="Test Category")
        db.session.add(self.category)
        db.session.commit()
        
        self.product = Product(
            name="Test Product",
            description="Test Description",
            price=100,
            category_id=self.category.id
        )
        db.session.add(self.product)
        db.session.commit()
    
    def test_get_products(self):
        """测试获取产品列表"""
        response = self.client.get('/api/v1/product/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertGreater(len(data['result']), 0)
    
    def test_create_product(self):
        """测试创建产品"""
        new_product = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 200,
            'category': self.category.id
        }
        
        response = self.client.post(
            '/api/v1/product/',
            data=json.dumps(new_product),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # 验证产品已创建
        product = db.session.query(Product).filter_by(name='New Product').first()
        self.assertIsNotNone(product)
        self.assertEqual(product.price, 200)
    
    def test_update_product(self):
        """测试更新产品"""
        update_data = {
            'name': 'Updated Product',
            'price': 150
        }
        
        response = self.client.put(
            f'/api/v1/product/{self.product.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 验证产品已更新
        updated_product = db.session.query(Product).get(self.product.id)
        self.assertEqual(updated_product.name, 'Updated Product')
        self.assertEqual(updated_product.price, 150)
    
    def test_delete_product(self):
        """测试删除产品"""
        response = self.client.delete(f'/api/v1/product/{self.product.id}')
        self.assertEqual(response.status_code, 200)
        
        # 验证产品已删除
        deleted_product = db.session.query(Product).get(self.product.id)
        self.assertIsNone(deleted_product)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```python
# tests/test_api_integration.py
import unittest
import json
from flask_appbuilder.tests.fixtures import BaseTestCase

class TestApiIntegration(BaseTestCase):
    
    def test_api_workflow(self):
        """测试完整的API工作流"""
        # 1. 创建类别
        category_data = {
            'name': 'Electronics',
            'description': 'Electronic devices'
        }
        
        response = self.client.post(
            '/api/v1/category/',
            data=json.dumps(category_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        category_result = json.loads(response.data)
        category_id = category_result['id']
        
        # 2. 创建产品
        product_data = {
            'name': 'Smartphone',
            'description': 'Latest smartphone',
            'price': 69900,  # 以分为单位
            'category': category_id
        }
        
        response = self.client.post(
            '/api/v1/product/',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        product_result = json.loads(response.data)
        product_id = product_result['id']
        
        # 3. 获取产品详情
        response = self.client.get(f'/api/v1/product/{product_id}')
        self.assertEqual(response.status_code, 200)
        
        # 4. 更新产品
        update_data = {
            'price': 59900
        }
        
        response = self.client.put(
            f'/api/v1/product/{product_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 5. 验证更新
        response = self.client.get(f'/api/v1/product/{product_id}')
        result = json.loads(response.data)
        self.assertEqual(result['result']['price'], 59900)
```

## 12. 完整API示例

让我们创建一个完整的电商API示例，包含产品、类别、订单和用户管理：

### 项目结构
```
api/
├── __init__.py
├── product_api.py
├── category_api.py
├── order_api.py
├── user_api.py
└── schemas.py
```

### 数据模型

```python
# models.py
from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_appbuilder.models.mixins import AuditMixin

class Category(Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return self.name

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(precision=10, scale=2))  # 使用Numeric而不是Integer以支持小数
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="products")
    
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return self.name

class Order(Model):
    __tablename__ = 'order'
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100))
    total_amount = Column(Numeric(precision=10, scale=2))
    status = Column(String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    created_on = Column(DateTime, default=func.now())
    
    items = relationship("OrderItem", back_populates="order")
    
    def __repr__(self):
        return f"Order {self.order_number}"

class OrderItem(Model):
    __tablename__ = 'order_item'
    
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(precision=10, scale=2))
    total_price = Column(Numeric(precision=10, scale=2))
    
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
```

### API Schema

```python
# api/schemas.py
from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields, validate, post_load
from ..models import Category, Product, Order, OrderItem

class CategorySchema(BaseModelSchema):
    class Meta:
        model = Category
        load_instance = True
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(validate=validate.Length(max=500))

class ProductSchema(BaseModelSchema):
    class Meta:
        model = Product
        load_instance = True
        include_relationships = True
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    
    # 关联字段
    category_name = fields.Method("get_category_name", dump_only=True)
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

class OrderItemSchema(BaseModelSchema):
    class Meta:
        model = OrderItem
        load_instance = True
    
    product_name = fields.Method("get_product_name", dump_only=True)
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

class OrderSchema(BaseModelSchema):
    class Meta:
        model = Order
        load_instance = True
    
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    customer_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    customer_email = fields.Email(validate=validate.Length(max=100))

class ProductSearchSchema(BaseModelSchema):
    """产品搜索参数Schema"""
    name = fields.Str(validate=validate.Length(max=100))
    min_price = fields.Decimal(validate=validate.Range(min=0))
    max_price = fields.Decimal(validate=validate.Range(min=0))
    category_id = fields.Int()
```

### 类别API

```python
# api/category_api.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields
from ..models import Category

class CategoryApi(ModelRestApi):
    resource_name = 'category'
    datamodel = SQLAInterface(Category)
    
    # 字段配置
    list_columns = ['id', 'name', 'description', 'is_active']
    show_columns = ['id', 'name', 'description', 'is_active', 'created_on', 'changed_on']
    add_columns = ['name', 'description', 'is_active']
    edit_columns = ['name', 'description', 'is_active']
    
    # 搜索配置
    search_columns = ['name', 'description']
    
    # 排序配置
    order_columns = ['id', 'name', 'created_on']
    
    # 分页配置
    page_size = 20

# 注册API
# appbuilder.add_api(CategoryApi)
```

### 产品API

```python
# api/product_api.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import protect
from flask import request
from sqlalchemy import and_
from ..models import Product, Category
from .schemas import ProductSchema, ProductSearchSchema

class ProductApi(ModelRestApi):
    resource_name = 'product'
    datamodel = SQLAInterface(Product)
    
    # Schema配置
    list_model_schema = ProductSchema()
    show_model_schema = ProductSchema()
    add_model_schema = ProductSchema()
    edit_model_schema = ProductSchema()
    
    # 字段配置
    list_columns = ['id', 'name', 'category_name', 'price', 'stock_quantity', 'is_active']
    show_columns = ['id', 'name', 'description', 'category.name', 'price', 'stock_quantity', 'is_active', 'created_on']
    add_columns = ['name', 'description', 'price', 'stock_quantity', 'category', 'is_active']
    edit_columns = ['name', 'description', 'price', 'stock_quantity', 'category', 'is_active']
    
    # 搜索配置
    search_columns = ['name', 'description', 'category', 'price']
    
    # 排序配置
    order_columns = ['id', 'name', 'price', 'created_on']
    
    # 分页配置
    page_size = 20
    
    # 自定义搜索端点
    @protect()
    def get_list(self):
        """自定义列表获取，支持高级搜索"""
        # 获取搜索参数
        search_params = {}
        for key in ['name', 'min_price', 'max_price', 'category_id']:
            if key in request.args:
                search_params[key] = request.args.get(key)
        
        # 如果有搜索参数，应用自定义过滤
        if search_params:
            query = self.datamodel.session.query(self.datamodel.obj)
            
            # 名称模糊匹配
            if 'name' in search_params:
                query = query.filter(Product.name.contains(search_params['name']))
            
            # 价格范围过滤
            if 'min_price' in search_params:
                query = query.filter(Product.price >= search_params['min_price'])
            if 'max_price' in search_params:
                query = query.filter(Product.price <= search_params['max_price'])
            
            # 类别过滤
            if 'category_id' in search_params:
                query = query.filter(Product.category_id == search_params['category_id'])
            
            # 只返回活跃产品
            query = query.filter(Product.is_active == True)
            
            # 应用分页和排序
            return self.paginate_query(query)
        
        # 否则使用默认行为
        return super().get_list()

# 注册API
# appbuilder.add_api(ProductApi)
```

### 订单API

```python
# api/order_api.py
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import protect
from flask import request
from ..models import Order, OrderItem

class OrderApi(ModelRestApi):
    resource_name = 'order'
    datamodel = SQLAInterface(Order)
    
    # 字段配置
    list_columns = ['id', 'order_number', 'customer_name', 'total_amount', 'status', 'created_on']
    show_columns = ['id', 'order_number', 'customer_name', 'customer_email', 'total_amount', 'status', 'created_on', 'items']
    add_columns = ['order_number', 'customer_name', 'customer_email', 'status']
    edit_columns = ['status']
    
    # 搜索配置
    search_columns = ['order_number', 'customer_name', 'customer_email', 'status']
    
    # 排序配置
    order_columns = ['id', 'created_on', 'order_number']
    order_direction = 'desc'
    
    # 分页配置
    page_size = 15
    
    # 自定义创建方法
    @protect()
    def post(self):
        """创建订单"""
        # 在创建订单前添加业务逻辑
        data = request.get_json()
        
        # 生成订单号（如果未提供）
        if 'order_number' not in data:
            import uuid
            data['order_number'] = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        return super().post()
    
    # 自定义更新方法
    @protect()
    def put(self, pk):
        """更新订单"""
        # 添加订单状态变更日志
        order = self.datamodel.get(pk)
        old_status = order.status if order else None
        
        result = super().put(pk)
        
        # 记录状态变更（实际应用中可能写入日志表）
        if old_status and order and old_status != order.status:
            print(f"Order {order.order_number} status changed from {old_status} to {order.status}")
        
        return result

# 注册API
# appbuilder.add_api(OrderApi)
```

### 用户API

```python
# api/user_api.py
from flask_appbuilder.api import ModelRestApi, BaseApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import protect
from flask_appbuilder.security.sqla.models import User
from flask import request
from ..models import Order

class UserApi(ModelRestApi):
    resource_name = 'user'
    datamodel = SQLAInterface(User)
    
    # 字段配置
    list_columns = ['id', 'username', 'email', 'first_name', 'last_name', 'active']
    show_columns = ['id', 'username', 'email', 'first_name', 'last_name', 'active', 'last_login']
    add_columns = ['username', 'email', 'first_name', 'last_name', 'active', 'roles']
    edit_columns = ['username', 'email', 'first_name', 'last_name', 'active', 'roles']
    
    # 搜索配置
    search_columns = ['username', 'email', 'first_name', 'last_name']
    
    # 排序配置
    order_columns = ['id', 'username', 'created_on']
    
    # 分页配置
    page_size = 20

class UserProfileApi(BaseApi):
    resource_name = 'user-profile'
    
    @protect()
    def get(self):
        """获取当前用户资料"""
        user = self.get_user()
        if not user:
            return self.response_404(message="User not found")
        
        return self.response(200,
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_on=user.created_on.isoformat() if user.created_on else None
        )
    
    @protect()
    def put(self):
        """更新当前用户资料"""
        user = self.get_user()
        if not user:
            return self.response_404(message="User not found")
        
        data = request.get_json()
        
        # 更新允许的字段
        updatable_fields = ['first_name', 'last_name', 'email']
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # 保存更改
        self.appbuilder.get_session.commit()
        
        return self.response(200, message="Profile updated successfully")

# 注册API
# appbuilder.add_api(UserApi)
# appbuilder.add_api(UserProfileApi)
```

### API注册

```python
# api/__init__.py
from .category_api import CategoryApi
from .product_api import ProductApi
from .order_api import OrderApi
from .user_api import UserApi, UserProfileApi

# 导出所有API类
__all__ = ['CategoryApi', 'ProductApi', 'OrderApi', 'UserApi', 'UserProfileApi']
```

### 应用集成

```python
# app/__init__.py
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_appbuilder.security.sqla.models import User
from .models import Category, Product, Order, OrderItem

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    # 初始化数据库
    db = SQLA(app)
    
    # 初始化Flask-AppBuilder
    appbuilder = AppBuilder(app, db.session)
    
    # 注册API
    from api import CategoryApi, ProductApi, OrderApi, UserApi, UserProfileApi
    appbuilder.add_api(CategoryApi)
    appbuilder.add_api(ProductApi)
    appbuilder.add_api(OrderApi)
    appbuilder.add_api(UserApi)
    appbuilder.add_api(UserProfileApi)
    
    return app
```

通过本章的学习，你应该能够：
- 理解REST API的基本概念和设计原则
- 使用Flask-AppBuilder的API生成器快速创建RESTful端点
- 自定义API行为以满足特定业务需求
- 实现API认证和授权机制
- 进行数据序列化和验证
- 实现分页、过滤和排序功能
- 处理API错误并提供统一的响应格式
- 生成API文档
- 优化API性能
- 编写API测试
- 构建完整的REST API示例

REST API是现代Web应用的重要组成部分，掌握Flask-AppBuilder的API功能将帮助你构建更加灵活和可扩展的应用程序。