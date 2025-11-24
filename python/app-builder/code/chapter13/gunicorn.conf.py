# Gunicorn配置文件
import os
import multiprocessing

# 服务器套接字
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')

# 工人进程
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = int(os.environ.get('GUNICORN_WORKER_CONNECTIONS', 1000))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 30))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', 2))

# 日志
accesslog = os.environ.get('GUNICORN_ACCESSLOG', '-')
errorlog = os.environ.get('GUNICORN_ERRORLOG', '-')
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')
access_log_format = os.environ.get('GUNICORN_ACCESS_LOG_FORMAT', 
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s')

# 进程命名
proc_name = os.environ.get('GUNICORN_PROC_NAME', 'flask-appbuilder')

# 守护进程
daemon = False
pidfile = os.environ.get('GUNICORN_PIDFILE', '/tmp/gunicorn.pid')

# 安全
user = os.environ.get('GUNICORN_USER', None)
group = os.environ.get('GUNICORN_GROUP', None)

# 性能
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 100))

# 前向代理支持
forwarded_allow_ips = os.environ.get('GUNICORN_FORWARDED_ALLOW_IPS', '*')

# 优雅重启
preload_app = True

# 工人进程生命周期钩子
def when_ready(server):
    """服务器启动完成时调用"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """工人进程中断时调用"""
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """工人进程中止时调用"""
    worker.log.info("worker received SIGABRT signal")