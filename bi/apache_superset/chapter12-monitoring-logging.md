# 第十二章：监控与日志管理

## 12.1 监控与日志概述

有效的监控和日志管理是保障 Apache Superset 稳定运行的关键。通过建立完善的监控体系，可以及时发现和解决问题，确保系统的高可用性和性能。

### 监控的重要性

1. **故障预警**：提前发现潜在问题，避免系统宕机
2. **性能优化**：识别性能瓶颈，指导优化方向
3. **安全防护**：检测异常访问行为，防范安全威胁
4. **容量规划**：了解资源使用情况，合理规划扩容
5. **合规审计**：满足法规要求，提供审计证据

### 监控维度

#### 应用层监控

- 系统可用性
- 响应时间
- 错误率
- 用户体验指标

#### 基础设施监控

- CPU 使用率
- 内存使用情况
- 磁盘空间
- 网络流量

#### 业务监控

- 用户活跃度
- 查询性能
- 数据新鲜度
- 功能使用情况

## 12.2 日志配置与管理

### 日志级别配置

```python
# superset_config.py
# 日志级别配置
LOG_LEVEL = 'INFO'

# 不同模块的日志级别
LOG_LEVELS = {
    'werkzeug': 'WARN',
    'superset': 'INFO',
    'flask_appbuilder': 'INFO',
    'sqlalchemy': 'WARN',
    'celery': 'INFO'
}

# 日志格式配置
LOG_FORMAT = (
    '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)

# 详细日志格式（用于调试）
LOG_FORMAT_VERBOSE = (
    '%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s'
)
```

### 日志文件配置

```python
# superset_config.py
import os

# 日志文件配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': '/var/log/superset/superset.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': '/var/log/superset/superset_error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file', 'error_file']
    }
}
```

### 结构化日志

```python
# 结构化日志配置
import json
import logging

class JSONFormatter(logging.Formatter):
    """JSON 格式日志格式化器"""
    
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
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

# 在配置中使用
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'json': {
            '()': JSONFormatter
        }
    },
    'handlers': {
        'json_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': '/var/log/superset/superset.json',
            'maxBytes': 52428800,  # 50MB
            'backupCount': 10
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['json_file']
    }
}
```

## 12.3 应用监控配置

### Prometheus 集成

```python
# superset_config.py
# Prometheus 监控配置
PROMETHEUS_ENABLED = True
PROMETHEUS_ENDPOINT = '/metrics'
PROMETHEUS_NAMESPACE = 'superset'

# 自定义指标
CUSTOM_METRICS = {
    'query_execution_time': {
        'type': 'histogram',
        'description': 'Query execution time distribution',
        'labels': ['database', 'user']
    },
    'dashboard_load_time': {
        'type': 'histogram',
        'description': 'Dashboard load time distribution',
        'labels': ['dashboard_id']
    },
    'active_users': {
        'type': 'gauge',
        'description': 'Number of active users',
        'labels': ['role']
    }
}
```

### 自定义监控指标

```python
# 监控指标收集器
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义监控指标
QUERY_COUNTER = Counter('superset_queries_total', 'Total number of queries', ['database', 'status'])
QUERY_DURATION = Histogram('superset_query_duration_seconds', 'Query duration in seconds', ['database'])
ACTIVE_USERS = Gauge('superset_active_users', 'Number of active users', ['role'])

class MetricsCollector:
    """监控指标收集器"""
    
    @staticmethod
    def record_query(database, status, duration):
        """记录查询指标"""
        QUERY_COUNTER.labels(database=database, status=status).inc()
        QUERY_DURATION.labels(database=database).observe(duration)
    
    @staticmethod
    def update_active_users(role_counts):
        """更新活跃用户数"""
        for role, count in role_counts.items():
            ACTIVE_USERS.labels(role=role).set(count)
    
    @staticmethod
    def record_dashboard_load(dashboard_id, duration):
        """记录仪表板加载时间"""
        DASHBOARD_LOAD_TIME.labels(dashboard_id=dashboard_id).observe(duration)

# 在查询执行中使用
def execute_query_with_metrics(query, database):
    start_time = time.time()
    try:
        result = execute_query(query)
        duration = time.time() - start_time
        MetricsCollector.record_query(database, 'success', duration)
        return result
    except Exception as e:
        duration = time.time() - start_time
        MetricsCollector.record_query(database, 'error', duration)
        raise
```

### 健康检查端点

```python
# 健康检查实现
from flask import Blueprint, jsonify
import psutil
import redis
from sqlalchemy import text

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """基础健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })

@health_bp.route('/health/detailed')
def detailed_health_check():
    """详细健康检查"""
    checks = {}
    
    # 数据库检查
    try:
        db.session.execute(text('SELECT 1'))
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
    
    # Redis 检查
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        checks['redis'] = 'ok'
    except Exception as e:
        checks['redis'] = f'error: {str(e)}'
    
    # 系统资源检查
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    checks['system'] = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
    
    # 整体状态判断
    overall_status = 'healthy' if all(
        v == 'ok' or isinstance(v, dict) 
        for v in checks.values()
    ) else 'unhealthy'
    
    return jsonify({
        'status': overall_status,
        'checks': checks,
        'timestamp': time.time()
    })

# 注册健康检查端点
app.register_blueprint(health_bp)
```

## 12.4 日志分析与告警

### 日志聚合配置

```yaml
# fluentd 配置示例
<source>
  @type tail
  path /var/log/superset/superset.log
  pos_file /var/log/superset/superset.log.pos
  tag superset.access
  format json
  time_key timestamp
</source>

<filter superset.**>
  @type record_transformer
  <record>
    service superset
    environment production
  </record>
</filter>

<match superset.**>
  @type elasticsearch
  host elasticsearch.example.com
  port 9200
  logstash_format true
  logstash_prefix superset
</match>
```

### Elasticsearch + Kibana 配置

```python
# 日志发送到 Elasticsearch
import json
import requests
from datetime import datetime

class ElasticsearchLogger:
    """Elasticsearch 日志记录器"""
    
    def __init__(self, es_host, index_prefix='superset'):
        self.es_host = es_host
        self.index_prefix = index_prefix
    
    def log_event(self, event_data):
        """记录事件到 Elasticsearch"""
        index_name = f"{self.index_prefix}-{datetime.now().strftime('%Y.%m.%d')}"
        
        payload = {
            '@timestamp': datetime.utcnow().isoformat(),
            **event_data
        }
        
        try:
            response = requests.post(
                f"{self.es_host}/{index_name}/_doc",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload)
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Failed to send log to Elasticsearch: {e}")
            return False

# 使用示例
es_logger = ElasticsearchLogger('http://elasticsearch:9200')

def log_user_action(user_id, action, details):
    """记录用户操作"""
    log_data = {
        'user_id': user_id,
        'action': action,
        'details': details,
        'type': 'user_action'
    }
    es_logger.log_event(log_data)
```

### 告警规则配置

```python
# 告警规则配置
ALERT_RULES = {
    'high_error_rate': {
        'metric': 'error_rate',
        'threshold': 0.05,  # 5% 错误率
        'window': '5m',     # 5分钟窗口
        'severity': 'critical',
        'notification_channels': ['email', 'slack']
    },
    'slow_query': {
        'metric': 'query_duration',
        'threshold': 30,    # 30秒
        'window': '1m',
        'severity': 'warning',
        'notification_channels': ['email']
    },
    'high_cpu_usage': {
        'metric': 'cpu_percent',
        'threshold': 80,    # 80% CPU 使用率
        'window': '5m',
        'severity': 'warning',
        'notification_channels': ['slack']
    }
}

class AlertManager:
    """告警管理器"""
    
    def __init__(self, rules):
        self.rules = rules
        self.alert_history = {}
    
    def check_alerts(self, metrics):
        """检查告警条件"""
        triggered_alerts = []
        
        for rule_name, rule in self.rules.items():
            metric_value = metrics.get(rule['metric'], 0)
            
            if metric_value > rule['threshold']:
                alert = {
                    'rule': rule_name,
                    'metric': rule['metric'],
                    'value': metric_value,
                    'threshold': rule['threshold'],
                    'severity': rule['severity'],
                    'timestamp': time.time()
                }
                
                # 检查是否已经触发过相同告警（避免重复告警）
                if not self.is_recent_alert(rule_name):
                    triggered_alerts.append(alert)
                    self.record_alert(rule_name, alert)
                    self.send_notification(alert, rule['notification_channels'])
        
        return triggered_alerts
    
    def is_recent_alert(self, rule_name):
        """检查最近是否已触发相同告警"""
        if rule_name in self.alert_history:
            last_alert_time = self.alert_history[rule_name]
            # 告警冷却时间 5 分钟
            return time.time() - last_alert_time < 300
        return False
    
    def record_alert(self, rule_name, alert):
        """记录告警历史"""
        self.alert_history[rule_name] = alert['timestamp']
    
    def send_notification(self, alert, channels):
        """发送告警通知"""
        for channel in channels:
            if channel == 'email':
                self.send_email_alert(alert)
            elif channel == 'slack':
                self.send_slack_alert(alert)
    
    def send_email_alert(self, alert):
        """发送邮件告警"""
        # 邮件发送逻辑
        pass
    
    def send_slack_alert(self, alert):
        """发送 Slack 告警"""
        # Slack 发送逻辑
        pass
```

## 12.5 性能监控

### 查询性能监控

```python
# 查询性能监控装饰器
import time
import functools
from superset.utils.logging import get_logger

logger = get_logger(__name__)

def monitor_query_performance(func):
    """查询性能监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        query_start = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - query_start
            
            # 记录查询性能指标
            logger.info(
                f"Query executed: {func.__name__} "
                f"took {execution_time:.2f}s",
                extra={
                    'query_time': execution_time,
                    'query_name': func.__name__,
                    'status': 'success'
                }
            )
            
            # 更新 Prometheus 指标
            QUERY_DURATION.labels(query_type=func.__name__).observe(execution_time)
            QUERY_COUNTER.labels(query_type=func.__name__, status='success').inc()
            
            return result
        except Exception as e:
            execution_time = time.perf_counter() - query_start
            
            logger.error(
                f"Query failed: {func.__name__} "
                f"took {execution_time:.2f}s with error: {str(e)}",
                extra={
                    'query_time': execution_time,
                    'query_name': func.__name__,
                    'status': 'error',
                    'error': str(e)
                }
            )
            
            # 更新 Prometheus 指标
            QUERY_COUNTER.labels(query_type=func.__name__, status='error').inc()
            
            raise
        finally:
            total_time = time.time() - start_time
            logger.debug(f"Total function time: {total_time:.2f}s")
    
    return wrapper

# 使用示例
@monitor_query_performance
def execute_database_query(sql, database_id):
    """执行数据库查询"""
    # 查询执行逻辑
    pass
```

### 用户行为监控

```python
# 用户行为监控中间件
from flask import request, g
import uuid
import time

class UserBehaviorMonitor:
    """用户行为监控"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """请求开始时记录"""
        g.request_start_time = time.time()
        g.request_id = str(uuid.uuid4())
        
        # 记录请求基本信息
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'user_agent': request.headers.get('User-Agent'),
                'ip': request.remote_addr
            }
        )
    
    def after_request(self, response):
        """请求结束时记录"""
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"Status: {response.status_code} Duration: {duration:.3f}s",
                extra={
                    'request_id': getattr(g, 'request_id', ''),
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration
                }
            )
            
            # 更新 Prometheus 指标
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code
            ).observe(duration)
            
            RESPONSE_COUNTER.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code
            ).inc()
        
        return response
    
    def teardown_request(self, exception):
        """请求清理"""
        if exception:
            logger.error(
                f"Request failed: {request.method} {request.path} "
                f"Error: {str(exception)}",
                extra={
                    'request_id': getattr(g, 'request_id', ''),
                    'method': request.method,
                    'path': request.path,
                    'error': str(exception)
                }
            )

# 初始化监控
user_behavior_monitor = UserBehaviorMonitor()
```

## 12.6 审计日志

### 敏感操作审计

```python
# 敏感操作审计日志
import inspect
from functools import wraps

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        self.audit_events = []
    
    def log_event(self, event_type, user_id, details, severity='info'):
        """记录审计事件"""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'severity': severity,
            'ip_address': request.remote_addr if request else 'unknown',
            'user_agent': request.headers.get('User-Agent') if request else 'unknown'
        }
        
        # 记录到专门的审计日志文件
        audit_logger = logging.getLogger('audit')
        audit_logger.info(json.dumps(event))
        
        # 保存到内存（用于实时监控）
        self.audit_events.append(event)
        
        # 如果是高严重性事件，发送告警
        if severity in ['warning', 'error', 'critical']:
            self.send_alert(event)
    
    def send_alert(self, event):
        """发送安全告警"""
        # 告警发送逻辑
        pass

# 全局审计日志实例
audit_logger = AuditLogger()

def audit_log(event_type, severity='info'):
    """审计日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取当前用户
            user_id = getattr(g, 'user_id', 'anonymous')
            
            # 记录函数调用前的参数
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            details = {
                'function': func.__name__,
                'module': func.__module__,
                'args': dict(bound_args.arguments)
            }
            
            # 记录操作开始
            audit_logger.log_event(
                f"{event_type}_start", 
                user_id, 
                {**details, 'status': 'started'}, 
                severity
            )
            
            try:
                result = func(*args, **kwargs)
                
                # 记录操作成功
                audit_logger.log_event(
                    f"{event_type}_success", 
                    user_id, 
                    {**details, 'status': 'success', 'result': str(result)[:100]}, 
                    severity
                )
                
                return result
            except Exception as e:
                # 记录操作失败
                audit_logger.log_event(
                    f"{event_type}_failure", 
                    user_id, 
                    {**details, 'status': 'failed', 'error': str(e)}, 
                    'error' if severity == 'info' else severity
                )
                raise
        
        return wrapper
    return decorator

# 使用示例
@audit_log('user_login', 'info')
def login_user(username, password):
    """用户登录"""
    # 登录逻辑
    pass

@audit_log('data_export', 'warning')
def export_sensitive_data(user_id, dataset_id):
    """导出敏感数据"""
    # 数据导出逻辑
    pass
```

### 数据访问审计

```python
# 数据访问审计
class DataAccessAuditor:
    """数据访问审计器"""
    
    def __init__(self):
        self.access_log = []
    
    def log_data_access(self, user_id, dataset_id, query, access_type='read'):
        """记录数据访问"""
        access_record = {
            'timestamp': time.time(),
            'user_id': user_id,
            'dataset_id': dataset_id,
            'query': query[:500],  # 限制查询长度
            'access_type': access_type,
            'ip_address': request.remote_addr if request else 'unknown'
        }
        
        # 记录到数据访问日志
        data_access_logger = logging.getLogger('data_access')
        data_access_logger.info(json.dumps(access_record))
        
        # 实时分析
        self.analyze_access_pattern(access_record)
    
    def analyze_access_pattern(self, access_record):
        """分析访问模式"""
        user_id = access_record['user_id']
        dataset_id = access_record['dataset_id']
        
        # 检查是否为异常访问
        if self.is_suspicious_access(user_id, dataset_id):
            self.trigger_security_alert(access_record)
    
    def is_suspicious_access(self, user_id, dataset_id):
        """判断是否为可疑访问"""
        # 检查访问频率
        recent_accesses = self.get_recent_accesses(user_id, dataset_id, window_minutes=5)
        if len(recent_accesses) > 100:  # 5分钟内超过100次访问
            return True
        
        # 检查访问时间
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # 非工作时间大量访问
            recent_off_hours = self.get_accesses_in_time_range(
                user_id, dataset_id, 
                start_hour=22, end_hour=6
            )
            if len(recent_off_hours) > 50:
                return True
        
        return False
    
    def trigger_security_alert(self, access_record):
        """触发安全告警"""
        alert_details = {
            'type': 'suspicious_data_access',
            'user_id': access_record['user_id'],
            'dataset_id': access_record['dataset_id'],
            'timestamp': access_record['timestamp'],
            'description': 'Unusual data access pattern detected'
        }
        
        # 发送告警
        security_logger = logging.getLogger('security')
        security_logger.warning(json.dumps(alert_details))

# 全局数据访问审计实例
data_auditor = DataAccessAuditor()
```

## 12.7 日志轮转与清理

### 日志轮转配置

```python
# 日志轮转配置
import logging.handlers
import os

class LogRotationConfig:
    """日志轮转配置"""
    
    @staticmethod
    def configure_log_rotation():
        """配置日志轮转"""
        # 应用日志轮转
        app_handler = logging.handlers.TimedRotatingFileHandler(
            filename='/var/log/superset/app.log',
            when='midnight',
            interval=1,
            backupCount=30  # 保留30天日志
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # 错误日志轮转
        error_handler = logging.handlers.RotatingFileHandler(
            filename='/var/log/superset/error.log',
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        ))
        
        # 审计日志轮转
        audit_handler = logging.handlers.TimedRotatingFileHandler(
            filename='/var/log/superset/audit.log',
            when='W0',  # 每周轮转
            interval=1,
            backupCount=52  # 保留一年审计日志
        )
        audit_handler.setLevel(logging.INFO)
        audit_logger = logging.getLogger('audit')
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
        
        return app_handler, error_handler, audit_handler

# 初始化日志轮转
log_handlers = LogRotationConfig.configure_log_rotation()
```

### 日志清理脚本

```bash
#!/bin/bash
# 日志清理脚本

# 配置变量
LOG_DIR="/var/log/superset"
RETENTION_DAYS=90

# 清理旧的应用日志
find ${LOG_DIR} -name "app.log.*" -mtime +${RETENTION_DAYS} -delete

# 清理旧的错误日志
find ${LOG_DIR} -name "error.log.*" -mtime +${RETENTION_DAYS} -delete

# 清理旧的审计日志
find ${LOG_DIR} -name "audit.log.*" -mtime +365 -delete

# 清理压缩的日志文件
find ${LOG_DIR} -name "*.gz" -mtime +${RETENTION_DAYS} -delete

# 检查磁盘使用情况
USAGE=$(df ${LOG_DIR} | awk 'NR==2 {print $5}' | sed 's/%//')
if [ ${USAGE} -gt 80 ]; then
    echo "Warning: Disk usage is ${USAGE}%"
    # 删除最旧的日志文件
    find ${LOG_DIR} -name "*.log.*" -mtime +60 -delete
fi

echo "Log cleanup completed at $(date)"
```

## 12.8 监控面板配置

### Grafana 监控面板

```json
{
  "dashboard": {
    "title": "Apache Superset Monitoring",
    "panels": [
      {
        "title": "Query Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(superset_query_duration_seconds_sum[5m]) / rate(superset_query_duration_seconds_count[5m])",
            "legendFormat": "Average Query Time"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "superset_active_users",
            "legendFormat": "{{role}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(superset_queries_total{status=\"error\"}[5m]) / rate(superset_queries_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

### 自定义监控仪表板

```python
# 自定义监控仪表板
from flask import Blueprint, render_template, jsonify
import psutil
import time

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/monitoring/system')
def system_metrics():
    """系统指标监控"""
    return jsonify({
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'network_io': {
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv
        },
        'timestamp': time.time()
    })

@monitoring_bp.route('/monitoring/application')
def application_metrics():
    """应用指标监控"""
    return jsonify({
        'active_connections': get_active_connections(),
        'queued_queries': get_queued_queries(),
        'cache_hit_rate': get_cache_hit_rate(),
        'uptime': get_application_uptime(),
        'timestamp': time.time()
    })

@monitoring_bp.route('/monitoring/dashboard')
def monitoring_dashboard():
    """监控仪表板页面"""
    return render_template('monitoring/dashboard.html')

# 注册监控蓝图
app.register_blueprint(monitoring_bp, url_prefix='/admin')
```

## 12.9 故障排查与诊断

### 诊断工具

```python
# 系统诊断工具
class DiagnosticTool:
    """系统诊断工具"""
    
    def __init__(self):
        self.diagnostic_results = {}
    
    def run_full_diagnosis(self):
        """运行完整诊断"""
        self.diagnostic_results = {
            'timestamp': time.time(),
            'system_checks': self.check_system_resources(),
            'application_checks': self.check_application_health(),
            'database_checks': self.check_database_connectivity(),
            'cache_checks': self.check_cache_status(),
            'network_checks': self.check_network_connectivity()
        }
        
        return self.diagnostic_results
    
    def check_system_resources(self):
        """检查系统资源"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'available': psutil.virtual_memory().available,
                'total': psutil.virtual_memory().total
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'free': psutil.disk_usage('/').free,
                'total': psutil.disk_usage('/').total
            }
        }
    
    def check_application_health(self):
        """检查应用健康状态"""
        try:
            # 检查应用是否响应
            response = requests.get('http://localhost:8088/health', timeout=5)
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_database_connectivity(self):
        """检查数据库连接"""
        try:
            db.session.execute(text('SELECT 1'))
            return {'status': 'connected'}
        except Exception as e:
            return {
                'status': 'disconnected',
                'error': str(e)
            }
    
    def check_cache_status(self):
        """检查缓存状态"""
        try:
            from superset import cache
            cache.set('diagnostic_test', 'test_value', timeout=10)
            value = cache.get('diagnostic_test')
            return {
                'status': 'working' if value == 'test_value' else 'not_working'
            }
        except Exception as e:
            return {
                'status': 'not_working',
                'error': str(e)
            }
    
    def generate_diagnostic_report(self):
        """生成诊断报告"""
        results = self.run_full_diagnosis()
        
        report = f"""
Apache Superset Diagnostic Report
=================================

Generated at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['timestamp']))}

SYSTEM RESOURCES:
  CPU Usage: {results['system_checks']['cpu_percent']}%
  Memory Usage: {results['system_checks']['memory']['percent']}%
  Disk Usage: {results['system_checks']['disk']['percent']}%

APPLICATION HEALTH:
  Status: {results['application_checks']['status']}
  Response Time: {results['application_checks'].get('response_time', 'N/A')}s

DATABASE CONNECTIVITY:
  Status: {results['database_checks']['status']}

CACHE STATUS:
  Status: {results['cache_checks']['status']}
        """
        
        return report

# 使用诊断工具
diagnostic_tool = DiagnosticTool()
```

### 性能剖析工具

```python
# 性能剖析工具
import cProfile
import pstats
import io
from functools import wraps

class PerformanceProfiler:
    """性能剖析工具"""
    
    def __init__(self, output_dir='/var/log/superset/profiling'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def profile_function(self, func):
        """函数性能剖析装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建 profiler
            pr = cProfile.Profile()
            pr.enable()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                pr.disable()
                
                # 生成剖析报告
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s)
                ps.sort_stats('cumulative')
                ps.print_stats(20)  # 显示前20个最耗时的函数
                
                # 保存报告
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                report_filename = f"{self.output_dir}/{func.__name__}_{timestamp}.prof"
                with open(report_filename, 'w') as f:
                    f.write(s.getvalue())
                
                logger.info(f"Performance profile saved to {report_filename}")
        
        return wrapper
    
    def profile_request(self, endpoint_name):
        """请求性能剖析"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.should_profile_request():
                    return self.profile_function(func)(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def should_profile_request(self):
        """决定是否对请求进行剖析"""
        # 可以基于随机采样或其他条件决定
        import random
        return random.random() < 0.01  # 1% 的请求进行剖析

# 使用性能剖析工具
profiler = PerformanceProfiler()

@profiler.profile_function
def complex_dashboard_render(dashboard_id):
    """复杂的仪表板渲染函数"""
    # 仪表板渲染逻辑
    pass
```

## 12.10 最佳实践总结

### 监控配置清单

```python
# 监控配置最佳实践
MONITORING_BEST_PRACTICES = {
    'essential_metrics': [
        'application_uptime',
        'response_time',
        'error_rate',
        'cpu_usage',
        'memory_usage',
        'disk_space',
        'database_connection_pool'
    ],
    'alert_thresholds': {
        'response_time_warning': 2.0,    # 2秒
        'response_time_critical': 5.0,   # 5秒
        'error_rate_warning': 0.01,      # 1%
        'error_rate_critical': 0.05,     # 5%
        'cpu_usage_warning': 70,         # 70%
        'cpu_usage_critical': 90,        # 90%
        'memory_usage_warning': 80,      # 80%
        'memory_usage_critical': 95      # 95%
    },
    'log_retention': {
        'application_logs': '30d',
        'error_logs': '90d',
        'audit_logs': '1y',
        'debug_logs': '7d'
    }
}
```

### 日志管理最佳实践

1. **结构化日志**：使用 JSON 格式便于解析和分析
2. **分级管理**：不同级别的日志分别存储和处理
3. **轮转策略**：合理设置日志轮转和清理策略
4. **安全存储**：审计日志单独存储，防止篡改
5. **实时监控**：关键日志实时监控和告警
6. **合规保留**：根据法规要求保留相应期限的日志

### 监控告警策略

```python
# 告警策略配置
ALERT_STRATEGY = {
    'escalation_levels': [
        {
            'level': 1,
            'channels': ['slack'],
            'repeat_interval': '5m',
            'max_notifications': 3
        },
        {
            'level': 2,
            'channels': ['slack', 'email'],
            'repeat_interval': '15m',
            'max_notifications': 5
        },
        {
            'level': 3,
            'channels': ['slack', 'email', 'sms'],
            'repeat_interval': '30m',
            'max_notifications': 10
        }
    ],
    'silence_rules': [
        {
            'pattern': 'maintenance_window',
            'start_time': '02:00',
            'end_time': '04:00',
            'days': ['Sun']
        }
    ]
}
```

## 12.11 小结

本章详细介绍了 Apache Superset 的监控与日志管理方案，包括日志配置、应用监控、性能监控、审计日志、日志轮转清理以及故障诊断等多个方面。通过建立完善的监控体系，可以确保 Superset 系统的稳定运行，及时发现和解决问题。

在下一章中，我们将学习 Apache Superset 的备份与恢复策略。