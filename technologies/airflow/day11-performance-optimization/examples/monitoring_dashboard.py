"""
Airflow 监控和分析工具示例代码
展示如何使用 Prometheus 和 Grafana 监控 Airflow 性能
"""

from datetime import datetime, timedelta
import time
import random
from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


# Prometheus 指标定义
# Counter: 只能增加的指标，用于计数
TASK_EXECUTION_COUNT = Counter(
    'airflow_task_executions_total',
    'Total number of task executions',
    ['dag_id', 'task_id', 'state']
)

# Gauge: 可以上下浮动的指标，用于表示当前状态
ACTIVE_DAG_RUNS = Gauge(
    'airflow_active_dag_runs',
    'Number of currently active DAG runs'
)

CURRENT_TASK_INSTANCES = Gauge(
    'airflow_current_task_instances',
    'Current number of task instances by state',
    ['state']
)

# Histogram: 用于观察事件的分布情况
TASK_DURATION = Histogram(
    'airflow_task_duration_seconds',
    'Duration of task executions in seconds',
    ['dag_id', 'task_id'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, float('inf'))
)

# Summary: 类似于 Histogram，但更关注分位数
TASK_PROCESSING_TIME = Summary(
    'airflow_task_processing_seconds',
    'Time spent processing tasks',
    ['dag_id', 'task_id']
)


# 模拟任务执行监控
def monitored_task_simulation(**context):
    """
    模拟带有监控的任务执行
    """
    dag_id = context['dag_run'].dag_id
    task_id = context['task_instance'].task_id
    
    print(f"开始执行任务: {dag_id}.{task_id}")
    
    # 增加任务执行计数
    TASK_EXECUTION_COUNT.labels(
        dag_id=dag_id, 
        task_id=task_id, 
        state='started'
    ).inc()
    
    # 更新活跃 DAG 运行数
    ACTIVE_DAG_RUNS.inc()
    
    # 更新当前任务实例状态
    CURRENT_TASK_INSTANCES.labels(state='running').inc()
    
    # 记录任务开始时间
    start_time = time.time()
    
    try:
        # 模拟任务执行时间（随机 1-30 秒）
        execution_time = random.uniform(1, 30)
        time.sleep(min(execution_time, 5))  # 限制最大等待时间以加快演示
        
        # 模拟任务成功率
        if random.random() < 0.9:  # 90% 成功率
            # 记录成功的任务
            TASK_EXECUTION_COUNT.labels(
                dag_id=dag_id, 
                task_id=task_id, 
                state='success'
            ).inc()
            
            print(f"任务 {dag_id}.{task_id} 执行成功")
            return "success"
        else:
            # 记录失败的任务
            TASK_EXECUTION_COUNT.labels(
                dag_id=dag_id, 
                task_id=task_id, 
                state='failed'
            ).inc()
            
            print(f"任务 {dag_id}.{task_id} 执行失败")
            raise Exception("任务执行失败")
            
    except Exception as e:
        # 记录失败的任务
        TASK_EXECUTION_COUNT.labels(
            dag_id=dag_id, 
            task_id=task_id, 
            state='failed'
        ).inc()
        
        print(f"任务 {dag_id}.{task_id} 发生异常: {str(e)}")
        raise
    finally:
        # 计算并记录任务持续时间
        duration = time.time() - start_time
        TASK_DURATION.labels(
            dag_id=dag_id, 
            task_id=task_id
        ).observe(duration)
        
        # 记录任务处理时间
        TASK_PROCESSING_TIME.labels(
            dag_id=dag_id, 
            task_id=task_id
        ).observe(duration)
        
        # 更新活跃 DAG 运行数
        ACTIVE_DAG_RUNS.dec()
        
        # 更新当前任务实例状态
        CURRENT_TASK_INSTANCES.labels(state='running').dec()
        
        if 'success' in locals() and success == "success":
            CURRENT_TASK_INSTANCES.labels(state='success').inc()
        else:
            CURRENT_TASK_INSTANCES.labels(state='failed').inc()
        
        print(f"任务 {dag_id}.{task_id} 完成，耗时 {duration:.2f} 秒")


# 系统性能监控
def system_performance_monitor(**context):
    """
    监控系统性能指标
    """
    import psutil
    import os
    
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # 创建临时 Gauge 指标来记录系统性能
    SYSTEM_CPU_USAGE = Gauge(
        'airflow_system_cpu_percent',
        'System CPU usage percentage'
    )
    
    SYSTEM_MEMORY_USAGE = Gauge(
        'airflow_system_memory_percent',
        'System memory usage percentage'
    )
    
    SYSTEM_DISK_USAGE = Gauge(
        'airflow_system_disk_percent',
        'System disk usage percentage'
    )
    
    # 更新指标值
    SYSTEM_CPU_USAGE.set(cpu_percent)
    SYSTEM_MEMORY_USAGE.set(memory.percent)
    SYSTEM_DISK_USAGE.set(disk.percent)
    
    print(f"系统性能监控:")
    print(f"  CPU 使用率: {cpu_percent}%")
    print(f"  内存使用率: {memory.percent}%")
    print(f"  磁盘使用率: {disk.percent}%")
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent
    }


# 数据库性能监控
def database_performance_monitor(**context):
    """
    监控数据库性能指标
    """
    # 模拟数据库连接池状态监控
    DB_CONNECTIONS_USED = Gauge(
        'airflow_db_connections_used',
        'Number of database connections currently in use'
    )
    
    DB_CONNECTIONS_AVAILABLE = Gauge(
        'airflow_db_connections_available',
        'Number of available database connections'
    )
    
    DB_QUERY_LATENCY = Histogram(
        'airflow_db_query_latency_seconds',
        'Database query latency in seconds',
        buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
    )
    
    # 模拟数据库连接状态
    used_connections = random.randint(5, 20)
    available_connections = 30 - used_connections
    
    DB_CONNECTIONS_USED.set(used_connections)
    DB_CONNECTIONS_AVAILABLE.set(available_connections)
    
    # 模拟查询延迟
    query_latency = random.uniform(0.01, 2.0)
    DB_QUERY_LATENCY.observe(query_latency)
    
    print(f"数据库性能监控:")
    print(f"  已使用连接数: {used_connections}")
    print(f"  可用连接数: {available_connections}")
    print(f"  查询延迟: {query_latency:.3f} 秒")
    
    return {
        "used_connections": used_connections,
        "available_connections": available_connections,
        "query_latency": query_latency
    }


# 自定义业务指标监控
def business_metrics_monitor(**context):
    """
    监控自定义业务指标
    """
    # 业务处理量指标
    PROCESSED_RECORDS = Counter(
        'airflow_processed_records_total',
        'Total number of records processed'
    )
    
    # 业务处理延迟指标
    PROCESSING_LATENCY = Histogram(
        'airflow_processing_latency_seconds',
        'Business processing latency in seconds',
        buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, float('inf'))
    )
    
    # 错误率指标
    ERROR_RATE = Gauge(
        'airflow_error_rate_percent',
        'Error rate percentage'
    )
    
    # 模拟业务处理
    records_count = random.randint(100, 1000)
    PROCESSED_RECORDS.inc(records_count)
    
    # 模拟处理延迟
    latency = random.uniform(0.1, 30.0)
    PROCESSING_LATENCY.observe(latency)
    
    # 模拟错误率
    error_rate = random.uniform(0, 5)
    ERROR_RATE.set(error_rate)
    
    print(f"业务指标监控:")
    print(f"  处理记录数: {records_count}")
    print(f"  处理延迟: {latency:.3f} 秒")
    print(f"  错误率: {error_rate:.2f}%")
    
    return {
        "records_count": records_count,
        "latency": latency,
        "error_rate": error_rate
    }


# Prometheus 指标导出器
def start_prometheus_exporter():
    """
    启动 Prometheus 指标导出器
    """
    try:
        # 启动 HTTP 服务器暴露指标（端口 9102）
        start_http_server(9102)
        print("Prometheus 指标导出器已启动，监听端口 9102")
        print("访问 http://localhost:9102 查看指标")
        return True
    except Exception as e:
        print(f"启动 Prometheus 指标导出器失败: {str(e)}")
        return False


# 创建监控仪表板 DAG
def create_monitoring_dashboard_dag():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        'performance_monitoring_dashboard',
        default_args=default_args,
        description='Airflow 性能监控仪表板演示',
        schedule_interval=timedelta(minutes=10),  # 每10分钟运行一次
        catchup=False,
        max_active_runs=1,
    )

    # 启动 Prometheus 导出器任务
    start_exporter_task = PythonOperator(
        task_id='start_prometheus_exporter',
        python_callable=start_prometheus_exporter,
        dag=dag,
    )

    # 监控任务示例
    monitored_tasks = []
    for i in range(3):
        task = PythonOperator(
            task_id=f'monitored_task_{i}',
            python_callable=monitored_task_simulation,
            dag=dag,
        )
        monitored_tasks.append(task)

    # 系统性能监控任务
    system_monitor_task = PythonOperator(
        task_id='system_performance_monitor',
        python_callable=system_performance_monitor,
        dag=dag,
    )

    # 数据库性能监控任务
    db_monitor_task = PythonOperator(
        task_id='database_performance_monitor',
        python_callable=database_performance_monitor,
        dag=dag,
    )

    # 业务指标监控任务
    business_monitor_task = PythonOperator(
        task_id='business_metrics_monitor',
        python_callable=business_metrics_monitor,
        dag=dag,
    )

    # 设置任务依赖关系
    start_exporter_task >> monitored_tasks[0]
    monitored_tasks[0] >> monitored_tasks[1] >> monitored_tasks[2]
    monitored_tasks[2] >> [system_monitor_task, db_monitor_task, business_monitor_task]

    return dag


# Grafana 仪表板配置示例
def generate_grafana_dashboard_config():
    """
    生成 Grafana 仪表板配置示例
    """
    dashboard_config = {
        "dashboard": {
            "title": "Airflow Performance Monitoring",
            "panels": [
                {
                    "title": "任务执行统计",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(airflow_task_executions_total[5m])",
                            "legendFormat": "{{dag_id}}.{{task_id}} ({{state}})"
                        }
                    ]
                },
                {
                    "title": "任务持续时间分布",
                    "type": "heatmap",
                    "targets": [
                        {
                            "expr": "airflow_task_duration_seconds_bucket",
                            "format": "heatmap"
                        }
                    ]
                },
                {
                    "title": "活跃 DAG 运行数",
                    "type": "gauge",
                    "targets": [
                        {
                            "expr": "airflow_active_dag_runs"
                        }
                    ]
                },
                {
                    "title": "系统资源使用情况",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "airflow_system_cpu_percent",
                            "legendFormat": "CPU 使用率"
                        },
                        {
                            "expr": "airflow_system_memory_percent",
                            "legendFormat": "内存使用率"
                        },
                        {
                            "expr": "airflow_system_disk_percent",
                            "legendFormat": "磁盘使用率"
                        }
                    ]
                },
                {
                    "title": "数据库连接状态",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "airflow_db_connections_used",
                            "legendFormat": "已使用连接"
                        },
                        {
                            "expr": "airflow_db_connections_available",
                            "legendFormat": "可用连接"
                        }
                    ]
                }
            ]
        }
    }
    
    return dashboard_config


# 监控告警规则示例
def generate_alerting_rules():
    """
    生成监控告警规则示例
    """
    alerting_rules = [
        {
            "name": "HighTaskFailureRate",
            "expr": "rate(airflow_task_executions_total{state='failed'}[5m]) > 0.1",
            "for": "5m",
            "labels": {
                "severity": "warning"
            },
            "annotations": {
                "summary": "任务失败率过高",
                "description": "过去5分钟内任务失败率超过10%"
            }
        },
        {
            "name": "HighSystemCPUUsage",
            "expr": "airflow_system_cpu_percent > 80",
            "for": "2m",
            "labels": {
                "severity": "critical"
            },
            "annotations": {
                "summary": "系统CPU使用率过高",
                "description": "系统CPU使用率持续超过80%"
            }
        },
        {
            "name": "LowAvailableDBConnections",
            "expr": "airflow_db_connections_available < 5",
            "for": "1m",
            "labels": {
                "severity": "warning"
            },
            "annotations": {
                "summary": "数据库可用连接数不足",
                "description": "数据库可用连接数少于5个"
            }
        }
    ]
    
    return alerting_rules


# 性能分析报告生成
def generate_performance_report(**context):
    """
    生成性能分析报告
    """
    from datetime import datetime
    
    report = {
        "report_time": datetime.now().isoformat(),
        "metrics_summary": {
            "total_task_executions": TASK_EXECUTION_COUNT.describe(),
            "active_dag_runs": ACTIVE_DAG_RUNS.describe(),
            "avg_task_duration": "查看 histogram 指标获取详细信息"
        },
        "recommendations": [
            "定期检查任务失败率，及时处理异常任务",
            "监控系统资源使用情况，避免资源瓶颈",
            "优化数据库查询，减少连接池压力",
            "根据业务需求调整任务并发度"
        ]
    }
    
    print("性能分析报告:")
    print(f"  报告时间: {report['report_time']}")
    print("  指标摘要:")
    for key, value in report['metrics_summary'].items():
        print(f"    {key}: {value}")
    print("  优化建议:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"    {i}. {rec}")
    
    return report


# 主函数
if __name__ == '__main__':
    print("Airflow Monitoring and Analysis Tools Examples")
    print("=" * 50)
    
    # 启动 Prometheus 导出器
    print("1. 启动 Prometheus 指标导出器:")
    start_prometheus_exporter()
    
    print("\n2. 生成 Grafana 仪表板配置:")
    dashboard = generate_grafana_dashboard_config()
    print("Grafana 仪表板配置已生成")
    
    print("\n3. 生成监控告警规则:")
    alerts = generate_alerting_rules()
    print(f"已生成 {len(alerts)} 条告警规则")
    
    print("\n监控和分析工具示例创建完成!")
    print("主要包括:")
    print("- Prometheus 指标收集")
    print("- Grafana 仪表板配置")
    print("- 监控告警规则")
    print("- 性能分析报告")