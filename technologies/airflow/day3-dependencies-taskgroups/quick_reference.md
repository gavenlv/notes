# Day 3 快速参考指南

## 任务依赖关系

### 基本依赖设置

```python
# 位移操作符
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

| 触发规则 | 描述 |
|---------|------|
| `all_success` (默认) | 所有上游任务成功 |
| `all_done` | 所有上游任务完成(不论成功或失败) |
| `all_failed` | 所有上游任务失败 |
| `one_success` | 至少一个上游任务成功 |
| `one_failed` | 至少一个上游任务失败 |
| `none_failed` | 没有上游任务失败(等同于all_success) |
| `none_skipped` | 没有上游任务被跳过 |
| `none_failed_or_skipped` | 没有上游任务失败或被跳过 |

```python
from airflow.operators.dummy import DummyOperator

# 设置触发规则
task = DummyOperator(
    task_id='my_task',
    trigger_rule='one_success'  # 只要有一个上游任务成功就执行
)
```

## 任务组(TaskGroup)

### 基本任务组

```python
from airflow.utils.task_group import TaskGroup

with DAG(...) as dag:
    with TaskGroup('group_name') as group:
        task1 = DummyOperator(task_id='task1')
        task2 = DummyOperator(task_id='task2')
        
        task1 >> task2
```

### 嵌套任务组

```python
with DAG(...) as dag:
    with TaskGroup('outer_group') as outer_group:
        with TaskGroup('inner_group') as inner_group:
            task1 = DummyOperator(task_id='task1')
            task2 = DummyOperator(task_id='task2')
            
            task1 >> task2
```

### 任务组依赖

```python
with DAG(...) as dag:
    start = DummyOperator(task_id='start')
    
    with TaskGroup('group_a') as group_a:
        a1 = DummyOperator(task_id='a1')
        a2 = DummyOperator(task_id='a2')
        a1 >> a2
    
    with TaskGroup('group_b') as group_b:
        b1 = DummyOperator(task_id='b1')
        b2 = DummyOperator(task_id='b2')
        b1 >> b2
    
    end = DummyOperator(task_id='end')
    
    # 任务组可以像普通任务一样设置依赖
    start >> group_a >> group_b >> end
```

## 分支操作符

### BranchPythonOperator

```python
from airflow.operators.python import BranchPythonOperator

def choose_branch():
    """选择要执行的分支"""
    # 返回要执行的任务ID
    return 'branch_a' if condition else 'branch_b'

with DAG(...) as dag:
    start = DummyOperator(task_id='start')
    
    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=choose_branch
    )
    
    branch_a = DummyOperator(task_id='branch_a')
    branch_b = DummyOperator(task_id='branch_b')
    
    # 合并点需要特殊触发规则
    join_point = DummyOperator(
        task_id='join_point',
        trigger_rule='none_failed_or_skipped'
    )
    
    start >> branching >> [branch_a, branch_b] >> join_point
```

### 基于条件的分支

```python
def check_data_quality(**kwargs):
    """基于数据质量选择分支"""
    ti = kwargs['ti']
    # 从XCom获取数据质量分数
    quality_score = ti.xcom_pull(task_ids='check_quality')
    
    if quality_score > 0.9:
        return 'high_quality_path'
    elif quality_score > 0.7:
        return 'medium_quality_path'
    else:
        return 'low_quality_path'
```

## 最佳实践

### 依赖关系设计

1. **保持简单**: 避免过于复杂的依赖关系
2. **文档化**: 为复杂的依赖关系添加注释
3. **测试**: 验证所有可能的执行路径
4. **一致性**: 在整个DAG中使用一致的依赖模式

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

## 常见问题解决

### 任务不执行

1. 检查触发规则是否正确设置
2. 确认上游任务状态
3. 验证DAG是否启用且未暂停

### 分支不工作

1. 确认分支函数返回的任务ID存在
2. 检查合并点的触发规则
3. 验证分支函数的逻辑

### 任务组问题

1. 确保任务组ID在整个DAG中唯一
2. 检查任务组内的任务ID是否唯一
3. 验证任务组的缩进和结构

## 有用命令

```bash
# 列出DAG中的任务
airflow tasks list <dag_id>

# 测试特定任务
airflow tasks test <dag_id> <task_id> <execution_date>

# 检查任务状态
airflow tasks state <dag_id> <task_id> <execution_date>

# 渲染DAG的依赖关系图
airflow dags report
```

---

*最后更新: 2023年11月*