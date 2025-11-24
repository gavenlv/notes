import os
from app import app

if __name__ == '__main__':
    # 从环境变量获取配置
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # 获取端口和调试模式
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # 运行应用
    app.run(host='0.0.0.0', port=port, debug=debug)