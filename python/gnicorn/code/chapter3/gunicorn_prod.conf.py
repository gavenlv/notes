# gunicorn_prod.conf.py
# 生产环境Gunicorn配置

import multiprocessing
import os

# 绑定地址和端口
bind = "127.0.0.1:8000"

# 工作进程数量（通常设置为 2 * CPU核心数 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
worker_class = "sync"

# 每个工作进程的线程数
threads = 1

# 工作进程连接数
worker_connections = 1000

# 最大请求数，达到后重启工作进程
max_requests = 1000

# 最大请求数的随机抖动
max_requests_jitter = 100

# 超时设置（秒）
timeout = 30
keepalive = 2

# 优雅关闭超时时间（秒）
graceful_timeout = 30

# 日志配置
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "warning"

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程名称
proc_name = "gunicorn_prod"

# 进程文件
pidfile = "/var/run/gunicorn/gunicorn_prod.pid"

# 守护进程设置
daemon = True

# 进程用户和组
user = "www-data"
group = "www-data"

# 临时目录
tmp_upload_dir = "/tmp/gunicorn"

# 限制请求大小（字节）
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 预加载应用
preload_app = True

# 检查文件修改时间间隔（秒）
check_config = False

# 服务器机制
server_mechanism = "egg:meinheld#gunicorn_worker"  # 可选：使用meinheld作为服务器机制

# SSL设置（如果直接使用HTTPS）
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"

# 环境变量
raw_env = [
    'DJANGO_SETTINGS_MODULE=myapp.settings.production',
    'ENV=production'
]