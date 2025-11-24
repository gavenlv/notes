from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_cors import CORS
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    # 初始化CORS
    CORS(app)
    
    # 初始化数据库
    db = SQLA(app)
    
    # 初始化Flask-AppBuilder
    appbuilder = AppBuilder(app, db.session)
    
    # 初始化Swagger
    swagger = Swagger(app)
    
    # 注册蓝图
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # 注册CLI命令
    from app.cli import register_commands
    register_commands(app)
    
    return app