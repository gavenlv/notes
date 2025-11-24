import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, g
from flask_appbuilder import SQLA, AppBuilder
from datetime import datetime
import time

# 初始化扩展
db = SQLA()
appbuilder = AppBuilder()

def setup_logging(app):
    """设置应用日志"""
    if not app.debug and not app.testing:
        # 确保日志目录存在
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 文件日志处理器
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/app.log'),
            maxBytes=app.config.get('LOG_MAX_BYTES', 1024*1024*100),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        ))
        
        file_handler.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
        app.logger.info('Application startup')

def create_app(config_name=None):
    """创建应用实例"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 设置日志
    setup_logging(app)
    
    # 初始化扩展
    db.init_app(app)
    appbuilder.init_app(app, db.session)
    
    # 注册蓝图
    from .views import ProductModelView, CategoryModelView
    appbuilder.add_view(
        ProductModelView,
        "Products",
        icon="fa-product-hunt",
        category="Catalog"
    )
    
    appbuilder.add_view(
        CategoryModelView,
        "Categories",
        icon="fa-tags",
        category="Catalog"
    )
    
    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            
            # 检查Redis连接
            if app.config.get('CACHE_TYPE') == 'redis':
                from redis import Redis
                redis_client = Redis.from_url(app.config.get('CACHE_REDIS_URL'))
                redis_client.ping()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'database': 'ok',
                    'redis': 'ok' if app.config.get('CACHE_TYPE') == 'redis' else 'not_configured'
                }
            }), 200
        except Exception as e:
            app.logger.error(f'Health check failed: {str(e)}')
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500
    
    # 请求处理钩子
    @app.before_request
    def before_request():
        """请求前处理"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 记录请求日志
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.info(
                f'{request.remote_addr} "{request.method} {request.path}" '
                f'{response.status_code} {duration:.3f}s'
            )
        
        return response
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal error: {str(error)}')
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# 创建应用实例
app = create_app()