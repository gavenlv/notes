# 第5章：Gunicorn监控与日志管理

## 章节概述

有效的监控和日志管理是维护稳定、高性能Web应用的关键。在本章中，我们将深入探讨如何监控Gunicorn服务器的状态、收集和分析日志、设置警报，以及使用专业工具提高运维效率。

## 学习目标

- 掌握Gunicorn日志配置和管理方法
- 了解不同的监控指标和收集方式
- 学会使用专业监控工具监控Gunicorn
- 掌握日志分析和故障定位技巧
- 学会设置有效的警报和通知系统

## 5.1 Gunicorn日志系统

### 5.1.1 日志类型

Gunicorn产生多种类型的日志：

1. **访问日志（Access Log）**：记录所有HTTP请求
2. **错误日志（Error Log）**：记录服务器错误和异常
3. **应用日志（Application Log）**：由应用程序产生的日志
4. **调试日志（Debug Log）**：详细的调试信息

### 5.1.2 日志配置

Gunicorn提供了丰富的日志配置选项：

```python
# gunicorn.conf.py
# 基本日志配置
accesslog = "/var/log/gunicorn/access.log"    # 访问日志路径
errorlog = "/var/log/gunicorn/error.log"      # 错误日志路径
loglevel = "info"                            # 日志级别
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 日志级别：debug, info, warning, error, critical
# 生产环境通常使用warning或error级别
loglevel = "warning"

# 是否将错误信息发送到syslog
syslog = False

# Syslog地址
syslog_addr = "unix:///var/run/syslog"
syslog_facility = "user"
syslog_prefix = "gunicorn"
```

### 5.1.3 自定义日志格式

Gunicorn支持自定义访问日志格式：

```python
# gunicorn.conf.py
# 标准访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 增强格式，包含更多详细信息
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s {%(h)s} "%(x)s"'

# JSON格式日志（便于日志分析工具处理）
access_log_format = '{"remote_addr": "%(h)s", "remote_user": "%(u)s", "request": "%(r)s", "status": %(s)s, "response_length": %(b)s, "referrer": "%(f)s", "user_agent": "%(a)s", "request_time": %(D)s, "timestamp": "%(t)s"}'

# 可用的日志变量：
# h: 远程地址
# l: 远程登录名（通常为-）
# u: 远程用户（如果经过认证）
# t: 时间戳
# r: 请求行（方法、URI、协议）
# s: 状态码
# b: 响应长度（字节）
# f: 引用页
# a: 用户代理
# T: 请求时间（秒）
# D: 请求时间（毫秒）
# p: 进程ID
# {header}i: 任意请求头
```

## 5.2 日志轮转与管理

### 5.2.1 使用logrotate进行日志轮转

logrotate是Linux系统中常用的日志管理工具：

```bash
# /etc/logrotate.d/gunicorn
/var/log/gunicorn/*.log {
    daily                     # 每天轮转
    missingok                 # 如果日志文件不存在，不报错
    rotate 30                 # 保留30天的日志
    compress                  # 压缩旧日志
    delaycompress             # 延迟压缩
    notifempty                # 如果日志为空则不轮转
    create 644 www-data www-data  # 创建新日志文件的权限和所有者
    postrotate
        # 向Gunicorn发送USR1信号，重新打开日志文件
        kill -USR1 $(cat /var/run/gunicorn.pid)
    endscript
}
```

### 5.2.2 使用Python日志库

在应用中使用Python标准库的logging模块：

```python
# app.py
import logging
import logging.handlers

# 配置应用日志
def setup_logging():
    # 创建应用日志器
    app_logger = logging.getLogger('myapp')
    app_logger.setLevel(logging.INFO)
    
    # 文件处理器（带轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        '/var/log/myapp/app.log', 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    ))
    app_logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    ))
    app_logger.addHandler(console_handler)
    
    return app_logger

# 在应用中使用
logger = setup_logging()

def my_view():
    logger.info("Processing request")
    try:
        # 业务逻辑
        logger.debug("Processing completed successfully")
        return "Success"
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
```

## 5.3 监控指标

### 5.3.1 关键性能指标（KPI）

监控以下关键指标有助于评估Gunicorn性能：

1. **吞吐量指标**：
   - 每秒请求数（RPS）
   - 每分钟请求数（RPM）
   - 数据传输速率（MB/s）

2. **延迟指标**：
   - 平均响应时间
   - 95%百分位响应时间（P95）
   - 最大响应时间

3. **资源使用指标**：
   - CPU使用率
   - 内存使用量
   - 活跃连接数
   - 网络I/O

4. **错误指标**：
   - 4xx错误率
   - 5xx错误率
   - 超时请求率
   - Worker崩溃次数

### 5.3.2 获取监控数据

使用不同方式获取Gunicorn监控数据：

```python
# metrics_collector.py
import psutil
import time
from collections import defaultdict, deque
import threading

class GunicornMetrics:
    def __init__(self, stats_file='/var/tmp/gunicorn.stats'):
        self.stats_file = stats_file
        self.metrics = defaultdict(deque)
        self.lock = threading.Lock()
    
    def collect_system_metrics(self):
        """收集系统指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return {
            'timestamp': time.time(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used': memory.used,
            'memory_available': memory.available,
            'disk_percent': disk.percent,
            'network_bytes_sent': network.bytes_sent,
            'network_bytes_recv': network.bytes_recv
        }
    
    def collect_process_metrics(self, pid):
        """收集Gunicorn进程指标"""
        try:
            process = psutil.Process(pid)
            children = process.children(recursive=True)
            
            # 主进程指标
            metrics = {
                'timestamp': time.time(),
                'main_process': {
                    'pid': pid,
                    'cpu_percent': process.cpu_percent(),
                    'memory_info': process.memory_info()._asdict(),
                    'status': process.status(),
                    'create_time': process.create_time()
                },
                'worker_processes': []
            }
            
            # Worker进程指标
            for child in children:
                worker_metrics = {
                    'pid': child.pid,
                    'cpu_percent': child.cpu_percent(),
                    'memory_info': child.memory_info()._asdict(),
                    'status': child.status(),
                    'create_time': child.create_time()
                }
                metrics['worker_processes'].append(worker_metrics)
            
            return metrics
        
        except psutil.NoSuchProcess:
            return None
    
    def save_metrics(self, metrics_type, metrics_data):
        """保存指标数据"""
        with self.lock:
            self.metrics[metrics_type].append(metrics_data)
            # 只保留最近1000条数据
            if len(self.metrics[metrics_type]) > 1000:
                self.metrics[metrics_type].popleft()
    
    def get_latest_metrics(self, metrics_type, count=10):
        """获取最新的指标数据"""
        with self.lock:
            return list(self.metrics[metrics_type])[-count:]

# 在Gunicorn配置中使用
def post_fork(server, worker):
    """Worker进程启动时执行"""
    server.metrics = GunicornMetrics()
    server.log.info("Metrics collector initialized")

def worker_exit(server, worker):
    """Worker进程退出时执行"""
    server.log.info("Worker %s exited", worker.pid)

def when_ready(server):
    """服务器启动时执行"""
    server.metrics = GunicornMetrics()
    server.log.info("Metrics collector initialized")
```

## 5.4 集成监控系统

### 5.4.1 Prometheus监控

集成Prometheus进行专业的监控：

```python
# prometheus_integration.py
from prometheus_client import start_http_server, Summary, Gauge, Counter, Histogram, generate_latest
import time
import psutil

# 定义指标
REQUEST_COUNT = Counter('gunicorn_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('gunicorn_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('gunicorn_active_connections', 'Active connections')
WORKER_PROCESSES = Gauge('gunicorn_worker_processes', 'Number of worker processes')
CPU_USAGE = Gauge('gunicorn_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('gunicorn_memory_usage_bytes', 'Memory usage in bytes')

class PrometheusMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        start_time = time.time()
        
        # 捕获原始的start_response
        def custom_start_response(status, headers, exc_info=None):
            # 记录指标
            method = environ.get('REQUEST_METHOD', 'unknown')
            endpoint = environ.get('PATH_INFO', 'unknown')
            status_code = status.split()[0]
            
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
            
            return start_response(status, headers, exc_info)
        
        # 处理请求
        response = self.app(environ, custom_start_response)
        
        # 记录请求时间
        REQUEST_DURATION.observe(time.time() - start_time)
        
        return response

def start_metrics_server():
    """启动Prometheus指标服务器"""
    start_http_server(8001)  # 在8001端口提供指标

def update_system_metrics():
    """更新系统指标"""
    CPU_USAGE.set(psutil.cpu_percent())
    memory = psutil.virtual_memory()
    MEMORY_USAGE.set(memory.used)

# 在Gunicorn配置中使用
def on_starting(server):
    """服务器启动时执行"""
    start_metrics_server()
    server.log.info("Prometheus metrics server started on port 8001")

def worker_exit(server, worker):
    """Worker进程退出时执行"""
    server.log.info("Worker %s exited", worker.pid)
    # 更新Worker进程数量
    WORKER_PROCESSES.dec()

def post_fork(server, worker):
    """Worker进程启动时执行"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)
    # 更新Worker进程数量
    WORKER_PROCESSES.inc()

# 在应用中使用
from flask import Flask
app = Flask(__name__)

# 添加Prometheus中间件
app.wsgi_app = PrometheusMiddleware(app.wsgi_app)

@app.route('/')
def hello():
    return "Hello, Prometheus!"
```

### 5.4.2 StatsD监控

集成StatsD进行监控：

```python
# statsd_integration.py
import statsd
import time

# 创建StatsD客户端
statsd_client = statsd.StatsClient('localhost', 8125, prefix='gunicorn')

class StatsDMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        start_time = time.time()
        
        # 捕获原始的start_response
        def custom_start_response(status, headers, exc_info=None):
            # 记录指标
            method = environ.get('REQUEST_METHOD', 'unknown')
            endpoint = environ.get('PATH_INFO', 'unknown')
            status_code = status.split()[0]
            
            # 发送计数器
            statsd_client.incr('requests.count', tags=[f'method:{method}', f'endpoint:{endpoint}', f'status:{status_code}'])
            
            return start_response(status, headers, exc_info)
        
        # 处理请求
        response = self.app(environ, custom_start_response)
        
        # 记录请求时间
        request_time = time.time() - start_time
        statsd_client.timing('request.duration', int(request_time * 1000))  # 转换为毫秒
        
        return response

def update_worker_metrics(server):
    """更新Worker指标"""
    # 获取Worker进程数量
    worker_count = len(server.cfg.workers) if hasattr(server.cfg, 'workers') else 0
    statsd_client.gauge('workers.count', worker_count)
    
    # 获取活跃连接数（如果有）
    if hasattr(server, 'connections'):
        statsd_client.gauge('connections.active', len(server.connections))

# 在应用中使用
from flask import Flask
app = Flask(__name__)

# 添加StatsD中间件
app.wsgi_app = StatsDMiddleware(app.wsgi_app)

@app.route('/')
def hello():
    return "Hello, StatsD!"
```

## 5.5 日志分析

### 5.5.1 使用ELK Stack分析日志

ELK Stack（Elasticsearch, Logstash, Kibana）是强大的日志分析解决方案：

```conf
# logstash.conf
input {
    file {
        path => "/var/log/gunicorn/access.log"
        start_position => "beginning"
        type => "gunicorn_access"
    }
    
    file {
        path => "/var/log/gunicorn/error.log"
        start_position => "beginning"
        type => "gunicorn_error"
    }
}

filter {
    if [type] == "gunicorn_access" {
        # 解析访问日志
        grok {
            match => { "message" => '%{IPORHOST:remote_addr} - %{DATA:remote_user} \[%{HTTPDATE:time_local}\] "%{WORD:request_method} %{DATA:request_uri} HTTP/%{NUMBER:http_version}" %{NUMBER:status} %{NUMBER:body_bytes_sent} "%{DATA:http_referer}" "%{DATA:http_user_agent}" %{NUMBER:request_time:float}' }
        }
        
        # 转换字段类型
        mutate {
            convert => { "status" => "integer" }
            convert => { "body_bytes_sent" => "integer" }
            convert => { "request_time" => "float" }
        }
        
        # 添加时间戳
        date {
            match => [ "time_local", "dd/MMM/yyyy:HH:mm:ss Z" ]
        }
    }
    
    if [type] == "gunicorn_error" {
        # 解析错误日志
        grok {
            match => { "message" => '\[%{TIMESTAMP_ISO8601:timestamp}\] \[%{LOGLEVEL:log_level}\] %{DATA:pid} %{GREEDYDATA:message}' }
        }
    }
}

output {
    elasticsearch {
        hosts => ["localhost:9200"]
        index => "gunicorn-%{+YYYY.MM.dd}"
    }
    
    # 输出到标准输出，便于调试
    stdout {
        codec => rubydebug
    }
}
```

### 5.5.2 使用Python分析日志

使用Python脚本分析日志：

```python
# log_analyzer.py
import re
from collections import defaultdict
import datetime

class GunicornLogAnalyzer:
    def __init__(self, access_log_path):
        self.access_log_path = access_log_path
        self.access_pattern = re.compile(r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" (?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)" (?P<response_time>[\d\.]+)')
    
    def parse_access_log(self, max_lines=None):
        """解析访问日志"""
        entries = []
        
        with open(self.access_log_path, 'r') as f:
            for i, line in enumerate(f):
                if max_lines and i >= max_lines:
                    break
                
                match = self.access_pattern.match(line)
                if match:
                    entry = {
                        'ip': match.group('ip'),
                        'timestamp': match.group('timestamp'),
                        'method': match.group('method'),
                        'path': match.group('path'),
                        'status': int(match.group('status')),
                        'size': int(match.group('size')),
                        'referer': match.group('referer'),
                        'user_agent': match.group('user_agent'),
                        'response_time': float(match.group('response_time'))
                    }
                    entries.append(entry)
        
        return entries
    
    def analyze_status_codes(self, entries):
        """分析HTTP状态码分布"""
        status_counts = defaultdict(int)
        
        for entry in entries:
            status = entry['status']
            status_category = f"{status // 100}xx"
            status_counts[status] += 1
            status_counts[status_category] += 1
        
        return status_counts
    
    def analyze_response_times(self, entries):
        """分析响应时间"""
        response_times = [entry['response_time'] for entry in entries]
        
        if not response_times:
            return {}
        
        return {
            'min': min(response_times),
            'max': max(response_times),
            'avg': sum(response_times) / len(response_times),
            'p50': self._percentile(response_times, 50),
            'p95': self._percentile(response_times, 95),
            'p99': self._percentile(response_times, 99)
        }
    
    def analyze_top_paths(self, entries, limit=10):
        """分析最受欢迎的路径"""
        path_counts = defaultdict(int)
        
        for entry in entries:
            path_counts[entry['path']] += 1
        
        return sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def analyze_top_ips(self, entries, limit=10):
        """分析访问最频繁的IP"""
        ip_counts = defaultdict(int)
        
        for entry in entries:
            ip_counts[entry['ip']] += 1
        
        return sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def analyze_hourly_requests(self, entries):
        """分析每小时的请求数"""
        hourly_counts = defaultdict(int)
        
        for entry in entries:
            timestamp = datetime.datetime.strptime(entry['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
            hour = timestamp.hour
            hourly_counts[hour] += 1
        
        return dict(hourly_counts)
    
    def _percentile(self, values, p):
        """计算百分位数"""
        if not values:
            return None
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * p / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

# 使用示例
if __name__ == "__main__":
    analyzer = GunicornLogAnalyzer('/var/log/gunicorn/access.log')
    entries = analyzer.parse_access_log()
    
    print("Status Code Distribution:")
    status_codes = analyzer.analyze_status_codes(entries)
    for code, count in status_codes.items():
        print(f"  {code}: {count}")
    
    print("\nResponse Times:")
    response_times = analyzer.analyze_response_times(entries)
    for metric, value in response_times.items():
        print(f"  {metric}: {value:.3f}s")
    
    print("\nTop Paths:")
    top_paths = analyzer.analyze_top_paths(entries)
    for path, count in top_paths:
        print(f"  {path}: {count}")
```

## 5.6 警报和通知

### 5.6.1 设置警报规则

使用Prometheus和Alertmanager设置警报：

```yaml
# alert_rules.yml
groups:
  - name: gunicorn_alerts
    rules:
      # 高错误率警报
      - alert: HighErrorRate
        expr: rate(gunicorn_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Gunicorn error rate is {{ $value }} errors per second"
      
      # 高响应时间警报
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(gunicorn_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"
      
      # 高CPU使用率警报
      - alert: HighCpuUsage
        expr: gunicorn_cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "Gunicorn CPU usage is {{ $value }}%"
      
      # 高内存使用警报
      - alert: HighMemoryUsage
        expr: gunicorn_memory_usage_bytes / (1024 * 1024 * 1024) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Gunicorn memory usage is {{ $value }}GB"
      
      # Worker崩溃警报
      - alert: WorkerCrash
        expr: increase(gunicorn_worker_processes[5m]) < 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Gunicorn worker crash detected"
          description: "One or more Gunicorn workers have crashed"
```

### 5.6.2 自定义警报系统

实现自定义警报系统：

```python
# alert_system.py
import smtplib
import requests
import time
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertManager:
    def __init__(self, config_file='alerts_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.alert_history = {}
    
    def check_metrics(self, metrics):
        """检查指标并发送警报"""
        for rule in self.config['rules']:
            if self._check_rule(rule, metrics):
                self._send_alert(rule, metrics)
    
    def _check_rule(self, rule, metrics):
        """检查单个警报规则"""
        metric_name = rule['metric']
        operator = rule['operator']
        threshold = rule['threshold']
        
        if metric_name not in metrics:
            return False
        
        value = metrics[metric_name]
        
        if operator == 'gt':
            return value > threshold
        elif operator == 'lt':
            return value < threshold
        elif operator == 'eq':
            return value == threshold
        
        return False
    
    def _send_alert(self, rule, metrics):
        """发送警报通知"""
        rule_name = rule['name']
        
        # 防止重复警报
        if rule_name in self.alert_history:
            time_since_last = time.time() - self.alert_history[rule_name]['last_sent']
            cooldown = rule.get('cooldown', 300)  # 默认5分钟冷却时间
            if time_since_last < cooldown:
                return
        
        # 记录警报历史
        self.alert_history[rule_name] = {
            'last_sent': time.time(),
            'message': rule['message'].format(**metrics)
        }
        
        # 发送邮件通知
        if 'email' in rule.get('notifications', {}):
            self._send_email_alert(rule, metrics)
        
        # 发送Slack通知
        if 'slack' in rule.get('notifications', {}):
            self._send_slack_alert(rule, metrics)
        
        # 发送Webhook通知
        if 'webhook' in rule.get('notifications', {}):
            self._send_webhook_alert(rule, metrics)
    
    def _send_email_alert(self, rule, metrics):
        """发送邮件警报"""
        email_config = rule['notifications']['email']
        
        subject = f"Alert: {rule['name']}"
        message = rule['message'].format(**metrics)
        
        msg = MIMEMultipart()
        msg['From'] = email_config['from']
        msg['To'] = ', '.join(email_config['to'])
        msg['Subject'] = subject
        
        body = MIMEText(message, 'plain')
        msg.attach(body)
        
        try:
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                if email_config.get('use_tls', True):
                    server.starttls()
                
                if 'username' in email_config and 'password' in email_config:
                    server.login(email_config['username'], email_config['password'])
                
                server.send_message(msg)
                
            print(f"Email alert sent for rule: {rule['name']}")
        
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
    
    def _send_slack_alert(self, rule, metrics):
        """发送Slack警报"""
        slack_config = rule['notifications']['slack']
        
        webhook_url = slack_config['webhook_url']
        channel = slack_config.get('channel', '#alerts')
        username = slack_config.get('username', 'GunicornBot')
        
        payload = {
            'channel': channel,
            'username': username,
            'text': rule['message'].format(**metrics),
            'icon_emoji': ':warning:'
        }
        
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            print(f"Slack alert sent for rule: {rule['name']}")
        
        except Exception as e:
            print(f"Failed to send Slack alert: {str(e)}")
    
    def _send_webhook_alert(self, rule, metrics):
        """发送Webhook警报"""
        webhook_config = rule['notifications']['webhook']
        
        url = webhook_config['url']
        method = webhook_config.get('method', 'POST')
        headers = webhook_config.get('headers', {})
        
        payload = {
            'rule_name': rule['name'],
            'message': rule['message'].format(**metrics),
            'metrics': metrics,
            'timestamp': time.time()
        }
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, json=payload, headers=headers)
            elif method.upper() == 'GET':
                response = requests.get(url, params=payload, headers=headers)
            
            response.raise_for_status()
            
            print(f"Webhook alert sent for rule: {rule['name']}")
        
        except Exception as e:
            print(f"Failed to send webhook alert: {str(e)}")

# 警报配置示例
"""
{
  "rules": [
    {
      "name": "high_error_rate",
      "metric": "error_rate",
      "operator": "gt",
      "threshold": 0.05,
      "message": "High error rate detected: {error_rate:.2%}",
      "cooldown": 300,
      "notifications": {
        "email": {
          "smtp_server": "smtp.example.com",
          "smtp_port": 587,
          "use_tls": true,
          "username": "alerts@example.com",
          "password": "password",
          "from": "alerts@example.com",
          "to": ["admin@example.com"]
        },
        "slack": {
          "webhook_url": "https://hooks.slack.com/services/...",
          "channel": "#alerts",
          "username": "GunicornAlertBot"
        },
        "webhook": {
          "url": "https://api.example.com/alerts",
          "method": "POST",
          "headers": {
            "Authorization": "Bearer token123"
          }
        }
      }
    }
  ]
}
"""

# 在Gunicorn配置中使用
def worker_exit(server, worker):
    """Worker进程退出时执行"""
    server.log.info("Worker %s exited", worker.pid)
    
    # 检查是否需要发送警报
    if hasattr(server, 'alert_manager'):
        # 计算Worker崩溃指标
        metrics = {
            'worker_crash': True,
            'worker_pid': worker.pid
        }
        
        server.alert_manager.check_metrics(metrics)
```

## 5.7 健康检查

### 5.7.1 实现健康检查端点

在应用中实现健康检查端点：

```python
# health_check.py
import time
import psutil
import threading
from functools import wraps
from flask import Flask, jsonify, request

app = Flask(__name__)

# 健康状态
health_status = {
    'status': 'ok',
    'timestamp': time.time(),
    'checks': {}
}

# 锁，防止并发更新
health_lock = threading.Lock()

def health_check(name):
    """健康检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                status = 'ok' if result else 'error'
                message = str(result) if isinstance(result, str) else "OK"
            except Exception as e:
                status = 'error'
                message = str(e)
            
            with health_lock:
                health_status['checks'][name] = {
                    'status': status,
                    'message': message,
                    'timestamp': time.time()
                }
            
            return result
        
        return wrapper
    return decorator

@health_check('database')
def check_database():
    """检查数据库连接"""
    # 这里应该是实际的数据库连接检查
    # 示例中我们总是返回True
    return True

@health_check('cache')
def check_cache():
    """检查缓存连接"""
    # 这里应该是实际的缓存连接检查
    import redis
    try:
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        return True
    except:
        return False

@health_check('disk_space')
def check_disk_space():
    """检查磁盘空间"""
    disk_usage = psutil.disk_usage('/')
    percent_used = disk_usage.used / disk_usage.total
    
    # 如果磁盘使用率超过90%，返回False
    if percent_used > 0.9:
        return False
    
    return True

@health_check('memory')
def check_memory():
    """检查内存使用"""
    memory = psutil.virtual_memory()
    
    # 如果内存使用率超过95%，返回False
    if memory.percent > 95:
        return False
    
    return True

@app.route('/health')
def health():
    """健康检查端点"""
    # 执行所有健康检查
    check_database()
    check_cache()
    check_disk_space()
    check_memory()
    
    with health_lock:
        # 检查是否有任何检查失败
        all_checks_ok = all(
            check['status'] == 'ok' 
            for check in health_status['checks'].values()
        )
        
        # 更新整体状态
        if all_checks_ok:
            health_status['status'] = 'ok'
        else:
            health_status['status'] = 'degraded'
        
        health_status['timestamp'] = time.time()
        
        return jsonify(health_status), 200 if all_checks_ok else 503

@app.route('/health/ready')
def readiness():
    """就绪检查端点（Kubernetes就绪探针）"""
    # 检查应用是否准备好处理请求
    return jsonify({
        'status': 'ready',
        'timestamp': time.time()
    })

@app.route('/health/live')
def liveness():
    """存活检查端点（Kubernetes存活探针）"""
    # 检查应用是否存活
    return jsonify({
        'status': 'alive',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 5.7.2 Kubernetes健康检查配置

在Kubernetes中配置健康检查：

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gunicorn-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gunicorn-app
  template:
    metadata:
      labels:
        app: gunicorn-app
    spec:
      containers:
      - name: gunicorn-app
        image: your-registry/gunicorn-app:latest
        ports:
        - containerPort: 8000
        # 存活探针
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        # 就绪探针
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        # 启动探针
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 5.8 实践练习

### 5.8.1 练习1：实现日志分析

1. 使用Python脚本分析Gunicorn访问日志
2. 统计状态码分布、响应时间分布、热门页面
3. 生成简单的报告

### 5.8.2 练习2：集成Prometheus监控

1. 为Gunicorn应用添加Prometheus监控
2. 定义关键指标（请求计数、响应时间等）
3. 使用Grafana创建仪表板

### 5.8.3 练习3：设置警报系统

1. 实现简单的警报系统
2. 设置错误率、响应时间等警报规则
3. 配置邮件或Slack通知

## 5.9 本章小结

在本章中，我们学习了：

- Gunicorn日志系统的配置和管理
- 日志轮转和分析方法
- 关键监控指标和收集方法
- 集成专业监控工具（Prometheus、StatsD等）
- 实现警报和通知系统
- 设置健康检查端点

有效的监控和日志管理是维护稳定、高性能Web应用的关键。在下一章中，我们将探讨Gunicorn的高可用与负载均衡，进一步提高系统的可靠性。

## 5.10 参考资料

- [Gunicorn日志文档](https://docs.gunicorn.org/en/stable/settings.html#logging)
- [Prometheus最佳实践](https://prometheus.io/docs/practices/)
- [ELK Stack文档](https://www.elastic.co/guide/)
- [Kubernetes健康检查](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)