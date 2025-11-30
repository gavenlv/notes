# 第9章：RabbitMQ监控与运维

## 📖 概述

本章节深入探讨RabbitMQ的监控与运维最佳实践，包括性能监控、日志管理、告警配置、健康检查、容量规划和故障诊断等关键运维任务。通过完善的监控体系和自动化运维工具，确保RabbitMQ集群的稳定运行。

### 🎯 学习目标

- 掌握RabbitMQ监控指标体系和关键性能指标
- 学会配置Prometheus、Grafana等监控工具
- 理解日志管理和分析的最佳实践
- 掌握告警配置和故障诊断技巧
- 学会容量规划和性能调优方法
- 了解自动化运维和DevOps集成

## 🔍 核心概念

### 1. 监控层次结构

RabbitMQ监控通常分为四个层次：

- **系统层监控**: CPU、内存、磁盘、网络等基础资源
- **容器层监控**: Docker/Kubernetes容器资源使用
- **应用层监控**: RabbitMQ进程、队列、连接等应用指标
- **业务层监控**: 消息延迟、吞吐量、错误率等业务指标

### 2. 关键监控指标

#### 系统指标
- CPU使用率、负载平均值
- 内存使用率、交换分区使用
- 磁盘空间使用率、I/O性能
- 网络带宽使用率、连接数

#### 应用指标
- 连接数、通道数、队列数
- 消息发布/消费速率
- 队列深度、消息堆积
- 消息确认率、重试率
- 错误率、超时率

#### 性能指标
- 消息延迟（端到端延迟）
- 吞吐量（消息/秒）
- 系统响应时间
- 资源利用率

### 3. 监控工具生态

```
数据采集层: RabbitMQ插件、Node Exporter、Prometheus Client
数据存储层: Prometheus、InfluxDB、Elasticsearch
数据展示层: Grafana、Kibana、自定义仪表板
告警层: Alertmanager、PagerDuty、Slack
日志层: ELK Stack、Fluentd、Loki
```

## 🛠 监控工具配置

### 1. Prometheus监控集成

#### 安装Prometheus插件

```bash
# 启用Prometheus插件
rabbitmq-plugins enable rabbitmq_prometheus

# 检查插件状态
rabbitmq-plugins list | grep prometheus
```

#### 配置Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rabbitmq_rules.yml"

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['localhost:15692']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s
    params:
      format: ['prometheus']
```

#### RabbitMQ告警规则

```yaml
# rabbitmq_rules.yml
groups:
- name: rabbitmq.rules
  rules:
  - alert: RabbitMQDown
    expr: up{job="rabbitmq"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "RabbitMQ instance is down"
      description: "RabbitMQ instance {{ $labels.instance }} is down for more than 1 minute."
      
  - alert: RabbitMQHighMemoryUsage
    expr: rabbitmq_process_resident_memory_bytes / rabbitmq_process_max_memory_bytes > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ high memory usage"
      description: "RabbitMQ instance {{ $labels.instance }} is using {{ $value | humanizePercentage }} of available memory."
      
  - alert: RabbitMQDiskSpaceLow
    expr: rabbitmq_disk_space_available_bytes / rabbitmq_disk_space_available_limit_bytes < 0.2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ low disk space"
      description: "RabbitMQ instance {{ $labels.instance }} has less than 20% disk space available."
      
  - alert: RabbitMQQueueMessagesHigh
    expr: rabbitmq_queue_messages > 10000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ queue high message count"
      description: "Queue {{ $labels.queue }} on {{ $labels.instance }} has {{ $value }} messages."
      
  - alert: RabbitMQConnectionCountHigh
    expr: rabbitmq_connections > 1000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ high connection count"
      description: "RabbitMQ instance {{ $labels.instance }} has {{ $value }} connections."
      
  - alert: RabbitMQChannelCountHigh
    expr: rabbitmq_channels > 2000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ high channel count"
      description: "RabbitMQ instance {{ $labels.instance }} has {{ $value }} channels."
```

### 2. Grafana仪表板配置

#### 创建数据源

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "basicAuth": false,
  "jsonData": {
    "httpMethod": "POST"
  }
}
```

#### RabbitMQ概览仪表板

```json
{
  "dashboard": {
    "id": null,
    "title": "RabbitMQ Overview",
    "tags": ["rabbitmq", "messaging"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "Connection Count",
        "type": "stat",
        "targets": [
          {
            "expr": "rabbitmq_connections",
            "legendFormat": "Total Connections"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 500},
                {"color": "red", "value": 1000}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "Message Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(rabbitmq_channel_messages_published_total[5m])",
            "legendFormat": "Publish Rate"
          },
          {
            "expr": "rate(rabbitmq_channel_messages_delivered_total[5m])",
            "legendFormat": "Deliver Rate"
          }
        ]
      },
      {
        "id": 3,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rabbitmq_process_resident_memory_bytes",
            "legendFormat": "Memory Usage"
          },
          {
            "expr": "rabbitmq_process_max_memory_bytes",
            "legendFormat": "Memory Limit"
          }
        ]
      },
      {
        "id": 4,
        "title": "Disk Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rabbitmq_disk_space_available_bytes",
            "legendFormat": "Available Disk Space"
          }
        ]
      },
      {
        "id": 5,
        "title": "Queue Depth",
        "type": "table",
        "targets": [
          {
            "expr": "rabbitmq_queue_messages",
            "legendFormat": "{{queue}}"
          }
        ],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "excludeByName": {},
              "indexByName": {},
              "renameByName": {
                "queue": "Queue Name",
                "Value": "Message Count"
              }
            }
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}
```

### 3. 日志管理配置

#### 配置RabbitMQ日志

```conf
# rabbitmq.conf
log.file.level = info
log.file.path = /var/log/rabbitmq/rabbit.log
log.file.rotation.date = $D0
log.file.rotation.count = 7

log.console = true
log.console.level = info

log.exchange = true
log.exchange.level = info

# 启用审计日志
log_levels.connection = debug
log_levels.authentication_failure_detailed = true
```

#### Filebeat配置

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/rabbitmq/*.log
  fields:
    service: rabbitmq
    environment: production
  multiline.pattern: '^[[:space:]]'
  multiline.negate: false
  multiline.match: after

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "rabbitmq-logs-%{+yyyy.MM.dd}"

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
```

## 📈 性能监控与分析

### 1. 消息延迟监控

#### 延迟监控实现

```python
import time
import pika
import json
from datetime import datetime
from typing import Dict, List
import logging

class MessageLatencyMonitor:
    """消息延迟监控器"""
    
    def __init__(self, rabbitmq_url: str, queue_name: str = "latency_test"):
        self.rabbitmq_url = rabbitmq_url
        self.queue_name = queue_name
        self.latencies = []
        self.logger = logging.getLogger(__name__)
        
    def setup_test_queue(self):
        """设置测试队列"""
        connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        channel = connection.channel()
        
        # 声明测试队列
        channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments={
                'x-message-ttl': 600000,  # 10分钟TTL
                'x-dead-letter-exchange': 'dlx.latency_test'
            }
        )
        
        # 设置消费者
        channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._on_message_received,
            auto_ack=False
        )
        
        connection.close()
        
    def _on_message_received(self, ch, method, properties, body):
        """消息接收回调"""
        try:
            # 解析消息时间戳
            message_data = json.loads(body.decode())
            sent_time = datetime.fromisoformat(message_data['timestamp'])
            received_time = datetime.now()
            
            # 计算延迟（毫秒）
            latency_ms = (received_time - sent_time).total_seconds() * 1000
            
            # 记录延迟
            self.latencies.append({
                'timestamp': received_time.isoformat(),
                'latency_ms': latency_ms,
                'message_id': message_data['message_id']
            })
            
            self.logger.info(f"消息延迟: {latency_ms:.2f}ms")
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            self.logger.error(f"处理消息时出错: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
    def send_test_message(self, message_id: str):
        """发送测试消息"""
        connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        channel = connection.channel()
        
        message_data = {
            'message_id': message_id,
            'timestamp': datetime.now().isoformat(),
            'test_type': 'latency'
        }
        
        channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message_data).encode(),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 持久化
                timestamp=int(time.time() * 1000)
            )
        )
        
        connection.close()
        self.logger.info(f"发送测试消息: {message_id}")
        
    def get_latency_stats(self) -> Dict:
        """获取延迟统计信息"""
        if not self.latencies:
            return {'error': 'No latency data available'}
            
        latencies = [l['latency_ms'] for l in self.latencies]
        
        return {
            'count': len(latencies),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'avg_latency_ms': sum(latencies) / len(latencies),
            'p50_latency_ms': self._percentile(latencies, 50),
            'p95_latency_ms': self._percentile(latencies, 95),
            'p99_latency_ms': self._percentile(latencies, 99)
        }
        
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[index]
        
    def export_metrics(self) -> Dict:
        """导出监控指标"""
        stats = self.get_latency_stats()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'queue_name': self.queue_name,
            'latency_stats': stats,
            'recent_latencies': self.latencies[-100:]  # 最近100条
        }
```

### 2. 吞吐量监控

```python
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta

class ThroughputMonitor:
    """吞吐量监控器"""
    
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.publish_counts = defaultdict(int)
        self.consume_counts = defaultdict(int)
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 60):
        """开始监控"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 获取当前统计
                current_stats = self._get_current_stats()
                
                # 计算吞吐量
                throughput = self._calculate_throughput(current_stats, interval)
                
                # 记录数据
                self._log_throughput(throughput)
                
                # 等待下一个周期
                time.sleep(interval)
                
            except Exception as e:
                logging.error(f"监控循环错误: {e}")
                time.sleep(interval)
                
    def _get_current_stats(self) -> Dict:
        """获取当前统计"""
        import pika
        
        connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        channel = connection.channel()
        
        # 获取队列统计
        queue_stats = {}
        try:
            result = channel.queue_declare(queue='', passive=True)
            queue_stats['messages'] = result.method.message_count
            queue_stats['consumers'] = result.method.consumer_count
        except:
            pass
            
        connection.close()
        
        return queue_stats
        
    def _calculate_throughput(self, current_stats: Dict, interval: int) -> Dict:
        """计算吞吐量"""
        current_time = datetime.now()
        
        # 计算消息速率
        publish_rate = self.publish_counts[current_time] / interval
        consume_rate = self.consume_counts[current_time] / interval
        
        return {
            'timestamp': current_time.isoformat(),
            'publish_rate': publish_rate,
            'consume_rate': consume_rate,
            'total_messages': current_stats.get('messages', 0),
            'interval_seconds': interval
        }
        
    def _log_throughput(self, throughput: Dict):
        """记录吞吐量"""
        logging.info(f"吞吐量 - 发布: {throughput['publish_rate']:.2f} msg/s, "
                    f"消费: {throughput['consume_rate']:.2f} msg/s")
```

### 3. 错误率监控

```python
import requests
from datetime import datetime
from typing import Dict, List

class ErrorRateMonitor:
    """错误率监控器"""
    
    def __init__(self, rabbitmq_api_url: str, username: str, password: str):
        self.api_url = rabbitmq_api_url
        self.auth = (username, password)
        self.error_counts = defaultdict(int)
        self.total_counts = defaultdict(int)
        
    def get_cluster_status(self) -> Dict:
        """获取集群状态"""
        try:
            response = requests.get(f"{self.api_url}/api/overview", auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"获取集群状态失败: {e}")
            return {}
            
    def get_node_status(self, node_name: str) -> Dict:
        """获取节点状态"""
        try:
            response = requests.get(f"{self.api_url}/api/nodes/{node_name}", auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"获取节点状态失败: {e}")
            return {}
            
    def get_queue_status(self, queue_name: str) -> Dict:
        """获取队列状态"""
        try:
            response = requests.get(f"{self.api_url}/api/queues/%2F/{queue_name}", auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"获取队列状态失败: {e}")
            return {}
            
    def calculate_error_rate(self, time_window: int = 300) -> Dict:
        """计算错误率"""
        current_time = datetime.now()
        
        # 获取错误统计
        cluster_stats = self.get_cluster_status()
        
        # 计算各种错误率
        error_rates = {
            'timestamp': current_time.isoformat(),
            'connection_error_rate': self._calculate_connection_error_rate(cluster_stats),
            'channel_error_rate': self._calculate_channel_error_rate(cluster_stats),
            'message_error_rate': self._calculate_message_error_rate(cluster_stats),
            'queue_error_rate': self._calculate_queue_error_rate(cluster_stats)
        }
        
        return error_rates
        
    def _calculate_connection_error_rate(self, stats: Dict) -> float:
        """计算连接错误率"""
        total_connections = stats.get('object_totals', {}).get('connections', 0)
        failed_connections = stats.get('connection_churn_rates', {}).get('connection_closed_details', {}).get('rate', 0)
        
        if total_connections > 0:
            return (failed_connections / total_connections) * 100
        return 0.0
        
    def _calculate_message_error_rate(self, stats: Dict) -> float:
        """计算消息错误率"""
        total_messages = stats.get('queue_totals', {}).get('messages', 0)
        failed_messages = stats.get('message_stats', {}).get('redeliver', 0)
        
        if total_messages > 0:
            return (failed_messages / total_messages) * 100
        return 0.0
```

## 🚨 告警管理

### 1. 告警配置

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'rabbitmq-alerts@example.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'critical-alerts'
  email_configs:
  - to: 'ops-team@example.com'
    subject: '[CRITICAL] RabbitMQ Alert - {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Instance: {{ .Labels.instance }}
      Severity: {{ .Labels.severity }}
      {{ end }}
  
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#ops-alerts'
    title: 'RabbitMQ Critical Alert'
    text: |
      {{ range .Alerts }}
      🚨 *{{ .Labels.alertname }}*
      *Instance:* {{ .Labels.instance }}
      *Severity:* {{ .Labels.severity }}
      *Description:* {{ .Annotations.description }}
      {{ end }}

- name: 'warning-alerts'
  email_configs:
  - to: 'dev-team@example.com'
    subject: '[WARNING] RabbitMQ Alert - {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Instance: {{ .Labels.instance }}
      Severity: {{ .Labels.severity }}
      {{ end }}
```

### 2. 智能告警

```python
import time
from datetime import datetime, timedelta
from typing import Dict, List

class SmartAlertManager:
    """智能告警管理器"""
    
    def __init__(self):
        self.alert_history = defaultdict(list)
        self.suppression_windows = defaultdict(lambda: timedelta(minutes=5))
        
    def should_send_alert(self, alert_name: str, instance: str, 
                         severity: str, value: float) -> bool:
        """判断是否应该发送告警"""
        key = f"{alert_name}:{instance}"
        current_time = datetime.now()
        
        # 获取历史记录
        history = self.alert_history[key]
        
        # 检查是否在最近发送过告警
        if history:
            last_alert = history[-1]
            time_since_last = current_time - last_alert['timestamp']
            
            # 如果在抑制窗口内，不发送告警
            if time_since_last < self.suppression_windows[key]:
                return False
                
            # 检查是否是重复告警
            if self._is_duplicate_alert(last_alert, value):
                return False
                
            # 检查是否是误报
            if self._is_false_positive(alert_name, instance, value):
                return False
                
        return True
        
    def _is_duplicate_alert(self, last_alert: Dict, current_value: float) -> bool:
        """检查是否是重复告警"""
        # 如果值变化不大，认为是重复告警
        threshold = 0.1  # 10%的变化阈值
        value_diff = abs(current_value - last_alert['value']) / last_alert['value']
        return value_diff < threshold
        
    def _is_false_positive(self, alert_name: str, instance: str, value: float) -> bool:
        """检查是否是误报"""
        # 检查历史趋势
        key = f"{alert_name}:{instance}"
        history = self.alert_history[key]
        
        if len(history) < 3:
            return False  # 数据不足，不认为是误报
            
        # 检查是否是瞬时峰值
        recent_values = [h['value'] for h in history[-3:]]
        avg_value = sum(recent_values) / len(recent_values)
        
        # 如果当前值远高于平均值，可能是瞬时峰值
        if value > avg_value * 2:
            return True
            
        return False
        
    def record_alert(self, alert_name: str, instance: str, 
                    severity: str, value: float):
        """记录告警"""
        key = f"{alert_name}:{instance}"
        self.alert_history[key].append({
            'timestamp': datetime.now(),
            'severity': severity,
            'value': value
        })
        
        # 保持历史记录长度
        if len(self.alert_history[key]) > 100:
            self.alert_history[key] = self.alert_history[key][-100:]
```

## 🔧 运维自动化

### 1. 自动扩缩容

```python
import docker
import kubernetes
from kubernetes import client, config

class AutoScaler:
    """自动扩缩容管理器"""
    
    def __init__(self, rabbitmq_api_url: str, k8s_config: str = None):
        self.rabbitmq_api_url = rabbitmq_api_url
        
        if k8s_config:
            config.load_kube_config(config_file=k8s_config)
        else:
            config.load_incluster_config()
            
        self.v1 = client.AppsV1Api()
        self.metrics_client = client.CustomObjectsApi()
        
    def check_scaling_conditions(self, deployment_name: str, namespace: str) -> Dict:
        """检查扩缩容条件"""
        conditions = {
            'should_scale_up': False,
            'should_scale_down': False,
            'reason': '',
            'metrics': {}
        }
        
        # 获取RabbitMQ指标
        metrics = self._get_rabbitmq_metrics()
        conditions['metrics'] = metrics
        
        # 获取当前副本数
        current_replicas = self._get_current_replicas(deployment_name, namespace)
        
        # 检查扩容条件
        if self._should_scale_up(metrics, current_replicas):
            conditions['should_scale_up'] = True
            conditions['reason'] = f"High load detected: {metrics['queue_depth']} messages, {metrics['connection_count']} connections"
            
        # 检查缩容条件
        elif self._should_scale_down(metrics, current_replicas):
            conditions['should_scale_down'] = True
            conditions['reason'] = f"Low load detected: {metrics['queue_depth']} messages, {metrics['connection_count']} connections"
            
        return conditions
        
    def _get_rabbitmq_metrics(self) -> Dict:
        """获取RabbitMQ指标"""
        try:
            # 这里应该调用RabbitMQ API获取指标
            # 简化实现，返回模拟数据
            return {
                'queue_depth': 15000,  # 队列深度
                'connection_count': 500,  # 连接数
                'message_rate': 1000,  # 消息速率
                'error_rate': 0.01  # 错误率
            }
        except Exception as e:
            logging.error(f"获取RabbitMQ指标失败: {e}")
            return {}
            
    def _should_scale_up(self, metrics: Dict, current_replicas: int) -> bool:
        """判断是否应该扩容"""
        # 扩容条件
        scale_up_conditions = [
            metrics.get('queue_depth', 0) > 10000,  # 队列深度超过10000
            metrics.get('connection_count', 0) > 1000,  # 连接数超过1000
            metrics.get('message_rate', 0) > 2000,  # 消息速率超过2000/s
            metrics.get('error_rate', 0) > 0.05  # 错误率超过5%
        ]
        
        # 至少满足2个条件才扩容
        satisfied_conditions = sum(scale_up_conditions)
        max_replicas = 10
        
        return satisfied_conditions >= 2 and current_replicas < max_replicas
        
    def _should_scale_down(self, metrics: Dict, current_replicas: int) -> bool:
        """判断是否应该缩容"""
        # 缩容条件
        scale_down_conditions = [
            metrics.get('queue_depth', 0) < 100,  # 队列深度小于100
            metrics.get('connection_count', 0) < 10,  # 连接数小于10
            metrics.get('message_rate', 0) < 100,  # 消息速率小于100/s
            metrics.get('error_rate', 0) < 0.001  # 错误率小于0.1%
        ]
        
        # 所有条件都满足才缩容
        satisfied_conditions = sum(scale_down_conditions)
        min_replicas = 2
        
        return satisfied_conditions >= 3 and current_replicas > min_replicas
        
    def scale_deployment(self, deployment_name: str, namespace: str, replicas: int) -> bool:
        """扩缩容部署"""
        try:
            # 获取当前部署
            deployment = self.v1.read_namespaced_deployment(deployment_name, namespace)
            
            # 更新副本数
            deployment.spec.replicas = replicas
            
            # 应用更新
            self.v1.patch_namespaced_deployment(
                deployment_name, 
                namespace, 
                deployment
            )
            
            logging.info(f"成功将 {deployment_name} 扩缩容到 {replicas} 副本")
            return True
            
        except Exception as e:
            logging.error(f"扩缩容失败: {e}")
            return False
```

### 2. 自动故障恢复

```python
import time
import docker
from datetime import datetime, timedelta

class AutoRecovery:
    """自动故障恢复管理器"""
    
    def __init__(self, rabbitmq_api_url: str, max_restart_attempts: int = 3):
        self.rabbitmq_api_url = rabbitmq_api_url
        self.max_restart_attempts = max_restart_attempts
        self.restart_history = defaultdict(list)
        self.docker_client = docker.from_env()
        
    def check_health_and_recover(self, container_name: str) -> bool:
        """检查健康状态并执行恢复"""
        try:
            # 获取容器状态
            container = self.docker_client.containers.get(container_name)
            
            # 检查容器状态
            if container.status != 'running':
                return self._restart_container(container_name)
                
            # 检查RabbitMQ健康状态
            if not self._check_rabbitmq_health():
                return self._restart_container(container_name)
                
            # 检查集群状态
            if not self._check_cluster_health():
                return self._repair_cluster()
                
            return True
            
        except Exception as e:
            logging.error(f"健康检查和恢复失败: {e}")
            return False
            
    def _check_rabbitmq_health(self) -> bool:
        """检查RabbitMQ健康状态"""
        try:
            # 这里应该调用RabbitMQ健康检查API
            # 简化实现
            return True
        except Exception as e:
            logging.error(f"RabbitMQ健康检查失败: {e}")
            return False
            
    def _check_cluster_health(self) -> bool:
        """检查集群健康状态"""
        try:
            # 这里应该检查集群状态
            # 简化实现
            return True
        except Exception as e:
            logging.error(f"集群健康检查失败: {e}")
            return False
            
    def _restart_container(self, container_name: str) -> bool:
        """重启容器"""
        try:
            # 检查重启次数
            key = container_name
            current_time = datetime.now()
            
            # 清理过期记录（24小时前）
            self.restart_history[key] = [
                restart_time for restart_time in self.restart_history[key]
                if current_time - restart_time < timedelta(hours=24)
            ]
            
            # 检查重启次数限制
            if len(self.restart_history[key]) >= self.max_restart_attempts:
                logging.warning(f"容器 {container_name} 重启次数过多，跳过重启")
                return False
                
            # 重启容器
            container = self.docker_client.containers.get(container_name)
            container.restart()
            
            # 记录重启时间
            self.restart_history[key].append(current_time)
            
            logging.info(f"成功重启容器: {container_name}")
            return True
            
        except Exception as e:
            logging.error(f"重启容器失败: {e}")
            return False
            
    def _repair_cluster(self) -> bool:
        """修复集群"""
        try:
            # 这里应该实现集群修复逻辑
            # 简化实现
            logging.info("集群修复完成")
            return True
        except Exception as e:
            logging.error(f"集群修复失败: {e}")
            return False
```

## 📊 容量规划

### 1. 容量评估

```python
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np

class CapacityPlanner:
    """容量规划器"""
    
    def __init__(self, rabbitmq_api_url: str, historical_data_days: int = 30):
        self.rabbitmq_api_url = rabbitmq_api_url
        self.historical_data_days = historical_data_days
        self.capacity_data = []
        
    def analyze_current_capacity(self) -> Dict:
        """分析当前容量"""
        current_metrics = self._get_current_metrics()
        
        capacity_analysis = {
            'timestamp': datetime.now().isoformat(),
            'current_utilization': self._calculate_utilization(current_metrics),
            'capacity_remaining': self._calculate_remaining_capacity(current_metrics),
            'bottlenecks': self._identify_bottlenecks(current_metrics),
            'recommendations': self._generate_recommendations(current_metrics)
        }
        
        return capacity_analysis
        
    def predict_future_capacity(self, forecast_days: int = 30) -> Dict:
        """预测未来容量需求"""
        # 获取历史数据
        historical_data = self._get_historical_metrics(self.historical_data_days)
        
        # 使用简单线性回归预测
        predictions = self._linear_forecast(historical_data, forecast_days)
        
        return {
            'forecast_period_days': forecast_days,
            'predicted_metrics': predictions,
            'capacity_warnings': self._generate_capacity_warnings(predictions),
            'scaling_recommendations': self._generate_scaling_recommendations(predictions)
        }
        
    def _get_current_metrics(self) -> Dict:
        """获取当前指标"""
        # 这里应该调用RabbitMQ API获取指标
        # 简化实现
        return {
            'connection_count': 500,
            'queue_count': 100,
            'message_rate': 1000,
            'memory_usage': 2.5,  # GB
            'disk_usage': 10.0,  # GB
            'cpu_usage': 45.0  # percentage
        }
        
    def _calculate_utilization(self, metrics: Dict) -> Dict:
        """计算利用率"""
        # 基于经验阈值计算利用率
        utilization = {
            'connection_utilization': min(metrics['connection_count'] / 1000 * 100, 100),
            'queue_utilization': min(metrics['queue_count'] / 500 * 100, 100),
            'message_rate_utilization': min(metrics['message_rate'] / 5000 * 100, 100),
            'memory_utilization': min(metrics['memory_usage'] / 4.0 * 100, 100),
            'disk_utilization': min(metrics['disk_usage'] / 50.0 * 100, 100),
            'cpu_utilization': metrics['cpu_usage']
        }
        
        # 计算总体利用率
        utilization['overall_utilization'] = np.mean([
            utilization['connection_utilization'],
            utilization['queue_utilization'],
            utilization['message_rate_utilization'],
            utilization['memory_utilization'],
            utilization['disk_utilization'],
            utilization['cpu_utilization']
        ])
        
        return utilization
        
    def _identify_bottlenecks(self, metrics: Dict) -> List[str]:
        """识别瓶颈"""
        bottlenecks = []
        
        # 检查各种瓶颈条件
        if metrics['connection_count'] > 800:
            bottlenecks.append('High connection count')
        if metrics['queue_count'] > 400:
            bottlenecks.append('High queue count')
        if metrics['message_rate'] > 4000:
            bottlenecks.append('High message rate')
        if metrics['memory_usage'] > 3.2:
            bottlenecks.append('High memory usage')
        if metrics['disk_usage'] > 40:
            bottlenecks.append('High disk usage')
        if metrics['cpu_usage'] > 80:
            bottlenecks.append('High CPU usage')
            
        return bottlenecks
        
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于指标生成建议
        if metrics['connection_count'] > 800:
            recommendations.append('Consider connection pooling or load balancing')
        if metrics['queue_count'] > 400:
            recommendations.append('Consider queue consolidation or partitioning')
        if metrics['message_rate'] > 4000:
            recommendations.append('Consider message batching or rate limiting')
        if metrics['memory_usage'] > 3.2:
            recommendations.append('Consider memory optimization or scaling')
        if metrics['disk_usage'] > 40:
            recommendations.append('Consider disk cleanup or scaling')
        if metrics['cpu_usage'] > 80:
            recommendations.append('Consider CPU optimization or scaling')
            
        return recommendations
```

### 2. 资源优化建议

```python
class ResourceOptimizer:
    """资源优化器"""
    
    def __init__(self, rabbitmq_api_url: str):
        self.rabbitmq_api_url = rabbitmq_api_url
        
    def analyze_memory_usage(self) -> Dict:
        """分析内存使用"""
        # 获取内存使用统计
        memory_stats = self._get_memory_stats()
        
        optimization_suggestions = {
            'current_memory_usage': memory_stats,
            'memory_optimization_suggestions': self._generate_memory_suggestions(memory_stats),
            'queue_memory_analysis': self._analyze_queue_memory(memory_stats),
            'connection_memory_analysis': self._analyze_connection_memory(memory_stats)
        }
        
        return optimization_suggestions
        
    def analyze_disk_usage(self) -> Dict:
        """分析磁盘使用"""
        disk_stats = self._get_disk_stats()
        
        optimization_suggestions = {
            'current_disk_usage': disk_stats,
            'disk_optimization_suggestions': self._generate_disk_suggestions(disk_stats),
            'log_file_analysis': self._analyze_log_files(disk_stats),
            'message_persistence_analysis': self._analyze_message_persistence(disk_stats)
        }
        
        return optimization_suggestions
        
    def _generate_memory_suggestions(self, stats: Dict) -> List[str]:
        """生成内存优化建议"""
        suggestions = []
        
        # 基于内存统计生成建议
        if stats.get('queue_memory', 0) > 1024 * 1024 * 1024:  # 1GB
            suggestions.append('Consider reducing queue memory usage')
        if stats.get('connection_memory', 0) > 512 * 1024 * 1024:  # 512MB
            suggestions.append('Consider reducing connection memory usage')
        if stats.get('message_memory', 0) > 2 * 1024 * 1024 * 1024:  # 2GB
            suggestions.append('Consider reducing message memory usage')
            
        return suggestions
        
    def _generate_disk_suggestions(self, stats: Dict) -> List[str]:
        """生成磁盘优化建议"""
        suggestions = []
        
        # 基于磁盘统计生成建议
        if stats.get('log_size', 0) > 10 * 1024 * 1024 * 1024:  # 10GB
            suggestions.append('Consider log rotation and cleanup')
        if stats.get('message_store_size', 0) > 50 * 1024 * 1024 * 1024:  # 50GB
            suggestions.append('Consider message store cleanup')
        if stats.get('queue_index_size', 0) > 5 * 1024 * 1024 * 1024:  # 5GB
            suggestions.append('Consider queue index optimization')
            
        return suggestions
```

## 🎯 最佳实践总结

### 1. 监控策略

1. **分层监控**: 系统层、容器层、应用层、业务层
2. **关键指标**: 连接数、队列深度、消息速率、资源使用率
3. **实时监控**: 实时数据采集和告警
4. **历史分析**: 趋势分析和容量规划

### 2. 告警策略

1. **分级告警**: 根据严重程度分级处理
2. **智能抑制**: 避免重复和误报告警
3. **多渠道通知**: 邮件、短信、Slack等
4. **自动响应**: 自动故障恢复和扩缩容

### 3. 运维自动化

1. **自动化部署**: CI/CD集成
2. **自动监控**: 监控工具自动配置
3. **自动恢复**: 故障自动检测和恢复
4. **自动优化**: 性能自动调优

### 4. 容量规划

1. **定期评估**: 定期容量评估和预测
2. **弹性扩展**: 基于负载的自动扩缩容
3. **资源优化**: 持续的资源优化建议
4. **成本控制**: 平衡性能和成本的优化

通过完善的监控与运维体系，可以确保RabbitMQ集群的稳定运行，及时发现和解决问题，提高系统的可靠性和可用性。