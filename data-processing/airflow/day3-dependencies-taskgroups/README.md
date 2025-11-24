# Day 3: 依赖关系与任务组

## 学习目标

今天我们将深入学习Airflow中的任务依赖关系和任务组(TaskGroup)概念，这些是构建复杂工作流的关键组件。通过今天的学习，您将能够：

- 理解不同类型的任务依赖关系
- 掌握任务组的创建和使用
- 学会使用分支操作符实现条件执行
- 设计复杂但结构清晰的工作流

## 任务依赖关系

### 基本依赖类型

Airflow提供了多种设置任务依赖关系的方法：

```python
# 位移操作符设置依赖
task1 >> task2  # task1完成后执行task2
task2 << task1  # 同上，另一种写法

# 链式依赖
task1 >> task2 >> task3 >> task4

# 分支依赖
task1 >> [task2, task3]  # task1完成后，并行执行task2和task3

# 合并依赖
[task1, task2] >> task3  # task1和task2都完成后，执行task3

# 复杂依赖
task1 >> [task2, task3] >> task4
```

### 触发规则

触发规则决定了任务在什么条件下可以执行：

```python
from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime

with DAG(
    dag_id='trigger_rules_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    # 默认触发规则: all_success (所有上游任务成功)
    task_default = DummyOperator(task_id='task_default')
    
    # all_done: 所有上游任务完成(不论成功或失败)
    task_all_done = DummyOperator(
        task_id='task_all_done',
        trigger_rule='all_done'
    )
    
    # all_failed: 所有上游任务失败
    task_all_failed = DummyOperator(
        task_id='task_all_failed',
        trigger_rule='all_failed'
    )
    
    # one_success: 至少一个上游任务成功
    task_one_success = DummyOperator(
        task_id='task_one_success',
        trigger_rule='one_success'
    )
    
    # one_failed: 至少一个上游任务失败
    task_one_failed = DummyOperator(
        task_id='task_one_failed',
        trigger_rule='one_failed'
    )
    
    # none_failed: 没有上游任务失败(等同于all_success)
    task_none_failed = DummyOperator(
        task_id='task_none_failed',
        trigger_rule='none_failed'
    )
    
    # none_skipped: 没有上游任务被跳过
    task_none_skipped = DummyOperator(
        task_id='task_none_skipped',
        trigger_rule='none_skipped'
    )
```

### 最新运行策略

Latest Only策略控制DAG在历史运行中的行为：

```python
from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime

with DAG(
    dag_id='latest_only_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=True
) as dag:
    
    # 默认情况下，Airflow会添加LatestOnlyOperator
    # 这确保只有最新的DAG运行会执行未标记为latest_only的任务
    
    task_a = DummyOperator(task_id='task_a')
    task_b = DummyOperator(task_id='task_b')
    task_c = DummyOperator(task_id='task_c')
    
    # 设置依赖
    task_a >> task_b >> task_c
```

## 任务组(TaskGroup)

### 基本任务组

任务组可以将多个任务组织成一个逻辑单元：

```python
from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

with DAG(
    dag_id='task_group_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    start = DummyOperator(task_id='start')
    
    # 创建任务组
    with TaskGroup('data_processing') as data_processing:
        task_1 = DummyOperator(task_id='extract')
        task_2 = DummyOperator(task_id='transform')
        task_3 = DummyOperator(task_id='load')
        
        # 任务组内部依赖
        task_1 >> task_2 >> task_3
    
    # 创建另一个任务组
    with TaskGroup('quality_check') as quality_check:
        check_1 = DummyOperator(task_id='validate')
        check_2 = DummyOperator(task_id='verify')
        
        check_1 >> check_2
    
    end = DummyOperator(task_id='end')
    
    # 设置任务组和外部任务的依赖
    start >> data_processing >> quality_check >> end
```

### 嵌套任务组

任务组可以嵌套使用，创建更复杂的结构：

```python
from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

with DAG(
    dag_id='nested_task_group_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    start = DummyOperator(task_id='start')
    
    # 外层任务组
    with TaskGroup('etl_pipeline') as etl_pipeline:
        
        # 嵌套任务组 - 提取
        with TaskGroup('extract') as extract:
            extract_db = DummyOperator(task_id='extract_from_db')
            extract_api = DummyOperator(task_id='extract_from_api')
            extract_file = DummyOperator(task_id='extract_from_file')
        
        # 嵌套任务组 - 转换
        with TaskGroup('transform') as transform:
            clean_data = DummyOperator(task_id='clean_data')
            enrich_data = DummyOperator(task_id='enrich_data')
            aggregate_data = DummyOperator(task_id='aggregate_data')
            
            clean_data >> enrich_data >> aggregate_data
        
        # 嵌套任务组 - 加载
        with TaskGroup('load') as load:
            load_warehouse = DummyOperator(task_id='load_to_warehouse')
            load_api = DummyOperator(task_id='load_to_api')
    
    end = DummyOperator(task_id='end')
    
    # 设置依赖关系
    start >> extract >> transform >> load >> end
```

### 任务组与依赖

任务组可以简化复杂依赖关系的设置：

```python
from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

with DAG(
    dag_id='task_group_dependencies',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    # 不使用任务组的复杂依赖
    # task1 >> task2 >> task3
    # task1 >> task4 >> task5
    # task3 >> task6
    # task5 >> task6
    
    # 使用任务组简化
    start = DummyOperator(task_id='start')
    
    with TaskGroup('branch_a') as branch_a:
        a1 = DummyOperator(task_id='a1')
        a2 = DummyOperator(task_id='a2')
        a1 >> a2
    
    with TaskGroup('branch_b') as branch_b:
        b1 = DummyOperator(task_id='b1')
        b2 = DummyOperator(task_id='b2')
        b1 >> b2
    
    end = DummyOperator(task_id='end')
    
    # 简化的依赖设置
    start >> [branch_a, branch_b] >> end
```

## 分支操作符

### BranchPythonOperator

BranchPythonOperator根据条件选择要执行的分支：

```python
from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from datetime import datetime
import random

def choose_branch():
    """随机选择一个分支"""
    branches = ['branch_a', 'branch_b', 'branch_c']
    return random.choice(branches)

def check_condition(**kwargs):
    """基于条件选择分支"""
    # 这里可以添加复杂的逻辑
    # 例如检查数据质量、时间条件等
    return 'branch_a' if random.random() > 0.5 else 'branch_b'

with DAG(
    dag_id='branch_operator_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    start = DummyOperator(task_id='start')
    
    # 使用BranchPythonOperator
    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=choose_branch
    )
    
    # 定义分支任务
    branch_a = DummyOperator(task_id='branch_a')
    branch_b = DummyOperator(task_id='branch_b')
    branch_c = DummyOperator(task_id='branch_c')
    
    # 合并点
    join_point = DummyOperator(
        task_id='join_point',
        trigger_rule='none_failed_or_skipped'
    )
    
    # 设置依赖
    start >> branching >> [branch_a, branch_b, branch_c] >> join_point
```

### 基于数据的分支

可以根据运行时的数据决定分支：

```python
from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from datetime import datetime

def check_data_quality(**kwargs):
    """检查数据质量并决定分支"""
    # 模拟数据质量检查
    quality_score = 0.85  # 这可以是从XComs获取的实际数据
    
    if quality_score > 0.9:
        return 'high_quality_path'
    elif quality_score > 0.7:
        return 'medium_quality_path'
    else:
        return 'low_quality_path'

def process_high_quality():
    """处理高质量数据"""
    print("Processing high quality data")

def process_medium_quality():
    """处理中等质量数据"""
    print("Processing medium quality data")

def process_low_quality():
    """处理低质量数据"""
    print("Processing low quality data")

with DAG(
    dag_id='data_based_branching',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    start = DummyOperator(task_id='start')
    
    # 数据质量检查
    check_quality = BranchPythonOperator(
        task_id='check_quality',
        python_callable=check_data_quality
    )
    
    # 不同质量的处理路径
    high_quality_path = PythonOperator(
        task_id='high_quality_path',
        python_callable=process_high_quality
    )
    
    medium_quality_path = PythonOperator(
        task_id='medium_quality_path',
        python_callable=process_medium_quality
    )
    
    low_quality_path = PythonOperator(
        task_id='low_quality_path',
        python_callable=process_low_quality
    )
    
    # 最终合并点
    finalize = DummyOperator(
        task_id='finalize',
        trigger_rule='none_failed_or_skipped'
    )
    
    # 设置依赖
    start >> check_quality >> [high_quality_path, medium_quality_path, low_quality_path] >> finalize
```

## 最佳实践

### 依赖关系设计

1. **保持简单**: 避免过于复杂的依赖关系
2. **使用任务组**: 将相关任务组织在一起
3. **合理设置触发规则**: 确保任务在正确的条件下执行
4. **文档化依赖**: 为复杂的依赖关系添加注释

### 任务组使用

1. **逻辑分组**: 将功能相关的任务放在同一组
2. **避免过深嵌套**: 通常不超过3层嵌套
3. **清晰命名**: 任务组和任务都应有描述性名称
4. **考虑重用**: 设计可重用的任务组结构

### 分支操作

1. **明确条件**: 分支条件应该清晰且可测试
2. **处理所有分支**: 确保所有可能的分支都有对应的任务
3. **设置合并点**: 使用适当的触发规则合并分支
4. **测试分支**: 验证所有分支路径都能正常工作

## 实践练习

1. 创建一个包含多个任务组的DAG，模拟ETL流程
2. 使用BranchPythonOperator实现基于条件的工作流
3. 设计一个包含嵌套任务组的复杂DAG
4. 实现一个使用不同触发规则的DAG

## 进阶阅读

- [Airflow官方文档 - 任务依赖](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#task-dependencies)
- [Airflow官方文档 - 任务组](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/taskgroup.html)
- [Airflow官方文档 - 分支操作](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/branching.html)

## 今日小结

今天我们学习了Airflow中的任务依赖关系和任务组概念，这些是构建复杂工作流的基础。掌握了这些技能后，您将能够设计更加灵活和可维护的工作流。

## 下一步计划

明天我们将学习XComs和任务间通信，这是实现复杂数据流的关键技术。

---

*最后更新: 2023年11月*