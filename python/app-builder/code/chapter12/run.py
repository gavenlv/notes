import os
from app import app

if __name__ == '__main__':
    # 从环境变量获取配置，如果没有则使用默认配置
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    app.run(host='0.0.0.0', port=8080, debug=app.config.get('DEBUG', False))