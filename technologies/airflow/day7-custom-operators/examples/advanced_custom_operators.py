"""
高级自定义操作符示例
演示如何创建复杂的自定义操作符，包括传感器、异步操作符、批量处理操作符等
"""

from airflow.models import BaseOperator, BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from airflow.exceptions import AirflowException, AirflowSensorTimeout
from airflow.utils.state import State

import time
import json
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np


class AdvancedSensorOperator(BaseSensorOperator):
    """
    高级传感器操作符 - 支持多种数据源的复杂轮询逻辑
    
    功能：
    - 多数据源轮询（文件、数据库、API）
    - 智能轮询策略（指数退避、自适应间隔）
    - 条件表达式支持
    - 数据预处理
    - 超时和重试机制
    
    参数：
    - data_source_type: 数据源类型 (file, database, api, custom)
    - data_source_config: 数据源配置
    - condition_expression: 条件表达式
    - polling_strategy: 轮询策略 (fixed, exponential_backoff, adaptive)
    - timeout_strategy: 超时策略 (hard, soft)
    - data_preprocessor: 数据预处理函数
    """
    
    template_fields = ('data_source_config', 'condition_expression')
    ui_color = '#FFF2E6'
    
    @apply_defaults
    def __init__(
        self,
        data_source_type: str,
        data_source_config: Dict[str, Any],
        condition_expression: str,
        polling_strategy: str = 'exponential_backoff',
        timeout_strategy: str = 'soft',
        data_preprocessor: Optional[Callable] = None,
        initial_poke_interval: int = 60,
        max_poke_interval: int = 3600,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.data_source_type = data_source_type
        self.data_source_config = data_source_config
        self.condition_expression = condition_expression
        self.polling_strategy = polling_strategy
        self.timeout_strategy = timeout_strategy
        self.data_preprocessor = data_preprocessor
        self.initial_poke_interval = initial_poke_interval
        self.max_poke_interval = max_poke_interval
        
        self.current_poke_interval = initial_poke_interval
        self.consecutive_failures = 0
        self.poke_count = 0
        self.start_time = None
        
        # 验证必需参数
        if not data_source_config or not condition_expression:
            raise AirflowException("data_source_config 和 condition_expression 是必需参数")
    
    def poke(self, context):
        """执行传感器检查"""
        if self.start_time is None:
            self.start_time = datetime.now()
        
        self.poke_count += 1
        self.log.info(f"第 {self.poke_count} 次轮询，间隔: {self.current_poke_interval}秒")
        
        try:
            # 获取数据
            data = self._fetch_data()
            
            # 数据预处理
            if self.data_preprocessor:
                data = self.data_preprocessor(data)
            
            # 评估条件
            condition_result = self._evaluate_condition(data)
            
            if condition_result:
                self.log.info("条件满足，传感器检查通过")
                self._update_polling_interval(success=True)
                return True
            else:
                self.log.info("条件不满足，继续等待")
                self._update_polling_interval(success=False)
                return False
                
        except Exception as e:
            self.consecutive_failures += 1
            self.log.warning(f"轮询失败: {str(e)}")
            
            # 检查超时策略
            if self.timeout_strategy == 'hard':
                if self._is_hard_timeout():
                    raise AirflowSensorTimeout(f"硬超时，连续失败次数: {self.consecutive_failures}")
            
            self._update_polling_interval(success=False)
            return False
    
    def _fetch_data(self):
        """从数据源获取数据"""
        fetch_functions = {
            'file': self._fetch_from_file,
            'database': self._fetch_from_database,
            'api': self._fetch_from_api,
            'custom': self._fetch_from_custom
        }
        
        if self.data_source_type not in fetch_functions:
            raise AirflowException(f"不支持的数据源类型: {self.data_source_type}")
        
        return fetch_functions[self.data_source_type]()
    
    def _fetch_from_file(self):
        """从文件获取数据"""
        file_path = self.data_source_config.get('file_path')
        file_format = self.data_source_config.get('format', 'json')
        
        if not os.path.exists(file_path):
            raise AirflowException(f"文件不存在: {file_path}")
        
        if file_format == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif file_format == 'csv':
            return pd.read_csv(file_path).to_dict('records')
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _fetch_from_database(self):
        """从数据库获取数据"""
        conn_id = self.data_source_config.get('connection_id')
        query = self.data_source_config.get('query')
        
        if not conn_id or not query:
            raise AirflowException("数据库连接需要 connection_id 和 query 参数")
        
        # 使用Airflow连接
        hook = BaseHook.get_hook(conn_id)
        return hook.get_records(query)
    
    def _fetch_from_api(self):
        """从API获取数据"""
        import requests
        
        url = self.data_source_config.get('url')
        method = self.data_source_config.get('method', 'GET')
        headers = self.data_source_config.get('headers', {})
        params = self.data_source_config.get('params', {})
        timeout = self.data_source_config.get('timeout', 30)
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            timeout=timeout
        )
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            return response.json()
        else:
            return response.text
    
    def _fetch_from_custom(self):
        """从自定义数据源获取数据"""
        custom_function = self.data_source_config.get('function')
        custom_params = self.data_source_config.get('params', {})
        
        if custom_function and callable(globals().get(custom_function)):
            return globals()[custom_function](**custom_params)
        else:
            raise AirflowException(f"自定义函数未定义: {custom_function}")
    
    def _evaluate_condition(self, data):
        """评估条件表达式"""
        try:
            # 安全评估表达式
            # 这里使用简化的表达式评估，实际项目中可以使用更安全的表达式引擎
            
            # 替换常用变量
            expression = self.condition_expression
            
            # 支持简单的数据访问
            if 'data' in expression:
                # 创建安全的评估环境
                eval_globals = {"__builtins__": {}}
                eval_locals = {"data": data}
                
                # 评估表达式
                return eval(expression, eval_globals, eval_locals)
            else:
                # 直接评估
                return bool(data)
                
        except Exception as e:
            self.log.error(f"条件评估失败: {str(e)}")
            return False
    
    def _update_polling_interval(self, success):
        """更新轮询间隔"""
        if success:
            # 成功时重置间隔
            self.consecutive_failures = 0
            if self.polling_strategy == 'exponential_backoff':
                self.current_poke_interval = max(
                    self.initial_poke_interval,
                    self.current_poke_interval // 2
                )
            elif self.polling_strategy == 'adaptive':
                self.current_poke_interval = self.initial_poke_interval
        else:
            # 失败时增加间隔
            if self.polling_strategy == 'exponential_backoff':
                self.current_poke_interval = min(
                    self.max_poke_interval,
                    self.current_poke_interval * 2
                )
            elif self.polling_strategy == 'adaptive':
                # 自适应策略：基于连续失败次数调整
                self.current_poke_interval = min(
                    self.max_poke_interval,
                    self.initial_poke_interval * (2 ** self.consecutive_failures)
                )
    
    def _is_hard_timeout(self):
        """检查是否硬超时"""
        if not self.start_time:
            return False
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.timeout and self.consecutive_failures >= 3


class AsyncBatchProcessorOperator(BaseOperator):
    """
    异步批量处理操作符 - 支持并发和异步处理
    
    功能：
    - 异步批量处理
    - 并发控制
    - 进度监控
    - 错误处理
    - 结果聚合
    
    参数：
    - batch_data: 批量数据
    - processing_function: 处理函数
    - batch_size: 批次大小
    - max_concurrency: 最大并发数
    - error_handling: 错误处理策略 (fail_fast, continue_on_error)
    - progress_callback: 进度回调函数
    """
    
    template_fields = ('batch_data', 'processing_function')
    ui_color = '#E6F7FF'
    
    @apply_defaults
    def __init__(
        self,
        batch_data: List[Any],
        processing_function: Union[str, Callable],
        batch_size: int = 100,
        max_concurrency: int = 4,
        error_handling: str = 'continue_on_error',
        progress_callback: Optional[Callable] = None,
        result_aggregator: Optional[Callable] = None,
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
        self.result_aggregator = result_aggregator
        
        self.processed_count = 0
        self.error_count = 0
        self.start_time = None
        
        # 验证参数
        if not batch_data:
            raise AirflowException("batch_data 不能为空")
        if not processing_function:
            raise AirflowException("processing_function 是必需参数")
    
    def execute(self, context):
        """执行批量处理任务"""
        self.start_time = datetime.now()
        self.log.info(f"开始批量处理，数据量: {len(self.batch_data)}, 批次大小: {self.batch_size}, 最大并发: {self.max_concurrency}")
        
        try:
            # 获取处理函数
            process_func = self._get_processing_function()
            
            # 分批处理
            results = self._process_batches(process_func)
            
            # 结果聚合
            final_result = self._aggregate_results(results)
            
            # 记录统计信息
            self._log_processing_statistics()
            
            return final_result
            
        except Exception as e:
            self.log.error(f"批量处理失败: {str(e)}")
            raise AirflowException(f"批量处理失败: {str(e)}")
    
    def _get_processing_function(self):
        """获取处理函数"""
        if callable(self.processing_function):
            return self.processing_function
        elif isinstance(self.processing_function, str):
            # 从全局函数获取
            if self.processing_function in globals():
                return globals()[self.processing_function]
            else:
                raise AirflowException(f"处理函数未定义: {self.processing_function}")
        else:
            raise AirflowException(f"无效的处理函数类型: {type(self.processing_function)}")
    
    def _process_batches(self, process_func):
        """分批处理数据"""
        total_batches = (len(self.batch_data) + self.batch_size - 1) // self.batch_size
        results = []
        
        self.log.info(f"总批次数: {total_batches}")
        
        # 使用线程池进行并发处理
        with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            # 提交所有批次任务
            future_to_batch = {}
            
            for batch_index in range(total_batches):
                start_idx = batch_index * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(self.batch_data))
                batch_data = self.batch_data[start_idx:end_idx]
                
                # 提交批次处理任务
                future = executor.submit(
                    self._process_single_batch,
                    process_func,
                    batch_data,
                    batch_index,
                    total_batches
                )
                future_to_batch[future] = batch_index
            
            # 收集结果
            for future in as_completed(future_to_batch):
                batch_index = future_to_batch[future]
                
                try:
                    batch_result = future.result()
                    results.append(batch_result)
                    
                    # 更新进度
                    self.processed_count += len(batch_data)
                    
                    # 进度回调
                    if self.progress_callback:
                        progress = self.processed_count / len(self.batch_data)
                        self.progress_callback(progress, batch_index, total_batches)
                    
                    self.log.info(f"批次 {batch_index + 1}/{total_batches} 处理完成")
                    
                except Exception as e:
                    self.error_count += 1
                    self.log.error(f"批次 {batch_index} 处理失败: {str(e)}")
                    
                    # 错误处理策略
                    if self.error_handling == 'fail_fast':
                        raise AirflowException(f"批次处理失败，采用快速失败策略: {str(e)}")
                    else:
                        # 记录错误但继续处理
                        results.append({
                            'batch_index': batch_index,
                            'status': 'failed',
                            'error': str(e),
                            'processed_items': 0
                        })
        
        return results
    
    def _process_single_batch(self, process_func, batch_data, batch_index, total_batches):
        """处理单个批次"""
        batch_results = []
        batch_start_time = datetime.now()
        
        try:
            # 处理批次中的每个项目
            for item in batch_data:
                try:
                    result = process_func(item)
                    batch_results.append({
                        'item': item,
                        'result': result,
                        'status': 'success'
                    })
                except Exception as item_error:
                    batch_results.append({
                        'item': item,
                        'error': str(item_error),
                        'status': 'failed'
                    })
            
            batch_end_time = datetime.now()
            processing_time = (batch_end_time - batch_start_time).total_seconds()
            
            return {
                'batch_index': batch_index,
                'status': 'success',
                'processed_items': len(batch_data),
                'successful_items': len([r for r in batch_results if r['status'] == 'success']),
                'failed_items': len([r for r in batch_results if r['status'] == 'failed']),
                'processing_time': processing_time,
                'results': batch_results
            }
            
        except Exception as batch_error:
            batch_end_time = datetime.now()
            processing_time = (batch_end_time - batch_start_time).total_seconds()
            
            return {
                'batch_index': batch_index,
                'status': 'failed',
                'error': str(batch_error),
                'processing_time': processing_time,
                'processed_items': 0
            }
    
    def _aggregate_results(self, batch_results):
        """聚合批次结果"""
        if self.result_aggregator and callable(self.result_aggregator):
            return self.result_aggregator(batch_results)
        
        # 默认聚合逻辑
        total_processed = sum(batch.get('processed_items', 0) for batch in batch_results)
        total_successful = sum(batch.get('successful_items', 0) for batch in batch_results)
        total_failed = sum(batch.get('failed_items', 0) for batch in batch_results)
        
        successful_batches = [batch for batch in batch_results if batch.get('status') == 'success']
        failed_batches = [batch for batch in batch_results if batch.get('status') == 'failed']
        
        total_processing_time = sum(batch.get('processing_time', 0) for batch in batch_results)
        
        return {
            'total_items': len(self.batch_data),
            'processed_items': total_processed,
            'successful_items': total_successful,
            'failed_items': total_failed,
            'success_rate': (total_successful / total_processed * 100) if total_processed > 0 else 0,
            'total_batches': len(batch_results),
            'successful_batches': len(successful_batches),
            'failed_batches': len(failed_batches),
            'total_processing_time': total_processing_time,
            'average_batch_time': total_processing_time / len(batch_results) if batch_results else 0,
            'batch_results': batch_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_processing_statistics(self):
        """记录处理统计信息"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        self.log.info(f"批量处理完成统计:")
        self.log.info(f"- 总处理时间: {total_time:.2f} 秒")
        self.log.info(f"- 处理项目数: {self.processed_count}")
        self.log.info(f"- 错误项目数: {self.error_count}")
        self.log.info(f"- 平均处理速度: {self.processed_count/total_time:.2f} 项目/秒")


class SmartDataProcessorOperator(BaseOperator):
    """
    智能数据处理操作符 - 支持数据转换、清洗、验证和增强
    
    功能：
    - 多步骤数据处理管道
    - 数据质量检查
    - 自动数据类型推断
    - 数据清洗和标准化
    - 数据验证和报告
    
    参数：
    - input_data: 输入数据
    - processing_pipeline: 处理管道配置
    - quality_checks: 数据质量检查配置
    - output_format: 输出格式
    - enable_caching: 是否启用缓存
    """
    
    template_fields = ('input_data', 'processing_pipeline', 'quality_checks')
    ui_color = '#F0FFE6'
    
    @apply_defaults
    def __init__(
        self,
        input_data: Any,
        processing_pipeline: List[Dict[str, Any]],
        quality_checks: Optional[List[Dict[str, Any]]] = None,
        output_format: str = 'json',
        enable_caching: bool = False,
        cache_ttl: int = 3600,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input_data = input_data
        self.processing_pipeline = processing_pipeline
        self.quality_checks = quality_checks or []
        self.output_format = output_format
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        
        self.processing_stats = {
            'input_records': 0,
            'output_records': 0,
            'processing_steps': [],
            'quality_issues': [],
            'processing_time': 0
        }
    
    def execute(self, context):
        """执行智能数据处理任务"""
        start_time = datetime.now()
        self.log.info("开始智能数据处理")
        
        try:
            # 加载输入数据
            data = self._load_input_data()
            self.processing_stats['input_records'] = len(data) if isinstance(data, list) else 1
            
            # 执行处理管道
            processed_data = self._execute_processing_pipeline(data)
            
            # 执行数据质量检查
            quality_report = self._execute_quality_checks(processed_data)
            
            # 格式化输出
            final_output = self._format_output(processed_data)
            
            # 更新统计信息
            self.processing_stats['output_records'] = len(processed_data) if isinstance(processed_data, list) else 1
            self.processing_stats['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # 生成处理报告
            processing_report = {
                'input_stats': {'records': self.processing_stats['input_records']},
                'output_stats': {'records': self.processing_stats['output_records']},
                'processing_steps': self.processing_stats['processing_steps'],
                'quality_report': quality_report,
                'processing_time': self.processing_stats['processing_time'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.log.info("智能数据处理完成")
            self._log_processing_summary()
            
            return {
                'processed_data': final_output,
                'processing_report': processing_report,
                'quality_score': quality_report.get('overall_score', 0)
            }
            
        except Exception as e:
            self.log.error(f"智能数据处理失败: {str(e)}")
            raise AirflowException(f"智能数据处理失败: {str(e)}")
    
    def _load_input_data(self):
        """加载输入数据"""
        if isinstance(self.input_data, str):
            # 文件路径
            if os.path.exists(self.input_data):
                file_format = self.input_data.split('.')[-1].lower()
                if file_format == 'json':
                    with open(self.input_data, 'r', encoding='utf-8') as f:
                        return json.load(f)
                elif file_format == 'csv':
                    return pd.read_csv(self.input_data).to_dict('records')
                else:
                    with open(self.input_data, 'r', encoding='utf-8') as f:
                        return f.read()
            else:
                # 假设是JSON字符串
                return json.loads(self.input_data)
        else:
            return self.input_data
    
    def _execute_processing_pipeline(self, data):
        """执行处理管道"""
        current_data = data
        
        for step_index, step_config in enumerate(self.processing_pipeline):
            step_name = step_config.get('name', f'step_{step_index}')
            step_type = step_config.get('type')
            step_params = step_config.get('params', {})
            
            self.log.info(f"执行处理步骤: {step_name} (类型: {step_type})")
            
            try:
                # 执行处理步骤
                processed_data = self._execute_processing_step(step_type, current_data, step_params)
                
                # 记录步骤统计
                step_stats = {
                    'step_name': step_name,
                    'step_type': step_type,
                    'input_records': len(current_data) if isinstance(current_data, list) else 1,
                    'output_records': len(processed_data) if isinstance(processed_data, list) else 1,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
                
                self.processing_stats['processing_steps'].append(step_stats)
                current_data = processed_data
                
                self.log.info(f"处理步骤 {step_name} 完成")
                
            except Exception as step_error:
                step_stats = {
                    'step_name': step_name,
                    'step_type': step_type,
                    'status': 'failed',
                    'error': str(step_error),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.processing_stats['processing_steps'].append(step_stats)
                self.log.error(f"处理步骤 {step_name} 失败: {str(step_error)}")
                raise
        
        return current_data
    
    def _execute_processing_step(self, step_type, data, params):
        """执行单个处理步骤"""
        processing_functions = {
            'filter': self._step_filter,
            'transform': self._step_transform,
            'clean': self._step_clean,
            'validate': self._step_validate,
            'enrich': self._step_enrich,
            'aggregate': self._step_aggregate,
            'normalize': self._step_normalize,
            'deduplicate': self._step_deduplicate
        }
        
        if step_type not in processing_functions:
            raise AirflowException(f"不支持的处理步骤类型: {step_type}")
        
        return processing_functions[step_type](data, params)
    
    def _step_filter(self, data, params):
        """数据过滤步骤"""
        condition = params.get('condition')
        
        if isinstance(data, list):
            return [item for item in data if self._evaluate_condition_on_item(item, condition)]
        else:
            return data if self._evaluate_condition_on_item(data, condition) else None
    
    def _step_transform(self, data, params):
        """数据转换步骤"""
        transformations = params.get('transformations', {})
        
        if isinstance(data, list):
            return [self._apply_transformations(item, transformations) for item in data]
        else:
            return self._apply_transformations(data, transformations)
    
    def _step_clean(self, data, params):
        """数据清洗步骤"""
        cleaning_rules = params.get('rules', [])
        
        if isinstance(data, list):
            return [self._apply_cleaning_rules(item, cleaning_rules) for item in data]
        else:
            return self._apply_cleaning_rules(data, cleaning_rules)
    
    def _step_validate(self, data, params):
        """数据验证步骤"""
        validation_rules = params.get('rules', [])
        
        if isinstance(data, list):
            validated_data = []
            for item in data:
                if self._validate_item(item, validation_rules):
                    validated_data.append(item)
            return validated_data
        else:
            return data if self._validate_item(data, validation_rules) else None
    
    def _step_enrich(self, data, params):
        """数据增强步骤"""
        enrichment_sources = params.get('sources', [])
        
        if isinstance(data, list):
            return [self._enrich_item(item, enrichment_sources) for item in data]
        else:
            return self._enrich_item(data, enrichment_sources)
    
    def _step_aggregate(self, data, params):
        """数据聚合步骤"""
        aggregation_functions = params.get('functions', {})
        group_by = params.get('group_by')
        
        if isinstance(data, list) and group_by:
            # 按字段分组聚合
            from collections import defaultdict
            groups = defaultdict(list)
            
            for item in data:
                key = item.get(group_by)
                groups[key].append(item)
            
            aggregated_data = []
            for key, group_items in groups.items():
                aggregated_item = {'group_key': key, 'count': len(group_items)}
                
                for func_name, func_config in aggregation_functions.items():
                    field = func_config.get('field')
                    func_type = func_config.get('type', 'sum')
                    
                    if field:
                        values = [item.get(field) for item in group_items if field in item]
                        
                        if func_type == 'sum':
                            aggregated_item[func_name] = sum(values)
                        elif func_type == 'avg':
                            aggregated_item[func_name] = sum(values) / len(values) if values else 0
                        elif func_type == 'count':
                            aggregated_item[func_name] = len(values)
                        elif func_type == 'max':
                            aggregated_item[func_name] = max(values) if values else None
                        elif func_type == 'min':
                            aggregated_item[func_name] = min(values) if values else None
                
                aggregated_data.append(aggregated_item)
            
            return aggregated_data
        
        return data
    
    def _step_normalize(self, data, params):
        """数据标准化步骤"""
        normalization_rules = params.get('rules', {})
        
        if isinstance(data, list):
            return [self._normalize_item(item, normalization_rules) for item in data]
        else:
            return self._normalize_item(data, normalization_rules)
    
    def _step_deduplicate(self, data, params):
        """数据去重步骤"""
        dedup_keys = params.get('keys', [])
        
        if isinstance(data, list) and dedup_keys:
            seen = set()
            deduplicated_data = []
            
            for item in data:
                # 创建去重键
                dedup_key = tuple(item.get(key) for key in dedup_keys if key in item)
                
                if dedup_key not in seen:
                    seen.add(dedup_key)
                    deduplicated_data.append(item)
            
            return deduplicated_data
        
        return data
    
    def _execute_quality_checks(self, data):
        """执行数据质量检查"""
        quality_report = {
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'warnings': 0,
            'quality_score': 0,
            'issues': []
        }
        
        for check_config in self.quality_checks:
            quality_report['total_checks'] += 1
            
            try:
                check_result = self._execute_single_quality_check(data, check_config)
                
                if check_result['status'] == 'passed':
                    quality_report['passed_checks'] += 1
                elif check_result['status'] == 'warning':
                    quality_report['warnings'] += 1
                    quality_report['issues'].append(check_result)
                else:  # failed
                    quality_report['failed_checks'] += 1
                    quality_report['issues'].append(check_result)
                    
            except Exception as check_error:
                quality_report['failed_checks'] += 1
                quality_report['issues'].append({
                    'check_name': check_config.get('name', 'unknown'),
                    'status': 'error',
                    'error': str(check_error)
                })
        
        # 计算质量分数
        if quality_report['total_checks'] > 0:
            quality_report['quality_score'] = (
                quality_report['passed_checks'] / quality_report['total_checks'] * 100
            )
        
        return quality_report
    
    def _execute_single_quality_check(self, data, check_config):
        """执行单个质量检查"""
        check_type = check_config.get('type')
        check_params = check_config.get('params', {})
        
        quality_functions = {
            'completeness': self._check_completeness,
            'accuracy': self._check_accuracy,
            'consistency': self._check_consistency,
            'validity': self._check_validity,
            'uniqueness': self._check_uniqueness,
            'timeliness': self._check_timeliness
        }
        
        if check_type not in quality_functions:
            return {'status': 'warning', 'message': f"未知的质量检查类型: {check_type}"}
        
        return quality_functions[check_type](data, check_params)
    
    def _format_output(self, data):
        """格式化输出"""
        if self.output_format == 'json':
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif self.output_format == 'csv':
            if isinstance(data, list):
                import io
                import csv
                
                output = io.StringIO()
                if data:
                    writer = csv.DictWriter(output, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                
                return output.getvalue()
            else:
                return str(data)
        else:
            return str(data)
    
    def _log_processing_summary(self):
        """记录处理摘要"""
        self.log.info("数据处理摘要:")
        self.log.info(f"- 输入记录数: {self.processing_stats['input_records']}")
        self.log.info(f"- 输出记录数: {self.processing_stats['output_records']}")
        self.log.info(f"- 处理步骤数: {len(self.processing_stats['processing_steps'])}")
        self.log.info(f"- 处理时间: {self.processing_stats['processing_time']:.2f}秒")
        
        if self.processing_stats['processing_steps']:
            self.log.info("处理步骤状态:")
            for step in self.processing_stats['processing_steps']:
                self.log.info(f"  - {step['step_name']}: {step['status']}")


# 示例处理函数
def sample_batch_processor(item):
    """示例批量处理函数"""
    # 模拟处理逻辑
    time.sleep(0.1)  # 模拟处理时间
    
    if isinstance(item, dict):
        # 添加处理标记
        item['processed'] = True
        item['processed_at'] = datetime.now().isoformat()
        return item
    else:
        return f"processed_{item}"


def sample_data_preprocessor(data):
    """示例数据预处理函数"""
    if isinstance(data, dict) and 'items' in data:
        return data['items']
    return data


def sample_progress_callback(progress, batch_index, total_batches):
    """示例进度回调函数"""
    print(f"处理进度: {progress:.1%} (批次 {batch_index + 1}/{total_batches})")


def sample_result_aggregator(batch_results):
    """示例结果聚合函数"""
    all_results = []
    for batch in batch_results:
        if batch.get('status') == 'success' and 'results' in batch:
            for item_result in batch['results']:
                if item_result.get('status') == 'success':
                    all_results.append(item_result.get('result'))
    
    return {
        'total_processed': len(all_results),
        'results': all_results,
        'aggregation_timestamp': datetime.now().isoformat()
    }


# 测试函数
def test_advanced_custom_operators():
    """测试高级自定义操作符"""
    from airflow import DAG
    from datetime import datetime, timedelta
    
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
    
    dag = DAG(
        'test_advanced_custom_operators',
        default_args=default_args,
        description='测试高级自定义操作符',
        schedule_interval=None,
        catchup=False,
    )
    
    # 1. 高级传感器操作符
    sensor_task = AdvancedSensorOperator(
        task_id='wait_for_data_file',
        data_source_type='file',
        data_source_config={
            'file_path': '/tmp/test_data.json',
            'format': 'json'
        },
        condition_expression="len(data.get('items', [])) >= 10",
        polling_strategy='exponential_backoff',
        initial_poke_interval=30,
        max_poke_interval=300,
        timeout=600,
        dag=dag
    )
    
    # 2. 异步批量处理操作符
    batch_data = [
        {'id': i, 'value': f'item_{i}', 'category': f'category_{i % 3}'}
        for i in range(100)
    ]
    
    batch_processor_task = AsyncBatchProcessorOperator(
        task_id='process_data_batch',
        batch_data=batch_data,
        processing_function=sample_batch_processor,
        batch_size=20,
        max_concurrency=4,
        error_handling='continue_on_error',
        progress_callback=sample_progress_callback,
        result_aggregator=sample_result_aggregator,
        dag=dag
    )
    
    # 3. 智能数据处理操作符
    processing_pipeline = [
        {
            'name': 'filter_valid_items',
            'type': 'filter',
            'params': {
                'condition': "item.get('value') is not None"
            }
        },
        {
            'name': 'transform_categories',
            'type': 'transform',
            'params': {
                'transformations': {
                    'category_upper': "item['category'].upper()"
                }
            }
        },
        {
            'name': 'add_timestamp',
            'type': 'enrich',
            'params': {
                'sources': [
                    {'type': 'timestamp', 'field': 'processed_timestamp'}
                ]
            }
        }
    ]
    
    quality_checks = [
        {
            'name': 'completeness_check',
            'type': 'completeness',
            'params': {
                'required_fields': ['id', 'value', 'category']
            }
        },
        {
            'name': 'validity_check',
            'type': 'validity',
            'params': {
                'rules': [
                    {'field': 'id', 'type': 'integer'},
                    {'field': 'value', 'type': 'string'}
                ]
            }
        }
    ]
    
    smart_processor_task = SmartDataProcessorOperator(
        task_id='process_data_intelligently',
        input_data=batch_data,
        processing_pipeline=processing_pipeline,
        quality_checks=quality_checks,
        output_format='json',
        enable_caching=True,
        cache_ttl=1800,
        dag=dag
    )
    
    # 设置任务依赖
    sensor_task >> batch_processor_task >> smart_processor_task
    
    return dag


if __name__ == "__main__":
    # 测试高级操作符
    print("测试高级自定义操作符...")
    
    # 创建测试DAG
    test_dag = test_advanced_custom_operators()
    
    print("测试DAG已创建，包含以下任务：")
    for task in test_dag.tasks:
        print(f"- {task.task_id}: {task.__class__.__name__}")
    
    print("\n高级操作符测试完成！")