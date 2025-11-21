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

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()