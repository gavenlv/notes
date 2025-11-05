# Day 2 练习题

## 基础练习

### 练习1：创建简单DAG

**目标**：创建一个包含3个任务的简单DAG，并设置任务之间的依赖关系。

**要求**：
1. 创建一个名为`simple_dag`的DAG
2. 包含3个任务：
   - 任务1：使用PythonOperator打印当前日期
   - 任务2：使用BashOperator打印"Hello Airflow!"
   - 任务3：使用PythonOperator打印当前时间
3. 设置任务依赖关系为：任务1 → 任务2 → 任务3
4. 设置适当的调度间隔和重试策略

**提示**：
- 使用`datetime`模块获取当前日期和时间
- 使用`timedelta`设置调度间隔
- 使用`>>`操作符设置任务依赖关系

### 练习2：使用不同操作符

**目标**：创建一个使用不同类型操作符的DAG。

**要求**：
1. 创建一个名为`operators_dag`的DAG
2. 包含以下任务：
   - BashOperator：执行系统命令，显示当前工作目录
   - PythonOperator：执行Python函数，计算1到100的和
   - EmailOperator：发送邮件通知（可以配置为不实际发送）
3. 设置任务依赖关系，确保按顺序执行
4. 为每个任务添加适当的文档

**提示**：
- 使用`os.getcwd()`获取当前工作目录
- 使用`sum(range(1, 101))`计算1到100的和
- 可以设置`email_on_failure=False`避免实际发送邮件

### 练习3：条件分支

**目标**：创建一个包含条件分支的DAG。

**要求**：
1. 创建一个名为`branch_dag`的DAG
2. 使用BranchPythonOperator根据条件选择执行路径
3. 设置至少两个分支：
   - 分支A：当条件为真时执行
   - 分支B：当条件为假时执行
4. 使用DummyOperator合并分支结果
5. 设置适当的触发规则

**提示**：
- 使用`random.choice([True, False])`生成随机条件
- 使用`trigger_rule='none_failed_or_skipped'`确保分支合并

### 练习4：参数传递

**目标**：创建一个在任务之间传递参数的DAG。

**要求**：
1. 创建一个名为`xcom_dag`的DAG
2. 包含以下任务：
   - 任务1：生成随机数并使用XCom推送
   - 任务2：使用XCom拉取任务1的结果，进行处理
   - 任务3：使用XCom拉取任务2的结果，打印最终结果
3. 在BashOperator中使用Jinja模板拉取XCom值

**提示**：
- 使用`ti.xcom_push()`推送XCom值
- 使用`ti.xcom_pull()`拉取XCom值
- 在BashOperator中使用`{{ ti.xcom_pull(...) }}`模板

## 进阶练习

### 练习5：动态任务生成

**目标**：创建一个动态生成任务的DAG。

**要求**：
1. 创建一个名为`dynamic_dag`的DAG
2. 使用循环动态生成多个任务
3. 为每个动态任务设置适当的依赖关系
4. 使用Python函数处理动态任务的结果

**提示**：
- 使用列表或字典定义动态任务的参数
- 在循环中创建任务并设置依赖关系
- 使用`op_kwargs`传递参数给Python函数

### 练习6：错误处理和重试

**目标**：创建一个包含错误处理和重试机制的DAG。

**要求**：
1. 创建一个名为`error_handling_dag`的DAG
2. 包含一个可能失败的任务
3. 设置适当的重试策略和重试延迟
4. 添加失败回调函数
5. 添加成功回调函数

**提示**：
- 使用`retries`和`retry_delay`设置重试策略
- 使用`on_failure_callback`和`on_success_callback`设置回调函数
- 可以使用`bash_command='exit 1'`模拟任务失败

### 练习7：子DAG和任务组

**目标**：创建一个包含子DAG或任务组的DAG。

**要求**：
1. 创建一个名为`subdag_dag`的主DAG
2. 创建一个子DAG或任务组，包含多个相关任务
3. 在主DAG中调用子DAG或任务组
4. 设置适当的依赖关系

**提示**：
- 使用`@task_group`装饰器创建任务组
- 或者使用`SubDagOperator`创建子DAG
- 确保子DAG或任务组有自己的DAG ID

### 练习8：时间感知DAG

**目标**：创建一个时间感知的DAG，根据执行日期执行不同的逻辑。

**要求**：
1. 创建一个名为`time_aware_dag`的DAG
2. 根据执行日期执行不同的任务
3. 使用`{{ ds }}`、`{{ ts }}`等宏变量
4. 根据执行日期的星期几或月份选择不同的处理路径

**提示**：
- 使用`{{ ds }}`获取执行日期
- 使用`{{ ts }}`获取执行时间戳
- 可以使用`datetime.strptime()`解析日期字符串

## 挑战练习

### 练习9：复杂ETL流程

**目标**：创建一个模拟复杂ETL流程的DAG。

**要求**：
1. 创建一个名为`etl_dag`的DAG
2. 包含以下阶段：
   - 数据提取（Extract）：从多个源提取数据
   - 数据转换（Transform）：清洗和转换数据
   - 数据加载（Load）：将处理后的数据加载到目标系统
3. 每个阶段包含多个任务，并行或串行执行
4. 使用XCom在任务间传递数据
5. 添加适当的错误处理和通知机制

**提示**：
- 使用不同的操作符模拟不同的数据源
- 使用Python函数实现数据转换逻辑
- 使用条件分支处理不同的数据类型

### 练习10：动态DAG生成

**目标**：创建一个能够动态生成其他DAG的DAG。

**要求**：
1. 创建一个名为`dag_generator_dag`的DAG
2. 根据配置文件或数据库中的定义动态生成其他DAG
3. 将生成的DAG写入DAGs文件夹
4. 确保生成的DAG符合Airflow规范

**提示**：
- 使用Python的字符串操作或模板引擎生成DAG代码
- 使用`write_to_file`或类似操作将DAG写入文件
- 确保生成的DAG有正确的导入和语法

## 解答参考

### 练习1解答参考

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'simple_dag',
    default_args=default_args,
    description='一个简单的DAG示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example'],
)

def print_current_date():
    """打印当前日期"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    print(f"当前日期: {current_date}")
    return current_date

def print_current_time():
    """打印当前时间"""
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"当前时间: {current_time}")
    return current_time

task1 = PythonOperator(
    task_id='print_date',
    python_callable=print_current_date,
    dag=dag,
)

task2 = BashOperator(
    task_id='print_hello',
    bash_command='echo "Hello Airflow!"',
    dag=dag,
)

task3 = PythonOperator(
    task_id='print_time',
    python_callable=print_current_time,
    dag=dag,
)

task1 >> task2 >> task3
```

### 练习4解答参考

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import random

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'xcom_dag',
    default_args=default_args,
    description='XCom示例DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'xcom'],
)

def generate_random_number(**kwargs):
    """生成随机数"""
    number = random.randint(1, 100)
    print(f"生成的随机数: {number}")
    kwargs['ti'].xcom_push(key='random_number', value=number)
    return number

def process_number(**kwargs):
    """处理数字"""
    ti = kwargs['ti']
    number = ti.xcom_pull(task_ids='generate_number', key='random_number')
    
    if number % 2 == 0:
        result = f"{number} 是偶数"
    else:
        result = f"{number} 是奇数"
    
    print(f"处理结果: {result}")
    ti.xcom_push(key='processing_result', value=result)
    return result

def print_result(**kwargs):
    """打印结果"""
    ti = kwargs['ti']
    result = ti.xcom_pull(task_ids='process_number', key='processing_result')
    print(f"最终结果: {result}")
    return result

task1 = PythonOperator(
    task_id='generate_number',
    python_callable=generate_random_number,
    dag=dag,
)

task2 = PythonOperator(
    task_id='process_number',
    python_callable=process_number,
    dag=dag,
)

task3 = PythonOperator(
    task_id='print_result',
    python_callable=print_result,
    dag=dag,
)

task4 = BashOperator(
    task_id='bash_pull',
    bash_command='echo "从Bash任务获取的值: {{ ti.xcom_pull(task_ids=\'generate_number\') }}"',
    dag=dag,
)

task1 >> task2 >> task3
task1 >> task4
```

## 学习资源

- [Airflow官方文档 - DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Airflow官方文档 - Operators](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html)
- [Airflow官方文档 - XComs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html)
- [Airflow DAG示例](https://github.com/apache/airflow/tree/main/airflow/example_dags)

## 评估标准

完成练习后，您应该能够：

1. 创建基本的DAG并定义任务
2. 使用不同类型的操作符
3. 设置任务之间的依赖关系
4. 使用XCom在任务间传递数据
5. 处理错误和设置重试策略
6. 创建条件分支和动态任务

如果您能够独立完成基础练习和大部分进阶练习，说明您已经掌握了Day 2的核心内容。挑战练习可以帮助您进一步提高技能。