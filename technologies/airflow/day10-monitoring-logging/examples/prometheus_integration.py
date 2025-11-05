#!/usr/bin/env python3
"""
Airflow与Prometheus集成示例

这个脚本演示了如何将Airflow指标导出到Prometheus，
以及如何创建自定义指标收集器。
"""

import time
import random
from typing import List, Dict, Any
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary
from prometheus_client.core import CollectorRegistry, GaugeMetricFamily
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AirflowMetricsCollector:
    """Airflow指标收集器"""
    
    def __init__(self):
        """初始化指标收集器"""
        # 创建指标
        self.dag_success_total = Counter(
            'airflow_dag_success_total',
            'Total number of successful DAG runs',
            ['dag_id']
        )
        
        self.dag_failure_total = Counter(
            'airflow_dag_failure_total',
            'Total number of failed DAG runs',
            ['dag_id']
        )
        
        self.task_duration_seconds = Histogram(
            'airflow_task_duration_seconds',
            'Task execution time in seconds',
            ['dag_id', 'task_id'],
            buckets=[1, 5, 10, 30, 60, 120, 300, 600, float('inf')]
        )
        
        self.scheduler_heartbeat = Gauge(
            'airflow_scheduler_heartbeat',
            'Scheduler heartbeat timestamp'
        )
        
        self.active_task_instances = Gauge(
            'airflow_active_task_instances',
            'Number of currently active task instances'
        )
        
        self.dag_run_duration_seconds = Summary(
            'airflow_dag_run_duration_seconds',
            'DAG run execution time in seconds',
            ['dag_id']
        )
        
        # 模拟数据
        self.dag_ids = ['example_dag', 'data_pipeline', 'ml_training', 'report_generation']
        self.task_ids = ['extract', 'transform', 'load', 'validate', 'publish']
        
    def collect_dag_metrics(self):
        """收集DAG相关指标"""
        for dag_id in self.dag_ids:
            # 模拟DAG成功和失败计数
            success_count = random.randint(0, 10)
            failure_count = random.randint(0, 3)
            
            for _ in range(success_count):
                self.dag_success_total.labels(dag_id=dag_id).inc()
                
            for _ in range(failure_count):
                self.dag_failure_total.labels(dag_id=dag_id).inc()
                
            # 记录DAG运行时间
            with self.dag_run_duration_seconds.labels(dag_id=dag_id).time():
                time.sleep(random.uniform(0.1, 1.0))  # 模拟DAG运行时间
                
    def collect_task_metrics(self):
        """收集任务相关指标"""
        for dag_id in self.dag_ids:
            for task_id in self.task_ids:
                # 模拟任务执行时间
                duration = random.uniform(0.5, 10.0)
                self.task_duration_seconds.labels(
                    dag_id=dag_id, 
                    task_id=task_id
                ).observe(duration)
                
    def update_scheduler_metrics(self):
        """更新调度器相关指标"""
        self.scheduler_heartbeat.set_to_current_time()
        self.active_task_instances.set(random.randint(0, 20))
        
    def simulate_metrics_collection(self):
        """模拟指标收集过程"""
        logger.info("Starting metrics collection simulation")
        
        while True:
            try:
                # 收集各种指标
                self.collect_dag_metrics()
                self.collect_task_metrics()
                self.update_scheduler_metrics()
                
                logger.info("Metrics collected successfully")
                time.sleep(5)  # 每5秒收集一次
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                time.sleep(5)

class CustomAirflowCollector:
    """自定义Airflow指标收集器"""
    
    def __init__(self):
        """初始化自定义收集器"""
        pass
        
    def collect(self):
        """收集自定义指标"""
        # 创建自定义指标
        metric = GaugeMetricFamily(
            'airflow_custom_business_metric',
            'Custom business metric for Airflow',
            labels=['business_unit', 'metric_type']
        )
        
        # 添加指标值
        metric.add_metric(['sales', 'revenue'], random.uniform(1000, 10000))
        metric.add_metric(['marketing', 'leads'], random.randint(50, 500))
        metric.add_metric(['support', 'tickets'], random.randint(10, 100))
        
        yield metric

def setup_prometheus_exporter(port: int = 9102):
    """
    设置Prometheus导出器
    
    Args:
        port: 导出器端口
    """
    logger.info(f"Starting Prometheus exporter on port {port}")
    
    # 创建注册表
    registry = CollectorRegistry()
    
    # 注册默认收集器
    registry.register(AirflowMetricsCollector())
    
    # 注册自定义收集器
    registry.register(CustomAirflowCollector())
    
    # 启动HTTP服务器
    start_http_server(port, registry=registry)
    logger.info(f"Prometheus exporter started on port {port}")

def main():
    """主函数"""
    # 设置Prometheus导出器
    setup_prometheus_exporter(9102)
    
    # 创建指标收集器实例
    collector = AirflowMetricsCollector()
    
    # 在后台线程中模拟指标收集
    collection_thread = threading.Thread(
        target=collector.simulate_metrics_collection,
        daemon=True
    )
    collection_thread.start()
    
    logger.info("Airflow Prometheus integration started")
    logger.info("Metrics are available at http://localhost:9102/metrics")
    
    # 保持程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        exit(0)

# 配置示例
PROMETHEUS_CONFIG_EXAMPLE = """
# Prometheus配置示例
scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['localhost:9102']
    scrape_interval: 15s
    scrape_timeout: 10s
"""

# Grafana仪表板示例
GRAFANA_DASHBOARD_EXAMPLE = """
{
  "dashboard": {
    "title": "Airflow Monitoring",
    "panels": [
      {
        "title": "DAG Success Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(airflow_dag_success_total[5m])",
            "legendFormat": "{{dag_id}}"
          }
        ]
      },
      {
        "title": "Task Duration",
        "type": "heatmap",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(airflow_task_duration_seconds_bucket[5m]))",
            "legendFormat": "{{dag_id}}.{{task_id}}"
          }
        ]
      }
    ]
  }
}
"""

# 告警规则示例
ALERT_RULES_EXAMPLE = """
groups:
- name: airflow_alerts
  rules:
  - alert: AirflowDAGFailureRate
    expr: rate(airflow_dag_failure_total[5m]) > 0.1
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "High DAG failure rate detected"
      description: "DAG failure rate is above 10% for the last 5 minutes"
      
  - alert: AirflowSchedulerDown
    expr: absent(airflow_scheduler_heartbeat) > 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Airflow scheduler is down"
      description: "No scheduler heartbeat detected for more than 2 minutes"
"""

if __name__ == '__main__':
    main()