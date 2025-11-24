# Day 16: 最佳实践与案例研究 - 学习材料

## 1. 生产环境最佳实践

### 1.1 高可用架构设计

在生产环境中，Airflow的高可用性至关重要。以下是关键组件的高可用配置：

```yaml
# 高可用Webserver配置示例
webserver:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1"
  livenessProbe:
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 60
    periodSeconds: 30
  readinessProbe:
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 30
    periodSeconds: 10

# 高可用Scheduler配置示例
scheduler:
  replicas: 2
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1"
  livenessProbe:
    exec:
      command:
        - python
        - -c
        - |
          import requests
          response = requests.get('http://localhost:8080/health')
          if response.status_code != 200:
            exit(1)
    initialDelaySeconds: 60
    periodSeconds: 30

# 高可用数据库配置示例
postgresql:
  replication:
    enabled: true
    readReplicas: 2
  persistence:
    enabled: true
    size: 100Gi
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"
```

### 1.2 安全配置指南

生产环境中的安全配置包括以下几个方面：

```python
# 安全配置示例 airflow.cfg
[webserver]
# 启用身份验证
authenticate = True
auth_backend = airflow.contrib.auth.backends.password_auth

# 启用CSRF保护
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# 启用安全头部
secure_headers = True

[api]
# 启用API认证
auth_backend = airflow.api.auth.backend.basic_auth

[core]
# 加密连接密码
fernet_key = your_fernet_key_here

# 隐藏敏感变量
hide_sensitive_variable_fields = True

# 启用DAG序列化
store_serialized_dags = True

[celery]
# 加密Celery消息
broker_url = redis://:your_password@redis:6379/0
result_backend = db+postgresql://airflow:your_password@postgres/airflow

[logging]
# 配置安全日志
remote_logging = True
remote_base_log_folder = s3://your-bucket/logs
remote_log_conn_id = aws_s3_logs
```

### 1.3 性能调优策略

性能调优是确保Airflow在生产环境中高效运行的关键：

```python
# DAG性能优化示例
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# 优化的DAG配置
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    # 优化参数
    'execution_timeout': timedelta(hours=2),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

dag = DAG(
    'optimized_dag',
    default_args=default_args,
    description='性能优化的DAG示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    # 性能相关配置
    max_active_runs=10,
    concurrency=16,
    max_active_tasks=16,
    dagrun_timeout=timedelta(days=1),
    tags=['production', 'optimized']
)

def optimized_task(**context):
    """优化的任务执行函数"""
    # 使用连接池
    from airflow.hooks.postgres_hook import PostgresHook
    hook = PostgresHook(postgres_conn_id='production_db')
    
    # 批量处理数据
    batch_size = 1000
    offset = 0
    
    while True:
        # 分批处理数据以减少内存使用
        sql = f"""
        SELECT * FROM large_table 
        LIMIT {batch_size} OFFSET {offset}
        """
        records = hook.get_records(sql)
        
        if not records:
            break
            
        # 处理记录
        process_records(records)
        offset += batch_size

# 配置资源优化的任务
optimized_task_op = PythonOperator(
    task_id='optimized_task',
    python_callable=optimized_task,
    # 资源配置
    resources={
        'request_memory': '2Gi',
        'request_cpu': '1',
        'limit_memory': '4Gi',
        'limit_cpu': '2'
    },
    dag=dag
)
```

## 2. 故障排除与调试技巧

### 2.1 常见问题诊断方法

```bash
# 检查Airflow服务状态
airflow webserver --daemon
airflow scheduler --daemon

# 查看服务日志
tail -f /var/log/airflow/webserver.log
tail -f /var/log/airflow/scheduler.log

# 检查DAG状态
airflow dags list
airflow dags state example_dag 2023-01-01

# 检查任务实例状态
airflow tasks list example_dag -s 2023-01-01 -e 2023-01-01
airflow tasks state example_dag task_id 2023-01-01

# 检查数据库连接
airflow db check
```

### 2.2 日志分析技巧

```python
# 日志分析脚本示例
import re
import json
from datetime import datetime
from collections import defaultdict

def analyze_airflow_logs(log_file_path):
    """分析Airflow日志文件"""
    error_patterns = {
        'database_errors': r'(database|connection|timeout)',
        'memory_errors': r'(memory|out of memory|oom)',
        'scheduler_errors': r'(scheduler|heartbeat|deadlock)',
        'task_errors': r'(task failed|retries exceeded)',
    }
    
    error_counts = defaultdict(int)
    error_details = defaultdict(list)
    
    with open(log_file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # 解析日志时间戳
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
            timestamp = timestamp_match.group() if timestamp_match else None
            
            # 检查各种错误模式
            for error_type, pattern in error_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    error_counts[error_type] += 1
                    error_details[error_type].append({
                        'line_number': line_num,
                        'timestamp': timestamp,
                        'message': line.strip()
                    })
    
    # 输出分析结果
    print("错误统计:")
    for error_type, count in error_counts.items():
        print(f"  {error_type}: {count}")
    
    print("\n详细错误信息:")
    for error_type, details in error_details.items():
        print(f"\n{error_type.upper()}:")
        for detail in details[:5]:  # 只显示前5个
            print(f"  行 {detail['line_number']}: {detail['message']}")

# 使用示例
# analyze_airflow_logs('/var/log/airflow/scheduler.log')
```

## 3. 性能调优案例

### 3.1 数据库优化案例

```sql
-- 数据库性能优化SQL示例

-- 为常用查询字段创建索引
CREATE INDEX idx_task_instance_dag_id ON task_instance(dag_id);
CREATE INDEX idx_task_instance_state ON task_instance(state);
CREATE INDEX idx_task_instance_execution_date ON task_instance(execution_date);
CREATE INDEX idx_dag_run_dag_id ON dag_run(dag_id);
CREATE INDEX idx_dag_run_state ON dag_run(state);
CREATE INDEX idx_dag_run_execution_date ON dag_run(execution_date);

-- 定期清理历史数据
DELETE FROM task_instance 
WHERE execution_date < NOW() - INTERVAL '30 days'
AND state IN ('success', 'failed', 'skipped');

DELETE FROM dag_run 
WHERE execution_date < NOW() - INTERVAL '30 days'
AND state IN ('success', 'failed');

-- 分析表以更新统计信息
ANALYZE task_instance;
ANALYZE dag_run;
ANALYZE log;
```

### 3.2 执行器调优案例

```python
# CeleryExecutor调优配置示例
from celery import Celery

# Celery配置优化
celery_config = {
    # 并发设置
    'worker_concurrency': 16,
    'worker_prefetch_multiplier': 1,
    
    # 任务路由
    'task_routes': {
        'airflow.executors.celery_executor.execute_command': {
            'queue': 'default',
            'routing_key': 'default'
        }
    },
    
    # 连接池设置
    'broker_pool_limit': 10,
    'broker_connection_retry': True,
    'broker_connection_retry_on_startup': True,
    
    # 结果后端优化
    'result_expires': 3600,
    'result_backend_always_retry': True,
    'result_backend_max_retries': 3,
    
    # 心跳设置
    'worker_heartbeat': 30,
    'worker_send_task_events': True,
    'task_send_sent_event': True,
    
    # 内存优化
    'worker_max_tasks_per_child': 1000,
    'worker_max_memory_per_child': 100000,  # KB
}

# 应用配置
app = Celery('airflow')
app.config_from_object(celery_config)
```

## 4. 行业应用案例分析

### 4.1 电商数据管道案例

```python
# 电商数据管道DAG示例
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from datetime import datetime, timedelta

def extract_sales_data(**context):
    """从数据库提取销售数据"""
    # 模拟数据提取过程
    print("提取销售数据...")
    # 实际实现会连接数据库并提取数据
    return "sales_data_extracted"

def transform_sales_data(**context):
    """转换销售数据"""
    # 获取上游任务的输出
    ti = context['task_instance']
    extracted_data = ti.xcom_pull(task_ids='extract_sales_data')
    
    print(f"转换数据: {extracted_data}")
    # 实际实现会进行数据清洗和转换
    return "sales_data_transformed"

def load_to_warehouse(**context):
    """加载数据到数据仓库"""
    ti = context['task_instance']
    transformed_data = ti.xcom_pull(task_ids='transform_sales_data')
    
    print(f"加载数据到仓库: {transformed_data}")
    # 实际实现会将数据加载到数据仓库

# DAG定义
dag = DAG(
    'ecommerce_data_pipeline',
    default_args={
        'owner': 'data-team',
        'depends_on_past': False,
        'start_date': datetime(2023, 1, 1),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
    },
    description='电商数据管道',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['ecommerce', 'etl', 'production']
)

# 任务定义
extract_task = PythonOperator(
    task_id='extract_sales_data',
    python_callable=extract_sales_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_sales_data',
    python_callable=transform_sales_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    dag=dag
)

# 设置任务依赖
extract_task >> transform_task >> load_task
```

## 5. 安全与合规

### 5.1 访问控制最佳实践

```python
# 基于角色的访问控制配置示例
from airflow.models import DagBag
from airflow.www.security import AirflowSecurityManager

class CustomSecurityManager(AirflowSecurityManager):
    """自定义安全管理员"""
    
    def init_role(self, role_name, perms):
        """初始化角色"""
        # 创建自定义角色
        role = self.find_role(role_name)
        if not role:
            role = self.add_role(role_name)
        
        # 分配权限
        for perm in perms:
            self.add_permission_to_role(role, perm)
    
    def is_authorized_dag(self, dag_id, user=None):
        """检查用户是否有权访问DAG"""
        if not user:
            user = self.current_user
        
        # 获取用户角色
        user_roles = [role.name for role in user.roles]
        
        # 根据角色确定访问权限
        if 'Admin' in user_roles:
            return True
        elif 'DataEngineer' in user_roles and dag_id.startswith('etl_'):
            return True
        elif 'Analyst' in user_roles and dag_id.startswith('report_'):
            return True
        else:
            return False

# 角色权限配置
roles_permissions = {
    'Admin': [
        'can_read',
        'can_edit',
        'can_delete',
        'can_create'
    ],
    'DataEngineer': [
        'can_read',
        'can_edit'
    ],
    'Analyst': [
        'can_read'
    ],
    'Viewer': [
        'can_read'
    ]
}
```

## 6. 监控与运维

### 6.1 关键指标监控

```python
# 监控指标收集脚本示例
import requests
import json
from datetime import datetime

def collect_airflow_metrics(webserver_url, auth=None):
    """收集Airflow关键指标"""
    metrics = {}
    
    try:
        # 收集DAG状态指标
        dag_stats_url = f"{webserver_url}/api/v1/dags"
        response = requests.get(dag_stats_url, auth=auth)
        if response.status_code == 200:
            dags_data = response.json()
            metrics['total_dags'] = len(dags_data.get('dags', []))
            
            # 统计各状态的DAG数量
            dag_states = {}
            for dag in dags_data.get('dags', []):
                state = dag.get('is_paused', False)
                dag_states[state] = dag_states.get(state, 0) + 1
            metrics['dag_states'] = dag_states
        
        # 收集任务实例指标
        task_stats_url = f"{webserver_url}/api/v1/taskInstances"
        response = requests.get(task_stats_url, auth=auth)
        if response.status_code == 200:
            tasks_data = response.json()
            metrics['total_tasks'] = len(tasks_data.get('task_instances', []))
            
            # 统计各状态的任务数量
            task_states = {}
            for task in tasks_data.get('task_instances', []):
                state = task.get('state')
                task_states[state] = task_states.get(state, 0) + 1
            metrics['task_states'] = task_states
            
    except Exception as e:
        print(f"收集指标时出错: {e}")
    
    return metrics

# 使用示例
# metrics = collect_airflow_metrics('http://localhost:8080', ('admin', 'admin'))
# print(json.dumps(metrics, indent=2))
```

### 6.2 自动化运维脚本

```bash
#!/bin/bash

# Airflow健康检查脚本
# airflow_health_check.sh

set -e

# 配置变量
AIRFLOW_HOME="/opt/airflow"
LOG_FILE="/var/log/airflow/health_check.log"
ALERT_EMAIL="admin@example.com"

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# 检查Airflow服务状态
check_services() {
    log "检查Airflow服务状态..."
    
    # 检查Webserver
    if pgrep -f "airflow webserver" > /dev/null; then
        log "Webserver: 运行中"
    else
        log "Webserver: 未运行"
        return 1
    fi
    
    # 检查Scheduler
    if pgrep -f "airflow scheduler" > /dev/null; then
        log "Scheduler: 运行中"
    else
        log "Scheduler: 未运行"
        return 1
    fi
    
    # 检查Workers (如果使用Celery)
    worker_count=$(pgrep -f "airflow worker" | wc -l)
    if [ $worker_count -gt 0 ]; then
        log "Workers: 运行中 ($worker_count 个进程)"
    else
        log "Workers: 未运行"
    fi
}

# 检查数据库连接
check_database() {
    log "检查数据库连接..."
    
    # 使用Airflow命令检查数据库
    if airflow db check > /dev/null 2>&1; then
        log "数据库连接: 正常"
    else
        log "数据库连接: 异常"
        return 1
    fi
}

# 检查DAG状态
check_dag_status() {
    log "检查DAG状态..."
    
    # 检查失败的任务
    failed_tasks=$(airflow tasks states-for-dag-run example_dag $(date -d "1 day ago" +%Y-%m-%d) | grep -c failed || echo "0")
    if [ "$failed_tasks" -gt 0 ]; then
        log "警告: 发现 $failed_tasks 个失败的任务"
        # 发送告警邮件
        echo "Airflow健康检查发现失败任务" | mail -s "Airflow告警" $ALERT_EMAIL
    else
        log "DAG状态: 正常"
    fi
}

# 检查磁盘空间
check_disk_space() {
    log "检查磁盘空间..."
    
    # 检查根分区使用率
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        log "警告: 磁盘使用率过高 (${disk_usage}%)"
        echo "磁盘使用率过高: ${disk_usage}%" | mail -s "磁盘空间告警" $ALERT_EMAIL
    else
        log "磁盘空间: 正常 (${disk_usage}%)"
    fi
}

# 主函数
main() {
    log "开始Airflow健康检查..."
    
    # 执行各项检查
    if check_services && check_database && check_dag_status && check_disk_space; then
        log "所有检查通过，Airflow运行正常"
        exit 0
    else
        log "健康检查发现问题"
        exit 1
    fi
}

# 执行主函数
main
```

这些学习材料涵盖了生产环境中使用Airflow的最佳实践，包括架构设计、安全配置、性能调优、故障排除、行业案例和监控运维等方面的内容。通过学习这些材料，您将能够更好地在生产环境中部署和管理Airflow。