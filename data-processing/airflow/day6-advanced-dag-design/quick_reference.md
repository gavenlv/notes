# Day 6: 高级DAG设计快速参考指南

## 1. 工厂模式DAG设计

### 核心概念
- **任务工厂**: 创建标准化任务组件的函数
- **参数化配置**: 通过参数控制任务行为
- **模板复用**: 减少重复代码，提高一致性

### 代码模板
```python
# 基础任务工厂
def create_task_factory(dag, task_type):
    """创建特定类型任务的工厂函数"""
    def factory(task_id, **kwargs):
        if task_type == 'python':
            return PythonOperator(
                task_id=task_id,
                python_callable=kwargs.get('callable'),
                dag=dag
            )
        elif task_type == 'bash':
            return BashOperator(
                task_id=task_id,
                bash_command=kwargs.get('command'),
                dag=dag
            )
    return factory

# 使用示例
python_factory = create_task_factory(dag, 'python')
extract_task = python_factory('extract_data', callable=extract_function)
```

### 高级工厂模式
```python
class TaskFactory:
    """高级任务工厂类"""
    
    def __init__(self, dag):
        self.dag = dag
        self.registry = {}
    
    def register_task_type(self, task_type, creator_func):
        """注册新的任务类型"""
        self.registry[task_type] = creator_func
    
    def create_task(self, task_type, task_id, **kwargs):
        """创建任务"""
        if task_type not in self.registry:
            raise ValueError(f"未知的任务类型: {task_type}")
        return self.registry[task_type](task_id, **kwargs)
```

## 2. 配置驱动DAG

### YAML配置格式
```yaml
# dag_config.yaml
dag:
  id: "config_driven_pipeline"
  description: "基于配置的数据管道"
  schedule_interval: "@daily"
  default_args:
    owner: "airflow"
    start_date: "2024-01-01"

tasks:
  - id: "extract_data"
    type: "python"
    callable: "extract_function"
    parameters:
      source: "database"
    
  - id: "transform_data"
    type: "python"
    callable: "transform_function"
    depends_on: ["extract_data"]
    
  - id: "load_data"
    type: "python"
    callable: "load_function"
    depends_on: ["transform_data"]
```

### 配置解析器
```python
import yaml
from pathlib import Path

class ConfigDrivenDAGBuilder:
    """配置驱动DAG构建器"""
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self):
        """加载YAML配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def build_dag(self):
        """构建DAG"""
        dag_config = self.config['dag']
        
        dag = DAG(
            dag_id=dag_config['id'],
            description=dag_config['description'],
            schedule_interval=dag_config['schedule_interval'],
            default_args=dag_config.get('default_args', {}),
            catchup=False
        )
        
        tasks = {}
        for task_config in self.config['tasks']:
            task = self._create_task(dag, task_config)
            tasks[task_config['id']] = task
        
        # 设置依赖关系
        self._set_dependencies(tasks)
        
        return dag
    
    def _create_task(self, dag, task_config):
        """创建单个任务"""
        task_type = task_config['type']
        
        if task_type == 'python':
            return PythonOperator(
                task_id=task_config['id'],
                python_callable=globals()[task_config['callable']],
                op_kwargs=task_config.get('parameters', {}),
                dag=dag
            )
        # 其他任务类型...
```

## 3. 动态DAG生成

### 数据库驱动DAG生成
```python
class DatabaseDrivenDAGGenerator:
    """数据库驱动DAG生成器"""
    
    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = create_engine(db_url)
    
    def generate_dags(self):
        """从数据库生成所有DAG"""
        dags = []
        
        # 查询活跃的DAG配置
        with self.engine.connect() as conn:
            result = conn.execute("""
                SELECT dag_id, config FROM workflow_configs 
                WHERE is_active = TRUE
            """)
            
            for row in result:
                dag = self._create_dag_from_config(row.dag_id, row.config)
                dags.append(dag)
        
        return dags
    
    def _create_dag_from_config(self, dag_id, config_json):
        """根据JSON配置创建DAG"""
        config = json.loads(config_json)
        
        dag = DAG(
            dag_id=dag_id,
            default_args=config.get('default_args', {}),
            schedule_interval=config.get('schedule_interval'),
            catchup=False
        )
        
        # 创建任务和依赖关系
        # ...
        
        return dag
```

### API驱动DAG生成
```python
import requests

class APIDrivenDAGGenerator:
    """API驱动DAG生成器"""
    
    def __init__(self, api_base_url, auth_token=None):
        self.api_base_url = api_base_url
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
    
    def refresh_dags(self):
        """从API刷新DAG配置"""
        try:
            response = self.session.get(f"{self.api_base_url}/dags")
            response.raise_for_status()
            
            dag_configs = response.json()
            return [self._create_dag(config) for config in dag_configs]
            
        except requests.RequestException as e:
            logger.error(f"API调用失败: {e}")
            return []
```

## 4. 子DAG设计模式

### 子DAG创建模板
```python
def create_standard_subdag(
    parent_dag_name: str,
    child_dag_name: str,
    default_args: dict,
    task_creator_func: callable
) -> DAG:
    """创建标准子DAG"""
    
    dag_id = f"{parent_dag_name}.{child_dag_name}"
    
    subdag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval=None,  # 子DAG不应该有自己的调度
        catchup=False,
    )
    
    with subdag:
        # 使用任务创建函数构建子DAG
        tasks = task_creator_func(subdag)
        
        # 设置子DAG内部依赖关系
        if isinstance(tasks, dict) and 'start' in tasks and 'end' in tasks:
            tasks['start'] >> tasks['end']
    
    return subdag

# 具体子DAG实现
def create_data_extraction_subdag(parent_dag_name, child_dag_name, args):
    """数据提取子DAG"""
    
    def extraction_task_creator(dag):
        """子DAG内部任务创建器"""
        start = DummyOperator(task_id='start', dag=dag)
        
        extract_db = PythonOperator(
            task_id='extract_database',
            python_callable=extract_from_database,
            dag=dag
        )
        
        extract_api = PythonOperator(
            task_id='extract_api',
            python_callable=extract_from_api,
            dag=dag
        )
        
        merge_data = PythonOperator(
            task_id='merge_extracted_data',
            python_callable=merge_data_function,
            dag=dag
        )
        
        end = DummyOperator(task_id='end', dag=dag)
        
        return {
            'start': start,
            'extract_db': extract_db,
            'extract_api': extract_api,
            'merge_data': merge_data,
            'end': end
        }
    
    return create_standard_subdag(
        parent_dag_name, 
        child_dag_name, 
        args, 
        extraction_task_creator
    )
```

### 子DAG使用模式
```python
# 在主DAG中使用子DAG
with dag:
    # 创建子DAG任务
    extraction_subdag_task = SubDagOperator(
        task_id='data_extraction',
        subdag=create_data_extraction_subdag(
            parent_dag_name='main_pipeline',
            child_dag_name='extraction',
            args=default_args
        ),
        dag=dag
    )
    
    # 主DAG的其他任务
    processing_task = PythonOperator(
        task_id='data_processing',
        python_callable=process_data,
        dag=dag
    )
    
    # 设置依赖关系
    extraction_subdag_task >> processing_task
```

## 5. 条件分支与并行执行

### 分支操作符模式
```python
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

# 分支决策函数
def dynamic_branch_decision(**kwargs):
    """动态分支决策"""
    ti = kwargs['ti']
    
    # 获取上游任务的结果
    data_quality = ti.xcom_pull(task_ids='check_data_quality')
    data_volume = ti.xcom_pull(task_ids='check_data_volume')
    
    # 基于多个条件决定分支
    if data_quality['score'] < 80:
        return 'reprocess_branch'
    elif data_volume['count'] > 10000:
        return 'parallel_processing_branch'
    else:
        return 'standard_processing_branch'

# 分支任务
branch_task = BranchPythonOperator(
    task_id='dynamic_branch_decision',
    python_callable=dynamic_branch_decision,
    dag=dag
)

# 各分支的最终合并任务
merge_results = PythonOperator(
    task_id='merge_all_results',
    python_callable=merge_function,
    trigger_rule=TriggerRule.ALL_DONE,  # 所有分支完成即执行
    dag=dag
)
```

### 并行执行优化
```python
# 数据分区并行处理
def create_parallel_tasks(dag, num_partitions, process_function):
    """创建并行处理任务"""
    
    parallel_tasks = []
    
    for i in range(num_partitions):
        task = PythonOperator(
            task_id=f'process_partition_{i}',
            python_callable=process_function,
            op_kwargs={'partition_id': i},
            pool='parallel_processing_pool',  # 使用资源池
            dag=dag
        )
        parallel_tasks.append(task)
    
    return parallel_tasks

# 使用示例
start_task = DummyOperator(task_id='start_parallel_processing', dag=dag)
parallel_tasks = create_parallel_tasks(dag, 8, process_data_partition)
merge_task = PythonOperator(task_id='merge_parallel_results', dag=dag)

# 设置并行执行依赖
start_task >> parallel_tasks >> merge_task
```

## 6. 高级错误处理

### 错误处理策略模式
```python
class ErrorHandlingStrategy:
    """错误处理策略基类"""
    
    def handle_error(self, task_instance, error):
        """处理错误"""
        raise NotImplementedError

class RetryStrategy(ErrorHandlingStrategy):
    """重试策略"""
    
    def __init__(self, max_retries=3, delay=300):
        self.max_retries = max_retries
        self.delay = delay
    
    def handle_error(self, task_instance, error):
        if task_instance.try_number < self.max_retries:
            logger.info(f"任务 {task_instance.task_id} 将重试")
            return True  # 允许重试
        return False

class AlertStrategy(ErrorHandlingStrategy):
    """告警策略"""
    
    def handle_error(self, task_instance, error):
        # 发送告警
        send_alert(f"任务失败: {task_instance.task_id}", str(error))
        return False  # 不重试

# 错误处理工厂
class ErrorHandlerFactory:
    """错误处理工厂"""
    
    strategies = {
        'retry': RetryStrategy,
        'alert': AlertStrategy,
        'skip': lambda: SkipStrategy()
    }
    
    @classmethod
    def create_strategy(cls, strategy_type, **kwargs):
        if strategy_type not in cls.strategies:
            raise ValueError(f"未知的错误处理策略: {strategy_type}")
        
        strategy_class = cls.strategies[strategy_type]
        return strategy_class(**kwargs)
```

### 全局错误处理
```python
def global_error_handler(context):
    """全局错误处理函数"""
    task_instance = context['task_instance']
    exception = context['exception']
    
    # 记录错误详情
    error_details = {
        'dag_id': task_instance.dag_id,
        'task_id': task_instance.task_id,
        'execution_date': context['execution_date'],
        'exception': str(exception),
        'try_number': task_instance.try_number
    }
    
    logger.error(f"任务执行失败: {error_details}")
    
    # 根据错误类型选择处理策略
    if isinstance(exception, ConnectionError):
        strategy = ErrorHandlerFactory.create_strategy('retry', max_retries=5)
    else:
        strategy = ErrorHandlerFactory.create_strategy('alert')
    
    return strategy.handle_error(task_instance, exception)

# 在DAG中设置全局错误处理
default_args = {
    'on_failure_callback': global_error_handler,
    'on_retry_callback': global_error_handler
}
```

## 7. 性能优化技巧

### 任务优化模式
```python
# 1. 减少任务数量
def optimize_task_count(dag):
    """优化任务数量"""
    # 合并相似的小任务
    # 使用更高效的操作符
    pass

# 2. 优化任务执行时间
def optimize_execution_time(task):
    """优化单个任务执行时间"""
    # 使用更高效的算法
    # 减少I/O操作
    # 使用缓存
    pass

# 3. 合理设置超时
def set_optimal_timeouts(tasks):
    """设置合理的任务超时"""
    for task in tasks:
        if task.task_type == 'heavy_processing':
            task.execution_timeout = timedelta(hours=2)
        else:
            task.execution_timeout = timedelta(minutes=30)
```

### 资源管理模式
```python
# 资源池配置
class ResourcePoolManager:
    """资源池管理器"""
    
    def __init__(self):
        self.pools = {
            'heavy_processing': 2,    # 2个并发槽
            'light_processing': 10,   # 10个并发槽
            'io_intensive': 5        # 5个并发槽
        }
    
    def get_pool_config(self, task_type):
        """获取任务类型的资源池配置"""
        if task_type in self.pools:
            return {
                'pool': task_type,
                'pool_slots': 1
            }
        return {}  # 不使用资源池

# 使用资源池
def create_resource_aware_task(dag, task_id, task_type, **kwargs):
    """创建资源感知的任务"""
    pool_manager = ResourcePoolManager()
    pool_config = pool_manager.get_pool_config(task_type)
    
    return PythonOperator(
        task_id=task_id,
        python_callable=kwargs.get('callable'),
        dag=dag,
        **pool_config,
        **kwargs
    )
```

## 8. 监控与指标收集

### 自定义指标模式
```python
import time
from datetime import datetime

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, metric_name, value, tags=None):
        """记录指标"""
        timestamp = datetime.now()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'timestamp': timestamp,
            'value': value,
            'tags': tags or {}
        })
    
    def timer(self, metric_name):
        """计时器装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.record_metric(metric_name, execution_time)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.record_metric(metric_name, execution_time, {'error': True})
                    raise
            return wrapper
        return decorator

# 使用示例
metrics = MetricsCollector()

@metrics.timer('data_processing_time')
def process_data(data):
    """数据处理函数"""
    # 处理逻辑
    pass
```

### 结构化日志模式
```python
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 在任务中使用结构化日志
def process_task_with_logging(**kwargs):
    """带结构化日志的任务函数"""
    task_instance = kwargs['ti']
    
    logger.info(
        "开始处理任务",
        task_id=task_instance.task_id,
        dag_id=task_instance.dag_id,
        execution_date=kwargs['execution_date']
    )
    
    try:
        # 处理逻辑
        result = heavy_processing()
        
        logger.info(
            "任务处理成功",
            records_processed=len(result),
            processing_time=time_taken
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "任务处理失败",
            error=str(e),
            task_id=task_instance.task_id
        )
        raise
```

## 9. 最佳实践总结

### 设计原则速查

1. **单一职责原则**: 每个DAG/任务只做一件事
2. **开闭原则**: 对扩展开放，对修改关闭
3. **依赖倒置**: 依赖抽象而非具体实现
4. **接口隔离**: 使用小而专的接口

### 代码组织模板
```
dags/
├── factories/          # 任务工厂
├── configs/           # 配置文件
├── subdags/           # 子DAG定义
├── utils/             # 工具函数
├── metrics/           # 指标收集
└── pipelines/         # 主DAG文件
```

### 性能优化检查清单
- [ ] 任务数量是否合理？
- [ ] 是否有不必要的依赖？
- [ ] 资源池配置是否优化？
- [ ] 任务超时设置是否合理？
- [ ] 并行执行是否充分利用？

这个快速参考指南涵盖了高级DAG设计的核心模式和最佳实践，可以作为日常开发的速查手册。