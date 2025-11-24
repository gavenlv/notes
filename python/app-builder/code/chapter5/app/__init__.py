import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 创建表
@app.before_first_request
def create_tables():
    db.create_all()

# 注册视图
from .views import DashboardView, ContactFormView

appbuilder.add_view_no_menu(DashboardView)
appbuilder.add_view(ContactFormView, "Add Contact", icon="fa-plus", category="Contacts")
appbuilder.add_link("Dashboard", href='/dashboard/', icon="fa-dashboard")

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)