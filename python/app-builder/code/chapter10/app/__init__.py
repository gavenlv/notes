import logging
from flask import Flask, session, request
from flask_appbuilder import SQLA, AppBuilder
from flask_babel import Babel
import os

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

db = SQLA(app)
babel = Babel(app)
appbuilder = AppBuilder(app, db.session)

# 设置语言选择器
@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

# 添加视图
from .views import ProductModelView
appbuilder.add_view(
    ProductModelView,
    "Products",
    icon="fa-product-hunt",
    category="Catalog"
)

@app.route('/')
def index():
    return '<a href="/login/">Click here to login</a>'

# 初始化数据库
@app.before_first_request
def init_db():
    db.create_all()
    
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