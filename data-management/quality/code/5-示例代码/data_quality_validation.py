#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证与质量规则示例代码
本代码展示了如何实现不同类型的数据验证规则以及构建数据验证框架
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns


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
    
    def load_rules_from_config(self, config_file: str):
        """
        从配置文件加载规则
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 未找到")
            return
        except json.JSONDecodeError:
            print(f"配置文件 {config_file} 格式错误")
            return
        
        for rule_config in config.get('rules', []):
            rule_type = rule_config.get('type')
            if rule_type == 'format':
                rule = FormatRule(
                    name=rule_config['name'],
                    description=rule_config['description'],
                    field=rule_config['field'],
                    pattern=rule_config['pattern'],
                    severity=rule_config.get('severity', 'error')
                )
            elif rule_type == 'range':
                rule = RangeRule(
                    name=rule_config['name'],
                    description=rule_config['description'],
                    field=rule_config['field'],
                    min_value=rule_config['min_value'],
                    max_value=rule_config['max_value'],
                    severity=rule_config.get('severity', 'error')
                )
            elif rule_type == 'required':
                rule = RequiredRule(
                    name=rule_config['name'],
                    description=rule_config['description'],
                    field=rule_config['field'],
                    severity=rule_config.get('severity', 'error')
                )
            else:
                print(f"未知的规则类型: {rule_type}")
                continue
            
            self.add_rule(rule)
    
    def validate_record(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        验证单条记录
        
        Args:
            record: 待验证的记录字典
            
        Returns:
            验证结果列表
        """
        record_results = []
        for rule in self.rules:
            is_valid, message = rule.validate(record)
            record_results.append({
                'rule_name': rule.name,
                'is_valid': is_valid,
                'message': message,
                'severity': rule.severity
            })
        return record_results
    
    def validate_dataframe(self, df: pd.DataFrame, dataset_name: str = "unknown") -> Dict[str, Any]:
        """
        验证DataFrame
        
        Args:
            df: 待验证的DataFrame
            dataset_name: 数据集名称
            
        Returns:
            验证结果字典
        """
        print(f"开始验证数据集: {dataset_name}")
        print(f"数据集大小: {df.shape}")
        
        validation_run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_results = {
            'run_id': validation_run_id,
            'dataset_name': dataset_name,
            'timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'validation_results': []
        }
        
        # 统计信息
        total_violations = 0
        error_violations = 0
        warning_violations = 0
        
        # 逐条记录验证
        for idx, record in df.iterrows():
            record_dict = record.to_dict()
            record_violations = []
            
            for rule in self.rules:
                is_valid, message = rule.validate(record_dict)
                if not is_valid:
                    violation = {
                        'record_id': idx,
                        'rule_name': rule.name,
                        'field': getattr(rule, 'field', 'unknown'),
                        'severity': rule.severity,
                        'message': message,
                        'record_data': {k: str(v) for k, v in record_dict.items()}
                    }
                    record_violations.append(violation)
                    total_violations += 1
                    if rule.severity == 'error':
                        error_violations += 1
                    elif rule.severity == 'warning':
                        warning_violations += 1
            
            if record_violations:
                run_results['validation_results'].extend(record_violations)
        
        # 添加统计信息
        run_results['summary'] = {
            'total_violations': total_violations,
            'error_violations': error_violations,
            'warning_violations': warning_violations,
            'error_rate': error_violations / len(df) if len(df) > 0 else 0,
            'warning_rate': warning_violations / len(df) if len(df) > 0 else 0
        }
        
        self.validation_results = run_results
        self.validation_history.append(run_results)
        
        print(f"验证完成:")
        print(f"  总违规数: {total_violations}")
        print(f"  错误级违规: {error_violations}")
        print(f"  警告级违规: {warning_violations}")
        
        return run_results
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        生成验证报告
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            验证报告字典
        """
        if not self.validation_results:
            print("没有验证结果可报告")
            return {}
        
        report = {
            'validation_run': self.validation_results,
            'detailed_violations': self.validation_results['validation_results']
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"验证报告已保存到: {output_file}")
        
        return report
    
    def get_violations_by_severity(self, severity: str = 'error') -> List[Dict[str, Any]]:
        """
        按严重程度获取违规记录
        
        Args:
            severity: 严重程度 ('error', 'warning')
            
        Returns:
            违规记录列表
        """
        if not self.validation_results:
            return []
        
        violations = [
            v for v in self.validation_results['validation_results']
            if v['severity'] == severity
        ]
        return violations
    
    def get_violations_by_rule(self, rule_name: str) -> List[Dict[str, Any]]:
        """
        按规则名称获取违规记录
        
        Args:
            rule_name: 规则名称
            
        Returns:
            违规记录列表
        """
        if not self.validation_results:
            return []
        
        violations = [
            v for v in self.validation_results['validation_results']
            if v['rule_name'] == rule_name
        ]
        return violations


def create_customer_data() -> pd.DataFrame:
    """
    创建客户数据示例
    
    Returns:
        包含客户数据的DataFrame
    """
    np.random.seed(42)
    
    # 创建基础数据
    n_customers = 1000
    customer_data = {
        'customer_id': range(10001, 10001 + n_customers),
        'name': [f'Customer_{i}' for i in range(1, n_customers + 1)],
        'email': [f'customer{i}@example.com' for i in range(1, n_customers + 1)],
        'phone': [f'138{np.random.randint(10000000, 99999999)}' for _ in range(n_customers)],
        'age': np.random.randint(18, 80, n_customers),
        'registration_date': pd.date_range('2020-01-01', periods=n_customers, freq='D'),
        'annual_income': np.random.normal(50000, 15000, n_customers),
        'credit_score': np.random.randint(300, 850, n_customers)
    }
    
    df = pd.DataFrame(customer_data)
    
    # 添加一些数据质量问题
    # 1. 无效邮箱
    invalid_email_indices = np.random.choice(n_customers, 20, replace=False)
    df.loc[invalid_email_indices[:10], 'email'] = 'invalid-email'
    df.loc[invalid_email_indices[10:], 'email'] = '@invalid.com'
    
    # 2. 无效电话号码
    invalid_phone_indices = np.random.choice(n_customers, 15, replace=False)
    df.loc[invalid_phone_indices[:5], 'phone'] = '12345'
    df.loc[invalid_phone_indices[5:], 'phone'] = '138123456789'
    
    # 3. 年龄异常
    age_outlier_indices = np.random.choice(n_customers, 10, replace=False)
    df.loc[age_outlier_indices[:5], 'age'] = np.random.randint(100, 150, 5)
    df.loc[age_outlier_indices[5:], 'age'] = np.random.randint(-10, 0, 5)
    
    # 4. 收入异常
    income_outlier_indices = np.random.choice(n_customers, 8, replace=False)
    df.loc[income_outlier_indices[:4], 'annual_income'] = np.random.uniform(1000000, 2000000, 4)
    df.loc[income_outlier_indices[4:], 'annual_income'] = np.random.uniform(-50000, 0, 4)
    
    # 5. 信用分数异常
    credit_outlier_indices = np.random.choice(n_customers, 12, replace=False)
    df.loc[credit_outlier_indices[:6], 'credit_score'] = np.random.randint(900, 1000, 6)
    df.loc[credit_outlier_indices[6:], 'credit_score'] = np.random.randint(-100, 0, 6)
    
    # 6. 缺失值
    missing_indices = np.random.choice(n_customers, 25, replace=False)
    df.loc[missing_indices[:10], 'email'] = None
    df.loc[missing_indices[10:20], 'phone'] = None
    df.loc[missing_indices[20:], 'age'] = None
    
    return df


def create_rules_config():
    """创建规则配置文件"""
    rules_config = {
        "rules": [
            {
                "name": "customer_email_format",
                "description": "客户邮箱格式验证",
                "type": "format",
                "field": "email",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "severity": "error"
            },
            {
                "name": "customer_phone_format",
                "description": "客户电话号码格式验证",
                "type": "format",
                "field": "phone",
                "pattern": "^1[3-9]\\d{9}$",
                "severity": "error"
            },
            {
                "name": "customer_age_range",
                "description": "客户年龄范围验证",
                "type": "range",
                "field": "age",
                "min_value": 0,
                "max_value": 150,
                "severity": "error"
            },
            {
                "name": "customer_income_range",
                "description": "客户年收入范围验证",
                "type": "range",
                "field": "annual_income",
                "min_value": 0,
                "max_value": 1000000,
                "severity": "warning"
            },
            {
                "name": "customer_credit_score_range",
                "description": "客户信用分数范围验证",
                "type": "range",
                "field": "credit_score",
                "min_value": 300,
                "max_value": 850,
                "severity": "error"
            },
            {
                "name": "customer_email_required",
                "description": "客户邮箱必填验证",
                "type": "required",
                "field": "email",
                "severity": "error"
            },
            {
                "name": "customer_phone_required",
                "description": "客户电话必填验证",
                "type": "required",
                "field": "phone",
                "severity": "warning"
            }
        ]
    }
    
    # 保存规则配置
    with open('customer_data_quality_rules.json', 'w', encoding='utf-8') as f:
        json.dump(rules_config, f, ensure_ascii=False, indent=2)
    print("规则配置文件已创建: customer_data_quality_rules.json")


def run_customer_data_validation():
    """执行客户数据验证"""
    print("=== 客户数据质量验证 ===\n")
    
    # 创建客户数据
    customer_df = create_customer_data()
    print("客户数据示例:")
    print(customer_df.head(10))
    print(f"\n数据形状: {customer_df.shape}\n")
    
    # 创建规则配置文件
    create_rules_config()
    
    # 创建验证器
    validator = DataQualityValidator()
    validator.load_rules_from_config('customer_data_quality_rules.json')
    
    # 执行验证
    results = validator.validate_dataframe(customer_df, "customer_data")
    
    # 生成报告
    report = validator.generate_report("customer_data_quality_report.json")
    
    # 分析结果
    print("\n=== 验证结果分析 ===")
    
    # 按严重程度统计
    error_violations = validator.get_violations_by_severity('error')
    warning_violations = validator.get_violations_by_severity('warning')
    
    print(f"错误级违规: {len(error_violations)} 条")
    print(f"警告级违规: {len(warning_violations)} 条")
    
    # 按规则统计
    print("\n按规则统计违规情况:")
    rule_stats = {}
    for violation in results['validation_results']:
        rule_name = violation['rule_name']
        if rule_name not in rule_stats:
            rule_stats[rule_name] = {'error': 0, 'warning': 0}
        rule_stats[rule_name][violation['severity']] += 1
    
    for rule_name, stats in rule_stats.items():
        print(f"  {rule_name}: 错误 {stats['error']}, 警告 {stats['warning']}")
    
    # 显示部分违规示例
    print("\n部分违规示例:")
    for i, violation in enumerate(error_violations[:5]):
        print(f"  {i+1}. 规则: {violation['rule_name']}")
        print(f"     消息: {violation['message']}")
        print(f"     记录ID: {violation['record_id']}")
        # 只显示前5个字段以避免输出过长
        record_data_sample = dict(list(violation['record_data'].items())[:5])
        print(f"     数据示例: {record_data_sample}")
        print()
    
    return validator, results


def visualize_validation_results(validator: DataQualityValidator):
    """
    可视化验证结果
    
    Args:
        validator: 数据质量验证器对象
    """
    if not validator.validation_results:
        print("没有验证结果可可视化")
        return
    
    results = validator.validation_results
    violations = results['validation_results']
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('数据质量验证结果分析', fontsize=16)
    
    # 1. 严重程度分布
    severity_counts = {'error': results['summary']['error_violations'],
                      'warning': results['summary']['warning_violations']}
    axes[0, 0].pie(severity_counts.values(), labels=severity_counts.keys(), autopct='%1.1f%%')
    axes[0, 0].set_title('违规严重程度分布')
    
    # 2. 规则违规数量
    rule_violations = {}
    for violation in violations:
        rule_name = violation['rule_name']
        rule_violations[rule_name] = rule_violations.get(rule_name, 0) + 1
    
    if rule_violations:
        rule_names = list(rule_violations.keys())
        violation_counts = list(rule_violations.values())
        
        axes[0, 1].bar(range(len(rule_names)), violation_counts)
        axes[0, 1].set_xlabel('规则名称')
        axes[0, 1].set_ylabel('违规数量')
        axes[0, 1].set_title('各规则违规数量')
        axes[0, 1].set_xticks(range(len(rule_names)))
        axes[0, 1].set_xticklabels(rule_names, rotation=45, ha='right')
    else:
        axes[0, 1].text(0.5, 0.5, '无违规数据', ha='center', va='center')
        axes[0, 1].set_title('各规则违规数量')
    
    # 3. 违规趋势（按记录ID）
    if violations:
        record_ids = [v['record_id'] for v in violations]
        axes[1, 0].hist(record_ids, bins=50, alpha=0.7)
        axes[1, 0].set_xlabel('记录ID')
        axes[1, 0].set_ylabel('违规数量')
        axes[1, 0].set_title('违规记录分布')
    else:
        axes[1, 0].text(0.5, 0.5, '无违规数据', ha='center', va='center')
        axes[1, 0].set_title('违规记录分布')
    
    # 4. 数据质量评分
    total_records = results['total_records']
    error_rate = results['summary']['error_rate']
    quality_score = (1 - error_rate) * 100
    
    axes[1, 1].bar(['数据质量评分'], [quality_score], color='green')
    axes[1, 1].set_ylabel('分数 (%)')
    axes[1, 1].set_ylim(0, 100)
    axes[1, 1].text(0, quality_score + 2, f'{quality_score:.1f}%', ha='center')
    axes[1, 1].set_title('整体数据质量评分')
    
    plt.tight_layout()
    plt.savefig('data_quality_validation_results.png', dpi=300, bbox_inches='tight')
    print("验证结果图表已保存为: data_quality_validation_results.png")
    plt.show()


def main():
    """主函数"""
    print("开始执行数据验证示例...")
    
    # 执行客户数据验证
    validator, results = run_customer_data_validation()
    
    # 可视化结果
    visualize_validation_results(validator)
    
    print("\n数据验证示例执行完成!")


if __name__ == "__main__":
    main()