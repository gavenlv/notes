import logging
from flask import Flask
from flask_appbuilder import AppBuilder
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder.security.manager import AUTH_DB
from flask_mail import Mail

# 初始化扩展
db = SQLAlchemy()
appbuilder = AppBuilder()
mail = Mail()

def create_app(config_name='config.Config'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_name)
    
    # 初始化扩展
    db.init_app(app)
    mail.init_app(app)
    
    # 初始化Flask-AppBuilder
    appbuilder.init_app(app, db)
    appbuilder.add_view_no_menu('TaskDashboardView')
    
    # 注册插件
    register_plugins(appbuilder)
    
    # 配置日志
    configure_logging(app)
    
    return app

def register_plugins(appbuilder):
    """注册插件"""
    try:
        # 导入并注册插件
        from plugins.audit_log.plugin import AuditLogPlugin
        from plugins.email_service.plugin import EmailServicePlugin
        from plugins.task_manager.plugin import TaskManagerPlugin
        from plugins.redis_cache.plugin import RedisCachePlugin
        from plugins.celery_tasks.plugin import CeleryTasksPlugin
        
        # 注册插件
        appbuilder.register_plugin(AuditLogPlugin)
        appbuilder.register_plugin(EmailServicePlugin)
        appbuilder.register_plugin(TaskManagerPlugin)
        appbuilder.register_plugin(RedisCachePlugin)
        appbuilder.register_plugin(CeleryTasksPlugin)
        
        logging.info("All plugins registered successfully")
    except Exception as e:
        logging.error(f"Failed to register plugins: {str(e)}")

def configure_logging(app):
    """配置日志"""
    if not app.debug:
        import os
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)