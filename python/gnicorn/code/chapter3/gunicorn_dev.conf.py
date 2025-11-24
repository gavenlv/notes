# gunicorn_dev.conf.py
# 开发环境Gunicorn配置

# 绑定地址和端口
bind = "127.0.0.1:8000"

# 工作进程数量（开发环境使用较少进程）
workers = 1

# 工作进程类型
worker_class = "sync"

# 每个工作进程的线程数
threads = 1

# 工作进程连接数
worker_connections = 1000

# 最大请求数（开发环境可以设置为较小值）
max_requests = 100

# 最大请求数的随机抖动
max_requests_jitter = 10

# 超时设置（开发环境可以设置较短的超时）
timeout = 30
keepalive = 2

# 优雅关闭超时时间（秒）
graceful_timeout = 30

# 日志配置（开发环境输出到控制台）
accesslog = "-"
errorlog = "-"
loglevel = "debug"

# 访问日志格式（开发环境更详细）
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程名称
proc_name = "gunicorn_dev"

# 进程文件
pidfile = "/tmp/gunicorn_dev.pid"

# 守护进程设置（开发环境通常不使用后台模式）
daemon = False

# 进程用户和组（开发环境使用当前用户）
user = None
group = None

# 临时目录
tmp_upload_dir = None

# 限制请求大小（开发环境可以放宽限制）
limit_request_line = 8190
limit_request_fields = 200
limit_request_field_size = 16380

# 预加载应用
preload_app = False

# 检查文件修改时间间隔（开发环境启用自动重载）
check_config = True

# 环境变量
raw_env = [
    'DJANGO_SETTINGS_MODULE=myapp.settings.development',
    'ENV=development',
    'DEBUG=True'
]