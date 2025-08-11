#!/usr/bin/env python3
"""
数据质量模板引擎
负责SQL模板的渲染和管理，支持多数据库和多场景
"""

import os
import re
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from string import Template


class TemplateEngine:
    """数据质量模板引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化模板引擎
        
        Args:
            config: 全局配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.template_cache = {}
        self.database_dialects = self._load_database_dialects()
        
    def _load_database_dialects(self) -> Dict[str, Dict]:
        """
        加载数据库方言配置
        
        Returns:
            Dict: 数据库类型到方言配置的映射
        """
        dialects = {
            'clickhouse': {
                'quote_char': '`',
                'string_quote': "'",
                'null_check': 'IS NULL',
                'not_null_check': 'IS NOT NULL',
                'regexp_operator': 'REGEXP',
                'date_functions': {
                    'today': 'today()',
                    'now': 'now()',
                    'date_add': 'addDays({date}, {days})',
                    'date_diff': 'dateDiff(\'day\', {start}, {end})'
                },
                'aggregate_functions': {
                    'count': 'COUNT',
                    'sum': 'SUM',
                    'avg': 'AVG',
                    'min': 'MIN',
                    'max': 'MAX',
                    'stddev': 'stddevPop'
                },
                'case_sensitive': False
            },
            'mysql': {
                'quote_char': '`',
                'string_quote': "'",
                'null_check': 'IS NULL',
                'not_null_check': 'IS NOT NULL',
                'regexp_operator': 'REGEXP',
                'date_functions': {
                    'today': 'CURDATE()',
                    'now': 'NOW()',
                    'date_add': 'DATE_ADD({date}, INTERVAL {days} DAY)',
                    'date_diff': 'DATEDIFF({end}, {start})'
                },
                'aggregate_functions': {
                    'count': 'COUNT',
                    'sum': 'SUM',
                    'avg': 'AVG',
                    'min': 'MIN',
                    'max': 'MAX',
                    'stddev': 'STDDEV'
                },
                'case_sensitive': True
            },
            'postgresql': {
                'quote_char': '"',
                'string_quote': "'",
                'null_check': 'IS NULL',
                'not_null_check': 'IS NOT NULL',
                'regexp_operator': '~',
                'date_functions': {
                    'today': 'CURRENT_DATE',
                    'now': 'NOW()',
                    'date_add': '{date} + INTERVAL \'{days} days\'',
                    'date_diff': 'EXTRACT(DAY FROM {end} - {start})'
                },
                'aggregate_functions': {
                    'count': 'COUNT',
                    'sum': 'SUM',
                    'avg': 'AVG',
                    'min': 'MIN',
                    'max': 'MAX',
                    'stddev': 'STDDEV'
                },
                'case_sensitive': True
            },
            'sqlserver': {
                'quote_char': '[',
                'close_quote_char': ']',
                'string_quote': "'",
                'null_check': 'IS NULL',
                'not_null_check': 'IS NOT NULL',
                'regexp_operator': 'LIKE',  # SQL Server doesn't have native regex
                'date_functions': {
                    'today': 'CAST(GETDATE() AS DATE)',
                    'now': 'GETDATE()',
                    'date_add': 'DATEADD(day, {days}, {date})',
                    'date_diff': 'DATEDIFF(day, {start}, {end})'
                },
                'aggregate_functions': {
                    'count': 'COUNT',
                    'sum': 'SUM',
                    'avg': 'AVG',
                    'min': 'MIN',
                    'max': 'MAX',
                    'stddev': 'STDEV'
                },
                'case_sensitive': False
            }
        }
        return dialects
    
    def render_rule_template(self, rule: Dict[str, Any], database_type: str = 'clickhouse') -> str:
        """
        渲染规则的SQL模板
        
        Args:
            rule: 规则配置
            database_type: 数据库类型
            
        Returns:
            str: 渲染后的SQL查询
        """
        try:
            # 获取模板内容
            template_content = self._get_template_content(rule)
            if not template_content:
                self.logger.error(f"无法获取规则模板: {rule.get('rule', {}).get('name')}")
                return ""
            
            # 获取模板变量
            variables = self._extract_template_variables(rule, database_type)
            
            # 适配数据库方言
            template_content = self._adapt_database_dialect(template_content, database_type)
            
            # 渲染模板
            rendered_sql = self._render_template(template_content, variables)
            
            # 清理和格式化SQL
            rendered_sql = self._clean_sql(rendered_sql)
            
            self.logger.debug(f"成功渲染规则模板: {rule.get('rule', {}).get('name')}")
            return rendered_sql
            
        except Exception as e:
            self.logger.error(f"渲染规则模板失败: {e}")
            return ""
    
    def _get_template_content(self, rule: Dict[str, Any]) -> str:
        """
        获取模板内容
        
        Args:
            rule: 规则配置
            
        Returns:
            str: 模板内容
        """
        rule_config = rule.get('rule', {})
        
        # 优先使用规则中的template字段
        if rule_config.get('template'):
            return rule_config['template']
        
        # 其次使用顶级的sql_template字段
        if rule.get('sql_template'):
            return rule['sql_template']
        
        # 最后尝试从模板文件加载
        rule_type = rule.get('rule_type', '')
        if rule_type:
            template_file = f"templates/{rule_type}-template.yml"
            return self._load_template_from_file(template_file)
        
        return ""
    
    def _load_template_from_file(self, template_file: str) -> str:
        """
        从文件加载模板
        
        Args:
            template_file: 模板文件路径
            
        Returns:
            str: 模板内容
        """
        try:
            # 检查缓存
            if template_file in self.template_cache:
                return self.template_cache[template_file]
            
            # 查找模板文件
            base_dir = self.config.get('templates', {}).get('base_dir', 'templates')
            full_path = os.path.join(base_dir, template_file)
            
            if not os.path.exists(full_path):
                # 尝试相对于当前目录
                full_path = template_file
            
            if not os.path.exists(full_path):
                self.logger.warning(f"模板文件不存在: {template_file}")
                return ""
            
            # 加载模板
            with open(full_path, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
            
            template_content = template_data.get('sql_template', '')
            
            # 缓存模板
            self.template_cache[template_file] = template_content
            
            return template_content
            
        except Exception as e:
            self.logger.error(f"加载模板文件失败 {template_file}: {e}")
            return ""
    
    def _extract_template_variables(self, rule: Dict[str, Any], database_type: str) -> Dict[str, Any]:
        """
        提取模板变量
        
        Args:
            rule: 规则配置
            database_type: 数据库类型
            
        Returns:
            Dict: 模板变量字典
        """
        variables = {}
        
        rule_config = rule.get('rule', {})
        target = rule_config.get('target', {})
        
        # 基本变量
        variables.update({
            'database_name': target.get('database', ''),
            'table_name': target.get('table', ''),
            'partition_column': target.get('partition_key', ''),
            'rule_name': rule_config.get('name', ''),
            'rule_type': rule.get('rule_type', ''),
            'category': rule_config.get('category', ''),
            'priority': rule_config.get('priority', 'medium')
        })
        
        # 数据库方言变量
        dialect = self.database_dialects.get(database_type, self.database_dialects['clickhouse'])
        variables.update({
            'quote_char': dialect['quote_char'],
            'string_quote': dialect['string_quote'],
            'null_check': dialect['null_check'],
            'not_null_check': dialect['not_null_check'],
            'regexp_operator': dialect['regexp_operator']
        })
        
        # 日期函数变量
        date_functions = dialect['date_functions']
        variables.update({
            'today_func': date_functions['today'],
            'now_func': date_functions['now']
        })
        
        # 分区条件
        if target.get('partition_key'):
            partition_condition = f"{target['partition_key']} >= {date_functions['today']} - 30"
        else:
            partition_condition = "1=1"
        variables['partition_condition'] = partition_condition
        
        # 列相关变量
        self._extract_column_variables(rule, variables)
        
        # 业务规则变量
        self._extract_business_rule_variables(rule, variables)
        
        # 相关表变量
        self._extract_related_table_variables(rule, variables)
        
        # 阈值变量
        thresholds = rule_config.get('thresholds', {})
        variables.update(thresholds)
        
        # 检查变量
        checks = rule_config.get('checks', {})
        for check_name, check_config in checks.items():
            if isinstance(check_config, dict) and check_config.get('enabled', True):
                # 添加检查相关的变量
                for key, value in check_config.items():
                    if key != 'enabled':
                        variables[f"{check_name}_{key}"] = value
        
        return variables
    
    def _extract_column_variables(self, rule: Dict[str, Any], variables: Dict[str, Any]):
        """提取列相关变量"""
        columns = rule.get('rule', {}).get('columns', [])
        if columns:
            first_column = columns[0]
            variables.update({
                'column_name': first_column.get('name', ''),
                'data_type': first_column.get('data_type', ''),
            })
            
            # 验证规则变量
            validation_rules = first_column.get('validation_rules', [])
            for validation in validation_rules:
                if validation.get('type') == 'range':
                    variables.update({
                        'min_value': validation.get('min_value', 0),
                        'max_value': validation.get('max_value', 999999)
                    })
                elif validation.get('type') == 'enum':
                    enum_values = validation.get('allowed_values', [])
                    variables['enum_values'] = variables['string_quote'] + (variables['string_quote'] + ', ' + variables['string_quote']).join(map(str, enum_values)) + variables['string_quote']
                elif validation.get('type') == 'format':
                    variables['regex_pattern'] = validation.get('pattern', '')
            
            # 如果有多个列，创建列列表
            if len(columns) > 1:
                column_names = [col.get('name', '') for col in columns]
                variables['column_list'] = ', '.join(column_names)
                variables['quoted_column_list'] = ', '.join([f"{variables['quote_char']}{col}{variables.get('close_quote_char', variables['quote_char'])}" for col in column_names])
    
    def _extract_business_rule_variables(self, rule: Dict[str, Any], variables: Dict[str, Any]):
        """提取业务规则变量"""
        business_rules = rule.get('business_rules', [])
        if business_rules:
            variables['business_rule_condition'] = business_rules[0].get('condition', '1=1')
        else:
            variables['business_rule_condition'] = '1=1'
        
        # 如果有多个业务规则，创建组合条件
        if len(business_rules) > 1:
            conditions = [br.get('condition', '1=1') for br in business_rules]
            variables['combined_business_rules'] = ' AND '.join(f"({cond})" for cond in conditions)
    
    def _extract_related_table_variables(self, rule: Dict[str, Any], variables: Dict[str, Any]):
        """提取相关表变量"""
        related_tables = rule.get('rule', {}).get('related_tables', [])
        if related_tables:
            related = related_tables[0]
            variables.update({
                'related_database': related.get('database', ''),
                'related_table': related.get('table', ''),
            })
            
            # 键列处理
            key_columns = related.get('key_columns', [])
            reference_columns = related.get('reference_columns', [])
            
            if key_columns:
                variables['key_columns'] = ', '.join(key_columns)
                variables['key_column'] = key_columns[0] if key_columns else ''
            
            if reference_columns:
                variables['reference_columns'] = ', '.join(reference_columns)
                variables['reference_column'] = reference_columns[0] if reference_columns else ''
    
    def _adapt_database_dialect(self, template: str, database_type: str) -> str:
        """
        适配数据库方言
        
        Args:
            template: 原始模板
            database_type: 数据库类型
            
        Returns:
            str: 适配后的模板
        """
        if database_type not in self.database_dialects:
            self.logger.warning(f"不支持的数据库类型: {database_type}，使用默认方言")
            database_type = 'clickhouse'
        
        dialect = self.database_dialects[database_type]
        
        # 替换日期函数
        date_functions = dialect['date_functions']
        
        # 替换 today() 函数
        template = re.sub(r'\btoday\(\)', date_functions['today'], template, flags=re.IGNORECASE)
        
        # 替换 now() 函数
        template = re.sub(r'\bnow\(\)', date_functions['now'], template, flags=re.IGNORECASE)
        
        # 替换正则表达式操作符
        if database_type == 'postgresql':
            template = re.sub(r'\bREGEXP\b', '~', template, flags=re.IGNORECASE)
        elif database_type == 'sqlserver':
            # SQL Server 没有原生正则，需要转换为 LIKE 或其他函数
            template = re.sub(r'(\w+)\s+REGEXP\s+', r'\1 LIKE ', template, flags=re.IGNORECASE)
        
        # 替换聚合函数
        agg_functions = dialect['aggregate_functions']
        for func, replacement in agg_functions.items():
            if func != replacement.lower():
                pattern = rf'\b{func}\b'
                template = re.sub(pattern, replacement, template, flags=re.IGNORECASE)
        
        return template
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template: 模板字符串
            variables: 变量字典
            
        Returns:
            str: 渲染后的字符串
        """
        try:
            # 使用Python的string.Template进行基本替换
            template_obj = Template(template)
            
            # 安全替换，忽略缺失的变量
            rendered = template_obj.safe_substitute(variables)
            
            # 处理剩余的占位符 (使用 {variable} 格式)
            for key, value in variables.items():
                pattern = rf'\{{{key}\}}'
                rendered = re.sub(pattern, str(value), rendered)
            
            return rendered
            
        except Exception as e:
            self.logger.error(f"模板渲染失败: {e}")
            return template
    
    def _clean_sql(self, sql: str) -> str:
        """
        清理和格式化SQL
        
        Args:
            sql: SQL字符串
            
        Returns:
            str: 清理后的SQL
        """
        if not sql:
            return sql
        
        # 移除多余的空白
        sql = re.sub(r'\s+', ' ', sql.strip())
        
        # 移除注释后的多余空行
        sql = re.sub(r'\n\s*\n', '\n', sql)
        
        # 移除未替换的占位符（可选）
        # sql = re.sub(r'\{[^}]+\}', '', sql)
        
        return sql
    
    def get_template_variables(self, template: str) -> List[str]:
        """
        提取模板中的变量
        
        Args:
            template: 模板字符串
            
        Returns:
            List[str]: 变量名列表
        """
        variables = set()
        
        # 查找 ${variable} 格式的变量
        dollar_vars = re.findall(r'\$\{([^}]+)\}', template)
        variables.update(dollar_vars)
        
        # 查找 {variable} 格式的变量
        brace_vars = re.findall(r'\{([^}]+)\}', template)
        variables.update(brace_vars)
        
        return sorted(list(variables))
    
    def validate_template(self, template: str, required_variables: List[str] = None) -> List[str]:
        """
        验证模板
        
        Args:
            template: 模板字符串
            required_variables: 必需的变量列表
            
        Returns:
            List[str]: 验证错误列表
        """
        errors = []
        
        if not template.strip():
            errors.append("模板内容为空")
            return errors
        
        # 检查SQL语法基本正确性
        template_lower = template.lower().strip()
        if not (template_lower.startswith('select') or template_lower.startswith('with')):
            errors.append("模板必须是有效的SELECT查询或CTE")
        
        # 检查必需的变量
        if required_variables:
            template_vars = self.get_template_variables(template)
            missing_vars = set(required_variables) - set(template_vars)
            if missing_vars:
                errors.append(f"缺少必需的变量: {', '.join(missing_vars)}")
        
        # 检查配对的括号
        if template.count('(') != template.count(')'):
            errors.append("括号不匹配")
        
        return errors
    
    def create_template_from_rule_type(self, rule_type: str, database_type: str = 'clickhouse') -> str:
        """
        根据规则类型创建基础模板
        
        Args:
            rule_type: 规则类型
            database_type: 数据库类型
            
        Returns:
            str: 基础模板
        """
        dialect = self.database_dialects.get(database_type, self.database_dialects['clickhouse'])
        quote_char = dialect['quote_char']
        
        templates = {
            'completeness': f"""
-- {rule_type.title()} Check for {{table_name}}
WITH completeness_metrics AS (
    SELECT
        COUNT(*) as total_rows,
        COUNT(CASE WHEN {{column_name}} IS NULL THEN 1 END) as null_count,
        COUNT(CASE WHEN {{column_name}} = '' THEN 1 END) as empty_count,
        COUNT(DISTINCT {{column_name}}) as unique_values
    FROM {quote_char}{{database_name}}{quote_char}.{quote_char}{{table_name}}{quote_char}
    WHERE {{partition_condition}}
)
SELECT
    total_rows,
    null_count,
    empty_count,
    unique_values,
    CASE 
        WHEN null_count > 0 THEN 'FAIL'
        WHEN empty_count > 0 THEN 'FAIL'
        ELSE 'PASS'
    END as check_result
FROM completeness_metrics
            """,
            
            'accuracy': f"""
-- {rule_type.title()} Check for {{table_name}}
WITH accuracy_metrics AS (
    SELECT
        COUNT(*) as total_rows,
        COUNT(CASE WHEN {{column_name}} < {{min_value}} OR {{column_name}} > {{max_value}} THEN 1 END) as range_violations,
        COUNT(CASE WHEN {{column_name}} {dialect['regexp_operator']} '{{regex_pattern}}' THEN 0 ELSE 1 END) as format_violations
    FROM {quote_char}{{database_name}}{quote_char}.{quote_char}{{table_name}}{quote_char}
    WHERE {{partition_condition}}
)
SELECT
    total_rows,
    range_violations,
    format_violations,
    CASE 
        WHEN range_violations > 0 THEN 'FAIL'
        WHEN format_violations > 0 THEN 'FAIL'
        ELSE 'PASS'
    END as check_result
FROM accuracy_metrics
            """,
            
            'consistency': f"""
-- {rule_type.title()} Check for {{table_name}}
WITH consistency_metrics AS (
    SELECT
        COUNT(*) as total_rows,
        COUNT(CASE WHEN {{key_column}} IS NOT NULL AND {{key_column}} NOT IN (
            SELECT {{reference_column}} FROM {quote_char}{{related_database}}{quote_char}.{quote_char}{{related_table}}{quote_char}
        ) THEN 1 END) as referential_violations
    FROM {quote_char}{{database_name}}{quote_char}.{quote_char}{{table_name}}{quote_char}
    WHERE {{partition_condition}}
)
SELECT
    total_rows,
    referential_violations,
    CASE 
        WHEN referential_violations > 0 THEN 'FAIL'
        ELSE 'PASS'
    END as check_result
FROM consistency_metrics
            """
        }
        
        return templates.get(rule_type, templates['completeness']).strip()
    
    def get_supported_databases(self) -> List[str]:
        """
        获取支持的数据库类型
        
        Returns:
            List[str]: 支持的数据库类型列表
        """
        return list(self.database_dialects.keys())
