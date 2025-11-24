import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_appbuilder.security.manager import AUTH_DB
from flask_migrate import Migrate
from .views import DocumentModelView, ImageGalleryModelView
import os

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

db = SQLA(app)
migrate = Migrate(app, db)
appbuilder = AppBuilder(app, db.session, auth_type=AUTH_DB)

# 创建上传目录
upload_path = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(upload_path, exist_ok=True)
os.makedirs(os.path.join(upload_path, 'images'), exist_ok=True)

# 添加视图
appbuilder.add_view(
    DocumentModelView,
    "Documents",
    icon="fa-file-text-o",
    category="File Management"
)

appbuilder.add_view(
    ImageGalleryModelView,
    "Image Gallery",
    icon="fa-picture-o",
    category="File Management"
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