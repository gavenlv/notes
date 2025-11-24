import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from .config import APP_NAME

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 添加初始数据
@app.before_first_request
def create_tables():
    db.create_all()
    
    # 添加初始数据
    from .models import ContactGroup, Gender
    
    # 检查是否已有数据
    if not db.session.query(ContactGroup).first():
        db.session.add(ContactGroup(name='Friends'))
        db.session.add(ContactGroup(name='Family'))
        db.session.add(ContactGroup(name='Work'))
        db.session.commit()
        
    if not db.session.query(Gender).first():
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"