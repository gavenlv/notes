#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证与质量规则示例代码（简化版）
本代码展示了如何实现不同类型的数据验证规则以及构建数据验证框架
去除了matplotlib依赖，便于在无图形环境运行
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple


class DataQualityRule:
    """数据质量规则基类"""
    
    def __init__(self, name: str, description: str, severity: str = 'error'):
        """
        初始化数据质量规则
        
        Args:
            name: 规则名称
            description: 规则描述
            severity: 严重程度 ('error', 'warning')
        """
        self.name = name
        self.description = description
        self.severity = severity
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证数据
        
        Args:
            data: 待验证的数据字典
            
        Returns:
            (是否通过验证, 验证消息)
        """
        raise NotImplementedError


class FormatRule(DataQualityRule):
    """格式规则"""
    
    def __init__(self, name: str, description: str, field: str, pattern: str, severity: str = 'error'):
        """
        初始化格式规则
        
        Args:
            name: 规则名称
            description: 规则描述
            field: 字段名
            pattern: 正则表达式模式
            severity: 严重程度
        """
        super().__init__(name, description, severity)
        self.field = field
        self.pattern = re.compile(pattern)
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证字段格式"""
        if self.field not in data:
            return False, f"字段 {self.field} 不存在"
        
        value = str(data[self.field]) if data[self.field] is not None else ""
        if self.pattern.match(value):
            return True, "验证通过"
        else:
            return False, f"字段 {self.field} 格式不正确: {value}"


class RangeRule(DataQualityRule):
    """范围规则"""
    
    def __init__(self, name: str, description: str, field: str, min_value: float, 
                 max_value: float, severity: str = 'error'):
        """
        初始化范围规则
        
        Args:
            name: 规则名称
            description: 规则描述
            field: 字段名
            min_value: 最小值
            max_value: 最大值
            severity: 严重程度
        """
        super().__init__(name, description, severity)
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证字段范围"""
        if self.field not in data:
            return False, f"字段 {self.field} 不存在"
        
        try:
            value = float(data[self.field])
            if self.min_value <= value <= self.max_value:
                return True, "验证通过"
            else:
                return False, f"字段 {self.field} 值 {value} 超出范围 [{self.min_value}, {self.max_value}]"
        except (ValueError, TypeError):
            return False, f"字段 {self.field} 值 {data[self.field]} 无法转换为数值"


class RequiredRule(DataQualityRule):
    """必填规则"""
    
    def __init__(self, name: str, description: str, field: str, severity: str = 'error'):
        """
        初始化必填规则
        
        Args:
            name: 规则名称
            description: 规则描述
            field: 字段名
            severity: 严重程度
        """
        super().__init__(name, description, severity)
        self.field = field
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证字段是否必填"""
        if self.field not in data:
            return False, f"字段 {self.field} 不存在"
        
        value = data[self.field]
        if pd.isna(value) or value == '' or value is None:
            return False, f"字段 {self.field} 不能为空"
        else:
            return True, "验证通过"


class RuleVersionManager:
    """规则版本管理器"""
    
    def __init__(self):
        """初始化规则版本管理器"""
        self.rules = {}
        self.versions = {}
    
    def add_rule(self, rule: DataQualityRule, version: str = "1.0"):
        """
        添加规则
        
        Args:
            rule: 数据质量规则对象
            version: 规则版本号
        """
        rule_key = f"{rule.name}_{version}"
        self.rules[rule_key] = rule
        if rule.name not in self.versions:
            self.versions[rule.name] = []
        self.versions[rule.name].append(version)
    
    def get_rule(self, rule_name: str, version: str = None) -> DataQualityRule:
        """
        获取规则
        
        Args:
            rule_name: 规则名称
            version: 规则版本号，如果为None则返回最新版本
            
        Returns:
            数据质量规则对象
        """
        if version is None:
            # 获取最新版本
            if rule_name in self.versions:
                latest_version = sorted(self.versions[rule_name], reverse=True)[0]
                rule_key = f"{rule_name}_{latest_version}"
                return self.rules.get(rule_key)
        else:
            rule_key = f"{rule_name}_{version}"
            return self.rules.get(rule_key)
        
        return None


class DataQualityValidator:
    """数据质量验证器"""
    
    def __init__(self):
        """初始化数据质量验证器"""
        self.rules = []
        self.validation_results = []
        self.validation_history = []
    
    def add_rule(self, rule: DataQualityRule):
        """
        添加验证规则
        
        Args:
            rule: 数据质量规则对象
        """
        self.rules.append(rule)
    
    def validate_record(self, record: Dict[str, Any]) -> List[Tuple[bool, str, DataQualityRule]]:
        """
        验证单条记录
        
        Args:
            record: 待验证的记录字典
            
        Returns:
            验证结果列表 [(是否通过, 消息, 规则对象)]
        """
        results = []
        for rule in self.rules:
            is_valid, message = rule.validate(record)
            results.append((is_valid, message, rule))
        return results
    
    def validate_dataset(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证数据集
        
        Args:
            dataset: 待验证的数据集
            
        Returns:
            验证结果统计
        """
        total_records = len(dataset)
        validation_stats = {
            'total_records': total_records,
            'passed_records': 0,
            'failed_records': 0,
            'rule_violations': {},
            'details': []
        }
        
        for i, record in enumerate(dataset):
            record_results = self.validate_record(record)
            record_passed = True
            
            for is_valid, message, rule in record_results:
                if not is_valid:
                    record_passed = False
                    # 记录违规信息
                    if rule.name not in validation_stats['rule_violations']:
                        validation_stats['rule_violations'][rule.name] = {
                            'count': 0,
                            'severity': rule.severity,
                            'description': rule.description
                        }
                    validation_stats['rule_violations'][rule.name]['count'] += 1
            
            if record_passed:
                validation_stats['passed_records'] += 1
            else:
                validation_stats['failed_records'] += 1
                validation_stats['details'].append({
                    'record_id': i,
                    'record': record,
                    'violations': [r for r in record_results if not r[0]]
                })
        
        return validation_stats


class BusinessRuleEngine:
    """业务规则引擎"""
    
    def __init__(self):
        """初始化业务规则引擎"""
        self.rules = []
    
    def add_business_rule(self, rule_func, rule_name: str, description: str):
        """
        添加业务规则
        
        Args:
            rule_func: 规则函数
            rule_name: 规则名称
            description: 规则描述
        """
        self.rules.append({
            'function': rule_func,
            'name': rule_name,
            'description': description
        })
    
    def apply_rules(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        应用业务规则
        
        Args:
            data: 待验证的数据
            
        Returns:
            规则应用结果
        """
        results = {
            'total_records': len(data),
            'rule_results': {}
        }
        
        for rule in self.rules:
            try:
                # 应用规则函数
                violations = rule['function'](data)
                results['rule_results'][rule['name']] = {
                    'description': rule['description'],
                    'violation_count': len(violations),
                    'violations': violations.head(10).to_dict('records') if len(violations) > 0 else []
                }
            except Exception as e:
                results['rule_results'][rule['name']] = {
                    'description': rule['description'],
                    'error': str(e)
                }
        
        return results


def create_sample_data() -> pd.DataFrame:
    """创建示例数据"""
    data = {
        'customer_id': range(1, 101),
        'name': [f'Customer_{i}' for i in range(1, 101)],
        'email': [f'customer{i}@email.com' if i % 10 != 0 else f'invalid_email_{i}' for i in range(1, 101)],
        'age': [25 + (i % 50) for i in range(1, 101)],
        'salary': [30000 + (i * 1000) for i in range(1, 101)],
        'phone': [f'1380013800{i % 10}' for i in range(1, 101)],
        'registration_date': [datetime(2023, 1, 1).strftime('%Y-%m-%d') for _ in range(1, 101)]
    }
    
    # 引入一些数据质量问题
    data['email'][5] = 'invalid.email'  # 格式错误
    data['email'][15] = ''  # 空值
    data['age'][25] = -5  # 负数
    data['age'][35] = 150  # 超出合理范围
    data['salary'][45] = 1000000  # 异常高值
    
    return pd.DataFrame(data)


def email_format_rule(data: pd.DataFrame) -> pd.DataFrame:
    """邮箱格式检查规则"""
    invalid_emails = data[~data['email'].str.contains(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', na=False)]
    return invalid_emails


def age_range_rule(data: pd.DataFrame) -> pd.DataFrame:
    """年龄范围检查规则"""
    invalid_ages = data[(data['age'] < 0) | (data['age'] > 120)]
    return invalid_ages


def salary_outlier_rule(data: pd.DataFrame) -> pd.DataFrame:
    """薪资异常值检查规则"""
    Q1 = data['salary'].quantile(0.25)
    Q3 = data['salary'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = data[(data['salary'] < lower_bound) | (data['salary'] > upper_bound)]
    return outliers


def main():
    """主函数"""
    print("=== 第5章：数据验证与质量规则 代码示例 ===\n")
    
    # 1. 基础规则验证示例
    print("1. 基础规则验证示例")
    print("-" * 40)
    
    # 创建验证器
    validator = DataQualityValidator()
    
    # 添加规则
    validator.add_rule(RequiredRule("姓名必填", "客户姓名不能为空", "name"))
    validator.add_rule(FormatRule("邮箱格式", "邮箱格式必须正确", "email", 
                               r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'))
    validator.add_rule(RangeRule("年龄范围", "年龄必须在0-120之间", "age", 0, 120))
    
    # 创建测试数据
    test_records = [
        {"name": "张三", "email": "zhangsan@example.com", "age": 25},
        {"name": "", "email": "lisi@example.com", "age": 30},  # 姓名为空
        {"name": "王五", "email": "invalid-email", "age": 35},  # 邮箱格式错误
        {"name": "赵六", "email": "zhaoliu@example.com", "age": -5},  # 年龄为负数
    ]
    
    # 验证数据
    for i, record in enumerate(test_records):
        print(f"记录 {i+1}: {record}")
        results = validator.validate_record(record)
        for is_valid, message, rule in results:
            status = "✓" if is_valid else "✗"
            print(f"  {status} {rule.name}: {message}")
        print()
    
    # 2. 数据集验证示例
    print("2. 数据集验证示例")
    print("-" * 40)
    
    # 创建更大的测试数据集
    dataset = []
    for i in range(20):
        record = {
            "name": f"用户{i}" if i % 5 != 0 else "",  # 每5个记录有一个空姓名
            "email": f"user{i}@example.com" if i % 7 != 0 else f"invalid.email.{i}",  # 每7个记录有一个无效邮箱
            "age": 20 + (i % 60) if i % 10 != 0 else -5  # 每10个记录有一个负年龄
        }
        dataset.append(record)
    
    # 验证数据集
    stats = validator.validate_dataset(dataset)
    print(f"数据集验证结果:")
    print(f"  总记录数: {stats['total_records']}")
    print(f"  通过记录数: {stats['passed_records']}")
    print(f"  失败记录数: {stats['failed_records']}")
    print(f"  违规规则:")
    for rule_name, violation_info in stats['rule_violations'].items():
        print(f"    {rule_name}: {violation_info['count']} 次违规")
    
    print("\n" + "=" * 60)
    
    # 3. 业务规则引擎示例
    print("3. 业务规则引擎示例")
    print("-" * 40)
    
    # 创建示例数据
    sample_data = create_sample_data()
    print(f"创建示例数据集，共 {len(sample_data)} 条记录")
    
    # 创建业务规则引擎
    rule_engine = BusinessRuleEngine()
    
    # 添加业务规则
    rule_engine.add_business_rule(email_format_rule, "邮箱格式检查", "检查邮箱格式是否正确")
    rule_engine.add_business_rule(age_range_rule, "年龄范围检查", "检查年龄是否在合理范围内")
    rule_engine.add_business_rule(salary_outlier_rule, "薪资异常检查", "检查薪资是否存在异常值")
    
    # 应用规则
    results = rule_engine.apply_rules(sample_data)
    
    print(f"\n业务规则检查结果:")
    print(f"  总记录数: {results['total_records']}")
    for rule_name, rule_result in results['rule_results'].items():
        if 'error' in rule_result:
            print(f"  {rule_name}: 执行出错 - {rule_result['error']}")
        else:
            print(f"  {rule_name}: 发现 {rule_result['violation_count']} 条违规记录")
            if rule_result['violation_count'] > 0:
                print(f"    前10条违规记录: {len(rule_result['violations'])} 条")
    
    print("\n" + "=" * 60)
    
    # 4. 规则版本管理示例
    print("4. 规则版本管理示例")
    print("-" * 40)
    
    # 创建规则版本管理器
    version_manager = RuleVersionManager()
    
    # 添加不同版本的规则
    version_manager.add_rule(
        RangeRule("年龄范围检查", "年龄必须在0-120之间", "age", 0, 120), 
        "1.0"
    )
    
    version_manager.add_rule(
        RangeRule("年龄范围检查", "年龄必须在0-150之间", "age", 0, 150), 
        "2.0"
    )
    
    # 获取规则
    rule_v1 = version_manager.get_rule("年龄范围检查", "1.0")
    rule_v2 = version_manager.get_rule("年龄范围检查", "2.0")
    rule_latest = version_manager.get_rule("年龄范围检查")
    
    print(f"规则版本信息:")
    print(f"  版本1.0: {rule_v1.description} (范围: {rule_v1.min_value}-{rule_v1.max_value})")
    print(f"  版本2.0: {rule_v2.description} (范围: {rule_v2.min_value}-{rule_v2.max_value})")
    print(f"  最新版本: {rule_latest.description} (范围: {rule_latest.min_value}-{rule_latest.max_value})")
    
    print("\n" + "=" * 60)
    print("数据验证与质量规则演示完成!")


if __name__ == "__main__":
    main()