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