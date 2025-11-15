#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第7章：数据质量工具与平台选型 - 示例代码
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DataProfilingTool:
    """数据剖析工具示例"""
    
    def __init__(self):
        pass
    
    def profile_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        对DataFrame进行全面的数据剖析
        
        Args:
            df: 待剖析的DataFrame
            
        Returns:
            包含数据剖析结果的字典
        """
        profile = {
            'basic_info': {
                'row_count': len(df),
                'column_count': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'creation_time': datetime.now().isoformat()
            },
            'columns': {},
            'data_types': df.dtypes.to_dict(),
            'missing_patterns': self._analyze_missing_patterns(df)
        }
        
        # 分析每一列
        for column in df.columns:
            col_data = df[column]
            col_profile = {
                'data_type': str(col_data.dtype),
                'null_count': int(col_data.isnull().sum()),
                'null_percentage': round((col_data.isnull().sum() / len(df)) * 100, 2),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': round((col_data.nunique() / len(df)) * 100, 2),
                'sample_values': col_data.dropna().head(5).tolist()
            }
            
            # 数值型字段的统计信息
            if col_data.dtype in ['int64', 'float64']:
                col_profile.update({
                    'min': float(col_data.min()) if not col_data.empty else None,
                    'max': float(col_data.max()) if not col_data.empty else None,
                    'mean': float(col_data.mean()) if not col_data.empty else None,
                    'std': float(col_data.std()) if not col_data.empty else None,
                    'median': float(col_data.median()) if not col_data.empty else None,
                    'quartiles': {
                        'q1': float(col_data.quantile(0.25)) if not col_data.empty else None,
                        'q3': float(col_data.quantile(0.75)) if not col_data.empty else None
                    }
                })
                
                # 检测潜在的异常值
                if col_data.std() > 0:
                    z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
                    outliers = col_data[z_scores > 3]
                    col_profile['outliers_count'] = int(len(outliers))
                    col_profile['outliers_percentage'] = round((len(outliers) / len(df)) * 100, 2)
            
            # 字符串字段的统计信息
            elif col_data.dtype == 'object':
                col_profile.update({
                    'avg_length': float(col_data.str.len().mean()) if col_data.str.len().mean() else 0,
                    'max_length': int(col_data.str.len().max()) if col_data.str.len().max() else 0,
                    'min_length': int(col_data.str.len().min()) if col_data.str.len().min() else 0,
                    'most_common_values': col_data.value_counts().head(5).to_dict()
                })
                
                # 检测潜在的格式问题
                col_profile['empty_strings'] = int((col_data == '').sum())
                col_profile['whitespace_only'] = int(col_data.str.strip().eq('').sum())
            
            profile['columns'][column] = col_profile
        
        return profile
    
    def _analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析缺失值模式"""
        missing_matrix = df.isnull()
        missing_patterns = {
            'total_missing_cells': int(missing_matrix.sum().sum()),
            'missing_percentage': round((missing_matrix.sum().sum() / (df.shape[0] * df.shape[1])) * 100, 2),
            'columns_with_missing': missing_matrix.any().sum(),
            'rows_with_missing': missing_matrix.any(axis=1).sum()
        }
        
        # 分析常见的缺失组合模式
        missing_combinations = missing_matrix.groupby(list(df.columns)).size().reset_index(name='count')
        missing_combinations = missing_combinations[missing_combinations['count'] > 1]
        missing_patterns['common_patterns'] = missing_combinations.head(5).to_dict('records')
        
        return missing_patterns
    
    def generate_report(self, profile: Dict[str, Any]) -> str:
        """生成数据剖析报告"""
        report = []
        report.append("=" * 60)
        report.append("数据剖析报告")
        report.append("=" * 60)
        
        # 基本信息
        basic = profile['basic_info']
        report.append(f"数据集基本信息:")
        report.append(f"  - 行数: {basic['row_count']:,}")
        report.append(f"  - 列数: {basic['column_count']}")
        report.append(f"  - 内存使用: {basic['memory_usage']:,} bytes")
        report.append("")
        
        # 缺失值分析
        missing = profile['missing_patterns']
        report.append(f"缺失值分析:")
        report.append(f"  - 总缺失单元格: {missing['total_missing_cells']:,}")
        report.append(f"  - 缺失比例: {missing['missing_percentage']}%")
        report.append(f"  - 有缺失值的列数: {missing['columns_with_missing']}")
        report.append(f"  - 有缺失值的行数: {missing['rows_with_missing']}")
        report.append("")
        
        # 列详细信息
        report.append("列详细信息:")
        for col_name, col_info in profile['columns'].items():
            report.append(f"  {col_name} ({col_info['data_type']}):")
            report.append(f"    - 唯一值: {col_info['unique_count']} ({col_info['unique_percentage']}%)")
            report.append(f"    - 缺失值: {col_info['null_count']} ({col_info['null_percentage']}%)")
            
            if col_info['data_type'] in ['int64', 'float64']:
                report.append(f"    - 最小值: {col_info.get('min', 'N/A')}")
                report.append(f"    - 最大值: {col_info.get('max', 'N/A')}")
                report.append(f"    - 平均值: {col_info.get('mean', 'N/A'):.2f}")
                report.append(f"    - 标准差: {col_info.get('std', 'N/A'):.2f}")
                if 'outliers_count' in col_info:
                    report.append(f"    - 异常值: {col_info['outliers_count']} ({col_info['outliers_percentage']}%)")
            
            report.append("")
        
        return "\n".join(report)


class DataValidationTool:
    """数据验证工具示例"""
    
    def __init__(self):
        self.rules = []
        self.validation_results = []
    
    def add_completeness_rule(self, column: str, name: str = None):
        """添加完整性规则"""
        rule = {
            'name': name or f"{column}_completeness",
            'type': 'completeness',
            'column': column
        }
        self.rules.append(rule)
    
    def add_range_rule(self, column: str, min_val: float, max_val: float, name: str = None):
        """添加范围规则"""
        rule = {
            'name': name or f"{column}_range",
            'type': 'range',
            'column': column,
            'min_value': min_val,
            'max_value': max_val
        }
        self.rules.append(rule)
    
    def add_format_rule(self, column: str, pattern: str, name: str = None):
        """添加格式规则"""
        rule = {
            'name': name or f"{column}_format",
            'type': 'format',
            'column': column,
            'pattern': pattern
        }
        self.rules.append(rule)
    
    def add_validity_rule(self, column: str, valid_values: List[Any], name: str = None):
        """添加有效性规则"""
        rule = {
            'name': name or f"{column}_validity",
            'type': 'validity',
            'column': column,
            'valid_values': valid_values
        }
        self.rules.append(rule)
    
    def validate(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """执行数据验证"""
        self.validation_results = []
        
        for rule in self.rules:
            result = self._apply_rule(df, rule)
            self.validation_results.append(result)
        
        return self.validation_results
    
    def _apply_rule(self, df: pd.DataFrame, rule: Dict[str, Any]) -> Dict[str, Any]:
        """应用单个验证规则"""
        column = rule['column']
        
        if column not in df.columns:
            return {
                'rule_name': rule['name'],
                'rule_type': rule['type'],
                'column': column,
                'status': 'error',
                'message': f'列 {column} 不存在于数据集中',
                'details': {}
            }
        
        col_data = df[column]
        
        if rule['type'] == 'completeness':
            null_count = col_data.isnull().sum()
            completeness_rate = 1 - (null_count / len(df))
            
            return {
                'rule_name': rule['name'],
                'rule_type': rule['type'],
                'column': column,
                'status': 'pass' if completeness_rate == 1.0 else 'fail',
                'message': f'完整性: {completeness_rate:.2%} ({null_count} 个空值)',
                'details': {
                    'null_count': int(null_count),
                    'completeness_rate': float(completeness_rate)
                }
            }
        
        elif rule['type'] == 'range':
            min_val = rule['min_value']
            max_val = rule['max_value']
            
            # 只检查数值型数据
            numeric_data = pd.to_numeric(col_data, errors='coerce')
            out_of_range = (numeric_data < min_val) | (numeric_data > max_val) | numeric_data.isnull()
            invalid_count = out_of_range.sum()
            validity_rate = 1 - (invalid_count / len(df))
            
            return {
                'rule_name': rule['name'],
                'rule_type': rule['type'],
                'column': column,
                'status': 'pass' if validity_rate >= 0.99 else 'fail',
                'message': f'范围检查: {validity_rate:.2%} 在 [{min_val}, {max_val}] 范围内',
                'details': {
                    'invalid_count': int(invalid_count),
                    'validity_rate': float(validity_rate),
                    'min_actual': float(numeric_data.min()) if not numeric_data.empty else None,
                    'max_actual': float(numeric_data.max()) if not numeric_data.empty else None
                }
            }
        
        elif rule['type'] == 'format':
            import re
            pattern = rule['pattern']
            try:
                regex = re.compile(pattern)
                # 只检查字符串类型数据
                string_data = col_data.astype(str)
                matches = string_data.apply(lambda x: bool(regex.match(x)))
                valid_count = matches.sum()
                validity_rate = valid_count / len(df)
                
                return {
                    'rule_name': rule['name'],
                    'rule_type': rule['type'],
                    'column': column,
                    'status': 'pass' if validity_rate >= 0.99 else 'fail',
                    'message': f'格式检查: {validity_rate:.2%} 符合格式 {pattern}',
                    'details': {
                        'valid_count': int(valid_count),
                        'validity_rate': float(validity_rate)
                    }
                }
            except Exception as e:
                return {
                    'rule_name': rule['name'],
                    'rule_type': rule['type'],
                    'column': column,
                    'status': 'error',
                    'message': f'格式检查失败: {str(e)}',
                    'details': {}
                }
        
        elif rule['type'] == 'validity':
            valid_values = set(rule['valid_values'])
            # 检查哪些值不在有效值列表中
            invalid_mask = ~col_data.isin(valid_values)
            invalid_count = invalid_mask.sum()
            validity_rate = 1 - (invalid_count / len(df))
            
            return {
                'rule_name': rule['name'],
                'rule_type': rule['type'],
                'column': column,
                'status': 'pass' if validity_rate >= 0.99 else 'fail',
                'message': f'有效性检查: {validity_rate:.2%} 在有效值列表中',
                'details': {
                    'invalid_count': int(invalid_count),
                    'validity_rate': float(validity_rate),
                    'invalid_values': col_data[invalid_mask].unique().tolist()
                }
            }
    
    def generate_validation_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("=" * 60)
        report.append("数据验证报告")
        report.append("=" * 60)
        
        passed = 0
        failed = 0
        errors = 0
        
        for result in self.validation_results:
            if result['status'] == 'pass':
                passed += 1
                status_icon = "✓"
            elif result['status'] == 'fail':
                failed += 1
                status_icon = "✗"
            else:
                errors += 1
                status_icon = "⚠"
            
            report.append(f"[{status_icon}] {result['rule_name']} ({result['column']})")
            report.append(f"    {result['message']}")
            report.append("")
        
        report.append(f"总结: {passed} 通过, {failed} 失败, {errors} 错误")
        return "\n".join(report)


class ToolSelector:
    """工具选择器"""
    
    def __init__(self):
        self.tools = self._load_tools_database()
    
    def _load_tools_database(self) -> Dict[str, Dict[str, Any]]:
        """加载工具数据库"""
        return {
            'Great Expectations': {
                'type': 'open_source',
                'language': 'python',
                'scale': 'small_to_medium',
                'features': ['profiling', 'validation', 'documentation'],
                'integration': ['pandas', 'spark', 'sql'],
                'cost': 'free',
                'ease_of_use': 90,
                'performance': 70,
                'extensibility': 85,
                'support': 80
            },
            'Deequ': {
                'type': 'open_source',
                'language': 'scala',
                'scale': 'large',
                'features': ['validation', 'metrics', 'anomaly_detection'],
                'integration': ['spark'],
                'cost': 'free',
                'ease_of_use': 60,
                'performance': 95,
                'extensibility': 90,
                'support': 70
            },
            'Apache Griffin': {
                'type': 'open_source',
                'language': 'java',
                'scale': 'enterprise',
                'features': ['profiling', 'validation', 'monitoring', 'dashboard'],
                'integration': ['hadoop', 'spark', 'kafka'],
                'cost': 'free',
                'ease_of_use': 70,
                'performance': 85,
                'extensibility': 90,
                'support': 75
            },
            'Informatica DQ': {
                'type': 'commercial',
                'language': 'java',
                'scale': 'enterprise',
                'features': ['profiling', 'cleansing', 'monitoring', 'matching'],
                'integration': ['enterprise_systems'],
                'cost': 'high',
                'ease_of_use': 85,
                'performance': 90,
                'extensibility': 95,
                'support': 95
            },
            'Talend DQ': {
                'type': 'commercial',
                'language': 'java',
                'scale': 'medium_to_large',
                'features': ['profiling', 'cleansing', 'validation'],
                'integration': ['talend_platform'],
                'cost': 'medium',
                'ease_of_use': 80,
                'performance': 85,
                'extensibility': 90,
                'support': 90
            }
        }
    
    def filter_tools(self, requirements: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """根据需求筛选工具"""
        filtered_tools = {}
        
        for tool_name, tool_info in self.tools.items():
            match = True
            
            # 检查技术要求
            if 'language' in requirements and requirements['language'] != tool_info['language']:
                match = False
            
            if 'scale' in requirements:
                scale_requirements = requirements['scale']
                tool_scale = tool_info['scale']
                if scale_requirements == 'large' and tool_scale == 'small_to_medium':
                    match = False
                elif scale_requirements == 'enterprise' and tool_scale in ['small_to_medium', 'large']:
                    match = False
            
            if 'type' in requirements and requirements['type'] != tool_info['type']:
                match = False
            
            if 'budget' in requirements and requirements['budget'] == 'low' and tool_info['cost'] == 'high':
                match = False
            
            if match:
                filtered_tools[tool_name] = tool_info
        
        return filtered_tools
    
    def evaluate_tools(self, tools: Dict[str, Dict[str, Any]], 
                      criteria_weights: Dict[str, float] = None) -> Dict[str, float]:
        """评估工具"""
        if criteria_weights is None:
            criteria_weights = {
                'ease_of_use': 0.25,
                'performance': 0.25,
                'extensibility': 0.25,
                'support': 0.25
            }
        
        scores = {}
        for tool_name, tool_info in tools.items():
            total_score = 0
            for criterion, weight in criteria_weights.items():
                if criterion in tool_info:
                    score = tool_info[criterion] * weight
                    total_score += score
            scores[tool_name] = round(total_score, 2)
        
        return scores
    
    def recommend_tools(self, requirements: Dict[str, Any], 
                       criteria_weights: Dict[str, float] = None) -> List[tuple]:
        """推荐工具"""
        filtered_tools = self.filter_tools(requirements)
        scores = self.evaluate_tools(filtered_tools, criteria_weights)
        
        # 按分数排序
        recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations


class PoCValidator:
    """PoC验证器"""
    
    def __init__(self, tool_name: str, test_data: pd.DataFrame):
        self.tool_name = tool_name
        self.test_data = test_data
        self.results = {}
    
    def setup_environment(self):
        """设置测试环境"""
        print(f"设置 {self.tool_name} 测试环境...")
        start_time = time.time()
        
        # 模拟环境设置过程
        time.sleep(1)  # 模拟设置时间
        
        self.results['setup_time'] = time.time() - start_time
        print(f"环境设置完成，耗时: {self.results['setup_time']:.2f} 秒")
    
    def run_functionality_tests(self):
        """运行功能测试"""
        print(f"运行 {self.tool_name} 功能测试...")
        start_time = time.time()
        
        # 使用我们的数据剖析工具进行测试
        profiler = DataProfilingTool()
        profile = profiler.profile_dataframe(self.test_data)
        
        # 使用数据验证工具进行测试
        validator = DataValidationTool()
        validator.add_completeness_rule('id')
        validator.add_range_rule('age', 0, 120)
        validator.add_format_rule('email', r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        validator.add_validity_rule('status', ['active', 'inactive', 'pending'])
        
        validation_results = validator.validate(self.test_data)
        
        self.results['functionality_time'] = time.time() - start_time
        self.results['profile_result'] = profile
        self.results['validation_results'] = validation_results
        self.results['functionality_passed'] = True
        
        print(f"功能测试完成，耗时: {self.results['functionality_time']:.2f} 秒")
    
    def run_performance_tests(self):
        """运行性能测试"""
        print(f"运行 {self.tool_name} 性能测试...")
        start_time = time.time()
        
        # 重复执行多次以测试性能
        for _ in range(5):
            profiler = DataProfilingTool()
            profiler.profile_dataframe(self.test_data)
        
        self.results['performance_time'] = time.time() - start_time
        self.results['average_processing_time'] = self.results['performance_time'] / 5
        
        print(f"性能测试完成，平均处理时间: {self.results['average_processing_time']:.2f} 秒")
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report = f"""
{self.tool_name} PoC验证报告
========================

1. 环境设置
   - 设置时间: {self.results.get('setup_time', 'N/A'):.2f} 秒

2. 功能测试
   - 通过状态: {'通过' if self.results.get('functionality_passed') else '失败'}
   - 测试时间: {self.results.get('functionality_time', 'N/A'):.2f} 秒
   - 数据集大小: {len(self.test_data)} 行 × {len(self.test_data.columns)} 列

3. 性能测试
   - 总测试时间: {self.results.get('performance_time', 'N/A'):.2f} 秒
   - 平均处理时间: {self.results.get('average_processing_time', 'N/A'):.2f} 秒

总结: {self.tool_name} 在本次PoC验证中表现{'良好' if self.results.get('functionality_passed') else '不佳'}
        """
        return report


def create_sample_data() -> pd.DataFrame:
    """创建示例数据"""
    np.random.seed(42)
    
    # 创建用户数据
    n_records = 10000
    user_ids = range(1, n_records + 1)
    ages = np.random.randint(18, 80, n_records)
    # 引入一些异常年龄
    ages[np.random.choice(n_records, 100, replace=False)] = np.random.randint(120, 200, 100)
    
    emails = [f"user_{i}@{'gmail' if i % 3 == 0 else 'yahoo' if i % 3 == 1 else 'outlook'}.com" 
              for i in user_ids]
    # 引入一些格式错误的邮箱
    for i in np.random.choice(n_records, 50, replace=False):
        emails[i] = f"invalid_email_{i}"
    
    statuses = np.random.choice(['active', 'inactive', 'pending', 'deleted'], n_records, p=[0.7, 0.2, 0.09, 0.01])
    
    # 引入一些缺失值
    missing_indices = np.random.choice(n_records, 200, replace=False)
    for i in missing_indices[:100]:
        ages[i] = np.nan
    for i in missing_indices[100:]:
        emails[i] = np.nan
    
    data = pd.DataFrame({
        'id': user_ids,
        'age': ages,
        'email': emails,
        'status': statuses,
        'created_at': pd.date_range('2023-01-01', periods=n_records, freq='1min')
    })
    
    return data


def main():
    """主函数"""
    print("第7章：数据质量工具与平台选型 - 示例代码演示")
    print("=" * 60)
    
    # 创建示例数据
    print("1. 创建示例数据...")
    sample_data = create_sample_data()
    print(f"创建了 {len(sample_data)} 行数据")
    print()
    
    # 数据剖析演示
    print("2. 数据剖析演示...")
    profiler = DataProfilingTool()
    profile_result = profiler.profile_dataframe(sample_data)
    profile_report = profiler.generate_report(profile_result)
    print(profile_report)
    print()
    
    # 数据验证演示
    print("3. 数据验证演示...")
    validator = DataValidationTool()
    validator.add_completeness_rule('id', '用户ID完整性检查')
    validator.add_completeness_rule('email', '邮箱完整性检查')
    validator.add_range_rule('age', 0, 120, '年龄范围检查')
    validator.add_format_rule('email', r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', '邮箱格式检查')
    validator.add_validity_rule('status', ['active', 'inactive', 'pending'], '状态有效性检查')
    
    validation_results = validator.validate(sample_data)
    validation_report = validator.generate_validation_report()
    print(validation_report)
    print()
    
    # 工具选型演示
    print("4. 工具选型演示...")
    selector = ToolSelector()
    
    # 定义需求
    requirements = {
        'language': 'python',
        'scale': 'medium',
        'type': 'open_source',
        'budget': 'low'
    }
    
    # 定义评估标准权重
    criteria_weights = {
        'ease_of_use': 0.3,
        'performance': 0.25,
        'extensibility': 0.25,
        'support': 0.2
    }
    
    # 获取推荐
    recommendations = selector.recommend_tools(requirements, criteria_weights)
    print("根据您的需求，推荐的工具排序如下:")
    for i, (tool, score) in enumerate(recommendations, 1):
        print(f"  {i}. {tool}: {score} 分")
    print()
    
    # PoC验证演示
    print("5. PoC验证演示...")
    poc_validator = PoCValidator("数据质量工具", sample_data)
    poc_validator.setup_environment()
    poc_validator.run_functionality_tests()
    poc_validator.run_performance_tests()
    poc_report = poc_validator.generate_report()
    print(poc_report)
    
    print("演示完成!")


if __name__ == "__main__":
    main()