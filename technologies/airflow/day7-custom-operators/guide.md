# Day 7: 自定义操作符开发指南

## 概述

自定义操作符是Airflow中扩展功能的核心机制，允许用户创建满足特定业务需求的工作流组件。本指南将详细介绍自定义操作符的开发最佳实践、高级技术和部署策略。

## 学习目标

### 基础开发技能
- 理解Airflow操作符架构和生命周期
- 掌握BaseOperator核心方法和属性
- 学会创建简单和复杂的自定义操作符
- 实现操作符参数验证和错误处理

### 高级开发技术
- 实现异步操作符和并发处理
- 开发智能传感器和轮询机制
- 构建多步骤数据处理管道
- 集成外部系统和API

### 最佳实践
- 编写可测试和可维护的操作符代码
- 实现操作符的日志记录和监控
- 优化性能和资源使用
- 遵循Airflow开发规范

### 测试与部署
- 编写单元测试和集成测试
- 实现操作符的版本控制
- 部署到生产环境
- 维护和升级策略

## 课程内容

### 1. 操作符基础架构

#### BaseOperator核心组件
```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class CustomOperator(BaseOperator):
    """
    自定义操作符模板
    
    参数说明:
        task_id: 任务ID
        param1: 参数1描述
        param2: 参数2描述
        *args, **kwargs: 传递给BaseOperator的其他参数
    """
    
    @apply_defaults
    def __init__(
        self,
        param1,
        param2=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.param1 = param1
        self.param2 = param2
        
        # 参数验证
        if not param1:
            raise ValueError("param1不能为空")
    
    def execute(self, context):
        """执行操作符的主要逻辑"""
        self.log.info(f"开始执行 {self.task_id}")
        
        try:
            # 操作符逻辑
            result = self._process_data()
            
            self.log.info(f"操作符 {self.task_id} 执行成功")
            return result
            
        except Exception as e:
            self.log.error(f"操作符 {self.task_id} 执行失败: {str(e)}")
            raise
    
    def _process_data(self):
        """具体的处理逻辑"""
        # 实现具体的业务逻辑
        pass
```

#### 操作符生命周期
1. **初始化**: `__init__`方法设置参数和属性
2. **预处理**: `pre_execute`方法执行前的准备工作
3. **执行**: `execute`方法执行主要逻辑
4. **后处理**: `post_execute`方法执行后的清理工作
5. **完成**: 返回结果或抛出异常

### 2. 简单操作符开发

#### 文件处理操作符
```python
import os
import json
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException

class FileProcessorOperator(BaseOperator):
    """文件处理操作符"""
    
    def __init__(
        self,
        input_path,
        output_path,
        processing_function,
        backup_original=False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input_path = input_path
        self.output_path = output_path
        self.processing_function = processing_function
        self.backup_original = backup_original
        
        # 参数验证
        if not input_path or not output_path:
            raise AirflowException("input_path和output_path是必需参数")
    
    def execute(self, context):
        """执行文件处理"""
        self.log.info(f"开始处理文件: {self.input_path}")
        
        # 检查输入文件
        if not os.path.exists(self.input_path):
            raise AirflowException(f"输入文件不存在: {self.input_path}")
        
        try:
            # 读取文件
            with open(self.input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 备份原始文件
            if self.backup_original:
                self._backup_file(self.input_path)
            
            # 处理数据
            processed_data = self._process_content(content)
            
            # 写入输出文件
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(processed_data)
            
            self.log.info(f"文件处理完成: {self.output_path}")
            
            return {
                'input_file': self.input_path,
                'output_file': self.output_path,
                'input_size': len(content),
                'output_size': len(processed_data)
            }
            
        except Exception as e:
            self.log.error(f"文件处理失败: {str(e)}")
            raise AirflowException(f"文件处理失败: {str(e)}")
    
    def _process_content(self, content):
        """处理文件内容"""
        if self.processing_function == 'process_json':
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif self.processing_function == 'process_default':
            return content
        else:
            # 自定义处理函数
            return self.processing_function(content)
    
    def _backup_file(self, file_path):
        """备份文件"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{file_path}.backup.{timestamp}"
        shutil.copy2(file_path, backup_path)
        self.log.info(f"文件已备份到: {backup_path}")
```

#### 数据验证操作符
```python
import json
import re
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException

class DataValidatorOperator(BaseOperator):
    """数据验证操作符"""
    
    def __init__(
        self,
        data_source,
        validation_rules,
        fail_on_validation_error=False,
        generate_report=False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.data_source = data_source
        self.validation_rules = validation_rules
        self.fail_on_validation_error = fail_on_validation_error
        self.generate_report = generate_report
    
    def execute(self, context):
        """执行数据验证"""
        self.log.info("开始数据验证")
        
        # 加载数据
        data = self._load_data()
        
        # 执行验证
        validation_results = self._validate_data(data)
        
        # 生成报告
        if self.generate_report:
            self._generate_validation_report(validation_results)
        
        # 检查验证结果
        if validation_results['failed_checks'] > 0 and self.fail_on_validation_error:
            raise AirflowException(f"验证失败: {validation_results['failed_checks']} 个检查未通过")
        
        return validation_results
    
    def _load_data(self):
        """加载数据"""
        if isinstance(self.data_source, str):
            with open(self.data_source, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.data_source
    
    def _validate_data(self, data):
        """验证数据"""
        results = {
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'details': []
        }
        
        for rule_name, rule_config in self.validation_rules.items():
            results['total_checks'] += 1
            
            try:
                if self._check_rule(data, rule_config):
                    results['passed_checks'] += 1
                    results['details'].append({
                        'rule': rule_name,
                        'status': 'passed',
                        'message': '验证通过'
                    })
                else:
                    results['failed_checks'] += 1
                    results['details'].append({
                        'rule': rule_name,
                        'status': 'failed',
                        'message': '验证失败'
                    })
                    
            except Exception as e:
                results['failed_checks'] += 1
                results['details'].append({
                    'rule': rule_name,
                    'status': 'error',
                    'message': f'验证错误: {str(e)}'
                })
        
        return results
    
    def _check_rule(self, data, rule_config):
        """检查单个规则"""
        rule_type = rule_config['type']
        
        if rule_type == 'completeness':
            return self._check_completeness(data, rule_config)
        elif rule_type == 'range':
            return self._check_range(data, rule_config)
        elif rule_type == 'format':
            return self._check_format(data, rule_config)
        else:
            raise ValueError(f"不支持的验证类型: {rule_type}")
    
    def _check_completeness(self, data, rule_config):
        """检查完整性"""
        required_fields = rule_config.get('required_fields', [])
        
        if isinstance(data, list):
            for item in data:
                for field in required_fields:
                    if field not in item or item[field] is None:
                        return False
        else:
            for field in required_fields:
                if field not in data or data[field] is None:
                    return False
        
        return True
    
    def _check_range(self, data, rule_config):
        """检查范围"""
        field = rule_config['field']
        min_val = rule_config.get('min')
        max_val = rule_config.get('max')
        
        if isinstance(data, list):
            for item in data:
                value = item.get(field)
                if value is not None:
                    if min_val is not None and value < min_val:
                        return False
                    if max_val is not None and value > max_val:
                        return False
        
        return True
    
    def _check_format(self, data, rule_config):
        """检查格式"""
        field = rule_config['field']
        pattern = rule_config['pattern']
        
        if isinstance(data, list):
            for item in data:
                value = item.get(field)
                if value is not None and not re.match(pattern, str(value)):
                    return False
        
        return True
    
    def _generate_validation_report(self, results):
        """生成验证报告"""
        from datetime import datetime
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_checks': results['total_checks'],
            'passed_checks': results['passed_checks'],
            'failed_checks': results['failed_checks'],
            'success_rate': results['passed_checks'] / results['total_checks'] if results['total_checks'] > 0 else 0,
            'details': results['details']
        }
        
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log.info(f"验证报告已生成: {report_file}")
```

### 3. 高级操作符开发

#### 智能传感器操作符
```python
import time
import json
import requests
from airflow.sensors.base import BaseSensorOperator
from airflow.exceptions import AirflowException

class AdvancedSensorOperator(BaseSensorOperator):
    """高级传感器操作符 - 支持多种数据源和智能轮询"""
    
    def __init__(
        self,
        data_source_type,
        data_source_config,
        condition_expression,
        polling_strategy='fixed',
        initial_poke_interval=60,
        max_poke_interval=600,
        exponential_backoff_multiplier=2,
        timeout=60 * 60 * 24 * 7,  # 7天
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.data_source_type = data_source_type
        self.data_source_config = data_source_config
        self.condition_expression = condition_expression
        self.polling_strategy = polling_strategy
        self.initial_poke_interval = initial_poke_interval
        self.max_poke_interval = max_poke_interval
        self.exponential_backoff_multiplier = exponential_backoff_multiplier
        self.current_poke_interval = initial_poke_interval
        self.consecutive_failures = 0
    
    def poke(self, context):
        """检查条件是否满足"""
        self.log.info(f"开始检查条件: {self.condition_expression}")
        
        try:
            # 获取数据
            data = self._fetch_data()
            
            # 评估条件
            condition_met = self._evaluate_condition(data)
            
            # 更新轮询间隔
            self._update_polling_interval(condition_met)
            
            if condition_met:
                self.log.info("条件已满足，传感器触发")
                return True
            else:
                self.log.info(f"条件未满足，当前轮询间隔: {self.current_poke_interval}秒")
                return False
                
        except Exception as e:
            self.log.error(f"传感器检查失败: {str(e)}")
            self._update_polling_interval(success=False)
            return False
    
    def _fetch_data(self):
        """获取数据"""
        if self.data_source_type == 'file':
            return self._fetch_from_file()
        elif self.data_source_type == 'api':
            return self._fetch_from_api()
        elif self.data_source_type == 'database':
            return self._fetch_from_database()
        else:
            raise AirflowException(f"不支持的数据源类型: {self.data_source_type}")
    
    def _fetch_from_file(self):
        """从文件获取数据"""
        file_path = self.data_source_config['file_path']
        format_type = self.data_source_config.get('format', 'json')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if format_type == 'json':
            return json.loads(content)
        else:
            return content
    
    def _fetch_from_api(self):
        """从API获取数据"""
        url = self.data_source_config['url']
        method = self.data_source_config.get('method', 'GET')
        headers = self.data_source_config.get('headers', {})
        params = self.data_source_config.get('params', {})
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def _fetch_from_database(self):
        """从数据库获取数据"""
        # 这里可以实现数据库查询逻辑
        # 使用Airflow的连接管理器
        pass
    
    def _evaluate_condition(self, data):
        """评估条件表达式"""
        try:
            # 使用安全的eval环境
            safe_globals = {"__builtins__": {}}
            safe_locals = {"data": data}
            
            return eval(self.condition_expression, safe_globals, safe_locals)
            
        except Exception as e:
            self.log.error(f"条件评估失败: {str(e)}")
            return False
    
    def _update_polling_interval(self, success=True):
        """更新轮询间隔"""
        if self.polling_strategy == 'fixed':
            return
        
        elif self.polling_strategy == 'exponential_backoff':
            if success:
                # 成功时重置间隔
                self.current_poke_interval = self.initial_poke_interval
                self.consecutive_failures = 0
            else:
                # 失败时增加间隔
                self.consecutive_failures += 1
                new_interval = self.current_poke_interval * self.exponential_backoff_multiplier
                self.current_poke_interval = min(new_interval, self.max_poke_interval)
        
        elif self.polling_strategy == 'adaptive':
            # 自适应策略：基于历史成功率调整间隔
            pass
```

#### 异步批量处理操作符
```python
import asyncio
import concurrent.futures
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException

class AsyncBatchProcessorOperator(BaseOperator):
    """异步批量处理操作符"""
    
    def __init__(
        self,
        batch_data,
        processing_function,
        batch_size=100,
        max_concurrency=5,
        error_handling='fail_fast',  # 'fail_fast' 或 'continue_on_error'
        progress_callback=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.batch_data = batch_data
        self.processing_function = processing_function
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency
        self.error_handling = error_handling
        self.progress_callback = progress_callback
        
        # 参数验证
        if not batch_data:
            raise AirflowException("batch_data不能为空")
        if not callable(processing_function):
            raise AirflowException("processing_function必须是可调用的函数")
    
    def execute(self, context):
        """执行批量处理"""
        self.log.info(f"开始批量处理，数据量: {len(self.batch_data)}")
        
        # 创建批次
        batches = self._create_batches()
        
        # 处理批次
        results = self._process_batches(batches)
        
        # 汇总结果
        summary = self._summarize_results(results)
        
        self.log.info(f"批量处理完成: {summary}")
        return summary
    
    def _create_batches(self):
        """创建批次"""
        batches = []
        for i in range(0, len(self.batch_data), self.batch_size):
            batch = self.batch_data[i:i + self.batch_size]
            batches.append({
                'batch_index': len(batches),
                'data': batch,
                'size': len(batch)
            })
        
        self.log.info(f"创建了 {len(batches)} 个批次，每批大小: {self.batch_size}")
        return batches
    
    def _process_batches(self, batches):
        """处理批次"""
        results = []
        
        if self.max_concurrency == 1:
            # 串行处理
            for batch in batches:
                result = self._process_single_batch(batch)
                results.append(result)
                
                # 更新进度
                if self.progress_callback:
                    progress = len(results) / len(batches)
                    self.progress_callback(progress, batch['batch_index'], len(batches))
        else:
            # 并行处理
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
                future_to_batch = {
                    executor.submit(self._process_single_batch, batch): batch
                    for batch in batches
                }
                
                for future in concurrent.futures.as_completed(future_to_batch):
                    batch = future_to_batch[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # 更新进度
                        if self.progress_callback:
                            progress = len(results) / len(batches)
                            self.progress_callback(progress, batch['batch_index'], len(batches))
                            
                    except Exception as e:
                        self.log.error(f"批次 {batch['batch_index']} 处理失败: {str(e)}")
                        
                        if self.error_handling == 'fail_fast':
                            raise AirflowException(f"批次处理失败，采用快速失败策略: {str(e)}")
                        else:
                            # 继续处理其他批次
                            results.append({
                                'batch_index': batch['batch_index'],
                                'status': 'failed',
                                'error': str(e)
                            })
        
        return results
    
    def _process_single_batch(self, batch):
        """处理单个批次"""
        self.log.info(f"开始处理批次 {batch['batch_index']}, 大小: {batch['size']}")
        
        processed_items = []
        failed_items = 0
        
        for item in batch['data']:
            try:
                processed_item = self.processing_function(item)
                processed_items.append(processed_item)
            except Exception as e:
                failed_items += 1
                self.log.warning(f"处理项目失败: {str(e)}")
                
                if self.error_handling == 'fail_fast':
                    raise AirflowException(f"项目处理失败，采用快速失败策略: {str(e)}")
        
        return {
            'batch_index': batch['batch_index'],
            'status': 'completed',
            'processed_items': len(processed_items),
            'failed_items': failed_items,
            'processed_data': processed_items
        }
    
    def _summarize_results(self, results):
        """汇总结果"""
        total_items = len(self.batch_data)
        processed_items = 0
        successful_items = 0
        failed_items = 0
        total_batches = len(results)
        failed_batches = 0
        
        for result in results:
            if result['status'] == 'completed':
                processed_items += result['processed_items']
                successful_items += result['processed_items']
                failed_items += result['failed_items']
            else:
                failed_batches += 1
        
        return {
            'total_items': total_items,
            'processed_items': processed_items,
            'successful_items': successful_items,
            'failed_items': failed_items,
            'total_batches': total_batches,
            'failed_batches': failed_batches,
            'success_rate': successful_items / total_items if total_items > 0 else 0
        }
```

#### 智能数据处理操作符
```python
import json
import pandas as pd
from airflow.models import BaseOperator
from airflow.exceptions import AirflowException

class SmartDataProcessorOperator(BaseOperator):
    """智能数据处理操作符 - 多步骤数据处理管道"""
    
    def __init__(
        self,
        input_data,
        processing_pipeline,
        quality_checks=None,
        output_format='json',  # 'json', 'csv', 'dict'
        enable_caching=False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input_data = input_data
        self.processing_pipeline = processing_pipeline
        self.quality_checks = quality_checks or []
        self.output_format = output_format
        self.enable_caching = enable_caching
        
        # 参数验证
        if not input_data:
            raise AirflowException("input_data不能为空")
        if not processing_pipeline:
            raise AirflowException("processing_pipeline不能为空")
    
    def execute(self, context):
        """执行数据处理管道"""
        self.log.info("开始智能数据处理")
        
        # 加载输入数据
        data = self._load_input_data()
        
        # 执行处理管道
        processed_data = self._execute_pipeline(data)
        
        # 执行质量检查
        quality_report = self._execute_quality_checks(processed_data)
        
        # 格式化输出
        formatted_output = self._format_output(processed_data)
        
        # 生成处理报告
        processing_report = {
            'input_records': len(data),
            'output_records': len(processed_data),
            'processing_steps': len(self.processing_pipeline),
            'quality_checks': len(self.quality_checks),
            'quality_score': quality_report.get('quality_score', 0),
            'quality_report': quality_report
        }
        
        self.log.info(f"数据处理完成: {processing_report}")
        
        return {
            'processed_data': formatted_output,
            'processing_report': processing_report
        }
    
    def _load_input_data(self):
        """加载输入数据"""
        if isinstance(self.input_data, str):
            # 文件路径
            with open(self.input_data, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.input_data
    
    def _execute_pipeline(self, data):
        """执行处理管道"""
        current_data = data
        
        for step in self.processing_pipeline:
            step_name = step['name']
            step_type = step['type']
            step_params = step.get('params', {})
            
            self.log.info(f"执行处理步骤: {step_name} (类型: {step_type})")
            
            if step_type == 'filter':
                current_data = self._apply_filter(current_data, step_params)
            elif step_type == 'transform':
                current_data = self._apply_transform(current_data, step_params)
            elif step_type == 'aggregate':
                current_data = self._apply_aggregate(current_data, step_params)
            else:
                raise AirflowException(f"不支持的步骤类型: {step_type}")
            
            self.log.info(f"步骤 {step_name} 完成，记录数: {len(current_data)}")
        
        return current_data
    
    def _apply_filter(self, data, params):
        """应用过滤器"""
        condition = params['condition']
        
        # 使用安全的eval环境
        safe_globals = {"__builtins__": {}}
        
        filtered_data = []
        for item in data:
            safe_locals = {"item": item}
            if eval(condition, safe_globals, safe_locals):
                filtered_data.append(item)
        
        return filtered_data
    
    def _apply_transform(self, data, params):
        """应用转换"""
        transformations = params.get('transformations', {})
        
        transformed_data = []
        for item in data:
            new_item = item.copy()
            
            # 使用安全的eval环境
            safe_globals = {"__builtins__": {}}
            
            for field_name, expression in transformations.items():
                safe_locals = {"item": item}
                try:
                    new_item[field_name] = eval(expression, safe_globals, safe_locals)
                except Exception as e:
                    self.log.warning(f"转换字段 {field_name} 失败: {str(e)}")
                    new_item[field_name] = None
            
            transformed_data.append(new_item)
        
        return transformed_data
    
    def _apply_aggregate(self, data, params):
        """应用聚合"""
        group_by = params['group_by']
        functions = params['functions']
        
        # 转换为DataFrame便于聚合
        df = pd.DataFrame(data)
        
        # 按指定字段分组
        grouped = df.groupby(group_by)
        
        # 执行聚合函数
        aggregated_data = []
        for group_key, group_df in grouped:
            group_result = {'group_key': group_key, 'count': len(group_df)}
            
            for func_name, func_config in functions.items():
                func_type = func_config['type']
                
                if func_type == 'count':
                    group_result[func_name] = len(group_df)
                elif func_type == 'sum':
                    field = func_config['field']
                    group_result[func_name] = group_df[field].sum()
                elif func_type == 'avg':
                    field = func_config['field']
                    group_result[func_name] = group_df[field].mean()
                elif func_type == 'min':
                    field = func_config['field']
                    group_result[func_name] = group_df[field].min()
                elif func_type == 'max':
                    field = func_config['field']
                    group_result[func_name] = group_df[field].max()
            
            aggregated_data.append(group_result)
        
        return aggregated_data
    
    def _execute_quality_checks(self, data):
        """执行质量检查"""
        if not self.quality_checks:
            return {'quality_score': 100, 'passed_checks': 0, 'failed_checks': 0}
        
        passed_checks = 0
        failed_checks = 0
        
        for check in self.quality_checks:
            check_name = check['name']
            check_type = check['type']
            check_params = check.get('params', {})
            
            try:
                if self._perform_quality_check(data, check_type, check_params):
                    passed_checks += 1
                else:
                    failed_checks += 1
                    
            except Exception as e:
                self.log.warning(f"质量检查 {check_name} 失败: {str(e)}")
                failed_checks += 1
        
        quality_score = (passed_checks / len(self.quality_checks)) * 100 if self.quality_checks else 100
        
        return {
            'quality_score': quality_score,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks
        }
    
    def _perform_quality_check(self, data, check_type, params):
        """执行质量检查"""
        if check_type == 'completeness':
            required_fields = params.get('required_fields', [])
            for item in data:
                for field in required_fields:
                    if field not in item or item[field] is None:
                        return False
            return True
        
        elif check_type == 'validity':
            rules = params.get('rules', [])
            for item in data:
                for rule in rules:
                    field = rule['field']
                    field_type = rule['type']
                    
                    if field in item and item[field] is not None:
                        value = item[field]
                        if field_type == 'integer' and not isinstance(value, int):
                            return False
                        elif field_type == 'float' and not isinstance(value, (int, float)):
                            return False
                        elif field_type == 'string' and not isinstance(value, str):
                            return False
            return True
        
        return True
    
    def _format_output(self, data):
        """格式化输出"""
        if self.output_format == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif self.output_format == 'csv':
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                return df.to_csv(index=False)
            else:
                return ""
        elif self.output_format == 'dict':
            return data
        else:
            return str(data)
```

### 4. 操作符测试策略

#### 单元测试框架
```python
import unittest
from unittest.mock import Mock, patch
from airflow.models import DAG, TaskInstance
from airflow.utils.state import State
from datetime import datetime

class TestCustomOperators(unittest.TestCase):
    """自定义操作符测试基类"""
    
    def setUp(self):
        """测试前置设置"""
        self.dag = DAG(
            'test_dag',
            default_args={
                'owner': 'test',
                'start_date': datetime(2024, 1, 1)
            },
            schedule_interval=None
        )
        
        self.context = {
            'task_instance': Mock(),
            'dag': self.dag,
            'execution_date': datetime(2024, 1, 1)
        }
    
    def test_operator_initialization(self):
        """测试操作符初始化"""
        operator = YourCustomOperator(
            task_id='test_task',
            param1='value1',
            param2='value2',
            dag=self.dag
        )
        
        self.assertEqual(operator.task_id, 'test_task')
        self.assertEqual(operator.param1, 'value1')
        self.assertEqual(operator.param2, 'value2')
    
    def test_operator_parameter_validation(self):
        """测试参数验证"""
        with self.assertRaises(ValueError):
            YourCustomOperator(
                task_id='test_task',
                param1='',  # 无效参数
                dag=self.dag
            )
    
    def test_operator_execution(self):
        """测试操作符执行"""
        operator = YourCustomOperator(
            task_id='test_task',
            param1='valid_value',
            dag=self.dag
        )
        
        result = operator.execute(self.context)
        
        # 验证执行结果
        self.assertIsNotNone(result)
        # 添加更多验证逻辑
    
    def test_operator_error_handling(self):
        """测试错误处理"""
        operator = YourCustomOperator(
            task_id='test_task',
            param1='error_value',  # 会触发错误的参数
            dag=self.dag
        )
        
        with self.assertRaises(AirflowException):
            operator.execute(self.context)
```

#### 集成测试
```python
import tempfile
import json
import os
from airflow.models import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime

class TestOperatorIntegration:
    """操作符集成测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流"""
        # 创建测试数据
        test_data = {
            'records': [
                {'id': 1, 'name': 'Alice', 'age': 25},
                {'id': 2, 'name': 'Bob', 'age': 30}
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建输入文件
            input_file = os.path.join(temp_dir, 'input.json')
            with open(input_file, 'w') as f:
                json.dump(test_data, f)
            
            # 创建DAG
            dag = DAG(
                'integration_test_dag',
                default_args={'start_date': datetime(2024, 1, 1)},
                schedule_interval=None
            )
            
            # 创建任务
            start_task = DummyOperator(task_id='start', dag=dag)
            
            process_task = FileProcessorOperator(
                task_id='process_data',
                input_path=input_file,
                output_path=os.path.join(temp_dir, 'output.json'),
                processing_function='process_json',
                dag=dag
            )
            
            validate_task = DataValidatorOperator(
                task_id='validate_data',
                data_source=os.path.join(temp_dir, 'output.json'),
                validation_rules={
                    'completeness': {
                        'type': 'completeness',
                        'required_fields': ['id', 'name', 'age']
                    }
                },
                dag=dag
            )
            
            end_task = DummyOperator(task_id='end', dag=dag)
            
            # 设置依赖
            start_task >> process_task >> validate_task >> end_task
            
            # 执行测试
            context = {'execution_date': datetime.now()}
            
            # 执行各个任务
            process_result = process_task.execute(context)
            validate_result = validate_task.execute(context)
            
            # 验证结果
            assert os.path.exists(process_result['output_file'])
            assert validate_result['passed_checks'] > 0
```

### 5. 最佳实践总结

#### 设计原则
1. **单一职责**: 每个操作符只负责一个明确的功能
2. **可配置性**: 提供丰富的配置选项
3. **错误处理**: 完善的错误处理和恢复机制
4. **可测试性**: 易于编写单元测试和集成测试
5. **性能优化**: 考虑大数据量和并发场景

#### 代码规范
1. **文档字符串**: 详细的参数说明和使用示例
2. **类型提示**: 使用类型注解提高代码可读性
3. **日志记录**: 适当的日志级别和详细信息
4. **参数验证**: 在初始化时验证所有必需参数
5. **异常处理**: 提供有意义的错误信息

#### 性能考虑
1. **资源管理**: 及时释放文件句柄和数据库连接
2. **批量处理**: 支持批量操作减少I/O开销
3. **并发控制**: 合理设置并发度避免资源竞争
4. **缓存机制**: 适当使用缓存提高性能
5. **内存管理**: 避免加载过大的数据集到内存

#### 安全考虑
1. **输入验证**: 验证所有外部输入
2. **SQL注入**: 使用参数化查询防止SQL注入
3. **文件路径**: 验证文件路径防止目录遍历攻击
4. **敏感信息**: 避免在日志中记录敏感信息
5. **权限控制**: 确保操作符有足够的权限执行操作

## 实践练习

### 基础练习
1. 创建文件压缩操作符
2. 实现数据格式转换操作符
3. 开发简单的HTTP请求操作符
4. 编写基本的单元测试

### 高级练习
1. 构建异步数据处理操作符
2. 实现智能传感器操作符
3. 开发多步骤数据处理管道
4. 创建可重用的操作符库

### 综合项目
1. 构建完整的数据ETL操作符套件
2. 实现企业级文件处理系统
3. 开发API集成操作符包
4. 创建操作符测试框架

## 常见问题解答

### Q: 如何选择继承BaseOperator还是BaseSensorOperator？
A: 如果操作符需要轮询等待某个条件满足，继承BaseSensorOperator；如果操作符执行具体的业务逻辑，继承BaseOperator。

### Q: 如何处理操作符中的长时间运行任务？
A: 考虑使用异步处理、分批处理或设置适当的超时时间。对于非常长的任务，可以考虑将其分解为多个子任务。

### Q: 如何在操作符之间共享数据？
A: 使用XCom进行小数据量的共享，对于大数据量使用文件或数据库等外部存储。

### Q: 如何优化操作符的性能？
A: 使用批量处理、并发执行、缓存机制，避免不必要的数据加载，优化算法复杂度。

### Q: 如何处理操作符的版本升级？
A: 使用语义化版本控制，保持向后兼容性，提供迁移指南，在文档中记录变更历史。

## 总结

自定义操作符开发是Airflow高级应用的核心技能。通过掌握基础架构、高级技术和最佳实践，你可以构建强大、可靠和可维护的工作流组件。记住始终遵循设计原则，编写高质量的代码，并进行充分的测试。

成功的自定义操作符应该具备以下特征：
- **功能完整**: 满足业务需求
- **性能优秀**: 高效处理大数据量
- **稳定可靠**: 完善的错误处理
- **易于使用**: 清晰的API和文档
- **可维护**: 良好的代码结构和测试覆盖

继续练习和探索，你将能够开发出更加复杂和强大的自定义操作符，为企业的数据处理工作流提供强有力的支持。