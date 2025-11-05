# Day 10: 监控与日志 - 学习资料

## 📘 核心概念

### Airflow日志系统架构

Airflow的日志系统设计用于跟踪DAG执行、任务运行和系统事件。理解其架构对于有效监控和故障排查至关重要。

#### 日志类型
1. **任务日志 (Task Logs)**: 每个任务实例执行时生成的日志
2. **调度器日志 (Scheduler Logs)**: 调度器运行时的日志
3. **Web服务器日志 (Webserver Logs)**: Web界面访问和操作日志
4. **工作者日志 (Worker Logs)**: 在分布式环境中工作者节点的日志

#### 日志存储
- **本地存储**: 默认情况下，日志存储在本地文件系统中
- **远程存储**: 可配置为存储在S3、GCS、Azure Blob等云存储中
- **数据库存储**: 某些情况下日志可以存储在数据库中

### 监控指标体系

Airflow提供了丰富的监控指标，可以帮助你了解系统健康状况和性能表现。

#### 核心指标类别
1. **DAG指标**: DAG执行成功率、执行时间等
2. **任务指标**: 任务执行状态、重试次数等
3. **系统指标**: 内存使用、CPU使用率等
4. **调度器指标**: 调度延迟、DAG处理速率等

#### 指标收集方式
- **StatsD**: 通过StatsD协议收集指标
- **Prometheus**: 通过Prometheus端点暴露指标
- **自定义收集器**: 编写自定义代码收集特定指标

## 🛠️ 配置指南

### 日志配置

Airflow的日志配置主要在`airflow.cfg`文件中进行：

```ini
[logging]
# 日志级别
logging_level = INFO

# 日志格式
log_format = [%%(asctime)s] {%%(filename)s:%%(lineno)d} %%(levelname)s - %%(message)s
simple_log_format = %%(asctime)s %%(levelname)s - %%(message)s

# 日志文件位置
base_log_folder = /usr/local/airflow/logs
dag_processor_manager_log_location = /usr/local/airflow/logs/dag_processor_manager/dag_processor_manager.log

# 任务日志相关配置
task_log_reader = task
# 是否在Web UI中显示日志
show_log_confidence = True

# 远程日志配置
remote_logging = False
remote_base_log_folder =
remote_log_conn_id =
delete_local_logs = False
```

### 监控配置

监控配置通常涉及指标收集和告警设置：

```ini
[scheduler]
# 调度器相关指标
scheduler_heartbeat_sec = 5
scheduler_health_check_threshold = 30

[metrics]
# 指标收集配置
metrics_allow_list = 
metrics_block_list = 
statsd_on = False
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow

[smtp]
# SMTP配置用于发送告警邮件
smtp_host = localhost
smtp_starttls = True
smtp_ssl = False
smtp_port = 25
smtp_mail_from = airflow@example.com
```

## 📊 实践示例

### 日志分析脚本

```python
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

class AirflowLogAnalyzer:
    def __init__(self, log_directory):
        self.log_directory = log_directory
        self.error_patterns = [
            r'ERROR',
            r'FAILED',
            r'Exception',
            r'Traceback'
        ]
    
    def analyze_task_logs(self, dag_id, days=7):
        """分析指定DAG的任务日志"""
        cutoff_date = datetime.now() - timedelta(days=days)
        error_summary = defaultdict(int)
        
        dag_log_path = os.path.join(self.log_directory, dag_id)
        if not os.path.exists(dag_log_path):
            print(f"No logs found for DAG: {dag_id}")
            return {}
        
        for root, dirs, files in os.walk(dag_log_path):
            for file in files:
                if file.endswith('.log'):
                    file_path = os.path.join(root, file)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_date >= cutoff_date:
                        self._analyze_log_file(file_path, error_summary)
        
        return dict(error_summary)
    
    def _analyze_log_file(self, file_path, error_summary):
        """分析单个日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    for pattern in self.error_patterns:
                        if re.search(pattern, line):
                            error_summary[pattern] += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# 使用示例
analyzer = AirflowLogAnalyzer('/usr/local/airflow/logs')
errors = analyzer.analyze_task_logs('example_dag', days=7)
print("Error summary:", errors)
```

### 指标收集器

```python
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
from datetime import datetime, timedelta
import statsd

class AirflowMetricsCollector:
    def __init__(self, statsd_host='localhost', statsd_port=8125, prefix='airflow'):
        self.statsd_client = statsd.StatsClient(statsd_host, statsd_port, prefix=prefix)
    
    def collect_dag_metrics(self):
        """收集DAG相关指标"""
        # 获取最近24小时的DAG运行情况
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # 成功的DAG运行
        successful_runs = DagRun.query.filter(
            DagRun.state == State.SUCCESS,
            DagRun.start_date >= cutoff_time
        ).count()
        
        # 失败的DAG运行
        failed_runs = DagRun.query.filter(
            DagRun.state == State.FAILED,
            DagRun.start_date >= cutoff_time
        ).count()
        
        # 发送指标到StatsD
        self.statsd_client.gauge('dag.runs.successful', successful_runs)
        self.statsd_client.gauge('dag.runs.failed', failed_runs)
        
        if successful_runs + failed_runs > 0:
            success_rate = successful_runs / (successful_runs + failed_runs) * 100
            self.statsd_client.gauge('dag.runs.success_rate', success_rate)
    
    def collect_task_metrics(self):
        """收集任务相关指标"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # 获取任务实例状态统计
        task_states = TaskInstance.query.with_entities(
            TaskInstance.state,
            db.func.count(TaskInstance.state)
        ).filter(
            TaskInstance.start_date >= cutoff_time
        ).group_by(TaskInstance.state).all()
        
        for state, count in task_states:
            if state:
                self.statsd_client.gauge(f'task.instances.{state.lower()}', count)

# 使用示例
collector = AirflowMetricsCollector()
collector.collect_dag_metrics()
collector.collect_task_metrics()
```

### 告警系统

```python
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils.email import send_email
import logging

class AirflowAlertingSystem:
    def __init__(self, smtp_config):
        self.smtp_config = smtp_config
        self.logger = logging.getLogger(__name__)
    
    def check_dag_failures(self, dag_id, threshold=3):
        """检查DAG失败次数是否超过阈值"""
        # 获取最近的DAG运行
        recent_runs = DagRun.query.filter(
            DagRun.dag_id == dag_id
        ).order_by(DagRun.execution_date.desc()).limit(threshold).all()
        
        # 统计失败次数
        failed_count = sum(1 for run in recent_runs if run.state == State.FAILED)
        
        if failed_count >= threshold:
            self._send_failure_alert(dag_id, failed_count, recent_runs)
            return True
        return False
    
    def _send_failure_alert(self, dag_id, failed_count, recent_runs):
        """发送失败告警邮件"""
        subject = f"Airflow DAG Alert: {dag_id} has failed {failed_count} times"
        
        # 构建邮件内容
        html_content = f"""
        <h2>Airflow DAG Failure Alert</h2>
        <p><strong>DAG ID:</strong> {dag_id}</p>
        <p><strong>Consecutive Failures:</strong> {failed_count}</p>
        <p><strong>Recent Runs:</strong></p>
        <ul>
        """
        
        for run in recent_runs:
            html_content += f"<li>{run.execution_date} - {run.state}</li>"
        
        html_content += """
        </ul>
        <p>Please check the Airflow UI and logs for more details.</p>
        """
        
        try:
            send_email(
                to=['admin@example.com'],
                subject=subject,
                html_content=html_content,
                smtp_host=self.smtp_config.get('host', 'localhost'),
                smtp_port=self.smtp_config.get('port', 25),
                smtp_user=self.smtp_config.get('user'),
                smtp_password=self.smtp_config.get('password')
            )
            self.logger.info(f"Alert email sent for DAG {dag_id}")
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {e}")

# 使用示例
smtp_config = {
    'host': 'smtp.example.com',
    'port': 587,
    'user': 'airflow@example.com',
    'password': 'password'
}

alerting_system = AirflowAlertingSystem(smtp_config)
alerting_system.check_dag_failures('example_dag', threshold=3)
```

## 🔧 故障排查技巧

### 常见问题及解决方案

1. **日志不显示在Web UI中**
   - 检查`airflow.cfg`中的日志配置
   - 确认日志文件权限
   - 验证远程日志存储配置

2. **监控指标不更新**
   - 检查StatsD配置是否正确
   - 确认网络连接是否正常
   - 验证指标收集代码是否执行

3. **告警邮件发送失败**
   - 检查SMTP配置
   - 确认网络连接和防火墙设置
   - 验证邮件服务器状态

### 调试工具

1. **Airflow CLI命令**
   ```bash
   # 查看任务日志
   airflow tasks test <dag_id> <task_id> <execution_date>
   
   # 查看DAG运行状态
   airflow dags list-runs -d <dag_id>
   
   # 查看任务实例状态
   airflow tasks list <dag_id>
   ```

2. **日志级别调整**
   ```python
   import logging
   
   # 临时提高日志级别用于调试
   logging.getLogger('airflow').setLevel(logging.DEBUG)
   ```

## 📚 扩展阅读

### 官方资源
- [Airflow Logging Documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging.html)
- [Airflow Metrics Documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/metrics.html)
- [Airflow Alerts Documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/alerts.html)

### 社区资源
- [Airflow GitHub Issues](https://github.com/apache/airflow/issues)
- [Airflow Slack Community](https://apache-airflow.slack.com)
- [Stack Overflow Airflow Tag](https://stackoverflow.com/questions/tagged/apache-airflow)

### 第三方工具集成
- **Prometheus**: 用于指标收集和可视化
- **Grafana**: 用于创建监控仪表板
- **ELK Stack**: 用于日志收集和分析
- **Datadog**: 用于全面的监控和告警