#!/bin/bash
# start_gunicorn.sh
# 启动Gunicorn的脚本示例

# 激活虚拟环境（如果需要）
# source /path/to/venv/bin/activate

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 启动Gunicorn
echo "Starting Gunicorn with configuration file..."
gunicorn simple_wsgi_app:application -c gunicorn_config.py

# 或者使用命令行参数启动
# echo "Starting Gunicorn with command line options..."
# gunicorn simple_wsgi_app:application \
#   --bind=0.0.0.0:8000 \
#   --workers=4 \
#   --worker-class=sync \
#   --timeout=30 \
#   --log-level=info \
#   --access-logfile=- \
#   --error-logfile=-