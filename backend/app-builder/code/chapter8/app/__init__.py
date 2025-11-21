import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 导入视图
from . import views, widgets

# 注册视图
from .views import ContactModelView, DashboardView
appbuilder.add_view(ContactModelView, "Contacts", icon="fa-users", category="Contacts")
appbuilder.add_view_no_menu(DashboardView)

# 创建表
db.create_all()

# 添加初始数据
from .models import Contact
if not db.session.query(Contact).first():
    contact = Contact()
    contact.name = "John Doe"
    contact.email = "john@example.com"
    contact.phone = "123-456-7890"
    contact.address = "123 Main St, City, Country"
    db.session.add(contact)
    db.session.commit()

@app.route('/')
def hello():
    return "Flask App-Builder Custom Widgets and Templates Demo. Visit /dashboard/ for the dashboard."