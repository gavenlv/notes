"""
自定义操作符测试和验证示例
演示如何编写单元测试、集成测试和性能测试来验证自定义操作符
"""

import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from airflow.models import TaskInstance, DAG
from airflow.utils.state import State
from airflow.exceptions import AirflowException

# 导入要测试的操作符
from basic_custom_operators import FileProcessorOperator, DataValidatorOperator, NotificationOperator
from advanced_custom_operators import AdvancedSensorOperator, AsyncBatchProcessorOperator, SmartDataProcessorOperator


class TestFileProcessorOperator(unittest.TestCase):
    """测试文件处理操作符"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = tempfile.mkdtemp()
        self.dag = DAG(
            'test_dag',
            default_args={'owner': 'test', 'start_date': datetime(2024, 1, 1)},
            schedule_interval=None
        )
        
        # 创建测试文件
        self.test_input_file = os.path.join(self.test_dir, 'test_input.json')
        self.test_output_file = os.path.join(self.test_dir, 'test_output.json')
        
        test_data = {
            'users': [
                {'id': 1, 'name': 'Alice', 'age': 25},
                {'id': 2, 'name': 'Bob', 'age': 30}
            ]
        }
        
        with open(self.test_input_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
    
    def tearDown(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir)
    
    def test_file_processor_initialization(self):
        """测试文件处理操作符初始化"""
        operator = FileProcessorOperator(
            task_id='test_file_processor',
            input_path=self.test_input_file,
            output_path=self.test_output_file,
            processing_function='process_json',
            dag=self.dag
        )
        
        self.assertEqual(operator.input_path, self.test_input_file)
        self.assertEqual(operator.output_path, self.test_output_file)
        self.assertEqual(operator.processing_function, 'process_json')
    
    def test_file_processor_missing_required_params(self):
        """测试缺少必需参数时的异常"""
        with self.assertRaises(AirflowException) as context:
            FileProcessorOperator(
                task_id='test_file_processor',
                input_path='',  # 空路径
                output_path=self.test_output_file,
                dag=self.dag
            )
        
        self.assertIn("input_path 和 output_path 是必需参数", str(context.exception))
    
    def test_file_processor_execute_json_formatting(self):
        """测试JSON格式化功能"""
        # 创建未格式化的JSON文件
        unformatted_json = '{"users":[{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]}'
        with open(self.test_input_file, 'w', encoding='utf-8') as f:
            f.write(unformatted_json)
        
        operator = FileProcessorOperator(
            task_id='test_json_format',
            input_path=self.test_input_file,
            output_path=self.test_output_file,
            processing_function='process_json',
            dag=self.dag
        )
        
        # 执行操作符
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证输出文件存在且内容正确
        self.assertTrue(os.path.exists(self.test_output_file))
        
        with open(self.test_output_file, 'r', encoding='utf-8') as f:
            formatted_content = f.read()
        
        # 验证内容被格式化
        self.assertIn('\n', formatted_content)  # 应该包含换行符
        self.assertIn('  ', formatted_content)  # 应该包含缩进
        
        # 验证返回结果
        self.assertIn('input_file', result)
        self.assertIn('output_file', result)
        self.assertIn('input_size', result)
        self.assertIn('output_size', result)
    
    def test_file_processor_backup_functionality(self):
        """测试文件备份功能"""
        operator = FileProcessorOperator(
            task_id='test_backup',
            input_path=self.test_input_file,
            output_path=self.test_output_file,
            processing_function='process_default',
            backup_original=True,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证备份文件存在
        backup_files = [f for f in os.listdir(self.test_dir) if f.endswith('.backup.')]
        self.assertTrue(len(backup_files) > 0)
    
    def test_file_processor_nonexistent_input_file(self):
        """测试输入文件不存在时的异常"""
        nonexistent_file = '/tmp/nonexistent_file.json'
        
        operator = FileProcessorOperator(
            task_id='test_nonexistent_file',
            input_path=nonexistent_file,
            output_path=self.test_output_file,
            processing_function='process_default',
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        
        with self.assertRaises(AirflowException) as context:
            operator.execute(context)
        
        self.assertIn("输入文件不存在", str(context.exception))


class TestDataValidatorOperator(unittest.TestCase):
    """测试数据验证操作符"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = tempfile.mkdtemp()
        self.dag = DAG(
            'test_dag',
            default_args={'owner': 'test', 'start_date': datetime(2024, 1, 1)},
            schedule_interval=None
        )
        
        # 创建测试数据文件
        self.test_data_file = os.path.join(self.test_dir, 'test_data.json')
        test_data = {
            'records': [
                {'id': 1, 'name': 'Alice', 'age': 25, 'email': 'alice@example.com'},
                {'id': 2, 'name': 'Bob', 'age': 30, 'email': 'bob@example.com'},
                {'id': 3, 'name': 'Charlie', 'age': 35, 'email': 'charlie@example.com'}
            ]
        }
        
        with open(self.test_data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
    
    def tearDown(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir)
    
    def test_data_validator_initialization(self):
        """测试数据验证操作符初始化"""
        validation_rules = {
            'age_check': {
                'type': 'range',
                'field': 'age',
                'min': 18,
                'max': 100
            }
        }
        
        operator = DataValidatorOperator(
            task_id='test_validator',
            data_source=self.test_data_file,
            validation_rules=validation_rules,
            dag=self.dag
        )
        
        self.assertEqual(operator.data_source, self.test_data_file)
        self.assertEqual(operator.validation_rules, validation_rules)
    
    def test_data_validator_completeness_check(self):
        """测试数据完整性检查"""
        validation_rules = {
            'completeness_check': {
                'type': 'completeness',
                'required_fields': ['id', 'name', 'age', 'email']
            }
        }
        
        operator = DataValidatorOperator(
            task_id='test_completeness',
            data_source=self.test_data_file,
            validation_rules=validation_rules,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证返回结果
        self.assertIn('total_checks', result)
        self.assertIn('passed_checks', result)
        self.assertIn('failed_checks', result)
        self.assertEqual(result['total_checks'], 1)
        self.assertEqual(result['passed_checks'], 1)
        self.assertEqual(result['failed_checks'], 0)
    
    def test_data_validator_range_check_failure(self):
        """测试数据范围检查失败"""
        # 创建包含无效年龄的数据
        invalid_data = {
            'records': [
                {'id': 1, 'name': 'Alice', 'age': 150, 'email': 'alice@example.com'}  # 年龄超出范围
            ]
        }
        
        invalid_data_file = os.path.join(self.test_dir, 'invalid_data.json')
        with open(invalid_data_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_data, f, ensure_ascii=False)
        
        validation_rules = {
            'age_range_check': {
                'type': 'range',
                'field': 'age',
                'min': 18,
                'max': 100
            }
        }
        
        operator = DataValidatorOperator(
            task_id='test_range_failure',
            data_source=invalid_data_file,
            validation_rules=validation_rules,
            fail_on_validation_error=True,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        
        with self.assertRaises(AirflowException) as context:
            operator.execute(context)
        
        self.assertIn("验证规则失败", str(context.exception))
    
    def test_data_validator_format_check(self):
        """测试数据格式检查"""
        validation_rules = {
            'email_format_check': {
                'type': 'format',
                'field': 'email',
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            }
        }
        
        operator = DataValidatorOperator(
            task_id='test_format',
            data_source=self.test_data_file,
            validation_rules=validation_rules,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证格式检查通过
        self.assertEqual(result['passed_checks'], 1)
        self.assertEqual(result['failed_checks'], 0)
    
    def test_data_validator_report_generation(self):
        """测试验证报告生成"""
        validation_rules = {
            'simple_check': {
                'type': 'completeness',
                'required_fields': ['id']
            }
        }
        
        operator = DataValidatorOperator(
            task_id='test_report',
            data_source=self.test_data_file,
            validation_rules=validation_rules,
            generate_report=True,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证报告文件生成
        report_files = [f for f in os.listdir('.') if f.startswith('validation_report_')]
        self.assertTrue(len(report_files) > 0)
        
        # 清理生成的报告文件
        for report_file in report_files:
            if os.path.exists(report_file):
                os.remove(report_file)


class TestAdvancedSensorOperator(unittest.TestCase):
    """测试高级传感器操作符"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = tempfile.mkdtemp()
        self.dag = DAG(
            'test_dag',
            default_args={'owner': 'test', 'start_date': datetime(2024, 1, 1)},
            schedule_interval=None
        )
        
        # 创建测试数据文件
        self.test_data_file = os.path.join(self.test_dir, 'sensor_test_data.json')
        test_data = {'items': []}  # 初始为空
        
        with open(self.test_data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
    
    def tearDown(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir)
    
    def test_sensor_operator_initialization(self):
        """测试传感器操作符初始化"""
        operator = AdvancedSensorOperator(
            task_id='test_sensor',
            data_source_type='file',
            data_source_config={'file_path': self.test_data_file, 'format': 'json'},
            condition_expression="len(data.get('items', [])) >= 5",
            polling_strategy='exponential_backoff',
            dag=self.dag
        )
        
        self.assertEqual(operator.data_source_type, 'file')
        self.assertEqual(operator.polling_strategy, 'exponential_backoff')
    
    def test_sensor_operator_condition_evaluation(self):
        """测试条件表达式评估"""
        # 更新数据文件，包含足够的数据项
        test_data = {'items': [{'id': i} for i in range(10)]}
        
        with open(self.test_data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
        
        operator = AdvancedSensorOperator(
            task_id='test_sensor_condition',
            data_source_type='file',
            data_source_config={'file_path': self.test_data_file, 'format': 'json'},
            condition_expression="len(data.get('items', [])) >= 5",
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.poke(context)
        
        # 条件应该满足
        self.assertTrue(result)
    
    def test_sensor_operator_polling_interval_update(self):
        """测试轮询间隔更新"""
        operator = AdvancedSensorOperator(
            task_id='test_polling_interval',
            data_source_type='file',
            data_source_config={'file_path': self.test_data_file, 'format': 'json'},
            condition_expression="len(data.get('items', [])) >= 100",  # 不可能满足的条件
            polling_strategy='exponential_backoff',
            initial_poke_interval=60,
            max_poke_interval=600,
            dag=self.dag
        )
        
        # 模拟失败情况
        operator._update_polling_interval(success=False)
        
        # 验证间隔增加
        self.assertGreater(operator.current_poke_interval, operator.initial_poke_interval)
    
    def test_sensor_operator_success_interval_reset(self):
        """测试成功时间隔重置"""
        operator = AdvancedSensorOperator(
            task_id='test_success_reset',
            data_source_type='file',
            data_source_config={'file_path': self.test_data_file, 'format': 'json'},
            condition_expression="True",  # 总是满足的条件
            polling_strategy='exponential_backoff',
            initial_poke_interval=60,
            dag=self.dag
        )
        
        # 先模拟失败增加间隔
        operator.current_poke_interval = 240
        operator.consecutive_failures = 3
        
        # 然后模拟成功
        operator._update_polling_interval(success=True)
        
        # 验证间隔重置
        self.assertEqual(operator.current_poke_interval, operator.initial_poke_interval)
        self.assertEqual(operator.consecutive_failures, 0)


class TestAsyncBatchProcessorOperator(unittest.TestCase):
    """测试异步批量处理操作符"""
    
    def setUp(self):
        """测试前置设置"""
        self.dag = DAG(
            'test_dag',
            default_args={'owner': 'test', 'start_date': datetime(2024, 1, 1)},
            schedule_interval=None
        )
        
        # 测试数据
        self.test_batch_data = [
            {'id': i, 'value': f'item_{i}', 'status': 'pending'}
            for i in range(50)
        ]
    
    def tearDown(self):
        """测试后置清理"""
        pass
    
    def test_batch_processor_initialization(self):
        """测试批量处理器初始化"""
        operator = AsyncBatchProcessorOperator(
            task_id='test_batch_processor',
            batch_data=self.test_batch_data,
            processing_function=lambda x: x,
            batch_size=10,
            max_concurrency=2,
            dag=self.dag
        )
        
        self.assertEqual(len(operator.batch_data), 50)
        self.assertEqual(operator.batch_size, 10)
        self.assertEqual(operator.max_concurrency, 2)
    
    def test_batch_processor_missing_required_params(self):
        """测试缺少必需参数时的异常"""
        with self.assertRaises(AirflowException) as context:
            AsyncBatchProcessorOperator(
                task_id='test_batch_processor',
                batch_data=[],  # 空数据
                processing_function=lambda x: x,
                dag=self.dag
            )
        
        self.assertIn("batch_data 不能为空", str(context.exception))
    
    def test_batch_processor_batch_creation(self):
        """测试批次创建逻辑"""
        operator = AsyncBatchProcessorOperator(
            task_id='test_batch_creation',
            batch_data=self.test_batch_data,
            processing_function=lambda x: x,
            batch_size=15,
            max_concurrency=3,
            dag=self.dag
        )
        
        # 计算批次数量
        total_batches = (len(self.test_batch_data) + 15 - 1) // 15
        self.assertEqual(total_batches, 4)  # 50个数据，每批15个，需要4批
    
    def test_batch_processor_successful_processing(self):
        """测试成功的批量处理"""
        def simple_processor(item):
            item['processed'] = True
            item['processed_at'] = datetime.now().isoformat()
            return item
        
        operator = AsyncBatchProcessorOperator(
            task_id='test_successful_processing',
            batch_data=self.test_batch_data,
            processing_function=simple_processor,
            batch_size=20,
            max_concurrency=2,
            error_handling='fail_fast',
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证处理结果
        self.assertIn('total_items', result)
        self.assertIn('processed_items', result)
        self.assertIn('successful_items', result)
        self.assertIn('failed_items', result)
        self.assertEqual(result['total_items'], 50)
        self.assertEqual(result['processed_items'], 50)
        self.assertEqual(result['successful_items'], 50)
        self.assertEqual(result['failed_items'], 0)
    
    def test_batch_processor_with_errors_continue_on_error(self):
        """测试包含错误的批量处理（继续处理策略）"""
        def error_prone_processor(item):
            if item['id'] % 10 == 0:  # 每10个项目中有一个会失败
                raise ValueError(f"Processing failed for item {item['id']}")
            item['processed'] = True
            return item
        
        operator = AsyncBatchProcessorOperator(
            task_id='test_with_errors_continue',
            batch_data=self.test_batch_data,
            processing_function=error_prone_processor,
            batch_size=10,
            max_concurrency=2,
            error_handling='continue_on_error',
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证错误处理结果
        self.assertEqual(result['total_items'], 50)
        self.assertEqual(result['processed_items'], 50)
        self.assertEqual(result['failed_items'], 5)  # id为0,10,20,30,40的项目会失败
        self.assertEqual(result['successful_items'], 45)
    
    def test_batch_processor_with_errors_fail_fast(self):
        """测试包含错误的批量处理（快速失败策略）"""
        def error_prone_processor(item):
            if item['id'] == 5:  # 第6个项目会失败
                raise ValueError("Processing failed")
            item['processed'] = True
            return item
        
        operator = AsyncBatchProcessorOperator(
            task_id='test_with_errors_fail_fast',
            batch_data=self.test_batch_data,
            processing_function=error_prone_processor,
            batch_size=10,
            max_concurrency=2,
            error_handling='fail_fast',
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        
        with self.assertRaises(AirflowException) as context:
            operator.execute(context)
        
        self.assertIn("批次处理失败，采用快速失败策略", str(context.exception))
    
    def test_batch_processor_progress_callback(self):
        """测试进度回调功能"""
        progress_calls = []
        
        def mock_progress_callback(progress, batch_index, total_batches):
            progress_calls.append({
                'progress': progress,
                'batch_index': batch_index,
                'total_batches': total_batches
            })
        
        operator = AsyncBatchProcessorOperator(
            task_id='test_progress_callback',
            batch_data=self.test_batch_data,
            processing_function=lambda x: x,
            batch_size=25,
            max_concurrency=2,
            progress_callback=mock_progress_callback,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        operator.execute(context)
        
        # 验证进度回调被调用
        self.assertGreater(len(progress_calls), 0)
        
        # 验证进度值
        for call in progress_calls:
            self.assertGreaterEqual(call['progress'], 0)
            self.assertLessEqual(call['progress'], 1.0)


class TestSmartDataProcessorOperator(unittest.TestCase):
    """测试智能数据处理操作符"""
    
    def setUp(self):
        """测试前置设置"""
        self.dag = DAG(
            'test_dag',
            default_args={'owner': 'test', 'start_date': datetime(2024, 1, 1)},
            schedule_interval=None
        )
        
        # 测试数据
        self.test_data = [
            {'id': 1, 'name': 'Alice', 'age': 25, 'salary': 50000, 'department': 'IT'},
            {'id': 2, 'name': 'Bob', 'age': 30, 'salary': 60000, 'department': 'HR'},
            {'id': 3, 'name': 'Charlie', 'age': 35, 'salary': 70000, 'department': 'IT'},
            {'id': 4, 'name': 'David', 'age': 28, 'salary': 55000, 'department': 'Finance'},
            {'id': 5, 'name': 'Eve', 'age': 32, 'salary': 65000, 'department': 'HR'}
        ]
    
    def tearDown(self):
        """测试后置清理"""
        pass
    
    def test_smart_processor_initialization(self):
        """测试智能处理器初始化"""
        processing_pipeline = [
            {
                'name': 'filter_adults',
                'type': 'filter',
                'params': {'condition': "item.get('age', 0) >= 18"}
            }
        ]
        
        operator = SmartDataProcessorOperator(
            task_id='test_smart_processor',
            input_data=self.test_data,
            processing_pipeline=processing_pipeline,
            dag=self.dag
        )
        
        self.assertEqual(operator.input_data, self.test_data)
        self.assertEqual(len(operator.processing_pipeline), 1)
    
    def test_smart_processor_filter_step(self):
        """测试过滤步骤"""
        processing_pipeline = [
            {
                'name': 'filter_it_department',
                'type': 'filter',
                'params': {'condition': "item.get('department') == 'IT'"}
            }
        ]
        
        operator = SmartDataProcessorOperator(
            task_id='test_filter_step',
            input_data=self.test_data,
            processing_pipeline=processing_pipeline,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证过滤结果
        processed_data = json.loads(result['processed_data'])
        self.assertEqual(len(processed_data), 2)  # IT部门只有2个人
        
        for item in processed_data:
            self.assertEqual(item['department'], 'IT')
    
    def test_smart_processor_transform_step(self):
        """测试转换步骤"""
        processing_pipeline = [
            {
                'name': 'normalize_names',
                'type': 'transform',
                'params': {
                    'transformations': {
                        'name_upper': "item['name'].upper()",
                        'salary_k': "item['salary'] / 1000"
                    }
                }
            }
        ]
        
        operator = SmartDataProcessorOperator(
            task_id='test_transform_step',
            input_data=self.test_data,
            processing_pipeline=processing_pipeline,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证转换结果
        processed_data = json.loads(result['processed_data'])
        
        for item in processed_data:
            self.assertIn('name_upper', item)
            self.assertIn('salary_k', item)
            self.assertEqual(item['name_upper'], item['name'].upper())
            self.assertEqual(item['salary_k'], item['salary'] / 1000)
    
    def test_smart_processor_aggregate_step(self):
        """测试聚合步骤"""
        processing_pipeline = [
            {
                'name': 'aggregate_by_department',
                'type': 'aggregate',
                'params': {
                    'group_by': 'department',
                    'functions': {
                        'total_salary': {'field': 'salary', 'type': 'sum'},
                        'avg_salary': {'field': 'salary', 'type': 'avg'},
                        'employee_count': {'type': 'count'}
                    }
                }
            }
        ]
        
        operator = SmartDataProcessorOperator(
            task_id='test_aggregate_step',
            input_data=self.test_data,
            processing_pipeline=processing_pipeline,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证聚合结果
        processed_data = json.loads(result['processed_data'])
        self.assertEqual(len(processed_data), 3)  # 3个部门
        
        # 验证聚合统计
        for dept_data in processed_data:
            self.assertIn('group_key', dept_data)
            self.assertIn('count', dept_data)
            self.assertIn('total_salary', dept_data)
            self.assertIn('avg_salary', dept_data)
    
    def test_smart_processor_quality_checks(self):
        """测试数据质量检查"""
        processing_pipeline = [
            {
                'name': 'simple_filter',
                'type': 'filter',
                'params': {'condition': "item.get('age', 0) >= 0"}
            }
        ]
        
        quality_checks = [
            {
                'name': 'completeness_check',
                'type': 'completeness',
                'params': {'required_fields': ['id', 'name', 'age']}
            },
            {
                'name': 'age_validity_check',
                'type': 'validity',
                'params': {
                    'rules': [
                        {'field': 'age', 'type': 'integer'},
                        {'field': 'salary', 'type': 'integer'}
                    ]
                }
            }
        ]
        
        operator = SmartDataProcessorOperator(
            task_id='test_quality_checks',
            input_data=self.test_data,
            processing_pipeline=processing_pipeline,
            quality_checks=quality_checks,
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证质量报告
        self.assertIn('quality_report', result['processing_report'])
        quality_report = result['processing_report']['quality_report']
        
        self.assertEqual(quality_report['total_checks'], 2)
        self.assertEqual(quality_report['passed_checks'], 2)
        self.assertEqual(quality_report['failed_checks'], 0)
        self.assertGreater(quality_report['quality_score'], 0)
    
    def test_smart_processor_csv_output_format(self):
        """测试CSV输出格式"""
        processing_pipeline = [
            {
                'name': 'simple_transform',
                'type': 'transform',
                'params': {
                    'transformations': {
                        'name_length': "len(item['name'])"
                    }
                }
            }
        ]
        
        operator = SmartDataProcessorOperator(
            task_id='test_csv_output',
            input_data=self.test_data,
            processing_pipeline=processing_pipeline,
            output_format='csv',
            dag=self.dag
        )
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        # 验证CSV格式输出
        csv_output = result['processed_data']
        lines = csv_output.strip().split('\n')
        
        # 验证标题行
        header = lines[0]
        self.assertIn('id', header)
        self.assertIn('name', header)
        self.assertIn('age', header)
        self.assertIn('salary', header)
        self.assertIn('department', header)
        self.assertIn('name_length', header)
        
        # 验证数据行数
        self.assertEqual(len(lines), 6)  # 1行标题 + 5行数据


class TestIntegrationScenarios(unittest.TestCase):
    """集成测试场景"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = tempfile.mkdtemp()
        self.dag = DAG(
            'integration_test_dag',
            default_args={'owner': 'test', 'start_date': datetime(2024, 1, 1)},
            schedule_interval=None
        )
    
    def tearDown(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir)
    
    def test_complete_data_processing_workflow(self):
        """测试完整的数据处理工作流"""
        # 创建输入文件
        input_file = os.path.join(self.test_dir, 'input_data.json')
        output_file = os.path.join(self.test_dir, 'output_data.json')
        
        input_data = {
            'records': [
                {'id': 1, 'name': 'Alice Johnson', 'age': 25, 'salary': 50000, 'department': 'IT'},
                {'id': 2, 'name': 'Bob Smith', 'age': 30, 'salary': 60000, 'department': 'HR'},
                {'id': 3, 'name': 'Charlie Brown', 'age': 35, 'salary': 70000, 'department': 'IT'},
                {'id': 4, 'name': 'Diana Prince', 'age': 28, 'salary': 55000, 'department': 'Finance'},
                {'id': 5, 'name': 'Eve Wilson', 'age': 32, 'salary': 65000, 'department': 'HR'}
            ]
        }
        
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(input_data, f, ensure_ascii=False)
        
        # 1. 文件处理任务 - 格式化JSON
        format_task = FileProcessorOperator(
            task_id='format_input_file',
            input_path=input_file,
            output_path=os.path.join(self.test_dir, 'formatted_data.json'),
            processing_function='process_json',
            dag=self.dag
        )
        
        # 2. 数据验证任务
        validation_rules = {
            'data_completeness': {
                'type': 'completeness',
                'required_fields': ['id', 'name', 'age', 'salary', 'department']
            },
            'age_validation': {
                'type': 'range',
                'field': 'age',
                'min': 18,
                'max': 65
            },
            'salary_validation': {
                'type': 'range',
                'field': 'salary',
                'min': 30000,
                'max': 200000
            }
        }
        
        validate_task = DataValidatorOperator(
            task_id='validate_data_quality',
            data_source=os.path.join(self.test_dir, 'formatted_data.json'),
            validation_rules=validation_rules,
            fail_on_validation_error=True,
            generate_report=True,
            dag=self.dag
        )
        
        # 3. 智能数据处理任务
        processing_pipeline = [
            {
                'name': 'filter_valid_records',
                'type': 'filter',
                'params': {'condition': "item.get('age', 0) >= 18"}
            },
            {
                'name': 'normalize_names',
                'type': 'transform',
                'params': {
                    'transformations': {
                        'name_upper': "item['name'].upper()",
                        'salary_k': "item['salary'] / 1000"
                    }
                }
            },
            {
                'name': 'aggregate_by_department',
                'type': 'aggregate',
                'params': {
                    'group_by': 'department',
                    'functions': {
                        'employee_count': {'type': 'count'},
                        'avg_salary': {'field': 'salary', 'type': 'avg'},
                        'total_salary': {'field': 'salary', 'type': 'sum'}
                    }
                }
            }
        ]
        
        quality_checks = [
            {
                'name': 'department_completeness',
                'type': 'completeness',
                'params': {'required_fields': ['group_key', 'count', 'avg_salary']}
            }
        ]
        
        process_task = SmartDataProcessorOperator(
            task_id='process_data_intelligently',
            input_data=os.path.join(self.test_dir, 'formatted_data.json'),
            processing_pipeline=processing_pipeline,
            quality_checks=quality_checks,
            output_format='json',
            dag=self.dag
        )
        
        # 4. 最终文件处理任务 - 保存结果
        final_format_task = FileProcessorOperator(
            task_id='format_final_output',
            input_path=os.path.join(self.test_dir, 'processed_data.json'),
            output_path=output_file,
            processing_function='process_json',
            dag=self.dag
        )
        
        # 设置任务依赖
        format_task >> validate_task >> process_task >> final_format_task
        
        # 执行工作流（模拟）
        context = {'task_instance': Mock()}
        
        # 执行各个任务
        format_result = format_task.execute(context)
        self.assertIsNotNone(format_result)
        
        validate_result = validate_task.execute(context)
        self.assertEqual(validate_result['passed_checks'], 3)
        self.assertEqual(validate_result['failed_checks'], 0)
        
        process_result = process_task.execute(context)
        self.assertIn('processed_data', process_result)
        self.assertIn('processing_report', process_result)
        
        # 验证最终输出文件存在
        self.assertTrue(os.path.exists(output_file))
        
        # 验证输出内容
        with open(output_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
        
        self.assertIsInstance(final_data, list)
        self.assertEqual(len(final_data), 3)  # 3个部门


class TestPerformanceBenchmarks(unittest.TestCase):
    """性能基准测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.dag = DAG(
            'performance_test_dag',
            default_args={'owner': 'test', 'start_date': datetime(2024, 1, 1)},
            schedule_interval=None
        )
    
    def test_batch_processor_performance_large_dataset(self):
        """测试大数据集上的批量处理器性能"""
        # 创建大型测试数据集
        large_dataset = [
            {'id': i, 'data': f'item_{i}', 'value': i * 10}
            for i in range(10000)
        ]
        
        def simple_processor(item):
            item['processed_value'] = item['value'] * 2
            item['processed'] = True
            return item
        
        operator = AsyncBatchProcessorOperator(
            task_id='test_large_dataset_performance',
            batch_data=large_dataset,
            processing_function=simple_processor,
            batch_size=500,
            max_concurrency=8,
            dag=self.dag
        )
        
        import time
        start_time = time.time()
        
        context = {'task_instance': Mock()}
        result = operator.execute(context)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 验证处理结果
        self.assertEqual(result['total_items'], 10000)
        self.assertEqual(result['processed_items'], 10000)
        self.assertEqual(result['successful_items'], 10000)
        
        # 验证性能（应该在合理时间内完成）
        self.assertLess(processing_time, 30)  # 10,000条记录应该在30秒内完成
        
        # 计算处理速度
        processing_speed = result['processed_items'] / processing_time
        print(f"处理速度: {processing_speed:.2f} 项目/秒")
        
        # 验证批次处理统计
        self.assertGreater(result['total_batches'], 0)
        self.assertEqual(result['failed_batches'], 0)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestFileProcessorOperator,
        TestDataValidatorOperator,
        TestAdvancedSensorOperator,
        TestAsyncBatchProcessorOperator,
        TestSmartDataProcessorOperator,
        TestIntegrationScenarios,
        TestPerformanceBenchmarks
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("开始运行自定义操作符测试...")
    
    # 运行所有测试
    success = run_all_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败！")
    
    exit(0 if success else 1)