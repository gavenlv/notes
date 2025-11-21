import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

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

# 注册视图
from .views import ContactModelView, GroupModelView, GenderModelView

appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-users", category="Contacts")
appbuilder.add_view(GenderModelView, "List Genders", icon="fa-circle", category="Contacts")

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)