# Day 10: 监控与日志 - 实践练习

## 🎯 练习目标

通过实践练习，掌握Airflow监控与日志管理的核心技能：
1. 配置和管理Airflow日志系统
2. 收集和分析系统监控指标
3. 实现自定义告警机制
4. 进行故障排查和性能优化

## 🏋️‍♂️ 基础练习

### 练习1: 配置日志系统

**目标**: 配置Airflow以将日志存储到远程存储（如S3）

**步骤**:
1. 创建一个S3存储桶用于存储日志
2. 配置Airflow连接以访问S3
3. 修改`airflow.cfg`文件启用远程日志存储
4. 验证日志是否正确写入S3

**配置示例**:
```ini
[logging]
remote_logging = True
remote_base_log_folder = s3://your-bucket/airflow-logs
remote_log_conn_id = aws_s3_logs
delete_local_logs = False
```

**验证方法**:
- 运行一个简单的DAG
- 检查S3存储桶中是否生成了日志文件
- 在Airflow Web UI中查看任务日志

### 练习2: 分析任务日志

**目标**: 编写脚本分析任务日志，识别常见错误模式

**步骤**:
1. 创建一个Python脚本用于分析Airflow日志
2. 实现错误模式识别功能
3. 统计不同类型错误的发生频率
4. 生成错误分析报告

**代码示例**:
```python
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

class LogAnalyzer:
    def __init__(self, log_directory):
        self.log_directory = log_directory
        self.error_patterns = {
            'connection_error': r'(Connection|connection).*error',
            'timeout_error': r'(Timeout|timeout)',
            'memory_error': r'(Memory|memory).*error',
            'syntax_error': r'SyntaxError',
            'import_error': r'ImportError|ModuleNotFoundError'
        }
    
    def analyze_recent_logs(self, days=7):
        """分析最近几天的日志"""
        cutoff_date = datetime.now() - timedelta(days=days)
        error_stats = defaultdict(int)
        
        for root, dirs, files in os.walk(self.log_directory):
            for file in files:
                if file.endswith('.log'):
                    file_path = os.path.join(root, file)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime >= cutoff_date:
                        self._analyze_file(file_path, error_stats)
        
        return dict(error_stats)
    
    def _analyze_file(self, file_path, error_stats):
        """分析单个日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    for error_type, pattern in self.error_patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            error_stats[error_type] += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# 使用示例
analyzer = LogAnalyzer('/path/to/airflow/logs')
stats = analyzer.analyze_recent_logs(days=7)
print("Error statistics:", stats)
```

## 🏋️‍♂️ 进阶练习

### 练习3: 集成Prometheus监控

**目标**: 配置Airflow以通过Prometheus端点暴露指标

**步骤**:
1. 安装和配置Prometheus服务器
2. 配置Airflow启用Prometheus指标
3. 创建Grafana仪表板展示关键指标
4. 设置告警规则

**配置示例**:
```ini
[metrics]
metrics_allow_list = 
metrics_block_list = 
statsd_on = False
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow

# 启用Flask exporter
flask_monitoringdashboard_host = 0.0.0.0
flask_monitoringdashboard_port = 5005
```

**Prometheus配置**:
```yaml
scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['airflow-webserver:8080']
```

### 练习4: 实现自定义告警系统

**目标**: 开发一个自定义告警系统，基于特定条件发送告警

**步骤**:
1. 创建一个Python类用于监控关键指标
2. 实现多种告警条件（如失败率、延迟等）
3. 集成多种通知渠道（邮件、Slack、Webhook等）
4. 配置告警抑制和去重机制

**代码示例**:
```python
from datetime import datetime, timedelta
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
import requests
import smtplib
from email.mime.text import MIMEText

class CustomAlertingSystem:
    def __init__(self, config):
        self.config = config
        self.notification_channels = {
            'email': self._send_email,
            'slack': self._send_slack,
            'webhook': self._send_webhook
        }
    
    def check_dag_health(self, dag_id, time_window_hours=24):
        """检查DAG健康状况"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # 获取DAG运行统计
        runs = DagRun.query.filter(
            DagRun.dag_id == dag_id,
            DagRun.start_date >= cutoff_time
        ).all()
        
        total_runs = len(runs)
        if total_runs == 0:
            return
        
        failed_runs = sum(1 for run in runs if run.state == State.FAILED)
        success_rate = (total_runs - failed_runs) / total_runs if total_runs > 0 else 0
        
        # 检查失败率是否超过阈值
        if success_rate < self.config.get('success_rate_threshold', 0.95):
            self._trigger_alert(
                'DAG_HEALTH',
                f"DAG {dag_id} success rate dropped to {success_rate:.2%}",
                {'dag_id': dag_id, 'success_rate': success_rate, 'total_runs': total_runs}
            )
    
    def check_task_delays(self, dag_id, delay_threshold_minutes=30):
        """检查任务延迟"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        delayed_tasks = TaskInstance.query.filter(
            TaskInstance.dag_id == dag_id,
            TaskInstance.start_date >= cutoff_time,
            TaskInstance.start_date > TaskInstance.execution_date + timedelta(minutes=delay_threshold_minutes)
        ).all()
        
        if delayed_tasks:
            self._trigger_alert(
                'TASK_DELAY',
                f"Found {len(delayed_tasks)} delayed tasks in DAG {dag_id}",
                {'dag_id': dag_id, 'delayed_count': len(delayed_tasks)}
            )
    
    def _trigger_alert(self, alert_type, message, details):
        """触发告警"""
        alert_data = {
            'type': alert_type,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        # 通过所有配置的渠道发送告警
        for channel in self.config.get('notification_channels', ['email']):
            if channel in self.notification_channels:
                try:
                    self.notification_channels[channel](alert_data)
                except Exception as e:
                    print(f"Failed to send alert via {channel}: {e}")
    
    def _send_email(self, alert_data):
        """发送邮件告警"""
        msg = MIMEText(f"Alert: {alert_data['message']}\nDetails: {alert_data['details']}")
        msg['Subject'] = f"Airflow Alert - {alert_data['type']}"
        msg['From'] = self.config.get('email_from', 'airflow@example.com')
        msg['To'] = ', '.join(self.config.get('email_to', []))
        
        smtp = smtplib.SMTP(self.config.get('smtp_host', 'localhost'))
        smtp.send_message(msg)
        smtp.quit()
    
    def _send_slack(self, alert_data):
        """发送Slack告警"""
        webhook_url = self.config.get('slack_webhook_url')
        if not webhook_url:
            return
        
        payload = {
            'text': f"Airflow Alert: {alert_data['message']}",
            'attachments': [{
                'color': 'danger',
                'fields': [
                    {'title': 'Type', 'value': alert_data['type'], 'short': True},
                    {'title': 'Time', 'value': alert_data['timestamp'], 'short': True},
                    {'title': 'Details', 'value': str(alert_data['details'])}
                ]
            }]
        }
        
        requests.post(webhook_url, json=payload)
    
    def _send_webhook(self, alert_data):
        """发送Webhook告警"""
        webhook_url = self.config.get('webhook_url')
        if not webhook_url:
            return
        
        requests.post(webhook_url, json=alert_data)

# 使用示例
config = {
    'success_rate_threshold': 0.95,
    'notification_channels': ['email', 'slack'],
    'email_from': 'airflow@example.com',
    'email_to': ['admin@example.com'],
    'smtp_host': 'smtp.example.com',
    'slack_webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
}

alerting_system = CustomAlertingSystem(config)
alerting_system.check_dag_health('example_dag')
alerting_system.check_task_delays('example_dag')
```

## 🏋️‍♂️ 挑战练习

### 练习5: 构建实时监控仪表板

**目标**: 使用Flask和WebSocket构建一个实时监控Airflow的Web仪表板

**步骤**:
1. 创建Flask应用提供实时监控界面
2. 实现WebSocket连接推送实时数据
3. 展示关键指标（运行中的任务、队列长度等）
4. 添加交互式图表和告警面板

**代码示例**:
```python
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

def background_monitor():
    """后台监控线程"""
    while True:
        # 获取实时数据
        active_runs = DagRun.query.filter(DagRun.state == State.RUNNING).count()
        queued_tasks = TaskInstance.query.filter(TaskInstance.state == State.QUEUED).count()
        running_tasks = TaskInstance.query.filter(TaskInstance.state == State.RUNNING).count()
        
        # 发送数据到前端
        socketio.emit('metrics_update', {
            'active_runs': active_runs,
            'queued_tasks': queued_tasks,
            'running_tasks': running_tasks,
            'timestamp': time.time()
        })
        
        time.sleep(5)  # 每5秒更新一次

@app.route('/')
def index():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == '__main__':
    # 启动后台监控线程
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # 启动Flask应用
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### 练习6: 性能优化分析

**目标**: 分析Airflow性能瓶颈并提出优化方案

**步骤**:
1. 使用性能分析工具（如py-spy）分析Airflow进程
2. 识别性能瓶颈（数据库查询、网络延迟等）
3. 实施优化措施（索引优化、缓存等）
4. 验证优化效果

**分析脚本**:
```python
import time
import psutil
from airflow.models import DagRun, TaskInstance
from airflow.utils.session import provide_session
from sqlalchemy import text

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = {}
    
    def measure_database_performance(self):
        """测量数据库性能"""
        start_time = time.time()
        
        # 测量复杂查询性能
        with provide_session() as session:
            # 模拟复杂查询
            result = session.execute(text("""
                SELECT dr.dag_id, COUNT(ti.task_id) as task_count
                FROM dag_run dr
                JOIN task_instance ti ON dr.dag_id = ti.dag_id
                WHERE dr.execution_date > NOW() - INTERVAL 7 DAY
                GROUP BY dr.dag_id
                ORDER BY task_count DESC
                LIMIT 10
            """))
            rows = result.fetchall()
        
        end_time = time.time()
        self.metrics['database_query_time'] = end_time - start_time
        self.metrics['result_rows'] = len(rows)
        
        return self.metrics
    
    def measure_system_resources(self):
        """测量系统资源使用情况"""
        process = psutil.Process()
        
        self.metrics['cpu_percent'] = process.cpu_percent()
        self.metrics['memory_mb'] = process.memory_info().rss / 1024 / 1024
        self.metrics['threads'] = process.num_threads()
        
        return self.metrics
    
    def generate_performance_report(self):
        """生成性能报告"""
        self.measure_database_performance()
        self.measure_system_resources()
        
        report = f"""
        Airflow Performance Report
        ==========================
        
        Database Performance:
        - Query Time: {self.metrics.get('database_query_time', 0):.4f} seconds
        - Result Rows: {self.metrics.get('result_rows', 0)}
        
        System Resources:
        - CPU Usage: {self.metrics.get('cpu_percent', 0):.2f}%
        - Memory Usage: {self.metrics.get('memory_mb', 0):.2f} MB
        - Thread Count: {self.metrics.get('threads', 0)}
        
        Recommendations:
        """
        
        # 基于测量结果提供优化建议
        if self.metrics.get('database_query_time', 0) > 1.0:
            report += "- Consider adding database indexes for frequently queried columns\n"
        
        if self.metrics.get('memory_mb', 0) > 500:
            report += "- Monitor memory usage and consider optimizing data processing\n"
        
        return report

# 使用示例
analyzer = PerformanceAnalyzer()
report = analyzer.generate_performance_report()
print(report)
```

## 📝 总结

完成这些练习后，你应该能够：
- 配置和管理Airflow日志系统
- 收集和分析系统监控指标
- 实现自定义告警机制
- 进行故障排查和性能优化
- 构建实时监控仪表板

记得在每个练习后更新你的学习总结！