# 第十二章：测试策略和调试

在软件开发过程中，测试和调试是确保应用程序质量和稳定性的关键环节。Flask-AppBuilder作为基于Flask的框架，可以充分利用Python生态系统的测试工具。本章将详细介绍如何为Flask-AppBuilder应用程序编写测试以及有效的调试策略。

## 目录
1. 测试基础概念
2. 单元测试
3. 集成测试
4. 功能测试
5. 测试环境配置
6. Flask-AppBuilder特定测试
7. 调试技巧和工具
8. 完整示例
9. 测试覆盖率
10. 最佳实践

## 1. 测试基础概念

### 测试类型
- **单元测试(Unit Testing)**: 测试最小的功能单元，如函数或方法
- **集成测试(Integration Testing)**: 测试模块间的交互
- **功能测试(Functional Testing)**: 测试整个功能流程
- **端到端测试(End-to-End Testing)**: 测试完整的用户场景

### 测试原则
- **自动化**: 测试应该能够自动运行
- **独立性**: 测试之间不应相互依赖
- **可重复性**: 测试结果应一致且可重现
- **快速反馈**: 测试应快速执行并提供即时反馈

## 2. 单元测试

### 设置测试环境

```bash
pip install pytest pytest-cov pytest-flask
```

### 基础测试结构

```python
# tests/test_models.py
import pytest
from app import app, db
from app.models import User, Product, Category

@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_data():
    """创建示例数据"""
    with app.app_context():
        # 创建分类
        category = Category(name="Electronics")
        db.session.add(category)
        db.session.commit()
        
        # 创建产品
        product = Product(
            name="Laptop",
            description="High performance laptop",
            price=1200,
            category_id=category.id
        )
        db.session.add(product)
        db.session.commit()
        
        return category, product

def test_product_creation(sample_data):
    """测试产品创建"""
    _, product = sample_data
    
    assert product.name == "Laptop"
    assert product.price == 1200
    assert product.category.name == "Electronics"

def test_product_repr(sample_data):
    """测试产品表示"""
    _, product = sample_data
    
    assert str(product) == "Laptop"
```

### 测试模型方法

```python
# app/models.py
from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Category(Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    products = relationship("Product", back_populates="category")
    
    def product_count(self):
        """获取该分类下的产品数量"""
        return len(self.products)
    
    def __repr__(self):
        return self.name

class Product(Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="products")
    
    def is_expensive(self):
        """判断产品是否昂贵(价格大于1000)"""
        return self.price > 1000
    
    def __repr__(self):
        return self.name
```

```python
# tests/test_model_methods.py
import pytest
from app import app, db
from app.models import Category, Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_category_product_count(client):
    """测试分类产品计数方法"""
    with app.app_context():
        # 创建分类和产品
        category = Category(name="Electronics")
        db.session.add(category)
        db.session.commit()
        
        product1 = Product(
            name="Laptop",
            price=1200,
            category_id=category.id
        )
        product2 = Product(
            name="Mouse",
            price=25,
            category_id=category.id
        )
        db.session.add_all([product1, product2])
        db.session.commit()
        
        # 测试产品计数
        assert category.product_count() == 2

def test_product_is_expensive(client):
    """测试产品昂贵判断方法"""
    with app.app_context():
        category = Category(name="Electronics")
        db.session.add(category)
        db.session.commit()
        
        # 昂贵的产品
        expensive_product = Product(
            name="Laptop",
            price=1200,
            category_id=category.id
        )
        # 便宜的产品
        cheap_product = Product(
            name="Mouse",
            price=25,
            category_id=category.id
        )
        db.session.add_all([expensive_product, cheap_product])
        db.session.commit()
        
        # 测试判断逻辑
        assert expensive_product.is_expensive() == True
        assert cheap_product.is_expensive() == False
```

## 3. 集成测试

### 测试数据库操作

```python
# tests/test_database_operations.py
import pytest
from app import app, db
from app.models import Category, Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_create_category(client):
    """测试创建分类"""
    with app.app_context():
        category = Category(name="Electronics")
        db.session.add(category)
        db.session.commit()
        
        # 验证分类已保存到数据库
        saved_category = db.session.query(Category).filter_by(name="Electronics").first()
        assert saved_category is not None
        assert saved_category.name == "Electronics"

def test_create_product_with_category(client):
    """测试创建带分类的产品"""
    with app.app_context():
        # 先创建分类
        category = Category(name="Electronics")
        db.session.add(category)
        db.session.commit()
        
        # 再创建产品
        product = Product(
            name="Laptop",
            description="High performance laptop",
            price=1200,
            category_id=category.id
        )
        db.session.add(product)
        db.session.commit()
        
        # 验证产品已保存并关联到分类
        saved_product = db.session.query(Product).filter_by(name="Laptop").first()
        assert saved_product is not None
        assert saved_product.category.name == "Electronics"
```

### 测试Flask-AppBuilder数据模型接口

```python
# tests/test_datamodel_interface.py
import pytest
from flask_appbuilder.models.sqla.interface import SQLAInterface
from app import app, db
from app.models import Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_datamodel_crud_operations(client):
    """测试数据模型CRUD操作"""
    with app.app_context():
        # 创建数据模型接口
        datamodel = SQLAInterface(Product)
        
        # 创建产品
        product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 100
        }
        
        # 添加产品
        product = Product(**product_data)
        result = datamodel.add(product)
        assert result is not None
        
        # 查询产品
        queried_product = datamodel.get(result.id)
        assert queried_product.name == 'Test Product'
        assert queried_product.price == 100
        
        # 更新产品
        updated_data = {'name': 'Updated Product', 'price': 150}
        datamodel.edit(result, **updated_data)
        updated_product = datamodel.get(result.id)
        assert updated_product.name == 'Updated Product'
        assert updated_product.price == 150
        
        # 删除产品
        datamodel.delete(result)
        deleted_product = datamodel.get(result.id)
        assert deleted_product is None
```

## 4. 功能测试

### 测试Flask路由

```python
# tests/test_routes.py
import pytest
from app import app, db
from app.models import User, Product, Category
from flask_appbuilder.security.sqla.models import User as FABUser

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF保护以便测试
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # 创建测试用户
            user = FABUser()
            user.username = 'testuser'
            user.email = 'test@example.com'
            user.active = True
            user.password = 'password'
            db.session.add(user)
            db.session.commit()
            
            yield client
            db.drop_all()

def test_homepage(client):
    """测试主页访问"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Click here to login' in response.data

def test_login_page(client):
    """测试登录页面"""
    response = client.get('/login/')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(client):
    """测试成功登录"""
    response = client.post('/login/', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # 登录成功后应该重定向到首页
    assert b'Welcome' in response.data or b'dashboard' in response.data.lower()

def test_login_failure(client):
    """测试登录失败"""
    response = client.post('/login/', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # 登录失败应该显示错误消息
    assert b'Invalid login' in response.data or b'error' in response.data.lower()
```

### 测试API端点

```python
# tests/test_api.py
import pytest
import json
from app import app, db
from app.models import Product, Category

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # 创建测试数据
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()
            
            product = Product(
                name="Laptop",
                description="High performance laptop",
                price=1200,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
            
            yield client
            db.drop_all()

def test_api_get_products(client):
    """测试获取产品列表API"""
    response = client.get('/api/v1/products/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'result' in data
    assert len(data['result']) == 1
    assert data['result'][0]['name'] == 'Laptop'

def test_api_get_product(client):
    """测试获取单个产品API"""
    # 先获取产品ID
    with app.app_context():
        product = db.session.query(Product).first()
        product_id = product.id
    
    response = client.get(f'/api/v1/products/{product_id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'result' in data
    assert data['result']['name'] == 'Laptop'
    assert data['result']['price'] == 1200

def test_api_create_product(client):
    """测试创建产品API"""
    with app.app_context():
        category = db.session.query(Category).first()
        category_id = category.id
    
    new_product_data = {
        'name': 'Smartphone',
        'description': 'Latest smartphone',
        'price': 800,
        'category_id': category_id
    }
    
    response = client.post(
        '/api/v1/products/',
        data=json.dumps(new_product_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    
    # 验证产品已创建
    response = client.get('/api/v1/products/')
    data = json.loads(response.data)
    assert len(data['result']) == 2  # 原有1个 + 新增1个
    assert any(p['name'] == 'Smartphone' for p in data['result'])
```

## 5. 测试环境配置

### 配置文件分离

```python
# config.py
import os
from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    AUTH_TYPE = AUTH_DB
    AUTH_ROLE_ADMIN = 'Admin'
    AUTH_ROLE_PUBLIC = 'Public'
    APP_NAME = "Flask AppBuilder App"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # 禁用CSRF保护以便测试

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 测试配置

```python
# tests/conftest.py
import pytest
from app import app, db

@pytest.fixture
def client():
    """创建测试客户端"""
    app.config.from_object('config.TestingConfig')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def auth_client(client):
    """创建已认证的测试客户端"""
    # 这里可以实现登录逻辑
    return client

@pytest.fixture
def runner():
    """创建CLI运行器"""
    return app.test_cli_runner()
```

## 6. Flask-AppBuilder特定测试

### 测试安全功能

```python
# tests/test_security.py
import pytest
from flask_appbuilder.security.sqla.models import User, Role
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_registration(client):
    """测试用户注册"""
    with app.app_context():
        # 创建角色
        role = Role(name='Public', permissions=[])
        db.session.add(role)
        db.session.commit()
        
        # 注册新用户
        from flask_appbuilder.security.registerviews import RegisterUserDBView
        reg_view = RegisterUserDBView()
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'conf_password': 'password123'
        }
        
        # 注意：这里需要模拟表单提交过程
        # 实际测试可能需要更复杂的设置

def test_role_permissions(client):
    """测试角色权限"""
    with app.app_context():
        # 创建角色和权限
        admin_role = Role(name='Admin')
        public_role = Role(name='Public')
        db.session.add_all([admin_role, public_role])
        db.session.commit()
        
        # 验证角色创建
        assert Role.query.filter_by(name='Admin').first() is not None
        assert Role.query.filter_by(name='Public').first() is not None
```

### 测试自定义视图

```python
# tests/test_custom_views.py
import pytest
from flask_appbuilder import BaseView, expose
from app import app, db

class TestCustomView(BaseView):
    route_base = '/test'
    
    @expose('/hello')
    def hello(self):
        return "Hello, World!"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # 注册测试视图
            appbuilder.add_view_no_menu(TestCustomView)
            
            yield client
            db.drop_all()

def test_custom_view_route(client):
    """测试自定义视图路由"""
    response = client.get('/test/hello')
    assert response.status_code == 200
    assert b'Hello, World!' in response.data
```

## 7. 调试技巧和工具

### 使用Flask调试器

```python
# app/__init__.py
import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

# 启用调试模式
if app.config.get('DEBUG'):
    app.debug = True

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 添加调试路由
@app.route('/debug/db')
def debug_db():
    """数据库调试路由"""
    try:
        # 尝试查询
        from app.models import Product
        count = db.session.query(Product).count()
        return f"Database connection successful. Product count: {count}"
    except Exception as e:
        return f"Database error: {str(e)}", 500

# 添加调试中间件
@app.before_request
def log_request_info():
    """记录请求信息"""
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.after_request
def log_response_info(response):
    """记录响应信息"""
    app.logger.debug('Response: %s', response.status)
    return response
```

### 使用pdb调试器

```python
# app/views.py
import pdb
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.models import Product

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    list_columns = ['name', 'category.name', 'price']
    
    def pre_add(self, item):
        """在添加产品前调试"""
        # 设置断点
        pdb.set_trace()
        
        # 打印调试信息
        print(f"Adding product: {item.name}")
        print(f"Product price: {item.price}")
        
        # 调用父类方法
        super().pre_add(item)
    
    def post_add(self, item):
        """在添加产品后调试"""
        # 记录日志
        self.appbuilder.get_logger.debug(f"Product added: {item.name}")
        super().post_add(item)
```

### 使用日志调试

```python
# app/utils.py
import logging
from functools import wraps

# 创建专用的日志记录器
logger = logging.getLogger('app.debug')

def debug_function(func):
    """函数调试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling function: {func.__name__}")
        logger.debug(f"Arguments: args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} raised exception: {e}")
            raise
    return wrapper

# 使用示例
@debug_function
def calculate_total_price(products):
    """计算产品总价"""
    total = sum(product.price for product in products)
    return total
```

## 8. 完整示例

### 项目结构
```
chapter12/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── api.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_api.py
│   ├── test_security.py
│   └── test_utils.py
├── config.py
└── run.py
```

### requirements.txt

```txt
Flask-AppBuilder==4.3.0
pytest==7.2.0
pytest-cov==4.0.0
pytest-flask==1.2.0
pytest-html==3.2.0
```

### 配置文件 (config.py)

```python
import os
from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    CSRF_ENABLED = True
    AUTH_TYPE = AUTH_DB
    AUTH_ROLE_ADMIN = 'Admin'
    AUTH_ROLE_PUBLIC = 'Public'
    
    APP_NAME = "Testing Demo App"

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # 禁用CSRF保护以便测试

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 模型文件 (app/models.py)

```python
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Category(AuditMixin, Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    products = relationship("Product", back_populates="category")
    
    def product_count(self):
        """获取该分类下的产品数量"""
        return len(self.products)
    
    def __repr__(self):
        return self.name

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="products")
    
    def is_expensive(self):
        """判断产品是否昂贵(价格大于1000)"""
        return self.price > 1000
    
    def __repr__(self):
        return self.name
```

### 视图文件 (app/views.py)

```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Product, Category

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    list_columns = ['name', 'category.name', 'price']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'category', 'price']}),
        ('Audit', {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    
    def pre_add(self, item):
        """在添加产品前验证"""
        if item.price < 0:
            raise ValueError("Price cannot be negative")
        super().pre_add(item)

class CategoryModelView(ModelView):
    datamodel = SQLAInterface(Category)
    list_columns = ['name', 'product_count']
```

### API文件 (app/api.py)

```python
from flask_appbuilder.api import BaseApi
from flask_appbuilder import expose
from sqlalchemy.orm import joinedload
from .models import Product

class ProductApi(BaseApi):
    resource_name = 'products'
    
    @expose('/', methods=['GET'])
    def get_list(self):
        """获取产品列表"""
        products = self.appbuilder.get_session.query(Product).options(
            joinedload(Product.category)
        ).all()
        
        result = []
        for product in products:
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'category': product.category.name if product.category else None
            })
        
        return self.response(200, result=result)
    
    @expose('/<int:pk>', methods=['GET'])
    def get(self, pk):
        """获取单个产品"""
        product = self.appbuilder.get_session.query(Product).options(
            joinedload(Product.category)
        ).get(pk)
        
        if not product:
            return self.response_404()
        
        result = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'category': product.category.name if product.category else None
        }
        
        return self.response(200, result=result)
```

### 工具函数文件 (app/utils.py)

```python
import logging
from functools import wraps

# 创建专用的日志记录器
logger = logging.getLogger('app.utils')

def validate_product_data(func):
    """产品数据验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 验证参数
        if 'price' in kwargs and kwargs['price'] < 0:
            raise ValueError("Price cannot be negative")
        
        return func(*args, **kwargs)
    return wrapper

def calculate_total_price(products):
    """计算产品总价"""
    logger.debug(f"Calculating total price for {len(products)} products")
    total = sum(product.price for product in products)
    logger.debug(f"Total price calculated: {total}")
    return total
```

### 应用初始化文件 (app/__init__.py)

```python
import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
import os

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_CONFIG') or 'config.DevelopmentConfig')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 添加视图
from .views import ProductModelView, CategoryModelView
from .api import ProductApi

appbuilder.add_view(
    ProductModelView,
    "Products",
    icon="fa-product-hunt",
    category="Catalog"
)

appbuilder.add_view(
    CategoryModelView,
    "Categories",
    icon="fa-tags",
    category="Catalog"
)

appbuilder.add_api(ProductApi)

@app.route('/')
def index():
    return '<a href="/login/">Click here to login</a>'

# 初始化数据库
@app.before_first_request
def init_db():
    db.create_all()
    
    # 创建默认数据
    from .models import Category, Product
    
    if not appbuilder.get_session.query(Category).first():
        # 创建示例分类
        electronics = Category(name="Electronics")
        books = Category(name="Books")
        clothing = Category(name="Clothing")
        
        appbuilder.get_session.add_all([electronics, books, clothing])
        appbuilder.get_session.commit()
        
        # 创建示例产品
        products = [
            Product(name="Laptop", description="High performance laptop", price=1200, category_id=electronics.id),
            Product(name="Python Book", description="Learn Python programming", price=35, category_id=books.id),
            Product(name="T-Shirt", description="Cotton t-shirt", price=20, category_id=clothing.id)
        ]
        
        appbuilder.get_session.add_all(products)
        appbuilder.get_session.commit()
    
    # 创建默认管理员用户
    if not appbuilder.sm.find_user(username='admin'):
        appbuilder.sm.add_user(
            username='admin',
            first_name='Admin',
            last_name='User',
            email='admin@fab.org',
            role=appbuilder.sm.find_role(appbuilder.sm.auth_role_admin),
            password='admin'
        )
```

### 运行文件 (run.py)

```python
import os
from app import app

if __name__ == '__main__':
    # 从环境变量获取配置，如果没有则使用默认配置
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    app.run(host='0.0.0.0', port=8080, debug=app.config.get('DEBUG', False))
```

### 测试配置文件 (tests/conftest.py)

```python
import pytest
from app import app, db

@pytest.fixture(scope='session')
def app_context():
    """创建应用上下文"""
    app.config.from_object('config.TestingConfig')
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app_context):
    """创建测试客户端"""
    with app_context.test_client() as client:
        with app_context.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture(scope='function')
def db_session(app_context):
    """创建数据库会话"""
    with app_context.app_context():
        db.create_all()
        yield db.session
        db.drop_all()
```

### 模型测试文件 (tests/test_models.py)

```python
import pytest
from app.models import Category, Product

def test_category_creation(db_session):
    """测试分类创建"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    assert category.id is not None
    assert category.name == "Electronics"

def test_product_creation(db_session):
    """测试产品创建"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    product = Product(
        name="Laptop",
        description="High performance laptop",
        price=1200,
        category_id=category.id
    )
    db_session.add(product)
    db_session.commit()
    
    assert product.id is not None
    assert product.name == "Laptop"
    assert product.category.name == "Electronics"

def test_category_product_count(db_session):
    """测试分类产品计数"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    product1 = Product(name="Laptop", price=1200, category_id=category.id)
    product2 = Product(name="Mouse", price=25, category_id=category.id)
    db_session.add_all([product1, product2])
    db_session.commit()
    
    assert category.product_count() == 2

def test_product_is_expensive(db_session):
    """测试产品昂贵判断"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    expensive_product = Product(name="Laptop", price=1200, category_id=category.id)
    cheap_product = Product(name="Mouse", price=25, category_id=category.id)
    db_session.add_all([expensive_product, cheap_product])
    db_session.commit()
    
    assert expensive_product.is_expensive() is True
    assert cheap_product.is_expensive() is False
```

### 视图测试文件 (tests/test_views.py)

```python
import pytest
from flask_appbuilder.security.sqla.models import User

def test_product_model_view(client):
    """测试产品模型视图"""
    # 先登录管理员用户
    with client.application.app_context():
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.email = 'admin@test.com'
        admin_user.active = True
        admin_user.password = 'admin'
        from app import db
        db.session.add(admin_user)
        db.session.commit()
    
    # 登录
    response = client.post('/login/', data={
        'username': 'admin',
        'password': 'admin'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # 访问产品列表页面
    response = client.get('/productmodelview/list/')
    assert response.status_code == 200

def test_category_model_view(client):
    """测试分类模型视图"""
    # 先登录管理员用户
    with client.application.app_context():
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.email = 'admin@test.com'
        admin_user.active = True
        admin_user.password = 'admin'
        from app import db
        db.session.add(admin_user)
        db.session.commit()
    
    # 登录
    response = client.post('/login/', data={
        'username': 'admin',
        'password': 'admin'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # 访问分类列表页面
    response = client.get('/categorymodelview/list/')
    assert response.status_code == 200
```

### API测试文件 (tests/test_api.py)

```python
import pytest
import json

def test_api_get_products(client):
    """测试获取产品列表API"""
    response = client.get('/api/v1/products/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'result' in data

def test_api_get_single_product(client):
    """测试获取单个产品API"""
    # 先获取一个产品的ID
    with client.application.app_context():
        from app.models import Product
        product = Product.query.first()
        if product:
            product_id = product.id
            
            response = client.get(f'/api/v1/products/{product_id}')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'result' in data
            assert data['result']['id'] == product_id
```

### 工具函数测试文件 (tests/test_utils.py)

```python
import pytest
from app.utils import calculate_total_price, validate_product_data
from app.models import Product

def test_calculate_total_price():
    """测试计算总价函数"""
    products = [
        Product(name="Product 1", price=100),
        Product(name="Product 2", price=200),
        Product(name="Product 3", price=300)
    ]
    
    total = calculate_total_price(products)
    assert total == 600

def test_validate_product_data_decorator():
    """测试产品数据验证装饰器"""
    @validate_product_data
    def create_product(name, price):
        return {"name": name, "price": price}
    
    # 正常情况
    result = create_product("Test Product", 100)
    assert result["price"] == 100
    
    # 异常情况
    with pytest.raises(ValueError):
        create_product("Test Product", -50)
```

## 9. 测试覆盖率

### 运行测试并生成覆盖率报告

```bash
# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term tests/

# 只生成XML格式的覆盖率报告
pytest --cov=app --cov-report=xml tests/

# 查看详细的覆盖率信息
pytest --cov=app --cov-report=term-missing tests/
```

### 配置覆盖率选项

```ini
# .coveragerc
[run]
source = app
omit = 
    */venv/*
    */env/*
    */tests/*
    */migrations/*
    */config.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

## 10. 最佳实践

### 测试最佳实践

1. **保持测试独立性**: 每个测试都应该独立运行，不依赖其他测试的结果
2. **使用描述性命名**: 测试函数名应该清楚地描述被测试的行为
3. **遵循AAA模式**: Arrange(准备)、Act(执行)、Assert(断言)
4. **测试边界条件**: 包括正常情况、异常情况和边界值
5. **保持测试简洁**: 每个测试应该只测试一个功能点

### 调试最佳实践

1. **使用日志而非print**: 使用logging模块而不是print语句进行调试
2. **合理使用断点**: 在关键位置设置断点，但不要过度使用
3. **记录调试信息**: 记录足够的上下文信息以便后续分析
4. **清理调试代码**: 发布前移除临时的调试代码
5. **使用专业工具**: 利用IDE的调试功能和专业调试工具

### 持续集成

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml tests/
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

通过本章的学习，你应该能够：
- 理解不同类型的测试及其作用
- 为Flask-AppBuilder应用程序编写单元测试、集成测试和功能测试
- 配置测试环境和测试数据库
- 使用专业的调试工具和技术
- 生成测试覆盖率报告
- 遵循测试和调试的最佳实践