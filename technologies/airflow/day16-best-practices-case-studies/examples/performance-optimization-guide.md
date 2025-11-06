# Apache Airflow 性能优化指南

## 1. 概述

### 1.1 目的
本文档旨在为Apache Airflow提供全面的性能优化指南，涵盖架构优化、配置调优、任务优化、资源管理、数据库优化、监控分析等方面，帮助提升Airflow在生产环境中的执行效率和稳定性。

### 1.2 适用范围
本指南适用于所有需要优化Apache Airflow性能的项目，包括但不限于：
- 大规模DAG部署（数百个DAG）
- 高频任务调度（每分钟数千个任务）
- 复杂依赖关系的任务流
- 资源受限的运行环境

### 1.3 性能优化目标
- 减少DAG解析时间
- 提高任务调度效率
- 降低资源消耗
- 缩短任务执行延迟
- 提升系统吞吐量

## 2. 架构优化

### 2.1 执行器选择与配置

#### 2.1.1 LocalExecutor优化
```python
# airflow.cfg - LocalExecutor配置优化
[core]
executor = LocalExecutor
parallelism = 32  # 根据CPU核心数调整
max_active_runs_per_dag = 16
max_active_tasks_per_dag = 16

[celery]
# 当使用LocalExecutor时，这些配置可忽略
worker_concurrency = 16
worker_prefetch_multiplier = 1
task_acks_late = True

[scheduler]
# 调度器优化
scheduler_heartbeat_sec = 5
scheduler_zombie_task_detection = True
clean_tombstoned_dag_runs = True
use_row_level_locking = True
max_tis_per_query = 16
```

#### 2.1.2 CeleryExecutor优化
```python
# airflow.cfg - CeleryExecutor配置优化
[core]
executor = CeleryExecutor
parallelism = 32
max_active_runs_per_dag = 16

[celery]
broker_url = redis://redis:6379/0
result_backend = db+postgresql://airflow:password@postgres:5432/airflow
worker_concurrency = 16
worker_prefetch_multiplier = 1  # 避免任务预取过多
task_acks_late = True  # 任务执行后再确认
worker_max_tasks_per_child = 1000  # 防止内存泄漏
worker_log_server_enabled = False  # 禁用日志服务器减少开销

[scheduler]
scheduler_heartbeat_sec = 5
max_tis_per_query = 32
processor_poll_interval = 1
```

#### 2.1.3 KubernetesExecutor优化
```python
# airflow.cfg - KubernetesExecutor配置优化
[core]
executor = KubernetesExecutor

[kubernetes]
# Kubernetes配置优化
pod_template_file = /opt/airflow/pod_templates/default_pod_template.yaml
worker_container_repository = company/airflow-worker
worker_container_tag = latest
delete_worker_pods = True
delete_worker_pods_on_failure = False
worker_pods_creation_batch_size = 5
multi_namespace_mode = False

# 资源限制
worker_resources = {
    "request_cpu": "500m",
    "request_memory": "1Gi",
    "limit_cpu": "1",
    "limit_memory": "2Gi"
}

# 环境变量优化
airflow_configmap = airflow-config
airflow_local_settings_configmap = airflow-local-settings
```

### 2.2 组件分离部署

#### 2.2.1 独立数据库部署
```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:13
          env:
            - name: POSTGRES_DB
              value: "airflow"
            - name: POSTGRES_USER
              value: "airflow"
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
          ports:
            - containerPort: 5432
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "4Gi"
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
```

#### 2.2.2 独立Redis部署
```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:6-alpine
          command:
            - "redis-server"
          args:
            - "--maxmemory"
            - "2gb"
            - "--maxmemory-policy"
            - "allkeys-lru"
            - "--save"
            - ""
          ports:
            - containerPort: 6379
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              cpu: "1"
              memory: "2Gi"
          volumeMounts:
            - name: redis-storage
              mountPath: /data
      volumes:
        - name: redis-storage
          emptyDir: {}
```

### 2.3 负载均衡和扩展

#### 2.3.1 Web Server水平扩展
```yaml
# webserver-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airflow-webserver-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airflow-webserver
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
```

#### 2.3.2 Worker自动扩缩容
```yaml
# worker-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airflow-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airflow-worker
  minReplicas: 5
  maxReplicas: 50
  metrics:
    # 基于CPU使用率
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
          
    # 基于自定义指标（任务队列长度）
    - type: Pods
      pods:
        metric:
          name: airflow_task_queue_length
        target:
          type: AverageValue
          averageValue: "10"
          
    # 基于内存使用率
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## 3. 配置调优

### 3.1 核心配置优化

#### 3.1.1 并行度配置
```ini
[core]
# 最大并行任务数
parallelism = 32

# 每个DAG的最大活跃运行数
max_active_runs_per_dag = 16

# 每个DAG的最大活跃任务数
max_active_tasks_per_dag = 16

# DAG文件处理并发数
dagbag_import_timeout = 30
dag_file_processor_timeout = 50

# 任务重试配置
default_task_retries = 3
default_task_retry_delay = 300
```

#### 3.1.2 调度器配置优化
```ini
[scheduler]
# 调度器心跳间隔
scheduler_heartbeat_sec = 5

# 使用行级锁定提高并发性能
use_row_level_locking = True

# 每次查询的最大任务实例数
max_tis_per_query = 32

# 处理器轮询间隔
processor_poll_interval = 1

# 僵尸任务检测
scheduler_zombie_task_detection = True
zombie_task_threshold = 300

# 清理墓碑DAG运行
clean_tombstoned_dag_runs = True

# DAG处理超时
dag_dir_list_interval = 300
```

#### 3.1.3 数据库连接池优化
```python
# database_pool_config.py
# 数据库连接池配置

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import logging

class OptimizedDatabasePool:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self._create_optimized_engine()
        
    def _create_optimized_engine(self):
        """创建优化的数据库引擎"""
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=20,           # 连接池大小
            max_overflow=30,        # 最大溢出连接数
            pool_pre_ping=True,     # 连接前检查
            pool_recycle=3600,      # 连接回收时间(秒)
            pool_timeout=30,        # 获取连接超时时间
            echo=False              # 禁用SQL日志
        )
        
    def get_optimized_connection(self):
        """获取优化的数据库连接"""
        try:
            connection = self.engine.connect()
            # 设置连接参数优化
            connection.execute("SET statement_timeout = 30000")  # 30秒语句超时
            connection.execute("SET lock_timeout = 10000")       # 10秒锁超时
            return connection
        except Exception as e:
            logging.error(f"获取数据库连接失败: {e}")
            raise

# 使用示例
def configure_airflow_database_pool():
    """配置Airflow数据库连接池"""
    db_url = "postgresql://airflow:password@postgres:5432/airflow"
    pool = OptimizedDatabasePool(db_url)
    return pool.engine
```

### 3.2 内存和CPU优化

#### 3.2.1 JVM参数优化（如果使用Java组件）
```bash
# jvm_options.sh
# JVM参数优化

export JAVA_OPTS="-Xms2g -Xmx4g \
                  -XX:+UseG1GC \
                  -XX:MaxGCPauseMillis=200 \
                  -XX:+UnlockExperimentalVMOptions \
                  -XX:+UseStringDeduplication \
                  -XX:+OptimizeStringConcat \
                  -XX:+UseCompressedOops \
                  -XX:NewRatio=1 \
                  -XX:SurvivorRatio=8 \
                  -XX:MaxTenuringThreshold=15 \
                  -XX:+CMSParallelRemarkEnabled \
                  -XX:+CMSScavengeBeforeRemark \
                  -XX:CMSInitiatingOccupancyFraction=70 \
                  -XX:+UseCMSInitiatingOccupancyOnly"
```

#### 3.2.2 Python进程优化
```python
# python_optimization.py
# Python进程优化

import gc
import sys
import os

def optimize_python_runtime():
    """优化Python运行时"""
    # 调整垃圾回收阈值
    gc.set_threshold(700, 10, 10)
    
    # 禁用调试模式
    if hasattr(sys, 'settrace'):
        sys.settrace(None)
        
    # 优化导入缓存
    sys.dont_write_bytecode = True
    
    # 设置Python缓冲区
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # 优化内存分配
    os.environ['MALLOC_ARENA_MAX'] = '2'
    
    print("Python运行时优化完成")

# 在Airflow启动时调用
optimize_python_runtime()
```

### 3.3 日志配置优化

#### 3.3.1 异步日志处理
```python
# async_logging.py
# 异步日志配置

import logging
import logging.handlers
import queue
import threading

class AsyncLogHandler(logging.Handler):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.log_queue = queue.Queue(-1)
        self.thread = threading.Thread(target=self._process_logs)
        self.thread.daemon = True
        self.thread.start()
        
    def emit(self, record):
        try:
            self.log_queue.put_nowait(record)
        except queue.Full:
            pass
            
    def _process_logs(self):
        while True:
            try:
                record = self.log_queue.get(timeout=1)
                self.handler.emit(record)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

# 配置异步日志
def configure_async_logging():
    """配置异步日志"""
    # 创建文件处理器
    file_handler = logging.FileHandler('/var/log/airflow/app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # 包装为异步处理器
    async_handler = AsyncLogHandler(file_handler)
    
    # 应用到根日志记录器
    root_logger = logging.getLogger()
    root_logger.addHandler(async_handler)
    root_logger.setLevel(logging.INFO)

configure_async_logging()
```

#### 3.3.2 日志轮转配置
```ini
[logging]
# 日志轮转配置
base_log_folder = /var/log/airflow
remote_base_log_folder = 

# 日志文件大小限制
log_rotation = True
log_rotation_max_file_size = 100MB
log_rotation_backup_count = 5

# 任务日志配置
task_log_reader = task
task_log_prefix_template = {{ti.dag_id}}/{{ti.task_id}}/{{ts}}/{{try_number}}.log

# Web Server日志
webserver_log_file = /var/log/airflow/webserver.log
webserver_log_format = [%%(asctime)s] {%%(filename)s:%%(lineno)d} %%(levelname)s - %%(message)s
webserver_log_format_with_thread_name = [%%(asctime)s] {%%(filename)s:%%(lineno)d} %%(threadName)s %%(levelname)s - %%(message)s
```

## 4. DAG优化

### 4.1 DAG结构优化

#### 4.1.1 减少DAG复杂度
```python
# optimized_dag_structure.py
# 优化的DAG结构示例

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta

# 使用默认参数减少重复配置
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建DAG时启用优化选项
dag = DAG(
    'optimized_data_pipeline',
    default_args=default_args,
    description='优化的数据处理管道',
    schedule_interval=timedelta(hours=1),
    catchup=False,  # 禁用回填以减少调度开销
    max_active_runs=1,  # 限制同时运行的实例数
    dagrun_timeout=timedelta(hours=2),  # 设置DAG运行超时
    tags=['data', 'optimization'],
)

# 使用DummyOperator作为分组标记
start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

# 优化的任务定义
def process_data(**context):
    """数据处理函数"""
    # 实现具体的业务逻辑
    pass

# 使用PythonOperator而不是复杂的自定义Operator
process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag,
)

# 简化依赖关系
start >> process_task >> end
```

#### 4.1.2 DAG解析优化
```python
# dag_parsing_optimization.py
# DAG解析优化

import os
from airflow import DAG
from airflow.utils.dag_cycle_tester import check_cycle

# 避免在全局作用域执行耗时操作
def create_dag():
    """延迟创建DAG"""
    dag = DAG(
        'optimized_dag',
        start_date=datetime(2023, 1, 1),
        schedule_interval='@daily',
        catchup=False,
    )
    
    # 只在需要时才执行复杂初始化
    if os.environ.get('AIRFLOW_ENV') == 'production':
        # 生产环境特定配置
        dag.max_active_runs = 1
    else:
        # 开发环境配置
        dag.max_active_runs = 3
        
    return dag

# 使用工厂模式创建DAG
dag = create_dag()

# 避免循环依赖
def check_dag_cycles(dag):
    """检查DAG循环依赖"""
    try:
        check_cycle(dag)
        return True
    except Exception as e:
        print(f"DAG存在循环依赖: {e}")
        return False
```

### 4.2 任务优化

#### 4.2.1 任务批处理
```python
# task_batching.py
# 任务批处理优化

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def batch_process_items(items_batch, **context):
    """批量处理项目"""
    processed_count = 0
    
    for item in items_batch:
        try:
            # 处理单个项目
            process_single_item(item)
            processed_count += 1
        except Exception as e:
            print(f"处理项目失败 {item}: {e}")
            # 根据需要决定是否继续处理其他项目
            
    print(f"批量处理完成，共处理 {processed_count}/{len(items_batch)} 个项目")
    return processed_count

def process_single_item(item):
    """处理单个项目"""
    # 实现具体处理逻辑
    pass

# 分批处理大量数据
def create_batched_dag():
    dag = DAG(
        'batched_data_processing',
        start_date=datetime(2023, 1, 1),
        schedule_interval='@hourly',
        catchup=False,
    )
    
    # 将大数据集分成小批次
    data_batches = [
        list(range(i, min(i+100, 1000))) 
        for i in range(0, 1000, 100)
    ]
    
    for i, batch in enumerate(data_batches):
        task = PythonOperator(
            task_id=f'process_batch_{i}',
            python_callable=batch_process_items,
            op_kwargs={'items_batch': batch},
            dag=dag,
        )
        
    return dag

dag = create_batched_dag()
```

#### 4.2.2 任务依赖优化
```python
# task_dependency_optimization.py
# 任务依赖优化

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

def lightweight_dependency_check(**context):
    """轻量级依赖检查"""
    # 快速检查上游任务是否成功
    # 避免执行重量级操作
    return "dependency_check_passed"

def heavy_data_processing(**context):
    """重量级数据处理"""
    # 实际的数据处理逻辑
    pass

# 使用TriggerDagRunOperator解耦复杂依赖
dag = DAG(
    'complex_workflow',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
)

# 轻量级依赖检查
dependency_check = PythonOperator(
    task_id='dependency_check',
    python_callable=lightweight_dependency_check,
    dag=dag,
)

# 触发另一个DAG处理复杂逻辑
trigger_heavy_processing = TriggerDagRunOperator(
    task_id='trigger_heavy_processing',
    trigger_dag_id='heavy_data_processing_dag',
    dag=dag,
)

dependency_check >> trigger_heavy_processing
```

### 4.3 资源管理优化

#### 4.3.1 动态资源分配
```python
# dynamic_resource_allocation.py
# 动态资源分配

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime

def get_dynamic_resources(task_type):
    """根据任务类型动态获取资源"""
    resource_mapping = {
        'light_task': {'cpu': '250m', 'memory': '512Mi'},
        'medium_task': {'cpu': '500m', 'memory': '1Gi'},
        'heavy_task': {'cpu': '1', 'memory': '2Gi'},
    }
    
    return resource_mapping.get(task_type, resource_mapping['medium_task'])

def adaptive_task_execution(**context):
    """自适应任务执行"""
    task_id = context['task_instance'].task_id
    task_type = Variable.get(f"task_type_{task_id}", default_var='medium_task')
    
    resources = get_dynamic_resources(task_type)
    print(f"为任务 {task_id} 分配资源: {resources}")
    
    # 根据资源需求执行相应逻辑
    # 这里可以集成到KubernetesExecutor中

dag = DAG(
    'adaptive_resource_management',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@hourly',
    catchup=False,
)

adaptive_task = PythonOperator(
    task_id='adaptive_task',
    python_callable=adaptive_task_execution,
    dag=dag,
)
```

#### 4.3.2 缓存和复用优化
```python
# caching_optimization.py
# 缓存优化

import hashlib
import pickle
from functools import wraps
from airflow.hooks.base_hook import BaseHook

class AirflowCache:
    def __init__(self):
        self.cache = {}
        self.max_size = 1000
        
    def get(self, key):
        """获取缓存值"""
        return self.cache.get(key)
        
    def set(self, key, value):
        """设置缓存值"""
        if len(self.cache) >= self.max_size:
            # 简单的LRU清除策略
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            
        self.cache[key] = value
        
    def generate_key(self, func_name, *args, **kwargs):
        """生成缓存键"""
        key_string = f"{func_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_string.encode()).hexdigest()

# 全局缓存实例
cache = AirflowCache()

def cached_task(func):
    """任务缓存装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 生成缓存键
        cache_key = cache.generate_key(func.__name__, *args, **kwargs)
        
        # 尝试从缓存获取结果
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            print(f"从缓存获取结果: {cache_key}")
            return cached_result
            
        # 执行函数并缓存结果
        result = func(*args, **kwargs)
        cache.set(cache_key, result)
        print(f"缓存结果: {cache_key}")
        
        return result
    return wrapper

@cached_task
def expensive_data_lookup(lookup_key):
    """昂贵的数据查找操作"""
    # 模拟耗时操作
    import time
    time.sleep(2)
    return f"data_for_{lookup_key}"

# 在DAG中使用
def lookup_with_cache(**context):
    result = expensive_data_lookup("customer_12345")
    return result
```

## 5. 数据库优化

### 5.1 查询优化

#### 5.1.1 索引优化
```sql
-- database_indexes.sql
-- 数据库索引优化

-- 为task_instance表添加复合索引
CREATE INDEX CONCURRENTLY idx_task_instance_dag_state 
ON task_instance (dag_id, state) 
WHERE state IN ('running', 'queued');

CREATE INDEX CONCURRENTLY idx_task_instance_exec_date 
ON task_instance (execution_date DESC);

CREATE INDEX CONCURRENTLY idx_task_instance_queued_dttm 
ON task_instance (queued_dttm) 
WHERE state = 'queued';

-- 为dag_run表添加索引
CREATE INDEX CONCURRENTLY idx_dag_run_dag_state 
ON dag_run (dag_id, state) 
WHERE state IN ('running', 'queued');

CREATE INDEX CONCURRENTLY idx_dag_run_exec_date 
ON dag_run (execution_date DESC);

-- 为log表添加索引
CREATE INDEX CONCURRENTLY idx_log_dttm 
ON log (dttm DESC);

CREATE INDEX CONCURRENTLY idx_log_event 
ON log (event);
```

#### 5.1.2 查询语句优化
```python
# optimized_queries.py
# 优化的数据库查询

from sqlalchemy import text
from airflow.utils.session import provide_session

class OptimizedQueryManager:
    @provide_session
    def get_pending_tasks(self, session=None):
        """获取待处理任务"""
        query = text("""
            SELECT ti.task_id, ti.dag_id, ti.execution_date
            FROM task_instance ti
            WHERE ti.state = 'queued'
            AND ti.queued_dttm < :cutoff_time
            ORDER BY ti.priority_weight DESC, ti.queued_dttm ASC
            LIMIT :limit
        """)
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        result = session.execute(query, {
            'cutoff_time': cutoff_time,
            'limit': 100
        })
        
        return result.fetchall()
        
    @provide_session
    def get_dag_statistics(self, dag_id, session=None):
        """获取DAG统计信息"""
        query = text("""
            SELECT 
                state,
                COUNT(*) as count,
                MAX(execution_date) as latest_execution
            FROM dag_run
            WHERE dag_id = :dag_id
            GROUP BY state
        """)
        
        result = session.execute(query, {'dag_id': dag_id})
        return {row.state: row for row in result}
        
    @provide_session
    def cleanup_old_records(self, days_to_keep=30, session=None):
        """清理旧记录"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # 分批删除以避免长时间锁表
        deleted_count = 0
        while True:
            result = session.execute(text("""
                DELETE FROM log
                WHERE dttm < :cutoff_date
                LIMIT 1000
            """), {'cutoff_date': cutoff_date})
            
            if result.rowcount == 0:
                break
                
            deleted_count += result.rowcount
            session.commit()
            
        return deleted_count
```

### 5.2 连接池优化

#### 5.2.1 自定义连接池
```python
# custom_connection_pool.py
# 自定义连接池优化

import threading
import queue
import time
from contextlib import contextmanager

class CustomConnectionPool:
    def __init__(self, max_connections=20, connection_timeout=30):
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.pool = queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self.current_connections = 0
        
    def _create_connection(self):
        """创建新连接"""
        # 这里应该实际创建数据库连接
        # 简化实现
        with self.lock:
            self.current_connections += 1
            return f"connection_{self.current_connections}"
            
    def get_connection(self):
        """获取连接"""
        try:
            # 尝试从池中获取连接
            return self.pool.get_nowait()
        except queue.Empty:
            # 池为空，创建新连接
            if self.current_connections < self.max_connections:
                return self._create_connection()
            else:
                # 等待可用连接
                return self.pool.get(timeout=self.connection_timeout)
                
    def return_connection(self, connection):
        """归还连接"""
        try:
            self.pool.put_nowait(connection)
        except queue.Full:
            # 池已满，关闭连接
            self._close_connection(connection)
            
    def _close_connection(self, connection):
        """关闭连接"""
        with self.lock:
            self.current_connections -= 1
            
    @contextmanager
    def connection(self):
        """连接上下文管理器"""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.return_connection(conn)

# 使用示例
pool = CustomConnectionPool(max_connections=20)

def database_operation():
    with pool.connection() as conn:
        # 执行数据库操作
        print(f"使用连接: {conn}")
        time.sleep(0.1)  # 模拟操作
```

#### 5.2.2 连接监控
```python
# connection_monitoring.py
# 连接监控

import time
import threading
from collections import defaultdict, deque

class ConnectionMonitor:
    def __init__(self, pool):
        self.pool = pool
        self.stats = defaultdict(deque)
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            self._collect_stats()
            time.sleep(60)  # 每分钟收集一次
            
    def _collect_stats(self):
        """收集统计信息"""
        timestamp = time.time()
        stats = {
            'timestamp': timestamp,
            'pool_size': self.pool.pool.qsize(),
            'active_connections': self.pool.current_connections,
            'max_connections': self.pool.max_connections,
        }
        
        # 保存最近60分钟的统计数据
        self.stats['pool_stats'].append(stats)
        while len(self.stats['pool_stats']) > 60:
            self.stats['pool_stats'].popleft()
            
    def get_stats_summary(self):
        """获取统计摘要"""
        if not self.stats['pool_stats']:
            return {}
            
        latest = self.stats['pool_stats'][-1]
        avg_pool_size = sum(s['pool_size'] for s in self.stats['pool_stats']) / len(self.stats['pool_stats'])
        
        return {
            'current': latest,
            'average_pool_size': avg_pool_size,
            'utilization_rate': latest['active_connections'] / latest['max_connections']
        }
        
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False

# 使用示例
monitor = ConnectionMonitor(pool)
```

### 5.3 数据分区和归档

#### 5.3.1 表分区策略
```sql
-- table_partitioning.sql
-- 表分区策略

-- 创建分区表 (PostgreSQL 10+)
CREATE TABLE task_instance_partitioned (
    LIKE task_instance INCLUDING ALL
) PARTITION BY RANGE (execution_date);

-- 创建月度分区
CREATE TABLE task_instance_y2023m01 PARTITION OF task_instance_partitioned
FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');

CREATE TABLE task_instance_y2023m02 PARTITION OF task_instance_partitioned
FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

-- 为分区表创建索引
CREATE INDEX idx_ti_part_dag_state ON task_instance_partitioned (dag_id, state);
CREATE INDEX idx_ti_part_exec_date ON task_instance_partitioned (execution_date);

-- 迁移数据到分区表
INSERT INTO task_instance_partitioned SELECT * FROM task_instance;
```

#### 5.3.2 自动归档脚本
```python
# auto_archiving.py
# 自动归档脚本

import logging
from datetime import datetime, timedelta
from airflow.utils.db import provide_session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class DataArchiver:
    def __init__(self, archive_threshold_days=90):
        self.archive_threshold_days = archive_threshold_days
        
    @provide_session
    def archive_old_task_instances(self, session=None):
        """归档旧的任务实例"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.archive_threshold_days)
        
        try:
            # 将旧数据移动到归档表
            archive_query = text("""
                INSERT INTO task_instance_archive
                SELECT * FROM task_instance
                WHERE execution_date < :cutoff_date
                AND state IN ('success', 'failed')
            """)
            
            result = session.execute(archive_query, {'cutoff_date': cutoff_date})
            archived_count = result.rowcount
            
            # 删除已归档的数据
            delete_query = text("""
                DELETE FROM task_instance
                WHERE execution_date < :cutoff_date
                AND state IN ('success', 'failed')
            """)
            
            session.execute(delete_query, {'cutoff_date': cutoff_date})
            session.commit()
            
            logger.info(f"归档了 {archived_count} 条任务实例记录")
            return archived_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"归档任务实例失败: {e}")
            raise
            
    @provide_session
    def archive_old_logs(self, session=None):
        """归档旧的日志"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.archive_threshold_days)
        
        try:
            # 归档日志数据
            archive_query = text("""
                INSERT INTO log_archive
                SELECT * FROM log
                WHERE dttm < :cutoff_date
            """)
            
            result = session.execute(archive_query, {'cutoff_date': cutoff_date})
            archived_count = result.rowcount
            
            # 删除已归档的日志
            delete_query = text("""
                DELETE FROM log
                WHERE dttm < :cutoff_date
            """)
            
            session.execute(delete_query, {'cutoff_date': cutoff_date})
            session.commit()
            
            logger.info(f"归档了 {archived_count} 条日志记录")
            return archived_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"归档日志失败: {e}")
            raise

# 定期执行归档
def run_periodic_archiving():
    """定期执行数据归档"""
    archiver = DataArchiver(archive_threshold_days=90)
    
    try:
        task_count = archiver.archive_old_task_instances()
        log_count = archiver.archive_old_logs()
        
        logger.info(f"数据归档完成: {task_count} 个任务实例, {log_count} 条日志")
        
    except Exception as e:
        logger.error(f"数据归档过程中出现错误: {e}")

# 可以通过Airflow的DAG定期执行此函数
```

## 6. 监控和分析

### 6.1 性能指标监控

#### 6.1.1 关键性能指标(KPIs)
```python
# performance_metrics.py
# 性能指标监控

import time
import logging
from datetime import datetime
from collections import defaultdict, deque
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
from airflow.utils.session import provide_session

logger = logging.getLogger(__name__)

class PerformanceMetricsCollector:
    def __init__(self):
        self.metrics_history = defaultdict(deque)
        self.max_history_size = 1000
        
    def collect_dag_metrics(self, dag_id):
        """收集DAG性能指标"""
        start_time = time.time()
        
        try:
            metrics = self._calculate_dag_metrics(dag_id)
            collection_time = time.time() - start_time
            
            # 添加收集时间到指标中
            metrics['collection_time'] = collection_time
            metrics['timestamp'] = datetime.utcnow()
            
            # 保存历史数据
            self._store_metrics_history(dag_id, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"收集DAG {dag_id} 性能指标失败: {e}")
            return {}
            
    @provide_session
    def _calculate_dag_metrics(self, dag_id, session=None):
        """计算DAG指标"""
        # 计算最近7天的DAG运行统计
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # 成功率
        total_runs = session.query(DagRun).filter(
            DagRun.dag_id == dag_id,
            DagRun.execution_date >= seven_days_ago
        ).count()
        
        successful_runs = session.query(DagRun).filter(
            DagRun.dag_id == dag_id,
            DagRun.state == State.SUCCESS,
            DagRun.execution_date >= seven_days_ago
        ).count()
        
        success_rate = successful_runs / total_runs if total_runs > 0 else 0
        
        # 平均运行时间
        avg_duration = session.query(
            func.avg(func.extract('epoch', DagRun.end_date - DagRun.start_date))
        ).filter(
            DagRun.dag_id == dag_id,
            DagRun.state == State.SUCCESS,
            DagRun.execution_date >= seven_days_ago
        ).scalar() or 0
        
        # 任务失败率
        total_tasks = session.query(TaskInstance).filter(
            TaskInstance.dag_id == dag_id,
            TaskInstance.execution_date >= seven_days_ago
        ).count()
        
        failed_tasks = session.query(TaskInstance).filter(
            TaskInstance.dag_id == dag_id,
            TaskInstance.state == State.FAILED,
            TaskInstance.execution_date >= seven_days_ago
        ).count()
        
        task_failure_rate = failed_tasks / total_tasks if total_tasks > 0 else 0
        
        return {
            'dag_id': dag_id,
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'success_rate': round(success_rate, 4),
            'average_duration_seconds': round(avg_duration, 2),
            'total_tasks': total_tasks,
            'failed_tasks': failed_tasks,
            'task_failure_rate': round(task_failure_rate, 4)
        }
        
    def _store_metrics_history(self, dag_id, metrics):
        """存储指标历史数据"""
        key = f"dag_{dag_id}_metrics"
        self.metrics_history[key].append(metrics)
        
        # 保持历史数据大小限制
        while len(self.metrics_history[key]) > self.max_history_size:
            self.metrics_history[key].popleft()
            
    def get_metrics_trend(self, dag_id, hours=24):
        """获取指标趋势"""
        key = f"dag_{dag_id}_metrics"
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        trend_data = [
            metrics for metrics in self.metrics_history[key]
            if metrics['timestamp'] >= cutoff_time
        ]
        
        return trend_data

# 使用示例
collector = PerformanceMetricsCollector()

def monitor_dag_performance():
    """监控DAG性能"""
    dag_ids = ['data_pipeline_daily', 'report_generation_weekly', 'ml_training_hourly']
    
    for dag_id in dag_ids:
        metrics = collector.collect_dag_metrics(dag_id)
        if metrics:
            print(f"DAG {dag_id} 性能指标:")
            for key, value in metrics.items():
                if key not in ['dag_id', 'timestamp']:
                    print(f"  {key}: {value}")
```

#### 6.1.2 实时性能监控
```python
# real_time_monitoring.py
# 实时性能监控

import psutil
import time
import threading
import logging
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class RealTimePerformanceMonitor:
    def __init__(self, sample_interval=1):
        self.sample_interval = sample_interval
        self.monitoring = False
        self.performance_data = deque(maxlen=3600)  # 保存1小时的数据
        self.monitor_thread = None
        
    def start_monitoring(self):
        """开始监控"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("实时性能监控已启动")
            
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("实时性能监控已停止")
        
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.performance_data.append(metrics)
                time.sleep(self.sample_interval)
            except Exception as e:
                logger.error(f"性能监控过程中出现错误: {e}")
                time.sleep(self.sample_interval)
                
    def _collect_system_metrics(self):
        """收集系统指标"""
        return {
            'timestamp': datetime.utcnow(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'network_bytes_sent': psutil.net_io_counters().bytes_sent,
            'network_bytes_recv': psutil.net_io_counters().bytes_recv,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
        }
        
    def get_current_performance(self):
        """获取当前性能数据"""
        if self.performance_data:
            return self.performance_data[-1]
        return {}
        
    def get_performance_summary(self, minutes=5):
        """获取性能摘要"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_data = [
            data for data in self.performance_data
            if data['timestamp'] >= cutoff_time
        ]
        
        if not recent_data:
            return {}
            
        # 计算平均值
        avg_cpu = sum(d['cpu_percent'] for d in recent_data) / len(recent_data)
        avg_memory = sum(d['memory_percent'] for d in recent_data) / len(recent_data)
        avg_disk = sum(d['disk_usage_percent'] for d in recent_data) / len(recent_data)
        
        # 获取最大值
        max_cpu = max(d['cpu_percent'] for d in recent_data)
        max_memory = max(d['memory_percent'] for d in recent_data)
        
        return {
            'period_minutes': minutes,
            'sample_count': len(recent_data),
            'average_cpu_percent': round(avg_cpu, 2),
            'average_memory_percent': round(avg_memory, 2),
            'average_disk_percent': round(avg_disk, 2),
            'peak_cpu_percent': max_cpu,
            'peak_memory_percent': max_memory
        }

# 使用示例
monitor = RealTimePerformanceMonitor(sample_interval=5)
monitor.start_monitoring()

# 在需要的地方获取性能数据
def check_system_performance():
    """检查系统性能"""
    current = monitor.get_current_performance()
    summary = monitor.get_performance_summary(minutes=10)
    
    print(f"当前系统性能: {current}")
    print(f"10分钟性能摘要: {summary}")
    
    # 检查是否需要告警
    if current.get('cpu_percent', 0) > 80:
        logger.warning(f"CPU使用率过高: {current['cpu_percent']}%")
        
    if current.get('memory_percent', 0) > 85:
        logger.warning(f"内存使用率过高: {current['memory_percent']}%")
```

### 6.2 性能分析工具

#### 6.2.1 任务执行时间分析
```python
# task_execution_analysis.py
# 任务执行时间分析

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from airflow.models import TaskInstance
from airflow.utils.session import provide_session
from airflow.utils.state import State

class TaskExecutionAnalyzer:
    def __init__(self):
        self.analysis_results = {}
        
    @provide_session
    def analyze_task_performance(self, dag_id, days=30, session=None):
        """分析任务执行性能"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 查询任务执行数据
        query = session.query(
            TaskInstance.task_id,
            TaskInstance.start_date,
            TaskInstance.end_date,
            TaskInstance.state,
            TaskInstance.duration
        ).filter(
            TaskInstance.dag_id == dag_id,
            TaskInstance.start_date >= cutoff_date
        )
        
        # 转换为DataFrame进行分析
        df = pd.read_sql(query.statement, query.session.bind)
        
        if df.empty:
            return {}
            
        # 数据预处理
        df['duration_seconds'] = df['duration']
        df['execution_date'] = df['start_date'].dt.date
        df['hour_of_day'] = df['start_date'].dt.hour
        
        # 计算基本统计信息
        stats = {
            'total_executions': len(df),
            'successful_executions': len(df[df['state'] == State.SUCCESS]),
            'failed_executions': len(df[df['state'] == State.FAILED]),
            'average_duration': df['duration_seconds'].mean(),
            'median_duration': df['duration_seconds'].median(),
            'std_duration': df['duration_seconds'].std(),
            'min_duration': df['duration_seconds'].min(),
            'max_duration': df['duration_seconds'].max()
        }
        
        # 成功率计算
        stats['success_rate'] = stats['successful_executions'] / stats['total_executions'] if stats['total_executions'] > 0 else 0
        
        # 按任务ID分组分析
        task_stats = df.groupby('task_id').agg({
            'duration_seconds': ['count', 'mean', 'median', 'std', 'min', 'max'],
            'state': lambda x: (x == State.SUCCESS).sum() / len(x) if len(x) > 0 else 0
        }).round(2)
        
        # 重命名列
        task_stats.columns = [
            'execution_count', 'avg_duration', 'median_duration', 
            'std_duration', 'min_duration', 'max_duration', 'success_rate'
        ]
        
        # 按小时分析
        hourly_stats = df.groupby('hour_of_day').agg({
            'duration_seconds': 'mean',
            'state': lambda x: (x == State.SUCCESS).sum() / len(x) if len(x) > 0 else 0
        }).round(2)
        
        hourly_stats.columns = ['avg_duration', 'success_rate']
        
        # 识别异常执行
        outliers = self._identify_outliers(df)
        
        analysis_result = {
            'dag_id': dag_id,
            'analysis_period_days': days,
            'overall_stats': stats,
            'task_breakdown': task_stats.to_dict(),
            'hourly_patterns': hourly_stats.to_dict(),
            'outliers': outliers,
            'generated_at': datetime.utcnow()
        }
        
        self.analysis_results[dag_id] = analysis_result
        return analysis_result
        
    def _identify_outliers(self, df, threshold=2):
        """识别异常执行"""
        if df.empty:
            return []
            
        # 使用Z-score方法识别异常值
        mean_duration = df['duration_seconds'].mean()
        std_duration = df['duration_seconds'].std()
        
        if std_duration == 0:
            return []
            
        df['z_score'] = abs(df['duration_seconds'] - mean_duration) / std_duration
        outliers = df[df['z_score'] > threshold]
        
        return outliers[['task_id', 'start_date', 'duration_seconds', 'z_score']].to_dict('records')
        
    def generate_performance_report(self, dag_id):
        """生成性能报告"""
        if dag_id not in self.analysis_results:
            self.analyze_task_performance(dag_id)
            
        result = self.analysis_results[dag_id]
        if not result:
            return "No data available for analysis"
            
        report = f"""
# Apache Airflow DAG性能分析报告

## 基本信息
- DAG ID: {result['dag_id']}
- 分析周期: {result['analysis_period_days']} 天
- 报告生成时间: {result['generated_at']}

## 整体性能统计
- 总执行次数: {result['overall_stats']['total_executions']}
- 成功执行次数: {result['overall_stats']['successful_executions']}
- 失败执行次数: {result['overall_stats']['failed_executions']}
- 成功率: {result['overall_stats']['success_rate']:.2%}
- 平均执行时间: {result['overall_stats']['average_duration']:.2f} 秒
- 中位数执行时间: {result['overall_stats']['median_duration']:.2f} 秒
- 执行时间标准差: {result['overall_stats']['std_duration']:.2f} 秒

## 任务详细分析
"""
        
        for task_id, stats in result['task_breakdown'].items():
            report += f"""
### 任务: {task_id}
- 执行次数: {stats['execution_count']}
- 平均执行时间: {stats['avg_duration']:.2f} 秒
- 成功率: {stats['success_rate']:.2%}
"""
            
        return report

# 使用示例
analyzer = TaskExecutionAnalyzer()

def generate_dag_performance_report(dag_id):
    """生成DAG性能报告"""
    try:
        report = analyzer.generate_performance_report(dag_id)
        print(report)
        
        # 也可以保存到文件
        with open(f'{dag_id}_performance_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
    except Exception as e:
        print(f"生成性能报告失败: {e}")
```

#### 6.2.2 资源使用分析
```python
# resource_usage_analysis.py
# 资源使用分析

import psutil
import docker
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

class ResourceUsageAnalyzer:
    def __init__(self):
        self.docker_client = docker.from_env() if self._check_docker_available() else None
        self.resource_data = []
        
    def _check_docker_available(self):
        """检查Docker是否可用"""
        try:
            docker.from_env()
            return True
        except:
            return False
            
    def collect_system_resources(self):
        """收集系统资源使用情况"""
        timestamp = datetime.utcnow()
        
        # 收集CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 收集内存使用情况
        memory = psutil.virtual_memory()
        
        # 收集磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 收集网络使用情况
        net_io = psutil.net_io_counters()
        
        resource_entry = {
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'memory_total_gb': memory.total / (1024**3),
            'memory_used_gb': memory.used / (1024**3),
            'memory_percent': memory.percent,
            'disk_total_gb': disk.total / (1024**3),
            'disk_used_gb': disk.used / (1024**3),
            'disk_percent': disk.percent,
            'network_bytes_sent_mb': net_io.bytes_sent / (1024**2),
            'network_bytes_recv_mb': net_io.bytes_recv / (1024**2)
        }
        
        self.resource_data.append(resource_entry)
        return resource_entry
        
    def collect_docker_resources(self):
        """收集Docker容器资源使用情况"""
        if not self.docker_client:
            return []
            
        containers = self.docker_client.containers.list()
        container_stats = []
        
        for container in containers:
            try:
                stats = container.stats(stream=False)
                
                # CPU使用率计算
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                
                if system_delta > 0:
                    cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100
                else:
                    cpu_percent = 0
                    
                # 内存使用情况
                memory_usage = stats['memory_stats']['usage'] / (1024**3)  # GB
                memory_limit = stats['memory_stats']['limit'] / (1024**3)  # GB
                memory_percent = (memory_usage / memory_limit) * 100 if memory_limit > 0 else 0
                
                container_stats.append({
                    'container_id': container.short_id,
                    'container_name': container.name,
                    'cpu_percent': cpu_percent,
                    'memory_usage_gb': memory_usage,
                    'memory_limit_gb': memory_limit,
                    'memory_percent': memory_percent,
                    'timestamp': datetime.utcnow()
                })
                
            except Exception as e:
                print(f"收集容器 {container.name} 资源信息失败: {e}")
                
        return container_stats
        
    def analyze_resource_trends(self, hours=24):
        """分析资源使用趋势"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_data = [
            data for data in self.resource_data
            if data['timestamp'] >= cutoff_time
        ]
        
        if not recent_data:
            return {}
            
        df = pd.DataFrame(recent_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 计算趋势统计
        trends = {
            'period_hours': hours,
            'data_points': len(df),
            'cpu_avg': df['cpu_percent'].mean(),
            'cpu_max': df['cpu_percent'].max(),
            'cpu_min': df['cpu_percent'].min(),
            'memory_avg_percent': df['memory_percent'].mean(),
            'memory_max_percent': df['memory_percent'].max(),
            'disk_avg_percent': df['disk_percent'].mean(),
            'disk_max_percent': df['disk_percent'].max()
        }
        
        return trends
        
    def generate_resource_report(self, hours=24):
        """生成资源使用报告"""
        trends = self.analyze_resource_trends(hours)
        
        if not trends:
            return "No resource data available"
            
        report = f"""
# Apache Airflow 资源使用分析报告

## 分析周期
- 时间范围: 最近 {trends['period_hours']} 小时
- 数据点数: {trends['data_points']}

## 系统资源使用情况
- CPU平均使用率: {trends['cpu_avg']:.2f}%
- CPU峰值使用率: {trends['cpu_max']:.2f}%
- 内存平均使用率: {trends['memory_avg_percent']:.2f}%
- 内存峰值使用率: {trends['memory_max_percent']:.2f}%
- 磁盘平均使用率: {trends['disk_avg_percent']:.2f}%
- 磁盘峰值使用率: {trends['disk_max_percent']:.2f}%

## 建议
"""
        
        # 根据使用率给出建议
        if trends['cpu_max'] > 80:
            report += "- CPU使用率较高，考虑增加CPU资源或优化任务\n"
            
        if trends['memory_max_percent'] > 85:
            report += "- 内存使用率较高，考虑增加内存资源或优化内存使用\n"
            
        if trends['disk_max_percent'] > 90:
            report += "- 磁盘使用率较高，考虑清理日志或增加存储空间\n"
            
        return report
        
    def plot_resource_usage(self, hours=24):
        """绘制资源使用图表"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_data = [
            data for data in self.resource_data
            if data['timestamp'] >= cutoff_time
        ]
        
        if not recent_data:
            print("没有可用的资源数据")
            return
            
        df = pd.DataFrame(recent_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('系统资源使用情况', fontsize=16)
        
        # CPU使用率
        axes[0, 0].plot(df['timestamp'], df['cpu_percent'], linewidth=1)
        axes[0, 0].set_title('CPU使用率 (%)')
        axes[0, 0].set_ylabel('百分比')
        axes[0, 0].grid(True)
        
        # 内存使用率
        axes[0, 1].plot(df['timestamp'], df['memory_percent'], linewidth=1, color='orange')
        axes[0, 1].set_title('内存使用率 (%)')
        axes[0, 1].set_ylabel('百分比')
        axes[0, 1].grid(True)
        
        # 磁盘使用率
        axes[1, 0].plot(df['timestamp'], df['disk_percent'], linewidth=1, color='green')
        axes[1, 0].set_title('磁盘使用率 (%)')
        axes[1, 0].set_ylabel('百分比')
        axes[1, 0].grid(True)
        
        # 网络流量
        axes[1, 1].plot(df['timestamp'], df['network_bytes_sent_mb'], 
                       label='发送', linewidth=1, color='blue')
        axes[1, 1].plot(df['timestamp'], df['network_bytes_recv_mb'], 
                       label='接收', linewidth=1, color='red')
        axes[1, 1].set_title('网络流量 (MB)')
        axes[1, 1].set_ylabel('兆字节')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        # 调整布局
        plt.tight_layout()
        plt.savefig('resource_usage_trends.png', dpi=300, bbox_inches='tight')
        plt.show()

# 使用示例
analyzer = ResourceUsageAnalyzer()

def monitor_and_analyze_resources():
    """监控和分析资源使用情况"""
    # 收集系统资源
    system_stats = analyzer.collect_system_resources()
    print(f"系统资源统计: {system_stats}")
    
    # 收集Docker资源（如果有Docker环境）
    if analyzer.docker_client:
        docker_stats = analyzer.collect_docker_resources()
        for stat in docker_stats:
            print(f"容器 {stat['container_name']} 资源使用: CPU {stat['cpu_percent']:.2f}%, 内存 {stat['memory_percent']:.2f}%")
    
    # 生成报告
    report = analyzer.generate_resource_report(hours=1)
    print(report)

# 定期收集资源数据
def start_resource_monitoring():
    """开始资源监控"""
    import time
    import threading
    
    def collect_loop():
        while True:
            try:
                analyzer.collect_system_resources()
                time.sleep(300)  # 每5分钟收集一次
            except Exception as e:
                print(f"资源收集失败: {e}")
                time.sleep(60)
                
    thread = threading.Thread(target=collect_loop)
    thread.daemon = True
    thread.start()
    return thread
```

## 7. 最佳实践总结

### 7.1 配置最佳实践

#### 7.1.1 环境特定配置
```python
# environment_config.py
# 环境特定配置管理

import os
from typing import Dict, Any

class EnvironmentConfig:
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.configs = self._load_environment_configs()
        
    def _load_environment_configs(self) -> Dict[str, Dict[str, Any]]:
        """加载环境特定配置"""
        return {
            'development': {
                'parallelism': 4,
                'max_active_runs_per_dag': 2,
                'scheduler_heartbeat_sec': 10,
                'log_level': 'DEBUG',
                'database_pool_size': 5,
                'worker_concurrency': 4
            },
            'staging': {
                'parallelism': 16,
                'max_active_runs_per_dag': 8,
                'scheduler_heartbeat_sec': 5,
                'log_level': 'INFO',
                'database_pool_size': 10,
                'worker_concurrency': 8
            },
            'production': {
                'parallelism': 32,
                'max_active_runs_per_dag': 16,
                'scheduler_heartbeat_sec': 5,
                'log_level': 'WARNING',
                'database_pool_size': 20,
                'worker_concurrency': 16,
                'enable_caching': True,
                'enable_monitoring': True
            }
        }
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        env_config = self.configs.get(self.environment, {})
        return env_config.get(key, default)
        
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.configs.get(self.environment, {})

# 使用示例
config = EnvironmentConfig()

# 在Airflow配置中使用
def configure_airflow_for_environment():
    """根据环境配置Airflow"""
    parallelism = config.get_config('parallelism', 8)
    max_active_runs = config.get_config('max_active_runs_per_dag', 4)
    
    print(f"配置环境: {config.environment}")
    print(f"并行度: {parallelism}")
    print(f"最大活跃运行数: {max_active_runs}")

# 在DAG中使用环境配置
def create_environment_aware_dag():
    """创建环境感知的DAG"""
    dag_config = {
        'schedule_interval': '@hourly' if config.environment == 'production' else '@daily',
        'catchup': False,
        'max_active_runs': config.get_config('max_active_runs_per_dag'),
    }
    
    return dag_config
```

#### 7.1.2 配置验证
```python
# config_validation.py
# 配置验证

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class ConfigValidator:
    def __init__(self):
        self.validation_rules = self._define_validation_rules()
        
    def _define_validation_rules(self) -> Dict[str, callable]:
        """定义验证规则"""
        return {
            'parallelism': self._validate_positive_integer,
            'max_active_runs_per_dag': self._validate_positive_integer,
            'scheduler_heartbeat_sec': self._validate_heartbeat_interval,
            'worker_concurrency': self._validate_positive_integer,
            'database_pool_size': self._validate_database_pool_size,
            'log_level': self._validate_log_level
        }
        
    def _validate_positive_integer(self, value, min_val=1, max_val=1000) -> Tuple[bool, str]:
        """验证正整数"""
        if not isinstance(value, int):
            return False, f"必须是整数，当前值: {type(value)}"
        if value < min_val or value > max_val:
            return False, f"必须在 {min_val}-{max_val} 范围内，当前值: {value}"
        return True, ""
        
    def _validate_heartbeat_interval(self, value) -> Tuple[bool, str]:
        """验证心跳间隔"""
        return self._validate_positive_integer(value, min_val=1, max_val=60)
        
    def _validate_database_pool_size(self, value) -> Tuple[bool, str]:
        """验证数据库连接池大小"""
        return self._validate_positive_integer(value, min_val=1, max_val=100)
        
    def _validate_log_level(self, value) -> Tuple[bool, str]:
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if value not in valid_levels:
            return False, f"日志级别必须是以下之一: {valid_levels}"
        return True, ""
        
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """验证配置"""
        errors = []
        
        for key, value in config.items():
            if key in self.validation_rules:
                is_valid, error_msg = self.validation_rules[key](value)
                if not is_valid:
                    errors.append(f"配置项 '{key}': {error_msg}")
                    
        return errors
        
    def validate_and_warn(self, config: Dict[str, Any]):
        """验证配置并发出警告"""
        errors = self.validate_config(config)
        
        if errors:
            for error in errors:
                logger.warning(f"配置验证警告: {error}")
                
        return len(errors) == 0

# 使用示例
validator = ConfigValidator()

def validate_airflow_config(config_dict):
    """验证Airflow配置"""
    is_valid = validator.validate_and_warn(config_dict)
    
    if is_valid:
        logger.info("所有配置验证通过")
    else:
        logger.error("配置验证失败，请检查上述警告")
        
    return is_valid

# 示例配置验证
sample_config = {
    'parallelism': 32,
    'max_active_runs_per_dag': 16,
    'scheduler_heartbeat_sec': 5,
    'worker_concurrency': 16,
    'database_pool_size': 20,
    'log_level': 'WARNING'
}

validate_airflow_config(sample_config)
```

### 7.2 运维最佳实践

#### 7.2.1 自动化运维脚本
```python
# automated_operations.py
# 自动化运维脚本

import subprocess
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

class AutomatedOperations:
    def __init__(self):
        self.operations_log = []
        
    def restart_unhealthy_components(self, component_names: List[str]) -> Dict[str, bool]:
        """重启不健康的组件"""
        results = {}
        
        for component in component_names:
            try:
                # 检查组件健康状态
                if self._is_component_healthy(component):
                    logger.info(f"组件 {component} 运行正常")
                    results[component] = True
                    continue
                    
                # 重启组件
                logger.warning(f"组件 {component} 不健康，正在重启...")
                restart_success = self._restart_component(component)
                
                if restart_success:
                    logger.info(f"组件 {component} 重启成功")
                    results[component] = True
                else:
                    logger.error(f"组件 {component} 重启失败")
                    results[component] = False
                    
            except Exception as e:
                logger.error(f"处理组件 {component} 时发生错误: {e}")
                results[component] = False
                
        return results
        
    def _is_component_healthy(self, component_name: str) -> bool:
        """检查组件健康状态"""
        try:
            # 这里应该实现具体的健康检查逻辑
            # 例如检查进程、端口、API响应等
            
            if component_name == 'webserver':
                # 检查Web Server是否响应
                result = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                     'http://localhost:8080/health'],
                    capture_output=True, text=True, timeout=10
                )
                return result.stdout.strip() == '200'
                
            elif component_name == 'scheduler':
                # 检查Scheduler进程
                result = subprocess.run(
                    ['pgrep', '-f', 'airflow scheduler'],
                    capture_output=True, text=True
                )
                return result.returncode == 0
                
            elif component_name == 'worker':
                # 检查Worker进程
                result = subprocess.run(
                    ['pgrep', '-f', 'airflow worker'],
                    capture_output=True, text=True
                )
                return result.returncode == 0
                
            return True  # 默认认为健康
            
        except Exception as e:
            logger.error(f"健康检查失败 {component_name}: {e}")
            return False
            
    def _restart_component(self, component_name: str) -> bool:
        """重启组件"""
        try:
            if component_name == 'webserver':
                subprocess.run(['airflow', 'webserver', '--daemon'], check=True)
            elif component_name == 'scheduler':
                subprocess.run(['airflow', 'scheduler', '--daemon'], check=True)
            elif component_name == 'worker':
                subprocess.run(['airflow', 'worker', '--daemon'], check=True)
                
            # 等待组件启动
            time.sleep(10)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"重启组件失败 {component_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"重启组件时发生未知错误 {component_name}: {e}")
            return False
            
    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        """清理旧日志"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # 查找并删除旧日志文件
            result = subprocess.run([
                'find', '/var/log/airflow', 
                '-type', 'f', 
                '-name', '*.log',
                '-mtime', f'+{days_to_keep}',
                '-delete'
            ], capture_output=True, text=True)
            
            deleted_count = result.returncode == 0
            logger.info(f"清理了 {deleted_count} 个旧日志文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧日志失败: {e}")
            return 0
            
    def rotate_config_backups(self, max_backups: int = 10) -> bool:
        """轮转配置备份"""
        try:
            # 创建当前配置备份
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_cmd = [
                'cp', '-r', 
                '/etc/airflow', 
                f'/etc/airflow.backup.{timestamp}'
            ]
            subprocess.run(backup_cmd, check=True)
            
            # 清理旧备份
            cleanup_cmd = [
                'find', '/etc', 
                '-name', 'airflow.backup.*',
                '-type', 'd',
                '-printf', '%T@ %p\n',
                '|', 'sort', '-n',
                '|', 'head', '-n', f'-{max_backups}',
                '|', 'cut', '-d', ' ', '-f', '2-',
                '|', 'xargs', 'rm', '-rf'
            ]
            
            subprocess.run(' '.join(cleanup_cmd), shell=True, check=True)
            
            logger.info("配置备份轮转完成")
            return True
            
        except Exception as e:
            logger.error(f"配置备份轮转失败: {e}")
            return False

# 使用示例
ops = AutomatedOperations()

def perform_daily_maintenance():
    """执行日常维护"""
    logger.info("开始执行日常维护任务")
    
    # 重启不健康的组件
    components = ['webserver', 'scheduler', 'worker']
    restart_results = ops.restart_unhealthy_components(components)
    
    # 清理旧日志
    cleaned_logs = ops.cleanup_old_logs(days_to_keep=30)
    
    # 轮转配置备份
    backup_rotated = ops.rotate_config