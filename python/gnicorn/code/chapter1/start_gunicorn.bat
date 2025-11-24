@echo off
REM start_gunicorn.bat
REM Windows环境下启动Gunicorn的脚本示例

REM 激活虚拟环境（如果需要）
REM call C:\path\to\venv\Scripts\activate.bat

REM 启动Gunicorn
echo Starting Gunicorn with configuration file...
gunicorn simple_wsgi_app:application -c gunicorn_config.py

REM 或者使用命令行参数启动
REM echo Starting Gunicorn with command line options...
REM gunicorn simple_wsgi_app:application ^
REM   --bind=0.0.0.0:8000 ^
REM   --workers=4 ^
REM   --worker-class=sync ^
REM   --timeout=30 ^
REM   --log-level=info ^
REM   --access-logfile=- ^
REM   --error-logfile=-

pause