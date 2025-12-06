# 第17章：RabbitMQ监控与运维

## 监控概述

在生产环境中，RabbitMQ作为关键的消息中间件，其稳定性和性能直接影响整个系统的运行状况。本章将详细介绍RabbitMQ的监控体系、运维管理、故障处理和性能优化等核心内容。

## 监控基础概念

### 监控的目标
- **可用性监控**：确保RabbitMQ服务始终可用
- **性能监控**：跟踪消息处理性能和系统资源使用
- **安全性监控**：监控安全事件和异常访问
- **容量规划**：基于历史数据预测容量需求
- **故障诊断**：快速定位和解决性能问题

### 监控层次结构
```
系统层监控
├── 主机层监控
│   ├── CPU使用率
│   ├── 内存使用情况
│   ├── 磁盘I/O
│   └── 网络流量
├── RabbitMQ层监控
│   ├── 队列指标
│   ├── 交换机指标
│   ├── 连接和通道指标
│   └── 集群健康状态
└── 应用层监控
    ├── 消息处理延迟
    ├── 消息吞吐量
    ├── 错误率和重试次数
    └── 业务指标
```

## RabbitMQ监控指标

### 核心性能指标

#### 1. 消息队列指标
- **队列长度**：`queue.length`
- **消息总数**：`queue.messages`
- **消费者数量**：`queue.consumers`
- **消息入队速率**：`queue.message_in.rate`
- **消息出队速率**：`queue.message_out.rate`

#### 2. 连接和通道指标
- **连接数**：`connection.count`
- **通道数**：`channel.count`
- **连接使用率**：`connection.utilisation`
- **通道平均寿命**：`channel.open.rate`

#### 3. 交换机和绑定指标
- **交换机数量**：`exchange.count`
- **绑定关系**：`exchange.bindings.rate`
- **路由消息数**：`exchange.message_in.rate`

#### 4. 系统资源指标
- **内存使用率**：`node.memory_used`
- **磁盘使用率**：`node.disk_free`
- **Erlang进程数**：`node.processes`
- **文件描述符**：`node.fd_used`

### 监控数据结构

```python
# 监控数据结构示例
metrics_data = {
    "timestamp": "2024-01-15T10:30:00Z",
    "cluster": {
        "name": "rabbitmq-cluster-01",
        "nodes": [
            {
                "name": "rabbit@node1",
                "status": "running",
                "memory": {
                    "used": 1024 * 1024 * 512,  # 512MB
                    "limit": 1024 * 1024 * 2048,  # 2GB
                    "pct": 25.0
                },
                "disk": {
                    "free": 1024 * 1024 * 1024 * 50,  # 50GB
                    "limit": 1024 * 1024 * 1024 * 5,  # 5GB
                    "pct": 90.0
                }
            }
        ]
    },
    "queues": [
        {
            "name": "orders",
            "vhost": "/",
            "messages": 1500,
            "durable": True,
            "consumers": 5,
            "memory": 1024 * 1024 * 64,  # 64MB
            "rates": {
                "in": 100.0,  # msg/s
                "out": 95.0
            }
        }
    ],
    "connections": [
        {
            "address": "192.168.1.100:54321",
            "user": "app_user",
            "state": "running",
            "channels": 10,
            "connected_at": "2024-01-15T09:00:00Z"
        }
    ]
}
```

## 监控实现方案

### 1. Prometheus + Grafana监控

#### Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['node1:15692', 'node2:15692', 'node3:15692']
    scrape_interval: 15s
    metrics_path: '/metrics'
    basic_auth:
      username: 'monitoring'
      password: 'monitor_password'
```

#### Grafana仪表板配置
```json
{
  "dashboard": {
    "title": "RabbitMQ监控仪表板",
    "panels": [
      {
        "title": "队列消息数量",
        "type": "graph",
        "targets": [
          {
            "expr": "rabbitmq_queue_messages",
            "legendFormat": "{{queue_name}}"
          }
        ]
      },
      {
        "title": "消息处理速率",
        "type": "graph",
        "targets": [
          {
            "expr": "rabbitmq_queue_message_in",
            "legendFormat": "入队: {{queue_name}}"
          },
          {
            "expr": "rabbitmq_queue_message_out",
            "legendFormat": "出队: {{queue_name}}"
          }
        ]
      }
    ]
  }
}
```

### 2. 自定义监控脚本

#### Python监控脚本
```python
import pika
import json
import time
import requests
from datetime import datetime

class RabbitMQMonitor:
    def __init__(self, username, password, api_url):
        self.username = username
        self.password = password
        self.api_url = api_url
        self.metrics = {}
    
    def collect_cluster_metrics(self):
        """收集集群级指标"""
        try:
            response = requests.get(
                f"{self.api_url}/api/overview",
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.metrics['cluster'] = {
                    'timestamp': datetime.now().isoformat(),
                    'rabbitmq_version': data.get('rabbitmq_version'),
                    'management_version': data.get('management_version'),
                    'total_connections': data.get('connection_totals', {}).get('current', 0),
                    'total_channels': data.get('channel_totals', {}).get('current', 0),
                    'total_queues': data.get('queue_totals', {}).get('messages', 0),
                    'total_messages': data.get('queue_totals', {}).get('messages', 0)
                }
                return True
        except Exception as e:
            print(f"收集集群指标失败: {e}")
            return False
    
    def collect_queue_metrics(self):
        """收集队列级指标"""
        try:
            response = requests.get(
                f"{self.api_url}/api/queues",
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code == 200:
                queues = []
                for queue_data in response.json():
                    queues.append({
                        'name': queue_data['name'],
                        'vhost': queue_data['vhost'],
                        'durable': queue_data['durable'],
                        'messages': queue_data['messages'],
                        'consumers': len(queue_data.get('consumer_details', [])),
                        'memory': queue_data.get('memory', 0),
                        'message_stats': queue_data.get('message_stats', {})
                    })
                
                self.metrics['queues'] = queues
                return True
        except Exception as e:
            print(f"收集队列指标失败: {e}")
            return False
    
    def collect_connection_metrics(self):
        """收集连接级指标"""
        try:
            response = requests.get(
                f"{self.api_url}/api/connections",
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code == 200:
                connections = []
                for conn_data in response.json():
                    connections.append({
                        'address': conn_data['address'],
                        'user': conn_data['user'],
                        'state': conn_data['state'],
                        'channels': conn_data.get('channels', 0),
                        'connected_at': conn_data.get('connected_at', ''),
                        'client_properties': conn_data.get('client_properties', {})
                    })
                
                self.metrics['connections'] = connections
                return True
        except Exception as e:
            print(f"收集连接指标失败: {e}")
            return False
    
    def check_alerts(self):
        """检查告警条件"""
        alerts = []
        
        # 检查内存使用率
        cluster = self.metrics.get('cluster', {})
        if cluster:
            # 假设从某个API获取内存使用率
            memory_usage = self.get_memory_usage()
            if memory_usage > 85:
                alerts.append({
                    'level': 'warning',
                    'type': 'memory',
                    'message': f'内存使用率过高: {memory_usage}%'
                })
        
        # 检查队列积压
        queues = self.metrics.get('queues', [])
        for queue in queues:
            if queue['messages'] > 10000:
                alerts.append({
                    'level': 'warning',
                    'type': 'queue_backlog',
                    'queue': queue['name'],
                    'message': f'队列 {queue["name"]} 消息积压严重: {queue["messages"]} 条'
                })
        
        # 检查无消费者的队列
        for queue in queues:
            if queue['messages'] > 0 and queue['consumers'] == 0:
                alerts.append({
                    'level': 'critical',
                    'type': 'no_consumer',
                    'queue': queue['name'],
                    'message': f'队列 {queue["name"]} 有消息但无消费者'
                })
        
        self.metrics['alerts'] = alerts
        return alerts
    
    def get_memory_usage(self):
        """获取内存使用率"""
        # 这里应该从系统监控获取实际内存使用率
        # 暂时返回模拟数据
        return 75.5
    
    def generate_report(self):
        """生成监控报告"""
        self.collect_cluster_metrics()
        self.collect_queue_metrics()
        self.collect_connection_metrics()
        alerts = self.check_alerts()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_connections': len(self.metrics.get('connections', [])),
                'total_queues': len(self.metrics.get('queues', [])),
                'total_messages': sum(q['messages'] for q in self.metrics.get('queues', [])),
                'critical_alerts': len([a for a in alerts if a['level'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['level'] == 'warning'])
            },
            'details': self.metrics
        }
        
        return report
    
    def save_metrics(self, filename):
        """保存指标到文件"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"监控报告已保存到: {filename}")

# 使用示例
if __name__ == "__main__":
    monitor = RabbitMQMonitor(
        username="monitor",
        password="password",
        api_url="http://node1.example.com:15672"
    )
    
    # 生成监控报告
    report = monitor.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 保存到文件
    monitor.save_metrics("rabbitmq_metrics.json")
```

## 日志管理

### 日志配置

#### 系统日志配置
```ini
# /etc/rabbitmq/rabbitmq.conf
log.file = /var/log/rabbitmq/rabbit.log
log.level = info
log.console = true
log.console.level = info
log.default_file = rabbitmq_default.log
log.default_file.level = debug
log.connection = rabbitmq_connection.log
log.connection.level = info
log.channel = rabbitmq_channel.log
log.channel.level = info
log.queue = rabbitmq_queue.log
log.queue.level = info
log.mirroring = rabbitmq_mirroring.log
log.mirroring.level = info
```

#### 日志轮转配置
```bash
# /etc/logrotate.d/rabbitmq-server
/var/log/rabbitmq/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 rabbitmq rabbitmq
    postrotate
        rabbitmqctl rotate_logs
    endscript
}
```

### 日志分析脚本

```python
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict

class RabbitMQLogAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.log_patterns = {
            'connection_errors': re.compile(r'connection_closed.*(Connection|(refused|closed))', re.I),
            'queue_errors': re.compile(r'queue.*(error|failed|crash)', re.I),
            'memory_warnings': re.compile(r'memory.*(high|warning|usage)', re.I),
            'performance_issues': re.compile(r'(slow|timeout|blocked|restart)', re.I)
        }
    
    def parse_log_entries(self, hours=24):
        """解析日志条目"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        parsed_logs = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = self._parse_single_line(line)
                    if log_entry and log_entry['timestamp'] > cutoff_time:
                        parsed_logs.append(log_entry)
        
        except FileNotFoundError:
            print(f"日志文件未找到: {self.log_file}")
        except Exception as e:
            print(f"解析日志文件失败: {e}")
        
        return parsed_logs
    
    def _parse_single_line(self, line):
        """解析单行日志"""
        # 提取时间戳
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})', line)
        if not timestamp_match:
            return None
        
        try:
            timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
        
        # 提取日志级别
        level_match = re.search(r'\s(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s', line)
        level = level_match.group(1) if level_match else 'UNKNOWN'
        
        # 提取进程ID
        pid_match = re.search(r'<(\d+\.\d+)>', line)
        pid = pid_match.group(1) if pid_match else None
        
        return {
            'timestamp': timestamp,
            'level': level,
            'pid': pid,
            'raw_line': line.strip()
        }
    
    def categorize_logs(self, log_entries):
        """对日志进行分类"""
        categories = defaultdict(list)
        
        for entry in log_entries:
            line = entry['raw_line']
            
            for category, pattern in self.log_patterns.items():
                if pattern.search(line):
                    categories[category].append(entry)
                    break
            else:
                categories['other'].append(entry)
        
        return dict(categories)
    
    def analyze_errors(self, log_entries):
        """分析错误信息"""
        error_analysis = {
            'total_errors': 0,
            'error_by_level': defaultdict(int),
            'error_by_pattern': defaultdict(int),
            'time_distribution': defaultdict(int),
            'top_errors': []
        }
        
        for entry in log_entries:
            if entry['level'] in ['ERROR', 'CRITICAL']:
                error_analysis['total_errors'] += 1
                error_analysis['error_by_level'][entry['level']] += 1
                
                # 时间分布分析
                hour = entry['timestamp'].hour
                error_analysis['time_distribution'][hour] += 1
                
                # 错误模式分析
                line = entry['raw_line']
                for pattern_name, pattern in self.log_patterns.items():
                    if pattern.search(line):
                        error_analysis['error_by_pattern'][pattern_name] += 1
                        break
        
        # 获取最频繁的错误
        error_counts = defaultdict(int)
        for entry in log_entries:
            if entry['level'] in ['ERROR', 'CRITICAL']:
                # 提取错误关键词
                error_msg = entry['raw_line'][:100]  # 取前100字符作为摘要
                error_counts[error_msg] += 1
        
        # 排序并取前10
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        error_analysis['top_errors'] = sorted_errors
        
        return error_analysis
    
    def generate_summary_report(self, log_entries):
        """生成摘要报告"""
        if not log_entries:
            return "没有找到日志条目"
        
        # 按类型分类
        categorized = self.categorize_logs(log_entries)
        error_analysis = self.analyze_errors([e for e in log_entries if e['level'] in ['ERROR', 'CRITICAL']])
        
        # 生成报告
        report = f"""
=== RabbitMQ 日志分析报告 ===
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
日志条目总数: {len(log_entries)}
时间范围: {log_entries[-1]['timestamp']} 到 {log_entries[0]['timestamp']}

=== 按级别统计 ===
"""
        level_counts = defaultdict(int)
        for entry in log_entries:
            level_counts[entry['level']] += 1
        
        for level, count in level_counts.items():
            report += f"{level}: {count}\n"
        
        report += f"""
=== 按类型分类 ===
"""
        for category, entries in categorized.items():
            report += f"{category}: {len(entries)}\n"
        
        report += f"""
=== 错误分析 ===
错误总数: {error_analysis['total_errors']}
"""
        for level, count in error_analysis['error_by_level'].items():
            report += f"{level}: {count}\n"
        
        report += "\n=== 最频繁的错误 ===\n"
        for error_msg, count in error_analysis['top_errors']:
            report += f"({count}次) {error_msg[:80]}...\n"
        
        return report
    
    def export_detailed_report(self, log_entries, output_file):
        """导出详细报告"""
        categorized = self.categorize_logs(log_entries)
        error_analysis = self.analyze_errors([e for e in log_entries if e['level'] in ['ERROR', 'CRITICAL']])
        
        detailed_report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_entries': len(log_entries),
            'time_range': {
                'start': log_entries[-1]['timestamp'].isoformat() if log_entries else None,
                'end': log_entries[0]['timestamp'].isoformat() if log_entries else None
            },
            'categorized_logs': {
                category: [self._serialize_log_entry(entry) for entry in entries]
                for category, entries in categorized.items()
            },
            'error_analysis': error_analysis,
            'level_distribution': dict(defaultdict(int)),
            'time_distribution': dict(error_analysis.get('time_distribution', {}))
        }
        
        # 计算级别分布
        for entry in log_entries:
            detailed_report['level_distribution'][entry['level']] += 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"详细报告已导出到: {output_file}")
    
    def _serialize_log_entry(self, entry):
        """序列化日志条目"""
        return {
            'timestamp': entry['timestamp'].isoformat(),
            'level': entry['level'],
            'pid': entry['pid'],
            'raw_line': entry['raw_line']
        }

# 使用示例
if __name__ == "__main__":
    analyzer = RabbitMQLogAnalyzer('/var/log/rabbitmq/rabbit.log')
    
    # 解析最近24小时的日志
    log_entries = analyzer.parse_log_entries(hours=24)
    
    # 生成摘要报告
    summary = analyzer.generate_summary_report(log_entries)
    print(summary)
    
    # 导出详细报告
    analyzer.export_detailed_report(log_entries, 'rabbitmq_log_analysis.json')
```

## 性能基准测试

### 基准测试工具

```python
import pika
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import json
from typing import List, Dict, Tuple

class RabbitMQBenchmark:
    def __init__(self, host='localhost', port=5672, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.results = {
            'producer_stats': [],
            'consumer_stats': [],
            'latency_stats': [],
            'throughput_stats': {}
        }
    
    def setup_connection(self):
        """建立连接"""
        if self.username and self.password:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
        else:
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port
            )
        
        return pika.BlockingConnection(parameters)
    
    def benchmark_producer(self, queue_name: str, message_count: int, 
                          message_size: int = 1024, threads: int = 1):
        """基准测试生产者性能"""
        message = b'x' * message_size
        
        def producer_worker(worker_id: int, messages_per_thread: int):
            """生产者工作线程"""
            try:
                connection = self.setup_connection()
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=True)
                
                send_times = []
                successful_sends = 0
                
                for i in range(messages_per_thread):
                    start_time = time.time()
                    
                    try:
                        channel.basic_publish(
                            exchange='',
                            routing_key=queue_name,
                            body=message,
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # 持久化
                            )
                        )
                        
                        end_time = time.time()
                        latency = (end_time - start_time) * 1000  # 转换为毫秒
                        send_times.append(latency)
                        successful_sends += 1
                        
                    except Exception as e:
                        print(f"Worker {worker_id} 发送消息失败: {e}")
                
                connection.close()
                
                return {
                    'worker_id': worker_id,
                    'messages_sent': successful_sends,
                    'avg_latency': statistics.mean(send_times) if send_times else 0,
                    'min_latency': min(send_times) if send_times else 0,
                    'max_latency': max(send_times) if send_times else 0,
                    'total_time': time.time() - start_time
                }
                
            except Exception as e:
                print(f"Worker {worker_id} 异常: {e}")
                return None
        
        # 计算每个线程发送的消息数
        messages_per_thread = message_count // threads
        remaining_messages = message_count % threads
        
        print(f"开始生产者基准测试...")
        print(f"队列: {queue_name}")
        print(f"总消息数: {message_count}")
        print(f"消息大小: {message_size} bytes")
        print(f"线程数: {threads}")
        print(f"每线程消息数: {messages_per_thread}")
        
        start_time = time.time()
        
        # 使用线程池执行测试
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            
            for i in range(threads):
                msg_count = messages_per_thread + (1 if i < remaining_messages else 0)
                future = executor.submit(producer_worker, i, msg_count)
                futures.append(future)
            
            worker_results = []
            for future in as_completed(futures):
                result = future.result()
                if result:
                    worker_results.append(result)
        
        total_time = time.time() - start_time
        
        # 计算总体统计
        total_sent = sum(r['messages_sent'] for r in worker_results)
        all_latencies = []
        for r in worker_results:
            # 假设平均延迟代表该worker的延迟分布
            all_latencies.extend([r['avg_latency']] * r['messages_sent'])
        
        summary = {
            'test_duration': total_time,
            'total_messages_sent': total_sent,
            'throughput_msg_per_sec': total_sent / total_time,
            'throughput_bytes_per_sec': (total_sent * message_size) / total_time,
            'avg_latency': statistics.mean(all_latencies) if all_latencies else 0,
            'min_latency': min(all_latencies) if all_latencies else 0,
            'max_latency': max(all_latencies) if all_latencies else 0,
            'worker_results': worker_results
        }
        
        self.results['producer_stats'].append(summary)
        
        print(f"生产者基准测试完成:")
        print(f"总耗时: {total_time:.2f}s")
        print(f"发送消息数: {total_sent}")
        print(f"吞吐量: {summary['throughput_msg_per_sec']:.0f} msg/s")
        print(f"平均延迟: {summary['avg_latency']:.2f}ms")
        
        return summary
    
    def benchmark_consumer(self, queue_name: str, message_count: int, 
                          prefetch_count: int = 100, threads: int = 1):
        """基准测试消费者性能"""
        consumed_messages = queue.Queue()
        consumption_times = []
        
        def consumer_worker(worker_id: int):
            """消费者工作线程"""
            try:
                connection = self.setup_connection()
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=True)
                
                # 设置预取计数
                channel.basic_qos(prefetch_count=prefetch_count // threads)
                
                messages_processed = 0
                start_time = time.time()
                
                def callback(ch, method, properties, body):
                    nonlocal messages_processed
                    
                    try:
                        process_start_time = time.time()
                        
                        # 模拟消息处理
                        time.sleep(0.001)  # 1ms处理时间
                        
                        process_end_time = time.time()
                        processing_time = (process_end_time - process_start_time) * 1000
                        
                        consumption_times.append(processing_time)
                        consumed_messages.put(body)
                        messages_processed += 1
                        
                        # 手动确认
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
                    except Exception as e:
                        print(f"Worker {worker_id} 处理消息失败: {e}")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=callback,
                    auto_ack=False
                )
                
                print(f"Consumer worker {worker_id} 开始消费")
                
                # 消费消息直到达到目标数量
                while messages_processed < (message_count // threads):
                    try:
                        connection.process_data_events(time_limit=1)
                    except Exception as e:
                        print(f"Worker {worker_id} 处理事件失败: {e}")
                        break
                
                connection.close()
                
                return {
                    'worker_id': worker_id,
                    'messages_processed': messages_processed,
                    'processing_time': time.time() - start_time
                }
                
            except Exception as e:
                print(f"Consumer worker {worker_id} 异常: {e}")
                return None
        
        print(f"开始消费者基准测试...")
        print(f"队列: {queue_name}")
        print(f"目标消息数: {message_count}")
        print(f"预取数: {prefetch_count}")
        print(f"线程数: {threads}")
        
        start_time = time.time()
        
        # 启动消费者线程
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(consumer_worker, i) for i in range(threads)]
            
            # 等待所有消费者完成
            worker_results = []
            for future in as_completed(futures):
                result = future.result()
                if result:
                    worker_results.append(result)
        
        # 收集所有处理的消息
        total_processed = 0
        processing_stats = []
        
        while not consumed_messages.empty():
            try:
                consumed_messages.get_nowait()
                total_processed += 1
            except queue.Empty:
                break
        
        total_time = time.time() - start_time
        
        # 计算统计信息
        if consumption_times:
            summary = {
                'test_duration': total_time,
                'total_messages_processed': total_processed,
                'throughput_msg_per_sec': total_processed / total_time,
                'avg_processing_time': statistics.mean(consumption_times),
                'min_processing_time': min(consumption_times),
                'max_processing_time': max(consumption_times),
                'worker_results': worker_results
            }
        else:
            summary = {
                'test_duration': total_time,
                'total_messages_processed': total_processed,
                'throughput_msg_per_sec': total_processed / total_time,
                'error': '没有处理任何消息'
            }
        
        self.results['consumer_stats'].append(summary)
        
        print(f"消费者基准测试完成:")
        print(f"总耗时: {total_time:.2f}s")
        print(f"处理消息数: {total_processed}")
        print(f"吞吐量: {summary['throughput_msg_per_sec']:.0f} msg/s")
        if 'avg_processing_time' in summary:
            print(f"平均处理时间: {summary['avg_processing_time']:.2f}ms")
        
        return summary
    
    def benchmark_end_to_end(self, queue_name: str, message_count: int, 
                           message_size: int = 1024, threads: int = 1):
        """端到端基准测试"""
        print(f"开始端到端基准测试...")
        
        # 启动消费者
        consumer_future = None
        
        def run_consumer():
            return self.benchmark_consumer(queue_name, message_count, threads=threads)
        
        # 在后台启动消费者
        import concurrent.futures
        consumer_future = concurrent.futures.ThreadPoolExecutor().submit(run_consumer)
        
        # 等待一点时间确保消费者已就绪
        time.sleep(5)
        
        # 启动生产者
        producer_result = self.benchmark_producer(
            queue_name, message_count, message_size, threads
        )
        
        # 等待消费者完成
        consumer_result = consumer_future.result()
        
        # 计算端到端统计
        end_to_end_result = {
            'producer_result': producer_result,
            'consumer_result': consumer_result,
            'end_to_end_latency': producer_result.get('avg_latency', 0) + 
                                consumer_result.get('avg_processing_time', 0),
            'total_throughput': min(
                producer_result.get('throughput_msg_per_sec', 0),
                consumer_result.get('throughput_msg_per_sec', 0)
            )
        }
        
        self.results['throughput_stats']['end_to_end'] = end_to_end_result
        
        print(f"端到端基准测试完成:")
        print(f"端到端延迟: {end_to_end_result['end_to_end_latency']:.2f}ms")
        print(f"总吞吐量: {end_to_end_result['total_throughput']:.0f} msg/s")
        
        return end_to_end_result
    
    def run_comprehensive_benchmark(self):
        """运行综合基准测试"""
        print("=== RabbitMQ 基准测试 ===")
        
        test_scenarios = [
            {'message_count': 1000, 'message_size': 1024, 'threads': 1},
            {'message_count': 5000, 'message_size': 1024, 'threads': 5},
            {'message_count': 10000, 'message_size': 2048, 'threads': 10},
        ]
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n--- 测试场景 {i+1} ---")
            print(f"消息数: {scenario['message_count']}")
            print(f"消息大小: {scenario['message_size']} bytes")
            print(f"线程数: {scenario['threads']}")
            
            queue_name = f"benchmark_queue_{i+1}"
            
            try:
                # 清理现有队列（如果存在）
                connection = self.setup_connection()
                channel = connection.channel()
                try:
                    channel.queue_delete(queue=queue_name)
                except:
                    pass
                connection.close()
                
                # 运行端到端测试
                result = self.benchmark_end_to_end(
                    queue_name,
                    scenario['message_count'],
                    scenario['message_size'],
                    scenario['threads']
                )
                
                print(f"测试结果: {result}")
                
            except Exception as e:
                print(f"测试场景 {i+1} 失败: {e}")
        
        return self.results
    
    def save_results(self, filename):
        """保存基准测试结果"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"基准测试结果已保存到: {filename}")

# 使用示例
if __name__ == "__main__":
    benchmark = RabbitMQBenchmark(
        host='localhost',
        port=5672,
        username='guest',
        password='guest'
    )
    
    # 运行基准测试
    results = benchmark.run_comprehensive_benchmark()
    
    # 保存结果
    benchmark.save_results('rabbitmq_benchmark_results.json')
```

## 运维自动化

### 健康检查自动化

```python
import requests
import json
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import psutil

class AutomatedHealthMonitor:
    def __init__(self, config):
        self.config = config
        self.alert_rules = config.get('alert_rules', {})
        self.notification_settings = config.get('notifications', {})
        
    def check_cluster_health(self):
        """检查集群健康状态"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'nodes': [],
            'queues': [],
            'alerts': []
        }
        
        # 检查每个节点
        for node_config in self.config['nodes']:
            node_health = self.check_node_health(node_config)
            health_report['nodes'].append(node_health)
        
        # 检查队列状态
        queues_health = self.check_queues_health()
        health_report['queues'] = queues_health['queues']
        health_report['alerts'].extend(queues_health['alerts'])
        
        # 检查系统资源
        system_health = self.check_system_resources()
        health_report['system'] = system_health
        health_report['alerts'].extend(system_health.get('alerts', []))
        
        # 计算整体状态
        critical_alerts = [a for a in health_report['alerts'] if a['level'] == 'critical']
        warning_alerts = [a for a in health_report['alerts'] if a['level'] == 'warning']
        
        if critical_alerts:
            health_report['overall_status'] = 'critical'
        elif warning_alerts:
            health_report['overall_status'] = 'warning'
        else:
            health_report['overall_status'] = 'healthy'
        
        return health_report
    
    def check_node_health(self, node_config):
        """检查单个节点健康状态"""
        node_health = {
            'name': node_config['name'],
            'host': node_config['host'],
            'status': 'unknown',
            'api_response_time': 0,
            'connections': 0,
            'queues': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'alerts': []
        }
        
        try:
            api_url = f"http://{node_config['host']}:15672/api/overview"
            start_time = time.time()
            
            response = requests.get(
                api_url,
                auth=(node_config['username'], node_config['password']),
                timeout=10
            )
            
            node_health['api_response_time'] = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                node_health['status'] = 'healthy'
                node_health['connections'] = data.get('connection_totals', {}).get('current', 0)
                node_health['queues'] = data.get('queue_totals', {}).get('messages', 0)
            else:
                node_health['status'] = 'unhealthy'
                node_health['alerts'].append({
                    'level': 'critical',
                    'type': 'api_error',
                    'message': f"API响应错误: HTTP {response.status_code}"
                })
        
        except requests.exceptions.Timeout:
            node_health['status'] = 'timeout'
            node_health['alerts'].append({
                'level': 'critical',
                'type': 'timeout',
                'message': 'API请求超时'
            })
        except Exception as e:
            node_health['status'] = 'error'
            node_health['alerts'].append({
                'level': 'critical',
                'type': 'connection_error',
                'message': f'连接错误: {e}'
            })
        
        return node_health
    
    def check_queues_health(self):
        """检查队列健康状态"""
        result = {'queues': [], 'alerts': []}
        
        try:
            # 从第一个可用节点获取队列信息
            node_config = next((n for n in self.config['nodes'] if n.get('healthy', True)), None)
            if not node_config:
                result['alerts'].append({
                    'level': 'critical',
                    'type': 'no_healthy_nodes',
                    'message': '没有可用的健康节点'
                })
                return result
            
            api_url = f"http://{node_config['host']}:15672/api/queues"
            response = requests.get(
                api_url,
                auth=(node_config['username'], node_config['password']),
                timeout=10
            )
            
            if response.status_code == 200:
                queues_data = response.json()
                
                for queue_data in queues_data:
                    queue_health = {
                        'name': queue_data['name'],
                        'vhost': queue_data['vhost'],
                        'messages': queue_data['messages'],
                        'consumers': len(queue_data.get('consumer_details', [])),
                        'status': 'healthy',
                        'alerts': []
                    }
                    
                    # 检查消息积压
                    if queue_data['messages'] > self.alert_rules.get('queue_backlog_threshold', 10000):
                        queue_health['alerts'].append({
                            'level': 'warning',
                            'type': 'message_backlog',
                            'message': f'消息积压: {queue_data["messages"]}'
                        })
                    
                    # 检查无消费者
                    if queue_data['messages'] > 0 and queue_health['consumers'] == 0:
                        queue_health['alerts'].append({
                            'level': 'critical',
                            'type': 'no_consumer',
                            'message': '有消息但无消费者'
                        })
                        queue_health['status'] = 'critical'
                    
                    result['queues'].append(queue_health)
                    result['alerts'].extend(queue_health['alerts'])
        
        except Exception as e:
            result['alerts'].append({
                'level': 'critical',
                'type': 'queue_check_error',
                'message': f'检查队列状态失败: {e}'
            })
        
        return result
    
    def check_system_resources(self):
        """检查系统资源"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            result = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100,
                'alerts': []
            }
            
            # 检查CPU使用率
            if cpu_percent > self.alert_rules.get('cpu_threshold', 80):
                result['alerts'].append({
                    'level': 'warning',
                    'type': 'high_cpu',
                    'message': f'CPU使用率过高: {cpu_percent}%'
                })
            
            # 检查内存使用率
            if memory.percent > self.alert_rules.get('memory_threshold', 85):
                result['alerts'].append({
                    'level': 'warning',
                    'type': 'high_memory',
                    'message': f'内存使用率过高: {memory.percent}%'
                })
            
            # 检查磁盘使用率
            if (disk.used / disk.total) * 100 > self.alert_rules.get('disk_threshold', 90):
                result['alerts'].append({
                    'level': 'warning',
                    'type': 'high_disk',
                    'message': f'磁盘使用率过高: {(disk.used / disk.total) * 100:.1f}%'
                })
            
            return result
        
        except Exception as e:
            return {
                'error': str(e),
                'alerts': [{
                    'level': 'critical',
                    'type': 'system_check_error',
                    'message': f'检查系统资源失败: {e}'
                }]
            }
    
    def process_alerts(self, health_report):
        """处理告警"""
        alerts = health_report.get('alerts', [])
        
        # 过滤需要通知的告警
        notification_alerts = []
        for alert in alerts:
            if self.should_notify(alert):
                notification_alerts.append(alert)
        
        if notification_alerts:
            self.send_notifications(notification_alerts, health_report)
    
    def should_notify(self, alert):
        """判断是否需要发送通知"""
        notification_rules = self.notification_settings.get('rules', {})
        
        # 检查告警类型是否启用通知
        if alert['type'] not in notification_rules:
            return False
        
        rule = notification_rules[alert['type']]
        return rule.get('enabled', False) and alert['level'] in rule.get('levels', [])
    
    def send_notifications(self, alerts, health_report):
        """发送通知"""
        email_config = self.notification_settings.get('email', {})
        
        if email_config.get('enabled') and email_config.get('smtp_server'):
            self.send_email_notification(alerts, health_report)
        
        # 其他通知方式（Slack、微信等）可以在这里添加
        webhook_config = self.notification_settings.get('webhook', {})
        if webhook_config.get('enabled') and webhook_config.get('url'):
            self.send_webhook_notification(alerts, health_report)
    
    def send_email_notification(self, alerts, health_report):
        """发送邮件通知"""
        try:
            email_config = self.notification_settings['email']
            
            # 构建邮件内容
            subject = f"RabbitMQ告警 - {health_report['overall_status']}"
            
            body = f"""
RabbitMQ集群健康状态告警

时间: {health_report['timestamp']}
整体状态: {health_report['overall_status']}

告警详情:
"""
            
            for alert in alerts:
                body += f"- [{alert['level'].upper()}] {alert['message']}\n"
            
            body += f"""

集群节点状态:
"""
            for node in health_report.get('nodes', []):
                body += f"- {node['name']}: {node['status']}\n"
            
            # 发送邮件
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = email_config['from']
            msg['To'] = email_config['to']
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 587))
            if email_config.get('use_tls', True):
                server.starttls()
            
            if email_config.get('username') and email_config.get('password'):
                server.login(email_config['username'], email_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            print(f"邮件通知已发送: {subject}")
        
        except Exception as e:
            print(f"发送邮件通知失败: {e}")
    
    def send_webhook_notification(self, alerts, health_report):
        """发送Webhook通知"""
        try:
            webhook_config = self.notification_settings['webhook']
            
            payload = {
                'timestamp': health_report['timestamp'],
                'overall_status': health_report['overall_status'],
                'alerts': alerts,
                'cluster_info': {
                    'nodes': len(health_report.get('nodes', [])),
                    'queues': len(health_report.get('queues', []))
                }
            }
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {}),
                timeout=10
            )
            
            if response.status_code == 200:
                print("Webhook通知发送成功")
            else:
                print(f"Webhook通知发送失败: HTTP {response.status_code}")
        
        except Exception as e:
            print(f"发送Webhook通知失败: {e}")
    
    def run_continuous_monitoring(self, check_interval=60):
        """运行持续监控"""
        print(f"开始持续监控，检查间隔: {check_interval}秒")
        
        while True:
            try:
                health_report = self.check_cluster_health()
                self.process_alerts(health_report)
                
                # 保存健康报告
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"health_report_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(health_report, f, indent=2, ensure_ascii=False)
                
                print(f"健康检查完成: {health_report['overall_status']}")
                
                # 等待下次检查
                time.sleep(check_interval)
            
            except KeyboardInterrupt:
                print("监控已停止")
                break
            except Exception as e:
                print(f"监控异常: {e}")
                time.sleep(check_interval)

# 配置文件示例
config = {
    "nodes": [
        {
            "name": "node1",
            "host": "192.168.1.10",
            "username": "admin",
            "password": "admin123",
            "healthy": True
        },
        {
            "name": "node2",
            "host": "192.168.1.11",
            "username": "admin",
            "password": "admin123",
            "healthy": True
        }
    ],
    "alert_rules": {
        "queue_backlog_threshold": 10000,
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90
    },
    "notifications": {
        "email": {
            "enabled": True,
            "smtp_server": "smtp.company.com",
            "smtp_port": 587,
            "use_tls": True,
            "username": "alerts@company.com",
            "password": "password",
            "from": "alerts@company.com",
            "to": "admin@company.com",
            "rules": {
                "high_cpu": {"enabled": True, "levels": ["critical"]},
                "high_memory": {"enabled": True, "levels": ["critical"]},
                "queue_backlog": {"enabled": True, "levels": ["warning", "critical"]},
                "no_consumer": {"enabled": True, "levels": ["critical"]}
            }
        },
        "webhook": {
            "enabled": False,
            "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "headers": {"Content-Type": "application/json"}
        }
    }
}

if __name__ == "__main__":
    monitor = AutomatedHealthMonitor(config)
    
    # 单次检查
    health_report = monitor.check_cluster_health()
    print(json.dumps(health_report, indent=2, ensure_ascii=False))
    
    # 持续监控
    # monitor.run_continuous_monitoring(check_interval=60)
```

## 故障排查指南

### 常见问题诊断流程

#### 1. 服务无法启动
```bash
# 检查RabbitMQ状态
sudo systemctl status rabbitmq-server

# 查看启动日志
sudo journalctl -u rabbitmq-server -f

# 检查端口占用
sudo netstat -tlnp | grep 5672

# 检查配置文件
sudo rabbitmqctl eval 'config().'
```

#### 2. 连接问题
```bash
# 检查网络连接
telnet rabbitmq-host 5672

# 检查防火墙
sudo iptables -L

# 查看连接状态
sudo rabbitmqctl list_connections
```

#### 3. 性能问题
```bash
# 查看队列状态
sudo rabbitmqctl list_queues name messages consumers

# 查看内存使用
sudo rabbitmqctl status | grep memory

# 查看磁盘空间
df -h
```

### 故障恢复脚本

```python
import subprocess
import time
import logging

class RabbitMQRecovery:
    def __init__(self):
        self.logger = self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def restart_rabbitmq(self):
        """重启RabbitMQ服务"""
        try:
            self.logger.info("正在重启RabbitMQ服务...")
            
            # 停止服务
            result = subprocess.run(['sudo', 'systemctl', 'stop', 'rabbitmq-server'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"停止服务失败: {result.stderr}")
                return False
            
            time.sleep(5)
            
            # 启动服务
            result = subprocess.run(['sudo', 'systemctl', 'start', 'rabbitmq-server'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"启动服务失败: {result.stderr}")
                return False
            
            # 等待服务启动
            time.sleep(10)
            
            # 检查服务状态
            result = subprocess.run(['sudo', 'systemctl', 'is-active', 'rabbitmq-server'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip() == 'active':
                self.logger.info("RabbitMQ服务重启成功")
                return True
            else:
                self.logger.error("RabbitMQ服务重启失败")
                return False
        
        except Exception as e:
            self.logger.error(f"重启服务异常: {e}")
            return False
    
    def clear_memory(self):
        """清理内存（删除所有队列）"""
        try:
            self.logger.info("正在清理所有队列...")
            
            # 列出所有队列
            result = subprocess.run([
                'rabbitmqctl', 'list_queues', 'name'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                queues = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                
                for queue in queues:
                    if queue:
                        # 删除队列
                        delete_result = subprocess.run([
                            'rabbitmqctl', 'delete_queue', queue
                        ], capture_output=True, text=True)
                        
                        if delete_result.returncode == 0:
                            self.logger.info(f"已删除队列: {queue}")
                        else:
                            self.logger.warning(f"删除队列失败: {queue}")
            
            self.logger.info("队列清理完成")
            return True
        
        except Exception as e:
            self.logger.error(f"清理队列异常: {e}")
            return False
    
    def reset_cluster(self):
        """重置集群（警告：会丢失所有数据）"""
        try:
            self.logger.warning("正在重置集群...")
            
            # 停止应用
            result = subprocess.run(['rabbitmqctl', 'stop_app'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"停止应用失败: {result.stderr}")
                return False
            
            # 重置应用
            result = subprocess.run(['rabbitmqctl', 'reset'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"重置应用失败: {result.stderr}")
                return False
            
            # 启动应用
            result = subprocess.run(['rabbitmqctl', 'start_app'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"启动应用失败: {result.stderr}")
                return False
            
            self.logger.info("集群重置完成")
            return True
        
        except Exception as e:
            self.logger.error(f"重置集群异常: {e}")
            return False
    
    def emergency_recovery(self):
        """紧急恢复流程"""
        self.logger.info("开始紧急恢复流程...")
        
        # 1. 检查服务状态
        result = subprocess.run(['sudo', 'systemctl', 'is-active', 'rabbitmq-server'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip() == 'active':
            self.logger.info("RabbitMQ服务正在运行，尝试重启...")
            if not self.restart_rabbitmq():
                self.logger.error("重启失败，尝试重置集群...")
                return self.reset_cluster()
        else:
            self.logger.warning("RabbitMQ服务未运行，正在启动...")
            return self.restart_rabbitmq()

if __name__ == "__main__":
    recovery = RabbitMQRecovery()
    recovery.emergency_recovery()
```

## 监控最佳实践

### 1. 监控指标设置
- **关键指标优先**：重点监控消息积压、连接数、内存使用
- **合理告警阈值**：避免过度告警，设置合理的告警级别
- **监控覆盖全面**：从系统、RabbitMQ、应用多个层面监控

### 2. 数据留存策略
- **短期高频**：最近24小时数据保留分钟级精度
- **中期中频**：最近7天数据保留小时级精度
- **长期低频**：历史数据保留天级精度

### 3. 告警管理
- **分级告警**：区分警告和严重级别
- **去重机制**：避免重复告警
- **告警抑制**：在维护窗口内抑制告警

### 4. 容量规划
- **历史数据分析**：基于历史数据预测容量需求
- **增长趋势监控**：监控业务增长对资源的需求
- **弹性扩容准备**：准备扩容方案和脚本

### 5. 文档和流程
- **监控文档**：维护详细的监控配置文档
- **应急流程**：制定故障处理的标准流程
- **定期演练**：定期进行故障应急演练

## 总结

RabbitMQ监控与运维是确保消息系统稳定运行的关键环节。通过完善的监控体系、及时的告警机制和自动化的运维工具，可以：

- **提前发现潜在问题**：通过监控指标提前识别性能瓶颈和资源问题
- **快速定位故障原因**：通过日志分析和监控数据快速定位问题根源
- **自动化处理常见问题**：通过自动化脚本处理常见故障
- **持续优化系统性能**：通过性能基准测试和数据分析优化系统配置

建立一个完善的监控运维体系需要：
1. **选择合适的监控工具**：Prometheus+Grafana是很好的组合
2. **制定合理的监控策略**：平衡监控覆盖度和成本
3. **建立完善的告警机制**：确保关键问题能及时发现
4. **培养运维团队技能**：提升团队对RabbitMQ的运维能力
5. **持续改进和优化**：根据实际运行情况不断改进监控策略

通过持续的监控和运维，可以确保RabbitMQ在生产环境中稳定、高效地运行，为业务提供可靠的消息服务支撑。