# Day 3 故障排除指南

## 任务依赖相关问题

### DAG不显示或任务不执行

**问题**: DAG或任务在UI中不显示，或者任务不执行

**可能原因**:
1. DAG文件有语法错误
2. 依赖关系设置不正确
3. 触发规则配置问题
4. DAG处于暂停状态

**解决方案**:
1. 检查DAG文件的语法错误
2. 验证任务依赖关系的设置
3. 确认触发规则是否符合预期
4. 检查DAG是否已启用

```bash
# 检查DAG文件语法
python -m py_compile your_dag_file.py

# 检查DAG列表
airflow dags list

# 检查DAG状态
airflow dags state <dag_id> <execution_date>
```

### 任务卡在运行状态

**问题**: 任务长时间处于运行状态，不完成也不失败

**可能原因**:
1. 任务依赖的上游任务未完成
2. 触发规则不满足
3. 任务实例被锁定

**解决方案**:
1. 检查所有上游任务的状态
2. 验证触发规则的设置
3. 清理锁定的任务实例

```bash
# 检查任务状态
airflow tasks state <dag_id> <task_id> <execution_date>

# 清理锁定的任务
airflow tasks clear <dag_id> -t <task_id> -e <execution_date>
```

### 触发规则不生效

**问题**: 设置的触发规则没有按预期工作

**可能原因**:
1. 触发规则选择不当
2. 上游任务状态不符合触发条件
3. 任务被跳过

**解决方案**:
1. 重新评估触发规则的选择
2. 检查所有上游任务的状态
3. 确认任务没有被跳过

```python
# 常见触发规则示例
# 当至少一个上游任务成功时执行
task = DummyOperator(
    task_id='my_task',
    trigger_rule='one_success'
)

# 当所有上游任务完成时执行（不论成功或失败）
task = DummyOperator(
    task_id='my_task',
    trigger_rule='all_done'
)
```

## 任务组相关问题

### 任务组不显示

**问题**: 任务组在UI中不显示或显示不正确

**可能原因**:
1. 任务组ID不唯一
2. 任务组嵌套过深
3. 任务组内任务ID冲突

**解决方案**:
1. 确保任务组ID在整个DAG中唯一
2. 减少任务组嵌套层级
3. 检查任务组内任务的ID唯一性

```python
# 正确的任务组示例
with DAG(...) as dag:
    with TaskGroup('unique_group_id') as group:
        task1 = DummyOperator(task_id='unique_task_id_1')
        task2 = DummyOperator(task_id='unique_task_id_2')
```

### 任务组依赖不工作

**问题**: 任务组之间的依赖关系不生效

**可能原因**:
1. 任务组依赖设置错误
2. 任务组内任务依赖冲突
3. 触发规则配置问题

**解决方案**:
1. 正确设置任务组之间的依赖
2. 检查任务组内部的依赖关系
3. 验证触发规则的设置

```python
# 正确的任务组依赖设置
with DAG(...) as dag:
    with TaskGroup('group_a') as group_a:
        task_a1 = DummyOperator(task_id='task_a1')
        task_a2 = DummyOperator(task_id='task_a2')
        task_a1 >> task_a2
    
    with TaskGroup('group_b') as group_b:
        task_b1 = DummyOperator(task_id='task_b1')
        task_b2 = DummyOperator(task_id='task_b2')
        task_b1 >> task_b2
    
    # 设置任务组之间的依赖
    group_a >> group_b
```

## 分支操作相关问题

### 分支不执行

**问题**: BranchPythonOperator选择的分支不执行

**可能原因**:
1. 分支函数返回的任务ID不存在
2. 分支函数执行出错
3. 返回的任务ID不在分支列表中

**解决方案**:
1. 确保返回的任务ID存在
2. 检查分支函数的逻辑
3. 验证返回的任务ID在分支列表中

```python
def choose_branch():
    """选择分支函数"""
    # 确保返回的任务ID存在
    if condition:
        return 'branch_a'  # 确保这个任务ID存在
    else:
        return 'branch_b'  # 确保这个任务ID存在

with DAG(...) as dag:
    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=choose_branch
    )
    
    # 确保这些任务ID存在
    branch_a = DummyOperator(task_id='branch_a')
    branch_b = DummyOperator(task_id='branch_b')
    
    branching >> [branch_a, branch_b]
```

### 分支合并问题

**问题**: 分支后的合并任务不执行

**可能原因**:
1. 合并任务的触发规则设置不当
2. 分支任务被跳过
3. 合并任务依赖设置错误

**解决方案**:
1. 使用适当的触发规则（如none_failed_or_skipped）
2. 确保分支任务能正常执行
3. 检查合并任务的依赖设置

```python
# 正确的分支合并设置
with DAG(...) as dag:
    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=choose_branch
    )
    
    branch_a = DummyOperator(task_id='branch_a')
    branch_b = DummyOperator(task_id='branch_b')
    
    # 使用适当的触发规则
    join_point = DummyOperator(
        task_id='join_point',
        trigger_rule='none_failed_or_skipped'
    )
    
    branching >> [branch_a, branch_b] >> join_point
```

## 性能问题

### DAG加载缓慢

**问题**: DAG文件加载或解析缓慢

**可能原因**:
1. DAG文件过大
2. 复杂的任务组嵌套
3. 动态任务生成过多

**解决方案**:
1. 拆分大型DAG文件
2. 简化任务组结构
3. 优化动态任务生成逻辑

```python
# 避免在DAG文件顶部执行耗时操作
# 不要这样做：
import time
time.sleep(5)  # 这会阻塞DAG加载

# 应该将耗时操作放在任务中
def time_consuming_operation():
    time.sleep(5)
    return "Done"

task = PythonOperator(
    task_id='time_consuming_task',
    python_callable=time_consuming_operation
)
```

### 任务执行缓慢

**问题**: 任务执行时间过长

**可能原因**:
1. 任务逻辑复杂
2. 资源限制
3. 外部依赖响应慢

**解决方案**:
1. 优化任务逻辑
2. 增加资源配置
3. 优化外部依赖调用

```python
# 设置合理的资源限制
task = PythonOperator(
    task_id='resource_intensive_task',
    python_callable=resource_intensive_function,
    # 设置资源限制
    executor_config={
        "KubernetesExecutor": {
            "request_memory": "256Mi",
            "request_cpu": "100m",
            "limit_memory": "512Mi",
            "limit_cpu": "200m"
        }
    }
)
```

## 调试技巧

### 启用详细日志

```python
# 在airflow.cfg中设置
[core]
logging_level = DEBUG

# 或者在DAG文件中设置
import logging
logging.getLogger('airflow').setLevel(logging.DEBUG)
```

### 使用测试模式

```bash
# 测试特定任务
airflow tasks test <dag_id> <task_id> <execution_date>

# 测试整个DAG
airflow dags test <dag_id> <execution_date>
```

### 检查任务实例

```python
# 在任务中获取任务实例信息
def debug_task(**kwargs):
    ti = kwargs['ti']
    dag_run = ti.get_dagrun()
    print(f"DAG Run: {dag_run}")
    print(f"Task Instance: {ti}")
    print(f"Execution Date: {ti.execution_date}")
    
task = PythonOperator(
    task_id='debug_task',
    python_callable=debug_task
)
```

## 获取帮助

### 官方文档

- [Airflow官方文档 - 任务依赖](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#task-dependencies)
- [Airflow官方文档 - 任务组](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/taskgroup.html)
- [Airflow官方文档 - 分支操作](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/branching.html)

### 社区资源

- [Airflow邮件列表](https://airflow.apache.org/community.html)
- [Airflow Slack频道](https://apache-airflow.slack.com/)
- [Stack Overflow标签](https://stackoverflow.com/questions/tagged/apache-airflow)

---

*最后更新: 2023年11月*