import os
from app import app

if __name__ == '__main__':
    # 获取配置名称
    config_name = os.environ.get('FLASK_CONFIG', 'production')
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )