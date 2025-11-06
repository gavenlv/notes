# Day 7: 自定义操作符快速参考指南

## 操作符开发基础

### BaseOperator 核心组件

```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException

class CustomOperator(BaseOperator):
    """自定义操作符模板"""
    
    # 模板字段 - 支持 Jinja2 模板
    template_fields = ('param1', 'param2')
    
    # 模板扩展 - 支持文件模板
    template_ext = ('.sql', '.json', '.yaml')
    
    # 操作符颜色
    ui_color = '#FFE6E6'
    
    # 操作符图标
    ui_fgcolor = '#000000'
    
    @apply_defaults
    def __init__(
        self,
        param1,
        param2=None,
        timeout=300,
        retry_delay=timedelta(minutes=5),
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.param1 = param1
        self.param2 = param2
        self.timeout = timeout
        self.retry_delay = retry_delay
    
    def execute(self, context):
        """执行操作符逻辑"""
        try:
            # 主要逻辑
            result = self.process_data()
            
            # 日志记录
            self.log.info(f"操作符执行成功: {result}")
            
            # 返回结果
            return result
            
        except Exception as e:
            self.log.error(f"操作符执行失败: {str(e)}")
            raise AirflowException(f"操作符执行失败: {str(e)}")
    
    def process_data(self):
        """自定义处理逻辑"""
        # 实现具体逻辑
        pass
```

### 上下文对象 (Context)

```python
def execute(self, context):
    """访问上下文信息"""
    
    # DAG 信息
    dag = context['dag']
    dag_id = context['dag'].dag_id
    
    # 任务实例信息
    task_instance = context['task_instance']
    task_id = context['task_instance'].task_id
    execution_date = context['execution_date']
    
    # 运行参数
    params = context['params']
    conf = context['conf']  # Airflow 配置
    
    # 连接和变量
    connection = context['conn']
    variable = context['var']
    
    # 前一任务输出
    prev_execution_date = context['prev_execution_date']
    next_execution_date = context['next_execution_date']
    
    # 自定义宏
    templates_dict = context.get('templates_dict', {})
```

## 传感器开发

### BaseSensorOperator 模板

```python
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

class CustomSensor(BaseSensorOperator):
    """自定义传感器模板"""
    
    template_fields = ('target_path', 'target_value')
    
    @apply_defaults
    def __init__(
        self,
        target_path,
        target_value=None,
        poke_interval=60,
        timeout=60*60*24,  # 24小时
        mode='poke',  # 'poke' 或 'reschedule'
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.target_path = target_path
        self.target_value = target_value
        self.poke_interval = poke_interval
        self.mode = mode
    
    def poke(self, context):
        """检查条件是否满足"""
        try:
            # 检查逻辑
            condition_met = self.check_condition()
            
            if condition_met:
                self.log.info("传感器条件已满足")
                return True
            else:
                self.log.info("传感器条件未满足，继续等待")
                return False
                
        except Exception as e:
            self.log.error(f"传感器检查失败: {str(e)}")
            return False
    
    def check_condition(self):
        """自定义检查逻辑"""
        # 实现检查逻辑
        pass
```

### 传感器模式选择

```python
# 1. 轮询模式 (默认)
sensor = CustomSensor(
    task_id='wait_for_file',
    target_path='/data/file.txt',
    mode='poke',  # 持续轮询，占用worker
    poke_interval=60,
    timeout=3600,
    dag=dag
)

# 2. 重调度模式 (推荐)
sensor = CustomSensor(
    task_id='wait_for_file',
    target_path='/data/file.txt',
    mode='reschedule',  # 释放worker，定时重试
    poke_interval=300,
    timeout=7200,
    dag=dag
)
```

## 高级特性实现

### 1. 异步操作符

```python
import asyncio
from airflow.models import BaseOperator

class AsyncOperator(BaseOperator):
    """异步操作符"""
    
    def __init__(self, async_function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.async_function = async_function
    
    def execute(self, context):
        """执行异步操作"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self.async_function(context)
            )
            return result
        finally:
            loop.close()
    
    async def async_execute(self, context):
        """异步执行逻辑"""
        # 异步操作
        await asyncio.sleep(1)
        return {"status": "completed"}

# 使用示例
async_task = AsyncOperator(
    task_id='async_processing',
    async_function=async_process_data,
    dag=dag
)
```

### 2. 批量处理操作符

```python
import concurrent.futures
from airflow.models import BaseOperator

class BatchProcessorOperator(BaseOperator):
    """批量处理操作符"""
    
    def __init__(
        self,
        items,
        process_function,
        batch_size=100,
        max_workers=4,
        timeout=300,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.items = items
        self.process_function = process_function
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.timeout = timeout
    
    def execute(self, context):
        """执行批量处理"""
        results = []
        
        # 分批处理
        for i in range(0, len(self.items), self.batch_size):
            batch = self.items[i:i + self.batch_size]
            batch_results = self.process_batch(batch)
            results.extend(batch_results)
        
        return {
            'total_processed': len(results),
            'successful': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results
        }
    
    def process_batch(self, batch):
        """处理单个批次"""
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [
                executor.submit(self.process_item, item)
                for item in batch
            ]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=self.timeout)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e)
                    })
            
            return results
    
    def process_item(self, item):
        """处理单个项目"""
        try:
            result = self.process_function(item)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

### 3. 条件分支操作符

```python
from airflow.models import BaseOperator
from airflow.operators.python import BranchPythonOperator

class ConditionalOperator(BaseOperator):
    """条件执行操作符"""
    
    def __init__(
        self,
        condition_function,
        true_task_id,
        false_task_id,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.condition_function = condition_function
        self.true_task_id = true_task_id
        self.false_task_id = false_task_id
    
    def execute(self, context):
        """执行条件判断"""
        condition_result = self.condition_function(context)
        
        if condition_result:
            self.log.info(f"条件满足，执行 {self.true_task_id}")
            return self.true_task_id
        else:
            self.log.info(f"条件不满足，执行 {self.false_task_id}")
            return self.false_task_id

# 使用分支操作符
def check_data_quality(**context):
    """检查数据质量"""
    data_quality_score = context['task_instance'].xcom_pull(
        task_ids='validate_data'
    )
    return 'process_high_quality' if data_quality_score > 90 else 'process_low_quality'

branch_task = BranchPythonOperator(
    task_id='quality_check',
    python_callable=check_data_quality,
    dag=dag
)

# 后续任务
high_quality_task = PythonOperator(
    task_id='process_high_quality',
    python_callable=process_high_quality_data,
    dag=dag
)

low_quality_task = PythonOperator(
    task_id='process_low_quality',
    python_callable=process_low_quality_data,
    dag=dag
)

branch_task >> [high_quality_task, low_quality_task]
```

## 错误处理和重试

### 1. 自定义异常处理

```python
from airflow.exceptions import AirflowException, AirflowSkipException

class RobustOperator(BaseOperator):
    """健壮的自定义操作符"""
    
    def __init__(
        self,
        error_handling='retry',  # 'retry', 'skip', 'fail'
        max_retries=3,
        retry_delay=timedelta(minutes=5),
        fallback_value=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.error_handling = error_handling
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fallback_value = fallback_value
    
    def execute(self, context):
        """执行带错误处理的逻辑"""
        try:
            return self.process_with_error_handling(context)
            
        except Exception as e:
            self.handle_error(e, context)
    
    def process_with_error_handling(self, context):
        """带错误处理的处理逻辑"""
        try:
            # 主要逻辑
            result = self.process_data(context)
            
            # 结果验证
            self.validate_result(result)
            
            return result
            
        except ValueError as e:
            # 数据错误
            self.log.error(f"数据错误: {str(e)}")
            if self.error_handling == 'skip':
                raise AirflowSkipException(f"跳过任务: {str(e)}")
            else:
                raise
                
        except ConnectionError as e:
            # 连接错误
            self.log.error(f"连接错误: {str(e)}")
            if self.error_handling == 'retry':
                # 触发重试
                raise AirflowException(f"连接失败，重试中: {str(e)}")
            else:
                raise
                
        except Exception as e:
            # 其他错误
            self.log.error(f"未知错误: {str(e)}")
            raise
    
    def handle_error(self, error, context):
        """错误处理"""
        error_type = type(error).__name__
        
        if self.error_handling == 'skip':
            self.log.warning(f"跳过任务: {error_type} - {str(error)}")
            raise AirflowSkipException(f"任务被跳过: {str(error)}")
            
        elif self.error_handling == 'fail':
            self.log.error(f"任务失败: {error_type} - {str(error)}")
            raise error
            
        else:  # retry
            self.log.error(f"任务失败，将重试: {error_type} - {str(error)}")
            raise error
    
    def validate_result(self, result):
        """结果验证"""
        if result is None:
            raise ValueError("处理结果为空")
        
        if isinstance(result, dict):
            if 'error' in result:
                raise ValueError(f"处理错误: {result['error']}")
            
            if 'status' in result and result['status'] == 'failed':
                raise ValueError("处理状态为失败")
```

### 2. 智能重试策略

```python
from datetime import timedelta
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class SmartRetryOperator(BaseOperator):
    """智能重试操作符"""
    
    @apply_defaults
    def __init__(
        self,
        exponential_backoff=True,
        max_retry_delay=timedelta(hours=1),
        retry_delay_multiplier=2,
        jitter=True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.exponential_backoff = exponential_backoff
        self.max_retry_delay = max_retry_delay
        self.retry_delay_multiplier = retry_delay_multiplier
        self.jitter = jitter
    
    def execute(self, context):
        """执行操作符逻辑"""
        retry_count = 0
        
        while retry_count <= self.retries:
            try:
                return self.process_data(context)
                
            except Exception as e:
                retry_count += 1
                
                if retry_count > self.retries:
                    self.log.error(f"达到最大重试次数 {self.retries}")
                    raise
                
                # 计算重试延迟
                delay = self.calculate_retry_delay(retry_count)
                
                self.log.warning(
                    f"第 {retry_count} 次重试，等待 {delay} 秒: {str(e)}"
                )
                
                time.sleep(delay)
    
    def calculate_retry_delay(self, retry_count):
        """计算重试延迟"""
        if self.exponential_backoff:
            delay = self.retry_delay.total_seconds() * (
                self.retry_delay_multiplier ** (retry_count - 1)
            )
            
            # 添加抖动
            if self.jitter:
                import random
                delay = delay * (0.5 + random.random())
            
            # 限制最大延迟
            max_delay = self.max_retry_delay.total_seconds()
            return min(delay, max_delay)
        else:
            return self.retry_delay.total_seconds()
```

## 测试和验证

### 1. 单元测试模板

```python
import unittest
from unittest.mock import Mock, patch
from airflow.models import TaskInstance, DagRun
from airflow.utils.state import State
from datetime import datetime

class TestCustomOperator(unittest.TestCase):
    """自定义操作符单元测试"""
    
    def setUp(self):
        """测试设置"""
        self.dag = Mock()
        self.task = Mock()
        self.task_instance = Mock(spec=TaskInstance)
        self.execution_date = datetime(2023, 1, 1)
        
        self.context = {
            'dag': self.dag,
            'task': self.task,
            'task_instance': self.task_instance,
            'execution_date': self.execution_date,
            'ds': '2023-01-01',
            'ts': '2023-01-01T00:00:00',
            'params': {},
            'conf': Mock()
        }
    
    def test_operator_initialization(self):
        """测试操作符初始化"""
        operator = CustomOperator(
            task_id='test_task',
            param1='value1',
            param2='value2'
        )
        
        self.assertEqual(operator.param1, 'value1')
        self.assertEqual(operator.param2, 'value2')
        self.assertEqual(operator.task_id, 'test_task')
    
    def test_successful_execution(self):
        """测试成功执行"""
        operator = CustomOperator(
            task_id='test_task',
            param1='test_value'
        )
        
        # 模拟成功执行
        operator.process_data = Mock(return_value={'status': 'success'})
        
        result = operator.execute(self.context)
        
        self.assertEqual(result['status'], 'success')
        operator.process_data.assert_called_once()
    
    def test_error_handling(self):
        """测试错误处理"""
        operator = CustomOperator(
            task_id='test_task',
            param1='invalid_value'
        )
        
        # 模拟执行错误
        operator.process_data = Mock(side_effect=ValueError("处理错误"))
        
        with self.assertRaises(AirflowException):
            operator.execute(self.context)
    
    def test_template_rendering(self):
        """测试模板渲染"""
        operator = CustomOperator(
            task_id='test_task',
            param1='{{ ds }}',
            param2='{{ params.custom_param }}'
        )
        
        self.context['params'] = {'custom_param': 'custom_value'}
        
        # 渲染模板
        rendered_param1 = operator.param1  # 需要实际渲染逻辑
        rendered_param2 = operator.param2
        
        # 验证渲染结果
        self.assertEqual(rendered_param1, '2023-01-01')
        self.assertEqual(rendered_param2, 'custom_value')
    
    @patch('airflow.hooks.base.BaseHook.get_connection')
    def test_connection_usage(self, mock_get_connection):
        """测试连接使用"""
        # 模拟连接
        mock_conn = Mock()
        mock_conn.host = 'localhost'
        mock_conn.port = 5432
        mock_get_connection.return_value = mock_conn
        
        operator = CustomOperator(
            task_id='test_task',
            conn_id='test_connection'
        )
        
        result = operator.execute(self.context)
        
        mock_get_connection.assert_called_once_with('test_connection')
```

### 2. 集成测试模板

```python
import tempfile
import os
from airflow.models import DAG, TaskInstance
from airflow.utils.state import State
from datetime import datetime, timedelta

class TestCustomOperatorIntegration(unittest.TestCase):
    """自定义操作符集成测试"""
    
    def setUp(self):
        """测试设置"""
        self.dag = DAG(
            'test_dag',
            default_args={
                'owner': 'test',
                'start_date': datetime(2023, 1, 1),
                'retries': 1,
                'retry_delay': timedelta(minutes=5)
            },
            schedule_interval=None
        )
    
    def test_dag_execution(self):
        """测试DAG执行"""
        # 创建任务
        task1 = CustomOperator(
            task_id='task1',
            param1='value1',
            dag=self.dag
        )
        
        task2 = CustomOperator(
            task_id='task2',
            param1='value2',
            dag=self.dag
        )
        
        # 设置依赖
        task1 >> task2
        
        # 执行DAG
        execution_date = datetime(2023, 1, 1)
        dag_run = self.dag.create_dagrun(
            run_id='test_run',
            execution_date=execution_date,
            state=State.RUNNING
        )
        
        # 验证执行结果
        ti1 = TaskInstance(task1, execution_date)
        ti2 = TaskInstance(task2, execution_date)
        
        # 执行任务
        ti1.run()
        self.assertEqual(ti1.state, State.SUCCESS)
        
        ti2.run()
        self.assertEqual(ti2.state, State.SUCCESS)
    
    def test_xcom_communication(self):
        """测试XCom通信"""
        def push_data(**context):
            return {'processed_data': 'test_data'}
        
        def pull_data(**context):
            data = context['task_instance'].xcom_pull(task_ids='push_task')
            return {'received_data': data['processed_data']}
        
        push_task = PythonOperator(
            task_id='push_task',
            python_callable=push_data,
            dag=self.dag
        )
        
        pull_task = PythonOperator(
            task_id='pull_task',
            python_callable=pull_data,
            dag=self.dag
        )
        
        push_task >> pull_task
        
        # 执行并验证
        execution_date = datetime(2023, 1, 1)
        
        push_ti = TaskInstance(push_task, execution_date)
        pull_ti = TaskInstance(pull_task, execution_date)
        
        push_ti.run()
        pull_ti.run()
        
        # 验证数据传递
        result = pull_ti.xcom_pull(task_ids='pull_task')
        self.assertEqual(result['received_data'], 'test_data')
```

## 性能优化技巧

### 1. 内存优化

```python
class MemoryEfficientOperator(BaseOperator):
    """内存优化的操作符"""
    
    def __init__(self, chunk_size=1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_size = chunk_size
    
    def execute(self, context):
        """内存优化的执行逻辑"""
        # 使用生成器处理大数据
        def data_generator():
            """数据生成器"""
            while True:
                chunk = self.fetch_data_chunk()
                if not chunk:
                    break
                yield chunk
        
        # 逐块处理
        for chunk in data_generator():
            processed_chunk = self.process_chunk(chunk)
            self.save_chunk(processed_chunk)
            
            # 显式清理内存
            del chunk
            del processed_chunk
    
    def fetch_data_chunk(self):
        """获取数据块"""
        # 实现数据获取逻辑
        pass
    
    def process_chunk(self, chunk):
        """处理数据块"""
        # 实现数据处理逻辑
        pass
    
    def save_chunk(self, chunk):
        """保存数据块"""
        # 实现数据保存逻辑
        pass
```

### 2. 并发优化

```python
import concurrent.futures
from airflow.models import BaseOperator

class ConcurrentOperator(BaseOperator):
    """并发处理操作符"""
    
    def __init__(
        self,
        max_workers=None,
        chunk_size=100,
        timeout=300,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.max_workers = max_workers or (os.cpu_count() * 2)
        self.chunk_size = chunk_size
        self.timeout = timeout
    
    def execute(self, context):
        """并发执行处理"""
        items = self.get_items_to_process()
        
        # 使用线程池进行并发处理
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            
            # 提交任务
            futures = []
            for i in range(0, len(items), self.chunk_size):
                chunk = items[i:i + self.chunk_size]
                future = executor.submit(self.process_chunk, chunk)
                futures.append(future)
            
            # 收集结果
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=self.timeout)
                    results.extend(result)
                except Exception as e:
                    self.log.error(f"处理失败: {str(e)}")
                    raise
        
        return results
    
    def get_items_to_process(self):
        """获取待处理项目"""
        # 实现获取逻辑
        pass
    
    def process_chunk(self, chunk):
        """处理数据块"""
        # 实现处理逻辑
        pass
```

### 3. 缓存优化

```python
import functools
import hashlib
import json
from airflow.models import BaseOperator

class CachedOperator(BaseOperator):
    """带缓存的操作符"""
    
    def __init__(self, cache_enabled=True, cache_ttl=3600, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
    
    def execute(self, context):
        """带缓存的执行逻辑"""
        # 生成缓存键
        cache_key = self.generate_cache_key(context)
        
        # 检查缓存
        if self.cache_enabled:
            cached_result = self.get_from_cache(cache_key)
            if cached_result:
                self.log.info("使用缓存结果")
                return cached_result
        
        # 执行实际处理
        result = self.process_data(context)
        
        # 保存到缓存
        if self.cache_enabled:
            self.save_to_cache(cache_key, result)
        
        return result
    
    def generate_cache_key(self, context):
        """生成缓存键"""
        # 基于参数和上下文生成唯一键
        key_data = {
            'task_id': self.task_id,
            'execution_date': str(context['execution_date']),
            'params': self.params,
            'operator_params': {
                k: v for k, v in self.__dict__.items()
                if not k.startswith('_')
            }
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_from_cache(self, cache_key):
        """从缓存获取"""
        # 实现缓存获取逻辑
        pass
    
    def save_to_cache(self, cache_key, data):
        """保存到缓存"""
        # 实现缓存保存逻辑
        pass
    
    def process_data(self, context):
        """实际处理逻辑"""
        # 实现具体处理
        pass
```

## 最佳实践清单

### 1. 代码规范
- [ ] 遵循 PEP 8 编码规范
- [ ] 使用类型注解
- [ ] 编写详细的文档字符串
- [ ] 添加适当的注释
- [ ] 保持代码简洁和可读性

### 2. 错误处理
- [ ] 实现完善的异常处理
- [ ] 提供有用的错误信息
- [ ] 支持重试机制
- [ ] 记录详细的错误日志
- [ ] 实现优雅降级

### 3. 性能优化
- [ ] 避免内存泄漏
- [ ] 实现批量处理
- [ ] 支持并发执行
- [ ] 添加缓存机制
- [ ] 优化I/O操作

### 4. 测试覆盖
- [ ] 编写单元测试
- [ ] 实现集成测试
- [ ] 添加性能测试
- [ ] 测试边界条件
- [ ] 验证错误处理

### 5. 文档和示例
- [ ] 提供使用示例
- [ ] 编写配置指南
- [ ] 添加故障排除
- [ ] 记录版本历史
- [ ] 提供最佳实践

### 6. 部署和维护
- [ ] 支持版本控制
- [ ] 实现向后兼容
- [ ] 提供升级指南
- [ ] 监控运行状态
- [ ] 收集性能指标

## 常见问题快速解决

### 1. 操作符执行超时
```python
# 增加超时时间
operator = CustomOperator(
    task_id='long_task',
    execution_timeout=timedelta(hours=2),
    dag=dag
)
```

### 2. 内存不足错误
```python
# 使用内存优化模式
operator = MemoryEfficientOperator(
    task_id='memory_task',
    chunk_size=500,  # 减小批处理大小
    dag=dag
)
```

### 3. 连接池耗尽
```python
# 正确管理连接
class ConnectionAwareOperator(BaseOperator):
    def execute(self, context):
        conn = None
        try:
            conn = self.get_connection()
            # 使用连接
            result = self.process_with_connection(conn)
            return result
        finally:
            if conn:
                self.return_connection(conn)
```

### 4. 模板渲染错误
```python
# 检查模板字段定义
template_fields = ('param1', 'param2')
template_ext = ('.sql', '.json')

# 验证模板参数
operator = CustomOperator(
    task_id='template_task',
    param1='{{ ds }}',  # 确保参数在template_fields中
    param2='{{ params.value }}',
    dag=dag
)
```

### 5. 传感器性能问题
```python
# 使用reschedule模式
sensor = CustomSensor(
    task_id='efficient_sensor',
    mode='reschedule',  # 释放worker资源
    poke_interval=300,  # 增加检查间隔
    timeout=3600,
    dag=dag
)
```