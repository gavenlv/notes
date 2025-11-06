"""
Airflow监控和指标收集示例
展示如何收集性能指标、设置监控和告警
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.hooks.base import BaseHook
from airflow.operators.email import EmailOperator
import time
import random
import logging
import json
import psutil
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# 尝试导入statsd，如果不可用则使用模拟实现
try:
    import statsd
    STATSD_AVAILABLE = True
except ImportError:
    STATSD_AVAILABLE = False
    logging.warning("statsd库不可用，将使用模拟实现")

# 性能指标数据类
@dataclass
class PerformanceMetric:
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags or {}
        }

# 监控管理器
class MonitoringManager:
    """监控管理器"""
    
    def __init__(self, prefix: str = "airflow.demo"):
        self.prefix = prefix
        self.metrics: List[PerformanceMetric] = []
        
        if STATSD_AVAILABLE:
            self.statsd_client = statsd.StatsClient(
                host='localhost',
                port=8125,
                prefix=prefix
            )
        else:
            self.statsd_client = None
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录仪表盘指标"""
        metric = PerformanceMetric(name, value, datetime.now(), tags)
        self.metrics.append(metric)
        
        if self.statsd_client:
            self.statsd_client.gauge(name, value)
        
        logging.info(f"指标记录 - {name}: {value} {tags or ''}")
    
    def timing(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录时间指标"""
        metric = PerformanceMetric(name, value, datetime.now(), tags)
        self.metrics.append(metric)
        
        if self.statsd_client:
            self.statsd_client.timing(name, value)
        
        logging.info(f"时间指标记录 - {name}: {value}ms {tags or ''}")
    
    def increment(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """记录计数指标"""
        metric = PerformanceMetric(name, value, datetime.now(), tags)
        self.metrics.append(metric)
        
        if self.statsd_client:
            self.statsd_client.incr(name, value)
        
        logging.info(f"计数指标记录 - {name}: {value} {tags or ''}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        summary = {
            'total_metrics': len(self.metrics),
            'metric_types': {},
            'latest_values': {}
        }
        
        for metric in self.metrics:
            metric_type = metric.name.split('.')[0]
            summary['metric_types'][metric_type] = summary['metric_types'].get(metric_type, 0) + 1
            summary['latest_values'][metric.name] = metric.value
        
        return summary
    
    def export_metrics(self, filepath: str):
        """导出指标到文件"""
        metrics_data = [metric.to_dict() for metric in self.metrics]
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"指标已导出到: {filepath}")

# 默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 监控指标DAG
dag = DAG(
    'monitoring_metrics_demo',
    default_args=default_args,
    description='监控和指标收集示例',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['monitoring', 'metrics', 'performance'],
)

def collect_system_metrics(**context):
    """收集系统指标"""
    monitoring = MonitoringManager("airflow.system")
    
    # CPU指标
    cpu_percent = psutil.cpu_percent(interval=1)
    monitoring.gauge("cpu.usage_percent", cpu_percent, {"type": "total"})
    
    # 每个CPU核心的使用率
    per_cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    for i, cpu_percent in enumerate(per_cpu_percent):
        monitoring.gauge("cpu.usage_percent", cpu_percent, {"core": str(i), "type": "per_core"})
    
    # 内存指标
    memory = psutil.virtual_memory()
    monitoring.gauge("memory.total_bytes", memory.total)
    monitoring.gauge("memory.available_bytes", memory.available)
    monitoring.gauge("memory.used_bytes", memory.used)
    monitoring.gauge("memory.percent", memory.percent)
    
    # 磁盘指标
    disk = psutil.disk_usage('/')
    monitoring.gauge("disk.total_bytes", disk.total)
    monitoring.gauge("disk.used_bytes", disk.used)
    monitoring.gauge("disk.free_bytes", disk.free)
    monitoring.gauge("disk.percent", (disk.used / disk.total) * 100)
    
    # 网络指标
    net_io = psutil.net_io_counters()
    monitoring.gauge("network.bytes_sent", net_io.bytes_sent)
    monitoring.gauge("network.bytes_recv", net_io.bytes_recv)
    monitoring.gauge("network.packets_sent", net_io.packets_sent)
    monitoring.gauge("network.packets_recv", net_io.packets_recv)
    
    # 进程指标
    process = psutil.Process()
    monitoring.gauge("process.memory_rss_bytes", process.memory_info().rss)
    monitoring.gauge("process.memory_vms_bytes", process.memory_info().vms)
    monitoring.gauge("process.memory_percent", process.memory_percent())
    monitoring.gauge("process.cpu_percent", process.cpu_percent())
    monitoring.gauge("process.num_threads", process.num_threads())
    
    # 保存监控管理器到上下文
    context['task_instance'].xcom_push(key='monitoring_manager', value=monitoring)
    
    logging.info(f"系统指标收集完成，记录了 {len(monitoring.metrics)} 个指标")
    return monitoring.get_metrics_summary()

def collect_airflow_metrics(**context):
    """收集Airflow特定指标"""
    monitoring = MonitoringManager("airflow.internal")
    
    # 任务队列长度（模拟）
    queue_length = random.randint(0, 20)
    monitoring.gauge("queue.length", queue_length, {"queue": "default"})
    
    # 活跃任务数（模拟）
    active_tasks = random.randint(1, 10)
    monitoring.gauge("tasks.active", active_tasks)
    
    # 成功任务数（模拟）
    success_tasks = random.randint(50, 100)
    monitoring.increment("tasks.success", success_tasks)
    
    # 失败任务数（模拟）
    failed_tasks = random.randint(0, 5)
    monitoring.increment("tasks.failed", failed_tasks)
    
    # DAG运行状态
    dag_run_count = random.randint(1, 5)
    monitoring.increment("dag_runs.total", dag_run_count)
    
    # 数据库连接数（模拟）
    db_connections = random.randint(5, 20)
    monitoring.gauge("database.connections", db_connections)
    
    # 数据库查询时间（模拟）
    query_time = random.uniform(0.01, 0.5)
    monitoring.timing("database.query_time_ms", query_time * 1000)
    
    # 保存监控管理器
    context['task_instance'].xcom_push(key='monitoring_manager', value=monitoring)
    
    logging.info(f"Airflow指标收集完成，记录了 {len(monitoring.metrics)} 个指标")
    return monitoring.get_metrics_summary()

def simulate_business_metrics(**context):
    """模拟业务指标收集"""
    monitoring = MonitoringManager("business.metrics")
    
    # 数据处理指标
    records_processed = random.randint(1000, 10000)
    monitoring.increment("data.records_processed", records_processed)
    monitoring.gauge("data.processing_rate_per_second", records_processed / 3600)  # 每小时处理速率
    
    # 数据质量指标
    data_quality_score = random.uniform(85, 99)
    monitoring.gauge("data.quality_score", data_quality_score)
    
    # 错误率
    error_count = random.randint(0, 50)
    error_rate = (error_count / records_processed) * 100 if records_processed > 0 else 0
    monitoring.gauge("data.error_rate_percent", error_rate)
    
    # 业务KPI
    revenue = random.uniform(1000, 10000)
    monitoring.gauge("business.revenue_usd", revenue)
    
    customer_count = random.randint(100, 1000)
    monitoring.gauge("business.customers", customer_count)
    
    # 转换率
    conversion_rate = random.uniform(2, 15)
    monitoring.gauge("business.conversion_rate_percent", conversion_rate)
    
    # 响应时间
    response_time = random.uniform(0.1, 2.0)
    monitoring.timing("api.response_time_ms", response_time * 1000)
    
    # 吞吐量
    throughput = random.randint(50, 500)
    monitoring.gauge("api.throughput_per_minute", throughput)
    
    # 保存监控管理器
    context['task_instance'].xcom_push(key='monitoring_manager', value=monitoring)
    
    logging.info(f"业务指标收集完成，处理了 {records_processed} 条记录")
    return monitoring.get_metrics_summary()

def performance_test_with_metrics(**context):
    """性能测试并收集指标"""
    monitoring = MonitoringManager("performance.tests")
    
    # 记录测试开始时间
    test_start_time = time.time()
    monitoring.gauge("test.start_time", test_start_time)
    
    # 模拟不同类型的性能测试
    test_types = ['cpu', 'memory', 'io', 'network']
    
    for test_type in test_types:
        monitoring.gauge(f"test.{test_type}.status", 1, {"test": "running"})
        
        start_time = time.time()
        
        if test_type == 'cpu':
            # CPU性能测试
            result = cpu_performance_test()
        elif test_type == 'memory':
            # 内存性能测试
            result = memory_performance_test()
        elif test_type == 'io':
            # IO性能测试
            result = io_performance_test()
        elif test_type == 'network':
            # 网络性能测试
            result = network_performance_test()
        
        duration = time.time() - start_time
        monitoring.timing(f"test.{test_type}.duration_ms", duration * 1000)
        monitoring.gauge(f"test.{test_type}.status", 0, {"test": "completed"})
        monitoring.gauge(f"test.{test_type}.result", result['score'])
        
        logging.info(f"性能测试 {test_type} 完成，耗时: {duration:.3f}s, 得分: {result['score']}")
    
    # 记录测试结束时间
    test_end_time = time.time()
    total_duration = test_end_time - test_start_time
    monitoring.timing("test.total_duration_ms", total_duration * 1000)
    monitoring.gauge("test.end_time", test_end_time)
    
    # 保存监控管理器
    context['task_instance'].xcom_push(key='monitoring_manager', value=monitoring)
    
    logging.info(f"性能测试完成，总耗时: {total_duration:.3f}s")
    return monitoring.get_metrics_summary()

def cpu_performance_test():
    """CPU性能测试"""
    # 简单的CPU基准测试
    start_time = time.time()
    result = 0
    
    for i in range(100000):
        result += i ** 2 % 1000000
    
    duration = time.time() - start_time
    score = max(0, 100 - duration * 10)  # 分数越高越好
    
    return {'score': score, 'duration': duration, 'type': 'cpu'}

def memory_performance_test():
    """内存性能测试"""
    start_time = time.time()
    
    # 创建和销毁大量对象
    objects = []
    for i in range(10000):
        obj = {'id': i, 'data': 'x' * 100}
        objects.append(obj)
        if len(objects) > 1000:
            objects = objects[-500:]  # 保持内存使用
    
    duration = time.time() - start_time
    score = max(0, 100 - duration * 50)  # 分数越高越好
    
    return {'score': score, 'duration': duration, 'type': 'memory'}

def io_performance_test():
    """IO性能测试"""
    start_time = time.time()
    
    # 文件读写测试
    test_file = '/tmp/io_test.txt'
    
    try:
        # 写入测试
        with open(test_file, 'w') as f:
            for i in range(1000):
                f.write(f"Test line {i}: {'x' * 100}\n")
        
        # 读取测试
        with open(test_file, 'r') as f:
            content = f.read()
        
        # 清理
        os.remove(test_file)
        
    except Exception as e:
        logging.error(f"IO性能测试失败: {e}")
        return {'score': 0, 'duration': 0, 'type': 'io', 'error': str(e)}
    
    duration = time.time() - start_time
    score = max(0, 100 - duration * 20)  # 分数越高越好
    
    return {'score': score, 'duration': duration, 'type': 'io'}

def network_performance_test():
    """网络性能测试（模拟）"""
    start_time = time.time()
    
    # 模拟网络延迟
    time.sleep(random.uniform(0.01, 0.1))
    
    duration = time.time() - start_time
    score = max(0, 100 - duration * 100)  # 分数越高越好
    
    return {'score': score, 'duration': duration, 'type': 'network'}

def generate_monitoring_report(**context):
    """生成监控报告"""
    # 收集所有监控管理器
    all_metrics = []
    
    # 从各个任务收集指标
    task_ids = [
        'collect_system_metrics',
        'collect_airflow_metrics',
        'simulate_business_metrics',
        'performance_test_with_metrics'
    ]
    
    for task_id in task_ids:
        try:
            monitoring_summary = context['task_instance'].xcom_pull(task_ids=task_id)
            if monitoring_summary:
                all_metrics.append({
                    'task_id': task_id,
                    'summary': monitoring_summary
                })
        except Exception as e:
            logging.error(f"获取任务 {task_id} 指标失败: {e}")
    
    # 生成综合报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'report_type': 'comprehensive_monitoring',
        'metrics_summary': all_metrics,
        'system_health': evaluate_system_health(all_metrics),
        'recommendations': generate_monitoring_recommendations(all_metrics)
    }
    
    # 保存报告
    report_file = f"/tmp/monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logging.info(f"监控报告已生成: {report_file}")
    return report

def evaluate_system_health(metrics_data):
    """评估系统健康状况"""
    health_status = {
        'overall': 'healthy',
        'components': {}
    }
    
    # 评估各个组件
    for data in metrics_data:
        task_id = data['task_id']
        summary = data['summary']
        
        if task_id == 'collect_system_metrics':
            # 系统资源评估
            health_status['components']['system_resources'] = 'healthy'
            
        elif task_id == 'collect_airflow_metrics':
            # Airflow组件评估
            health_status['components']['airflow'] = 'healthy'
            
        elif task_id == 'simulate_business_metrics':
            # 业务指标评估
            health_status['components']['business'] = 'healthy'
            
        elif task_id == 'performance_test_with_metrics':
            # 性能测试评估
            health_status['components']['performance'] = 'healthy'
    
    # 总体评估
    component_statuses = list(health_status['components'].values())
    if 'unhealthy' in component_statuses:
        health_status['overall'] = 'unhealthy'
    elif 'warning' in component_statuses:
        health_status['overall'] = 'warning'
    
    return health_status

def generate_monitoring_recommendations(metrics_data):
    """生成监控建议"""
    recommendations = []
    
    # 基于指标数据生成建议
    for data in metrics_data:
        task_id = data['task_id']
        summary = data['summary']
        
        if task_id == 'collect_system_metrics':
            recommendations.extend([
                "定期监控系统资源使用情况",
                "设置资源使用率告警阈值",
                "优化系统配置以提高性能"
            ])
            
        elif task_id == 'collect_airflow_metrics':
            recommendations.extend([
                "监控任务队列长度，避免队列积压",
                "关注失败任务数量，及时处理异常",
                "优化DAG设计以提高执行效率"
            ])
            
        elif task_id == 'simulate_business_metrics':
            recommendations.extend([
                "监控业务关键指标趋势",
                "设置数据质量告警机制",
                "定期审查业务KPI表现"
            ])
            
        elif task_id == 'performance_test_with_metrics':
            recommendations.extend([
                "定期进行性能基准测试",
                "监控性能指标变化趋势",
                "根据性能数据优化系统配置"
            ])
    
    return recommendations

# 告警任务
def check_alerts(**context):
    """检查告警条件"""
    # 这里可以集成真实的告警系统
    # 现在只是模拟告警检查
    
    alerts = [
        {
            'level': 'warning',
            'message': 'CPU使用率超过80%，需要关注',
            'timestamp': datetime.now().isoformat()
        },
        {
            'level': 'info',
            'message': '系统运行正常',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    logging.info(f"告警检查完成，发现 {len(alerts)} 个告警")
    return alerts

# 定义任务
with dag:
    
    # 系统指标收集
    system_metrics_task = PythonOperator(
        task_id='collect_system_metrics',
        python_callable=collect_system_metrics,
        dag=dag,
    )
    
    # Airflow指标收集
    airflow_metrics_task = PythonOperator(
        task_id='collect_airflow_metrics',
        python_callable=collect_airflow_metrics,
        dag=dag,
    )
    
    # 业务指标模拟
    business_metrics_task = PythonOperator(
        task_id='simulate_business_metrics',
        python_callable=simulate_business_metrics,
        dag=dag,
    )
    
    # 性能测试
    performance_test_task = PythonOperator(
        task_id='performance_test_with_metrics',
        python_callable=performance_test_with_metrics,
        dag=dag,
    )
    
    # 告警检查
    alert_check_task = PythonOperator(
        task_id='check_alerts',
        python_callable=check_alerts,
        dag=dag,
    )
    
    # 生成监控报告
    report_task = PythonOperator(
        task_id='generate_monitoring_report',
        python_callable=generate_monitoring_report,
        dag=dag,
    )
    
    # 设置任务依赖
    [system_metrics_task, airflow_metrics_task, business_metrics_task, performance_test_task] >> alert_check_task >> report_task