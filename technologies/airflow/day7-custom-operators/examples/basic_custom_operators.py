"""
基础自定义操作符示例
演示如何创建简单的自定义操作符，包括文件处理、数据验证和通知发送
"""

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from airflow.exceptions import AirflowException

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List


class FileProcessorOperator(BaseOperator):
    """
    文件处理操作符 - 基础自定义操作符示例
    
    功能：
    - 读取文件内容
    - 执行数据处理
    - 保存处理结果
    - 记录处理统计信息
    
    参数：
    - input_path: 输入文件路径
    - output_path: 输出文件路径
    - processing_function: 处理函数名称
    - encoding: 文件编码（默认utf-8）
    - backup_original: 是否备份原文件
    """
    
    template_fields = ('input_path', 'output_path')
    ui_color = '#FFE6E6'
    
    @apply_defaults
    def __init__(
        self,
        input_path: str,
        output_path: str,
        processing_function: str = 'process_default',
        encoding: str = 'utf-8',
        backup_original: bool = False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input_path = input_path
        self.output_path = output_path
        self.processing_function = processing_function
        self.encoding = encoding
        self.backup_original = backup_original
        
        # 验证必需参数
        if not input_path or not output_path:
            raise AirflowException("input_path 和 output_path 是必需参数")
    
    def execute(self, context):
        """执行文件处理任务"""
        self.log.info(f"开始处理文件: {self.input_path}")
        
        try:
            # 检查输入文件是否存在
            if not os.path.exists(self.input_path):
                raise AirflowException(f"输入文件不存在: {self.input_path}")
            
            # 备份原文件（如果启用）
            if self.backup_original:
                self._backup_file()
            
            # 读取文件内容
            content = self._read_file()
            
            # 处理数据
            processed_content = self._process_content(content)
            
            # 保存处理结果
            self._write_file(processed_content)
            
            # 记录统计信息
            self._log_statistics(content, processed_content)
            
            self.log.info(f"文件处理完成: {self.output_path}")
            
            # 返回处理统计
            return {
                'input_file': self.input_path,
                'output_file': self.output_path,
                'input_size': len(content),
                'output_size': len(processed_content),
                'processing_function': self.processing_function,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log.error(f"文件处理失败: {str(e)}")
            raise AirflowException(f"文件处理失败: {str(e)}")
    
    def _backup_file(self):
        """备份原文件"""
        backup_path = f"{self.input_path}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        import shutil
        shutil.copy2(self.input_path, backup_path)
        self.log.info(f"文件已备份到: {backup_path}")
    
    def _read_file(self):
        """读取文件内容"""
        with open(self.input_path, 'r', encoding=self.encoding) as f:
            return f.read()
    
    def _process_content(self, content):
        """处理文件内容"""
        # 根据指定的处理函数处理内容
        processing_functions = {
            'process_default': self._process_default,
            'process_json': self._process_json,
            'process_csv': self._process_csv,
            'process_uppercase': self._process_uppercase,
            'process_lowercase': self._process_lowercase,
            'process_strip_whitespace': self._process_strip_whitespace
        }
        
        if self.processing_function not in processing_functions:
            raise AirflowException(f"未知的处理函数: {self.processing_function}")
        
        return processing_functions[self.processing_function](content)
    
    def _write_file(self, content):
        """写入处理后的内容"""
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding=self.encoding) as f:
            f.write(content)
    
    def _log_statistics(self, original_content, processed_content):
        """记录处理统计信息"""
        original_size = len(original_content)
        processed_size = len(processed_content)
        compression_ratio = (original_size - processed_size) / original_size * 100 if original_size > 0 else 0
        
        self.log.info(f"处理统计 - 原始大小: {original_size}, 处理后大小: {processed_size}, 压缩率: {compression_ratio:.2f}%")
    
    # 处理函数定义
    def _process_default(self, content):
        """默认处理函数 - 不做任何处理"""
        return content
    
    def _process_json(self, content):
        """JSON处理函数 - 格式化JSON"""
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            self.log.warning("内容不是有效的JSON，返回原内容")
            return content
    
    def _process_csv(self, content):
        """CSV处理函数 - 标准化CSV格式"""
        import csv
        import io
        
        # 读取CSV内容
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        # 标准化处理
        output = io.StringIO()
        writer = csv.writer(output)
        
        for row in rows:
            # 去除空行和空值
            cleaned_row = [cell.strip() for cell in row if cell.strip()]
            if cleaned_row:
                writer.writerow(cleaned_row)
        
        return output.getvalue()
    
    def _process_uppercase(self, content):
        """转换为大写"""
        return content.upper()
    
    def _process_lowercase(self, content):
        """转换为小写"""
        return content.lower()
    
    def _process_strip_whitespace(self, content):
        """去除多余空白字符"""
        import re
        # 去除行尾空格，压缩连续空行
        lines = content.split('\n')
        cleaned_lines = []
        empty_line_count = 0
        
        for line in lines:
            line = line.rstrip()
            if line:
                cleaned_lines.append(line)
                empty_line_count = 0
            else:
                empty_line_count += 1
                if empty_line_count <= 1:  # 最多保留一个空行
                    cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)


class DataValidatorOperator(BaseOperator):
    """
    数据验证操作符 - 验证数据质量和完整性
    
    功能：
    - 验证数据格式
    - 检查数据完整性
    - 验证业务规则
    - 生成验证报告
    
    参数：
    - data_source: 数据源路径或连接信息
    - validation_rules: 验证规则配置
    - fail_on_validation_error: 验证失败时是否失败任务
    - generate_report: 是否生成验证报告
    """
    
    template_fields = ('data_source',)
    ui_color = '#E6F3FF'
    
    @apply_defaults
    def __init__(
        self,
        data_source: str,
        validation_rules: Dict[str, Any],
        fail_on_validation_error: bool = True,
        generate_report: bool = True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.data_source = data_source
        self.validation_rules = validation_rules
        self.fail_on_validation_error = fail_on_validation_error
        self.generate_report = generate_report
    
    def execute(self, context):
        """执行数据验证任务"""
        self.log.info(f"开始验证数据源: {self.data_source}")
        
        validation_results = {
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'warnings': 0,
            'errors': [],
            'warnings_list': [],
            'validation_timestamp': datetime.now().isoformat()
        }
        
        try:
            # 加载数据
            data = self._load_data()
            
            # 执行验证规则
            for rule_name, rule_config in self.validation_rules.items():
                self.log.info(f"执行验证规则: {rule_name}")
                
                validation_results['total_checks'] += 1
                
                try:
                    result = self._execute_validation_rule(rule_name, rule_config, data)
                    
                    if result['status'] == 'passed':
                        validation_results['passed_checks'] += 1
                    elif result['status'] == 'warning':
                        validation_results['warnings'] += 1
                        validation_results['warnings_list'].append(result['message'])
                    else:  # failed
                        validation_results['failed_checks'] += 1
                        validation_results['errors'].append(result['message'])
                        
                        if self.fail_on_validation_error:
                            raise AirflowException(f"验证规则失败: {rule_name} - {result['message']}")
                
                except Exception as e:
                    validation_results['failed_checks'] += 1
                    validation_results['errors'].append(f"规则 {rule_name} 执行失败: {str(e)}")
                    
                    if self.fail_on_validation_error:
                        raise
            
            # 生成验证报告
            if self.generate_report:
                self._generate_validation_report(validation_results)
            
            # 记录验证结果
            self._log_validation_summary(validation_results)
            
            return validation_results
            
        except Exception as e:
            self.log.error(f"数据验证失败: {str(e)}")
            raise AirflowException(f"数据验证失败: {str(e)}")
    
    def _load_data(self):
        """加载数据"""
        if self.data_source.endswith('.json'):
            with open(self.data_source, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif self.data_source.endswith('.csv'):
            import csv
            with open(self.data_source, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        else:
            # 假设是文本文件
            with open(self.data_source, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _execute_validation_rule(self, rule_name, rule_config, data):
        """执行单个验证规则"""
        rule_type = rule_config.get('type', 'data_type')
        
        validation_functions = {
            'data_type': self._validate_data_type,
            'range': self._validate_range,
            'format': self._validate_format,
            'completeness': self._validate_completeness,
            'uniqueness': self._validate_uniqueness,
            'business_rule': self._validate_business_rule
        }
        
        if rule_type not in validation_functions:
            return {
                'status': 'warning',
                'message': f"未知的验证规则类型: {rule_type}"
            }
        
        return validation_functions[rule_type](rule_name, rule_config, data)
    
    def _validate_data_type(self, rule_name, rule_config, data):
        """验证数据类型"""
        expected_type = rule_config.get('expected_type')
        field = rule_config.get('field')
        
        if field and isinstance(data, dict):
            value = data.get(field)
        elif isinstance(data, list) and len(data) > 0:
            value = data[0].get(field) if isinstance(data[0], dict) else data[0]
        else:
            value = data
        
        actual_type = type(value).__name__
        
        if actual_type == expected_type:
            return {'status': 'passed', 'message': f"数据类型验证通过: {expected_type}"}
        else:
            return {'status': 'failed', 'message': f"数据类型不匹配: 期望 {expected_type}, 实际 {actual_type}"}
    
    def _validate_range(self, rule_name, rule_config, data):
        """验证数据范围"""
        min_value = rule_config.get('min')
        max_value = rule_config.get('max')
        field = rule_config.get('field')
        
        if field and isinstance(data, (list, dict)):
            values = [item.get(field) for item in data] if isinstance(data, list) else [data.get(field)]
        else:
            values = [data] if not isinstance(data, list) else data
        
        for value in values:
            if min_value is not None and value < min_value:
                return {'status': 'failed', 'message': f"值 {value} 小于最小值 {min_value}"}
            if max_value is not None and value > max_value:
                return {'status': 'failed', 'message': f"值 {value} 大于最大值 {max_value}"}
        
        return {'status': 'passed', 'message': "范围验证通过"}
    
    def _validate_format(self, rule_name, rule_config, data):
        """验证数据格式"""
        pattern = rule_config.get('pattern')
        field = rule_config.get('field')
        
        import re
        
        if field and isinstance(data, (list, dict)):
            values = [item.get(field) for item in data] if isinstance(data, list) else [data.get(field)]
        else:
            values = [data] if not isinstance(data, list) else data
        
        for value in values:
            if not re.match(pattern, str(value)):
                return {'status': 'failed', 'message': f"格式验证失败: {value} 不匹配模式 {pattern}"}
        
        return {'status': 'passed', 'message': "格式验证通过"}
    
    def _validate_completeness(self, rule_name, rule_config, data):
        """验证数据完整性"""
        required_fields = rule_config.get('required_fields', [])
        
        if isinstance(data, dict):
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return {'status': 'failed', 'message': f"缺少必需字段: {missing_fields}"}
        elif isinstance(data, list):
            for item in data:
                missing_fields = [field for field in required_fields if field not in item or not item[field]]
                if missing_fields:
                    return {'status': 'failed', 'message': f"数据项缺少必需字段: {missing_fields}"}
        
        return {'status': 'passed', 'message': "完整性验证通过"}
    
    def _validate_uniqueness(self, rule_name, rule_config, data):
        """验证数据唯一性"""
        field = rule_config.get('field')
        
        if isinstance(data, list) and field:
            values = [item.get(field) for item in data if field in item]
            unique_values = set(values)
            
            if len(values) != len(unique_values):
                duplicates = [value for value in unique_values if values.count(value) > 1]
                return {'status': 'failed', 'message': f"存在重复值: {duplicates}"}
        
        return {'status': 'passed', 'message': "唯一性验证通过"}
    
    def _validate_business_rule(self, rule_name, rule_config, data):
        """验证业务规则"""
        rule_function = rule_config.get('function')
        rule_params = rule_config.get('params', {})
        
        if rule_function and callable(globals().get(rule_function)):
            result = globals()[rule_function](data, **rule_params)
            return result
        else:
            return {'status': 'warning', 'message': f"业务规则函数未定义: {rule_function}"}
    
    def _generate_validation_report(self, results):
        """生成验证报告"""
        report_content = f"""
数据验证报告
============

验证时间: {results['validation_timestamp']}
数据源: {self.data_source}

验证结果统计:
- 总检查数: {results['total_checks']}
- 通过: {results['passed_checks']}
- 失败: {results['failed_checks']}
- 警告: {results['warnings']}

错误详情:
{chr(10).join(results['errors'])}

警告详情:
{chr(10).join(results['warnings_list'])}
"""
        
        report_path = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.log.info(f"验证报告已生成: {report_path}")
    
    def _log_validation_summary(self, results):
        """记录验证摘要"""
        success_rate = (results['passed_checks'] / results['total_checks'] * 100) if results['total_checks'] > 0 else 0
        
        self.log.info(f"验证完成 - 成功率: {success_rate:.1f}%")
        self.log.info(f"通过: {results['passed_checks']}, 失败: {results['failed_checks']}, 警告: {results['warnings']}")


class NotificationOperator(BaseOperator):
    """
    通知操作符 - 发送各种类型通知
    
    功能：
    - 发送邮件通知
    - 发送Slack消息
    - 发送Webhook通知
    - 支持模板化消息
    
    参数：
    - notification_type: 通知类型 (email, slack, webhook)
    - recipients: 接收者列表
    - message: 消息内容
    - subject: 主题（邮件用）
    - template_context: 模板上下文
    """
    
    template_fields = ('message', 'subject', 'template_context')
    ui_color = '#E6FFE6'
    
    @apply_defaults
    def __init__(
        self,
        notification_type: str,
        recipients: List[str],
        message: str,
        subject: str = None,
        template_context: Dict[str, Any] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.notification_type = notification_type.lower()
        self.recipients = recipients
        self.message = message
        self.subject = subject or "Airflow通知"
        self.template_context = template_context or {}
    
    def execute(self, context):
        """执行通知发送任务"""
        self.log.info(f"发送{self.notification_type}通知给: {self.recipients}")
        
        # 渲染消息模板
        rendered_message = self._render_template(self.message, context)
        rendered_subject = self._render_template(self.subject, context) if self.subject else self.subject
        
        try:
            if self.notification_type == 'email':
                self._send_email_notification(rendered_message, rendered_subject)
            elif self.notification_type == 'slack':
                self._send_slack_notification(rendered_message)
            elif self.notification_type == 'webhook':
                self._send_webhook_notification(rendered_message)
            else:
                raise AirflowException(f"不支持的通知类型: {self.notification_type}")
            
            self.log.info("通知发送成功")
            
            return {
                'notification_type': self.notification_type,
                'recipients': self.recipients,
                'subject': rendered_subject,
                'message_length': len(rendered_message),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log.error(f"通知发送失败: {str(e)}")
            raise AirflowException(f"通知发送失败: {str(e)}")
    
    def _render_template(self, template, context):
        """渲染消息模板"""
        from jinja2 import Template
        
        try:
            # 合并上下文
            template_vars = {**context, **self.template_context}
            
            # 渲染模板
            jinja_template = Template(template)
            return jinja_template.render(**template_vars)
            
        except Exception as e:
            self.log.warning(f"模板渲染失败，使用原始消息: {str(e)}")
            return template
    
    def _send_email_notification(self, message, subject):
        """发送邮件通知"""
        from airflow.operators.email_operator import EmailOperator
        
        # 创建邮件操作符
        email_op = EmailOperator(
            task_id=f"email_notification_{self.task_id}",
            to=self.recipients,
            subject=subject,
            html_content=message,
            dag=None  # 临时操作符，不关联DAG
        )
        
        # 执行邮件发送
        email_op.execute(self.context)
    
    def _send_slack_notification(self, message):
        """发送Slack通知"""
        from airflow.providers.slack.operators.slack import SlackAPIPostOperator
        
        # 创建Slack操作符
        slack_op = SlackAPIPostOperator(
            task_id=f"slack_notification_{self.task_id}",
            channel=self.recipients[0] if self.recipients else "#general",
            text=message,
            dag=None
        )
        
        # 执行Slack发送
        slack_op.execute(self.context)
    
    def _send_webhook_notification(self, message):
        """发送Webhook通知"""
        import requests
        
        webhook_url = self.recipients[0] if self.recipients else None
        if not webhook_url:
            raise AirflowException("Webhook URL未提供")
        
        # 构建请求数据
        payload = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'dag_id': self.dag_id,
            'task_id': self.task_id
        }
        
        # 发送POST请求
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()
        
        self.log.info(f"Webhook通知发送成功，状态码: {response.status_code}")


# 示例使用函数
def example_business_rule(data, **params):
    """示例业务规则验证函数"""
    min_value = params.get('min_value', 0)
    max_value = params.get('max_value', 100)
    
    if isinstance(data, (int, float)):
        if min_value <= data <= max_value:
            return {'status': 'passed', 'message': f"值 {data} 在有效范围内 [{min_value}, {max_value}]"}
        else:
            return {'status': 'failed', 'message': f"值 {data} 超出有效范围 [{min_value}, {max_value}]"}
    
    return {'status': 'warning', 'message': "无法验证数据类型"}


# 测试函数
def test_basic_custom_operators():
    """测试基础自定义操作符"""
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
        'test_basic_custom_operators',
        default_args=default_args,
        description='测试基础自定义操作符',
        schedule_interval=None,
        catchup=False,
    )
    
    # 创建测试文件
    test_data = {
        'users': [
            {'id': 1, 'name': 'Alice', 'age': 25, 'email': 'alice@example.com'},
            {'id': 2, 'name': 'Bob', 'age': 30, 'email': 'bob@example.com'},
            {'id': 3, 'name': 'Charlie', 'age': 35, 'email': 'charlie@example.com'}
        ]
    }
    
    # 写入测试文件
    test_file_path = '/tmp/test_data.json'
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    # 1. 文件处理操作符 - JSON格式化
    format_json_task = FileProcessorOperator(
        task_id='format_json_file',
        input_path=test_file_path,
        output_path='/tmp/formatted_data.json',
        processing_function='process_json',
        backup_original=True,
        dag=dag
    )
    
    # 2. 数据验证操作符
    validation_rules = {
        'data_completeness': {
            'type': 'completeness',
            'required_fields': ['id', 'name', 'age', 'email']
        },
        'age_range': {
            'type': 'range',
            'field': 'age',
            'min': 18,
            'max': 100
        },
        'email_format': {
            'type': 'format',
            'field': 'email',
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }
    }
    
    validate_data_task = DataValidatorOperator(
        task_id='validate_data',
        data_source='/tmp/formatted_data.json',
        validation_rules=validation_rules,
        fail_on_validation_error=True,
        generate_report=True,
        dag=dag
    )
    
    # 3. 通知操作符
    notify_completion_task = NotificationOperator(
        task_id='notify_completion',
        notification_type='email',
        recipients=['admin@example.com'],
        subject='数据处理完成通知',
        message='数据处理任务已成功完成！\n\n处理详情：{{ task_instance.xcom_pull(task_ids="format_json_file") }}',
        template_context={'completion_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        dag=dag
    )
    
    # 设置任务依赖
    format_json_task >> validate_data_task >> notify_completion_task
    
    return dag


if __name__ == "__main__":
    # 测试操作符
    print("测试基础自定义操作符...")
    
    # 创建测试DAG
    test_dag = test_basic_custom_operators()
    
    print("测试DAG已创建，包含以下任务：")
    for task in test_dag.tasks:
        print(f"- {task.task_id}: {task.__class__.__name__}")
    
    print("\n操作符测试完成！")