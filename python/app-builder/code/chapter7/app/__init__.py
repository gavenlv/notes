import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_appbuilder.api import Api

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 创建API
api = Api(app)

# 导入并注册API
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

@app.route('/')
def hello():
    return "Flask App-Builder REST API Demo. Visit /api/v1/contacts/ for API endpoints."