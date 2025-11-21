# gunicorn_config.py
# Gunicorn配置文件示例

# 绑定地址和端口
bind = "0.0.0.0:8000"

# 工作进程数量 (通常设置为 (2 * CPU核心数) + 1)
workers = 4

# 工作进程类型
# 可选: sync, eventlet, gevent, tornado, gaiohttp
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
accesslog = "-"  # "-" 表示输出到标准输出
errorlog = "-"   # "-" 表示输出到标准错误
loglevel = "info"

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程名称
proc_name = "gunicorn_example"

# 进程文件
pidfile = "/tmp/gunicorn_example.pid"

# 守护进程设置
daemon = False  # 设置为True后台运行

# 进程用户和组
user = None
group = None

# 临时目录
tmp_upload_dir = None

# 限制请求大小（字节）
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 预加载应用
preload_app = False

# 检查文件修改时间间隔（秒）
check_config = False