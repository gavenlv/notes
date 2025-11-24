import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_caching import Cache
from flask_compress import Compress
import os

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

# 初始化扩展
db = SQLA(app)
cache = Cache(app)
Compress(app)

appbuilder = AppBuilder(app, db.session)

# 添加视图
from .views import ProductModelView, ProductPublicView
from .api import ProductApi

appbuilder.add_view(
    ProductModelView,
    "Products",
    icon="fa-product-hunt",
    category="Catalog"
)

appbuilder.add_view(
    ProductPublicView,
    "Public Products",
    icon="fa-list",
    category="Public"
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