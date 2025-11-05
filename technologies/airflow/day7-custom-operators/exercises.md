# Day 7: 自定义操作符练习题

## 基础练习

### 练习1: 文件压缩操作符
**难度**: ⭐⭐  
**时间**: 30分钟  
**目标**: 创建基础的文件压缩操作符

**要求**:
1. 创建一个`FileCompressorOperator`，支持压缩单个文件或整个目录
2. 支持多种压缩格式（zip, tar, gzip）
3. 提供压缩级别配置
4. 实现错误处理和日志记录
5. 返回压缩文件信息

**提示代码**:
```python
import os
import zipfile
import tarfile
import gzip
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException

class FileCompressorOperator(BaseOperator):
    """文件压缩操作符"""
    
    def __init__(
        self,
        source_path,
        output_path,
        compression_format='zip',
        compression_level=6,
        include_subdirs=True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        # 你的代码：初始化参数
        
    def execute(self, context):
        """执行压缩操作"""
        # 你的代码：实现压缩逻辑
        pass
    
    def _compress_zip(self, source_path, output_path):
        """ZIP压缩"""
        # 你的代码：实现ZIP压缩
        pass
    
    def _compress_tar(self, source_path, output_path):
        """TAR压缩"""
        # 你的代码：实现TAR压缩
        pass
    
    def _compress_gzip(self, source_path, output_path):
        """GZIP压缩"""
        # 你的代码：实现GZIP压缩
        pass
```

**测试用例**:
```python
def test_file_compressor():
    # 创建测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("测试数据" * 1000)
        test_file = f.name
    
    # 测试ZIP压缩
    compressor = FileCompressorOperator(
        task_id='compress_zip',
        source_path=test_file,
        output_path='/tmp/test.zip',
        compression_format='zip',
        dag=dag
    )
    
    result = compressor.execute(context)
    assert os.path.exists(result['compressed_file'])
    assert result['compression_ratio'] > 0
```

---

### 练习2: 数据格式转换操作符
**难度**: ⭐⭐  
**时间**: 45分钟  
**目标**: 创建数据格式转换操作符

**要求**:
1. 创建一个`DataFormatConverterOperator`，支持多种数据格式转换
2. 支持JSON、CSV、XML、YAML格式
3. 提供字段映射和转换规则
4. 处理嵌套数据结构
5. 验证输出数据格式

**提示代码**:
```python
import json
import csv
import xml.etree.ElementTree as ET
import yaml
import pandas as pd
from airflow.models import BaseOperator

class DataFormatConverterOperator(BaseOperator):
    """数据格式转换操作符"""
    
    def __init__(
        self,
        input_data,
        input_format,
        output_format,
        field_mapping=None,
        nested_separator='.',
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        # 你的代码：初始化参数
        
    def execute(self, context):
        """执行格式转换"""
        # 你的代码：实现格式转换逻辑
        pass
    
    def _parse_json(self, data):
        """解析JSON"""
        # 你的代码：解析JSON数据
        pass
    
    def _parse_csv(self, data):
        """解析CSV"""
        # 你的代码：解析CSV数据
        pass
    
    def _flatten_nested_dict(self, data, parent_key='', sep='.'):
        """扁平化嵌套字典"""
        # 你的代码：处理嵌套结构
        pass
    
    def _convert_to_output_format(self, data, output_format):
        """转换为目标格式"""
        # 你的代码：转换为目标格式
        pass
```

---

### 练习3: HTTP请求操作符
**难度**: ⭐⭐⭐  
**时间**: 60分钟  
**目标**: 创建功能完整的HTTP请求操作符

**要求**:
1. 创建一个`HTTPRequestOperator`，支持各种HTTP方法
2. 实现请求重试和超时机制
3. 支持请求头和请求体配置
4. 处理响应数据和错误状态码
5. 提供响应验证功能

**提示代码**:
```python
import requests
import json
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class HTTPRequestOperator(BaseOperator):
    """HTTP请求操作符"""
    
    def __init__(
        self,
        endpoint,
        method='GET',
        headers=None,
        data=None,
        params=None,
        timeout=30,
        max_retries=3,
        backoff_factor=1,
        status_forcelist=None,
        response_validation=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        # 你的代码：初始化参数
        
    def execute(self, context):
        """执行HTTP请求"""
        # 你的代码：实现HTTP请求逻辑
        pass
    
    def _create_session(self):
        """创建请求会话"""
        # 你的代码：配置重试策略
        pass
    
    def _validate_response(self, response):
        """验证响应"""
        # 你的代码：验证响应数据
        pass
    
    def _handle_response_data(self, response):
        """处理响应数据"""
        # 你的代码：处理不同类型的响应
        pass
```

---

## 高级练习

### 练习4: 异步数据处理操作符
**难度**: ⭐⭐⭐⭐  
**时间**: 90分钟  
**目标**: 创建支持异步处理的高级操作符

**要求**:
1. 创建一个`AsyncDataProcessorOperator`，支持异步数据处理
2. 实现并发任务执行和结果聚合
3. 提供进度监控和取消机制
4. 支持多种并发策略（线程、进程、异步IO）
5. 实现优雅的错误处理和资源清理

**提示代码**:
```python
import asyncio
import concurrent.futures
import threading
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException

class AsyncDataProcessorOperator(BaseOperator):
    """异步数据处理操作符"""
    
    def __init__(
        self,
        data_items,
        processing_function,
        concurrency_type='thread',  # 'thread', 'process', 'asyncio'
        max_workers=None,
        chunk_size=100,
        timeout_per_item=30,
        enable_progress_callback=False,
        error_handling='continue',  # 'continue', 'fail_fast'
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        # 你的代码：初始化参数
        
    def execute(self, context):
        """执行异步处理"""
        # 你的代码：实现异步处理逻辑
        pass
    
    def _process_with_threads(self, data_items):
        """使用线程池处理"""
        # 你的代码：实现线程池处理
        pass
    
    def _process_with_processes(self, data_items):
        """使用进程池处理"""
        # 你的代码：实现进程池处理
        pass
    
    async def _process_with_asyncio(self, data_items):
        """使用异步IO处理"""
        # 你的代码：实现异步IO处理
        pass
    
    def _progress_callback(self, completed, total):
        """进度回调"""
        # 你的代码：实现进度监控
        pass
    
    def _handle_processing_error(self, item, error):
        """处理处理错误"""
        # 你的代码：实现错误处理
        pass
```

**挑战扩展**:
- 实现任务优先级队列
- 添加处理结果缓存机制
- 支持动态调整并发度
- 实现处理中断和恢复功能

---

### 练习5: 智能传感器操作符
**难度**: ⭐⭐⭐⭐  
**时间**: 120分钟  
**目标**: 创建支持多数据源的智能传感器

**要求**:
1. 创建一个`SmartSensorOperator`，支持多种数据源轮询
2. 实现智能轮询策略（固定间隔、指数退避、自适应）
3. 支持条件表达式和复杂逻辑判断
4. 提供数据源健康检查和故障转移
5. 实现传感器状态持久化

**提示代码**:
```python
import time
import json
import requests
from airflow.sensors.base import BaseSensorOperator
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta

class SmartSensorOperator(BaseSensorOperator):
    """智能传感器操作符"""
    
    def __init__(
        self,
        data_sources,  # 多数据源配置
        trigger_condition,
        polling_strategy='adaptive',
        initial_interval=60,
        max_interval=3600,
        backoff_multiplier=2,
        health_check_enabled=True,
        state_persistence=False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        # 你的代码：初始化参数
        
    def poke(self, context):
        """检查触发条件"""
        # 你的代码：实现智能轮询逻辑
        pass
    
    def _fetch_data_from_sources(self):
        """从多个数据源获取数据"""
        # 你的代码：实现多数据源获取
        pass
    
    def _evaluate_trigger_condition(self, data):
        """评估触发条件"""
        # 你的代码：实现复杂条件评估
        pass
    
    def _update_polling_interval(self, condition_met):
        """更新轮询间隔"""
        # 你的代码：实现智能轮询间隔调整
        pass
    
    def _perform_health_check(self):
        """执行健康检查"""
        # 你的代码：实现数据源健康检查
        pass
    
    def _persist_sensor_state(self, state):
        """持久化传感器状态"""
        # 你的代码：实现状态持久化
        pass
```

**数据源配置示例**:
```python
data_sources = [
    {
        'name': 'file_source',
        'type': 'file',
        'config': {
            'path': '/data/sensor_data.json',
            'format': 'json',
            'polling_interval': 60
        },
        'priority': 1,
        'fallback_enabled': True
    },
    {
        'name': 'api_source',
        'type': 'api',
        'config': {
            'url': 'https://api.example.com/status',
            'method': 'GET',
            'headers': {'Authorization': 'Bearer token'},
            'timeout': 30
        },
        'priority': 2,
        'fallback_enabled': True
    },
    {
        'name': 'database_source',
        'type': 'database',
        'config': {
            'connection_id': 'postgres_default',
            'query': "SELECT COUNT(*) as count FROM sensor_data WHERE status = 'ready'",
            'polling_interval': 120
        },
        'priority': 3,
        'fallback_enabled': False
    }
]
```

---

### 练习6: 多步骤数据处理管道操作符
**难度**: ⭐⭐⭐⭐⭐  
**时间**: 150分钟  
**目标**: 创建复杂的数据处理管道操作符

**要求**:
1. 创建一个`DataPipelineOperator`，支持多步骤数据处理
2. 实现步骤间的数据传递和状态管理
3. 支持条件步骤执行和循环处理
4. 提供数据质量检查和异常处理
5. 实现管道执行的可视化和监控

**提示代码**:
```python
import json
import pandas as pd
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException
from datetime import datetime

class DataPipelineOperator(BaseOperator):
    """数据处理管道操作符"""
    
    def __init__(
        self,
        pipeline_definition,  # 管道定义
        input_data,
        execution_context=None,
        enable_step_caching=True,
        quality_gates=None,
        rollback_on_failure=True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        # 你的代码：初始化参数
        
    def execute(self, context):
        """执行数据处理管道"""
        # 你的代码：实现管道执行逻辑
        pass
    
    def _validate_pipeline_definition(self, pipeline_definition):
        """验证管道定义"""
        # 你的代码：验证管道结构
        pass
    
    def _execute_pipeline_step(self, step, input_data, execution_context):
        """执行管道步骤"""
        # 你的代码：实现步骤执行
        pass
    
    def _evaluate_step_condition(self, condition, data, context):
        """评估步骤执行条件"""
        # 你的代码：实现条件评估
        pass
    
    def _perform_quality_check(self, data, quality_gate):
        """执行质量检查"""
        # 你的代码：实现质量检查
        pass
    
    def _handle_pipeline_failure(self, failed_step, error, execution_context):
        """处理管道失败"""
        # 你的代码：实现失败处理
        pass
    
    def _generate_pipeline_report(self, execution_context):
        """生成管道执行报告"""
        # 你的代码：生成执行报告
        pass
```

**管道定义示例**:
```python
pipeline_definition = {
    'name': 'customer_data_processing',
    'version': '1.0',
    'steps': [
        {
            'id': 'load_data',
            'type': 'data_loader',
            'config': {
                'source': 'database',
                'query': 'SELECT * FROM customers WHERE updated_at > ${last_execution_date}'
            }
        },
        {
            'id': 'validate_data',
            'type': 'data_validator',
            'depends_on': ['load_data'],
            'config': {
                'rules': [
                    {'field': 'email', 'type': 'email_format'},
                    {'field': 'age', 'type': 'range', 'min': 18, 'max': 120}
                ]
            },
            'quality_gate': {
                'min_quality_score': 95,
                'max_error_rate': 0.05
            }
        },
        {
            'id': 'clean_data',
            'type': 'data_cleaner',
            'depends_on': ['validate_data'],
            'condition': '${validate_data.quality_score} >= 90',
            'config': {
                'operations': [
                    {'type': 'trim_whitespace', 'fields': ['name', 'email']},
                    {'type': 'normalize_case', 'fields': ['email'], 'case': 'lower'}
                ]
            }
        },
        {
            'id': 'enrich_data',
            'type': 'data_enricher',
            'depends_on': ['clean_data'],
            'config': {
                'enrichments': [
                    {
                        'field': 'customer_segment',
                        'source': 'api',
                        'endpoint': 'https://api.example.com/segment',
                        'mapping': {'customer_id': 'id'}
                    }
                ]
            }
        },
        {
            'id': 'aggregate_data',
            'type': 'data_aggregator',
            'depends_on': ['enrich_data'],
            'config': {
                'group_by': ['customer_segment', 'region'],
                'aggregations': [
                    {'field': 'revenue', 'function': 'sum'},
                    {'field': 'customer_id', 'function': 'count'}
                ]
            }
        },
        {
            'id': 'save_results',
            'type': 'data_saver',
            'depends_on': ['aggregate_data'],
            'config': {
                'destination': 's3',
                'bucket': 'processed-data',
                'path': 'customers/${execution_date}/'
            }
        }
    ],
    'error_handling': {
        'strategy': 'retry_and_continue',
        'max_retries': 3,
        'retry_delay': 300,
        'fallback_steps': [
            {
                'step_id': 'save_error_data',
                'type': 'error_handler',
                'config': {'save_failed_records': True}
            }
        ]
    }
}
```

---

## 综合项目

### 练习7: 企业级ETL操作符套件
**难度**: ⭐⭐⭐⭐⭐  
**时间**: 180分钟  
**目标**: 构建完整的企业级ETL操作符套件

**项目要求**:
1. **数据提取操作符套件**
   - `DatabaseExtractorOperator`: 支持多种数据库（PostgreSQL, MySQL, MongoDB, SQL Server）
   - `APIExtractorOperator`: 支持REST API数据提取，包含分页处理
   - `FileExtractorOperator`: 支持多种文件格式（CSV, JSON, XML, Excel, Parquet）
   - `CloudStorageExtractorOperator`: 支持AWS S3, Azure Blob, Google Cloud Storage

2. **数据转换操作符套件**
   - `DataCleansingOperator`: 数据清洗（去重、填充缺失值、格式标准化）
   - `DataValidatorOperator`: 数据验证（完整性、格式、范围检查）
   - `DataEnrichmentOperator`: 数据增强（外部数据源集成、计算字段）
   - `DataAggregationOperator`: 数据聚合（分组统计、时间窗口聚合）
   - `DataNormalizationOperator`: 数据标准化（归一化、标准化、编码转换）

3. **数据加载操作符套件**
   - `DatabaseLoaderOperator`: 支持批量数据加载和更新
   - `FileLoaderOperator`: 支持多种输出格式和压缩选项
   - `CloudStorageLoaderOperator`: 云存储数据加载
   - `MessageQueueLoaderOperator`: 消息队列数据发布

4. **监控和质量操作符**
   - `DataQualityMonitorOperator`: 数据质量监控和告警
   - `PipelineHealthCheckOperator`: 管道健康检查
   - `PerformanceProfilerOperator`: 性能分析和优化建议
   - `DataLineageTrackerOperator`: 数据血缘追踪

**技术规范**:
- 统一的操作符接口和配置规范
- 完善的错误处理和重试机制
- 支持操作符间的数据传递和状态共享
- 提供详细的执行日志和性能指标
- 支持操作符的版本控制和向后兼容

**示例使用**:
```python
from etl_operators import *

# 创建ETL管道
dag = DAG('enterprise_etl_pipeline', ...)

# 数据提取
extract_task = DatabaseExtractorOperator(
    task_id='extract_customer_data',
    connection_id='postgres_production',
    query="""
        SELECT customer_id, name, email, created_at, updated_at
        FROM customers 
        WHERE updated_at > '${last_execution_date}'
    """,
    chunk_size=10000,
    output_format='parquet',
    dag=dag
)

# 数据验证
validate_task = DataValidatorOperator(
    task_id='validate_customer_data',
    validation_rules={
        'completeness': {
            'required_fields': ['customer_id', 'name', 'email']
        },
        'format': {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        },
        'uniqueness': {
            'fields': ['customer_id']
        }
    },
    quality_threshold=95,
    dag=dag
)

# 数据清洗
clean_task = DataCleansingOperator(
    task_id='clean_customer_data',
    cleansing_operations=[
        {'type': 'trim_whitespace', 'fields': ['name', 'email']},
        {'type': 'normalize_email', 'fields': ['email']},
        {'type': 'remove_duplicates', 'fields': ['customer_id']},
        {'type': 'fill_missing', 'field': 'phone', 'default': 'N/A'}
    ],
    dag=dag
)

# 数据增强
enrich_task = DataEnrichmentOperator(
    task_id='enrich_customer_data',
    enrichment_sources=[
        {
            'source': 'api',
            'endpoint': 'https://api.example.com/customer-segment',
            'mapping': {'customer_id': 'id'},
            'fields': ['customer_segment', 'lifetime_value']
        },
        {
            'source': 'database',
            'connection_id': 'postgres_analytics',
            'query': """
                SELECT customer_id, total_orders, total_spent
                FROM customer_analytics
                WHERE customer_id IN (${customer_ids})
            """,
            'mapping': {'customer_id': 'id'}
        }
    ],
    dag=dag
)

# 数据加载
load_task = DatabaseLoaderOperator(
    task_id='load_to_data_warehouse',
    connection_id='snowflake_warehouse',
    target_table='customers',
    load_strategy='merge',
    match_fields=['customer_id'],
    batch_size=5000,
    dag=dag
)

# 质量监控
monitor_task = DataQualityMonitorOperator(
    task_id='monitor_data_quality',
    connection_id='snowflake_warehouse',
    quality_checks=[
        {
            'check_name': 'row_count_validation',
            'query': 'SELECT COUNT(*) as count FROM customers',
            'expected_range': {'min': 100000, 'max': 10000000}
        },
        {
            'check_name': 'null_percentage',
            'query': """
                SELECT 
                    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as null_pct
                FROM customers
            """,
            'expected_range': {'max': 5}
        }
    ],
    alert_config={
        'enabled': True,
        'channels': ['email', 'slack'],
        'recipients': ['data-team@company.com']
    },
    dag=dag
)

# 设置任务依赖
extract_task >> validate_task >> clean_task >> enrich_task >> load_task >> monitor_task
```

---

### 练习8: 操作符测试框架开发
**难度**: ⭐⭐⭐⭐  
**时间**: 120分钟  
**目标**: 构建专业的操作符测试框架

**项目要求**:
1. **测试基类和工具**
   - `OperatorTestBase`: 操作符测试基类
   - `MockContextBuilder`: 模拟上下文构建器
   - `DataGenerator`: 测试数据生成器
   - `ConnectionMock`: 连接模拟工具

2. **测试类型支持**
   - 单元测试（参数验证、执行逻辑）
   - 集成测试（外部系统模拟）
   - 性能测试（吞吐量、延迟测试）
   - 边界测试（异常输入、极限条件）

3. **测试辅助功能**
   - 测试数据管理（创建、清理、验证）
   - 测试结果断言库
   - 性能基准测试
   - 测试覆盖率报告

4. **持续集成支持**
   - Docker化测试环境
   - 并行测试执行
   - 测试结果报告生成
   - 测试失败自动重试

**示例测试**:
```python
from operator_testing import OperatorTestBase, MockContextBuilder

class TestFileProcessorOperator(OperatorTestBase):
    """文件处理操作符测试"""
    
    def setUp(self):
        super().setUp()
        self.operator_class = FileProcessorOperator
        
    def test_parameter_validation(self):
        """测试参数验证"""
        # 测试必需参数缺失
        with self.assertRaises(AirflowException):
            self.create_operator(
                task_id='test_missing_params',
                # 缺少必需参数
            )
    
    def test_successful_execution(self):
        """测试成功执行"""
        # 创建测试文件
        test_file = self.create_temp_file('test_data.json', {
            'records': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        })
        
        # 创建操作符
        operator = self.create_operator(
            task_id='test_success',
            input_path=test_file,
            output_path='/tmp/output.json',
            processing_function='process_json'
        )
        
        # 执行操作符
        result = operator.execute(self.mock_context)
        
        # 验证结果
        self.assertFileExists(result['output_file'])
        self.assertValidJson(result['output_file'])
        self.assertEqual(result['input_size'], result['output_size'])
    
    def test_error_handling(self):
        """测试错误处理"""
        operator = self.create_operator(
            task_id='test_error',
            input_path='/nonexistent/file.json',
            output_path='/tmp/output.json',
            processing_function='process_json'
        )
        
        with self.assertRaises(AirflowException) as context:
            operator.execute(self.mock_context)
        
        self.assertIn("输入文件不存在", str(context.exception))
    
    @performance_test(timeout=30, max_memory_mb=100)
    def test_performance_large_file(self):
        """测试大文件处理性能"""
        # 生成大型测试文件
        large_data = self.generate_test_data(size=1000000)
        large_file = self.create_temp_file('large_data.json', large_data)
        
        operator = self.create_operator(
            task_id='test_performance',
            input_path=large_file,
            output_path='/tmp/large_output.json',
            processing_function='process_json'
        )
        
        # 测量执行时间
        execution_time = self.measure_execution_time(
            lambda: operator.execute(self.mock_context)
        )
        
        # 验证性能要求
        self.assertLess(execution_time, 30)  # 30秒内完成
        
    @mock_connections(['postgres_default', 'aws_default'])
    def test_integration_with_external_systems(self):
        """测试与外部系统集成"""
        # 模拟数据库连接
        self.mock_database_query(
            connection_id='postgres_default',
            query='SELECT * FROM customers',
            result=[{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        )
        
        # 创建需要数据库连接的操作符
        operator = DatabaseExtractorOperator(
            task_id='test_integration',
            connection_id='postgres_default',
            query='SELECT * FROM customers',
            dag=self.dag
        )
        
        # 执行操作符
        result = operator.execute(self.mock_context)
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertDatabaseQueryCalled('postgres_default', 'SELECT * FROM customers')
```

---

## 练习提交要求

### 代码规范
1. **代码风格**: 遵循PEP 8规范，使用类型注解
2. **文档字符串**: 详细的类和方法文档
3. **错误处理**: 完善的异常处理和用户友好的错误信息
4. **日志记录**: 适当的日志级别和详细信息
5. **参数验证**: 输入参数的类型和有效性验证

### 测试要求
1. **单元测试**: 每个操作符至少80%的代码覆盖率
2. **集成测试**: 关键功能点的端到端测试
3. **性能测试**: 大数据量和并发场景的性能验证
4. **边界测试**: 异常输入和极限条件的处理

### 文档要求
1. **使用说明**: 详细的操作符使用方法和示例
2. **配置指南**: 参数说明和最佳实践
3. **故障排除**: 常见问题和解决方案
4. **版本历史**: 变更记录和版本兼容性

### 评分标准
- **功能完整性** (30%): 是否满足所有功能要求
- **代码质量** (25%): 代码规范、可读性和可维护性
- **测试覆盖** (20%): 测试的完整性和有效性
- **性能优化** (15%): 性能和资源使用效率
- **文档质量** (10%): 文档的完整性和清晰度

完成这些练习将帮助你掌握Airflow自定义操作符开发的核心技能，从基础功能实现到高级特性开发，再到企业级应用的最佳实践。