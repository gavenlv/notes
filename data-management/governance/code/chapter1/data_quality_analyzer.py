"""
第1章代码示例：数据质量分析工具
演示如何分析数据质量问题，计算质量指标和业务影响
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import re
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date

class DataQualityAnalyzer:
    """数据质量分析工具，用于评估和监控数据质量问题"""
    
    def __init__(self):
        """初始化数据质量分析器"""
        self.quality_dimensions = [
            'completeness',    # 完整性
            'accuracy',        # 准确性
            'consistency',     # 一致性
            'timeliness',      # 及时性
            'uniqueness',      # 唯一性
            'validity'         # 有效性
        ]
        
        self.quality_results = {}
        self.business_rules = {}
    
    def set_business_rules(self, table_name: str, rules: Dict[str, Dict]):
        """设置业务规则
        
        Args:
            table_name: 表名
            rules: 业务规则字典，格式为 {列名: 规则字典}
        """
        self.business_rules[table_name] = rules
        print(f"已设置表 '{table_name}' 的业务规则")
    
    def analyze_completeness(self, df: pd.DataFrame, table_name: str) -> Dict[str, float]:
        """分析数据完整性
        
        Args:
            df: 数据框
            table_name: 表名
            
        Returns:
            完整性指标字典
        """
        completeness_results = {}
        
        # 计算每列的完整性（非空值比例）
        for column in df.columns:
            non_null_count = df[column].notna().sum()
            total_count = len(df)
            completeness = non_null_count / total_count if total_count > 0 else 0
            
            completeness_results[column] = completeness
        
        # 计算整体完整性
        overall_completeness = np.mean(list(completeness_results.values()))
        completeness_results['overall'] = overall_completeness
        
        self.quality_results[f"{table_name}_completeness"] = completeness_results
        
        return completeness_results
    
    def analyze_accuracy(self, df: pd.DataFrame, table_name: str) -> Dict[str, Dict[str, Any]]:
        """分析数据准确性
        
        Args:
            df: 数据框
            table_name: 表名
            
        Returns:
            准确性指标字典
        """
        accuracy_results = {}
        rules = self.business_rules.get(table_name, {})
        
        for column, rule in rules.items():
            if column not in df.columns:
                continue
                
            accuracy_info = {
                'total_records': len(df),
                'valid_records': 0,
                'invalid_records': 0,
                'accuracy_rate': 0.0,
                'rule_type': rule.get('type', 'unknown'),
                'rule_description': rule.get('description', ''),
                'invalid_samples': []
            }
            
            if rule['type'] == 'pattern':
                # 模式验证（如邮箱、电话等）
                pattern = rule['pattern']
                valid_mask = df[column].str.match(pattern, na=False)
                
            elif rule['type'] == 'range':
                # 范围验证
                min_val = rule.get('min')
                max_val = rule.get('max')
                
                if min_val is not None and max_val is not None:
                    valid_mask = (df[column] >= min_val) & (df[column] <= max_val)
                elif min_val is not None:
                    valid_mask = df[column] >= min_val
                elif max_val is not None:
                    valid_mask = df[column] <= max_val
                else:
                    valid_mask = pd.Series([True] * len(df))
                    
            elif rule['type'] == 'values':
                # 枚举值验证
                valid_values = rule['values']
                valid_mask = df[column].isin(valid_values)
                
            else:
                # 无验证规则
                valid_mask = pd.Series([True] * len(df))
            
            # 统计准确性
            accuracy_info['valid_records'] = valid_mask.sum()
            accuracy_info['invalid_records'] = len(df) - valid_mask.sum()
            accuracy_info['accuracy_rate'] = accuracy_info['valid_records'] / len(df) if len(df) > 0 else 0
            
            # 获取无效样本（最多5个）
            invalid_samples = df[~valid_mask][column].dropna().head(5).tolist()
            accuracy_info['invalid_samples'] = invalid_samples
            
            accuracy_results[column] = accuracy_info
        
        # 计算整体准确性
        if accuracy_results:
            overall_accuracy = np.mean([info['accuracy_rate'] for info in accuracy_results.values()])
            accuracy_results['overall'] = {
                'overall_accuracy_rate': overall_accuracy
            }
        
        self.quality_results[f"{table_name}_accuracy"] = accuracy_results
        
        return accuracy_results
    
    def analyze_consistency(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          key_columns: List[str], compare_columns: List[str],
                          table1_name: str, table2_name: str) -> Dict[str, Any]:
        """分析两个表之间的一致性
        
        Args:
            df1: 第一个数据框
            df2: 第二个数据框
            key_columns: 关键字段列表
            compare_columns: 需要比较的字段列表
            table1_name: 第一个表名
            table2_name: 第二个表名
            
        Returns:
            一致性分析结果
        """
        # 确保关键列在两个表中都存在
        for col in key_columns:
            if col not in df1.columns or col not in df2.columns:
                raise ValueError(f"关键列 '{col}' 不存在于表中")
        
        # 确保比较列在两个表中都存在
        for col in compare_columns:
            if col not in df1.columns or col not in df2.columns:
                raise ValueError(f"比较列 '{col}' 不存在于表中")
        
        # 合并数据
        merged_df = pd.merge(
            df1[key_columns + compare_columns],
            df2[key_columns + compare_columns],
            on=key_columns,
            how='inner',
            suffixes=('_1', '_2')
        )
        
        # 计算每列的一致性
        consistency_results = {}
        total_comparisons = len(merged_df)
        
        if total_comparisons == 0:
            # 如果没有匹配的行
            for col in compare_columns:
                consistency_results[col] = {
                    'consistent_records': 0,
                    'inconsistent_records': 0,
                    'consistency_rate': 0.0,
                    'no_match_records': True
                }
        else:
            for col in compare_columns:
                col1 = f"{col}_1"
                col2 = f"{col}_2"
                
                # 比较两个列的值（考虑NaN情况）
                mask = (merged_df[col1].isna() & merged_df[col2].isna()) | \
                       (merged_df[col1] == merged_df[col2])
                
                consistent_count = mask.sum()
                inconsistent_count = total_comparisons - consistent_count
                consistency_rate = consistent_count / total_comparisons if total_comparisons > 0 else 0
                
                consistency_results[col] = {
                    'consistent_records': consistent_count,
                    'inconsistent_records': inconsistent_count,
                    'consistency_rate': consistency_rate,
                    'no_match_records': False
                }
        
        # 统计只在一个表中存在的记录
        df1_only = df1[~df1[key_columns].apply(tuple, axis=1).isin(
            df2[key_columns].apply(tuple, axis=1))]
        df2_only = df2[~df2[key_columns].apply(tuple, axis=1).isin(
            df1[key_columns].apply(tuple, axis=1))]
        
        overall_consistency = np.mean([info['consistency_rate'] for info in consistency_results.values()])
        
        results = {
            'column_consistency': consistency_results,
            'overall_consistency': overall_consistency,
            'table1_only_count': len(df1_only),
            'table2_only_count': len(df2_only),
            'matched_count': total_comparisons,
            'table1_name': table1_name,
            'table2_name': table2_name
        }
        
        self.quality_results[f"{table1_name}_{table2_name}_consistency"] = results
        
        return results
    
    def analyze_timeliness(self, df: pd.DataFrame, date_column: str, 
                         table_name: str, current_date: date = None) -> Dict[str, Any]:
        """分析数据及时性
        
        Args:
            df: 数据框
            date_column: 日期列名
            table_name: 表名
            current_date: 当前日期（默认为今天）
            
        Returns:
            及时性分析结果
        """
        if date_column not in df.columns:
            raise ValueError(f"日期列 '{date_column}' 不存在于表中")
        
        if current_date is None:
            current_date = datetime.now().date()
        
        # 转换日期列
        date_series = pd.to_datetime(df[date_column]).dt.date
        
        # 计算延迟天数
        today_mask = date_series == current_date
        yesterday_mask = date_series == pd.to_datetime(current_date) - pd.Timedelta(days=1)
        last_week_mask = date_series >= pd.to_datetime(current_date) - pd.Timedelta(days=7)
        last_month_mask = date_series >= pd.to_datetime(current_date) - pd.Timedelta(days=30)
        
        # 计算及时性指标
        results = {
            'total_records': len(df),
            'today_records': today_mask.sum(),
            'yesterday_records': yesterday_mask.sum(),
            'last_week_records': last_week_mask.sum(),
            'last_month_records': last_month_mask.sum(),
            'today_percentage': (today_mask.sum() / len(df) * 100) if len(df) > 0 else 0,
            'yesterday_percentage': (yesterday_mask.sum() / len(df) * 100) if len(df) > 0 else 0,
            'last_week_percentage': (last_week_mask.sum() / len(df) * 100) if len(df) > 0 else 0,
            'last_month_percentage': (last_month_mask.sum() / len(df) * 100) if len(df) > 0 else 0,
            'latest_date': date_series.max(),
            'earliest_date': date_series.min(),
            'average_delay_days': ((current_date - date_series).mean().days) if len(date_series) > 0 else 0
        }
        
        self.quality_results[f"{table_name}_timeliness"] = results
        
        return results
    
    def analyze_uniqueness(self, df: pd.DataFrame, key_columns: List[str], 
                          table_name: str) -> Dict[str, Any]:
        """分析数据唯一性
        
        Args:
            df: 数据框
            key_columns: 应该唯一的列或列组合
            table_name: 表名
            
        Returns:
            唯一性分析结果
        """
        total_records = len(df)
        results = {}
        
        for column in key_columns:
            if column not in df.columns:
                continue
            
            unique_count = df[column].nunique()
            duplicate_count = total_records - unique_count
            uniqueness_rate = unique_count / total_records if total_records > 0 else 0
            
            results[column] = {
                'total_records': total_records,
                'unique_count': unique_count,
                'duplicate_count': duplicate_count,
                'uniqueness_rate': uniqueness_rate,
                'duplicate_rows': None
            }
            
            # 获取重复行（最多10个）
            if duplicate_count > 0:
                duplicate_mask = df[column].duplicated(keep=False)
                duplicate_rows = df[duplicate_mask].head(10).to_dict('records')
                results[column]['duplicate_rows'] = duplicate_rows
        
        # 分析组合唯一性（如果提供了多列）
        if len(key_columns) > 1:
            combination_col = '_'.join(key_columns)
            unique_combinations = df[key_columns].drop_duplicates().shape[0]
            duplicate_combinations = total_records - unique_combinations
            combination_uniqueness_rate = unique_combinations / total_records if total_records > 0 else 0
            
            results['combination'] = {
                'columns': key_columns,
                'total_records': total_records,
                'unique_combinations': unique_combinations,
                'duplicate_combinations': duplicate_combinations,
                'uniqueness_rate': combination_uniqueness_rate
            }
        
        self.quality_results[f"{table_name}_uniqueness"] = results
        
        return results
    
    def calculate_business_impact(self, table_name: str, table_size: int, 
                                data_usage: Dict[str, int], 
                                importance_weights: Dict[str, float] = None) -> Dict[str, Any]:
        """计算数据质量问题对业务的影响
        
        Args:
            table_name: 表名
            table_size: 表大小（行数）
            data_usage: 数据使用情况字典，格式为 {用途: 次数}
            importance_weights: 各质量维度的重要性权重
            
        Returns:
            业务影响分析结果
        """
        if importance_weights is None:
            importance_weights = {
                'completeness': 0.25,
                'accuracy': 0.25,
                'consistency': 0.2,
                'timeliness': 0.15,
                'uniqueness': 0.15
            }
        
        # 获取各质量维度的分数
        dimension_scores = {}
        
        for dimension in self.quality_dimensions:
            result_key = f"{table_name}_{dimension}"
            if result_key in self.quality_results:
                if dimension == 'completeness':
                    overall_score = self.quality_results[result_key].get('overall', 0)
                elif dimension == 'accuracy':
                    overall_score = self.quality_results[result_key].get('overall', {}).get('overall_accuracy_rate', 0)
                elif dimension == 'consistency':
                    # 对于一致性，使用第一个表名匹配的结果
                    for key, result in self.quality_results.items():
                        if key.endswith('_consistency') and table_name in key:
                            overall_score = result.get('overall_consistency', 0)
                            break
                elif dimension == 'timeliness':
                    overall_score = self.quality_results[result_key].get('today_percentage', 0) / 100
                elif dimension == 'uniqueness':
                    # 对于唯一性，使用第一个列的分数
                    first_column = next(iter(self.quality_results[result_key].keys()), None)
                    if first_column and first_column != 'combination':
                        overall_score = self.quality_results[result_key][first_column]['uniqueness_rate']
                    else:
                        overall_score = 0
                else:
                    overall_score = 0
                
                dimension_scores[dimension] = overall_score
        
        # 计算加权总体质量分数
        overall_quality_score = sum(
            dimension_scores.get(dim, 0) * importance_weights.get(dim, 0)
            for dim in self.quality_dimensions
        )
        
        # 计算业务影响
        total_usage = sum(data_usage.values())
        
        # 假设数据质量影响与使用频率成正比
        impact_score = (1 - overall_quality_score) * total_usage
        
        # 估算问题记录数
        problem_records = {
            'completeness': int(table_size * (1 - dimension_scores.get('completeness', 0))),
            'accuracy': int(table_size * (1 - dimension_scores.get('accuracy', 0))),
            'timeliness': int(table_size * (1 - dimension_scores.get('timeliness', 0))),
            'uniqueness': 0  # 唯一性问题需要特殊处理
        }
        
        # 计算唯一性问题记录数
        uniq_key = f"{table_name}_uniqueness"
        if uniq_key in self.quality_results:
            for col, uniq_result in self.quality_results[uniq_key].items():
                if col != 'combination' and isinstance(uniq_result, dict):
                    problem_records['uniqueness'] += uniq_result.get('duplicate_count', 0)
        
        # 估算修复成本（基于问题记录数和使用频率）
        repair_cost_per_record = 0.1  # 假设每条记录修复成本
        total_repair_cost = sum(problem_records.values()) * repair_cost_per_record
        
        # 计算数据价值损失（基于质量分数和使用频率）
        data_value_per_usage = 100  # 假设每次使用的价值
        data_value_loss = total_usage * data_value_per_usage * (1 - overall_quality_score)
        
        results = {
            'table_name': table_name,
            'dimension_scores': dimension_scores,
            'overall_quality_score': overall_quality_score,
            'total_usage': total_usage,
            'impact_score': impact_score,
            'problem_records': problem_records,
            'total_repair_cost': total_repair_cost,
            'data_value_loss': data_value_loss,
            'importance_weights': importance_weights,
            'total_business_impact': total_repair_cost + data_value_loss
        }
        
        return results
    
    def generate_quality_report(self, table_name: str) -> Dict[str, Any]:
        """生成数据质量报告
        
        Args:
            table_name: 表名
            
        Returns:
            数据质量报告
        """
        report = {
            'table_name': table_name,
            'generated_at': datetime.now().isoformat(),
            'dimensions': {},
            'recommendations': []
        }
        
        # 收集各维度结果
        for dimension in self.quality_dimensions:
            result_key = f"{table_name}_{dimension}"
            if result_key in self.quality_results:
                report['dimensions'][dimension] = self.quality_results[result_key]
        
        # 生成建议
        recommendations = self._generate_recommendations(table_name)
        report['recommendations'] = recommendations
        
        return report
    
    def _generate_recommendations(self, table_name: str) -> List[Dict[str, str]]:
        """基于分析结果生成改进建议
        
        Args:
            table_name: 表名
            
        Returns:
            改进建议列表
        """
        recommendations = []
        
        # 检查完整性
        completeness_key = f"{table_name}_completeness"
        if completeness_key in self.quality_results:
            completeness = self.quality_results[completeness_key]
            
            for column, score in completeness.items():
                if column != 'overall' and score < 0.9:
                    recommendations.append({
                        'dimension': 'completeness',
                        'priority': 'high' if score < 0.7 else 'medium',
                        'issue': f"列 '{column}' 的完整性仅为 {score:.1%}",
                        'recommendation': f"实施非空值检查，设置默认值或通过数据补齐程序填充 '{column}' 列的缺失值"
                    })
        
        # 检查准确性
        accuracy_key = f"{table_name}_accuracy"
        if accuracy_key in self.quality_results:
            accuracy = self.quality_results[accuracy_key]
            
            for column, info in accuracy.items():
                if column != 'overall' and isinstance(info, dict):
                    if info['accuracy_rate'] < 0.95:
                        priority = 'high' if info['accuracy_rate'] < 0.9 else 'medium'
                        recommendations.append({
                            'dimension': 'accuracy',
                            'priority': priority,
                            'issue': f"列 '{column}' 的准确性仅为 {info['accuracy_rate']:.1%}，有 {info['invalid_records']} 条无效记录",
                            'recommendation': f"实施 {info['rule_type']} 验证规则，检查并修正 '{column}' 列中的无效数据"
                        })
        
        # 检查唯一性
        uniqueness_key = f"{table_name}_uniqueness"
        if uniqueness_key in self.quality_results:
            uniqueness = self.quality_results[uniqueness_key]
            
            for column, info in uniqueness.items():
                if column != 'combination' and isinstance(info, dict):
                    if info['uniqueness_rate'] < 0.99:
                        priority = 'high' if info['uniqueness_rate'] < 0.9 else 'medium'
                        recommendations.append({
                            'dimension': 'uniqueness',
                            'priority': priority,
                            'issue': f"列 '{column}' 存在 {info['duplicate_count']} 条重复记录，唯一性仅为 {info['uniqueness_rate']:.1%}",
                            'recommendation': f"实施唯一约束，检查并清除 '{column}' 列中的重复记录"
                        })
        
        # 检查及时性
        timeliness_key = f"{table_name}_timeliness"
        if timeliness_key in self.quality_results:
            timeliness = self.quality_results[timeliness_key]
            
            if timeliness.get('today_percentage', 0) < 50:
                recommendations.append({
                    'dimension': 'timeliness',
                    'priority': 'high',
                    'issue': f"今日数据仅为 {timeliness['today_percentage']:.1%}，数据更新不及时",
                    'recommendation': "检查数据抽取和加载流程，确保数据能够及时更新"
                })
        
        return recommendations
    
    def visualize_quality_dimensions(self, table_name: str):
        """可视化各质量维度分数
        
        Args:
            table_name: 表名
        """
        dimensions = []
        scores = []
        
        for dimension in self.quality_dimensions:
            result_key = f"{table_name}_{dimension}"
            if result_key in self.quality_results:
                if dimension == 'completeness':
                    score = self.quality_results[result_key].get('overall', 0) * 100
                elif dimension == 'accuracy':
                    score = self.quality_results[result_key].get('overall', {}).get('overall_accuracy_rate', 0) * 100
                elif dimension == 'consistency':
                    # 对于一致性，使用第一个表名匹配的结果
                    score = 0
                    for key, result in self.quality_results.items():
                        if key.endswith('_consistency') and table_name in key:
                            score = result.get('overall_consistency', 0) * 100
                            break
                elif dimension == 'timeliness':
                    score = self.quality_results[result_key].get('today_percentage', 0)
                elif dimension == 'uniqueness':
                    # 对于唯一性，使用第一个列的分数
                    first_column = next(iter(self.quality_results[result_key].keys()), None)
                    if first_column and first_column != 'combination':
                        score = self.quality_results[result_key][first_column]['uniqueness_rate'] * 100
                    else:
                        score = 0
                else:
                    score = 0
                
                dimensions.append(dimension)
                scores.append(score)
        
        # 创建图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(dimensions, scores, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        
        # 添加数据标签
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{score:.1f}%', ha='center', va='bottom')
        
        plt.title(f'数据质量维度分析 - {table_name}')
        plt.ylabel('分数 (%)')
        plt.ylim(0, 100)
        plt.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='警戒线 (80%)')
        plt.axhline(y=90, color='orange', linestyle='--', alpha=0.7, label='良好线 (90%)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{table_name}_quality_dimensions.png', dpi=300, bbox_inches='tight')
        plt.show()


# 演示数据质量分析
def demonstrate_data_quality_analysis():
    """演示数据质量分析工具的使用"""
    print("="*60)
    print("数据质量分析工具演示")
    print("="*60)
    
    # 创建模拟数据
    print("\n1. 创建模拟数据")
    print("-"*40)
    
    # 客户数据
    customers_data = {
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['张三', '李四', '', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一'],
        'email': ['zhangsan@example.com', 'lisi@', 'wangwu@example.com', 'zhaoliu@example.com', 
                 'qianqi', 'sunba@example.com', 'zhoujiu', 'wu10@example.com', 'zheng11@example.com', 'zheng11@example.com'],
        'phone': ['13812345678', '13998765432', '13612345678', '13712345678', 
                  '13512345678', '13412345678', '13312345678', '13212345678', '13112345678', '13112345678'],
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 65],  # 最后一个年龄与第9个重复，模拟重复记录
        'city': ['北京', '上海', '广州', '深圳', '杭州', '苏州', '成都', '重庆', '西安', '西安'],
        'registration_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', 
                             '2023-05-12', '2023-06-18', '2023-07-22', '2023-08-25', '2023-09-30', '2023-09-30']
    }
    
    customers_df = pd.DataFrame(customers_data)
    
    # 订单数据
    orders_data = {
        'order_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 9],  # 最后两个订单属于同一客户
        'order_date': ['2023-11-20', '2023-11-21', '2023-11-22', '2023-11-23', 
                      '2023-11-20', '2023-11-21', '2023-11-22', '2023-11-23', 
                      '2023-11-20', '2023-11-21'],
        'amount': [100.50, 75.25, 120.00, 85.75, 200.00, 50.25, 95.50, 110.00, 80.25, 80.25]
    }
    
    orders_df = pd.DataFrame(orders_data)
    
    print("客户数据:")
    print(customers_df.head())
    
    print("\n订单数据:")
    print(orders_df.head())
    
    # 创建分析器实例
    analyzer = DataQualityAnalyzer()
    
    # 设置业务规则
    print("\n2. 设置业务规则")
    print("-"*40)
    
    # 客户表业务规则
    customer_rules = {
        'email': {
            'type': 'pattern',
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'description': '有效的邮箱格式'
        },
        'phone': {
            'type': 'pattern',
            'pattern': r'^1[3-9]\d{9}$',
            'description': '有效的中国手机号格式'
        },
        'age': {
            'type': 'range',
            'min': 18,
            'max': 100,
            'description': '年龄应在18-100岁之间'
        },
        'city': {
            'type': 'values',
            'values': ['北京', '上海', '广州', '深圳', '杭州', '苏州', '成都', '重庆', '西安', '武汉', '南京'],
            'description': '必须是主要城市之一'
        }
    }
    
    # 订单表业务规则
    order_rules = {
        'amount': {
            'type': 'range',
            'min': 0.01,
            'max': 10000.00,
            'description': '订单金额应在0.01-10000元之间'
        }
    }
    
    analyzer.set_business_rules('customers', customer_rules)
    analyzer.set_business_rules('orders', order_rules)
    
    # 3. 分析完整性
    print("\n3. 分析数据完整性")
    print("-"*40)
    
    customers_completeness = analyzer.analyze_completeness(customers_df, 'customers')
    orders_completeness = analyzer.analyze_completeness(orders_df, 'orders')
    
    print("客户数据完整性:")
    for column, completeness in customers_completeness.items():
        print(f"  {column}: {completeness:.1%}")
    
    print("\n订单数据完整性:")
    for column, completeness in orders_completeness.items():
        print(f"  {column}: {completeness:.1%}")
    
    # 4. 分析准确性
    print("\n4. 分析数据准确性")
    print("-"*40)
    
    customers_accuracy = analyzer.analyze_accuracy(customers_df, 'customers')
    orders_accuracy = analyzer.analyze_accuracy(orders_df, 'orders')
    
    print("客户数据准确性:")
    for column, info in customers_accuracy.items():
        if column != 'overall' and isinstance(info, dict):
            print(f"  {column}: {info['accuracy_rate']:.1%} ({info['invalid_records']}条无效)")
            if info['invalid_samples']:
                print(f"    无效样本: {info['invalid_samples']}")
    
    # 5. 分析一致性
    print("\n5. 分析数据一致性")
    print("-"*40)
    
    # 模拟第二份客户数据（有差异）
    customers_v2_data = customers_data.copy()
    customers_v2_data['city'] = ['北京', '上海', '广州', '深圳', '杭州', '苏州', '成都', '重庆', '南京', '西安']  # 第9个城市不同
    
    customers_v2_df = pd.DataFrame(customers_v2_data)
    
    consistency_result = analyzer.analyze_consistency(
        customers_df, customers_v2_df, 
        ['customer_id'], ['city'],
        'customers_v1', 'customers_v2'
    )
    
    print("客户数据一致性分析:")
    print(f"  匹配记录数: {consistency_result['matched_count']}")
    print(f"  仅存在于v1的记录数: {consistency_result['table1_only_count']}")
    print(f"  仅存在于v2的记录数: {consistency_result['table2_only_count']}")
    print(f"  整体一致性: {consistency_result['overall_consistency']:.1%}")
    
    for column, info in consistency_result['column_consistency'].items():
        if isinstance(info, dict):
            print(f"  {column}: {info['consistency_rate']:.1%} (一致: {info['consistent_records']}, 不一致: {info['inconsistent_records']})")
    
    # 6. 分析及时性
    print("\n6. 分析数据及时性")
    print("-"*40)
    
    customers_timeliness = analyzer.analyze_timeliness(customers_df, 'registration_date', 'customers')
    orders_timeliness = analyzer.analyze_timeliness(orders_df, 'order_date', 'orders')
    
    print("客户数据及时性:")
    print(f"  总记录数: {customers_timeliness['total_records']}")
    print(f"  最新日期: {customers_timeliness['latest_date']}")
    print(f"  最早日期: {customers_timeliness['earliest_date']}")
    print(f"  平均延迟天数: {customers_timeliness['average_delay_days']:.1f}")
    
    # 7. 分析唯一性
    print("\n7. 分析数据唯一性")
    print("-"*40)
    
    customers_uniqueness = analyzer.analyze_uniqueness(customers_df, ['customer_id', 'email'], 'customers')
    orders_uniqueness = analyzer.analyze_uniqueness(orders_df, ['order_id', 'customer_id'], 'orders')
    
    print("客户数据唯一性:")
    for column, info in customers_uniqueness.items():
        if column != 'combination' and isinstance(info, dict):
            print(f"  {column}: {info['uniqueness_rate']:.1%} (唯一: {info['unique_count']}, 重复: {info['duplicate_count']})")
    
    # 8. 计算业务影响
    print("\n8. 计算业务影响")
    print("-"*40)
    
    # 假设数据使用情况
    customers_usage = {
        'customer_service_queries': 1000,
        'marketing_campaigns': 500,
        'analytics_reports': 300,
        'fraud_detection': 200
    }
    
    orders_usage = {
        'order_fulfillment': 2000,
        'analytics_reports': 500,
        'fraud_detection': 150
    }
    
    customers_impact = analyzer.calculate_business_impact(
        'customers', len(customers_df), customers_usage
    )
    
    orders_impact = analyzer.calculate_business_impact(
        'orders', len(orders_df), orders_usage
    )
    
    print("客户数据质量业务影响:")
    print(f"  总体质量分数: {customers_impact['overall_quality_score']:.1%}")
    print(f"  影响分数: {customers_impact['impact_score']:.1f}")
    print(f"  问题记录数: {customers_impact['problem_records']}")
    print(f"  修复成本: ¥{customers_impact['total_repair_cost']:.2f}")
    print(f"  数据价值损失: ¥{customers_impact['data_value_loss']:.2f}")
    print(f"  总业务影响: ¥{customers_impact['total_business_impact']:.2f}")
    
    # 9. 生成质量报告
    print("\n9. 生成质量报告")
    print("-"*40)
    
    customers_report = analyzer.generate_quality_report('customers')
    
    print("客户数据质量报告:")
    print(f"  生成时间: {customers_report['generated_at']}")
    print(f"  分析维度: {len(customers_report['dimensions'])}个")
    print(f"  改进建议: {len(customers_report['recommendations'])}条")
    
    print("\n主要改进建议:")
    for rec in customers_report['recommendations']:
        print(f"  - {rec['issue']} ({rec['priority']}优先级)")
    
    # 10. 可视化
    print("\n10. 可视化质量维度")
    print("-"*40)
    
    analyzer.visualize_quality_dimensions('customers')
    
    return analyzer


if __name__ == "__main__":
    # 运行演示
    analyzer = demonstrate_data_quality_analysis()
    
    print("\n数据质量分析演示完成！")