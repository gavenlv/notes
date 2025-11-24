#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主数据质量评估工具
实现对主数据质量的全面评估和监控
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict
import re
import logging
import hashlib
import uuid
import statistics
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class QualityDimension:
    """质量维度"""
    name: str
    description: str
    weight: float
    threshold: float
    
    def to_dict(self):
        """转换为字典"""
        return asdict(self)


@dataclass
class QualityAssessment:
    """质量评估结果"""
    assessment_id: str
    entity_id: str
    entity_type: str
    dimensions: Dict[str, float]
    overall_score: float
    grade: str  # 'A', 'B', 'C', 'D', 'F'
    assessment_date: datetime
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    
    def to_dict(self):
        """转换为字典"""
        result = asdict(self)
        result['assessment_date'] = self.assessment_date.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建评估结果"""
        data['assessment_date'] = datetime.fromisoformat(data['assessment_date'])
        return cls(**data)


class QualityRule:
    """质量规则"""
    
    def __init__(self, rule_id: str, name: str, description: str, 
                 dimension: str, check_function: Callable, 
                 severity: str = 'medium', weight: float = 1.0):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.dimension = dimension
        self.check_function = check_function
        self.severity = severity  # 'low', 'medium', 'high', 'critical'
        self.weight = weight
    
    def check(self, entity_data: Dict[str, Any], field: str = None) -> Dict[str, Any]:
        """执行质量检查"""
        try:
            result = self.check_function(entity_data, field)
            result['rule_id'] = self.rule_id
            result['rule_name'] = self.name
            result['dimension'] = self.dimension
            result['severity'] = self.severity
            return result
        except Exception as e:
            logger.error(f"Error in rule {self.name}: {e}")
            return {
                'passed': False,
                'score': 0.0,
                'message': f"Rule execution error: {str(e)}",
                'rule_id': self.rule_id,
                'rule_name': self.name,
                'dimension': self.dimension,
                'severity': 'critical'  # 规则执行错误视为严重问题
            }


class CompletenessAssessor:
    """完整性评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.required_fields = self.config.get('required_fields', {})
        self.optional_fields = self.config.get('optional_fields', {})
    
    def assess(self, entity_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """评估完整性"""
        # 获取必填字段和可选字段
        required = self.required_fields.get(entity_type, [])
        optional = self.optional_fields.get(entity_type, [])
        
        # 计算必填字段完整性
        required_filled = sum(1 for field in required 
                             if field in entity_data and entity_data[field] is not None and str(entity_data[field]).strip())
        required_completeness = required_filled / len(required) if required else 1.0
        
        # 计算可选字段完整性
        optional_filled = sum(1 for field in optional 
                             if field in entity_data and entity_data[field] is not None and str(entity_data[field]).strip())
        optional_completeness = optional_filled / len(optional) if optional else 0.0
        
        # 综合完整性评分（必填字段权重更高）
        overall_completeness = 0.7 * required_completeness + 0.3 * optional_completeness
        
        # 识别缺失字段
        missing_required = [field for field in required 
                           if field not in entity_data or entity_data[field] is None or str(entity_data[field]).strip() == '']
        missing_optional = [field for field in optional 
                           if field not in entity_data or entity_data[field] is None or str(entity_data[field]).strip() == '']
        
        issues = []
        if missing_required:
            issues.append({
                'type': 'missing_required_fields',
                'fields': missing_required,
                'severity': 'high',
                'message': f"Missing required fields: {', '.join(missing_required)}"
            })
        
        if missing_optional and optional_completeness < 0.5:
            issues.append({
                'type': 'missing_optional_fields',
                'fields': missing_optional,
                'severity': 'medium',
                'message': f"Many optional fields missing: {', '.join(missing_optional[:5])}"
            })
        
        return {
            'dimension': 'completeness',
            'score': overall_completeness,
            'details': {
                'required_completeness': required_completeness,
                'optional_completeness': optional_completeness,
                'missing_required': missing_required,
                'missing_optional': missing_optional
            },
            'issues': issues
        }


class AccuracyAssessor:
    """准确性评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.validation_patterns = self.config.get('validation_patterns', {})
        self.reference_data = self.config.get('reference_data', {})
    
    def assess(self, entity_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """评估准确性"""
        total_checks = 0
        passed_checks = 0
        issues = []
        field_scores = {}
        
        # 获取该类型的验证模式
        patterns = self.validation_patterns.get(entity_type, {})
        
        # 检查每个字段的准确性
        for field, value in entity_data.items():
            if field in patterns:
                validation = patterns[field]
                result = self._validate_field(field, value, validation)
                
                total_checks += 1
                if result['passed']:
                    passed_checks += 1
                    field_scores[field] = result.get('score', 1.0)
                else:
                    field_scores[field] = result.get('score', 0.0)
                    issues.append({
                        'type': 'field_accuracy',
                        'field': field,
                        'severity': result.get('severity', 'medium'),
                        'message': result.get('message', f"Field {field} failed accuracy check")
                    })
        
        # 计算总体准确性
        overall_accuracy = passed_checks / total_checks if total_checks > 0 else 1.0
        
        # 检查参考数据一致性
        if entity_type in self.reference_data:
            reference_result = self._check_reference_data(entity_data, entity_type)
            if reference_result['passed']:
                overall_accuracy = (overall_accuracy + reference_result['score']) / 2
            else:
                overall_accuracy *= 0.8  # 如果参考数据不一致，降低总分
                issues.append(reference_result)
        
        return {
            'dimension': 'accuracy',
            'score': overall_accuracy,
            'details': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'field_scores': field_scores
            },
            'issues': issues
        }
    
    def _validate_field(self, field: str, value: Any, validation: Dict[str, Any]) -> Dict[str, Any]:
        """验证字段值"""
        if value is None or value == '':
            return {
                'passed': False,
                'score': 0.0,
                'message': f"Field {field} is empty",
                'severity': 'medium'
            }
        
        # 数据类型检查
        if 'type' in validation:
            expected_type = validation['type']
            if expected_type == 'string' and not isinstance(value, str):
                return {
                    'passed': False,
                    'score': 0.0,
                    'message': f"Field {field} is not a string",
                    'severity': 'high'
                }
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                return {
                    'passed': False,
                    'score': 0.0,
                    'message': f"Field {field} is not a number",
                    'severity': 'high'
                }
            elif expected_type == 'email' and not self._is_valid_email(str(value)):
                return {
                    'passed': False,
                    'score': 0.0,
                    'message': f"Field {field} is not a valid email",
                    'severity': 'high'
                }
            elif expected_type == 'phone' and not self._is_valid_phone(str(value)):
                return {
                    'passed': False,
                    'score': 0.0,
                    'message': f"Field {field} is not a valid phone number",
                    'severity': 'high'
                }
            elif expected_type == 'date' and not self._is_valid_date(str(value)):
                return {
                    'passed': False,
                    'score': 0.0,
                    'message': f"Field {field} is not a valid date",
                    'severity': 'high'
                }
        
        # 范围检查
        if 'min' in validation and value < validation['min']:
            return {
                'passed': False,
                'score': 0.5,
                'message': f"Field {field} is below minimum value {validation['min']}",
                'severity': 'medium'
            }
        
        if 'max' in validation and value > validation['max']:
            return {
                'passed': False,
                'score': 0.5,
                'message': f"Field {field} is above maximum value {validation['max']}",
                'severity': 'medium'
            }
        
        # 长度检查
        if isinstance(value, str):
            if 'min_length' in validation and len(value) < validation['min_length']:
                return {
                    'passed': False,
                    'score': 0.5,
                    'message': f"Field {field} is too short",
                    'severity': 'medium'
                }
            
            if 'max_length' in validation and len(value) > validation['max_length']:
                return {
                    'passed': False,
                    'score': 0.5,
                    'message': f"Field {field} is too long",
                    'severity': 'medium'
                }
        
        # 模式检查
        if 'pattern' in validation:
            if not re.match(validation['pattern'], str(value)):
                return {
                    'passed': False,
                    'score': 0.5,
                    'message': f"Field {field} does not match required pattern",
                    'severity': 'medium'
                }
        
        return {
            'passed': True,
            'score': 1.0,
            'message': f"Field {field} passed all checks"
        }
    
    def _check_reference_data(self, entity_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """检查参考数据一致性"""
        reference = self.reference_data.get(entity_type, {})
        match_count = 0
        total_checks = 0
        
        for field, ref_values in reference.items():
            if field in entity_data:
                total_checks += 1
                if entity_data[field] in ref_values:
                    match_count += 1
        
        if total_checks == 0:
            return {
                'passed': True,
                'score': 1.0,
                'message': "No reference data to check"
            }
        
        consistency = match_count / total_checks
        
        return {
            'passed': consistency >= 0.8,
            'score': consistency,
            'message': f"Reference data consistency: {consistency:.2%}",
            'type': 'reference_data_consistency',
            'severity': 'medium' if consistency >= 0.5 else 'high'
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """检查是否为有效的电子邮件"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """检查是否为有效的电话号码"""
        # 简化的电话号码验证
        pattern = r'^[\d\s\-\+\(\)]+$'
        return re.match(pattern, phone) is not None and len(phone.replace(' ', '').replace('-', '')) >= 7
    
    def _is_valid_date(self, date_str: str) -> bool:
        """检查是否为有效的日期"""
        try:
            # 尝试解析常见的日期格式
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                try:
                    datetime.strptime(date_str, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False


class ConsistencyAssessor:
    """一致性评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.consistency_rules = self.config.get('consistency_rules', {})
        self.cross_field_rules = self.config.get('cross_field_rules', {})
    
    def assess(self, entity_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """评估一致性"""
        total_checks = 0
        passed_checks = 0
        issues = []
        
        # 获取一致性规则
        rules = self.consistency_rules.get(entity_type, {})
        
        # 检查字段内部一致性
        for field, rule in rules.items():
            if field in entity_data:
                result = self._check_field_consistency(entity_data[field], rule)
                
                total_checks += 1
                if result['passed']:
                    passed_checks += 1
                else:
                    issues.append({
                        'type': 'field_consistency',
                        'field': field,
                        'severity': result.get('severity', 'medium'),
                        'message': result.get('message', f"Field {field} failed consistency check")
                    })
        
        # 检查跨字段一致性
        cross_rules = self.cross_field_rules.get(entity_type, [])
        for rule in cross_rules:
            if all(field in entity_data for field in rule['fields']):
                result = self._check_cross_field_consistency(entity_data, rule)
                
                total_checks += 1
                if result['passed']:
                    passed_checks += 1
                else:
                    issues.append({
                        'type': 'cross_field_consistency',
                        'fields': rule['fields'],
                        'severity': result.get('severity', 'medium'),
                        'message': result.get('message', f"Cross-field consistency check failed")
                    })
        
        # 计算总体一致性
        overall_consistency = passed_checks / total_checks if total_checks > 0 else 1.0
        
        return {
            'dimension': 'consistency',
            'score': overall_consistency,
            'details': {
                'total_checks': total_checks,
                'passed_checks': passed_checks
            },
            'issues': issues
        }
    
    def _check_field_consistency(self, value: Any, rule: Dict[str, Any]) -> Dict[str, Any]:
        """检查字段内部一致性"""
        # 检查值域一致性
        if 'values' in rule:
            if value not in rule['values']:
                return {
                    'passed': False,
                    'message': f"Value '{value}' not in allowed values: {rule['values']}",
                    'severity': 'high'
                }
        
        # 检查格式一致性
        if 'format' in rule:
            if not re.match(rule['format'], str(value)):
                return {
                    'passed': False,
                    'message': f"Value '{value}' does not match required format",
                    'severity': 'medium'
                }
        
        return {
            'passed': True,
            'message': "Field passed consistency check"
        }
    
    def _check_cross_field_consistency(self, entity_data: Dict[str, Any], 
                                      rule: Dict[str, Any]) -> Dict[str, Any]:
        """检查跨字段一致性"""
        if rule['type'] == 'conditional':
            # 条件一致性：一个字段的值决定另一个字段的值
            condition = rule['condition']
            condition_field = condition['field']
            condition_value = condition['value']
            result_field = rule['result']['field']
            expected_value = rule['result']['value']
            
            if entity_data[condition_field] == condition_value:
                if entity_data[result_field] != expected_value:
                    return {
                        'passed': False,
                        'message': f"When {condition_field} is {condition_value}, {result_field} should be {expected_value}, but is {entity_data[result_field]}",
                        'severity': 'medium'
                    }
        
        elif rule['type'] == 'correlation':
            # 相关性一致性：两个字段的值应该相关
            correlation = rule['correlation']
            field1, field2 = rule['fields']
            
            if correlation == 'positive':
                # 正相关：两个字段应该同时存在或同时不存在
                if (entity_data[field1] and not entity_data[field2]) or (not entity_data[field1] and entity_data[field2]):
                    return {
                        'passed': False,
                        'message': f"Fields {field1} and {field2} should be correlated",
                        'severity': 'medium'
                    }
            elif correlation == 'negative':
                # 负相关：两个字段不应该同时存在
                if entity_data[field1] and entity_data[field2]:
                    return {
                        'passed': False,
                        'message': f"Fields {field1} and {field2} should not both have values",
                        'severity': 'medium'
                    }
        
        return {
            'passed': True,
            'message': "Cross-field consistency check passed"
        }


class UniquenessAssessor:
    """唯一性评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.unique_fields = self.config.get('unique_fields', {})
        self.key_fields = self.config.get('key_fields', {})
    
    def assess(self, entity_data: Dict[str, Any], entity_type: str, 
               all_entities: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """评估唯一性"""
        if not all_entities:
            # 如果没有提供所有实体数据，假设唯一性满足
            return {
                'dimension': 'uniqueness',
                'score': 1.0,
                'details': {'message': 'No duplicate check performed'},
                'issues': []
            }
        
        # 获取需要检查唯一性的字段
        unique_fields = self.unique_fields.get(entity_type, [])
        key_fields = self.key_fields.get(entity_type, [])
        
        if not unique_fields and not key_fields:
            return {
                'dimension': 'uniqueness',
                'score': 1.0,
                'details': {'message': 'No uniqueness rules defined for this entity type'},
                'issues': []
            }
        
        total_checks = 0
        passed_checks = 0
        issues = []
        duplicates = {}
        
        # 检查唯一字段
        for field in unique_fields:
            if field in entity_data:
                total_checks += 1
                value = entity_data[field]
                
                # 查找重复值
                duplicate_count = sum(1 for e in all_entities 
                                     if e.get('entity_id') != entity_data.get('entity_id') 
                                     and e.get(field) == value)
                
                if duplicate_count > 0:
                    duplicates[field] = duplicate_count + 1  # 包括当前实体
                    issues.append({
                        'type': 'duplicate_unique_field',
                        'field': field,
                        'count': duplicate_count + 1,
                        'severity': 'high',
                        'message': f"Unique field {field} has {duplicate_count + 1} duplicates"
                    })
                else:
                    passed_checks += 1
        
        # 检查关键字段组合
        for key_combo in key_fields:
            if all(field in entity_data for field in key_combo):
                total_checks += 1
                key_value = tuple(entity_data[field] for field in key_combo)
                
                # 查找重复的组合值
                duplicate_count = sum(1 for e in all_entities 
                                     if e.get('entity_id') != entity_data.get('entity_id') 
                                     and tuple(e.get(field) for field in key_combo) == key_value)
                
                if duplicate_count > 0:
                    combo_str = '-'.join(str(v) for v in key_value)
                    duplicates['-'.join(key_combo)] = duplicate_count + 1
                    issues.append({
                        'type': 'duplicate_key_fields',
                        'fields': key_combo,
                        'count': duplicate_count + 1,
                        'severity': 'high',
                        'message': f"Key field combination {combo_str} has {duplicate_count + 1} duplicates"
                    })
                else:
                    passed_checks += 1
        
        # 计算总体唯一性
        overall_uniqueness = passed_checks / total_checks if total_checks > 0 else 1.0
        
        return {
            'dimension': 'uniqueness',
            'score': overall_uniqueness,
            'details': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'duplicates': duplicates
            },
            'issues': issues
        }


class TimelinessAssessor:
    """及时性评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.timeliness_rules = self.config.get('timeliness_rules', {})
        self.current_date = datetime.now()
    
    def assess(self, entity_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """评估及时性"""
        total_checks = 0
        passed_checks = 0
        issues = []
        field_scores = {}
        
        # 获取及时性规则
        rules = self.timeliness_rules.get(entity_type, {})
        
        for field, rule in rules.items():
            if field in entity_data:
                total_checks += 1
                result = self._check_field_timeliness(entity_data[field], rule)
                field_scores[field] = result['score']
                
                if result['passed']:
                    passed_checks += 1
                else:
                    issues.append({
                        'type': 'field_timeliness',
                        'field': field,
                        'severity': result.get('severity', 'medium'),
                        'message': result.get('message', f"Field {field} failed timeliness check")
                    })
        
        # 计算总体及时性
        overall_timeliness = passed_checks / total_checks if total_checks > 0 else 1.0
        
        return {
            'dimension': 'timeliness',
            'score': overall_timeliness,
            'details': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'field_scores': field_scores
            },
            'issues': issues
        }
    
    def _check_field_timeliness(self, value: Any, rule: Dict[str, Any]) -> Dict[str, Any]:
        """检查字段及时性"""
        if value is None:
            return {
                'passed': True,
                'score': 1.0,
                'message': "Null field, not checking timeliness"
            }
        
        # 转换为日期
        try:
            if isinstance(value, str):
                # 尝试解析常见的日期格式
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                    try:
                        date_value = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # 如果所有格式都失败，尝试解析ISO格式
                    date_value = datetime.fromisoformat(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return {
                    'passed': True,
                    'score': 1.0,
                    'message': "Field is not a date, not checking timeliness"
                }
        except:
            return {
                'passed': True,
                'score': 1.0,
                'message': "Could not parse date, not checking timeliness"
            }
        
        # 计算时间差
        time_diff = abs((self.current_date - date_value).days)
        
        # 检查是否在允许的时间范围内
        if 'max_days' in rule:
            max_days = rule['max_days']
            if time_diff > max_days:
                # 计算分数
                score = max(0.0, 1.0 - (time_diff - max_days) / max_days)
                return {
                    'passed': False,
                    'score': score,
                    'message': f"Field is {time_diff} days old, exceeds maximum of {max_days} days",
                    'severity': 'medium' if time_diff < 2 * max_days else 'high'
                }
        
        # 检查是否在期望的时间范围内
        if 'expected_range' in rule:
            min_days, max_days = rule['expected_range']
            if time_diff < min_days or time_diff > max_days:
                # 计算分数
                if time_diff < min_days:
                    score = time_diff / min_days
                else:
                    score = max(0.0, 1.0 - (time_diff - max_days) / max_days)
                
                return {
                    'passed': False,
                    'score': score,
                    'message': f"Field age {time_diff} days is outside expected range {min_days}-{max_days} days",
                    'severity': 'medium'
                }
        
        return {
            'passed': True,
            'score': 1.0,
            'message': "Field passed timeliness check"
        }


class DataQualityAssessmentTool:
    """数据质量评估工具"""
    
    def __init__(self, config_path: str = None):
        """初始化数据质量评估工具"""
        self.config = self._load_config(config_path)
        
        # 初始化数据库
        self.db_path = self.config.get('db_path', 'data_quality.db')
        self._initialize_database()
        
        # 初始化各维度评估器
        self.completeness_assessor = CompletenessAssessor(self.config.get('completeness', {}))
        self.accuracy_assessor = AccuracyAssessor(self.config.get('accuracy', {}))
        self.consistency_assessor = ConsistencyAssessor(self.config.get('consistency', {}))
        self.uniqueness_assessor = UniquenessAssessor(self.config.get('uniqueness', {}))
        self.timeliness_assessor = TimelinessAssessor(self.config.get('timeliness', {}))
        
        # 初始化质量维度
        self.dimensions = self._initialize_dimensions()
        
        # 初始化质量规则
        self.rules = []
        self._initialize_rules()
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "db_path": "data_quality.db",
            "completeness": {
                "required_fields": {
                    "customer": ["name", "email", "phone"],
                    "product": ["name", "sku", "price"],
                    "supplier": ["name", "contact_email"]
                },
                "optional_fields": {
                    "customer": ["address", "city", "country"],
                    "product": ["description", "category"],
                    "supplier": ["address", "phone"]
                }
            },
            "accuracy": {
                "validation_patterns": {
                    "customer": {
                        "email": {"type": "email"},
                        "phone": {"type": "phone"},
                        "postal_code": {"pattern": r"^\d{5,6}(-\d{4})?$"}
                    },
                    "product": {
                        "price": {"type": "number", "min": 0},
                        "sku": {"pattern": r"^[A-Z0-9]{3,10}$"}
                    }
                },
                "reference_data": {
                    "customer": {
                        "country": ["China", "USA", "UK", "Japan", "Germany"]
                    }
                }
            },
            "consistency": {
                "consistency_rules": {
                    "customer": {
                        "status": {"values": ["active", "inactive", "pending"]},
                        "gender": {"values": ["male", "female", "other"]}
                    }
                },
                "cross_field_rules": {
                    "customer": [
                        {
                            "type": "conditional",
                            "condition": {"field": "status", "value": "inactive"},
                            "result": {"field": "last_order_date", "value": None}
                        }
                    ]
                }
            },
            "uniqueness": {
                "unique_fields": {
                    "customer": ["email"],
                    "product": ["sku"]
                },
                "key_fields": {
                    "customer": [["name", "phone"], ["name", "address"]]
                }
            },
            "timeliness": {
                "timeliness_rules": {
                    "customer": {
                        "last_update_date": {"max_days": 365},
                        "last_order_date": {"expected_range": [1, 90]}
                    },
                    "product": {
                        "last_update_date": {"max_days": 180}
                    }
                }
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                # 合并配置
                for key, value in file_config.items():
                    if key in default_config and isinstance(default_config[key], dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
        
        return default_config
    
    def _initialize_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建质量评估结果表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_assessments (
            assessment_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            dimensions TEXT NOT NULL,
            overall_score REAL NOT NULL,
            grade TEXT NOT NULL,
            assessment_date TEXT NOT NULL,
            issues TEXT,
            recommendations TEXT
        )
        ''')
        
        # 创建质量趋势表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_trends (
            trend_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            dimension TEXT NOT NULL,
            average_score REAL NOT NULL,
            assessment_date TEXT NOT NULL,
            entity_count INTEGER NOT NULL
        )
        ''')
        
        # 创建质量规则表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_rules (
            rule_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            dimension TEXT NOT NULL,
            severity TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            creation_date TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_dimensions(self) -> Dict[str, QualityDimension]:
        """初始化质量维度"""
        dimensions = {
            'completeness': QualityDimension(
                name='completeness',
                description='完整性 - 数据是否包含所有必要的信息',
                weight=0.3,
                threshold=0.9
            ),
            'accuracy': QualityDimension(
                name='accuracy',
                description='准确性 - 数据是否正确反映现实世界',
                weight=0.25,
                threshold=0.95
            ),
            'consistency': QualityDimension(
                name='consistency',
                description='一致性 - 数据是否在内部和跨系统保持一致',
                weight=0.2,
                threshold=0.9
            ),
            'uniqueness': QualityDimension(
                name='uniqueness',
                description='唯一性 - 数据是否没有重复',
                weight=0.15,
                threshold=0.95
            ),
            'timeliness': QualityDimension(
                name='timeliness',
                description='及时性 - 数据是否及时更新',
                weight=0.1,
                threshold=0.8
            )
        }
        
        return dimensions
    
    def _initialize_rules(self):
        """初始化质量规则"""
        # 这里可以添加自定义质量规则
        # 为了简化，暂时使用默认配置中的规则
        pass
    
    def assess_entity(self, entity_data: Dict[str, Any], entity_type: str, 
                      all_entities: List[Dict[str, Any]] = None) -> QualityAssessment:
        """评估单个实体的数据质量"""
        assessment_id = str(uuid.uuid4())
        assessment_date = datetime.now()
        
        # 评估各维度
        dimension_results = {}
        all_issues = []
        
        # 完整性评估
        completeness_result = self.completeness_assessor.assess(entity_data, entity_type)
        dimension_results['completeness'] = completeness_result['score']
        all_issues.extend(completeness_result.get('issues', []))
        
        # 准确性评估
        accuracy_result = self.accuracy_assessor.assess(entity_data, entity_type)
        dimension_results['accuracy'] = accuracy_result['score']
        all_issues.extend(accuracy_result.get('issues', []))
        
        # 一致性评估
        consistency_result = self.consistency_assessor.assess(entity_data, entity_type)
        dimension_results['consistency'] = consistency_result['score']
        all_issues.extend(consistency_result.get('issues', []))
        
        # 唯一性评估
        uniqueness_result = self.uniqueness_assessor.assess(entity_data, entity_type, all_entities)
        dimension_results['uniqueness'] = uniqueness_result['score']
        all_issues.extend(uniqueness_result.get('issues', []))
        
        # 及时性评估
        timeliness_result = self.timeliness_assessor.assess(entity_data, entity_type)
        dimension_results['timeliness'] = timeliness_result['score']
        all_issues.extend(timeliness_result.get('issues', []))
        
        # 计算加权总体分数
        overall_score = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_results.items():
            if dimension in self.dimensions:
                weight = self.dimensions[dimension].weight
                overall_score += score * weight
                total_weight += weight
        
        overall_score = overall_score / total_weight if total_weight > 0 else 0.0
        
        # 确定等级
        grade = self._calculate_grade(overall_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(dimension_results, all_issues)
        
        # 创建评估结果
        assessment = QualityAssessment(
            assessment_id=assessment_id,
            entity_id=entity_data.get('entity_id', 'unknown'),
            entity_type=entity_type,
            dimensions=dimension_results,
            overall_score=overall_score,
            grade=grade,
            assessment_date=assessment_date,
            issues=all_issues,
            recommendations=recommendations
        )
        
        # 保存评估结果
        self._save_assessment(assessment)
        
        return assessment
    
    def assess_entities(self, entities: List[Dict[str, Any]], entity_type: str) -> List[QualityAssessment]:
        """批量评估实体数据质量"""
        assessments = []
        
        for entity in entities:
            assessment = self.assess_entity(entity, entity_type, entities)
            assessments.append(assessment)
        
        # 更新质量趋势
        self._update_quality_trends(entity_type, assessments)
        
        return assessments
    
    def get_quality_report(self, entity_type: str = None, 
                          start_date: datetime = None, 
                          end_date: datetime = None) -> Dict[str, Any]:
        """获取质量报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询
        query = '''
        SELECT entity_type, dimensions, overall_score, grade, assessment_date, COUNT(*) as count
        FROM quality_assessments
        WHERE 1=1
        '''
        params = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if start_date:
            query += " AND assessment_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND assessment_date <= ?"
            params.append(end_date.isoformat())
        
        query += " GROUP BY entity_type, grade ORDER BY entity_type, grade"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 处理结果
        report = {
            'entity_types': {},
            'overall': {
                'total_assessments': 0,
                'average_score': 0.0,
                'grade_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
            },
            'dimension_scores': {},
            'date_range': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            }
        }
        
        total_score = 0.0
        total_count = 0
        all_dimension_scores = defaultdict(list)
        
        for entity_type, dimensions, overall_score, grade, assessment_date, count in rows:
            # 实体类型统计
            if entity_type not in report['entity_types']:
                report['entity_types'][entity_type] = {
                    'total_assessments': 0,
                    'average_score': 0.0,
                    'grade_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                }
            
            report['entity_types'][entity_type]['total_assessments'] += count
            report['entity_types'][entity_type]['average_score'] += overall_score * count
            report['entity_types'][entity_type]['grade_distribution'][grade] += count
            
            # 总体统计
            report['overall']['total_assessments'] += count
            total_score += overall_score * count
            total_count += count
            report['overall']['grade_distribution'][grade] += count
            
            # 维度分数
            dimension_scores = json.loads(dimensions)
            for dim, score in dimension_scores.items():
                all_dimension_scores[dim].append(score)
        
        # 计算平均值
        report['overall']['average_score'] = total_score / total_count if total_count > 0 else 0.0
        
        for entity_type in report['entity_types']:
            type_data = report['entity_types'][entity_type]
            type_data['average_score'] /= type_data['total_assessments'] if type_data['total_assessments'] > 0 else 0.0
        
        # 计算维度平均分
        for dim, scores in all_dimension_scores.items():
            report['dimension_scores'][dim] = sum(scores) / len(scores) if scores else 0.0
        
        conn.close()
        return report
    
    def get_quality_trends(self, entity_type: str, dimension: str = None, 
                          days: int = 30) -> List[Dict[str, Any]]:
        """获取质量趋势"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 计算开始日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询
        query = '''
        SELECT assessment_date, average_score, entity_count
        FROM quality_trends
        WHERE entity_type = ? AND assessment_date >= ? AND assessment_date <= ?
        '''
        params = [entity_type, start_date.isoformat(), end_date.isoformat()]
        
        if dimension:
            query += " AND dimension = ?"
            params.append(dimension)
        
        query += " ORDER BY assessment_date"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 处理结果
        trends = []
        for assessment_date, average_score, entity_count in rows:
            trends.append({
                'date': assessment_date,
                'score': average_score,
                'entity_count': entity_count
            })
        
        conn.close()
        return trends
    
    def generate_improvement_plan(self, entity_type: str = None, 
                                  start_date: datetime = None, 
                                  end_date: datetime = None) -> Dict[str, Any]:
        """生成质量改进计划"""
        # 获取质量报告
        report = self.get_quality_report(entity_type, start_date, end_date)
        
        # 确定优先改进的维度
        if entity_type:
            dimension_scores = {}
            for dim in self.dimensions:
                # 获取该类型的特定维度分数
                # 这里简化处理，实际应该从查询中获取
                dimension_scores[dim] = report.get('dimension_scores', {}).get(dim, 0.0)
        else:
            dimension_scores = report.get('dimension_scores', {})
        
        # 按分数从低到高排序
        sorted_dimensions = sorted(
            [(dim, score) for dim, score in dimension_scores.items()],
            key=lambda x: x[1]
        )
        
        # 生成改进建议
        improvement_plan = {
            'entity_type': entity_type,
            'priority_dimensions': [],
            'recommendations': []
        }
        
        # 为每个维度生成具体的改进建议
        for dim, score in sorted_dimensions:
            if score < self.dimensions[dim].threshold:
                priority = 'high' if score < 0.7 else 'medium'
                improvement_plan['priority_dimensions'].append({
                    'dimension': dim,
                    'current_score': score,
                    'target_score': self.dimensions[dim].threshold,
                    'priority': priority,
                    'description': self.dimensions[dim].description
                })
                
                # 添加维度特定的改进建议
                if dim == 'completeness':
                    improvement_plan['recommendations'].extend([
                        "识别并补充缺失的关键字段",
                        "设置数据输入验证，确保关键字段不为空",
                        "优化数据收集流程，提高数据完整性"
                    ])
                elif dim == 'accuracy':
                    improvement_plan['recommendations'].extend([
                        "实施数据验证规则，确保数据格式正确",
                        "引入外部参考数据，验证数据准确性",
                        "建立数据修正流程，及时纠正错误数据"
                    ])
                elif dim == 'consistency':
                    improvement_plan['recommendations'].extend([
                        "统一数据标准和定义，确保一致性",
                        "实施跨字段验证规则",
                        "定期检查不同系统间的数据一致性"
                    ])
                elif dim == 'uniqueness':
                    improvement_plan['recommendations'].extend([
                        "实施重复数据检测机制",
                        "建立实体匹配和去重流程",
                        "设置唯一性约束，防止重复数据产生"
                    ])
                elif dim == 'timeliness':
                    improvement_plan['recommendations'].extend([
                        "建立定期数据更新机制",
                        "设置数据过期警报",
                        "优化数据同步流程，提高实时性"
                    ])
        
        return improvement_plan
    
    def visualize_quality_report(self, entity_type: str = None, save_path: str = None):
        """可视化质量报告"""
        # 获取质量报告
        report = self.get_quality_report(entity_type)
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"Data Quality Report{' - ' + entity_type if entity_type else ''}", fontsize=16)
        
        # 1. 等级分布饼图
        if entity_type:
            grades = report['entity_types'].get(entity_type, {}).get('grade_distribution', {})
        else:
            grades = report['overall']['grade_distribution']
        
        labels = list(grades.keys())
        sizes = list(grades.values())
        colors = ['green', 'lightgreen', 'yellow', 'orange', 'red']
        
        axes[0, 0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Grade Distribution')
        
        # 2. 维度分数条形图
        dimensions = list(report['dimension_scores'].keys())
        scores = list(report['dimension_scores'].values())
        thresholds = [self.dimensions[dim].threshold for dim in dimensions]
        
        x = np.arange(len(dimensions))
        width = 0.35
        
        axes[0, 1].bar(x, scores, width, label='Current Score')
        axes[0, 1].bar(x + width, thresholds, width, label='Threshold')
        axes[0, 1].set_title('Dimension Scores')
        axes[0, 1].set_xticks(x + width / 2)
        axes[0, 1].set_xticklabels(dimensions)
        axes[0, 1].legend()
        
        # 3. 实体类型统计（如果未指定实体类型）
        if not entity_type:
            entity_types = list(report['entity_types'].keys())
            type_scores = [report['entity_types'][et]['average_score'] for et in entity_types]
            
            axes[1, 0].bar(entity_types, type_scores)
            axes[1, 0].set_title('Average Score by Entity Type')
            axes[1, 0].set_ylabel('Score')
            plt.setp(axes[1, 0].get_xticklabels(), rotation=45, ha='right')
        else:
            # 如果指定了实体类型，显示最近的质量趋势
            trends = self.get_quality_trends(entity_type, days=30)
            if trends:
                dates = [t['date'] for t in trends]
                scores = [t['score'] for t in trends]
                
                axes[1, 0].plot(dates, scores)
                axes[1, 0].set_title('Quality Trend (Last 30 Days)')
                axes[1, 0].set_ylabel('Score')
                plt.setp(axes[1, 0].get_xticklabels(), rotation=45, ha='right')
        
        # 4. 问题严重程度分布
        # 这里简化处理，实际应该从查询中获取
        severity_counts = {'low': 20, 'medium': 30, 'high': 15, 'critical': 5}
        
        severities = list(severity_counts.keys())
        counts = list(severity_counts.values())
        
        axes[1, 1].bar(severities, counts, color=['green', 'yellow', 'orange', 'red'])
        axes[1, 1].set_title('Issue Severity Distribution')
        axes[1, 1].set_ylabel('Count')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存或显示图表
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Quality report visualization saved to {save_path}")
        else:
            plt.show()
    
    def _calculate_grade(self, score: float) -> str:
        """计算质量等级"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, dimension_results: Dict[str, float], 
                                issues: List[Dict[str, Any]]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于维度分数生成建议
        for dimension, score in dimension_results.items():
            if score < self.dimensions[dimension].threshold:
                if dimension == 'completeness':
                    recommendations.append("增加数据完整性，补充缺失的关键字段")
                elif dimension == 'accuracy':
                    recommendations.append("提高数据准确性，验证和修正错误数据")
                elif dimension == 'consistency':
                    recommendations.append("确保数据一致性，统一标准和定义")
                elif dimension == 'uniqueness':
                    recommendations.append("消除重复数据，确保实体唯一性")
                elif dimension == 'timeliness':
                    recommendations.append("更新数据，确保信息的及时性")
        
        # 基于问题类型生成建议
        issue_types = [issue.get('type') for issue in issues]
        issue_counts = Counter(issue_types)
        
        for issue_type, count in issue_counts.most_common(3):
            if issue_type == 'missing_required_fields':
                recommendations.append("优先处理缺失的必填字段")
            elif issue_type == 'field_accuracy':
                recommendations.append("实施字段验证规则，提高数据准确性")
            elif issue_type == 'field_consistency':
                recommendations.append("检查并修复不一致的字段值")
            elif issue_type == 'duplicate_unique_field':
                recommendations.append("识别并合并重复的数据记录")
            elif issue_type == 'field_timeliness':
                recommendations.append("更新过时的数据，保持信息新鲜度")
        
        return recommendations
    
    def _save_assessment(self, assessment: QualityAssessment):
        """保存评估结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO quality_assessments 
        (assessment_id, entity_id, entity_type, dimensions, overall_score, 
         grade, assessment_date, issues, recommendations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assessment.assessment_id,
            assessment.entity_id,
            assessment.entity_type,
            json.dumps(assessment.dimensions),
            assessment.overall_score,
            assessment.grade,
            assessment.assessment_date.isoformat(),
            json.dumps(assessment.issues),
            json.dumps(assessment.recommendations)
        ))
        
        conn.commit()
        conn.close()
    
    def _update_quality_trends(self, entity_type: str, assessments: List[QualityAssessment]):
        """更新质量趋势"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 计算各维度的平均分
        dimension_scores = defaultdict(list)
        for assessment in assessments:
            for dimension, score in assessment.dimensions.items():
                dimension_scores[dimension].append(score)
        
        # 保存趋势数据
        assessment_date = datetime.now().isoformat()
        entity_count = len(assessments)
        
        for dimension, scores in dimension_scores.items():
            average_score = sum(scores) / len(scores) if scores else 0.0
            
            cursor.execute('''
            INSERT INTO quality_trends 
            (trend_id, entity_type, dimension, average_score, assessment_date, entity_count)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                entity_type,
                dimension,
                average_score,
                assessment_date,
                entity_count
            ))
        
        conn.commit()
        conn.close()


def generate_sample_entities(entity_type: str, count: int = 20) -> List[Dict[str, Any]]:
    """生成示例实体"""
    import random
    
    if entity_type == 'customer':
        first_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴']
        last_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军']
        domains = ['example.com', 'test.com', 'demo.com', 'sample.com']
        countries = ['China', 'USA', 'UK', 'Japan', 'Germany']
        
        entities = []
        for i in range(count):
            # 创建一些有质量问题的实体
            name = f"{random.choice(first_names)}{random.choice(last_names)}"
            
            # 10%的概率邮箱为空
            if random.random() < 0.1:
                email = ''
            # 10%的概率邮箱格式错误
            elif random.random() < 0.1:
                email = f"{name.lower()}@invalid-email"
            else:
                email = f"{name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"
            
            phone = f"+86-13{random.randint(100000000, 999999999)}"
            
            # 20%的概率地址为空
            if random.random() < 0.2:
                address = ''
            else:
                address = f"{random.choice(['北京市', '上海市', '广州市', '深圳市'])}某区某街道{random.randint(1, 100)}号"
            
            # 5%的国家不在列表中
            if random.random() < 0.05:
                country = 'InvalidCountry'
            else:
                country = random.choice(countries)
            
            # 随机生成最后更新日期
            days_ago = random.randint(0, 365)
            last_update_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # 10%的概率没有最后订单日期
            if random.random() < 0.1:
                last_order_date = None
            else:
                order_days_ago = random.randint(1, 90)
                last_order_date = (datetime.now() - timedelta(days=order_days_ago)).strftime('%Y-%m-%d')
            
            entity = {
                'entity_id': f"cust-{i+1:03d}",
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'country': country,
                'last_update_date': last_update_date,
                'last_order_date': last_order_date
            }
            entities.append(entity)
        
        return entities
    
    elif entity_type == 'product':
        products = ['智能手机', '笔记本电脑', '平板电脑', '智能手表', '蓝牙耳机']
        brands = ['品牌A', '品牌B', '品牌C', '品牌D']
        
        entities = []
        for i in range(count):
            name = f"{random.choice(brands)} {random.choice(products)}"
            
            # 10%的概率SKU为空
            if random.random() < 0.1:
                sku = ''
            # 10%的概率SKU格式错误
            elif random.random() < 0.1:
                sku = f"invalid-{random.randint(1000, 9999)}"
            else:
                sku = f"{name[0].upper()}{random.randint(1000, 9999)}"
            
            # 5%的概率价格为负数
            if random.random() < 0.05:
                price = -random.uniform(10.0, 1000.0)
            else:
                price = round(random.uniform(100.0, 5000.0), 2)
            
            # 随机生成最后更新日期
            days_ago = random.randint(0, 365)
            last_update_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            entity = {
                'entity_id': f"prod-{i+1:03d}",
                'name': name,
                'sku': sku,
                'price': price,
                'category': random.choice(['电子产品', '数码配件', '智能设备']),
                'last_update_date': last_update_date
            }
            entities.append(entity)
        
        return entities
    
    else:
        # 默认生成通用实体
        entities = []
        for i in range(count):
            entity = {
                'entity_id': f"entity-{i+1:03d}",
                'name': f"实体 {i+1}",
                'value': random.randint(1, 100)
            }
            entities.append(entity)
        
        return entities


def demonstrate_quality_assessment():
    """演示质量评估能力"""
    # 创建质量评估工具
    quality_tool = DataQualityAssessmentTool()
    
    print("\n=== 数据质量评估工具演示 ===")
    
    # 1. 生成示例客户实体
    print("\n1. 生成示例客户实体:")
    customers = generate_sample_entities('customer', 15)
    for customer in customers[:5]:  # 只显示前5个
        print(f"  {customer['entity_id']}: {customer['name']}, {customer['email']}, {customer['country']}")
    
    # 2. 评估单个实体
    print("\n2. 评估单个实体质量:")
    assessment = quality_tool.assess_entity(customers[0], 'customer', customers)
    print(f"  实体ID: {assessment.entity_id}")
    print(f"  总体分数: {assessment.overall_score:.2f}")
    print(f"  等级: {assessment.grade}")
    print(f"  维度分数: {assessment.dimensions}")
    print(f"  问题数量: {len(assessment.issues)}")
    print(f"  建议数量: {len(assessment.recommendations)}")
    
    # 3. 批量评估实体
    print("\n3. 批量评估实体质量:")
    assessments = quality_tool.assess_entities(customers, 'customer')
    
    # 统计等级分布
    grade_counts = {}
    for assessment in assessments:
        grade = assessment.grade
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    print(f"  评估了 {len(assessments)} 个客户实体")
    print(f"  等级分布: {grade_counts}")
    
    # 计算平均分
    avg_score = sum(a.overall_score for a in assessments) / len(assessments)
    print(f"  平均分数: {avg_score:.2f}")
    
    # 4. 获取质量报告
    print("\n4. 获取质量报告:")
    report = quality_tool.get_quality_report('customer')
    
    print(f"  总评估数: {report['overall']['total_assessments']}")
    print(f"  平均分数: {report['overall']['average_score']:.2f}")
    print(f"  等级分布: {report['overall']['grade_distribution']}")
    print(f"  维度分数: {report['dimension_scores']}")
    
    # 5. 获取质量趋势
    print("\n5. 获取质量趋势:")
    trends = quality_tool.get_quality_trends('customer', days=30)
    if trends:
        print(f"  最近30天有 {len(trends)} 条趋势记录")
        print(f"  最新分数: {trends[-1]['score']:.2f}")
        print(f"  趋势变化: {trends[-1]['score'] - trends[0]['score']:.2f}")
    else:
        print("  无趋势数据")
    
    # 6. 生成改进计划
    print("\n6. 生成改进计划:")
    improvement_plan = quality_tool.generate_improvement_plan('customer')
    
    print(f"  优先改进维度: {[d['dimension'] for d in improvement_plan['priority_dimensions']]}")
    print("  改进建议:")
    for i, recommendation in enumerate(improvement_plan['recommendations'][:5]):
        print(f"    {i+1}. {recommendation}")
    
    # 7. 生成示例产品实体并评估
    print("\n7. 评估产品质量:")
    products = generate_sample_entities('product', 10)
    product_assessments = quality_tool.assess_entities(products, 'product')
    
    product_avg_score = sum(a.overall_score for a in product_assessments) / len(product_assessments)
    print(f"  评估了 {len(product_assessments)} 个产品实体")
    print(f"  产品平均分数: {product_avg_score:.2f}")
    
    # 8. 可视化质量报告
    print("\n8. 生成质量报告可视化:")
    try:
        output_path = "quality_report.png"
        quality_tool.visualize_quality_report('customer', save_path=output_path)
        print(f"  质量报告图表已保存到 {output_path}")
    except Exception as e:
        print(f"  生成图表失败: {e}")
        print("  可能缺少matplotlib库，请安装: pip install matplotlib seaborn")


if __name__ == "__main__":
    demonstrate_quality_assessment()