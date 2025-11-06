# Day 14: 监控与日志

## 用户故事 1: 系统监控配置

### 描述
作为系统管理员，我希望配置Superset的系统监控，以便实时了解系统性能、资源使用情况和潜在问题。

### 验收标准
- 能够监控Superset关键性能指标
- 配置资源使用监控（CPU、内存、磁盘等）
- 监控数据库连接和查询性能
- 设置性能基准和阈值告警

### 分步指南

#### 配置Prometheus指标导出

```python
# superset_config.py - 添加Prometheus指标配置

# 启用Prometheus指标导出
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

# 应用初始化后添加指标收集器
class SupersetMetrics:
    def __init__(self, app=None):
        self.metrics = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        # 初始化Prometheus指标收集器
        self.metrics = PrometheusMetrics(app)
        
        # 请求指标 - 按路径和状态码分组
        self.metrics.register_default(metrics=None)
        
        # 添加自定义指标
        self.add_custom_metrics()
    
    def add_custom_metrics(self):
        # 查询执行时间指标
        self.query_execution_time = self.metrics.gauge(
            'superset_query_execution_time_seconds',
            'SQL查询执行时间',
            ['database', 'query_type']
        )
        
        # 活动用户指标
        self.active_users = self.metrics.gauge(
            'superset_active_users',
            '当前活动用户数量'
        )
        
        # 数据库连接指标
        self.db_connections = self.metrics.gauge(
            'superset_db_connections',
            '数据库连接池状态',
            ['database', 'status']
        )

# 创建指标实例
SUPERSET_METRICS = SupersetMetrics()

# 自定义中间件 - 注册到Flask应用
def register_metrics(app):
    SUPERSET_METRICS.init_app(app)
    
    # 添加自定义请求处理钩子
    @app.after_request
    def add_metrics(response):
        # 可以在这里添加额外的指标收集
        return response

# 在应用初始化时调用
ADDITIONAL_MIDDLEWARE = [register_metrics]
```

#### Prometheus配置文件

```yaml
# prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # 监控Superset服务器
  - job_name: 'superset'
    metrics_path: '/admin/metrics'
    scrape_interval: 10s
    static_configs:
      - targets: ['superset-web:8088']
    
  # 监控Superset Worker
  - job_name: 'superset-worker'
    metrics_path: '/admin/metrics'
    scrape_interval: 10s
    static_configs:
      - targets: ['superset-worker:8088']
    
  # 监控PostgreSQL数据库
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  # 监控Redis缓存
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    
  # 监控Node节点
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

#### 自定义指标收集器

```python
# superset_metrics.py - 自定义指标收集器

from datetime import datetime, timedelta
from flask import g, current_app
from sqlalchemy import text
import psutil
import time

# 数据库查询性能监控
def monitor_query_performance(database, query, query_type="general"):
    """监控SQL查询执行性能"""
    start_time = time.time()
    try:
        result = database.session.execute(text(query))
        execution_time = time.time() - start_time
        
        # 记录指标
        if hasattr(current_app, 'superset_metrics'):
            current_app.superset_metrics.query_execution_time.labels(
                database=database.name,
                query_type=query_type
            ).set(execution_time)
            
        # 记录慢查询
        if execution_time > current_app.config.get('SLOW_QUERY_THRESHOLD', 5.0):
            current_app.logger.warning(
                f"慢查询检测 - 数据库: {database.name}, "
                f"类型: {query_type}, "
                f"执行时间: {execution_time:.2f}秒"
            )
        
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        current_app.logger.error(
            f"查询执行失败 - 数据库: {database.name}, "
            f"类型: {query_type}, "
            f"错误: {str(e)}"
        )
        raise

# 系统资源监控
def collect_system_metrics():
    """收集系统资源使用指标"""
    metrics = {
        'cpu_percent': psutil.cpu_percent(interval=1, percpu=True),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024),
        'disk_percent': psutil.disk_usage('/').percent,
        'disk_used_gb': psutil.disk_usage('/').used / (1024 * 1024 * 1024),
        'network_stats': psutil.net_io_counters()._asdict(),
        'process_count': len(psutil.pids())
    }
    
    return metrics

# 数据库连接池监控
def monitor_db_connections():
    """监控数据库连接池状态"""
    from superset.models.core import Database
    from sqlalchemy.orm import sessionmaker
    
    engine = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 获取所有数据库连接
        databases = db.query(Database).all()
        
        for database in databases:
            try:
                # 测试连接
                conn = database.get_sqla_engine().connect()
                conn.close()
                status = "healthy"
            except Exception:
                status = "unhealthy"
                
            # 更新指标
            if hasattr(current_app, 'superset_metrics'):
                current_app.superset_metrics.db_connections.labels(
                    database=database.name,
                    status=status
                ).set(1 if status == "healthy" else 0)
    finally:
        db.close()

# 活动用户监控
def update_active_users_count():
    """更新活动用户数量指标"""
    from flask_login import current_user
    from superset.models.core import Log
    from datetime import datetime, timedelta
    
    # 获取最近10分钟内活动的用户数量
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    active_user_count = Log.query.filter(
        Log.action == 'login',
        Log.dttm >= ten_minutes_ago
    ).distinct(Log.user_id).count()
    
    # 更新指标
    if hasattr(current_app, 'superset_metrics'):
        current_app.superset_metrics.active_users.set(active_user_count)
    
    return active_user_count

# 定时任务 - 收集指标
def scheduled_metrics_collection():
    """定时收集指标的任务"""
    with current_app.app_context():
        # 收集系统指标
        system_metrics = collect_system_metrics()
        current_app.logger.info(f"系统指标: {system_metrics}")
        
        # 监控数据库连接
        monitor_db_connections()
        
        # 更新活动用户计数
        active_users = update_active_users_count()
        current_app.logger.info(f"活动用户数量: {active_users}")
```

## 用户故事 2: 日志收集与分析

### 描述
作为系统管理员/DevOps工程师，我希望配置Superset的日志收集与分析，以便跟踪系统行为、排查问题和审计用户活动。

### 验收标准
- 配置结构化日志格式
- 支持日志级别控制
- 集成外部日志收集系统（如ELK Stack、Graylog等）
- 设置日志轮转和保留策略
- 实现关键事件的日志告警

### 分步指南

#### 高级日志配置

```python
# superset_config.py - 日志配置

import os
import logging
import logging.config
import datetime
import json
from pythonjsonlogger import jsonlogger

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件名
LOG_FILE = os.path.join(LOG_DIR, 'superset.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'superset_error.log')

# 自定义JSON日志格式化器
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.datetime.utcnow().isoformat()
        if not log_record.get('level'):
            log_record['level'] = record.levelname
        if not log_record.get('logger'):
            log_record['logger'] = record.name
        if not log_record.get('service'):
            log_record['service'] = 'superset'
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)

# 日志配置字典
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            '()': CustomJsonFormatter,
            'fmt': '%(timestamp)s %(level)s %(name)s %(message)s %(service)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'formatter': 'json',
            'level': 'INFO',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'encoding': 'utf8',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ERROR_LOG_FILE,
            'formatter': 'json',
            'level': 'ERROR',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'encoding': 'utf8',
        },
        # 可选: 添加SocketHandler发送到中央日志服务器
        # 'socket': {
        #     'class': 'logging.handlers.SocketHandler',
        #     'host': 'logstash-server',
        #     'port': 5000,
        #     'level': 'INFO',
        # },
        # 可选: 添加HTTPHandler发送到ELK或Graylog
        # 'http': {
        #     'class': 'logging.handlers.HTTPHandler',
        #     'host': 'graylog-server:12201',
        #     'url': '/gelf',
        #     'method': 'POST',
        #     'level': 'INFO',
        # },
    },
    'loggers': {
        'superset': {
            'handlers': ['console', 'file', 'error_file'],  # 可以添加'socket'或'http'
            'level': 'INFO',
            'propagate': True,
        },
        'flask_appbuilder': {
            'handlers': ['console', 'file'],
            'level': 'WARN',
            'propagate': True,
        },
        'sqlalchemy': {
            'handlers': ['console', 'file'],
            'level': 'WARN',
            'propagate': True,
        },
        'werkzeug': {
            'handlers': ['console', 'file'],
            'level': 'WARN',
            'propagate': True,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'ldap3': {
            'handlers': ['console', 'file'],
            'level': 'WARN',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'WARN',
    },
}

# 应用日志配置
logging.config.dictConfig(LOGGING_CONFIG)

# 自定义日志记录器
logger = logging.getLogger('superset')

# 日志记录增强 - 自定义用户活动日志
def log_user_activity(user_id, username, action, details=None):
    """记录用户活动的辅助函数"""
    log_data = {
        'user_id': user_id,
        'username': username,
        'action': action,
        'timestamp': datetime.datetime.utcnow().isoformat(),
    }
    if details:
        log_data['details'] = details
    
    logger.info(json.dumps(log_data))

# 自定义请求日志中间件
class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # 记录请求信息
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        remote_addr = environ.get('REMOTE_ADDR', '')
        
        # 跳过静态文件请求
        if path.startswith('/static/') or path.startswith('/health'):
            return self.app(environ, start_response)
        
        # 记录请求开始
        logger.info(f"请求开始: {method} {path} 来自 {remote_addr}")
        
        # 调用原始应用
        response = self.app(environ, start_response)
        
        # 记录请求结束
        logger.info(f"请求结束: {method} {path}")
        
        return response

# 注册中间件
ADDITIONAL_MIDDLEWARE = [RequestLoggingMiddleware]
```

#### ELK Stack集成配置

```yaml
# filebeat.yml - Filebeat配置

filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /path/to/superset/logs/superset.log
    - /path/to/superset/logs/superset_error.log
  json.keys_under_root: true
  json.overwrite_keys: true
  tags: ["superset"]

output.logstash:
  hosts: ["logstash:5044"]
  ssl.certificate_authorities: ["/etc/ssl/certs/logstash.crt"]

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
```

```ruby
# logstash.conf - Logstash配置

input {
  beats {
    port => 5044
    ssl => true
    ssl_certificate => "/etc/logstash/ssl/logstash.crt"
    ssl_key => "/etc/logstash/ssl/logstash.key"
  }
}

filter {
  if "superset" in [tags] {
    date {
      match => ["timestamp", "ISO8601"]
      target => "@timestamp"
    }
    
    # 解析Superset特定字段
    if [action] {
      mutate {
        add_field => { "event_type" => "user_activity" }
      }
    }
    
    # 处理错误日志
    if [level] == "ERROR" {
      grok {
        match => { "message" => "%{GREEDYDATA}" }
        add_field => { "error_type" => "superset_error" }
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "superset-%{+YYYY.MM.dd}"
    user => "elastic"
    password => "changeme"
  }
}
```

```json
// kibana-dashboard.json - Kibana仪表板配置示例
{
  "title": "Superset监控仪表板",
  "panels": [
    {
      "title": "日志级别分布",
      "type": "pie",
      "query": "tags:superset",
      "group_by": "level"
    },
    {
      "title": "错误日志时间线",
      "type": "line",
      "query": "tags:superset AND level:ERROR",
      "time_field": "@timestamp",
      "interval": "1h"
    },
    {
      "title": "用户活动",
      "type": "table",
      "query": "tags:superset AND action:*",
      "fields": ["timestamp", "username", "action", "details"]
    },
    {
      "title": "慢查询",
      "type": "table",
      "query": "tags:superset AND message:*slow*",
      "fields": ["timestamp", "database", "query_type", "execution_time"]
    }
  ]
}
```

#### 日志分析与告警配置

```python
# log_analyzer.py - 日志分析与告警工具

import os
import re
import json
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class LogAnalyzer:
    def __init__(self, log_file_path, config=None):
        self.log_file_path = log_file_path
        self.config = config or {
            'error_threshold': 5,  # 每小时错误阈值
            'slow_query_threshold': 10.0,  # 慢查询阈值（秒）
            'notification_email': 'admin@example.com',
            'slack_webhook_url': None,
            'alert_cooldown': 30,  # 告警冷却时间（分钟）
        }
        self.last_alert_time = {}
    
    def parse_json_logs(self, hours_back=1):
        """解析最近几小时的JSON格式日志"""
        logs = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        try:
            with open(self.log_file_path, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        # 检查日志时间戳
                        log_time = datetime.fromisoformat(log_entry.get('timestamp', datetime.utcnow().isoformat()))
                        if log_time >= cutoff_time:
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        # 忽略非JSON格式的日志行
                        continue
        except FileNotFoundError:
            print(f"日志文件不存在: {self.log_file_path}")
        
        return logs
    
    def analyze_errors(self, logs):
        """分析错误日志"""
        error_logs = [log for log in logs if log.get('level') == 'ERROR']
        
        # 按错误类型分组
        error_groups = {}
        for log in error_logs:
            error_msg = log.get('message', '')
            # 简单的错误模式提取
            error_pattern = re.search(r'([A-Za-z]+Error):', error_msg)
            error_type = error_pattern.group(1) if error_pattern else 'GeneralError'
            
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(log)
        
        return error_logs, error_groups
    
    def analyze_slow_queries(self, logs):
        """分析慢查询日志"""
        slow_queries = []
        
        for log in logs:
            # 查找包含执行时间的日志
            message = log.get('message', '')
            if isinstance(message, dict):
                execution_time = message.get('execution_time', 0)
                if execution_time > self.config['slow_query_threshold']:
                    slow_queries.append(log)
            elif isinstance(message, str):
                # 尝试从文本消息中提取执行时间
                time_match = re.search(r'execution_time: ([0-9.]+)', message)
                if time_match:
                    execution_time = float(time_match.group(1))
                    if execution_time > self.config['slow_query_threshold']:
                        slow_queries.append(log)
        
        return slow_queries
    
    def analyze_user_activity(self, logs):
        """分析用户活动日志"""
        activities = [log for log in logs if 'action' in log]
        
        # 统计用户活动
        user_actions = {}
        for log in activities:
            username = log.get('username', 'unknown')
            action = log.get('action', 'unknown')
            
            key = f"{username}:{action}"
            if key not in user_actions:
                user_actions[key] = 0
            user_actions[key] += 1
        
        return activities, user_actions
    
    def should_send_alert(self, alert_type):
        """检查是否应该发送告警（基于冷却时间）"""
        current_time = datetime.now()
        last_time = self.last_alert_time.get(alert_type, datetime.min)
        
        if (current_time - last_time).total_seconds() / 60 > self.config['alert_cooldown']:
            self.last_alert_time[alert_type] = current_time
            return True
        
        return False
    
    def send_email_alert(self, subject, message):
        """发送邮件告警"""
        sender = 'superset-monitor@example.com'
        recipients = [self.config['notification_email']]
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'html'))
        
        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('smtp_user', 'smtp_password')
                server.send_message(msg)
            print(f"邮件告警已发送: {subject}")
        except Exception as e:
            print(f"发送邮件告警失败: {str(e)}")
    
    def send_slack_alert(self, message):
        """发送Slack告警"""
        if not self.config['slack_webhook_url']:
            return
        
        payload = {
            "text": message,
            "username": "Superset监控",
            "icon_emoji": ":warning:"
        }
        
        try:
            response = requests.post(
                self.config['slack_webhook_url'],
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print("Slack告警已发送")
            else:
                print(f"发送Slack告警失败: {response.text}")
        except Exception as e:
            print(f"发送Slack告警异常: {str(e)}")
    
    def run_analysis(self):
        """运行完整的日志分析并发送告警"""
        # 解析最近1小时的日志
        logs = self.parse_json_logs(hours_back=1)
        print(f"分析了 {len(logs)} 条日志记录")
        
        # 分析错误
        error_logs, error_groups = self.analyze_errors(logs)
        print(f"发现 {len(error_logs)} 条错误日志")
        
        # 错误阈值检查
        if len(error_logs) >= self.config['error_threshold']:
            if self.should_send_alert('high_error_rate'):
                subject = f"Superset告警: 检测到高错误率 ({len(error_logs)} 个错误)"
                message = f"""
                <html>
                <body>
                    <h2>Superset高错误率告警</h2>
                    <p>在过去1小时内检测到 <strong>{len(error_logs)}</strong> 个错误。</p>
                    <h3>错误类型统计:</h3>
                    <ul>
                        {''.join([f'<li>{error_type}: {len(logs)} 次</li>' for error_type, logs in error_groups.items()])}
                    </ul>
                    <p>请检查Superset日志以获取更多详情。</p>
                </body>
                </html>
                """
                self.send_email_alert(subject, message)
                self.send_slack_alert(f"⚠️ Superset告警: 过去1小时内检测到 {len(error_logs)} 个错误")
        
        # 分析慢查询
        slow_queries = self.analyze_slow_queries(logs)
        if slow_queries:
            print(f"发现 {len(slow_queries)} 个慢查询")
            if self.should_send_alert('slow_queries'):
                subject = f"Superset告警: 检测到慢查询 ({len(slow_queries)} 个)"
                message = f"""
                <html>
                <body>
                    <h2>Superset慢查询告警</h2>
                    <p>在过去1小时内检测到 <strong>{len(slow_queries)}</strong> 个慢查询。</p>
                    <p>阈值: {self.config['slow_query_threshold']} 秒</p>
                </body>
                </html>
                """
                self.send_email_alert(subject, message)
                self.send_slack_alert(f"⚠️ Superset告警: 过去1小时内检测到 {len(slow_queries)} 个慢查询")
        
        # 分析用户活动
        activities, user_actions = self.analyze_user_activity(logs)
        print(f"分析了 {len(activities)} 条用户活动记录")
        
        return {
            'total_logs': len(logs),
            'error_logs': len(error_logs),
            'error_groups': error_groups,
            'slow_queries': len(slow_queries),
            'user_activities': len(activities),
            'user_actions': user_actions
        }

# 使用示例
if __name__ == "__main__":
    analyzer = LogAnalyzer(
        log_file_path="/path/to/superset/logs/superset.log",
        config={
            'error_threshold': 5,
            'slow_query_threshold': 10.0,
            'notification_email': 'admin@example.com',
            'slack_webhook_url': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
            'alert_cooldown': 30
        }
    )
    results = analyzer.run_analysis()
    print(json.dumps(results, indent=2, ensure_ascii=False))
```

## 用户故事 3: 健康检查策略

### 描述
作为DevOps工程师/系统管理员，我希望配置Superset的健康检查策略，以便监控系统可用性并实现自动恢复机制。

### 验收标准
- 提供端点级健康检查
- 实现组件级健康检查（数据库、缓存等）
- 配置健康检查阈值和超时设置
- 支持集成到负载均衡器和容器编排平台

### 分步指南

#### 健康检查端点配置

```python
# superset_config.py - 健康检查配置

from flask import Flask, jsonify, request
from superset.app import create_app
import time
import socket
import psutil

# 创建Flask应用实例
app = create_app()

# 健康检查端点
@app.route('/health')
def health_check():
    """基础健康检查端点"""
    # 检查服务是否正常运行
    status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'superset',
        'version': '1.5.0',
        'hostname': socket.gethostname()
    }
    
    return jsonify(status), 200

# 详细健康检查端点
@app.route('/health/detailed')
def detailed_health_check():
    """详细健康检查端点，包括各组件状态"""
    start_time = time.time()
    
    # 初始化状态
    status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'superset',
        'version': '1.5.0',
        'hostname': socket.gethostname(),
        'uptime': time.time() - app.config.get('START_TIME', start_time),
        'components': {}
    }
    
    # 检查数据库连接
    try:
        db_start = time.time()
        # 执行简单的数据库查询
        from superset import db
        db.session.execute('SELECT 1')
        db.session.close()
        db_time = time.time() - db_start
        
        status['components']['database'] = {
            'status': 'healthy',
            'response_time': db_time,
            'timestamp': time.time()
        }
        
        # 数据库响应时间检查
        if db_time > app.config.get('DB_RESPONSE_TIME_THRESHOLD', 1.0):
            status['components']['database']['status'] = 'degraded'
            status['components']['database']['warning'] = f"数据库响应时间过长: {db_time:.2f}秒"
    except Exception as e:
        status['status'] = 'unhealthy'
        status['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }
    
    # 检查缓存连接
    try:
        cache_start = time.time()
        # 测试缓存连接
        from superset import cache
        cache_key = 'health_check_test'
        cache.set(cache_key, 'test_value', timeout=5)
        value = cache.get(cache_key)
        cache.delete(cache_key)
        cache_time = time.time() - cache_start
        
        if value == 'test_value':
            status['components']['cache'] = {
                'status': 'healthy',
                'response_time': cache_time,
                'timestamp': time.time()
            }
        else:
            raise Exception("缓存读写测试失败")
    except Exception as e:
        status['status'] = 'degraded'  # 缓存问题不一定导致服务完全不可用
        status['components']['cache'] = {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }
    
    # 检查Celery连接（如果启用）
    if app.config.get('ENABLE_CELERY', False):
        try:
            celery_start = time.time()
            from superset.tasks.celery_app import app as celery_app
            # 检查Celery连接
            if celery_app.control.ping(timeout=2):
                celery_time = time.time() - celery_start
                status['components']['celery'] = {
                    'status': 'healthy',
                    'response_time': celery_time,
                    'timestamp': time.time()
                }
            else:
                raise Exception("Celery工作器无响应")
        except Exception as e:
            status['status'] = 'degraded'  # Celery问题不一定导致服务完全不可用
            status['components']['celery'] = {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }
    
    # 检查系统资源
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        status['components']['system'] = {
            'status': 'healthy',
            'memory_percent': memory.percent,
            'cpu_percent': cpu_percent,
            'timestamp': time.time()
        }
        
        # 系统资源阈值检查
        memory_threshold = app.config.get('MEMORY_THRESHOLD_PERCENT', 85)
        cpu_threshold = app.config.get('CPU_THRESHOLD_PERCENT', 90)
        
        if memory.percent > memory_threshold or cpu_percent > cpu_threshold:
            status['components']['system']['status'] = 'warning'
            warnings = []
            if memory.percent > memory_threshold:
                warnings.append(f"内存使用率过高: {memory.percent}%")
            if cpu_percent > cpu_threshold:
                warnings.append(f"CPU使用率过高: {cpu_percent}%")
            status['components']['system']['warnings'] = warnings
    except Exception as e:
        # 系统资源检查失败不应影响整体状态
        status['components']['system'] = {
            'status': 'unknown',
            'error': str(e),
            'timestamp': time.time()
        }
    
    # 根据组件状态确定整体状态
    component_statuses = [comp['status'] for comp in status['components'].values()]
    if 'unhealthy' in component_statuses and 'database' in [k for k, v in status['components'].items() if v['status'] == 'unhealthy']:
        status['status'] = 'unhealthy'
    elif 'unhealthy' in component_statuses:
        status['status'] = 'degraded'
    elif 'warning' in component_statuses or 'degraded' in component_statuses:
        status['status'] = 'degraded'
    
    # 根据状态设置HTTP响应码
    if status['status'] == 'unhealthy':
        return jsonify(status), 503
    elif status['status'] == 'degraded':
        return jsonify(status), 207
    else:  # healthy
        return jsonify(status), 200

# 组件特定健康检查
@app.route('/health/<component>')
def component_health_check(component):
    """特定组件的健康检查"""
    component_checks = {
        'database': check_database_health,
        'cache': check_cache_health,
        'celery': check_celery_health,
        'system': check_system_health
    }
    
    if component in component_checks:
        try:
            result = component_checks[component]()
            status_code = 200 if result.get('status') == 'healthy' else 503
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'component': component,
                'error': str(e),
                'timestamp': time.time()
            }), 503
    else:
        return jsonify({
            'status': 'error',
            'message': f'未知组件: {component}',
            'available_components': list(component_checks.keys())
        }), 404

# 组件健康检查函数
def check_database_health():
    """检查数据库健康状态"""
    start_time = time.time()
    try:
        from superset import db
        # 执行更详细的数据库检查
        results = db.session.execute('SELECT NOW() as current_time, version() as version').fetchone()
        response_time = time.time() - start_time
        
        # 检查数据库连接池状态
        engine = db.session.get_bind()
        pool_status = {
            'pool_size': engine.pool.size(),
            'checkedin_connections': engine.pool.checkedin(),
            'checkedout_connections': engine.pool.checkedout(),
            'overflow_connections': engine.pool.overflow(),
            'connection_timeout': engine.pool.timeout()
        }
        
        return {
            'status': 'healthy',
            'component': 'database',
            'response_time': response_time,
            'database_time': str(results.current_time),
            'database_version': results.version,
            'pool_status': pool_status,
            'timestamp': time.time()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'component': 'database',
            'error': str(e),
            'timestamp': time.time()
        }

def check_cache_health():
    """检查缓存健康状态"""
    start_time = time.time()
    try:
        from superset import cache
        # 执行缓存性能测试
        cache_key = f'health_check_{time.time()}'
        cache.set(cache_key, 'test_value', timeout=5)
        
        # 测试多次读写性能
        read_times = []
        for _ in range(5):
            read_start = time.time()
            value = cache.get(cache_key)
            read_times.append(time.time() - read_start)
        
        cache.delete(cache_key)
        
        avg_read_time = sum(read_times) / len(read_times)
        response_time = time.time() - start_time
        
        return {
            'status': 'healthy' if value == 'test_value' else 'unhealthy',
            'component': 'cache',
            'response_time': response_time,
            'avg_read_time': avg_read_time,
            'cache_type': cache.__class__.__name__,
            'timestamp': time.time()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'component': 'cache',
            'error': str(e),
            'timestamp': time.time()
        }

def check_celery_health():
    """检查Celery健康状态"""
    start_time = time.time()
    try:
        if not app.config.get('ENABLE_CELERY', False):
            return {
                'status': 'disabled',
                'component': 'celery',
                'message': 'Celery未启用',
                'timestamp': time.time()
            }
        
        from superset.tasks.celery_app import app as celery_app
        
        # 检查Celery工作器
        workers = celery_app.control.ping(timeout=2)
        
        # 获取任务队列长度
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active() or {}
        reserved_tasks = inspect.reserved() or {}
        scheduled_tasks = inspect.scheduled() or {}
        
        # 任务统计
        task_stats = {
            'total_workers': len(workers) if workers else 0,
            'active_tasks': sum(len(tasks) for tasks in active_tasks.values()),
            'reserved_tasks': sum(len(tasks) for tasks in reserved_tasks.values()),
            'scheduled_tasks': sum(len(tasks) for tasks in scheduled_tasks.values())
        }
        
        response_time = time.time() - start_time
        
        return {
            'status': 'healthy' if workers else 'unhealthy',
            'component': 'celery',
            'response_time': response_time,
            'task_stats': task_stats,
            'workers': workers,
            'timestamp': time.time()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'component': 'celery',
            'error': str(e),
            'timestamp': time.time()
        }

def check_system_health():
    """检查系统资源健康状态"""
    try:
        # 系统内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_percent': memory.percent,
            'used_gb': round(memory.used / (1024**3), 2)
        }
        
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_info = {
            'avg_percent': sum(cpu_percent) / len(cpu_percent),
            'per_cpu_percent': cpu_percent,
            'count': len(cpu_percent)
        }
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_info = {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'used_percent': disk.percent
        }
        
        # 进程信息
        process = psutil.Process()
        process_info = {
            'cpu_percent': process.cpu_percent(interval=0.1),
            'memory_percent': process.memory_percent(),
            'threads': process.num_threads(),
            'open_files': len(process.open_files()),
            'connections': len(process.connections())
        }
        
        # 网络信息
        net_io = psutil.net_io_counters()
        net_info = {
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        # 确定系统状态
        status = 'healthy'
        warnings = []
        
        memory_threshold = app.config.get('MEMORY_THRESHOLD_PERCENT', 85)
        cpu_threshold = app.config.get('CPU_THRESHOLD_PERCENT', 90)
        disk_threshold = app.config.get('DISK_THRESHOLD_PERCENT', 90)
        
        if memory_info['used_percent'] > memory_threshold:
            status = 'warning'
            warnings.append(f"内存使用率过高: {memory_info['used_percent']}%")
        
        if cpu_info['avg_percent'] > cpu_threshold:
            status = 'warning'
            warnings.append(f"CPU使用率过高: {cpu_info['avg_percent']}%")
        
        if disk_info['used_percent'] > disk_threshold:
            status = 'warning'
            warnings.append(f"磁盘使用率过高: {disk_info['used_percent']}%")
        
        return {
            'status': status,
            'component': 'system',
            'memory': memory_info,
            'cpu': cpu_info,
            'disk': disk_info,
            'process': process_info,
            'network': net_info,
            'warnings': warnings if warnings else None,
            'timestamp': time.time()
        }
    except Exception as e:
        return {
            'status': 'unknown',
            'component': 'system',
            'error': str(e),
            'timestamp': time.time()
        }

# 负载均衡器健康检查配置
def setup_load_balancer_health_check(app):
    """配置用于负载均衡器的健康检查"""
    # 设置启动时间用于计算正常运行时间
    app.config['START_TIME'] = time.time()
    
    # 注册健康检查端点
    # 注意：这些端点已经在上面定义，但如果需要可以在这里添加更多配置
    pass

# 注册健康检查
setup_load_balancer_health_check(app)
```

#### Kubernetes健康检查配置

```yaml
# kubernetes/deployment-health-checks.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: superset-web
  namespace: superset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: superset
      component: web
  template:
    metadata:
      labels:
        app: superset
        component: web
    spec:
      containers:
      - name: superset-web
        image: apache/superset:latest
        ports:
        - containerPort: 8088
        # 存活探针
        livenessProbe:
          httpGet:
            path: /health
            port: 8088
          initialDelaySeconds: 60  # 容器启动后60秒开始检查
          periodSeconds: 30        # 每30秒检查一次
          timeoutSeconds: 10       # 检查超时时间
          failureThreshold: 3      # 连续3次失败判定为不健康
          successThreshold: 1      # 1次成功判定为健康
        
        # 就绪探针
        readinessProbe:
          httpGet:
            path: /health/detailed
            port: 8088
          initialDelaySeconds: 30  # 容器启动后30秒开始检查
          periodSeconds: 15        # 每15秒检查一次
          timeoutSeconds: 5        # 检查超时时间
          failureThreshold: 2      # 连续2次失败判定为未就绪
          successThreshold: 1      # 1次成功判定为就绪
        
        # 启动探针
        startupProbe:
          httpGet:
            path: /health
            port: 8088
          initialDelaySeconds: 10  # 容器启动后10秒开始检查
          periodSeconds: 10        # 每10秒检查一次
          timeoutSeconds: 5        # 检查超时时间
          failureThreshold: 30     # 允许30次失败（给应用足够的启动时间）
          successThreshold: 1      # 1次成功判定为已启动
        
        # 资源限制
        resources:
          requests:
            cpu: 1
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
        
        # 环境变量
        env:
        - name: MEMORY_THRESHOLD_PERCENT
          value: "85"
        - name: CPU_THRESHOLD_PERCENT
          value: "90"
        - name: DISK_THRESHOLD_PERCENT
          value: "90"
        - name: DB_RESPONSE_TIME_THRESHOLD
          value: "1.0"
```

## 用户故事 4: 性能监控指标

### 描述
作为性能工程师/系统管理员，我希望配置Superset的性能监控指标，以便分析系统性能趋势、识别瓶颈并进行优化。

### 验收标准
- 监控关键性能指标（响应时间、查询执行时间等）
- 跟踪用户行为和交互性能
- 分析系统资源使用趋势
- 生成性能报告和可视化仪表板

### 分步指南

#### 性能指标收集配置

```python
# superset_config.py - 性能指标配置扩展

import time
import functools
from flask import request, g
from prometheus_client import Counter, Histogram, Gauge, Summary

# 初始化Prometheus指标
REQUEST_COUNT = Counter(
    'superset_requests_total',
    '请求总数',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'superset_request_duration_seconds',
    '请求延迟时间（秒）',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2.5, 5, 10, 30, 60)
)

ACTIVE_USERS = Gauge(
    'superset_active_users',
    '当前活动用户数'
)

QUERY_EXECUTION_TIME = Histogram(
    'superset_query_execution_seconds',
    'SQL查询执行时间',
    ['database', 'query_type'],
    buckets=(0.1, 0.5, 1, 2.5, 5, 10, 30, 60, 120)
)

CACHE_HIT_RATE = Summary(
    'superset_cache_hit_rate',
    '缓存命中率',
    ['cache_type']
)

# 中间件 - 请求性能监控
class PerformanceMonitoringMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        
        # 包装start_response以获取状态码
        def wrapped_start_response(status, response_headers, exc_info=None):
            # 提取状态码（如 '200 OK' -> '200'）
            status_code = status.split()[0]
            
            # 计算请求延迟
            latency = time.time() - start_time
            
            # 记录指标
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path
            ).observe(latency)
            
            # 记录慢请求
            if latency > 5.0:  # 5秒以上视为慢请求
                self.app.logger.warning(
                    f"慢请求检测: {method} {path} - "
                    f"状态码: {status_code}, "
                    f"延迟: {latency:.2f}秒"
                )
            
            # 调用原始的start_response
            return start_response(status, response_headers, exc_info)
        
        # 调用应用
        return self.app(environ, wrapped_start_response)

# 查询性能监控装饰器
def monitor_query_performance(database_name, query_type="general"):
    """装饰器：监控SQL查询性能"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 记录查询执行时间
                QUERY_EXECUTION_TIME.labels(
                    database=database_name,
                    query_type=query_type
                ).observe(execution_time)
                
                # 记录慢查询
                if execution_time > 10.0:  # 10秒以上视为慢查询
                    current_app.logger.warning(
                        f"慢查询检测 - 数据库: {database_name}, "
                        f"类型: {query_type}, "
                        f"执行时间: {execution_time:.2f}秒"
                    )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                current_app.logger.error(
                    f"查询执行失败 - 数据库: {database_name}, "
                    f"类型: {query_type}, "
                    f"执行时间: {execution_time:.2f}秒, "
                    f"错误: {str(e)}"
                )
                raise
        return wrapper
    return decorator

# 缓存性能监控装饰器
def monitor_cache_performance(cache_type="general"):
    """装饰器：监控缓存性能"""
    cache_hits = Counter(
        f'superset_cache_{cache_type}_hits',
        f'{cache_type}缓存命中次数'
    )
    cache_misses = Counter(
        f'superset_cache_{cache_type}_misses',
        f'{cache_type}缓存未命中次数'
    )
    
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            cache_key = kwargs.get('key', args[0] if args else None)
            start_time = time.time()
            
            # 执行原始函数
            result = f(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # 记录缓存操作
            if 'get' in f.__name__:
                if result is not None:
                    cache_hits.inc()
                else:
                    cache_misses.inc()
            
            # 计算并更新命中率
            total = cache_hits._value.get() + cache_misses._value.get()
            if total > 0:
                hit_rate = cache_hits._value.get() / total
                CACHE_HIT_RATE.labels(cache_type=cache_type).observe(hit_rate)
            
            return result
        return wrapper
    return decorator

# 用户会话监控
def track_user_session():
    """跟踪用户会话活动"""
    @app.before_request
    def before_request():
        # 记录请求开始时间
        g.start_time = time.time()
        
        # 更新活动用户数
        if hasattr(request, 'user') and request.user.is_authenticated:
            # 这里可以实现更复杂的活动用户跟踪逻辑
            # 例如使用Redis存储活跃会话信息
            ACTIVE_USERS.inc()
    
    @app.after_request
    def after_request(response):
        # 计算请求延迟
        if hasattr(g, 'start_time'):
            latency = time.time() - g.start_time
            
            # 可以在这里添加更多性能指标收集
            
        return response

# 配置监控中间件
ADDITIONAL_MIDDLEWARE = [PerformanceMonitoringMiddleware]

# 启用用户会话跟踪
track_user_session()
```

#### Grafana仪表板配置

```json
// grafana-dashboard.json - Superset性能监控仪表板
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "注释 & 警报",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 1,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.3.7",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "sum(rate(superset_requests_total[5m])) by (status)",
          "interval": "",
          "legendFormat": "{{status}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "请求率（按状态码）",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": true,
        "current": false,
        "max": true,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.3.7",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(superset_query_execution_seconds_bucket[5m])) by (le, database, query_type))",
          "interval": "",
          "legendFormat": "{{database}} - {{query_type}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "95%查询执行时间（按数据库和查询类型）",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "s",
          "label": "秒",
          "logBase": 1,
          "max": null,
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "cacheTimeout": null,
      "colorBackground": false,
      "colorValue": false,
      "colors": [
        "#299c46",
        "rgba(237, 129, 40, 0.89)",
        "#d44a3a"
      ],
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "format": "percentunit",
      "gauge": {
        "maxValue": 100,
        "minValue": 0,
        "show": true,
        "thresholdLabels": true,
        "thresholdMarkers": true
      },
      "gridPos": {
        "h": 8,
        "w": 6,
        "x": 0,
        "y": 16
      },
      "id": 5,
      "interval": null,
      "links": [],
      "mappingType": 1,
      "mappingTypes": [
        {
          "name": "value to text",
          "value": 1
        },
        {
          "name": "range to text",
          "value": 2
        }
      ],
      "maxDataPoints": 100,
      "nullPointMode": "connected",
      "nullText": null,
      "options": {
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        }
      },
      "pluginVersion": "7.3.7",
      "postfix": "",
      "postfixFontSize": "50%",
      "prefix": "",
      "prefixFontSize": "50%",
      "rangeMaps": [
        {
          "from": "null",
          "text": "N/A",
          "to": "null"
        }
      ],
      "sparkline": {
        "fillColor": "rgba(31, 118, 189, 0.18)",
        "full": false,
        "lineColor": "rgb(31, 120, 193)",
        "show": false
      },
      "tableColumn": "",
      "targets": [
        {
          "expr": "superset_cache_hit_rate{cache_type=\"general\"}",
          "interval": "",
          "legendFormat": "",
          "refId": "A"
        }
      ],
      "thresholds": "70, 90",
      "title": "缓存命中率",
      "type": "singlestat",
      "valueFontSize": "80%",
      "valueMaps": [
        {
          "op": "=",
          "text": "N/A",
          "value": "null"
        }
      ],
      "valueName": "current"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 26,
  "style": "dark",
  "tags": [
    "superset",
    "performance",
    "monitoring"
  ],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Superset性能监控",
  "uid": "superset-performance",
  "version": 1
}
```

#### 性能分析和报告工具

```python
# performance_analyzer.py - 性能分析和报告生成工具

import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import requests
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib

class SupersetPerformanceAnalyzer:
    def __init__(self, prometheus_url="http://prometheus:9090", config=None):
        self.prometheus_url = prometheus_url
        self.config = config or {
            'report_email': 'admin@example.com',
            'slow_query_threshold': 10.0,
            'slow_request_threshold': 5.0,
            'min_data_points': 100
        }
    
    def query_prometheus(self, query, start_time, end_time, step=60):
        """查询Prometheus获取指标数据"""
        params = {
            'query': query,
            'start': start_time,
            'end': end_time,
            'step': step
        }
        
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/query_range", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'success':
                raise Exception(f"Prometheus查询失败: {data.get('error', 'Unknown error')}")
            
            return data['data']['result']
        except Exception as e:
            print(f"查询Prometheus失败: {str(e)}")
            return []
    
    def get_request_metrics(self, hours=24):
        """获取请求性能指标"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # 查询请求延迟数据
        latency_query = 'histogram_quantile(0.95, sum(rate(superset_request_duration_seconds_bucket[5m])) by (le, endpoint))'
        latency_data = self.query_prometheus(latency_query, start_time, end_time)
        
        # 查询请求计数数据
        count_query = 'sum(rate(superset_requests_total[5m])) by (method, endpoint, status)'
        count_data = self.query_prometheus(count_query, start_time, end_time)
        
        return {
            'latency': latency_data,
            'count': count_data
        }
    
    def get_query_metrics(self, hours=24):
        """获取查询性能指标"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # 查询查询执行时间
        query_time_query = 'histogram_quantile(0.95, sum(rate(superset_query_execution_seconds_bucket[5m])) by (le, database, query_type))'
        query_time_data = self.query_prometheus(query_time_query, start_time, end_time)
        
        # 查询慢查询计数
        slow_query_query = 'sum(increase(superset_query_execution_seconds_count{superset_query_execution_seconds="10.0"}[5m])) by (database, query_type)'
        slow_query_data = self.query_prometheus(slow_query_query, start_time, end_time)
        
        return {
            'execution_time': query_time_data,
            'slow_queries': slow_query_data
        }
    
    def get_user_activity_metrics(self, hours=24):
        """获取用户活动指标"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # 查询活跃用户数
        active_users_query = 'superset_active_users'
        active_users_data = self.query_prometheus(active_users_query, start_time, end_time)
        
        return {
            'active_users': active_users_data
        }
    
    def analyze_request_performance(self, metrics):
        """分析请求性能"""
        # 处理延迟数据
        latency_df = pd.DataFrame()
        for result in metrics['latency']:
            endpoint = result['metric'].get('endpoint', 'unknown')
            values = result['values']
            
            timestamps = [datetime.fromtimestamp(float(v[0])) for v in values]
            latencies = [float(v[1]) for v in values]
            
            temp_df = pd.DataFrame({
                'timestamp': timestamps,
                'endpoint': endpoint,
                'latency_95p': latencies
            })
            
            latency_df = latency_df.append(temp_df)
        
        # 处理计数数据
        count_df = pd.DataFrame()
        for result in metrics['count']:
            method = result['metric'].get('method', 'unknown')
            endpoint = result['metric'].get('endpoint', 'unknown')
            status = result['metric'].get('status', 'unknown')
            values = result['values']
            
            timestamps = [datetime.fromtimestamp(float(v[0])) for v in values]
            rates = [float(v[1]) for v in values]
            
            temp_df = pd.DataFrame({
                'timestamp': timestamps,
                'method': method,
                'endpoint': endpoint,
                'status': status,
                'request_rate': rates
            })
            
            count_df = count_df.append(temp_df)
        
        # 分析慢请求
        if not latency_df.empty:
            slow_requests = latency_df[latency_df['latency_95p'] > self.config['slow_request_threshold']]
            problematic_endpoints = slow_requests.groupby('endpoint')['latency_95p'].mean().sort_values(ascending=False)
        else:
            problematic_endpoints = pd.Series()
        
        # 分析错误率
        if not count_df.empty:
            error_rates = count_df[count_df['status'].str.startswith('5')].groupby('endpoint')['request_rate'].sum()
            total_rates = count_df.groupby('endpoint')['request_rate'].sum()
            if not total_rates.empty:
                error_percentages = (error_rates / total_rates * 100).fillna(0).sort_values(ascending=False)
            else:
                error_percentages = pd.Series()
        else:
            error_percentages = pd.Series()
        
        return {
            'latency_dataframe': latency_df,
            'count_dataframe': count_df,
            'problematic_endpoints': problematic_endpoints,
            'error_percentages': error_percentages
        }
    
    def analyze_query_performance(self, metrics):
        """分析查询性能"""
        # 处理查询执行时间数据
        query_time_df = pd.DataFrame()
        for result in metrics['execution_time']:
            database = result['metric'].get('database', 'unknown')
            query_type = result['metric'].get('query_type', 'general')
            values = result['values']
            
            timestamps = [datetime.fromtimestamp(float(v[0])) for v in values]
            execution_times = [float(v[1]) for v in values]
            
            temp_df = pd.DataFrame({
                'timestamp': timestamps,
                'database': database,
                'query_type': query_type,
                'execution_time_95p': execution_times
            })
            
            query_time_df = query_time_df.append(temp_df)
        
        # 分析慢查询
        if not query_time_df.empty:
            slow_queries = query_time_df[query_time_df['execution_time_95p'] > self.config['slow_query_threshold']]
            problematic_queries = slow_queries.groupby(['database', 'query_type'])['execution_time_95p'].mean().sort_values(ascending=False)
        else:
            problematic_queries = pd.Series()
        
        return {
            'query_time_dataframe': query_time_df,
            'problematic_queries': problematic_queries
        }
    
    def generate_performance_report(self, days=7):
        """生成性能分析报告"""
        print(f"生成过去{days}天的性能报告...")
        
        # 获取指标数据
        request_metrics = self.get_request_metrics(hours=days*24)
        query_metrics = self.get_query_metrics(hours=days*24)
        user_metrics = self.get_user_activity_metrics(hours=days*24)
        
        # 分析数据
        request_analysis = self.analyze_request_performance(request_metrics)
        query_analysis = self.analyze_query_performance(query_metrics)
        
        # 生成可视化图表
        charts = self.generate_charts(request_analysis, query_analysis, user_metrics)
        
        # 生成报告内容
        report_content = self.format_report_content(request_analysis, query_analysis, user_metrics, days)
        
        return {
            'content': report_content,
            'charts': charts,
            'request_analysis': request_analysis,
            'query_analysis': query_analysis,
            'user_metrics': user_metrics
        }
    
    def generate_charts(self, request_analysis, query_analysis, user_metrics):
        """生成性能报告图表"""
        charts = {}
        
        # 设置图表样式
        sns.set(style="whitegrid")
        
        # 1. 请求延迟趋势图
        if not request_analysis['latency_dataframe'].empty and len(request_analysis['latency_dataframe']) >= self.config['min_data_points']:
            plt.figure(figsize=(12, 6))
            latency_df = request_analysis['latency_dataframe']
            
            # 只显示前5个端点以避免图表过于拥挤
            top_endpoints = latency_df.groupby('endpoint')['latency_95p'].mean().nlargest(5).index
            top_latency_df = latency_df[latency_df['endpoint'].isin(top_endpoints)]
            
            sns.lineplot(x='timestamp', y='latency_95p', hue='endpoint', data=top_latency_df)
            plt.title('请求延迟趋势（95分位数）')
            plt.xlabel('时间')
            plt.ylabel('延迟（秒）')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # 保存为字节流
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            charts['request_latency'] = buf
            plt.close()
        
        # 2. 慢查询分析图
        if not query_analysis['problematic_queries'].empty:
            plt.figure(figsize=(12, 6))
            problematic_queries = query_analysis['problematic_queries']
            
            # 转换索引为易读格式
            labels = [f"{db} - {qtype}" for db, qtype in problematic_queries.index]
            
            problematic_queries.plot(kind='bar')
            plt.title('问题查询（95分位数执行时间 > 阈值）')
            plt.xlabel('数据库 - 查询类型')
            plt.ylabel('执行时间（秒）')
            plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
            plt.tight_layout()
            
            # 保存为字节流
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            charts['slow_queries'] = buf
            plt.close()
        
        # 3. 错误率分析图
        if not request_analysis['error_percentages'].empty and len(request_analysis['error_percentages']) >= 1:
            plt.figure(figsize=(12, 6))
            error_percentages = request_analysis['error_percentages']
            
            # 只显示前10个端点
            error_percentages.head(10).plot(kind='bar')
            plt.title('端点错误率（%）')
            plt.xlabel('端点')
            plt.ylabel('错误率（%）')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # 保存为字节流
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            charts['error_rates'] = buf
            plt.close()
        
        return charts
    
    def format_report_content(self, request_analysis, query_analysis, user_metrics, days):
        """格式化报告内容"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        report = f"""
        <html>
        <head>
            <title>Superset性能分析报告 - {start_date} 至 {end_date}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333366; }}
                h2 {{ color: #333399; margin-top: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .warning {{ background-color: #fff3cd; }}
                .critical {{ background-color: #f8d7da; }}
                .summary-box {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; background-color: #f8f9fa; }}
                .chart {{ margin: 20px 0; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>Superset性能分析报告</h1>
            <p>报告生成时间: {now}</p>
            <p>分析期间: {start_date} 至 {end_date}</p>
        """
        
        # 添加摘要部分
        report += """
            <div class="summary-box">
                <h2>性能摘要</h2>
                <table>
                    <tr>
                        <th>指标</th>
                        <th>状态</th>
                        <th>详情</th>
                    </tr>
        """
        
        # 请求性能摘要
        problematic_endpoints_count = len(request_analysis['problematic_endpoints'])
        request_status = "警告" if problematic_endpoints_count > 0 else "正常"
        request_class = "warning" if problematic_endpoints_count > 0 else ""
        
        report += f"""
                    <tr class="{request_class}">
                        <td>请求性能</td>
                        <td>{request_status}</td>
                        <td>发现 {problematic_endpoints_count} 个性能问题端点</td>
                    </tr>
        """
        
        # 查询性能摘要
        problematic_queries_count = len(query_analysis['problematic_queries'])
        query_status = "警告" if problematic_queries_count > 0 else "正常"
        query_class = "warning" if problematic_queries_count > 0 else ""
        
        report += f"""
                    <tr class="{query_class}">
                        <td>查询性能</td>
                        <td>{query_status}</td>
                        <td>发现 {problematic_queries_count} 个慢查询类型</td>
                    </tr>
        """
        
        # 错误率摘要
        high_error_endpoints = len(request_analysis['error_percentages'][request_analysis['error_percentages'] > 5])
        error_status = "警告" if high_error_endpoints > 0 else "正常"
        error_class = "warning" if high_error_endpoints > 0 else ""
        
        report += f"""
                    <tr class="{error_class}">
                        <td>错误率</td>
                        <td>{error_status}</td>
                        <td>发现 {high_error_endpoints} 个高错误率端点</td>
                    </tr>
                </table>
            </div>
        """
        
        # 添加问题端点详情
        if problematic_endpoints_count > 0:
            report += """
            <h2>问题端点详情</h2>
            <p>延迟超过阈值 ({self.config['slow_request_threshold']} 秒) 的端点:</p>
            <table>
                <tr>
                    <th>端点</th>
                    <th>平均延迟 (秒)</th>
                    <th>状态</th>
                </tr>
            """
            
            for endpoint, latency in request_analysis['problematic_endpoints'].head(10).items():
                severity = "严重" if latency > self.config['slow_request_threshold'] * 2 else "警告"
                severity_class = "critical" if latency > self.config['slow_request_threshold'] * 2 else "warning"
                
                report += f"""
                <tr class="{severity_class}">
                    <td>{endpoint}</td>
                    <td>{latency:.2f}</td>
                    <td>{severity}</td>
                </tr>
                """
            
            report += """
            </table>
            """
        
        # 添加慢查询详情
        if problematic_queries_count > 0:
            report += """
            <h2>慢查询详情</h2>
            <p>执行时间超过阈值 ({self.config['slow_query_threshold']} 秒) 的查询:</p>
            <table>
                <tr>
                    <th>数据库 - 查询类型</th>
                    <th>平均执行时间 (秒)</th>
                    <th>状态</th>
                </tr>
            """
            
            for (database, query_type), exec_time in query_analysis['problematic_queries'].head(10).items():
                severity = "严重" if exec_time > self.config['slow_query_threshold'] * 2 else "警告"
                severity_class = "critical" if exec_time > self.config['slow_query_threshold'] * 2 else "warning"
                
                report += f"""
                <tr class="{severity_class}">
                    <td>{database} - {query_type}</td>
                    <td>{exec_time:.2f}</td>
                    <td>{severity}</td>
                </tr>
                """
            
            report += """
            </table>
            """
        
        # 添加高错误率端点详情
        if high_error_endpoints > 0:
            report += """
            <h2>高错误率端点</h2>
            <p>错误率超过5%的端点:</p>
            <table>
                <tr>
                    <th>端点</th>
                    <th>错误率 (%)</th>
                    <th>状态</th>
                </tr>
            """
            
            high_error_endpoints_data = request_analysis['error_percentages'][request_analysis['error_percentages'] > 5].head(10)
            for endpoint, error_rate in high_error_endpoints_data.items():
                severity = "严重" if error_rate > 20 else "警告"
                severity_class = "critical" if error_rate > 20 else "warning"
                
                report += f"""
                <tr class="{severity_class}">
                    <td>{endpoint}</td>
                    <td>{error_rate:.2f}</td>
                    <td>{severity}</td>
                </tr>
                """
            
            report += """
            </table>
            """
        
        # 添加建议部分
        report += """
            <h2>性能优化建议</h2>
            <ul>
        """
        
        if problematic_endpoints_count > 0:
            report += """
                <li>优化性能问题端点的代码或增加缓存策略</li>
                <li>考虑为高频访问的端点增加资源分配</li>
            """
        
        if problematic_queries_count > 0:
            report += """
                <li>审查并优化慢查询SQL语句</li>
                <li>为常用查询添加适当的索引</li>
                <li>考虑增加数据库只读副本分担查询压力</li>
            """
        
        if high_error_endpoints > 0:
            report += """
                <li>调查并修复高错误率端点的潜在问题</li>
                <li>增加错误处理和重试机制</li>
            """
        
        report += """
                <li>监控系统资源使用情况，确保有足够的CPU和内存</li>
                <li>定期清理缓存和临时文件</li>
                <li>考虑对高流量时段进行负载测试，评估系统容量</li>
            </ul>
        
            <h2>结论</h2>
            <p>本报告基于过去{days}天的性能数据生成。请根据上述分析采取相应措施优化Superset系统性能。</p>
        </body>
        </html>
        """
        
        return report
    
    def send_report_email(self, report):
        """发送性能报告邮件"""
        sender = 'superset-monitor@example.com'
        recipients = [self.config['report_email']]
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"Superset性能分析报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 添加HTML报告正文
        msg.attach(MIMEText(report['content'], 'html'))
        
        # 添加图表附件
        for chart_name, chart_buf in report['charts'].items():
            attachment = MIMEApplication(chart_buf.read(), Name=f"{chart_name}.png")
            attachment['Content-Disposition'] = f'attachment; filename="{chart_name}.png"'
            msg.attach(attachment)
        
        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('smtp_user', 'smtp_password')
                server.send_message(msg)
            print("性能报告邮件已发送")
        except Exception as e:
            print(f"发送性能报告邮件失败: {str(e)}")

# 使用示例
if __name__ == "__main__":
    analyzer = SupersetPerformanceAnalyzer(
        prometheus_url="http://localhost:9090",
        config={
            'report_email': 'admin@example.com',
            'slow_query_threshold': 10.0,
            'slow_request_threshold': 5.0
        }
    )
    
    # 生成报告
    report = analyzer.generate_performance_report(days=7)
    
    # 发送报告邮件
    analyzer.send_report_email(report)
    
    print("性能分析报告生成并发送完成")
```

## 参考资料

### 官方文档
- [Superset 监控指南](https://superset.apache.org/docs/installation/monitoring/)
- [Flask Prometheus 集成](https://flask.palletsprojects.com/en/2.0.x/patterns/apierrors/)

### 工具与集成
- [Prometheus 文档](https://prometheus.io/docs/introduction/overview/)
- [Grafana 仪表板](https://grafana.com/grafana/dashboards/)
- [ELK Stack 指南](https://www.elastic.co/guide/index.html)

### 最佳实践
- 监控关键指标：响应时间、错误率、吞吐量、资源使用率
- 建立性能基准并设置合理的告警阈值
- 实施集中式日志管理，便于故障排查
- 定期生成性能报告，跟踪系统性能趋势
- 考虑使用APM工具（如New Relic、Datadog）进行更深入的性能分析

## 总结

本章节介绍了Superset的监控与日志管理配置，包括系统监控、日志收集与分析、健康检查策略和性能监控指标。通过合理配置这些功能，您可以：

1. **实时监控系统状态**：及时发现并解决性能问题和错误
2. **深入分析用户行为**：了解用户如何使用Superset，优化用户体验
3. **预测性能瓶颈**：通过性能趋势分析，提前识别潜在问题
4. **自动化运维**：配置健康检查和告警，实现自动化故障检测和恢复

良好的监控与日志管理是保证Superset生产环境稳定运行的关键。建议根据实际部署规模和需求，逐步实施这些监控措施，并定期审查和优化监控策略。,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.3.7",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(superset_request_duration_seconds_bucket[5m])) by (le, endpoint))",
          "interval": "",
          "legendFormat": "{{endpoint}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "95%请求延迟（按端点）",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "s",
          "label": "秒",
          "logBase": 1,
          "max": null,
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "cacheTimeout": null,
      "colorBackground": false,
      "colorValue": false,
      "colors": [
        "#299c46",
        "rgba(237, 129, 40, 0.89)",
        "#d44a3a"
      ],
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "format": "short",
      "gauge": {
        "maxValue": 100,
        "minValue": 0,
        "show": false,
        "thresholdLabels": false,
        "thresholdMarkers": true
      },
      "gridPos": {
        "h": 8,
        "w": 6,
        "x": 0,
        "y": 8
      },
      "id": 3,
      "interval": null,
      "links": [],
      "mappingType": 1,
      "mappingTypes": [
        {
          "name": "value to text",
          "value": 1
        },
        {
          "name": "range to text",
          "value": 2
        }
      ],
      "maxDataPoints": 100,
      "nullPointMode": "connected",
      "nullText": null,
      "options": {
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        }
      },
      "pluginVersion": "7.3.7",
      "postfix": "",
      "postfixFontSize": "50%",
      "prefix": "",
      "prefixFontSize": "50%",
      "rangeMaps": [
        {
          "from": "null",
          "text": "N/A",
          "to": "null"
        }
      ],
      "sparkline": {
        "fillColor": "rgba(31, 118, 189, 0.18)",
        "full": false,
        "lineColor": "rgb(31, 120, 193)",
        "show": false
      },
      "tableColumn": "",
      "targets": [
        {
          "expr": "superset_active_users",
          "interval": "",
          "legendFormat": "",
          "refId": "A"
        }
      ],
      "thresholds": "",
      "title": "当前活动用户数",
      "type": "singlestat",
      "valueFontSize": "80%",
      "valueMaps": [
        {
          "op": "=",
          "text": "N/A",
          "value": "null"
        }
      ],
      "valueName": "current"
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 18,
        "x": 6,
        "y": 8
      },
      "hiddenSeries": false,
      "id": 4,
      "legend": {
        "avg": true,
        "current": false,
        "max": true,
        "min": false,
        "show": true,
        "total": false