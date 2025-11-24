# Flask日志管理与监控

日志是应用程序的重要组成部分，它帮助开发者和运维人员了解应用的运行状态、诊断问题、监控性能并进行安全审计。在Flask应用中，合理的日志管理策略对于维护应用的稳定性和可维护性至关重要。

## 目录
1. Flask日志基础
2. 日志配置与管理
3. 结构化日志记录
4. 日志级别与分类
5. 日志轮转与存储
6. 日志监控与分析
7. 第三方日志服务集成
8. 安全日志与审计
9. 性能优化与最佳实践

## 1. Flask日志基础

### 1.1 Flask默认日志

Flask默认使用Python的logging模块，提供了基本的日志功能：

```python
from flask import Flask
import logging

app = Flask(__name__)

@app.route('/')
def index():
    app.logger.info('Index page accessed')
    return "Hello, World!"

@app.route('/error')
def error():
    try:
        # 模拟错误
        result = 1 / 0
    except Exception as e:
        app.logger.error(f'Error occurred: {str(e)}', exc_info=True)
        return "Error occurred", 500
```

### 1.2 日志级别

Python logging模块定义了以下日志级别（按严重程度递增）：

1. **DEBUG**：详细信息，通常只在诊断问题时使用
2. **INFO**：确认应用按预期工作
3. **WARNING**：表明发生了意外情况，但应用仍能正常工作
4. **ERROR**：由于严重问题，应用的某些功能不能正常工作
5. **CRITICAL**：严重错误，表明应用本身可能无法继续运行

```python
app.logger.debug('Debug message')
app.logger.info('Info message')
app.logger.warning('Warning message')
app.logger.error('Error message')
app.logger.critical('Critical message')
```

## 2. 日志配置与管理

### 2.1 基本日志配置

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    # 确保日志目录存在
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10240,  # 10KB
        backupCount=10   # 保留10个备份文件
    )
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    
    # 设置日志级别
    file_handler.setLevel(logging.INFO)
    
    # 添加处理器到应用日志器
    app.logger.addHandler(file_handler)
    
    # 设置应用日志级别
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

# 在应用初始化时调用
app = Flask(__name__)
configure_logging(app)
```

### 2.2 高级日志配置

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    },
    'loggers': {
        'app': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'error_file'],
            'propagate': False
        }
    }
}

# 应用日志配置
logging.config.dictConfig(LOGGING_CONFIG)
```

### 2.3 环境相关的日志配置

```python
import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

def configure_logging(app):
    # 根据环境设置不同的日志级别
    if not app.debug and not app.testing:
        # 生产环境配置
        
        # 邮件通知错误
        if app.config.get('MAIL_SERVER'):
            auth = None
            if app.config.get('MAIL_USERNAME') or app.config.get('MAIL_PASSWORD'):
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
            secure = None
            if app.config.get('MAIL_USE_TLS'):
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_USERNAME'],
                toaddrs=app.config['ADMINS'],
                subject='Flask App Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        
        # 文件日志
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')
```

## 3. 结构化日志记录

### 3.1 JSON格式日志

```python
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """自定义JSON格式化器"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# 使用JSON格式化器
def configure_json_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/app.json',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(JSONFormatter())
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### 3.2 请求上下文日志

```python
from flask import g, request
import uuid

@app.before_request
def before_request():
    # 为每个请求生成唯一ID
    g.request_id = str(uuid.uuid4())
    
    # 记录请求开始
    app.logger.info(
        f"Request started: {request.method} {request.url}",
        extra={
            'request_id': g.request_id,
            'method': request.method,
            'url': request.url,
            'user_agent': request.headers.get('User-Agent')
        }
    )

@app.after_request
def after_request(response):
    # 记录请求结束
    app.logger.info(
        f"Request completed: {response.status_code}",
        extra={
            'request_id': g.request_id,
            'status_code': response.status_code,
            'content_length': response.content_length
        }
    )
    return response

# 在视图函数中使用
@app.route('/user/<int:user_id>')
def get_user(user_id):
    g.user_id = user_id  # 将用户ID添加到请求上下文
    
    app.logger.info(
        f"Fetching user {user_id}",
        extra={
            'request_id': g.request_id,
            'user_id': user_id,
            'action': 'get_user'
        }
    )
    
    # 获取用户逻辑
    user = fetch_user(user_id)
    
    if user:
        return user.to_dict()
    else:
        app.logger.warning(
            f"User {user_id} not found",
            extra={
                'request_id': g.request_id,
                'user_id': user_id,
                'action': 'user_not_found'
            }
        )
        return {"error": "User not found"}, 404
```

## 4. 日志级别与分类

### 4.1 自定义日志级别

```python
import logging

# 定义自定义日志级别
AUDIT = 25
logging.addLevelName(AUDIT, 'AUDIT')

def audit(self, message, *args, **kwargs):
    if self.isEnabledFor(AUDIT):
        self._log(AUDIT, message, args, **kwargs)

logging.Logger.audit = audit

# 使用自定义日志级别
app.logger.audit('User login attempt', extra={'user_id': 123})
```

### 4.2 多个日志器

```python
# 创建不同的日志器用于不同目的
security_logger = logging.getLogger('security')
performance_logger = logging.getLogger('performance')
business_logger = logging.getLogger('business')

# 配置不同的处理器
def configure_specialized_loggers():
    # 安全日志器
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=10240000,
        backupCount=10
    )
    security_handler.setLevel(logging.WARNING)
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    # 性能日志器
    performance_handler = RotatingFileHandler(
        'logs/performance.log',
        maxBytes=10240000,
        backupCount=10
    )
    performance_handler.setLevel(logging.INFO)
    performance_logger.addHandler(performance_handler)
    performance_logger.setLevel(logging.INFO)

# 在应用中使用
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # 安全日志
    security_logger.info(
        'Login attempt',
        extra={
            'username': username,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
    )
    
    # 登录逻辑
    if authenticate_user(username, password):
        security_logger.info(
            'Login successful',
            extra={'username': username}
        )
        return redirect('/dashboard')
    else:
        security_logger.warning(
            'Login failed',
            extra={'username': username}
        )
        return "Invalid credentials", 401
```

## 5. 日志轮转与存储

### 5.1 时间轮转日志

```python
from logging.handlers import TimedRotatingFileHandler
import logging

def configure_timed_rotation(app):
    # 按天轮转日志
    timed_handler = TimedRotatingFileHandler(
        'logs/app.log',
        when='midnight',
        interval=1,
        backupCount=30  # 保留30天的日志
    )
    timed_handler.setLevel(logging.INFO)
    timed_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    app.logger.addHandler(timed_handler)
    app.logger.setLevel(logging.INFO)

# 按小时轮转
hourly_handler = TimedRotatingFileHandler(
    'logs/app_hourly.log',
    when='H',
    interval=1,
    backupCount=24
)
```

### 5.2 大小轮转日志

```python
from logging.handlers import RotatingFileHandler

def configure_size_rotation(app):
    # 按大小轮转（每个文件最大100MB，保留10个备份）
    size_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=104857600,  # 100MB
        backupCount=10
    )
    size_handler.setLevel(logging.INFO)
    size_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    app.logger.addHandler(size_handler)
    app.logger.setLevel(logging.INFO)
```

## 6. 日志监控与分析

### 6.1 实时日志监控

```python
import threading
import time
from collections import deque

class LogMonitor:
    def __init__(self, log_file, error_threshold=5, time_window=60):
        self.log_file = log_file
        self.error_threshold = error_threshold
        self.time_window = time_window
        self.error_timestamps = deque()
        self.running = False
    
    def start_monitoring(self):
        """启动日志监控"""
        self.running = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_monitoring(self):
        """停止日志监控"""
        self.running = False
    
    def _monitor_loop(self):
        """监控循环"""
        last_position = 0
        
        while self.running:
            try:
                with open(self.log_file, 'r') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()
                
                # 分析新日志行
                for line in new_lines:
                    if 'ERROR' in line or 'CRITICAL' in line:
                        self._handle_error(line)
                
                # 清理过期的时间戳
                self._cleanup_timestamps()
                
                # 检查错误率
                self._check_error_rate()
                
            except Exception as e:
                app.logger.error(f"Log monitoring error: {e}")
            
            time.sleep(5)  # 每5秒检查一次
    
    def _handle_error(self, line):
        """处理错误日志"""
        timestamp = time.time()
        self.error_timestamps.append(timestamp)
        app.logger.warning(f"Error detected: {line.strip()}")
    
    def _cleanup_timestamps(self):
        """清理过期的时间戳"""
        cutoff_time = time.time() - self.time_window
        while self.error_timestamps and self.error_timestamps[0] < cutoff_time:
            self.error_timestamps.popleft()
    
    def _check_error_rate(self):
        """检查错误率"""
        if len(self.error_timestamps) >= self.error_threshold:
            app.logger.critical(
                f"High error rate detected: {len(self.error_timestamps)} errors "
                f"in the last {self.time_window} seconds"
            )
            # 可以在这里添加告警逻辑
            self._send_alert()

    def _send_alert(self):
        """发送告警"""
        # 实现告警逻辑（邮件、短信、Slack等）
        pass

# 使用日志监控
log_monitor = LogMonitor('logs/app.log')
log_monitor.start_monitoring()
```

### 6.2 日志分析工具

```python
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

class LogAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
    
    def analyze_errors(self, hours=24):
        """分析指定时间范围内的错误"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        errors = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                # 解析日志行
                match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+): (.+)', line)
                if match:
                    timestamp_str, level, message = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    if timestamp >= cutoff_time and level in ['ERROR', 'CRITICAL']:
                        errors.append({
                            'timestamp': timestamp,
                            'level': level,
                            'message': message
                        })
        
        return errors
    
    def get_error_statistics(self, hours=24):
        """获取错误统计信息"""
        errors = self.analyze_errors(hours)
        error_counts = Counter()
        error_by_hour = defaultdict(int)
        
        for error in errors:
            # 统计错误类型
            message = error['message']
            if 'Database' in message:
                error_counts['Database'] += 1
            elif 'Network' in message:
                error_counts['Network'] += 1
            elif 'Authentication' in message:
                error_counts['Authentication'] += 1
            else:
                error_counts['Other'] += 1
            
            # 按小时统计
            hour = error['timestamp'].hour
            error_by_hour[hour] += 1
        
        return {
            'total_errors': len(errors),
            'error_types': dict(error_counts),
            'errors_by_hour': dict(error_by_hour)
        }
    
    def generate_report(self, hours=24):
        """生成日志分析报告"""
        stats = self.get_error_statistics(hours)
        
        report = f"""
Flask Application Log Analysis Report
====================================
Time Period: Last {hours} hours
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total Errors: {stats['total_errors']}
- Error Types:
"""
        
        for error_type, count in stats['error_types'].items():
            report += f"  {error_type}: {count}\n"
        
        report += "\nErrors by Hour:\n"
        for hour in sorted(stats['errors_by_hour'].keys()):
            count = stats['errors_by_hour'][hour]
            report += f"  {hour:02d}:00 - {count} errors\n"
        
        return report

# 使用日志分析器
analyzer = LogAnalyzer('logs/app.log')
report = analyzer.generate_report(hours=24)
print(report)
```

## 7. 第三方日志服务集成

### 7.1 Sentry集成

```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def configure_sentry(app):
    sentry_sdk.init(
        dsn="YOUR_SENTRY_DSN",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,  # 性能监控采样率
        environment=app.config.get('ENVIRONMENT', 'development')
    )

# 在应用中使用
@app.route('/error-test')
def error_test():
    # 这个错误会被自动发送到Sentry
    division_by_zero = 1 / 0
    return "This will never be reached"
```

### 7.2 ELK Stack集成

```python
import logging
from pythonjsonlogger import jsonlogger

def configure_elk_logging(app):
    # 安装: pip install python-json-logger
    
    # JSON格式化日志
    json_handler = logging.StreamHandler()
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    json_handler.setFormatter(json_formatter)
    
    app.logger.addHandler(json_handler)
    app.logger.setLevel(logging.INFO)

# 配合Filebeat或Logstash使用
```

### 7.3 Datadog集成

```bash
pip install ddtrace
```

```python
from ddtrace import patch_all
patch_all()  # 自动patch Flask和其他库

# 启动应用时使用:
# ddtrace-run python app.py
```

## 8. 安全日志与审计

### 8.1 用户行为审计

```python
from datetime import datetime

class AuditLogger:
    def __init__(self, app):
        self.app = app
        self.audit_logger = logging.getLogger('audit')
        
        # 配置审计日志
        handler = RotatingFileHandler(
            'logs/audit.log',
            maxBytes=10240000,
            backupCount=10
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s'
        ))
        self.audit_logger.addHandler(handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def log_user_action(self, user_id, action, details=None):
        """记录用户操作"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'ip_address': getattr(g, 'ip_address', 'unknown'),
            'user_agent': getattr(g, 'user_agent', 'unknown')
        }
        
        self.audit_logger.info(
            f"AUDIT: User {user_id} performed {action}",
            extra=audit_entry
        )

# 初始化审计日志
audit_logger = AuditLogger(app)

# 在视图中使用
@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # 记录审计日志
    audit_logger.log_user_action(
        user_id=g.current_user.id,
        action='delete_user',
        details={'target_user_id': user_id}
    )
    
    # 执行删除操作
    delete_user_from_database(user_id)
    return {"message": "User deleted successfully"}
```

### 8.2 敏感信息处理

```python
import re

class SensitiveDataFilter(logging.Filter):
    """过滤敏感信息的日志过滤器"""
    
    def filter(self, record):
        # 过滤密码
        if isinstance(record.args, dict):
            for key in record.args:
                if 'password' in key.lower() or 'token' in key.lower():
                    record.args[key] = '***REDACTED***'
        
        # 过滤日志消息中的敏感信息
        if hasattr(record, 'msg'):
            # 过滤邮箱
            record.msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                              '***EMAIL***', str(record.msg))
            # 过滤电话号码
            record.msg = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '***PHONE***', str(record.msg))
        
        return True

# 应用敏感信息过滤器
def configure_secure_logging(app):
    sensitive_filter = SensitiveDataFilter()
    
    for handler in app.logger.handlers:
        handler.addFilter(sensitive_filter)
```

## 9. 性能优化与最佳实践

### 9.1 异步日志记录

```python
import logging
import logging.handlers
import queue
import threading

def configure_async_logging(app):
    """配置异步日志记录"""
    # 创建队列
    log_queue = queue.Queue(-1)  # 无限制队列
    
    # 创建队列处理器
    queue_handler = logging.handlers.QueueHandler(log_queue)
    app.logger.addHandler(queue_handler)
    
    # 创建文件处理器
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # 创建队列监听器
    listener = logging.handlers.QueueListener(log_queue, file_handler)
    listener.start()
    
    # 应用关闭时停止监听器
    import atexit
    atexit.register(listener.stop)
```

### 9.2 日志采样

```python
import random

class SamplingFilter(logging.Filter):
    """日志采样过滤器"""
    
    def __init__(self, sample_rate=0.1):
        super().__init__()
        self.sample_rate = sample_rate
    
    def filter(self, record):
        # DEBUG和INFO级别按采样率记录
        if record.levelno <= logging.INFO:
            return random.random() < self.sample_rate
        # WARNING及以上级别全部记录
        return True

# 应用采样过滤器
def configure_sampling_logging(app):
    sampling_filter = SamplingFilter(sample_rate=0.01)  # 1%采样率
    
    for handler in app.logger.handlers:
        handler.addFilter(sampling_filter)
```

### 9.3 日志性能优化

```python
import logging

class PerformanceOptimizedFormatter(logging.Formatter):
    """性能优化的日志格式化器"""
    
    def format(self, record):
        # 预编译格式字符串
        if not hasattr(self, '_style'):
            return super().format(record)
        
        # 避免重复的字符串操作
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        
        # 使用预编译的格式
        s = self._style.format(record)
        return s

def configure_performance_logging(app):
    """配置高性能日志"""
    # 减少日志格式的复杂度
    formatter = PerformanceOptimizedFormatter(
        '%(asctime)s %(levelname)s: %(message)s'
    )
    
    # 避免在生产环境中记录DEBUG级别日志
    if not app.debug:
        app.logger.setLevel(logging.INFO)
    
    # 使用缓冲日志处理器
    handler = logging.handlers.MemoryHandler(
        capacity=100,
        target=logging.FileHandler('logs/app.log')
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
```

### 9.4 完整配置示例

```python
import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging.config

class LoggingConfig:
    """日志配置类"""
    
    @staticmethod
    def init_app(app):
        """初始化应用日志配置"""
        # 确保日志目录存在
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 根据环境配置日志
        if app.config.get('TESTING'):
            LoggingConfig._configure_testing_logging(app)
        elif app.config.get('DEBUG'):
            LoggingConfig._configure_development_logging(app)
        else:
            LoggingConfig._configure_production_logging(app)
    
    @staticmethod
    def _configure_development_logging(app):
        """开发环境日志配置"""
        app.logger.setLevel(logging.DEBUG)
        
        # 控制台日志
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        app.logger.addHandler(console_handler)
    
    @staticmethod
    def _configure_production_logging(app):
        """生产环境日志配置"""
        app.logger.setLevel(logging.INFO)
        
        # 文件日志（按大小轮转）
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        app.logger.addHandler(file_handler)
        
        # 错误日志（单独文件）
        error_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=10485760,
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        app.logger.addHandler(error_handler)
        
        # 审计日志
        audit_handler = TimedRotatingFileHandler(
            'logs/audit.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger = logging.getLogger('audit')
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
    
    @staticmethod
    def _configure_testing_logging(app):
        """测试环境日志配置"""
        app.logger.setLevel(logging.CRITICAL)
        
        # 禁用大多数日志输出
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

# 在应用初始化时使用
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化日志配置
    LoggingConfig.init_app(app)
    
    return app
```

## 总结

Flask日志管理与监控是应用运维的重要组成部分。通过合理的配置和使用，可以：

1. **快速定位问题**：详细的日志记录帮助快速诊断和解决问题
2. **监控应用状态**：实时监控应用运行状态和性能指标
3. **安全审计**：记录用户行为和安全相关事件
4. **性能优化**：通过日志分析发现性能瓶颈
5. **合规要求**：满足行业和法规的日志记录要求

在实际应用中，应该根据具体需求选择合适的日志策略，平衡日志详细程度与性能影响，并建立完善的日志监控和分析体系。