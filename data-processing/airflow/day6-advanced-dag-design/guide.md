# Day 6: 高级DAG设计指南

## 概述

高级DAG设计是Airflow的核心技能，它使我们能够构建复杂、可维护和可扩展的数据工作流。本指南将深入探讨高级DAG设计的各个方面。

## 1. 高级DAG设计模式

### 1.1 工厂模式DAG设计

工厂模式通过创建可重用的DAG组件来提高代码的可维护性。

**核心概念：**
- 任务创建工厂函数
- 标准化的任务模板
- 可配置的参数化设计

**优势：**
- 减少代码重复
- 提高一致性
- 易于维护和扩展

**示例代码：**
```python
def create_data_processing_task(dag, task_id, processing_function, dependencies=None):
    """创建数据处理任务的工厂函数"""
    def task_wrapper(**kwargs):
        try:
            print(f"开始执行任务: {task_id}")
            result = processing_function(**kwargs)
            print(f"任务 {task_id} 执行成功")
            return result
        except Exception as e:
            print(f"任务 {task_id} 执行失败: {str(e)}")
            raise
    
    return PythonOperator(
        task_id=task_id,
        python_callable=task_wrapper,
        dag=dag,
        provide_context=True
    )
```

### 1.2 配置驱动DAG设计

配置驱动的方法将DAG逻辑与配置分离，使DAG更加灵活。

**实现方式：**
- YAML/JSON配置文件
- 数据库存储配置
- API动态获取配置

**配置文件示例：**
```yaml
dag_config:
  dag_id: "config_driven_pipeline"
  description: "基于配置的数据管道"
  schedule_interval: "@daily"

data_sources:
  - name: "user_data"
    type: "database"
    query: "SELECT * FROM users"

processing_steps:
  - step_id: "extract"
    type: "extraction"
```

### 1.3 模块化DAG架构

将大型DAG分解为更小的、可重用的模块。

**模块化策略：**
- 按功能划分模块
- 使用Python包组织代码
- 创建共享的工具函数

## 2. 动态DAG生成

### 2.1 基于配置文件的动态DAG

**实现步骤：**
1. 定义配置文件格式
2. 创建配置解析器
3. 根据配置生成DAG
4. 注册DAG到Airflow

**关键考虑：**
- 配置验证
- 错误处理
- 配置版本控制

### 2.2 基于数据库的动态DAG

**适用场景：**
- 频繁变化的业务需求
- 多租户环境
- 需要实时更新的工作流

**实现架构：**
```python
class DatabaseDrivenDAGGenerator:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def generate_dags(self):
        configs = self._load_configs_from_db()
        return [self._create_dag(config) for config in configs]
```

### 2.3 基于API的动态DAG

**优势：**
- 实时配置更新
- 与外部系统集成
- 支持复杂的业务逻辑

**实现模式：**
```python
class APIDrivenDAGGenerator:
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint
    
    def refresh_dags(self):
        # 定期调用API获取最新配置
        configs = requests.get(self.api_endpoint).json()
        return self.generate_dags(configs)
```

## 3. 子DAG与DAG依赖

### 3.1 子DAG的概念

子DAG允许我们将复杂的DAG分解为更小的、可管理的部分。

**使用场景：**
- 复杂的数据处理流程
- 可重用的工作流组件
- 团队协作开发

**创建子DAG：**
```python
def create_data_extraction_subdag(parent_dag_name, child_dag_name, args):
    dag_id = f"{parent_dag_name}.{child_dag_name}"
    
    subdag = DAG(
        dag_id=dag_id,
        default_args=args,
        schedule_interval=None,  # 子DAG不应该有自己的调度
        catchup=False,
    )
    
    # 在子DAG中定义任务
    with subdag:
        # ... 子DAG任务定义
    
    return subdag
```

### 3.2 DAG之间的依赖

**跨DAG依赖的实现：**
- 使用ExternalTaskSensor
- 通过数据库状态协调
- 使用消息队列

**ExternalTaskSensor示例：**
```python
wait_for_extraction = ExternalTaskSensor(
    task_id='wait_for_extraction',
    external_dag_id='data_extraction_dag',
    external_task_id='extraction_complete',
    mode='reschedule',
    timeout=3600,
    dag=dag
)
```

### 3.3 子DAG的最佳实践

**设计原则：**
- 保持子DAG的独立性
- 明确定义输入输出
- 避免循环依赖
- 合理的错误处理

## 4. 条件分支与并行执行

### 4.1 条件分支执行

**BranchPythonOperator使用：**
```python
def decide_processing_path(**kwargs):
    ti = kwargs['ti']
    quality_data = ti.xcom_pull(task_ids='check_data_quality')
    
    if quality_data['score'] >= 90:
        return 'high_quality_path'
    else:
        return 'standard_path'

decide_path = BranchPythonOperator(
    task_id='decide_processing_path',
    python_callable=decide_processing_path,
    dag=dag
)
```

### 4.2 并行执行优化

**并行策略：**
- 任务级并行
- 数据分区并行
- 资源池管理

**并行任务创建：**
```python
# 创建多个并行任务
parallel_tasks = []
for i in range(num_partitions):
    task = PythonOperator(
        task_id=f'process_partition_{i}',
        python_callable=process_data_chunk,
        op_kwargs={'partition': i},
        dag=dag
    )
    parallel_tasks.append(task)

# 设置并行执行
start_task >> parallel_tasks >> merge_results
```

### 4.3 触发规则（Trigger Rules）

**常用触发规则：**
- `ALL_SUCCESS`: 所有前置任务成功
- `ONE_SUCCESS`: 至少一个前置任务成功
- `ALL_FAILED`: 所有前置任务失败
- `ONE_FAILED`: 至少一个前置任务失败
- `ALL_DONE`: 所有前置任务完成（无论成功失败）

**使用示例：**
```python
merge_task = PythonOperator(
    task_id='merge_results',
    python_callable=merge_function,
    trigger_rule=TriggerRule.ALL_SUCCESS,  # 所有并行任务成功才执行
    dag=dag
)
```

## 5. 高级错误处理

### 5.1 重试策略

**配置重试：**
```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,  # 指数退避
    'max_retry_delay': timedelta(minutes=30)
}
```

### 5.2 自定义错误处理

**错误处理任务：**
```python
def handle_processing_error(**kwargs):
    ti = kwargs['ti']
    
    # 获取失败任务信息
    failed_tasks = ti.get_failed_tasks()
    
    # 发送告警
    send_alert(f"处理失败: {failed_tasks}")
    
    # 记录错误日志
    log_error_details(failed_tasks)

error_handler = PythonOperator(
    task_id='error_handler',
    python_callable=handle_processing_error,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag
)
```

## 6. 性能优化

### 6.1 任务优化

**优化策略：**
- 减少任务数量
- 优化任务执行时间
- 合理设置任务超时

### 6.2 资源管理

**资源池配置：**
```python
task_with_pool = PythonOperator(
    task_id='resource_intensive_task',
    python_callable=heavy_processing,
    pool='heavy_processing_pool',
    pool_slots=2,  # 占用2个资源槽
    dag=dag
)
```

## 7. 监控与日志

### 7.1 自定义指标

**记录业务指标：**
```python
def process_data(**kwargs):
    start_time = datetime.now()
    
    # 处理数据
    result = heavy_processing()
    
    # 记录指标
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # 推送到监控系统
    push_metric('processing_time', processing_time)
    push_metric('records_processed', len(result))
    
    return result
```

### 7.2 结构化日志

**日志格式：**
```python
import structlog

logger = structlog.get_logger()

def process_task(**kwargs):
    logger.info("开始处理任务", task_id=kwargs['task_instance'].task_id)
    
    try:
        # 处理逻辑
        result = process_data()
        logger.info("任务处理成功", records_processed=len(result))
        return result
    except Exception as e:
        logger.error("任务处理失败", error=str(e), exc_info=True)
        raise
```

## 8. 最佳实践总结

### 8.1 设计原则

1. **单一职责**: 每个DAG应该有明确的单一目标
2. **模块化**: 将复杂DAG分解为可重用的组件
3. **配置驱动**: 将配置与代码分离
4. **错误恢复**: 设计健壮的错误处理机制
5. **监控友好**: 便于监控和调试

### 8.2 代码组织

**推荐的项目结构：**
```
dags/
├── common/           # 共享工具和函数
│   ├── __init__.py
│   ├── factories.py  # 任务工厂函数
│   └── utils.py      # 工具函数
├── configs/          # 配置文件
│   ├── etl_pipeline.yaml
│   └── reporting.yaml
├── subdags/          # 子DAG定义
│   ├── extraction.py
│   └── processing.py
└── pipelines/        # 主DAG文件
    ├── etl_pipeline.py
    └── reporting_pipeline.py
```

### 8.3 测试策略

**测试方法：**
- 单元测试：测试单个任务函数
- 集成测试：测试DAG整体流程
- 端到端测试：测试完整的数据管道

通过掌握这些高级DAG设计技术，您将能够构建出更加健壮、可维护和高效的数据工作流。