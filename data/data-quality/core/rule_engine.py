#!/usr/bin/env python3
"""
数据质量规则引擎
负责规则的加载、验证、管理和执行逻辑
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path


class RuleEngine:
    """数据质量规则引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化规则引擎
        
        Args:
            config: 全局配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.rules_cache = {}
        self.rule_schemas = self._load_rule_schemas()
        
    def _load_rule_schemas(self) -> Dict[str, Dict]:
        """
        加载规则schema定义
        
        Returns:
            Dict: 规则类型到schema的映射
        """
        schemas = {
            'completeness': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table'],
                'optional_fields': ['rule.columns', 'rule.checks', 'rule.thresholds'],
                'checks': ['null_check', 'empty_string_check', 'duplicate_check', 'volume_check']
            },
            'accuracy': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table'],
                'optional_fields': ['rule.columns', 'rule.checks', 'rule.thresholds'],
                'checks': ['range_check', 'format_check', 'enum_check', 'business_rule_check']
            },
            'consistency': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table'],
                'optional_fields': ['rule.related_tables', 'rule.checks', 'rule.thresholds'],
                'checks': ['referential_integrity', 'cross_table_consistency', 'schema_consistency']
            },
            'timeliness': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table'],
                'optional_fields': ['rule.time_columns', 'rule.checks', 'rule.thresholds'],
                'checks': ['freshness_check', 'latency_check', 'frequency_check']
            },
            'connectivity': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table'],
                'optional_fields': ['rule.checks', 'rule.thresholds'],
                'checks': ['connection_test', 'system_access_test', 'function_test']
            },
            'referential_integrity': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table', 'rule.reference.database', 'rule.reference.table', 'rule.reference.column'],
                'optional_fields': ['rule.checks', 'rule.thresholds', 'rule.conditions'],
                'checks': ['foreign_key_check', 'orphan_check', 'circular_reference_check']
            },
            'uniqueness': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table', 'rule.columns'],
                'optional_fields': ['rule.checks', 'rule.thresholds', 'rule.conditions'],
                'checks': ['single_column_unique', 'composite_unique', 'business_key_unique']
            },
            'custom': {
                'required_fields': ['rule.name', 'rule.target.database', 'rule.target.table', 'rule.template'],
                'optional_fields': ['rule.parameters', 'rule.conditions', 'rule.thresholds'],
                'checks': ['custom_check']
            }
        }
        return schemas
    
    def load_rules(self, rule_paths: List[str], scenario: str = None) -> List[Dict]:
        """
        从指定路径加载规则
        
        Args:
            rule_paths: 规则文件路径列表
            scenario: 场景名称，用于过滤规则
            
        Returns:
            List[Dict]: 加载的规则列表
        """
        all_rules = []
        
        for rule_path in rule_paths:
            try:
                rules = self._load_rules_from_path(rule_path)
                all_rules.extend(rules)
            except Exception as e:
                self.logger.error(f"加载规则文件失败 {rule_path}: {e}")
        
        # 过滤场景
        if scenario:
            all_rules = self._filter_rules_by_scenario(all_rules, scenario)
        
        # 验证规则
        valid_rules = []
        for rule in all_rules:
            if self.validate_rule(rule):
                valid_rules.append(rule)
            else:
                rule_name = rule.get('rule', {}).get('name', 'unknown')
                self.logger.warning(f"规则验证失败，跳过: {rule_name}")
        
        self.logger.info(f"成功加载 {len(valid_rules)} 个有效规则")
        return valid_rules
    
    def _load_rules_from_path(self, rule_path: str) -> List[Dict]:
        """
        从单个路径加载规则
        
        Args:
            rule_path: 规则文件或目录路径
            
        Returns:
            List[Dict]: 规则列表
        """
        path = Path(rule_path)
        rules = []
        
        if path.is_file():
            # 单个文件
            if path.suffix.lower() in ['.yml', '.yaml']:
                rules.extend(self._load_yaml_rules(str(path)))
        elif path.is_dir():
            # 目录，递归查找所有yaml文件
            for yaml_file in path.rglob('*.yml'):
                rules.extend(self._load_yaml_rules(str(yaml_file)))
            for yaml_file in path.rglob('*.yaml'):
                rules.extend(self._load_yaml_rules(str(yaml_file)))
        else:
            self.logger.warning(f"规则路径不存在: {rule_path}")
        
        return rules
    
    def _load_yaml_rules(self, file_path: str) -> List[Dict]:
        """
        从YAML文件加载规则
        
        Args:
            file_path: YAML文件路径
            
        Returns:
            List[Dict]: 规则列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            # 如果是单个规则，转换为列表
            if isinstance(content, dict):
                content = [content]
            elif not isinstance(content, list):
                self.logger.warning(f"无效的规则文件格式: {file_path}")
                return []
            
            # 为每个规则添加文件信息
            for rule in content:
                rule['_source_file'] = file_path
                rule['_file_name'] = os.path.basename(file_path)
            
            self.logger.debug(f"从 {file_path} 加载了 {len(content)} 个规则")
            return content
            
        except Exception as e:
            self.logger.error(f"解析YAML文件失败 {file_path}: {e}")
            return []
    
    def _filter_rules_by_scenario(self, rules: List[Dict], scenario: str) -> List[Dict]:
        """
        根据场景过滤规则
        
        Args:
            rules: 规则列表
            scenario: 场景名称
            
        Returns:
            List[Dict]: 过滤后的规则列表
        """
        filtered_rules = []
        
        for rule in rules:
            # 检查规则是否启用
            if not rule.get('rule', {}).get('enabled', True):
                continue
            
            # 检查场景匹配
            rule_scenarios = rule.get('scenarios', [])
            if not rule_scenarios:
                # 如果规则没有指定场景，则在所有场景中可用
                filtered_rules.append(rule)
            elif scenario in rule_scenarios:
                # 明确指定了该场景
                filtered_rules.append(rule)
            elif scenario == 'all':
                # 特殊场景：包含所有规则
                filtered_rules.append(rule)
        
        self.logger.info(f"场景 '{scenario}' 过滤后剩余 {len(filtered_rules)} 个规则")
        return filtered_rules
    
    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        """
        验证规则配置的有效性
        
        Args:
            rule: 规则配置
            
        Returns:
            bool: 是否有效
        """
        try:
            # 检查基本结构
            if not isinstance(rule, dict):
                self.logger.error("规则必须是字典类型")
                return False
            
            # 检查规则类型
            rule_type = rule.get('rule_type')
            if not rule_type:
                self.logger.error("规则缺少 rule_type 字段")
                return False
            
            if rule_type not in self.rule_schemas:
                self.logger.error(f"不支持的规则类型: {rule_type}")
                return False
            
            # 获取该类型的schema
            schema = self.rule_schemas[rule_type]
            
            # 检查必填字段
            for required_field in schema.get('required_fields', []):
                if not self._check_nested_field(rule, required_field):
                    self.logger.error(f"规则缺少必填字段: {required_field}")
                    return False
            
            # 检查rule部分的基本字段
            rule_config = rule.get('rule', {})
            if not rule_config.get('name'):
                self.logger.error("规则缺少名称")
                return False
            
            # 检查目标表配置
            target = rule_config.get('target', {})
            if not target.get('database') or not target.get('table'):
                self.logger.error("规则缺少目标数据库或表配置")
                return False
            
            # 检查SQL模板或template字段
            if not rule_config.get('template') and not rule.get('sql_template'):
                self.logger.error("规则缺少SQL模板")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"规则验证异常: {e}")
            return False
    
    def _check_nested_field(self, data: Dict, field_path: str) -> bool:
        """
        检查嵌套字段是否存在
        
        Args:
            data: 数据字典
            field_path: 字段路径，用.分隔，如 'rule.target.database'
            
        Returns:
            bool: 字段是否存在且有值
        """
        try:
            keys = field_path.split('.')
            current = data
            
            for key in keys:
                if not isinstance(current, dict) or key not in current:
                    return False
                current = current[key]
            
            # 检查值是否为空
            return current is not None and str(current).strip() != ''
            
        except Exception:
            return False
    
    def get_rule_by_name(self, rule_name: str, rules: List[Dict]) -> Optional[Dict]:
        """
        根据名称查找规则
        
        Args:
            rule_name: 规则名称
            rules: 规则列表
            
        Returns:
            Optional[Dict]: 找到的规则，未找到返回None
        """
        for rule in rules:
            if rule.get('rule', {}).get('name') == rule_name:
                return rule
        return None
    
    def get_rules_by_type(self, rule_type: str, rules: List[Dict]) -> List[Dict]:
        """
        根据类型筛选规则
        
        Args:
            rule_type: 规则类型
            rules: 规则列表
            
        Returns:
            List[Dict]: 符合类型的规则列表
        """
        return [rule for rule in rules if rule.get('rule_type') == rule_type]
    
    def get_rules_by_priority(self, priority: str, rules: List[Dict]) -> List[Dict]:
        """
        根据优先级筛选规则
        
        Args:
            priority: 优先级 (high, medium, low)
            rules: 规则列表
            
        Returns:
            List[Dict]: 符合优先级的规则列表
        """
        return [rule for rule in rules if rule.get('rule', {}).get('priority', 'medium') == priority]
    
    def get_rules_by_category(self, category: str, rules: List[Dict]) -> List[Dict]:
        """
        根据类别筛选规则
        
        Args:
            category: 类别名称
            rules: 规则列表
            
        Returns:
            List[Dict]: 符合类别的规则列表
        """
        return [rule for rule in rules if rule.get('rule', {}).get('category') == category]
    
    def get_rules_statistics(self, rules: List[Dict]) -> Dict[str, Any]:
        """
        获取规则统计信息
        
        Args:
            rules: 规则列表
            
        Returns:
            Dict: 统计信息
        """
        stats = {
            'total_rules': len(rules),
            'by_type': {},
            'by_priority': {'high': 0, 'medium': 0, 'low': 0},
            'by_category': {},
            'enabled_rules': 0,
            'disabled_rules': 0
        }
        
        for rule in rules:
            # 按类型统计
            rule_type = rule.get('rule_type', 'unknown')
            stats['by_type'][rule_type] = stats['by_type'].get(rule_type, 0) + 1
            
            # 按优先级统计
            priority = rule.get('rule', {}).get('priority', 'medium')
            if priority in stats['by_priority']:
                stats['by_priority'][priority] += 1
            
            # 按类别统计
            category = rule.get('rule', {}).get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # 按启用状态统计
            if rule.get('rule', {}).get('enabled', True):
                stats['enabled_rules'] += 1
            else:
                stats['disabled_rules'] += 1
        
        return stats
    
    def validate_rule_dependencies(self, rules: List[Dict]) -> List[str]:
        """
        验证规则依赖关系
        
        Args:
            rules: 规则列表
            
        Returns:
            List[str]: 依赖问题列表
        """
        issues = []
        rule_names = {rule.get('rule', {}).get('name') for rule in rules}
        
        for rule in rules:
            rule_name = rule.get('rule', {}).get('name')
            dependencies = rule.get('dependencies', [])
            
            for dep in dependencies:
                if dep not in rule_names:
                    issues.append(f"规则 '{rule_name}' 依赖的规则 '{dep}' 不存在")
        
        return issues
    
    def sort_rules_by_dependency(self, rules: List[Dict]) -> List[Dict]:
        """
        根据依赖关系对规则进行排序
        
        Args:
            rules: 规则列表
            
        Returns:
            List[Dict]: 排序后的规则列表
        """
        # 简单实现：按优先级排序，高优先级的先执行
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        def get_priority_value(rule):
            priority = rule.get('rule', {}).get('priority', 'medium')
            return priority_order.get(priority, 1)
        
        return sorted(rules, key=get_priority_value)
    
    def get_supported_rule_types(self) -> List[str]:
        """
        获取支持的规则类型列表
        
        Returns:
            List[str]: 支持的规则类型
        """
        return list(self.rule_schemas.keys())
    
    def get_rule_template_variables(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取规则的模板变量
        
        Args:
            rule: 规则配置
            
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
        
        # 分区条件
        if target.get('partition_key'):
            partition_condition = f"{target['partition_key']} >= today() - 30"
        else:
            partition_condition = "1=1"
        variables['partition_condition'] = partition_condition
        
        # 列相关变量
        columns = rule_config.get('columns', [])
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
                    variables['enum_values'] = "'" + "', '".join(map(str, enum_values)) + "'"
                elif validation.get('type') == 'format':
                    variables['regex_pattern'] = validation.get('pattern', '')
        
        # 业务规则变量
        business_rules = rule.get('business_rules', [])
        if business_rules:
            variables['business_rule_condition'] = business_rules[0].get('condition', '1=1')
        
        # 相关表变量
        related_tables = rule_config.get('related_tables', [])
        if related_tables:
            related = related_tables[0]
            variables.update({
                'related_database': related.get('database', ''),
                'related_table': related.get('table', ''),
                'key_columns': related.get('key_columns', []),
                'reference_columns': related.get('reference_columns', [])
            })
        
        # 阈值变量
        thresholds = rule_config.get('thresholds', {})
        variables.update(thresholds)
        
        return variables
