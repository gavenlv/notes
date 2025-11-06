# Day 3 练习题

## 基础练习

### 1. 简单任务组创建

创建一个DAG，包含以下内容：
- 一个开始任务
- 一个名为"数据处理"的任务组，包含三个任务：提取、转换、加载
- 一个结束任务
- 设置适当的依赖关系

**提示**：使用`TaskGroup`上下文管理器创建任务组。

### 2. 分支操作符使用

创建一个DAG，使用`BranchPythonOperator`实现以下逻辑：
- 有一个开始任务
- 使用分支操作符根据随机数选择执行路径A或路径B
- 每个路径包含一个Python任务
- 使用适当的触发规则合并分支

**提示**：使用`trigger_rule="none_failed_or_skipped"`确保合并点能正确执行。

### 3. 触发规则实践

创建一个DAG，演示不同的触发规则：
- 创建三个并行任务：task_a, task_b, task_c
- 创建一个任务，使用`all_success`触发规则
- 创建一个任务，使用`one_success`触发规则
- 创建一个任务，使用`all_done`触发规则

**提示**：观察在不同任务成功/失败情况下，这些任务的执行行为。

### 4. 嵌套任务组

创建一个DAG，包含嵌套任务组：
- 创建一个名为"ETL流程"的任务组
- 在ETL流程中创建三个子任务组：提取、转换、加载
- 每个子任务组包含至少两个任务
- 设置适当的依赖关系

**提示**：任务组可以像普通任务一样设置依赖关系。

## 进阶练习

### 5. 动态任务组

创建一个DAG，动态生成任务组：
- 定义一个数据源列表（例如：["mysql", "postgresql", "sqlite"]）
- 为每个数据源动态创建一个任务组
- 每个任务组包含连接、查询、断开连接三个任务
- 设置适当的依赖关系

**提示**：使用循环和动态任务创建技术。

### 6. 条件任务组

创建一个DAG，根据条件选择执行不同的任务组：
- 使用BranchPythonOperator检查某个条件
- 根据条件选择执行"正常流程"任务组或"紧急流程"任务组
- 每个任务组包含不同的任务序列
- 使用适当的触发规则合并流程

**提示**：任务组本身不能直接作为分支目标，但可以在任务组内部使用分支操作符。

### 7. 复杂依赖设计

设计一个DAG，模拟真实的数据处理流程：
- 数据提取阶段：从多个源并行提取数据
- 数据验证阶段：验证所有提取的数据
- 数据转换阶段：根据数据质量选择不同的转换路径
- 数据加载阶段：将转换后的数据加载到目标系统
- 通知阶段：根据整体流程结果发送不同通知

**提示**：结合使用任务组、分支操作符和不同的触发规则。

### 8. 错误处理与重试

创建一个DAG，演示错误处理和重试机制：
- 创建一个可能失败的任务（例如，随机生成成功或失败）
- 设置重试策略
- 创建一个在所有重试失败后执行的任务
- 创建一个在任务成功后执行的任务
- 使用适当的触发规则确保正确的执行流程

**提示**：使用`retries`和`retry_delay`参数设置重试策略。

## 挑战练习

### 9. 动态ETL管道

设计一个动态ETL管道DAG：
- 从配置文件或数据库读取数据源配置
- 根据配置动态创建提取任务
- 根据数据类型动态创建转换任务
- 根据目标系统动态创建加载任务
- 使用任务组组织这些动态任务

**提示**：考虑使用XComs在任务间传递配置信息。

### 10. 条件任务组链

创建一个DAG，实现条件任务组链：
- 有多个任务组，每个任务组代表一个处理阶段
- 使用分支操作符根据前一阶段的结果决定下一阶段
- 可能跳过某些阶段或执行额外的处理阶段
- 确保所有可能的路径都能正确执行

**提示**：这可能需要复杂的分支逻辑和触发规则组合。

---

## 解答参考

### 练习1解答

```python
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup

with DAG(
    dag_id="exercise_1_task_group",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["exercise"],
) as dag:
    start = DummyOperator(task_id="start")
    
    with TaskGroup("data_processing") as data_processing:
        extract = DummyOperator(task_id="extract")
        transform = DummyOperator(task_id="transform")
        load = DummyOperator(task_id="load")
        
        extract >> transform >> load
    
    end = DummyOperator(task_id="end")
    
    start >> data_processing >> end
```

### 练习2解答

```python
from __future__ import annotations

import pendulum
import random

from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator

def choose_branch():
    """随机选择一个分支"""
    return "path_a" if random.random() > 0.5 else "path_b"

def process_path_a():
    """处理路径A"""
    print("Processing path A")

def process_path_b():
    """处理路径B"""
    print("Processing path B")

with DAG(
    dag_id="exercise_2_branching",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["exercise"],
) as dag:
    start = DummyOperator(task_id="start")
    
    branching = BranchPythonOperator(
        task_id="branching",
        python_callable=choose_branch
    )
    
    path_a = PythonOperator(
        task_id="path_a",
        python_callable=process_path_a
    )
    
    path_b = PythonOperator(
        task_id="path_b",
        python_callable=process_path_b
    )
    
    join_point = DummyOperator(
        task_id="join_point",
        trigger_rule="none_failed_or_skipped"
    )
    
    end = DummyOperator(task_id="end")
    
    start >> branching >> [path_a, path_b] >> join_point >> end
```

---

*最后更新: 2023年11月*