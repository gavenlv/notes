# Day 4: XComs与任务间通信练习

## 基础练习

### 练习1: 基本XComs传递

创建一个DAG，包含以下任务：
1. 生成随机数据（数字、字符串、字典）
2. 处理数据（计算、转换）
3. 存储处理结果

要求：
- 使用PythonOperator生成不同类型的数据
- 在后续任务中拉取并处理这些数据
- 使用BashOperator存储处理结果

<details>
<summary>参考答案</summary>

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime
import random

@dag(
    dag_id='exercise1_basic_xcom',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
)
def exercise1_basic_xcom():
    
    @task
    def generate_number():
        return random.randint(1, 100)
    
    @task
    def generate_string():
        import string
        return ''.join(random.choices(string.ascii_letters, k=10))
    
    @task
    def generate_dict():
        return {
            "id": random.randint(1000, 9999),
            "name": f"Item_{random.randint(1, 100)}",
            "value": round(random.uniform(10.0, 100.0), 2)
        }
    
    @task
    def process_data(ti):
        number = ti.xcom_pull(task_ids='generate_number')
        string = ti.xcom_pull(task_ids='generate_string')
        dict_data = ti.xcom_pull(task_ids='generate_dict')
        
        processed = {
            "doubled_number": number * 2,
            "upper_string": string.upper(),
            "increased_value": dict_data["value"] * 1.1
        }
        
        return processed
    
    store_result = BashOperator(
        task_id='store_result',
        bash_command='echo "{{ ti.xcom_pull(task_ids=\"process_data\") }}" > /tmp/result.json'
    )
    
    [generate_number(), generate_string(), generate_dict()] >> process_data() >> store_result

exercise1_dag = exercise1_basic_xcom()
```
</details>

### 练习2: 跨任务组XComs

创建一个包含多个任务组的DAG，实现：
1. 数据提取任务组（提取不同类型数据）
2. 数据处理任务组（处理提取的数据）
3. 数据验证任务组（验证处理结果）

要求：
- 每个任务组包含多个任务
- 任务组之间通过XComs传递数据
- 验证任务组根据处理结果决定是否继续

<details>
<summary>参考答案</summary>

```python
from airflow.decorators import dag, task, task_group
from datetime import datetime
import random

@dag(
    dag_id='exercise2_cross_taskgroup_xcom',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
)
def exercise2_cross_taskgroup_xcom():
    
    @task_group
    def data_extraction():
        @task
        def extract_customer_data():
            return {"customers": [{"id": i, "name": f"Customer_{i}"} for i in range(1, 6)]}
        
        @task
        def extract_product_data():
            return {"products": [{"id": i, "name": f"Product_{i}"} for i in range(1, 11)]}
        
        [extract_customer_data(), extract_product_data()]
    
    @task_group
    def data_processing():
        @task
        def process_customers(ti):
            customer_data = ti.xcom_pull(task_ids='data_extraction.extract_customer_data')
            processed = [f"Processed_{c['name']}" for c in customer_data["customers"]]
            return {"processed_customers": processed}
        
        @task
        def process_products(ti):
            product_data = ti.xcom_pull(task_ids='data_extraction.extract_product_data')
            processed = [f"Processed_{p['name']}" for p in product_data["products"]]
            return {"processed_products": processed}
        
        [process_customers(), process_products()]
    
    @task_group
    def data_validation():
        @task
        def validate_results(ti):
            customer_result = ti.xcom_pull(task_ids='data_processing.process_customers')
            product_result = ti.xcom_pull(task_ids='data_processing.process_products')
            
            is_valid = len(customer_result["processed_customers"]) > 0 and len(product_result["processed_products"]) > 0
            
            return {
                "validation": "passed" if is_valid else "failed",
                "customer_count": len(customer_result["processed_customers"]),
                "product_count": len(product_result["processed_products"])
            }
        
        validate_results()
    
    data_extraction() >> data_processing() >> data_validation()

exercise2_dag = exercise2_cross_taskgroup_xcom()
```
</details>

### 练习3: 基于XComs的条件分支

创建一个DAG，根据XComs中的数据类型或状态，选择不同的处理路径。

要求：
- 生成包含不同类型/状态的数据
- 使用BranchPythonOperator根据数据值选择分支
- 每个分支执行不同的处理逻辑
- 最终合并结果

<details>
<summary>参考答案</summary>

```python
from airflow.decorators import dag, task, branch
from airflow.operators.dummy import DummyOperator
from datetime import datetime
import random

@dag(
    dag_id='exercise3_xcom_branching',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
)
def exercise3_xcom_branching():
    
    @task
    def generate_data():
        data_types = ["high_priority", "medium_priority", "low_priority"]
        return {
            "type": random.choice(data_types),
            "content": f"Data_{random.randint(1000, 9999)}"
        }
    
    @branch
    def choose_processor(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        data_type = data["type"]
        
        if data_type == "high_priority":
            return 'process_high_priority'
        elif data_type == "medium_priority":
            return 'process_medium_priority'
        else:
            return 'process_low_priority'
    
    @task
    def process_high_priority(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        return {"status": "processed", "priority": "high", "content": data["content"]}
    
    @task
    def process_medium_priority(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        return {"status": "processed", "priority": "medium", "content": data["content"]}
    
    @task
    def process_low_priority(ti):
        data = ti.xcom_pull(task_ids='generate_data')
        return {"status": "processed", "priority": "low", "content": data["content"]}
    
    join_results = DummyOperator(task_id='join_results')
    
    @task
    def store_results(ti):
        # 尝试从所有可能的处理任务中获取结果
        high_result = ti.xcom_pull(task_ids='process_high_priority')
        medium_result = ti.xcom_pull(task_ids='process_medium_priority')
        low_result = ti.xcom_pull(task_ids='process_low_priority')
        
        result = high_result or medium_result or low_result
        return result
    
    generate_data() >> choose_processor() >> [
        process_high_priority(),
        process_medium_priority(),
        process_low_priority()
    ] >> join_results >> store_results()

exercise3_dag = exercise3_xcom_branching()
```
</details>

### 练习4: Jinja模板与XComs结合

创建一个DAG，在BashOperator中使用Jinja模板和XComs，实现动态命令生成。

要求：
- 使用PythonOperator生成配置数据
- 在BashOperator中使用Jinja模板引用XComs
- 根据XComs值动态生成命令
- 执行生成的命令并处理结果

<details>
<summary>参考答案</summary>

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime
import random

@dag(
    dag_id='exercise4_jinja_template_xcom',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
)
def exercise4_jinja_template_xcom():
    
    @task
    def generate_config():
        return {
            "input_path": f"/data/input/{random.randint(1, 100)}",
            "output_path": f"/data/output/{random.randint(1, 100)}",
            "file_type": random.choice(["csv", "json", "xml"]),
            "records": random.randint(1000, 10000)
        }
    
    process_data = BashOperator(
        task_id='process_data',
        bash_command="""
        CONFIG="{{ ti.xcom_pull(task_ids='generate_config') }}"
        INPUT_PATH=$(echo "$CONFIG" | python -c "import sys, json; print(json.load(sys.stdin)['input_path'])")
        OUTPUT_PATH=$(echo "$CONFIG" | python -c "import sys, json; print(json.load(sys.stdin)['output_path'])")
        FILE_TYPE=$(echo "$CONFIG" | python -c "import sys, json; print(json.load(sys.stdin)['file_type'])")
        RECORDS=$(echo "$CONFIG" | python -c "import sys, json; print(json.load(sys.stdin)['records'])")
        
        echo "Processing $RECORDS $FILE_TYPE records from $INPUT_PATH to $OUTPUT_PATH"
        echo "Processing date: {{ ds }}"
        
        # 模拟处理命令
        echo "python process_data.py --input $INPUT_PATH --output $OUTPUT_PATH --type $FILE_TYPE --records $RECORDS"
        """,
        xcom_push=True
    )
    
    store_result = BashOperator(
        task_id='store_result',
        bash_command="""
        COMMAND="{{ ti.xcom_pull(task_ids='process_data') }}"
        RESULT_FILE="/tmp/result_{{ ds_nodash }}.txt"
        
        echo "Command executed: $COMMAND" > $RESULT_FILE
        echo "Execution date: {{ ds }}" >> $RESULT_FILE
        echo "Status: Success" >> $RESULT_FILE
        
        echo "Result stored to $RESULT_FILE"
        """
    )
    
    generate_config() >> process_data() >> store_result()

exercise4_dag = exercise4_jinja_template_xcom()
```
</details>

## 进阶练习

### 练习5: 复杂数据传递链

创建一个DAG，实现复杂的数据传递链，包括：
1. 多级数据转换
2. 数据聚合
3. 条件处理
4. 结果分发

要求：
- 使用多个任务组组织工作流
- 实现跨任务组的多级数据传递
- 根据中间结果决定后续处理路径
- 将最终结果分发到多个目标

### 练习6: 动态XComs处理

创建一个DAG，能够动态处理不同数量和类型的XComs：
1. 生成可变数量的数据项
2. 动态创建处理任务
3. 聚合所有处理结果
4. 生成综合报告

要求：
- 使用动态任务映射
- 处理可变数量的XComs
- 实现灵活的数据聚合逻辑
- 生成包含所有处理结果的报告

### 练习7: XComs性能优化

创建一个DAG，演示XComs的性能优化技巧：
1. 大数据的XComs替代方案
2. XComs清理策略
3. 批量XComs操作
4. XComs缓存机制

要求：
- 比较不同数据传递方法的性能
- 实现XComs的自动清理
- 演示批量XComs操作
- 实现简单的XComs缓存

### 练习8: XComs错误处理

创建一个DAG，演示XComs的错误处理和恢复：
1. XComs推送失败处理
2. XComs拉取失败处理
3. 数据类型不匹配处理
4. XComs超时处理

要求：
- 实现XComs操作的错误捕获
- 提供XComs操作的恢复机制
- 处理常见XComs错误情况
- 实现XComs操作的超时控制

## 挑战练习

### 练习9: 分布式XComs系统

设计并实现一个模拟分布式XComs系统：
1. 多个DAG之间的XComs共享
2. 跨DAG的数据传递和同步
3. 分布式XComs的协调机制
4. 分布式XComs的一致性保证

要求：
- 设计跨DAG的XComs共享机制
- 实现DAG间的数据传递和同步
- 提供分布式XComs的协调逻辑
- 确保分布式XComs的一致性

### 练习10: XComs监控系统

创建一个XComs监控系统，包括：
1. XComs使用情况跟踪
2. XComs性能指标收集
3. XComs异常检测和报警
4. XComs使用报告生成

要求：
- 跟踪XComs的使用情况和模式
- 收集XComs的性能指标
- 实现XComs异常的检测和报警
- 生成详细的XComs使用报告

---

通过完成这些练习，你将深入理解XComs机制和任务间通信，掌握在Airflow中实现复杂数据传递的技巧。